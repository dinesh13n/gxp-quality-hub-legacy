"""C10 R2 search (F08 BEH-REV-03..06, ADR-012; INC-09): derived, rebuildable corpus index (documents + archive items), SQLite FTS5 / trigram engine
behind the `search.fts` flag (default off) and a fallback engine with the same grammar and the same ordering formula.

Keyword / field search only (ADR-002, OD-08): no embeddings, no model call, no query rewriting, no synonyms, no generation. The query text is never
concatenated into SQL: every term is a bound parameter inside a quoted FTS phrase. Synthetic, unvalidated.
"""
