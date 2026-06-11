# GATE1-REPLAY-CONSOLIDATION-EXEC-TASKCARD-001

```text
task_id = GATE1-REPLAY-CONSOLIDATION-EXEC-TASKCARD-001
status = human_signed_margin_policy_frozen_pending_stage0_anchor
card_type = executable Gate 1 preflight task card
research_layer = mechanism hypothesis layer / bounded execution preflight
source_meta_card = GATE1-REPLAY-CONSOLIDATION-TASKCARD-001B
source_draft = GATE1-REPLAY-CONSOLIDATION-EXEC-TASKCARD-DRAFT-001
freeze_label = GATE1-REPLAY-CONSOLIDATION-PREFLIGHT-FREEZE-001
execution_authorized = stage0_pre_run_finalization_only_until_first_run_allowed_true
```

## 0. Human sign-off and margin-freeze status

Human owner has approved promotion from draft to executable task card under the following frozen scope.

```text
human_signoff_status = approved_by_human_owner
human_owner_decision = proceed_to_executable_gate1_preflight_card
human_signoff_date = 2026-06-10
authorized_scope = bounded Gate 1 preflight execution only
```

Execution remains blocked until all margin-freeze fields below are filled.

```text
margin_freeze_completed = true
external_time_anchor_completed = true
first_run_allowed = true
```

No run, training, evaluation, pilot, calibration, benchmark, or data generation may occur until:

```text
margin_freeze_completed = true
external_time_anchor_completed = true
first_run_allowed = true
```

## 1. Executive authorization boundary

This card authorizes a bounded Gate 1 preflight execution only after margin freeze.

It does not authorize:

* EGO mainline integration
* agent architecture changes
* companion behavior
* LLM / RAG / emotion / relationship / affect / viability / user-model modules
* consciousness, subjective experience, real emotion, self-awareness, agency, functional-subject, companion-readiness, EGO-readiness, electronic-life, or AGI claims
* winner selection between candidates
* predictive superiority over retrieval
* open-world robustness claim
* total theory proof
* modifying Gate 0 evidence or Gate 0 claim ceiling
* modifying Phase 1 / Phase 2 / Phase 3 / Phase 2R / Phase 3 Delta / Phase 4 records
* reintroducing counterfactual action replay
* demoting mandatory controls
* changing margins after seeing results
* dropping failed or aborted runs
* post-hoc lineage repair

## 2. Inherited frozen scope

```text
1.  fast_to_slow_structure_transfer        = primary candidate
2.  latent_dynamics_consistency_replay     = secondary candidate
3.  counterfactual_action_replay           = excluded in every role
4.  graph_cache_control_stack              = first-class mandatory
5.  generic_replay_buffer_control_stack    = first-class mandatory
6.  comparison_margins                     = predeclared before any run
7.  runtime_access_attestation             = mandatory
8.  source_deletion_timing_preregistration = mandatory
9.  lineage_records                        = mandatory
10. anti_hardcoding_scan                   = mandatory
11. control_parity                         = mandatory
12. environment_preregistration            = mandatory
13. complete_run_ledger                    = mandatory
```

If any item above is weakened, omitted, or reinterpreted, execution must stop.

## 3. Correct problem definition

The correct question:

> Can a bounded Gate 1 preflight execution distinguish strict source-removed fast-to-slow transfer, or strict cache-free latent-dynamics replay, from retrieval / cache / generic replay explanations under frozen margins and mandatory controls?

Wrong questions:

* How can we make Gate 1 pass?
* Which mechanism is the winner?
* How do we build EGO memory?
* How do we prove replay / consolidation?
* How do we show agency, consciousness, or functional-subject evidence?
* How do we integrate this into EGO?
* How do we make a useful companion system?

Any output organized around those wrong questions is invalid.

## 4. Candidate hierarchy

### Candidate A — primary

```text
candidate_id = A
name = tightened_fast_to_slow_structure_transfer
role = primary_candidate
```

Definition:

Replay / transfer may use a fast episodic source, teacher, generator, synthetic library, or source snapshot only during the transfer event. The claimed effect must later be expressed by slow model state or slow parameters under slow-only evaluation after all fast/source objects are removed.

Allowed during transfer only, with lineage:

```text
fast_source_used_during_transfer = allowed_with_lineage
teacher_used_during_transfer = allowed_with_lineage
generator_used_during_transfer = allowed_with_lineage
synthetic_library_used_during_transfer = allowed_with_lineage
source_snapshot_used_during_transfer = allowed_with_lineage
```

Forbidden at evaluation:

```text
fast_source_available_at_evaluation = forbidden
teacher_available_at_evaluation = forbidden
generator_available_at_evaluation = forbidden
synthetic_library_available_at_evaluation = forbidden
summary_memory_available_at_evaluation = forbidden
teacher_output_cache_available_at_evaluation = forbidden
generator_as_memory_available_at_evaluation = forbidden
nearest_neighbor_index_available_at_evaluation = forbidden
graph_cache_available_at_evaluation = forbidden
transition_table_available_at_evaluation = forbidden
successor_map_cache_available_at_evaluation = forbidden
predecessor_map_cache_available_at_evaluation = forbidden
direct_episodic_traversal_available_at_evaluation = forbidden
```

Candidate A effect carrier:

```text
effect_carrier = slow_model_state_or_slow_parameters
not_effect_carrier = fast_store_or_teacher_or_generator_or_summary_cache
```

### Candidate B — secondary

```text
candidate_id = B
name = tightened_latent_dynamics_consistency_replay
role = secondary_candidate
```

Definition:

Replay uses preregistered raw sequence chunks to update parameters governing recomputed multi-step latent or recurrent dynamics. Latent/recurrent traces must be exactly recomputable from raw chunks plus frozen model snapshots.

Allowed only as derived, auditable variables:

```text
latent_state = allowed_only_if_recomputable_from_raw_trace_plus_frozen_snapshot
recurrent_state = allowed_only_if_recomputable_from_raw_trace_plus_frozen_snapshot
latent_trace = allowed_only_if_recomputable_from_raw_trace_plus_frozen_snapshot
```

Forbidden at evaluation:

```text
stored_hidden_state_at_evaluation = forbidden
hidden_state_cache_at_evaluation = forbidden
prefix_cache_at_evaluation = forbidden
longer_context_retrieval_at_evaluation = forbidden
chunk_checkpoint_library_at_evaluation = forbidden
sequence_lookup_at_evaluation = forbidden
nearest_neighbor_sequence_retrieval_at_evaluation = forbidden
raw_chunk_access_on_evaluation_forward_path = forbidden
```

Candidate B evaluation-path rule:

* Evaluation forward path must be computable without raw chunks, stored hidden states, caches, prefix libraries, or retrieval indices.
* Raw chunk access is allowed only inside a separate offline verification replay for recomputability and lineage.
* Offline verification replay outputs must not be used as evaluation outputs.
* Any recomputation protocol that gives the evaluation forward path access to raw chunks, caches, or sequence retrieval collapses Candidate B to retrieval and fails.

### Excluded candidate

```text
candidate_id = X
name = gate0_bounded_counterfactual_action_replay
role = excluded_in_every_role
```

No exception clause exists.

Counterfactual action replay must not appear as:

* candidate
* auxiliary mechanism
* data augmenter
* synthetic label generator
* replay item type
* salience source
* ablation target
* hidden baseline helper
* optional extension

If reintroduced, execution stops.

## 5. Hypotheses

### H1 — primary

Strict source-removed fast-to-slow transfer may produce a durable slow-state change that remains observable under slow-only evaluation after all fast/source objects are removed.

H1 is admissible only if distinguishable from:

* summary-memory retrieval
* teacher-output cache
* generator-as-memory
* synthetic library lookup
* direct episodic retrieval
* graph/cache lookup
* transition-table lookup
* successor-map cache
* generic replay-buffer training
* equal-compute extra training

### H2 — secondary

Strict cache-free latent-dynamics consistency replay may produce a durable latent/recurrent parameter-state change that remains observable with hidden-state caches, prefix caches, stored hidden states, and longer-context retrieval disabled.

H2 is admissible only if distinguishable from:

* hidden-state cache
* prefix-cache reuse
* longer-context retrieval
* sequence lookup
* generic chunk replay
* same-data online-only learner
* equal-compute extra training

### H0 — null

All apparent Gate 1 effects can be explained by one or more of:

* runtime retrieval
* summary memory
* graph/cache lookup
* transition-table lookup
* successor/predecessor-map cache
* generic replay-buffer training
* equal-compute extra training
* hidden-state cache
* prefix cache
* teacher-output cache
* generator-as-memory
* synthetic library lookup
* post-hoc lineage construction
* hand-coded schedule
* hand-curated chunking
* tuned deletion timing
* seed selection
* weak controls
* environment design favoring the candidate

## 6. Claim ceiling

This execution can support at most:

> bounded Gate 1 preflight evidence that strict source-removed fast-to-slow transfer, or strict cache-free latent-dynamics replay, produced durable, traceable, replayable model-state change distinguishable from the mandatory control stacks under frozen margins in the preregistered setting.

It cannot support:

* consciousness
* subjective experience
* real emotion
* self-awareness
* agency
* functional-subject evidence
* electronic life
* AGI
* companion readiness
* EGO mainline readiness
* predictive-performance superiority over retrieval
* open-world robustness
* outcome unpredictability
* total theory proof
* exhaustiveness of retrieval controls

A future pass means only:

```text
not_matched_by_listed_controls_under_predeclared_rule_in_this_setting
```

It must never be rewritten as:

```text
not_explainable_by_retrieval_in_general
```

## 7. Margin-freeze block

Execution is blocked until this section is filled and externally anchored.

### 7.1 Margin-freeze metadata

Stage 0 must create a separate auditable margin-freeze / readiness record before the first candidate/control run. The fields below are not optional; they are to be recorded by Stage 0, not invented post hoc.

```text
margin_freeze_event = stage0_margin_policy_anchor_for_conservative_zero_advantage_rule
margin_freeze_commit_hash = record_current_task_card_commit_or_file_hash_before_first_run
external_time_anchor = required_before_first_run
external_time_anchor_method = repository_remote_push_or_other_auditable_external_timestamp
external_time_anchor_timestamp = record_before_first_run
first_run_start_time = record_only_after_external_anchor
margin_hash = hash_of_sections_7_and_margin_freeze_block
margin_provenance_record = Phase4_001B_conservative_anti_fake_pass_policy
```

Required ordering rule:

```text
margin_freeze_commit_time < first_run_start_time
```

Required external anchor:

```text
external_time_anchor_required = true
```

Pre-freeze comparative runs are forbidden.

```text
pre_freeze_candidate_or_control_runs = forbidden
```

Smoke tests are allowed only if all are true:

```text
smoke_test_uses_placeholder_data = true
smoke_test_data_disjoint_from_evaluation_tasks = true
smoke_test_records_no_candidate_vs_control_metrics = true
smoke_test_logged_in_lineage = true
```

### 7.2 Primary metric definitions

The task uses comparison-oriented metrics. All task-specific scores must be converted to the candidate-advantage orientation defined in the Margin-freeze block.

```text
primary_candidate_A_metric = paired_candidate_advantage_lower_bound_on_A_required_slices_after_source_deletion
primary_candidate_B_metric = paired_candidate_advantage_lower_bound_on_B_required_cache_free_slices
primary_control_match_metric = paired_candidate_advantage_lower_bound <= 0
model_state_delta_metric = required_snapshot_delta_present_and_logged_not_sufficient_for_success
trace_reconstruction_metric = exact_reconstruction_pass_required_for_all_required_lineage_records
runtime_access_violation_metric = forbidden_runtime_object_count_must_equal_0
lineage_completeness_metric = required_lineage_fields_present_and_reconstructable_rate_must_equal_1.0
```

### 7.3 Frozen comparison margins

The frozen comparison policy is conservative zero-advantage. No positive slack is granted to the candidate. A control matches the candidate whenever the candidate's paired advantage lower bound is not strictly positive.

```text
A_vs_graph_cache_match_margin = 0.0
A_vs_transition_table_match_margin = 0.0
A_vs_successor_map_cache_match_margin = 0.0
A_vs_predecessor_map_cache_match_margin = 0.0
A_vs_count_table_predictor_match_margin = 0.0
A_vs_direct_episodic_graph_traversal_match_margin = 0.0
A_vs_generic_replay_match_margin = 0.0
A_vs_same_data_online_only_match_margin = 0.0
A_vs_equal_compute_extra_training_match_margin = 0.0
A_vs_summary_memory_match_margin = 0.0
A_vs_teacher_output_cache_match_margin = 0.0
A_vs_generator_as_memory_match_margin = 0.0
A_vs_synthetic_library_lookup_match_margin = 0.0
A_vs_direct_episodic_retrieval_match_margin = 0.0

B_vs_hidden_state_cache_match_margin = 0.0
B_vs_prefix_cache_match_margin = 0.0
B_vs_longer_context_retrieval_match_margin = 0.0
B_vs_sequence_lookup_match_margin = 0.0
B_vs_nearest_neighbor_sequence_retrieval_match_margin = 0.0
B_vs_generic_chunk_replay_match_margin = 0.0
B_vs_same_data_online_only_match_margin = 0.0
B_vs_equal_compute_extra_training_match_margin = 0.0
B_vs_random_replay_match_margin = 0.0
B_vs_shuffled_replay_match_margin = 0.0

control_competence_floor_margin_graph_cache = exact_success_on_preregistered_pure_lookup_sanity_task
control_competence_floor_margin_generic_replay = nonzero_learning_or_loss_reduction_on_preregistered_replay_friendly_sanity_task
environment_lookup_triviality_rule = block_if_lookup_or_cache_solves_all_required_slices_by_construction
environment_controls_disabled_by_construction_rule = block_if_environment_prevents_mandatory_controls_from_exercising_intended_access_pattern_or_competence
```

### 7.4 Margin provenance

```text
margin_id = conservative_zero_advantage_margin_policy
margin_value_or_rule = candidate_distinguishable_from_control_if_paired_candidate_advantage_lower_bound_greater_than_0
margin_scope = all_candidate_vs_control_comparisons_and_required_evaluation_slices
margin_provenance = Phase4_001B_derived_conservative_anti_fake_pass_policy
why_not_post_hoc = frozen_before_first_run_and_anchored_by_stage0_readiness_record
human_owner_approval = approved_by_human_owner_2026_06_10
```

Acceptance is conjunctive across all mandatory controls.

```text
candidate_pass_requires_not_matched_by_every_required_control = true
```

If any margin is changed after any run starts:

```text
verdict = gate1_preflight_failed_post_hoc_margin_change
```

## 8. Environment preregistration

Before execution, fill:

```text
environment_id =
environment_description =
environment_hash_or_generation_record =
environment_freeze_time =
environment_selection_rationale =
lookup_triviality_assessment =
control_disabled_by_construction_assessment =
heldout_structure_description =
state_space_summary =
observation_space_summary =
action_space_summary =
episode_or_sequence_length_rules =
```

Blocked environment verdicts:

```text
gate1_preflight_blocked_environment_lookup_triviality
gate1_preflight_blocked_environment_controls_disabled_by_construction
```

If the environment is lookup-trivial, candidate pass is impossible.

If the environment disables controls by construction, candidate pass is impossible.

## 9. Mandatory control stack A — graph/cache controls

```text
control_stack_id = graph_cache_control_stack
role = first_class_mandatory_control
```

Required controls:

1. runtime graph lookup
2. transition-table lookup
3. successor-map cache
4. predecessor-map cache
5. finite-state transition planner
6. count-table predictor
7. compressed predictive-map memory
8. direct episodic graph traversal

Collapse rule:

```text
if graph_cache_control_matches_candidate_under_predeclared_comparison_rule:
    candidate_verdict = not_distinguishable_in_this_setting
```

Omitting this control stack invalidates the execution.

## 10. Mandatory control stack B — generic replay-buffer controls

```text
control_stack_id = generic_replay_buffer_control_stack
role = first_class_mandatory_control
```

Generic replay form:

```text
B = replay_buffer
q(i | context) = replay_selector
r_i = selected_replay_item
theta_after = theta_before + update(theta_before, r_i)
```

Required controls:

1. frozen Gate 0 no-replay learner
2. same-data online-only learner
3. uniform factual replay
4. salience-weighted factual replay
5. generic chunk replay
6. random replay
7. shuffled replay
8. equal-compute extra training
9. frozen-theta control
10. post-hoc trace generator control

Collapse rule:

```text
if generic_replay_control_matches_candidate_under_predeclared_comparison_rule:
    candidate_verdict = replay_buffer_collapse
```

Omitting this control stack invalidates the execution.

## 11. Control parity and anti-sandbagging

Required parity fields:

```text
candidate_implementation_standard =
control_implementation_standard =
candidate_tuning_budget =
control_tuning_budget =
compute_matching_basis =
control_competence_tasks =
control_competence_results =
```

Control parity requirements:

```text
controls_built_to_same_engineering_standard_as_candidates = true
control_tuning_budget_class >= candidate_tuning_budget_class
compute_matching_basis_predeclared = true
compute_matching_basis_same_for_equal_compute_controls = true
control_competence_floor_required = true
```

Compute-matching basis must be one of:

```text
update_steps
FLOPs
wall_clock
```

The selected basis must be chosen before margin freeze.

Control competence floor:

* graph/cache controls must pass a pure-lookup sanity task
* generic replay controls must show measurable learning on a replay-friendly sanity task

If a control fails competence:

```text
comparison_verdict = control_incompetent_invalid_comparison
```

This must never be converted into candidate success.

## 12. Required ablations

### 12.1 Salience selection

Salience is a modifier only.

Required ablations:

* no-salience replay
* prediction-error salience
* uncertainty salience, only if epistemic vs aleatoric distinction is logged
* salience-weighted generic replay baseline

Blocked unless Gate-0-reduced with lineage:

* reward salience
* value salience
* goal salience

Fully blocked:

* preference salience
* affect salience
* user-model salience
* semantic-memory salience
* relationship salience
* viability salience

### 12.2 Order-sensitive update geometry

Order is a modifier only.

Required ablations:

* matched item multiset
* matched compute
* matched optimizer state
* matched seeds
* shuffled order
* random order
* candidate order
* reverse / forward order only if preregistered

Hand-picked replay order after observing outcomes is invalid.

## 13. Runtime-access attestation

Evaluation-time access must be enforced by construction, not by promise.

Required attestation fields:

```text
run_id =
candidate_or_control_id =
evaluation_process_id =
reachable_object_inventory =
reachable_object_hashes =
forbidden_object_absence_proof =
loaded_model_hashes =
loaded_cache_hashes =
loaded_index_hashes =
loaded_store_hashes =
environment_isolation_record =
attestation_time =
attestation_signer =
```

Valid attestation requires:

```text
reachable_objects_listed_and_hashed = true
forbidden_objects_not_loaded = true
forbidden_objects_not_reachable = true
```

Invalid attestation:

```text
attestation_only_says_we_did_not_use_X = invalid
```

### 13.1 Candidate A forbidden runtime access

At evaluation, Candidate A must not access:

* fast episodic store
* original replay buffer, unless explicitly part of a control run
* teacher model
* generator model
* synthetic item library
* generated trajectory library
* teacher-output cache
* summary memory
* nearest-neighbor index
* graph cache
* transition-table cache
* successor-map cache
* predecessor-map cache
* direct episodic traversal

### 13.2 Candidate B forbidden runtime access

At evaluation, Candidate B must not access:

* stored hidden states
* hidden-state cache
* prefix cache
* chunk checkpoint library
* longer-context retrieval index
* sequence lookup table
* original chunks on the evaluation forward path
* nearest-neighbor sequence retrieval
* graph/cache lookup
* transition-table lookup

Raw chunks may be used only in offline verification replay.

Offline verification replay outputs must not be evaluation outputs.

## 14. Source deletion timing

Deletion timing must be preregistered and verified through runtime-access attestation inventory.

### 14.1 Candidate A deletion timing

Evidential arm:

```text
source_deletion_timing = after_transfer_before_evaluation
evaluation_mode = slow_only
```

Objects to remove before evaluation:

* fast episodic store
* teacher model
* generator model
* synthetic item library
* generated trajectory library
* summary memory
* teacher-output cache
* generator-as-memory path
* nearest-neighbor retrieval index

Comparison arms may include:

* deletion before transfer
* deletion after evaluation
* source weakening
* teacher removal only
* generator removal only
* synthetic library removal only
* summary memory removal only
* fast-store removal only

Only after-transfer-before-evaluation slow-only evaluation is evidential for Candidate A.

Collapse rule:

```text
if deleting_fast_or_source_objects_after_transfer_before_evaluation_destroys_effect:
    candidate_A_verdict = source_dependent_collapse
```

### 14.2 Candidate B deletion timing

Must distinguish removal of:

* hidden-state cache
* prefix cache
* chunk checkpoint library
* sequence lookup table
* longer-context retrieval index
* nearest-neighbor sequence index

Candidate B evidential condition:

```text
evaluation_forward_path_cache_free = true
hidden_state_cache_removed_before_evaluation = true
prefix_cache_removed_before_evaluation = true
longer_context_retrieval_removed_before_evaluation = true
```

Collapse rule:

```text
if hidden_state_cache_or_longer_context_retrieval_matches_or_erases_effect:
    candidate_B_verdict = cache_or_retrieval_collapse
```

## 15. Lineage ledger

Minimum required fields:

```text
run_id
candidate_id
control_id
replay_event_id
source_trace_ids
replay_item_type
source_snapshot_hash
source_availability_time
model_snapshot_freeze_time
rng_seed_if_applicable
transformation_rule_if_applicable
chunk_boundaries_if_applicable
burn_in_length_if_applicable
hidden_state_recomputation_record_if_applicable
fast_store_snapshot_hash_if_applicable
slow_state_snapshot_hash_before
slow_state_snapshot_hash_after
deletion_timing_record
runtime_access_attestation
evaluation_time_allowed_access_manifest
baseline_output_records
post_hoc_provenance_generator_control_records
margin_hash
smoke_test_records
control_competence_records
environment_preregistration_record
```

Run ledger completeness:

```text
all_initiated_runs_logged = true
aborted_runs_logged = true
failed_runs_logged = true
seed_policy_predeclared = true
seed_count_predeclared = true
seed_selection_rule_predeclared = true
aggregation_rule_predeclared = true
```

Dropping runs or seeds after outcome inspection is a stop condition.

Lineage reconstruction rule:

```text
if lineage_cannot_be_reconstructed_from_frozen_records:
    verdict = trace_nonidentifiable
```

## 16. Gate 0 interface boundary

Allowed variables:

* raw trace items
* action
* observation
* belief state
* theta parameters
* prediction error
* uncertainty
* all-action predictions
* transition / observation pseudo-counts
* chronology / commitment records

Counterfactual action contrast:

```text
counterfactual_action_contrast = read_only_historical_citation_only
```

It must never be used as:

* input feature
* training target
* replay item
* salience signal
* data-generation source
* synthetic item rule
* ablation target

Blocked unless explicitly reduced to Gate 0 lineage:

* reward
* value
* goal
* preference
* affect
* viability
* social latent
* user model
* LLM semantic memory
* external world model not derived from Gate 0 traces
* hidden teacher
* hidden future oracle

If any candidate or control requires blocked variables without derivation lineage:

```text
verdict = gate0_interface_violation
```

## 17. Anti-hardcoding scan

Required checks:

```text
no_hand_coded_deletion_timing = true
no_curated_replay_items_after_outcome_inspection = true
no_manually_tuned_salience_formula_after_outcome_inspection = true
no_hand_picked_seeds = true
no_run_or_seed_dropping_after_outcome_inspection = true
no_hard_coded_graph_topology_in_candidate_path = true
no_hand_curated_chunk_boundaries = true
no_manually_tuned_burn_in_length = true
no_hidden_if_else_behavior = true
no_test_only_logic_paths = true
no_threshold_tuning_after_results = true
no_post_hoc_margin_changes = true
no_environment_design_that_trivially_favors_candidate = true
no_environment_design_that_disables_controls_by_construction = true
no_control_sandbagging = true
no_pre_freeze_comparative_pilot_runs = true
no_post_hoc_lineage_repair = true
```

If success depends on any violation:

```text
verdict = gate1_preflight_failed_hardcoding
```

## 18. Evidence outputs required

A future executable run must produce:

```text
1. task manifest
2. frozen comparison margins
3. margin freeze commit hash
4. external time anchor record
5. ordering proof: margin freeze before first run
6. candidate run manifests
7. control run manifests
8. runtime-access manifests with reachable-object inventory hashes
9. lineage ledgers including aborted and failed runs
10. source deletion logs
11. model snapshot hashes
12. slow-state before/after snapshots
13. latent recomputation records
14. baseline output records
15. control competence check records
16. environment preregistration records
17. anti-hardcoding audit report
18. stop-condition report
19. final bounded verdict report
```

Missing required output is a task failure unless execution stopped before running due to a valid stop condition.

## 19. Acceptance gates

### 19.1 Universal acceptance requirements

All must be true:

```text
human_signoff_present = true
all_comparison_margins_predeclared = true
margin_freeze_ordering_verified = true
external_time_anchor_present = true
runtime_access_attestation_pass = true
lineage_reconstruction_pass = true
run_ledger_complete_including_aborted_runs = true
source_deletion_timing_preregistered = true
anti_hardcoding_scan_pass = true
gate0_interface_audit_pass = true
mandatory_graph_cache_controls_present = true
mandatory_generic_replay_controls_present = true
control_competence_checks_pass = true
environment_preregistration_pass = true
counterfactual_action_replay_absent = true
```

If any universal requirement fails, no candidate may pass.

### 19.2 Candidate A acceptance requirements

All must be true:

```text
candidate_A_slow_only_evaluation_pass = true
fast_store_removed_before_evaluation = true
teacher_removed_before_evaluation = true
generator_removed_before_evaluation = true
synthetic_library_removed_before_evaluation = true
summary_memory_removed_before_evaluation = true
teacher_output_cache_removed_before_evaluation = true
generator_as_memory_path_removed_before_evaluation = true
slow_state_snapshot_delta_logged = true
graph_cache_controls_do_not_match_under_predeclared_rule = true
generic_replay_controls_do_not_match_under_predeclared_rule = true
teacher_cache_control_does_not_match_under_predeclared_rule = true
generator_as_memory_control_does_not_match_under_predeclared_rule = true
summary_memory_control_does_not_match_under_predeclared_rule = true
equal_compute_control_does_not_match_under_predeclared_rule = true
```

Candidate A failure modes:

```text
candidate_A_source_dependent_collapse
candidate_A_graph_cache_collapse
candidate_A_generic_replay_collapse
candidate_A_teacher_cache_collapse
candidate_A_generator_memory_collapse
candidate_A_summary_memory_collapse
candidate_A_equal_compute_collapse
```

### 19.3 Candidate B acceptance requirements

All must be true:

```text
candidate_B_cache_free_evaluation_pass = true
latent_traces_recomputable_from_raw_chunks = true
evaluation_forward_path_reads_no_raw_chunks = true
encoder_dynamics_snapshots_frozen = true
chunk_boundaries_preregistered = true
burn_in_length_preregistered = true
hidden_state_cache_forbidden = true
prefix_cache_forbidden = true
longer_context_retrieval_forbidden = true
chunk_checkpoint_library_forbidden = true
hidden_state_cache_control_does_not_match_under_predeclared_rule = true
longer_context_retrieval_control_does_not_match_under_predeclared_rule = true
sequence_lookup_control_does_not_match_under_predeclared_rule = true
generic_chunk_replay_control_does_not_match_under_predeclared_rule = true
same_data_online_only_control_does_not_match_under_predeclared_rule = true
equal_compute_control_does_not_match_under_predeclared_rule = true
```

Candidate B failure modes:

```text
candidate_B_hidden_state_cache_collapse
candidate_B_prefix_cache_collapse
candidate_B_longer_context_retrieval_collapse
candidate_B_sequence_lookup_collapse
candidate_B_generic_chunk_replay_collapse
candidate_B_same_data_online_only_collapse
candidate_B_equal_compute_collapse
candidate_B_recomputation_nonidentifiable
```

### 19.4 Package acceptance rule

A package-level preflight pass requires Candidate A to pass.

Candidate B is secondary only.

Candidate B may strengthen the package only if Candidate A passes.

Candidate B alone must never be used to imply package-level Gate 1 pass.

Allowed package verdicts:

```text
gate1_preflight_bounded_pass_primary_fast_to_slow
gate1_preflight_bounded_pass_primary_fast_to_slow_secondary_latent
gate1_preflight_latent_secondary_only_no_package_pass
gate1_preflight_failed_generic_replay_collapse
gate1_preflight_failed_graph_cache_collapse
gate1_preflight_failed_runtime_access_violation
gate1_preflight_failed_lineage_nonidentifiability
gate1_preflight_failed_gate0_interface_violation
gate1_preflight_failed_hardcoding
gate1_preflight_failed_margin_freeze_ordering
gate1_preflight_failed_control_incompetence
gate1_preflight_failed_run_ledger_incomplete
gate1_preflight_blocked_environment_lookup_triviality
gate1_preflight_blocked_environment_controls_disabled_by_construction
gate1_preflight_blocked_no_clean_candidate
```

## 20. Stop conditions

The task must stop or fail if any of the following occur:

```text
counterfactual_action_replay_reintroduced = true
mandatory_graph_cache_controls_missing = true
mandatory_generic_replay_controls_missing = true
comparison_margins_not_predeclared = true
external_time_anchor_missing = true
pre_freeze_comparative_run_detected = true
runtime_access_attestation_missing = true
evaluation_environment_contains_forbidden_object = true
source_deletion_timing_not_preregistered = true
lineage_records_incomplete = true
run_or_seed_dropped_after_outcome_inspection = true
gate0_interface_violation = true
candidate_depends_on_runtime_retrieval = true
candidate_depends_on_source_access_at_evaluation = true
graph_cache_control_matches_effect_under_predeclared_rule = true
generic_replay_control_matches_effect_under_predeclared_rule = true
hidden_state_cache_matches_latent_effect = true
longer_context_retrieval_matches_latent_effect = true
control_competence_check_failed = true
teacher_or_generator_remains_on_runtime_path = true
source_deletion_after_transfer_removes_fast_to_slow_effect = true
synthetic_or_counterfactual_item_leaks_future_outcome = true
environment_solved_by_lookup = true
environment_disables_controls_by_construction = true
success_depends_on_hardcoded_schedule_or_seed = true
post_hoc_margin_change_detected = true
post_hoc_lineage_repair_detected = true
draft_self_promoted_to_executable_without_human_signoff = true
```

## 21. Rollback plan

Allowed rollback outcomes:

```text
rollback_to_phase4_scope_edit
rollback_to_phase3_delta_retry
rollback_to_phase2r_retry
block_gate1_no_clean_candidate
```

Rollback rules:

* If controls are missing, return to task-card design; do not execute.
* If counterfactual replay is reintroduced anywhere, roll back to Phase 4 scope enforcement.
* If graph/cache controls match the candidate, mark candidate as not distinguishable in this setting.
* If generic replay controls match the candidate, mark candidate as replay-buffer collapse.
* If source removal destroys Candidate A, mark Candidate A as source-dependent collapse.
* If hidden-state cache or longer-context retrieval matches Candidate B, mark Candidate B as cache/retrieval collapse.
* If lineage cannot be reconstructed, mark trace non-identifiability.
* If Gate 0 variables are violated, mark Gate 0 interface failure.
* If control competence fails, mark comparison invalid; do not infer candidate success.
* If the environment is lookup-trivial or disables controls by construction, block the setting.
* If both Candidate A and Candidate B fail, block Gate 1.

## 22. Final report shape

A future executable task must end with:

```text
A. Executive verdict
B. Scope confirmation
C. Candidate A result
D. Candidate B result
E. Mandatory graph/cache control results
F. Mandatory generic replay control results
G. Control competence check results
H. Runtime-access attestation with inventory hashes
I. Source deletion timing report
J. Lineage reconstruction report with complete run ledger
K. Gate 0 interface audit
L. Anti-hardcoding audit
M. Margin-freeze and external-time-anchor report
N. Environment preregistration report
O. Stop-condition report
P. Claim ceiling statement
Q. What this does not prove
R. Rollback or next-action recommendation
```

## 23. Completeness checklist mapping inherited freeze constraints

| Inherited freeze constraint                                 | Enforcing section |
| ----------------------------------------------------------- | ----------------- |
| fast-to-slow structure transfer = primary candidate         | 4, 5, 14, 19      |
| latent-dynamics consistency replay = secondary candidate    | 4, 5, 14, 19      |
| counterfactual action replay = excluded in every role       | 4, 16, 20         |
| graph/cache control stack = first-class mandatory           | 9, 11, 19, 20     |
| generic replay-buffer control stack = first-class mandatory | 10, 11, 19, 20    |
| comparison margins = predeclared before any future run      | 7, 19, 20         |
| runtime-access attestation = mandatory                      | 13, 18, 19, 20    |
| source deletion timing = mandatory                          | 14, 18, 19, 20    |
| lineage records = mandatory                                 | 15, 18, 19, 20    |
| anti-hardcoding scan = mandatory                            | 17, 18, 19, 20    |
| control parity = mandatory                                  | 11, 19, 20        |
| environment preregistration = mandatory                     | 8, 19, 20         |
| complete run ledger = mandatory                             | 15, 18, 19, 20    |

## 24. What this task does not prove

This task does not prove Candidate A works.

This task does not prove Candidate B works.

This task does not prove Gate 1 will pass.

This task does not prove replay / consolidation is necessary.

This task does not prove predictive superiority over retrieval.

This task does not prove that the control list is exhaustive.

This task does not prove open-world robustness.

This task does not prove consciousness, subjective experience, real emotion, self-awareness, agency, functional-subject evidence, electronic life, companion readiness, EGO readiness, or AGI.

This task does not authorize EGO mainline integration.

It only authorizes a bounded preflight execution after margin freeze and external time anchor.

## 25. Execution readiness decision

Execution is forbidden until:

```text
human_signoff_status = approved_by_human_owner
margin_freeze_completed = true
external_time_anchor_completed = true
first_run_allowed = true
```

Current status at creation:

```text
human_signoff_status = approved_by_human_owner
margin_policy_frozen_in_card = true
stage0_pre_run_finalization_allowed = true
margin_freeze_completed = false_until_stage0_record_exists
external_time_anchor_completed = false_until_stage0_anchor_exists
first_run_allowed = false_until_stage0_readiness_passes
```

Final pre-run check:

```text
if stage0_pre_run_finalization_has_not_recorded_task_card_hash:
    stop_before_candidate_or_control_runs

if stage0_pre_run_finalization_has_not_recorded_margin_hash:
    stop_before_candidate_or_control_runs

if margin_freeze_completed != true:
    stop_before_candidate_or_control_runs

if external_time_anchor_completed != true:
    stop_before_candidate_or_control_runs

if first_run_allowed != true:
    stop_before_candidate_or_control_runs
```

Stage 0 is allowed to create only the minimum readiness / margin-freeze / external-anchor record needed to turn these fields true. Stage 0 must not run candidates, controls, training, evaluation, pilot comparisons, calibration, benchmarks, or data generation.


## Margin-freeze block

```text
margin_freeze_status = margin_policy_frozen_in_card_pending_stage0_external_anchor_record
margin_policy = conservative_zero_advantage_rule
post_hoc_margin_setting = forbidden
pre_freeze_candidate_or_control_runs = forbidden
acceptance_logic = conjunctive_across_all_mandatory_controls
```

### 1. Metric orientation

All candidate-vs-control comparisons must be converted into a candidate advantage score.

For higher-is-better metrics:

```text
candidate_advantage = candidate_score - control_score
```

For lower-is-better metrics, such as NLL, prediction loss, reconstruction loss, latent consistency loss, or calibration error:

```text
candidate_advantage = control_score - candidate_score
```

Interpretation:

```text
candidate_advantage > 0  means candidate is better than control
candidate_advantage = 0  means candidate is tied with control
candidate_advantage < 0  means control is better than candidate
```

### 2. Universal control-match rule

A control is considered to match the candidate if the candidate does not show a strictly positive advantage under the predeclared paired aggregation rule.

```text
control_matches_candidate_if:
    paired_candidate_advantage_lower_bound <= 0
```

Candidate is distinguishable from a control only if:

```text
candidate_distinguishable_from_control_if:
    paired_candidate_advantage_lower_bound > 0
```

No positive slack margin is granted to the candidate.

```text
candidate_advantage_equivalence_margin = 0.0
```

This is intentionally conservative. If the result is tied, noisy, overlapping, or ambiguous, the control counts as matching the candidate.

### 3. Paired aggregation rule

All candidate-vs-control comparisons must be paired by the same environment instance, same seed group, same evaluation slice, and same compute-matching basis.

```text
paired_unit = environment_instance + seed + evaluation_slice
aggregation_rule = paired bootstrap or exact paired aggregate if deterministic
confidence_rule = lower_bound_of_candidate_advantage_must_be_above_zero
```

If bootstrap or uncertainty estimation is not implemented, the fallback rule is stricter:

```text
fallback_rule:
    candidate_advantage_must_be_positive_on_every_required_seed_and_every_required_evaluation_slice
```

If neither paired uncertainty nor strict all-slice dominance can be computed, the comparison is non-identifiable.

```text
verdict = comparison_nonidentifiable
```

### 4. Required evaluation slices

Candidate A must be evaluated at minimum on:

```text
A_slice_1 = slow_only_after_source_deletion
A_slice_2 = slow_only_heldout_or_unreplayed_structure
A_slice_3 = slow_only_post_deletion_stability
```

Candidate B must be evaluated at minimum on:

```text
B_slice_1 = cache_free_evaluation
B_slice_2 = hidden_state_cache_removed
B_slice_3 = longer_context_retrieval_removed
B_slice_4 = heldout_sequence_or_alias_disambiguation
```

A candidate may pass only if it is distinguishable from every mandatory control on every required slice.

```text
slice_acceptance = conjunctive
```

If a control matches the candidate on any required slice:

```text
candidate_verdict = control_matched_candidate_on_required_slice
```

### 5. Structural / audit margins

The following are zero-tolerance requirements.

```text
runtime_forbidden_object_count_margin = 0
missing_required_lineage_field_margin = 0
unreconstructable_lineage_record_margin = 0
post_hoc_margin_change_margin = 0
dropped_run_or_seed_margin = 0
unlogged_initiated_run_margin = 0
gate0_interface_violation_margin = 0
counterfactual_action_replay_occurrence_margin = 0
control_stack_omission_margin = 0
forbidden_runtime_access_margin = 0
source_deletion_timing_deviation_margin = 0
post_hoc_lineage_repair_margin = 0
hardcoded_schedule_or_seed_margin = 0
```

Any violation triggers failure or rollback.

### 6. Runtime-access attestation margin

```text
runtime_access_attestation_margin = exact
```

Valid only if:

```text
reachable_object_inventory_present = true
forbidden_objects_loaded = 0
forbidden_objects_reachable = 0
inventory_hashes_present = true
```

Invalid if:

```text
attestation_only_says_we_did_not_use_X = true
```

### 7. Lineage reconstruction margin

```text
lineage_reconstruction_margin = exact
```

Valid only if every required record can be reconstructed from frozen records:

```text
lineage_reconstruction_pass_rate_required = 1.0
```

If any required lineage record is missing:

```text
verdict = trace_nonidentifiable
```

### 8. Run ledger margin

```text
run_ledger_completeness_required = 1.0
```

Every initiated run must appear in the ledger.

```text
initiated_runs_logged_rate_required = 1.0
aborted_runs_logged_rate_required = 1.0
failed_runs_logged_rate_required = 1.0
```

If any initiated run, failed run, aborted run, or seed is missing:

```text
verdict = gate1_preflight_failed_run_ledger_incomplete
```

### 9. Control competence margins

Control competence is not a candidate-vs-control success metric. It is a validity prerequisite.

Graph/cache controls must pass a pure lookup sanity task.

```text
graph_cache_control_competence_rule:
    control must solve the preregistered pure-lookup sanity task according to its own task-specific exact-success criterion
```

Generic replay controls must pass a replay-friendly sanity task.

```text
generic_replay_control_competence_rule:
    control must show nonzero learning or loss reduction on the preregistered replay-friendly sanity task under the same metric orientation used for the candidate comparison
```

If a control fails competence:

```text
verdict = control_incompetent_invalid_comparison
```

This is never candidate success.

### 10. Environment margins

The environment is invalid if it is lookup-trivial.

```text
environment_lookup_triviality_rule:
    if graph/cache, transition-table, count-table, or direct episodic lookup can solve all required evaluation slices by construction, verdict = gate1_preflight_blocked_environment_lookup_triviality
```

The environment is also invalid if it disables controls by construction.

```text
environment_controls_disabled_by_construction_rule:
    if the environment prevents a properly implemented mandatory control from exercising its intended access pattern or competence, verdict = gate1_preflight_blocked_environment_controls_disabled_by_construction
```

Neither condition may be interpreted as candidate success.

### 11. Candidate A comparison margins

For all Candidate A comparisons:

```text
A_comparison_margin = 0.0
A_candidate_distinguishable_if = paired_candidate_advantage_lower_bound > 0
A_control_matches_if = paired_candidate_advantage_lower_bound <= 0
```

Apply the same rule to:

```text
A_vs_graph_cache_match_margin = 0.0
A_vs_transition_table_match_margin = 0.0
A_vs_successor_map_cache_match_margin = 0.0
A_vs_predecessor_map_cache_match_margin = 0.0
A_vs_count_table_predictor_match_margin = 0.0
A_vs_direct_episodic_graph_traversal_match_margin = 0.0
A_vs_generic_replay_match_margin = 0.0
A_vs_same_data_online_only_match_margin = 0.0
A_vs_equal_compute_extra_training_match_margin = 0.0
A_vs_summary_memory_match_margin = 0.0
A_vs_teacher_output_cache_match_margin = 0.0
A_vs_generator_as_memory_match_margin = 0.0
A_vs_synthetic_library_lookup_match_margin = 0.0
A_vs_direct_episodic_retrieval_match_margin = 0.0
```

If any listed control matches Candidate A under this rule:

```text
candidate_A_verdict = collapsed_or_not_distinguishable_in_this_setting
```

### 12. Candidate B comparison margins

For all Candidate B comparisons:

```text
B_comparison_margin = 0.0
B_candidate_distinguishable_if = paired_candidate_advantage_lower_bound > 0
B_control_matches_if = paired_candidate_advantage_lower_bound <= 0
```

Apply the same rule to:

```text
B_vs_hidden_state_cache_match_margin = 0.0
B_vs_prefix_cache_match_margin = 0.0
B_vs_longer_context_retrieval_match_margin = 0.0
B_vs_sequence_lookup_match_margin = 0.0
B_vs_nearest_neighbor_sequence_retrieval_match_margin = 0.0
B_vs_generic_chunk_replay_match_margin = 0.0
B_vs_same_data_online_only_match_margin = 0.0
B_vs_equal_compute_extra_training_match_margin = 0.0
B_vs_random_replay_match_margin = 0.0
B_vs_shuffled_replay_match_margin = 0.0
```

If any listed control matches Candidate B under this rule:

```text
candidate_B_verdict = collapsed_or_not_distinguishable_in_this_setting
```

### 13. Model-state evidence margins

Model-state evidence is required but not sufficient.

Candidate A must show:

```text
slow_state_snapshot_before_present = true
slow_state_snapshot_after_present = true
slow_state_snapshot_delta_logged = true
source_removed_before_evaluation = true
```

Candidate B must show:

```text
encoder_dynamics_snapshot_present = true
latent_recomputation_record_present = true
latent_traces_recomputable_from_raw_chunks = true
evaluation_forward_path_reads_no_raw_chunks = true
```

But state change alone is not candidate success.

```text
state_change_alone_implies_success = false
```

### 14. Package-level margin rule

Package-level preflight pass requires Candidate A to pass all Candidate A requirements.

Candidate B is secondary only.

```text
package_pass_requires_candidate_A_pass = true
candidate_B_alone_package_pass = forbidden
```

Candidate B may only strengthen the package if Candidate A already passes.

### 15. Margin provenance statement

The margin policy is intentionally conservative because Gate 0 did not establish predictive superiority over retrieval. The frozen policy therefore treats ties, overlaps, noisy differences, and ambiguous comparisons as baseline matches rather than candidate wins.

```text
margin_provenance = Phase 4 / 001B-derived conservative anti-fake-pass policy
why_not_post_hoc = margins are fixed before execution and before any candidate-vs-control run
```

