"""Shape tests for tofu/modules/dev_vm/.

Per design §7.2 — verifies tofu validate succeeds, the os variable's
validation block accepts the three known values and rejects others,
and main.tf contains the module-internal initialization {} block
and (since gitlab-runner Step 1b) the optional consumer variables, which default
to empty/DHCP so existing behaviour is unchanged.
"""

import pathlib
import re
import subprocess
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
MODULE = REPO_ROOT / "tofu" / "modules" / "dev_vm"


def test_module_directory_exists() -> bool:
    ok = MODULE.is_dir()
    print(f"{'OK' if ok else 'FAIL'}: module dir exists at {MODULE}")
    return ok


def test_required_files_exist() -> bool:
    required = ["versions.tf", "variables.tf", "main.tf", "outputs.tf", "README.md"]
    missing = [f for f in required if not (MODULE / f).is_file()]
    ok = not missing
    print(f"{'OK' if ok else 'FAIL'}: required files present (missing={missing})")
    return ok


def test_tofu_validate() -> bool:
    if not MODULE.is_dir():
        print(f"FAIL: tofu validate (module dir missing at {MODULE})")
        return False
    result = subprocess.run(
        ["tofu", "init", "-backend=false"],
        cwd=MODULE,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(f"FAIL: tofu init in module: {result.stderr.strip()}")
        return False
    result = subprocess.run(
        ["tofu", "validate"],
        cwd=MODULE,
        capture_output=True,
        text=True,
    )
    ok = result.returncode == 0
    print(f"{'OK' if ok else 'FAIL'}: tofu validate ({result.stdout.strip() or result.stderr.strip()})")
    return ok


def test_os_variable_validation() -> bool:
    vars_file = MODULE / "variables.tf"
    if not vars_file.is_file():
        print(f"FAIL: variable os has validation accepting the three short-names (variables.tf missing)")
        return False
    body = vars_file.read_text()
    has_validation = re.search(
        r'variable\s+"os"\s*\{[^}]*?validation\s*\{[^}]*?contains\s*\(\s*\[\s*"ubuntu26"\s*,\s*"fedora"\s*,\s*"win11"\s*\]',
        body,
        re.DOTALL,
    )
    ok = has_validation is not None
    print(f"{'OK' if ok else 'FAIL'}: variable os has validation accepting the three short-names")
    return ok


def test_main_has_initialization_block() -> bool:
    main_file = MODULE / "main.tf"
    if not main_file.is_file():
        print(f"FAIL: main.tf has initialization with ip_config/ipv4/address=dhcp (main.tf missing)")
        return False
    body = main_file.read_text()
    has_init = re.search(
        r'initialization\s*\{[^}]*?ip_config\s*\{[^}]*?ipv4\s*\{[^}]*?address\s*=[^\n]*"dhcp"',
        body,
        re.DOTALL,
    )
    ok = has_init is not None
    print(f"{'OK' if ok else 'FAIL'}: main.tf has initialization with ip_config/ipv4/address=dhcp")
    return ok


def _variable_block(body: str, name: str) -> str:
    m = re.search(rf'variable\s+"{name}"\s*\{{(.*?)\n\}}', body, re.DOTALL)
    return m.group(1) if m else ""


def test_consumer_cidata_variables_optional() -> bool:
    """Polarity flip of the old bare-template guard (gitlab-runner Step 1b).

    The consumer variables now exist, are optional, and default to empty/DHCP.
    Defaults asserted per variable; user_data_file_id/static_ip stay absent.
    """
    vars_file = MODULE / "variables.tf"
    if not vars_file.is_file():
        print("FAIL: consumer cidata variables optional (variables.tf missing)")
        return False
    body = vars_file.read_text()
    want = {
        "ssh_public_keys": ("list(string)", r"\[\s*\]"),
        "ssh_username": ("string", r'"user"'),
        "ipv4_cidr": ("string", r'""'),
        "ipv4_gateway": ("string", r'""'),
        "dns_servers": ("list(string)", r"\[\s*\]"),
        "dns_domain": ("string", r'""'),
        "vm_id": ("number", r"null"),
        "firewall": ("bool", r"false"),
        "cpu_type": ("string", r'"host"'),
    }
    bad = []
    for name, (typ, default) in want.items():
        blk = _variable_block(body, name)
        if not blk:
            bad.append(f"{name}:missing")
            continue
        if not re.search(rf"type\s*=\s*{re.escape(typ)}\s*\n", blk):
            bad.append(f"{name}:type")
        if not re.search(rf"default\s*=\s*{default}\s*\n", blk):
            bad.append(f"{name}:default")
    forbidden = [n for n in ("user_data_file_id", "static_ip") if re.search(rf'variable\s+"{n}"', body)]
    bad += [f"{n}:forbidden" for n in forbidden]
    ok = not bad
    print(f"{'OK' if ok else 'FAIL'}: consumer cidata variables optional with empty/DHCP defaults (bad={bad})")
    return ok


def test_gateway_validation() -> bool:
    """ipv4_gateway must be set whenever ipv4_cidr is."""
    body = (MODULE / "variables.tf").read_text()
    blk = _variable_block(body, "ipv4_gateway")
    ok = bool(re.search(r"validation\s*\{[^}]*var\.ipv4_cidr\s*==\s*\"\"[^}]*var\.ipv4_gateway\s*!=\s*\"\"", blk, re.DOTALL))
    print(f"{'OK' if ok else 'FAIL'}: ipv4_gateway validated against ipv4_cidr")
    return ok


def test_provider_pin_floor() -> bool:
    """versions.tf pins bpg/proxmox to a >= 0.108.0 floor (gitlab-runner Step 1a)."""
    body = (MODULE / "versions.tf").read_text() if (MODULE / "versions.tf").is_file() else ""
    m = re.search(r'version\s*=\s*"\s*>=\s*0\.108\.0\s*"', body)
    ok = m is not None and "~>" not in body
    print(f"{'OK' if ok else 'FAIL'}: provider pin is >= 0.108.0 (no ~> cap)")
    return ok


def _main() -> str:
    f = MODULE / "main.tf"
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


def test_main_renders_scalars() -> bool:
    """vmid, cpu type and NIC firewall flag come from the variables (Step 1c)."""
    body = _main()
    checks = {
        "vm_id": re.search(r"^\s*vm_id\s*=\s*var\.vm_id\s*$", body, re.M) is not None,
        "cpu.type": re.search(r"type\s*=\s*var\.cpu_type\b", _block(body, r"\bcpu")) is not None,
        "nic.firewall": re.search(r"firewall\s*=\s*var\.firewall\b", _block(body, r"\bnetwork_device")) is not None,
    }
    bad = [k for k, v in checks.items() if not v]
    print(f"{'OK' if not bad else 'FAIL'}: main.tf renders vm_id/cpu.type/network_device.firewall (bad={bad})")
    return not bad


def test_main_static_ip_config() -> bool:
    """address is dhcp unless ipv4_cidr set; gateway only with a static address."""
    ip = _block(_block(_main(), r"\bip_config"), r"\bipv4")
    addr = re.search(r'address\s*=\s*var\.ipv4_cidr\s*==\s*""\s*\?\s*"dhcp"\s*:\s*var\.ipv4_cidr\b', ip)
    gw = re.search(r'gateway\s*=\s*var\.ipv4_cidr\s*==\s*""\s*\?\s*null\s*:\s*var\.ipv4_gateway\b', ip)
    ok = bool(addr and gw)
    print(f"{'OK' if ok else 'FAIL'}: ip_config address=dhcp unless ipv4_cidr; gateway null unless static")
    return ok


def test_main_conditional_blocks() -> bool:
    """user_account and dns render only when their inputs are set."""
    init = _block(_main(), r"\binitialization")
    ua = _block(init, r'dynamic\s+"user_account"')
    dns = _block(init, r'dynamic\s+"dns"')
    bad = []
    if not re.search(r"for_each\s*=\s*length\(var\.ssh_public_keys\)\s*>\s*0\s*\?\s*\[1\]\s*:\s*\[\]", ua):
        bad.append("user_account:for_each")
    if not (re.search(r"keys\s*=\s*var\.ssh_public_keys\b", ua) and re.search(r"username\s*=\s*var\.ssh_username\b", ua)):
        bad.append("user_account:content")
    if not re.search(r'for_each\s*=[^\n]*var\.dns_servers[^\n]*var\.dns_domain[^\n]*\?\s*\[1\]\s*:\s*\[\]', dns):
        bad.append("dns:for_each")
    if not (re.search(r"servers\s*=\s*var\.dns_servers\b", dns) and re.search(r'domain\s*=\s*var\.dns_domain\s*==\s*""\s*\?\s*null\s*:\s*var\.dns_domain', dns)):
        bad.append("dns:content")
    print(f"{'OK' if not bad else 'FAIL'}: user_account and dns are conditional dynamic blocks (bad={bad})")
    return not bad


def test_ipv4_configured_output() -> bool:
    """ipv4_configured is the static address sans prefix, null when DHCP (Step 1d)."""
    f = MODULE / "outputs.tf"
    out = _block(f.read_text() if f.is_file() else "", r'output\s+"ipv4_configured"')
    m = re.search(
        r'value\s*=\s*var\.ipv4_cidr\s*==\s*""\s*\?\s*null\s*:\s*split\("/",\s*var\.ipv4_cidr\)\[0\]\s*$',
        out.strip(),
    )
    ok = m is not None
    print(f"{'OK' if ok else 'FAIL'}: ipv4_configured strips the prefix, null when ipv4_cidr empty")
    return ok


def main() -> int:
    results = [
        test_module_directory_exists(),
        test_required_files_exist(),
        test_tofu_validate(),
        test_os_variable_validation(),
        test_main_has_initialization_block(),
        test_consumer_cidata_variables_optional(),
        test_gateway_validation(),
        test_provider_pin_floor(),
        test_main_renders_scalars(),
        test_main_static_ip_config(),
        test_main_conditional_blocks(),
        test_ipv4_configured_output(),
    ]
    total, passed = len(results), sum(results)
    if passed == total:
        print(f"PASS: {passed}/{total}")
        return 0
    print(f"FAIL: {total - passed}/{total} checks failed")
    return 1


if __name__ == "__main__":
    sys.exit(main())
