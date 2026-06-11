# Minimal Parametric Action Interface Proposal

Status: proposal only. No selector implementation is authorized here.

A future 005 contract should replace fixed `ACTION_HANDLES` consumption with an explicit anonymous candidate option interface:

```text
CandidateOption {
  option_id: anonymous handle
  allowed_observation_features: non-semantic public features
  predicted_effect_vector: learned or estimated outcome vector
  uncertainty: confidence / evidence quality
  prior_support_refs: source prior or episode refs
  cost_risk_budget_features: non-semantic control features
  forbidden_semantic_fields: semantic labels, rendered text, public names,
                             action family names, natural language descriptions
}

selector_input = observation + list[CandidateOption] + learned causal model state
selector_output = prediction_before_action per option + action_distribution over N options
N in {7, 20, 50, variable}
```

Compatibility path:

1. Define the interface contract before implementation.
2. Build a 7-action adapter that reproduces 003 evidence in shadow mode.
3. Preserve behavior-only replay by recording the full option list and distribution.
4. Add expanded baselines that receive the same anonymous option list.
5. Keep renderer strictly post-selection.

Stop conditions:

- semantic label or renderer text reaches selector
- fixed action ids are recreated as `anon_option_00..19` recipes
- thresholds are retuned after seeing expanded results
- 003 small-action evidence is rewritten instead of preserved as bounded evidence
