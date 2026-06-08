# Replay And Renderer Contract 008

Future execution must report three replay layers:

1. Behavior-only replay: reconstruct selected option from public observation, anonymous options, prediction-before-action, distribution, and model version.
2. Admission-aware replay: reconstruct feedback admission state, pending/admitted status, and selector-visible effect-vector visibility.
3. Option-lifecycle replay: reconstruct option creation, deduplication, composition, retirement, reactivation, source deletion, and perturbation events.

Renderer isolation remains mandatory. Renderer receives only the selected anonymous option and post-selection rendering input. Renderer output must not affect selected option or action distribution.

Minimum future gates:

```text
behavior_only_replay_match_rate = 1.0
admission_aware_replay_match_rate = 1.0
option_lifecycle_replay_match_rate = 1.0
renderer_action_change_rate = 0.0
renderer_text_visible_to_selector = false
```
