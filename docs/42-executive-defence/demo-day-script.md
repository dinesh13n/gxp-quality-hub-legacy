---
stage: "42 — Executive Defence & Final Value Story"
artifact: "demo-day-script.md"
version: "v0.1"
date: "2026-10-25"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/30-release/evidence/", "docs/34-measure-after/evidence/", "docs/26-tevv/evidence/", "docs/16-repo-validation/", "docs/42-executive-defence/executive-evidence-index.md"]
supersedes: "none"
---
## Summary

**Label: synthetic repository, unvalidated against any organisation.** A 15 to 20 minute demo that shows what exists, what is refused, and what is missing. **It is built from recorded evidence logs first.** A live run is optional and only ever on a full sandbox copy of the repository outside the working tree (OD-03a), with the backup checksum verified before and after (`sha256sum -c ../_data-backup-2026-10-17/SHA256SUMS.txt`). **Never run anything against the working-tree `data/` (OD-03).** No step shows a production system because none exists. The demo ends on the blocked gate, deliberately.

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->

### DS-1 Run sheet
| Min | Beat | Show (evidence file) | Say | Claims |
|---|---|---|---|---|
| 0-1 | Frame | This document's label; `executive-narrative.md` EN-2 | "Everything is synthetic. Nothing is released. I will show you what works, what is refused, and what is unknown." | C-01, C-19 |
| 1-3 | Problem | `docs/06-root-cause/confirmed-root-causes.md` RC-8 row; `baseline-kpi-sheet.md` K-10, K-06 | "The same month-end total is 742,956.61 in one report and 622,826.44 in another because a join fans out. Also, 98 % of the synthetic feed rows point at cases that do not exist; that is test residue, so we treat the baseline as method validation only." | C-02, C-03 |
| 3-5 | Decision | `docs/08-ai-qualification/qualification-decision.md` QD-1 and QD-3 | "We qualified AI out. Here are the triggers that would bring it back." | C-05, C-06 |
| 5-8 | The hub refuses | Evidence logs: `docs/30-release/evidence/s30-log-12-set-authoritative-without-approval.txt` | "Trying to make a capability authoritative without an approval reference is refused (E-CFG-INVALID)." | C-12 |
| 8-9 | Audit | `s30-log-04-verify-audit.txt` and its `limitation` field | "Chain verifies. Read the limitation out loud: records deleted after the last anchor are not detectable." | C-07, RP-03 |
| 9-11 | Behaviour parity | `docs/16-repo-validation/regression-results.md`; `s30-log-06-golden-compare.txt` | "134 of 134 characterisation checks on legacy. The golden comparison is red on purpose because 11 differences are unapproved." | C-09 |
| 11-13 | Attack results | `docs/26-tevv/tevv-release-gate.md` GT-1 table; `red-team-findings.md` F-02 | "No Critical. One High: a reviewer could read a restricted note. We fixed it under an assumption Dinesh has not yet confirmed." | C-14, C-34 |
| 13-14 | Metrics with definitions | `docs/34-measure-after/after-intervention-kpi-sheet.md` K-03 and K-09-OPS rows | "4 of 4 figures carry their definition. Backlog count 89 of 125 matches legacy. That is parity, not improvement." | C-22 |
| 14-16 | Release gate | `docs/30-release/go-no-go-criteria.md` GN-1 and `release-approvals.md` | "NO-GO. 16 technical criteria pass; G1, T-09, T-10 fail; T-05 not run. Approvals: 0 of 40." | C-19 |
| 16-17 | Value | `docs/36-roi/roi-model.md` Summary; `verified-benefits.md` | "ROI not computable. Zero verified benefits. I will not give you a number." | C-25 |
| 17-20 | Ask | `next-step-recommendations.md` NS-1 | "Fourteen decisions; the first five unblock the story." | NS-1 |

### DS-2 Optional live segment (sandbox only)
Prerequisites: a full copy of the repo under `~/fde_sbx/<name>`, `HUB_WORKTREE_ROOT` and `HUB_SANDBOX_ROOT` set as in `docs/34-measure-after/evidence/run_hub_metrics.sh`, `PYTHONHASHSEED=0`, Python 3.10.12 on the reference laptop. Candidate live commands (the exact arguments are those used in the cited evidence scripts; do not improvise):
1. `python -m hub.release evaluate` over the shipped `gate-results.json` and `approvals-register.json` (expected: NO-GO; see `s30-rehearse.sh`).
2. The set-authoritative refusal (expected exit 2, E-CFG-INVALID) per `s30-log-12`.
3. The audit verification command used in `s30-log-04-verify-audit.txt` (and `hub.decision verify-chain`, see `run_hub_metrics.sh` step 01h) on a freshly migrated sandbox store.
Expected outputs are the recorded logs. **If a live output differs from the log, say so and show the log.** After the demo remove the sandbox copy (OD-16 housekeeping; the device disk is about 9.8 GB) and verify the backup checksum.

### DS-3 What the demo must not do
| Do not | Reason |
|---|---|
| Start a web server on any non-loopback address, or show the legacy compose file running | VR-03, VR-04, RP-11 |
| Run `app/generate.py` or any batch job in the working tree | OD-03 (writes repo-relative `data/`) |
| Flip any authority switch with a "sandbox" reference in front of an audience and call it a cutover | It is a rehearsal (T-04) |
| Show a dashboard mock-up as if it were live | None exists; the dashboard specs are documents |
| Say "approved" for any item whose register row is OPEN | OD-32 |

### DS-4 Fallback if the live segment fails
Use the evidence logs. They are in the repository and hash-listed (`docs/30-release/evidence/SHA256SUMS.txt`).

### DS-5 Q&A bank
Use `executive-narrative.md` EN-4 (20 questions), `architecture-defence.md` AD-5, `ai-decision-defence.md` AI-5, `economic-value-summary.md` EV-7.

## Evidence References
Logs and documents named in DS-1; claim IDs C-01..C-34.

## Assumptions
A-42-07 [Assumption] The laptop environment and the sandbox scripts still run at main b1de232 (not re-run in Stage 42).

## Unknowns
Whether the live segment passes today; audience; time.

## Unresolved Issues
T-05 (full regression at final HEAD) is the orchestrator's; a live demo does not substitute for it.

## Residual Risks
A live demo producing a surprise; mitigated by DS-4.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-25 | claude-fde-agent | Initial. |
