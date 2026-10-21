---
stage: "19 — Intelligence Core — Prompt, Retrieval & Model Engineering"
artifact: "not-applicable.md"
version: "v0.1"
date: "2026-10-20"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: [".fde/orchestrator-decisions.md OD-08 (and OD-23, OD-24)", ".fde/stage-prompts/19_Intelligence-Core-Prompt-Retrieval-and-Model-Engineering.md (Conditional stage clause)", "docs/08-ai-qualification/qualification-decision.md (QD-1, QD-3, QD-4)", "docs/09-initial-prd/non-goals.md (NG-01, NG-B)", "docs/09-initial-prd/initial-prd.md", "docs/10-architecture/adrs/ADR-002-no-ai-boundary-enforcement.md", "docs/11-data-context/retrieval-strategy.md", "docs/17-implementation-prd/implementation-prd.md (IP-7 OD-08 Decided)", "docs/15-modernization/test-execution-log.md (TST-CO-12, E05..E09EGRESS)", "docs/15-modernization/evidence/inc03|inc04/hub-final-C_inner-egress-run.json", "docs/16-repo-validation/evidence/cloud-regression.log", "docs/16-repo-validation/architecture-conformance-report.md", "docs/16-repo-validation/security-scan-summary.md SS-01", "hub/guards/no_ai.py, hub/guards/egress.py, hub/obs/metrics.py, hub/obs/collect.py, hub/ops/release.py (G5), hub/core/untrusted.py", "hub/policy/engine.py, hub/review/templates.py, hub/search/, hub/r2/drafts.py + templates.json, hub/metrics/", "tests/hub/test_inc09_egress_guard.py", "docs/00-preflight/ai-economics/provisional-model-call-inventory.md (MC-01..MC-05)"]
supersedes: "none"
---
## Summary

**Stage 19 is NOT APPLICABLE.** The stage prompt's conditional clause applies: *"If Stage 8 selected No-AI, create `not-applicable.md` in the stage folder with the justification and stop."* Stage 8 recommended No-AI and Dinesh Naik approved it (OD-08, 2026-10-18). There is no prompt, model configuration, embedding, retrieval-augmented generation, extraction model or inference path to build, evaluate or gate. The 12 artifacts listed under the prompt's "Required Artifacts" are therefore **not produced**. Producing them would design intelligence that Stage 8 did not approve, which the prompt's Scope excludes.

**Outcome: NOT APPLICABLE.** This is the skip outcome the prompt defines. The skip is fully evidenced, so there is no blocking condition. Proceed to Stage 20. Label: synthetic repository, unvalidated against any organisation.

## Findings

### NA-1 Justification

| # | Finding | Evidence | Label |
|---|---|---|---|
| 1 | The AI decision is **No-AI**, approved by the sole approver. The product is rules, keyword/FTS search, templates and a deterministic core. OD-08 itself says "Stage 19 = not-applicable.md". | `.fde/orchestrator-decisions.md` OD-08 ("Approved by Dinesh (2026-10-18)") | Verified Fact |
| 2 | Stage 8 decided every touchpoint as follows: T1 rules (rule trace), T2 rules + reason codes, T3 keyword/field search (AI-assisted not selected, conditional on RQ-1..RQ-3), T4 rules/template, T5 rules (agentic rejected). For Stage 19, QD-4 says "Nothing to build". | `docs/08-ai-qualification/qualification-decision.md` QD-1, QD-4 | Verified Fact |
| 3 | The PRD contains no AI functional requirement. NG-01 excludes all AI/LLM/ML/agentic capability. The Implementation PRD records OD-08 as **Decided**: "no model calls". | `docs/09-initial-prd/non-goals.md` NG-01; `docs/09-initial-prd/initial-prd.md` l.84; `docs/17-implementation-prd/implementation-prd.md` IP-7 | Verified Fact |
| 4 | The retrieval strategy is deterministic keyword and field retrieval only. It has no embeddings, no vector store, no LLM reranker, no generated answers and no RAG. Results are always original documents with provenance. | `docs/11-data-context/retrieval-strategy.md` | Verified Fact |
| 5 | The Stage 19 dimensions (retrieval relevance, groundedness, answer quality, hallucination, abstention, model latency/cost) have nothing to measure. No generation step exists. Search relevance of the deterministic T3 search is a product-quality concern for Stages 20/26 and the RQ-1 baseline. It is not a Stage 19 model metric. | Findings 1-4 | Inference |
| 6 | Stage 19 also depends on Stage 18. Stage 18 is in progress concurrently, and `docs/18-*` did not exist when this record was written. The skip does not depend on Stage 18, because there is no intelligence rubric to consume. | `ls docs/` at 40b2762 | Verified Fact (absence) / Inference (no dependency) |

### NA-2 Deterministic components that cover the need (as built, read-only inspection)

| Need (touchpoint) | Deterministic component | Property | Label |
|---|---|---|---|
| T1 triage explanation / "deterministic rule/explanation module" (OD-08) | `hub/policy/engine.py` (rule evaluation returns `outcome`, row-by-row `trace`, `defaulted` marker); `hub/review/templates.py` (`trace_template/1`) | Explanation text is rendered only from stored trace fields. The module docstring says "Pure: no I/O, no clock, no randomness, no network, no model", and its output is byte-identical (PNFR-17). The three as-found rule sets are loaded **inactive**. Activation needs a Zone H decision, and `zone_h.holders` is empty (OD-16/17). | Verified Fact |
| T2 feed exception classification | `hub/intake/*` (contracts, reasons, validate, quarantine); `hub/intake/untrusted_lint.py`; `hub/core/untrusted.py` | Reason codes plus quarantine. Inbound text is wrapped as `Untrusted` and cannot reach decision fields (ADR-002 B(3)). | Verified Fact |
| T3 document Q&A | `hub/search/` (`fts.py` FTS5 probe/select, `engine.py` `R2SearchService`, `text.py` Python fallback, `corpus.py` derived index) | Keyword/field search runs on SQLite FTS5 with a runtime-detected fallback. Every search test asserts identical results on both engines (`evidence/inc09/planned-tests.md`). It ships **off**: `search.enabled false`, `search.fts "off"` (`hub/search/settings.py`). | Verified Fact |
| T4 deviation/CAPA narrative | `hub/r2/drafts.py` + `hub/r2/templates.json` | Deterministic template drafts with field validation. They ship **off** (`templates.enabled false`). | Verified Fact |
| T5 cross-store investigation | `hub/crosswalk/*`, `hub/r2/joined.py` | Exact-key crosswalk. Orphans are reported and never guessed. | Verified Fact |
| Figures/KPIs | `hub/metrics/*` | Deterministic metrics with definition tags, reproducible from stored inputs. | Verified Fact |

### NA-3 Evidence that no model is called

| # | Evidence | Result | Source | Label |
|---|---|---|---|---|
| E-1 | Structural deny-list: `hub/guards/no_ai.py` blocks imports and manifest entries for openai, anthropic, transformers, torch, tensorflow, langchain*, langgraph, llama*, etc., plus prefix families. Exit E-CO-DENYLIST-IMPORT. | TST-CO-11 a-d PASS. The deny-list scan of hub/ + tests/hub found 0 findings. | `docs/15-modernization/test-execution-log.md` (TST-CO-11); `dependency-changes.md` | Verified Fact |
| E-2 | Egress guard: `hub/guards/egress.py` patches connect/connect_ex/sendto/getaddrinfo, allows loopback only and counts `egress_attempts_total`. | Installed at every CLI start (RD-18). | `docs/15-modernization/refactoring-decisions.md` RD-18 | Verified Fact |
| E-3 | Zero-tripwire: `hub/obs/metrics.py` defines `model_calls_total`. "The product has no model client, so nothing increments it". The only incrementer is `record_model_call`, a sensor that any future approved AI element would have to call. | Exported at the end of every CLI run (`hub/obs/collect.py` TRIPWIRE_NAMES). Release gate G5 requires it to equal 0 (`hub/ops/release.py`). | code | Verified Fact |
| E-4 | Stage 15 TST-CO-12 e: the full INC-02..04 suite was re-run under the egress guard. | `{"egress_attempts": [], "tests_run": 123, "successful": true, "tripwires": {"egress_attempts_total": 0, "model_calls_total": 0}}` | `docs/15-modernization/evidence/inc04/hub-final-C_inner-egress-run.json` (also inc03, 86 tests) | Verified Fact |
| E-5 | Stage 15 E05EGRESS, E06EGRESS, E07EGRESS, E08EGRESS, E09EGRESS: the modules of each later increment ran under the guard. Each test asserts `egress_attempts == []` and `tripwires == {"egress_attempts_total": 0, "model_calls_total": 0}` (e.g. `tests/hub/test_inc09_egress_guard.py` l.36-37). | Every group: ok, "0 attempts, model_calls_total 0". | `test-execution-log.md` (E05 l.164, E07 l.198, E09 l.239; E06 per `inc06-design-notes.md` D-14; E08 l.217/248) | Verified Fact |
| E-6 | Stage 16 cloud regression at 2c63b07 (Python 3.13.16, OD-23). | Group C 5 ok; I45/I6/I7 (which contain E05..E07EGRESS) 88/43/59 ok; E8 1 ok; E9 1 ok; 0 FAIL/ERROR; checksums rc 0 before and after. | `docs/16-repo-validation/evidence/cloud-regression.log`; `regression-results.md` R-1 | Verified Fact |
| E-7 | Stage 16 conformance: ADR-002 "Conforms (manual gate)". SS-01: "zero model calls (No-AI OD-08 holds)". | — | `architecture-conformance-report.md`; `security-scan-summary.md` SS-01 | Verified Fact |
| E-8 | The code validated at Stage 16 is the code at HEAD. `git diff --stat 2c63b07 40b2762 -- hub tests pyproject.toml .github` is empty. A read-only grep on 2026-10-20 for `import`/`from` of openai, anthropic, transformers, torch, tensorflow, langchain, langgraph, llama, sentence_transformers, sklearn, numpy, requests or httpx in hub/ and tests/hub found 0 matches. | — | this stage, read-only | Verified Fact |
| E-9 | The evidence above comes from sandbox test runs only. No production or runtime telemetry exists (OD-04). | — | OD-04 | Verified Fact (limitation) |

### NA-4 What would restart this stage

Stage 19 restarts **only** if both of the following happen: (a) a re-qualification trigger fires and Stage 8 is re-run for that specific element; and (b) Dinesh records a new decision that supersedes OD-08 for that element (HAR-10/HAR-11; BR-AI-1..7). ADR-002 would then be superseded.

| ID | Trigger (from QD-3 / non-goals NG-B) | Evidence required before any Stage 19 work |
|---|---|---|
| RQ-1 | A real or realistic document corpus becomes available (U-V02) | A labelled question set (proposal: ≥50 questions with known answer documents) and the measured top-5 recall of the as-built FTS5/fallback search. AI is considered only below a threshold Dinesh sets (proposal: 80%). |
| RQ-2 | Real content is multilingual or OCR-noisy in a way the baseline demonstrably fails | Baseline failure examples per language/quality band |
| RQ-3 | A named stakeholder requests a language-based touchpoint and accepts a reviewer-time budget | A recorded request with an owner and measured reviewer minutes |
| RQ-4 (agency, Stage 22) | Only after RQ-1..3 produced an approved AI element and the crosswalk exists | Measured residual cross-store set that deterministic queries cannot resolve |

On restart, Stage 19 must follow its own prompt from the start: evaluation datasets are built **before** any tuning, with the RQ-1 labelled set as the seed. Every AI call must go through `record_model_call`, so the G5 / Stage 32 tripwire is replaced by budgeted counting rather than silently bypassed.

### NA-5 What downstream stages inherit

| Stage | Inherits |
|---|---|
| 20 Application | The as-built deterministic modules (NA-2) are the whole "intelligence". There is no model client, prompt store or AI adapter slot (ADR-002 option C rejected). |
| 22 Agentic engineering | **Not triggered** (OD-08; `minimum-agency-assessment.md`). Record its own not-applicable note. |
| 26 TEVV | No model evaluation. TEVV covers deterministic behaviour, the planted-string suite (86/22/44, release gate G9) and the No-AI gates. |
| 31 Observability | `model_calls_total` and `egress_attempts_total` are zero-tripwires. They are not AI telemetry. |
| 32 FinOps | Track zero model calls as a tripwire. Token and model-call lines are asserted as 0. Scenarios S3/S4 (MC-01..MC-05 in `provisional-model-call-inventory.md`) stay **dormant**. Add reviewer-time measurement for rule-flagged items (QD-4). |
| 27 / CI | The No-AI gates (TST-CO-11/12, E05..E09) run only manually today. `.github/workflows` is unchanged, and CI wiring is still missing (RTD-14, S16 RG-05). Until that is fixed, G5 is a manual gate. |

## Evidence References

See the front-matter `evidence_sources`. Prompt: `.fde/stage-prompts/19_Intelligence-Core-Prompt-Retrieval-and-Model-Engineering.md`. The repo was inspected read-only at `main` 40b2762. No code was run. Nothing outside `docs/19-intelligence/` was written.

## Assumptions

- A-19-01 [Assumption] The sandbox egress-guarded runs (E-4..E-6) are representative of how the product will run. This holds while the product stays stdlib-only and loopback-only (A-10-03). Confirm: Engagement lead (Dinesh Naik), Stage 27.
- A-19-02 [Assumption] The ADR-002 deny-list is heuristic. It covers all AI packages likely to be introduced. Maintenance happens through reviewed PRs (`hub/guards/no_ai.py`). Confirm: Stage 24.

## Unknowns

- U-19-01 [Unknown] Whether a real corpus would defeat keyword search (U-10-04 / RQ-1). This is resolved only through RQ-1..RQ-3.
- U-19-02 [Unknown] The RQ-1 thresholds (question-set size, recall). These are proposals until Dinesh sets them (Stage 8 DN-7, still open).

## Unresolved Issues

- UI-19-01 No-AI gates run only manually, with no CI enforcement (RTD-14 / RG-05). Owner: orchestrator. Resolving stage: 27. This does not block the skip.
- UI-19-02 DN-7 (RQ-1 thresholds) is open. Owner: Engagement lead (Dinesh Naik). It is needed only if the triggers are to be made operational.

## Residual Risks

- RR-19-01 False negative on AI: real documents may defeat keyword search (Stage 8 residual risk). Mitigation: the RQ-1..RQ-3 triggers, with the deterministic baseline already built so that it can be measured.
- RR-19-02 Silent reintroduction: a transitive or renamed AI package could slip past the heuristic deny-list. Mitigations: the egress guard (no outbound network at all), the `model_calls_total` / G5 tripwire, and Stage 32 monitoring. The residual risk stays elevated until CI enforces the gates (UI-19-01).
- RR-19-03 Single-person authorship and approval of the No-AI conclusion on synthetic data (Stage 8 CD-7).

## Change History

| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-20 | claude-fde-agent | Initial record: Stage 19 NOT APPLICABLE under the prompt's conditional clause (OD-08). No prompt, retrieval or model artifacts produced. |
