from itl_devbench.eval.run_matrix import REQUIRED_BASELINES, minimal_loop_variants, run_benchmark
import json


def test_all_eight_minimal_loop_variants_are_labeled_and_run(tmp_path):
    variants = minimal_loop_variants()
    assert [variant for variant, _agent in variants] == [
        "000",
        "100",
        "010",
        "001",
        "110",
        "101",
        "011",
        "111",
    ]

    run_dir = run_benchmark(
        config={"width": 7, "height": 7, "max_ticks": 12, "smoke_seeds": [0]},
        smoke=True,
        output_root=tmp_path,
    )
    metrics_text = (run_dir / "metrics.json").read_text(encoding="utf-8")
    for variant in ["000", "100", "010", "001", "110", "101", "011", "111"]:
        assert f'"variant": "{variant}"' in metrics_text
    for baseline in REQUIRED_BASELINES:
        assert f'"agent_id": "{baseline}"' in metrics_text


def test_oracle_gap_is_computed_for_non_oracle_rows(tmp_path):
    run_dir = run_benchmark(
        config={"width": 7, "height": 7, "max_ticks": 12, "smoke_seeds": [0]},
        smoke=True,
        output_root=tmp_path,
    )
    metrics = json.loads((run_dir / "metrics.json").read_text(encoding="utf-8"))
    non_oracle_rows = [
        row for row in metrics["episode_metrics"] if row["agent_id"] != "oracle" and row["stage"] == 0
    ]

    assert non_oracle_rows
    assert all(row["oracle_gap"] is not None for row in non_oracle_rows)
