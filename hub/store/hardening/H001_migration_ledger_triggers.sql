-- H001 (Stage 27 S24 DQ-S24-09 / RS-12): the core migration ledger becomes insert-only.
-- schema_migrations (M000) shipped without triggers; drift was only detected by the sha256 comparison in hub.store.migrate.check. A row can now be
-- neither changed nor removed through SQL (E-SEC-RETAINED, same error text as every other ledger). Rows are still inserted by the runners.
CREATE TRIGGER IF NOT EXISTS schema_migrations_no_update BEFORE UPDATE ON schema_migrations BEGIN SELECT RAISE(ABORT,'E-SEC-RETAINED'); END;
CREATE TRIGGER IF NOT EXISTS schema_migrations_no_delete BEFORE DELETE ON schema_migrations BEGIN SELECT RAISE(ABORT,'E-SEC-RETAINED'); END;
