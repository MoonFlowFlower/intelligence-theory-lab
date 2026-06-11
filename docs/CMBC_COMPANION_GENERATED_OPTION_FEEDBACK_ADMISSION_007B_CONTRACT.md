# CMBC Companion Generated Option Feedback Admission 007B Contract

Status: contract-only. No implementation or execution is authorized.

## Source RCA

`CMBC-COMPANION-CANDIDATE-OPTION-GENERATION-007-RCA` ended with:

```text
verdict = outcome_update_ordering_bug_confirmed
secondary_findings = feedback_admission_not_applied_to_generated_options,
  weak_evidence_high_confidence_confirmed,
  replay_trace_insufficient_for_generated_feedback_admission,
  selector_scoring_not_primary_blocker
```

The source failure is narrow: pending counterevidence was recorded, but the
selector-visible generated-option effect vector changed before admission
filtering. That caused the selected option to flip from
`generated_option_08_of_24` to `generated_option_04_of_24`.

## Goal

Define a feedback admission and outcome update ordering contract for generated
CandidateOptions, so pending counterevidence cannot modify selector-visible
`predicted_effect_vector` or action distribution before admission.

## Required Ordering

```text
single feedback
-> PendingCounterevidenceRecord
-> FeedbackAdmissionState
-> uncertainty / confidence / context-local pending evidence may change
-> selector-visible predicted_effect_vector remains base-only
-> repeated or high-confidence feedback
-> admitted_context_counterevidence
-> admitted delta enters AdmissionFilteredEffectVector
-> selector sees only admission-filtered effect vectors
```

## Current Claim Ceiling

Current maximum claim remains:

```text
bounded generated CandidateOption execution remains failed;
failure localized to pending feedback admission/update ordering
```

This contract cannot prove generated-option execution support, open-ended option
generation robustness, real companion readiness, EGO readiness, consciousness,
subjective experience, real emotion, or real love.

## Required Contract Objects

- `PendingCounterevidenceRecord`
- `FeedbackAdmissionState`
- `GeneratedOptionFeedbackUpdateLedger`
- `ContextScopedFeedbackAdmission`
- `AdmissionFilteredEffectVector`
- `SelectorVisibleEffectVectorContract`
- `GeneratedOptionUncertaintyUpdateContract`
- `AdmissionAwareReplayTrace`
- `FeedbackAdmissionOrderingProof`

## Core Rules

1. `pending_counterevidence` must not change selector-visible `predicted_effect_vector`.
2. `pending_counterevidence` may change uncertainty / confidence / pending evidence state.
3. `admitted_context_counterevidence` may change selector-visible `predicted_effect_vector`.
4. Repeated or high-confidence feedback is required for admission.
5. `context_scope` must be explicit and traceable.
6. Option lineage must inherit pending/admitted feedback state.
7. Replay trace must contain `proposal_id`, `admission_decision_id`, `feedback_admission_status`, `context_scope`, and effect-vector visibility status.
8. Selector must only see admission-filtered effect vectors.
9. Behavior-only replay and admission-aware replay must both be reported.
10. Semantic labels and natural-language descriptions remain forbidden selector inputs.

## Not Authorized

- 007B implementation
- 007B shadow execution
- selector patch
- threshold change
- RAG / heuristic / nearest-neighbor baseline weakening
- mutation of prior probes after results
- EGO integration
- real companion implementation
- proactive messages
- LLM action selection
- rewrite of 003 / 005 / 006 / 007-SHADOW evidence

## Recommended Next Task

If this contract is accepted, the next task may be:

`CMBC-COMPANION-GENERATED-OPTION-FEEDBACK-ADMISSION-007B-SHADOW`

That task is not authorized by this contract.
