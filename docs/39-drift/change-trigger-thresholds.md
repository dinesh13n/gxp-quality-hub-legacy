---
stage: "39 — Drift + Continuous Improvement"
artifact: "change-trigger-thresholds.md"
version: "v0.1"
date: "2026-10-25"
author_agent: "claude-fde-agent (Stage 39 run)"
status: "DRAFT"
evidence_sources: ["docs/39-drift/*.md", "hub/obs/alerts.py", "hub/obs/slo.py", "docs/31-observability/error-budget-policy.md", "docs/26-tevv/release-thresholds.md", "docs/29-incident-bcdr/incident-severity-matrix.md", "docs/37-operating-model/change-governance.md", ".fde/orchestrator-decisions.md (OD-24, OD-32, OD-34, OD-36)"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated against any organisation. Documentation only (Stage 39 adds files under `docs/39-drift/` and changes nothing else). The product is No-AI (OD-08), not in production, loopback-only, synthetic data only; there is no production telemetry (OD-04). "Drift" here means DETERMINISTIC drift (rule-set, configuration, schema, golden/characterization, dependency/runtime, synthetic-baseline data, documentation-vs-code, ownership). No model, embedding or prompt drift is invented. Every threshold, cadence and window is a CANDIDATE ASSUMPTION written by the agent under OD-32, not a commitment, not a measured need, and not approved by Dinesh Naik. No risk is accepted here.**

## Summary
Sixteen triggers TRG-01..TRG-16 that move a signal from WATCH to INVESTIGATE or from INVESTIGATE to a controlled change. **Every number is a CANDIDATE ASSUMPTION** (OD-32); none was measured, none is a commitment, none is an SLA. Where Stage 26 or 31 already declared a threshold, it is reused unchanged and cited; where no anchor exists the trigger is a binary condition or a dated event instead of an invented number. Following the Stage 26 rule, a threshold is not edited after results exist to change an outcome: a change is a new version with a "changed after results" mark.

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
### TT-1 Trigger table
Tier: W = WATCH, I = INVESTIGATE, C = CHANGE request (class per `change-governance.md`), X = incident (Stage 29 severity), not drift.

| ID | Condition (candidate) | Source of the number | Tier / class | Owner role (interim) | Signal detail |
|---|---|---|---|---|---|
| TRG-01 | `model_calls_total` > 0, `egress_attempts_total` > 0, or `zone_h_service_actor_accepted` > 0, or the metric is absent | reused: ALT-01/02/03, INV-01..03 (Stage 31); RT-05 | X (SEV-B / SEV-A) | Engagement lead (Dinesh Naik) | PM-01, PM-02; never waived by an agent (HAR-11, TP-14) |
| TRG-02 | any sha256 mismatch: as-found pins, legacy baseline pins, FX-BASE125, golden MANIFEST | reused: pin files ("changing a pin = reviewed PR") | I, then C2 if intended | RL-02 service owner (Dinesh, interim) | PM-06, DM-02, DM-03 |
| TRG-03 | `sha256sum -c ../_data-backup-2026-10-17/SHA256SUMS.txt` rc != 0 | reused: RT-04, OD-03a | I immediately; all runs stop | Engagement lead (Dinesh Naik) | DM-01 |
| TRG-04 | **Dated:** 2026-10-31 (end of life of Python 3.10 per public schedule, to be confirmed: A-39-09). Candidate: have 3.12+ regression and characterization evidence recorded, and a decision on D-27-02, before the date; if not by the date, open an INVESTIGATE item that re-states exposure | date: Assumption; requirement: RT-14, OD-24 | I on the date; C6 for the floor move | Engagement lead (Dinesh Naik) | PM-12; today is 2026-10-25, six days before the date; no 3.12+ evidence exists (OD-33) so this will almost certainly be INVESTIGATE on the day |
| TRG-05 | characterization: any failing CT other than CT-13 with the recorded signature; or CT-13's stderr signature changes beyond the Node patch string; or the recorded Node/Java/Python/SQLite versions differ from the last evaluation | reused: RT-03; signature from S24-DEV-04 | I; C2/C6 to re-baseline | RL-02 (Dinesh, interim) | PM-09, PM-11, PM-15 |
| TRG-06 | full hub regression: any FAIL or ERROR in any group, or executed != expected, on `main` or on a stage branch before merge | reused: RT-01; OD-23, OD-27 | I; no merge | RL-02 (Dinesh, interim) | AM-05; device cap 180 s per call (OD-21) shapes how it is run |
| TRG-07 | a config key or flag changes value vs the recorded decided value without an `approval_ref`; or an unknown key is accepted | reused: closed key schema (Stage 27 `E-CFG-INVALID`), DW-17 | C3 / C5 | Engagement lead (Dinesh Naik) | PM-10 |
| TRG-08 | active rule sets > 0, or `zone_h.holders` non-empty, without a recorded decision | reused: OD-16, OD-17, OD-31 (shipped 0 / EMPTY) | C4 | RL-03 proposes, RL-04 activates (both VACANT; Dinesh decides) | PM-07 |
| TRG-09 | any SLO candidate state RED or EXHAUSTED (budget < 10 %), per Stage 31 states; or ALT-06..ALT-12 firing | reused: A-31-03 (50 / 10 %), A-31-04..07 | I; error-budget-policy EB-3 | Engagement lead (Dinesh Naik) | DC-8; no traffic exists, so these cannot fire from real use yet |
| TRG-10 | a doc-vs-code test fails (D03, C05, A01 and any successor) | reused: Stage 31 tests | C0 (fix the doc) or C1 (fix code) | RL-02 (Dinesh, interim) | KM-01, KM-02 |
| TRG-11 | an open decision or risk has no owner at an evaluation, or is open at a stated trigger event (pilot start, production exposure, real data) | trigger events from Stage 34/35/37; no due dates exist | I | Engagement lead (Dinesh Naik) | KM-06, KM-07 |
| TRG-12 | a new third-party import, dependency, CI action, base-image change, or a runtime upgrade | reused: C6 class; RT-05 | C6 (ADR + decision) | Engagement lead (Dinesh Naik) | PM-03, PM-04, PM-14 |
| TRG-13 | **Event:** a real after-window, pilot, production exposure, real data, a non-loopback bind, a second human reviewer, or any real stakeholder/owner is named | Stage 34 D-34-01/02, Stage 36 PC-1..10, HAR-15 | C5/C8; re-derive thresholds from the first 30 days of real data (D-31-10 / A-31-06); re-run Stage 34/35/36 as v0.2 (OD-36) | Engagement lead (Dinesh Naik) | all candidate thresholds in this stage lose their status as candidates only through this step |
| TRG-14 | baseline distribution snapshot differs: candidate total-variation distance > 0.10 on a categorical field, or a category appears/disappears | Assumption A-39-05 (placeholder form; no snapshot exists) | I | RL-02 (Dinesh, interim) | DM-05; blocked until G-39-01 closes |
| TRG-15 | migration file set and `schema_migrations` rows disagree, or an applied migration's body changed | reused: A-27-05 insert-only trigger; Stage 20-27 migrations | I, then C1/C2 | RL-02 (Dinesh, interim) | DM-07 |
| TRG-16 | search engine in use changes without a config/runtime change; index/corpus count mismatch after a load; golden-query order changes | Assumption; blocked until G-39-05 | I | RL-02 (Dinesh, interim) | RM-01..RM-03 |

### TT-2 Reuse versus invention [Verified Fact: counts from the table]
Reused from earlier stages: TRG-01, 02, 03, 05, 06, 07, 08, 09, 10, 12, 15 (11 of 16). Dated or event-based, no number: TRG-04, 11, 13. Invented-by-agent placeholders: TRG-14 (0.10), TRG-16. No latency, throughput, cost, adoption or value threshold is proposed (see `drift-framework.md` DF-5).

### TT-3 Threshold lifecycle
A threshold is DRAFT (this document), then PROPOSED when Dinesh accepts the form, then CALIBRATED only after TRG-13 supplies real data. No threshold becomes a commitment or an SLA through this document (Stage 31 SD-4 stands).

## Evidence References
See header.

## Assumptions
- A-39-12 The Python 3.10 end-of-life date of 2026-10-31 is from public release schedules, not verified in the session. Confirm: Dinesh.
- A-39-13 TRG-14's 0.10 and the WATCH/INVESTIGATE split are placeholders.
- A-39-14 Owner roles follow `change-governance.md`; every non-Dinesh role is VACANT (OD-34), so "owner" means Dinesh by interim default, which is not an accepted assignment.

## Unknowns
- U-39-10 What response time anyone expects after a trigger: none exists, and none is invented (no SLA).

## Unresolved Issues
- TRG-04 will arrive before D-27-02 is decided unless Dinesh decides first.

## Residual Risks
- RR-39-10 Sensitive-by-default thresholds with no traffic may produce noise once traffic exists; or insensitive ones may miss; neither can be assessed now. Low now.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-25 | claude-fde-agent | First issue (Stage 39). |
