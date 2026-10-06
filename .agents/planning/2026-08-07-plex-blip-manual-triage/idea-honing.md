# Idea Honing — Manual Triage of a Mid-Stream Plex Uptime Blip

> **Provenance note.** The usual one-question-at-a-time honing was not run. At the
> Step 2 checkpoint the operator chose **"Preliminary research first"**, and the
> research phase then produced a live-blip investigation that answered most of the
> questions honing would have asked — empirically rather than by preference.
> What follows records the decisions that were actually taken, in order, with the
> options that were on the table at the time.

---

## Q1. How should this planning session start?

**Options offered:** requirements clarification (default) · preliminary research
first · operator supplies additional context first.

**Answer: Preliminary research first.**

Rationale carried forward: two adjacent projects already existed
(`2026-07-29-plex-monitoring`, `2026-08-04-debug-plex-blip`, the latter reporting
all implementation steps complete), so the state of the world needed establishing
before scope could be set.

---

## Q2. Is the proposed five-topic research plan right?

**Options offered:** run all five · add client/player-side evidence · add a live
mid-blip probe · drop the prior-art topic.

**Answer: Plan is good — run all 5.**

Scope fixed as: `current-telemetry-inventory`, `blip-taxonomy-and-discriminators`,
`triage-window-and-data-survival`, `instrumentation-gaps`, `prior-art-and-upstream`.

---

## Q3. Which search tools should be used?

**Options offered:** web search + fetch · repo only · also read live system state ·
also search Google Drive / Dropbox.

**Answer: Web search + fetch** (alongside repo reading). Live system access was
**not** granted at this point — a constraint that shaped the research, and one that
was later reversed in Q5.

---

## Q4. Is the research sufficient to move on?

**Options offered:** go to requirements clarification · go straight to design ·
needs more research.

**Answer: Needs more research first — "Also take a look at the most recent logs
dump in /tmp/plex-logs/2026-08-07".**

This became the single most consequential input to the project. It produced
[research/live-blip-2026-08-07-case-study.md](research/live-blip-2026-08-07-case-study.md)
and falsified part of the 2026-08-04 diagnosis.

---

## Q5. Where next, after the case study?

**Options offered:** design now · operator runs the live checks · grant read-only
live access · requirements clarification.

**Answer: "Let me run the live checks first."**

The operator executed the six read-only checks on CT 110 and the PVE host and
returned the output. This reversed the Q3 constraint in practice and produced the
root-cause finding (§9 of the case study): a WAL pinned at 43× the checkpoint
threshold, and two watchdog probes that have never functioned.

---

## Q6. Proceed to detailed design?

**Answer: Yes.**

---

## Requirements established (by evidence rather than by preference)

These are the requirements the design must satisfy. Each traces to a specific
finding rather than to a stated preference, and each is marked accordingly.

| # | Requirement | Source |
|---|---|---|
| R1 | Produce a **manual triage procedure** a human follows when a stream drops mid-playback, using telemetry that exists today | original request |
| R2 | Produce a **gap analysis and instrumentation plan** for what to add | original request |
| R3 | The procedure must be ordered by **evidence decay**, not by importance — Tier-0 state dies in seconds | `triage-window-and-data-survival.md` |
| R4 | It must **not require restarting Plex** as a first step; the transcode dir is tmpfs and a restart destroys evidence (and now also masks the WAL state) | decay analysis + §9.3 |
| R5 | It must distinguish **"Plex was down" from "the exporter timed out" from "the proxy failed"** | inventory §2.1 |
| R6 | It must include the **banner-vs-restart** discriminator | case study §4 |
| R7 | It must state that **`dmesg` inside CT 110 is empty by design** and kernel evidence comes from the PVE host | case study §9.5 |
| R8 | New instrumentation must be priced by **load imposed on Plex** — monitoring has already caused one outage here | `instrumentation-gaps.md` preamble |
| R9 | **Fix the tools that already exist before adding new ones** — `fuser` has failed 34/34, `lsof` fails 12/12 in-blip | case study §9.2 |
| R10 | Health probes must alert on **duration**, not only success — `/identity` stayed 200 through a 5-minute outage | case study §6 |
| R11 | Guards must assert the property that **actually matters** — the WAL audit passes green while the pathology is live | case study §9.6 |
| R12 | **WAL size** must become a first-class monitored signal | case study §9.3 |
| R13 | Detection must not depend on a human noticing a paused stream | `instrumentation-gaps.md` §1 |

---

## Q7. Design review — the five open questions

**Answers, in order:**

1. **Alertmanager: defer.** Alert *rules* still ship (they evaluate and are visible in
   Prometheus and Grafana); only push delivery and the receiver choice are deferred.
2. **node-exporter on the PVE host: research it first before deciding.** → Q8.
3. **Checkpoint the WAL after C1–C4 land**, not before. Keeps the validation
   experiment intact: the alert gets proven against a known-live fault.
4. **WAL threshold of 8 MiB: confirmed.**
5. **Nothing pulled back into scope — client-side stays out.** Class G is blind by
   decision.

---

## Q8. PVE host telemetry — after research

Research written to
[research/pve-host-telemetry-options.md](research/pve-host-telemetry-options.md).
Findings: Proxmox staff endorse node_exporter on the host; Proxmox's own External
Metric Server does not support Prometheus and adds no signal we lack; `pve-exporter`
provably covers no ZFS/SMART/disk-latency; and the Plex database sits on `pve-root`,
making host disk latency a live suspect rather than a speculative gap.

**Options offered:** pinned static binary + persistent journald (recommended) ·
Debian package instead · journald only, no exporter.

**Answer: Debian package** (`prometheus-node-exporter` from Debian main).

Trade recorded: the package receives security updates automatically, which a pinned
binary would not; in exchange it joins the host's apt dependency graph and upgrades on
Debian's schedule rather than ours. Debian main is not a third-party repository, so
the dependency-conflict warnings that circulate about Proxmox host customisation
largely do not apply. `apt-mark hold` remains available if version control is wanted
back.

---

## Open questions deferred to implementation

- **Notification path for alerts** — needed only when Alertmanager is picked up
  (deferred at Q7). Telegram is unwired in this repo
  (`[[ralph-robot-telegram-unwired]]`); ntfy, webhook, email, or the existing
  uptime-kuma push endpoint are the candidates.
- **`zpool status` / SMART textfile script** — the collector and directory are
  provisioned by C10; populating them waits for a reason.
- **DAS redundancy** — `DASPool` is a single USB vdev, scrub took 2 d 13 h. Out of
  scope here; raised as a separate availability risk.

**Settled, not deferred:** client-side/player-side evidence (Tautulli and similar) is
**out of scope** by operator decision at Q7.5. Failure class G — "did the client give
up, or did the server drop it?" — therefore stays undecidable, and the runbook must
say so rather than implying it can be inferred.
