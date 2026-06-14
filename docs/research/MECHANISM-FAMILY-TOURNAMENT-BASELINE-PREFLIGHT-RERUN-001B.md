# MECHANISM-FAMILY-TOURNAMENT-BASELINE-PREFLIGHT-RERUN-001B

Verdict: `mechanism_family_tournament_baseline_preflight_rerun_001b_all_closed_or_needs_redesign`

Layer: engineering-governance / no-candidate callable baseline-preflight rerun.

Mainline integration status: not integrated.

Enabled status: no runtime, no bridge/admission, no Gate4 replacement, no candidate, no tournament execution, no trigger path.

Claim ceiling: no-candidate baseline-preflight evidence only. No mechanism validity, no Gate4 validity, no candidate behavior, no tournament result, no runtime readiness, no bridge/admission readiness, and no EGO readiness.

Auto-Remote-Anchor: conditional.

## Bounded Task Card

- Task id: `MECHANISM-FAMILY-TOURNAMENT-BASELINE-PREFLIGHT-RERUN-001B`
- Problem definition: rerun baseline preflight against the anchored executable-surface contract without candidate code or tournament execution.
- Current stage/layer: engineering-governance evidence execution.
- Mainline target: none; not integrated.
- Enabled-state requirement: no runtime, no bridge/admission, no Gate4 replacement, no candidate, no tournament execution, and no trigger path.
- Real-trigger evidence requirement: consume the parent `family_surface_contract.json` artifact and run callable target resolvers, metrics, baselines, leakage scans, and positive controls.
- Hypothesis: cheap faithful baselines can close fixture-like surfaces before any candidate family is authorized.
- Strongest baseline: exact lookup, table/memorization, retrieval, static decoder, static formula/rule, trace/order/key, and family-specific shortcut baselines.
- Ablation requirement: positive-control shortcut masking is represented through recomputable baseline records; no candidate ablation is run.
- Trace/replay requirement: every score stores serialized inputs and is recomputable through `recompute_baseline_score`.
- Computed-evidence provenance gate: scores record producer function, module path, code hash, inputs, run id, seed, record/context IDs, predictions, targets, threshold, aggregation, and contribution.
- Acceptance gate: parent anchor readable, six family contracts loaded from artifact, callables valid, baselines run, positive controls fail as expected, provenance verifies, no forbidden paths.
- Claim ceiling: no-candidate baseline-preflight evidence only. No mechanism validity, no Gate4 validity, no candidate behavior, no tournament result, no runtime readiness, no bridge/admission readiness, and no EGO readiness.
- Stop condition: parent anchor failure, missing callable target or metric, missing threshold, leakage/positive-control failure, provenance gap, forbidden file path, candidate/tournament/runtime/Gate4 path.
- Rollback plan: remove only isolated 001B source/test/report/artifact paths; do not rewrite parent artifacts or prior results.
- Expected changed files: isolated 001B source package, focused test, research report, and artifacts under `artifacts/mechanism_family_tournament_baseline_preflight_rerun_001b/`.
- Forbidden changes: candidate code, candidate score, tournament execution, Gate4 repair/rerun or replacement design, runtime, bridge/admission, EGO-mainline, LLM/RAG/UI/companion path.
- Auto-Remote-Anchor decision: conditional.

## Parent Anchor Readback

- Parent commit: `614b3414e0a9417ebca65096e067f6c003addfa5`
- Parent tag: `remote-anchor-mechanism-family-tournament-executable-surface-contract-001a-614b341`
- Local tag hash: `614b3414e0a9417ebca65096e067f6c003addfa5`
- Remote tag hash: `614b3414e0a9417ebca65096e067f6c003addfa5`
- Tag type: `commit`
- Parent tag exact match: `True`
- Remote branch exact parent at read time: `True`
- Parent is ancestor of current HEAD: `True`

## Family Decisions

| family ID | best faithful cheap baseline | score | threshold | decision |
|---|---:|---:|---:|---|
| `causal_world_model_control` | `exact_lookup` | `1.0` | `0.8` | `closed_by_faithful_cheap_baseline` |
| `jepa_like_latent_prediction` | `exact_lookup` | `1.0` | `0.8` | `closed_by_faithful_cheap_baseline` |
| `replay_consolidation_adaptation` | `exact_lookup` | `1.0` | `0.8` | `closed_by_faithful_cheap_baseline` |
| `self_boundary_controllability_model` | `exact_lookup` | `1.0` | `0.8` | `closed_by_faithful_cheap_baseline` |
| `viability_value_gated_prediction_action_loop` | `exact_lookup` | `1.0` | `0.8` | `closed_by_faithful_cheap_baseline` |
| `social_latent_inference_without_partner_id_lookup` | `exact_lookup` | `1.0` | `0.8` | `closed_by_faithful_cheap_baseline` |

## Survivors / Closed / Needs Redesign

- Survivors: `[]`
- Closed families: `['causal_world_model_control', 'jepa_like_latent_prediction', 'replay_consolidation_adaptation', 'self_boundary_controllability_model', 'viability_value_gated_prediction_action_loop', 'social_latent_inference_without_partner_id_lookup']`
- Needs-redesign families: `[]`
- Future tournament eligibility: `False`

## Positive Controls

- `target_leak` expected `target_leak_detected` observed `target_leak_detected` failed as expected `True`.
- `partner_id_lookup` expected `partner_id_lookup_shortcut_detected` observed `partner_id_lookup_shortcut_detected` failed as expected `True`.
- `table_lookup` expected `faithful_table_lookup_reaches_threshold` observed `faithful_table_lookup_reaches_threshold` failed as expected `True`.
- `static_formula` expected `static_formula_shortcut_detected` observed `static_formula_shortcut_detected` failed as expected `True`.
- `missing_threshold` expected `missing_threshold` observed `missing_threshold` failed as expected `True`.
- `missing_callable_target` expected `missing_callable_target` observed `missing_callable_target` failed as expected `True`.

## Forbidden-Action Guard

- Candidate code created: `False`
- Candidate score produced: `False`
- Tournament execution attempted: `False`
- Gate4 repair/rerun attempted: `False`
- Runtime/mainline path created: `False`
- Forbidden files modified: `[]`

## Stop Conditions

- None.

## Explicit Boundary Statement

This is no-candidate baseline-preflight evidence only. It created no candidate code, no candidate score, no tournament execution, no Gate4 repair/rerun, no Gate4 replacement design, no runtime or EGO-mainline path, and no mechanism-validity evidence.

## What This Does Not Prove

- mechanism validity
- Gate4 validity
- candidate behavior
- candidate score
- tournament result
- runtime readiness
- bridge/admission readiness
- agency
- subjectivity
- consciousness
- emotion
- autonomy
- companion readiness
- EGO readiness

## Next Minimal Closed-Loop Action

Route away from tournament execution for these surfaces unless a separate bounded redesign creates families that survive cheap faithful baselines under the same callable provenance gate.

## Remote Anchor Status

- Remote anchor performed: `False`
