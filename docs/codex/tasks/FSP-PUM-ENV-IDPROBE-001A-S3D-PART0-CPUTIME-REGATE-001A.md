# FSP-PUM-ENV-IDPROBE-001A — S3d PART-0 CPU-time re-gate 001A

## task id
`FSP-PUM-ENV-IDPROBE-001A-S3D-PART0-CPUTIME-REGATE-001A`

## problem definition
Claude audit B1 found that the S3d PART-0 line-30 re-gate used wall-clock-derived projected CPU-hours for the stop decision, while the execution card's process-parallelism section requires the line/gate/guard to use per-unit process CPU-time (user+sys) as the contention-robust realization of per-unit `threads=1` cost. The wall-gated artifact `artifacts/FSP-PUM-ENV-IDPROBE-001A/s3d_compute_projection_line30.0.json` reported `32.00740120549966 > L=30`, but the metric basis is non-compliant and close enough to flip.

## current stage
S3d PART-0 metric-compliance repair only. This card does not authorize the S3d certificate/NULL battery.

## current layer
Engineering implementation layer: artifact-side timing instrumentation and replayable line re-gate hygiene only.

## mainline target
No EGO/runtime/mainline target. The target is the task-local S3d PART-0 projection artifact under `artifacts/FSP-PUM-ENV-IDPROBE-001A/`.

## enabled-state requirement
The re-gate runner must be directly callable from the repo checkout and must leave the full battery unlaunched. Single-thread CPU environment must remain enforced.

## real-trigger evidence requirement
The produced re-gate artifact must include a fresh run id, wall-clock start/finish timestamps, code-path hash, per-unit wall and process CPU seconds, wall/CPU flags, serial dominant-unit remeasurements, and replayed line relation.

## hypothesis
Under the execution-card-required per-unit process CPU-time gate, the S3d PART-0 projected CPU-hours are `<= L=30`.

## strongest baseline
The current wall-gated STOP artifact is the baseline: removing CPU-time accounting and reverting to the old wall-clock projection must reproduce the preserved `32.00740120549966` STOP relation.

## ablation requirement
Read the preserved `s3d_compute_projection_line30.0_wall_gate_noncompliant_v1.json` and replay its wall-clock `total_projected_cpu_hours`; it must remain `>30` with STOP relation. This ablation does not rerun science metrics.

## trace/replay requirement
The new `s3d_compute_projection_line30.0_cputime_regate.json` must be sufficient to recompute:
- total CPU-time projected hours from serialized per-component CPU seconds and units;
- disclosed wall-clock projected hours from serialized per-component wall seconds and units;
- final line relation after dominant-unit serial remeasurement replacement;
- ablation relation from the preserved wall-gated artifact.

## computed-evidence provenance gate
Every reported timing score must include producer function, input artifacts, run id, eval user/cell/member context where applicable, aggregation rule, and code-path hash. The gate verdict must be computed from callable runner output, not a literal verdict dictionary.

## acceptance gate
Acceptance requires all of:
1. Existing wall-gated artifacts are copied byte-for-byte to `*_wall_gate_noncompliant_v1` before any current artifact normalization.
2. Per-unit process CPU-time is recorded for generation, ideal, each prefix-family member, selected sklearn/GRU units, and bootstrap without changing fit/score/certificate/NULL metric logic.
3. CPU-time projection and disclosed wall projection are recomputed from serialized timings.
4. Wall/CPU ratio flags are listed for every unit where `wall/CPU > 1.25`.
5. Dominant units `ideal`, `nearest_neighbor_user_matching`, and `discounted_LS_lambda_0.95` are remeasured serially on at least three eval users from 640-799 and final gate is recomputed with mean CPU-time replacements.
6. Certificate and NULL metric files are byte/metric unchanged from the preserved wall-gated copies.
7. Banked/protected artifacts are byte-unchanged; heldout users 800-999 are not touched.
8. If final CPU projection is `<=30`, write `within_line` and STOP for Claude audit; if `>30`, write failure manifest and STOP for operator.

## claim ceiling
At most: line-30, 001B frozen-contract S3d metric-compliant PART-0 gate result. No battery evidence, certificate evidence, NULL-env evidence, environment validity, gap, mechanism, learning, agency, EGO, or readiness claim.

## stop condition
STOP with `failure_manifest.json` if preconditions fail, heldout 800-999 is touched, a protected/banked artifact mutates, certificate/NULL metrics change, the wall-gate preservation copy is missing or altered, or final CPU-time projection exceeds L=30.

## rollback plan
Rollback equals removing the CPU-time re-gate runner/artifacts and restoring pre-run `result.json` / `failure_manifest.json` from their `*_wall_gate_noncompliant_v1` copies. No science code, fit/score logic, thresholds, member set, guard k, strength, NULL MDE, or line value may be changed.

## expected changed files
- `docs/codex/tasks/FSP-PUM-ENV-IDPROBE-001A-S3D-PART0-CPUTIME-REGATE-001A.md`
- `artifacts/FSP-PUM-ENV-IDPROBE-001A/s3d_part0_cputime_regate_runner.py`
- `artifacts/FSP-PUM-ENV-IDPROBE-001A/s3d_compute_projection_line30.0_cputime_regate.json`
- `artifacts/FSP-PUM-ENV-IDPROBE-001A/*_wall_gate_noncompliant_v1.*`
- `artifacts/FSP-PUM-ENV-IDPROBE-001A/claim_ceiling`
- `artifacts/FSP-PUM-ENV-IDPROBE-001A/result.json`
- `artifacts/FSP-PUM-ENV-IDPROBE-001A/failure_manifest.json` only for STOP or historical wall-manifest normalization
- `artifacts/FSP-PUM-ENV-IDPROBE-001A/s3d_operator_bank_ops_proposal_cputime_regate.ps1`

## forbidden changes
Do not modify frozen specs, rho thresholds, strength 3.2, member set, guard `k=5`, line `L=30`, NULL MDE, fit/score/certificate/NULL metric logic, heldout 800-999, EGO runtime, UI, LLM integration, deployment, or any banked/protected artifact. Do not run git. Do not launch the full S3d battery.

## Auto-Remote-Anchor decision
Auto-Remote-Anchor: forbidden.
