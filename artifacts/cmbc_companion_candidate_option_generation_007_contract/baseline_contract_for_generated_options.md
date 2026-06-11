# Baseline Contract For Generated Options

RAG / heuristic / generator baselines receive equivalent allowed inputs.

Future baselines must receive the same admitted anonymous option list as CMBC, plus only the public inputs allowed by the 005 and 006 contracts.

Required future baselines:

- `RAGSummaryMemoryBaseline`
- `StrongHumanLikeHeuristicBaseline`
- `ExpandedActionNearestNeighborBaseline`
- `GeneratorProposalBaseline`

The generator baseline may score proposals as a challenger, but it cannot be used as CMBC's selector and cannot receive privileged labels or hidden target outputs.
