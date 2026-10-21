---
stage: "23 — HITL/HOTL & Deterministic Control Boundaries"
artifact: "README.md"
version: "v0.1"
date: "2026-10-21"
author_agent: "claude-fde-agent"
status: "IN REVIEW"
evidence_sources: ["docs/17-implementation-prd/implementation-prd.md IP-5 (IC-1..IC-8)", "docs/12-specs/ (frozen v0.1)", "docs/12-specs/contracts/schemas/", "docs/23-human-control/stage12-v0.2/error-code-registry.json", "docs/23-human-control/stage12-v0.2/schemas/", "docs/23-human-control/stage12-v0.2/schema-addendum-changes.json", "hub/control/registry.py", "tests/hub/test_tst_hub_stg23_registry.py", "tests/hub/test_tst_hub_stg23_schemas.py", ".fde/orchestrator-decisions.md OD-25, OD-29"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated. The product is No-AI (OD-08). zone_h.holders ships EMPTY; every holder named in a test is SYNTHETIC TEST DATA, not an approver. approval_ref values are references the hub cannot verify (Unknown). Nothing here is a human approval; the sole provisional approver is Dinesh Naik (OD-01).**

## Summary
Stage 12 v0.2 addendum package (DW-13). The Stage 12 v0.1 files stay frozen and unchanged; this folder adds the v0.2 content approved by Dinesh Naik (OD-25: IC-1..IC-8 approved as Stage 12 v0.2 content; OD-29: the exit-code clashes 2 and 9 are documented and the numbers kept). It carries a **generated** error-code registry (109 codes, regenerated from `hub/**` and diffed by a test), the exit-code table, and 16 additive JSON schemas (v0.2) that the built hub's stored objects validate against.

## Findings
### Package contents
| IC | Subject | Normative text | v0.2 artefact in this folder | Stage 23 change over IP-5 |
|---|---|---|---|---|
| IC-1 | Exit codes (CLI) | IP-5 IC-1 | exit-code table in `error-code-registry.md` (generated) | clashes 2 and 9 documented, numbers kept (OD-29); families 19 / 31 / 32 documented; uniqueness test |
| IC-2 | Error codes beyond the 82-code registry | IP-5 IC-2 | `error-code-registry.json` / `.md` (generated) | 109 codes in code: 79 in the Stage 12 spec, 30 added; 3 spec codes have no class; 2 code literals are not classes (listed in the file) |
| IC-3 | Configuration keys | IP-5 IC-3 | `schemas/hub-config.schema.json` (effective configuration) | adds the `approval_refs` key (flag path -> approval reference) and the validated `capability_authority` object |
| IC-4 | Migrations and version tables M000..M007 | IP-5 IC-4 | by reference | none |
| IC-5 | Token and credential formats | IP-5 IC-5 | by reference | none |
| IC-6 | Audit actions and event types | IP-5 IC-6 | by reference | CONFIG_CHANGED now also carries `flag:<path>` objects, `direction` and, for an L3 flip, `rollback: "L3"` |
| IC-7 | API and schema additions | IP-5 IC-7 | `schemas/*.schema.json` (16) and `schema-addendum-changes.json` | additive fields for intake-outcome, metric-value, partner-feed-envelope; error-envelope `details` nullable; hub-config rewritten |
| IC-8 | Runtime | IP-5 IC-8 | by reference (OD-24: production 3.12+, floor 3.10) | none |

"By reference" means IP-5 of `docs/17-implementation-prd/implementation-prd.md` is the text of record for that IC (approved by OD-25 as v0.2 content); it is not copied here so the two cannot drift.

### Exit-code table (generated; OD-29 documents the clashes and keeps the numbers)
| Exit | Codes | Classification | Note |
|---|---|---|---|
| 1 | E-HUB-INTERNAL | unique |  |
| 2 | E-AUTH-PASSWORD-POLICY, E-CFG-INVALID, E-FX-HASH | documented_clash | usage / E-FX-HASH / E-CFG-INVALID / E-AUTH-PASSWORD-POLICY share exit 2 (INC-02 / INC-03 choices; RTD-21) |
| 3 | E-HUB-KILLED | unique |  |
| 6 | E-CO-UNAPPROVED-DEVIATION | unique |  |
| 7 | E-CO-NOT-SANDBOX | unique |  |
| 8 | E-CO-RUNTIME-UNSUPPORTED | unique |  |
| 9 | E-CO-DENYLIST-IMPORT, E-SEC-EXPOSURE-NOT-APPROVED | documented_clash | E-CO-DENYLIST-IMPORT (INC-02) and E-SEC-EXPOSURE-NOT-APPROVED (as specified) share exit 9 (RTD-24, DEV-23) |
| 10 | E-CO-LEGACY-WRITE-REFUSED | unique |  |
| 11 | E-CO-EGRESS-ATTEMPT | unique |  |
| 12 | E-INT-UNTRUSTED-USE | unique |  |
| 13 | E-CO-LEGACY-SCHEMA-DRIFT | unique |  |
| 14 | E-OBS-TRIPWIRE | unique |  |
| 15 | E-STORE-MIGRATION-DRIFT | unique |  |
| 16 | E-SEC-SCAN-FINDINGS | unique |  |
| 17 | E-SEC-AUDIT-TAMPER-DETECTED | unique |  |
| 18 | E-SEC-AUDIT-WRITE-FAILED, E-SEC-SECRET-IN-AUDIT | shared_within_area |  |
| 19 | 11 codes (E-AUTH-BAD-CREDENTIALS, E-AUTH-FORBIDDEN, E-AUTH-LOCKED ...) | documented_family | access-refusal family: E-AUTH-*, E-GATE-NO-HOLDERS / NOT-AUTHORISED / REAUTH-REQUIRED / UNKNOWN-ACTION, E-SEC-CSRF, E-SEC-REASON-REQUIRED (INC-03 / 04 / 08 / 09) |
| 20 | E-CO-RELEASE-BLOCKED | unique |  |
| 21 | E-STORE-BACKUP-INVALID | unique |  |
| 22 | E-STORE-NOT-MIGRATED | unique |  |
| 23 | 10 codes (E-POL-AUTHORITY-REQUIRED, E-POL-CLOCK-CALENDAR-REQUIRED, E-POL-DECISION-REQUIRED ...) | shared_within_area |  |
| 24 | E-POL-ASFOUND-DRIFT | unique |  |
| 25 | 18 codes (E-DEC-CASE-EXISTS, E-DEC-CASE-ID-INVALID, E-DEC-CASE-NOT-FOUND ...) | shared_within_area |  |
| 26 | 7 codes (E-ID-AMBIGUOUS-TYPE, E-ID-LINK-EXISTS, E-ID-LINK-NOT-FOUND ...) | shared_within_area |  |
| 27 | E-DEC-BACKFILL-MISMATCH | unique |  |
| 28 | 7 codes (E-INT-CONFLICT-ALREADY-RESOLVED, E-INT-ENVELOPE-INVALID, E-INT-ITEM-NOT-FOUND ...) | shared_within_area |  |
| 29 | 5 codes (E-RUN-ALREADY-RUNNING, E-RUN-CHECKPOINT-INVALID, E-RUN-SCHEDULE-DISABLED ...) | shared_within_area |  |
| 30 | 9 codes (E-MET-CUTOFF-REQUIRED, E-MET-DEFINITION-REQUIRED, E-MET-NOT-AVAILABLE ...) | shared_within_area |  |
| 31 | 15 codes (E-GATE-EXTREF-INVALID, E-GATE-MODE-NONE, E-GATE-PACK-STALE ...) | documented_family | request / gate / reviewer family: E-GATE-* payload and mode errors, E-REQ-*, E-REV-* (INC-08) |
| 32 | E-R2-INPUT-INVALID, E-REV-INDEX-ABSENT | documented_family | R2 family: E-R2-INPUT-INVALID, E-REV-INDEX-ABSENT (INC-09) |

- **Documented clashes** (two meanings on one number, kept): 2 = E-FX-HASH, E-CFG-INVALID, E-AUTH-PASSWORD-POLICY; 9 = E-CO-DENYLIST-IMPORT, E-SEC-EXPOSURE-NOT-APPROVED. A script must read the JSON `code`, not the exit number, to tell them apart.
- **Families** (one area-spanning group on one number): 19 access refusals, 31 request / gate / reviewer, 32 R2.
- Exit 6, 7 and 8 keep their specified meanings.

### Schemas
- 16 v0.2 schemas (draft-07, `$id` suffix `:v0.2`) derived from the frozen v0.1 files by `docs/23-human-control/evidence/s23_make_v02_schemas.py`; only additive changes (new optional properties, one widened type, `hub-config` rewritten).
- Test STG23 S32 validates built objects: 0 invalid under v0.2; under v0.1 exactly the 5 changed schemas fail (the addendum is needed and sufficient). 16 of 16 schemas are exercised.
- **23 store tables have no Stage 12 JSON schema** (list in `evidence/store-table-coverage.json`, pinned by S33). That is a gap, not a pass: FAC-09 scope for these tables is a decision for Dinesh.

### Findings
- [Verified Fact] Codes in code = codes in the registry, diff 0, from three derivations (STG23 S20).
- [Verified Fact] No undocumented exit-code clash exists; the two documented clashes are still present (S22); a planted clash or a silent renumbering is reported (S23).
- [Verified Fact] A validator written for the draft-07 subset the schemas use agrees with `jsonschema` 3.2.0 on all 16 schemas in exploration; `jsonschema` is not a product dependency.
- [Inference] Freezing v0.2 as the new baseline needs Dinesh's confirmation of the exit-code table and the 23-table gap.
- [Unknown] Whether OP-INT-01's intake envelope needs a 17th schema (its field names are in IC-7 but no schema file exists).

## Evidence References
Files above; STG23 S20..S24 and S30..S34; `evidence/schema-validation.json`, `exit-code-uniqueness.json`, `error-registry-check.json`.

## Assumptions
- A-23-12 IP-5 is the text of record for IC-4, IC-5, IC-6, IC-8 (approved by OD-25).

## Unknowns
- U-23-14 Need for an intake-envelope schema. U-23-15 FAC-09 scope for the 23 schema-less tables.

## Unresolved Issues
- 23 tables without a schema (documented gap).

## Residual Risks
- A consumer may assume v0.2 covers every table; it covers 10 of 33 (RR-HC-7, Low).

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-21 | claude-fde-agent | Initial issue (Stage 23 BUILD). |
