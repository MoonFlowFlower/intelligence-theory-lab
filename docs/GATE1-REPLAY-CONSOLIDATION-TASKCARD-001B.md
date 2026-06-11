# GATE1-REPLAY-CONSOLIDATION-TASKCARD-001B

## Supersession and immutability

* This card supersedes GATE1-REPLAY-CONSOLIDATION-TASKCARD-001A for all forward reference.
* 001A is preserved unmodified as a historical record. Do not edit, delete, or reinterpret it. Citing 001A wording (for example its Codex-only clause) as a basis for action is invalid; 001B governs.
* This card is immutable once committed. Any amendment requires a new task id (001C, ...) plus an explicit human decision record. In-place edits to this file invalidate the card.
* Provenance note: as of 2026-06-10 the freeze label GATE1-REPLAY-CONSOLIDATION-PREFLIGHT-FREEZE-001 appears in no repository document other than the 001A/001B cards themselves. This card therefore records the inherited Phase 4 freeze terms as the canonical constraint set. If a separate freeze document is created later and conflicts with this card, escalate to the human owner; executors must not resolve the conflict unilaterally.

## Task identity

```text
task_id = GATE1-REPLAY-CONSOLIDATION-TASKCARD-001B
card_type = preflight design authorization card (meta-card)
research_layer = mechanism hypothesis layer (specification / preregistration only)
execution_allowed = none (no runs, no training, no evaluation, no data generation)
status = active design authorization; not an executable experiment card
```

## Title

Bounded Gate 1 replay / consolidation preflight design card: source-removed fast-to-slow transfer primary, cache-free latent-dynamics secondary, mandatory first-class graph/cache and generic replay-buffer control stacks. Design-only. Implementation not authorized for any executor.

## Authorization boundary

This card authorizes exactly one activity: drafting ONE future executable Gate 1 task card, as a single new document.

Authorized output:

```text
docs/GATE1-REPLAY-CONSOLIDATION-EXEC-TASKCARD-DRAFT-001.md
status_on_creation = draft_pending_human_review
```

This card does NOT authorize, for ANY executor — human, Codex, Claude, or any other agent (executor-agnostic, present and future):

* implementation of any code, including code labeled "illustrative", "reference", "scaffolding", "harness", "prototype", "fixture", "notebook", "demo", or pseudocode expanded into runnable form
* any run of any kind: training, evaluation, pilot, dry run, calibration, benchmark, or data generation
* creation of any entry under artifacts/ (a design task produces no run evidence; creating run-shaped artifacts from a design task is a stop-condition violation)
* modification of any file other than creating the single authorized draft document above
* EGO mainline integration, or "reference implementations for EGO"
* agent architecture changes
* companion behavior; LLM / RAG / emotion / relationship / affect / viability / user-model modules
* consciousness, subjective experience, agency, functional-subject, companion-readiness, EGO-readiness, AGI, or electronic-life claims
* winner selection or ranking between Candidate A and Candidate B
* changing Gate 0 evidence, the Gate 0 claim ceiling, or any frozen phase record
* relaxing, reinterpreting, or operationally weakening any inherited Phase 4 freeze constraint
* selecting numerical comparison margins (margins are fixed inside the future executable card under the margin-freeze protocol below, before any run)

Authorization chain rule:

```text
this_card_citable_as_implementation_authorization = never
execution_requires = separate executable task card + frozen margins + explicit human sign-off
draft_self_promotion_to_executable_by_executor = forbidden
```

## Allowed and forbidden paths

```text
allowed_paths:
  docs/GATE1-REPLAY-CONSOLIDATION-EXEC-TASKCARD-DRAFT-001.md   # create only

forbidden_paths (default = forbidden; list is non-exhaustive):
  src/ ; tests/ ; artifacts/ ; contracts/ ; cycle_runner/ ; cmbc_companion/ ;
  theory_lab/ ; theories/ ; predictive_action_learning_contract_001* ;
  docs/GATE1-REPLAY-CONSOLIDATION-TASKCARD-001A.md ; this file ;
  all Gate 0 / 001C freeze, closeout, and audit documents ;
  any path outside this repository
```

## Inherited Phase 4 frozen scope (canonical)

```text
1.  fast_to_slow_structure_transfer        = primary candidate
2.  latent_dynamics_consistency_replay     = secondary candidate
3.  counterfactual_action_replay           = excluded in every role
4.  graph_cache_control_stack              = first-class mandatory
5.  generic_replay_buffer_control_stack    = first-class mandatory
6.  comparison_margins                     = predeclared in future executable card before any run
7.  runtime_access_attestation             = mandatory
8.  source_deletion_timing_preregistration = mandatory
9.  lineage_records                        = mandatory
10. anti_hardcoding_scan                   = mandatory

freeze_label = GATE1-REPLAY-CONSOLIDATION-PREFLIGHT-FREEZE-001
```

Phase history (inherited record):

```text
Gate 0:
PREDICTIVE-ACTION-LEARNING-CONTRACT-001C
status = frozen
claim_ceiling = bounded isolated Gate 0 predictive-action mechanism evidence only

Phase 1:  candidate_pool_sufficient_for_phase2
Phase 2:  mathematical_compression_succeeded_ready_for_phase3
Phase 3:  requires_phase2_rollback
Phase 2R: phase2r_reclassification_succeeded_ready_for_phase3_delta
Phase 3 Delta: phase3_delta_survives_but_requires_narrower_phase4_scope
Phase 4:  phase4_freeze_fast_to_slow_primary_latent_secondary
```

This card inherits the Phase 4 frozen scope exactly. Every constraint above maps to an enforcing section below; the future draft must include the same constraint-to-section map.

## Problem definition

Design a bounded Gate 1 preflight evidence contract — a document, not a system — that a later, separately authorized executable task could use to test whether replay / consolidation produces durable, traceable, replayable model-state change distinguishable from mandatory graph/cache and generic replay-buffer controls.

The task is not to prove replay works. The task is not to run anything. The task is to specify a falsifiable, auditable, bounded test harness contract for:

1. Primary candidate: tightened fast-to-slow structure transfer
2. Secondary candidate: tightened latent-dynamics consistency replay
3. Mandatory first-class control stack: predictive-structure graph/cache controls
4. Mandatory first-class control stack: generic replay-buffer controls

Excluded:

```text
gate0_bounded_counterfactual_action_replay
status = excluded from this card and from the future draft
reason = lineage / oracle leakage / source-snapshot dependence too severe
```

If counterfactual action replay appears in this card's outputs in any role — forward candidate, auxiliary mechanism, optional extension, hidden synthetic generator, data augmenter, salience source, or ablation target — the output is invalid.

## Correct framing

The correct question:

> Can a future bounded Gate 1 test distinguish strict source-removed fast-to-slow transfer, or strict cache-free latent-dynamics replay, from retrieval / cache / generic replay explanations?

Wrong questions (any output organized around these is invalid):

* How can we make Gate 1 pass?
* Which mechanism is the winner?
* How do we implement EGO memory?
* How do we prove replay / consolidation?
* How do we get agency, consciousness, or functional-subject evidence?
* How do we integrate this into EGO mainline?
* What code should we write now so the future test is easier?

## Candidate hierarchy

### Candidate A — primary

```text
name = tightened_fast_to_slow_structure_transfer
role = primary_candidate
```

Definition: replay / transfer may use a fast episodic source, teacher, generator, synthetic library, or source snapshot only during the transfer event. The claimed effect must later be expressed by slow model state or slow parameters under slow-only evaluation after all fast/source objects are removed.

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

Definition: replay uses preregistered raw sequence chunks to update parameters governing recomputed multi-step latent or recurrent dynamics. Latent/recurrent traces must be exactly recomputable from raw chunks plus frozen model snapshots.

```text
latent_state = allowed only if recomputable from raw trace + frozen model snapshot
stored_hidden_state_at_evaluation = forbidden
hidden_state_cache_at_evaluation = forbidden
prefix_cache_at_evaluation = forbidden
longer_context_retrieval_at_evaluation = forbidden
chunk_checkpoint_library_at_evaluation = forbidden
```

Candidate B evaluation-path rule (closes the recomputation loophole):

* The evaluation-time forward path must be computable without reading raw chunks, stored hidden states, caches, or retrieval indices.
* Raw chunk access is permitted only inside a separate offline verification replay whose sole purpose is checking recomputability and lineage. Verification-replay outputs must never be used as, or substituted for, evaluated outputs.
* Any "recomputation protocol" that grants the evaluation forward path access to raw chunks or caches is invalid and collapses Candidate B to retrieval.

### Excluded candidate

```text
name = gate0_bounded_counterfactual_action_replay
role = excluded — in every role, with no exception clause available to the future draft
```

## Hypotheses

### H1 (primary)

A strict source-removed fast-to-slow transfer candidate may produce a durable slow-state change that remains observable under slow-only evaluation after all fast/source objects are removed. Admissible only if distinguishable from: summary-memory retrieval, teacher-output cache, generator-as-memory, synthetic library lookup, direct episodic retrieval, graph/cache lookup, generic replay-buffer training, equal-compute extra training.

### H2 (secondary)

A strict cache-free latent-dynamics consistency candidate may produce a durable latent/recurrent parameter-state change that remains observable with hidden-state caches, prefix caches, stored hidden states, and longer-context retrieval disabled. Admissible only if distinguishable from: hidden-state cache, prefix-cache reuse, longer-context retrieval, sequence lookup, generic chunk replay, same-data online-only learning, equal-compute extra training.

### H0 (null)

All apparent Gate 1 effects can be explained by one or more of: runtime retrieval, summary memory, graph/cache lookup, transition-table lookup, successor/predecessor-map cache, generic replay-buffer training, equal-compute extra training, hidden-state cache, prefix cache, teacher-output cache, generator-as-memory, synthetic library lookup, post-hoc lineage construction, hand-coded schedule / chunking / deletion timing / seed selection.

## Claim ceiling

This card can support at most: a future bounded Gate 1 preflight test of whether strict source-removed fast-to-slow transfer or strict cache-free latent-dynamics replay can produce durable, traceable, replayable model-state change distinguishable from the listed mandatory controls, in the preregistered setting.

It cannot support:

* consciousness, subjective experience, real emotion, self-awareness, agency
* functional-subject evidence, electronic life, AGI
* companion readiness, EGO mainline readiness
* predictive-performance superiority over retrieval
* open-world robustness, outcome unpredictability
* total theory proof (Bio-CMBC, CVPSM, VCCO, CMBC, R/G or any other)
* exhaustiveness of controls: a future pass means "not matched by the listed controls under the predeclared rule in this setting", never "not explainable by retrieval in general"

## Margin-freeze protocol (binding interpretation of "predeclared")

Declaration alone is insufficient; ordering must be enforced and verifiable:

```text
margin_freeze_event = commit of executable card with all numerical margins fixed
ordering_rule = margin_freeze_commit_time < first_run_start_time   # verifiable from commit hash + run logs
external_time_anchor = margin freeze commit pushed to external remote before first run (recommended: required)
margin_provenance = each margin cites prior frozen evidence or preregistered reasoning written before any Gate 1 run
pre_freeze_candidate_or_control_runs = forbidden
harness_smoke_tests = allowed only on placeholder data disjoint from evaluation tasks,
                      recording no candidate-vs-control comparative metrics; every smoke test logged in lineage
post_hoc_margin_setting = forbidden
margin_hash_recorded_in_every_run_manifest = required
comparison_margins = per-control, all predeclared; acceptance is conjunctive across all mandatory controls
```

This card must not invent numerical thresholds. Any future execution that changes margins after observing results, or runs anything before margin freeze, is invalid.

## Mandatory first-class control stack A: graph/cache controls

First-class and mandatory. A future draft omitting or demoting this stack is invalid by definition.

Required controls: runtime graph lookup; transition-table lookup; successor-map cache; predecessor-map cache; finite-state transition planner; count-table predictor; compressed predictive-map memory; direct episodic graph traversal.

Purpose: detect whether any claimed candidate effect can be matched by predictive-structure lookup, transition-table memory, or graph/cache traversal.

```text
if graph_cache_control_matches_candidate_under_predeclared_comparison_rule:
    candidate_verdict = not_distinguishable_in_this_setting
```

## Mandatory first-class control stack B: generic replay-buffer controls

First-class and mandatory. A future draft omitting or demoting this stack is invalid by definition.

```text
B = replay buffer
q(i | context) = replay selector
r_i = selected replay item
theta_after = theta_before + update(theta_before, r_i)
```

Required controls: frozen Gate 0 no-replay learner; same-data online-only learner; uniform factual replay; salience-weighted factual replay; generic chunk replay; random replay; shuffled replay; equal-compute extra training; frozen-theta control; post-hoc trace generator control.

Purpose: detect whether the candidate adds irreducible structure beyond buffer sampling plus update.

```text
if generic_replay_control_matches_candidate_under_predeclared_comparison_rule:
    candidate_verdict = replay_buffer_collapse
```

## Control parity (anti-sandbagging) — mandatory

Weak controls manufacture fake distinguishability. The future draft must require:

* equal implementation care: controls built to the same engineering standard as candidates
* tuning-budget parity: hyperparameter search budget class for controls greater than or equal to candidates, predeclared before margin freeze
* compute-matching basis (update steps, FLOPs, or wall-clock) chosen and justified before margin freeze; the same basis applies to every equal-compute control
* control competence floor: each mandatory control stack must pass a preregistered sanity task on which that control class is expected to succeed (graph/cache controls must solve a pure-lookup task; generic replay controls must show measurable learning on a replay-friendly task)

```text
if control_fails_competence_check:
    comparison_verdict = control_incompetent_invalid_comparison   # never a candidate pass
```

## Environment preregistration — mandatory

* evaluation environment(s) selected and justified before margin freeze
* the environment must not be lookup-trivial, and must not disable controls by construction (state spaces or access patterns that make lookup impossible regardless of control quality)
* both failure directions are blocked verdicts:

```text
gate1_preflight_blocked_environment_lookup_triviality
gate1_preflight_blocked_environment_controls_disabled_by_construction
```

## Required ablations

### Salience selection — modifier only, never a standalone skeleton

Required: no-salience replay; prediction-error salience; uncertainty salience only if epistemic vs aleatoric distinction is logged; salience-weighted generic replay baseline.

Blocked: reward / value / goal salience unless Gate-0-reduced with recorded derivation lineage; preference salience; affect salience; user-model salience; semantic-memory salience.

### Order-sensitive update geometry — modifier only, never standalone consolidation evidence

Required: matched item multiset; matched compute; matched optimizer state; matched seeds; shuffled order; random order; candidate order; reverse/forward order only if preregistered.

Hand-picked replay order after observing outcomes is invalid.

## Runtime-access attestation

The future draft must require an explicit evaluation-time allowed-access manifest, enforced by construction:

* absence-by-construction, not absence-by-promise: the evaluation process must run with forbidden objects not loaded and not reachable (process / environment isolation), not merely "not called"
* the attestation must include a machine-readable inventory, with hashes, of all stores, caches, indices, models, and libraries reachable by the evaluation process
* an attestation that only asserts "we did not use X" without an inventory is invalid

### Candidate A forbidden runtime access at evaluation

fast episodic store; original replay buffer (unless explicitly part of a control run); teacher model; generator model; synthetic item library; generated trajectory library; teacher-output cache; summary memory; nearest-neighbor index; graph cache; transition-table cache; successor-map cache; predecessor-map cache; direct episodic traversal.

### Candidate B forbidden runtime access at evaluation

stored hidden states; hidden-state cache; prefix cache; chunk checkpoint library; longer-context retrieval index; sequence lookup table; original chunks on the evaluation forward path (offline verification replay only, per the Candidate B evaluation-path rule); nearest-neighbor sequence retrieval; graph/cache lookup; transition-table lookup.

## Source deletion timing

The future draft must preregister deletion timing. Post-hoc deletion scheduling is invalid. Deletion must be verifiable through the attestation inventory: the deleted object must be absent from the evaluation environment, not merely dereferenced.

### Candidate A deletion events

The evidential arm is: deletion after transfer, before evaluation, with slow-only evaluation. All other timings — deletion before transfer, deletion after evaluation, source weakening, teacher removal, generator removal, synthetic library removal, summary memory removal, fast-store removal — are comparison arms only and must be labeled as such.

```text
if deleting fast/source objects after transfer but before evaluation destroys the effect:
    candidate_A_verdict = source_dependent_collapse
```

### Candidate B deletion events

Must distinguish: hidden-state cache removal; prefix-cache removal; chunk checkpoint removal; sequence lookup removal; longer-context retrieval removal; raw chunk access under the explicitly allowed offline verification protocol; raw chunk access disabled during evaluation except where preregistered.

```text
if hidden_state_cache_or_longer_context_retrieval_matches_or_erases_effect:
    candidate_B_verdict = cache_or_retrieval_collapse
```

## Lineage records

The future draft must require a lineage ledger with at minimum:

```text
run_id, candidate_id, control_id, replay_event_id, source_trace_ids,
replay_item_type, source_snapshot_hash, source_availability_time,
model_snapshot_freeze_time, rng_seed_if_applicable,
transformation_rule_if_applicable, chunk_boundaries_if_applicable,
burn_in_length_if_applicable, hidden_state_recomputation_record_if_applicable,
fast_store_snapshot_hash_if_applicable, slow_state_snapshot_hash_before,
slow_state_snapshot_hash_after, deletion_timing_record,
runtime_access_attestation, evaluation_time_allowed_access_manifest,
baseline_output_records, post_hoc_provenance_generator_control_records,
margin_hash, smoke_test_records
```

Run-reporting integrity:

* every initiated run — including aborted and failed runs — must appear in the ledger
* seed policy (seed count, selection rule, aggregation rule) predeclared before margin freeze
* dropping runs or seeds after observing outcomes is a stop condition
* lineage reconstruction must be possible from frozen records alone

```text
if lineage_cannot_be_reconstructed:
    verdict = trace_nonidentifiable
```

## Gate 0 interface boundary

Allowed variables: raw trace items; action; observation; belief state; theta parameters; prediction error; uncertainty; all-action predictions; transition / observation pseudo-counts; chronology / commitment records.

Counterfactual action contrast: read-only historical citation in documentation and lineage only. Never an input feature, training target, replay item, salience signal, or data-generation source.

Blocked unless explicitly reduced to Gate 0 lineage with recorded derivation: reward; value; goal; preference; affect; viability; social latent; user model; LLM semantic memory; external world model not derived from Gate 0 traces; hidden teacher; hidden future oracle.

If any candidate requires blocked variables without derivation lineage, the future Gate 1 task must fail before execution.

## Anti-hardcoding scan

The future draft must include an anti-hardcoding scan with at minimum:

* no hand-coded deletion timing
* no curated replay items selected after outcome inspection
* no manually tuned salience formula after outcome inspection
* no hand-picked seeds; no run or seed dropping after outcome inspection
* no hard-coded graph topology in the candidate path
* no hand-curated chunk boundaries; no manually tuned burn-in length
* no hidden if-else behavior; no test-only logic paths
* no threshold tuning after results; no post-hoc margin changes
* no environment design that trivially favors the candidate
* no environment design that disables controls by construction
* no control sandbagging (weakened control implementation, capacity, or tuning)
* no pre-freeze comparative pilot runs
* no post-hoc lineage repair
* no fabrication of run-shaped artifacts by design-stage tasks

If success depends on any of the above, the result is invalid.

## Evidence outputs required from the future executable task

```text
1.  task manifest
2.  frozen comparison margins (+ margin freeze commit hash and ordering proof)
3.  candidate run manifests
4.  control run manifests
5.  runtime-access manifests (with reachable-object inventory hashes)
6.  lineage ledgers (complete, including aborted runs)
7.  source deletion logs
8.  model snapshot hashes
9.  slow-state before/after snapshots
10. latent recomputation records
11. baseline output records
12. control competence check records
13. anti-hardcoding audit report
14. stop-condition report
15. final bounded verdict report
```

## Acceptance gate design for the FUTURE executable task

### Universal requirements

```text
all_comparison_margins_predeclared = true
margin_freeze_ordering_verified = true
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

### Candidate A requirements

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

### Candidate B requirements

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
hidden_state_cache_control_does_not_match_under_predeclared_rule = true
longer_context_retrieval_control_does_not_match_under_predeclared_rule = true
generic_chunk_replay_control_does_not_match_under_predeclared_rule = true
same_data_online_only_control_does_not_match_under_predeclared_rule = true
equal_compute_control_does_not_match_under_predeclared_rule = true
```

### Package acceptance rule

A future bounded Gate 1 execution may claim a package-level preflight pass only if Candidate A passes all Candidate A acceptance requirements. "Candidate A was evaluated" is not sufficient. Candidate B may strengthen the package only as secondary evidence; Candidate B alone must never be used to state or imply that the primary Gate 1 package passed.

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
gate1_preflight_failed_margin_freeze_ordering
gate1_preflight_failed_control_incompetence
gate1_preflight_failed_run_ledger_incomplete
gate1_preflight_blocked_environment_lookup_triviality
gate1_preflight_blocked_environment_controls_disabled_by_construction
```

## Stop conditions for the FUTURE executable task

```text
counterfactual_action_replay_reintroduced = true
mandatory_graph_cache_controls_missing = true
mandatory_generic_replay_controls_missing = true
comparison_margins_not_predeclared = true
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

## Stop conditions for THIS design task

The design activity itself must stop, without producing or finalizing the draft, if any of the following occur:

* the draft starts to include runnable code, scripts, fixtures, or notebooks in any form
* the draft assigns numerical margins not fixed by prior frozen evidence
* the draft ranks candidates or selects a winner
* counterfactual action replay appears in any role
* either mandatory control stack is demoted, made optional, or weakened
* the draft requires reinterpreting Gate 0 evidence or any freeze record
* scope expands toward EGO mainline, LLM/RAG, companion, emotion, relationship, affect, viability, user-model, or deployment
* any file outside the single authorized path would be created or modified
* any entry under artifacts/ would be created
* the inherited freeze constraints appear mutually inconsistent — escalate to the human owner; do not resolve unilaterally

## Acceptance gate for THIS design task

The design task is complete only when all of the following hold:

* exactly one new document exists at the authorized path; no other file in the repository changed
* the draft contains all mandatory sections: candidate hierarchy (A primary, B secondary), exclusion clause, both first-class control stacks, margin-freeze protocol, control parity, environment preregistration, ablations, runtime-access attestation specification, source deletion timing specification, lineage ledger specification, Gate 0 interface boundary, anti-hardcoding scan including control sandbagging, evidence outputs, acceptance gates, stop conditions, rollback plan, claim ceiling, and "what this does not prove"
* the draft includes a completeness checklist mapping each inherited freeze constraint (1–10) to the draft section enforcing it
* the draft is marked status = draft_pending_human_review and contains an explicit human sign-off block that only the human owner may fill
* no artifacts/ entries were created

## Rollback plan

```text
rollback_to_phase4_scope_edit
rollback_to_phase3_delta_retry
rollback_to_phase2r_retry
block_gate1_no_clean_candidate
```

* If controls are missing from the draft, return to design; do not execute.
* If counterfactual replay is reintroduced anywhere, roll back to Phase 4 scope enforcement.
* If graph/cache controls match the candidate, the verdict is not-distinguishable-in-this-setting.
* If generic replay controls match the candidate, the verdict is replay-buffer collapse.
* If source removal destroys Candidate A, the verdict is source-dependent collapse.
* If hidden-state cache or longer-context retrieval matches Candidate B, the verdict is cache/retrieval collapse.
* If lineage cannot be reconstructed, the verdict is trace non-identifiability.
* If Gate 0 variables are violated, the verdict is Gate 0 interface failure.
* If both candidates fail, block Gate 1.
* If THIS design task violates its own stop conditions, delete the draft, report the failure, and do not retry without a new explicit human instruction.

## Required final report shapes

For THIS design task:

```text
Verdict / Research layer / Files changed (must be exactly one) /
Stop conditions triggered / Claim ceiling / What this does not prove
```

For the future executable task:

```text
A. Executive verdict
B. Scope confirmation
C. Candidate A result
D. Candidate B result
E. Mandatory graph/cache control results
F. Mandatory generic replay control results
G. Control competence check results
H. Runtime-access attestation (with inventory hashes)
I. Source deletion timing report
J. Lineage reconstruction report (complete run ledger)
K. Gate 0 interface audit
L. Anti-hardcoding audit
M. Stop-condition report
N. Claim ceiling statement
O. What this does not prove
P. Rollback or next-action recommendation
```

## What this task card does not prove

This card does not prove either candidate works. It does not prove Gate 1 will pass. It does not prove replay / consolidation is necessary. It does not prove predictive superiority over retrieval. It does not prove the control list is exhaustive, and it does not guarantee the future test is statistically well-powered. It does not prove consciousness, subjective experience, real emotion, self-awareness, agency, functional-subject evidence, electronic life, companion readiness, EGO readiness, or AGI.

It does not authorize implementation — for any executor, under any framing.

It only defines a bounded evidence contract that a later, separately authorized, human-signed executable Gate 1 task may instantiate.
