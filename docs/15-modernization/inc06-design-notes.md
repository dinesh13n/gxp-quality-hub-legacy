# INC-06 design notes (data intake)
Branch `stage-15-inc06-intake`. Labels: Verified Fact / Inference / Assumption / Unknown. Test data synthetic, unvalidated. No AI/model call, no network egress beyond loopback, `zone_h.holders` empty.

## Decisions
- D-01 (Verified Fact) Append-only `raw_intake` plus append-only `intake_outcome`; current outcome = highest `outcome_seq`; view `intake_current` excludes NOOP_DUPLICATE. Raw payloads are never changed (E-INT-RAW-IMMUTABLE triggers; BEFORE DELETE triggers on all four tables).
- D-02 (Verified Fact) M004 lives in `hub/intake/migrations/` and is applied by `hub.intake.schema` with its own table `intake_schema_migrations` (INC-04/05 precedent), after a backup labelled `pre-intake-M004-`; needs M001, M002, M003.
- D-03 (Verified Fact, OD-18) identity key = sha256 of canonical [source, partner, record_kind, ref_id, normalised source_ts]; incomplete identity falls back to an `unkeyed` hash and never merges. content_hash = sha256 of canonical {schema_rev, payload}.
- D-04 (Verified Fact) Stage order per SBR-INT-04: store raw, identity/hash compare (NOOP_DUPLICATE / REVISED_CONFLICT), validate L1/L2/L3, classify (pure, fixed precedence SBR-INT-03, 15 codes), crosswalk match, outcome. One transaction and one INTAKE_RUN audit record (with outcomes_digest) per run; an audit failure rolls the run back.
- D-05 (Verified Fact, OD-10d) Contract bindings are per source, default record_only; changes are CONTRACT_BINDING_CHANGED rows in `policy_events` written only through the shared Zone H gate (ZH-10). With empty holders nobody can switch to enforce.
- D-06 (Verified Fact) Free text is stored via `untrusted_text()`, returned as {text, trust: untrusted}, escaped for display; runtime guard plus static AST lint (U1/U2/U3) keep it out of decision parameters. The lint is heuristic (A-15-06-1).
- D-07 (Verified Fact) Matching uses the crosswalk's exact LT-04 rules inside the run's own transaction (`audit.change` cannot nest); no fuzzy matching.
- D-08 (Verified Fact) HTTP client only under `hub/adapters/` (ADR-002 R2), loopback only, no proxy, no redirects, bounded retries with exponential back-off for 5xx/429/connection errors; 4xx not retried. It sleeps via `threading.Event().wait` because adapters may not import `time` (TST-CO-13 b).
- D-09 (Verified Fact) Source naming: `source_message` stands for legacy `external-feed`. Documents (22 bodies) are not an intake source here (INC-07).
- D-10 (Verified Fact) Exit code 28 for E-INT-* errors (INC-06 choice).
- D-14 (Verified Fact) TST-CO-12 is frozen: INC-06 modules skip when `HUB_EGRESS_INNER` is set; `test_inc06_egress_guard.py` (E06EGRESS) runs them under the egress guard (0 attempts, model_calls_total 0).

## Added files
`hub/intake/*` (schema, canon, reasons, contracts, profiles, validate, service, untrusted_lint, replay, cli), `hub/adapters/intake_sources.py`, `hub/adapters/gateway_client.py`, `tests/hub/_inc06.py` and five test modules, this file, `rollback-rehearsal-inc06.md`, `evidence/inc06/`.
