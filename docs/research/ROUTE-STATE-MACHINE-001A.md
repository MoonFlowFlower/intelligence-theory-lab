# ROUTE-STATE-MACHINE-001A

## Scope

This is a bounded repo-local control-plane artifact for route state and closure
packet validation. It is not a new mechanism roadmap, not a mechanism
experiment, and not an EGO runtime/mainline integration.

## Layer and claim ceiling

- Layer: engineering implementation / route-governance evidence hygiene.
- Mainline integration status: not integrated; local repo CLI only.
- Enabled status: local `python -m route_state_machine_001a.routectl` commands.
- Real trigger evidence: local CLI validation over serialized route JSON under
  `artifacts/ROUTE-STATE-MACHINE-001A/routes/`.
- Claim ceiling: local route-governance validation only; no mechanism validity,
  theory pressure, agency, autonomy, subjectivity, consciousness, EGO readiness,
  companion readiness, or mainline effect.

## Frozen state enum

- `PROPOSED`
- `REGISTERED`
- `READY_TO_IMPLEMENT`
- `IMPLEMENTING`
- `RUN_ATTEMPTED`
- `EVIDENCE_PACKET_READY`
- `CLOSURE_REVIEW_REQUIRED`
- `ADJUDICATED`
- `NEXT_FRONTIER_ASSIGNED`
- `REDESIGN_REQUIRED`
- `RERUN_REQUIRED`
- `OPS_FIX_REQUIRED`
- `TOMBSTONED`

## Frozen closure type enum

- `THEORY_PRESSURE`
- `INSTRUMENT_INVALID`
- `BASELINE_EQUIVALENCE`
- `IMPLEMENTATION_DEFECT`
- `OPERATION_ERROR`
- `LEAKAGE_OR_CHEATING`
- `METRIC_DEGENERACY`
- `UNDERPOWERED`
- `GOVERNANCE_STOP`
- `INCONCLUSIVE`
- `SCOPE_MISMATCH`
- `ARTIFACT_ONLY`

## Local CLI

```powershell
$env:PYTHONPATH="src"
python -m route_state_machine_001a.routectl validate --root .
python -m route_state_machine_001a.routectl status --root .
python -m route_state_machine_001a.routectl dashboard --root .
```

`validate` writes
`artifacts/ROUTE-STATE-MACHINE-001A/validation_report.json` through callable
code. `status` and `dashboard` re-run local validation and print summaries.

`transition` is intentionally deferred in this first local version. A safe
transition writer would need a separate authorization boundary because it would
mutate route state.

## Validation rules in 001A

Validation fails if:

1. a route has an invalid `current_state`;
2. `CLOSURE_REVIEW_REQUIRED` lacks `closure.json`;
3. `closure.json` lacks `closure_type`;
4. `closure.json` lacks non-empty `allowed_next_actions`;
5. `closure.json` lacks non-empty `forbidden_next_actions`;
6. `closure.json` lacks `claim_ceiling.max`;
7. `THEORY_PRESSURE` is claimed without baseline, ablation, replay, and
   provenance marked `present`;
8. `INSTRUMENT_INVALID` sets `theory_pressure_authorized=true`;
9. `ARTIFACT_ONLY` sets `mechanism_evidence_authorized=true`;
10. `IMPLEMENTATION_DEFECT` allows `start_new_mechanism_route`;
11. unresolved `CLOSURE_REVIEW_REQUIRED` exists while roadmap-like changed files
    are detected, unless the file is part of this task's own authorized path
    set.

## Historical PUM-ENV-v0 example packet

The included PUM-ENV-v0 packet is a conservative historical example. Current
repo readback supports the instrument-invalid classification through:

- `docs/research/FSP-STAGE-LEDGER.md` L-005: P0.2 closed as
  `INVALID_INSTRUMENT`;
- `docs/research/FSP-STAGE-LEDGER.md` L-011: PUM-ENV terminal
  `INVALID_INSTRUMENT`, with PUM-dependent routes blocked on that substrate;
- `docs/codex/tasks/FSP-PUM-ENV-IDPROBE-001A-S3D-V0-TOMBSTONE-001A.md`:
  S3d v0 tombstoned as an invalid latent-mechanism gate and not a theory or
  mechanism falsification;
- `artifacts/FSP-PUM-ENV-IDPROBE-001A/s3d_v0_closure_record.json`:
  machine-readable historical closure record with verdict
  `S3D_V0_TOMBSTONED`.

The packet does not infer theory failure, mechanism invalidity, or fresh
adjudication. Unknowns are represented explicitly in the packet where not
established by this task.

## What this does not prove

This does not prove route correctness, mechanism validity, theory pressure,
learning/adaptation, agency, autonomy, subjectivity, consciousness, EGO
readiness, companion readiness, production readiness, or mainline effect.
