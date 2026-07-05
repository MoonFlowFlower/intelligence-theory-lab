from __future__ import annotations

import json
from pathlib import Path

import torch.nn as nn

from src.tlgp_001b_r2 import preregistration as P
from src.tlgp_capability_witness_preflight_001a import rung1_capacity_sweep_002a as runner


def test_002a_design_recipe_and_trainability_are_bound():
    design = runner.verify_frozen_design()

    assert design["match"] is True
    assert design["computed_sha256"] == runner.EXPECTED_DESIGN_SHA256
    assert design["recorded_sha256"] == runner.EXPECTED_DESIGN_SHA256

    cfg = runner.build_run_config(dry_run=False)
    assert cfg.model_seeds == P.model_seeds()[:3]
    assert cfg.phase2_rule_counts == [8, 16, 32, 64, 128, 172]
    assert cfg.trainability_control_rule_count == 2
    assert cfg.trainability_threshold == 0.90
    assert cfg.c0_anchor_min_meta == 0.49
    assert cfg.peak_lr_grid == [0.0003, 0.0001, 0.00003]
    assert cfg.optimizer == "AdamW"
    assert cfg.betas == [0.9, 0.95]
    assert cfg.weight_decay == 0.1
    assert cfg.grad_clip_global_norm == 1.0
    assert cfg.warmup_epochs == 15
    assert cfg.min_lr_fraction == 0.1
    assert cfg.early_stop_min_epochs == 35
    assert runner.FROZEN_DESIGN["full_scout_forbidden_until_review"] is True
    assert all(
        cap["d_model"] % cap["heads"] == 0
        for cap in runner.FROZEN_DESIGN["capacity_grid"]["phase1"].values()
    )


def test_002a_optimizer_groups_and_lr_schedule_are_auditable():
    model = nn.Sequential(nn.Linear(3, 4), nn.LayerNorm(4))
    groups = runner.make_adamw_param_groups(model, weight_decay=0.1)

    assert len(groups) == 2
    assert groups[0]["weight_decay"] == 0.1
    assert groups[1]["weight_decay"] == 0.0
    assert all(param.ndim >= 2 for param in groups[0]["params"])
    assert all(param.ndim < 2 for param in groups[1]["params"])

    cfg = runner.build_run_config(
        dry_run=True,
        dry_overrides={
            "warmup_epochs": 2,
            "max_epochs": 6,
            "steps_max": 12,
            "n_train": 4,
            "batch_size": 2,
            "peak_lr_grid": [0.0003],
        },
    )
    steps_per_epoch = runner.steps_per_epoch(cfg.n_train, cfg.batch_size)
    lrs = [
        runner.scheduled_lr(
            peak_lr=0.0003,
            step=step,
            steps_per_epoch=steps_per_epoch,
            config=cfg,
        )[0]
        for step in range(1, 13)
    ]

    assert lrs[0] < lrs[3]
    assert lrs[-1] < lrs[3]
    assert lrs[-1] >= 0.00003


def test_002a_tiny_dry_run_writes_non_evidential_contract(tmp_path: Path):
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
            "max_epochs": 4,
            "warmup_epochs": 1,
            "early_stop_min_epochs": 2,
            "steps_max": 8,
            "batch_size": 2,
            "peak_lr_grid": [0.0001],
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
    curves = [
        json.loads(line)
        for line in (tmp_path / "val_curves.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]

    assert report["dry_run"] is True
    assert report["full_scout_launched"] is False
    assert dry["evidential"] is False
    assert dry["trainability_control_path_exercised"] is True
    assert dry["trainability_gate_asserted"] is False
    assert dry["c0_anchor_gate_asserted"] is False
    assert dry["warmup_schedule_observed"]["lr_rises"] is True
    assert result["evidential"] is False
    assert result["full_scout_launched"] is False
    assert replay["metrics_reconstructed_exact"] is True
    assert replay["max_abs_diff"] <= 1e-9
    assert any(row["warmup_active"] for row in curves)
    assert all("lr" in row and "warmup_active" in row for row in curves)
