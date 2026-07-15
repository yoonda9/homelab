#!/bin/bash
# R12/R13 probe — Inquisitor, design.rejected (2026-07-15).
# Verifies the Design Critic's two findings first-hand, and establishes the fact
# that decides R12: the :111 gate ALREADY handles the absent dir deliberately.
#
# Run:  ansible-playbook logs/r12-absent-semantics-probe.sh.yml   (see heredoc below)
#       ./logs/r12-absent-semantics-probe.sh   -> writes r12-absent-semantics-probe.log
#
# Pinned toolchain: ansible-core 2.21.1 (the version this repo actually resolves).
set -u

WORK=$(mktemp -d)
trap 'rm -rf "$WORK"' EXIT
ABSENT="$WORK/definitely-absent"   # never created — that is the point

echo "=== ansible version (must be the pinned one) ==="
ansible --version | head -1

# ---------------------------------------------------------------------------
# PROBE 1 — the CONCERN: the design's stated absent-tolerant definition errors.
# design 4.2:260 requires the stat to "Tolerate absence"; the stated definition
# (dir uid != plex_uid or dir gid != plex_gid) cannot be evaluated when absent.
# ---------------------------------------------------------------------------
cat > "$WORK/p1.yml" <<EOF
- hosts: localhost
  gather_facts: false
  vars: {plex_uid: 64000, plex_gid: 64000}
  tasks:
    - ansible.builtin.stat: {path: $ABSENT}
      register: s
    - ansible.builtin.debug:
        msg: "exists={{ s.stat.exists }} · keys present={{ s.stat.keys() | list }}"
    - name: "the design's STATED definition, verbatim"
      ansible.builtin.debug:
        msg: "chown_needed={{ s.stat.uid != plex_uid or s.stat.gid != plex_gid }}"
      ignore_errors: true
EOF
echo; echo "=== PROBE 1 — stated definition vs an absent dir (expect: hard error) ==="
ansible-playbook "$WORK/p1.yml" 2>&1 | grep -E "exists=|has no attribute|fatal|PLAY RECAP" -A1 | head -12

# ---------------------------------------------------------------------------
# PROBE 2 — the fact that decides R12: the REAL gate (:111) tolerates absence.
# assert's `that:` evaluates in order and STOPS at the first false condition, so
# `stat.exists` short-circuits before `.uid` is ever touched — and the fail_msg's
# `| default('missing')` renders. The absent case was authored on purpose.
# ---------------------------------------------------------------------------
cat > "$WORK/p2.yml" <<EOF
- hosts: localhost
  gather_facts: false
  vars:
    plex_uid: 64000
    plex_gid: 64000
    plex_service_user: plex
    plex_state_dir: $ABSENT
  tasks:
    - ansible.builtin.stat: {path: "{{ plex_state_dir }}"}
      register: plex_state_stat
    - name: "the REAL gate assert (roles/plex/tasks/main.yml:111), shape verbatim"
      ansible.builtin.assert:
        that:
          - plex_state_stat.stat.exists
          - plex_state_stat.stat.isdir
          - plex_state_stat.stat.uid | int == plex_uid | int
          - plex_state_stat.stat.gid | int == plex_gid | int
        fail_msg: >-
          {{ plex_state_dir }} must be owned by {{ plex_service_user }}
          ({{ plex_uid }}:{{ plex_gid }}) but reports
          {{ plex_state_stat.stat.uid | default('missing') }}:{{ plex_state_stat.stat.gid | default('missing') }}.
      ignore_errors: true
EOF
echo; echo "=== PROBE 2 — the real :111 gate vs an absent dir (expect: clean, missing:missing) ==="
ansible-playbook "$WORK/p2.yml" 2>&1 | grep -E "assertion|evaluated_to|msg\"|PLAY RECAP" -A1 | head -12

# ---------------------------------------------------------------------------
# PROBE 3 — R12 is satisfiable: Jinja `and` short-circuits past the missing attr.
# Feasibility only. NOT a prescription — the derivation site is the Architect's call.
# ---------------------------------------------------------------------------
cat > "$WORK/p3.yml" <<EOF
- hosts: localhost
  gather_facts: false
  vars: {plex_uid: 64000, plex_gid: 64000}
  tasks:
    - ansible.builtin.stat: {path: $ABSENT}
      register: s
    - name: "exists-guarded form vs an absent dir"
      ansible.builtin.set_fact:
        chown_needed: "{{ s.stat.exists and (s.stat.uid | int != plex_uid | int or s.stat.gid | int != plex_gid | int) }}"
      ignore_errors: true
    - ansible.builtin.debug: {msg: "chown_needed={{ chown_needed | default('<ERRORED>') }}"}
    - name: "the WRONG-ANSWER ATTRACTOR the design must warn against"
      ansible.builtin.set_fact:
        chown_needed_bad: "{{ s.stat.uid | default(0) | int != plex_uid | int }}"
    - ansible.builtin.debug:
        msg: "| default(0) yields chown_needed={{ chown_needed_bad }} -> chown -R fires on a NONEXISTENT path, shadowing :111"
EOF
echo; echo "=== PROBE 3 — R12 satisfiable? + the |default(0) attractor ==="
ansible-playbook "$WORK/p3.yml" 2>&1 | grep -E "chown_needed=|default\(0\) yields|PLAY RECAP" | head -8

# ---------------------------------------------------------------------------
# PROBE 4 — the FAIL: the Provenance guard is vacuous by construction.
# design 7.1 / plan.md:143: "the chown's when: MUST NOT name the getent register".
# Under 4.2/6.3's OWN requirement that chown_needed be a named fact reused by two
# tasks, the chown's when: is a bare name in BOTH designs -> the guard cannot fail.
# ---------------------------------------------------------------------------
cat > "$WORK/accepted.yml" <<'EOF'
- name: Derive the migration predicate
  ansible.builtin.set_fact:
    chown_needed: "{{ early.stat.uid | int != plex_uid | int or early.stat.gid | int != plex_gid | int }}"
- name: Migrate state dir ownership to the pinned ids
  ansible.builtin.command: chown -R {{ plex_uid }}:{{ plex_gid }} {{ plex_state_dir }}
  when: chown_needed
EOF
cat > "$WORK/rejected.yml" <<'EOF'
- name: Derive the migration predicate
  ansible.builtin.set_fact:
    chown_needed: "{{ ansible_facts.getent_passwd['plex'][1] | int != plex_uid | int }}"
- name: Migrate state dir ownership to the pinned ids
  ansible.builtin.command: chown -R {{ plex_uid }}:{{ plex_gid }} {{ plex_state_dir }}
  when: chown_needed
EOF
cat > "$WORK/guard.py" <<'EOF'
import yaml
# The Provenance guard EXACTLY as design 7.1 / plan.md:143 words it.
def provenance_guard(path):
    tasks = yaml.safe_load(open(path))
    chown = next(t for t in tasks if 'chown' in str(t.get('ansible.builtin.command', '')))
    when = str(chown.get('when', ''))
    return ('getent' not in when), when
for label, f in (('accepted (dir, both halves)', 'accepted.yml'),
                 ('REJECTED (getent-keyed, wedges)', 'rejected.yml')):
    ok, when = provenance_guard(f)
    print(f"  {label:34} chown when: {when!r:16} guard -> {'PASS' if ok else 'FAIL'}")
print("\n  Both PASS. The guard cannot fail: a bare name carries no provenance.")
EOF
echo; echo "=== PROBE 4 — Provenance guard vs both designs (expect: PASS/PASS = vacuous) ==="
PY=$(head -1 "$(command -v ansible-playbook)" | sed 's|^#!||')   # ansible's interpreter has PyYAML
(cd "$WORK" && "$PY" guard.py)

echo; echo "=== CONCLUSIONS ==="
echo "  1. CONCERN real  — stated definition hard-errors on absent."
echo "  2. FAIL real     — provenance guard PASSES for the rejected design."
echo "  3. R12 is NOT a new policy — :111 already handles absent deliberately"
echo "     (exists asserted first + | default('missing')). Preserve it."
echo "  4. R12 is satisfiable; the mechanism remains the Architect's call."
