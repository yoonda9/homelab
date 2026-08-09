#!/usr/bin/env python3
"""Runtime gate for the plex-blip alert rules (plex-blip-manual-triage Step 7d).

The alert clauses in `scripts/test_traefik_config_shape.py` are STATIC: they
parse the rendered template and hold its shape. They cannot answer whether
Prometheus itself accepts the file, nor whether an alert actually FIRES — an
alert loads at `promtool` rc=0 and fires never whether its `job=` names nothing
or its threshold is a thousand times too high (mem: an == 0 alert cannot match an
absent series). So this file runs the real validator and a real simulated clock:

  1. `promtool check rules` on the rendered file — rc=0, "N rules found"
     (plan.md's first Tests bullet: "add to just test").
  2. `promtool test rules` on a unit suite built against that same render —
     `plex_sqlite_wal_bytes` at 43,735,168 for 15 m FIRES `PlexSqliteWalOversized`
     and a 2 MiB series does NOT (plan.md's third Tests bullet).

BOTH run out of the PINNED image via the `docker_host_prometheus_image` relation
read from `ansible/roles/docker_host/defaults/main.yml` — never a re-spelled tag
and never a host `promtool` binary (acceptance 5). `promtool test rules` runs a
SIMULATED clock, so the `for: 15 m` arm is exercised in test-rules time rather
than wall clock (acceptance 6; mem: plex-watchdog-debounce-hides-per-line-diffs).

THE UNIT SUITE IS BUILT FROM THE RENDER, NOT SPELLED BESIDE IT. `promtool test
rules` compares the produced alert's labels AND annotations exactly, so a hand
copy of `PlexSqliteWalOversized`'s `severity` and `summary` into this file would
be the "two literals that agree" class the whole suite guards against — a reword
of the shipped summary would leave this oracle green over a stale expectation.
Instead `expected_labels`/`expected_annotations` are READ from the rendered rule,
so the firing expectation moves with the file. What is genuinely THIS test's own
input — the 43,735,168 B live fault, the 2 MiB control, and the 15 m eval — are
named constants below; everything else is derived. The generated suite is written
to `logs/` for a human to inspect and re-run by hand.

NO VACUOUS SKIP. This repo has paid twice for a `try/except … skip` that read
green over a check that never ran, so a missing `docker`, a missing image, or
Jinja that survives rendering is a FAIL here, not a skip. The one measured trap
this rig dodges is the uid: `prom/prometheus:v3.12.0` runs as `nobody`
(uid 65534), so a default-0700 `mkdtemp` mount answers `permission denied`
UNIFORMLY and reads exactly like the binary refusing every document. The temp dir
is chmod 0755 and its files 0644 before the mount, and a positive `check rules` is
the control that the rig is live before any `test rules` verdict is trusted.

Dual-mode (module-level `test_*() -> bool` + `main() -> int`), mirroring the
other `scripts/test_*.py` shape tests so `run_gate.py`'s glob auto-includes it as
one more step inside the gate count (acceptance 4).
"""

import pathlib
import re
import subprocess
import sys
import tempfile

import yaml

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
ROLE = REPO_ROOT / "ansible" / "roles" / "docker_host"
DEFAULTS = ROLE / "defaults" / "main.yml"
RULES_TEMPLATE = ROLE / "templates" / "plex-blip-rules.yml.j2"
LOGS = REPO_ROOT / "logs"

# The relation, not a literal: the image promtool runs out of is whatever the
# role ships to the docker host, read from defaults so a bump there moves this
# gate with it rather than leaving a second copy to drift (the c6c4/e627 class).
PROM_IMAGE_VAR = "docker_host_prometheus_image"
# The basename the generated suite's `rule_files:` names; the render is written
# here so the two sit together in the mounted dir.
RENDERED_RULES_BASENAME = "plex-blip-rules.yml"
UNIT_SUITE_BASENAME = "plex-blip-rules.unit.yml"

# --- THIS test's own inputs (everything else is read from the render) ---------
WAL_ALERT = "PlexSqliteWalOversized"
WAL_METRIC = "plex_sqlite_wal_bytes"
# The real value CT 110's Step 3 Demo reded at: the WAL guard aborted the play at
# `43,735,168 > 8,388,608`. Validating the alert against a KNOWN-LIVE fault before
# it is trusted on an unknown one is the Demo's whole point (plan.md:554-555).
WAL_LIVE_BYTES = 43_735_168
# 2 MiB — below the 8 MiB threshold, so the rule is never even pending: the
# healthy control that a rule firing unconditionally would fail.
WAL_HEALTHY_BYTES = 2 * 1024 * 1024
# 1 m interval, so the `> 8,388,608` comparison is true from t=0 and the
# `for: 15 m` clears at exactly eval_time 15 m (measured on v3.12.0). `x20`
# carries the series past 15 m for the firing leg and gives the control room too.
UNIT_INTERVAL = "1m"
UNIT_SAMPLES = 20
UNIT_EVAL_TIME = "15m"


def _read(path: pathlib.Path) -> str:
    return path.read_text() if path.is_file() else ""


def _prometheus_image() -> str | None:
    """`docker_host_prometheus_image` from role defaults, or None if unreadable.

    A line reader rather than a full `yaml.safe_load` of the whole file so an
    unrelated parse issue elsewhere in defaults cannot take this key down with it;
    the value is a plain scalar (`prom/prometheus:v3.12.0`).
    """
    for line in _read(DEFAULTS).splitlines():
        m = re.match(rf"\s*{re.escape(PROM_IMAGE_VAR)}\s*:\s*(\S+)\s*$", line)
        if m:
            return m.group(1).strip().strip("'\"")
    return None


def _render_rules() -> tuple[str | None, str | None]:
    """The template with its one Jinja reference substituted, or (None, why).

    `plex-blip-rules.yml.j2` carries exactly one construct — `{{ ansible_managed
    }}` on a comment line. Substituting it to a plain scalar preserves the
    document's structure. Any Jinja that SURVIVES is a fail, not a silent pass:
    promtool would choke on it and the reason must be legible.
    """
    body = _read(RULES_TEMPLATE)
    if not body:
        return None, f"{RULES_TEMPLATE} is empty or absent"
    rendered = body.replace(
        "{{ ansible_managed }}", "Ansible managed: plex-blip-rules.yml")
    leftover = re.findall(r"\{\{.*?\}\}|\{%.*?%\}", rendered)
    if leftover:
        return None, f"unrendered Jinja survives: {leftover}"
    return rendered, None


def _wal_rule(rendered: str) -> tuple[dict | None, str | None]:
    """The `PlexSqliteWalOversized` rule dict out of the rendered file."""
    try:
        doc = yaml.safe_load(rendered)
    except yaml.YAMLError as exc:
        return None, f"render does not parse: {str(exc).splitlines()[0]}"
    groups = (doc or {}).get("groups") if isinstance(doc, dict) else None
    rules = groups[0].get("rules") if isinstance(groups, list) and groups else None
    if not isinstance(rules, list):
        return None, "rendered file carries no rules list"
    for r in rules:
        if isinstance(r, dict) and r.get("alert") == WAL_ALERT:
            return r, None
    return None, f"{WAL_ALERT} is absent from the render"


def _build_unit_suite(rendered: str) -> tuple[str | None, str | None]:
    """The `promtool test rules` YAML, with exp_alerts READ from the render."""
    rule, why = _wal_rule(rendered)
    if rule is None:
        return None, why
    # promtool auto-adds `alertname`; exp_labels is the rule's OWN labels and
    # exp_annotations its annotations, so the two match the produced alert exactly
    # because they are the same bytes promtool parses from the render.
    exp_labels = rule.get("labels") if isinstance(rule.get("labels"), dict) else {}
    exp_anns = rule.get("annotations") if isinstance(
        rule.get("annotations"), dict) else {}
    if not exp_labels or not exp_anns:
        return None, (
            f"{WAL_ALERT} is missing labels/annotations (labels={exp_labels}, "
            f"annotations={exp_anns}) — Step 7d must ship both before this "
            "oracle can assert the produced alert"
        )
    suite = {
        "rule_files": [RENDERED_RULES_BASENAME],
        "evaluation_interval": UNIT_INTERVAL,
        "tests": [
            {
                "name": f"{WAL_METRIC} held at the live {WAL_LIVE_BYTES:,} B for "
                        f"{UNIT_EVAL_TIME} fires {WAL_ALERT}",
                "interval": UNIT_INTERVAL,
                "input_series": [
                    {"series": WAL_METRIC,
                     "values": f"{WAL_LIVE_BYTES}+0x{UNIT_SAMPLES}"},
                ],
                "alert_rule_test": [
                    {"eval_time": UNIT_EVAL_TIME, "alertname": WAL_ALERT,
                     "exp_alerts": [
                         {"exp_labels": exp_labels, "exp_annotations": exp_anns}]},
                ],
            },
            {
                "name": f"{WAL_METRIC} at {WAL_HEALTHY_BYTES:,} B never fires "
                        f"{WAL_ALERT}",
                "interval": UNIT_INTERVAL,
                "input_series": [
                    {"series": WAL_METRIC,
                     "values": f"{WAL_HEALTHY_BYTES}+0x{UNIT_SAMPLES}"},
                ],
                "alert_rule_test": [
                    {"eval_time": UNIT_EVAL_TIME, "alertname": WAL_ALERT,
                     "exp_alerts": []},
                ],
            },
        ],
    }
    return yaml.safe_dump(suite, sort_keys=False, allow_unicode=True), None


def _docker_promtool(image, mount, args):
    """Run `promtool <args>` out of `image` with `mount` bound read-only at /work."""
    cmd = [
        "docker", "run", "--rm",
        "-v", f"{mount}:/work:ro",
        "--entrypoint", "promtool",
        image,
        *args,
    ]
    return subprocess.run(cmd, capture_output=True, text=True)


def _run(log) -> bool:
    image = _prometheus_image()
    if not image:
        return _fail(log, (
            f"cannot read {PROM_IMAGE_VAR} from {DEFAULTS} — the image relation "
            "is the source of the promtool binary and there is no fallback "
            "(acceptance 5)"))
    if not _which("docker"):
        return _fail(log, (
            f"`docker` is not on PATH — this gate runs promtool out of the pinned "
            f"{image} and does NOT skip when docker is absent (a skip would be the "
            "vacuous green this suite is built to refuse)"))

    rendered, why = _render_rules()
    if rendered is None:
        return _fail(log, why)
    suite, why = _build_unit_suite(rendered)
    if suite is None:
        return _fail(log, why)

    LOGS.mkdir(exist_ok=True)
    (LOGS / UNIT_SUITE_BASENAME).write_text(suite)  # human-inspectable copy

    with tempfile.TemporaryDirectory() as tmp:
        mount = pathlib.Path(tmp)
        (mount / RENDERED_RULES_BASENAME).write_text(rendered)
        (mount / UNIT_SUITE_BASENAME).write_text(suite)
        # uid 65534 trap: 0755 dir + 0644 files or promtool is permission-denied.
        mount.chmod(0o755)
        for p in mount.iterdir():
            p.chmod(0o644)

        # 1. check rules — the control: if the rig is dead (image gone, uid trap)
        #    this reds first and no `test rules` verdict is trusted over it.
        chk = _docker_promtool(
            image, mount, ["check", "rules", f"/work/{RENDERED_RULES_BASENAME}"])
        log.write(f"$ promtool check rules ({image})\nrc={chk.returncode}\n"
                  f"{chk.stdout}{chk.stderr}\n")
        check_ok = chk.returncode == 0 and "rules found" in chk.stdout
        tail = (chk.stdout.strip().splitlines() or [chk.stderr.strip()])[-1]
        print(f"{'OK' if check_ok else 'FAIL'}: promtool check rules "
              f"(rc={chk.returncode}) — {tail}")
        if not check_ok:
            print(chk.stdout + chk.stderr)
            return False

        # 2. test rules — the firing suite against that same render.
        tst = _docker_promtool(
            image, mount, ["test", "rules", f"/work/{UNIT_SUITE_BASENAME}"])
        log.write(f"$ promtool test rules ({image})\nrc={tst.returncode}\n"
                  f"{tst.stdout}{tst.stderr}\n")
        test_ok = tst.returncode == 0 and "SUCCESS" in tst.stdout
        out = tst.stdout.strip() or tst.stderr.strip()
        tail = out.splitlines()[-1] if out else "(no output)"
        print(f"{'OK' if test_ok else 'FAIL'}: promtool test rules "
              f"(rc={tst.returncode}) — {WAL_ALERT} fires at {WAL_LIVE_BYTES:,} B "
              f"for {UNIT_EVAL_TIME}, silent at {WAL_HEALTHY_BYTES:,} B — {tail}")
        if not test_ok:
            print(tst.stdout + tst.stderr)
        return check_ok and test_ok


def _which(name: str):
    import shutil
    return shutil.which(name)


def _fail(log, why: str) -> bool:
    msg = f"FAIL: {why}"
    print(msg)
    log.write(msg + "\n")
    return False


def test_promtool_check_and_test_rules_pass_on_the_render() -> bool:
    """Step-7d acceptance 3/4/5/6: promtool validates AND unit-tests the render."""
    LOGS.mkdir(exist_ok=True)
    print("\n=== plex-blip alert rules — promtool check + test ===")
    with (LOGS / "builder-7d-promtool.log").open("w") as log:
        return _run(log)


def main() -> int:
    results = [
        test_promtool_check_and_test_rules_pass_on_the_render(),
    ]
    total, passed = len(results), sum(results)
    if passed == total:
        print(f"\nPASS: {passed}/{total}")
        return 0
    print(f"\nFAIL: {total - passed}/{total} checks failed")
    return 1


if __name__ == "__main__":
    sys.exit(main())
