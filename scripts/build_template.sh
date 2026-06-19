#!/usr/bin/env bash
set -euo pipefail
# ============================================================================
# build_template.sh — front-door for Packer-driven dev VM template builds
#
# Usage: scripts/build_template.sh {ubuntu26|fedora|windows11}
#
# Pipeline:
#   1. Validate the positional arg against the known short-name set.
#   2. Pre-flight that PROXMOX_HOST/USER/TOKEN_ID/TOKEN_SECRET are populated
#      (load via direnv/.envrc on the operator's workstation).
#   3. ubuntu26 + fedora: ensure tpl-cloud-{ubuntu26,fedora44} exists on PVE
#      via scripts/bootstrap_cloud_template.sh (DEC-020 option b — proxmox-clone
#      requires a Cloud-Init source template; the bootstrap is idempotent).
#      windows11 only: pre-flight genisoimage (per C-11) and pre-bake
#      packer_cache/autounattend-win11.iso with -volid "Unattend" from
#      packer/autounattend/windows11/ (per C-10). Fedora does NOT pre-bake a
#      cidata seed via genisoimage — DEC-019 Q2 picked on-the-fly cd_files via
#      Packer's additional_iso_files; only windows11 keeps the pre-bake.
#   4. cd into packer/, run `packer init .` (idempotent).
#   5. Resolve per-OS Packer source key (DEC-019 Q1: ubuntu26 + fedora →
#      proxmox-clone cloud-image flow; windows11 stays on proxmox-iso) and run
#      `packer build -force -only=<source> -var-file=common.pkrvars.hcl .`
#      (directory form — single-file form does NOT load _variables.pkr.hcl
#      siblings, so the shared variable + required_plugins declarations would
#      be invisible and every var.* reference would error at HCL parse).
#   6. Exit with Packer's exit code.
#
# Idempotent: re-running overwrites the prior template (FR-5). Silent: no
# [y/N] prompt before the destructive overwrite.
# ============================================================================

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

log() { echo >&2 "==> $*"; }
err() { echo >&2 "ERROR: $*"; }

usage() {
  cat >&2 <<'EOF'
Usage: scripts/build_template.sh {ubuntu26|fedora|windows11}

  ubuntu26   Build the pkr-ubuntu26 template (VM-ID 9100).
  fedora     Build the pkr-fedora-workstation template (VM-ID 9101).
  windows11  Build the pkr-win11 template (VM-ID 9102).
EOF
}

if [[ $# -ne 1 ]]; then
  usage
  exit 64
fi

NAME="$1"
case "$NAME" in
ubuntu26 | fedora | windows11) ;;
*)
  err "unknown OS '$NAME'"
  usage
  exit 64
  ;;
esac

log "step 1: env-var pre-flight"
REQUIRED_VARS=(PROXMOX_HOST PROXMOX_USER PROXMOX_TOKEN_ID PROXMOX_TOKEN_SECRET)
MISSING=()
for v in "${REQUIRED_VARS[@]}"; do
  if [[ -z "${!v:-}" ]]; then
    MISSING+=("$v")
  fi
done
if [[ ${#MISSING[@]} -gt 0 ]]; then
  err "missing required env vars: ${MISSING[*]}"
  err "source your mise env (mise install; copy mise.local.toml from the .example)"
  exit 78
fi

export PKR_VAR_proxmox_host="$PROXMOX_HOST"
export PKR_VAR_proxmox_user="$PROXMOX_USER"
export PKR_VAR_proxmox_token_id="$PROXMOX_TOKEN_ID"
export PKR_VAR_proxmox_token_secret="$PROXMOX_TOKEN_SECRET"

case "$NAME" in
ubuntu26)
  log "step 2: ubuntu26 — ensure tpl-cloud-ubuntu26 source template (idempotent)"
  "$REPO_ROOT/scripts/bootstrap_cloud_template.sh" ubuntu26
  ;;
fedora)
  log "step 2: fedora — ensure tpl-cloud-fedora44 source template (idempotent)"
  "$REPO_ROOT/scripts/bootstrap_cloud_template.sh" fedora
  ;;
windows11)
  log "step 2: windows11 — genisoimage pre-flight"
  if ! command -v genisoimage >/dev/null 2>&1; then
    err "genisoimage not found on PATH (required to pre-bake autounattend cidata)"
    err "install via 'sudo apt install genisoimage' (Debian/Ubuntu) or 'brew install cdrtools' (macOS)"
    exit 69
  fi

  log "step 3: windows11 — pre-bake autounattend cidata ISO"
  PACKER_CACHE_DIR="${PACKER_CACHE_DIR:-$REPO_ROOT/packer/packer_cache}"
  mkdir -p "$PACKER_CACHE_DIR"
  AUTOUNATTEND_ISO="$PACKER_CACHE_DIR/autounattend-win11.iso"
  AUTOUNATTEND_SRC="$REPO_ROOT/packer/autounattend/windows11"
  genisoimage \
    -output "$AUTOUNATTEND_ISO" \
    -volid "Unattend" \
    -joliet -rock -input-charset utf-8 \
    "$AUTOUNATTEND_SRC"
  log "       wrote $AUTOUNATTEND_ISO"
  ;;
esac

case "$NAME" in
ubuntu26) ONLY="proxmox-clone.ubuntu26" ;;
fedora) ONLY="proxmox-clone.fedora" ;;
windows11) ONLY="proxmox-iso.windows11" ;;
esac

log "step 4: packer init"
cd "$REPO_ROOT/packer"
packer init .

log "step 5: packer build -only=$ONLY (force=true overwrite)"
packer build -force -only="$ONLY" -var-file=common.pkrvars.hcl .

log "DONE: $NAME"
