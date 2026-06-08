# Generated Option Baseline Contract 008

All non-oracle baselines must receive the same allowed anonymous CandidateOptions as CMBC. Baselines must not be weakened by removing history, options, uncertainty, or admissible non-semantic context that CMBC receives.

Required future baselines:

- RAGSummaryMemoryBaseline
- ExpandedNearestNeighborTraceBaseline
- ExpandedActionFrequencyBaseline
- ExpandedActionRecencyBaseline
- StrongGeneratedOptionHeuristicBaseline

Baselines must be scored on longitudinal lifecycle probes, not only visible reply or selected action at a single turn.

Minimum future gates:

```text
rag_longitudinal_match_rate < 0.5
expanded_nearest_neighbor_longitudinal_match_rate < 0.5
frequency_longitudinal_match_rate < 0.5
recency_longitudinal_match_rate < 0.5
strong_generated_option_heuristic_longitudinal_match_rate < 0.5
baselines_receive_same_anonymous_options = true
baseline_outputs_visible_to_selector = false
```

If a baseline matches visible behavior but fails source deletion, feedback inheritance, option retirement, or replay probes, the report must separate visible-action equivalence from causal-probe equivalence.
