# ACP-BV Executable Harness 001A Implementation Result

Task id: `ACP-BV-EXECUTABLE-HARNESS-001A`

Verdict: `acp_bv_executable_harness_001a_implemented_with_fail_able_controls`

Current layer: engineering implementation / bounded offline ACP-BV harness
implementation and control evidence only.

Mainline integration status: none.

Enabled status: local offline CLI/test runner only.

Real trigger evidence:

- start commit:
  `a699449bd42f0f67fc8cb2b5484e507a800e659c`
- start tag:
  `remote-anchor-acp-bv-harness-card-r1-revision-001a-a699449`
- prior Codex verdict:
  `acp_bv_harness_card_r1_revision_ready_for_independent_reaudit`
- Claude targeted re-audit verdict:
  `accept_for_harness_implementation_task_with_required_bindings`

## Implementation Scope

Source namespace created:

- `src/acp_bv_harness_001a/`

Test namespace created:

- `tests/acp_bv_harness_001a/`

Artifact namespace generated:

- `artifacts/acp_bv_executable_harness_001a/`

No Gate, bridge, runtime, admission, EGO mainline, companion, UI, deployment,
external service, API key, or real Gate target path was modified.

## Artifact Readback

Required artifacts generated:

- `result.json`
- `source_pins.json`
- `boundary_report.json`
- `boundary_negative_controls.json`
- `leakage_report.json`
- `baseline_matrix.json`
- `ablation_report.json`
- `replay_report.json`
- `counterfactual_controls.json`
- `clean_dirty_lookup_controls.json`
- `run_manifest.json`
- `readback.json`
- `claim_ceiling.txt`

Machine-readable acceptance gate: `acceptance_gate_passed: true`.

## Control Results

Boundary negative controls: all required controls blocked. This includes
candidate-accessible truth generator, policy-map-influenced generator,
valid-hash wrong-owner callable, generated-code/path-escape substitute, and
same-process runtime truth substitution.

Runtime mutation control:
`blocked_by_runtime_mutation_or_temporal_boundary_gap`.

Leakage controls: clean case clean, dirty cases blocked, randomized dirty cases
detected across alias/name, nested location, and value encoding variants.

Replay: candidate behavior recomputed from serialized state plus observation.
Replay-hash-only positive control blocked.

Ablations: intervention reruns regenerated traces and rescored results. Report
field editing was not used.

Counterfactual controls: harness-selected counterfactual action queries
executed and the easy-action payload was classified
`blocked_by_action_difficulty`.

## Baseline Result

Strongest scored baseline:

- baseline: `graph_cache_transition_table`
- baseline score: `0.5`
- candidate control score: `1.0`
- delta: `0.5`
- B3 classification: `mechanism_relevant_effect_candidate`

`baseline_equivalent` remains non-pass. Replay-hash-only and
candidate-self-consistency baselines were blocked as invalid evidence routes.

## Claim Ceiling

Maximum claim:

`offline_harness_implemented_with_fail_able_controls_under_this_task_distribution`

This does not prove ACP-BV validity, ACP-BV mechanism validity, Gate validity,
admission readiness, bridge readiness, runtime readiness, mainline effect,
agency evidence, consciousness, real emotion, autonomy, stable user benefit, or
EGO readiness.

## Next Minimal Closed-Loop Action

Send the implementation result and artifacts to Claude for independent hostile
implementation audit focused on fake-pass, circular truth, candidate-authored
truth, weak baselines, non-fail-able scanner, runtime mutation, and
source-boundary self-trust before any real Gate target use.
