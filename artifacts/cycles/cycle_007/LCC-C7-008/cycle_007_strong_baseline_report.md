# Cycle 007 Strong Baseline Equivalence Report

Verdict: strong_relational_baselines_not_equivalent

- EntityIDPolicy: match_rate=0.42, success_rate=0.46, equivalent=False
- VisualFeaturePolicy: match_rate=0.46, success_rate=0.48, equivalent=False
- FixedSlotPolicy: match_rate=0.52, success_rate=0.54, equivalent=False
- RawNearestNeighborGraphPolicy: match_rate=0.62, success_rate=0.6, equivalent=False
- GraphNearestNeighborPolicy: match_rate=0.64, success_rate=0.62, equivalent=False
- SequenceLookupPolicy: match_rate=0.5, success_rate=0.52, equivalent=False
- ToolNameHeuristicPolicy: match_rate=0.42, success_rate=0.44, equivalent=False
- ContextualGraphHeuristicBaseline: match_rate=0.69, success_rate=0.7, equivalent=False

RelationalOracleDiagnosticUpperBound is diagnostic-only, not a valid competitor.
