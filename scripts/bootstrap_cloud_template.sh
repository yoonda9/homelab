#!/usr/bin/env bash
set -euo pipefail
# ============================================================================
# bootstrap_cloud_template.sh — one-time-per-cloud-image PVE source-template
# bootstrap for the Packer proxmox-clone flow (DEC-020 option b).
#
# proxmox-clone REQUIRES that tpl-cloud-<os> already exist on the PVE node;
# this script ssh's to $PROXMOX_HOST and runs the qm create / importdisk /
# qm set / qm template chain from research.md:55-68 idempotently. Re-running
# is safe: a `qm status $SRC_VMID` guard short-circuits when the source
# template VM is already present.
#
# Usage: scripts/bootstrap_cloud_template.sh {ubuntu26|fedora}
#
# Env vars (read from .envrc / direnv):
#   PROXMOX_HOST       (required) PVE node hostname or IP
#   PVE_SSH_USER       (optional, default: root) ssh login on the PVE node
# ============================================================================

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

log() { echo >&2 "==> $*"; }
err() { echo >&2 "ERROR: $*"; }

usage() {
  cat >&2 <<'EOF'
Usage: scripts/bootstrap_cloud_template.sh {ubuntu26|fedora}

  ubuntu26   Bootstrap tpl-cloud-ubuntu26 (vmid 9000) from the Ubuntu 26.04
             server cloud image at cloud-images.ubuntu.com.
  fedora     Bootstrap tpl-cloud-fedora44 (vmid 9001) from the Fedora 44
             Cloud Base Generic qcow2 at download.fedoraproject.org.
EOF
}

if [[ $# -ne 1 ]]; then
  usage
  exit 64
fi

NAME="$1"
case "$NAME" in
ubuntu26)
  SRC_VMID=9000
  TPL_NAME="tpl-cloud-ubuntu26"
  IMG_URL="https://cloud-images.ubuntu.com/releases/26.04/release/ubuntu-26.04-server-cloudimg-amd64.img"
  ;;
fedora)
  SRC_VMID=9001
  TPL_NAME="tpl-cloud-fedora44"
  IMG_URL="https://download.fedoraproject.org/pub/fedora/linux/releases/44/Cloud/x86_64/images/Fedora-Cloud-Base-Generic-44-1.7.x86_64.qcow2"
  ;;
*)
  err "unknown OS '$NAME'"
  usage
  exit 64
  ;;
esac

if [[ -z "${PROXMOX_HOST:-}" ]]; then
  err "PROXMOX_HOST not set; run 'direnv allow' or export it"
  exit 78
fi

PVE_USER="${PVE_SSH_USER:-root}"
SSH_TARGET="${PVE_USER}@${PROXMOX_HOST}"
IMG_FILE="/tmp/$(basename "$IMG_URL")"

ssh_pve() {
  ssh -o StrictHostKeyChecking=accept-new "$SSH_TARGET" "$@"
}

log "step 1: idempotent guard — qm status $SRC_VMID on $SSH_TARGET"
if ssh_pve "qm status $SRC_VMID" >/dev/null 2>&1; then
  # VMID exists. Verify the occupant is actually $TPL_NAME (with template:1 +
  # scsi0) before short-circuiting. A bare 'qm status' check is too weak:
  # VMIDs 9000/9001 may be occupied by pre-existing manual cloud templates
  # whose names differ. Packer's proxmox-clone resolves clone_vm by NAME, so
  # a silent skip here turns into a misleading "VM not found" downstream.
  cfg="$(ssh_pve "qm config $SRC_VMID" 2>/dev/null || true)"
  existing_name="$(printf '%s\n' "$cfg" | sed -n 's/^name:[[:space:]]*//p' | head -n1)"
  has_template=0
  if printf '%s\n' "$cfg" | grep -q '^template:[[:space:]]*1'; then has_template=1; fi
  has_scsi0=0
  if printf '%s\n' "$cfg" | grep -q '^scsi0:'; then has_scsi0=1; fi
  if [[ "$existing_name" == "$TPL_NAME" && "$has_template" -eq 1 && "$has_scsi0" -eq 1 ]]; then
    # Self-heal a dirty ide2 cloud-init drive on the existing template. The
    # line-136 attach was removed, but a pre-existing or web-UI-introduced
    # ide2 cidata seed re-creates the dual-cidata SSH-timeout regression
    # (mem-1777927418-a0b3) because this guard would otherwise short-circuit
    # and leave it attached for packer's clone to inherit.
    if printf '%s\n' "$cfg" | grep -q '^ide2:'; then
      log "       repairing dirty ide2 cloud-init drive on existing $TPL_NAME (qm set $SRC_VMID --delete ide2)"
      ssh_pve "qm set $SRC_VMID --delete ide2"
    fi
    log "       template VM $SRC_VMID ($TPL_NAME) already exists; skipping bootstrap"
    exit 0
  fi
  err "VMID $SRC_VMID is occupied but is NOT $TPL_NAME (found name='$existing_name', template=$has_template, scsi0=$has_scsi0)."
  err "Remediation: free the VMID by destroying the colliding VM (qm destroy $SRC_VMID) or"
  err "renumbering it; alternatively change SRC_VMID in this script to an id that is free per"
  err "'pvesh get /cluster/resources --type vm'."
  exit 70
fi

log "step 2: download cloud image on PVE node — $IMG_URL"
ssh_pve "test -f $IMG_FILE || curl -fsSLo $IMG_FILE '$IMG_URL'"

log "step 3: qm create $SRC_VMID --name $TPL_NAME"
ssh_pve "qm create $SRC_VMID --name $TPL_NAME --memory 2048 --cpu host --cores 2 \
  --net0 virtio,bridge=vmbr0 --scsihw virtio-scsi-pci --serial0 socket \
  --ostype l26 --machine q35 --bios ovmf \
  --efidisk0 local-lvm:0,efitype=4m,pre-enrolled-keys=1"

log "step 4: qm importdisk $SRC_VMID $IMG_FILE local-lvm"
# Capture stdout+stderr; the parser must accept BOTH PVE output formats:
#   PVE 9 (Trixie): "unused0: successfully imported disk 'local-lvm:vm-NNNN-disk-X'"
#                   (unusedN: OUTSIDE quotes; only the volid is quoted)
#   PVE 8 legacy:   "Successfully imported disk as 'unused0:local-lvm:vm-NNNN-disk-X'"
#                   (whole unusedN:local-lvm:... INSIDE single quotes)
# The slot index X is NOT necessarily 0: step 3 already allocated
# vm-NNNN-disk-0 for efidisk0 via '--efidisk0 local-lvm:0,...', so importdisk
# lands on disk-1. Hardcoding 'disk-0' for scsi0 below would attach the 4 MiB
# EFI disk and, after 'qm template', rename the EFI LV to 'base-NNNN-disk-0'
# — leaving efidisk0's reference dangling and breaking proxmox-clone.
import_out="$(ssh_pve "qm importdisk $SRC_VMID $IMG_FILE local-lvm" 2>&1)"
printf '%s\n' "$import_out" >&2
imported_disk="$(printf '%s\n' "$import_out" \
  | sed -n \
      -e "s/^unused[0-9]\+:.*'local-lvm:\(vm-[0-9]\+-disk-[0-9]\+\)'.*/\1/p" \
      -e "s/.*'unused[0-9]*:local-lvm:\(vm-[0-9]\+-disk-[0-9]\+\)'.*/\1/p" \
  | tail -n1)"
if [[ -z "$imported_disk" ]]; then
  err "could not parse imported disk name from 'qm importdisk' output"
  err "expected one of:"
  err "  PVE 9: unusedN: successfully imported disk 'local-lvm:vm-${SRC_VMID}-disk-X'"
  err "  PVE 8: Successfully imported disk as 'unusedN:local-lvm:vm-${SRC_VMID}-disk-X'"
  exit 70
fi

log "step 5: attach scsi0 ($imported_disk) + boot order + grow scsi0 to fit workstation install"
ssh_pve "qm set $SRC_VMID --scsi0 local-lvm:${imported_disk},discard=on,ssd=1"
ssh_pve "qm set $SRC_VMID --boot order=scsi0"
# Grow scsi0 from the cloud image's 5 GiB virtual size (Fedora 44 / Ubuntu 26
# Cloud Base both ship at 5 GiB) to 25 GiB so cloud-init's growpart fills the
# clone's rootfs to ~25 GiB on first boot. Without this, the fedora packer
# build's '@workstation-product-environment' dnf provisioner exhausts the
# rootfs mid-install with "needs NMB more space on the / filesystem" climbing
# from ~2880 MiB to 3729 MiB and exits 1 (DEBUG.md task-1777857784-fb79;
# evidence: mem-1777948460-029f single-variable resize 5G→25G test finished
# build in 5m37s with zero ENOSPC matches in logs/fedora-enospc-test.log).
# +20G is additive and non-destructive on existing storage; ubuntu26 gets the
# same headroom for free.
ssh_pve "qm resize $SRC_VMID scsi0 +20G"
# Intentionally NO '--ide2 local-lvm:cloudinit' here. Packer's proxmox-clone
# attaches its own NoCloud seed via additional_iso_files (ide0, label=cidata),
# and the bpg/proxmox provider's initialization{} block on Tofu clones
# generates its own cidata drive too. Pre-baking a Proxmox-auto cloud-init
# drive on the source template causes the clone to boot with TWO cidata-
# labelled CDs (sr0=our seed, sr1=Proxmox empty seed); cloud-init's NoCloud
# datasource picks one by /dev/disk/by-label/cidata and silently ignores the
# other. When it picks the empty Proxmox seed, our user-data (ssh_pwauth:true,
# user unlock) never runs, sshd keeps PasswordAuthentication=no, and Packer's
# SSH login hangs until its 30-minute timeout (DEBUG.md task-1777857784-fb79).

log "step 6: qm template $SRC_VMID"
ssh_pve "qm template $SRC_VMID"

log "DONE: $TPL_NAME (vmid $SRC_VMID) ready as Cloud-Init source template"
