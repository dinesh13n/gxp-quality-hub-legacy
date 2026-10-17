# Domain records and local endpoints

- `GET /api/domain/deviations?limit=20&offset=0` — relational record with schema `deviation_id TEXT PRIMARY KEY, batch_id TEXT NOT NULL REFERENCES batch_records(batch_id), opened_at TEXT NOT NULL, classification TEXT NOT NULL, root_cause TEXT, status TEXT NOT NULL`
- `GET /api/domain/lab_results?limit=20&offset=0` — relational record with schema `result_id TEXT PRIMARY KEY, batch_id TEXT NOT NULL REFERENCES batch_records(batch_id), analyte TEXT NOT NULL, result_value REAL, unit TEXT NOT NULL, test_status TEXT NOT NULL, measured_at TEXT NOT NULL`
- `GET /api/domain/capa_actions?limit=20&offset=0` — relational record with schema `capa_id TEXT PRIMARY KEY, deviation_id TEXT NOT NULL REFERENCES deviations(deviation_id), action_owner TEXT NOT NULL, due_at TEXT NOT NULL, state TEXT NOT NULL`
- `GET /api/domain/sop_versions?limit=20&offset=0` — relational record with schema `sop_id TEXT NOT NULL, version TEXT NOT NULL, effective_at TEXT NOT NULL, retired_at TEXT, PRIMARY KEY(sop_id,version)`

All records are synthetic. Resource endpoints expose legacy read models and should not be assumed to be complete domain APIs.
