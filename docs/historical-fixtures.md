# Historical data and external-file estate
This repository includes a legacy API and source simulator, plus a reproducible historical workload generator. Run `python -m app.historical_fixture --tier tiny` for a small, fast fixture. The `workshop` tier generates **500,000 transactions, 1,000,000 events, and 600 documents**, and `stress` generates **2,000,000 transactions, 5,000,000 events, and 1,000 documents**; larger tiers take longer and require significant disk space. All historical assets are synthetic and are generated under `data/lake/` independently of the preloaded `data/legacy.sqlite3`. Do not commit generated large fixtures.

Use `python -m app.historical_estate data/lake/tiny/partner_export.csv` to ingest a flat-file partner export. Java 17+: `javac legacy_java/ReconcileLegacy.java && java -cp legacy_java ReconcileLegacy data/lake/tiny/partner_export.csv`; Node 18+: `node legacy_js/legacy_policy.js`. These are **legacy reconciliation consumers** and reflect the inconsistent business logic commonly found in brownfield estates.

Domain event types: batch_exception, oos_lab, capa_action, sop_change.

Legacy business rules may disagree with the policy archive: investigate before changing behavior.
