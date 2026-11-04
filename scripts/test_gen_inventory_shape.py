"""Shape tests for scripts/gen_inventory.py (gitlab-runner Step 2c).

Imports render() and drives it with fixture `tofu output -json` maps:
  - the gitlab_runner group renders from a gitlab_runners output;
  - the static fallback (.120) works with no output at all;
  - the pre-existing docker_host and plex groups stay byte-identical.
Stdlib only; no tofu needed.
"""

import importlib.util
import pathlib
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
GEN = REPO_ROOT / "scripts" / "gen_inventory.py"

# The two groups that existed before the gitlab_runner group, verbatim.
LEGACY = (
    "    docker_host:\n"
    "      hosts:\n"
    "        docker-host:\n"
    "          ansible_host: 192.168.1.111  # tofu output had no live IP yet; static design fallback\n"
    "          ansible_user: root\n"
    "    plex:\n"
    "      hosts:\n"
    "        plex:\n"
    "          ansible_host: 192.168.1.110  # tofu output had no live IP yet; static design fallback\n"
    "          ansible_user: root\n"
)


def _render(outputs: dict) -> str:
    spec = importlib.util.spec_from_file_location("gen_inventory", GEN)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.render(outputs)


def _report(ok: bool, msg: str) -> bool:
    print(f"{'OK' if ok else 'FAIL'}: {msg}")
    return ok


def test_group_from_output() -> bool:
    out = _render({"gitlab_runners": {"value": {
        "gitlab-runner-pve": {"ipv4": "192.168.1.120", "vm_id": 120},
        "runner-b": {"ipv4": "192.168.1.121", "vm_id": 121},
    }}})
    want = (
        "    gitlab_runner:\n"
        "      hosts:\n"
        "        gitlab-runner-pve:\n"
        "          ansible_host: 192.168.1.120\n"
        "          ansible_user: user\n"
        "          ansible_become: true\n"
        "        runner-b:\n"
        "          ansible_host: 192.168.1.121\n"
        "          ansible_user: user\n"
        "          ansible_become: true\n"
    )
    return _report(want in out, "gitlab_runner group renders every host from the output")


def test_static_fallback() -> bool:
    out = _render({})
    want = (
        "    gitlab_runner:\n"
        "      hosts:\n"
        "        gitlab-runner-pve:\n"
        "          ansible_host: 192.168.1.120"
    )
    return _report(want in out and "ansible_user: user\n" in out,
                   "no output -> gitlab-runner-pve at static 192.168.1.120")


def test_null_ip_falls_back() -> bool:
    out = _render({"gitlab_runners": {"value": {"gitlab-runner-pve": {"ipv4": None, "vm_id": 120}}}})
    return _report("ansible_host: 192.168.1.120" in out, "null ipv4 in the output falls back to .120")


def test_legacy_groups_byte_identical() -> bool:
    out = _render({})
    return _report(LEGACY in out and out.index(LEGACY) < out.index("gitlab_runner:"),
                   "docker_host and plex groups unchanged and precede gitlab_runner")


def main() -> int:
    results = [test_group_from_output(), test_static_fallback(),
               test_null_ip_falls_back(), test_legacy_groups_byte_identical()]
    total, passed = len(results), sum(results)
    if passed == total:
        print(f"PASS: {passed}/{total}")
        return 0
    print(f"FAIL: {total - passed}/{total} checks failed")
    return 1


if __name__ == "__main__":
    sys.exit(main())
