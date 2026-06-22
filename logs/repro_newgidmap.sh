#!/usr/bin/env bash
# Faithful pve-path repro of CT110 newgidmap failure on the REAL /usr/bin/newgidmap.
# root-owned userns (real uid 0 == target owner 0 -> ownership check passes),
# newgidmap called by root, allowance checked against root's /etc/subgid == lxc_map_ids.
# EXACT DEBUG.md gid map:
#   0 100000 44 / 44 44 1 / 45 100045 948 / 993 993 1 / 994 100994 64542
set -u

SG=/etc/subgid
BAK=/tmp/subgid.repro.bak
MAP="0 100000 44 44 44 1 45 100045 948 993 993 1 994 100994 64542"

cp -f "$SG" "$BAK" 2>/dev/null || : > "$BAK"

run_trial() {
  local label="$1"; shift
  # remaining args = lines to put in /etc/subgid
  : > "$SG"
  for line in "$@"; do echo "$line" >> "$SG"; done
  echo "=== $label ==="
  echo "  subgid: $(tr '\n' ' ' < "$SG")"
  # root-owned userns held open via fifo
  local fifo; fifo=$(mktemp -u /tmp/repro.fifo.XXXX); mkfifo "$fifo"
  unshare -U bash -c "echo \$\$ > ${fifo}.pid; read _ < ${fifo}" &
  local upid; for _ in 1 2 3 4 5 6 7 8 9 10; do [ -s "${fifo}.pid" ] && break; sleep 0.1; done
  upid=$(cat "${fifo}.pid")
  local out rc
  out=$(newgidmap "$upid" $MAP 2>&1); rc=$?
  echo "  newgidmap exit=$rc"
  [ -n "$out" ] && echo "  stderr: $out"
  echo "  gid_map: $(cat /proc/$upid/gid_map 2>/dev/null | tr -s ' \n' ' ' )"
  echo _ > "$fifo"; wait 2>/dev/null
  rm -f "$fifo" "${fifo}.pid"
}

run_trial "TRIAL1 default-only (root:100000:65536) -> expect FAIL [44-45)" "root:100000:65536"
run_trial "TRIAL2 +punches (root:44:1 root:993:1) -> expect exit0 full map" "root:100000:65536" "root:44:1" "root:993:1"
run_trial "ADV drop 993:1 keep 44:1 -> expect FAIL rolls to [993-994)" "root:100000:65536" "root:44:1"

# restore
cp -f "$BAK" "$SG"
echo "=== restored /etc/subgid (root lines): $(grep -c '^root:' "$SG" 2>/dev/null) ==="
rm -f "$BAK"
