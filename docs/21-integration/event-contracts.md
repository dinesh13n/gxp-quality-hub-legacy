---
stage: "21 — Enterprise Integration"
artifact: "event-contracts.md"
version: "v0.1"
date: "2026-10-21"
author_agent: "claude-fde-agent"
status: "IN REVIEW"
evidence_sources: ["docs/12-specs/event-contracts.md (EV-1..EV-5)", "docs/05-current-state/integration-landscape.md IL-02, IL-05, IL-C", "hub/intake/service.py (intake_run_event, audit INTAKE_RUN / INTAKE_RUN_FAILED / CONTRACT_BINDING_CHANGED)", "hub/intake/migrations/M004_intake.sql", "hub/runs/sources.py (OrderedSource, RTD-61)", "services/source_gateway/server.py", "docs/21-integration/evidence/gateway-stub-conformance.json", "tests/hub/test_tst_hub_stg21_integration.py S02, S04, S07", "tests/hub/test_inc06_supplementary.py S06, S09, S14", "tests/hub/test_tst_run_01_15_runs.py TST-RUN-05..14"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated. There is no event infrastructure (no broker, queue, topic or webhook); "events" are rows in append-only tables or items of a pulled HTTP page.**

## Summary
Integration events fall into three groups: (1) **consumed** - gateway events pulled from the loopback stub (and the legacy `gateway_inbox` / `partner_feeds` rows read as deliveries); (2) **recorded by the hub about integration runs** - `intake_run_event` (RUN_STARTED / RUN_CHECKPOINT / RUN_FINISHED / RUN_FAILED), `raw_intake` + `intake_outcome` (EV-INT-01..03), and one hash-chained audit record per run (`INTAKE_RUN`, `INTAKE_RUN_FAILED`) or binding change (`CONTRACT_BINDING_CHANGED`, EV-POL-12, Zone H); (3) **published** - none: the hub emits no event to another system. Delivery is **pull, at-least-once, idempotent at the hub** (natural key + content hash); **ordering is not guaranteed** by any source and the hub does not rely on it, except the INC-07 job checkpoint, whose late-arrival limitation (RTD-61) is now characterised by a test (STG21 S07).

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
### EC-1 Consumed event streams
| Stream | Producer | Delivery | Identity / dedupe in the hub | Ordering facts | Evidence | Tag |
|---|---|---|---|---|---|---|
| gateway events (`/api/events`) | `services/source_gateway/server.py` | pull by offset page; the same offset returns the same events (deterministic `message_id`) | natural key (partner=system, record_kind=event_type, ref_id=business_key, source_ts=occurred_at) + content hash; re-pull -> NOOP_DUPLICATE | `occurred_at` / `published_at` are formulae of the offset; 10 / 125 events are "published" before they "occurred" | S02 | [Verified Fact] |
| legacy partner feed rows | legacy generator (`app/partner_feeds.py`) | batch read of the table | natural key (OD-18) + content hash; 67 REPLAY rows -> NOOP_DUPLICATE | 2,234 / 8,567 rows have `source_ts` > `ingest_ts` | TST-INT-05, S07 | [Verified Fact] |
| legacy `source_messages`, `gateway_inbox` | legacy app / bridge | batch read | as above | ordered by `received_at` in the reader | INC06 S11 | [Verified Fact] |

### EC-2 Hub integration-run events (append-only)
| Event | Table / stream | When | Body | Guarantee | Evidence | Tag |
|---|---|---|---|---|---|---|
| RUN_STARTED | `intake_run_event` | first row of every run | `received`, `binding_mode` | same transaction as the items | INC06 S06 | [Verified Fact] |
| RUN_CHECKPOINT | `intake_run_event` | gateway pull after the page is stored | `{next_offset, attempts}` (hub-owned offset) | written in the same transaction as the page | S02 (checkpoint 125), INC06 S09 | [Verified Fact] |
| RUN_FINISHED | `intake_run_event` | end of run | received, stored, skipped_existing, outcomes | one transaction per run: all or nothing | INC06 S06 | [Verified Fact] |
| RUN_FAILED | `intake_run_event` | source unreachable / timeout | `{error: SOURCE_UNREACHABLE, details}`; **no item row** | + audit `INTAKE_RUN_FAILED` outcome `error` | TST-INT-26, S04 | [Verified Fact] |
| raw_intake / intake_outcome | EV-INT-01..03 | per delivery / per (re)classification | verbatim bytes; outcome_seq history | insert-only triggers | INC06 S05 | [Verified Fact] |
| audit INTAKE_RUN | `audit_log` (hash chain) | per run | counts + `outcomes_digest` | chain verified (`verify-audit`) | INC06 S06 | [Verified Fact] |
| CONTRACT_BINDING_CHANGED | `policy_events` + audit (EV-POL-12) | Zone H ZH-10 only | source, from/to mode | impossible while holders are empty | INC06 S04 | [Verified Fact] |
| run_event (INC-07 jobs) | `run_event` (EV-RUN-01..05) | scheduled / manual jobs (scheduler OFF) | order-key checkpoint `[source_ts, source_key, n]` | resume without duplicates (TST-RUN-07) | TST-RUN-05..14 | [Verified Fact] |

### EC-3 Findings register
| ID | Finding | Evidence | Impact | Risk | Confidence | Open question |
|---|---|---|---|---|---|---|
| EF-01 | No source guarantees order; the hub's identity does not depend on order (natural key + hash), so duplicates and re-pulls are harmless | S02 stale re-pull 125 -> NOOP, totals unchanged; TST-INT-04/05 | replay-safe | Low | High | — |
| EF-02 | RTD-61: an INC-07 job resumed from a checkpoint does not see a delivery that appears later with an earlier `source_ts`; the idempotent catch-up (`hub.intake ingest-legacy`, `idempotent_backfill`) stores exactly that item | S07 (characterised, no behaviour change) | late items wait for a catch-up run; with the scheduler OFF, catch-up is a manual operator action | Medium | High | DQ-S21-06: should a scheduled job also run the catch-up (Stage 28 resilience)? |
| EF-03 | EV-RUN-02 names checkpoint body `{receipt_time, raw_id}`; the intake gateway checkpoint is `{next_offset, attempts}` and the INC-07 job checkpoint is an order key (DEV-66) | `event-contracts.md` EV-RUN-02; `hub/runs/sources.py` docstring | spec text lags code | Low | High | Stage 12 v0.2 addendum (DW-13) |
| EF-04 | The hub publishes no events; downstream systems can only pull (HTTP / CLI) | II-1 | consumers of hub outputs must be added deliberately (Stage 30) | Low | High | — |

## Evidence References
- STG21 S02 / S04 / S07; INC06 S05 / S06 / S09 / S14; TST-INT-04/05/26; TST-RUN-05..14.

## Assumptions
- A-21-EC-1 [Assumption] Pull-only integration remains acceptable for R1 (no push / webhook requirement exists in the approved PRD). Confirm: Engagement lead (Dinesh Naik).

## Unknowns
- U-21-EC-1 Real upstream delivery guarantees (exactly-once, ordering, retention window) - no real source; Engagement lead (Dinesh Naik).
- U-21-EC-2 Freshness expectation: the archived "partner feed accepted within 4 hours / stale risk signal 24 hours" targets (`docs/operations-service-levels.md`) are not measured guarantees; whether they apply to the hub is open (Stage 31 SLOs).

## Unresolved Issues
- EF-02 catch-up policy; EF-03 spec addendum.

## Residual Risks
- RR-21-EC-1 Late deliveries stay invisible to a resumed job until the next catch-up (Medium; observable through queue ages / backlog).

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-21 | claude-fde-agent | First issue. |
