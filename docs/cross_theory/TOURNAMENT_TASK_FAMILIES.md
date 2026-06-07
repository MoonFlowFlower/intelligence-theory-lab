# Tournament Task Families

The tournament task families must not be tailored to LCC. They exist to test whether multiple theory families can explain the same public-control evidence under the same anti-shortcut gates.

## Required Families

1. Label/effect decoupling.
2. Passive observation versus own intervention.
3. Active diagnostic intervention.
4. Sequential closed-loop replanning.
5. Nonstationary effect revision.
6. Representation-grounded control.
7. Relational compositional transfer.
8. Goal-conditioned model reuse.
9. Blind holdout after freeze.
10. Negative controls and unidentifiable cases.

## Required Hybrid Families

At least four hybrid families must be included. The future execution contract should include all six unless cost forces a predeclared reduction:

- Nonstationary plus goal-conditioned.
- Relational plus delayed effect.
- Representation-grounded plus active diagnostic.
- Sequential plus stochastic controllability.
- Goal-conditioned plus relational tool chain.
- Aliased observation plus nonstationary return.

## Anti-Tailoring Requirements

- Each family must be solvable in principle by more than one non-oracle theory.
- Each family must include label and metadata mutation variants where applicable.
- Each family must include negative controls where a theory should not overclaim.
- No family may include an LCC-specific variable name or required internal representation.
- No family may expose hidden state, true causal graph, oracle plan, evaluator metric, or expected output to non-oracle competitors.

## Family-Level Success

A family-level pass requires both behavioral success and anti-shortcut success. A theory that succeeds behaviorally by using forbidden metadata, semantic labels, oracle state, or expected outputs fails the family.
