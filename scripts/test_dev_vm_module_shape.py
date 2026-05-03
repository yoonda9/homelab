"""Shape tests for tofu/modules/dev_vm/.

Per design §7.2 — verifies tofu validate succeeds, the os variable's
validation block accepts the three known values and rejects others,
and main.tf contains the module-internal initialization {} block
with NO user_account / user_data_file_id consumer-variable references
(per Q6/A6 bare-template framing).
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
        r'initialization\s*\{[^}]*?ip_config\s*\{[^}]*?ipv4\s*\{[^}]*?address\s*=\s*"dhcp"',
        body,
        re.DOTALL,
    )
    ok = has_init is not None
    print(f"{'OK' if ok else 'FAIL'}: main.tf has initialization with ip_config/ipv4/address=dhcp")
    return ok


def test_no_consumer_cidata_variables() -> bool:
    vars_file = MODULE / "variables.tf"
    if not vars_file.is_file():
        print(f"FAIL: no consumer cidata variables leaked (variables.tf missing)")
        return False
    vars_body = vars_file.read_text()
    forbidden = ["user_account", "user_data_file_id", "ssh_authorized_keys", "static_ip"]
    leaks = [name for name in forbidden if re.search(rf'variable\s+"{name}"', vars_body)]
    ok = not leaks
    print(f"{'OK' if ok else 'FAIL'}: no consumer cidata variables leaked (found={leaks})")
    return ok


def main() -> int:
    results = [
        test_module_directory_exists(),
        test_required_files_exist(),
        test_tofu_validate(),
        test_os_variable_validation(),
        test_main_has_initialization_block(),
        test_no_consumer_cidata_variables(),
    ]
    total, passed = len(results), sum(results)
    if passed == total:
        print(f"PASS: {passed}/{total}")
        return 0
    print(f"FAIL: {total - passed}/{total} checks failed")
    return 1


if __name__ == "__main__":
    sys.exit(main())
