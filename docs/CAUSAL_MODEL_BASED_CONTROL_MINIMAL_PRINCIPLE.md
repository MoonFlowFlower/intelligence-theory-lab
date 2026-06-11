# Causal Model-Based Control Minimal Principle

## Status

```text
principle_status = strongest_surviving_theory_family_under_current_tournament
theory_support = not_yet
implementation_authorized = false
```

The cross-theory tournament did not prove a bottom intelligence principle. It did identify causal model-based control as the strongest surviving theory family under the current bounded tournament, because it reproduced the LCC pass profile under the same public I/O, redteam gates, independent scoring, and replication checks.

## Minimal Principle

Intelligence-relevant control is learned causal model-based control:

```text
learn p(outcome | do(action), context)
-> query counterfactuals
-> choose action or diagnostic intervention
-> observe outcome
-> revise model from prediction error
-> repeat under current goals and constraints
```

Short form:

```text
systems select actions by learned intervention-conditioned causal effects,
not by semantic labels, passive correlations, evaluator metrics, or trace-only explanations.
```

## Core Mechanisms That Remain Plausible

1. Intervention-grounded causal learning

The system must learn from its own interventions. Passive observation can inform priors, but it cannot be treated as proof of own-action causality.

2. Counterfactual query

The model must support queries of the form:

```text
What would happen if I did action A instead of action B in this context?
```

Without counterfactual action queries, the system is only predicting, not controlling.

3. Action selection by predicted causal effect

Action distributions must change when learned effects change and remain stable when labels change but effects stay fixed.

4. Model revision under mismatch

Prediction error must reduce confidence, trigger re-identification when needed, and preserve recoverable context-specific knowledge when older contexts return.

5. Goal/constraint-conditioned planning

The causal model and the goal must be separable:

```text
world model = what can happen
goal / constraint vector = what should be preferred
policy = effect-conditioned choice under current goal and constraints
```

6. Anti-shortcut validation

Every positive claim must survive gates that block action-label lookup, static safety tables, scenario IDs, semantic goal names, evaluator metric leakage, hidden transition tables, trace-only explanations, and score-only causality.

## LCC Reframed

LCC should now be treated as:

```text
LCC Gates = anti-shortcut operational validation protocol for learned causal model-based control
```

LCC should not be treated as:

```text
an independent bottom theory
a general agent architecture
an EGO migration path
a proof of AGI, consciousness, self-awareness, life, or robust universal support
```

## Required Validation Gates For Any Future Implementation

Any future causal model-based control implementation contract must predeclare at least:

```text
label/effect decoupling
passive observation vs own intervention split
active diagnostic intervention
sequential closed-loop replanning
nonstationary effect revision
representation-grounded counterfactual control
relational and compositional transfer
goal-conditioned model reuse
candidate freeze before blind holdout generation
independent trace-only scoring
strong baseline equivalence checks
negative controls for false confidence
```

## Known

```text
VCCO / VCAC / FOPC were rejected or downgraded through redteam.
LCC survived Cycle 000-010 as bounded evidence.
Independent clean-room bounded replication passed.
Cross-theory tournament returned lcc_collapses_into_causal_model_based_control.
T3_CausalModelBasedControl matched LCC with max_metric_abs_diff = 0.0.
Shared redteam gates passed.
Independent scoring matched.
Replication was stable.
```

## Reasonable Inference

```text
LCC is best retained as operational evidence discipline.
Causal model-based control is the current strongest surviving theory family.
Future work should test indispensable mechanisms inside learned causal model-based control,
not continue LCC as a protected label.
```

## Unknown

```text
Whether causal model-based control is sufficient for broader intelligence.
Whether active inference, empowerment, predictive processing, or model-based RL
become equivalent to causal model-based control at larger scales.
Whether real embodied systems can learn robust enough causal models under resource limits.
Which components remain indispensable outside the current bounded tournament.
```

## Cannot Prove

This principle does not prove:

```text
bottom intelligence principle
AGI
consciousness
subjective experience
self-awareness
life
EGO readiness
robust universal mechanism support
```

## Authorization Boundary

This document is a theory closeout and principle ledger only. It does not authorize implementation, Cycle 011, a general LCC agent, autonomous theory search, EGO migration, or any renamed continuation of LCC without a new human-reviewed contract.

