# FSP-PUM-ENV-IDPROBE-001A — S3d SHOULD-WIN-NULL-ENV Battery Execution 001A

Status: **AUTHORIZED for Codex implementation ONLY AFTER the operator signs the line-raise.**
Self-gating: if the precondition below is not met, the executor STOPs before any battery work.

## task id
`FSP-PUM-ENV-IDPROBE-001A-S3D-BATTERY-EXEC-001A`

## precondition — signed line-raise (BLOCKING GATE)
The 12.0 CPU-h S3d line is `operator-adjustable only by signed decision note` (spec §6). Before
any work, the executor MUST confirm all of:
1. `docs/codex/tasks/FSP-PUM-ENV-IDPROBE-001A-S3D-BUDGET-DECISION-001A.md` §8 is filled and
   committed with **Option B**, a concrete line value **L** (auditor-recommended **L = 30.0**),
   operator name, and date.
2. The variance-probe evidence is banked (commit banking
   `s3d_part0_variance_probe.json`), and the 12-line STOP commit `17cce05` is in history.
If any is missing → write `s3d_battery_precondition_failure_manifest.json` and STOP. Do NOT set a
line yourself; read L from the signed note.

## problem definition / objective
Execute the **frozen** `FSP-PUM-ENV-IDPROBE-001A-S3D-SHOULD-WIN-NULL-ENV-SPEC-001A` (the 8th
frozen blob — read-only rule source) under the operator-authorized budget line L, producing the
should-win certificate + NULL-env battery evidence it pre-registers. This card authorizes
**execution and the compute-line change only**; it does not define or alter any science
threshold.

## current stage
S3d full certificate battery (post-STOP, post-probe, under operator-raised line L).

## hypothesis (from the frozen spec — do not restate thresholds here)
Per S3D-SHOULD-WIN-NULL-ENV-SPEC-001A: the should-win cert cells pass their pre-registered ρ
headroom thresholds for every one of the 18 members incl. the ideal, AND the NULL-env shows
metric ≤ chance + 0.005 for every member incl. the ideal (no false headroom). Pass/fail and the
exact thresholds are the spec's, not this card's.

## baseline / ablation (from the frozen spec)
The 18-member battery already includes the mandatory challenger families (graph-cache:
count_table / transition_table / successor_map / fsm_planner / episodic_traversal; retrieval:
rag_k5 / nearest_neighbor; ls-online; obs-decoders; seq ± action; degenerates) plus the 2
cert-only degenerate variants and the BASE-invariance regression. Use them exactly as frozen; do
not add, drop, or re-weight members.

## line-raise (the ONLY threshold change authorized)
- Apply L (from the signed note) to BOTH the PART-0 re-gate and the runtime guard, as a single
  isolated change (update `S3D_CPU_HOUR_LIMIT` to L **or** thread L as one explicit parameter —
  no second logic path, no test-only path). The applied value MUST equal the signed L.
- Provenance firewall (spec §6): L is a compute-budget convention, NOT claim-bearing; never cite
  it against the S2 tractability line.

## PART-0 re-gate under L (before launching the full run)
Re-run the PART-0 projection under L and write a **new** artifact
`s3d_compute_projection_line{L}.json` (do NOT overwrite the banked `s3d_compute_projection.json`).
If projection > L → STOP with failure manifest (do not shrink grid/member/threshold). Expected:
~17–19 CPU-h ≤ 30, so it passes; still perform the gate for protocol fidelity.

## runtime guard during the run
Cumulative per-completed-unit CPU-h trace; > L → STOP immediately with failure manifest; a
**second** breach returns to the operator (do not auto-raise again). The CPU-h that feeds this
guard MUST be the contention-robust per-unit measure defined in the parallelism section below —
NOT a raw parallel wall-clock, which can be inflated by co-scheduling.

## process parallelism (freed-machine speedup — spec-permitted, no spec change)
GPU is prohibited (spec §6). The freed machine is used via the spec-permitted
`cell/member-level process parallelism`:
- Run battery units (per member × cell, and NULL-env) as independent worker processes to cut
  **wall-clock**. Each worker keeps threads=1 (OMP/MKL/OpenBLAS/NumExpr/torch=1, torch cpu).
- Determinism is non-negotiable: each unit fully independent, own seeded RNG, no shared mutable
  state. Parallel results MUST be **bit-identical to serial** — assert this on ≥1 sampled unit
  (recompute serially, compare metric to full precision). Parallelism is a scheduling
  optimization ONLY; it may never change any certificate/NULL metric.
- Do NOT oversubscribe: `N_workers × 1 thread ≤ physical cores`. Record N.
- CPU-h accounting under contention (direct evidence: the S3d variance probe found co-scheduled
  memory-bound units — exact filter, NN — inflate per-unit wall-clock up to ~2.4×). The budget
  line/gate/guard is a bound on **compute consumed**, so record per unit BOTH wall-clock AND
  CPU-time (process user+sys). Use **per-unit CPU-time** as the contention-robust realization of
  the spec's "per-unit threads=1 wall-clock" for the line/gate/guard, and report the
  wall-clock-based sum alongside it (disclosed). Flag any unit with `wall/CPU-time > 1.25`. If the
  contention-robust CPU-h approaches L, re-measure the dominant units in isolation (serial)
  before any STOP. This is a disclosed operationalization for auditor adjudication, NOT a change
  to the frozen spec's definition.
- Report: N, total wall-clock (parallel), total contention-robust CPU-h, wall-clock-based CPU-h,
  per-unit both-timings, contention flags, and the serial-equivalence assertion result.

## trace / replay requirement (per spec)
Per S3D-SHOULD-WIN-NULL-ENV-SPEC-001A trace/replay contract: per-member cert cells, ρ vs
per-cell ideal anchor, NULL-env rows, BASE-invariance regression hashes, CPU-h trace,
`code_path_hash`, `single_thread_environment`. Replay must reconstruct verdicts from recorded
trace without hidden future info.

## acceptance gate
Battery ran to completion under L (or STOPped on a real, preserved failure); all spec-required
artifacts emitted (below); the applied line equals the signed L; the banked 12-line STOP
artifacts are byte-unchanged; NO change to any ρ threshold / NULL MDE / cert-cell / 18-member
definition / frozen spec; `s3d_certificate_report.json` + `s3d_null_env_report.json` now present
and internally consistent with the trace. Parallelism criteria: `N_workers × 1 ≤ physical cores`
recorded; parallel results asserted **bit-identical to serial** on ≥1 sampled unit; contention-
robust CPU-h and wall-clock-based CPU-h both reported; no metric depends on N.

## evidence artifacts (under artifacts/FSP-PUM-ENV-IDPROBE-001A/)
`s3d_compute_projection_line{L}.json`, `s3d_certificate_report.json`, `s3d_null_env_report.json`,
`result.json` (or spec-named equivalent), `trace.jsonl`/`.csv`, `baseline_comparison.json`,
`ablation_report.json`, `replay_report.json`, `failure_manifest.json` if anything fails,
`claim_ceiling` field. No artifact = no evidence.

## claim ceiling
At most: **bounded S3d should-win + NULL-env instrument evidence under the frozen contract, at
line L.** NOT environment-validity, baseline-power, headroom-as-mechanism, gap, mechanism,
learning, agency, EGO-mainline, or companion-readiness. A pass certifies the instrument behaves
as pre-registered; it does not validate the environment or any candidate.

## stop condition
STOP + failure manifest if: precondition unmet; PART-0 re-gate > L; runtime guard > L (2nd breach
→ operator); any heldout 800–999 touched; BASE-invariance regression fails; NULL false-headroom
breach (`FAIL_NULL_FALSE_HEADROOM`, all S3d results void — preserve, do not patch); any required
change to a frozen science threshold. Preserve every failure artifact; do not patch failures into
passes.

## rollback plan
The line change is isolated and revertible (one constant/parameter). All new artifacts are new
files; no banked artifact is overwritten. Rollback = revert the line change + delete the new
battery artifacts; the banked 12-line STOP and probe evidence are untouched. Codex runs no git.

## dev rules / forbidden
Read the frozen spec as read-only rule source; do NOT modify it, its thresholds, cert cells, the
18-member set, NULL MDE, or any other frozen file except the single isolated line value. Do NOT
run git; emit a proposed operator bank-ops script (HEAD-pin + git reset + allowlist + staged
count + zero-deletion + per-file Get-FileHash + scoped `git commit -- paths` + no push) and STOP
for Claude audit. Forbidden: threshold tuning after seeing results; second logic/test-only path;
heldout/label leakage; using future observations; rewriting banked artifacts; auto re-raising L.
