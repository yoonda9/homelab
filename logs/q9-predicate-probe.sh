#!/bin/bash
# Q9 probe — does a dir-ownership predicate re-fire correctly on a half-migrated tree?
# Replicates the role's real sequence (ansible/roles/plex/tasks/main.yml:90-117).
# Run as root in debian:bookworm (same image the Design Critic used).
set -u

DIR=/var/lib/plexmediaserver
OLD_UID=999; OLD_GID=991
NEW_UID=64000; NEW_GID=64000

apt-get -qq update >/dev/null 2>&1
apt-get -qq install -y strace >/dev/null 2>&1
echo "strace: $(which strace || echo MISSING)"

groupadd -g $OLD_GID plex
useradd -u $OLD_UID -g $OLD_GID -M -d "$DIR" -s /usr/sbin/nologin plex
getent passwd plex

# Build a tree comparable to the live one (12,043 files / real layout).
mkdir -p "$DIR/Library/Application Support/Plex Media Server"
for i in $(seq 1 150); do
  mkdir -p "$DIR/Library/Application Support/Plex Media Server/d$i"
  touch "$DIR/Library/Application Support/Plex Media Server/d$i"/f{1..80}
done
chown -R $OLD_UID:$OLD_GID "$DIR"
TOTAL=$(find "$DIR" | wc -l)
echo "tree built: $TOTAL entries, top-level=$(stat -c '%u:%g' "$DIR")"

top()  { stat -c '%u:%g' "$DIR"; }
oldu() { find "$DIR" -uid $OLD_UID | wc -l; }
oldg() { find "$DIR" -gid $OLD_GID | wc -l; }

echo
echo "=================================================================="
echo "PROBE 1 — chown -R ordering: is the TOP-LEVEL dir chowned LAST?"
echo "=================================================================="
# Deterministic: strace the real syscalls and compare the top-level's position.
strace -f -y -e trace=fchownat,chown,lchown -o /tmp/chown.trace \
  chown -R $NEW_UID:$NEW_GID "$DIR" >/dev/null 2>&1
TOTAL_CALLS=$(grep -c 'chownat\|chown' /tmp/chown.trace)
# The top-level dir call is the one naming the bare path (no child component).
TOPLINE=$(grep -n 'chownat' /tmp/chown.trace | grep -v 'Library' | grep "plexmediaserver" | tail -1 | cut -d: -f1)
echo "total chown syscalls: $TOTAL_CALLS"
echo "top-level dir chowned at syscall line: $TOPLINE"
echo "--- first 3 chown calls ---"; grep 'chownat' /tmp/chown.trace | head -3
echo "--- last 3 chown calls ---";  grep 'chownat' /tmp/chown.trace | tail -3

echo
echo "=================================================================="
echo "PROBE 2 — reset, then groupmod+usermod ONLY (the interrupted state)"
echo "=================================================================="
chown -R $OLD_UID:$OLD_GID "$DIR"
groupmod -g $NEW_GID plex
usermod  -u $NEW_UID plex
echo "getent:         $(getent passwd plex)"
echo "top-level dir:  $(top)"
echo "files still uid=$OLD_UID: $(oldu)"
echo "files still gid=$OLD_GID: $(oldg)  <-- groupmod does NOT chgrp (design 4.3)"

echo
echo "=================================================================="
echo "PROBE 3 — evaluate BOTH predicates at that exact interrupted state"
echo "=================================================================="
CUR_UID=$(getent passwd plex | cut -d: -f3)
DU=$(stat -c %u "$DIR"); DG=$(stat -c %g "$DIR")

# (a) CURRENT DESIGN: predicate keys on the USER (detailed-design.md:414)
if [ "$CUR_UID" != "$NEW_UID" ]; then A=TRUE; else A=FALSE; fi
echo "(a) current design  [passwd uid $CUR_UID != $NEW_UID]        => $A"

# (b) dir predicate, UID HALF ONLY
if [ "$DU" != "$NEW_UID" ]; then B=TRUE; else B=FALSE; fi
echo "(b) dir, uid only   [dir uid $DU != $NEW_UID]              => $B"

# (c) PROPOSED: dir predicate, BOTH HALVES
if [ "$DU" != "$NEW_UID" ] || [ "$DG" != "$NEW_GID" ]; then C=TRUE; else C=FALSE; fi
echo "(c) PROPOSED both   [dir $DU:$DG != $NEW_UID:$NEW_GID]     => $C"
echo
echo "TRUE = chown re-fires and recovery completes. FALSE = wedged."

echo
echo "=================================================================="
echo "PROBE 4 — interrupt chown -R MID-WALK, re-evaluate proposed predicate"
echo "=================================================================="
chown -R $OLD_UID:$OLD_GID "$DIR"
groupmod -g $NEW_GID plex >/dev/null 2>&1 || true
usermod  -u $NEW_UID plex >/dev/null 2>&1 || true
echo "pre-chown state: top-level=$(top)"
chown -R $NEW_UID:$NEW_GID "$DIR" &
CPID=$!
# kill it partway through the walk
for _ in $(seq 1 400); do :; done
kill -9 $CPID 2>/dev/null
wait $CPID 2>/dev/null
echo "AFTER INTERRUPT:"
echo "  top-level dir:            $(top)"
echo "  entries still gid=$OLD_GID:  $(oldg) of $TOTAL  <-- proof the walk was incomplete"
DU=$(stat -c %u "$DIR"); DG=$(stat -c %g "$DIR")
if [ "$DU" != "$NEW_UID" ] || [ "$DG" != "$NEW_GID" ]; then C=TRUE; else C=FALSE; fi
echo "  PROPOSED predicate [dir $DU:$DG]: $C  (TRUE => re-run completes it)"

echo
echo "=================================================================="
echo "PROBE 5 — R6: converged steady state must report changed=0"
echo "=================================================================="
chown -R $NEW_UID:$NEW_GID "$DIR"   # complete the migration
DU=$(stat -c %u "$DIR"); DG=$(stat -c %g "$DIR")
CUR_UID=$(getent passwd plex | cut -d: -f3)
if [ "$DU" != "$NEW_UID" ] || [ "$DG" != "$NEW_GID" ]; then C=TRUE; else C=FALSE; fi
if [ "$CUR_UID" != "$NEW_UID" ]; then S=TRUE; else S=FALSE; fi
echo "converged top-level: $DU:$DG"
echo "  chown predicate (dir both halves): $C   <-- must be FALSE for R6"
echo "  stop  predicate (passwd uid):      $S   <-- must be FALSE for R6"
echo "  uniform ownership: $(find "$DIR" ! -uid $NEW_UID | wc -l) entries not uid=$NEW_UID, $(find "$DIR" ! -gid $NEW_GID | wc -l) not gid=$NEW_GID"

echo
echo "=================================================================="
echo "PROBE 6 — fresh rebuild: user ABSENT, dir already correct"
echo "=================================================================="
# design 6.3: fresh rebuild -> pins create at 64000 -> dir already correct -> no chown
userdel plex 2>/dev/null; groupdel plex 2>/dev/null
if getent passwd plex >/dev/null; then echo "user present"; else echo "user ABSENT (as on a fresh rebuild)"; fi
DU=$(stat -c %u "$DIR"); DG=$(stat -c %g "$DIR")
if [ "$DU" != "$NEW_UID" ] || [ "$DG" != "$NEW_GID" ]; then C=TRUE; else C=FALSE; fi
echo "dir=$DU:$DG  chown predicate: $C  <-- FALSE, and it needed NO getent to decide"
echo
echo "PROBE COMPLETE"
