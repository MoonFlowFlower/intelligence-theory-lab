import json
import subprocess
import sys
from pathlib import Path


def test_prereg_contract_freezes_band_controls_and_floor_family():
    from scripts.env_headroom_probe.contract import (
        CONTROL_EXPECTED_VERDICTS,
        EQUIVALENCE_BAND,
        FAIR_BASELINE_FLOOR,
        PHASE_B_CANDIDATE_ENVS,
        build_prereg_contract,
    )

    contract = build_prereg_contract()

    assert EQUIVALENCE_BAND == 0.05
    assert CONTROL_EXPECTED_VERDICTS == {
        "POS_INTERNAL_ESTAR": "HEADROOM",
        "NEG_5A846D5_SCOUT": "SATURATED",
    }
    assert FAIR_BASELINE_FLOOR == (
        "predict_all",
        "predict_none",
        "per_user_lookup",
        "nearest_neighbor",
        "count_table",
        "frequency_marginal",
        "graph_closure",
        "obs_only_decoder",
    )
    assert contract["phase"] == "PHASE_A_PREREG_NO_SCORING"
    assert contract["official_scoring_enabled"] is False
    assert len(PHASE_B_CANDIDATE_ENVS) == 6
    assert "ideal_oracle" not in FAIR_BASELINE_FLOOR
    assert contract["ceiling"]["reference"] == "ideal_oracle"


def test_verdict_function_uses_computed_scores_not_expected_verdict_literals():
    from scripts.env_headroom_probe.battery import evaluate_verdict

    headroom = evaluate_verdict(
        scores={
            "ideal_oracle": 1.0,
            "predict_all": 0.2,
            "predict_none": 0.0,
            "per_user_lookup": 0.3,
            "nearest_neighbor": 0.25,
            "count_table": 0.3,
            "frequency_marginal": 0.2,
            "graph_closure": 0.35,
            "obs_only_decoder": 0.4,
        },
        equivalence_band=0.05,
    )
    saturated = evaluate_verdict(
        scores={
            "ideal_oracle": 1.0,
            "predict_all": 0.5,
            "predict_none": 0.0,
            "per_user_lookup": 0.93,
            "nearest_neighbor": 0.90,
            "count_table": 0.90,
            "frequency_marginal": 0.88,
            "graph_closure": 0.96,
            "obs_only_decoder": 0.91,
        },
        equivalence_band=0.05,
    )

    assert headroom["verdict"] == "HEADROOM"
    assert headroom["strongest_fair_baseline_id"] == "obs_only_decoder"
    assert saturated["verdict"] == "SATURATED"
    assert saturated["strongest_fair_baseline_id"] == "graph_closure"


def test_probe_valid_gate_voids_on_either_control_mismatch():
    from scripts.env_headroom_probe.battery import probe_valid_gate

    valid = probe_valid_gate(
        {"POS_INTERNAL_ESTAR": "HEADROOM", "NEG_5A846D5_SCOUT": "SATURATED"}
    )
    invalid = probe_valid_gate(
        {"POS_INTERNAL_ESTAR": "SATURATED", "NEG_5A846D5_SCOUT": "SATURATED"}
    )

    assert valid["probe_valid"] is True
    assert invalid["probe_valid"] is False
    assert invalid["candidate_verdict_policy"] == "VOID_ALL_CANDIDATE_VERDICTS"


def test_seed_everything_sets_random_numpy_and_torch_if_available():
    from scripts.env_headroom_probe.battery import seed_everything

    report = seed_everything(123)

    assert report["python_random_seed"] == 123
    assert report["numpy_seed"] == 123
    assert "torch_seed" in report


def test_contract_cli_is_fresh_process_and_does_not_write_official_artifacts(tmp_path):
    repo = Path(__file__).resolve().parents[2]
    official_artifact = (
        repo
        / "artifacts"
        / "BORROW-FIRST-ENV-SELECTION-AND-HEADROOM-PROBE-001A"
        / "result.json"
    )
    if official_artifact.exists():
        raise AssertionError(f"pre-existing forbidden artifact: {official_artifact}")

    proc = subprocess.run(
        [
            sys.executable,
            "-m",
            "scripts.env_headroom_probe.runner",
            "--mode",
            "contract",
        ],
        cwd=repo,
        text=True,
        capture_output=True,
        check=True,
    )
    payload = json.loads(proc.stdout)

    assert payload["phase"] == "PHASE_A_PREREG_NO_SCORING"
    assert payload["official_scoring_enabled"] is False
    assert not official_artifact.exists()
