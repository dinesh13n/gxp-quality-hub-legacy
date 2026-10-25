---
stage: "40 — Scale / 90-Day Transformation Roadmap"
artifact: "accelerator-pack.md"
version: "v0.1"
date: "2026-10-25"
author_agent: "claude-fde-agent (Stage 40 run)"
status: "DRAFT"
evidence_sources: ["docs/40-scale/reusable-components.md", "docs/40-scale/pattern-catalog.md", "docs/26-tevv/", "docs/27-hardening/production-readiness-checklist.md", "docs/14-transformation/", "integration/source-contract-v1.json", "docs/36-roi/roi-model.md", "docs/37-operating-model/"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated against any organisation. Documentation only. PROPOSAL: the pack is a manifest of what could be packaged. Nothing is built, moved or copied by this stage. No value claim, no cutover scheduled, no risk accepted for Dinesh Naik.**

## Summary
Eight accelerators assembled only from assets that have a cited basis in `reusable-components.md` (tier A or B) or `pattern-catalog.md`. Each entry says what it contains, what must be generalised first, and what is deliberately left out (first-use-case debt). **No accelerator has been used by a second team**, so none is "proven"; the claim made is "extractable with the listed work". The pack's purpose is to cut the cost of the *next* unit, but **how much it would cut is Unknown**: there is no effort data per stage (OB-04 not yet collected) and no cost model beyond one measured term (Stage 32), so no saving is stated.

## Findings
| ID | Accelerator | Contents (existing source) | Generalisation needed before use | Left out on purpose | Status | Basis |
|---|---|---|---|---|---|---|
| AP-01 | Guarded-boundary kit | `hub/guards/` (No-AI, egress, sandbox, runtime), tripwire tests E26..E28 pattern | Parameterise the allow-list of loopback; document the OD-08 precondition | Any model-call allowance | NOT PACKAGED | RC-01, PT-10 |
| AP-02 | Audit + store kit | `hub/store/`, `hub/admin/` verify-audit, backup/restore with checksum manifest | Fix F-29-01; decide seal and key custody; retention parameter | Hold-all retention default | NOT PACKAGED | RC-02, PT-06 |
| AP-03 | Regression-group runner + sandbox rules | `tests/hub/run_hub_groups.py`, `regression_groups.json`, OD-03a / OD-23 rules, "non-add edits" mechanism | Hosted runner (3.12+); split group C | Laptop-specific paths | NOT PACKAGED | RC-03, PT-11 |
| AP-04 | Source onboarding checklist | `source-contract-v1.json`, intake envelope schema, natural-key rule (OD-18), `partner-feed-operations.md`, per-source contract template (to be written at SB-22) | Per-source contract template; schema_version allow-list; late-delivery catch-up (D-28-04) | The first partner's values | PARTLY EXISTS (contract + schema); checklist NOT WRITTEN | RC-05, PT-07 |
| AP-05 | TEVV kit | Threshold declaration pattern, dataset specs (golden, edge, failure, adversarial), mutation gate, red-team plan, walkthrough record template | Replace dataset contents per use case; add human adversary and real-browser step (RTR-14) | S26 datasets as evidence for other use cases | EXISTS in `docs/26-tevv/`, NOT GENERALISED | RC-19, PT-08, PT-09 |
| AP-06 | Production-readiness scorecard | 38-check list with MET / NOT MET / UNKNOWN | Re-score for each unit; add checks for TLS/2FA/hosting once exposure exists | The current 24-of-38 result for other units | EXISTS, NOT GENERALISED | RC-20 |
| AP-07 | Decision, ownership and gate templates | OD-log structure, RACI / decision-rights / escalation templates (Stage 37), artifact header skeleton | None for structure; every holder cell stays VACANT until a person accepts | Any named role holder; Dinesh as universal owner | EXISTS | RC-18 |
| AP-08 | Value-evidence capture sheet | Slots I-01..I-14 (`roi-model.md`), KPI dictionary with Stage 4 v0.2 addendum (when raised), time-capture design (CA-06) | Stage 4 v0.2 addendum; time capture; finance-approved rate | Any number in the slots | PARTLY EXISTS (slots empty) | `roi-model.md` RM-2 |

**Pack governance:** an accelerator is released to a scale step only after (1) its generalisation work is closed, (2) it is exercised on one unit and passes its own checks, (3) Dinesh records the release (`scale-governance.md` SG-3). Until then the manifest is a plan.

## Evidence References
Per-row. Sources in `docs/26-tevv/`, `docs/27-hardening/`, `docs/36-roi/`, `docs/37-operating-model/`.

## Assumptions
- A-40-04 [Assumption] Packaging inside the same repository (not a separate product) is the default, because no second team or repository exists. Confirm: Engagement lead (Dinesh Naik).

## Unknowns
- U-40-05 Effort to generalise each accelerator (no effort data; OB-04).
- U-40-06 Who will maintain the pack after Stage 38 (RL-02 VACANT; who runs orchestrator duties after Stage 38 is open, OD-34).

## Unresolved Issues
- AP-04's checklist and AP-08's data are not written; they are backlog items, not assets.

## Residual Risks
- Packaging debt: copying first-use-case defaults along with the code (SR-04).

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-25 | claude-fde-agent | First issue |
