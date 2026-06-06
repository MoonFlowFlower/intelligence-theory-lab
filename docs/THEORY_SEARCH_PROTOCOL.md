# Theory Search Protocol

## Purpose

This lab exists to run bounded falsifiable theory-evolution cycles. It does not exist to keep theories alive until they pass.

## Cycle Contract

Each cycle must stop after one candidate theory and one closeout verdict.

Allowed verdicts:

```text
failed
reduced
superseded
supported_bounded
inconclusive
```

## Required Cycle Order

```text
1. Write theory card.
2. Write experiment contract.
3. Declare kill tests and stop conditions.
4. Review prior failed claims and successor constraints.
5. Implement only the minimum testbed authorized by the contract.
6. Add strong baselines before claiming candidate support.
7. Run redteam gates.
8. Preserve negative evidence.
9. Close, reduce, or supersede the theory.
10. Produce a human review packet.
```

## Non-Negotiable Rules

```text
No theory card -> no code.
No experiment contract -> no experiment.
No kill tests -> no implementation.
No strong baseline -> no support claim.
No negative evidence update -> no successor.
No human review -> no next cycle.
```

## Theory Mutation Rule

A successor theory must:

```text
explain predecessor failure
delete or replace at least one failed component
introduce a stronger kill test
avoid previously detected shortcuts
state the fastest way it can be killed
```

