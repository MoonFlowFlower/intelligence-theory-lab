# ITL-DEV-BENCH-001B - Oracle Headroom Repair

## Task Card

Task id: ITL-DEV-BENCH-001B-ORACLE-HEADROOM-REPAIR

Problem definition: Repair the ITL-DEV-BENCH-001A upper-bound/headroom contract after smoke run `RUN_20260629T151318Z` produced `oracle_no_headroom_benchmark_invalid`, with `graph_cache` outperforming the hidden-state oracle on the primary reward aggregate.

Current stage / layer: benchmark validation and engineering repair only.

Mainline target: isolated `itl_devbench` benchmark runner, metrics, oracle, graph-cache audit, reports, and tests. No EGO runtime, product, companion, persona, or candidate-mechanism tuning.

Enabled-state requirement: the existing smoke CLI remains the trigger: `python -m itl_devbench.eval.run_matrix --config configs/itl_devbench_001a.yaml --smoke`.

Real-trigger evidence requirement: a new timestamped smoke run must emit `manifest.json`, `trace.jsonl`, `metrics.json`, `baseline_scores.json`, `baseline_scores_by_stage.json`, `oracle_headroom_report.json`, `leakage_audit_graph_cache.json`, `diagnosis_oracle_headroom.md`, `replay_report.json`, `audit_report.json`, and `report.md`.

Hypothesis: The invalid headroom verdict is caused by a mismatch between the oracle policy and the primary metric objective, plus missing metric-orientation and by-stage headroom diagnostics. Repairing the oracle to optimize the same reward objective over legal hidden-state paths should either restore oracle upper-bound validity or produce computed evidence that the benchmark objective contract is invalid.

Strongest baseline: `graph_cache` can exploit observation/action/outcome memory within each episode. Its access must remain observation-only and scoped to the current seed/stage/episode.

Ablation requirement: keep all eight minimal-loop variants runnable and unchanged. This task does not change candidate PE, memory, planner flags, or policy.

Trace/replay requirement: preserve the existing trace contract and replay reproducibility from config, seeds, actions, rewards, done flags, info, event hash chain, and metrics hash.

Computed-evidence provenance gate: metric orientation, stage aggregates, oracle headroom, graph-cache leakage audit, diagnosis, replay, audit, and report verdicts must be computed from traces/source/config, not hand-written verdicts.

Acceptance gate: focused devbench pytest tests pass; new oracle/headroom tests pass; replay succeeds; audit succeeds; oracle is valid upper bound by stage and aggregate, or the run is explicitly declared invalid with computed evidence; graph-cache access contract is documented and audited; candidate code is not modified.

Claim ceiling: benchmark/headroom repair only. No candidate, mechanism, learning, agency, Joi, or EGO claim.

Stop condition: stop as `benchmark_objective_contract_invalid` if oracle cannot be made a valid upper bound without changing the task objective. Stop as `invalid_due_graph_cache_leakage` if graph-cache reads hidden state or future outcomes. Stop as `oracle_headroom_unresolved` if oracle remains below graph-cache after repair.

Rollback plan: revert only files changed for `ITL-DEV-BENCH-001B` under `docs/tasks/`, `src/itl_devbench/eval/`, `src/itl_devbench/agents/oracle.py`, tests, and new `artifacts/ITL-DEV-BENCH-001A/RUN_*`/`latest` outputs. Do not delete or rewrite historical runs, especially `RUN_20260629T151318Z`.

Expected changed files: this task card, oracle/headroom/audit/report/metrics modules, new headroom tests, and new generated artifacts under `artifacts/ITL-DEV-BENCH-001A/`.

Forbidden changes: no minimal-loop candidate tuning, no environment redesign before diagnosing oracle/metric mismatch, no EGO/Joi/persona/UI/runtime integration, no hidden-state access for candidates or graph-cache, no old artifact rewrite, no push/tag.

Auto-Remote-Anchor: forbidden.

## Bounded Audit Before Implementation

Real objective: restore an auditable upper-bound/headroom contract, not improve candidate results.

Problem-definition risk: if the primary metric is `total_reward`, oracle must maximize `total_reward`, not shortest path to a beneficial object or survival alone.

Strongest baseline explanation: `graph_cache` performed better because its patrol/cache behavior accidentally avoids bad hidden-state choices and survives longer; a greedy oracle can perform worse despite hidden-state access if it does not optimize the metric.

Strongest invalidity reason: if graph-cache state leaks across seed/rule-seed/stage or uses future outcomes, previous baseline result is invalid. If it is fair and oracle still trails after objective alignment, the benchmark upper-bound contract remains unresolved.

Falsifier for repair: by-stage or aggregate report shows any frozen baseline primary score greater than oracle without a documented metric exception.

Insufficient evidence: aggregate-only pass, replay-only pass, or a report verdict without by-stage headroom and graph-cache leakage audit.

Mechanism vs resemblance: this task tests benchmark validity and auditability only. It does not test or validate learning.

Risk checks:
- Hard-coding: oracle may read hidden state as an explicit upper-control, but should optimize objective generically through legal action rollouts, not per-stage hand coding.
- Leakage: graph-cache audit must inspect trace/source for hidden-state strings, future outcome fields, and reset scope.
- Weak baseline: graph-cache remains a frozen baseline and can still saturate candidate comparisons.
- Schema split: add by-stage outputs derived from the same trace metrics.
- Claim inflation: reports remain benchmark/headroom wording only.

Minimal validation: failing tests for missing orientation/stage/headroom/leakage outputs, oracle-upper-bound smoke assertions, focused devbench pytest, smoke run, replay, audit, and artifact readback.

Acceptance signal: a new smoke run with `oracle_headroom_report.json` showing `oracle_upper_bound_valid` or an explicit computed invalid verdict; no candidate source changes.

## Collision Record

Candidate approach A - fix only report labels:
- Evidence produced: report no longer says oracle invalid.
- Strongest cheap baseline that could match it: unchanged graph-cache still beats oracle.
- Leakage / hard-coding risk: high; this hides the mismatch.
- Smallest falsifying test: compare oracle and graph-cache primary score by stage.
- Expected failure mode: false closure.

Candidate approach B - objective-aligned hidden-state oracle:
- Evidence produced: oracle uses hidden-state rollouts over legal actions to optimize the same primary metric orientation used in metrics.
- Strongest cheap baseline that could match it: graph-cache may still match on simple stages but should not exceed the oracle on the same deterministic objective.
- Leakage / hard-coding risk: contained because oracle is explicitly labeled as headroom control.
- Smallest falsifying test: deterministic smoke by-stage oracle score must be at least every frozen baseline for higher-is-better primary metric.
- Expected failure mode: environment reward objective itself is malformed or horizon-limited oracle remains weak.

Candidate approach C - redesign environment:
- Evidence produced: possibly harder benchmark with more oracle headroom.
- Strongest cheap baseline that could match it: graph-cache/lookup may still saturate if symbolic state is too direct.
- Leakage / hard-coding risk: high if done before diagnosing the mismatch.
- Smallest falsifying test: old mismatch remains unexplained.
- Expected failure mode: moving target and lost diagnostic value.

Selected approach: B. The task explicitly forbids environment redesign until oracle/metric mismatch is diagnosed and forbids candidate tuning.
