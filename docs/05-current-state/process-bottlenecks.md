---
stage: "5 — Discover Current Process & Brownfield Landscape"
artifact: "process-bottlenecks.md"
version: "v0.1"
date: "2026-10-17"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["app/generate.py", "app/partner_feeds.py", "app/gateway_bridge.py", "app/enterprise_legacy.py", "docs/04-baseline-kpis/proxy-metrics.md", "docs/04-baseline-kpis/baseline-kpi-sheet.md", "operations/incidents/INC-2025-014.md", "docs/historic-decisions.md", "docs/correspondence/operations-vs-risk-2024.md", "data/legacy.sqlite3 (read-only)", "data/enterprise_legacy.sqlite3 (read-only)"]
supersedes: "none"
---
## Summary

Bottlenecks supported by evidence. Important discipline: **wait times in the data are generator parameters, not measurements.** Stage 4 proxies (first review median 12.06 h; evidence arrival lag median 36 h; open-case age median 565 d) are shown below to be mechanically bounded or random by construction, so they are *not* bottleneck evidence. Defensible bottleneck evidence is (1) structural (capacity limits and manual triggers visible in code), (2) stock/queue sizes at the snapshot, and (3) documented claims. Each row carries finding, evidence, impact, risk, confidence, open question as the stage prompt requires.

## Findings

### PB-A. Why the Stage 4 proxies cannot be read as bottleneck evidence

| ID | Proxy | Construction in code | Consequence | Class |
|---|---|---|---|---|
| PB-00a | P-01 created→first review (max 27.53 h) | `etime = created + randint(1,300) min`; review event = `etime + randint(0,24) h` (`app/generate.py`); so the value can never exceed 5 h + 24 h = 29 h whatever the "process" | The 12 h median is the mean of two uniform draws, not a queue delay | [Verified Fact] |
| PB-00b | P-03 evidence arrival lag (median 36 h, none negative) | `arrival = t + ((i*3) % 72) h` (`app/enterprise_legacy.py` L43): a deterministic sawtooth, max 69 h | Median equals design; no signal | [Verified Fact] |
| PB-00c | P-04 / K-09 open-case age (median 565 d) | Case date uniform over 1,100 days; status drawn independently of date (`states` weights 35/25/28/8/4 %) | Age of OPEN cases is the age of a random date; no ageing mechanism | [Verified Fact] |
| PB-00d | Lake events / gateway timestamps | Gateway `occurred_at` = `2025-03-{n%28}T{n%24}:00` formula; 92 lake events carry impossible dates | Not usable as flow times | [Verified Fact] |

### PB-B. Bottleneck register

| ID | Bottleneck | Evidence | Impact | Risk | Confidence | Unresolved question | Class |
|---|---|---|---|---|---|---|---|
| BN-01 | **Manual trigger + capped reconcile**: `--reconcile` handles at most 1,000 rows per run; shipped backlog 8,567 (8,000 NEW + 500 RETRY + 67 REPLAY) = 9 runs; nothing schedules a run | `app/partner_feeds.py` `reconcile(limit=1000)`; `GROUP BY processing_status`; no scheduler (grep) | Feed-driven work waits for a human to start the job; backlog grows with any pause | Late or missing reconciliation, divergence of totals (cf. INC-2025-014) | High (code) / Medium (impact) | Real feed volume and run cadence | [Verified Fact] code; [Inference] impact |
| BN-02 | **Decision step outside the system**: no write path for decisions or dispositions | Absence of any INSERT/UPDATE on `cases.status`; API GET-only | Throughput of the core step cannot be measured or improved from system data | Control and traceability live in unknown tools | High | Where/how decisions are made (U-05-02) | [Verified Fact] |
| BN-03 | **Closure definition conflict** (48 h vs evidence vs finance "resolved") | `operations-vs-risk-2024.md`; `business-context.md` L19 | Ops target and compliance rule collide, so the closing step is where cases can stall or be closed prematurely | Either speed pressure on evidence quality or unbounded dwell | High (docs say so) | Clock start/stop, owner of the definition | [Verified Fact] (claim) |
| BN-04 | **Backlog stock at snapshot**: 89 of 125 cases not CLOSED (71%); 29 flagged high-severity or escalated/reopened; of non-closed, 25 need manual review; 17 on the `review` list, 2 `urgent` | SQL on `cases` + `legacy_logic.py` | Manual-review population is 28% of open work | Unmeasured dwell time | Medium (stock only) | Arrival/closure rates to turn stock into wait | [Verified Fact] counts; flow [Unknown] |
| BN-05 | **Batch quality stock**: batch_records QA_HOLD 42 + REVIEW 50 of 125 (74%) not CLOSED; deviations OPEN 14 + INVESTIGATION 16 of 42 (71%); CAPA OPEN 7 + OVERDUE 6 of 21 (62%) | SQL | Large share of the domain records sit in intermediate states | Synthetic proportions - do not generalise | Low | Real distribution | [Verified Fact] on data |
| BN-06 | **Overdue handling not derived**: all 13 non-verified CAPA actions have `due_at` before the dataset snapshot (2023 dates), yet only 6 are marked OVERDUE (7 remain OPEN) | SQL `capa_actions` vs 2025-12-19 | State is stored, not computed; overdue work is invisible unless someone sets the flag | Missed CAPA deadlines (GxP) | Medium (synthetic snapshot choice A-04-03) | Who sets OVERDUE, when | [Verified Fact] |
| BN-07 | **Unassigned queue items**: 695 of 6,250 workflow tasks (11%) have no assignee | `workflow_tasks.assigned_to IS NULL` | Items with no owner cannot age out visibly | Work stalls unnoticed | Medium (rule `i%9==0` is a generator pattern) | Real assignment practice | [Verified Fact] data |
| BN-08 | **Row multiplication slows and distorts night shift** | `shift_reconciliation.py` LEFT JOIN: `--limit 500` covered 118 distinct objects (0A WF-07) | Reviewers receive repeated lines; capacity spent on duplicates | Over-counting totals per tenant | High | Whether output is read by anyone | [Verified Fact] |
| BN-09 | **Replay storms**: all REPLAY rows treated as duplicates without content comparison; 2025 rollout rolled back after replay inflated the exception queue | `app/partner_feeds.py` L65; `historic-decisions.md` 2025 | Exception queue inflation and, in the other direction, discarding a corrected replay | Quality exceptions mishandled | Medium | Frequency of corrected vs identical replays | [Verified Fact] code; claim for 2025 |
| BN-10 | **Single shared SQLite file** for API, bridge, reconcile and reports | `app/store.py` (`timeout=15`, `busy_timeout=15000`) | Writers block each other; a long reconcile blocks API writes/DDL (`init()` on partner routes) | Lock waits up to 15 s then error [Inference] | Low | Concurrency in real deployment | [Verified Fact] config; [Inference] effect |
| BN-11 | **Month-end double computation** (Java float / SQL join / API counts) | `ReconcileLegacy.java`, `legacy_reports.sql`, `/api/metrics` | Reconciliation effort repeated to explain differences (K-10: 8 of 36 months agree) | Finance/ops disagreement | Medium | Effort per month (U-24) | [Verified Fact] code; effort [Unknown] |

## Evidence References

`app/generate.py` (event/offset formulae); `app/enterprise_legacy.py` L43, L47; `app/partner_feeds.py` L60-71; `app/store.py`; SQL (read-only, immutable) on `cases`, `batch_records`, `deviations`, `capa_actions`, `workflow_tasks`, `partner_feeds`; `docs/04-baseline-kpis/proxy-metrics.md` P-01..P-04.

## Assumptions

- A-05-10: Stock counts (BN-04..BN-07) are acceptable as bottleneck *indicators* only; they are not wait times. Confirm: Engagement lead (Dinesh Naik).

## Unknowns

- U-05-18 Any real cycle time, queue age or throughput. U-05-19 Whether BN-01 is a bottleneck in practice (needs real feed volumes).

## Unresolved Issues

- Stage 4's proxies P-01, P-03, P-04 should be re-labelled "generator-bounded, not evidence of flow" in any later reuse (see `current-state-summary.md` CS-D).

## Residual Risks

- Risk of optimising against synthetic wait times; risk that the true bottleneck (BN-02, the human decision step) is unmeasurable until instrumentation exists.

## Change History

| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-17 | claude-fde-agent | Initial Stage 5 discovery draft (read-only; no application code executed; SQLite opened `mode=ro&immutable=1`). |
