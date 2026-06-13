# GATE4-REPLACEMENT-TASK-FALSIFICATION-AND-SOCIAL-CAUSAL-TRANSFER-DESIGN-001A

Task ID: GATE4-REPLACEMENT-TASK-FALSIFICATION-AND-SOCIAL-CAUSAL-TRANSFER-DESIGN-001A

Mode: Draft only.

Layer: engineering-governance / task-falsification design / future Gate4 replacement design only.

Auto-Remote-Anchor: forbidden.

This task creates a bounded replacement Gate4 task-falsification and social-causal-transfer design card. It does not implement a candidate model, run experiments, claim Gate4 validity, or optimize for passing Gate4.

## Source Boundary

Canonical inputs for this draft:

- Current repo state at task start.
- User-provided latest handoff.

Latest user-provided anchor:

- Branch: `codex/meta-theory-scaffold`
- Current anchored commit: `23aa206cf6400f59443327ea1091113f310d9013`
- Preserved invalid target commit: `78889b69b75baa424e89332558bda798685e9634`
- Remote-anchor tag: `remote-anchor-preserve-gate4-001a-invalid-self-report-audit-23aa206`
- Preserved Claude audit SHA-256: `66e7a1cf846679d9a1d51e3fe60220035b96741b6af3056c516fa609e1044e0c`

Live readback at draft time found local `HEAD`, remote branch, and remote tag all at `23aa206cf6400f59443327ea1091113f310d9013`. The preserved invalid target commit is an ancestor of the current anchored commit.

This draft does not rely on memory for commit hashes, branch state, tag state, worktree state, test counts, artifact paths, or prior Gate verdicts.

## Problem Definition

The previous Gate4 implementation attempt produced invalid self-report negative evidence. The failure was not a small implementation defect. It was an evidence-type failure: candidate behavior appeared equivalent to a label-generator, handwritten-oracle, or unfairly weakened-baseline path, so the high candidate score could not count as mechanism evidence.

The replacement task family must be designed to falsify cheap shortcuts before any candidate is implemented. It must test whether a future candidate can exhibit bounded social-causal transfer under controlled conditions while preventing the following from counting as evidence:

- label-generator equivalence
- handwritten oracle candidate path
- partner-ID lookup
- preference-table shortcut
- retrieval shortcut
- imitation shortcut
- trace memorization
- weakened baseline contrast
- rule mirroring
- static verdict reports
- unconditional clean reports
- tests that only assert pass

The design target is not to make Gate4 pass. The design target is to define conditions under which the replacement task family is rejected before candidate implementation.

## Current Stage

Current stage: engineering-governance / negative-evidence preservation completed.

Latest preserved negative evidence:

- `invalid_self_report`
- `negative_evidence_baseline_equivalence`
- `audit_blocked_requires_repair`

Current authorized action:

- Draft a replacement Gate4 task-falsification and mechanism-design card.

Current unauthorized actions:

- Do not repair commit `78889b69b75baa424e89332558bda798685e9634` directly.
- Do not create a same-family 002E patch.
- Do not implement candidate code.
- Do not enter Gate5, admission, bridge, runtime, EGO-mainline, LLM/RAG, companion, or productization.
- Do not claim Gate4 validity.
- Do not claim social understanding, agency, subjectivity, consciousness, emotion, autonomy, stable user benefit, or EGO readiness.

## Anti-Sycophancy Audit

Strongest baseline explanation:

Any apparent future Gate4 success is most likely non-mechanism recovery unless proven otherwise: partner-ID lookup, preference-table reconstruction, retrieval over prior traces, imitation of observed behavior, order-k history matching, generator-proxy decoding, oracle-shaped rules, serialized-state decoding, full-bundle decoding, graph/cache lookup, count tables, FSM planning, or trace memorization.

Strongest reason this task may be invalid:

The replacement task may still encode the answer in the generator structure, observation schema, partner identity, deterministic literals, filenames, helper functions, trace order, or evaluation utilities. If that happens, a high future candidate score would only show that the task is shortcut-solvable.

What would falsify the current framing:

- The target can be recovered from single-step visible fields.
- The target can be recovered from partner ID, context ID, stable row order, or preference table.
- Any cheap independent baseline reaches or exceeds the planned candidate threshold before candidate implementation.
- Replay cannot recompute behavior from `serialized_state + observation`.
- The leakage scanner lacks a positive-control case that actually fails.
- The design needs the candidate implementation to decide whether baselines are valid.

Evidence that would still be insufficient:

- Aggregate candidate score.
- Stored-output or hash-only replay.
- A clean report over a sanitized bundle.
- Baseline comparison that weakens the strongest faithful baseline.
- Post-hoc explanation of why the candidate "used" a mechanism.
- Tests that assert a pass verdict without recomputing metrics.
- A task card, source pin, commit, tag, or remote anchor by itself.

Whether this tests mechanism or only behavioral resemblance:

This design task tests neither. It produces a governance contract for a future mechanism-proxy test. A future executable task may test bounded social-causal-transfer proxy behavior only if it enforces baseline-first invalidation, intervention sensitivity, trace/replay recomputation, ablation sensitivity, leakage resistance, and computed-evidence provenance.

## Hypothesis

A future Gate4 replacement may be valid only if the task family requires a candidate to infer and update a bounded latent social-causal model from history, intervention, and transfer structure, while independent cheap baselines fail under the same evaluation.

Bounded mechanism hypothesis only:

A future candidate may demonstrate bounded social-causal-transfer proxy behavior if it can:

1. infer latent partner/task structure not directly readable from single-step observable fields;
2. update internal state from interaction history or intervention feedback;
3. transfer predictions across held-out partner/context/task families;
4. remain robust under leakage scans, ablations, replay recomputation, and independent baseline comparison.

This is not a consciousness, emotion, agency, subjectivity, autonomy, or EGO-readiness hypothesis.

## Framing Correction

Do not require that the target be impossible to recover from observations in general.

Correct requirement:

The target must not be recoverable from single-step visible fields, partner ID, static preference tables, generator literals, rule mirroring, retrieval, imitation, trace memorization, or shared helper functions.

The target may be recoverable only through the intended information route:

- cross-episode history
- controlled intervention response
- latent state update
- causal transfer structure
- held-out context generalization
- serialized-state replay recomputation

If the intended route is absent, the task is not a valid mechanism test.

## Required Negative-Evidence Inheritance

This card explicitly inherits the preserved invalid-self-report audit:

- Preserved report: `docs/research/CLAUDE-INDEPENDENT-AUDIT-IMPLEMENT-FUTURE-GATE4-CROSS-FAMILY-SOCIAL-CAUSAL-TRANSFER-001A.md`
- Preservation result: `artifacts/preserve_claude_independent_audit_implement_future_gate4_001a_invalid_self_report_restore_worktree_001a/result.json`
- Routing record: `artifacts/preserve_claude_independent_audit_implement_future_gate4_001a_invalid_self_report_restore_worktree_001a/negative_evidence_routing_record.json`
- Classification record: `artifacts/preserve_claude_independent_audit_implement_future_gate4_001a_invalid_self_report_restore_worktree_001a/invalid_self_report_classification.json`

Inherited conclusions:

- Candidate score was reported as `1.0`, but the independent audit classified the result as `invalid_self_report`.
- A same-access faithful baseline scored `1.0`, tying the candidate and producing `negative_evidence_baseline_equivalence`.
- The prior result cannot support positive Gate4 evidence, mechanism validity, social-latent inference success, Gate5, admission, bridge, runtime, or EGO-mainline.
- Commit `78889b69b75baa424e89332558bda798685e9634` must be preserved as invalid negative evidence and must not be repaired directly.

This card also inherits the current-repo baseline-collapse guardrail from `docs/research/GATE4-TASK-FAMILY-THEORY-COVERAGE-REDESIGN-001A.md`: future Gate4 work must make baseline, leakage, replay, and negative-evidence stop conditions central, not secondary.

## Baseline Inventory

All baselines below are required cheap baselines. They must be independent callable implementations. They must not share candidate code, generator code, helper functions, tables, literals, target rules, or scoring shortcuts.

Baselines must run before candidate implementation.

Required cheap baselines:

1. Partner-ID lookup baseline
   - Predicts using partner identity or stable partner index only.
   - Invalidates the task if it reaches or exceeds the planned candidate threshold.

2. Preference-table baseline
   - Learns or reconstructs partner-choice tables from observed history.
   - Invalidates the task if table reconstruction reaches or exceeds the planned candidate threshold.

3. Retrieval baseline
   - Predicts by nearest-neighbor or exact-match retrieval over prior traces.
   - Invalidates the task if retrieval reaches or exceeds the planned candidate threshold.

4. Imitation baseline
   - Predicts from observed action frequencies or demonstrated behavior without latent causal update.
   - Invalidates the task if imitation reaches or exceeds the planned candidate threshold.

5. Order-k history baseline
   - Uses bounded recent history without causal latent inference.
   - Invalidates the task if bounded recent history reaches or exceeds the planned candidate threshold.

6. Static majority / marginal baseline
   - Predicts global or context-conditioned marginal target.
   - Invalidates the task if the candidate target cannot clear this sanity baseline by the predeclared margin.

7. Generator-proxy baseline
   - Attempts to infer labels from exposed generator-correlated fields.
   - Invalidates the task if exposed fields leak the target.

8. Oracle-shape baseline
   - Uses candidate-like rule templates without learned state update.
   - Invalidates the task if the task is solvable by handwritten if/else structure.

9. Shuffled-linkage control
   - Breaks partner/context/episode linkage while preserving superficial distributions.
   - Invalidates the task if shuffled linkage preserves planned candidate-level performance.

10. Counterfactual-pair baseline
   - Tests whether paired observations with changed latent cause but similar surface fields force different predictions.
   - Invalidates the task if surface-similar pairs remain shortcut-solvable.

Current-repo inherited challenger families are also mandatory where applicable:

- serialized-state decoder
- full-bundle decoder
- n-gram trace lookup
- pair-count or frequency baseline
- static belief table
- graph-cache family: `graph_lookup`, `transition_table`, `successor_map`, `count_table`, `fsm_planner`, `episodic_traversal`
- query-capable imitation baseline

Baseline invalidation rule:

If any cheap faithful baseline reaches or exceeds the planned candidate threshold, the task family is invalid. Do not implement candidate. Do not weaken that baseline. Do not revise the threshold after seeing baseline results.

Best faithful baseline rule:

The strongest baseline that is faithful to the available information must be reported as the primary contrast. It must not be artificially weakened.

## Ablation Requirement

The future executable task must rerun full episodes under real interventions. It must not merely alter stored outputs, hashes, or reports.

Required ablations:

1. Remove latent social-causal history.
2. Remove partner/context linkage.
3. Shuffle intervention feedback.
4. Freeze internal state update.
5. Swap held-out partner/context mappings.
6. Inject misleading retrieval matches.
7. Remove transfer phase.
8. Replace causal feedback with non-causal correlated cue.
9. Positive-control leakage injection.
10. Candidate-code isolation check.

Expected ablation behavior:

- If the task is valid, removing the intended causal/history/update route should degrade candidate performance.
- If performance does not degrade, the candidate is likely using a shortcut.
- If leakage-positive control does not fail, the leakage scanner is invalid.
- If baseline performance does not change under intended ablations, the task may not discriminate mechanism use.

## Trace / Replay Requirement

Replay must recompute behavior from:

```text
serialized_state + observation
```

Replay must not merely compare stored hashes, cached predictions, or static trace rows.

Required replay fields:

- `run_id`
- `seed`
- `context_id`
- `episode_id`
- `partner_id` or anonymized partner key
- `observation`
- `serialized_state_before`
- `candidate_prediction`
- `serialized_state_after`
- `target`
- `score_contribution`
- `producer_function`
- `code_path_hash`
- `aggregation_rule`

Replay acceptance:

1. Recompute candidate prediction from serialized state and observation.
2. Recompute score from prediction and target.
3. Verify that replayed score matches original score.
4. Verify that changing serialized state can change prediction when the task requires state dependence.
5. Verify that replay fails when serialized state, observation, or linkage is corrupted.
6. Re-invoke baselines under replay when baseline replay is claimed.

Replay rejection:

Reject if replay only checks stored prediction hashes or static report consistency.

## Computed-Evidence Provenance Gate

Every score, baseline, ablation result, leakage scan, and replay metric must come from callable computation paths.

Forbidden:

- static verdict JSON
- literal pass reports
- unconditional clean reports
- tests that only assert pass
- hard-coded expected metrics
- hand-filled score files
- candidate importing generator code
- candidate sharing helper functions with target generation
- candidate mirroring target rule
- baseline code that is intentionally weakened
- leakage scanner without positive control
- replay that only compares stored hashes

Every score must record:

- `producer_function`
- `input_artifacts`
- `run_id`
- `seed`
- `context_ids`
- `episode_ids`
- `aggregation_rule`
- `code_path_hash`

Required independence:

- Candidate predictor must not import, call, mirror, or share logic with target generator.
- Label generator and candidate predictor must not share rules, tables, literals, or helper functions.
- Baselines must be callable independent implementations.
- Ablations must rerun episodes under real interventions.
- Leakage scanner must include at least one injected positive-control case and must fail when leakage is injected.
- Replay must recompute from `serialized_state + observation`.

Unused-data blocker:

Any unused frozen seed, train context, held-out context, counterfactual pair, ablation condition, or declared baseline must block the task.

## Acceptance Gate

This design task passes only if it produces a replacement Gate4 task card that includes:

1. problem definition
2. current stage
3. bounded hypothesis
4. baseline inventory
5. ablation requirement
6. trace/replay requirement
7. computed-evidence provenance gate
8. acceptance gate
9. claim ceiling
10. stop condition
11. rollback plan

It must also include:

- explicit negative-evidence inheritance from preserved invalid-self-report audit
- explicit ban on repairing the invalid commit directly
- explicit cheap-baseline-first requirement
- explicit task-family invalidation rule when cheap baselines succeed
- explicit leakage-positive-control requirement
- explicit replay recomputation requirement
- explicit no-candidate-implementation boundary
- explicit no-Gate5/admission/bridge/runtime boundary

This task does not pass if it implements candidate code, runs experiments, creates pass-shaped metrics, or claims Gate4 validity.

## Stop Condition

Stop immediately and preserve as negative evidence if any of the following occurs:

1. The task design requires candidate implementation to determine whether cheap baselines are valid.
2. Target labels can be recovered from visible fields by simple rules.
3. Target labels can be recovered from partner ID or preference table.
4. Label generator and candidate predictor would need to share helper functions, tables, or literals.
5. Any cheap baseline reaches the proposed candidate threshold.
6. Leakage scanner has no positive-control failure case.
7. Replay cannot recompute behavior from `serialized_state + observation`.
8. Ablations do not require real episode reruns.
9. The card drifts toward "make Gate4 pass."
10. The design requires weakening the best faithful baseline.

If stopped, write a failure-preserving report and do not continue to implementation.

## Rollback Plan

If this design is later found invalid:

1. Preserve the invalid design as negative evidence.
2. Record the exact reason for invalidation.
3. Do not patch it into a pass-shaped task.
4. Do not reuse affected thresholds, schemas, or helper functions without audit.
5. Restore repo to the previous clean anchored state if implementation side effects occurred.
6. Open a new replacement-design task only if it changes the task family or falsification route, not merely the wording.

## Current Route Best Answer

Within the current route, the best next action is exactly this design card and its machine-readable governance artifacts. It should freeze the falsification boundary before any candidate, harness, or experiment is created.

## Better Framing Outside The Current Route

The better framing is not:

```text
How do we build a future Gate4 candidate that passes?
```

It is:

```text
What evidence target would make shortcut equivalence a decisive pre-candidate failure?
```

This makes baseline-first invalidation, leakage positive controls, real replay recomputation, and negative-evidence stop conditions the center of the task.

## Minimal Validation Action

The minimum future validation action is a no-candidate baseline-preflight package that runs the cheap baselines and leakage positive control against the proposed task family before candidate code exists.

That future preflight must answer:

- Which target cannot be solved by partner ID, preference table, visible fields, retrieval, or order-k history?
- Which held-out split proves more than same-family interpolation?
- Which intervention makes the claimed update path necessary?
- Which faithful baseline tie immediately blocks the route?
- Which replay corruption proves cached outputs cannot pass?

## Stop-Loss And Rollback

Stop if the next route starts implementing a candidate, environment, harness, baseline, test, 002E, Gate5/admission/bridge/runtime/EGO-mainline artifact, LLM/RAG path, UI, companion behavior, or productization before the baseline-preflight contract is separately authorized.

Rollback means leave unauthorized generated files uncommitted, report exact paths, and preserve any invalid design as negative evidence. Do not edit prior artifacts or rewrite history.

## Acceptance Signals

Acceptance signals for this design task:

- Design/governance artifacts only.
- No `src/` changes.
- No `tests/` changes.
- No candidate implementation.
- No experiment execution.
- Preserved invalid-self-report audit inherited explicitly.
- Stop conditions encoded explicitly.
- Baseline inventory encoded explicitly.
- Provenance gate encoded explicitly.
- Claim ceiling bounded to replacement Gate4 task-design only.

## Claim Ceiling

This task may claim only:

- replacement Gate4 task-design completed;
- evidence-hygiene requirements specified;
- future falsification harness requirements specified;
- negative evidence inherited and bounded;
- no implementation performed.

This task must not claim:

- Gate4 validity;
- social understanding;
- agency;
- subjectivity;
- consciousness;
- real emotion;
- live autonomy;
- stable user benefit;
- EGO readiness;
- runtime readiness;
- admission readiness;
- bridge readiness.

## What This Does Not Prove

This card does not prove future Gate4 validity. It does not prove mechanism validity, social understanding, agency, subjectivity, consciousness, emotion, autonomy, EGO readiness, runtime readiness, admission readiness, bridge readiness, companion readiness, or user benefit.

It also does not prove that a future replacement task family will resist every shortcut. It only defines a bounded falsification-first design contract that requires cheap shortcuts to be tested before candidate implementation.
