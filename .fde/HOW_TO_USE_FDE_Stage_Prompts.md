# How to Use the AI FDE Stage System Prompts

A guide to the 46 stage-by-stage system prompts built from the **AI FDE End-to-End Production Delivery Spine**, the **Prompt Template** and the **Prompt Anatomy**.

| Item | Detail |
|---|---|
| Package | FDE_Stage_System_Prompts |
| Prompts | 46 files: Stages 0A, 0B, 0C, 1–42 and FINAL |
| Prepared for | Dinesh Naik — FDE training programme |
| Prepared on | 17 October 2026 |
| Version | v1.0 |

## 1. What is in the package

```
FDE_Stage_System_Prompts/
├── HOW_TO_USE_FDE_Stage_Prompts.md     ← this guide (Markdown)
├── HOW_TO_USE_FDE_Stage_Prompts.docx   ← this guide (Word)
└── stage-prompts/
    ├── 00A_Pre-Flight-Repository-and-System-Orientation.md
    ├── 00B_Provisional-Operating-Contract-and-Engineering-Boundaries.md
    ├── 00C_Provisional-Token-Efficiency-and-AI-Economics-Envelope.md
    ├── 01_Engage-and-Qualify.md
    ├── …                                (one file per stage, in run order)
    ├── 42_Executive-Defence-and-Final-Value-Story.md
    └── 43_FINAL_Authoritative-Final-As-Built-PRD.md
```

**One file = one stage = one system prompt.** Each file stands on its own: it repeats the Global Execution Contract, so you never need to load two files together.

## 2. File naming — how to read it

- The **numeric prefix is the stage number**, so files sort in run order and match the `docs/` folder each stage writes to. For example, `07_…md` writes to `docs/07-repo-assessment/`.
- **Pre-flight stages** use `00A`, `00B` and `00C`. All three write under `docs/00-preflight/` (sub-folders `discovery/`, `operating-contract/` and `ai-economics/`).
- **FINAL** uses the prefix `43_FINAL_` only so that it sorts last. It is **not** a Stage 43. It writes to `docs/final-prd/`.
- The YAML header in every file also shows `run_order: N of 46`, which removes any doubt about sequence.

## 3. How each prompt is built

Every stage prompt follows the **Prompt Template** section order. Each section is labelled with the **Prompt Anatomy** component it implements, and a few production-grade additions are layered on top.

| Prompt section | Source | Anatomy component | Why it is there |
|---|---|---|---|
| YAML header | Added | 8 — Lifecycle Linkage | Machine-readable stage ID, run order, mode, path, dependencies and next stage |
| How to use | Added | — | One-line instruction for the operator |
| Role | Added | — | Sets the expert persona and FDE behaviour |
| Engagement Context | Added | — | `{{placeholders}}` you fill before running |
| Global Execution Contract | Delivery Spine | 5 — Evidence Rules | Rules for every artifact, repeated so each file is self-contained |
| Operating Mode | Added | 3 — Constraints | Read-only / docs-only / scoped-write / validate / operate |
| Objective | Template | 1 — Action / Mission | Action verb + outcome + evidence sources |
| Lifecycle Linkage | Template + Spine | 8 — Lifecycle Linkage | What the stage consumes and feeds |
| Scope (Include / Exclude) | Template | 2 — Scope / Objects | What to inspect or change, and what not to |
| Required Analysis | Template | 4 — Analysis Dimensions | Lenses plus the 6-field finding format |
| Evidence Rules | Template | 5 — Evidence Rules | Verified Fact / Inference / Assumption / Unknown |
| Constraints / Guardrails | Template | 3 — Constraints / Guardrails | Do not / Only / Preserve |
| Required Artifacts | Template + Spine | 6 — Artifact Generation | Exact folder and file list, with the purpose of each file |
| Artifact header skeleton | Added | 6 — Artifact Generation | Standard YAML header and sections for every generated file |
| Execution Method | Added | 1 — Action / Mission | Ordered steps so the agent works predictably |
| Completion Gate | Template | 7 — Completion / Quality Gate | Conditions plus PASS / CONDITIONAL PASS / BLOCKED definitions |
| Required Final Response | Template | 7 — Completion / Quality Gate | Seven-part standard response (plus stage-specific items) |
| Prompt Anatomy Coverage | Added | All 8 | Audit table showing where each anatomy component lives |

## 4. Stage index — run order

| # | Stage | Title | Phase | Mode | Writes to | Depends on |
|---|---|---|---|---|---|---|
| 1 | 0A | Pre-Flight Repository & System Orientation | Pre-Flight | DISCOVERY | docs/00-preflight/discovery/ | — |
| 2 | 0B | Provisional Operating Contract & Engineering Boundaries | Pre-Flight | DESIGN | docs/00-preflight/operating-contract/ | 0A |
| 3 | 0C | Provisional Token Efficiency & AI Economics Envelope | Pre-Flight | DESIGN | docs/00-preflight/ai-economics/ | 0A, 0B |
| 4 | 1 | Engage & Qualify | Discover & Frame | DESIGN | docs/01-engagement/ | 0A, 0B, 0C |
| 5 | 2 | Stakeholder Discovery & Authority Confirmation | Discover & Frame | DESIGN | docs/02-stakeholders/ | 0B, 1 |
| 6 | 3 | Frame Problem & Value | Discover & Frame | DESIGN | docs/03-problem-value/ | 1, 2 |
| 7 | 4 | Capture Before-AI / Before-Intervention KPIs | Discover & Frame | DISCOVERY | docs/04-baseline-kpis/ | 2, 3 |
| 8 | 5 | Discover Current Process & Brownfield Landscape | Discover & Frame | DISCOVERY | docs/05-current-state/ | 0A, 3 |
| 9 | 6 | Root-Cause Analysis | Discover & Frame | DESIGN | docs/06-root-cause/ | 3, 4, 5 |
| 10 | 7 | Deep Brownfield Repository Assessment & Behaviour Baseline | Assess & Qualify | VALIDATE | docs/07-repo-assessment/ | 0A, 0B, 5 |
| 11 | 8 | AI-vs-No-AI Qualification | Assess & Qualify | DESIGN | docs/08-ai-qualification/ | 0C, 3, 6, 7 |
| 12 | 9 | Initial PRD / Product Intent | Product & Design | DESIGN | docs/09-initial-prd/ | 3, 6, 8 |
| 13 | 10 | Target Architecture + ADRs | Product & Design | DESIGN | docs/10-architecture/ | 0B, 0C, 7, 8, 9 |
| 14 | 11 | Data, Knowledge & Context Strategy | Product & Design | DESIGN | docs/11-data-context/ | 0B, 10 |
| 15 | 12 | Spec-Driven Design | Product & Design | DESIGN | docs/12-specs/ | 9, 10, 11 |
| 16 | 13 | Requirements → Specs → Tests → Evidence Traceability | Product & Design | DESIGN | docs/13-traceability/ | 9, 12 |
| 17 | 14 | Transformation / Migration Plan | Product & Design | DESIGN | docs/14-transformation/ | 7, 10, 12, 13 |
| 18 | 15 | Transform Bad Repo → Good Repo | Transform the Brownfield | BUILD | docs/15-modernization/ | 0B, 7, 14 |
| 19 | 16 | Validate the Good Repo | Transform the Brownfield | VALIDATE | docs/16-repo-validation/ | 7, 10, 12, 15 |
| 20 | 17 | Finalise Implementation PRD | Transform the Brownfield | DESIGN | docs/17-implementation-prd/ | 9, 10, 16 |
| 21 | 18 | Evidence-Driven Delivery Planning | Plan & Build | DESIGN | docs/18-delivery/ | 12, 13, 17 |
| 22 | 19 | Intelligence Core — Prompt, Retrieval & Model Engineering | Plan & Build | BUILD | docs/19-intelligence/ | 8, 11, 12, 18 |
| 23 | 20 | Application & Services Engineering | Plan & Build | BUILD | docs/20-application/ | 12, 18, 19 |
| 24 | 21 | Enterprise Integration | Plan & Build | BUILD | docs/21-integration/ | 11, 12, 20 |
| 25 | 22 | Agent, Tool, Harness, Loop & Graph Engineering | Plan & Build | BUILD | docs/22-agentic-engineering/ | 8, 0B, 19, 20 |
| 26 | 23 | HITL/HOTL & Deterministic Control Boundaries | Control & Assure | BUILD | docs/23-human-control/ | 0B, 2, 8, 20, 22 |
| 27 | 24 | Security + Privacy + Responsible AI by Design | Control & Assure | BUILD | docs/24-security-privacy/ | 10, 11, 19, 22, 23 |
| 28 | 25 | Governance + Compliance + Assurance | Control & Assure | DESIGN | docs/25-governance/ | 0B, 2, 23, 24 |
| 29 | 26 | TEVV + AI Red Teaming | Control & Assure | VALIDATE | docs/26-tevv/ | 12, 13, 18, 19, 22, 24 |
| 30 | 27 | Production Hardening | Production Readiness & Release | BUILD | docs/27-hardening/ | 24, 26 |
| 31 | 28 | Reliability & Resilience Engineering | Production Readiness & Release | BUILD | docs/28-resilience/ | 10, 21, 22, 26 |
| 32 | 29 | AI Incident Response + BC/DR | Production Readiness & Release | VALIDATE | docs/29-incident-bcdr/ | 24, 28 |
| 33 | 30 | Release / Cutover / Rollback | Production Readiness & Release | BUILD | docs/30-release/ | 14, 26, 27, 29 |
| 34 | 31 | Observability + SLO/SLA Engineering | Production Readiness & Release | BUILD | docs/31-observability/ | 12, 19, 22, 28 |
| 35 | 32 | Token Efficiency + AI FinOps + TCO | Economics & Value | OPERATE | docs/32-finops/ | 0C, 8, 31 |
| 36 | 33 | Vendor / Third-Party / Concentration Risk | Economics & Value | DESIGN | docs/33-vendor-risk/ | 10, 25, 27, 32 |
| 37 | 34 | Measure After-Intervention KPIs | Economics & Value | OPERATE | docs/34-after-kpis/ | 4, 30, 31 |
| 38 | 35 | Before-vs-After Variance + Value Leakage | Economics & Value | OPERATE | docs/35-value-leakage/ | 4, 32, 34 |
| 39 | 36 | ROI / NPV / Benefits Realisation | Economics & Value | OPERATE | docs/36-benefits/ | 32, 35 |
| 40 | 37 | Target Operating Model + RACI + Ownership | Transition & Sustain | DESIGN | docs/37-operating-model/ | 0B, 2, 23, 25 |
| 41 | 38 | Handover + Knowledge Transfer | Transition & Sustain | VALIDATE | docs/38-handover/ | 29, 31, 37 |
| 42 | 39 | Drift + Continuous Improvement | Transition & Sustain | OPERATE | docs/39-continuous-improvement/ | 26, 31, 35 |
| 43 | 40 | Scale / 90-Day Transformation Roadmap | Transition & Sustain | DESIGN | docs/40-scale/ | 26, 35, 36, 39 |
| 44 | 41 | Retirement / Decommissioning | Transition & Sustain | DESIGN | docs/41-retirement/ | 25, 33, 37 |
| 45 | 42 | Executive Defence & Final Value Story | Defend & Baseline | DESIGN | docs/42-executive/ | 4, 8, 10, 26, 35, 36 |
| 46 | FINAL | Authoritative Final As-Built PRD | Defend & Baseline | DESIGN | docs/final-prd/ | 9, 17, 26, 37, 42 |

File names follow the pattern `<stage-number>_<Stage-Title>.md`; see the `stage-prompts/` folder.

## 5. Operating modes

Every prompt declares exactly one operating mode. The mode is the agent's write permission for that stage.

| Mode | What the agent may do | Stages |
|---|---|---|
| DISCOVERY — READ-ONLY | Inspect, read and analyse only. Do not modify application code, tests, dependencies, configuration, infrastructure, data or workflows. The only permitted writes are the artifacts listed below, under this stage's `docs/` folder. | 0A, 4, 5 |
| DESIGN — DOCUMENTATION-ONLY | Produce analysis, decisions, designs and specifications as version-controlled documents. Do not change implementation code, configuration, infrastructure or data. Writes are limited to this stage's `docs/` folder. | 0B, 0C, 1, 2, 3, 6, 8, 9, 10, 11, 12, 13, 14, 17, 18, 25, 33, 37, 40, 41, 42, FINAL |
| VALIDATE — EXECUTE & OBSERVE | Execute tests, scans, evaluations, exercises and comparisons. Do not change implementation, thresholds or datasets to make results pass — record failures as findings and route them to remediation. Writes are limited to this stage's `docs/` folder and test/evaluation outputs. | 7, 16, 26, 29, 38 |
| BUILD — SCOPED WRITE | Implementation changes are permitted only within the repository-write, environment and data boundaries approved in Stage 0B (as updated in Stages 2, 23 and 25) and only to deliver approved specifications. Work in small, reviewable, reversible increments and run relevant tests after every increment. Never touch production directly. | 15, 19, 20, 21, 22, 23, 24, 27, 28, 30, 31 |
| OPERATE — MEASURE & GOVERN | Work from production telemetry, operational records and approved evidence. Do not change production systems, metric definitions or controls. Any recommended change goes through the controlled change process with human approval. | 32, 34, 35, 36, 39 |

> **Note:** Code is changed only in BUILD stages, and only within the Stage 0B boundaries (as later confirmed in Stages 2, 23 and 25). Configure your agent's tool permissions to match the mode before each run.

## 6. How to run one stage — step by step

1. **Prepare the repository.** Make sure the target repository has a `docs/` folder (the stage creates its own sub-folder) and is under version control. Commit before every stage run.
2. **Open the stage file** from `stage-prompts/`, e.g. `07_Deep-Brownfield-Repository-Assessment-and-Behaviour-Baseline.md`.
3. **Fill the Engagement Context placeholders**: `{{CLIENT_NAME}}`, `{{ENGAGEMENT_NAME}}`, `{{REPO_ROOT}}`, `{{RUN_DATE}}`, `{{AGENT_NAME}}`, `{{ARTIFACT_VERSION}}`, `{{PRIOR_STAGE_ARTIFACTS}}`. You can edit them in the file or send them as the first user message.
4. **Load the whole file as the system prompt** (system message, custom instructions, project instructions or agent definition). Do not trim sections; the guardrails and gate depend on them.
5. **Grant access** to the repository and to the prior-stage `docs/` folders listed under *Lifecycle Linkage → Consumes*. Set tool permissions to match the Operating Mode.
6. **Send the trigger message:** `Execute Stage <ID>.` You can add stage-specific inputs, e.g. stakeholder notes for Stage 2 or KPI data extracts for Stage 4.
7. **Review the Required Final Response.** Check the stage status, the blocking issues and the list of artifacts created.
8. **Apply the gate decision** (Section 7). Commit the artifacts with a message such as `stage-07: repo assessment v0.1 (CONDITIONAL PASS)`.
9. **Move to the next stage** shown in `next_stage` in the YAML header.

## 7. Gate decisions — what to do next

| Status returned | Meaning | Your action |
|---|---|---|
| PASS | Every gate condition is met with evidence | Commit artifacts and run the next stage |
| CONDITIONAL PASS | No blocking gaps; non-blocking gaps documented with owner, due date and risk | Commit, log the conditions in your tracker, proceed, and re-verify the conditions at the stage named as their resolver |
| BLOCKED | At least one blocking condition remains | Do not proceed. Resolve the named blocker (more evidence, a stakeholder decision, approval) and re-run the same stage with a bumped `{{ARTIFACT_VERSION}}` |

Re-runs never silently overwrite evidence. Bump the version (v0.1 → v0.2) and let the artifact's *Change History* and `supersedes` field record what changed.

## 8. Critical cross-stage threads

Some stages create commitments that later stages must honour. Keep these threads in mind when reviewing outputs.

| Thread | Created in | Confirmed / used in | What to watch |
|---|---|---|---|
| Provisional governance | 0B | 2, 23, 25 → closed in 37 | Items marked PROVISIONAL must be confirmed or updated, never assumed |
| AI economics | 0C | 8 (reconcile) → 32 (actuals) | Stage 8 retires irrelevant AI cost assumptions; Stage 32 compares against the applicable scenario |
| AI-vs-No-AI decision | 8 | 10, 19, 22, 32 | Controls whether Stages 19 and 22 build anything, and how Stage 32 measures cost |
| Frozen KPI baseline | 4 | 34 → 35 → 36 | Definitions are frozen; Stages 34–36 must not redefine KPIs |
| Behaviour baseline | 7 | 15 (preserve) → 16 (compare) | Every behaviour difference must be explained in Stage 16 |
| PRD lineage | 9 | 17 (implementation) → FINAL (as-built) | FINAL dispositions every Stage 9 requirement: Delivered / Changed / Deferred / Rejected / Superseded |
| Traceability | 13 | 18, 26, FINAL | Requirement → spec → test → evidence must stay intact |
| Human control | 0B | 23 → 37 | Autonomy matrix and never-delegate actions carry into the operating model |

## 9. Conditional stages

- **Stage 19 — Intelligence Core:** if Stage 8 selected *No-AI*, the agent writes `not-applicable.md` with the justification and stops.
- **Stage 22 — Agentic Engineering:** runs only if Stage 8 justified agentic behaviour. Otherwise the agent writes only `not-applicable.md`, and no agent artifacts are invented.
- **Stage 32 — FinOps:** if Stage 8 rejected AI, the stage measures platform and infrastructure economics instead of token metrics.
- **Agent-specific artifacts** in Stages 31, 37, 39 and FINAL are marked *(or N/A)*: they record N/A with the Stage 8 reference when there are no agents.

## 10. Ways to use the prompts

### 10.1 Chat assistant (Claude / ChatGPT / Copilot)

1. Create one project or workspace per engagement.
2. Paste the stage file into the project instructions (or custom instructions) for that stage's conversation.
3. Attach or connect the repository and the prior `docs/` artifacts.
4. Send `Execute Stage <ID>.` and save the artifacts it produces into the repository.

### 10.2 Coding agent (Claude Code, GitHub Copilot agent, Cursor)

Store the prompts in the repository so every run is reproducible, for example under `.fde/stage-prompts/`. Start a fresh session per stage and pass the stage file as the system prompt or agent definition, e.g.:

```
claude --append-system-prompt "$(cat .fde/stage-prompts/07_Deep-Brownfield-Repository-Assessment-and-Behaviour-Baseline.md)" \
       "Execute Stage 7."
```

Use a separate git branch per BUILD stage (15, 19–22, 24, 27, 28, 30, 31) so changes are reviewable through a pull request.

### 10.3 API (Python — Azure OpenAI / Anthropic)

```
from pathlib import Path

PROMPTS = Path("stage-prompts")

def load_stage(stage_file: str, ctx: dict) -> str:
    text = (PROMPTS / stage_file).read_text(encoding="utf-8")
    for key, value in ctx.items():               # fill {{PLACEHOLDERS}}
        text = text.replace("{{" + key + "}}", value)
    return text

ctx = {"CLIENT_NAME": "Contoso Health", "ENGAGEMENT_NAME": "Claims Triage Assistant",
       "REPO_ROOT": "/repos/claims-triage", "RUN_DATE": "2026-10-17",
       "AGENT_NAME": "fde-agent", "ARTIFACT_VERSION": "v0.1",
       "PRIOR_STAGE_ARTIFACTS": "/repos/claims-triage/docs"}

system_prompt = load_stage("00A_Pre-Flight-Repository-and-System-Orientation.md", ctx)

# Azure OpenAI
# resp = client.chat.completions.create(model=DEPLOYMENT, messages=[
#     {"role": "system", "content": system_prompt},
#     {"role": "user", "content": "Execute Stage 0A."}])

# Anthropic
# resp = client.messages.create(model=MODEL, max_tokens=16000, system=system_prompt,
#     messages=[{"role": "user", "content": "Execute Stage 0A."}])
```

### 10.4 Orchestrated pipeline (LangGraph)

Model the spine as a graph: one node per stage, with a conditional edge on the gate status.

- Each node loads its stage file, runs the agent with tools scoped to the stage's Operating Mode, and parses the stage status from the Required Final Response.
- **PASS / CONDITIONAL PASS** → edge to `next_stage`. **BLOCKED** → edge to a human-review interrupt, then re-run the same node.
- Route around Stages 19 and 22 when the Stage 8 decision is No-AI (they still emit `not-applicable.md`).
- Keep a human-approval interrupt before every BUILD stage and before Stage 30 (Release).

## 11. Placeholder reference

| Placeholder | Example | Used for |
|---|---|---|
| {{CLIENT_NAME}} | Contoso Health | Artifact headers and context |
| {{ENGAGEMENT_NAME}} | Claims Triage Assistant | Engagement identity |
| {{REPO_ROOT}} | /repos/claims-triage | Where the agent reads code |
| {{RUN_DATE}} | 2026-10-17 | Artifact `date` |
| {{AGENT_NAME}} | fde-agent-01 | Artifact `author_agent` |
| {{ARTIFACT_VERSION}} | v0.1 | Artifact `version`; bump on re-run |
| {{PRIOR_STAGE_ARTIFACTS}} | /repos/claims-triage/docs | Where upstream evidence lives |

## 12. Corrections made to the source artifact names

In the Delivery Spine PDF, the table layout split many artifact file names across lines, inserting commas, stray spaces or the word "and". The prompts use the corrected names below. Please confirm them against your master copy.

| Stage | As extracted from PDF | Used in prompt |
|---|---|---|
| 0A | security-observability, overview.md | security-observability-overview.md |
| 0B | docs/00-preflight/operatingcontract/ | docs/00-preflight/operating-contract/ |
| 0B | provisional-operating, contract.md · repository-write, boundaries.md · environment-accessboundaries.md | provisional-operating-contract.md · repository-write-boundaries.md · environment-access-boundaries.md |
| 0B | provisional-tool-agentpermissions.md · provisional-human-approval, rules.md · operating-contractand readiness.md | provisional-tool-agent-permissions.md · provisional-human-approval-rules.md · operating-contract-readiness.md |
| 0C | docs/00-preflight/aieconomics/ | docs/00-preflight/ai-economics/ |
| 0C | provisional-model-call, inventory.md · provisional-contextbudget.md · quality-latency-costenvelope.md · preliminary-finops, baseline.md | provisional-model-call-inventory.md · provisional-context-budget.md · quality-latency-cost-envelope.md · preliminary-finops-baseline.md |
| 1 | open-qualificationand questions.md | open-qualification-questions.md |
| 2 | operating-contract. confirmations.md | operating-contract-confirmations.md |
| 6 | evidence-confidencematrix.md | evidence-confidence-matrix.md |
| 7 | partial-migrationregister.md · critical-workflowinventory.md · characterization-testplan.md · security-code-qualityfindings.md · maintainabilityand assessment.md · repo-transformation. readiness.md | partial-migration-register.md · critical-workflow-inventory.md · characterization-test-plan.md · security-code-quality-findings.md · maintainability-assessment.md · repo-transformation-readiness.md |
| 8 | deterministic-vs-aiboundaries.md · minimum-intelligenceassessment.md · economics-baselinereconciliation.md | deterministic-vs-ai-boundaries.md · minimum-intelligence-assessment.md · economics-baseline-reconciliation.md |
| 10 | architecture-riskregister.md · architecture-decisionsummary.md | architecture-risk-register.md · architecture-decision-summary.md |
| 11 | context-engineering, strategy.md | context-engineering-strategy.md |
| 13 | requirements-traceability, matrix.md | requirements-traceability-matrix.md |
| 15 | behavior-preservation, evidence.md | behavior-preservation-evidence.md |
| 16 | architecture-conformance, report.md · behavior-differencereport.md | architecture-conformance-report.md · behavior-difference-report.md |
| 17 | finalized-acceptancecriteria.md · implementation-baselinesignoff.md | finalized-acceptance-criteria.md · implementation-baseline-signoff.md |
| 19 | quality-latency-costand results.md | quality-latency-cost-results.md |
| 20 | error-handlingimplementation.md · access-controlimplementation.md | error-handling-implementation.md · access-control-implementation.md |
| 23 | deterministic-controlrules.md · operating-contractand updates.md · human-control-testresults.md | deterministic-control-rules.md · operating-contract-updates.md · human-control-test-results.md |
| 25 | operating-contractgovernance-updates.md | operating-contract-governance-updates.md |
| 27 | production-readinessand checklist.md | production-readiness-checklist.md |
| 28 | graceful-degradation, design.md | graceful-degradation-design.md |
| 30 | environment-promotion, plan.md | environment-promotion-plan.md |
| 31 | observability- save architecture.md | observability-architecture.md |
| 32 | production-token-dashboard, spec.md · baseline-vs-actual-tokenanalysis.md | production-token-dashboard-spec.md · baseline-vs-actual-token-analysis.md |
| 33 | third-party-riskassessment.md · data-processingdependencies.md · concentration-riskanalysis.md | third-party-risk-assessment.md · data-processing-dependencies.md · concentration-risk-analysis.md |
| 34 | after-intervention-kpisheet.md · production-performance, report.md | after-intervention-kpi-sheet.md · production-performance-report.md |
| 36 | benefits-realisationdashboard-spec.md | benefits-realisation-dashboard-spec.md |
| 37 | operating-contract. closure.md | operating-contract-closure.md |
| 38 | handover-acceptance. signoff.md | handover-acceptance-signoff.md |
| 39 | docs/39-continuousimprovement/ · prompt-model-driftmetrics.md · continuous-evaluation, plan.md | docs/39-continuous-improvement/ · prompt-model-drift-metrics.md · continuous-evaluation-plan.md |
| 40 | adjacent-use-caseinventory.md · reuse-readiness, assessment.md | adjacent-use-case-inventory.md · reuse-readiness-assessment.md |
| FINAL | requirement-dispositionmatrix.md · final-api-interface, baseline.md · final-data-knowledgebaseline.md · final-security-governance, baseline.md · final-acceptance-evidencemap.md · final-operating, boundaries.md · final-product-baseline. signoff.md | requirement-disposition-matrix.md · final-api-interface-baseline.md · final-data-knowledge-baseline.md · final-security-governance-baseline.md · final-acceptance-evidence-map.md · final-operating-boundaries.md · final-product-baseline-signoff.md |

**Naming interpretations added for clarity** (not explicit in the source): ADRs are named `adrs/ADR-NNN-<decision>.md` (Stage 10); feature specs are named `features/<feature>.md` (Stage 12); and Stages 19 and 22 write `not-applicable.md` when Stage 8 rules them out.

## 13. Good practice

- **Run one stage per session.** A clean context per stage keeps the agent focused and makes gates auditable.
- **Never skip a stage silently.** If a stage truly does not apply, run it anyway and let it record N/A with justification.
- **Keep humans on the gates.** The agent proposes PASS / CONDITIONAL PASS / BLOCKED; an accountable person accepts it.
- **Treat prompts as code.** Version the `stage-prompts/` folder. If you tailor a prompt for a client, change the copy in that client's repository and record why.
- **Do not loosen guardrails to get unstuck.** A BLOCKED status is a finding, not a failure. Resolve the evidence gap instead.
- **Tailor safely.** Add client-specific scope, tools or regulations in the *Scope* and *Constraints* sections. Do not remove the Evidence Rules, Completion Gate or Required Final Response.
