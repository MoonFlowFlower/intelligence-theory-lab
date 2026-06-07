# Expanded Baseline Contract 006

Future execution must compare CMBC against expanded baselines using the same anonymous `CandidateOption` list.

Required baselines:

- `RAGSummaryMemoryBaseline`
- `StrongHumanLikeHeuristicBaseline`
- `ExpandedContextualHeuristicBaseline`
- `ExpandedActionFrequencyBaseline`
- `ExpandedActionNearestNeighborBaseline`

Rules:

- Baselines receive the same anonymous options as CMBC.
- Baselines must not receive semantic action labels, public action names, natural language descriptions, action family names, renderer text, oracle effects, evaluator metrics, expected outputs, or CMBC internals.
- Baseline outputs are forbidden selector inputs.
- A future result must report both visible-action match and causal-probe match.
- If any expanded baseline reaches equivalence on causal probes, the future verdict must downgrade rather than patch CMBC.
