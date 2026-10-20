"""Data protection by field class (BEH-SEC-10, FR-SEC-03, PNFR-12; metadata-model M2/M3/M4; INC-09).

Classes (M2, Assumption A-11-02 - Stage 24 decides): C0 public (none in the estate), C1 internal, C2 confidential, C3 restricted. FIELD_CLASSES maps
every field the hub serves to a class and a handling rule; `project(record_type, record, roles)` applies the M4 matrix to one record:
  * finance_read sees `account_id` MASKED (C2 identifiers);
  * documents: the access level decides (hub.decision.access); a missing or unknown access_level / classification is `restricted` (MA-1);
  * restricted (C3) content needs a named role; a caller without one gets {access: "denied"} and no content;
  * every read of C3 data and every export needs a non-empty reason, audited (MA-2): `require_reason` raises E-SEC-REASON-REQUIRED otherwise.
Pure apart from `audit_c3_read` (one audit record). No model, no network.
"""
from hub.decision import access
from hub.r2.errors import ReasonRequired
from hub.security import audit

CLASSES = ("C0", "C1", "C2", "C3")
# record type -> field -> (class, handling)
FIELD_CLASSES = {
    "case": {"case_id": ("C2", "show"), "account_id": ("C2", "mask_for_finance"), "state": ("C2", "show"), "site": ("C1", "show"),
             "amount": ("C2", "show")},
    "batch": {"batch_id": ("C1", "show"), "qa_status": ("C1", "show"), "batch_site": ("C1", "show")},
    "deviation": {"deviation_id": ("C1", "show"), "status": ("C1", "show")},
    "capa": {"capa_id": ("C1", "show"), "action_owner": ("C2", "pseudonymous"), "state": ("C1", "show")},
    "document": {"doc_id": ("by_access_level", "show"), "body": ("by_access_level", "untrusted_escaped"), "access_level": ("C1", "show")},
    "audit": {"actor": ("C3", "named_role"), "reason": ("C3", "named_role")},
}
# M4: which roles may read a class at all (C2 for finance_read is masked; C3 = restricted documents and the audit trail)
CLASS_READERS = {
    "C0": ("reviewer", "quality_lead", "compliance", "finance_read", "integration", "dispositioner"),
    "C1": ("reviewer", "quality_lead", "compliance", "finance_read", "integration", "dispositioner"),
    "C2": ("reviewer", "quality_lead", "compliance", "finance_read", "integration", "dispositioner"),
    "C3": ("quality_lead", "compliance", "dispositioner"),
}
MASK = "****"


def document_class(access_level):
    """C2 for engineering / quality / operations, C3 for restricted; missing or unknown -> C3 (MA-1)."""
    return "C2" if access_level in ("engineering", "quality", "operations") else "C3"


def mask(value):
    if not isinstance(value, str) or len(value) <= 4:
        return MASK
    return MASK + value[-4:]


def project(record_type, record, roles):
    """One record as the caller may see it. Unknown record types are denied (deny by default)."""
    fields = FIELD_CLASSES.get(record_type)
    if fields is None:
        return {"access": "denied"}
    if record_type == "document":
        level = record.get("access_level")
        level = level if level in access.LEVELS else "restricted"
        if not access.can_read(roles, level):
            return {"type": "document", "access": "denied"}
        out = dict((k, record.get(k)) for k in fields if k in record)
        out["access_level"] = level
        out["field_class"] = document_class(level)
        return out
    out = {}
    for k, v in record.items():
        cls, handling = fields.get(k, ("C3", "named_role"))  # an unmapped field is treated as restricted
        if not any(r in CLASS_READERS[cls] for r in roles):
            out[k] = {"access": "denied"}
        elif handling == "mask_for_finance" and "finance_read" in roles and not any(
                r in roles for r in ("reviewer", "quality_lead", "compliance", "dispositioner")):
            out[k] = mask(v)
        else:
            out[k] = v
    return out


def require_reason(reason, op, c3_rows):
    why = reason.strip() if isinstance(reason, str) else ""
    if not why:
        raise ReasonRequired({"op": op, "c3_rows": c3_rows})
    return why[:500]


def audit_c3_read(con, clock, anchor, principal, reason, op, details, correlation_id):
    """Append the C3_READ audit record (the reason is stored in the audit `reason` column, non-empty)."""
    d = {"op": op}
    d.update(details or {})
    return audit.append(con, clock, anchor=anchor, actor=principal.principal_id, actor_kind=principal.actor_kind, action="C3_READ",
                        outcome="success", correlation_id=correlation_id, object_ref=op, reason=reason, details=d)


def coverage():
    """Field classes that have at least one mapped field (AC-NFR-12 checks this equals every class present in the estate)."""
    present = set()
    for fields in FIELD_CLASSES.values():
        for cls, _ in fields.values():
            if cls in CLASSES:
                present.add(cls)
    present.update(["C2", "C3"])  # document classes come from the access level
    return sorted(present)
