---
stage: "7 — Deep Brownfield Repository Assessment & Behaviour Baseline"
artifact: "repo-transformation-readiness.md"
version: "v0.1"
date: "2026-10-17"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/07-repo-assessment/repo-assessment.md", "docs/07-repo-assessment/baseline-test-results.md", "docs/07-repo-assessment/baseline-behaviour.md", "docs/07-repo-assessment/characterization-test-plan.md", "docs/07-repo-assessment/technical-debt-register.md", "docs/07-repo-assessment/critical-workflow-inventory.md", "docs/07-repo-assessment/security-code-quality-findings.md", "docs/07-repo-assessment/maintainability-assessment.md", "docs/06-root-cause/root-cause-readiness.md", "docs/00-preflight/operating-contract/*", ".fde/orchestrator-decisions.md"]
supersedes: "none"
---
## Summary

**Readiness verdict: READY FOR TRANSFORMATION PLANNING (Stage 8-14); NOT READY FOR CODE CHANGE (Stage 15) until the P0 conditions R-1..R-5 below are met.** Planning is safe now because the as-found behaviour is captured, deterministic and mutation-validated, the data is backed up and checksum-gated, and no source was modified. Code change is not yet safe because the golden baseline is not an executable regression suite, the existing tests are destructive and non-protective, the dataset identity is provisional, and three decisions (RC-3 authority, dataset OD-02, disposition location) are open.

## Findings

### Readiness checklist

| ID | Criterion | Status | Evidence | Gap / action | Owner | Due stage |
|---|---|---|---|---|---|---|
| R-1 | Behaviour baseline captured and reproducible | **Met (data)** / **Partial (executable)** | 3 goldens, 2 identical runs; 14/14 mutants replay-killed | Convert to harness (CT-H1..H7) | Engagement lead (Dinesh Naik) | 14 plan / 15 build |
| R-2 | Safe execution pattern for tests | **Not met in repo; met in sandbox** | TQ-01; OD-03a | Hermetic fixture (CT-H1); never run in working tree | Engagement lead (Dinesh Naik) | 15 |
| R-3 | Data backup + integrity gate | **Met** | `../_data-backup-2026-10-17/SHA256SUMS.txt` (1,512 entries) verified before and after | none | orchestrator | - |
| R-4 | Baseline dataset decision | **Provisional** | OD-02; BB-12 | Confirm 125/4100 vs 6000/4326 (or both) | Engagement lead (Dinesh Naik) | 8 |
| R-5 | Authority for rule conflicts (fix vs preserve) | **Open** | RC-3, TD-05 | Decide approval/closure definition owner | Engagement lead (Dinesh Naik) | 8 |
| R-6 | Critical workflows inventoried with baseline | **Met** | 14 workflows | criticality is inference (A-07-06) | Engagement lead (Dinesh Naik) | 8 |
| R-7 | Characterisation plan | **Met** | CT-01..18 | build it | - | 15 |
| R-8 | Environments for parity | **Partial** | Python 3.10.12/JDK 11/Node 22 only | run on 3.12; Docker/Compose tier E2 | Engagement lead (Dinesh Naik) | 14 |
| R-9 | Tooling (coverage, lint, SAST/SCA, formatter) | **Not available offline** | C-4 | procure/enable in BUILD sandbox | Engagement lead (Dinesh Naik) | 14 |
| R-10 | Human-approval boundary for disposition preserved | **Met (documented)** | CW-14, CT-16 | encode CT-16 guard | - | 15 |
| R-11 | Security posture adequate for any non-local exposure | **Not met** | SC-01/02/06 | design stages 23-25 | Engagement lead (Dinesh Naik) | 23-25 |
| R-12 | Documentation safe to follow | **Not met** | TD-04 | correct on a BUILD branch | Engagement lead (Dinesh Naik) | 15 |

### Transformation risk heat map (inputs to Stage 14)

| Area | Change risk | Why | Prerequisite |
|---|---|---|---|
| `app/legacy_logic.py` + callers | Medium | tiny code, but decision semantics (RC-4/RC-3) | CT-01..03 + R-5 |
| `app/server.py` | High | untested god handler | CT-04 |
| `app/partner_feeds.reconcile` | High | destructive in-place state | CT-08, append-only decision |
| `app/gateway_bridge.py` + gateway | Medium | idempotent but silent drops | CT-06/07 |
| `legacy_batch`, Java, SQL | High (numbers) | wrong-but-pinned figures; consumers unknown | CT-10..12 + disposition per defect |
| `app/store.py` (config) | High (ripple) | import-time global used by 11 modules | harness first (R-2) |
| Generators / `data/` tooling | Low | not production behaviour, but reproducibility baseline | CT-14 |
| Missing capabilities (decision write path, audit trail) | Highest | net-new, regulated | Stage 8-13 requirements; HAR-12 |

### Recommended sequence (input, not a plan)

1. Stage 8 decisions: R-4, R-5, disposition location. 2. Stage 14: choose harness approach (subprocess-per-test vs refactor-for-injection), tooling, 3.12 baseline. 3. Stage 15 (BUILD branch): implement CT harness against untouched code -> verify green + 15/15 mutants killed -> only then any refactor. 4. Re-capture goldens only via the reviewed `--update-golden` path (CT-H4). 5. Compare in Stage 16 using the same scripts.

### Go / no-go summary

| Decision | Verdict |
|---|---|
| Proceed to Stage 8 | **Go** |
| Begin refactoring/modernisation code | **No-go** until R-1(executable), R-2, R-4, R-5 are met |
| Run existing tests in the working tree | **No-go** (TQ-01) |

## Evidence References

Artifacts listed in `evidence_sources`; integrity attestation in `repo-assessment.md`.

## Assumptions

- A-07-18: Stage 14/15 will be allowed to add a `tests/characterization/` tree and tooling config on a BUILD branch (WB-04/WB-05 with HAR-07 for CI/config). Confirm: orchestrator / Engagement lead (Dinesh Naik).

## Unknowns

- U-07-10: Whether the transformed system is intended to keep SQLite/Python or move platform (Stage 14); readiness items R-8/R-9 depend on it.

## Unresolved Issues

- Open decisions R-4, R-5; items marked Partial/Not met above.

## Residual Risks

- R-07-14: Pressure to start refactoring because the suite is green and fast (TQ-09) while it offers almost no protection (TQ-05).

## Change History

| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-17 | claude-fde-agent | Initial readiness assessment. |
