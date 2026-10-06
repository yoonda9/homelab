# Summary — Deterministic Plex UID/GID Across CT Recreation

**Project:** `2026-07-15-plex-user-persistence`
**Rough idea:** "Ensure plex user is the same across recreation of the container"
**Planned:** 2026-07-15 · **Status:** planning complete, ready for implementation

---

## Artifacts created

```
.agents/planning/2026-07-15-plex-user-persistence/
├── rough-idea.md                      the initial concept, verbatim
├── idea-honing.md                     Q1–Q8 requirements clarification + the premise correction
├── research/
│   └── live-state-2026-07-15.md       live probe of CT 110 — overturned the project's founding premise
├── design/
│   └── detailed-design.md             standalone design (approved 2026-07-15)
├── implementation/
│   └── plan.md                        3 incremental steps + progress checklist
└── summary.md                         this document
```

## What the project turned out to be

**Not what it started as.** The rough idea described preventing the `plex` uid/gid
from drifting across a CT rebuild. Two things emerged during clarification that
reshaped it:

1. **The feature already exists.** `ansible/roles/plex/tasks/main.yml:90-104`
   already pins the gid and uid ahead of the `plexmediaserver` install. It landed
   in `0670e97` — an auto-commit from a Ralph loop, plausibly never exercised.
2. **The premise was false.** Planning proceeded for several rounds on the belief
   that CT 110 was broken (state dir at raw `65534`, PMS crash-looping), sourced
   from the docstring of `scripts/verify_plex_state_ownership_gate.py`. A live
   check disproved it: **PMS is `active`, all 12,043 files are uniformly
   `plex:plex`, QSV transcoding works.** That docstring describes a historical
   state, since remediated.

So the project is **not** "build pinning" and **not** "repair a broken server". It
is: *the existing pin is aimed at a value the allocator can collide with —
re-aim it, on a healthy system.*

## The design in one paragraph

Move the in-CT `plex` user and group from `999:991` to **`uid = gid = 64000`**.
The current values sit inside Debian's dynamic system range (`100-999`), which
`useradd --system` allocates from descending from 999 — they were never chosen,
just what the allocator handed out. `64000` sits in Debian Policy §9.2.2's
reserved band (`60001-64999`), above `UID_MAX=60000` and far above
`LAST_SYSTEM_UID=999`, so **no allocator in the container can emit it**. The
migration runs entirely in-CT through the existing role (stop PMS → `groupmod` →
`usermod` → `chown -R` → start), needs no `pve` access and no OpenTofu change, and
the CT is not replaced.

## Why act on a healthy server

The single most important finding: **the collision this prevents has already
happened in this container, to a different group.** `getent` returns
`kvm:x:993:plex` *and* `render:x:993:plex` — two groups sharing GID 993, held
together by a deliberate `non_unique: true` workaround that the role's own comment
predicted. The dynamic range does not hold here. `999`/`991` simply have not
collided *yet*.

Without that evidence this would be hardening against a theoretical failure. With
it, it is closing a class of failure that is demonstrably live.

## Implementation approach

Three steps, ordered so **`just play` never breaks between them**:

| Step | What | Demo |
|---|---|---|
| **1** | Add the migration machinery to the role, **inert** (ids stay `999`/`991`) | `just play` green, `changed=0`, PMS untouched — machinery present and provably dormant |
| **2** | Flip to `64000`; the machinery executes the live migration | `id plex` → `64000:64000`, host-side `164000:164000`, full 1.4 GB library intact in the UI, QSV working, re-run `changed=0` |
| **3** | Retire the stale harness, correct the docs | `just test` green; the repo no longer asserts a false world |

The split is the risk control: the naive order (flip ids, then add machinery)
would leave `usermod` fighting 8 live processes and the ownership gate failing the
play. Step 1 proves the machinery is inert before Step 2 arms it, so the risky
change is one line surrounded by already-proven code.

## Next steps

1. Review `design/detailed-design.md` — particularly §4.3 (the
   `usermod`/`groupmod` asymmetry) and §9.2 (the stale-docstring incident).
2. Work the checklist in `implementation/plan.md`.
3. **Schedule Step 2 for a quiet window** — it stops PMS, and 8 plex processes
   including a Transcoder were live at planning time.

## Areas needing further refinement

- **The one accepted gap (AR1).** Nothing proves the `plexmediaserver` package
  honours a pre-created `64000` user rather than overriding it on install. The
  rebuild test that would demonstrate it was declined (X6); so was the 6-line
  post-install assert that would close it cheaply (§7.4). **The pin's first real
  test will be a future unplanned rebuild.** The exposure is narrower than before
  this work — a package override rather than an allocator collision — but it is
  the project's known blind spot and the first thing to revisit. §7.4 carries the
  ready-made fix.
- **`kvm`/`render` at GID 993** (X2) — documented, not fixed. `render` cannot
  move: 993 is dictated by the host's `/dev/dri/renderD128` group and punched 1:1
  through the idmap. Only `kvm` could move, and it is package-allocated. Its own
  task deserves its own thought.
- **`plex_idmap_base: 100000` duplicates `local.idmap_uid_offset`** (X3) —
  deferred. The `+100000` shift holds for `64000` only because it lands in an
  offset tile rather than a punched one. Same tile-dependent property `991` had;
  neither improved nor worsened, still undefended by any gate.
- **Plex account/server identity** (X1) — never in scope. If a rebuild ever
  de-registers the server from plex.tv, that is a separate project.

## Process notes worth carrying forward

Two things went wrong during planning that are worth remembering:

1. **A stale docstring propagated a wrong conclusion.** The repo asserted a broken
   state that had been fixed; several rounds of design followed from it, including
   an architecturally wrong conclusion (that a `pve` Ansible target was needed for
   a host-side chown). The operator challenged it, and a live check settled it in
   one command. Retiring that harness (Step 3) is a direct consequence.
2. **A "read-only check" contained a live `chown`.** It was predicted to fail; it
   succeeded, mutating live state on a healthy server. Prior ownership was
   recovered only because a `stat` in the same command happened to run first —
   luck, not design. **A command that can write is not a read-only check,
   regardless of the predicted outcome.**
