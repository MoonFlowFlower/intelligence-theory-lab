import json

from acolb_001a.baselines import select_strongest_fair_baseline
from acolb_001a.headroom_preflight import run_headroom_preflight


def test_saturated_fixture_closes_before_mechanism_claim(tmp_path):
    result = run_headroom_preflight(output_dir=tmp_path, fixture="saturated")

    assert result["verdict"] == "saturated_close"
    assert result["candidate_evidence_reached"] is False
    assert (tmp_path / "headroom_preflight.json").exists()
    persisted = json.loads((tmp_path / "failure_manifest.json").read_text(encoding="utf-8"))
    assert "blocked_by_saturated_distribution" in persisted["stop_conditions"]


def test_fair_baseline_sensitivity_records_shared_decay_selection(tmp_path):
    result = run_headroom_preflight(output_dir=tmp_path, fixture="normal")
    sensitivity = json.loads((tmp_path / "fair_baseline_sensitivity.json").read_text(encoding="utf-8"))
    decay_rows = sensitivity["decay_candidates"]
    decay_values = {row["decay"] for row in decay_rows}
    selected = sensitivity["selected_rules"]["drift_aware_validation"]
    selected_row = next(row for row in decay_rows if row["decay"] == selected["decay"])

    assert {0.35, 1.0} <= decay_values
    assert selected["decay"] == result["candidate_decay"]
    assert selected["decay"] == result["fair_amortized_decay"]
    assert selected_row["legal_for_baseline"] is True
    assert selected_row["saturated_close"] is True
    assert sensitivity["aggregation_rule"] == result["aggregation_rule"] == "mean_episode_score"


def test_parity_broken_fixture_closes_on_underpowered_amortized_baseline(tmp_path):
    result = run_headroom_preflight(output_dir=tmp_path, fixture="parity_broken")

    assert result["verdict"] == "parity_broken_close"
    assert result["candidate_evidence_reached"] is False
    persisted = json.loads((tmp_path / "failure_manifest.json").read_text(encoding="utf-8"))
    assert "blocked_by_underpowered_or_unfair_amortized_baseline" in persisted["stop_conditions"]


def test_strongest_fair_baseline_selection_is_argmax_by_score_not_name():
    selected = select_strongest_fair_baseline(
        {
            "amortized_seq": {"ood_score": 0.40},
            "factorized_lookup": {"ood_score": 0.67},
            "oracle": {"ood_score": 1.0},
        }
    )

    assert selected == {"name": "factorized_lookup", "score": 0.67}
