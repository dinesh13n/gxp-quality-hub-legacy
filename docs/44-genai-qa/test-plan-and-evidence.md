# Test plan and evidence

All evidence is from a LOCAL FAKE Azure OpenAI server on loopback. No real Azure call was made or is claimed.

## New tests (group S44, 26 tests; group E44, 1 test)
- core (C01-C14): success with citations, no-retrieval refusal (no model call), injection text (exclude and flag policies), uncited / invented / wrong-number / obeying answers rejected, INSUFFICIENT_CONTEXT, restricted rows excluded, budget cap, rate limit, key never in audit/logs/output, usage recorded.
- CLI (L01-L06): disabled-by-default, missing env, kill switch, success, provider errors and exit codes.
- boundary (B01-B06): endpoint validation, no redirects, no env proxy, adapter is the only urllib user, key hidden in repr, API errors/timeouts/429/5xx/bad JSON/oversize.
- E44EGRESS: whole S44 run inside the runtime egress guard; only the permitted loopback fake is reachable; inner run asserts ok == 26.
Fake modes: ok, uncited, invented, number, obey, insufficient, s429, s500, s401, s302, slow, badjson, huge, nousage, content_filter.

## Existing tests updated (listed in tests/hub/non_add_edits.json)
CO-05 c (accepts dated_doc_notes), CO-12 (model-call site is only azure_openai.py), stg26 D01, stg27 F05, stg28 A02, stg30/31 D01.

## Results
Run 2026-10-26 on sandbox copies (never the working-tree data/), one group per run, checksum of the backup manifest rc 0 pre and post each run.

| Group | Result |
|---|---|
| S44 | 26 ok |
| E44 | 1 ok |
| B | 41 ok, 1 skipped (expected inner-run skip) |
| A | 45 ok |
| S20 | 18 ok |
| S23 | 26 ok |
| S24 | 21 ok |
| S26 | 23 ok |
| S27 | 25 ok (ratchet kept: 0 cycles, grounding.check refactored under complexity 16) |
| S28 | 19 ok |
| S30 | 19 ok |
| S31 | 19 ok |

Ripple fixes found by these runs: S27 R01 (error registry additions), S27 S01 (adapter metrics import made function-level; grounding helper split), S28 A02 (adapter env names read via ENV_NAMES). The full characterization harness was not run (not required).

## Evidence samples
evidence/c01-success.json and evidence/l04-cli-success.json (fake only, synthetic data).

## Gate
CONDITIONAL PASS: code and tests green against the fake; no real-deployment test, no validation, no human approvals; release not executed.
