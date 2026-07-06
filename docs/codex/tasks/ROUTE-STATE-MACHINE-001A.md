# ROUTE-STATE-MACHINE-001A

## Task id

`ROUTE-STATE-MACHINE-001A`

## Problem definition

Implement a bounded repo-local route control-plane artifact that records route
state, closure packets, allowed/forbidden next actions, and validation outcomes
without creating a new mechanism roadmap, running a mechanism experiment, or
upgrading historical route closures into mechanism/theory claims.

## Current stage

Engineering-governance implementation only. PUM-ENV v0/S3d v0 is historical
negative/closure evidence and may be used only as a conservative example packet
if current repo readback supports the classification.

## Current layer

Engineering implementation layer / route-governance evidence hygiene only.

## Mainline target

No EGO mainline target. Local repo CLI and artifacts only.

## Enabled-state requirement

`python -m route_state_machine_001a.routectl validate --root .`,
`status`, and `dashboard` must execute locally with standard-library Python.
`transition` may be implemented only if scoped and safe; otherwise defer.

## Real-trigger evidence requirement

Real trigger evidence is limited to the requested local CLI commands reading the
repo-local route artifact tree and producing `validation_report.json` through a
callable code path.

## Hypothesis

A small JSON-backed route state machine and validator can reduce false route
advancement by blocking invalid state names, missing closure review packets,
unsafe closure-action combinations, closure-claim inflation, and roadmap-like
changes while a closure remains unresolved.

## Strongest baseline / shortcut explanation

A static checklist or manual route status note could appear to provide the same
governance value without executable validation. This task must therefore produce
callable validation code and tests for failure paths, not only a prose status
document.

## Ablation requirement

Unit tests must remove or mutate each required closure safety field and observe
validation failure. No mechanism ablation is authorized.

## Trace/replay requirement

No mechanism replay is authorized. Route-governance replay is limited to
deterministic re-validation from serialized JSON route state plus closure packet
plus supplied/simulated changed-file list.

## Computed-evidence provenance gate

`validation_report.json` must be produced by callable code and include:

- `producer_function`
- `input_artifacts`
- `run_id`
- `aggregation_rule`
- `code_path_hash`
- `validation_errors`
- `validation_warnings`
- `verdict`

## Acceptance gate

The first local version is accepted only if all of the following hold:

1. The task card exists at `docs/codex/tasks/ROUTE-STATE-MACHINE-001A.md` and is
   read back before implementation.
2. The implementation stays within:
   - `docs/codex/tasks/`
   - `docs/research/`
   - `src/`
   - `tests/`
   - `artifacts/`
3. No `.github/`, `scripts/`, or new root-level governance directory is created.
4. State enum includes exactly:
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
5. Closure types include exactly:
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
6. `routectl` supports `status`, `validate`, and `dashboard`.
7. Validation fails when:
   - a route has an invalid `current_state`;
   - `CLOSURE_REVIEW_REQUIRED` lacks `closure.json`;
   - `closure.json` lacks `closure_type`;
   - `closure.json` lacks non-empty `allowed_next_actions`;
   - `closure.json` lacks non-empty `forbidden_next_actions`;
   - `closure.json` lacks `claim_ceiling.max`;
   - `THEORY_PRESSURE` is claimed without baseline, ablation, replay, and
     provenance marked `present`;
   - `INSTRUMENT_INVALID` sets `theory_pressure_authorized=true`;
   - `ARTIFACT_ONLY` sets `mechanism_evidence_authorized=true`;
   - `IMPLEMENTATION_DEFECT` allows `start_new_mechanism_route`;
   - unresolved `CLOSURE_REVIEW_REQUIRED` exists while roadmap-like changed
     files are detected, unless the file is part of this task's own authorized
     path set.
8. Tests include at least the requested valid and invalid cases.
9. Required commands run:

   ```powershell
   $env:PYTHONPATH="src"
   python -m route_state_machine_001a.routectl validate --root .
   python -m route_state_machine_001a.routectl status --root .
   python -m route_state_machine_001a.routectl dashboard --root .
   pytest tests/route_state_machine_001a -q
   git status --short
   ```

## Claim ceiling

Local route-governance control-plane artifact and validator only. No mechanism
validity, theory pressure, agency, autonomy, subjectivity, consciousness, EGO
readiness, companion readiness, production integration, or mainline effect.

## Stop condition

Stop and report if:

- an existing dirty path overlaps planned task paths;
- the task card cannot be saved or read back;
- repo instructions conflict with this task;
- implementation would require mechanism experiment execution;
- historical PUM-ENV v0 cannot be conservatively represented from current repo
  readback;
- validation cannot produce a callable-code provenance report;
- planned changes would touch unauthorized paths.

## Rollback plan

Before commit, rollback is deleting only the files created by this task under
the authorized paths. Do not modify, delete, revert, or stage pre-existing dirty
user work.

## Expected changed files

- `docs/codex/tasks/ROUTE-STATE-MACHINE-001A.md`
- `docs/research/ROUTE-STATE-MACHINE-001A.md`
- `src/route_state_machine_001a/__init__.py`
- `src/route_state_machine_001a/routectl.py`
- `src/route_state_machine_001a/state_machine.py`
- `src/route_state_machine_001a/validator.py`
- `tests/route_state_machine_001a/test_validator.py`
- `artifacts/ROUTE-STATE-MACHINE-001A/schemas/route_state.schema.json`
- `artifacts/ROUTE-STATE-MACHINE-001A/schemas/closure_packet.schema.json`
- `artifacts/ROUTE-STATE-MACHINE-001A/routes/PUM-ENV-v0/state.json`
- `artifacts/ROUTE-STATE-MACHINE-001A/routes/PUM-ENV-v0/closure.json`
- `artifacts/ROUTE-STATE-MACHINE-001A/routes/PUM-ENV-v0/events.jsonl`
- `artifacts/ROUTE-STATE-MACHINE-001A/STATUS.md`
- `artifacts/ROUTE-STATE-MACHINE-001A/validation_report.json`

## Forbidden changes

- No mechanism roadmap.
- No new mechanism experiment.
- No EGO mainline runtime, UI, companion behavior, LLM integration, AIRI
  integration, deployment, API keys, emotion systems, proactive behavior,
  relationship learning, or self-awareness simulation.
- No `.github/`.
- No `scripts/`.
- No new root-level governance directory.
- No push, tag, or remote-anchor.
- No commit unless explicitly authorized after final validation and staged-path
  readback.

## Auto-Remote-Anchor decision

Forbidden.

## Collision record

### Candidate A: minimal implementation

- Evidence produced: local JSON schemas, one route packet, validator, and CLI
  outputs.
- Strongest cheap baseline that could match it: a prose checklist with manual
  review.
- Leakage / hard-coding risk: validator could key on PUM-ENV path only or tests
  only.
- Smallest falsifying test: construct another in-memory route with a mutated
  closure packet and verify the same callable validator blocks it.
- Expected failure mode: under-specified route schema lets unsafe closure/action
  combinations through.

### Candidate B: strongest baseline / shortcut explanation

- Evidence produced: static docs plus a status table.
- Strongest cheap baseline that could match it: the docs themselves.
- Leakage / hard-coding risk: all verdicts become hand-written assertions.
- Smallest falsifying test: delete a required closure field and observe no
  executable failure.
- Expected failure mode: no discriminative control-plane effect; false closure
  can continue.

### Candidate C: mechanism-faithful implementation

- Evidence produced: route graph plus typed transitions and closure-action
  guards.
- Strongest cheap baseline that could match it: a simpler static validator for
  the current artifacts.
- Leakage / hard-coding risk: overbuilding a roadmap or implicitly creating
  mechanism route policy.
- Smallest falsifying test: unresolved closure plus roadmap-like changed file
  must block unless the changed file is in this task's authorized path set.
- Expected failure mode: scope creep into route strategy or theory-pressure
  claims.

### Selected approach

Candidate C in a minimal local-only form: implement only the route state enum,
closure type enum, JSON validator, `status`/`validate`/`dashboard` CLI, tests,
schemas, and one conservative PUM-ENV-v0 historical example packet. Defer any
broader transition automation unless it can remain safely scoped.
