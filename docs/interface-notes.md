# Current Integration Notes

Upstream partner feeds are represented by `source_messages`, preserving original JSON payloads and `schema_version`. The existing adapter in `app/integration.py` reads them in arrival order.

Routes: `GET /health`, `GET /api/cases`, `GET /api/cases/{id}`, `GET /api/metrics`, and `GET /api/incidents`.

Data stores: SQLite for standalone execution; historical deployment descriptions mention SQL Server/Oracle, which is not required for local startup. No vendor credentials are needed.

Historical change log excerpt:
- 2019: feed intake integrated with core cases
- 2021: status mappings amended after regional expansion
- 2023: server moved from a shared host to a container host
- 2025: reporting team implemented new monthly operating metrics
