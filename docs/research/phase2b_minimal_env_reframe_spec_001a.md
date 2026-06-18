# Phase2B Minimal Environment Reframe Spec 001A

Status: draft candidate-free environment reframe spec opened by
`RESEARCH-CAMPAIGN-PHASE2B-MINIMAL-ENV-REFRAME-SPEC-001A`.

Auto-Remote-Anchor: forbidden.

## Purpose

This document drafts a replacement candidate-free environment surface after the
audited Phase 2 result `no_headroom_baseline_saturated` on
`MINIMAL-ENV-SPEC-001A`. It is a specification draft only. It does not freeze a
new surface, implement a harness, compute oracle scores, run baselines,
implement candidates, open Phase 3, or authorize runtime/EGO mainline work.

The only immediate allowed action after this draft is focused validation of the
task card and spec. A future execution card would have to separately freeze the
spec, implement a candidate-free baseline-first harness, and measure headroom
or no-headroom before any candidate work.

## Source Negative Evidence

Phase 2 source result:

- source task: `RESEARCH-CAMPAIGN-PHASE2-BASELINE-FIRST-HEADROOM-001A`
- verdict: `no_headroom_baseline_saturated`
- visible-channel oracle macro F1: `1.0`
- strongest fair baseline: `count_table`
- strongest fair baseline macro F1: `1.0`
- equivalence band: `0.03`
- candidate mechanism run: `false`
- Phase 3 opened: `false`

Interpretation: `MINIMAL-ENV-SPEC-001A` is not repaired or refrozen here. It is
preserved as a blocked no-headroom surface.

## Claim Ceiling

Phase2B environment-reframe draft only. This does not prove headroom, mechanism
validity, subjective experience, consciousness, real emotion, autonomy, EGO
readiness, companion readiness, runtime readiness, or mainline effect.

## Design Rule

The new surface must make the future legal interaction channel different from
an answer key. A runner may receive observations and spend budget on legal
interactions, but no candidate-visible field or legal response may expose:

- target labels;
- final-action scores;
- answer maps;
- complete legal response bundles;
- hidden target variables;
- semantic labels that identify the correct final action;
- fixture names, filenames, source paths, or artifact structure that encode the
  target.

## Environment Identity

Environment id: `minimal_closed_loop_counterfactual_boundary_001a`.

Informal name: Minimal Counterfactual Boundary Loop.

The environment is a small partially observable control task with three
separate latent factors:

- protected viability state;
- self-caused transition state;
- external perturbation state.

The final decision depends on a counterfactual distinction between self-caused
and externally caused changes. Legal interactions expose only local observation
updates, intervention outcomes, and budgeted probes. They do not expose a final
action ranking or target score.

## Candidate-Free Scope

The future harness may implement only:

- a generator;
- a visible-channel oracle;
- fair baselines;
- leakage scanners;
- replay recomputation;
- ablation/control producers;
- provenance/readback producers;
- a final verdict aggregator.

The future harness may not implement a candidate mechanism until measured
candidate-free headroom exists.

## Required State Schema

Each generated episode must distinguish diagnostic fields from admissible
fields.

Admissible fields:

- `episode_id`
- `seed`
- `current_observation`
- `legal_action_or_query_schema`
- `budget_state`
- `runner_action_history`
- budgeted legal interaction results actually requested by the runner
- `serialized_state` stripped of target labels and final-action scores

Diagnostic-only fields:

- `hidden_state`
- `target_label`
- `target_final_action`
- `target_score_by_action`
- `full_unqueried_legal_response_bundle`
- `external_perturbation_schedule`
- `self_caused_transition_trace`
- `generator_config`

Forbidden candidate-visible fields:

- `target_label`
- `target_final_action`
- `target_score_by_action`
- `answer_map`
- `oracle_action_rank`
- `full_unqueried_legal_response_bundle`
- any alias that carries equivalent information

## Legal Interaction Boundary

Legal interactions must be budgeted and partial:

- `observe_visible_state`: returns only current visible variables.
- `probe_local_sensor`: returns one named local sensor value, not a final
  action score.
- `apply_test_action`: applies an intervention and returns the next visible
  observation, not whether the final action is correct.
- `store_state`: stores admissible visible state and budget state.
- `replay_state`: recomputes from serialized admissible state plus current
  observation and legal schema.
- `inspect_budget`: returns remaining budget only.

Forbidden legal interactions:

- query all action scores;
- query best final action;
- query target label;
- query hidden transition family as a class label;
- query full response bundle or full legal response bundles;
- query an oracle explanation that names or ranks final actions.

## Final Decision Boundary

Future final actions should use anonymous handles or non-semantic ids in the
candidate-visible channel. Human-readable labels may exist only in diagnostic
metadata after scoring.

The future harness must include a semantic-label leak positive control that
proves validation fails if final-action names encode the answer.

## Budget And Measurement Rule

Budget must be frozen before any score exists. The future harness must compare
visible-channel oracle and every fair baseline under the same budget and input
boundary.

Headroom condition:

```text
battery_max_fair_baseline < visible_channel_oracle - equivalence_band
```

No-headroom condition:

```text
battery_max_fair_baseline >= visible_channel_oracle - equivalence_band
```

If no-headroom is measured, candidate search remains blocked.

## Required Future Baselines

The future baseline battery must include:

- random, majority, and constant predictors;
- passive observation-only attackers;
- nearest-neighbor passive attacker;
- supervised passive attacker;
- count table;
- graph lookup;
- transition table;
- successor map;
- FSM planner;
- episodic traversal;
- exhaustive legal query under the same budget;
- greedy uncertainty query under the same budget;
- trace-only replay;
- n-gram trace lookup;
- full-bundle decoder positive/negative boundary;
- serialized-state decoder;
- strongest known classical method for the generated task type.

Strongest fair baseline is `max(all applicable callable baselines)`.

## Leakage And Positive Controls

A future leakage scanner must inspect:

- observation names and values;
- action ids and human-readable action metadata;
- probe names;
- filenames;
- fixture names;
- artifact structure;
- source paths;
- generator metadata;
- label ordering;
- serialized-state fields;
- legal response payloads.

Positive controls must include injected:

- target label;
- final-action score;
- answer map;
- semantic action-label leak;
- full legal response bundle;
- full legal response bundles;
- source-path target leak.

Each positive control must be detected and consumed by the final verdict.

## Replay Requirement

Replay must recompute from:

```text
serialized_state + current_observation + legal_action_or_query_schema + budget_state
```

Replay must fail if target labels, final-action scores, answer maps, or full
legal response bundles are removed from diagnostic-only storage and the replay
path depended on them.

## Provenance Requirement

Future execution must record:

- generator source path and SHA256;
- generator config SHA256;
- source spec path and SHA256;
- producer functions;
- input artifacts;
- run id;
- seed/context/episode ids;
- aggregation rule;
- code path hashes;
- leakage and replay control ids;
- consumed-by-final-verdict flags.

## Validation Requirement For This Draft

This draft is valid as a task-card/spec-opening checkpoint only if local
validation confirms:

- it is candidate-free;
- it preserves Phase 2 no-headroom negative evidence;
- it forbids target labels, final-action scores, answer maps, full legal
  response bundles, semantic action-label leaks, and old-spec mutation;
- it predeclares the strong baseline battery;
- it requires future headroom measurement before candidate work;
- it does not authorize execution, candidates, Phase 3, runtime/mainline,
  remote action, or spec freeze.

## Stop Conditions

Stop if:

- this draft is treated as measured headroom;
- this draft is frozen without a separate freeze/readback card;
- any executable harness or candidate is implemented under this card;
- any baseline is removed because it saturated Phase 2;
- any prior no-headroom evidence is rewritten into positive evidence.

## Next Minimal Closed-Loop Action

Run focused local validation of the Phase2B task card and this spec draft. If it
passes, record the validation and keep the next frontier at read-only reviewer
audit before any Phase2B execution task.
