import json
from pathlib import Path

from itl_devbench.core.hashing import sha256_file
from itl_devbench.envs.task_family_generator import load_generator_config
from itl_devbench.eval.run_matrix import run_benchmark


def test_minimal_loop_source_hash_matches_001b_baseline_before_and_after_run(tmp_path):
    baseline_path = Path("artifacts/ITL-DEV-BENCH-001A/latest/source_hashes_001b.json")
    baseline = json.loads(baseline_path.read_text(encoding="utf-8"))
    current_hash = sha256_file(baseline["source_path"])
    assert current_hash == baseline["sha256"]

    config = load_generator_config("configs/itl_devbench_001c.yaml")
    run_dir = run_benchmark(config=config, smoke=True, output_root=tmp_path)
    check = json.loads((run_dir / "candidate_source_hash_check.json").read_text(encoding="utf-8"))

    assert check["verdict"] == "candidate_source_unchanged"
    assert check["before_sha256"] == baseline["sha256"]
    assert check["after_sha256"] == baseline["sha256"]
