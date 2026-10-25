---
stage: "42 — Executive Defence & Final Value Story"
artifact: "architecture-defence.md"
version: "v0.1"
date: "2026-10-25"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/10-architecture/architecture-decision-summary.md", "docs/16-repo-validation/architecture-conformance-report.md", "docs/16-repo-validation/remaining-debt-register.md", "docs/27-hardening/hardening-plan.md", "docs/28-reliability/resilience-readiness.md"]
supersedes: "none"
---
## Summary

**Label: synthetic repository, unvalidated against any organisation.** The architecture is a **modular monolith, `hub/`, built beside the untouched legacy estate**, stdlib-only, single-host, loopback-only, with append-only SQLite stores, a hash-chained audit trail, a human disposition gate (Zone H), and every consequential capability shipped off. It is defensible as a **safe brownfield transformation** (additive, reversible, behaviour-comparable). It is **not** defensible as a production architecture: no TLS, no wired resilience, no monitoring delivery, no owners, no off-device backup (C-07, C-08, C-13, C-16, C-17, C-18).

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->

### AD-1 The decision and why (brownfield)
| Decision | Rationale | Evidence | Class |
|---|---|---|---|
| ADR-001 modular monolith beside legacy, not rewrite or in-place refactor | Root causes RC-1..RC-8 are absences; the legacy estate has no safety net (shipped suite kills 1 of 15 mutants, the Stage 15 harness kills 15 of 15); additive change keeps rollback trivial | `docs/10-architecture/adrs/ADR-001-architecture-style.md`; `docs/16-repo-validation/regression-results.md` | [Verified Fact] (mutation numbers) / [Inference] (rationale) |
| ADR-003 read-only adapters, shadow comparison, no dual-write | Keeps legacy authoritative until a human approves; golden comparison makes differences explicit (DV-01..DV-11) | ADR-003; `docs/30-release/go-no-go-criteria.md` G1 | [Verified Fact] |
| ADR-002 structural No-AI enforcement | Turns OD-08 into tripwires (deny-list, egress guard, `model_calls_total = 0`) rather than a promise | ADR-002; Stage 26 D01, E26 | [Verified Fact] |
| ADR-004/005 append-only events, hash-chained audit | Answers RC-1/RC-2 (no record, mutable state) | ADR-004, ADR-005; Stage 30 logs 04/10/16/19 verify-audit ok | [Verified Fact] (sandbox) |
| ADR-006 human gate with two recording modes | Disposition must stay human (BR-08, HAR-12); recording location is undecided (OPD-05) so the gate defaults to blocked | ADR-006; OD-22 | [Verified Fact] |
| ADR-007 versioned policies, one rule service, no adopted defaults | Three divergent rules (RC-4); choosing one is a policy decision, not engineering | ADR-007; OD-16 | [Verified Fact] |
| ADR-015 single host, loopback, file-based store | Smallest blast radius while data is synthetic | ADR-015 | [Verified Fact] |
| ADR-017 buy vs build | **Not evaluated** (OPD-10 unanswered) | ADR-017 | [Verified Fact] (gap) |

### AD-2 Status of the ADRs
[Verified Fact] At Stage 10 all 18 ADRs are PROPOSED; only ADR-002's underlying decision (OD-08) is approved. OD-25 accepted the *implementation baseline* (PCH-47) which embodies the build, but I found **no per-ADR ACCEPTED record** [Unknown, U-42-01]. ADR-018 states Python 3.12 while the code floor is 3.10; OD-24 resolved this as "production targets 3.12+, code keeps the 3.10 floor", and no 3.12+ run exists on the laptop (RT-14).

### AD-3 What the architecture proves and what it does not
| Property | Evidence | Verdict |
|---|---|---|
| Additive to legacy; legacy behaviour unchanged | 134/134 characterisation; D5 = 0; checksum gate rc 0 around every run | Proven in sandbox |
| No third-party dependency | dependency scan (Stage 16) | Proven at Stage 16 |
| No model call, no egress | tripwires zero in S26/E26/S30 groups | Proven in sandbox |
| Tamper-evident audit | verify-audit ok incl. after restore; every tamper detected in S26 | Proven in sandbox; **the anchor is an unsigned local file, and tail records after the last anchor can be removed undetected** (RP-03) |
| Replay safety | 8,567 re-delivered rows all NOOP_DUPLICATE, queues unchanged | Proven in a sandbox run; raw store grows by the re-delivered rows (8,583 to 17,150) |
| Concurrency, availability, capacity | No capacity target; SQLite contention hypothesis H-14 SUPPORTED by config only | **Unknown** |
| Fault tolerance in service | Mechanisms built, **not wired** into `gateway-pull` or `hub web serve` (C-16) | Not delivered |
| Exposure beyond loopback | No TLS, single-factor passwords, token expiry is a recommendation | **Not supported** |

### AD-4 Trade-offs accepted (and who accepted them)
1. **Shadow-first means no value yet.** Keeping everything off protects the legacy estate and delays any benefit; value cannot exist before a cutover decision (C-19). Decision-maker: Dinesh.
2. **Single store, single host, SQLite.** Simple and rebuildable; limits concurrency and recovery (RTO 4 h and RPO 1 working day are agent targets, C-17).
3. **Stdlib-only.** Zero supply-chain exposure; every capability (HTTP, rate limiting, search) is hand-built and so hand-maintained. Nine over-complex functions remain (Stage 27).
4. **Many migration runners and copies of the holder check.** Recorded debt (C-08); cheap to create, costly to maintain without owners.
5. **Controls designed around one human.** Safe by default, but a single approver is a bottleneck and a separation-of-duties gap (RP-01).

### AD-5 Hard questions on architecture
| Question | Defensible answer |
|---|---|
| Why not just fix the legacy code? | The legacy code has no behavioural safety net and unowned rules; the hub lets us compare behaviour (golden comparison) before anything changes. In-place fixing was not evaluated as a measured alternative; the choice is a documented option comparison (`docs/10-architecture/architecture-options.md`), not an experiment. |
| Why SQLite and a monolith for a GxP system? | Because the data is synthetic and the exposure is nil; it is deliberately the smallest thing that can be rebuilt and rolled back. It is not a production data architecture and we do not claim it is. |
| Is the audit trail enough for GxP? | No claim is made. It is tamper-evident framing (Part 11 framing only); the anchor is unsigned and retention is hold-all by interim decision. |
| Where is the cloud / enterprise integration? | No real enterprise system, endpoint, credential or SLA exists (OD-28). Integration is against archived synthetic interfaces and fixtures. |
| What breaks first at scale? | Unknown, never measured. Candidates: SQLite write contention, the 145 s+ group runtimes of the test suite, vacant owners. |

## Evidence References
`docs/10-architecture/` (summary, options, ADRs), `docs/16-repo-validation/`, `docs/27-hardening/hardening-plan.md`, `docs/28-reliability/resilience-readiness.md`, `docs/30-release/go-no-go-criteria.md`, `docs/25-governance/risk-acceptance-register.md` RP-03; claims C-07..C-10, C-12, C-13, C-16..C-18.

## Assumptions
- A-42-05 [Assumption] Architecture options comparison at Stage 10 is a fair basis for the choice. Confirm: Dinesh.

## Unknowns
- Per-ADR acceptance (U-42-01); buy vs build (OPD-10); capacity; behaviour on Python 3.12+; behaviour with real data volumes.

## Unresolved Issues
- OPD-05, OPD-10, OPD-11 accepted open; layer-leak and import-cycle debt (cycles reported removed in Stage 27, not re-verified here); wiring of Stage 28 controls (D-28-01/02).

## Residual Risks
RS-01..RS-16, RP-03, RP-06, RP-11 (legacy keeps its control gaps while legacy runs, including `0.0.0.0` bind in the legacy compose file) remain open, none accepted.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-25 | claude-fde-agent | Initial. |
