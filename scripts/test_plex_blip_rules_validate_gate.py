#!/usr/bin/env python3
"""Runtime gate: the Step-7c `validate:` actually REJECTS a bad rules render.

The static clause `test_plex_blip_rules_render_is_validated_against_the_pinned_image`
in `scripts/test_traefik_config_shape.py` proves the render task CARRIES a
`validate:` that names `promtool check rules` and the pinned-image variable. What
it cannot prove is that the command WORKS: a `validate: /bin/true %s`, or a
promtool invocation pointed at the wrong path, or a validator that reads the
render but exits 0 on garbage, all pass a static "carries check rules" test while
gating nothing. That is the vacuous-guard class this repo has paid for repeatedly
(a door proved against a REFUSES list is half a door).

So this file lifts the EXACT command ansible will run out of `tasks/main.yml` —
the same folded `validate:` scalar, with `{{ docker_host_prometheus_image }}`
substituted from role defaults and `%s` substituted with a fixture path, exactly
as `ansible.builtin.template` does — and drives it both ways:

  * GOOD render (the shipped `plex-blip-rules.yml.j2`, Jinja substituted) -> rc 0,
    "SUCCESS: N rules found". The anti-vacuity control: the gate must ACCEPT the
    file the role actually ships, or it would block every honest deploy.
  * BAD render (one unparseable `expr`) -> rc != 0, "could not parse expression".
    The load-bearing leg: this is precisely the input that leaves the live
    container `exited` under `restart: unless-stopped` (mem: a malformed rules
    file does not degrade prometheus, it STOPS it), so a `validate:` that lets it
    through is a gate that never closes.

Because it runs the SHIPPED command verbatim, it also re-measures the two facts
the command depends on: the validator is the pinned image's promtool (a broken
image name reds the GOOD leg), and `--user 0:0` reads the root-owned 0600 temp
(the default `nobody` uid answers `permission denied` on it, which would red the
GOOD leg identically — measured, `logs/builder-7c-uid-trap.log`).

NO VACUOUS SKIP. A missing `docker`, an unreadable image variable, or a validate
command that cannot be parsed out of the task is a FAIL, not a skip — a skip is
the green-over-a-check-that-never-ran this suite exists to refuse. Dual-mode
(`test_*() -> bool` + `main() -> int`) so `run_gate.py`'s glob auto-includes it.
"""

import pathlib
import re
import shlex
import shutil
import subprocess
import sys
import tempfile

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
ROLE = REPO_ROOT / "ansible" / "roles" / "docker_host"
TASKS = ROLE / "tasks" / "main.yml"
DEFAULTS = ROLE / "defaults" / "main.yml"
RULES_TEMPLATE = ROLE / "templates" / "plex-blip-rules.yml.j2"
LOGS = REPO_ROOT / "logs"

PROM_IMAGE_VAR = "docker_host_prometheus_image"
RULES_SRC = "plex-blip-rules.yml.j2"
# The fixture basename the command's `%s` is replaced with; the mount target
# inside the container is whatever the shipped command names, so this is only the
# host-side file the temp render stands in for.
FIXTURE_BASENAME = "plex-blip-rules.yml"


def _read(path: pathlib.Path) -> str:
    return path.read_text() if path.is_file() else ""


def _prometheus_image() -> str | None:
    """`docker_host_prometheus_image` from role defaults, or None if unreadable."""
    for line in _read(DEFAULTS).splitlines():
        m = re.match(rf"\s*{re.escape(PROM_IMAGE_VAR)}\s*:\s*(\S+)\s*$", line)
        if m:
            return m.group(1).strip().strip("'\"")
    return None


def _render_task_block(body: str, src: str) -> str:
    """The `ansible.builtin.template` task rendering `src` (see the shape suite)."""
    ms = list(re.finditer(rf'(?m)^\s*src:\s*{re.escape(src)}\s*$', body))
    if len(ms) != 1:
        return ""
    start = body.rfind("\n- name:", 0, ms[0].start())
    if start == -1:
        return ""
    end = body.find("\n- ", start + 1)
    return body[start:end if end != -1 else len(body)]


def _validate_command(task: str) -> str | None:
    """The `validate:` folded scalar joined to one line, or None — the same fold
    `_render_task_validate` performs in the shape suite, kept here so this gate
    reads the task independently rather than importing the file it cross-checks."""
    m = re.search(r'(?m)^([ \t]*)validate:[ \t]*(.*?)[ \t]*\r?$', task or "")
    if not m:
        return None
    key_indent = len(m.group(1).expandtabs())
    head = m.group(2).strip()
    parts = [] if re.fullmatch(r'[>|][+-]?', head) else ([head] if head else [])
    for line in task[m.end():].splitlines():
        if not line.strip():
            continue
        lead = line[: len(line) - len(line.lstrip(" \t"))]
        if len(lead.expandtabs()) <= key_indent:
            break
        parts.append(line.strip())
    return " ".join(parts) if parts else None


def _render_good_rules() -> tuple[str | None, str | None]:
    """The shipped template with its one `{{ ansible_managed }}` substituted."""
    body = _read(RULES_TEMPLATE)
    if not body:
        return None, f"{RULES_TEMPLATE} is empty or absent"
    rendered = body.replace(
        "{{ ansible_managed }}", "Ansible managed: plex-blip-rules.yml")
    leftover = re.findall(r"\{\{.*?\}\}|\{%.*?%\}", rendered)
    if leftover:
        return None, f"unrendered Jinja survives: {leftover}"
    return rendered, None


def _bad_rules() -> str:
    """A rules document with one unparseable `expr` — valid YAML, invalid PromQL,
    which is exactly the leg that leaves the live container `exited`."""
    return (
        "groups:\n"
        "  - name: plex-blip\n"
        "    rules:\n"
        "      - alert: Broken\n"
        "        expr: this is ) not ( a valid promql expression\n"
        "        for: 1m\n"
    )


def _resolve(cmd: str, image: str, fixture: pathlib.Path) -> list[str]:
    """The shipped `validate:` string as ansible would run it: image variable and
    `%s` substituted, split into argv. `%s` is done with a literal replace (not
    `%`-formatting) so a stray `%` elsewhere in the command cannot corrupt it —
    ansible substitutes the single `%s` the same way."""
    resolved = re.sub(
        r'\{\{\s*' + re.escape(PROM_IMAGE_VAR) + r'\s*\}\}', image, cmd)
    resolved = resolved.replace("%s", str(fixture))
    return shlex.split(resolved)


def _run(log) -> bool:
    image = _prometheus_image()
    if not image:
        return _fail(log, (
            f"cannot read {PROM_IMAGE_VAR} from {DEFAULTS} — the image relation is "
            "the source of the validator and there is no fallback"))
    if not shutil.which("docker"):
        return _fail(log, (
            "`docker` is not on PATH — this gate runs the shipped validate command "
            "and does NOT skip when docker is absent (a skip would be vacuous green)"))

    task = _render_task_block(_read(TASKS), RULES_SRC)
    cmd = _validate_command(task)
    if not cmd:
        return _fail(log, (
            f"no `validate:` on the {RULES_SRC} render task in {TASKS} — the whole "
            "point of Step 7c is that the render cannot reach the process unvalidated"))
    if "%s" not in cmd:
        return _fail(log, (
            f"the validate command names no `%s` — it validates a fixed path, not "
            f"the render ansible is about to copy: {cmd!r}"))
    log.write(f"shipped validate command:\n{cmd}\nimage={image}\n\n")

    good, why = _render_good_rules()
    if good is None:
        return _fail(log, why)

    ok = True
    with tempfile.TemporaryDirectory() as tmp:
        d = pathlib.Path(tmp)
        d.chmod(0o755)
        # 0600, REPRODUCING ansible's own temp render (not a convenience 0644):
        # `prom/prometheus` runs as `nobody`, so the shipped command's `--user 0:0`
        # is what lets it read this file. A mutant dropping `--user 0:0` reds the
        # GOOD leg with `permission denied` — that is what ARMS the uid fix rather
        # than papering over it with a world-readable fixture the trap never bites.
        # GOOD leg — the anti-vacuity control: the gate must ACCEPT what ships.
        gf = d / FIXTURE_BASENAME
        gf.write_text(good)
        gf.chmod(0o600)
        gproc = subprocess.run(
            _resolve(cmd, image, gf), capture_output=True, text=True)
        gtail = (gproc.stdout.strip().splitlines()
                 or [gproc.stderr.strip()])[-1] if (gproc.stdout or gproc.stderr) else ""
        log.write(f"$ GOOD render\nrc={gproc.returncode}\n{gproc.stdout}{gproc.stderr}\n")
        good_ok = gproc.returncode == 0
        print(f"{'OK' if good_ok else 'FAIL'}: shipped validate ACCEPTS the shipped "
              f"rules (rc={gproc.returncode}) — {gtail}")
        if not good_ok:
            print(gproc.stdout + gproc.stderr)
        ok = ok and good_ok

        # BAD leg — the load-bearing one: an unparseable expr must be rejected.
        bf = d / FIXTURE_BASENAME
        bf.write_text(_bad_rules())
        bf.chmod(0o600)
        bproc = subprocess.run(
            _resolve(cmd, image, bf), capture_output=True, text=True)
        btail = (bproc.stderr.strip().splitlines()
                 or [bproc.stdout.strip()])[-1] if (bproc.stdout or bproc.stderr) else ""
        log.write(f"$ BAD render\nrc={bproc.returncode}\n{bproc.stdout}{bproc.stderr}\n")
        bad_ok = bproc.returncode != 0
        print(f"{'OK' if bad_ok else 'FAIL'}: shipped validate REJECTS an unparseable "
              f"expr (rc={bproc.returncode}) — {btail}")
        if not bad_ok:
            print("the validate command let a crash-looping rules file through:\n"
                  + bproc.stdout + bproc.stderr)
        ok = ok and bad_ok

    return ok


def _fail(log, why: str) -> bool:
    print(f"FAIL: {why}")
    log.write(f"FAIL: {why}\n")
    return False


def test_shipped_validate_rejects_a_bad_rules_render() -> bool:
    """Step-7c acceptance 1/3/4: the render's own `validate:` gates a bad render."""
    LOGS.mkdir(exist_ok=True)
    print("\n=== plex-blip rules validate — good accepted, bad rejected ===")
    with (LOGS / "builder-7c-validate-gate.log").open("w") as log:
        return _run(log)


def main() -> int:
    results = [
        test_shipped_validate_rejects_a_bad_rules_render(),
    ]
    total, passed = len(results), sum(results)
    if passed == total:
        print(f"\nPASS: {passed}/{total}")
        return 0
    print(f"\nFAIL: {total - passed}/{total} checks failed")
    return 1


if __name__ == "__main__":
    sys.exit(main())
