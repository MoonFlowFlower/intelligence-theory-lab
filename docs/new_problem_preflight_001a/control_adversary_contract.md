# NEW-PROBLEM-PREFLIGHT-001A Control Adversary Contract

All future executable versions must include fair versions of:

```text
full-history count/statistic controls
online count/statistic controls
finite-state / automaton controls
online FSM controls
graph/cache controls
online graph/cache controls
kNN / episodic retrieval controls
online kNN controls
summary/statistic controls
causal table controls where applicable
behavior-only replay controls
trace-only replay controls
graph/cache trace-generator controls
random-representation controls
shuffled-label controls
shuffled-outcome controls
oracle/leakage probes
```

Controls must receive the same allowed information as the witness unless they
are explicitly labeled forbidden-access oracle/leakage probes.

```text
banning_useful_allowed_statistics = invalid
forbidding_equivalent_FSM_state = invalid
resource_starving_controls = invalid
hardcoded_competence_or_fairness = invalid
```

If a cheap control solves the future proxy under fair access, the future proxy
must fail.
