#!/usr/bin/env bash
# Ansible Vault password resolver (referenced by ansible.cfg
# vault_password_file). The password is never committed: it is read from
# $ANSIBLE_VAULT_PASSWORD, set in the gitignored mise.local.toml
# (template: mise.local.toml.example documents it). The shipped
# group_vars/vault.yml holds placeholders only; rekey with `ansible-vault
# rekey` before storing real secrets.
set -euo pipefail

if [[ -z "${ANSIBLE_VAULT_PASSWORD:-}" ]]; then
  echo "ANSIBLE_VAULT_PASSWORD is unset; define it in mise.local.toml" >&2
  exit 1
fi

printf '%s' "${ANSIBLE_VAULT_PASSWORD}"
