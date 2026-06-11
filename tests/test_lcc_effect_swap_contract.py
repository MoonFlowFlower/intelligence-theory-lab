import json

from theory_lab.lcc_effect_swap import run_contract


def test_required_split_holds(tmp_path):
    result = run_contract(tmp_path)

    assert result["verdict"] == "lcc_contract_pass_bounded"
    assert result["gates"]["label_permutation_invariance"]["passed"] is True
    assert result["gates"]["effect_swap_sensitivity"]["passed"] is True
    assert result["metrics"]["label_permutation_change_rate"] == 0.0
    assert result["metrics"]["effect_swap_change_rate"] > 0.0


def test_behavior_only_replay_reconstructs_decisions(tmp_path):
    result = run_contract(tmp_path)

    replay = result["behavior_only_replay"]
    assert replay["passed"] is True
    assert replay["replayed_decisions"] == replay["total_decisions"]
    assert replay["used_fields"] == [
        "context",
        "action_handles",
        "learned_effect_estimates",
    ]


def test_candidate_has_no_forbidden_input_leak(tmp_path):
    result = run_contract(tmp_path)

    leak_scan = result["leak_scan"]
    assert leak_scan["candidate_passed"] is True
    assert leak_scan["candidate_forbidden_fields"] == []
    assert leak_scan["candidate_forbidden_source_tokens"] == []


def test_strong_baselines_are_not_equivalent(tmp_path):
    result = run_contract(tmp_path)

    equivalence = result["baseline_equivalence"]
    assert equivalence["passed"] is True
    assert equivalence["baselines"]["ActionLabelHeuristicBaseline"]["equivalent"] is False
    assert equivalence["baselines"]["StaticSafetyTableBaseline"]["equivalent"] is False
    assert equivalence["baselines"]["EffectBlindBaseline"]["equivalent"] is False
    assert equivalence["diagnostics"]["OracleEffectUpperBound"]["diagnostic_only"] is True


def test_required_artifacts_are_written(tmp_path):
    result = run_contract(tmp_path)
    required = {
        "STATUS.md",
        "verdict.json",
        "traces.jsonl",
        "behavior_only_replay.json",
        "label_permutation_report.md",
        "effect_swap_report.md",
        "leak_scan_report.md",
        "baseline_equivalence_report.md",
    }

    assert required.issubset({path.name for path in tmp_path.iterdir()})
    with (tmp_path / "verdict.json").open("r", encoding="utf-8") as fh:
        verdict = json.load(fh)
    assert verdict["verdict"] == result["verdict"]
    assert verdict["claim_boundary"] == "bounded contract result only"
