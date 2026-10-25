#!/bin/bash
# Stage 29 sandbox rehearsal: backup -> damage (sandbox copy only) -> detect -> restore -> verify. NOT a drill on working-tree data.
R=$HOME/fde_sbx/s29-reh; cd $R/repo
export HUB_WORKTREE_ROOT=$HOME/mnt/Case-Execution/gxp-quality-hub-legacy HUB_SANDBOX_ROOT=$R/scratch PYTHONHASHSEED=0 PYTHONDONTWRITEBYTECODE=1
D=$R/scratch/data; mkdir -p $R/scratch/anchor; CFG=$R/scratch-config.json; echo "{\"audit\": {\"anchor_path\": \"$R/scratch/anchor/audit-anchor.jsonl\"}}" > $CFG; A="python3 -B -m hub.admin --config $CFG"
step(){ local n=$1; shift; local t0=$(date +%s.%N); "$@" > $R/log-$n.txt 2>&1; local rc=$?; local t1=$(date +%s.%N); printf "%s rc=%s elapsed_s=%.2f\n" "$n" "$rc" "$(echo "$t1 - $t0" | bc)"; }
rm -rf $R/scratch/*; mkdir -p $D $R/scratch/anchor
step 01-migrate $A migrate --data-dir $D --backup-root $R/scratch/premig
step 02-status $A status --data-dir $D
step 03-verify-audit-clean $A verify-audit --data-dir $D
step 04-backup $A backup --data-dir $D --dest-root $R/scratch/backups --label reh-001
ls -la $D $R/scratch/backups/reh-001 > $R/ls-after-backup.txt 2>&1
step 05-verify-backup-manifest bash -c "cd $R/scratch/backups/reh-001 && sha256sum -c SHA256SUMS"
step 06-verify-audit-after-backup $A verify-audit --data-dir $D
# damage: truncate the audit anchor in the sandbox copy (simulated tamper / loss)
AN=$(find $R/scratch/anchor -name 'audit-anchor.jsonl' | head -1); echo "anchor=$AN" > $R/anchor-path.txt
if [ -n "$AN" ]; then cp $AN $R/anchor.before; echo '{"seq":999999,"hash":"deadbeef"}' >> $AN; fi
step 07-verify-audit-after-damage $A verify-audit --data-dir $D
step 08-restore $A restore --data-dir $D --backup $R/scratch/backups/reh-001
step 09-verify-audit-after-restore $A verify-audit --data-dir $D
# negative: corrupt the backup copy and confirm restore refuses
cp -r $R/scratch/backups/reh-001 $R/scratch/backups/reh-bad; printf 'X' | dd of=$R/scratch/backups/reh-bad/hub.sqlite3 bs=1 seek=100 conv=notrunc 2>/dev/null
step 10-restore-corrupt-backup $A restore --data-dir $D --backup $R/scratch/backups/reh-bad
step 11-verify-audit-after-refused-restore $A verify-audit --data-dir $D
