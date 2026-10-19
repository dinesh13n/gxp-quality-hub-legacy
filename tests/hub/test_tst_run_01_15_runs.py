"""TST-RUN-01..03, 05..15 (F06 scheduled runs and run records; INC-07, scheduler OFF per OD-19). TST-RUN-04 (HTTP POST /runs role check) is planned for
INC-08 (no HTTP surface yet); its service-level equivalent is TST-HUB-INC07-S02. Synthetic, unvalidated data; zone_h.holders are synthetic test data.

A 'scheduled trigger' in these tests is an explicit call with trigger='scheduled' at a controlled test-clock time: there is no scheduler in the product.
"""
import ast
import json
import os
import re
import sqlite3
import unittest
from unittest import mock

import _support as S
import _inc07 as R
from hub.core.errors import ConfigInvalid
from hub.gate import errors as GE
from hub.obs import collect
from hub.runs import detector, jobs as jobs_mod
from hub.runs.errors import RunAlreadyRunning, RunCheckpointInvalid, RunScheduleDisabled, RunTotalsMismatch, RunUnknownJob
from hub.runs.service import RunService
from hub.security.canonical import parse

SCHEMA = os.path.join(S.CODE_ROOT, "docs", "12-specs", "contracts", "schemas", "run-record.schema.json")


def setUpModule():
    R.skip_in_inner_egress_run()


class _Base(unittest.TestCase):
    def setUp(self):
        self.stores = []

    def tearDown(self):
        for st in self.stores:
            st.close()

    def store(self, *a, **kw):
        st = R.RStore(*a, **kw)
        self.stores.append(st)
        return st


class TST_RUN_Runs(_Base):

    def test_TST_RUN_01_scheduled_trigger_runs_when_flag_is_on(self):
        """AC-RUN-01 (class B, OD-S12-10): flag switched on through Zone H ZH-09 by a (synthetic) holder; at the configured test-clock time the scheduled
        trigger starts a non-Zone-H job; the run record has trigger = scheduled; the missing-run detector then finds nothing missing."""
        st = self.store(extra={"schedule": {"expected": [{"job": "verify_projection", "at": "02:00"}]}})
        self.assertFalse(st.runs.schedule()["enabled"])
        st.clock._t = parse("2026-10-18T03:00:00.000000Z")
        state = st.enable_schedule()
        self.assertTrue(state["enabled"])
        ev = st.con.execute("SELECT event_type, actor, holder_check_ref, authority_ref FROM policy_events WHERE event_type = 'SCHEDULE_CHANGED'").fetchall()
        self.assertEqual(len(ev), 1)
        self.assertEqual((ev[0][0], ev[0][1]), ("SCHEDULE_CHANGED", "holder-1"))
        self.assertTrue(ev[0][2].startswith("audit:"))
        st.clock._t = parse("2026-10-19T02:00:00.000000Z")  # the configured time on the test clock
        rec = st.runs.run("verify_projection", st.service_session(), trigger="scheduled", correlation_id="t-r01")
        self.assertEqual((rec["trigger"], rec["outcome"], rec["triggered_by"]), ("scheduled", "finished", "svc-integration"))
        self.assertGreaterEqual(rec["started_at"], "2026-10-19T02:00:00")
        self.assertEqual(R.schema_problems(RunService.to_schema(rec), SCHEMA), [])
        det = detector.missing(st.con, st.runs.rs, "2026-10-19T09:00:00.000000Z")
        self.assertEqual((det["schedule"], det["expected_checked"], det["run_missed_total"]), ("enabled", 1, 0))
        self.assertEqual(collect.zone_h_service_actor_accepted(st.con), 0)

    def test_TST_RUN_02_scheduled_trigger_refused_on_fresh_install(self):
        """AC-RUN-02: fresh install (flag off): a scheduled trigger gets E-RUN-SCHEDULE-DISABLED and a run record with outcome refused; no lock, no data change."""
        st = self.store()
        before = st.digest()
        with self.assertRaises(RunScheduleDisabled) as cm:
            st.runs.run("verify_audit", st.service_session(), trigger="scheduled", resources={"anchor_path": st.anchor_path}, correlation_id="t-r02")
        self.assertEqual(cm.exception.code, "E-RUN-SCHEDULE-DISABLED")
        runs = st.runs.list_runs()
        self.assertEqual([(r["outcome"], r["trigger"], r["job"]) for r in runs], [("refused", "scheduled", "verify_audit")])
        self.assertEqual([e["event_type"] for e in st.run_events()], ["RUN_REFUSED"])
        self.assertEqual(st.con.execute("SELECT count(*) FROM run_lock").fetchone()[0], 0)
        self.assertEqual(st.digest(), before)
        self.assertEqual(R.schema_problems(RunService.to_schema(dict(runs[0], batch_size=1)), SCHEMA), [])
        self.assertEqual(st.audit_actions("RUN_REFUSED")[0]["outcome"], "denied")

    def test_TST_RUN_03_service_actor_cannot_enable_the_schedule(self):
        """AC-RUN-03: a service actor attempting ZH-09 is rejected (E-GATE-NOT-AUTHORISED) and the schedule stays disabled; a human non-holder is rejected
        too; with the SHIPPED empty holder list even a dispositioner gets E-GATE-NO-HOLDERS."""
        st = self.store()
        with self.assertRaises(GE.GateNotAuthorised):
            st.sched.set_enabled(st.service_session(), True, R.AUTH, "t-r03")
        with self.assertRaises(GE.GateNotAuthorised):
            st.sched.set_enabled(st.reauth("nonholder"), True, R.AUTH, "t-r03b")
        self.assertFalse(st.runs.schedule()["enabled"])
        self.assertEqual(st.con.execute("SELECT count(*) FROM policy_events WHERE event_type = 'SCHEDULE_CHANGED'").fetchone()[0], 0)
        att = [a for a in st.audit_actions("ZONE_H_ATTEMPT") if a["details"].get("zh") == "ZH-09"]
        self.assertEqual([(a["actor"], a["actor_kind"], a["outcome"]) for a in att], [("svc-integration", "service", "denied"), ("nonholder", "human", "denied")])
        self.assertEqual(collect.zone_h_service_actor_accepted(st.con), 0)
        shipped = self.store(extra={"zone_h": {"holders": []}})
        with self.assertRaises(GE.GateNoHolders):
            shipped.sched.set_enabled(shipped.reauth("holder-1"), True, R.AUTH, "t-r03c")
        self.assertFalse(shipped.runs.schedule()["enabled"])

    def test_TST_RUN_05_every_run_has_a_complete_record(self):
        """AC-RUN-05 / PNFR-14: 10 runs of mixed jobs -> 100% have a record with every BEH-RUN-03 field, conforming to run-record.schema.json."""
        st = self.store()
        ql, res = st.sess("ql"), {"anchor_path": st.anchor_path}
        plan = [("verify_audit", {}), ("verify_projection", {}), ("rebuild_projection", {}), ("metrics_snapshot", {}), ("verify_projection", {}),
                ("metrics_snapshot", {}), ("verify_audit", {}), ("intake_partner_feed", R.readers(10)), ("intake_partner_feed", R.readers(20)),
                ("verify_projection", {})]
        for i, (job, extra) in enumerate(plan):
            st.runs.run(job, ql, batch_size=10, resources=dict(res, **extra), correlation_id="t-r05-%d" % i)
        recs = st.runs.list_runs()
        self.assertEqual(len(recs), 10)
        fields = ("run_id", "job", "trigger", "triggered_by", "started_at", "ended_at", "inputs_seen", "outcomes_by_type", "errors", "limit_reached",
                  "batch_size", "backlog_remaining", "checkpoint", "config_version", "code_version")
        for r in recs:
            sr = RunService.to_schema(r)
            self.assertEqual(r["outcome"], "finished", r)
            self.assertEqual(R.schema_problems(sr, SCHEMA), [], sr)
            self.assertTrue(all(k in sr for k in fields))
            self.assertTrue(sr["config_version"] and sr["code_version"] and sr["started_at"] < sr["ended_at"])
        self.assertEqual([r["job"] for r in recs if r["job"] == "intake_partner_feed"], ["intake_partner_feed"] * 2)
        self.assertEqual(sum(r["inputs_seen"] for r in recs if r["job"] == "intake_partner_feed"), 20)

    def test_TST_RUN_06_run_totals_reconcile_with_outcome_rows(self):
        """AC-RUN-06 / BEH-RUN-04: a run processing 500 items -> sum(outcomes_by_type) = 500 = intake_outcome rows with that run's batch ids; a job whose
        reported totals disagree fails the run (E-RUN-TOTALS-MISMATCH)."""
        st = self.store()
        rec = st.runs.run("intake_partner_feed", st.sess("ql"), batch_size=1000, resources=R.readers(500), correlation_id="t-r06")
        rid = rec["run_id"]
        self.assertEqual((rec["inputs_seen"], sum(rec["outcomes_by_type"].values())), (500, 500))
        rows = st.con.execute("SELECT count(*) FROM intake_outcome WHERE run_id >= ? AND run_id < ?", (rid + ".b", rid + ".c")).fetchone()[0]
        self.assertEqual(rows, 500)
        by_outcome = dict(st.con.execute("SELECT outcome, count(*) FROM intake_outcome WHERE run_id >= ? AND run_id < ? GROUP BY 1", (rid + ".b", rid + ".c")))
        self.assertEqual(by_outcome, rec["outcomes_by_type"])
        lying = {"inputs_seen": 3, "outcomes_by_type": {"VALIDATED": 3}, "errors": [], "limit_reached": False, "backlog_remaining": 0, "checkpoint": None,
                 "reconcile_intake": True}
        with mock.patch.dict(jobs_mod.IMPLEMENTATIONS, {"intake_gateway": lambda ctx: lying}):
            with self.assertRaises(RunTotalsMismatch) as cm:
                st.runs.run("intake_gateway", st.sess("ql"), batch_size=10, correlation_id="t-r06b")
        self.assertEqual(cm.exception.details["outcome_rows"], 0)
        failed = [r for r in st.runs.list_runs() if r["job"] == "intake_gateway"][0]
        self.assertEqual((failed["outcome"], failed["errors"][0]["code"]), ("failed", "E-RUN-TOTALS-MISMATCH"))

    def test_TST_RUN_07_killed_run_is_abandoned_and_resume_equals_uninterrupted(self):
        """AC-RUN-07 / BEH-RUN-07: the process dies between a committed batch and its checkpoint row; the next run writes RUN_ABANDONED for it, resumes from
        the last checkpoint without duplicate effects, and the final outcome row set equals that of an uninterrupted run."""
        armed = [True]

        def kill(k):
            if k == 2 and armed[0]:
                armed[0] = False  # the process dies once
                raise R.SimulatedKill()
        a = self.store(hooks={"before_checkpoint": kill})
        ql = a.sess("ql")
        with self.assertRaises(R.SimulatedKill):
            a.runs.run("intake_partner_feed", ql, batch_size=100, until_empty=True, resources=R.readers(300), correlation_id="t-r07a")
        dead = a.runs.list_runs()[0]
        self.assertEqual(dead["outcome"], "running")
        self.assertEqual([e["event_type"] for e in a.run_events(dead["run_id"])], ["RUN_STARTED", "RUN_CHECKPOINT"])
        self.assertEqual(a.raw_digest(), (200, 200))  # batch 2 is committed, its checkpoint is not
        with self.assertRaises(RunAlreadyRunning):
            a.runs.run("intake_partner_feed", ql, batch_size=100, until_empty=True, resources=R.readers(300), correlation_id="t-r07x")
        a.clock.advance(16 * 60)  # heartbeat older than 15 minutes
        self.assertEqual(a.runs.get_run(dead["run_id"])["outcome"], "abandoned")  # visible before it is closed in the store
        rec = a.runs.run("intake_partner_feed", ql, batch_size=100, until_empty=True, resources=R.readers(300), correlation_id="t-r07b")
        old = a.run_events(dead["run_id"])
        self.assertEqual(old[-1]["event_type"], "RUN_ABANDONED")
        self.assertEqual(old[-1]["body"]["detected_by"], rec["run_id"])
        self.assertEqual((rec["outcome"], rec["inputs_seen"], rec["backlog_remaining"], sum(rec["outcomes_by_type"].values())), ("finished", 200, 0, 100))
        self.assertEqual(rec["checkpoint"]["order_keys"]["partner_feed"][:2], R.source(300).items[-1][0][:2])
        b = self.store()
        b.runs.run("intake_partner_feed", b.sess("ql"), batch_size=100, until_empty=True, resources=R.readers(300), correlation_id="t-r07c")
        self.assertEqual(a.raw_digest(), (300, 300))
        self.assertEqual(a.raw_digest(), b.raw_digest())
        self.assertEqual(a.outcome_rows(), b.outcome_rows())

    def test_TST_RUN_08_no_silent_cap_three_runs_exactly_once(self):
        """AC-RUN-08 / BEH-RUN-05: backlog 2,500, batch_size 1,000 -> run 1 limit_reached, backlog 1,500; run 2 backlog 500; run 3 backlog 0 and
        limit_reached false; every item processed exactly once; the checkpoint stores the ordering key of the last processed item."""
        st = self.store()
        ql, res = st.sess("ql"), R.readers(2500)
        src = R.source(2500)
        seen = []
        for i, (limit, backlog, last) in enumerate(((True, 1500, 999), (True, 500, 1999), (False, 0, 2499)), 1):
            rec = st.runs.run("intake_partner_feed", ql, batch_size=1000, resources=res, correlation_id="t-r08-%d" % i)
            seen.append((rec["limit_reached"], rec["backlog_remaining"], rec["batch_size"]))
            self.assertEqual(rec["checkpoint"]["order_keys"]["partner_feed"], src.items[last][0])
            self.assertEqual(R.schema_problems(RunService.to_schema(rec), SCHEMA), [])
            self.assertEqual((limit, backlog), (rec["limit_reached"], rec["backlog_remaining"]))
        self.assertEqual(seen, [(True, 1500, 1000), (True, 500, 1000), (False, 0, 1000)])
        self.assertEqual(st.raw_digest(), (2500, 2500))
        self.assertEqual(st.con.execute("SELECT count(*), count(DISTINCT raw_id) FROM intake_outcome").fetchone(), (2500, 2500))
        again = st.runs.run("intake_partner_feed", ql, batch_size=1000, resources=res, correlation_id="t-r08-4")
        self.assertEqual((again["inputs_seen"], again["backlog_remaining"], again["limit_reached"]), (0, 0, False))
        self.assertEqual(st.raw_digest(), (2500, 2500))

    def test_TST_RUN_09_until_empty_loops_inside_one_run(self):
        """AC-RUN-09: the same backlog with --until-empty -> one run, backlog 0 at the end, exactly one record, 3 checkpoints."""
        st = self.store()
        rec = st.runs.run("intake_partner_feed", st.sess("ql"), batch_size=1000, until_empty=True, resources=R.readers(2500), correlation_id="t-r09")
        self.assertEqual((rec["backlog_remaining"], rec["limit_reached"], rec["inputs_seen"], rec["outcome"]), (0, False, 2500, "finished"))
        self.assertEqual(len(st.runs.list_runs("intake_partner_feed")), 1)
        full = st.runs.get_run(rec["run_id"], with_events=True)
        self.assertEqual([e["event_type"] for e in full["events"]], ["RUN_STARTED"] + ["RUN_CHECKPOINT"] * 3 + ["RUN_FINISHED"])
        self.assertEqual([e["body"]["backlog_remaining"] for e in full["events"][1:4]], [1500, 500, 0])
        self.assertEqual(st.raw_digest(), (2500, 2500))
        self.assertEqual(full["events"][-1]["body"]["extras"]["batches"], 3)

    def test_TST_RUN_10_no_hard_coded_row_cap(self):
        """AC-RUN-10: no hard-coded row cap (LIMIT 1000 and friends) in the new source or its JSON / SQL; a batching job without a configured cap is refused
        (no hidden default); the cap used is printed in the run record (--batch-size or runs.batch_size)."""
        rx = re.compile(r"(?i)\bLIMIT\s+\d{2,}|\blimit\s*=\s*\d{2,}|\bbatch_size\s*[:=]\s*\d|\bfetchmany\(\s*\d|\.head\(\s*\d")
        legacy_cap = re.compile(r"(?i)LIMIT\s+1000\b|limit\s*=\s*1000\b|\[:1000\]")
        hits, legacy_hits = [], []
        for d, _, fns in os.walk(os.path.join(S.CODE_ROOT, "hub")):
            if "__pycache__" in d:
                continue
            for fn in fns:
                if not fn.endswith((".py", ".sql", ".json")):
                    continue
                p = os.path.join(d, fn)
                rel = os.path.relpath(p, os.path.join(S.CODE_ROOT, "hub"))
                text = open(p, encoding="utf-8").read()
                if rel.split(os.sep)[0] in ("runs", "metrics", "obs") and rx.search(text):
                    hits.append(rel)
                if legacy_cap.search(text):
                    legacy_hits.append(rel)
        self.assertEqual(hits, [])
        self.assertEqual(legacy_hits, [])
        st = self.store()
        with self.assertRaises(ConfigInvalid):
            st.runs.run("intake_partner_feed", st.sess("ql"), resources=R.readers(3), correlation_id="t-r10")
        self.assertEqual(st.runs.list_runs(), [])  # refused before any record: nothing was started
        rec = st.runs.run("intake_partner_feed", st.sess("ql"), batch_size=7, resources=R.readers(20), correlation_id="t-r10b")
        self.assertEqual((rec["batch_size"], rec["inputs_seen"], rec["limit_reached"], rec["backlog_remaining"]), (7, 7, True, 13))
        cfgd = self.store(extra={"runs": {"batch_size": 9}})
        rec = cfgd.runs.run("intake_partner_feed", cfgd.sess("ql"), resources=R.readers(20), correlation_id="t-r10c")
        self.assertEqual((rec["batch_size"], rec["inputs_seen"], rec["backlog_remaining"]), (9, 9, 11))

    def test_TST_RUN_11_single_flight_second_start_refused(self):
        """AC-RUN-11 / BEH-RUN-06: while a run of a job holds its lock a second start of the same job gets E-RUN-ALREADY-RUNNING and a refused record;
        exactly one run executes; a different job is not blocked."""
        st = self.store()
        con2 = sqlite3.connect(os.path.join(st.data, "hub.sqlite3"))
        con2.execute("PRAGMA foreign_keys = ON")
        seen = {}

        def other_start(rid):
            other = RunService(con2, st.s, st.clock, st.anchor, st.cfg)
            try:
                other.run("verify_projection", st.sess("ql"), correlation_id="t-r11b")
            except RunAlreadyRunning as e:
                seen["same"] = e
            seen["different"] = other.run("verify_audit", st.sess("ql"), resources={"anchor_path": st.anchor_path}, correlation_id="t-r11c")
        try:
            rec = st.run_service(hooks={"after_start": other_start}).run("verify_projection", st.sess("ql"), correlation_id="t-r11a")
        finally:
            con2.close()
        self.assertEqual(seen["same"].code, "E-RUN-ALREADY-RUNNING")
        self.assertEqual(seen["same"].details["held_by"], rec["run_id"])
        recs = [r for r in st.runs.list_runs() if r["job"] == "verify_projection"]
        self.assertEqual(sorted(r["outcome"] for r in recs), ["finished", "refused"])
        self.assertEqual(seen["different"]["outcome"], "finished")
        self.assertEqual(st.con.execute("SELECT count(*) FROM run_lock").fetchone()[0], 0)

    def test_TST_RUN_12_jobs_cannot_reach_zone_h(self):
        """AC-RUN-12 / FR-GATE-01: (a) import-graph / AST test: the job and runner modules import nothing from hub.gate and call no Zone H method; only
        hub/runs/schedule.py (ZH-09) imports the gate and no job module reaches it; (b) a job forced to call the gate with the service identity fails
        with E-GATE-NOT-AUTHORISED, the run is RUN_FAILED and the attempt is audited as denied."""
        base = os.path.join(S.CODE_ROOT, "hub", "runs")
        forbidden_calls = set(["require_holder", "set_binding", "adopt", "accept_open", "activate", "deactivate", "record_activation_decision",
                               "edit_rule_row", "fork_as_custom", "create_candidate", "resolve_conflict", "create_human_link", "retract",
                               "transition", "record_fact", "attach_evidence", "create_case", "GateService", "GatedPolicyService", "set_enabled"])
        job_modules = ["jobs", "service", "sources", "flag", "detector", "catalogue", "settings", "errors"]
        imports = {}
        for m in job_modules + ["schedule"]:
            tree = ast.parse(open(os.path.join(base, m + ".py"), encoding="utf-8").read())
            mods, used = set(), set()
            for n in ast.walk(tree):
                if isinstance(n, ast.ImportFrom) and n.module:
                    mods.add(n.module)
                    used.update(a.name for a in n.names)
                elif isinstance(n, ast.Import):
                    mods.update(a.name for a in n.names)
                elif isinstance(n, ast.Attribute):
                    used.add(n.attr)
                elif isinstance(n, ast.Name):
                    used.add(n.id)
            imports[m] = (mods, used)
        for m in job_modules:
            mods, used = imports[m]
            self.assertEqual([x for x in mods if x.startswith("hub.gate")], [], m)
            self.assertEqual(sorted(used & forbidden_calls), [], m)
        self.assertTrue([x for x in imports["schedule"][0] if x.startswith("hub.gate")])
        closure, todo = set(), ["jobs", "service"]
        while todo:
            m = todo.pop()
            if m in closure:
                continue
            closure.add(m)
            todo += [x.split(".")[2] for x in imports.get(m, (set(), set()))[0] if x.startswith("hub.runs.") and x.split(".")[2] in imports]
        self.assertNotIn("schedule", closure)
        st = self.store()

        def forced(ctx):
            from hub.gate.service import GateService
            GateService(ctx.con, ctx.s, ctx.clock, ctx.anchor).require_holder(st.service_session(), "ZH-06", ctx.cid, "ruleset:forced")
        with mock.patch.dict(jobs_mod.IMPLEMENTATIONS, {"verify_audit": forced}):
            with self.assertRaises(GE.GateNotAuthorised):
                st.runs.run("verify_audit", st.sess("ql"), correlation_id="t-r12")
        rec = st.runs.list_runs()[0]
        self.assertEqual((rec["outcome"], rec["errors"][0]["code"]), ("failed", "E-GATE-NOT-AUTHORISED"))
        att = [a for a in st.audit_actions("ZONE_H_ATTEMPT") if a["details"].get("zh") == "ZH-06"]
        self.assertEqual([(a["actor_kind"], a["outcome"]) for a in att], [("service", "denied")])
        self.assertEqual(collect.zone_h_service_actor_accepted(st.con), 0)
        self.assertEqual(st.con.execute("SELECT count(*) FROM run_lock").fetchone()[0], 0)

    def test_TST_RUN_13_unreachable_source_finishes_with_error_and_no_items(self):
        """AC-RUN-13: an unreachable source -> RUN_FINISHED with errors[] = SOURCE_UNREACHABLE, outcomes_by_type empty, no fabricated item."""
        st = self.store()
        before = st.digest()
        res = {"readers": {"partner_feed": R.rsources.UnreachableSource("partner_feed", {"reason": "connection refused (synthetic)"})}}
        rec = st.runs.run("intake_partner_feed", st.sess("ql"), batch_size=10, resources=res, correlation_id="t-r13")
        self.assertEqual(rec["outcome"], "finished")
        self.assertEqual([e["code"] for e in rec["errors"]], ["SOURCE_UNREACHABLE"])
        self.assertEqual((rec["outcomes_by_type"], rec["inputs_seen"], rec["backlog_remaining"]), ({}, 0, 0))
        after = st.digest()
        self.assertEqual({k: v - before[k] for k, v in after.items()}, dict((k, 0) for k in before))
        self.assertEqual(R.schema_problems(RunService.to_schema(rec), SCHEMA), [])

    def test_TST_RUN_14_corrupt_checkpoint_refuses_the_run(self):
        """AC-RUN-14: a corrupt checkpoint value -> E-RUN-CHECKPOINT-INVALID, run refused, no data change (several corruptions of the stored shape)."""
        st = self.store()
        ql = st.sess("ql")
        bodies = [{"checkpoint": {"order_keys": {"partner_feed": 5}}}, {"checkpoint": {"order_keys": {"gateway": ["a", "b", 0]}}},
                  {"checkpoint": "garbage"}, {"checkpoint": {"order_keys": {"no_such_source": ["2024-01-01T00:00:00Z", "k", 0]}}}]
        for i, cp in enumerate(bodies):
            rid = "RUN-FIXTURE%d" % i  # a prior run (written like the runner writes one) whose stored checkpoint was damaged
            base = {"batch_size": 10, "config_version": "x", "code_version": "x"}
            prog = {"inputs_seen": 1, "outcomes_by_type": {}, "backlog_remaining": 0}
            full = dict(prog, errors=[], limit_reached=False, checkpoint=cp["checkpoint"], batch_size=10, config_version="x", code_version="x")
            for seq, (et, body) in enumerate((("RUN_STARTED", base), ("RUN_CHECKPOINT", dict(prog, **cp)), ("RUN_FINISHED", full)), 1):
                st.con.execute("INSERT INTO run_event(run_id, run_seq, event_type, job, trigger, triggered_by, occurred_at, body) VALUES (?,?,?,?,?,?,?,?)",
                               (rid, seq, et, "intake_partner_feed", "manual", "fixture", st.clock(), json.dumps(body)))
            st.con.commit()
            before = st.digest()
            with self.assertRaises(RunCheckpointInvalid) as cm:
                st.runs.run("intake_partner_feed", ql, batch_size=10, resources=R.readers(5), correlation_id="t-r14-%d" % i)
            self.assertEqual(cm.exception.code, "E-RUN-CHECKPOINT-INVALID")
            self.assertEqual(st.digest(), before)
            self.assertEqual(st.con.execute("SELECT count(*) FROM run_lock").fetchone()[0], 0)
        refused = [r for r in st.runs.list_runs() if r["outcome"] == "refused"]
        self.assertEqual(len(refused), len(bodies))
        self.assertEqual({r["errors"][0]["code"] for r in refused}, {"E-RUN-CHECKPOINT-INVALID"})

    def test_TST_RUN_15_missing_run_detector(self):
        """AC-RUN-15 / BEH-RUN-08: schedule on, expected 02:00 run absent -> the detector lists it; once a scheduled run exists nothing is missing; with the
        schedule off it reports 'schedule disabled', not failures."""
        st = self.store(extra={"schedule": {"expected": [{"job": "intake_partner_feed", "at": "02:00"}], "grace_minutes": 60}})
        off = detector.missing(st.con, st.runs.rs, "2026-10-19T09:00:00.000000Z")
        self.assertEqual((off["schedule"], off["message"], off["missed"], off["run_missed_total"]), ("disabled", "schedule disabled", [], 0))
        st.clock._t = parse("2026-10-18T03:00:00.000000Z")
        st.enable_schedule()
        absent = detector.missing(st.con, st.runs.rs, "2026-10-19T09:00:00.000000Z")
        self.assertEqual(absent["missed"], [{"job": "intake_partner_feed", "expected_at": "2026-10-19T02:00:00.000000Z"}])
        self.assertEqual((absent["run_missed_total"], absent["by_job"]), (1, {"intake_partner_feed": 1}))
        not_due = detector.missing(st.con, st.runs.rs, "2026-10-19T02:30:00.000000Z")
        self.assertEqual(not_due["run_missed_total"], 0)  # inside the grace period
        st.clock._t = parse("2026-10-19T02:05:00.000000Z")
        st.runs.run("intake_partner_feed", st.service_session(), trigger="scheduled", batch_size=10, resources=R.readers(3), correlation_id="t-r15")
        done = detector.missing(st.con, st.runs.rs, "2026-10-19T09:00:00.000000Z")
        self.assertEqual((done["run_missed_total"], done["expected_checked"]), (0, 1))


if __name__ == "__main__":
    unittest.main()
