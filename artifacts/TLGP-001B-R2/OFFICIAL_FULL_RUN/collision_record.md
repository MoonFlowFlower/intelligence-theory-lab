# TLGP-001B-R2-FULL-ORCHESTRATION-AND-RUN-001 Collision Record

## Scope

- Task type: isolated official TLGP-001B-R2 full-run orchestration plus conditional execution.
- Current layer: engineering implementation + mechanism-hypothesis preflight execution.
- Real objective: replace the existing `--full` block stub with a prereg-verified, CUDA-active, replayable full-run pipeline and launch it only if all pre-run gates pass.
- Mainline integration status: none.
- Enabled status: isolated offline TLGP-001B-R2 official full run only.
- Claim ceiling: bounded offline candidate-free TLGP-001B-R2 evidence under the frozen preregistration only.
- Auto-Remote-Anchor: forbidden.

## Bounded Audit

- Problem definition risk: treating an implementation or smoke command as official evidence. Mitigation: official evidence is written only under `artifacts/TLGP-001B-R2/OFFICIAL_FULL_RUN/` after all required rungs, scanners, leakage, replay, and integrity checks complete.
- Strongest baseline explanation: cheap lookup/count-table/majority/no-context paths may saturate Rung 1. Mitigation: callable Rung 1 scanner records cheap baseline saturation and context ablation remains load-bearing.
- Strongest invalidity reason: `--full` could shrink the frozen experiment or train/evaluate on CPU despite CUDA availability. Mitigation: dry-run self-check compares frozen prereg counts/seeds/grid and requires model/tensor CUDA probes on `cuda:0`.
- Falsifier for current framing: prereg SHA mismatch, non-clean `AGENTS.md` readback, forbidden-path tracked drift, CUDA available but inactive, experiment shrinkage, replay mismatch, leakage controls failing, or source delivered/executed mismatch.
- Insufficient evidence even if complete: a terminal R2 verdict does not prove learning-as-mechanism, agency, self, feeling, subjectivity, intelligence, autonomy, EGO readiness, or mainline effect.
- Mechanism-vs-behavior classification: this task tests the frozen TLGP-001B-R2 offline question only; it is not EGO mainline or subject-validation evidence.

## Candidate Approaches

### Candidate A: Minimal CLI Unblock

- Evidence produced: `--full --dry-run` accepted and `--full` writes a result-shaped artifact.
- Strongest cheap baseline that could match it: report-shaped success from static dictionaries or partial smoke data.
- Leakage/hard-coding risk: high; terminal verdict could become an else branch or static literal.
- Smallest falsifying test: replay from saved traces must recompute all verdict inputs without retraining.
- Expected failure mode: creates pass-shaped artifacts without running the frozen rungs.

### Candidate B: Strongest Shortcut/Baseline Full Run

- Evidence produced: full split construction, ideal/lower-reference scores, scanner reports, and cheap ablations without training every frozen model seed/grid.
- Strongest cheap baseline that could match it: lookup/count-table/no-context baselines can explain Rung 1, and undertraining can mimic underpowered/inconclusive outcomes.
- Leakage/hard-coding risk: medium if scanner outputs are callable, but the official model path would still be incomplete.
- Smallest falsifying test: source self-check must detect missing model seeds, capacities, rungs, ablations, or primary-family adjudication.
- Expected failure mode: faster but violates no-shrinkage and cannot be official.

### Candidate C: Frozen Full Orchestration

- Evidence produced: prereg readback, complete frozen split/count/seed/grid execution, Rung 0/1/2/3 summaries, primary-family adjudication, diagnostic MLP records, context/shuffle ablations, leakage positive/negative controls, trace manifest, no-retrain replay, tamper/integrity checks, source manifest, and exact terminal verdict from `compute_verdict`.
- Strongest cheap baseline that could match it: cheap baselines may explain Rung 1; the scanner and ablation reports must preserve that fact instead of hiding it.
- Leakage/hard-coding risk: lower if all score/verdict fields are computed from callable paths and trace rows.
- Smallest falsifying test: `--full --dry-run` must fail on any prereg mismatch, CUDA inactive path, or frozen experiment shrinkage before training starts.
- Expected failure mode: long runtime or invalid/inconclusive scientific result; both are bounded outcomes, not implementation success claims.

## Selected Approach

Select Candidate C. Candidate A and B cannot satisfy the official no-shrinkage, callable evidence, CUDA, replay, leakage, and claim-ceiling requirements.

## Minimal Validation Before Full Run

- `artifacts/TLGP-001B-R2/prereg.json` canonical SHA equals `6e61a831c6f287c10c25cccbb09a40671410cd4805214dbd91d62528b2c3d5a7`.
- `git diff --ignore-space-at-eol -- AGENTS.md` is empty.
- HEAD is `c142443e9b85a2087e569a3f74a9f8fdd05ac32c` on `codex/meta-theory-scaffold`.
- Index is empty.
- CUDA is available and selected as `cuda:0`.
- GRU and Transformer parameters and training/query tensors are on `cuda:0` in dry-run probe.
- Dry-run self-check reports all frozen rungs, seeds, counts, primary families, diagnostic family, capacity grid, and verdict enum unchanged.

## Acceptance Signals

- Official artifacts are written under `artifacts/TLGP-001B-R2/OFFICIAL_FULL_RUN/`.
- `result.json` contains one of the seven frozen terminal verdicts.
- `replay_report.json` recomputes verdict-relevant metrics and the official verdict from saved traces without retraining.
- `leakage_report.json` includes planted, renamed planted, and clean controls.
- `rung1_scanner_report.json` records callable cheap baseline results and `cheap_baseline_saturation`.
- `ablation_report.json` records context and shuffle collapse results.
- `source_manifest.json` reports delivered source hashes equal executed source hashes.
- `SHA256SUMS.txt` hashes the official bundle.
- No git add, commit, push, tag, or remote-anchor action occurs.

## Stop Conditions

- `blocked_prereg_sha_mismatch`
- `blocked_scope_cleanup_not_clean`
- `blocked_cuda_available_but_not_used`
- `blocked_forbidden_drift`
- `blocked_full_orchestration_selfcheck_failed`
- `blocked_replay_or_trace_integrity_failed`
- `blocked_leakage_control_failed`
- `blocked_runtime_interrupted_incomplete`
- `blocked_other_exact_reason`

## Rollback Plan

Rollback is limited to files created or modified by this task under:

- `src/tlgp_001b_r2/**`
- `artifacts/TLGP-001B-R2/OFFICIAL_FULL_RUN/**`

The frozen preregistration, historical TLGP-001A artifacts, TLGP-001B-R1 artifacts, R1 audit artifacts, task cards, global config, `AGENTS.md`, and `CLAUDE.md` must remain untouched.
