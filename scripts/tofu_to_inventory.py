"""Translate `tofu output -json ansible_inventory` into a YAML Ansible inventory.

Usage:
    tofu output -json ansible_inventory | python3 scripts/tofu_to_inventory.py
    python3 scripts/tofu_to_inventory.py --input inv.json --output ansible/inventory/tofu_generated.yml

Reads the JSON value of the `ansible_inventory` output (a mapping of
group → {hosts, vars}). Writes a real Ansible YAML inventory:

    proxmox_vms:
      hosts:
        ubuntu26-dev:
          ansible_host: 192.168.50.10
          vmid: 310
          node_name: pve-01
        centos10-dev:
          ansible_host: 192.168.50.11
          vmid: 311
          node_name: pve-01
      vars:
        ansible_user: user

Hosts whose ansible_host is null (DHCP not yet leased) are skipped with a
stderr warning naming each one so pre-apply runs don't silently drop hosts.

There is NO per-host `ansible_user` override. Every guest is reachable as
the uniform `default_user` ('user') the linux_vm cloud-init drops in via
`initialization.user_account`. Group-level `proxmox_vms.vars.ansible_user`
(emitted by `tofu/outputs.tf` from `var.default_user`) is the single
source of truth.

Stdlib only (no PyYAML) to keep the runtime footprint minimal and dependency-free.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Any

DEFAULT_OUTPUT = os.path.join("ansible", "inventory", "tofu_generated.yml")


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
    result: dict[str, Any] = {}
    any_remaining = False
    for group_name, group in data.items():
        if not isinstance(group, dict):
            continue
        transformed = transform_group(group_name, group)
        result[group_name] = transformed
        if transformed["hosts"]:
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
