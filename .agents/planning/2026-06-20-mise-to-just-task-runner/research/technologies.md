# Technologies — Step 3

- **just** — pinned `just = "1.53.0"` in `mise.toml [tools]` (bare registry short
  form → `aqua:casey/just`). `{{param}}` substitution and `(recipe "arg")`
  dependency-with-arguments syntax are both well below the `[working-directory]`
  floor of just 1.38.0, so no version risk. Verified live against just 1.51/1.53
  ([[mem-1781924320-63ea]]).
- **scripts/build_template.sh** — existing Packer driver, args `{ubuntu26|fedora|windows11}`,
  exits 64 on unknown OS, 78 on missing Packer creds. Untouched by Step 3.
- **scripts/bootstrap_cloud_template.sh** — existing cloud source-template
  bootstrap, args `{ubuntu26|fedora}`, exits 64/78 likewise. Untouched by Step 3.
- **scripts/test_justfile_shape.py** — stdlib-only (pathlib/re/sys/tomllib), no
  subprocess (binary-free per R9). Auto-joins the gate via `run_gate.py` glob.

No new dependencies introduced by Step 3 — it is pure justfile wiring over
already-present scripts.
