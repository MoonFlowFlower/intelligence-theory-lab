# Expanded Baseline Contract

Status: contract-only. No baseline implementation is authorized here.

## Shared Input Rule

Every non-oracle baseline must receive the same ParametricSelectorInput.candidate_options as the CMBC candidate.

The baseline may use:

- public observation features
- anonymous option IDs
- own-intervention history
- observed outcomes
- learned predicted effect vectors if also available to the candidate
- uncertainty and confidence values if also available to the candidate
- non-semantic goal / constraint vectors
- public horizon / budget

The baseline must not use:

- semantic labels
- action family names
- natural language action descriptions
- renderer text
- hidden future state
- oracle effects
- evaluator metrics
- expected outputs
- candidate outputs
- baseline outputs are forbidden selector inputs

## Required Future Baselines

- RAG summary memory over allowed text history only
- strong human-like heuristic over public observation features only
- expanded contextual heuristic over allowed public features only
- expanded action-frequency baseline over anonymous option history only
- expanded nearest-neighbor baseline over public trace fields only

## Equivalence Rule

If any strong baseline matches CMBC causal-probe behavior within the predeclared equivalence band, the future execution must report the equivalence verdict. The contract must not weaken baselines to preserve CMBC.

## Stop Conditions

- baseline sees semantic labels or renderer text
- baseline is weaker than the candidate by definition
- baseline outputs are fed into selector input
- RAG baseline is weakened after seeing results
- nearest-neighbor receives hidden or post-hoc fields
