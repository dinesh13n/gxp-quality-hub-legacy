---
stage: "25 — Governance + Compliance + Assurance"
artifact: "compliance-obligations.md"
version: "v0.1"
date: "2026-10-21"
author_agent: "claude-fde-agent"
status: "IN REVIEW"
evidence_sources: ["docs/domain-assurance.md", "docs/03-problem-value/{nfrs,scope-exclusions,assumptions-register}.md (NFR-09, EX-05, A-08)", "docs/09-initial-prd/{nfrs,non-goals,product-risks,open-product-decisions}.md (PNFR-09, NG-06, PR-14, OPD-09, OPD-16)", "docs/17-implementation-prd/finalized-nfrs.md", "docs/13-traceability/coverage-gap-register.md GAP-13-22", "docs/12-specs/acceptance-criteria.md ACC-8", "docs/11-data-context/metadata-model.md U-11-17", "docs/05-current-state/integration-landscape.md L69", "docs/07-repo-assessment/security-code-quality-findings.md SC-06", "docs/02-stakeholders/{decision-rights-map,approval-authority-map,stakeholder-map}.md", "docs/00-preflight/operating-contract/*.md", ".fde/orchestrator-decisions.md (OD-04, OD-08, OD-15, OD-22, OD-24)"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated. Nothing here is legal advice and nothing here claims compliance. Every regulatory reference is limited to what earlier stage documents already cite; anything beyond that is marked Unknown or Assumption and flagged for qualified (legal / quality-assurance) review. Owner of every human decision: Engagement lead (Dinesh Naik).**

## Summary
Sixteen obligations (OB-01..OB-16) were identified from what the repository and earlier stages actually cite. The only regulatory references in the repo are: **21 CFR Part 11** (audit trail / attribution framing), **"GMP data integrity principles"** and **ALCOA+** (named once as a lens, "not yet assessed against regulation"), and **DPDP / GDPR** (named once as "not assessed"). All of them are recorded as **framing, not binding** (A-08, DR-29, EX-05, NG-06, GAP-13-22), and `docs/domain-assurance.md` states the environment is "a synthetic training environment, not compliance certification". Binding status has never been answered by a decision-maker (GD-11 / Q-02-06 / DQ-17 open). Result: 7 obligations are internal-binding today (OB-02, OB-06, OB-10, OB-11, OB-12, OB-13, OB-16); 3 are external-regulatory themes with framing-only status (OB-01, OB-03, OB-04); 6 have an Unknown binding status (OB-05, OB-07, OB-08, OB-09, OB-14, OB-15). No AI-governance regulation or framework (e.g. an AI act or management-system standard) is cited anywhere in the repo; none is applied here (OB-15).

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
### OG-1 Obligation register
Binding column: **Internal-binding** = bound by a recorded decision or the operating contract; **Framing** = cited as a lens only (A-08/DR-29); **Unknown** = no source says whether it applies.

| ID | Obligation (as the repo states it) | Source (path / ID) | Type | Binding status | Tag | Applicability to this repo |
|---|---|---|---|---|---|---|
| OB-01 | Every decision and state change attributable (who, when, what evidence) and tamper-evident | `docs/03-problem-value/nfrs.md` NFR-09; `docs/17-implementation-prd/finalized-nfrs.md` PNFR-09 ("framing, not Part 11"); ADR-005; `domain-assurance.md` ("21 CFR Part 11 and GMP data integrity principles" as background; "source attribution for each decision") | Regulatory theme (Part 11 audit trail) | Framing | [Verified Fact] that the repo says so; binding status [Unknown] | Applies as a design target; no compliance claim allowed (GAP-13-22, ACC-8) |
| OB-02 | Batch disposition is a decision requiring authorised human review; existing human approval gates preserved; nothing may make, pre-fill, simulate or automate it | `domain-assurance.md` ("Decision requiring authorized human review: `batch_disposition`"; "preserving existing human approval gates"); HAR-12; STOP-07; NG-02; BR-08 | Organisational + domain | Internal-binding (HAR-12 / STOP-07 stand; OD-04 forbids inventing an approver) | [Verified Fact] | Applies in full; authority holder is a GAP (DR-22, `zone_h.holders` []) |
| OB-03 | Electronic signature must not be claimed or simulated by the product | HAR-12; ADR-006 ("not implemented as a cryptographic or legal signature"); `docs/12-specs/api-contracts.md` ZH-03 ("records that a human acted; not a cryptographic or legal signature") | Regulatory theme (Part 11 e-signature) | Framing | [Verified Fact] on the product position; Part 11 e-signature requirements themselves [Unknown] (never assessed) | Applies as a limit on claims; legal review needed before any use as a signature |
| OB-04 | Data integrity (ALCOA+ lens): no silent drops, no silent skips, no in-place status overwrite, no dropped legitimate replays, no lost evidence | `docs/05-current-state/integration-landscape.md` L69 ("not yet assessed against regulation"); `docs/07-repo-assessment/security-code-quality-findings.md` SC-06; PNFR-11, PNFR-16, PNFR-17 | Regulatory theme (GMP data integrity) | Framing | [Verified Fact] on the defects and the lens; attribute-by-attribute mapping [Unknown] (the repo never lists ALCOA+ attributes; none is invented here) | Applies at theme level only |
| OB-05 | Retention, authorisation and audit-evidence rules belong to the risk and security partner role | `docs/business-context.md` (SH-06); DR-24; OPD-09; PNFR-10; OD-S12-09 | Organisational / regulatory | Unknown (no retention rule, period or owner exists) | [Verified Fact] gap | Interim rule: hold-all, no deletion (OD-15) |
| OB-06 | Authentication and authorisation for every endpoint; 0 anonymous reads / writes | PNFR-07; FR-SEC-01; `docs/12-specs/security-spec.md` SEC-2/SEC-3 | Organisational (security) | Internal-binding as a PRD requirement (PRD baseline approved, OD-22) | [Verified Fact] | Applies; values are proposals until Stage 24 (RTD-26) |
| OB-07 | Compliance team position: no automatic closure without verifiable evidence | `docs/correspondence/operations-vs-risk-2024.md` as cited in `stakeholder-map.md` SH-09; FR-DEC-05 | Stakeholder claim | Unknown (a document says it; no holder confirms; sufficiency criteria OPD-07 open) | [Verified Fact] only that the document says X (NE-1) | Applies as design constraint (structural evidence presence only, A-09-03) |
| OB-08 | Privacy / data-protection regime (India DPDP, GDPR for DE data named as candidates) | `docs/11-data-context/metadata-model.md` U-11-17 ("not assessed"); PNFR-12; NG-09 | Regulatory | Unknown | [Unknown] | All data is synthetic (OD-04, `data_origin` = synthetic); regime applicability is moot until real data exists; flag for qualified review |
| OB-09 | No silent cross-tenant action | `domain-assurance.md` | Domain safety | Unknown how it maps | [Verified Fact] requirement text; [Inference] the hub has no tenant concept (single store, loopback, single site) | Treated as met by absence of multi-tenancy; not tested as such |
| OB-10 | No AI / LLM / ML / agentic capability in the product; introduction needs a new Dinesh decision and HAR-10 | OD-08; HAR-10; NG-01; PNFR-18; RQ-1..RQ-3 (`docs/08-ai-qualification/qualification-decision.md` QD-3) | Organisational (AI governance) | Internal-binding (OD-08 approved by Dinesh 2026-10-18) | [Verified Fact] | Applies in full |
| OB-11 | Change control and approvals: branch + PR + review + OD-log record; approvals only by Dinesh's own message or an "Approved" OD entry; no force-push; prior evidence immutable | CC-01..CC-12; HAR-01..HAR-16; OD-01, OD-13; `evidence-contract.md` EV-07, EO-4 | Organisational | Internal-binding for OD-01 / OD-04 / OD-13; other items PROVISIONAL (see `operating-contract-governance-updates.md`) | [Verified Fact] | Applies |
| OB-12 | No fabrication: no invented stakeholders, approvals, KPIs, telemetry; synthetic figures labelled "synthetic, unvalidated" | OD-04; `evidence-contract.md` NE-4; PNFR-20 | Organisational | Internal-binding (OD-04 Approved) | [Verified Fact] | Applies to every artifact |
| OB-13 | Untrusted content (data, documents, feed text) never acts as an instruction or changes a decision field | PNFR-13; DF-08; STOP-05 | Organisational (security) | Internal-binding (PRD baseline) | [Verified Fact] internal; external basis [Unknown] | Applies; owner of control values is Stage 24 |
| OB-14 | Contractual obligations (SOW, SLA, data-processing terms) | `docs/02-stakeholders/operating-contract-confirmations.md` A-0B-01 (no SOW exists) | Contractual | Unknown | [Unknown] | None evidenced |
| OB-15 | External AI-governance obligations (AI-specific laws, management-system standards, risk frameworks) | none cited anywhere in the repo | Regulatory / AI governance | Unknown | [Unknown] | Not applied; the product has no AI (OB-10); if RQ-1..3 ever fire, re-assess with qualified review |
| OB-16 | Behaviour-changing code needs a characterisation baseline and Dinesh's approval of the deviation (preserve-or-fix); no deviation is approved yet | HAR-06; CC-05; TG-4; DV-01..DV-11 (`docs/16-repo-validation/behavior-difference-report.md`); OD-S12-13 | Organisational (change safety) | Internal-binding; OD-S12-13 accepted open | [Verified Fact] | Applies; blocks CUT steps |

### OG-2 Findings on applicability
| ID | Finding | Evidence | Impact | Risk | Confidence | Unresolved question |
|---|---|---|---|---|---|---|
| OF-01 | [Verified Fact] Every regulatory reference is framing only; no decision-maker has ever stated whether Part 11 / GMP data integrity binds any resulting system | A-08, DR-29, EX-05, NG-06, GD-11, Q-02-06, DQ-17 | The system can be built and labelled "tamper-evident (framing)" but never "compliant" | Medium (claim creep) | High | Framing or binding? (Dinesh; qualified review if binding) |
| OF-02 | [Inference] The two strongest obligations are internal, not regulatory: the human-disposition rule (OB-02) and the No-AI rule (OB-10). Both are enforced in code and recorded in approved decisions | OD-08; ADR-006; `hub/security/zone_h.py`; `hub/guards/no_ai.py` | Governance effort should go to keeping these two enforced | Medium | High | none |
| OF-03 | [Unknown] Which external regulation (if any) a real deployment would fall under, and its clauses | no source | Control mapping cannot cite clauses; this stage cites none | Medium | High | Legal / quality review if the product ever leaves the synthetic setting (OPD-16) |
| OF-04 | [Verified Fact] No client-side owner exists for any obligation (SH-03..SH-15 unfilled) | `stakeholder-map.md`; OD-04 | Obligations have a decision owner (Dinesh) but no subject-matter owner | High for any real use | High | Who would own OB-05 / OB-07 / OB-08? |
| OF-05 | [Verified Fact] The legacy estate does not meet the audit / human-gate themes (CG-01, CG-02 control gaps; SC-06) — the hub addresses them in shadow only | `docs/05-current-state/control-points.md`; `docs/07-repo-assessment/security-code-quality-findings.md` | Value of governance depends on cutover that cannot start (RB-4) | High (value) | High | CUT decisions |

## Evidence References
See `evidence_sources`. Obligation-to-control mapping: `compliance-control-matrix.md`. Owners: `accountability-map.md`. Evidence locations: `audit-evidence-index.md`.

## Assumptions
- A-25-OB-1 [Assumption] Part 11 / GMP data integrity / ALCOA+ remain framing only, as in A-08 / DR-29 (this is the default in DQ-17 / GD-11). Confirm: Engagement lead (Dinesh Naik), Stage 25 decision.
- A-25-OB-2 [Assumption] The hub is single-site and single-tenant, so OB-09 is met by construction. Confirm: Engagement lead (Dinesh Naik).
- A-25-OB-3 [Assumption] Approval of the Initial PRD (OD-22) makes the PRD NFRs internal-binding requirements (OB-06, OB-13); it does not make any regulation binding.

## Unknowns
- U-25-OB-1 Whether Part 11 / GxP binds any real deployment (OPD-16, GD-11).
- U-25-OB-2 Applicable privacy regime (U-11-17).
- U-25-OB-3 Any contractual terms (A-0B-01).
- U-25-OB-4 Any AI-governance law or standard the organisation follows (none cited).
- U-25-OB-5 Retention requirement and period (DR-24, OPD-09).

## Unresolved Issues
- GD-11 / DQ-17 framing decision; OPD-09 retention; OPD-16 real-vs-synthetic. All are 'accepted open' unless Dinesh answers.

## Residual Risks
- RR-OB-1 Misreading framing as certification (PR-14) — Medium; mitigated by labels and `system-card.md` limits.
- RR-OB-2 A real regulatory clause not cited in the repo could apply later; this register would then be incomplete — Medium; owner Engagement lead (Dinesh Naik) with qualified review.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-21 | claude-fde-agent | First issue. |
