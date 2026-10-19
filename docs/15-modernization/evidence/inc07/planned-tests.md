# INC-07 planned tests (docs/14-transformation/evidence/increment-test-map.csv, increment = INC-07)
Verified Fact: the map lists **39** planned INC-07 tests: TST-RUN-01, 02, 03, 05..15 (14), TST-MET-01, 03..11, 13..18 (16), TST-OBS-01..09 (9). All 39 are implemented and pass (modules `test_tst_run_01_15_runs.py`, `test_tst_met_01_18_metrics.py`, `test_tst_obs_01_09_observability.py`).

Not in INC-07 per the map: TST-RUN-04, TST-MET-02, TST-MET-12, TST-MET-21 (INC-08, need the HTTP / UI surface); TST-MET-19, TST-MET-20 (INC-09, R2). Service-level equivalents of four of them run as supplementary tests S02, S06 and S07 (they do not replace the INC-08 tests).

Class B tests (OD-S12-10 schedule default, OD-S12-12 runtime floor) are tested in both modes: TST-RUN-01/02/03 (flag on and off, holder, non-holder, service actor, empty holder list) and TST-OBS-07 (floor 3.10 accepted, floor 3.12 refused on this 3.10 device, FTS5 present and absent).
