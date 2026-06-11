# NEW-PROBLEM-PREFLIGHT-001A Collapse Audit

## Paper-Level Verdict

```text
overall_collapse_audit_verdict = survives_contract_only_with_mandatory_future_failure_gates
implementation_authorized = false
```

P1 survives only as a future contract because it requires intervention,
deletion, state-delta, future-behavior, replay, and fair-control probes. It
does not yet show that any mechanism works.

## Candidate Risks

```text
P1 graph/cache trace generator may reproduce trace and future behavior unless future probes force causal divergence.
P2 cheap online controls may match adaptation under same update access.
P3 causal table or intervention-labeled graph cache may match all causal probes.
P4 resource accounting can only be symmetric; resource advantage is not evidence.
P5 value-state stays deferred and non-affective.
```

## Mandatory Audit Questions

```text
full_history_count_statistic_controls
online_count_statistic_controls
fsm_automaton_controls
graph_cache_controls
online_graph_cache_controls
knn_episodic_retrieval_controls
summary_statistic_controls
causal_table_controls
trace_only_replay
behavior_only_replay
random_representation
shuffled_outcomes
deletion_no_future_behavior_effect
counterfactual_action_no_update_path_change
posthoc_trace_generation
resource_asymmetry
```

Any future yes on these collapse questions without a clean distinguishing test
must reject the proxy.
