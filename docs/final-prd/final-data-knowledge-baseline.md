---
stage: "FINAL — Authoritative Final As-Built PRD (run as Stage 43)"
artifact: "final-data-knowledge-baseline.md"
version: "v0.1"
date: "2026-10-25"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["data/legacy.sqlite3 (sha256 only)", "docs/11-data-context/", "docs/17-implementation-prd/implementation-prd.md", "docs/21-integration/integration-inventory.md", "docs/41-retirement/legal-hold-check.md", "docs/29-incident-bcdr/", "docs/38-handover/open-handover-items.md", ".fde/orchestrator-decisions.md"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated against any organisation. Documentation only. Authoritative ONLY as "as-built, NOT released": the hub is a shadow build; nothing here records a release, an approval, realised value or a sign-off.**

## Summary
The data baseline is a 125-case synthetic snapshot plus the hub's append-only stores built from it. There is no real data, no knowledge base and no AI index. Retention is hold-all; backup is single-device.

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
### DK-1 Baseline data [Verified Fact]
- As-found baseline: `data/legacy.sqlite3`, **125 cases**, sha256 `c254649f…d70aa`, seed 4100 (OD-02 confirmed by OD-09); backup in `../_data-backup-2026-10-17/` with SHA256SUMS (OD-03/OD-03a). Tag `baseline-as-found` = a6eb4e8 (OD-06). The README's 6,000-case dataset (seed 4326) is not part of the baseline.
- All data is **synthetic**; no real or production data, user or telemetry exists (OD-04; K-21 = 0 of 125). Every figure is labelled 'synthetic, unvalidated'.
- `data/` is not to be written or tested in place; code runs only in full copies outside the tree (OD-03a).

### DK-2 Hub store contents on shipped data [Verified Fact, Stage 17 / Stage 21]
| Item | Value |
|---|---|
| Raw intake items | 10,983 (append-only); REPLAY 67 to NOOP_DUPLICATE; legacy replay DUPLICATE 64 (DV-02) |
| Intake outcomes | EXCEPTION 8,109 (UNMATCHED_REF 7,903; NO_BUSINESS_KEY 206), QUARANTINED 223, VALIDATED 165, VALIDATED_WITH_FLAGS 3, NOOP_DUPLICATE 67 (DV-07a) |
| Crosswalk links | 168 exact-key links (deviation-batch, capa-deviation, lab_result-batch) |
| Cases backfilled | 125 (as-of is a created_at proxy) |
| Month-end total | hub 622,826.44 (n 125) vs legacy report 742,956.61 (join fan-out), DV-01 |
| Rule sets | 3 as-found sets loaded, INACTIVE; no active set |
| Zone H holders | `[]` |
| Policies | 5 candidates, none adopted |

### DK-3 Knowledge / search [Verified Fact]
No knowledge base, vector store, embedding or model exists (No-AI). Keyword/FTS5 reviewer search over 22 document bodies exists but is **off** (`search.enabled` false, `search.fts` off); search ranking quality is unassessed (RTD-80); FTS5 availability on the production runtime is Unknown (RTD-79). Document bodies are search corpus, not intake (PCH-44).

### DK-4 Data classification and retention [Verified Fact / Assumption]
[Verified Fact] Field classes C0..C3 are built (R2, dark) on a PROPOSED map; a C3 read needs a reason and is audited (C3_READ). [Assumption] Classes, tenant dimension and privacy regime (DPDP/GDPR named) are undecided (RS-06, RP-07). [Verified Fact] Retention is **hold-all** (OD-15, OD-30): no deletion path exists; insert-only triggers. Session and login-attempt rows are archived with the store (D-41-08 open). Stage 41 legal-hold check is INCOMPLETE; every asset is treated as held (NR-5).

### DK-5 Lineage and reproducibility [Verified Fact]
Metrics reproduce from stored inputs; projection check 0 mismatches after backfill; goldens captured on Python 3.10.12 are environment-specific (10 of 16 CT checks differ on 3.13 by environment only, OD-23); CT-13 fails on Node patch drift (v22.23.2 golden vs v22.23.4 laptop; S24-DEV-04).

### DK-6 Backup and recovery [Verified Fact]
Backup-before-migrate; restore with checksum rehearsed on sandbox copies (T-03). Off-device copy NOT made (HAR-09, AP-OPS-04 OPEN); the baseline lives in git-ignored files (`data/*.sqlite3`, `data/lake/`) on one laptop (HO-13). [Inference] Single-device loss would be unrecoverable without the backup folder on the same device.

## Evidence References
See `evidence_sources` in the header and the per-row evidence columns.

## Assumptions
- A-43-07 [Assumption] Counts in DK-2 are those recorded at Stage 17/21 on the sandbox; I did not re-run the hub (docs-only).

## Unknowns
- U-43-06 Production data classes, tenant, privacy regime, retention periods (D-41-06, RS-06).

## Unresolved Issues
- See `open-items-and-decision-register.md`.

## Residual Risks
- See `residual-risk-register.md`.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-25 | claude-fde-agent | First issue. |
