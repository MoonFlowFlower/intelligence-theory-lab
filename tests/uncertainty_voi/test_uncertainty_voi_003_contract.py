import json
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


EXPECTED_PREREG_SHA = "9964fbce108228cf32cd2df8834ed8b002bb27bc210956c3186c3fd7b96a5b26"


def test_003_config_uses_fresh_seed_blocks_and_preserves_prereg_hash():
    from uncertainty_voi import runner_002, runner_003

    cfg = runner_003.FrozenConfig()

    assert runner_003.sha256_lf(cfg.prereg_path.read_bytes()) == EXPECTED_PREREG_SHA
    assert cfg.task_id == "UNCERTAINTY-VOI-REQUEST-MECHANISM-003A"
    assert cfg.scored_seeds == tuple(range(9401, 9421))
    assert cfg.transfer_seeds == tuple(range(9421, 9431))
    assert cfg.tuning_seeds == tuple(range(9301, 9311))
    assert cfg.probe_seed == 9001
    assert cfg.q == pytest.approx(0.004)
    assert runner_003.assert_seed_blocks_disjoint(cfg) is True

    # 003A must reuse the frozen 002A simulation/policy implementation, not fork it.
    assert runner_003.simulate_policy is runner_002.simulate_policy
    assert runner_003.choose_mechanism_action is runner_002.choose_mechanism_action


def test_corrected_collapse_accepts_negative_control_advantage_and_survival_requires_positive_lower_ci():
    from uncertainty_voi import runner_003

    collapsed_negative = {"ci95": [-10.0, -1.0], "mean": -4.0}
    clean_minus_control = {"ci95": [2.0, 8.0], "mean": 5.0}
    survived_positive = {"ci95": [0.5, 3.0], "mean": 1.8}

    assert runner_003.control_collapse_signature(collapsed_negative, clean_minus_control) == {
        "control_ci_upper_le_zero": True,
        "clean_minus_control_ci_lower_gt_zero": True,
        "collapsed": True,
        "survived": False,
    }
    assert runner_003.control_survives(survived_positive) is True
    assert runner_003.control_survives(collapsed_negative) is False


def test_003_smoke_gate_emits_corrected_signature_reports_without_official_side_effects(tmp_path):
    from uncertainty_voi import runner_003

    cfg = runner_003.FrozenConfig(
        horizon=30,
        scored_seeds=(9401, 9402),
        transfer_seeds=(9421, 9422),
        tuning_seeds=(9301, 9302),
        bootstrap_reps=128,
        fresh_process_recompute_count=0,
    )
    payload = runner_003.run_gate(cfg=cfg, output_dir=tmp_path, write_artifacts=True)

    required = {
        "result.json",
        "trace.jsonl",
        "metric_records.json",
        "baseline_comparison.json",
        "ablation_report.json",
        "falsifier_report.json",
        "calibration_transfer_report.json",
        "replay_report.json",
        "headroom_report.json",
        "tripwire_report.json",
        "claim_ceiling.txt",
    }
    assert required.issubset({p.name for p in tmp_path.iterdir()})

    result = json.loads((tmp_path / "result.json").read_text(encoding="utf-8"))
    records = json.loads((tmp_path / "metric_records.json").read_text(encoding="utf-8"))
    falsifier = json.loads((tmp_path / "falsifier_report.json").read_text(encoding="utf-8"))
    replay = json.loads((tmp_path / "replay_report.json").read_text(encoding="utf-8"))

    assert result["task_id"] == "UNCERTAINTY-VOI-REQUEST-MECHANISM-003A"
    assert result["producer_function"] == "uncertainty_voi.runner_003.run_gate"
    assert result["config_shas"]["preregistration_lf_sha256"] == EXPECTED_PREREG_SHA
    assert result["seed_blocks"]["scored"] == [9401, 9402]
    assert result["seed_blocks"]["transfer"] == [9421, 9422]
    assert "collapse_signature" in result["gates"]["G2_falsifiers"]
    assert "survival_signature" in result["gates"]["G2_falsifiers"]
    assert "collapse_signature" in falsifier
    assert result["verdict"] in runner_003.VERDICT_SET
    assert all(record["producer_function"].startswith("uncertainty_voi.runner_003") for record in records["records"])
    assert replay["bit_exact"] is True
    assert payload["trace_size_bytes"] <= cfg.trace_size_cap_bytes


def test_003_rng_audit_scans_runner_003_and_positive_control_fires():
    from uncertainty_voi import runner_003

    audit = runner_003.run_rng_audit()

    assert audit["clean_scan"]["passed"] is True
    assert audit["positive_control"]["detected"] is True
    assert audit["scanned_module"] == "uncertainty_voi.runner_003"
