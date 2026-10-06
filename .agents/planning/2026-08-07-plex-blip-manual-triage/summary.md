# Summary — Plex Blip Manual Triage & Instrumentation

**Project:** `2026-08-07-plex-blip-manual-triage` · **Completed:** 2026-08-07

---

## What was asked

> Help me plan how to manually inspect a blip in plex uptime in the middle of a stream
> given the current set of metrics and logging that we enabled and also plan any
> additional logging or metrics tracking that can be used to triage.

## What happened

The planning session turned into a root-cause investigation. A log dump from the
morning of 2026-08-07 revealed a live blip, and following it produced a probable root
cause plus two defects in tooling that was believed complete.

---

## Artifacts

```
.agents/planning/2026-08-07-plex-blip-manual-triage/
├── rough-idea.md
├── idea-honing.md                              decisions taken, with provenance
├── research/
│   ├── current-telemetry-inventory.md          every signal today + its resolution limit
│   ├── blip-taxonomy-and-discriminators.md     10 failure classes, discriminator each
│   ├── triage-window-and-data-survival.md      the decay table
│   ├── instrumentation-gaps.md                 gaps priced by load-on-Plex
│   ├── prior-art-and-upstream.md               what 07-29 and 08-04 settled
│   ├── live-blip-2026-08-07-case-study.md      ★ the investigation
│   └── pve-host-telemetry-options.md           the PVE host decision
├── design/detailed-design.md                   10 components, data models, tests
├── implementation/plan.md                      10 steps, checklist, demos
└── summary.md                                  this file
```

---

## Key findings

**The 2026-08-04 remediation works, and was not enough.** `METRICS_MEDIA_COLLECTING_INTERVAL_SECONDS=1800`
holds — library sweeps run on a clean 31-minute cadence and **none occurred in the
blip window**. That earlier work identified an *amplifier*, not the trigger. A worse
blip followed on 2026-08-07: five minutes, peak request **108,832 ms** against 35,905 ms.

**The watchdog's lock-holder probes have never worked.** Across 34 snapshots, `fuser`
failed 34/34 — `psmisc` is not in the role's package list. `lsof` succeeded in all 22
healthy snapshots and **timed out in all 12 in-blip snapshots** against a hard 0.5 s
limit. The tool captured lock-holder data exclusively when nothing was wrong.

**The SQLite WAL is pinned at 43× its checkpoint threshold.** `journal_mode=wal` is
correctly set, but `-wal` is **41.71 MiB** against a 40.9 MiB database,
`freelist_count = 0`, and the file has been byte-identical across 42.5 hours spanning
both blips. Plex has not been restarted in the entire retained window. This is the
leading root-cause hypothesis.

**A guard passes green over a live fault.** The 08-04 audit asserts
`journal_mode == 'wal'`. That assertion is *true*. It checks the wrong property.

**The escalation is measurable.** Normalised per 1,000 `/:/timeline` requests:
`0.00 → 0.00 → 0.00 → 0.00 → 19.87 → 338.71` across six rotated logs. Zero over three
days and 5,296 requests, then a step change and a 17× acceleration — with *less*
streaming producing *more* lock holds.

---

## Two hypotheses this investigation killed

Recorded because the reasoning that killed them is reusable.

**"The watchdog is the new amplifier."** Deployed 15:38, escalation began 23:08 — a
correlation strong enough to be the leading hypothesis, and a fitting one given that a
monitoring component caused the 08-04 outage. Refuted by a natural experiment already
in the logs: item 377 played for 2 h 17 min *after* the deploy — 1,617 timeline
requests, **zero** `Held transaction` events.

**"Item 378 is pathological."** The database settled it: 377 and 378 share a section
and type and were added **125 seconds apart in January 2023**. Structurally
indistinguishable. The clean/dirty split was coincidental timing.

## Two of my own claims that were wrong

**"The watchdog fires 49 seconds late."** It fired **52 ms** after the first ≥500 ms
completion, via a trigger I had overlooked. The `Held transaction` gap costs
*attribution*, not latency — which the design now states as the justification, so
nobody re-derives the wrong one.

**"`/identity` is the safe probe target."** Right about cost, wrong about sensitivity.
It returned HTTP 200 on every probe through the five-minute outage, worst case
1,761 ms, while `/status/sessions` reached 101,394 ms. A `probe_success` alert on it
would have stayed green throughout. The design now pairs the two probes and alerts on
duration.

---

## The design

Four principles, each earned: **fix what exists before adding what doesn't**; **price
every addition by load on Plex** (monitoring caused the 08-04 outage); **order by
decay, not importance**; **a guard must assert the property that matters**.

Ten components across capture → durable → detect → use. Capture is repaired *before*
detection is added, because an alert firing into a broken capture path buys a page and
no evidence.

The design is validated by an experiment rather than by unit tests: deploy, confirm the
WAL alert fires against the known-live fault, checkpoint, confirm it clears, stream an
evening, count `TX_HELD`. Zero confirms the mechanism; a recurrence means a long-lived
reader is blocking checkpoint reset. Either outcome names the next move.

## The plan

Ten steps, each test-driven and independently demoable. **Steps 1–3 need no new
infrastructure** and each would have changed the 2026-08-07 investigation on its own.
Every parser change is tested against **real fixtures** — 92 MB of logs from both blip
windows and 448 KB of watchdog snapshots.

Decisions taken at review: Alertmanager deferred (rules still ship and evaluate);
`prometheus-node-exporter` from Debian main on the PVE host; checkpoint after Steps
1–4; WAL threshold 8 MiB; client-side evidence out of scope.

---

## Suggested next steps

1. Read [design/detailed-design.md](design/detailed-design.md) — §1.2 for the findings,
   §10 for the decisions table.
2. Read [implementation/plan.md](implementation/plan.md) and work the checklist.
3. **Consider doing Step 1 by hand today.** Adding `psmisc` is one line, and until it
   lands every blip continues to produce snapshots with no lock-holder data.
4. Run the Step 10 experiment once Steps 1–7 are in. It is the thing that converts a
   strong hypothesis into a root cause.

## Areas that may need refinement

- **The WAL hypothesis is strong but unproven.** A constant WAL size is not by itself
  proof that checkpointing stopped — SQLite reuses a WAL in place. The reasoning is
  laid out in case study §9.3 and the experiment is designed to falsify it.
- **`FSYNCS/SECOND: 385`** on `pve-root` is low for NVMe and may be a contributing
  factor. Step 6 makes it observable; nothing yet explains it.
- **Class G (client-side) is blind by decision.** Out of scope, and the runbook says so
  rather than implying it can be inferred.
- **R13 is only partly met** while Alertmanager is deferred — detection is pull, not
  push.
- **`DASPool` is a single USB vdev with no redundancy** and its last scrub took
  2 d 13 h. Not implicated in this fault; a real availability risk on its own terms and
  worth a separate project.
- **The notification receiver** remains unchosen whenever Alertmanager is picked up.

---

## Handing off to implementation

This SOP ends at planning. To start the Ralph loop yourself:

```bash
ralph run --config presets/pdd-to-code-assist.yml --prompt "Implement Step 1 of .agents/planning/2026-08-07-plex-blip-manual-triage/implementation/plan.md"
```

or

```bash
ralph run -c ralph.yml -H builtin:pdd-to-code-assist -p "Implement Step 1 of .agents/planning/2026-08-07-plex-blip-manual-triage/implementation/plan.md"
```
