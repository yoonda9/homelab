# Runbook: Plex latency baseline (Step 1 — capture it from OFF the LAN)

This runbook covers the **one-shot baseline capture** that Step 4 of the Plex
optimization plan is compared against
(`.agents/planning/2026-07-27-plex-optimization/implementation/plan.md`). The
repo-side half — the re-runnable harness `scripts/measure_plex_latency.py` — is
already built and committed (Step 1a). This document is the **operator** half:
where to stand, what to type, and what to write down.

The split of responsibilities mirrors `plex-ramdisk.md`: the harness is owned by
the repo, and **running it from an external network is a manual, operator-run
step** — no agent in this repo has a route off the LAN. §5 is the deliverable
the operator fills in; everything above it is how to fill it in correctly.

> ⚠️ **The single most misread part of this plan.** The baseline must be
> captured from an **external network** — a phone **mobile hotspot**, LTE, or
> any link that is not this house's LAN. See §1. A LAN capture is a *control*,
> not the baseline, and filing one as the baseline quietly destroys Step 4.

---

## 1. Why the measurement must come from an external network

The complaint being optimized is *remote* Plex: a client out on the internet
reaching `plex.yoonnation.com`. From inside the LAN that request never travels
the path under test.

- **No WAN path.** On the LAN the packet goes client → switch → Traefik, and
  never leaves the LAN. The WAN uplink, the ISP's upstream latency and the
  round trip back are all absent from the number, and they are most of what a
  remote user waits for.
- **No router hairpin.** A LAN client resolving the public hostname either gets
  a split-horizon answer (and hits the reverse proxy directly) or is
  hairpinned by the router back through the NAT table. Neither is what an
  external client does, and the hairpin case in particular has its own cost
  that is present in the baseline and absent afterwards, or the reverse.
- **A different TLS and routing decision.** An external client may be steered
  through a different path entirely; a LAN client never is.

So: a run taken on the LAN is a **control** — useful for separating "Traefik is
slow" from "the internet is slow", which is exactly what the direct-`:32400`
leg in §3 is for — but it is **not the baseline**. The harness makes the
distinction mandatory rather than advisory: `--vantage` has no default, and
every record is stamped with the vantage it was taken from, so a LAN run can
never be silently paired against an external one.

**Take the external capture on a link you can reproduce in Step 4.** The same
phone, the same carrier, roughly the same signal, ideally the same time of day.
Step 4 subtracts these two numbers; whatever differs between them is what the
comparison will attribute to the changes.

---

## 2. Before you start

1. **Get off the LAN.** Turn Wi-Fi off on the laptop and tether to the phone's
   hotspot, or run the capture from a machine that was never on this network.
   Confirm it, do not assume it:

   ```bash
   curl -s https://ifconfig.me; echo
   ```

   That address must **not** be the house's WAN address. If it is, you are
   still on the LAN (or on the VPN — see §6).

2. **The Plex token, if you want the library endpoints.** The harness reads it
   from the `PLEX_TOKEN` environment variable and from nowhere else — there is
   deliberately **no `--token` flag**, because a flag lands in shell history.
   Get the value from the Plex web app (any library item → **Get Info** →
   **View XML**; the token is the `X-Plex-Token` query parameter of the URL that
   opens).

   ```bash
   export PLEX_TOKEN='<paste-the-value-here-in-this-shell-only>'
   ```

   > 🔒 **Never** paste the token into a file in this repo, into a commit, into
   > the results table below, or into any chat. It is a credential for the whole
   > Plex account. This repo has a no-plaintext-secrets rule; the token lives in
   > your shell for the length of the capture and nowhere else.

   Without `PLEX_TOKEN` the harness probes the unauthenticated `/identity` only,
   which is still a valid TTFB baseline — just not a library-load one.

3. **Wake Plex up.** Open the Plex app once and let a library view render, then
   wait ~30 s. A cold server measures cold-start, not steady-state (§6).

---

## 3. The capture

### 3a. The baseline — from the external network

This is the run that matters. Take it **first**, while you are off-LAN.

```bash
python3 scripts/measure_plex_latency.py \
  --label baseline \
  --vantage external \
  --skip-direct \
  --repeats 10
```

- `--label baseline` — Step 4 pairs runs by label and vantage; an unlabelled
  run cannot be paired, so the flag is required.
- `--vantage external` — stamps the record as off-LAN. Required, no default.
- `--skip-direct` — **do not omit this off-LAN.** The direct leg addresses the
  backend at its RFC1918 address (`192.168.1.110:32400`), which is unroutable
  from outside the house. Without the flag a perfectly good capture spends
  `repeats × timeout` hanging on a leg that cannot answer and then exits `1`.
  The record is stamped `direct_probed=false` so the missing A/B is explicit.
- `--repeats 10` — ten samples per endpoint instead of the default five.
  A hotspot is noisy and this run is not cheap to retake.

Keep the whole report. The **report goes to stdout**; notes and `WARNING` lines
go to **stderr**. To keep both, in order, alongside the automatic JSONL record:

```bash
python3 scripts/measure_plex_latency.py --label baseline --vantage external --skip-direct --repeats 10 2>&1 | tee /var/tmp/plex-baseline-external.txt
```

### 3b. The direct-`:32400` control — a SEPARATE run, back on the LAN

**This is not part of the external capture and cannot be run from the hotspot.**
The direct leg only exists on the LAN. Come home, rejoin the LAN, and take it as
its own run:

```bash
python3 scripts/measure_plex_latency.py \
  --label baseline-lan-control \
  --vantage lan \
  --repeats 10
```

Here the direct leg is *not* skipped, so the run probes the same endpoint twice
— once through Traefik on `:443` and once straight at `192.168.1.110:32400` —
and prints the headline the A/B exists for:

```
Traefik overhead on /identity (median TTFB): +9.4 ms
```

That difference is the only number that isolates the reverse proxy from the
network. The external run in §3a cannot produce it, which is precisely why both
runs exist.

### 3c. Exit codes

| exit | meaning |
|---|---|
| `0` | everything it set out to measure was measured. |
| `1` | at least one target returned no usable sample — it never answered, or only ever answered with a status (a `401`, a Traefik `404`/`502`) that means it did no work. **The record is written before this is returned**, so the measurement is on disk. |
| `2` | bad arguments — nothing was probed. Fix the command and re-run; nothing was lost. |
| `3` | the measurement succeeded but the record **could not be written**. This outranks `1`: the endpoints are fine and the *data* is what was lost, so the report on stdout is the only remaining copy. **Save it before you close the terminal.** |

A non-zero exit on a `1` is not a reason to re-run blindly — read the `status`
column first. A `401` everywhere means the token is stale, not that Plex is slow.

### 3d. Where the numbers land

Every run appends one JSON record to `logs/plex-latency.jsonl` (override with
`--out`, or suppress with `--no-log` for a throwaway run). The current schema
version is **4**.

> ⚠️ `logs/plex-latency.jsonl` already contains records at schema `1`, `2`, `3`
> and `4`, and only one is `4`. Versions 1–3 counted rejected requests (non-2xx)
> as if they were measurements. **Step 4 must filter on `schema == 4`** before
> diffing anything.

---

## 4. The UI-level number (browser DevTools)

The plan's Demo asks for **UI/library load times**, and a `curl`-style TTFB does
not capture full app-load time — the web app fetches a plan of assets and API
calls, and the wait a human complains about is when the library grid finishes
rendering, not when the first byte of the first request arrives.

Take this from the **same external network**, in the same sitting as §3a:

1. Open a **private/incognito** window (no warm cache, no extensions) and open
   DevTools → **Network** *before* navigating.
2. Tick **Disable cache**. Leave throttling **off** — the hotspot is the
   condition under test.
3. Navigate to `https://plex.yoonnation.com` and sign in if prompted.
4. Click into the **library** so the grid actually loads.
5. Record, from the Network panel:
   - the **TTFB** of the initial document request (hover the request →
     *Timing* → *Waiting for server response*),
   - the **TTFB** and duration of the first `/library/sections` XHR,
   - the panel's summary line: **`DOMContentLoaded`**, **`Load`**, total
     requests and transferred bytes,
   - a screenshot of the waterfall, saved outside the repo.

Write the numbers into §5 alongside the harness numbers. They measure different
things and both belong in the baseline: the harness number is what Steps 2–3
can move, the DevTools number is what the household actually perceives.

---

## 5. RESULTS — the external capture, taken 2026-07-28

> ✋ **Every cell here is either MEASURED or still `___`.** Do not estimate,
> interpolate or copy a number from a LAN run. Step 4 cannot tell an invented
> baseline from a measured one, and an invented one makes every conclusion drawn
> from the comparison false. An empty cell is a known gap; a fabricated one is a
> wrong answer.
>
> The external capture (§3a) is **done** — the rows below carrying numbers come
> from `logs/plex-latency.jsonl`, the record stamped
> `2026-07-28T02:43:04.348185Z`, and from nowhere else. Still owed, and still
> `___`: the LAN control (§3b), the DevTools numbers (§4), and the two metadata
> cells only the operator holds. `test_plex_latency_runbook_shape.py` pins that
> split row by row, so neither half can drift without the gate saying so.
>
> ⚠️ Before trusting these numbers for a comparison, read
> `docs/plex-remote-latency-audit.md` §4: the link this was taken on has a
> sample-to-sample RTT spread far larger than any effect Steps 2–3 could
> produce, so a Step 4 diff against this baseline cannot resolve one.

### Run metadata

| field | value |
|---|---|
| UTC timestamp of the run (from the report header) | `2026-07-28T02:43:04.348185Z` |
| vantage | `external` |
| network used (carrier / hotspot / other) | `___` |
| label passed to the harness | `baseline` |
| repeats | `10` |
| Plex version / server state at capture | `___` |

### Harness results (`scripts/measure_plex_latency.py`)

| endpoint | n | TTFB min / med / max (ms) | total min / med / max (ms) | status |
|---|---|---|---|---|
| traefik/identity | `10/10` | `157.0 / 293.2 / 485.6` | `157.0 / 293.3 / 485.7` | `200` |
| traefik/library/sections | `10/10` | `164.8 / 183.9 / 926.3` | `164.8 / 186.3 / 926.4` | `200` |
| direct/identity (LAN control only) | `___` | `___ / ___ / ___` | `___ / ___ / ___` | `___` |
| direct/library/sections (LAN control only) | `___` | `___ / ___ / ___` | `___ / ___ / ___` | `___` |

The external run passed `--skip-direct` (the backend is RFC1918 and unreachable
off-LAN), so its record is stamped `direct_probed=false` and the two `direct/`
rows stay unfilled until §3b runs on the LAN.

Headline from the LAN control — Traefik overhead on `/identity`
(median TTFB): `___` ms

### Browser DevTools results (§4)

| measurement | value |
|---|---|
| initial document TTFB | `___` |
| first `/library/sections` XHR — TTFB | `___` |
| first `/library/sections` XHR — duration | `___` |
| `DOMContentLoaded` | `___` |
| `Load` | `___` |
| requests / transferred | `___` |

---

## 6. What would make this measurement invalid

Any one of these means the capture is not a baseline. Check them before you
write anything into §5 — a baseline nobody can reproduce is worse than none,
because Step 4 will quietly compare against it anyway.

- **Measured on the LAN.** The whole point of §1. If `--vantage lan` is in the
  command, it is a control run, not the baseline.
- **A VPN or tailnet route is up on the client.** Tailscale, WireGuard or a
  commercial VPN can carry the "external" request straight back into the LAN or
  out through a completely different egress. Turn it off and re-check the
  address from §2 step 1.
- **Plex was asleep or its caches were cold.** The first library load after an
  idle period measures spin-up, not steady state. Wake it (§2 step 3) and, if
  the first sample is a wild outlier compared with the rest, note it rather than
  averaging it away.
- **A transcode was running.** A concurrent transcode — or any active stream —
  changes what the server has left to answer with. Check the Plex dashboard for
  active sessions and wait until it is idle.
- **Something else was saturating the uplink.** A backup, a large upload or
  another device streaming makes this a bandwidth measurement.
- **A stale token.** A `401` in the `status` column is a rejection, not a
  library load. The harness refuses to count it as a measurement and exits `1`;
  re-export a fresh `PLEX_TOKEN` and retake.
- **The two runs used different networks.** If Step 4's re-measurement is taken
  on a different carrier or in a different place from the baseline, the diff
  measures the move, not the changes.

---

## 7. When the capture is done

1. Fill in §5 and commit **this file** — the table only, never the token, never
   the raw report if you pasted a URL carrying `X-Plex-Token` into it.
2. Confirm the record landed:

   ```bash
   tail -n 1 logs/plex-latency.jsonl | python3 -c 'import json,sys; r=json.load(sys.stdin); print({k: r[k] for k in ("schema","label","vantage","timestamp","direct_probed")})'
   ```

   It must show `schema: 4`, the `label` and `vantage` you passed, and the
   timestamp of the run you just took. Copy that timestamp into §5.

   The record never contains the token — the harness does not write one — but
   confirm it anyway, since this file gets committed:

   ```bash
   grep -ci x-plex-token logs/plex-latency.jsonl   # must print 0
   ```
3. That closes Step 1. Step 4 re-runs §3a with `--label post-change` from the
   same vantage and diffs the two records.
