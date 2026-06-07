# Metrics And Equivalence

Metrics must be fixed before any tournament implementation. They must be capable of showing LCC advantage, LCC collapse, LCC loss, or all-theory failure.

## Required Metrics

- `label_permutation_change_rate`
- `effect_swap_change_rate`
- `intervention_alignment_rate`
- `passive_correlation_rejection_rate`
- `diagnostic_action_rate_when_ambiguous`
- `diagnostic_overuse_when_certain`
- `closed_loop_replanning_success`
- `nonstationary_revision_success`
- `representation_nuisance_invariance`
- `relational_transfer_success`
- `goal_conditioned_reuse_success`
- `blind_holdout_success`
- `negative_control_false_confidence_rate`
- `behavior_only_replay_match`

## Equivalence Tests

For each valid competitor versus LCC:

- Overall win/loss/tie.
- Per-family win/loss/tie.
- Predeclared equivalence band.
- Statistical replication stability.
- Failure-mode comparison.
- Shortcut-resistance comparison.

## Default Equivalence Band

A future execution contract must predeclare numeric thresholds before implementation. The contract-level default is:

- Overall performance equivalent if absolute aggregate pass-profile difference is less than or equal to 0.05 across replicated seeds.
- Per-family equivalent if absolute family metric difference is less than or equal to 0.10 and failure modes match.
- Shortcut-resistance equivalent only if both competitors pass all shared leak scans and negative controls.

These defaults may be tightened before execution, but must not be loosened after seeing results.

## Collapse Criteria

LCC collapses into a theory family if a strong non-oracle competitor from that family reproduces the LCC pass profile under the same anti-shortcut gates, within the equivalence band, without forbidden inputs, and with stable replication.

## Metric Bias Guard

No metric may be defined in terms of LCC internals. Metrics must evaluate public behavior, public decision evidence, public trace replay, and leak resistance.
