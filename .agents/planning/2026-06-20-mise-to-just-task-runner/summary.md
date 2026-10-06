# Project Summary — Migrate the Task Runner from mise to just

## What this is

Planning artifacts for switching the homelab's task layer from **mise tasks** to
a **`just` justfile**, so commands compose — e.g. one `just provision` runs
`apply → gen-inventory → play` instead of four manual `mise run` invocations.
mise is **kept** underneath for toolchain pinning and env/secret injection (the
two things `just` cannot do); only the task layer moves.

## Artifacts created

```
.agents/planning/2026-06-20-mise-to-just-task-runner/
├── rough-idea.md              the initial idea + intake context
├── idea-honing.md             the full requirements Q&A (10 questions) + agreed recipe table
├── research/                  (empty — no research phase was needed)
├── design/
│   └── detailed-design.md     standalone design: architecture, recipes, gate/test migration, appendices
├── implementation/
│   └── plan.md                5-step TDD implementation plan + checklist
└── summary.md                 this document
```

## Design in brief

- **Layered, not a replacement.** `mise.toml` keeps `[tools]` (+ a pinned
  `just`) and `[env]`; its `[tasks.*]` are removed. The `justfile` is the single
  source of truth for tasks; recipes run inside the active mise environment.
- **Recipe set:** `default`, `plan`, `apply` (interactive + arg/env auto-approve
  hatch), `gen-inventory`, `play`, `fmt`, `test`, `destroy`; composites `infra`,
  `config`, `provision`; parameterized `build <os>`, `build-all`,
  `bootstrap <os>`.
- **Composition** via `just` recipe dependencies, fail-fast on the first
  non-zero exit.
- **Gate:** `scripts/run_gate.py` engine unchanged; `just test` drives it. New
  `scripts/test_justfile_shape.py` asserts the recipe shape and the
  `test → run_gate.py` anchor; `scripts/test_mise_config_shape.py` is trimmed of
  task assertions and gains no-`[tasks]` / `just`-pinned checks.
- **Docs:** live operator-facing files swept `mise run …` → `just …` (incl. the
  generated banner in `ansible/inventory/hosts.yml`); historical scratchpad left
  as-is.

## Implementation plan in brief

1. Justfile foundation — leaf recipes + pin `just` in mise; add the justfile
   shape test. (mise tasks still coexist)
2. Composite recipes (`infra`/`config`/`provision`/`destroy`) + auto-approve hatch.
3. Parameterized template recipes (`build`/`build-all`/`bootstrap`).
4. Cutover — remove `[tasks.*]` from `mise.toml`; retarget the mise shape test.
5. Live-docs sweep + generated banner; retarget the runbook gate assertion.

The offline gate stays green at every step; mise tasks coexist through Step 3
and are removed only once just fully covers the surface.

## Areas that may need refinement during implementation

- The exact pinned `just` version (needs ≥1.38 for `[working-directory]`) and
  the mise backend used to install it — confirm `mise install` resolves `just`
  on your host at the chosen version.
- The auto-approve `--dry-run`/echo verification in Step 2's demo (confirming
  `-auto-approve` is actually passed) is best checked against your real Tofu
  config.

## Next steps

1. Review `design/detailed-design.md` and `implementation/plan.md`.
2. When ready to build, start the Ralph loop yourself (see below) — I do not
   start implementation as part of this planning SOP.

## Ralph loop handoff

When you want to begin implementation, start the loop yourself with one of:

- `ralph run --config presets/pdd-to-code-assist.yml --prompt "Implement Step 1 of .agents/planning/2026-06-20-mise-to-just-task-runner/implementation/plan.md"`
- `ralph run -c ralph.yml -H builtin:pdd-to-code-assist -p "Implement Step 1 of .agents/planning/2026-06-20-mise-to-just-task-runner/implementation/plan.md"`

This SOP ends here, at planning + handoff.
