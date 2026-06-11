# NEW-PROBLEM-PREFLIGHT-001A Proxy Contract

## Contract Verdict

```text
task_id = NEW-PROBLEM-PREFLIGHT-001A
verdict = new_problem_preflight_001a_proxy_contract_bounded_pass
execution_type = proxy contract drafting + collapse audit + falsification design only
mechanism_implementation_authorized = false
mechanism_training_authorized = false
```

## Selected Proxy

```text
primary_axis = process / intervention
primary_proxy = P1 Intervention-Sensitive State Update Proxy
online_adaptation = supporting_constraint
causal_intervention = supporting_constraint
resource_constraint = symmetric_accounting_only
value_state = deferred
```

The proxy asks whether controlled interventions alter the allowed update path,
state delta, and later behavior in ways that fair cheap controls cannot
reproduce under the same access, trace/replay, ablation, deletion, and
counterfactual probes.

## Not The Proxy

```text
history_to_output_label = rejected
decorative_state_trace = rejected
cache_key_as_mechanism = rejected
FSM_state_as_mechanism = rejected
summary_statistic_as_belief = rejected
intervention_log_as_trace_theater = rejected
resource_starvation_gap = rejected
value_emotion_subjectivity_proxy = rejected
```

## Acceptance Shape For A Future Executable Card

```text
not_output_level_proxy = true
primary_axis_process_intervention = true
future_behavior_effect_required = true
state_delta_metric_contract_defined = true
trace_replay_contract_defined = true
intervention_contract_defined = true
mandatory_controls_carried_forward = true
claim_ceiling_enforced = true
```

If future evidence is matched by behavior-only replay, trace-only replay,
graph/cache trace generation, FSM, summary statistics, kNN, or online cheap
controls under fair access, the future proxy fails.

## Boundary

```text
MODEL_CLASS_RESET = not_authorized
Gate1_reopen = not_authorized
same_agent_bridge = blocked
EGO_integration = not_authorized
```
