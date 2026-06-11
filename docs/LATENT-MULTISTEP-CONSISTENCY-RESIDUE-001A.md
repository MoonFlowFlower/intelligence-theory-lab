# LATENT-MULTISTEP-CONSISTENCY-RESIDUE-001A

## Title

Bounded residue test for the multi-step latent-consistency objective after Gate1 local package failure.

## Task identity

```text
task_id = LATENT-MULTISTEP-CONSISTENCY-RESIDUE-001A
status = executable_after_stage0_freeze_and_anchor
research_layer = mechanism hypothesis layer / narrow residue test
parent_result = GATE1-REPLAY-CONSOLIDATION-EXEC-TASKCARD-001
parent_verdict = gate1_preflight_failed_graph_cache_collapse
candidate_A_status = closed_current_operationalization
candidate_B_status = failed_but_retained_as_multistep_consistency_residue
```

## Authorization boundary

This task authorizes a bounded isolated experiment only for the multi-step latent-consistency residue observed in Candidate B.

Authorized paths:

```text
src/latent_multistep_consistency_residue/
tests/test_latent_multistep_consistency_residue.py
artifacts/latent_multistep_consistency_residue_001a/
docs/LATENT-MULTISTEP-CONSISTENCY-RESIDUE-001A.md  # if task card must be saved
```

Forbidden paths:

```text
EGO mainline
Gate 0 / 001C frozen documents
GATE1-REPLAY-CONSOLIDATION-EXEC-TASKCARD-001 artifacts
GATE1-REPLAY-CONSOLIDATION-TASKCARD-001A / 001B
previous artifacts except read-only citation
any companion / LLM / RAG / emotion / relationship / user-model module
```

Do not modify prior artifacts. Prior results may be read only as historical evidence.

This task does not authorize:

* Gate0→Gate1 same-agent bridge
* EGO integration
* reopening Candidate A
* re-running Gate1 package
* counterfactual action replay
* consciousness / agency / functional-subject / companion-readiness / EGO-readiness / AGI claims
* predictive superiority over retrieval
* total theory proof
* winner selection

## Problem definition

The prior Gate1 package failed. Candidate A collapsed under graph/cache and generic replay controls. Candidate B failed the frozen package rule because `shuffled_replay_B` matched it, but B left a narrow residue: the multi-step latent-consistency objective appeared to beat single-step replay, random replay, equal-compute training, online-only training, and cache/retrieval controls in the prior small setting.

Correct question:

Is the multi-step latent-consistency objective itself a real, reproducible, auditable mechanism residue, or was the prior B signal an artifact of shuffled replay equivalence, optimizer path, tiny environment structure, weak function approximation baselines, or redundant evaluation slices?

Wrong questions:

* Can we make Gate1 pass?
* Can we rescue Candidate A?
* Can we prove replay/consolidation?
* Can we bridge Gate0 to Gate1 now?
* Can we build EGO memory?
* Can we infer agency, consciousness, functional subject, companion readiness, or AGI?

## Candidate under test

```text
candidate_id = R
name = multi_step_latent_consistency_objective
role = narrow_residue_candidate
```

Candidate R is not full Gate1 replay/consolidation.

Candidate R is only the following claim:

Training with a multi-step latent-consistency objective produces a durable, reproducible model-state change distinguishable from single-step replay, shuffled same-loss replay, reverse-order replay, random replay, equal-compute training, online-only learning, cache/retrieval baselines, and stronger function-approximation baselines in a preregistered environment where lookup/table dominance is not structurally decisive.

## Claim ceiling

At most:

```text
bounded local residue evidence that a multi-step latent-consistency objective was distinguishable from the listed controls under frozen margins in the preregistered setting
```

This cannot support:

* Gate1 package pass
* replay/consolidation necessity
* predictive superiority over retrieval in general
* Gate0→Gate1 bridge evidence
* same-agent continuity evidence
* EGO readiness
* companion readiness
* functional-subject evidence
* agency
* consciousness
* subjective experience
* real emotion
* AGI
* total theory proof

## Stage 0 — freeze, anchor, and preregistration

Before any candidate/control run:

1. Save this task card if needed.
2. Record task-card hash.
3. Record parent final report hash, result.json hash, and baseline_comparison.json hash.
4. Freeze margins.
5. Freeze seeds.
6. Freeze environment generator.
7. Freeze evaluation slices.
8. Freeze baseline list.
9. Freeze hyperparameter budgets.
10. Freeze compute-matching basis.
11. Create external time anchor.
12. Record first_run_start_time only after the external anchor exists.

If external time anchor cannot be created or verified, stop before running.

No pilot candidate/control comparison may occur before anchor.

Smoke tests are allowed only on placeholder data and may not record candidate-vs-control metrics.

## Frozen margin policy

Use the conservative zero-advantage rule.

For higher-is-better metrics:

```text
candidate_advantage = candidate_score - control_score
```

For lower-is-better metrics, including NLL / prediction loss / latent consistency loss:

```text
candidate_advantage = control_score - candidate_score
```

Candidate is distinguishable from a control only if:

```text
paired_candidate_advantage_lower_bound > 0
```

A control matches the candidate if:

```text
paired_candidate_advantage_lower_bound <= 0
```

If paired uncertainty cannot be computed, use the stricter fallback:

```text
candidate_advantage_must_be_positive_on_every_required_seed_and_every_required_evaluation_slice
```

Ties, overlaps, noisy differences, or ambiguous comparisons count as control matches.

Post-hoc margin changes are forbidden.

## Environment requirement

The prior environment had two caveats:

```text
count_table dominated Candidate A structurally
B_slice_4 became redundant with B_slice_1 after repair
```

This task must use a preregistered environment family that avoids both failure modes without disabling controls by construction.

Required environment properties:

```text
environment_family = latent_alias_sequence_or_pomdp_family
partial_observability = required
latent_state_not_directly_observed = required
multi_step_prediction_needed = required
heldout_sequences = required
heldout_transition_or_alias_patterns = required
B_slice_redundancy_check = required
lookup_triviality_check = required
controls_disabled_by_construction_check = required
```

The environment must not be lookup-trivial.

The environment must not make graph/cache or retrieval controls impossible by construction.

If count/table lookup or nearest-neighbor sequence retrieval dominates everything, the result is blocked, not candidate success.

If controls are disabled by construction, the result is blocked, not candidate success.

## Required evaluation slices

At minimum:

```text
R_slice_1 = cache_free_heldout_sequence_prediction
R_slice_2 = hidden_state_cache_removed
R_slice_3 = longer_context_retrieval_removed
R_slice_4 = heldout_alias_or_state_disambiguation
R_slice_5 = nonredundant_long_horizon_prediction
```

Before running, prove or check:

```text
R_slice_4_not_equivalent_to_R_slice_1 = true
R_slice_5_not_equivalent_to_R_slice_1 = true
```

If slices collapse into each other, stop and repair before any run. Preserve failure manifest and re-anchor if repaired.

## Candidate R requirements

Candidate R must include:

```text
multi_step_latent_consistency_loss = present
latent_trace_recomputed_from_raw_chunks = true
encoder_dynamics_snapshots_frozen = true
hidden_state_cache_at_evaluation = forbidden
prefix_cache_at_evaluation = forbidden
longer_context_retrieval_at_evaluation = forbidden
sequence_lookup_at_evaluation = forbidden
raw_chunk_access_on_evaluation_forward_path = forbidden
```

Raw chunks may be used only for offline lineage verification, not for evaluation outputs.

Candidate R must log:

```text
model_snapshot_before
model_snapshot_after
latent_recomputation_record
chunk_boundaries
burn_in_length
multi_step_depth
training_events
evaluation_queries
```

## Mandatory baselines and controls

### A. Prior failure control

The prior killer control must be first-class:

```text
shuffled_same_loss_replay = mandatory
```

Candidate R must beat shuffled same-loss replay under the frozen margin rule on every required slice.

If not:

```text
verdict = latent_residue_failed_shuffled_same_loss_collapse
```

### B. Order controls

Required:

```text
same_item_multiset_shuffled_order
same_item_multiset_reverse_order
same_item_multiset_random_order
same_item_multiset_original_order
matched_optimizer_state
matched_compute
matched_seeds
```

If order controls match Candidate R:

```text
verdict = latent_residue_failed_order_geometry_collapse
```

### C. Generic replay controls

Required:

```text
single_step_chunk_replay
generic_chunk_replay
random_replay
uniform_replay
equal_compute_extra_training
same_data_online_only
frozen_theta
```

If any generic replay control matches:

```text
verdict = latent_residue_failed_generic_replay_collapse
```

### D. Cache / retrieval controls

Required:

```text
hidden_state_cache
prefix_cache
longer_context_retrieval
sequence_lookup
nearest_neighbor_sequence_retrieval
episodic_sequence_retrieval
```

If any cache/retrieval control matches:

```text
verdict = latent_residue_failed_cache_or_retrieval_collapse
```

### E. Strong function-approximation baselines

Required:

```text
same_architecture_no_multistep_loss
larger_capacity_single_step_model
equal_parameter_budget_model
equal_compute_model
stronger_sequence_model_without_multistep_consistency
```

If any stronger function-approximation baseline matches:

```text
verdict = latent_residue_failed_function_approximation_baseline
```

The stronger baseline must not use forbidden runtime cache/retrieval.

### F. Graph / table controls

If the environment is finite enough for table controls, include:

```text
count_table
transition_table
graph_lookup
compressed_map
```

If table/graph controls match:

```text
verdict = latent_residue_failed_graph_or_table_collapse
```

If table/graph controls cannot be fairly implemented because the environment disables them by construction:

```text
verdict = latent_residue_blocked_controls_disabled_by_construction
```

## Control parity

Controls must not be sandbagged.

Required:

```text
control_implementation_quality >= candidate_implementation_quality
control_tuning_budget >= candidate_tuning_budget
control_compute_budget matched_or_greater
control_competence_floor_required = true
```

If a control fails competence:

```text
verdict = control_incompetent_invalid_comparison
```

Never convert incompetent controls into candidate success.

## Runtime-access attestation

Evaluation must run in isolated subprocesses or equivalent isolation.

Forbidden runtime objects:

```text
stored_hidden_states
hidden_state_cache
prefix_cache
chunk_checkpoint_library
longer_context_retrieval_index
sequence_lookup_table
nearest_neighbor_sequence_index
raw_chunks_on_forward_path
training_replay_buffer_on_forward_path
graph_or_table_cache_unless_in_control_arm
```

Attestation must include:

```text
reachable_object_inventory
reachable_object_hashes
forbidden_object_absence_proof
loaded_model_hashes
loaded_cache_hashes
loaded_index_hashes
loaded_store_hashes
evaluation_process_id
```

If attestation only says "we did not use X" without an inventory:

```text
verdict = runtime_access_attestation_invalid
```

## Lineage ledger

Every initiated run must be logged, including aborted and failed runs.

Required fields:

```text
run_id
seed
candidate_or_control_id
environment_id
environment_hash
slice_id
chunk_ids
chunk_boundaries
burn_in_length
multi_step_depth
model_snapshot_before
model_snapshot_after
training_event_ids
evaluation_query_ids
runtime_access_manifest
forbidden_object_inventory
metric_outputs
candidate_advantage_records
failure_manifest_if_any
```

If any run or seed is dropped after outcome inspection:

```text
verdict = latent_residue_failed_run_ledger_incomplete
```

## Gate 0 interface boundary

Allowed variables:

```text
raw_trace_items
actions
observations
belief_state_if_derived
theta_parameters
prediction_error
uncertainty
chronology
commitment_records
```

Blocked unless explicitly reduced:

```text
reward
value
goal
preference
affect
viability
social_latent
user_model
LLM_semantic_memory
external_world_model
hidden_teacher
future_oracle
counterfactual_action_replay
```

Counterfactual action replay remains excluded in every role.

## Anti-hardcoding scan

Must check:

```text
no_hand_picked_seeds
no_seed_dropping
no_hand_curated_chunks_after_outcome_inspection
no_post_hoc_burn_in_tuning
no_post_hoc_multistep_depth_tuning
no_post_hoc_margin_change
no_control_sandbagging
no_environment_design_that_trivially_favors_candidate
no_environment_design_that_disables_controls
no_hidden_if_else
no_test_only_logic
no_post_hoc_lineage_repair
```

If any violation occurs:

```text
verdict = latent_residue_failed_hardcoding
```

## Acceptance requirements

Universal acceptance:

```text
external_anchor_present = true
margin_freeze_before_first_run = true
all_margins_predeclared = true
environment_preregistered = true
runtime_access_attestation_pass = true
lineage_reconstruction_pass = true
run_ledger_complete = true
control_competence_pass = true
gate0_interface_audit_pass = true
anti_hardcoding_scan_pass = true
counterfactual_action_replay_absent = true
```

Candidate R acceptance:

```text
candidate_R_beats_shuffled_same_loss_replay = true
candidate_R_beats_reverse_order_replay = true
candidate_R_beats_single_step_chunk_replay = true
candidate_R_beats_random_replay = true
candidate_R_beats_equal_compute_extra_training = true
candidate_R_beats_same_data_online_only = true
candidate_R_beats_hidden_state_cache = true
candidate_R_beats_longer_context_retrieval = true
candidate_R_beats_sequence_lookup = true
candidate_R_beats_stronger_function_approximation_baseline = true
candidate_R_passes_all_required_slices = true
slice_redundancy_check_pass = true
```

All comparisons use the conservative zero-advantage rule.

If any required baseline matches, Candidate R fails.

## Allowed verdicts

```text
latent_residue_bounded_pass
latent_residue_failed_shuffled_same_loss_collapse
latent_residue_failed_order_geometry_collapse
latent_residue_failed_generic_replay_collapse
latent_residue_failed_cache_or_retrieval_collapse
latent_residue_failed_function_approximation_baseline
latent_residue_failed_graph_or_table_collapse
latent_residue_failed_runtime_access_violation
latent_residue_failed_lineage_nonidentifiability
latent_residue_failed_gate0_interface_violation
latent_residue_failed_hardcoding
latent_residue_failed_run_ledger_incomplete
latent_residue_blocked_environment_lookup_triviality
latent_residue_blocked_controls_disabled_by_construction
latent_residue_blocked_slice_redundancy
control_incompetent_invalid_comparison
```

## Stop conditions

Stop immediately if:

```text
counterfactual_action_replay_reintroduced = true
candidate_A_reintroduced = true
Gate1_package_claim_reintroduced = true
same_agent_bridge_started = true
EGO_mainline_touched = true
margins_changed_after_first_run = true
external_anchor_missing = true
pre_freeze_comparative_run_detected = true
runtime_forbidden_object_reachable = true
lineage_cannot_be_reconstructed = true
run_or_seed_dropped = true
shuffled_same_loss_control_missing = true
strong_function_approximation_baseline_missing = true
slice_redundancy_detected_after_run = true
environment_lookup_trivial = true
environment_disables_controls_by_construction = true
```

## Required outputs

All outputs must be written under:

```text
artifacts/latent_multistep_consistency_residue_001a/
```

Required files:

```text
task_manifest.json
margin_freeze_record.json
external_anchor_record.json
environment_preregistration.json
slice_redundancy_report.json
control_competence_report.json
runtime_access_attestation/
lineage_ledger.jsonl
baseline_comparison.json
candidate_result.json
anti_hardcoding_audit.json
gate0_interface_audit.json
stop_condition_report.json
final_report.md
result.json
```

Tests:

```text
tests/test_latent_multistep_consistency_residue.py
```

Implementation must stay under:

```text
src/latent_multistep_consistency_residue/
```

## Final report shape

Final report must include:

```text
A. Executive verdict
B. Scope confirmation
C. Parent result inheritance
D. Environment preregistration
E. Slice redundancy report
F. Candidate R result
G. Shuffled same-loss control result
H. Order control results
I. Generic replay control results
J. Cache/retrieval control results
K. Strong function-approximation baseline results
L. Graph/table control results if applicable
M. Runtime-access attestation
N. Lineage reconstruction
O. Gate 0 interface audit
P. Anti-hardcoding audit
Q. Stop-condition report
R. Claim ceiling
S. What this does not prove
T. Rollback or next-action recommendation
```

## Rollback plan

If Candidate R fails:

```text
if shuffled_same_loss_matches:
    close_residue_as_order_or_replay_geometry_artifact

if function_approximation_baseline_matches:
    close_residue_as_function_approximation_artifact

if cache_or_retrieval_matches:
    close_residue_as_retrieval_artifact

if graph_or_table_matches:
    close_residue_as_lookup_artifact

if environment_invalid:
    preserve_failure_manifest_and_reanchor_before_any_rerun
```

If Candidate R passes:

```text
do_not_claim_gate1_pass
do_not_claim_replay_consolidation_success
next_allowed_step = draft_same_agent_bridge_protocol_for_this_narrow_residue_only
```

## What this task does not prove

This task does not prove Gate1 passed.

It does not prove replay/consolidation works.

It does not prove replay/consolidation is necessary.

It does not prove predictive superiority over retrieval.

It does not prove same-agent continuity.

It does not prove Gate0→Gate1 bridge evidence.

It does not prove agency, consciousness, functional subject, companion readiness, EGO readiness, or AGI.

It only tests whether the narrow multi-step latent-consistency residue survives stronger local falsification.
