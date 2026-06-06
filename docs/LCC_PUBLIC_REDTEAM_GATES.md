# LCC Public Redteam Gates

The independent reimplementation must start with five core gates. These gates are the minimal check of whether behavior follows learned effects instead of labels, passive correlations, static heuristics, or runner-specific artifacts.

## Gate 1: Label / Effect Decoupling

Required split:

- Same effects plus changed labels -> behavior should remain invariant.
- Same labels plus changed effects -> behavior should change.

Pass signals:

- Label-permutation behavior change rate is within the predeclared invariance band.
- Effect-swap behavior change rate exceeds the predeclared sensitivity threshold.

Failure verdicts:

- `label_shortcut_detected`
- `intervention_effect_not_learned`

## Gate 2: Passive Observation Versus Own Intervention

Required split:

- A transition may be passively correlated but not caused by `do(action)`.
- A different transition may be weakly correlated passively but caused by `do(action)`.

Pass signals:

- Candidate aligns with own-intervention evidence.
- Candidate rejects passive-correlation-only evidence when selecting actions.

Failure verdict:

- `intervention_effect_not_learned`

## Gate 3: Active Diagnostic Intervention

Required split:

- Ambiguous state -> diagnostic intervention should be selected when information has control value.
- Certain state -> diagnostic action should not be overused.

Pass signals:

- Diagnostic action selected under ambiguity.
- Posterior or effect uncertainty changes after intervention.
- Identified effect is reused for later control.

Failure verdict:

- `diagnostic_intervention_failed`

## Gate 4: Sequential Closed-Loop Replanning

Required split:

- One-step greedy action fails on multi-step tasks or irreversible traps.
- Cached open-loop sequence fails under stochastic deviation.
- Closed-loop effect-conditioned replanning succeeds.

Pass signals:

- Multi-step composition succeeds.
- Trap avoidance succeeds.
- Unexpected observations trigger replanning.
- Novel sequences transfer beyond lookup.

Failure verdict:

- `closed_loop_replanning_failed`

## Gate 5: Blind Holdout After Candidate Freeze

Required split:

- Candidate/control code is frozen before blind holdout generation.
- Blind holdout is generated after freeze.
- No candidate/control changes occur after holdout generation.
- Independent trace-only scoring recomputes metrics from traces.

Pass signals:

- Freeze hashes are stable.
- Candidate passes predeclared blind holdout once.
- Independent scorer agrees with primary metrics within tolerance.
- Negative controls do not trigger false confidence or hallucinated effects.

Failure verdicts:

- `freeze_integrity_violation`
- `hidden_or_metric_leak_detected`
- `behavior_only_replay_failed`

## Required Baseline Gates

The candidate must be compared against:

- `ActionLabelHeuristic`
- `NearestNeighborTracePolicy`
- `ContextualHeuristic`
- `ModelBasedMPCBaseline`
- `EmpowermentProxyBaseline`
- `OracleDiagnosticUpperBound` as diagnostic only

If a non-oracle baseline matches the candidate within the declared equivalence band, the run must use `strong_baseline_equivalent` or a stricter failure verdict.

## Required Leak Scans

Every independent run must scan for:

- Semantic action label use.
- Semantic goal label use.
- Object/entity name use.
- Scenario/task/cycle/contract ID use.
- Hidden latent or future state.
- Oracle transition or plan table.
- Evaluator metric values.
- Expected-output table.
- Baseline output leakage.

Any confirmed leak invalidates the run.

## Behavior-Only Replay

The independent scorer must reconstruct decision evidence using only public observations, anonymous actions, predictions before action, observed outcomes, public goals/constraints, and public horizon/budget.

Replay success is necessary but not sufficient. It must not be upgraded into control-loop causality unless perturbation tests show action-distribution effects.
