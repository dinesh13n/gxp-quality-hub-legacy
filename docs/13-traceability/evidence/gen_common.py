import json, os, sys, collections
ROOT = os.environ['REPO']; EV = os.path.join(ROOT, 'docs/13-traceability/evidence'); OUT = os.path.join(ROOT, 'docs/13-traceability')
C = json.load(open(os.path.join(EV, 'coverage.json'))); S = C['stats']; CH = C['chains']; UP = C['upstream']; TESTS = C['tests']
M = json.load(open(os.path.join(EV, 'trace_model.json')))
OWNER = 'Engagement lead (Dinesh Naik)'
LABEL = '**Label: synthetic repository, unvalidated against any organisation. Status DRAFT: not approved. Planned tests are PLANNED / NOT-RUN: nothing in this stage was executed against the application, and no evidence listed here as "expected" exists yet. Approval is Dinesh Naik\'s decision (HAR-11).**'
def ids(l, n=None):
    l = list(l)
    if not l: return '-'
    return ', '.join(l if n is None or len(l) <= n else l[:n] + ['... +%d' % (len(l) - n)])
def rng(acs):
    # compact AC list: AC-DEC-01..04 style
    out = []; by = collections.OrderedDict()
    for a in acs: by.setdefault(a.rsplit('-', 1)[0], []).append(a.rsplit('-', 1)[1])
    for p, ns in by.items():
        ns = sorted(ns); run = [ns[0]]; groups = []
        for n in ns[1:]:
            if int(n) == int(run[-1]) + 1: run.append(n)
            else: groups.append(run); run = [n]
        groups.append(run)
        out.append(p + '-' + ','.join(g[0] if len(g) < 3 else g[0] + '..' + g[-1] for g in groups))
    return '; '.join(out) if out else '-'
def write(name, sources, summary, findings, refs, assumptions, unknowns, issues, risks, status='DRAFT'):
    fm = '---\nstage: "13 — Requirements → Specs → Tests → Evidence Traceability"\nartifact: "%s"\nversion: "v0.1"\ndate: "2026-10-18"\nauthor_agent: "claude-fde-agent"\nstatus: "%s"\nevidence_sources: %s\nsupersedes: "none"\n---\n' % (name, status, json.dumps(sources))
    def sec(t, b): return '## %s\n%s\n\n' % (t, b.strip())
    body = sec('Summary', LABEL + '\n\n' + summary) + sec('Findings', findings) + sec('Evidence References', refs) + sec('Assumptions', assumptions) + sec('Unknowns', unknowns) + sec('Unresolved Issues', issues) + sec('Residual Risks', risks)
    body += sec('Change History', '| Version | Date | Author/agent | Change |\n|---|---|---|---|\n| v0.1 | 2026-10-18 | claude-fde-agent | Initial traceability produced by script from docs/ (evidence/trace_parse.py, trace_compute.py). |')
    open(os.path.join(OUT, name), 'w', encoding='utf-8').write(fm + body)
    print('wrote', name, len(fm + body))
SRC_STD = ['docs/09-initial-prd/functional-requirements.md', 'docs/09-initial-prd/nfrs.md', 'docs/12-specs/acceptance-criteria.md', 'docs/12-specs/business-rules.md', 'docs/12-specs/spec-readiness.md', 'docs/13-traceability/evidence/coverage.json', 'docs/13-traceability/evidence/coverage_output.txt', '.fde/orchestrator-decisions.md (OD-03a, OD-07, OD-08, OD-09, OD-10)']
