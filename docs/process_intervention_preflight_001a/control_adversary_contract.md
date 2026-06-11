# PROCESS-INTERVENTION-PREFLIGHT-001A Control Adversary Contract

Mandatory fair controls:

```text
full-history count/statistic
online count/statistic
FSM / automaton
online FSM
graph/cache
online graph/cache
kNN / episodic retrieval
online kNN
summary/statistic
causal table
behavior-only replay
trace-only replay
graph/cache trace generator
random representation
shuffled-label / shuffled-outcome
oracle/leakage probes
```

Controls must not be weakened, banned, resource-starved, or denied equivalent
allowed state/update access. Useful summary statistics are fair controls, not
leakage, unless they use forbidden oracle data.
