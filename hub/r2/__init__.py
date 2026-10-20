"""INC-09 / R2 services beside the frozen R1 modules: rule divergence report (OP-POL-07), intake delay / freshness reports (OP-INT-04), joined
crosswalk view (OP-ID-04), consistency findings (OP-ID-05), per-source data quality (OP-MET-06), field-class data protection (BEH-SEC-10) and
deterministic template drafts (OP-REV-04), plus `R2WebApp`, the additive WebApp subclass that serves them.

Every report is read-only: it changes no domain state (audit records only, plus finding rows for the consistency check). No AI, no model call,
no randomness, no wall clock in a computation (the clock is injected). Synthetic, unvalidated.
"""
