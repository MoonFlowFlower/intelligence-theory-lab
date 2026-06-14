# PRESERVE-ACTION-CONDITIONED-SELF-BOUNDARY-PREFLIGHT-001A-HOSTILE-AUDIT-001A

## Verdict

`block as invalid_harness`

This record preserves the hostile audit of `ACTION-CONDITIONED-SELF-BOUNDARY-PREFLIGHT-001A`.
The original preflight reported `admitted_surface_preflight`; that verdict is superseded for
downstream use by this invalid-harness preservation record.

## Layer

Engineering governance / invalid-harness preservation / no mechanism execution.

## Mainline Status

- Mainline integration status: none.
- Enabled status: no runtime, bridge, tournament, Gate5, candidate, or EGO mainline path enabled.
- Real trigger evidence: user-provided hostile audit plus read-only probe over frozen artifacts.
- Claim ceiling: invalid-harness preservation and route-governance evidence only.

## Prior Negative Evidence Lineage

The frozen preflight itself cited this failure family as prior negative evidence:

- `artifacts/preserve_composite_ctsr_hostile_audit_001a/result.json`
- `artifacts/preserve_ctsr_solvability_inversion_preflight_001a_hostile_audit_001a/result.json`
- `artifacts/preserve_claude_audit_legal_interface_oracle_block_001a/result.json`

This preservation record keeps that lineage active and blocks the action-conditioned preflight from
being reused as surface-admission evidence.

## Preserved Blocking Issues

B1. Oracle-target tautology: `_legal_oracle_prediction` and `_target_from_downstream` reduce to
`_class_from_delta(actuator_effects[selected_action])` on the frozen surface.

B2. Baseline omission: simple legal baselines reach oracle-level accuracy, including
`effect_vector_lookup`, `sensor_phase x selected_action`, and `sensor_phase x action_index`.

B3. Margin collapse: reported oracle-vs-baseline margin becomes `0.0` once any of those fair
baselines is included.

B4. Semantic answer-bearing legal field: `actuator_effects[selected_action]` deterministically
encodes the target.

B5. Proxy-channel gap: same-state pair validation equalizes `pre_state`, but metadata/context proxy
fields are not equivalently controlled.

B6. Replay tautology: replay recomputes from a legal field that already encodes the answer function.

B7. Leakage guard gap: name-fragment positive control catches forbidden-name aliases but benign-named
answer aliases can pass the scan.

B8. Field-registry gap: nested path enumeration is syntactic and does not detect semantic answer
encodings.

## Read-Only Probe Summary

Probe path:
`artifacts/preserve_action_conditioned_self_boundary_preflight_001a_hostile_audit_001a/audit_probe.py`

The probe parses frozen files only. It does not import or execute the frozen preflight runner.

Key readback:

- Original verdict: `admitted_surface_preflight`
- Preserved audit verdict: `invalid_harness`
- Oracle equals target for all episodes: `true`
- `effect_vector_lookup` accuracy: `1.0`
- `sensor_phase x selected_action` accuracy: `1.0`
- `sensor_phase x action_index` accuracy: `1.0`
- Heldout key coverage for both `sensor_phase` table baselines: `32/32`
- Margin if fair baseline included: `0.0`
- Benign named answer alias path: `legal_state_observation.controllability_outlook`
- Benign named answer alias scan passed: `true`
- Benign named answer alias accuracy: `1.0`
- Frozen field registry answer-bearing fields: `[]`
- Frozen field registry `legal_tuple_deterministically_encodes_target`: `false`
- Frozen replay passed with prediction match rate: `1.0`

Full probe stdout is preserved at:
`artifacts/preserve_action_conditioned_self_boundary_preflight_001a_hostile_audit_001a/audit_probe_stdout.txt`

## Non-Blocking Caveats

- The audit and this preservation are read-only with respect to the frozen action-conditioned run.
- Some ablations appear to rerun rather than mutate stored labels.
- This does not prove the controllability/self-boundary mechanism family false.
- A repaired harness would require a separate bounded task card.

## Downstream Usage Rule

`ACTION-CONDITIONED-SELF-BOUNDARY-PREFLIGHT-001A` is not admissible surface-admission evidence.
It must not authorize candidate, Gate4/Gate5, bridge, runtime, tournament, or EGO-mainline work.
Successor tasks must cite this preservation artifact as prior negative evidence before proposing a
new gate, bridge, or implementation.

## Changed Files

- `docs/research/PRESERVE-ACTION-CONDITIONED-SELF-BOUNDARY-PREFLIGHT-001A-HOSTILE-AUDIT-001A.md`
- `artifacts/preserve_action_conditioned_self_boundary_preflight_001a_hostile_audit_001a/audit_probe.py`
- `artifacts/preserve_action_conditioned_self_boundary_preflight_001a_hostile_audit_001a/audit_probe_stdout.txt`
- `artifacts/preserve_action_conditioned_self_boundary_preflight_001a_hostile_audit_001a/claim_ceiling.txt`
- `artifacts/preserve_action_conditioned_self_boundary_preflight_001a_hostile_audit_001a/readback.json`
- `artifacts/preserve_action_conditioned_self_boundary_preflight_001a_hostile_audit_001a/result.json`

## Forbidden Changes

The preservation task does not modify:

- `src/action_conditioned_self_boundary_preflight_001a/`
- `tests/test_action_conditioned_self_boundary_preflight_001a.py`
- `artifacts/action_conditioned_self_boundary_preflight_001a/`
- `docs/research/ACTION-CONDITIONED-SELF-BOUNDARY-PREFLIGHT-001A.md`
- old CTSR/COMPOSITE negative evidence
- Gate4/Gate5/tournament/bridge/runtime/EGO-mainline files
- candidate implementation files

## Next Minimal Closed-Loop Action

Run scope/readback checks, commit the additive preservation record if clean, and perform conditional
remote-anchor publication only if all task-card gates remain satisfied.

## What This Does Not Prove

This does not prove mechanism failure, controllability/self-boundary impossibility, Gate4/Gate5
invalidity, candidate behavior, agency, autonomy, consciousness, emotion, subjectivity, companion
readiness, EGO readiness, runtime readiness, stable user benefit, or any mechanism score.
