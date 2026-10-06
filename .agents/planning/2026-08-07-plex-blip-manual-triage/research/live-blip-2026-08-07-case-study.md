# Research: Live Blip Case Study — 2026-08-07 06:37 EDT

**Source:** `/tmp/plex-logs/2026-08-07/` (92 MB dump, pulled 12:37).
**Method:** `scripts/analyze_plex_blips.py` plus direct log inspection. All
timestamps EDT, from `Plex Media Server.log`.

This is a **fresh blip, three days after the 2026-08-04 remediation landed**. It is
the single most valuable input to this project, because it falsifies part of the
prior diagnosis and exposes two concrete defects in the tooling built for it.

---

## Headline findings

1. **The blip recurred, and it was three times worse.** Peak request duration
   **108,832 ms** vs 35,905 ms on 2026-08-04.
2. **The 2026-08-04 remediation is working — and was not enough.** The
   `plex-exporter` library sweep, the amplifier blamed last time, is **provably
   absent** from this blip's window.
3. **The causal log signature is one that neither the watchdog nor the offline
   analyzer matches.** Verified by executing `check_trigger` directly.
4. **A blackbox probe on `/identity` would have stayed green through the whole
   outage.** This corrects a recommendation made earlier in this project's own
   research.

---

## Timeline

| Time | Event |
|---|---|
| 06:31:39.886 | Log rotates. Banner re-emitted (**not** a restart — see §4) |
| 06:36:40 | Baseline healthy: `/identity` **2 ms**, `/status/sessions` **3 ms**, segments **2–4 ms**, `(5 live)` |
| 06:37:17 | Last fast transcode segment: `03068.ts` in **4 ms** |
| 06:37:24.3 | Timeline request `#8ec18` arrives; its internal steps now take ~200 ms each (were sub-ms) |
| 06:37:25.3 | First slow completion: `/:/timeline` **1031 ms** |
| **06:37:33.273** | **`Held transaction for too long (StatisticsManager.cpp:288): 0.54 s`** ← **first causal line** |
| 06:37:35.8 | `Held transaction ... MetadataItemSetting.cpp:409` 0.18 s |
| 06:37:39 | Segments degrade: `03069.ts` 5092 ms, `03070.ts` 6889 ms |
| **06:38:22.285** | First `Took too long ... to start a transaction` ← **first line the watchdog sees, 49 s late** |
| 06:38:40.5 | `/:/timeline` **45,153 ms** |
| 06:38:52.3 | `/identity` **1761 ms** — worst it ever gets; still HTTP 200 |
| 06:38:55.1 | Transcode segment `03072.ts` **62,170 ms** |
| 06:39:37.2 | `/status/sessions` **45,047 ms** |
| 06:39:42 | **Client reports `buffering`.** Progress freezes at 3,072,590 ms |
| 06:40:38.2 | **Peak: `/:/timeline` 108,832 ms** |
| 06:41:20.9 | `Completed after connection close ... 103,819 ms **0 bytes**` — client gave up |
| 06:41:24.6 | `/status/sessions` **101,394 ms** |
| 06:41:45 – 06:42:23 | Three more `Completed after connection close`, 0 bytes |
| 06:42:49 | `/status/sessions` back to 7000 ms; recovery |
| ~06:43 | Normal service |

**Outage envelope:** roughly 06:37:25 → 06:42:30, about **5 minutes**, with the
client visibly buffering and frozen for **2 min 40 s** (06:39:42 → 06:42:22).

Affected client: `192.168.1.208`, Android (`DYGS24U`), user `masyllis`, connected
**directly to `:32400`** — not through Traefik.

---

## 1. The exporter sweep is definitively exonerated

The 2026-08-04 diagnosis was that Prometheus scrapes triggered a synchronous
`GET /library/sections/<key>/all` sweep which collided with SQLite contention and
retried every 60 s, amplifying a transient stall into a stream-killing stall. The
fix set `METRICS_MEDIA_COLLECTING_INTERVAL_SECONDS=1800` with a 60 s/50 s scrape
pair.

**That fix is working exactly as designed.** Library sweeps in this log occur at:

```
06:58:40   07:29:40   08:00:40   08:31:40
```

— a clean **31-minute cadence** (1800 s throttle + scrape alignment). And in the
blip window:

```
sweeps between 06:36 and 06:43 :  0
```

What the exporter *did* do during the blip is its cheap per-scrape trio —
`/identity`, `/status/sessions`, `/activities`, once per 60 s. Those requests were
**victims** of the stall (`/status/sessions` reaching 101 s), not causes of it.

**Conclusion: Class A's amplifier is excluded. The underlying contention is a
separate, still-unaddressed fault**, exactly as
[prior-art-and-upstream.md](prior-art-and-upstream.md) anticipated — "the amplifier
was fixed; the trigger was not." That is no longer a caution; it is an observation.

---

## 2. The causal signature: `Held transaction for too long`

The 2026-08-04 work keyed everything on `Took too long (N seconds) to start a
transaction` — the **victim's** view: a thread waiting for a lock. This dump
contains a different line, which appears **first**:

```
06:37:33.273 WARN - Held transaction for too long
             (.../Statistics/StatisticsManager.cpp:288): 0.540000 seconds
```

This is the **holder's** view — the thread that *took* the lock and kept it. 42
occurrences in this log. The distribution of sites:

| Site | Meaning | Peak hold |
|---|---|---|
| `Statistics/StatisticsManager.cpp:288` | statistics flush | 0.54 s |
| `Library/MetadataItemSetting.cpp:409` | play-state / view-offset write | 2.25 s |
| `Library/MetadataItemSetting.cpp:459` | play-state / view-offset write | 2.51 s |

**All three are writes driven by ordinary playback timeline reporting.** No
scheduled task ran in the window (the only nearby task was `Refreshing section 1`
at 06:33:29, four minutes earlier, touching 0 IDs). There is no library scan, no
backup, no maintenance job. **A single Android client reporting its play position
every ~10 s was enough to produce 2.5-second lock holds**, and those holds cascaded
into 100-second request queues.

This reframes the fault. It is not "an expensive background job collides with
playback." It is "**the play-state write path itself becomes pathologically slow**,
and once it does, every request that needs the database queues behind it."

A quantitative note that reinforces this: total measured *waiting* time across all
32 `Took too long` events is **9.45 s**, but requests stalled for **108 s**. The
lock-wait accounting does not come close to explaining the outage duration — which
means what we are measuring is the ripple, not the stone. The `Held transaction`
lines and the climbing connection count (§5) are closer to the stone.

---

## 3. Both existing tools are blind to that signature — verified

`ansible/roles/plex/files/plex_blip_watchdog.py::check_trigger` matches on
`"Took too long" in line and "to start a transaction" in line`. Executed directly
against both lines:

```
check_trigger("...Held transaction for too long (StatisticsManager.cpp:288): 0.54 seconds")
  -> None

check_trigger("...Took too long (0.110000 seconds) to start a transaction on ...")
  -> {'event_type': 'TX_STALL', 'delay_ms': 110.0, ...}
```

`scripts/analyze_plex_blips.py::parse_log_line` has the identical condition at
line 67 and the identical gap.

**Operational consequence, measured on this event:**

- First causal line: **06:37:33.273**
- First line the watchdog can see: **06:38:22.285**
- **The watchdog fires 49 seconds late.**

Forty-nine seconds is not a rounding error here — it is the entire early phase of
the cascade, during which connection count climbs from 4 to 10 and the first 45-
and 62-second requests are already in flight. The diagnostic snapshot
(`fuser`/`lsof`/`pidstat`) is meant to catch *who holds the lock*; by the time it
fires, the holder has released and the picture is of the pileup, not the cause.

Worse, the `Held transaction` line **names the holding site directly in its text** —
`StatisticsManager.cpp:288` — which is precisely the attribution the `fuser`/`lsof`
snapshot was built to approximate. The cheapest signal is also the most specific
one, and it is being discarded.

**This is the single highest-value fix available, and it is a one-line regex
change plus tests in both tools.**

---

## 4. The startup banner is not a restart — a triage trap

`Plex Media Server.log` opens with:

```
06:31:39.886 INFO - Plex Media Server v1.42.2.10156-f737b826c - Debian ... 
06:31:39.887 INFO - Processor: 6-core 13th Gen Intel(R) Core(TM) i5-13500
```

Read naively this is a **process restart at 06:31:39, six minutes before the blip**
— a compelling Class B story. It is wrong. Plex re-emits its version banner at the
head of every rotated log file. The discriminators, all visible at the boundary:

- Request IDs continue across it: `#8e27e` (in `.1.log`) → `#8e281` (in `.log`)
- Thread IDs are identical on both sides (`132687881837368`, `132688108632888`)
- The transcode session `f0ccf4d2-…` continues uninterrupted, segment 2725 → 2726
- Timestamps interleave to the millisecond (`.885` appears on both sides)
- `(4 live)` connection count is continuous
- No `Shutting down`, no `SIGTERM`, no signal line anywhere in the log

**Rule for the runbook:** a banner is a restart only if request/thread/session IDs
*reset* across it. Check the tail of `.1.log` against the head of `.log` before
concluding Class B. This trap costs nothing to avoid and would otherwise send an
entire investigation down the wrong branch.

---

## 5. An unused saturation signal is already in every log line

Every `Request:`/`Completed:` line carries a live-connection count. Across the blip:

```
06:36:40  (5 live)     baseline
06:37:40  (5 live)
06:38:50  (10 live)
06:38:52  (11 live)
06:40:43  (12 live)
06:40:46  (13 live)    peak
06:41:24  (7 live)     draining
06:42:27  (3 live)     recovered
```

This is a clean, monotonic saturation curve — arrivals outpacing completions — and
it is **already being written to disk on every single request**. Neither tool
extracts it. Turning it into `plex_live_connections` (via the textfile-collector
route in [instrumentation-gaps.md](instrumentation-gaps.md) §7) would give a
leading indicator at zero collection cost and zero added load on Plex.

---

## 6. Correction: `/identity` alone is not a sufficient health probe

[instrumentation-gaps.md](instrumentation-gaps.md) §2 recommends blackbox probes
against `/identity`, on the reasoning that it is unauthenticated and does no
database work. This event shows that reasoning is right about *cost* and wrong
about *sensitivity*. Measured, from `192.168.1.111`:

| Time | `/identity` | `/status/sessions` |
|---|---|---|
| 06:36:40 | 2 ms | 3 ms |
| 06:37:40 | 225 ms | 2,398 ms |
| 06:38:52 | **1,761 ms** | 45,047 ms |
| 06:39:42 | 913 ms | — |
| 06:40:43 | 1,763 ms | 78,529 ms |
| 06:41:42 | 1,436 ms | **101,394 ms** |
| 06:42:41 | 953 ms | 7,000 ms |

`/identity` **returned HTTP 200 for every single probe**, and its worst case was
1.76 s — inside any sane blackbox timeout. A `probe_success`-based alert on
`/identity` would have stayed **green for the entire five-minute outage**.

That is exactly the property that makes it cheap: it doesn't touch the database, so
it doesn't feel the lock. Meanwhile `/status/sessions` — which does — went to 101
seconds.

**Revised recommendation (supersedes gap §2 as written):**

1. Keep the `/identity` probe, but alert on **`probe_duration_seconds`**, not only
   `probe_success`. The 2 ms → 1,761 ms shift is an ~900× signal and is
   unmistakable; the binary success bit is not.
2. **Add a second, DB-touching probe** — `/status/sessions` — at a lower frequency
   (60 s) with a generous timeout. This is the probe that actually goes red.
3. The **ratio** between the two is itself the best available discriminator:
   `/identity` fast + `/status/sessions` slow ⇒ database/lock (Class A-like);
   both slow ⇒ thread-pool or host-level saturation; both unreachable ⇒ process or
   network.

This is a genuine correction driven by measurement, and it is the kind of error
that would have shipped silently had this dump not been available.

---

## 7. Minor observations

- **SSDP flap:** `192.168.1.163 (Master Bedroom TV)` departed at 06:36:23 after
  21.6 s unseen, re-arrived 06:36:34 — about a minute before onset. Probably
  unrelated LAN multicast noise, but it is the only network-adjacent anomaly nearby
  and is worth a second look if a pattern emerges across events.
- **Transcode throttling** cycles normally right up to onset (`unthrottling` /
  `Going into sloth mode` every ~15 s), so the transcoder was healthy and
  buffer-ahead was working. Class F is not implicated.
- **Direct connection:** the affected client hit `192.168.1.208 → :32400` directly.
  A Traefik access log, had one existed, **would not have recorded this outage at
  all** — reinforcing the caveat in
  [instrumentation-gaps.md](instrumentation-gaps.md) §3.
- **Timing:** 06:37, not the top of the hour. The "07:00 EDT" framing from the
  earlier investigation does not generalise.
- The dump also contains `Plex Media Server.{1..5}.log` covering 2026-08-04
  22:59 → 08-07 06:31, i.e. **the retained history spans under three days at
  10 MB × 6 files**. Direct confirmation of the rotation-pressure hazard in
  [triage-window-and-data-survival.md](triage-window-and-data-survival.md).

---

## What this changes for the project

| Area | Change |
|---|---|
| **Taxonomy** | Class A splits: A1 = exporter-amplified (fixed), A2 = play-state write path stalls on its own (**live, unexplained**). Today's event is A2. |
| **Watchdog** | Add `Held transaction for too long` as a trigger, with the holding site captured. Highest-value single change identified so far. |
| **Analyzer** | Same regex gap; add the event type and report holder-vs-waiter separately. |
| **Probes** | `/identity` + `/status/sessions` pair, alert on duration not just success. |
| **New metric** | `plex_live_connections` from the `(N live)` field — free leading indicator. |
| **Runbook** | Must include the banner-vs-restart check, and must lead with "bound the window from `Held transaction`, not from `plex_up`." |
| **Root cause** | Still open. Why do `MetadataItemSetting.cpp:409/459` writes hold locks for 2.5 s under a single playing client? Candidates: WAL not actually enabled, checkpoint stalls, storage latency under the DB path, DB bloat. The WAL audit from 2026-08-04 Step 5 is now directly relevant and its result should be checked. |

---

## 8. Root-cause dig into A2 — the escalation, and what it is *not*

Extending the `Held transaction` count across all six retained log files, and
**normalising by playback volume** (`/:/timeline` requests, a direct proxy for
minutes streamed):

| Log | Window | Timeline reqs | `Held` (excl. DB-optimisation) | per 1k reqs |
|---|---|---|---|---|
| `.5` | Aug 04 12:15 → Aug 04 22:59 | 1,126 | 0 | **0.00** |
| `.4` | Aug 04 22:59 → Aug 05 11:40 | 1,339 | 0 | **0.00** |
| `.3` | Aug 05 11:40 → Aug 06 02:38 | 1,856 | 0 | **0.00** |
| `.2` | Aug 06 02:38 → Aug 06 20:25 | 975 | 0 | **0.00** |
| `.1` | Aug 06 20:25 → Aug 07 06:31 | 906 | 18 | **19.87** |
| `.log` | Aug 07 06:31 → Aug 07 08:37 | 124 | 42 | **338.71** |

**Zero across 5,296 timeline requests spanning three days, then 19.87, then
338.71.** With *less* streaming producing *more* lock holds, this is not a volume
artifact — it is a step change followed by a 17× acceleration.

The three `Held` events in `.3` are excluded above because they are a different,
benign thing: `[Database optimization/…] Held transaction for too long
(Library/FullTextSearch.cpp:…)` at **Aug 06 02:00:11**, i.e. Plex's scheduled
nightly database optimisation. Expected, off-peak, unrelated to playback.

All 60 playback-path events fall in exactly two hours:

```
Aug 06 23:00 — 18 events
Aug 07 06:00 — 42 events
```

### Ruled out

| Hypothesis | Evidence against |
|---|---|
| **Plex version change** | Banner is `v1.42.2.10156-f737b826c` in all six logs, Aug 4 → Aug 7. No update. |
| **Plex restart** | No `Shutting down`, no signal lines, no init sequence anywhere. Every banner is a rotation (§4). |
| **Exporter library sweep** | 31-minute cadence; zero sweeps in either event window (§1). |
| **Scheduled task collision** | No scan, backup, or maintenance job in either window. The nightly optimisation is at 02:00 and is cleanly separated. |
| **The WAL-audit commit mutated the DB** | `5c9a830` adds a **read-only** `PRAGMA journal_mode;` with `changed_when: false`. It queries; it does not set. It also only runs during an Ansible play, not continuously. |
| **The watchdog is the new amplifier** | **Refuted by a natural experiment — see below.** |

### The natural experiment that refutes the watchdog hypothesis

The watchdog (`e3415f0`) was deployed **Aug 6 15:38**, and the escalation begins
Aug 6 23:08 — a temporal correlation strong enough that the watchdog was the
leading hypothesis, and it would have been a grimly fitting one given that a
monitoring component caused the 2026-08-04 incident.

The logs refute it. After the watchdog was deployed, item **377** was played for
**2 h 17 min** (Aug 6 20:25 → 22:42):

```
timeline requests for ratingKey=377 in that window : 1,617
Held-transaction events in that window             :     0
```

Item **378** began at **22:42:02**; the first `Held` event followed at **23:08:49**.
Every subsequent event, in both sessions, occurs during item 378 playback.

Same watchdog, same host, same client (`192.168.1.208`), same evening. The variable
that changed is the **media item**. (Note also that the 15:38 → 20:25 stretch has
**zero** timeline requests — no playback at all — so `.2`'s clean record across the
deploy proves nothing either way. The 377 window is the informative control.)

### The surviving hypothesis: something about item 378's play-state write path

Items 371 → 377 were watched in sequence across Aug 4–6 with a **perfect zero**
event rate. Item 378 produces `Held transaction for too long` at
`Library/MetadataItemSetting.cpp:409/459` — the view-offset / play-state write —
within half an hour of first playback, on both occasions it has been played.

Also worth noting: `Refreshing section 1 of type: 2` (a **show** section) ran at
**06:33:29**, roughly four minutes before the Aug 7 onset.

Candidate mechanisms, none confirmable from logs alone:

1. **Row-level pathology for item 378** in `metadata_item_settings` — an unusually
   large or contended row set, or an index that has degenerated for this item.
2. **Recently-added item still settling** — 378 is the newest in the sequence; if
   its metadata/section refresh is incomplete, play-state writes may be contending
   with background metadata work on the same rows.
3. **WAL not actually enabled, or checkpoint stalling.** The 2026-08-04 Step 5 audit
   asserts `journal_mode == wal` — its *actual result on the live DB* is not
   recorded anywhere in the repo. A DB in `delete`/`truncate` journal mode would
   serialise readers against writers exactly as observed.
4. **Storage latency under the database path** — a 2.5 s lock hold is consistent
   with an fsync that went to slow media.

### What would settle it — all require live access

| Check | Command | Settles |
|---|---|---|
| Journal mode, for real | `sqlite3 …/com.plexapp.plugins.library.db 'PRAGMA journal_mode;'` | #3 |
| WAL size / checkpoint backlog | `ls -l …/com.plexapp.plugins.library.db*` | #3 |
| DB size & free-page bloat | `PRAGMA page_count; PRAGMA freelist_count;` | #1 |
| Item 378's settings rows | `SELECT count(*) FROM metadata_item_settings WHERE guid IN (SELECT guid FROM metadata_items WHERE id=378);` | #1 |
| Whether the watchdog ever fired | `ls /var/log/plex_blip_watchdog/` on CT 110 | closes the watchdog question outright |
| Storage latency under the DB | `dmesg -T`, disk I/O on the PVE host | #4 |

**Recommended immediate empirical test, costing nothing:** play item **377**
again and then item **378**, and diff the `Held transaction` rate. The logs predict
0 for the former and a burst for the latter. If that reproduces, the fault is
item-scoped and the fix is a targeted metadata repair rather than an
infrastructure change — a far smaller and safer remediation than anything in
[instrumentation-gaps.md](instrumentation-gaps.md).

---

## 9. Live-system results (operator-run, 2026-08-07 ~09:14)

### 9.1 CORRECTION to §3 — the watchdog fires on time

§3 claimed the watchdog "fires 49 seconds late", derived by comparing the first
`Held transaction` line (06:37:33.273) against the first `Took too long` line
(06:38:22.285). **That comparison was wrong**, because it ignored the watchdog's
third trigger: `Completed:` ≥ 500 ms. The snapshot file shows the actual firing:

```
first ≥500 ms completion : 06:37:25.337
watchdog snapshot written: 06:37:25.389     → 52 ms later
```

The watchdog is **prompt**. What it does not do is *classify* or *attribute* the
event: it recorded `SLOW_QUERY`, not a lock-holder event, and it never captured
`StatisticsManager.cpp:288` — the holding site that the `Held transaction` line
states in plain text.

That makes the regex gap **more** important, not less, for the reason in §9.2:
the two probes designed to identify the lock holder do not work, so the log line
is the only surviving source of holder attribution.

### 9.2 The watchdog's diagnostic probes have never worked

34 snapshots across both event days. Every one of them:

```
"fuser": "[probe error: [Errno 2] No such file or directory: 'fuser']"
```

`fuser` ships in **`psmisc`**. The role installs `sysstat`, `lsof`, `procps`,
`sqlite3` (`ansible/roles/plex/tasks/main.yml:237-245`) — **`psmisc` is not in the
list**. The primary lock-holder probe has failed on 34 of 34 invocations since
deployment.

`lsof` is worse than broken — it is **anti-correlated with the fault**:

| Period | `lsof` result |
|---|---|
| Healthy (22 snapshots) | `ok` — full output |
| **Inside both blip windows (12 snapshots)** | **`[probe timeout exceeded]`** |

`_run_cmd` uses a hard `timeout=0.5` s. During a stall, `lsof` on the database
files exceeds 500 ms every single time and returns nothing. So:

> **The watchdog captured lock-holder data on every occasion when nothing was
> wrong, and captured none on every occasion when something was.**

Of its four probes — `fuser`, `lsof`, `pidstat -tl`, fd-count — the two that
identify *who holds the database* are exactly the two that fail. `pidstat` and
`fd_count` work throughout.

Incidentally the timeout pattern is itself a clean signal: `lsof` on the DB files
crossing 500 ms is a one-bit indicator that the inode is contended. If the probe
recorded its own duration instead of discarding it on timeout, that alone would be
a usable metric.

### 9.3 The likely root cause: a WAL pinned at 43× the checkpoint threshold

```
com.plexapp.plugins.library.db       41 M
com.plexapp.plugins.library.db-wal   42 M      ← larger than the database
com.plexapp.plugins.library.db-shm  352 K
journal_mode = wal
page_count   = 41831,  page_size = 1024,  freelist_count = 0
```

- `41831 × 1024` = **40.9 MiB** of database.
- The WAL is **41.71 MiB** — SQLite's default `wal_autocheckpoint` is 1000 pages,
  i.e. **~1 MiB**. The WAL is **43× that threshold**, and holds roughly as many
  frames as the database has pages: essentially the whole database has been
  rewritten into the log.
- `freelist_count = 0` — the database itself is **not** bloated. The pathology is
  entirely in the WAL.

And the watchdog's own `lsof` output gives us a 42.5-hour history of that file's
size, because it captures the fd:

```
2026-08-06T14:03:48   43,735,168 bytes
2026-08-06T20:25:13   43,735,168
2026-08-06T23:08:23   43,735,168
2026-08-07T06:37:25   43,735,168
2026-08-07T08:37:03   43,735,168
```

**Byte-for-byte identical across 42.5 hours**, spanning both blips and all the
healthy periods between. The WAL high-water mark is frozen.

A caveat stated honestly: a constant WAL size is *not by itself* proof that
checkpointing has stopped, because SQLite reuses a WAL in place after a successful
checkpoint rather than truncating it. But the file had to *reach* 41.71 MiB in the
first place, and it can only do that if checkpointing was blocked for a long
stretch while ~42,000 frames accumulated. Once large it never shrinks without an
explicit `wal_checkpoint(TRUNCATE)` — or a clean restart. And **Plex has not been
restarted at any point in the retained log window** (§4).

Why this produces the observed symptom: every reader must consult the WAL index
(`-shm`, now 352 KB) to find the newest version of each page. A larger WAL means
more index and more work per read, and it makes each checkpoint attempt more
expensive — which makes it more likely to be starved out by continuous write
traffic, which keeps the WAL large. That is a self-sustaining state, and it is
consistent with a fault that appears out of nowhere and then escalates.

**Supporting measurement — `pveperf /` on the PVE host:**

```
BUFFERED READS:    2955.08 MB/sec
AVERAGE SEEK TIME: 0.04 ms          ← NVMe-class
FSYNCS/SECOND:     385.21           ← low for NVMe (expect 1000s)
```

Fast reads and seeks, but modest fsync throughput. A 42,000-frame checkpoint
against 385 fsync/s is not cheap. This is a plausible contributing factor to
checkpoint starvation rather than an independent fault.

### 9.4 The item-378 hypothesis is dead

§8 proposed that item 378 was pathological. The database says otherwise:

```
id | section | type | added_at   | updated_at
377|       1 |    4 | 1672756658 | 1784087152
378|       1 |    4 | 1672756783 | 1784128195
```

Same library section, same metadata type (4 = episode), **added 125 seconds apart
in January 2023**, metadata updated 11 hours apart in July 2026. They are
structurally indistinguishable, and neither is a recent addition.

So the 377-clean / 378-dirty split is **coincidental** — 22:42 is simply when the
system crossed the threshold at which lock holds began exceeding Plex's 100 ms
logging cutoff. The escalating variable is time (and WAL state), not the item.

This also retires the "replay 377 then 378" test proposed in §8: it would not
isolate anything.

### 9.5 Storage: no faults, but a slow device

PVE `dmesg` shows **no** USB resets, I/O errors, or OOM kills. ZFS:

```
pool: DASPool   state: ONLINE   READ 0  WRITE 0  CKSUM 0
  usb-QNAP_TR-004_DISK00_...        ← single vdev, USB, no redundancy
scan: scrub repaired 0B in 2 days 13:17:22 ... on Fri Jul 17
no zpool events since Jul 17
```

Nothing is failing. But a **2 day 13 hour scrub** indicates a very slow device, and
it is a single USB vdev with no redundancy. The media path (`/media/Videos/Korean
Shows/Running Man/…`, per the transcoder command line captured in `pidstat`) lives
here; the **database does not** — it is on CT 110's rootfs on PVE local storage.
So the DAS is not implicated in the lock contention, but it remains an availability
risk worth raising separately.

Also confirmed: **`dmesg -T` inside CT 110 returns empty** — an unprivileged LXC
has no kernel ring buffer. Kernel evidence must come from the PVE host, and a blank
result inside the container must not be read as "no errors". This validates the
Class B/D caveat in
[blip-taxonomy-and-discriminators.md](blip-taxonomy-and-discriminators.md).

### 9.6 Revised remediation ranking

| # | Action | Basis | Cost |
|---|---|---|---|
| 1 | **Add `psmisc` to the role's package list** | `fuser` has failed 34/34 times | one line |
| 2 | **Raise `_run_cmd` timeout for `lsof`, and record probe duration on timeout** | `lsof` fails in 12/12 in-blip snapshots | small |
| 3 | **Checkpoint the WAL** (`wal_checkpoint(TRUNCATE)`, or a clean Plex restart) and re-measure | WAL is 43× threshold, frozen 42.5 h | minutes |
| 4 | **Monitor WAL size as a metric** — it is the leading indicator | 42.5 h of evidence already in the JSONL | small |
| 5 | Add `Held transaction` trigger with holder-site capture | only working source of attribution (§9.1) | one regex |
| 6 | Extend the 08-04 WAL audit to assert **size**, not just mode | the audit passes today while the pathology is live | one task |

Item 6 deserves emphasis. `5c9a830`'s audit asserts `journal_mode == 'wal'` and
that assertion is **true** — the check passes. It simply checks the wrong property.
A guard that is green while the fault it exists to catch is active is worse than no
guard, and this is the second time in this codebase that a Plex guard has needed
its claim strengthened rather than its polarity flipped.

**The decisive experiment, now cheap and safe:** checkpoint the WAL (or restart
Plex cleanly), confirm `-wal` drops to near zero, then stream for an evening and
count `Held transaction` lines. Zero would confirm the mechanism; a recurrence
would mean the WAL is a symptom of something still upstream — most likely a
long-lived reader preventing checkpoint reset, which `PRAGMA wal_checkpoint(PASSIVE)`
return values would then expose.

---

## References

- Live results, operator-run 2026-08-07 ~09:14: `sqlite3 -readonly` pragmas on
  CT 110; `pveperf /`, `zpool status`, `dmesg -T` on the PVE host.
- Watchdog snapshots: `/tmp/plex-logs/plex_blip_diagnostics_{20260806,20260807}.jsonl`
  (34 snapshots, 448 KB).
- Dump: `/tmp/plex-logs/2026-08-07/` — `Plex Media Server.log` (06:31:39 → 08:37:03)
  plus `.1`–`.5` covering Aug 04 12:15 → Aug 07 06:31.
- Commits correlated: `e3415f0` (watchdog service, Aug 6 15:38), `3d33f30` (scrape
  remediation, Aug 6 15:47), `5c9a830` (WAL audit, Aug 6 16:18).
- Tooling exercised: `scripts/analyze_plex_blips.py`,
  `ansible/roles/plex/files/plex_blip_watchdog.py` (`check_trigger` executed directly).
- Prior diagnosis under test: `.agents/planning/2026-08-04-debug-plex-blip/research/log-correlation-patterns.md`
- Remediation under test: `ansible/roles/docker_host/templates/prometheus.yml.j2`,
  `compose.yml.j2` (`METRICS_MEDIA_COLLECTING_INTERVAL_SECONDS=1800`).
- `docs/runbooks/plex-sqlite-maintenance.md` — the WAL audit now worth re-checking.
