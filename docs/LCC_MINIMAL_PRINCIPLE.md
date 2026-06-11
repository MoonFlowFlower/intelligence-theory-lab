# LCC Minimal Principle Review

Milestone 001 compresses LCC_v0 into the smallest statement that still matches the surviving bounded evidence.

## Minimal Principle

Intelligence-relevant control is learned counterfactual effect control: actions are selected by intervention-grounded predictions that remain label-invariant and change under effect perturbations.

## Necessary Terms

| Term | Why It Remains |
| --- | --- |
| Learned | Cycle 001 and later gates reject explicit effect tables as the main candidate path. |
| Counterfactual effect | The core split is label-invariant behavior when effects stay fixed, and behavior change when effects change. |
| Intervention-grounded | Cycle 002 and Cycle 003 reject passive correlation as enough. |
| Control | The evidence must affect action distribution, not only metrics, trace labels, or scores. |
| Label-invariant | This is the direct constraint inherited from the FOPC failure. |

## Stress Dimensions, Not Core Terms

The following dimensions strengthen the evidence but are not currently part of the minimal one-sentence principle:

- Sequential planning.
- Nonstationary revision.
- Raw or aliased representation grounding.
- Relational composition.
- Goal-conditioned reuse.
- Blind holdout replication.

They are important because they make shortcut explanations harder, not because each is a separate primitive in the theory.

## Implementation Details To Exclude From Theory

- Cycle-specific runners.
- Fixed action counts or vector dimensions.
- Toy-world names and scenario layouts.
- Artifact schemas.
- Baseline labels.
- Threshold values.
- Trace field names.
- Any explicit contract recipe.

## Deletion Tests

LCC_v0 should be closed or revised if any future independently authored test shows:

- Action labels can explain the behavior.
- Effect perturbation does not change the action distribution.
- Passive correlation is treated as own-intervention effect.
- Behavior-only replay cannot reconstruct decision evidence.
- A strong generic baseline matches the candidate under the same observation restrictions.
- Independent reimplementation cannot reproduce the key label/effect and intervention/effect splits.

## Current Boundary

This principle is a candidate compression of bounded evidence, not theory support. It does not prove intelligence, AGI, consciousness, subjective experience, self-awareness, life, robust universal support, or EGO readiness.
