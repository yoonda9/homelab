import os
import sys

import yaml

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
VARS_PATH = os.environ.get(
    "VARS_PATH",
    os.path.join(REPO_ROOT, "ansible", "group_vars", "all.yml"),
)
TEMPLATES_PATH = os.environ.get(
    "TEMPLATES_PATH",
    os.path.join(
        REPO_ROOT, "ansible", "roles", "pve_base", "tasks", "templates.yml"
    ),
)
CICUSTOM_DIR = os.path.join(
    REPO_ROOT, "ansible", "roles", "pve_base", "files", "cicustom"
)
FEDORA_SNIPPET = os.path.join(CICUSTOM_DIR, "fedora-workstation-dev.yaml")
UBUNTU_SNIPPET = os.path.join(CICUSTOM_DIR, "ubuntu-26-dev.yaml")

UPLOAD_TASK_NAME = "Upload Cloud-Init Custom Snippet"
SET_CICUSTOM_TASK_NAME = "Set --cicustom for Cloud Template"
DOWNLOAD_TASK_NAME = "Download Cloud Images"
ATTACH_TASK_NAME = "Attach Disk and Configure Cloud-Init"
CONVERT_TASK_NAME = "Convert VM to Template"


def load_yaml(path):
    if not os.path.exists(path):
        print(f"FAIL: '{path}' is missing.")
        sys.exit(1)
    with open(path, "r") as f:
        return yaml.safe_load(f)


def read_text(path):
    if not os.path.exists(path):
        return None
    with open(path, "r") as f:
        return f.read()


def test_fedora_snippet_content():
    text = read_text(FEDORA_SNIPPET)
    if text is None:
        print(
            f"FAIL: fedora workstation snippet missing at "
            f"{FEDORA_SNIPPET}."
        )
        return False
    if not text.lstrip().startswith("#cloud-config"):
        print(
            f"FAIL: fedora snippet '{FEDORA_SNIPPET}' must start with "
            f"'#cloud-config' header (cloud-init user-data convention)."
        )
        return False
    if "@workstation-product-environment" not in text:
        print(
            f"FAIL: fedora snippet '{FEDORA_SNIPPET}' missing the literal "
            f"'@workstation-product-environment' token in runcmd "
            f"(required to install the Fedora Workstation product env)."
        )
        return False
    lower = text.lower()
    if "dnf" not in lower or "install" not in lower:
        print(
            f"FAIL: fedora snippet '{FEDORA_SNIPPET}' must invoke "
            f"'dnf ... install' for dev-tool baseline."
        )
        return False
    missing = [
        pkg for pkg in ("git", "vim", "nodejs") if pkg not in text
    ]
    if missing:
        print(
            f"FAIL: fedora snippet '{FEDORA_SNIPPET}' missing dev "
            f"package(s) in dnf install: {missing}."
        )
        return False
    print(
        "OK: fedora-workstation-dev.yaml present, starts with "
        "#cloud-config, runcmd installs @workstation-product-environment "
        "and git+vim+nodejs via dnf."
    )
    return True


def test_ubuntu_snippet_content():
    text = read_text(UBUNTU_SNIPPET)
    if text is None:
        print(
            f"FAIL: ubuntu-26 dev snippet missing at {UBUNTU_SNIPPET}."
        )
        return False
    if not text.lstrip().startswith("#cloud-config"):
        print(
            f"FAIL: ubuntu snippet '{UBUNTU_SNIPPET}' must start with "
            f"'#cloud-config' header."
        )
        return False
    try:
        loaded = yaml.safe_load(text)
    except yaml.YAMLError as exc:
        print(
            f"FAIL: ubuntu snippet '{UBUNTU_SNIPPET}' is not valid YAML: "
            f"{exc}."
        )
        return False
    if not isinstance(loaded, dict):
        print(
            f"FAIL: ubuntu snippet '{UBUNTU_SNIPPET}' must parse to a "
            f"YAML mapping (got {type(loaded).__name__})."
        )
        return False
    if loaded.get("package_update") is not True:
        print(
            f"FAIL: ubuntu snippet '{UBUNTU_SNIPPET}' must set "
            f"'package_update: true'."
        )
        return False
    packages = loaded.get("packages")
    if not isinstance(packages, list):
        print(
            f"FAIL: ubuntu snippet '{UBUNTU_SNIPPET}' must define a "
            f"'packages:' list."
        )
        return False
    required = {"git", "build-essential", "docker.io", "python3-pip"}
    pkg_set = {str(p) for p in packages}
    missing = sorted(required - pkg_set)
    if missing:
        print(
            f"FAIL: ubuntu snippet '{UBUNTU_SNIPPET}' packages list "
            f"missing required dev package(s): {missing}."
        )
        return False
    print(
        "OK: ubuntu-26-dev.yaml present, starts with #cloud-config, "
        "package_update: true, packages list contains git, "
        "build-essential, docker.io, python3-pip."
    )
    return True


def test_cicustom_field_on_target_entries(variables):
    images = variables.get("pve_cloud_images") or []
    expected = {
        "ubuntu-26.04-cloud": "ubuntu-26-dev.yaml",
        "fedora-cloud-base": "fedora-workstation-dev.yaml",
    }
    found = {}
    for img in images:
        if not isinstance(img, dict):
            continue
        name = str(img.get("name", ""))
        if name in expected:
            found[name] = img.get("cicustom")
    failures = []
    for name, want in expected.items():
        if name not in found:
            failures.append(
                f"missing pve_cloud_images entry '{name}'"
            )
            continue
        got = found[name]
        if got != want:
            failures.append(
                f"entry '{name}' has cicustom={got!r}, expected {want!r}"
            )
    if failures:
        print(
            "FAIL: cicustom field on pve_cloud_images entries — "
            + "; ".join(failures)
            + "."
        )
        return False
    print(
        "OK: ubuntu-26.04-cloud cicustom='ubuntu-26-dev.yaml' AND "
        "fedora-cloud-base cicustom='fedora-workstation-dev.yaml'."
    )
    return True


def _code_line_indices(text, needle):
    """Return 0-based line indices where needle appears in non-comment lines.

    Skips lines whose lstripped content starts with '#' so a YAML comment
    cannot satisfy an ordering check (mem-1777478162-68e8).
    """
    indices = []
    for idx, raw in enumerate(text.splitlines()):
        if raw.lstrip().startswith("#"):
            continue
        if needle in raw:
            indices.append(idx)
    return indices


def test_templates_ordering():
    text = read_text(TEMPLATES_PATH)
    if text is None:
        print(f"FAIL: templates.yml missing at {TEMPLATES_PATH}.")
        return False

    def first(needle):
        hits = _code_line_indices(text, f"name: {needle}")
        return hits[0] if hits else None

    upload_idx = first(UPLOAD_TASK_NAME)
    set_idx = first(SET_CICUSTOM_TASK_NAME)
    download_idx = first(DOWNLOAD_TASK_NAME)
    attach_idx = first(ATTACH_TASK_NAME)
    convert_idx = first(CONVERT_TASK_NAME)

    missing = [
        label
        for label, idx in (
            (UPLOAD_TASK_NAME, upload_idx),
            (SET_CICUSTOM_TASK_NAME, set_idx),
            (DOWNLOAD_TASK_NAME, download_idx),
            (ATTACH_TASK_NAME, attach_idx),
            (CONVERT_TASK_NAME, convert_idx),
        )
        if idx is None
    ]
    if missing:
        print(
            f"FAIL: templates.yml missing required task name(s) "
            f"(comment-only matches ignored): {missing}."
        )
        return False

    failures = []
    if not (download_idx < upload_idx < convert_idx):
        failures.append(
            f"ordering violation: '{UPLOAD_TASK_NAME}' must sit between "
            f"'{DOWNLOAD_TASK_NAME}' (line {download_idx + 1}) and "
            f"'{CONVERT_TASK_NAME}' (line {convert_idx + 1}); "
            f"got upload at line {upload_idx + 1}"
        )
    if not (attach_idx < set_idx < convert_idx):
        failures.append(
            f"ordering violation: '{SET_CICUSTOM_TASK_NAME}' must sit "
            f"between '{ATTACH_TASK_NAME}' (line {attach_idx + 1}) and "
            f"'{CONVERT_TASK_NAME}' (line {convert_idx + 1}); "
            f"got set at line {set_idx + 1}"
        )
    if failures:
        print("FAIL: templates.yml task ordering — " + "; ".join(failures) + ".")
        return False
    print(
        f"OK: templates.yml ordering — Upload (line {upload_idx + 1}) "
        f"between Download (line {download_idx + 1}) and Convert "
        f"(line {convert_idx + 1}); Set --cicustom (line {set_idx + 1}) "
        f"between Attach (line {attach_idx + 1}) and Convert."
    )
    return True


def test_new_tasks_gated_on_cicustom():
    tasks = load_yaml(TEMPLATES_PATH)
    if not isinstance(tasks, list):
        print(
            f"FAIL: templates.yml did not parse to a task list "
            f"(got {type(tasks).__name__})."
        )
        return False
    targets = {UPLOAD_TASK_NAME, SET_CICUSTOM_TASK_NAME}
    found = {}
    for task in tasks:
        if not isinstance(task, dict):
            continue
        name = str(task.get("name", ""))
        if name in targets:
            found[name] = task
    missing = sorted(targets - set(found))
    if missing:
        print(
            f"FAIL: templates.yml missing task(s) by name: {missing}."
        )
        return False
    failures = []
    for name in targets:
        when_clause = str(found[name].get("when", ""))
        if "item.cicustom is defined" not in when_clause:
            failures.append(
                f"task '{name}' missing 'when: item.cicustom is defined' "
                f"(got when={when_clause!r})"
            )
    if failures:
        print("FAIL: cicustom gating — " + "; ".join(failures) + ".")
        return False
    print(
        f"OK: both new tasks ('{UPLOAD_TASK_NAME}' and "
        f"'{SET_CICUSTOM_TASK_NAME}') are gated by "
        f"'item.cicustom is defined'."
    )
    return True


def main():
    variables = load_yaml(VARS_PATH)

    checks = [
        ("fedora-workstation-dev.yaml content", test_fedora_snippet_content),
        ("ubuntu-26-dev.yaml content", test_ubuntu_snippet_content),
        (
            "cicustom field on ubuntu-26.04-cloud + fedora-cloud-base",
            lambda: test_cicustom_field_on_target_entries(variables),
        ),
        (
            "templates.yml task ordering (Upload + Set --cicustom)",
            test_templates_ordering,
        ),
        (
            "new tasks gated by 'item.cicustom is defined'",
            test_new_tasks_gated_on_cicustom,
        ),
    ]

    results = []
    for label, check_fn in checks:
        passed = check_fn()
        results.append((label, passed))

    print()
    failed = [label for label, passed in results if not passed]
    if failed:
        print(f"FAILED {len(failed)}/{len(results)} checks:")
        for label in failed:
            print(f"  - {label}")
        sys.exit(1)
    print(f"SUCCESS: All {len(results)} cicustom snippet checks passed.")
    sys.exit(0)


if __name__ == "__main__":
    main()
