# Gate Evidence Provenance Verifier 001A Historical Negative Calibration 001A Final Report

Verdict: `historical_negative_calibration_completed_diagnostic_only`

Current layer: engineering-governance / historical negative calibration for local provenance-shape verifier.
Mainline integration status: none.
Enabled status: local CLI diagnostic only.
Real trigger evidence: Claude independent hostile audit artifact accepted the verifier only as `accept_as_local_provenance_shape_checker` with caveat that it cannot catch metric degeneracy or omitted / mis-declared strongest fair baseline.
Claim ceiling: Diagnostic calibration only. No Gate pass, no mechanism validity, no baseline-immunity, no candidate success, no Route C viability, no mainline/runtime/live effect, no agency, autonomy, consciousness, emotion, stable user benefit, or EGO readiness.
Next minimal closed-loop action: draft `GATE1-REPLACEMENT-READBACK-OR-PREFLIGHT-SELECTION-001A`; do not proceed to Gate4/Gate5 from this calibration alone.

## Files Changed

- `docs/decision_log.md` appended one bounded audit acceptance pointer entry.
- `artifacts/gate_evidence_provenance_verifier_001a_historical_negative_calibration_001a/` generated this diagnostic artifact bundle.

## Commands Run

- `PYTHONPATH=src python -m gate_evidence_provenance_verifier_001a artifacts/acolb_001a` -> exit `0`, verdict `invalid_schema_or_parse_failure`.
- `PYTHONPATH=src python -m gate_evidence_provenance_verifier_001a artifacts/acp_bv_distribution_harness_001b_execution_001a` -> exit `0`, verdict `invalid_schema_or_parse_failure`.
- `PYTHONPATH=src python -m gate_evidence_provenance_verifier_001a artifacts/route_c_candidate_harness_001a` -> exit `0`, verdict `invalid_schema_or_parse_failure`.
- `PYTHONPATH=src python -m gate_evidence_provenance_verifier_001a artifacts/candidate_free_route_c_baseline_separation_probe_001a` -> exit `0`, verdict `invalid_literal_or_detached_verdict`.
- `git diff --check -- docs/decision_log.md` -> exit `0`.

## Artifacts Generated

- `artifacts/gate_evidence_provenance_verifier_001a_historical_negative_calibration_001a/calibration_results.json`
- `artifacts/gate_evidence_provenance_verifier_001a_historical_negative_calibration_001a/claim_ceiling.txt`
- `artifacts/gate_evidence_provenance_verifier_001a_historical_negative_calibration_001a/decision_log_report.json`
- `artifacts/gate_evidence_provenance_verifier_001a_historical_negative_calibration_001a/final_report.md`
- `artifacts/gate_evidence_provenance_verifier_001a_historical_negative_calibration_001a/interpretation_table.md`
- `artifacts/gate_evidence_provenance_verifier_001a_historical_negative_calibration_001a/selected_bundles.json`
- `artifacts/gate_evidence_provenance_verifier_001a_historical_negative_calibration_001a/start_state.json`
- `artifacts/gate_evidence_provenance_verifier_001a_historical_negative_calibration_001a/validation_report.json`
- `artifacts/gate_evidence_provenance_verifier_001a_historical_negative_calibration_001a/verifier_cli_outputs.jsonl`

## Calibration Results

- `artifacts/acolb_001a`: `invalid_schema_or_parse_failure` -> `schema_incompatible_diagnostic_only`.
- `artifacts/acp_bv_distribution_harness_001b_execution_001a`: `invalid_schema_or_parse_failure` -> `schema_incompatible_diagnostic_only`.
- `artifacts/route_c_candidate_harness_001a`: `invalid_schema_or_parse_failure` -> `schema_incompatible_diagnostic_only`.
- `artifacts/candidate_free_route_c_baseline_separation_probe_001a`: `invalid_literal_or_detached_verdict` -> `invalid_shape_diagnostic_only`.

Baseline results: no baseline was run; historical baseline facts were not re-evaluated in this diagnostic.
Ablation results: no ablation was run; this was a verifier CLI read-only calibration.
Replay result: no replay was run; verifier output was recorded as shape-diagnostic only.

## Validation

- JSON parse validation: `True`.
- JSONL parse validation: `True`.
- Path allowlist violations: `0`.
- Forbidden positive-claim scan violations: `0`.
- Decision-log diff check exit code: `0`.

## Stop Conditions Triggered

None recorded for the task-touched paths. Pre-existing dirty/untracked worktree items remain outside this task's write scope and were not cleared.

## What This Does Not Prove

This does not prove Gate admission, mechanism validity, baseline-immunity, candidate success, Route C viability, mainline/runtime/live effect, agency, autonomy, consciousness, emotion, stable user benefit, or EGO readiness.
