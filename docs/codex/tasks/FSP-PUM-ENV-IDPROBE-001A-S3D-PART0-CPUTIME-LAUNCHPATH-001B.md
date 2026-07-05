# FSP-PUM-ENV-IDPROBE-001A — S3d PART-0 CPU-time launch-path repair 001B

## task id
`FSP-PUM-ENV-IDPROBE-001A-S3D-PART0-CPUTIME-LAUNCHPATH-001B`

## problem definition
Claude audit BL1 found that the CPU-time PART-0 repair exists only in
`artifacts/FSP-PUM-ENV-IDPROBE-001A/s3d_part0_cputime_regate_runner.py`, while
the canonical launch runner `artifacts/FSP-PUM-ENV-IDPROBE-001A/s3d_battery_runner_line30.py`
still gates PART-0 preflight through wall-derived projection fields. Under contention this
can reproduce the preserved non-compliant wall STOP (`~32 > L=30`) or pass depending on host
load, so the launch path is not compliant with the execution card's per-unit CPU-time gate.

## current stage
S3d launch-path PART-0 cost-projection repair only. This card does not authorize the full
S3d certificate/NULL battery and does not create certificate/NULL result evidence.

## current layer
Engineering implementation layer: timing/projection/gate hygiene in the artifact-side runner.

## mainline target
The task-local canonical launch file
`artifacts/FSP-PUM-ENV-IDPROBE-001A/s3d_battery_runner_line30.py`, specifically its PART-0
preflight projection path before battery launch.

## enabled-state requirement
The launch runner must compute `projected_cpu_hours` from per-unit process CPU-time. The existing
runtime guard behavior remains unchanged.

## real-trigger evidence requirement
Focused tests must show a fixed wall-heavy/CPU-within-line projection does not STOP, while a
CPU-over-line projection does STOP, using the same shared projection routine callable from both
the launch runner and the audited regate runner.

## hypothesis
Moving the audited CPU-time projection math into one shared function in
`s3d_battery_runner_line30.py`, and making both runners call it, removes the launch-path B1
wall-gate nondeterminism without changing any fit/score/certificate/NULL metric logic.

## strongest baseline
The baseline is the wall-gate preflight: summing wall-derived projected hours can exceed L and
STOP even when per-unit process CPU-time is within L. The preserved wall-gated evidence remains
valid only as non-compliant failure evidence.

## ablation requirement
Removing the process CPU-time fields or reverting the launch preflight to wall-derived totals
must reproduce the B1 family: a `wall_sum > L` / `cpu_sum <= L` case can STOP. A fixed unit test
constructs this wall-heavy/CPU-within-line condition and fails if the gate uses wall totals.

## trace/replay requirement
Tests T1-T3 must cover:
- T1 shared-function deterministic recomputation from fixed measured wall/process CPU seconds
  and projected units.
- T2 B1 killer case: wall-derived hours exceed L while CPU-derived hours are within L, then a
  CPU-over-line contrast.
- T3 launch preflight instrumentation coverage: generation, ideal, selected sklearn/GRU units,
  prefix-family members, and bootstrap measurement records all carry process CPU-time fields.

## computed-evidence provenance gate
The projection/gate result must be computed from callable Python functions, not literals. The
shared function records measured wall seconds, measured process CPU seconds, projected units,
CPU-hour total, disclosed wall-hour total, wall/CPU flags, and gate relation.

## acceptance gate
Acceptance requires all of:
1. `s3d_battery_runner_line30.py` contains the single shared PART-0 CPU-time projection routine.
2. `s3d_part0_cputime_regate_runner.py` calls that shared routine and retains no second
   multiplication/summation projection routine.
3. Launch preflight records per-unit process CPU-time for generation, ideal, selected
   sklearn/GRU units, each prefix-family member, and bootstrap.
4. Launch preflight `projected_cpu_hours` means total projected CPU-hours; disclosed wall-hours
   remain separately recorded.
5. The existing `if projection["projected_cpu_hours"] > applied_line` STOP behavior is unchanged
   but now consumes CPU-hours.
6. Dominant serial remeasurement, when invoked, uses fit/validation users only (640, 720, 799)
   and does not touch heldout 800-999.
7. T1/T2/T3 pass; `py_compile` passes for both runner files.
8. Certificate/NULL scorer helpers and science constants remain byte/content unchanged.

## claim ceiling
At most: the S3d launch-path PART-0 preflight is compliant with the CPU-time line/gate metric and
B1 is repaired in the launch path as shown by focused tests. This is not battery evidence,
certificate evidence, NULL-env evidence, environment validity, gap, mechanism, agency, or EGO
evidence.

## stop condition
STOP if 001B or L=30 preconditions are not signed/banked, the audited regate runner is absent,
tests require touching certificate/NULL scoring helpers, heldout 800-999 is touched, a battery is
launched, or preserving a single projection routine requires a second launch/test-only logic path.

## rollback plan
Rollback equals restoring the launch preflight to the prior wall-derived projection path and
restoring the regate runner's prior local projection helper. Science files, certificate/NULL
helpers, rho thresholds, strength 3.2, guard k=5, member set, NULL MDE, and L=30 remain unchanged.

## expected changed files
- `artifacts/FSP-PUM-ENV-IDPROBE-001A/s3d_battery_runner_line30.py`
- `artifacts/FSP-PUM-ENV-IDPROBE-001A/s3d_part0_cputime_regate_runner.py`
- `tests/fsp_pum_env/test_s3d_part0_cputime_launchpath.py`
- `docs/codex/tasks/FSP-PUM-ENV-IDPROBE-001A-S3D-PART0-CPUTIME-LAUNCHPATH-001B.md`

## forbidden changes
Do not modify certificate/NULL scoring helpers such as `macro_balanced_accuracy`; do not change
fit/score numeric logic; do not change rho thresholds, strength 3.2, guard k=5, member set,
NULL MDE, L=30, frozen rule sources, EGO runtime, UI, LLM integration, deployment, banked
artifacts, or preserved `*_wall_gate_noncompliant_v1` evidence. Do not run git. Do not run the
full battery.

## Auto-Remote-Anchor decision
Auto-Remote-Anchor: forbidden.
