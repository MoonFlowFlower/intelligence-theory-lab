import json

from itl_devbench.envs.families import REQUIRED_FAMILY_IDS
from itl_devbench.envs.task_family_generator import load_generator_config
from itl_devbench.eval.run_matrix import run_benchmark


def test_all_required_families_run_and_emit_family_metrics(tmp_path):
    config = load_generator_config("configs/itl_devbench_001c.yaml")
    run_dir = run_benchmark(config=config, smoke=True, output_root=tmp_path)

    summary = json.loads((run_dir / "family_metric_summary.json").read_text(encoding="utf-8"))
    families = {row["family_id"] for row in summary["families"]}
    assert set(REQUIRED_FAMILY_IDS).issubset(families)
    assert all(row["valid_headroom"] is True for row in summary["families"])

    for name in [
        "baseline_scores_by_family.json",
        "baseline_scores_by_dimension.json",
        "graph_cache_saturation_report.json",
        "oracle_headroom_report.json",
        "family_metric_summary.json",
        "candidate_source_hash_check.json",
    ]:
        assert (run_dir / name).exists(), name

    manifest = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["report_verdict"] in {
        "discriminative_generator_smoke_ready",
        "still_baseline_saturated_environment_needs_redesign",
    }
