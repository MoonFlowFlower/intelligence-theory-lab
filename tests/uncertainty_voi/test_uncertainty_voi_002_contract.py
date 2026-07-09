import json
import sys
from pathlib import Path

import numpy as np
import pytest


ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


EXPECTED_PREREG_SHA = "bc087cfc13102a57a624b7bb5d8684b50303db7c9be701bdd08d709bffffdf73"


def test_002_frozen_config_preserves_prereg_hash_seed_blocks_and_task_identity():
    from uncertainty_voi import runner_002

    cfg = runner_002.FrozenConfig()

    assert runner_002.sha256_lf(cfg.prereg_path.read_bytes()) == EXPECTED_PREREG_SHA
    assert cfg.task_id == "UNCERTAINTY-VOI-REQUEST-MECHANISM-002A"
    assert cfg.k == 8
    assert cfg.horizon == 200
    assert cfg.tau_hi == pytest.approx(0.06)
    assert cfg.tau_lo == pytest.approx(0.005)
    assert cfg.q == pytest.approx(0.004)
    assert cfg.scored_seeds == tuple(range(9101, 9121))
    assert cfg.transfer_seeds == tuple(range(9201, 9211))
    assert cfg.tuning_seeds == tuple(range(9301, 9311))
    assert runner_002.assert_seed_blocks_disjoint(cfg) is True
    assert "SIMPLE_ACTIVE_SUFFICIENT" in runner_002.VERDICT_SET


def test_model_a_regret_loads_belief_incumbent_on_noop(monkeypatch):
    from uncertainty_voi import runner_002

    cfg = runner_002.FrozenConfig(horizon=1)
    values = np.array([[0.1, 0.9, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2], [0.1] * 8], dtype=float)
    world = runner_002.RestlessGaussianBanditWorld(
        env_seed=123,
        values=values,
        query_noise=np.zeros((1, 8), dtype=float),
        request_noise=np.zeros((1, 8), dtype=float),
        fast_arm_mask=np.array([True, True, True, True, False, False, False, False]),
        slow_arm_mask=np.array([False, False, False, False, True, True, True, True]),
    )

    monkeypatch.setattr(runner_002.RestlessGaussianBanditWorld, "from_seed", classmethod(lambda cls, seed, cfg: world))

    episode = runner_002.simulate_policy("hold_only", 123, cfg, trace=True)

    assert episode.action_counts["noop"] == 1
    assert episode.regret == pytest.approx(0.8)
    assert episode.trace_rows[0]["incumbent_arm"] == 0
    assert episode.trace_rows[0]["action"] == {"kind": "noop"}
    assert episode.trace_rows[0]["regret"] == pytest.approx(0.8)


def test_kg_exploit_pressure_noops_when_belief_is_certain_and_queries_when_ambiguous():
    from uncertainty_voi import runner_002

    cfg = runner_002.FrozenConfig()
    certain_action = runner_002.choose_mechanism_action(
        np.full(cfg.k, 0.5, dtype=float),
        np.full(cfg.k, 1e-12, dtype=float),
        cfg,
    )
    ambiguous_action = runner_002.choose_mechanism_action(
        np.full(cfg.k, 0.5, dtype=float),
        np.full(cfg.k, cfg.initial_var, dtype=float),
        cfg,
    )

    assert certain_action == {"kind": "noop"}
    assert ambiguous_action["kind"] in {"query", "request"}


def test_random_active_is_a_rival_that_queries_every_step_and_trace_hides_truth():
    from uncertainty_voi import runner_002

    cfg = runner_002.FrozenConfig(horizon=5)
    episode = runner_002.simulate_policy("random_active", 9001, cfg, trace=True)

    assert episode.action_counts["query"] == cfg.horizon
    assert episode.action_counts["noop"] == 0
    assert all("offline_true_values" not in row for row in episode.trace_rows)
    assert all("tau" not in json.dumps(row["observation"], sort_keys=True) for row in episode.trace_rows)


def test_002_trace_replay_recomputes_actions_and_rejects_tamper():
    from uncertainty_voi import runner_002

    cfg = runner_002.FrozenConfig(horizon=20)
    episode = runner_002.simulate_policy("mechanism", 9001, cfg, trace=True)

    replay = runner_002.replay_trace(episode.trace_rows, cfg)
    assert replay["bit_exact"] is True
    assert replay["uses_hash_only_comparison"] is False
    assert replay["recomputed_from_serialized_state_and_observation"] is True

    tampered = [dict(row) for row in episode.trace_rows]
    tampered[0] = dict(tampered[0])
    tampered[0]["action"] = {"kind": "noop"} if tampered[0]["action"].get("kind") != "noop" else {"kind": "query", "arm": 0}
    tamper_replay = runner_002.replay_trace(tampered, cfg)
    assert tamper_replay["bit_exact"] is False
    assert "action_mismatch" in " ".join(tamper_replay["mismatches"])


def test_002_static_tuning_uses_only_tuning_seed_block():
    from uncertainty_voi import runner_002

    cfg = runner_002.FrozenConfig(horizon=20, tuning_seeds=(9301, 9302))
    tuning = runner_002.tune_static_threshold(cfg)

    assert tuning["used_seeds"] == list(cfg.tuning_seeds)
    assert set(tuning["used_seeds"]).isdisjoint(cfg.scored_seeds)
    assert set(tuning["used_seeds"]).isdisjoint(cfg.transfer_seeds)
    assert tuning["best_params"]["theta"] in cfg.static_theta_grid
    assert tuning["best_params"]["request_period"] in cfg.static_request_period_grid


def test_002_smoke_gate_emits_callable_reports_without_official_artifact_side_effects(tmp_path):
    from uncertainty_voi import runner_002

    cfg = runner_002.FrozenConfig(
        horizon=30,
        scored_seeds=(9101, 9102),
        transfer_seeds=(9201, 9202),
        tuning_seeds=(9301, 9302),
        bootstrap_reps=128,
        fresh_process_recompute_count=0,
    )
    payload = runner_002.run_gate(cfg=cfg, output_dir=tmp_path, write_artifacts=True)

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
    replay = json.loads((tmp_path / "replay_report.json").read_text(encoding="utf-8"))

    assert result["producer_function"] == "uncertainty_voi.runner_002.run_gate"
    assert result["config_shas"]["preregistration_lf_sha256"] == EXPECTED_PREREG_SHA
    assert "G1a_static_rival" in result["gates"]
    assert "G1b_random_active_rival" in result["gates"]
    assert result["verdict"] in runner_002.VERDICT_SET
    assert all(record["producer_function"].startswith("uncertainty_voi.runner_002") for record in records["records"])
    assert all(len(record["code_path_hash"]) == 64 for record in records["records"])
    assert replay["bit_exact"] is True
    assert payload["trace_size_bytes"] <= cfg.trace_size_cap_bytes


def test_002_rng_audit_has_clean_scan_and_fail_able_positive_control():
    from uncertainty_voi import runner_002

    audit = runner_002.run_rng_audit()

    assert audit["clean_scan"]["passed"] is True
    assert audit["positive_control"]["detected"] is True
    assert "np.random.default_rng()" in audit["positive_control"]["source"]
