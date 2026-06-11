# Cycle 008 Strong Baseline Equivalence Report

Verdict: strong_goal_conditioned_baselines_not_equivalent

- SingleGoalPolicy: match_rate=0.33, success_rate=0.42, equivalent=False
- TaskLabelPolicy: match_rate=0.25, success_rate=0.35, equivalent=False
- GoalLookupTablePolicy: match_rate=0.5, success_rate=0.54, equivalent=False
- NearestNeighborTaskPolicy: match_rate=0.58, success_rate=0.57, equivalent=False
- FixedConstraintPolicy: match_rate=0.5, success_rate=0.52, equivalent=False
- StaticSafetyTableBaseline: match_rate=0.58, success_rate=0.56, equivalent=False
- DominantGoalPolicy: match_rate=0.45, success_rate=0.5, equivalent=False
- FixedPriorityPolicy: match_rate=0.38, success_rate=0.44, equivalent=False
- RewardTablePolicy: match_rate=0.5, success_rate=0.52, equivalent=False
- TaskSpecificPolicy: match_rate=0.54, success_rate=0.54, equivalent=False

OracleGoalPlannerDiagnosticUpperBound is diagnostic-only, not a valid competitor.
