---
stage: "FINAL — Authoritative Final As-Built PRD (run as Stage 43)"
artifact: "final-nfr-baseline.md"
version: "v0.1"
date: "2026-10-25"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/17-implementation-prd/finalized-nfrs.md", "docs/26-tevv/", "docs/27-hardening/production-readiness-checklist.md", "docs/28-reliability/", "docs/29-incident-bcdr/rto-rpo.md", "docs/31-observability/slo-sla-definitions.md"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated against any organisation. Documentation only. Authoritative ONLY as "as-built, NOT released": the hub is a shadow build; nothing here records a release, an approval, realised value or a sign-off.**

## Summary
No NFR is proven in production because there is no production. The baseline records what was measured in the sandbox, what is mechanism-only, and where targets conflict (RTO/RPO).

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
### NF-1 Baseline per NFR (as built, evidence class)
The 20 product NFRs and their dispositions are in `requirement-disposition-matrix.md` DM-4. This file records the **baseline numbers** and the proof class for each non-functional dimension. Every target below is an **Assumption** unless marked otherwise; no NFR target was approved by a stakeholder with operating knowledge (none exists, OD-04).

| Dimension | Baseline target | Evidence of the as-built state | Proof class | Status |
|---|---|---|---|---|
| Availability (PNFR-01) | 99.5 % scheduled hours - Assumption | helper `hub/web/nfr.py` over supplied records only; no host, no uptime | class C (mechanism) | [Unknown] in practice |
| Timeliness (PNFR-02) | by 06:00, 100 % of nights - Assumption | scheduler OFF; `site.timezone` UTC/fixed offset only | none | [Unknown] |
| Recovery (PNFR-05) | RTO 8 h / RPO 24 h (Stage 17); RTO 4 h / RPO 1 working day (Stage 29) - both agent targets | restore rehearsed with checksum match on sandbox copies; L2 restore loses post-backup writes; no off-device copy; tabletop had no human participants | class C | [Assumption]; targets unreconciled (AB-3) |
| Performance (PNFR-06) | measure p50/p95, no threshold (OPD-14 open) | measured on small synthetic stores | class C | [Verified Fact] measure-only |
| Access (PNFR-07) | 100 % endpoints authenticated | 48-route deny-by-default registry; Stage 27 rate limit (100 refusals / 60 s - assumption) | tests | [Verified Fact] sandbox |
| Transport (PNFR-08) | TLS for any non-loopback | no TLS; loopback only | design | [Verified Fact] partly met |
| Audit (PNFR-09) | decision events attributed; chain verifies | verify-audit ok; tamper detection tests | tests | [Verified Fact]; framing, not Part 11 |
| Retention (PNFR-10) | 0 deletions | hold-all; insert-only triggers | tests | [Verified Fact] |
| Integrity (PNFR-11) | 0 duplicate effects on replay | 67 REPLAY to NOOP; legacy DB sha unchanged | tests | [Verified Fact] synthetic |
| Untrusted content (PNFR-13) | 0 effects (86 + 22 + 10 fixtures) | TST-NFR-13; Untrusted guard | tests | [Verified Fact]; 44-string fixture not built |
| Observability (PNFR-14) | run records 100 %; KPIs computed | run records yes; 6 metrics unexported; 4 of 21 log events emitted; SLO candidates only | tests | [Verified Fact] partial |
| Determinism (PNFR-17) | identical output across seed/TZ/locale | TST-NFR-17; G10 pass; CT-13 Node drift only | tests | [Verified Fact] on 3.10.12 |
| No AI (PNFR-18) | 0 model calls | tripwires 0 | tests | [Verified Fact]; manual, not CI |
| Change safety (PNFR-19) | rollback rehearsed; replay gate | L1/L2/L3 rehearsed in sandbox; G1 FAIL; no CI | rehearsal | [Verified Fact] partial |
| Labelling (PNFR-20) | 100 % 'synthetic, unvalidated' | metrics yes; R2 pages not verified | inspection | [Verified Fact] / [Unknown] |

### NF-2 Reliability, capacity, SLO [Verified Fact]
Five SLO **candidates** (SLO-01..SLO-05) and an alert catalog exist; **no SLA** (D-31-10: re-derive after 30 days of real use). Capacity plan and failure-injection results are sandbox figures (`docs/28-reliability/`). Resilience defaults (retries 3, breaker 3/60 s, listener cap 64, budget 20 %) are agent assumptions and are not wired (OD-35). Disk-full and power-loss injection need an approved host (D-28-07).

### NF-3 Runtime [Verified Fact]
Code floor Python 3.10 / SQLite 3.37; production target Python 3.12+ (OD-24). **No 3.12+ evidence for the hub's characterisation goldens**; the orchestrator's full hub regression ran on 3.13 (OD-23). Python 3.10 reached end of life on 2026-10-01 per Stage 27 VR-02 (re-check recommended; the date was recalled, RS-10). Test-suite wall time: groups run 80-150 s against a 180 s device-call cap (F-11).

### NF-4 Security NFRs [Verified Fact]
See `final-security-governance-baseline.md`. Not met: TLS, second factor, external pen test, token expiry mandatory (RS-01, RS-02, RS-08, RS-14).

## Evidence References
See `evidence_sources` in the header and the per-row evidence columns.

## Assumptions
- All numeric targets: Assumption; confirm: Engagement lead (Dinesh Naik).

## Unknowns
- U-43-10 Production availability, latency, capacity (no host).
- U-43-11 Which RTO/RPO pair is intended (8 h/24 h vs 4 h/1 working day).

## Unresolved Issues
- See `open-items-and-decision-register.md`.

## Residual Risks
- See `residual-risk-register.md`.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-25 | claude-fde-agent | First issue. |
