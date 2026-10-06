# Implementation Plan

## Checklist
> **QUEUE-STATE CORRECTION, 2026-08-01 (Planner, `queue.advance` after 5d closed — DEC-154).**
> Every line below that says an operator gate is OPEN was true when written and **three of the four
> are no longer true**. `task-1785290391-b51a` (1b), `task-1785324247-3934` (2b) and
> `task-1785370581-de17` (3b) are all `status: closed` on the queue's own record. Corroborating:
> `ansible/group_vars/all/vault.yml` is MODIFIED in the working tree, mtime 2026-07-30 01:56 —
> between 2a's close and 3b's — and every hat in this objective declared "no vault value" in every
> round, so that edit is the operator's; and `task-1785460529-aeb4`, the 4b Critic's own question
> about exactly this, is itself closed. **The limit, stated rather than glossed:** this is the
> QUEUE's state, not a live verification — no agent re-ran a query, and no agent should reopen an
> operator's own gate on suspicion. **Exactly ONE operator gate is open: 4d.**

- [x] Step 1: Add Traefik Histogram Buckets — **1a repo change CLOSED**; **1b operator gate CLOSED**
      (see the correction above). It was blocked by 2a (2026-07-29, review round 3): 1b's evidence is
      a Prometheus query and Prometheus had been crash-looping in production since 15 July on an
      unreadable 0640 config — 2a's `mode: "0644"` is the repair, so 1b could not pass until 2a was
      in the tree. It is, and the gate is closed.
- [x] Step 2: Create Proxmox API User and Deploy PVE Exporter — **2a repo-side CLOSED 2026-07-30**
      (Finalizer, after 15 review rounds; guard `1a95b475`, `just test` 35/35); **2b operator gate
      CLOSED**. 2a's `mode: "0644"` discharged the 1b/2b blocker and one `just play` satisfied both.
- [x] Step 3: Deploy Plex Media Server Exporter — split 3a/3b at the secret line (DEC-055).
      **3a repo-side CLOSED 2026-07-30** (Finalizer, after 12 review rounds; guard `2fe4bc38`,
      `PASS: 41/41`, `just test` GATE PASS 35/35 rc=0, Finalizer's own 6/6 adversarial battery in
      `logs/final-step03a-adversarial.log`). **3b operator gate CLOSED 2026-07-30T23:13Z.** No
      agent-side work and no open gate remains in Steps 1, 2 or 3.
- [~] Step 4: Import and Configure Grafana Dashboards — **AGENT-SIDE DONE 2026-07-31**, 4d operator gate open; **4a CLOSED 2026-07-31**, **4b CLOSED 2026-07-31** (Finalizer, after 6 review rounds; guard `396ecd28` PASS 13/13, `just test` GATE PASS 36/36 rc=0, Finalizer battery `logs/final-step04b-adversarial.py` 9/10 — the 1 was an OPEN FINDING for the Planner: `templating` has no guard row, see progress.md). **THAT FINDING IS MATERIALIZED, NOT BANKED — `task-1785497167-e413` (`code-assist:plex-monitoring:guard:dashboard-template-vars-declared`, P2), created 2026-07-31 after the Planner re-measured it: the guard source contained `templating` and `label_values` ZERO times, while `grafana-pve-dashboard.json` interpolates `$guest` in 13 targets across 11 panels off ONE declaration. **RE-MEASURED 2026-07-31 at the Step 5 cut and the `templating` half of that number is now STALE** — 4c's round 11 made it NINE, because `_dashboard_variable_queries` enumerates `templating.list[]` to read each variable's own query as PromQL. That is a different question; `label_values` is still zero, nothing compares an interpolated `$name` to a declared one, and F7/F7b are still GREEN. The finding stands, the number does not, and the correction is on the task.** **4c CLOSED 2026-07-31** (Finalizer, after 11 review rounds all on ONE clause of the PromQL reader; guard `a3b1595e` **PASS 18/18** — up 13 → 18 — `just test` GATE PASS 36/36 rc=0, dashboard `1e8f3617`, HEAD `7e9c426`, no commit). Finalizer's own work went where no round went: `logs/final-step04c-adversarial.py` **19/19** (all five AC (b) mutations RED, plus the delivery path and the five defects that POPULATE and are wrong, three controls GREEN), and `logs/final-step04c-grafana-loads.sh` **6/6** — **the pinned `grafana/grafana:13.1.0` booted OFFLINE against the delivered tree ACCEPTS all three dashboards**, holds `plex-health` with all 11 panels, resolves uid `Prometheus` in its own store, and DECLINES an invalid document (the adversarial row that makes the other five mean something). A repo-side guard proves the JSON parses; this is the first evidence Grafana will load it. **All agent-side work in Step 4 is now done. The only thing left in Step 4 is 4d, an operator gate.** 4d operator. Wave
      materialized (Planner, `queue.advance`): 4a `task-1785442414-452f`, 4b `task-1785442438-e959`,
      4c `task-1785442474-5022`, 4d `task-1785442499-1851` (operator).
      **CORRECTED — "needs no secret and does not split" was half wrong (DEC-068).** No secret is
      right; *does not split* is not. The split line in Steps 1–3 was never "the secret" as such,
      it was **the live line**: 1a/1b split with no secret at all. Step 4's acceptance is *open
      Grafana and see panels populate*, which is a browser against a running stack — so it splits
      the same way, 4a–4c repo-side and 4d operator.
- [x] Step 5: Close the guard findings that make a delivered artifact SILENTLY wrong — **CLOSED
      2026-08-01 (Planner, `queue.advance` after 5d). THE FOUR-ROW WAVE IS EXHAUSTED — 5a, 5b, 5c
      AND 5d ALL CLOSED. This was the LAST numbered step, so no Step 6 is cut (DEC-153) and the
      agent-side queue is empty BY DECISION, not by omission. What remains under this objective is
      eleven rows priced below this step's own bar with the reason recorded — the six Family-B
      deferrals, Family C `cd0e`, the three filed since (`579d`/`9df3`/`bad2`) and the 5c sweep
      residual `task-1785571952-8144` this close finally gave a carrier — and ONE operator gate,
      `4d`. Everything now depends on a browser David has not yet opened.**
      3 of the 4-row wave closed (5a, 5b, 5c); **5d was the only agent-side row left in it**,
      created 2026-07-31 (Planner, `queue.advance` after 4c closed). Nine agent-side tasks
      were ready and homeless; the Step 4c Finalizer asked whether they are one wave. **They are
      not** — priced in the Step 5 section. Wave is THREE (5a `task-1785497167-e413`,
      5b `task-1785517907-a5ec`, 5c `task-1785441840-e8eb`); six are DEFERRED behind it with the
      reason recorded, and two of the nine turned out to be ONE finding filed twice.
      **5a CLOSED 2026-07-31** (Finalizer, after 8 review rounds; the round-8 `review.passed`
      carried one docstring-exemplar defect and DEC-110's written pre-commitment routed it to the
      Finalizer, which corrected it in-hat and proved it docstring-only by an AST diff —
      `logs/finalizer-step05a-r8-exemplar.py` 14/14 — then ran plan.md's own Demo end to end for
      the first time, `logs/finalizer-step05a-demo.py` 9/9, F7b RED where Step 4b scored it GREEN
      13/13. Guard `5696b01b`, gate 36/36 rc=0, guard PASS 19/19, HEAD still `7e9c426`).
      **THE WAVE IS NOW FOUR:** `task-1785524605-ea55` (5d, the PVE dashboard's own drop-down
      declaration) was routed OUT of 5a by DEC-104 rather than smuggled into it, and has been ready
      and step-less since. It is Step 5 work by construction — the Planner gives it a home rather
      than letting the close leave a homeless ready task again, which is the exact defect that
      caused this step to be cut. Blocked by 5b: same guard file
      (`scripts/test_grafana_provisioning_shape.py`), the same reason 5b was blocked by 5a.
      **5b CLOSED 2026-07-31** (Finalizer, after ONE review round — the only row in this step that
      passed first time; guard `df94b58c` **PASS 20/20**, gate 36/36 rc=0, HEAD still `7e9c426`; the
      Critic's 59/59 single-carrier sweep found no fail-open at any position, and the round's one
      citation defect was corrected at its source with the calibration re-run against real
      `grafana/grafana:13.1.0`, `diff` = one line).
      **5c CLOSED 2026-08-01** (Finalizer, after 5 rework rounds; guard `53338616` **PASS 42/42** —
      41 → 42 is the plan's own Demo clause — gate 36/36 rc=0, HEAD still `7e9c426`, no commit,
      templates `02a4c5c2`/`097eca50` untouched). The Finalizer's own work went where no round went:
      every prior battery MUTATED an existing carrier, so `logs/finalizer-step05c-new-twin.py`
      **10/10** swept the GROWTH direction instead — a twin ADDED to either provider is discovered
      (`examined` 7 → 8, the roster is a floor and not the population), GREEN when its clauses
      agree, RED naming the newcomer when the rule or the service is repointed or the sibling is
      absent. **5d `task-1785524605-ea55` ROUTED 2026-08-01** (Planner, this `queue.advance`) — it
      is the LAST agent-side row in Step 5. Closing 5c also discharged the last blocker on the six
      Family-B deferrals, so they are ready again; **they defer again, per the pre-commitment this
      plan wrote before they did** — 5d is still open, and 4d's operator evidence, the one input the
      re-pricing was waiting on, has NOT arrived (DEC-132). And the one judgement the pass rests on
      was re-measured rather than trusted:
      `logs/finalizer-step05c-f0-loudness.py` **12/12** confirms the review's F0 — the guard is
      **blind 8/8** to the `splitlines()`-vs-`b-char` class at the file provider's own carrier, and
      all eight draw a **go-yaml load error** from the real compose parser, so it is LOUD on
      delivery and correctly not filed. 5d `task-1785524605-ea55` is unblocked and is the
      row after it. 5b's close filed one new P3 (`task-1785534580-9df3`, the `.j2` truth source read
      raw, blocked by 5d) and unblocked `task-1785533369-cd0e`, which is **DEFERRED behind 5c+5d,
      not routed** — DEC-121, priced in the Step 5 section.
      **5d `task-1785524605-ea55` CLOSED 2026-08-01** (Finalizer, after 11 review rounds, all
      of them on the same class one field over; guard `e8d62f31` **PASS 21/21**, gate 36/36
      rc=0, HEAD still `7e9c426`, no commit, delivered artifacts `a8a8c24e`/`1e8f3617` untouched).
      The Finalizer's own work went where no round went: every round asked the pinned engine what
      it REFUSES, and this row's claim is read off the BYTES ON DISK while the 4d operator meets
      what the engine STORES. `logs/finalizer-step05d-engine-stores-the-dropdown.py` **25/25** on
      the pinned `grafana/grafana:13.1.0` booted offline against the delivered tree — the stored
      `templating` entry keeps every key the row pins (name, type, both query spellings, `label`,
      and the four refusal keys `hide`/`regex`/`includeAll`/`multi`/`allValue`) and all 13 `$guest`
      references survive the save layer; **the engine SAVES all three mutations the row exists to
      refuse** (drop-down deleted with the references frozen, `hide: 2`, a rewriting `regex`) — the
      row's premise measured rather than asserted — and the guard REDs on each at the REAL delivery
      path with a verdict line and no traceback, restoring `a8a8c24e` byte-identically. The review's
      one finding is filed, not a rejection (`task-1785571102-579d`, `_read`'s raw-byte decode:
      pre-existing, untouched, outside r11's scope).
- [x] Step 6: Close the SILENT-class guard rows filed AFTER Step 5's wave was cut — **CLOSED
      2026-08-01. Wave EXHAUSTED at one row: `task-1785601096-9ffc` closed by the Finalizer after
      13 review rounds at guard `9c61b6112215`, every number re-run at the Finalizer's own hands
      (`just test` GATE PASS 36/36 rc=0, guard standalone PASS 22/22 — up 21 → 22 — `red-9ffc`
      73/73, r11 13/13, r12 19/19, r13 20/20, `critic-9ffc-r13-name-collision-classes` 12/12).
      HEAD stays `7e9c426`, no commit, no `just play`, no live call, gates 1b/2b/3b/4d untouched.
      The Finalizer's adversarial pass went at the round's DEFERRAL rather than its finding and
      MEASURED it with a real `ansible-playbook` (`logs/finalizer-9ffc-r13-h1-one-file-on-disk.py`
      8/8) — the deferral held, and that measurement is now filed as its own row
      (`task-1785621026-fc70`, see Step 7).** — **CUT
      2026-08-01 (Planner, `queue.advance` after `579d` closed at `c1fbc7b3`), DEC-182.** DEC-153
      said no Step 6 would be cut; that decision has since been TESTED THREE TIMES and answered.
      Iterations 88, 89 and 90 all met the empty queue and produced no event, and the operator's
      reply was to RESTART the runner rather than to open a browser — after which iteration 91 took
      a filed guard row (`579d`), and it ran build → 12 review rounds → pass → closed, closing a
      real hole. **DEC-153's premise ("everything left is either operator-gated or
      deferred-with-reasons") is no longer true**: `task-1785601096-9ffc` was filed 2026-08-01 by
      the review that closed `579d`, is priced here for the FIRST time, and clears Step 5's own
      bar — SILENT, no cause named by the engine, guard GREEN over it. Wave is **ONE row**:
      `task-1785601096-9ffc` (`code-assist:plex-monitoring:guard:duplicate-title-provider-lockout`,
      P2). Everything else defers on the reasons already recorded, unchanged. Queue hygiene done in
      the same turn: `task-1785504947-fbde` CLOSED as the duplicate of `b939` it was re-titled
      SUPERSEDED on 2026-07-31 and never retired.
- [x] Step 7: Close the MISDIRECTED-ALARM guard rows — the gate is RED and the verdict names a field
      the engine never looked at — **CUT 2026-08-01 (Planner, `queue.advance` after `9ffc` closed),
      DEC-194; CLOSED 2026-08-01, wave exhausted at its one row.** `task-1785594766-fb36` went
      build → 2 review rounds → PASSED → CLOSED at guard `a70d851ce802`, PASS 22/22, gate 36/36
      rc=0, HEAD `7e9c426`, no commit. Its Finalizer reported criterion (c) UNMET with the
      measurement that shows it was unsatisfiable when the task was written (DEC-196) rather than
      re-reading it to fit, and filed the round-2 Critic's finding as `task-1785624345-a15c`
      instead of patching it. Step 6 emptied the SILENT class of every row that clears its bar, so the bar moves
      one notch out to the class Step 6's own table named NEXT: a row that fires correctly and then
      sends the operator to the wrong field. Wave is **ONE row**: `task-1785594766-fb36`
      (`code-assist:plex-monitoring:guard:readable-row-rule-order`, P2) — the READABLE row is wrong
      in TWO directions, measured at 0/2 on whole gate runs, and the order to carry is already
      written down (`mem-1785592369-90dd`). Everything else defers on the reasons already recorded,
      unchanged. Queue hygiene done in the same turn: the H1 class the `9ffc` Finalizer flagged as
      the Planner's is now a runtime row, `task-1785621026-fc70` (P2) — it had existed only as
      `mem-1785620544-7b12`/`mem-1785620824-120c`. **Agent-actionable ready rows: 12 → 13.**
- [x] Step 8: Close the THIRD site of the misdirected-alarm defect — the READABLE row's PRESENCE
      GATE — **CUT 2026-08-01 (Planner, `queue.advance` after `fb36` closed), DEC-198; CLOSED
      2026-08-02, wave exhausted at its one row.** `task-1785622294-ba6c` went build → 1 review
      round → PASSED → CLOSED at guard `9c08e2b54dc2`, PASS 22/22, gate 36/36 rc=0, HEAD `7e9c426`,
      no commit. The presence gate became the SHAPE clause alone (DEC-199) and both policy halves
      moved INTO the chain — an ordering of four executable lines, not a deletion. Its Critic
      carried the one claim that outran its carriers (a sentence parameterised on
      `type(doc).__name__` claims all SIX non-dict json types; `logs/critic-ba6c-shape-class-types.py`
      13/13 on the pinned engine delivered the four that were missing, `mem-1785627131-ecba`), and
      its Finalizer re-expressed the delivered chain from the delivered predicates rather than
      calling the row (`logs/finalizer-ba6c-adversarial.py` 25/25: no old-RED → new-GREEN leak at
      any spelling of either half, both controls GREEN). The two undisclosed casualty harnesses
      were exonerated by counting the anchor at BOTH texts instead of reproducing the failure at
      one — `fb36` moved that call, not `ba6c` (`mem-1785630967-6fdd`). The bar has
      not moved; this is Step 7's own class continued. `fb36` repaired two of the three sites where
      `test_delivered_dashboards_parse_as_dashboards` names a field the engine never looked at and
      DEFERRED the third in writing (DEC-195), on `fb36`'s own atomicity and nothing else — a
      deferral that expired when `fb36` closed. Wave is **ONE row**: `task-1785622294-ba6c`
      (`code-assist:plex-monitoring:guard:presence-gate-precedes-every-engine-rule`, P2). Its
      evidence GREW after it was filed: a top-level JSON ARRAY is a THIRD carrier the description
      does not name (`mem-1785624803-6b47`), carried in the payload rather than `ensure`d into the
      record. Everything else defers on the reasons already recorded, unchanged; `task-1785624345-a15c`
      is named as the declared successor. Queue hygiene this turn: **nothing filed, nothing retired**
      — the `fb36` Finalizer's one adversarial finding is a NON-defect and a prohibition
      (`mem-1785624794-9c63`: do NOT add an `id` rule), not a task. **Agent-actionable ready rows:
      14, unchanged.**
- [x] Step 9: Close the FIRST spelling of the rule order — `_unreadable`'s save-layer chain fences
      the uid predicate with `isinstance()` alone — **CUT 2026-08-02 (Planner, `queue.advance` after
      `ba6c` closed), DEC-200; CLOSED 2026-08-02, wave exhausted at its one row.**
      `task-1785624345-a15c` went build → 4 review rounds → PASSED-naming-one-defect → **repaired
      IN-HAT by the Finalizer** (DEC-203 wrote the pre-commitment, DEC-204 took it) and CLOSED at
      guard `56bba79ef94e`, PASS 22/22, gate 36/36 rc=0, HEAD `7e9c426`, no commit. Round 1 was the
      whole executable repair — `refuses_uid` in the 4th slot, the predicate LAST, a `log=None`
      clause for the members the engine prints nothing for, measured one delivered file per ADJACENT
      PAIR on the pinned `grafana/grafana:13.1.0` (`logs/builder-a15c-red.py` 65/65) — and rounds
      2-4 were each ONE comment clause: scope the citation (DEC-202), then DISJOINT-not-a-partition
      with the third class NAMED, the carrier count pinned to `len(CASES)`, and the readable set
      BANKED as `task-1785635701-d2fd` rather than deferred in prose. The Finalizer's repair was the
      round's last owed identifier — a pointer that resolved at NO text, re-aimed at
      `logs/builder-a15c-r4-red.py` PART D, which is green at the sha the sentence ships at
      (`logs/finalizer-a15c-r4-repair.py` **22/22**: `ast.dump` identical with no docstring
      normalisation, the reverser's OUTPUT proved unmoved, the deliberate flip named by row).
      **`mem-1785636803-90cb`: a citation in shipped source must be GREEN at the sha it ships at —
      and a citation repair must check the CITED harness's own dependencies, not just the pointer.** The bar has not moved and this is not a new class: it is the LAST
      site of the same chain, the one spelling of it Steps 7 and 8 did not reach. Wave is **ONE
      row**: `task-1785624345-a15c`
      (`code-assist:plex-monitoring:guard:unreadable-chain-uid-halves`, P3). Re-measured at this cut
      rather than read off the filer's prose: `logs/critic-fb36-r2-unreadable-sibling.py` **6/6 at
      the DELIVERED guard `9c08e2b54dc2`**, so `ba6c` did not disturb it and the defect is live at
      the tree the Builder will start from. Everything else defers on the reasons already recorded,
      unchanged. Queue hygiene this turn: **nothing filed, nothing retired**, and `a15c` was NOT
      re-`ensure`d (its description is long and measured; `ensure` rewrites by key). **Agent-actionable
      ready rows: 13 — the Step 8 close's "14" counted the operator gate; see the arithmetic in the
      Step 9 section.**
- [~] Step 10: Close the DOCSTRING layer of the misdirected-sentence class — `_unreadable`'s
      blast-radius paragraph says FIVE readers pass `provisioned=` and the AST counts SIX — **CUT
      2026-08-02 (Planner, `queue.advance` after `a15c` closed at guard `56bba79ef94e`), DEC-205.**
      The bar has not moved and this is not a new class. `mem-1785632642-168d` wrote it down during
      this very thread: a guard whose sentences are the deliverable has its contract in THREE places
      — docstring, inline comment, printed clause — and a round that updates only one ships false
      sentences in the others. Steps 7/8/9 repaired the **clause** and the **comment** of the
      `_unreadable` chain. This is the **docstring**, and it is the only ready row that is a FALSE
      sentence in shipped source rather than a disclosed gap or a standing deferral. Wave is **ONE
      row**: `task-1785634257-80de`
      (`code-assist:plex-monitoring:guard:unreadable-provisioned-caller-count`, P3).
      **RE-MEASURED AT MY OWN HANDS AT THIS CUT** (`mem-1785631438-d7dc`): at the delivered guard
      `56bba79ef94e` there are **7** `_unreadable(...)` call sites, **SIX** pass `provisioned=`
      (`_delivered_dashboard_documents` :2151, and the five rows at :4501, :5339, :5635, :6022,
      :6443) and exactly one passes neither (:4809, the silent side, correct). The sentence at
      **:1170** still reads "the five readers". **The filer's LINE NUMBERS have moved** — a15c
      round 4's comment lines pushed :5621→:5635, :6008→:6022, :6429→:6443 — **the SET has not.**
      **ONE CORRECTION IS OWED TO THE ROW AND IT IS THE REASON THIS CUT RE-`ensure`d IT.** Its
      acceptance (d) names `logs/builder-a15c-r2-pre-guard.py` PART D as the inertness oracle. That
      harness is **DEAD at the delivered sha** — `AssertionError: anchor not unique/present`,
      measured this cut, because a15c round 3 rewrote the comment block it quotes
      (`mem-1785634963-bf38`) — **and it never had a PART D.** `logs/builder-a15c-r2-collateral.py`
      dies with it (it imports that reverser). The living reverser is
      `logs/builder-a15c-r4-pre-guard.py`, green here and chaining `821b687f6267` →
      `8cb7299e4568` → `54cec7fc4cea` → `9c08e2b54dc2`. And a docstring round needs the
      **normalised** dump oracle (`mem-1785633523-cbc8`), which rounds 3 and 4 did not need and did
      not ship — so the round must BUILD it on r4's reverser, not cite one. Handing a Builder an
      acceptance criterion that points at a harness which cannot run is the exact defect
      `mem-1785636803-90cb` names, one layer out into the queue record; **a correction to the
      CONTRACT is re-`ensure`d, unlike Steps 8/9 where new EVIDENCE rode in the payload.**
      Blast radius pre-measured and handed over: `logs/red-579d-r4-critic-recheck.py` is the only
      other file quoting the sentence and it is **already RED at the delivered tree (9/16, R14 at
      0x) before this row touches anything** — count the anchor at BOTH texts, do not reproduce the
      failure at one (`mem-1785630967-6fdd`). Everything else defers on the reasons already
      recorded, unchanged; `fc70` (P2) remains the bar-leader and is argued down, not glossed, in
      the Step 10 section. Queue hygiene this turn: **nothing filed, nothing retired.**
      **Agent-actionable ready rows: 14** — 13 at the Step 9 cut, minus `a15c` (closed, off the
      list), plus the TWO rows a15c's own rounds banked (`80de` and `d2fd`). After this cut `80de`
      is the wave and **13 rows defer**.

---

## Step 1: Add Traefik Histogram Buckets

- **Objective:** Tune the existing Traefik Prometheus metrics to use custom histogram buckets for meaningful latency analysis.

  > **CORRECTED 2026-07-29 (Planner, `queue.advance`).** This step originally prescribed
  > `[0.1, 0.3, 1.2, 5.0]` and called the incumbent "Go's defaults". Both were wrong and the
  > error was load-bearing: those four numbers are **traefik:v3.7.5's own default** for this
  > histogram (`docker run --rm traefik:v3.7.5 traefik --help` →
  > `--metrics.prometheus.buckets (Default: "0.100000, 0.300000, 1.200000, 5.000000")`), so
  > shipping them is a runtime no-op, and Traefik does **not** use client_golang's `DefBuckets`
  > here. That was the round-2 rejection; rounds 3–6 retuned the ladder. The text below is the
  > shipped ladder. See `progress.md` for the full chain.

- **General Implementation Guidance:**
  Edit `ansible/roles/docker_host/templates/traefik.yml.j2`. The `metrics.prometheus` block
  already exists; add a `buckets` block sequence under it with the **shipped ladder** —
  `0.00025, 0.0005, 0.001, 0.0025, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 1.0, 5.0, 30.0`.
  These are calibrated against what the series actually observes: **server-side handler
  duration**, which excludes TCP connect, the TLS handshake and client transit, so browser
  TTFB numbers are the wrong ruler. Guard the value, its location inside the block, and the
  existence of the series it measures, in `scripts/test_traefik_config_shape.py`. Then run the
  Ansible playbook (`just play`) to re-render the template and **restart** Traefik — `traefik.yml`
  is the STATIC config, so the file provider's `watch: true` (which governs `dynamic.yml` only)
  will not pick this up.
- **Test Requirements:**
  Repo side: `just test` green, with a mutation battery proving the new check is non-vacuous.
  Deploy side, after the playbook runs: query `traefik_entrypoint_request_duration_seconds_bucket`
  in Prometheus and confirm the shipped boundaries are present. Send a request to Plex via Traefik
  and confirm the latency lands in a plausible bucket (at or under `le="0.25"` for a healthy hit).
- **Integration:**
  This is a contained change to an existing, already-scraped config. Prometheus is already scraping
  Traefik at `traefik:8082` — no new scrape job needed.
- **Demo:**
  In Prometheus, query `traefik_entrypoint_request_duration_seconds_bucket{entrypoint="websecure"}`
  and see **14** `le` labels, including the decisive falsifier **`le="0.00025"`** — which cannot
  exist under Traefik's `0.1/0.3/1.2/5.0` default. Seeing exactly `0.1 / 0.3 / 1.2 / 5.0 / +Inf`
  and nothing else means the restart did not take.
  **PRECONDITION added 2026-07-29:** none of this is queryable today. Prometheus itself is down
  (see Step 2a's item 5), so the first thing 1b's operator must confirm is that
  `docker ps --filter name=prometheus` reads `Up` and not `Restarting`. A Traefik 404 on
  `prometheus.yoonnation.com` means the container is still cycling, not a routing fault. Expect an
  empty TSDB: every series starts at that deploy.

## Step 2: Create Proxmox API User and Deploy PVE Exporter

- **Objective:** Collect resource metrics (CPU, memory, disk I/O, network I/O) for the PVE host and all LXC containers, including the Plex CT 110.

  > **SPLIT AT THE SECRET LINE 2026-07-29 (Planner, DEC-036).** This step is six items and only
  > items 1 and 6 need a human. **2a** is the repo-side half (defaults, `env.j2` reference,
  > compose service, scrape job, shape guard, `just test` green — no live anything) and is
  > buildable NOW; **2b** is the operator gate (mint the token, put the value in the vault,
  > `just play`, confirm live). 2a does **not** block on Step 1b — it touches files 1b never reads.
  > The vault VALUE is separable from the variable REFERENCE, because `env.j2` renders every
  > secret with `| default('')`.

  > **CORRECTED 2026-07-29 (Planner, same pass).** The original item 5 —
  > `job_name: pve-exporter`, target `pve-exporter:9221` — is a **runtime no-op that reads as a
  > success**, and the original Test Requirement ("confirm the target is `UP`") would have
  > confirmed it. `prometheus-pve-exporter` is a **multi-target** exporter: PVE metrics are served
  > from **`/pve?target=<node>`**, while the default `/metrics` path serves only the exporter's own
  > scrape/process metrics. Scraping `pve-exporter:9221` on the default path therefore returns
  > `200 OK` → target **`UP`** → **zero `pve_*` series**. Same class as the Step 1 bucket defect
  > (a change that looks like a change but isn't, with acceptance criteria that confirm the wrong
  > thing). The falsifier below is metric-level, not target-level, for exactly that reason.

- **Reference facts established by the Planner (verified, not assumed):**
  - Exporter docs: `prometheus-pve-exporter` README (upstream `main`) — `/pve?target=…&cluster=1&node=1`;
    env-var config activates only when **`PVE_USER`** is set, and then reads `PVE_TOKEN_NAME`,
    `PVE_TOKEN_VALUE`, `PVE_VERIFY_SSL`.
  - Guest series (`pve_up`, `pve_cpu_usage_ratio`, `pve_memory_usage_bytes`,
    `pve_network_receive_bytes`) come from the **cluster** collectors; `id` labels are
    `node/<name>`, `lxc/<vmid>`, `qemu/<vmid>`.

  > **CORRECTED 2026-07-29 (Builder, Step 2a rework — review round 2).** This bullet used to end
  > "so **`cluster=1` is required**", and that was **false**. Measured against the shipped
  > `prompve/prometheus-pve-exporter:3.9.0`, not read off the README: `pve_exporter/http.py`
  > declares `def on_pve(self, module='default', target='localhost', cluster='1', node='1')` —
  > `cluster` and `node` **already default to 1**. A/B against a stub PVE API logging request
  > paths: with the params and with no params at all, the API-call set and the metric set are
  > **identical** (`cluster=0&node=0` makes zero calls, as the control). So the params are a
  > runtime no-op; they are still written out for legibility, and the guard still pins them, but
  > **stated as stricter-than-runtime rather than as the thing that produces the series**. The
  > pins that actually carry the contract are `metrics_path: /pve` and the `__param_target`
  > relabel (`target` defaults to `localhost`). The same false claim had reached the guard
  > docstring, the template comment, both runtime tasks and a memory; all corrected in the same
  > pass, because fixing one copy is what lets the number re-derive.
  - PVE endpoint is `192.168.1.50` (`mise.toml:31`, `PROXMOX_VE_ENDPOINT`) — committed and
    non-secret, so it belongs in role defaults, not the vault.
  - The PVE cert is self-signed (`PROXMOX_VE_INSECURE=true`, same file), so **`PVE_VERIFY_SSL=false`**
    is required or every scrape errors and the target is DOWN.
  - Concrete image pin available: `prompve/prometheus-pve-exporter:3.9.0`. The tag MUST be a
    three-part version — `test_no_floating_service_image_tags` in
    `scripts/test_traefik_config_shape.py` reddens on any `docker_host_*_image` that is not.

### Step 2a — Repo-side wiring + shape guard (agent-closable, no live infrastructure)

- **General Implementation Guidance:**
  1. `ansible/roles/docker_host/defaults/main.yml`: add `docker_host_pve_exporter_image`
     (concrete-pinned), plus the non-secret PVE coordinates — the API host (`192.168.1.50`),
     `PVE_USER` (`prometheus@pve`) and the token NAME. Only the token **value** is a secret.
  2. `ansible/roles/docker_host/templates/env.j2`: add the token value sourced from the vault as
     `{{ vault_pve_api_token | default('') }}`, following the `CF_DNS_API_TOKEN` /
     `GF_SECURITY_ADMIN_PASSWORD` pattern exactly. `default('')` is what makes 2a landable before
     the operator mints anything.
  3. `ansible/roles/docker_host/templates/compose.yml.j2`: add a `pve-exporter` service modeled on
     `node-exporter` / `cadvisor` — scrape-only, **no Traefik labels**, no published ports. Read
     the secret from the sibling `.env` with the established `${VAR:-}` indirection, never a
     literal. Pass `--no-collector.config` (one PVE API call per guest otherwise).
  4. `ansible/roles/docker_host/templates/prometheus.yml.j2`: add the scrape job using the
     **multi-target** shape — `metrics_path: /pve`, `params: {module: [default], cluster: ['1'],
     node: ['1']}`, and the PVE node as the relabel target with `__address__` replaced by
     `pve-exporter:9221`. A job that omits `metrics_path: /pve` is the no-op described above.
  5. `ansible/roles/docker_host/tasks/main.yml` + `handlers/main.yml`: **deliver** the rendered
     scrape config. Rendering it is not delivering it — `prometheus.yml` is a read-only bind mount
     read once at start, `docker compose up -d` does not touch a container whose own spec is
     unchanged, and there is no `--web.enable-lifecycle`, so `POST /-/reload` is 403. The render
     task needs `notify: Restart prometheus` and a handler mirroring `Restart traefik`. It also
     needs `mode: "0644"`, not the 0640 the other renders use: `prom/prometheus` runs as `nobody`
     and cannot read a 0640 root:root config. **CORRECTED 2026-07-29 (review round 3):** that mode
     is not a precaution taken on account of the new restart — it is the **repair of a live
     outage**. Read off the host: `stack-prometheus-1` has been `Restarting` since 2026-07-15,
     RestartCount 20801, `permission denied` every ~60 s, TSDB empty since 28 May,
     `prometheus.yoonnation.com` 404. `restart: unless-stopped` had been re-reading that file all
     along. Every Prometheus-backed gate in this plan — including Step 1b — has been unpassable
     since before this objective started.
     And **the restart is only the LAST hop.** Delivery is `dest` → the bind mount's host side →
     its container side → `--config.file` → the restart, and the guard must pin all of it: with
     only the restart pinned, dropping the bind mount is SILENT (Prometheus boots on the image's
     own default config, scrapes only itself, target UP, nothing errors).
  6. Guard all of it in `scripts/test_traefik_config_shape.py` (it already owns `compose.yml.j2` and
     `prometheus.yml.j2` and carries `_compose_service_block` / `_scrape_target_port`), with a
     mutation battery proving each new check is non-vacuous — including the delivery path, which a
     content-only guard structurally cannot see.
- **Test Requirements:** `just test` green (currently 35/35), the new guard failing under mutation,
  and no live call of any kind. Nothing here touches the household stack.
- **Demo:** `just test` → GATE PASS with the new checks counted, and `git diff` showing a
  `pve-exporter` service that carries no Traefik labels and a scrape job whose `metrics_path` is
  `/pve`.

### Step 2b — Operator gate: mint the token, vault the value, deploy, confirm live

- **General Implementation Guidance (OPERATOR ONLY — an agent MUST NOT close this):**
  1. In the Proxmox Web UI, create user `prometheus@pve`, assign role `PVEAuditor` at path `/`
     (with propagate), and generate an API Token whose ID matches the token name 2a wrote into the
     role defaults. Uncheck "Privilege Separation" or grant `PVEAuditor` to the token itself.
  2. Put the token's secret value in `ansible/group_vars/all/vault.yml` as `vault_pve_api_token`.
  3. Run `just play` to render `.env`, `compose.yml` and `prometheus.yml` and restart the stack.
- **Test Requirements:**
  The decisive check is **metric-level, not target-level** — a `UP` target proves only that the
  exporter answered, which a misconfigured path also does. In Prometheus query
  **`pve_up{id="lxc/110"}`**: it must return a series (value `1`). Then confirm
  `pve_cpu_usage_ratio` returns data for both `lxc/110` (Plex) and `lxc/111` (docker-host), and
  that `pve_network_receive_bytes{id="lxc/110"}` is populating.
  **What failure looks like**, most likely first:
  - **No `pve-exporter` job at all** in `Status → Targets` (not DOWN — absent), and
    `count(up{job="pve-exporter"})` is empty. Prometheus did not re-read its config. 2a wired
    `notify: Restart prometheus`, so this should not happen; if it does, check that the handler
    actually ran in the `just play` output.
  - **The whole Prometheus container is STILL down / restarting.** This is the pre-existing outage
    above, not a new symptom. Check `docker logs stack-prometheus-1` for `Error loading config ...
    permission denied` and `stat -c %a /opt/stack/prometheus/prometheus.yml` — 644 means 2a's
    repair deployed, 640 means it was not in the tree when `just play` ran.
  - Target `UP`, every `pve_*` query "Empty query result" — the scrape hit the default `/metrics`
    path. Not a token problem. (`cluster=1`/`node=1` are **not** a candidate cause: they are the
    exporter's own defaults — see the correction under Step 2's reference facts.)
  - Target `DOWN` with a TLS error — `PVE_VERIFY_SSL` was left `true`.
  - Target `DOWN` with `401`/`403`, or HTTP `500` "No valid authentication credentials were
    supplied" — the token value, the Token ID vs the role default, or the `PVEAuditor` grant.
- **Integration:**
  Follows the established pattern: new Docker service in the Compose stack, new scrape job in
  `prometheus.yml.j2`, secrets via Ansible Vault → `.env`. All existing services are unaffected.
  `just play` is `ansible-playbook site.yml` only — no tofu, so no CT is recreated.
- **Demo:**
  Open Prometheus and query `pve_memory_usage_bytes{id="lxc/110"}` to see real-time memory usage
  for the Plex container.

## Step 3: Deploy Plex Media Server Exporter

- **Objective:** Extract application-level metrics from Plex, including stream states, transcoding activity, and active sessions.

  > **SPLIT AT THE SECRET LINE 2026-07-30 (Planner, DEC-055), same as Step 2.** **3a** is the
  > repo-side half (defaults, `env.j2` reference, compose service, scrape job, shape guard,
  > `just test` green — no live anything) and is buildable NOW; **3b** is the operator gate
  > (read the Plex token, put the VALUE in the vault, `just play`, confirm live). The vault VALUE
  > is separable from the variable REFERENCE because `env.j2` renders every secret with
  > `| default('')`. Step 4 (dashboard JSON) needs no secret at all and does not split.

  > **CORRECTED 2026-07-30 (Planner, same pass) — the original Test Requirement below was
  > "confirm the `plex-exporter` target is `UP`", and that is the THIRD instance of this
  > objective's recurring defect** (Step 1's `[0.1, 0.3, 1.2, 5.0]` buckets that were Traefik's
  > own default; Step 2's job on the exporter's default `/metrics` path). Measured against the
  > exporter's actual source at tag `2.1.0` (`lib/middleware/collector.rb`, fetched, not
  > recalled): `plex_up` is set from Plex's **`/identity`** endpoint inside a
  > `rescue HTTP::Error` / `ensure` pair, while every series a dashboard would use
  > (`plex_sessions_count`, `plex_media_count`) comes from the **token-gated** endpoints
  > `/status/sessions` and `/library/sections`. So `UP` proves only that a Ruby web server
  > answered, and `plex_up 1` proves only that *something* at `PLEX_ADDR` replied to an
  > unauthenticated identity probe. The falsifiers below are therefore metric-level AND
  > token-gated. See the reference facts for the full contract.

- **Reference facts established by the Planner 2026-07-30 (verified against the upstream registry
  and the tagged source, not read off the research doc):**
  - **Image:** `ghcr.io/axsuul/plex-media-server-exporter:2.1.0` — the exporter the design doc
    selected (`design/detailed-design.md:119`), and the tag is a **three-part** version, so
    `test_no_floating_service_image_tags` (`scripts/test_traefik_config_shape.py`) stays green.
    Verified live: the ghcr tag list carries `1.0.0, 1.1.2, 1.1.3, 2.0.0, 2.1.0, latest` + 45
    commit-sha tags; `2.1.0` resolves to an OCI index (`sha256:ab89d0ba039e…`) with a
    `linux/amd64` manifest. **The runner-up cannot be used as pinned:**
    `ghcr.io/jsclayton/prometheus-plex-exporter` publishes **only `latest` and `main`** — no
    version tag exists, so it cannot satisfy the concrete-pin guard without a digest pin. That
    settles the design doc's "verify maintenance status before committing" item in axsuul's
    favour on availability grounds.
  - **Maintenance status (the other half of that item):** MIT, not archived, 78 stars, and the
    last release *and* last push are both **2024-12-22** — i.e. ~19 months stale as of today.
    Nothing is broken by that (the Plex HTTP API endpoints it calls are long-stable), but it is a
    fact the Builder should record rather than discover.
  - **Configuration is env-var only** (`collector.rb` `initialize`), defaults in parentheses:
    `PORT` (`9594`), `PLEX_ADDR` (`http://localhost:32400`), `PLEX_TOKEN`, `PLEX_TIMEOUT` (`10`),
    `PLEX_RETRIES_COUNT` (`0`), `PLEX_SSL_VERIFY` (`true`), `METRICS_PREFIX` (`plex`),
    `METRICS_MEDIA_COLLECTING_INTERVAL_SECONDS` (`300`). There is no config file and no CLI flag,
    so this service has **no `command:`** — one region fewer than `pve-exporter`.
    `PLEX_ADDR` defaulting to `localhost` matters: unset, the exporter probes **its own
    container** and every scrape is `plex_up 0` with the target still **UP**.
  - **It is NOT a multi-target exporter.** Metrics are served on the plain default `/metrics`
    path (`config.ru` → `Prometheus::Middleware::Exporter`; the collector runs only when
    `PATH_INFO == "/metrics"` exactly). So unlike `pve-exporter` the scrape job needs **no
    `metrics_path`, no `params`, and no relabel** — the whole Step 2 shape is *wrong* here, and
    copying it would produce a 404. Target is simply `plex-exporter:9594`.
  - **Metric names and label shapes** (verbatim from the README's own output at `2.1.0`):
    `plex_up` (no labels), `plex_info{version=…}`, `plex_media_count{title,type}`,
    `plex_sessions_count{state,user_id,username}`,
    `plex_audio_transcode_sessions_count{state,user_id,username}`,
    `plex_video_transcode_sessions_count{state,user_id,username}`,
    `plex_media_downloads_count{user_id,username}`. `state` is Plex's own player state —
    `playing` / `paused` / `buffering`. **Session series do not exist until a session exists**
    (`set_gauge_metric_values_or_reset_missing` writes nothing for an empty value set), and once
    a stream ends the series stays present at `0` rather than disappearing.
  - **A collection failure is not uniform, and the difference is load-bearing for 3b's failure
    list.** `plex_up` is wrapped in `rescue HTTP::Error` → on an unreachable `PLEX_ADDR` the
    scrape still returns 200 with `plex_up 0`. The three collectors are wrapped the same way —
    but `send_plex_api_request` ends in `JSON.parse(response)`, and **`JSON::ParserError` is not
    an `HTTP::Error`**, so a non-JSON body (which is what Plex returns for a rejected token)
    escapes every rescue and the `/metrics` request itself **500s** → target **DOWN**, no series
    at all. Expected, therefore: bad/absent token ⇒ DOWN with a 500, *not* a partially populated
    scrape. **The Builder must confirm this against a stub** the way Step 2a's `logs/calibration-step02a-f3.log`
    did for the PVE 401-vs-500 question, because 3b's failure list is written on it.
  - **Scrape budget is a real integration risk, not a nicety.** `collect_media_metrics` runs
    **synchronously inside the scrape request** and issues one `/library/sections/<key>/all` call
    per library section (plus a second for every `show` section), throttled to once per
    `METRICS_MEDIA_COLLECTING_INTERVAL_SECONDS` (300 s). `prometheus.yml.j2` sets a global
    `scrape_interval: 15s` and no `scrape_timeout`, so Prometheus' default 10 s timeout applies —
    and `PLEX_TIMEOUT` alone is 10 s **per request**. Every fifth minute one scrape does the
    library sweep and can exceed the budget. Prometheus also **refuses to load a config whose
    `scrape_timeout` exceeds its `scrape_interval`**, so the pair must move together (e.g. this
    job gets its own `scrape_interval: 60s` + `scrape_timeout: 30s`).

  > **CORRECTED 2026-07-30 (Builder, Step 3a).** This bullet used to end "`promtool check
  > config` inside `just test` catches the invalid pair", and that was **false** — the third
  > time this objective has shipped an unverified claim about what a check catches. `just test`
  > runs 35 steps (`scripts/run_gate.py`): 30 shape scripts, `tofu fmt/init/validate`,
  > `ansible-lint`, `ansible-playbook --syntax-check`. **There is no promtool step and nothing
  > in the gate renders this template**, so nothing in this repo would have caught an unloadable
  > scrape config before the operator's `just play`. The refusal itself is real and measured on
  > the pinned `prom/prometheus:v3.12.0` — `FAILED: … scrape timeout greater than scrape
  > interval for scrape config with job name "plex-exporter"`, rc=1 — but it is promtool run by
  > hand, not by the gate (`logs/calibration-step03a-scrape-budget.log`, R2). So the pair is
  > pinned in the shape guard, which is where the gate can see it. The measurement also found
  > the case that matters more, because Prometheus does NOT refuse it: a job-local
  > `scrape_interval: 60s` written **without** its timeout is rc=0 and loads with the 10 s
  > default still in force (R4) — the sweep scrape then times out and nothing anywhere says so.
  > `scrape_timeout: 30s` written without its interval IS refused (R3), so only one half of the
  > pair fails loudly.
  - The Plex address is already a role default: `docker_host_plex_url: http://192.168.1.110:32400`
    (`defaults/main.yml:50`) — the same cross-LXC path Traefik's file provider uses. Reuse it;
    do not write a second literal.

### Step 3a — Repo-side wiring + shape guard (agent-closable, no live infrastructure)

- **General Implementation Guidance:**
  1. `ansible/roles/docker_host/defaults/main.yml`: add `docker_host_plex_exporter_image:
     ghcr.io/axsuul/plex-media-server-exporter:2.1.0`. No other new default is needed — the Plex
     URL already exists as `docker_host_plex_url`, and the token is the only secret.
  2. `ansible/roles/docker_host/templates/env.j2`: add
     `PLEX_TOKEN={{ vault_plex_token | default('') }}`, following `PVE_TOKEN_VALUE` /
     `CF_DNS_API_TOKEN` exactly. `default('')` is what makes 3a landable before the operator
     reads anything out of `Preferences.xml`.
  3. `ansible/roles/docker_host/templates/compose.yml.j2`: add a `plex-exporter` service modeled
     on `pve-exporter` — scrape-only, **no Traefik labels**, no published ports, secret read from
     the sibling `.env` via the established `${PLEX_TOKEN:-}` indirection and never a literal.
     Set `PLEX_ADDR={{ docker_host_plex_url }}` (unset means it probes its own container) and
     `METRICS_PREFIX` left at its default so the metric names above hold.
  4. `ansible/roles/docker_host/templates/prometheus.yml.j2`: add the scrape job as an **ordinary
     single-target job** — `targets: [plex-exporter:9594]`, no `metrics_path`, no `params`, no
     relabel — plus the job-local `scrape_interval`/`scrape_timeout` pair the library sweep needs
     (see the scrape-budget fact). Copying Step 2's multi-target shape here is a 404, and a
     `scrape_timeout` above the job's `scrape_interval` makes Prometheus refuse the whole config.
  5. `scripts/test_traefik_config_shape.py`: guard all of it, with a mutation battery proving each
     new check is non-vacuous. The guard already owns these four files and now carries
     `_service_env_map`, `_service_mount_map`, `_kv_entries` and `_last_flag_value` from Step 2a —
     **reuse them**; `environment:` is one of the five regions whose duplicate-entry class Step 2a
     closed, so a second `PLEX_ADDR=` entry must redden. Pin at least: the concrete image, the
     absence of Traefik labels and published ports, `PLEX_TOKEN` reaching the service by
     indirection rather than as a literal, `PLEX_ADDR` resolving to `docker_host_plex_url`, the
     job's target/port, the **absence** of a `metrics_path` on this job (the Step-2 copy-paste
     defect), and `scrape_timeout <= scrape_interval` for it.
  6. No new delivery machinery: `prometheus.yml` already renders with `mode: "0644"` and notifies
     `Restart prometheus` (Step 2a), and `.env`/`compose.yml` already re-render. Confirm that
     rather than re-adding it.
- **Test Requirements:** `just test` green (currently 35/35), each new check failing under
  mutation, and **no live call of any kind** — including no request to `192.168.1.110:32400`. A
  stub-based calibration leg (the Step 2a pattern) is the right way to settle the bad-token
  500-vs-200 question without touching Plex.
- **Demo:** `just test` → GATE PASS with the new checks counted, and `git diff` showing a
  `plex-exporter` service with no Traefik labels and no published ports, and a scrape job with a
  bare `plex-exporter:9594` target and no `metrics_path`.

### Step 3b — Operator gate: read the Plex token, vault it, deploy, confirm live

- **General Implementation Guidance (OPERATOR ONLY — an agent MUST NOT close this):**
  1. Get the Plex token: either the web-app XML method (open any library item → **Get Info** →
     **View XML** → copy `X-Plex-Token` out of the URL), or read `PlexOnlineToken` from
     `Preferences.xml` in the Plex state directory (`/tank/Server/AppData/plex`, CT 110).
  2. Put the VALUE in `ansible/group_vars/all/vault.yml` as `vault_plex_token`.
  3. Run `just play` (`ansible-playbook site.yml` only — no tofu, no CT recreate).
- **Test Requirements:**
  Three checks, in this order, and **none of them is "the target is UP"** — a `UP` target here
  means only that the Ruby web server answered:
  1. **Reachability:** `plex_up` returns `1`. `0` means `PLEX_ADDR` is wrong or Plex is not
     answering; the target is still UP either way.
  2. **The token actually works:** `plex_media_count` returns series (one per library, `type` =
     `movie` / `show` / `artist`, plus a `… - Episodes` row per show library). This is the
     decisive token check, because `/library/sections` is token-gated while `plex_up`'s
     `/identity` probe is not. Allow up to
     `METRICS_MEDIA_COLLECTING_INTERVAL_SECONDS` (300 s) for the first sweep.
  3. **The streams half:** start a real stream on a client, then query
     `plex_sessions_count{state="playing"}` — it must return a series with value `>= 1`, labelled
     with the streaming user. Stop the stream and confirm it drops to `0` (the series stays
     present; it does not vanish). If the client is transcoding video,
     `plex_video_transcode_sessions_count{state="playing"}` populates too — that is the metric the
     buffering diagnosis in Step 4 is built on.
  **What failure looks like**, most likely first:
  - **No `plex-exporter` job in `Status → Targets`** (absent, not DOWN) — Prometheus did not
    re-read its config. 3a wires nothing new for this; the `notify: Restart prometheus` from
    Step 2a is what carries it, so check the handler ran in the `just play` output.
  - **Target DOWN with a `500`** — expected shape for a rejected/empty token, and **the ONLY
    shape a bad token produces**. Confirmed against a stub on the pinned
    `ghcr.io/axsuul/plex-media-server-exporter:2.1.0`
    (`logs/calibration-step03a-token.log`, rows B and E): the container stays RUNNING
    (`state=running`, RestartCount 0) and answers `/metrics` with HTTP 500 after exactly two
    upstream calls — `/identity`, which succeeds, then `/status/sessions`, which does not.
    Check `docker logs stack-plex-exporter-1`; the exporter prints `method=get url=…` per call
    and then the Rack error naming the cause.
  - **Target UP, `plex_up 0`, no other series** — `PLEX_ADDR` never reached Plex. Not a token
    problem. Confirmed (row D): all four collectors raise `HTTP::Error`, every one of them is
    rescued, and the scrape is a clean 200 carrying `plex_up 0` and nothing else.

  > **CORRECTED 2026-07-30 (Builder, Step 3a).** This list used to carry a fourth shape —
  > "**Target UP, `plex_up 1`, `plex_media_count` empty for >5 min** — token accepted the
  > identity probe but not the library read. This is the case the falsifier exists to catch" —
  > and it is **unreachable**. Measured, not reasoned: on a rejected token the FIRST token-gated
  > call (`/status/sessions`) already raises out of the collector, so the `/metrics` response is
  > a 500 and **no series at all are emitted — including `plex_up`**, which the exporter had
  > already set to 1 (rows B and E: `plex_up: 0 series`). There is no state in which `plex_up`
  > is visible at 1 while `plex_media_count` is missing for token reasons; the check-2 falsifier
  > is decisive because the scrape either fully succeeds or 500s, not because it catches a
  > partial one. The reasoning behind the old bullet was also narrower than the outcome: it
  > assumed Plex answers a rejected token with a NON-JSON body (`JSON::ParserError`, which is
  > not an `HTTP::Error`). That is what happens (row B), **but the outcome does not depend on
  > it** — with a JSON 401 body instead, `JSON.parse` succeeds and
  > `collect_media_metrics` then calls `.each` on the nil `Directory`, so it is
  > `NoMethodError` and still a 500 (row C). Bad token ⇒ DOWN, by two independent paths.
  - **Scrapes time out every ~5 minutes only** — the synchronous library sweep exceeded
    `scrape_timeout`. Raise the job's interval/timeout pair or
    `METRICS_MEDIA_COLLECTING_INTERVAL_SECONDS`.
- **Integration:**
  Same Compose + Prometheus pattern as Step 2, minus the multi-target shape. The exporter reaches
  Plex over the LAN at `192.168.1.110:32400` — the same cross-LXC path Traefik already uses, so no
  network changes are needed. All existing services are unaffected.
- **Demo:**
  While streaming a video, query `plex_sessions_count{state="playing"}` in Prometheus and see the
  count move as the stream starts and stops, with `plex_media_count` showing the real library
  sizes alongside it.

## Step 4: Import and Configure Grafana Dashboards

- **Objective:** Visualize all new metrics alongside existing ones to enable diagnosis of sporadic connection issues.
- **General Implementation Guidance:**
  1. Download or create Grafana dashboard JSON files for:
     - Proxmox PVE metrics (community dashboard ID `10347` is a good starting point)
     - Plex exporter metrics (check if the exporter ships with a recommended dashboard, otherwise create one)
  2. Place the JSON files in the Grafana dashboards directory provisioned by the Ansible role (mounted at `/var/lib/grafana/dashboards` inside the Grafana container, sourced from `{{ docker_host_project_dir }}/grafana/dashboards` on the host).
  3. The existing dashboard provider in `grafana-dashboards.yml.j2` auto-loads JSON files from this directory with a 30s update interval — no additional Grafana configuration is needed.
  4. Optionally create a composite "Plex Health" dashboard that overlays Traefik latency for the `plex@file` service, PVE container resource usage for CT 110, and Plex stream state on a single view.
- **Test Requirements:**
  Open each dashboard in Grafana and confirm panels populate with data. Verify that the Proxmox dashboard's container drop-down correctly lists CT 110 (Plex) and CT 111 (docker-host). Verify that the Plex dashboard shows session data during an active stream.
- **Integration:**
  Consumes the centralized Prometheus data from Steps 1–3 via the existing provisioned datasource. No datasource configuration changes needed.
- **Demo:**
  Open Grafana and view the Proxmox dashboard showing real-time CPU, memory, and network for the Plex LXC, alongside the Traefik dashboard showing request latency for the `plex@file` service.

### Wave (Planner, `queue.advance` 2026-07-30 — three repo-side tasks and one operator gate)

> **THREE CORRECTIONS TO THE GUIDANCE ABOVE, MADE BEFORE THE WAVE WAS CUT.** They are why 4a
> exists and why the "optional" item 4 is not optional.
>
> **(i) "No datasource configuration changes needed" is false, and item 3's "no additional
> Grafana configuration is needed" is false with it.** Two repo-side defects sit between the
> provisioned files and a rendered panel, and both are the *same class* as the `0640`
> `prometheus.yml` that had Prometheus crash-looping since 15 July — a config the container's uid
> cannot read:
> - **The modes.** `tasks/main.yml:94-102` creates `grafana/provisioning/{datasources,dashboards}`
>   and `grafana/dashboards` at `0750` root, and `:133-155` writes `datasource.yml`,
>   `dashboards.yml` and `homelab.json` at `0640` root:root. `compose.yml.j2:128-138` declares no
>   `user:`, so `grafana/grafana:13.1.0` runs as uid 472 and both mounts are `:ro`. Unreadable.
> - **The uid.** `grafana-datasource.yml.j2` provisions a datasource *named* `Prometheus` with no
>   `uid:`, so Grafana generates one; `files/grafana-homelab-dashboard.json` references
>   `uid: "Prometheus"` on every panel and target. A name is not a uid.
>
>   Neither is provable offline, so 4a is told to source them and to flip the fix if a measurement
>   contradicts either — a guard that forbids the real answer is the failure this repo has hit.
>
> **(ii) There is no Traefik dashboard to put "alongside" anything.** The Demo asks for one and
> `files/grafana-homelab-dashboard.json` is two node-exporter panels. Step 1 tuned the histogram
> ladder (`traefik.yml.j2:91-`) precisely so latency could be read and **nothing reads it.** So
> item 4's composite is the carrier for it, and 4c is a required task, not an optional one.
>
> **(iii) The dashboards cannot be downloaded.** The gate is offline; ID `10347` is a reference,
> not a fetch. 4b authors the JSON in-repo in the hand-written style of the existing file.

1. **4a — the provisioning path** (`task-1785442414-452f`, READY): the modes, the datasource
   `uid`, the existing dashboard's references, and a NEW `scripts/test_grafana_provisioning_shape.py`
   whose load-bearing row is *cross-file*: the provisioned uid and every delivered dashboard's
   datasource reference must AGREE, over an inventory of the files the role actually copies, so a
   dashboard added by 4b/4c cannot silently skip it. No new dashboards here.
2. **4b — the Proxmox dashboard** (`task-1785442438-e959`, blocked by 4a): `grafana-pve-dashboard.json`
   + delivery + guard rows. Templated over the guest id so the drop-down requirement (CT 110 and
   CT 111) is a variable, not two hard-coded panels.
3. **4c — the composite "Plex Health" dashboard** (`task-1785442474-5022`, blocked by 4a): traefik
   `plex@file` latency read off the Step 1 `_bucket` series, `plex_*` stream state, CT 110 resource
   usage, one view.
4. **4d — OPERATOR GATE** (`task-1785442499-1851`, blocked by 4a+4b+4c): `just play`, then open each
   dashboard and confirm the panels populate.

**THE ONLY pve_\* AND plex_\* SERIES THIS REPO HAS PINNED ARE `pve_up{id="lxc/110"}` AND
`plex_media_count` / `plex_sessions_count{state="playing"}`** — the acceptance lines of gates 2b and
3b. Every other series a panel names is a claim about an exporter no agent here can query, so 4b and
4c are both required to source each name or mark it unverified in the delivery comment, and 4d is
told that an empty panel is a real finding to route back rather than a nuisance. A green guard here
proves the JSON parses, the uid resolves, the delivery exists and the mode is readable. **It does not
prove a panel populates**, and three of the four series depend on gates 1b/2b/3b that have never run.

## Step 5: Close the guard findings that make a delivered artifact SILENTLY wrong

- **Objective:** Spend the remaining agent-side budget on the guard holes whose failure mode is a
  GREEN gate over a broken artifact, and stop spending it on the ones whose failure mode is loud.

- **Why this step exists at all.** Step 4 closed its last agent-side task (4c) with nine agent-side
  runtime tasks ready and belonging to no numbered step — eight `guard:*` rows banked by Builders,
  Critics and Finalizers across Steps 3 and 4, plus one P3 battery flip. The Finalizer routed the
  pricing question to the Planner: *are the eight one wave, or eight independent P2s?* Neither.
  They are three families with three different values, and one of them was double-filed.

### The pricing, which is the actual work of this step

**THE BAR IS THIS OBJECTIVE'S OWN RECURRING DEFECT, NOT "is it a real finding".** All nine are real
and all nine are measured — that is not in dispute and none of them is deleted. What separates them
is the one thing this plan has been wrong about four times: Step 1's `[0.1, 0.3, 1.2, 5.0]` buckets
that were Traefik's own default; Step 2's scrape job on the exporter's default `/metrics` path;
Step 3's `plex_up`-vs-token acceptance line; the `0640` `prometheus.yml` that had Prometheus
crash-looping since 15 July. Every one is **a change or a check that looks like it works and does
not, with nothing anywhere saying so.** A guard hole in that class is worth a build. A guard hole
whose failure the operator meets as a red panel is worth a filed row and nothing more — and 4d's
operator is about to be standing in front of exactly that browser.

**FAMILY A — SILENT: green guard, delivered dashboard renders "No data". This is the wave.**

1. **5a — `task-1785497167-e413`, the templating hole** (`code-assist:plex-monitoring:guard:dashboard-template-vars-declared`).
   This is not a hardening nicety, it is **Step 4's own Test Requirement, verbatim** — "Verify that
   the Proxmox dashboard's container drop-down correctly lists CT 110 (Plex) and CT 111
   (docker-host)" — and 4d step 3. `grafana-pve-dashboard.json` interpolates `$guest` in 13 targets
   across 11 panels off ONE declaration, and the Step 4b Finalizer scored the realistic mutation
   (rename `guest` → `guestt`, leave the targets dangling) **GREEN 13/13 while every panel on the
   dashboard renders a broken query**. Highest value in the queue; routed first.
   **Its headline number went stale and the Planner re-measured it rather than shipping it:**
   the task said the guard contains `templating` zero times; 4c's round 11 made it nine, because
   `_dashboard_variable_queries` now enumerates `templating.list[]` to read each variable's own
   query as PromQL. That answers *is this variable's query readable*. It does not answer *is every
   interpolated `$name` declared*, `label_values` is still zero, and no code compares an
   interpolated spelling to a declared name — so F7/F7b still pass and the drop-down is still
   unguarded. The correction is appended to the task, with the two consequences it carries: reuse
   the walk that already exists, and the tree is now THREE dashboards, so 4c's `templating.list: []`
   composite is the live anti-vacuity case rather than a hypothetical one.
   **CLOSED 2026-07-31 after 8 review rounds.** The Demo this step declares is now RUN, not
   promised: `logs/finalizer-step05a-demo.py` **9/9** — the Step 4b Finalizer's F7b mutation
   (rename `guest` → `guestt`) is **RED where it was GREEN 13/13**, naming both the dangling
   reference and the renamed declaration, with the anti-vacuity control (rename the declaration
   AND all 13 uses → GREEN) that proves the row answers the DANGLING reference and not the file
   changing. Guard PASS 19/19, gate 36/36 rc=0.
2. **5b — `task-1785517907-a5ec`, datasource `type` vs the uid beside it.** One comparison, not a
   new reader: a carrier that names a provisioned uid and declares a type must agree with the type
   `grafana-datasource.yml.j2` provisions at that uid. In the wave because **the mismatch is a
   defect in its own right — that panel draws nothing — independently of the exemption it unlocks**,
   and because the measured route in is ordinary (copy a panel out of a Loki dashboard, update only
   the uid). Blocked by 5a: both rows live in `test_grafana_provisioning_shape.py`.
   **CLOSED 2026-07-31 after ONE review round.** The task's own rationale — "that panel draws
   nothing" — was FALSE and the Builder measured it before writing the row's sentence: the uid
   routes and the type is only believed, so a mismatched carrier still SENDS its PromQL while the
   readability row reads that type and stops asking where the query lives. The row shipped on the
   stronger reason. Guard **PASS 20/20**, gate 36/36 rc=0, 59/59 carriers RED with the new row named.
3. **5c — `task-1785441840-e8eb`, the `<svc>-web` twins' unasked `rule` clause.** The odd one out
   and it earns its place on severity, not genus: different file
   (`scripts/test_traefik_config_shape.py`), different subject (Traefik routers), and **the only one
   of the nine with a measured live consequence** — with the dashboard's web twin repointed at the
   one public host, `plex.<domain>:80` answers 403 where the delivered tree answers 301 (the WAN
   HTTP→HTTPS upgrade is dead) and `traefik.<domain>:80` answers 404, guard PASS 41/41 throughout.
   It has also been ready and unrouted since 2026-07-30, banked twice. Blocked by 5a only so the
   Builder meets one task at a time. **UNBLOCKED 2026-07-31 by 5a's close; ROUTED 2026-07-31 on the
   `queue.advance` that closed 5b. CLOSED 2026-08-01** after 5 rework rounds, all of them on the
   same question in a different place: r2 the rule's OPERATORS (a rule is a boolean expression, so
   a set of `Host()` arguments cannot tell `Host(h)` from `!Host(h)`), r3 the argument ARITY, r4 the
   whitespace CLASS at four seams on the `rule` path, r5 the same class on the `service` clause at
   all four sites that read it plus the shared reader's seven other keys. Guard **PASS 42/42**,
   gate 36/36 rc=0. The residual the Builder named honestly — ~167 further `\s`/`.strip()` sites in
   this file — is a sweep row of its own and is NOT claimed closed here.
4. **5d — `task-1785524605-ea55`, the PVE dashboard must DECLARE the drop-down its Test Requirement
   names.** Added to the wave 2026-07-31 on the `queue.advance` that closed 5a. It is not new work
   and it is not invented: the Step 5a round-3 review's F2 measured it, and **DEC-104 deliberately
   refused to smuggle it into 5a's row** — 5a's claim is *every `$name` a dashboard interpolates is
   declared in its own `templating.list`*, which is TRUE of the delivered tree and stays true when
   the PVE dashboard's `templating.list` is EMPTIED and its thirteen `$guest` rewritten to the
   literal `lxc/110`. That mutation deletes Step 4's own Test Requirement (the CT 110 / CT 111
   drop-down) and 5a's row is GREEN over it, because the anti-vacuity floor sums `checked` over the
   WHOLE inventory and one declared-and-used variable anywhere satisfies it (C1 of
   `logs/critic-step05a-r3-battery.py`; D1/D2 of `logs/red-step05a-rework-r4.py`). **5a shipped a
   DECLARED BOUND that names this task as its carrier** — the same way DEC-102/103 state theirs —
   so leaving it homeless would leave the bound uncarried. Same family as 5a and 5b: green guard
   over a dashboard whose drop-down is gone. Blocked by 5b (same guard file).
   **UNBLOCKED 2026-07-31 by 5b's close; ROUTED 2026-08-01** on the `queue.advance` that closed 5c.
   It is the LAST agent-side row in this step. The open question its Builder must WRITE DOWN rather
   than leave implicit is the identity pin: how the Proxmox dashboard is identified in the
   `_delivered_dashboards(body)` inventory (uid `pve-overview`, or the delivery name), and what the
   row does when that dashboard is ABSENT from the inventory — an identity pin that silently matches
   nothing is this same vacuity failure one level up, and the row would be answering its own
   question with the answer it was given.

**FAMILY B — LOUD, or measured to cost a FALSE REFUSAL. Deferred behind the wave, not deleted.**
This family is the PromQL reader's scanner, and it is the same clause that consumed **eleven review
rounds** of Step 4c. The Finalizer refused a twelfth pass and called it review-termination rather
than rigour; the Planner agrees, and the tasks' own measurements are why:

- `task-1785509072-b939` (canonical) **and `task-1785504947-fbde` are ONE FINDING FILED TWICE** —
  same mechanism (`_promql_skip_quoted` runs to the end of the text, so the call is never formed),
  same exemplar `sum(plex_media_count{"type!="show_episode"})`, same reason for leaving it. Merged
  2026-07-31: b939 is canonical because it is the more measured (three spellings, four consumers of
  the skip logic, and the two false-census corrections rounds 7 and 8 paid for); fbde's one unique
  contribution — the concrete accept-side price, that the cheap fix reddens
  `plex_media_count{$filter}`, an ordinary Grafana idiom — is appended to b939, and fbde is
  re-titled SUPERSEDED rather than closed. **By its own measurement the harm is LOUD:** an
  unterminated literal is a lex error, so the panel ERRORS instead of drawing a plausible number.
- `task-1785506726-adc5` (same-kind-per-call) carries a **measured false refusal on the accept
  side**: D5, `sum(plex_media_count{title="Movies"} or plex_media_count{title="TV"})`, is a correct
  panel and is the same shape as the defect D2, and `title` has no offline kind that separates
  them. Its own row D1 is "not unambiguously wrong".
- `task-1785516964-1b02` (`__name__` regex) says it in the task: **"nobody types this by accident,
  which is why it is filed rather than coded."**
- `task-1785457578-580a` (`_grants_access` owner name → uid 472) needs a **compound precondition**
  that nothing in the tree meets (everything is `owner: root`), and both runtime outcomes are loud —
  ansible fails the chown, or Grafana logs a provisioning permission error and exits 1.
- `task-1785517288-aca4` (P3) is a stale expectation in an old battery, not a guard hole.

**FAMILY C — a DECLARED BOUND's carrier, filed by the row that declared it. Deferred behind the
rest of the wave, 2026-07-31 (DEC-121).** `task-1785533369-cd0e` (P3) is the carrier 5b filed for
its own bound: grafana's three built-in uids are provisioned nowhere, so a carrier naming one is
counted-and-skipped, and `{"type": "loki", "uid": "-- Grafana --"}` with its query under an unknown
key is compared by nothing. It joined the ready set when 5b closed and it is NOT routed, for three
measured reasons rather than a preference. **The fix is a constant transcribed from Grafana**, so
its own failure mode is *stale on an upgrade* — the loud end of this step's bar, and the precise
hazard this repo has been rejected twice for. **The route in is three deliberate contortions** (a
built-in uid AND a wrong declared type AND a query moved to an unreadable key), where 5b earned its
place on an ordinary copy-paste route. And **the cheap measurement arrived after the task was
filed** — `mem-1785534624-584f`, `GET /api/frontend/settings` field `meta.id` on a booted container,
where the task text still proposes grepping the pinned image's frontend bundle — so the honest move
is to re-price it with that in hand, not to route prose known to be stale. Blocked by 5c AND 5d
(unlike the six, whose blockers were left alone to avoid churn on rich records): one record, nothing
at risk, so it gets the accurate statement of "behind the wave".

**THIS REPO HAS BEEN REJECTED TWICE FOR A GUARD THAT FORBIDS THE REAL ANSWER**, and Family B is
where that happens next: three of its five ask for a stricter scanner against defects that are
visible when they occur, at a price two of them have already measured in false refusals of correct
panels. Deferring them is the judgement, and it is recorded here rather than left as a queue that
quietly never gets there. They are blocked by the wave, so a future Planner re-prices them when 5c
closes — with 4d's operator evidence in hand, which is new information none of these rows have.
**Their blockers are 5a/5b/5c and were NOT extended to 5d**, deliberately: adding a blocker to six
tasks to preserve a bookkeeping invariant is churn against rich task records, and the re-pricing
Planner meets them at 5c's close either way. If 5d is still open then, it is the current step's own
work and the six defer again on the same reasoning — say so rather than routing them by accident.

**THAT MOMENT ARRIVED 2026-08-01 AND THE BRANCH IT NAMED IS THE ONE THAT APPLIES (DEC-132).** 5c's
close discharged the last of the six's blockers, the agent-side ready set went from one to SEVEN,
and 5d is still open — so **the six defer again, and this is the Planner saying so rather than
routing them by accident.** The substantive reason is not the pre-commitment itself but what was
checked under it: **the input the re-pricing was waiting on has not arrived.** The stated ground for
re-pricing at 5c's close was *"with 4d's operator evidence in hand, which is new information none of
these rows has"* — and 4d `task-1785442499-1851` is still open and OPERATOR-ONLY. Nobody has opened
a Grafana panel. A re-pricing today would be the same judgement made twice rather than a better one,
and none of the five reasons moved: b939 still LOUD by its own measurement, fbde still the same
finding filed twice, adc5 still carrying a measured false refusal of a correct panel, 1b02 still
saying in its own text that nobody types it by accident, 580a still needing a precondition the tree
does not meet with both outcomes loud, aca4 still a P3 stale battery expectation. Their blockers are
STILL not extended to 5d — the churn argument is unchanged, and the six being VISIBLY ready is now
the signal that makes the next Planner price them, which re-blocking would hide behind bookkeeping.
**What the Planner at 5d's close inherits, stated so it is not a surprise:** the wave is exhausted
at that point, the ready set is the six plus `cd0e` and `9df3` (whose blockers 5d discharges) plus
anything 5d files, and that Planner has a real decision — re-price with 4d's evidence if it has
arrived, or record that Step 5 is exhausted and that everything remaining is either operator-gated
or deferred-with-reasons. DEC-132 does NOT pre-commit that answer; it covers only the 5d-open case.

### THE CLOSE, 2026-08-01 — the branch this step pre-wrote, taken (DEC-153)

The paragraph above named the two branches the inheriting Planner would face. **Branch 2 applies,
and the deciding input is the one that was named a week in advance: 4d's operator evidence has not
arrived.** `task-1785442499-1851` is open and OPERATOR-ONLY. Nobody has opened a Grafana panel.

**STEP 5 IS EXHAUSTED AND NO STEP 6 IS CUT.** Step 5 earned its existence because nine READY rows
belonged to no numbered step and one of them was Step 4's own Test Requirement. **Being ready was
never the reason — clearing the bar was**, and cutting a Step 6 out of what is left would run that
same argument in reverse. Every remaining row was priced against this step's own bar, and the three
filed since the wave was cut were priced here for the first time:

| Row | P | Class | Why it defers |
|---|---|---|---|
| `task-1785571102-579d` — `_read`'s raw-byte decode | P2 | **LOUD** | Its own acceptance criterion is *"the failure must be a sentence, not a stack trace."* The gate **already refuses** the file — rc=1, no summary line — so the row buys a better MESSAGE, not a repair. The trigger is a raw invalid UTF-8 byte in a delivered `.json`, which nothing in the tree writes and neither an editor nor a Grafana export produces. DEC-152 filed it "for the Planner to route"; the Planner priced it and says why instead. **Kept on the record because it has one property the others do not:** when it fires it takes every OTHER row's verdict with it, and four 04b/04c harnesses then attribute a failure to a substring absent from the output. |
| `task-1785534580-9df3` — the `.j2` truth source read raw | P3 | Family A **genus, not shipping** | The class this loop has closed five times on other files (3a's "renderer that deploys", 4b's "DELIVERED NAME") — but C2 measured that the delivered `datasources:` block contains **no Jinja at all**, so raw == rendered today (A1), and the wrong direction is a false refusal of correct carriers. Hardening for the first person who templates a `url`/`type`/`uid`, not a live hole. |
| `task-1785553255-bad2` — a panel following a SECOND variable | P3 | Family A **genus, contrived route** | Measured GREEN, so the hole is real — but the route in is a second `custom` templating entry **plus twelve repointed panels**, the same "three deliberate contortions" shape DEC-121 declined for `cd0e`, and the fix needs a value-list reader for custom/constant variables this file does not have. Its bound is declared in the row's own docstring, so it cannot be lost. |
| `task-1785571952-8144` — the ~167 whitespace sites | P3 | **declared, now carried** | Filed by this close. Not new work: 5c's round 5 named it in writing (*"the general form belongs in one sweep row"*) and it had **no carrier task** — and this repo's own rule is that a defect declared and never scheduled *"is not banked, it is shipped."* Deferred because a 167-site sweep is not one atomic task; its honest first move is a census, and 5c's `f0-loudness` 12/12 says most such seams are loud. |
| the six Family-B rows, and Family C `cd0e` | P2/P3 | unchanged | DEC-132's ground is unchanged because its named input never arrived. None of the five reasons moved. |

**WHAT THIS LEAVES, AND IT IS ONE THING.** Steps 1, 2 and 3 are complete, gates included. Step 4 is
agent-side complete. Step 5 is closed. **The whole numbered plan now advances through exactly one
action, and no agent may take it: `task-1785442499-1851` — `just play`, then open each dashboard.**
Its prerequisites are all satisfied (4a/4b/4c closed, both tokens vaulted, the `0644`
`prometheus.yml` repair shipped in 2a), and its step 5 asks the operator to record which panels were
empty and why — which is the input that re-prices all eleven deferred rows and may file repo-side
work worth more than any of them. Building another guard row before that browser check is the "same
judgement made twice rather than a better one" this section already refused once.

- **Test Requirements:** unchanged from every repo-side task in this objective — `just test` exits
  0, each new row RED under a reproducible mutation of the REAL files reverted in a `finally` with
  sha256 asserted at both ends, control rows GREEN, and an anti-vacuity clause for the state where
  the row finds nothing to check. No live call, no `just play`, no vault value, no commit. Gate 4d
  untouched (1b/2b/3b are closed — DEC-154).
- **Demo:** `just test` → GATE PASS with the guard's own count up by the rows added, and the
  Step 4b Finalizer's F7b mutation (rename `guest` → `guestt`) reddening where it was green.

---

## Step 6: Close the SILENT-class guard rows filed AFTER Step 5's wave was cut

- **Objective:** Give the guard rows filed since Step 5 was cut a numbered home, and route them ONE
  at a time against Step 5's own bar — not because they are ready, but because they clear it.
- **Demoable outcome:** `just test` exits 0 with `scripts/test_grafana_provisioning_shape.py`'s own
  count up by the row added, and a tree carrying the newly-guarded defect goes RED with a verdict
  sentence that names the offending files.
- **Expected subtask wave:** ONE row. `task-1785601096-9ffc`.

### WHY THIS STEP EXISTS WHEN DEC-153 SAID IT WOULD NOT (DEC-182)

DEC-153 closed Step 5 with *"no Step 6 is cut"* and *"building another guard row before that browser
check is the same judgement made twice rather than a better one."* That was a sound decision on the
information it had. **Three things happened after it that it did not have:**

1. **The empty queue was tested three times and did not terminate the loop.** Iterations 88, 89 and
   90 each met an empty `tasks.ready`, refused to close gate 4d (correctly — no agent may), and
   produced NO EVENT. Nothing advanced.
2. **The operator's answer was to restart the runner, not to open a browser.** 4d is still open;
   `just play` has still not been run. A restart after three deliberate parks is an instruction to
   keep going on what an agent CAN do — `mem-1785119117-63d8` ("a resume without a close means route
   past the gate, not park again"), and the precedent this thread then set at iteration 91.
3. **Iteration 91 routed a filed guard row and it was worth doing.** `task-1785571102-579d` went
   build → 12 review rounds → PASSED → CLOSED at guard `c1fbc7b3`, and along the way MEASURED the
   two uid layers, the global duplicate tracker and the trim class against the pinned engine
   (`mem-1785598736-71df`, `mem-1785593450-761b`). None of that existed when DEC-153 was written.

**So the queue contract's "leave the queue empty so the Finalizer can terminate" does not apply
here, because the queue is NOT empty** — twelve agent-actionable rows are open in this objective's
own `code-assist:plex-monitoring:guard:*` namespace. The Planner instruction forbids INVENTING
tasks once the numbered steps run out. It does not license leaving a dozen already-filed,
already-measured rows homeless; that is the exact defect that caused Step 5 to be cut in the first
place, and this plan said so in Step 5's own text.

### THE ROW THIS STEP ROUTES, AND WHY IT AND NOT ONE OF THE OTHER ELEVEN

Step 5's bar is unchanged and is this objective's own recurring defect: **a change or a check that
looks like it works and does not, with nothing saying so.** Routing by readiness is what
`progress.md` warned a resume against. So the pricing is on the bar, and only one row clears it
outright.

**`task-1785601096-9ffc` — two delivered dashboards with the SAME title, distinct legal uids.**
Measured twice in two containers on the pinned `grafana/grafana:13.1.0`
(`logs/critic-579d-r12-duplicate-title-lockout.py` 7/7, first sighting in
`logs/critic-579d-r12-empty-uid-same-title.py` 6/6): the provider takes the SAME provider-wide
`has no database write permissions because of duplicates` lockout that
`test_delivered_dashboards_have_distinct_uids` states the blast radius of in its own sentence —
reached by a cause that row cannot see, because its key is the uid and this collision is not one.
**Three properties put it above every other open row:**

- **Silent at the engine.** Unlike the uid collision there is NO `the same UID is used more than
  once` line and no title message of any kind — three polls, three bare lockout lines. An operator
  reading the container log cannot tell why the provider stopped writing. This refuted the probe's
  own first prediction, which is why it is a measurement and not a guess.
- **Silent at the artifact.** Both files are still SERVED on the first run, so there is no missing
  dashboard to notice. The damage is entirely in the future: every later edit to either dashboard
  is silently not applied.
- **Silent at the guard.** PART B ran the WHOLE guard over a tempdir tree whose PVE dashboard
  carries the Homelab dashboard's title: PASS 21/21, rc=0, and the collision row in particular
  prints `problems=[]`. **Re-verified at the Planner's own hands rather than adopted:** `grep -i
  "same title|title is used|duplicate title"` over `scripts/test_grafana_provisioning_shape.py`
  returns ZERO hits, and none of the 21 rows asks the question.

**And the tree as delivered is safe today, verified here rather than taken from the row:**
`homelab-overview`/`Homelab Overview`, `plex-health`/`Plex Health`, `pve-overview`/`Proxmox VE` —
distinct on BOTH axes. So this is a latent guard hole and not a live outage, the same character as
the other open `guard:` rows and the same character as every row Step 5 closed.

**Why not the other eleven, priced against the same bar:**

| Row | P | Why it is not this step's wave |
|---|---|---|
| `task-1785594766-fb36` — the READABLE row's rule order | P2 | **Real, and NEXT in line — but LOUDER.** The row is already RED when this fires; it names the wrong FIELD (uid or number where the engine names the title). A misdirected alarm is worse than no alarm only if nobody is looking, and here somebody is: the gate has already failed. Same file as `9ffc`, so it serialises behind it either way, and its measured order (`mem-1785592369-90dd`) does not go stale. |
| `task-1785598629-7407` — the PVE row's printed sentence | P3 | Same class as `fb36` and one priority lower; the work is a decision about a SELECTOR two earlier logs hold, not the wording. Serialises behind both. |
| the five Family-B rows (`b939`, `adc5`, `1b02`, `580a`, `aca4`) | P2/P3 | **DEC-132's reasons are unchanged and its named input still has not arrived.** Four are the same PromQL scanner clause that consumed ELEVEN review rounds of Step 4c; two have already MEASURED the price as a false refusal of a correct panel. `fbde` is no longer among them — retired this turn. |
| Family C `cd0e`, plus `9df3`, `bad2`, `8144` | P3 | Priced in DEC-153's table and nothing moved: genus-not-shipping, contrived route, or a 167-site census that is not one atomic task. |

### THE OPERATOR GATE IS NOT SUPERSEDED BY THIS STEP

`task-1785442499-1851` (4d) stays open, stays P1, and stays the single most valuable thing anyone
can do to this objective — `just play`, then open each dashboard and record which panels are empty
and why. That evidence re-prices all eleven deferred rows and may file repo-side work worth more
than any of them. **Step 6 is what an agent may do while waiting, not a substitute for it.**
`.ralph/agent/operator-ask.md` carries the ask; RObot/Telegram is unwired in this repo, so there is
no way to ask interactively — `human.interact` emits into a void here.

- **Test Requirements:** unchanged from every repo-side task in this objective — `just test` exits
  0, the new row RED under a reproducible mutation of the REAL files reverted in a `finally` with
  sha256 asserted at both ends, control rows GREEN, and an anti-vacuity clause for the state where
  the row finds nothing to check. **Plus one this row owns specifically:** the SCOPE of the title
  collision (provider / folder / global) must be MEASURED on the pinned image, not inferred from the
  uid tracker's scope — that tracker is global over delivered spellings
  (`red-579d-r11-crossprovider` X1) and this collision was measured only within one provider in one
  folder. A claim about a scope needs a carrier at that scope (`mem-1785593456-9d15`). No live call,
  no `just play`, no vault value, no commit. Gate 4d untouched.
- **Demo:** `just test` → GATE PASS, guard PASS n/n with n up by the row added; a tempdir tree whose
  two delivered dashboards share a title is RED with a sentence naming BOTH files and saying the
  engine gives no reason of its own; the tree as delivered stays GREEN.

---

## Step 7: Close the MISDIRECTED-ALARM guard rows — the gate is RED and the verdict names the wrong field

- **Objective:** Now that the SILENT class is empty of rows that clear Step 5's bar, route the class
  that sits immediately behind it: a guard row that fires CORRECTLY and then names a field the
  engine never looked at. One row at a time, priced on the bar and not on readiness.
- **Demoable outcome:** `just test` exits 0, `scripts/test_grafana_provisioning_shape.py` is PASS
  n/n on the tree as delivered, and a tempdir tree carrying each of the two combined defects goes
  RED naming the SAME field the pinned `grafana/grafana:13.1.0` names in its own container log.
- **Expected subtask wave:** ONE row. `task-1785594766-fb36`.

### WHY THE BAR MOVES, AND WHY IT IS A MOVE AND NOT AN ABANDONMENT (DEC-194)

Step 5's bar — *a change or a check that looks like it works and does not, with nothing saying so* —
is this objective's recurring defect and it stays the ordering principle. What changed is the
inventory under it: Step 6 routed `9ffc`, the last open row that cleared that bar outright, and the
Finalizer closed it at 22/22. **Step 6's own pricing table already recorded where the queue goes
next**, in the row it deferred:

> `task-1785594766-fb36` — **Real, and NEXT in line — but LOUDER.** … Same file as `9ffc`, so it
> serialises behind it either way, and its measured order (`mem-1785592369-90dd`) does not go stale.

Both halves of that deferral have now expired. `9ffc` is closed, so the serialisation is discharged;
and it was deferred *relative to a silent row*, not on a standing reason of its own. Every other
open row still carries its standing reason, re-checked this turn and unmoved:

| Row | P | Standing reason, re-checked 2026-08-01 |
|---|---|---|
| the five Family-B rows (`b939`, `adc5`, `1b02`, `580a`, `aca4`) | P2/P3 | **DEC-132, and its named input STILL has not arrived** — 4d is open, `just play` has not run. Four are the same PromQL-scanner clause that consumed eleven review rounds of Step 4c; two have already MEASURED the price as a false refusal of a CORRECT panel. Unchanged. |
| `task-1785598629-7407` — the PVE row's printed sentence | P3 | Same misdirected-alarm class as `fb36` and one priority lower; the work is a decision about a SELECTOR two earlier logs hold. Serialises behind `fb36` in the same file. Next after it, if nothing sharper is filed. |
| `cd0e`, `9df3`, `bad2`, `8144` | P3 | Priced in DEC-153's table, nothing moved: genus-not-shipping, contrived route, or a 167-site census that is not one atomic task. |
| `task-1785615546-0956` — the SILENCE claim's residual | P3 | Silent in character but **NOT MEASURED BY ANYONE, and its own description says so**: it needs a four-dashboard tree with THREE spellings on ONE address, delivered and read back at the pinned engine, and no run in this thread or `579d`'s carries it. It is a research row before it is a build row, and it is P3. It does not outrank a P2 whose order is already written down. |
| `task-1785621026-fc70` — the delivery-arity class | P2 | **Filed THIS TURN** (below). Same file as `fb36`, so it serialises behind it regardless; and its own acceptance criteria demand a blast-radius enumeration first, because the repair may belong in the inventory builder and may move rows that are currently GREEN. That is not one atomic increment yet. |

So `fb36` is the only open P2 in this namespace with no standing deferral against it. That is the
pricing, and it lands where the `9ffc` Finalizer independently priced it.

### THE ROW THIS STEP ROUTES

**`task-1785594766-fb36` — `test_delivered_dashboards_parse_as_dashboards` asks its rules in the
wrong order, in TWO directions.** Measured by the `579d` round-8 review on WHOLE gate runs over a
readable delivered dashboard (`logs/critic-579d-r8-uidlen-and-readable-row.py` PART D, **0/2**):

- illegal uid + a blank-after-trim title → the row names the **UID**; the engine names the **TITLE**.
- a number past the IEEE double range + the same title → the row names the **NUMBER**, because the
  parse raises before any field is read; the engine still names the **TITLE**.

**Every wrong answer sends the operator to a field the engine never looked at.** This is the LOUD
class and the step says so plainly: the gate is already RED when this fires, so nobody is missing an
outage — what they are missing is the hour spent on the wrong field. That is a smaller harm than a
silent hole, which is exactly why it is routed AFTER the silent rows and not instead of them.

**It is cheap for a reason that will not survive neglect.** `_unreadable`'s save-layer chain
(~line 1413) already asks these rules in the engine's measured order — title, uid, number, tags —
with the number DEFERRED out of the parse via `_grafana_provisionable_json(deferred=...)`. This row
is the SECOND spelling of that same order and never got the treatment. The order to carry is written
down and must not be re-derived (`mem-1785592369-90dd`, and the constant blocks above each
predicate): parse/bare-token (LOAD) → load-layer `MustString()` title and top-level shape (LOAD) →
save-time title trim + 5000-byte bound → uid (charset then length, on the string that survives
`GRAFANA_SHORT_UID_TRIM`) → number past the IEEE double range → tag 50-byte bound.

**The one harness this costs, priced and not discovered later.** DEC-176 recorded that reordering
this or-chain moves the FIRST LINE of the row, which is the open anchor `R1` of
`logs/red-step05d-rework-r10-critic-recheck.py` cuts on. That anchor **already cannot reach its
target** — its reconstruction lands on `905f46d8` against a declared `10fd3cdb`, because seven
rounds of `579d` changed the file outside its three anchors. So the true cost is one stale anchor
line, not a lost fact. Say so in the increment; do not silently break it.

### QUEUE HYGIENE DONE AT THIS CUT

`task-1785621026-fc70` (P2,
`code-assist:plex-monitoring:guard:delivery-arity-shared-basename-one-dest`) is **NEW**. The `9ffc`
Finalizer flagged it as the Planner's own: the H1 class existed only as `mem-1785620544-7b12` and
`mem-1785620824-120c` with no runtime row, and its measurement **sharpens what the class is**. The
round-13 review deferred H1 as an identity-print problem that no print could reach; the Finalizer
then asked ansible (`logs/finalizer-9ffc-r13-h1-one-file-on-disk.py` **8/8**, real
`ansible-playbook` core 2.21.1) and got a different animal: two `copy:` tasks with distinct-byte
srcs under ONE basename onto a directory `dest:` leave **ONE** file (A1), the survivor is the
SECOND src (A2), and the CONTROL with distinct basenames leaves TWO (A3). **The guard groups per
DELIVERY where ansible resolves per ADDRESS** — it prints `2 delivered dashboard(s)` where the
filesystem holds 1. That is an inventory defect, not a verdict-wording one, and it is reachable on
this repo's own flat shape because `root = TEMPLATES if is_template else FILES` (a `copy:` and a
`template:` task, two flat srcs, one basename). **The deferral was still correct** — grafana is
handed one dashboard and one title there, so acceptance (b) of round 13 was not unmet on a
reachable tree, and had two files landed this would have been `finalization.failed`.

### THE OPERATOR GATE IS STILL THE HIGHEST-VALUE ACTION AND STILL NOT AGENT-CLOSABLE

`task-1785442499-1851` (4d) stays open, stays P1, and is unaffected by this step: `just play`, then
open each Grafana dashboard and record which panels populate and which are empty and why. That
evidence re-prices the five Family-B rows directly (DEC-132's named input) and may file repo-side
work worth more than every guard row in this table. **Step 7 is what an agent may do while waiting,
not a substitute for it.** `.ralph/agent/operator-ask.md` carries the ask; RObot/Telegram is unwired
in this repo, so `human.interact` emits into a void and there is no interactive way to ask.

- **Test Requirements:** unchanged from every repo-side task in this objective — `just test` exits 0,
  the row RED-first under a reproducible mutation of the REAL files reverted in a `finally` with
  sha256 asserted at both ends, control rows GREEN, and an anti-vacuity clause for the state where
  the row finds nothing to check. **Plus the two this row owns:** the expected field must be scored
  against the pinned `grafana/grafana:13.1.0`'s OWN container-log line for each combined pair rather
  than against the order in the source (a claim about what the engine names needs a carrier at the
  engine — `mem-1785593456-9d15`), and the reconstruction chain must still close
  (`logs/red-579d-r9-recheck-chain.py` or its successor, 10/10). No live call, no `just play`, no
  vault value, no commit. Gates 1b/2b/3b/4d untouched.
- **Demo:** `just test` → GATE PASS; the review's PART D flips from 0/2 to 2/2; a tempdir tree with
  an illegal uid + a blank-after-trim title is RED naming the TITLE, and the same tree with a number
  past the IEEE double range is RED naming the TITLE — both matching the container log; the tree as
  delivered stays GREEN at PASS n/n.

---

## Step 8: Close the THIRD site of the misdirected-alarm defect — the READABLE row's PRESENCE GATE

- **Objective:** `fb36` repaired two of the three sites where
  `test_delivered_dashboards_parse_as_dashboards` names a field the engine never looked at, and
  DEFERRED the third in writing (DEC-195) because batching two repairs into one increment is what
  gets a round rejected in this file. That deferral was made relative to `fb36`'s own atomicity and
  nothing else; `fb36` is closed, so it has expired. Route the third site.
- **Demoable outcome:** `just test` exits 0, `scripts/test_grafana_provisioning_shape.py` is PASS
  n/n on the tree as delivered, and a delivered dashboard carrying `uid: ""` — or no `uid` key, or a
  top-level JSON **array** — is RED naming the **TITLE**, the same field the pinned
  `grafana/grafana:13.1.0` names in its own container log for that carrier.
- **Expected subtask wave:** ONE row. `task-1785622294-ba6c`.

### WHY THIS STEP AND NOT A NEW BAR (DEC-198)

Step 5's bar — *a check that looks like it works and does not, with nothing saying so* — is still
the ordering principle and it has not moved since Step 7. Step 8 is Step 7's own class continued:
the SILENT side holds no row that clears the bar outright and is not deferred on a standing reason,
and the LOUD side now holds the residue of the very repair Step 7 shipped. `fb36`'s Finalizer
verified that residue is not a silent hole before handing over — `logs/finalizer-fb36-r2-unmodelled-refusals.py`,
one run on the pinned engine, D1: the one carrier the engine refuses outside the row's five rules
(a top-level JSON array) is RED at the guard. So nothing silent is hiding behind this step.

**The `fb36` Finalizer priced this turn's queue differently and it is worth saying why it is not
followed.** Its handoff put the two "silent P2s" first — `b939` and `1b02`. Both are Family-B and
both keep DEC-132, whose named input (4d's operator walkthrough) still has not arrived. Beyond that:

- `b939`'s own description says the harm is **LOUD** — *"the engine refuses the query and the panel
  ERRORS rather than drawing a plausible number. Loud harm, so it stays declared."* It is silent at
  the GUARD and loud at the ARTIFACT, which is not the shape Step 5's bar ranks first, and DEC-132
  already recorded it that way. It also carries a measured accept-side price: a fix must keep
  `plex_media_count{$filter}` and `traefik_service_requests_total{service="plex@file",code=~"$code"}`
  GREEN, and this file has been rejected twice for forbidding correct panels.
- `1b02` is genuinely silent (a `__name__` regex graphs the whole proxy under a Plex title at PASS
  17/17) but its own description closes the reachability question against itself — *"nobody types
  this by accident, which is why it is filed rather than coded."*

Neither is re-priced downward here and neither is retired; they keep DEC-132 and are re-checked at
the next `queue.advance`, as they have been at every one.

### THE ROW THIS STEP ROUTES

**`task-1785622294-ba6c` — the presence gate asks a GUARD-POLICY requirement before every engine
rule.** `test_delivered_dashboards_parse_as_dashboards` opens with

```python
if not isinstance(doc, dict) or not doc.get("uid") or not doc.get("title"):  # -> "no top-level uid/title"
```

above the save-layer chain `fb36` just reordered. The uid half of that clause is not an engine rule:
Grafana does not refuse an empty or absent uid, it **generates a uuid and saves the dashboard**
(`mem-1785606269-dbcd`, and `_grafana_short_uid_defect`'s own first two branches say so in their
returned sentences). Measured in `fb36`'s own pinned run rather than reasoned about
(`logs/red-fb36.py` PART D, one delivered file per carrier, scored on BOTH the pre-edit and the
delivered text): `uid: ""` with a 5001-character title, and NO `uid` key with the same title, are
both `Dashboard title cannot contain more than 5000 characters` at the engine — the **TITLE** —
while the row answers `no top-level uid/title` for both.

**A THIRD CARRIER CLASS, measured after the row was filed and NOT in its description**
(`mem-1785624803-6b47`, `logs/finalizer-fb36-r2-unmodelled-refusals.py`): a top-level JSON **ARRAY**
is refused with `Dashboard title cannot be empty` — the TITLE, alone — while the row prints
`no top-level uid/title`, naming the uid the engine never asked for. It reaches the same gate
through the `isinstance(doc, dict)` half and is cheap to deliver. **The row was deliberately NOT
re-`ensure`d to add it** — `ensure` reuses by key and REWRITES the record, and this description is
long and carefully measured (the clobbering risk DEC-182/DEC-132 both priced). It is carried here,
in the memory, and in the `tasks.ready` payload instead.

**The price is already counted and it is a census, not an edit.** Removing that sentence costs FOUR
live assertions in three other hats' harnesses, each of which greps the string:
`logs/red-step05d-rework-r10.py` S1 and S2, `logs/red-step05d-rework-r11.py` S6,
`logs/critic-step05d-r9-title-provisionability.py` D2. Moving the clause BELOW the chain makes it
unreachable instead, because `_grafana_short_uid_defect` already answers its whole class (`""` → the
trim class, absent → not a string) — and a dead clause is worse than a wrong one, because nothing
measures it. **So the first move is the blast-radius census: decide whether the row keeps a policy
sentence at all, and if it does, where it can sit so it is BOTH reachable AND after every engine
rule.** `logs/builder-fb36-collateral.py` PART C already runs all four carriers over two guard texts
and prints the whole line, so the census has a runner that does not need writing. **Never edit
another hat's harness** — if an assertion falls, DISCLOSE and attribute it.

### THE ROW THAT IS NEXT AFTER THIS ONE, NAMED SO IT IS NOT RE-DERIVED

`task-1785624345-a15c` (P3, `code-assist:plex-monitoring:guard:unreadable-chain-uid-halves`) — the
FIRST spelling of the same rule order, `_unreadable`'s save-layer chain at ~:1413, which fences the
same predicate with `isinstance(uid, str)` alone (HALF the line `fb36` split it on) and so gets both
halves wrong in OPPOSITE directions. Measured 6/6 by the `fb36` round-2 Critic
(`logs/critic-fb36-r2-unreadable-sibling.py`), so its order cannot go stale. It is the cheapest open
row in this namespace and it does not lead only because it is P3, its carriers need a separate
delivered-file set and a separate container run, and the file is RED either way — a wrong REASON,
not a false GREEN. It serialises behind `ba6c` in the same file regardless.

Standing deferrals re-checked at this cut and unmoved: the five Family-B rows (`b939`, `adc5`,
`1b02`, `580a`, `aca4`) on DEC-132; `cd0e`, `9df3`, `bad2`, `8144` on DEC-153's table; `7407` the
same class one priority lower, now behind `a15c` too; `0956` silent in character but **unmeasured by
anyone** and P3 — a research row before it is a build row; `fc70` (P2) on its OWN standing clause,
not on `fb36` — its acceptance criteria demand a blast-radius enumeration of every row the inventory
repair moves, because the fix may belong in the inventory builder and may move rows that are
currently GREEN. `fb36`'s half of `fc70`'s deferral ("serialises behind it in the same file") has
expired; that half has not.

### QUEUE HYGIENE AT THIS CUT

**Nothing filed and nothing retired.** The `fb36` Finalizer's adversarial pass found one thing worth
banking and it is a NON-defect: a stale numeric top-level `id`, `panels` as a string, and 600 nested
arrays are all **served, not refused** by `grafana/grafana:13.1.0` (`mem-1785624794-9c63`), which
REFUTED that hat's own written prediction. The consequence is a prohibition, not a task: **do NOT
add an `id` rule to this row's or-chain** — it would be a refusal the delivery path does not make,
the same class the tags predicate is deliberately silent on. Inventing a row for it is exactly what
the queue contract forbids.

### THE OPERATOR GATE IS STILL THE HIGHEST-VALUE ACTION AND STILL NOT AGENT-CLOSABLE

`task-1785442499-1851` (4d) stays open, stays P1, and is untouched by this step: `just play`, then
open each Grafana dashboard and record which panels populate and which are empty and why. That
evidence re-prices the five Family-B rows directly (DEC-132's named input) and may file repo-side
work worth more than every guard row in this table. **Step 8 is what an agent may do while waiting,
not a substitute for it.** `.ralph/agent/operator-ask.md` carries the ask; RObot/Telegram is unwired
in this repo, so `human.interact` emits into a void and there is no interactive way to ask.

- **Test Requirements:** unchanged from every repo-side task in this objective — `just test` exits 0,
  the row RED-first under a reproducible mutation of the REAL files reverted in a `finally` with
  sha256 asserted at both ends, control rows GREEN, and an anti-vacuity clause for the state where
  the row finds nothing to check. **Plus the two this row owns:** each carrier's expected field must
  be scored against the pinned `grafana/grafana:13.1.0`'s OWN container-log line rather than against
  the order in the source (`mem-1785593456-9d15`), and the four sibling assertions must either still
  hold or have their failure DISCLOSED and attributed — never edited. No live call, no `just play`,
  no vault value, no commit. Gates 1b/2b/3b/4d untouched.
- **Demo:** `just test` → GATE PASS; `logs/red-fb36.py` PART D flips; the array carrier of
  `mem-1785624803-6b47` is RED naming the TITLE; the tree as delivered stays GREEN at PASS n/n.

## Step 9: Close the FIRST spelling of the rule order — `_unreadable`'s chain

- **Objective:** `scripts/test_grafana_provisioning_shape.py` holds the save-layer rule order in TWO
  spellings. Step 7 (`fb36`) repaired the second and Step 8 (`ba6c`) repaired the gate above it. The
  FIRST spelling — `_unreadable`'s chain at :1413-1421 — still fences the uid predicate with
  `isinstance(uid, str)` alone, which is HALF the line the repair split it on, so it gets both
  non-refusing members wrong in OPPOSITE directions. Route the last site.
- **Demoable outcome:** `just test` exits 0, `scripts/test_grafana_provisioning_shape.py` is PASS
  n/n on the tree as delivered, and a delivered dashboard whose invalid byte sits at a SAVED
  position and whose uid is only the engine's trim class is RED naming the **NUMBER** (or the TAG) —
  the rule the pinned `grafana/grafana:13.1.0` actually stopped on — while a NON-STRING uid alone is
  NAMED rather than dropped.
- **Expected subtask wave:** ONE row. `task-1785624345-a15c`.

### WHY THIS STEP AND WHY IT IS NOT A NEW BAR (DEC-200)

Step 5's bar — *a check that looks like it works and does not, with nothing saying so* — has not
moved since Step 6, and Step 7 moved the class one notch out to *the check fires correctly and then
sends the operator to the wrong field*. Step 9 is neither a new bar nor a new class: it is the SAME
chain's remaining spelling. Two steps in a row repaired sites of one defect and the file now
**contradicts itself** — measured, not asserted: for a non-string uid the repaired row's 5th link
names `uidtype-NOTAREFUSAL` while `_unreadable`'s chain names nothing at all and prints its
`SAVES this file with those bytes replaced by U+FFFD` clause. The two spellings disagree on the
**polarity** of a class, not merely on its position, and that disagreement is something this
objective created the visibility for.

**RE-MEASURED AT THIS CUT, NOT READ OFF THE FILER'S PROSE.** `logs/critic-fb36-r2-unreadable-sibling.py`
was scored at guard `a70d851ce802`; `ba6c` has moved the file to `9c08e2b54dc2` since. Re-run at the
Planner's own hands on the delivered tree: **PASS 6/6**, PART Z confirming the guard sha, so `ba6c`
left this chain untouched and the defect is live at the text the Builder starts from. The site was
also read directly: :1415 is
`(_grafana_short_uid_defect(uid) if isinstance(uid, str) else None, GRAFANA_LOG_SAVE)` asked **2nd**
of four — ahead of the deferred number at :1417 and the tags at :1419 — against the repaired
spelling at :5362-5367, which computes
`refuses_uid = isinstance(uid, str) and _grafana_stored_uid(uid) is not None`, asks the refusing half
4th, and asks the whole predicate LAST after the tag.

### THE PRICING, ON THE BAR AND NOT ON PRIORITY

`a15c` is P3 and `fc70` is P2, so routing `a15c` needs an argument rather than a declaration. Both
were re-priced here:

- **`fc70` (P2, delivery arity) is the SILENT one and it still does not lead.** Its harm clears
  Step 5's bar outright — the guard prints `2 delivered dashboard(s)` where the filesystem holds 1
  — but its deferral was never `fb36`-relative and has not discharged. Its own acceptance criterion
  (c) demands *every row whose verdict the repair moves enumerated in a log and each move argued*,
  because the repair may belong in the INVENTORY BUILDER that every `files`-keyed row is built from,
  and it may move rows that are currently GREEN. Its own description also says *"the tree as
  delivered today does NOT carry it — verify that before assuming a live defect"*, and
  `mem-1785620824-120c` measured why: this repo ships full-path dests. So it is a wide-blast-radius
  increment against an unreachable-today class, in a file whose own history is that batching gets a
  round rejected. That is a standing clause, not a stale one.
- **`a15c` (P3) is narrower, cheaper, and the only one whose ORDER cannot go stale.** It is one
  ordering in one function in one file, its engine half is already measured on the pinned image
  (calibration `step05d-rework-r9-uid-charset` C2 and `logs/critic-fb36-r2-nonrefusal-generalizes.py`
  PART A), and the repair it needs was shipped one screen away by `fb36` round 2 — so `done` has a
  diff for an oracle (`mem-1785622988-cf79`). It is honestly BELOW `fc70` on the silent/loud bar:
  the file is RED either way there, so this is a wrong REASON to an operator and not a false GREEN.
  It leads because its cost is the lowest open on this objective, its measurement is fresh at the
  delivered sha, and leaving one chain's two spellings disagreeing on a class's polarity is a debt
  the next reader of this file pays.

Nothing is re-priced downward and nothing is retired. The five Family-B rows (`b939`, `adc5`,
`1b02`, `580a`, `aca4`) keep DEC-132 — its named input, 4d's operator walkthrough, **still has not
arrived**; `cd0e`, `9df3`, `bad2`, `8144` keep DEC-153's table; `7407` and `0956` are unchanged
(`0956` is still unmeasured by anyone — a research row before it is a build row); `fc70` keeps its
own standing clause above.

### THE ARITHMETIC, CORRECTED

The Step 8 close reported *"14 agent-actionable rows remain ready"*. `<ready-tasks>` does hold 14
rows, but one of them is `task-1785442499-1851` — **4d, OPERATOR ONLY and unclosable by any agent**.
Agent-actionable is **13**, and it was 14 at the Step 8 cut only because `ba6c` was itself in that
wave. The number matters because it is what the next Planner prices, so: **13 agent-actionable ready
rows + 1 operator gate.** After this cut, `a15c` is the wave and 12 rows defer.

### QUEUE HYGIENE AT THIS CUT

**Nothing filed and nothing retired.** The `ba6c` round banked two things and NEITHER is a defect:
`mem-1785627131-ecba` (a sentence parameterised over a type claims the whole class — carry every
type) and `mem-1785630967-6fdd` (*pre-existing* is a claim about the OTHER text — count the
casualty's anchor at both, do not reproduce its failure at one). Both are method for the next
reviewer, not work. `mem-1785624794-9c63`'s prohibition still stands and travels with this step: do
NOT add a top-level `id` rule to either chain — the pinned engine STRIPS a stale numeric `id` and
SERVES the dashboard.

**`a15c` was NOT re-`ensure`d.** Its description already carries PART A/PART B, the reachability
limit and all four acceptance criteria, measured. `ensure` reuses by key and REWRITES the record, so
re-supplying it is the clobbering risk DEC-182/DEC-132 priced. The twelve non-wave rows are likewise
not re-blocked behind it; they stay visibly ready so the next Planner prices them, and the Builder
is routed by the `tasks.ready` payload, not by scanning the ready list.

### THE OPERATOR GATE IS STILL THE HIGHEST-VALUE ACTION AND STILL NOT AGENT-CLOSABLE

`task-1785442499-1851` (4d) stays open, stays P1, and is untouched by this step: `just play`, then
open each Grafana dashboard and record which panels populate and which are empty and why. That
evidence re-prices the five Family-B rows directly (DEC-132's named input) and may file repo-side
work worth more than every guard row in this table. **Step 9 is what an agent may do while waiting,
not a substitute for it.** `.ralph/agent/operator-ask.md` carries the ask; RObot/Telegram is unwired
in this repo, so `human.interact` emits into a void and there is no interactive way to ask.

- **Test Requirements:** unchanged from every repo-side task in this objective — `just test` exits 0,
  the row RED-first under a reproducible mutation of the REAL files reverted in a `finally` with
  sha256 asserted at both ends, control rows GREEN, and an anti-vacuity clause for the state where
  the row finds nothing to check. **Plus the two this row owns:** the carriers are a SEPARATE
  delivered-file set — a dashboard `_read` cannot decode as UTF-8 whose bad byte sits at a SAVED
  position — and each carrier's expected field must be scored against the pinned
  `grafana/grafana:13.1.0`'s OWN container-log line rather than against the order in the source
  (`mem-1785593456-9d15`); and the NON-STRING member must be NAMED rather than dropped, which only
  the member-ALONE carrier can show (with a rule the engine really applies alongside it, the drop is
  invisible). Never edit another hat's harness — if an assertion falls, DISCLOSE and attribute it,
  and attribute it by counting its anchor at BOTH texts (`mem-1785630967-6fdd`). No live call, no
  `just play`, no vault value, no commit. Gates 1b/2b/3b/4d untouched.
- **Demo:** `just test` → GATE PASS; `logs/critic-fb36-r2-unreadable-sibling.py` PART A and PART B
  flip; PART C prints the two spellings agreeing on every carrier in both sets; the tree as
  delivered stays GREEN at PASS n/n.

---

## Step 10: Close the DOCSTRING layer — `_unreadable`'s blast-radius paragraph counts FIVE and the AST counts SIX

- **Objective:** `_unreadable`'s docstring paragraph "AND THE CLAUSE IS EARNED BY THE CALLER, NOT BY
  THE BYTE" (~:1168-1172 of `scripts/test_grafana_provisioning_shape.py`) asserts that
  "`provisioned=` is passed by the five readers that iterate `_delivered_dashboards`, **and by
  nothing else**". At the delivered guard `56bba79ef94e` six callers pass it. "And by nothing else"
  is the paragraph's whole point — it is the blast-radius claim that licenses the conclusion the
  reader is asked to draw — so a reader who audits it finds six and cannot tell whether the sixth
  caller is the very defect the sentence warns about or the sentence is merely stale.
- **Demoable outcome:** `just test` exits 0, `scripts/test_grafana_provisioning_shape.py` is PASS
  n/n on the tree as delivered, and the paragraph's number is one an AST sweep DERIVES rather than
  one a reader counts by eye — with the helper/row distinction that produced the discrepancy said
  out loud, and the sweep kept as a log so the next reader can re-run it.
- **Expected subtask wave:** ONE row. `task-1785634257-80de`.

### WHY THIS STEP AND WHY IT IS NOT A NEW BAR (DEC-205)

Step 5's bar — *a check that looks like it works and does not, with nothing saying so* — has not
moved since Step 6, and Step 7 moved the class one notch out to *the check fires correctly and then
sends the operator to the wrong field*. Step 10 is not a third bar. It is the class this thread
wrote down for itself and then did not finish walking. `mem-1785632642-168d`, banked during Step 9's
own rounds:

> a guard whose sentences are the deliverable has its contract in three places (docstring, inline
> comment, printed clause) and a round that updates only the printed one ships two false sentences.

Steps 7, 8 and 9 repaired the **printed clause** and the **inline comment** of the `_unreadable`
chain across four sites. **The docstring is the third place and nothing has been at it.** The
sentence Step 10 routes is not adjacent to that work by coincidence — it is in the docstring of the
very function Step 9 re-ordered.

**IT IS A FALSE SENTENCE, NOT A GAP.** That is the whole pricing argument against the other fresh
row and it is worth stating plainly: `80de` is a claim in shipped source that is **wrong**, while
`d2fd` is a gap the guard **discloses in its own voice** and cites an open id for. A reader of the
guard today is *misled* by the first and *correctly warned* by the second. A false sentence outranks
a disclosed gap, and the disclosed one is not going anywhere.

**RE-MEASURED AT MY OWN HANDS AT THIS CUT, NOT READ OFF THE FILER'S PROSE** (`mem-1785631438-d7dc`).
The row was filed by the a15c round-2 Critic against `9c08e2b54dc2`; the Finalizer has since moved
the file to `56bba79ef94e`. One AST sweep over the delivered tree, container-free, taking every
`_unreadable(...)` call with its enclosing function and its keyword set:

| line | enclosing function | keywords |
|------|--------------------|----------|
| :2151 | `_delivered_dashboard_documents` | `provisioned`, `rendered` |
| :4501 | `test_delivered_dashboards_reference_the_provisioned_uid` | `provisioned`, `rendered` |
| :4809 | `test_dashboard_delivery_inventory_is_complete` | *(neither)* |
| :5339 | `test_delivered_dashboards_parse_as_dashboards` | `provisioned`, `rendered` |
| :5635 | `test_delivered_dashboards_have_distinct_uids` | `provisioned`, `rendered` |
| :6022 | `test_delivered_dashboards_have_distinct_titles` | `provisioned`, `rendered` |
| :6443 | `test_pve_panels_name_series_the_exporter_declares` | `provisioned`, `rendered` |

Seven call sites, **six** pass `provisioned=`, one passes neither and is the silent side the same
paragraph describes — correct. The uncounted sixth is `_delivered_dashboard_documents`, a HELPER and
not a test row, which is very likely the entire story: the count was taken over test ROWS and the
sentence was written over CALLERS. **The filer's line numbers have moved and its SET has not** —
a15c round 4's comment lines pushed :5621→:5635, :6008→:6022, :6429→:6443. The defect is live at the
text the Builder starts from.

### THE ONE CORRECTION THIS CUT MAKES TO THE ROW, AND WHY IT IS `ensure`d RATHER THAN CARRIED

The row's acceptance (d) reads: *proven with the docstring-normalised AST diff oracle
`logs/builder-a15c-r2-pre-guard.py` PART D already builds*. **Three things are wrong with that
pointer and all three were measured here:**

1. **The harness is DEAD at the delivered sha.** `AssertionError: anchor not unique/present:
   "        # asked twice and none is dropped. \`_unreadable\`'s chain — the"`. a15c round 3 rewrote
   the comment block its second pair quotes — the exact failure mode `mem-1785634963-bf38` describes
   (a reverser is killed by the next round that edits its anchor).
2. **It never had a PART D.** `logs/builder-a15c-r2-collateral.py` is where the docstring
   normalisation lived, and it dies with it: it *imports* that reverser.
3. **Nothing living implements the oracle the row needs.** Rounds 3 and 4 were comment-only, so both
   used a RAW `ast.dump` equality with normalisation explicitly disabled. A **docstring** round
   cannot use that: `ast.dump` fails for the right reason and tells you nothing
   (`mem-1785633523-cbc8`). The round must BUILD the normalised oracle, not cite one.

The living reverser is **`logs/builder-a15c-r4-pre-guard.py`** — run at this cut and green,
rebuilding `821b687f6267` and chaining `8cb7299e4568` / `54cec7fc4cea` / `9c08e2b54dc2` with the
real path unmoved. Build the normalisation on top of it: replace every Module/FunctionDef/ClassDef
docstring with a placeholder, require the two dumps IDENTICAL (that is the statement about the CODE),
and then admit the set of differing docstrings BY NAME as the round's intended change.

Steps 8 and 9 both declined to re-`ensure` a routed row, and both were right: what they had was new
EVIDENCE, which rides in the payload. **This is different in kind.** An acceptance criterion that
points at a harness which cannot run is a false CONTRACT, and handing it to a Builder is
`mem-1785636803-90cb`'s defect ("a citation must be green at the sha it ships at") one layer out
into the queue record. It is corrected where the Builder will read it. The rest of the description
is preserved verbatim.

### BLAST RADIUS, PRE-MEASURED AND HANDED OVER

`logs/red-579d-r4-critic-recheck.py` is the **only** other file in `logs/` or `scripts/` that quotes
the sentence (at its line 104). It is **already RED at the delivered tree before this row touches
anything**: SCORE **9/16**, `R14-unique MISS pair 14: the round-4 text appears 0x`, and its
reconstruction is `76eea07b` against a reviewed guard of `e102f69b`, so it skips its own re-score.
That is the exoneration handed over rather than left to be rediscovered — and it is handed over in
the only form that is a claim: **count the anchor at BOTH texts, do not reproduce the failure at
one** (`mem-1785630967-6fdd`). The round still owes the census; it does not owe the discovery.

### THE PRICING, ON THE BAR AND NOT ON PRIORITY

`80de` is P3 and `fc70` is P2, so this needs an argument. Both were re-priced here, and the honest
statement first: **`80de` is BELOW `fc70` on the silent/loud bar.**

- **`fc70` (P2, delivery arity) is the SILENT one and it still does not lead.** Its harm clears
  Step 5's bar outright — the guard prints `2 delivered dashboard(s)` where a real
  `ansible-playbook` leaves 1 file on disk. Its deferral was never `a15c`-relative and has not
  discharged: acceptance (c) demands *every row whose verdict the repair moves enumerated in a log
  and each move argued*, because the fix may belong in the INVENTORY BUILDER that every
  `files`-keyed row is built from and may move rows that are currently GREEN — and its own
  description says **this repo's delivered tree does not carry the class today** (full-path dests,
  `mem-1785620824-120c`). A wide-blast-radius increment against an unreachable-today class, in a
  file whose entire history is that batching gets a round rejected. Unchanged since the Step 9 cut
  priced it the same way.
- **`d2fd` (P3, acceptance (b)'s readable half) is the declared successor and not this row.** It is
  the strongest ready row after `80de` and it is a genuine gap — the two spellings were compared on
  `_unreadable`'s undecodable carriers only, and the five-slot chain's own set has no carriers and
  no run. But the guard SAYS SO in its own voice and cites `task-1785635701-d2fd` by id, which is
  a15c round 4 doing exactly what DEC-197 asks. Disclosed-and-banked outranks nothing; it is
  outranked by *false*.
- **`80de` leads on cost, freshness and finish.** One AST sweep the Planner has already run,
  container-free, PROSE-ONLY, against a sentence in the docstring of the function Steps 7-9 spent
  four rounds inside — and it is the last of the three places `mem-1785632642-168d` names. `done`
  has an oracle that is a `str` and an `ast.dump`, not a container.

### STANDING DEFERRALS RE-CHECKED AT THIS CUT AND UNMOVED

- The five **Family-B** rows (`b939`, `adc5`, `1b02`, `580a`, `aca4`) keep **DEC-132**. Its named
  input — 4d's operator walkthrough — **still has not arrived.** Neither `b939` nor `1b02` is
  re-priced downward or retired.
- `cd0e`, `9df3`, `bad2`, `8144` keep **DEC-153**'s table.
- `7407` is the same class one priority lower. `0956` is silent in character but **unmeasured by
  anyone** — a research row before it is a build row.
- `fc70` keeps its own standing clause, priced above. `d2fd` is the declared successor.
- `mem-1785624794-9c63`'s prohibition still stands and travels with this step: do **NOT** add a
  top-level `id` rule to either chain — the pinned engine STRIPS a stale numeric `id` and SERVES the
  dashboard, so the rule would be a refusal the delivery path does not make.

### THE ARITHMETIC

`<ready-tasks>` holds **15** rows. One of them is `task-1785442499-1851` — 4d, **OPERATOR ONLY** and
unclosable by any agent. **Agent-actionable is 14**, plus 1 operator gate. The Step 9 cut counted 13;
the difference is arithmetic and not drift — `a15c` closed and left the list, and its own rounds
banked TWO new rows (`task-1785634257-80de` and `task-1785635701-d2fd`), so 13 − 1 + 2 = 14. Nothing
was filed and nothing was retired by this Planner. After this cut `80de` is the wave and **13 rows
defer**.

### WHAT THIS STEP IS NOT A SUBSTITUTE FOR

**4d is still the only thing in this objective that can move the objective.** Every guard row in this
table makes the safety net honest; none of them puts a panel in front of a human. 4d's evidence
re-prices the five Family-B rows directly (DEC-132's named input) and may file repo-side work worth
more than every guard row left. **Step 10 is what an agent may do while waiting, not a substitute
for it.** `.ralph/agent/operator-ask.md` carries the ask; RObot/Telegram is unwired in this repo, so
`human.interact` emits into a void and there is no interactive way to ask.

- **Test Requirements:** unchanged from every repo-side task in this objective — `just test` exits 0
  and the guard is PASS n/n on the tree as delivered. **Plus the three this row owns:** (1) the
  number in the sentence is **DERIVED** by the same AST sweep the round ships, kept as a log, and not
  counted by eye; (2) the round is **PROSE-ONLY**, proven by a **docstring-NORMALISED** `ast.dump`
  equality built on `logs/builder-a15c-r4-pre-guard.py` — with the changed docstring admitted by
  name — and NOT by the dead `logs/builder-a15c-r2-pre-guard.py`; (3) the neighbouring number in the
  same docstring ("11 rows keyed on a DELIVERY printed it against the 1 that had earned it", ~:1205)
  is a **different count over a different measured run** and **MUST NOT** be edited to agree with
  this one. Never edit another hat's harness — if an assertion falls, DISCLOSE and attribute it by
  counting its anchor at BOTH texts (`mem-1785630967-6fdd`); `red-579d-r4-critic-recheck.py`'s
  pre-existing 9/16 is already measured above. No live call, no `just play`, no vault value, no
  commit. Gates 1b/2b/3b/4d untouched.
- **Demo:** `just test` → GATE PASS; the shipped sentence's number equals the count the round's own
  AST sweep prints, re-runnable from `logs/`; the helper/row distinction is stated so a bare 5→6 edit
  is not mistaken for the repair; the docstring-normalised dumps are IDENTICAL with exactly one
  docstring named as changed; the tree as delivered stays GREEN at PASS n/n.
