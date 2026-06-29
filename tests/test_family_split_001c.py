import json

from itl_devbench.envs.task_family_generator import TaskFamilyGenerator, load_generator_config
from itl_devbench.eval.run_matrix import run_benchmark


def test_smoke_heldout_split_has_no_overlap_and_is_deterministic():
    config = load_generator_config("configs/itl_devbench_001c.yaml")
    first = TaskFamilyGenerator(config).build_spec()
    second = TaskFamilyGenerator(config).build_spec()

    assert first == second
    smoke = {tuple(item["dimension_values"]) for item in first["smoke_split"]["combinations"]}
    heldout = {tuple(item["dimension_values"]) for item in first["heldout_split"]["combinations"]}
    assert smoke
    assert heldout
    assert smoke.isdisjoint(heldout)


def test_generator_spec_artifact_records_splits(tmp_path):
    config = load_generator_config("configs/itl_devbench_001c.yaml")
    run_dir = run_benchmark(config=config, smoke=True, output_root=tmp_path)
    spec = json.loads((run_dir / "generator_spec_001c.json").read_text(encoding="utf-8"))

    for key in [
        "families",
        "dimension_space",
        "smoke_split",
        "validation_split",
        "heldout_split",
        "extrapolation_split",
        "hidden_rule_sampling",
        "seed_policy",
    ]:
        assert key in spec
