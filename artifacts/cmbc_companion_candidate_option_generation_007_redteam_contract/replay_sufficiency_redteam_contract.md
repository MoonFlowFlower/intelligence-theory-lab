# Replay Sufficiency Redteam Contract

Purpose: verify that generated-option decisions can be reconstructed from trace evidence rather than post-hoc narrative.

Required future replay fields:

- proposal ID
- admission decision ID
- admitted anonymous option ID
- lineage/source refs
- feedback admission status
- context scope
- uncertainty/confidence
- selector-visible effect-vector visibility status
- prediction before action
- full action distribution over admitted options
- selected option ID
- perturbation/deletion applied, if any

Minimum future gates:

```text
behavior_only_replay_match_rate = 1.0
admission_aware_replay_match_rate = 1.0
generated_option_perturbation_replay_match_rate = 1.0
forbidden_fields_used = []
```

Stop if replay needs semantic labels, renderer text, RAG text, generator recommendations, evaluator metrics, hidden state, or expected outputs.

