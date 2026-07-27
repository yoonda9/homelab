"""Shape test for Step 1b — the off-LAN Plex latency baseline runbook.

Per `.agents/planning/2026-07-27-plex-optimization/implementation/plan.md`
Step 1 (and `.ralph/specs/plex-optimization/plan.md`'s wave split) — verifies
`docs/runbooks/plex-latency-baseline.md` documents the OPERATOR procedure for
capturing the baseline that Step 4 is compared against:

  * the **external-network requirement** and its reason — from the LAN the
    request never crosses the WAN path or the router hairpin, so a LAN number is
    a *control*, not the baseline. This is the single most misread part of the
    plan, so it is pinned as prose, not as a flag,
  * a **results section** carrying the plan's own metric names (TTFB and total
    load time, per endpoint, min/median/max) plus the run's UTC timestamp and
    vantage — and left **UNFILLED**, because a fabricated baseline silently
    invalidates Step 4's whole comparison. The prohibition is stated once, at
    the `## 5.` heading, and §5 holds THREE tables plus the LAN-control
    headline, so the guard is scoped to the SECTION and not to the one table a
    header regex can recognise (mem-1785131238-5b83),
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
without touching the closed, committed harness itself. It compiles the harness
FROM SOURCE rather than importing it by spec, because the obvious loader reads
`__pycache__` and would grade bytecode that is not on disk (mem-1785131222-b87c).

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
import io
import pathlib
import re
import shlex
import sys
import types

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


def _section(body: str, number: int) -> str:
    """The doc between `## <number>.` and the next SAME-LEVEL `##` heading.

    `###` subheadings stay inside — `^##\\s` needs whitespace after exactly two
    hashes — which is the point: §5's three tables each live under their own
    `###` head, and the prohibition is stated once, at the `##`.
    """
    out, inside = [], False
    for line in body.splitlines():
        if re.match(rf'^##\s+{number}\.', line):
            inside = True
            continue
        if inside and re.match(r'^##\s', line):
            break
        if inside:
            out.append(line)
    return "\n".join(out)


def _tables(body: str) -> list[list[list[str]]]:
    """Every markdown table in `body`, as `[header_cells, *data_rows]`.

    A table is a MAXIMAL RUN of consecutive table lines — a blank line, prose or
    a heading ends one and starts the next. Separator rows (`|---|---|`) are
    dropped from the run without breaking it. Returning tables rather than a
    flat list of rows is what lets a caller assert HOW MANY there are.
    """
    tables: list[list[list[str]]] = []
    current: list[list[str]] = []
    for line in body.splitlines():
        stripped = line.strip()
        if not (stripped.startswith("|") and stripped.endswith("|")):
            if current:
                tables.append(current)
                current = []
            continue
        cells = [c.strip() for c in stripped.strip("|").split("|")]
        if all(re.fullmatch(r':?-{2,}:?', c) for c in cells if c):
            continue
        current.append(cells)
    if current:
        tables.append(current)
    return tables


#: The section that carries the prohibition — `## 5. RESULTS`.
RESULTS_SECTION = 5

#: How many tables §5 governs: Run metadata, Harness results, Browser DevTools.
#: ASSERTED, not discovered. The predicate below runs over every table in the
#: section, so a table added later is covered automatically — but a table added
#: later is also a claim about what the baseline contains, and this number is
#: what forces whoever adds it to come back here (mem-1785131238-5b83).
EXPECTED_RESULT_TABLES = 3

#: A cell that has NOT been filled in: `___`, `TBD`, `n/a`, or a `/`-separated
#: run of them (`___ / ___ / ___`), optionally in backticks. Anything else in a
#: measured column — a digit above all — is a number nobody measured.
PLACEHOLDER = re.compile(
    r'[`\s]*(?:_{2,}|TBD|n/a)(?:\s*/\s*(?:_{2,}|TBD|n/a))*[`\s]*', re.IGNORECASE
)

#: Rows §5 owes, matched against the FIRST COLUMN of every table in the section.
#: A placeholder guard with no existence pin is satisfied by DELETING the row —
#: "no filled cells" is trivially true of a table that is not there. Matching
#: across all of §5's tables rather than per-table keeps this from also pinning
#: which table a field lives in.
REQUIRED_ROWS = {
    "UTC timestamp row": r'\bUTC\b',
    "vantage row": r'\bvantage\b',
    "network row": r'\bnetwork\b',
    "label row": r'\blabel\b',
    "repeats row": r'\brepeats\b',
    "a traefik endpoint row": r'\btraefik\s*/',
    "a direct-:32400 endpoint row": r'\bdirect\s*/',
    "initial-document TTFB row": r'\bdocument\b[^|]*\bTTFB\b',
    "/library/sections XHR row": r'/library/sections\b[^|]*\bXHR\b',
    "DOMContentLoaded row": r'\bDOMContentLoaded\b',
    "Load row": r'\bLoad\b',
    "requests / transferred row": r'\brequests\b',
}


def test_results_section_is_present_and_unfilled() -> bool:
    """§5's cells are ALL still placeholders — every table, not one of three.

    §5 opens with *"Leave every cell as `___` until a real capture has been
    taken. Do not estimate, interpolate or copy a number from a LAN run"* and
    then holds THREE tables: Run metadata, Harness results, and the Browser
    DevTools numbers that are the plan's own Demo metric. The prohibition is
    stated at the SECTION, so the predicate is scoped to the SECTION — sliced
    between `## 5.` and the next `##` — and applied to every table inside.
    Scoping it instead to the one table a header regex can recognise left a
    complete invented DevTools baseline, and an invented run stamp, both GREEN
    (mem-1785131238-5b83).

    Three claims, all of them the same claim — that Step 4 diffs against a
    MEASUREMENT and can never tell an invented one from a real one:

      * the harness table carries the plan's metric names (endpoint, TTFB,
        total, min/median/max),
      * §5 still holds the rows it owes — the run stamp (UTC timestamp,
        vantage, network, label, repeats), both legs of the A/B, and the five
        DevTools numbers — because a placeholder guard alone is satisfied by
        deleting the row,
      * and every measured cell in every table, plus the LAN-control headline
        that is the one number Step 4 actually reads, is still a placeholder.

    Step 1c (the operator) fills these in. Anything filled in here is invented.
    """
    body = _read(RUNBOOK)
    section = _section(body, RESULTS_SECTION)
    tables = _tables(section)
    flat = _flat(section)

    # The harness table, by the metric names the plan itself uses. Its header is
    # a REQUIREMENT of the section, not the boundary of the guard below.
    metrics = {"harness results table (TTFB + total)": False}
    for cells in (t[0] for t in tables):
        head = " ".join(cells).lower()
        if "ttfb" in head and "total" in head:
            metrics = {
                "endpoint column": "endpoint" in head,
                "TTFB column": "ttfb" in head,
                "total load time column": "total" in head,
                "min/median/max": re.search(r'min\s*/?\s*med', head) is not None
                and re.search(r'max', head) is not None,
            }
            break

    # Every table's first row is its header; every row after it is data, and
    # every column after the first is a MEASURED column.
    data_rows = [cells for table in tables for cells in table[1:]]
    measured = [cell for cells in data_rows for cell in cells[1:]]
    filled = [cell for cell in measured if re.search(r'\d', cell)]
    unheld = [cell for cell in measured if not PLACEHOLDER.fullmatch(cell)]

    first_column = " | ".join(cells[0] for cells in data_rows)
    present = {
        name: re.search(pattern, first_column, re.IGNORECASE) is not None
        for name, pattern in REQUIRED_ROWS.items()
    }

    # The headline the A/B exists for lives in §5 as prose, not in a table, and
    # is the single number Step 4 reads. Same prohibition, so same predicate.
    headline = re.search(r'Traefik\s+overhead\b.{0,160}?\bms\b', flat, re.IGNORECASE)
    structure = {
        "§5 section found": bool(section.strip()),
        f"§5 holds {EXPECTED_RESULT_TABLES} tables": len(tables)
        == EXPECTED_RESULT_TABLES,
        "every table has data rows": bool(tables)
        and all(len(t) > 1 for t in tables),
        "LAN-control headline present": headline is not None,
        "LAN-control headline unfilled": headline is not None
        and not re.search(r'\d', headline.group())
        and re.search(r'_{2,}', headline.group()) is not None,
    }

    missing = [k for k, v in {**structure, **metrics, **present}.items() if not v]
    ok = not missing and not filled and not unheld
    print(
        f"{'OK' if ok else 'FAIL'}: §{RESULTS_SECTION} carries the plan's metrics and "
        f"is left UNFILLED (tables={len(tables)}, rows={len(data_rows)}, "
        f"cells={len(measured)}, missing={missing}, filled_cells={filled}, "
        f"not_placeheld={unheld})"
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
    """The harness's REAL argparse parser, compiled FROM ITS SOURCE TEXT.

    Deliberately NOT `importlib.util.spec_from_file_location` + `exec_module`,
    for the same reason its sibling `test_plex_latency_harness_shape.py::_load_harness`
    refuses it: that loader consults `__pycache__`, whose cache key is
    `(source mtime truncated to whole SECONDS, source size)`. A mutation matrix
    — the one instrument whose entire job is detecting false greens — poisons it
    in both directions, and this check is the load-bearing one, so both land
    here (mem-1785131222-b87c, mem-1785122728-5116):

      * FALSE GREEN — write a SAME-SIZE drift (`VANTAGES` `lan` -> `wan`, so the
        harness stops accepting the `--vantage lan` §3b documents) and restore
        the mtime; the stale `.pyc` still validates and this check prints `OK`
        against a real cross-file drift,
      * FALSE RED — compile the drift under the pristine mtime, then restore the
        bytes (exactly what `shutil.copy2` does on a matrix restore); the source
        is byte-identical to git, `git status` is clean, and `just test` goes
        `GATE PASS` -> `GATE FAIL` forever.

    `scripts/run_gate.py` execs shape tests as `[sys.executable, path]` with no
    `-B`, and `-B` would not help anyway — it stops the cache being WRITTEN, not
    being READ. `compile()` over the text read from disk has no cache to
    consult, so the artifact graded is the artifact in git, always.
    """
    module = types.ModuleType("_plex_latency_harness")
    module.__file__ = str(harness)
    source = harness.read_text(encoding="utf-8") if harness.is_file() else ""
    if not source:
        return None
    exec(compile(source, str(harness), "exec"), module.__dict__)  # noqa: S102
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
    test_results_section_is_present_and_unfilled,
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
