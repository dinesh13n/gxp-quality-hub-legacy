"""Stage 15 INC-07 supplementary tests (no Stage 13 ID; TST-HUB-INC07-Sxx): the M005 applier and the runs CLI, run roles (service-level equivalent of
TST-RUN-04), CLI end to end with log scan, timeliness and time zone, text-amount handling (service-level TST-MET-12), renderings and determinism (service-
level TST-MET-02 / 21), database triggers, no-scheduler static scan, stale / abandoned runs, job coverage, exception rate, error codes, purity / deny-list,
settings validation, schedule flag both ways, shipped configuration. Synthetic, unvalidated.
"""
import ast
import json
import os
import sqlite3
import subprocess
import sys
import unittest

import _support as S
import _inc06 as I
import _inc07 as R
from hub.core.errors import ConfigInvalid, HubError
from hub.gate import errors as GE
from hub.guards import no_ai
from hub.metrics import errors as met_errors, values as V
from hub.metrics.errors import MetUnparsableInput
from hub.metrics.sources import RowsSource
from hub.obs import log as obslog
from hub.runs import catalogue, detector, errors as run_errors, jobs as jobs_mod, schema as rschema, settings as rsettings, sources as rsources
from hub.runs.errors import RunAlreadyRunning
from hub.security import scan
from hub.security.canonical import parse
from hub.security.errors import AuthForbidden

CUTOFF = "2030-01-01T00:00:00.000000Z"


def setUpModule():
    R.skip_in_inner_egress_run()


def cli(module, args, cfg_path, env_extra=None, timeout=120):
    return subprocess.run([sys.executable, "-B", "-m", module, "--config", cfg_path] + list(args), cwd=S.CODE_ROOT, env=S.child_env(env_extra),
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, timeout=timeout)


def jout(proc):
    assert proc.returncode == 0, proc.stderr[-1500:]
    return json.loads(proc.stdout)


def envelope(proc):
    """The error envelope is the last JSON document on stderr (pretty-printed, after any one-line log records)."""
    text = proc.stderr
    k = text.rfind("\n{\n")
    k = 0 if k < 0 and text.startswith("{\n") else k + 1
    return json.loads(text[k:]) if k >= 0 and text.strip() else None


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


class TST_HUB_INC07_Supplementary(_Base):

    def test_TST_HUB_INC07_S01_m005_applier_and_status(self):
        """S01: M005 is applied by its own module after a backup (M001..M004 required), is idempotent, is reported by `status`; a store without M005
        refuses RunService / MetricsService construction."""
        i6 = I.IStore(loaded=False)
        self.stores.append(i6)
        with self.assertRaises(HubError):
            R.RunService(i6.con, i6.s, i6.clock, i6.anchor, i6.cfg)
        self.assertEqual(rschema.status(i6.con)["state"], "absent")
        bk = S.tmpdir("p7bk-")
        p = cli("hub.runs", ["migrate", "--data-dir", i6.data, "--backup-root", bk], i6.cfg_path)
        self.assertEqual(p.returncode, 0, p.stderr[-1500:])
        out = json.loads(p.stdout)
        self.assertTrue(out["applied"])
        self.assertTrue(out["backup"]["label"].startswith("pre-runs-M005-"))
        self.assertEqual(jout(cli("hub.runs", ["status", "--data-dir", i6.data], i6.cfg_path))["state"], "applied")
        again = jout(cli("hub.runs", ["migrate", "--data-dir", i6.data, "--backup-root", bk], i6.cfg_path))
        self.assertFalse(again["applied"])
        con = sqlite3.connect(os.path.join(i6.data, "hub.sqlite3"))
        try:
            names = set(r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type = 'table'"))
        finally:
            con.close()
        self.assertTrue({"run_event", "run_lock", "metric_definition", "metric_value", "obs_metric", "runs_schema_migrations"} <= names)

    def test_TST_HUB_INC07_S02_run_roles(self):
        """S02 (service-level TST-RUN-04): quality_lead, compliance and the integration service identity may start a run; a reviewer is forbidden;
        no lock is left behind by a forbidden start."""
        st = self.store(loaded=False)
        for who in ("ql", "comp"):
            self.assertEqual(st.runs.run("verify_projection", st.sess(who), correlation_id="t-s02")["outcome"], "finished")
        self.assertEqual(st.runs.run("verify_projection", st.service_session(), correlation_id="t-s02")["triggered_by"], "svc-integration")
        with self.assertRaises(AuthForbidden):
            st.runs.run("verify_projection", st.sess("rev"), correlation_id="t-s02r")
        with self.assertRaises(AuthForbidden):
            st.runs.run("verify_projection", st.sess("nonholder"), correlation_id="t-s02n")
        self.assertEqual(st.con.execute("SELECT count(*) FROM run_lock").fetchone()[0], 0)
        self.assertEqual(len(st.runs.list_runs()), 3)

    def test_TST_HUB_INC07_S03_cli_end_to_end_and_log_scan(self):
        """S03: `python -m hub.runs` list / run / show / report health / detect-missing / schedule show / selfcheck / obs-snapshot against a store; the
        password comes from the environment only; stderr log lines pass the log scan; the error envelope carries the correlation id."""
        st = self.store(loaded=False)
        env = {"HUB_RUN_PASSWORD": st.pw}
        base = ["--data-dir", st.data]
        p = cli("hub.runs", ["--correlation-id", "cli-s03", "run", "verify_projection", "--principal", "ql"] + base, st.cfg_path, env)
        self.assertEqual(p.returncode, 0, p.stderr[-1500:])
        rec = json.loads(p.stdout)
        self.assertEqual((rec["job"], rec["outcome"], rec["trigger"]), ("verify_projection", "finished", "manual"))
        lines = [l for l in p.stderr.splitlines() if l.strip()]
        self.assertTrue(lines)
        self.assertEqual(obslog.prohibited_findings(lines, [st.pw] + list(st.tokens.values())), [])
        self.assertEqual(json.loads(lines[-1])["correlation_id"], "cli-s03")
        self.assertEqual(json.loads(cli("hub.runs", ["list"] + base, st.cfg_path).stdout)["runs"][0]["run_id"], rec["run_id"])
        shown = json.loads(cli("hub.runs", ["show", rec["run_id"]] + base, st.cfg_path).stdout)
        self.assertEqual([e["event_type"] for e in shown["events"]], ["RUN_STARTED", "RUN_FINISHED"])
        health = json.loads(cli("hub.runs", ["report", "health"] + base, st.cfg_path).stdout)
        self.assertEqual((len(health["runs"]), health["label"]), (1, "synthetic, unvalidated"))
        self.assertEqual(json.loads(cli("hub.runs", ["detect-missing"] + base, st.cfg_path).stdout)["schedule"], "disabled")
        self.assertFalse(json.loads(cli("hub.runs", ["schedule", "show"] + base, st.cfg_path).stdout)["enabled"])
        sc = json.loads(cli("hub.runs", ["selfcheck"] + base, st.cfg_path).stdout)
        self.assertEqual((sc["runtime"]["floor"], sc["gate"]["schedule_enabled"]), ("3.10", False))
        self.assertGreater(json.loads(cli("hub.runs", ["obs-snapshot"] + base, st.cfg_path).stdout)["samples_stored"], 0)
        bad = cli("hub.runs", ["--correlation-id", "cli-s03b", "run", "verify_projection", "--principal", "ql"] + base, st.cfg_path,
                  {"HUB_RUN_PASSWORD": "wrong-password-synthetic"})
        self.assertNotEqual(bad.returncode, 0)
        self.assertEqual(envelope(bad)["correlation_id"], "cli-s03b")
        self.assertNotIn("wrong-password-synthetic", bad.stderr + bad.stdout)

    def test_TST_HUB_INC07_S04_cli_error_codes_and_gate(self):
        """S04: an unknown job exits 29 E-RUN-UNKNOWN-JOB; a scheduled run with the flag off exits 29 E-RUN-SCHEDULE-DISABLED; `schedule set` with the
        SHIPPED empty holder list exits with E-GATE-NO-HOLDERS; a batching job without a cap is E-CFG-INVALID."""
        st = self.store(loaded=False, extra={"zone_h": {"holders": []}})
        env = {"HUB_RUN_PASSWORD": st.pw}
        base = ["--data-dir", st.data]
        p = cli("hub.runs", ["run", "no_such_job", "--principal", "ql"] + base, st.cfg_path, env)
        self.assertEqual((p.returncode, envelope(p)["code"]), (29, "E-RUN-UNKNOWN-JOB"))
        p = cli("hub.runs", ["run", "verify_projection", "--principal", "ql", "--trigger", "scheduled"] + base, st.cfg_path, env)
        self.assertEqual((p.returncode, envelope(p)["code"]), (29, "E-RUN-SCHEDULE-DISABLED"))
        p = cli("hub.runs", ["schedule", "set", "--enabled", "true", "--authority-ref", "X", "--principal", "holder-1"] + base, st.cfg_path, env)
        self.assertEqual((p.returncode, envelope(p)["code"]), (GE.GateNoHolders.exit_code, "E-GATE-NO-HOLDERS"))
        p = cli("hub.runs", ["run", "intake_partner_feed", "--principal", "ql"] + base, st.cfg_path, env)
        self.assertEqual(envelope(p)["code"], "E-CFG-INVALID")

    def test_TST_HUB_INC07_S05_timeliness_and_time_zone(self):
        """S05: 'finished before 06:00 local' per scheduled run; UTC is labelled Unknown; a fixed offset moves the local deadline; manual runs are not
        listed by default."""
        st = self.store(loaded=False, extra={"site": {"timezone": "+05:30"}, "schedule": {"expected": [{"job": "verify_audit", "at": "05:00"}]}})
        st.clock._t = parse("2026-10-18T04:00:00.000000Z")
        st.enable_schedule()
        st.clock._t = parse("2026-10-19T00:20:00.000000Z")  # 05:50 local
        early = st.runs.run("verify_audit", st.service_session(), trigger="scheduled", resources={"anchor_path": st.anchor_path}, correlation_id="t-s05a")
        st.clock._t = parse("2026-10-20T00:45:00.000000Z")  # 06:15 local
        late = st.runs.run("verify_audit", st.service_session(), trigger="scheduled", resources={"anchor_path": st.anchor_path}, correlation_id="t-s05b")
        st.runs.run("verify_audit", st.fresh("ql"), resources={"anchor_path": st.anchor_path}, correlation_id="t-s05c")
        rep = detector.timeliness(st.runs.list_runs(), st.runs.rs)
        self.assertEqual([(r["run_id"], r["finished_before_deadline"]) for r in rep["runs"]], [(early["run_id"], 1), (late["run_id"], 0)])
        self.assertEqual(rep["timezone"], "+05:30")
        self.assertEqual(rep["runs"][1]["deadline_local"], "2026-10-20T06:00:00")
        utc = detector.timeliness(st.runs.list_runs(), rsettings.resolve({}))
        self.assertIn("Unknown", utc["timezone_note"])
        self.assertEqual([r["finished_before_deadline"] for r in utc["runs"]], [1, 1])  # same instants, UTC clock: 00:20 and 00:45

    def test_TST_HUB_INC07_S06_text_amounts_partial_and_negative(self):
        """S06 (service-level TST-MET-12): 1 blank, 1 'abc', 1 negative among 100 rows -> the default call raises E-MET-UNPARSABLE-INPUT naming 2 rows;
        allow_partial flags the result partial with 2 errors; the negative value is summed as-is and flagged NEGATIVE_VALUE; nothing is zero-filled."""
        st = self.store(loaded=False)
        rows = [("r%03d" % i, "1.00") for i in range(97)] + [("rb", ""), ("rx", "abc"), ("rn", "-5.50")]
        src = RowsSource("vendor_rows.amount_text", rows)
        with self.assertRaises(MetUnparsableInput) as cm:
            st.met.month_end_total(CUTOFF, "fx", src)
        self.assertEqual(cm.exception.details["count"], 2)
        self.assertEqual(sorted(r["row_id"] for r in cm.exception.details["rows"]), ["rb", "rx"])
        self.assertEqual(st.con.execute("SELECT count(*) FROM metric_value").fetchone()[0], 0)
        m = st.met.month_end_total(CUTOFF, "fx", src, allow_partial=True)
        self.assertTrue(m.partial)
        self.assertEqual(sorted((e["row_id"], e["code"]) for e in m.errors), [("rb", "BLANK_AMOUNT"), ("rx", "UNPARSABLE_AMOUNT")])
        self.assertEqual((m.value, m.n), ("91.50", 98))
        self.assertEqual(m.detail["flags"], [{"row_id": "rn", "code": "NEGATIVE_VALUE"}])
        self.assertIn("PARTIAL", V.render_text(m))
        self.assertTrue(st.met.get_value(m.value_id).partial)

    def test_TST_HUB_INC07_S07_renderings_carry_tag_version_status_label_and_are_deterministic(self):
        """S07 (service-level TST-MET-02 / 21): text, JSON and CSV renderings of tagged figures carry tag, policy version, status and the label (100%);
        two computations of the same inputs give identical JSON (without computed_at) and identical inputs_hash."""
        st = self.store()
        vals = list(st.met.time_to_close()) + [st.met.backlog_by_site("D-OPS", "2025-12-19"), st.met.unresolved_exception_rate("D-OPS")]
        for v in vals:
            t, j = V.render_text(v), json.loads(V.render_json(v))
            for needle in (v.definition_tag, v.policy_version, v.policy_status, "synthetic, unvalidated"):
                self.assertIn(needle, t)
            self.assertEqual((j["definition_tag"], j["policy_version"], j["policy_status"], j["label"]),
                             (v.definition_tag, v.policy_version, v.policy_status, "synthetic, unvalidated"))
            self.assertNotIn("computed_at", j)
        import csv as csvmod
        import io
        rows = list(csvmod.reader(io.StringIO(V.render_csv(vals))))
        self.assertEqual(",".join(rows[0]), "metric_id,definition_tag,policy_version,policy_status,value,null_reason,n,partial,label")
        self.assertEqual(len(rows), 1 + len(vals))
        self.assertTrue(all(r[-1] == "synthetic, unvalidated" and r[1] and r[2] and r[3] for r in rows[1:]))
        a, b = st.met.backlog_by_site("D-OPS", "2025-12-19", store=False), st.met.backlog_by_site("D-OPS", "2025-12-19", store=False)
        self.assertEqual((V.render_json(a), a.inputs_hash), (V.render_json(b), b.inputs_hash))
        self.assertEqual(V.render_json(st.met.get_value(vals[2].value_id)), V.render_json(vals[2]))

    def test_TST_HUB_INC07_S08_triggers_and_constraints(self):
        """S08: run_event / run_lock-independent tables are insert-only (UPDATE / DELETE abort), the run sequence is gapless, a NULL metric value needs
        a reason, a synthetic value needs the label; the secret scan / deletion grep stay clean."""
        st = self.store()
        st.runs.run("verify_projection", st.sess("ql"), correlation_id="t-s08")
        st.met.time_to_close()
        st.met.registry.seed_builtin()
        collect = __import__("hub.obs.collect", fromlist=["x"])
        collect.snapshot(st.con, st.clock, collect.samples(st.con))
        for sql in ("UPDATE run_event SET job = 'x'", "DELETE FROM run_event", "UPDATE metric_value SET n = 9", "DELETE FROM metric_value",
                    "UPDATE metric_definition SET name = 'x'", "DELETE FROM metric_definition", "UPDATE obs_metric SET value = '9'", "DELETE FROM obs_metric"):
            with self.assertRaises(sqlite3.DatabaseError, msg=sql):
                st.con.execute(sql)
        st.con.rollback()
        ins = "INSERT INTO run_event(run_id, run_seq, event_type, job, trigger, triggered_by, occurred_at, body) VALUES (?,?,?,?,?,?,?,?)"
        with self.assertRaises(sqlite3.DatabaseError):
            st.con.execute(ins, ("RUN-GAP", 2, "RUN_STARTED", "verify_audit", "manual", "x", st.clock(), "{}"))
        st.con.rollback()
        cols = ("value_id, metric_id, metric_version, n, denominator, exclusions, basis, data_origin, label, inputs_hash, code_version, computed_at")
        vals = ("'MV-X', 'M', 1, 0, 'd', 'e', 'event_derived', 'synthetic', %s, 'h', 'c', 't'")
        with self.assertRaises(sqlite3.IntegrityError):  # NULL value without reason
            st.con.execute("INSERT INTO metric_value(%s) VALUES (%s)" % (cols, vals % "'synthetic, unvalidated'"))
        st.con.rollback()
        with self.assertRaises(sqlite3.IntegrityError):  # synthetic origin without the label
            st.con.execute("INSERT INTO metric_value(%s, value) VALUES (%s, '1')" % (cols, vals % "'validated'"))
        st.con.rollback()
        rep = scan.run(S.CODE_ROOT, st.con)
        self.assertEqual((rep["secret_findings"], rep["deletion_findings"], rep["clean"]), ([], [], True))

    def test_TST_HUB_INC07_S09_there_is_no_scheduler(self):
        """S09 (OD-19): no scheduler, timer, daemon thread, sleep loop, cron / systemd file or scheduling dependency exists in the INC-07 code or the
        repository; the only 'schedule' code is the Zone H flag (hub/runs/schedule.py, flag.py) and the read-only detector."""
        banned_mods = ("sched", "threading", "multiprocessing", "asyncio", "signal", "apscheduler", "celery", "schedule")
        banned_calls = ("sleep", "Timer", "Thread", "alarm", "setitimer", "daemon", "fork")
        for pkg in ("runs", "metrics", "obs"):
            for d, _, fns in os.walk(os.path.join(S.CODE_ROOT, "hub", pkg)):
                for fn in fns:
                    if not fn.endswith(".py") or fn == "metrics.py":  # obs/metrics.py (INC-01) keeps a lock for its process-local counters
                        continue
                    tree = ast.parse(open(os.path.join(d, fn), encoding="utf-8").read())
                    for n in ast.walk(tree):
                        mods = [a.name for a in n.names] if isinstance(n, ast.Import) else ([n.module or ""] if isinstance(n, ast.ImportFrom) else [])
                        for m in mods:
                            self.assertNotIn(m.split(".")[0], banned_mods, (pkg, fn, m))
                        if isinstance(n, ast.Attribute):
                            self.assertNotIn(n.attr, banned_calls, (pkg, fn))
                        if isinstance(n, ast.While) and isinstance(n.test, ast.Constant) and n.test.value is True:
                            self.fail("while True in %s/%s" % (pkg, fn))
        bad = []
        for d, dirs, fns in os.walk(S.CODE_ROOT):
            dirs[:] = [x for x in dirs if x not in (".git", "__pycache__", "data", "node_modules")]
            for fn in fns:
                if fn.endswith((".timer", ".service")) or fn in ("crontab", "cron.d") or fn.startswith("cron"):
                    bad.append(os.path.join(d, fn))
        self.assertEqual(bad, [])
        st = self.store(loaded=False)
        self.assertFalse(st.runs.schedule()["enabled"])  # fresh install: off, and enabling it starts nothing
        st.enable_schedule()
        self.assertEqual(st.runs.list_runs(), [])
        st.clock.advance(7 * 86400)
        self.assertEqual(st.runs.list_runs(), [])

    def test_TST_HUB_INC07_S10_stale_lock_heartbeat_boundary(self):
        """S10: a killed run's lock blocks a second start until the heartbeat is older than 900 s (a checkpoint refreshes it); after that the next start
        writes RUN_ABANDONED for the dead run and runs; reap_stale closes a stale run without starting one."""
        armed = [True]

        def kill(k):
            if k == 2 and armed[0]:
                armed[0] = False
                raise R.SimulatedKill()
        st = self.store(hooks={"before_checkpoint": kill})
        ql = st.sess("ql")
        with self.assertRaises(R.SimulatedKill):
            st.runs.run("intake_partner_feed", ql, batch_size=10, until_empty=True, resources=R.readers(30), correlation_id="t-s10a")
        dead = st.runs.list_runs()[0]["run_id"]
        st.clock.advance(880)
        with self.assertRaises(RunAlreadyRunning):
            st.runs.run("intake_partner_feed", ql, batch_size=10, until_empty=True, resources=R.readers(30), correlation_id="t-s10b")
        self.assertEqual(st.runs.reap_stale("t-s10c"), [])  # not stale yet
        st.clock.advance(40)
        self.assertEqual(st.runs.reap_stale("t-s10d"), [dead])
        self.assertEqual(st.con.execute("SELECT count(*) FROM run_lock").fetchone()[0], 0)
        self.assertEqual(st.runs.get_run(dead)["outcome"], "abandoned")
        self.assertTrue(st.runs.get_run(dead)["reaped"])
        rec = st.runs.run("intake_partner_feed", ql, batch_size=10, until_empty=True, resources=R.readers(30), correlation_id="t-s10e")
        self.assertEqual((rec["outcome"], rec["backlog_remaining"], st.raw_digest()), ("finished", 0, (30, 30)))
        self.assertEqual(st.audit_actions("RUN_ABANDONED")[0]["actor_kind"], "system")

    def test_TST_HUB_INC07_S11_every_catalogue_job_runs(self):
        """S11: every job of the closed catalogue has an implementation and runs; multi-source backfill keeps one order key per source; totals
        reconcile for every intake job; metrics_snapshot stores the parameter-free KPIs."""
        self.assertEqual(sorted(jobs_mod.IMPLEMENTATIONS), sorted(catalogue.JOBS))
        st = self.store()
        ql, res = st.sess("ql"), {"anchor_path": st.anchor_path}
        rs = R.rsources
        rdr = dict((n, rs.OrderedSource(n, I.batch(3, i * 10))) for i, n in enumerate(("partner_feed", "gateway", "source_message", "vendor_csv")))
        for job in ("intake_gateway", "intake_source_messages", "intake_vendor_csv"):
            rec = st.runs.run(job, ql, batch_size=10, resources=dict(res, readers=rdr), correlation_id="t-s11")
            self.assertEqual((rec["outcome"], rec["inputs_seen"], sum(rec["outcomes_by_type"].values())), ("finished", 3, 3), job)
        rec = st.runs.run("backfill_legacy", ql, batch_size=2, until_empty=True, resources=dict(res, readers=rdr), correlation_id="t-s11b")
        self.assertEqual(sorted(rec["checkpoint"]["order_keys"]), ["gateway", "partner_feed", "source_message"])
        self.assertEqual((rec["inputs_seen"], rec["backlog_remaining"], rec["errors"]), (9, 0, []))
        for job in ("verify_audit", "verify_projection", "rebuild_projection"):
            self.assertEqual(st.runs.run(job, ql, resources=res, correlation_id="t-s11c")["outcome"], "finished", job)
        snap = st.runs.run("metrics_snapshot", ql, resources=res, correlation_id="t-s11d")
        self.assertEqual(snap["outcome"], "finished")
        self.assertGreaterEqual(st.con.execute("SELECT count(*) FROM metric_value").fetchone()[0], 4)
        self.assertGreater(st.con.execute("SELECT count(*) FROM obs_metric").fetchone()[0], 0)
        part = st.runs.run("intake_partner_feed", ql, batch_size=10, resources={"readers": {}}, correlation_id="t-s11e")
        self.assertEqual([e["code"] for e in part["errors"]], ["SOURCE_NOT_CONFIGURED"])

    def test_TST_HUB_INC07_S12_unresolved_exception_rate(self):
        """S12: no exception-queue item -> null with a reason (never 0); after four invalid deliveries every item is open -> 1.0000; the value
        reproduces; the formula is stated in the detail."""
        st = self.store()
        m0 = st.met.unresolved_exception_rate("D-OPS")
        self.assertEqual((m0.value, m0.null_reason, m0.n), (None, "no_exception_queue_items", 0))
        st.isvc.ingest("partner_feed", [I.feed(i, payload_text="not json at all") for i in range(4)] + I.batch(3, 50), "s12", "t-s12")
        m = st.met.unresolved_exception_rate("D-OPS")
        self.assertEqual((m.n, m.detail["open"], m.detail["all"]), (m.detail["all"], m.detail["open"], m.detail["all"]))
        self.assertGreaterEqual(m.detail["all"], 4)
        self.assertEqual(m.value, format(__import__("decimal").Decimal(m.detail["open"]) / __import__("decimal").Decimal(m.detail["all"]), ".4f"))
        self.assertIn("formula", m.detail)
        self.assertTrue(st.met.reproduce(m.value_id)["equal"])

    def test_TST_HUB_INC07_S13_error_codes(self):
        """S13: INC-07 error codes: E-RUN-* exit 29, E-MET-* exit 30, codes start with their family prefix, unique except the deliberately shared
        unknown-job / unknown-run code; every class has a message."""
        def classes(mod):
            return [c for c in vars(mod).values() if isinstance(c, type) and issubclass(c, HubError) and c is not HubError and c.__module__ == mod.__name__]
        runs, mets = classes(run_errors), classes(met_errors)
        self.assertEqual(len(runs), 6)
        self.assertEqual(len(mets), 9)
        self.assertTrue(all(c.code.startswith("E-RUN-") and c.exit_code == 29 and c.message for c in runs))
        self.assertTrue(all(c.code.startswith("E-MET-") and c.exit_code == 30 and c.message for c in mets))
        self.assertEqual(len(set(c.code for c in mets)), 9)
        self.assertEqual(sorted(c.code for c in runs).count("E-RUN-UNKNOWN-JOB"), 2)
        self.assertEqual(len(set(c.code for c in runs)), 5)

    def test_TST_HUB_INC07_S14_purity_and_deny_list(self):
        """S14: the dependency / import deny-list (ADR-002) finds nothing in the INC-07 code; hub/runs, hub/metrics and hub/obs import no network,
        random, secrets or time module (the clock is injected); hub/obs also imports no datetime; no dependency file changed."""
        paths = [os.path.join(S.CODE_ROOT, "hub", p) for p in ("runs", "metrics", "obs")] + [os.path.join(S.CODE_ROOT, "tests", "hub")]
        self.assertEqual(no_ai.scan(paths), [])
        banned = ("socket", "urllib", "http", "random", "secrets", "time", "requests", "ssl", "ftplib", "smtplib")
        for pkg in ("runs", "metrics", "obs"):
            for d, _, fns in os.walk(os.path.join(S.CODE_ROOT, "hub", pkg)):
                for fn in fns:
                    if not fn.endswith(".py"):
                        continue
                    tree = ast.parse(open(os.path.join(d, fn), encoding="utf-8").read())
                    for n in ast.walk(tree):
                        mods = [a.name for a in n.names] if isinstance(n, ast.Import) else ([n.module or ""] if isinstance(n, ast.ImportFrom) else [])
                        for m in mods:
                            self.assertNotIn(m.split(".")[0], banned, (pkg, fn, m))
                            if pkg == "obs":
                                self.assertNotEqual(m.split(".")[0], "datetime", (pkg, fn))
        for name in ("pyproject.toml", "requirements.txt", "package.json"):
            self.assertFalse(os.path.exists(os.path.join(S.CODE_ROOT, "hub", name)))

    def test_TST_HUB_INC07_S15_settings_validation(self):
        """S15: run / schedule / site settings are validated: the schedule cannot be switched on by configuration; the batch size is never defaulted;
        bad values are E-CFG-INVALID."""
        d = rsettings.resolve({})
        self.assertEqual((d["schedule"]["enabled"], d["runs"]["batch_size"], d["runs"]["heartbeat_stale_seconds"], d["site"]["timezone"]),
                         (False, None, 900, "UTC"))
        for bad in ({"schedule": {"enabled": True}}, {"schedule": {"expected": [{"job": "nope", "at": "02:00"}]}},
                    {"schedule": {"expected": [{"job": "verify_audit", "at": "2:00"}]}}, {"schedule": {"grace_minutes": 0}},
                    {"runs": {"batch_size": 0}}, {"runs": {"batch_size": "10"}}, {"runs": {"batch_size": True}}, {"runs": {"heartbeat_stale_seconds": -1}},
                    {"site": {"timezone": "Europe/Berlin"}}, {"site": {"timezone": "+25:00"}}, {"runs": {"unknown_key": 1}}, {"schedule": []}):
            with self.assertRaises(ConfigInvalid, msg=str(bad)):
                rsettings.resolve(bad)
        ok = rsettings.resolve({"runs": {"batch_size": 500}, "site": {"timezone": "-03:30"}, "schedule": {"expected": [{"job": "verify_audit", "at": "23:59"}]}})
        self.assertEqual((ok["runs"]["batch_size"], rsettings.tz_offset_minutes(ok["site"]["timezone"])), (500, -210))

    def test_TST_HUB_INC07_S16_schedule_flag_both_ways(self):
        """S16: ZH-09 switches the flag on and off (two SCHEDULE_CHANGED policy events with the holder-check audit reference); after disabling, a
        scheduled trigger is refused again; manual runs never depend on the flag."""
        st = self.store(loaded=False)
        self.assertEqual(st.runs.run("verify_projection", st.sess("ql"), correlation_id="t-s16a")["trigger"], "manual")
        st.enable_schedule()
        self.assertEqual(st.runs.run("verify_projection", st.service_session(), trigger="scheduled", correlation_id="t-s16b")["trigger"], "scheduled")
        off = st.sched.set_enabled(st.fresh("holder-2"), False, R.AUTH, "t-s16c")
        self.assertFalse(off["enabled"])
        with self.assertRaises(R.RunScheduleDisabled if hasattr(R, "RunScheduleDisabled") else run_errors.RunScheduleDisabled):
            st.runs.run("verify_projection", st.service_session(), trigger="scheduled", correlation_id="t-s16d")
        ev = st.con.execute("SELECT actor, new_value FROM policy_events WHERE event_type = 'SCHEDULE_CHANGED' ORDER BY rowid").fetchall()
        self.assertEqual([e[0] for e in ev], ["holder-1", "holder-2"])
        self.assertEqual(st.runs.run("verify_projection", st.sess("ql"), correlation_id="t-s16e")["outcome"], "finished")

    def test_TST_HUB_INC07_S17_shipped_configuration(self):
        """S17: the SHIPPED example configuration keeps zone_h.holders EMPTY and ships no schedule, no run cap and no expected runs; a fresh store has
        the schedule flag off."""
        found = []
        for d, dirs, fns in os.walk(S.CODE_ROOT):
            dirs[:] = [x for x in dirs if x not in (".git", "__pycache__", "data", "tmp", "node_modules")]
            for fn in fns:
                if fn.startswith("hub-config") and fn.endswith(".json") and "schema" not in fn:
                    found.append(os.path.join(d, fn))
        self.assertTrue(found)
        for p in found:
            cfg = json.load(open(p, encoding="utf-8"))
            self.assertEqual(cfg.get("zone_h", {}).get("holders", []), [], p)
            self.assertEqual(cfg.get("schedule", {"enabled": False}), {"enabled": False}, p)
            self.assertNotIn("batch_size", cfg.get("runs", {}), p)


    def test_TST_HUB_INC07_S18_rollback_rehearsal_m005(self):
        """S18 (rehearsal of rollback-rehearsal-inc07.md): pre-M005 backup -> apply M005 -> runs and a metric snapshot -> restore the backup (L2) ->
        checksum matches, audit chain verifies, run / metric tables gone, decision record unchanged -> roll forward -> runs work again."""
        from hub.metrics.service import MetricsService
        from hub.ops import backup
        from hub.runs.service import RunService
        from hub.security import audit
        ds = I.IStore(loaded=True)
        base_events = ds.con.execute("SELECT count(*) FROM decision_events").fetchone()[0]
        ds.close()
        bk_root = os.path.join(ds.base, "rehearsal-backups")

        def connect():
            con = sqlite3.connect(os.path.join(ds.data, "hub.sqlite3"))
            con.execute("PRAGMA foreign_keys = ON")
            return con
        res = rschema.apply(ds.data, bk_root, ds.anchor_path, ds.clock, "s18-apply")
        self.assertTrue(res["applied"])
        bk = res["backup"]
        pre = backup.verify_backup(bk["path"])
        self.assertNotIn("run_event", json.dumps(pre["schema_versions"]))
        con = connect()
        sess = ds.authn.__class__(con, ds.s, ds.clock, ds.anchor)
        sess = sess.authenticate(ds.tokens["ql"], "s18")
        rec = RunService(con, ds.s, ds.clock, ds.anchor, ds.cfg).run("verify_projection", sess, correlation_id="s18")
        MetricsService(con, ds.s, ds.clock, ds.anchor, ds.cfg).time_to_close()
        self.assertEqual(rec["outcome"], "finished")
        audit.write_anchor(con, ds.anchor_path)
        head_after = audit.head(con)
        con.close()
        rest = backup.restore(bk["path"], ds.data, ds.anchor_path, ds.clock)
        self.assertTrue(rest["checksum_match"])
        self.assertEqual(rest["restored"], pre["files"])
        self.assertIn("hub.sqlite3", rest["set_aside"])
        con = connect()
        try:
            names = set(r[0] for r in con.execute("SELECT name FROM sqlite_master"))
            self.assertFalse(names & {"run_event", "run_lock", "metric_definition", "metric_value", "obs_metric", "runs_schema_migrations"})
            self.assertEqual(con.execute("SELECT count(*) FROM decision_events").fetchone()[0], base_events)
            self.assertEqual(audit.verify(con, ds.anchor_path)["status"], "ok")
            self.assertLess(audit.head(con)[0], head_after[0])
        finally:
            con.close()
        self.assertTrue(rschema.apply(ds.data, bk_root, ds.anchor_path, ds.clock, "s18-apply2")["applied"])
        con = connect()
        try:
            sess = ds.authn.__class__(con, ds.s, ds.clock, ds.anchor).authenticate(ds.tokens["ql"], "s18b")
            again = RunService(con, ds.s, ds.clock, ds.anchor, ds.cfg).run("verify_projection", sess, correlation_id="s18b")
            self.assertEqual(again["outcome"], "finished")
            self.assertEqual(con.execute("SELECT count(DISTINCT run_id) FROM run_event").fetchone()[0], 1)
            self.assertEqual(audit.verify(con, ds.anchor_path)["status"], "ok")
        finally:
            con.close()


    def test_TST_HUB_INC07_S19_shipped_sources_through_a_capped_run(self):
        """S19: the shipped legacy streams (hash-gated snapshot, FX-BASE125) are ordered OrderedSources of 8,567 / 15 / 1 items and the 2,400-row tiny
        vendor CSV; one capped run takes exactly the cap and reports the exact remaining backlog; the next run continues without overlap."""
        from hub.adapters import intake_sources
        st = self.store()
        h = R.D.legacy_handle("p7s19-")
        try:
            readers = rsources.legacy_sources(h)
        finally:
            h.close()
        self.assertEqual(dict((k, len(v.items)) for k, v in readers.items()), {"partner_feed": 8567, "source_message": 15, "gateway": 1})
        vend, sha = rsources.vendor_csv_source(intake_sources.csv_path(S.LEGACY_ROOT, "tiny"))
        self.assertEqual(len(vend.items), 2400)
        self.assertRegex(sha, r"^[0-9a-f]{64}$")
        r1 = st.runs.run("intake_partner_feed", st.sess("ql"), batch_size=200, resources={"readers": readers}, correlation_id="t-s19a")
        self.assertEqual((r1["inputs_seen"], r1["limit_reached"], r1["backlog_remaining"]), (200, True, 8367))
        r2 = st.runs.run("intake_partner_feed", st.sess("ql"), batch_size=200, resources={"readers": readers}, correlation_id="t-s19b")
        self.assertEqual((r2["inputs_seen"], r2["backlog_remaining"]), (200, 8167))
        self.assertEqual(st.raw_digest()[0], 400)
        self.assertEqual(st.con.execute("SELECT count(*), count(DISTINCT raw_id) FROM intake_outcome").fetchone(), (400, 400))
        self.assertEqual(sum(r2["outcomes_by_type"].values()), 200)


if __name__ == "__main__":
    unittest.main()
