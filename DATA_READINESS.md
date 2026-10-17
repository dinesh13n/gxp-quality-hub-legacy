# Data readiness — gxp-quality-hub legacy

Every dataset required for the standard offline capstone is **included in this archive**. Do not seed or generate data before the first run.

Run `python scripts/verify_preloaded.py` to confirm packaged datasets and referential integrity. This command reads data only.

## Preloaded historical tiers

| Tier | Transactions | Events | Documents |
|---|---:|---:|---:|
| tiny | 2,400 | 9,500 | 360 |
| bundled | 50,000 | 100,000 | 600 |

Operational and enterprise relational databases, domain documents, supplier/partner feeds, and historical artifacts are also preloaded under `data/`.

## Offline startup (no data generation)

```sh
python scripts/verify_preloaded.py
python -m app.workshop_check
python -m unittest discover -s tests -q
python -m app.server
```

No LLM credentials, cloud APIs, enterprise software, or external dataset downloads are needed for the baseline Python workshop. Python 3.10+ is required. Docker runtime/cross-platform compatibility is not certified by this package.

The source is a legacy training system and contains intentional brownfield deficiencies; do not interpret test success as production safety certification.
