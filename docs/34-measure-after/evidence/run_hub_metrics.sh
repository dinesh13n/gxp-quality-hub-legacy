#!/bin/bash
# Stage 34 sandbox run of the hub metrics CLI against a sandbox copy of the 125-case baseline. Never touches working-tree data/.
R=$HOME/fde_sbx/s34-run; S=$HOME/fde_sbx/s34-scratch; O=$HOME/fde_sbx/s34-out
cd $R
export HUB_WORKTREE_ROOT=$HOME/mnt/Case-Execution/gxp-quality-hub-legacy HUB_SANDBOX_ROOT=$S PYTHONHASHSEED=0 PYTHONDONTWRITEBYTECODE=1
rm -rf $S; mkdir -p $S/data $S/anchor $S/run
CFG=$S/config.json; echo "{\"audit\": {\"anchor_path\": \"$S/anchor/audit-anchor.jsonl\"}}" > $CFG
A="python3 -B -m hub.admin --config $CFG"; M="python3 -B -m hub.metrics --config $CFG"
step(){ local n=$1; shift; "$@" > $O/hub-$n.json 2> $O/hub-$n.err; echo "$n rc=$?"; }
step 01-migrate $A migrate --data-dir $S/data --backup-root $S/premig
step 01b-policy-migrate python3 -B -m hub.policy --config $CFG migrate --data-dir $S/data --backup-root $S/premig2
step 01b2-policy-seed python3 -B -m hub.policy --config $CFG seed --data-dir $S/data
step 01c-decision-migrate python3 -B -m hub.decision --config $CFG migrate --data-dir $S/data --backup-root $S/premig3
step 01d-intake-migrate python3 -B -m hub.intake --config $CFG migrate --data-dir $S/data --backup-root $S/premig4
step 01e-runs-migrate python3 -B -m hub.runs --config $CFG migrate --data-dir $S/data --backup-root $S/premig5
step 01f-decision-backfill python3 -B -m hub.decision --config $CFG backfill --data-dir $S/data --legacy-root $R --run-dir $S/run
step 01g-verify-projection python3 -B -m hub.decision --config $CFG verify-projection --data-dir $S/data
step 01h-verify-chain python3 -B -m hub.decision --config $CFG verify-chain --data-dir $S/data
step 02-registry $M registry --data-dir $S/data
step 03-snapshot $M snapshot --data-dir $S/data --legacy-root $R --run-dir $S/run
step 04-snapshot-again $M snapshot --data-dir $S/data --legacy-root $R --run-dir $S/run
step 05-kpi-coverage $M kpi-coverage --data-dir $S/data
step 06-values $M values --data-dir $S/data
step 07-month-end-nocutoff $M month-end --data-dir $S/data --legacy-root $R --run-dir $S/run
step 08-month-end $M month-end --data-dir $S/data --legacy-root $R --run-dir $S/run --cutoff 2025-12-31T23:59:59+00:00 --denominator cases
