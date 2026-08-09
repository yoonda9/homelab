#!/usr/bin/env bash
set -euo pipefail
# ============================================================================
# plex_blip_capture.sh — one-shot Tier-0 "blip" evidence grab (design §4.3, C3)
#
# Usage: scripts/plex_blip_capture.sh   (also: just plex-blip-capture)
#
# Perishable Tier-0 state — live locks, the session list, thread states, WAL
# size — dies in seconds. Today the grab is ~a dozen commands across two SSH
# hops, so in practice it never happens. This is the ONE command that captures
# the design §4.3 bundle from the workstation against both hosts:
#
#   /tmp/plex-blip-<UTC-ISO>/
#   ├── manifest.json   # {command,host,exit_code,elapsed_ms,output_file} per entry (§5.4)
#   ├── ct110/          # CT 110 (Plex LXC) capture outputs
#   └── pve/            # PVE hypervisor capture outputs
#
# Interface contract (§4.3 / §6): READ-ONLY throughout; every command's
# non-zero exit is RECORDED in manifest.json and NEVER aborts the run — a
# partial capture is far better than none, and one unreachable host must still
# yield the other host's half.
#
# Step 8a — VERTICAL SLICE: the runnable skeleton + a schema-valid manifest.
# The full §4.3 command set and the sqlite3 `-readonly` shape guard land in 8c;
# the non-abortive-runner exit_code/elapsed_ms identity test in 8b; the
# one-host-unreachable partial bundle in 8d.
#
# Overridable via env (so the gate can drive it with no reachable host):
#   PLEX_BLIP_CAPTURE_OUTDIR      bundle dir (default /tmp/plex-blip-<UTC-ISO>)
#   PLEX_BLIP_CAPTURE_SSH         transport command (default "ssh"; word-split)
#   PLEX_BLIP_CAPTURE_CT110_HOST  CT 110 ssh target (default 192.168.1.110)
#   PLEX_BLIP_CAPTURE_PVE_HOST    PVE  ssh target   (default pve)
# ============================================================================

log() { echo >&2 "==> $*"; }

# --- Configuration (all env-overridable) ------------------------------------
OUTDIR="${PLEX_BLIP_CAPTURE_OUTDIR:-/tmp/plex-blip-$(date -u +%Y%m%dT%H%M%SZ)}"
CT110_HOST="${PLEX_BLIP_CAPTURE_CT110_HOST:-192.168.1.110}"
PVE_HOST="${PLEX_BLIP_CAPTURE_PVE_HOST:-pve}"
# Word-split so PLEX_BLIP_CAPTURE_SSH may carry flags ("ssh -o ConnectTimeout=5")
# or point at a stub transport for the gate.
read -r -a SSH_CMD <<<"${PLEX_BLIP_CAPTURE_SSH:-ssh}"

MANIFEST_ENTRIES="$OUTDIR/.manifest-entries.jsonl"

# --- Transport --------------------------------------------------------------
# One indirection so the gate can override ssh with a stub. Runs CMD on HOST;
# the caller redirects the combined stdout+stderr to the output file.
run_on_host() {
  local host="$1" cmd="$2"
  "${SSH_CMD[@]}" "$host" "$cmd"
}

now_ms() { date +%s%3N; }

# --- Capture runner ---------------------------------------------------------
# capture HOST SUBDIR OUTNAME COMMAND
# Runs COMMAND on HOST, times it, records its exit code, writes combined
# output to SUBDIR/OUTNAME under the bundle, and appends one manifest entry.
# NEVER aborts the run on a non-zero exit (§6: partial capture beats none).
capture() {
  local host="$1" subdir="$2" outname="$3" cmd="$4"
  local rel="$subdir/$outname"
  mkdir -p "$OUTDIR/$subdir"

  local start end elapsed rc
  start="$(now_ms)"
  rc=0
  run_on_host "$host" "$cmd" >"$OUTDIR/$rel" 2>&1 || rc=$?
  end="$(now_ms)"
  elapsed=$((end - start))

  jq -n \
    --arg command "$cmd" \
    --arg host "$host" \
    --argjson exit_code "$rc" \
    --argjson elapsed_ms "$elapsed" \
    --arg output_file "$rel" \
    '{command: $command, host: $host, exit_code: $exit_code, elapsed_ms: $elapsed_ms, output_file: $output_file}' \
    >>"$MANIFEST_ENTRIES"

  log "captured $rel (host=$host exit=$rc ${elapsed}ms)"
}

main() {
  mkdir -p "$OUTDIR"
  : >"$MANIFEST_ENTRIES"
  log "Tier-0 capture → $OUTDIR"

  # --- CT 110 (Plex LXC) — one representative probe; full §4.3 set is 8c -----
  capture "$CT110_HOST" ct110 sessions.json \
    "curl -s --max-time 5 http://127.0.0.1:32400/status/sessions"

  # --- PVE hypervisor — one representative probe; full §4.3 set is 8c --------
  capture "$PVE_HOST" pve dmesg.txt \
    "dmesg -T"

  # Assemble the manifest array from the per-entry JSONL.
  jq -s '.' "$MANIFEST_ENTRIES" >"$OUTDIR/manifest.json"
  rm -f "$MANIFEST_ENTRIES"

  log "wrote $OUTDIR/manifest.json"
  echo "$OUTDIR"
}

main "$@"
