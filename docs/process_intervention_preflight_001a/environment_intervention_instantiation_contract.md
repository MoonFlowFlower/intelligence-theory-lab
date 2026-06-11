# PROCESS-INTERVENTION-PREFLIGHT-001A Environment Intervention Instantiation Contract

## Frozen Environment Family

The future executable task must use a bounded offline environment family with:

```text
finite episodes
paired baseline, intervened, and non_intervened_twin episodes
observable context aliases that do not reveal hidden simulator state
heldout intervention compositions or novel intervention-context pairs
no seed, split, future observation, future outcome, or verifier-label leakage
```

If the intervention space is fully enumerable by a causal table or graph/cache
within budget and those controls match, the future task fails.

## Intervention Instantiation Schema

Each intervention must freeze:

```text
intervention_id
intervention_name
when_applied
trigger_condition
what_changes
what_must_not_change
expected_internal_update_effect
expected_later_behavior_effect
allowed_access_change
forbidden_access_risk
oracle_leakage_risk
cheap_control_collapse_risk
required_controls
failure_condition
heldout_condition
paired_control_episode
```

## Required Intervention Families

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

`intervention_labeled_graph_cache` may key on `intervention_condition`.
intervention_labeled_graph_cache may key on `intervention_condition`.
`causal_table` may use intervention labels when the witness receives the same
labels. Denying this access is an invalid cheap-control weakening.

Failure verdict:

```text
process_intervention_preflight_001a_amendment_001_failed_intervention_instantiation_missing
```
