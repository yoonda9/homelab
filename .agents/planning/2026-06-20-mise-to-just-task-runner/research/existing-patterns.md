# Existing Patterns — Step 3 (template recipes)

> NOTE: Step 3 is **already shipped + validated** (commit `1f9b777`, HEAD `28b36fc`,
> tree clean). This `design.approved` is a no-op re-trigger. The grounding below
> records that the shipped code matches the approved design 1:1.

## Recipe-definition pattern (justfile)
The repo's justfile uses plain leaf/composite recipes with `{{param}}`
substitution and `just` dependency ordering — no shell-side validation layered in.

- `justfile:67-68` — `build os:` → `scripts/build_template.sh {{os}}` (repo root, no `[working-directory]`).
- `justfile:71` — `build-all: (build "ubuntu26") (build "fedora") (build "windows11")` — pure dependency chain, sequences the three builds.
- `justfile:74-75` — `bootstrap os:` → `scripts/bootstrap_cloud_template.sh {{os}}`.

This mirrors the Step 1/2 convention: recipe bodies are thin wrappers over the
existing `scripts/*.sh`; just only forwards args.

## Script-side OS validation (anti-drift — design DEC)
The justfile deliberately carries **no** OS allow-list. The scripts own it:

- `scripts/build_template.sh:39-60` — `usage()` lists `{ubuntu26|fedora|windows11}`;
  `case "$NAME" in ubuntu26|fedora|windows11) ;;` else `err "unknown OS"` + `exit 64`.
- `scripts/bootstrap_cloud_template.sh:43-57` — `case "$NAME" in ubuntu26) … fedora) …`
  else `err "unknown OS"` + `exit 64`.

So `just build nope` surfaces the script's `exit 64` unchanged — no duplicated
short-name list to drift. Matches plan.md Step 3 "No OS-validation in the justfile".

## Shape-test pattern (test_justfile_shape.py)
Dual-mode stdlib shape test (per [[mem-1781891042-4495]] convention): module-level
`test_*()->bool` fns print OK/FAIL, `main()` sums and `sys.exit(1)`. Step 3 added 4
checks (11→15): `template_recipes_defined`, `build_invokes_script`,
`bootstrap_invokes_script`, `build_all_sweeps_three` (via `_recipe_deps` + os substring).
Regex anchors on the inner body (`scripts/..\.sh\s+\{\{\s*os\s*\}\}`), not just the header.
