# GATE4-001C-EXECUTION-CONTRACT-001D-AMENDMENT

Task ID: GATE4-001C-EXECUTION-CONTRACT-001D-AMENDMENT

Mode: Bounded contract-amendment drafting only.

Layer: Evidence-governance / failure-preserving contract repair only.

Claim ceiling: bounded Gate4 001C execution-contract 001D amendment only; no Gate4 001C execution, no Gate4 validity, no mechanism validity, no theory validity, no Gate5/admission/runtime/bridge/EGO-mainline readiness, and no agency, selfhood, consciousness, real emotion, relationship learning, or stable autonomy claim.

## Authorization Boundary

This amendment drafts a future execution-contract repair after independent audit
classified commit `bbbb66c85f51d7b2b0176e5c575aa5fe64e29ece` as
`audit_failed_false_pass_or_computation_gap`.

This task does not execute Gate4 001C, repair `bbbb66c`, rerun tests, rerun
Gate4 001C, create 001D execution files, enter Gate5, enter admission, enter
runtime, enter bridge, or touch EGO-mainline.

Authorization matrix:

- `gate4_001c_execution_authorized`: false
- `gate4_001c_reexecution_authorized`: false
- `gate5_authorized`: false
- `admission_authorized`: false
- `runtime_authorized`: false
- `bridge_authorized`: false
- `ego_mainline_authorized`: false
- `mechanism_validity_claim_authorized`: false
- `agency_claim_authorized`: false
- `consciousness_claim_authorized`: false

## Bounded Task Card Fields

- Problem definition: the 001C execution contract allowed a false-pass surface by letting harness and leakage controls be satisfied against synthetic or governance-only inputs instead of the real output bundle.
- Current stage: post-execution audit preservation and future contract amendment only.
- Hypothesis: a future rerun contract can preserve the failure by requiring real-bundle harness submission, real-bundle leakage scanning, stronger count-table challengers, semantic ablation alignment, and state-update replay.
- Baseline: the previous 001C baseline family was insufficient because a stream-keyed `count_table` challenger matched the candidate at `1.0`.
- Ablation: future ablations must be real reruns and semantically match their names; mismatches are blocking failures.
- Trace/replay requirement: future replay must recompute both action selection and `serialized_state_after`, not only action.
- Acceptance gate: this amendment is accepted only as a static governance contract if all required anchors read back exactly and all amendment artifacts parse as JSON.
- Claim ceiling: this amendment does not produce mechanism evidence.
- Stop condition: any attempt to use `bbbb66c` as positive Gate4 support, rerun Gate4 001C, repair old artifacts, or authorize downstream stages stops the task.
- Rollback plan: remove only this task card and `artifacts/gate4_001c_execution_contract_001d_amendment/`.

## Prerequisite Anchors

The future executor must read back these exact anchors before any 001D rerun:

- Execution-card draft anchor:
  - commit: `43284ae960d08a2a3f8094f16b76e519ef451899`
  - tag: `remote-anchor-gate4-001c-execution-task-card-001a-43284ae`
- Failed execution-preflight evidence snapshot:
  - commit: `bbbb66c85f51d7b2b0176e5c575aa5fe64e29ece`
  - tag: `remote-anchor-gate4-001c-failure-preserving-repair-001c-execution-preflight-bbbb66c`
- Claude audit of failed execution preflight:
  - commit: `5a005a2cb4dc1843e45bea4e34f7ad881c63169f`
  - tag: `remote-anchor-claude-audit-gate4-001c-execution-preflight-5a005a2`
  - report: `docs/research/AUDIT-GATE4-001C-FAILURE-PRESERVING-REPAIR-001C-EXECUTION-PREFLIGHT-CLAUDE-001.md`

If any local or remote readback differs from the exact commit above, future
execution must stop with `blocked_prerequisite_anchor_mismatch`.

## Failure Inheritance

Commit `bbbb66c85f51d7b2b0176e5c575aa5fe64e29ece` is not accepted as Gate4
001C pass evidence.

It is retained as negative evidence and as a false-pass surface. Its computed
metrics may be cited only as reproducibility evidence, not as Gate4 mechanism
evidence.

The final verdict `passed_bounded_gate4_001c_execution_preflight` in `bbbb66c`
is superseded by the Claude audit verdict
`audit_failed_false_pass_or_computation_gap`.

Any downstream use of `bbbb66c` as positive support must fail with
`blocked_known_false_pass_snapshot`.

## Harness Scope Repair

Future execution must submit the real output bundle to
`evidence_harness_contract_enforcement_smoke_001a.runner.evaluate_bundle`.

The real harness bundle must include at least:

- `result.json`
- `metric_provenance.json`
- `baseline_comparison.json`
- `ablation_report.json`
- `replay_report.json`
- `leakage_scan_report.json`
- `harness_challenger_input_bundle.json`
- `harness_challenger_report.json`
- `tests/test_gate4_001c_failure_preserving_repair_001c.py`
- source file hashes for all candidate, baseline, ablation, replay, and leakage modules
- output bundle manifest with file hashes

A governance-only stub must not satisfy the harness threshold.

If the true bundle triggers `rejected_false_pass_risk`, the future execution
must report `blocked_by_evidence_harness_challenger`. This is a valid
failure-preserving result, not a condition to bypass.

Future execution must also run a harness positive-control bundle proving that
`evaluate_bundle` blocks a known false-pass-shaped bundle.

Required future artifacts:

- `harness_positive_control_bundle.json`
- `harness_positive_control_report.json`
- `harness_real_bundle_report.json`

If the positive control does not block, verdict must be
`failed_harness_not_fail_able`. If the real bundle is not actually submitted,
verdict must be `failed_harness_scope_evasion`.

## Leakage Scope Repair

Future leakage scanning must load `output_bundle_manifest.json` and scan every
included real artifact path declared in the manifest. Synthetic controls may be
used only as additional controls; they are insufficient alone.

Each scanned item must record scanned path, path class, hash, scanner rule,
finding, and scanner function provenance. Excluded paths must be marked
`not_scanned`, never `clean`.

Sentinel leakage controls must be injected into copied temporary artifact
fixtures, not historical artifacts. The scanner must prove it detects injected
sentinels in real-bundle-shaped files.

If `--bundle` is accepted but ignored, verdict must be
`failed_leakage_bundle_argument_ignored`. If only synthetic controls are
scanned, verdict must be `failed_leakage_scope_evasion`.

## Baseline Challenger Repair

Future rerun must add non-oracle `count_table_challenger` baselines with these
minimum variants:

- key = `(seed, context_id, partner_id)`
- key = `(context_id, partner_id)`
- key = `(context_id, observable_prefix_without_phase_token)`
- key = `(seed, context_id, partner_id, observable_prefix_without_phase_token)`

If any non-oracle count-table challenger matches or exceeds the candidate, the
future verdict must be `blocked_candidate_count_table_equivalence`.

The future result must not claim candidate margin unless it beats all required
baselines and all challenger baselines.

The `retrieval_imitation_baseline` must compare observable prefixes after
normalizing away train/heldout phase tokens. If retrieval degenerates to
constant prediction because of avoidable prefix mismatch, verdict must be
`failed_retrieval_baseline_degenerate_by_design`.

## Ablation Naming Repair

Future ablation names must semantically match interventions:

- `shuffled_feedback_ablation` must actually shuffle feedback, not deterministically invert rewards.
- `partner_identity_masked_ablation` must mask identity fields, not merely set feedback to `None`.
- If an ablation is renamed, the new name must reflect the actual intervention.

If ablation name and intervention mismatch, verdict must be
`failed_ablation_semantic_mismatch`.

## Replay Repair

Future replay must recompute both action selection and state update /
`serialized_state_after`.

If replay validates only action and not state update, verdict must be
`failed_replay_state_update_not_recomputed`.

## Test Repair

Future tests must include failure-path coverage for:

- harness real-bundle scope evasion
- harness positive control not blocking
- leakage `--bundle` argument ignored
- leakage synthetic-only scan
- count-table challenger matching candidate
- retrieval baseline degenerating from phase-token mismatch
- replay action-only validation without state-update recomputation
- ablation semantic mismatch

Tests must not merely assert pass-shaped JSON fields.

## Future Verdict Taxonomy

Future execution verdict taxonomy must include at least:

- `passed_bounded_gate4_001c_execution_preflight_after_001d_repair`
- `blocked_by_evidence_harness_challenger`
- `failed_harness_not_fail_able`
- `failed_harness_scope_evasion`
- `failed_leakage_bundle_argument_ignored`
- `failed_leakage_scope_evasion`
- `blocked_candidate_count_table_equivalence`
- `failed_retrieval_baseline_degenerate_by_design`
- `failed_ablation_semantic_mismatch`
- `failed_replay_state_update_not_recomputed`
- `blocked_known_false_pass_snapshot`
- `blocked_prerequisite_anchor_mismatch`
- `failed_old_artifact_mutation`
- `failed_metric_without_callable_provenance`

## Static Validation Only

This amendment is validated only by anchor readback, JSON parse checks for
`artifacts/gate4_001c_execution_contract_001d_amendment/`, and git diff/status
scope checks.

Do not run Gate4 001C, execution tests, or full project pytest for this
amendment.

## What This Does Not Prove

This amendment does not prove Gate4 validity, mechanism validity, theory
validity, architecture correctness, Gate5/admission/runtime/bridge/EGO-mainline
readiness, agency, selfhood, consciousness, real emotion, relationship learning,
or stable autonomy.
