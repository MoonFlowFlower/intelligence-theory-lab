# MINIMAL-ENV-SPEC-001A

Status: FROZEN ENVIRONMENT SPEC CANDIDATE, pending freeze metadata readback.
Auto-Remote-Anchor: forbidden.

## Purpose

This document specifies a candidate-free minimal closed-loop environment for the
next Gate1-replacement Phase-0 headroom test. It freezes an environment contract
only. It does not implement a generator, run an oracle, run baselines, implement
WM-P, implement VSB-C, implement CSL, run Route C, run Gate1, or authorize any
runtime/mainline/admission/bridge path.

The immediate next allowed bounded card is `BASELINE-FIRST-HARNESS-001A`. That
future card must implement only a candidate-free oracle/baseline harness against
this frozen spec and report measured headroom or no-headroom.

## Layer And Claim Ceiling

- Current layer: engineering-governance / candidate-free environment spec freeze.
- Mainline integration status: none.
- Enabled status: no executable path is enabled by this file.
- Real trigger evidence: 00XA closeout and independent 001B re-audit sources are
  SHA256-recorded in `artifacts/minimal_env_spec_001a/source_readback.json`.
- Claim ceiling: frozen minimal closed-loop environment spec only.

This file does not claim headroom, Gate1 pass, Gate1 replacement validity,
mechanism validity, candidate feasibility, baseline-immunity enforcement,
runtime readiness, agency, autonomy, consciousness, emotion, stable user
benefit, or EGO readiness.

## Accepted Negative Evidence Boundary

00XA is treated as accepted bounded offline negative route evidence and closed
for candidate work. It is not inherited as an admissible surface. The relevant
failure family is that a fair candidate-free baseline can saturate the visible
oracle when the fixed budget permits full legal-channel recovery. The next route
therefore must be:

1. minimal environment spec;
2. baseline-first headroom harness;
3. measured headroom or no-headroom decision;
4. only then candidate micro-implementation, if measured headroom exists.

Route tournament, candidate contracts, WM-P, VSB-C, CSL, LLM-agent, world-model
candidate, viability candidate, curriculum candidate, and skill-library
candidate work are forbidden until a candidate-free measured headroom precheck
clears.

## Strongest False Explanation

The strongest false explanation for any future apparent success is that the
environment looks mechanism-sensitive but is actually solved by a cheaper route:

- exhaustive legal query under the same budget;
- graph lookup, transition table, successor map, count table, FSM planner, or
  episodic traversal;
- lookup imitation or serialized-state decoding;
- passive observation decodability;
- degenerate prediction;
- size-only scoring;
- hidden answer key, planted truth, or generator leakage;
- prompt/template/script imitation;
- replay hashes rather than behavior recomputation;
- post-hoc budget or threshold tuning;
- generator/source-pin provenance gaps.

The future harness must make every item above callable, fail-able, and consumed
by the final verdict.

## Environment Identity

Environment id: `minimal_closed_loop_latent_maintenance_001a`.

Informal name: Minimal Latent Maintenance Loop.

This is a tiny partially observable maintenance task. Each episode contains a
small protected system with hidden dynamics, a viability reservoir, a
self-caused action trace, and an external perturbation process. The runner sees
only a legal visible channel and may spend a fixed candidate-matched budget on
observations, probes, memory/replay operations, or interventions before choosing
a final protective action. The target is not exposed in admissible channels.

This environment is intended as a shared Phase-0 route-neutral headroom surface
only if the future harness measures headroom. Route neutrality is provisional:

- WM-P support surface: hidden dynamics, action-conditioned transition, and
  replay from serialized state.
- VSB-C support surface: viability state, self-boundary state, and external vs
  self-caused perturbation distinction.
- CSL support surface: store/replay operations and future heldout/mutation
  hooks, but no learning/adaptation claim in Phase 0.

If the future harness finds that the surface structurally favors one route or
that baseline headroom is absent, this spec must be treated as route-specific or
closed as no-headroom negative evidence. It must not be used as a neutral
tournament environment by declaration.

## Episode Lifecycle

Each episode must follow this abstract lifecycle:

1. A generator initializes hidden episode state from a seed and a pre-declared
   generator config.
2. The runner receives an `initial_observation` drawn from admissible visible
   fields only.
3. The runner may consume up to `candidate_matched_budget_tokens = 5` across
   legal observation, probe, store, replay, or intervention operations.
4. The runner emits one final decision from the frozen final-action set.
5. The harness computes balanced metrics from generated target variables and
   runner decisions.

The full legal channel count for exhaustive recovery is frozen as
`full_legal_channel_count = 12`. The Phase-0 budget is therefore strictly below
full legal-channel access. Budget strictness is necessary but not sufficient:
the future harness must still show that no cheap/fair baseline reaches the
visible oracle under this same budget.

## Required State Schema

Every generated episode record must contain these fields:

- `episode_id`: stable episode identifier.
- `seed`: generator seed.
- `hidden_state`: diagnostic-only latent state, forbidden for admissibility.
- `observable_state`: fair visible observation payload.
- `legal_action_space`: legal actions available at each step.
- `legal_channel_responses`: legal responses produced by observe/probe/query
  operations.
- `viability_state`: protected-system viability value and bucket.
- `self_boundary_state`: variables distinguishing self-caused changes from
  external perturbations.
- `external_perturbation_state`: hidden perturbation source and schedule.
- `transition_rule_id`: hidden dynamics rule identifier.
- `serialized_state`: replayable state snapshot.
- `target_label_or_target_variable`: generated target for metric computation;
  diagnostic-only and forbidden for admissibility support.
- `generator_source_hash`: SHA256 of generator source in the future harness.
- `generator_config_hash`: SHA256 of generator config in the future harness.
- `source_pin_readback`: canonical source-pin readback for the future harness.

Visibility classes:

- Fair baselines and visible-channel oracle may read: `episode_id`, `seed`,
  `observable_state`, `legal_action_space`, legal responses from actions they
  actually spend budget on, budget state, and their own action history.
- Diagnostic oracle only may read: `hidden_state`,
  `target_label_or_target_variable`, unqueried `legal_channel_responses`, full
  perturbation schedule, and hidden transition parameters.
- Forbidden for all admissibility support: answer maps, target labels, hidden
  target variables, source paths that encode labels, fixture names that encode
  labels, candidate-authored truth, post-hoc thresholds, post-hoc budget edits,
  and any generated field marked diagnostic-only.

## Hidden Dynamics Contract

The future generator must instantiate at least four pre-declared transition
families under `transition_rule_id`. Each family must couple:

- an action-conditioned transition;
- one external perturbation rule;
- one self-boundary update rule;
- one viability update rule.

The transition family must be selected by seed and config before any harness
score is generated. Train/validation/heldout/test separation, if used, must be
based on seed partitions declared before the run. The generator may not encode
the target in observation names, filenames, fixture names, action names, artifact
layout, label ordering, or source-pin paths.

## Legal Actions And Queries

The action/query schema is frozen as a minimal superset. A future implementation
may implement a strict subset only if it preserves prediction, intervention,
viability/boundary, and replay requirements.

- `observe`: spend one budget token to refresh the current visible observation.
- `probe`: spend one budget token to query one legal sensor from a frozen set of
  eight probe channels. A probe response is legal visible evidence only for the
  caller that spent the token.
- `move_or_act`: spend one budget token to apply one action-conditioned state
  transition.
- `repair_or_protect_viability`: spend one budget token to protect or repair a
  viability component.
- `store`: spend one budget token to serialize current visible/budget state into
  runner memory.
- `replay`: spend one budget token to recompute candidate behavior from
  `serialized_state`, current observation, legal action/query schema, and
  budget state.
- `exploit`: spend one budget token to make a non-protective action that may
  improve short-term score while risking viability.
- `ignore`: no-op action; if it is free, it must still be represented in the
  trace.
- `ask_or_query_channel`: alias for a named legal probe channel; it may not read
  hidden truth or target labels.

Final decision labels are frozen as:

- `protect_left_boundary`;
- `protect_right_boundary`;
- `repair_core_viability`;
- `exploit_safe_window`;
- `defer_or_ignore`.

The future harness may not add a final decision label after seeing baseline or
oracle scores.

## Budget Rule

The candidate-matched budget is frozen at five budget tokens per episode for
Phase 0. The full legal-channel count is twelve. The future harness must compare
every admissible oracle, baseline family, and control under the same budget.

The true headroom condition is:

`battery_max_fair_baseline < visible_channel_oracle - equivalence_band`

under the same candidate-matched budget.

Budget below full legal-channel count is not enough. If any cheap/fair baseline
reaches the visible-channel oracle within the equivalence band, the future
harness must return no-headroom / baseline-saturated and stop before candidate
work.

## Metric Requirement

The future harness must use balanced metrics:

- primary metric: macro F1, beta = 1.0;
- per-class precision floor: 0.85;
- per-class recall floor: 0.85;
- equivalence band: 0.03;
- oracle target floor: 0.90;
- passive rejection floor: below 0.87;
- degenerate rejection floor: below 0.87;
- size-only rejection floor: below 0.87;
- false-positive and false-negative accounting by final decision label.

Admission from these metrics is forbidden:

- recall-only;
- precision-only;
- coverage-only;
- specificity-only;
- abstention-only;
- size-only score;
- natural-language summary;
- static verdict dictionary;
- provenance-wellformed-only.

Any threshold chosen after seeing baseline or oracle scores is invalid.

## Mandatory Phase-0 Headroom Precheck

`BASELINE-FIRST-HARNESS-001A` must compute and consume:

- visible-channel oracle score;
- answer-key diagnostic oracle score;
- strongest fair baseline score;
- passive family max score;
- degenerate predictor max score;
- size-only sweep max score;
- full graph-cache family max score;
- exhaustive legal query score;
- leakage positive-control result;
- replay recomputation result;
- source/generator provenance result.

Required Phase-0 pass condition:

- visible-channel oracle >= 0.90;
- passive family max < 0.87;
- degenerate controls max < 0.87;
- size-only sweep max < 0.87;
- strongest fair baseline < visible_channel_oracle - 0.03;
- exhaustive legal query < visible_channel_oracle - 0.03;
- every graph-cache challenger < visible_channel_oracle - 0.03;
- no leakage positive-control failure;
- replay recomputes from serialized_state + observation;
- generator/source provenance is complete and consumed.

If any cheap/fair baseline enters the oracle equivalence band, the future
harness must stop with no-headroom / baseline-saturated verdict. It must not
enter route tournament or candidate implementation.

## Baseline Battery Requirement

The future harness must define strongest fair baseline as:

`max(all applicable baseline battery members)`

not as a hand-picked baseline.

Mandatory callable producers:

- degenerate predictors: `predict_all`, `predict_none`, `constant_k_sweep`,
  `random`, `majority`;
- size-only sweep: `size_only_sweep_0_to_n`;
- passive family: `observation_only`, `value_decoder_mean`,
  `value_decoder_variance`, `value_decoder_correlation`, `value_decoder_pca`,
  `nearest_neighbor_passive`, `membership_passive_attacker`,
  `supervised_passive_attacker`;
- active/query baselines: `exhaustive_legal_query`,
  `greedy_uncertainty_query_under_budget`;
- six graph-cache challengers: `graph_lookup`, `transition_table`,
  `successor_map`, `count_table`, `fsm_planner`, `episodic_traversal`;
- lookup imitation: `trace_only_replay`, `ngram_trace_lookup`,
  `full_bundle_decoder`, `serialized_state_decoder`, `belief_table`,
  `pair_count_table`;
- direct objective optimizers where applicable: `discounted_wls`,
  `least_squares`, `convex_solver`;
- amortized learner only if a learning/adaptation claim appears: real fitted
  learner with anti-stub guard and recorded fit;
- strongest known classical method for the task type.

Every baseline result must record `producer_function`, input artifacts, run id,
seed/context/episode ids, aggregation rule, and code path hash. Every result
must be consumed by the final verdict.

## Multi-Seed And Power Requirement

The future harness must use more than a minimal toy seed count:

- at least five seeds;
- at least twenty episodes per seed;
- per-seed scores and aggregate macro F1;
- declared aggregation rule before run;
- seed-noise tolerance;
- failure if headroom exists only inside seed noise.

Any smaller floor requires a pre-run rationale recorded before any score exists.

## Leakage Requirement

The future harness must include a fail-able leakage scanner with positive
controls. Scanned channels must include:

- observation names;
- action names;
- filenames;
- fixture names;
- artifact structure;
- baseline hints;
- planted answer maps;
- value-level fields;
- label ordering;
- generator metadata;
- source-pin paths.

Positive controls must prove:

- injected leak is detected;
- detection id is recorded;
- removal of injected leak removes detection;
- detection is consumed by final verdict.

## Replay Requirement

Replay must recompute behavior from:

- `serialized_state`;
- current observation;
- legal action/query schema;
- budget state.

Hash-only replay and stored-output replay are invalid. The future harness must
include at least one replay tamper negative control.

## Generator And Source Provenance Requirement

The future harness must record and consume:

- generator source path;
- generator source SHA256;
- generator config SHA256;
- producer function;
- code path hash;
- readback channel;
- fair-baseline-access declaration;
- hidden-target-storage declaration;
- no-candidate-authored-truth assertion;
- source-pin integrity status;
- consumed_by_final_verdict.

If generator provenance is missing, unverifiable, self-readback-only, or
candidate-authored, the future harness must stop before headroom or
admissibility conclusions.

## Freeze And Mutation Ban

The freeze metadata must include:

- spec path;
- SHA256;
- author/source;
- freeze timestamp or decision-log pointer;
- canonical readback channel;
- source inputs and hashes;
- mutation ban;
- next-harness readback requirement.

The next harness implementer may not mutate, normalize, amend, or refreeze this
spec. Any required environment redesign must use a new bounded task card.

## Acceptance Gate

This spec is acceptable only if validation confirms:

- candidate-free Phase-0 purpose;
- baseline-first harness as immediate next step;
- measured headroom, not declared headroom;
- strongest fair baseline as max over full battery;
- budget-matched comparison;
- budget below full legal-channel count or stronger anti-exhaustive proof;
- all six graph-cache challengers;
- balanced metric and per-class floors;
- multi-seed / power accounting;
- leakage positive controls;
- replay recomputation;
- generator/source provenance gate;
- no candidate or route tournament implementation;
- no source/test/runtime path touched;
- no remote action.

Expected verdict if all validation passes:

`minimal_env_spec_001a_frozen`

## Stop Conditions

Stop and emit a blocked report if:

- source or tests are written;
- baselines or oracle scores are run;
- a candidate is implemented;
- a candidate surface is frozen instead of an environment spec;
- full baseline battery requirements are omitted;
- budget-matched headroom is omitted;
- route specificity remains ambiguous;
- generator/source provenance gate is omitted;
- 00XA evidence is mutated;
- runtime/mainline/admission is touched;
- commit, push, tag, or remote anchor is attempted.

## Rollback Plan

Rollback is limited to removing only files created for this task:

- `docs/research/MINIMAL-ENV-SPEC-001A.md`;
- `docs/research/MINIMAL-ENV-SPEC-001A.freeze.json`;
- `artifacts/minimal_env_spec_001a/`.

Do not delete, move, or rewrite 00XA negative evidence, 001A/001B evidence,
closeout files, or unrelated dirty workspace material.

## Next Minimal Closed-Loop Action

Immediately draft and run the next bounded task:

`BASELINE-FIRST-HARNESS-001A`

That next task must implement only a candidate-free baseline/oracle harness
against this frozen environment spec and report measured headroom or
no-headroom. If the baseline battery saturates the oracle, it must stop and
record no-headroom negative evidence without route tournament or candidate
implementation.
