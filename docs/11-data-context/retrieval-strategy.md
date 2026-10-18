---
stage: "11 — Data, Knowledge & Context Strategy"
artifact: "retrieval-strategy.md"
version: "v0.1"
date: "2026-10-18"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/10-architecture/adrs/ADR-012-reviewer-search.md", "docs/10-architecture/adrs/ADR-002-no-ai-boundary-enforcement.md", "docs/09-initial-prd/functional-requirements.md FR-REV-03, FR-INT-07, FR-GATE-02", "docs/08-ai-qualification/qualification-decision.md (T3, RQ-1..RQ-3)", "data/documents/source_documents.jsonl", "data/archive_documents/", "sandbox test $HOME/fde_sbx/s11 (in-memory SQLite, outside repo)", ".fde/orchestrator-decisions.md OD-08"]
supersedes: "none"
---
## Summary

**Label: synthetic repository, unvalidated against any organisation.** Per OD-08 the product is No-AI, so this is a **deterministic keyword and field retrieval design (touchpoint T3)** over documents plus structured "evidence pack" assembly for reviewers. There are **no embeddings, no vector store, no LLM reranker, no generated answers, no RAG** (ADR-012 option D rejected; Stage 19 not applicable). Results are always the original documents (with provenance) — never synthesised text. The ADR-012 Unknown ("is FTS5 available?") is **resolved for the inspection device**: stdlib Python 3.10.12 with SQLite 3.37.2 has `ENABLE_FTS5`, `unicode61` and `trigram` tokenizers, `snippet()` and `bm25()` (in-memory test in `$HOME/fde_sbx/s11`, nothing written to the repo). Availability on any target runtime remains Unknown and keeps the ADR-012 fallback (LIKE/inverted index in Python).

## Findings

### R1. Corpus facts that shape the design [Verified Fact]

| Fact | Value | Design consequence |
|---|---|---|
| Documents | 1,200 JSONL (`body` max 99 characters) + 420 archive files (269-478 bytes, avg 339) | Whole-document indexing; **no chunking** needed |
| Languages | locales es-MX 267, de-DE 230, en-IN 222, ja-JP 242, en-US 239; archive en/de/hi/ja/pt/es | Unicode-aware tokenizer; Japanese needs trigram or n-gram (no word boundaries) |
| Bodies | only 3 distinct base sentences (387/394/397) + 22 with an injection line (9/5/8) | Ranking quality cannot be assessed on this corpus (see `synthetic-data-strategy.md`) |
| Versions / dates | revA/revB/v1/v2; effective 2023-01-01..2025-09-26 | Filters by `version`, `effective_at` |
| `reference` linkage | 30 of 1,200 resolve to a case | Reference search will mostly return "no case match" |
| OCR | `ocr_confidence` NULL 900; 38 < 0.70 | Show quality flag; do not hide low-confidence hits |
| Access | `access_level` 4 values, restricted 328 | Filter before ranking |

### R2. Pipeline (ingest -> normalise -> index -> query -> rank -> present)

| Step | Design | Rationale / evidence |
|---|---|---|
| RS-1 Ingest | Read-only adapters load `source_documents.jsonl`, archive `.eml`/`.html` (decode quoted-printable; strip HTML tags/scripts to text), optionally lake documents; each becomes an immutable `(doc_id, version)` row with `source_hash`. | FR-INT-01; DC-06/07 |
| RS-2 Normalise | Unicode NFC; lowercase via tokenizer; preserve original text; store both. Untrusted flag set. | DQ-22; ADR-002 |
| RS-3 Chunk | **None** for current corpus (bodies <= 99 chars; archive <= 478 bytes). Rule for future: if a document exceeds a configured size, split on structural boundaries (paragraph/heading) with `parent_doc_id`, `offset_start/end`, never overlapping windows, so citations always point to exact character ranges. | R1 facts; PRD forbids generation |
| RS-4 Index | SQLite FTS5 table `doc_index` in `hub.sqlite3`, columns: `body` (indexed) + UNINDEXED `doc_id, reference, locale, version, effective_at, access_level, source, source_hash`. Tokenizers: `unicode61 remove_diacritics 2` default; second `trigram` table for ja-JP and substring/ID search. | ADR-012 option B; sandbox test |
| RS-5 Query | Query text is parsed by a **fixed grammar** (terms, quoted phrases, field filters `ref:`, `doc:`, `locale:`, `version:`, `from:/to:` on effective date). User input is never passed raw to `MATCH`; terms are quoted/escaped to prevent FTS operator injection. Parameterised SQL only. | FR-REV-03; PNFR-13 |
| RS-6 Authorise | Apply `access_level`/`tenant`/role filter inside the query (`WHERE`) before ranking; totals count only permitted rows. | metadata-model MA-3 |
| RS-7 Rank | `bm25()` score, tie-break by `effective_at` desc then `doc_id` (deterministic). **No reranker.** A "latest effective version" toggle collapses versions per `reference`; default shows all versions with their dates. | PNFR-17 determinism |
| RS-8 Present | Each hit: document text (escaped), `doc_id`, version, effective date, source, locale, access label, `ocr_confidence` flag, hash prefix, and the match highlight via `snippet()` with output escaped. Marked "untrusted source text". Pack link to crosswalk case if one exists, else "no linked case". | `provenance-policy.md` |
| RS-9 Evidence pack (FR-GATE-02) | For one case: read-only assembly from tables by crosswalk (events, linked objects, documents, rule trace, open findings). Pure joins; no summarisation. Missing links are listed as "none found". | FR-GATE-02, FR-ID-04 |

### R3. What is explicitly excluded

- No semantic/vector search, no query rewriting, no synonym learning, no LLM summaries, no auto-generated citations, no "answer" box (OD-08, ADR-012 D, FR-REV-03 "No generative answer").
- No retrieval that crosses tenants or access levels; no fuzzy identity matching (FR-ID-02).
- Re-qualification only through RQ-1..RQ-3 and a new Dinesh decision (ADR-002).

### R4. Findings

| ID | Finding | Evidence | Impact | Risk | Conf. | Class |
|---|---|---|---|---|---|---|
| RT-01 | FTS5 is available in the device stdlib SQLite (3.37.2) incl. `trigram`; match, `snippet` and `bm25` returned expected rows on a 2-row in-memory test. | sandbox test (outside repo) | Removes the main ADR-012 technical Unknown for dev; no dependency needed | Low | High (device) / Low (target runtime) | [VF] |
| RT-02 | Planted injection lines are matched like any text (`"ignore previous"` returns the row) - they are data and remain findable; they must not alter ranking inputs other than text relevance, and the UI must label them. | sandbox test | Safe if output escaped and no consumer interprets text | Medium | High | [VF] |
| RT-03 | Corpus too homogeneous to evaluate retrieval quality (3 base sentences); 97.5% (1,170 of 1,200) of document references are orphan to cases. | queries this stage | Any "search works" claim would be unearned; need synthetic query/ground-truth set | Medium | High | [VF] |
| RT-04 | RQ-1 baseline (reviewer time-to-find) is unmeasurable with no real reviewers and no usage data. | OD-04; U-S01 | RQ triggers cannot be evaluated; AI remains out | Low | High | [VF]/[UNK] |
| RT-05 | FTS5 index content duplicates restricted text; the index file itself is C3 data and inherits backup/classification rules. | metadata-model | Index must be backed up, access-controlled and rebuilt from source | Medium | High | [INF] |
| RT-06 | Query-time latency target is open (OPD-14); expected well within range at 1,620 docs, but unmeasured. | PNFR-06 | Measure first | Low | Medium | [INF] |

### R5. Acceptance tests proposed (Stage 14/17 to own)

- AT-1 Query for a known phrase returns exactly the expected doc_ids (golden set built from synthetic data).
- AT-2 FTS operator characters (`" * ( ) NEAR AND OR -`) in input return a safe parse or a clear error, never a crash or an unintended query.
- AT-3 A user without `restricted` rights sees 0 restricted hits and an unchanged "total" semantics.
- AT-4 Planted-string fixture: injection documents are returned as plain escaped text; decision fields unchanged.
- AT-5 Rebuild of `doc_index` from sources reproduces identical hits/order (determinism).
- AT-6 ja-JP substring query works via trigram table.

## Evidence References

ADR-012; `source_documents.jsonl` profile (body max 99; 3 base sentences); archive file sizes (min 269, max 478, avg 339 bytes); sandbox: `sqlite3.sqlite_version` 3.37.2, compile options `ENABLE_FTS5`, `create virtual table ... tokenize='trigram'` ok.

## Assumptions

- A-11-11: Tokenizer choices (unicode61 + trigram) suffice for six languages; Hindi tokenisation quality untested. Confirm: Engagement lead (Dinesh Naik), Stage 14.
- A-11-12: "Latest effective version" semantics are acceptable; no real reviewers have validated them.

## Unknowns

- U-11-18 FTS5 on the target runtime (Dockerfile python:3.12-slim has not been run; Docker not installed). U-11-19 Whether reviewers want document Q&A (OPD-12/U-S01).

## Unresolved Issues

- Ground-truth query set does not exist; to be created in Stage 14 using synthetic strategy.

## Residual Risks

- DR-04, DR-14, DR-15.

## Change History

| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-18 | claude-fde-agent | Initial deterministic retrieval design. |
