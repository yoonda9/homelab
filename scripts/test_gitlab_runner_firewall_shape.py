"""Shape tests for the gitlab-runner Proxmox firewall stage gate (Step 10b; gate 2506).

Text-parsed (stdlib only). The root variable `gitlab_runner_firewall_stage`
defaults to 1 and is validated to exactly [0, 1]. Stage 0 = no firewall resources
(rollback); the census below requires every firewall resource to be gated on the
variable by count/for_each. Gate 2506 (2026-11-10) found pve's datacenter and node
firewalls already on, so the per-VM objects are live at stage 1 and the old
stage-2 singletons (datacenter input ACCEPT, node firewall off) are retired: no
resource anywhere under tofu/ may be a pve-wide firewall switch.
`dev_vm`'s `firewall` input still defaults to false.
"""

import pathlib
import re
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
TOFU = REPO_ROOT / "tofu"
STAGE = "gitlab_runner_firewall_stage"
# resource types that are the datacenter-wide switch (retired with stage 2)
SWITCH_TYPES = {
    "proxmox_virtual_environment_cluster_firewall",
    "proxmox_virtual_environment_firewall_options_cluster",
}
# resource types that are the node (pve host) firewall switch (retired with stage 2)
NODE_TYPES = {
    "proxmox_node_firewall",
    "proxmox_virtual_environment_node_firewall",
}
FIREWALL_TYPE = re.compile(r'resource\s+"(proxmox_(?:virtual_environment_)?[a-z_]*firewall[a-z_]*)"\s+"([^"]+)"\s*\{')


def _block_at(body: str, start: int) -> str:
    depth, i = 1, start
    while i < len(body) and depth:
        depth += {"{": 1, "}": -1}.get(body[i], 0)
        i += 1
    return body[start:i - 1]


def _block(body: str, header: str) -> str:
    m = re.search(header + r"\s*\{", body)
    return _block_at(body, m.end()) if m else ""


def _report(ok: bool, msg: str) -> bool:
    print(f"{'OK' if ok else 'FAIL'}: {msg}")
    return ok


def _tofu_text(root: pathlib.Path = TOFU) -> dict:
    return {f.name: f.read_text() for f in sorted(root.glob("*.tf"))}


def _variable(files: dict) -> str:
    return _block("\n".join(files.values()), r'variable\s+"' + STAGE + r'"')


def census(files: dict) -> list:
    """(file, type, name, body) for every firewall resource at the root."""
    out = []
    for fname, text in files.items():
        for m in FIREWALL_TYPE.finditer(text):
            out.append((fname, m.group(1), m.group(2), _block_at(text, m.end())))
    return out


def check_variable(files: dict) -> bool:
    v = _variable(files)
    ok = (
        re.search(r"^\s*type\s*=\s*number\s*$", v, re.M) is not None
        and re.search(r"^\s*default\s*=\s*1\s*$", v, re.M) is not None
        and re.search(r"condition\s*=[^\n]*contains\(\s*\[\s*0\s*,\s*1\s*\]\s*,\s*var\." + STAGE + r"\s*\)", v) is not None
    )
    return _report(ok, f"variable {STAGE} is a number, default 1, validated to exactly [0, 1] (stage 2 retired)")


def check_census(files: dict) -> bool:
    bad = []
    for fname, rtype, name, body in census(files):
        gated = re.search(r"^\s*(count|for_each)\s*=[^\n]*var\." + STAGE + r"\b", body, re.M)
        if not gated:
            bad.append(f"{fname}:{rtype}.{name} ungated")
        elif rtype in SWITCH_TYPES | NODE_TYPES:
            bad.append(f"{fname}:{rtype}.{name} pve-wide switch (retired with stage 2)")
    return _report(not bad, f"every firewall resource is stage-gated and per-VM (bad={bad})")


def check_stage0_empty(files: dict) -> bool:
    """Rollback: at stage 0 nothing may exist, so every resource gates on stage >= 1."""
    entries = census(files)
    bad = [f"{rtype}.{name}" for _f, rtype, name, body in entries
           if not re.search(r"var\." + STAGE + r"\s*>=\s*1\b", body)]
    return _report(bool(entries) and not bad and check_census(files),
                   f"stage 0 (rollback) instantiates no firewall resources (bad={bad})")


def check_dev_vm_default() -> bool:
    v = _block((TOFU / "modules/dev_vm/variables.tf").read_text(), r'variable\s+"firewall"')
    ok = re.search(r"^\s*default\s*=\s*false\s*$", v, re.M) is not None
    return _report(ok, "dev_vm firewall input still defaults to false")


def _res(files: dict, rtype: str, name: str) -> str:
    for _f, t, n, body in census(files):
        if t == rtype and n == name:
            return body
    return ""


def _assign(body: str, key: str):
    m = re.search(r"^\s*" + key + r'\s*=\s*("[^"\n]*"|true|false)\s*$', body, re.M)
    return m.group(1) if m else None


def _all_tf_resource_types(root: pathlib.Path = TOFU) -> list:
    """(relative path, type) for every resource in any .tf under tofu/, modules included."""
    out = []
    for f in sorted(root.rglob("*.tf")):
        if ".terraform" in f.parts:
            continue
        for m in re.finditer(r'^\s*resource\s+"([a-z0-9_]+)"', f.read_text(), re.M):
            out.append((str(f.relative_to(root)), m.group(1)))
    return out


def check_cluster_pins(files: dict) -> bool:
    """Gate 2506 polarity flip: the datacenter switch was pinned to ACCEPT; now it must not exist.

    pve's datacenter firewall is on (policy_in DROP) and is managed outside Tofu; a
    cluster-firewall resource here would overwrite it (input ACCEPT) or, on destroy, reset it.
    """
    found = [f"{p}:{t}" for p, t in _all_tf_resource_types() if t in SWITCH_TYPES]
    return _report(not found, f"no datacenter firewall resource anywhere under tofu/ (found={found})")


def check_node_firewall_off(files: dict) -> bool:
    """Gate 2506 polarity flip: the node firewall was turned off at stage 2; now no resource may touch it."""
    found = [f"{p}:{t}" for p, t in _all_tf_resource_types() if t in NODE_TYPES]
    return _report(not found, f"no node (pve host) firewall resource anywhere under tofu/ (found={found})")


def check_vm_options(files: dict) -> bool:
    b = _res(files, "proxmox_virtual_environment_firewall_options", "vm")
    want = {"enabled": "true", "input_policy": '"DROP"', "output_policy": '"ACCEPT"', "macfilter": "true",
            "ipfilter": "true", "radv": "false", "dhcp": "false", "ndp": "false"}
    bad = {k: _assign(b, k) for k, v in want.items() if _assign(b, k) != v}
    return _report(not bad, f"VM options pin enabled/DROP-in/ACCEPT-out/macfilter/ipfilter/radv/dhcp/ndp (bad={bad})")


def check_ipset(files: dict) -> bool:
    b = _res(files, "proxmox_virtual_environment_firewall_ipset", "ipfilter")
    cidr = _block(b, r"cidr")
    ok = (
        _assign(b, "name") == '"ipfilter-net0"'
        and re.search(r"^\s*name\s*=\s*split\(\"/\",\s*each\.value\.ip_cidr\)\[0\]\s*$", cidr, re.M) is not None
    )
    return _report(ok, "ipset ipfilter-net0 holds the runner's own IP")


def check_rules(files: dict) -> bool:
    b = _res(files, "proxmox_virtual_environment_firewall_rules", "vm")
    drops = set(re.findall(r'action\s*=\s*"DROP"\s*\n\s*dest\s*=\s*"([^"]+)"', b))
    need = {"10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16", "100.64.0.0/10", "224.0.0.0/4", "255.255.255.255", "::/0"}
    in_rules = "9100,9252" in b and '"22"' in b
    return _report(need <= drops and in_rules, f"drops cover RFC1918, tailnet, multicast, broadcast, IPv6 (missing={sorted(need - drops)}); ingress 22 and 9100,9252")


def check_stage_semantics(files: dict) -> bool:
    """Stage 0 none, 1 the per-VM objects: each one is a for_each over the runner map."""
    bad = []
    entries = census(files)
    for _f, rtype, name, body in entries:
        per_vm = re.search(
            r"^\s*for_each\s*=\s*var\." + STAGE + r"\s*>=\s*1\s*\?\s*local\.gitlab_runners\s*:\s*\{\}\s*$", body, re.M
        )
        if not per_vm:
            bad.append(f"{rtype}.{name}")
    return _report(bool(entries) and not bad,
                   f"every firewall resource is per-VM: for_each over local.gitlab_runners at stage >= 1 (bad={bad})")


def main() -> int:
    files = _tofu_text()
    results = [
        check_variable(files),
        check_census(files),
        check_stage0_empty(files),
        check_dev_vm_default(),
        check_cluster_pins(files),
        check_node_firewall_off(files),
        check_vm_options(files),
        check_ipset(files),
        check_rules(files),
        check_stage_semantics(files),
    ]
    total, passed = len(results), sum(results)
    if passed == total:
        print(f"PASS: {passed}/{total}")
        return 0
    print(f"FAIL: {total - passed}/{total} checks failed")
    return 1


if __name__ == "__main__":
    sys.exit(main())
