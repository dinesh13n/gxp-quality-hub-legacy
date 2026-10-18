from gen_common import *
import re, collections
FR, PN, AC, BEH, SBR, SEC = M['FR'], M['PNFR'], M['AC'], M['BEH'], M['SBR'], M['SEC']
acb = C['ac_behs']; T = {t['ac']: t for t in TESTS}
def expand(s):
    out = set()
    for m in re.finditer(r'AC-([A-Z]+)-(\d+)((?:/\d+)*)', s):
        out.add('AC-%s-%s' % (m.group(1), m.group(2)))
        for n in [x for x in m.group(3).split('/') if x]: out.add('AC-%s-%s' % (m.group(1), n))
    return sorted(out)
def rows(idl, note=None):
    note = note or {}
    r = ['| ID | Requirement (abridged) | Rel | Acceptance criteria | #AC | #neg | Class | Evidence stage | Domain note |', '|---|---|---|---|---|---|---|---|---|']
    for i in idl:
        c = CH[i]; txt = (FR[i]['text'] if i in FR else PN[i]['text'] + ' - ' + PN[i]['target'])[:110].replace('|', '/')
        r.append('| %s | %s | %s | %s | %d | %d | %s | %s | %s |' % (i, txt, c['release'], rng(c['acs']), len(c['acs']), c['neg'], c['classes'], ','.join(map(str, c['evidence_stages'])), note.get(i, '')))
    return '\n'.join(r)
def stats(idl):
    acs = sorted({a for i in idl for a in CH[i]['acs']}); return acs, sum(AC[a]['kind'] == 'negative' for a in acs), collections.Counter(T[a]['evidence_class'][0] for a in acs)
def generic(name, sources, summary, fnd, refs, ass, unk, iss, risk): write(name, SRC_STD + sources, summary, fnd, refs, ass, unk, iss, risk)
# ================= SECURITY =================
sec_fr = [f for f in FR if f.startswith(('FR-SEC', 'FR-GATE'))] + ['FR-INT-07', 'FR-DEC-05', 'FR-POL-03', 'FR-ID-02']
sec_pn = ['PNFR-07', 'PNFR-08', 'PNFR-09', 'PNFR-12', 'PNFR-13', 'PNFR-10']
sec_ids = sec_fr + sec_pn; acs, neg, cl = stats(sec_ids)
th = ['| Threat | Objective | Control (spec ref) | Requirements | Planned tests (cited ACs + ACs of cited behaviours) | #AC | Fixture / planted data |', '|---|---|---|---|---|---|---|']
nothr = []
for k, v in SEC.items():
    cited = set(expand(v['control'])); bs = re.findall(r'BEH-[A-Z]+-\d+', v['control'])
    for b in bs: cited |= {a for a in AC if b in acb[a]}
    cited |= {a for f in v['frs'] for a in CH[f]['acs']} if not cited else set()
    if not cited: nothr.append(k)
    th.append('| %s | %s | %s | %s | %s | %d | %s |' % (k, v['threat'][:60], v['control'][:80].replace('|', '/'), ', '.join(v['frs'] + v['pnfrs'] + v['brs']), rng(sorted(cited)), len(cited), 'planted-string set (86/22/44)' if k in ('SEC-04',) else ''))
zh = ['FR-GATE-01', 'FR-GATE-02', 'FR-GATE-03', 'FR-GATE-04', 'FR-GATE-05', 'FR-GATE-06']
fnd = '''### SEC-1 Scope and counts [Verified Fact: computed]
%d requirements in the security view (%d FR + %d PNFR); they carry **%d distinct acceptance criteria, %d of them negative (forbidden-path)** (%.0f%%). Class mix of those criteria: A %d / B %d / C %d. Threat register SEC-01..SEC-%02d (security-spec.md): **%d of %d threats have >= 1 planned test**; threats with none: %s.

### SEC-2 Requirement -> test (security view)
%s

### SEC-3 Threat -> control -> requirement -> test
%s

### SEC-4 Findings
- **[Verified Fact]** Zone H (human-only disposition/release/e-signature, BR-08, FR-GATE-01..06) has %d ACs; %d are negative. The fresh-install state (holders empty, mode `none`) is itself tested (FR-GATE-04, OD-S12-05/06), so *no pilot use of Zone H is permitted or testable with real holders* until Dinesh decides (RD-4).
- **[Verified Fact]** Evidence class for authentication/authorisation (PNFR-07), transport/secrets (PNFR-08), audit tamper-evidence (PNFR-09), untrusted content (PNFR-13): class A/B sandbox tests, evidence stage 26 (TEVV). They prove the mechanism on synthetic data only. No penetration test, secret-scan baseline or TLS configuration review is planned in any AC beyond AC-SEC-15/16/18 and AC-NFR-08 [Inference].
- **[Verified Fact]** Error codes with security meaning not asserted by any AC: %s [GAP-13-12].
- **[Verified Fact]** `FR-SEC-03` and `PNFR-12` (sensitive-field access levels) are **R2**; no R1 control covers field-level protection (data-use-constraints). Impact: R1 treats all data as restricted by default (`evidence_record.access_level` default `restricted`) [Inference].
- **[Inference]** The planted-string fixture (86 feed rows, 22 document bodies, 44 regex hits) is the single evidence source for FR-INT-07/PNFR-13; its counts come from Stage 9/12 and were not re-counted in this documentation-only stage.
- **[Unknown]** Who administers users and holder lists in real operation (OD-S12-06); where the audit anchor lives in a deployment (OD-S12-18). Without them AC-SEC-10/11 can only prove the mechanism.
- **[Assumption]** "Tamper-evident" is framing only; there is no Part 11 / GxP compliance claim (DR-29; ACC-8).
''' % (len(sec_ids), len(sec_fr), len(sec_pn), len(acs), neg, 100.0 * neg / len(acs), cl['A'], cl['B'], cl['C'], len(SEC), len(SEC) - len(nothr), len(SEC), ids(nothr) if nothr else 'none', rows(sec_ids, {'FR-SEC-03': 'R2: no R1 control', 'PNFR-12': 'R2', 'FR-GATE-04': 'blocked by OD-S12-05/06', 'FR-GATE-05': 'OD-S12-05 both modes'}), '\n'.join(th), sum(len(CH[f]['acs']) for f in zh), sum(CH[f]['neg'] for f in zh), ', '.join(e for e in S['ERR_not_asserted_by_AC'] if re.match(r'E-(AUTH|SEC|GATE)', e)))
generic('security-traceability.md', ['docs/12-specs/security-spec.md', 'docs/12-specs/api-contracts.md'], 'Security view: %d requirements -> %d acceptance criteria (%d negative) -> evidence at Stage 26 (TEVV). %d of %d threats have a planned test. Mechanism-level evidence only; no real users, holders or environment exist.' % (len(sec_ids), len(acs), neg, len(SEC) - len(nothr), len(SEC)), fnd,
 '- `docs/12-specs/security-spec.md` (threat register), `docs/12-specs/features/f02-human-disposition-gate.md`, `f09-access-audit-protection.md`, `docs/09-initial-prd/functional-requirements.md`, `nfrs.md`, `docs/12-specs/acceptance-criteria.md`, `error-handling-spec.md`.',
 '- A-13-08 [Assumption]: the security view membership (FR-SEC, FR-GATE, FR-INT-07, FR-DEC-05, FR-POL-03, FR-ID-02, PNFR-07..10,12,13) is correct; Stage 24 may extend it.', '- U-13-07: real role holders, admin model and audit anchor location (OD-S12-06, OD-S12-18).',
 '- Zone H unusable until OD-S12-05/06 decided (owner: %s, before pilot, Stage 15+).\n- Unasserted security error codes (GAP-13-12).' % OWNER, '- R-13-07 Passing sandbox security tests could be mistaken for a security assessment; none was performed (no pen test, no threat-model review beyond security-spec.md).')
# ================= DATA =================
dat_fr = [f for f in FR if f.startswith(('FR-INT', 'FR-ID'))] + ['FR-DEC-01', 'FR-DEC-02', 'FR-DEC-03', 'FR-DEC-04', 'FR-DEC-06', 'FR-MET-04', 'FR-MET-06', 'FR-CO-01']
dat_pn = ['PNFR-10', 'PNFR-11', 'PNFR-12', 'PNFR-16', 'PNFR-17', 'PNFR-20']; dat_ids = dat_fr + dat_pn; acs, neg, cl = stats(dat_ids)
sch = ['| Schema | Table / shape | Requirement(s) | Planned tests (via requirement) | Contract file |', '|---|---|---|---|---|']
import os
sdir = os.path.join(ROOT, 'docs/12-specs/contracts/schemas'); sfiles = set(os.listdir(sdir))
for k, v in M['SCH'].items():
    f = v['shape'] + '.schema.json'
    sch.append('| %s | %s | %s | %s | %s |' % (k, v['table'][:40], ', '.join(v['frs'] + v['pnfrs']) or '**none** (cross-cutting)', rng(sorted({a for r in v['frs'] + v['pnfrs'] for a in CH[r]['acs']}))[:90], ('`schemas/%s` (exists)' % f) if f in sfiles else 'no file (derived or DDL-only)'))
evt = ['| Event | Name | Requirement(s) | Planned tests |', '|---|---|---|---|']
for k, v in M['EV'].items(): evt.append('| %s | %s | %s | %s |' % (k, v['name'], ', '.join(v['frs'] + v['pnfrs']), rng(sorted({a for r in v['frs'] + v['pnfrs'] for a in CH[r]['acs']}))[:90]))
fnd = '''### DAT-1 Counts [Verified Fact: computed]
%d requirements in the data view (%d FR + %d PNFR) -> **%d acceptance criteria (%d negative)**; class A %d / B %d / C %d. %d schemas (SCH-), %d decision events (EV-), %d JSON Schema files, DDL `contracts/ddl/hub-schema-v0.1.sql`, 14 valid examples + `invalid-cases.json`.

### DAT-2 Requirement -> test (data view)
%s

### DAT-3 Schema -> requirement -> test
%s

### DAT-4 Event -> requirement -> test
%s

### DAT-5 Findings
- **[Verified Fact]** Every schema and event except `SCH-ERROR` traces to an FR/PNFR. `SCH-ERROR` (error envelope) is a cross-cutting convention justified by API conventions, not a requirement [GAP-13-05].
- **[Verified Fact]** Replay/idempotency (FR-INT-02, BR-05, PNFR-11) is the highest-value data requirement (2025 rollback, INC-2025-014). It has ACs for identical re-delivery; the *changed-content* path (FR-INT-03 REVISED_CONFLICT) has **no negative AC** and its corrected-replay fixture cannot come from shipped data (none exists, FND-INT-1) so it is class C (synthetic fixture) [GAP-13-11].
- **[Verified Fact]** Stage 11 DC-03 identity key is wrong (business_key is not an item identity; 2,386 of 2,407 multi-row groups differ) - OD-10(a). Specs use the natural key (partner, record_kind, ref_id, source_ts) (OD-S12-17); tests built on DC-03 would be wrong. Stage 11 v0.2 addendum is pending (owner: %s).
- **[Verified Fact]** Source contract: `source_messages` 15/15 conform, `partner_feeds` 0/8,567, `gateway_inbox` 0/1 (RF-2). The per-source `record_only` vs `enforce` choice (OD-S12-11) is open, so FR-INT-04 tests must run both modes (class B).
- **[Verified Fact]** Month-end totals (FR-MET-04, BR-10): the legacy SQL report 742,956.61 vs true 622,826.44 (+19.3%%) (DV-01) is a golden (CT-12) that is not acceptance-linked [GAP-13-06]; cut-off/denominator/cost source are open (OD-S12-08).
- **[Verified Fact]** Retention (PNFR-10) is hold-all: tests assert 0 deletions; no deletion/archival path exists to test (OD-S12-09).
- **[Inference]** All data-quality evidence runs on the 125-case, seed-4100 baseline (OD-09) and synthetic feeds; no real data exists (OD-04). Results are labelled "synthetic, unvalidated" (PNFR-20).
- **[Unknown]** Case creation path (OD-S12-19): R1 is backfill only, so data-creation requirements for non-legacy cases cannot be traced or tested.
''' % (len(dat_ids), len(dat_fr), len(dat_pn), len(acs), neg, cl['A'], cl['B'], cl['C'], len(M['SCH']), len(M['EV']), len(sfiles), rows(dat_ids, {'FR-INT-03': 'no negative AC; synthetic fixture', 'FR-INT-04': 'OD-S12-11 both modes', 'FR-MET-04': 'OD-S12-08', 'PNFR-10': 'OD-S12-09 hold-all'}), '\n'.join(sch), '\n'.join(evt), OWNER)
generic('data-traceability.md', ['docs/12-specs/schema-specifications.md', 'docs/12-specs/event-contracts.md', 'docs/12-specs/contracts/', 'docs/11-data-context/data-contracts.md'], 'Data view: %d requirements -> %d acceptance criteria (%d negative); %d schemas and %d events traced; replay/changed-content and month-end paths are the weak spots; all evidence is synthetic.' % (len(dat_ids), len(acs), neg, len(M['SCH']), len(M['EV'])), fnd,
 '- `docs/12-specs/schema-specifications.md`, `event-contracts.md`, `contracts/schemas/`, `contracts/ddl/`, `docs/11-data-context/data-contracts.md`, `docs/12-specs/spec-readiness.md` (RF-1, RF-2), `docs/07-repo-assessment/characterization-test-plan.md` (CT-05, CT-07, CT-08, CT-12).',
 '- A-13-09 [Assumption]: natural key (partner, record_kind, ref_id, source_ts) is the item identity (supported only by 67 replay pairs, A-12-F04-3).', '- U-13-08: item identity on real data; corrected-replay behaviour; cost data source.',
 '- Stage 11 DC-03 addendum pending (OD-10a); OD-S12-08/09/11/17/19 open.', '- R-13-08 Tests pinned to an unconfirmed identity key may need rewriting if OD-S12-17 is decided differently.')
