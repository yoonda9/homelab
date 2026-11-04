"""Shape tests for the gitlab-runner Proxmox firewall stage gate (Step 10b).

Text-parsed (stdlib only). The root variable `gitlab_runner_firewall_stage`
defaults to 0 and is validated to 0..2, so firewall code can merge without an
ordinary `just apply` touching it. Stage 0 = no firewall resources; the census
below requires every firewall resource to be gated on the variable by
count/for_each, and any resource that is the datacenter switch to need stage 2.
`dev_vm`'s `firewall` input still defaults to false.
"""

import pathlib
import re
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
TOFU = REPO_ROOT / "tofu"
STAGE = "gitlab_runner_firewall_stage"
# resource types that are the datacenter-wide switch (stage 2 only)
SWITCH_TYPES = {
    "proxmox_virtual_environment_cluster_firewall",
    "proxmox_virtual_environment_firewall_options_cluster",
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
        and re.search(r"^\s*default\s*=\s*0\s*$", v, re.M) is not None
        and re.search(r"condition\s*=[^\n]*contains\(\s*\[\s*0\s*,\s*1\s*,\s*2\s*\]\s*,\s*var\." + STAGE + r"\s*\)", v) is not None
    )
    return _report(ok, f"variable {STAGE} is a number, default 0, validated to [0, 1, 2]")


def check_census(files: dict) -> bool:
    bad = []
    for fname, rtype, name, body in census(files):
        gated = re.search(r"^\s*(count|for_each)\s*=[^\n]*var\." + STAGE + r"\b", body, re.M)
        if not gated:
            bad.append(f"{fname}:{rtype}.{name} ungated")
        elif rtype in SWITCH_TYPES and not re.search(r"var\." + STAGE + r"\s*(>=\s*2|==\s*2)", body):
            bad.append(f"{fname}:{rtype}.{name} switch not stage-2 only")
    return _report(not bad, f"every firewall resource is stage-gated (bad={bad})")


def check_stage0_empty(files: dict) -> bool:
    """At the default of 0 nothing may exist: either no resource, or all gated (census)."""
    v = _variable(files)
    default0 = re.search(r"^\s*default\s*=\s*0\s*$", v, re.M) is not None
    return _report(default0 and check_census(files), "stage 0 (the default) instantiates no firewall resources")


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


def check_cluster_pins(files: dict) -> bool:
    b = _res(files, "proxmox_virtual_environment_cluster_firewall", "dc")
    ok = (
        _assign(b, "input_policy") == '"ACCEPT"'
        and _assign(b, "output_policy") == '"ACCEPT"'
        and _assign(b, "forward_policy") == '"ACCEPT"'
        and _assign(b, "enabled") == "true"
        and _assign(b, "ebtables") == "true"
        and re.search(r"var\." + STAGE + r"\s*>=\s*2", b) is not None
    )
    return _report(ok, "datacenter switch: enabled, input/output/forward ACCEPT pinned, ebtables, stage >= 2")


def check_node_firewall_off(files: dict) -> bool:
    b = _res(files, "proxmox_node_firewall", "pve")
    ok = _assign(b, "enabled") == "false" and re.search(r"var\." + STAGE + r"\s*>=\s*2", b) is not None
    dc = _res(files, "proxmox_virtual_environment_cluster_firewall", "dc")
    ordered = re.search(r"depends_on\s*=\s*\[[^\]]*proxmox_node_firewall\.pve", dc) is not None
    return _report(ok and ordered, "node firewall disabled at stage 2 and ordered before the datacenter switch")


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
    """Stage 0 none, 1 per-VM objects only, 2 everything."""
    bad = []
    for _f, rtype, name, body in census(files):
        switch = rtype in SWITCH_TYPES or rtype == "proxmox_node_firewall"
        thresh = "2" if switch else "1"
        if not re.search(r"var\." + STAGE + r"\s*>=\s*" + thresh + r"\b", body):
            bad.append(f"{rtype}.{name}")
    return _report(not bad, f"singletons gate on stage >= 2, per-VM objects on stage >= 1 (bad={bad})")


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
