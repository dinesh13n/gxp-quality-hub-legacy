# INC-09 R2 figures (printed by the tests, final run `f9`)
All figures are sandbox measurements on the hash-gated FX-BASE125 copy or on labelled synthetic fixtures - **synthetic, unvalidated**; none is a validated target.

| Test | Figure | Note |
|---|---|---|
| TST-REV-09 | 30 documents reference a case (of 1,200); C00000038 -> DOC-00000415, DOC-00001089 | equal to the LT-05 crosswalk LINKED count |
| TST-REV-15 | top-5 recall 0.3776 over 61 generated labelled queries, identical on fts5 and fallback | baseline only; label set generated from metadata (OPD-12); ranking quality cannot be assessed (3 base sentences) |
| TST-POL-24 | 3 of 125 shipped cases divergent on `amount_over_limit`; null outputs: as-found-batch 125, as-found-js 0, as-found-python 0 | reported, not resolved (A-12-F03-1) |
| TST-NFR-03 | share within 4 h = 66.7% (2 of 3; 1 future excluded) | 4 h is an Assumption (PNFR-03) |
| TST-NFR-04 | partner_feed newest accepted item 25.000 h > 24 h -> listed | 'risk signal' undefined (Unknown) |
| TST-MET-19 | partner_feed unmatched rate 0.2500, p50 delay 0.000 h; source_message 0.0000, 0.000 h | synthetic runs; delays are µs on the test clock |
| TST-NFR-12 | field classes covered C1, C2, C3 of C1, C2, C3 (100%) | C0 has no data in the estate |
