---
stage: "8 — AI-vs-No-AI Qualification"
artifact: "intervention-options.md"
version: "v0.1"
date: "2026-10-17"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/06-root-cause/confirmed-root-causes.md", "docs/06-root-cause/root-cause-readiness.md", "docs/03-problem-value/business-requirements.md", "docs/03-problem-value/nfrs.md", "docs/07-repo-assessment/repo-transformation-readiness.md", "docs/00-preflight/ai-economics/solution-scenarios.md", "docs/00-preflight/ai-economics/cost-scenarios.md", "docs/00-preflight/operating-contract/provisional-human-approval-rules.md", "app/legacy_logic.py", "app/partner_feeds.py", ".fde/orchestrator-decisions.md"]
supersedes: "none"
---
## Summary

Ten intervention options (O0-O9) are listed from "do nothing" through process redesign, deterministic software, workflow automation, analytics, rules/search/templates, classical ML, single-pass GenAI/RAG and read-only agentic AI. Each is stated without presupposing a winner, mapped to the Stage 6 root causes RC-1..RC-8 it could address, and given a disposition. **Status: all of this is a recommendation pending approval by Dinesh Naik (sole approver); nothing here is an approval.** Label for all content: synthetic repository, unvalidated against any organisation (Stage 6 scope statement, `confirmed-root-causes.md`).

The options are not mutually exclusive. O1-O5 compose into one non-AI package (P-NOAI). O6-O8 are the only options containing a statistical or generative component; none of them is mapped to any confirmed root cause in section F-08-OPT-2.

## Findings

### Options register

| ID | Option | What it is (no technology bias) | Minimum capability level | Authority needed to adopt |
|---|---|---|---|---|
| O0 | Status quo | Leave system as found (manual operations, three rule copies, GET-only API) | none | none |
| O1 | Process redesign and policy change | Owner decision (or recorded "accepted open") on the definition of closed/resolved/approved and the speed-vs-evidence trade-off; name the owner of the decision-of-record; decide where batch disposition lives; manual run-cadence and run-log discipline for reconcile | L0 (people/policy) | Dinesh Naik for any decision (RC-3 is a decision gap, `confirmed-root-causes.md` CR-D); HAR-11 |
| O2 | Deterministic software core | Append-only decision/event write path with actor, time, basis and a human approval gate (RC-1, RC-2); a single table-driven rule service replacing the three copies (RC-4); shared identity/crosswalk (RC-7); quarantine-and-compare intake instead of destructive overwrite (RC-6) | L1 (deterministic code) | HAR-06 for any rule change; HAR-12 guard; BUILD stages only |
| O3 | Workflow automation | Scheduled reconcile with run records and checkpoints, no capacity cap hidden in a default argument (RC-5) | L1 | HAR-07 if CI/config touched |
| O4 | Analytics / reporting | One shared metric definition per figure, definition tag on every report, fix of the SQL fan-out join (RC-8, BR-01, BR-10) | L1 | RC-3 definition decision first |
| O5 | Rules, search and templates for the candidate touchpoints | T1 rule-trace explanation from fields; T2 rule-based classification with reason codes; T3 keyword/field search (SQLite FTS5 or equivalent); T4 structured/templated form | L2 (rules/lookup) | none beyond BUILD gating |
| O6 | Classical ML | e.g. gradient-boosted classifier for feed exceptions or anomaly scoring (0C scenario S2 ML portion) | L3 | HAR-10 |
| O7 | GenAI single-pass / RAG | LLM summarisation, document Q&A, narrative drafting with human review of every output (0C scenario S3) | L4 | HAR-10, HAR-09 (egress), HAR-08 (dependencies) |
| O8 | Agentic AI (read-only tools) | Tool-using loop for cross-store investigation (0C scenario S4, touchpoint T5) | L5 | HAR-10, HAR-09, plus Stage 22 justification |
| O9 | Replace with a commercial QMS | Buy and migrate instead of modernising | n/a | Not evaluated, see below |

### F-08-OPT-1 Option dispositions

| ID | Disposition | Reason (details in `ai-vs-no-ai-matrix.md`) | Confidence |
|---|---|---|---|
| O0 | **Rejected as the end state; retained as the baseline for before/after** | Leaves 8 confirmed structural root causes (RC-1..RC-8) unaddressed; keeps unattributable decisions (NFR-09 gap) | High |
| O1 | **Selected (recommended), mandatory precondition** | Only way to resolve RC-3 and to place RC-1's external gate; engineering must not silently choose a side (`root-cause-readiness.md` RR-C) | High |
| O2 | **Selected (recommended), the core** | Addresses RC-1, RC-2, RC-4, RC-6, RC-7 directly; deterministic, explainable, testable against the Stage 7 goldens | High (fit) / Medium (effort, unquantified) |
| O3 | **Selected (recommended)** | Addresses RC-5; low risk | High |
| O4 | **Selected (recommended)** | Addresses RC-8 (19.3% fan-out inflation re-executed read-only in Stage 6, `validation-plan.md` V-08) | High |
| O5 | **Selected (recommended) for T1-T4 at the minimum level** | Meets the evidenced content: feed fields are fixed-key and enumerated, documents are short stubs (see F-08-OPT-3) | Medium (synthetic content only) |
| O6 | **Rejected** | No root cause is statistical; no labelled data; synthetic labels would not transfer (0C `solution-scenarios.md` S2 caveat). Not mapped to any RC | High |
| O7 | **Rejected for this engagement scope; conditional re-qualification possible (triggers RQ-1..RQ-4 in `qualification-decision.md`)** | No evidenced language/reasoning/generation need that O5 cannot meet; injection exposure (NFR-13); every output needs human review so it adds oversight labour; unknowns (U-V02 real document size and language) could change this | Medium |
| O8 | **Rejected** | T5's underlying gap is the missing shared key (RC-7). An agent without keys would guess links; Stage 6 guardrail "Must not fabricate links for orphan feeds". Highest injection exposure (0C), quadratic token growth | High |
| O9 | **Not evaluated (Unknown)** | No evidence in repo or stakeholder record on buy-vs-build, licensing, or validation status of any product; recorded so it is not silently dropped. Owner: Engagement lead (Dinesh Naik); resolving stage 9/10 | n/a |

### F-08-OPT-2 Root-cause coverage by option (F = addresses directly, P = partial/enabling, - = does not address)

| RC | O0 | O1 | O2 | O3 | O4 | O5 | O6 | O7 | O8 |
|---|---|---|---|---|---|---|---|---|---|
| RC-1 no decision record/step | - | P (place the gate) | F (write path + gate; **never** simulates disposition, HAR-12) | - | - | - | - | - | - |
| RC-2 mutable state | - | - | F | - | - | - | - | - | - |
| RC-3 no owned definition (decision gap) | - | F (only option that resolves it) | P (carries a definition tag, does not choose) | - | P (shows tag) | - | - | - | - |
| RC-4 three divergent rules | - | P (decide authoritative rule) | F (single rule table once authority known) | - | - | P (T1 explains the one rule) | - | - | - |
| RC-5 manual capped runs | - | P (cadence) | - | F | - | - | - | - | - |
| RC-6 destructive intake | - | - | F | P | - | P (T2 reason codes) | - | - | - |
| RC-7 no shared identity | - | - | F | - | - | - | - | - | - |
| RC-8 independent totals | - | P (definition) | - | - | F | - | - | - | - |

[Inference] No AI option (O6-O8) is a "F" or "P" for any confirmed root cause. Reasoning: Stage 6 states RC-1..RC-8 as absences or defects of design (no write path, mutable snapshot, no owner, three unsynchronised copies, no scheduler, destructive overwrite, no key, independent computation). Each is closed by creating, constraining or deciding something; none by interpreting uncertain or unstructured input. Confidence High for the mapping; the scope caveat is that this holds for the repo, not for an organisation.

### F-08-OPT-3 Candidate touchpoints T1-T5 (from 0C `solution-scenarios.md`): what the content actually is

| Touchpoint | Content evidence (read-only, 2026-10-17) | Consequence |
|---|---|---|
| T1 triage explanation | `app/legacy_logic.py` is 8 lines: `priority()` and `manual_review_required()` over status/severity/amount only. [Verified Fact] | The full "reason" for a priority is a few field comparisons. A rule trace is an exact explanation; an LLM paraphrase adds risk of misstatement |
| T2 feed exception classification | `partner_feeds.raw_json` has 11 fixed keys in all 8,567 rows (`business_key` present in 8,357); `notes` exists in all rows but has 6 distinct values; `reconcile()` applies 4 deterministic branches (`app/partner_feeds.py`); `policy_exceptions.explanation` has 5 distinct values in 224 rows. [Verified Fact] | Categorical, enumerable input. Rules fully cover current content. 86 rows carry an injected "SYSTEM NOTE" in `notes` (0C DF-08) |
| T3 document Q&A | `data/documents/source_documents.jsonl`: 1,200 docs, 3 distinct first body lines; `data/archive_documents/`: 421 files averaging 339 bytes; `locale` label takes 5 values but the body text read is English; `ocr_confidence` is null for 900 and minimum 0.653 among the rest. [Verified Fact] | Content is too small and repetitive to show any retrieval failure of keyword search. Real corpus unknown (U-V02) |
| T4 deviation/CAPA narrative | `deviations.root_cause` is NULL for 21 of 42 and otherwise 3 distinct phrases; `capa_actions` has owner/due/state only; WF-04 is data-only (no transition logic). [Verified Fact] | No narrative workflow exists to augment and no business requirement (BR-01..BR-13) asks for narrative generation |
| T5 cross-store investigation | `cases` has no batch/deviation/CAPA/feed key; `partner_feeds.ref_id` has no FK (RC-7). [Verified Fact] | The blocker is a missing key, not missing reasoning |

## Evidence References

`docs/06-root-cause/confirmed-root-causes.md` CR-A, CR-D; `docs/03-problem-value/business-requirements.md` BR-01..BR-13; `docs/00-preflight/ai-economics/solution-scenarios.md`; `docs/00-preflight/operating-contract/provisional-human-approval-rules.md` HAR-06..HAR-12; content measurements by read-only SQLite (`file:data/legacy.sqlite3?mode=ro&immutable=1`) and read-only file reads, listed in `qualification-decision.md` Evidence Appendix.

## Assumptions

- A-08-01 Touchpoints T1-T5 are the only AI-shaped candidates; they are hypothetical (0C A-S01), nobody has requested them. Confirm: Engagement lead (Dinesh Naik).
- A-08-02 Options are scored for the repository as shipped (OD-02 baseline: 125-case DB) and its synthetic content; real content may differ.

## Unknowns

- U-08-01 Whether buying a commercial QMS (O9) is in scope. Owner: Engagement lead (Dinesh Naik); Stage 9/10.
- U-08-02 Where the real decision-of-record and closure evidence live (U-05-02, C-3). Affects O1/O2 scope.

## Unresolved Issues

- RC-3 decision (C-2 in `root-cause-readiness.md`) and R-4/R-5 (dataset, authority for rule conflicts) are still open; O2's rule-table part and O4 cannot be finalised until they are decided or recorded as accepted-open.

## Residual Risks

- Anchoring risk in both directions: the 0C touchpoints were AI-shaped by construction; the rejection here rests on synthetic content that is deliberately simple. Real data could change T3/T4 (see re-qualification triggers).
- O9 unexamined.

## Change History

| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-17 | claude-fde-agent | Initial options register. |
