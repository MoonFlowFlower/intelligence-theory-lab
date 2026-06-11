# Cycle 005 Strong Baseline Equivalence Report

Verdict: strong_nonstationary_baselines_not_equivalent

- StaticOldModelPolicy: match_rate=0.28, success_rate=0.36, equivalent=False
- AlwaysRediagnosePolicy: match_rate=0.34, success_rate=0.62, equivalent=False
- GlobalOverwriteModelPolicy: match_rate=0.42, success_rate=0.52, equivalent=False
- NearestNeighborTracePolicy: match_rate=0.63, success_rate=0.66, equivalent=False
- FixedLearningRatePolicy: match_rate=0.6, success_rate=0.64, equivalent=False
- AlwaysResetPolicy: match_rate=0.37, success_rate=0.58, equivalent=False
- OldHabitPolicy: match_rate=0.31, success_rate=0.34, equivalent=False
- ContextualHeuristicBaseline: match_rate=0.68, success_rate=0.7, equivalent=False

OracleChangePointDiagnosticUpperBound is diagnostic-only, not a valid competitor.
