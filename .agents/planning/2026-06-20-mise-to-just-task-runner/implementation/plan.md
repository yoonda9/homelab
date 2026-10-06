# Implementation Plan — Migrate the Task Runner from mise to just

Built test-driven, in working/demoable increments. Each step writes or updates
its shape test alongside the change; the offline gate (`python
scripts/run_gate.py`, soon `just test`) must exit 0 at the end of every step.
The justfile and mise tasks **coexist** through Steps 1–3 (low risk), then Step
4 is the cutover that removes the mise tasks, and Step 5 finishes the docs.

> Build instruction (per the SOP): _Convert the design into a series of
> implementation steps that build each component test-driven, each a working,
> demoable increment, no big complexity jumps, each building on the last and
> ending with wiring — no orphaned code._

## Checklist

- [ ] **Step 1** — Introduce the `justfile` with leaf recipes + pin `just` in mise; add `test_justfile_shape.py`.
- [ ] **Step 2** — Add composite recipes (`infra`, `config`, `provision`, `destroy`) + the auto-approve escape hatch.
- [ ] **Step 3** — Add the parameterized template recipes (`build <os>`, `build-all`, `bootstrap <os>`).
- [ ] **Step 4** — Cutover: remove `[tasks.*]` from `mise.toml`; retarget `test_mise_config_shape.py`.
- [ ] **Step 5** — Live-docs sweep + generated banner; retarget the runbook gate assertion.

---

## Step 1: Justfile foundation — leaf recipes + `just` pinned in mise

**Objective.** Stand up a working `justfile` at the repo root whose leaf recipes
mirror the existing mise tasks 1:1 (`default`, `plan`, `apply`, `gen-inventory`,
`play`, `fmt`, `test`), and pin `just` in `mise.toml [tools]` so `mise install`
provisions it. The mise tasks stay in place this step (parallel, zero-downtime).

**Guidance.**
- Create `justfile` (repo root). Use the `[working-directory: 'tofu']` attribute
  for `plan`/`apply`/`fmt` and `[working-directory: 'ansible']` for `play`;
  `gen-inventory`/`test` run from repo root. `default` = `@just --list` and is
  the first recipe.
- Recipe bodies call tools directly (active-mise model): `tofu plan`,
  `tofu apply`, `tofu fmt -recursive`, `ansible-playbook site.yml`,
  `python scripts/gen_inventory.py`, `python scripts/run_gate.py`.
- Add `just = "<pinned ≥1.38>"` to `mise.toml [tools]` (a version supporting the
  `[working-directory]` attribute). Do **not** remove the mise tasks yet.

**Test requirements.**
- Add `scripts/test_justfile_shape.py` (dual-mode convention: `test_*() -> bool`
  printing `OK`/`FAIL`, `main() -> int`, stdlib only, parses the `justfile`
  text). Assert: justfile exists; the seven leaf recipes are defined; the `test`
  recipe drives `python scripts/run_gate.py` (the migrated "test recipe is the
  full gate" anchor); `mise.toml [tools]` pins `just`. It auto-joins the gate via
  the existing `scripts/test_*.py` glob.
- Gate stays green: `python scripts/run_gate.py` exits 0 (count rises by one).

**Integration.** First component; nothing depends on it yet, but it is fully
exercised by the gate and runnable by hand. mise tasks remain the documented
path until Step 5, so nothing breaks.

**Demo.** `just --list` shows the recipes; `just fmt` formats Tofu; `just test`
runs the full offline gate to exit 0; `mise install` installs `just`. `mise run
fmt` still works (parallel path intact).

---

## Step 2: Composite recipes + auto-approve escape hatch

**Objective.** Add the composing recipes — `infra` (apply), `config`
(gen-inventory → play), `provision` (apply → gen-inventory → play) — plus
`destroy`, and the interactive-by-default `apply` with an arg/env auto-approve
hatch that propagates through `provision`/`infra`.

**Guidance.**
- Define `AUTO := env_var_or_default("AUTO_APPROVE", "")`. Rewrite `apply` as
  `apply approve=AUTO:` whose body adds `-auto-approve` only when
  `approve != ""`.
- `infra approve=AUTO: (apply approve)`;
  `provision approve=AUTO: (apply approve) gen-inventory play`;
  `config: gen-inventory play`; `destroy:` → `tofu destroy`
  (`[working-directory: 'tofu']`, interactive).
- Rely on `just`'s left-to-right dependency ordering + fail-fast (non-zero
  aborts the chain).

**Test requirements.**
- Extend `scripts/test_justfile_shape.py`: assert `infra`, `config`,
  `provision`, `destroy` exist; `provision` composes `apply`/`gen-inventory`/
  `play` (dependency line mentions all three); `infra` composes `apply`;
  `config` composes `gen-inventory`/`play`; the `apply` auto-approve hatch is
  wired (reads `AUTO_APPROVE` default and/or `approve` arg).
- Gate stays green.

**Integration.** Builds directly on Step 1's leaf recipes (composites are
dependencies over them). The auto-approve default keeps existing `just apply`
behavior unchanged (interactive).

**Demo.** `just provision` runs apply (pauses at the `yes/no` prompt) → on
confirm, gen-inventory → play. `AUTO_APPROVE=1 just provision` and `just
provision approve=1` run unattended (verify the `-auto-approve` flag is passed,
e.g. via `--dry-run`/echo). `just infra` / `just config` / `just destroy` work.

---

## Step 3: Parameterized template recipes — `build`, `build-all`, `bootstrap`

**Objective.** Wire the Packer template workflow into just: `build <os>` for a
single template, `build-all` to sweep all three, and `bootstrap <os>` for the
one-time cloud source-template step.

**Guidance.**
- `build os:` → `scripts/build_template.sh {{os}}` (repo root).
- `build-all: (build "ubuntu26") (build "fedora") (build "windows11")`.
- `bootstrap os:` → `scripts/bootstrap_cloud_template.sh {{os}}`.
- No OS-validation in the justfile — the existing scripts already validate and
  exit non-zero on an unknown OS; `just` surfaces that (avoids drift).

**Test requirements.**
- Extend `scripts/test_justfile_shape.py`: assert `build`, `build-all`,
  `bootstrap` exist; `build`/`bootstrap` take an `os` parameter and invoke the
  respective `scripts/*.sh`; `build-all` depends on `build` for the three OSes.
- Gate stays green.

**Integration.** Completes the full recipe set over Steps 1–2; the justfile now
covers everything the mise tasks did plus the template/bootstrap flows the mise
tasks never had.

**Demo.** `just build ubuntu26` invokes `scripts/build_template.sh ubuntu26`;
`just bootstrap fedora` invokes the bootstrap script; `just build-all` sequences
the three; an unknown OS (`just build nope`) fails fast with the script's error.

---

## Step 4: Cutover — remove `[tasks.*]` from `mise.toml`, retarget the mise shape test

**Objective.** Make the justfile the sole task interface: delete the mise task
blocks and update `scripts/test_mise_config_shape.py` so the gate proves the
migration happened and stays anti-drift.

**Guidance.**
- Remove all `[tasks.plan/apply/play/gen-inventory/fmt/test]` blocks from
  `mise.toml`. Keep `[tools]` (incl. `just`), `[env]`, the venv config, and the
  secret split.
- Update `mise.toml` header comments: `mise run <task>` → `just <recipe>`; note
  tasks live in the justfile now.
- In `test_mise_config_shape.py`: **remove** `test_five_tasks_present` and
  `test_test_task_is_full_aggregate` (+ its `_test_task_gate_text` helper and
  `REQUIRED_TASKS`); the "test recipe is the full gate" guarantee already lives
  in `test_justfile_shape.py` from Step 1. **Add** assertions that `[tasks]` is
  absent/empty and that `[tools]` pins `just`. Update the module docstring
  (drop "and the five tasks").

**Test requirements.**
- `test_mise_config_shape.py` runs green standalone with the new assertions; all
  retained tools/env/secrets/no-`.envrc` checks still pass.
- Full gate green. (Note: at this step the runbook still says `mise run …`; the
  retained `test_acceptance_runbook_documents_reproducibility` still asserts
  `mise run …` and so still passes — it is retargeted in Step 5.)

**Integration.** This is the cutover: it depends on Steps 1–3 having fully
replicated the task surface in just before mise tasks are removed, so no
capability is lost. After this step `mise run plan` no longer exists; `just
plan` is the path.

**Demo.** `mise run plan` errors (task gone); `just plan` works. `mise tasks`
lists nothing. `python scripts/test_mise_config_shape.py` exits 0 with the new
no-tasks/`just`-pinned assertions. Full gate exits 0.

---

## Step 5: Live-docs sweep + generated banner; retarget the runbook gate assertion

**Objective.** Bring all operator-facing references in sync with the new `just`
interface and the committed generated artifact, and retarget the one gate
assertion that anchors on the runbook's literal command strings.

**Guidance.**
- Update `scripts/gen_inventory.py`: docstring `mise run gen-inventory` →
  `just gen-inventory`, and the generated banner string it writes into
  `ansible/inventory/hosts.yml`. Regenerate (or one-line edit) so the committed
  `ansible/inventory/hosts.yml` header reads `(just gen-inventory)`.
- Update `scripts/run_gate.py` docstring `mise run test` → `just test`.
- Sweep live docs `mise run …` → `just …`: `README.md` (and add `just` to the
  prereqs as mise-provisioned), `docs/runbooks/acceptance-validation.md` (incl.
  the checklist and the destroy→apply→gen-inventory→play cycle — now usable as a
  single `just provision`/`just destroy`), `docs/runbooks/host-bootstrap.md`,
  `docs/runbooks/das-zfs-migration.md`. Leave the historical
  `.agents/scratchpad/implementation/proxmox-homelab/` records untouched.
- Retarget `test_acceptance_runbook_documents_reproducibility` in
  `test_mise_config_shape.py`: assert `just apply` / `just gen-inventory` /
  `just play` (and `tofu destroy`) instead of `mise run …`. Do the runbook edit
  and this assertion change **together** so the gate never goes red mid-step.

**Test requirements.**
- The retargeted runbook assertion passes against the edited runbook; full gate
  exits 0.
- A repo grep confirms no live (non-scratchpad) `mise run` references remain.

**Integration.** Final wiring: closes the loop so docs, the committed inventory
banner, and the gate all describe the `just` interface. With Steps 1–4 the
behavior is already migrated; this step makes the documentation and the
gate's literal-string anchor consistent.

**Demo.** `grep -rn "mise run" --exclude-dir=.agents` (or excluding the
scratchpad path) returns nothing; `ansible/inventory/hosts.yml` header reads
`(just gen-inventory)`; `just test` exits 0; the acceptance runbook reads as a
`just`-driven rebuild cycle (`just destroy` → `just provision`).

---

## Completion criteria

- `just <recipe>` covers every former `mise run <task>` plus `provision`/`infra`/
  `config`/`build[-all]`/`bootstrap`/`destroy`/`default`.
- `mise.toml` has no `[tasks]`; pins `just`; keeps tools/env/secret split.
- `scripts/run_gate.py` unchanged as the gate engine; `just test` drives it;
  `test_justfile_shape.py` + trimmed `test_mise_config_shape.py` both green and
  auto-joined to the gate.
- No live docs/comments/generated artifacts reference `mise run`; historical
  scratchpad untouched.
- Offline gate exits 0 at every step.
