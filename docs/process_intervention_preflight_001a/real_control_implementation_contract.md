# PROCESS-INTERVENTION-PREFLIGHT-001A Real-Control Implementation Contract

## Hard Rule

actual implementations or real closed-form decision procedures
Hardcoded competence attestations
Hardcoded fairness attestations

All future cheap controls must be actual implementations or real closed-form
decision procedures. The required standard is actual implementations or real
closed-form decision procedures. Name-only controls are invalid. Hardcoded competence
attestations and hardcoded fairness attestations are invalid. A listed but
unimplemented required control counts as missing. If a required control is
missing, the future executable preflight fails.

## Required Control Signature Fields

Each control must freeze:

```text
control_name
family
allowed_access
forbidden_access
online_update_access
intervention_label_access
trace_generation_rights
resource_budget
state_budget
memory_budget
solve_criterion
competence_calibration_task
failure_verdict_if_it_matches
```

## Concrete Challenger Signatures

All listed challengers are required unless the future task card explicitly
records a stronger replacement and fails if that replacement is absent.

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

## Access Rules

```text
allowed_access = observation, action, allowed history, intervention_condition when also visible to witness
forbidden_access = hidden simulator state, future observation, future outcome, verifier label, seed leakage, split leakage
online_update_access = current step inputs only, committed before later probe result
intervention_label_access = allowed for intervention_labeled_graph_cache and causal_table if witness receives same intervention_condition
trace_generation_rights = audit output only, never hidden working memory
```

## Solve Criterion

A fair cheap control solves the future task if it matches all frozen metrics
within the declared equivalence band and matches the frozen witness-vs-online-
control separation statistic. If it matches, the future executable preflight
fails with a control-match verdict, not a pass.
