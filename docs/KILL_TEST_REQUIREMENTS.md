# Kill Test Requirements

Every theory must define kill tests before implementation.

## Required Gates

```text
label permutation
effect swap
action distribution counterfactual
hidden-state leak scan
metric provenance audit
trace replay
behavior-only replay
strong baseline equivalence
ablation no-op audit
parameter sweep
heldout causal world
```

## Mandatory Stop Conditions

Stop and close or downgrade if:

```text
candidate uses semantic action labels
candidate reads hidden future or oracle state
candidate uses evaluator metric as feature
candidate wins only against weak baselines
ablation is no-op
score changes but action distribution does not
trace records a variable that selector does not read
label permutation changes behavior when semantics are preserved
effect swap does not change behavior when effects change
strong heuristic matches candidate
parameter sweep collapses support
successor does not explain predecessor failures
```

## Evidence Standard

Primary evidence is counterfactual action-distribution change under declared constraints.

Secondary evidence includes score change, trace metrics, reward, viability, and report summaries.

