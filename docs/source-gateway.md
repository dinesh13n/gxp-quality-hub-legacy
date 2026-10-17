# Life Sciences: historical source-system bridge

The estate includes a separate local source-system simulator (`services/source_gateway/server.py`). It exposes `GET /health`, `GET /api/catalog`, `GET /api/events?offset=0&limit=50`, `GET /api/record/<id>`, and `GET /api/failure?mode=timeout|schema|rate_limit`.

A separate `app.gateway_bridge` process ingests events into persistent `gateway_inbox` and tracks offsets. Multiple source systems and replay scenarios are represented; operations are intentionally imperfect and their behavior requires assessment.

This architecture simulates inter-application boundaries locally and never contacts real enterprise systems.

## Native terminal workflow

Run `python -m services.source_gateway.server` in one terminal (port 8090). In another terminal run `python -m app.gateway_bridge --limit 50`. For a domain report run `python -m app.operational_report`. Run the main application on 8080.

## Compose workflow

From an extracted standalone repo run `docker compose up --build -d`; check `docker compose ps` and `docker compose logs bridge`. Shut down with `docker compose down` (preserves data volume). Use `docker compose down -v` only if you deliberately intend to reset data.

Other repositories require separate host ports when run at the same time; set `HOST_PORT` and `SOURCE_HOST_PORT` on each.
