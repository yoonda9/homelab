"""Shape tests for the gitlab-runner in-VM egress firewall (gitlab-runner Step 7).

The ruleset is a template, so arms render it through Ansible (the gate Python has
no jinja2). Mutants edit a rendered copy and re-run the same checkers.
"""

import pathlib
import re
import shutil
import subprocess
import sys
import tempfile

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
ROLE = REPO_ROOT / "ansible" / "roles" / "gitlab_runner"
NFT = ROLE / "templates" / "ci-egress.nft.j2"
UNIT = ROLE / "templates" / "ci-egress.service.j2"
DEFAULTS = ROLE / "defaults" / "main.yml"


def _report(ok: bool, msg: str) -> bool:
    print(f"{'OK' if ok else 'FAIL'}: {msg}")
    return ok


def _read(rel: str) -> str:
    p = ROLE / rel
    return p.read_text() if p.is_file() else ""


def _render(template: pathlib.Path, extra: str = "") -> str | None:
    ans = ["mise", "exec", "--", "ansible"] if shutil.which("mise") else ["ansible"]
    with tempfile.TemporaryDirectory() as tmp:
        out = pathlib.Path(tmp) / "out"
        cmd = ans + ["localhost", "-c", "local", "-m", "ansible.builtin.template",
                     "-a", f"src={template} dest={out}", "-e", f"@{DEFAULTS}"]
        if extra:
            cmd += ["-e", extra]
        proc = subprocess.run(cmd, capture_output=True, text=True, cwd=REPO_ROOT, check=False)
        return out.read_text() if proc.returncode == 0 and out.is_file() else None


def _chain(text: str, name: str) -> str:
    m = re.search(r"chain " + name + r"\s*\{(.*?)\n    \}", text, re.S)
    return m.group(1) if m else ""


LAN_DROP = r"^\s*ip daddr 192\.168\.1\.0/24 drop$"
DNS_OK = r"^\s*ip daddr 192\.168\.1\.1 meta l4proto \{ udp, tcp \} th dport 53 accept$"


def check_flush(t: str) -> bool:
    return "flush ruleset" not in t


def check_lan_drop(t: str) -> bool:
    return all(re.search(LAN_DROP, _chain(t, c), re.M) for c in ("output", "forward"))


def check_dns_only(t: str) -> bool:
    for c in ("output", "forward"):
        body = _chain(t, c)
        gw = [ln for ln in body.splitlines() if "192.168.1.1 " in ln]
        if len(gw) != 1 or not re.search(DNS_OK, body, re.M):
            return False
        if body.find("192.168.1.1 ") > body.find("192.168.1.0/24"):
            return False  # the accept must precede the drop
    return True


def check_ipv6(t: str) -> bool:
    return all(re.search(r"^\s*meta nfproto ipv6 drop$", _chain(t, c), re.M) for c in ("output", "forward"))


def check_lo(t: str) -> bool:
    out, inp = _chain(t, "output"), _chain(t, "input")
    first = lambda b: next((ln.strip() for ln in b.splitlines() if ln.strip() and not ln.strip().startswith("type")), "")
    return first(out) == "oif lo accept" and first(inp) == "iif lo accept"


def check_input(t: str) -> bool:
    body = _chain(t, "input")
    return bool(re.search(r"^\s*tcp dport \{ 9100, 9252 \} ip saddr != \{ 192\.168\.1\.111 \} drop$", body, re.M))


def check_header(t: str) -> bool:
    return bool(re.search(r"^table inet ci_egress\ndelete table inet ci_egress\n", t, re.M))


def check_hooks(t: str) -> bool:
    return all(re.search(rf"hook {h} priority 0", _chain(t, h)) for h in ("output", "forward", "input"))


ARMS = {
    "no flush ruleset": check_flush,
    "LAN drop in output and forward": check_lan_drop,
    "only port 53 to the gateway, before the drop": check_dns_only,
    "IPv6 drop in output and forward": check_ipv6,
    "oif lo / iif lo accepted first": check_lo,
    "input admits metrics ports only from .111": check_input,
    "declare-then-delete header": check_header,
    "three base-chain hooks": check_hooks,
}


def test_ruleset_arms() -> bool:
    t = _render(NFT)
    if t is None:
        return _report(False, "ci-egress.nft.j2 renders")
    bad = [k for k, fn in ARMS.items() if not fn(t)]
    return _report(not bad, f"ruleset arms (failed: {bad})")


def test_values_follow_vars() -> bool:
    t = _render(NFT, "gitlab_runner_lan_cidr=10.9.0.0/16 gitlab_runner_lan_gateway=10.9.0.1")
    return _report(t is not None and "10.9.0.0/16 drop" in t and "10.9.0.1 meta" in t,
                   "LAN cidr and gateway come from variables")


def test_unit() -> bool:
    t = _render(UNIT) or ""
    checks = {
        "Type=oneshot": re.search(r"^Type=oneshot$", t, re.M),
        "RemainAfterExit=yes": re.search(r"^RemainAfterExit=yes$", t, re.M),
        "Before=docker.service": re.search(r"^Before=.*\bdocker\.service\b", t, re.M),
        "nft -f ruleset": re.search(r"^ExecStart=/usr/sbin/nft -f /etc/nftables\.d/ci-egress\.nft$", t, re.M),
    }
    bad = [k for k, v in checks.items() if not v]
    return _report(not bad, f"ci-egress.service (failed: {bad})")


def test_tasks() -> bool:
    t, h, main = _read("tasks/firewall.yml"), _read("handlers/main.yml"), _read("tasks/main.yml")
    checks = {
        "/etc/nftables.conf untouched": "/etc/nftables.conf" not in t,
        "ruleset dest": "dest: /etc/nftables.d/ci-egress.nft" in t,
        "ruleset validated by nft -c": "validate: /usr/sbin/nft -c -f %s" in t,
        "unit dest": "dest: /etc/systemd/system/ci-egress.service" in t,
        "enabled and started": "enabled: true" in t and "state: started" in t,
        "IPv6 sysctls": "net.ipv6.conf.all.disable_ipv6" in t and "net.ipv6.conf.default.disable_ipv6" in t,
        "reload handler restarts": bool(re.search(r"- name: Reload ci-egress\n\s+ansible\.builtin\.systemd:\n\s+name: ci-egress\n\s+state: restarted", h)),
        "daemon-reload handler precedes restart": 0 <= h.find("Reload systemd for ci-egress") < h.find("- name: Reload ci-egress"),
        "imported before install": 0 <= main.find("firewall.yml") < main.find("install.yml"),
        "imported before docker": main.find("firewall.yml") < main.find("docker.yml"),
    }
    bad = [k for k, v in checks.items() if not v]
    return _report(not bad, f"firewall.yml shape (failed: {bad})")


def test_mutants() -> bool:
    t = _render(NFT)
    if t is None:
        return _report(False, "mutants: template renders")
    fwd = _chain(t, "forward")
    mutants = {
        "remove forward LAN drop": (check_lan_drop, t.replace(fwd, re.sub(LAN_DROP + "\n?", "", fwd, flags=re.M))),
        "add flush ruleset": (check_flush, "flush ruleset\n" + t),
        "remove ipv6 drop in forward": (check_ipv6, t.replace(fwd, fwd.replace("meta nfproto ipv6 drop", ""))),
        "widen gateway accept to all ports": (check_dns_only, t.replace("th dport 53 accept", "accept")),
        "drop iif lo accept": (check_lo, t.replace("iif lo accept", "")),
        "metrics from anywhere": (check_input, t.replace("saddr != { 192.168.1.111 }", "saddr != { 0.0.0.0/0 }")),
    }
    survived = [k for k, (fn, m) in mutants.items() if m != t and fn(m)]
    unchanged = [k for k, (_, m) in mutants.items() if m == t]
    return _report(not survived and not unchanged, f"mutants killed (survived: {survived}, no-op: {unchanged})")


def main() -> int:
    results = [fn() for name, fn in sorted(globals().items()) if name.startswith("test_") and callable(fn)]
    passed, total = sum(results), len(results)
    print(f"PASS: {passed}/{total}" if passed == total else f"FAIL: {total - passed}/{total} checks failed")
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
