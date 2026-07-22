"""Shape test for Step 3 — the CT 110 `/transcode` ramdisk bind mount.

Per `.agents/planning/2026-07-22-plex-ramdisk-transcoding/implementation/plan.md`
Step 3 — verifies `tofu/main.tf` `module "plex"` passes the host tmpfs
provisioned by Step 2 (`docs/runbooks/plex-ramdisk.md`: an `/etc/fstab` `tmpfs`
at `/mnt/plex-transcode`, `size=4G,uid=100999,gid=100991`) through to the
container as `/transcode`, read-write, so Plex transcodes into RAM instead of
the ZFS/DAS pool.

The load-bearing detail this file exists to pin is the **pairing**: the
`/mnt/plex-transcode` host path and the `/transcode` CT path must live in the
**same** `bind_mounts` entry of the **plex** module. Two independent greps over
`main.tf` are not that check — a stray comment, a different module, or the
module's own `bind_mounts` default would satisfy them. So every assertion below
runs against a *parsed* entry list: comments are stripped, the `bind_mounts`
list is extracted from inside the named module block, and each `{ ... }` entry
is parsed into a dict. Mutations that split the pair, flip `read_only`, or move
the entry to another module all redden.

Follows the repo's dual-mode shape-test convention (see
`test_lxc_service_module_shape.py`, `test_plex_ramdisk_runbook_shape.py`):
module-level `test_<name>() -> bool` functions that print `OK` / `FAIL: ...`
(no `assert`), plus `main() -> int` that sums the booleans and `sys.exit`s
non-zero on any failure. Stdlib only. The gate discovers this file by glob
(`scripts/run_gate.py`) and `main()` sums the `TESTS` tuple — a function not
listed there would be green-by-omission (mem-1784137124-c346), so every
`test_*` below is registered in `TESTS`.
"""

import pathlib
import re
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
MAIN_TF = REPO_ROOT / "tofu" / "main.tf"
LXC_VARIABLES_TF = REPO_ROOT / "tofu" / "modules" / "lxc_service" / "variables.tf"
RUNBOOK = REPO_ROOT / "docs" / "runbooks" / "plex-ramdisk.md"

HOST_PATH = "/mnt/plex-transcode"
CT_PATH = "/transcode"


def _read(path: pathlib.Path) -> str:
    return path.read_text() if path.is_file() else ""


def _strip_comments(body: str) -> str:
    """Drop `#` comments so prose about a path can never satisfy a check."""
    return re.sub(r"#[^\n]*", "", body)


def _module_body(body: str, name: str) -> str:
    """Inner text of `module "<name>" { ... }`, comments stripped ('' if absent)."""
    block = re.search(r'module\s+"%s"\s*\{(.*?)\n\}' % re.escape(name), body, re.DOTALL)
    return _strip_comments(block.group(1)) if block else ""


def _module_names(body: str) -> list:
    return re.findall(r'module\s+"([^"]+)"\s*\{', body)


def _bracketed(code: str, attr: str) -> str:
    """Text inside `attr = [ ... ]`, matched by bracket depth ('' if absent)."""
    opener = re.search(r"\b%s\s*=\s*\[" % re.escape(attr), code)
    if not opener:
        return ""
    start = opener.end()
    depth = 1
    for i in range(start, len(code)):
        if code[i] == "[":
            depth += 1
        elif code[i] == "]":
            depth -= 1
            if depth == 0:
                return code[start:i]
    return ""


def _objects(listing: str) -> list:
    """Split a HCL list body into its `{ ... }` object entries by brace depth."""
    entries, depth, start = [], 0, None
    for i, ch in enumerate(listing):
        if ch == "{":
            if depth == 0:
                start = i + 1
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0 and start is not None:
                entries.append(listing[start:i])
                start = None
    return entries


def _attrs(entry: str) -> dict:
    """Parse an object entry's `key = value` pairs (values kept as raw tokens)."""
    return {
        m.group(1): m.group(2).strip()
        for m in re.finditer(r'(\w+)\s*=\s*("[^"]*"|[^\s#]+)', entry)
    }


def _bind_mounts(body: str, module: str) -> list:
    """Parsed `bind_mounts` entries of one module block in main.tf."""
    return [_attrs(e) for e in _objects(_bracketed(_module_body(body, module), "bind_mounts"))]


def _transcode_entries(entries: list) -> list:
    return [e for e in entries if e.get("host_path") == f'"{HOST_PATH}"']


def test_plex_bind_mounts_parse() -> bool:
    """Premise guard: the parser really sees the plex module's existing binds.

    Without this, every check below could pass vacuously-red/green off an empty
    parse (a renamed module or a changed HCL layout would look like 'the entry
    is missing' rather than 'the test stopped working')."""
    entries = _bind_mounts(_read(MAIN_TF), "plex")
    known = {'"/tank/Media"', '"/tank/Server/AppData/plex"'}
    found = {e.get("host_path") for e in entries}
    ok = len(entries) >= 4 and known <= found
    print(
        f"{'OK' if ok else 'FAIL'}: module plex bind_mounts parse "
        f"(entries={len(entries)}, known_present={sorted(known & found)})"
    )
    return ok


def test_transcode_bind_pairing() -> bool:
    """AC: ONE entry carries host_path /mnt/plex-transcode AND ct_path /transcode.

    Asserted as a pairing inside a single parsed entry — two independent greps
    over main.tf would pass on a comment or on halves in different entries."""
    entries = _transcode_entries(_bind_mounts(_read(MAIN_TF), "plex"))
    paired = [e for e in entries if e.get("ct_path") == f'"{CT_PATH}"']
    ok = len(paired) == 1
    print(
        f"{'OK' if ok else 'FAIL'}: module plex has exactly one bind_mounts entry "
        f'pairing host_path "{HOST_PATH}" with ct_path "{CT_PATH}" '
        f"(host_path matches={len(entries)}, paired={len(paired)})"
    )
    return ok


def test_transcode_bind_is_writable() -> bool:
    """AC: that same entry is read_only = false — Plex WRITES its transcodes here.

    read_only = true (or an omitted attribute) would mount the ramdisk useless."""
    paired = [
        e
        for e in _transcode_entries(_bind_mounts(_read(MAIN_TF), "plex"))
        if e.get("ct_path") == f'"{CT_PATH}"'
    ]
    ok = len(paired) == 1 and paired[0].get("read_only") == "false"
    got = paired[0].get("read_only") if paired else None
    print(
        f"{'OK' if ok else 'FAIL'}: the {CT_PATH} bind entry sets read_only = false "
        f"(read_only={got!r})"
    )
    return ok


def test_transcode_host_path_matches_runbook() -> bool:
    """AC: cross-file consistency — the tofu host_path IS the runbook's fstab target.

    Step 2's operator procedure mounts the tmpfs at a path documented only in
    `docs/runbooks/plex-ramdisk.md`; if the two strings drift, the CT gets a
    bind of a plain (non-tmpfs) directory and the ramdisk silently does nothing.
    The runbook target is read out of its fstab line, not hardcoded here."""
    fstab = re.search(
        r"^\s*tmpfs\s+(\S+)\s+tmpfs\s+\S*size=4G", _read(RUNBOOK), re.MULTILINE
    )
    runbook_target = fstab.group(1) if fstab else None
    entries = _bind_mounts(_read(MAIN_TF), "plex")
    tofu_hosts = {
        e.get("host_path", "").strip('"')
        for e in entries
        if e.get("ct_path") == f'"{CT_PATH}"'
    }
    ok = runbook_target is not None and tofu_hosts == {runbook_target}
    print(
        f"{'OK' if ok else 'FAIL'}: tofu host_path for {CT_PATH} equals the runbook "
        f"fstab tmpfs target (runbook={runbook_target!r}, tofu={sorted(tofu_hosts)})"
    )
    return ok


def test_transcode_bind_scoped_to_plex_module() -> bool:
    """AC: the entry lives in module "plex" — not another module, not the default.

    Moving it to `module "docker_host"` (or leaning on the lxc_service
    `bind_mounts` variable default) would bind the ramdisk into the wrong
    container while a whole-file grep still matched."""
    body = _read(MAIN_TF)
    elsewhere = sorted(
        m
        for m in _module_names(body)
        if m != "plex" and _transcode_entries(_bind_mounts(body, m))
    )
    default_listing = _bracketed(
        _strip_comments(_read(LXC_VARIABLES_TF)), "default"
    )
    in_default = HOST_PATH in default_listing
    in_plex = bool(_transcode_entries(_bind_mounts(body, "plex")))
    ok = in_plex and not elsewhere and not in_default
    print(
        f"{'OK' if ok else 'FAIL'}: the {HOST_PATH} bind is scoped to module plex "
        f"(in_plex={in_plex}, other_modules={elsewhere}, in_module_default={in_default})"
    )
    return ok


TESTS = (
    test_plex_bind_mounts_parse,
    test_transcode_bind_pairing,
    test_transcode_bind_is_writable,
    test_transcode_host_path_matches_runbook,
    test_transcode_bind_scoped_to_plex_module,
)


def main() -> int:
    results = [fn() for fn in TESTS]
    total, passed = len(results), sum(results)
    if passed == total:
        print(f"PASS: {passed}/{total}")
        return 0
    print(f"FAIL: {total - passed}/{total}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
