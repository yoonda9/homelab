"""Shape test for the just task-runner foundation (mise-to-just Step 1).

Verifies the root `justfile` reproduces the live mise task surface 1:1 — seven
leaf recipes (`default` first, the Tofu/Ansible ones carrying the canonical
`[working-directory: '…']` attribute, bodies calling the tools directly) — and
that `mise.toml [tools]` pins the `just` binary so `mise install` provisions it.
The mise `[tasks.*]` stay this step (parallel, zero-downtime); cutover is Step 4.

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
# Recipes carrying a `[working-directory: '…']` attribute and their directory.
WORKDIRS = {"plan": "tofu", "apply": "tofu", "fmt": "tofu", "play": "ansible"}
# The `[working-directory]` recipe attribute landed in just 1.38 — the floor.
VERSION_FLOOR = (1, 38)


def _justfile_text() -> str:
    """Return the justfile contents, or '' if it is absent."""
    return JUSTFILE.read_text() if JUSTFILE.is_file() else ""


def _recipe_header(name: str) -> re.Pattern[str]:
    """Compiled pattern matching a recipe header `name:` at column 0.

    Anchors on the recipe-header grammar (`^name\\s*:`, MULTILINE) so a recipe
    *name* appearing inside a comment or another body is not a false positive
    (cf. mem-1781892715-142d: anchor on the construct, not a loose substring).
    """
    return re.compile(rf"^{re.escape(name)}\s*:", re.MULTILINE)


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
        for m in re.finditer(r"^([a-z][\w-]*)\s*:", text, re.MULTILINE)
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
            rf"^\[working-directory:\s*'{d}'\]\s*\n{re.escape(name)}\s*:",
            text,
            re.MULTILINE,
        )
    ]
    ok = not bad
    print(
        f"{'OK' if ok else 'FAIL'}: plan/apply/fmt carry "
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


TESTS = (
    test_justfile_exists,
    test_leaf_recipes_defined,
    test_default_is_list,
    test_test_recipe_drives_gate,
    test_workdir_attributes,
    test_mise_pins_just,
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
