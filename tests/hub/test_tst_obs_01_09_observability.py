"""TST-OBS-01..09 (observability-spec; INC-07): structured logs, run health, missing-run detector, log scan, latency measurement (no verdict),
zero-tripwires, selfcheck, KPI coverage and intake metrics. Synthetic, unvalidated data; 'measure only' items print numbers and never judge them."""
import json
import re
import unittest
from unittest import mock

import _support as S
import _inc06 as I
import _inc07 as R
from hub.metrics.sources import case_sites
from hub.core.errors import RuntimeUnsupported
from hub.obs import collect, log as obslog
from hub.runs import detector, reports
from hub.runs.errors import RunScheduleDisabled
from hub.security import errors as sec_errors
from hub.security.canonical import parse, utc_now

INJECTION = "<script>alert(1)</script>' OR '1'='1'; DROP TABLE cases;--"


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

    def logger(self, st, lines):
        return obslog.Logger(st.clock, lines.append, "test+inc07", "cfg-test")


class TST_OBS_Observability(_Base):

    def test_TST_OBS_01_one_log_line_per_call_with_correlation_id(self):
        """AC-OBS-01: a call completes -> one log line with correlation_id, op_id, outcome, duration_ms; the same correlation id is in the audit record
        (writes) and in the error envelope of a failed call."""
        st = self.store()
        lines = []
        log = self.logger(st, lines)
        with log.step("OP-RUN-01", "c-obs01", actor="ql", actor_kind="human", object_ref="job:verify_projection") as info:
            rec = st.runs.run("verify_projection", st.sess("ql"), correlation_id="c-obs01")
            info["run_id"] = rec["run_id"]
        self.assertEqual(len(lines), 1)
        row = json.loads(lines[0])
        self.assertEqual((row["correlation_id"], row["op_id"], row["outcome"], row["event"], row["run_id"]), ("c-obs01", "OP-RUN-01", "success", "http_request", rec["run_id"]))
        self.assertIsInstance(row["duration_ms"], float)
        self.assertGreaterEqual(row["duration_ms"], 0)
        self.assertEqual(sorted(row), sorted(obslog.FIELDS))
        self.assertGreaterEqual(st.con.execute("SELECT count(*) FROM audit_log WHERE correlation_id = 'c-obs01'").fetchone()[0], 1)
        with self.assertRaises(RunScheduleDisabled) as cm:
            with log.step("OP-RUN-01", "c-obs01e", actor="svc-integration", actor_kind="service"):
                st.runs.run("verify_audit", st.service_session(), trigger="scheduled", resources={"anchor_path": st.anchor_path}, correlation_id="c-obs01e")
        env = obslog.envelope_with_correlation(cm.exception, "c-obs01e")
        err = json.loads(lines[1])
        self.assertEqual((env["correlation_id"], err["correlation_id"], err["error_code"], err["outcome"]),
                         ("c-obs01e", "c-obs01e", "E-RUN-SCHEDULE-DISABLED", "error"))
        self.assertGreaterEqual(st.con.execute("SELECT count(*) FROM audit_log WHERE correlation_id = 'c-obs01e'").fetchone()[0], 1)

    def test_TST_OBS_02_health_lists_every_run_and_the_killed_one_as_abandoned(self):
        """AC-OBS-02: 10 job runs, one killed -> `report health` lists every run and the killed run as abandoned (amber), before and after it is closed."""
        flag = [True]

        def kill(k):
            if flag[0]:
                raise R.SimulatedKill()
        st = self.store(hooks={"before_checkpoint": kill})
        ql = st.sess("ql")
        with self.assertRaises(R.SimulatedKill):
            st.runs.run("intake_partner_feed", ql, batch_size=10, resources=R.readers(30), correlation_id="t-o2k")
        flag[0] = False
        for i, job in enumerate(("verify_audit", "verify_projection", "rebuild_projection", "metrics_snapshot") * 3):
            if i == 9:
                break
            st.runs.run(job, ql, resources={"anchor_path": st.anchor_path}, correlation_id="t-o2-%d" % i)
        st.clock.advance(16 * 60)
        h = reports.health(st.runs, st.clock(), st.anchor_path)
        self.assertEqual(len(h["runs"]), 10)
        self.assertEqual(h["run_counts"], {"abandoned": 1, "finished": 9})
        ab = [i for i in h["items"] if i["code"] == "RUN_ABANDONED"]
        self.assertEqual([(i["level"], i["job"], i["closed_in_store"]) for i in ab], [("amber", "intake_partner_feed", False)])
        self.assertEqual(h["label"], "synthetic, unvalidated")
        closed = st.runs.reap_stale("t-o2r")
        self.assertEqual(len(closed), 1)
        h2 = reports.health(st.runs, st.clock(), st.anchor_path)
        self.assertEqual(len(h2["runs"]), 10)
        self.assertEqual([i["closed_in_store"] for i in h2["items"] if i["code"] == "RUN_ABANDONED"], [True])
        self.assertEqual([i for i in h2["items"] if i["level"] == "red"], [])

    def test_TST_OBS_03_missing_run_detector_counts_the_absent_run(self):
        """AC-OBS-03: schedule enabled, one expected run absent -> run_missed_total = 1 and the run is listed (also exported as an observability sample)."""
        st = self.store(extra={"schedule": {"expected": [{"job": "verify_audit", "at": "02:00"}, {"job": "verify_projection", "at": "03:00"}]}})
        st.clock._t = parse("2026-10-18T04:00:00.000000Z")
        st.enable_schedule()
        st.clock._t = parse("2026-10-19T02:10:00.000000Z")
        st.runs.run("verify_audit", st.service_session(), trigger="scheduled", resources={"anchor_path": st.anchor_path}, correlation_id="t-o3")
        det = detector.missing(st.con, st.runs.rs, "2026-10-19T09:00:00.000000Z")
        self.assertEqual(det["run_missed_total"], 1)
        self.assertEqual(det["missed"], [{"job": "verify_projection", "expected_at": "2026-10-19T03:00:00.000000Z"}])
        smp = collect.samples(st.con, st.runs.list_runs(), det["by_job"])
        self.assertEqual(collect.value_of(smp, "run_missed_total", job="verify_projection"), 1)
        self.assertEqual(collect.value_of(smp, "run_missed_total"), 1)
        h = reports.health(st.runs, "2026-10-19T09:00:00.000000Z")
        self.assertIn({"level": "red", "code": "RUN_MISSED", "count": 1}, h["items"])

    def test_TST_OBS_04_logs_contain_no_secrets_tokens_hashes_or_raw_text(self):
        """AC-OBS-04: logs produced by a mini acceptance run (successful run, failed logins, injection fixtures, denied Zone H) scanned for passwords,
        tokens, hashes and raw notes text -> 0 matches; the scanner does find a planted leak (negative control)."""
        st = self.store()
        lines = []
        log = self.logger(st, lines)
        wrong = "Wr0ng-Passw0rd-SYNTHETIC"
        secrets = [st.pw, wrong, INJECTION] + list(st.tokens.values())
        for name, pw in (("rev", wrong), ("rev", st.pw), ("nobody-" + INJECTION[:20], wrong)):
            try:
                with log.step("OP-AUTH-LOGIN", "c-o4-login", event="auth_login", actor=name):
                    st.authn.login(name, pw, "c-o4-login")
            except Exception:
                pass
        try:
            with log.step("OP-AUTH-ME", "c-o4-bad", event="auth_denied"):
                st.authn.authenticate("bogus-token-" + INJECTION, "c-o4-bad")
        except Exception:
            pass
        with log.step("OP-RUN-01", "c-o4-run", actor="ql", object_ref="job:" + INJECTION):
            st.runs.run("intake_partner_feed", st.sess("ql"), batch_size=5,
                        resources={"readers": {"partner_feed": R.rsources.OrderedSource("partner_feed", I.batch(5))}}, correlation_id="c-o4-run")
        try:
            with log.step("OP-GATE-ZH09", "c-o4-zh", event="zone_h_attempt", actor="svc-integration", actor_kind="service"):
                st.sched.set_enabled(st.service_session(), True, INJECTION, "c-o4-zh")
        except Exception:
            pass
        log.emit("run_finished", correlation_id=INJECTION, object_ref=INJECTION, run_id="RUN-1; DROP", actor="x" * 200)
        self.assertGreaterEqual(len(lines), 6)
        self.assertEqual(obslog.prohibited_findings(lines, secrets), [])
        self.assertEqual(json.loads(lines[-1])["correlation_id"], "redacted")
        for ln in lines:
            self.assertEqual(set(json.loads(ln)), set(obslog.FIELDS))
        self.assertNotEqual(obslog.prohibited_findings(lines + ['{"password":"x"}', '{"t":"%s"}' % ("a" * 64), '{"n":"%s"}' % INJECTION], secrets), [])
        kinds = set(f["kind"] for f in obslog.prohibited_findings(['{"password": "x"}', "a" * 64, "<script>"], []))
        self.assertEqual(kinds, {"credential_assignment", "hex_digest", "markup_or_sql"})

    def test_TST_OBS_05_latency_p50_p95_without_a_verdict(self):
        """AC-OBS-05 (measure only, OPD-14): 200 calls per key operation on the 125-case baseline -> p50 and p95 per operation are printed; no
        pass / fail anywhere."""
        st = self.store()
        ql = st.sess("ql")
        ops = {"decision.state": lambda: st.svc.state(ql, "C00000001"), "runs.list_runs": st.runs.list_runs,
               "metrics.time_to_close": lambda: st.met.time_to_close(store=False), "policy.list": st.pol.list_policies}
        rep = reports.latency(ops, 200, utc_now)
        self.assertEqual([o["operation"] for o in rep["operations"]], sorted(ops))
        for o in rep["operations"]:
            self.assertEqual(o["calls"], 200)
            self.assertLessEqual(o["p50_ms"], o["p95_ms"])
            self.assertGreaterEqual(o["p50_ms"], 0)
        self.assertIsNone(rep["verdict"])
        text = json.dumps(rep).lower()
        for word in ("pass", "fail", "target met", "within"):
            self.assertNotIn(word, text.replace("measure only: no target exists", ""))
        self.assertEqual(rep["label"], "synthetic, unvalidated")

    def test_TST_OBS_06_zero_tripwires_after_a_mixed_run(self):
        """AC-OBS-06: after a mixed run (including a service-actor Zone H attempt) model_calls_total = 0, egress_attempts_total = 0 and
        zone_h_service_actor_accepted = 0; the rejection is counted; a non-zero tripwire turns the health report red."""
        st = self.store()
        st.runs.run("verify_projection", st.sess("ql"), correlation_id="t-o6")
        with self.assertRaises(Exception):
            st.sched.set_enabled(st.service_session(), True, R.AUTH, "t-o6z")
        trip = collect.tripwires(st.con)
        self.assertEqual(trip, {"model_calls_total": 0, "egress_attempts_total": 0, "zone_h_service_actor_accepted": 0})
        smp = collect.samples(st.con, st.runs.list_runs())
        self.assertEqual([collect.value_of(smp, k) for k in sorted(trip)], [0, 0, 0])
        self.assertGreaterEqual(collect.value_of(smp, "zone_h_service_actor_rejections_total"), 1)
        end = collect.run_end_samples(st.con, "verify_projection", 0.5, 0)
        self.assertEqual(sorted(s["name"] for s in end if s["name"].endswith("_total") or s["name"] == "zone_h_service_actor_accepted"),
                         ["egress_attempts_total", "model_calls_total", "zone_h_service_actor_accepted"])
        self.assertEqual(reports.health(st.runs, st.clock())["items"], [])
        with mock.patch.object(collect.tripwire_metrics, "tripwires", return_value={"model_calls_total": 1, "egress_attempts_total": 0}):
            h = reports.health(st.runs, st.clock())
        self.assertIn({"level": "red", "code": "TRIPWIRE_NON_ZERO", "metric": "model_calls_total", "value": 1}, h["items"])

    def test_TST_OBS_07_selfcheck_prints_versions_fts5_config_hash_gate(self):
        """AC-OBS-07 (class B, OD-S12-12; both modes): selfcheck prints Python, SQLite, FTS5, config hash and gate status under the default floor 3.10;
        under the ADR-018 PROPOSED floor 3.12 this 3.10 device is refused E-CO-RUNTIME-UNSUPPORTED; FTS5 absent is reported, not fatal."""
        st = self.store()
        rep = reports.selfcheck(st.cfg, st.s, st.con)
        self.assertEqual(rep["runtime"]["floor"], "3.10")
        self.assertTrue(re.match(r"^3\.\d+\.\d+$", rep["runtime"]["python"]) and re.match(r"^3\.\d+\.\d+$", rep["runtime"]["sqlite"]))
        self.assertIsInstance(rep["runtime"]["fts5"], bool)
        self.assertTrue(re.match(r"^[0-9a-f]{64}$", rep["config_hash"]))
        self.assertEqual(rep["gate"], {"disposition_mode": rep["gate"]["disposition_mode"], "holders_configured": 2, "schedule_enabled": False})
        self.assertEqual(rep["label"], "synthetic, unvalidated")
        self.assertEqual(reports.selfcheck(st.cfg, st.s, st.con)["config_hash"], rep["config_hash"])
        if tuple(__import__("sys").version_info[:2]) < (3, 12):
            with self.assertRaises(RuntimeUnsupported):
                reports.selfcheck(st.cfg, st.s, st.con, floor="3.12")
        with mock.patch("hub.runtime.fts5_available", return_value=False):
            self.assertFalse(reports.selfcheck(st.cfg, st.s, st.con)["runtime"]["fts5"])
            smp = collect.samples(st.con)
            self.assertEqual(collect.value_of(smp, "search_engine", engine="fallback"), 1)
        st.enable_schedule()
        self.assertTrue(reports.selfcheck(st.cfg, st.s, st.con)["gate"]["schedule_enabled"])

    def test_TST_OBS_08_kpi_coverage_on_the_baseline(self):
        """AC-OBS-08: kpi-coverage on the shipped baseline lists every R1 KPI with a value or a stated reason (no_completed_cycles etc.); nothing is
        silently absent and nothing is zero-filled."""
        st = self.store()
        sites = case_sites(R.D.legacy_handle("p7obs-"))
        st.met.snapshot("t-o8", site_of=sites, as_of="2025-12-19")
        cov = {k["metric_id"]: k for k in st.met.kpi_coverage()}
        self.assertEqual(sorted(cov), ["MET-BACKLOG-D-OPS", "MET-MONTH-END-TOTAL", "MET-TTC-C-EVID", "MET-TTC-C-OPS", "MET-UNRESOLVED-EXC-RATE-D-OPS"])
        for k in cov.values():
            self.assertTrue(k["value"] is not None or k["reason"], k)
            self.assertEqual(k["label"], "synthetic, unvalidated")
        self.assertEqual((cov["MET-TTC-C-OPS"]["status"], cov["MET-TTC-C-OPS"]["reason"]), ("no_value", "no_completed_cycles"))
        self.assertEqual((cov["MET-TTC-C-EVID"]["status"], cov["MET-TTC-C-EVID"]["reason"]), ("no_value", "no_completed_cycles"))
        self.assertEqual((cov["MET-BACKLOG-D-OPS"]["status"], cov["MET-BACKLOG-D-OPS"]["value"]), ("computed", "89"))
        self.assertEqual(cov["MET-MONTH-END-TOTAL"]["status"], "no_value")
        self.assertIn("cutoff_ts", cov["MET-MONTH-END-TOTAL"]["reason"])
        self.assertEqual(cov["MET-UNRESOLVED-EXC-RATE-D-OPS"]["reason"], "no_exception_queue_items")

    def test_TST_OBS_09_duplicate_replay_counts_noop_duplicates_and_leaves_queues(self):
        """AC-OBS-09: a duplicate replay of 100 items -> intake_noop_duplicate_total +100 and the queue depths unchanged."""
        st = self.store()
        items = I.batch(100)
        st.isvc.ingest("partner_feed", items, "o9-first", "t-o9a")
        mid = collect.samples(st.con)
        st.isvc.ingest("partner_feed", items, "o9-replay", "t-o9b")
        after = collect.samples(st.con)
        d = collect.value_of(after, "intake_noop_duplicate_total") - collect.value_of(mid, "intake_noop_duplicate_total")
        self.assertEqual(d, 100)
        depth = lambda smp: [(s["name"], tuple(sorted(s["labels"].items())), s["value"]) for s in smp if s["name"] in ("quarantine_depth", "exception_queue_depth")]
        self.assertEqual(depth(mid), depth(after))
        self.assertTrue(depth(after))
        self.assertEqual(collect.value_of(mid, "intake_noop_duplicate_total"), 0)


if __name__ == "__main__":
    unittest.main()
