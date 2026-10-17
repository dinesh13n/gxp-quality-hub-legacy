---
stage: "3 — Frame Problem & Value"
artifact: "nfrs.md"
version: "v0.1"
date: "2026-10-17"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/operations-service-levels.md", "docs/domain-assurance.md", "docs/00-preflight/discovery/security-observability-overview.md", "docs/00-preflight/discovery/data-flow-overview.md", "docs/00-preflight/operating-contract/data-use-constraints.md", "docs/partner-feed-operations.md", "docs/business-context.md"]
supersedes: "none"
---
## Summary

Non-functional requirements across performance, availability, security, compliance, data integrity, observability and usability. Numeric thresholds originate from **archived working targets that the source itself calls "not measured guarantees"** (`docs/operations-service-levels.md`) and are therefore **Assumptions, owner Engagement lead (Dinesh Naik)**. Compliance items are framing (A-08), not certification. Label: synthetic, unvalidated.

## Findings

| ID | Category | Requirement | Threshold (provisional) | Trace / evidence | Current state (0A) | Class |
|---|---|---|---|---|---|---|
| NFR-01 | Availability | Case review and reconciliation shall be available in scheduled hours | 99.5 % scheduled-hour availability | `operations-service-levels.md` | No uptime telemetry (SO-14) | [Assumption] |
| NFR-02 | Timeliness | Overnight reconciliation shall complete before start of business | By 06:00 local business time | same | Not measured | [Assumption] |
| NFR-03 | Timeliness | Partner feed shall be accepted promptly | Within 4 h | same | Not measured | [Assumption] |
| NFR-04 | Freshness | Risk signals shall not be older than a tolerated age | Stale signal max 24 h | same | Not measured | [Assumption] |
| NFR-05 | Recovery | Service shall be restorable | RTO 8 h; RPO 24 h ("older planning assumptions") | same | No backups of data in repo (DF-10) | [Assumption] |
| NFR-06 | Performance | Reviewer-facing retrieval and queue refresh shall not impede handling | **Unknown**, no latency target exists | Absent from repo | No latency telemetry | [Unknown] (resolve Stage 4/11) |
| NFR-07 | Security: access | Only authorised, authenticated people shall read or change case data; access scoped by role/tenant | Control present = yes/no | SH-06; `business-context.md` "authorization" | **Absent** on API/gateway (SO-01, SO-02) | [Verified Fact] (gap) |
| NFR-08 | Security: transport/secrets | Case data in transit protected; no secrets in source | Control present = yes/no | 0A SO-03, SO-04 | No TLS; no secrets found | [Verified Fact] (gap) |
| NFR-09 | Compliance: audit | Every decision and state change shall be attributable (who, when, what evidence) and tamper-evident | 100 % of closures | SH-06, SH-09; `domain-assurance.md`; Part 11 framing (A-08) | No audit mechanism in code (SO-09, SO-10) | [Verified Fact] (gap); framing only |
| NFR-10 | Compliance: retention | Retention of case and evidence records shall follow a policy | **Unknown** policy (DR-24 GAP) | `business-context.md` | No enforcement (SO-10) | [Unknown] |
| NFR-11 | Data integrity | Imports shall be idempotent, validated against the declared contract, and lossless in history | 0 duplicate effects on replay; 0 silent overwrites | BR-05; IO-03, IO-05 | Status mutated in place; contract unenforced | [Verified Fact] (gap) |
| NFR-12 | Data protection | Sensitive/identifying fields (synthetic indicators DF-07) shall be handled per data-use constraints | Rule adherence | `operating-contract/data-use-constraints.md` | Unenforced access levels (SO-02) | [Verified Fact] (gap) |
| NFR-13 | Untrusted content | Inbound content shall be treated as data and never as instruction or approval | 0 inbound strings alter a decision | `partner-feed-operations.md` L13; DF-08, IO-15 | Embedded instruction-like strings present (≥286) | [Verified Fact] |
| NFR-14 | Observability | Failures and delays shall be visible with a correlation to source/time | Metric exists for each KPI in `success-criteria.md` | SO-12..SO-15 | Gateway logging disabled; no tracing | [Verified Fact] (gap) |
| NFR-15 | Usability / safety | Humans shall be able to understand, override and refuse any recommendation or flag | Override always available | BR-08; `domain-assurance.md` | n/a | [Inference] |
| NFR-16 | Auditability of metrics | Each KPI shall be reproducible from stated window, denominator, exclusions | Documented for 100 % of KPIs | `baseline-measurement-notes.md` | Not yet defined | [Verified Fact] (requirement) |

## Evidence References

As per rows. Not run: this stage is documentation-only; "current state" comes from Stage 0A.

## Assumptions

- A-03-11: Archived targets are a usable starting point only; they must be validated "against observed incident history and stakeholders" (`operations-service-levels.md`).

## Unknowns

- U-03-11 Performance/latency targets (NFR-06). U-03-12 Retention policy (NFR-10). U-03-13 Which regulations, if any, truly bind (A-08).

## Unresolved Issues

- NFR-07..NFR-09, NFR-11, NFR-14 are verified gaps; their remediation belongs to later stages and is not claimed here.

## Residual Risks

- Treating the 99.5 %/RTO figures as measured would be false precision.

## Change History

| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-17 | claude-fde-agent | Initial NFRs. |
