# ACTION-CONDITIONED-SELF-BOUNDARY-EXECUTABLE-PREFLIGHT-001B-LEARNED-BASELINE-SCALING-CHALLENGE

Verdict: `action_conditioned_self_boundary_executable_preflight_001b_survives_learned_baseline_scaling_challenge`

Current layer: `engineering implementation / offline executable learned-baseline and scaling challenge only`

Mainline integration status: `none`

Enabled status: `local offline module, tests, and artifact generation only`

Real trigger evidence: `callable local 001B execution produced artifacts`

Claim ceiling: `offline learned-baseline/scaling challenge evidence only`

Auto-Remote-Anchor: conditional

No mechanism validity is claimed.

No Gate4, Gate5, bridge, runtime, tournament, companion, product, or EGO-mainline path is enabled.

## Bounded Task Card Readback

- Task id: `ACTION-CONDITIONED-SELF-BOUNDARY-EXECUTABLE-PREFLIGHT-001B-LEARNED-BASELINE-SCALING-CHALLENGE`
- Problem definition: challenge 001A with learned no-boundary baselines, scaling probes, adversarial heldout intervention splits, leakage controls, replay recomputation, and provenance checks.
- Current stage/layer: `engineering implementation / offline executable learned-baseline and scaling challenge only`
- Mainline target: none.
- Enabled-state requirement: `local offline module, tests, and artifact generation only`
- Real-trigger evidence requirement: callable code must generate artifacts from reference, learned baselines, capacity-disabled reference, ablations, leakage, replay, and provenance paths.
- Hypothesis: the 001A reference path remains surface-discriminative against stronger learned no-boundary and capacity-matched disabled alternatives under fixed scaling probes.
- Strongest baseline: `capacity_matched_boundary_disabled_reference`.
- Ablation requirement: rerun all six inherited 001A ablations under every 001B probe setting.
- Trace/replay requirement: recompute from serialized state plus observation and intervention, not stored hashes or verdicts.
- Computed-evidence provenance gate: every score records callable producer, input hash, run id, seed/context/episode ids, aggregation, code path hash, scanner path, replay path, and 001A source hashes.
- Acceptance gate: fixed thresholds, leakage controls, replay, provenance, changed-file allowlist, and bounded claims all pass.
- Claim ceiling: `offline learned-baseline/scaling challenge evidence only`
- Stop condition: `[]`
- Rollback plan: revert only the isolated 001B allowlisted paths if a forbidden touch or evidence-shaping failure appears.
- Auto-Remote-Anchor decision: conditional.

## Source Readback

- 001A runner SHA-256: `3f08137b9dc9963b8d1b2bef2b768fb5aba6b45c13ddb428e3b7c7fc52ab2000`
- 001A result SHA-256: `12b930ce10fad79db9a396b33514811b73fa226ee4512013376bb3df597f0578`

## Probe Scores

- `small_reproduction` reference: `1.0`
- `small_reproduction` strongest non-oracle: `learned_feature_mlp_without_boundary_state` = `0.0`
- `small_reproduction` strongest learned no-boundary: `learned_feature_mlp_without_boundary_state` = `0.0`
- `small_reproduction` capacity-disabled reference: `0.0`
- `combinatorial_heldout` reference: `1.0`
- `combinatorial_heldout` strongest non-oracle: `learned_feature_mlp_without_boundary_state` = `0.0`
- `combinatorial_heldout` strongest learned no-boundary: `learned_feature_mlp_without_boundary_state` = `0.0`
- `combinatorial_heldout` capacity-disabled reference: `0.0`
- `noisy_decoy_intervention` reference: `1.0`
- `noisy_decoy_intervention` strongest non-oracle: `learned_feature_mlp_without_boundary_state` = `0.0`
- `noisy_decoy_intervention` strongest learned no-boundary: `learned_feature_mlp_without_boundary_state` = `0.0`
- `noisy_decoy_intervention` capacity-disabled reference: `0.0`

## Learned Baselines

- `learned_feature_mlp_without_boundary_state`
- `sequence_model_without_boundary_update`
- `embedding_knn_or_episodic_retrieval_baseline`
- `capacity_matched_boundary_disabled_reference`

## Leakage, Replay, Provenance

- Leakage positive controls: `6/6`
- Learned contaminated positive-control score: `1.0`
- Replay passed: `True`
- Provenance passed: `True`

## What This Does Not Prove

This does not prove mechanism validity, Gate validity, candidate behavior, agency, autonomy, consciousness, emotion, subjectivity, companion readiness, EGO readiness, runtime readiness, stable user benefit, or mainline effect.
