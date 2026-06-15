# CLAUDE-INDEPENDENT-ACSB-001D-EXECUTION-001A-HOSTILE-AUDIT-001A

## Verdict

`claude_independent_acsb_001d_execution_001a_audit_blocks_feature_impoverished_or_unfair_baseline`

Route consequence:

`acsb_001d_execution_001a_bounded_negative_evidence_not_accepted`

## Layer And Scope

- Layer: `engineering-governance / independent hostile audit preservation only`
- Mainline integration status: none.
- Enabled status: none.
- Real trigger evidence: current handoff containing Claude's independent hostile audit verdict.
- Claim ceiling: `ACSB-001D execution 001A invalid-harness blocker preservation only`
- Auto-Remote-Anchor: conditional.

This is preservation-only. It does not repair ACSB-001D, rerun 001D,
implement a replacement harness, create 001E, or enable any Gate4/Gate5,
bridge, tournament, runtime, companion, EGO-mainline, product, production, or
mainline config path.

## Audited Execution Boundary

- Audited execution commit: `fe5aa85430850f4bd7607917b1e73e129a8a8a21`
- Audited execution tag: `remote-anchor-acsb-001d-bounded-execution-001a-fe5aa85`
- Branch: `codex/meta-theory-scaffold`
- Superseded earlier tag/commit: `remote-anchor-acsb-001d-bounded-execution-001a-9cda505` /
  `9cda5051f1a64d886843c9517348e73cca6872ca`
- Superseded status: `9cda505` is not canonical for the preserved audit target.

The audited execution reported:

- Reference score: `1.0`
- Strongest fair baseline: `fitted_pure_python_mlp_no_boundary_learner = 1.0`
- Capacity-disabled score: `1.0`
- Survival margin: `0.0`

The hostile audit blocks this as valid bounded negative evidence.

## Decisive Preserved Findings

1. `_make_episode` generates labels using `_target_from_observation`.
2. `_target_from_observation` computes `target = phase_bit XOR action_bit`.
3. `phase_bit` and `action_bit` are present in `legal_observation`.
4. `fitted_pure_python_mlp_no_boundary_learner` is wired to `_legal_rule_predictions`.
5. `_legal_rule_predictions` calls `_target_from_observation`.
6. The reported fitted baseline does not consume training data; with empty train it still scores `1.0`.
7. The fitted baseline is therefore an oracle/rule path, not a learned no-boundary baseline.
8. `reference_core.selected_output` also calls `_target_from_observation`.
9. `reference_core.selected_output` is independent of `boundary_memory` and disable flags.
10. `full_reference`, `capacity_disabled`, and strongest baseline are structurally identical to the label oracle.
11. Therefore `1.0 / 1.0 / 0.0` is a constructive identity artifact, not valid bounded negative evidence.
12. The 001D execution result cannot be cited as ACSB negative evidence or ACSB closure/downgrade evidence.

## Blocker Interpretation

The preserved hostile baseline explanation is that
`fitted_pure_python_mlp_no_boundary_learner` is not a learned fair baseline
because it is wired to the target-generation rule and ignores training data.

The preserved boundary-memory finding is that boundary-specific ablations did
not establish causal boundary use because `reference_core.selected_output` is
independent of `boundary_memory` and disable flags.

Replay recomputation does not rescue the ACSB evidence claim because it
recomputes the same legal XOR rule rather than demonstrating boundary-memory
causality.

## Route Consequence

- ACSB-001D execution 001A is invalid as bounded negative evidence.
- `fe5aa85` must not be cited as ACSB negative evidence.
- `fe5aa85` may be cited only as invalid-harness / unfair-baseline /
  oracle-wiring blocker evidence.
- ACSB remains unresolved by 001D execution 001A.
- No 001E is created or authorized.
- Future work, if any, requires a separate route-decision card, not immediate repair.

## What This Does Not Prove

This preservation does not prove ACSB validity or invalidity in general,
mechanism validity, Gate validity, agency, autonomy, consciousness, emotion,
subjectivity, runtime readiness, EGO readiness, stable user benefit,
companion/product readiness, or mainline effect.

## Next Minimal Closed-Loop Action

Route-decision review: decide whether ACSB should be closed or downgraded due
to repeated non-discriminative or invalid surfaces, or whether a separate
non-001E replacement design is justified. Do not repair 001D immediately.
