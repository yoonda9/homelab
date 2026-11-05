"""Shape tests for docs/runbooks/gitlab-runner.md (gitlab-runner Step 2e).

Pins the section headings and the filled-in bodies (create the VM, register,
add a project, rotate, security, hygiene, compromise, firewall, ...). Later steps
extend REQUIRED_HEADINGS as they fill sections in. Stdlib only.
"""

import pathlib
import re
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
RUNBOOK = REPO_ROOT / "docs" / "runbooks" / "gitlab-runner.md"

REQUIRED_HEADINGS = (
    "Create the VM",
    "Register a runner",
    "Add a project",
    "Rotate a token",
    "Upgrade",
    "Clean disk",
    "Troubleshooting",
    "Security model",
    "GitLab-side hygiene",
    "Compromise playbook",
    "Routine re-image",
    "Firewall",
    "Hairpin",
    "Known limits",
)


def _body() -> str:
    return RUNBOOK.read_text() if RUNBOOK.is_file() else ""


def _section(body: str, title: str) -> str:
    m = re.search(rf"^## {re.escape(title)}\s*$(.*?)(?=^## |\Z)", body, re.M | re.S)
    return m.group(1) if m else ""


def _report(ok: bool, msg: str) -> bool:
    print(f"{'OK' if ok else 'FAIL'}: {msg}")
    return ok


def test_headings() -> bool:
    body = _body()
    missing = [h for h in REQUIRED_HEADINGS if not re.search(rf"^## {re.escape(h)}\s*$", body, re.M)]
    return _report(not missing, f"runbook has every required section heading (missing: {missing})")


def test_toc_lists_sections() -> bool:
    toc = _section(_body(), "Table of contents")
    missing = [h for h in REQUIRED_HEADINGS if f"[{h}]" not in toc]
    return _report(not missing, f"table of contents links every required section (missing: {missing})")


def test_create_vm_body() -> bool:
    s = _section(_body(), "Create the VM")
    checks = {
        "pvesm status": "pvesm status" in s,
        "150 GB on local-lvm": re.search(r"150\s*GB", s) is not None and "local-lvm" in s,
        ".120 free / outside DHCP": "192.168.1.120" in s and "DHCP" in s,
        "just plan": "just plan" in s,
        "just apply": "just apply" in s,
        "qm guest exec": "qm guest exec" in s,
    }
    bad = [k for k, v in checks.items() if not v]
    return _report(not bad, f"create-the-VM section is filled in (missing: {bad})")


def test_security_model_body() -> bool:
    s = _section(_body(), "Security model")
    checks = {
        "Developer-or-above = root claim": re.search(r"Developer", s) and re.search(r"root\s+on\s+the\s+runner\s+VM", s),
        "all its tokens": re.search(r"all\s+its\s+tokens", s) is not None,
        "trusted projects only": re.search(r"only\s+trusted\s+projects", s, re.I) is not None,
    }
    bad = [k for k, v in checks.items() if not v]
    return _report(not bad, f"security-model section states the trust boundary (missing: {bad})")


def test_hygiene_body() -> bool:
    s = _section(_body(), "GitLab-side hygiene")
    checks = {
        "runner locked to project": re.search(r"locked to (its|the) project", s) is not None,
        "fork pipelines off": re.search(r"fork pipelines", s, re.I) is not None and re.search(r"\boff\b", s) is not None,
        "max timeout 5400-5700 s": re.search(r"5400\s*[-–]\s*5700\s*s", s) is not None,
        "job-token allowlist default": "allowlist" in s and re.search(r"default", s) is not None,
    }
    bad = [k for k, v in checks.items() if not v]
    return _report(not bad, f"GitLab-side hygiene section lists the four settings (missing: {bad})")


def test_known_limits_body() -> bool:
    s = _section(_body(), "Known limits")
    checks = {
        "no Alertmanager": "Alertmanager" in s,
        "split manager follow-up": re.search(r"split manager", s, re.I) is not None,
        "sysbox follow-up": re.search(r"sysbox", s, re.I) is not None,
    }
    bad = [k for k, v in checks.items() if not v]
    return _report(not bad, f"known-limits section names the three limits (missing: {bad})")


def test_hairpin_body() -> bool:
    s = _section(_body(), "Hairpin")
    checks = {
        "WAN IP": "WAN IP" in s,
        "whoami probe": "whoami" in s and "curl" in s,
        "source IP echoed": "RemoteAddr" in s or "X-Real-Ip" in s,
        "internal-allowlist": "internal-allowlist" in s,
        "router admin ports": re.search(r"admin\s+ports", s) is not None,
        "evidence or acceptance": re.search(r"evidence", s, re.I) is not None
        and re.search(r"accept", s, re.I) is not None,
    }
    bad = [k for k, v in checks.items() if not v]
    return _report(not bad, f"hairpin section states the probe and the outcomes (missing: {bad})")


def test_compromise_body() -> bool:
    s = _section(_body(), "Compromise playbook")
    checks = {
        "pause the runner": re.search(r"pause\s+the\s+runner", s, re.I) is not None,
        "re-image": re.search(r"re-image", s, re.I) is not None,
        "runner-reimage named": "just runner-reimage" in s,
        # Polarity flip (Step 12f): the recipe landed in Step 10d, so the
        # section must no longer call it planned/missing, nor send the operator
        # to a by-hand replace, and the recipe it names must exist.
        "runner-reimage not called planned or missing": re.search(r"planned|does\s+not\s+exist", s, re.I) is None,
        "no by-hand tofu apply -replace": re.search(r"tofu\s+apply\s+-replace|by\s+hand", s, re.I) is None,
        "runner-reimage recipe exists in justfile": re.search(
            r"^runner-reimage\s+NAME\s*:", (REPO_ROOT / "justfile").read_text(), re.M
        )
        is not None
        if (REPO_ROOT / "justfile").is_file()
        else False,
        "delete and recreate / ID reset": re.search(r"delete\s+and\s+recreate", s, re.I) is not None
        and re.search(r"\bID\b", s) is not None,
        "rotate CI variables": re.search(r"rotate", s, re.I) is not None and "CI variables" in s,
    }
    bad = [k for k, v in checks.items() if not v]
    return _report(not bad, f"compromise-playbook section lists the four steps (missing: {bad})")


def test_reimage_body() -> bool:
    s = _section(_body(), "Routine re-image")
    checks = {
        "monthly": re.search(r"monthly", s, re.I) is not None,
        "on upgrades": re.search(r"upgrade", s, re.I) is not None,
        "SSH host key changes": re.search(r"host\s+key", s, re.I) is not None and re.search(r"chang", s) is not None,
    }
    bad = [k for k, v in checks.items() if not v]
    return _report(not bad, f"routine-re-image section states cadence and host-key change (missing: {bad})")


def test_firewall_body() -> bool:
    s = _section(_body(), "Firewall")
    checks = {
        "stage 1 then stage 2": "gitlab_runner_firewall_stage" in s
        and re.search(r"stage\s*=\s*1", s) is not None
        and re.search(r"stage\s*=\s*2", s) is not None,
        "root SSH session held open": re.search(r"root\s+SSH\s+session", s) is not None,
        "rollback pve-firewall stop": "pve-firewall stop" in s,
        "pre-flight bridge-nf sysctl": "net.bridge.bridge-nf-call-iptables" in s,
        "conntrack count": "conntrack -C" in s,
        "Plex latency baseline": re.search(r"Plex latency", s) is not None and "baseline" in s,
        "0 to change/destroy on the VM": re.search(r"0 to change", s) is not None,
        "verification: 9252 from CT 111": ":9252" in s and "CT 111" in s,
        "nft flush negative control": "nft flush ruleset" in s,
        "restore after flush": "systemctl restart ci-egress docker gitlab-runner" in s,
        "runner-reimage re-checks before unpause": "just runner-reimage" in s
        and "pve-firewall status" in s
        and re.search(r"unpause", s, re.I) is not None,
    }
    bad = [k for k, v in checks.items() if not v]
    return _report(not bad, f"firewall section states sequence, rollback, verification, re-image (missing: {bad})")


def test_register_body() -> bool:
    s = _section(_body(), "Register a runner")
    checks = {
        "project runner in the GitLab UI": re.search(r"project runner", s, re.I) is not None and "GitLab UI" in s,
        "untagged on": re.search(r"untagged", s, re.I) is not None,
        "locked": re.search(r"\blocked\b", s, re.I) is not None,
        "protected off": re.search(r"protected", s, re.I) is not None,
        "max timeout SET 5400-5700 s": re.search(r"5400\s*[-–]\s*5700\s*s", s) is not None
        and re.search(r"\bset\b", s, re.I) is not None,
        "description = runner name": re.search(r"description", s, re.I) is not None,
        "runner id recorded": re.search(r"runner\s+id", s, re.I) is not None,
        "ansible-vault edit": "ansible-vault edit" in s,
        "vault_gitlab_runner_tokens.<name>": "vault_gitlab_runner_tokens" in s,
        "vars entry in gitlab_runner_runners": "gitlab_runner_runners" in s
        and "group_vars/gitlab_runner/vars.yml" in s,
        "same commit": re.search(r"same\s+commit", s, re.I) is not None,
        "just play-runner": "just play-runner" in s,
        "token never in chat": re.search(r"never\s+(paste|enter)", s, re.I) is not None
        and re.search(r"chat|transcript", s, re.I) is not None,
        "drain timeout invariant": re.search(r"drain\s+timeout", s, re.I) is not None,
    }
    bad = [k for k, v in checks.items() if not v]
    return _report(not bad, f"register section states attributes, vault, vars, play (missing: {bad})")


def test_add_project_body() -> bool:
    s = _section(_body(), "Add a project")
    checks = {
        "path 1: new project runner": re.search(r"new project runner", s, re.I) is not None,
        "path 1: vars entry": "gitlab_runner_runners" in s,
        "path 1: vault key": "vault_gitlab_runner_tokens" in s,
        "path 1: play": "just play-runner" in s,
        "path 2: enable existing runner in UI": re.search(r"enable\s+(the|an)\s+existing", s, re.I) is not None
        and "GitLab UI" in s,
        "path 2: no repo change": re.search(r"no\s+repo\s+change", s, re.I) is not None,
        "both paths named": re.search(r"two\s+paths|either", s, re.I) is not None,
    }
    bad = [k for k, v in checks.items() if not v]
    return _report(not bad, f"add-a-project section gives both paths (missing: {bad})")


def test_rotate_body() -> bool:
    s = _section(_body(), "Rotate a token")
    checks = {
        "ID-based reset endpoint": "/runners/:id/reset_authentication_token" in s,
        "UI Reset token alternative": re.search(r"Reset token", s) is not None,
        "token-based reset forbidden (literal path absent)": re.search(r"/runners/reset_authentication_token", s) is None,
        "token-based reset named as never": re.search(r"never[^.]*token-based", s, re.I) is not None,
        "new token into vault": "ansible-vault edit" in s,
        "play": "just play-runner" in s,
        "runner id unchanged": re.search(r"runner\s+id[^.]*unchanged|unchanged[^.]*runner\s+id", s, re.I) is not None,
        "401 from verify means rotate": "401" in s and "gitlab-runner verify" in s and re.search(r"rotate", s, re.I) is not None,
        "old cache volumes orphaned, prune reclaims": re.search(r"orphan", s, re.I) is not None
        and "cache" in s
        and re.search(r"prune", s, re.I) is not None,
    }
    bad = [k for k, v in checks.items() if not v]
    return _report(not bad, f"rotate section uses the ID-based reset and states the effects (missing: {bad})")


def test_troubleshooting_body() -> bool:
    s = _section(_body(), "Troubleshooting")
    checks = {
        "journalctl": "journalctl -u gitlab-runner" in s,
        "verify": "gitlab-runner verify" in s,
        "401 means rotate": "401" in s and re.search(r"rotate", s, re.I) is not None,
        "offline runner": re.search(r"offline", s, re.I) is not None,
        "pending jobs": re.search(r"pending", s, re.I) is not None,
        "drain wait, no kill -9": re.search(r"drain", s, re.I) is not None and "kill -9" in s,
        "pre-render assert names missing vault key": re.search(r"pre-render\s+assert", s, re.I) is not None
        and "vault_gitlab_runner_tokens" in s,
        "never paste token": re.search(r"never\s+paste", s, re.I) is not None,
    }
    bad = [k for k, v in checks.items() if not v]
    return _report(not bad, f"troubleshooting section covers offline, stuck, 401, assert (missing: {bad})")


def test_runner_vars_file() -> bool:
    f = REPO_ROOT / "ansible" / "group_vars" / "gitlab_runner" / "vars.yml"
    txt = f.read_text() if f.is_file() else ""
    live = [l for l in txt.splitlines() if l.strip() and not l.lstrip().startswith("#")]
    checks = {
        "file exists": bool(txt),
        "list is [] until the token step": "gitlab_runner_runners: []" in live,
        "lumologic-pve entry prepared": "name: lumologic-pve" in txt and "project: lumologic/lumologic" in txt,
        "no token value": re.search(r"glrt-|token\s*:", txt) is None,
    }
    bad = [k for k, v in checks.items() if not v]
    return _report(not bad, f"runner vars file carries the prepared entry, no secret (missing: {bad})")


def test_heading_order_and_uniqueness() -> bool:
    body = _body()
    found = re.findall(r"^## (.+?)\s*$", body, re.M)
    body_headings = [h for h in found if h != "Table of contents"]
    toc = _section(body, "Table of contents")
    toc_order = re.findall(r"^- \[(.+?)\]\(#", toc, re.M)
    checks = {
        "no duplicate headings": len(found) == len(set(found)),
        "headings in REQUIRED order": body_headings == list(REQUIRED_HEADINGS),
        "TOC in REQUIRED order": toc_order == list(REQUIRED_HEADINGS),
    }
    bad = [k for k, v in checks.items() if not v]
    return _report(not bad, f"headings are unique and ordered like the TOC (failing: {bad})")


def test_no_empty_sections() -> bool:
    body = _body()
    empty = [h for h in REQUIRED_HEADINGS if len(_section(body, h).strip()) < 10]
    return _report(not empty, f"every required section has a body, filled or marked not yet written (empty: {empty})")


def main() -> int:
    results = [
        test_headings(),
        test_heading_order_and_uniqueness(),
        test_no_empty_sections(),
        test_toc_lists_sections(),
        test_create_vm_body(),
        test_register_body(),
        test_add_project_body(),
        test_rotate_body(),
        test_troubleshooting_body(),
        test_runner_vars_file(),
        test_security_model_body(),
        test_hygiene_body(),
        test_compromise_body(),
        test_reimage_body(),
        test_firewall_body(),
        test_hairpin_body(),
        test_known_limits_body(),
    ]
    total, passed = len(results), sum(results)
    if passed == total:
        print(f"PASS: {passed}/{total}")
        return 0
    print(f"FAIL: {total - passed}/{total} checks failed")
    return 1


if __name__ == "__main__":
    sys.exit(main())
