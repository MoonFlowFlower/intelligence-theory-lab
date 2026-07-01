from __future__ import annotations

import json
from pathlib import Path

from src.tlgp_001b_r2 import preregistration as P
from src.tlgp_capability_witness_preflight_001a import rung3_powered_full_run as runner


def test_phase_b_design_sha_and_full_budget_are_bound():
    design = runner.verify_phase_b_design()

    assert design["computed_sha256"] == runner.EXPECTED_PHASE_B_DESIGN_SHA256
    assert design["recorded_sha256"] == runner.EXPECTED_PHASE_B_DESIGN_SHA256
    assert design["match"] is True

    cfg = runner.build_run_config(dry_run=False)
    budget = P.training_budget()
    assert cfg.model_seeds == P.model_seeds()
    assert cfg.lr_grid == [0.001, 0.0003]
    assert cfg.lr_grid == budget["lr_grid"]
    assert cfg.n_train == 5000
    assert cfg.n_val == 1000
    assert cfg.rung1_n_test == 200
    assert cfg.rung3_n_test == 200
    assert cfg.rung3_required_test_rules == 125
    assert cfg.max_epochs == 200
    assert cfg.early_stop_patience == budget["early_stop_patience"]
    assert cfg.steps_max == budget["steps_max"]
    assert cfg.epsilon == P.DELTA()


def test_dry_run_writes_contract_and_replay(tmp_path: Path):
    report = runner.run_orchestration(
        dry_run=True,
        out_dir=tmp_path,
        dry_overrides={
            "n_train": 2,
            "n_val": 2,
            "rung1_n_test": 2,
            "rung3_n_test": 2,
            "rung2_n_test": 2,
            "max_epochs": 1,
            "steps_max": 1,
            "batch_size": 2,
        },
    )

    required = {
        "result.json",
        "trace.jsonl",
        "val_curves.jsonl",
        "baseline_comparison.json",
        "ablation_report.json",
        "eligibility_report.json",
        "leakage_report.json",
        "replay_report.json",
        "route_decision_input.json",
        "route_decision.json",
        "manifest.json",
        "dry_run_report.json",
    }
    assert required.issubset({p.name for p in tmp_path.iterdir()})

    dry = json.loads((tmp_path / "dry_run_report.json").read_text(encoding="utf-8"))
    replay = json.loads((tmp_path / "replay_report.json").read_text(encoding="utf-8"))
    result = json.loads((tmp_path / "result.json").read_text(encoding="utf-8"))

    assert report["dry_run"] is True
    assert dry["evidential"] is False
    assert dry["full_run_launched"] is False
    assert result["evidential"] is False
    assert replay["verdict_reconstructed_exact"] is True
    assert replay["max_abs_diff"] <= 1e-9
