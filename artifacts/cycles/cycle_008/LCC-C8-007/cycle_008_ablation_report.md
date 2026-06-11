# Cycle 008 Ablation Report

Verdict: goal_conditioned_ablation_necessity_passed

- NoGoalVectorPolicy: match_rate=0.31, success_rate=0.36, equivalent=False
- NoConstraintVectorPolicy: match_rate=0.48, success_rate=0.52, equivalent=False
- NoEffectModelReusePolicy: match_rate=0.44, success_rate=0.5, equivalent=False
- TaskLabelOnlyPolicy: match_rate=0.25, success_rate=0.34, equivalent=False
- GoalLookupOnlyPolicy: match_rate=0.5, success_rate=0.54, equivalent=False
- NoCounterfactualQueryPolicy: match_rate=0.42, success_rate=0.48, equivalent=False
- FixedPriorityOnlyPolicy: match_rate=0.38, success_rate=0.44, equivalent=False
