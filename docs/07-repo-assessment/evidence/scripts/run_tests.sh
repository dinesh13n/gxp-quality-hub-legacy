#!/bin/bash
# Stage 7 test runner: every run on a FRESH copy of the pristine sandbox repo
S=$HOME/fde_sbx/stage7; E=$S/evidence
export PYTHONHASHSEED=0 PYTHONDONTWRITEBYTECODE=1
fresh(){ rm -rf $S/$1; cp -a $S/repo $S/$1; }
counts(){ python3 - "$1" <<'PY'
import sqlite3,sys
c=sqlite3.connect('file:%s?mode=ro'%sys.argv[1],uri=True)
print({t:c.execute('select count(*) from '+t).fetchone()[0] for t in ('cases','events','source_messages','operating_costs','batch_records','materials','deviations','lab_results','capa_actions','sop_versions','gateway_inbox') if c.execute("select 1 from sqlite_master where name=?",(t,)).fetchone()})
PY
}
# R1: full suite fresh
fresh t1; cd $S/t1
echo "PRE legacy.sqlite3 $(sha256sum data/legacy.sqlite3|cut -c1-64)" > $E/R1_unittest_fresh.log; counts data/legacy.sqlite3 >> $E/R1_unittest_fresh.log
( time python3 -m unittest discover -s tests -v ) >> $E/R1_unittest_fresh.log 2>&1; echo "EXIT=$?" >> $E/R1_unittest_fresh.log
echo "POST legacy.sqlite3 $(sha256sum data/legacy.sqlite3|cut -c1-64)" >> $E/R1_unittest_fresh.log; counts data/legacy.sqlite3 >> $E/R1_unittest_fresh.log
# R2: second run same (already-mutated) copy
( time python3 -m unittest discover -s tests -v ) > $E/R2_unittest_rerun_mutated.log 2>&1; echo "EXIT=$?" >> $E/R2_unittest_rerun_mutated.log
echo "POST legacy.sqlite3 $(sha256sum data/legacy.sqlite3|cut -c1-64)" >> $E/R2_unittest_rerun_mutated.log; counts data/legacy.sqlite3 >> $E/R2_unittest_rerun_mutated.log
# R3: fresh again (determinism of the post-state)
fresh t3; cd $S/t3
( time python3 -m unittest discover -s tests -v ) > $E/R3_unittest_fresh_again.log 2>&1; echo "EXIT=$?" >> $E/R3_unittest_fresh_again.log
echo "POST legacy.sqlite3 $(sha256sum data/legacy.sqlite3|cut -c1-64)" >> $E/R3_unittest_fresh_again.log; counts data/legacy.sqlite3 >> $E/R3_unittest_fresh_again.log
# R4: each module in isolation on fresh copy
: > $E/R4_per_module_isolation.log
for m in test_domain test_enterprise test_enterprise_legacy_v6 test_historical_fixture test_partner_feeds test_source_gateway test_workflow; do
  fresh t4; cd $S/t4
  echo "##### $m" >> $E/R4_per_module_isolation.log
  python3 -m unittest -v tests.$m >> $E/R4_per_module_isolation.log 2>&1; echo "EXIT=$?" >> $E/R4_per_module_isolation.log
  echo "POST $(counts data/legacy.sqlite3)" >> $E/R4_per_module_isolation.log
done
# R5: reverse-ish order: workflow first then enterprise then others (discover order is alphabetical)
fresh t5; cd $S/t5
python3 -m unittest -v tests.test_workflow tests.test_source_gateway tests.test_enterprise tests.test_domain > $E/R5_alt_order.log 2>&1; echo "EXIT=$?" >> $E/R5_alt_order.log
echo "POST $(counts data/legacy.sqlite3)" >> $E/R5_alt_order.log
# R6: verification scripts in order of scripts/verify.sh on fresh copy
fresh t6; cd $S/t6
{ echo '## scripts/verify.sh'; ( time sh scripts/verify.sh ) 2>&1; echo "EXIT=$?"; } > $E/R6_verify_sh.log 2>&1
# R7: other scripts (read-only ones) on pristine copy
fresh t7; cd $S/t7
{ for s in "scripts/offline_inventory.py" "scripts/verify_preloaded.py" "scripts/rehearse_local.py"; do echo "## python3 $s"; python3 $s | head -c 6000; echo "EXIT=${PIPESTATUS[0]}"; done; } > $E/R7_readonly_scripts.log 2>&1
echo DONE > $E/RUN_DONE
