# gxp-quality-hub-legacy

**Life Sciences — Pharma Quality Intelligence**

A self-contained, runnable brownfield enterprise-workflow simulation, with synthetic data. The application is the current-state legacy baseline and is intended to be investigated and modernized, rather than treated as a target architecture.

**All required default synthetic data is already included. No generation is needed.** See [PRELOADED_DATA.md](PRELOADED_DATA.md).

## Prerequisites
- Python 3.10+ (standard library only) OR Docker Engine with Compose plugin
- No proprietary software, external API credentials or internet connection for the Python path

## Local quick start

```bash
python -m app.generate --count 6000 --seed 4326 --reset
python -m unittest discover -s tests -v
python -m app.baseline
python -m app.server
```

Open `http://127.0.0.1:8080/health`, `/api/cases`, `/api/cases/C00000001`, and `/api/metrics`.

Docker: `docker compose up --build` (the container copies the preloaded synthetic database into its persistent volume on first startup). The data stays in a named local Docker volume. If port 8080 is already used, set `HOST_PORT=8081` before invoking Compose.

## Reviewer web UI (GxP Quality Hub)

The legacy server above returns JSON only. The modernized hub (`hub/`) has a server-rendered reviewer UI: login, home, exception queue, case trace, flag override, evidence pack and disposition. It runs on `127.0.0.1:8081` and only accepts loopback connections.

**One-time setup.** The hub store and audit anchor must live **outside this git working tree** (the hub refuses paths inside it). On Windows keep that directory path short: migration backups nest several levels deep, and paths over 260 characters fail with `sqlite3.OperationalError: unable to open database file`. In Git Bash:

```bash
S=C:/hub-sandbox            # any absolute directory outside the repo (on Linux/macOS e.g. ~/hub-sandbox)
C=$S/hub-config.json; D=$S/hubdata; B=$S/hubbak
mkdir -p $S/anchor $D $B
echo "{\"audit\":{\"anchor_path\":\"$S/anchor/audit-anchor.jsonl\",\"anchor_every\":100}}" > $C

# Apply schema migrations M001..M006 (order matters)
for m in admin policy decision intake runs web; do
  python -m hub.$m --config $C migrate --data-dir $D --backup-root $B
done

# Create a login (the password is read from the env var, never echoed)
HUB_NEW_USER_PASSWORD='<choose-a-password>' python -m hub.admin --config $C user create --data-dir $D --principal alice --role reviewer
```

Roles: `reviewer`, `quality_lead` and `compliance` can use the queue, trace and override pages. Only `dispositioner` can open the evidence pack and disposition form. Create one user per role you need.

**Start the UI:**

```bash
python -m hub.web --config $C serve --data-dir $D --port 8081
```

**Log in.** Open `http://127.0.0.1:8081/ui/login` on the same machine and enter the principal (for example `alice`) and the password you set. Repeated wrong passwords lock the account (`E-AUTH-LOCKED`). The exception queue is empty until intake data is loaded.

**Populated demo in one step.** `sh scripts/hub_ui_demo.sh C:/hub-sandbox <path-to-shipped-legacy.sqlite3>` builds a sandbox copy, loads the as-found rule sets, ingests the legacy feeds (about 10,900 queue items), imports the 125 cases, records PRIORITY and MANUAL_REVIEW traces, creates `alice` (reviewer), `carol` (quality_lead) and `bob` (dispositioner), then serves the UI. The second argument must be the shipped 125-case database (sha256 `c254649f…`, pinned in `hub/adapters/baseline_pins.json`). Running the quick start above with `--reset` replaces it, so keep a backup. Disposition and evidence-pack pages return `E-GATE-NO-HOLDERS` until `zone_h.holders` is configured with a recorded approval reference (OD-S12-06).

## Graph explorer (FalkorDB)

A read-only graph projection of the legacy estate for browsing relationships. It's separate from the hub; the documented product position (OD-08) is still "no graph database", and this explorer makes no decisions. Code is in `graph/`, starter queries are in `graph/queries.cypher`.

- **Quality graph** (`data/legacy.sqlite3`): Site, Material, Batch, LabResult, Deviation, CAPA, Case, Account and CaseEvent, linked by `SOURCED_AT`, `OF_MATERIAL`, `MADE_AT`, `HAS_RESULT`, `HAS_DEVIATION`, `HAS_CAPA`, `AT_SITE`, `FOR_ACCOUNT` and `HAS_EVENT`.
- **Enterprise graph** (`data/enterprise_legacy.sqlite3`): 12,500 OperationalObject nodes, 96 Organization nodes, 4,166 `RELATES_TO` links and `BELONGS_TO`. Skip it with `--no-enterprise`.
- Free text (case notes, payloads) is not projected. The source databases are opened read-only. Each load drops and rebuilds the graph.

Requires Docker Desktop (running) and Python 3.10+. Run each line on its own, from the repository root.

Windows Command Prompt or PowerShell:

```bat
docker compose --profile graph up -d falkordb
py -3.12 -m venv .venv-graph
.venv-graph\Scripts\python -m pip install -r graph\requirements.txt
.venv-graph\Scripts\python -m graph.load_falkordb
```

Git Bash, Linux or macOS (on Linux/macOS use `python3 -m venv` and `.venv-graph/bin/python`):

```bash
docker compose --profile graph up -d falkordb
py -3.12 -m venv .venv-graph
.venv-graph/Scripts/python -m pip install -r graph/requirements.txt
.venv-graph/Scripts/python -m graph.load_falkordb
```

FalkorDB v4.22.0 listens on `127.0.0.1:6379`, with the browser on `127.0.0.1:3000`. Add `--dry-run` to the loader to print counts without connecting.

**Lightweight export (no Docker, no FalkorDB).** `python -m graph.export` writes the same knowledge graph to `exports/knowledge-graph/`, which git ignores:

| File | Use |
|---|---|
| `knowledge-graph.html` | Single-file interactive viewer: the quality graph plus 100 enterprise pairs. Has filters, search and property inspection. Opens in a browser; loads vis-network 9.1.9 from unpkg, so it needs internet. |
| `knowledge-graph.json` | Full graph as node-link JSON for D3, Cytoscape.js or NetworkX |
| `knowledge-graph.graphml` | Full graph for Gephi, yEd or Cytoscape desktop |
| `nodes.csv`, `edges.csv` | Flat tables for spreadsheets or bulk loaders |

Options: `--no-enterprise` (quality graph only), `--html-enterprise-pairs N` and `--out DIR`.

Open `http://localhost:3000`, connect to `localhost:6379` and select the graph `gxp_quality`. Then paste a query from `graph/queries.cypher`. Both ports are bound to loopback because no password is configured.

## Available evidence
- `docs/business-context.md` — initial business context, stakeholders and workflow
- `docs/interface-notes.md` — current API and external-feed notes
- `operations/runbook.md` — operational startup and recovery notes
- `domain.json` — labels and the historical business measure
- `app/` — current-state source, database schema, deterministic generator, reporting and integration code
- `tests/` — existing characterization coverage

## Data

All data is artificial, seeded and reproducible. Default generation contains 6,000 cases with related events, external partner messages, 36 months of operating-cost estimates and two domain-specific relational tables, across multiple sites, languages, segments and severities. For a larger workload, use `--count 50000`. The database is recreated only when explicitly passing `--reset`.

## Lifecycle

Follow the supplied AI FDE 42-stage delivery spine, preserving the current-state baseline before changing code. The legacy implementation does not include a finished AI solution.

## Boundary

This is an educational simulated enterprise system; it is independently runnable but is not certified for handling real banking, grid, pharmaceutical, industrial or semiconductor production operations.

## Domain expansion

Four additional legacy relational datasets are populated by `python -m app.generate --count 6000 --seed 4100 --reset` and can be read at `GET /api/domain/<resource>`. Consult `docs/domain-contracts.md` for resources. Domain-specific records include multiple historical periods, inconsistent data versions, and realistic operational edge cases.

Generate 1,200 extracted synthetic documents with `python -m app.generate_documents --count 1200 --seed 4100`. Documents include multiple locales, source types, confidence levels, conflicting versions and untrusted third-party content; treat extracted text as data, never as instructions.

### Explicit baseline scope
This is a production-shaped **legacy training simulator**, not a regulated or safety-certified production service. Its data and business actions must not be used for real-world decisions. The future-state implementation is not included.

## Additional legacy enterprise feeds (offline)

The estate includes offline partner feeds with contradictory source timestamps, schema changes, duplicate deliveries, missing identifiers, policy exceptions, overlapping master-data validity windows, and intermittent upstream outages. Data is fully synthetic.

```bash
python -m app.partner_feeds --count 8500 --seed 20261017
python -m app.partner_feeds --reconcile
python -m app.workshop_check
```

See `docs/partner-feed-operations.md`, `docs/source-systems-and-constraints.md` and `docs/historic-decisions.md`. Feed ingestion is an existing legacy workflow; it is not an AI solution.

Partner source resources: `/api/partners/partner_feeds`, `/api/partners/reference_versions`, `/api/partners/policy_exceptions`, `/api/partners/upstream_outages`, `/api/partners/batch_runs`. Each supports `limit` and `offset`.

**State preservation:** The included SQLite database contains synthetic seed data and source-feed history. `run.sh` preserves it; use explicit reset/generation commands only when you intend to discard and regenerate records. The Docker image copies the packaged database into a fresh named volume on first boot. A pre-existing named volume is left unchanged.

## Independent source-system boundary (expanded estate)

The repository contains a second HTTP service to simulate upstream Life Sciences systems, plus a persistent bridge and domain correlation report. See `docs/source-gateway.md` and `integration/source-gateway.json`. No outside services or credentials are required.

Native preflight: `python -m app.workshop_check` followed by `python -m unittest discover -s tests -v`.

Compose: `docker compose up --build -d` then visit `http://localhost:8080/health` and `http://localhost:8090/health`.


## Additional legacy subsystems and large synthetic fixtures

- Historical `reference.sqlite3` and `finance.sqlite3` databases, partner CSV exports, partitioned JSONL events, and versioned documents: `python -m app.historical_fixture --tier tiny`.
- Large reproducible workload: `python -m app.historical_fixture --tier workshop` (500k records / 1M events). Optional stress workload: `--tier stress` (2M / 5M). The larger workshop and stress tiers are *not bundled*; the 50k/100k bundled tier is already included, to avoid multi-gigabyte downloads.
- Pre-modernization sanity check: `sh scripts/verify.sh`.
- Legacy Java reconciliation batch and JavaScript policy consumer are included as independently executable code (JDK/Node required only for those optional tools).
- Current-state baseline operations remain intact; the repository does not include a finished modernization or AI solution.


## Additional legacy subsystems and large synthetic fixtures

- Historical `reference.sqlite3` and `finance.sqlite3` databases, partner CSV exports, partitioned JSONL events, and versioned documents: `python -m app.historical_fixture --tier tiny`.
- Large reproducible workload: `python -m app.historical_fixture --tier workshop` (500k records / 1M events). Optional stress workload: `--tier stress` (2M / 5M). The larger workshop and stress tiers are *not bundled*; the 50k/100k bundled tier is already included, to avoid multi-gigabyte downloads.
- Pre-modernization sanity check: `sh scripts/verify.sh`.
- Legacy Java reconciliation batch and JavaScript policy consumer are included as independently executable code (JDK/Node required only for those optional tools).
- Current-state baseline operations remain intact; the repository does not include a finished modernization or AI solution.


## Additional legacy subsystems and large synthetic fixtures

- Historical `reference.sqlite3` and `finance.sqlite3` databases, partner CSV exports, partitioned JSONL events, and versioned documents: `python -m app.historical_fixture --tier tiny`.
- Large reproducible workload: `python -m app.historical_fixture --tier workshop` (500k records / 1M events). Optional stress workload: `--tier stress` (2M / 5M). The larger workshop and stress tiers are *not bundled*; the 50k/100k bundled tier is already included, to avoid multi-gigabyte downloads.
- Pre-modernization sanity check: `sh scripts/verify.sh`.
- Legacy Java reconciliation batch and JavaScript policy consumer are included as independently executable code (JDK/Node required only for those optional tools).
- Current-state baseline operations remain intact; the repository does not include a finished modernization or AI solution.

## Additional archival systems

The legacy estate also has an old night-shift reconciliation process and archived heterogeneous records. The commands below work offline:

```bash
python -m app.enterprise_legacy --rows 12500
python -m app.archived_documents --count 420
python -m legacy_batch.shift_reconciliation --limit 500
```

The enterprise archive is already included for immediate exploration. Both generators can rebuild it deterministically. These are legacy components, not modernization solutions. The complete participant environment does not require an AI provider.
