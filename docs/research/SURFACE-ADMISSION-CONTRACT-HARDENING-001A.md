# SURFACE-ADMISSION-CONTRACT-HARDENING-001A

Verdict: `contract_hardened_pass`.

Verdict enum reconciliation: prior top-level `result.json` verdict
`blocked_preserved_false_positive_surfaces` is preserved as a contract mismatch.
The reconciled top-level verdict must be one of:

- `contract_hardened_pass`
- `contract_refused`
- `invalid_contract_harness`

Layer: engineering-governance / harness-contract hardening / no mechanism surface.

Mainline integration status: not integrated. This contract does not enter EGO mainline, runtime, bridge, Gate5, tournament, UI, LLM integration, or deployment.

Enabled status: local validator contract only. No new mechanism candidate, no new surface, and no old harness repair is authorized.

Real trigger evidence: preserved negative controls from:

- `artifacts/preserve_composite_ctsr_hostile_audit_001a/result.json`
- `artifacts/preserve_ctsr_solvability_inversion_preflight_001a_hostile_audit_001a/result.json`
- `artifacts/preserve_action_conditioned_self_boundary_preflight_001a_hostile_audit_001a/result.json`

Claim ceiling: engineering-governance / evidence-hygiene only.

Auto-Remote-Anchor: conditional only if the contract validator passes against all three preserved negative controls, the old artifacts remain unchanged, the scoped commit is clean, and exact remote branch/tag readback can be completed safely.

No mechanism candidate is implemented or scored by this task. No mechanism score is produced.

## Computed Validator Readback

Artifact result: `artifacts/surface_admission_contract_hardening_001a/result.json`.
Artifact readback: `artifacts/surface_admission_contract_hardening_001a/readback.json`.

Readback:

- all preserved negative controls blocked: yes;
- G1 through G14 passed: yes;
- failed gates: none;
- static task-id denylist used: false;
- anti-blacklist renamed positive-control blocked by features: yes;
- task-id-only counter-control not rejected by blacklist: yes;
- reason-specific positive-controls triggered expected gates: yes;
- reason-specific counter-controls did not trigger expected gates: yes;
- mechanism score produced: false;
- candidate or new surface designed: false;
- preserved input artifacts modified: false.

## Bounded Task Card

- Task id: `SURFACE-ADMISSION-CONTRACT-HARDENING-001A`
- Problem definition: future surface-admission tasks must be blocked before execution when their harness permits semantic answer encoding, evaluator privilege, missing fair challengers, replay tautology, or static pass reports.
- Current stage/layer: engineering-governance / harness-contract hardening / no mechanism surface.
- Mainline target: none; this is an offline validator contract.
- Enabled-state requirement: callable local validator only.
- Real-trigger evidence requirement: validator must read the preserved negative controls as read-only inputs.
- Hypothesis: a feature-based validator can reject the preserved false-positive families without task-id denylisting.
- Strongest baseline: a static name scanner or task-id denylist could appear to pass while missing benign semantic answer aliases.
- Ablation requirement: static pass and non-fail-able boolean claims must be refused by positive control.
- Trace/replay requirement: replay must be rejected when it recomputes labels with the same function/path as label generation or reads answer-bearing state.
- Computed-evidence provenance gate: reports must identify producer functions, protected input hashes, and generated machine-readable artifacts.
- Acceptance gate: G1 through G14 below must pass.
- Claim ceiling: engineering-governance / evidence-hygiene only.
- Stop condition: if any preserved negative control is not blocked, result is `invalid_contract_harness`; if verdict discipline, G13, or G14 is not satisfied, result is `contract_refused` or `invalid_contract_harness` instead of pass.
- Rollback plan: revert the isolated validator package, test file, contract document, and generated artifact directory.
- Expected changed files: `src/surface_admission_contract_hardening_001a/`, `tests/test_surface_admission_contract_hardening_001a.py`, this document, and `artifacts/surface_admission_contract_hardening_001a/`.
- Forbidden changes: mechanism candidates, new surfaces, frozen artifacts, old invalid harnesses, EGO mainline, runtime, Gate5, bridge, UI, LLM integration, deployment, and API keys.
- Auto-Remote-Anchor decision: conditional.

## Required Gates

G1. Oracle-target tautology must be detected when oracle, scorer, replay, or target generation share the same answer function.

G2. Legal-field semantic answer encoding must be detected by semantic probes, not only forbidden-name matching.

G3. Simple legal baselines equaling oracle must block admission.

G4. Evaluator privilege must block admission when oracle/scorer has rule, label, target, hidden function, or forbidden-alias access not granted to fair baselines.

G5. Missing fair challengers must be detected by synthesizing all required simple legal baselines before admission:

- `single_legal_field_lookup`
- `legal_tuple_lookup`
- `state_action_table`
- `action_index_context_key_arithmetic`
- `effect_vector_lookup`
- `nearest_neighbor_legal_observations`

G6. Replay tautology must be detected when replay recomputes the target with the same function/path as label generation or reads answer-bearing state.

G7. Benign-named answer aliases must be detected even when path fragments do not include target, answer, label, hidden, oracle, or forbidden names.

G8. Same-state proxy leaks through metadata, context, action-index, query-offset, or similar fields must block admission.

G9. Static pass reports and non-fail-able boolean claims must be refused. Literal pass verdicts, `passed=true`, `verified=true`, perfect scores without callable provenance, and clean reports without positive controls are not evidence.

G10. All three preserved negative controls must be blocked by the validator.

G11. The top-level result verdict must conform to the allowed verdict enum, and
the prior `blocked_preserved_false_positive_surfaces` value must remain recorded
as a contract mismatch rather than silently disappearing.

G12. Anti-blacklist readback must show that a renamed positive-control remains
blocked by detected features while a task-id-only counter-control is not rejected
by static blacklist behavior.

G13. Reason-specific positive-controls and counter-controls must be computed:
positive-controls must trigger their expected gates, and counter-controls must
not trigger those gates.

G14. Scope and preservation guards must remain true: no mechanism score, no
candidate, no new mechanism surface, and no old preserved input artifact drift.

## Future Surface Admission Contract

A future surface-admission task may not proceed to candidate, Gate4, Gate5, tournament, bridge, runtime, or EGO mainline work unless it provides a machine-readable surface bundle that passes the validator and includes:

- protected input hashes;
- callable label, oracle, baseline, ablation, leakage, replay, and scorer producers;
- the synthesized challenger suite listed in G5;
- positive controls for semantic answer aliases and leakage scans;
- replay recomputation from non-answer-bearing serialized state plus observation;
- failure-path tests proving the validator can block false positives;
- claim ceiling fields that remain below mechanism validity.

Passing this contract would only mean the surface-admission harness cleared these engineering-governance blockers. It would not prove mechanism validity, Gate4 validity, candidate behavior, agency, autonomy, consciousness, emotion, EGO readiness, runtime readiness, or mainline effect.

## Prior Negative Evidence Cited

- COMPOSITE-CTSR is preserved as negative evidence because the legal interface was unsolvable and success depended on forbidden or answer-bearing alias fields.
- CTSR solvability inversion is preserved as negative evidence because fair task-B-only legal baselines reached oracle-level accuracy through context-key/query-offset arithmetic and related legal challengers.
- ACTION-CONDITIONED-SELF-BOUNDARY is preserved as negative evidence because oracle-target tautology, legal `actuator_effects[selected_action]` answer encoding, benign answer aliases, same-state proxy fields, and replay tautology invalidated the original admission claim.

## What This Does Not Prove

This contract does not prove mechanism validity, Gate4 validity, candidate behavior, surface validity, agency, autonomy, consciousness, emotion, EGO readiness, runtime readiness, companion readiness, stable user benefit, or mainline effect.
