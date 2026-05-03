"""Translate `tofu output -json ansible_inventory` into a YAML Ansible inventory.

Usage:
    tofu output -json ansible_inventory | python3 scripts/tofu_to_inventory.py
    python3 scripts/tofu_to_inventory.py --input inv.json --output ansible/inventory/tofu_generated.yml

Reads the JSON value of the `ansible_inventory` output (a mapping of
group → {hosts, vars}) and writes a real Ansible YAML inventory:

    proxmox_vms:
      hosts:
        ubuntu26-dev:
          ansible_host: 192.168.50.10
          vmid: 310
          node_name: pve-01
        fedora-workstation-dev: { ... }
      children:
        windows:
          hosts:
            win10-dev: { ansible_host: ..., vmid: 320, node_name: pve-01 }
            win11-dev: { ... }
          vars:
            ansible_shell_type: powershell
      vars:
        ansible_user: user

The Tofu-side output emits `windows_dev_vms` as a sibling top-level
group; this generator reshapes it into `proxmox_vms.children.windows`
so the group-level `ansible_user: user` flows through Ansible's group
inheritance to both Linux hosts and the Windows child. The Windows
child carries `ansible_shell_type: powershell` so Ansible drives the
ansible.windows.* modules over WinRM/PowerShell.

Hosts whose ansible_host is null (DHCP not yet leased, or Windows
install still running) are skipped with a stderr warning naming each.

There is NO per-host `ansible_user` override on either Linux or
Windows hosts. Group-level `proxmox_vms.vars.ansible_user` (emitted
from `var.default_user`) is the single source of truth.

Stdlib only (no PyYAML) to keep the runtime footprint minimal.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Any

DEFAULT_OUTPUT = os.path.join("ansible", "inventory", "tofu_generated.yml")

# The Tofu-side `ansible_inventory` output emits Windows hosts as a
# sibling top-level `windows_dev_vms` group. The generator reshapes
# that into `proxmox_vms.children.windows` so Linux + Windows guests
# share the inherited `ansible_user: user`.
WINDOWS_GROUP_KEY = "windows_dev_vms"
PARENT_GROUP_KEY = "proxmox_vms"
WINDOWS_CHILD_KEY = "windows"


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Translate tofu ansible_inventory JSON to YAML inventory.",
    )
    parser.add_argument(
        "--input",
        "-i",
        default=None,
        help="Path to JSON file (default: read stdin).",
    )
    parser.add_argument(
        "--output",
        "-o",
        default=DEFAULT_OUTPUT,
        help=f"Path to YAML output file (default: {DEFAULT_OUTPUT}).",
    )
    return parser.parse_args(argv)


def load_input(path: str | None) -> dict[str, Any]:
    if path is None:
        raw = sys.stdin.read()
        source = "<stdin>"
    else:
        if not os.path.exists(path):
            sys.stderr.write(f"ERROR: input path does not exist: {path}\n")
            sys.exit(2)
        with open(path, "r", encoding="utf-8") as f:
            raw = f.read()
        source = path
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        sys.stderr.write(
            f"ERROR: failed to parse JSON from {source}: {exc.msg} "
            f"(line {exc.lineno}, column {exc.colno})\n"
        )
        sys.exit(3)
    if not isinstance(data, dict):
        sys.stderr.write(
            f"ERROR: top-level JSON in {source} must be an object "
            f"(got {type(data).__name__})\n"
        )
        sys.exit(4)
    return data


def validate_inventory_shape(data: dict[str, Any]) -> None:
    """Require at least one group with a `hosts` mapping. Fails loudly otherwise."""
    for _group_name, group in data.items():
        if isinstance(group, dict) and isinstance(group.get("hosts"), dict):
            return
    sys.stderr.write(
        "ERROR: ansible_inventory shape invalid: no top-level group has a "
        "'hosts' mapping (expected e.g. {\"proxmox_vms\": {\"hosts\": {...}}})\n"
    )
    sys.exit(5)


def transform_group(group_name: str, group: dict[str, Any]) -> dict[str, Any]:
    """Filter out null-ansible_host hosts; preserve group-level vars verbatim.

    No per-host `ansible_user` override is applied — the legacy
    hostname-prefix dispatch (`ubuntu*`/`centos*`) is gone in Step 1b.
    The single uniform `ansible_user: user` lives on the group's
    `vars` and is emitted from `var.default_user` by `tofu/outputs.tf`.
    """
    src_hosts = group.get("hosts", {}) or {}
    out_hosts: dict[str, Any] = {}
    for host, attrs in src_hosts.items():
        if not isinstance(attrs, dict):
            sys.stderr.write(
                f"WARNING: host '{host}' in group '{group_name}' is not a "
                f"mapping (got {type(attrs).__name__}); skipping.\n"
            )
            continue
        if attrs.get("ansible_host") is None:
            sys.stderr.write(
                f"WARNING: skipping host '{host}' in group '{group_name}': "
                f"ansible_host is null (DHCP lease not yet observed).\n"
            )
            continue
        out_hosts[host] = dict(attrs)
    out: dict[str, Any] = {"hosts": out_hosts}
    if isinstance(group.get("vars"), dict):
        out["vars"] = dict(group["vars"])
    return out


def transform(data: dict[str, Any]) -> dict[str, Any]:
    """Build the YAML-shaped inventory.

    Special handling for the Windows sibling group: rather than emit
    `windows_dev_vms` as a peer of `proxmox_vms` (which would lose the
    inherited `ansible_user`), reshape it into
    `proxmox_vms.children.windows` and stamp
    `ansible_shell_type: powershell` on the child group's vars. The
    parent `ansible_user` then flows through to Windows hosts via
    Ansible group inheritance, matching the spec's "single uniform
    `user`" intent.
    """
    result: dict[str, Any] = {}
    any_remaining = False
    for group_name, group in data.items():
        if not isinstance(group, dict):
            continue
        if group_name == WINDOWS_GROUP_KEY:
            continue  # handled separately below
        transformed = transform_group(group_name, group)
        result[group_name] = transformed
        if transformed["hosts"]:
            any_remaining = True

    win_group = data.get(WINDOWS_GROUP_KEY)
    if isinstance(win_group, dict):
        win_transformed = transform_group(WINDOWS_GROUP_KEY, win_group)
        # Drop ansible_user from the Windows child's vars — it lives
        # on the parent proxmox_vms.vars and is inherited. Stamp
        # ansible_shell_type=powershell so Ansible drives win_*
        # modules over PowerShell.
        win_vars = win_transformed.get("vars", {}) or {}
        win_vars.pop("ansible_user", None)
        win_vars["ansible_shell_type"] = "powershell"
        win_child = {"hosts": win_transformed["hosts"], "vars": win_vars}
        parent = result.setdefault(PARENT_GROUP_KEY, {"hosts": {}})
        children = parent.setdefault("children", {})
        children[WINDOWS_CHILD_KEY] = win_child
        if win_transformed["hosts"]:
            any_remaining = True

    if not any_remaining:
        sys.stderr.write(
            "ERROR: every host was skipped (all ansible_host values were "
            "null); nothing to write to inventory.\n"
        )
        sys.exit(6)
    return result


def _format_scalar(value: Any) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    text = str(value).replace('"', '\\"')
    return f'"{text}"'


def _emit_mapping(data: dict[str, Any], indent: int) -> list[str]:
    pad = "  " * indent
    lines: list[str] = []
    for key, value in data.items():
        if isinstance(value, dict):
            if not value:
                lines.append(f"{pad}{key}: {{}}")
                continue
            lines.append(f"{pad}{key}:")
            lines.extend(_emit_mapping(value, indent + 1))
        else:
            lines.append(f"{pad}{key}: {_format_scalar(value)}")
    return lines


def emit_yaml(data: dict[str, Any]) -> str:
    body = "\n".join(_emit_mapping(data, 0))
    return "---\n# Generated by scripts/tofu_to_inventory.py — DO NOT EDIT.\n" + body + "\n"


def write_output(text: str, path: str) -> None:
    parent = os.path.dirname(path)
    if parent and not os.path.isdir(parent):
        os.makedirs(parent, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv if argv is not None else sys.argv[1:])
    data = load_input(args.input)
    validate_inventory_shape(data)
    inventory = transform(data)
    write_output(emit_yaml(inventory), args.output)
    sys.stderr.write(f"wrote {args.output}\n")


if __name__ == "__main__":
    main()
