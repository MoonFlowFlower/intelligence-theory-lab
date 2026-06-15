# EVIDENCE-ADMISSION-VERIFIER-001B-UNCLEAN-STATE-CLASSIFICATION-001A

## Task Card

task_id: EVIDENCE-ADMISSION-VERIFIER-001B-UNCLEAN-STATE-CLASSIFICATION-001A

problem_definition: The standalone callable-provenance verifier repair was committed locally as `b1070058736235dc897d4fa9e693f48f06e63059`, but post-commit worktree state remained unclean because two untracked files were present: `artifacts/evidence_admission_verifier_001a_real_bundle_calibration_001a/claim_ceiling.txt` and `docs/codex/tasks/EVIDENCE-ADMISSION-VERIFIER-001A-REAL-BUNDLE-CALIBRATION-001A.md`. Classify and resolve the untracked state without changing verifier behavior.

current_stage: engineering-governance / verifier repair reproducibility hygiene only

current_layer: engineering implementation layer

mainline_target: none

enabled_state_requirement: no new enabled path; existing standalone CLI only: `python -m evidence_admission_verifier_001a <bundle> --out <artifact_dir>`

real_trigger_evidence_requirement: use current repo state after commit `b1070058736235dc897d4fa9e693f48f06e63059`

hypothesis: If the two untracked files are transient leftovers, removing them from the repo should preserve scoped verifier test behavior and no tracked evidence artifact should require preserving them. If they are durable evidence files, scoped verifier tests should still pass without them, while inspection should show they are part of the prior calibration evidence/task-card scope and should be preserved in a separate hygiene commit.

strongest_baseline: Treat all untracked files as disposable scratch if tests pass without them.

ablation_requirement: Temporarily move both untracked files outside the repo and rerun the scoped verifier tests.

trace_replay_requirement: Record exact start status, local HEAD, upstream branch HEAD, file hashes, file contents classification, tracked-reference checks, temporary-move status, pytest output, and final classification.

computed_evidence_provenance_gate: Classification must come from repo readback, file inspection, tracked-reference search, and scoped test execution with the files absent from the repo. Do not infer dependency or durability from memory alone.

acceptance_gate:
- no verifier source behavior changes
- no Gate3/Gate4/mainline/bridge/runtime files modified
- final worktree is clean
- scoped tests pass from the final tracked state
- if files are preserved, explain why they are durable evidence records and not hidden dependencies
- exact local HEAD and upstream HEAD status is recorded

claim_ceiling: repo-hygiene and reproducibility closure only. No Gate validity, mechanism validity, integrated admission readiness, mainline effect, agency, consciousness, emotion, autonomy, stable user benefit, or EGO readiness claim.

stop_condition: Stop if scoped tests depend on the untracked files but those files are not allowed to be preserved, if any verifier behavior change is required, if any forbidden path changes, or if exact upstream/local status is inconsistent.

rollback_plan: If classification fails, restore the untracked files to their original paths and preserve a blocker artifact. Do not remote-anchor.

expected_changed_files:
- `docs/codex/tasks/EVIDENCE-ADMISSION-VERIFIER-001B-UNCLEAN-STATE-CLASSIFICATION-001A.md`
- `artifacts/evidence_admission_verifier_001b_unclean_state_classification_001a/**`
- `artifacts/evidence_admission_verifier_001a_real_bundle_calibration_001a/claim_ceiling.txt`
- `docs/codex/tasks/EVIDENCE-ADMISSION-VERIFIER-001A-REAL-BUNDLE-CALIBRATION-001A.md`

forbidden_changes:
- verifier source files
- Gate3/Gate4 source or artifacts except read-only inspection
- integrated admission source
- bridge/runtime/mainline files
- unrelated tests
- unrelated artifacts

Auto-Remote-Anchor: conditional

## Remote Anchor Conditions

Remote-anchor only if final worktree is clean, scoped tests pass from tracked state, no hidden untracked dependency remains, changed files are within allowlist, and local HEAD, remote branch HEAD, local tag, and remote tag exactly match after push and tag readback.
