# Implementation Context — Step 3: template recipes (`build`, `build-all`, `bootstrap`)

## ⚠️ Status: ALREADY SHIPPED + VALIDATED (no-op re-trigger)
Step 3 was implemented in commit `1f9b777` and the whole mise-to-just migration is
complete + validated at HEAD `28b36fc` (tree clean). This `design.approved` event is
a no-op re-trigger of validated work — confirmed by the prior Inquisitor / Architect /
Design-Critic scratchpad entries, all of which VERIFIED rather than rebuilt.

The Explorer phase below grounds the (already-shipped) design in codebase reality so
the Planner can likewise VERIFY-not-rebuild.

## Summary of findings
- **Recipes present** — `justfile:67-75` carry `build os:`, `build-all:`, `bootstrap os:`,
  matching plan.md Step 3 guidance and detailed-design R8 1:1.
- **Anti-drift design honored** — no OS allow-list in the justfile; the scripts validate
  (`build_template.sh:55-60`, `bootstrap_cloud_template.sh:43-57` → `exit 64` on unknown OS)
  and just surfaces that exit code.
- **Tests green** — `python scripts/test_justfile_shape.py` → **PASS 15/15 exit 0**, including
  all four Step-3 checks (template_recipes_defined / build_invokes_script /
  bootstrap_invokes_script / build_all_sweeps_three).

## Integration points
- `build-all` composes `build` three times via just dependency-with-args — sequences
  ubuntu26 → fedora → windows11.
- `build`/`bootstrap` forward `{{os}}` to the existing Packer scripts; no other code touched.
- Shape test auto-joins the offline gate via `run_gate.py` glob (no run_gate edit needed).

## Constraints / considerations for the Builder (if ever re-run)
- Do NOT add OS validation to the justfile — it would duplicate the scripts and drift.
- Keep the shape-test regex anchored on the recipe body (`scripts/..\.sh\s+\{\{\s*os\s*\}\}`),
  not just the header.
- zsh `noclobber` trap: run the gate with `>|` to avoid stale-log false reads
  ([[mem-1781926348-262c]]).

## Recommendation
No implementation work remains for Step 3. Hand to Planner to VERIFY the existing
plan/tests against shipped code rather than author new work.

See `research/existing-patterns.md`, `research/technologies.md`, `research/broken-windows.md`.
