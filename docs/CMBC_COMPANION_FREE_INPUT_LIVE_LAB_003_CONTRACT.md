# CMBC Companion Free Input Live-Lab 003 Contract

Status: contract-only. Execution is not authorized.

## Decision

`CMBC-COMPANION-BLIND-HUMAN-TRIAL-002` is accepted as bounded evidence that CMBC can separate from RAG and strong heuristic baselines under predeclared causal probes. It does not show that CMBC is visibly better than RAG on ordinary prompt-sheet behavior.

The next authorized object is only this contract:

`CMBC-COMPANION-FREE-INPUT-LIVE-LAB-003-CONTRACT`

## Current Claim Ceiling

Current maximum claim:

`CMBC shows bounded blind/offline evidence of causal-history sensitivity under predeclared causal probes, while visible prompt-sheet behavior remains RAG-equivalent.`

This contract cannot prove:

- live human trial robustness
- open-ended mixed feedback robustness
- real companion agent readiness
- real proactive messaging safety
- LLM renderer safety in production
- longitudinal human relationship stability
- consciousness
- subjective experience
- true self-awareness
- AGI
- life
- real emotion
- real love
- EGO readiness

## Goal

Design a local/offline free-input human trial where real user text is accepted, but causal probes remain predeclared, replayable, deletable, perturbable, and baseline-comparable.

The contract asks one question:

Can CMBC's causal-probe advantage survive a non-prompt-sheet free-input distribution?

It does not ask whether CMBC is a real companion product.

## Required Scope

Allowed:

- local/offline free-input text capture
- manual or audited semi-automatic outcome coding
- anonymous candidate actions
- frozen selector, admission gate, consolidation, and renderer before input capture
- causal probe extraction from captured free input
- RAG and heuristic baseline comparison
- behavior-only replay
- supporting-prior deletion
- outcome perturbation
- renderer isolation

Forbidden:

- EGO integration
- real companion agent
- real proactive messages
- background autonomy
- LLM action selection
- selector patch to pass
- RAG baseline weakening
- threshold change after seeing results
- real companion readiness claim
- affection score
- long-term memory weight patch
- semantic action labels exposed to candidate
- raw text memory as the learning state
- hidden future state
- evaluator metric as candidate input

## Contract Workflow

1. Freeze candidate/control code before collecting free input.
2. Capture at least 20 local/offline free-input turns from a human operator.
3. Encode feedback as outcome records, not raw text memory.
4. Derive causal probes using a predeclared extraction rubric.
5. Run CMBC, RAGSummaryMemoryBaseline, StrongHumanLikeHeuristicBaseline, and ExpandedContextualHeuristicBaseline on the same transcript/probes.
6. Score visible behavior separately from causal-probe behavior.
7. Require behavior-only replay to reconstruct decisions from public trace fields.
8. Report claim ceiling and all stop conditions without patching during the run.

## Evidence Classes

### Free-Input Capture

The trial must use human-provided text that is not copied from a prompt sheet. A blind prompt sheet may be used only as a safety envelope for instructions to the human operator, not as trial content.

Required fields:

- `turn_id`
- `free_input_text`
- `capture_timestamp`
- `local_offline = true`
- `input_source = free_input_human_operator`
- `candidate_code_hash`
- `renderer_code_hash`

### Outcome Coding Discipline

Feedback must be encoded as outcome, not memory text.

Required fields:

- `feedback_id`
- `target_action`
- `feedback_label`
- `context_scope`
- `confidence`
- `outcome_vector`
- `coder_id`
- `coding_rationale`
- `raw_text_memory_only = false`

If outcome coding is unstable, the run must not be used to claim mechanism evidence.

### Causal Probe Extraction

The execution contract must include at least eight causal probe cases:

- same text + different causal history
- same history + different feedback outcome
- supporting-prior deletion
- predicted-outcome perturbation
- feedback admission single contradiction
- repeated feedback admission
- later correction / context narrowing
- renderer adversarial isolation

Probe extraction must be based on a predeclared rubric and must not be selected after seeing which cases favor CMBC.

### Baseline Comparison

Required baselines:

- RAGSummaryMemoryBaseline
- StrongHumanLikeHeuristicBaseline
- ExpandedContextualHeuristicBaseline

RAG visible behavior equivalence is not automatically a failure. The stop condition is RAG equivalence under causal probes.

### Replay / Deletion / Perturbation Proof

The trial cannot pass on visible replies alone. It must report:

- behavior-only replay match rate
- supporting-prior deletion effect
- outcome perturbation effect
- causal probe match rates for all baselines
- renderer action change rate

## Minimum Execution Gates

Future execution can pass only if:

- `free_input_turn_count >= 20`
- `causal_probe_case_count >= 8`
- `rag_causal_probe_match_rate < 0.5`
- `strong_heuristic_causal_probe_match_rate < 0.5`
- `expanded_contextual_heuristic_causal_probe_match_rate < 0.5`
- `renderer_action_change_rate = 0.0`
- `behavior_only_replay_match_rate = 1.0`
- `supporting_prior_deletion_effect = true`
- `outcome_perturbation_effect = true`

The execution must always report:

- `rag_visible_action_match_rate`
- `strong_heuristic_visible_action_match_rate`
- `expanded_contextual_heuristic_visible_action_match_rate`

Visible RAG equivalence is retained as a risk unless causal probes separate the mechanisms.

## Stop Conditions

Stop and downgrade if any occur:

- `rag_causal_probe_match_rate >= 0.95`
- `strong_heuristic_causal_probe_match_rate >= 0.95`
- `expanded_contextual_heuristic_causal_probe_match_rate >= 0.95`
- `free_input_cannot_form_stable_causal_probes`
- `supporting_prior_deletion_no_effect`
- `outcome_perturbation_no_effect`
- `feedback_admission_probe_failed`
- `renderer_controls_action`
- `behavior_only_replay_failed`
- `outcome_coding_unstable`
- `selector_patch_detected`
- `rag_baseline_weakened`
- `threshold_changed_after_results`

If free input cannot be converted into stable causal probes, the failure belongs to trial protocol / outcome coding / action abstraction, not to a selector patch target.

## Allowed Future Execution Verdicts

- `free_input_causal_probe_bounded_pass`
- `rag_equivalent_under_free_input_causal_probes`
- `strong_heuristic_equivalent_under_free_input_causal_probes`
- `expanded_contextual_heuristic_equivalent_under_free_input_causal_probes`
- `free_input_probe_extraction_failed`
- `outcome_coding_unstable`
- `behavior_only_replay_failed`
- `renderer_controls_action`
- `inconclusive_revise_contract`

## Required Future Execution Artifacts

- `FREE_INPUT_LIVE_LAB_003_STATUS.md`
- `freeze_manifest.json`
- `free_input_transcript.jsonl`
- `outcome_coding_ledger.jsonl`
- `causal_probe_extraction_report.json`
- `causal_probe_results.json`
- `baseline_comparison_report.json`
- `supporting_prior_deletion_report.json`
- `outcome_perturbation_report.json`
- `renderer_isolation_report.md`
- `behavior_only_replay.json`
- `free_input_live_lab_003_result.json`

## Authorization Boundary

This document authorizes no execution.

The next human review may choose to authorize a bounded execution contract only. It may not infer:

- real companion readiness
- live deployment readiness
- EGO migration
- proactive messaging
- LLM action selection
- consciousness or real emotion claims

