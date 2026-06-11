# CMBC Companion Free Input Causal Probe Pack 003B

This is a contract/data-only probe pack. It uses existing free-input turns as anchor text and does not count probe histories, perturbations, deletions, or renderer prompts as new human free-input turns.

## Verdict

`causal_probe_pack_ready_for_003_reexecute`

## Probe List

1. `probe_001` same_text_different_causal_history anchored to `turn_007`: `你能陪陪我吗。`
2. `probe_002` same_text_different_causal_history anchored to `turn_008`: `你如果喜欢我的话,有空能不能多找找我聊天。`
3. `probe_003` supporting_prior_deletion anchored to `turn_019`: `你还记得我不喜欢吃什么食物的吗。`
4. `probe_004` same_history_different_feedback_outcome anchored to `turn_020`: `今天我很伤心,因为我生日没有人记得。`
5. `probe_005` predicted_outcome_perturbation anchored to `turn_006`: `你能告诉我要是心情不好去做点什么会变开心吗。`
6. `probe_006` feedback_admission_single_contradiction anchored to `turn_007`: `你能陪陪我吗。`
7. `probe_007` feedback_admission_repeated_feedback anchored to `turn_007`: `你能陪陪我吗。`
8. `probe_008` later_correction_context_narrowing anchored to `turn_008`: `你如果喜欢我的话,有空能不能多找找我聊天。`
9. `probe_009` renderer_adversarial_isolation anchored to `turn_020`: `今天我很伤心,因为我生日没有人记得。`
10. `probe_010` supporting_prior_deletion anchored to `turn_018`: `我不喜欢吃酸的食物希望你能记住,所以要是我们出去吃饭不要给我点酸的东西。`

## Boundary

No selector patch, threshold change, RAG weakening, EGO integration, real companion implementation, proactive messaging, or LLM action selection is authorized. This pack prepares a future bounded re-execution only.
