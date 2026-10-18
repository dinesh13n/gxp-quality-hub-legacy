"""INC-05 identity crosswalk (C7, F05, ADR-009). Standard library only; no model call (OD-08).

Explicit `crosswalk_link` rows: rule links only by an exact registered key (no inference of any kind), human links by a
reviewer with a reason. Orphans stay orphans and are counted, never repaired. Synthetic, unvalidated.
"""
STAGE = "15 INC-05"
