# ITL-DEV-BENCH-001D-CANDIDATE-FACTORIAL-RUN

## Task Card

Task id: ITL-DEV-BENCH-001D-CANDIDATE-FACTORIAL-RUN

Problem definition: Run the frozen `minimal_loop` 000-111 factorial variants against the 001C task-family generator and compute by-family causal contribution signals from trace-derived metrics. This is an evaluation run only.

Current stage/layer: candidate factorial evaluation under benchmark contract only.

Mainline target: `itl_devbench` offline benchmark artifact path.

Enabled-state requirement: 001C generator config enabled, frozen baselines included, all minimal-loop variants included.

Real-trigger evidence requirement: fresh smoke run, trace emitted, replay succeeds, audit succeeds, and 001D factorial artifacts are computed from metrics.

Hypothesis: factorial interactions may show a bounded candidate signal under the 001C generator, but the result may also be no signal, noncausal ablation pattern, or baseline saturation.

Strongest baseline: frozen graph-cache and other frozen baselines under the same 001C trace contract.

Ablation requirement: compute `111 - 011`, `111 - 101`, `111 - 110`, and `111 - max(110,101,011)` by family and aggregate.

Trace/replay requirement: deterministic trace/replay contract from 001C must remain valid.

Computed-evidence provenance gate: candidate scores, baseline comparison, interactions, and verdict must be derived from `metrics.json`, `baseline_scores_by_family.json`, `family_metric_summary.json`, replay report, audit report, and source hash checks.

Acceptance gate: scoped pytest passes; all variants and baselines run; replay/audit pass; candidate/generator/baseline source hashes unchanged; interaction metrics computed.

Claim ceiling: candidate factorial evidence only; at most bounded offline candidate-signal evidence under the specified 001C trace/replay contract.

Stop condition: stop on replay failure, audit failure, candidate source hash drift, generator/baseline source drift, missing variants/baselines, or missing computed interaction artifacts.

Rollback plan: do not alter candidate/generator/baseline sources; if evaluation artifacts fail, preserve the run as negative evidence and repair only eval/report plumbing in a later task.

Expected changed files: this task card, a scoped eval postprocessor, and 001D tests/artifacts.

Forbidden changes: no edits to `src/itl_devbench/agents/minimal_loop.py`, `src/itl_devbench/envs/task_family_generator.py`, `src/itl_devbench/envs/families.py`, `src/itl_devbench/envs/developmental_grid.py`, or frozen baseline agent files.

Auto-Remote-Anchor: forbidden.

## Bounded Audit

Real objective: produce replayable factorial evidence artifacts, not a candidate win.

Strongest shortcut explanation: frozen baselines may still match or exceed the best candidate variant by family.

Strongest invalidity risk: the verdict could be hand-written after inspecting scores, or source drift could invalidate the frozen-candidate condition.

Falsifying result for the current framing: replay/audit fails, a required variant/baseline is absent, or source hashes drift for candidate/generator/baseline sources.

Insufficient evidence: aggregate-only scores without by-family interactions, or interaction deltas not tied to metrics.

Mechanism status: this tests only factorial candidate behavior under a benchmark contract; it does not validate a mechanism.

Leakage/hardcoding checks: preserve graph-cache audit, source hashes, trace replay, and audit forbidden-claim checks.

Acceptance signal: `candidate_factorial_scores_by_family.json`, `candidate_factorial_interactions.json`, `baseline_comparison_by_family.json`, `report.md`, replay report, and audit report agree on a computed 001D verdict.

## Collision Record

Approach A, reuse 001C report only: cheap, but fails 001D because interaction deltas and 001D verdict are absent.

Approach B, eval-only postprocessor over a fresh 001C generator run: produces the required factorial artifacts without touching candidate/generator/baselines. Failure mode is that the result may be no signal or baseline saturated.

Approach C, redesign candidate policy or generator: forbidden by task constraints and would invalidate the frozen evaluation.

Selected approach: Approach B.
