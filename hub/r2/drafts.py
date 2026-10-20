"""Template drafts (OP-REV-04, BEH-REV-07, FR-REV-04 R2 Could, AC-REV-18; INC-09). Deterministic templates: hub/r2/templates.json.

Deferred by default: `templates.enabled` false -> E-REV-DRAFTS-DISABLED (the INC-08 code). When enabled, a human reviewer / quality_lead / compliance
creates a draft owned by the author: only the fields the author typed are stored, exactly as typed (no pre-fill from rules, search, intake or any
other source; no generation). Unknown template / field, wrong type or over-long value -> E-REV-TEMPLATE-INVALID. A draft has NO Zone H power: this
module never imports hub.gate or hub.decision.service and the response offers no action. Final submission / signature happens outside the product
(T4). Insert-only table review_draft (M007); one audit record per draft (DRAFT_CREATED, field names only, never the text).
"""
import json
import os

from hub.review.errors import DraftsDisabled, TemplateInvalid
from hub.search import schema, settings as ssettings
from hub.security import audit
from hub.security.errors import AuthForbidden, AuthUnauthenticated

ROLES = ("reviewer", "quality_lead", "compliance")
PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates.json")


def catalogue():
    with open(PATH, encoding="utf-8") as f:
        return json.load(f)["templates"]


def form(template_id):
    t = catalogue().get(template_id)
    if t is None:
        raise TemplateInvalid({"template_id": str(template_id)[:40], "reason": "unknown template"})
    return {"template_id": template_id, "version": t["version"], "title": t["title"],
            "fields": [dict(f, value=None) for f in t["fields"]], "prefilled": False}


def validate(template_id, fields):
    t = catalogue().get(template_id)
    if t is None:
        raise TemplateInvalid({"template_id": str(template_id)[:40], "reason": "unknown template"})
    fields = fields or {}
    if not isinstance(fields, dict):
        raise TemplateInvalid({"reason": "fields must be an object"})
    spec = dict((f["name"], f) for f in t["fields"])
    errs = []
    for k in sorted(fields):
        if k not in spec:
            errs.append({"field": str(k)[:40], "reason": "unknown field"})
        elif not isinstance(fields[k], str):
            errs.append({"field": k, "reason": "text expected"})
        elif len(fields[k]) > spec[k]["max_length"]:
            errs.append({"field": k, "reason": "longer than %d characters" % spec[k]["max_length"]})
    if errs:
        raise TemplateInvalid({"errors": errs})
    return t, dict((k, fields[k]) for k in sorted(fields))


def create(con, clock, anchor, cfg, sess, template_id, fields, correlation_id="draft"):
    if sess is None:
        raise AuthUnauthenticated()
    p = sess.principal
    if p.kind != "human" or not any(r in p.roles for r in ROLES):
        raise AuthForbidden({"reason": "role"})
    if not ssettings.templates_enabled(cfg):
        raise DraftsDisabled({"op": "OP-REV-04", "hint": "templates.enabled is false (deferred by default, BEH-REV-07)"})
    t, stored = validate(template_id, fields)
    schema.require(con)
    with audit.change(con, clock, anchor=anchor, actor=p.principal_id, actor_kind=p.actor_kind, action="DRAFT_CREATED", outcome="success",
                      correlation_id=correlation_id, object_ref="draft", details={}) as ctx:
        did = "DRF-%08d" % (con.execute("SELECT count(*) FROM review_draft").fetchone()[0] + 1)
        now = clock()
        con.execute("INSERT INTO review_draft(draft_id, template_id, template_version, fields, owner, created_at, label) VALUES (?,?,?,?,?,?,?)",
                    (did, template_id, t["version"], json.dumps(stored, sort_keys=True), p.principal_id, now, "synthetic, unvalidated"))
        ctx.fields["details"] = {"draft_id": did, "template_id": template_id, "field_names": sorted(stored)}
    return {"draft_id": did, "template_id": template_id, "template_version": t["version"], "fields": stored, "owner": p.principal_id,
            "created_at": now, "prefilled": False, "zone_h": "none (a draft carries no Zone H power; submission and signature happen outside the product)",
            "label": "synthetic, unvalidated"}
