"""Adversarial smoke test for the Step 1b two-map for_each shape in
`tofu/main.tf`.

Asserts that root `main.tf` declares:
- `local.cloud_templates` mapping the canonical template names
  (`ubuntu-26-04`, `centos-stream-10`) to vmids.
- `local.linux_vms` mapping the dev hostnames (`ubuntu26-dev`,
  `centos10-dev`) to objects with the required keys (`vmid`, `template`,
  `memory`, `cores`, `disk_gb`).
- A single `module "linux_vm"` block driven by
  `for_each = local.linux_vms` and sourced from `./modules/linux_vm`,
  with `clone_from` indirected via `local.cloud_templates[...]`.
- The Step 1a placeholder labels `ubuntu26_test` and `centos10_test`
  are absent (replace, not coexist).

Text-based — no HCL parser dependency. Mirrors the convention in
`scripts/test_tofu_linux_vm_module.py` and
`scripts/test_tofu_inventory_output.py`.
"""

import os
import re
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOFU_DIR = os.environ.get("TOFU_DIR", os.path.join(REPO_ROOT, "tofu"))
ROOT_MAIN_PATH = os.environ.get(
    "ROOT_MAIN_PATH", os.path.join(TOFU_DIR, "main.tf")
)

EXPECTED_CLOUD_TEMPLATES = {
    "ubuntu-26-04": 9001,
    "centos-stream-10": 9002,
}
EXPECTED_LINUX_VMS = {
    "ubuntu26-dev": "ubuntu-26-04",
    "centos10-dev": "centos-stream-10",
}
REQUIRED_LINUX_VM_KEYS = ("vmid", "template", "memory", "cores", "disk_gb")
FORBIDDEN_LEGACY_LABELS = ("ubuntu26_test", "centos10_test")

# Step 2 — Windows half. Vmids 320 / 321 keep the dev fleet's number
# space tidy: 9000-series for cloud-init templates, 310-series for
# Linux dev VMs, 320-series for Windows dev VMs. ISO substrings (`Win10`
# / `Win11`) defend against an accidental swap of the iso filenames in
# `local.windows_vms`.
EXPECTED_WINDOWS_VMS = {
    "win10-dev": {"vmid": 320, "iso_substring": "Win10"},
    "win11-dev": {"vmid": 321, "iso_substring": "Win11"},
}
REQUIRED_WINDOWS_VM_KEYS = ("vmid", "iso", "memory", "cores", "disk_gb")


def read_text(path):
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def _extract_block(text, header_pattern):
    """Return the body of the first block matching `header_pattern { ... }`.

    Tolerates two levels of brace nesting inside the body so a `locals`
    block containing `cloud_templates = { ... }` and `linux_vms = { ... }`
    map sub-blocks is captured fully (each map is itself a brace-delimited
    block, and individual entries like `ubuntu26-dev = { ... }` add a
    second level of nesting).
    """
    pattern = (
        header_pattern
        + r"\s*\{"
        + r"(?P<body>(?:[^{}]|\{(?:[^{}]|\{[^{}]*\})*\})*)"
        + r"\}"
    )
    match = re.search(pattern, text)
    return match.group("body") if match else None


def _extract_named_map(body, map_name):
    """Return the body of `<map_name> = { ... }` from a containing block body."""
    pattern = (
        re.escape(map_name)
        + r"\s*=\s*\{"
        + r"(?P<body>(?:[^{}]|\{[^{}]*\})*)"
        + r"\}"
    )
    match = re.search(pattern, body)
    return match.group("body") if match else None


def test_main_tf_exists():
    if os.path.isfile(ROOT_MAIN_PATH):
        print(f"OK: root main.tf exists at '{ROOT_MAIN_PATH}'.")
        return True
    print(f"FAIL: root main.tf is missing at '{ROOT_MAIN_PATH}'.")
    return False


def test_locals_block_present():
    text = read_text(ROOT_MAIN_PATH)
    if text is None:
        print(f"FAIL: '{ROOT_MAIN_PATH}' is missing.")
        return False
    body = _extract_block(text, r"locals")
    if body is None:
        print(
            f"FAIL: '{ROOT_MAIN_PATH}' must declare a top-level "
            f"'locals {{ ... }}' block (Step 1b two-map for_each shape)."
        )
        return False
    print(f"OK: '{ROOT_MAIN_PATH}' declares a 'locals {{ ... }}' block.")
    return True


def test_cloud_templates_local_map():
    text = read_text(ROOT_MAIN_PATH)
    if text is None:
        print(f"FAIL: '{ROOT_MAIN_PATH}' is missing.")
        return False
    locals_body = _extract_block(text, r"locals")
    if locals_body is None:
        print(f"FAIL: '{ROOT_MAIN_PATH}' has no 'locals {{}}' block.")
        return False
    map_body = _extract_named_map(locals_body, "cloud_templates")
    if map_body is None:
        print(
            f"FAIL: '{ROOT_MAIN_PATH}' locals block must declare "
            f"'cloud_templates = {{ ... }}' map."
        )
        return False
    missing = []
    for template_name, vmid in EXPECTED_CLOUD_TEMPLATES.items():
        # Map keys with hyphens must match exactly; allow optional quoting.
        pattern = (
            r'"?'
            + re.escape(template_name)
            + r'"?\s*=\s*'
            + str(vmid)
            + r"\b"
        )
        if not re.search(pattern, map_body):
            missing.append(f"{template_name} = {vmid}")
    if missing:
        print(
            f"FAIL: '{ROOT_MAIN_PATH}' local.cloud_templates is missing: "
            f"{', '.join(missing)}."
        )
        return False
    print(
        f"OK: '{ROOT_MAIN_PATH}' local.cloud_templates pins "
        f"{', '.join(f'{n}={v}' for n, v in EXPECTED_CLOUD_TEMPLATES.items())}."
    )
    return True


def test_linux_vms_local_map_with_required_keys():
    text = read_text(ROOT_MAIN_PATH)
    if text is None:
        print(f"FAIL: '{ROOT_MAIN_PATH}' is missing.")
        return False
    locals_body = _extract_block(text, r"locals")
    if locals_body is None:
        print(f"FAIL: '{ROOT_MAIN_PATH}' has no 'locals {{}}' block.")
        return False
    map_body = _extract_named_map(locals_body, "linux_vms")
    if map_body is None:
        print(
            f"FAIL: '{ROOT_MAIN_PATH}' locals block must declare "
            f"'linux_vms = {{ ... }}' map "
            f"(named exactly 'linux_vms'; do not rename it — the "
            f"module \"linux_vm\" for_each must reference local.linux_vms)."
        )
        return False
    for host, template in EXPECTED_LINUX_VMS.items():
        # Each entry: <hostname> = { ... }. Hostname has a hyphen so allow
        # optional quoting; capture the brace-delimited entry body.
        entry_pattern = (
            r'"?'
            + re.escape(host)
            + r'"?\s*=\s*\{'
            + r"(?P<body>[^{}]*)"
            + r"\}"
        )
        match = re.search(entry_pattern, map_body)
        if match is None:
            print(
                f"FAIL: '{ROOT_MAIN_PATH}' local.linux_vms missing entry "
                f"for '{host}' (Step 1b dev fleet uses ubuntu26-dev / "
                f"centos10-dev exclusively)."
            )
            return False
        entry_body = match.group("body")
        for key in REQUIRED_LINUX_VM_KEYS:
            if not re.search(re.escape(key) + r"\s*=\s*", entry_body):
                print(
                    f"FAIL: '{ROOT_MAIN_PATH}' local.linux_vms[{host!r}] "
                    f"missing required key '{key}' "
                    f"(every dev VM must declare {REQUIRED_LINUX_VM_KEYS})."
                )
                return False
        # Template attribute must reference the canonical key name in
        # cloud_templates so the indirection works at apply time.
        tpl_pattern = (
            r'template\s*=\s*"?'
            + re.escape(template)
            + r'"?'
        )
        if not re.search(tpl_pattern, entry_body):
            print(
                f"FAIL: '{ROOT_MAIN_PATH}' local.linux_vms[{host!r}] must "
                f"set template = \"{template}\" "
                f"(matches a key in local.cloud_templates)."
            )
            return False
    print(
        f"OK: '{ROOT_MAIN_PATH}' local.linux_vms declares "
        f"{', '.join(EXPECTED_LINUX_VMS)} with required keys "
        f"{REQUIRED_LINUX_VM_KEYS}."
    )
    return True


def test_module_linux_vm_uses_for_each_local_linux_vms():
    text = read_text(ROOT_MAIN_PATH)
    if text is None:
        print(f"FAIL: '{ROOT_MAIN_PATH}' is missing.")
        return False
    body = _extract_block(text, r'module\s+"linux_vm"')
    if body is None:
        print(
            f"FAIL: '{ROOT_MAIN_PATH}' must declare a single "
            f"'module \"linux_vm\" {{ ... }}' block "
            f"(replaces the per-host ubuntu26_test/centos10_test blocks)."
        )
        return False
    if not re.search(r"for_each\s*=\s*local\.linux_vms\b", body):
        print(
            f"FAIL: 'module \"linux_vm\"' in '{ROOT_MAIN_PATH}' must use "
            f"for_each = local.linux_vms (renaming the local map breaks "
            f"the wiring; this assertion catches that)."
        )
        return False
    if not re.search(
        r'source\s*=\s*"\./modules/linux_vm"', body
    ):
        print(
            f"FAIL: 'module \"linux_vm\"' in '{ROOT_MAIN_PATH}' must set "
            f"source = \"./modules/linux_vm\" (Step 1a renamed module path)."
        )
        return False
    if not re.search(
        r"clone_from\s*=\s*local\.cloud_templates\[each\.value\.template\]",
        body,
    ):
        print(
            f"FAIL: 'module \"linux_vm\"' in '{ROOT_MAIN_PATH}' must set "
            f"clone_from = local.cloud_templates[each.value.template] "
            f"(template key indirection — required so adding a new "
            f"distro is one map entry)."
        )
        return False
    print(
        f"OK: '{ROOT_MAIN_PATH}' declares "
        f"'module \"linux_vm\" {{ for_each = local.linux_vms ... }}' "
        f"with clone_from indirected via local.cloud_templates."
    )
    return True


def test_windows_vms_local_map_with_required_keys():
    text = read_text(ROOT_MAIN_PATH)
    if text is None:
        print(f"FAIL: '{ROOT_MAIN_PATH}' is missing.")
        return False
    locals_body = _extract_block(text, r"locals")
    if locals_body is None:
        print(f"FAIL: '{ROOT_MAIN_PATH}' has no 'locals {{}}' block.")
        return False
    map_body = _extract_named_map(locals_body, "windows_vms")
    if map_body is None:
        print(
            f"FAIL: '{ROOT_MAIN_PATH}' locals block must declare "
            f"'windows_vms = {{ ... }}' map "
            f"(named exactly 'windows_vms'; the module \"windows_vm\" "
            f"for_each must reference local.windows_vms)."
        )
        return False
    for host, expected in EXPECTED_WINDOWS_VMS.items():
        entry_pattern = (
            r'"?'
            + re.escape(host)
            + r'"?\s*=\s*\{'
            + r"(?P<body>[^{}]*)"
            + r"\}"
        )
        match = re.search(entry_pattern, map_body)
        if match is None:
            print(
                f"FAIL: '{ROOT_MAIN_PATH}' local.windows_vms missing "
                f"entry for '{host}' (Step 2 dev fleet uses "
                f"win10-dev / win11-dev exclusively)."
            )
            return False
        entry_body = match.group("body")
        for key in REQUIRED_WINDOWS_VM_KEYS:
            if not re.search(re.escape(key) + r"\s*=\s*", entry_body):
                print(
                    f"FAIL: '{ROOT_MAIN_PATH}' "
                    f"local.windows_vms[{host!r}] missing required key "
                    f"'{key}' (every Windows dev VM must declare "
                    f"{REQUIRED_WINDOWS_VM_KEYS})."
                )
                return False
        # vmid pin: defends against accidental collision with the
        # 310-series Linux vmids or the 9000-series template vmids.
        vmid_pattern = (
            r"vmid\s*=\s*" + str(expected["vmid"]) + r"\b"
        )
        if not re.search(vmid_pattern, entry_body):
            print(
                f"FAIL: '{ROOT_MAIN_PATH}' "
                f"local.windows_vms[{host!r}] must set "
                f"vmid = {expected['vmid']} "
                f"(reserved Windows dev-VM vmid range)."
            )
            return False
        # iso substring: defends against an accidental swap of the
        # Win10 / Win11 install ISO filenames between map entries.
        iso_block = re.search(r'iso\s*=\s*"([^"]*)"', entry_body)
        if iso_block is None:
            print(
                f"FAIL: '{ROOT_MAIN_PATH}' "
                f"local.windows_vms[{host!r}].iso must be a "
                f"quoted string referencing the install ISO filename."
            )
            return False
        if expected["iso_substring"] not in iso_block.group(1):
            print(
                f"FAIL: '{ROOT_MAIN_PATH}' "
                f"local.windows_vms[{host!r}].iso "
                f"= \"{iso_block.group(1)}\" does not contain expected "
                f"substring '{expected['iso_substring']}' "
                f"(suggests an accidental Win10/Win11 swap)."
            )
            return False
    print(
        f"OK: '{ROOT_MAIN_PATH}' local.windows_vms declares "
        f"{', '.join(EXPECTED_WINDOWS_VMS)} with required keys "
        f"{REQUIRED_WINDOWS_VM_KEYS} and Win10/Win11 iso pins."
    )
    return True


def test_module_windows_vm_uses_for_each_local_windows_vms():
    text = read_text(ROOT_MAIN_PATH)
    if text is None:
        print(f"FAIL: '{ROOT_MAIN_PATH}' is missing.")
        return False
    body = _extract_block(text, r'module\s+"windows_vm"')
    if body is None:
        print(
            f"FAIL: '{ROOT_MAIN_PATH}' must declare a "
            f"'module \"windows_vm\" {{ ... }}' block "
            f"(parallel to module \"linux_vm\")."
        )
        return False
    if not re.search(r"for_each\s*=\s*local\.windows_vms\b", body):
        print(
            f"FAIL: 'module \"windows_vm\"' in '{ROOT_MAIN_PATH}' must "
            f"use for_each = local.windows_vms (renaming the local map "
            f"breaks the wiring; this assertion catches that)."
        )
        return False
    if not re.search(r'source\s*=\s*"\./modules/windows_vm"', body):
        print(
            f"FAIL: 'module \"windows_vm\"' in '{ROOT_MAIN_PATH}' must "
            f"set source = \"./modules/windows_vm\" "
            f"(matches the new module's path)."
        )
        return False
    print(
        f"OK: '{ROOT_MAIN_PATH}' declares "
        f"'module \"windows_vm\" {{ for_each = local.windows_vms ... }}' "
        f"sourced from ./modules/windows_vm."
    )
    return True


def test_legacy_labels_absent():
    text = read_text(ROOT_MAIN_PATH)
    if text is None:
        print(f"FAIL: '{ROOT_MAIN_PATH}' is missing.")
        return False
    # Scan code lines (skip comment-prefixed lines) so an explanatory
    # historical comment in main.tf doesn't trip the assertion.
    # Pattern from mem-1777478162-68e8.
    code = "\n".join(
        line
        for line in text.splitlines()
        if not line.lstrip().startswith("#")
    )
    leaked = []
    for label in FORBIDDEN_LEGACY_LABELS:
        if re.search(r"\b" + re.escape(label) + r"\b", code):
            leaked.append(label)
    if leaked:
        print(
            f"FAIL: '{ROOT_MAIN_PATH}' must not contain Step 1a "
            f"placeholder labels {FORBIDDEN_LEGACY_LABELS} (replace, not "
            f"coexist); found: {leaked}."
        )
        return False
    print(
        f"OK: '{ROOT_MAIN_PATH}' has no legacy "
        f"{FORBIDDEN_LEGACY_LABELS} labels in code (comments are ignored)."
    )
    return True


def main():
    checks = [
        ("root main.tf exists", test_main_tf_exists),
        ("locals block present", test_locals_block_present),
        (
            "local.cloud_templates pins ubuntu-26-04 / centos-stream-10",
            test_cloud_templates_local_map,
        ),
        (
            "local.linux_vms declares dev hosts with required keys",
            test_linux_vms_local_map_with_required_keys,
        ),
        (
            "module \"linux_vm\" uses for_each = local.linux_vms",
            test_module_linux_vm_uses_for_each_local_linux_vms,
        ),
        (
            "local.windows_vms declares win10-dev/win11-dev with required keys",
            test_windows_vms_local_map_with_required_keys,
        ),
        (
            "module \"windows_vm\" uses for_each = local.windows_vms",
            test_module_windows_vm_uses_for_each_local_windows_vms,
        ),
        (
            "legacy ubuntu26_test/centos10_test labels absent",
            test_legacy_labels_absent,
        ),
    ]
    results = [(label, fn()) for label, fn in checks]
    print()
    failed = [label for label, passed in results if not passed]
    if failed:
        print(f"FAILED {len(failed)}/{len(results)} checks:")
        for label in failed:
            print(f"  - {label}")
        sys.exit(1)
    print(
        f"SUCCESS: All {len(results)} dev-vms main.tf two-map "
        f"for_each checks passed."
    )
    sys.exit(0)


if __name__ == "__main__":
    main()
