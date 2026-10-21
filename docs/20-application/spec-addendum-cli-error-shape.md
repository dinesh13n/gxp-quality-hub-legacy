---
stage: "20 — Application & Services Engineering"
artifact: "spec-addendum-cli-error-shape.md"
version: "v0.1"
date: "2026-10-21"
author_agent: "claude-fde-agent"
status: "IN REVIEW"
evidence_sources: ["hub/core/errors.py (HubError.envelope)", "hub/obs/log.py envelope_with_correlation", "hub/*/cli.py (10 runners)", "hub/web/wire.py (HTTP wrapper)", "tests/hub/test_tst_hub_stg20_r1_gaps.py S10", "docs/16-repo-validation/security-scan-summary.md SS-07", "docs/17-implementation-prd/finalized-acceptance-criteria.md FAC-10", ".fde/orchestrator-decisions.md OD-26 (DQ-05)"]
supersedes: "none (addendum to docs/12-specs/error-handling-spec.md; the Stage 12 file is not edited, HAR-13)"
---
**Label: synthetic repository, unvalidated. This addendum records the CLI error shape AS BUILT, by the Engagement lead's decision DQ-05 (OD-26: "hub CLI errors keep their current shape, documented as a spec addendum; no behaviour change"). It is proposed spec text; acceptance of the addendum is part of the Stage 12 v0.2 package (DW-13, Stage 23).**

## Summary
FAC-10 allows either option; DQ-05 chose "record the CLI shape as an addendum". No code changed for DW-09. The shape below is pinned by the new test TST-HUB-STG20-S10 over all ten runners.

## Findings
- [Verified Fact] **CLI error shape (all `python -m hub*` runners).** On a refused command the runner writes exactly ONE JSON object to stderr (`json.dumps(sort_keys=True, indent=1)`), writes nothing to stdout, and exits with the error class's exit code:
  `{"code": "E-...", "message": "<fixed text per code>", "details": <object|null>}`.
  Runners `hub.metrics`, `hub.r2`, `hub.runs`, `hub.search`, `hub.web` add `"correlation_id": "<id>"` (AC-OBS-01, INC-07+); runners `hub`, `hub.admin`, `hub.decision`, `hub.intake`, `hub.policy` do not. An error raised before the correlation id exists may use the base shape on any runner (accepted by S10).
- [Verified Fact] **HTTP error shape is different and unchanged:** the HTTP layer wraps the same envelope as `{"error": {code, message, correlation_id, ...}}` (`hub/web/wire.py`). The CLI never uses the `error` wrapper (S10 asserts it is absent).
- [Verified Fact] **Exceptions to the JSON rule:** argparse usage errors (unknown option / missing argument) print argparse's plain-text usage and exit 2 (`EXIT_USAGE`); `golden-compare` exit 6 is a result (the report is on stdout), not an error envelope.
- [Verified Fact] Observed (S10, Python 3.10.12): kill switch -> `E-HUB-KILLED`, exit 3, all 10 runners; runtime floor 3.12 on 3.10 -> `E-CO-RUNTIME-UNSUPPORTED`, exit 8, all 10 runners.

## Evidence References
`tests/hub/test_tst_hub_stg20_r1_gaps.py::test_TST_HUB_STG20_S10_cli_error_shape_all_runners` (green, sandbox run 2026-10-21); prototype probe over the 10 runners (kill / bad anchor) in the Stage 20 session (key sets as above).

## Assumptions
- A-20-CLI-1 [Assumption] Operator tooling parses stderr JSON per runner family; confirm: Engagement lead (Dinesh Naik).

## Unknowns
- U-20-CLI-1 Whether exit codes 2 and 9 collisions (DQ-04) change before CI scripts depend on them (Stage 23).

## Unresolved Issues
- Formal acceptance as Stage 12 v0.2 content (DW-13 / DQ-03 scope, Stage 23).

## Residual Risks
- RR-CLI-1 Two CLI shapes (with / without correlation_id) remain; a parser must tolerate both (Low).

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-21 | claude-fde-agent | First issue (DW-09, DQ-05 / OD-26). |
