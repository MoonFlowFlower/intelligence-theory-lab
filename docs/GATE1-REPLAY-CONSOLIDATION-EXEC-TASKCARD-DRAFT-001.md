# GATE1-REPLAY-CONSOLIDATION-EXEC-TASKCARD-DRAFT-001

```text
task_id = GATE1-REPLAY-CONSOLIDATION-EXEC-TASKCARD-DRAFT-001
status = draft_pending_human_review
card_type = future executable Gate 1 preflight task-card draft
research_layer = mechanism hypothesis layer / bounded evidence preflight
execution_status = not executable until human sign-off + margin freeze
source_meta_card = GATE1-REPLAY-CONSOLIDATION-TASKCARD-001B
freeze_label = GATE1-REPLAY-CONSOLIDATION-PREFLIGHT-FREEZE-001
```

## 0. Human sign-off block

This draft is not executable until this block is completed by the human owner.

```text
human_owner_name =
human_owner_date =
human_owner_signature =
authorized_to_execute = false
margin_freeze_completed = false
external_time_anchor_record =
execution_task_id_if_promoted =
```

If `authorized_to_execute = false`, no execution is allowed.

If this draft is copied, modified, or promoted without explicit human sign-off, the task is invalid.

---

## 1. Scope confirmation

This card defines a bounded future Gate 1 preflight task.

It is designed to test whether either of the following can produce durable, traceable, replayable model-state change distinguishable from mandatory retrieval/cache and generic replay controls:

1. **Candidate A — primary:** tightened fast-to-slow structure transfer
2. **Candidate B — secondary:** tightened latent-dynamics consistency replay

This card also freezes two first-class mandatory control stacks:

3. **Mandatory control stack A:** predictive-structure graph/cache controls
4. **Mandatory control stack B:** generic factual replay / generic replay-buffer controls

This card explicitly excludes:

```text
gate0_bounded_counterfactual_action_replay = excluded_in_every_role
```

Counterfactual action replay must not appear as:

* forward candidate
* auxiliary mechanism
* optional extension
* data augmenter
* synthetic label generator
* replay item type
* salience source
* ablation target
* hidden baseline improvement
* “small helper” mechanism

If counterfactual action replay appears anywhere in the executable task, the task must stop before execution.

---

## 2. Authorization boundary

This draft does not itself authorize execution.

After human sign-off and margin freeze, a later executable version may authorize only the bounded Gate 1 preflight described here.

Even after sign-off, this task does not authorize:

* EGO mainline integration
* agent architecture changes
* companion behavior
* LLM / RAG / emotion / relationship / affect / viability / user-model modules
* consciousness, subjective experience, real emotion, self-awareness, agency, functional-subject, companion-readiness, EGO-readiness, electronic-life, or AGI claims
* winner selection between Candidate A and Candidate B
* claim of predictive superiority over retrieval
* open-world robustness claim
* total theory proof
* modifying Gate 0 evidence or Gate 0 claim ceiling
* modifying Phase 1 / Phase 2 / Phase 3 / Phase 2R / Phase 3 Delta / Phase 4 records
* relaxing mandatory control stacks
* post-hoc margin setting
* post-hoc lineage repair

Allowed future activity, only after human sign-off:

```text
bounded_gate1_preflight_execution = allowed_only_after_human_signoff_and_margin_freeze
```

Forbidden before sign-off:

```text
training = forbidden
evaluation = forbidden
pilot_run = forbidden
calibration_run = forbidden
benchmark_run = forbidden
data_generation = forbidden
artifact_creation = forbidden
```

---

## 3. Phase inheritance

```text
Gate 0:
  PREDICTIVE-ACTION-LEARNING-CONTRACT-001C
  status = frozen
  claim_ceiling = bounded isolated Gate 0 predictive-action mechanism evidence only

Phase 1:
  candidate_pool_sufficient_for_phase2

Phase 2:
  mathematical_compression_succeeded_ready_for_phase3

Phase 3:
  requires_phase2_rollback

Phase 2R:
  phase2r_reclassification_succeeded_ready_for_phase3_delta

Phase 3 Delta:
  phase3_delta_survives_but_requires_narrower_phase4_scope

Phase 4:
  phase4_freeze_fast_to_slow_primary_latent_secondary
```

Inherited frozen scope:

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
```

Any future executable version that omits or weakens any of the ten inherited constraints is invalid.

---

## 4. Correct problem definition

The correct question:

> Can a bounded Gate 1 preflight test distinguish strict source-removed fast-to-slow transfer, or strict cache-free latent-dynamics replay, from retrieval / cache / generic replay explanations under predeclared margins and mandatory controls?

The wrong questions:

* How can we make Gate 1 pass?
* Which mechanism is best?
* How do we implement EGO memory?
* How do we prove replay / consolidation?
* How do we show agency, consciousness, or functional-subject evidence?
* How do we integrate this into EGO?
* How do we create a useful companion memory system?

Any task output organized around those wrong questions is invalid.

---

## 5. Candidate hierarchy

### 5.1 Candidate A — primary

```text
candidate_id = A
name = tightened_fast_to_slow_structure_transfer
role = primary_candidate
```

Definition:

Replay / transfer may use a fast episodic source, teacher, generator, synthetic library, or source snapshot only during the transfer event. The claimed effect must later be expressed by slow model state or slow parameters under slow-only evaluation after all fast/source objects are removed.

Allowed only during transfer, with lineage:

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
```

Candidate A minimum meaning:

```text
effect_carrier = slow_model_state_or_slow_parameters
not_effect_carrier = fast_store_or_teacher_or_generator_or_summary_cache
```

### 5.2 Candidate B — secondary

```text
candidate_id = B
name = tightened_latent_dynamics_consistency_replay
role = secondary_candidate
```

Definition:

Replay uses preregistered raw sequence chunks to update parameters governing recomputed multi-step latent or recurrent dynamics. Latent/recurrent traces must be exactly recomputable from raw chunks plus frozen model snapshots.

Allowed only as recomputable derived variables:

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
```

Candidate B evaluation-path rule:

* The evaluation-time forward path must be computable without reading raw chunks, stored hidden states, caches, prefix libraries, or retrieval indices.
* Raw chunk access is permitted only inside a separate offline verification replay whose sole purpose is checking recomputability and lineage.
* Offline verification replay outputs must never be used as evaluation outputs.
* Any recomputation protocol that gives the evaluation forward path access to raw chunks, caches, or sequence retrieval collapses Candidate B to retrieval and fails.

### 5.3 Excluded candidate

```text
candidate_id = X
name = gate0_bounded_counterfactual_action_replay
role = excluded_in_every_role
```

This exclusion has no exception clause.

---

## 6. Hypotheses

### H1 — primary hypothesis

A strict source-removed fast-to-slow transfer candidate may produce a durable slow-state change that remains observable under slow-only evaluation after all fast/source objects are removed.

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

### H2 — secondary hypothesis

A strict cache-free latent-dynamics consistency candidate may produce a durable latent/recurrent parameter-state change that remains observable with hidden-state caches, prefix caches, stored hidden states, and longer-context retrieval disabled.

H2 is admissible only if distinguishable from:

* hidden-state cache
* prefix-cache reuse
* longer-context retrieval
* sequence lookup
* generic chunk replay
* same-data online-only learner
* equal-compute extra training

### H0 — null hypothesis

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
* environment design favoring the candidate
* weak controls

---

## 7. Claim ceiling

This future executable task may support at most:

> bounded Gate 1 preflight evidence that strict source-removed fast-to-slow transfer, or strict cache-free latent-dynamics replay, produced durable, traceable, replayable model-state change distinguishable from the mandatory control stacks under predeclared margins in the preregistered setting.

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

---

## 8. Margin-freeze protocol

No numerical margin is set in this draft.

All comparison margins must be filled before execution by the human owner or by a separately authorized margin-freeze step.

Required fields before execution:

```text
margin_freeze_event =
margin_freeze_commit_hash =
external_time_anchor =
first_run_start_time =
margin_hash =
margin_provenance_record =
```

Ordering rule:

```text
margin_freeze_commit_time < first_run_start_time
```

External time anchor rule:

```text
external_time_anchor_required = true
```

A future executable task must not start until the margin-freeze commit is pushed to an external remote or externally timestamped in a way that later auditors can verify.

Pre-freeze comparative runs are forbidden:

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

Comparison margins must be declared per control group.

Acceptance is conjunctive across all mandatory controls:

```text
candidate_pass_requires_not_matched_by_every_required_control = true
```

Post-hoc margin setting is invalid.

---

## 9. Environment preregistration

Before execution, the future executable task must preregister evaluation environment(s).

Required environment fields:

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

The environment must not be lookup-trivial.

The environment must also not disable controls by construction.

Two blocked verdicts must be available:

```text
gate1_preflight_blocked_environment_lookup_triviality
gate1_preflight_blocked_environment_controls_disabled_by_construction
```

If either applies, the candidate cannot pass.

---

## 10. Mandatory control stack A — graph/cache controls

```text
control_stack_id = graph_cache_control_stack
role = first_class_mandatory_control
```

This stack is mandatory. Omitting it invalidates the task.

Required controls:

1. runtime graph lookup
2. transition-table lookup
3. successor-map cache
4. predecessor-map cache
5. finite-state transition planner
6. count-table predictor
7. compressed predictive-map memory
8. direct episodic graph traversal

Purpose:

Detect whether any claimed candidate effect can be matched by predictive-structure lookup, transition-table memory, graph traversal, or compressed map cache.

Required collapse rule:

```text
if graph_cache_control_matches_candidate_under_predeclared_comparison_rule:
    candidate_verdict = not_distinguishable_in_this_setting
```

A graph/cache control match is not a candidate pass.

It is a candidate failure or setting-level non-identifiability.

---

## 11. Mandatory control stack B — generic replay-buffer controls

```text
control_stack_id = generic_replay_buffer_control_stack
role = first_class_mandatory_control
```

This stack is mandatory. Omitting it invalidates the task.

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

Purpose:

Detect whether the candidate adds irreducible structure beyond buffer sampling plus update.

Required collapse rule:

```text
if generic_replay_control_matches_candidate_under_predeclared_comparison_rule:
    candidate_verdict = replay_buffer_collapse
```

A generic replay match is not a candidate pass.

It is replay-buffer collapse.

---

## 12. Control parity and anti-sandbagging

Weak controls manufacture fake distinguishability.

The future executable task must require control parity.

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

---

## 13. Required ablations

### 13.1 Salience selection

Salience selection is a modifier only.

It is not a standalone skeleton.

Required ablations:

* no-salience replay
* prediction-error salience
* uncertainty salience, only if epistemic vs aleatoric distinction is logged
* salience-weighted generic replay baseline

Blocked salience variants unless Gate-0-reduced with lineage:

* reward salience
* value salience
* goal salience

Fully blocked salience variants:

* preference salience
* affect salience
* user-model salience
* semantic-memory salience
* relationship salience
* viability salience

### 13.2 Order-sensitive update geometry

Order-sensitive update geometry is a modifier only.

It is not standalone consolidation evidence.

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

---

## 14. Runtime-access attestation

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

Invalid attestation:

```text
attestation_only_says_we_did_not_use_X = invalid
```

Valid attestation requires inventory:

```text
reachable_objects_listed_and_hashed = true
forbidden_objects_not_loaded = true
forbidden_objects_not_reachable = true
```

### 14.1 Candidate A forbidden runtime access

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

### 14.2 Candidate B forbidden runtime access

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

---

## 15. Source deletion timing

Deletion timing must be preregistered.

Post-hoc deletion scheduling is invalid.

Deletion must be verified through runtime-access attestation inventory.

### 15.1 Candidate A deletion timing

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

But only the after-transfer-before-evaluation slow-only arm is evidential for Candidate A.

Collapse rule:

```text
if deleting_fast_or_source_objects_after_transfer_before_evaluation_destroys_effect:
    candidate_A_verdict = source_dependent_collapse
```

### 15.2 Candidate B deletion timing

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

---

## 16. Lineage ledger

The future executable task must produce a complete lineage ledger.

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

---

## 17. Gate 0 interface boundary

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

---

## 18. Anti-hardcoding scan

The future executable task must include an anti-hardcoding audit.

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

---

## 19. Evidence outputs required

A future executable task must produce:

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

Missing required output is a task failure unless the task stopped before execution due to a valid stop condition.

---

## 20. Acceptance gates

### 20.1 Universal acceptance requirements

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

### 20.2 Candidate A acceptance requirements

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

### 20.3 Candidate B acceptance requirements

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

### 20.4 Package acceptance rule

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

---

## 21. Stop conditions

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

---

## 22. Rollback plan

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

---

## 23. Final report shape

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

---

## 24. Completeness checklist mapping inherited freeze constraints

| Inherited freeze constraint                                 | Enforcing section        |
| ----------------------------------------------------------- | ------------------------ |
| fast-to-slow structure transfer = primary candidate         | 5.1, 6, 15.1, 20.2, 20.4 |
| latent-dynamics consistency replay = secondary candidate    | 5.2, 6, 15.2, 20.3, 20.4 |
| counterfactual action replay = excluded in every role       | 5.3, 17, 21              |
| graph/cache control stack = first-class mandatory           | 10, 12, 20.1, 21         |
| generic replay-buffer control stack = first-class mandatory | 11, 12, 20.1, 21         |
| comparison margins = predeclared before any future run      | 8, 20.1, 21              |
| runtime-access attestation = mandatory                      | 14, 19, 20.1, 21         |
| source deletion timing = mandatory                          | 15, 19, 20.1, 21         |
| lineage records = mandatory                                 | 16, 19, 20.1, 21         |
| anti-hardcoding scan = mandatory                            | 18, 19, 20.1, 21         |

---

## 25. What this task does not prove

This task does not prove Candidate A works.

This task does not prove Candidate B works.

This task does not prove Gate 1 will pass.

This task does not prove replay / consolidation is necessary.

This task does not prove predictive superiority over retrieval.

This task does not prove that the control list is exhaustive.

This task does not prove open-world robustness.

This task does not prove consciousness, subjective experience, real emotion, self-awareness, agency, functional-subject evidence, electronic life, companion readiness, EGO readiness, or AGI.

This task does not authorize EGO mainline integration.

This task only defines a bounded preflight evidence procedure under the inherited Phase 4 scope.

---

## 26. Human review notes

Before execution, the human owner must fill or approve:

```text
1. human sign-off block
2. numerical comparison margins
3. margin provenance
4. external time anchor mechanism
5. environment selection
6. control competence sanity tasks
7. compute-matching basis
8. seed policy
9. aggregation rule
10. final executable task id
```

If any of these remain unfilled, this draft remains non-executable.

```text
final_status = draft_pending_human_review
```
