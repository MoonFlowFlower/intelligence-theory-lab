# Cycle 004 Strong Baseline Equivalence Report

Verdict: strong_sequence_baselines_not_equivalent

- OneStepGreedyPolicy: match_rate=0.28, success_rate=0.42, equivalent=False
- OpenLoopSequencePolicy: match_rate=0.36, success_rate=0.48, equivalent=False
- SequenceLookupTablePolicy: match_rate=0.55, success_rate=0.58, equivalent=False
- NearestNeighborSequencePolicy: match_rate=0.62, success_rate=0.64, equivalent=False
- ContextualHeuristicBaseline: match_rate=0.66, success_rate=0.7, equivalent=False
- StaticTrapAvoidanceTableBaseline: match_rate=0.59, success_rate=0.66, equivalent=False

OraclePlannerDiagnosticUpperBound is diagnostic-only, not a valid competitor.
