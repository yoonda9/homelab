# Idea Honing — Plex User Persistence

Requirements clarification Q&A for the rough idea: "Ensure plex user is the same across recreation of the container".

---

## Q1: Which "plex identity" must stay stable across CT recreation?

The repo shows two distinct things that both drift when CT 110 is recreated, and
"the plex user is the same" could reasonably mean either (or both):

- **A — The in-CT POSIX user/group (`plex` uid/gid).** The `plexmediaserver`
  package allocates `plex` from the dynamic system range at install time, so a
  rebuild can land on a different uid/gid. The bind-mounted state dir on
  `/tank/Server/AppData/plex` keeps its host-side ownership (`100999:100991`),
  so a drifted uid means PMS can no longer read its own library. This is what
  the existing ownership gate in `ansible/roles/plex/tasks/main.yml` detects.
- **B — The Plex *account*/server identity (claim token, server machine
  identifier, "this server" registration).** Recreating the CT can re-register
  the server with plex.tv as a new machine, losing shares/managed users even
  when the files are fine. `docs/runbooks/plex-claim.md` exists in the repo.
- **C — Both.**

**Answer:** **A — the in-CT POSIX `plex` user/group (uid/gid).**

The Plex account/server identity (claim token, machine identifier) is explicitly
**out of scope** for this project. Scope is: the `plex` uid/gid inside CT 110
must be deterministic across container recreation, so the bind-mounted state dir
on `/tank/Server/AppData/plex` stays readable by PMS without a re-chown.

_Alternatives considered: B (plex.tv server identity), C (both). Rejected as
out of scope for this pass._

---

## Q2: Does this project also remediate the currently-broken live CT 110, or only guarantee determinism going forward?

`scripts/verify_plex_state_ownership_gate.py` documents that CT 110's state dir
is *right now* sitting at raw ownership `65534` with PMS crash-looping, and that
the corrective `chown -R 100999:100991 /tank/Server/AppData/plex` is destructive
on a live ~1.2GB library and is deliberately not automated.

- **A — Prevention only.** Make the uid/gid deterministic so a *future* rebuild
  can't drift. Leave the live CT 110 broken; fixing it stays a manual operator
  runbook step.
- **B — Prevention + remediation.** Same, plus this project owns getting CT 110
  green again (automated or runbook'd chown, cutover order, verification).
- **C — Remediation first.** The live breakage is the pain; determinism is the
  follow-on.

**Answer:** **B — prevention + remediation.**

This project owns both making the uid/gid deterministic AND getting the live
CT 110 back to green. Rationale: prevention is unverifiable while the CT is
broken — without remediation, every implementation step's "demo" would be "the
gate still fails, but differently", and the pinning would only be proven at the
next rebuild, which is the worst moment to discover a mistake. The destructive
chown must be snapshot-gated (ZFS makes this cheap).

_Alternatives considered: A (prevention only), C (remediation first). Rejected._

---

## Q3: Given that the pinning already exists in HEAD, what is the actual gap?

**Discovered during clarification, not previously stated in the rough idea:** the
uid/gid pinning this project was scoped to build is *already implemented*:

- `ansible/roles/plex/tasks/main.yml:90` — "Pin the plex group GID ahead of the
  package install" (`ansible.builtin.group`, gid `991`, system)
- `ansible/roles/plex/tasks/main.yml:97` — "Pin the plex user UID ahead of the
  package install" (`ansible.builtin.user`, uid `999`, system)
- `ansible/roles/plex/defaults/main.yml` — `plex_uid: 999`, `plex_gid: 991`,
  documented as pinned so "the package reuses them instead of auto-allocating"

It landed in `0670e97` ("chore: auto-commit before merge (loop primary)") — the
most recent commit, produced by a Ralph loop rather than by hand, and plausibly
never exercised against a real CT rebuild.

So the project is not "build pinning". Candidate real gaps:

- **A — Validate what exists.** The mechanism is right; it has never been proven
  end-to-end through a destroy/recreate cycle. Scope = remediate CT 110, then
  prove a rebuild lands on 999:991 with PMS green.
- **B — The pinned values are fragile.** `999`/`991` sit inside Debian's dynamic
  system-allocation range (`FIRST_SYSTEM_UID=100`, `LAST_SYSTEM_UID=999`;
  `adduser --system` allocates *descending from 999*). `plex_uid: 999` is simply
  whoever installed first. Worse, the role installs `intel-media-va-driver-non-free`
  / `vainfo` / `intel-gpu-tools` at task line 36 — *before* the pin at line 90 —
  so an earlier package can take 999/991 and the pin then collides. The
  `non_unique: true` workaround on the render/video groups is direct evidence
  this collision class already bit once. Scope = move plex to a static uid/gid
  *outside* the dynamic range, re-chown, re-tile the idmap.
- **C — The invariant is duplicated and undefended.** `plex_idmap_base: 100000`
  in Ansible restates `local.idmap_uid_offset` in OpenTofu, and the gid shift
  holds only because `991` happens to land in the `g 45 100045 948` tile. Nothing
  fails if tofu re-tiles. Scope = single source of truth + a gate.
- **D — Some combination.**

**Answer:** **B + A — the pinned values are fragile, and the mechanism is unproven.**

Scope: move `plex` to a static uid/gid *outside* any auto-allocation range,
re-chown the state dir to match, remediate CT 110, and prove determinism through
a real destroy/recreate cycle. Rationale: Q2 already commits us to a chown, so
re-pointing it at a collision-proof id is nearly free, and validating (A) the
current 999/991 scheme would only certify a pin that races the allocator.

C (single source of truth for the idmap shift) is **not** in scope as its own
workstream, but the design should avoid making the duplication worse.

_Alternatives considered: A alone, B alone, C. Rejected as above._

---

## Q4: What should the canonical `plex` uid/gid actually be?

The pin is only collision-proof if the value sits outside every range the
allocator hands out automatically. On Debian (`/etc/adduser.conf`, `login.defs`):

| Range | Who allocates it | Safe to pin? |
|---|---|---|
| `0-99` | Debian base packages, statically | No — reserved |
| `100-999` | `useradd --system`, **descending from 999** | No — this is where 999/991 live today |
| `1000-60000` | `useradd` (regular users), ascending from 1000 | Risky — nothing creates regular users in a service CT, but nothing forbids it |
| `60001-64999` | **Nobody.** Debian Policy §9.2.2 reserves it ("globally allocated, created on demand"); above `UID_MAX=60000` so regular `useradd` never reaches it, and far above `LAST_SYSTEM_UID=999` | **Yes** |
| `65534` | `nobody` | No |

Both idmap tiles accommodate the whole space: the uid map is one tile
(`u 0 100000 65536`), and a gid in the `g 994 100994 64542` tail shifts by a
clean +100000, same as `991` does today.

- **A — `uid = gid = 64000`.** In the Debian-reserved band; no allocator can
  ever hand it out. Host-side becomes `164000:164000`.
- **B — `uid = gid = 3000`.** Conventional/readable; inside the regular-user
  range, so safe in practice but not by construction.
- **C — Keep them distinct** (e.g. `64000:64001`) to preserve the existing
  "uid != gid" lesson.

On C: the defaults comment warns "they are allocated INDEPENDENTLY, so uid !=
gid — do not collapse them into one value". That is a warning against *assuming*
equality for accidentally-allocated ids, not a requirement that they differ.
Once the ids are deliberately chosen, `uid == gid` is a property we enforce, not
an assumption we make — but the chown must still name both halves explicitly.

**Answer:** **A — `uid = gid = 64000`** (host-side `164000:164000`).

Chosen because it is the only option that is collision-proof *by construction*:
`64000` sits in Debian Policy §9.2.2's reserved `60001-64999` band, above
`UID_MAX=60000` (so regular `useradd` never reaches it) and far above
`LAST_SYSTEM_UID=999` (so `useradd --system` never descends to it). No allocator
can hand it out, which makes the ordering of the pin relative to the
`intel-media-va-driver` install (the latent line-36-before-line-90 bug) moot
rather than merely unlikely.

Consequence: the "uid != gid" comment in `defaults/main.yml` must be **rewritten,
not deleted**. The lesson it encodes — *the chown must name both halves
explicitly, never derive the gid from the uid* — stays load-bearing even though
the two values are now equal.

_Alternatives considered: B (`3000`, inside the regular-user range — safe in
practice, not by construction), C (distinct ids to preserve the uid != gid
property). Rejected._

---

## Q5: How do we prove determinism, and what is the rollback?

Q2 committed to remediating live CT 110; Q3's "A" half committed to proving a
rebuild actually lands on the pinned ids. Both need a cutover procedure.

Relevant constraints found in the repo:

- `just destroy` is a bare `tofu destroy` — it takes down **every** CT, not just
  plex. A targeted `tofu apply -replace=module.plex.<resource>` is needed.
- `docs/runbooks/plex-claim.md:88` — Proxmox **vzdump excludes bind mounts**, so
  CT backups do *not* cover the library. "The pool *is* the backup story."
- The library data lives on the `DASPool/Server/AppData` dataset, *outside* the
  CT. Destroying CT 110 does not touch it.
- CT 110's PMS is **already crash-looping**, so the CT itself has little
  remaining value to protect.

Options:

- **A — Targeted replace of CT 110**, preceded by a ZFS snapshot of
  `DASPool/Server/AppData`. Highest-fidelity proof: a real destroy/recreate.
- **B — Non-destructive convergence test.** `usermod` plex to a deliberately
  wrong uid in the live CT, re-run `just play`, assert it reconciles to 64000.
  Proves idempotent convergence, not a true rebuild (the package-install path is
  never re-exercised).
- **C — Throwaway parallel CT** at a spare `vm_id` against a ZFS *clone* of the
  dataset. Proves the rebuild without touching 110, then cut over.

**Answer:** **Remediate only — no rebuild verification, no snapshot, no manifest.**

The operator explicitly reduced scope: pin `64000`, chown the state dir to
`164000:164000`, get PMS green, stop there.

**Recorded as a deliberate, operator-acknowledged risk acceptance:**

1. **The pin ships unproven.** No destroy/recreate exercises it. Its first real
   test will be a future unplanned rebuild. This is acknowledged to be the same
   class of artifact as `0670e97` (an unexercised pin), which is what prompted
   this project. The operator accepts this.
2. **The chown is one-way.** No ZFS snapshot and no ownership manifest, so the
   prior ownership map is unrecoverable. `chown -R` does not destroy file
   contents, so the realistic failure mode is "wrong ownership, chown again" —
   the residual risk is bounded.
3. **Fallback is a full library rescan.** Operator states this is acceptable.
   Noted for the record: a rescan restores libraries but **not** watch history,
   playlists, collections, or ratings, which live in the library DB inside the
   state dir rather than in the media files.

_Alternatives considered: A (targeted replace + ZFS snapshot — recommended,
declined), B (non-destructive convergence test), C (throwaway parallel CT), and
a middle-ground post-install gate asserting the package did not override the pin
(declined). Rejected per operator direction._

_Design consequence: because determinism is not being demonstrated, the design
should lean harder on **static, reviewable** guarantees — a value the allocator
provably cannot hand out (Q4's `64000`) is doing more load-bearing work than it
would in a plan that included a rebuild test._

---

## Q6: Where does the remediation chown actually run — and can it be automated?

This is a technical constraint question, not a preference one, but it changes the
shape of the implementation plan enough to settle now.

The state dir must end up host-owned `164000:164000`. The question is *who* runs
the chown:

- **In-CT (`chown -R plex:plex /var/lib/plexmediaserver`, via the existing
  `root@plex` Ansible target).** Elegant — the idmap translates in-CT `64000` to
  host `164000` automatically, no host access needed. **But it likely cannot
  work today:** the dir currently shows as `65534`/nobody in-CT, meaning its
  host-side owner falls *outside* CT 110's `100000-165535` map. Root inside an
  unprivileged CT cannot chown a file whose current owner is unmapped in its
  namespace. This is almost certainly why the existing runbook specifies a
  host-side chown.
- **Host-side on `pve` (`chown -R 164000:164000 /tank/Server/AppData/plex`).**
  Works regardless of current ownership. Requires either an operator runbook step
  or a `pve` host target in the Ansible inventory.

Sub-question: does the repo's Ansible inventory have a `pve` host target, or does
everything target the service CTs?

**Answer:** **In-CT. No `pve` target needed. The operator was right; the analysis
above was wrong.**

Verified live against CT 110 on 2026-07-15 (see
`research/live-state-2026-07-15.md`). The in-CT `chown` **succeeded**. The
reasoning above was internally sound but rested on a false premise: the state dir
is **not** unmapped. It is `999:991` — squarely inside CT 110's `100000-165535`
map — so root-in-CT holds real CAP_CHOWN over it. The `65534`/overflowuid claim
came from the gate harness's docstring, which is **stale**.

Migration path is therefore entirely in-CT and role-automatable: stop PMS →
`groupmod`/`usermod` plex to the new ids → `chown -R plex:plex {{ plex_state_dir }}`
→ start PMS. The idmap translates in-CT `64000` to host `164000` for free.

---

## ⚠ CORRECTION — premises invalidated (2026-07-15)

The live check invalidated the factual basis of **Q2** and **Q5**. Both were
answered on the belief that CT 110 was broken. It is not.

| Believed (from the gate docstring) | Actually true (verified live) |
|---|---|
| State dir at raw `65534` ownership | Uniformly `999:991` across all 12,043 files |
| PMS crash-looping / failed | `systemctl is-active` → **active**, enabled |
| Chown is destructive on a live 1.2GB library | 1.4GB, healthy; chown is in-CT and trivially revertible |
| Host-side chown required | In-CT chown **verified working** |
| "Nothing to lose — PMS is already down" | A **working** server with library DB, watch history, playlists |

Consequences:

- **Q2 = B (prevention + remediation) is moot.** There is nothing to remediate.
  Scope collapses to prevention — i.e. Q2's rejected option A.
- **Q5's risk acceptance was made on a false premise.** "A full rescan is fine"
  and "don't snapshot" were accepted for a service the operator believed was
  already dead. It is alive and healthy. **This must be re-decided.**
- **Q5's "no manifest" concern is now moot anyway.** Ownership is *uniform* —
  all 12,043 files are `plex:plex`. The entire manifest is one fact, recorded
  here: **everything was `999:991`**. Revert is `chown -R 999:991`.
- **Q3/Q4's fragility argument is strengthened, by new evidence.** `getent`
  shows `kvm:x:993:plex` and `render:x:993:plex` — two groups colliding on GID
  993 via `non_unique: true`. The dynamic-range collision class is not
  hypothetical; it has already happened in this container.

### Process note

The live `chown` was issued inside a check described to the operator as
read-only. It was predicted to fail; it succeeded, mutating live state. Prior
ownership was recovered only because the `stat` in the same command ran first —
luck, not design. Restored to `999:991` within the same minute. **A command that
can write is not a read-only check, regardless of the predicted outcome.**

---

## Q7: Given the system is healthy, is this project still worth doing?

Re-decided from scratch after the correction above, because the original scope
("fix a broken container") no longer describes reality ("change a working
container to harden it").

**Answer:** **Yes — migrate to `64000` in-CT. No snapshot.**

Scope: role-automated, entirely in-CT — stop PMS → `groupmod`/`usermod` plex to
`64000` → `chown -R plex:plex {{ plex_state_dir }}` → start PMS. Also fix the
stale docstring in `verify_plex_state_ownership_gate.py` and update the gate's
expected ids.

Rationale: the `kvm`/`render` GID-993 collision is live proof that pinning inside
Debian's `100-999` dynamic range does not hold in this container. `999`/`991`
have not collided *yet*. `64000` (Policy §9.2.2 reserved band) cannot collide by
construction.

**Snapshot: declined again, now on correct premises.** The operator re-confirmed
after being told the server is live and healthy with a real library DB. Residual
risk is genuinely low: ownership is uniform (12,043 files, all `plex:plex`), so
revert is exactly `chown -R 999:991 /var/lib/plexmediaserver`. Recorded as an
informed acceptance, not an uninformed one.

_Alternatives considered: docs-only (keep 999/991), stage the migration, drop the
project. Rejected._

---

## Q8: What collateral does this project fix, and what does it leave alone?

The live check surfaced adjacent defects. Each needs an explicit in/out call so
the implementation plan does not quietly grow.

1. **Stale gate docstring** (`scripts/verify_plex_state_ownership_gate.py`).
   Asserts `65534` raw ownership and a failed PMS; both false. It actively misled
   this planning session into a wrong conclusion (Q6). Fixing it is unavoidable —
   the gate's expected ids change to `64000` regardless.
2. **`kvm`/`render` both at GID 993.** `non_unique: true` forced `render` onto
   993 after the package-allocated `kvm` took it. `id plex` reports `993` twice.
   Note: `render` **cannot** move — the idmap punches 993 through 1:1 and
   `/dev/dri/renderD128` is group-owned by host GID 993, so 993 is fixed by the
   host, not chosen. Any fix would have to move *`kvm`*, which is
   package-allocated. Materially different problem from the plex uid/gid pin.
3. **Stray files owned by uid 999 outside the bind mount** (logs, `/tmp`,
   caches). `usermod` does not chase them. After the migration they would be
   orphaned at 999 — and 999 is exactly the id a future package might allocate.
4. **`plex_idmap_base: 100000` duplicating `local.idmap_uid_offset`** (Q3's
   option C, deferred). The gid shift holds only because the id lands in an
   offset tile, not a punched one — still true for `64000` (tail tile
   `g 994 100994 64542`), but still undefended.

**Answer:**

1. **Stale gate docstring — IN SCOPE (mandatory).** The gate's expected ids move
   to `64000` regardless, and the docstring's false claims actively misled this
   planning session. Fix the docstring and the expected ids together.
2. **`kvm`/`render` at GID 993 — OUT OF SCOPE, documented.** Recorded in the
   design as a known issue with its analysis. `render` **cannot** move: 993 is
   dictated by the host's `/dev/dri/renderD128` group ownership and punched 1:1
   through the idmap. Only `kvm` could move, and it is package-allocated —
   a different problem, different shape. It currently works; `non_unique: true`
   holds it deliberately. Fixing it would risk live QSV transcoding to resolve a
   cosmetic duplicate. Revisit as its own task.
3. **Stray uid-999 files — MOOT.** Verified live: `find / -xdev -uid 999 -not
   -path "/var/lib/plexmediaserver/*"` returns exactly **1** hit, the mount point
   itself. There are no strays to chase.
4. **`plex_idmap_base` duplication — OUT OF SCOPE (deferred, per Q3).** The
   design must not make it worse. `64000` lands in the `g 994 100994 64542` tail
   tile, so the `+100000` shift still holds — same tile-dependent property as
   `991`, neither better nor worse.

_Alternatives considered: folding the kvm/render fix in (rejected — risks working
GPU passthrough); leaving it undocumented (rejected — it is the primary evidence
for Q4's `64000`)._

---

## Additional live verification (2026-07-15)

Run to de-risk the chosen plan:

| Check | Result | Bearing |
|---|---|---|
| `getent passwd 64000` | **FREE** | Target uid available |
| `getent group 64000` | **FREE** | Target gid available |
| `/etc/login.defs` → `UID_MAX 60000`, `GID_MAX 60000` | confirmed | **Empirically proves Q4**: `64000` is above the regular range and far above the system range (`SYS_UID_MAX` unset → default 999). No allocator in this CT can emit it. |
| stray uid-999 files outside the mount | **1** (the mount point) | No orphan cleanup needed |

## Note on Q5's standing after the correction

Q5's "no rebuild verification" was decided on the false premise that CT 110 was
already broken ("nothing to lose"). The premise was wrong — but the decision is
**more** defensible on the corrected facts, not less: a destroy/recreate test
against a *live, healthy* server carries real risk, whereas against a
crash-looped one it would have been nearly free.

The residual exposure also shrank. The unproven-pin risk was "999/991 might
collide on rebuild"; after the migration the pinned value is collision-proof by
construction, so the pin has less to prove. The gap that remains: nothing
demonstrates the `plexmediaserver` package honours a pre-created `64000` user
rather than overriding it. Q5's declined middle-ground (a post-install gate
asserting `id plex == 64000:64000`) would close exactly that gap cheaply, and the
design will note it as a recommended follow-up without re-litigating the call.

---

## Q9: When a Step-2 migration is interrupted mid-walk, what recovery must the role *guarantee*?

Asked by the Inquisitor on `design.rejected` (`task-1784130463-5f9e`,
`pdd:plex-user-persistence:requirements`), 2026-07-15, after the Design Critic
rejected the approved design on one blocking defect.

**The defect, in one line.** The migration predicate (`getent passwd plex` uid
`!= plex_uid`, §4.2/§6.3) governs both the stop and the chown — but the condition
it must actually guard is the **state dir's ownership**. Those are written by
different operations at different times, so the guard latches false while the
migration is still undone. Reproduced: re-running the play from a post-`usermod`
state skips both tasks and fails the gate, every time.

**Why this is a question for you and not a design detail.** The Critic's Q1–Q3
("what should the predicate key on", "where does the early `stat` live", "should
the stop task share it") are all *mechanism*, and mechanism is the Architect's
job. But they are all downstream of one decision that is **operator policy, not
engineering**: is a plain `just play` re-run *required* to finish an interrupted
migration, or is attended hand-repair the accepted recovery path? The Architect
can research either into existence. Only you can say which one this system owes
its operator.

**What makes the fork genuinely balanced** — the case for each is real, and the
obvious answer is not as obvious as the rejection makes it sound:

- The migration fires **exactly once**, attended, in a quiet window, with a human
  in the Plex UI (plan Step 2's own Demo requires one). After it, the predicate
  never fires again (§6.3 steady state). Self-healing buys nothing outside that
  single window — a future rebuild creates the user fresh at `64000` with the dir
  already correct, so no migration runs at all.
- Against that: the window is **not** an instant. It is the entire 12,043-file
  walk over a 1.4 GB bind mount — the part the plan itself flags as slow. A
  dropped SSH session lands in it, PMS is stopped, and §6.4's by-hand revert
  (**verified working**) is the only way out.
- X4 declined the snapshot — twice, the second time on corrected premises with
  the server known live and healthy. That is not being relitigated. But it does
  mean the documented recovery is the *only* fallback, which is what makes this
  decision load-bearing rather than cosmetic.

**The fork:**

- **(A) Self-healing.** A plain `just play` re-run must complete the migration
  from any interrupted state, unattended. Consequence: the predicate must be
  re-keyed (Critic Q1–Q3 become live design work), and Step 1's shape tests must
  assert the predicate is *recovery-correct*, not merely *present* (Q4) — today
  they assert presence only, so this would otherwise ship untested with X6 out
  and §7.4 declined.
- **(B) Attended hand-repair.** The play need not self-heal; the operator
  completes or reverts by hand via §6.4. Consequence: the predicate may stay as
  it is, and the correction is confined to the docs — but that correction becomes
  *mandatory and urgent*, because today they forbid the one action that works.

**Not in the fork — mandatory under either answer.** `plan.md:176-179` currently
tells the operator *"do not hand-fix: re-run the play. The predicate re-fires and
completes the chown."* That instructs the one action that provably cannot work,
while PMS is stopped and someone is watching. It is wrong under (A) *and* (B) and
is corrected regardless. Same for §6.1's internal contradiction: F2 says the
interrupted dir is `999:991`; §4.3 says `usermod` auto-chowns the home tree, so it
is `64000:991` (confirmed live).

**Answer:** **(A) — self-healing. A plain `just play` re-run must complete the
migration from any interrupted state, unattended.**

Answered on the documented timeout default (no operator reply within the window).
But the default was chosen on *risk policy alone* at confidence 70; the mechanism
has now been researched and reproduced, which is what actually settles it. (A)
costs one read-only `stat`, one re-keyed `when:`, and one test. That is far too
cheap to trade a permanently-wedged PMS against, and it makes §6.4 — the *only*
fallback X4 left standing — automatic rather than load-bearing prose.

Evidence: `logs/q9-predicate-probe.log` (script `logs/q9-predicate-probe.sh`),
`debian:bookworm` under podman, replicating the role's real sequence against a
12,154-entry tree. Six probes.

### The finding that changes the shape of the fix

**Re-keying the predicate to the state dir is necessary but NOT sufficient.** The
rejection framed this as "key on the dir, not the user". A dir predicate that
tests only the **uid half** wedges *identically to the one being replaced*.
Evaluated at the exact interrupted state (post-`usermod`, pre-`chown`, dir
`64000:991`):

| Predicate | Result | Outcome |
|---|---|---|
| (a) `getent passwd plex` uid `!= plex_uid` — current design (`:414`) | **FALSE** | wedged (reproduces the rejection) |
| (b) dir uid `!= plex_uid` — "key on the dir" | **FALSE** | **wedged just the same** |
| (c) dir uid `!= plex_uid` **or** dir gid `!= plex_gid` | **TRUE** | re-fires, completes |

Why (b) fails: `usermod` auto-chowns the home tree's **uid** (probe 2: 0 of 12,154
files left at uid `999`) while `groupmod` chgrps **nothing** (all 12,154 still gid
`991`). So at the interrupted state the dir's uid half already reads `64000` and a
uid-only test latches false. §4.4's rule — *"never derive the gid from the uid;
any chown must name both halves explicitly"* — turns out to govern **predicates**,
not just chowns. This is the same lesson the project exists for, one layer up.

### Why (A) is safe to guarantee: the completion-flag invariant

`chown -R` is **post-order** — the top-level dir is chowned **last**. Proven
deterministically by strace, not by sampling: of 12,154 `fchownat` calls, the
top-level dir is call **12,154 of 12,154** —

```
fchownat(5</var/lib/plexmediaserver/Library>, "Application Support", 64000, 64000, ...)
fchownat(4</var/lib/plexmediaserver>, "Library", 64000, 64000, ...)
fchownat(AT_FDCWD</>, "/var/lib/plexmediaserver", 64000, 64000, ...)   <-- LAST
```

Combined with `groupmod` never touching files, this yields the invariant (A) rests on:

> **The top-level dir reads `plex_uid:plex_gid` if and only if the `chown -R` ran
> to completion.**

Nothing else in the sequence can write that gid. So the top-level dir's ownership
*is* the migration's completion flag — one cheap `stat`, no marker file, no
manifest (which X5 already ruled unnecessary). Probe 4 confirms the interrupt
case: killed mid-walk with 11,916 of 12,154 entries still un-chgrp'd, the
top-level still read `999:991` → predicate TRUE → a re-run completes it.

### Mechanism (answers Critic Q1–Q3, which are this hat's scope)

**Q1 / Q3 — there is no single predicate, and that is the actual resolution.** The
proxy/target split does not get fixed by swapping one proxy for another. Two
operations have two genuinely different preconditions, and each must key on the
thing it guards:

- **Stop predicate — keys on the USER.** Its job is F1: `usermod -u` refuses while
  the user owns running processes. That is a fact about the *user*, so
  `getent passwd plex` is the *right* key here — it was only ever wrong for the
  chown. Widen it to fire when **either** the user's uid is wrong **or** the dir's
  ownership is wrong, so PMS is never live while its state dir is rewritten
  underneath it. Both false in steady state, so R6 is unaffected.
- **Chown predicate — keys on the DIR**, both halves, per (c) above.

**Q2 — where the early `stat` lives, and how R6 survives.** A new read-only `stat`
at the **top of the block, before the pins at `:90`/`:97`** (and before the stop),
registered separately. It must be before the pins, not merely before the chown:
`usermod` rewrites the dir's uid as a side effect (§4.3), so a stat placed after
the pins reads a fact already rewritten by the operation it is meant to gate —
which is the original defect wearing a new hat. It must guard on `.stat.exists`
(fresh CT). The gate's existing `stat` at `:106` **stays exactly where it is**,
after the chown. Two stats, two jobs: the early one is the **predicate**, the late
one is the **verdict**. Conflating them is what created this bug.

R6 holds (probe 5): converged, the dir reads `64000:64000` → chown predicate
FALSE; passwd uid `64000` → stop predicate FALSE; both tasks skip, and `stat`/
`getent` never report `changed`. Ownership stays uniform — 0 stragglers on either
half — so §6.4's revert keeps its "exact and complete" property. Probe 6: on a
fresh rebuild the user is *absent* and the dir already correct → predicate FALSE,
decided **without needing `getent` at all**, which the current predicate cannot do
(it has to special-case the missing user).

**Q4 — yes, and shape-checking cannot do it.** "Predicate is present" is exactly
what passes today. Assert *behaviour*: slice the real `when:` expression from the
role and evaluate it through ansible-core's bundled Jinja2 against three synthetic
stat facts — `999:991` → TRUE (migration fires), **`64000:991` → TRUE (the
recovery case; the current predicate returns FALSE here)**, `64000:64000` → FALSE
(R6). Plus an anti-vacuity assert that reddens when the slice parses nothing, and
a regression guard that the chown's `when:` names both `.uid` and `.gid` and does
**not** reference the passwd/getent register. This mirrors the technique already
proven in this repo (`mem-1784125195-49ac`), where a shape regex went *vacuously
green* over the very defect it was written to catch.

### What this does not touch

Not relitigating Q8.1 (superseded), AR1 (known + accepted), or X4 — (A) is
independent of all three. X4 only explains *why* the recovery path is
load-bearing; it is not reopened. The design's verified-sound sections (§4.3,
§4.6, §3.3, §5.3, A.1, §6.2's gate-as-safety-net) were honoured, not re-probed —
except where probe 2 *independently reconfirmed* §4.3's asymmetry as a side effect
of testing the predicate.

### Mandatory regardless of this answer

1. `plan.md:176-179` ("do not hand-fix: re-run the play") becomes **true** under
   (A) — but only once the predicate is fixed. It must not ship as-is against the
   current predicate, and it should say *why* re-running works (the top-level dir
   is chowned last), not merely assert it.
2. §6.1 F2's detection column says the interrupted dir is `999:991`. It is
   `64000:991` — confirmed again in probe 2. F3's *detection* claim stands
   (post-order chown reddens the gate); only its "re-run" handling was wrong.
3. **`plan.md:70-73` must stop calling the module choice a performance
   preference.** See "Accepted, with one carried flag" below — this is the third
   mandatory correction and it is the one that can silently undo (A).

## Q9 — ACCEPTED (Inquisitor, on `answer.proposed`, 2026-07-15)

**(A) self-healing is accepted and Q9 is closed.** The answer arrived on the
announced timeout default, which is legitimate — but it was not taken on trust.
The probe script and log were read, and the script genuinely tests what the log
reports; the six probes are honest. The requirements phase is complete.

### Accepted, with one carried flag — the invariant is module-specific

**Not a new fork, and it does not reopen (A).** (A) remains satisfiable and cheap.
But (A) rests entirely on the completion-flag invariant, and that invariant is a
property of **GNU coreutils**, not of "recursively chowning a tree". The Architect
proved it by strace against `chown -R` (post-order, top-level = call 12,154 of
12,154). That proof is sound *and it does not transfer*.

`plan.md:70-73` currently records the module choice as a **performance**
preference:

> "Prefer `command:` over `ansible.builtin.file` with `recurse: yes` — the latter
> stats every one of 12,043 files and is markedly slower **for the same result**."

Under (A), **"for the same result" is false.** Reproduced side by side —
`logs/q9-traversal-order-probe.sh` → `logs/q9-traversal-order-probe.log`,
9,723-entry tree, `podman unshare`:

| Implementation | Interrupted mid-walk | Chown predicate (c) | Outcome |
|---|---|---|---|
| `command: chown -R` (design `:242-244`) | top-level **still old** at all 5 interrupt depths, 5,268–9,603 entries un-chowned | **TRUE** | re-run **recovers** |
| `ansible.builtin.file: recurse=yes` | top-level **already `1:1`**, 9,134 of 9,723 un-chowned | **FALSE** | re-run **skips → wedged** |

Cause, in `ansible/modules/file.py` (`ensure_directory`): `:683` sets the
top-level's attributes **first**, then `:686` recurses via `:335`'s
`os.walk(b_path)` — `topdown=True` by default. **Pre-order.** So the file module
chowns the top level *before* the tree, which inverts the invariant: the
completion flag is raised at the *start* of the walk instead of the end.

**This is the same failure this project exists for, one layer further out.** The
Architect found the Critic's "key on the dir" was necessary but not sufficient
(a uid-only dir test wedges identically). The same holds one level up: "key on the
dir, both halves" is necessary but not sufficient — it is only *sufficient* if the
chown is post-order. The plan's own prose currently tells a future reader the two
implementations differ only in speed, which is an invitation to swap in the one
that silently breaks the recovery guarantee. §9.2's stale docstring, in a new
costume.

**Left to the Architect (mechanism, not this hat's call):** whether to pin the
invariant with a comment at the task, a test that would catch a pre-order swap, or
both — and how to word `plan.md:70-73` so the reason is *correctness*, with speed
as the secondary benefit it actually is. The requirement this hat records is only
this: **(A)'s guarantee holds only for a post-order recursive chown, and nothing
in the tree currently says so.**

### Checked and dropped — not carried

`ansible-lint` does **not** flag `command: chown`: the `command-instead-of-module`
rule's `_modules` table (`chkconfig`/`curl`/`git`/`mount`/`sed`/`systemctl`/… )
has no `chown` entry, and the repo has no `.ansible-lint` config that would add
one. So there is *no* lint pressure pushing a Builder off `command:` and onto the
file module. That worry was checked and is unfounded; it is recorded here only so
it is not re-raised. The risk is the plan's **prose**, not the toolchain.

Confidence 92 — both sides reproduced against the real module, and the `why` is
confirmed in ansible's own source, not inferred from behaviour.

_Alternatives considered: (B) attended hand-repair — viable, and the happy path is
unaffected under it, but it keeps a predicate that is wrong-by-construction in the
tree and leaves the operator's only recovery as prose, with no snapshot behind it.
Rejected as a false economy once (A) priced out at one `stat` and one `or`._


---

## Q10 — NOT ASKED. Requirements complete. (Inquisitor, `design.rejected`, 2026-07-15)

The Design Critic closed with *"Both findings are ONE question: where does
`chown_needed` live, and what is it when the dir is absent?"* — and then, correctly,
declined to prescribe. This hat's call: **that is one question, and it is not mine.
Both halves are mechanism.** No Q10.

### Verified both findings before routing them — did not take the rejection on trust

Reproduced on **the pinned `ansible-core 2.21.1`**, not by argument:

- **FAIL (provenance guard).** Real. Built both designs as role snippets under the
  design's own reuse requirement and ran the guard exactly as §7.1/`plan.md:143`
  states it:

  | impl | chown `when:` | provenance guard |
  |---|---|---|
  | accepted (dir, both halves) | `chown_needed` | **PASS** |
  | rejected (getent-keyed, wedges) | `chown_needed` | **PASS** |

  The guard cannot fail. Once `chown_needed` is a named fact reused by two tasks,
  the `when:` is a bare name and carries no provenance to assert on.

- **CONCERN (dir-absent).** Real, verbatim:
  `Error while resolving value for 'msg': object of type 'dict' has no attribute 'uid'`.
  The design's stated definition genuinely cannot be evaluated when the dir is absent.

### The reframe: dir-absent is not an open question — the project already answered it

This is the half that looked like it might be mine, and it is not. The Critic wrote
that the correct answer is *"almost certainly absent ⇒ FALSE ⇒ let the gate speak,
but the design must SAY it."* **The gate already says it, and it works.** Two facts
from the real role, both checked:

1. `:111`'s `that:` lists `plex_state_stat.stat.exists` **first**, and `assert`
   short-circuits at the first false condition — it never reaches `.uid`. Proved:
   `{"assertion": "plex_state_stat.stat.exists", "evaluated_to": false}`.
2. That fail_msg renders `{{ ... .stat.uid | default('missing') }}` → **`missing:missing`**.
   The `| default('missing')` is not incidental. Someone **deliberately wrote the
   absent case into the diagnostic.**

So the tree already carries a decision here. That makes the requirement
**"do not regress an existing designed behaviour"** — not "invent a semantic," and
not an operator-policy fork for a human to arbitrate. An A/B on dir-absent would be
asking the user to re-decide something the role decided, in a state that (Critic,
checked honestly) is **unreachable on CT 110** because the mp is configured in tofu.
That is the "nice to have" question this hat is told to stop at.

### Checked that the requirement is satisfiable before handing it over

Declining to prescribe is not licence to hand the Architect an impossible constraint
— the *last* rejection was exactly a design demanding a tolerance its own definition
forbade. So: Jinja's `and` short-circuits past the missing attribute
(`s.stat.exists and (uid != ... or gid != ...)` → `False`, no error, verified).
Absent ⇒ FALSE is expressible. **That is a feasibility check, not the mechanism** —
`exists and`, a `default`, or a separate guard task are all still the Architect's
call.

### Bounding the FAIL: false security, not a coverage hole

Worth carrying, because "the guard is vacuous" reads scarier than it is. The
rejected design is **already caught behaviourally**: §6.3/§7.1's fixture demands
`chown_needed` = TRUE at `64000:991`, and the getent-keyed predicate returns FALSE
there (§4.2.1 row (a), `logs/q9-predicate-probe.log`). The state table *is* the
guard that works. The provenance check adds no coverage it doesn't already have —
its only product is the **appearance** of protection over a defect the fixtures
would catch anyway. Whether that means re-keying it to the derivation or retiring it
in favour of the behavioural fixture is **the Architect's call — not prescribed.**

### Requirements recorded (consequences of the rejection, not new forks)

- **R12** — `chown_needed` MUST be FALSE when the state dir is absent, and the
  `:111` diagnostic MUST remain the only voice on that state. `| default(0)` is a
  known wrong-answer attractor: it yields TRUE → `chown -R` on a nonexistent path →
  a cryptic failure that shadows `:111`. §6.3 gains the row; §7.1 gains the fixture.
- **R13** — the provenance guard MUST key on the **derivation** of `chown_needed`,
  or be retired in favour of the behavioural coverage that already discriminates.
  As written it is vacuous by construction and MUST NOT be carried forward as-is.
- **R14** — §4.2:260's *"Registers `chown_needed`"* MUST be corrected. A `stat`
  registers a stat result; it cannot register a boolean. This conflation is the
  **root cause of both findings** and it must not survive the revision.

### Not relitigated

Q8.1, AR1, X4, Q9, the two-predicate split, §4.2.1 both-halves, R11/§4.2.2, §4.3,
§6.3's four rows, §6.4, the `64000` tile, §7.5. The Critic's independent
re-verification of R11 on 2.21.1 and the idmap math stands — **do not re-probe.**

Confidence 88 — both findings reproduced first-hand on the pinned version, and the
reframe rests on two checked facts about the real role, not on reading its intent.
