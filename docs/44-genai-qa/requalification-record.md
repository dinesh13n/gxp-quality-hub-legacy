# Re-qualification record - T3 advisory document Q&A (OD-40)

Date: 2026-10-26. Owner of decision: Dinesh Naik. Prior decision: OD-08 (no AI; docs/08-ai-qualification/). This record re-qualifies ONLY tier T3 (advisory Q&A over existing hub search).

## Authorisation (RQ triggers met)
Re-qualification triggers RQ-1..RQ-3 (docs/final-prd/final-ai-agent-baseline.md AI-4) require an explicit owner decision. On 2026-10-26 Dinesh answered: use case = document Q&A over existing search; posture = off by default, advisory only; connection = config placeholders only, local fake, no real key/endpoint/call.

## Scope limits (what this does NOT change)
- Default state is unchanged: `ai.enabled=false`; 0 model calls, 0 egress attempts (Stage 32 tripwires still 0 when off).
- Turning it on needs `approval_refs["ai.enabled"]` (decision flag) and the four env vars.
- Synthetic data only: a guard refuses a corpus whose origin is not synthetic/shipped/fixture.
- Output is advisory and is NOT a GxP record. It writes only to the audit log; no case, record or approval is modified.

## Risk assessment
| Risk | Control | Residual |
|---|---|---|
| Hallucination | Answer built only from retrieved passages; fixed system rules; grounding check (every sentence cites [S#], numbers must appear in the cited source, lexical overlap >= 0.6, no unknown URLs); INSUFFICIENT_CONTEXT allowed; label "AI-generated, advisory, not a GxP record, human verification required" | Grounding is lexical; it does not prove truth. Human verification required |
| Prompt injection | Sanitise passages (control/bidi chars, HTML escape), instruction-pattern filter (policy exclude or flag), delimiting, no tools and no write path, grounding rejects obeying output | Pattern list catches about 12 of 19 test strings; structural controls are primary |
| Data leakage | Only caller-visible rows; restricted (C3) rows dropped and counted; synthetic-only guard; only a validated Azure host (https, Azure suffixes, or loopback); no redirects, no env proxy; key never logged | Real-data use not approved (OPEN) |
| GxP record status | Labelled advisory; audit only; no record created | Procedure/SOP wording is Dinesh-owned (OPEN) |
| 21 CFR Part 11 / EU Annex 11 | Considerations only, no compliance claim: attributable audit entries (hash-chained), access via principal, no e-signature use. Computerised-system validation of the model is NOT done | Validation OPEN |
| Cost | daily_token_budget 20000, max_request_tokens 3000, max output 300; computed from the audit log | Best-effort for one operator |
| Latency / availability | 20 s timeout, one attempt, no retry; provider errors map to exit 41 and are audited | None: core hub works without the model |
| Secret exposure | Key only from env; never in config, repo, log, audit or output; redacted from provider messages | Operator hygiene of the local environment |

## Conclusion
Acceptable as an OFF-by-default, synthetic-only, advisory capability, evidenced against a local fake only. Not accepted for real data or production use.
