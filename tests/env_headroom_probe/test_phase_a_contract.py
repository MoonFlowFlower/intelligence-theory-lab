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
        STRUCTURAL_FAIR_BASELINES,
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
    assert STRUCTURAL_FAIR_BASELINES == (
        "per_user_lookup",
        "nearest_neighbor",
        "count_table",
        "frequency_marginal",
        "graph_closure",
        "obs_only_decoder",
    )
    assert "predict_all" not in STRUCTURAL_FAIR_BASELINES
    assert "predict_none" not in STRUCTURAL_FAIR_BASELINES
    assert contract["ceiling"]["reference"] == "ideal_oracle"
    assert contract["shuffle_leakage_criterion"]["callable"] == "shuffle_leakage_ok"
    assert contract["floor_key_contract"] == {
        "per_user_lookup": ["lookup_key"],
        "count_table": ["cache_key"],
        "graph_closure": ["relation_pairs", "asserted_tuple"],
        "frequency_marginal": ["frequency_value"],
    }


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


def test_shuffle_leakage_ok_blocks_structural_baselines_but_ignores_oracle():
    from scripts.env_headroom_probe.battery import shuffle_leakage_ok

    shuffled_scores = {
        "ideal_oracle": 1.0,
        "predict_all": 0.8,
        "predict_none": 0.0,
        "per_user_lookup": 0.25,
        "nearest_neighbor": 0.30,
        "count_table": 0.20,
        "frequency_marginal": 0.26,
        "graph_closure": 0.0,
        "obs_only_decoder": 0.29,
    }
    assert shuffle_leakage_ok(shuffled_scores, chance_score=0.25, tol=0.05) is True

    leaked = dict(shuffled_scores)
    leaked["obs_only_decoder"] = 0.31
    assert shuffle_leakage_ok(leaked, chance_score=0.25, tol=0.05) is False


def test_verdict_voids_when_shuffle_leakage_or_floor_degeneracy_blocks_phase_b():
    from scripts.env_headroom_probe.battery import evaluate_verdict

    scores = {
        "ideal_oracle": 1.0,
        "predict_all": 0.1,
        "predict_none": 0.0,
        "per_user_lookup": 0.2,
        "nearest_neighbor": 0.2,
        "count_table": 0.2,
        "frequency_marginal": 0.2,
        "graph_closure": 0.2,
        "obs_only_decoder": 0.2,
    }

    shuffle_void = evaluate_verdict(
        scores,
        equivalence_band=0.05,
        shuffle_leakage_ok=False,
    )
    floor_void = evaluate_verdict(
        scores,
        equivalence_band=0.05,
        floor_degenerate=True,
    )

    assert shuffle_void["verdict"] == "VOID_SHUFFLE_LEAKAGE"
    assert floor_void["verdict"] == "VOID_FLOOR_DEGENERATE"


def test_run_battery_records_prediction_variation_and_voids_all_constant_structural_floor():
    from scripts.env_headroom_probe.adapters import ProbeRecord
    from scripts.env_headroom_probe.battery import run_battery
    from scripts.env_headroom_probe.contract import STRUCTURAL_FAIR_BASELINES

    records = []
    for split in ("train", "eval"):
        for idx in range(3):
            records.append(
                ProbeRecord(
                    record_id=f"degenerate-{split}-{idx}",
                    split=split,
                    group_id="degenerate",
                    O={
                        "schema_version": "env_headroom_probe.observation.v1",
                        "feature": f"{split}-{idx}",
                    },
                    y=("positive",),
                    y_star=("positive",),
                )
            )

    result = run_battery(records, seed=7)
    variation = result["prediction_variation"]

    assert result["verdict"]["verdict"] == "VOID_FLOOR_DEGENERATE"
    assert result["floor_competence"]["floor_degenerate"] is True
    assert set(result["floor_competence"]["structural_members"]) == set(STRUCTURAL_FAIR_BASELINES)
    assert all(variation[name]["varies"] is False for name in STRUCTURAL_FAIR_BASELINES)


def test_parent_card_documents_b2_b3_rework_contract():
    repo = Path(__file__).resolve().parents[2]
    card = (
        repo
        / "docs"
        / "codex"
        / "tasks"
        / "BORROW-FIRST-ENV-SELECTION-AND-HEADROOM-PROBE-001A.md"
    ).read_text(encoding="utf-8")

    assert "Status: DESIGN CARD" in card
    assert "ideal MUST collapse" not in card
    assert "shuffle_leakage_ok(scores_shuffled) -> bool" in card
    assert "VOID_FLOOR_DEGENERATE" in card
    assert "lookup_key" in card
    assert "cache_key" in card
    assert "relation_pairs" in card
    assert "asserted_tuple" in card
    assert "frequency_value" in card


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


def test_controls_score_mode_is_guarded_and_emits_required_artifact_set(tmp_path):
    repo = Path(__file__).resolve().parents[2]

    blocked = subprocess.run(
        [
            sys.executable,
            "-m",
            "scripts.env_headroom_probe.runner",
            "--mode",
            "score",
            "--emit-artifacts",
            "--artifact-dir",
            str(tmp_path),
        ],
        cwd=repo,
        text=True,
        capture_output=True,
    )
    assert blocked.returncode != 0
    assert "--phase-b-authorized" in (blocked.stderr + blocked.stdout)

    proc = subprocess.run(
        [
            sys.executable,
            "-m",
            "scripts.env_headroom_probe.runner",
            "--mode",
            "score",
            "--phase-b-authorized",
            "--emit-artifacts",
            "--artifact-dir",
            str(tmp_path),
        ],
        cwd=repo,
        text=True,
        capture_output=True,
    )
    assert proc.returncode in {0, 1}

    expected_files = {
        "controls_result.json",
        "trace.jsonl",
        "baseline_comparison.json",
        "ablation_report.json",
        "replay_report.json",
        "probe_valid.json",
        "claim_ceiling.txt",
    }
    assert expected_files <= {p.name for p in tmp_path.iterdir()}

    controls_result = json.loads((tmp_path / "controls_result.json").read_text(encoding="utf-8"))
    replay_report = json.loads((tmp_path / "replay_report.json").read_text(encoding="utf-8"))
    trace_rows = [
        json.loads(line)
        for line in (tmp_path / "trace.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]

    assert set(controls_result["per_control"]) == {"POS_INTERNAL_ESTAR", "NEG_5A846D5_SCOUT"}
    assert controls_result["candidate_envs_scored"] == []
    assert controls_result["equivalence_band"] == 0.05
    assert replay_report["fresh_process_recompute_count"] == 2
    assert "bit_exact" in replay_report
    assert {row["env_id"] for row in trace_rows} == {
        "POS_INTERNAL_ESTAR",
        "NEG_5A846D5_SCOUT",
    }
    assert {row["mode"] for row in trace_rows} == {
        "normal",
        "drop_graph_closure",
        "shuffle_o_y",
    }
