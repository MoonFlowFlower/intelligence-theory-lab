# LCC Public Theory Card

Theory ID: `LCC_v0`

Name: Learned Counterfactual Controllability

Status: bounded evidence candidate only.

## Minimal Principle

Intelligence-relevant control is learned counterfactual effect control: actions are selected by intervention-grounded predictions that remain label-invariant and change under effect perturbations.

## Core Requirements

An LCC candidate must show all of the following:

- Actions are selected from learned intervention-conditioned effect predictions.
- Renaming action labels does not change behavior when effects and observations stay fixed.
- Swapping action effects changes behavior when labels and observations stay fixed.
- Passive observation is not treated as own-intervention evidence.
- Perturbing the learned effect model changes the action distribution.
- Behavior-only replay can reconstruct prediction-before-action decision evidence.
- Strong non-oracle baselines do not match the candidate under the same observation restrictions.

## Public Mechanism Claim

LCC claims only this bounded mechanism pattern:

The candidate uses past own-intervention outcomes to learn counterfactual action effects, then selects anonymous actions by predicted effects under current observations, goals, constraints, horizon, and budget.

## Required Non-Claims

This card does not claim:

- LCC theory support.
- A bottom intelligence principle.
- General intelligence.
- Consciousness.
- Subjective experience.
- Self-awareness.
- Life.
- EGO readiness.
- Robust universal support.
- Authorization to implement a general LCC agent.

## Prior Negative Evidence Constraints

The public theory must preserve constraints from VCCO / VCAC / FOPC:

- Trace-visible variables are not control-loop components unless perturbing them changes action distribution.
- Score-only causality is insufficient.
- No-op ablations cannot count as component necessity.
- Future-option proxies must not reduce to action labels or static safety tables.
- Evaluator metrics cannot be reused as candidate features.

## Candidate Closure Conditions

Close or revise LCC_v0 if any independent test finds:

- Action labels explain behavior.
- Effect perturbation does not change action distribution.
- Passive correlation is mistaken for own-intervention effect.
- Behavior-only replay fails.
- A strong baseline matches the candidate.
- Independent reimplementation cannot reproduce the core label/effect and intervention/effect splits.

Failure must be recorded as evidence, not patched away.
