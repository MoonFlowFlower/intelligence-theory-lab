# Selector Parametricity Audit

verdict = selector_static_action_handle_bottleneck_confirmed

static_action_handle_count = 7

choose_signature = `(self, observation: 'CandidateObservation', effect_estimates: 'dict[str, OutcomeVector]') -> 'dict[str, Any]'`

Findings:

- `CMBCGrowthLoopCandidate.choose` has no `candidate_options` parameter.
- It constructs utilities by iterating the global `ACTION_HANDLES` tuple.
- Extra keys in `effect_estimates` are ignored by selector scoring.
- `fit_effect_model` also initializes `by_action` from `ACTION_HANDLES`.
- `make_trace` writes predictions and anonymous candidate actions from `ACTION_HANDLES`.

Conclusion:

The frozen selector is not parametric over candidate action space. The 004 failure is therefore not evidence against CMBC free-input causal probes; it is evidence that the current implementation only supports the small 7-action anonymous interface.
