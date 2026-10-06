# Implementation Context — Plex Blip Manual Triage & Instrumentation

**Source type.** Existing PDD directory: `.agents/planning/2026-08-07-plex-blip-manual-triage/`
(`rough-idea.md`, `idea-honing.md`, `research/`, `design/detailed-design.md`,
`implementation/plan.md`). `plan.md` is the numbered step plan and owns strategy;
this file records what was measured at the delivered tree before the wave was cut.

**Original request.** Implement Step 1 of `implementation/plan.md` — repair the
watchdog's two lock-holder diagnostic probes so they produce data during a blip
rather than only when nothing is wrong.

---

## Measured state of the tree (verified by the Planner at `5c9a830`, 2026-08-07)

Every claim below was re-derived at my own hands rather than carried from `plan.md`.
Where the plan and the tree disagree, the tree is recorded here and the routed row's
description carries the correction.

### 1. `psmisc` is genuinely absent — and the plan's pointer is ambiguous

`ansible/roles/plex/tasks/main.yml` holds **two** apt name lists:

| Line | Task | List |
|---|---|---|
| :38 | `Install the Plex media packages` | `"{{ plex_media_packages }}"` (a var) |
| :237-245 | `Install Plex watchdog and diagnostic dependencies` | inline: `sysstat`, `lsof`, `procps`, `sqlite3` |

`fuser(1)` ships in `psmisc`, which is in neither. The `_run_cmd(["fuser", "-v"] + targets)`
call at `plex_blip_watchdog.py:331` has therefore never been able to run — consistent
with the 34/34 failure count in `plan.md`.

Step 1's guidance says "add `psmisc` to the package list in
`ansible/roles/plex/tasks/main.yml`". **The file is right; "the package list" is not
unique.** `psmisc` belongs in the inline watchdog-deps list at :239, beside `lsof` and
`procps` — not in `plex_media_packages`, which is the hardware-transcoding driver set.
A Builder that greps for the variable puts it in the wrong task and the row still looks
green. This is pinned in the acceptance criteria of `step-01:psmisc-dependency`.

### 2. `_run_cmd`'s current contract loses exactly what Step 1 wants

`ansible/roles/plex/files/plex_blip_watchdog.py:82-96`:

```python
def _run_cmd(cmd: list[str], timeout: float = 0.5) -> str:
    try:
        proc = subprocess.run(cmd, ..., timeout=timeout)
        return proc.stdout.strip()
    except subprocess.TimeoutExpired:
        return "[probe timeout exceeded]"
    except Exception as e:
        return f"[probe error: {e}]"
```

Three facts, each one read of the function:

- The **0.5 s hard timeout is real** and is the default at all four probe call sites
  (`fuser` :331, `lsof` :332, `pidstat` :341, `ps` :343) — none passes an override.
- **`elapsed_ms` is not merely unreported, it is never measured.** There is no clock in
  the function. "`lsof` crossed 0.5 s" and "`lsof` crossed 2.0 s" are the same string.
- **`missing` is currently indistinguishable from `error`.** `FileNotFoundError` (the
  no-`psmisc` case) falls into the generic `except Exception` and is spelled
  `[probe error: ...]`, the same as a permissions failure or a decode error. The
  four-status contract in design §5.1 is a real refinement, not a rename.

### 3. Blast radius `plan.md` does not name: three dry-run branches string-test the return

`capture_snapshot` guards its dry-run fallbacks by testing `_run_cmd`'s return **as a
string**:

- `:335` `if not fuser_out or "probe error" in fuser_out or fuser_out == "":`
- `:337` the same for `lsof_out`
- `:343` `if self.dry_run and ("probe error" in pidstat_out or not pidstat_out):`

Against a `dict`, `"probe error" in d` tests **keys**, so it is always `False`, and a
non-empty dict makes `not d` `False` too. The result is not a crash — it is the
dry-run fallbacks **silently ceasing to fire**, which is the failure mode that survives
a green test run. These three sites move in the same commit as the contract change or
`--dry-run` quietly stops simulating. This is a functional dependency on the return
*shape*, not a literal, so a grep for `_run_cmd` finds the call sites but not the risk.

### 4. The existing test suite is barely coupled to the shape — so "existing tests pass
unmodified" is a true contract, not a hopeful one

`scripts/test_plex_blip_watchdog.py` touches the snapshot shape at exactly one line:
`:137 self.assertIn("lock_holders", record)`. It asserts the key exists, never its
value type. `plan.md`'s Step 1 acceptance "existing tests still pass unmodified" is
therefore cheap and checkable, and a Builder that finds itself editing existing
assertions has changed something Step 1 did not ask it to change.

---

## Repo patterns to follow

- **Watchdog source** lives at `ansible/roles/plex/files/plex_blip_watchdog.py`
  (deployed as a file, not a template) with tests at `scripts/test_plex_blip_watchdog.py`.
  Tests are stdlib `unittest`, no pytest fixtures.
- **Shape tests** are the repo's idiom for asserting that a rendered/edited config still
  says what it must: `scripts/test_traefik_config_shape.py`,
  `scripts/test_plex_*_runbook_shape.py`. Step 1's Ansible assertion follows this.
- **`just test`** is the backpressure gate. Its Ansible-side steps are
  `ansible-lint --offline --profile production` and `ansible-playbook --syntax-check
  site.yml`, both run in `ansible/` with `ANSIBLE_VAULT_PASSWORD=CHANGEME`
  (`scripts/run_gate.py:66-69`). *(Corrected 2026-08-08, DEC-220: this line said
  `playbooks/plex.yml`. No `playbooks/` directory exists in this repo and
  `git log --all` has no record of one; `ansible/site.yml` is the only playbook and its
  third play is the `plex` role. The old spelling exits 1 with "could not be found",
  which reads like a broken playbook rather than a bad path.)*
- **The gate globs its own membership.** `run_gate.py:53` walks `scripts/test_*.py`, so a
  new shape test joins `just test` with no wiring. 33 shape tests + 3 tofu + 2 ansible =
  the 38/38 reported through 1a and 1b; each new test file moves that total by one.
- **Guards are proven red before green.** A guard is only evidence once it has been
  watched to fail — see `plan.md` Step 3 and the standing repo convention.
- **PyYAML *is* importable in a shape test** — measured at 1c, 2026-08-08. The comment at
  `scripts/test_plex_state_ownership_shape.py:249-252` ("the GATE pythons lack PyYAML", so
  YAML helpers are reachable only after that file's ansible re-exec) is **stale for the
  interpreter the gate actually uses**: `just test` runs `python scripts/run_gate.py`, and
  both `python` and the `[sys.executable, path]` at `run_gate.py:56` resolve to
  `.venv/bin/python`, which carries **PyYAML 6.0.3**. Confirmed end-to-end by
  `scripts/test_plex_watchdog_deps_shape.py` importing `yaml` at module level and passing
  *inside* the 39/39 gate. The stdlib-only rule (mem-1782133401-4307) still binds anything
  needing `import ansible` — that half is unchanged and still true.
- **Import a missing parser loudly; do not reach for the skip idiom.** The repo's
  `OK (skip): not installed -> return True` pattern (`test_build_template_runner.py:52-57`)
  is right for genuinely optional tools like `shellcheck`, and wrong for a parser a check
  depends on: it converts an unrun assertion into a green badge. Same reasoning as that
  file's own C-2 block.
- **Assert the *containing task*, not the string.** `ansible/roles/plex/tasks/main.yml`
  holds **four** apt name lists, and a package installs from any of them — so a
  `"<pkg>" in main.yml` grep is green for every placement and discriminates nothing. Parse
  the role and locate the package by its owning task. Parsing also avoids a false positive
  regex takes: `sqlite3` appears at `:339` inside a `command: argv:` list, so "the name
  appears in the file" is not a proxy for "the package is installed". And pair the positive
  with a negative that can actually *answer* — read list literals from `defaults/main.yml`,
  never through the `{{ var }}` string in `tasks/main.yml`.

## Acceptance criteria for Step 1 (from `plan.md` §Step 1, unmodified)

- Timeout → `status == "timeout"` **and** `elapsed_ms ≈ timeout × 1000` (the regression
  that matters most: the old code lost the number).
- Nonexistent binary → `status == "missing"`, distinct from `"error"`.
- Success → `status == "ok"`, output preserved, `elapsed_ms > 0`.
- Snapshot dict round-trips through `json.dumps` with the new `lock_holders` shape.
- Every existing top-level JSONL key retained, so the 448 KB of captures already on
  disk stay parseable.
- Existing tests pass **unmodified**.

## Constraints

- Default timeout rises 0.5 s → 2.0 s, per-probe overridable (design §5.1).
- `elapsed_ms` is recorded **even on timeout** — a slow `lsof` on the database files is
  itself a contention signal.
- Additive-only on the JSONL top level. Nothing already on disk may become unparseable.
- Steps 2–4 write into the structure Step 1 defines, so the shape is a published
  contract, not an internal detail.

## Out of scope for Step 1

`TX_HELD` / `hold_site` / `live_connections` (Step 2), the `sqlite` WAL block
(Step 3), textfile metrics and `plex_watchdog_probe_status` (Step 4). Step 1 defines
the container these land in and stops there.
