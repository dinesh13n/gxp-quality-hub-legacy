# Domain data dictionary

The legacy application includes shared intake tables (`cases`, `events`, `source_messages`, `operating_costs`) and these additional domain tables:

- `materials`: material_id TEXT PRIMARY KEY, material_name TEXT NOT NULL, source_site TEXT NOT NULL, spec_version TEXT NOT NULL
- `batch_records`: batch_id TEXT PRIMARY KEY, material_id TEXT NOT NULL REFERENCES materials(material_id), batch_site TEXT NOT NULL, observed_assay REAL NOT NULL, assay_unit TEXT NOT NULL, qa_status TEXT NOT NULL

Rows use synthetic identifiers, local site aliases, valid foreign-key relationships and generated historical values. The site, currency, revision and unit choices reflect multiple inherited operational practices rather than a canonical enterprise data model.

Inspect the joins and semantics before deriving KPIs.
