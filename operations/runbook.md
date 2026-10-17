# Operations Runbook

Start using `./run.sh` or `python -m app.server`; query `GET /health`. To regenerate synthetic data, run `python -m app.generate --reset`. The source feed adapter can be inspected with `python -m app.integration`. Logs are emitted on stderr. API process does not mutate core records.

This local simulation contains no access to production customer systems, physical equipment, real credit approvals or pharmaceutical batch disposition.
