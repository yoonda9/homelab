# Broken Windows — Step 3 touched files

Touched files: `justfile` (recipes 67-75), `scripts/test_justfile_shape.py`,
`scripts/build_template.sh`, `scripts/bootstrap_cloud_template.sh`.

No low-risk broken windows found in the Step-3 surface.

- `justfile:67-75` — recipes are minimal thin wrappers; comments present
  (`# One-time cloud source-template bootstrap …` at justfile:73). No dead code,
  no magic values (OS short-names live in the scripts by design, not duplicated here).
- `scripts/build_template.sh` / `scripts/bootstrap_cloud_template.sh` — pre-existing,
  well-documented `usage()` blocks; `exit 64`/`exit 78` are standard sysexits codes,
  not magic. Out of Step-3 scope to modify (the design intentionally leaves them as
  the single source of OS validation — touching them would create drift).
- `scripts/test_justfile_shape.py` — follows the established dual-mode shape-test
  convention; consistent with sibling `test_*_shape.py` files.

Nothing for the Builder to opportunistically fix.
