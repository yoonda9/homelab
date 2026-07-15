#!/bin/bash
# Q9 follow-up probe — Inquisitor, on answer.proposed (accepting (A)).
#
# The (A) guarantee rests on ONE invariant (idea-honing.md "completion-flag invariant"):
#
#   "The top-level dir reads plex_uid:plex_gid IFF the chown -R ran to completion."
#
# The Architect proved it by strace against GNU `chown -R` (post-order, top-level
# chowned LAST: call 12,154 of 12,154). That proof is sound — but it is a proof about
# GNU coreutils, NOT about "recursively chowning a tree" in general.
#
# plan.md:70-73 currently records the module choice as a PERFORMANCE preference:
#   "Prefer `command:` over `ansible.builtin.file` with `recurse: yes` — the latter
#    stats every one of 12,043 files and is markedly slower FOR THE SAME RESULT."
#
# This probe tests whether "the same result" is true under (A). It is not.
#
# Run under `podman unshare` (gives a subuid-mapped root, so chown works locally).
set -u

DIR=/tmp/fileprobe/tree
OLD=0; NEW=1   # ids are arbitrary: this probe measures TRAVERSAL ORDER, not values.

rm -rf /tmp/fileprobe; mkdir -p "$DIR/Library/sub"
for i in $(seq 1 120); do
  mkdir -p "$DIR/Library/sub/d$i"; touch "$DIR/Library/sub/d$i"/f{1..80}
done
TOTAL=$(find "$DIR" | wc -l)
echo "tree built: $TOTAL entries (comparable to the live 12,043)"

top()  { stat -c '%u:%g' "$DIR"; }
oldn() { find "$DIR" -uid $OLD | wc -l; }

# The predicate the Architect's answer settled on: dir, BOTH halves.
predicate() {
  local du dg
  du=$(stat -c %u "$DIR"); dg=$(stat -c %g "$DIR")
  if [ "$du" != "$NEW" ] || [ "$dg" != "$NEW" ]; then echo TRUE; else echo FALSE; fi
}

echo
echo "=================================================================="
echo "PROBE A — command: chown -R   (what the design specifies, :242-244)"
echo "=================================================================="
# GNU chown -R does 9,723 entries in ~11ms, so a sleep-then-kill race cannot catch
# it — an uninterrupted run converges and reports FALSE for the RIGHT reason, which
# would silently look like the wedge we are testing for. Interrupt deterministically
# with a sub-ms timeout, and interrupt at FIVE different depths to show the result
# is a property of the traversal order, not of where the kill happened to land.
for T in 0.001 0.002 0.003 0.004 0.006; do
  chown -R $OLD:$OLD "$DIR"
  timeout -s KILL ${T}s chown -R $NEW:$NEW "$DIR" 2>/dev/null
  LEFT=$(oldn)
  if [ "$LEFT" = "0" ]; then echo "  timeout=${T}s -> ran to completion, not a valid interrupt; skipping"; continue; fi
  echo "  timeout=${T}s | top-level=$(top) | un-chowned=$LEFT of $TOTAL | predicate: $(predicate)"
done
echo "  ^ top-level NEVER pre-chowned => predicate TRUE at every interrupt => a re-run RECOVERS"

echo
echo "=================================================================="
echo "PROBE B — ansible.builtin.file recurse=yes  (the 'same result' swap)"
echo "=================================================================="
chown -R $OLD:$OLD "$DIR"
setsid /home/user/.local/share/chezmoi/.bootstrap.venv/bin/ansible localhost -c local \
  -m file -a "path=$DIR owner=$NEW group=$NEW recurse=yes state=directory" \
  >/tmp/fileprobe/ansible.out 2>&1 & APID=$!
sleep 0.5
kill -9 -$APID 2>/dev/null; kill -9 $APID 2>/dev/null; sleep 0.2
echo "  top-level dir                : $(top)"
echo "  entries still un-chowned     : $(oldn) of $TOTAL"
echo "  chown predicate (both halves): $(predicate)   <-- FALSE => a re-run SKIPS. WEDGED."

echo
echo "=================================================================="
echo "WHY — ansible/modules/file.py, ensure_directory()"
echo "=================================================================="
cat <<'EOF'
  :683   changed = module.set_fs_attributes_if_different(file_args, ...)  <-- TOP-LEVEL FIRST
  :686   if recurse: changed |= recursive_set_attributes(b_path, ...)     <-- children AFTER
  :335   for b_root, b_dirs, b_files in os.walk(b_path):                  <-- topdown=True (default)

  GNU chown -R  : post-order -> top-level LAST  -> top-level correct IFF complete.  (A) holds.
  file recurse= : pre-order  -> top-level FIRST -> top-level correct while incomplete. (A) BREAKS.

  The two modules are NOT "the same result" under (A). The module choice is
  load-bearing for the recovery guarantee, not a performance preference.
EOF
echo
echo "PROBE COMPLETE"
