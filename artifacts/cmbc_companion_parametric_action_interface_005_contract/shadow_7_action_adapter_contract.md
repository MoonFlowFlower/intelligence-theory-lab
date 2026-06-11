# Shadow 7-Action Adapter Contract

Status: contract-only. No adapter implementation is authorized here.

## Purpose

The shadow adapter is a compatibility gate. It checks whether a future parametric interface can represent the existing small-action evidence without rewriting that evidence as expanded or scalable evidence.

## Required Behavior

- It must map each existing small anonymous action to exactly one anonymous `CandidateOption`.
- It must keep option IDs opaque and non-semantic.
- It must provide the same effect vector, uncertainty, and prior support references that current traces already justify.
- It must not expose public action names, action family names, natural language descriptions, renderer text, or semantic labels.
- It must emit a full `ParametricReplayTrace` with all candidate options and the complete option distribution.

## Preservation Rules

- 003 remains bounded small-action-set evidence.
- No selector patch is authorized.
- No threshold change is authorized.
- No old 003 result may be relabeled as parametric action-space support.
- Any mismatch against the old replay decisions must be reported as a shadow adapter failure, not silently patched.

## Failure Verdicts

- `shadow_adapter_invalid`
- `evidence_preservation_failed`
- `semantic_leak_risk_unresolved`
- `boundary_violation`
