# Risk Register 005

| Risk | Contract stance | Stop / mitigation |
| --- | --- | --- |
| 7 fixed actions become 20 fixed actions | forbidden | stop on `ACTION_HANDLES = 20` or fixed recipe tables |
| semantic action family leaks into selector | forbidden | stop on `semantic_action_family` or action family names |
| natural language option descriptions steer selector | forbidden | selector schema excludes descriptions |
| renderer controls selected action | forbidden | renderer adapter is strictly post-selection |
| thresholds are retuned after seeing results | forbidden | stop with `boundary_violation` |
| RAG baseline is weakened | forbidden | stop with `baseline_contract_incomplete` or `boundary_violation` |
| oracle effects enter CandidateOption | forbidden | predicted effects must be learned or derived from allowed experience |
| 003 evidence is rewritten | forbidden | preserve as small-action-set evidence only |
| replay hides option pruning | open | future traces must include full option list and distribution |
| baselines receive weaker input than candidate | open | all baselines receive the same anonymous options |
| N=7 shadow compatibility fails | open | report `shadow_adapter_invalid`, do not patch selector |
| N>=20 execution collapses | open | report future execution failure, do not retune thresholds |
