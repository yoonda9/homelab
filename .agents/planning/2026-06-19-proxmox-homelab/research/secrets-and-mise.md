# Research: mise dev-env + secrets management

_Sources: mise.jdx.dev docs (verified 2026-06-19). Project is migrating direnv → mise (Q11)._

## mise replaces asdf + direnv + make/just; all config in `mise.toml`

```toml
[tools]
opentofu  = "1.9.0"      # registry tools, pinned
packer    = "1.12.0"
python    = "3.12"
"pipx:ansible" = "latest" # ansible has no good standalone binary → pipx backend
                          # (pipx auto-uses uvx when uv is on PATH → fast, fits the repo's uv usage)

[env]
PROXMOX_VE_ENDPOINT = "https://192.168.1.50:8006/"   # non-secret → committed
PROXMOX_VE_INSECURE = "true"
_.python.venv = { path = ".venv", create = true }    # auto-activates uv venv

[tasks.plan]  # `mise run plan`
run = "tofu -chdir=tofu plan"
[tasks.fmt]
run = ["tofu -chdir=tofu fmt", "ansible-lint"]
```
- `[tools]` merges across the config hierarchy (child overrides parent). opentofu, packer,
  python, ansible all resolvable.
- Auto-loads `[env]` on `cd` (the direnv-replacement behavior) when `mise activate` is in the shell.
- **`mise.local.toml`** = gitignored local overrides, **higher precedence** than `mise.toml`.

## Secrets options
1. **Plain dotenv** `_.file = ".env"` — loads, does NOT decrypt; must be gitignored.
2. **SOPS + age (built-in, EXPERIMENTAL):** mise transparently decrypts when `_.file` points at
   a sops-encrypted file:
   ```toml
   [env]
   _.file = { path = ".env.sops.json", redact = true }
   ```
   Setup: `mise use -g sops age`; `age-keygen -o ~/.config/mise/age.txt`;
   `sops encrypt -i --age "<age pubkey>" .env.sops.json`. Formats: JSON/YAML/TOML.
   **age-only — no AWS/GCP KMS.** Encrypted file is safe to commit.
3. **gitignored `mise.local.toml`** — simplest, zero crypto, but secrets live only on each
   machine (no shared encrypted source of truth; drift / accidental-commit risk).
4. **Ansible Vault** — purpose-built for **in-playbook** secrets; does NOT help with the shell
   env vars OpenTofu/Packer need.

## Recommendation (for the design decision, Q8)
**Split by consumer:**
- **mise + SOPS + age** for shell/OpenTofu/Packer env-var secrets (Proxmox API token, Cloudflare
  token, Plex claim). Encrypted-at-rest, committable, transparent decrypt on `cd`, one age key
  per repo. ⚠️ Flag: feature is **experimental** + **age-only**.
- **Ansible Vault** for secrets consumed **inside** playbooks/roles (service admin passwords,
  Grafana admin pw, app API keys) — integrates with `ansible-playbook --vault-id`.

Rationale: matches the repo's existing "env-vars-drive-the-provider" pattern (just moves the
source from `.envrc` to mise+SOPS), keeps secrets out of git encrypted rather than merely
gitignored, and uses each tool's native mechanism. If the experimental SOPS support proves
flaky, fall back to gitignored `mise.local.toml` for env secrets (documented escape hatch).

## direnv → mise migration mapping
| `.envrc` | `mise.toml [env]` |
|---|---|
| `export FOO=bar` | `FOO = "bar"` |
| `dotenv .env` | `_.file = ".env"` |
| `PATH_add ./bin` | `_.path = "./bin"` |
| `layout python` | `_.python.venv = { path=".venv", create=true }` |
| `source_env x.sh` | `_.source = "./x.sh"` |
Do **not** run direnv + mise together (unsupported). Remove the existing `.envrc` as part of
the migration; move `PROXMOX_VE_*` into `mise.toml` (non-secret) + SOPS file (token).

## Committed vs gitignored
- **Commit:** `mise.toml` (tool pins, non-secret env, tasks), `.env.sops.json` (encrypted),
  `.sops.yaml` (recipients), `vault`-encrypted ansible files.
- **Gitignore:** `mise.local.toml`, plaintext `.env`, age private key (lives in `~/.config/mise`).

## URLs
- config: https://mise.jdx.dev/configuration.html · env: https://mise.jdx.dev/environments/
- secrets/sops: https://mise.jdx.dev/environments/secrets/sops.html · direnv: https://mise.jdx.dev/direnv.html
- pipx backend: https://mise.jdx.dev/dev-tools/backends/pipx.html
