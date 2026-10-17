# Preloaded participant data — independent offline deployment

This archive already includes **all datasets required for the default workshop**. Do not run any generator or reset command during initial setup. The legacy services read packaged files and databases as-is.

## Preloaded contents

- `data/legacy.sqlite3` — populated current-state operational and partner-feed database.
- `data/enterprise_legacy.sqlite3` — populated relational enterprise estate.
- `data/lake/tiny/` — historical starter fixture, reference/finance databases, partner export, 60 monthly event partitions, versioned documents.
- `data/lake/bundled/` — **50,000 additional historical transactions, 100,000 historical events, 600 documents**, supporting reference and finance databases and exported partner data.
- `data/documents/`, `data/archive_documents/` — synthetic operational, historical email/HTML documents.
- Historical source feed files, incident evidence, policies, and domain-specific records under `data/`, `docs/`, `operations/`.

The `workshop` (500k/1M) and `stress` (2M/5M) tiers are **not** included; neither is required for the standard workshop. They are optional performance experiments only. Do not conflate those optional targets with preloaded data.

## No-generation quick start

Python 3.10+ (standard library only):

```sh
python scripts/offline_inventory.py
python -m app.workshop_check
python -m unittest discover -s tests -q
python -m app.baseline
python -m app.server
```

Open http://127.0.0.1:8080/health and http://127.0.0.1:8080/api/metrics. In additional terminals you may run `python -m services.source_gateway.server` and `python -m app.gateway_bridge --limit 50` to exercise the upstream simulator. The bridge intentionally mutates operational ingestion state; start from a copied working tree if you need a pristine baseline.

Do not start two repositories simultaneously on the default ports. Set `PORT` and `SOURCE_PORT` or use the Compose host-port variables as needed. Docker Compose support is provided but has not been executed in the release-building environment.

## Preservation

Keep an untouched copy of the original ZIP and compare business KPIs before modernization. No actual customer, employee, or patient records appear in these generated fixtures. This is a synthetic legacy **training environment**, not a validated production system.
