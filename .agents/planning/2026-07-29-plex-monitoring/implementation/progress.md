# Progress — plex-monitoring

## Current Step

**STEP 10 — Close the DOCSTRING layer of the misdirected-sentence class: `_unreadable`'s
blast-radius paragraph says FIVE readers pass `provisioned=` and the AST counts SIX. CUT 2026-08-02
(Planner, `queue.advance` after `task-1785624345-a15c` closed at guard `56bba79ef94e`), DEC-205.**

**Wave is ONE row and it is routed by this activation: `task-1785634257-80de`**
(`code-assist:plex-monitoring:guard:unreadable-provisioned-caller-count`, P3). At **:1170** of
`scripts/test_grafana_provisioning_shape.py`, inside `_unreadable`'s docstring paragraph "AND THE
CLAUSE IS EARNED BY THE CALLER, NOT BY THE BYTE":

> `provisioned=` is passed by the five readers that iterate `_delivered_dashboards`, and by nothing
> else.

Six callers pass it. Full pricing table in `plan.md` Step 10.

**THE BAR HAS NOT MOVED AND THIS IS NOT A NEW CLASS.** `mem-1785632642-168d`, banked during Step 9's
own rounds, wrote it down: *a guard whose sentences are the deliverable has its contract in three
places — docstring, inline comment, printed clause — and a round that updates only the printed one
ships two false sentences.* Steps 7, 8 and 9 repaired the **printed clause** and the **inline
comment** across four sites of the `_unreadable` chain. **The docstring is the third place and
nothing has been at it**, and the sentence is in the docstring of the very function Step 9
re-ordered.

**IT IS A FALSE SENTENCE, NOT A GAP — that is the whole argument for routing it over `d2fd`.**
`80de` is a claim in shipped source that is **wrong**; `d2fd` is a gap the guard **discloses in its
own voice** and cites an open id for (a15c round 4 doing exactly what DEC-197 asks). A reader of the
guard today is *misled* by the first and *correctly warned* by the second.

**RE-MEASURED AT MY OWN HANDS AT THIS CUT, NOT ADOPTED FROM THE FILER'S PROSE**
(`mem-1785631438-d7dc`). The row was filed against `9c08e2b54dc2` and the a15c Finalizer has moved
the file to `56bba79ef94e` since, so a re-run was owed before routing. One container-free `ast`
sweep over the delivered tree, every `_unreadable(...)` call with its enclosing function and keyword
set: **7 call sites, SIX pass `provisioned=`** — `_delivered_dashboard_documents` (:2151),
`test_delivered_dashboards_reference_the_provisioned_uid` (:4501),
`test_delivered_dashboards_parse_as_dashboards` (:5339),
`test_delivered_dashboards_have_distinct_uids` (:5635),
`test_delivered_dashboards_have_distinct_titles` (:6022),
`test_pve_panels_name_series_the_exporter_declares` (:6443) — and **exactly one passes neither**
(`test_dashboard_delivery_inventory_is_complete`, :4809), the silent side the same paragraph
describes, correct. **The filer's LINE NUMBERS have moved and its SET has not:** a15c round 4's
comment lines pushed :5621→:5635, :6008→:6022, :6429→:6443. The uncounted sixth is a HELPER, not a
test row — very likely the whole story, and acceptance (b) already forbids a bare 5→6 edit that
leaves that ambiguity standing.

**ONE CORRECTION IS OWED TO THE ROW, AND IT IS WHY THIS CUT RE-`ensure`d IT.** Acceptance (d) named
`logs/builder-a15c-r2-pre-guard.py` PART D as the inertness oracle. Measured here, three things are
wrong with that pointer: **(1)** the harness is **DEAD at the delivered sha** — `AssertionError:
anchor not unique/present: "        # asked twice and none is dropped. \`_unreadable\`'s chain — the"`
— because a15c round 3 rewrote the comment block its second pair quotes (`mem-1785634963-bf38`);
**(2)** it **never had a PART D** — the docstring normalisation lived in
`logs/builder-a15c-r2-collateral.py`, which dies with it because it *imports* that reverser; **(3)**
**nothing living implements the oracle this row needs** — rounds 3 and 4 were comment-only and both
used a RAW `ast.dump` with normalisation explicitly disabled, which for a **docstring** round fails
for the right reason and tells you nothing (`mem-1785633523-cbc8`). The living reverser is
**`logs/builder-a15c-r4-pre-guard.py`**, run at this cut and green (rebuilds `821b687f6267`, chains
`8cb7299e4568` / `54cec7fc4cea` / `9c08e2b54dc2`, real path unmoved). The round must **BUILD** the
normalised-dump oracle on it, not cite one.

Steps 8 and 9 both declined to re-`ensure` a routed row and both were right — what they had was new
EVIDENCE, which rides in the payload. **This is different in kind:** an acceptance criterion pointing
at a harness that cannot run is a false CONTRACT, which is `mem-1785636803-90cb`'s defect ("a
citation must be green at the sha it ships at") one layer out into the queue record. It is corrected
where the Builder reads it, and the rest of the description is preserved verbatim.

**BLAST RADIUS PRE-MEASURED AND HANDED OVER RATHER THAN LEFT TO BE REDISCOVERED.**
`logs/red-579d-r4-critic-recheck.py` (line 104) is the **only** other file in `logs/` or `scripts/`
quoting the sentence, and it is **already RED at the delivered tree before this row touches
anything**: SCORE **9/16**, `R14-unique MISS pair 14: the round-4 text appears 0x`, reconstruction
`76eea07b` against a reviewed guard of `e102f69b`, so it skips its own re-score. The round still owes
the census — and owes it in the only form that is a claim: **count the anchor at BOTH texts, do not
reproduce the failure at one** (`mem-1785630967-6fdd`).

**THE ROUTED ROW IS P3 AND `fc70` IS P2, SO THE PRICING IS ARGUED RATHER THAN DECLARED, AND `80de`
IS HONESTLY BELOW IT ON THE SILENT/LOUD BAR.** `fc70` is the silent one and clears Step 5's bar
outright — the guard prints `2 delivered dashboard(s)` where a real `ansible-playbook` leaves 1 file
on disk — but its deferral was never `a15c`-relative and has not discharged: acceptance (c) demands
every row the repair moves enumerated in a log and each move argued, because the fix may belong in
the INVENTORY BUILDER every `files`-keyed row is built from and may move rows that are currently
GREEN, and its own description says the delivered tree does not carry the class today
(`mem-1785620824-120c`). A wide-blast-radius increment against an unreachable-today class, in a file
whose history is that batching gets a round rejected. `80de` leads on cost, freshness and finish
instead: one AST sweep already run, container-free, PROSE-ONLY, and the last of the three places
`mem-1785632642-168d` names.

**STANDING DEFERRALS RE-CHECKED AT THIS CUT AND UNMOVED.** The five Family-B rows (`b939`, `adc5`,
`1b02`, `580a`, `aca4`) keep DEC-132 — its named input, 4d's operator walkthrough, **still has not
arrived** — and neither `b939` nor `1b02` is re-priced downward or retired. `cd0e`, `9df3`, `bad2`,
`8144` keep DEC-153's table. `7407` is the same class one priority lower. `0956` is silent in
character but **unmeasured by anyone** — a research row before it is a build row. `fc70` keeps its
own standing clause, priced above. `d2fd` is the **declared successor**.

**QUEUE HYGIENE THIS TURN: NOTHING FILED, NOTHING RETIRED.** `mem-1785624794-9c63`'s prohibition
still stands and travels with this step: do **NOT** add a top-level `id` rule to either chain — the
pinned engine STRIPS a stale numeric `id` and SERVES the dashboard, so the rule would be a refusal
the delivery path does not make.

**THE ARITHMETIC.** `<ready-tasks>` holds **15** rows; one is `task-1785442499-1851` — 4d, OPERATOR
ONLY and unclosable by any agent. **Agent-actionable is 14**, plus 1 operator gate. The Step 9 cut
reported 13 and that is not drift, it is arithmetic: `a15c` closed and left the list, and its own
rounds banked TWO new rows (`task-1785634257-80de` and `task-1785635701-d2fd`), so 13 − 1 + 2 = 14.
**This Planner filed nothing and retired nothing** — both newcomers are the Builder's and the
Critic's, banked rather than deferred in prose, which is DEC-197's shape done right. After this cut
`80de` is the wave and **13 rows defer**.

**WHAT IS DELIBERATELY NOT DONE (confidence ~85), unchanged from DEC-200/DEC-198/DEC-194/DEC-182/DEC-132.**
The thirteen non-wave rows are NOT re-blocked behind `80de`; they stay visibly ready, because that
is what makes the next Planner price them, and because re-blocking means re-supplying thirteen long
measured descriptions through a command that rewrites the record. The Builder is routed by the
`tasks.ready` payload, not by scanning the ready list. **4d is still the only thing in this objective
that can move the objective** — every guard row here makes the safety net honest; none puts a panel
in front of a human. Step 10 is what an agent may do while waiting, not a substitute for it.

---

### The state this replaces, kept for the chain

**STEP 9 — CLOSED 2026-08-02, WAVE EXHAUSTED AT ITS ONE ROW.** `task-1785624345-a15c` closed by the
Finalizer at guard **`56bba79ef94e`**, PASS 22/22, gate 36/36 rc=0, HEAD `7e9c426`, no commit —
after 4 review rounds and an IN-HAT repair of the one defect round 4's `review.passed` named
(DEC-203 → DEC-204, `logs/finalizer-a15c-r4-repair.py` 22/22). No agent-side work remains in this
step; the next wave is the Planner's to cut. The cut description below is kept as delivered.

**CUT 2026-08-02 (Planner, `queue.advance` after `task-1785622294-ba6c` closed at guard
`9c08e2b54dc2`), DEC-200 — Close the FIRST spelling of the rule order: `_unreadable`'s save-layer
chain fences the uid predicate with `isinstance()` alone, so the trim-class member outranks the
number AND the non-string member is dropped entirely.**

**Wave is ONE row and it is routed by this activation: `task-1785624345-a15c`**
(`code-assist:plex-monitoring:guard:unreadable-chain-uid-halves`, P3) —
`scripts/test_grafana_provisioning_shape.py` holds the save-layer rule order in TWO spellings, and
this is the one Steps 7 and 8 did not reach. At **:1415** the chain asks
`(_grafana_short_uid_defect(uid) if isinstance(uid, str) else None, GRAFANA_LOG_SAVE)` **2nd of
four** — ahead of the deferred number at :1417 and the tags at :1419. `_grafana_short_uid_defect` is
four rules under one name and only TWO are refusals; the repaired spelling at **:5362-5367** splits
them at `isinstance(uid, str) and _grafana_stored_uid(uid) is not None`. `isinstance(uid, str)`
alone is HALF that line, so this chain gets both non-refusing members wrong in OPPOSITE directions:
the trim-class member is MIS-ORDERED (ahead of the number and the tag) and the non-string member is
DROPPED (the fence yields `None` and nothing re-asks the predicate). Full pricing table in `plan.md`
Step 9.

**RE-MEASURED AT MY OWN HANDS AT THIS CUT, NOT ADOPTED FROM THE FILER'S PROSE.** The row's evidence
was scored at guard `a70d851ce802` and `ba6c` has moved the file to `9c08e2b54dc2` since, so a
re-run was owed before routing: `logs/critic-fb36-r2-unreadable-sibling.py` → **PASS 6/6** on the
delivered tree, PART Z confirming the sha. `ba6c` left this chain untouched and the defect is live
at the text the Builder starts from. I also read the two sites directly rather than trusting the
harness's summary — the line numbers above are from the delivered file.

**THE TWO SPELLINGS NOW DISAGREE ON A CLASS'S POLARITY, NOT MERELY ON ITS POSITION.** For a
NON-STRING uid alone, the repaired row's 5th link names `uidtype-NOTAREFUSAL` while `_unreadable`'s
chain names nothing at all and prints its `SAVES this file with those bytes replaced by U+FFFD`
clause (PART C of the same run prints the pair). That is a contradiction inside one file that Steps
7 and 8 created the visibility for, and it is the whole reason this step exists rather than the
queue advancing to a different class.

**THE ROUTED ROW IS P3 AND `fc70` IS P2, SO THE PRICING IS ARGUED RATHER THAN DECLARED.** `fc70` is
the SILENT one and it clears Step 5's bar outright — the inventory prints `2 delivered dashboard(s)`
where the filesystem holds 1 — but its deferral was never `fb36`-relative and has not discharged:
its own acceptance criterion (c) demands every row the repair moves enumerated in a log and each
move argued, because the fix may belong in the INVENTORY BUILDER every `files`-keyed row is built
from and may move rows that are currently GREEN, and its own description says the delivered tree
does not carry the class today (this repo ships full-path dests, `mem-1785620824-120c`). That is a
wide-blast-radius increment against an unreachable-today class in a file whose history is that
batching gets a round rejected. `a15c` is honestly BELOW it on the silent/loud bar — the file is RED
either way there, so this is a wrong REASON to an operator and not a false GREEN — and it leads on
cost and freshness instead: one ordering in one function, its engine half already measured on the
pinned image, and the repair shipped one screen away by `fb36` round 2, so `done` has a diff for an
oracle.

**THE ARITHMETIC, CORRECTED.** The Step 8 close reported "14 agent-actionable rows remain ready".
`<ready-tasks>` holds 14 rows, but one is `task-1785442499-1851` — 4d, OPERATOR ONLY and unclosable
by any agent. **Agent-actionable is 13**, plus 1 operator gate; it was 14 at the Step 8 cut only
because `ba6c` was itself in that wave. After this cut `a15c` is the wave and 12 rows defer.

**STANDING DEFERRALS RE-CHECKED AT THIS CUT AND UNMOVED.** The five Family-B rows (`b939`, `adc5`,
`1b02`, `580a`, `aca4`) keep DEC-132 — its named input, 4d's operator walkthrough, **still has not
arrived**, and neither `b939` nor `1b02` is re-priced downward or retired (`b939`'s own description
calls the harm LOUD at the artifact; `1b02` closes its own reachability question). `cd0e`, `9df3`,
`bad2`, `8144` keep DEC-153's table. `7407` is the same class one priority lower. `0956` is silent in
character but **unmeasured by anyone** — a research row before it is a build row. `fc70` keeps its
own standing clause, priced above.

**QUEUE HYGIENE THIS TURN: NOTHING FILED, NOTHING RETIRED.** The `ba6c` round banked two things and
NEITHER is a defect: `mem-1785627131-ecba` (a sentence parameterised over a type claims the whole
class — carry every type, not a representative) and `mem-1785630967-6fdd` (*pre-existing* is a claim
about the OTHER text — count the casualty's anchor at both, do not reproduce its failure at one).
Both are method for the next reviewer, not work. `mem-1785624794-9c63`'s prohibition still stands and
travels with this step: do **NOT** add a top-level `id` rule to either chain — the pinned engine
STRIPS a stale numeric `id` and SERVES the dashboard, so the rule would be a refusal the delivery
path does not make. Inventing a row for it is what the queue contract forbids.

**WHAT IS DELIBERATELY NOT DONE, unchanged from DEC-198/DEC-194/DEC-182/DEC-132 (confidence ~85).**
`a15c` was **NOT re-`ensure`d** — its description already carries PART A/PART B, the reachability
limit and all four acceptance criteria, measured, and `ensure` reuses by key and REWRITES the record.
The twelve non-wave rows are NOT re-blocked behind it either; they stay visibly ready, because that
is what makes the next Planner price them, and because re-blocking means re-supplying twelve long
measured descriptions through a command that rewrites the record. The Builder is routed by the
`tasks.ready` payload, not by scanning the ready list.

---

### The state this replaces, kept for the chain

**STEP 7 — Close the MISDIRECTED-ALARM guard rows: the gate is RED and the verdict names a field the
engine never looked at. CUT 2026-08-01 (Planner, `queue.advance` after `task-1785601096-9ffc` closed
at guard `9c61b6112215`), DEC-194. CLOSED 2026-08-01 at `a70d851ce802`, wave exhausted at its one
row — `task-1785594766-fb36`, build → 2 review rounds → PASSED → CLOSED, PASS 22/22, gate 36/36
rc=0, HEAD `7e9c426`, no commit.**

**Wave is ONE row and it is routed by this activation: `task-1785594766-fb36`**
(`code-assist:plex-monitoring:guard:readable-row-rule-order`, P2) —
`test_delivered_dashboards_parse_as_dashboards` asks its rules in the wrong order in TWO directions,
measured at **0/2** on WHOLE gate runs (`logs/critic-579d-r8-uidlen-and-readable-row.py` PART D):
an illegal uid + a blank-after-trim title makes the row name the **UID** where the engine names the
**TITLE**, and a number past the IEEE double range makes it name the **NUMBER** — the parse raises
before any field is read — where the engine still names the **TITLE**. Full pricing table, and why
this row and not the other twelve, in `plan.md` Step 7.

**THE BAR DID NOT MOVE; THE INVENTORY UNDER IT DID.** Step 5's bar — a check that looks like it
works and does not, with nothing saying so — stays the ordering principle, and Step 6 emptied it of
every row that cleared it outright by closing `9ffc` at 22/22. **Step 6's own table already wrote
down where the queue goes next**, in the row it deferred: *"Real, and NEXT in line — but LOUDER …
same file as `9ffc`, so it serialises behind it either way, and its measured order does not go
stale."* Both halves of that deferral have expired — `9ffc` is closed, and `fb36` was deferred
RELATIVE TO A SILENT ROW, never on a standing reason of its own. Every other open row still carries
its standing reason, re-checked this turn and unmoved (Family-B on DEC-132, whose named input — the
4d walkthrough — still has not arrived; `cd0e`/`9df3`/`bad2`/`8144` on DEC-153's table; `7407` one
priority lower in this same class; `0956` silent in character but **unmeasured by anyone and P3**,
a research row before it is a build row). `fb36` is the only open P2 in this namespace with no
standing deferral against it, and that is where the `9ffc` Finalizer independently priced it.

**THIS IS THE LOUD CLASS AND THE STEP SAYS SO PLAINLY.** The gate is already RED when `fb36` fires,
so nobody is missing an outage — what they are missing is the hour spent on a field the engine never
looked at. Smaller harm than a silent hole, which is exactly why it is routed AFTER the silent rows
and not instead of them. What makes it cheap now is that the repair already exists one screen away:
`_unreadable`'s save-layer chain (~line 1413) asks these same rules in the engine's measured order
with the number deferred out of the parse. **The order is written down and MUST NOT be re-derived**
(`mem-1785592369-90dd`).

**QUEUE HYGIENE DONE THIS TURN (the `9ffc` Finalizer flagged it as the Planner's):**
`task-1785621026-fc70` is **NEW** (P2,
`code-assist:plex-monitoring:guard:delivery-arity-shared-basename-one-dest`). The H1 class existed
only as `mem-1785620544-7b12`/`mem-1785620824-120c` with no runtime row, and this repo's own rule is
that a defect declared and never scheduled is not banked, it is shipped. **The Finalizer's
measurement also changed what the class IS:** round 13's review deferred H1 as an identity-print
problem no print could reach; the Finalizer then asked a real `ansible-playbook`
(`logs/finalizer-9ffc-r13-h1-one-file-on-disk.py` 8/8) and found an INVENTORY defect — two `copy:`
tasks with distinct-byte srcs under one basename onto a directory `dest:` leave ONE file (A1), the
survivor is the second src (A2), the distinct-basename CONTROL leaves two (A3). The guard groups per
DELIVERY where ansible resolves per ADDRESS, so it prints `2 delivered dashboard(s)` over one file.
It is filed, not waved: same file as `fb36`, and its own acceptance criteria demand a blast-radius
enumeration first because the repair may belong in the inventory builder and may move rows that are
currently GREEN. **Agent-actionable ready rows: 12 → 13.**

**WHAT WAS DELIBERATELY NOT DONE, unchanged from DEC-182 and DEC-132 (confidence ~85).** The twelve
non-wave rows were NOT re-blocked behind `fb36`, so they stay visibly ready. `ralph tools task
ensure` reuses by key and REWRITES the record, so re-blocking twelve rows means re-supplying twelve
long, carefully-measured descriptions and risking clobbering them — a data-loss risk taken against a
bookkeeping invariant. Their being VISIBLY ready is what makes the next Planner price them; the
Builder is routed by the `tasks.ready` payload, not by scanning the ready list.

---

### The state this replaces, kept for the chain

**STEP 6 — Close the SILENT-class guard rows filed AFTER Step 5's wave was cut. CUT 2026-08-01
(Planner, `queue.advance` after `task-1785571102-579d` closed at guard `c1fbc7b3`), DEC-182.
CLOSED 2026-08-01 at `9c61b6112215`, wave exhausted at its one row.**

**Wave is ONE row and it is routed by this activation: `task-1785601096-9ffc`**
(`code-assist:plex-monitoring:guard:duplicate-title-provider-lockout`, P2) — two delivered
dashboards with the SAME title and distinct legal uids take the provider-wide write lockout, the
engine names NO cause, both files are still served, and the guard is GREEN over it at PASS 21/21.
Full pricing table, and why this row and not the other eleven, in `plan.md` Step 6.

**This REVERSES DEC-153's "no Step 6 is cut", on three facts DEC-153 did not have:** the empty queue
was met three times (iterations 88/89/90) and produced no event; the operator's answer was to
RESTART the runner, not to open a browser; and iteration 91 then routed a filed guard row (`579d`)
which ran build → 12 review rounds → PASSED → CLOSED and closed a real hole. **The queue contract's
"leave the queue empty so the Finalizer can terminate" does not apply, because the queue is not
empty** — twelve agent-actionable rows are open in this objective's own `guard:*` namespace.
Inventing tasks is forbidden; leaving already-filed, already-measured rows homeless is the defect
that caused Step 5 to be cut in the first place.

**AND THE BAR IS STILL THE BAR — this is not a route-by-readiness.** `progress.md` warned a resume
against exactly that, and the warning holds. `9ffc` was priced against Step 5's own bar (SILENT vs
LOUD) and clears it on three axes measured rather than asserted: silent at the ENGINE (no message of
any kind, three polls, three bare lockout lines — which refuted the probe's own first prediction),
silent at the ARTIFACT (both files still served; the damage is every FUTURE edit, silently dropped),
silent at the GUARD (whole-guard run over a colliding tree PASSes 21/21). The two next-best rows
(`fb36`, `7407`) are the LOUD class — the gate is already RED when they fire, they merely name the
wrong field — and they serialise behind `9ffc` in the same file regardless.

**QUEUE HYGIENE DONE THIS TURN (the `579d` Finalizer flagged it as the Planner's):**
`task-1785504947-fbde` is **CLOSED**. It was re-titled `SUPERSEDED by task-1785509072-b939` on
2026-07-31 when the two were merged, and was still sitting open at P2 in the ready list. Verified
before closing rather than taken on the title: same mechanism (`_promql_skip_quoted` runs to the end
of the text so `_promql_match_paren` never closes and `_promql_calls` drops the call), same exemplar
(`sum(plex_media_count{"type!="show_episode"})`), and `b939`'s own description already carries the
one thing `fbde` added — the accept-side price, `plex_media_count{$filter}` and
`traefik_service_requests_total{service="plex@file",code=~"$code"}` must stay GREEN. `b939` is open
and canonical. **Agent-actionable ready rows: 13 → 12.**

**WHAT WAS DELIBERATELY NOT DONE, and it is a judgement call (confidence ~85, DEC-182).** The
eleven non-wave rows were NOT re-blocked behind `9ffc`, so they stay visibly ready. `ralph tools
task ensure` reuses by key and rewrites the record, so re-blocking eleven rows means re-supplying
eleven long, carefully-measured descriptions and risking clobbering them — a data-loss risk taken
against a bookkeeping invariant. DEC-132 made the same call for the same reason and named the
upside: the rows being VISIBLY ready is what makes the next Planner price them. The Builder is
routed by the `tasks.ready` payload, not by scanning the ready list — iteration 88 proved that
directly by blocking on an EMPTY payload while nine rows were ready.

---

### The state this replaces, kept for the chain

**NONE — every numbered step in `plan.md` is closed. Written 2026-08-01 (Planner, `queue.advance`
after 5d closed).**

**Step 5's four-row wave is EXHAUSTED (5a/5b/5c/5d all closed) and Step 5 was the last numbered
step, so no Step 6 is cut and the agent-side queue is empty BY DECISION (DEC-153).** The Planner
contract forbids inventing tasks once the numbered steps run out, and Step 5's own text pre-wrote
this moment with two branches: *re-price the deferrals with 4d's operator evidence if it has
arrived, or record that Step 5 is exhausted and that everything remaining is either operator-gated
or deferred-with-reasons.* **4d (`task-1785442499-1851`) is open and OPERATOR-ONLY — nobody has
opened a Grafana panel — so branch 2 applies, and branch 2 is a recording action, not a routing
one.** No `tasks.ready` was published; the full pricing table is in `plan.md` Step 5, "THE CLOSE".

**THE ONE THING LEFT IN THE WHOLE NUMBERED PLAN IS 4D, AND NO AGENT MAY DO IT.** Its blockers
(4a/4b/4c) are closed, both tokens are vaulted and 2a's `0644` `prometheus.yml` repair is in the
tree — so it is not merely open, it is **fully actionable by David today**: `just play`, then open
each dashboard. Its step 5 asks him to record which panels were empty and why, and that is the
input that re-prices all eleven deferred rows — and may file repo-side work worth more than any of
them. `.ralph/agent/operator-ask.md` carries the ask; RObot/Telegram is unwired, so there is no way
to ask interactively.

**QUEUE-STATE CORRECTION — the "four operator gates" claim was wrong and is now one (DEC-154).**
`plan.md`, this file and the 5d Finalizer's own `queue.advance` payload all said 1b/2b/3b/4d were
open. `task-1785290391-b51a` (1b), `task-1785324247-3934` (2b) and `task-1785370581-de17` (3b) are
`status: closed` on the queue's record. Corroborating, not proving: `ansible/group_vars/all/vault.yml`
is MODIFIED in the working tree, mtime 2026-07-30 01:56 — between 2a's close and 3b's — and every
hat here declared "no vault value" in every round, so that edit is the operator's; and
`task-1785460529-aeb4`, the 4b Critic's own question about exactly this, is itself closed. **The
limit, stated:** this is the queue's state, not a live verification. No agent re-ran a query, and no
agent should reopen an operator's own gate on suspicion — 4d is where it gets checked.

**WHAT A RESUME MUST NOT DO.** `mem-1785119117-63d8`'s rule — *a resume without a close means route
past the gate, not park again* — was written for a park with work behind the gate. **There is none
here.** If this loop is resumed with 4d still open, the correct move is to re-price the eleven
deferred rows with whatever new information the resume carries, or to declare completion — **not**
to route a below-bar row by default because the queue looks ready.

---

### The step this replaces, kept for the chain

**Step 5 — Close the guard findings that make a delivered artifact SILENTLY wrong.** Created
2026-07-31 (Planner, `queue.advance` after 4c closed). Step 4's agent-side wave is EXHAUSTED —
4a/4b/4c all closed, 4d is an operator gate — and the close left **nine agent-side runtime tasks
ready and belonging to no numbered step**: eight `code-assist:plex-monitoring:guard:*` rows banked
across Steps 3 and 4, plus one P3 battery flip. The 4c Finalizer routed the pricing question here:
*are the eight one wave, or eight independent P2s?* **Neither, and the answer is the work of this
step.** Full reasoning in `plan.md` Step 5; the short form:

- **The bar is this objective's own recurring defect** — a change or a check that looks like it
  works and does not, with nothing saying so (Traefik's own default buckets; the `/metrics` no-op
  path; `plex_up` vs the token; the `0640` `prometheus.yml`). All nine findings are real and
  measured; what separates them is whether their failure is SILENT or LOUD.
- **Wave = three (silent class).** 5a `task-1785497167-e413` (the templating hole — Step 4's own
  Test Requirement, the CT 110/111 drop-down, GREEN today over a dashboard whose every panel would
  render a broken query); 5b `task-1785517907-a5ec` (datasource `type` vs the uid beside it — one
  comparison, and the mismatch is a defect in its own right); 5c `task-1785441840-e8eb` (the
  `<svc>-web` twins' `rule` clause — the only one of the nine with a measured live consequence,
  403/404 on the public host, and ready-but-unrouted since 2026-07-30). 5b and 5c are blocked by 5a.
- **Six deferred BEHIND the wave, reason recorded, none deleted.** `task-1785509072-b939` +
  `task-1785504947-fbde` are **ONE finding filed twice** (merged: b939 canonical, fbde's unique
  accept-side price appended to it, fbde re-titled SUPERSEDED); `task-1785506726-adc5` carries a
  measured FALSE REFUSAL of a correct panel (D5); `task-1785516964-1b02` says in its own text that
  nobody types it by accident; `task-1785457578-580a` needs a compound precondition nothing in the
  tree meets and both its runtime outcomes are loud; `task-1785517288-aca4` is P3.
- **Why deferral and not a build.** Four of those five are the SAME PromQL scanner clause that
  consumed **eleven review rounds** of Step 4c. The Finalizer refused a twelfth and called it
  review-termination rather than rigour. This repo has been rejected twice for a guard that forbids
  the real answer, and two of these rows have already measured that exact price. They unblock when
  5c closes, so a future Planner re-prices them with 4d's operator evidence in hand — which is new
  information none of them has.

**Queue effect, verified:** the agent-side ready set went from nine to ONE (`task-1785497167-e413`).
The only other ready task is 4d, which is the operator's and is not routed to a Builder.

**UPDATED 2026-08-01 (Planner, `queue.advance` after 5c closed). Three of four are closed. 5d is the
LAST agent-side row in this step and this `queue.advance` routes it — and the six deferrals came
back into the ready set exactly as the prior Planner predicted in writing, so the pre-commitment is
what answers them, not a fresh re-cut.**

- **5c `task-1785441840-e8eb` CLOSED** after 5 rework rounds, all of them the same question in a
  different place: r2 the rule's OPERATORS (a rule is a boolean expression, so a set of `Host()`
  arguments cannot tell `Host(h)` from `!Host(h)`), r3 the argument ARITY, r4 the whitespace CLASS
  at four seams on the `rule` path, r5 that class on the `service` clause at all four sites that
  read it plus the shared reader's seven other keys. Guard `53338616` **PASS 42/42** (41 → 42 is
  the plan's own Demo clause), gate **36/36 rc=0**, HEAD still `7e9c426`, templates
  `02a4c5c2`/`097eca50` untouched, no commit. The Finalizer's own round went where none of the five
  did — the GROWTH direction (`logs/finalizer-step05c-new-twin.py` **10/10**: a twin ADDED to either
  provider is discovered, `examined` 7 → 8, so the roster really is a floor and not the population)
  — and re-measured the one judgement the pass rests on rather than trusting it
  (`logs/finalizer-step05c-f0-loudness.py` **12/12**: the guard is blind 8/8 to the
  `splitlines()`-vs-`b-char` class at the file provider's own carrier, and all eight draw a
  **go-yaml load error** from the real compose parser, so the review's "loud, do not file" call was
  right). `mem-1785550680-84fa`, `mem-1785550692-1844`.
- **5d `task-1785524605-ea55` is routed now.** Its `Blocked by: task-1785517907-a5ec` (5b) has been
  discharged since 5b closed; the `[blocked]` rendering some views still show is the stale
  blocked-by list, not a real block — verified on the record, status `open`, description intact.
  It is the wave's last row and it carries the DECLARED BOUND 5a shipped: 5a's claim (*every `$name`
  a dashboard interpolates is declared in its own `templating.list`*) stays TRUE when the PVE
  dashboard's `templating.list` is EMPTIED and its thirteen `$guest` rewritten to the literal
  `lxc/110`, because the anti-vacuity floor sums `checked` over the WHOLE inventory and one
  declared-and-used variable anywhere satisfies it. That mutation deletes Step 4's own Test
  Requirement — the CT 110 / CT 111 drop-down — and today's guard is GREEN over it.
- **THE SIX CAME BACK READY, AND THE ANSWER WAS WRITTEN DOWN BEFORE THEY DID.** Closing 5c
  discharged the last of their `5a/5b/5c` blockers, so `ralph tools task ready` now shows SEVEN
  agent-side rows, not one: 5d plus `580a`, `fbde`, `adc5`, `b939`, `1b02`, `aca4`. That is the
  homeless-ready-task condition that caused this step to be cut in the first place, and the prior
  Planner pre-committed to its answer in this very file: *"If 5d is still open at that moment, it is
  the current step's own work and the six defer again on the same reasoning — a Planner who finds
  them ready should say so, not route them by accident."* **5d is still open. They defer again.**
  See DEC-132 below for what was re-measured before accepting that, and for the one input the
  re-pricing is still waiting on.
- **Nothing re-cut, nothing created, nothing closed.** No new task, no blocker rewritten, no
  deferral deleted. `task-1785533369-cd0e` (Family C) is still correctly blocked by 5d, and 5b's
  filed P3 `task-1785534580-9df3` likewise — both stay out of the ready set on their own blockers.

_(Superseded — kept for the chain. The `queue.advance` that closed 5b:)_
**UPDATED 2026-07-31 (Planner, `queue.advance` after 5b closed). Two of four are closed and the wave
is NOT exhausted — 5c is what this `queue.advance` routes, 5d is the row after it.**

- **5b `task-1785517907-a5ec` CLOSED** — the only row in this step to PASS its first review. Guard
  `39551b62` → `df94b58c` (docstring-only, proven by an AST diff with every docstring emptied,
  `logs/finalizer-step05b-citation.py` 16/16), **PASS 20/20**, gate **36/36 rc=0**, HEAD still
  `7e9c426`. The Critic swept all **59** delivered carriers one at a time — every one RED with the
  new row named as the speaker, no fail-open at any position — plus the inheritance seam a
  per-carrier battery cannot reach. The Finalizer corrected the round's one citation defect at its
  SOURCE rather than only where it was quoted (DEC-119) and **re-ran the calibration against real
  `grafana/grafana:13.1.0`** rather than hand-editing a recorded `.log`: 10/10, `diff` old-vs-new =
  exactly one line, every measured value re-measured identical.
- **5c is routed now, and the order the prior Planner wrote down is held.** `task-1785441840-e8eb`,
  `scripts/test_traefik_config_shape.py` — `test_tunnel_web_routers_present` asks each `<svc>-web`
  twin four clauses and asks NONE of them WHICH HOST it answers for. It is the only one of the nine
  with a **measured live consequence** (dashboard web twin repointed at the one public host →
  `plex.<domain>:80` answers 403 where the delivered tree answers 301, the WAN HTTP→HTTPS upgrade
  dead, and `traefik.<domain>:80` answers 404, guard PASS 41/41 throughout), and it has been ready
  and unrouted since 2026-07-30, banked twice. Its S1 bound (`plex-web.service` → `api@internal`,
  latent only because the pinned redirect still 301s) is in scope on the same battery.
- **Nothing in the Step 5 pricing changed and nothing was re-cut.** 5b's close produced one new
  finding (`task-1785534580-9df3`, the `.j2` truth source read raw — P3, already blocked by 5d) and
  unblocked one filed bound (`task-1785533369-cd0e`), which is deferred behind the wave by DEC-121
  below rather than routed. Six deferrals plus these two remain open; 1b/2b/3b/4d are operator gates.
- **A NOTE THE NEXT BUILDER SHOULD READ BEFORE IT COSTS A REVIEW ROUND** (`mem-1785533512-8085`):
  5c's guard is a DIFFERENT file, but the same trap applies — `scripts/test_traefik_config_shape.py`
  prints its own count (`PASS: 41/41` in the evidence on the task), and prior harnesses in `logs/`
  pin that number as a string. Grep for it before handing off, and prove the drop with a recheck
  harness rather than editing another hat's evidence.

_(Superseded — kept for the chain. The `queue.advance` that closed 5a:)_
**5a is CLOSED and the wave is NOT exhausted — it is now FOUR, and 5b is what that `queue.advance`
routed.**

- **5a `task-1785497167-e413` CLOSED** after 8 review rounds. The round-8 `review.passed` carried
  one defect (Fact 1's exemplar quoting `$guest$$$$$ct`'s measurements under `$guest$$$ct`) and
  DEC-110's written pre-commitment — *"either repair ends this row, and the Finalizer should treat
  the second as terminating"* — routed it to the Finalizer, which corrected it in-hat and proved it
  docstring-only rather than arguing it (`logs/finalizer-step05a-r8-exemplar.py` **14/14**: the AST
  with every docstring emptied identical before/after, with the anti-vacuity row that the trees
  WITH docstrings differ). Guard `b2684f33` → `5696b01b`, gate **36/36 rc=0**, guard **PASS 19/19**,
  3 dashboards + `tasks/main.yml` byte-identical, HEAD still `7e9c426`.
- **The step's Demo is RUN, not promised** — `logs/finalizer-step05a-demo.py` **9/9**: F7b (rename
  `guest` → `guestt`) is RED where the Step 4b Finalizer scored it GREEN 13/13, and the control that
  locates it holds (rename the declaration AND all 13 uses → GREEN again).
- **5d added: `task-1785524605-ea55`.** It was routed OUT of 5a by DEC-104 rather than smuggled into
  it, and has been ready and belonging to no step since 2026-07-31 — the exact condition that caused
  Step 5 to be cut. It is Step 5 work by construction (green guard, PVE drop-down gone), and 5a
  shipped a DECLARED BOUND naming it as carrier, so leaving it homeless leaves the bound uncarried.
  `ralph tools task ensure --blocked-by task-1785517907-a5ec` applied — blocked by 5b for the same
  reason 5b was blocked by 5a: both rows live in `scripts/test_grafana_provisioning_shape.py`.
  Verified after: description intact, and `ralph tools task ready` shows the agent-side ready set as
  exactly {5b `a5ec`, 5c `e8eb`} — 4d is the operator's and is not routed to a Builder.
- **Order held rather than re-cut.** 5c is the only row with a measured live consequence and there
  was a case for jumping it ahead, but nothing new arrived to justify re-pricing an order the prior
  Planner wrote down: 5b is ONE comparison in the file 5a just left, and 5c is a different file
  (`test_traefik_config_shape.py`) that is not made cheaper or dearer by waiting one task. Routing
  5b now, 5c next, 5d last.

**5a's headline number was STALE and the Planner re-measured it before routing.** The task said the
guard contains `templating` zero times; at guard `a3b1595e` it is NINE — round 11's
`_dashboard_variable_queries` enumerates `templating.list[]` to read each variable's own query as
PromQL. That answers *is this variable's query readable*, not *is every interpolated `$name`
declared*: `label_values` is still zero, no code compares an interpolated spelling to a declared
name, F7/F7b are still GREEN. Correction appended to the task and to `plan.md`, with its two
consequences — reuse the walk that already exists rather than writing a second one (DEC-085), and
the tree is now THREE dashboards, so 4c's `templating.list: []` composite is the live anti-vacuity
case AC (c) demands rather than a hypothetical one.

_(Superseded — kept for the chain. Step 4's framing when it was current:)_
**Step 4 — Import and Configure Grafana Dashboards. Split at the LIVE line, not the secret line
(DEC-068).** Step 4 needs no secret at all, and `plan.md`'s checklist said it therefore "does not
split". Half right. Steps 1–3 did not split at the secret either — **1a/1b split with no secret in
it**; what they split at was the LIVE line, the point where the evidence stops being a file in the
tree and becomes a query against a running stack. Step 4's acceptance is *open Grafana and see
panels populate*. That is a browser against a live host, so it splits the same way.

Wave materialized 2026-07-30: **4a `task-1785442414-452f` (READY — the only agent-side task routed),
4b `task-1785442438-e959`, 4c `task-1785442474-5022`** (both blocked by 4a), **4d
`task-1785442499-1851`** (OPERATOR, blocked by 4a+4b+4c so it never enters an agent's ready set).

**As of 2026-07-31 both 4a and 4b are CLOSED and the wave is NOT exhausted: 4c is the one agent-side
task left in it, and it is what this `queue.advance` routes.** 4d stays blocked behind it.

**4a IS A REPAIR, NOT A SCAFFOLD, AND THAT IS WHY IT GOES FIRST.** `plan.md` Step 4 said "no
datasource configuration changes needed" and "no additional Grafana configuration is needed". Both
are false, and the two defects are the SAME CLASS as the `0640` `prometheus.yml` that Step 2a
repaired — a config the container's uid cannot read:
- **the modes** — `tasks/main.yml:94-102` creates the three grafana dirs at `0750` root and
  `:133-155` writes `datasource.yml` / `dashboards.yml` / `homelab.json` at `0640` root:root, while
  `compose.yml.j2:128-138` declares no `user:`, so `grafana/grafana:13.1.0` runs as uid 472 against
  two `:ro` mounts;
- **the uid** — the datasource is provisioned with a NAME and no `uid:`, so Grafana generates one,
  and every panel and target in `grafana-homelab-dashboard.json` references `uid: "Prometheus"`.

Neither is provable offline. 4a is told to source both claims, to pin what it cannot verify to the
repo's own measured evidence (the prometheus `0644` comment records this exact failure mode read off
the live host), and to FLIP the fix if a measurement contradicts it — a guard that forbids the real
answer is the failure this repo has already hit once.

**4c IS NOT THE PLAN'S "OPTIONAL" ITEM ANY MORE.** The Demo asks for "the Traefik dashboard showing
request latency for the `plex@file` service" and no such dashboard exists — the only dashboard in
the repo is two node-exporter panels. Step 1's whole deliverable, the histogram ladder at
`traefik.yml.j2:91-`, is read by nothing. The composite is its carrier.

**WHAT NO GUARD IN THIS STEP CAN PROVE.** The only `pve_*` / `plex_*` series this repo has pinned
are `pve_up{id="lxc/110"}`, `plex_media_count` and `plex_sessions_count{state="playing"}` — the
acceptance lines of gates 2b and 3b. Every other series a panel names is a claim about an exporter
no agent here can query. 4b and 4c must source each name or mark it unverified in the delivery
comment; 4d is told an empty panel is a finding to route back, with the observed series name, not a
nuisance. Green means the JSON parses, the uid resolves, the delivery exists, the mode is readable.

`task-1785441840-e8eb` (P2, the `<svc>-web` twins' unasked `rule` clause, banked by the round-12
Critic with its rows attached) is agent-side, open, and NOT part of this wave. It is a banked review
finding, not a step; it stays available and is routed after Step 4's agent-side wave closes.

**Four operator gates are now open at once — 1b, 2b, 3b, 4d — and ONE `just play` is the deploy half
of all four.** They do not hold this wave, for the reason DEC-036 established and DEC-055 restated:
an operator gate is not agent work, and treating it as a wave that must close first is what parks
the loop on a human.

_(Superseded — kept for the chain. Step 3's framing when it was current:)_
**Step 3 — Deploy Plex Media Server Exporter, split at the secret line (DEC-055).** Step 3a
(repo-side wiring + shape guard, `task-1785370559-2a76`) is **CLOSED 2026-07-30 (Finalizer, after
12 review rounds)**. Step 3b (`task-1785370581-de17`) is an operator gate that 3a's close has now
UNBLOCKED — it is open and only David can close it.

**No agent-side work remains in Steps 1, 2 or 3.** Their three open tasks are all operator gates.
The next agent-side wave is **Step 4 (Grafana dashboards)**, which has no runtime tasks yet —
Planner owns creating them. `task-1785441840-e8eb` (P2, the `<svc>-web` twins' unasked `rule`
clause, banked by the round-12 Critic with its rows attached) is agent-side and still open.

**Steps 1 and 2 have no agent-side work left, and they are not "the current step" any more.** Step
1a and Step 2a are both CLOSED. What remains of both — `task-1785290391-b51a` (1b) and
`task-1785324247-3934` (2b) — are OPERATOR-ONLY gates that only David can close, their shared 2a
blocker is discharged, and **one `just play` satisfies both**. They stay open beside Step 3's wave
rather than holding it: 3a touches `defaults/main.yml`, `env.j2`, `compose.yml.j2`,
`prometheus.yml.j2` and the guard, and neither gate reads any of those as evidence. This is the same
reading of the one-wave-at-a-time contract that DEC-036 established when Step 2's wave was
materialized beside the still-open 1b — an *operator* gate is not agent work, and treating it as a
wave that must close first is what parks the loop on a human (DEC-055).

_(Superseded — kept for the chain. Step 2's framing when it was current:)_
**Step 2 — Create Proxmox API User and Deploy PVE Exporter, split at the secret line (DEC-036).**
Step 2a (repo-side wiring + shape guard) is READY and is where the Builder works. Step 2b (mint the
token, vault it, `just play`, confirm live) is an operator gate, blocked by 2a so it cannot surface
as a bare checkbox.

**Step 1 stays open alongside it.** Step 1a (repo change + guard) is CLOSED; Step 1b (operator
deploy + live confirmation) is still open and still operator-only. 1b does **not** block 2a.

**CHANGED 2026-07-29 (review round 3, DEC-039): 1b is now `--blocked-by` 2a.** Not because 2a's
pve-exporter work is needed for the buckets, but because 1b's evidence is a query against a running
Prometheus and **Prometheus has been crash-looping in production since 2026-07-15** on a 0640 config
its `nobody` user cannot read (RestartCount 20801, read off the host). 2a's `mode: "0644"` is the
repair. Running `just play` before 2a is in the tree restarts straight back into the crash loop, so
1b would fail for a reason that has nothing to do with Traefik. Both gates still share one
`just play` once 2a lands.

Tune the existing `metrics.prometheus` block in
`ansible/roles/docker_host/templates/traefik.yml.j2` with custom histogram buckets, guarded by a
non-vacuous check in the existing `scripts/test_traefik_config_shape.py`, then deployed and
confirmed in live Prometheus.

**CORRECTED 2026-07-29 (Finalizer).** The values first written here — `[0.1, 0.3, 1.2, 5.0]` —
are traefik:v3.7.5's OWN defaults, so shipping them was a runtime no-op and the demo built on them
was unfalsifiable. That was the round-2 rejection. The SHIPPED ladder is:

    0.00025, 0.0005, 0.001, 0.0025, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 1.0, 5.0, 30.0, +Inf

Demo for this step: `traefik_entrypoint_request_duration_seconds_bucket{entrypoint="websecure"}`
returns 14 `le` labels including **`le="0.00025"`**, which cannot exist under Traefik's
0.1/0.3/1.2/5.0 default. That single label is the falsifier. Seeing exactly
0.1 / 0.3 / 1.2 / 5.0 / +Inf and nothing else means the restart did NOT take.

These boundaries measure SERVER-SIDE handler duration — not TCP connect, the TLS handshake, or
client transit — so they must not be compared against browser TTFB numbers.

## Active Wave

**STEP 10 — ONE ROW, ROUTED 2026-08-02 (Planner, `queue.advance` after `a15c` closed). DEC-205.**

| Task key | ID | State |
|----------|----|-------|
| `code-assist:plex-monitoring:guard:unreadable-provisioned-caller-count` | `task-1785634257-80de` | **10a — READY, ROUTED by this activation** (P3). `scripts/test_grafana_provisioning_shape.py`, `_unreadable`'s docstring at **:1170** (the "AND THE CLAUSE IS EARNED BY THE CALLER, NOT BY THE BYTE" paragraph): "`provisioned=` is passed by the **five** readers that iterate `_delivered_dashboards`, **and by nothing else**". **Re-measured at the Planner's own hands on the delivered guard `56bba79ef94e`: 7 `_unreadable(...)` call sites, SIX pass `provisioned=`** (:2151 `_delivered_dashboard_documents`, :4501, :5339, :5635, :6022, :6443) **and one passes neither** (:4809, correct). The filer's line numbers moved with a15c r4's comment lines (:5621→:5635, :6008→:6022, :6429→:6443); the SET did not. **Re-`ensure`d at this cut** to correct acceptance (d) — see below |

**"AND BY NOTHING ELSE" IS THE PARAGRAPH'S ENTIRE POINT, WHICH IS WHY THIS IS A ROW AND NOT A TYPO.**
It is the blast-radius claim that licenses the conclusion the reader is asked to draw — that a reader
added later inherits the byte and NOT a claim it has not earned. A reader who audits it counts six
and cannot tell whether the sixth caller is the very defect the sentence warns about or the sentence
is merely stale. That is the same cost this thread has paid repeatedly for a sentence whose scope
outran its measurement.

**THE UNCOUNTED SIXTH IS A HELPER, AND THE HELPER/ROW DISTINCTION *IS* THE DISCREPANCY.**
`_delivered_dashboard_documents` is not a test row; the count was very likely taken over ROWS and the
sentence written over CALLERS. Acceptance (b) therefore forbids a bare 5→6 edit: if the sentence
means test rows it must say so explicitly.

**ACCEPTANCE (d) WAS CORRECTED AT THIS CUT AND THE ROW RE-`ensure`d.** It named
`logs/builder-a15c-r2-pre-guard.py` PART D. That harness is **DEAD at the delivered sha**
(`AssertionError: anchor not unique/present` — a15c round 3 rewrote the comment block its second pair
quotes, `mem-1785634963-bf38`), **it never had a PART D**, and
`logs/builder-a15c-r2-collateral.py` — where the docstring normalisation actually lived — dies with
it because it *imports* that reverser. The living reverser is **`logs/builder-a15c-r4-pre-guard.py`**
(green here: rebuilds `821b687f6267`, chains `8cb7299e4568` / `54cec7fc4cea` / `9c08e2b54dc2`, real
path unmoved). Rounds 3 and 4 used a RAW `ast.dump` with normalisation disabled because they were
comment-only; **a docstring round cannot** — `ast.dump` fails for the right reason and tells you
nothing (`mem-1785633523-cbc8`). **Build the normalised oracle on r4's reverser: placeholder every
Module/FunctionDef/ClassDef docstring, require the dumps IDENTICAL, then admit the differing
docstring BY NAME as the round's intended change.**

**DO NOT TOUCH THE NEIGHBOURING NUMBER.** The same docstring carries "11 rows keyed on a DELIVERY
printed it against the 1 that had earned it" (~:1205). That is a **different count over a different
measured run** and must not be edited to agree with this one.

**BLAST RADIUS, ALREADY MEASURED.** `logs/red-579d-r4-critic-recheck.py` (line 104) is the only other
file in `logs/` or `scripts/` quoting the sentence, and it is **already RED at the delivered tree
before this row touches anything** — SCORE 9/16, `R14-unique MISS ... 0x`, reconstruction `76eea07b`
vs reviewed `e102f69b`. **Never edit another hat's harness**; if an assertion falls, DISCLOSE it and
attribute it by counting its anchor at **BOTH** texts rather than reproducing its failure at one
(`mem-1785630967-6fdd`).

**One prohibition carried forward so it is not re-derived:** do NOT add a top-level `id` rule to
either chain. A stale numeric `id`, `panels` as a string and 600 nested arrays are all SERVED by the
pinned engine (`mem-1785624794-9c63`).

**Why this row and not the other thirteen.** It is the only ready row that is a FALSE sentence in
shipped source rather than a disclosed gap or a standing deferral, and it is the third of the three
places `mem-1785632642-168d` names as the guard's contract. The full pricing — including why P2
`fc70` does not lead despite being the silent one, and why the freshly-banked `d2fd` is the declared
successor rather than this wave — is in `plan.md` Step 10 and in the Current Step section above.

---

### The Step 9 wave, kept for the chain

**STEP 9 — ONE ROW, ROUTED 2026-08-02 (Planner, `queue.advance` after `ba6c` closed). DEC-200.
CLOSED 2026-08-02 at `56bba79ef94e` after 4 review rounds and an in-hat Finalizer repair.**

| Task key | ID | State |
|----------|----|-------|
| `code-assist:plex-monitoring:guard:unreadable-chain-uid-halves` | `task-1785624345-a15c` | **9a — READY, ROUTED by this activation** (P3). `scripts/test_grafana_provisioning_shape.py` `_unreadable`, the save-layer chain at **:1413-1421**: `(_grafana_short_uid_defect(uid) if isinstance(uid, str) else None, GRAFANA_LOG_SAVE)` is asked **2nd of four**, ahead of the deferred number (:1417) and the tags (:1419). That fence is HALF the line the repaired spelling splits on at **:5362** (`isinstance(uid, str) and _grafana_stored_uid(uid) is not None`), so the chain gets both non-refusing members wrong in OPPOSITE directions: the TRIM-CLASS member is MIS-ORDERED and the NON-STRING member is DROPPED. **Re-measured at the Planner's own hands on the delivered guard `9c08e2b54dc2`: `logs/critic-fb36-r2-unreadable-sibling.py` PASS 6/6** (A-trim-vs-number, A-trim-vs-tag, B-nonstring-dropped, B-repaired-row-disagrees, B-nonstring-tag-is-right-by-accident, Z-guard) — `ba6c` did not disturb this chain and the defect is live |

**THE CARRIERS ARE A SEPARATE DELIVERED-FILE SET AND A SEPARATE CONTAINER RUN, and that is why it
was filed rather than batched into `fb36`.** This chain runs only for a delivered dashboard `_read`
cannot decode as UTF-8 whose bad byte sits at a **SAVED** position (inside a string). The file is RED
either way — it is unreadable — so what is wrong is the REASON given to the operator, not the
polarity of the gate. The engine half of every claim is already measured on the pinned
`grafana/grafana:13.1.0` (calibration `step05d-rework-r9-uid-charset` C2 enumerates the whole
non-string class as SAVED under a generated uid; `logs/critic-fb36-r2-nonrefusal-generalizes.py`
PART A drove four more types), so the row's ORDER cannot go stale.

**THE DROP IS INVISIBLE UNLESS THE CARRIER IS THE MEMBER ALONE.** A non-string uid WITH a 51-byte tag
names `tag`, which is the engine's own answer — right by accident. Only the ALONE carrier exposes
that the chain names no defect at all and falls through to its `SAVES this file with those bytes
replaced by U+FFFD` clause. Acceptance (a) is written on exactly that.

**THE REPAIR IS AN ORDERING AND NEVER A DELETION** (`mem: flip a guard's polarity, never delete it`):
ask the REFUSING half where the engine asks it and the two NON-refusing members LAST, after the tag,
so the chain stays RED for a dashboard saved at an address nothing in this repo can name without
letting that outrank a rule the engine stopped on. Diffing the two calls is the cheapest oracle for
`done` (`mem-1785622988-cf79`). **Never edit another hat's harness** — if an assertion falls,
DISCLOSE it and attribute it by counting its anchor at **BOTH** texts rather than reproducing its
failure at one (`mem-1785630967-6fdd`).

**One prohibition carried forward so it is not re-derived:** do NOT add a top-level `id` rule to
either chain. A stale numeric `id`, `panels` as a string and 600 nested arrays are all SERVED by the
pinned engine (`mem-1785624794-9c63`).

**Why this row and not the other twelve.** Its only remaining deferral was that it serialised behind
`ba6c` in the same file, and `ba6c` is closed. The full pricing — including why P2 `fc70` does not
lead despite being the silent one — is in `plan.md` Step 9 and in the Current Step section above.

---

### The Step 8 wave, kept for the chain

**STEP 8 — ONE ROW, ROUTED 2026-08-01 (Planner, `queue.advance` after `fb36` closed). DEC-198.
CLOSED 2026-08-02 at `9c08e2b54dc2` after 1 review round.**

| Task key | ID | State |
|----------|----|-------|
| `code-assist:plex-monitoring:guard:presence-gate-precedes-every-engine-rule` | `task-1785622294-ba6c` | **8a — BUILT 2026-08-01, `review.ready`** (was READY, ROUTED by the Step 8 activation; P2). Guard `a70d851ce802` → `9c08e2b54dc2`; the census ran BEFORE the edit and its answer is in the Verification Notes. **The four sibling assertions FAIL and are disclosed there, not patched over.** The presence gate above `test_delivered_dashboards_parse_as_dashboards`' save-layer chain asks a guard-policy uid requirement BEFORE every engine rule, and the engine never refuses an empty or absent uid at all — it generates a uuid and saves. Measured on the pinned `grafana/grafana:13.1.0` in `fb36`'s own run (`logs/red-fb36.py` PART D, both texts): `uid: ""` and NO `uid` key, each with a 5001-character title, are `Dashboard title cannot contain more than 5000 characters` — the TITLE — while the row answers `no top-level uid/title`. **THIRD CARRIER, not in the row's description: a top-level JSON ARRAY** → `Dashboard title cannot be empty` at the engine, `no top-level uid/title` at the row (`mem-1785624803-6b47`, `logs/finalizer-fb36-r2-unmodelled-refusals.py`) |

**THE FIRST MOVE IS A CENSUS, NOT AN EDIT, and the row says so.** Deleting the sentence costs FOUR
live assertions in three other hats' harnesses — `logs/red-step05d-rework-r10.py` S1/S2,
`logs/red-step05d-rework-r11.py` S6, `logs/critic-step05d-r9-title-provisionability.py` D2 — each of
which greps the string. Moving the clause BELOW the chain makes it unreachable instead, because
`_grafana_short_uid_defect` already answers its whole class (`""` → the trim class, absent → not a
string), and a dead clause is worse than a wrong one because nothing measures it. So the question to
settle first is whether the row keeps a policy sentence at all and, if it does, where it can sit so
it is BOTH reachable AND after every engine rule. **`logs/builder-fb36-collateral.py` PART C already
runs all four carriers over two guard texts and prints the whole line** — the census has a runner
that does not need writing. **Never edit another hat's harness:** if an assertion falls, DISCLOSE and
attribute it (acceptance (b)).

**One prohibition carried in from the `fb36` Finalizer, so it is not re-derived:** do NOT add a
top-level `id` rule to this chain. A stale numeric `id`, `panels` as a string and 600 nested arrays
are all SERVED by the pinned engine (`mem-1785624794-9c63`) — an `id` rule would be a refusal the
delivery path does not make.

**Why this row and not the other thirteen.** Its only deferral was DEC-195, made relative to
`fb36`'s atomicity, and `fb36` is closed. Family-B (`b939`, `adc5`, `1b02`, `580a`, `aca4`) keeps
DEC-132 and its named input has still not arrived; `cd0e`, `9df3`, `bad2`, `8144` keep DEC-153's
table; `a15c` is the same class and the declared successor but P3, with carriers needing a separate
delivered-file set and container run; `7407` is one priority lower again; `0956` is silent in
character but unmeasured by anyone and P3 — a research row before a build row; `fc70` keeps its OWN
standing clause (a blast-radius enumeration of every row the inventory repair moves), of which only
the "serialises behind `fb36`" half expired. Full pricing in `plan.md` Step 8.

---

### The Step 7 wave, kept for the chain

**STEP 7 — ONE ROW, ROUTED 2026-08-01 (Planner, `queue.advance` after `9ffc` closed). DEC-194.
CLOSED at `a70d851ce802` after 2 review rounds.**

| Task key | ID | State |
|----------|----|-------|
| `code-assist:plex-monitoring:guard:readable-row-rule-order` | `task-1785594766-fb36` | **7a — READY, ROUTED by this activation** (P2). `test_delivered_dashboards_parse_as_dashboards` asks its rules in the wrong order in TWO directions, measured at **0/2** on WHOLE gate runs over a READABLE delivered dashboard (`logs/critic-579d-r8-uidlen-and-readable-row.py` PART D): illegal uid + blank-after-trim title → the row names the UID, the engine names the TITLE; a number past the IEEE double range + the same title → the row names the NUMBER (the parse raises before any field is read), the engine still names the TITLE. **The order to carry is written down and MUST NOT be re-derived** (`mem-1785592369-90dd` and the constant blocks above each predicate): parse/bare-token (LOAD) → load-layer `MustString()` title and top-level shape (LOAD) → save-time title trim + 5000-byte bound → uid (charset then length, on the string surviving `GRAFANA_SHORT_UID_TRIM`) → number past the IEEE double range → tag 50-byte bound. **The row owes ONE thing beyond the usual RED-first: the expected field must be scored against the pinned `grafana/grafana:13.1.0`'s OWN container-log line for each combined pair, not against the order in the source** — `mem-1785593456-9d15`, a claim about what the engine names needs a carrier at the engine |

**The one harness this costs, priced here and not discovered mid-build.** DEC-176 recorded that
reordering this or-chain moves the FIRST LINE of the row, which is the open anchor `R1` of
`logs/red-step05d-rework-r10-critic-recheck.py` cuts on. That anchor **already cannot reach its
target** — its reconstruction lands on `905f46d8` against a declared `10fd3cdb`, because seven
rounds of `579d` changed the file outside its three anchors. So the true cost is one stale anchor
line, not a lost fact. Say so in the increment; do not silently break it. The reconstruction chain
itself must still close (`logs/red-579d-r9-recheck-chain.py` or its successor, 10/10).

**Why this row and not the other twelve.** `fb36` is the only open P2 in this namespace with no
standing deferral: Family-B (`b939`, `adc5`, `1b02`, `580a`, `aca4`) keeps DEC-132 and its named
input has still not arrived; `cd0e`, `9df3`, `bad2`, `8144` keep DEC-153's table; `7407` is the same
class one priority lower and serialises behind `fb36` in the same file; `0956` is silent in
character but is **unmeasured by anyone** — its own description says the four-dashboard,
three-spelling tree has never been delivered — and is P3; `fc70` was filed this turn and its first
move is a blast-radius census, not one atomic increment. Full pricing in `plan.md` Step 7.

---

### The Step 6 wave, kept for the chain

**EXHAUSTED (2026-08-01).** `task-1785601096-9ffc` CLOSED by the Finalizer after 13 review rounds at
guard `9c61b6112215` — guard standalone **PASS 22/22** (up 21 → 22), `just test` GATE PASS 36/36
rc=0, `red-9ffc` 73/73, r11 13/13, r12 19/19, r13 20/20,
`critic-9ffc-r13-name-collision-classes` 12/12, all re-run at the Finalizer's own hands rather than
read off either hat's log. The repair signature was checked BY ROW, not by total: the review's own
detector `critic-9ffc-r12-group-member-identity` re-run UNEDITED is 8/12 with exactly four MISS (the
sha pin plus the three finding rows) and every control OK. HEAD stays `7e9c426`, no commit, no
`just play`, no live call, nothing written under `ansible/` or `scripts/`, gates 1b/2b/3b/4d
untouched. **The adversarial pass went at the round's DEFERRAL rather than its finding** — the row
backing the deferral's premise was vacuous, so the Finalizer asked ansible instead
(`logs/finalizer-9ffc-r13-h1-one-file-on-disk.py` 8/8, core 2.21.1); the deferral held, and the
measurement is now filed as `task-1785621026-fc70`.

**STEP 6 — ONE ROW, ROUTED 2026-08-01 (Planner, `queue.advance` after `579d` closed). DEC-182.**

| Task key | ID | State |
|----------|----|-------|
| `code-assist:plex-monitoring:guard:duplicate-title-provider-lockout` | `task-1785601096-9ffc` | **6a — READY, ROUTED by this activation** (P2). Two delivered dashboards with the SAME title and distinct, legal, non-trimming uids take the SAME provider-wide `has no database write permissions because of duplicates` lockout whose blast radius `test_delivered_dashboards_have_distinct_uids` already states in its own sentence — reached by a cause that row cannot see, because its key is the uid and this collision is not one. Measured twice in two containers on pinned `grafana/grafana:13.1.0` (`logs/critic-579d-r12-duplicate-title-lockout.py` 7/7, `logs/critic-579d-r12-empty-uid-same-title.py` 6/6). The engine names NO cause (no `the same UID is used more than once` line, no title message at all — three polls, three bare lockout lines), both files are still SERVED, and the whole guard PASSes 21/21 over a colliding tree with the collision row printing `problems=[]`. **The row owes ONE thing beyond the usual RED-first: the SCOPE (provider / folder / global) must be MEASURED on the pinned image, not inferred from the uid tracker's global scope** — `mem-1785593456-9d15`, a claim about a scope needs a carrier at that scope |

**Verified at the Planner's own hands rather than adopted from the review that filed it:** `grep -i
"same title|title is used|duplicate title"` over `scripts/test_grafana_provisioning_shape.py`
returns ZERO hits; `test_delivered_dashboards_have_distinct_uids` is at line 5303 and is the row
whose sentence already owns the blast radius; and the delivered tree is
`homelab-overview`/`Homelab Overview`, `plex-health`/`Plex Health`, `pve-overview`/`Proxmox VE` —
distinct on BOTH axes, so this is a latent guard hole and not a live outage.

**Deferred behind it, unchanged:** eleven rows. `fb36` and `7407` are the LOUD class (the gate is
already RED when they fire; they name the wrong field) and serialise behind `9ffc` in the same file
regardless — `fb36` is NEXT in line. The five Family-B rows keep DEC-132's reasons verbatim; `cd0e`,
`9df3`, `bad2` and `8144` keep DEC-153's table. `fbde` is no longer among them: CLOSED this turn as
the duplicate of `b939`. Full pricing in `plan.md` Step 6.

---

### The Step 5 wave, kept for the chain

**EXHAUSTED (2026-08-01, DEC-153).** The table
below is the wave as it finished. All four rows are closed; every row under it is DEFERRED with its
reason, and the deferrals are deliberately left **visibly ready** rather than re-blocked — that
visibility is the signal that makes the next Planner price them, and re-blocking would hide it
behind bookkeeping (the argument DEC-132 made and this close keeps).

**Priced for the first time by this close (the three filed after the wave was cut, plus one carrier
this close created). Full reasoning in `plan.md` Step 5, "THE CLOSE":**

| Task key | ID | Verdict |
|----------|----|---------|
| `code-assist:plex-monitoring:guard:read-text-raw-invalid-utf8` | `task-1785571102-579d` | **DEFERRED** (P2). LOUD: the gate ALREADY refuses the file (rc=1, no summary) — the row buys a better MESSAGE, not a repair, and its own AC says so ("the failure must be a sentence, not a stack trace"). Trigger is a raw invalid UTF-8 byte nothing in the tree writes. DEC-152 filed it "for the Planner to route"; priced instead. Kept on record for its one unique property: when it fires it takes every other row's verdict with it |
| `code-assist:plex-monitoring:guard:datasource-truth-source-unrendered` | `task-1785534580-9df3` | **DEFERRED** (P3). Family A genus — the class this loop has closed five times elsewhere — but C2 measured no Jinja at all in the delivered `datasources:` block, so raw == rendered today (A1) and the wrong direction is a false refusal |
| `code-assist:plex-monitoring:guard:pve-panels-follow-a-second-variable` | `task-1785553255-bad2` | **DEFERRED** (P3). Measured GREEN so the hole is real, but the route in is a second `custom` entry plus twelve repointed panels — DEC-121's "three deliberate contortions" shape — and the fix needs a value-list reader the file lacks. Bound declared in the row's docstring |
| `code-assist:plex-monitoring:guard:traefik-whitespace-class-sweep` | `task-1785571952-8144` | **FILED BY THIS CLOSE, then DEFERRED** (P3). 5c's round 5 declared the ~167-site residual in writing and it had **no carrier task** — and this repo's own rule is that a defect declared and never scheduled "is not banked, it is shipped". Deferred because a 167-site sweep is not one atomic task; its first move is a census, and `finalizer-step05c-f0-loudness.py` 12/12 says most such seams are loud |

**The wave as it finished.** Three tasks as cut, grown to four; six deferred behind them. The
Step 1–4 table below it is kept for the chain.

| Task key | ID | State |
|----------|----|-------|
| `code-assist:plex-monitoring:guard:dashboard-template-vars-declared` | `task-1785497167-e413` | **5a — CLOSED** 2026-07-31 (Finalizer, after 8 review rounds; corrected in-hat per DEC-110's pre-commitment, proven docstring-only by AST diff 14/14, and the plan's Demo run end to end 9/9). Guard `5696b01b` PASS 19/19, gate 36/36 rc=0 |
| `code-assist:plex-monitoring:guard:datasource-type-exemption-unvalidated` | `task-1785517907-a5ec` | **5b — CLOSED** 2026-07-31 (Finalizer, after 1 review round — PASSED first time, the only row in this step that did). Guard `df94b58c` **PASS 20/20**, gate 36/36 rc=0. DEC-118's citation defect corrected in-hat AT THE SOURCE (DEC-119) with the calibration RE-RUN against real `grafana/grafana:13.1.0`, 10/10, diff = exactly one line |
| `code-assist:plex-monitoring:guard:web-twin-rule-clause` | `task-1785441840-e8eb` | **5c — CLOSED** 2026-08-01 (Finalizer, after 5 rework rounds — r2 operators, r3 arity, r4 the whitespace class on `rule`, r5 the same class on `service` at all four sites plus the shared reader's seven other keys). Guard `53338616` **PASS 42/42**, gate 36/36 rc=0. Finalizer swept the GROWTH direction no round reached (10/10, `examined` 7 → 8) and re-measured the review's F0 loudness ground (12/12, go-yaml load error 8/8) |
| `code-assist:plex-monitoring:guard:pve-dashboard-declares-its-drop-down` | `task-1785524605-ea55` | **5d — CLOSED** 2026-08-01 (Finalizer, after **11 rework rounds**, every one of them the same class one field over: r2 `regex`/`hide`, r3 `includeAll`/`multi`, r4 `allValue`/`repeat`, r5 the expanded row, r6 the gridPos sort, r7 the axis test, r8 the parse layer, r9 the save layer, r10 the `title` half, r11 the two `.encode(` calls). Guard `e8d62f31` **PASS 21/21**, gate 36/36 rc=0, HEAD `7e9c426`, artifacts `a8a8c24e`/`1e8f3617` untouched. The Finalizer's own 25/25 went where no round went — the engine's **STORE** side, not its REFUSE side: the stored `templating` entry keeps every key the row pins, all 13 `$guest` references survive the save layer, and **the engine SAVES all three mutations the row exists to refuse**, so the row's premise is measured rather than asserted. The review's one finding is filed, not reworked (`task-1785571102-579d`, DEC-152) |
| `code-assist:plex-monitoring:guard:builtin-datasource-type-unpinned` | `task-1785533369-cd0e` | **DEFERRED** behind the rest of the wave 2026-07-31 (this `queue.advance`) — `--blocked-by` 5c + 5d. Filed by the 5b Builder as the DECLARED BOUND's carrier (DEC-116); P3 by its own filer's pricing. See DEC-121 below |
| `code-assist:plex-monitoring:guard:promql-unbalanced-quote-invisible-call` | `task-1785509072-b939` | **DEFERRED** behind the wave. CANONICAL for the unterminated-literal class; fbde merged into it 2026-07-31. Harm is LOUD (lex error → the panel errors) |
| `code-assist:plex-monitoring:guard:promql-unterminated-string` | `task-1785504947-fbde` | **DEFERRED**, re-titled **SUPERSEDED by b939** — same mechanism, same exemplar, filed twice. Its unique contribution (the `plex_media_count{$filter}` accept-side price) is appended to b939 |
| `code-assist:plex-monitoring:guard:plex-media-same-kind-per-call` | `task-1785506726-adc5` | **DEFERRED**. Carries a MEASURED false refusal of a correct panel (D5), and its own D1 is "not unambiguously wrong" |
| `code-assist:plex-monitoring:guard:traefik-name-regex-invisible` | `task-1785516964-1b02` | **DEFERRED**. "Nobody types this by accident, which is why it is filed rather than coded" — its own words |
| `code-assist:plex-monitoring:guard:owner-name-uid-mapping` | `task-1785457578-580a` | **DEFERRED**. Compound precondition nothing in the tree meets (`owner: root` everywhere); both runtime outcomes loud |
| `code-assist:plex-monitoring:battery:r2-d10-stale-expectation` | `task-1785517288-aca4` | **DEFERRED** (P3). A stale expectation in an old battery, not a guard hole |

**DEC-121 — `task-1785533369-cd0e` IS DEFERRED, NOT ROUTED, AND NOT LEFT HOMELESS (confidence 85).**
Closing 5b unblocked it and it landed in the agent-side ready set belonging to no numbered step —
the exact condition that caused Step 5 to be cut. So it was priced against this step's own bar
rather than picked up because it was ready:

- **Its filer priced it P3 and said why** — the fix is a CONSTANT TRANSCRIBED FROM GRAFANA (the three
  built-in uids are provisioned nowhere), whose failure mode is *stale on a Grafana upgrade*, in the
  LOUD direction. That is the opposite end of this step's bar, and it is the hazard this repo has
  already been rejected twice for: a guard that forbids the real answer.
- **The route in is three deliberate contortions, not a copy-paste.** The uncompared mutation needs a
  built-in uid AND a wrong declared type AND the query moved to a key no reader knows. 5b earned its
  place because its route in was ordinary (copy a panel out of a Loki dashboard, change only the
  uid); this one has no such route.
- **New information arrived AFTER it was filed and it should be re-priced with that in hand.**
  `mem-1785534624-584f`: the dashboard-JSON type for the built-ins is readable off `GET
  /api/frontend/settings`, field `meta.id`, on a booted container — so the task's own proposal to
  grep the pinned image's frontend bundle is the dear route, and its text still says the dear one.
  DEC-120 deliberately did not hand-edit the record; a Planner re-pricing it at 5c/5d's close reads
  the corrected R8 title the citation points at, plus that memory.
- **Blocked by 5c AND 5d, unlike the six.** The six's blockers were left at 5a/5b/5c to avoid churn
  on six rich records; cd0e is one record with nothing at risk, so it gets the accurate statement of
  "behind the wave". Verified after the `ensure`: description intact at 1956 chars, both blockers
  applied, and the agent-side ready set is exactly {5c `e8eb`, 5d `ea55`} — in-wave only.

**The six older deferrals are blocked by all three ORIGINAL wave tasks, so they unblock together
when 5c closes** — at which point a future Planner re-prices them with 4d's operator evidence in hand, which
is new information none of these rows currently has. Nothing was closed, failed or deleted to
achieve this. **Their blockers were deliberately NOT extended to 5d** when 5d joined the wave: six
`ensure` rewrites of rich task records to preserve a bookkeeping invariant is churn, and the
re-pricing Planner meets them at 5c's close either way. If 5d is still open at that moment, it is
the current step's own work and the six defer again on the same reasoning — a Planner who finds them
ready should say so, not route them by accident.

**DEC-132 — THE SIX ARE READY AND THEY DEFER AGAIN; 5d IS ROUTED (confidence 88). 2026-08-01, the
`queue.advance` that closed 5c.** The paragraph directly above is a pre-commitment, and this is the
moment it fires. It is honoured rather than re-derived, but three things were checked before
accepting it, because a pre-commitment discharged without looking is the same defect as no
pre-commitment at all:

- **The precondition is literally true.** 5d `task-1785524605-ea55` is `open`, unblocked, and is
  Step 5's own work by construction. So the branch the prior Planner wrote — *"if 5d is still open
  … the six defer again"* — is the one that applies. Routing any of the six now would jump the
  current step's last row to pick up work the step deliberately priced OUT of itself.
- **The one input the deferral is waiting on has NOT arrived.** The stated reason to re-price the
  six at this close was *"with 4d's operator evidence in hand, which is new information none of
  these rows has"*. `task-1785442499-1851` (4d) is still open and is OPERATOR-ONLY — nobody has
  opened a Grafana panel yet. The evidence that was supposed to make the re-pricing better than
  the original pricing does not exist, so a re-pricing today would be the SAME judgement made
  twice, not a better one. That is the substantive finding of this turn: the trigger fired, the
  input did not.
- **Nothing in the six changed under them.** No new measurement landed on any of the five reasons:
  b939 is still LOUD by its own measurement (an unterminated literal is a lex error, so the panel
  errors rather than drawing a plausible number), `fbde` is still the same finding filed twice,
  `adc5` still carries a measured FALSE REFUSAL of a correct panel (D5), `1b02` still says in its
  own text that nobody types it by accident, `580a` still needs a compound precondition the tree
  does not meet with both runtime outcomes loud, and `aca4` is still a P3 stale battery expectation
  rather than a guard hole. Four of the five remain the same PromQL scanner clause that consumed
  eleven review rounds of Step 4c.

**Their blockers are STILL not extended to 5d, and that is now a deliberate second refusal.** The
churn argument holds unchanged, and there is a stronger one: the six being visibly ready is the
signal that makes the next Planner price them. Re-blocking them would hide that signal behind
bookkeeping and buy nothing — the routing decision is made by the `tasks.ready` event, not by the
ready set. **The consequence, stated so it is not a surprise:** when 5d closes, the agent-side ready
set is the six plus whatever 5d files, with `cd0e` and `9df3` joining as 5d discharges their
blockers, and Step 5's wave is exhausted. That Planner has a genuine decision — re-price the six
with 4d's evidence if it has arrived, or record that Step 5 is exhausted and that everything
remaining is either operator-gated or deferred-with-reasons — and it should NOT read this DEC as
pre-committing that answer too. This one covers only the case where 5d is open.

---

_(Superseded — kept for the chain. Steps 1–4's wave:)_

| Task key | ID | State |
|----------|----|-------|
| `code-assist:plex-monitoring:step-01:traefik-histogram-buckets` | `task-1785290378-db09` | **CLOSED** 2026-07-29 (Finalizer, after 6 review rounds) |
| `code-assist:plex-monitoring:step-01:operator-deploy-verify-buckets` | `task-1785290391-b51a` | **BLOCKED** by 2a since 2026-07-29 (DEC-039) — **OPERATOR ONLY**, not agent-closable |
| `code-assist:plex-monitoring:step-02:pve-exporter-repo-wiring` | `task-1785324219-b403` | **CLOSED** 2026-07-30 (Finalizer, after 15 review rounds) |
| `code-assist:plex-monitoring:step-02:operator-token-deploy-verify-pve` | `task-1785324247-3934` | **READY** 2026-07-30 (2a closed → unblocked) — **OPERATOR ONLY**, not agent-closable |
| `code-assist:plex-monitoring:step-03:plex-exporter-repo-wiring` | `task-1785370559-2a76` | **CLOSED** 2026-07-30 (Finalizer, after 12 review rounds) |
| `code-assist:plex-monitoring:step-03:operator-token-deploy-verify-plex` | `task-1785370581-de17` | **READY** 2026-07-30 (3a closed → unblocked) — **OPERATOR ONLY**, not agent-closable |
| `code-assist:plex-monitoring:guard:web-twin-rule-clause` | `task-1785441840-e8eb` | **NOW 5c** — banked by the round-12 Critic 2026-07-30, homeless until the Step 5 cut gave it one |
| `code-assist:plex-monitoring:guard:owner-name-uid-mapping` | `task-1785457578-580a` | **NOW DEFERRED behind the Step 5 wave** — banked by the Step 4a Finalizer 2026-07-31 |
| `code-assist:plex-monitoring:step-04:provisioning-readability-and-datasource-uid` | `task-1785442414-452f` | **CLOSED** 2026-07-31 (Finalizer, after 3 review rounds) |
| `code-assist:plex-monitoring:guard:dashboard-template-vars-declared` | `task-1785497167-e413` | **NOW 5a, the head of the Step 5 wave** — materialized from the Step 4b Finalizer's open finding 2026-07-31 |
| `code-assist:plex-monitoring:step-04:pve-dashboard` | `task-1785442438-e959` | **CLOSED** 2026-07-31 (Finalizer, after 6 review rounds) |
| `code-assist:plex-monitoring:step-04:plex-health-dashboard` | `task-1785442474-5022` | **CLOSED** 2026-07-31 (Finalizer, after 11 review rounds) |
| `code-assist:plex-monitoring:step-04:operator-deploy-verify-dashboards` | `task-1785442499-1851` | **READY** 2026-07-31 (4a+4b+4c all closed → unblocked) — **OPERATOR ONLY**, not agent-closable, not routed to a Builder |

**Step 4's wave was materialized 2026-07-30** on the `queue.advance` that closed Step 3a. The
checklist line "needs no secret and does not split" is corrected in `plan.md` and under **Current
Step** above: no secret is right, does not split is not — the split line was always the LIVE line
(1a/1b split with no secret in it), and Step 4's acceptance is a browser against a running Grafana.
4b/4c are blocked on 4a because a dashboard added before the mode and uid repairs cannot load and
its uid reference has nothing to agree with.

**Two operator gates in this wave**, neither agent-closable; as of 2026-07-29 both are blocked by
2a (see DEC-039 above), and neither blocks the other:
`task-1785290391-b51a` (Step 1b) runs `just play` and reads live Prometheus for the bucket ladder;
`task-1785324247-3934` (Step 2b) mints the Proxmox token and reads live Prometheus for
`pve_up{id="lxc/110"}`. RObot/Telegram is unwired in this repo, so each task IS its own ask. Both
can be satisfied by a single `just play` once 2a lands. **The loop no longer parks on them** — 2a
is agent-side work that needs neither.

**2026-07-29, Planner on `queue.advance`.** Re-published `task-1785290391-b51a` as the wave's next
ready task and created NO new tasks. Step 1's wave is not exhausted, so Step 2/3/4 waves may not
exist yet (one step's wave at a time). Read the gate's corrected description end to end rather
than trusting the Finalizer's summary: it names `le="0.00025"` as the single falsifier, states the
full 14-label ladder, spells out what failure looks like, bounds a healthy hit at `le="0.25"`, and
warns that this series is server-side handler duration. It is falsifiable and executable as
written — no further edit needed. **Step 1 now advances only by an operator running `just play`;
no agent-side work remains in it.**

> ~~Steps 2 and 3 will each park the same way (they need an operator-minted `prometheus@pve` API
> token and a Plex auth token respectively), so materializing them early would only queue a second
> gate behind this one.~~ **RETRACTED 2026-07-29 (Planner, DEC-036).** This was DEC-034 and it was
> too broad. It conflated "the ready set is gated" with "the OBJECTIVE is gated". Reading `plan.md`
> end to end falsifies it: Step 2 is six items and only items 1 and 6 need a human — the `env.j2`
> reference, the compose service and the scrape job are ordinary repo edits with a shape guard, the
> exact shape Step 1a already shipped, and a secret's VALUE is separable from its variable
> REFERENCE (`env.j2` renders every secret with `| default('')`). Step 4 needs no secret at all.
> The correct move was to split each step at its secret line, not to park the objective.

**2026-07-29, Planner on `queue.advance` (task.resume after the 1b park).** Materialized the Step 2
wave split at the secret line — 2a repo-side (READY, Builder) and 2b operator (blocked by 2a, so
the ready set is no longer 100% gate and no fresh Builder can meet a bare checkbox). Did NOT touch
Step 1b, did NOT materialize Steps 3/4.

**And corrected a load-bearing error in `plan.md` Step 2 while writing the wave.** The original
item 5 prescribed `job_name: pve-exporter`, target `pve-exporter:9221` — and the original Test
Requirement was "confirm the target is `UP`". Those two together are unfalsifiable in the same way
the pre-rejection Step 1 demo was. `prometheus-pve-exporter` is a **multi-target** exporter: PVE
metrics live at `/pve?target=<node>&cluster=1&node=1`, while the default `/metrics` path serves
only the exporter's own scrape/process metrics. So a job on the default path answers `200`, the
target reads **UP**, and there are **zero `pve_*` series** — the operator would have confirmed a
runtime no-op as a success. Both halves are fixed: 2a's guard pins `metrics_path: /pve` and
`cluster: ['1']`, and 2b's falsifier is metric-level (`pve_up{id="lxc/110"}` returns a series), not
target-level. Verified against the upstream README rather than assumed, along with the env-var
contract (`PVE_USER` gates the whole env path; `PVE_VERIFY_SSL=false` is required because the PVE
cert at `192.168.1.50` is self-signed), the `id="lxc/<vmid>"` label shape, and a concrete image pin
`prompve/prometheus-pve-exporter:3.9.0` (three-part, so `test_no_floating_service_image_tags` stays
green). The PVE endpoint `192.168.1.50` comes from `mise.toml:31` — committed and non-secret, so it
belongs in role defaults, not the vault.

No code changed, no tests written, no `just play`, no live query, no commit. Two docs touched
(`plan.md`, `progress.md`) and two tasks created.

**2026-07-31, Planner on `queue.advance` (Step 4a closed).** Step 4's wave is NOT exhausted — 4a's
close unblocked **4b (`task-1785442438-e959`)** and **4c (`task-1785442474-5022`)**, both agent-side,
and 4d stays blocked on them. Per the one-wave rule I created NO tasks and materialized no Step 5
(there is none; Step 4 is the last numbered step). Published 4b as the wave's next ready task.

**AND I CORRECTED A ROW IN 4B THAT 4A'S MEASUREMENT FALSIFIED.** 4b was written on 2026-07-30 from
the same premise 4a carried — that `0750` dirs / `0640` root:root renders are unreadable to uid 472 —
and its AC (b) told the Builder to prove "the file mode regressed to `0640` -> RED". 4a REFUTED that
premise against real `grafana/grafana:13.1.0` (the container runs uid 472 **gid 0** and the files are
root-group, so the group bits grant the read) and FLIPPED the guard to an access question
(`_grants_access`), where `0640` root:root is correctly GREEN. A Builder following 4b literally would
have had to either fake a red row or re-flip a guard that three review rounds and a live image had
just settled — the "a guard that forbids the real answer" failure this repo has already hit. The row
is rewritten to what survives the flip: deliver the new JSON at a mode that does NOT grant read to
uid 472/gid 0 (`0600`, or its dir at `0700`) -> RED, which still proves the new file entered 4a's
inventory rather than being assumed into it, plus an explicit "do not re-flip `_grants_access`
without a run against the real image in the log". I also wrote 4a's two other operator-facing
outcomes into the task so they are not rediscovered: the datasource uid is **pinned to `Prometheus`**
(`grafana-datasource.yml.j2:54`, with the live store's generated `PBFA97CFB590B2093` handled as a
migration), so 4b's panels reference that exact string; and the two non-fatal `level=error` lines for
`provisioning/alerting` and `provisioning/plugins` are **ours** — the `:ro` mount replaces the
directory the image ships — so neither 4b nor 4d should read them as the failure.

**4C I READ AND LEFT ALONE.** It never carried the literal-mode row (it says "the mode is readable",
which is the access framing 4a landed on), so there is nothing in it to correct. It stays READY for
the next `queue.advance`.

Verified the description actually changed rather than trusting `ensure`'s terse "Reused task" line.
No code changed, no tests run, no `just play`, no live query, no vault value, no commit; the
operator gates 1b/2b/3b/4d are untouched.

**2026-07-31, Planner on `queue.advance` (Step 4b closed).** Step 4's wave is still NOT exhausted —
4b's close leaves **4c (`task-1785442474-5022`)**, agent-side and repo-side, as the only remaining
task in it; 4d stays blocked behind 4c. Published 4c as the wave's next ready task. Step 4 is the
last numbered step, so **no Step 5 exists and none was invented** — `LOOP_COMPLETE` is not available
while 4c and four operator gates are open.

**I MATERIALIZED THE FINALIZER'S OPEN FINDING INSTEAD OF BANKING IT, AND I RE-MEASURED IT FIRST.**
`task-1785497167-e413` (`code-assist:plex-monitoring:guard:dashboard-template-vars-declared`, P2) —
same shape as the two `guard:*` rows already in the queue: agent-side, open, NOT part of a step wave.
The finding arrived as a claim, so I checked it rather than routing it: `grep -c` for `templating`
and for `label_values` over `scripts/test_grafana_provisioning_shape.py` returns **0** — the guard
does not read the templating block at all — while `files/grafana-pve-dashboard.json` declares
**exactly one** variable (`guest`) and interpolates `$guest` in **13 target expressions across 11
panels**, and `files/grafana-homelab-dashboard.json` declares and interpolates none. So the
Finalizer's F7/F7b (delete the list; rename `guest` -> `guestt`) are GREEN 13/13 over a dashboard
where every panel renders a broken query. That is `plan.md` Step 4's own Test Requirement — the
drop-down listing CT 110 and CT 111 — and 4d step 3 verbatim. **mem-1785467707-f8cd's rule is that a
defect declared and never SCHEDULED is shipped**, and the Finalizer was right not to reopen 4b for
it: it is a hole in the GUARD, not a defect in the ARTIFACT, and 4b's own AC enumerated its
mutations and reddened all of them. A row the task never asked for is not a seventh round.

**AND I WROTE TWO THINGS INTO THE NEW TASK THAT THE FINDING DID NOT CARRY.** Grafana interpolates a
variable in **three** spellings — `$var`, `${var}` and `[[var]]` — so a tokeniser that forms only the
first is blind to a near-miss it cannot form, which is precisely the six-round defect DEC-077 closed
in the `pve_*` row; the task is told to write the tokeniser against the grammar. And the **built-ins
are the declared price**: `$__rate_interval` and its siblings must stay GREEN, neither dashboard uses
one today, so an exclusion list that is wrong in the permissive direction would be INVISIBLE — hence
an explicit AC row that adds a built-in to a real file and asserts GREEN. The unused-declaration
direction is explicitly NOT red, so 4c's composite may legitimately declare nothing.

**I CORRECTED 4C RATHER THAN LEAVING IT ALONE THIS TIME.** The previous Planner read 4c and found
nothing 4a had falsified. 4b has since landed five facts that were not true when 4c was written on
2026-07-30, three of which would have reddened a Builder's first `just test` by surprise:
- **the `pve_*` allow-list row scans EVERY delivered dashboard**, over the same
  `_delivered_dashboards` inventory — so 4c's file enters its scope the moment its copy task exists.
  Its CT 110 panels must name families in `PVE_EXPORTER_SERIES` (38, read out of the pinned image by
  AST at digest `sha256:78a58df7…0757f`), and the DECLARED PRICE applies to 4c too: a `pve_`/`PVE_`
  token used as PROSE in a title or description reddens. Rename the prose, do not widen the guard.
- **six rows come free** (inventory, `_grants_access` readability, uid agreement, distinct dashboard
  uids, parse, delivered-where-Grafana-looks) — 4c adds rows for what nothing yet covers (the
  `plex@file` selector, the `_bucket` histogram read, the `plex_*` names) and does not re-add those.
- **do not re-flip `_grants_access` or the round-6 tokeniser** — both are settled against a run on
  the real image; `0640` root:root is correctly GREEN because the container is uid 472 **gid 0**.
- **the datasource uid is the pinned literal `Prometheus`**, and the two `level=error` provisioning
  lines for `alerting`/`plugins` are ours, not a failure.
- **the templating hole is now `task-1785497167-e413` and is NOT a blocker on 4c** — but nothing
  offline will catch a typo in a variable 4c declares, so 4c checks that by hand and says so.

Verified both `ensure` calls by re-reading the stored task rather than trusting the terse
"Ensured/Reused" line. No code changed, no tests run, no `just play`, no live query, no vault value,
no commit; HEAD still `7e9c426`; the operator gates 1b/2b/3b/4d are untouched.

## Verification Notes

_(Builder: record the gate result and the mutation matrix for the shape guard here.
Operator: paste the live Prometheus query and the returned `le` labels here, with the date.)_

- 2026-08-02 — **Finalizer, Step 9 (`task-1785624345-a15c`) — REPAIRED IN-HAT, CLOSED,
  `queue.advance`.** Guard `6bbd6944da50` → **`56bba79ef94e`**, eight comment lines, one hunk. The
  round-4 review PASSED naming ONE defect and wrote the pre-commitment down (DEC-203); I took it
  rather than opening a fifth prose round (DEC-204), because acceptance (a)-(d) were satisfied at
  the delivered sha and the objective's highest-value row is an operator gate no prose round
  advances. **THE REPAIR IS ONE IDENTIFIER:** the clause's closing pointer now names
  `logs/builder-a15c-r4-red.py` PART D **at THIS text** — `PASS: 26/26` at the sha the sentence
  ships at, its D5 delivering three top-level ARRAYs and printing 0 reaching `_unreadable`, 0
  entering the chain — while `logs/critic-a15c-r3-neither-set.py` is **KEPT** (round 4's own A6
  asserts its presence) with the text it scored, `821b687f6267`, named beside it.
  **WHAT THE REVIEW DID NOT PRICE, AND WHY THIS WAS NOT A ONE-WORD EDIT:**
  `logs/builder-a15c-r4-pre-guard.py` quotes the edited block as its `new` side under an
  EXACTLY-ONCE assert, so editing the guard alone would have fired it and turned
  `builder-a15c-r4-red.py` E1/E2/E3 RED **in the same edit that cites it** — the defect being
  repaired, recreated. The anchor GREW instead, and the invariant is measured rather than assumed:
  `logs/finalizer-a15c-r4-repair.py` **22/22** (container-free, both real trees byte-identical at
  each end) rebuilds the PRE-repair reverser in a mirror, runs it at round 4's own text, and
  requires the two to emit the **SAME BYTES** — `821b687f6267`, chaining to `8cb7299e4568`,
  `54cec7fc4cea`, `9c08e2b54dc2`. The anchor moved; the OUTPUT did not, so no reader loses a TEXT.
  **INERTNESS PROVED, NOT ASSERTED:** inverse edit rebuilds `6bbd6944da50`, `ast.dump` IDENTICAL
  with no docstring normalisation, all 8 changed lines `#` comments inside the sibling's own
  `5271-5485`; A5 checks that every one of the 7 claims round 4 was passed for is still in the
  clause — the repair ADDED a pointer and retired no sentence. D2 is the row that closes the
  review's argument: the citing sentence and a PASSING cited harness now exist **in one text**, a
  pair that existed at no text before. **BACKPRESSURE, RE-RUN NOT READ:** `just test` **GATE PASS
  36/36 rc=0** (pre and post), guard standalone **22/22**, `builder-a15c-r4-red.py` **26/26** at
  the shipping sha, `-collateral.py` **18/18**, `-pre-guard.py` rc=0 on all four texts.
  **COST, BY NAME:** `logs/critic-a15c-r4-citation-resolves.py` 13/13 → **FAIL 10/13**, red rows
  exactly `A1-delivered-sha`, `A2-citation-on-disk-once`, `D2-and-the-comment-does-not-name-it`,
  and **PASS 13/13** in a mirror at `6bbd6944da50` — its SUBJECT is repaired, it is not broken,
  which is also why a review harness may never be cited by the source it reviews; its B3 stays
  green in the red run. A direct grep agrees with the census: exactly three files quote the edited
  sentence — my proof, the reverser, and that deliberately-red harness. **NOT DONE:** no commit
  (HEAD `7e9c426`), no `just play`, no live call, no vault value, nothing under `ansible/`, no
  container, no gate touched, no task created. **Step 9's one-row wave is exhausted; 14 ready guard
  rows and Step 4d remain, so this is `queue.advance` and not `LOOP_COMPLETE` —
  `task-1785442499-1851` (Step 4d, P1, OPERATOR ONLY) is still the highest-value action on this
  objective and no agent may close it.** Confidence 88.

- 2026-08-02 — **Builder, Step 9 (`task-1785624345-a15c`) — BUILT, `review.ready`.** Guard
  `9c08e2b54dc2` → `54cec7fc4cea`, **three executable lines** (`refuses_uid = …`, the fifth chain
  entry, the `log is None` clause branch) plus the comment that prices them. RED FIRST:
  `logs/builder-a15c-red.py` at `9c08e2b54dc2` = **FAIL 56/65**
  (`logs/builder-a15c-red-pre.log`), the nine misses being exactly the two mis-ordered carriers,
  the drop, the false log line and the disagreements they cause. Same harness at the delivered
  text = **PASS 65/65** (`logs/builder-a15c-red-post.log`).

  **THE ENGINE, RE-MEASURED FOR THIS CHAIN'S OWN CARRIERS.** This code runs only for a delivered
  dashboard `_read` cannot decode as UTF-8 whose bad byte sits at a SAVED position, so its carriers
  are a separate delivered-file set from every earlier round's: 14 files each carrying a raw `0xff`
  inside a panel's `title` string, delivered in ONE provisioning run on the pinned
  `grafana/grafana:13.1.0`, container log kept, every `error=` printed, `/api/search` read back.
  **All 13 predictions were written down before the run and all 13 held** (PART A), in both runs.
  One delivered file per ADJACENT PAIR of the repaired five-slot chain — `title`↔`uid`,
  `uid`↔`number`, `number`↔`tag`, and `tag`↔each non-refusing member — never against a shared
  pivot. Anti-vacuity in the same run: the legal control served, each of the five rules ALONE
  reached and named, and no duplicate-uid warning, no duplicate-title warning, no provider lockout
  (every carrier's uid and title spelling is its own; three distinct trim-class spellings, three
  distinct non-string uids).

  **THE REPAIR IS AN ORDERING, AND A THIRD CLAIM THE TASK DID NOT NAME.** `refuses_uid =
  isinstance(uid, str) and _grafana_stored_uid(uid) is not None` puts the refusing half in the
  engine's 4th slot and both non-refusing members LAST, after the tag — nothing deleted, the chain
  still RED for a dashboard saved at an address nothing in this repo can name. What moving them
  alone would have shipped is a NEW false sentence: `_unreadable` does not merely name a defect, it
  frames it ("refuses to serve the document it holds … so look for `<log>` in the container log"),
  and the engine prints NO line for these two and SERVES the file. Measured, pre-edit, PART D:
  a trim-class uid ALONE was already being sent to grep `failed to save dashboard` for a document
  `/api/search` returns. So the fifth entry carries `log=None` and gets its own clause. `just test`
  → **GATE PASS 36/36 rc=0** (`logs/builder-a15c-gate.log`).

  **COLLATERAL, ATTRIBUTED AT BOTH TEXTS AND NOT BY REPRODUCING A FAILURE AT ONE**
  (mem-1785630967-6fdd). `logs/builder-a15c-pre-guard.py` rebuilds `9c08e2b54dc2` by inverse edit,
  sha-verified, real path unmoved; `logs/builder-a15c-collateral.py` (**PASS 8/8**) pulls every
  string literal out of the 63 `logs/*.py` that name this chain or its predicate and counts each in
  BOTH texts. Four anchors moved. Two are **DELIBERATE** — `builder-fb36-r2-collateral.py`'s
  `S-first-spelling-keeps-its-fence` and `critic-fb36-uid-nonrefusal-before-number.py`'s
  `C-first-spelling-has-the-fence` both assert the fence this row exists to replace. Two are in old
  chained reversal scripts (`red-579d-r5-pre-guard.py`, `red-579d-r8-pre-guard.py`) and **both were
  already not running at `9c08e2b54dc2`** for anchors no round of this task touched (r5 pair 1; r8
  pairs 3 and 4) — a15c deepens an already-broken chain by one pair each, disclosed, and the re-link
  is a `recheck-chain` file, which is what those rounds did for their own predecessors. **NOT ONE
  harness was edited.** `logs/critic-fb36-r2-unreadable-sibling.py` — the fb36 review that FILED
  this row, 6/6 pre-edit (`logs/builder-a15c-critic-sibling-pre.log`) — is now **3/6**, flipping
  EXACTLY its three defect-asserting rows (`A-trim-vs-number`, `A-trim-vs-tag`,
  `B-nonstring-dropped`) while its other two rows and its `Z-guard` stay OK. That flip is
  acceptance (a).

  No commit, no `just play`, no live call, no vault value, no `ansible/` write, no operator gate
  touched (1b/2b/3b/4d), no task created or closed. Per `mem-1785624794-9c63`, **no top-level `id`
  rule was added to either chain.**

- 2026-08-02 — **Planner, Step 9 cut (`queue.advance` after `ba6c` closed) — the routed row
  re-measured BEFORE routing, not adopted.** `logs/critic-fb36-r2-unreadable-sibling.py` was scored
  at guard `a70d851ce802` and `ba6c` has since moved the file to `9c08e2b54dc2`, so its 6/6 was a
  fact about a text that no longer exists. Re-run at the delivered tree: **PASS 6/6** — PART A
  (trim-class uid vs the number, vs the tag), PART B (non-string uid ALONE dropped; the repaired
  row's 5th link disagrees on polarity; non-string + tag right by accident), PART Z (`Z-guard`
  confirms `9c08e2b54dc2`). The two sites were also read directly rather than taken from the
  harness's summary: `_unreadable`'s chain at **:1413-1421** asks
  `(_grafana_short_uid_defect(uid) if isinstance(uid, str) else None, GRAFANA_LOG_SAVE)` **2nd of
  four**; the repaired spelling at **:5362-5367** computes
  `refuses_uid = isinstance(uid, str) and _grafana_stored_uid(uid) is not None`, asks the refusing
  half 4th and the whole predicate LAST. No file under `scripts/` or `ansible/` was written this
  turn; the harness starts no container and the guard sha is unchanged at both ends.

- 2026-08-01 — **Builder, Step 8a (`task-1785622294-ba6c`) — BUILT, `review.ready`.** Guard
  `a70d851ce802` → `9c08e2b54dc2`, **four executable lines in one row**
  (`logs/builder-ba6c-pre-guard.py --ast`, docstrings stripped). `just test` **GATE PASS 36/36
  rc=0** (`logs/builder-ba6c-gate.log`; the guard runs INSIDE the gate — verified by grep at line
  484, not assumed), guard standalone **PASS 22/22**.

  **THE REPAIR IS AN ORDERING AND NOT A DELETION, and neither half of the gate is dropped.** The
  presence gate's `uid` half was a GUARD-POLICY claim asked above every engine rule; its `title`
  half was already answered, in the engine's own words, by `_grafana_title_defect` at the head of
  the chain. Both classes move INTO the chain — a falsy `title` to its first clause, a falsy `uid`
  to the LAST one, the non-refusing half `fb36` put after the tag. What stays is the SHAPE, and it
  is an engine rule at the engine's own position: the three predicates take FIELDS, a document that
  is not an object has none, and the engine refuses such a file at the LOAD layer, BEFORE every
  save-time rule. Its sentence now quotes the engine's own line (`Dashboard title cannot be empty`)
  and mirrors the one `_unreadable` — the FIRST spelling of this chain — already carries.

  **RED FIRST AND AT MY OWN HANDS.** `logs/red-ba6c.py` against the UNEDITED guard: **40/52**
  (`logs/red-ba6c-pre.log`), the twelve MISSes being exactly the ten carriers and fb36's own two
  PART D rows. After the edit, **69/69** (`logs/red-ba6c-post.log`) with BOTH texts scored off ONE
  engine run (the pre-edit text rebuilt BY SHA in the same process — `mem-1785601139-1394`, a
  cached engine answer is not a measurement).

  **THE ENGINE, ONE DELIVERED FILE PER CARRIER, ONE RUN ON THE PINNED `grafana/grafana:13.1.0`,
  container log kept, `/api/search` read back. All 13 predictions were written down above the run
  and all 13 landed.** `uid: ""` + a 5001-char title and NO `uid` + the same title are the TITLE;
  `uid: ""` + a 51-byte tag is the TAG — the rule FURTHEST from it; NO `uid` + `1e400` is the
  NUMBER; `uid: ""` + a blank-after-trim title is the TITLE. **NOT ONE of the eight carriers the
  gate answered for is a `uid` refusal at the engine** (`A-no-uid-rule`). The SHAPE class was
  delivered in THREE spellings, not one: a top-level ARRAY, an ARRAY carrying `1e400`, and a bare
  `42` — the engine names the TITLE for all three, including the one that also breaks the number
  rule, which is what puts the shape clause ahead of the deferred number and not merely beside it.

  **AND THE NON-REFUSAL IS PROVED BY SURVIVAL, not by an untriggered rule** (PART B): `uid: ""`
  alone and NO `uid` alone are each **IN THE STORE** in that same run, under an address nothing in
  this repo can name — which is why this row stays RED for them, through the chain's last clause
  and in the engine's own terms (`GENERATES a uuid`), and not through a refusal.

  **NO FAIL-OPEN, MEASURED RATHER THAN ARGUED** (PART F): all **fourteen** falsy spellings of the
  two fields — `""`, `0`, `0.0`, `False`, `[]`, `{}`, absent, for each of `uid` and `title` — are
  RED on BOTH texts. The sentence moves; the verdict does not. `fb36`'s three seams
  (title|uid, uid|number, number|tag) are byte-identical across the two texts (PART S).

  **THE CENSUS RAN FIRST AND ITS ANSWER IS THAT THE FOUR SIBLING ASSERTIONS CANNOT SURVIVE THE
  REPAIR — DISCLOSED AND ATTRIBUTED, NEVER EDITED.** `logs/builder-ba6c-collateral.py` **20/20**
  (`logs/builder-ba6c-collateral.log`). Each sibling is run WHOLE in a tempdir TREE built at each
  text, `logs/` copied verbatim so its own `parents[1]` resolves to the copy:
  `red-step05d-rework-r10.py` **S1/S2**, `red-step05d-rework-r11.py` **S6** and
  `critic-step05d-r9-title-provisionability.py` **D2** each HELD at `a70d851ce802` and FAIL at
  `9c08e2b54dc2`. All four assert `"no top-level uid/title" in <the row's line>` — the sentence
  this round removes — so what they lost is the SPELLING of a refusal and not the refusal: every
  one of their carriers is still RED, through the chain, naming the rule the engine stopped on.
  **The bound is counted, not promised** (PART G): 48 + 43 + 61 = 152 rows scored across the three
  harnesses and EXACTLY `S1, S2, S6, D2` moved. Every `.py` under `logs/` hashes identically at
  both ends of the run (`Z-logs`).

  **THE RECONSTRUCTION CHAIN IS TWO LINKS LONGER, NOT BROKEN** (PART K): `ba6c` →
  `a70d851ce802` → (`builder-fb36-r2-pre-guard.py`, UNEDITED) → `881e2c620ddc` →
  (`builder-fb36-pre-guard.py`, UNEDITED) → `9c61b6112215`, each link asked for its OWN declared
  sha, and non-vacuous (the r2 link run against the delivered text lands elsewhere). PART Q: the
  r9/r10/r8 critic-rechecks and the three 579d recheck chains give **identical outcomes on both
  texts** — already unreachable before this round and unmoved by it.

  No commit, no `just play`, no live call, no vault value; nothing under `ansible/` written and
  gates 1b/2b/3b/4d untouched. `task-1785442499-1851` (Step 4d, P1, OPERATOR ONLY) remains the
  highest-value action on this objective and no agent may close it.

- 2026-08-01 — **Planner, `queue.advance` after `fb36` closed (Step 7 exhausted, Step 8 cut).**
  Nothing built and nothing run beyond three cheap state checks, each verified rather than taken
  from the handoff: `HEAD` is `7e9c426`; `sha256sum scripts/test_grafana_provisioning_shape.py`
  is `a70d851ce802…`, matching the guard sha the `fb36` Finalizer reported; and
  `task-1785622294-ba6c` is `status: open`, `priority: 2`, `blocked_by: []` on the queue's own
  record, so the wave this activation routes is genuinely ready and not blocked. The gate result
  itself (`just test` 36/36 rc=0, guard standalone 22/22) is the Finalizer's measurement, taken on
  its word and labelled as such — no hat re-ran it this turn.

- 2026-08-01 — **Builder, Step 6a (`task-1785601096-9ffc`) — BUILT, `review.ready`.** New row
  `test_delivered_dashboards_have_distinct_titles` in `scripts/test_grafana_provisioning_shape.py`;
  the guard is **21 rows → 22**. `just test` **GATE PASS 36/36 rc=0** (`logs/gate-9ffc.log`), guard
  standalone **PASS 22/22 rc=0**.

  **RED FIRST, and the pre-edit run is kept.** `logs/red-9ffc.py` against the UNEDITED guard:
  **3/12** (`logs/red-9ffc-pre.log`) — over a tree whose pve dashboard carries the homelab
  dashboard's title the whole guard printed **PASS 21/21 rc=0** and the title row was ABSENT. After
  the edit, **12/12** (`logs/red-9ffc.log`): the colliding tree is `FAIL 1/22 rc=1` with the verdict
  naming BOTH files and saying the engine gives no message of its own; the delivered tree is
  **PASS 22/22 rc=0**; a near-miss title, and the trailing-space twin the engine stores under ONE
  title, are both GREEN; a pair the provisioner never saves is RED at the parse row and silent here.
  Every edit is made in a tempdir copy and all six real files are sha256-identical at both ends.

  **THE TEST REQUIREMENT PROMOTED BY THE PLANNER — the SCOPE — is MEASURED, not inherited.**
  `logs/red-9ffc-title-scope.py` / `.log`, **8/8**, eight providers in ONE container on pinned
  `grafana/grafana:13.1.0`, every uid distinct and legal so the title is the only variable: two
  providers with one file each and the same title in the General folder BOTH take the lockout (so it
  is **NOT provider-scoped**); the same title in two folders — by `foldersFromFilesStructure` (`te`)
  and by two providers' distinct `folder:` (`tf`/`tg`) — takes NONE (so it **is folder-scoped**);
  and WITHOUT the folders flag two subdirectories flatten into one folder and the lockout returns
  (`th`), which is DEC-074's flattening claim measured rather than asserted. `ta`/`tb` re-carry the
  finding and its anti-vacuity in that same container.

  **AND THE KEY IS THE TITLE AS DELIVERED — MY OWN PREDICTION, REFUTED, LEFT VISIBLE.**
  `logs/red-9ffc-title-key.py` / `.log`, **8/8**. I wrote down before the run that the tracker would
  key on the title the engine SAVED, so that its trim would make two spellings one key. It does not:
  titles differing only by a trailing U+FEFF (`ua`) or U+0020 (`ub`) are STORED UNDER ONE TITLE,
  both served, and take **no lockout**, while the same title delivered twice verbatim (`uf`) takes
  it in that same container. So the row compares the delivered string EXACTLY — a `title.strip()`
  would have printed a provider-wide lockout over a delivery the engine serves in full. All FOUR
  members of the `_grafana_title_defect` fence were delivered twice apiece (`uc` empty at the LOAD,
  `ug` non-string at the LOAD, `ud` trim-empty at the SAVE, `uh` 5001 bytes at the SAVE): none is
  served and none collides, so skipping them is measured and not assumed.

  **THE FILING REVIEW'S OWN HARNESS, RE-RUN UNEDITED AT MY HANDS**
  (`logs/red-9ffc-critic-r12-recheck.log`): `critic-579d-r12-duplicate-title-lockout.py` now scores
  **6/7** — its engine rows A1/A2/A3 and both anti-vacuity rows are unchanged, and the ONE row that
  flips is **B1, its finding-detector**, which asserted the guard is GREEN over the colliding tree.
  It is RED now (`FAIL 1/22`). The finding is gone, which is the point.

  **THE COLLATERAL, PRICED RATHER THAN DESCRIBED** (`logs/red-9ffc-pre-guard.py` / `.log`, **7/7**).
  15 harnesses under `logs/` compare the literal `PASS: 21/21` in 26 assertions; none may be edited.
  This rebuilds the PRE-EDIT guard **by sha** (`c1fbc7b3e2e9`, the digest the RED-first run recorded)
  by inverting this round's two edits — one function block, one line in `main()` — and diffs a
  container-free stale harness across both trees: exactly **one** reachable row moves (`P1`, the
  count), the rest were already failing against the pre-edit guard (they detect the surrogate crash
  the 579d thread repaired), the abort line is identical in both trees, and no row silently improved.
  So what those harnesses lost is the NUMBER, not the verdict: the tree they run over is still green.

  No commit (HEAD `7e9c426`), no `just play`, no live call, no vault value, no other hat's harness
  edited, no leftover container. Only `scripts/test_grafana_provisioning_shape.py` and files under
  `logs/` were written. Gates 1b/2b/3b/4d untouched — **4d is still open, still P1, and still the
  highest-value action available to anyone.**

- 2026-07-31 — **Finalizer, Step 4a (`task-1785442414-452f`) CLOSED after 3 review rounds.**
  Gate re-run by me at both ends: `just test` **GATE PASS 36/36 rc=0**, the new guard
  `scripts/test_grafana_provisioning_shape.py` **PASS 11/11** inside the gate's own file list,
  traefik 41/41.

  **The battery was aimed where the review rounds were not.** Rounds 1–3 hardened the DELIVERY path
  (notify → handler → bind mount) and duplicate-key scanning, and the Critic re-measured those 18/18
  by execution. Every battery in the step, though, mutates the ONE dashboard that already exists —
  while AC (c) is forward-looking and **4b/4c are exactly the addition it anticipates**. So the
  Finalizer built the 4b pair (a new JSON in `files/` + its delivery task) from the attacker's side:
  17 rows in `logs/final-step04a-adversarial.log`, 9 more in `logs/final-step04a-adversarial2.log`,
  every watched file sha-identical at both ends. The generated uid, the name-not-uid spelling, the
  JSON with no delivery task, the inline `content:` spelling, the dashboard delivered one directory
  over, 0600 modes and the compose `user:` companion are all RED — **and the row where 4b is done
  RIGHT is GREEN**, which is the half that stops the guard forbidding the work it is meant to admit.
  Battery 2 reddens the two checks nobody had reddened (#1 sources-exist, #11 delivered-where-grafana
  -looks), so **all 11 checks now have a RED row an independent hat ran**.

  **AC (b)'s two literal rows are the ones the task told the Builder to flip.** "dashboards dir back
  to 0750 → RED" and "a grafana file back to 0640 → RED" both presume D1, which measurement
  refuted (uid 472 runs with GID 0; the files are root:root). The Finalizer re-measured the FLIPPED
  edges rather than inheriting them: a provisioning dir at 0700 RED, the datasource file at 0600 RED,
  the world-readable 0644 spelling GREEN, the delivered tree GREEN.

  **Real harness — the wave's next step, executed** (`logs/final-step04a-wave-harness.log`, 8/8):
  real `ansible-playbook` over the role's own tasks with a 4b-shaped second dashboard, then real
  `grafana/grafana:13.1.0` on the ansible OUTPUT at the role's real modes. 13 tasks ran including
  `RUNNING HANDLER [Restart grafana]`; both dashboards landed in the mount; the server booted;
  `/api/datasources/uid/Prometheus` returned 200 with `uid=Prometheus`; `/api/search` returned
  **`['Homelab Overview', 'Proxmox VE']`**; and the second dashboard's STORED panel reference read
  back as the provisioned uid. So the shape the guard blesses is the shape that works.

  **FOR 4d, AND IT CORRECTS AN ATTRIBUTION.** A healthy server prints four `level=error` lines. A
  BARE-IMAGE control (same image, none of our mounts, sampled after a settle) prints the two
  `plugin.backgroundinstaller` ones — those are the image's. The other two are **OURS**: the image
  SHIPS `/etc/grafana/provisioning` with `alerting/` and `plugins/` subdirs and the role's `:ro`
  mount REPLACES that directory, so `provisioning.plugins` / `provisioning.alerting` cannot read
  what is no longer there. **They are non-fatal** — the datasource resolves and both dashboards load
  with them in the log — and 4d's operator must not read them as the failure.

  **One finding banked, not blocking** (`task-1785457578-580a`, P2): `_grants_access` maps the
  ansible owner NAME `grafana` to uid 472, an unmeasured claim about the host's user table in the one
  file whose whole subject is identity. The delivered tree is `owner: root` everywhere and both
  runtime outcomes are loud, so it sits below the severity bar this loop set in round 12.

  Scope re-checked rather than trusted: none of the six out-of-scope files named in AC (d) carries a
  grafana-touching change (their diffs belong to Steps 1a–3a), `grafana-homelab-dashboard.json` is
  byte-identical to HEAD — pinning the uid to the name the JSON already used made the repoint the
  scope anticipated unnecessary — and HEAD is still `7e9c426`, so no commit. No live host, no
  `just play`, no vault value. Gates 1b/2b/3b/4d untouched. **4a's close unblocks 4b and 4c, both
  agent-side and both now READY**, so the wave is not exhausted and this is a `queue.advance`, not
  `LOOP_COMPLETE`.


- 2026-07-29 — Builder, woke on `tasks.ready` for `task-1785290391-b51a` and **did not start it**.
  Step 1b is operator-only in every one of its five steps (`just play` against the live household
  stack, a real request through `websecure`, a query against a running Prometheus), so there is no
  agent-runnable slice to take and marking it in-progress would misrepresent the queue. Did **not**
  close it — closing an operator gate as a checkbox is the failure mode this project has hardened
  against twice (mem-1784143921-4d7f, mem-1784742...-16d5). Emitted `build.blocked`.
  Verification actually run this iteration: `just test` → **GATE PASS 35/35 exit 0**
  (`logs/gate-builder-step01b-park.log`), so the tree the operator would deploy from is green.
  Re-confirmed the deploy path from the role side rather than from the Finalizer's summary:
  `justfile:38-39` `play` = `ansible-playbook site.yml` (no tofu), `docker_host/tasks/main.yml:78`
  notifies `Restart traefik`, `docker_host/handlers/main.yml:5-8` runs `docker compose restart
  traefik` — so the static-config change does land. The ask is written up for David in
  `.ralph/agent/operator-ask.md` (current gate first, the still-open plex-ramdisk ask preserved
  below it), with the runner PID and the `--continue` resume line.

- 2026-07-29 — Planner, `queue.advance` after 1a closed. **`plan.md` was the third copy of the
  stale literal and nobody had swept it.** The Finalizer fixed the operator task and the top of
  this file; `plan.md` Step 1 still prescribed `[0.1, 0.3, 1.2, 5.0]` as the values to write and
  still named them as the Demo's success signal, and it called the incumbent "Go's defaults".
  `plan.md` is the artifact that defines what "Step 1 is done" MEANS, so an operator or a future
  hat reading it would have confirmed the change did NOT land — the same inversion, one artifact
  further out (mem-1785295766-6d76's blast-radius rule). Swept the repo for the literal: the only
  other live occurrences are `scripts/test_traefik_config_shape.py:459,466`
  (`TRAEFIK_DEFAULT_BUCKETS`, correctly labelled as Traefik's default and load-bearing for the
  `is_custom` pin) and `traefik.yml.j2:66` (the comment, also correctly labelled). Everything else
  is historical narrative in this file. **`plan.md` Step 1 now carries the shipped 13-boundary
  ladder, names `le="0.00025"` as the falsifier and 14 as the label count, says what failure looks
  like, states that the series is server-side handler duration, and records the correction inline
  so the wrong value cannot be re-derived from a stale doc.** Checklist marked `[~]` — 1a closed,
  1b open.

- 2026-07-29 — Planner: repo facts confirmed on disk before decomposing. `metrics.prometheus`
  exists at `traefik.yml.j2:59-64`; `prometheus.yml.j2` already scrapes `traefik:8082`, so Step 1
  needs no new scrape job; the gate is `just test` → `scripts/run_gate.py`, which auto-globs
  `scripts/test_*.py`; `scripts/test_traefik_config_shape.py` is the existing guard over this
  template and is where the new check belongs.

- 2026-07-29 — Builder, Step 1a (`task-1785290378-db09`,
  `code-assist:plex-monitoring:step-01:traefik-histogram-buckets`). Increment = 2 files:
  `M ansible/roles/docker_host/templates/traefik.yml.j2` (+10: a `buckets:` block sequence
  `0.1/0.3/1.2/5.0` under `metrics.prometheus`, with the WHY in the surrounding comment style)
  and `M scripts/test_traefik_config_shape.py` (+1 check → 31, the new
  `test_prometheus_histogram_buckets_tuned`). No new shape-test file, so the gate step count
  moves 34 → 35 only because of the per-check accounting, not a new glob entry.

  TDD: RED first — the check went in before the template did and failed for the intended
  reason (`block=True, in_block=None`: the `metrics.prometheus` block was found, the key was
  absent), then GREEN 31/31. Two defects in my OWN check surfaced between those runs and were
  fixed before the battery: `m.end()` sits before the key line's newline (so `splitlines()`
  yielded a leading `''` and the parse returned `[]`), and `\s*` after `buckets:` is greedy
  ACROSS the newline, swallowing the first `- 0.1` into the inline group (`[0.3, 1.2, 5.0]`).
  Both now use `[^\S\n]` and an explicit `lstrip("\n")`.

  The check slices `metrics:` → `prometheus:` in two hops and reads the `buckets` value out of
  THAT text only, in either flow or block form, then pins the four values by list equality —
  so it pins the values and the enclosing block, not the presence of a key. `EXPECTED_BUCKETS`
  is itself asserted strictly ascending and length 4, so a later edit of the constant cannot
  quietly relax the ordering the check exists to pin.

  MUTATION BATTERY — 10 rows, driver `/var/tmp/mutate_buckets.py`, full output
  `logs/mutation-step01a-traefik-buckets.log`. Every row rewrites the template with
  `write_text` (never `copy2` — a preserved mtime keeps a stale `__pycache__` entry valid,
  mem-1785122728-5116), runs the real shape test as a subprocess, restores with `write_text`
  and re-checks sha256. Pristine/final sha256 `d7e6773316b9f14f2471b20b5e2acfeb9ba49c23373ed20c89a8e4f7935bd36b`,
  `restored=True` on all 10.

  | Row | Mutation | Expected | Got |
  |---|---|---|---|
  | M1 | `buckets` block deleted | RED | RED (`in_block=None`) |
  | M2 | one value changed, `1.2 → 12.0` | RED | RED (`[0.1, 0.3, 12.0, 5.0]`) |
  | M3 | order reversed (descending) | RED | RED (`[5.0, 1.2, 0.3, 0.1]`) |
  | M4 | first boundary dropped (3 values) | RED | RED (`[0.3, 1.2, 5.0]`) |
  | M5 | extra `10.0` appended (5 values) | RED | RED (`[..., 5.0, 10.0]`) |
  | M6 | moved OUT to the file's top level | RED | RED (`in_block=None`) |
  | M7 | under `metrics:` but outside `prometheus:` | RED | RED (`in_block=None`) |
  | M8 | CONTROL — same values in YAML flow form | GREEN | GREEN |
  | M9 | CONTROL — unrelated edit (`log.level INFO → DEBUG`) | GREEN | GREEN |
  | M10 | whole `metrics.prometheus` section deleted | RED | RED (`block=False`) |

  M6/M7 are what make "INSIDE the block" load-bearing rather than decorative: the values are
  byte-identical and correct in both, and both redden purely on location. M8/M9 are the
  polarity controls — without them "no buckets anywhere" would pass every RED row and be
  unusable. M10 shows the premise pin (`block`) reports distinctly from the value pin.

  GATE: `just test` **GATE PASS 35/35 exit 0** (`logs/gate-step01a-traefik-histogram-buckets.log`)
  — 31/31 in this file, tofu init/validate, `ansible-lint --offline --profile production`,
  `ansible-playbook --syntax-check site.yml` all exit 0.

  TREE: the template is byte-identical to pristine after the battery (sha256 above). `git status`
  also shows carry-over from the in-flight plex-optimization work — `docs/runbooks/plex-latency-baseline.md`,
  `scripts/test_plex_latency_runbook_shape.py`, `logs/gate-step01-baseline-runbook.log`,
  `docs/plex-remote-latency-audit.md`, `ralph.agy.yml` — all of which were already modified when
  this iteration started and none of which this increment touched (the task names them
  explicitly out of scope). No commit (Builder preset).

  NOT DONE, by design: no playbook run and no live Prometheus query. Traefik's file provider
  watches only the DYNAMIC config; `traefik.yml` is STATIC, so these buckets do not reach the
  running proxy until `just play` re-renders the template and restarts the container. That is
  Step 1b, `task-1785290391-b51a`, operator-only.

## Completed Steps

**STEPS 1–9 ARE CLOSED; STEP 10 IS OPEN with a one-row wave (DEC-205).** **Step 9 CLOSED 2026-08-02**
— its one row (`task-1785624345-a15c`) went build → 4 review rounds → PASSED-naming-one-defect →
**repaired IN-HAT by the Finalizer** (DEC-203 wrote the pre-commitment, DEC-204 took it) and CLOSED
at guard `56bba79ef94e`, PASS 22/22, gate 36/36 rc=0, HEAD `7e9c426`, no commit. Round 1 was the
whole executable repair (`logs/builder-a15c-red.py` 65/65 on the pinned engine); rounds 2-4 were each
ONE comment clause, and the Finalizer's repair was the round's last owed identifier — a pointer that
resolved at NO text, re-aimed at `logs/builder-a15c-r4-red.py` PART D, green at the sha the sentence
ships at (`logs/finalizer-a15c-r4-repair.py` 22/22). **Step 10 is the DOCSTRING layer of that same
class** — `mem-1785632642-168d` names the guard's contract as three places (docstring, inline
comment, printed clause); Steps 7/8/9 repaired the clause and the comment, and nothing has been at
the docstring. Wave `task-1785634257-80de`, re-measured at the delivered sha before routing (7 call
sites, SIX pass `provisioned=`, the sentence says five) and re-`ensure`d to correct an acceptance
criterion that pointed at a dead harness. The paragraph below was written for the Step 8/9 state and
is kept as-is except for this correction. **Step 8 CLOSED 2026-08-02**
— its one row (`task-1785622294-ba6c`) went build → 1 review round → PASSED → CLOSED at guard
`9c08e2b54dc2`, PASS 22/22, gate 36/36 rc=0, HEAD `7e9c426`, no commit. The presence gate became the
SHAPE clause alone (DEC-199): both policy halves moved INTO the chain, four executable lines, an
ordering and not a deletion, proved by driving all fourteen falsy spellings of both fields through
the delivered predicates at both texts (`logs/finalizer-ba6c-adversarial.py` 25/25, both controls
GREEN). Two method memories came out of it and neither is a defect (`mem-1785627131-ecba`,
`mem-1785630967-6fdd`). **Step 9 is the LAST site of the same chain** — `_unreadable`'s spelling,
which fences the uid predicate with `isinstance()` alone; wave `task-1785624345-a15c`, re-measured
6/6 at the delivered sha before routing. The paragraph below was written for the Step 7/8 state and
is kept as-is except for this correction. **Step 7 was
cut on the `queue.advance` that closed `9ffc` (DEC-194) and is now CLOSED** — its one row
(`task-1785594766-fb36`) went build → 2 review rounds → PASSED → CLOSED at guard `a70d851ce802`,
PASS 22/22, gate 36/36 rc=0, HEAD `7e9c426`, no commit. Its Finalizer reported acceptance criterion
(c) UNMET with the measurement showing it was unsatisfiable when the task was written (DEC-196)
rather than re-reading it to fit, and FILED the round-2 Critic's finding (`task-1785624345-a15c`)
instead of patching it. **Step 8 is that step's own residue, not a new class** — the third of three
sites of one defect in one row, deferred in writing by DEC-195 on `fb36`'s atomicity alone; wave
`task-1785622294-ba6c`. The paragraph below was written for the earlier state and is kept as-is
except for this correction. Steps 1, 2 and
3 are complete gates included; Step 4 is agent-side complete with 4d the one operator gate still
open; Step 5 is closed with its four-row wave exhausted. **Step 6 was cut after DEC-153's "no Step 6"
was tested three times by an empty queue and answered by an operator restart**, and is now CLOSED —
its one row (`task-1785601096-9ffc`) went build → 13 review rounds → PASSED → CLOSED at guard
`9c61b6112215`, PASS 22/22, gate 36/36 rc=0, HEAD `7e9c426`, no commit. **Step 7 continues the same
contract one notch out on the bar** — the misdirected-alarm class, wave `task-1785594766-fb36` —
see `## Current Step`. The per-step "Outstanding: operator gate" lines below were written when
those gates were open — **1b, 2b and 3b have since closed** (DEC-154); only 4d remains.

1. **Step 1a — Traefik histogram buckets** (`task-1785290378-db09`) — CLOSED 2026-07-29 by the
   Finalizer after 6 review rounds. Shipped ladder
   `0.00025 … 30.0` in `traefik.yml.j2`, guarded in `scripts/test_traefik_config_shape.py`.
   Outstanding: **Step 1b** (`task-1785290391-b51a`), operator gate, now unblocked.
2. **Step 2a — pve-exporter repo-side wiring** (`task-1785324219-b403`) — CLOSED 2026-07-30 by the
   Finalizer after 15 review rounds; guard `1a95b475`, `just test` 35/35. Wired the image default,
   the PVE coordinates, `PVE_TOKEN_VALUE` via the vault, the `pve-exporter` service, the
   multi-target `/pve` scrape job, and the delivery chain (`mode: "0644"` + `notify: Restart
   prometheus`) that repairs the live Prometheus crash loop. Outstanding: **Step 2b**
   (`task-1785324247-3934`), operator gate, now unblocked.
3. **Step 3a — plex-exporter repo-side wiring** (`task-1785370559-2a76`) — CLOSED 2026-07-30 by the
   Finalizer after 12 review rounds; guard `2fe4bc38`, delivered `PASS: 41/41`, `just test` GATE
   PASS 35/35 rc=0, plus the Finalizer's own independent 6/6 adversarial battery
   (`logs/final-step03a-adversarial.log`) aimed at the deliverable rather than at the
   template-reader the review rounds had been hardening. Wired the image default, `PLEX_TOKEN` via
   the vault, the `plex-exporter` service, and the SINGLE-TARGET scrape job whose shape is
   deliberately the opposite of 2a's `/pve` job. Outstanding: **Step 3b**
   (`task-1785370581-de17`), operator gate, unblocked by this close.

4. **Step 4 — Import and Configure Grafana Dashboards** — AGENT-SIDE COMPLETE 2026-07-31.
   **4a** (`task-1785442414-452f`, the provisioning path: the modes, the datasource `uid`, and the
   new `scripts/test_grafana_provisioning_shape.py` whose load-bearing row is cross-file) CLOSED
   after 3 review rounds. **4b** (`task-1785442438-e959`, `grafana-pve-dashboard.json` templated
   over the guest id) CLOSED after 6 rounds; guard `396ecd28` PASS 13/13. **4c**
   (`task-1785442474-5022`, the composite Plex Health dashboard, the carrier that finally READS
   Step 1's histogram ladder) CLOSED after 11 rounds — all eleven on one clause of the PromQL
   reader; guard `a3b1595e` PASS 18/18, count up 13 → 18. The Finalizer's own work went where no
   round went: `logs/final-step04c-adversarial.py` 19/19, and `logs/final-step04c-grafana-loads.sh`
   6/6 — `grafana/grafana:13.1.0` booted OFFLINE against a tree assembled the way the role
   delivers it, accepting all three dashboards and DECLINING an invalid one. Outstanding:
   **Step 4d** (`task-1785442499-1851`), operator gate, unblocked by 4c's close.

## Remaining Steps (from `plan.md`)

**ONE: Step 10 — the DOCSTRING layer of the misdirected-sentence class, `_unreadable`'s
blast-radius paragraph (DEC-205), wave `task-1785634257-80de`, CURRENT.** Beside it, not part of it:
the operator gate `task-1785442499-1851` (4d), which no agent may close and which stays the single
highest-value action on this objective, and **thirteen** agent-side rows each deferred with its
reason recorded per row (see **Current Step**, **Active Wave**, and `plan.md` Step 10). **The successor is
declared this time: `task-1785635701-d2fd`** — acceptance (b)'s READABLE half, banked by a15c round
4 and cited by id in the guard's own prose, so the guard is currently correct-and-incomplete about
it rather than wrong. `fc70` (P2, the delivery-arity miscount) remains the bar-leader on
silence and remains blocked by the same thing it has been blocked by since it was filed: the
blast-radius enumeration its own acceptance criterion (c) demands over a class this repo's delivered
tree does not carry today.

6. **Close the SILENT-class guard rows filed AFTER Step 5's wave was cut** — **CLOSED** 2026-08-01,
   cut the same day on the `queue.advance` that closed `579d` (DEC-182). Wave as cut and as
   finished: ONE row, `task-1785601096-9ffc`, build → 13 review rounds → PASSED → CLOSED at guard
   `9c61b6112215`, PASS 22/22, gate 36/36 rc=0, HEAD `7e9c426`, no commit. Queue hygiene at the cut
   retired `task-1785504947-fbde`; queue hygiene at the close filed `task-1785621026-fc70`.

7. **Close the MISDIRECTED-ALARM guard rows — the gate is RED and the verdict names a field the
   engine never looked at** — **CLOSED** 2026-08-01, cut the same day on the `queue.advance` that
   closed `9ffc` (DEC-194). Wave as cut and as finished: ONE row, `task-1785594766-fb36`, build →
   2 review rounds → PASSED → CLOSED at guard `a70d851ce802`, PASS 22/22, gate 36/36 rc=0, HEAD
   `7e9c426`, no commit. The row repaired TWO of the three sites where
   `test_delivered_dashboards_parse_as_dashboards` names a field the engine never looked at and
   DEFERRED the third in writing (DEC-195 → `task-1785622294-ba6c`, now Step 8's wave); its round-2
   Critic finding was FILED, not patched (`task-1785624345-a15c`), and acceptance criterion (c) was
   reported UNMET with the measurement that shows it was unsatisfiable when the task was written
   (DEC-196). Queue hygiene at the cut filed `task-1785621026-fc70`; at the close, nothing — the
   Finalizer's one adversarial finding is a NON-defect and a prohibition (`mem-1785624794-9c63`).

8. **Close the THIRD site of the misdirected-alarm defect — the READABLE row's PRESENCE GATE** —
   **CLOSED** 2026-08-02, cut 2026-08-01 on the `queue.advance` that closed `fb36` (DEC-198). Wave as
   cut and as finished: ONE row, `task-1785622294-ba6c`, build → 1 review round → PASSED → CLOSED at
   guard `9c08e2b54dc2`, PASS 22/22, gate 36/36 rc=0, HEAD `7e9c426`, no commit. The presence gate
   became the SHAPE clause alone (DEC-199) — an ordering of four executable lines, not a deletion.
   Queue hygiene at cut and close: nothing filed, nothing retired.

9. **Close the FIRST spelling of the rule order — `_unreadable`'s save-layer chain** — **CLOSED**
   2026-08-02, cut the same day on the `queue.advance` that closed `ba6c` (DEC-200). Wave as cut and
   as finished: ONE row, `task-1785624345-a15c`, build → 4 review rounds → PASSED-naming-one-defect →
   **repaired IN-HAT by the Finalizer** (DEC-203 → DEC-204) and CLOSED at guard `56bba79ef94e`,
   PASS 22/22, gate 36/36 rc=0, HEAD `7e9c426`, no commit. Queue hygiene at the cut: nothing filed,
   nothing retired; at the close its own rounds had banked two rows, `task-1785634257-80de` (now
   Step 10's wave) and `task-1785635701-d2fd` (the declared successor).

10. **Close the DOCSTRING layer of the misdirected-sentence class — `_unreadable`'s blast-radius
    paragraph counts FIVE and the AST counts SIX** — **CUT 2026-08-02** on the `queue.advance` that
    closed `a15c` (DEC-205), **CURRENT**. Wave: ONE row, `task-1785634257-80de`. Not a new bar and
    not a new class — `mem-1785632642-168d` names the guard's contract as three places (docstring,
    inline comment, printed clause) and Steps 7/8/9 repaired only the latter two. Re-measured at the
    delivered guard `56bba79ef94e` before routing, and **re-`ensure`d** to correct acceptance (d),
    which named a harness that is dead at that sha. Queue hygiene this turn: nothing filed, nothing
    retired.

### Step 5's close, and the "no Step 6" it wrote — kept for the chain

**Superseded twice over, and both reversals are recorded rather than quietly dropped:** DEC-182 cut
a Step 6 on three facts DEC-153 did not have, and DEC-194 has now cut a Step 7 on the same contract.
The paragraph below is what was true when Step 5 closed.

**NONE. 2026-08-01: Step 5 closed, and it was the last numbered step.** What remains is not a step:
one operator gate (`task-1785442499-1851`, 4d) and eleven agent-side rows priced below Step 5's own
bar with the reason recorded per row (see **Active Wave** and `plan.md` Step 5, "THE CLOSE").
No Step 6 was cut — DEC-153, and the paragraph two blocks down explains why that distinction is the
whole point.

### Step 5, as it was while current — kept for the chain

5. **Close the guard findings that make a delivered artifact SILENTLY wrong** — **CLOSED**, cut
   2026-07-31 on the `queue.advance` that closed 4c. Wave as cut: 5a `task-1785497167-e413`, 5b
   `task-1785517907-a5ec`, 5c `task-1785441840-e8eb`; six deferred behind it. **Updated 2026-07-31
   on the `queue.advance` that closed 5a: 5a CLOSED (8 review rounds), 5b READY and routed now, 5c
   READY and next, and the wave grew to FOUR — 5d `task-1785524605-ea55`, blocked by 5b.** See
   **Current Step** and **Active Wave** for the pricing that produced those numbers, and `plan.md`
   Step 5 for the full argument.

**STEP 5 WAS NOT INVENTED WORK AND THE DISTINCTION IS THE POINT.** The Planner contract forbids
inventing tasks once the numbered steps run out. Nothing here was invented: all nine tasks already
existed, every one filed by a Builder, Critic or Finalizer with its own measurement attached, and
all nine were READY with no step to belong to — which is why `LOOP_COMPLETE` was forbidden at 4c's
close. What this step adds is decomposition, which is the Planner's own job: an order, a bar, a
merge of the two that were one finding, and a recorded reason for the six that wait. When 5c closes,
a future Planner re-prices the six with 4d's operator evidence in hand; if that pricing says no,
what is left is the four operator gates (1b, 2b, 3b, 4d) that only David can close.

**THAT PRICING RAN 2026-08-01 AND IT SAID NO (DEC-153), AND THE SAME DISTINCTION IS WHY NO STEP 6
EXISTS.** Step 5 was legitimate because nine rows were READY with no step to belong to and one of
them was Step 4's own Test Requirement — *being ready was never the reason, clearing the bar was.*
Eleven rows are ready now and none clears it, so cutting a Step 6 out of them would run Step 5's own
argument in reverse: decomposition is the Planner's job, but manufacturing a step to keep a Builder
busy is the invention the contract forbids. **And the count in the sentence above is now wrong in
the good direction — three of those four gates are closed. What is left is ONE: 4d.**

### 2026-07-29 — Step 1a REWORK after `review.rejected` (task-1785290378-db09)

  REJECTION, upheld in full: the shipped `[0.1, 0.3, 1.2, 5.0]` are traefik:v3.7.5's OWN defaults.
  Re-verified against the pinned image rather than taken on trust —
  `docker run --rm traefik:v3.7.5 traefik --help` prints
  `--metrics.prometheus.buckets (Default: "0.100000, 0.300000, 1.200000, 5.000000")`.
  The previous increment was a runtime no-op.

  FIX, two files (unchanged scope):
  - `traefik.yml.j2` — boundaries are now
    `[0.005, 0.01, 0.025, 0.05, 0.1, 0.15, 0.25, 0.4, 0.6, 1.0, 2.5, 5.0, 10.0]`, chosen off this
    project's own measurements: Traefik's LAN-leg overhead +9.4 ms median (was entirely inside the
    default's first bucket, i.e. the proxy hop was unresolvable) and remote /identity TTFB
    157/293/486 ms (the default collapsed the whole range into le=0.3 and le=1.2).
  - The comment's false claim is corrected. Traefik does NOT use client_golang's DefBuckets for
    this histogram — it has its own default, and DefBuckets are FINER below 100 ms, not coarser.
    The comment now names Traefik's actual default and cites the measurements.
  - `test_traefik_config_shape.py` — `EXPECTED_BUCKETS` updated; new `TRAEFIK_DEFAULT_BUCKETS`
    constant (with its `traefik --help` provenance) and an `is_custom` pin asserting EXPECTED
    differs from it; the length pin is now printed separately from the ordering pin so a RED names
    which one fired. The two-hop block slice and the M6/M7 location mutations are kept as-is, per
    the review. Structure otherwise untouched.

  RUNTIME DIFFERENTIAL — the evidence whose absence caused the rejection
  (`/var/tmp/buckets-diff/run.sh`): two live traefik:v3.7.5 containers, identical config except the
  `buckets` key, real requests on a real entrypoint, both scraped at `/metrics`:
      CONTROL   (no buckets key)  le= 0.1 0.3 1.2 5 +Inf
      TREATMENT (this change)     le= 0.005 0.01 0.025 0.05 0.1 0.15 0.25 0.4 0.6 1 2.5 5 10 +Inf
  DIFFER. The key is observable at runtime, so Step 1b (`task-1785290391-b51a`) is now falsifiable:
  `le="0.005"` and `le="0.025"` cannot appear in live Prometheus without this change.

  MUTATION BATTERY 13/13 as designed (`logs/mutation-step01a-traefik-buckets.log`), template and
  test both restored byte-exact (both sha256s re-checked, `write_text` throughout, never `copy2`).
  M1–M10 carry over (values, ordering, length, the M6/M7 location-only mutations, M8/M9 polarity
  controls, M10 premise pin). NEW:
  - M11 — the rejected defect reintroduced as a SELF-CONSISTENT template+constant pair (both set
    to Traefik's default). Every template-side pin is satisfied; RED on `is_custom=False`.
  - M12 — M11's compositional pair (mem-1785128183-323c): same mutation but with
    `TRAEFIK_DEFAULT_BUCKETS` also neutered → GREEN, which proves `is_custom` and nothing else is
    the pin that sees M11.
  - M13 — length pin relaxed in the constant + a boundary dropped from the template → RED on
    `expected_len=False` with `expected_ascending=True`, so the two pins fail distinguishably.

  GATE: `just test` **GATE PASS 35/35 exit 0** (`logs/gate-step01a-traefik-histogram-buckets.log`),
  31/31 in this file.

  TREE: only the two in-scope files plus the two logs. The plex-optimization carry-over
  (`docs/runbooks/plex-latency-baseline.md`, `scripts/test_plex_latency_runbook_shape.py`,
  `logs/gate-step01-baseline-runbook.log`, `docs/plex-remote-latency-audit.md`, `ralph.agy.yml`)
  was already modified when this iteration started and is untouched. No commit (Builder preset).

  STILL NOT DONE, by design: no playbook run, no live Prometheus query. `traefik.yml` is the STATIC
  config — the file provider's `watch: true` governs `dynamic.yml` only — so these buckets need a
  container restart to reach the running proxy. Repo-green is not deploy-green; that remains Step
  1b, operator-only.

### Step 1a — REWORK round 4 (review.rejected, task-1785290378-db09)

REJECTION UPHELD, and I re-derived the load-bearing fact myself rather than reading the payload.
Rejection was: the buckets were calibrated against client-side TTFB, a quantity
`traefik_entrypoint_request_duration_seconds` does not contain.

CALIBRATION HARNESS (`/var/tmp/builder-buckets4/run.sh`, re-runnable and self-cleaning; output at
`logs/calibration-step01a-server-side-duration.log`): traefik:v3.7.5 on TLS, a backend with
controllable think-time (`?sleep=`) and body size (`?bytes=`), an asyncio TCP proxy injecting
100 ms RTT in front. Every leg scrapes bucket **and `_sum`/`_count`** before/after and reads the
delta, so the reported mean is bucket-independent.

  A. does the metric contain the NETWORK in front of Traefik?  — NO
     | leg                          | client TTFB | recorded server-side mean |
     |---|---|---|
     | instant backend, no WAN delay |  41.2 ms | 0.392 ms |
     | instant backend, +100 ms RTT  | 151.0 ms | 0.379 ms |
     | backend 200 ms, no WAN delay  | 241.2 ms | 200.542 ms |
     | backend 200 ms, +100 ms RTT   | 351.4 ms | 200.540 ms |
     Rows 3/4: client TTFB differs by 110 ms, recorded mean identical to three decimals.

  B. does the metric contain the RESPONSE WRITE? — YES, but only past the socket buffers.
     4 MB to a slow reader recorded 3.6 ms (buffers absorbed it, client took 1161 ms);
     16 MB at ~2 MB/s recorded **6.96 s** server-side against 8.44 s at the client.
     This is what justifies the multi-second tail, and it is a stronger claim than the
     rejection assumed — client backpressure IS visible here for streaming responses.

VALUES `[0.00025, 0.0005, 0.001, 0.0025, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 1.0, 5.0, 30.0]`.
Took the Critic's suggested shape but moved the floor one boundary lower: measured, an
empty-backend request through this proxy records 0.392 ms mean (0/20 under 0.25 ms, 19/20 under
0.5 ms) and this repo's LAN capture puts direct-to-Plex `/identity` at 0.327 ms median — so a
0.0005 floor would have buried every `/identity` in bucket one, which is the exact defect being
fixed, two orders down.

COMMENTS: both now state what the series does and does NOT include (`does NOT include TCP
connect, the TLS handshake, or client transit`) and cite the measurement, not the client-side
numbers. The false client_golang/`+9.4 ms`/`157-293-486 ms` rationales are gone from both files.

REAL-ARTIFACT PROOF (the corollary from round 3): rendered `traefik.yml.j2` through Jinja and
booted traefik:v3.7.5 on the rendered file with real traffic — starts clean, 0 static-config
errors, emits `le= 0.00025 0.0005 0.001 0.0025 0.005 0.01 0.025 0.05 0.1 0.25 1 5 30 +Inf`.
`le="0.00025"` cannot exist under Traefik's default 0.1/0.3/1.2/5.0, so Step 1b stays falsifiable.

MUTATION BATTERY 13/13 as designed (10 RED / 3 GREEN, `logs/mutation-step01a-traefik-buckets.log`),
both files restored byte-exact. The battery itself was retargeted: it now derives the
`EXPECTED_BUCKETS` literal by regex instead of hardcoding it in three places — the hardcoded
literal is precisely how it would have gone stale on a retune.

GATE: `just test` **GATE PASS 35/35 exit 0** (`logs/gate-step01a-traefik-histogram-buckets.log`),
31/31 in this file. Template sha256 `88b3160a…`, test sha256 `2ecd09f4…`.

UNCHANGED, by design: no `just play`, no live Prometheus query — static config needs a container
restart. Repo-green is not deploy-green; Step 1b remains operator-only.


---

## 2026-07-29 — Step 1a ROUND 5 (review.rejected: guard SCOPE — existence, not just values)

Active task: task-1785290378-db09 (`code-assist:plex-monitoring:step-01:traefik-histogram-buckets`).
Round 4's rejection is upheld and closed. Values, both calibration rationales, the two-hop slice,
`_bucket_values`, `is_custom` and the M11/M12 pair were ACCEPTED and are untouched (DEC-029).

DEFECT: the check pinned the BOUNDARIES of a series whose EXISTENCE nothing pinned. Confirmed as
stated — before this change `addEntryPointsLabels: true -> false` was PASS 31/31 and GATE PASS
35/35 with zero `traefik_entrypoint_*` series live.

FIX 1 — four existence pins inside the check that already slices the block, each its own printed
field (`entrypoint_labels`, `service_labels`, `entry_point`, `port_agrees`). `port_agrees` derives
BOTH sides — the port of the entrypoint named by `metrics.prometheus.entryPoint`, and the port
prometheus.yml.j2's `traefik` scrape job targets — so it is an agreement, not a hardcoded 8082.

FIX 2 — the template comment's false claim narrowed: Traefik's default puts every NON-STREAMING
request in its first bucket. Its top boundary is 5.0 and line B3 of
`logs/calibration-step01a-server-side-duration.log` records 6961.43 ms server-side for a 16 MB body
to a ~2 MB/s reader, i.e. `+Inf`. The comment now names that number and that log line.

RUNTIME EVIDENCE, measured not argued (`logs/calibration-step01a-emission-surface.log`) — real
rendered `traefik.yml.j2` through Jinja, traefik:v3.7.5, real TLS traffic, scraped on :8082, the
exact port the scrape job targets:

  | variant                                | scrape | entrypoint_bucket | service_bucket |
  |---|---|---|---|
  | V0 CONTROL pristine                    | ok :8082    | 14 | 14 |
  | V1 addEntryPointsLabels -> false       | ok :8082    |  0 | 14 |
  | V2 addServicesLabels -> false          | ok :8082    | 14 |  0 |
  | V3 `entryPoint: metrics` deleted       | ok :8082    |  0 |  0 |
  | V4 metrics address :8082 -> :8083      | UNREACHABLE |  0 |  0 (14 on :8083) |

  Every row `status=running restarts=0`, so none of these is a broken container: the other
  histogram surviving at 14 is the control that makes each one a LOST SERIES. V3 is the quietest —
  Traefik falls back to its default entrypoint name `traefik`, :8082 still answers, and both
  families are gone from it.

MUTATION BATTERY 24/24 as designed, 18 RED / 6 GREEN (`logs/mutation-step01a-traefik-buckets.log`),
all three files restored byte-exact by sha256. New rows: M14/M15 (each label flip, RED on its own
field alone), M16 (`entryPoint` deleted), M17 (moved to `websecure`), M18 (value blanked), M19
(endpoint port moved), M21 (scrape target moved), plus three controls/pairs — M20 (BOTH ends moved
together -> GREEN, which is what proves `port_agrees` is an agreement), M22 (`True` vs `true` ->
GREEN, the pin sees the value not the bytes) and M23/M24 (entrypoint renamed self-consistently at
the same port -> RED, and GREEN once the name clause alone is relaxed, so that clause is not
decorative). The battery now mutates prometheus.yml.j2 as a third file.

STATED PLAINLY, because two of these pins are stricter than the runtime: the label switches default
to `true` in Traefik, so deleting them still emits, and a both-sides rename at the same port is
runtime-equivalent. They are pinned anyway to keep the emission surface explicit in the file;
`port_agrees` is the pin carrying the actual runtime contract. The docstring says so.

GATE: `just test` **GATE PASS 35/35 exit 0** (`logs/gate-step01a-traefik-histogram-buckets.log`),
31/31 in this file. sha256 — template `73ddf123…`, test `c267dffb…`, prometheus.yml.j2 unchanged
at `3d94ba6c…`.

HARNESS TEARDOWN, verified after the fact and not by a line the harness prints: `docker ps -a`,
`pgrep`, `ss` all zero. The first run of my own harness DID leak its backend on :19000 — `cd $D;
nohup python3 backend.py` leaves a relative cmdline that `pkill -f "$D/backend.py"` cannot match,
which is exactly how the last two rounds leaked theirs. Fixed in the script and re-run clean.

UNCHANGED, by design: no `just play`, no live Prometheus query — static config needs a container
restart. Repo-green is not deploy-green; Step 1b remains operator-only.

## Step 1a — ROUND 6 (review.rejected → the HOST field of the endpoint address)

Active task `task-1785290378-db09` / key `code-assist:plex-monitoring:step-01:traefik-histogram-buckets`.
Round 5's `port_agrees` derives both ends of the PORT contract and throws the HOST away, so the
metrics endpoint can move off the network the scraper is on with nothing reddening.

REPRODUCED FIRST, not read: with the round-5 check, `address: ":8082"` -> `"127.0.0.1:8082"` is
`PASS 31/31 rc=0` with `port_agrees=True`. The battery row for it (M25) came back
`expected=RED got=GREEN`. A second row came back red-when-it-should-be-green: M27 (`"[::]:8082"`)
printed `port_agrees=False (metrics:None ...)` — the old regex could not parse the bracketed IPv6
form at all, so it was ALSO a false RED on a benign config.

FIX, test-side only (`scripts/test_traefik_config_shape.py`); the template is untouched this round:
`_entrypoint_port` -> `_entrypoint_address`, returning `(host, port)`; the `\[...\]` alternative
comes first so the IPv6 form's own colons are not read as the port separator. New pin
`peer_reachable` — `ep_host in PEER_REACHABLE_HOSTS` (`""`, `0.0.0.0`, `[::]`) — printed as its own
field with the offending host quoted, so a RED names which pin fired.

MEASURED, not asserted (`logs/calibration-step01a-bind-host.log`). traefik:v3.7.5 on the rendered
artifact, real TLS traffic through `websecure` to a real nginx backend, scraped FROM A PEER
CONTAINER BY SERVICE NAME — the network position Prometheus actually occupies:

  variant                     container    websecure  own_loopback  peer_scrape  ep_bucket  svc_bucket
  V0 CONTROL  address ":8082"  running/r0     200          200          200         14         14
  H1          "127.0.0.1:8082" running/r0     200          200          000          0          0
  H4          "0.0.0.0:8082"   running/r0     200          200          200         14         14
  H6          "[::]:8082"      running/r0     200          200          200         14         14

H1 is the argument: the proxy is healthy AND the endpoint exists on the right port AND answers
itself — only the peer gets nothing. H4/H6 are why this is a host CLAUSE and not a ban on host
prefixes; H6 also settles the open question the allow-list would otherwise assert, since `[::]` had
never been booted. The docker-provider error line is common-mode across all four including the
control (no socket mounted) and explains none of the differences; recorded as an addendum.

MUTATION BATTERY 27/27 as designed, 19 RED / 8 GREEN (`logs/mutation-step01a-traefik-host.log`),
all three files restored byte-exact by sha256. Three new rows: M25 (loopback bind alone -> RED on
`peer_reachable` ONLY, every other field still True), M26 (`0.0.0.0` -> GREEN, the prescribed
polarity control), M27 (`[::]` -> GREEN, the third member of the allow-list — an unexercised member
is an unproven clause). A parse table over nine address forms is appended to the calibration log;
`[::1]`, the IPv6 twin of the defect, reddens for free, which a denylist of `127.0.0.1` would not.

GATE: `just test` **GATE PASS 35/35 exit 0** (`logs/gate-step01a-traefik-host-clause.log`), 31/31
in this file. sha256 — test `63d8cca5…`, template unchanged from round 5 at `73ddf123…`,
prometheus.yml.j2 unchanged at `3d94ba6c…`.

DOCSTRING CORRECTED where the rejection falsified it: "`port_agrees` is the pin carrying the actual
runtime contract" was the sentence the loopback bind disproves. It now names `port_agrees` and
`peer_reachable` together, because an address has more than one field.

TEARDOWN verified after the fact: containers 0, networks 0, ports 0, host helpers 0 — every probe
ran in a container, so there was nothing to leak. Note for the next hat: a bare `pgrep -fc <tag>`
reads 3 because it matches its own command line; `pgrep -af` to read WHICH, not just how many.

UNCHANGED, by design: no `just play`, no live Prometheus query — static config needs a container
restart, and Step 1b remains operator-only. Values, both calibration rationales, the two-hop slice,
`_bucket_values`, `is_custom`, M11/M12, M20 and M23/M24 untouched (DEC-031). `manualRouting: true`
left out of scope as recorded: it requires ADDING a key and serves 404, which marks the Prometheus
target DOWN rather than silently empty.

---

## 2026-07-29 — FINALIZER, Step 1a (task-1785290378-db09) — CLOSED, wave NOT exhausted

Verified independently rather than from the review payload.

**Repo signal, re-run by me.** `just test` → **GATE PASS 35/35 exit 0**
(`logs/gate-finalizer-step01a.log`); `scripts/test_traefik_config_shape.py` standalone
**PASS 31/31 exit 0**. All three sha256s match the payload and are unchanged by my pass:
test `63d8cca5…`, template `73ddf123…`, `prometheus.yml.j2` `3d94ba6c…`.

**Deploy path confirmed real** (Step 1b depends on it and nobody had checked it from the
role side): `docker_host/tasks/main.yml:73-78` renders `traefik.yml.j2` and carries
`notify: Restart traefik`; `handlers/main.yml` runs `docker compose restart traefik`. So
`just play` does land a STATIC-config change. Step 1b is executable.

**ADVERSARIAL PASS — the finding, and it is the reason this is not `LOOP_COMPLETE`.**
I did not re-review the diff (six rounds did that). I attacked the only path that delivers
Step 1's user-facing outcome: the operator gate `task-1785290391-b51a`. Its acceptance
criteria were STALE AND INVERTED IN BOTH DIRECTIONS against the shipped ladder:

* Step 4 told the operator to confirm `le="0.1"`, `le="0.3"`, `le="1.2"`, `le="5.0"`.
  `0.3` and `1.2` DO NOT EXIST in the shipped config — they exist only in Traefik's
  default. An operator confirming them would have been confirming the change did NOT land.
* The same step called `0.005/0.01/0.025` "Go's default ladder" and told the operator to
  treat them as disqualifying. Those are three of the SHIPPED boundaries. Following the
  text literally, a SUCCESSFUL deploy reads as a failure.
* Step 5's "at or under `le="0.3"`" names a boundary that does not exist; nearest is `0.25`.

This is the exact unfalsifiable-operator-check class the round-2 rejection was about
(mem-1785290923-21b0): the task text was written against the pre-rejection values and never
followed the six rounds of retuning. Repo-green would have been handed to the operator with a
checklist that inverts the verdict.

FIXED via `task ensure --key …` (idempotent, same ID `task-1785290391-b51a`, description
replaced and re-read to confirm). The gate now names ONE decisive falsifier — `le="0.00025"`,
which cannot exist under Traefik's 0.1/0.3/1.2/5.0 default — states the full 14-label ladder,
spells out what FAILURE looks like (exactly 0.1/0.3/1.2/5.0/+Inf and nothing else = the restart
did not take), corrects the plausible-bucket bound to `le="0.25"`, and warns that this series is
server-side handler duration so it must not be compared against browser TTFB. The stale
`[0.1, 0.3, 1.2, 5.0]` demo at the top of this file was corrected the same way.

**Wave is NOT exhausted → `queue.advance`, not `LOOP_COMPLETE`.**
* `task-1785290391-b51a` (Step 1b) is now unblocked and READY — open, operator-only, and the
  loop parks here exactly as this file predicted. Step 1's Demo is NOT yet delivered.
* Steps 2, 3 and 4 of `plan.md` remain, none materialized as tasks. Planner owns that wave
  creation; I did not create them.

**Not run, by design:** no `just play`, no live Prometheus query. Both are Step 1b and
operator-only. Tree carry-over from plex-optimization untouched. No commit (Finalizer).

---

## 2026-07-29 — Builder, Step 2a (task-1785324219-b403) — pve-exporter wired repo-side, GREEN

Four template/defaults edits and four new checks in `scripts/test_traefik_config_shape.py`.
No `just play`, no live query, no vault value, no commit. Step 1b untouched.

**RED first** (`logs/red-step02a-pve-exporter.log`): the four new checks registered in `main()`
and run against the unmodified templates → `FAIL: 4/35`, each for its own reason
(`present=False`, `metrics_path=None`, `env_from_vault=False`, `host=None`), with the 31
pre-existing checks still green. Then the templates, then `PASS: 35/35`.

**What landed:**
* `defaults/main.yml` — `docker_host_pve_exporter_image: prompve/prometheus-pve-exporter:3.9.0`
  (three-part, so `test_no_floating_service_image_tags` stays green — proven by mutation M23),
  plus the three NON-secret coordinates: `docker_host_pve_api_host: 192.168.1.50`,
  `docker_host_pve_user: prometheus@pve`, `docker_host_pve_token_name: prometheus`.
* `env.j2` — `PVE_TOKEN_VALUE={{ vault_pve_api_token | default('') }}`, following
  `CF_DNS_API_TOKEN`/`TUNNEL_TOKEN` exactly.
* `compose.yml.j2` — `pve-exporter`, scrape-only: no labels, no ports, `restart: unless-stopped`,
  `PVE_USER`/`PVE_TOKEN_NAME` from the role defaults, `PVE_TOKEN_VALUE=${PVE_TOKEN_VALUE:-}`
  from the sibling `.env`, `PVE_VERIFY_SSL=false`, `command: [--no-collector.config]`.
* `prometheus.yml.j2` — the multi-target job: `metrics_path: /pve`, `params: {cluster: ['1'],
  node: ['1']}`, target `{{ docker_host_pve_api_host }}`, and the three relabel hops
  (`__address__` → `__param_target`, `__param_target` → `instance`, `__address__` →
  `pve-exporter:9221`).

**The guard** (4 checks, 31 → 35 inside the file): `test_pve_scrape_job_is_multi_target`
(the sharp one), `test_pve_exporter_service_block`, `test_pve_token_sourced_from_vault`,
`test_pve_non_secret_coordinates_in_defaults`. Two clauses are agreements rather than
duplicated literals, in the shape of Step 1a's `port_agrees`: the compose `${...}` name is
derived from the same `PVE_TOKEN_ENV` env.j2 assigns (renaming one side alone reddens, M18),
and the defaults' API host is checked against `mise.toml`'s committed `PROXMOX_VE_ENDPOINT`
rather than pinned twice (M19).

**MUTATION BATTERY — 23/23 reddened** (`logs/mutation-step02a-pve-exporter.log`; driver kept at
`logs/mutation-step02a-driver.py`, re-runnable, restores every file it touches and re-asserts
green at the end). Each mutation is applied to the pristine tree, the guard is run standalone,
and the check that reddens is recorded by name. The decisive one is first: **deleting
`metrics_path: /pve` reddens the gate**, as does writing the default `/metrics` explicitly, as
does dropping `cluster=1` — the three spellings of the no-op DEC-036 caught in `plan.md`.
Also covered: pointing the target at the exporter instead of the PVE host, dropping either
relabel hop, renaming the job, adding a Traefik label or a published port, dropping `PVE_USER`,
flipping `PVE_VERIFY_SSL` back to `true`, inlining the token as a literal, dropping
`default('')`, pointing env.j2 at a non-vault key, and leaking a `vault_*` value into the
plaintext defaults.

**The battery found a real vacuity in my own guard, first run.** Deleting the
`command: [--no-collector.config]` entry left the gate GREEN: the check matched free text over
the raw service block, and the COMMENT one line above names the flag it documents. So the check
was satisfiable by its own documentation. Fixed by adding `_strip_comments` and re-anchoring
every clause of the compose checks on a real YAML entry (`^\s*-\s*--no-collector\.config$`).
Same defect class as the Step 1 `is_custom` clause — a check that cannot distinguish the state
it exists to forbid — caught here by mutation rather than by review.

**Verification commands, all re-run by me this iteration:**
* `python scripts/test_traefik_config_shape.py` → `PASS: 35/35` (baseline was 31/31).
* `just test` → **`GATE PASS: 35/35 steps`, exit 0** (`logs/gate-step02a-pve-exporter.log`),
  including `ansible-lint --offline --profile production` and `ansible-playbook --syntax-check`.
* `python logs/mutation-step02a-driver.py` → `BATTERY PASS: 23/23`, tree restored green.
* Render check → `RENDER PASS` (`logs/render-step02a-pve-exporter.log`, driver at
  `logs/render-step02a-driver.py`). See below.

**Correction to this task's acceptance criteria, stated rather than quietly ignored.** The task
predicted "both totals should rise (35/35 gate steps and 31/31 inside the file)". The INNER
total rose 31 → 35 as expected. The GATE total did NOT and structurally cannot: `run_gate.py`
counts `len(glob("scripts/test_*.py")) + 5`, so it moves only when a new shape-test FILE is
added, and this step correctly extends the file that already owns `compose.yml.j2` and
`prometheus.yml.j2` (as the task itself instructed). Adding a file to move a counter would be
the wrong trade. `GATE PASS: 35/35` here is the same 35 as the baseline, with four more checks
inside step 30.

**Adversarial pass — what `just test` cannot see.** The gate never RENDERS these templates:
`ansible-lint` and `--syntax-check` read playbooks and roles, not `.j2` output. So a YAML error
or a Jinja typo in the new blocks would pass the whole gate and surface only during the
operator's `just play` in Step 2b — the worst possible place, since that is the run nobody here
can repeat. Closed with `logs/render-step02a-driver.py`: renders all three templates with the
real role defaults (`trim_blocks`/`lstrip_blocks`, `ChainableUndefined`), `yaml.safe_load`s
them, and asserts on the PARSED structure — `job["metrics_path"] == "/pve"`,
`params["cluster"] == ["1"]`, `targets == ["192.168.1.50"]`, both relabel hops, the service
having no `labels`/`ports` key at all, and the Step-1 `traefik` job still on `traefik:8082`.
It also renders BOTH sides of the 2a/2b split explicitly: with `vault_pve_api_token` UNDEFINED
the line renders `PVE_TOKEN_VALUE=` (empty) — the separability claim this whole task rests on,
now measured rather than asserted — and with it defined the value is carried through.
One assertion of mine was wrong there (I expected 9 compose services; there are 9 pre-existing
plus pve-exporter = 10) and I corrected the assertion, not the code.

**Expected pre-2b runtime state, so it is not read as a regression:** with the vault key absent
`.env` carries an empty `PVE_TOKEN_VALUE`, so after any `just play` before 2b the `pve-exporter`
container starts and its Prometheus target is DOWN/401. That is correct and intended; 2b is what
makes it green.

**Not done, by design:** no `just play`, no live Prometheus query, no vault value, no commit,
Step 1b (`task-1785290391-b51a`) not touched, not started, not closed. Working-tree carry-over
from plex-optimization untouched. **Nothing in this objective is committed.**

## 2026-07-29 — Step 2a REWORK (review round 2: F1 blocker + F2 + F3)

`review.rejected` reproduced first, then fixed. All three findings were in what the round-1
increment did NOT check, and all three are now checked.

**F1 (blocker) — nothing delivered the rendered config, and the fix needed a second change the
review did not name.** `tasks/main.yml` rendered `prometheus.yml` with no `notify:`, and
`handlers/main.yml` had only `Restart traefik`. Fixed with `notify: Restart prometheus` plus a
handler mirroring the traefik one — and with `mode: "0640"` → `"0644"`, which is the part worth
reading twice. Proving the fix end to end surfaced it: `prom/prometheus:v3.12.0` runs as
`nobody` (uid 65534, `docker run --entrypoint id`), so it cannot open a 0640 root:root config;
it exits on `Error loading config … permission denied`, and `restart: unless-stopped` makes that
a crash loop. ~~**The restart is what makes an unreadable config LOUD** — before it, the file was
never re-read and the mode never mattered.~~ **STRUCK 2026-07-29 (round 3): false.** `restart:
unless-stopped` had been re-reading that file every ~60 s all along, and production proves it —
`stack-prometheus-1` `Restarting`, RestartCount 20801 since 2026-07-15. The 0644 is a repair of a
live outage, not a consequence of the new handler; see the round-3 entry below. The rest of the
paragraph stands. 0644 is safe:
the scrape config carries no credential (the PVE token is an env var out of the 0600 `.env`).
Traefik's renders stay 0640 because that container runs as root, and the guard pins the two modes
per row rather than as one literal (DEC-038).

**Evidence, live, not argued — `logs/delivery-step02a-driver.py`, output in
`logs/delivery-step02a-f1.log`.** Three legs against a real `prom/prometheus:v3.12.0` on the
RENDERED artifacts, with the REAL task extracted verbatim from `tasks/main.yml` and the REAL
`handlers/main.yml` imported into a play (only `owner`/`group: root` → the unprivileged user is
rewritten, and the harness prints the rewrite):

* **A — the blocker still reproduces.** Boot on the pre-2a config, land the 2a config, run the
  role's own `docker compose up -d --remove-orphans`: same container id, same `StartedAt`, job
  set UNCHANGED, no `pve-exporter` job. `POST /-/reload` → **403**.
* **B — the fix delivers.** `RUNNING HANDLER [Restart prometheus]`, `changed=2`, `StartedAt`
  moves, and the job is live in `/api/v1/status/config` with `metrics_path: /pve`. The target
  Prometheus builds is
  `http://pve-exporter:9221/pve?cluster=1&node=1&target=192.168.1.50` — the multi-target shape,
  read off a running Prometheus rather than off the template.
* **C — it stays idempotent.** Second run: `changed=0`, the handler does NOT fire, `StartedAt`
  unchanged. A handler that fires every run would redden the role's idempotency scan.

One near-miss worth recording because it is the same class as the defect: the harness's first
run had the handler reporting `changed` while nothing restarted. The handler runs a bare
`docker compose restart prometheus` and derives the project name from its `chdir`, and the
harness was passing `-p` a different name — `restart` against a project with nothing running is
a silent **rc 0** no-op. In the role the two agree (both are the project dir), but "the command
exited 0" was again not the same claim as "the thing restarted".

**F2 — the guard's self-declared sharpest check was a runtime no-op, and the claim was in six
places.** `params: {cluster: ['1'], node: ['1']}` are the exporter's OWN defaults
(`on_pve(module='default', target='localhost', cluster='1', node='1')` in the shipped image).
The params are KEPT — explicit beats implicit against a default upstream may move, and it matches
upstream's README — and every sentence calling them load-bearing is corrected: the guard
docstring, the `PVE_REQUIRED_PARAMS` comment, the `prometheus.yml.j2` comment, the
`compose.yml.j2` comment, task 2a, task 2b's failure list, and `plan.md`'s reference facts
(corrected in place, struck through with the reason, per the rule that keeps the old bucket
numbers). The docstring now names which pins carry the runtime contract — `metrics_path: /pve`
and the `__param_target` relabel (`target` defaults to `localhost`) — and labels the params as
stricter than the runtime, the same honesty rule Step 1a's `entry_point` clause uses. The two
battery rows that mutate the params are kept and RECLASSIFIED `strict`, not deleted: they prove
the clause sees the file, and the label is what stops the claim re-deriving.

**F3 — authentication was the one thing pinned nowhere.** Deleting
`- PVE_TOKEN_NAME={{ docker_host_pve_token_name }}` from compose left the round-1 guard PASS
35/35, while the real image answers `/pve` with HTTP 500 "No valid authentication credentials
were supplied". Fixed as an AGREEMENT rather than another literal: `PVE_DEFAULT_VARS` maps env
var → role-defaults var and is read by both the compose check and the defaults check, copying
`port_agrees`. That closes the realm hole in the same clause — `PVE_USER=prometheus` with the
realm stripped in COMPOSE was green under the old `PVE_USER=\S+` regex, because the realm was
only ever checked on the defaults side.

**Verification, all re-run this pass:**

| what | result | log |
| --- | --- | --- |
| `just test` | `GATE PASS: 35/35 steps`, exit 0 | `logs/gate-step02a-rework-f1.log` |
| standalone guard | `PASS: 36/36` (was 35 — one new check) | — |
| mutation battery | `BATTERY PASS: 36/36` (was 23) | `logs/mutation-step02a-rework-f1.log` |
| render + parse | `RENDER PASS` | re-run of `logs/render-step02a-driver.py` |
| live delivery | `DELIVERY PASS` (legs A/B/C) | `logs/delivery-step02a-f1.log` |

The battery now declares a verdict per row instead of assuming RED, so it can carry the
compositional pair: renaming the handler on BOTH sides self-consistently must stay **GREEN**
(else the clause pins the string `Restart prometheus`, not the task→handler agreement), while
moving either side alone is RED. Rows are classified `runtime` / `strict` / `guard` — 27 / 3 / 5
plus the one GREEN — so "the guard reddened" and "the deploy would have broken" stay distinct
claims. The row that fires `in_compose` alone renames the compose SERVICE and leaves the handler
untouched; read its reddened LIST, not just the exit code.

**Not done, unchanged from round 1:** no `just play`, no live Prometheus query, no vault value,
no commit. Step 1b (`task-1785290391-b51a`) not touched, not started, not closed. Working-tree
carry-over from plex-optimization untouched. **Nothing in this objective is committed.**

---

## 2026-07-29 — Step 2a REWORK round 3 (Builder, `review.rejected` → F1/F2/F3)

Task `task-1785324219-b403`, key `code-assist:plex-monitoring:step-02:pve-exporter-repo-wiring`.
Three findings, all three reproduced before being fixed, one of them by going and looking at the
live host rather than by reading the review's summary of it.

**F1 (blocker) — a restart is only the LAST hop of delivery.** The round-2 clause walked
task → notify → handler → compose service → mode and never asserted that the file the render
WRITES is the file the service MOUNTS and READS. Reproduced first, as the RED step: seven
mutations added to the battery, all seven **GREEN** against the round-2 guard
(`logs/mutation-step02a-driver.py`, first run of this round) — `dest` off the mount source, the
bind mount dropped, a different host file mounted there, `--config.file` naming a path nothing is
mounted at, the mount target moved while the flag stays, `notify:` buried inside the module args,
and traefik's config moved off its default container path.

Fixed as an **agreement**, the `port_agrees` shape already in this file. `RELOAD_CONTRACT` rows
became records carrying `service`, `mode`, `config_flag` and `default_path`; the check
(renamed `test_rendered_configs_reach_the_service_that_reads_them`) now derives the mount from the
render `dest` and then checks the flag **against that mount's own target**, not against a literal.
So moving the container-side path consistently stays GREEN and moving it on one side alone reddens
— the battery carries that compositional pair. Where the image takes no config flag the path IS
the contract, so traefik's row pins `default_path: /etc/traefik/traefik.yml` instead.
The `notify:` match is now anchored at the task's own key indent, because one indent deeper it is a
module arg that passes `ansible-lint --profile production` and `--syntax-check` and fails only at
the operator's `just play`.

**The silent one, measured rather than cited** — new leg D in `logs/delivery-step02a-driver.py`
(`logs/delivery-step02a-f1-round3.log`): with the bind mount dropped and everything else intact
(file rendered, 0644, notified, handler fired, container restarted), Prometheus comes up on the
image's own default config, `GET /-/healthy` -> 200, the job set collapses from
`['cadvisor','node-exporter','prometheus','pve-exporter','traefik']` to `['prometheus']`, and the
one surviving target reads **UP**. Nothing errors anywhere. That is the state the new `mounted`
pin forbids. Cross-check from production, which is the strongest evidence available: the live
container's `Cmd` is `['--config.file=/etc/prometheus/prometheus.yml']` and its `Mounts` include
`/opt/stack/prometheus/prometheus.yml -> /etc/prometheus/prometheus.yml` — exactly the agreement
the guard now derives.

**F2 (blocker) — the framing was false and live Prometheus has been down for two weeks.**
Confirmed independently, read-only, `ansible docker-host -m ansible.builtin.shell`:
`stack-prometheus-1` is `Restarting`, **RestartCount 20801**, created 2026-07-15, logging
`open /etc/prometheus/prometheus.yml: permission denied` once a minute; the file is `640 root:root`
and the container runs as `nobody`. So `restart: unless-stopped` had been re-reading that config
all along, "the mode never mattered before the restart" was wrong, and **2a's `0644` is the repair
of a live outage.** Corrected in the guard comment, `context.md`, `plan.md`, and struck in place
in the round-2 entry above (the old wording is kept — it is the record of the mistake).
Consequences drawn, not just the fact recorded:

* **Step 1b is now `--blocked-by` Step 2a** (DEC-039). Its deliverable is a Prometheus query and
  Prometheus does not start until 2a's mode change lands; running `just play` before then would
  restart into the same crash loop and fail the gate for a reason unrelated to Traefik's buckets.
* **Both operator tasks were rewritten** to lead with the outage: 1b now opens with the measured
  state, adds a "confirm Prometheus is actually up" step before any query, and its failure list
  leads with "the query page does not load" instead of sending David to Traefik's bucket config.
  2b gains a "know what this play also does" paragraph — it ends the outage, Grafana comes back at
  the same time, and the TSDB starts empty.

**F3 — three false runtime claims in comments, all now transcripts.** Measured against the shipped
`prompve/prometheus-pve-exporter:3.9.0` with an auth-enforcing PVE stub
(`logs/calibration-step02a-f3.py`, output `logs/calibration-step02a-f3.log`):

* (A) `PVE_USER` unset -> **not** "401s while the container stays up": `cli.py:110` opens
  `/etc/prometheus/pve.yml` unguarded, `FileNotFoundError` at startup, crash loop, no scrape.
* (B) token empty -> **HTTP 500**, not 401; container UP, restarts 0, target DOWN with
  `server returned HTTP status 500 INTERNAL SERVER ERROR`.
* (C) a claim nobody had checked, in `defaults/main.yml`: a realm-less `PVE_USER` does produce
  PVE's `401 Unauthorized` — but only in the exporter's own `docker logs`
  (`proxmoxer.core.ResourceException`). Prometheus sees the same HTTP 500 as a missing token, so
  the realm is *not* distinguishable from the metric side. Comment rewritten to say that.
* Control, same wiring with a realm and a secret the stub accepts: `/pve` -> 200 with
  `pve_up{id="lxc/110"} 1.0`, so the 500s above are auth-caused, not stub-caused.

**Verification.** `just test` **GATE PASS 35/35 exit 0** (`logs/gate-step02a-rework-f1-round3.log`);
guard standalone **36/36**; mutation battery **44/44 rows gave their declared verdict**, tree
restored, control green before and after (`logs/mutation-step02a-rework-f1-round3.log`); render
driver **RENDER PASS**; delivery driver **DELIVERY PASS** with the new leg D. Guard count stays 36
and the gate stays 35/35 steps — one check was widened, not added (`run_gate.py` counts files + 5,
DEC-037).

**Near-miss worth carrying.** The F3 calibration's first run reported leg C's status from leg B's
container: the legs share `--network host`, so a leftover container still holding `:9221` silently
answers the next leg's probe. The driver now removes every leg's container before each run. Same
class as round 2's "the command exited 0 is not the thing restarted" — a harness that measures the
wrong process reports a confident wrong number.

**Not done, unchanged:** no `just play`, no live Prometheus query, no vault value, **no commit**.
The only live access used was read-only (`ansible ... -m ansible.builtin.shell` with `docker ps` /
`docker logs` / `docker inspect` / `stat`). All harness containers, networks and volumes removed.
Working-tree carry-over from plex-optimization untouched. **Nothing in this objective is committed.**

## Step 2a — REWORK round 4 (`review.rejected` -> F1/F2), 2026-07-29

Both blockers were **guard-only**, as the review said: `scripts/test_traefik_config_shape.py` is
the sole file changed this round. No template, task, handler or default was touched.

**F1 — a clause that pins an ABSENCE must read both YAML spellings, and this one failed OPEN.**
`no_ports = re.search(r'(?m)^\s*ports:\s*$', block) is None` anchors the key to the end of its
line, so only the block spelling was visible to it.

* **RED step first** (`logs/red-step02a-rework-f1-round4.log`), six new battery rows against the
  round-3 guard: the inline `ports: ["9221:9221"]` on `pve-exporter` was **GREEN**, `ports: []` was
  **GREEN**, and the identical inline spelling on `cloudflared` — whose docstring promises "zero
  inbound surface" — was **GREEN**. The long block syntax (`- target: 9221`) and the short block
  form already reddened, and a *comment* naming the forbidden spelling correctly stayed GREEN.
* **Measured, not reasoned** (`logs/calibration-step02a-f1-round4.py`, output
  `…-round4.log`). Leg A: the evaded state renders, `yaml.safe_load`s to `['9221:9221']` and
  `docker compose config` returns **rc=0** — a DEPLOYABLE state, so `just play` would ship it
  rather than catch it. Leg B, on the real `prompve/prometheus-pve-exporter:3.9.0` with a **valid**
  token against an auth-enforcing PVE stub and the port published: an anonymous caller outside the
  container gets `/metrics` (57 lines) and `/pve?target=…` (154 lines) with
  `pve_up{id="lxc/110"} 1.0` and both guests, driving **14 PVE API calls made with the container's
  own credential for a caller that presented none**; pointing `target=` at TEST-NET-1 instead sent
  the exporter elsewhere, so the destination is caller-chosen. The exporter authenticates to PVE
  and nothing authenticates to the exporter.
* **Fix**: `_service_published_ports(service_block)` returns the entries in **either** spelling
  (flow list, short block list, long `- target:`/`published:` syntax) over the comment-stripped
  block, or `None` when the key is absent — and both clauses now read `published is None`. The pin
  is on the KEY: `ports: []` publishes nothing and still reddens. That is stricter than the runtime
  and the row is classified `strict`, because such a key has no reason to exist in a scrape-only or
  outbound-only service and is one edit away from one that publishes. Both `no_ports` fields now
  print `published=…` so a reader sees WHAT was found, not just a boolean.
* Why this was the increment's own defect and not a nitpick: every other flow-vs-block gap in this
  file fails **closed** (an inline `volumes:` makes `_indented_block` return "" and the delivery row
  goes RED), and `_service_command_args` — added by round 3 — handles both spellings and says so.
  The distinction was known, applied to `command:`, and missed on the one clause where it fails open.

**F2 — the sweep that deletes a false claim everywhere must include the guard.** Round 3's whole F3
was "three false runtime claims, now transcripts", corrected in `compose.yml.j2`, `env.j2` and
`defaults/main.yml` — and left verbatim in `test_pve_exporter_service_block`'s docstring ("without
`PVE_USER` every scrape 401s while the container stays up"). Replaced with the measurement:
`cli.py:110` opens a `/etc/prometheus/pve.yml` the image does not ship, `FileNotFoundError` at
startup, `restart: unless-stopped` makes it a crash loop — `State.Status=restarting`, RestartCount
8, curl exit 7 connection refused, no listener and no scrape at all.

Then swept the rest of the file rather than fixing only the named line: `user_realm`'s docstring in
`test_pve_non_secret_coordinates_in_defaults` still said a realm-less user "is a 401 that looks like
a bad token" — the same class of claim, and the same one `defaults/main.yml` already corrects.
Rewritten to F3(C) as measured: PVE answers 401, the exporter serves the scrape **HTTP 500**, so
Prometheus records the same `lastError` as a missing token and the realm is visible only in the
exporter's own `docker logs` — which is precisely why the clause is worth having.

**Verification.** `just test` **GATE PASS 35/35 exit 0** (`logs/gate-step02a-rework-f1-round4.log`);
guard standalone **36/36**; mutation battery **50/50 rows gave their declared verdict**, control
green before and after, tree restored (`logs/mutation-step02a-rework-f1-round4.log`); render driver
**RENDER PASS**; delivery driver **DELIVERY PASS** A–D (`logs/delivery-step02a-f1-round4.log`).
Check count stays 36 and the gate stays 35/35 — two clauses were widened, nothing was added.

**Harness near-miss, same family as the last two rounds.** The calibration's own teardown block
caught its own leak: `ThreadingHTTPServer.shutdown()` stops `serve_forever` but leaves the LISTEN
socket open, so `:8006` was still held after the run reported success. `server_close()` fixed it,
and the run only failed because the harness prints `ss -ltn` and `docker ps -a` **after** teardown
instead of printing a teardown line.

**Not done, unchanged:** no `just play`, no live Prometheus query, no vault value, **no commit**. No
live access at all this round — every measurement was local docker plus a stub. All harness
containers and listeners removed (evidence in the calibration log). Step 1b untouched.

---

## 2026-07-29 — Step 2a REWORK round 5 (`review.rejected` → F1/F2), task-1785324219-b403

Both findings were guard-only and the review was right that nothing in a template, task or handler
is implied: **`scripts/test_traefik_config_shape.py` is the only repo file this round touches**
(`compose.yml.j2` is sha256 `3fb4fa74…` before and after).

**F1 — the pin was on a KEY; the invariant is REACHABILITY.** Round 4 replaced a block-only
`ports:` regex with `_service_published_ports`, reading all three spellings compose accepts. That
fix is real, and it is still bounded by the enumeration behind it: `network_mode: host` declares no
`ports:` key at all, so `published` is `None`, `no_ports` is True and the guard passed 36/36.

RED step first, twelve rows against the round-4 guard
(`logs/red-step02a-rework-f1-round5.log`): **8 of 12 answered wrongly** — `network_mode: host`
(bare and quoted-value), `network_mode: service:traefik`, the same key on cloudflared, the quoted
key `"ports":` on both services, an `expose:` key and an explicit `networks:` membership were all
GREEN. Then measured the two claims the fix rests on instead of inheriting the review's summary
(`logs/calibration-step02a-f1-round5.log`):

* **Leg A — deployability.** Every evasion renders through Jinja, `yaml.safe_load`s with the key
  landing as a REAL service key (`pve-exporter.network_mode='host'`,
  `pve-exporter.ports=['9221:9221']`) and `docker compose config` returns **rc=0**. `just play`
  ships these; none is a syntax error the operator would catch.
* **Leg B — the runtime state, as a three-column table.** Same real
  `prompve/prometheus-pve-exporter:3.9.0`, same command, same env, ONE service key different.
  Compose network → peer reaches it at `172.19.0.2:9221` HTTP 200, **no `:9221` line in `ss -ltn`**,
  and an anonymous GET at this box's LAN address is **000**. `network_mode: host` → **`LISTEN
  *:9221` in the host netns** and the same anonymous GET is **HTTP 200, 3174 bytes**. The middle
  column is what separates "exposed" from "dead container": both rows are healthy.
* **Leg C — the mitigation, stated honestly.** Host networking also drops the service off the
  compose network: a peer resolving `pve-exporter:9221` **by name** gets 200 on the compose network
  and **000** under host mode, so the scrape breaks LOUDLY. That mitigates the MONITORING outcome
  and not the SECURITY one, and this clause is a security pin.

**The fix is a shape change, not another spelling.** An absence pin fails OPEN one key past its
enumeration — three rejections have now walked that edge outwards. `_service_keys()` reads the
service's own key column (derived from the block, unquoted via the new `_yaml_key`) and the clause
became an ALLOW-LIST: `SCRAPE_ONLY_KEYS` / `OUTBOUND_ONLY_KEYS`. It fails CLOSED — `network_mode`,
`networks`, `expose`, `hostname` and any compose key that does not exist yet all land outside it
without anyone having had to think of them first. Stricter than the runtime for the benign members,
and the constant's comment says so. Both fields now print the key set they saw
(`keys=[…], unexpected=[…]`), not a bare boolean.

**`no_ports` was kept, not replaced** — two pins that fail differently, and each is proven
SEPARATELY because a `ports:` mutation moves both at once (mem-1785132609-4175). Three
compositional rows: `ports:` + `ports` admitted to the allow-list → still RED (`no_ports` alone
sees it); `ports:` + `no_ports` dropped from the conjunction → still RED (`keys_allowed` alone sees
it); and the honest half — `network_mode: host` + `network_mode` admitted to the allow-list → back
to **GREEN**, which is what makes "`keys_allowed` is the only pin that sees the second door" an
argument rather than a claim.

**F2, and I swept the CLASS rather than the named line.** `_yaml_key` unquotes keys, so
`"ports":`/`'ports':` are read like any other spelling. Then grepped every absence pin in the file
for the same defect — a clause written `re.search(r'(?m)^\s*<key>:\s*$', …) is None` is blind to
the quoted key AND, because of the `\s*$`, to a key carrying an inline flow value. **Two more, both
outside the clauses the review named, both now RED and both previously GREEN:** `le-http` in FLOW
form (`le-http: {acme: {httpChallenge: …}}` is a whole second ACME resolver on one line, in the
check whose docstring claims `le-dns-cf` is the SOLE resolver), and a vaulted secret copied into
role defaults under a QUOTED key (`"vault_pve_api_token": …`), which is this step's own
plaintext-secret pin. Both go through the new `_declares_key`, and the polarity control — comments
naming both keys — stays GREEN.

**Verification.** `just test` **GATE PASS 35/35 exit 0** (`logs/gate-step02a-rework-f1-round5.log`);
guard standalone **36/36**; mutation battery **66/66 rows gave their declared verdict** (by class:
45 RED/runtime, 7 RED/guard, 6 RED/strict, 8 GREEN/guard), control green before and after and the
tree restored (`logs/mutation-step02a-rework-f1-round5.log`); render driver **RENDER PASS**;
delivery driver **DELIVERY PASS** A–D (`logs/delivery-step02a-f1-round5.log`). Check count stays 36
and the gate stays 35/35 — four clauses were widened, none was added.

**Harness safety.** The exporter that briefly held `*:9221` on this box ran with a deliberately
INVALID credential aimed at 192.0.2.1 (TEST-NET-1), so the listener put on the LAN could reach no
PVE at all. Probes came from throwaway containers at this box's LAN address, never `docker exec`
and never loopback — both of those reach a binding the measurement exists to distinguish. Teardown
evidence printed AFTER teardown: no `cal-r5` containers, no `cal-r5` networks, no socket on `:9221`.

**Not done, unchanged:** no `just play`, no live Prometheus query, no vault value, **no commit**. No
live host access at all this round. Step 1b untouched.

## 2026-07-29 — Step 2a REWORK round 6 (review.rejected → F1) — BUILT, `review.ready`

One finding, one fix, and the review was right that no template, task or handler change is implied:
**`scripts/test_traefik_config_shape.py` is the only repo file this round touches.** compose.yml.j2
sha256 `3fb4fa74…`, traefik.yml.j2 `73ddf123…`, defaults/main.yml `8fd98ed3…` — unchanged from the
critic's own reading, before and after.

**F1. The allow-list was bounded by its PARSER, and the parser failed OPEN.** Round 5 correctly
stopped enumerating forbidden keys and made both reachability clauses key allow-lists — but
`_yaml_key` reads only `[A-Za-z_][\w.-]*:` and `_service_keys` **silently DISCARDED** every line it
could not parse, so a key arriving without a parsable key LINE was invisible to the list that
claimed to catch "any compose key that does not exist yet".

RED step first, sixteen rows against the round-5 guard (`logs/red-step02a-rework-f1-round6.log`):
**10 of 16 answered wrongly.** Then measured rather than inherited
(`logs/calibration-step02a-f1-round6.log`): **leg A** — each of seven spellings renders,
`yaml.safe_load`s with `network_mode`/`ports` landing as a REAL service key, and `docker compose
config` returns **rc=0** with the key on the RESOLVED service, so `just play` ships it: merge key
`<<: *hostnet` off a top-level `x-` field, the same merge inline, YAML explicit-key `? network_mode`
/ `: host`, a Jinja-emitted key, `? ports`, and the merge key on cloudflared. **Leg A′** — the same
class one helper down: an explicit-key second resolver renders to `certificatesResolvers:
['le-dns-cf', 'le-http']` inside the check whose docstring calls `le-dns-cf` the SOLE resolver, and
an explicit-key `vault_pve_api_token` lands in plaintext role defaults past this step's own secret
pin. **Leg C** — the obvious fix really is unavailable: the gate interpreter
(`/home/user/Work/homelab/.venv/bin/python`) raises `ModuleNotFoundError` for both `yaml` and
`jinja2`.

**The fix refuses to guess instead of guessing more.** A fifth enumeration of spellings extends the
walk (one spelling → three → the key set → the parser); classifying every line and failing CLOSED on
the unreadable ones ends it. New `_line_class` returns `blank` / `doc` / `seq` / `key` /
`unreadable`; `_service_key_lines` returns `(keys, unreadable)` for the service's own key column and
both clauses redden on either; `_declares_key` returns REASONS (so the printed field says which line
answered) and reports any unreadable line in the body. `doc` and `seq` are named and exempted
because they carry no key by construction and both occur in the delivered tree. **Measured free
before prescribing it** (leg B): **0** non-key lines at the key column across all ten compose
services, **0** unreadable lines in traefik.yml.j2 and defaults/main.yml — zero false REDs.

**Each half proven SEPARATELY.** `keys_allowed` now has two terms and a bare RED cannot say which
answered — the same attribution problem round 5 solved one level up. Three compositional rows:
merge key + the `unreadable` half dropped → **GREEN** (the honest half: `unreadable` is the only pin
that sees it); merge key + the `unexpected` half dropped → still RED; and readable `network_mode:
host` + the `unreadable` half dropped → still RED, so round 6 completed round 5's pin rather than
quietly replacing it.

**Deployability in its strongest form.** The critic ran the FULL gate with the merge-key mutation in
the tree and got GATE PASS 35/35. Same mutation, same command, now: **GATE FAIL, exit 1**, naming
`keys_allowed=False (keys=[image, restart, environment, command], unexpected=[],
unreadable=['<<: *hostnet'])` — `logs/gate-step02a-rework-f1-round6-mutated.log`.

**Verification.** `just test` **GATE PASS 35/35 exit 0** (`logs/gate-step02a-rework-f1-round6.log`);
guard standalone **36/36**; mutation battery **81/81 rows gave their declared verdict** (by class:
53 RED/runtime, 9 RED/guard, 7 RED/strict, 12 GREEN/guard), control green before and after with the
tree restored (`logs/mutation-step02a-rework-f1-round6-battery.log`); RED-step rows re-run against
the fixed guard **16/16** (`logs/mutation-step02a-rework-f1-round6.log`); render driver **RENDER
PASS**; delivery driver **DELIVERY PASS A–D** (`logs/delivery-step02a-f1-round6.log`). Check count
stays 36 and the gate stays 35/35 — four clauses were widened, none was added.

**Harness safety.** No container was started to prove the exposure this round: round 5 measured what
`network_mode: host` does on the real image (LISTEN `*:9221` in the host netns, anonymous LAN GET
200) and the critic reproduced it on the merge-key spelling, so the leg this round owed was
deployability, which needs only `docker compose config`. The delivery driver's own containers tore
themselves down with the evidence printed AFTER teardown; `:9221` and `:8006` free, no harness
containers or networks.

**Not done, unchanged:** no `just play`, no live Prometheus query, no vault value, **no commit**. No
live host access at all this round. Step 1b untouched.

## Step 2a — REWORK round 7 (`review.rejected` → F1), 2026-07-29

**Scope: `scripts/test_traefik_config_shape.py` only.** No template, task or handler byte moved —
compose.yml.j2 `3fb4fa74…`, traefik.yml.j2 `73ddf123…`, dynamic.yml.j2 `097eca50…`, defaults
`8fd98ed3…`, identical before and after.

**F1. Round 6 made the line CLASSIFIER fail closed. The SLICER that decides which lines it sees
still failed SILENT.** Both block slicers ended a block at the next non-space GLYPH
(`(?=^\s{2}\S|^\S|\Z)` for a service, `(?=^\s{4}\S|\Z)` for a router). Two line shapes match such a
lookahead, carry no YAML key, and end no node at runtime — and both are this repo's own idiom: a
whole-line comment at the block's own column (compose.yml.j2 comments its service groups at 2 spaces
on lines 25/72/175/199 while bodies use 4; dynamic.yml.j2 comments its routers at 4 while bodies use
6) and a column-0 Jinja `{% if %}` (dynamic.yml.j2:84-89).

**RED step first, thirteen rows against the round-6 guard: 7 of 13 answered wrongly**
(`logs/red-step02a-rework-f1-round7.log`). Then measured rather than inherited
(`logs/calibration-step02a-f1-round7.log`): leg A — all five compose shapes render,
`yaml.safe_load` with the forbidden key on the REAL service, and `docker compose config` returns
rc=0 with it on the RESOLVED service, so `just play` ships them. Leg A′ — the same boundary one
helper over: an allowlist entry behind a 4-space comment inside the `plex` router renders to
`http.routers.plex.middlewares == ['security-headers@file', 'internal-allowlist@file']`, i.e. the
ONE public router silently becomes unreachable from the WAN. Leg C — the ruled-out fix re-confirmed
from my side: the gate interpreter has neither `yaml` nor `jinja2`.

**The fix is a boundary rule, in one place, and it is not another enumeration.** New
`_key_bounded_block(body, name, indent)`: strip whole-line comments BEFORE slicing, and terminate a
block only on a line `_line_class` reads as a KEY at `indent` or shallower. `_compose_service_block`
and `_router_block` become two-line wrappers around it (DEC-041 — the review named `_router_block`
without asking for it; measuring it first is what made the extension a finding rather than a guess).
Anything the parser cannot read now stays INSIDE the block and is judged by round 6's classifier,
which already fails closed on it — so the boundary fails CLOSED too: an over-run is a false RED, not
a silent truncation. **Measured free before prescribing it** (leg B): across all ten compose
services and all four routers the new blocks carry byte-identical content to the old ones and
introduce **zero** unreadable lines.

**No new field, and each pin proven separately** — a truncated-block mutation reddens a clause
holding three pins, so a bare RED attributes nothing. Four compositional rows: the readable
`network_mode: host` row + the OLD service slicer restored → **GREEN** (the honest half: the slicer
is the pin, round 6's classifier fully intact); the allowlist row + the OLD router slicer restored →
**GREEN**; the Jinja-gated row + round 6's `unreadable` half dropped → **GREEN**; the comment-hidden
row + the same half dropped → still **RED**. So round 7 reuses round 5's `unexpected` term and round
6's `unreadable` term and adds no constant of its own.

**Deployability in the form the critic used against me.** They ran the FULL gate with the
comment-then-`ports:` mutation in the tree and got GATE PASS 35/35 exit 0 while the clause printed
`keys_allowed=True … no_ports=True (published=None)`. Same mutation, same command, now: **GATE FAIL
exit 1**, the clause printing `keys_allowed=False (keys=[image, restart, environment, command,
ports], unexpected=['ports'], unreadable=[]), no_ports=False (published=['9221:9221'])` —
`logs/gate-step02a-rework-f1-round7-mutated.log`.

**Verification.** `just test` **GATE PASS 35/35 exit 0** (`logs/gate-step02a-rework-f1-round7.log`);
guard standalone **36/36**; mutation battery **96/96 rows gave their declared verdict** (by class:
59 RED/runtime, 10 RED/guard, 7 RED/strict, 20 GREEN/guard), control green before and after with the
tree restored (`logs/mutation-step02a-rework-f1-round7-battery.log`); RED-step rows re-run against
the fixed guard **13/13** (`logs/red-step02a-rework-f1-round7-after.log`); render driver **RENDER
PASS** (`logs/render-step02a-round7.log`); delivery driver **DELIVERY PASS A–D**
(`logs/delivery-step02a-f1-round7.log`, teardown clean). Check count stays 36 and the gate stays
35/35 — one helper added, two slicers rewritten as wrappers, no clause added.

**Harness safety.** No exporter container was started this round: rounds 5 and 6 and the critic have
all three measured what a published `:9221` and `network_mode: host` do on the real
`prompve/prometheus-pve-exporter:3.9.0` (LISTEN `0.0.0.0:9221`, anonymous LAN GET `/metrics` → HTTP
200, `target=` caller-chosen). The leg the Builder owes is deployability, and that needs only
`docker compose config`. The delivery driver's own containers tore themselves down with the evidence
printed AFTER teardown (`docker ps -a` empty, work dir removed).

**Not done, unchanged:** no `just play`, no live Prometheus query, no vault value, **no commit**. No
live host access at all this round. Step 1b untouched.

## Step 2a REWORK round 8 (task-1785324219-b403, `review.rejected` → F1) — BUILT

**Scope kept to the review's.** `scripts/test_traefik_config_shape.py` is the only repo file this
round touches. Templates and defaults byte-identical before and after: compose.yml.j2 `3fb4fa74`,
dynamic.yml.j2 `097eca50`, traefik.yml.j2 `73ddf123`, defaults `8fd98ed3`.

**F1. Round 7 fixed where a block ENDS; where it STARTS was never scoped.**
`_compose_service_block` handed `_key_bounded_block` the WHOLE compose document and took the first
2-space key of that name anywhere in it — the docstring said "under `services:`" and nothing
enforced it. A top-level `x-` extension field (compose-spec sanctioned, runtime-IGNORED, the same
idiom rounds 5–6 built their findings on) holding a decoy `pve-exporter:` became "the service".
No spelling is involved: the forbidden key is plain, readable and on the real service.

**RED step first**, eleven rows against the round-7 guard before touching it: **4 of 11 answered
wrongly** (`logs/red-step02a-rework-f1-round8.log`). Three were silent holes; the fourth was a
FALSE RED — a legitimate `tcp:` section carrying nothing forbidden reddened three presence clauses.

**Measured rather than inherited** (`logs/calibration-step02a-f1-round8.log`). Leg A: all three
compose rows render, `yaml.safe_load` with the forbidden key on the REAL service, and
`docker compose config` returns rc=0 with it on the RESOLVED service (`published: '9221'`,
`network_mode: 'host'`, cloudflared `9222`) while the `x-` decoy resolves to nothing. Leg A′: the
`tcp:` document parses as legitimate Traefik config and its rendered
`http.routers.plex.middlewares == ['security-headers@file', 'internal-allowlist@file']` — the ONE
public router off the WAN. Leg C: the ruled-out shadow re-confirmed from the Builder's side — a
DUPLICATE `pve-exporter:` under `services:` fools the unscoped anchor identically but compose-go
rejects it (rc=1, `mapping key "pve-exporter" already defined`), so the `x-` field is the shipping
form and the next round should not chase the duplicate.

**The fix is an anchor PATH, and it adds no constant and no spelling** — round 7's own helper one
level up. `_compose_services_block` (`services:` at column 0) feeds `_compose_service_block`;
`_http_block` (`http:` at column 0) feeds `_routers_block` and `_services_block`. The anchor rule
now sits beside the boundary rule in one commented block, and it fails CLOSED: an anchor that does
not resolve returns `""`, `present` goes False and the clause reddens — it never searches wider.
DEC-043 records the call to fix the `routers:` anchor the review named but did not demand; it was
measured first, and it turned out to cost on BOTH sides (silent hole *and* false RED), which is
what made it a finding rather than symmetry. **Measured free before shipping** (leg B): every
compose service block and every router block byte-identical in content, zero unreadable lines
introduced, and the three `*-data` keys under top-level `volumes:` correctly stop resolving as
services — no clause slices those.

**No new field, and each edge attributed separately.** The battery now carries one attribution pair
per edge: round 8's rows restore the UNSCOPED anchor with round 7's boundary fully intact → the
exposure comes back **GREEN** (service side ×2, router side ×1), so the anchor is isolated; round
7's rows restore its slicing whole. And `x-` decoy + `ports:` + round 6's `unreadable` half dropped
is still **RED**, so round 5's `unexpected` term is what answers and round 8 added no term.
The router rows are CLAUSE-SCOPED (new optional 5th field in the battery runner): with the unscoped
anchor the decoy reddens three PRESENCE clauses while the pin under test stays green, so a
whole-guard verdict would have called that hole "closed" for the wrong reason.

**Deployability in the form the critic used against me.** They ran the FULL gate with the `x-`
decoy + `ports:` mutation and reported `just test` rc=0 **GATE PASS 35/35** while
`docker compose config` resolved `published: '9221'`. Same mutation, same command, now **GATE FAIL
exit 1**, `1/35 step(s) failed`, the clause printing `keys_allowed=False (unexpected=['ports']) …
no_ports=False (published=['9221:9221'])` — `logs/gate-step02a-rework-f1-round8-mutated.log`, which
prints the template's sha256 before, during and after (`3fb4fa74` → `e8a68cd5` → `3fb4fa74`).

**Verification.** `just test` **GATE PASS 35/35 exit 0** (`logs/gate-step02a-rework-f1-round8.log`);
guard standalone **36/36**; mutation battery **107/107 rows gave their declared verdict** (63
RED/runtime, 11 RED/guard, 7 RED/strict, 26 GREEN/guard), control green before and after with the
tree restored (`logs/mutation-step02a-rework-f1-round8-battery.log`); RED-step rows re-run against
the fixed guard **11/11** (`logs/red-step02a-rework-f1-round8-after.log`); render driver **RENDER
PASS** (`logs/render-step02a-round8.log`); delivery driver **DELIVERY PASS A–D**
(`logs/delivery-step02a-f1-round8.log`, teardown clean). Check count stays 36 and the gate stays
35/35 — two anchor helpers added, three slicers rewritten as compositions, no clause added.

**Harness safety.** No container was started to re-prove the exposure — rounds 5, 6 and the critic
have all measured what a published `:9221` does on the real `prompve/prometheus-pve-exporter:3.9.0`
(LISTEN `0.0.0.0:9221`, anonymous LAN GET `/metrics` → HTTP 200, caller-chosen `target=`). The leg
the Builder owes is deployability, and that needs only `docker compose config`. The delivery
driver's own containers tore down with evidence printed AFTER teardown.

**Not done, unchanged:** no `just play`, no live Prometheus query, no vault value, **no commit**. No
live host access. Step 1b untouched.

## Step 2a REWORK round 9 (task-1785324219-b403, `review.rejected` → F1) — BUILT

**Scope: `scripts/test_traefik_config_shape.py` ONLY.** No template, task, handler or defaults change
is implied by this finding and none was made — compose `3fb4fa74`, prometheus `d2e5b364`, dynamic
`097eca50`, traefik `73ddf123`, env `b76d2ef8`, tasks `2e120676`, handlers `0e05058e`, defaults
`8fd98ed3`, identical before and after.

**F1 — the anchor rule was a claim, not a rule.** Round 8's header says *"THE ANCHOR RULE, IN ONE
PLACE … every slicer below names its parents and the column each one sits at."* Four slicers below it
named no parent, and `_scrape_job_block` — the slicer `test_pve_scrape_job_is_multi_target` is built
on — took the first `- job_name:` at ANY indent and did not strip comments.

RED step first, eleven rows against the round-8 guard, **5 of 12 answered wrongly**
(`logs/red-step02a-rework-f1-round9.log`): the review's three `external_labels` rows, a Jinja
`{% if %}/{% else %}` either-or pair of the SAME job that they did not claim, and the second
`static_configs` entry they measured and did not demand.

**Deployability, leg A** (`logs/calibration-step02a-f1-round9.log`): every RED row renders,
`yaml.safe_load`s and passes `promtool check config` on the real `prom/prometheus:v3.6.0` at
**rc=0**, and the log prints what Prometheus then LOADS — `metrics_path=None`,
`param_target_relabel=False`, and for the second-entry row `targets=['192.168.1.50',
'203.0.113.9']`. Those are states `just play` ships.

**The fix is the sweep, in two halves, and it adds no constant and no spelling.**
`_scrape_job_block` walks `scrape_configs:` at column 0 through round 7's own `_key_bounded_block`
(which strips comments, so the job body stops being satisfiable by its own nine-line comment);
`_indented_block` states that it is region-relative by construction; `_render_task_block` and
`_handler_block` state the column-0 document-root anchor they already had. Then the half a PATH
cannot answer — **an anchor that resolves to two nodes has not resolved** — because the Jinja pair
lives INSIDE the anchored region. Where the claim is UNIVERSAL the read goes plural instead
(`_indented_blocks`, one call site: `targets:`).

**Priced, not claimed free (leg B):** three of five job blocks byte-identical; `traefik` and
`pve-exporter` differ ONLY because `_key_bounded_block` strips comments; every anchored name in the
delivered tree — five job names, four `_indented_block` call sites, ten services' `volumes:`/
`command:`, nine render `src:`s, both handler names — resolves exactly **once**, so the fail-closed
rule costs zero false REDs today.

**Attribution, one relaxation per edge:** restore the UNSCOPED job anchor → the `external_labels`
decoy answers again (GREEN); restore first-match-wins with the path intact → the Jinja pair answers
again (GREEN); restore the singular `targets` read alone → **still RED**, because the fail-closed
half also sees it, so the isolation row relaxes BOTH and only then goes GREEN. And round 9 adds no
term: drop the clause's EXISTING `path_pinned` from the conjunction and the decoy row goes GREEN.

**Verification.** `just test` **GATE PASS 35/35 exit 0** (`logs/gate-step02a-rework-f1-round9.log`),
guard standalone **PASS 36/36** (check count unchanged — no clause added), battery **120/120**
(`logs/mutation-step02a-round9.log`, was 107), RED rows re-run **12/12**
(`logs/red-step02a-rework-f1-round9-afterfix.log`), **RENDER PASS**
(`logs/render-step02a-round9.log`), **DELIVERY PASS A–D** (`logs/delivery-step02a-round9.log`).
The critic's own mutation through the critic's own command flips from their guard PASS 36/36 to
**GATE FAIL exit 1** (`logs/gate-step02a-rework-f1-round9-mutated.log`, template sha printed before
`d2e5b364` → during `db745803` → after `d2e5b364`).

Harness: the only container started for calibration was `prom/prometheus:v3.6.0` with
`--rm --network none` and a read-only config mount — no listener, no credential, no network. The
delivery driver tore its own containers down with evidence printed after teardown. No live host
access, no `just play`, no vault value, **no commit**. Step 1b untouched.

## 2026-07-29 — Step 2a REWORK round 10 (task-1785324219-b403, review.rejected → F1)

**The review's F1 was one clause; its GENERAL RULE was the shape.** `relabel_configs` is a LIST and
`test_pve_scrape_job_is_multi_target` built both LOAD-BEARING pins from `(?ms) … .*? …` spans over
the whole block, so the two halves of each pin could come from different entries. The rule the
review wrote with it — *after sweeping the slicers, grep the clause bodies for `.*?` and for any
regex spanning a block that is a LIST* — is what round 10 acted on, because round 9 was rejected for
applying a rule only where a review had pointed.

**RED first, and the sweep found EIGHT more clauses, not one** (`logs/red-step02a-rework-f1-round10.log`).
Eighteen rows: the review's five verbatim, plus thirteen of mine. **12 of 18 answered wrongly by the
round-9 guard**, every GREEN row rendering, `yaml.safe_load`ing and confirmed on the REAL server —
`prom/prometheus:v3.12.0` (the image the repo PINS; the review used v3.6.0) and `traefik:v3.7.5`:

| row | clause | what the server LOADS while the guard prints PASS 36/36 |
|-----|--------|---------------------------------------------------------|
| A1  | pve scrape job | `?target=pve-exporter%3A9221` — the exporter asked about ITSELF |
| A2  | pve scrape job | `http://192.168.1.50:8006/pve?…` — the request dialed at the PVE API |
| A3  | pve scrape job | `/pve?cluster=1&node=1` — no `target=` at all (the `__adress__` typo) |
| B1  | plex public router | `plex -> api@internal` on `web`, allowlist-free: the **unauthenticated Traefik API on the WAN port-forward** |
| B2  | plex service backend | `plex -> http://127.0.0.1:32400` — traefik's own loopback, a 502 for the one public host |
| B3  | internal-allowlist | two of the four ranges on a middleware no router references — the tunnel's Docker hop and Tailscale v6 403'd |
| B4  | middlewares defined | `redirect-to-https` loaded with `["headers"]` — the public host's http→https upgrade gone |
| B5  | entrypoints | `web` on `:8080` — `address:\s*"?:80` has no right boundary |
| B6  | entrypoints | `{"tunnel": ":80", "web": ":9080"}` — the tunnel arriving on an entrypoint no router serves |
| B7  | caServer toggle | the ACTIVE resolver on **LE STAGING** with a second resolver answering for the toggle |
| B8  | cloudflared | `depends_on: []`, answered by a later `TUNNEL_ORIGIN_SERVER_NAME=traefik` |
| B9  | dashboard web twin | the twin on `websecure` after an ordinary reorder, `plex-web`'s `- web` answering |

Six controls (A4/A5/B1c/B3c/B6c/B7c) were RED as wanted, so no row is a tautology.

**The fix: one new slicer, two missing anchor hops, and every per-entity claim asked of ONE entity.**
`_list_entries` (the review's own prototype, verbatim) slices a list into entries — needed because a
relabel entry is a MAPPING and `_param_values` cannot express one. `_middleware_block` and
`_resolver_block` complete the two anchor paths the file was missing, on the same key-bounded path as
`_routers_block`. `_dynamic_service_block` does for `http.services:` what `_router_block` does for
routers. No new clause (still 36), and the ORDER half of the pve pin is a comparison of the two
entries' indices — which is where the docstring's own "and THEN" comes from for free.

Where the claim is UNIVERSAL the read stays wide, per the rule's own point 3: `hardcoded` in
`test_plex_public_router_present` keeps reading all four routers, because "no router hard-codes a
resolver" quantifies over the lot — narrowing it would have dropped the only pin covering `plex-web`.

**GREEN: 18/18 rows RED** against the round-10 guard (`logs/green-step02a-rework-f1-round10.log`).

**Attribution, one relaxation per edge — 12/12** (`logs/attrib-step02a-rework-f1-round10.log`, leg 1):
each fix's OLD spelling is written back into the real guard, its row goes GREEN again, and the guard
is restored. One row needs TWO relaxations and says so: B7 fails **2/36**, because `sole` and the
scoped `caServer` pin each catch the second resolver independently. That redundancy is real, stated,
and kept — they are different claims and neither should need the other to be true.

**PRICE, and it found a false RED of my own making** (leg 2): eight rows of ordinary YAML that the
runtime treats as identical to the delivered tree — flow-form `entryPoints`, a re-sorted
`sourceRange`, a `depends_on` condition map, an explicit `0.0.0.0:80` bind, a re-ordered and a
re-quoted relabel list — must all stay GREEN, and one did not. `_param_values` read a WRAPPED flow
sequence as an empty list, which is a false RED on correct config; it now gathers to the closing
bracket, which also fixes the pre-existing limitation for `params:`. All 8/8 green after that.
Leg 3: every anchored name in the delivered tree resolves exactly once.

Two things measured and deliberately NOT built, so round 11 neither over-builds nor rediscovers them:
**last-write-wins** in a relabel list (the review's R6 — needs a model of relabel ACTIONS, fails
loudly) and **exclusivity of `sourceRange`** is now pinned but `ipAllowList` semantics beyond the
range set are not.

**Verification.** `just test` **GATE PASS 35/35 exit 0** (`logs/gate-step02a-rework-f1-round10.log`),
guard standalone **PASS 36/36** with the check count unchanged, standing battery **120/120**
(`logs/mutation-step02a-round10.log`) — one row needed maintenance and got it: round 7's
comment-boundary attribution row now also relaxes round 10's plex scoping, because a truncated
router block loses its `tls:` too, and the row's job is to isolate round 7. **RENDER PASS**
(`logs/render-step02a-round10.log`), **DELIVERY PASS A–D** (`logs/delivery-step02a-round10.log`).

`scripts/test_traefik_config_shape.py` is the ONLY repo file this round touches: prometheus
`d2e5b364`, traefik `73ddf123`, dynamic `097eca50`, compose `3fb4fa74`, tasks `2e120676`, handlers
`0e05058e`, defaults `8fd98ed3` — identical before and after, printed by every driver.

Harness: `prom/prometheus:v3.12.0` (read-only mount, `127.0.0.1:19091` only, `--rm`, `--network none`
for promtool) and `traefik:v3.7.5` (read-only mounts, `127.0.0.1:18081` only, the probe's own API
entrypoint moved to `:8099` so it cannot collide with a decoy's port). `docker ps -a` shows no
`builder-r10*` containers and no r10 networks. No live host access, no `just play`, no vault value,
**no commit**. Step 1b untouched.

## 2026-07-29 — Step 2a REWORK round 11 (review.rejected → F1) — BUILT

The review's F1 was right, and its rule (1) — "a clause with N pins is fixed when all N are, and a
round that rewrites one pin is exactly when the others get inherited" — was right about more clauses
than the two it raised. So the round applies BOTH of the review's greps to the whole file rather than
to the two lines named. `scripts/test_traefik_config_shape.py` is the only repo file touched
(prometheus `d2e5b364`, traefik `73ddf123`, dynamic `097eca50`, compose `3fb4fa74`, env `b76d2ef8`,
tasks `2e120676`, handlers `0e05058e`, defaults `8fd98ed3`, group_vars `616abca2` — identical before
and after, printed by every driver).

**RED first — 12 rows, 6 wrongly GREEN, 2 false REDS** (`logs/red-step02a-rework-f1-round11.log`),
every GREEN row carried to what the SERVER does on the pinned `traefik:v3.7.5`, through
`docker compose config`, or through the real `ansible`:

* **A1/A2** reproduce the review's C1/C2: `plex-web` loses `redirect-to-https@file` while a
  documentation COMMENT on the next router (A1) or an ordinary sibling `apex-web` router (A2) answers
  the span. Guard **PASS 36/36**, field byte-identical to the honest tree's, and traefik loads
  `plex-web.mw=['security-headers@file']` and answers `GET http://plex.<domain>/` on `:80` with
  **HTTP 502 — it PROXIED the plain-HTTP request** where the delivered tree answers **301 → https**.
  A3 (no carrier) is RED.
* **A4** is the review's C4 in the form that actually SHIPS. Their spelling kept a bare
  `environment:` and compose-go rejects that document (rc=1, "must be a mapping"), so the deployable
  form is the block's deletion: guard **PASS 36/36** with the service's own comment carrying
  `HOMEPAGE_ALLOWED_HOSTS=home.{{ domain }}` while `docker compose config` resolves
  `services.homepage.environment=None`. A5 control RED, **A6 the false RED** (a 2-space comment inside
  the service on a CORRECT tree).
* **A7 is the sweep's own find and the one rule (1) predicts.** Round 10 rewrote the `websecure` pin
  in `test_plex_public_router_present` and left `(?s)entryPoints:.*?\bwebsecure\b` one clause down in
  `test_traefik_dashboard_router_present`. With `entryPoints: [web]` and one middleware REFERENCE
  named `redirect-to-websecure`, the whole field printed `websecure=True` at **PASS 36/36** while the
  real traefik loaded `traefik-dashboard` on `['web']` — `https://traefik.<domain>`, the direct
  LAN/Tailscale path and the only one serving the wildcard cert this router requests, with no router
  at all. A8 control RED.
* **B1/B2 are the second grep's find: FOUR hand-rolled slicers over `group_vars/all/vars.yml`**,
  `(?ms)^<key>:\s*$(.*?)^\S`, breaking the same three settled rules as the homepage row. A column-0
  comment — that file's own idiom — ends the block, and TWO of the four pins are ABSENCE pins, so they
  fail OPEN: `prometheus` and `whoami` each PROMOTED into `public_services` printed
  `entries=['plex']` and `not_public=True` at **PASS 36/36** while the real `ansible` loads
  `public_services=['plex', 'prometheus']`. B3 control RED, **B4 the false RED** (a column-0 comment
  inside a CORRECT `internal_services:`).

**Severity, priced where it belongs rather than levelled up.** A1/A2 are the ship-blocker on this
repo's own precedent: a green guard over a WAN-facing state the docstring exists to forbid, on the ONE
router carrying no allowlist. A7 and A4 fail LOUD (the dashboard's direct path and homepage's Host
validation) and I say so. B1/B2 are the mildest of the three: `vars.yml` states these lists are
documentation-only and nothing renders from them, so the harm is exactly the one that file names —
"they must not mislead a future operator" — plus the two false REDS.

**GREEN 12/12** (`logs/green-step02a-rework-f1-round11.log`): six flip GREEN→RED, four controls stay
RED, and **both false REDS go GREEN**. The fix adds **no clause** (still 36) and no new spelling:
`_param_values(_router_block(dynamic,'plex-web'),'middlewares')` and
`_param_values(dash,'entryPoints')` are the file's own idiom one clause over, `_compose_service_block`
already existed, and `_top_level_list` is `_key_bounded_block` + `_line_class` — the two helpers whose
whole point is that a boundary and a line class are decided in one place.

**Attribution 8/8, one relaxation per edge** (`logs/attrib-step02a-rework-f1-round11.log`): the OLD
spelling written back into the REAL guard and the row answers again; the two false-RED rows return to
RED, which is what isolates them. One honest note: B1's relaxation has to leave `pub` bound, because
the clause's printed field names it — a row that dies on a NameError measures the driver.

**PRICE 8/8** — ordinary YAML the runtime treats as identical stays GREEN: flow-form `middlewares`,
a reordered two-entry list, the middleware referenced WITHOUT the optional `@file` suffix, flow-form
`entryPoints`, a quoted env entry, a re-ordered `internal_services`, a quoted list entry. The eighth
is declared **RED** with its reason: an INLINE FLOW `public_services: ["plex"]` reddens, it reddened
before this round too, and what round 11 changes is the fail-OPEN half — `not_public` was GREEN on a
list the guard cannot read and is now RED.

**Measured and NOT built** (`logs/red-step02a-rework-f1-round11b.log`), so round 12 neither
over-builds nor rediscovers: `_metrics_prometheus_block`'s glyph boundary fails CLOSED (a 2-space
comment inside `metrics.prometheus` prints `in_block=None`, a false RED) exactly like
`_entrypoint_address`'s, which the review measured and forbade chasing; `sans:.*?\*\.{{ domain }}` is
the LAST key in the dashboard router's block, so nothing follows it to answer (printed, not asserted);
`(?s)redirections:` is an absence pin with no span whose claim is universal; site.yml's cross-play
span fails loudly at the syntax check already in `just test`. **Do not chase any of these.**

**Verification.** `just test` **GATE PASS 35/35 exit 0** (`logs/gate-step02a-rework-f1-round11.log`),
guard standalone **PASS 36/36** with the check count unchanged, standing battery **134/134**
(`logs/mutation-step02a-round11.log`, was 120 — 14 new rows, and no existing row needed maintenance
this round), **RENDER PASS**, **DELIVERY PASS A–D**.

Harness: one `traefik:v3.7.5` (`--rm`, `127.0.0.1:18080/18081` only, read-only mounts, removed in a
`finally`; the probe static carries NO `certificatesResolvers` so no ACME request can leave this box,
and the rendered plex backend is repointed at the container's own `127.0.0.1:1`), the HTTP client
REFUSES redirects for the reason the review disclosed, and `docker compose config` / `ansible` run
locally. `docker ps -a` shows no `builder-r11*` containers and no r11 networks. No live host access,
no `just play`, no vault value, **no commit**. Step 1b untouched.

## 2026-07-29 — Builder, Step 2a REWORK round 12 (review.rejected → F1) — BUILT

**Active task:** task-1785324219-b403 (`code-assist:plex-monitoring:step-02:pve-exporter-repo-wiring`).
**Repo files touched: `scripts/test_traefik_config_shape.py` ONLY** (`0246c3df` → `825cf2e3`). All ten
artifact shas identical to round 11's and printed at both ends by every driver: compose `3fb4fa74`,
env `b76d2ef8`, traefik `73ddf123`, dynamic `097eca50`, prometheus `d2e5b364`, defaults `8fd98ed3`,
tasks `2e120676`, handlers `0e05058e`, group_vars `616abca2`, mise `fb1ae417`.

**The class.** A pin with NO span and NO slicer: a raw whole-file substring search over an
un-comment-stripped template, which a whole-line `#` comment can satisfy (a comment line's first
non-space character is `#`, so `(?m)^\s*<key>:` can never match one while a bare substring can).
Presence pins of that shape fail OPEN; absence pins fail CLOSED on correct trees. Both directions
measured.

**RED first, on guard `0246c3df`** (`logs/red-step02a-rework-f1-round12.log`, 17 rows, all giving
their declared PRE-fix verdict): the review's rows reproduce — `internal-allowlist@file` deleted from
a router behind an ordinary `# was:` comment is **PASS 36/36** (A1/A4/A5), `homepage-web` moved to
`websecure` AND repointed at grafana's backend is **PASS 36/36** (A6, the Error-1000 class), a
resolver hard-coded to a literal the companion pin does not enumerate is **PASS 36/36** (A7);
controls with no carrier are RED (A3/A3b); and three ABSENCE pins are **FALSE REDS on fully correct
trees** (A8/A9/A10). Each of the three security rows carried to `docker compose config` **rc=0**,
resolving the mutated label — states `just play` ships. The server's 403→200 is the round-12 review's
own measurement (`logs/review-step02a-rework-f1-round12b.log`); I agree with it and cite rather than
re-run it, so **no container was started this round**.

**Leg E — the one-word fix is not enough, measured:** with the extras clause patched to
`_strip_comments(_read(COMPOSE))` and nothing else, the comment carrier dies (E1 RED) but a label
defining `routers.grafana.middlewares` placed on the **whoami** service is still **GREEN** (E2).

**The fix.** One helper, no new clause, constant or spelling; check count unchanged at 36:
`_service_labels(body, name) = _list_entries(_indented_block(_compose_service_block(body, name), "labels"))`
for PRESENCE pins, and `_strip_comments` for ABSENCE pins, whose claim is document-wide (a `tls` label
for router X on service Y still configures router X, so scoping those would fail OPEN).

**The sweep, run to exhaustion rather than stopped at the review's eleven**
(`logs/red-step02a-rework-f1-round12c.py`): an AST walk for `re.search` over a whole document with a
pattern not anchored at line start. 8 sites, then **9** after I fixed my own blind spot — it
classified only NAMED subjects and missed an inline `re.search(pat, _read(MISE))`; disclosed in the
driver, not quietly repaired. That found a **seventh** clause (`test_resolver_is_variable_driven`,
surfaced by my own post-fix run: fixing the six reddened it on a correct tree) plus **five more** in
four more files. Measured differentially — old spelling restored, rows run, delivered spelling
restored, same rows run again — in `logs/red-step02a-rework-f1-round12b.log` (2 rows) and
`-round12d.log` (7 rows), all flipping. env.j2's three token pins were GREEN with the assignment
**commented out** while the rendered `.env` carries no such key at all; `redirections:`, `:8080`, the
`buggy` CF reference and mise.toml's endpoint were wrong in the other direction. **The sweep now
returns ONE carriable site**, `test_site_applies_docker_host_role`, which two prior reviews forbade
chasing, and prints that reason.

**Two corrections to the review, both measured.** A2's cross-service carrier is classified `guard`,
not `runtime`: two containers defining one router name is a docker-provider CONFLICT, not a quietly
unprotected Grafana — its job is leg E's point. And the `@file`-suffix row is **not** a price row in a
docker label (without the suffix traefik resolves the middleware in the docker provider's own
namespace and it does not resolve at all); it is disclosed as a deliberate looseness of the pin
instead. The equivalent row IS a price row one file over in dynamic.yml.j2.

**Price.** 4/4 GREEN on ordinary compose the runtime treats identically (a quoted label entry, a
reordered middleware list, a whole-line comment inside the labels list, and — post-fix — every
false-RED row). The fifth, `labels:` as a **MAPPING**, is declared **RED** and labelled `strict`:
legal compose, identical runtime, `_list_entries` returns `[]` on it and fails CLOSED — and it was RED
before this round too, since the pins require `=` where a mapping writes `:`.

**Verification.** `just test` **GATE PASS 35/35 exit 0** (`logs/gate-step02a-rework-f1-round12.log`);
guard standalone **PASS 36/36**, check count unchanged; post-fix driver **17/17 rows** on the flipped
expectation (`logs/green-step02a-rework-f1-round12.log`); standing battery **154/154**
(`logs/mutation-step02a-round12.log`, was 134 — 20 new rows, and **no existing row needed
maintenance**).

No container started, no live host access, no `just play`, no vault value, **no commit**. Every
mutation was written to the real file and reverted in a `finally`, shas printed at both ends. Step 1b
untouched.

## 2026-07-29 — Builder, Step 2a REWORK round 13 (task-1785324219-b403)

Round 13's review named TWO fail-OPEN classes on the pins round 12 had just rewritten, and they are
independent. Both are fixed; `scripts/test_traefik_config_shape.py` is the only repo file touched
(`825cf2e3` -> `17740113`), and the eleven other shas are identical to round 12's
(`logs/red-step02a-rework-f1-round13.log` prints all twelve at both ends of every run).

**F1 — three lines inside `_strip_comments`, the one function the whole read chain funnels through.**
A line was dropped only when its FIRST non-space character was `#`, so an INLINE (trailing) comment
survived it and every reader built on it (`_key_bounded_block` -> `_compose_service_block` ->
`_indented_block` -> `_list_entries` -> `_service_labels`); the pins' own `[^\n]*` tails cross the `#`,
so the carrier needed no line of its own. `re.sub(r'\s+#.*$', '', ln)` alongside the whole-line drop.
`\s+#` is YAML's own rule for a trailing comment, and the price is a printed census: **0**
inline-comment sites in the eleven files the pins are asked of (leg D), and where a future value really
does contain ` #` the cut SHORTENS the subject, so the pin fails CLOSED.

**F2 — the effective VALUE, not the existence of a matching entry. No comment is involved, so F1
cannot touch it.** Docker labels are a MAP: a duplicate key in the `labels:` SEQUENCE is legal YAML
(nothing is duplicated as far as the parser is concerned) and docker collapses them LAST-WINS, while
round 12's pins were existential over entries. `_service_label_map` (built on `_service_labels`, so it
keeps round 12's service scoping) + `_label_members` for the comma-split membership, and
`_env_assignments` for the same defect one file over — a `.env` is line-based, so compose collapses a
duplicate assignment too. Six label clauses and both env clauses now read one named key's effective
value; the ABSENCE pins stay document-wide and decommented, because a `tls` label for router X on
service Y still configures router X.

**Which surfaces F2 has to cover was MEASURED, not assumed** (leg E): the labels sequence and the
`.env` document collapse SILENTLY (`docker compose config` rc=0 with the wrong value), while a
duplicated compose SERVICE key (`mapping key "whoami" already defined`) and a duplicated
prometheus.yml key (`field metrics_path already set`, promtool on the pinned image) are REFUSED by the
runtime, and a duplicated `labels:` KEY already reddens through `_indented_block` (round 9). That is
what bounds the fix to two readers instead of a sweep.

**RED first, on the shipped guard `825cf2e3`** (`logs/red-step02a-rework-f1-round13.log`, 23 rows, all
giving their declared PRE verdict; `-green-...log` is the SAME driver under `--post`, judging the same
rows against the flipped expectation, 23/23). 14 rows were fail-OPEN and are now RED: R1-R7 the
inline carrier (whoami/grafana/prometheus/whoami-web allowlists, a resolver hard-coded to `le-staging`,
`homepage-web` moved to `websecure` AND repointed at grafana's backend — the Error-1000 class), R9/R9b
env.j2's CF and PVE assignments DELETED with the old text trailing another line, D1-D5 the duplicate
key with no comment anywhere. The no-carrier controls R0/R0b are RED throughout. R8's FALSE RED on a
fully correct tree clears. `docker compose config` rc=0 on every row with the mutated value RESOLVED,
so each is a state `just play` ships; the env rows are rendered with STAND-IN vault values, without
which a dropped assignment is indistinguishable from the delivered tree.

**I cite the server rather than re-run it.** The review measured 403 delivered -> 200 carried for both
classes on `traefik:v3.7.5` with the real docker provider and labels taken out of the rendered template
(`-round13b.log`, and `-round13e.log` leg H2 on the effective map). I agree with both; starting
containers to re-derive an agreed number is cost without a claim. No traefik or whoami container was
started this round — the one container is `promtool check config`, for leg E's refusal measurement.

**The sweep found a clause no review asked about** (`logs/red-step02a-rework-f1-round13b.py`, an AST
walk over all 113 pin subjects in the guard): `test_tasks_idempotent_builtin_only` read its
600-character guard window off the RAW file with an UNANCHORED pattern, so a comment naming
`changed_when` answered for an `ansible.builtin.command` with no guard at all — and this file's idiom
is exactly that, long comments directly above the tasks they describe. Measured differentially in leg
G (old spelling restored in the real guard, reverted in a `finally`): PRE the comment carrier is
**GREEN**, delivered it is **RED**, and the no-carrier control is RED both ways. Disclosed price: with
comments off the window reaches further into live task lines, so a neighbouring task's guard can
answer where a comment used to pad the distance — the inherited heuristic's crudeness, unchanged in
kind, and a comment that satisfies a pin is the worse of the two.

**Three of my own defects disclosed, all mine and all in the logs.** The sweep's classifier was wrong
three times before it was right: `ast.unparse` re-escapes an f-string's backslashes (four anchored
patterns read as carriers), a subject that is a CAPTURE GROUP is bounded by its producing pattern and
not by the document (seven more), and a name bound by `for a, b in re.findall(...)` is a capture too.
And leg D's census first counted the guard's own source, where this round's F1 docstring now quotes
` #` — the guard is never a pin subject, so it is counted separately and the PRE log's `0` is stated
rather than silently re-based.

**The list is CLOSED with three judged exceptions, printed with their reasons**, of which exactly ONE
is carriable: `test_site_applies_docker_host_role`, forbidden by two prior reviews and loud at the
`ansible-playbook --syntax-check` step already inside `just test`. The other two are judgements, not
holes: `test_no_plaintext_secrets` is a LEAK scan whose polarity makes a comment a FALSE RED (and
decommenting it would blind the guard to a secret sitting in a comment), and one pin in
`test_rendered_configs_reach_the_service_that_reads_them` is built by string concatenation, so the
sweep cannot read it as a literal and I judge it by hand.

**Price.** 5/5 GREEN on ordinary compose the runtime treats identically (quoted entry, reordered
middleware list, whole-line comment, an inline comment on a CORRECT line, a space after the comma).
Two rows are RED by design and labelled `strict`: `labels:` as a MAPPING (unchanged from round 12), and
— new — the `@file` provider suffix omitted, which round 12 disclosed as a LOOSENESS of the substring
pin and explained: in a docker label the bare name resolves in the docker provider's own namespace,
where no such middleware exists, so the reference does not resolve at all. Naming the reference
(`INTERNAL_ALLOWLIST_REF`, hoisted once) closes it.

**Verification.** `just test` **GATE PASS 35/35 exit 0** (`logs/gate-step02a-rework-f1-round13.log`);
guard standalone **PASS 36/36**, check count unchanged at 36; post-fix driver **23/23** on the flipped
expectation; standing battery **173/173** (`logs/mutation-step02a-round13.log`, was 154 — 19 new rows,
and **no existing row needed maintenance**). No live host access, no `just play`, no vault value, **no
commit**. Every mutation written to the real file and reverted in a `finally`. Step 1b untouched.

## Step 2a — REWORK round 14 (task-1785324219-b403, `review.rejected` → F1/F2)

Round 14's review does not widen the search. It tests round 13's **own closure claim**:
`_service_label_map`'s docstring said *"Nothing else in this guard reads a region the runtime
flattens"* and its leg E concluded the collapsing surfaces were *"exactly (1) the labels SEQUENCE and
(2) the .env document"*. That enumeration was short by **two regions of the same shape in the same
file**, and one of them carries the PVE credential this task exists to wire. Both are fixed, both were
measured before and after on the same 24-row driver run twice
(`logs/red-step02a-rework-f1-round14.log` PRE on guard `17740113`,
`logs/green-step02a-rework-f1-round14.log` under `--post` on the delivered `25c566c7`; **24/24 rows
gave their declared verdict both ways**).

**F1 — `environment:`.** A YAML SEQUENCE of `KEY=VALUE` strings that docker collapses into a map
LAST-WINS, exactly like `labels:`, and five pinned keys were read with a whole-block `re.search`, i.e.
FIRST entry wins. All five were **PASS 36/36** with the wrong effective value on a tree `just play`
ships (`docker compose config` rc=0, no stderr): `PVE_USER=''`, `PVE_TOKEN_NAME=''`,
`PVE_TOKEN_VALUE=''`, `PVE_VERIFY_SSL=true`, `HOMEPAGE_ALLOWED_HOSTS=''` (rows O1–O5). The five
delete-controls C1–C5 are RED, so green-vs-red was purely whether a **second** assignment followed the
pinned one. Fix = `_service_env_map` on round 13's own funnel one key over
(`_compose_service_block → _indented_block → _list_entries → _kv_entries`), service-scoped and
decommented for free; four clauses now ask that map for the named key (`defaults_vars`,
`verify_ssl_off`, `compose_indirection`, `test_homepage_allowed_hosts`).

**F2 — `volumes:`.** The runtime's key is the **CONTAINER-side target**; `_bind_mount_target` looked
entries up by their HOST side and returned the first match, so a second mount onto
`/etc/prometheus/prometheus.yml` from `/srv/legacy` was **PASS 36/36 printing `2/2 paths whole,
broken={}`** — the clause whose entire job is to say the rendered config REACHES the service,
answering yes about a file the service never sees. Fix = `_service_mount_map`, keyed by the target,
last wins; `_bind_mount_target` asks it the runtime's question and returns None when no target
resolves to the rendered file (rows V1/V2, controls VC1/VC2 RED).

**Leg R asked the PROCESS, not compose** (`logs/red-step02a-rework-f1-round14b.log`, the pinned
`prom/prometheus:v3.12.0`, shipped shape, private network, no published ports, all `--rm`): the
delivered single mount loads the rendered file (`/api/v1/status/config` echoes it, `scrape_interval=37s`,
`jobs=['pve']`); the shadowed pair loads the **SHADOW** (`1m31s`, `jobs=['legacy']`) from a container
that starts normally; the deleted mount loads the image's default (15s, `jobs=['prometheus']`, scraping
nothing but itself). Compose's answer about its own model is not the claim this clause makes — which
file the process READ is.

**X1, in the same edit and not a round of its own,** because the review named it rather than blocking
on it: `--collector.config` / `--no-collector.config` are ONE argparse BooleanOptionalAction on the
real image, so a second positive entry wins while `no_collector_config` pinned only the presence of the
negative form. It now reads the LAST of the pair.

**THE CRITERION replaces the enumeration**, and it lives on `_kv_entries` where the next review can
check it against the guard's reads instead of re-listing regions: *a duplicate YAML **KEY** is caught by
somebody* — ansible-lint `yaml[key-duplicates]` exit 2 inside `just test`, compose on a duplicated
SERVICE key, promtool on a duplicated prometheus.yml key, `_indented_block` → `""` on a key that
resolves twice — *while a duplicate entry in a **STRING SEQUENCE THE RUNTIME MAPS BY AN IN-STRING
KEY** is invisible to every linter, because nothing is duplicated as far as YAML is concerned.* Leg S
of the driver applies it and prints the result: `labels:` and `.env` (round 13), `environment:` and
`volumes:` (round 14), `command:` weakly (X1). Round 13's docstring is CORRECTED in place rather than
deleted — the claim it made is replaced by the stronger one that is true.

**Price 7/7 GREEN** on ordinary compose the runtime resolves identically: whole-line comment inside
`environment:`, inline trailing comment on a correct entry, the four entries reordered, the QUOTED
entry (**RED before this round** — an improvement, not a cost), plus a quoted mount entry, a comment
inside `volumes:`, and the two prometheus mounts reordered. One row is RED by design and labelled
`strict`: `environment:` as a MAPPING — legal compose, identical runtime, RED before this round too,
the same disclosed exception the `labels:` mapping carries.

**Verification.** `just test` **GATE PASS 35/35 exit 0** (`logs/gate-step02a-rework-f1-round14.log`);
guard standalone **PASS 36/36**, check count unchanged at 36; post-fix driver **24/24** on the flipped
expectation, each row reddening **exactly its own clause, 1/36**; standing battery **193/193**
(`logs/mutation-step02a-round14.log`, was 173 — **20 new rows, no existing row needed maintenance**).
`scripts/test_traefik_config_shape.py` is the only repo file touched (`17740113` → `25c566c7`); the
other eleven shas are identical to round 13's and printed at both ends of every run (compose
`3fb4fa74`, env `b76d2ef8`, traefik `73ddf123`, dynamic `097eca50`, prometheus `d2e5b364`, defaults
`8fd98ed3`, tasks `2e120676`, handlers `0e05058e`, group_vars `616abca2`, mise `fb1ae417`,
homepage-services `27929d70`). Containers this round: three `prom/prometheus:v3.12.0` + three
`curlimages/curl:8.11.1` legs, all `--rm`, all torn down in a `finally`, `docker ps -a`/`network ls`
clean of `r14legr*`. No live host access, no `just play`, no vault value, **no commit**. Step 1b
untouched.

**2026-07-30, Finalizer on `review.passed` — Step 2a CLOSED (`task-1785324219-b403`), `queue.advance`.**
Re-verified rather than inherited: all seven shas matched the Critic's claims on the tree as found,
`just test` **GATE PASS 35/35 exit 0**, guard standalone **PASS 36/36**, and a 9-row mutation battery
written for this turn (`logs/finalizer-step02a-adversarial.py`, `-pre.log` / `-post.log`) with every
row mutating a real repo file and reverting in a `finally`.

Two rows moved and both were fixed in this turn, taking the guard `25c566c7` → `1a95b475`:
**G1**, the gap the Critic deliberately left for this gate — `command:` is the fifth region of round
14's own criterion and only one of its two consumers read it last-wins, so a decoy
`--config.file=/etc/prometheus/decoy.yml` appended after the delivered entry was PASS 36/36; and
**P1**, a false RED the battery found on its own — the same entry merely QUOTED took the clause RED
while docker resolves it identically. `_last_flag_value` + unquoting in `_service_command_args` fix
both; post-fix the battery is **9/9 as declared** (G1 RED, P1 GREEN, the four chain rows still RED,
the three price rows still GREEN) and `just test` is **35/35**. Rationale for fixing here rather than
reopening: DEC-054.

**Step 2a's acceptance criteria are met end to end** — `just test` green, every new check non-vacuous
under mutation, no live call of any kind, and the demo holds (`pve-exporter` with no Traefik labels
and no published ports; scrape job `metrics_path: /pve` with the `__param_target` relabel and
`__address__` → `pve-exporter:9221`).

**The wave is NOT exhausted, so this is `queue.advance`, not `LOOP_COMPLETE`.** Step 1b
(`task-1785290391-b51a`) and Step 2b (`task-1785324247-3934`) are both open, both **OPERATOR ONLY**,
and both were blocked by 2a — that blocker is now discharged and a single `just play` satisfies both.
Steps 3 and 4 have no runtime tasks yet; Planner owns creating that wave. No live host, no
`just play`, no vault value, no commit.

## 2026-07-30 — Planner on `queue.advance` (Step 2a closed) — Step 3 wave materialized, `tasks.ready`

**What changed in the queue.** Step 2a closed with no agent-side work left anywhere in Steps 1 or 2,
so the current step moves to **Step 3**, split 3a/3b at the secret line exactly as Step 2 was
(DEC-055): `task-1785370559-2a76` (3a, repo-side wiring + shape guard, READY, the Builder's task)
and `task-1785370581-de17` (3b, operator gate, `--blocked-by` 3a). Step 4 gets no tasks.

**Did NOT re-publish 1b or 2b as the Builder's next task.** Both are ready in the queue now that 2a
discharged their blocker, and both are OPERATOR-ONLY in every step: `just play` against the live
household stack, a real request through `websecure`, a Proxmox token minted in a web UI, a live
Prometheus query. A fresh Builder handed one of those can only park — which already happened once on
1b (`build.blocked`, runner stopped) and is the failure mode the resume was told not to repeat. They
stay open beside Step 3's wave; they do not block 3a, which touches no file either gate reads as
evidence.

**Reference facts verified this pass, not inherited from the research doc.** Step 3's guidance was
written from `research/plex-monitoring.md`, which recommended axsuul's exporter but left "maintenance
status and LXC compatibility should be verified before committing" open, and whose Test Requirement
was **"confirm the `plex-exporter` target is `UP`"**. That is the third appearance of this
objective's recurring defect — the Step 1 buckets that were Traefik's own default, and the Step 2 job
on the exporter's default `/metrics` path — so it is corrected in `plan.md` before a Builder can
build on it.

Fetched, not recalled:

- **ghcr tag list for `axsuul/plex-media-server-exporter`**: `1.0.0, 1.1.2, 1.1.3, 2.0.0, 2.1.0,
  latest` + 45 commit-sha tags. `2.1.0` resolves to an OCI index `sha256:ab89d0ba039e…` with a
  `linux/amd64` manifest. Three-part tag ⇒ `test_no_floating_service_image_tags` stays green.
- **The runner-up cannot be pinned at all**: `ghcr.io/jsclayton/prometheus-plex-exporter` publishes
  **only `latest` and `main`**. That decides the design doc's open question on availability grounds
  rather than on the feature comparison. Maintenance: MIT, not archived, 78 stars, last release *and*
  last push both `2024-12-22` — ~19 months stale, recorded rather than left to be discovered.
- **`lib/middleware/collector.rb` at tag `2.1.0`** — the falsifier evidence. `plex_up` comes from
  Plex's `/identity` inside a `rescue HTTP::Error` / `ensure` pair; the series a dashboard actually
  uses come from the **token-gated** `/status/sessions` and `/library/sections`. So `UP` proves a Ruby
  web server answered and `plex_up 1` proves something replied to an **unauthenticated** probe.
  3b's decisive check is therefore `plex_media_count` returning series (token-gated), plus
  `plex_sessions_count{state="playing"} >= 1` during a real stream.
- **Failure shapes are not uniform**, and 3b's failure list is written on the difference: an
  unreachable `PLEX_ADDR` is rescued (200 + `plex_up 0`, target still UP), while a rejected token
  returns a non-JSON body to `JSON.parse` and **`JSON::ParserError` is not an `HTTP::Error`** — it
  escapes every rescue, `/metrics` 500s, target DOWN, zero series. 3a is asked to confirm that
  against a stub, the way `logs/calibration-step02a-f3.log` settled the PVE 401-vs-500 question.
- **It is NOT a multi-target exporter** (`config.ru` → `Prometheus::Middleware::Exporter`; the
  collector runs only when `PATH_INFO == "/metrics"`). The scrape job is an ordinary
  `plex-exporter:9594` target with **no `metrics_path`, no `params`, no relabel** — copying Step 2's
  `/pve` shape here is a 404, so 3a's guard is asked to pin the **absence** of `metrics_path` on this
  job.
- **Scrape budget is a real risk, not a nicety.** `collect_media_metrics` runs **synchronously inside
  the scrape request**, one `/library/sections/<key>/all` per library plus one more per `show`
  library, throttled to once per 300 s. `prometheus.yml.j2` is `scrape_interval: 15s` with no
  `scrape_timeout` (⇒ Prometheus' 10 s default), and `PLEX_TIMEOUT` alone is 10 s per request — so
  every fifth minute one scrape does the sweep and can blow the budget. Prometheus refuses a config
  whose `scrape_timeout` exceeds its `scrape_interval`, so the pair must move together and `promtool`
  inside `just test` catches an invalid one.
- **No new default needed for the address**: `docker_host_plex_url: http://192.168.1.110:32400`
  already exists (`defaults/main.yml:50`). Reuse it rather than writing a second literal.

**Also refreshed `.ralph/agent/operator-ask.md`.** Its correction header said "Step 2a is still in
review inside the loop and nothing is committed… nothing to do right now", which was true on 07-29
and is not now: 2a is closed and in the working tree, so the single `just play` that satisfies both
1b and 2b is live.

No code changed, no tests written, no `just play`, no live query, no vault value, no commit. Two
planning docs plus the operator ask touched, two runtime tasks created.

## 2026-07-30 — Builder, Step 3a (task-1785370559-2a76) — BUILT, `review.ready`

Repo-side wiring for the Plex exporter, plus the guard for it. TDD: the three new checks were
written and confirmed **RED for the expected reason** on the untouched tree (`logs/red-step03a.log`
— `FAIL: 3/39`, everything else still green) before a single template line changed.

**Delivered (four repo files + the guard):**
- `defaults/main.yml`: `docker_host_plex_exporter_image:
  ghcr.io/axsuul/plex-media-server-exporter:2.1.0`. Pulled here, so the Planner's digest is
  confirmed rather than inherited: `sha256:ab89d0ba039e4ea70fe5ee087b89c11f36b2eb30b4b85792c0caf60d5e4b2cd1`.
  No other new default — the address is the existing `docker_host_plex_url`.
- `env.j2`: `PLEX_TOKEN={{ vault_plex_token | default('') }}`, the `PVE_TOKEN_VALUE` pattern.
- `compose.yml.j2`: `plex-exporter`, scrape-only — no Traefik labels, no published ports, **no
  `command:`** (config is env-var only on this image), `PLEX_TOKEN=${PLEX_TOKEN:-}` from the
  sibling `.env`, `PLEX_ADDR={{ docker_host_plex_url }}`, and the six pinned config vars.
- `prometheus.yml.j2`: an ordinary single-target job — `targets: [plex-exporter:9594]`, no
  `metrics_path`, no `params`, no relabel — with its own `scrape_interval: 60s` /
  `scrape_timeout: 30s`.
- `scripts/test_traefik_config_shape.py`: three new checks (36 → **39**), plus
  `_duration_seconds` and `_vault_token_hops`; `test_pve_token_sourced_from_vault` now reads the
  shared hops rather than its own copy of the same four reads.

**Verification.** `just test` **GATE PASS 35/35 exit 0** (`logs/gate-step03a.log`); guard standalone
**PASS 39/39**. Mutation battery **47/47 rows as declared** — 36 RED, 11 GREEN price rows — every
row mutating a REAL repo file and reverting in a `finally`, shas printed at both ends, delivered
tree re-verified 39/39 after (`logs/mutation-step03a.py` / `.log`). Two rows were wrong on the first
pass and both are disclosed there: C11 put its decoy `METRICS_PREFIX=` *before* the delivered entry,
where docker legitimately keeps the delivered value, so GREEN was the right answer and the row said
nothing until it was moved after it (C11b keeps the before-position as the control); and C3's clause
was not a boolean field, so the battery could not see a RED the guard had in fact produced.

**Two live calibration legs, no live call of any kind** — nothing touched `192.168.1.110:32400`.
- `logs/calibration-step03a-token.log` (acceptance criterion c), five rows against the pinned
  exporter and a stub Plex: valid token → 200 with `plex_up 1`, `plex_info` and three
  `plex_media_count` series; **rejected token → HTTP 500, container still RUNNING, and ZERO series
  including `plex_up`**; unreachable `PLEX_ADDR` → 200 with `plex_up 0` and nothing else; empty
  token (the delivered pre-3b state) → 500. The plan's reasoning is confirmed AND the outcome is
  broader than it: a JSON 401 body removes the `JSON::ParserError` mechanism entirely and it still
  500s, via `NoMethodError` on the nil `Directory` in `collect_media_metrics`.
- `logs/calibration-step03a-scrape-budget.log`, six rows against `prom/prometheus:v3.12.0`: the
  delivered config loads at `scrapeUrl=http://plex-exporter:9594/metrics interval=1m timeout=30s`;
  timeout > interval is rc=1; a job-local timeout with no interval is rc=1; **a job-local interval
  with no timeout is rc=0 and silently keeps the 10 s default**; `15s`/`10s` written out is a legal
  no-op; and `metrics_path: /pve` copied onto this job is rc=0 and builds
  `scrapeUrl=…:9594/pve` — the 404 is deployable, which is why its absence is pinned.

**Two corrections to plan.md, both from measurement.** (1) "`promtool check config` inside
`just test` catches the invalid pair" is **false** — the gate's 35 steps hold no promtool step and
never render this template, so the guard is the only thing that catches it. (2) The 3b failure list
carried "Target UP, `plex_up 1`, `plex_media_count` empty for >5 min", which is **unreachable**: on a
bad token the response is a 500 and no series are emitted at all, `plex_up` included.

**Confirmed, not re-added (task item 6):** the `prometheus.yml` render task already carries
`mode: "0644"` and `notify: Restart prometheus`, and `.env`/`compose.yml` already re-render;
`test_rendered_configs_reach_the_service_that_reads_them` still passes unchanged.

No `just play`, no vault value, no live host access, **no commit**. Steps 1b and 2b untouched.

### Step 3a REWORK (review.rejected F1) — 2026-07-30, Builder

One blocker, closed by two deletions. `scripts/test_traefik_config_shape.py:3196` compared
`env_map.get(key,"").strip('"\'').lower() != want.lower()`, so two of `PLEX_EXPORTER_ENV`'s six keys
could move to a spelling the container reads differently with the guard still `PASS: 39/39`.

- **RED first, on the untouched tree** (`logs/red-step03a-case-lower.log`, guard `559d688f`):
  `METRICS_PREFIX=PLEX` **GREEN**, `METRICS_PREFIX=Plex` **GREEN**, `PLEX_SSL_VERIFY=True`
  **GREEN**, `PLEX_SSL_VERIFY=TRUE` **GREEN** — four fail-open rows at `PASS: 39/39`. Controls
  (`plexx`, `false`, `PLEX_TIMEOUT=1O`, key deleted) RED, five price rows GREEN. 15/15 as declared.
- **GREEN after the fix** (`logs/green-step03a-case-lower.log`, guard `8d3dc938`): the same four rows
  RED, controls still RED, all five price rows still GREEN — quoted and single-quoted scalars, a
  whole-line comment inside `environment:`, an inline comment, and reordered entries. 15/15.
- **Delivered tree unchanged:** guard standalone `PASS: 39/39`, `just test` **GATE PASS 35/35 exit 0**
  (`logs/gate-step03a-rework-f1.log`; `grep -ci promtool` = **0**, so the Builder's earlier
  correction still holds). The Critic's own 20-row battery re-run on the fixed tree is now
  **20/20 as declared** (`logs/battery-step03a-rework-f1-recheck.log`) where it was 18/20 — the two
  disagreements were exactly M1/M3.
- **The class was swept rather than patched at the one site** (DEC-058). Six case-folding sites in
  the guard; two deleted; four kept with the measurement beside each: `(?i)` in the leak detectors
  (455/2898/3005) BROADENS detection; `verify_ssl_off` (2827) mirrors
  `pve_exporter/config.py:54` `env['PVE_VERIFY_SSL'].lower() not in ['false','0']`, read out of the
  pinned image; and `addEntryPointsLabels`/`addServicesLabels` (1365-1366) are YAML booleans that
  `traefik:v3.7.5` itself folds — measured, `true` vs `True` byte-identical at `/metrics` 200 with
  the same entrypoint and service series (`logs/calibration-step03a-yaml-bool.log`).
- **Carry-forward corrected in place, not deferred:** `env.j2`'s comment and the
  `test_plex_token_sourced_from_vault` docstring stated the collector's rescue more broadly than
  `collector.rb` does. Both now say what it catches (`HTTP::Error`, connection-level only), name the
  TWO measured escapes on a rejected token (`JSON::ParserError` row B, `NoMethodError` row C), say
  the 500 carries ZERO series including `plex_up`, and note that a TLS handshake failure escapes it
  too — inert while `docker_host_plex_url` is `http://`.

Files touched: `scripts/test_traefik_config_shape.py` (the fix + three comment blocks),
`ansible/roles/docker_host/templates/env.j2` (comment only). Check count unchanged at 39.
No `just play`, no vault value, no live host access, **no commit**. Steps 1b and 2b untouched.

## Step 3a REWORK round 3 (`review.rejected` F1 → the value-strips) — task-1785370559-2a76

**F1 verified on disk before fixing it.** `scripts/test_traefik_config_shape.py:3229` was
`env_map.get(key, "").strip('"\'') != want` and :3232 the same for `port_agrees`. Both are gone.

- **RED first, on the untouched round-2 tree** (`logs/red-step03a-value-quotes.log`, guard
  `8d3dc938`): all EIGHT value-quoted spellings of the six pinned keys are **GREEN at `PASS: 39/39`**
  — `METRICS_PREFIX` and `PLEX_SSL_VERIFY` in both quote characters, `PLEX_TIMEOUT="10"`,
  `PORT="9594"`, `PLEX_RETRIES_COUNT='0'`,
  `METRICS_MEDIA_COLLECTING_INTERVAL_SECONDS="300"`. Controls that are quoted AND wrong
  (`"plexx"`, `"false"`) and the deletion are RED, so green-vs-red is the quotes alone. 19/19 rows
  as declared.
- **GREEN after the two deletions** (`logs/green-step03a-value-quotes.log`): the same eight rows RED,
  and all six price rows still GREEN — whole-ENTRY quoting in both quote characters (`_kv_entries`
  owns that quote), whole-entry quoting on the `PORT` key, a whole-line comment inside
  `environment:`, an inline comment, reordered entries. 19/19. `PORT="9594"` reddens BOTH clauses
  (`env_pinned=False (wrong={'PORT': '"9594"'})`, `port_agrees=False`), so the second strip site is
  independently exercised.
- **The severity split, carried per row rather than flattened.** `PLEX_TIMEOUT="10"` is the live and
  silent one: `collector.rb:13` is `ENV[...]&.to_i` and `'"10"'.to_i` is 0 in Ruby, so every request
  times out inside the rescue that reports it as `plex_up 0` — 200, healthy, target UP, and 3b's two
  falsifier series ABSENT. `PLEX_SSL_VERIFY="true"` is round 2's M3 reached through quotes. A quoted
  sweep interval makes the synchronous library sweep run on every scrape. `METRICS_PREFIX="plex"`
  and `PORT="9594"` fail LOUD (boot `ArgumentError` on the metric name; `URI::InvalidURIError` on
  the puma bind) and are not the blocker.

**The class was closed rather than the two sites (DEC-059), and this half is a MEASUREMENT the
review did not have.** The review's criterion for the sites it kept — those readers hold a raw
capture, so one unquoting is the parser's own work — is right, and a bare deletion there would
redden the ordinary one-layer spelling. But `str.strip(chars)` does not implement that criterion; it
strips repeatedly. Measured on the pinned `prom/prometheus:v3.12.0` against a stub at the real
service name (`logs/calibration-step03a-doubled-quotes.log`, `-s2.log`):

| spelling | promtool | target | series |
|---|---|---|---|
| `- plex-exporter:9594` | accepted | **UP**, `http://plex-exporter:9594/metrics` | `up=1` |
| `- "plex-exporter:9594"` | accepted | **UP**, identical to the bare form | `up=1` |
| `- '"plex-exporter:9594"'` | **accepted** | **DOWN**, `http://"plex-exporter:9594"/metrics`, `invalid port ":9594\"" after host` | `up=0` |

So all eleven remaining sites moved to `_yaml_unquote`, which removes exactly ONE matched pair.
`logs/red-step03a-doubled-quotes.log` / `green-...`: **15/15 as declared in BOTH modes** across five
readers — D1-D6 (targets, `_duration_seconds`, `_top_level_list`, `_param_values` block AND flow
forms, the reload contract's `notify:` capture) GREEN before and RED after; S1-S6, the one-layer
price, GREEN in both; C1-C3 controls RED in both. The `pre` leg counter-mutates only the helper's
body and restores it in a `finally`, because `git stash` would land on HEAD's 30-check guard rather
than this objective's uncommitted 39-check tree.

**Severity of that half, stated honestly: it is weaker than F1's.** Every doubled spelling lands in
the visible bucket (DOWN target with `up 0`, a config Prometheus refuses, a handler not found), not
the silent-healthy 200. Fixed because the guard was green on trees that cannot work and one layer
costs nothing.

**Delivered tree.** Guard standalone `PASS: 39/39`; `just test` **GATE PASS 35/35 exit 0**
(`logs/gate-step03a-rework-quotes-final.log`, `grep -ci promtool` = **0**). The Critic's own 20-row
battery re-run unchanged is **20/20 as declared** (`logs/battery-step03a-round3-recheck.log`). The
Critic's 16-row quote battery re-run in its `pre` mode
(`logs/review-quotes-step03a-round3-recheck.log`) now disagrees on **exactly its eight Q rows and
nothing else** — they read RED where it declared GREEN, because the fix landed — so the change is
scoped to precisely what F1 claimed.

Files touched: `scripts/test_traefik_config_shape.py` only (guard `8d3dc938` → `32e338e3`).
`compose.yml.j2 c519900b`, `prometheus.yml.j2 133e356c`, `env.j2 6760ae43`, `defaults 8046511b`,
`vars.yml 90935713`, `tasks/main.yml 6de82192`, `dynamic.yml.j2 fe24729c` — identical at both ends.
Check count unchanged at 39. Two containers plus one network per calibration leg, all removed in a
`finally`; `docker ps -a` / `network ls` clean. No live host access, no `just play`, no vault value,
**no commit**. Steps 1b (`task-1785290391-b51a`) and 2b (`task-1785324247-3934`) untouched.

## 2026-07-30 — Builder, Step 3a REWORK round 4 (review.rejected F1 → `_kv_entries`' `.strip()`)

Task `task-1785370559-2a76`, key `code-assist:plex-monitoring:step-03:plex-exporter-repo-wiring`.
One repo file touched: `scripts/test_traefik_config_shape.py`, guard `32e338e3` → `57021341`.
Check count unchanged at **39**.

**The fix is one expression.** `_kv_entries` ended in `out[m.group("key")] = m.group("val").strip()`;
it now ends in `= m.group("val")`. That reader is shared by `env_pinned`, `port_agrees` AND
`addr_from_var`, which is why rounds 2 and 3 deleted `.lower()` and `.strip('"\'')` from the CLAUSE
and left the operator with the widest reach sitting upstream of all three.

**RED then GREEN, 21 rows, my own harness** (`logs/red-step03a-whitespace.py`, run twice:
`red-step03a-whitespace.log` pre, `green-step03a-whitespace.log` post) — every row mutates the REAL
`compose.yml.j2` and reverts in a `finally`, and each row also prints what `_kv_entries` RESOLVED,
imported from the guard under test:

| rows | pre (guard `32e338e3`) | post (guard `57021341`) |
|---|---|---|
| W1-W11 whitespace spellings (11, incl. a TAB and the `PLEX_TOKEN` credential entry) | GREEN `PASS: 39/39` | **RED** |
| C5 duplicate `PLEX_TIMEOUT= 10` appended (round 14's last-wins class) | GREEN | **RED** |
| C1-C4 controls (wrong value, deletion, INTERNAL space, literal `PLEX_ADDR`) | RED | RED |
| P1-P5 price (whole-entry quotes ×2, trailing on a plain scalar, trailing after a closing quote, extra space after the `-`) | GREEN | GREEN |

**21/21 as declared in both modes**, delivered tree `PASS: 39/39` in both. `just test`
**GATE PASS 35/35 exit 0** (`logs/gate-step03a-r4-builder.log`, `grep -ci promtool` = 0).

**C3, the row the review invited me to attack, holds — and the instrument says why.** With the strip
in place `_kv_entries` returns `PLEX_TIMEOUT='1 0'` for C3 but `'10'` for W5, the same key: the
internal space reddens through the VALUE COMPARE (the value really is `1 0`), while the leading space
was laundered before the compare ever happened. Green-vs-red is the leading/trailing fold
specifically, exactly as the review attributed it.

**The premise, re-measured rather than inherited** (`logs/green-step03a-whitespace-process.py/.log`,
real rendered template, pinned image, `cat -A` on the process environment): `- PLEX_SSL_VERIFY= true`
→ `' true'` → `< true>`; `- "PLEX_SSL_VERIFY=true "` → `'true '` → `<true >`; a TAB survives as
`<^I10>`; `- PLEX_ADDR= {{ var }}` → `< http://192.168.1.110:32400>`. The two layers the fix KEEPS
are compose's own: trailing whitespace on a plain scalar resolves to `"10"` and whole-entry quotes to
`plex`. Severity is NOT re-priced here — the review measured it on the pinned image and this round
accepts it.

**The sweep, both halves, because rounds 2 and 3 were each rejected for the next site of one class.**
- Static: `logs/sweep-step03a-whitespace-sites.py/.log` enumerates **all 32 folds across 23
  functions** and requires every one to be classified; an unclassified site prints `SWEEP FAIL`.
  Result **SWEEP PASS** — one FIXED, the rest parser-owned, detector-widening, runtime-mirroring, or
  structural (emptiness/indent tests).
- Measured: `_label_members` was the one keeper that could not be settled on paper, and it is live on
  the allowlist claim (eleven routers spell the label as a two-member comma list). On pinned
  `traefik:v3.7.5` with the DOCKER provider and `internal-allowlist` given a sourceRange the request
  is NOT in (`logs/sweep-step03a-whitespace-label-list.py/.log`): S1 control and all four whitespace
  spellings S2-S5 are `enabled` + **403**, i.e. Traefik's own decoder trims each member and the
  allowlist RUNS; the bad-ref control S6 is `disabled`,
  `middleware "nonexistent@file" does not exist`, **404**. So that `.strip()` mirrors the parser and
  stays — and an unresolvable reference is a visible failure, not a silent bypass.

Two harness mistakes recorded in the artifacts rather than deleted: the label leg's first draft read
the Traefik API before the router had been replaced (S6 came back identical to S1 — a stale read, now
fixed by waiting for the router to disappear first), and the process leg's first draft ran
`stdout.strip()` and so ate the very leading space rows A2/A6 exist to show — F1's own defect,
committed by F1's own harness.

Cleanup: `docker compose run`'s `tmp*_default` networks are torn down per row and the eight left by
the first draft were removed explicitly; label-leg containers and network removed in a `finally`;
`docker ps -a` / `network ls` clean. No live host access, no `just play`, no vault value, **no
commit**. Steps 1b (`task-1785290391-b51a`) and 2b (`task-1785324247-3934`) untouched.

## 2026-07-30 — Step 3a REWORK round 5 (task-1785370559-2a76), `review.rejected` F1 → the entry the reader CANNOT read

**Active task:** Step 3a, `code-assist:plex-monitoring:step-03:plex-exporter-repo-wiring`. One repo
file touched: `scripts/test_traefik_config_shape.py` (`57021341` → `07962df2`). `compose c519900b`,
`prom 133e356c`, `env.j2 6760ae43`, `defaults 8046511b` identical at both ends.

**The fix (F1).** `_kv_entries` ended in `out[key] = val` and skipped what it could not read, so an
earlier readable entry stood while the runtime resolved the region LAST-WINS and took the entry the
guard could not read; its docstring claimed the opposite. Now one rule on a shared helper
(`_unreadable`): readable → assign, unreadable with a discernible key → that key becomes
`UNREADABLE`, unreadable with NO key → every key assigned so far does. Absent keys need no poison —
the callers already redden on them (C2/C3).

**RED → GREEN, 29 rows, both modes as declared** (`logs/red-step03a-unreadable-entry.py`,
`--mode pre` → `red-…log`, `--mode post` → `green-…log`; every row mutates the REAL template and
reverts in a `finally`, shas at both ends, each row printing what the guard's OWN reader resolved):
17 fail-open rows GREEN before / RED after — the review's eight bare `- KEY` entries (K1-K8), a
MULTI-LINE entry and a MAPPING entry and a KEYLESS one (K9-K11, shapes no round had tested), the two
labels rows (L1-L2), `volumes:` (V1-V2) and the `.env` (E1-E2). Six controls RED in both, six price
rows GREEN in both. Delivered tree `PASS: 39/39` in both modes; `just test` **GATE PASS 35/35 exit 0**
(`logs/gate-step03a-rework-r5.log`, `grep -ci promtool` = 0); check count unchanged at 39.

**The class is the READER, and the sweep found the review's bound was one spelling wide.**
`logs/sweep-step03a-unreadable-entry-sites.py` enumerates every per-entry MAP builder **from the
guard's AST** (7 functions) and prints `SWEEP FAIL` on any unclassified one or any FIXED one that no
longer poisons — **SWEEP PASS**, and non-vacuous: deleting the poison from `_kv_entries` prints
`SWEEP FAIL … never calls _unreadable`, rc=1 (`logs/sweep-step03a-unreadable-entry-vacuity.log`).
Two more live sites, both measured rather than argued
(`logs/green-step03a-unreadable-entry-process.log`, real `docker compose` v5.3.1):

- `_service_mount_map` (`volumes:`) — a single-part entry is an ANONYMOUS VOLUME that takes the
  target and the bind is GONE (`cat: Is a directory`); a long-form `type/source/target` entry WINS
  (container reads the shadow file). Both are the silent path this clause's own docstring names:
  Prometheus starting on the image default and scraping nothing but itself. FIXED (poison).
- `_env_assignments` (the `.env`) — the review called this reader immune, from the one spelling dotenv
  really does ignore (`PLEX_TOKEN` with no `=`, row E3 → `real-token`, unchanged). `export PLEX_TOKEN=`
  is not that spelling: it is READ and it WINS (`real-token` → `""`), and `export PLEX_TOKEN=stolen` →
  `stolen`. Here the fix MIRRORS the parser (read `export`) instead of poisoning — rounds 2-4's own
  criterion applied to this operator. E1 is the vault hop going empty behind a green guard, i.e.
  Step 3b's failure list.
- `command:` (`_service_command_args` + `_last_flag_value`) is the one immunity claim worth measuring
  and leg I runs it: a multi-line and a single-line `--config.file=` decoy are both RED, the quoted
  delivered spelling still GREEN.

**Premise attacked as instructed** (`logs/green-step03a-unreadable-entry-traefik.log`, pinned
`traefik:v3.7.5`, docker provider, label read off `docker inspect`, `internal-allowlist` given a
sourceRange the request is NOT in): T1 control **403**, T2 empty label **200** with
`status=enabled, middlewares=None, error=None`, T4 no label at all **identical**, T3 bad ref
`disabled` + `middleware "nonexistent@file" does not exist` + 404. The discriminators settle the
mechanism the review guessed at: `,` decodes to `['@docker','@docker']` and `'   '` to `['@docker']`,
both **disabled + 404**, so the empty value is DROPPED (empty means ABSENT) rather than decoded to an
empty list. The verdict is unchanged and sharper — the silent shape is exactly the empty value a bare
`- …middlewares` entry produces, and eleven routers spell that label.

**Compose REJECTS two of the eleven K shapes and I report that rather than implying all are silent:**
`- PLEX_ADDR: http://evil:1` and a bare `-` are rc=1 (`unexpected type map[string]interface {}` /
`unexpected type <nil>`), i.e. LOUD; K1-K3 resolve to `null` with the variable ABSENT from the process
environment (`in env: 0`), and K9's multi-line folds to `http://evil:1 andmore` and DOES reach the
process. Containers and networks removed per row; `docker ps -a` shows none of mine. No live host
access, no `just play`, no vault value, **no commit**. Steps 1b (`task-1785290391-b51a`) and 2b
(`task-1785324247-3934`) untouched.

## 2026-07-30 — Step 3a REWORK round 6 (review.rejected F1 → the ACCEPT side)

Active task: `task-1785370559-2a76` (`code-assist:plex-monitoring:step-03:plex-exporter-repo-wiring`).
Only `scripts/test_traefik_config_shape.py` modified (`07962df2` → `79faa396`).

| command | result |
|---|---|
| `python logs/red-step03a-accept-side.py --mode pre` | ROWS PASS — A1-A6 GREEN (fail-open), C1-C3 RED, P0-P2 GREEN, R leg 17 entries / 7 Jinja |
| `python logs/red-step03a-accept-side.py --mode post` | ROWS PASS — A1-A6 now RED, controls and price rows unmoved |
| `python logs/sweep-step03a-accept-side.py` | SWEEP PASS — 12 entry readers classified, legs V/P/Q/K/R/S measured |
| vacuity (`--guard` on a copy with the gate deleted) | SWEEP FAIL rc=1, `_service_mount_map … never calls _scalar_entry` |
| `python logs/green-step03a-accept-side-process.py` | LEG D PASS — A1/A3/A5/A6 serve the SHADOW on pinned prom/prometheus:v3.12.0; A4 REFUSED (rc=1) |
| `python logs/sweep-step03a-unreadable-entry-sites.py` (round 5's reject-side sweep) | SWEEP PASS, unchanged |
| `python logs/red-step03a-unreadable-entry.py --mode post` (round 5's 29 rows) | 29/29 as declared |
| `just test` | **GATE PASS 35/35, exit 0** (`logs/gate-step03a-rework-r6.log`) |
| delivered guard | `PASS: 39/39`, check count unchanged at 39 |

Templates identical at both ends of every harness: compose `c519900b`, prom `133e356c`,
env.j2 `6760ae43`, defaults `8046511b`. No live host access, no `just play`, no vault value,
no commit. Operator gates 1b / 2b / 3b untouched.

## 2026-07-30 — Step 3a REWORK round 7 (review.rejected F1 → the JINJA KEY; F2 → the allow-list)

Active task: `task-1785370559-2a76` (`code-assist:plex-monitoring:step-03:plex-exporter-repo-wiring`).
Only `scripts/test_traefik_config_shape.py` modified (`79faa396` → `0b4e6645`). DEC-063.

F1 was the mount TARGET; the fix is the CLASS, because the target is only one of five
in-string keys this guard reads out of a template. One shared predicate `_resolvable_key`,
five call sites (`_service_mount_map`, `_kv_entries` ×2 branches, `_env_assignments`,
`_last_flag_value`). F2 is `no_multi_target_shape`, converted from an absence pin over three
names to an allow-list over the job's own key column via the existing `_service_key_lines`.

| command | result |
|---|---|
| `python logs/red-step03a-jinja-key.py --mode pre` | ALL ROWS AS DECLARED — **9** FAIL-OPEN rows GREEN at `PASS: 39/39` against the real round-6 guard `79faa396` (J1 J2 J3 K1 K2 L1 E1 G1 G2) |
| `python logs/red-step03a-jinja-key.py --mode post` | ALL ROWS AS DECLARED — **10** FAIL-OPEN rows RED, controls unmoved, price rows K4/E3 GREEN |
| C1's BEFORE verdict | C1 was added AFTER the fix landed, so it has no round-6 run; its before-verdict comes from the vacuity harness (gate removed → C1 GREEN), which is the sharper instrument anyway |
| leg B (`docker compose config --format json`) | rc=0 — J1/J2/J3 land the SHADOW at the delivered target; K1/K2 resolve `PLEX_ADDR` to `http://stolen:1`; L1 empties the whoami allowlist |
| leg E (rendered `.env` as `--env-file`) | rc=0 — E1 resolves `PLEX_TOKEN` to `stolen`; E3 (no `=`) keeps `plex-tok`, so the skip mirrors dotenv |
| leg P (`promtool check config`, pinned prom/prometheus:v3.12.0) | rc=0 on ALL FOUR job rows — `file_sd_configs` and `scheme: https` are deployable, not syntax errors |
| leg Q (the PROCESS, same image) | delivered args `state=running`; C1 (Jinja arg) and C2 (literal decoy) both `state=exited 2` — byte-identical states, and the guard saw only one |
| leg D (the PRICE, per region) | 0 Jinja KEYS delivered anywhere: volumes 17 entries / 7 Jinja SOURCE / 0 TARGET; environment 16 + labels 55 / 19 Jinja VALUE / 0 KEY; `.env` 5 / 5 VALUE / 0 KEY |
| `python logs/vacuity-step03a-jinja-key.py` | **EVERY GATE BITES** — six gates, each removed alone from a COPY, each one's rows all flip GREEN without it |
| `python logs/sweep-step03a-key-side.py` | **SWEEP PASS** — 21 signature matches all classified (round 6's signature matched 12) |
| vacuity (`--vacuity _service_mount_map`) | **SWEEP FAIL** rc=1, `_service_mount_map is classified KEYED but never calls _resolvable_key` |
| `just test` | **GATE PASS 35/35, exit 0** (`logs/gate-step03a-r7.log`) |
| delivered guard | `PASS: 39/39`, check count unchanged at 39 |

Templates identical at both ends of every harness: compose `c519900b`, prom `133e356c`,
env.j2 `6760ae43`, defaults `8046511b`. No live host access, no `just play`, no vault value,
no commit. Operator gates 1b / 2b / 3b untouched.

TWO SURFACES I DID NOT SETTLE, stated rather than implied:
1. `RELOAD_CONTRACT`'s `config_flag: None` branch (traefik) trusts the image's default path.
   Traefik has no `command:` today, so nothing exercises it — but a `command:` added there
   with a `--configFile=` would move the read SILENTLY and this pin would not notice. That is
   an enumeration gap in the contract, not the Jinja-key class, and I left it alone.
2. J4 is LOUD and declared as a price row: a Jinja target that shadows NOTHING reddens too.
   Zero delivered entries carry one, so the cost falls entirely on entries nobody has written.

## Step 3a REWORK round 8 (review.rejected F1 → the Jinja that MOVES THE SPLIT) — task-1785370559-2a76

F1 was on disk as routed (guard `0b4e6645`, `logs/review-step03a-r8-jinja-split.py/.log`
present) and I ran RED first. The review is right and the reason is one layer deeper than the
region: `_resolvable_key` is asked about a FIELD that a Jinja-blind `str.split` produced, and a
Jinja construct is a delimited SPAN — one containing the separator puts its OPEN in the
previous field (the source/value side, where round 6 correctly allows it) and only its CLOSE in
the key. Fix: `_JINJA_OPEN` → `_JINJA_DELIM = re.compile(r'\{[{%#]|[}%#]\}')`, matching both
ends of the pair. Guard `0b4e6645` → `07aee483`; **no other repo file touched**.

| command | result |
|---|---|
| `python logs/red-step03a-jinja-close.py --mode pre --patch-open` | **BATTERY PASS** — 4 FAIL-OPEN rows GREEN at `PASS: 39/39` under the round-7 predicate (M1 M2 M3 M7); controls M4/M5/M6/K2 RED; 5 price rows GREEN |
| `python logs/red-step03a-jinja-close.py --mode post` | **BATTERY PASS** — M1/M2/M3/M7 RED, controls unmoved, P1–P5 still GREEN, delivered `PASS: 39/39` |
| leg B (`docker compose config --format json`) | rc=0 on every row — M1/M2/M7 put `/srv/monitoring/prometheus/legacy.yml` at `/etc/prometheus/prometheus.yml`, M3 puts `legacy-traefik.yml` at `/etc/traefik/traefik.yml`. Deployable states, not syntax errors |
| leg S (the SEVERITY boundary) | S1–S4 RED in **both** modes: a role variable holding the tail, a bare `{{ ':' }}` separator, a `{% if %}` straddle, the conditional either-or. The ordinary spellings were already fail-closed |
| leg V (NON-VACUITY per HALF) | delivered `PASS: 39/39` under each half alone. OPEN only → M1/M2/M3/M7 GREEN, K2 RED. CLOSE only → M1/M2/M3/M7 RED, K2 GREEN. Both halves load-bearing, in different regions |
| leg D (the PRICE, read through the guard's OWN slicers) | 96 delivered keys — volumes 17, environment 16, labels 55, command 3, `.env` 5 — **0** carrying a Jinja CLOSE, 0 carrying an OPEN |
| `python logs/red-step03a-jinja-key.py --mode post` (round 7's battery) | **ALL ROWS AS DECLARED**, 22/22 leg-A rows unmoved by this change |
| `python logs/vacuity-step03a-jinja-key.py` | **EVERY GATE BITES** (unchanged) |
| `python logs/sweep-step03a-key-side.py` | **SWEEP PASS** (unchanged) |
| `just test` | **GATE PASS 35/35, exit 0** (`logs/gate-step03a-r8-jinja-close.log`) |
| delivered guard | `PASS: 39/39`, check count unchanged at 39 |

Templates identical at both ends of every harness: compose `c519900b`, prom `133e356c`,
env.j2 `6760ae43`, defaults `8046511b`. No live host access, no `just play`, no vault value,
no commit. Operator gates 1b / 2b / 3b untouched.

STATED RATHER THAN IMPLIED:
1. `%}` and `#}` are in the delimiter class for SYMMETRY. I could not construct a fail-open
   spelling for either — statements come in pairs, so the partner tag puts an OPEN back in the
   same field (row S3 is that measurement). Leg D prices them at zero.
2. The split in `_short_mount_fields` stays Jinja-blind ON PURPOSE. Tokenizing Jinja there
   would be a second parser to get wrong, and the boundary-moving trick is a property of every
   splitter in the file — so the consequence is caught where it lands, in the caller's KEY.
3. The two surfaces round 7 left unsettled are still unsettled and still outside this class:
   `RELOAD_CONTRACT`'s `config_flag: None` branch, and the sweep's inability to see that a
   predicate's ARGUMENT is untrustworthy (it only checks that the predicate is CALLED).

### Step 3a — REWORK round 9 (`review.rejected` F1 → the line the guard never sees)

F1 was `_strip_comments` dropping `#{{ CHR10 }}PLEX_TOKEN=stolen-shadow`. I built the review's
rows first, then asked its own altitude question — is the carrier the COMMENT or the NEWLINE? —
and the answer moved the fix.

| command | result |
|---|---|
| `python logs/red-step03a-line-manufacture.py --mode pre` (round-8 guard) | **BATTERY PASS, 14/14 rows as declared.** SIX fail-open rows GREEN at `PASS: 39/39`: N1/N2/N3 (the review's comment carrier) **and V1/V2/V3, which carry no `#` at all** |
| leg B (ansible-core jinja2 → `docker compose config --format json` / dotenv) | rc=0 on all six. N1/V1 → dotenv last-wins `PLEX_TOKEN = 'stolen-shadow'`; N2/V2 → `PLEX_ADDR = 'http://stolen:1'`; N3 → `/etc/prometheus/prometheus.yml <- /srv/monitoring/prometheus/legacy.yml`; **V3 → `traefik.http.routers.prometheus.middlewares = 'security-headers@file'`, the internal-allowlist gone (Error-1000 class)** |
| controls C1–C4 (same shadow, no carrier) | RED in both modes — green-vs-red is purely the carrier |
| bounding rows B1/B2 (`volumes:` key line, `volumes:` entry tail) | RED in both modes — already fail-closed via the block opener and `_short_mount_fields`' field count. The fix is not credited with them |
| destruction probes D1/D2 (`{% if False %}` around a pinned line) | RED in both modes — already fail-closed via `_env_assignments`' and `_service_mount_map`' `{%` poison. Two sites, not a proof |
| `python logs/red-step03a-line-manufacture.py --mode post` | **BATTERY PASS, 14/14.** N1/N2/N3 + V1/V2/V3 all RED at `FAIL: 1/40` |
| `python logs/green-step03a-line-manufacture-price.py` leg P | **PRICE ZERO** — 77 delivered constructs (70 bare references, 5 `\| default('')`, 2 `if`/`endif`), 0 rejected, printed row by row |
| same, leg V (vacuity) | **EVERY CLAUSE BITES** — 10 reject probes, one per clause, each for its own reason; 5 accept probes, no false red |
| same, leg S (the sweep) | 19 text-to-structure readers listed from the guard's own AST; **10 never call `_strip_comments`**, which is why the fix is not there |
| `just test` | **GATE PASS 35/35, exit 0** (`logs/gate-step03a-r9-line-manufacture.log`) |
| delivered guard | `PASS: 40/40` (39 → 40, one new check) |

Only `scripts/test_traefik_config_shape.py` changed (`07aee483` → `38b002ed`). Templates
identical at both ends of every harness: compose `c519900b`, prom `133e356c`, env.j2 `6760ae43`,
traefik.yml.j2 `4ea627dc`, dynamic.yml.j2 `fe24729c`, defaults `8046511b`. No live host access,
no `just play`, no vault value, no commit. Operator gates 1b / 2b / 3b untouched.

STATED RATHER THAN IMPLIED:
1. I did NOT take the review's priced fix (B). Not because it is wrong — it flips N1–N3 — but
   because V1/V2/V3 prove the carrier is the NEWLINE, and (B) cannot reach a value position. On
   top of this pin it would also be vacuous: no row isolates it.
2. Residual one: a bare `{{ var }}` whose VARIABLE VALUE holds a newline is invisible to any
   text-level pin. Every delivered construct is a reference, so that is the whole remaining
   surface of this class. The review disclosed the same residual against its own proposal.
3. Residual two: DESTRUCTION (`{% if False %}` removing a pinned line) is NOT closed here,
   because dynamic.yml.j2 spells the conditional legitimately. D1/D2 measure two sites and both
   are already fail-closed; that is an enumeration gap, named as one.
4. A future template that genuinely needs `{% for %}` will redden check #40. That is the intended
   reading: teach the clause what the loop can emit — the alternative is a guard whose line
   numbers are a guess.

## 2026-07-30 — Builder, Step 3a REWORK round 10 (review.rejected F1 → the RENDERER that deploys) — task-1785370559-2a76

**F1: check #40's accept rule declares `if/elif/else/endif` line-bounded. True of the STATEMENT,
false of the LINE.** `ansible.builtin.template` renders with `trim_blocks=True` (ansible-core
2.21.1, `plugins/action/template.py:58`) and `lstrip_blocks=False` (`:59`); the role overrides
neither (leg R greps the whole `ansible/` tree — the only hit is dynamic.yml.j2's own comment
"trim_blocks keeps YAML valid"). So the newline after a `%}` is DELETED and a block tag beside
content moves the line boundary even though the statement emits nothing.

**Increment: one guard file.** `scripts/test_traefik_config_shape.py` `38b002ed` → `ddc7e8eb`.
New `_unbounded_block_tag(text, start, end, body)` carries the `{%` half of
`_line_manufacturing_jinja`; `_WS_CONTROL_MARKER` beside `_LINE_BOUNDED_STMT`. Check count
unchanged at 40 — this is one clause inside round 9's check, not a new one.

THREE CLAUSES, EACH WITH ITS OWN ROW (`logs/red-step03a-trim-blocks.py --mode pre|post`,
**12/12 rows as declared in BOTH modes**, every row mutating a real template and reverting in a
`finally`, shas at both ends):

| row | carrier | pre | post | runtime at `trim_blocks=True` |
|---|---|---|---|---|
| T1 | `{% if true %}` at the END of a labels entry, `{% endif %}` on the last | PASS 40/40 | FAIL 1/40 (#40) | `compose config` rc=0, prometheus `middlewares = None` |
| T1b | same, `{% endif %}` standalone at column 0 | PASS 40/40 | FAIL 1/40 (#40) | same |
| T2 | column-0 tag with CONTENT AFTER it, below the last pinned label | PASS 40/40 | FAIL 1/40 (#40) | rc=0, `middlewares = 'security-headers@file'` |
| T4 | INDENTED tag alone, above a column-0 entry (re-indents it INTO the block) | PASS 40/40 | FAIL 1/40 (#40) | rc=0, `middlewares = 'security-headers@file'` |
| T3 | `{% if true -%}` — the marker joins what column 0 cannot | PASS 40/40 | FAIL 1/40 (#40) | rc=**1**, `did not find expected key` → LOUD |
| T2c | T2's trick ABOVE a pinned label | FAIL 1/40 | FAIL 2/40 | rc=0, allowlist gone — red for an INCIDENTAL reason |
| Bm | `{%- if true %}` | FAIL 1/40 | FAIL 1/40 | already refused before this round |
| C1 | the label simply DELETED | FAIL 2/40 | FAIL 2/40 | rc=0, `middlewares = None` |
| C2 | the identical `shadow.note` entry, NO tags | PASS 40/40 | PASS 40/40 | rc=0, allowlist INTACT |
| B1/B2 | the same merge in the `.env` / compose `environment:` | RED | RED | already fail-closed |
| D1 | `{% if False %}` around the vault hop (destruction) | RED | RED | round 9's row, unmoved |

Every fail-open row reddens on **check #40 itself**, each for its own reason — attribution
printed per row, not inferred from the count.

| gate | result |
|---|---|
| `just test` | **GATE PASS 35/35 exit 0** (`logs/gate-step03a-r10-trim-blocks.log`) |
| delivered guard | `PASS: 40/40` |
| price | **ZERO** — 77 delivered constructs, 0 rejected; the tree's only two block tags are dynamic.yml.j2's pair, already column-0 and marker-free |
| vacuity | 12 probes, each accepted/rejected for its OWN printed reason (leg P) |

**The instrument was the reason round 9 missed this**, and it is fixed here: round 9's battery
rendered with `jinja2.Environment(keep_trailing_newline=True)` and no `trim_blocks`. Leg R prints
the delivered dynamic.yml.j2 at **109 template lines → 107 rendered with trim_blocks, 109
without** — the instrument disagreed with deployment on the DELIVERED tree, before any mutation.

Only the guard changed. compose `c519900b`, prom `133e356c`, env.j2 `6760ae43`, traefik.yml.j2
`4ea627dc`, dynamic.yml.j2 `fe24729c`, defaults `8046511b` identical at both ends. No live host
access, no `just play`, no vault value, no commit. Operator gates 1b / 2b / 3b untouched.

STATED RATHER THAN IMPLIED:
1. T3's row is a guard-COMPLETENESS row, not a severity row: at the `labels:` site the `-%}`
   dedent is LOUD (`docker compose config` rc=1). The clause stays because a column-0 rule that
   permits the renderer's own whitespace operator is unsound, not because it buys severity.
2. T2c is recorded because its red is INCIDENTAL (the column-0 line ends the block before labels
   the guard pins). Placement is what makes T2 reachable; that is a property of the tree today,
   not a bound.
3. DESTRUCTION is still not closed (D1) — unchanged from round 9, and this clause does not touch
   it. Nor is residual (1): a bare `{{ var }}` whose VALUE holds a newline.
4. The renderer settings are now part of the claim in writing: any future battery over these
   templates must render `trim_blocks=True, lstrip_blocks=False, keep_trailing_newline=True`.

---

## Step 3a REWORK round 11 (task-1785370559-2a76) — the DELETE direction, and the unasked twin

Two blockers, both routed as measured to HTTP 200 and both landed at **price zero**. Only
`scripts/test_traefik_config_shape.py` changed: git-blob `ddc7e8eb` -> `15bdb43b`
(the battery's own sha256/8 spelling: `7b3105ea` -> `2fe4bc38`).

**F1 — the clause that closed the MERGE direction blessed the DELETE direction.** Round 10's
`_unbounded_block_tag` refuses every `{% %}` spelling except the column-0 standalone tag — which
is exactly the shape that DELETES the lines it wraps. Rounds 9 and 10 both bounded destruction at
the `.env` and compose `volumes:`, both fail-closed on `{%` poison that predates them;
dynamic.yml.j2 was never asked, and it is the file where a column-0 line is ORDINARY (it ships
such a gate at line 84, and `_router_block` is TAUGHT to read straight through it). New check #41
`test_no_undeclared_conditional_region`: the `{% if %}`…`{% endif %}` regions across
`LINE_READ_TEMPLATES` must EQUAL the one region this repo deliberately ships — an INVENTORY
(condition AND the lines wrapped, compared as a MULTISET), not a membership test, because rounds
6 and 7 both rejected absence pins bounded by an enumeration.

**F2 — no Jinja required at all.** `test_tunnel_web_routers_present` states four clauses, names
`traefik-dashboard-web` in its own docstring, asks all four of the compose twins, and asked that
one clause (1) only. It is now asked (2), (3) and (4) from its own block, the same shape the
twins are read with.

| leg | result |
| --- | --- |
| battery | `logs/red-step03a-r11-unasked-clauses.py --mode pre\|post` — **15/15 rows as declared in BOTH modes** |
| gate | `just test` **GATE PASS 35/35 exit 0** (`logs/gate-step03a-r11-unasked-clauses.log`) |
| delivered guard | `PASS: 41/41` (was 40/40) |
| price | **ZERO** — 1 region across the six line-read templates, and it is the declared one |
| vacuity | 9 probes + leg D, each answered for its OWN printed reason (`logs/green-step03a-r11-region-price.log`) |

Nine rows GREEN->RED: X1 (dashboard-web's allowlist gated away — the WAN row), X2 (the websecure
twin), X3 (the middleware DEFINITION), X4/X6 (the declaration's own two edges), P1-P4 (the four
ordinary-YAML mutations of the unasked twin). Controls unmoved: B1 (compose `labels:`) and N1
(`whoami-web`) RED in both modes, G0/G1/G2 GREEN in both.

STATED RATHER THAN IMPLIED:
1. X4 and X6 are COMPLETENESS rows, not severity: the declared condition is TRUE on the delivered
   tree, so a region carrying it emits. The severity is X1-X3, where a FALSE condition deletes.
2. X5 (the declared region REPLACED by a same-signature decoy) is already fail-closed via
   `test_traefik_dashboard_wildcard_domains`; #41 reddens it too, on its own terms, which is why
   the key is the BODY and not a signature — but the fix is not credited with that row.
3. F2 is PRE-EXISTING Step-2a work, not round 10's. It is landed here because it is in this file,
   price zero, and measured at HTTP 200.
4. NOT CLOSED, and named: nothing in this module evaluates a condition's TRUTH VALUE. `le-dns-cf`
   is pinned in group_vars by `test_acme_resolver_is_dns_cf`, which is the only reason the
   declared region is known to emit; ansible variable precedence puts an inventory-level override
   outside what any of these checks can see. Residual (1) from round 9 — a bare `{{ var }}` whose
   VALUE holds a newline — is unchanged.

## 2026-07-30 — Builder, Step 4a (task-1785442414-452f) — BUILT, `review.ready`

**THE TASK SHIPPED TWO DEFECTS AND ONLY ONE OF THEM EXISTS.** Both were measured against the pinned
image, offline, before a line of fix was written — the task's own instruction ("if a measurement
contradicts D1 or D2, say so and flip the fix").

    A1  grafana/grafana:13.1.0   Config.User='472' -> id: uid=472(grafana) GID=0(root)
    A2  prom/prometheus:v3.12.0  -> uid=65534 gid=65534          (the contrast, and the whole story)
    B1  DELIVERED tree (0750 dirs / 0640 files root:root, :ro) read as 472:0     READABLE
    B2  the same tree at 0700/0600                                               DENIED (control)
    B3  the same tree at 0755/0644                                               READABLE
    B4  the DELIVERED tree read as 472:472                                       DENIED
    D1  a REAL server booted on the delivered tree: datasource provisioned AND
        dashboard.grafana.app/dashboards/homelab-overview in its store, no permission line
    C1  datasource with NO uid:  -> stored uid `PBFA97CFB590B2093`   (the JSON asks "Prometheus")
    C2  datasource with uid: Prometheus -> stored uid `Prometheus`

**D1 (the modes) is FALSE.** A uid with no explicit gid runs with gid 0 and these files are
`root:root`, so the ROOT-GROUP bits answer for this container. `prometheus.yml` needed `0644` for
the opposite reason, also measured: `65534:65534` matches neither owner nor group. **D2 (the uid)
is TRUE** and is the one functional change: `uid: Prometheus` on the provisioned datasource, which
makes it agree with the four references already in `grafana-homelab-dashboard.json` — so the JSON
needed no edit at all.

**THE GUARD STATES THE PROPERTY, NOT THE NUMBER** (`scripts/test_grafana_provisioning_shape.py`,
9 checks): the delivered owner/group/mode must grant read (+traverse for dirs) to the identity
`uid 472, gid {0}`, evaluated as POSIX access. `0750 root:root` passes on the group bit, `0755`
passes on the other bit — a guard demanding `0755` would have forbidden the delivered tree, which is
the failure this repo has already hit. Its COMPANION is in another file and is checked: the identity
holds only while `compose.yml.j2` declines to override `user:` away from gid 0 (B4).

**Battery: 17/17 rows as declared, every watched file byte-identical at both ends**
(`logs/red-step04a-provisioning-battery.py` / `.log`). R1 dirs->0700, R2 a file->0600, R3 group root
->grafana, R4 `user: "472:472"`, R5 the uid line removed, R6 one TARGET's ref repointed, R7 the uid
moved with the dashboards left behind, R8 a 2nd dashboard never delivered, **R9 a 2nd dashboard
DELIVERED with an undeclared uid — the row that says 4b/4c cannot skip the check**, R10 malformed
JSON, R11 a dashboard referencing no datasource at all, R12 the dir declaration deleted, R13 the
provider's scan path repointed, R14 the dest moved one dir over: **all RED**. R0 control, **G1 the
mode the refuted D1 demanded (0755/0644) and G2 `user: "472:0"`: GREEN** — the polarity rows.

**Verification.** `just test` **GATE PASS 36/36 exit 0** (`logs/gate-step04a-provisioning.log`,
35→36: the new guard is auto-globbed by `run_gate.py`), guard **PASS: 9/9**, and the pre-fix RED it
replaces is on disk (`logs/red-step04a-guard-pre-fix.log`: 2/9 failed — both uid checks — while the
mode checks passed, which is D1's refutation restated by the guard itself).

**AC.** (a) gate rc=0, guard counted, PASS 9/9. (b) every check RED under a reverted mutation of a
real file — the four rows the task named, in their flipped form, plus ten more. (c) the cross-file
row reads BOTH sides over an inventory keyed on the delivery DEST, so a dashboard 4b/4c adds is
inside it the moment its delivery task exists (R9); the reverse direction is R8. (d) no live call,
no `just play`, no commit; `compose.yml.j2` `02a4c5c2`, `prometheus.yml.j2` `028f8d80`, `env.j2`
`3ae6e541`, `dynamic.yml.j2` `097eca50`, `defaults/main.yml` `eda1e7d9` — identical to the shas the
round-12 Critic recorded, i.e. untouched.

**INFERRED, NOT MEASURED, AND NOT RELIED ON:** that an unresolvable uid renders "Datasource not
found" rather than falling back to the `isDefault: true` datasource. That needs a browser; once the
uids agree the reference resolves either way. **NOT PROVEN BY ANYTHING HERE:** that a panel
populates — that is 4d's, and 4b/4c still owe every series name a source. DEC-069.

## 2026-07-30 — Step 4a REWORK round 2 (task-1785442414-452f, review.rejected F1) — BUILT

**Active task:** Step 4a, `code-assist:plex-monitoring:step-04:provisioning-readability-and-datasource-uid`.
**Verification commands:** `python3 logs/red-step04a-migration-battery.py`,
`python3 logs/calibration-step04a-builtin-datasources.py`,
`python3 logs/red-step04a-provisioning-battery.py`, `just test`.

**THE REJECTION WAS RIGHT AND IT REPRODUCES ON THE FILE THE ROLE DELIVERS.** Round 1 measured the
uid pin against an EMPTY grafana store. The live target is a named volume that has held
`name: Prometheus` under a GENERATED uid since a8c17db (2026-06-19), and provisioning matches BY
NAME. `logs/red-step04a-migration-battery.log`, ten rows on grafana/grafana:13.1.0, five of them
controls, no repo file modified:

    M0  fresh store + the round-1 file                        HEALTHY   (control)
    M1  fresh store + the a8c17db file (no uid:)              HEALTHY, uid 404  (the live-host shape)
    M2  M1's store + the ROUND-1 file          <-- BLOCKER    DID NOT START, exit 1
    M3  M1's store + the DELIVERED file        <-- THE FIX    HEALTHY, uid 200
    M4  M3's store rebooted with the same file                HEALTHY   (idempotent)
    M5  fresh store + the DELIVERED file                      HEALTHY   (greenfield unbroken)
    M6  a dirty store, delete at `orgId: 2`                   DID NOT START, exit 1
    M7  a dirty store, delete naming `Prom2`                  DID NOT START, exit 1
    M8  a dirty store, the block written BELOW `datasources:` HEALTHY, and it STORES Prometheus
    M9  a dirty store, the delete's `orgId:` line removed     HEALTHY

M2's death is `Datasource provisioning error: data source not found` — the provisioning module
failing and taking every dependent module down with it, under `restart: unless-stopped`.

**THE FIX IS FOUR LINES OF YAML AND ONE CHECK.** `deleteDatasources:` naming `Prometheus`/`orgId: 1`
in the same provisioning file, and check #10 `test_datasource_uid_change_is_migrated`, which ties the
deleted NAME and orgId to the provisioned entry in BOTH directions. M6/M7 are why both halves of the
tie are pinned rather than decorative; M8 and M9 are why the check does NOT pin block order and does
NOT demand the `orgId:` key — a guard that forbade either would forbid a file that boots (rows G4,
G5, GREEN).

**THE TWO ROUND-1 EDGES ARE CLOSED IN THE SAME FILE, PRICE ZERO.** E1: the cross-file check reddened
on the built-in annotation every Grafana EXPORT carries, which 4b/4c would have hit first. The
allow-list is sourced from the SERVER, not from the bundle —
`logs/calibration-step04a-builtin-datasources.log` reads `/api/frontend/settings` and takes the three
entries marked `builtIn: True`; `-- Public --` appears in the image's JS and NOT in the server's map,
so it stays RED (R21). E2: a `copy:` + inline `content:` delivery was SKIPPED by the dashboard
inventory — AC (c)'s "cannot silently skip", with a spelling that could. It is now reported (R20).

**Battery: 27/27 rows as declared, every watched file byte-identical at both ends**
(`logs/red-step04a-provisioning-battery.log`) — round 1's 17 rows re-run unchanged, plus **R15 the
`deleteDatasources:` block removed, which IS round 1's own tree and is now RED** (the Critic's X4
fail-open closed), R16 a wrong delete name, R17 a wrong orgId, R18 a 2nd provisioned datasource with
no delete entry, R19 a delete for a name nothing re-creates, R20 the inline delivery, R21
`-- Public --`; and the three new GREEN polarity rows G3 (a Grafana export, which was RED before),
G4 (block order), G5 (absent orgId).

**Verification.** `just test` **GATE PASS 36/36 exit 0** (`logs/gate-step04a-provisioning.log`),
guard **PASS: 10/10**.

**AC.** (a) gate rc=0, guard counted, PASS 10/10. (b) every check RED under a reverted mutation of a
real file, 21 RED rows. (c) unchanged and now stricter — the inventory reports the one delivery
spelling it used to skip. (d) no live call, no `just play`, no commit; the only repo files this
iteration touched are `grafana-datasource.yml.j2` and the guard.

**STILL NOT PROVEN BY ANYTHING HERE:** that a panel populates. That is 4d's, and 4b/4c still owe
every series name a source. DEC-070.

## Step 4a REWORK round 3 (task-1785442414-452f) — the file now REACHES the process

**Active task.** `code-assist:plex-monitoring:step-04:provisioning-readability-and-datasource-uid`,
routed by `review.rejected` (round 2). The migration itself was re-verified by the Critic and is NOT
touched: `grafana-datasource.yml.j2`'s `deleteDatasources:` block and `uid: Prometheus` are unchanged
this iteration.

**F1 — the delivery path.** `notify: Restart grafana` on the two PROVISIONING renders, a
`Restart grafana` handler, and TWO new `RELOAD_CONTRACT` rows in `test_traefik_config_shape.py` (the
table whose own comment says it exists "so the next render task added to this role has a check that
already names the invariant"). Measured first, on real `grafana/grafana:13.1.0`:

    D1  datasource.yml edited under the LIVE :ro mount, +40s   url UNCHANGED   (start-only)
    P1  a second PROVIDER entry added under it, +40s           still ONE dashboard
    D2/P2  `docker restart`, same container                    BOTH delivered  (control)
    D5  a DASHBOARD JSON edited under the same mount, +40s     new title, NO restart
    N1  the same body delivered as `datasources/other.yml`     provisions identically
    N2  the same body at the provisioning ROOT                 never provisioned at all

D5 is why the dashboard `copy:` task deliberately has no `notify:` and no row; N1/N2 are why the row
pins the DIRECTORY (`default_dir`) and not the path — a path pin would forbid a rename that works.
`_bind_mount_target` now resolves a `dest` that lies UNDER a mount source (grafana renders into a
mounted directory), which the review flagged in advance as the thing that would otherwise redden a
correct tree; nested mounts stay fail-closed.

**F2 — the duplicate key.** New check `test_provisioning_files_have_no_duplicate_key` over BOTH
provisioning templates, at every depth, plus a fail-closed `_provisioning_entries` (it used to take
the first `re.search` hit). Leg K measured four depths and all four exit 1:
K1 a second `datasources:`, K2 a second `providers:` in the provider file, K3 a second `apiVersion:`,
K4 a second `name:` INSIDE one entry — each `yaml: unmarshal errors … already defined`; K0 control
HEALTHY.

**Battery: 16 rows, every one as declared, every watched file byte-identical at both ends**
(`logs/red-step04a-r3-guard-mutations.log`). RED: G1/G2 either `notify:` removed, G3 the handler
deleted, G4 the handler restarting the WRONG service, G5 the `notify:` indented into the module args
(the lint-clean spelling), G6 a prefix-sibling dir, G7 the provisioning root, G9 the compose mount
deleted, H1-H4 the four duplicate-key depths, H6 the flow-mapping price. GREEN polarity rows: C0 the
delivered tree, G8 the rename N1 says works, H5 a legitimate SECOND datasource with its delete entry.

**Verification.** `just test` **GATE PASS 36/36 rc=0** (`logs/gate-step04a-r3.log`), traefik guard
**PASS 41/41**, grafana guard **PASS 11/11**.

**Files this iteration:** `tasks/main.yml` (two `notify:` + three comments), `handlers/main.yml` (the
handler), `scripts/test_traefik_config_shape.py` (two rows, `default_dir`, the under-a-mount hop),
`scripts/test_grafana_provisioning_shape.py` (check #11, the scanner, the fail-closed reader). No
live host, no `just play`, no vault value, no commit. Steps 1b/2b/3b/4d untouched; 4b/4c still blocked.

**STILL NOT PROVEN BY ANYTHING HERE:** that a panel populates, and that the handler FIRES on a real
run — the wiring is pinned by the guard and by `--syntax-check`, but only 4d's `just play` executes it.

## 2026-07-31 — Builder, Step 4b (task-1785442438-e959) — the Proxmox VE dashboard

**What landed.** `ansible/roles/docker_host/files/grafana-pve-dashboard.json` (uid `pve-overview`,
title `Proxmox VE`, 11 panels + a `guest` template variable), its delivery task `Install the Grafana
Proxmox VE dashboard` in `tasks/main.yml` (copy → `grafana/dashboards/pve.json`, 0640 root:root, NO
`notify:` — the provider polls), and two new rows in
`scripts/test_grafana_provisioning_shape.py` (**11 → 13**).

**The metric names are SOURCED, not invented.** All 12 distinct `pve_*` names were read out of
`prompve/prometheus-pve-exporter:3.9.0` — the tag `defaults/main.yml` pins — by walking its own
collector modules by AST (`logs/calibration-step04b-pve-series.py` / `.log`: **38** metric families
across `collector/cluster.py` and `collector/node.py`, counting both the direct `GaugeMetricFamily(…)`
spelling and the `super().__init__(…)` one that `pve_ha_state`/`pve_lock_state` use). The new check
`test_pve_panels_name_series_the_exporter_declares` holds every delivered dashboard to that list, so
a near-miss like `pve_memory_used_bytes` reddens offline. It scans the RAW TEXT rather than the keys
a reader happens to model, because a series name reaches Prometheus from a panel `expr`, an
annotation `expr`, a variable `query` and its `definition`.

**What is still unverified, and it is named in the delivery comment so 4d does not rediscover it:**
whether the live PVE API populates each family for an LXC on this cluster. `pve_up{id="lxc/110"}`
(gate 2b, never run) is the only series pinned to this cluster, and it is deliberately what the
`guest` drop-down is built from — an empty drop-down at 4d is 2b's exporter, not a dashboard bug.
Panel 9 (block I/O) is the likeliest legitimately-empty one: the exporter's own docstring says those
families are "not available for all storage types".

**The uid-collision row is MEASURED** (`logs/calibration-step04b-uid-collision.py` / `.log`, real
`grafana/grafana:13.1.0` at the delivered modes): U0 two dashboards with distinct uids → both land;
U1 the same uid → `/api/search` holds ONE, and the server logs `the same UID is used more than once
… times=2` **and `dashboards provisioning provider has no database write permissions because of
duplicates`** — the blast radius is the WHOLE PROVIDER, so the starter dashboard stops updating too;
U2 the same collision with the two FILE NAMES swapped → the OTHER one survives. Healthy server, no
error level, just a dashboard quietly not there. Hence
`test_delivered_dashboards_have_distinct_uids`.
**The first version of that script was a dead instrument and the log says so:** it read
`select … from dashboard` out of `grafana.db` and printed 0 rows for every row INCLUDING the control.
13.1.0 serves from unified storage and leaves that table empty (4a's
`calibration-step04a-delivered-tree-boots.log` shows the same). Re-done over the server's own API.

**Battery 12/12 as declared**, every watched file sha-identical at both ends, and every row names the
CHECK it expected to move rather than just "something went red"
(`logs/red-step04b-mutations.py` / `.log`): B1 delivery task deleted, B2 datasource uid →
unprovisioned, B3 dashboard uid duplicated with the starter's, B4 delivered `0600`, B5 its DIRECTORY
at `0700`, B6 near-miss series, B7 every `pve_*` replaced by a real `node_*`, B8 truncated to invalid
JSON, B9 dest pointed at `homelab.json`, B10 inline `content:` instead of `src:` — all RED, each via
exactly the expected check. **Polarity rows GREEN, per 4a's flip:** C1 `0644` (access, not a literal
mode — `0640` is the measured-correct delivered mode and is NOT asserted red anywhere), C2 a legal
THIRD dashboard, which is the shape 4c is about to add.

**Whole path, on a real server** (`logs/green-step04b-wave-harness.py` / `.log`, **9/9**): real
`ansible-playbook` over the role's own tasks (13 tasks ran — counted, because an unmatched
`--start-at-task` exits 0 having run nothing), then real `grafana/grafana:13.1.0` booted on the
ANSIBLE OUTPUT at the role's real modes. Both dashboards delivered at 640; server healthy;
`/api/datasources/uid/Prometheus` 200; `/api/search` holds both with distinct uids; **all 27 stored
panel/target refs are `Prometheus`**; the `guest` variable is stored with its `pve_up` query. W9's
error diff against a BARE-IMAGE control adds only the `provisioning/{plugins,alerting}` pair 4a
attributed to our own `:ro` mount — non-fatal, and 4d must not read it as the failure. Nothing was
mutated: both watched files byte-identical at both ends, every container and volume removed.

**Verification.** `just test` **GATE PASS 36/36 rc=0** at both ends (`logs/gate-step04b.log`,
`logs/gate-step04b-after.log`), grafana guard **PASS 13/13** in the gate's own file list, traefik
guard 41/41.

**Files this iteration:** `ansible/roles/docker_host/files/grafana-pve-dashboard.json` (new),
`ansible/roles/docker_host/tasks/main.yml` (one delivery task + its comment),
`scripts/test_grafana_provisioning_shape.py` (two checks + `PVE_EXPORTER_SERIES`). No live host, no
`just play`, no Grafana call against real infrastructure, no vault value, no commit. Steps 1b/2b/3b
and 4d untouched; 4c left for the next `queue.advance`.

**STILL NOT PROVEN BY ANYTHING HERE:** that a panel POPULATES. There is no Prometheus behind the
datasource in the harness and no PVE host behind the exporter, so `pve_up` has no samples and the
drop-down has no values to list. That is 4d's, and it rests on gate 2b, which has never run.

## 2026-07-31 — Step 4b REWORK round 2 (task-1785442438-e959) — `review.rejected` F1

**The blocker, and the half of it nobody had measured.** The review proved
`test_delivered_dashboards_have_distinct_uids` does `if src.suffix == ".j2": continue` before
reading the uid while its docstring promises such a file is REPORTED. Both skip lines are gone
(the parse check carried the same copy). Re-running the reviewer's two rows would be a re-run,
so the battery builds the collision in EVERY delivery spelling `_delivered_dashboards` knows
(`logs/rework-step04b-r2-delivery-spellings.log`, 11/11 in BOTH modes, and the appendix run is
against the rejected increment as delivered, not a reconstruction):

  R1 `template:` + `templates/…json.j2`  GREEN pre -> RED post   the review's F1
  R2 `copy:` + `files/…json.j2`          GREEN pre -> RED post   a SECOND carrier, unasked
  R3/R4 the `.json` spellings            RED in both — the skip keyed on the SUFFIX, not the module
  R5 inline `content:`, no src           RED in both
  P1 Jinja INSIDE a JSON string value    GREEN in both — THE PRICE: a real templated dashboard still ships
  P2 Jinja in a STRUCTURAL slot          RED in both — the refs check, which never had a skip, already refused it

So the fix forbids nothing the guard used to accept, which is a stronger price claim than "no
`.j2` dashboard exists today".

**A second silent carrier, through the other reader (DEC-073).** A `dest:` naming the dashboards
DIRECTORY is a real ansible spelling and was invisible to the dest-keyed inventory: a third
dashboard duplicating the PVE dashboard's uid there is guard GREEN 13/13 whenever its filename
also misses the sibling inventory's `files/*dashboard*.json` glob
(`logs/rework-step04b-r2-dest-dir-probe.log`, row D2 `--mode pre`). `_delivered_dashboards` now
keys such a delivery on the basename ansible would give it. Price measured both ways: P1 the same
delivery with its OWN uid stays GREEN, P2 the same with inline `content:` is now REPORTED.

**MY OWN INSTRUMENT WAS WRONG FIRST AND THE LOG SAYS SO.** The battery's `--mode pre` rebuilt the
rejected guard with `str.replace` on `try: doc = json.loads(raw)` — an anchor that ALSO matches
inside `test_delivered_dashboards_reference_the_provisioned_uid`, which never had a skip. That
built a three-skip guard the increment never shipped, and row P2 flipped GREEN in the re-run,
which is how it was caught. The anchor now includes its `except` body and the script asserts the
`pre` guard carries exactly 2 skips.

**Verification.** `just test` **GATE PASS 36/36 rc=0** (`logs/gate-step04b-r2.log`); grafana guard
**PASS 13/13**, count unchanged — a polarity repair, not a new check
(`logs/green-step04b-r2-guard.log`); round-1's acceptance battery re-run **12/12** against the
changed reader (`logs/red-step04b-r2-mutations.log`); the real-grafana wave harness re-run **9/9**,
containers and volumes removed (`logs/green-step04b-r2-wave-harness.log`). Every watched file
byte-identical at both ends of every battery.

**Files this iteration:** `scripts/test_grafana_provisioning_shape.py` only (two skip lines
deleted, one helper widened, three docstrings told why). No dashboard JSON change, no tasks/main.yml
change, no live host, no `just play`, no vault value, no commit. Gates 1b/2b/3b/4d untouched.

## 2026-07-31 — Step 4b REWORK round 3 (task-1785442438-e959) — review.rejected F1 → the DELIVERED NAME

**Active task:** `code-assist:plex-monitoring:step-04:pve-dashboard`, third rework. F1: the
increment now COMPUTES a delivered filename and nothing in the guard asks whether Grafana reads
one — measured by the review on real grafana 13.1.0, a dashboard delivered as `third.json.j2` is
silently never loaded while the guard prints PASS 13/13.

**The fix.** One clause folded into `test_dashboards_are_delivered_where_grafana_looks`, which
already owns "delivered where grafana LOOKS" — the NAME is half of that. Check count UNCHANGED at
13: a polarity repair, not a new check.

**RED first, against the guard AS DELIVERED — no reconstruction.**
`logs/rework-step04b-r3-name-spellings.py --mode pre|post` runs the guard exactly as it is on
disk and ASSERTS which program it measured by the clause's own marker in the guard source, so a
mislabelled run cannot be reported (round 2's instrument bug, closed at the root rather than
patched). **9/9 in BOTH modes** (`…-pre.log` guard sha 174cb19e, `…-post.log` sha e335ba40):
N2 a plain `dest: …/probe.json.j2`, N3 the dir-`dest:` name ansible really writes, N4 `.JSON`,
N5 `.yaml` are all guard-GREEN before and RED after — each failing the name clause and NOTHING
ELSE. N1/N6/N7 (ordinary delivery, a legitimately TEMPLATED dashboard at a `.json` dest, the
round-2 dir-dest widening) stay GREEN in both modes. N8 declared non-price: inline `content:` is
RED in both modes for the src-None reporters, never for this clause.

**The half the review did not ask: what the rule ACCEPTS.**
`logs/rework-step04b-r3-accepted-names-live.log`, real `grafana/grafana:13.1.0` at the delivered
root:root 0750/0640, **5/5** — C1 `probe.json` loads (control), **C2 a DOT-FILE `.probe.json`
loads too**, so the rule is the suffix and only the suffix. **C3: the provider RECURSES** —
`dashboards/sub/probe.json` IS loaded while the check's existing directory clause reddens it.
That RED is a real price, charged since 4a and unmeasured until now; kept deliberately (it is
LOUD, and three-paths-equal is the invariant the check exists for) and written into the
docstring + DEC-074 rather than left as an assumption.

**MY OWN INSTRUMENT WAS WRONG FIRST AND THE LOG SAYS SO.** Run 1 was 5/9: the probe dashboard was
created once up front, so on every row that did not deliver it the ORPHAN check reddened —
rows failing for another check's reason, a mismatch, not a price. The probe src is now
materialised inside `deliver()` alongside the task that delivers it, and the sibling spelling
removed. Same class the review's own price battery hit, now caught by the same rule.

**Verification.** `just test` **GATE PASS 36/36 rc=0** (`logs/gate-step04b-r3.log`); guard
**PASS 13/13**, count unchanged (`logs/green-step04b-r3-guard.log`); round-1's acceptance battery
**12/12** against the changed reader (`logs/red-step04b-r3-mutations.log`); round-2's
delivery-spellings **11/11** and dest-dir probe as declared, both `--mode post`
(`logs/rework-step04b-r3-*-recheck.log`). Every watched file byte-identical at both ends.

**Files this iteration:** `scripts/test_grafana_provisioning_shape.py` only. No dashboard JSON
change, no tasks/main.yml change, no live host, no `just play`, no vault value, no commit. Gates
1b/2b/3b/4d untouched.

## 2026-07-31 — Step 4b REWORK round 4 (task-1785442438-e959) — the ORPHAN direction stops keying on a filename

**Active task:** `code-assist:plex-monitoring:step-04:pve-dashboard`, rework round 4 from
`review.rejected` (F1 the on-disk side of the inventory, F2 a docstring claim the check cannot keep).

**F1 — the fix.** `test_dashboard_delivery_inventory_is_complete`'s on-disk side is now
`_dashboard_sources_on_disk`: the two filename globs it was, UNIONED with a content test
(parses to a mapping with top-level `uid` + `title` + `panels`/`schemaVersion` — the same keys
the delivered-side parse check reads). Nothing in this repo enforces the `dashboard` token, and
the check whose docstring promises to catch an undelivered dashboard was the one missing it.

**F2 — the sentence, measured instead of asserted.** The three-path clause claimed it made
"a dashboard delivered one directory over a FAILURE rather than a silence". W1: move the real
pve delivery one directory over and that clause prints **OK** — `_delivered_dashboards` is
dest-keyed, so it only ever sees deliveries already inside the tree. The shape is caught by
inventory-complete (as an ORPHAN), which after F1 is keyed on content, not on a second
convention. W2: one directory DOWN is what the clause does see. Docstring rewritten to that,
with the attribution.

**The half nobody asked — what the content test CLAIMS** (`logs/rework-step04b-r4-content-keys-live.log`,
real `grafana/grafana:13.1.0` at the delivered root:root 0750/0640, **5/5**): the provider loads a
dashboard with **NO top-level `uid`** (A2) and one with **`uid`+`title` and nothing else** (A3),
silently, on a healthy server. So the key set is strictly NARROWER than the server and an
undelivered file of either shape is still invisible. Stated as a bound, kept narrow because both
shapes are RED on the DELIVERED side the instant a delivery task exists (I7, asserted by check
name) — DEC-075.

**Verification.** `logs/rework-step04b-r4-inventory-content.py --mode pre|post` **10/10 in BOTH
modes**, run against the guard AS IT IS ON DISK with the mode asserted by a marker in the guard
SOURCE; count UNCHANGED at 13 (a polarity repair). `just test` **GATE PASS 36/36 rc=0**
(`logs/gate-step04b-r4.log`); guard **PASS 13/13** (`logs/green-step04b-r4-guard.log`); round-1
mutations **12/12**, round-2 delivery-spellings **11/11** and dest-dir probe as declared, round-3
name-spellings **9/9** — all re-run against the changed reader. Instrument bug found and logged:
run 1 read the run total off the end of `FAIL: n/13 checks failed` and reported I3 red for the
parser's reason, not the guard's.

**Files this iteration:** `scripts/test_grafana_provisioning_shape.py` only. No dashboard JSON
change, no tasks/main.yml change, no live host (throwaway container only), no `just play`, no
vault value, no commit; HEAD still `7e9c426`. Gates 1b/2b/3b/4d untouched.

## 2026-07-31 — Step 4b REWORK round 5 (task-1785442438-e959) — the orphan direction's WHERE and its KEY SET

Answering `review.rejected` round 5. Both halves are the review's PRICED fix, re-measured here
rather than inherited. One function, two lines, plus its docstring and DEC-076.

**F1 — the round changed *what* the on-disk side reads, not *where* it looks.** All four patterns
in `_dashboard_sources_on_disk` were `Path.glob`, which is NOT recursive, so each was pinned to
the TOP LEVEL of `files/`/`templates/` — while the DELIVERED side has no such limit
(`_delivered_dashboards` builds `root / src`, and ansible's `src:` takes directory components).
Reproduced on my side (`logs/rework-step04b-r5-subdir-and-keys-pre.log` **R1**): an ORDINARY
undelivered dashboard at `files/dashboards/grafana-plex-health.json`, `tasks/main.yml` UNMUTATED,
is guard **PASS 13/13**; **R2** the IDENTICAL BYTES one directory UP are RED — the directory is
the whole difference. Fix: `glob` -> `rglob`, all four patterns. The legitimate pair stays GREEN
(**R4**) and is held to the other twelve checks (**R5**, a uid collision with the PVE dashboard
reddens `distinct-uids`).

**F2 — DEC-075's PAIR ARGUMENT WAS FALSE FOR ONE OF THE TWO SHAPES IT NAMED.** The key set was
`uid`+`title`+(`panels`|`schemaVersion`) and the docstring justified the extra key by claiming
both excluded shapes "cannot ship, only sit unwired". Round 4 delivered only the NO-UID shape.
Delivered the other (**R6**): `uid`+`title`+a real datasource ref, no top-level
`panels`/`schemaVersion` is guard **GREEN 13/13** — it SHIPS, and its undelivered twin was
invisible here (**R7**). Fix: align the on-disk key set to the parse check's `uid`+`title`, which
is what the docstring already claimed it was.

**Bounds declared, not discovered.** **R9** a non-dashboard JSON in a subdirectory stays GREEN, so
what the change newly forbids is still only a file that LOOKS like a dashboard. **R10** a bare
`.j2` src with no `.json` (`templates/grafana-plex-health.j2`) matches no pattern under EITHER
program — `rglob` does not close it; the repo's templates are all `<name>.<ext>.j2`. The no-uid
shape stays unclaimed here and is the bound the pair argument DOES cover.

**Verification.** `logs/rework-step04b-r5-subdir-and-keys.py --mode pre|post` **11/11 in BOTH
modes**, run against the guard AS IT IS ON DISK, mode asserted by a marker (`FILES.rglob(...)`) in
the guard SOURCE, every row asserting WHICH checks printed FAIL and reverting in a `finally` with
sha at both ends. Count **UNCHANGED at 13** — a polarity repair, no new check. `just test`
**GATE PASS 36/36 rc=0** (`logs/gate-step04b-r5.log`); guard **PASS 13/13**
(`logs/green-step04b-r5-guard.log`). Re-run against the changed reader: round-4 inventory battery
**10/10**, round-1 mutations **12/12**, round-2 delivery-spellings **11/11**, dest-dir probe as
declared, round-3 name-spellings **9/9**.

**Instrument failure, logged.** Run 1's R5 hard-coded `proxmox-ve` as the PVE dashboard's uid; the
file says `pve-overview`, so the row printed FAIL for the instrument's reason and not the guard's.
Re-keyed to read the uid off the real file. A row reddening for its own bug is not a measurement.

**Files this iteration:** `scripts/test_grafana_provisioning_shape.py` only. No dashboard JSON
change, no `tasks/main.yml` change, no live host, no `just play`, no vault value, no commit; HEAD
still `7e9c426`. Gates 1b/2b/3b/4d untouched.

## 2026-07-31 — Step 4b REWORK round 6 (task-1785442438-e959), `review.rejected` F1 → the TOKENISER

**Active task.** task-1785442438-e959 / `code-assist:plex-monitoring:step-04:pve-dashboard`.

**What changed.** One line and its docstring paragraph in
`test_pve_panels_name_series_the_exporter_declares`:
`\bpve_[a-z0-9_]+\b` -> `\b[Pp][Vv][Ee]_[A-Za-z0-9_:]+\b`. Check COUNT **unchanged at 13** — a
polarity repair, not a new check. DEC-077 records the reasoning and the correction to the
review's colon argument.

**The review's half, re-measured not inherited.** A Prometheus metric name is
`[a-zA-Z_:][a-zA-Z0-9_:]*`, so a near-miss with a capital in the TAIL is a token the old pattern
cannot form: `pve_upTime_seconds` is guard **GREEN 13/13** (T1), as is `pve_Memory_usage_bytes`
(T2) and the same capital in the OTHER delivered dashboard (T3), while the CONTROL — the identical
near-miss in lower case — is RED and only `pve-series` (C1).

**The half the prescription does not reach.** `--mode mid` reconstructs the review's prescription
AND NOTHING ELSE, in place, reverted in a `finally` with the guard sha restored byte-identical:
under it, `PVE_uptime_seconds` (H1), `Pve_up` (H2) and the head capital in the other dashboard
(H3) are still **GREEN 13/13** — the tail class was widened and the head left a case-sensitive
literal. And **K1**: `pve_up:rate5m` TRUNCATES at the colon to `pve_up`, which IS a declared
family, so it is ACCEPTED under `pre`, under `mid`, and under a head+tail-only fix. The review's
colon row (`pve_cpu:ratio`, K2) is right and does not generalise — it is a claim per HEAD, not per
rule, because its truncated head is not a declared family.

**Verification.** `logs/rework-step04b-r6-pve-token-case.py --mode pre|mid|post`, **15/15 in ALL
THREE modes**, run against the guard AS IT IS ON DISK, mode asserted by that program's own
`re.findall(...)` call in the guard SOURCE, every row mutating the REAL dashboards, naming WHICH
checks printed FAIL, and reverting in a `finally` with sha at both ends. `just test`
**GATE PASS 36/36 rc=0** (`logs/gate-step04b-r6.log`); guard **PASS 13/13**
(`logs/green-step04b-r6-guard.log`). Regression against the changed reader: round-5 subdir/keys
**11/11**, round-4 inventory **10/10**, round-1 mutations **12/12** with its control green at both
ends, round-2 delivery-spellings **11/11**, dest-dir probe as declared, round-3 name-spellings
**9/9**.

**Price, measured as zero.** The real tree names the IDENTICAL 12 `pve_*` tokens under every
pattern considered, so the delivered tree stays GREEN with the count unchanged. **P2** is the
declared price and is unchanged in KIND: a `pve_` token used as PROSE in a title already reddened
in lower case (**P1**, RED under every program) and now reddens in `PVE_` case too.

**Bounds, declared not closed.** **B1** `node_pve_up` — `pve_` EMBEDDED after a word char — stays
GREEN under every program; it is a different namespace, as is every non-`pve_` family a panel
might name, and closing that needs a live Prometheus this offline gate does not have. A token
carrying a character outside the metric-name grammar still vanishes, and such a string is not a
metric name at all.

**Files this iteration:** `scripts/test_grafana_provisioning_shape.py` only (`4fd32458` ->
`396ecd28`). No dashboard JSON change, no `tasks/main.yml` change, no live host, no `just play`,
no vault value, no commit; HEAD still `7e9c426`. Gates 1b/2b/3b/4d untouched.

---

## Step 4b — CLOSED (Finalizer, 2026-07-31, task-1785442438-e959)

Closed after 6 review rounds. Every acceptance criterion re-run by the Finalizer, not inherited.

| leg | result |
| --- | --- |
| AC (a) gate | `just test` **GATE PASS 36/36 rc=0** (`/tmp/finalizer-4b-gate.log`) |
| AC (a) guard | **PASS 13/13**; count UP **10 -> 13** across 4b (4a closed at 10/10) |
| AC (b) battery | `logs/final-step04b-adversarial.py` **9/10** (`.log` alongside), controls A0/A1 GREEN at both ends, sha256 identical at both ends on all four watched files |
| AC (b) F1 delivery task deleted | **RED** |
| AC (b) F2 delivered outside the provider's scanned dir | **RED** |
| AC (b) F3 mode `0600` (the 4a access-inventory row) | **RED** |
| AC (b) F4 datasource uid the provisioning does not declare | **RED** |
| AC (b) F5 dashboard uid collided with the starter's | **RED** |
| AC (b) F8 near-miss `pve_memory_usage_bytes` -> `pve_memory_used_bytes` | **RED** |
| AC (b) F9 cosmetic title edit (anti-vacuity price) | **GREEN**, correct |
| AC (c) F6 JSON truncated to invalid | **RED** |
| AC (d) | HEAD still `7e9c426`, no commit, no `just play`, no live host, no vault value; gates 1b/2b/3b/4d untouched |

**Content delivered in full**, not the easy subset: 11 panels — per-guest status, uptime, allocated
CPU, allocated memory, CPU ratio, memory, root disk, network throughput and block I/O, all over the
`$guest` drop-down — plus node-level CPU and memory for the PVE host. `uid: pve-overview`, distinct
from `homelab-overview`. Drop-down is `label_values(pve_up{id=~"lxc/.*"}, id)`, built on the one
series this repo has pinned, so an empty drop-down at 4d indicts gate 2b's exporter, not the JSON.

### OPEN FINDING FOR THE PLANNER — `templating` has NO guard row at all

`scripts/test_grafana_provisioning_shape.py` contains neither `templating` nor `label_values`.

- **F7** — delete the dashboard's templating list outright -> guard **GREEN 13/13**.
- **F7b** — the realistic version: rename the variable `guest` -> `guestt`, leaving all **13
  `$guest` targets across 11 panels** dangling -> guard **GREEN 13/13**, while every panel on the
  dashboard renders a broken query.

This is plan.md Step 4's own Test Requirement ("the container drop-down correctly lists CT 110 and
CT 111") and step 3 of the 4d operator gate verbatim, and offline nothing sees it.

**Why this did not reopen 4b.** It is a hole in the GUARD, not a defect in the ARTIFACT — the
delivered drop-down is present and correct — and the property is gated by 4d step 3, which is
blocked on 4b/4c regardless, so it does not ship unchecked. Task 4b's AC (b) enumerated the
mutations it required and every one is RED. **It is written here so it is SCHEDULED rather than
banked** (mem-1785467707-f8cd: a defect declared and never scheduled is shipped). Suggested shape,
matching the two `code-assist:plex-monitoring:guard:*` rows already in the queue: a row asserting
that every `$var` interpolated by any delivered dashboard's panel targets is declared by that
dashboard's own `templating.list`. Planner owns creating it.

### Queue state at close

Step 4 is **not exhausted**: 4c (`task-1785442474-5022`, composite Plex Health dashboard) is open
and repo-side; 4d (`task-1785442499-1851`) is the operator gate behind it. No later numbered steps
remain — Steps 1/2/3 are repo-side complete and hold only their operator gates 1b/2b/3b, none
agent-closable. `LOOP_COMPLETE` is therefore forbidden; `queue.advance`.

## Step 4c — the composite "Plex Health" dashboard (task-1785442474-5022) — BUILT, `review.ready`

**Active task:** `code-assist:plex-monitoring:step-04:plex-health-dashboard`. Repo-side only. No
`just play`, no live host, no Grafana HTTP call, no vault value, no commit; HEAD still `7e9c426`.

**Verification commands.** `just test` -> **GATE PASS 36/36 rc=0**
(`logs/gate-step04c-plex-health-dashboard.log`); the guard alone -> **PASS 16/16**, count **UP
13 -> 16**; the AC(b) battery `logs/red-step04c-mutations.py` -> **27/27** with A0/A1 GREEN at both
ends and every watched file byte-identical (guard, `main.yml`, and all three dashboard JSONs).

### What was measured before anything was written

Neither half of this dashboard's vocabulary was pinned anywhere in the repo, so both were read off
the pinned images offline rather than guessed:

| Calibration | Result |
| --- | --- |
| `logs/calibration-step04c-traefik-plex-series.py` / `.log` — traefik:v3.7.5 booted with this repo's own metrics block and a file-provider `plex` router | **7/7**. Family is `traefik_service_request_duration_seconds` (+`_bucket`/`_sum`/`_count`); the file-provider service labels **`plex@file`** while a docker-provider CONTROL on the same proxy labels `whoami@docker`; the 13 `le` values on that series are **exactly** the Step-1a ladder; `plex@file` never appears on the entrypoint family |
| `logs/calibration-step04c-plex-series.py` / `.log` — `ghcr.io/axsuul/plex-media-server-exporter:2.1.0` | **5/5**. **7** families. Unlike the PVE exporter the names are NOT literals: `collector.rb` registers `:"#{@metrics_prefix}_<suffix>"`, so the suffixes are read off the image and the prefix comes from `METRICS_PREFIX=plex`, which `PLEX_EXPORTER_ENV` already pins. Row P4 boots the real exporter at that prefix and scrapes `plex_up` off it |

### The three rows added (13 -> 16)

- `test_plex_panels_name_series_the_exporter_declares` — every `plex_*` token in any delivered
  dashboard is one of the 7 declared families. Tokeniser written against the metric-name grammar
  (`[Pp][Ll][Ee][Xx]_[A-Za-z0-9_:]+`), taking DEC-077's lesson rather than re-learning it.
- `test_plex_latency_panels_select_the_file_provider_service` — every `traefik_service_*` selector
  names exactly `service="plex@file"`. Bounded to the service families because the entrypoint family
  carries no `service` label at all (measured, R7) — DEC-081.
- `test_plex_latency_panels_read_the_tuned_histogram_buckets` — the latency panels read the
  `_bucket` series through `histogram_quantile` over a `rate()`, with `le` kept through every
  aggregation. **This is the first thing in the repo that reads Step 1a's ladder at all.**

### AC audit

| Criterion | Result |
| --- | --- |
| (a) `just test` exits 0, guard count up, delivered guard PASS n/n | **PASS** — 36/36 rc=0, guard PASS 16/16, count 13 -> 16 |
| (b) every new check RED under a reverted mutation of the REAL file | **PASS** — 27/27, sha identical at both ends |
| (b) delivery task deleted | **RED** (B1) |
| (b) traefik service selector off `plex@file` | **RED** (B7); selector removed entirely **RED** (B8); regex matcher **RED** (B9) |
| (b) histogram expression that does not read `_bucket` | **RED** (B10); `le` dropped from the aggregation **RED** (B11); no `histogram_quantile` **RED** (B12) |
| (b) datasource uid changed to an undeclared one | **RED** (B4) |
| (b) dashboard uid duplicated with another dashboard's | **RED** (B5) |
| (b) the four rows that come FREE, proved to redden FOR THIS FILE | **RED** — inventory B1/B2, readability `0600` B3, delivered-name B19, and the 4b `pve_*` allow-list B18 |
| (c) the JSON parses in the guard | **PASS** — truncated to invalid is **RED** (B6) |
| (d) no live call, no `just play`, no commit, gates 1b/2b/3b/4d untouched | **PASS** |

**The C rows are not decoration.** `0644` stays GREEN (C1 — `_grants_access` is an access property,
not a literal mode, and the task forbids asserting otherwise); a cosmetic title edit stays GREEN
(C2); retuning the rate window stays GREEN (C3 — no row here claims it); `@file` in prose stays
GREEN (C4); and a DECLARED family named in prose stays GREEN (C5).

**One row of this battery was WRONG on its first run and the log says so.** B14 wrote `plex_up` into
a panel title and expected RED. `plex_up` **is** a declared family, so the guard was correct to stay
green — the price is charged on the VOCABULARY, not on the location. The row now uses an undeclared
token and C5 pins the other half, and the guard's own docstring was corrected: it had said "a
`plex_…` token in prose reddens", which is false.

### What a green guard here does NOT mean

It proves this file parses, is delivered where Grafana looks, is readable to uid 472/gid 0, resolves
against the provisioned datasource uid, holds a distinct dashboard uid, and names only series the
two pinned exporters declare. **It cannot prove a single panel populates**, and three of the four
sources are behind operator gates that have never run — 1b for the latency panels, 2b for the CT 110
panels, 3b for every stream panel but the heartbeat. Prometheus itself has been restart-looping
since 15 July. Until `just play` runs, **every panel here is empty and that is the expected state**.
Confirming otherwise is Step 4d's, and it is an operator's job.

### The templating hole was side-stepped, not walked into

This dashboard declares **no** template variable and interpolates none — checked by hand as the task
asks: `grep -c '\$'` over the delivered JSON returns **0**, and there is no `${var}` or `[[var]]`
either. `task-1785497167-e413` is unaffected and remains open; DEC-080 records why the `guest`-style
drop-down and `$__rate_interval` were both declined here.

## Step 4c — REWORK round 2 (task-1785442474-5022), answering `review.rejected` F1/F2

**Verification.** `just test` **GATE PASS 36/36 rc=0** (`logs/gate-step04c-r2-rework.log`); the guard
alone **PASS 17/17**, count **UP 16 -> 17**. Batteries: the new
`logs/rework-step04c-r2-aggregation-and-media.py` **18/18 in BOTH modes**
(`-pre.log` / `-post.log`); the round-1 AC (b) battery `logs/red-step04c-mutations.py` **27/27**,
watched files byte-identical at both ends; the Critic's own
`logs/critic-step04c-fresh-eyes.py` **9/9**, up from the 7/9 it rejected on, with its four
GREEN-expected rows still GREEN. Calibration
`logs/calibration-step04c-r2-promql-aggregation.py` **12/12**.

### F1 — the histogram row was fail-open on the bare aggregation

Round 1 iterated the `by (…)`/`without (…)` clauses that EXIST. The repair enumerates the
aggregations APPLIED to the bucket subject and requires a `le`-preserving modifier on each, with an
unclassified call head RED rather than skipped (DEC-082). The classification is read off the real
PromQL parser in `prom/prometheus:v3.12.0` — a grouping modifier is legal only on an aggregation, so
`X by (le) (…)` parses iff X is one — and the collapse itself is put to the real ENGINE through
`promtool test rules` over a synthetic ladder: a bare `sum` and a bare `avg` leave
`histogram_quantile` with nothing (B2/B4) while the bare `sum` they wrap is a plausible single
number (B3), and `without (code)` (B6), the trailing `sum (…) by (le)` spelling (B7) and no
aggregation at all (B8) are correct and stay GREEN.

RED before GREEN, in the log: `--mode pre` runs the ROUND-1 guard as it was on disk — restored
byte-for-byte by a hash-gated inverse patch, `logs/rework-step04c-r2-restore-round1-guard.py`, which
refuses unless the result hashes to the `5b42e07c` the first run recorded — and prints the holes
GREEN. `--mode post` prints them RED: bare `sum` (D1), bare `avg` (D2), bare `max` (D5), bare
`topk(3, …)` (D6), an unclassified head (D10), and D12, the finding at its sharpest — an inner
`by (le)` that satisfies a scan of the clauses written while the outer bare `sum` collapses `le`
anyway. The two spellings the task NAMED (D3/D4) are RED in both, so nothing was traded away.

### F2 — `sum(plex_media_count)` double-counted every TV library

Re-derived off the pinned exporter rather than inherited: `collect_media_metrics` emits a second,
SYNTHETIC `{title="<section> - Episodes", type="show_episode"}` series for every `show` section, so
a bare sum adds a TV library's episodes to its titles — it populates, it reads plausible, and it is
wrong by the size of the TV library. Panel 4 now reads
`sum(plex_media_count{type!="show_episode"})` and is titled "Library titles (episodes excluded)",
with the reason in the panel description and by the delivery task in `tasks/main.yml`. The 17th
check, `test_plex_library_panels_do_not_double_count_episodes`, prices it and accepts all three
correct shapes (DEC-083): exclude in the selector, keep `type` through the aggregation, or do not
aggregate.

### Instruments that were wrong first, and the log says so

The calibration filed `topk`/`bottomk`/`quantile`/`count_values` as functions on a one-argument
probe — the parser had already classified them ("wrong number of arguments FOR AGGREGATE
EXPRESSION") and the instrument had not — and expected a bare `{}` from `without (code)`, which
keeps `service` too. The battery's D10 mutation left the parentheses unbalanced, so it was not PromQL
at all and printed GREEN for its own reason; and its E-row anchor was keyed to the guard's mode
rather than to the dashboard, which printed BROKEN once the panel was repaired. The round-1 AC (b)
battery pinned its control at `PASS: 16/16` and correctly refused a 17-check tree; its control now
derives the total from the guard's own summary.

### Unchanged

HEAD is still `7e9c426` — no commit, no `just play`, no live host, no vault value; operator gates
1b/2b/3b/4d untouched. The subprocesses here are `promtool` and `cat` against LOCAL pinned images,
the same offline read the 4b and 4c calibrations do.

## Step 4c REWORK round 3 (task-1785442474-5022) — `review.rejected` F1/F2/F3, guard only

Commands: `python logs/calibration-step04c-r3-promql-case.py` **19/19**;
`python logs/red-step04c-r3-mutations.py` **13/22 before the fix → 22/22 after** (`-pre.log` /
`-post.log`); `python scripts/test_grafana_provisioning_shape.py` **PASS 17/17**, count UNCHANGED;
`just test` **GATE PASS 36/36 rc=0**. Re-runs of everything this round could have broken:
AC (b) battery **27/27**, round-1 Critic battery **9/9**, round-2 Critic battery **18/18** (it
rejected at 13/18). One source file changed: `scripts/test_grafana_provisioning_shape.py`. The
dashboard JSON is byte-identical — sha256 asserted at both ends of every mutation.

### F1 — the tokeniser was case-sensitive and PromQL keywords are not

`sum BY (code)` was GREEN 17/17 and returns ZERO samples from the real engine. The repair folds
exactly what the parser folds and nothing else (DEC-084), which is a measurement and not a
convenience: aggregation operators fold (A1, including the parametrised four), `BY`/`WITHOUT` fold
in both modifier positions (A2), the set-operator and matching keywords fold (A4) — but FUNCTION
names do not (`unknown function with name "RATE"`, A3'), metric names do not (A5), and LABEL names
do not (`by (LE)` collapses `le` just like `by (code)`, B12/B13). A blanket `.lower()` would have
satisfied the finding and filed `RATE(…)` as the label-transparent `rate`.

### F2 — the two rows shipped in one commit disagreed about an unknown head

Both now call `_promql_head_kind()`, and the library row's unclassified head is RED with a message
naming the head (DEC-085). The residual the Critic measured, `limitk(5, plex_media_count)`, is R16
and is RED.

### F3 — the accept side, which is where a guard forbids the real answer

`max(histogram_quantile(0.50, sum by (le) (…)))` is CORRECT — the quantile consumes `le`, so what
is stacked above it is free — and `sum by (title) (plex_media_count)` does not double-count, the
synthetic row carrying its own title. `_promql_subject_reaches()` asks whether the subject reaches a
call UNCONSUMED, and `PLEX_MEDIA_DISTINGUISHING_LABELS` accepts either separating label (DEC-086).
The REJECT side is pinned by controls in the same battery: R12 (a broken inner aggregation under a
legal outer one) and R21 (`without (title, type)`) are still RED.

### The instrument was wrong first, again, and it is in the log

Run 1 of the round-3 calibration printed A1 FAIL for `COUNT_VALUES`/`BOTTOMK`/`TOPK`/`QUANTILE` on a
one-argument probe — the identical bug round 2 recorded, and the parse error itself says the parser
had already classified them. Fixed to probe all three arities and re-run before anything was read
off it.

### Unchanged

HEAD is still `7e9c426` — no commit, no `just play`, no live host, no vault value; operator gates
1b/2b/3b/4d untouched. Round 1's C6/C7 (a real series name with a wrong label KEY, `id="lxc/1100"`)
are still GREEN and still 4d's — the stated bound, not touched this round. The `templating` hole is
still side-stepped and still `task-1785497167-e413`.

## Step 4c REWORK round 4 (task-1785442474-5022) — `review.rejected` F1/F2/F3, guard only

Commands: `python logs/calibration-step04c-r4-promql-quotes-and-selection.py` **27/27**
(`prom/prometheus:v3.12.0`, digest sha256:69f52414…a8ac);
`python logs/red-step04c-r4-mutations.py` **17/29 before the fix → 31/31 after** (`-pre.log` /
`-post.log`, guard sha `751002dd` → `f8b17384`, dashboard sha `1e8f3617` in BOTH);
`python scripts/test_grafana_provisioning_shape.py` **PASS 17/17**, count UNCHANGED;
`just test` **GATE PASS 36/36 rc=0**. Re-runs of everything this round could have broken: AC (b)
battery **27/27**, round-1 Critic battery **9/9**, round-2 Critic battery **18/18**, round-3
mutation battery **22/22**. One source file changed:
`scripts/test_grafana_provisioning_shape.py`. The dashboard JSON is byte-identical — sha256
asserted at both ends of every mutation.

### F1 — a quoted label name is legal, and is the bare name

`sum without ("le")` was GREEN 17/17 while the engine returned zero samples, `without
("title","type")` was GREEN at 60 against a true 10, and the correct `sum by ("le")` was RED.
`_promql_label_set` now unquotes a BALANCED pair and nothing else (DEC-087) — not the prescribed
`.strip("\"'`")`, because `sum by ("le` does not parse at all (A6) and a strip would have called
that panel correct. The bound is measured on both sides: quoting does not fold case (A3, battery
R8), a quoted non-identifier is a different label (A5, R9).

### F2 — a selection is not a merge, and it is not free over a ladder either

`topk`/`bottomk` hand back the picked series whole, `__name__` included (C1/C2/C3), so the library
row's refusal of `topk(3, plex_media_count)` was factually false and is now an ACCEPT. The histogram
row still REFUSES a selection, and this is the one place the round does not do what the finding
prescribed: a ladder IS its boundaries, so `topk(2, …)` under a quantile returns p20 0.3 against a
true 0.06 (C9/C9') and `bottomk(2, …)` drops `+Inf` and returns a NaN sample rather than an empty
vector (C8/C8'). The message is repaired to say that instead of the false `le` claim. One
classifier, two prices, because the subjects differ (DEC-088), and the battery now asserts the
MESSAGE — R11'/R14' — because a RED/GREEN row cannot see a refusal that is wrong for its stated
reason.

### F3 — a per-call predicate was computed per-expression

`sum(plex_media_count{type!="show_episode"}) / sum(plex_media_count)` was GREEN and the engine
returns 10/60 (D2). `_plex_media_rows_excluded(text, span)` is the call's own question and demands
EVERY occurrence in the span carry the exclusion, because `any()` inside one span is the same
mistake one scope down — D4/R22 (DEC-089).

### Instruments that were wrong first, and the logs say so

Run 1 of the calibration filed C1/C2/C3/C6 FAIL because I wrote the expected labels as an
AGGREGATION's output, which drops `__name__` — a selection does not, which is the finding itself.
Two more rows were tie-broken rather than measured: `bottomk(2, …)` over a ladder with two equal
rates picked arbitrarily (both `NaN` and `0.1` were observed), and the `+Inf`-drop row asked at p90
where the mutilated answer and the true one coincide. Both moved to a tie-free ladder and to p20,
where the answer is forced, before anything was read off them.

### Unchanged

HEAD is still `7e9c426` — no commit, no `just play`, no live host, no vault value; operator gates
1b/2b/3b/4d untouched. Round 1's C6/C7 are still GREEN and still 4d's. The `templating` hole is
still side-stepped and still `task-1785497167-e413`.

## Step 4c — rework round 5 (task-1785442474-5022), Builder

Active task: `code-assist:plex-monitoring:step-04:plex-health-dashboard`. One source file changed,
`scripts/test_grafana_provisioning_shape.py`. The dashboard JSON, the delivery task, the datasource
uid, `_grants_access`, the `pve_` tokeniser and the histogram row's `le` logic are untouched and
byte-identical (`1e8f3617` before and after every run).

### Verification commands and results

| command | result |
|---|---|
| `python logs/calibration-step04c-r5-matchers.py` | **39/39**, `prom/prometheus:v3.12.0` (`…-r5-matchers.log`) |
| `python logs/red-step04c-r5-mutations.py` (pre-fix) | **24/36**, guard `f8b17384` (`…-pre.log`) |
| `python logs/red-step04c-r5-mutations.py` (post-fix) | **37/37**, guard `387b3fa3` (`…-post.log`) |
| `python scripts/test_grafana_provisioning_shape.py` | **PASS 17/17**, count UNCHANGED (`green-step04c-r5-guard.log`) |
| `just test` | **GATE PASS 36/36 rc=0** (`gate-step04c-r5-rework.log`) |
| the Critic's own instrument, re-run | **20/28 → 27/28** (`critic-step04c-r4-recheck-round5.log`) |
| AC (b) round-1 battery / r3 / r4 batteries | 27/27, 22/22, 31/31 — all unmoved |
| round-1 and round-2 Critic instruments | 9/9, 18/18 |

### The three findings, and the one mechanism that answers all three

`_promql_matchers()` parses a `{…}` block into `(name, op, value)` triples instead of searching it
for a string. **F1** dies by construction — a name is matched as a name or not at all, so
`plex_media_count{mediatype!="show_episode"}` (engine 60 against a true 10, B14) and
`…_bucket{exported_service="plex@file"}` (B18: selects nothing, so merely empty — the lesser harm,
and said so) both redden. **F2** is the unquote, applied to matcher names as round 4 applied it to
grouping clauses: all three quote flavours normalise to the bare name (A1/A2/A3) and the delivered
expressions re-spelled are GREEN. **F3** is the accept side rewritten per-KIND: the rows entering a
call may not be of both, which an `=` on either distinguishing label guarantees outright, `!=` only
against the synthetic value, and `=~`/`!~` by asking the regex — Prometheus anchors label regexes at
both ends, and Python's `fullmatch` was made to agree with RE2 on nine patterns (C1-C9) before it
was allowed to answer.

### Declared, not fixed

An UNTERMINATED string literal stops `_promql_match_paren`, so `_promql_calls` returns `[]` and no
aggregation row examines the expression at all. Measured, declared in the docstring and in battery
row R21', and filed as `task-1785504947-fbde` — such an expression is a lex error in Prometheus
(A8), so the panel ERRORS rather than drawing a wrong number, and the cheap fix would redden
`plex_media_count{$filter}`. DEC-090 argues the trade.

Also declared: a regex admitting ONLY the synthetic type (`{type=~"(?i)SHOW_EPISODE"}`, engine 50
and therefore correct) is still refused, because "admits one value only" needs the label's live
cardinality; the refusal names the `=` spelling instead (R20).

### Instrument that was wrong first

Run 1 of the round-5 battery scored 20/36 with three CONTROLS failing: `_which()`, copied from round
4, tagged a failing check off the whole `FAIL:` line, and a selector refusal quotes the bucket
family's name. Tagged off the check summary now, and re-run before anything was read off it.

### Unchanged

HEAD is still `7e9c426` — no commit, no `just play`, no live host, no vault value; operator gates
1b/2b/3b/4d untouched. The `templating` hole is still side-stepped and still `task-1785497167-e413`.

## Step 4c — rework round 6 (task-1785442474-5022), review.rejected F1 → the shared subset

Round 5's `_promql_regex_matches` handed a question the ENGINE answers with RE2 to Python's `re` on
the licence of nine agreeing patterns. Nine agreeing patterns confirm the SHARED SUBSET. The class
outside it is POSIX bracket expressions: RE2 has them, Python reads `[[:alpha:]]` as a literal set
and only warns, so `sum(plex_media_count{type=~"[[:alpha:]_]+"})` was guard PASS 17/17 while the
engine returns 60 against a true 10.

### What changed

One source file, `scripts/test_grafana_provisioning_shape.py`. `_PROMQL_POSIX_CLASS` (the
CONSTRUCT, `\[:\^?[a-zA-Z]+:\]`, not the `[[:` spelling the review priced — `[a-z[:punct:]]+` is
the same divergence and was GREEN under that pattern). `_promql_regex_matches` returns None for it;
`_plex_media_matcher_pins_one_kind` is now three-valued; `_plex_media_mixed_selector` gives the
undecidable case its OWN sentence naming the construct, so it cannot inherit the mixed-selector
claim about the rows. DEC-091.

### Verification

| command | result |
|---|---|
| `python logs/calibration-step04c-r6-re2-vs-python.py` | **55/55**, `prom/prometheus:v3.12.0` |
| `python logs/red-step04c-r6-posix-mutations.py` (pre) | **15/25** — R1-R9 + R19, and nothing else |
| `python logs/red-step04c-r6-posix-mutations.py` (post) | **25/25** |
| guard alone | **PASS 17/17**, count unchanged |
| `just test` | **GATE PASS 36/36 rc=0** (`logs/gate-step04c-r6.log`) |
| round-5 battery re-run | 37/37 |
| round-4 / round-3 / round-1 batteries | 31/31, 22/22, 27/27 |
| round-1 / round-2 Critic instruments | 9/9, 18/18 |
| round-4 Critic instrument | 27/28 — D1 only, unmoved since round 5 |
| round-5 Critic instrument | **26/26 → 24/26**, and the two that flipped are C1/C2, the rows asserting the hole is real |
| round-5 Critic price script | 8/8 → 6/8, both failures being "pre already reddens" |
| round-3 Critic instrument | cannot run — it patches a construct round 5 removed |

Guard `387b3fa3` → `95608fb7`; dashboard `1e8f3617` byte-identical at both ends of every mutation.

### Declared, not closed

Review F2 — every selector pins one kind, nothing requires them to pin the SAME kind. Measured
(D1-D5): `sum(…{type="show_episode"} or …{type="movie"})` = 57, `sum(…{title="TV"} or
…{title="TV - Episodes"})` = 53 against a true 3, and the two-call spelling merges at a binary
operator no per-call loop sees. NOT closed because the price is measured and real:
`sum(…{title="Movies"} or …{title="TV"})` = 10, correct, and the SAME SHAPE as the 53. Filed as
`task-1785506726-adc5` with what a fix must prove; argued in the docstring and DEC-091.

Also declared: the detector over-triggers on `[:alpha:]` OUTSIDE a bracket expression, where both
engines agree it is a plain character set (calibration C12, battery R19). A loud false refusal of a
pattern nobody writes — the only price this fix charges.

### Suspected and cleared

The STRING layer underneath: a double-quoted PromQL pattern is escape-processed by the lexer before
RE2 sees it. `_promql_unquote` decodes it the same way, so Python is asked the same pattern
(calibration E1-E4, battery R20-R22). Not a gap. Found because run 1 of the calibration was wrong —
it delivered backslash patterns in double quotes and read the PromQL lexer's refusal as RE2's.

### Unchanged

HEAD is still `7e9c426` — no commit, no `just play`, no live host, no vault value; operator gates
1b/2b/3b/4d untouched. `task-1785504947-fbde` and `task-1785497167-e413` both still stand.

## Step 4c — rework round 7 (task-1785442474-5022), 2026-07-31

Answering the round-6 review: F1 the STRING layer, F2 the refusal's reason and the caller's wrapper.
The "suspected and cleared" note above is WRONG and its sentence has been removed from the guard —
it was cleared only over the escapes Go REJECTS.

### Commands

| command | result |
|---|---|
| `python logs/calibration-step04c-r7-lexer-escapes.py` | **PASS 46/46** — the lexer's escape grammar, `prom/prometheus:v3.12.0` |
| `python logs/red-step04c-r7-escape-mutations.py` (pre) | **FAIL 10/22** — the finding, on the real dashboard |
| `python logs/red-step04c-r7-escape-mutations.py` (post) | **PASS 22/22** |
| `python scripts/test_grafana_provisioning_shape.py` | **PASS 17/17**, count unchanged |
| `just test` | **GATE PASS 36/36, rc=0** |
| round-6/5/4/3/1 batteries re-run | 25/25, 37/37, 31/31, 22/22, 27/27 — all unmoved |
| round-6 Critic's instrument re-run | 18/18 → **13/18**, every flip the fix (B1-B3, C2, C4; C1 on the return shape) |

### What changed

`scripts/test_grafana_provisioning_shape.py` only, `95608fb7` → `da964dd7`. `_promql_unquote`
implements Prometheus' `lexEscape` (the simple set + the OPENING quote, `\xNN`, `\NNN`, `\uNNNN`,
`\UNNNNNNNN`, the surrogate/max-rune check) and refuses what the lexer refuses;
`_promql_regex_matches` returns `bool | str` so the refusal's REASON is reachable from exactly one
branch; `_plex_media_mixed_selector` returns `(demonstrated, reason)` and the library row asserts the
double count only when it was demonstrated. DEC-092.

### Declared, not closed

An UNBALANCED quote hides the whole call from `_promql_calls` (its skip-quoted scan swallows the
closing paren), so the library row is vacuous for it rather than fooled. NOT a fail-open: the engine
refuses those expressions too, so the panel errors rather than drawing (calibration H1-H3). Filed as
`task-1785509072-b939`, named in the docstring.

### Unchanged

HEAD is still `7e9c426` — no commit, no `just play`, no live host, no vault value; operator gates
1b/2b/3b/4d untouched. Dashboard JSON byte-identical at `1e8f3617`. `task-1785506726-adc5`,
`task-1785504947-fbde` and `task-1785497167-e413` all still stand.

## 2026-07-31 — Step 4c REWORK round 8 (review.rejected: F1 the raw string the SCANNER escape-processes, F2 a cited count that is not the log's)

Active task `task-1785442474-5022` (`code-assist:plex-monitoring:step-04:plex-health-dashboard`).

### The change

`scripts/test_grafana_provisioning_shape.py` only, `da964dd7` → `4e1f5ad1`. One branch in
`_promql_skip_quoted` — `and quote != "`"` — so a BACKTICK string is scanned raw, the same fact
`_promql_unquote` already implemented one layer up. The other two flavours keep their escapes. The
invisible-call bound and `task-1785509072-b939` are rewritten to name the class that is actually
left. The lexer log's citation is corrected to (46/46). DEC-093.

### Verification

| command | result |
|---|---|
| `logs/red-step04c-r8-raw-string-scanner.py` (pre, guard reconstructed at `da964dd7`) | **19/32** |
| the same battery, post | **32/32** |
| `python scripts/test_grafana_provisioning_shape.py` | **PASS 17/17**, count unchanged |
| `just test` (`logs/gate-step04c-r8.log`) | **GATE PASS 36/36**, rc=0 |
| r7 / r6 / r5 / r4 / r3 / r1 batteries, re-run | 22/22, 25/25, 37/37, 31/31, 22/22, 27/27 |
| the round-7 critic's own instrument, re-run | 19/19 → **14/19**, every flip the fix |

The engine rows are `prom/prometheus:v3.12.0` over the 7/3/50 library fixture and the synthetic
bucket ladder: the raw spelling is ACCEPTED and draws 60 against a true 10 (A3), the CORRECT raw
spelling is the delivered query at 10 (A4/A5), and an unterminated literal is refused in both
flavours (A6/A7). The accept side is measured per consumer on the real dashboard — C5 the library
row, C6 the traefik selector + histogram rows, which the pre-run shows were FALSELY REFUSING a legal
raw-quoted selector (16/17) and are now GREEN.

### Declared, not closed

A string literal with NO CLOSING DELIMITER still hides the whole call from `_promql_calls`. That
class IS a lex error in every flavour (A6/A7, H1-H3), so the panel errors rather than drawing.
`task-1785509072-b939` rewritten: title, the sentence that named UNBALANCED quotes, and what a fix
must prove.

### Unchanged

HEAD `7e9c426` at the start of this entry — no `just play`, no live host, no vault value; operator
gates 1b/2b/3b/4d untouched. Dashboard JSON byte-identical at `1e8f3617`. `task-1785506726-adc5`,
`task-1785504947-fbde` and `task-1785497167-e413` all still stand.

## 2026-07-31 — Step 4c REWORK round 9 (task-1785442474-5022) — `#` COMMENTS

**Verification.** `just test` **GATE PASS 36/36 rc=0** (`logs/gate-step04c-r9.log`); guard alone
**PASS 17/17**, count unchanged. Round battery `logs/red-step04c-r9-promql-comments.py`:
**22/40 pre** (`-pre.log`, guard `4e1f5ad1` — the bytes the Critic reviewed) → **40/40 post**
(`-post.log`, guard `188896df`). Round 8's own battery re-runs **32/32**. The round-8 Critic's
instrument goes **46/46 → 41/46** and all five flips are the fix: C3/C6 (the two fail-opens) now
RED, D1 ("no scanner knows a comment exists") now false, F4 (a correct panel REFUSED) now GREEN,
F5 (the skip does not fix that direction) now moot because the shipped file does.

**What changed.** `_promql_blank_comments` + `_promql_strings` in
`scripts/test_grafana_provisioning_shape.py`; the three PromQL-reading rows read the funnel, the
title row still reads `_json_strings`. Two docstring paragraphs and `task-1785509072-b939`'s
description stop stating the declared bound as a census. DEC-094.

**Engine rows** (`prom/prometheus:v3.12.0`, the 7/3/50 fixture + the synthetic ladder): every
carrier is ACCEPTED and DRAWS — the commented bare sum at 60 against a true 10 with a canonical form
identical to the bare sum (A3/A4), a quantile over RAW counters whose `rate(` is only in a comment
(A9), a bare bucket sum whose `histogram_quantile(` is only in a comment (A10) — and the two
false-refusal carriers are correct panels (A7 normalises to the DELIVERED expression at 10, A11 is
an ordinary session panel).

**Unchanged.** Dashboard JSON byte-identical at `1e8f3617`. No `just play`, no live query, no vault
value; operator gates 1b/2b/3b/4d untouched. `task-1785511204-29b8` CLOSED (fixed this round);
`task-1785506726-adc5`, `task-1785504947-fbde`, `task-1785497167-e413` still stand.

## 2026-07-31 — Step 4c REWORK round 10 (task-1785442474-5022) — THE NAME INSIDE THE BRACES

**Verification.** `just test` **GATE PASS 36/36 rc=0** (`logs/gate-step04c-r10.log`); guard alone
**PASS 17/17**, count unchanged at 17. Round battery `logs/red-step04c-r10-name-in-braces.py`:
**22/51 pre** (`-pre.log`, guard `188896df` — the bytes the Critic reviewed) → **59/59 post**
(`-post.log`, guard `1327c21f`). Grammar calibration `logs/calibration-step04c-r10-name-in-braces-
grammar.log` **22/22** on `prom/prometheus:v3.12.0`. Every earlier battery re-run green against the
new guard: r9 40/40, r8 32/32, r7 22/22, r6 25/25, r5 38/38, r4 31/31, r3 22/22, r2-era 27/27
(`logs/*-r10recheck.log`).

**What changed** (`scripts/test_grafana_provisioning_shape.py` only). `_metric_selector` is the one
boundary both PromQL selector rows use: the block in FRONT of the name, the ENCLOSING block when the
occurrence is at a metric-NAME position inside one, or "not a selector" for a mention that names no
series. Supporting: `_promql_bare_metric_name`, `_promql_quoted_span`, `_promql_literal_closed`,
`_promql_enclosing_matcher_block`, `_promql_block_names_metric`, `PROMQL_NAME_LABEL`;
`_promql_matchers` reads the bare string entry as the `__name__` equality the parser makes of it.
The rows print the selector as WRITTEN. DEC-095.

**F1 — the review's finding, both halves.** `sum({__name__="plex_media_count", type!="show_episode"})`
and `sum({"plex_media_count", …})` are ACCEPTED and draw the DELIVERED 10 (A3/A4); the library row
was RED 16/17 on both with "every show library EPISODE count is added to its title count" (C2/C3),
and the sibling selector row was RED on the `__name__` quantile — which draws the delivered 0.91 —
with "carries NO label matcher" over a block carrying `service="plex@file"` (A10/A11, C10/C11). All
GREEN now, in all three quote flavours and with the bare name first, middle or last (C4-C7), while
every DEFECT in the same spelling stays RED with the sentence that is TRUE of it: the bare
`{__name__=…}` and `{"…"}` sums at 60 (D2/D3), the whole-proxy quantile (D4), the neighbouring label
name (D5) and the regex service matcher (D6).

**F2 — the sentence its own caller falsified.** `_promql_skip_quoted` no longer claims it is only
asked about blanked text: `_promql_blank_comments` asks it about RAW text, and that call is what
keeps a `#` inside a label VALUE the character it is.

**The docstrings the review quoted are corrected, not reworded.** The fail-closed enumeration is
FOUR, and the fifth — "no selector is readable in this span" — is gone with the branch it described.
`_promql_matchers`' declared bound is now the narrow, loud one the engine agrees with (two different
bare names refused).

**Unchanged.** HEAD `7e9c426`; dashboard JSON byte-identical at `1e8f3617`. No `just play`, no live
query, no vault value; operator gates 1b/2b/3b/4d untouched. `task-1785506726-adc5`,
`task-1785504947-fbde`, `task-1785497167-e413` and `task-1785509072-b939` all still stand.

## 2026-07-31 — Step 4c REWORK round 11 (review.rejected F1 → PROSE IS NOT AN EXPRESSION)

**Active task** task-1785442474-5022 (`code-assist:plex-monitoring:step-04:plex-health-dashboard`).
**Verification** `just test` GATE PASS 36/36 rc=0 (`logs/gate-step04c-r11.log`); guard alone
**18/18**; this round's battery `logs/red-step04c-r11-prose-not-expression.py` **15/38 pre → 38/38
post** (`-pre.log` / `-post.log`); every earlier battery re-run at the final guard sha
(`logs/red-step04c-r11-battery-sweep.log`): r10 59/59, r9 40/40, r8 32/32, r7 22/22, r6 25/25, r5
38/38, r2-era mutations 27/27.

**F1 — the three PromQL rows now read the fields a dashboard DECLARES a query in.**
`_promql_strings` was `_json_strings`, i.e. every string LEAF, so a `description`, `title` or
`legendFormat` was read as an expression: measured pre, a description documenting the latency
panel's own series is 15/17 with "carries NO label matcher — this panel graphs the whole proxy under
a Plex title" AND "reads … outside histogram_quantile()" over a SENTENCE, a legendFormat 15/17, a
title 15/17, and a library description quoting the expression an author must not write 16/17 with
the prose counted as an aggregation. All 18/18 now, and the asymmetry the review named ("document
the plex metric, never the traefik one") is gone. `_dashboard_query_strings` is `expr` at any depth
(panel targets, a collapsed row's child targets, annotation queries in both spellings) plus a
`query` variable's `definition` / `query` / `query.query`; the `plex_*` and `pve_*` NAME rows keep
`_json_strings`, whose breadth is their point.

**The narrowing is fail-closed, and that is a new row — 17 → 18.**
`test_delivered_dashboard_queries_are_readable` reports the difference between the slots a query
lives in (`_dashboard_query_carriers`) and the queries this file can read: a prometheus target,
annotation or query variable whose query is in an unknown key REDDENS naming the keys it did find
(E1/E2), a non-prometheus carrier does not (E3), and zero readable queries FAILS. Every real defect
is still RED in every carrier — `expr` (D1-D3), an annotation query (D5), a variable query (D6) and
a collapsed row's child panel (D7).

**F2 — declared, not coded.** `{__name__=~".*request_duration_seconds_bucket"}` with no service
matcher is invisible to the literal-text subject scan; the traefik selector row now says so and
names `task-1785516964-1b02`.

**One pre-existing red, measured and filed.** `rework-step04c-r2-aggregation-and-media.py --mode
post` is 17/18 on D10 (`clamp_min()` wrapping the whole quantile). Not this round's: the same
mutation is PASS against a copy of the guard with `_promql_strings` restored to `_json_strings`.
Filed as `task-1785517288-aca4`.

**Unchanged.** HEAD `7e9c426`; dashboard JSON byte-identical at `1e8f3617` (every mutation reverted
in a `finally` with sha at both ends). No `just play`, no live query, no vault value; operator gates
1b/2b/3b/4d untouched.

## 2026-07-31 — Step 4c CLOSED (Finalizer, task-1785442474-5022) → `queue.advance`

**Verification, all re-run by the Finalizer.** `just test` **GATE PASS 36/36 rc=0**
(`/tmp/finalizer-4c-gate.log`); guard alone **PASS 18/18**, count **UP 13 → 18** across 4c (the
`plex_*` vocabulary row, the declared-query readability row, the `plex@file` selector row, the
`_bucket`-through-`histogram_quantile` row, the `plex_media_count` aggregation row). Guard
`a3b1595e`, dashboard `1e8f3617`, `main.yml` `71e88a89`, HEAD `7e9c426` — no commit.

**AC (b), my own battery.** `logs/final-step04c-adversarial.py` / `.log`, **19/19**, mutating the
REAL files and reverting in a `finally` with sha256 asserted at both ends. All five mutations the AC
NAMED are RED (delivery task deleted; service selector → `plex@docker`; the quantile replaced by a
`_sum` rate so Step 1a's ladder goes unread; uid → the generated `PBFA97CFB590B2093`; uid collided
with `pve-overview`). Five more the AC did not ask for, because "the file entered the inventory" is
what everything else rests on: mode `0600`, delivered outside the scanned dir, delivered as
`.jsonn`, truncated JSON, blanked uid — all RED. Five that POPULATE and are wrong, which 4d's
operator cannot catch by looking: `plex_session_count`, `pve_memory_used_bytes`, the dropped
`show_episode` exclusion, the dropped `le`, the deleted service matcher — all RED. Three controls
(title, gridPos, a reworded description) GREEN.

**REAL HARNESS — the first evidence Grafana will actually load this file.**
`logs/final-step04c-grafana-loads.sh` / `.log`, **6/6**. The guard proves the JSON parses; Grafana's
provisioner validates the document and can decline it silently, leaving the dashboard ABSENT — the
failure 4d's operator meets in a browser. `grafana/grafana:13.1.0` booted OFFLINE (local cache, no
repo host, no vault value, no `just play`) against a tree assembled the way the role delivers it —
same three mounts, `:ro`, `0640` root:root under root-group dirs, no `user:` so 472:0 applies:
server healthy, `GET /api/dashboards/uid/plex-health` → "Plex Health", `/api/search` holds all **3**
dashboards, the loaded document holds all **11** panels, and the server's own store answers at
`/api/datasources/uid/Prometheus` so every panel reference resolves in a running server rather than
against a template. The adversarial row: an invalid document is DECLINED
(`Unexpected element in Dashboard JSON … got=string expected=array`), so the five OK rows are
load-bearing. The only other `level=error` lines are the two `provisioning/{alerting,plugins}` ones
that are ours by the `:ro` mount, as 4a predicted.

**Requirement fidelity.** 11 panels over the three named sources; `uid: plex-health` / `Plex Health`
distinct from both siblings; every series name sourced to a measured boot of its pinned image; the
`show_episode` exclusion explained as a correctness fix; the demanded sentence that a green guard is
not evidence a panel populates, with each panel mapped to the gate (1b/2b/3b) it waits on. The
by-hand check the Planner asked for in item (5): `templating.list: []`, no `$var` / `${var}` /
`[[var]]` anywhere — the legitimate no-variable case, re-checked by the Finalizer.

**Queue state.** Step 4's agent-side work is EXHAUSTED (4a/4b/4c closed); 4d is an operator gate.
Nine agent-side runtime tasks remain ready — eight `code-assist:plex-monitoring:guard:*` rows and
one P3 battery-expectation flip (`task-1785517288-aca4`) — so `LOOP_COMPLETE` is forbidden.
`queue.advance`. **For the Planner:** the eight guard rows are now the largest thing in this
objective's queue and they are one genus (a guard reading a field out of the artifact it guards, or
a scan an author can spell around). Price whether they are a wave rather than eight independent P2s.

## 2026-07-31 — Builder, Step 5a (task-1785497167-e413) — the declared-variable guard

**Task.** `code-assist:plex-monitoring:guard:dashboard-template-vars-declared` — every `$var` a
delivered dashboard interpolates must be DECLARED in that dashboard's own `templating.list`. This is
plan.md Step 4's own Test Requirement (the container drop-down listing CT 110 and CT 111) and 4d
step 3; the Step 4b Finalizer measured it GREEN 13/13 with `templating.list` deleted (F7) and GREEN
again with the variable renamed and all thirteen references dangling (F7b).

**Verification commands and results.**
* `python3 scripts/test_grafana_provisioning_shape.py` → **PASS 19/19** rc=0 (was 18/18: +1 row).
  The new row reads **13 variable reference(s) across 3 delivered dashboard(s)** against the **1**
  variable the PVE dashboard declares.
* `just test` → **GATE PASS 36/36** rc=0 (`logs/gate-step05a-template-vars.log`).
* `logs/red-step05a-template-vars.py` → **29/29** (`…-post.log`); the same battery against the guard
  as it stood before this change is **0/29**, every row `ABSENT` (`…-pre.log`) — the check did not
  exist, which is the RED. sha256 of guard + 3 dashboards + `tasks/main.yml` identical at both ends
  of both runs, every mutation reverted in a `finally`.
* Calibration, offline, against the pinned image:
  `logs/calibration-step05a-grafana-interpolation.sh` / `.py` / `.log` and
  `logs/calibration-step05a-grafana-builtins.py` / `.log`.

**What the calibration bought.** Grafana 13.1.0's own interpolation regex, copied out of the
`.js.map` `sourcesContent` the image ships rather than transcribed from docs — declared identically
in `public/app/features/variables/utils.ts` and
`public/app/features/dashboard-scene/variables/utils.ts` — and the NAME VALIDATOR beside it
(`/^(?!__).*$/`, "Template names cannot begin with '__'"), which is what turns the built-in
exemption from a list that can rot into the complement of the set being checked (DEC-098).

**Not done, deliberately.** No commit, no `just play`, no live call, no vault value; gates
1b/2b/3b/4d untouched; `_grants_access` and the round-6 `pve_*` tokeniser not re-flipped. The
round-11 PromQL narrowing is untouched — the only edit inside an existing function moved
`_dashboard_variable_queries`' `templating.list` enumeration into a shared `_dashboard_variables`
so the declared side reuses the walk 4c already wrote (DEC-085), with no change to what it returns.

### Step 5a REWORK round 2 (task-1785497167-e413) — the review's F1/F2/F3

**Active task.** `code-assist:plex-monitoring:guard:dashboard-template-vars-declared`, answering
`review.rejected`. All three findings are in `scripts/test_grafana_provisioning_shape.py`; the row
count does not change (the row exists, it was wrong in three ways).

**F1, the blocker (SILENT).** The unconditional `__`-prefix exemption is not the complement of the
check. `templating/template_srv.ts::_evaluateVariableExpression` leaves a `__` name that is neither
declared nor in `macroRegistry` LITERAL in the query, so `$__guest` / `$__rate_intervall` /
`${__feild.displayName}` all render as their own text and the panel draws "No data" while the guard
stays PASS. Replaced by `GRAFANA_BUILT_IN_VARIABLES`, a 25-name frozenset sourced from four places
in the pinned image (DEC-099, superseding DEC-098).

**F2 (SILENT).** The docstring claimed a `repeat` clause was covered by the string walk; a repeat
clause names its variable BARE, so no tokeniser reaches it. Added `_dashboard_repeat_clauses`,
scoped to `panels[]` entries at any depth (DEC-100).

**F3 (LOUD).** JS `\w` is ASCII, Python's is Unicode, so `$guesté` formed `guesté` here and `guest`
in Grafana — a RED over a dashboard that renders correctly. `_GRAFANA_INTERPOLATION` now compiles
with `re.ASCII`, and the comment says it is a translation rather than a transcription and why.

**Verification commands and results.**
* `python3 scripts/test_grafana_provisioning_shape.py` → **PASS 19/19** rc=0 (unchanged count; the
  row now reads `13 variable reference(s) (0 of them a bare repeat clause) … 0 reference(s) to one
  of the 25 sourced built-ins exempt`).
* `just test` → **GATE PASS 36/36** rc=0 (`logs/gate-step05a-rework-r2.log`).
* `logs/red-step05a-rework-r2.py` → **32/32** (`…-post.log`). The SAME 32 rows against a reverted
  copy of the guard (prefix rule restored, repeat walk removed, `re.ASCII` dropped) → **20/32**
  (`…-pre.log`); the twelve misses are exactly F1 (B1-B6), F2 (D1/D2/D4/D5/D8) and F3 (E1). Every
  mutation reverted in a `finally`; sha256 of guard + 3 dashboards + `tasks/main.yml` identical at
  both ends of both runs. The reverted copy lived in `scripts/` (the guard resolves the repo from
  `__file__.parent.parent`) and was deleted after the run.
* The review's own battery re-run VERBATIM, `logs/critic-step05a-builtin-exemption.py` →
  **12/12** (was 6/12), `…-rerun.log`.
* New calibration: `logs/calibration-step05a-grafana-builtin-set.py` / `.log`, rc=0 — offline off
  the `.js.map` `sourcesContent` already in `/var/tmp/step05a-grafana-src`, every extractor raising
  on a miss. Prints each of the 25 names with its `file:line`, the macro registry and
  `DataLinkBuiltInVars` verbatim, and asserts the plugin's own `partsToKeep` census leaves nothing
  over. This replaces `calibration-step05a-grafana-builtins.py`, whose `!! macro map not matched`
  was the instrument failure DEC-098 read as a design choice.

**Accept side, measured rather than assumed.** C1-C6 keep every really-substituted built-in GREEN,
including `$__range_s` (sourced only from the Prometheus plugin) and `$__timezone` (only from
`macroRegistry`); D3 keeps ordinary repeating GREEN; D7 keeps a panel option spelled `repeat` GREEN;
E1 keeps `$guesté` GREEN. AC(b)'s six mutations (F1-F6) and AC(c)'s anti-vacuity (G1) re-run against
the reworked guard, unchanged verdicts.

**Not done, deliberately.** No commit, no `just play`, no live call, no vault value; gates
1b/2b/3b/4d untouched; no dashboard or ansible file edited; the round-11 PromQL reader untouched.

### Step 5a REWORK round 3 — task-1785497167-e413, `code-assist:plex-monitoring:guard:dashboard-template-vars-declared`

Answering the round-2 review's F1/F2 — both on the ACCEPT side of the row round 2 built. One file
edited: `scripts/test_grafana_provisioning_shape.py` (`5801f0db` → `9b99dce1`).

**Reproduced before changing anything.** The review's battery, run verbatim against the guard as
round 2 left it: **6/12**, exactly the score it reports.

**F1 — an undeclared ALL-DIGIT name is PromQL's capture group, and is now skipped** (DEC-101,
`_PROMQL_CAPTURE_GROUP`). Both halves sourced, not recalled:
`logs/calibration-step05a-r3-capture-group.py` / `.log` → **7/7** rc=0, every extractor raising on a
miss. Out of `grafana/grafana:13.1.0`: the `return match` branch of
`template_srv.ts::_evaluateVariableExpression`, and NO digit special-casing anywhere in that file, so
`$1` takes the same branch as `$guestt` and reaches Prometheus verbatim. Out of
`prom/prometheus:v3.12.0` (`promtool test rules`): `label_replace(pve_up{id="lxc/110"}, "guest_name",
"$1", "id", "lxc/(.*)")` → `guest_name="110"`; the same with a bare `1` → the literal `"1"`; Go's
`${1}` → `"110"` as well, which is why the skip tests the NAME (both alternations form it) rather
than one spelling. The skip yields to a declaration and is counted and printed separately from the
references checked (`… 0 skipped as PromQL capture groups …`).

**F2 — a literal `$` in prose SPLITS** (DEC-102). `$5/month` in a markdown text panel dies with the
digit skip. `$HOME` in a `description` is a DECLARED BOUND: a description is interpolated at render
(`VizPanel.getDescription` → `this.interpolate(description)`, calibration A4), so it and a dangling
`$guestt` are the same runtime event and nothing in the document separates them; the only "fix"
would be to stop reading descriptions and titles, where a real `$guest` is substituted and read by a
human. The refusal stands, loud, and the escape is one edit.

**Verification.**

* `logs/red-step05a-rework-r3.py` → **22/22** (`…-post.log`), was **16/22** against the unfixed guard
  (`…-pre.log`) with the six misses exactly B1-B5 and C1.
* The SAME 22 rows against a MECHANICALLY reverted copy (`logs/red-step05a-rework-r3-revert.py`,
  each inverse edit asserted to apply exactly once) → **15/22** (`…-reverted.log`); the seven misses
  are those six plus D8's reason-clause, which cannot fire on the old guard. Copy lived in
  `scripts/` and was deleted in a `finally`.
* `just test` → **GATE PASS 36/36** rc=0 (`logs/gate-step05a-rework-r3.log`); guard **PASS 19/19**.
* Round 2's battery re-run → **32/32**, unchanged (`logs/red-step05a-rework-r2-rerun-r3.log`).
* The review's own battery re-run VERBATIM → **10/12**, was 6/12
  (`logs/critic-step05a-r2-dollar-capture-rerun-r3.log`). BOTH remaining misses are intentional and
  named by the review itself: C2 is DEC-102's declared bound, and E4 is the row the review scores
  `want=RED` while writing "that is not a defect … do not widen `_dashboard_repeat_clauses` for it".
* Every mutation reverted in a `finally`; sha256 of the 3 dashboards + `tasks/main.yml` identical at
  both ends of every run (`a8a8c24e` / `1e8f3617` / `fde25673` / `71e88a89`).

**Not done, deliberately.** No commit, no `just play`, no live call, no vault value; gates
1b/2b/3b/4d untouched; no dashboard or ansible file edited; the round-11 PromQL reader untouched.

## 2026-07-31 — Step 5a REWORK round 4 (task-1785497167-e413, review.rejected F1/F2)

Active task: `code-assist:plex-monitoring:guard:dashboard-template-vars-declared`. One file edited:
`scripts/test_grafana_provisioning_shape.py` (`9b99dce1` → `884a5fe4`).

**The review reproduces first.** `just test` 36/36 rc=0 and guard PASS 19/19 at the handed-off sha,
its `logs/critic-step05a-r3-battery.py` 12/16 and `logs/critic-step05a-r3-named-group.py` 4/4.

**F1 — the same Go grammar has four spellings and round 3 shipped two.** `label_replace` calls Go's
`Regexp.Expand`, which resolves `$name`/`${name}` against a `(?P<name>…)` group as well as `$1`/`${1}`
against a numbered one. THE GRAMMAR IS ENUMERATED FROM ITS ENGINE, not from the example that prompted
the fix (`logs/calibration-step05a-r4-named-group.py` / `.log`, **10/10**, every extractor raising on a
miss): both named spellings work (B1/B2); Go 1.22's `(?<name>` synonym — which nobody had named — is
ACCEPTED by `prom/prometheus:v3.12.0` (B3); a group name is `\w`, Grafana's alphabet (B4); an
undeclared name expands to EMPTY (B5); Go takes a name as long as possible, so `$ctx` beside
`(?P<ct>…)` is dead (B6); `$$` is Go's literal-`$` escape (B7); and Expand resolves against
`label_replace`'s regex ARGUMENT only, so a group declared in a matcher beside the call does not
resolve in it (B8). Grafana hands the reference over intact — the `if (!variable)` branch `return
match`s and nothing on that path knows what a capture group is (A1/A2). So the skip is on an EXACT
name whose declaration sits in THE SAME STRING, in either Go spelling; it fails closed everywhere
else and the per-string scope is declared as the bound it is. DEC-103.

**F2 — the anti-vacuity clause is a WHOLE-INVENTORY floor and the docstring claimed more.** One
declared-and-used variable anywhere satisfies it, so the PVE drop-down can leave outright while the
row stays GREEN. The repair is the SENTENCE (the extent stated, the unseen mutation named) plus
per-dashboard `n ref/n declared` counts on the printed line, so that state is legible. Making it FAIL
wants a pin on the PVE dashboard's own declaration — a claim about one dashboard's identity, which
the review itself prices as "a different row"; recorded as
`code-assist:plex-monitoring:guard:pve-dashboard-declares-its-drop-down` rather than dropped. DEC-104.

**Verification.**

* `logs/red-step05a-rework-r4.py` → **29/29** (`…-post.log`), was **21/29** against the unfixed guard
  (`…-pre.log`), the eight misses exactly B1-B5 (the named spellings), C7 (anti-vacuity under the new
  skip) and D1/D4 (the F2 sentence and counts).
* The SAME 29 rows against a MECHANICALLY reverted copy (`logs/red-step05a-rework-r4-revert.py`, six
  inverse edits each asserted to apply exactly once, plus the F2 paragraphs cut back to round 3's
  sentence) → **20/29** (`…-reverted.log`): those eight plus D3, which can only fail where the false
  claim is still present. Copy lived in `scripts/` and was deleted in a `finally`.
* `just test` → **GATE PASS 36/36** rc=0 (`logs/gate-step05a-rework-r4.log`); guard **PASS 19/19**
  (row count unchanged: the row existed, its accept side was blind to half a grammar).
* Round 3's battery re-run **22/22**, round 2's **32/32** — unchanged.
* The round-3 review's battery re-run VERBATIM → **15/16** (was 12/16); the one miss is its C1, the
  F2 mutation that DEC-104 deliberately leaves GREEN for the reason the review gave when it named the
  pin a different row. The round-2 review's battery re-run → **10/12**, unchanged, both misses named
  by the review itself (C2 = DEC-102's declared bound, E4 = the legacy `rows[]` repeat it wrote "is
  not a defect").
* Every mutation reverted in a `finally`; sha256 of the 3 dashboards + `tasks/main.yml` identical at
  both ends of every run (`a8a8c24e` / `1e8f3617` / `fde25673` / `71e88a89`).

**Not done, deliberately.** No commit, no `just play`, no live call, no vault value; gates
1b/2b/3b/4d untouched; no dashboard or ansible file edited; the round-11 PromQL reader untouched.

## 2026-07-31 — Step 5a REWORK round 5 (task-1785497167-e413) — `review.rejected` F1

**Task.** `code-assist:plex-monitoring:guard:dashboard-template-vars-declared`. Round-4 review: the
capture-group exemption is a test on the NAME, applied to spellings Go cannot read. F2 was accepted
and is not re-litigated.

**Reproduced the review first, every number of it.** `logs/critic-step05a-r4-battery.py` **9/15** with
the misses exactly C1-C4 + D1-D2 and the controls E1/E2 RED, `logs/critic-step05a-r4-spelling.py`
**9/9**, `just test` 36/36 rc=0, guard PASS 19/19 at `884a5fe4` as handed off. The finding is real.

**Built.** `_promql_capture_reference` now takes the SPELLING and reads the name back out of it with
a constant transcribed from Go's own `extract()` (`_PROMQL_EXPAND_REFERENCE`,
`\$(?:(\w+)|\{(\w+)\})\Z`); both exemptions moved behind the declared test, which is Grafana's
`getVariableAtIndex`-before-`macroRegistry` order and the review's "minor". DEC-105.

**Verification.**

* `logs/calibration-step05a-r5-spelling-intersection.py` → **19/19** (`.log`), `prom/prometheus:v3.12.0`
  via `promtool test rules`, every extractor raising on a miss. Exhaustive by construction:
  `_GRAFANA_INTERPOLATION` pinned by pattern text and group count (7 texts per name), the guard's own
  tokeniser made to read all 14 texts as the name under test, then the engine asked. Go resolves
  `$name` and `${name}` and nothing else, on BOTH halves. `${ct.tail:raw}` had been measured by no
  earlier calibration or review here.
* `logs/red-step05a-rework-r5.py` → **25/25** (`…-post.log`), was **14/25** against the unfixed guard
  (`…-pre.log`), the eleven misses exactly C1-C5, D1-D5 (the five literal spellings on each half) and
  F1 (the ordering).
* The SAME 25 rows against a MECHANICALLY reverted copy (`logs/red-step05a-rework-r5-revert.py`,
  three inverse edits each asserted to apply exactly once, plus checks that the new constant survives
  as a definition and is unreachable) → **14/25** (`…-reverted.log`), the same eleven. Copy lived in
  `scripts/` and was deleted in a `finally`.
* The round-4 review's own battery re-run VERBATIM → **15/15** (was 9/15).
* `just test` → **GATE PASS 36/36** rc=0 (`logs/gate-step05a-rework-r5.log`); guard **PASS 19/19**,
  count unchanged — the row existed, its accept side read a name where it owed a text.
* Rounds 4/3/2 batteries re-run **29/29**, **22/22**, **32/32**; the round-3 review's **15/16** and
  the round-2 review's **10/12**, all unchanged, every remaining miss already named as a declared
  bound or as task-1785524605-ea55.
* Every mutation reverted in a `finally`; sha256 of the 3 dashboards + `tasks/main.yml` identical at
  both ends of every run (`a8a8c24e` / `1e8f3617` / `fde25673` / `71e88a89`); guard `884a5fe4` →
  `b1013daa`.

**Not done, deliberately.** No commit, no `just play`, no live call, no vault value; gates
1b/2b/3b/4d untouched; no dashboard or ansible file edited; F2 and the round-11 PromQL reader
untouched.

## 2026-07-31 — Step 5a REWORK round 6 (task-1785497167-e413), `review.rejected` F1 → the accept side's TWO ENDS

**What the review found.** Round 5's exemption tests the TEXT, which fixed the five spellings Go
cannot read — and `\Z` anchors that test to the end of the text GRAFANA matched. Grafana's alphabet
is ASCII; Go's `extract()` takes `unicode.IsLetter`/`IsDigit`/`_`. So `$ctß` beside `(?P<ct>…)` is a
reference to `ctß` that expands to NOTHING (the label is dropped), while the guard looked up the
prefix `ct`, found it declared as a group, and printed "1 skipped as PromQL capture groups". A
declared prefix exempting an undeclared full name is the wave-through direction.

**The same claim has a second side, and this file asserted its opposite.** Go spends `$$` as a
literal `$` BEFORE it calls `extract()`, and Grafana's tokeniser matches at the SECOND `$` — so
`$$ct` was exempted too, while the panel draws the literal text `$ct`. The docstring said that one
"is not skipped". It was. Both facts live one character OUTSIDE the matched text, one on each side,
which is why the repair is a predicate over the STRING AND THE SPAN and not a trailing-character
test: `_promql_capture_reference(text, span, groups)` now asks Go's four questions in Go's order —
is this `$` a reference or a spent escape (parity of the `$` run in front), is the text one Go reads,
does Go's name END where Grafana's did (`_go_expand_absorbs`), and is that name a positional group or
one the same string declares. `_grafana_interpolations` carries the span and stays Grafana's, whole.
DEC-107.

**The alphabet is transcribed, not approximated.** `unicode.IsLetter` is category L and
`unicode.IsDigit` is Nd — not Nl, not No — and Python's `isalpha()`/`isdecimal()` are exactly those
two. Python's own `\w` takes `isalnum()` and would refuse `$ctⅧ` and `$ct²`; an ASCII-shaped test
would refuse `$ctµ`. The pinned engine expands all three, so both obvious approximations are FALSE
REFUSALS and each is a battery row rather than an argument.

**Verification.**

* `logs/calibration-step05a-r6-name-boundary.py` → **69/69** (`.log`), `prom/prometheus:v3.12.0` via
  `promtool test rules`, every extractor raising on a miss. Enumerated by CATEGORY, not from the
  character that prompted the fix: sixteen boundary characters (L's five subcategories, Nd in two
  scripts, No/Nl/Mn/Pd/Pc/Pe/Po) put to the engine on the named half, the numbered half and both
  brace forms, each compared to `_go_expand_absorbs`; H1-H5 measure both `$$` parities on both
  spellings; G1-G3 re-pin `_GRAFANA_INTERPOLATION` by pattern text, group count and `re.ASCII`.
* `logs/red-step05a-rework-r6.py` → **24/24** (`.log`), was **16/24** against the unfixed guard
  (`…-pre.log`), the eight misses exactly B1-B8 (six alphabet rows across Ll/Lo/Nd on both halves,
  two `$$` rows).
* The SAME 24 rows against a MECHANICALLY reverted copy (`logs/red-step05a-rework-r6-revert.py`, five
  inverse edits each asserted to apply exactly once, plus checks that `_go_expand_absorbs` survives
  as a definition and is unreachable) → **16/24** (`…-reverted.log`), the same eight. Copy lived in
  `scripts/` and was deleted in a `finally`.
* The C rows are the point of the revert: eight working queries (`${ct}ß`, `$ct²`, `$ctⅧ`, `$ct—`,
  `${1}ß`, `$$$ct`, a cosmetic non-ASCII title, a DECLARED `$guestß`) GREEN at BOTH ends, so the fix
  did not buy B by breaking C. D1/D2 are RED at both ends — the tokeniser, not the boundary.
* The round-5 review's own battery re-run VERBATIM → **9/10** (was 7/10); the remaining miss is its
  D1, the per-string scope DEC-103 declares and which the review excluded from the rejection.
* Rounds 5/4/3/2 batteries **25/25**, **29/29**, **22/22**, **32/32**; the round-4 review's **15/15**,
  the round-3 review's **15/16**, the round-2 review's **10/12** — all unchanged, every remaining miss
  already named as a declared bound or as task-1785524605-ea55.
* `just test` → **GATE PASS 36/36** rc=0 (`logs/gate-step05a-rework-r6.log`); guard **PASS 19/19**
  (`logs/guard-step05a-rework-r6.log`), count unchanged — the row existed; its accept side read the
  text but not either end of it.
* Every mutation reverted in a `finally`; sha256 of the 3 dashboards + `tasks/main.yml` identical at
  both ends of every run (`a8a8c24e` / `1e8f3617` / `fde25673` / `71e88a89`); guard `b1013daa` →
  `9dabefbe`.

**Two round-5 scripts no longer run, loudly and in the safe direction.**
`logs/critic-step05a-r5-alphabet.py` raises `ValueError` on the 2-tuple unpack and
`logs/calibration-step05a-r5-spelling-intersection.py` raises its own `NotSourced` instrument guard
rather than measuring the wrong thing — both are round-5-API calibrations superseded by the round-6
one. Every mutation battery is subprocess-based and unaffected, which is why the numbers above are
re-runnable.

**Not done, deliberately.** No commit, no `just play`, no live call, no vault value; gates
1b/2b/3b/4d untouched; no dashboard or ansible file edited; the round-11 PromQL reader, F2's
anti-vacuity sentence and DEC-103's per-string scope untouched.

## 2026-07-31 — Step 5a REWORK round 7 (task-1785497167-e413) — the SUBSTITUTION seam, both ends

**The finding, reproduced first.** The round-6 review's own battery
(`logs/critic-step05a-r6-substitution-seam.py`) re-runs **21/25** under my hand at the handed-off
guard `9dabefbe`, the four misses exactly S1-S4, and `just test` 36/36 with guard PASS 19/19.

**The repair.** `_promql_capture_reference` now takes the set Grafana will REPLACE
(`declared | GRAFANA_BUILT_IN_VARIABLES`) and refuses the exemption when a replaced reference abuts
the match — ENDING at its start (both spellings; `$$` pairing is decided in front of the `$`) or
BEGINNING at its end (unbraced only; a `}` ends the name for both readers). `_grafana_substituted_spans`
is that list. The row's docstring paragraph claiming the on-disk string is what `Expand` takes is
replaced by what the two engines do. DEC-109.

**Calibration** (`logs/calibration-step05a-r7-substitution-boundary.py` / `.log`, **16/16**, every
extractor raising on a miss). Grafana 13.1.0 offline off the `.js.map` sourcesContent: the
substituter's order is declared → registered macro → `return match` (G1); ONE global `String.replace`
pass, so a value's own text is never rescanned (G2); `$__from`/`$__to` are written straight into the
variable INDEX as `timeRange.from.valueOf().toString()`, an epoch-millisecond number, so a built-in
neighbour moves the boundary exactly as a declared one does (G3); and `timeFilter` is in the guard's
set without being a macro or an index entry, so the set is a superset that can only refuse (G4).
prom/prometheus:v3.12.0 via `promtool test rules`: `$ctlxc/110` → `/110` (E2, wrong not missing),
`$ct1753900000000` → gone (E3), `${ct}lxc/110` → `110lxc/110` (E4 — the brace form is a WORKING
query and stays exempt), `lxc/110$ct` → `lxc/110110` (E7 — what the left-hand refusal costs),
`lxc/110$$ct` → `lxc/110$ct` and `lxc/110$${ct}` → the literal `${ct}` (E8/E10 — why it is refused
anyway), `$ct-lxc/110` / `lxc/110-$ct` → working (E6/E11 — the one-character escape).

**Evidence.**
* `logs/red-step05a-rework-r7.py` **26/26** (`…-post.log`); **16/26** pre-fix (`…-pre.log`), the ten
  misses exactly B1-B6 (right end, incl. a built-in neighbour) and C1-C4 (left end).
* The SAME 26 rows against a MECHANICALLY reverted copy (`logs/red-step05a-rework-r7-revert.py`,
  three inverse edits each asserted to apply exactly once, plus checks that
  `_grafana_substituted_spans` survives as a definition and is unreachable) → **16/26**
  (`…-reverted.log`), the same ten. Copy lived in `scripts/` and was deleted in a `finally`.
* The D rows are the point of the revert: eight working queries GREEN at BOTH ends, including
  `${ct}$guest` and `${1}$guest` (the brace escape) and `$ct-$guest` / `$guest-$ct` (the separator).
  E4 is the row that LOCATES the repair — `$ct$guestt`, an UNDECLARED neighbour, is RED for the
  dangling name while the line still prints `1 skipped as PromQL capture groups`, which is pinned by
  text; a rule written on adjacency rather than substitution would print `0`.
* The round-6 review's own battery re-run VERBATIM → **25/25** (was 21/25).
* Rounds 6/5/4/3/2 batteries **24/24**, **25/25**, **29/29**, **22/22**, **32/32**; the round-5
  review's **9/10** (its D1 = DEC-103's per-string scope, untouched), the round-4 review's **15/15**,
  the round-4 spelling harness **9/9**, the round-2 review's **10/12** — all unchanged.
* `just test` → **GATE PASS 36/36** rc=0 (`logs/gate-step05a-rework-r7.log`); guard **PASS 19/19**
  (`logs/guard-step05a-rework-r7.log`), count unchanged and the exemption counter still 0 on the
  delivered tree.
* Every mutation reverted in a `finally`; sha256 of the 3 dashboards + `tasks/main.yml` identical at
  both ends of every run (`a8a8c24e` / `1e8f3617` / `fde25673` / `71e88a89`); guard `9dabefbe` →
  `c1752670`.

**Two round-6 scripts no longer run, loudly and in the safe direction.**
`logs/calibration-step05a-r6-name-boundary.py` raises `TypeError: … missing 1 required positional
argument: 'substituted'` and `logs/red-step05a-rework-r6-revert.py` raises its own "revert is not
mechanical" guard. Both are round-6-API harnesses superseded by the round-7 pair; neither returns a
wrong answer. The signature was deliberately left WITHOUT a default, because a default set is
fail-open — a caller that forgets it would silently get round 6's behaviour (DEC-109).

**Not done, deliberately.** No commit, no `just play`, no live call, no vault value; gates
1b/2b/3b/4d untouched; no dashboard or ansible file edited; the round-11 PromQL reader, F2's
anti-vacuity sentence, DEC-103's per-string scope and DEC-104's whole-inventory floor untouched.

## 2026-07-31 — Step 5a REWORK round 8 (task-1785497167-e413, `review.rejected` F1 → the parity RUN's far edge)

**The change, in one expression.** `_promql_capture_reference`'s left-hand abutment now asks
`any(stop == start - run)` instead of `any(stop == start)`, where `run` is the `$` run the parity
clause one line up already counts. Go pairs `$` from the START of a maximal run, so a substituted
value can lengthen that run from its FAR EDGE however many `$` this file wrote; at `run == 0` the
new clause IS round 7's, which is what makes "no control moves" checkable rather than hopeful.
Fact 1 of the docstring, which asserted the opposite, is rewritten — and it now also states that
the RIGHT-hand end has no distance analogue, so a ninth round does not over-repair. DEC-111.

**Verification (`just test` last, everything from the repo root, `.venv/bin/python`).**
* Calibration `logs/calibration-step05a-r8-parity-run-distance.py` / `.log` → **13/13**, every
  extractor raising on a miss. `grafana/grafana:13.1.0` offline off the `.js.map` sourcesContent
  (one global `String.replace` pass; the tokeniser's own start/run/neighbour numbers for the three
  seam texts; and the structural row — NO interpolation span can END in a `$` across all 14 texts,
  so `start - run` is the ONE index a neighbour can reach the run at). `prom/prometheus:v3.12.0` via
  `promtool test rules`: run=4 ordinary → `lxc/110$$110`, run=4 `$`-terminated → `lxc/110$$$ct`
  (`ct` LITERAL); the accept side `$guestt$$$ct` → `$110`; the separator escape at both value
  flavours; and the built-in price stated (`1750000000000$$$ct` → `1750000000000$110`).
* `logs/red-step05a-rework-r8.py` / `.log` → **25/25** post-fix, **19/25** pre-fix with the six
  misses exactly B1-B6.
* The SAME 25 rows against a MECHANICALLY reverted copy (`logs/red-step05a-rework-r8-revert.py`,
  one inverse edit asserted to apply exactly once, plus body-level checks that the round-8 local is
  gone and round 7's clause is back verbatim) → **19/25**, the same six. Copy in `scripts/`, deleted
  in a `finally`.
* The C and D rows are the point of the revert: seven working queries GREEN at BOTH ends
  (`$$$ct` with nothing in front, `$guest-$$$ct` across a separator, `${ct}$guest`, `$ct-$guest`,
  `$ct²`) and eight RED at both ends. D8 LOCATES the repair — `$guestt$$$ct`, an UNDECLARED
  neighbour, keeps its `1 skipped as PromQL capture groups` (pinned by TEXT) while the dangling
  `guestt` is reported; a rule written on adjacency would print `0`.
* **The review's own battery goes 20/23 → 19/23, and the drop is proven rather than asserted**:
  `logs/critic-step05a-r7-recheck-r8.py` / `.log` → **7/7**. The four misses are exactly the four
  rows that ENCODE the defect — P3/P4 `want=True` ("the predicate exempts `$guest$$$ct`"), and
  S1/S2 whose COLOUR flips to RED as asked while their `1 skipped as PromQL capture groups` pin is
  now correctly ABSENT. S3, the run-length row with no pin, flips cleanly to OK; every control
  (K1-K5, P1/P2/P5/P6) and every engine row still scores.
* Rounds 6/5/4/3/2 batteries **24/24**, **25/25**, **29/29**, **22/22**, **32/32**; the round-6
  review's **25/25**, round-5's **9/10**, round-4's **15/15**, r4-spelling **9/9**, round-2's
  **10/12** — all unchanged.
* `just test` → **GATE PASS 36/36** rc=0 (`logs/gate-step05a-rework-r8.log`); guard **PASS 19/19**
  (`logs/guard-step05a-rework-r8.log`), row count unchanged and the exemption counter still 0 on
  the delivered tree.
* Every mutation reverted in a `finally`; sha256 of the 3 dashboards + `tasks/main.yml` identical at
  both ends of every run (`a8a8c24e` / `1e8f3617` / `fde25673` / `71e88a89`); guard `c1752670` →
  `b2684f33`.

**One round-7 script no longer runs, loudly.** `logs/red-step05a-rework-r7-revert.py` raises its own
`revert is not mechanical: 0 occurrence(s) of 'start, end = span'` — round 8 edited two of the lines
its inverse hunk quotes. It fails LOUD and returns no wrong answer; round 7's FORWARD battery
(`logs/red-step05a-rework-r7.py`) still runs unchanged and is **26/26**, and round 7's clauses are
re-proven here by D1/D3 (RED at both ends) and by the r8 revert copy, which IS round 7's behaviour.
Same treatment round 7 gave the two superseded round-6 harnesses.

**Not done, deliberately.** No commit, no `just play`, no live call, no vault value; gates
1b/2b/3b/4d untouched; no dashboard or ansible file edited; one source file changed
(`scripts/test_grafana_provisioning_shape.py`); the round-11 PromQL reader, F2's anti-vacuity
sentence, DEC-103's per-string scope and DEC-104's whole-inventory floor untouched.

## 2026-07-31 — Step 5a CLOSED (Finalizer, task-1785497167-e413) → `queue.advance`

**THE ROW ENDED WHERE DEC-110 SAID IT WOULD.** Round 8's `review.passed` carried one defect and
routed it here rather than to a ninth round: Fact 1's sentence named `$guest$$$ct` and then gave
`$guest$$$$$ct`'s measurements. DEC-110 had pre-committed in writing — *"either repair ends this row,
and the Finalizer should treat the second as terminating"* — and the five rejection triggers are a
concrete bug, a missed requirement, a likely regression, failed verification and over-engineering.
An illustration that points one run out is none of them. **I made the correction here, in this hat,
and proved it cannot change a verdict.**

**I REPRODUCED THE HANDOFF BEFORE I TOUCHED ANYTHING.** `just test` **GATE PASS 36/36 rc=0**; guard
**PASS 19/19** at the handed-off `b2684f33`; `logs/red-step05a-rework-r8.py` **25/25**. Then the
defect itself, against the logs rather than against the prose: `logs/calibration-step05a-r8-parity-run-distance.log`
G2 `'$guest$$$ct': start=8 run=2` vs G3 `'$guest$$$$$ct': start=10 run=4`, and its E1/E2 (five `$` →
`lxc/110$$110`, six → `lxc/110$$$ct`) are **run=4's** rows; `$guest$$$ct`'s real pair is E2/E3 of
`logs/critic-step05a-r7-parity-run-seam.log` (three `$` → `lxc/110$110`, four → `lxc/110$$ct`). The
critic's F1 is exact.

**THE CORRECTION.** Each string now carries its own measurements — `$guest$$$ct` (run=2) with three/four
`$`, `$guest$$$$$ct` (run=4) kept beside it because it is what makes the test a RUN and not the number
two — and the run=2 rows are cited **by file**, since the old text called them "round 7's calibration"
when they are the round-7 *review's* battery (round 7's calibration's E2/E5 are the RIGHT seam and the
numbered brace row).

**PROVEN DOCSTRING-ONLY, NOT ARGUED.** `logs/finalizer-step05a-r8-exemplar.py` / `.log` **14/14**:
the module's AST with every docstring emptied is **identical** before and after (the BEFORE file
reconstructed by an inverse edit asserted to apply exactly once), while the trees **with** docstrings
differ — so the comparison ran against the edited file and not a stale copy. Then B1-B5 on the new
numbers and C1-C6 on the cited rows, every extractor raising on a miss.

**THE PLAN'S OWN DEMO, RUN END TO END** (`logs/finalizer-step05a-demo.py` / `.log` **9/9**). Not
another row-by-row battery — the mutation this step exists for, on the REAL file, through the guard's
own entry point: the delivered tree GREEN 19/19 (D1); one declaration and **13** `$guest`
interpolations present (D2); **F7b — rename `guest` → `guestt` — now `rc=1` RED where the Step 4b
Finalizer scored it GREEN 13/13** (D4), naming both the dangling reference and the renamed
declaration so the operator is told which edit did it (D5/D6); and the anti-vacuity control that
locates it — rename the declaration **and all 13 uses** and the consistent dashboard is GREEN again
(D7), so D4 is the dangling reference and not a reaction to the file changing. Reverted in a
`finally`, sha256 identical at both ends (D8), restored tree GREEN (D9).

**ACCEPTANCE CRITERIA, CHECKED AGAINST THE TASK TEXT RATHER THAN THE HANDOFF.** (a) gate 0, guard
19/19. (b) every mutation the task enumerates *by name* scores on the delivered guard —
`logs/red-step05a-template-vars.py` **29/29**: B1 F7 templating deleted RED, B3 F7b RED, B4 one
target dangling RED, B5/B6 the `${var}` and `[[var]]` spellings RED, B7 `$__rate_interval` GREEN, A1
cosmetic GREEN, plus E1-E6 (title, legendFormat, repeat, collapsed row, annotation, chained variable)
and F1/F2 (one dashboard's declaration must not satisfy another's). (c) anti-vacuity live, not
hypothetical: G1 unused declaration GREEN (the delete direction), H1 the whole-inventory floor RED.
(d) no live call, no `just play`, no vault value, no commit; gates 1b/2b/3b/4d untouched; HEAD still
`7e9c426`.

**POST-EDIT, EVERYTHING RE-RUN:** gate **36/36 rc=0**, guard **19/19**, red-r8 **25/25**, r7 forward
**26/26**, `logs/critic-step05a-r7-recheck-r8.py` **7/7**, round-1 battery **29/29**, and the round-8
fail-open sweep re-run against the corrected file. Guard `b2684f33` → `5696b01b`; the 3 dashboards
(`a8a8c24e` / `1e8f3617` / `fde25673`) and `tasks/main.yml` (`71e88a89`) **byte-identical**.

**NOT `LOOP_COMPLETE` — the wave is not exhausted.** Step 5 planned three: 5b
(`task-1785517907-a5ec`, datasource `type` vs the uid beside it) and 5c (`task-1785441840-e8eb`, the
`<svc>-web` twins' `rule` clause — the only one of the nine with a measured live consequence) were
both blocked by 5a alone and are now unblocked. The declared bound this row shipped rides on
`task-1785524605-ea55`, ready. Step 4d remains an OPERATOR-ONLY gate. → `queue.advance`.

## 2026-07-31 — Builder, Step 5b (task-1785517907-a5ec) — BUILT, `review.ready`

**THE ROW.** `test_delivered_dashboard_datasource_types_agree_with_the_provisioned_uid` — a carrier
that names a provisioned uid AND declares a `datasource.type` must declare THAT uid's type.
`grafana-datasource.yml.j2` declares both at every uid it provisions, so the comparison is
cross-file, and until now `{"type": "loki", "uid": "Prometheus"}` was a sentence no row disagreed
with. Guard **19/19 → 20/20**, gate **36/36 rc=0**. `_datasource_refs` now returns
`(path, uid, type)` — ONE walk, not a second walker over the same grammar — and the uid row's unpack
is the only other line that moved.

**I MEASURED THE TASK'S OWN RATIONALE AND IT IS FALSE — WHICH MAKES THE FIX MORE NECESSARY, NOT LESS**
(`logs/calibration-step05b-type-vs-uid-routing.py` / `.log` **10/10**, grafana/grafana:13.1.0, DEC-115).
The task says the mismatch means "that panel draws nothing". It does not: R3, through Grafana's own
query endpoint with a dead-URL datasource so the error names who was consulted, a query spelled
`{"type": "loki", "uid": "Prom5b"}` reaches the PROMETHEUS datasource, and R4 the reply is
BYTE-IDENTICAL to the matching-type control's. The uid routes; the type is only believed. So the
mismatched carrier still ships PromQL to Prometheus while
`test_delivered_dashboard_queries_are_readable` reads that type and stops asking where its query
lives. The exemption is NOT widened (probe N10 depends on it): the two rows compose, and the
readability row's docstring now says so.

**RED, AND THE EDIT IS PROVEN TO BE WHAT BOUGHT IT.** `logs/red-step05b-datasource-type.py` / `.log`
**15/15** — every row mutates the REAL files, runs the REAL guard, reverts in a `finally` with
sha256 asserted at both ends, and pins WHICH `FAIL` line spoke. B1 is probe N11 verbatim (the
measured exploit); B2 the mismatch alone; B3/B4/B5 panel, template variable, annotation; B6 a
CASE-only mismatch; B7 the anti-vacuity strip; B8 the provisioning side losing its own `type:`; B9
a second provisioned datasource referenced with the wrong type. Controls C1-C6 score both before and
after, including **C2 = probe N10**, and C4/C5 use the pin the other way (`forbid_row`) to show the
uid row still owns "no uid" and "unprovisioned uid". `logs/red-step05b-revert.py` / `.log` **6/6**:
the pre-edit guard reconstructed by inverse edits each asserted to apply exactly once is
**BYTE-IDENTICAL to the handed-off `5696b01b`**, still scores its own `PASS: 19/19`, and the same
battery against it is **6/15 with the misses exactly {B1-B9}**. Copy written to `logs/` — never
`scripts/`, which `run_gate.py` globs — and deleted in a `finally`.

**THE PROBE THAT FOUND THIS DEFECT NOW SCORES FULLY:** `logs/critic-step04c-r11-probe.py`
**19/20 → 20/20**, N11 being the row it was missing.

**SAID BEFORE THE NEXT HAT RUNS IT: `logs/finalizer-step05a-demo.py` GOES 9/9 → 6/9, AND IT IS A
COUNT PIN.** D1/D7/D9 match the guard's summary line `"PASS: 19/19"`; a twentieth row makes it read
`PASS: 20/20`. Proven rather than narrated (DEC-117) — `logs/red-step05b-demo-recheck.py` / `.log`
**10/10**: the misses are exactly {D1,D7,D9}, every row about the DEMO still scores (D2-D6, D8), the
guard is rc=0 at `PASS: 20/20`, the old count appears exactly three times so the substitution is
mechanical, and the SAME demo with that one number substituted is **9/9**. Step 5a's file is left
byte-identical — it is that round's evidence, not this round's to edit.

**DECLARED BOUND, WITH ITS MUTATION NAMED AND A TASK FILED (DEC-116).** Grafana's three built-in
uids are provisioned nowhere, so a carrier naming one is counted-and-skipped, and
`{"type": "loki", "uid": "-- Grafana --"}` with its query in an unknown key stays uncompared. I
looked for the constant rather than assuming: calibration R7/R9 (the built-ins are absent from the
provisionable list) and R8 (the server reports all three as the plugin CATEGORY `datasource` while
their ids differ), so pinning it needs a constant transcribed from Grafana's frontend — a different
claim, stale-on-upgrade, and wrong pins redden N10. Filed as
`code-assist:plex-monitoring:guard:builtin-datasource-type-unpinned`, blocked by 5b so it does not
land ready-and-unrouted.

**ACCEPTANCE CRITERIA.** (a) `just test` rc=0, guard count up by exactly the row added (19→20).
(b) RED under reverted mutations of the REAL files with sha256 asserted at both ends — B1-B9 above.
(c) controls GREEN including N10 — C2, plus C1/C3/C6 and the `forbid_row` pins C4/C5. (d)
anti-vacuity for the state where the row finds no typed carrier — B7 (every declared type stripped)
and B8 (the truth source loses its own type), and the floor is the row's own `if not compared`.

**EVERY PRIOR BATTERY RE-RUN, ALL UNCHANGED:** fail-open sweep **50/50**, r7-recheck-r8 **7/7**, r7
forward **26/26**, rounds 6/5/4/3/2 **24/24 25/25 29/29 22/22 32/32**, `red-step05a-template-vars`
**29/29**, `finalizer-step05a-r8-exemplar` **14/14**, `red-step04c-r3-mutations` **22/22**.

**WHAT I DID NOT DO.** One source file edited (`scripts/test_grafana_provisioning_shape.py`,
`5696b01b` → `39551b62`). No commit, HEAD still `7e9c426`; no `just play`, no live call, no vault
value; gates 1b/2b/3b/4d untouched. The 3 dashboards (`a8a8c24e` / `1e8f3617` / `fde25673`),
`tasks/main.yml` (`71e88a89`) and `grafana-datasource.yml.j2` (`2c1da6a6`) byte-identical at both
ends of every run; the grafana container the calibration starts is removed in a `finally`. 5c
(`task-1785441840-e8eb`) and 4d untouched. → `review.ready`.

## 2026-07-31 — Builder, Step 5c (task-1785441840-e8eb) — BUILT, `review.ready`

**THE HOLE, REPRODUCED BEFORE ANYTHING WAS WRITTEN.** `logs/red-step05c-web-twin-rule.py` /
`-PRE.log` against the delivered guard `1ec74652`: **6/17**, missing exactly the eleven M rows, every
one of them `PASS: 41/41` rc=0 on the full guard with the REAL templates — `whoami-web` →
`home.<domain>`, `prometheus-web`/`homepage-web`/`uptime-kuma-web`/`grafana-web` → `plex.<domain>`,
`traefik-dashboard-web` → `plex.<domain>` (the row with the measured 403/404), `plex-web` →
`traefik.<domain>`, `plex-web.service` → `api@internal` (the task's S1), a twin's rule DELETED, a
twin respelled `HostRegexp` and BOTH sides' rules deleted. Every row reverts in a `finally` with
sha256/8 of compose/dynamic/guard printed at both ends.

**LANDED:** `scripts/test_traefik_config_shape.py` `1ec74652` → `e91616eb`,
`test_web_twins_double_their_websecure_sibling` — **guard PASS 42/42**, `just test`
**GATE PASS 36/36 rc=0** (`logs/gate-step05c-web-twin-rule.log`). The same battery re-run is
**17/17**: all eleven M rows RED at `FAIL: 1/42`, controls GREEN — a host rename applied to BOTH
sides (C2), an `|| Host(...)` alternative added to both (C4), the scalar re-quoted (C3), a comment
naming another host above a twin (C5).

**THE ROW IS NAMED AS THE SPEAKER, NOT INFERRED FROM `1/42`.**
`logs/red-step05c-attribution.py` / `.log` **18/18** imports the guard fresh under each mutated tree
and calls ONLY the new row, so the verdict and the printed field belong to it. It also asks the two
questions the full-guard battery cannot, because in both states other checks redden too: **A2** one
twin renamed away → `examined=6, missing=['grafana-web']` RED (the row names what it lost rather
than passing on the six that remain), and **V2** both templates blanked → `examined=0` RED (`not
failures` is TRUE over an empty population; the row is not). Two new mutations the first battery did
not carry are here too — M12 `traefik-dashboard-web.service` → `plex` and M13 `whoami-web.service` →
`grafana` — so the service half is RED on BOTH providers, not only on `plex-web`.

**THE ONE RUNTIME DEFAULT THIS ROW ENCODES WAS MEASURED, NOT ASSUMED** (DEC-122):
`logs/calibration-step05c-web-twin-service-default.py` / `.log` **7/7** on the pinned
`traefik:v3.7.5` with the REAL docker provider, one container per row, all removed in a `finally`.
The delivered websecure siblings carry no `.service` label at all, so the sibling's backend is a
default: with ONE declared `traefik.http.services.<n>.*` the router lands on that declared service
(A); an explicit `.service` wins (B); with TWO declared and no `.service` the router is **absent
from `/api/http/routers` entirely** — ambiguity is LOUD, so the reader returns `None` and reddens
rather than guessing (C); with ZERO declared it is a CONTAINER-derived name no template line states,
returned as a marker so two silent sides still compare equal (D); and the delivered shape resolves
sibling and twin to ONE backend (E).

**THE COUNT WARNING WAS DISCHARGED BY SWEEP, NOT BY GREP** (`mem-1785533512-8085`).
`logs/red-step05c-count-pin-recheck.py` / `.log` **6/6**: 286 `.py` files under `logs/` + `scripts/`
(this harness excluded, and the carve-out is stated and asserted to be exactly one path), parsed by
**AST** so a `41/41` in a docstring is prose and a `41/41` in a comparison is a pin. **S1: zero live
literals pin `41/41`.** S2 enumerates the eight live `PASS: N/N` pins in files that run this guard —
they read **39/39 and 40/40**, i.e. they were ALREADY stale before this task, so 41 → 42 breaks
nothing that was scoring. S4 is the instrument's own anti-vacuity (a synthetic live pin IS seen, the
same text in a docstring is NOT). **I did not edit another hat's evidence.**

**THE ROUND-12 EVIDENCE INVERTS UNDER THE NEW GUARD, UNEDITED.**
`logs/review-step03a-r12-rule-clause.py` — the Critic harness that MEASURED this hole — re-run
untouched now reports R1/R2/R4 `declared ? measured RED` and R3 still RED, rc=0, tree byte-identical
(`logs/review-step03a-r12-rule-clause-AFTER-05c.log`).

**AC (a)-(d).** (a) `just test` rc=0 and the guard count up by exactly the row added, 41 → 42.
(b) RED under reproducible mutations of the REAL files reverted in a `finally` with sha256 at both
ends — M1-M13. (c) controls GREEN — C1-C5, and the structural comparison is what makes them so.
(d) anti-vacuity: `examined` is printed, `EXPECTED_WEB_TWINS` is a floor the discovery must clear,
and V2/A2 prove both directions.

**WHAT I DID NOT DO.** One source file edited (`scripts/test_traefik_config_shape.py`, `1ec74652` →
`e91616eb`). No commit, HEAD still `7e9c426`; no `just play`, no live call, no vault value; gates
1b/2b/3b/4d untouched. No template edited — `compose.yml.j2` `02a4c5c2` and `dynamic.yml.j2`
`097eca50` byte-identical at both ends of every run; every calibration container removed in its
`finally`. 5d (`task-1785524605-ea55`) and the deferred rows untouched; I did not close, fail or
create a task. → `review.ready`.

## 2026-07-31 — Step 5c REWORK round 2 (task-1785441840-e8eb) — `review.rejected` F1, the operator fail-open

**THE ROW'S OWN SENTENCE WAS THE THING BEING VIOLATED.** `test_web_twins_double_their_websecure_sibling`
says every twin "ANSWERS FOR its sibling's host"; `_rule_hosts` compared `Host(...)` ARGUMENTS, and a
traefik rule is a boolean expression, so `!Host(`h`)` — the exact complement — was scored as
agreement. Fixed at the seam the review named and the one that already fails closed: `_rule_host_args`
accepts `Host(`a`[, `b`…]) [ || Host(…) ]…` and refuses every other expression to the empty set the
caller already treats as a defect on either side (DEC-124).

**RED FIRST, AND THE HOLE IS ELEVEN ROWS WIDE.** `logs/red-step05c-rework-r2-operators.py` /
`-PRE.log` on the reviewed guard `e91616eb` is **7/18** — the misses are exactly N1-N11, each
`PASS: 42/42` rc=0 on the FULL guard with the real templates. Post-fix the same battery is **18/18**,
every N row `FAIL: 1/42` and the printed field naming the twin. It carries the review's five shapes
(N1-N5) plus the ones a blacklist would have missed: `|| PathPrefix` (N6), `Host(h) && Host(h)` (N7),
a parenthesised group (N8), BOTH sides negated (N9 — the two-empties fail-open in the operator
direction), and the SIBLING side on both providers (N10/N11).

**THE REVIEW'S OWN PROBE, RE-RUN VERBATIM: 3/8 → 8/8.** `logs/critic-step05c-rule-operators.py`
unedited → `logs/red-step05c-rework-r2-critic-probe-AFTER.log`. Its `want`s were all correct, so a
correct repair takes it to n/n and no drop needs explaining.

**AND THE FIX IS A STRICT NARROWING, PROVEN AGAINST THE PRE-FIX FILE ITSELF.**
`logs/red-step05c-rework-r2-differential.py` **51/51**: reconstructs the reviewed guard by an inverse
edit whose every marker is asserted to occur once, hashes it to **`e91616eb`** (S1 — the sha both
prior hats printed), imports BOTH modules and runs 42 expressions through each. S6: for every one,
the new reader returns the SAME set or NOTHING — never a different non-empty set. 12 readings kept,
19 withdrawn. The copy sits one level under the repo root and NOT in `scripts/` (which `run_gate.py`
globs), and is deleted in a `finally` (S3/S8), with the delivered guard byte-identical (S9).

**NOTHING THE PREVIOUS ROUND BOUGHT WAS LOST.** `logs/red-step05c-web-twin-rule.py` **17/17**,
`logs/red-step05c-attribution.py` **18/18** (the two reason strings gained the suffix
" disjunction"; that harness checks by SUBSTRING and its pins are prefixes, so its evidence stands
unedited), `logs/red-step05c-count-pin-recheck.py` **6/6** — no row was added, so the guard's printed
count is unchanged at 42/42 and no pin moved. `logs/review-step03a-r12-rule-clause.py`, the harness
that found the original hole, still inverts untouched (rc=0, `-AFTER-05c-r2.log`).

**GATE.** `just test` **GATE PASS 36/36 rc=0**, guard **PASS 42/42**
(`logs/gate-step05c-rework-r2.log`).

**WHAT I DID NOT DO.** One source file edited (`scripts/test_traefik_config_shape.py`, `e91616eb` →
`98d4442e`). No commit, HEAD still `7e9c426`; no `just play`, no live call, no vault value; gates
1b/2b/3b/4d untouched. No template edited — `compose.yml.j2` `02a4c5c2` and `dynamic.yml.j2`
`097eca50` byte-identical at both ends of every row. No other hat's evidence edited or deleted; no
task closed, failed or created; 5d and the deferred rows untouched. → `review.ready`.

## 2026-07-31 — Builder, Step 5c REWORK round 3 (review.rejected F1 → THE ARITY) — task-1785441840-e8eb

**RED FIRST, TEN ROWS WIDE.** `logs/red-step05c-rework-r3-arity.py` / `-PRE.log` on the reviewed
guard `98d4442e` is **7/17**, and the misses are exactly N1-N10 — the duplicated argument on
`plex-web` (file), `whoami-web` (docker) and `traefik-dashboard-web` (file), the SIBLING side
(`prometheus`), the blank second argument, ``Host(`h`) || Host(``)``, the blank-with-a-space, both
sides duplicated, and a two-HOST comma list on both `plex` sides. Post-fix **17/17**
(`-arity.log`), every N row with the twin NAMED in the printed `failures=` field — a row that
reddens for some other reason is not this battery seeing it, so the name is part of every RED want.

**THE FIX IS THE GRAMMAR, NOT A COUNT AT THE CALLER — DEC-126, conf 84.** `_HOST_ARG_RE` is now one
backtick-quoted scalar with at least one non-blank character, and it CAPTURES, so the shape accepted
and the value read are one statement instead of two (`fullmatch` + a separate `findall`). The
truthiness filter in `_rule_hosts` (`if h.strip()`) went with it: it dropped a blank argument and
kept the rest, which is how ``Host(`h`, ``)`` read `{h}` and compared equal to a plain sibling while
traefik disabled the router. Refusal belongs where the shape is decided.

**AND IT IS A STRICT NARROWING, PROVEN AGAINST THE REVIEWED FILE ITSELF.**
`logs/red-step05c-rework-r3-differential.py` **51/51**: reconstructs the reviewed guard by an inverse
edit whose every marker is asserted to occur once, hashes it to **`98d4442e`** (S1), imports BOTH
modules and runs 42 expressions through each. S6 — every one returns the SAME set or NOTHING, never
a different non-empty set; 11 kept, 11 withdrawn. Copy one level under ROOT, never `scripts/`,
deleted in a `finally`, delivered guard byte-identical (S3/S8/S9).

**THE THREE EXPECTATIONS THIS COSTS ARE FLIPPED AND PROVEN, NOT QUIETLY EDITED — DEC-127, conf 86.**
`red-...-r2-operators.py` C5 (GREEN → RED) and `red-...-r2-differential.py` K06/K12 (KEEP → REFUSE).
`logs/red-step05c-rework-r3-recheck.py` **18/18** runs each file BOTH ways against BOTH guards
(`98d4442e` reconstructed, `44eefe35` delivered): pre-flip@r2 18/18 and 51/51, flipped@r3 18/18 and
51/51, and the two cross cells fail on EXACTLY {C5} and {D-K06, D-K12}. The E-rows go further —
every row's OBSERVED value (`got=`, `old=`/`new=`) is identical pre-flip vs flipped on the same
guard, so the flip moved an expectation and never a measurement.

**THE REVIEW'S OWN HARNESS INVERTS, UNEDITED.** `logs/critic-step05c-r2-comma-arg.py` verbatim →
`-AFTER-r3.log` **11/11 → 7/11**, and the four drops are exactly its finding rows S1-S4, each now
`FAIL: 1/42` with the twin named (`plex-web@file(twin pins no Host() disjunction)`). Its runtime
rows are untouched (R0 200, R1 404, R1b `status='disabled'`) because traefik did not move.

**NOTHING THE PREVIOUS ROUNDS BOUGHT WAS LOST.** web-twin-rule **17/17**, attribution **18/18**,
count-pin-recheck **6/6** (no row added → the printed count stays 42/42), carrier-sweep **60/60**,
`critic-step05c-rule-operators.py` **8/8** — all re-run post-fix into `-AFTER-r3.log` files, the
round-2 logs left as they were written.

**GATE.** `just test` **GATE PASS 36/36 rc=0** (`logs/gate-step05c-rework-r3.log`), guard
**PASS 42/42**.

**WHAT I DID NOT DO.** One source file (`98d4442e` → `44eefe35`), and two of my own prior batteries
flipped in place. No commit, HEAD still `7e9c426`; no `just play`, no live call, no vault value;
gates 1b/2b/3b/4d untouched; no template edited (`compose.yml.j2` `02a4c5c2`, `dynamic.yml.j2`
`097eca50` byte-identical at both ends of every run); no other hat's evidence edited; no task closed,
failed or created; 5d and the deferred rows untouched. → `review.ready`.

## 2026-07-31 — Builder, Step 5c REWORK round 4 (review.rejected F1 → THE WHITESPACE CLASSES) — BUILT

**RED FIRST, AND WIDER THAN THE REVIEW'S FINDING.**
`logs/red-step05c-rework-r4-gowhitespace.py` / `-PRE.log` on the reviewed guard `44eefe35` is
**9/21** and the twelve misses are N1-N12 — the review's own seam (the tokeniser skip) plus THREE
MORE the review's stated one-line fix does not reach, each measured through the FULL guard at
`PASS: 42/42` before it was written:

  seam 1  `_rule_host_args`' `rule[i].isspace()`        the traefik rule lexer   N1-N5
  seam 2  `_HOST_ARG_RE`'s `\s*` INSIDE the parens      the same lexer           N6-N8
  seam 3  `_router_rule`'s `[^\S\n]*` after `rule:`     YAML's `s-white`         N9-N10
  seam 4  `_scalar_entry`'s trailing `\s*` on a label   YAML again, and          N11-N12
          + `_yaml_unquote`'s bare `.strip()`           `_yaml_unquote` is why
                                                        a fix to seam 3 alone
                                                        left N9/N10 green

Post-fix **22/22**. Every RED row requires the twin NAMED in the printed `failures=` field. M0 is the
price, measured not argued: NEITHER delivered template holds one non-Go whitespace character. W1
enumerates where Python's `\s` and Go's `unicode.IsSpace` differ over Latin-1 (`0x1c-0x1f`, Python
only) and pins the DIRECTION — the guard refuses what the engine accepts, a loud false refusal.

**THE FIX IS ONE STATEMENT — DEC-129, conf 86.** Every class comes from the engine that reads those
bytes: `_GO_SPACE = " \t\r\n"` outside the backticks (Go's `go/parser` lexer, via
`vulcand/predicate`), YAML's space-or-tab plus the line break at the two YAML seams. The class left
UNICODE is deliberate and stated: whether an argument is BLANK is traefik's own `strings.TrimSpace`.

**STRICT NARROWING, AGAINST THE REVIEWED FILE ITSELF.**
`logs/red-step05c-rework-r4-differential.py` **61/61** reconstructs `44eefe35` by an inverse edit
(every marker asserted to occur its expected number of times) and hashes it to that sha. Both modules
imported: S6 — 38 expressions through `_rule_hosts`, every one the SAME set or NOTHING (11 kept,
11 withdrawn); S8 — 13 texts through the two YAML seams END TO END (`_router_rule` on real router
blocks, `_scalar_entry` on real label entries), every one the same scalar or refused. Copy one level
under ROOT, never `scripts/`, deleted in a `finally`.

**THE THREE HARNESSES THIS COSTS ARE PROVEN MECHANICAL, NOT ROTTED.**
`logs/red-step05c-rework-r4-recheck.py` **17/17**: the r2 differential, the r3 differential and the
r3 recheck all reconstruct an OLDER guard from the delivered file, so this round's edits retire them
by construction. Run against `44eefe35` (reconstructed BY SHA, so the bytes are the reviewed file)
they score **51/51, 51/51, 18/18** again; against the delivered `ea1cca07` all three fail IN THE
RECONSTRUCTION with **no `[FAIL] D-` behavioural row anywhere**. Their files are untouched.

**THE REVIEW'S OWN TWO HARNESSES INVERT, UNEDITED.**
`logs/critic-step05c-r3-unicode-space-guard.py` verbatim → `-AFTER-r4.log`, **11/11 → 3/11**, and the
eight drops are exactly its finding rows S1-S8, each now `FAIL: 1/42` with the twin named.
`logs/critic-step05c-r3-gate-loudness.py` → `-AFTER-r4.log` **2/2 → 1/2**: G1 was "the FULL gate is
GREEN on a tree whose whoami-web router is dead" and is now `GATE FAIL: 1/36` naming
`shape: scripts/test_traefik_config_shape.py`. That row's vector is the trailing label U+00A0 — seam
4 — so the review's own loudness harness would have stayed green under the one-line fix it proposed.

**NOTHING THE PREVIOUS ROUNDS BOUGHT WAS LOST.** web-twin-rule **17/17**, attribution **18/18**,
count-pin-recheck **6/6** (no row added → the printed count stays 42/42), r2-operators **18/18**,
r3-arity **17/17**, carrier-sweep **60/60**, `critic-step05c-rule-operators.py` **8/8**,
`critic-step05c-r2-comma-arg.py` **7/11** (unmoved from `-AFTER-r3`) — all re-run post-fix into
`-AFTER-r4.log` files, the earlier logs left exactly as their authors wrote them.

**GATE.** `just test` **GATE PASS 36/36 rc=0** (`logs/gate-step05c-rework-r4.log`), guard
**PASS 42/42**, `44eefe35` → `ea1cca07`.

**WHAT I DID NOT DO.** One source file. No commit, HEAD still `7e9c426`; no `just play`, no live call,
no vault value; gates 1b/2b/3b/4d untouched; no template edited (`compose.yml.j2` `02a4c5c2`,
`dynamic.yml.j2` `097eca50` byte-identical at both ends of every run); no other hat's evidence edited
or deleted; no task closed, failed or created; 5d and the deferred rows untouched; no runtime
measurement of my own — the 404 / `illegal character U+00A0` evidence is the Critic's, cited by file
and row. → `review.ready`.

## 2026-08-01 — Builder, Step 5c REWORK round 5 (review.rejected F1 → the `service` CLAUSE) — BUILT

**THE ROW COMPARES FOUR CLAUSES; ROUND 4 TOOK ONE TO THE ENGINE, AND THE OTHER HAD FOUR SITES.**
The review named `_block_scalar`'s `[^\S\n]`/`(\S+)` — Python's unicode classes reading the file
provider's `service:`. Before writing the battery I asked which SITES read that clause, from the
guard's own AST, and there are four: the twin row through `_block_scalar`, plus three rows with a
hand-rolled `^\s*service:\s*<value>\s*$` of their own (`:875` plex public router, `:4528`
traefik-dashboard, `:4688` the tunnel twins). All four on `\s`.

**AND THE THREE PINS ARE NOT REDUNDANT WITH THE TWIN ROW — THEY ARE ITS ONLY COVER FOR THE
TWO-SIDED EDIT.** The twin row is RELATIVE, so a U+00A0 appended to BOTH `plex` and `plex-web`
reads equal on both sides and is invisible to it by construction. Row R1: that edit is
`PASS: 42/42` on the reviewed guard with BOTH routers dead — measured at the engine, E6, both hosts
404 while a third router in the same file answers 200.

**RED FIRST.** `logs/red-step05c-rework-r5-blockscalar.py` / `-PRE.log` — **14/23** on `ea1cca07`,
missing exactly N1-N5, R1, N7-N9; post-fix **23/23**. Full guard, real templates, reverted in a
`finally`, sha at both ends, every RED row required to name the guard row that saw it.

**THE FIX IS ONE READER PLUS ONE HELPER.** `_block_scalar`'s three classes become YAML's
(`s-white` = space|tab, value ends at `s-white` or `b-char`), and the three hand-rolled pins become
`_pins_scalar(block, key, value)` — the same reader, so the class question is answered once.
`logs/red-step05c-rework-r5-differential.py` **12/12**: the pre-edit file is reconstructed BY SHA
(`ea1cca07`), and over a **1120-block grid** through BOTH implementations all **480** pin
disagreements are one direction (old accepted / new refuses) and every disagreeing block carries a
non-`s-white` character — a strict narrowing, with the accept side (80) and refuse side (560)
both reached.

**THE ENGINES, MEASURED — the reader is shared by 8 keys across THREE parsers.**
`logs/red-step05c-rework-r5-engine.py` / `.log` **13/13**, pinned `traefik:v3.7.5` +
`prom/prometheus:v3.12.0`, real HTTP, containers removed in a `finally`: E1/E2 a TAB either side of
the value IS dropped by YAML (200, resolved `backend`) so the ASCII half of the fold stays; E3 the
QUOTE layer is YAML's (200, `backend`) — the reader returns the RAW token, so a one-sided re-quote
is a FALSE RED, stated as a price; E4 a U+00A0 in the router KEY leaves the router alive and
answering 200, so the guard reading it as `plex-web` (row S1) is NOT a fail-open; E5 U+00A0 as
INDENTATION takes the whole document (witness 404 too) — loud, and the guard's discovery floor
already reddens there (S2); P1 prometheus REFUSES `scrape_interval: 60s<NBSP>` at load; P2 ACCEPTS
`metrics_path: /pve<NBSP>` and the running server scrapes `/pve%C2%A0` — silent; P3 traefik's STATIC
`entryPoint: metrics<NBSP>` serves no metrics at all (404 where the control has 5 `traefik_` series).

**THE EXISTENCE CLAUSE SWEPT IN THE SAME RUN** (S1-S5): one GREEN and correct (E4), four RED and
fail-closed. The clause the row compares, not the path the review walked.

**THE TWO HARNESSES THIS RETIRES ARE PROVEN MECHANICAL.**
`logs/red-step05c-rework-r5-recheck.py` **6/6**: r4's `-differential` and `-recheck` are
version-pinned across the span this round edited, so they retire by construction (0/1 and 0/2, and
ONLY in their sha rows — no behavioural row failed). Against `ea1cca07` reconstructed by sha they
score **61/61** and **17/17** again. Neither file edited.
`logs/red-step05c-rework-r5-critic-recheck.py` **7/7**: the review's own battery goes 9/9 → **6/9**,
the misses are exactly its defect rows S1/S2/S3, each now `want=GREEN got=RED` naming
`service 'plex\xa0' != 'plex'`; a copy with only those three `want`s flipped (3 lines) is 9/9 again.
`logs/finalizer-step05a-demo.py` is 6/9 for the reason mem-1785533512-8085 records (a Step-5b count
pin) — it reads `test_grafana_provisioning_shape.py` and cannot be this round's.

**GATE.** `just test` **GATE PASS 36/36 rc=0** (`logs/red-step05c-rework-r5-gate.log`), guard
**PASS 42/42**, `ea1cca07` → `53338616`.

**RESIDUAL, NAMED RATHER THAN QUIETLY LEFT.** The same question — "is this whitespace class the
engine's?" — has ~167 sites in this file (every `\s`/`[^\S\n]`/`.strip()` in code). This round took
the four that read the `service` clause and the shared reader's other seven keys. The rest are
neither measured nor claimed; the general form belongs in one sweep row, not in a sixth rework
round on this task.

**WHAT I DID NOT DO.** One source file. No commit, HEAD still `7e9c426`; no `just play`, no live
call against the real homelab, no vault value; gates 1b/2b/3b/4d untouched; no template edited
(`compose.yml.j2` `02a4c5c2`, `dynamic.yml.j2` `097eca50` byte-identical at both ends of every run);
no other hat's evidence edited or deleted; no task closed, failed or created. → `review.ready`.

## 2026-08-01 — Finalizer, Step 5c (task-1785441840-e8eb) — CLOSED, `queue.advance`

**VERIFIED THE HANDOFF RATHER THAN INHERITING IT.** HEAD still `7e9c426`, no commit; guard
`53338616`, `compose.yml.j2` `02a4c5c2`, `dynamic.yml.j2` `097eca50` — all three the shas the
Builder and Critic each printed. `just test` run by me end to end: **GATE PASS 36/36 rc=0**, guard
**PASS 42/42 rc=0** (41 → 42 is the row this task bought, which is the plan's own Demo clause).

**MY OWN WORK WENT WHERE NO ROUND WENT: THE GROWTH DIRECTION.** Every battery in this task's five
rounds MUTATED a carrier the tree already has — round 2's 60-row carrier sweep, round 4's four
seams, round 5's 252-row service sweep, the review's 12/12 task-exemplars. All of them answer *is
an EXISTING twin asked its clauses?* The task's title says **ALL of them**, and the row is
quantified over what it DISCOVERS with `EXPECTED_WEB_TWINS` as a floor of 7 — so the second half of
that claim is *does a twin added tomorrow get asked the same four clauses?*, which a floor cannot
answer by construction (a new name is not in it, `missing` stays empty, the row stays green
whatever the newcomer says). `logs/finalizer-step05c-new-twin.py` / `.log` — **10/10**, full guard,
real templates, restored in a `finally`, shas at both ends: a new `smoke-web` pair inserted into
**both** providers is DISCOVERED (`examined` 7 → 8 in every row, floor untouched), GREEN when the
clauses agree (D1/F1), and RED **naming the newcomer in the row's own `failures=` field** when the
rule is repointed (D2/F2), the service is repointed (D3/F3), or the sibling is absent (D4/F4).
Discovery covers growth in both providers; the roster is genuinely a floor and not the population.

**I RE-MEASURED THE ONE JUDGEMENT THE PASS RESTS ON.** The review found a REAL blind class (F0:
`_block_scalar` never sees a template line — `_key_bounded_block` feeds it `splitlines()`, which
breaks on eight characters YAML 1.2's `b-char ::= LF | CR` does not) and did NOT file it, on the
ground that both delivery paths refuse the document. If that ground were wrong a silent one-router
kill would ship and this close would be premature, so I measured the loudness half independently on
the real compose parser: `logs/finalizer-step05c-f0-loudness.py` / `.log` — **12/12**. The guard is
**blind 8/8** at the file provider's `plex-web.service` (GREEN with the value mutated), and all
eight draw a **go-yaml load error** from `docker compose config` (`control characters are not
allowed` for 0x0b-0x1e, `could not find expected ':'` for NEL/LSEP/PSEP), with U+00A0 as the
contrast row drawing none. **The review's call was right** — loud on delivery, which is this task's
own recorded bar, the one it used to dismiss the duplicate-key finding.

**TWO CORRECTIONS MY OWN HARNESSES PAID FOR, STATED IN THEM RATHER THAN QUIETLY FIXED.** (1) The
first cut of the loudness rows classified on `rc`, and this repo's compose file fails PROJECT
VALIDATION under any crude Jinja flattener ("refers to undefined volume") — on `rc` alone all eight
rows would have passed for a reason unrelated to the mutation. They are written on the ERROR LAYER
(`go-yaml load error`, strictly earlier than project validation), and C2 anchors it. (2) The
blindness rows first mutated the DOCKER twin's `service` label, which `_compose_router_service`
reads and correctly reddens (blind 0/8) — `_block_scalar` is only on the FILE PROVIDER path. A
blindness row aimed at the wrong reader is a miss, not a refutation. Same shape as
mem-1785541129-e6f7's false NBSP row: the harness contradicted a unit-level trace, and that is what
located the error.

**WHOLE-TASK FIDELITY.** The task's acceptance is the twins' `rule` clause asked of every twin in
both providers, plus S1 (`plex-web.service`). Round 4 answered `rule` at four seams, round 5
answered `service` at four sites plus the shared reader's seven other keys, and the review's
task-exemplars battery has all five recorded `PASS: 41/41` states RED with the twin named and R3,
the task's negative control, still reddening. The plan's Test Requirements are met in full: gate
exits 0, each new row RED under a reproducible mutation of the REAL files reverted in a `finally`
with sha asserted at both ends, controls GREEN, anti-vacuity present (floor + printed count), no
live call, no `just play`, no vault value, no commit, gates 1b/2b/3b/4d untouched.

**NOT LOOP_COMPLETE, AND THE STEP IS NOT EXHAUSTED.** Step 5's wave is FOUR: 5a, 5b and 5c are
closed; **5d `task-1785524605-ea55` is open and unblocked** and is the row after this one. Behind it
sit the six Family-B/C deferrals whose blockers name 5c — the Planner re-prices them at this close,
as this plan says in writing. Four operator gates (1b/2b/3b/4d) remain and none is agent-closable.

**WHAT I DID NOT DO.** No source file edited — guard and both templates byte-identical at both ends
of both harnesses; no commit, HEAD `7e9c426`; no `just play`, no live call against the real homelab,
no vault value; no other hat's evidence edited or deleted; no task created or failed. One task
closed: `task-1785441840-e8eb`. Files added: `logs/finalizer-step05c-{new-twin,f0-loudness}.py` +
their `.log`s. No containers started (the compose parser needs none). → `queue.advance`.

## 2026-08-01 — Builder, Step 5d (task-1785524605-ea55) — BUILT, `review.ready`

**THE ROW EXISTS AND THE HOLE IS CLOSED.** `test_pve_dashboard_declares_the_container_drop_down`
in `scripts/test_grafana_provisioning_shape.py`. Guard **PASS 21/21** (20 → 21, the count the task
predicts), `just test` **GATE PASS 36/36 rc=0** (`logs/gate-step05d.log`), guard `bb50f24e`,
dashboards `a8a8c24e`/`1e8f3617`/`fde25673` and `tasks/main.yml` `71e88a89` byte-identical at both
ends of every harness. HEAD still `7e9c426`, no commit.

**RED FIRST, AND THE VERDICT WAS `ABSENT` RATHER THAN GREEN.**
`logs/red-step05d-pve-dropdown-PRE.log` — the battery run against the guard as 5b left it
(`df94b58c`) scores **0/22**: the row's marker is nowhere in the output, on every row. The same
battery against the row **23/23** (`logs/red-step05d-pve-dropdown.log`). The PRE run predates F2,
which was added after F1's first exemplar turned out to be refused for a different reason than the
one written beside it — see below; every row in it, F1 included, was ABSENT.

**EVERY ROW IS SCORED ON BOTH ROWS AT ONCE, because that is the claim.** A mutation that reddens
5a's declared-variable row proves nothing here. The decisive pairs are the ones where **5a is GREEN
and the drop-down is gone**: B1 (the task's own C1 — `templating.list` emptied AND the thirteen
`$guest` rewritten to the literal `lxc/110`, with another dashboard carrying one ordinary variable),
B2 (the declaration kept, the references literal — 5a's DELETE direction is deliberately not a
failure), B4 (`{node="$guest"}` — every reference declared, matched against a label no series
carries), C1-C5 (the query that no longer yields the containers), D1/D2 (the identity pin matching
nothing), E1/E2 (one panel of thirteen pinned literally). Eight GREEN controls, including AC (b)'s
added dashboard that declares nothing, a CONSISTENT rename (`guest` → `ct` on both sides — the name
is not the contract), a rewritten query admitting the same containers, and the three NODE panels,
which admit no container and are not asked to name the drop-down.

**ONE CORRECTION THE TASK'S OWN C1 NEEDED, MEASURED RATHER THAN CARRIED.** The task says the C1
companion is "give `grafana-plex-health-dashboard.json` one ordinary custom variable". That is one
word short: 5a's floor counts REFERENCES, so a declared-and-unused variable leaves `checked` at 0
and 5a reddens on its own anti-vacuity clause instead — which would have made B1 prove nothing.
The battery declares AND uses it (a `repeat` clause, the one carrier needing no expression edited),
and says so in `plex_gains_a_variable`'s docstring.

**THE FIRST CLAUSE IS MEASURED AGAINST THE ENGINE, NOT READ OFF THE DOCUMENTATION.**
`logs/calibration-step05d-label-values.py` / `.log` — **11/11**, `prom/prometheus:v3.12.0`, offline,
container removed in a `finally`. `label_values` is not PromQL: Grafana turns it into
`GET /api/v1/label/<label>/values?match[]=<selector>`, so that call is what was measured, on a
fixture carrying every `id` shape the exporter emits. The delivered query returns the containers and
ONLY the containers (A1-A3); the scope dropped returns the node, the VM and the storage beside them
(B1); the scope narrowed loses CT 111 (B2); the wrong label returns an EMPTY list (B3); an
undeclared family returns an empty list (B4). **PART C measures the harm** rather than asserting it:
`pve_up{id="$guest"}` unsubstituted selects NOTHING (C2) — not an error, not an empty drop-down, a
panel that is simply always blank, which is what B1/B2 deliver on thirteen targets at once.

**THE IDENTITY PIN IS WRITTEN DOWN, WHICH THE TASK ASKED FOR BY NAME (DEC-133).** The pin is the
dashboard's own `uid` `pve-overview`, not the `src:` and not the `dest:` — this file's own U2
measurement shows the FILE NAME is not identity, while the uid is what Grafana keys its store by and
what `tasks/main.yml` already documents as a contract. **When it matches nothing the row FAILS**,
naming the uid it looked for and listing what the inventory did hold: "no such dashboard" read as
"nothing to check" is the same vacuity failure one level up.

**TWO BOUNDS DECLARED IN THE DOCSTRING RATHER THAN LEFT TO BE FOUND.** (1) A drop-down over a
SYNTHESISED label is refused, and one spelling of that is a genuine FALSE REFUSAL: `label_values(
label_replace(pve_up, "n", "$0", "id", "lxc/.*"), n)` works — F1. Its near twin with `$1` yields the
bare `110` and every panel reading it is empty — F2. Two spellings one character apart, opposite
verdicts, nothing in the document distinguishing them, so the row says what it can see and the price
is on the record. (2) A matcher block this file cannot parse (`pve_up{$filter}`, the ordinary
Grafana idiom) is COUNTED on the printed line, not failed — `_promql_calls`' own docstring prices
reddening it as the wrong trade.

**WHAT I DID NOT DO.** No delivered artifact edited — the three dashboards and `tasks/main.yml` are
byte-identical to their pre-round shas; no commit; no `just play`, no live call against the real
homelab, no vault value; gates 1b/2b/3b/4d untouched; no other hat's evidence edited or deleted; no
task closed, failed or created. Files added: `scripts/` unchanged except the one guard file;
`logs/red-step05d-pve-dropdown.py` + `.log` + `-PRE.log`, `logs/calibration-step05d-label-values.py`
+ `.log`, `logs/gate-step05d.log`. One container started and removed, leftover check: none.

## 2026-08-01 — Builder, Step 5d REWORK round 2 (review.rejected F1 → `regex` and `hide`) — task-1785524605-ea55

**THE REVIEW WAS RIGHT AND ITS RATIONALE WAS MEASURED BEFORE IT WAS IMPLEMENTED.** Guard **PASS
21/21** (unchanged — no row added, so no count pin moved), `just test` **GATE PASS 36/36 rc=0**
(`logs/gate-step05d-rework-r2.log`), guard `bb50f24e` → `8a850a70`, delivered artifacts
byte-identical at both ends (`a8a8c24e` / `1e8f3617` / `fde25673`, tasks `71e88a89`), HEAD `7e9c426`,
no commit.

**RED FIRST, AND THE REVIEW'S OWN THREE ROWS ARE IN IT VERBATIM.**
`logs/red-step05d-rework-r2.py` / `-PRE.log` **14/22** against the guard as round 1 left it; the
eight misses are exactly the new-behaviour rows. Post-fix **22/22** (`-rework-r2.log`). Every case
mutates the DELIVERED `grafana-pve-dashboard.json` on disk, re-imports the guard and scores 5d AND
5a — because the claim is "5a stays GREEN and the Test Requirement is gone" — and every RED row
also pins WHICH clause spoke (`want_in`), so a row cannot pass for another refusal's reason. The
review's own battery, run verbatim and unedited, goes **20/24 → 23/24**.

**FOUR CLAIMS ASKED OF grafana/grafana:13.1.0 ITSELF, NOT OF THE REVIEW**
(`logs/calibration-step05d-rework-r2-regex-hide.py` / `.log`, **20/20**, sourcemap `sourcesContent`
out of the pinned image, offline, `--network=none`, nothing started):
- `regex` is compiled under JS truthiness, DROPS a non-matching value (`if (!matches.length)
  continue`) and REWRITES on a capture group (`text = value = firstMatch[1]`, and the named
  `value`/`text` groups likewise); `stringToJsRegex` anchors a bare string `^…$`. C1 and C2 confirmed.
- **`regexApplyTo` — the review's "mind it" — CANNOT make a live regex inert.** It chooses WHICH of
  text/value the pattern is tested against and nothing else; the single drop and every rewrite are
  downstream of both branches (R4). So the refusal is on `regex` alone and this reader never has to
  read `regexApplyTo`. Scored as D4.
- **`hide` is refused on ONE value, because refusing "not zero" is measured false.**
  `VariableValueSelectWrapper` returns null exactly on `hideVariable`; `hideLabel` (1) drops only
  the label and `inControlsMenu` (3) moves the control — both keep the picker (H3/H5, B4/B5). Both
  spellings of the refused value are covered: `2` and the v2 schema's `"hideVariable"` (D3).
- **AND ONE THE REVIEW DID NOT RAISE, CHECKED AND CLEARED.** `refresh: 0` looks like the same class
  (a saved `options` array standing in for the query's answer) and is not one here:
  `QueryVariable.getValueOptions` guards on the QUERY and never on `refresh`, and the only `refresh`
  test in the variable set is the time-range re-run (F1/F2). Stated as a bound, scored GREEN as B9.

**THE TWO REFUSALS ARE DELIBERATELY DIFFERENT SHAPES, AND THE FALSE SIDE OF EACH IS SCORED
(DEC-135).** `regex` is refused for the whole non-empty class — `regex: ".*"` is a genuine false
refusal and is scored as **D2** so the price is on the record, loud and one word to undo, with
widening to "a pattern that provably keeps both ids whole" additive. The value is NOT stripped
first: `" "` is truthy to Grafana and anchors to `/^ $/`, which empties the drop-down (**D1**).
`hide` is refused on the single enum value, per H5.

**FOUR REGRESSION ROWS PROVE THE NEW REFUSALS SHADOW NOTHING.** E1-E4 — the scope dropped, the
`custom` swap, the motivating templating-emptied defect, and one panel of thirteen literalised — are
all still RED for their ORIGINAL reasons with `regex`/`hide` clean. Round 1's own battery
`logs/red-step05d-pve-dropdown.py` still **23/23**, unedited.

**C4 IS FILED, NOT CODED — DEC-136.** The review named it "lower priority, NOT the rejection basis
(file or declare)"; it is now both. `task-1785553255-bad2`
(`…:guard:pve-panels-follow-a-second-variable`), plus a declared bound in the row's docstring so it
survives the task never being picked up. The ground for not coding it is the SHAPE of the fix, not
effort: refusing every `id` matcher that names a non-drop-down variable would forbid a legitimate
`$node` drop-down beside this one, so the honest rule is narrower ("a NON-`query` variable whose
LITERAL values admit a container") and needs a value-list reader this file does not have.

**WHAT I DID NOT DO.** One source file edited (`scripts/test_grafana_provisioning_shape.py`). No
delivered artifact edited, no template touched, no commit, no `just play`, no live call against the
homelab, no vault value; gates 1b/2b/3b/4d untouched; no task closed, failed or reopened; no other
hat's evidence edited or deleted — the review's battery ran verbatim. One task created
(`task-1785553255-bad2`, above). Files added: `logs/red-step05d-rework-r2.py` + `.log` + `-PRE.log`,
`logs/calibration-step05d-rework-r2-regex-hide.py` + `.log`, `logs/gate-step05d-rework-r2.log`. One
container started and removed by the calibration harness, leftover check: none.

## 2026-08-01 — Builder, Step 5d REWORK round 3 (`review.rejected` F1 → `includeAll`/`multi`)

Task `task-1785524605-ea55` / `code-assist:plex-monitoring:guard:pve-dashboard-declares-its-drop-down`.

**VERIFICATION.** Guard **PASS 21/21** (count unchanged — no row added), `just test`
**GATE PASS 36/36 rc=0** (`logs/gate-step05d-rework-r3.log`). Guard `8a850a70` → `1ee28f06`.
Delivered artifacts byte-identical at both ends: `grafana-pve-dashboard.json` `a8a8c24e`,
`grafana-plex-health-dashboard.json` `1e8f3617`, `grafana-homelab-dashboard.json` `fde25673`,
`tasks/main.yml` `71e88a89`. HEAD `7e9c426`, no commit.

**RED FIRST.** `logs/red-step05d-rework-r3.py` / `-PRE.log` **12/23** on the guard as round 2 left
it — the eleven MISSes exactly the new-behaviour rows — and **23/23** after
(`logs/red-step05d-rework-r3.log`). C1/C2/C3 are the review's own B1/B2/B3 verbatim. Every row pins
WHICH clause spoke (`want_in`).

**THE REVIEW'S OWN HARNESSES, RUN UNEDITED.** `logs/critic-step05d-r2-includeall.py` **14/17 →
17/17** (`…-r3recheck.log`); `logs/critic-step05d-battery.py` **23/24**, C4 the declared MISS
(`…-r3recheck.log`); round 2's `logs/red-step05d-rework-r2.py` **22/22**; round 1's
`logs/red-step05d-pve-dropdown.py` **23/23**.

**THE REPAIR IS THE RELATION, NOT THE KEY (DEC-137).** `_grafana_variable_alternates` reports which
of `includeAll`/`multi` a drop-down entry sets, under JS truthiness; clause 2's second half refuses
only when the matcher naming that drop-down carries an operator outside `PROMQL_REGEX_OPERATORS`.
No new reader: `_promql_matchers` already hands the loop `(name, op, value)`.

**WHAT MEASURING THE RATIONALE BOUGHT** (`logs/calibration-step05d-rework-r3-includeall.py`
**39/39**, sourcemaps out of `grafana/grafana:13.1.0` offline plus `prom/prometheus:v3.12.0`):
  1. **`!=` is the harm the review did not probe, and it is worse than `=`.**
     `{id!="(lxc/110|lxc/111)"}` returns EVERY series including the node (C3) — a per-container
     panel graphing the whole cluster, never empty and always wrong — while `!~` stays coherent
     (C4). The split is literal-vs-regex, not positive-vs-negative.
  2. **`multi` does NOT break on load.** `interpolateQueryExpr` returns `escapedValues[0]` for a
     single selection (A6), so one ticked container interpolates the bare id exactly as today (C5).
     It is refused for the operator's SECOND tick — one click, no file edited — and that price is
     declared as D3 rather than left implicit.
  3. **The Python predicate IS the JS gate, measured against node.** `isMulti: variable.multi` is
     passed through RAW, not `Boolean()`-wrapped (A2), so all twelve JSON scalars were run through
     `!(!x)` in node and through `GRAFANA_FALSY_VALUES` (B1-B12): they agree. `multi: "false"` is a
     TRUE flag to Grafana (D5 of the RED harness) and `multi: 0` is not one (E5).

**THE ROUND'S SCOPE IS THE CARRIER, NOT THE KEY (DEC-138).** Three reviews in a row found a defect
in an unexamined key of the same entry. All fourteen delivered keys — not the twelve two reviews
called it (D0) — are now priced: `sort` reorders and cannot filter (D1), `options` is overwritten
from the query on load (D2), `allValue` is reachable only through `includeAll` (D3), `label` is the
picker's caption (D4), `current` falls through when it matches nothing (D5), and `datasource` is
already a carrier for this file's uid and type rows. The result is
`GRAFANA_PVE_DROP_DOWN_KEYS_PRICED`, and the row PRINTS any delivered key outside it — printed and
not failed, because Grafana adds variable fields between releases.

**ONE INERT REFACTOR, PROVEN RATHER THAN ASSERTED.** The two pre-existing `op in ("=~", "!~")` sites
now read `op in PROMQL_REGEX_OPERATORS`. `logs/inert-step05d-rework-r3-operator-constant.log`
**7/7**: identical answers for every operator the tokeniser can produce and three it cannot.

**WHAT I DID NOT DO.** One source file edited (`scripts/test_grafana_provisioning_shape.py`). No
delivered artifact or template touched, no commit, no `just play`, no live call against the
homelab, no vault value; gates 1b/2b/3b/4d untouched; no task closed, failed, created or reopened;
no other hat's evidence edited or deleted — all four prior harnesses ran verbatim, their re-runs
written to new `-r3recheck` logs. Files added: `logs/red-step05d-rework-r3.py` + `.log` +
`-PRE.log`, `logs/calibration-step05d-rework-r3-includeall.py` + `.log`,
`logs/gate-step05d-rework-r3.log`, `logs/inert-step05d-rework-r3-operator-constant.log`, the two
`-r3recheck.log` files. Containers started and removed in a `finally`, extracted sourcemaps
deleted, leftover: none.

## 2026-08-01 — Step 5d REWORK round 4 (task-1785524605-ea55) — BUILT

Active task: `code-assist:plex-monitoring:guard:pve-dashboard-declares-its-drop-down`, triggered by
`review.rejected` (round 4) with F1 `allValue`, F2 the `repeat` false refusal, F3 a docstring
pointer to a name nothing defines.

**Verification run this round**
- `just test` → **GATE PASS 36/36 rc=0** (`logs/gate-step05d-rework-r4.log`); guard **PASS 21/21**
  (row count unchanged — two clauses, no new row).
- RED first: `logs/red-step05d-rework-r4.py` / `-PRE.log` **18/28** on the guard as round 3 left
  it, the ten MISSes exactly the new-behaviour rows; **28/28** after (`.log`).
- Measurement of record: `logs/calibration-step05d-rework-r4-allvalue.py` / `.log` **28/28**
  (grafana/grafana:13.1.0 sourcesContent offline `--network=none`, node against the bundle's own
  escape class, `prom/prometheus:v3.12.0` on the round's fixture).
- Prior harnesses run VERBATIM into `-r4recheck.log`: `red-step05d-rework-r3` **23/23**,
  `red-step05d-rework-r2` **22/22**, `red-step05d-pve-dropdown` **23/23**,
  `critic-step05d-battery` **23/24** (C4 the declared MISS), `critic-step05d-r2-includeall`
  **17/17**, `critic-step05d-r3-allvalue` **19/20** — the one MISS is the review's own B5, which
  scores `allValue` without `includeAll` as GREEN/"unreachable"; calibration A5/A6/A14/A15 is the
  disagreement, and it agrees with that review's own repair sentence ("refused wherever it is
  named").
- Refactor proven inert: `logs/inert-step05d-rework-r4-guard-flip.py` / `.log` **14/14** (the De
  Morgan flip of round 3's guard clause, over every operator the tokeniser produces and three it
  cannot, crossed with both membership answers).
- Delivered artifacts byte-identical at both ends: `a8a8c24e` (pve), `1e8f3617` (plex-health),
  `fde25673` (homelab), `tasks/main.yml` `71e88a89`. Guard `1ee28f06` → `5f0820a2`. HEAD `7e9c426`,
  no commit.

**What changed** — one source file, `scripts/test_grafana_provisioning_shape.py`:
`GRAFANA_VARIABLE_ALL_VALUE_KEY` with the measured chain, `_grafana_variable_all_value` and
`_panel_repeats_over` beside `_grafana_variable_alternates`, both wired into clause 2's existing
matcher walk; `allValue` re-priced in `GRAFANA_PVE_DROP_DOWN_KEYS_PRICED` against the shape that
SHIPPED; F3's dangling `GRAFANA_PVE_VARIABLE_KEYS_READ` pointer corrected. DEC-139, DEC-140.

No delivered artifact or template touched, no commit, no `just play`, no live call, no vault value;
gates 1b/2b/3b/4d untouched; no task closed, failed, created or reopened; no other hat's evidence
edited. Containers started and removed in a `finally`, extracted sourcemaps deleted, leftover: none.

## 2026-08-01 — Step 5d REWORK round 5 (`task-1785524605-ea55`) — review F1: the EXPANDED repeating row

- **Verification:** guard **PASS 21/21** (no row added), `just test` **GATE PASS 36/36 rc=0**
  (`logs/gate-step05d-rework-r5.log`).
- RED first: `logs/red-step05d-rework-r5.py` / `-PRE.log` **17/23** on the guard as round 4 left it
  — the six MISSes are exactly A1/A2/B6/B8/B9/B13, the new-behaviour rows, and every false-side row
  already passed — then **23/23** (`.log`) after the change. A1-A4 are the review's own A1-A4
  verbatim; every row pins WHICH clause spoke.
- Prior harnesses re-run UNEDITED into `-r5recheck` logs: `red-r4` **28/28**, `red-r3` **23/23**,
  `red-r2` **22/22**, `red-step05d-pve-dropdown` **23/23**, `critic-step05d-battery` **23/24** (C4
  the declared MISS, filed as `task-1785553255-bad2`), `critic-r2-includeall` **17/17**,
  `critic-r3-allvalue` **19/20** (B5, the disagreement round 4 declared and the review did not
  hold), `inert-r4-guard-flip` **14/14**, and the review's row-repeat calibration
  `critic-step05d-r4-rowrepeat-calib` **12/12** (offline, `--network=none`, sourcemaps removed in
  its own `finally`). The review's own `critic-step05d-r4-repeat` is now **11/11**, up from the
  9/11 that was the rejection basis.
- **What changed** — one source file, `scripts/test_grafana_provisioning_shape.py`:
  `GRAFANA_ROW_PANEL_TYPE` / `GRAFANA_ROW_COLLAPSED_KEY` carrying the four measured links,
  `_grafana_row_span`, a third member on `_dashboard_repeat_clauses`' tuples, and
  `_panel_repeats_over` testing the set. F2's two stale citations corrected: the guard's
  `allValue` calibration is **28/28**, not "25/26 with B5 the declared MISS" (that count is
  `logs/critic-step05d-r3-allvalue.py`'s 19/20), fixed here and in `logs/red-step05d-rework-r4.py`'s
  module docstring. DEC-141.
- Delivered artifacts byte-identical at both ends: `a8a8c24e` (pve), `1e8f3617` (plex-health),
  `tasks/main.yml` `71e88a89`. Guard `5f0820a2` → `a90acb79`. HEAD `7e9c426`, no commit.
- No delivered artifact or template touched, no commit, no `just play`, no live call, no vault
  value; gates 1b/2b/3b/4d untouched; no task closed, failed, created or reopened; no other hat's
  evidence edited (F2's second citation is my own round-4 harness's module docstring, prose only —
  it re-ran 28/28 after the edit).

## 2026-08-01 — Step 5d REWORK round 6 (`task-1785524605-ea55`) — review F1: the span is over the ARRAY, Grafana's membership is over the GRIDPOS SORT

- **Verification:** guard **PASS 21/21** (no row added), `just test` **GATE PASS 36/36 rc=0**
  (`logs/gate-step05d-rework-r6.log`).
- RED first: `logs/red-step05d-rework-r6.py` / `-PRE.log` **26/31** on the guard as round 5 left it
  — the five MISSes are exactly A3/A4/A5 (the review's own B3/B4/B5) and C1/C2 (the measured
  gridPos default), and every false-side row already passed — then **31/31** (`.log`) after the
  change. The review's own `critic-step05d-r5-gridpos.py`, re-run UNEDITED, goes **9/12 →  12/12**
  (`-r6PRE.log` / `-r6recheck.log`).
- Calibration: `logs/calibration-step05d-rework-r6-gridpos.py` / `.log` **11/11**, offline
  (`--network=none`, nothing started, sourcemaps removed in a `finally`) — P1/P2/P5 every
  `panels[]` entry becomes a `PanelModel` in the same constructor, before the sort; P3/P4 those
  defaults are `defaultsDeep(this, cloneDeep({gridPos: {x:0,y:0,h:3,w:6}, …}))`, so a missing OR
  PARTIAL `gridPos` sorts as (0,0); S1-S6 against node itself — the sort is stable, and a
  non-numeric axis reaches the comparator as NaN, which SortCompare turns into "equal to
  everything" rather than a place, which is why an unreadable position withholds the span.
- Prior harnesses re-run UNEDITED into `-r6recheck` logs: `red-r5` **23/23**, `red-r4` **28/28**,
  `red-r3` **23/23**, `red-r2` **22/22**, `red-step05d-pve-dropdown` **23/23**,
  `critic-step05d-battery` **23/24** (C4 the declared MISS, `task-1785553255-bad2`),
  `critic-r2-includeall` **17/17**, `critic-r3-allvalue` **19/20** (B5, the declared
  disagreement), `critic-r4-repeat` **11/11**, `inert-r4-guard-flip` **14/14**.
- **What changed** — one source file, `scripts/test_grafana_provisioning_shape.py`:
  `GRAFANA_PANEL_POSITION_KEY` / `_AXES` / `_DEFAULT` and `GRAFANA_SORTED_PANEL_LIST_PATH` with the
  measured chain, `_grafana_panel_position` and `_grafana_panel_order` beside `_grafana_row_span`,
  which now walks that order and emits ORIGINAL indices. The fifth bound is stated in its docstring
  and in `_panel_repeats_over`'s. DEC-142.
- Delivered artifacts byte-identical at both ends: `a8a8c24e` (pve), `1e8f3617` (plex-health),
  `tasks/main.yml` `71e88a89`. Guard `a90acb79` → `a93e1511`. HEAD `7e9c426`, no commit.
- No delivered artifact or template touched, no commit, no `just play`, no live call, no vault
  value; gates 1b/2b/3b/4d untouched; no task closed, failed, created or reopened; no other hat's
  evidence edited.

### 2026-08-01 — Step 5d REWORK round 7 (`task-1785524605-ea55`) — `review.rejected` F1 → THE AXIS TEST

- Active task `task-1785524605-ea55` / `code-assist:plex-monitoring:guard:pve-dashboard-declares-
  its-drop-down`. Verification: `just test` **GATE PASS 36/36 rc=0**
  (`logs/gate-step05d-rework-r7.log`), guard **PASS 21/21** (count unchanged, no row added).
- **RED first.** `logs/red-step05d-rework-r7.py` / `-PRE.log` **15/20** on the guard as round 6 left
  it — the five MISSes are exactly the new-behaviour rows (A1/A2 boolean, A5 `gridPos: null`, A6 the
  double, B4 the priced `x` refusal) while every control in Part C and both already-refused
  spellings in A3/A4 passed, so the harness is aimed before the change. **20/20** after
  (`.log`).
- Calibration: `logs/calibration-step05d-rework-r7-axis.py` / `.log` **21/21**, offline
  (`--network=none`, nothing started, sourcemaps and the extracted lodash removed in a `finally`).
  PART L runs **real lodash 4.18.1**, required out of the image's own sourcesContent, over
  PanelModel's own `defaults`: an absent or partial `gridPos` is filled to the origin, a WRITTEN
  null is not (and the comparator reading `.y` off it THROWS), a primitive `gridPos` reads NaN and
  an ARRAY reads the ORIGIN. PART C puts every JSON spelling of an axis through the comparator:
  `true`/`false`/`null`/`""`/`[]`/`"3"`/`[3]` all subtract to a number and none is `===` to it.
  PART T tests the review's own prescription and refutes it (T1) without denying its case (T4).
  PART N: the engine's axis is an IEEE double and Python's is an exact int.
- Differential: `logs/red-step05d-rework-r7-differential.py` / `.log` **7/7** — it IMPORTS the
  review's `logs/critic-step05d-r6-gridpos-differential.py` reference model rather than restating
  it, and re-fuzzes over the widened vocabulary: **1500 dashboards, ZERO false accepts**, every
  refusal explained by a value the guard declares unreadable, and zero divergence in BOTH directions
  once the vocabulary is numbers again.
- Prior harnesses re-run UNEDITED into `-r7recheck` logs: `red-r6` **31/31**, `red-r5` **23/23**,
  `red-r4` **28/28**, `red-r3` **23/23**, `red-r2` **22/22**, `pve-dropdown` **23/23**,
  `critic-step05d-battery` **23/24** (C4 the declared MISS, `task-1785553255-bad2`),
  `critic-r2-includeall` **17/17**, `critic-r3-allvalue` **19/20** (B5 the declared disagreement),
  `critic-r4-repeat` **11/11**, `critic-r5-gridpos` **12/12**, r6 calibration **11/11**,
  `inert-r4-guard-flip` **14/14**. The review's own two: `critic-r6-gridpos-differential`
  **10/13 → 11/13** (D2, the rejection basis, is FIXED; C4 and D1 are the priced-refusal rows this
  round declares a measured disagreement with — see DEC-143) and `critic-r6-e2e-boolean-axis`
  **4/5** (B1, the false accept, FIXED; C1 is that same declared disagreement).
- **What changed** — one source file, `scripts/test_grafana_provisioning_shape.py`: a new
  `_grafana_axis_double`, `_grafana_panel_position` testing membership with `in` instead of `.get`,
  and the measurement written into `GRAFANA_PANEL_POSITION_KEY`'s block and `_grafana_row_span`'s
  docstring. DEC-143.
- Delivered artifacts byte-identical at both ends: `a8a8c24e` (pve), `1e8f3617` (plex-health),
  `tasks/main.yml` `71e88a89`. Guard `a93e1511` → `b3729aad`. HEAD `7e9c426`, no commit.
- No delivered artifact or template touched, no commit, no `just play`, no live call, no vault
  value; gates 1b/2b/3b/4d untouched; no task closed, failed, created or reopened; no other hat's
  evidence edited.

## Step 5d REWORK round 8 — Builder (task-1785524605-ea55), `review.rejected` F1 → THE PARSE LAYER

- **The review is right, and the class is two spellings wider than its repair sentence.** A
  delivered dashboard meets Go's `encoding/json` (Grafana's provisioner) before any browser, and Go
  is strictly narrower than Python's `json` at both ends the review named. Its prescription —
  `parse_constant` for the three bare tokens, plus "the overflow half is the `OverflowError`
  already caught" — covers the INT spelling of the overflow only: `1e400` is the same value,
  `json.loads` turns it into `float('inf')` with no exception raised at all, and it was a place.
- **Calibration** `logs/calibration-step05d-rework-r8-number-range.py` / `.log` **18/18**, on the
  pinned `grafana/grafana:13.1.0` over its own HTTP API with the repo's own file-provider shape:
  `1`+400 zeros and `1e400` are the same 404 (B2); sign and distance past the maximum do not
  rescue it (B3); `1.7976931348623157e308`, `9007199254740993` and a denormal all provision 200
  (B4); the same literal in `fieldConfig.defaults.min` kills the same file (B6).
  **B5 CORRECTED MY OWN HYPOTHESIS BEFORE THE CODE WAS WRITTEN:** `1e-400` is a
  `strconv.ParseFloat` range error in exactly the way `1e400` is, and the engine LOADS it — so the
  class is ONE-SIDED and my first detector, written by symmetry, would have refused a working
  dashboard. Scored, and held by A7/B6 of the battery.
- **RED first.** `logs/red-step05d-rework-r8.py` / `-PRE.log` **13/32** on the guard as round 7
  left it — every miss a new-behaviour row (A2-A6/A9, B3-B5, C2-C4, D1/D2/D4, E1-E4) and every
  control green. **32/32** after. B5 was re-aimed mid-run: at `+1e400` the row is already RED
  because an infinity sorts LAST, which is the right colour for the wrong reason.
- **The repair is at the parse layer, in the idiom the file already has.**
  `_grafana_provisionable_json` + `GrafanaUnprovisionableJSON`, called by the FIVE readers of a
  delivered dashboard, all of which already handled an unreadable delivery — no new error path,
  one shared rule. `_grafana_axis_double` no longer converts anything non-finite into a place, and
  the constant block's N3/N4 bullet now states the rule the code implements.
- **The sixth `json.loads` is deliberately left lenient and scored.** `_dashboard_sources_on_disk`
  is DISCOVERY, not delivery: narrowing it would hide an undelivered broken dashboard from
  `test_dashboard_delivery_inventory_is_complete` instead of reporting it (F1/F2). E2 carries the
  AST sweep as a LIVE row with that one carve-out declared, and E4 proves a sixth reader written
  the old way fails it.
- **Blast radius closed:** an unprovisionable file now reddens 10 of the 21 rows (C2/C3/C4),
  where the review measured the whole guard staying green (its D2/D3).
- **The review's own battery drops 23/23 → 12/23, and the drop is PROVEN, not narrated.**
  `logs/red-step05d-rework-r8-critic-recheck.py` / `.log` **9/9**: the misses are EXACTLY the
  eleven defect-encoding rows (R2), all five ENGINE rows and every anchor/control still score
  (R3/R4), and a mechanical inverse edit rebuilds the reviewed guard to the sha it was handed off
  as — `b3729aad` (V1) — where the same battery is back to **23/23** (V3/V4). No byte of the
  review's evidence edited.
- **Prior harnesses re-run UNEDITED into `-r8recheck` logs, all at their declared numbers:**
  `red-r7` **20/20**, `red-r7-differential` **7/7**, `red-r6` **31/31**, `red-r5` **23/23**,
  `pve-dropdown` **23/23**, `critic-step05d-battery` **23/24**, `critic-r2-includeall` **17/17**,
  `critic-r3-allvalue` **19/20**, `critic-r4-repeat` **11/11**, `critic-r5-gridpos` **12/12**,
  `critic-r6-gridpos-differential` **11/13**, `critic-r6-e2e-boolean-axis` **4/5**.
- **Verification:** guard **PASS 21/21** (no row added — this is a reader, not a claim),
  `just test` **GATE PASS 36/36 rc=0** (`logs/gate-step05d-rework-r8.log`).
- Guard `b3729aad` → `d1f33db2`. Delivered artifacts byte-identical: `a8a8c24e` (pve),
  `1e8f3617` (plex-health), `tasks/main.yml` `71e88a89`. HEAD `7e9c426`, no commit.
- One source file edited. No delivered artifact or template touched, no `just play`, no live call,
  no vault value; gates 1b/2b/3b/4d untouched; no task closed, failed, created or reopened; no
  other hat's evidence edited. One `--rm` Grafana container per calibration run, removed in a
  `finally`, tmpdirs deleted, leftover: none.

### Step 5d rework round 9 — the SAVE layer's `uid` rule (task-1785524605-ea55)

- **Event:** `review.rejected` (round 9). F1: round 8 modelled the PARSE and the review's class is
  the SAVE — four delivered files Go's `encoding/json` reads perfectly (uid of 41 chars, uid with
  a space / a slash / a dot) are refused by the provisioner's own save-time validation with the
  guard GREEN 21/21. Repair site named by the review: beside the `uid`/`title` truthiness test in
  `test_delivered_dashboards_parse_as_dashboards`, NOT inside `_grafana_provisionable_json`.
- **Change:** `_grafana_short_uid_defect` + its measured constant block, called from that row.
  One source file edited (the guard). DEC-145.
- **The rule is MEASURED, because the review asked not to be inherited from:**
  `logs/calibration-step05d-rework-r9-uid-charset.py` / `.log` **31/31** — pinned
  `grafana/grafana:13.1.0` over its own HTTP API with the repo's own file-provider shape, **121
  delivered dashboards in ONE provisioning run**. The accepted charset is EXACTLY `[A-Za-z0-9_-]`
  (64 in / 40 out over every printable ASCII char plus tab/CR/LF and a unicode sample, row A1); the
  length steps at 40 (B1/B2/B39/B40 save, B41/B42/B64/B128 do not); and PART E scores the guard's
  own predicate against all 114 string rows with **zero disagreements**.
- **A third outcome neither the review nor round 8 names:** a NON-STRING uid is not refused —
  Grafana generates a uuid and SAVES the dashboard under it (C2), so the file is at an address
  nothing in the repo can name. The string `"42"` stays an ordinary legal uid (C1).
- **RED first:** `logs/red-step05d-rework-r9.py` / `-PRE.log` **11/22** → **22/22**. Every miss a
  new-behaviour row; controls A1/A2 and accept-side E1-E6 green before and after; each D/N row
  requires the FAIL to come from the row that reads the field AND to name the uid.
- **The review's own battery stays 15/16 and the miss MOVED, proven not narrated:**
  `logs/red-step05d-rework-r9-critic-recheck.py` / `.log` **17/17** — the inverse edit reconstructs
  the reviewed guard to `d1f33db2` (R1), where the battery scores its original 15/16 with C2 the
  deliberate RED (R2); against the delivered guard the only miss is C3, whose `want` IS the defect
  (R3/R3b/R3c); all ten ENGINE verdicts identical in both directions (R4a).
- **Prior harnesses re-run UNEDITED into `-r9recheck` logs, all at their declared numbers:**
  `red-r8` **32/32**, `calibration-r8-number-range` **18/18**, `critic-r7-nonfinite-token`
  **12/23**, `red-r7` **20/20**, `red-r7-differential` **7/7**, `red-r6` **31/31**, `red-r5`
  **23/23**, `pve-dropdown` **23/23**, `critic-step05d-battery` **23/24**, `critic-r2-includeall`
  **17/17**, `critic-r3-allvalue` **19/20**, `critic-r4-repeat` **11/11**, `critic-r5-gridpos`
  **12/12**, `critic-r6-gridpos-differential` **11/13**, `critic-r6-e2e-boolean-axis` **4/5**,
  `inert-r4-guard-flip` **14/14**. ONE moved: `red-r8-critic-recheck` 9/9 → **8/9**, the single miss
  being **V1, a sha pin** (it reconstructs the r7 guard by inverting r8's edit, and this round edits
  inside its span). `logs/red-step05d-rework-r9-retired-recheck.py` **10/10** proves that
  mechanical: **9/9** at the reconstructed r8 guard (T2), V1 the only miss at the delivered guard
  (T3), every behavioural row green in BOTH directions (T4).
- **INCIDENT, declared (DEC-146):** two 04b harnesses (`rework-step04b-r4-inventory-content.py` I3,
  `-r5-subdir-and-keys.py` R8) author an undelivered dashboard at the literal path Step 4c now
  delivers and `unlink()` it, then crash before restoring. They destroyed
  `grafana-plex-health-dashboard.json`; it is UNTRACKED so git could not check it out. Recovered
  **byte-identical** (`1e8f3617`) from blob `3db468df` by sweeping all 4108 git objects for its
  sha256, and every harness scored against the broken tree was re-run afterwards and is back at its
  declared number. The hazard is now asserted statically (retired-recheck PART S, S1-S4) so the next
  hat does not repeat it. Those harnesses were NOT edited.
- **Verification:** guard **PASS 21/21** (no row added — a predicate, not a claim), `just test`
  **GATE PASS 36/36 rc=0** (`logs/gate-step05d-rework-r9.log`).
- Guard `d1f33db2` → `10fd3cdb`. Delivered artifacts byte-identical: `a8a8c24e` (pve), `1e8f3617`
  (plex-health), `fde25673` (homelab), `tasks/main.yml` `71e88a89`. HEAD `7e9c426`, no commit.
- No delivered artifact or template changed, no `just play`, no live call, no vault value; gates
  1b/2b/3b/4d untouched; no task closed, failed, created or reopened; no other hat's evidence
  edited. Grafana containers `--rm` and removed in a `finally`, tmpdirs deleted, leftover: none.

### Step 5d REWORK round 10 (task-1785524605-ea55) — `review.rejected` F1 → THE `title` HALF
- **The finding, reproduced:** the row promises "a uid + title THE PROVISIONER SAVES" and the
  `title` half was `not doc.get("title")` — Python truthiness. `logs/red-step05d-rework-r10.py`
  scores the guard as handed to me at **29/48**: nineteen delivered files the pinned engine
  refuses to save, every one GREEN.
- **Measured, not inherited — and the measurement refuted the review's own two bounds and
  found a third field.** `logs/calibration-step05d-rework-r10-title.py` (88/94, the six REDs
  being the refutations) and `-title-class.py` (**72/72**, 535 delivered files in one
  provisioning run on the pinned `grafana/grafana:13.1.0`):
  - the trim's class is Go's `unicode.White_Space` **plus U+FEFF** — 26 codepoints, settled by
    delivering every Cc/Cf/Zs/Zl/Zp codepoint in Unicode alone and again wrapped around a real
    title. `str.strip()` **crosses** it: wider by U+001C…U+001F (a false refusal four ways),
    narrower by U+FEFF (a fail-open). The review's `not title.strip()` is wrong in BOTH
    directions.
  - the 5000 is counted in **UTF-8 BYTES**, whatever the message says: 2500 two-byte characters
    save and 2501 do not; 1250 four-byte save and 1251 do not. `len(title) > 5000` in Python is
    a false accept on every multi-byte title between 5001 bytes and 5000 characters.
  - and the count is taken AFTER the trim; a non-string title is `""` to `MustString()` and
    lands on `Dashboard title cannot be empty`, not on a type error.
  - **the ninth key of the same carrier:** a `tags` member over 50 UTF-8 bytes refuses the whole
    file (`dashboard tag too long`). The other eight top-level keys were priced and all save.
- **The repair:** `_grafana_title_defect` and `_grafana_tags_defect` beside
  `_grafana_short_uid_defect`, in the row that reads the fields — the site the review names.
  The empty/absent title still fails through the OLD truthiness clause and its OLD message, so
  the four harnesses and the review's own D2 that read that string keep passing (red rows S1-S4).
- **Verification:** guard **PASS 21/21** (predicates, not a new row), `just test`
  **GATE PASS 36/36 rc=0** (`logs/gate-step05d-rework-r10.log`), red harness **29/48 → 48/48**,
  the review's own battery **60/61 → 61/61** with C1 (the finding) now green.
  `logs/red-step05d-rework-r10-critic-recheck.py` **9/9** rebuilds the reviewed bytes by a
  mechanical inverse edit to their declared sha `10fd3cdb`, re-scores the battery there at
  60/61, and shows all 33 PART A engine verdicts identical in both directions.
- Guard `10fd3cdb` → `3737ab86`. Delivered artifacts byte-identical: `a8a8c24e` (pve),
  `1e8f3617` (plex-health), `fde25673` (homelab), `tasks/main.yml` `71e88a89`. HEAD `7e9c426`,
  no commit.
- One casualty, declared (DEC-149): `logs/red-step05d-rework-r9-critic-recheck.py` and the
  `-retired-recheck.py` that imports its `reconstruct()` stop at a source anchor that spans the
  exact lines the review asked me to edit. NOT edited; the other seven r9-era batteries re-run
  byte-identically (`-r10recheck.log` beside each `-r9recheck.log`).
- No delivered artifact or template changed, no `just play`, no live call, no vault value; gates
  1b/2b/3b/4d untouched; no task closed, failed, created or reopened. Grafana containers `--rm`
  and removed in a `finally`, tmpdirs deleted, leftover: none.

### Step 5d rework round 11 (task-1785524605-ea55) — the STRING THE HOST LANGUAGE CANNOT ENCODE
- **The finding, reproduced RED-first:** both predicates round 10 added end in
  `len(….encode("utf-8"))`, and that call RAISES on a lone surrogate — which a delivered
  `.json` carries in pure ASCII (`"title": "A\ud800B"`). `logs/red-step05d-rework-r11.py`
  scores the guard as handed to me at **26/43**: thirteen delivered files the pinned engine
  handles fine kill the guard mid-row (no verdict, no summary line), and four more rows say
  the class is unanswered.
- **Measured, not inherited.** The r10 review handed over the arithmetic and said it need
  not be re-measured; the review's sentence settles the COUNT and not the other two things
  the repair decides, so `logs/calibration-step05d-rework-r11-surrogate.py` **38/38** asked
  the pinned `grafana/grafana:13.1.0` directly (19 delivered files, one provisioning run,
  stored titles read back over the HTTP API):
  - the replacement is **per codepoint** and U+FFFD is **3 bytes** — `A\ud800B` is stored
    `'A�B'`, two adjacent lone surrogates store as TWO U+FFFDs, 4997+one saves at 5000 and
    4998+one is refused at 5001, 4985+FIVE saves and 4986+five does not;
  - the SAME arithmetic at the other field: a tag of 47+one is 50 and saves, 48+one is 51
    and takes the whole file down, with 47 ASCII as the control;
  - it is **above the trim** and the trim does not move: a title that is only a lone
    surrogate stores `'�'` and SAVES, padded or wrapped in U+00A0/U+3000 it is trimmed
    around the replacement — no title changes its EMPTY verdict, only a length can move;
  - a title already carrying U+FFFD behaves identically (4997 saves, 4998 does not), so the
    model cannot invent a defect.
  - **and the engine refuted my own case list**: a HIGH escape followed by a LOW one is a
    PAIR to Go and to `json.loads` alike (stored `'A\U00010000B'`), so adjacency is not the
    class — PAIRING is, which is why the substitution is per code point.
- **The repair:** `_grafana_saved_text` beside the two constants, and the trim and both
  byte counts taken on its output. It is deliberately NOT in the shared loader (DEC-150) —
  a surrogate elsewhere carries no rule at the engine, and a loader-wide substitution would
  change what every other row compares with nothing measured behind it.
- **The bound is LIVE, not declared:** red rows Y1/Y2 sweep the guard's own AST and require
  every `.encode(` RECEIVER to be derived from `_grafana_saved_text`, with the sweep proven
  able to speak by bolting a third site into an in-memory copy; Y3-Y5 ask both predicates
  in process. W1-W6 hold the "did the crash move one field over?" question open by putting
  a surrogate in six other slots of a delivered dashboard.
- **Verification:** guard **PASS 21/21** (no new row), `just test` **GATE PASS 36/36 rc=0**
  (`logs/gate-step05d-rework-r11.log`), red harness **26/43 → 43/43**, the review's own
  surrogate battery **34/37 → 37/37**.
  `logs/red-step05d-rework-r11-critic-recheck.py` **9/9**: R1 rebuilds the reviewed bytes by
  a mechanical inverse edit to their declared sha `3737ab86a7e5…`, R2/R3 re-score the review's
  battery 34/37 there and 37/37 here, R4 shows all 17 ENGINE rows identical in both
  directions, R5 prices the one casualty both ways, R7 keeps round 10's red harness at 48/48
  in BOTH directions and R8 keeps round 10's own critic-recheck at 9/9.
- One casualty, declared and NOT edited (DEC-151): `-surrogate-collateral.py`, whose whole
  subject is the crash, dies reading a traceback that is no longer there — 14/14 against the
  reconstruction, first failing row P2 against the delivered guard.
- Guard `3737ab86` → `e8d62f31`. Delivered artifacts byte-identical: `a8a8c24e` (pve),
  `1e8f3617` (plex-health), `fde25673` (homelab), `tasks/main.yml` `71e88a89`. HEAD `7e9c426`,
  no commit.
- No file under `ansible/` edited, no `just play`, no live call, no vault value; gates
  1b/2b/3b/4d untouched; no task closed, failed, created or reopened. Grafana container
  `--rm` and removed in a `finally`, tmpdirs deleted, leftover: none.

### Step 5d CLOSED 2026-08-01 (Finalizer, task-1785524605-ea55) — after 11 review rounds
- **Reproduced, not read off logs:** `just test` **GATE PASS 36/36 rc=0**
  (`logs/final-step05d-r11-gate.log`, run by me), guard **PASS 21/21**, guard sha `e8d62f31`,
  artifacts `a8a8c24e` (pve) / `1e8f3617` (plex-health), `tasks/main.yml` `71e88a89`,
  HEAD `7e9c426`, no commit. Every number the round and the review declared holds.
- **The Finalizer's own work went where no round went.** All eleven rounds asked the pinned
  engine what it **REFUSES** (a 5001-byte title, a 51-byte tag, a lone surrogate, a non-finite
  number, a long `uid`) — the save layer's reject side. But this row's claim is read off the
  BYTES ON DISK, and the operator at gate 4d meets what the engine **STORES**. If the engine
  dropped, defaulted or rewrote any key the row pins, all three clauses would be green about a
  field nobody ever sees, and 4d would fail in a browser with the repo-side gate at 21/21.
  `logs/finalizer-step05d-engine-stores-the-dropdown.py` **25/25**, pinned
  `grafana/grafana:13.1.0` booted OFFLINE against a tree assembled as the role delivers it
  (same three mounts, `:ro`, 0640 root:root under 0755 root-group dirs, image default 472:0):
  - **PART A (12/12) — the engine stores the declaration verbatim.** `pve-overview` is HELD
    (A1); exactly one `templating.list` entry (A2); stored `name` `guest` (A3), `type` `query`
    (A4), `definition` AND `query.query` both still `label_values(pve_up{id=~"lxc/.*"}, id)` —
    **the selector clause 1 measured is unrewritten** (A5/A6); `label` `Container`, the word
    the Test Requirement uses (A7); and the four keys clauses 1-2 refuse are kept as delivered
    — `hide` 0, `regex` `''`, `includeAll`/`multi` both `False`, `allValue` absent (A8-A11).
    All **13** `$guest` references survive the save layer (A12).
  - **PART B (4/4) — the engine is NOT a guard, which is this row's premise, now measured.**
    The three mutations the row exists to refuse were provisioned as their own dashboards and
    the engine **SAVED ALL THREE** without complaint: the drop-down deleted outright with the
    thirteen `$guest` frozen to `lxc/110` (B1), `hide: 2` (B2), `regex: "lxc/110"` (B3) — and
    B1 is stored exactly as authored, no drop-down at all, every panel pinned to one container
    (B4). A dashboard that renders clean and is wrong. Only the repo-side row stands there.
  - **PART C (9/9) — the guard's own direction at the REAL delivery path.** Control PASS 21/21
    rc=0 (C0); each of the same three mutations, written to the delivered file in place, is
    rc=1 with a `FAIL:` verdict naming the dashboard (C1/C2/C3) — and each **reaches a verdict
    line with no traceback** (C1v/C2v/C3v), which is r11's own property exercised at the
    delivery path rather than in a fixture. Restored byte-identically `a8a8c24e` (Z1) and green
    again (Z2).
- **The review's one filed finding is correctly a task and not a rejection** (`task-1785571102-579d`,
  `_read` is `read_text()` inside `except OSError`, so a delivered `.json` carrying a RAW invalid
  UTF-8 byte kills the gate with no verdict while the pinned engine SAVES it). Pre-existing,
  untouched, unintroduced by r11, and outside r11's scope (r10's F1, the two `.encode(` calls).
  Rounds 9/10/11 were each rejected for "the same class, one field over"; a fourth is a regress.
- **Queue-state artifact, not a review matter:** `blocked_by` on ea55 still listed
  `task-1785517907-a5ec`, which is `closed`. Closed on the evidence, as the Critic flagged.
- **STEP 5's FOUR-ROW WAVE IS NOW EXHAUSTED** (5a, 5b, 5c, 5d all closed). What remains under
  this objective: the six Family-B guard deferrals + the three filed since, and the operator
  gates (1b, 2b, 3b, 4d). No agent-side row of Step 5 is left.
- No file under `ansible/` or `scripts/` edited (the in-place mutations are restored and
  re-verified), no commit, no `just play`, no live call, no vault value; gates 1b/2b/3b/4d
  untouched. Container `--rm` and removed in `__exit__`, tmpdirs deleted, leftover: none.

## 2026-08-01 — Builder, iteration 88 (`tasks.ready`, EMPTY payload) — NO TASK TO BUILD, `build.blocked`

- **The event carries no `task_id` and no `task_key`.** The previous iteration was the Planner's
  Step 5 close, which emitted **no event** by design (DEC-153: Step 5 exhausted, no Step 6 cut,
  every remaining row priced and deferred with reasons). A `tasks.ready` with an empty payload
  after a deliberate no-event is the runner's default topic, **not a routing decision** — no hat
  selected a row, and the Builder contract is to implement the task *from the payload*.
- **Verified rather than read off the Finalizer's log:** `just test` **GATE PASS 36/36 rc=0**
  (`logs/builder-it88-gate.log`, run by me), HEAD `7e9c426`, no commit. Nothing is broken and no
  repair is implied by the tree's state.
- **The queue's 12 ready rows were priced one iteration ago and none is mine to take.** The P1
  (`task-1785442499-1851`, Step 4d) is **OPERATOR ONLY, not agent-closable**. The other eleven are
  the six Family-B deferrals (DEC-132), Family-C `cd0e`, and the four priced for the first time at
  the close (`579d`, `9df3`, `bad2`, `8144`) — each deferred **with a stated reason**, none of which
  moved in the last thirteen minutes. Picking one would be exactly the failure the close wrote down
  as foreseeable: *routing a below-bar row by default because the queue looks ready.*
- **What I did not do.** No task started, closed, failed, created or reopened; `task-1785442499-1851`
  untouched — an agent starting an operator gate is the one move the operator-gate discipline exists
  to forbid. No file under `ansible/` or `scripts/` edited, no commit, no `just play`, no live call,
  no vault value; gates 1b/2b/3b/4d untouched. One log written (`logs/builder-it88-gate.log`).
- **Emitting `build.blocked` to Ralph** naming the gate that actually blocks. The objective advances
  through `just play` + a browser, and no agent may take it.

## 2026-08-01 — Builder, `task-1785571102-579d` (guard: `_read` on raw invalid UTF-8) — BUILT, `review.ready`

**WHY A ROW AT ALL, WITH THE PLAN'S NUMBERED STEPS EXHAUSTED (DEC-157).** The runner was **started
again at 10:15:30Z** with 4d still open (fresh `build.start`, PIDs 287876/287888) after three
iterations that deliberately published nothing. Nothing else moved — `find -newermt 08:30` returns
only `.ralph` runner state, 4d is still `open`, HEAD is still `7e9c426` — so the restart is an
operator ACTION without operator EVIDENCE. It re-prices magnitude, not correctness, and `579d` was
deferred on magnitude alone. It is not a Step 6: no step is cut, no wave materialized, the other ten
rows keep their deferrals, and `task-1785442499-1851` is untouched and was not `task start`ed.

**THE REPAIR (DEC-158), option (ii) of the two the task named.** `scripts/test_grafana_provisioning_shape.py`
`bb…` → sha256 **c5dc74ba**:
  - `_read` catches `UnicodeDecodeError` beside `OSError` (it is a ValueError, so `except OSError`
    never caught it) and pins `encoding="utf-8"`;
  - new `_unreadable(path)` turns the None back into a sentence with the **byte offset**, the
    sequence in hex and the decoder's own reason, and says what the engine does with it;
  - the five reporting sites print that reason instead of the bare word `missing` — the word is
    unchanged for a file that is genuinely absent;
  - `main()` sets the stdout ERROR POLICY (not the encoding) so the sentence can be printed at all.

**RED FIRST, and the RED is 12 rows wide.** `logs/red-579d-read-invalid-utf8.py`
**8/20 → 20/20** (`-pre.log` / `.log`). The 12 MISSes are exactly the new-behaviour rows: PART A the
four measured byte sequences produce `verdict=None` + a traceback; PART B no line names the file and
the offset; PART C under `LC_ALL=en_US.iso88591` all four are **`PASS: 21/21`** — the FALSE ACCEPT
half. The accept side passed before the change and still does: PART D the tree as delivered is GREEN
in both locales and a legal `é☃` title stays GREEN; PART E an ABSENT carrier still reddens with the
old word `missing` and claims no byte offset, so PART B is a new fact and not a rename.

**EVERY CLAUSE IS LOAD-BEARING.** `logs/red-579d-inert-check.py` **19/19** reconstructs each PRE
state by an inverse substitution into a **private tempdir** whose `ansible/` is a symlink to the real
tree — the real guard is never written to (`mem-1785571118-df19`, and Z2 asserts its sha is
unchanged). V1 no pin → accepted under latin-1; V2 no catch → traceback, no summary line; V3 no
stdout policy → `UnicodeEncodeError`, summary line lost a second way; V4 no `_unreadable` → RED, but
it says `missing` about a file that is right there. Each is paired with the repaired guard on the
same bytes.

**THE ACCEPTANCE CRITERIA, IN THEIR OWN ORDER.**
  - (a) `just test` **GATE PASS 36/36 rc=0** (`logs/gate-579d-read-invalid-utf8.log`), guard
    **PASS 21/21** (no row added — a reader and a sentence, not a claim).
  - (b) `logs/critic-step05d-r11-rawbytes.py` re-run **UNEDITED** on the pinned
    `grafana/grafana:13.1.0` (`-579d-recheck.log`): PART A **4/4 still SAVED** and PART B's controls
    still discriminate, PART C **4/4 now carry a verdict** where they carried `None`, and the
    harness's own finding rows **D2/D3 FAIL** — 13/15, and that failure IS the flip.
  - (c) `logs/critic-step05d-r11-surrogate-slots.py` re-run unedited **67/67**
    (`-579d-recheck.log`); all three delivered dashboards restored byte-identical.
  - (d) No live call, no `just play`, no commit, no vault value; gates 1b/2b/3b/4d untouched.

**ARTIFACTS BYTE-IDENTICAL AT BOTH ENDS.** `fde25673` / `a8a8c24e` / `1e8f3617`, `tasks/main.yml`
`71e88a89`, HEAD `7e9c426`, no commit. No leftover container (`podman ps -a` empty) and no leftover
tmpdir.

**THE ENGINE NUMBER WORTH KEEPING.** Go substitutes PER BYTE at this layer: `ed a0 80` stores as
three U+FFFD, `c0 80` as two, `ff` and `c3` as one each — where the `\uD800` ESCAPE r11 repaired
stores as ONE. That is why `_grafana_saved_text` is not the repair here and why nothing substitutes.

## 2026-08-01 — `579d` REWORK round 2 (`review.rejected` F1 → the sentence's ENGINE CLAUSE, F2 → the discovery reader, F3)

**THE VERDICT WAS RIGHT AND THE REASON WAS HALF WRONG, SO THE REPAIR IS IN THE REASON.** The review
reproduced every number and rejected on what the increment was built to produce: `_unreadable`
printed *"the provisioner SAVES this file with those bytes replaced by U+FFFD"* for a decode failure
at EVERY offset, but Go's `encoding/json` substitutes U+FFFD only while SCANNING A STRING. Outside
one an invalid byte is a syntax error and the file never loads at all — so for 2 of 4 measured
positions the operator was sent to the Grafana UI to compare a served dashboard that is ABSENT.

**WHAT CHANGED (three functions, all repo-side).**
  - `_json_string_open_at(raw, offset)` — a byte scan of the prefix with JSON's own escape rule.
    Safe on bytes because `offset` is a `UnicodeDecodeError.start`, so the prefix decoded, and a
    continuation byte is `>= 0x80` and can be neither `"` nor `\`.
  - `_unreadable` now prints the branch that was MEASURED for that position: INSIDE a string →
    SAVES with U+FFFD; OUTSIDE every string → REFUSES the whole file, `failed to load dashboard
    from`, and names the container log as where the repair is.
  - `_undecodable_role_json` + `_role_json_sources` — the discovery reader's THIRD STATE. F2's
    fail-open was real: catching the decode had turned a traceback into `PASS: 21/21` rc=0 for an
    undelivered undecodable `.json` whose name misses the `*dashboard*` glob.
    `test_dashboard_delivery_inventory_is_complete` now carries an `unreadable=[…]` term — the sixth
    `_unreadable` site — and it is the right row because it is the only reader here not keyed on a
    delivery. F3's `_dashboard_json_paths` is gone; the docstring names `_dashboard_sources_on_disk`
    and records that ONE caller (the datasource-type census) still skips, by design.

**RED-FIRST, AND THE PRE STATE IS A RUN AND NOT A CLAIM.**
`logs/red-579d-r2-position-and-discovery.py` **13/28 → 28/28**; the 15 MISSes are exactly the
new-behaviour rows (10 classifier, 2 sentence, 2 discovery, 1 docstring). The PRE log is a real run
of the ROUND-1 guard, reconstructed by inverse substitution of this round's three edits into a
private tempdir (`-pre.log`). Every guard run in this harness is over a TEMPDIR COPY of `scripts/` +
`ansible/` — the review's method (`mem-1785580683-b0a3`), so **no file under `ansible/` or
`scripts/` is written by the harness at all**.

**THE ACCEPTANCE CRITERIA, IN THEIR OWN ORDER.**
  - (a) `just test` **GATE PASS 36/36 rc=0** (`logs/gate-579d-r2.log`), guard **PASS 21/21**
    (`logs/green-579d-r2-guard.log`) — no row added, the third state lives inside an existing row.
  - (b) **The review's own harness, re-run UNEDITED: `logs/critic-579d-bad-byte-position.py`
    14/16 → 16/16** (`-r2-recheck.log`). Its PART A re-measured the engine in this run —
    `instr`/`inkey` SAVED, `struct`/`afterval` REFUSED, B1/B2 discriminating — and **D2/D3 flip**.
    `logs/critic-step05d-r11-rawbytes.py` unedited: PART C 4/4 keep a verdict, its finding rows
    D2/D3 still FAIL (13/15), which is the flip the task asked for; all four of its sequences are
    inside the `title` string and the classifier says INSIDE for all four, which the same run's
    engine side confirms (SAVED 4/4).
  - (c) Accept side: `logs/critic-step05d-r11-surrogate-slots.py` unedited **67/67**;
    `logs/red-579d-read-invalid-utf8.py` (round 1) unedited **20/20**; a legal non-ASCII UTF-8 title
    and a decodable non-dashboard JSON under `files/` are both still GREEN (E1/E2).
  - (d) No live call, no `just play`, no commit, no vault value; gates 1b/2b/3b/4d untouched.

**SHAS.** Guard `c5dc74ba` → **`aa95f902`**. Delivered artifacts byte-identical at both ends:
`fde25673` / `a8a8c24e` / `1e8f3617`, `tasks/main.yml` `71e88a89`, HEAD `7e9c426`, no commit.
No leftover container, no leftover tmpdir.

---

## 2026-08-01 — `579d` REWORK ROUND 3 (review.rejected F1 → the ESCAPE SLOTS, F2 → the SUBJECT)

**THE REJECTION WAS RIGHT, AND I RE-MEASURED THE ENGINE RATHER THAN CARRYING ITS TABLE.**
`logs/red-579d-r3-escape-slot-and-subject.py` provisions all FIVE positions itself on the pinned
`grafana/grafana:13.1.0`, one delivered file per position in ONE run, read back over the HTTP API,
with the anti-vacuity pair (legal control SAVED / 5001-char title REFUSED) in that same run. It
reproduces the review exactly: `0xb0` in the `title` string is **SAVED** as `'H<FFFD>me overview'`;
the same byte in an **ESCAPE slot** and inside a **`\uXXXX` escape** are **REFUSED**, and both are
INSIDE a string. **RED 30/38 → 38/38**, the 8 MISSes exactly the review's two findings.

**WHAT CHANGED, TWO EDITS IN TWO FUNCTIONS.**
  - **F1 — the classifier's rule is now the engine's.** `_json_string_open_at` carried `escaped`
    and discarded it; it now carries it plus a four-byte countdown after `\u` and returns
    `in_string and not escaped and not uhex`. The name is unchanged (three harnesses call it) and
    the docstring now states the rule as A CHARACTER POSITION, with the three-row measured table.
  - **F2 — the engine clause is earned by the CALLER.** `_unreadable(path, *, provisioned=False)`.
    The five readers that iterate `_delivered_dashboards` pass `provisioned=True`; the inventory
    row — which walks ANY role JSON, delivered or not, dashboard or not — does not, and prints the
    byte with "this row names the byte only". The default is the silent side, so a reader added
    later inherits the byte and not a claim. A `.j2` never earns it either: ansible renders it and
    the engine reads the RENDERED dest, at another path and another offset.
  - **F3 was raised and killed by the review itself** (Jinja quotes come in pairs and cancel; zero
    templates in this role spell one). Nothing to do, and the classifier docstring records it.

**THE BOUNDARIES OF THE NEW TERMS ARE MEASURED, NOT REASONED.** `escaped` and the countdown are
off-by-one hazards and the five rejection positions all sit at the START of an escape.
`logs/red-579d-r3-countdown-edges.py` **16/16** is a SECOND engine run over four more positions:
the byte after a complete `A` is SAVED (`'HA<FFFD>me overview'`), the FIRST hex digit is
REFUSED, and the byte after an escaped `\\` or an escaped `"` is SAVED. Nine measured positions,
nine agreements.

**THE ACCEPTANCE CRITERIA, IN THEIR OWN ORDER.**
  - (a) `just test` **GATE PASS 36/36 rc=0** (`logs/gate-579d-r3.log`), guard **PASS 21/21**
    (`logs/green-579d-r3-guard.log`) — no row added.
  - (b) **The round-2 review's own harness, re-run UNEDITED: `logs/critic-579d-r2-scope-and-escape.py`
    27/33 → 33/33** (`-r3-recheck.log`) — D1/D2/D3, D4-inesc/D4-inuesc and E2, all six findings,
    flip. The round-1 review's `logs/critic-579d-bad-byte-position.py` unedited **16/16**;
    `logs/red-579d-r2-position-and-discovery.py` unedited **28/28**;
    `logs/critic-step05d-r11-rawbytes.py` unedited **13/15** — PART C 4/4 keep a verdict and its
    finding rows D2/D3 FAIL, the flip the task asked for.
  - (c) Accept side: `logs/critic-step05d-r11-surrogate-slots.py` unedited **67/67**;
    `logs/red-579d-read-invalid-utf8.py` unedited **20/20**; clean tree, a legal non-ASCII title and
    a decodable non-dashboard role JSON all `PASS: 21/21` rc=0 (H1/H2/H3).
  - (d) No live call, no `just play`, no commit, no vault value; gates 1b/2b/3b/4d untouched.

**SHAS.** Guard `aa95f902` → **`e102f69b`**. `tasks/main.yml` `71e88a89` and the delivered
dashboard `fde25673` byte-identical at both ends of every run (Z rows), HEAD `7e9c426`, no commit.
No file under `ansible/` written at all — every guard run is over a tempdir copy. No leftover
container or tmpdir.

## 2026-08-01 — `579d` REWORK round 4 (review.rejected F1 → the SECOND byte, F2 → the MODULE)

**BOTH FINDINGS ARE ENGINE CLAIMS, SO THE RED HARNESS PROVISIONS THEM ITSELF.**
`logs/red-579d-r4-second-byte-and-template.py` / `.log` / `-pre.log`, pinned
`grafana/grafana:13.1.0`, three multi-byte carriers as one delivered file each in ONE provisioning
run, HTTP API readback, B1/B2 discriminating in that same run, plus a real `ansible-playbook`
(core 2.21.1). It reproduces the review exactly: `0xb0` at a rune position in the title PLUS
`0xa0` in the structural whitespace before the final brace (bytes 1598, 1660) is **REFUSED**
(`failed to load dashboard from` in that run's container log), both bytes at rune positions
(1598, 1602) is **SAVED** as `'H<FFFD>me <FFFD>verview'`, and the same pair in the other order
(2, 1599) is REFUSED. **RED 18/25 → 25/25**, the 7 MISSes being exactly the review's two findings
plus the three boundary rows the walk had to earn.

**F1 — THE CLASS IS THE FILE'S, NOT THE FIRST BYTE'S (DEC-167).** `_unreadable` walks EVERY invalid
sequence (`raw[start:].decode()`, accumulating `start + exc.start` / `start += exc.end`) and takes
`rune = all(_json_string_open_at(raw, o) …)`. The classifier is untouched: same name, same rule,
same nine measured positions, so DEC-164 stands and the three harnesses that call it by name stay
runnable unedited. The sentence still opens with the FIRST bad byte — where an operator's editor
lands — gains `, and N more invalid sequence(s) at byte(s) …`, and names the byte its class belongs
to (`byte 1660 is not a character position …`), because attributing the deciding class to byte 1598
would have replaced one false sentence with another. **The single-offset spelling is byte-identical
to round 3's**, which is what keeps six pinned harnesses scoreable unedited. Three boundary rows
that only measurement settles: two ADJACENT bad bytes are both counted (a walk resuming at
`exc.start` would loop), a truncated `c3` at EOF terminates it, and the deciding byte is named.

**F2 — THE MODULE IS THE FACT, THE SUFFIX WAS A PROXY (DEC-166).** `_delivered_dashboards` now
PUBLISHES `is_template` as a fourth field instead of computing and discarding it, and the five
delivery readers pass `provisioned=not rendered`; `_unreadable` no longer reads `path.suffix`.
Re-measured with real ansible (E1): `template:` with `src: dash.json` renders it, `{{ 40 + 2 }}`
arriving as `42`. Both directions now hold end to end through the guard, in the same run — a
`template:`-delivered `.json` gets the byte WITHOUT the provisioner clause (F2), and a
`copy:`-delivered `.json.j2` KEEPS the clause its verbatim bytes earn (G2).

**THE REVIEW'S OWN BATTERY MOVED 19/22 → 20/22, AND THE DELTA IS PROVEN TO BE MINE.**
`logs/red-579d-r4-critic-recheck.py` **22/22** rebuilds the pre-round-4 guard by a 15-pair inverse
edit, asserts it back to **`e102f69b` byte-for-byte**, and re-runs
`logs/critic-579d-r3-second-byte-and-render.py` UNEDITED against that reconstruction: its three
findings (C-strstruct, F2, G2) are still MISS there, so they are this round's work and nothing
else moved. Its D2/D3 flip to MISS against the new guard **by design** — those two rows assert the
guard says SAVES/SERVES where the harness's own PART A measured the engine REFUSING, i.e. they are
the review's DEMONSTRATION of the defect. One further difference is fenced and measured rather
than argued: E1 shells out to `mise exec -- ansible-playbook` from the harness's own `ROOT`, so a
copy under a tempdir measures that tempdir's tools; PART T runs the identical playbook from the
REAL root in the same run and it renders rc=0. **Unlike its name suggests, this recheck never
writes the real guard** (mem-1785571118-df19 is about the overwrite-and-restore kind) — Z1/Z2
assert the file byte-for-byte.

**NUMBERS.** `just test` **GATE PASS 36/36 rc=0** (`logs/gate-579d-r4.log`), guard **PASS 21/21**
(`logs/green-579d-r4-guard.log`) — no row added. Re-run UNEDITED, all at their handed-off scores:
`red-579d-r3-escape-slot-and-subject.py` **38/38**, `red-579d-r3-countdown-edges.py` **16/16**,
`critic-579d-r2-scope-and-escape.py` **33/33**, `red-579d-r2-position-and-discovery.py` **28/28**,
`critic-579d-bad-byte-position.py` **16/16**, `red-579d-read-invalid-utf8.py` **20/20**,
`critic-step05d-r11-surrogate-slots.py` **67/67** (the accept side), and
`critic-step05d-r11-rawbytes.py` **13/15** with D2/D3 the flip the task asked for.
Guard sha `e102f69b` → **`1e207a2b`**.

**WHAT I DID NOT DO.** No commit (HEAD `7e9c426`), no `just play`, no live call, no vault value;
gates 1b/2b/3b/4d untouched and `task-1785442499-1851` not started, closed or edited. **No file
under `ansible/` written at all** — `tasks/main.yml` is still `71e88a89` and the carrier
`fde25673`; every guard run lived in a tempdir copy. No task created, closed, failed or reopened.
No leftover container or tmpdir.

## 2026-08-01 — `579d` REWORK round 5 (review.rejected F1 → the SAVE LAYER, F2 → the SECOND WITHHOLD REASON)

Task `task-1785571102-579d`, artifact `scripts/test_grafana_provisioning_shape.py`
`1e207a2b` → **`0c711e57`**. RED first: `logs/red-579d-r5-save-layer-and-subject.py`
**35/58 → 58/58**, and the RED half is the SAME harness against a tempdir reconstruction of
`1e207a2b` (`logs/red-579d-r5-pre-guard.py`, asserted back byte-for-byte), so the delta is this
round and nothing else. Pinned `grafana/grafana:13.1.0`, seventeen delivered files in ONE
provisioning run, HTTP API readback by uid AND by title, container log kept, B1/B2 discriminating
in that same run. Every guard run lived in a TEMPDIR COPY; Z1–Z4 assert the real tree.

**F1 — THE THIRD SENTENCE (DEC-169), AND THE REVIEW'S HAZARD WAS REAL.** A file whose bad bytes
are all at rune positions PARSES and then meets the SAVE layer, whose rules this guard already
holds. `_unreadable` now decodes the bytes, runs `_grafana_provisionable_json`,
`_grafana_short_uid_defect`, `_grafana_title_defect` and `_grafana_tags_defect` over the document,
and prints a third outcome naming the rule and the container-log line measured for it. Nine
carriers, every bad byte at a rune position — so the shipped guard said "SAVES" for all nine:

| carrier | engine | the line in the log |
|---|---|---|
| `0xb0` in the top-level `uid` | **REFUSED** | `failed to save dashboard` / `uid contains illegal characters` |
| `0xb0` in `title`, and in a KEY string | SAVED | — |
| `0xb0` + a trailing comma | **REFUSED** | `failed to load dashboard from` / `invalid character` |
| a tag of 48 ASCII + `0xb0` (51 bytes) | **REFUSED** | `failed to save dashboard` / `dashboard tag too long` |
| a tag of 47 ASCII + `0xb0` (50 bytes) | SAVED | — |
| `0xb0` inside a top-level ARRAY | **REFUSED** | `failed to load dashboard from` |

**AND THE DECODER IS GO'S, NOT PYTHON'S — the one thing DEC-168 could not settle from the loop.**
Measured on the STORED title in that same run (PART C, 6/6): the engine substitutes ONE U+FFFD per
invalid BYTE — `ed a0 80`→3, `c0 80`→2, `ff`→1, `c3`→1, `e2 82`→**2**, `f0 9f`→**2** — while
python's `errors="replace"` works per MAXIMAL SUBPART and says 1 for both truncated prefixes. It is
a VERDICT and not a count: a tag of 46 ASCII + `e2 82` is **52 bytes to the engine and 49 to
python**, one side of the 50 bound each, and the engine REFUSED it in this run (A-tagtrunc52,
C-verdict). Hence `_grafana_saved_bytes`, the byte-layer twin of `_grafana_saved_text`; the
substitution stays inside the reporting function, clear of DEC-150/DEC-167(iii).

**F2 — TWO WITHHOLD REASONS, TWO SENTENCES (DEC-170).** `rendered=` is a second keyword rather
than a second meaning of `provisioned=`, and the five delivery readers pass
`provisioned=True, rendered=rendered`. On a real `ansible.builtin.template:` delivery of a
dashboard carrying one bad byte (PART G): 11 of 11 withholding delivery rows now name the RENDERING
and none makes an engine claim, the delivery rows print "this is not one" **zero** times (was 11),
and the ONE inventory row keyed on no delivery still prints its own sentence byte-identically.

**NUMBERS.** `just test` **GATE PASS 36/36 rc=0** (`logs/gate-579d-r5.log`), guard **PASS 21/21**
(`logs/green-579d-r5-guard.log`) — no row added.
Re-run UNEDITED against the shipped guard, all at their handed-off scores:
`red-579d-r4-second-byte-and-template.py` **25/25**, `red-579d-r3-escape-slot-and-subject.py`
**38/38**, `red-579d-r3-countdown-edges.py` **16/16**, `critic-579d-r2-scope-and-escape.py`
**33/33**, `red-579d-r2-position-and-discovery.py` **28/28**, `critic-579d-bad-byte-position.py`
**16/16**, `red-579d-read-invalid-utf8.py` **20/20**, `critic-step05d-r11-surrogate-slots.py`
**67/67** (the accept side), `critic-step05d-r11-rawbytes.py` **13/15** with D2/D3 the flip the
task asked for. **THE ROUND-4 REVIEW'S OWN BATTERY WENT 20/24 → 24/24**
(`critic-579d-r4-save-layer-and-subject.py`): all four of its findings — C-uidbyte, D3, E2, F2 —
flip to OK and nothing else moved.

**THE ONE HARNESS THAT DOES NOT RE-RUN CLEAN, AND WHY IT IS NOT A REGRESSION.**
`red-579d-r4-critic-recheck.py` scores **9/16**: six of its fifteen inverse-edit pairs quote text
round 5 rewrote, so it can no longer rebuild `e102f69b` from the SHIPPED guard. A recheck's
inverse edit is keyed to the revision it was written against, and the fact is not lost — it is
CHAINED. `logs/red-579d-r5-recheck-chain.py` **5/5** imports both harnesses' pair lists unedited
and shows `0c711e57` → (round 5's own inverse edit) → **`1e207a2b`** → (the r4 harness's OWN 15
pairs, all matching exactly once there) → **`e102f69b`**, and names the six pairs that moved as
exactly [7, 8, 9, 12, 13, 14]. Their file is not edited.

**WHAT I DID NOT DO.** No commit (HEAD `7e9c426`), no `just play`, no live call, no vault value;
gates 1b/2b/3b/4d untouched and `task-1785442499-1851` not started, closed or edited. **No file
under `ansible/` written at all** — `tasks/main.yml` still `71e88a89`, carrier `fde25673`; every
guard run lived in a tempdir copy and Z1–Z4 assert the real tree at both ends. No task created,
closed, failed or reopened. No leftover container or tmpdir.

## 2026-08-01 — `579d` REWORK round 6 (review.rejected F1 → THE LOG LINE IS THE RULE'S)

**Task.** `task-1785571102-579d` — *guard: `_read` is `read_text()` inside `except OSError`*.
Round-5 review rejected on F1/DEC-171: `_unreadable` assigns the container-log line the operator
greps for by `try`/`except` BRANCH, and the engine partitions by RULE. Two of the eight rules the
review priced disagree, one in each direction.

**Verification commands and results.**

| command | result |
|---|---|
| `logs/red-579d-r6-rule-to-log-line.py` (RED, guard `0c711e57`) | **45/59**, `logs/red-579d-r6-pre.log` |
| `logs/red-579d-r6-rule-to-log-line.py` (GREEN, guard `60160595`) | **59/59**, `logs/red-579d-r6.log` |
| `logs/red-579d-r6-pre-guard.py` | rebuilds `0c711e57` byte-for-byte from the shipped file |
| `logs/red-579d-r6-critic-recheck.py` | **6/6** — both review batteries score their ORIGINAL numbers and miss sets at `0c711e57` |
| `logs/red-579d-r6-recheck-chain.py` | **6/6** — `60160595 → 0c711e57 → 1e207a2b → e102f69b` |
| `logs/red-579d-r5-save-layer-and-subject.py` (round 5's own, unedited) | **58/58** unchanged |
| `logs/critic-579d-r5-rule-to-log-line.py` (review's, unedited) | **8/9** unchanged (its one miss is its own wrong prediction, an engine row) |
| `logs/critic-579d-r5-savelog-and-granularity.py` | 19/20 → **18/20**: the FINDING row flips to OK, its two end-to-end DEMONSTRATION rows flip to MISS |
| `logs/critic-579d-r5-title-key-mangled.py` | 6/7 → **5/7**: same shape, `D-log-line` is the demonstration |
| `just test` | **GATE PASS 36/36 rc=0**, `logs/gate-579d-r6.log` |
| guard standalone | **PASS 21/21** |

**What changed in `scripts/test_grafana_provisioning_shape.py`** (`0c711e57` → `60160595`):
`GRAFANA_LOG_SAVE`/`GRAFANA_LOG_LOAD` with the measured rule→line table above them;
`GrafanaUnprovisionableJSON` carries `.log`, learned at each `raise` (`_number` → SAVE,
`_token` → LOAD, default LOAD); `_unreadable` splits its `except` so the exception's own line is
used and adds `_grafana_dashboard_title` — the engine's `MustString()` — as a LOAD-layer rule
asked BEFORE the save-layer `or` chain.

**Two things this round measured that the review's table did not have** (DEC-172). (1) The
discriminator is not `isinstance`: `""` is a `str` and is refused on the LOAD line with absent /
`null` / `42`, while `"   "` is a `str` and is refused on the SAVE line. (2) The order the review
handed over rather than assumed is real — a document with both an absent title and an illegal uid
is refused on the TITLE, at the LOAD.

**WHAT I DID NOT DO.** No commit (HEAD `7e9c426`), no `just play`, no live call, no vault value;
gates 1b/2b/3b/4d untouched and `task-1785442499-1851` not started, closed or edited. **No file
under `ansible/` written at all** — `tasks/main.yml` still `71e88a89`, carrier `fde25673`; every
guard run lived in a tempdir copy and the Z rows assert the real tree at both ends. No task
created, closed, failed or reopened. No leftover container or tmpdir.

## 2026-08-01 — `579d` REWORK round 7 (review.rejected F1/DEC-173 → THE RULES IN THE ENGINE'S ORDER)

**Task.** `task-1785571102-579d` — *guard: `_read` is `read_text()` inside `except OSError`*.
Round-6 review rejected on F1: DEC-172's ordering principle is implemented inside
`_unreadable`'s `else:` only, so the ONE save-line rule that arrives as an EXCEPTION — a number
past the IEEE double range — is caught before the `else:` is entered and answers for every
document that also breaks a rule the engine reaches earlier.

**Verification commands and results.**

| command | result |
|---|---|
| `logs/red-579d-r7-rule-order.py` (RED, guard `60160595`) | **43/61**, `logs/red-579d-r7-pre.log` |
| `logs/red-579d-r7-rule-order.py` (GREEN, guard `be32a6ce`) | **59/61**, `logs/red-579d-r7.log` |
| `logs/red-579d-r7-tag-vs-number.py` (second run, every log line printed) | **13/13** |
| `logs/red-579d-r7-end-to-end-lines.py` (both revisions, offline) | **9/9** |
| `logs/red-579d-r7-pre-guard.py` | rebuilds `60160595` byte-for-byte from the shipped file |
| `logs/red-579d-r7-recheck-chain.py` | **8/8** — `be32a6ce → 60160595 → 0c711e57 → 1e207a2b → e102f69b` |
| the review's `logs/critic-579d-r6-parse-vs-load-order.py`, UNEDITED | 28/40 → **40/40** |
| the review's `logs/critic-579d-r6-rule-named.py`, UNEDITED | 2/7 → **7/7** |
| round 6's `logs/red-579d-r6-rule-to-log-line.py`, UNEDITED | **59/59** unchanged |
| round 5's `logs/red-579d-r5-save-layer-and-subject.py`, UNEDITED | **58/58** unchanged |
| `logs/critic-579d-r5-rule-to-log-line.py` | **8/9** unchanged, same miss |
| `logs/critic-579d-r5-savelog-and-granularity.py` | **18/20** unchanged, same miss set as round 6 |
| `logs/critic-579d-r5-title-key-mangled.py` | **5/7** unchanged, same miss set as round 6 |
| `just test` | **GATE PASS 36/36 rc=0**, `logs/gate-579d-r7.log` |
| guard standalone | **PASS 21/21** |

**What changed in `scripts/test_grafana_provisioning_shape.py`** (`60160595` → `be32a6ce`):
`_grafana_provisionable_json` gains `deferred: list | None = None` — the number-range refusal is
collected instead of raised for the ONE caller that has to name WHICH rule refused the file, and
every other caller keeps the raise and the default; `_unreadable` asks the six rules in the
engine's measured order (parse → load-layer title/shape → uid → title trim/bound → NUMBER →
tags), with the save-layer chain now an explicit ordered sequence of `(refusal, line)` pairs; and
the LOAD-layer branch prints the load layer's own sentence instead of borrowing
`_grafana_title_defect`'s save-time TRIM text (the review's F2). The measured order table lives
above `GRAFANA_LOG_SAVE`.

**What this round measured that the review's own repair did not have** (DEC-174). The review
handed over "the number-range refusal is asked LAST" and named `tags` as the pair its run could
not separate. Carried: a document with `1e400` AND a 51-byte tag is refused on
`json: cannot unmarshal number 1e400`, and the tag rule is named NOWHERE in its log line — so the
number is **5th of six**, ahead of the tags, and "last" would have named a rule the engine never
reached. `logs/red-579d-r7-pre.log` A-num_tag is that prediction failing in the very run that
priced it; `logs/red-579d-r7-tag-vs-number.py` reproduces it in a second run, with the tag rule
alone reached in that same run (A3) so the silence is a measurement.

**The two misses in the GREEN run are the harness's own predictions, not guard defects.**
`A-num_tag` is the one above — an ENGINE row, kept unedited between the RED and the GREEN run so
the delta stays one file's. `F3` demands that all 12 end-to-end rows name the LOAD line, and one
of the twelve is the inventory reader, which is not keyed on a delivery and names no engine line
by design (r5 F2/G2). `logs/red-579d-r7-end-to-end-lines.py` scores the true claim at both
revisions: **0 SAVE / 11 LOAD** now against **11 SAVE / 0 LOAD** at `60160595`, with the silent
row identified by its own sentence.

**WHAT I DID NOT DO.** No commit (HEAD `7e9c426`), no `just play`, no live call, no vault value;
gates 1b/2b/3b/4d untouched and `task-1785442499-1851` not started, closed or edited. **No file
under `ansible/` written at all** — `tasks/main.yml` still `71e88a89`, carrier `fde25673`; every
guard run lived in a tempdir copy and the Z rows assert the real tree at both ends. No task
created, closed, failed or reopened. No leftover container or tmpdir.

## 2026-08-01 — Builder, `579d` REWORK round 8 (review.rejected F1 → THE TITLE IS ASKED BEFORE THE `uid`)

Active task `task-1785571102-579d` (`code-assist:plex-monitoring:guard:read-text-raw-invalid-utf8`),
artifact `scripts/test_grafana_provisioning_shape.py` (`be32a6ce` → `1fa628fd`). Verification
commands: `just test`, the guard standalone, this round's RED harness at BOTH revisions, and
every prior hat's battery unedited.

**What changed.** `_unreadable`'s save-layer chain asks `_grafana_title_defect(title)` before
`_grafana_short_uid_defect(uid)`; the ordinal table above `GRAFANA_LOG_SAVE` and `_unreadable`'s
docstring state the measured order (parse → LOAD-layer title → **title trim/5000** → **uid** →
NUMBER → tags); and `_grafana_short_uid_defect` asks its CHARSET branch before its length branch.

**RED → GREEN, same harness, engine answers held fixed.** `logs/red-579d-r8-title-before-uid.py`
**20/25 at `be32a6ce` → 25/25 at `1fa628fd`** — five misses, three of them the review's own PART
C rows and two the `uid` sub-rule nothing had carried. The pre revision is rebuilt to its own sha
by `logs/red-579d-r8-pre-guard.py`, so the RED number is the same harness against the guard the
round started from and not a narration.

**The engine, measured here rather than taken from the handover.** One delivered file per carrier
in ONE provisioning run on the pinned `grafana/grafana:13.1.0`, container log kept, every `error=`
per file printed, anti-vacuity 6/6 in that same run: illegal `uid` + a blank-after-trim title →
`Dashboard title cannot be empty`; illegal `uid` + a 5001-character title → the 5000 bound; uid
TOO LONG + blank title → the title; uid + a 51-byte tag → the uid. And the pair DEC-175 declared
NOT measured: a 43-character uid carrying a space is `uid contains illegal characters`, with the
space at the END and at the FRONT alike, while the same run names `uid too long` for a legal
41-character uid.

**Nothing undisputed moved.** `just test` **GATE PASS 36/36 rc=0**, guard **PASS 21/21**. The
round-7 review's own battery `critic-579d-r7-save-layer-order.py` **18/21 → 21/21 UNEDITED**;
`critic-579d-r6-parse-vs-load-order.py` **40/40**; `critic-579d-r6-rule-named.py` **7/7**;
`red-579d-r7-rule-order.py` **59/61** with the same two declared misses (`A-num_tag`, `F3`);
`red-579d-r6-rule-to-log-line.py` **59/59**; `red-579d-r5-save-layer-and-subject.py` **58/58**.
`logs/red-579d-r8-recheck-chain.py` **9/9** keeps every reviewed revision rebuildable:
`1fa628fd → be32a6ce → 60160595 → 0c711e57 → 1e207a2b → e102f69b`, each link another hat's own
pair list, unedited.

**FILED, NOT REPAIRED (DEC-176).** `test_delivered_dashboards_parse_as_dashboards` spells the same
order a second time for READABLE deliveries and still asks the uid first. Out of the review's
stated scope, and its first line is another harness's cut anchor — priced in DEC-176, where that
harness's R1 is shown to be already unreachable (`905f46d8` against a declared `10fd3cdb`).

**WHAT I DID NOT DO.** No commit (HEAD `7e9c426`), no `just play`, no live call, no vault value;
gates 1b/2b/3b/4d untouched and `task-1785442499-1851` not started, closed or edited. **No file
under `ansible/` written at all** — `tasks/main.yml` still `71e88a89`, carrier `fde25673`; every
guard run lived in a tempdir copy and the Z rows assert the real tree at both ends. No task
created, closed, failed or reopened. No leftover container or tmpdir.

---

## 2026-08-01 — `579d` REWORK round 9 (Builder) — F1 THE uid TRIM CLASS, `1fa628fd` → `74df518a`

**THE ASSIGNED WORK.** The round-8 review's F1: the engine TRIMS a class off a delivered
`uid` and `_grafana_short_uid_defect` called that `uid contains illegal characters`, reddening
`just test` on 28 of 38 candidates the provisioner SERVES. Repaired, and the class is carried
whole rather than inherited.

**Verification commands and results.**

| command | result |
|---|---|
| `just test` | **GATE PASS 36/36 rc=0** |
| `python3 scripts/test_grafana_provisioning_shape.py` | **PASS 21/21 rc=0** |
| `logs/red-579d-r9-uid-trim-class.py` (41 delivered files, pinned image, `RED579DR9_ENGINE` held) | **RED 31/36 at `1fa628fd` → GREEN 36/36 at `74df518a`** |
| `logs/red-579d-r9-collision-detail.py` (2 colliding pairs + a control, whole container log) | **9/9** |
| `logs/red-579d-r9-end-to-end-collision.py` (whole gate at 3 revisions) | **12/12** |
| `logs/red-579d-r9-pre-guard.py` | reconstruction lands on **`1fa628fd`** byte-for-byte, real path unwritten |
| `logs/red-579d-r9-recheck-chain.py` | **10/10** — `74df518a → 1fa628fd → be32a6ce → 60160595 → 0c711e57 → 1e207a2b → e102f69b` |
| `logs/red-579d-r8-title-before-uid.py` (unedited, own hook + cached engine) | **25/25** — round 8's reorder untouched |
| `logs/red-579d-r8-end-to-end-rule-named.py` (unedited) | PART A **4/4**, numbers byte-identical; PART B/C raise (input revision moved) |
| `logs/critic-579d-r8-uid-trim-class.py` (the review's OWN battery, unedited) | **26/27**, its D1 count **28 → 1** |

**THE CLASS, MEASURED WHOLE.** All 12 codepoints the review declared not carried —
U+2001…U+200A, U+2029, U+205F — are TRIMMED at BOTH ends and the dashboard is served under the
trimmed uid; U+2000 and U+3000 are re-carried as a BRIDGE and answer exactly as the review's
run did. U+FEFF and U+200B are refused. So the class is Go's `unicode.White_Space` =
`GRAFANA_TITLE_TRIM` minus U+FEFF, 25 of 25 carried. **Round 8's sentence "at the END and at
the FRONT alike" is deleted**: its carriers are INTERIOR, and at the true ends the answer is
`uid too long` (D4) while the same character in the middle is still the charset (B2/B3).

**TWO EDITS, BECAUSE THE FIRST OPENS A HOLE.** `_grafana_stored_uid` is shared by
`_grafana_short_uid_defect` and `test_delivered_dashboards_have_distinct_uids`. At the MIDDLE
revision (trim honoured, sibling row untouched) a whole gate is **`PASS 21/21` over two
dashboards the engine keeps ONE of** — measured, not warned about. And the engine does not
warn either: zero duplicate-uid lines, zero write-lockout lines, no `error=`, the control
served, the survivor decided by file name.

**ROUTED, NOT RE-FILED.** F2 (the readable row's rule order, the review's own 0/2) is
**task-1785594766-fb36**, `code-assist:plex-monitoring:guard:readable-row-rule-order`, P2.

**WHAT I DID NOT DO.** No commit (HEAD `7e9c426`), no `just play`, no live call, no vault
value; gates 1b/2b/3b/4d untouched. **No file under `ansible/` written** — `tasks/main.yml`
still `71e88a89`, carriers unchanged; every gate run lived in a tempdir copy and the Z rows
assert the real tree at both ends. No leftover container or tmpdir. DEC-178.

---

## 2026-08-01 — Builder, `579d` REWORK round 10 (review.rejected F1 → THE THIRD CALL SITE, F2 → THE MULTISET QUESTION)

Active task `task-1785571102-579d` / `code-assist:plex-monitoring:guard:read-text-raw-invalid-utf8`.
Artifact `scripts/test_grafana_provisioning_shape.py` **`74df518a` → `84e87152`**. Two edits, both
in the review's own words, and nothing inside `_grafana_short_uid_defect` touched.

| verification | result |
|---|---|
| `just test` | **GATE PASS 36/36**, rc=0 |
| `python scripts/test_grafana_provisioning_shape.py` | **PASS 21/21** |
| `logs/red-579d-r10.py` (3 providers in ONE container + 5 whole-gate runs) | RED **20/25** → GREEN **25/25** |
| `logs/red-579d-r10-at-74df518a.log` (same harness, reconstruction) | **20/25**, the SAME five rows — the RED number reproduces from the shipped tree |
| `logs/red-579d-r10-pre-guard.py` | reconstruction lands on **`74df518a`** byte-for-byte, real path unwritten |
| `logs/red-579d-r10-recheck-chain.py` | **11/11** — `84e87152 → 74df518a → 1fa628fd → be32a6ce → 60160595 → 0c711e57 → 1e207a2b → e102f69b` |
| `logs/red-step05d-pve-dropdown.py` (unedited, at MY revision) | **23/23** — including D1/D2, the identity-pin rows F1 changes |
| `logs/red-579d-r9-end-to-end-collision.py` (unedited, at its own input revision) | **12/12** |
| `logs/critic-579d-r9-third-uid-row.py` (the review's OWN battery, unedited, at `74df518a`) | **21/21** reproduced at my hands, my own container |

**F1 — THE THIRD ROW KEYED ON THE FIELD.** `doc.get("uid") == PVE_DASHBOARD_UID` →
`_grafana_stored_uid(doc.get("uid")) == PVE_DASHBOARD_UID`. Measured at the row's OWN literal
base rather than a `pve…`-shaped stand-in: a delivered `pve-overview` + U+00A0 is **stored and
served at `pve-overview`** (PART A `a-pve`, read back over the HTTP API), and the pre revision
reddens the whole gate with `NO delivered dashboard carries the uid 'pve-overview'` — a wrong
VERDICT on a served document. PART B: rc=1 → **rc=0, PASS 21/21**.

**F2 — THE BRANCH ASKS THE ENGINE'S QUESTION NOW.** `len(spellings) == 1` →
`len(spellings) < len(claims)`, and the mixed case prints the loud sentence **plus** the trim
clause. Carried BOTH WAYS IN ONE CONTAINER, which no run had done: provider `pb` — FOUR files,
THREE spellings, one repeated (an arity the review did not carry) — gets `the same UID is used
more than once` (`times=2`) **and** the `provider=pb` write lockout; provider `pc` — two files,
two spellings, none repeated — gets **neither**, while still serving only ONE of its two. The
`for either` is now `for any of them` (arity-wrong for three claims).

**THE ACCEPT SIDE IS NOT BOUGHT WITH A WIDENING.** PART E: two IDENTICAL delivered spellings
still print the U1/U2 sentence **byte-for-byte**, so the harnesses that score it by substring
re-run unedited. PART D: a pure-trim pair still prints the SILENT sentence. PART F: the tree as
delivered is `PASS 21/21`.

**ONE PREDICTION THE RUN REFUTED, LEFT VISIBLE.** The chain's G1 row predicted `[4]` for which
round-9 pair my edit moves; it measured **`[6]`** — I counted r9's four numbered COMMENTS instead
of its six PAIRS. Same shape as the last chain's refuted prediction (mem-1785594888-2581); the
row now states what it measures and says so.

**WHAT I DID NOT DO.** No commit (HEAD `7e9c426`), no `just play`, no live call, no vault value;
gates 1b/2b/3b/4d untouched and `task-1785442499-1851` not started, closed or edited. **No file
under `ansible/` written** — every gate run lived in a tempdir copy and PART Z asserts the real
guard, all three dashboards and their uids at both ends. No task created, closed, failed or
reopened. No leftover container (`podman ps -a` empty) or tmpdir. DEC-179.

## 2026-08-01 — Builder, `579d` REWORK round 11 (review.rejected F1 → THE SKIP ABOVE THE BRANCH, F2 → the trim clause's gate)

Active task `task-1785571102-579d`, artifact `scripts/test_grafana_provisioning_shape.py`
**`84e87152` → `8e162d7b`**. Both rejection findings repaired as the review specified; F3
FILED as `task-1785598629-7407` (DEC-180).

**Verification, all at the shipped sha.**

| command | result |
|---|---|
| `just test` | **GATE PASS 36/36**, rc=0 (`logs/gate-579d-r11.log`) |
| the guard alone | **PASS 21/21** |
| `logs/red-579d-r11.py` (this round's RED) | **24/29 → 29/29** |
| the same, at `84e87152` via the inverse edit | **24/29**, the same five rows (`…-at-84e87152.log`) |
| `logs/red-579d-r11-crossprovider.py` | **9/9** |
| `logs/critic-579d-r10-dedupe-key.py` — the REVIEW's own, unedited | **9/12 → 11/12** |
| `logs/red-579d-r10.py` — round 10's own, unedited | **25/25** |
| `logs/critic-step05d-r11-surrogate-slots.py` — task criterion (c) | **67/67** |
| `logs/red-579d-r11-recheck-chain.py` | **13/13**, `8e162d7b` → `e102f69b` |

The five RED rows are exactly the two findings: B1/B2/B3 (F1 — the skip) and E2/E3 (F2 — the
clause). Every engine row and every accept-side row was ALREADY OK at `84e87152`, so the round
is additive. The review's B2 stays a MISS on purpose: it is an ENGINE row (a repeated
NON-STRING uid is silent), reproduced independently as this round's A7, and it is the
discriminator that fences the repair to a `str` uid.

**WHAT I DID NOT DO.** No commit (HEAD `7e9c426`), no `just play`, no live call, no vault
value, nothing under `ansible/` written — every gate run lived in a tempdir copy and PART Z
asserts the real guard and all three dashboards at both ends. Gates 1b/2b/3b/4d untouched and
`task-1785442499-1851` not started, closed or edited. No earlier hat's harness edited. One task
created (F3), none closed, failed or reopened. No leftover container or tmpdir. DEC-180.

## 2026-08-01 — Builder, `579d` REWORK round 12 (review.rejected F1 → THE EMPTY DELIVERED uid)

Active task `task-1785571102-579d`, key
`code-assist:plex-monitoring:guard:read-text-raw-invalid-utf8`. Artifact
`scripts/test_grafana_provisioning_shape.py`, **`8e162d7b` → `c1fbc7b3`**. ONE `and` operand:
the loop DEC-180 added is now fenced on `spelling` being non-empty, because
`_grafana_stored_uid(s) is None` names TWO members for a `str` and Grafana's dedupe skips the
empty key. DEC-181. No second finding filed.

| verification | result |
|---|---|
| `just test` | **GATE PASS 36/36**, rc=0 (`logs/gate-579d-r12.log`) |
| the guard alone | **PASS 21/21** (`logs/guard-579d-r12.log`) |
| `logs/red-579d-r12.py` (this round's RED) | **17/21 → 21/21** |
| the same, at `8e162d7b` via the inverse edit | **17/21**, the same four rows (`…-r12-pre.log`) |
| `logs/red-579d-r12-pre-guard.py --ast` | rebuilds `8e162d7b` by sha; AST delta = **1 line** |
| `logs/critic-579d-r11-empty-uid.py` — the REVIEW's own, unedited | **14/16 → 16/16** |
| `logs/red-579d-r11.py` — round 11's own, unedited | **29/29** |
| `logs/critic-step05d-r11-rawbytes.py` — task criterion (b) | **13/15**, row-for-row identical to the r5 recheck; PART C **4/4 a verdict, no traceback** |
| `logs/critic-step05d-r11-surrogate-slots.py` — task criterion (c) | **67/67** |

The four RED rows are exactly the finding: B1/B2 (the row's verdict over `""` twice) and D1/D2
(the four-dashboard tree carrying BOTH members, where the fence has to discriminate rather than
suppress). Every engine row and every accept-side row was ALREADY OK at `8e162d7b`, so the
round is additive. PART A swept the class the fence KEEPS — all 25 codepoints of
`GRAFANA_SHORT_UID_TRIM`, imported from the guard rather than retyped, plus a two-character
member, 26 of 26 loud — so "it fences nothing else" is a measurement.

**WHAT I DID NOT DO.** No commit (HEAD `7e9c426`), no `just play`, no live call, no vault
value, nothing under `ansible/` written — every gate run lived in a tempdir copy and PART Z
asserts the real guard and all three dashboards at both ends. Gates 1b/2b/3b/4d untouched and
`task-1785442499-1851` not started, closed or edited. No earlier hat's harness edited. No task
created, closed, failed or reopened. No leftover container or tmpdir.

## 2026-08-01 — Builder, Step 6a REWORK round 3 (review.rejected F1 → THE DECODE LAYER), guard `caf07913` → `fe6cc374`

**ACTIVE TASK** `task-1785601096-9ffc` (`code-assist:plex-monitoring:guard:duplicate-title-provider-lockout`).
Round 2's row grouped on `_grafana_provisionable_json(raw).get("title")` — the string PYTHON's
`json.loads` produced — where the engine groups on the string GO decoded. ONE call site, repaired in
this file's own idiom.

**COMMANDS RUN (all at my hands, none read off another hat's log):**

- `./logs/red-9ffc.py` **BEFORE the guard edit** → `logs/red-9ffc-r7-pre.log`, **12/15 rc=1**, the
  three new rows MISS: the whole guard printed `PASS: 22/22 rc=0` and `3 distinct title(s)` over the
  tree the review measured as locked out. That is the RED, and it is the review's F1 verbatim.
- `./logs/red-9ffc.py` **after** → `logs/red-9ffc.log`, **15/15 rc=0**, guard `fe6cc374`.
- `just test` → `logs/gate-9ffc.log`, **GATE PASS 36/36 rc=0** (AC(a)).
- `./logs/red-9ffc-pre-guard.py` → `logs/red-9ffc-pre-guard.log`, **7/7**: the pre-edit guard is
  still reconstructed **by sha** (`c1fbc7b3e2e9`) from the shipped one, because this round's edits
  live entirely inside the span that harness already deletes. Exactly `['P1']` — the row count —
  still moves, nothing silently improved.
- `./logs/critic-9ffc-surrogate-title.py` **UNEDITED, another hat's harness, fresh container** →
  `logs/red-9ffc-r3-critic-recheck.log`, **8/11** (was 11/11), harness sha `5e7796f5bcd2` at both
  ends.

**THE THREE ROWS THAT FLIPPED IN THE REVIEW'S HARNESS ARE ITS THREE FINDING-DETECTORS, AND NOTHING
ELSE MOVED.** All five ENGINE rows re-measured green in a NEW container (`A1` `\ud800` vs `\udc00`
lockout, `A2` both served under ONE stored title, `A3` the literal U+FFFD, `A4` two distinct titles
silent, `A5` the verbatim twin) — so the finding's measurement stands unedited and this is a repair
and not a re-argument. `B1`/`B2` asserted the guard is GREEN over the locked-out trees and it is now
RED; `C1` asserted the defective literal `titles.setdefault((folder, title), []).append(src.name)`
is present and it is gone. `B3` (verbatim twin caught) and `C2` (both siblings already apply
`_grafana_saved_text`) stay OK; `C3` real tree byte-identical.

**THE NEW ROWS** — `red-9ffc.py` R7a/R7b/R7c: the guard is RED over `\ud800` vs `\udc00` (R7a), the
verdict names both files AND both delivered spellings (R7b), and the second member of the class — a
lone surrogate against the literal U+FFFD — is RED too (R7c). The accept side is unmoved: R2 (the
tree as delivered, 22/22), R3 (near miss), R4 (the trailing-space twin the engine serves) and R5 (the
unsavable pair) are all still GREEN, which is the point of DEC-184 below — a substitution on the key
can only merge groups, so it cannot manufacture a false refusal the way a trim would.

**PRINTED WHAT IS ON DISK, GROUPED ON WHAT GO HOLDS.** The single-spelling verdict is BYTE-IDENTICAL
to round 2's (`R1`'s sentence is unchanged); the decode clause only appears when the delivered
spellings actually differ, because that is the only case where naming the decoded title alone would
send an operator grepping their own file for text nothing on disk carries.

**NOT DONE:** no commit (HEAD `7e9c426`), no `just play`, no live call, no vault value, no other
hat's harness edited, no task created or closed, gates 1b/2b/3b/4d untouched, no leftover container.
Files written: `scripts/test_grafana_provisioning_shape.py`, `logs/red-9ffc.py`, and four logs.

## 2026-08-01 — Step 6a REWORK round 4 (task-1785601096-9ffc): the fence, and the half of the uid predicate the engine SAVES

Guard `fe6cc374` → `8dbcf6fa`, still 22 rows. `just test` **GATE PASS 36/36 rc=0**
(`logs/gate-9ffc-r4.log`); `logs/red-9ffc.py` **21/21** (was 15/15, six rows added).

**RED FIRST.** R8a…R8d and R9a/R9b went into `logs/red-9ffc.py` before the guard was touched:
`logs/red-9ffc-r8-pre.log` **17/21** — the four R8 rows MISS against guard `fe6cc374` (the collision
row prints a provider-wide lockout over trees the engine is silent about) and R9a/R9b already pass,
which is what makes them a guard-rail and not a new claim.

**THE MEASUREMENT THAT CHANGED THE REPAIR.** The review named the parse row's `or` verbatim.
`_grafana_short_uid_defect` has four members and only two are refusals; the other two are SAVED
under a generated uuid. `logs/red-9ffc-r4-uuid-uid-title.py` / `.log`, **8/8**, seven providers in
one container on the pinned `grafana/grafana:13.1.0`: `yc` (uid `42`) and `yd` (uid U+2003) BOTH take
the provider-wide lockout with BOTH files served; `yf`/`yg` (same uids, DISTINCT titles) are silent,
which attributes it to the title; `ye` reproduces the review's `xb`. So the fence asks the uid
predicate through `_grafana_stored_uid`, and the verbatim `or` would have installed a false GREEN
where a false SENTENCE was (DEC-185).

**THE CONFOUND, KEPT VISIBLE.** That harness's first run
(`logs/red-9ffc-r4-uuid-uid-title-confounded.log`, 6/7) gave `yd` and `yg` the same empty-trimming
uid spelling `"  "` and the engine locked BOTH out on `the same UID is used more than once` — the
uid tracker is global over spellings, exactly what bit `red-579d-r11`'s first attempt. Distinct
spellings (U+2003 / U+3000) fix it, and a new Y0 row fails the harness if the confound ever returns.

**COLLATERAL, RE-RUN UNEDITED.** `logs/red-9ffc-pre-guard.log` **7/7** — the pre-edit guard still
rebuilds BY SHA, because this round's edits are entirely inside the new function's span (which is why
DEC-185 refused a new helper). `logs/red-9ffc-r4-critic-fence-recheck.log` **3/7**: the review's own
harness, unedited — G1…G4 were its finding-detectors and G5 (delivered tree GREEN) / G6 (two savable
files, one title, still RED) / G7 stay green. `logs/red-9ffc-r4-surrogate-recheck.log` **8/11**,
identical to round 3, all five ENGINE rows green — this round is inert on the decode class.

**NOT DONE:** no commit (HEAD `7e9c426`), no `just play`, no live call, no vault value, no other
hat's harness edited, no task created or closed, gates 1b/2b/3b/4d untouched, no leftover container.

## 2026-08-01 — Step 6a REWORK round 5 (task-1785601096-9ffc): the row now QUOTES the engine's line, guard `8dbcf6fa` → `3f6b816a`

**THE REJECTION WAS THE SENTENCE, NOT THE FENCE**, and the review said so — it re-ran round 4's work
unedited and could not break it. The closing clause, untouched since round 1, said "AND THE ENGINE
GIVES NO MESSAGE OF ITS OWN … no title line … so the log names neither of these files". The engine
prints `dashboard title is not unique in folder` with the title verbatim, the `folderID`, `times=N`
and the provider, IMMEDIATELY ABOVE the lockout. Five containers agreed it was silent because all
five keep only lines matching `more than once` or the lockout string, and that line carries neither.

**RED FIRST.** `logs/red-9ffc-r5-pre.log` **21/26** against guard `8dbcf6fa`: R1d (rewritten — it
asserted the false clause), R10a, R10b, R10b2, R10c all MISS; **R10d already passed**, which is what
makes the uid row's `grafana keeps ONE of them` a guard-rail rather than a new claim.

**THE MEASUREMENT, AND IT CLOSED THE REVIEW'S OWN HANDOVER.** `logs/red-9ffc-r5-title-line.py` /
`.log` **9/9**, seven providers in ONE container on the pinned `grafana/grafana:13.1.0`, W0 failing
the harness if either global tracker's confound returns:

    W1/W2  the finding's shape — the line names title/folderID=0/times=2/providers=[va], printed
           BEFORE the lockout. The BRIDGE to the review's own container.
    W3     distinct titles: no line, no lockout, both served — this run can say NO.
    W4/W5  THE HANDOVER ("I did not measure whether the title line appears for the SILENT scopes"):
           `foldersFromFilesStructure` with one title in two subdirectories, and two providers with
           distinct `folder:`, print NO title line either. Folder-scoped in BOTH outputs, so this
           row staying GREEN there leaves no engine line unexplained.
    W6/W7  `times=3` with all three served; and the COPY (one title AND one uid) prints BOTH lines
           and keeps ONE — the arity and the conditioning, re-carried rather than read off their log.
    W8     the engine's spelling asserted POSITIVELY, and the invented `title is used more than
           once` shown absent from the whole log.

**THE EDIT (DEC-186), one clause and one dict, all inside the row's own span.** Quote the engine's
line and keep the true half (it names a TITLE and a folder, never a FILE — the mapping is this row's
value); take `times={n}` and "these {n} FILES" from `len(files)`; and condition the serving claim on
`claimed[uid] > 1`, counted over the whole delivery because the uid tracker is global over delivered
SPELLINGS. Both sides of that condition are carried: R10a keeps `grafana serves all 2 of them` where
the spellings differ, R10c withholds it and names the repeated spelling where they do not.

**GREEN.** `logs/red-9ffc-r5.log` **26/26** against `3f6b816a`; `logs/gate-9ffc-r5.log` **GATE PASS
36/36 rc=0**.

**COLLATERAL, RE-RUN UNEDITED — INCLUDING THE REVIEW'S OWN.**
`logs/red-9ffc-r5-unfiltered-recheck.log` **5/5** and `logs/red-9ffc-r5-title-and-uid-recheck.log`
**8/8** — the round-4 review's two harnesses, at my hands in my own containers, so the fact this
round is built on is one measurement and not their log quoted back.
`logs/red-9ffc-r5-pre-guard.log` **7/7** (the pre-task guard still rebuilds BY SHA — every edit is
inside the row's span). `logs/red-9ffc-r5-critic-fence-recheck.log` **3/7** and
`logs/red-9ffc-r5-surrogate-recheck.log` **8/11**, both row-for-row IDENTICAL to round 4: the
`disables the WHOLE provider's writes` substring those harnesses score is kept BYTE-IDENTICAL, and
this round is inert on the decode class.

**ONE ACCEPTANCE CRITERION IS NOW REFUTED BY MEASUREMENT, FLAGGED NOT EDITED.** The task's WHAT says
the verdict "must name the two files and say that the engine gives no reason of its own". The first
half stands; the second is false (U1/U2, W1/W2) and the row now says the opposite. Changing the
task's own text is the Planner's call, not this hat's.

**NOT DONE:** no commit (HEAD `7e9c426`), no `just play`, no live call, no vault value, no other
hat's harness edited, no task created or closed, gates 1b/2b/3b/4d untouched, no leftover container.

## 2026-08-01 — Step 6a REWORK round 6 (task-1785601096-9ffc): the serving clause now carries BOTH uid keys, guard `3f6b816a` → `fb806621`

**THE REJECTION WAS ONE KEY SHORT, AND THE REVIEW MEASURED IT.** DEC-186 conditioned `grafana serves
all N of them` on `claimed[uid] > 1` — the DELIVERED spelling. The row one screen above needs two
keys and says so: the engine DEDUPES on the uid as delivered and STORES under the trimmed one. Two
files under one title whose uids differ only by a `GRAFANA_SHORT_UID_TRIM` member are two spellings
and ONE address, so `claimed` is 1 for each and the clause was KEPT — over a delivery the engine
serves 1 of 2 from, on the same gate output where the uid row printed `keeps ONE file, silently`.
That is exactly the self-contradiction `red-9ffc.py` R10d asserts round 5 removed, standing on the
key R10d does not carry.

**RED FIRST, AND RE-TAKEN SO IT IS ATTRIBUTABLE.** `logs/red-9ffc-r6-red.log` **28/30** against
guard `3f6b816a`. That first log's R10e MISS is over-determined — the kept clause (the finding) AND
a single-escaped needle of my own, where the row's `problems={bad}` repr()s an already-repr()'d uid
and reaches the operator as `\\xa0`. The guard is UNTRACKED, so there is no HEAD copy to re-run
against; `logs/red-9ffc-r6-preedit-swap.py` / `.log` rebuilds the pre-edit text by reversing this
round's three code edits, runs `logs/red-9ffc.py` UNEDITED against it, and restores the shipped file
in a `finally`: **28/31**, MISS on exactly R10e / R10e2 / R10h and nothing else, shipped sha
restored identical.

**THE MEASUREMENT IS THE REVIEW'S, RE-RUN AT MY HANDS.**
`logs/red-9ffc-r6-critic-r5-recheck.log` — `logs/critic-9ffc-r5-trim-uid-under-one-title.py`
UNEDITED, in my own container on the pinned `grafana/grafana:13.1.0`, **8/8**, `no leftover
container: True`. So `wa` served 1/2 with the title line, `times=2`, the LOCKOUT and **no uid line
at all** (C3–C6), and `wb`'s attribution of the lost file to the trim and not the title (C7), are
one measurement rather than two logs joined by prose.

**THE EDIT (DEC-187), one dict, one comprehension, one f-string, all inside the row's span.** Count
`_grafana_stored_uid` beside `claimed` past the SAME fence (`None` untracked — the engine generates
a uuid there and nothing can be lost to it); withhold the serving claim on EITHER key; print the two
causes as TWO sentences, because their engine evidence is opposite — the repeated spelling has `the
same UID is used more than once` to go read and the trim collision has NOTHING, which is what makes
the guard's sentence the only thing the operator has there.

**THE MIXED TREE IS ASSERTED, NOT ASSUMED.** R10h delivers one spelling twice plus a third that
trims onto it: both sentences print and each uid is named under ITS OWN cause (`claimed[uid] == 1`
keeps the twice-delivered spelling out of the silent list) — the shape the uid row's own `trimmed`
clause already describes.

**GREEN.** `logs/red-9ffc-r6.log` **31/31** against `fb806621`; `logs/gate-9ffc-r6.log` **GATE PASS
36/36 rc=0**, the guard's own row 21/21 and the delivered tree still `3 distinct title(s)`.

**COLLATERAL, RE-RUN UNEDITED.** `logs/red-9ffc-r6-pre-guard-recheck.log` **7/7** (the pre-task
guard still rebuilds BY SHA — every edit is inside the row's span) and
`logs/red-9ffc-r6-fence-recheck.log` **3/7**, row-for-row IDENTICAL to round 5's rerun: the
`disables the WHOLE provider's writes` substring other hats' harnesses score is kept BYTE-IDENTICAL,
and no harness in `logs/` other than `red-9ffc.py` scores the sentence this round changed.

**STILL FLAGGED, NOT EDITED (from round 5).** The filing task's WHAT — "say that the engine gives no
reason of its own" — is refuted by measurement and the row says the opposite. Changing the task text
is the Planner's call.

**NOT DONE:** no commit (HEAD `7e9c426`), no `just play`, no live call, no vault value, no other
hat's harness edited, no task created or closed, gates 1b/2b/3b/4d untouched, no leftover container.

## 2026-08-01 — Builder, `9ffc` REWORK round 7 (review.rejected F1 → THE DEDUPE'S KEY IS NOT A LOST FILE)

**THE INCREMENT.** One condition on round 6's `repeated` comprehension —
`and _grafana_stored_uid(uid) is not None` — plus the comment that now says why.
`claimed[uid] > 1` is the DEDUPE's key and answers "does the engine WARN"; the clause it guards
claims a LOST FILE. They part company on the class `_grafana_stored_uid` returns None for: the
provisioner generates a uuid PER FILE, so a spelling delivered twice is stored twice and BOTH are
served. `trimmed` already asked the same question structurally (`held` only keys on a stored uid,
so `held.get(None, ())` is empty); this asks it out loud on the other tracker.

**THE ENGINE, RE-RUN UNEDITED AT MY HANDS, NOT READ OFF THE REVIEW'S LOG.**
`logs/builder-9ffc-r7-engine-recheck.log` — the review's own
`critic-9ffc-r6-empty-trim-repeat.py`, new container, pinned `grafana/grafana:13.1.0`: `za` uid
`""` twice **2/2 served**, `zb` U+00A0 twice **2/2 served**, `zc` a normal spelling twice **1/2** —
the calibration where round 6's sentence is TRUE. C0 clean (no shared title, no shared spelling
across providers), C4 both still take the title line and the lockout, C5 `zb` loud and `za` with no
uid line at all. **12/13, the same single MISS** — that review's own prediction that the uid row
would say `none is lost` over `""`; it is SILENT there instead.

**RED FIRST, AND THE PRE-EDIT RUN IS KEPT.** `logs/red-9ffc.py` grew R11a/R11b (the two members of
the class, four checks each). `logs/builder-9ffc-r7-red-pre.log` **35/39** against the shipped
`fb806621`: exactly the four new sentence checks MISS and all 35 earlier checks pass. Post-edit
`logs/builder-9ffc-r7-red-post.log` **39/39** — R10a..R10h unchanged, and R11's `-the-lockout-claim-
still-stands` / `-the-two-rows-agree-on-one-output` pass in BOTH runs, which is what makes the RED
the SENTENCE and not the verdict.

**GREEN.** `logs/builder-9ffc-r7-gate.log` **GATE PASS 36/36 rc=0** (pre-edit baseline
`logs/builder-9ffc-r7-pre-gate.log`, also 36/36). Guard `fb806621` → `0edd1b25`.

**THE REVIEW'S REPAIR PROBE, RE-RUN UNEDITED BEFORE SHIPPING** —
`logs/builder-9ffc-r7-repair-probe-recheck.log` **9/9** against `fb806621`: P1/P2 flip to `grafana
serves all 2 of them`, P3/P4/P5 byte-identical. Run AGAIN after shipping
(`…-repair-probe-post.log`) it is rc=1 and says so in its own words — its BEFORE anchor is round 6's
comprehension, which is no longer in the file. That is the repair landing, not collateral.

**COLLATERAL, AND ONE FAILURE ATTRIBUTED RATHER THAN ASSERTED.**
`logs/builder-9ffc-r7-red-9ffc-pre-guard-recheck.log` **7/7**.
`critic-9ffc-r3-fence-at-the-guard` is **3/7** — round 6 recorded the same 3/7 and I did not take
that on trust: `logs/builder-9ffc-r7-fence-harness-attribution.py` / `.log` **4/4** runs it over the
shipped file AND over a tempdir copy with round 7's edit REVERSED (whose sha is `fb80662176b0`, the
review's file, byte for byte) — identical rc, identical four MISSes, G1..G4. Its needle is `grafana
serves both`, a phrase ROUND 6 removed; the live successors of those four rows are R8a..R8d /
R9a/R9b in `red-9ffc.py`, green.

**NOT DONE:** no commit (HEAD `7e9c426`), no `just play`, no live call, no vault value, nothing
under `ansible/` written, no other hat's harness edited, no task created or closed, gates 1b/2b/3b/4d
untouched — **4d is still the highest-value action available to anyone on this objective** — no
leftover container (`podman ps -a` clean).

### 2026-08-01 — Builder, `9ffc` REWORK round 8 (review.rejected F1 → THE SCOPE OF THE TWO TRACKERS)

**THE EDIT.** `claimed` and `held` stay GLOBAL — the engine's dedupe and its store both are — and
each now keeps the FILES it counted instead of a count, so the sentence they gate can ask whether
the collision's other claimant is in THIS folder+title group. `repeated` and `trimmed` are scoped to
the group; a claimant OUTSIDE it gets a third sentence of its own (DEC-188) and is NAMED (DEC-189).
Guard `0edd1b25f166` → `730008d0ef74`.

**RED FIRST, AND THE PRE RUN IS AGAINST THE PRE-EDIT GUARD AND THE FINAL ASSERTIONS.**
`logs/builder-9ffc-r8-red-pre-mirror.py` mirrors the repo into a tempdir, REVERSES this round's
edits there — the reversal's sha is `0edd1b25f166`, the exact byte string the round-7 review
measured, which is what proves the reversal complete — and runs the FINAL `red-9ffc.py` against it:
`logs/builder-9ffc-r8-red-pre.log` **43/49**, the six new R12 assertions MISS.
`logs/builder-9ffc-r8-red-post.log` **49/49**. R12c (the in-group repeat) and R12d (the no-address
class across the boundary) pass in BOTH runs — the calibrations the fence must not move.

**THE IDENTITY, MEASURED RATHER THAN ADOPTED.** `logs/builder-9ffc-r8-identity-probe.py` / `.log`
**9/9**: one tree, two spellings of the outside file's src basename, three guards (round 7's, the
review's repair verbatim, round 8's). I2-N — the review's `src.name` identity with the outsider
renamed to a group member's basename — prints `grafana does NOT serve all 2 of them` again. The
dest identity does not move (I2-D), and I1-D/I2-D are byte-identical but for the outsider's name.

**GREEN.** `logs/builder-9ffc-r8-gate.log` **GATE PASS 36/36 rc=0**.

**COLLATERAL, ATTRIBUTED RATHER THAN ASSERTED.** `logs/builder-9ffc-r8-collateral.log`:
`critic-9ffc-r3-fence-at-the-guard` is 3/7 with the SAME four MISSes it had before round 7;
`red-9ffc-pre-guard` 7/7; eleven `red-579d-*` harnesses answer IDENTICALLY over round 7's guard and
round 8's. The two that MOVED are both anchored on the TEXT this round replaced, not on any verdict:
`critic-9ffc-r7-repair-probe` (the review's own — its BEFORE anchor is gone, which is the repair
landing) and `builder-9ffc-r7-fence-harness-attribution` (it reverses round 7's edit).

**NOT DONE:** no commit (HEAD `7e9c426`), no `just play`, no live call, no vault value, nothing under
`ansible/` written, no other hat's harness edited, no task created or closed, no container run, gates
1b/2b/3b/4d untouched — **4d is still the highest-value action available to anyone on this
objective**.

## 2026-08-01 — Builder, `9ffc` REWORK round 9 (review.rejected F1 → THE `SILENTLY` HALF IS A WHOLE-LOG CLAIM)

**THE INCREMENT.** `test_delivered_dashboards_have_distinct_titles`' trim branch closed with
"SILENTLY: the engine prints no uid line of any kind for this half". Round 8 scoped the QUESTION
to the folder+title group on both lists and left that SENTENCE at the container's scope. One new
comprehension re-asks it there — `loud_trim = sorted({u for u in trimmed if len(claimed[u]) > 1})`,
which IS the engine's dedupe predicate because `claimed` was deliberately kept GLOBAL — and the
silence is claimed only where that list is empty; otherwise the spelling is NAMED and the operator
is sent to `the same UID is used more than once`. Guard `730008d0ef74` → `e810391f7670`.

**RED FIRST, AND THE PRE RUN IS THE FINAL HARNESS AGAINST THE PRE-EDIT GUARD.** The twelve R13
assertions were written and settled BEFORE the guard was touched, so the pre and post runs differ in
the guard and in nothing else: `logs/builder-9ffc-r9-red-pre.log` **57/61** with exactly four MISSes
— `R13a/R13b-the-silence-claim-is-gone` and `-and-the-engine-is-quoted-on-the-spelling-it-names` —
and `logs/builder-9ffc-r9-red-post.log` **61/61**. R13c, the calibration, passes in BOTH runs.

**TWO MEMBERS AND A CONTROL, ON A CARRIER NO ROUND HAD.** R13a/R13b put the group on ONE address
(`r13share` and `r13share`+U+00A0) and give the outside plex dashboard first one spelling and then
the OTHER, verbatim — so the predicate is shown to be per-SPELLING and not a property of the group,
and the sentence names only the repeated one where `trimmed` holds both. R13c is the same tree with
the outsider on an unrelated address: `SILENTLY` is kept, and `shared` is absent. The review's own
carrier is a FOUR-file tree; these are the repo's three, so the two runs are independent.

**ANOTHER HAT'S HARNESSES, RE-RUN UNEDITED AT MY HANDS.**
`logs/builder-9ffc-r9-engine-recheck.log` **13/13** — the review's `critic-9ffc-r8-crossgroup-repeat`
in my own container on the pinned `grafana/grafana:13.1.0`: C1/C2 the loud line naming the spelling,
C3 the anti-vacuity control silent in that same container. `logs/builder-9ffc-r9-repair-probe-recheck.log`
**10/10** — their repair probe against the shipped `730008d0ef74` BEFORE this round's edit, so their
run and mine are one measurement rather than two logs joined by prose.

**THE EXECUTABLE DELTA, AS A CHECK.** `logs/builder-9ffc-r9-pre-guard.py --ast` rebuilds the
pre-edit text BY SHA (`730008d0ef74`, asserted) by inverting this round's own edits, and prints the
whole runnable change with docstrings stripped: **3 lines** — the new comprehension and the sentence
it gates. Everything else this round wrote is prose.

**GREEN.** `logs/builder-9ffc-r9-gate.log` **GATE PASS 36/36 rc=0**, guard PASS 22/22, the delivered
tree `problems=[]`.

**COLLATERAL, ATTRIBUTED — AND ONE PREDICTION REFUTED.** `logs/builder-9ffc-r9-collateral.log` runs
eight sibling harnesses UNEDITED against round 8's guard (rebuilt in a mirror) and round 9's. Five
answer identically. `critic-9ffc-r8-repair-probe` goes anchor-dead here and is 10/10 in the mirror —
that is this round taking its repair. `red-579d-r12-pre-guard` moves its reconstruction sha, as it
did in round 8, and was already failing. **`builder-9ffc-r8-red-pre-mirror` MOVED, against my written
prediction**: it replaces the whole clause span, but this round's docstring and comment edits are
OUTSIDE that span, so it now reverses to `ad5d2033f2b2` instead of round 7's `0edd1b25f166`. It is
superseded by `builder-9ffc-r9-pre-guard.py`, the same way rounds 6 and 7's probes were.

**NOT DONE:** no commit (HEAD `7e9c426`), no `just play`, no live call, nothing under `ansible/`
written, no other hat's harness edited, no task created or closed, gates 1b/2b/3b/4d untouched —
**4d is still the highest-value action available to anyone on this objective**.

## 2026-08-01 — Builder, `9ffc` REWORK round 10 (review.rejected F1 → THE CLOSING CLAUSE'S ATTRIBUTION)

**TASK.** `task-1785601096-9ffc`, key `code-assist:plex-monitoring:guard:duplicate-title-provider-lockout`.
Round 9's `loud_trim` half is right and the review could not break it; what shipped beside it was a
THIRD claim — "It is the OTHER claimant's doing and not this pair's, so the line names a uid these
two files do not lose a file to" — false on both halves by construction. DEC-191.

**THEIR EVIDENCE, RE-RUN UNEDITED AT MY HANDS AND BEFORE MY EDIT.**
`logs/builder-9ffc-r10-review-harness-recheck.log` **17/17** — the review's own
`critic-9ffc-r9-loud-uid-is-the-address.py` in my own container on pinned `grafana/grafana:13.1.0`:
`qa` served 1/3 with the survivor the OUTSIDER, `qb` the mirror, `qc` the anti-vacuity control
silent at 2/3 in that same run. Their container and mine are ONE measurement.

**RED FIRST.** `logs/builder-9ffc-r10-red-pre.log` **67/73** against the pre-edit guard
`e810391f7670` — six MISSes, and they are exactly the six new claims (R13a/R13b × 2, R14a × 2).
Post: `logs/builder-9ffc-r10-red-post.log` **73/73**.

**THE CARRIER NO ROUND HAD: A GROUP OF THREE.** R14 delivers a FOURTH dashboard by appending one
`copy:` task in the tempdir (`red-579d-r12.py`'s idiom), so the group is all three delivered files
under one title and the outsider is a fourth. It caught a second half of the same defect the review
did not name: the shipped clause said "these two files" over a group of THREE — the arity class
mem-1785607757-192f names. R14b is the control in that same shape: the outsider on an unrelated
address, `loud_trim` empty, the SILENT sentence back byte-identical.

**THE EXECUTABLE DELTA, AS A CHECK.** `logs/builder-9ffc-r10-pre-guard.py --ast` rebuilds the
pre-edit text BY SHA (`e810391f7670`, asserted) and prints the whole runnable change with docstrings
stripped: **ONE string constant**, the closing clause of the loud branch. The comment block beside it
cannot appear there at all, which is what makes "the rest is prose" a check. Shipped `642465a454da`.

**GREEN.** `logs/builder-9ffc-r10-gate.log` **GATE PASS 36/36 rc=0**, guard PASS **22/22**, the
delivered tree `problems=[]`.

**COLLATERAL, ATTRIBUTED.** `logs/builder-9ffc-r10-collateral.log`: ten container-free siblings run
UNEDITED against both texts, **7 SAME, 3 MOVED** — and all three are anchored on a sha of this file
or on the exact text replaced, never on a verdict. `builder-9ffc-r9-pre-guard` goes anchor-dead here
and is 1/1 in the mirror: that is this round taking the repair, and it is why round 10 ships a
rebuild of its own. Post-edit, the review's own harness is **15/17**
(`logs/builder-9ffc-r10-review-harness-post.log`) — A2 is its finding-detector and A9 is a sha pin
on this file; every real file it reads is byte-identical in both of my runs.

**FILED, NOT BUILT.** `task-1785615546-0956` — the SILENCE claim's residual, handed over by the
review as explicitly unmeasured: a third spelling delivered twice OUTSIDE the group that trims onto
the group's address leaves `loud_trim` empty while the container carries a uid line about that
address. Four dashboards and three spellings on one address; nobody has delivered that tree.

**NOT DONE:** no commit (HEAD `7e9c426`), no `just play`, no live call, nothing under `ansible/`
written, no other hat's harness edited, no task closed, gates 1b/2b/3b/4d untouched — **4d is still
the highest-value action available to anyone on this objective**. No leftover container.

## 2026-08-01 — Builder, Step 9ffc REWORK round 11 (`review.rejected` → F1/F2, the `shared` paragraph)

`task-1785601096-9ffc`. The review re-ran round 10's edit and could not break it; what it
rejected is the paragraph round 10's new clause DEFERS TO, at :6079-6097, carrying both defects
one class each. Guard on disk before `642465a454da`, after **`63c864f5c91f`**. HEAD `7e9c426`,
nothing committed.

**RED FIRST — `logs/red-9ffc-r11.py`, pre-edit `8/13`** (`logs/builder-9ffc-r11-red-pre.log`),
post-edit **`13/13`** (`logs/builder-9ffc-r11-red-post.log`). Five rows moved, and the two
anti-vacuity controls were OK at BOTH ends.

- **A — the arity, as a CLASS.** Round 10's carrier `R14a-no-pronoun-hardcodes-a-pair` greps the
  absence of TWO literal spellings, and `the two files named here` was a THIRD. A1/A2/A3 scan
  the WHOLE printed paragraph with one regex and resolve every count-shaped noun phrase against
  `len(files)` — so the next pronoun in this class fails a row that is already written. A1 is the
  loud three-file group, A3 the same group on the `elif shared` branch (the paragraph is appended
  by BOTH), A2 the PAIR control, where a pair-shaped pronoun is the correct English and must stay.
- **B — a fact the row never asks.** `held` carries `(dest, src.name)`; nothing here ever compares
  the outsider's title to the group's. The group key is `(folder, saved)`, so with
  `foldersFromFilesStructure: true` the subdirectory IS the folder and a delivered file under the
  group's OWN title in another subdirectory is OUTSIDE the group and can claim its address. B1 is
  that tree, B2 the control with a genuinely different title — and **B3 is the proof no conditional
  could rescue the claim: the two verdicts are BYTE-IDENTICAL.** B4 keeps the fence on ONE clause:
  the claimant is still named, the address is still named, `So a file IS lost` still closes it.

**THE EXECUTABLE DELTA, AS A CHECK.** `logs/builder-9ffc-r11-pre-guard.py --ast` rebuilds the
pre-edit text BY SHA (`642465a454da`, asserted, landed) and prints the whole runnable change with
docstrings stripped: **ONE string constant** — the `shared` paragraph, carrying both repairs
(`delivered OUTSIDE this title group`, and `the {len(files)} files named here`). The comment block
beside it cannot appear there at all.

**GREEN.** `logs/builder-9ffc-r11-gate.log` **GATE PASS 36/36 rc=0**, guard PASS **22/22**, the
delivered tree `problems=[]`. `logs/red-9ffc.py` **73/73**.

**THE REVIEW'S OWN DETECTOR, AT MY HANDS.** `logs/builder-9ffc-r11-review-harness-recheck.log` —
`critic-9ffc-r10-shared-paragraph.py` run UNEDITED, **10/13**: its two FINDING rows `A3` and `B2`
now **MISS** (that is the repair) and `Z` misses on its sha pin (that is the edit); every control
row is OK, and **PART C at the engine is 4/4 on pinned `grafana/grafana:13.1.0`** — `pf` takes the
provider lockout, the title line counts `times=2` for the FOLDER only, the outside file is a real
claimant of the contested address, and `pg` is answered identically. No leftover container.

**COLLATERAL, ATTRIBUTED.** `logs/builder-9ffc-r11-collateral.log`: sixteen container-free siblings
run UNEDITED against both texts, **12 SAME, 4 MOVED** — and all four are anchored on a sha of this
file, none on a verdict. `builder-9ffc-r10-pre-guard` is 0/1 here and 1/1 in the mirror (this round
taking the repair, and why round 11 ships a rebuild of its own); `builder-9ffc-r10-collateral`
refuses to sweep the wrong pair, loudly. `builder-9ffc-r8-identity-probe` is **9/9 SAME**: the
grouping keys did not move.

**ONE HARNESS WAS EDITED AND IT IS DISCLOSED.** `logs/red-9ffc.py` greps the replaced sentence at
five sites — TWO positive (R14a's `the paragraph it points at is printed`, and the round-9 pairing
row's `the outside claimant is still named`) and THREE negative (R12c, R13c, R14b). Left alone the
two positives would have turned red and the three negatives VACUOUS, so all five were retargeted
onto the new spelling in the same edit, polarity untouched. It is therefore
NOT in the unedited sweep, and the sweep says so.

**NOT DONE:** no commit (HEAD `7e9c426`), no `just play`, no live call, nothing under `ansible/`
written, no task closed, gates 1b/2b/3b/4d untouched — **4d is still the highest-value action
available to anyone on this objective**.

## 2026-08-01 — Builder, task-1785601096-9ffc REWORK round 12 (`review.rejected` → the identity beside the boundary)

**THE FINDING, TAKEN WHOLE.** Round 11 moved the `shared` paragraph's clause onto the boundary the
row really holds (`d not in group` → "delivered OUTSIDE this title group"), and the review could
not break that half. What it left beside the new clause was the string that NAMES the claimant:
`f"{src_name} -> {d.rsplit('/', 1)[-1]}"`. The group key is `(folder, saved)`, so with
`foldersFromFilesStructure: true` the FOLDER is what puts a file outside the group — and
`rsplit("/", 1)[-1]` is the operation that deletes it. A sentence that asserts which side of a
boundary a file is on, printing a name with that boundary's coordinate cut off.

**THE EXECUTABLE CHANGE IS ONE F-STRING EXPRESSION**, to `d[len(DASHBOARDS_DIR):].strip("/")` — the
idiom already used for `folder` at the `titles` key, so the print and the key now agree on one
coordinate system. `logs/builder-9ffc-r12-pre-guard.py --ast` rebuilds the pre-edit text **BY SHA**
at `63c864f5c91f` and prints the delta: **2 lines, one expression**. Shipped `d6b928cb34f6`.

**RED FIRST — `logs/red-9ffc-r12.py`, 14/19 → 19/19.** Whole guard over tempdir trees.
E1 the identity: an outsider in `team-b/` from a src carrying a group member's basename onto that
member's dest basename printed `grafana-homelab-dashboard.json -> homelab.json`, BOTH halves
strings the verdict already prints as this group's own. E2 THE ARITY, asserted as a property and
not a spelling: `len(printed) == the number of out-of-group claimants the tree delivers` — five
delivered dashboards, three claimants on one address, ONE entry printed. E3 the control that
isolates the cause (distinct dest basenames printed two entries all along, so the collapse is the
truncation and not the set). E4 the fence on the repair itself: on the FLAT tree this repo actually
ships the identity must still be exactly `outsider.json` — a repair that printed `d` whole would
pass E1/E2/E3 and put the machine's filesystem layout in front of the operator on every real run.
E5 re-asks round 11's two fences on all four trees. Pre-edit: exactly the five new claims MISS,
every control and both fences OK.

**THE REVIEW'S OWN DETECTOR, RUN AT MY HANDS, BEFORE AND AFTER.**
`logs/critic-9ffc-r11-outside-identity.py` unedited: **10/10 pre** (`…-review-harness-pre.log`) →
**5/10 post** (`…-review-harness-post.log`), with its four FINDING rows and its sha pin MISSing and
**every control OK**. That is the repair landing, measured by the harness that raised it.

**NOTHING ELSE MOVED.** `just test` **GATE PASS 36/36 rc=0** (`logs/builder-9ffc-r12-gate.log`),
the row itself `OK: 3 delivered dashboard(s) carry 3 distinct title(s) in 1 folder(s)
(problems=[])`. `red-9ffc.py` **73/73**, `red-9ffc-r11.py` **13/13** — both unedited this round,
which is why both are IN the sweep for the first time.

**COLLATERAL, ATTRIBUTED.** `logs/builder-9ffc-r12-collateral.log`: twenty-three container-free
siblings run UNEDITED against both texts, **16 SAME, 7 MOVED, 0 unexpected**. Every mover is either
this round's own detector (`red-9ffc-r12`, `critic-9ffc-r11-outside-identity`) or a harness that
echoes a sha of this file — the latter class differs only in a digest, with identical rc and
identical sentence, and both lines are printed for each. `builder-9ffc-r8-identity-probe` is **9/9
SAME**: no grouping key moved, only a printed string.

**PROSE KEPT HONEST.** DEC-189's `I2-D-still-names-the-outsider-unambiguously` clause is the claim
D1 refutes, so it is amended in the same commit rather than left to disagree with the file; DEC-192
records the decision, the three refused alternatives, and the 8 points it does not claim.

**NOT DONE:** no commit (HEAD `7e9c426`), no `just play`, no live call, nothing under `ansible/`
written, no task closed, gates 1b/2b/3b/4d untouched — **4d is still the highest-value action
available to anyone on this objective**.

---

## 2026-08-01 — Builder, `task-1785601096-9ffc` ROUND 13 (`review.rejected` → F1: the group's OWN members)

**THE FINDING, TAKEN WHOLE.** Round 12 carried the folder onto the out-of-group claimant and the
review could not break it; the same `bad.append` holds a SECOND identity and it was never asked.
`names = sorted(name for name, _title, _uid, _dest in files)` is `src.name`, a BASENAME — the thing
this row's own comment at :5889-5894 calls unusable as an identity, applies to `claimed`, and then
prints the group's members by anyway, with `_dest` unpacked in the comprehension that discards it.

**RED FIRST, AND IT MOVES 12/20 → 20/20.** `logs/red-9ffc-r13.py`, the WHOLE guard over tempdir
trees. Pre-edit log is the harness run UNEDITED against round 12's text in a mirror
(`…-red-pre.log`, guard sha `d6b928cb34f6`): **exactly the eight new claims MISS, every control and
both inherited fences OK**. Post-edit **20/20** (`…-red-post.log`).
D1 two srcs under `files/nested-x` and `files/nested-y`, one basename, one title, distinct legal
uids, distinct dests → `delivered by ['dup-dashboard.json', 'dup-dashboard.json']`, and it is
**1/22, the only failing row on the tree**, so that sentence is all the operator gets. D2 needs no
nesting: `root = TEMPLATES if is_template else FILES`, so a `copy:` and a `template:` task with two
FLAT srcs of one basename collapse identically — the layout this repo ships. D3 the contrast in one
verdict: the outsider is named `src -> team-b/out.json` (round 12 working) while the two files the
sentence is ABOUT are indistinguishable. D4/D5 the two branches — a non-colliding member prints
byte-identically, and D5 holds both branches in ONE verdict. D6 the fence on the repair: the dest is
cut at `DASHBOARDS_DIR`, so no absolute path and no project dir ever reaches the operator. D7 the
tree as delivered stays GREEN.

**THE REVIEW'S OWN DETECTOR, UNEDITED AT MY HANDS.**
`logs/critic-9ffc-r12-group-member-identity.py`: **12/12 → 8/12**
(`…-review-harness-post.log`), its three FINDING rows and its sha pin MISSing, **every control OK**.

**THE EDIT IS THREE LINES AND IT IS REVERSIBLE BY SHA.** `logs/builder-9ffc-r13-pre-guard.py --ast`
rebuilds the pre-edit text and lands on round 12's `d6b928cb34f6` exactly; the executable delta is
one assignment split in two (`…-pre-guard.log`). Shipped text is now `9c61b6112215`.

**NOTHING ELSE MOVED.** `just test` **GATE PASS 36/36 rc=0** (`…-gate.log`); the guard standalone
**PASS 22/22** with the row itself `OK: 3 delivered dashboard(s) carry 3 distinct title(s) in 1
folder(s) (problems=[])`. `red-9ffc.py` **73/73**, `red-9ffc-r11.py` **13/13**, `red-9ffc-r12.py`
**19/19**, each re-run unedited.

**COLLATERAL, ATTRIBUTED** (`logs/builder-9ffc-r13-collateral.log`): twenty-seven container-free
siblings run UNEDITED against both texts, **18 SAME, 9 MOVED, 0 unexpected**. The three standing
REDs are SAME in both texts, which is the conditional-branch claim priced from the outside.
**DISCLOSED:** this round consumes a reversal anchor of `builder-9ffc-r8-red-pre-mirror.py` (the
`names` line), so that mirror and `builder-9ffc-r8-identity-probe.py` (9/9) now exit at `anchor not
unique (0)` against the shipped text — a chain going stale, not a claim failing: the probe is 9/9 in
the sweep's round-12 column and the chain still runs by composing round 13's rebuild first.
Retargeting either anchor was rejected (DEC-193): the new anchor would not exist in the round-12
text and would break the two-text sweep for both.

**NOT DONE:** no commit (HEAD `7e9c426`), no `just play`, no live call, nothing under `ansible/`
written, no task closed, gates 1b/2b/3b/4d untouched — **4d is still the highest-value action
available to anyone on this objective**.

## 2026-08-01 — Builder, Step 7 / `task-1785594766-fb36`: THE READABLE ROW ASKS ITS RULES IN THE ENGINE'S ORDER

`code-assist:plex-monitoring:guard:readable-row-rule-order`. Guard `9c61b6112215` → `881e2c620ddc`.
Six executable lines in one row, all inside `test_delivered_dashboards_parse_as_dashboards`.

**THE DEFECT WAS WIDER THAN THE ROW THAT OPENED IT.** The task named TWO directions from the
round-8 review's PART D (0/2). Delivering every ADJACENT PAIR of the installed order to the pinned
`grafana/grafana:13.1.0` in ONE run named **SIX** (`logs/red-fb36-pre.log`, guard `9c61b6112215`):
a blank-after-trim title with an illegal uid / with a uid TOO LONG / with a 5001-character title
and an illegal uid — the row named the **UID** for all three, the engine names the TITLE; and an
illegal uid + `1e400`, a uid too long + `1e400`, a blank title + `1e400` — the row named the
**NUMBER**, because the parse raised before any field was read. The three the task did not name are
the same defect at the same two sites.

**RED-FIRST, AND BOTH COLUMNS COME OFF ONE ENGINE RUN.** `logs/red-fb36.py` **PASS 60/60**
(`…-fb36.log`). PART A is the engine, one delivered file per carrier, container log kept, every
`error=` printed — and every carrier's answer was PREDICTED IN THE SOURCE before the run (16/16),
so PART A could have contradicted this round. PART B is anti-vacuity in that same run: the legal
control is served, each of the six rules ALONE is reached and named, and no single-rule carrier
reached the store. PART C scores the DELIVERED row against PART A's own answers, 14/14. PART R is
the RED record — the PRE-EDIT text rebuilt BY SHA in the same process, scored off the SAME engine
run (no cached answers, mem-1785601139-1394), naming exactly the six seams wrong and the eight
others right. `R-red-is-not-vacuous` asserts the six by name: were it empty the round repaired
nothing.

**THE REVIEW'S OWN BATTERY, UNEDITED AT MY HANDS.**
`logs/critic-579d-r8-uidlen-and-readable-row.py` **PASS 22/22**
(`…-fb36-recheck.log`) — its PART D **flips 0/2 → 2/2**, which is acceptance criterion (a), and
every PART A engine row and PART C `_unreadable` row is unmoved.

**REVERSIBLE BY SHA.** `logs/builder-fb36-pre-guard.py --ast` rebuilds the pre-edit text and lands
on `9c61b6112215` exactly; the executable delta is **6 lines**, all in the one row
(`…-pre-guard.log`).

**NOTHING ELSE MOVED.** `just test` **GATE PASS 36/36 rc=0** (`logs/builder-fb36-gate.log`); the
guard standalone **PASS 22/22** on the tree as delivered.

**COLLATERAL, ATTRIBUTED** (`logs/builder-fb36-collateral.log`, **23/23**). PART C: the presence
gate's `no top-level uid/title` and every SINGLE-rule sentence are **byte-identical across both
texts** — a reordering cannot move a document that breaks one rule, and that is measured rather
than argued, for every carrier the four sibling harnesses deliver (`red-step05d-rework-r10` S1/S2/S3,
`-r11` S1-S6, `critic-step05d-r9-title-provisionability` D2). PART K: the reconstruction chain is
**one link longer, not broken** — `builder-9ffc-r13-pre-guard.py` UNEDITED, pointed at this round's
pre-edit text, lands on `d6b928cb34f6` exactly, and lands elsewhere against the delivered text, so
the composition is doing the work.

**DISCLOSED, AND ALREADY PRICED (DEC-176).** This round consumes the reconstruction anchor of
`red-step05d-rework-r10-critic-recheck.py` (edit-3 opens on the row's first chain line) and of
`-r8-critic-recheck.py` (the parse call the deferral changes). PART N measures both against the
PRE-EDIT text first: they reconstruct `6defb9b0` and `85d342aa` against declared `10fd3cdb` and
`b3729aad` — **already the wrong bytes before this round ran**. The cost is an anchor on a
reconstruction whose sha was already lost, not a fact.

**ACCEPTANCE CRITERION (c) IS NOT MET AND WAS NOT MEETABLE — measured, not waved.**
`logs/red-579d-r9-recheck-chain.py` and its r10/r11 successors, and `-r9-critic-recheck.py`, all
fail at their FIRST link, and PART Q shows the outcome is **identical on the pre-edit and the
delivered text**: thirteen rounds of `9ffc` moved their input revision long before this round. The
chain that does close through this edit is PART K's composition.

**NOT DONE:** no commit (HEAD `7e9c426`), no `just play`, no live call, nothing under `ansible/`
written, no task closed, gates 1b/2b/3b/4d untouched — **4d remains the highest-value action on
this objective**.

## 2026-08-01 — Builder, Step 7 / `task-1785594766-fb36` ROUND 2 (`review.rejected` → the uid link is TWO HALVES)

**THE FINDING, REPRODUCED AT MY HANDS BEFORE IT WAS REPAIRED.** The review's basis is that round 9
put the whole of `_grafana_short_uid_defect` in the engine's 4th slot, and **two of that
predicate's four members are not refusals**: a NON-STRING uid and a uid that is only
`GRAFANA_SHORT_UID_TRIM` are SAVED under a generated uuid, which the predicate's own returned
sentence says verbatim. `logs/builder-fb36-r2-red-pre.log` — **FAIL 40/44**, one delivered file per
carrier in ONE provisioning run on the pinned `grafana/grafana:13.1.0`, `/api/search` read back —
and the four MISSes are exactly the four the review named:
`C-nonstr_uid_num`, `C-trimuid_num`, `C-nonstr_uid_tag`, `C-trimuid_tag`. Every engine prediction
in that run was written down before it and all 15 landed (PART A), including `nonstr_uid_alone`
and `trimuid_alone` at `-` — **and both are IN THE STORE afterwards** (PART B), which is what makes
those members non-refusals rather than refusals the run failed to trigger.

**THE REPAIR IS AN ORDERING, NOT A DELETION** (mem: flip a guard's polarity, never delete it), and
it is three executable lines:

```python
uid = doc.get("uid")
refuses_uid = isinstance(uid, str) and _grafana_stored_uid(uid) is not None
defect = (_grafana_title_defect(doc.get("title"))
          or (_grafana_short_uid_defect(uid) if refuses_uid else None)   # 4th: the REFUSING half
          or (None if number is None else f"{number}")
          or _grafana_tags_defect(doc.get("tags"))
          or _grafana_short_uid_defect(uid))                             # LAST: the two that save
```

`_grafana_stored_uid(uid) is not None` is exactly the line between the halves — None for both
non-refusals, a string for both refusals — so no member is asked twice and none is dropped.

**GREEN, both texts off ONE engine run.** `logs/builder-fb36-r2-red-post.log` **PASS 60/60**: all
four finding carriers now name what the engine named; the row is still **RED** for each
non-refusing member alone with the predicate's own "saves it at an address nothing in this repo can
name" sentence (PART U); `R-repair-moves-only-the-finding` — the answer changes on those four
carriers **and on nothing else**. The pre-repair column is `881e2c620ddc` rebuilt BY SHA in the
same process (`logs/builder-fb36-r2-pre-guard.py`, `--ast`: **4 executable lines**, all inside this
one row).

**BACKPRESSURE.** `just test` **GATE PASS 36/36 rc=0** (`logs/builder-fb36-r2-gate.log`); the guard
standalone **PASS 22/22** on the tree as delivered.

**COLLATERAL** (`logs/builder-fb36-r2-collateral.log`, **28/28**). PART C: every single-rule
carrier a sibling harness reads by substring — and both moved members alone — print a
**byte-identical line and rc** on the two texts. PART K: the reversal chain is now **three links**,
`a70d851ce802 → 881e2c620ddc → 9c61b6112215 → d6b928cb34f6`, every predecessor imported UNEDITED
and each link asserted at its own declared value. PART N — **the one anchor this round costs**:
`logs/builder-fb36-pre-guard.py` can no longer reverse from the real tree (its expression anchor is
the chain this round rewrote); it stops at the anchor rather than landing elsewhere, and PART K is
the repair. PART S: the reviewer's harness imported UNEDITED — `_unreadable` still names the NUMBER
for `uid: 42` + `1e400`, and the critic's own `C-second-spelling-lacks-it` row **INVERTS**, which is
the finding closing at the needle it was scored on. PART Q: the two DEC-176 anchors and the three
579d recheck chains behave identically on both texts — this round costs them nothing further.

**FILED, NOT BATCHED.** `_unreadable`'s chain fences the same predicate with `isinstance(uid, str)`
only — half of this line — so the TRIM-CLASS member is still ahead of the number in that first
spelling. Its carriers are a separate measurement and it is named in the comment rather than
repaired here.

**NOT DONE:** no commit (HEAD `7e9c426`), no `just play`, no live call, nothing under `ansible/`
written (PART Z byte-identical at both ends of both runs), no task closed, gates 1b/2b/3b/4d
untouched — **4d remains the highest-value action on this objective**.

## Step 9 / `task-1785624345-a15c` ROUND 2 — Builder, `review.rejected` (PROSE ONLY)

**THE VERDICT I CONSUMED.** Round 1's increment was accepted on the merits and rejected for TWO
SENTENCES THE EDIT DID NOT MOVE, both false of the code beside them at `54cec7fc4cea`
(`logs/critic-a15c-stale-sentences.py` 11/11): (1) `_unreadable`'s OWN docstring still said the
NON-STRING branch is "DELIBERATELY NOT CONSULTED" and handed the class to "the second sentence"
(`elif rune:`), a design the function no longer has and a branch the class can no longer reach;
(2) the sibling's cross-reference in `test_delivered_dashboards_parse_as_dashboards` still described
`_unreadable` as fenced with `isinstance(uid, str)` and the repair as "FILED RATHER THAN REPAIRED
here" — a STATUS claim about landed work, and the very comment this task's description cites as the
deferral's record.

**WHAT I WROTE.** `scripts/test_grafana_provisioning_shape.py` `54cec7fc4cea -> 8cb7299e4568`, two
prose blocks: the `:1271` paragraph now states the split the code HAS (the refusing half in the
engine's 4th slot, the WHOLE predicate LAST after the tag, `log=None` reading into its own clause)
and points at that fourth sentence instead of `elif rune:`; the `:5421` comment records the FIRST
spelling as REPAIRED by `a15c`, with its carrier set.

**RED FIRST** (`logs/builder-a15c-r2-red.py`, pre `4/21` -> post **21/21**;
`logs/builder-a15c-r2-red-pre.log` / `-post.log`). Every replacement sentence is SCORED against the
code beside it, not merely matched: the 4th-slot ordinal is the one the measured table above
`GRAFANA_LOG_SAVE` gives the save-time uid (B2), the chain's last entry and the tag before it are
read off the AST (B3), the `log=None` arity is exactly ONE entry so no refusal can reach the fourth
sentence (B4), and the retained half of the old paragraph is re-measured — U+FFFD substitution
leaves a non-string uid an `int`, so the class arrives AS AUTHORED (B8).

**INERTNESS — THE AST IS THE ORACLE** (PART D). `logs/builder-a15c-r2-pre-guard.py` rebuilds
`54cec7fc4cea` by inverse edit and CHAINS through round 1's reversal to `9c08e2b54dc2`. With every
docstring normalised to a placeholder the two trees `ast.dump` **IDENTICAL** — which is the whole of
edit 2, since a comment never reaches the parser — and exactly ONE docstring differs, `_unreadable`'s,
admitted by name. The five-entry chain unparses character-identical at both texts.

**BACKPRESSURE.** `just test` **GATE PASS 36/36 rc=0** (`logs/builder-a15c-r2-gate.log`); the guard
standalone **PASS 22/22** on the tree as delivered. Round 1's own container battery re-run at the
new sha: `logs/builder-a15c-red.py` **65/65** (`logs/builder-a15c-r2-red-a15c-recheck.log`), one
delivered file per adjacent pair in ONE run on the pinned `grafana/grafana:13.1.0`, PART F agreement
and PART Z intact.

**COLLATERAL** (`logs/builder-a15c-r2-collateral.log`, **10/10**) — and the census's own PROXY
failed first, which is the finding worth keeping. Counting string literals in the guard SOURCE named
five 579d harnesses as casualties for `SERVES = "the dashboard it serves is not the one on disk"`.
They are not: they match it against `_unreadable`'s RETURN VALUE, the `elif rune:` clause assembles
it from two f-string fragments, and the contiguous spelling existed in the source ONLY inside the
paragraph this round rewrote. PART B settles it by measurement — the same 11-carrier battery, one
per clause of the row, run through BOTH texts with every sentence byte-identical. PART C measures
the two reversal chains at all THREE texts: `red-579d-r6/r7-pre-guard.py` have the IDENTICAL set of
missing pairs at `9c08e2b54dc2`, `54cec7fc4cea` and the delivered text, so round 2 costs them no
link they still had. PART D: the review's own harness falls 11/11 -> **7/11** on EXACTLY the four
rows that quote the stale prose; its seven CODE rows all hold.

**NOT DONE:** no commit (HEAD `7e9c426`), no `just play`, no live call, no vault value, nothing
under `ansible/` written, no task created or closed, no other hat's harness edited, gates 1b/2b/3b/4d
untouched — **4d (`task-1785442499-1851`, P1, OPERATOR ONLY) remains the highest-value action on
this objective**.

## Step 9 — task-1785624345-a15c ROUND 3 (`review.rejected`, ONE COMMENT CLAUSE) — 2026-08-02

Guard `8cb7299e4568` -> `821b687f6267`. **Zero executable lines, zero docstrings, six comment
lines in one hunk.**

**WHAT WAS WRONG.** Round 2's new sibling cross-reference closed with "`PART F` prints the two
spellings agreeing on **both sets**". `logs/builder-a15c-red.py`'s own docstring scopes that part to
"on every carrier in **this** set", and the second set is not merely unmeasured — it is UNPRINTABLE
by that instrument: the sibling reaches `_unreadable` only on the `raw is None` branch and that
branch `continue`s, so one delivered file is in exactly ONE of the two chains' inputs. A
cross-reference inherits the cited harness's scope sentence (mem-1785634271-3a8f).

**THE REPAIR** is the scope AND the reason the scope is enough: PART F is cited for "every carrier
in THAT set, which is every carrier it has", the readable set is named as OWED ("needs its own
carriers and its own run"), and the disjointness is given as the reason.

**RED FIRST** (`logs/builder-a15c-r3-red.py`, pre **13/24** -> post **25/25**;
`-red-pre.log` / `-red-post.log`). Not a spell-check: PART B derives the cited PART's scope sentence
from ITS OWN docstring and matches it against the citing one modulo the demonstrative (the diff
mem-1785634271-3a8f asks for, run rather than eyeballed); PART C re-derives all 13 carriers by
importing the harness and shows all 14 blobs, control included, fail UTF-8 decoding; PART D measures
the disjointness off the AST **and** off `_read` (the same document is in the readable set, and with
one raw `0xff` is in `_unreadable`'s — never both); PART E reads the cited run's own log.

**INERTNESS.** `logs/builder-a15c-r3-pre-guard.py` rebuilds `8cb7299e4568` by inverse edit and
composes round 2's and round 1's reversers to reach `54cec7fc4cea` and `9c08e2b54dc2`. The two trees
`ast.dump` **IDENTICAL with no docstring normalisation** — this round moved neither code nor a
docstring — and the line diff is 6 lines, every one a `#` comment inside the sibling's own byte
range (5271-5475).

**BACKPRESSURE.** `just test` **GATE PASS 36/36 rc=0** (`logs/builder-a15c-r3-gate.log`); guard
standalone **PASS 22/22**; round 1's container battery re-run at the delivered sha —
`logs/builder-a15c-red.py` **65/65**, PART Z pinning `821b687f6267`
(`logs/builder-a15c-r3-red-a15c-recheck.log`). Round 1's review harness
`logs/critic-a15c-stale-sentences.py` is **7/11**, unmoved from round 2.

**COLLATERAL** (`logs/builder-a15c-r3-collateral.log`, **16/16**). This round is the MIRROR IMAGE of
round 2's proxy failure: the retired clause is a COMMENT, so it is a real source anchor (in the
source once, in NO sentence the row can print — PART B still runs the 11-carrier voice battery at
both texts to prove it). Two files quote it: the round-2 review's own harness (DELIBERATE — its
`CLAIM` **is** that sentence) and `logs/builder-a15c-r2-pre-guard.py`. **And a functional dependency
is not a literal:** four harnesses import or shell out to round 2's reverser, so PART E does not
count them, it RE-RUNS them in a mirror tree whose `scripts/` holds the rebuilt `8cb7299e4568`
(`.py` copied not symlinked, because `resolve()` walks a symlink back to the real repo). All four
score the verdict they score there today — 21/21, 9/10 (the 9/10 the round-2 review itself reported,
its one casualty asserted by name), 15/15, 14/14 — so what round 3 costs them is a POINTER, not a
measurement, and PART C shows the pointer restored by composition.

**NOT DONE:** no commit (HEAD `7e9c426`), no `just play`, no live call, no vault value, nothing
under `ansible/` written, no task created or closed, no other hat's harness edited, gates 1b/2b/3b/4d
untouched — **4d (`task-1785442499-1851`, P1, OPERATOR ONLY) remains the highest-value action on
this objective and no agent may close it**.

---

## 2026-08-02 — Builder, Step 9 / `a15c` ROUND 4 (review.rejected — THREE CLAIMS IN ONE COMMENT CLAUSE)

**TASK** `task-1785624345-a15c` (`code-assist:plex-monitoring:guard:unreadable-chain-uid-halves`).
Guard `821b687f6267` -> `6bbd6944da50`. **Twelve comment lines in ONE hunk**; no executable line, no
docstring. The round-3 review verified everything else itself and I did not re-litigate DEC-202.

**THE THREE REPAIRS, ALL IN THE SIBLING'S CROSS-REFERENCE.**
1. **A DISJOINTNESS IS NOT A PARTITION.** Round 3 shipped "so one delivered file is in exactly ONE
   of them"; the premise (`_unreadable` only under `raw is None`, which `continue`s) gives at most
   one. Now: "so no delivered file is in BOTH", **plus the class that falls through the middle** —
   the two further `continue` exits (the parse `except`, `not isinstance(doc, dict)`) leave a file
   that DECODES but never becomes an object in NEITHER set, cited to `critic-a15c-r3-neither-set.py`.
2. **THE COUNT.** "which is every carrier it has" was 13 of 14 (PART F iterates the 13 `CASES`; the
   14th blob is the legal control) -> "all 13 rule carriers".
3. **THE DEFERRAL IS NOW A ROW.** Banked `task-1785635701-d2fd`
   (`code-assist:plex-monitoring:guard:unreadable-acceptance-b-readable-set`, P3, open) for
   acceptance (b)'s readable half, and the clause cites the id. No new prose deferral ships.

**RED FIRST** (`logs/builder-a15c-r4-red.py`, **13/26 -> 26/26**;
`-red-pre.log` / `-red-post.log`). Not a spell-check: PART B reads the 13/14 off
`builder-a15c-red.py` BY IMPORTING IT and off round 3's own C2 row; PART C reads the banked row out
of `.ralph/agent/tasks.jsonl` and requires it open, keyed, NOT this task, and naming the work;
PART D measures "not a partition" twice — the AST exit-count between the two consumers
(2, at `:5347`/`:5389`), then the REAL row over a mirror tree with **both sets as anti-vacuity
controls** (3 chain/0 unreadable GREEN; 0/3 with one raw `0xff` RED; **0/0** for three delivered
top-level arrays, RED, every file named). The spy carries a **re-entrancy flag** — `_unreadable`
calls `_grafana_title_defect` itself, so an unguarded spy prints 3/3 and reads as a refutation
(mem-1785635541-2a06).

**INERTNESS.** `logs/builder-a15c-r4-pre-guard.py` rebuilds `821b687f6267` and **composes** round
3's reverser, reaching `8cb7299e4568`, `54cec7fc4cea` and `9c08e2b54dc2` — four texts from one call.
`ast.dump` **IDENTICAL with no docstring normalisation**; the line diff is 12 lines, every one a `#`
comment inside the sibling's own byte range (5271-5479).

**BACKPRESSURE.** `just test` **GATE PASS 36/36 rc=0** (`logs/builder-a15c-r4-gate.log`); guard
standalone **PASS 22/22** (`-guard.log`); round 1's container battery re-run at the delivered sha —
`logs/builder-a15c-red.py` **65/65**, PART Z pinning `6bbd6944da50`
(`logs/builder-a15c-r4-red-a15c-recheck.log`). Round 1's review harness
`logs/critic-a15c-stale-sentences.py` **7/11**, unmoved from round 3.

**COLLATERAL** (`logs/builder-a15c-r4-collateral.log`, **18/18**). Both retired sentences are
COMMENTS, so the source count is the right instrument — PART B still runs the 11-carrier voice
battery at both texts and every sentence is byte-identical. Two DELIBERATE flips, and both are the
review's own work: `critic-a15c-r3-neither-set.py` 13/13 -> **10/13** and `builder-a15c-r3-red.py`
25/25 -> **16/25**, with the red rows asserted **BY NAME** rather than by count. Round 3's census
cannot RUN here at all (it imports round 3's reverser) — a POINTER, and PART E answers all three by
RE-RUNNING them in a mirror tree at the rebuilt `821b687f6267`: **25/25, 16/16, 13/13**. One row was
rewritten mid-round after it caught me: attribution is **not monotone**, so `delivered == pre-r3` was
the wrong equality for `builder-a15c-r2-pre-guard.py` (its pair 1 runs ONLY at `8cb7299e4568`, and
round 3 is what cost it). The claim round 4 may make is `delivered == pre-r4`, and the row now prints
which text each missing pair still runs at.

**NOT DONE:** no commit (HEAD `7e9c426`), no `just play`, no live call, no vault value, nothing
written under `ansible/`, no task closed, no other hat's harness edited. One task CREATED —
`task-1785635701-d2fd`, the banked deferral the review asked for. Gates 1b/2b/3b/4d untouched —
**4d (`task-1785442499-1851`, P1, OPERATOR ONLY) remains the highest-value action on this objective
and no agent may close it**.

## 2026-08-02 — Builder, Step 10 / `task-1785634257-80de` (THE DOCSTRING LAYER — PROSE ONLY)

**THE ROW.** `_unreadable`'s docstring, the "AND THE CLAUSE IS EARNED BY THE CALLER" paragraph:
"`provisioned=` is passed by the five readers that iterate `_delivered_dashboards`, and by nothing
else." That is the paragraph's BLAST-RADIUS claim, and the AST says SIX. Re-derived here at the
delivered `56bba79ef94e` rather than adopted from the filer or the Planner: **7 `_unreadable(...)`
call sites, SIX pass `provisioned=`, ONE passes neither** (`test_dashboard_delivery_inventory_is_
complete`, the silent side, correct). The uncounted caller is `_delivered_dashboard_documents` — a
HELPER, not a test row — so the count was taken over ROWS and the sentence was written over CALLERS.

**THE REPAIR IS NOT 5→6 (acceptance (b), DEC-206).** It fixes the UNIT, names the helper, and carries
two more facts the sweep produced: the relative clause never narrowed to five OR six (**15** functions
call `_delivered_dashboards()`, only 7 reach `_unreadable`), and the radius does not stop at the
helper (it folds the sentence into `problems`, which **7** further rows print, and A6 proves the two
row sets DISJOINT — so **12** rows can carry the clause where 5 pass the keyword).

**RED FIRST** (`logs/builder-80de-r1-red.py`, **13/20 → 20/20**; `-red-pre.log` / `-red-post.log`).
PART B scores no digits: it BUILDS the four demanded sentences out of PART A's sweep, so if the AST
moves, the sentence the docstring must carry moves with it. PART C proves that in both directions
against two mutant trees — a caller ADDED (demand says seven), the helper's keyword REMOVED (five) —
with the unmutated tree as the control. The mutant anchor is the HELPER'S OWN BYTE RANGE: the call
text is identical at six sites, which is the fact under audit, so a whole-file replace would have
mutated the first ROW and scored the wrong direction.

**INERTNESS (acceptance (d)).** `logs/builder-80de-r1-pre-guard.py` rebuilds `56bba79ef94e` by
inverse edit and **composes** a15c round 4's living reverser: `821b687f6267`, `8cb7299e4568`,
`54cec7fc4cea`, `9c08e2b54dc2` — **five texts from one call**. The oracle is the one DEC-205
specified and NOT the raw dump the comment rounds used: docstring-NORMALISED `ast.dump` **IDENTICAL**
(`3645b089712e`), with a raw-dump-DIFFERS row beside it so the normalisation cannot hide a no-op, and
the changed set **ADMITTED BY NAME** — `['_unreadable']`, 12985 → 14003 chars, all 17 added lines
inside its own docstring span `:1144-1332`.

**COLLATERAL** (`logs/builder-80de-r1-collateral.log`, **16/16**). Census over 929 guard quotations in
305 files at BOTH texts: **927 LIVE, one 80DE-BROKE-IT** — `logs/red-579d-r4-critic-recheck.py`, the
harness the Planner handed over. The cost is a NAMED ROW and not a score: 9/16 → 8/16, **newly red
{`R5-unique`}** (its INVERSE pair 5 IS the retired sentence), **healed {}**; every other red row,
`R-sha` included, is a15c's bill and was red before this round opened. PART F answers the FUNCTIONAL
dependents, which a string census cannot reach: all three PIN the delivered sha, so all three redden
at any new text — `builder-a15c-r4-collateral.py` 18/18 → 11/18, `finalizer-a15c-r4-repair.py`
22/22 → 12/22, `builder-a15c-r4-pre-guard.py` rc 0 → 1. Re-run in a mirror at the text they pin they
score **exactly their own logs — 18/18, 22/22, rc=0** — so this round costs a POINTER, not a
measurement (attribution is not monotone; the claim this round may make is `delivered == pre-80de`).
F3 shows a15c's reverser still FUNCTIONALLY live at the new text. One instrument bug found and fixed
mid-round rather than billed to the round: the mirror needs `.ralph/` or
`logs/builder-a15c-r4-red.py` PART C cannot RUN and the finalizer harness reports 18/22 (DEC-207,
mem-1785639147-0a8d).

**BACKPRESSURE.** `just test` **GATE PASS 36/36 rc=0** (`logs/builder-80de-r1-gate.log`; baseline
`-gate-pre.log` 36/36 before the edit); guard standalone **PASS 22/22** (`-guard.log`). Delivered
guard `6973aa2769c5`. The docstring's own citation is GREEN at the sha it ships at
(mem-1785636803-90cb): it points at `logs/builder-80de-r1-red.py` PART A and `-red-post.log`, 20/20
at `6973aa2769c5`, and that harness's only dependency is `builder-80de-r1-pre-guard.py`, which is
rc=0 at the same sha.

**NOT DONE:** no commit (HEAD `7e9c426`), no `just play`, no live call, no vault value, no container,
nothing written under `ansible/`, no task closed or filed, no other hat's harness edited. Gates
1b/2b/3b/4d untouched — **4d (`task-1785442499-1851`, P1, OPERATOR ONLY) remains the highest-value
action on this objective and no agent may close it**.
