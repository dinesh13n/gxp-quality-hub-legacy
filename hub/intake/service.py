"""IntakeService: non-destructive, idempotent, content-aware intake (C6, F04, ADR-008, FR-INT-01..07; INC-06).

* Every delivery gets a NEW `raw_intake` row (verbatim bytes); nothing is ever updated or deleted (SQLite triggers + no such method).
  Processing results go to the separate append-only `intake_outcome`; the current outcome is the highest outcome_seq per raw_id.
  The legacy partner_feeds status columns are never read as truth and never written (the adapters read snapshots only).
* Stage order (SBR-INT-04): store raw -> identity / content-hash comparison (NOOP_DUPLICATE or REVISED_CONFLICT) -> validate (L1/L2/L3)
  -> classify (pure) -> match through the crosswalk (exact keys only, no link for quarantined items) -> outcome.
* Identity = natural key (partner, record_kind, ref_id, source_ts) per OD-18; `business_key` / `feed_id` are not identities.
* A run is ONE transaction with ONE hash-chained audit record (INTAKE_RUN): all deliveries of the run or none. Per-item results are
  covered by an outcomes_digest in that record; each human resolution and each contract-binding change has its own audit record.
* Contract bindings (L3) default to `record_only` for every source (OD-S12-11 default); the effective binding is the latest
  CONTRACT_BINDING_CHANGED policy event, written only through the shared Zone H gate (ZH-10); with `zone_h.holders` empty (shipped)
  nobody can switch a source to `enforce`.
* Free text (notes, payload attributes, resolution reasons) is typed Untrusted: stored verbatim, returned as {text, trust: untrusted} or
  escaped and length-bounded, never passed to a decision parameter (BEH-INT-09, ADR-002); the payload `state` is stored as `source_state`.
"""
import hashlib
import json
import re

from hub.core.untrusted import Untrusted, decision_params, require_trusted
from hub.crosswalk.registry import normalise
from hub.crosswalk.service import CrosswalkService, _pair, identity_targets
from hub.gate.service import GateService
from hub.intake import canon, contracts, reasons as R, schema, validate
from hub.intake.errors import (ConflictAlreadyResolved, EnvelopeInvalid, ItemNotFound, ResolutionReasonRequired)
from hub.intake.profiles import PROFILES
from hub.policy.errors import AuthorityRequired
from hub.security import audit
from hub.security.canonical import canonical, parse
from hub.security.errors import AuthForbidden, AuthUnauthenticated

ADAPTER_VERSION = "intake-adapter/1"
RESOLUTIONS = ("accept_revision", "keep_original", "reject_both")
RESOLVE_ROLES = ("reviewer", "quality_lead")
READ_ROLES = ("reviewer", "quality_lead", "compliance", "dispositioner")
MODES = ("record_only", "enforce")
REASON_MAX = 2000
DISPLAY_MAX = 200
_RUN_ID = re.compile(r"^[A-Za-z0-9._:-]{1,80}$")
OUT_COLS = ("raw_id", "outcome_seq", "outcome", "primary_reason", "all_reasons", "queue", "contract_check", "counts_toward_totals",
            "matched_link", "resolution", "resolution_reason", "resolved_by", "run_id", "decided_at", "contract_missing",
            "conflicts_with", "reason_detail")


def _s(v):
    """Column text for an envelope value: str as is, None as None, anything else stringified and bounded (the verbatim value is in raw_bytes)."""
    return v if isinstance(v, str) else (None if v is None else str(v)[:200])


def untrusted_text(v):
    """The single storage point for free text from external content (checked by hub.intake.untrusted_lint)."""
    return None if v is None else Untrusted(v, "intake").for_storage()


class _Matcher(CrosswalkService):
    """CrosswalkService rule matching WITHOUT its own transaction: the intake run owns the transaction and the audit record."""

    def begin(self, code):
        lt = self.registry.link_type(code)
        active, retracted = self._states([(lt["from_type"], lt["to_type"])])
        return {"lt": lt, "code": code, "active": active, "retracted": retracted,
                "n": self.con.execute("SELECT count(*) FROM crosswalk_link").fetchone()[0]}

    def match(self, st, from_id, key, targets, run_id, now):
        """(result, link_id, candidates); result in LINKED | NOOP_ALREADY_LINKED | SKIPPED_RETRACTED | UNMATCHED_REF | AMBIGUOUS_MATCH | NO_KEY."""
        lt = st["lt"]
        ft, tt = lt["from_type"], lt["to_type"]
        k = normalise(key)
        if not k:
            return "NO_KEY", None, []
        cands = list(targets.get(k, []))
        if not cands:
            return "UNMATCHED_REF", None, []
        if len(cands) > 1:
            return "AMBIGUOUS_MATCH", None, sorted(cands)
        pk = _pair(ft, from_id, tt, cands[0])
        if pk in st["active"]:
            row = self.con.execute("SELECT link_id FROM crosswalk_link WHERE from_type = ? AND from_id = ? AND to_type = ? AND to_id = ?",
                                   (ft, from_id, tt, cands[0])).fetchone()
            return "NOOP_ALREADY_LINKED", row[0] if row else None, cands
        if pk in st["retracted"]:
            return "SKIPPED_RETRACTED", None, cands
        st["n"] += 1
        link_id = self._insert_link(st["n"], ft, from_id, tt, cands[0], lt["key_used"], "rule", st["code"], now, None, run_id,
                                    "crosswalk-matcher", "LINK_CREATED_RULE")
        st["active"].add(pk)
        return "LINKED", link_id, cands


class IntakeService(object):
    def __init__(self, con, settings, clock, anchor=None, profiles=None, registry=None):
        self.con, self.s, self.clock, self.anchor = con, settings, clock, anchor
        self.profiles = profiles if profiles is not None else PROFILES
        schema.require(con)
        self.matcher = _Matcher(con, settings, clock, anchor, registry)

    # ------------------------------------------------------------------ bindings (L3 scope, OD-S12-11)
    def binding(self, source):
        prof = self.profiles.get(source)
        if prof is None:
            raise EnvelopeInvalid({"source": str(source)[:40], "reason": "unknown source"})
        row = self.con.execute("SELECT new_value, event_id FROM policy_events WHERE policy_ref = ? AND event_type = 'CONTRACT_BINDING_CHANGED'"
                               " ORDER BY rowid DESC LIMIT 1", ("contract_binding:" + source,)).fetchone()
        if row is None:
            return {"source": source, "mode": "record_only", "contract_file": prof["contract"], "origin": "default"}
        v = json.loads(row[0])
        return {"source": source, "mode": v["mode"], "contract_file": v["contract_file"], "origin": row[1]}

    def set_binding(self, sess, source, mode, authority_ref, correlation_id="intake"):
        """Zone H (ZH-10): change the contract-binding mode of a source. Needs a human holder in zone_h.holders with a fresh re-auth;
        with the shipped empty holder list it raises E-GATE-NO-HOLDERS."""
        require_trusted([source, mode, authority_ref], "set_binding")
        if source not in self.profiles or mode not in MODES:
            raise EnvelopeInvalid({"source": str(source)[:40], "mode": str(mode)[:20], "allowed_modes": list(MODES)})
        if not isinstance(authority_ref, str) or not authority_ref.strip():
            raise AuthorityRequired()
        ref = "contract_binding:" + source
        hcr = "audit:%d" % GateService(self.con, self.s, self.clock, self.anchor).require_holder(sess, "ZH-10", correlation_id, ref)
        prof = self.profiles[source]
        old = self.binding(source)
        p = sess.principal
        with audit.change(self.con, self.clock, anchor=self.anchor, actor=p.principal_id, actor_kind=p.actor_kind,
                          action="CONTRACT_BINDING_CHANGED", outcome="success", correlation_id=correlation_id, object_ref=ref,
                          details={"source": source, "from_mode": old["mode"], "to_mode": mode}) as ctx:
            n = self.con.execute("SELECT count(*) FROM policy_events").fetchone()[0] + 1
            eid = "PE-%08d" % n
            self.con.execute("INSERT INTO policy_events(event_id, policy_ref, event_type, actor, occurred_at, old_value, new_value,"
                             " authority_ref, holder_check_ref) VALUES (?,?,?,?,?,?,?,?,?)",
                             (eid, ref, "CONTRACT_BINDING_CHANGED", p.principal_id, self.clock(),
                              canonical({"mode": old["mode"], "contract_file": old["contract_file"]}),
                              canonical({"mode": mode, "contract_file": prof["contract"]}), authority_ref.strip(), hcr))
            ctx.fields["details"]["event_id"] = eid
        return self.binding(source)

    # ------------------------------------------------------------------ targets
    def case_targets(self):
        """Core-entity keys for the matcher: the cases of the decision record (exact id = registered key)."""
        return identity_targets([r[0] for r in self.con.execute("SELECT case_id FROM case_state ORDER BY case_id")])

    # ------------------------------------------------------------------ run records
    def _run_event(self, run_id, seq, event_type, source, body):
        self.con.execute("INSERT INTO intake_run_event(run_id, run_seq, event_type, source, occurred_at, body) VALUES (?,?,?,?,?,?)",
                         (run_id, seq, event_type, source, self.clock(), canonical(body)))

    def last_checkpoint(self, source):
        """Hub-owned offset of the latest RUN_CHECKPOINT of a source (AD-04); legacy gateway checkpoints are never touched."""
        row = self.con.execute("SELECT body FROM intake_run_event WHERE source = ? AND event_type = 'RUN_CHECKPOINT' ORDER BY rowid DESC LIMIT 1",
                               (source,)).fetchone()
        return json.loads(row[0]) if row else None

    def fail_run(self, source, run_id, error_code, details=None, correlation_id="intake"):
        """A run that could not read its source (AC-INT-26): one RUN_FAILED record + one audit record; NO item outcome is fabricated."""
        if source not in self.profiles:
            raise EnvelopeInvalid({"source": str(source)[:40], "reason": "unknown source"})
        if not isinstance(run_id, str) or not _RUN_ID.match(run_id):
            raise EnvelopeInvalid({"run_id": "invalid"})
        body = {"error": str(error_code)[:60], "details": details or {}}
        with audit.change(self.con, self.clock, anchor=self.anchor, actor="intake-job", actor_kind="system", action="INTAKE_RUN_FAILED",
                          outcome="error", correlation_id=correlation_id, object_ref="intake:" + source,
                          details={"run_id": run_id, "source": source, "error": body["error"]}):
            self._run_event(run_id, 1, "RUN_STARTED", source, {})
            self._run_event(run_id, 2, "RUN_FAILED", source, body)
        return {"run_id": run_id, "source": source, "status": "failed", "error": body["error"]}

    # ------------------------------------------------------------------ ingest
    def ingest(self, source, deliveries, run_id, correlation_id="intake", targets=None, idempotent_backfill=False, checkpoint=None):
        """Ingest `deliveries` (dicts: source_key, partner, schema_rev, source_ts, ref_id, record_kind, payload_text, raw) of one source in
        ONE transaction. Returns the run report. idempotent_backfill=True skips a delivery already stored with the same (source, source_key,
        content_hash) - the legacy backfill rule of BEH-INT-10 (a normal repeated delivery is stored again and becomes NOOP_DUPLICATE)."""
        prof = self.profiles.get(source)
        if prof is None:
            raise EnvelopeInvalid({"source": str(source)[:40], "reason": "unknown source"})
        if not isinstance(deliveries, (list, tuple)) or not all(isinstance(d, dict) for d in deliveries):
            raise EnvelopeInvalid({"reason": "deliveries must be a list of objects"})
        if not isinstance(run_id, str) or not _RUN_ID.match(run_id):
            raise EnvelopeInvalid({"run_id": "invalid"})
        if self.con.execute("SELECT 1 FROM intake_run_event WHERE run_id = ?", (run_id,)).fetchone():
            raise EnvelopeInvalid({"run_id": run_id, "reason": "run id already used"})
        bind = self.binding(source)
        contract = contracts.load(bind["contract_file"]) if bind["contract_file"] else None
        cnt = {"received": len(deliveries), "stored": 0, "skipped_existing": 0, "noop_duplicate": 0, "revised_conflict": 0,
               "linked": 0, "outcomes": {}, "reasons": {}, "queues": {}, "contract_check": {}}
        digest = hashlib.sha256()
        first_raw = last_raw = None
        with audit.change(self.con, self.clock, anchor=self.anchor, actor="intake-job", actor_kind="system", action="INTAKE_RUN",
                          outcome="success", correlation_id=correlation_id, object_ref="intake:" + source, details={}) as ctx:
            self._run_event(run_id, 1, "RUN_STARTED", source, {"received": len(deliveries), "binding_mode": bind["mode"]})
            now = self.clock()
            n_raw = self.con.execute("SELECT count(*) FROM raw_intake").fetchone()[0]
            match_state = tgt = None
            for d in deliveries:
                chash = canon.content_hash(d.get("schema_rev"), d.get("payload_text"))
                if idempotent_backfill and self.con.execute("SELECT 1 FROM raw_intake WHERE source = ? AND source_key = ? AND content_hash = ?",
                                                            (source, _s(d.get("source_key")), chash)).fetchone():
                    cnt["skipped_existing"] += 1
                    continue
                ident, complete = canon.identity_key(source, d.get("partner"), d.get("record_kind"), d.get("ref_id"),
                                                     d.get("source_ts"), d.get("source_key"), chash)
                prior = self.con.execute("SELECT raw_id, content_hash FROM raw_intake WHERE identity_key = ? ORDER BY rowid", (ident,)).fetchall()
                same = [p[0] for p in prior if p[1] == chash]
                n_raw += 1
                raw_id = "RAW-%010d" % n_raw
                raw = d["raw"] if isinstance(d.get("raw"), dict) else dict((k, v) for k, v in d.items() if k != "raw")
                self.con.execute("INSERT INTO raw_intake(raw_id, source, source_key, partner, schema_rev, receipt_time, identity_key, content_hash,"
                                 " duplicate_of, raw_bytes, run_id, adapter_version) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
                                 (raw_id, source, _s(d.get("source_key")), _s(d.get("partner")), _s(d.get("schema_rev")), now, ident, chash,
                                  same[0] if same else None, canon.raw_bytes(raw), run_id, ADAPTER_VERSION))
                cnt["stored"] += 1
                first_raw = first_raw or raw_id
                last_raw = raw_id
                found, detail, facts = validate.validate(prof, d)
                cc, missing = ("not_bound", []) if contract is None else contracts.check(contract, facts["payload"])
                if same:
                    out = {"outcome": "NOOP_DUPLICATE", "primary_reason": None, "all_reasons": [], "queue": None}
                    counts, link, conflicts_with, detail = 0, None, None, {}
                    cnt["noop_duplicate"] += 1
                else:
                    if bind["mode"] == "enforce" and cc == "fail":
                        found.add("CONTRACT_VIOLATION")
                        detail["CONTRACT_VIOLATION"] = missing
                    conflicts_with = prior[0][0] if prior else None
                    if prior:
                        found.add("REVISED_CONFLICT")
                        detail["REVISED_CONFLICT"] = {"conflicts_with": conflicts_with}
                        cnt["revised_conflict"] += 1
                    link = None
                    if prof["match"] and not (found & R.NO_MATCH_REASONS):
                        if match_state is None:
                            match_state = self.matcher.begin(prof["match"])
                            tgt = targets() if callable(targets) else (targets if targets is not None else self.case_targets())
                        res, link, cands = self.matcher.match(match_state, _s(d.get("source_key")), d.get("ref_id"), tgt, run_id, now)
                        if res == "AMBIGUOUS_MATCH":
                            found.add("AMBIGUOUS_MATCH")
                            detail["AMBIGUOUS_MATCH"] = {"candidates": cands}
                        elif res in ("UNMATCHED_REF", "SKIPPED_RETRACTED", "NO_KEY"):
                            found.add("UNMATCHED_REF")
                            if res == "SKIPPED_RETRACTED":
                                detail["UNMATCHED_REF"] = {"note": "link was retracted by a human; not re-created"}
                        elif res == "LINKED":
                            cnt["linked"] += 1
                    out = R.classify(found)
                    counts = 1
                    self._attrs(raw_id, prof, d, facts)
                self._append_outcome(raw_id=raw_id, outcome_seq=1, outcome=out["outcome"], primary_reason=out["primary_reason"],
                                     all_reasons=out["all_reasons"], queue=out["queue"], contract_check=cc, counts_toward_totals=counts,
                                     matched_link=link, run_id=run_id, decided_at=now, contract_missing=missing,
                                     conflicts_with=conflicts_with, reason_detail=detail)
                cnt["outcomes"][out["outcome"]] = cnt["outcomes"].get(out["outcome"], 0) + 1
                for code in out["all_reasons"]:
                    cnt["reasons"][code] = cnt["reasons"].get(code, 0) + 1
                if out["queue"]:
                    cnt["queues"][out["queue"]] = cnt["queues"].get(out["queue"], 0) + 1
                cnt["contract_check"][cc] = cnt["contract_check"].get(cc, 0) + 1
                digest.update(("%s|%s|%s|%s\n" % (raw_id, out["outcome"], out["primary_reason"], out["queue"])).encode("utf-8"))
            seq = 2
            if checkpoint is not None:
                self._run_event(run_id, seq, "RUN_CHECKPOINT", source, checkpoint)
                seq += 1
            report = dict(cnt, run_id=run_id, source=source, status="finished", binding=bind, first_raw_id=first_raw,
                          last_raw_id=last_raw, outcomes_digest=digest.hexdigest())
            self._run_event(run_id, seq, "RUN_FINISHED", source, {k: report[k] for k in ("received", "stored", "skipped_existing", "outcomes")})
            ctx.fields["details"] = {"run_id": run_id, "source": source, "binding_mode": bind["mode"], "received": cnt["received"],
                                     "stored": cnt["stored"], "skipped_existing": cnt["skipped_existing"],
                                     "noop_duplicate": cnt["noop_duplicate"], "revised_conflict": cnt["revised_conflict"],
                                     "linked": cnt["linked"], "outcomes": cnt["outcomes"], "reasons": cnt["reasons"],
                                     "queues": cnt["queues"], "contract_check": cnt["contract_check"],
                                     "first_raw_id": first_raw, "last_raw_id": last_raw, "outcomes_digest": report["outcomes_digest"]}
        return report

    def _attrs(self, raw_id, prof, d, facts):
        a = validate.attrs(prof, facts["payload"])
        if not a:
            return
        self.con.execute("INSERT INTO intake_item_attr(raw_id, record_kind, ref_id, source_ts, source_state, source_quality_flag, source_subtype,"
                         " amount_text, notes, notes_trust) VALUES (?,?,?,?,?,?,?,?,?, 'untrusted')",
                         (raw_id, _s(d.get("record_kind")), _s(d.get("ref_id")), _s(d.get("source_ts")),
                          untrusted_text(a.get("source_state")), untrusted_text(a.get("source_quality_flag")),
                          untrusted_text(a.get("source_subtype")), facts["amount_text"], untrusted_text(a.get("notes"))))

    @decision_params
    def _append_outcome(self, raw_id, outcome_seq, outcome, primary_reason, all_reasons, queue, contract_check, counts_toward_totals,
                        matched_link, run_id, decided_at, contract_missing, conflicts_with, reason_detail, resolution=None,
                        resolution_reason=None, resolved_by=None):
        """The only writer of intake_outcome. Every parameter drives a decision / queue / status: an Untrusted value raises
        E-INT-UNTRUSTED-USE (runtime guard of AC-INT-23; the resolution reason is stored by resolve_conflict through untrusted_text)."""
        self.con.execute("INSERT INTO intake_outcome(" + ", ".join(OUT_COLS) + ") VALUES (" + ",".join("?" * len(OUT_COLS)) + ")",
                         (raw_id, outcome_seq, outcome, primary_reason, canonical(list(all_reasons)), queue, contract_check, counts_toward_totals,
                          matched_link, resolution, resolution_reason, resolved_by, run_id, decided_at, canonical(list(contract_missing)),
                          conflicts_with, canonical(reason_detail)))

    # ------------------------------------------------------------------ human resolution of a revision conflict
    def resolve_conflict(self, sess, raw_id, resolution, reason, correlation_id="intake"):
        """BEH-INT-04: reviewer / quality_lead resolves a REVISED_CONFLICT with accept_revision | keep_original | reject_both and a reason.
        Appends a CONFLICT_RESOLVED outcome (seq+1) + one audit record; no case state, decision event or gate event is touched."""
        require_trusted([raw_id, resolution], "resolve_conflict")
        if sess is None:
            raise AuthUnauthenticated()
        p = sess.principal
        if not (p.kind == "human" and any(r in p.roles for r in RESOLVE_ROLES)):
            audit.append(self.con, self.clock, anchor=self.anchor, actor=p.principal_id, actor_kind=p.actor_kind, action="AUTHZ_DENIED",
                         outcome="denied", correlation_id=correlation_id, object_ref="intake:resolve",
                         details={"reason": "role", "needs_one_of": list(RESOLVE_ROLES)})
            raise AuthForbidden({"reason": "role"})
        if resolution not in RESOLUTIONS:
            raise EnvelopeInvalid({"resolution": str(resolution)[:30], "allowed": list(RESOLUTIONS)})
        text = reason.for_storage() if isinstance(reason, Untrusted) else reason
        text = text.strip() if isinstance(text, str) else ""
        if not text or len(text) > REASON_MAX:
            raise ResolutionReasonRequired({"reason": "a non-empty reason of at most %d characters is required" % REASON_MAX})
        with audit.change(self.con, self.clock, anchor=self.anchor, actor=p.principal_id, actor_kind=p.actor_kind,
                          action="INTAKE_CONFLICT_RESOLVED", outcome="success", correlation_id=correlation_id,
                          object_ref="intake:" + str(raw_id)[:40], details={}) as ctx:
            row = self.con.execute("SELECT outcome, outcome_seq, conflicts_with, contract_check, counts_toward_totals, contract_missing, reason_detail"
                                   " FROM intake_outcome WHERE raw_id = ? ORDER BY outcome_seq DESC LIMIT 1", (raw_id,)).fetchone()
            if row is None or row[2] is None:
                raise ItemNotFound({"raw_id": str(raw_id)[:40]})
            if row[0] == "CONFLICT_RESOLVED":
                raise ConflictAlreadyResolved({"raw_id": raw_id})
            self._append_outcome(raw_id=raw_id, outcome_seq=row[1] + 1, outcome="CONFLICT_RESOLVED", primary_reason=None, all_reasons=[],
                                 queue=None, contract_check=row[3], counts_toward_totals=row[4], matched_link=None,
                                 run_id="resolve-" + correlation_id[:60], decided_at=self.clock(), contract_missing=json.loads(row[5]),
                                 conflicts_with=row[2], reason_detail=json.loads(row[6]), resolution=resolution,
                                 resolution_reason=untrusted_text(text), resolved_by=p.principal_id)
            ctx.fields["details"] = {"raw_id": raw_id, "conflicts_with": row[2], "resolution": resolution}
            ctx.fields["reason"] = "resolution reason recorded on the outcome row"
        return self.get_item(raw_id)

    # ------------------------------------------------------------------ reads
    def outcomes(self, raw_id):
        rows = self.con.execute("SELECT " + ", ".join(OUT_COLS) + " FROM intake_outcome WHERE raw_id = ? ORDER BY outcome_seq", (raw_id,)).fetchall()
        out = []
        for r in rows:
            o = dict(zip(OUT_COLS, r))
            for k in ("all_reasons", "contract_missing", "reason_detail"):
                o[k] = json.loads(o[k])
            out.append(o)
        return out

    def get_item(self, raw_id):
        r = self.con.execute("SELECT raw_id, source, source_key, partner, schema_rev, receipt_time, identity_key, content_hash, duplicate_of,"
                             " run_id FROM raw_intake WHERE raw_id = ?", (raw_id,)).fetchone()
        if r is None:
            raise ItemNotFound({"raw_id": str(raw_id)[:40]})
        d = dict(zip(("raw_id", "source", "source_key", "partner", "schema_rev", "receipt_time", "identity_key", "content_hash",
                      "duplicate_of", "run_id"), r))
        d["outcomes"] = self.outcomes(raw_id)
        d["current"] = d["outcomes"][-1] if d["outcomes"] else None
        a = self.con.execute("SELECT record_kind, ref_id, source_ts, source_state, source_quality_flag, source_subtype, amount_text, notes"
                             " FROM intake_item_attr WHERE raw_id = ?", (raw_id,)).fetchone()
        d["attributes"] = None if a is None else dict(
            zip(("record_kind", "ref_id", "source_ts", "source_state", "source_quality_flag", "source_subtype", "amount_text"), a[:7]))
        d["notes"] = None if a is None or a[7] is None else Untrusted(a[7], "intake").to_wire()
        return d

    def raw_bytes(self, raw_id):
        r = self.con.execute("SELECT raw_bytes FROM raw_intake WHERE raw_id = ?", (raw_id,)).fetchone()
        if r is None:
            raise ItemNotFound({"raw_id": str(raw_id)[:40]})
        return bytes(r[0])

    def display_notes(self, raw_id, limit=DISPLAY_MAX):
        """HTML-escaped, length-bounded, labelled (BEH-INT-09)."""
        w = self.get_item(raw_id)["notes"]
        if w is None:
            return None
        u = Untrusted(w["text"][:limit], "intake")
        return {"text": u.escaped(), "truncated": len(w["text"]) > limit, "trust": "untrusted", "label": "untrusted source text"}

    def versions(self, raw_id):
        """Both versions of a conflict are retrievable and linked: [original, revision] raw ids."""
        cur = self.con.execute("SELECT conflicts_with FROM intake_outcome WHERE raw_id = ? ORDER BY outcome_seq DESC LIMIT 1", (raw_id,)).fetchone()
        if cur is None:
            raise ItemNotFound({"raw_id": str(raw_id)[:40]})
        return [cur[0], raw_id] if cur[0] else [raw_id]

    def queue_snapshot(self, as_of):
        """Queue sizes, ages, per-reason counts and totals over the CURRENT outcomes without NOOP_DUPLICATE (SBR-INT-08)."""
        t = parse(as_of).timestamp()
        queues, ages = {}, {}
        for q, rt in self.con.execute("SELECT o.queue, r.receipt_time FROM intake_current o JOIN raw_intake r ON r.raw_id = o.raw_id"
                                      " WHERE o.queue IS NOT NULL ORDER BY o.raw_id"):
            queues[q] = queues.get(q, 0) + 1
            age = t - parse(rt).timestamp()
            a = ages.setdefault(q, {"min": age, "max": age, "sum": 0.0})
            a["min"], a["max"], a["sum"] = min(a["min"], age), max(a["max"], age), a["sum"] + age
        reasons = {}
        for (ar,) in self.con.execute("SELECT all_reasons FROM intake_current"):
            for c in json.loads(ar):
                reasons[c] = reasons.get(c, 0) + 1
        totals = dict(self.con.execute("SELECT outcome, count(*) FROM intake_current WHERE counts_toward_totals = 1 GROUP BY outcome").fetchall())
        return {"queues": dict(sorted(queues.items())), "ages_seconds": dict(sorted(ages.items())), "reasons": dict(sorted(reasons.items())),
                "totals": dict(sorted(totals.items())), "total_items": sum(totals.values())}

    def counts(self):
        return {"raw": self.con.execute("SELECT count(*) FROM raw_intake").fetchone()[0],
                "outcomes": self.con.execute("SELECT count(*) FROM intake_outcome").fetchone()[0],
                "noop_duplicate": self.con.execute("SELECT count(*) FROM intake_outcome WHERE outcome = 'NOOP_DUPLICATE'").fetchone()[0],
                "runs": self.con.execute("SELECT count(*) FROM intake_run_event WHERE event_type = 'RUN_FINISHED'").fetchone()[0]}

    def vendor_totals(self, source="vendor_csv"):
        """Exact Decimal sum of the parsable amounts of non-duplicate items of a source, per currency (FR-MET-04)."""
        totals = {}
        for cur, amt in self.con.execute(
                "SELECT json_extract(CAST(r.raw_bytes AS TEXT), '$.currency'), a.amount_text FROM intake_current o"
                " JOIN raw_intake r ON r.raw_id = o.raw_id JOIN intake_item_attr a ON a.raw_id = o.raw_id WHERE r.source = ?"
                " ORDER BY o.raw_id", (source,)):
            dec = validate.to_decimal(amt)
            if dec is not None:
                totals[cur] = totals.get(cur, validate.Decimal(0)) + dec
        return dict((k, str(v)) for k, v in sorted(totals.items(), key=lambda kv: str(kv[0])))
