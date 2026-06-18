# BASELINE-FIRST-HARNESS-001A-R1 Final Report

Verdict: `rejected_no_headroom_baseline_saturated`

Current layer: engineering-governance / Phase-0 candidate-free environment-headroom harness

Mainline integration status: none

Enabled status: no runtime/mainline/admission/bridge path enabled

Real trigger evidence: actual harness run over frozen MINIMAL-ENV-SPEC-001A with spec SHA256 readback, freeze readback, provenance rows, callable baselines, oracle controls, leakage control, replay recomputation, and final_verdict.json.

Claim ceiling: candidate-free Phase-0 environment-headroom/no-headroom evidence only. No Gate1 pass. No mechanism validity. No candidate feasibility. No runtime/mainline effect. No agency/autonomy/consciousness/EGO readiness.

Files changed:
- scripts/research/baseline_first_harness_001a.py
- scripts/research/baseline_battery_001a.py
- scripts/research/minimal_env_spec_loader_001a.py
- scripts/research/evidence_provenance_001a.py
- scripts/research/oracle_budget_faithfulness_001a.py
- scripts/research/strategy_class_alignment_001a.py
- tests/research/test_baseline_first_harness_001a.py
- artifacts/baseline_first_harness_001a/

Commands run:
- `python scripts/research/baseline_first_harness_001a.py --spec docs/research/MINIMAL-ENV-SPEC-001A.md --freeze docs/research/MINIMAL-ENV-SPEC-001A.freeze.json --required-spec-sha256 bf48145b165c5c847cecd7ecda6c2a78818ce326c44f5ad92be391d003daf658 --out artifacts/baseline_first_harness_001a`
- `python scripts/research/baseline_first_harness_001a.py --spec docs/research/MINIMAL-ENV-SPEC-001A.md --freeze docs/research/MINIMAL-ENV-SPEC-001A.freeze.json --required-spec-sha256 bf48145b165c5c847cecd7ecda6c2a78818ce326c44f5ad92be391d003daf658 --out artifacts/baseline_first_harness_001a_self_check_tmp --self-check`
- `python -m pytest tests/research/test_baseline_first_harness_001a.py`

Artifacts generated:
- artifacts/baseline_first_harness_001a/source_readback.json
- artifacts/baseline_first_harness_001a/evidence_table.jsonl
- artifacts/baseline_first_harness_001a/baseline_registry.json
- artifacts/baseline_first_harness_001a/score_summary.json
- artifacts/baseline_first_harness_001a/seed_power_report.json
- artifacts/baseline_first_harness_001a/leakage_report.json
- artifacts/baseline_first_harness_001a/replay_recompute_report.json
- artifacts/baseline_first_harness_001a/oracle_budget_faithfulness_report.json
- artifacts/baseline_first_harness_001a/strategy_class_alignment_report.json
- artifacts/baseline_first_harness_001a/final_verdict.json
- artifacts/baseline_first_harness_001a/final_report.md

Required score summary:
- visible_channel_oracle_score: 1.0
- answer_key_diagnostic_oracle_score: 1.0
- strongest_fair_baseline_score: 1.0
- strongest_fair_baseline_producer: budget_limited_belief_state_planner
- passive_family_max_score: 0.4000000000000001
- degenerate_predictor_max_score: 0.18892239142997486
- size_only_sweep_max_score: 0.4000000000000001
- exhaustive_legal_query_score: 1.0
- six_graph_cache_challenger_scores: {"count_table": 1.0, "episodic_traversal": 1.0, "fsm_planner": 1.0, "graph_lookup": 1.0, "successor_map": 1.0, "transition_table": 1.0}
- lookup_imitation_max_score: 1.0
- oracle_minus_baseline_margin: 0.0
- equivalence_band: 0.03
- seed_power_status: not_applicable_no_headroom_baseline_saturated

Required control summary:
- visible_channel_oracle_budget_faithfulness_result: passed
- oracle consumed-field manifest: ["budget_state", "episode_id", "legal_action_space", "legal_channel_responses.probe_action_trace_mod.value_if_queried", "legal_channel_responses.probe_boundary_pressure.value_if_queried", "legal_channel_responses.probe_perturbation_phase.value_if_queried", "legal_channel_responses.probe_rule_family.value_if_queried", "legal_channel_responses.probe_viability_bucket.value_if_queried", "observable_state", "own_query_history", "seed"]
- oracle query budget trace summary: max_query_count=5
- strategy_class_alignment_result: passed
- strongest known classical method operationalization: ["budget_limited_belief_state_planner", "greedy_information_gain_or_uncertainty_planner_under_budget", "fsm_planner", "successor_map", "transition_table", "graph_lookup", "episodic_traversal"]
- leakage_positive_control_result: passed
- replay_recomputation_result: passed
- generator_source_provenance_result: passed
- oracle_strategy_class: budget_limited_belief_state_planner
- strongest_classical_strategy_class: budget_limited_belief_state_planner

Baseline results:
- strongest_fair_baseline_score equals visible_channel_oracle_score, so a fair classical baseline entered the oracle equivalence band.
- all six graph-cache challengers were separately invoked and scored.

Ablation results:
- B1 hidden-field ablation passed: masking prohibited hidden fields did not improve or change visible-oracle predictions.
- Candidate ablations were not run because this is candidate-free Phase 0 and no candidate was implemented.

Replay result:
- replay_recomputation_result: passed from serialized_state plus permitted observation/query trace; hash-only and tamper negative controls failed as intended.

Stop conditions triggered: `fair_baseline_entered_visible_oracle_equivalence_band`.

Post-result routing: stop; preserve negative environment evidence; do not start route tournament; do not implement candidates.

What this does not prove: Gate1 pass, candidate feasibility, mechanism validity, agency, autonomy, consciousness, EGO readiness, or runtime/mainline effect. No candidate implementation is authorized by this verdict.
