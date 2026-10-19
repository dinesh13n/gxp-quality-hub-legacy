"""C8 runs (F06, ADR-010, INC-07): CLI jobs with append-only run records, checkpoints, single-flight lock, no silent capacity cap.

THE SCHEDULER IS OFF (OD-19, OD-S12-10 / HAR-10 open): this package contains no scheduler, timer, daemon or loop. A run exists only
because an operator (or an OS-level entry outside the repository, documented in inc07-design-notes.md) invoked `python -m hub.runs run`.
`--trigger scheduled` is refused with E-RUN-SCHEDULE-DISABLED (and a refused run record) unless a Zone H holder switched the flag on (ZH-09);
the shipped config has zone_h.holders EMPTY, so nobody can. Synthetic, unvalidated; no model call; no network beyond loopback.
"""
import hub

CODE_VERSION = "%s+inc07" % hub.__version__
