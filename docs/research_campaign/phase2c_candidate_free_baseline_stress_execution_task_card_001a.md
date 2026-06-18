# Phase2C Candidate-Free Baseline Stress Execution Task Card 001A

Task ID:
`RESEARCH-CAMPAIGN-PHASE2C-CANDIDATE-FREE-BASELINE-STRESS-EXECUTION-001A`

Status: opened for bounded implementation and execution.

Parent reviewed contract:
`docs/research_campaign/phase2c_candidate_free_baseline_stress_task_card_001a.md`

Parent validation:
`artifacts/research_campaign/phase2c_candidate_free_baseline_stress_task_card_validation_001a.json`

Parent audit:
`artifacts/research_campaign/phase2c_candidate_free_baseline_stress_task_card_audit_001a.json`

## Problem Definition

The reviewed Phase2C baseline-stress task card authorizes a later bounded
checkpoint to implement and run candidate-free baseline stress. The immediate
problem is to execute that stress without starting candidate mechanism work,
Phase 3, route tournament, runtime/EGO mainline work, push, tag, remote anchor,
terminal verdict, or route-exhaustion claim.

The current evidence is still under-stressed: one fixed run, 12 trace rows, and
random/lookup-family baselines tied the strongest fair macro accuracy. This
checkpoint must measure whether that apparent surface headroom survives a
larger candidate-free stress battery.

## Current Stage And Layer

Current stage:
`phase2c_candidate_free_baseline_stress_execution`

Layer:
`engineering_implementation + mechanism_hypothesis_governance`

Mainline integration status: none.

Enabled status: local candidate-free baseline-stress implementation and
execution only.

Real trigger evidence: parent task-card validation passed, parent read-only
audit returned `success_reached`, and the user explicitly authorized running
the reviewed stress path.

Claim ceiling: candidate-free Phase2C baseline-stress execution evidence only.
This cannot prove candidate validity, mechanism validity, learning/adaptation
success, subjectivity, consciousness, real emotion, autonomy, EGO readiness,
companion readiness, runtime/mainline effect, route exhaustion, terminal
verdict, or program completion.

Auto-Remote-Anchor: forbidden.

## Bounded Audit Before Implementation

Real objective: run a larger candidate-free stress battery that can falsify
the current hidden-latent surface before any candidate mechanism work.

Problem-definition risk: stress implementation could accidentally become a
candidate route or weaken baselines. It must stay a wrapper over candidate-free
surface generation, baseline battery, leakage, replay, ablation, provenance,
and aggregate verdict computation.

Strongest baseline explanation: if random, lookup, graph-cache,
transition-table, successor-map, FSM planner, episodic traversal,
trace-only replay, exhaustive legal query, or observation-only behavior reaches
oracle-equivalent performance or ties strongest after stress aggregation, the
surface still lacks interpretable candidate headroom.

Strongest invalidating reason: if the stress wrapper drops any baseline,
changes the access boundary, leaks hidden labels, skips replay recomputation,
uses static verdict dictionaries, or fails to consume ablations/provenance, its
result is invalid even if tests pass.

Falsifier for current framing: aggregate stress records baseline saturation,
random or lookup-family strongest tie, leakage positive-control failure,
replay recomputation failure, missing provenance, or unconsumed ablations.

Evidence still insufficient: a clean candidate-free stress run does not
validate any candidate mechanism and does not open Phase 3 by itself. A
post-result route check is required before candidate work.

Mechanism-vs-behavior classification: this task tests baseline-resistant
environment headroom only. It does not test a mechanism.

Hard-coding / leakage / weak-baseline checks:

- no candidate mechanism implementation;
- no Phase 3 mechanism search;
- no route tournament;
- no edits to `src/phase2c_hidden_latent_harness_001a/`;
- no mutation of repaired or invalid Phase2C output artifacts;
- no baseline removal or access-boundary weakening;
- no threshold tuning after stress results;
- no static pass verdict or hand-written score;
- no runtime, EGO mainline, UI, LLM, AIRI, deployment, push, tag, or remote
  anchor;
- no terminal verdict or route-exhaustion claim.

## Collision Record

### Candidate A: Rerun old repaired harness with larger output path

Evidence it would produce: another single-seed run from the prior harness.

Strongest cheap baseline that could match it: the same random and lookup-family
ties already recorded.

Leakage / hard-coding risk: low, but it fails the stress contract.

Smallest falsifying test: seed count remains 1 or trace rows remain 12.

Expected failure mode: repeat evidence is mistaken for stress evidence.

Decision: rejected.

### Candidate B: Thin stress wrapper around existing callable producers

Evidence it would produce: multi-seed candidate-free stress using the already
audited surface, baseline, leakage, replay, ablation, and provenance functions,
with aggregate/per-seed reporting and fresh artifacts.

Strongest cheap baseline that could match it: the full existing baseline
battery under equal candidate-visible access.

Leakage / hard-coding risk: medium; must preserve hidden-label isolation and
positive controls.

Smallest falsifying test: missing required baselines, seed count below 5,
wrong family/episode counts, output artifact omissions, or candidate flag true.

Expected failure mode: the surface collapses under broader stress.

Decision: selected.

### Candidate C: Modify the original Phase2C runner directly

Evidence it would produce: stress support inside the older runner.

Strongest cheap baseline that could match it: same as Candidate B.

Leakage / hard-coding risk: higher because it mutates already-audited source
and risks invalidating previous evidence boundaries.

Smallest falsifying test: diff touches `src/phase2c_hidden_latent_harness_001a/`.

Expected failure mode: prior evidence boundary is blurred.

Decision: rejected.

## Mainline Target

None. This task has no runtime, EGO mainline, UI, LLM, AIRI, external service,
deployment, product, or companion target.

## Enabled-State Requirement

Enabled actions:

- create this execution task card;
- implement a candidate-free stress wrapper under
  `src/phase2c_candidate_free_baseline_stress_001a/`;
- add focused tests under
  `tests/phase2c_candidate_free_baseline_stress_001a/`;
- run the candidate-free stress wrapper;
- write artifacts under `artifacts/phase2c_candidate_free_baseline_stress_001a/`;
- write campaign summary and audit artifacts under `artifacts/research_campaign/`;
- update `docs/research_campaign/plan.md`;
- update `docs/OVERALL_PROGRESS.md`;
- update `artifacts/research_campaign/stage_scorecard.json`;
- append `artifacts/research_campaign/experiment_log.jsonl`;
- create one local commit after validation and audit pass, using exact path
  staging only.

No candidate mechanism, Phase 3, route tournament, runtime/EGO mainline, push,
tag, or remote anchor is enabled.

## Real-Trigger Evidence Requirement

Execution must read and record:

- repo root, branch, HEAD, upstream/ahead-behind, and
  `git status --short --branch -uall`;
- this execution task card;
- parent task card, validation, and audit artifacts;
- `docs/research_campaign/goal_stage_audit_loop_001a.md`;
- `docs/research_campaign/plan.md`;
- `docs/OVERALL_PROGRESS.md`;
- `artifacts/research_campaign/stage_scorecard.json`;
- `artifacts/research_campaign/experiment_log.jsonl`;
- source route-check artifact and audit;
- prior repaired result, baseline, and trace artifacts.

## Hypothesis

If apparent Phase2C headroom was mainly a low-row fixed-run artifact, then
multi-seed candidate-free stress will either record baseline collapse or
preserve only a bounded headroom signal requiring a later route check.

## Strongest Baseline

The stress wrapper must invoke the full baseline battery:

- random;
- majority;
- observation-only;
- lookup;
- count table;
- transition table;
- graph cache;
- successor map;
- nearest neighbor;
- FSM planner;
- episodic traversal;
- trace-only replay;
- exhaustive legal query.

The strongest fair baseline is the maximum aggregate macro accuracy over the
full battery. If any baseline reaches oracle-equivalence under the declared
equivalence band, record no-headroom. If random or lookup-family baselines tie
strongest after aggregation, record candidate work blocked pending redesign or
route check.

## Ablation Requirement

The stress wrapper must invoke and consume the existing ablation battery for
each seed surface:

- memory deletion;
- source-memory deletion;
- latent-rule swap;
- heldout task-family transfer;
- cross-episode reset;
- exploration-budget ablation;
- partial-observation ablation;
- observation-field masking;
- spurious-token injection/removal.

Stored-score mutation and static verdict dictionaries are invalid.

## Trace / Replay Requirement

The stress wrapper must write non-empty trace rows for every stressed episode.
Replay must recompute from:

```text
serialized_state + current_observation + legal_action_or_query_schema + budget_state + latent_belief_or_memory_state
```

Stored-output comparison or hash-only comparison is insufficient.

## Computed-Evidence Provenance Gate

Every score-bearing result must record producer function, input artifact,
run ID, seed/context/episode IDs, aggregation rule, and code path hash.

The final campaign summary must record:

- stress seeds;
- train/heldout family counts;
- episodes per family;
- total trace rows;
- baseline IDs;
- aggregate strongest fair baseline ID and macro accuracy;
- baseline IDs tying strongest;
- whether random ties strongest;
- whether lookup-family baselines tie strongest;
- oracle macro accuracy;
- equivalence band;
- candidate, Phase 3, route tournament, runtime/mainline, push/tag/remote
  flags;
- source hashes;
- claim ceiling;
- next minimal closed-loop action.

## Acceptance Gate

This checkpoint is accepted only if:

- this execution task card exists and validates;
- focused tests show the stress wrapper enforces at least 5 seeds, 3 train
  families, 3 heldout families, 4 episodes per family, full baseline battery,
  non-empty trace, positive-control leakage scan, replay recomputation,
  ablation consumption, and provenance;
- TDD red failure is preserved before implementation;
- stress execution writes all required output artifacts;
- campaign summary artifact exists and parses;
- read-only audit returns `success_reached`, or failure is preserved;
- no candidate mechanism is run;
- Phase 3 remains unopened;
- route tournament remains unauthorized;
- runtime/EGO mainline, push, tag, remote anchor, terminal verdict, and
  route-exhaustion claims remain blocked;
- plan/progress/scorecard/ledger agree on the result and next route.

## Stop Conditions

Stop and preserve a failure if:

- the stress wrapper edits `src/phase2c_hidden_latent_harness_001a/`;
- any required baseline is missing;
- seed count, family count, or episode count is below the contract;
- trace rows are empty or below the expected minimum;
- leakage positive controls fail;
- replay recomputation fails or uses stored outputs only;
- ablations are not consumed;
- provenance is missing or static;
- candidate mechanism, Phase 3, route tournament, runtime/EGO mainline, push,
  tag, remote anchor, terminal verdict, or route-exhaustion claim is attempted.

## Rollback Plan

If implementation, execution, validation, or audit fails, keep the failure
artifact and dirty-path classification, preserve generated evidence, and record
the blocker in `plan.md`, `docs/OVERALL_PROGRESS.md`,
`artifacts/research_campaign/stage_scorecard.json`, and
`artifacts/research_campaign/experiment_log.jsonl`.

Do not delete prior route-check, repaired-output, invalid-output, audit,
baseline, or negative-evidence records.

## Expected Changed Files

- `docs/research_campaign/phase2c_candidate_free_baseline_stress_execution_task_card_001a.md`
- `src/phase2c_candidate_free_baseline_stress_001a/__init__.py`
- `src/phase2c_candidate_free_baseline_stress_001a/runner.py`
- `tests/phase2c_candidate_free_baseline_stress_001a/test_phase2c_candidate_free_baseline_stress_001a.py`
- `artifacts/phase2c_candidate_free_baseline_stress_001a/result.json`
- `artifacts/phase2c_candidate_free_baseline_stress_001a/trace.jsonl`
- `artifacts/phase2c_candidate_free_baseline_stress_001a/baseline_comparison.json`
- `artifacts/phase2c_candidate_free_baseline_stress_001a/ablation_report.json`
- `artifacts/phase2c_candidate_free_baseline_stress_001a/replay_report.json`
- `artifacts/phase2c_candidate_free_baseline_stress_001a/leakage_report.json`
- `artifacts/phase2c_candidate_free_baseline_stress_001a/computed_evidence_provenance.json`
- `artifacts/phase2c_candidate_free_baseline_stress_001a/failure_manifest.json`
- `artifacts/research_campaign/phase2c_candidate_free_baseline_stress_execution_task_card_validation_001a.json`
- `artifacts/research_campaign/phase2c_candidate_free_baseline_stress_001a.json`
- `artifacts/research_campaign/phase2c_candidate_free_baseline_stress_audit_001a.json`
- `docs/research_campaign/plan.md`
- `docs/OVERALL_PROGRESS.md`
- `artifacts/research_campaign/stage_scorecard.json`
- `artifacts/research_campaign/experiment_log.jsonl`

## Forbidden Changes

- No edits to `src/phase2c_hidden_latent_harness_001a/`.
- No mutation of prior repaired or invalid Phase2C output artifacts.
- No candidate mechanism implementation.
- No Phase 3 mechanism search.
- No route tournament.
- No runtime, EGO mainline, UI, LLM, AIRI, external service, deployment,
  push, tag, or remote anchor.
- No program terminal verdict or route-exhaustion claim.
- No deletion, rewriting, or weakening of prior negative, repair, audit, or
  baseline evidence.
- No `git add -A`; local staging must use exact paths only.

## Auto-Remote-Anchor Decision

Auto-Remote-Anchor: forbidden.

Push, tag, and remote anchor are not authorized by this task card.

## Local Commit Decision

Local commit: authorized after focused validation and read-only audit pass, but
only for the exact expected changed files listed in this card.

## Next Minimal Closed-Loop Action

Validate this execution task card, add a failing stress-wrapper test, implement
the minimal candidate-free stress wrapper, run it, validate/audit the produced
artifacts, and then open a post-result route check before any candidate
mechanism work.
