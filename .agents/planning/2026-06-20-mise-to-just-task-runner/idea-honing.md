# Idea Honing — mise → just task runner

Requirements clarification Q&A. One question at a time.

---

## Q1: Scope — what role does mise keep?

`just` only runs commands; it does not pin toolchains (opentofu/packer/python/
ansible) or inject env/secrets (`PROXMOX_VE_*`, `mise.local.toml`), which
`mise.toml` currently does. Which end state do you want?

- **(A) Layered (recommended):** `just` owns *tasks* (composable recipes); mise
  stays underneath for toolchain pinning + env/secret injection. Recipes run
  inside the mise environment.
- **(B) Full replacement:** remove mise entirely; `just` plus some other
  mechanism (e.g. a `.env` file / asdf / system packages / a shell hook)
  handles tools and secrets too.
- **(C) Something else** — describe.

**Answer:** **(A) Layered.** `just` owns composable task recipes; mise stays
underneath for toolchain pinning + env/secret injection. Recipes run inside the
mise environment.

---

## Q2: Which composite (orchestration) recipes do you want?

The motivating one is a single `provision` that chains
`plan → apply → gen-inventory → play`. Beyond keeping the existing leaf tasks
(`plan`, `apply`, `gen-inventory`, `play`, `fmt`, `test`), which composite
recipes should exist? For example:

- **`provision`** — full pipeline: plan → apply → gen-inventory → play
- **`infra`** — just the Tofu half: plan → apply
- **`config`** — just the Ansible half: gen-inventory → play
- **`build`** — the Packer template builds (`scripts/build_template.sh …`)
- a **`default`** recipe (what `just` with no args does — often `just --list`)

Which of these (and any others) do you want?

**Answer:** **`provision`, `infra`, `config`, `build`, and `default`.**
- `provision` = plan → apply → gen-inventory → play
- `infra` = plan → apply
- `config` = gen-inventory → play
- `build` = Packer template builds (`scripts/build_template.sh`)
- `default` = list recipes (`just --list`)
- Leaf tasks retained: `plan`, `apply`, `gen-inventory`, `play`, `fmt`, `test`.

---

## Q3: How should recipes get the mise toolchain + env?

Recipes need the pinned CLIs (`tofu`, `ansible-playbook`, the `.venv` python)
and the injected env (`PROXMOX_VE_*`, secrets from `mise.local.toml`). Two
common ways under the "layered" model:

- **(A) Assume mise is active (recommended):** rely on `mise activate` /
  shell-hook having already put the toolchain on PATH and env in the
  environment, so recipes just call `tofu plan`, `ansible-playbook …`
  directly. Simple recipes; depends on the operator's shell being mise-hooked
  (or running `mise exec -- just …`).
- **(B) Self-contained via `mise exec`:** each recipe wraps commands as
  `mise exec -- tofu plan` etc., so `just` works even from a shell where mise
  isn't activated. More robust in CI / bare shells, but more verbose. [not chosen]
- **(C) Mix** — e.g. a recipe setting (`set positional-arguments`) or a shared
  prefix variable so it's one place to change.

Which approach fits how you actually run things (interactive shell with mise
hooked? CI? both)?

**Answer:** **(A) Assume mise is active.** Recipes call tools directly
(`tofu plan`, `ansible-playbook …`); the operator's shell is mise-hooked (or
they run via `mise exec -- just …`). Keep recipes clean.

---

## Q4: What happens to the `[tasks.*]` blocks in `mise.toml`?

Under the layered model the toolchain + `[env]` clearly stay in `mise.toml`.
The open question is the task definitions:

- **(A) Remove them (recommended):** delete `[tasks.plan/apply/play/...]` from
  `mise.toml` so the **justfile is the single source of truth** for tasks. You
  run `just plan`, never `mise run plan`. No drift between two task lists.
- **(B) Keep thin aliases:** leave `mise run <x>` working by having each mise
  task call `just <x>` (or vice-versa). Backwards-compatible muscle memory, but
  two files to maintain and a risk of drift.

Which do you want?

**Answer:** **(A) Remove them.** The justfile is the single source of truth;
`mise.toml` keeps only `[tools]` + `[env]`. No `mise run <task>`.

---

## Q5: How should the offline gate + its shape-tests adapt?

Removing the mise tasks breaks three things currently asserted by
`scripts/test_mise_config_shape.py` (which itself runs inside the gate):
1. `test_five_tasks_present` — asserts `[tasks]` defines plan/apply/play/fmt/test.
2. `test_test_task_is_full_aggregate` — reads `[tasks.test].run` and asserts it
   drives the full offline gate (globs `test_*.py`, tofu fmt/validate, ansible
   lint/syntax). This anchor moves from `mise.toml` to the justfile.
3. `test_acceptance_runbook_documents_reproducibility` — asserts the runbook
   shows `mise run apply` / `mise run gen-inventory` / `mise run play`.

Also: `just test` still needs to run `python scripts/run_gate.py` (the actual
gate logic in `run_gate.py` is task-runner-agnostic and stays as-is).

Proposed adaptation (recommended):
- **Drop the task assertions** from `test_mise_config_shape.py` (keep its
  tools/env/secrets/no-`.envrc` checks).
- **Add `scripts/test_justfile_shape.py`** that asserts the justfile defines the
  expected recipes (plan/apply/gen-inventory/play/fmt/test + provision/infra/
  config/build/default) and that the `test` recipe drives `run_gate.py`. It
  auto-joins the gate via the existing `test_*.py` glob.
- **Update the acceptance runbook** to `just apply` / `just gen-inventory` /
  `just play` (or `just provision`).

Does this match what you want — migrate the gate's shape assertions to the
justfile and keep `run_gate.py` as the gate engine? Any nuance (e.g. keep a
single combined shape test vs. a new file)?

**Answer:** **Yes, exactly as proposed.** Use a **new file**
`scripts/test_justfile_shape.py` for the justfile recipe assertions; trim the
task checks out of `test_mise_config_shape.py`; keep `run_gate.py` as the gate
engine; update the acceptance runbook to `just …`.

---

## Q6: Should `just` itself be installed/pinned via mise `[tools]`?

mise can install `just` (e.g. an aqua/ubi/cargo backend), so `mise install`
would provision `just` alongside tofu/packer/python/ansible — keeping a
one-command bootstrap and a pinned `just` version. Alternatively `just` is
assumed to be a host-level prerequisite the operator installs themselves.

- **(A) Pin `just` in `mise.toml` `[tools]` (recommended):** `mise install`
  also installs `just`. One-command bootstrap, version-pinned, consistent with
  how the rest of the toolchain is managed.
- **(B) Treat `just` as a host prerequisite:** document "install just" in the
  README prerequisites; mise doesn't manage it.

Which do you prefer?

**Answer:** **(A) Pin `just` in `mise.toml` `[tools]`.** `mise install` also
provisions `just`; one-command, version-pinned bootstrap.

---

## Q7: How wide should the docs / comment / `mise run …` sweep go?

`grep "mise run"` finds two classes of references:

**Live, operator-facing (should update to `just …`):**
- `README.md` (prereqs/quickstart)
- `docs/runbooks/acceptance-validation.md` (the rebuild cycle + checklist — also
  driven by the Q5 shape test)
- `docs/runbooks/host-bootstrap.md` (`mise run plan`)
- `docs/runbooks/das-zfs-migration.md` (`mise run apply`)
- `scripts/gen_inventory.py` — the comment **and** the generated banner it writes
  into `ansible/inventory/hosts.yml` (`# GENERATED … (mise run gen-inventory)`),
  so regenerating updates the committed inventory header too.
- `scripts/run_gate.py` docstring; `mise.toml` header comments.

**Historical planning records (under `.agents/scratchpad/implementation/
proxmox-homelab/` — plan.md, progress.md, validation.md, tasks/*, research/*):**
these are a point-in-time record of the original 12-step build.

- **(A) Update live files only; leave historical scratchpad records as-is
  (recommended):** they document what was true at the time; rewriting them
  distorts the record.
- **(B) Sweep everything**, including the historical scratchpad, for
  consistency.

Which scope?

**Answer:** **(A) Update live files only.** Leave the historical scratchpad
records under `.agents/scratchpad/implementation/proxmox-homelab/` untouched.

---

## Q8: Inside `provision`/`infra`, how should `apply` and the standalone `plan` behave?

`tofu apply` already computes its own plan and prompts `yes/no` before changing
anything. So a literal `plan → apply` chain runs the plan **twice** (once
informational, once inside apply). Two decisions:

1. **Does the standalone `plan` belong in the composite chains?**
   - **(A) Drop `plan` from the chains (recommended):** `infra = apply`,
     `provision = apply → gen-inventory → play`. `apply`'s own pre-apply plan +
     approval prompt is the review gate. `plan` stays as a standalone recipe for
     "just look, change nothing".
   - **(B) Keep `plan` in the chains:** `infra = plan → apply` — you see a
     standalone plan first, then apply re-plans and prompts. Redundant compute
     but an explicit two-stage look.

2. **Should `apply` keep its interactive approval, even inside `provision`?**
   - **(A) Keep interactive approval (recommended):** `provision` pauses at
     apply's `yes/no` prompt; you confirm, then it proceeds to gen-inventory →
     play. Safe by default.
   - **(B) Auto-approve** (`tofu apply -auto-approve`) so `provision` runs
     unattended end-to-end. Faster, but applies infra with no confirmation.

What's your preference on (1) and (2)?

**Answer:**
1. **(A) Drop standalone `plan` from the chains.** `infra = apply`,
   `provision = apply → gen-inventory → play`. `plan` remains a standalone
   "look, change nothing" recipe.
2. **(A) Keep `apply` interactive by default**, **plus an escape hatch**: an
   arg or environment variable that flips `apply` (and therefore `provision`)
   to non-interactive `-auto-approve` for an unattended run. (Exact mechanism —
   recipe parameter like `just provision auto=yes` and/or an env var like
   `AUTO_APPROVE=1` — to be settled in design; requirement is that BOTH a
   per-invocation arg and an env var can trigger it.)

---

## Q9: How should the `build` recipe handle the per-OS template argument?

`scripts/build_template.sh` takes exactly one of `ubuntu26` | `fedora` |
`windows11`. So `build` can't be a zero-arg recipe like the others.

- **(A) Parameterized recipe (recommended):** `just build ubuntu26` →
  `scripts/build_template.sh ubuntu26`. One template per invocation, mirrors the
  script's own contract and the README quickstart.
- **(B) Build-all convenience:** `just build` loops all three
  (ubuntu26 → fedora → windows11) sequentially; maybe a separate
  `just build-one <os>` for a single template.
- **(C) Both:** `build <os>` for one, and a `build-all` recipe for the sweep.

Note: the one-time `scripts/bootstrap_cloud_template.sh ubuntu26|fedora` is a
prerequisite for the two Linux templates — should it get its own recipe too
(e.g. `bootstrap <os>`), or stay a documented manual step?

**Answer:** **(C) Both** — `build <os>` for one template plus a `build-all`
sweep (ubuntu26 → fedora → windows11). **Add a `bootstrap <os>` recipe** for the
one-time `scripts/bootstrap_cloud_template.sh ubuntu26|fedora` source-template
step.

---

## Q10: Completeness check + any remaining recipes

Recipe set decided so far:
- Leaf: `plan`, `apply` (interactive + auto-approve escape hatch),
  `gen-inventory`, `play`, `fmt`, `test`.
- Composite: `provision` (apply → gen-inventory → play), `infra` (apply),
  `config` (gen-inventory → play), `build <os>`, `build-all`, `bootstrap <os>`,
  `default` (list recipes).

One gap I noticed: the acceptance-validation runbook's rebuild-from-code cycle
starts with `tofu destroy`, but there's no `destroy` recipe in the set.

- Should I add a **`destroy`** recipe (`tofu destroy`, interactive) to round out
  the rebuild cycle?
- Anything else missing from the recipe set?
- Do you consider requirements clarification **complete** and ready to move on?
- Before design, do you want any **research** (e.g. confirming the best mise
  backend to pin `just`, or `just` arg/env-var idioms for the auto-approve
  escape hatch), or should I go straight to the detailed design?

**Answer:**
1. **Yes — add a `destroy` recipe** (`tofu destroy`, interactive).
2. Nothing else missing.
3. **Requirements clarification is complete.**
4. **No research phase** — proceed straight to the detailed design.

---

## Final recipe set (agreed)

| Recipe | Action | Notes |
| --- | --- | --- |
| `default` | `just --list` | no-arg default |
| `plan` | `tofu plan` (dir=tofu) | look, change nothing |
| `apply` | `tofu apply` (dir=tofu) | interactive; auto-approve via arg/env |
| `gen-inventory` | `python scripts/gen_inventory.py` | |
| `play` | `ansible-playbook site.yml` (dir=ansible) | |
| `fmt` | `tofu fmt -recursive` (dir=tofu) | |
| `test` | `python scripts/run_gate.py` | offline gate engine unchanged |
| `destroy` | `tofu destroy` (dir=tofu) | interactive |
| `infra` | → `apply` | Tofu half |
| `config` | → `gen-inventory` → `play` | Ansible half |
| `provision` | → `apply` → `gen-inventory` → `play` | full pipeline |
| `build` `<os>` | `scripts/build_template.sh <os>` | one template |
| `build-all` | ubuntu26 → fedora → windows11 | sweep |
| `bootstrap` `<os>` | `scripts/bootstrap_cloud_template.sh <os>` | one-time source template |

Foundational decisions: layered (mise keeps `[tools]`+`[env]`, drops `[tasks]`);
recipes assume an active mise env; `just` pinned in `mise.toml [tools]`; new
`scripts/test_justfile_shape.py` + trimmed `test_mise_config_shape.py`;
`run_gate.py` unchanged as the gate engine; live-docs-only sweep.
