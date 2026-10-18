from gen_common import *
import re, collections
FR, PN, AC, BEH, SBR = M['FR'], M['PNFR'], M['AC'], M['BEH'], M['SBR']
T = {t['ac']: t for t in TESTS}
def rows(idl, note=None):
    note = note or {}
    r = ['| ID | Requirement (abridged) | Rel | Acceptance criteria | #AC | #neg | Class | Evidence stage | Domain note |', '|---|---|---|---|---|---|---|---|---|']
    for i in idl:
        c = CH[i]; txt = (FR[i]['text'] if i in FR else PN[i]['text'] + ' - ' + PN[i]['target'])[:110].replace('|', '/')
        r.append('| %s | %s | %s | %s | %d | %d | %s | %s | %s |' % (i, txt, c['release'], rng(c['acs']), len(c['acs']), c['neg'], c['classes'], ','.join(map(str, c['evidence_stages'])), note.get(i, '')))
    return '\n'.join(r)
def stats(idl):
    acs = sorted({a for i in idl for a in CH[i]['acs']}); return acs, sum(AC[a]['kind'] == 'negative' for a in acs), collections.Counter(T[a]['evidence_class'][0] for a in acs)
# ================= AI QUALITY =================
tp = {}
for f, v in FR.items():
    m = re.search(r'touchpoint (T\d)', v['text'])
    if m: tp[f] = m.group(1)
ai_ids = ['FR-CO-04', 'PNFR-18', 'PNFR-17', 'FR-REV-01', 'FR-REV-03', 'FR-REV-04', 'FR-INT-06', 'FR-ID-04', 'FR-GATE-06', 'PNFR-15', 'PNFR-13']
acs, neg, cl = stats(ai_ids)
ai_acs = [a for a in AC if re.search(r'model|egress|llm|generat|ai\b|ml\b', ' '.join([AC[a]['given'], AC[a]['when'], AC[a]['then']]).lower()) and AC[a]['prefix'] in ('CO', 'OBS', 'NFR', 'REV')]
tprow = ['| Touchpoint | Requirement | Mechanism (No-AI) | Planned tests |', '|---|---|---|---|']
for f, t in sorted(tp.items(), key=lambda kv: kv[1]): tprow.append('| %s | %s | rules / templates / keyword-FTS / deterministic join | %s |' % (t, f, rng(CH[f]['acs'])))
fnd = '''### AIQ-1 Position [Verified Fact: OD-08; docs/08-ai-qualification/qualification-decision.md]
Dinesh answered **Accept No-AI** (OD-08, 2026-10-18). The product contains **no model call**. There are therefore **no AI-quality requirements** (no accuracy, groundedness, hallucination, bias or prompt-regression metrics) to trace: Stage 19 is not-applicable, Stage 22 is not triggered. Tracing AI-quality evidence here would be fabricating requirements. What *is* traceable is the **absence** of AI and the quality of the deterministic stand-ins.

### AIQ-2 Requirements that carry the No-AI position (planned tests) [Verified Fact: computed]
%s

Totals: %d acceptance criteria (%d negative); class A %d / B %d / C %d.

### AIQ-3 AI-related criteria found by text scan [Inference]
%s

### AIQ-4 Findings
- **[Verified Fact]** `FR-CO-04` (no AI/LLM/ML call, no model-inference egress) -> `PNFR-18` (0 model calls, tripwire = 0 at Stage 32) -> AC-CO-11, AC-CO-12, AC-OBS-06, AC-NFR-18 (static import/egress guards and a run-time counter). Evidence stages 16, 31, 32. All class A and negative/static in nature.
- **[Verified Fact]** The five Stage 8 touchpoints are deterministic: %s. Each has an FR and planned tests; none requires a model.
- **[Verified Fact]** Search quality (`FR-REV-03`, R2): the only quality evidence possible is a recall *baseline* on a synthetic corpus of 3 base sentences (AC-REV-15, class C). It cannot support or refute a case for AI-assisted Q&A. Re-qualification is allowed only via RQ-1..RQ-3 (real corpus + >= 50 labelled questions, multilingual/OCR failure, or a named stakeholder request) and a new Dinesh decision [Verified Fact: qualification-decision.md].
- **[Inference]** Determinism is the "quality" property: PNFR-17 (identical input -> bit-identical output) with AC-DEC-05, AC-GATE-15, AC-POL-22, AC-INT-20, AC-MET-21, AC-REV-14, AC-CO-13, AC-NFR-17 and the Stage 7 goldens (CT-01..CT-03) as evidence. Template-rendered explanations (FR-REV-01) are tested for faithfulness to the rule trace by exact match, not by a judge model.
- **[Verified Fact]** Coding assistants used to build the system are dev tooling, not product AI (OD-08); their output is subject to the same tests.
- **[Unknown]** Whether a future AI-assisted touchpoint will be requested. If so, a new Stage 8 qualification and new requirements are needed before any AI-quality traceability exists.

### AIQ-5 Gap statement
No AI-quality gap exists *because* no AI-quality requirement exists. This is not a coverage claim; it is a scope fact tied to OD-08. The tripwire (PNFR-18) is the only continuing control and must be wired at Stage 32 [GAP-13-14].
''' % (rows(ai_ids), len(acs), neg, cl['A'], cl['B'], cl['C'], ', '.join('%s (%s)' % (a, AC[a]['kind']) for a in sorted(ai_acs)[:20]) or 'none', '\n'.join(tprow))
write('ai-quality-traceability.md', SRC_STD + ['docs/08-ai-qualification/qualification-decision.md', 'docs/08-ai-qualification/deterministic-vs-ai-boundaries.md'], 'No-AI product (OD-08): there are no AI-quality requirements to trace. The view traces the controls that keep it No-AI (FR-CO-04 -> PNFR-18 -> %d ACs incl. static egress guards, Stage 32 tripwire) and the deterministic stand-ins (touchpoints T1-T5, determinism PNFR-17). Search recall is a baseline only (class C).' % len(acs), fnd,
 '- `.fde/orchestrator-decisions.md` OD-08; `docs/08-ai-qualification/qualification-decision.md` (T1-T5, RQ-1..RQ-3); `docs/09-initial-prd/nfrs.md` PNFR-17/18; `docs/12-specs/acceptance-criteria.md`.',
 '- A-13-10 [Assumption]: OD-08 stands for R1/R2. [Verified Fact] A read-only grep in this stage for openai|anthropic|langchain|llm|gpt- over *.py, *.js, *.java, *.toml, *.txt outside docs/, .fde/ and data/ returned 0 files, so no model client is present in the legacy source (a name scan, not a proof of absence of egress).', '- U-13-09: any future request for AI-assisted Q&A (RQ-1..RQ-3).', '- Tripwire wiring is a Stage 32 task (GAP-13-14).', '- R-13-09 Scope creep: an AI feature added without re-qualification would have no requirement, test or evidence.')
# ================= RESILIENCE =================
res_ids = ['FR-RUN-01', 'FR-RUN-02', 'FR-RUN-03', 'FR-INT-01', 'FR-INT-02', 'FR-INT-03', 'FR-INT-08', 'FR-CO-03', 'FR-CO-01', 'FR-DEC-02', 'FR-MET-05', 'PNFR-01', 'PNFR-02', 'PNFR-03', 'PNFR-04', 'PNFR-05', 'PNFR-11', 'PNFR-14', 'PNFR-19']
acs, neg, cl = stats(res_ids)
fnd = '''### RES-1 Counts [Verified Fact: computed]
%d requirements (%d FR + %d PNFR) -> **%d acceptance criteria (%d negative)**; class A %d / B %d / C %d. Business requirements: BR-05 (replay safe), BR-06 (delayed/missing/revised items visible), BR-12 (backlog ageing), BR-13 (releasable without 2025-style rollback); root causes RC-5 (silent capacity cap) and RC-6 (replay as duplicate); incident INC-2025-014.

### RES-2 Requirement -> test (resilience view)
%s

### RES-3 Findings
- **[Verified Fact]** The targets PNFR-01..05 (99.5%% availability, 06:00 completion, 4 h feed acceptance, 24 h staleness, RTO 8 h / RPO 24 h) come from archived working targets the source calls "not measured guarantees" (`docs/operations-service-levels.md`). All five are **class C**: evidence is a sandbox measurement or rehearsal labelled synthetic; attainment of the target on a real environment cannot be shown (ACC-8). PNFR-03/04 are R2.
- **[Verified Fact]** No-silent-cap (FR-RUN-03, RC-5) is traced to the legacy behaviour characterised in Stage 7 (1000-row reconcile cap, CT-08; night-shift limits, CT-10). Both CT tests are P1 and **not acceptance-linked** [GAP-13-06].
- **[Verified Fact]** Concurrency on one SQLite file (15 s busy_timeout) is uncharacterised (CT-17, U-07-05); AC-DEC-22 covers logical sequence conflict only. A resilience claim about parallel API+bridge+reconcile cannot be made [GAP-13-15].
- **[Verified Fact]** Rollback rehearsal and replay-safety release gate (FR-CO-03 Should/R1, PNFR-19) are tested at AC-CO-09/15, AC-NFR-19; evidence belongs to Stage 30 (release) and requires a release process that does not yet exist.
- **[Verified Fact]** Restore rehearsal (PNFR-05): backup `../_data-backup-2026-10-17/` with 1,512-file SHA256SUMS exists for the *legacy* data; a rehearsal for the new `hub.sqlite3` and audit anchor is only planned (AC-NFR-05, AC-CO-09).
- **[Verified Fact]** Scheduler is disabled by default pending OD-S12-10 (is a deterministic scheduler an "automated action" under HAR-10); FR-RUN-01 tests run both modes (class B), and PNFR-02 cannot be proven until a schedule is enabled.
- **[Inference]** No chaos/failure-injection, DR (BC/DR is Stage 29) or load test is traced: no requirement asks for one. The 125-case baseline is too small for capacity conclusions; PNFR-06 target is Unknown (OPD-14).
- **[Unknown]** Site timezone for the 06:00 check (`site.timezone` not configured, U-12 register); Docker/Compose behaviour (CT-18) and Python 3.12 runtime (OD-S12-12).
''' % (len(res_ids), sum(i.startswith('FR') for i in res_ids), sum(i.startswith('PNFR') for i in res_ids), len(acs), neg, cl['A'], cl['B'], cl['C'], rows(res_ids, {'PNFR-01': 'class C, working target', 'PNFR-02': 'needs schedule (OD-S12-10)', 'PNFR-05': 'rehearsal of hub.sqlite3 + anchor', 'FR-RUN-01': 'OD-S12-10 both modes', 'FR-INT-08': 'R2', 'PNFR-03': 'R2', 'PNFR-04': 'R2'}))
write('resilience-traceability.md', SRC_STD + ['docs/operations-service-levels.md', 'docs/07-repo-assessment/characterization-test-plan.md', 'docs/12-specs/features/f06-scheduled-runs.md', 'docs/12-specs/features/f10-coexistence-change-safety.md'], 'Resilience view: %d requirements -> %d acceptance criteria. Replay safety, no-silent-cap and rollback are testable in a sandbox; availability/timeliness/RTO-RPO targets are unvalidated working targets and only measurable as synthetic proxies (class C).' % (len(res_ids), len(acs)), fnd,
 '- `docs/09-initial-prd/nfrs.md` (PNFR-01..05, 11, 14, 19), `docs/operations-service-levels.md`, `docs/12-specs/nfr-spec.md`, `docs/07-repo-assessment/characterization-test-plan.md` (CT-08, CT-10, CT-17, CT-18), `docs/12-specs/spec-readiness.md` (OD-S12-10, -12).',
 '- A-13-11 [Assumption]: resilience targets stay Assumptions until Dinesh adopts or rejects them (OD-S12-14).', '- U-13-10: site timezone; real environment; concurrency behaviour (U-07-05).', '- GAP-13-07 (class C targets) and GAP-13-15 (concurrency) are open.', '- R-13-10 A passing sandbox rehearsal could be read as an RTO/RPO guarantee.')
# ================= COST =================
cost_ids = ['FR-MET-04', 'FR-MET-06', 'FR-MET-08', 'PNFR-18', 'PNFR-16', 'PNFR-06', 'PNFR-20']
acs, neg, cl = stats(cost_ids)
fnd = '''### COST-1 What "cost" means in this PRD [Verified Fact]
Stage 9 contains **no cost, budget, TCO or capacity-cost requirement**. Cost appears in three narrow forms: (1) *case cost and avoidable rework attributable per case/period* (BR-10, Should) realised by month-end metric correctness FR-MET-04 and the R2 placeholder FR-MET-08 (OP-MET-05 returns E-MET-NOT-AVAILABLE until a cost input and owner exist, OPD-08); (2) *zero model-call cost* as a tripwire (PNFR-18, QD-4 in `nfrs.md`); (3) reproducibility/labelling of any figure (PNFR-16, PNFR-20). `docs/09-initial-prd/nfrs.md` states "No benefit is quantified" and U-09-03 "Real volumes, timings, labour and cost (no production telemetry; OD-04)".

### COST-2 Requirement -> test (cost view)
%s

Totals: %d acceptance criteria (%d negative); class A %d / B %d / C %d.

### COST-3 Findings
- **[Verified Fact]** `docs/00-preflight/ai-economics/` (Stage 0C) holds provisional TCO, token and loop budgets: every price, effort and usage input is an **Assumption**; gross cost only, no benefits (OD-04). With OD-08 (No-AI) the token/context/loop budgets are void: expected model cost is 0, to be verified by the tripwire.
- **[Verified Fact]** `FR-MET-04`'s tests (AC-INT-27, AC-MET-09..13) check correctness of money arithmetic (exact decimal, no join fan-out, unparsable amounts surfaced); the legacy figure 742,956.61 vs 622,826.44 (DV-01) is the preserved-vs-fix case. They do **not** evaluate the economics of running the product.
- **[Verified Fact]** `operating_costs.total_cases` is random, not "cases created" (OD-07); AC-MET-16 refuses it as a source (E-MET-SOURCE-REFUSED). Therefore no cost-per-case KPI can be produced from shipped data.
- **[Inference]** There is no requirement or planned test for infrastructure cost, build/run effort, storage growth, or the cost of reviewer time; Stage 32 (FinOps/TCO) will have only PNFR-18 as a measurable control. This is a requirements gap, not a test gap [GAP-13-16].
- **[Unknown]** Cost data source and owner (OD-S12-08/OPD-08); real volumes; labour rates.
''' % (rows(cost_ids, {'FR-MET-08': 'R2 placeholder: E-MET-NOT-AVAILABLE', 'PNFR-18': 'tripwire for Stage 32'}), len(acs), neg, cl['A'], cl['B'], cl['C'])
write('cost-traceability.md', SRC_STD + ['docs/00-preflight/ai-economics/preliminary-tco.md', 'docs/00-preflight/ai-economics/economics-readiness.md', 'docs/12-specs/features/f07-metrics-definition-tags.md'], 'Cost view: the PRD has no cost/budget requirement beyond metric correctness (BR-10, FR-MET-04), a cost placeholder (FR-MET-08, R2) and the zero-model-call tripwire (PNFR-18). %d ACs trace; infrastructure/run-cost has no requirement (GAP-13-16). All cost inputs remain Assumptions (OD-04).' % len(acs), fnd,
 '- `docs/00-preflight/ai-economics/*`, `docs/09-initial-prd/nfrs.md`, `docs/12-specs/features/f07-metrics-definition-tags.md`, `docs/12-specs/acceptance-criteria.md`, `.fde/orchestrator-decisions.md` OD-04, OD-07, OD-08.',
 '- A-13-12 [Assumption]: cost is out of R1 product scope except the items above; Stage 32 may add requirements.', '- U-13-11: cost data owner and source (OD-S12-08).', '- GAP-13-16 (no TCO requirement).', '- R-13-11 Cost claims at Stage 32/36 may have no traced requirement or evidence.')
