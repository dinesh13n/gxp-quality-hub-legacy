"""RunService: run orchestration and append-only run records (C8, F06, ADR-010, FR-RUN-01..03; INC-07).

* A run is a sequence of insert-only `run_event` rows: RUN_STARTED (written, with the lock, BEFORE any work), RUN_CHECKPOINT (after each
  batch), then exactly one of RUN_FINISHED / RUN_FAILED; RUN_REFUSED is a one-event run; RUN_ABANDONED closes a run whose process died
  (stale heartbeat) and is written by the NEXT invocation of the same job (or `reap_stale`). The run record is a fold of those rows.
* Single flight (BEH-RUN-06): one `run_lock` row per job with a heartbeat; a second start gets E-RUN-ALREADY-RUNNING and a refused record.
* No silent cap (BEH-RUN-05): the cap is batch_size from configuration or --batch-size, never a constant; limit_reached / backlog_remaining
  are exact and the checkpoint resumes the next run; --until-empty loops until the backlog is 0 inside one run.
* Resume is idempotent (BEH-RUN-07): batches are ingested with the legacy-backfill rule (skip a delivery already stored with the same source
  key and content hash), so a kill between a committed batch and its checkpoint row cannot create duplicates.
* Totals reconcile (BEH-RUN-04): for intake jobs sum(outcomes_by_type) must equal the intake_outcome rows of the run's batch ids.
* Every run start and every terminal event is ONE transaction with ONE hash-chained audit record; the three zero-tripwires are exported to
  obs_metric at every run end (BEH-OBS-06).
* Authority: manual and scheduled triggers need a session with role quality_lead, compliance or integration (BEH-RUN-01). The scheduled
  trigger is accepted only while the ZH-09 flag is on. There is no scheduler anywhere in this package (OD-19).
No import of hub.gate here or in hub.runs.jobs (AC-RUN-12).
"""
import json

from hub.core.errors import ConfigInvalid, HubError
from hub.obs import collect
from hub.runs import CODE_VERSION, catalogue, jobs as jobs_mod, schema, settings as rsettings
from hub.runs.errors import (RunAlreadyRunning, RunCheckpointInvalid, RunNotFound, RunScheduleDisabled, RunTotalsMismatch,
                             RunUnknownJob)
from hub.runs.flag import schedule_state
from hub.runs.sources import valid_key
from hub.security import audit, settings as sec_settings
from hub.security.canonical import canonical, parse
from hub.security.errors import AuthForbidden, AuthUnauthenticated

TERMINAL = ("RUN_FINISHED", "RUN_FAILED", "RUN_ABANDONED", "RUN_REFUSED")
_OUTCOME = {"RUN_FINISHED": "finished", "RUN_FAILED": "failed", "RUN_ABANDONED": "abandoned", "RUN_REFUSED": "refused"}
RECORD_FIELDS = ("run_id", "job", "trigger", "triggered_by", "started_at", "ended_at", "outcome", "inputs_seen", "outcomes_by_type",
                 "errors", "limit_reached", "batch_size", "backlog_remaining", "checkpoint", "config_version", "code_version")


class _Lost(Exception):
    """Internal: another run of the job holds a fresh lock (the start transaction is rolled back, then the refusal is recorded)."""


class JobContext(object):
    """What a job sees: the connection, settings, the run id, its cap and checkpoint, and `checkpoint_save`. No session, no gate."""

    def __init__(self, svc, run_id, job, trigger, batch_size, until_empty, checkpoint, cid, res):
        self.con, self.s, self.clock, self.anchor, self.cfg = svc.con, svc.s, svc.clock, svc.anchor, svc.cfg
        self.run_id, self.job, self.trigger, self.batch_size, self.until_empty = run_id, job, trigger, batch_size, until_empty
        self.checkpoint, self.cid, self.res, self._svc, self._k = checkpoint, cid, res, svc, 0

    def checkpoint_save(self, checkpoint, inputs_seen, outcomes_by_type, backlog_remaining):
        self._k += 1
        self._svc._hook("before_checkpoint", self._k)
        self._svc._write_checkpoint(self.run_id, checkpoint, inputs_seen, outcomes_by_type, backlog_remaining, self._k)
        self._svc._hook("after_checkpoint", self._k)


class RunService(object):
    def __init__(self, con, settings, clock, anchor=None, cfg=None, hooks=None):
        """settings: hub security settings (hub.security.settings.resolve); cfg: the loaded hub config dict; hooks: TEST SEAM only
        ({'after_start'|'before_checkpoint'|'after_checkpoint': callable}), used to simulate a killed process / a concurrent start."""
        self.con, self.s, self.clock, self.anchor, self.cfg = con, settings, clock, anchor, cfg or {}
        self.rs = rsettings.resolve(self.cfg)
        self.config_version = sec_settings.config_hash(self.cfg)
        self.hooks = hooks or {}
        schema.require(con)

    # ---------------------------------------------------------------- helpers
    def _hook(self, name, *a):
        fn = self.hooks.get(name)
        if fn is not None:
            fn(*a)

    def _stale(self, heartbeat_at):
        return parse(self.clock()).timestamp() - parse(heartbeat_at).timestamp() > self.rs["runs"]["heartbeat_stale_seconds"]

    def _new_id(self):
        return "RUN-%08d" % (self.con.execute("SELECT count(DISTINCT run_id) FROM run_event").fetchone()[0] + 1)

    def _seq(self, run_id):
        return self.con.execute("SELECT COALESCE(MAX(run_seq), 0) + 1 FROM run_event WHERE run_id = ?", (run_id,)).fetchone()[0]

    def _insert(self, run_id, etype, job, trigger, by, body):
        self.con.execute("INSERT INTO run_event(run_id, run_seq, event_type, job, trigger, triggered_by, occurred_at, body) VALUES (?,?,?,?,?,?,?,?)",
                         (run_id, self._seq(run_id), etype, job, trigger, by, self.clock(), canonical(body)))

    def _authorise(self, sess, cid):
        if sess is None:
            raise AuthUnauthenticated()
        p = sess.principal
        if not any(r in p.roles for r in catalogue.RUN_ROLES):
            audit.append(self.con, self.clock, anchor=self.anchor, actor=p.principal_id, actor_kind=p.actor_kind, action="AUTHZ_DENIED",
                         outcome="denied", correlation_id=cid, object_ref="OP-RUN-01",
                         details={"reason": "role", "needs_one_of": list(catalogue.RUN_ROLES)})
            raise AuthForbidden({"reason": "role"})
        return p

    def _base_body(self, batch_size):
        return {"batch_size": batch_size, "config_version": self.config_version, "code_version": CODE_VERSION}

    def _refuse(self, job, trigger, p, err_cls, details, cid, batch_size=None):
        with audit.change(self.con, self.clock, anchor=self.anchor, actor=p.principal_id, actor_kind=p.actor_kind, action="RUN_REFUSED",
                          outcome="denied", correlation_id=cid, object_ref="job:" + job, details={}) as ctx:
            rid = self._new_id()
            body = dict(self._base_body(batch_size), error=err_cls.code, details=details or {})
            self._insert(rid, "RUN_REFUSED", job, trigger, p.principal_id, body)
            ctx.fields["details"] = {"run_id": rid, "job": job, "trigger": trigger, "error": err_cls.code}
        raise err_cls(dict(details or {}, run_id=rid))

    # ---------------------------------------------------------------- checkpoints
    def last_checkpoint(self, job):
        """(checkpoint dict | None). A stored checkpoint that is not valid for the job raises E-RUN-CHECKPOINT-INVALID."""
        row = self.con.execute("SELECT body FROM run_event WHERE job = ? AND event_type = 'RUN_CHECKPOINT' ORDER BY rowid DESC LIMIT 1", (job,)).fetchone()
        if row is None:
            return None
        try:
            cp = json.loads(row[0]).get("checkpoint")
        except (ValueError, AttributeError):
            raise RunCheckpointInvalid({"job": job, "reason": "not JSON"})
        ok = isinstance(cp, dict) and sorted(cp) == ["order_keys"] and isinstance(cp["order_keys"], dict) and all(
            k in catalogue.INTAKE_JOBS.get(job, ()) for k in cp["order_keys"]) and all(
            valid_key(v) for v in cp["order_keys"].values())
        if not ok:
            raise RunCheckpointInvalid({"job": job, "reason": "unknown or malformed checkpoint"})
        return cp

    def _write_checkpoint(self, run_id, checkpoint, inputs_seen, outcomes_by_type, backlog_remaining, k):
        r = self.con.execute("SELECT job, trigger, triggered_by FROM run_event WHERE run_id = ? AND run_seq = 1", (run_id,)).fetchone()
        self.con.execute("BEGIN IMMEDIATE")
        try:
            self._insert(run_id, "RUN_CHECKPOINT", r[0], r[1], r[2],
                         {"checkpoint": checkpoint, "inputs_seen": inputs_seen, "outcomes_by_type": dict(sorted(outcomes_by_type.items())),
                          "backlog_remaining": backlog_remaining, "batch": k})
            self.con.execute("UPDATE run_lock SET heartbeat_at = ? WHERE run_id = ?", (self.clock(), run_id))
            self.con.commit()
        except BaseException:
            self.con.rollback()
            raise

    # ---------------------------------------------------------------- start / run / finish
    def _abandon(self, old_id, by_run):
        first = self.con.execute("SELECT job, trigger, triggered_by FROM run_event WHERE run_id = ? AND run_seq = 1", (old_id,)).fetchone()
        done = self.con.execute("SELECT 1 FROM run_event WHERE run_id = ? AND event_type IN ('RUN_FINISHED','RUN_FAILED','RUN_ABANDONED','RUN_REFUSED')",
                                (old_id,)).fetchone()
        if first is None or done:
            return None
        self._insert(old_id, "RUN_ABANDONED", first[0], first[1], first[2],
                     {"reason": "stale heartbeat", "info": "E-RUN-ABANDONED", "detected_by": by_run})
        return old_id

    def reap_stale(self, correlation_id="run-reap"):
        """Close every run whose lock heartbeat is stale (writes RUN_ABANDONED, releases the lock). Returns the abandoned run ids."""
        out = []
        for job, rid, hb in self.con.execute("SELECT job, run_id, heartbeat_at FROM run_lock ORDER BY job").fetchall():
            if not self._stale(hb):
                continue
            with audit.change(self.con, self.clock, anchor=self.anchor, actor="hub", actor_kind="system", action="RUN_ABANDONED",
                              outcome="error", correlation_id=correlation_id, object_ref="job:" + job, details={}) as ctx:
                got = self._abandon(rid, "reap")
                self.con.execute("DELETE FROM run_lock WHERE job = ? AND run_id = ?", (job, rid))
                ctx.fields["details"] = {"run_id": rid, "job": job, "abandoned": bool(got)}
            if got:
                out.append(rid)
        return out

    def run(self, job, sess, trigger="manual", batch_size=None, until_empty=False, resources=None, correlation_id="run"):
        """Start and execute one run; returns the final run record. Errors raised AFTER a record exists leave RUN_FAILED / RUN_REFUSED."""
        if job not in catalogue.JOBS:
            raise RunUnknownJob({"job": str(job)[:60], "catalogue": list(catalogue.JOBS)})
        if trigger not in catalogue.TRIGGERS:
            raise ConfigInvalid({"trigger": str(trigger)[:20], "allowed": list(catalogue.TRIGGERS)})
        p = self._authorise(sess, correlation_id)
        batching = job in catalogue.INTAKE_JOBS
        bs = batch_size if batch_size is not None else self.rs["runs"]["batch_size"]
        if batching and (isinstance(bs, bool) or not isinstance(bs, int) or bs < 1):
            raise ConfigInvalid({"runs.batch_size": bs, "reason": "a batching job needs an explicit cap (config runs.batch_size or --batch-size); there is no hidden default"})
        if not batching:
            bs = None
        if trigger == "scheduled" and not schedule_state(self.con)["enabled"]:
            self._refuse(job, trigger, p, RunScheduleDisabled, {"schedule_enabled": False}, correlation_id, bs)
        try:
            cp = self.last_checkpoint(job) if batching else None
        except RunCheckpointInvalid as e:
            self._refuse(job, trigger, p, RunCheckpointInvalid, e.details, correlation_id, bs)
        res = dict(resources or {})
        try:
            with audit.change(self.con, self.clock, anchor=self.anchor, actor=p.principal_id, actor_kind=p.actor_kind, action="RUN_STARTED",
                              outcome="success", correlation_id=correlation_id, object_ref="job:" + job, details={}) as ctx:
                rid = self._new_id()
                lock = self.con.execute("SELECT run_id, heartbeat_at FROM run_lock WHERE job = ?", (job,)).fetchone()
                abandoned = None
                if lock is not None:
                    if not self._stale(lock[1]):
                        raise _Lost()
                    abandoned = self._abandon(lock[0], rid)
                    self.con.execute("DELETE FROM run_lock WHERE job = ?", (job,))
                self._insert(rid, "RUN_STARTED", job, trigger, p.principal_id,
                             dict(self._base_body(bs), until_empty=bool(until_empty), resume_from=cp))
                now = self.clock()
                self.con.execute("INSERT INTO run_lock(job, run_id, started_at, heartbeat_at) VALUES (?,?,?,?)", (job, rid, now, now))
                ctx.fields["details"] = {"run_id": rid, "job": job, "trigger": trigger, "batch_size": bs, "abandoned_run": abandoned}
        except _Lost:
            self._refuse(job, trigger, p, RunAlreadyRunning, {"job": job, "held_by": lock[0]}, correlation_id, bs)
        self._hook("after_start", rid)
        jc = JobContext(self, rid, job, trigger, bs, bool(until_empty), cp, correlation_id, res)
        try:
            result = jobs_mod.IMPLEMENTATIONS[job](jc)
            if result.get("reconcile_intake"):
                rows = self.con.execute("SELECT count(*) FROM intake_outcome WHERE run_id >= ? AND run_id < ?",
                                        (rid + ".b", rid + ".c")).fetchone()[0]
                total = sum(result["outcomes_by_type"].values())
                if rows != total:
                    raise RunTotalsMismatch({"run_id": rid, "outcomes_by_type_total": total, "outcome_rows": rows})
        except HubError as e:
            self._finish(rid, job, trigger, p, "RUN_FAILED", bs, {"errors": [{"code": e.code, "detail": json.dumps(e.details, default=str)[:300]}]},
                         correlation_id)
            raise
        except Exception as e:
            self._finish(rid, job, trigger, p, "RUN_FAILED", bs, {"errors": [{"code": "E-HUB-INTERNAL", "detail": type(e).__name__}]},
                         correlation_id)
            raise
        body = dict((k, result[k]) for k in ("inputs_seen", "outcomes_by_type", "errors", "limit_reached", "backlog_remaining", "checkpoint"))
        body["extras"] = result.get("extras", {})
        self._finish(rid, job, trigger, p, "RUN_FINISHED", bs, body, correlation_id)
        return self.get_run(rid)

    def _finish(self, rid, job, trigger, p, etype, bs, body, cid):
        if self.con.in_transaction:
            self.con.rollback()
        full = dict(self._base_body(bs), inputs_seen=0, outcomes_by_type={}, errors=[], limit_reached=False, backlog_remaining=0, checkpoint=None)
        full.update(body)
        if full["batch_size"] is None:  # non-batching job: processed in one pass; the schema requires an integer >= 1 (DEV-67)
            full["batch_size"] = max(1, full["inputs_seen"])
        with audit.change(self.con, self.clock, anchor=self.anchor, actor=p.principal_id, actor_kind=p.actor_kind, action=etype,
                          outcome="success" if etype == "RUN_FINISHED" and not full["errors"] else "error", correlation_id=cid,
                          object_ref="job:" + job, details={}) as ctx:
            self._insert(rid, etype, job, trigger, p.principal_id, full)
            self.con.execute("DELETE FROM run_lock WHERE run_id = ?", (rid,))
            started = self.con.execute("SELECT occurred_at FROM run_event WHERE run_id = ? AND run_seq = 1", (rid,)).fetchone()[0]
            ended = self.con.execute("SELECT occurred_at FROM run_event WHERE run_id = ? AND event_type = ?", (rid, etype)).fetchone()[0]
            dur = round(parse(ended).timestamp() - parse(started).timestamp(), 6)
            collect.insert_samples(self.con, self.clock, collect.run_end_samples(self.con, job, dur, full["backlog_remaining"]), rid)
            ctx.fields["details"] = {"run_id": rid, "job": job, "trigger": trigger, "inputs_seen": full["inputs_seen"],
                                     "outcomes_by_type": full["outcomes_by_type"], "limit_reached": full["limit_reached"],
                                     "backlog_remaining": full["backlog_remaining"], "errors": [e["code"] for e in full["errors"]]}

    # ---------------------------------------------------------------- run records (reads)
    def _fold(self, rows):
        first = rows[0]
        rec = {"run_id": first[0], "job": first[2], "trigger": first[3], "triggered_by": first[4], "started_at": first[5], "ended_at": None,
               "outcome": "running", "inputs_seen": 0, "outcomes_by_type": {}, "errors": [], "limit_reached": False, "batch_size": None,
               "backlog_remaining": 0, "checkpoint": None, "config_version": None, "code_version": None, "reaped": None,
               "duration_seconds": None}
        hb = first[5]
        for (rid, seq, job, trig, by, occ, etype, body) in [(r[0], r[1], r[2], r[3], r[4], r[5], r[6], json.loads(r[7])) for r in rows]:
            if etype == "RUN_STARTED":
                for k in ("batch_size", "config_version", "code_version"):
                    rec[k] = body.get(k)
            elif etype == "RUN_CHECKPOINT":
                hb = occ
                for k in ("inputs_seen", "outcomes_by_type", "backlog_remaining"):
                    rec[k] = body[k]
                rec["checkpoint"] = body["checkpoint"]
            elif etype in TERMINAL:
                rec["outcome"], rec["ended_at"] = _OUTCOME[etype], occ
                for k in ("inputs_seen", "outcomes_by_type", "errors", "limit_reached", "backlog_remaining", "checkpoint", "batch_size",
                          "config_version", "code_version"):
                    if k in body:
                        rec[k] = body[k]
                if etype == "RUN_ABANDONED":
                    rec["errors"] = [{"code": "E-RUN-ABANDONED", "detail": body.get("reason", "")}]
                    rec["reaped"] = True
                if etype == "RUN_REFUSED":
                    rec["started_at"] = occ
                    rec["errors"] = [{"code": body.get("error", "")}]
        if rec["ended_at"]:
            rec["duration_seconds"] = round(parse(rec["ended_at"]).timestamp() - parse(rec["started_at"]).timestamp(), 6)
        elif self._stale(hb):
            lock = self.con.execute("SELECT heartbeat_at FROM run_lock WHERE run_id = ?", (rec["run_id"],)).fetchone()
            if lock is None or self._stale(lock[0]):
                rec["outcome"], rec["reaped"] = "abandoned", False  # stale; the RUN_ABANDONED row is written by the next invocation / reap
        return rec

    def _rows(self, where="", args=()):
        return self.con.execute("SELECT run_id, run_seq, job, trigger, triggered_by, occurred_at, event_type, body FROM run_event" + where +
                                " ORDER BY run_id, run_seq", args).fetchall()

    def list_runs(self, job=None):
        rows = self._rows(" WHERE job = ?", (job,)) if job else self._rows()
        out, cur, buf = [], None, []
        for r in rows:
            if r[0] != cur:
                if buf:
                    out.append(self._fold(buf))
                cur, buf = r[0], []
            buf.append(r)
        if buf:
            out.append(self._fold(buf))
        return out

    def get_run(self, run_id, with_events=False):
        rows = self._rows(" WHERE run_id = ?", (run_id,))
        if not rows:
            raise RunNotFound({"run_id": str(run_id)[:40]})
        rec = self._fold(rows)
        if with_events:
            rec["events"] = [{"run_seq": r[1], "event_type": r[6], "occurred_at": r[5], "body": json.loads(r[7])} for r in rows]
        return rec

    def schedule(self):
        return schedule_state(self.con)

    @staticmethod
    def to_schema(rec):
        """The run record exactly as run-record.schema.json describes it (no report-only fields)."""
        return dict((k, rec[k]) for k in RECORD_FIELDS if not (k == "ended_at" and rec[k] is None))
