# BATCH-ENV-HEADROOM-SCOUT-002B Independent Static And Compute-Baseline Scout Task Card 001A

Status: draft task card only. Do not execute in the 002A false-promotion
closeout task.

Auto-Remote-Anchor: forbidden.

## Problem Definition

`BATCH-ENV-HEADROOM-SCOUT-002A` produced a false-positive promotion for
`relational_contrast_budget_probe` because its static kill scan echoed
author-provided flags and its micro-probe battery did not include fair
legal-channel compute/fitted baselines. The promoted oracle was itself a
budget-faithful computation over legal visible channels.

002B must accelerate candidate-free environment discovery by batch-screening
environment sketches with independent static analysis and a complete cheap
baseline micro-battery before any full-harness promotion.

## Current Stage / Layer

engineering-governance / Phase-0 candidate-free environment portfolio scouting
repair task card.

## Mainline Target

none.

## Enabled-State Requirement

No runtime/mainline/admission/bridge path is enabled.

## Real-Trigger Evidence Requirement

002B, when separately authorized and executed, must produce machine-readable
artifacts from callable static analyzers, callable generators, callable
oracles, callable cheap baselines, fitted/rule legal-channel learners, and
consumed verdict rows. Natural-language summaries are not evidence.

## Hard Rule

Parallelize environment screening, not candidate implementation.

## Forbidden Scope

002B must not:

- implement WM-P, VSB-C, or CSL;
- start a route tournament;
- implement candidates;
- wire runtime/mainline/admission/bridge;
- reopen or optimize `MINIMAL-ENV-SPEC-001A`;
- execute `relational_contrast_budget_probe` full harness;
- commit, push, tag, or remote-anchor.

## Hypothesis

An environment sketch is worth promoting to a full baseline-first harness only
if independent static analysis cannot kill it and a complete cheap-baseline
micro-battery, including legal-channel compute and fitted/rule learners, leaves
a preliminary oracle-vs-baseline gap of at least 0.08.

## Strongest Baseline

The strongest baseline is the maximum score over all consumed fair baselines,
including:

- `exhaustive_legal_query`;
- `budget_limited_belief_state_planner`;
- `greedy_information_gain_or_uncertainty_planner_under_budget`;
- `graph_lookup`;
- `transition_table`;
- `successor_map`;
- `count_table`;
- `fsm_planner`;
- `episodic_traversal`;
- `trace_only_replay`;
- `ngram_trace_lookup`;
- passive decoder;
- size-only;
- degenerate controls;
- fitted legal-channel learner.

## Independent Static Kill Scan Requirement

Static kill scan must be independent. Do not trust
`sketch.static_kill_flags` as evidence. Author-provided flags may be stored only
as `author_claims`.

The scanner must derive kill reasons from executable generator, oracle, target,
visible-channel, legal-query, metric, and split definitions.

Required derived checks:

- target dependency set over visible/legal channels;
- whether target is deterministic from <= budget legal channels;
- whether oracle is just a legal-channel compute baseline;
- whether any visible field equals or encodes target;
- whether legal-query can read all target components;
- whether train/test split only defeats memorization but not compute;
- whether state/signature space permits lookup saturation;
- whether graph/cache/transition table can recover target;
- whether metric is balanced and non-degenerate;
- whether oracle touches hidden_state, answer_key, future labels, or unqueried values.

If static kill scan is not independently derived, the verdict must be:

`blocked_static_scan_not_independent`

## Oracle-As-Baseline Rule

If the oracle computes target using only legal visible channels within budget,
then the same computation must be registered as a fair baseline.

If that fair baseline reaches the oracle equivalence band, reject:

- `reject_direct_decode`; or
- `reject_legal_compute_baseline_saturated`.

The oracle may not create headroom by placing legal compute on the oracle side
while leaving only lookup or memory on the baseline side.

## Complete Micro-Probe Baseline Battery

Every promoted sketch must invoke at minimum:

- `exhaustive_legal_query`;
- `budget_limited_belief_state_planner`;
- `greedy_information_gain_or_uncertainty_planner_under_budget`;
- `graph_lookup`;
- `transition_table`;
- `successor_map`;
- `count_table`;
- `fsm_planner`;
- `episodic_traversal`;
- `trace_only_replay`;
- `ngram_trace_lookup`;
- passive decoder;
- size-only;
- degenerate controls;
- fitted legal-channel learner.

The fitted legal-channel learner must include at least one model capable of
learning algebraic or rule-based mappings over legal observed channels, such as:

- multinomial logistic regression or equivalent linear classifier where applicable;
- decision tree or rule learner where applicable;
- least-squares / linear model where applicable;
- compact symbolic/rule search for small discrete legal-channel targets where applicable.

If the target is a simple formula over legal channels and no fitted/rule learner
is run, promotion is blocked:

`blocked_compute_baseline_missing`

## Baseline Independence / Alias Check

Every baseline row must record:

- `producer_function`;
- `source_body_hash`;
- `prediction_vector_hash`;
- `input_field_manifest`;
- `strategy_signature`;
- `baseline_family`;
- `independence_family`;
- `consumed_by_final_verdict`.

If multiple baselines share identical function body and identical predictions,
they must be collapsed into one `independence_family` for evidence
interpretation. They may not be cited as independent corroboration.

## Ablation Requirement

002B is a scout, not a formal Gate. Its micro-probe must still include
candidate-free failure controls:

- remove legal compute baseline and verify the verdict blocks rather than promotes;
- reduce oracle query budget below target dependency count and verify
  `reject_oracle_not_budget_faithful` or equivalent rejection;
- inject target/answer/future-label visible aliases and require leakage detection;
- force train/test signature overlap and require graph/cache saturation detection;
- force passive alias and require passive decoder rejection;
- force degenerate label distribution and require metric-degeneracy rejection.

## Trace / Replay Requirement

Every micro-probe must emit enough trace to recompute each oracle and baseline
prediction from serialized visible state, legal query trace, and budget ledger.
Hash-only replay or stored-prediction replay is insufficient.

Required replay negative controls:

- tamper stored prediction while preserving state and require recomputation mismatch;
- remove queried legal channel and require replay failure;
- add hidden/answer/future-label field access and require oracle-budget failure.

## Computed-Evidence Provenance Gate

Every score, static kill reason, baseline row, leakage scan, replay result, and
promotion decision must be produced by callable code and must record:

- `producer_function`;
- input artifacts;
- `run_id`;
- seed/context/episode IDs;
- aggregation rule;
- code/source body hash;
- consumed-by-verdict status.

Static dictionaries, hand-written verdicts, self-declared flags, and tests that
only assert pass are not evidence.

## Promotion Rule

A sketch may be promoted to full baseline-first harness candidate only if:

- static kill scan independently passes;
- oracle is budget-faithful;
- oracle is not merely a legal-channel compute baseline unless the same compute
  baseline is scored and remains below oracle;
- strongest cheap baseline is below oracle by preliminary gap >= 0.08;
- `exhaustive_legal_query` is below oracle minus band;
- fitted legal-channel learner is below oracle minus band;
- graph/cache family is below oracle minus band;
- passive/size-only/degenerate controls are low;
- train/test split defeats both memorization and simple legal-channel compute;
- all required baseline rows are `consumed_by_final_verdict`.

## Allowed Micro-Probe Verdicts

Micro-probe may produce only:

- `reject_direct_decode`;
- `reject_legal_compute_baseline_saturated`;
- `reject_graph_cache_saturated`;
- `reject_passive_decodable`;
- `reject_metric_degenerate`;
- `reject_oracle_not_budget_faithful`;
- `reject_underpowered_surface`;
- `blocked_compute_baseline_missing`;
- `blocked_static_scan_not_independent`;
- `blocked_baseline_battery_incomplete`;
- `promote_to_full_harness_candidate`.

Micro-probe may not produce:

- `headroom_confirmed`;
- `candidate_authorized`;
- `route_tournament_authorized`.

## Promotion Artifact Requirement

Any promoted sketch must include a machine-readable promotion case with:

- `sketch_id`;
- `target_rule`;
- `target_dependency_set`;
- `legal_channel_set`;
- `budget`;
- `oracle_definition`;
- `oracle_field_access_manifest`;
- `strongest_cheap_baseline_score`;
- `strongest_cheap_baseline_producer`;
- `fitted_legal_channel_learner_score`;
- `exhaustive_legal_query_score`;
- `graph_cache_family_max`;
- `passive_family_max`;
- `degenerate_max`;
- `size_only_max`;
- `preliminary_gap`;
- why direct legal-channel compute does not saturate;
- why train/test split defeats both memorization and compute;
- remaining risks;
- claim ceiling.

## Acceptance Gate

002B is accepted only if it writes required artifacts, all JSON artifacts parse,
static scan is independently derived, the complete baseline battery is invoked
for every micro-probed survivor, baseline independence families are reported,
and every promotion decision consumes the required evidence rows.

Any promotion remains only a full baseline-first harness candidate. It is not
headroom confirmation, candidate authorization, route-tournament authorization,
Gate1 pass, mechanism validity, or runtime/mainline effect.

## Required 002B Artifacts When Later Executed

- `artifacts/batch_env_headroom_scout_002b/sketch_registry.json`;
- `artifacts/batch_env_headroom_scout_002b/author_claims.json`;
- `artifacts/batch_env_headroom_scout_002b/independent_static_kill_scan.json`;
- `artifacts/batch_env_headroom_scout_002b/dependency_analysis.json`;
- `artifacts/batch_env_headroom_scout_002b/micro_probe_results.json`;
- `artifacts/batch_env_headroom_scout_002b/baseline_independence_report.json`;
- `artifacts/batch_env_headroom_scout_002b/promoted_full_harness_candidates.json`;
- `artifacts/batch_env_headroom_scout_002b/rejected_sketches.json`;
- `artifacts/batch_env_headroom_scout_002b/final_report.md`.

## Stop Condition

Stop and reject, block, or close if:

- static scan is not independent;
- target is deterministic from <= budget legal channels and the same compute
  baseline reaches oracle;
- legal query can read all target components;
- visible fields leak target;
- graph/cache/transition/lookup saturates;
- passive decoder saturates;
- metric is degenerate;
- oracle reads hidden_state, answer_key, future labels, or unqueried values;
- required compute/fitted baselines are missing;
- baseline rows are not consumed by final verdict;
- promotion would depend only on train/test memorization split rather than
  compute-resistant evidence.

## Rollback Plan

If 002B execution is later attempted and fails scope or evidence controls, delete
only new 002B artifacts and code from the authorized 002B paths. Do not rewrite
002A artifacts, `MINIMAL-ENV-SPEC-001A`, or prior negative evidence.

## Expected Changed Files For Later 002B Execution

- `scripts/research/batch_env_headroom_scout_002b.py`;
- `tests/research/test_batch_env_headroom_scout_002b.py`;
- `artifacts/batch_env_headroom_scout_002b/`.

## Forbidden Changes

- candidate implementations;
- WM-P / VSB-C / CSL files;
- route tournament files;
- runtime/mainline/admission/bridge wiring;
- `MINIMAL-ENV-SPEC-001A` edits;
- 002A artifact rewrites;
- commit, push, tag, or remote-anchor.

## Claim Ceiling

002B candidate-free scout task card only until separately executed.

No headroom confirmation. No Gate1 pass. No mechanism validity. No candidate
feasibility. No runtime/mainline effect. No agency, autonomy, consciousness, or
EGO readiness.

## Next Minimal Closed-Loop Action

Review this task card. If accepted, run `BATCH-ENV-HEADROOM-SCOUT-002B` as a
separate candidate-free scout task. Stop before candidate implementation.
