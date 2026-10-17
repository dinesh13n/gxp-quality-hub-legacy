---
stage: "4 — Capture Before-AI / Before-Intervention KPIs"
artifact: "proxy-metrics.md"
version: "v0.1"
date: "2026-10-17"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/04-baseline-kpis/evidence/measure_baseline.output.json", "docs/04-baseline-kpis/evidence/probe_enterprise_estate.output.json", "docs/04-baseline-kpis/baseline-data-quality.md"]
supersedes: "none"
---
## Summary

Proxies defined where direct measures are impossible (DQ-01). A proxy is NOT the KPI: it must never be reported under the KPI's name, never be used to claim improvement on the KPI, and must carry its limits. Four proxies defined; none has been validated against a real measure (no real data exists).

## Findings

| ID | Proxy | For KPI | Definition and value (synthetic) | Why it might track the KPI | Limits | Validity | Confidence |
|---|---|---|---|---|---|---|---|
| P-01 | Created → first operations review | K-04-OPS, K-05 | Hours from `cases.created_at` to `events.recorded_at` of STATUS_REVIEWED (reviewer="operations"). All: median 12.06 h, p90 25.62 h, n=20 (max 27.53 h). Cases now CLOSED only: median 9.51 h, p90 22.84 h, n=6 | First human touch is an early stage of the path to closure | Not a closing time: 20 of 125 cases (16 %) have it, the review happens for OPEN/REOPENED/UNDER_REVIEW cases too; all values < 28 h suggests generator design; says nothing about evidence | [Inference] Weak. Valid only as "time to first review" | Low |
| P-02 | Created → first external-feed message | K-05 | Hours from `created_at` to `source_messages.received_at`: median 2.90 h, p90 4.14 h, n=15 (8 of 15 messages report CLOSED) | External information arrival is part of evidence gathering | Message presence ≠ evidence completeness; n=15; a message with status CLOSED is the source's claim, not an approver record | [Inference] Weak | Low |
| P-03 | Evidence arrival lag (secondary estate) | K-05 | `evidence_events.arrival_time − event_time`: median 36.0 h, p90 63.0 h, n=12,500, none negative (`data/enterprise_legacy.sqlite3`) | Lag between evidence being produced and reaching the system is a component of time-to-evidence | Different population from OD-02; one evidence event per object; not receipt→complete; 416 of 2,079 CLOSED objects carry strength-0 evidence | [Inference] Weak; use only if Dinesh adopts the enterprise estate as a baseline tier | Low |
| P-04 | Open-case age at snapshot | K-04-OPS | Age of non-CLOSED cases at AS_OF (K-09-OPS: median 565.1 d, p90 974.2 d) | Right-censored lower bound of time-to-close for cases still open | Biased: ignores closed cases; cannot be compared with closed-case durations | [Inference] Lower bound only | Medium |
| (D-EVID bound) | Evidence-complete upper bound | K-09-EVID | 125 of 125 not demonstrably evidence-complete | Absence of fields | It is a structural bound, not a measure | [Verified Fact] as bound | High |

### Rules for use (frozen with the dictionary)

1. Report proxies in a separate column labelled "PROXY", with the limits above.
2. FAIL-02 applies: a proxy improving while the real KPI is unmeasured is not an improvement claim.
3. Replace each proxy with a direct measure as soon as event capture exists (earliest: Stage 34 post-intervention instrumentation, or a real stakeholder trail).

## Evidence References

`evidence/measure_baseline.output.json` keys `P-01_*`, `P-02_*`, `K-09_*`; `evidence/probe_enterprise_estate.output.json` `evidence_arrival_delay_hours`.

## Assumptions

A-04-05: STATUS_REVIEWED with reviewer "operations" is an operations-side review (taken from the payload label; no process documentation confirms it) — confirm Stage 5.

## Unknowns

U-04-11 correlation between any proxy and true time-to-close (unmeasurable now).

## Unresolved Issues

- No proxy exists for K-01, K-07, K-22.

## Residual Risks

- Proxies are easily mistaken for baselines in executive materials (Stage 42).

## Change History

| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-17 | claude-fde-agent | Initial proxies. |
