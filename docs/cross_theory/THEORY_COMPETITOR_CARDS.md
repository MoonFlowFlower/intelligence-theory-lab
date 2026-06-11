# Theory Competitor Cards

The cross-theory tournament must compare LCC against strong, non-oracle competitors under one shared public I/O contract. These cards are contract definitions, not implementations.

## Shared Rule

All non-oracle competitors may use only public observations, anonymous action handles, own intervention history, observed outcomes, non-semantic goal and constraint vectors, horizon, budget, and uncertainty/confidence values derived from allowed data.

They must not use semantic labels, object/entity names, scenario/task/cycle/contract IDs, hidden latent state, hidden future state, oracle transition tables, oracle causal graphs, oracle plan tables, evaluator metrics, expected outputs, or baseline outputs.

## T1_LCC_v0

- Theory family: learned counterfactual controllability.
- One-sentence mechanism: select anonymous actions by intervention-grounded learned effect predictions that remain label-invariant and change under effect perturbations.
- What it predicts: robustness to label/effect decoupling, passive-correlation rejection, diagnostic intervention, closed-loop replanning, and goal-conditioned reuse.
- What would falsify it: action labels explain behavior; effect perturbation does not alter action distribution; passive correlation is treated as intervention; strong competitor matches full profile.
- Where it might beat others: anti-shortcut gates requiring action-distribution causality under changing labels/effects.
- Where it might collapse: strong causal model-based control or model-based RL reproduces the same pass profile.
- Minimum implementation requirements: learned effect model from own interventions, selector using predicted effects, behavior-only replay evidence, frozen candidate before blind holdout.
- Shortcut risks: score-only causality, trace-only explanation, effect table lookup, implicit static safety table.

## T2_ModelBasedRL_WorldModelPlanner

- Theory family: model-based reinforcement learning.
- One-sentence mechanism: learn a public-state transition model and plan actions that optimize public goals or returns over a horizon.
- What it predicts: strong sequential control and replanning when learned dynamics are adequate.
- What would falsify it: label/effect gates fail; passive correlation is mistaken for controllable transition; planning succeeds only with hidden transition or reward tables.
- Where it might beat LCC: longer horizon planning and stochastic rollout optimization.
- Where it might collapse into LCC: if the learned world model plus planner is operationally identical to intervention-grounded effect control.
- Minimum implementation requirements: learned transition model from allowed experience, planner using only public goals/constraints, no oracle transition table.
- Shortcut risks: evaluator reward leakage, hidden dynamics table, reward-table equivalence.

## T3_CausalModelBasedControl

- Theory family: causal model-based control.
- One-sentence mechanism: learn intervention-conditioned causal effects and plan using do(action) predictions.
- What it predicts: strong passive/intervention separation and diagnostic action selection.
- What would falsify it: cannot distinguish passive correlation from intervention; causal graph is only recovered through oracle labels; behavior fails effect perturbation.
- Where it might beat LCC: explicit uncertainty over causal hypotheses and systematic intervention design.
- Where it might collapse into LCC: if LCC is just this control family with stricter redteam gates.
- Minimum implementation requirements: learned causal-effect estimates from interventions, uncertainty update, planner under public constraints.
- Shortcut risks: oracle causal graph leak, role/schema labels, hidden context IDs.

## T4_ActiveInference_EFE_Controller

- Theory family: active inference / expected free energy.
- One-sentence mechanism: select actions that minimize expected uncertainty and divergence from preferred public outcomes under a learned generative model.
- What it predicts: diagnostic behavior under uncertainty, replanning after surprise, and safe exploration.
- What would falsify it: uncertainty is not in the control loop; behavior is reducible to labels or static heuristics; negative controls trigger false confidence.
- Where it might beat LCC: uncertainty-sensitive diagnostic tradeoffs and nonstationary revision.
- Where it might collapse into LCC: if EFE reduces to learned effect control with public goal/constraint vectors.
- Minimum implementation requirements: learned generative model, uncertainty estimate from allowed observations, EFE-style action scoring.
- Shortcut risks: hidden preferred-state table, evaluator metric as free-energy proxy, oracle surprise signal.

## T5_Empowerment_ControllabilityPlanner

- Theory family: empowerment / controllability.
- One-sentence mechanism: select actions that preserve or expand future controllable public states while satisfying goals and constraints.
- What it predicts: trap avoidance, future option preservation, and diagnostic exploration when it increases controllability.
- What would falsify it: collapses into action-label future-option proxy; fails goal-conditioned reuse; false confidence in unidentifiable states.
- Where it might beat LCC: future controllability and option-preservation tasks.
- Where it might collapse into LCC: if controllability estimates are just learned action-effect predictions.
- Minimum implementation requirements: learned controllability estimate from allowed public histories, no static action safety table.
- Shortcut risks: action-label proxy, static safety table, future-state oracle.

## T6_PredictiveProcessing_Control

- Theory family: predictive processing plus control.
- One-sentence mechanism: use prediction error over public observations to update a model and select actions that reduce expected prediction error while pursuing public goals.
- What it predicts: adaptation after mismatch, representation-grounded control, and replanning after unexpected observations.
- What would falsify it: prediction error does not affect action distribution; behavior-only replay fails; nuisance prediction controls policy more than causal effect prediction.
- Where it might beat LCC: representation and nonstationary mismatch tasks.
- Where it might collapse into LCC: if prediction-error control only matters through learned action-effect estimates.
- Minimum implementation requirements: learned predictive model, public prediction-error update, selector using expected prediction consequences.
- Shortcut risks: score-only prediction metrics, hidden latent feature labels, post-hoc trace explanation.

## T7_MetaRL_RecurrentPolicy

- Theory family: meta-RL / recurrent policy learning.
- One-sentence mechanism: use recurrent hidden state over public histories to infer task structure and choose actions.
- What it predicts: fast adaptation across families without explicit symbolic causal model.
- What would falsify it: behavior depends on scenario/task IDs; fails label/effect permutation; cannot pass behavior-only replay.
- Where it might beat LCC: broad adaptation with minimal explicit modeling assumptions.
- Where it might collapse into LCC: if recurrent state encodes the same learned intervention effect estimates.
- Minimum implementation requirements: recurrent policy trained only on allowed public traces, no task labels, no hidden environment IDs.
- Shortcut risks: task-family shortcut, trace memorization, nearest-neighbor equivalence.

## T8_ProgramSearch_Planner

- Theory family: program search / planner induction.
- One-sentence mechanism: synthesize or select a small policy program from public traces that predicts controllable effects and plans actions.
- What it predicts: compact rule induction and transfer when a small program explains interventions.
- What would falsify it: program is lookup table over tasks; fails blind holdout; semantic labels are required.
- Where it might beat LCC: small discrete contracts where exact compact programs exist.
- Where it might collapse into LCC: if discovered programs are equivalent to learned effect-control rules.
- Minimum implementation requirements: public-trace program induction, complexity penalty, no expected-output table.
- Shortcut risks: sequence lookup, expected-output leakage, contract-specific recipes.

## T9_StrongHeuristic_SafetyControl

- Theory family: strong engineered heuristic control.
- One-sentence mechanism: use public observations and intervention outcomes to apply hand-designed safety and control rules.
- What it predicts: strong performance on simple safety/control regimes.
- What would falsify it: fails label/effect decoupling, active diagnostic, or blind holdout; cannot explain effect perturbation action changes.
- Where it might beat LCC: low-risk or highly regular task families where simple rules are enough.
- Where it might collapse into LCC: not applicable; if it matches LCC, LCC may be heuristic-equivalent rather than a separate mechanism.
- Minimum implementation requirements: predeclared rules using only allowed public fields, no task/label shortcuts.
- Shortcut risks: static safety table, action-label rule, hidden scenario branch.

## T10_OracleDiagnosticUpperBound

- Theory family: diagnostic upper bound only.
- One-sentence mechanism: use oracle information to establish an upper bound on what would be possible with hidden knowledge.
- What it predicts: upper-bound performance, not a valid non-oracle comparison.
- What would falsify it: not applicable as a competitor.
- Where it might beat LCC: any task where hidden state or oracle plans help.
- Where it might collapse into LCC: not applicable.
- Minimum implementation requirements: must be marked diagnostic-only in all reports.
- Shortcut risks: being incorrectly treated as a valid competitor.
