# INC-09 planned tests (20) - mapping and result
Source: `docs/14-transformation/evidence/increment-test-map.csv` rows with `increment = INC-09` (20 rows; evidence class A = 17, C = 3; release R2; assignment rule 'R2-only requirement'). Result = final sandbox run `f9` on code commit `d3992d4` (group `-k I9_ -k INC09_S`: 33 ok) and again under the egress guard (`fe9`, E09EGRESS ok). Synthetic, unvalidated. Verified Fact unless marked.

| Planned ID | AC | Class | Test method | Module | Result |
|---|---|---|---|---|---|
| TST-ID-13 | AC-ID-13 | A | test_I9_ID_13_same_linked_set_from_every_member | test_inc09_reports_planned | PASS (3 from every member; 4 with LT-03, DEV-92) |
| TST-ID-14 | AC-ID-14 | A | test_I9_ID_14_size_cap_is_flagged_never_silent | test_inc09_reports_planned | PASS |
| TST-ID-15 | AC-ID-15 | A | test_I9_ID_15_consistency_rule_raises_one_finding_and_changes_nothing | test_inc09_reports_planned | PASS |
| TST-ID-16 | AC-ID-16 | A | test_I9_ID_16_no_adopted_policy_means_no_findings | test_inc09_reports_planned | PASS |
| TST-ID-17 | AC-ID-17 | A | test_I9_ID_17_restricted_documents_are_denied_and_not_counted | test_inc09_reports_planned | PASS |
| TST-INT-28 | AC-INT-28 | A | test_I9_INT_28_delay_report_lists_items_per_source | test_inc09_reports_planned | PASS |
| TST-MET-19 | AC-MET-19 | A | test_I9_MET_19_unmatched_rate_and_delay_per_source | test_inc09_reports_planned | PASS |
| TST-MET-20 | AC-MET-20 | A | test_I9_MET_20_case_cost_is_not_available | test_inc09_reports_planned | PASS |
| TST-NFR-03 | AC-NFR-03 | C | test_I9_NFR_03_share_within_four_hours | test_inc09_reports_planned | PASS (66.7%; target is an Assumption) |
| TST-NFR-04 | AC-NFR-04 | C | test_I9_NFR_04_source_older_than_24_hours_is_listed | test_inc09_reports_planned | PASS (age 25.000 h) |
| TST-NFR-12 | AC-NFR-12 | A | test_I9_NFR_12_every_field_class_has_an_access_fixture | test_inc09_search_planned | PASS (C1, C2, C3 = 100%) |
| TST-POL-24 | AC-POL-24 | A | test_I9_POL_24_divergence_report_over_the_shipped_cases | test_inc09_reports_planned | PASS (3 of 125 divergent) |
| TST-REV-09 | AC-REV-09 | A | test_I9_REV_09_ref_filter_returns_the_case_documents | test_inc09_search_planned | PASS (30 referencing documents) |
| TST-REV-11 | AC-REV-11 | A | test_I9_REV_11_operator_and_sql_text_is_literal | test_inc09_search_planned | PASS |
| TST-REV-12 | AC-REV-12 | A | test_I9_REV_12_restricted_rows_are_neither_returned_nor_counted | test_inc09_search_planned | PASS |
| TST-REV-13 | AC-REV-13 | A | test_I9_REV_13_trigram_substring_and_diacritics | test_inc09_search_planned | PASS |
| TST-REV-15 | AC-REV-15 | C | test_I9_REV_15_labelled_recall_is_a_reported_baseline | test_inc09_search_planned | PASS (baseline 0.3776, no threshold) |
| TST-REV-18 | AC-REV-18 | A | test_I9_REV_18_template_drafts_are_never_prefilled | test_inc09_search_planned | PASS |
| TST-SEC-19 | AC-SEC-19 | A | test_I9_SEC_19_field_class_handling_by_role | test_inc09_search_planned | PASS (finance masking at the protection layer, DEV-91) |
| TST-SEC-20 | AC-SEC-20 | A | test_I9_SEC_20_c3_read_needs_a_reason_and_is_audited | test_inc09_search_planned | PASS |

Every search test runs on both engines (FTS5 and fallback) and asserts identical results. Supplementary (not planned ids): `test_inc09_supplementary.py` S01..S13 (engine parity, REV-10/14/16 on FTS5, engine selection, drop-index rollback, M007, corpus pin and sandbox guard, CLIs, static guards, R2WebApp delegation, shipped defaults, archive parsing, text rules vs bm25(), M007 rollback rehearsal); `test_inc09_egress_guard.py` (E09EGRESS).
