-- M000 (Stage 15 INC-02) - docs/14-transformation/schema-migration-plan.md row M000.
-- DDL ADDENDUM to docs/12-specs/contracts/ddl/hub-schema-v0.1.sql (that file is not edited in place, HAR-13):
--   schema_migrations   (not in DDL v0.1)
--   deviation_register  (BEH-CO-02 defines it; DDL v0.1 omits it)
--   coexistence_inventory (BEH-CO-05; DDL v0.1 omits it)
-- Synthetic, unvalidated. Rollback: delete the sandbox hub.sqlite3 (no data of value yet).

CREATE TABLE IF NOT EXISTS schema_migrations (
  version    TEXT PRIMARY KEY,
  sha256     TEXT NOT NULL,
  applied_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS deviation_register (
  dev_id        TEXT PRIMARY KEY CHECK (dev_id GLOB 'DV-[0-9][0-9]*'),
  golden_ref    TEXT NOT NULL,
  legacy_value  TEXT NOT NULL,
  new_value     TEXT NOT NULL,
  justification TEXT NOT NULL,
  approval_ref  TEXT,
  status        TEXT NOT NULL DEFAULT 'proposed' CHECK (status IN ('proposed', 'approved', 'rejected')),
  CHECK (status <> 'approved' OR (approval_ref IS NOT NULL AND length(trim(approval_ref)) > 0))
);

CREATE TABLE IF NOT EXISTS coexistence_inventory (
  item_id     TEXT PRIMARY KEY,
  description TEXT NOT NULL,
  owner       TEXT NOT NULL,
  status      TEXT NOT NULL
);

-- BEH-CO-05: protected workflows cannot be altered or retired by the product.
CREATE TRIGGER IF NOT EXISTS coexistence_inventory_no_update
BEFORE UPDATE ON coexistence_inventory
BEGIN SELECT RAISE(ABORT, 'E-CO-PROTECTED-WORKFLOW'); END;

CREATE TRIGGER IF NOT EXISTS coexistence_inventory_no_delete
BEFORE DELETE ON coexistence_inventory
BEGIN SELECT RAISE(ABORT, 'E-CO-PROTECTED-WORKFLOW'); END;
