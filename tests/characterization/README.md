# Characterisation harness (Stage 15 INC-01)

Executable form of the Stage 7 characterisation plan (`docs/07-repo-assessment/characterization-test-plan.md`):
CT-01..CT-16 compared against the Stage 7 goldens, plus the M1..M15 mutation gate. Standard library only.
The legacy code is **not modified and never executed in the working tree**.

## Run

From the repository root:

```sh
python3 -B tests/characterization/run_characterization.py                  # CT-01..CT-16 + shipped tests (~40 s)
python3 -B tests/characterization/run_characterization.py --mutation-gate  # + M1..M15 (~5-6 min)
python3 -B tests/characterization/run_characterization.py --mutation-gate --mutants M1,M2   # subset
sha256sum -c --quiet ../_data-backup-2026-10-17/SHA256SUMS.txt             # must exit 0 afterwards
```

Exit code 0 = all green, 1 = a characterisation difference / surviving mutant / shipped-suite deviation,
2 = refused (unsafe sandbox, fixture hash mismatch, golden manifest mismatch).
Report: `<sandbox-root>/<label>/report.json` (default sandbox root `~/fde_sbx/s15-inc01`).

## How it stays safe

1. `--sandbox-root` must resolve outside the working tree and the fixture source, and must not be an
   ancestor of either (E-CO-NOT-SANDBOX, AC-CO-06). Deletion only happens strictly inside it.
2. A *pristine* copy is built in the sandbox: code from the working tree (read only, without `.git` and
   `data/`) + `data/` from the fixture source (default `../_data-backup-2026-10-17`), then every one of the
   1,512 files is checked against `fixtures/FX-BASE125.sha256` (CT-H1, OD-09 baseline 125 cases / seed 4100).
3. Every capture (`capture/*.py`) runs as a child process started from the sandbox copy, and each
   mutating step works on its own fresh copy (subprocess-per-scenario, HD-1 option B).
4. Children get `PYTHONHASHSEED=0`, no bytecode, and no inherited `LEGACY_DB`/`HOST`/`PORT`; servers bind
   to `127.0.0.1` on ephemeral ports (CT-H2).

## Files

| Path | Purpose |
|---|---|
| `run_characterization.py` | CLI: build sandbox, run captures, compare (unittest, one TestCase per CT), shipped suite, mutation gate |
| `harness.py` | sandbox guard, fixture gate, CT-H3 normalisation (rules N1-N4), comparison |
| `capture/{api,batch,lib}.py` | ports of the Stage 7 capture scripts (same requests/commands/keys) |
| `capture/supplement.py` | INC-01 additions: `sql/legacy_reports.sql` itself (CT-12), readiness scripts (CT-15), write methods on every route + static scan (CT-16) |
| `catalogue.json` | CT-01..CT-18 -> golden elements; `ac_links` for CT-04..CT-16 (Stage 13 C3) |
| `mutants.json` | M1..M15 (verbatim from Stage 7 `mutation_probe.sh`) |
| `golden/stage7/` | byte copies of the Stage 7 goldens and R1/R7 logs |
| `golden/inc01/supplement_golden_v1.json` | INC-01 supplement golden (captured once on unmodified code) |
| `golden/INDEX.json`, `golden/MANIFEST.sha256` | active goldens + integrity manifest (checked before every run) |
| `fixtures/FX-BASE125.sha256` | pinned sha256 of all 1,512 baseline data files |

## Updating a golden (CT-H4)

`--update-golden <api|batch|lib|supplement> --reviewed-by NAME` writes a **new** versioned file
(never overwrites). It becomes active only when `golden/INDEX.json` and `golden/MANIFEST.sha256` are changed
in a reviewed PR. Stage 7 goldens are never edited in place.

This directory deliberately has no `__init__.py`, so `python -m unittest discover -s tests` (CI, `scripts/verify.sh`)
does not pick it up and the shipped suite behaves exactly as before.
