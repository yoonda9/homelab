"""Adversarial smoke test for the OpenTofu scaffold under `tofu/`.

Mirrors the shape of the other `scripts/test_tofu_*.py` scripts (e.g.
`scripts/test_tofu_vm_module.py`): load the artifact, assert key
declarations are present, fail with a precise message otherwise.
Intentionally text-based so we don't add an HCL parser dependency for a
one-step scaffold check.
"""

import os
import re
import sys

TOFU_DIR = os.environ.get("TOFU_DIR", "tofu")
VERSIONS_PATH = os.environ.get(
    "VERSIONS_PATH", os.path.join(TOFU_DIR, "versions.tf")
)
PROVIDERS_PATH = os.environ.get(
    "PROVIDERS_PATH", os.path.join(TOFU_DIR, "providers.tf")
)
VARIABLES_PATH = os.environ.get(
    "VARIABLES_PATH", os.path.join(TOFU_DIR, "variables.tf")
)
GITIGNORE_PATH = os.environ.get(
    "GITIGNORE_PATH", os.path.join(TOFU_DIR, ".gitignore")
)

EXPECTED_PROVIDER_SOURCE = "bpg/proxmox"
EXPECTED_PROVIDER_LOCAL_NAME = "proxmox"
EXPECTED_API_TOKEN_VAR = "pve_api_token"
REQUIRED_VARIABLES = (
    "pve_api_endpoint",
    "pve_api_token",
    "pve_node_name",
    "pve_insecure",
)
REQUIRED_GITIGNORE_PATTERNS = (
    ".terraform/",
    "*.tfstate",
    "*.tfstate.backup",
    "terraform.tfvars",
    "*.auto.tfvars",
)


def read_text(path):
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def test_tofu_dir_exists():
    if os.path.isdir(TOFU_DIR):
        print(f"OK: tofu directory exists at '{TOFU_DIR}'.")
        return True
    print(f"FAIL: tofu directory '{TOFU_DIR}' is missing.")
    return False


def test_versions_declares_bpg_provider():
    text = read_text(VERSIONS_PATH)
    if text is None:
        print(f"FAIL: '{VERSIONS_PATH}' is missing.")
        return False
    # The required_providers block must declare a provider whose source
    # is "bpg/proxmox". Match the source line directly.
    if not re.search(
        r'source\s*=\s*"bpg/proxmox"', text
    ):
        print(
            f"FAIL: '{VERSIONS_PATH}' does not declare provider "
            f"source = \"{EXPECTED_PROVIDER_SOURCE}\" "
            f"(required_providers must pin bpg/proxmox)."
        )
        return False
    if not re.search(r"required_version\s*=", text):
        print(
            f"FAIL: '{VERSIONS_PATH}' must set required_version."
        )
        return False
    if not re.search(r"version\s*=\s*\"[~>=\s\d.]+\"", text):
        print(
            f"FAIL: '{VERSIONS_PATH}' must pin the bpg/proxmox "
            f"provider to a specific version constraint."
        )
        return False
    print(
        f"OK: '{VERSIONS_PATH}' declares "
        f"source = \"{EXPECTED_PROVIDER_SOURCE}\" with a version pin."
    )
    return True


def test_providers_wires_api_token():
    text = read_text(PROVIDERS_PATH)
    if text is None:
        print(f"FAIL: '{PROVIDERS_PATH}' is missing.")
        return False
    if not re.search(
        r'provider\s+"' + re.escape(EXPECTED_PROVIDER_LOCAL_NAME) + r'"',
        text,
    ):
        print(
            f"FAIL: '{PROVIDERS_PATH}' must contain a "
            f"provider \"{EXPECTED_PROVIDER_LOCAL_NAME}\" block."
        )
        return False
    if not re.search(
        r"api_token\s*=\s*var\." + re.escape(EXPECTED_API_TOKEN_VAR),
        text,
    ):
        print(
            f"FAIL: '{PROVIDERS_PATH}' must wire "
            f"api_token = var.{EXPECTED_API_TOKEN_VAR} "
            f"(token must come from the input variable)."
        )
        return False
    if not re.search(r"endpoint\s*=\s*var\.pve_api_endpoint", text):
        print(
            f"FAIL: '{PROVIDERS_PATH}' must wire "
            f"endpoint = var.pve_api_endpoint."
        )
        return False
    if not re.search(r"insecure\s*=\s*var\.pve_insecure", text):
        print(
            f"FAIL: '{PROVIDERS_PATH}' must wire "
            f"insecure = var.pve_insecure."
        )
        return False
    print(
        f"OK: '{PROVIDERS_PATH}' wires endpoint, api_token, and "
        f"insecure from input variables."
    )
    return True


def test_variables_declares_required_inputs():
    text = read_text(VARIABLES_PATH)
    if text is None:
        print(f"FAIL: '{VARIABLES_PATH}' is missing.")
        return False
    missing = []
    for name in REQUIRED_VARIABLES:
        if not re.search(
            r'variable\s+"' + re.escape(name) + r'"\s*\{', text
        ):
            missing.append(name)
    if missing:
        print(
            f"FAIL: '{VARIABLES_PATH}' missing variable "
            f"declarations: {', '.join(missing)}."
        )
        return False
    # pve_api_token must be sensitive so state files don't leak it
    # in plaintext on every plan/apply.
    token_block = re.search(
        r'variable\s+"pve_api_token"\s*\{(?P<body>[^}]*)\}', text
    )
    if not token_block or not re.search(
        r"sensitive\s*=\s*true", token_block.group("body")
    ):
        print(
            f"FAIL: '{VARIABLES_PATH}' variable "
            f"\"pve_api_token\" must declare sensitive = true."
        )
        return False
    insecure_block = re.search(
        r'variable\s+"pve_insecure"\s*\{(?P<body>[^}]*)\}', text
    )
    if not insecure_block or not re.search(
        r"default\s*=\s*false", insecure_block.group("body")
    ):
        print(
            f"FAIL: '{VARIABLES_PATH}' variable "
            f"\"pve_insecure\" must default to false."
        )
        return False
    print(
        f"OK: '{VARIABLES_PATH}' declares all "
        f"{len(REQUIRED_VARIABLES)} required variables "
        f"(pve_api_token sensitive, pve_insecure default false)."
    )
    return True


def test_gitignore_covers_state_and_tfvars():
    text = read_text(GITIGNORE_PATH)
    if text is None:
        print(f"FAIL: '{GITIGNORE_PATH}' is missing.")
        return False
    lines = {line.strip() for line in text.splitlines()}
    missing = [p for p in REQUIRED_GITIGNORE_PATTERNS if p not in lines]
    if missing:
        print(
            f"FAIL: '{GITIGNORE_PATH}' missing required "
            f"patterns: {', '.join(missing)} "
            f"(state and tfvars files must not be committed)."
        )
        return False
    print(
        f"OK: '{GITIGNORE_PATH}' covers all "
        f"{len(REQUIRED_GITIGNORE_PATTERNS)} required patterns."
    )
    return True


def main():
    checks = [
        ("tofu directory exists", test_tofu_dir_exists),
        (
            "versions.tf declares bpg/proxmox provider with version pin",
            test_versions_declares_bpg_provider,
        ),
        (
            "providers.tf wires api_token from var.pve_api_token",
            test_providers_wires_api_token,
        ),
        (
            "variables.tf declares the four required input variables",
            test_variables_declares_required_inputs,
        ),
        (
            ".gitignore covers tfstate and tfvars patterns",
            test_gitignore_covers_state_and_tfvars,
        ),
    ]
    results = [(label, fn()) for label, fn in checks]
    print()
    failed = [label for label, passed in results if not passed]
    if failed:
        print(f"FAILED {len(failed)}/{len(results)} checks:")
        for label in failed:
            print(f"  - {label}")
        sys.exit(1)
    print(f"SUCCESS: All {len(results)} tofu scaffold checks passed.")
    sys.exit(0)


if __name__ == "__main__":
    main()
