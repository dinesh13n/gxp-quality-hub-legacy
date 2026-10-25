---
stage: "36 - ROI / NPV / Benefits Realisation"
artifact: "benefits-signoff.md"
version: "v0.1"
date: "2026-10-25"
author_agent: "claude-fde-agent (Stage 36 run)"
status: "DRAFT"
evidence_sources: ["docs/36-roi/verified-benefits.md", "docs/36-roi/double-counting-check.md", "docs/36-roi/roi-model.md", ".fde/orchestrator-decisions.md (OD-04, OD-30, OD-32..OD-35)", "docs/37-operating-model/raci.md"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated against any organisation. Documentation only (Stage 36 adds files under `docs/36-roi/` and changes nothing else). Result in one line: ROI, NPV and payback are NOT COMPUTABLE from the evidence in this repository. There is no production after-data (the hub is not in production), the three like-for-like KPI pairs are sandbox parity and not improvement (Stage 35), Stage 3 never quantified an intended benefit, the Stage 0C economics are unvalidated Assumptions with four unpriced cost terms, and Stage 32 found model spend USD 0 and every other cost Unknown. No benefit, saving, ROI, NPV, discount rate, rate card or stakeholder is invented here; no risk is accepted on behalf of Dinesh Naik (OD-04, OD-32, HAR-11). Any placeholder in this file is an empty input slot, not a number.**

## Summary
**Sign-off state: UNSIGNED.** No human has reviewed or approved any benefit, because there is none to approve and no reviewer other than Dinesh Naik exists. This file records the sign-off lines with their true state, the go/no-go framing (**insufficient evidence**), and the gate ruling for Stage 36.

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
### BS-1 Go / no-go framing
| Question | Answer from evidence |
|---|---|
| Is value proven? | **No.** Verified benefits: 0 (`verified-benefits.md`). |
| Is the investment case computable? | **No.** ROI, NPV and payback are NOT COMPUTABLE (empty slots, no discount rate, no finance-approved rate, four unpriced cost terms). |
| Is there evidence of harm or of failure? | **No.** Absence of data is not a negative result (Stage 35: 'no variance measured on any production basis'). |
| Decision supportable by this stage | **INSUFFICIENT EVIDENCE.** Neither 'go' nor 'no-go' on economic grounds can be justified. |
| What this stage does not say | It does not recommend proceeding, expanding, funding or stopping. It does not imply value will appear. Whether to continue spending is Dinesh's decision on grounds this stage cannot supply. |
| What would change the answer | Phases R0 to R5 in `benefits-realisation-dashboard-spec.md` BD-3, then Stage 36 v0.2. |

### BS-2 Sign-off table
| Line | Required by | Signer | State |
|---|---|---|---|
| Verified-benefit list (empty) is accepted as the benefit baseline | Gate | Engagement lead (Dinesh Naik) | UNSIGNED |
| Double-counting rules DCK-1..14 accepted | Gate | Dinesh | UNSIGNED |
| Cost model structure and 0C ranges accepted as planning frame (not budget) | Gate | Dinesh; Finance partner (unfilled) | UNSIGNED |
| Finance-approved labour rate | Prompt guardrail | Finance partner (unfilled) | NONE EXISTS |
| Discount rate | NPV | Finance partner (unfilled) | NONE EXISTS |
| Benefits owner named | Realisation | Dinesh (role VACANT) | NOT NAMED |
| Any risk acceptance | n/a | Dinesh only | NONE MADE; RS-01..16, RP-01..12, VA-01..07, RTR-01..15, F-11 remain open |

The agent has not signed anything on any person's behalf and has recorded no approval.

### BS-3 Gate ruling (applying the prompt's own rule)
| Gate condition | Met? | Basis |
|---|---|---|
| Only verified benefits are valued | **Met** (vacuously) | 0 benefits valued; none unverified is counted |
| Double-counting check complete | **Met** (structural) | `double-counting-check.md`; to be re-run when values exist |
| Benefits sign-off recorded | **Partly**: the sign-off record exists (this file) and states UNSIGNED | No human signature; see ruling note |
| All required artifacts exist | **Met** | 11 of 11 under `docs/36-roi/` (path differs from prompt: A-36-01) |
| Critical gaps resolved or explicitly documented | **Met** (documented) | Unknowns U-36-01..12, preconditions PC-1..10 |
| Evidence supports the stage conclusion | **Met** | The conclusion is 'not computable / insufficient evidence', which the evidence supports |

**Ruling: CONDITIONAL PASS** for the stage's documentation deliverables. Reasoning: the prompt defines BLOCKED as a blocking condition remaining; the stage's conclusion (not computable) is itself supported and nothing unverified was valued, so no gap prevents the honest output. **It is not a pass of the business case: the economic case is unproven and the benefit status is 'insufficient evidence'.** Caveat for Dinesh: if 'benefits sign-off recorded' is read as requiring a human signature, the gate is BLOCKED until Dinesh signs line 1 to 3 of BS-2; that reading is his to make and the ruling should be changed if he makes it. Whether Stage 37 (already merged) is affected: no, Stage 37 does not consume a Stage 36 number.

### BS-4 Findings
| ID | Finding | Evidence | Impact | Risk | Confidence | Unresolved question |
|---|---|---|---|---|---|---|
| BSF-1 | [Verified Fact] No signature exists on any benefit line | BS-2 | Gate condition 3 is satisfied only in the 'record exists' sense | Medium | High | Dinesh's reading |
| BSF-2 | [Verified Fact] No benefits owner, finance partner or cost owner exists | OD-34; `raci.md` | Nobody to sign or to own realisation | High | High | Naming |
| BSF-3 | [Inference] Stages 42 and FINAL must carry 'economic value: unproven' from this file, not a number. Reasoning: those stages consume Stage 36 output, which contains none | Stage 36 prompt Lifecycle Linkage | Prevents a value story built on nothing | High | High | none |


## Evidence References
`docs/36-roi/*.md`; `docs/35-variance/*`; `docs/37-operating-model/raci.md`; OD-04, OD-30, OD-32..OD-35.

## Assumptions
- A-36-14 [Assumption] CONDITIONAL PASS applies the prompt's gate wording as written; the alternative reading (human signature required) would make the gate BLOCKED. Confirm: Engagement lead (Dinesh Naik).
- A-36-01 [Assumption] Artifact directory is `docs/36-roi/` as instructed by the orchestrator, not `docs/36-benefits/` as written in the stage prompt. Confirm: Engagement lead (Dinesh Naik).
- A-36-02 [Assumption] Default-answer authority (OD-32) covers the scope choices here (skeleton instead of numbers; scenarios built only on cost-side Stage 0C ranges). It does not accept any risk, name any owner or approve anything. Confirm: Engagement lead (Dinesh Naik).

## Unknowns
- U-36-13 Whether Dinesh wants a human signature as the gate condition.

## Unresolved Issues
- All BS-2 lines UNSIGNED; all risk registers open.

## Residual Risks
- RR-36-18 'CONDITIONAL PASS' read as 'value confirmed' (High). RR-36-19 Stage 42 narrative inherits optimism not present here (High).

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-25 | claude-fde-agent | First issue (Stage 36). |
