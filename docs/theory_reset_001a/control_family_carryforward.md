# THEORY RESET 001A Control Family Carryforward

Every future mechanism preflight must treat the following as mandatory
adversaries:

```text
full-history count/statistic controls
finite-state / automaton controls
graph/cache controls
kNN / episodic retrieval controls
summary/statistic controls
oracle/leakage probes
shuffled-label or shuffled-outcome controls where applicable
behavior-only replay controls
trace-only replay controls
random-representation controls
ablation controls
```

## Carryforward Rule

```text
omitting_any_required_family = preflight_incomplete
banning_useful_allowed_statistics = invalid
disabling_graph_cache_or_kNN_by_split_design = invalid
allowing_witness_state_but_forbidding_equivalent_FSM_state = invalid
hardcoded_competence_or_fairness_attestation = invalid
```

## Future Failure Rule

If any fair control reproduces both behavior and declared trace/process
evidence, the future task must fail. A mechanism claim cannot rest on output
labels alone.
