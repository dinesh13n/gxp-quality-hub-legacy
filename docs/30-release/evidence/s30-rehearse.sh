#!/bin/bash
# Stage 30 sandbox rehearsal: rollout -> backup -> release-gate refusal -> cutover dry-run (authority flip + L3 flip back) -> L2 restore -> corrupt-backup refusal
# -> L1 code revert (in a clone) -> regeneration check. EVERYTHING runs on copies under ~/fde_sbx/s30-reh; the working tree and its data/ are only READ
# (git archive / git clone of the repository, cp of the backup). Nothing here approves, merges, tags, installs CI or flips a shipped switch.
# usage: bash s30-rehearse.sh   (from anywhere; run it after committing, it rehearses the committed HEAD)
WT=$HOME/mnt/Case-Execution/gxp-quality-hub-legacy
BK=$WT/../_data-backup-2026-10-17
R=$HOME/fde_sbx/s30-reh
EV=$WT/docs/30-release/evidence
SUM=$EV/s30-rehearsal-summary.txt
export PYTHONDONTWRITEBYTECODE=1 PYTHONHASHSEED=0
: > $SUM
note(){ echo "$*" | tee -a $SUM; }
clean(){ sed -i "s#$HOME#~#g" "$1"; }
step(){ local n=$1; shift; local t0=$(date +%s.%N); "$@" > $EV/s30-log-$n.txt 2>&1; local rc=$?; local t1=$(date +%s.%N); clean $EV/s30-log-$n.txt; printf "%s rc=%s elapsed_s=%.2f\n" "$n" "$rc" "$(echo "$t1 - $t0" | bc)" | tee -a $SUM; return 0; }
chk(){ (cd $WT && sha256sum -c --quiet ../_data-backup-2026-10-17/SHA256SUMS.txt > /dev/null 2>&1; echo "$1 working-tree data checksum rc=$?" | tee -a $SUM); }
note "stage 30 rehearsal; HEAD=$(git -C $WT rev-parse --short HEAD); python=$(python3 --version 2>&1)"
chk "pre"
rm -rf $R; mkdir -p $R/repo $R/scratch/anchor
(cd $WT && git archive HEAD | tar -x -C $R/repo)
rm -rf $R/repo/data; cp -r $BK/data $R/repo/data   # replace any tracked data/ files by the verified backup copy
cd $R/repo
(sha256sum -c --quiet $BK/SHA256SUMS.txt > /dev/null 2>&1; echo "sandbox copy of data checksum rc=$?" | tee -a $SUM)
D=$R/scratch/data; CFG=$R/scratch/config.json; AN=$R/scratch/anchor/audit-anchor.jsonl
echo "{\"audit\": {\"anchor_path\": \"$AN\"}}" > $CFG
A="python3 -B -m hub.admin --config $CFG"; C="python3 -B -m hub.control --config $CFG"
export HUB_WORKTREE_ROOT=$WT HUB_SANDBOX_ROOT=$R/scratch
note "--- R1 rollout (fresh store, shadow)"
step 01-migrate $A migrate --data-dir $D --backup-root $R/scratch/premig
step 02-status $A status --data-dir $D
step 03-startup-check $A startup-check
step 04-verify-audit $A verify-audit --data-dir $D
step 05-posture python3 -B -m hub.release posture --config $CFG
step 06-golden-compare python3 -B -m hub --config $CFG golden-compare --json --data-dir $R/scratch/gc --legacy-root $R/repo --observe
note "--- R2 pre-cutover backup"
step 07-backup $A backup --data-dir $D --dest-root $R/scratch/backups --label rel-pre-001
step 08-verify-backup-manifest bash -c "cd $R/scratch/backups/rel-pre-001 && sha256sum -c SHA256SUMS"
python3 - > $EV/s30-head-at-backup.txt <<PY
import sqlite3
c=sqlite3.connect("$R/scratch/backups/rel-pre-001/hub.sqlite3"); print("audit head at backup:", c.execute("select max(audit_seq) from audit_log").fetchone()[0])
PY
note "--- R3 release record refuses 'ready' without evidence (mark-ready attempted with every unevaluated gate not_run)"
step 09-release-checklist-mark-ready $A release-checklist --data-dir $D --release R-S30-REHEARSAL-1 --evidence-dir $R/scratch/ev1 --scratch-root $R/scratch/g7 --mark-ready
step 09b-release-checklist-no-mark $A release-checklist --data-dir $D --release R-S30-REHEARSAL-2 --evidence-dir $R/scratch/ev2 --scratch-root $R/scratch/g7b --gate G1=fail:docs/30-release/evidence/s30-log-06-golden-compare.txt:UNAPPROVED --gate G2=pass:docs/30-release/evidence/s30-regression-groups.txt:I6 --gate G4=pass:docs/30-release/evidence/s30-regression-groups.txt:I45 --gate G8=pass:docs/30-release/evidence/s30-regression-groups.txt:I8a --gate G9=pass:docs/30-release/evidence/s30-regression-groups.txt:I6 --gate G10=pass:docs/30-release/evidence/s30-regression-groups.txt:B
cp $R/scratch/ev2/checklist-R-S30-REHEARSAL-2.json $EV/s30-checklist-R-S30-REHEARSAL-2.json 2>/dev/null; clean $EV/s30-checklist-R-S30-REHEARSAL-2.json
step 10-verify-audit-after-refusal $A verify-audit --data-dir $D
note "--- R4 cutover dry-run on the sandbox (the shipped config is NOT touched; the reference below is a rehearsal marker, not an approval)"
step 11-flags-before $C flags
step 12-set-authoritative-without-approval $C set-flag --flag capability_authority.CUT-2 --value '"authoritative"' --data-dir $D
step 13-posture-after-refusal python3 -B -m hub.release posture --config $CFG
step 14-set-authoritative-sandbox-ref $C set-flag --flag capability_authority.CUT-2 --value '"authoritative"' --approval-ref REHEARSAL-SANDBOX-NOT-AN-APPROVAL --data-dir $D
cp $CFG $EV/s30-config-while-authoritative.json; clean $EV/s30-config-while-authoritative.json
step 15-posture-while-authoritative python3 -B -m hub.release posture --config $CFG
step 16-verify-audit-while-authoritative $A verify-audit --data-dir $D
step 17-flip-to-shadow-L3 $C flip-to-shadow --capability CUT-2 --reason "Stage 30 rehearsal L3 rollback" --data-dir $D
step 18-posture-after-L3 python3 -B -m hub.release posture --config $CFG
step 19-verify-audit-after-L3 $A verify-audit --data-dir $D
python3 - > $EV/s30-audit-config-changed.txt <<PY
import sqlite3, json
c=sqlite3.connect("$R/scratch/data/hub.sqlite3")
for seq, obj, d in c.execute("select audit_seq, object_ref, details from audit_log where action='CONFIG_CHANGED' order by audit_seq"):
    j=json.loads(d); print(seq, obj, j.get("old"), "->", j.get("new"), "approval_ref=%s" % j.get("approval_ref"), j.get("direction"), j.get("rollback", ""))
PY
note "--- R5 L2 restore from the pre-cutover backup (records written after the backup are set aside, F-29-06)"
step 20-head-before-restore python3 -B -c "
import sqlite3; c=sqlite3.connect('$D/hub.sqlite3'); print('audit head before restore:', c.execute('select max(audit_seq) from audit_log').fetchone()[0])"
step 21-restore $A restore --data-dir $D --backup $R/scratch/backups/rel-pre-001
step 22-verify-audit-after-restore $A verify-audit --data-dir $D
step 23-posture-after-restore python3 -B -m hub.release posture --config $CFG
ls $R/scratch > $EV/s30-ls-scratch-after-restore.txt; clean $EV/s30-ls-scratch-after-restore.txt
note "--- R6 corrupt backup is refused"
cp -r $R/scratch/backups/rel-pre-001 $R/scratch/backups/rel-bad; printf 'X' | dd of=$R/scratch/backups/rel-bad/hub.sqlite3 bs=1 seek=100 conv=notrunc 2>/dev/null
step 24-restore-corrupt-backup $A restore --data-dir $D --backup $R/scratch/backups/rel-bad
step 25-verify-audit-after-refused-restore $A verify-audit --data-dir $D
note "--- R7 L1 code revert in a clone (the working repository is only read)"
CL=$R/clone; git clone -q --shared $WT $CL || { note 'clone failed'; exit 1; }
cd $CL || exit 1
MAINSHA=ef72e4e
step 26-l1-checkout git -c advice.detachedHead=false checkout -q -b rehearsal-l1 $MAINSHA
step 27-l1-revert-stage-31 git -c user.name=Claude -c user.email=noreply@anthropic.com revert --no-edit d1e3dbb
step 28-l1-tree-vs-pre-stage-31 bash -c "git diff --stat d1e3dbb^ HEAD -- hub tests/hub | tail -3; echo diff-rc=\$(git diff --quiet d1e3dbb^ HEAD -- hub tests/hub; echo \$?)"
step 29-l1-hub-release-gone bash -c "ls hub/obs; python3 -B -c 'import hub.obs.slo' 2>&1 | tail -1"
step 30-l1-revert-the-revert git -c user.name=Claude -c user.email=noreply@anthropic.com revert --no-edit HEAD
step 31-l1-tree-restored bash -c "echo diff-rc=\$(git diff --quiet $MAINSHA HEAD; echo \$?)"
cd $R/repo
note "--- R8 regeneration check F-29-12 (sandbox copy; shipped baseline is 125 cases, seed 4100)"
step 32-regenerate-125 bash -c "cp data/legacy.sqlite3 $R/legacy.shipped.sqlite3; python3 -B -m app.generate --count 125 --seed 4100 --reset; sha256sum data/legacy.sqlite3 $R/legacy.shipped.sqlite3"
step 33-kill-switch-reads grep -rn "hub.kill\|\"kill\"\|\[.kill.\]" hub --include=*.py
cd $WT
chk "post"
rm -rf $R/clone
note "done"
