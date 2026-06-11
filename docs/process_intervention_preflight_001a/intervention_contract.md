# PROCESS-INTERVENTION-PREFLIGHT-001A Intervention Contract

Required intervention families:

```text
state deletion
memory deletion
representation freezing
prediction-error injection
counterfactual action substitution
observation perturbation
history-preserving causal perturbation
online distribution shift
```

Each intervention must define:

```text
what changes
what must not change
expected internal update effect
expected later behavior effect
cheap-control collapse risk
failure condition
```

Failure gates:

```text
intervention does not change update path
deletion/freezing has no later behavior effect
prediction error is only logged but not used
counterfactual action does not alter state update
```
