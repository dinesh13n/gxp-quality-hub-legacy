---
stage: "4 — Capture Before-AI / Before-Intervention KPIs"
artifact: "kpi-baseline-signoff.md"
version: "v0.1"
date: "2026-10-17"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/04-baseline-kpis/kpi-dictionary.md", "docs/04-baseline-kpis/baseline-kpi-sheet.md", "docs/02-stakeholders/operating-contract-confirmations.md", "docs/02-stakeholders/decision-rights-map.md", ".fde/orchestrator-decisions.md"]
supersedes: "none"
---
## Summary

**Freeze status: FROZEN-PROVISIONAL (v0.1). Owner sign-off: NOT GIVEN.** The definitions in `kpi-dictionary.md` (K-01..K-22, including the D-OPS / D-EVID / D-FIN split and the proxies P-01..P-04) are frozen as of this version so Stages 34-36 have a fixed yardstick, but the freeze rests on two unanswered questions: Q-02-04 (baseline dataset; OD-02 PROVISIONAL) and Q-02-05 (working definitions of closed/resolved/48 h clock). No human other than Dinesh Naik exists (OD-04), and he has not signed. This is recorded as a documented blocker to *final* freeze, not a claimed approval.

## Findings

### Frozen items (v0.1)

| Item | Frozen content | Frozen how |
|---|---|---|
| Definitions | Formula, unit, source, population, segmentation of K-01..K-22 | `kpi-dictionary.md` v0.1 |
| Three-definition reporting | Every closed/resolved-dependent KPI reported separately as -OPS, -EVID, -FIN; no primary chosen | SC-01/DR-20 unowned |
| Baseline population | `data/legacy.sqlite3`, sha256 `c254649f57e2f05a0b54229923597a5a82a37633d455270b9ee40577071d70aa`, 125 cases | OD-02 PROVISIONAL |
| Measurement script | `evidence/measure_baseline.py` sha256 `cb062e1bae216db47abd909f8923ee9284fa619f2743ba86ae8d3849d53f60a6`; reference time AS_OF = 2025-12-19T07:11Z | hash |
| Baseline values | `evidence/measure_baseline.output.json` sha256 `31ffa1b2b136de5a0676f612e172d190d4e23730ee1c7e3c7ebf7f41216d61ba` | hash |
| Labelling rule | Any value from this DB carries "measured on synthetic baseline data (method validation only)" (FAIL-05) | rule |
| Targets | None set. Stage 3 relative targets (A-03-13) remain relative until a real baseline exists | rule |

### What would change the freeze (versioned change record required: v0.2+)

| Trigger | Effect on this baseline | Action |
|---|---|---|
| Dinesh overrides OD-02 (e.g. regenerates 6,000 cases, seed 4326 — generation writes `data/`, so sandbox only) | All values in `baseline-kpi-sheet.md` replaced; definitions unchanged; new DB hash recorded | Re-run script in sandbox; v0.2 sheet; keep v0.1 as superseded evidence |
| Dinesh selects one definition of closed/resolved (Q-02-05) | Designates a primary variant among -OPS/-EVID/-FIN; the others stay as secondary; K-04/K-09 formulas unchanged | Change record; no re-measurement of values |
| Dinesh defines D-FIN | K-04-FIN and K-09-FIN gain formulas; values still Unknown until data exists | Change record |
| Dinesh records "accepted open" | Three-way reporting becomes permanent | Change record |
| Real source of closure/evidence timestamps appears | K-04, K-05, K-09-EVID become measurable; proxies retired | Change record + new baseline |
| Dinesh changes owner/role names | Owner column only | Change record |

### Change-control rule (frozen)

No definition, formula, population, AS_OF, script or rounding rule may change without (1) a row in the Change History of `kpi-dictionary.md`, (2) a version bump, (3) the prior version retained (status SUPERSEDED), and (4) a stated effect on comparability with the v0.1 baseline.

### Sign-off record

| Role | Name | Decision | Date | Basis |
|---|---|---|---|---|
| KPI owner (all KPIs) | Engagement lead (Dinesh Naik) | **NOT SIGNED — pending** | — | Requested: confirm or amend Q-02-04, Q-02-05 and the K-01..K-22 dictionary |
| Operations / Quality / Finance / Compliance KPI owners | none exist | No sign-off possible | — | OD-04; roles are stand-ins |
| Agent | claude-fde-agent | Prepared; no authority to approve | 2026-10-17 | — |

Items requested of Dinesh (owner: Engagement lead (Dinesh Naik); needed before Stage 34 uses the baseline; ideally before Stage 6):
1. Q-02-04: keep the 125-case DB (OD-02) or override.
2. Q-02-05: record a working definition of closed/resolved/48 h, or "accepted open" (K-11 stays 0 of 2 until then).
3. Accept or amend the 22-KPI dictionary (or reduce it).
4. Decide whether `data/enterprise_legacy.sqlite3` (12,500 objects) is a secondary baseline tier (P-03).

## Evidence References

`kpi-dictionary.md`; `baseline-kpi-sheet.md`; `baseline-evidence.md` E-05, E-12; `operating-contract-confirmations.md` GD-02, CG-2, CG-3, Q-02-04, Q-02-05.

## Assumptions

A-04-06: Freezing provisionally is better than leaving definitions floating, because Stage 34 needs an anchor, and the change process is cheap while there is only one baseline. Confirm: Engagement lead (Dinesh Naik).

## Unknowns

U-04-12 whether Dinesh agrees with the dictionary scope (22 KPIs) or wants a smaller set.

## Unresolved Issues

- Final (approved) freeze outstanding: Q-02-04, Q-02-05, dictionary acceptance.
- Stage 5 inherits: A-04-01 (total_cases meaning), A-04-03 (AS_OF), A-04-05 (reviewer role), and the sources needed for K-04/K-05.

## Residual Risks

- Self-sign-off risk: the same person owns, measures and approves (ER-11).
- If the baseline DB is replaced after Stage 6, stage 3-6 conclusions based on synthetic magnitudes need re-checking.
- Provisional freeze may be mistaken for approved freeze: every consumer must read this file's status.

## Change History

| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-17 | claude-fde-agent | Frozen-provisional; owner sign-off pending. |
