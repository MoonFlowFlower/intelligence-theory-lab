# REPRESENTATIONAL-GAP-PREFLIGHT-001B

## Title

Fair-control representational-gap preflight after 001A audit closeout.

## Task Identity

```text
task_id = REPRESENTATIONAL-GAP-PREFLIGHT-001B
status = executable_after_stage0_freeze_and_anchor
research_layer = mechanism hypothesis layer / fair-control representational-gap preflight
parent_closeout = REPRESENTATIONAL-GAP-PREFLIGHT-001A-AUDIT-CLOSEOUT
execution_type = design + closed-form proof + constructive verifier only
mechanism_training_authorized = false
agent_training_authorized = false
same_agent_bridge_authorized = false
model_class_reset_authorized = false
ego_integration_authorized = false
```

## Parent Audit Inheritance

001B inherits the independent audit disposition of 001A:

```text
codex_001a_verdict = superseded_by_independent_audit
001a_full_pass_status = rejected
001a_residue_status = narrow_residue_accepted_only
accepted_residue = K<=4 bounded-window collision gap; valid 1-bit XOR witness
rejected_claims = count/table family gap; FSM family gap; graph-cache family gap; controls_not_disabled_by_construction; hardcoded competence/fairness attestations
MODEL-CLASS-RESET-PREFLIGHT-001A = not_authorized
same_agent_bridge = not_authorized
Gate1_reopen = not_authorized
```

001A may be cited only as a negative-audit parent and as a narrow bounded-window
residue. It is not a full representational-gap preflight pass.

## Correct Problem Definition

Can a bounded task family preserve a representational gap after fair full-history
controls are given real implementations and the same allowed observation/action
stream as the witness?

This task is not allowed to rescue 001A. If fair controls solve the frozen
target, the correct outcome is failure.

## Authorization Boundary

Authorized outputs only:

```text
docs/REPRESENTATIONAL-GAP-PREFLIGHT-001B.md
src/representational_gap_preflight_001b/
tests/test_representational_gap_preflight_001b.py
artifacts/representational_gap_001b/
```

Forbidden:

```text
mechanism training
agent training
model-class reset experiment
Gate1 replay/consolidation rerun
Candidate A rerun
Candidate B residue rerun
same-agent bridge drafting or implementation
EGO mainline changes
LLM/RAG/companion/emotion/relationship/user-model modules
consciousness / agency / functional-subject / AGI claims
```

## Frozen Candidate Environment

This preflight retests the only accepted 001A residue under fair controls:

```text
environment_family = ParityAliasGridFairHistory-v1
ladder_level = L1_partial_observable_causal_environment
sequence_length = 6
token_alphabet = a0_o0, a0_o1, a1_o0, a1_o1
target_rule = XOR over action_bit XOR observation_bit for every token in the full history
heldout_split_definition = exhaustive finite family; exact-match training split withheld for retrieval probes only
```

The positive witness is a one-bit XOR update rule using only allowed tokens.

The decisive 001B question is whether fair full-history controls also solve this
target. If they do, the verdict must be failure.

## Stage 0 Freeze and Anchor

Before any verifier run:

```text
task_card_hash = required
environment_family_definition = frozen
target_rule_definition = frozen
sequence_or_episode_length = frozen
heldout_split_definition = frozen
control_family_definitions = frozen_with_actual_signatures
graph_cache_family_definitions = frozen_with_actual_signatures
fsm_family_definitions = frozen_with_capacity_bounds
summary_family_definitions = frozen_with_actual_statistics
allowed_access_contract = frozen
positive_witness_class_definition = frozen
external_time_anchor = required
first_run_start_time_after_anchor = required
```

If Stage 0 cannot be verified:

```text
verdict = representational_gap_001b_failed_stage0_anchor
claim_ceiling = no 001B representational-gap evidence
```

## Fair Control Families

All controls must be actual implementations or real closed-form decision
procedures. Name-only controls, hardcoded competence passes, and hardcoded
fairness passes are invalid.

Required families:

```text
C0 bounded-window controls K=1..4
C1 fair full-history count/statistic controls
C2 finite-state automaton controls with capacities 2,4,8,16
C3 graph/cache controls with actual memory/state
C4 kNN / episodic retrieval controls
C5 summary controls
C6 oracle/leakage probes
```

If any fair full-history count/statistic, FSM, graph/cache, kNN, episodic, or
summary control solves the target, 001B fails rather than passing partially.

## Acceptance Gate

A pass requires all of:

```text
stage0_anchor_pass = true
environment_contract_frozen = true
access_contract_frozen = true
control_signatures_frozen = true
control_competence_tests_execute_real_code_or_real_proofs = true
bounded_window_gap_verified = true
full_history_count_statistic_controls_fail_fairly = true
finite_state_automaton_controls_fail_fairly = true
graph_cache_controls_fail_fairly = true
knn_episodic_controls_fail_fairly = true
summary_controls_fail_fairly = true
positive_witness_exists = true
positive_witness_uses_only_allowed_access = true
positive_witness_not_in_failed_challenger_family = true
controls_not_disabled_by_construction = true
environment_not_lookup_trivial = true
not_trivial_horizon_gap = true
claim_ceiling_observed = true
```

If the positive witness belongs to a challenger family that is declared to fail,
001B fails.

## Allowed Verdicts

```text
representational_gap_001b_bounded_pass
representational_gap_001b_failed_window_only_gap
representational_gap_001b_blocked_trivial_horizon_gap
representational_gap_001b_failed_count_or_statistic_control_solved
representational_gap_001b_failed_fsm_control_solved
representational_gap_001b_failed_graph_cache_control_solved
representational_gap_001b_failed_knn_or_episodic_control_solved
representational_gap_001b_failed_summary_control_solved
representational_gap_001b_failed_no_positive_witness
representational_gap_001b_failed_witness_uses_oracle_access
representational_gap_001b_failed_witness_family_contradiction
representational_gap_001b_blocked_controls_disabled_by_construction
representational_gap_001b_blocked_lookup_triviality
representational_gap_001b_failed_hardcoded_attestation
representational_gap_001b_failed_stage0_anchor
representational_gap_001b_failed_scope_violation
```

## Claim Ceiling

At most:

```text
bounded fair-control representational-gap preflight evidence
```

This does not prove a new model class works.

```text
model_class_reset = not_authorized
Gate1_reopen = not_authorized
same_agent_bridge = blocked
EGO_integration = not_authorized
agency_consciousness_functional_subject_companion_AGI_claims = not_supported
```
