"""INC-05 decision & evidence record (C3, F01, ADR-004/005), legacy backfill (DM-1) and CLI. Standard library only; no model call (OD-08).

The record is append-only: the service exposes no update or delete of an event, SQLite triggers reject UPDATE / DELETE,
and every append is one transaction with its projection row and its hash-chained audit record. Humans decide; nothing
here evaluates evidence sufficiency or labels a case 'closed' from a fact event. Synthetic, unvalidated.
"""
STAGE = "15 INC-05"
