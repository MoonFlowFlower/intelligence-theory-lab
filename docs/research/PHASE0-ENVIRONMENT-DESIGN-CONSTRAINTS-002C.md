# PHASE0-ENVIRONMENT-DESIGN-CONSTRAINTS-002C

Status: recorded design-constraint synthesis.

Auto-Remote-Anchor: forbidden.

## Verdict

`design_constraints_002c_recorded`

This record synthesizes closed Phase-0 environment failures from
`BASELINE-FIRST-HARNESS-001A-R1`, `BATCH-ENV-HEADROOM-SCOUT-002A`, and
`BATCH-ENV-HEADROOM-SCOUT-002B` into constraints for a later
`BATCH-ENV-HEADROOM-SCOUT-003A` sketch generator.

This task did not generate new environment sketches, run a scout, run a full
harness, implement candidates, or wire runtime/mainline/admission/bridge paths.

## Current Layer

engineering-governance / Phase-0 environment design-constraint synthesis.

## Mainline Integration Status

none.

## Enabled Status

no runtime/mainline/admission/bridge path enabled.

## Real Trigger Evidence

The synthesis is based on repo-local readback of:

- `docs/research/BASELINE-FIRST-HARNESS-001A-R1-ACCEPTED-NO-HEADROOM-CLOSEOUT-001A.md`
- `artifacts/baseline_first_harness_001a/final_verdict.json`
- `artifacts/CLAUDE-INDEPENDENT-BASELINE-FIRST-HARNESS-001A-R1-EVIDENCE-INTEGRITY-HOSTILE-AUDIT-001A/audit_result.json`
- `docs/research/BATCH-ENV-HEADROOM-SCOUT-002A-FALSE-PROMOTION-CLOSEOUT-001A.md`
- `artifacts/batch_env_headroom_scout_002a_false_promotion_closeout_001a/closeout_record.json`
- `docs/research/BATCH-ENV-HEADROOM-SCOUT-002B-INDEPENDENT-STATIC-AND-COMPUTE-BASELINE-SCOUT-TASK-CARD-001A.md`
- `artifacts/batch_env_headroom_scout_002b/final_report.md`
- `artifacts/batch_env_headroom_scout_002b/rejected_sketches.json`
- `artifacts/batch_env_headroom_scout_002b/micro_probe_results.json`
- `docs/research/PHASE0-ENVIRONMENT-ATTACK-LIBRARY-001A.md`

## Failure Taxonomy

### 001A no-headroom legal-channel / belief-planner saturation

`BASELINE-FIRST-HARNESS-001A-R1` is accepted bounded negative environment
evidence. Its callable verdict was `rejected_no_headroom_baseline_saturated`.
The visible-channel oracle score was `1.0`, strongest fair baseline score was
`1.0`, the strongest fair baseline was `budget_limited_belief_state_planner`,
oracle-minus-baseline margin was `0.0`, and all six graph-cache challenger
scores were `1.0`.

Design implication: a future surface must not make the target exactly recoverable
by budget-respecting legal-channel readers, belief-state planners, or graph/cache
families. Merely adding more candidate-side complexity cannot create headroom
when the environment itself is saturated by cheap fair routes.

### 002A false promotion by direct legal-channel compute

`BATCH-ENV-HEADROOM-SCOUT-002A` is closed as
`blocked_promotion_false_positive_direct_decode`. The promoted
`relational_contrast_budget_probe` used a visible oracle that read
`contrast_a`, `contrast_b`, and `phase_probe` under budget 3 and applied
`(a + 2b + phase) % 3`. That oracle was itself a fair legal-channel compute
baseline, but the same computation was not scored on the fair-baseline side.

Design implication: oracle-as-baseline symmetry is mandatory. If the oracle
uses only budget-visible legal channels, the same computation must be registered
as a baseline and any oracle-band result rejects the sketch rather than
promoting it.

### 002B repaired scout all-rejected result

`BATCH-ENV-HEADROOM-SCOUT-002B-RUN-001A` returned
`all_rejected_static_or_microprobe`: 7 sketches registered, 3 static rejections,
4 micro-probed, 0 promoted full-harness candidates, 7 total rejections.

The observed closed families were:

- direct legal-channel compute: `direct_legal_channel_compute` rejected by
  independent static scan as `reject_direct_decode`.
- answer-key oracle: `answer_key_oracle_surface` rejected by independent static
  scan as `reject_oracle_not_budget_faithful`.
- metric degeneracy: `metric_degenerate_predict_all_surface` rejected by
  independent static scan as `reject_metric_degenerate`.
- graph/cache saturation: `graph_cache_transition_surface` rejected by
  micro-probe as `reject_graph_cache_saturated`.
- lookup-vs-compute artifact: `lookup_split_compute_artifact` rejected by
  micro-probe as `reject_no_headroom_likely`; lookup failure did not matter
  because exhaustive legal query and fitted legal-channel learner reached
  oracle band.
- underpowered surface: `low_signal_underpowered_surface` rejected by micro-probe
  as `reject_underpowered_surface`.
- passive value leakage: `passive_value_leak_surface` rejected by micro-probe as
  `reject_passive_decodable`.

Design implication: 003A must generate fewer sketches with stronger
predeclared constraints rather than many random variants. A sketch is not
interesting unless it has a plausible budget-faithful oracle strategy, enough
oracle signal, and a concrete reason the strongest false explanations A1-A9 do
not already solve or invalidate the surface.

## Forbidden Surface Patterns

The next batch generator must reject or refuse to emit surfaces with these
patterns:

- target deterministic from <= budget legal/visible channels;
- oracle computes a legal-channel formula not mirrored as a fair baseline;
- train/test split defeats memory but not compute;
- state/signature space small enough for graph/cache/table saturation;
- metric allows `predict_all`, `predict_none`, constant-k, random, majority, or
  size-only predictors to score high;
- passive visible values encode target;
- oracle needs `hidden_state`, `answer_key`, future labels, or unqueried values;
- signal is too weak for the budget-faithful oracle to clear the oracle floor;
- baseline battery relies on aliases or omits fitted/classical compute;
- any proposed positive case depends on missing baselines, omitted graph/cache
  family members, or lookup failure alone.

## Required Positive Properties For 003A

Each later 003A sketch must predeclare all of the following before any run:

- target is not exactly computable from <= budget legal channels;
- oracle is high because of a legitimate budget-faithful partial-observation
  strategy, not hidden/answer/future access;
- exhaustive legal query within budget leaves nontrivial remaining uncertainty;
- graph/cache/table baselines are structurally disadvantaged on heldout
  generalization, not merely absent;
- fitted legal-channel learner and strongest applicable classical method are
  included and expected to remain below the visible oracle;
- passive value-decoder family is expected below ceiling by value-level analysis;
- balanced macro-F1 metric with per-class precision/recall floor is required;
- train/test split defeats both memorization and simple legal-channel compute;
- visible oracle signal is expected to exceed the oracle floor;
- strongest false explanation is stated before any run and mapped to A1-A9.

The positive grammar is not "make baselines weaker." It is: design surfaces where
the legal budget gives a real but incomplete partial-observation channel, where
the oracle earns score through budget-faithful information gathering, and where
cheap fair baselines remain fully present and fail for structural reasons.

## Next-Batch Generation Brief

`BATCH-ENV-HEADROOM-SCOUT-003A`, if separately authorized, should generate 6 to
10 higher-quality sketches, not 20 random variants. Each sketch must include:

- A1-A9 self-attack mapping explaining why the sketch is not statically killed;
- candidate-free oracle strategy and field-access manifest;
- expected strongest cheap baseline and why it should remain below oracle;
- explicit fitted/classical learner expectation;
- passive value-level leakage expectation;
- graph/cache heldout-generalization resistance expectation;
- metric robustness declaration;
- signal-floor expectation;
- no candidate implementation;
- micro-probe only;
- promotion only to a separate full baseline-first harness task card.

## Stop Conditions

Stop and record `blocked_no_valid_environment_design_grammar` for a future
design step if the only available way to produce a gap is to weaken, omit, alias,
or underpower baselines, or if no surface can satisfy budget-faithful oracle
signal plus resistance to A1-A9.

## Generated Artifacts

- `artifacts/phase0_environment_design_constraints_002c/failure_taxonomy.json`
- `artifacts/phase0_environment_design_constraints_002c/design_constraints.json`
- `artifacts/phase0_environment_design_constraints_002c/forbidden_surface_patterns.json`
- `artifacts/phase0_environment_design_constraints_002c/required_positive_properties.json`
- `artifacts/phase0_environment_design_constraints_002c/next_batch_generation_brief.json`

## Claim Ceiling

Phase-0 environment design-constraint synthesis only.

No headroom confirmation. No Gate1 pass. No mechanism validity. No candidate
feasibility. No runtime/mainline effect. No agency, autonomy, consciousness, or
EGO readiness.

## Next Minimal Closed-Loop Action

Review these design constraints. Authorize `BATCH-ENV-HEADROOM-SCOUT-003A` only
if this 002C brief is accepted as a concrete next-batch generation constraint
set.

## What This Does Not Prove

This does not prove that any future environment has headroom. It does not
authorize 003A execution, full-harness execution, candidate implementation,
route tournament, runtime/mainline/admission/bridge wiring, or any mechanism,
agency, autonomy, consciousness, or EGO readiness claim.
