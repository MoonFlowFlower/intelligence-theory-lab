from __future__ import annotations

import json
from pathlib import Path

from src.tlgp_001b_r2 import preregistration as P
from src.tlgp_capability_witness_preflight_001a import rung1_capacity_sweep as runner


def test_rung1_capacity_sweep_design_and_budget_are_bound():
    design = runner.verify_frozen_design()

    assert design["match"] is True
    assert design["computed_sha256"] == runner.EXPECTED_DESIGN_SHA256
    assert design["recorded_sha256"] == runner.EXPECTED_DESIGN_SHA256

    cfg = runner.build_run_config(dry_run=False)
    budget = P.training_budget()
    assert cfg.model_seeds == P.model_seeds()[:3]
    assert cfg.n_train == 5000
    assert cfg.n_val == 1000
    assert cfg.n_test == 200
    assert cfg.max_epochs == 200
    assert cfg.steps_max == int(budget["steps_max"])
    assert cfg.lr_grid == [0.001, 0.0003]
    assert cfg.clear_count_min == 2
    assert cfg.consistency_expected_meta == {
        "20260710": 0.519,
        "20260711": 0.504,
        "20260712": 0.510,
    }
    assert all(
        cap["d_model"] % cap["heads"] == 0
        for cap in runner.FROZEN_DESIGN["capacity_grid"]["phase1"].values()
    )


def test_rung1_capacity_sweep_dry_run_writes_contract_and_replay(tmp_path: Path):
    report = runner.run_orchestration(
        dry_run=True,
        out_dir=tmp_path,
        dry_overrides={
            "model_seeds": [P.model_seeds()[0]],
            "phase1_capacity_tags": ["C0"],
            "phase2_rule_counts": [8],
            "n_train": 4,
            "n_val": 2,
            "n_test": 3,
            "max_epochs": 1,
            "steps_max": 2,
            "batch_size": 2,
            "lr_grid": [0.001],
        },
    )

    required = {
        "result.json",
        "trace.jsonl",
        "val_curves.jsonl",
        "baseline_comparison.json",
        "ablation_report.json",
        "leakage_report.json",
        "replay_report.json",
        "manifest.json",
        "dry_run_report.json",
    }
    assert required.issubset({p.name for p in tmp_path.iterdir()})

    dry = json.loads((tmp_path / "dry_run_report.json").read_text(encoding="utf-8"))
    replay = json.loads((tmp_path / "replay_report.json").read_text(encoding="utf-8"))
    result = json.loads((tmp_path / "result.json").read_text(encoding="utf-8"))

    assert report["dry_run"] is True
    assert report["full_scout_launched"] is False
    assert dry["evidential"] is False
    assert dry["c0_consistency_gate_asserted"] is False
    assert dry["all_evidence_files_written"] is True
    assert result["evidential"] is False
    assert replay["metrics_reconstructed_exact"] is True
    assert replay["max_abs_diff"] <= 1e-9
