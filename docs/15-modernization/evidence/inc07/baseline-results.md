# INC-07 evidence: metric results on the shipped baseline (FX-BASE125, hash-gated snapshot)
Labels: Verified Fact (asserted by the named tests in a sandbox copy). All figures are 'synthetic, unvalidated' and carry no verdict: no definition, clock duration or cut-off is adopted.

| Metric | Result | Test | Tag |
|---|---|---|---|
| Month-end total of cases.amount (explicit cut-off after all case dates) | 622826.44, n = 125 (legacy join-inflated 742,956.61 not produced) | TST-MET-09 | Verified Fact |
| Backlog under D-OPS, as_of 2025-12-19 (label CLOSED is the closing state, no CLOSURE policy adopted) | 89 of 125; per-site and age-bucket counts sum to 89 | TST-MET-17 | Verified Fact |
| Time to close, clocks C-OPS and C-EVID | null, reason `no_completed_cycles`, n = 0, open_count 125 | TST-MET-08 | Verified Fact |
| Unresolved-exception rate (D-OPS) | null, reason `no_exception_queue_items` (no intake yet) | TST-OBS-08 | Verified Fact |
| KPI coverage | 5 R1 KPIs each with a value or a stated reason | TST-OBS-08 | Verified Fact |
| Shipped sources through a capped run | partner_feed 8,567 / source_message 15 / gateway 1 / vendor CSV (tiny) 2,400; two runs of cap 200 leave backlog 8,367 then 8,167, no overlap | TST-HUB-INC07-S19 | Verified Fact |
