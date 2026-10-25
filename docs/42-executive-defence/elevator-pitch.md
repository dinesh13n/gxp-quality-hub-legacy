---
stage: "42 — Executive Defence & Final Value Story"
artifact: "elevator-pitch.md"
version: "v0.1"
date: "2026-10-25"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/42-executive-defence/executive-evidence-index.md"]
supersedes: "none"
---
## Summary

**Label: synthetic repository, unvalidated against any organisation.** Three versions of the pitch (10 seconds, 30 seconds, 90 seconds) plus words never to use. Every sentence maps to claim IDs in `executive-evidence-index.md`. No savings, customers, endorsements or adoption are claimed.

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->

### EP-1 Ten seconds
"We diagnosed why a GxP quality estate cannot agree on its own case numbers, chose not to use AI because the evidence did not call for it, and built a safe, switched-off, deterministic replacement beside the old system. It is not released, and the value is not yet proven." (C-02, C-05, C-12, C-19, C-25)

### EP-2 Thirty seconds
"The legacy system has eight structural gaps: no recorded decision step, mutable history, three different approval rules, unowned definitions of 'closed', and more. We qualified AI against those gaps and it lost on fit and risk, so the product is No-AI, and a human approved that. We built a standard-library-only hub that runs beside the legacy code, reproduces its behaviour where it should, and keeps every consequential switch off. It passed a heavy sandbox test and attack programme, with defects found and fixed along the way. The release gate is blocked at zero of forty approvals, there are no users, and ROI is not computable. The honest ask is a handful of human decisions and a defined pilot window." (C-02, C-05..C-12, C-14, C-15, C-19, C-21, C-25, NS-1)

### EP-3 Ninety seconds (spoken)
1. **Problem.** In a synthetic GxP quality estate the same case can be counted, closed and costed differently by operations, finance and compliance. Eight causes are confirmed in the code. We do not know what it costs in real life: no real data or stakeholders exist. (C-01, C-02)
2. **Decision.** We tested AI honestly. The causes are missing owners, keys and records, not unstructured language. AI scored lowest, adds an injection risk, and the decision does not change at zero token price. Dinesh approved No-AI; there are explicit triggers to revisit. (C-05, C-06)
3. **Build.** A modular, additive, stdlib-only hub with an audit chain and a human approval gate. Everything that matters ships off. Legacy behaviour is unchanged where we checked it: 134 of 134 characterisation checks. (C-07..C-12)
4. **Proof and its limits.** The test and red-team programme found 11 findings, one High; most are fixed. Human walkthroughs are unsigned and there is no Python 3.12 evidence. (C-14, C-15)
5. **Status.** Release is blocked: zero of forty approvals, and monitoring and High-finding decisions are missing. Nothing has been cut over. (C-19)
6. **Value.** There is no after-window, so no measured improvement. ROI, NPV and payback are not computable and we will not invent them. (C-21, C-25)
7. **Ask.** Fourteen decisions, mostly one person's, then a 90-day gated plan that reaches a limited-entry decision at best. (NS-1, C-29)

### EP-4 Do not say
| Phrase | Why not |
|---|---|
| "production-ready", "go-live", "deployed" | C-19, C-15 |
| "saves X hours / X %" | C-21, C-26 |
| "GxP compliant", "Part 11 compliant", "audit-ready" | C-28 |
| "customers/users love", "validated by the business" | C-01, C-21 |
| "AI-powered" | C-05 (No-AI) |
| "proven", "verified benefits" | C-25 |
| "secure" without "loopback, synthetic, shadow only" | C-13 |

## Evidence References
Claim IDs inline; `executive-evidence-index.md`.

## Assumptions
The audience understands "No-AI" as a deliberate result of qualification.

## Unknowns
Audience; time slot.

## Unresolved Issues
Depends on release and value outcomes; re-write after Stage 30 v0.2 and Stage 34/35/36 v0.2.

## Residual Risks
A short pitch drops caveats. EP-4 is the guard.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-25 | claude-fde-agent | Initial. |
