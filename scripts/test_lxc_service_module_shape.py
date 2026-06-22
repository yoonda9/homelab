"""Shape tests for tofu/modules/lxc_service/.

Per design §4.1/§5 and task-03 — verifies the generic lxc_service module
exists with the 5-file set, wraps proxmox_virtual_environment_container,
defaults unprivileged to true, pins bpg/proxmox >= 0.108.0, and emits the
optional device_passthrough / mount_point / idmap blocks as `dynamic`
constructs gated on their list vars (so docker-host, which sets none,
renders nothing). Dual-mode (module-level test_*()->bool + main()->int),
stdlib only, mirroring test_dev_vm_module_shape.py.

Per mem-1781892715-142d the block regexes anchor on the inner driver
(for_each = var.<list>), NOT just the `dynamic "<block>"` opener, so a
bare/empty block could not satisfy the check.
"""

import json
import pathlib
import re
import subprocess
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
MODULE = REPO_ROOT / "tofu" / "modules" / "lxc_service"
TOFU_DIR = REPO_ROOT / "tofu"

# Unprivileged default map constants (design §5.1/§5.3): container 0..65535 maps
# to host 100000..165535, and the full id space is 65536 entries.
ID_SPACE = 65536
UID_OFFSET = 100000


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


def test_resource_is_container() -> bool:
    main_file = MODULE / "main.tf"
    if not main_file.is_file():
        print("FAIL: resource is proxmox_virtual_environment_container (main.tf missing)")
        return False
    body = main_file.read_text()
    ok = re.search(r'resource\s+"proxmox_virtual_environment_container"', body) is not None
    print(f"{'OK' if ok else 'FAIL'}: resource is proxmox_virtual_environment_container")
    return ok


def test_unprivileged_defaults_true() -> bool:
    vars_file = MODULE / "variables.tf"
    if not vars_file.is_file():
        print("FAIL: variable unprivileged defaults true (variables.tf missing)")
        return False
    body = vars_file.read_text()
    has_default = re.search(
        r'variable\s+"unprivileged"\s*\{[^{}]*?default\s*=\s*true',
        body,
        re.DOTALL,
    )
    ok = has_default is not None
    print(f"{'OK' if ok else 'FAIL'}: variable unprivileged defaults true")
    return ok


def test_versions_pin_bpg_floor() -> bool:
    versions_file = MODULE / "versions.tf"
    if not versions_file.is_file():
        print("FAIL: versions.tf pins bpg/proxmox >= 0.108.0 (versions.tf missing)")
        return False
    body = versions_file.read_text()
    has_pin = re.search(
        r'source\s*=\s*"bpg/proxmox".*?version\s*=\s*">=\s*0\.108\.0"',
        body,
        re.DOTALL,
    )
    ok = has_pin is not None
    print(f"{'OK' if ok else 'FAIL'}: versions.tf pins bpg/proxmox >= 0.108.0")
    return ok


def test_device_passthrough_dynamic() -> bool:
    main_file = MODULE / "main.tf"
    if not main_file.is_file():
        print("FAIL: dynamic device_passthrough gated on var.device_passthroughs (main.tf missing)")
        return False
    body = main_file.read_text()
    has_block = re.search(
        r'dynamic\s+"device_passthrough"\s*\{[^{}]*?for_each\s*=\s*var\.device_passthroughs',
        body,
        re.DOTALL,
    )
    ok = has_block is not None
    print(f"{'OK' if ok else 'FAIL'}: dynamic device_passthrough gated on var.device_passthroughs")
    return ok


def test_mount_point_dynamic() -> bool:
    main_file = MODULE / "main.tf"
    if not main_file.is_file():
        print("FAIL: dynamic mount_point gated on var.bind_mounts (main.tf missing)")
        return False
    body = main_file.read_text()
    has_block = re.search(
        r'dynamic\s+"mount_point"\s*\{[^{}]*?for_each\s*=\s*var\.bind_mounts',
        body,
        re.DOTALL,
    )
    ok = has_block is not None
    print(f"{'OK' if ok else 'FAIL'}: dynamic mount_point gated on var.bind_mounts")
    return ok


def test_idmap_dynamic() -> bool:
    main_file = MODULE / "main.tf"
    if not main_file.is_file():
        print("FAIL: dynamic idmap gated on gid_maps/uid_maps (main.tf missing)")
        return False
    body = main_file.read_text()
    # Anchor on the inner driver: the dynamic idmap iterates a local that is
    # built from BOTH var.gid_maps and var.uid_maps. An empty pair renders no
    # idmap blocks (docker-host case).
    has_dyn = re.search(
        r'dynamic\s+"idmap"\s*\{[^{}]*?for_each\s*=\s*local\.idmap_entries',
        body,
        re.DOTALL,
    )
    feeds_gid = re.search(r'idmap_entries\s*=.*?var\.gid_maps', body, re.DOTALL)
    feeds_uid = re.search(r'idmap_entries\s*=.*?var\.uid_maps', body, re.DOTALL)
    ok = bool(has_dyn and feeds_gid and feeds_uid)
    print(f"{'OK' if ok else 'FAIL'}: dynamic idmap gated on local.idmap_entries (from var.gid_maps + var.uid_maps)")
    return ok


def test_idmap_type_literals_valid() -> bool:
    """Regression (mem-1781916305-0a00): bpg/proxmox v0.110 validates the idmap
    block `type` to exactly {"uid","gid"}. The earlier literals "g"/"u" are
    rejected at plan time (`Error: expected type to be one of ["uid" "gid"], got
    g`). The gid_maps branch MUST tag type="gid" and the uid_maps branch
    type="uid"; reverting to "g"/"u" must fail this gate."""
    main_file = MODULE / "main.tf"
    if not main_file.is_file():
        print("FAIL: idmap type literals valid (main.tf missing)")
        return False
    body = main_file.read_text()
    # Anchor each type literal to its source list comprehension so we verify the
    # gid branch -> "gid" and the uid branch -> "uid" specifically.
    gid_ok = re.search(
        r'var\.gid_maps\s*:\s*\{[^{}]*?type\s*=\s*"gid"',
        body,
        re.DOTALL,
    )
    uid_ok = re.search(
        r'var\.uid_maps\s*:\s*\{[^{}]*?type\s*=\s*"uid"',
        body,
        re.DOTALL,
    )
    # Guard against any rejected literal sneaking back in (code only; comments
    # may cite the old values for historical context).
    main_code = re.sub(r"#[^\n]*", "", body)
    no_bad = re.search(r'type\s*=\s*"(?:g|u|group|user)"', main_code) is None
    ok = bool(gid_ok and uid_ok and no_bad)
    print(f"{'OK' if ok else 'FAIL'}: idmap type literals are gid/uid (gid={bool(gid_ok)} uid={bool(uid_ok)} no_bad={no_bad})")
    return ok


def _tofu_eval_json(expr: str):
    """Evaluate an HCL expression in the root tofu dir via `tofu console` and
    return the parsed value. `jsonencode(...)` makes the console print a single
    JSON-string literal, so we json.loads twice (outer HCL string -> inner JSON).
    Returns None on any failure (missing local, console error, parse error) so
    the caller reports FAIL. `tofu console` evaluates locals offline with no
    provider auth (locals never touch resources)."""
    if not TOFU_DIR.is_dir():
        return None
    try:
        # The root config has a module block, so the working dir must be
        # initialized (modules registered) before console can evaluate. Mirrors
        # the init step test_tofu_validate runs in the submodule.
        init = subprocess.run(
            ["tofu", "init", "-backend=false", "-input=false"],
            cwd=TOFU_DIR,
            capture_output=True,
            text=True,
        )
        if init.returncode != 0:
            return None
        result = subprocess.run(
            ["tofu", "console"],
            cwd=TOFU_DIR,
            input=f"jsonencode({expr})\n",
            capture_output=True,
            text=True,
        )
    except FileNotFoundError:
        return None
    for line in reversed(result.stdout.splitlines()):
        line = line.strip()
        if line.startswith('"'):
            try:
                return json.loads(json.loads(line))
            except (ValueError, TypeError):
                continue
    return None


def _check_contiguous(tiles) -> tuple:
    """Assert the idmap tiling is gap-free, contiguous, non-overlapping and fully
    covers container 0..ID_SPACE. Strict adjacency (next.container_id ==
    prev.container_id + prev.size) rules out BOTH gaps and overlaps."""
    if not isinstance(tiles, list) or not tiles:
        return False, "tiling is empty or not a list"
    ordered = sorted(tiles, key=lambda t: t["container_id"])
    if ordered[0]["container_id"] != 0:
        return False, f"first tile starts at {ordered[0]['container_id']}, not 0"
    for prev, cur in zip(ordered, ordered[1:]):
        expected = prev["container_id"] + prev["size"]
        if cur["container_id"] != expected:
            return False, (
                f"gap/overlap: tile at {cur['container_id']} expected {expected}"
            )
    last = ordered[-1]
    end = last["container_id"] + last["size"]
    if end != ID_SPACE:
        return False, f"tiling ends at {end}, not {ID_SPACE}"
    return True, "contiguous 0..%d" % ID_SPACE


def test_idmap_tiling_gapfree() -> bool:
    """AC2: the gid tiling (local.plex_gid_maps) is gap-free/contiguous and
    punches each host_gid (44 video, 993 render) through 1:1 (size-1 tile with
    host_id == container_id). Evaluated from the real HCL via tofu console."""
    tiles = _tofu_eval_json("local.plex_gid_maps")
    if tiles is None:
        print("FAIL: idmap gid tiling gap-free (could not evaluate local.plex_gid_maps)")
        return False
    contiguous, why = _check_contiguous(tiles)
    if not contiguous:
        print(f"FAIL: idmap gid tiling gap-free ({why})")
        return False
    punches = {t["container_id"] for t in tiles if t["size"] == 1 and t["host_id"] == t["container_id"]}
    missing = {44, 993} - punches
    ok = not missing
    print(f"{'OK' if ok else 'FAIL'}: idmap gid tiling gap-free + 1:1 punches at 44/993 (missing={missing})")
    return ok


def test_idmap_uid_full_offset() -> bool:
    """AC2: the uid map (local.plex_uid_maps) needs no punches — a single
    full-offset tile container 0 -> host 100000, size 65536."""
    tiles = _tofu_eval_json("local.plex_uid_maps")
    if tiles is None:
        print("FAIL: uid map full-offset (could not evaluate local.plex_uid_maps)")
        return False
    ok = (
        len(tiles) == 1
        and tiles[0]["container_id"] == 0
        and tiles[0]["host_id"] == UID_OFFSET
        and tiles[0]["size"] == ID_SPACE
    )
    print(f"{'OK' if ok else 'FAIL'}: uid map is single full-offset tile 0->{UID_OFFSET} size {ID_SPACE}")
    return ok


def test_idmap_generated_from_host_gids() -> bool:
    """AC3: the tiling is DERIVED by folding over local.host_gids, not
    hand-enumerated. The GID literals (993/44) must live ONLY in the host_gids
    block of locals.tf — never as per-GID punch tiles in main.tf — so adding a
    GID regenerates the tiling."""
    locals_file = TOFU_DIR / "locals.tf"
    main_file = TOFU_DIR / "main.tf"
    if not locals_file.is_file() or not main_file.is_file():
        print("FAIL: idmap generated from host_gids (locals.tf/main.tf missing)")
        return False
    locals_body = locals_file.read_text()
    main_body = main_file.read_text()
    # The tiling folds over values(local.host_gids), and plex_gid_maps/
    # plex_uid_maps are the exported tilings.
    folds = re.search(r"values\(local\.host_gids\)", locals_body) is not None
    exports = (
        re.search(r"plex_gid_maps\s*=", locals_body) is not None
        and re.search(r"plex_uid_maps\s*=", locals_body) is not None
    )
    # The GID literals must not be hand-written as tiles in main.tf (comments,
    # which may cite the GIDs for context, are stripped before the check).
    main_code = re.sub(r"#[^\n]*", "", main_body)
    no_literal_gid = re.search(r"\b(993|44)\b", main_code) is None
    ok = folds and exports and no_literal_gid
    print(f"{'OK' if ok else 'FAIL'}: idmap derived from values(local.host_gids), no GID literals in main.tf")
    return ok


def test_plex_module_wired() -> bool:
    """AC1: module "plex" instantiates lxc_service with GPU device_passthrough
    (renderD128 + card1 GIDs from local.host_gids), the /tank/media -> /media
    bind, and the tiled gid/uid maps."""
    main_file = TOFU_DIR / "main.tf"
    if not main_file.is_file():
        print("FAIL: module plex wired (main.tf missing)")
        return False
    body = main_file.read_text()
    block = re.search(r'module\s+"plex"\s*\{(.*?)\n\}', body, re.DOTALL)
    if not block:
        print("FAIL: module plex wired (no module \"plex\" block)")
        return False
    b = block.group(1)
    checks = {
        "renderD128 passthrough": re.search(r"/dev/dri/renderD128", b),
        "card1 passthrough": re.search(r"/dev/dri/card1", b),
        "render gid from host_gids": re.search(r"local\.host_gids\.render", b),
        "video gid from host_gids": re.search(r"local\.host_gids\.video", b),
        "tank media bind host": re.search(r'host_path\s*=\s*"/tank/media"', b),
        "media bind ct path": re.search(r'ct_path\s*=\s*"/media"', b),
        "gid_maps tiled": re.search(r"gid_maps\s*=\s*local\.plex_gid_maps", b),
        "uid_maps tiled": re.search(r"uid_maps\s*=\s*local\.plex_uid_maps", b),
    }
    missing = [k for k, v in checks.items() if v is None]
    ok = not missing
    print(f"{'OK' if ok else 'FAIL'}: module plex wired (missing={missing})")
    return ok


def test_plex_nesting_enabled() -> bool:
    """Regression (mem-1782080830-9609): the Plex CT 110 vzreboot timed out
    because module "plex" OMITTED `nesting`, defaulting it to false
    (variables.tf). The Debian 13 template ships systemd 257, which hangs on
    first boot in an unprivileged CT without features.nesting=true, so the
    create's reboot step never completes and the CT is left tainted. docker_host
    (nesting=true) is the live positive control. The plex module MUST pass
    nesting = true; reverting to the default (omitting it) must fail this gate."""
    main_file = TOFU_DIR / "main.tf"
    if not main_file.is_file():
        print("FAIL: plex nesting enabled (main.tf missing)")
        return False
    body = main_file.read_text()
    block = re.search(r'module\s+"plex"\s*\{(.*?)\n\}', body, re.DOTALL)
    if not block:
        print("FAIL: plex nesting enabled (no module \"plex\" block)")
        return False
    # Strip comments so the historical nesting note can't satisfy the check.
    code = re.sub(r"#[^\n]*", "", block.group(1))
    ok = re.search(r"nesting\s*=\s*true", code) is not None
    print(f"{'OK' if ok else 'FAIL'}: module plex passes nesting = true")
    return ok


def test_operator_ssh_keys_wired() -> bool:
    """Regression (DEBUG.md 2026-06-22): `just play` SSH failed with
    "Permission denied (publickey,password)" because NEITHER module call passed
    ssh_public_keys, so user_account.keys=[] in tfstate and the provisioned CTs
    had no root credential. The fix declares a root-level operator SSH key source
    (variables.tf operator_ssh_public_keys / operator_ssh_public_key_file, merged
    into local.operator_ssh_keys) and wires it as ssh_public_keys into BOTH the
    docker_host and plex module calls. Dropping either wiring — or the variable —
    must fail this gate."""
    main_file = TOFU_DIR / "main.tf"
    vars_file = TOFU_DIR / "variables.tf"
    if not main_file.is_file() or not vars_file.is_file():
        print("FAIL: operator ssh keys wired (tofu/main.tf or variables.tf missing)")
        return False
    vars_body = vars_file.read_text()
    # The root operator-key variable(s) must be declared.
    var_declared = re.search(
        r'variable\s+"operator_ssh_public_keys"', vars_body
    ) is not None

    main_body = main_file.read_text()
    missing = []
    for mod in ("docker_host", "plex"):
        block = re.search(r'module\s+"%s"\s*\{(.*?)\n\}' % mod, main_body, re.DOTALL)
        if not block:
            missing.append(f"{mod} (no module block)")
            continue
        # Strip comments so a comment mentioning ssh_public_keys can't satisfy it.
        code = re.sub(r"#[^\n]*", "", block.group(1))
        wired = re.search(
            r'ssh_public_keys\s*=\s*(?:local\.operator_ssh_keys|var\.operator_ssh_public_keys)',
            code,
        )
        if not wired:
            missing.append(mod)
    ok = var_declared and not missing
    print(
        f"{'OK' if ok else 'FAIL'}: operator ssh keys wired into both module calls "
        f"(var_declared={var_declared} missing={missing})"
    )
    return ok


def test_plex_outputs() -> bool:
    """AC4: outputs.tf exposes plex id/name/ipv4 (mirroring docker_host) so the
    Ansible inventory can target the Plex host in Step 8."""
    outputs_file = TOFU_DIR / "outputs.tf"
    if not outputs_file.is_file():
        print("FAIL: plex outputs present (outputs.tf missing)")
        return False
    body = outputs_file.read_text()
    needed = ["plex_vm_id", "plex_name", "plex_ipv4"]
    missing = [n for n in needed if re.search(r'output\s+"%s"' % n, body) is None]
    ok = not missing
    print(f"{'OK' if ok else 'FAIL'}: plex outputs present (missing={missing})")
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


def main() -> int:
    results = [
        test_module_directory_exists(),
        test_required_files_exist(),
        test_resource_is_container(),
        test_unprivileged_defaults_true(),
        test_versions_pin_bpg_floor(),
        test_device_passthrough_dynamic(),
        test_mount_point_dynamic(),
        test_idmap_dynamic(),
        test_idmap_type_literals_valid(),
        test_idmap_tiling_gapfree(),
        test_idmap_uid_full_offset(),
        test_idmap_generated_from_host_gids(),
        test_plex_module_wired(),
        test_plex_nesting_enabled(),
        test_operator_ssh_keys_wired(),
        test_plex_outputs(),
        test_tofu_validate(),
    ]
    total, passed = len(results), sum(results)
    if passed == total:
        print(f"PASS: {passed}/{total}")
        return 0
    print(f"FAIL: {total - passed}/{total} checks failed")
    return 1


if __name__ == "__main__":
    sys.exit(main())
