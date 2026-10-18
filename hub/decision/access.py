"""Evidence access rule (AC-DEC-13, FR-SEC-01/03) - Assumption A-15-05-1: the role-to-level matrix does not exist in the specs.

Level `restricted` (the default level of a new evidence record) is readable by quality_lead, compliance and dispositioner;
the levels engineering, quality and operations by every role allowed to read events (reviewer included). A caller without
access gets the redacted placeholder {ev_id, access: "denied"} - no kind, source or body.
"""
LEVELS = ("engineering", "quality", "operations", "restricted")
READERS = {
    "restricted": ("quality_lead", "compliance", "dispositioner"),
    "engineering": ("reviewer", "quality_lead", "compliance", "dispositioner"),
    "quality": ("reviewer", "quality_lead", "compliance", "dispositioner"),
    "operations": ("reviewer", "quality_lead", "compliance", "dispositioner"),
}


def can_read(roles, level):
    return any(r in READERS.get(level, ()) for r in roles)
