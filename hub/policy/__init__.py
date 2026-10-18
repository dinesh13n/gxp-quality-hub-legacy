"""INC-04 policy & rule service (C4, ADR-007, F03; Stage 15). Standard library only; no model call (OD-08).

Policy objects (candidate / adopted / accepted-open), table-driven rule sets as data, a pure evaluation engine,
and the three as-found legacy approval rule sets loaded as named, versioned, INACTIVE candidates (OD-16).
Nothing here is an approval: no rule set is active and no policy is adopted on a fresh install.
Synthetic, unvalidated.
"""
STAGE = "15 INC-04"
