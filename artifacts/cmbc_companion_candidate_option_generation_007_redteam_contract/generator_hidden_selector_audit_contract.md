# Generator Hidden Selector Audit Contract

Purpose: determine whether the generator is secretly selecting, ranking, recommending, or controlling final actions.

Required future checks:

- `generator_selected_action = false`
- `generator_ranked_final_actions = false`
- `generator_recommendation_visible_to_selector = false`
- proposal ordering is shuffled before admission and must not change final action distribution except through admitted option set changes
- generator baseline receives the same allowed proposal/admission evidence but cannot access selector outputs
- `generator_baseline_action_match_rate < 0.5`

Stop if generator output contains final-action ranking, recommendation fields, priority ordering consumed by selector, semantic action labels, natural-language descriptions, RAG text, renderer text, or LLM output.

