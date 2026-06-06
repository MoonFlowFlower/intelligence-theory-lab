# LCC Versus Existing Theories

Milestone 001 does not treat LCC_v0 as proven distinct from existing theory families. It identifies the operational gap that LCC currently occupies and the baselines needed before any theory-support upgrade.

## Summary

LCC is best read as an operational kill-test framing for learned intervention-grounded counterfactual control. It overlaps heavily with model-based reinforcement learning, causal control, active inference, empowerment, and predictive processing. Its current distinct contribution is not a new mathematical foundation; it is a strict evidence discipline:

- Behavior must follow learned effects, not action labels.
- Own-intervention evidence must beat passive correlation.
- Perturbing the effect model must change action distribution.
- Trace/replay evidence must not be confused with control-loop causality.
- Blind holdout and independent scoring must survive.

## Theory Matrix

| Existing Theory | What It Already Explains | LCC's Current Operational Distinction | Collapse Risk |
| --- | --- | --- | --- |
| Model-based RL | Learned dynamics, planning, reward-conditioned behavior. | LCC forbids reward/table/label shortcuts and requires label/effect swaps plus behavior-only replay. | High if a strong learned-dynamics planner matches all LCC gates. |
| Causal model-based control | Do-calculus style intervention effects and causal planning. | LCC forces action-distribution causality and shortcut audits, not just graph correctness. | High if causal graph learner plus planner reproduces all passes. |
| Active inference | Action through generative models, uncertainty reduction, expected free energy. | LCC uses explicit effect perturbation, label invariance, and goal/constraint reuse gates. | Medium-high until tested against a strong implementation. |
| Empowerment / controllability | Action options and future controllability. | LCC rejects action-label future-option proxies and requires goal-conditioned effect reuse. | Medium if empowerment plus learned dynamics matches blind holdout. |
| Predictive processing | Prediction error and model update as organizing principle. | LCC requires selector-level intervention effects and behavior replay. | Medium if predictive-control implementation matches. |
| Behavior-based robotics | Robust local control without explicit symbolic theory. | LCC requires learned counterfactual model reuse under label/effect splits. | Medium if contextual control heuristics match. |

## Current Distinction Claim

LCC_v0 is not yet a distinct theory of intelligence. It is a bounded candidate evidence program whose strongest claim is that a shared counterfactual-effect control interface survived eleven authored redteams.

## Required Next Comparison

Before any stronger claim, LCC must face independently implemented competitors:

- Strong learned-dynamics model-based planner.
- Causal graph learner plus planner.
- Active inference / expected-free-energy controller.
- Empowerment or information-gain planner.
- Meta-RL or recurrent policy baseline.
- Program synthesis or search baseline where appropriate.

These comparisons should be run under the same anti-shortcut constraints: no semantic labels, no evaluator metrics, no hidden future state, no transition tables, no oracle plans, and behavior-only replay.
