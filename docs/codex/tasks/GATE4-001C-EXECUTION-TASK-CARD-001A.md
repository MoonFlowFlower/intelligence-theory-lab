# GATE4-001C-EXECUTION-TASK-CARD-001A

Task ID: GATE4-001C-EXECUTION-TASK-CARD-001A

Mode: Bounded execution-card drafting only.

Layer: Evidence-governance / execution-contract preparation boundary only.

Claim ceiling: bounded Gate4 001C execution-card drafting only; no Gate4 001C execution, no mechanism validity, no Gate5/admission/runtime/bridge/EGO-mainline readiness

## Authorization Boundary

This task card drafts the future Gate4 001C execution contract. It does not
execute Gate4 001C, implement candidate source, implement execution tests,
generate Gate4 001C metrics, create remote anchor tags, enter Gate5, enter
admission, enter runtime, enter bridge, or validate a mechanism.

This task card does not restore, read, copy, import, cherry-pick, merge, or use
provisional Gate4 001C commit `d7b5b7a33cc68cbe7e3ca0960b99e0082e1ac728`.

Authorization matrix:

- `gate4_001c_execution_authorized`: false
- `gate4_001c_execution_card_drafted`: true
- `gate5_authorized`: false
- `admission_authorized`: false
- `runtime_authorized`: false
- `bridge_authorized`: false
- `ego_mainline_authorized`: false
- `mechanism_validity_claim_authorized`: false
- `agency_claim_authorized`: false
- `consciousness_claim_authorized`: false

## Anti-Sycophancy Audit

Strongest baseline explanation: a future Gate4 001C run may appear to pass
because historical Gate4 001B bounded-pass language, artifact shape, old scores,
old baselines, old ablation summaries, old replay summaries, or scanner
whitelists create pass-like evidence without computed mechanism evidence.

Strongest reason this task may be invalid: if the future executor cannot build
the declared isolated candidate, independent baselines, real ablations,
behavioral replay, and fail-able leakage scanner without using old Gate4 001B
or quarantined evidence, the correct result is a blocking verdict, not a pass.

Falsification condition: any future execution uses a quarantined target as
positive support, reads provisional 001C, changes thresholds after observing
results, omits a required baseline or ablation, uses replay without behavior
recomputation, misses a leakage positive control, mutates protected artifacts,
or is blocked by the evidence-harness challenger.

Evidence still insufficient after this task: this card and its artifacts do not
prove Gate4 validity, mechanism validity, theory validity, architecture
correctness, EGO-mainline readiness, agency, selfhood, consciousness, real
emotion, relationship learning, or stable autonomy.

This task tests only execution-contract completeness. It does not test a
mechanism and does not produce behavioral resemblance evidence.

## Prerequisite Anchors

Before any future Gate4 001C execution can be attempted, the executor must
read back these exact anchors:

- Gate4 001C task-card amendment:
  - commit: `1267ada5a0e72cf7bcfb071a63e2e6828b7e5bbc`
  - tag: `remote-anchor-gate4-001c-failure-preserving-repair-task-card-001b-amendment-1267ada`
- Claude narrow amendment audit:
  - commit: `5e004acc5927447ea697b3453f9fc331ef4f2ff4`
  - tag: `remote-anchor-claude-audit-gate4-001c-task-card-001b-amendment-5e004ac`

If either anchor fails exact local and remote readback, future execution verdict
must be `blocked_prerequisite_anchor_mismatch`.

## Future Execution Source And Entrypoint

The future execution task must create a new isolated source family:

`src/gate4_001c_failure_preserving_repair_001c/`

The future execution entrypoint must be:

```powershell
python -m gate4_001c_failure_preserving_repair_001c.run --config artifacts/gate4_001c_failure_preserving_repair_001c/config.json
```

The future execution must not reuse `ego_mainline_gate4_preflight_executable_001b`
code as candidate implementation. That family may be used only as rejected
negative evidence and positive-control false-pass reference.

## Future Execution Artifacts

Future execution artifacts must be isolated under:

`artifacts/gate4_001c_failure_preserving_repair_001c/`

The future execution must not write into previous Gate0/Gate1/Gate2/Gate3/Gate4,
Gate4 001B, admission, or evidence-harness artifact directories.

## Future Tests And Commands

The future execution test file must be:

`tests/test_gate4_001c_failure_preserving_repair_001c.py`

The future execution card must predeclare and run these commands in order:

```powershell
git status --short --branch
git rev-parse 1267ada5a0e72cf7bcfb071a63e2e6828b7e5bbc
git rev-parse 5e004acc5927447ea697b3453f9fc331ef4f2ff4
git rev-parse remote-anchor-gate4-001c-failure-preserving-repair-task-card-001b-amendment-1267ada
git rev-parse remote-anchor-claude-audit-gate4-001c-task-card-001b-amendment-5e004ac
git ls-remote origin refs/tags/remote-anchor-gate4-001c-failure-preserving-repair-task-card-001b-amendment-1267ada
git ls-remote origin refs/tags/remote-anchor-claude-audit-gate4-001c-task-card-001b-amendment-5e004ac
python -m gate4_001c_failure_preserving_repair_001c.protected_artifacts --phase before --config artifacts/gate4_001c_failure_preserving_repair_001c/config.json --out artifacts/gate4_001c_failure_preserving_repair_001c/protected_artifact_hashes_before.json
python -m gate4_001c_failure_preserving_repair_001c.run --config artifacts/gate4_001c_failure_preserving_repair_001c/config.json
python -m pytest tests/test_gate4_001c_failure_preserving_repair_001c.py -q
python -m gate4_001c_failure_preserving_repair_001c.validate_json --artifact-dir artifacts/gate4_001c_failure_preserving_repair_001c
python -m gate4_001c_failure_preserving_repair_001c.leakage_scan --config artifacts/gate4_001c_failure_preserving_repair_001c/config.json --bundle artifacts/gate4_001c_failure_preserving_repair_001c/output_bundle_manifest.json --out artifacts/gate4_001c_failure_preserving_repair_001c/leakage_scan_report.json
python -c "import json, pathlib; from evidence_harness_contract_enforcement_smoke_001a.runner import evaluate_bundle; bundle=json.loads(pathlib.Path('artifacts/gate4_001c_failure_preserving_repair_001c/harness_challenger_input_bundle.json').read_text(encoding='utf-8')); pathlib.Path('artifacts/gate4_001c_failure_preserving_repair_001c/harness_challenger_report.json').write_text(json.dumps(evaluate_bundle(bundle), indent=2, sort_keys=True), encoding='utf-8')"
python -m gate4_001c_failure_preserving_repair_001c.protected_artifacts --phase after --config artifacts/gate4_001c_failure_preserving_repair_001c/config.json --out artifacts/gate4_001c_failure_preserving_repair_001c/protected_artifact_hashes_after.json
python -m gate4_001c_failure_preserving_repair_001c.protected_artifacts --phase compare --before artifacts/gate4_001c_failure_preserving_repair_001c/protected_artifact_hashes_before.json --after artifacts/gate4_001c_failure_preserving_repair_001c/protected_artifact_hashes_after.json --out artifacts/gate4_001c_failure_preserving_repair_001c/protected_artifact_mutation_report.json
git status --short --branch
```

## Data, Episodes, Seeds, And Splits

Each future episode record must contain:

- `episode_id`
- `seed`
- `context_id`
- `partner_id`
- `train_or_heldout`
- `observation_t`
- `candidate_serialized_state_before`
- `candidate_action_t`
- `environment_feedback_t`
- `candidate_serialized_state_after`
- `ground_truth_latent_label`
- `ground_truth_latent_label_access_allowed`
- `counterfactual_pair_id`
- `counterfactual_source_episode_id`
- `metric_eligibility`

`ground_truth_latent_label_access_allowed` must be false for the candidate and
all non-oracle baselines.

Predeclared seeds:

`[4101, 4102, 4103, 4104, 4105]`

Predeclared contexts:

`["ctx_stable_preference", "ctx_shifted_preference", "ctx_ambiguous_signal", "ctx_conflicting_feedback"]`

Predeclared partners:

`["partner_a", "partner_b", "partner_c", "partner_d"]`

Minimum episode count:

- 5 seeds
- 4 contexts
- 4 partners
- at least 10 train episodes per seed/context/partner
- at least 10 heldout episodes per seed/context/partner
- minimum total train episodes: 800
- minimum total heldout episodes: 800

Train/heldout split must be deterministic from
`(seed, context_id, partner_id, episode_index)` and recorded in a callable split
function. A handwritten split list is forbidden.

## Counterfactual Pair Construction

Every heldout episode must have a counterfactual pair with:

- same seed
- same context family
- same observable prefix length
- different latent partner condition
- matched surface observation length
- no direct partner-ID shortcut
- pair construction function recorded as callable provenance

If any heldout episode lacks a valid counterfactual pair, future verdict must be
`blocked_incomplete_counterfactual_pairs`.

## Candidate Restrictions

The future candidate must:

- update internal serialized state from observation and feedback only
- not read ground-truth latent labels
- not read heldout labels
- not read partner ID as a direct lookup key
- not branch on literal episode IDs
- not use static dictionaries mapping context/partner to answer
- not use old Gate4 001B outputs as pass evidence
- not use sibling Gate4 001B bounded-pass verdicts as evidence
- not use any of the 12 quarantined critical/high-risk targets as positive
  support evidence
- not cite targets 11-12 as confirmed false-pass contamination

## Required Baselines

Future execution must implement independent callable baselines, not wrappers
around the candidate. Every baseline must run on the same heldout episode set as
the candidate.

Required baselines:

1. `frozen_state_baseline`
2. `order2_history_baseline`
3. `partner_id_table_baseline`
4. `context_only_baseline`
5. `preference_table_baseline`
6. `retrieval_imitation_baseline`
7. `trace_only_hygiene_baseline`
8. `oracle_label_positive_control`

The oracle label positive control is allowed only as a sanity upper bound. It
must not count as a competitor baseline and must not support admission.

If any required baseline is missing or not invoked, future verdict must be
`failed_missing_independent_baseline`.

## Required Ablations

Future execution must rerun episodes under real interventions. Ablations must
not be post-hoc filters over already-generated outputs.

Required ablations:

1. `no_state_update_ablation`
2. `shuffled_feedback_ablation`
3. `partner_identity_masked_ablation`
4. `context_shift_removed_ablation`
5. `counterfactual_pair_swapped_ablation`
6. `serialized_state_zeroed_before_action_ablation`

If ablation artifacts do not show independent reruns, future verdict must be
`failed_ablation_not_real_intervention`.

## Replay Requirement

Replay must recompute candidate behavior from:

- `serialized_state_before`
- `observation_t`
- candidate code path hash
- config hash
- seed
- episode ID

Replay must not merely compare stored hashes or stored candidate actions.

If replay does not recompute behavior, future verdict must be
`failed_replay_not_behavioral_recomputation`.

## Leakage Scanner Contract

The future execution card must require a callable leakage scanner with explicit
included and excluded path classes.

Rules:

- included paths must be scanned
- excluded paths must be marked `not_scanned`, never `clean`
- no broad whitelist / allowlist / trusted-prefix / known-safe-directory escape
  is allowed
- positive controls must be placed in normal included path, whitelist-looking
  path, allowlist-looking path, trusted-prefix-looking path, and
  excluded-looking path
- clean controls must pass through the same scanner path
- a missed positive control is failure
- an unconditional clean report is failure
- any broad exemption is failure

Required verdict on failure:

`failed_leakage_scanner_not_fail_able`

## Evidence-Harness Challenger

The future 001C output bundle must be passed through:

- module: `evidence_harness_contract_enforcement_smoke_001a.runner`
- function: `evaluate_bundle`
- source path: `src/evidence_harness_contract_enforcement_smoke_001a/runner.py`
- anchor: `remote-anchor-evidence-harness-contract-enforcement-smoke-001a-5b4cdbe`
- anchor commit: `5b4cdbeedb380aafa8da9ead827e1b40b04d8153`

The challenger is a blocker only, not a positive admission discriminator.

If the harness blocks, future verdict must be
`blocked_by_evidence_harness_challenger`.

If the harness entrypoint is missing, future verdict must be
`blocked_missing_harness_challenger_entrypoint`.

## Metric Provenance And Thresholds

Every metric, comparison, baseline score, ablation score, leakage result, replay
result, and final verdict must record:

- `producer_function`
- `producer_module`
- `code_path_hash`
- `input_artifacts`
- `input_artifact_hashes`
- `run_id`
- `seed`
- `episode_ids`
- `train_context_ids`
- `heldout_context_ids`
- `counterfactual_pair_ids`
- `aggregation_rule`
- `threshold_rule`
- `created_at_utc`

No metric may be accepted if it appears only as a literal in JSON without a
callable producer path. If any score lacks callable provenance, future verdict
must be `failed_metric_without_callable_provenance`.

Thresholds must be predeclared before any run:

- candidate heldout latent/action-consistency score must exceed the best
  non-oracle baseline by at least `0.20`
- candidate must beat best non-oracle baseline in every context class
- candidate must beat best non-oracle baseline in at least 5/5 seeds
- no context class may fall below `0.70`
- replay recomputation exact-match rate must be `1.0`
- leakage scanner positive-control detection must be `1.0`
- protected artifact mutation violations must be `0`
- harness challenger must not block the future bundle

Thresholds must not be changed after seeing results. If thresholds are changed
after execution begins, future verdict must be
`failed_posthoc_threshold_selection`.

## Protected Artifact Contract

The future execution card must require before/after hash inventories for
protected paths including:

- all prior Gate0/Gate1/Gate2/Gate3 artifact directories
- all prior Gate4 001A/001B/001C task-card amendment artifact directories
- evidence-harness artifacts
- admission artifacts
- Claude audit reports
- remote-anchor reference docs
- canonical rejected Gate4 001B artifacts

Any mutation outside the future 001C allowed paths must fail with
`failed_old_artifact_mutation`.

## Failure Taxonomy

Future verdict taxonomy must include:

- `passed_bounded_gate4_001c_execution_preflight`
- `failed_metric_without_callable_provenance`
- `failed_missing_independent_baseline`
- `failed_ablation_not_real_intervention`
- `failed_replay_not_behavioral_recomputation`
- `failed_leakage_scanner_not_fail_able`
- `blocked_by_evidence_harness_challenger`
- `blocked_missing_harness_challenger_entrypoint`
- `failed_old_artifact_mutation`
- `failed_posthoc_threshold_selection`
- `blocked_prerequisite_anchor_mismatch`
- `blocked_incomplete_counterfactual_pairs`
- `blocked_quarantined_evidence_reuse`
- `failed_provisional_commit_contamination`

## Stop And Rollback

Future execution must stop if any prerequisite anchor mismatches, candidate code
uses old or quarantined evidence as positive support, a required baseline or
ablation is missing, replay is not behavioral recomputation, leakage positive
controls fail, the harness challenger blocks, protected artifacts mutate,
provisional 001C contamination is detected, or any downstream authorization flag
becomes true.

Rollback must remove only newly generated future execution files under:

- `src/gate4_001c_failure_preserving_repair_001c/`
- `tests/test_gate4_001c_failure_preserving_repair_001c.py`
- `artifacts/gate4_001c_failure_preserving_repair_001c/`

Rollback must not modify historical evidence, old Gate artifacts, evidence
harness artifacts, amendment artifacts, or Claude audit reports.

## What This Does Not Prove

This execution-card draft does not prove Gate4 validity, mechanism validity,
theory validity, architecture correctness, EGO-mainline readiness, agency,
selfhood, consciousness, real emotion, relationship learning, or stable
autonomy.
