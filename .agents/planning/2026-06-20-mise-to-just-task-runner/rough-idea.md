# Rough Idea

Consider switching the task runner from mise to just (justfile) so that the
commands can be composed. For example, if I want to provision the homelab with
mise I have to run the plan, apply, gen-inventory, and play commands all in
sequence manually.

## Context captured at intake (2026-06-20)

Current `mise.toml` plays two roles:

1. **Toolchain + env management** — pins opentofu/packer/python and the
   `pipx:ansible*` CLIs, creates the `.venv`, and injects non-secret env
   (`PROXMOX_VE_*`) plus secret env from the gitignored `mise.local.toml`.
2. **Task runner** — defines `plan`, `apply`, `play`, `gen-inventory`, `fmt`,
   `test`, each with a `dir` and `run`.

`just` is a command runner only; it does not manage toolchains or inject env.
So the migration question is really about the *task* layer and what (if
anything) stays in mise underneath it.

Relevant existing tasks (mise.toml):
- `plan`        → dir=tofu, `tofu plan`
- `apply`       → dir=tofu, `tofu apply`
- `gen-inventory` → `python scripts/gen_inventory.py`
- `play`        → dir=ansible, `ansible-playbook site.yml`
- `fmt`         → dir=tofu, `tofu fmt -recursive`
- `test`        → `python scripts/run_gate.py` (offline gate)

Note: `scripts/test_mise_config_shape.py` currently asserts the mise task
shape and is part of `scripts/run_gate.py`.
