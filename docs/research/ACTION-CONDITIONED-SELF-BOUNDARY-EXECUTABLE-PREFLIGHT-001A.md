# ACTION-CONDITIONED-SELF-BOUNDARY-EXECUTABLE-PREFLIGHT-001A

Verdict: `action_conditioned_self_boundary_executable_preflight_001a_surface_discriminative`

Current layer: `engineering implementation / offline executable preflight only`

Mainline integration status: `none`

Enabled status: `local module entrypoint, local pytest tests, local artifact generation only`

Real trigger evidence: `callable local execution produced artifacts`

Claim ceiling: `offline executable surface-preflight evidence only`

Auto-Remote-Anchor: conditional

No mechanism validity is claimed.

No Gate4, Gate5, bridge, runtime, tournament, companion, product, or EGO-mainline path is enabled.

## Bounded Task Card Readback

- Task id: `ACTION-CONDITIONED-SELF-BOUNDARY-EXECUTABLE-PREFLIGHT-001A`
- Problem definition: execute a local offline preflight for `ACSB-CONTINGENCY-BOUNDARY-UPDATE-OBJECT-001A` to test executability, failability, replay, leakage controls, baselines, ablations, and provenance.
- Current stage/layer: `engineering implementation / offline executable preflight only`
- Mainline target: none.
- Enabled-state requirement: local module entrypoint, local pytest tests, and local artifact generation only.
- Real-trigger evidence requirement: callable code must generate artifacts from computed behavior, baseline, ablation, leakage, replay, and provenance paths.
- Hypothesis: the bounded reference path should outperform cheap non-oracle baselines on heldout action-effect intervention probes, while mechanism-removing ablations degrade.
- Strongest baseline: transition-table / FSM / graph-cache / episodic traversal plus action-effect frequency without explicit self-boundary state.
- Ablation requirement: freeze boundary update, remove action-conditioned contingency, remove no-action counterfactual, shuffle linkage, replace state with recency, and reset state before probe.
- Trace/replay requirement: recompute from serialized state plus observation and intervention, not stored hashes or verdicts.
- Computed-evidence provenance gate: every score records producer function, input hash, run id, seed/context/episode ids, aggregation, code path hash, scanner path, replay path, and source hash.
- Acceptance gate: all scoped tests/checks pass, baselines do not match reference, positive controls block, replay recomputes, and claims remain bounded.
- Stop condition: `[]`
- Rollback plan: revert only the isolated allowed task paths if a forbidden touch or evidence-shaping failure appears.
- Auto-Remote-Anchor decision: conditional.

## Source Pins

- Measurement object spec: `docs/research/ACTION-CONDITIONED-SELF-BOUNDARY-MEASUREMENT-OBJECT-SPEC-001A.md`
- Measurement object spec SHA-256: `084b64076f03d603351a8131eb3c9291485fc5666cd2a39dd0a31f9eeda5c8c9`
- Prior invalid harness preserved by: `PRESERVE-ACTION-CONDITIONED-SELF-BOUNDARY-PREFLIGHT-001A-HOSTILE-AUDIT-001A`
- Inherited blocker family: oracle-target tautology, answer-bearing legal fields, omitted fair baselines, proxy leakage, replay tautology, report-shaped success, transition-table/FSM solving, graph-cache/episodic traversal solving.

## Scores

- Reference path score: `1.0`
- Strongest non-oracle baseline: `fsm_baseline` = `0.25`
- Oracle leakage positive-control baseline: `1.0`
- Reference margin over strongest non-oracle baseline: `0.75`

## Baselines

Invoked baselines: `['action_effect_frequency_without_boundary_state_baseline', 'fsm_baseline', 'graph_cache_episodic_traversal_baseline', 'majority_baseline', 'oracle_leakage_positive_control_baseline', 'random_baseline', 'recency_or_last_effect_baseline', 'transition_table_baseline']`

Missing baselines: `[]`

## Ablations

- `freeze_boundary_update`: score `0.0`, degradation `1.0`
- `remove_action_conditioned_contingency`: score `0.0`, degradation `1.0`
- `remove_no_action_counterfactual`: score `0.0`, degradation `1.0`
- `shuffle_action_effect_linkage`: score `0.0`, degradation `1.0`
- `replace_boundary_state_with_recency_state`: score `0.0`, degradation `1.0`
- `reset_state_before_probe`: score `0.0`, degradation `1.0`

## Leakage And Replay

- Leakage positive controls blocked: `6/6`
- Replay exact recomputation match: `True`
- State mutation changed behavior: `True`
- Observation mutation changed behavior: `True`
- Metadata-only mutation preserved behavior: `True`

## Provenance

Provenance verification passed: `True`

Score records: `15`

## What This Does Not Prove

This does not prove mechanism validity, Gate validity, Gate4/Gate5 validity, candidate behavior, agency, autonomy, consciousness, emotion, subjectivity, companion readiness, EGO readiness, runtime readiness, stable user benefit, or mainline effect.
