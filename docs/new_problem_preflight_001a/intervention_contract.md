# NEW-PROBLEM-PREFLIGHT-001A Intervention Contract

Future executable tasks must freeze all intervention operators before any run.

## Required Intervention Categories

```text
I1 state deletion
I2 memory deletion
I3 representation freezing
I4 prediction-error injection
I5 counterfactual action substitution
I6 observation perturbation
I7 history-preserving causal perturbation
I8 online distribution shift
```

For each intervention, the future task card must define:

```text
intervention_name
when_applied
what_is_changed
what_must_not_be_changed
expected effect on internal update
expected effect on future behavior
cheap-control collapse risk
oracle/leakage risk
failure condition
```

## Required Causal Link

```text
future_behavior_effect_required = true
```

If an intervention only changes trace fields but not later behavior, the future
proxy must fail. If counterfactual action substitution does not change the
allowed update path where the contract says it should, the future proxy must
fail.
