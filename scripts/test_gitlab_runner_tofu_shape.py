"""Shape tests for the gitlab-runner root tofu wiring (gitlab-runner Step 2).

Text-parsed (stdlib only): the `gitlab_runners` map in tofu/locals.tf drives a
`for_each` call of modules/dev_vm in tofu/main.tf, with `node` a per-entry
field, vmid 120 and 192.168.1.120/24, the operator-keys precondition present,
and every Proxmox firewall resource confined to gitlab_runner_firewall.tf (stage-gated). The root
`gitlab_runners` output (ipv4 + vm_id per VM) feeds inventory generation.
"""

import pathlib
import re
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
TOFU = REPO_ROOT / "tofu"


def _read(name: str) -> str:
    f = TOFU / name
    return f.read_text() if f.is_file() else ""


def _block(body: str, header: str) -> str:
    """Brace-balanced body of the first block whose header matches the regex."""
    m = re.search(header + r"\s*\{", body)
    if not m:
        return ""
    depth, i = 1, m.end()
    while i < len(body) and depth:
        depth += {"{": 1, "}": -1}.get(body[i], 0)
        i += 1
    return body[m.end():i - 1]


def _report(ok: bool, msg: str) -> bool:
    print(f"{'OK' if ok else 'FAIL'}: {msg}")
    return ok


def test_map_entry_fields() -> bool:
    """The map has the vm, with node a per-entry field, vmid 120 and .120."""
    m = _block(_read("locals.tf"), r"\bgitlab_runners\s*=")
    entry = _block(m, r'"gitlab-runner-pve"\s*=')
    want = {
        "node": r'^\s*node\s*=\s*"pve"\s*$',
        "vm_id": r"^\s*vm_id\s*=\s*120\s*$",
        "ip_cidr": r'^\s*ip_cidr\s*=\s*"192\.168\.1\.120/24"\s*$',
        "cores": r"^\s*cores\s*=\s*8\s*$",
        "memory_mb": r"^\s*memory_mb\s*=\s*16384\s*$",
        "disk_gb": r"^\s*disk_gb\s*=\s*150\s*$",
    }
    bad = [k for k, rx in want.items() if not re.search(rx, entry, re.M)]
    return _report(not bad, f"gitlab_runners entry carries node/vm_id/ip_cidr/size (bad={bad})")


def _call() -> str:
    return _block(_read("main.tf"), r'module\s+"gitlab_runner"')


def test_for_each_over_map() -> bool:
    call = _call()
    ok = re.search(r"^\s*for_each\s*=\s*local\.gitlab_runners\s*$", call, re.M) is not None
    return _report(ok, "module gitlab_runner is for_each over local.gitlab_runners")


def test_call_inputs_from_entry() -> bool:
    call = _call()
    want = {
        "source": r'^\s*source\s*=\s*"\./modules/dev_vm"\s*$',
        "name": r"^\s*name\s*=\s*each\.key\s*$",
        "os": r'^\s*os\s*=\s*"ubuntu26"\s*$',
        "template_id": r"^\s*template_id\s*=\s*local\.template_ids\.ubuntu26\s*$",
        "node": r"^\s*node\s*=\s*each\.value\.node\s*$",
        "vm_id": r"^\s*vm_id\s*=\s*each\.value\.vm_id\s*$",
        "cores": r"^\s*cores\s*=\s*each\.value\.cores\s*$",
        "memory_mb": r"^\s*memory_mb\s*=\s*each\.value\.memory_mb\s*$",
        "disk_gb": r"^\s*disk_gb\s*=\s*each\.value\.disk_gb\s*$",
        "ipv4_cidr": r"^\s*ipv4_cidr\s*=\s*each\.value\.ip_cidr\s*$",
        "ipv4_gateway": r"^\s*ipv4_gateway\s*=\s*local\.net\.gateway\s*$",
        "dns_servers": r"^\s*dns_servers\s*=\s*local\.net\.dns_servers\s*$",
        "dns_domain": r"^\s*dns_domain\s*=\s*local\.net\.dns_domain\s*$",
        "ssh_public_keys": r"^\s*ssh_public_keys\s*=\s*local\.operator_ssh_keys\s*$",
        "firewall": r"^\s*firewall\s*=\s*true\b",
    }
    bad = [k for k, rx in want.items() if not re.search(rx, call, re.M)]
    return _report(not bad, f"module gitlab_runner inputs come from the entry / shared locals (bad={bad})")


def test_keys_precondition() -> bool:
    """An empty operator key list must fail the plan, and gate the VM."""
    body = _read("main.tf")
    guard = _block(body, r'resource\s+"terraform_data"\s+"gitlab_runner_operator_keys"')
    pre = _block(guard, r"\bprecondition")
    ok = (
        re.search(r"length\(local\.operator_ssh_keys\)\s*>\s*0", pre) is not None
        and re.search(r"error_message\s*=", pre) is not None
        and re.search(r"depends_on\s*=\s*\[\s*terraform_data\.gitlab_runner_operator_keys\s*\]", _call())
        is not None
    )
    return _report(ok, "non-empty operator keys precondition exists and the module depends on it")


def test_no_firewall_resource_before_stage_gate() -> bool:
    bad = []
    for f in sorted(TOFU.glob("*.tf")):
        for m in re.finditer(r'resource\s+"(proxmox_(?:virtual_environment_)?[a-z_]*firewall[a-z_]*)"', f.read_text()):
            if f.name != "gitlab_runner_firewall.tf":
                bad.append(f"{f.name}:{m.group(1)}")
    present = "proxmox_virtual_environment_cluster_firewall" in (TOFU / "gitlab_runner_firewall.tf").read_text()
    return _report(not bad and present, f"Proxmox firewall resources live only in gitlab_runner_firewall.tf, which holds them (stray={bad}); gating is test_gitlab_runner_firewall_shape")


def test_root_output() -> bool:
    """outputs.tf exposes gitlab_runners as {name: {ipv4, vm_id}} from the module."""
    out = _block(_read("outputs.tf"), r'output\s+"gitlab_runners"')
    ok = (
        re.search(r"for\s+k\s*,\s*m\s+in\s+module\.gitlab_runner\s*:", out) is not None
        and re.search(r"\bipv4\s*=\s*m\.ipv4_configured\b", out) is not None
        and re.search(r"\bvm_id\s*=\s*m\.vm_id\b", out) is not None
    )
    return _report(ok, "root output gitlab_runners maps each module instance to {ipv4, vm_id}")


def main() -> int:
    results = [
        test_map_entry_fields(),
        test_for_each_over_map(),
        test_call_inputs_from_entry(),
        test_keys_precondition(),
        test_no_firewall_resource_before_stage_gate(),
        test_root_output(),
    ]
    total, passed = len(results), sum(results)
    if passed == total:
        print(f"PASS: {passed}/{total}")
        return 0
    print(f"FAIL: {total - passed}/{total} checks failed")
    return 1


if __name__ == "__main__":
    sys.exit(main())
