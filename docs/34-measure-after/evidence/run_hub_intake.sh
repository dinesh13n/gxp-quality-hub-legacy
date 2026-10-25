#!/bin/bash
# Stage 34 sandbox: hub shadow intake over the sandbox copy; K-06/K-07 hub-path measurements. Run after run_hub_metrics.sh (same scratch store).
R=$HOME/fde_sbx/s34-run; S=$HOME/fde_sbx/s34-scratch; O=$HOME/fde_sbx/s34-out
cd $R
export HUB_WORKTREE_ROOT=$HOME/mnt/Case-Execution/gxp-quality-hub-legacy HUB_SANDBOX_ROOT=$S PYTHONHASHSEED=0 PYTHONDONTWRITEBYTECODE=1
CFG=$S/config.json; I="python3 -B -m hub.intake --config $CFG"
step(){ local n=$1; shift; local t0=$(date +%s); "$@" > $O/hub-$n.json 2> $O/hub-$n.err; echo "$n rc=$? s=$(( $(date +%s)-t0 ))"; }
step 10-ingest-legacy $I ingest-legacy --data-dir $S/data --legacy-root $R --run-dir $S/run
step 11-report-before-replay $I report --data-dir $S/data
step 12-verify-replay $I verify-replay --data-dir $S/data --legacy-root $R --run-dir $S/run
step 13-report-after-replay $I report --data-dir $S/data
python3 -B -m hub.metrics --config $CFG snapshot --data-dir $S/data --legacy-root $R --run-dir $S/run > $O/hub-14-snapshot-after-intake.json 2> $O/hub-14-snapshot-after-intake.err; echo snap rc=$?
python3 -B -m hub.metrics --config $CFG values --data-dir $S/data > $O/hub-15-values-after-intake.json 2>/dev/null
python3 -B -m hub.admin --config $CFG verify-audit --data-dir $S/data > $O/hub-16-verify-audit.json 2> $O/hub-16-verify-audit.err; echo audit rc=$?
echo DONE
