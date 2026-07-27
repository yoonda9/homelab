"""Shape test for Step 1b — the off-LAN Plex latency baseline runbook.

Per `.agents/planning/2026-07-27-plex-optimization/implementation/plan.md`
Step 1 (and `.ralph/specs/plex-optimization/plan.md`'s wave split) — verifies
`docs/runbooks/plex-latency-baseline.md` documents the OPERATOR procedure for
capturing the baseline that Step 4 is compared against:

  * the **external-network requirement** and its reason — from the LAN the
    request never crosses the WAN path or the router hairpin, so a LAN number is
    a *control*, not the baseline. This is the single most misread part of the
    plan, so it is pinned as prose, not as a flag,
  * a **results table** carrying the plan's own metric names (TTFB and total
    load time, per endpoint, min/median/max) plus the run's UTC timestamp and
    vantage — and left **UNFILLED**, because a fabricated baseline silently
    invalidates Step 4's whole comparison,
  * **cross-file agreement**: every `measure_plex_latency.py` command line the
    runbook prints actually parses against the harness's REAL argparse parser,
    with the external capture carrying `--vantage external --skip-direct` and
    the direct-:32400 control being a SEPARATE `--vantage lan` run,
  * **no literal token** anywhere in the doc — `$PLEX_TOKEN` comes from the
    environment (the harness has no `--token` flag by design).

The capture itself is off-LAN and operator-only; this test gates only the
repo-side artifact, the same scope as the other `*_runbook_shape.py` tests.

The cross-file check reads TWO artifacts — the runbook and
`scripts/measure_plex_latency.py` — which is what makes it load-bearing in both
directions (mem-1784757961-4fb7). It takes the harness path as a defaulted
argument so its harness half can be proven non-vacuous against a doctored COPY,
without touching the closed, committed harness itself.

Follows the repo's dual-mode shape-test convention (see
`test_plex_ramdisk_runbook_shape.py`, `test_acceptance_validation_runbook_shape.py`):
module-level `test_<name>() -> bool` functions that print `OK` / `FAIL: ...`
(no `assert`), plus `main() -> int` that sums the booleans and `sys.exit`s
non-zero on any failure. Stdlib only. Regexes anchor on the inner content
(mem-1781892715-142d). The gate discovers this file by glob
(`scripts/run_gate.py`), and `main()` sums the `TESTS` tuple — a function not
listed there would be green-by-omission (mem-1784137124-c346), so every `test_*`
below is registered in `TESTS`.
"""

import contextlib
import importlib.util
import io
import pathlib
import re
import shlex
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
RUNBOOK = REPO_ROOT / "docs" / "runbooks" / "plex-latency-baseline.md"
HARNESS = REPO_ROOT / "scripts" / "measure_plex_latency.py"

#: The harness script as it is invoked from the repo root.
INVOKES = "measure_plex_latency.py"


def _read(path: pathlib.Path) -> str:
    return path.read_text() if path.is_file() else ""


def _flat(body: str) -> str:
    # Collapse whitespace so assertions are robust to markdown line-wrapping.
    return " ".join(body.split())


def test_runbook_exists_and_nonempty() -> bool:
    body = _read(RUNBOOK)
    ok = len(body.strip()) > 0
    print(
        f"{'OK' if ok else 'FAIL'}: docs/runbooks/plex-latency-baseline.md exists "
        f"and is non-empty (chars={len(body)})"
    )
    return ok


def test_external_vantage_requirement() -> bool:
    """The baseline is off-LAN, and the runbook must say WHY, not just how.

    Requires the concrete vantage (mobile hotspot / LTE / cellular), the reason
    the LAN cannot serve (the request never leaves the LAN — no WAN path, no
    router hairpin), and the explicit demotion of a LAN run to a *control*.
    A bare `--vantage external` in a code block satisfies none of these: the
    flag is what the operator types, the paragraph is what stops them typing it
    from the sofa.
    """
    flat = _flat(_read(RUNBOOK))
    checks = {
        "external network named": re.search(
            r'\bexternal\s+network\b', flat, re.IGNORECASE
        )
        is not None,
        "mobile hotspot / LTE vantage": re.search(
            r'\b(?:mobile\s+hotspot|hotspot|LTE|cellular|4G|5G)\b', flat, re.IGNORECASE
        )
        is not None,
        "WAN path / hairpin reason": re.search(
            r'\bWAN\b|\bhairpin\w*\b|\bnever\s+leaves\s+the\s+LAN\b',
            flat,
            re.IGNORECASE,
        )
        is not None,
        # The demotion, stated as such: a LAN number is a control, not THE
        # baseline. Anchored on the literal claim rather than on `LAN` near
        # `control` — the string `baseline-lan-control` is a run LABEL in §3b
        # and would otherwise satisfy this check by coincidence.
        "LAN run demoted to a control": re.search(
            r'\bcontrol\b[^.]{0,250}?\bnot\s+the\s+baseline\b'
            r'|\bnot\s+the\s+baseline\b[^.]{0,250}?\bcontrol\b',
            flat,
            re.IGNORECASE,
        )
        is not None,
    }
    missing = [k for k, v in checks.items() if not v]
    ok = not missing
    print(
        f"{'OK' if ok else 'FAIL'}: runbook requires an EXTERNAL vantage and says "
        f"why a LAN run is only a control (missing={missing})"
    )
    return ok


def _table_rows(body: str) -> list[list[str]]:
    """Every markdown table row in the doc, as lists of stripped cells.

    Separator rows (`|---|---|`) are dropped; everything else is returned so a
    caller can pick out the header it cares about and the rows under it.
    """
    rows = []
    for line in body.splitlines():
        stripped = line.strip()
        if not stripped.startswith("|") or not stripped.endswith("|"):
            continue
        cells = [c.strip() for c in stripped.strip("|").split("|")]
        if all(re.fullmatch(r':?-{2,}:?', c) for c in cells if c):
            continue
        rows.append(cells)
    return rows


def test_results_table_is_present_and_unfilled() -> bool:
    """The plan's metric names, per endpoint, with every cell still a placeholder.

    Two claims in one check because they are the same claim: the table has to
    carry TTFB *and* total load time *and* min/median/max *and* the run's UTC
    timestamp + vantage, AND none of those cells may already hold a number.
    Step 1c (the operator) fills it; anything filled in here is invented data,
    and an invented baseline is worse than no baseline because Step 4 cannot
    tell the difference.
    """
    body = _read(RUNBOOK)
    flat = _flat(body)
    rows = _table_rows(body)

    header = None
    for index, cells in enumerate(rows):
        joined = " ".join(cells).lower()
        if "ttfb" in joined and "total" in joined:
            header = index
            break

    metrics = {}
    data_rows: list[list[str]] = []
    if header is not None:
        head = " ".join(rows[header]).lower()
        metrics = {
            "endpoint column": "endpoint" in head,
            "TTFB column": "ttfb" in head,
            "total load time column": "total" in head,
            "min/median/max": re.search(r'min\s*/?\s*med', head) is not None
            and re.search(r'max', head) is not None,
        }
        width = len(rows[header])
        for cells in rows[header + 1:]:
            if len(cells) != width:
                break
            data_rows.append(cells)

    # Every measured cell (all but the endpoint name) must still be a
    # placeholder: no digits, because a digit here is a fabricated measurement.
    filled = [
        cells
        for cells in data_rows
        for cell in cells[1:]
        if re.search(r'\d', cell)
    ]
    placeheld = bool(data_rows) and all(
        re.search(r'_{2,}|\bTBD\b|\bn/a\b', cell)
        for cells in data_rows
        for cell in cells[1:]
    )
    # The run's own stamp: without a UTC timestamp and a vantage, two filled
    # tables cannot be told apart, and Step 4 pairs runs by label + vantage.
    stamped = {
        "UTC timestamp line": re.search(r'\bUTC\b', flat) is not None,
        "vantage line": re.search(r'\bvantage\b', flat, re.IGNORECASE) is not None,
    }

    missing = [k for k, v in {**metrics, **stamped}.items() if not v]
    ok = header is not None and not missing and not filled and placeheld
    print(
        f"{'OK' if ok else 'FAIL'}: results table carries the plan's metrics and is "
        f"left UNFILLED (header={header is not None}, rows={len(data_rows)}, "
        f"missing={missing}, filled_cells={len(filled)}, placeheld={placeheld})"
    )
    return ok


def _documented_invocations(body: str) -> list[list[str]]:
    """Every `measure_plex_latency.py` command line the runbook prints, as argv.

    Only FENCED CODE BLOCKS are scanned — a prose mention of the script is not
    a command, and treating one as an invocation would make the check fail on
    the sentence that explains it. Shell line-continuations are joined, a
    leading `$` prompt and any `VAR=value` env prefix are stripped, and
    everything up to and including the script name is dropped — what is left is
    exactly what argparse would see.
    """
    text = re.sub(r'\\\n\s*', ' ', body)
    argvs = []
    in_fence = False
    for line in text.splitlines():
        if line.strip().startswith("```"):
            in_fence = not in_fence
            continue
        if not in_fence:
            continue
        stripped = line.strip().lstrip("$").strip()
        if INVOKES not in stripped or stripped.startswith("#"):
            continue
        try:
            words = shlex.split(stripped, comments=True)
        except ValueError:
            words = stripped.split()
        for index, word in enumerate(words):
            if word.endswith(INVOKES):
                argvs.append(_until_shell_operator(words[index + 1:]))
                break
    return argvs


#: Where the shell takes over from the command — argparse never sees past here.
SHELL_OPERATORS = ("|", "||", "&&", ";", ">", ">>", "2>", "2>&1", "&")


def _until_shell_operator(words: list[str]) -> list[str]:
    """Truncate argv at the first shell operator (a pipe, a redirect, a chain)."""
    for index, word in enumerate(words):
        if word in SHELL_OPERATORS:
            return words[:index]
    return words


def _load_parser(harness: pathlib.Path):
    """The harness's REAL argparse parser, loaded from the file under test."""
    spec = importlib.util.spec_from_file_location("_plex_latency_harness", harness)
    if spec is None or spec.loader is None:
        return None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module._parser()


def test_documented_invocations_match_the_real_harness(harness: pathlib.Path = HARNESS) -> bool:
    """CROSS-FILE: the documented commands must parse against the real parser.

    This is the check that earns its keep. A runbook command that has drifted
    from the harness's flags fails at the one moment nobody can retry it — the
    operator is on a hotspot, off-LAN, with one shot at a capture. So every
    documented invocation is fed to `measure_plex_latency.py`'s own
    `argparse` parser, and the two shapes the procedure depends on are pinned:

      * the EXTERNAL capture is `--vantage external` **with** `--skip-direct` —
        off-LAN the backend is RFC1918, and without the flag a perfectly good
        capture hangs for `repeats x timeout` and exits 1,
      * the direct-:32400 control is a SEPARATE `--vantage lan` run that does
        NOT skip the direct leg — that is the only run where the A/B exists.

    Reads two artifacts, so it reddens for a drift introduced on either side.
    `harness` is defaulted rather than hardcoded purely so the harness half can
    be proven load-bearing against a doctored copy.
    """
    body = _read(RUNBOOK)
    argvs = _documented_invocations(body)
    parser = _load_parser(harness)

    parsed, unparsed = [], []
    for argv in argvs:
        if parser is None:
            unparsed.append(argv)
            continue
        buffer = io.StringIO()
        try:
            with contextlib.redirect_stderr(buffer), contextlib.redirect_stdout(buffer):
                parsed.append((argv, parser.parse_args(argv)))
        except SystemExit:
            unparsed.append(argv)

    # Parsing alone is NOT cross-file agreement: argparse accepts unambiguous
    # ABBREVIATIONS, so a documented `--skip-direct` parses happily against a
    # parser whose flag has been renamed to `--skip-direct-leg` — the rename
    # lands in the namespace, not in an error. Pin the literal option strings
    # so a rename on either side reddens.
    known = set()
    for action in getattr(parser, "_actions", []):
        known.update(action.option_strings)
    documented = {word for argv in argvs for word in argv if word.startswith("-")}
    unknown = sorted(documented - known)

    external = [ns for _, ns in parsed if getattr(ns, "vantage", None) == "external"]
    lan = [ns for _, ns in parsed if getattr(ns, "vantage", None) == "lan"]
    checks = {
        "runbook prints >=2 invocations": len(argvs) >= 2,
        "every documented invocation parses": bool(argvs) and not unparsed,
        "every documented flag is a real option string": bool(documented)
        and not unknown,
        "an external capture is documented": bool(external),
        "external capture passes --skip-direct": bool(external)
        and all(getattr(ns, "skip_direct", False) for ns in external),
        "external capture is labelled baseline": bool(external)
        and any(getattr(ns, "label", None) == "baseline" for ns in external),
        "a separate LAN control run is documented": bool(lan),
        "LAN control keeps the direct leg": bool(lan)
        and any(not getattr(ns, "skip_direct", True) for ns in lan),
    }
    missing = [k for k, v in checks.items() if not v]
    ok = not missing
    print(
        f"{'OK' if ok else 'FAIL'}: documented invocations parse against "
        f"{harness.name} and carry the external/LAN split "
        f"(found={len(argvs)}, rejected={unparsed}, unknown_flags={unknown}, "
        f"missing={missing})"
    )
    return ok


def test_no_literal_token_in_the_runbook() -> bool:
    """`$PLEX_TOKEN` from the environment, never a pasted value.

    The harness has no `--token` flag on purpose. A runbook that shows a real
    token teaches the operator to paste one, and a pasted one lands in shell
    history or — the road this check actually guards — in a commit.
    """
    body = _read(RUNBOOK)
    flat = _flat(body)
    # Any PLEX_TOKEN assignment must assign a placeholder, not a value.
    assignments = re.findall(r'PLEX_TOKEN=(\S*)', body)
    bad_assignments = [
        value
        for value in assignments
        if re.fullmatch(r'[A-Za-z0-9]{8,}', value.strip('"\''))
    ]
    # A Plex token is a ~20-char mixed alphanumeric string; refuse anything
    # token-shaped anywhere in the doc, assignment or not.
    tokenish = [
        word
        for word in re.findall(r'\b[A-Za-z0-9]{19,25}\b', body)
        if re.search(r'[A-Za-z]', word) and re.search(r'\d', word)
    ]
    checks = {
        "reads the token from the environment": re.search(
            r'\$?PLEX_TOKEN', flat
        )
        is not None,
        "warns against committing the token": re.search(
            r'(?:never|do not|don\'t)\b.{0,120}?(?:commit|paste|repo|repository|version control)',
            flat,
            re.IGNORECASE,
        )
        is not None,
        "no literal PLEX_TOKEN value": not bad_assignments,
        "no token-shaped literal anywhere": not tokenish,
    }
    missing = [k for k, v in checks.items() if not v]
    ok = not missing
    print(
        f"{'OK' if ok else 'FAIL'}: runbook keeps the token in $PLEX_TOKEN and "
        f"carries no literal value (missing={missing}, "
        f"assignments={bad_assignments}, tokenish={tokenish})"
    )
    return ok


TESTS = (
    test_runbook_exists_and_nonempty,
    test_external_vantage_requirement,
    test_results_table_is_present_and_unfilled,
    test_documented_invocations_match_the_real_harness,
    test_no_literal_token_in_the_runbook,
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
