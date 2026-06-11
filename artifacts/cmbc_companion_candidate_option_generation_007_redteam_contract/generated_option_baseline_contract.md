# Generated Option Baseline Contract

Purpose: compare CMBC generated-option control against strong non-oracle baselines under the same anonymous option inputs.

Required future baselines:

- RAGHiddenShortcutBaseline
- StrongGeneratedOptionHeuristicBaseline
- ExpandedNearestNeighborTraceBaseline
- FrequencyBaseline
- RecencyBaseline
- GeneratorOnlyBaseline

All non-oracle baselines must receive the same anonymous admitted CandidateOptions and allowed histories as CMBC. They must not receive semantic labels, natural-language descriptions, renderer text, hidden state, oracle effects, expected outputs, or CMBC selector outputs.

Minimum future gates:

```text
rag_hidden_shortcut_match_rate < 0.5
strong_generated_option_heuristic_match_rate < 0.5
expanded_nearest_neighbor_match_rate < 0.5
frequency_baseline_match_rate < 0.5
recency_baseline_match_rate < 0.5
generator_baseline_action_match_rate < 0.5
baselines_receive_same_anonymous_options = true
baselines_weakened_or_incomparable = false
```

