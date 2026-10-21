"""MetricsService: deterministic metric computation from stored rows, definition tags, stored values, reproduction (C9, F07, ADR-011; INC-07).

Every metric function returns MetricValue objects carrying tag, policy version / status, window, denominator, exclusions, n, basis, inputs_hash, code
version, computed_at and the label 'synthetic, unvalidated'. Stored values (`metric_value`, insert-only) keep their parameters and inputs, so
`reproduce` can recompute them: event-derived metrics are bounded by `recorded_until` (rows added later are ignored), the month-end total re-reads
exactly the stored row ids. No adopted definition, clock duration or cut-off ships: verdicts stay `not_available_no_adopted_policy`; the month-end
total has no default cut-off (E-MET-CUTOFF-REQUIRED); backlog by site implements the state-based D-OPS definition only (DEV-69).
Money is Decimal(repr(float)) summed exactly and quantised to 2 decimals ROUND_HALF_EVEN at presentation only (assumed currency minor unit 2).
"""
import decimal
import json

from hub.decision import settings as dsettings
from hub.decision.service import DecisionService, norm_ts
from hub.metrics import values as V
from hub.metrics.errors import (MetCutoffRequired, MetDefinitionRequired, MetNotAvailable, MetNotReproducible, MetSourceRefused,
                                MetUnknownMetric, MetUnparsableInput)
from hub.metrics.registry import BUILTIN, NEEDS_PARAMS, Registry
from hub.metrics.sources import ALLOWED, parse_amount
from hub.policy import clocks, withdrawal
from hub.policy.service import PolicyService
from hub.runs import CODE_VERSION, schema
from hub.security.canonical import canonical, parse, sha256_hex

D = decimal.Decimal
BUCKETS = ("<=90", "91-365", "366-730", ">730")
BACKLOG_TAG = "D-OPS"
RATE_PLACES = D("0.0001")
MONEY_PLACES = D("0.01")


def _bucket(days):
    return BUCKETS[0] if days <= 90 else (BUCKETS[1] if days <= 365 else (BUCKETS[2] if days <= 730 else BUCKETS[3]))


def _as_of(value):
    """Date-only -> end of that day (the K-09-OPS baseline counts the cases created on the as_of day); otherwise a normal timestamp."""
    if isinstance(value, str) and len(value) == 10:
        return norm_ts(value + "T23:59:59.999999Z", "as_of")
    return norm_ts(value, "as_of")


class MetricsService(object):
    def __init__(self, con, settings, clock, anchor=None, cfg=None):
        self.con, self.s, self.clock, self.anchor, self.cfg = con, settings, clock, anchor, cfg or {}
        schema.require(con)
        self.policy = PolicyService(con, settings, clock, anchor)
        self.decision = DecisionService(con, settings, clock, anchor, dsettings.resolve(self.cfg))
        self.registry = Registry(con, clock)
        self.data_origin = self.cfg.get("data_origin", "synthetic")

    # ---------------------------------------------------------------- plumbing
    def _label(self):
        return V.LABEL if self.data_origin == "synthetic" else ""

    def _mv(self, metric_id, **kw):
        try:
            d = self.registry.get(metric_id)
        except MetUnknownMetric:
            if metric_id not in set(b["metric_id"] for b in BUILTIN):
                raise
            self.registry.seed_builtin()  # the built-in KPI definitions are registered on first use (insert-only catalogue rows)
            d = self.registry.get(metric_id)
        base = dict(metric_version=d["version"], definition_tag=d["definition_tag"], denominator=d["denominator"], exclusions=d["exclusions"],
                    basis=d["basis"], data_origin=self.data_origin, label=self._label(), code_version=CODE_VERSION)
        base.update(kw)
        pref, at = base.get("policy_version"), base.get("computed_at")
        if pref and at and base.get("policy_status") == "adopted":  # Stage 20 DW-07: the value shows a withdrawal in effect at computed_at
            w = withdrawal.effective(self.con, pref, at)
            if w:
                base["detail"] = dict(base.get("detail") or {}, policy_withdrawal={"event_id": w["event_id"], "withdrawn_from": w["withdrawn_from"]})
        return V.MetricValue(metric_id, **base)

    def _store(self, mv):
        self.con.execute("BEGIN IMMEDIATE")
        try:
            mv.value_id = "MV-%08d" % (self.con.execute("SELECT count(*) FROM metric_value").fetchone()[0] + 1)
            self.con.execute(
                "INSERT INTO metric_value(value_id, metric_id, metric_version, definition_tag, policy_version, value, n, partial, window_start,"
                " window_end, denominator, exclusions, basis, data_origin, label, inputs_hash, code_version, computed_at, null_reason, policy_status,"
                " errors, params, inputs, detail) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (mv.value_id, mv.metric_id, mv.metric_version, mv.definition_tag, mv.policy_version, mv.value, mv.n, int(mv.partial),
                 mv.window_start, mv.window_end, mv.denominator, mv.exclusions, mv.basis, mv.data_origin, mv.label, mv.inputs_hash,
                 mv.code_version, mv.computed_at, mv.null_reason, mv.policy_status, canonical(mv.errors), canonical(mv.params),
                 canonical(mv.inputs), canonical(mv.detail)))
            self.con.commit()
        except BaseException:
            self.con.rollback()
            raise
        return mv

    def _load(self, row):
        c = ["value_id", "metric_id", "metric_version", "definition_tag", "policy_version", "value", "n", "partial", "window_start", "window_end",
             "denominator", "exclusions", "basis", "data_origin", "label", "inputs_hash", "code_version", "computed_at", "null_reason",
             "policy_status", "errors", "params", "inputs", "detail"]
        d = dict(zip(c, row))
        for k in ("errors", "params", "inputs", "detail"):
            d[k] = json.loads(d[k])
        d["partial"] = bool(d["partial"])
        return V.MetricValue(**d)

    def get_value(self, value_id):
        row = self.con.execute("SELECT value_id, metric_id, metric_version, definition_tag, policy_version, value, n, partial, window_start,"
                               " window_end, denominator, exclusions, basis, data_origin, label, inputs_hash, code_version, computed_at,"
                               " null_reason, policy_status, errors, params, inputs, detail FROM metric_value WHERE value_id = ?", (value_id,)).fetchone()
        if row is None:
            raise MetUnknownMetric({"value_id": str(value_id)[:40]})
        return self._load(row)

    def values_for(self, metric_id):
        rows = self.con.execute("SELECT value_id FROM metric_value WHERE metric_id = ? ORDER BY rowid", (metric_id,)).fetchall()
        return [self.get_value(r[0]) for r in rows]

    def _tag_policy(self, tag, kind=None):
        if not isinstance(tag, str) or not tag.strip():
            raise MetDefinitionRequired({"reason": "a definition tag is required"})
        for p in self.policy.list_policies(kind=kind, latest_only=True):
            if p["definition_tag"] == tag:
                return p
        raise MetDefinitionRequired({"reason": "unknown definition tag", "tag": tag[:40]})

    @staticmethod
    def _pref(p):
        return "%s@%d" % (p["policy_id"], p["version"])

    # ---------------------------------------------------------------- BEH-MET-04 time to close, per clock
    def _ensure_clock_metric(self, pol):
        mid = "MET-TTC-" + pol["policy_id"]
        try:
            self.registry.get(mid)
        except MetUnknownMetric:
            tag = pol["definition_tag"] or pol["policy_id"]
            self.registry.register({"metric_id": mid, "name": "Time to close (clock %s)" % pol["policy_id"], "category": "time", "definition_tag": tag,
                                    "window": "all completed cycles recorded", "basis": "event_derived",
                                    "denominator": "completed cycles (a start and a stop event of the clock exist in the cycle)",
                                    "exclusions": "incomplete cycles (counted as open_count); never pooled with another clock",
                                    "documentation": "Median and p90 elapsed hours between the clock's start and stop events per completed cycle."})
        return mid

    def _compute_ttc(self, pol, recorded_until, computed_at):
        body = pol["body"]
        start_t, stop_t = body["clock_start_event"], body["clock_stop_event"]
        cyc = {}
        for eid, cid, cycle, et, occ, h in self.con.execute(
                "SELECT event_id, case_id, cycle, event_type, occurred_at, hash FROM decision_events WHERE event_type IN (?,?) AND recorded_at <= ?"
                " ORDER BY case_id, seq", (start_t, stop_t, recorded_until)):
            slot = cyc.setdefault((cid, cycle), {})
            slot.setdefault("start" if et == start_t else "stop", (eid, occ, h))
        durations, inputs, open_count, invalid = [], [], 0, 0
        for key in sorted(cyc):
            s = cyc[key]
            if "start" not in s:
                continue  # a stop without a start is not a completed cycle and not an open one either
            if "stop" not in s:
                open_count += 1
                continue
            if s["stop"][1] < s["start"][1]:
                invalid += 1
                continue
            durations.append(clocks.elapsed_hours(s["start"][1], s["stop"][1]))
            inputs.append([key[0], key[1], s["start"][0], s["start"][2], s["stop"][0], s["stop"][2]])
        st = V.summarise(durations)
        detail = {"unit": "hours", "calendar_basis": body["calendar_basis"], "open_count": open_count, "invalid_order": invalid,
                  "median": None if st["median"] is None else V.dtext(st["median"]), "p90": None if st["p90"] is None else V.dtext(st["p90"]),
                  "method": V.METHOD, "clock": pol["policy_id"], "verdict": clocks.NO_POLICY if pol["status"] != "adopted" else "see policy"}
        mv = self._mv(self._ensure_clock_metric(pol), definition_tag=pol["definition_tag"] or pol["policy_id"], policy_version=self._pref(pol),
                      policy_status=pol["status"], n=st["n"], value=detail["median"], null_reason=None if durations else "no_completed_cycles",
                      window_end=recorded_until, inputs=inputs, detail=detail, inputs_hash=sha256_hex(canonical(inputs)), computed_at=computed_at,
                      params={"kind": "time", "policy_id": pol["policy_id"], "policy_version": pol["version"], "recorded_until": recorded_until})
        return mv

    def time_to_close(self, clock_ids=None, store=True):
        """One separate series per configured CLOCK policy (latest version; any status), never pooled (AC-MET-06)."""
        now = self.clock()
        out = []
        for pol in self.policy.list_policies(kind="CLOCK", latest_only=True):
            if clock_ids is not None and pol["policy_id"] not in clock_ids:
                continue
            mv = self._compute_ttc(pol, now, now)
            out.append(self._store(mv) if store else mv)
        return out

    # ---------------------------------------------------------------- BEH-MET-05/06/09 month-end total
    def _check_source(self, source):
        name = getattr(source, "name", None)
        if name is None:
            raise MetSourceRefused({"reason": "no source given", "allowed": list(ALLOWED)})
        if str(name).startswith("operating_costs"):
            raise MetSourceRefused({"source": str(name)[:60], "reason": "operating_costs.total_cases is random, not 'cases created' (OD-07, BEH-MET-09)"})
        if name not in ALLOWED:
            raise MetSourceRefused({"source": str(name)[:60], "allowed": list(ALLOWED)})
        return name

    def _compute_total(self, cutoff_ts, denominator_ref, source, allow_partial, restrict_ids, computed_at):
        t = norm_ts(cutoff_ts, "cutoff_ts")
        name = self._check_source(source)
        total, n, errors, flags, inputs = D(0), 0, [], [], []
        for row_id, raw, ts in source.read():
            if restrict_ids is not None and row_id not in restrict_ids:
                continue
            if ts is not None:
                try:
                    if norm_ts(ts, "created_at") > t:
                        continue
                except Exception:
                    errors.append({"row_id": row_id, "raw_text": str(ts)[:80], "code": "BAD_TIMESTAMP"})
                    continue
            dec, code = parse_amount(raw)
            if code:
                errors.append({"row_id": row_id, "raw_text": "" if raw is None else str(raw)[:80], "code": code})
                continue
            if dec < 0:
                flags.append({"row_id": row_id, "code": "NEGATIVE_VALUE"})
            total += dec
            n += 1
            inputs.append([row_id, sha256_hex(canonical([row_id, repr(raw)]))])
        if errors and not allow_partial:
            raise MetUnparsableInput({"rows": errors, "count": len(errors)})
        q = total.quantize(MONEY_PLACES, rounding=decimal.ROUND_HALF_EVEN)
        mv = self._mv("MET-MONTH-END-TOTAL", value=format(q, "f"), n=n, partial=bool(errors), errors=errors, window_end=t, denominator=denominator_ref,
                      exclusions="none" if not errors else "rows with errors (%d) excluded; result is PARTIAL" % len(errors),
                      inputs=inputs, inputs_hash=sha256_hex(canonical(inputs)), computed_at=computed_at,
                      detail={"source": name, "flags": flags, "currency_minor_unit": 2, "rounding": "ROUND_HALF_EVEN at presentation only"},
                      params={"kind": "month_end", "cutoff_ts": t, "denominator_ref": denominator_ref, "source": name,
                              "allow_partial": bool(allow_partial)})
        return mv

    def month_end_total(self, cutoff_ts=None, denominator_ref=None, source=None, allow_partial=False, store=True):
        """The only month-end function. cutoff_ts and denominator_ref are required parameters (no hidden default, OD-S12-08)."""
        missing = [k for k, v in (("cutoff_ts", cutoff_ts), ("denominator_ref", denominator_ref)) if not (isinstance(v, str) and v.strip())]
        if missing:
            raise MetCutoffRequired({"missing": missing})
        mv = self._compute_total(cutoff_ts, denominator_ref, source, allow_partial, None, self.clock())
        return self._store(mv) if store else mv

    # ---------------------------------------------------------------- BEH-MET-08 backlog ageing and unresolved-exception rate
    def _compute_backlog(self, tag, as_of, recorded_until, site_of, computed_at):
        pol = self._tag_policy(tag, "DEFINITION")
        if tag != BACKLOG_TAG:
            raise MetNotAvailable({"tag": tag, "reason": "only the state-based D-OPS definition is implemented; D-EVID needs the evidence check (DEV-69)"})
        closing, mode, cref = self.decision.closing_set()
        t = _as_of(as_of)
        created = dict(self.con.execute("SELECT case_id, MIN(occurred_at) FROM decision_events WHERE event_type IN ('CASE_CREATED','CASE_IMPORTED')"
                                        " AND recorded_at <= ? GROUP BY case_id", (recorded_until,)))
        states = dict(self.con.execute(
            "SELECT d.case_id, d.to_state FROM decision_events d WHERE d.affects_state = 1 AND d.occurred_at <= ? AND d.recorded_at <= ? AND d.seq ="
            " (SELECT MAX(x.seq) FROM decision_events x WHERE x.case_id = d.case_id AND x.affects_state = 1 AND x.occurred_at <= ? AND x.recorded_at <= ?)",
            (t, recorded_until, t, recorded_until)))
        sites, inputs, backlog = {}, [], 0
        tnow = parse(t).timestamp()
        for cid in sorted(states):
            site = (site_of or {}).get(cid, "unknown")
            b = sites.setdefault(site, {"backlog": 0, "cases": 0, "buckets": dict((k, 0) for k in BUCKETS)})
            b["cases"] += 1
            inputs.append([cid, states[cid], created.get(cid)])
            if states[cid] not in closing:
                b["backlog"] += 1
                backlog += 1
                days = int((tnow - parse(created[cid]).timestamp()) // 86400)
                b["buckets"][_bucket(days)] += 1
        detail = {"by_site": dict(sorted(sites.items())), "closing_states": sorted(closing), "closure_basis": mode, "closure_policy": cref,
                  "cases_considered": len(states), "as_of": t, "age_buckets_days": list(BUCKETS)}
        return self._mv("MET-BACKLOG-D-OPS", definition_tag=tag, policy_version=self._pref(pol), policy_status=pol["status"], value=str(backlog),
                        n=len(states), window_end=t, inputs=inputs,
                        inputs_hash=sha256_hex(canonical({"inputs": inputs, "sites": site_of and sorted(site_of.items())})), computed_at=computed_at,
                        detail=detail, params={"kind": "backlog", "tag": tag, "as_of": t, "recorded_until": recorded_until,
                                               "site_map": bool(site_of)})

    def backlog_by_site(self, definition_tag=None, as_of=None, site_of=None, store=True):
        """Backlog and ageing per site under ONE declared definition. A missing tag -> E-MET-DEFINITION-REQUIRED (AC-MET-18)."""
        if as_of is None:
            raise MetDefinitionRequired({"reason": "as_of is required"})
        now = self.clock()
        mv = self._compute_backlog(definition_tag, as_of, now, site_of, now)
        return self._store(mv) if store else mv

    def _compute_exc_rate(self, tag, recorded_until, site_of, computed_at):
        pol = self._tag_policy(tag, "DEFINITION")
        rows = {}
        for raw_id, seq, queue, link in self.con.execute("SELECT raw_id, outcome_seq, queue, matched_link FROM intake_outcome WHERE decided_at <= ?"
                                                         " ORDER BY raw_id, outcome_seq", (recorded_until,)):
            rows.setdefault(raw_id, []).append((queue, link))
        cases = set(r[0] for r in self.con.execute("SELECT case_id FROM case_state"))
        links = {}
        for lid, fi, ti in self.con.execute("SELECT link_id, from_id, to_id FROM crosswalk_link"):
            links[lid] = fi if fi in cases else (ti if ti in cases else None)
        sites, inputs = {}, []
        for raw_id in sorted(rows):
            hist = rows[raw_id]
            if not any(q for q, _ in hist):
                continue
            is_open = hist[-1][0] is not None
            link = next((l for _, l in reversed(hist) if l), None)
            site = (site_of or {}).get(links.get(link), "unknown") if link else "unknown"
            s = sites.setdefault(site, {"open": 0, "all": 0})
            s["all"] += 1
            s["open"] += 1 if is_open else 0
            inputs.append([raw_id, len(hist), int(is_open), site])
        total_open, total_all = sum(s["open"] for s in sites.values()), sum(s["all"] for s in sites.values())
        for s in sites.values():
            s["rate"] = format((D(s["open"]) / D(s["all"])).quantize(RATE_PLACES, rounding=decimal.ROUND_HALF_EVEN), "f")
        value = None if total_all == 0 else format((D(total_open) / D(total_all)).quantize(RATE_PLACES, rounding=decimal.ROUND_HALF_EVEN), "f")
        return self._mv("MET-UNRESOLVED-EXC-RATE-D-OPS", definition_tag=tag, policy_version=self._pref(pol), policy_status=pol["status"], value=value,
                        null_reason=None if total_all else "no_exception_queue_items", n=total_all, window_end=recorded_until, inputs=inputs,
                        inputs_hash=sha256_hex(canonical({"inputs": inputs, "sites": site_of and sorted(site_of.items())})), computed_at=computed_at,
                        detail={"by_site": dict(sorted(sites.items())), "open": total_open, "all": total_all,
                                "formula": "open exception-queue items / all exception-queue items (A-12-F07-2)"},
                        params={"kind": "exception_rate", "tag": tag, "recorded_until": recorded_until, "site_map": bool(site_of)})

    def unresolved_exception_rate(self, definition_tag=None, site_of=None, store=True):
        now = self.clock()
        mv = self._compute_exc_rate(definition_tag, now, site_of, now)
        return self._store(mv) if store else mv

    def case_cost(self, *a, **k):
        """OP-MET-05 (R2, Could): interface placeholder until a cost input and owner exist (OPD-08)."""
        raise MetNotAvailable({"op": "OP-MET-05", "reason": "no cost input or owner (OPD-08)"})

    # ---------------------------------------------------------------- BEH-MET-07 reproduce
    def reproduce(self, value_id, source=None, site_of=None, strict=False):
        """Recompute a stored value from its stored parameters and inputs. Returns {'equal', 'diff', 'stored', 'recomputed'}; with strict=True a
        value that does not reproduce raises E-MET-NOT-REPRODUCIBLE (a defect)."""
        old = self.get_value(value_id)
        p = old.params
        kind = p.get("kind")
        if kind == "time":
            new = self._compute_ttc(self.policy.get_policy(p["policy_id"], p["policy_version"]), p["recorded_until"], old.computed_at)
        elif kind == "month_end":
            new = self._compute_total(p["cutoff_ts"], p["denominator_ref"], source, True, set(i[0] for i in old.inputs), old.computed_at)
        elif kind == "backlog":
            new = self._compute_backlog(p["tag"], p["as_of"], p["recorded_until"], site_of, old.computed_at)
        elif kind == "exception_rate":
            new = self._compute_exc_rate(p["tag"], p["recorded_until"], site_of, old.computed_at)
        else:
            raise MetUnknownMetric({"value_id": value_id, "kind": str(kind)[:30]})
        diff = {}
        for f in ("value", "null_reason", "n", "partial", "definition_tag", "policy_version", "denominator", "exclusions", "inputs_hash", "errors", "detail"):
            a, b = getattr(old, f), getattr(new, f)
            if canonical(a) != canonical(b):
                diff[f] = {"stored": a, "recomputed": b}
        res = {"value_id": value_id, "equal": not diff, "diff": diff, "stored": old.value, "recomputed": new.value,
               "code_version_stored": old.code_version, "code_version_now": new.code_version}
        if diff and strict:
            raise MetNotReproducible({"value_id": value_id, "fields": sorted(diff)})
        return res

    # ---------------------------------------------------------------- snapshot and KPI coverage (BEH-OBS-05)
    def snapshot(self, correlation_id="metrics", site_of=None, as_of=None):
        """Compute every R1 KPI that needs no explicit parameter and store the values: time to close per clock, backlog and unresolved-exception
        rate under D-OPS. The month-end total is NOT computed (cut-off and denominator are required parameters). Returns the stored rows."""
        self.registry.seed_builtin()
        out = [{"metric_id": mv.metric_id, "value_id": mv.value_id, "value": mv.value, "null_reason": mv.null_reason} for mv in self.time_to_close()]
        when = as_of or self.clock()
        for fn, kw in ((self.backlog_by_site, {"definition_tag": BACKLOG_TAG, "as_of": when, "site_of": site_of}),
                       (self.unresolved_exception_rate, {"definition_tag": BACKLOG_TAG, "site_of": site_of})):
            mv = fn(**kw)
            out.append({"metric_id": mv.metric_id, "value_id": mv.value_id, "value": mv.value, "null_reason": mv.null_reason})
        return out

    def kpi_coverage(self):
        """Every registered R1 KPI with its latest value or a stated reason (AC-OBS-08)."""
        rows = []
        for d in self.registry.list():
            last = self.values_for(d["metric_id"])
            if last:
                v = last[-1]
                rows.append({"metric_id": d["metric_id"], "definition_tag": d["definition_tag"], "status": "computed" if v.value is not None else "no_value",
                             "value": v.value, "reason": v.null_reason, "n": v.n, "policy_version": v.policy_version,
                             "policy_status": v.policy_status, "value_id": v.value_id, "label": v.label})
            else:
                rows.append({"metric_id": d["metric_id"], "definition_tag": d["definition_tag"], "status": "no_value", "value": None,
                             "reason": NEEDS_PARAMS.get(d["metric_id"], "not computed yet (run the metrics_snapshot job)"), "n": 0,
                             "policy_version": None, "policy_status": None, "value_id": None, "label": self._label()})
        return rows
