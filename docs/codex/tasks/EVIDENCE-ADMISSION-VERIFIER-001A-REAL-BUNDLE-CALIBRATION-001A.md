# EVIDENCE-ADMISSION-VERIFIER-001A-REAL-BUNDLE-CALIBRATION-001A

## Task Card

task_id: EVIDENCE-ADMISSION-VERIFIER-001A-REAL-BUNDLE-CALIBRATION-001A

problem_definition: Verifier Kernel v0 currently passes focused synthetic fixtures only. This does not prove it can block a preserved real false-pass bundle, classify a real candidate evidence bundle, or resist forged provenance/control rows. Calibrate v0 as-is before any Gate retrofit.

current_stage: engineering-governance / standalone evidence-admission calibration only

current_layer: engineering implementation layer, evidence-admission calibration only

mainline_target: none

enabled_state_requirement: run only through the existing standalone CLI: `python -m evidence_admission_verifier_001a <bundle_path> --out <artifact_dir>`

real_trigger_evidence_requirement:
- run one repo-preserved real false-pass / blocked pass-shaped evidence bundle
- run one repo-preserved real candidate evidence bundle
- run one adversarial forged-provenance fixture created only for calibration
- do not count synthetic unit-test fixtures as real-trigger evidence

hypothesis: If v0 is useful as an admission kernel, it should block the real false-pass bundle for computed reasons independent of verdict/report text, and produce a precise admit/block/missing-schema decision for the real candidate bundle.

strongest_baseline: A naive verdict/report-only reader trusts `result.json` or report verdict text. Record whether that naive baseline would admit the same false-pass bundle.

ablation_requirement: Run the verifier against a modified copy of the real candidate bundle with one required evidence category removed or corrupted. Preserve the computed block reason.

trace_replay_requirement: Record command, bundle path, output artifact path, verifier code hash, input file hashes, decision, block reasons, and whether report/verdict text was ignored.

computed_evidence_provenance_gate: All decisions must come from verifier code execution over bundle contents. Do not accept static expected-verdict dictionaries. Record producer_function where present, inputs, run_id, seed/context/episode IDs where present, aggregation, verifier function path, and verifier code hash.

acceptance_gate:
- existing verifier source is frozen during calibration; do not repair it in this task
- record hashes for `src/evidence_admission_verifier_001a/**` and `tests/test_evidence_admission_verifier_001a.py` before calibration outputs are interpreted
- scoped pytest still passes
- real false-pass bundle is run through the CLI
- real candidate bundle is run through the CLI
- forged-provenance positive control is run through the CLI
- if the real false-pass or forged-provenance fixture is admitted, stop and report `verifier_v0_calibration_blocked`
- if candidate is blocked, preserve the missing-schema / missing-evidence reason instead of rewriting it to pass
- no Gate3/Gate4/mainline files are modified

claim_ceiling: standalone calibration evidence only. No Gate validity, mechanism validity, admission readiness, mainline effectiveness, agency, consciousness, emotion, autonomy, or EGO readiness claim.

stop_condition: Stop if no repo-preserved real false-pass bundle can be located, if verifier code must be modified to run, if bundle selection relies only on memory or narrative, if forged-provenance is admitted, or if any forbidden path changes.

rollback_plan: Revert generated calibration artifacts if malformed or if source files were modified. Preserve a blocker report if v0 admits false-pass or forged-provenance.

expected_changed_files:
- docs/codex/tasks/EVIDENCE-ADMISSION-VERIFIER-001A-REAL-BUNDLE-CALIBRATION-001A.md
- artifacts/evidence_admission_verifier_001a_real_bundle_calibration_001a/**
- optionally stage existing v0 files only if their content hash matches the task-start hash

forbidden_changes:
- Gate3/Gate4 source
- integrated admission source
- bridge/runtime/mainline files
- verifier source modifications during calibration

Auto-Remote-Anchor: conditional

## Anchor Conditions

Anchor only if the verifier blocks the real false-pass bundle, forged-provenance positive control blocks, real candidate bundle produces a documented admit/block decision, pytest passes, changed files are within allowlist, worktree is clean after commit, and local branch hash, remote branch hash, local tag hash, and remote tag hash exactly match.

If any blocker triggers, preserve local blocker evidence if authorized, but do not remote-anchor as a successful verifier boundary.
