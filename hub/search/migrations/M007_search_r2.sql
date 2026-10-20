-- M007 (INC-09, R2): derived search corpus + R2 records. Applied by hub.search.schema (own table search_schema_migrations), not by hub.store.migrate.
-- Synthetic, unvalidated. Forward-only; rollback = backup restore (records) or `python -m hub.search drop-index` (derived corpus only).
-- The FTS5 virtual tables search_fts / search_tri are NOT created here: they are derived objects that the index builder creates only when the
-- runtime offers FTS5 + trigram (BEH-REV-06, OD-S12-12), and drops on rollback.

-- Derived, rebuildable corpus rows (documents + archive items). Deleting all rows is the rollback; no insert-only trigger by design.
CREATE TABLE search_doc(
  rowid INTEGER PRIMARY KEY, doc_id TEXT NOT NULL, version TEXT NOT NULL, effective_at TEXT, source TEXT, locale TEXT,
  access_level TEXT NOT NULL CHECK(access_level IN ('engineering','quality','operations','restricted')), access_level_given INTEGER NOT NULL,
  reference TEXT, hash TEXT NOT NULL, body TEXT NOT NULL, folded TEXT NOT NULL, ocr_confidence REAL, origin TEXT NOT NULL, load_id TEXT NOT NULL,
  UNIQUE(doc_id, version));
CREATE INDEX search_doc_reference ON search_doc(reference);
CREATE INDEX search_doc_order ON search_doc(effective_at, doc_id);

-- Provenance of every corpus load / drop (insert-only).
CREATE TABLE search_corpus_load(
  load_id TEXT PRIMARY KEY, event TEXT NOT NULL CHECK(event IN ('LOADED','DROPPED')), occurred_at TEXT NOT NULL, actor TEXT NOT NULL,
  origin TEXT NOT NULL, documents INTEGER NOT NULL, archive_items INTEGER NOT NULL, inputs TEXT NOT NULL DEFAULT '{}',
  fts TEXT NOT NULL DEFAULT '{}', label TEXT NOT NULL CHECK(label = 'synthetic, unvalidated'));
CREATE TRIGGER search_corpus_load_no_update BEFORE UPDATE ON search_corpus_load BEGIN SELECT RAISE(ABORT,'E-SEC-RETAINED'); END;
CREATE TRIGGER search_corpus_load_no_delete BEFORE DELETE ON search_corpus_load BEGIN SELECT RAISE(ABORT,'E-SEC-RETAINED'); END;

-- Consistency findings (BEH-ID-07): one open finding per rule + objects + policy version; insert-only; never auto-corrected.
CREATE TABLE consistency_finding(
  finding_id TEXT PRIMARY KEY, rule_ref TEXT NOT NULL, object_refs TEXT NOT NULL, policy_version TEXT NOT NULL, detected_at TEXT NOT NULL,
  status TEXT NOT NULL CHECK(status = 'open'), run_id TEXT NOT NULL, detail TEXT NOT NULL DEFAULT '{}',
  UNIQUE(rule_ref, object_refs, policy_version));
CREATE TRIGGER consistency_finding_no_update BEFORE UPDATE ON consistency_finding BEGIN SELECT RAISE(ABORT,'E-SEC-RETAINED'); END;
CREATE TRIGGER consistency_finding_no_delete BEFORE DELETE ON consistency_finding BEGIN SELECT RAISE(ABORT,'E-SEC-RETAINED'); END;

-- Template drafts (BEH-REV-07, R2 Could): owned by the author, stored exactly as typed, no Zone H power; insert-only.
CREATE TABLE review_draft(
  draft_id TEXT PRIMARY KEY, template_id TEXT NOT NULL, template_version INTEGER NOT NULL, fields TEXT NOT NULL, owner TEXT NOT NULL,
  created_at TEXT NOT NULL, label TEXT NOT NULL CHECK(label = 'synthetic, unvalidated'));
CREATE TRIGGER review_draft_no_update BEFORE UPDATE ON review_draft BEGIN SELECT RAISE(ABORT,'E-SEC-RETAINED'); END;
CREATE TRIGGER review_draft_no_delete BEFORE DELETE ON review_draft BEGIN SELECT RAISE(ABORT,'E-SEC-RETAINED'); END;
