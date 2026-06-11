# PROCESS-INTERVENTION-PREFLIGHT-001B Executable-Preflight Task Card

Task ID: PROCESS-INTERVENTION-PREFLIGHT-001B

Layer: engineering implementation plus mechanism-hypothesis testing, bounded
offline executable preflight only.

## Authorization Boundary

```text
mechanism_implementation_authorized = false
mechanism_training_authorized = false
agent_training_authorized = false
model_class_reset_authorized = false
gate1_reopen_authorized = false
same_agent_bridge_authorized = false
ego_integration_authorized = false
llm_rag_companion_emotion_relationship_user_model_modules_authorized = false
execution_authorized_by_this_draft = false
```

This card is executable-preflight drafting and authorization-review material.
It does not itself run the preflight. A later implementation turn may create
isolated verifier and evaluator files only after Stage0 freeze is complete.

Allowed future implementation paths, only after authorization review:

```text
src/process_intervention_preflight_001b/
tests/test_process_intervention_preflight_001b*.py
artifacts/process_intervention_preflight_001b/
```

Forbidden paths remain EGO mainline, Gate1 reopening, same-agent bridge,
model-class reset, LLM/RAG/companion/emotion/relationship/user-model modules,
and any deployment or external service.

## Negative Evidence Admission

This successor task card must pass `NEGATIVE-EVIDENCE-ADMISSION-GATE-001A`
before any future implementation work.

Inherited evidence:

```text
001A supersession = REPRESENTATIONAL-GAP-PREFLIGHT-001A-AUDIT-CLOSEOUT / superseded_by_independent_audit
001B fair-control failure = representational_gap_001b_failed_count_or_statistic_control_solved
001C canonical evidence = PREDICTIVE-ACTION-LEARNING-CONTRACT-001C-CANONICAL-FREEZE plus PREDICTIVE-ACTION-LEARNING-CONTRACT-001C-CANONICAL-ERRATA-001A
process intervention draft caveat = process_intervention_001a_independent_audit_pass_with_caveats is not executable authorization
verdict-string tests are not acceptance evidence
Gate1 replay_verification_pass is not sufficient without gate1_preflight_failed_graph_cache_collapse
Fable causality claim = none; any such claim would require provenance, diff, and mechanism evidence
```

The 001C current-worktree closeout is not treated as clean canonical evidence
without the canonical errata. 001C evidence must be cited through freeze
commit/tag plus sha256 manifest or canonical errata.

## Problem Definition

Can a bounded process/intervention witness show intervention-sensitive update
dynamics and later behavior change that remain non-equivalent to fair online
cheap controls under the same access, resource, trace-commitment, replay, and
separation-statistic contracts?

This is not a consciousness, agency, emotion, autonomy, EGO readiness, or
companion-readiness test.

## Current Stage

Executable-preflight authorization-review draft. The previous AMENDMENT-001
semantic blocker was missing support contracts and amendment artifacts. The
draft may proceed only because those support contracts now exist:

```text
docs/process_intervention_preflight_001a/real_control_implementation_contract.md
docs/process_intervention_preflight_001a/trace_commitment_contract.md
docs/process_intervention_preflight_001a/match_metric_contract.md
docs/process_intervention_preflight_001a/update_path_contract.md
docs/process_intervention_preflight_001a/separation_statistic_contract.md
docs/process_intervention_preflight_001a/state_accounting_contract.md
docs/process_intervention_preflight_001a/resource_budget_contract.md
docs/process_intervention_preflight_001a/environment_intervention_instantiation_contract.md
docs/process_intervention_preflight_001a/memory_key_fidelity_contract.md
docs/process_intervention_preflight_001a/behavior_probe_contract.md
docs/process_intervention_preflight_001a/stage0_freeze_anchor_contract.md
artifacts/process_intervention_preflight_001a_amendment_001/amendment_matrix.json
artifacts/process_intervention_preflight_001a_amendment_001/blocking_gate_status.json
```

## Hypothesis

Engineering hypothesis:

```text
H1 = A bounded witness may produce a resource-normalized heldout-composition update signature that fair online cheap controls do not match.
```

Null / expected collapse hypothesis:

```text
H0 = A fair online table, FSM, graph/cache, kNN, summary statistic, causal table, or trace generator matches the witness under frozen metrics and the task fails.
```

The honest prior is that H0 may win. That failure is valid evidence and must
not be patched into a pass.

## Frozen Environment Family

The future executable preflight must instantiate a bounded offline environment:

```text
episode_count = 96 paired episodes
train_history = 64 episodes
online_history = 32 episodes
contexts = 8 observable context aliases
actions = 4 discrete actions
heldout_compositions = 8 pairwise intervention compositions
episode_design = baseline, intervened, non_intervened_twin
hidden_simulator_state_visible_to_non_oracle_systems = false
seed_or_split_leakage_allowed = false
future_observation_or_outcome_access_allowed = false
```

If the environment is fully enumerable by causal table or graph/cache within
budget and those controls match, the task fails.

## Interventions

Each intervention must instantiate all fields in
`environment_intervention_instantiation_contract.md`.

Required families:

```text
I1 state deletion
I2 memory deletion
I3 representation freezing
I4 prediction-error injection
I5 counterfactual action substitution
I6 observation perturbation
I7 history-preserving causal perturbation
I8 online distribution shift
```

The future executable preflight must include heldout pairwise compositions of
these interventions.

## Baselines And Controls

Every listed control must be real implemented code or a real closed-form
decision procedure. Name-only controls are invalid. Hardcoded competence or
fairness attestations are invalid.

Required controls:

```text
full_history_count_statistic
online_count_statistic
fsm_automaton
online_fsm
graph_lookup
transition_table
successor_map
count_table
fsm_planner
episodic_traversal
online_graph_lookup
online_transition_table
online_successor_map
online_count_table
online_fsm_planner
online_episodic_traversal
knn_episodic
online_knn_episodic
summary_statistic
online_summary_statistic
causal_table
intervention_labeled_graph_cache
behavior_only_replay
trace_only_replay
graph_cache_trace_generator
random_representation
shuffled_label
shuffled_outcome
oracle_leakage_probe
```

`intervention_labeled_graph_cache` and `causal_table` may use
`intervention_condition` when the witness receives the same label. If a fair
control matches all frozen criteria, the preflight fails.

## Resource Budgets

Freeze these default budgets before implementation:

```text
memory_budget = 128 key-value entries, each <= 256 bytes
state_budget = 16 KiB serialized state per system step
trace_storage_budget = unbounded write-only audit output for all systems
online_update_budget = one update call per environment step
lookup_budget = 128 key reads or graph traversals per step
replay_budget = one deterministic replay per system per frozen seed
per_step_compute_budget_if_applicable = 100000 primitive operations or declared unbounded for all systems
```

Each required control must pass a competence calibration task inside the
budget. If the budget starves a control, the task fails by resource asymmetry.

## Trace / Replay Requirement

All systems must emit step-interleaved, append-only, hash-chained traces before
verifier outcome or later behavior-probe results are known.

Minimum fields:

```text
episode_id
step_id
previous_trace_hash
current_trace_hash
commit_index
system_id
intervention_condition
observation
action
prediction_before_observation
actual_observation
prediction_error_or_update_signal
internal_state_before_update_hash
internal_state_after_update_hash
state_delta_hash
memory_read_keys
memory_write_keys
retrieval_hits
resource_usage
access_manifest
```

Replay must recompute allowed update paths step by step. Schema-only replay
fails. Trace fields are write-only audit outputs and may not become hidden
working memory.

## Frozen Metrics

Primary metrics:

```text
intervention_response_match
internal_update_trace_match
later_behavior_change_match
```

Default solve rule:

```text
match = frozen metric distance inside equivalence band
reproduce = match all three primary metrics on the same frozen split
solve = reproduce and match the primary separation statistic
```

Metric thresholds:

```text
intervention_response_match threshold = match_rate >= 0.95 with distance <= 0.05
internal_update_trace_match threshold = match_rate >= 0.90 with distance <= 0.10
later_behavior_change_match threshold = match_rate >= 0.95 with distance <= 0.05
seed_aggregation = lower 95 percent bootstrap confidence bound must meet threshold
```

No metric or threshold may be selected after observing results.

## Separation Statistic

Primary statistic:

```text
resource_normalized_heldout_composition_update_divergence
```

A witness passes this statistic only if it exceeds the best fair online cheap
control by more than 0.10 after resource normalization, and the lower 95
percent bootstrap confidence bound of the margin is greater than 0.05.

Required secondary diagnostics:

```text
prediction_error_causal_use_profile
deletion_sensitivity_profile
```

If the best fair online cheap control matches the witness on the frozen
primary statistic, the executable preflight fails.

## Ablation

Required ablations:

```text
state deletion ablation
memory deletion ablation
representation freeze ablation
prediction-error removal ablation
counterfactual action removal ablation
intervention label shuffle
outcome shuffle
random representation replacement
trace-only replay
behavior-only replay
```

If ablations do not change later behavior where the contract predicts they
should, the preflight fails.

## Behavior Probes

Required probes:

```text
future_action_distribution_shift
future_policy_choice_change
future_prediction_change
future_error_recovery_change
future_intervention_probe_response
```

Minimum normalized paired effect size is 0.10. Effects that appear only under
post-hoc-selected probes are invalid.

## Stage0 Freeze

Before any verifier run, create:

```text
artifacts/process_intervention_preflight_001b/stage0_freeze_manifest.json
artifacts/process_intervention_preflight_001b/sha256_manifest.json
artifacts/process_intervention_preflight_001b/external_anchor.json
```

The freeze must precede the anchor, and the anchor must precede the first
verifier run.

Freeze:

```text
task_card_hash
environment_family_definition
train_test_split
intervention_set
control_implementations_or_closed_form_procedures
control_access_contracts
resource_budgets
trace_commitment_protocol
match_metrics
separation_statistics
behavior_probe_protocol
oracle_leakage_probes
acceptance_gate
claim_ceiling
stop_conditions
```

## Acceptance Gate

Executable acceptance must be computed by independent verifier code or a
closed-form audit. The candidate system must not self-attest acceptance.

The future executable preflight may return bounded pass only if:

```text
negative_evidence_admission_passed = true
stage0_freeze_complete_before_first_run = true
all_required_controls_implemented_or_closed_form = true
control_competence_calibration_passed = true
trace_commitment_hash_chain_valid = true
allowed_update_path_replay_valid = true
memory_key_fidelity_replay_valid = true
resource_budget_symmetry_valid = true
oracle_leakage_probe_clean = true
no_fair_online_control_solves = true
primary_separation_statistic_exceeds_best_fair_online_control = true
required_ablations_have_predicted_later_behavior_effect = true
claim_ceiling_enforced = true
no_forbidden_scope_leak = true
```

The acceptance gate must not be tested by asserting a pass verdict string.
Tests must assert structure, frozen inputs, replayability, boundary flags, and
allowed failure verdicts.

## Failure Verdicts

```text
process_intervention_preflight_001b_failed_negative_evidence_admission
process_intervention_preflight_001b_failed_stage0_freeze_or_anchor
process_intervention_preflight_001b_failed_missing_real_control
process_intervention_preflight_001b_failed_control_calibration
process_intervention_preflight_001b_failed_trace_commitment
process_intervention_preflight_001b_failed_update_path_replay
process_intervention_preflight_001b_failed_memory_key_fidelity
process_intervention_preflight_001b_failed_resource_asymmetry
process_intervention_preflight_001b_failed_oracle_leakage
process_intervention_preflight_001b_failed_control_intervention_response_match
process_intervention_preflight_001b_failed_control_update_trace_match
process_intervention_preflight_001b_failed_control_later_behavior_match
process_intervention_preflight_001b_failed_control_separation_statistic_match
process_intervention_preflight_001b_failed_ablation_no_later_behavior_effect
process_intervention_preflight_001b_failed_verdict_string_test
process_intervention_preflight_001b_failed_self_attestation
process_intervention_preflight_001b_failed_scope_leak
process_intervention_preflight_001b_bounded_pass
```

## Stop Conditions

Stop if:

```text
any required control remains name-only
controls are weakened, denied fair access, or resource-starved
match/reproduce/solve metrics are changed after seeing results
trace is generated post hoc for a non-generator system
trace fields become hidden working memory
schema-only replay substitutes for step-level replay
intervention-labeled graph/cache is denied fair intervention labels
fair online cheap control matches the witness
lexical admission is treated as mechanism evidence
old experiments are rerun or old artifacts are repaired
new Fable or model-poisoning audit is created
Fable causality is claimed without provenance, diff, and mechanism evidence
mechanism implementation begins before Stage0 authorization
training begins
model-class reset is authorized
Gate1 is reopened
same-agent bridge is drafted
EGO mainline is touched
LLM/RAG/companion/emotion/relationship/user-model modules are introduced
```

## Rollback Plan

If scope is violated, remove only newly created 001B files and preserve a
failure manifest under `artifacts/process_intervention_preflight_001b/`. Do
not rewrite old artifacts, do not patch failures into passes, do not normalize
001C, do not reopen Gate1, and do not touch EGO.

## Claim Ceiling

Maximum allowed claim if the future executable preflight passes:

```text
bounded offline evidence that PROCESS-INTERVENTION-PREFLIGHT-001B survived its frozen controls, ablations, replay checks, and separation statistic
```

This does not prove mechanism correctness, online adaptation in general,
causal model correctness, model-class reset readiness, Gate1 readiness,
same-agent bridge readiness, EGO readiness, agency, consciousness, subjective
experience, functional subjectivity, emotion, relationship learning, companion
readiness, AGI, or Fable causality.

## What This Draft Does Not Prove

This draft does not prove the future preflight will pass. It does not prove
the witness exists. It does not prove the triple target separates a mechanism
from cheap controls. It only defines the next executable-preflight contract
well enough for an authorization review to accept, reject, or require a narrow
repair.

