# GATE1-REPLAY-CONSOLIDATION-TASKCARD-001A

## Title

Bounded Gate 1 replay / consolidation preflight task card: source-removed fast-to-slow transfer primary, cache-free latent-dynamics secondary, mandatory retrieval/cache and generic replay controls.

## Authorization boundary

This task card authorizes **bounded Gate 1 task-card design only**.

It does **not** authorize:

* implementation
* EGO mainline integration
* agent architecture changes
* companion behavior
* LLM/RAG/emotion/relationship modules
* consciousness, agency, functional-subject, companion-readiness, EGO-readiness, or AGI claims
* winner selection between mechanisms
* changing Gate 0 evidence or claim ceiling
* relaxing any inherited Phase 4 freeze constraint

Codex must not implement code unless a later separate execution task explicitly authorizes implementation.

## Current phase

Current stage:

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

Freeze label:
GATE1-REPLAY-CONSOLIDATION-PREFLIGHT-FREEZE-001
```

This task card must inherit the Phase 4 frozen scope exactly.

## Problem definition

Design a bounded Gate 1 preflight evidence contract that can later test whether replay / consolidation produces **durable, traceable, replayable model-state change** distinguishable from mandatory retrieval/cache and generic replay controls.

The task is not to prove replay works.

The task is to define a falsifiable, auditable, bounded test harness specification for:

1. **Primary candidate:** tightened fast-to-slow structure transfer
2. **Secondary candidate:** tightened latent-dynamics consistency replay
3. **Mandatory first-class control stack:** predictive-structure graph/cache controls
4. **Mandatory first-class control stack:** generic replay-buffer controls

The following is excluded:

```text
Gate-0-bounded counterfactual action replay
status = excluded from this task card
reason = lineage / oracle leakage / source-snapshot dependence too severe
```

If counterfactual action replay is reintroduced in this task card, the task card is invalid.

## Correct framing

The correct question is:

> Can a future bounded Gate 1 test distinguish strict source-removed fast-to-slow transfer or strict cache-free latent-dynamics replay from retrieval/cache/generic replay explanations?

The wrong questions are:

* How can we make Gate 1 pass?
* Which mechanism is the winner?
* How do we implement EGO memory?
* How do we prove replay / consolidation?
* How do we get agency, consciousness, or functional-subject evidence?
* How do we integrate this into EGO mainline?

## Candidate hierarchy

### Candidate A — primary

```text
name = tightened_fast_to_slow_structure_transfer
role = primary_candidate
```

Definition:

Replay / transfer may use a fast episodic source, teacher, generator, synthetic library, or source snapshot only during the transfer event. The claimed effect must later be expressed by a slow model state or slow parameters under slow-only evaluation after all fast/source objects are removed.

Required interpretation:

```text
fast_source_used_during_transfer = allowed
fast_source_available_at_evaluation = forbidden

teacher_used_during_transfer = allowed only with lineage
teacher_available_at_evaluation = forbidden

generator_used_during_transfer = allowed only with lineage
generator_available_at_evaluation = forbidden

synthetic_library_used_during_transfer = allowed only with lineage
synthetic_library_available_at_evaluation = forbidden

summary_memory_available_at_evaluation = forbidden
```

### Candidate B — secondary

```text
name = tightened_latent_dynamics_consistency_replay
role = secondary_candidate
```

Definition:

Replay uses preregistered raw sequence chunks to update parameters governing recomputed multi-step latent or recurrent dynamics. Latent/recurrent traces must be exactly recomputable from raw chunks and frozen model snapshots. Evaluation must forbid stored hidden states, hidden-state caches, prefix caches, checkpointed chunks, and undeclared longer-context retrieval.

Required interpretation:

```text
latent_state = allowed only if recomputable from raw trace + frozen model snapshot
stored_hidden_state_at_evaluation = forbidden
hidden_state_cache_at_evaluation = forbidden
prefix_cache_at_evaluation = forbidden
longer_context_retrieval_at_evaluation = forbidden
chunk_checkpoint_library_at_evaluation = forbidden
```

### Excluded candidate

```text
name = gate0_bounded_counterfactual_action_replay
role = excluded
```

This task card must not include counterfactual action replay as a forward candidate, auxiliary mechanism, optional extension, hidden synthetic generator, or ablation target.

## Hypotheses

### Primary hypothesis H1

A strict source-removed fast-to-slow transfer candidate may produce a durable slow-state change that remains observable under slow-only evaluation after all fast/source objects are removed.

This hypothesis is admissible only if the effect is distinguishable from:

* summary-memory retrieval
* teacher-output cache
* generator-as-memory
* synthetic library lookup
* direct episodic retrieval
* graph/cache lookup
* generic replay-buffer training
* equal-compute extra training

### Secondary hypothesis H2

A strict cache-free latent-dynamics consistency candidate may produce a durable latent/recurrent parameter-state change that remains observable when hidden-state caches, prefix caches, stored hidden states, and longer-context retrieval are disabled.

This hypothesis is admissible only if the effect is distinguishable from:

* hidden-state cache
* prefix-cache reuse
* longer-context retrieval
* sequence lookup
* generic chunk replay
* same-data online-only learning
* equal-compute extra training

### Null hypothesis H0

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
* hand-coded schedule, chunking, deletion timing, or seed selection

## Claim ceiling

This task card can support at most a future bounded Gate 1 preflight test of whether strict source-removed fast-to-slow transfer or strict cache-free latent-dynamics replay can produce durable, traceable, replayable model-state change distinguishable from mandatory retrieval/cache and generic replay controls.

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

## Mandatory comparison margins

All comparison margins must be predeclared in the later executable Gate 1 task card before any run.

This task card must specify that future margins are required, but it must not invent numerical thresholds unless already fixed by prior evidence.

Required rule:

```text
comparison_margin_policy = predeclare_before_execution
post_hoc_margin_setting = forbidden
```

Any future Gate 1 execution that changes margins after observing results is invalid.

## Mandatory first-class control stack A: graph/cache controls

This control stack is first-class and mandatory.

A future Gate 1 task card omitting this stack is invalid by definition.

Required controls:

* runtime graph lookup
* transition-table lookup
* successor-map cache
* predecessor-map cache
* finite-state transition planner
* count-table predictor
* compressed predictive-map memory
* direct episodic graph traversal

Purpose:

Detect whether any claimed candidate effect can be matched by predictive-structure lookup, transition-table memory, or graph/cache traversal.

Required collapse rule:

```text
if graph_cache_control_matches_candidate_under_predeclared_comparison_rule:
    candidate_verdict = not_distinguishable_in_this_setting
```

No numerical comparison margin may be invented in this task card.

## Mandatory first-class control stack B: generic replay-buffer controls

This control stack is first-class and mandatory.

A future Gate 1 task card omitting this stack is invalid by definition.

Generic replay form:

```text
B = replay buffer
q(i | context) = replay selector
r_i = selected replay item
theta_after = theta_before + update(theta_before, r_i)
```

Required controls:

* frozen Gate 0 no-replay learner
* same-data online-only learner
* uniform factual replay
* salience-weighted factual replay
* generic chunk replay
* random replay
* shuffled replay
* equal-compute extra training
* frozen-theta control
* post-hoc trace generator control

Purpose:

Detect whether the candidate adds irreducible structure beyond buffer sampling plus update.

Required collapse rule:

```text
if generic_replay_control_matches_candidate_under_predeclared_comparison_rule:
    candidate_verdict = replay_buffer_collapse
```

No numerical comparison margin may be invented in this task card.

## Required ablations

### Salience selection

Salience selection is a modifier only.

It must not be treated as a standalone skeleton.

Required ablations:

* no-salience replay
* prediction-error salience
* uncertainty salience, only if epistemic vs aleatoric distinction is logged
* salience-weighted generic replay baseline

Blocked salience variants:

* reward salience unless Gate-0-reduced
* value salience unless Gate-0-reduced
* goal salience unless Gate-0-reduced
* preference salience
* affect salience
* user-model salience
* semantic-memory salience

### Order-sensitive update geometry

Order is a modifier only.

It must not be treated as standalone consolidation evidence.

Required ablations:

* matched item multiset
* matched compute
* matched optimizer state
* matched seeds
* shuffled order
* random order
* candidate order
* reverse/forward order only if preregistered

Hand-picked replay order after observing outcomes is invalid.

## Runtime-access attestation

A future Gate 1 task card must require an explicit evaluation-time allowed-access manifest.

### Candidate A forbidden runtime access

For fast-to-slow transfer, evaluation must forbid access to:

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

### Candidate B forbidden runtime access

For latent-dynamics replay, evaluation must forbid access to:

* stored hidden states
* hidden-state cache
* prefix cache
* chunk checkpoint library
* longer-context retrieval index
* sequence lookup table
* original chunks, unless recomputation protocol explicitly permits raw trace replay
* nearest-neighbor sequence retrieval
* graph/cache lookup
* transition-table lookup

## Source deletion timing

A future Gate 1 task card must preregister deletion timing.

Post-hoc deletion scheduling is invalid.

### Required deletion events for Candidate A

Must distinguish:

* deletion before transfer
* deletion after transfer but before evaluation
* deletion after evaluation
* source weakening
* teacher removal
* generator removal
* synthetic library removal
* summary memory removal
* fast-store removal

Candidate A is interpretable only if the claimed effect remains after source removal and slow-only evaluation.

Collapse condition:

```text
if deleting fast/source objects after transfer but before evaluation destroys the effect:
    candidate_A_verdict = source_dependent_collapse
```

### Required deletion events for Candidate B

Must distinguish:

* hidden-state cache removal
* prefix-cache removal
* chunk checkpoint removal
* sequence lookup removal
* longer-context retrieval removal
* raw chunk access under explicitly allowed recomputation protocol
* raw chunk access disabled during evaluation, except where preregistered

Candidate B is interpretable only if the claimed effect remains without hidden-state or prefix-cache access.

Collapse condition:

```text
if hidden_state_cache_or_longer_context_retrieval_matches_or_erases_effect:
    candidate_B_verdict = cache_or_retrieval_collapse
```

## Lineage records

A future Gate 1 task card must require a lineage ledger.

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
```

Lineage reconstruction must be possible from frozen records alone.

Collapse condition:

```text
if lineage_cannot_be_reconstructed:
    verdict = trace_nonidentifiable
```

## Gate 0 interface boundary

Allowed variables:

* raw trace items
* action
* observation
* belief state
* theta parameters
* prediction error
* uncertainty
* all-action predictions
* counterfactual action contrast only as historical excluded context
* transition / observation pseudo-counts
* chronology / commitment records

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

If any candidate requires blocked variables without derivation lineage, the future Gate 1 task must fail before execution.

## Anti-hardcoding scan

A future Gate 1 task card must include an anti-hardcoding scan.

Required checks:

* no hand-coded deletion timing
* no curated replay items selected after outcome inspection
* no manually tuned salience formula after outcome inspection
* no hand-picked seeds
* no hard-coded graph topology in candidate path
* no hand-curated chunk boundaries
* no manually tuned burn-in length
* no hidden if-else behavior
* no threshold tuning after results
* no environment design that trivially favors the candidate
* no post-hoc margin changes
* no post-hoc lineage repair

If success depends on any of the above, the result is invalid.

## Evidence outputs required from the future executable task

This task card does not authorize implementation, but any later executable task must produce at minimum:

```text
1. task manifest
2. frozen comparison margins
3. candidate run manifests
4. control run manifests
5. runtime-access manifests
6. lineage ledgers
7. source deletion logs
8. model snapshot hashes
9. slow-state before/after snapshots
10. latent recomputation records
11. baseline output records
12. anti-hardcoding audit report
13. stop-condition report
14. final bounded verdict report
```

## Acceptance gate design

A later executable Gate 1 task may pass only if all of the following are true.

### Universal acceptance requirements

```text
all_comparison_margins_predeclared = true
runtime_access_attestation_pass = true
lineage_reconstruction_pass = true
source_deletion_timing_preregistered = true
anti_hardcoding_scan_pass = true
gate0_interface_audit_pass = true
mandatory_graph_cache_controls_present = true
mandatory_generic_replay_controls_present = true
counterfactual_action_replay_absent = true
```

### Candidate A acceptance requirements

```text
candidate_A_slow_only_evaluation_pass = true
fast_store_removed_before_evaluation = true
teacher_removed_before_evaluation = true
generator_removed_before_evaluation = true
synthetic_library_removed_before_evaluation = true
summary_memory_removed_before_evaluation = true
slow_state_snapshot_delta_logged = true
graph_cache_controls_do_not_match_under_predeclared_rule = true
generic_replay_controls_do_not_match_under_predeclared_rule = true
teacher_cache_control_does_not_match_under_predeclared_rule = true
generator_as_memory_control_does_not_match_under_predeclared_rule = true
equal_compute_control_does_not_match_under_predeclared_rule = true
```

### Candidate B acceptance requirements

```text
candidate_B_cache_free_evaluation_pass = true
latent_traces_recomputable_from_raw_chunks = true
encoder_dynamics_snapshots_frozen = true
chunk_boundaries_preregistered = true
burn_in_length_preregistered = true
hidden_state_cache_forbidden = true
prefix_cache_forbidden = true
longer_context_retrieval_forbidden = true
hidden_state_cache_control_does_not_match_under_predeclared_rule = true
longer_context_retrieval_control_does_not_match_under_predeclared_rule = true
generic_chunk_replay_control_does_not_match_under_predeclared_rule = true
same_data_online_only_control_does_not_match_under_predeclared_rule = true
equal_compute_control_does_not_match_under_predeclared_rule = true
```

### Package acceptance rule

Because Phase 4 froze fast-to-slow as primary and latent as secondary, a future bounded Gate 1 execution may only claim the package-level preflight result if Candidate A is evaluated.

Candidate B may strengthen the package only as secondary evidence.

Candidate B alone must not be used to imply the primary Gate 1 package passed.

Allowed future package verdicts:

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
gate1_preflight_blocked_environment_lookup_triviality
```

## Stop conditions

The future executable Gate 1 task must stop or fail if any of the following occur:

```text
counterfactual_action_replay_reintroduced = true
mandatory_graph_cache_controls_missing = true
mandatory_generic_replay_controls_missing = true
comparison_margins_not_predeclared = true
runtime_access_attestation_missing = true
source_deletion_timing_not_preregistered = true
lineage_records_incomplete = true
gate0_interface_violation = true
candidate_depends_on_runtime_retrieval = true
candidate_depends_on_source_access_at_evaluation = true
graph_cache_control_matches_effect_under_predeclared_rule = true
generic_replay_control_matches_effect_under_predeclared_rule = true
hidden_state_cache_matches_latent_effect = true
longer_context_retrieval_matches_latent_effect = true
teacher_or_generator_remains_on_runtime_path = true
source_deletion_after_transfer_removes_fast_to_slow_effect = true
synthetic_or_counterfactual_item_leaks_future_outcome = true
environment_solved_by_lookup = true
success_depends_on_hardcoded_schedule_or_seed = true
post_hoc_margin_change_detected = true
post_hoc_lineage_repair_detected = true
```

## Rollback plan

If any stop condition fires, rollback must be explicit.

Rollback outcomes:

```text
rollback_to_phase4_scope_edit
rollback_to_phase3_delta_retry
rollback_to_phase2r_retry
block_gate1_no_clean_candidate
```

Rollback rules:

* If controls are missing, rollback to task-card design; do not execute.
* If counterfactual replay is reintroduced, rollback to Phase 4 scope enforcement.
* If graph/cache controls match the candidate, mark candidate as not distinguishishable in that setting.
* If generic replay controls match the candidate, mark candidate as replay-buffer collapse.
* If source-removal destroys Candidate A, mark fast-to-slow as source-dependent collapse.
* If hidden-state cache or longer-context retrieval matches Candidate B, mark latent as cache/retrieval collapse.
* If lineage cannot be reconstructed, mark trace non-identifiability.
* If Gate 0 variables are violated, mark Gate 0 interface failure.
* If both primary and secondary candidates fail, block Gate 1.

## Required final report shape for future executable task

A later executable task must end with a bounded report containing:

```text
A. Executive verdict
B. Scope confirmation
C. Candidate A result
D. Candidate B result
E. Mandatory graph/cache control results
F. Mandatory generic replay control results
G. Runtime-access attestation
H. Source deletion timing report
I. Lineage reconstruction report
J. Gate 0 interface audit
K. Anti-hardcoding audit
L. Stop-condition report
M. Claim ceiling statement
N. What this does not prove
O. Rollback or next-action recommendation
```

## What this task card does not prove

This task card does not prove either candidate works.

It does not prove Gate 1 will pass.

It does not prove replay / consolidation is necessary.

It does not prove predictive superiority over retrieval.

It does not prove consciousness, subjective experience, real emotion, self-awareness, agency, functional-subject evidence, electronic life, companion readiness, EGO readiness, or AGI.

It does not authorize implementation.

It only defines a bounded evidence contract that a later executable Gate 1 task may instantiate.
