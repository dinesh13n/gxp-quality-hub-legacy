#!/usr/bin/env bash
# Stage 15 INC-03 rollback rehearsal 1 (BEH-CO-06, rollback-strategy L1+L2, gate G7). Runs ONLY under $SBX.
set -u
R=$HOME/mnt/Case-Execution/gxp-quality-hub-legacy
SBX=$HOME/fde_sbx/s15-inc03/rehearsal-1
export HUB_WORKTREE_ROOT=$R PYTHONDONTWRITEBYTECODE=1 PYTHONHASHSEED=0 HUB_OPERATOR=rehearsal-operator
CFG=$SBX/hub-config.json; D=$SBX/live/data; ANCHOR=$SBX/live/anchor/audit-anchor.jsonl; BK=$SBX/backups
step() { echo; echo "### $*"; }
run() { echo "\$ $*"; "$@"; local rc=$?; echo "[rc=$rc]"; return 0; }
sha() { sha256sum "$1" | cut -c1-64; }
step "0. prepare code trees from git (read-only: git archive), config"
rm -rf $SBX/code-main $SBX/code-inc03 $SBX/live $BK $SBX/ev $SBX/scratch
mkdir -p $SBX/code-main $SBX/code-inc03
(cd $R && git archive main hub | tar -x -C $SBX/code-main) && (cd $R && git archive HEAD hub | tar -x -C $SBX/code-inc03)
echo "main=$(cd $R && git rev-parse --short main) inc03=$(cd $R && git rev-parse --short HEAD)"
printf '{"audit": {"anchor_path": "%s", "anchor_every": 100}}\n' "$ANCHOR" > $CFG; cat $CFG
OLD="python3 -B -m hub"; NEW="python3 -B -m hub.admin --config $CFG"
step "1. pre-release state: INC-02 code creates the M000 store"
cd $SBX/code-main && run $OLD init --data-dir $D && echo "M000 store sha=$(sha $D/hub.sqlite3)"
step "2. release INC-03: migrate (backup-before-migrate B0), create users, checklist, verify"
cd $SBX/code-inc03
run $NEW migrate --data-dir $D --backup-root $BK
B0=$(ls -d $BK/pre-migrate-M000-to-M001-*); echo "B0=$(basename $B0)"; cat $B0/SHA256SUMS
HUB_NEW_USER_PASSWORD=$(head -c 16 /dev/urandom | od -An -tx1 | tr -d ' \n') run $NEW user create --data-dir $D --principal alice --role reviewer
HUB_NEW_USER_PASSWORD=$(head -c 16 /dev/urandom | od -An -tx1 | tr -d ' \n') run $NEW user create --data-dir $D --principal bob --role quality_lead
run $NEW release-checklist --data-dir $D --release R-inc03-rehearsal --evidence-dir $SBX/ev --scratch-root $SBX/scratch --gate "G1=fail:$SBX/ev/G1-not-evaluated:OD-S12-13 open (golden-compare exits 6 by design)"
run $NEW verify-audit --data-dir $D
step "3. post-release backup B1, then more activity (carol) after B1"
run $NEW backup --data-dir $D --dest-root $BK --label B1
HUB_NEW_USER_PASSWORD=$(head -c 16 /dev/urandom | od -An -tx1 | tr -d ' \n') run $NEW user create --data-dir $D --principal carol --role compliance
run $NEW user list --data-dir $D
step "4. INCIDENT: offline tamper of audit row 5 (triggers dropped) -> verify-audit must fail (exit 17)"
python3 -B - "$D/hub.sqlite3" <<'PY'
import sqlite3, sys
con = sqlite3.connect(sys.argv[1]); con.execute("DROP TRIGGER audit_log_no_update")
with con: con.execute("UPDATE audit_log SET actor='mallory' WHERE audit_seq=5")
con.close(); print("tampered audit_seq 5 (offline attacker)")
PY
run $NEW verify-audit --data-dir $D
step "5. ROLLBACK L2 to B1: stop (CLI, no daemon) -> restore hub.sqlite3 + anchor -> checksum -> verify -> restart"
run $NEW restore --data-dir $D --backup $BK/B1
echo "restored sha=$(sha $D/hub.sqlite3) manifest=$(grep hub.sqlite3 $BK/B1/SHA256SUMS | cut -c1-64)"
run $NEW verify-audit --data-dir $D
run $NEW user list --data-dir $D
echo "set aside (not deleted):"; ls -R $D/pre-restore | head -8
step "6. FULL INCREMENT ROLLBACK (L1 code -> INC-02 + L2 store -> B0 pre-migration)"
run $NEW restore --data-dir $D --backup $B0
echo "restored sha=$(sha $D/hub.sqlite3) B0 manifest=$(grep hub.sqlite3 $B0/SHA256SUMS | cut -c1-64)"
cd $SBX/code-main
python3 -B -c "import sqlite3,sys; c=sqlite3.connect('file:'+sys.argv[1]+'?mode=ro',uri=True); print('schema_migrations', [r[0] for r in c.execute('SELECT version FROM schema_migrations')]); print('tables', sorted(r[0] for r in c.execute(\"SELECT name FROM sqlite_master WHERE type='table'\")))" $D/hub.sqlite3
run $OLD deviations --data-dir $D
run $OLD selfcheck
step "7. ROLL FORWARD again with INC-03 code (new pre-migration backup), verify"
cd $SBX/code-inc03
run $NEW migrate --data-dir $D --backup-root $BK
run $NEW verify-audit --data-dir $D
run $NEW status --data-dir $D
step "8. forward-compat probe: INC-02 code against an M001 store copy"
mkdir -p $SBX/probe && cp $D/hub.sqlite3 $SBX/probe/ && cd $SBX/code-main && run $OLD deviations --data-dir $SBX/probe
step "9. data checksum"
cd $R && sha256sum -c --quiet ../_data-backup-2026-10-17/SHA256SUMS.txt; echo "[backup manifest rc=$?]"
