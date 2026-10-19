# INC-06 shipped-source profile (evidence)
Verified Fact: output of TST-HUB-INC06-S11 in a sandbox copy (OD-03/03a); legacy DB sha256 c254649f57e2f05a0b54229923597a5a82a37633d455270b9ee40577071d70aa (unchanged). Synthetic, unvalidated fixtures derived from the 125-case seed-4100 baseline (OD-09).

Partner feed, default binding record_only (8,567 rows): EXCEPTION 8,109 (UNMATCHED_REF 7,903 reason rows), NOOP_DUPLICATE 67, QUARANTINED 223 (UNSUPPORTED_REVISION), VALIDATED 165, VALIDATED_WITH_FLAGS 3 (NEGATIVE_VALUE). 168 items linked to a baseline case; revised conflicts 0; contract check fail on all 8,567; queue snapshot 8,500 items (NOOP excluded); outcomes_digest 4a50d7151ced475024419ffe4e867e3da2fc1605f89e7c93f5a0c65604f0b98a.
Enforce binding (TST-INT-13): 8,500 QUARANTINED (CONTRACT_VIOLATION) + 67 NOOP_DUPLICATE.
source_message: 15 VALIDATED, contract pass 15. gateway_inbox: 1 VALIDATED, contract fail 1 (enforce: quarantined, TST-INT-14).
Vendor tiny CSV (2,400 rows): UNPARSABLE_AMOUNT 10, NEGATIVE_VALUE 11, IDENTIFIER_PATTERN 2,400, UNKNOWN_CURRENCY 382 (BRL).
