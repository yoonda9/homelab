#!/usr/bin/env python3
"""Runtime gate for the host-disk alert rules (host-disk-rules.yml.j2).

`promtool check rules` proves the file loads; it says nothing about whether an
alert can FIRE, and a ratio rule over a mistyped mountpoint loads clean and fires
never. So this runs `promtool test rules` on a simulated clock as well, out of
the PINNED image, reusing the plex-blip rig (test_plex_blip_alert_rules_promtool)
for the image relation, the uid-65534-safe mount and the no-skip policy:

  1. 10% free on CT 111's `/` fires HostRootFilesystemLow and NOT the critical
     rule; 50% free fires neither (the healthy control).
  2. 3% free fires HostRootFilesystemCritical.
  3. Only plex-node-exporter reporting `/` opens the absence door for
     node-exporter; both reporting keeps it shut.

Expected labels/annotations and each eval time (the rule's own `for:`) are READ
from the render, so a reworded summary moves the oracle with it. The free-space
fractions are this test's own inputs. The generated suite is written to `logs/`.
"""

import pathlib
import sys
import tempfile

import yaml

import test_plex_blip_alert_rules_promtool as rig

RULES_TEMPLATE = rig.ROLE / "templates" / "host-disk-rules.yml.j2"
RENDERED_RULES_BASENAME = "host-disk-rules.yml"
UNIT_SUITE_BASENAME = "host-disk-rules.unit.yml"

LOW_ALERT = "HostRootFilesystemLow"
CRITICAL_ALERT = "HostRootFilesystemCritical"
ABSENT_ALERT = "HostRootFilesystemSeriesAbsent"

# --- THIS test's own inputs ---------------------------------------------------
SIZE_BYTES = 32 * 1024**3  # CT 111's rootfs since 2026-10-27
LOW_FREE = 0.10       # under the 15% warning, over the 5% critical
CRITICAL_FREE = 0.03  # under both
HEALTHY_FREE = 0.50   # CT 111 right after the resize was ~56%
UNIT_INTERVAL = "1m"
UNIT_SAMPLES = 30
# The label sets the live series carry (queried 2026-10-27), minus `instance`,
# which promtool does not need to be realistic.
DOCKER_HOST_FS = {
    "job": "node-exporter", "mountpoint": "/", "fstype": "ext4",
    "device": "/dev/mapper/pve-vm--111--disk--0",
}
PLEX_FS = {
    "job": "plex-node-exporter", "mountpoint": "/", "fstype": "ext4",
    "device": "/dev/mapper/pve-vm--110--disk--0",
}


def _render_rules():
    body = rig._read(RULES_TEMPLATE)
    if not body:
        return None, f"{RULES_TEMPLATE} is empty or absent"
    rendered = body.replace(
        "{{ ansible_managed }}", f"Ansible managed: {RENDERED_RULES_BASENAME}")
    leftover = rig.re.findall(r"\{\{.*?\}\}|\{%.*?%\}", rendered)
    if leftover:
        return None, f"unrendered Jinja survives: {leftover}"
    return rendered, None


def _rules(rendered):
    try:
        doc = yaml.safe_load(rendered)
    except yaml.YAMLError as exc:
        return None, f"render does not parse: {str(exc).splitlines()[0]}"
    groups = (doc or {}).get("groups") if isinstance(doc, dict) else None
    rules = groups[0].get("rules") if isinstance(groups, list) and groups else None
    if not isinstance(rules, list):
        return None, "rendered file carries no rules list"
    by_name = {r.get("alert"): r for r in rules if isinstance(r, dict)}
    missing = [a for a in (LOW_ALERT, CRITICAL_ALERT, ABSENT_ALERT)
               if a not in by_name]
    if missing:
        return None, f"absent from the render: {missing}"
    for name, r in by_name.items():
        if not isinstance(r.get("labels"), dict) or not isinstance(
                r.get("annotations"), dict) or not r.get("for"):
            return None, f"{name} lacks labels, annotations or for:"
    return by_name, None


def _series(metric, labels, value):
    sel = ",".join(f'{k}="{v}"' for k, v in sorted(labels.items()))
    return {"series": f"{metric}{{{sel}}}",
            "values": f"{int(value)}+0x{UNIT_SAMPLES}"}


def _fs(labels, free):
    return [_series("node_filesystem_size_bytes", labels, SIZE_BYTES),
            _series("node_filesystem_avail_bytes", labels, SIZE_BYTES * free)]


def _fired(rule, series_labels):
    return {"exp_labels": {**series_labels, **rule["labels"]},
            "exp_annotations": rule["annotations"]}


def _build_unit_suite(rules):
    low, crit, door = rules[LOW_ALERT], rules[CRITICAL_ALERT], rules[ABSENT_ALERT]
    absent_labels = {"job": DOCKER_HOST_FS["job"], "mountpoint": "/"}

    def case(name, series, checks):
        return {"name": name, "interval": UNIT_INTERVAL, "input_series": series,
                "alert_rule_test": [
                    {"eval_time": rule["for"], "alertname": rule["alert"],
                     "exp_alerts": exp} for rule, exp in checks]}

    suite = {
        "rule_files": [RENDERED_RULES_BASENAME],
        "evaluation_interval": UNIT_INTERVAL,
        "tests": [
            case(f"{LOW_FREE:.0%} free fires {LOW_ALERT}, not {CRITICAL_ALERT}",
                 _fs(DOCKER_HOST_FS, LOW_FREE) + _fs(PLEX_FS, HEALTHY_FREE),
                 [(low, [_fired(low, DOCKER_HOST_FS)]), (crit, [])]),
            case(f"{HEALTHY_FREE:.0%} free fires nothing",
                 _fs(DOCKER_HOST_FS, HEALTHY_FREE) + _fs(PLEX_FS, HEALTHY_FREE),
                 [(low, []), (crit, []), (door, [])]),
            case(f"{CRITICAL_FREE:.0%} free fires {CRITICAL_ALERT}",
                 _fs(DOCKER_HOST_FS, CRITICAL_FREE) + _fs(PLEX_FS, HEALTHY_FREE),
                 [(crit, [_fired(crit, DOCKER_HOST_FS)])]),
            case(f"node-exporter silent on / opens {ABSENT_ALERT}",
                 _fs(PLEX_FS, HEALTHY_FREE),
                 [(door, [_fired(door, absent_labels)])]),
        ],
    }
    return yaml.safe_dump(suite, sort_keys=False, allow_unicode=True)


def _run(log) -> bool:
    image = rig._prometheus_image()
    if not image:
        return rig._fail(log, f"cannot read {rig.PROM_IMAGE_VAR} from {rig.DEFAULTS}")
    if not rig._which("docker"):
        return rig._fail(log, (
            f"`docker` is not on PATH; this gate runs promtool out of {image} "
            "and does NOT skip when docker is absent"))
    rendered, why = _render_rules()
    if rendered is None:
        return rig._fail(log, why)
    rules, why = _rules(rendered)
    if rules is None:
        return rig._fail(log, why)
    suite = _build_unit_suite(rules)

    rig.LOGS.mkdir(exist_ok=True)
    (rig.LOGS / UNIT_SUITE_BASENAME).write_text(suite)  # human-inspectable copy

    with tempfile.TemporaryDirectory() as tmp:
        mount = pathlib.Path(tmp)
        (mount / RENDERED_RULES_BASENAME).write_text(rendered)
        (mount / UNIT_SUITE_BASENAME).write_text(suite)
        mount.chmod(0o755)  # uid 65534 trap, as in the rig
        for p in mount.iterdir():
            p.chmod(0o644)

        chk = rig._docker_promtool(
            image, mount, ["check", "rules", f"/work/{RENDERED_RULES_BASENAME}"])
        log.write(f"$ promtool check rules ({image})\nrc={chk.returncode}\n"
                  f"{chk.stdout}{chk.stderr}\n")
        check_ok = chk.returncode == 0 and "3 rules found" in chk.stdout
        tail = (chk.stdout.strip().splitlines() or [chk.stderr.strip()])[-1]
        print(f"{'OK' if check_ok else 'FAIL'}: promtool check rules "
              f"(rc={chk.returncode}) — {tail}")
        if not check_ok:
            print(chk.stdout + chk.stderr)
            return False

        tst = rig._docker_promtool(
            image, mount, ["test", "rules", f"/work/{UNIT_SUITE_BASENAME}"])
        log.write(f"$ promtool test rules ({image})\nrc={tst.returncode}\n"
                  f"{tst.stdout}{tst.stderr}\n")
        test_ok = tst.returncode == 0 and "SUCCESS" in tst.stdout
        out = tst.stdout.strip() or tst.stderr.strip()
        tail = out.splitlines()[-1] if out else "(no output)"
        print(f"{'OK' if test_ok else 'FAIL'}: promtool test rules "
              f"(rc={tst.returncode}) — low/critical/door fire, controls silent "
              f"— {tail}")
        if not test_ok:
            print(tst.stdout + tst.stderr)
        return check_ok and test_ok


def test_host_disk_rules_check_and_fire_on_the_render() -> bool:
    """promtool validates the render AND each rule fires, with a silent control."""
    rig.LOGS.mkdir(exist_ok=True)
    print("\n=== host-disk alert rules — promtool check + test ===")
    with (rig.LOGS / "host-disk-promtool.log").open("w") as log:
        return _run(log)


def main() -> int:
    results = [test_host_disk_rules_check_and_fire_on_the_render()]
    total, passed = len(results), sum(results)
    if passed == total:
        print(f"\nPASS: {passed}/{total}")
        return 0
    print(f"\nFAIL: {total - passed}/{total} checks failed")
    return 1


if __name__ == "__main__":
    sys.exit(main())
