"""Shape test for the just task-runner (mise-to-just Steps 1–2).

Verifies the root `justfile` reproduces the live mise task surface 1:1 — seven
leaf recipes (`default` first, the Tofu/Ansible ones carrying the canonical
`[working-directory: '…']` attribute, bodies calling the tools directly) — and
that `mise.toml [tools]` pins the `just` binary so `mise install` provisions it.
Step 2 adds the composite recipes (`infra`/`config`/`provision`/`destroy`)
chained over the leaves and the interactive-by-default `apply approve=AUTO:`
auto-approve hatch; this test asserts those compose the expected leaves and the
hatch is wired. Step 3 adds the parameterized Packer template recipes
(`build <os>`/`build-all`/`bootstrap <os>`) — `build`/`bootstrap` take an `os`
parameter forwarded to `scripts/*.sh` (the scripts own OS validation, so the
justfile does not re-validate), and `build-all` sweeps the three OSes via
`build` dependencies. The mise `[tasks.*]` stay (parallel, zero-downtime);
cutover is Step 4.

Follows the repo's dual-mode shape-test convention (see
`test_mise_config_shape.py`, `test_dev_vm_module_shape.py`): module-level
`test_<name>() -> bool` functions that print `OK` / `FAIL: ...` (no `assert`),
plus `main() -> int` that sums the booleans and `sys.exit`s non-zero on any
failure. Stdlib only — and, per R9, the justfile is **text-parsed** (never shell
out to `just`) so the offline gate needs no provisioned binary.
"""

import pathlib
import re
import sys
import tomllib

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
JUSTFILE = REPO_ROOT / "justfile"
MISE_TOML = REPO_ROOT / "mise.toml"

# The seven leaf recipes that mirror the live mise tasks 1:1 (`default` is new).
RECIPES = ("default", "plan", "apply", "fmt", "play", "gen-inventory", "test")
# Step-2 composite recipes layered over the leaf recipes (dependency chains).
COMPOSITES = ("infra", "config", "provision", "destroy")
# Step-3 parameterized Packer template recipes.
TEMPLATES = ("build", "build-all", "bootstrap")
# The three OS short-names `build-all` sweeps via `build` dependencies.
BUILD_ALL_OSES = ("ubuntu26", "fedora", "windows11")
# Recipes carrying a `[working-directory: '…']` attribute and their directory.
# `destroy` (Step 2) joins the Tofu recipes; composites that are pure dependency
# chains (`infra`/`config`/`provision`) inherit each leaf's own directory.
WORKDIRS = {
    "plan": "tofu",
    "apply": "tofu",
    "fmt": "tofu",
    "play": "ansible",
    "destroy": "tofu",
}
# The `[working-directory]` recipe attribute landed in just 1.38 — the floor.
VERSION_FLOOR = (1, 38)


def _justfile_text() -> str:
    """Return the justfile contents, or '' if it is absent."""
    return JUSTFILE.read_text() if JUSTFILE.is_file() else ""


def _recipe_header(name: str) -> re.Pattern[str]:
    """Compiled pattern matching a recipe header `name:` at column 0.

    Anchors on the recipe-header grammar (`^name[ params]:`, MULTILINE) so a
    recipe *name* appearing inside a comment or another body is not a false
    positive (cf. mem-1781892715-142d: anchor on the construct, not a loose
    substring). The optional `[^\\n:]*` tolerates a parameter list — e.g. the
    Step-2 `apply approve=AUTO:` signature — without crossing a line or colon.
    """
    return re.compile(rf"^{re.escape(name)}(?:\s+[^\n:]*)?\s*:", re.MULTILINE)


def _recipe_deps(name: str, text: str) -> str:
    """Return the dependency portion (after the `:`) of recipe `name`'s header.

    For `provision approve=AUTO: (apply approve) gen-inventory play` this returns
    ` (apply approve) gen-inventory play`; for a leaf recipe with no
    dependencies it returns `''`. Matches only the header line (no newline in the
    class), so a recipe body never leaks in.
    """
    m = re.search(rf"^{re.escape(name)}(?:\s+[^\n:]*)?:([^\n]*)$", text, re.MULTILINE)
    return m.group(1) if m else ""


def _mentions(deps: str, recipe: str) -> bool:
    """True if `recipe` appears as a whole token in a dependency string."""
    return re.search(rf"(?<![\w-]){re.escape(recipe)}(?![\w-])", deps) is not None


def _parse_major_minor(version: str) -> tuple[int, int]:
    """Parse `major.minor` from a version string as an int tuple.

    Strips any non-numeric suffix per part and tolerates a bare major, so the
    comparison stays robust to pins like `1.53.0` or `1.53`.
    """
    nums: list[int] = []
    for part in version.split(".")[:2]:
        m = re.match(r"\d+", part.strip())
        nums.append(int(m.group()) if m else 0)
    while len(nums) < 2:
        nums.append(0)
    return (nums[0], nums[1])


def test_justfile_exists() -> bool:
    ok = JUSTFILE.is_file()
    print(f"{'OK' if ok else 'FAIL'}: root justfile exists (path={JUSTFILE.name})")
    return ok


def test_leaf_recipes_defined() -> bool:
    text = _justfile_text()
    missing = [r for r in RECIPES if not _recipe_header(r).search(text)]
    ok = not missing
    print(
        f"{'OK' if ok else 'FAIL'}: justfile defines {list(RECIPES)} as recipe "
        f"headers (missing={missing})"
    )
    return ok


def test_default_is_list() -> bool:
    text = _justfile_text()
    body_ok = (
        re.search(r"^default\s*:[^\n]*\n\s*@just\s+--list", text, re.MULTILINE)
        is not None
    )
    headers = [
        (m.start(), m.group(1))
        for m in re.finditer(r"^([a-z][\w-]*)(?:\s+[^\n:]*)?\s*:", text, re.MULTILINE)
    ]
    first_ok = bool(headers) and min(headers)[1] == "default"
    ok = body_ok and first_ok
    print(
        f"{'OK' if ok else 'FAIL'}: default recipe is `@just --list` and the "
        f"first recipe (body={body_ok}, first={first_ok})"
    )
    return ok


def test_test_recipe_drives_gate() -> bool:
    text = _justfile_text()
    ok = (
        re.search(
            r"^test\s*:[^\n]*\n\s*python\s+scripts/run_gate\.py",
            text,
            re.MULTILINE,
        )
        is not None
    )
    print(
        f"{'OK' if ok else 'FAIL'}: test recipe body runs "
        f"`python scripts/run_gate.py` (the full offline gate)"
    )
    return ok


def test_workdir_attributes() -> bool:
    text = _justfile_text()
    bad = [
        name
        for name, d in WORKDIRS.items()
        if not re.search(
            rf"^\[working-directory:\s*'{d}'\]\s*\n{re.escape(name)}(?:\s+[^\n:]*)?\s*:",
            text,
            re.MULTILINE,
        )
    ]
    ok = not bad
    print(
        f"{'OK' if ok else 'FAIL'}: plan/apply/fmt/destroy carry "
        f"[working-directory: 'tofu'] and play carries 'ansible' (bad={bad})"
    )
    return ok


def test_mise_pins_just() -> bool:
    tools: dict = {}
    if MISE_TOML.is_file():
        try:
            with MISE_TOML.open("rb") as fh:
                tools = tomllib.load(fh).get("tools", {})
        except tomllib.TOMLDecodeError:
            tools = {}
    pin = tools.get("just")
    has_str = isinstance(pin, str) and bool(pin.strip())
    version = _parse_major_minor(pin) if has_str else (0, 0)
    ok = has_str and version >= VERSION_FLOOR
    print(
        f"{'OK' if ok else 'FAIL'}: mise.toml [tools] pins bare `just` "
        f"(value={pin!r}, parsed={version}, floor>={VERSION_FLOOR})"
    )
    return ok


def test_composite_recipes_defined() -> bool:
    text = _justfile_text()
    missing = [r for r in COMPOSITES if not _recipe_header(r).search(text)]
    ok = not missing
    print(
        f"{'OK' if ok else 'FAIL'}: justfile defines {list(COMPOSITES)} composite "
        f"recipes (missing={missing})"
    )
    return ok


def test_provision_composes_pipeline() -> bool:
    deps = _recipe_deps("provision", _justfile_text())
    needed = ("apply", "gen-inventory", "play")
    missing = [r for r in needed if not _mentions(deps, r)]
    ok = not missing
    print(
        f"{'OK' if ok else 'FAIL'}: provision depends on apply/gen-inventory/play "
        f"(deps={deps.strip()!r}, missing={missing})"
    )
    return ok


def test_infra_composes_apply() -> bool:
    deps = _recipe_deps("infra", _justfile_text())
    ok = _mentions(deps, "apply")
    print(
        f"{'OK' if ok else 'FAIL'}: infra depends on apply "
        f"(deps={deps.strip()!r})"
    )
    return ok


def test_config_composes_inventory_play() -> bool:
    deps = _recipe_deps("config", _justfile_text())
    missing = [r for r in ("gen-inventory", "play") if not _mentions(deps, r)]
    ok = not missing
    print(
        f"{'OK' if ok else 'FAIL'}: config depends on gen-inventory/play "
        f"(deps={deps.strip()!r}, missing={missing})"
    )
    return ok


def test_apply_auto_approve_hatch() -> bool:
    text = _justfile_text()
    # The `AUTO_APPROVE` env default feeds the `approve` parameter default.
    auto_decl = (
        re.search(
            r'^AUTO\s*:=\s*env_var_or_default\(\s*"AUTO_APPROVE"\s*,\s*""\s*\)',
            text,
            re.MULTILINE,
        )
        is not None
    )
    # `apply` is now parameterized with an `approve=AUTO` default …
    apply_param = (
        re.search(r"^apply\s+approve\s*=\s*AUTO\s*:", text, re.MULTILINE) is not None
    )
    # … and the body gates `-auto-approve` on that parameter (interactive default).
    gated = re.search(r"if\s+approve\b[^\n]*-auto-approve", text) is not None
    ok = auto_decl and apply_param and gated
    print(
        f"{'OK' if ok else 'FAIL'}: apply auto-approve hatch wired "
        f"(AUTO_decl={auto_decl}, approve_param={apply_param}, gated_flag={gated})"
    )
    return ok


def test_template_recipes_defined() -> bool:
    text = _justfile_text()
    missing = [r for r in TEMPLATES if not _recipe_header(r).search(text)]
    ok = not missing
    print(
        f"{'OK' if ok else 'FAIL'}: justfile defines {list(TEMPLATES)} template "
        f"recipes (missing={missing})"
    )
    return ok


def test_build_invokes_script() -> bool:
    text = _justfile_text()
    # `build os:` header takes an `os` parameter and the body forwards it to the
    # build script unchanged — no in-justfile OS validation (the script owns it).
    ok = (
        re.search(
            r"^build\s+os\s*:[^\n]*\n\s*scripts/build_template\.sh\s+\{\{\s*os\s*\}\}",
            text,
            re.MULTILINE,
        )
        is not None
    )
    print(
        f"{'OK' if ok else 'FAIL'}: build takes an `os` param and runs "
        f"`scripts/build_template.sh {{{{os}}}}`"
    )
    return ok


def test_bootstrap_invokes_script() -> bool:
    text = _justfile_text()
    ok = (
        re.search(
            r"^bootstrap\s+os\s*:[^\n]*\n\s*scripts/bootstrap_cloud_template\.sh"
            r"\s+\{\{\s*os\s*\}\}",
            text,
            re.MULTILINE,
        )
        is not None
    )
    print(
        f"{'OK' if ok else 'FAIL'}: bootstrap takes an `os` param and runs "
        f"`scripts/bootstrap_cloud_template.sh {{{{os}}}}`"
    )
    return ok


def test_build_all_sweeps_three() -> bool:
    deps = _recipe_deps("build-all", _justfile_text())
    # `build-all` is a pure dependency chain invoking `build` per OS short-name.
    builds_ok = _mentions(deps, "build")
    missing_os = [os for os in BUILD_ALL_OSES if os not in deps]
    ok = builds_ok and not missing_os
    print(
        f"{'OK' if ok else 'FAIL'}: build-all depends on build for "
        f"{list(BUILD_ALL_OSES)} (deps={deps.strip()!r}, build={builds_ok}, "
        f"missing_os={missing_os})"
    )
    return ok


TESTS = (
    test_justfile_exists,
    test_leaf_recipes_defined,
    test_default_is_list,
    test_test_recipe_drives_gate,
    test_workdir_attributes,
    test_mise_pins_just,
    test_composite_recipes_defined,
    test_provision_composes_pipeline,
    test_infra_composes_apply,
    test_config_composes_inventory_play,
    test_apply_auto_approve_hatch,
    test_template_recipes_defined,
    test_build_invokes_script,
    test_bootstrap_invokes_script,
    test_build_all_sweeps_three,
)


def main() -> int:
    results = [fn() for fn in TESTS]
    total, passed = len(results), sum(results)
    if passed == total:
        print(f"PASS: {passed}/{total}")
        return 0
    print(f"FAIL: {total - passed}/{total}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
