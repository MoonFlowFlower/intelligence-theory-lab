# BATCH-ENV-HEADROOM-SCOUT-002A-FULL-HARNESS-CARD-RELATIONAL_CONTRAST_BUDGET_PROBE

Problem definition: Build a full candidate-free baseline-first harness for promoted sketch `relational_contrast_budget_probe` to test whether the preliminary micro-probe gap survives stronger callable baselines and controls.
Current stage/layer: candidate-free full baseline-first harness task card draft only / engineering-governance / Phase-0 environment portfolio scouting
Mainline target: none
Enabled-state requirement: no runtime/mainline/admission/bridge path enabled
Real-trigger evidence requirement: Run the full harness from generated episodes and write machine-readable baseline/oracle/control artifacts.
Hypothesis: The environment surface may retain measurable oracle-vs-cheap-baseline separation under a full baseline battery.
Strongest baseline: transition_table
Preliminary oracle score: 0.883417548044231
Preliminary strongest cheap baseline score: 0.3388257153474545
Preliminary gap: 0.5445918326967765

Baseline requirements:
- budget_limited_belief_state_planner
- greedy_information_gain_or_uncertainty_planner_under_budget
- graph_lookup
- transition_table
- successor_map
- fsm_planner
- passive decoder
- size-only
- degenerate controls

Ablation requirement: Rerun the full harness with oracle query budget reduced, adaptive query disabled, passive-only view, graph-cache-only view, and leakage-positive controls.
Trace/replay requirement: Replay must recompute predictions from serialized visible state plus legal query trace; stored prediction or hash-only replay must fail.
Computed-evidence provenance gate: Every score must record producer_function, input artifacts, run_id, seed/context/episode IDs, aggregation rule, and code path hash.
Acceptance gate: Only candidate-free full-harness candidate promotion if oracle is high, strongest cheap baseline remains at least 0.08 below oracle, passive/degenerate/size-only remain low, graph-cache does not saturate, oracle is budget-faithful, and train/test split resists memorization.
Claim ceiling: No headroom confirmation from this task card. Candidate-free full baseline-first harness candidate only. No candidate authorization, no route tournament, no Gate1 pass, no mechanism validity, no runtime/mainline effect.
Stop condition: Stop on direct decode, graph-cache saturation, passive decodability, metric degeneracy, non-budget-faithful oracle, or gap < 0.08.
Rollback plan: Delete only the new full-harness draft artifacts for this sketch; do not mutate prior negative evidence or MINIMAL-ENV-SPEC-001A.

Expected changed files:
- scripts/research/relational_contrast_budget_probe_full_baseline_first_harness.py
- tests/research/test_relational_contrast_budget_probe_full_baseline_first_harness.py
- artifacts/relational_contrast_budget_probe_full_baseline_first_harness/

Forbidden changes:
- WM-P / VSB-C / CSL implementation
- candidate implementation
- route tournament
- runtime/mainline/admission/bridge wiring
- MINIMAL-ENV-SPEC-001A edits
- push/tag/remote-anchor

Auto-Remote-Anchor: forbidden
Candidate implementation authorized: False
Route tournament authorized: False
