import json
from pathlib import Path

from src.fsp_pum_env.trajectory_sets import (
    MEMBER_VIEW_KEYS,
    TrajectorySetSpec,
    build_generation_specs,
    iter_member_view_records,
    load_frozen_design,
    regenerate_member_view_sha256,
    write_trajectory_set_recipe,
)


FROZEN = Path(__file__).resolve().parents[2] / "artifacts" / "FSP-PUM-ENV-IDPROBE-001A" / "frozen_design.json"


def test_generation_specs_use_frozen_population_seeds_and_real_env_mode():
    design = load_frozen_design(FROZEN)

    specs = build_generation_specs(design, env_mode="base")

    assert [spec.master_seed for spec in specs] == design["population_and_data"]["env_master_seeds"]
    assert specs[0].env_mode == "base"
    assert specs[0].partitions == {
        "train": {"start_user_id": 0, "count": design["population_and_data"]["N_train_users"]},
        "heldout": {
            "start_user_id": design["population_and_data"]["N_train_users"],
            "count": design["population_and_data"]["N_heldout_users"],
        },
    }
    assert specs[0].turns_per_user == design["env_parameters"]["episodes"]["total_turns_per_user"]
    assert specs[0].logging_policy == design["population_and_data"]["log_parity_trajectory_policy"]


def test_member_view_records_expose_only_prefix_visible_fields():
    design = load_frozen_design(FROZEN)
    spec = TrajectorySetSpec(
        set_id="unit_set",
        master_seed=design["population_and_data"]["env_master_seeds"][0],
        env_mode="base",
        partitions={"heldout": {"start_user_id": design["population_and_data"]["N_train_users"], "count": 1}},
        turns_per_user=design["env_parameters"]["episodes"]["total_turns_per_user"],
        logging_policy=design["population_and_data"]["log_parity_trajectory_policy"],
    )

    records = list(iter_member_view_records(design, spec))

    assert len(records) == design["env_parameters"]["episodes"]["total_turns_per_user"]
    assert set(records[0]) == MEMBER_VIEW_KEYS
    assert {key for record in records for key in record} == MEMBER_VIEW_KEYS
    assert all(set(record["observation"]) == {"symbol"} for record in records)
    assert all("theta" not in json.dumps(record).lower() for record in records)
    assert all("trust" not in json.dumps(record).lower() for record in records)
    assert all("seed" not in json.dumps(record).lower() for record in records)
    assert records[0]["session_boundary"] == "start"
    assert records[-1]["step_index"] == design["env_parameters"]["episodes"]["total_turns_per_user"] - 1


def test_recipe_manifest_entry_regenerates_member_view_sha_byte_identically(tmp_path):
    design = load_frozen_design(FROZEN)
    spec = TrajectorySetSpec(
        set_id="unit_set",
        master_seed=design["population_and_data"]["env_master_seeds"][0],
        env_mode="base",
        partitions={"heldout": {"start_user_id": design["population_and_data"]["N_train_users"], "count": 2}},
        turns_per_user=design["env_parameters"]["episodes"]["total_turns_per_user"],
        logging_policy=design["population_and_data"]["log_parity_trajectory_policy"],
    )

    entry = write_trajectory_set_recipe(design, spec, tmp_path, raw_size_limit_bytes=1)
    regenerated = regenerate_member_view_sha256(design, entry)

    assert entry["storage_mode"] == "recipe_only_raw_estimate_exceeds_limit"
    assert entry["member_view_sha256"] == regenerated
    assert len(entry["generator_code_hash"]) == 64
    recipe_path = tmp_path / entry["recipe_path"]
    assert recipe_path.exists()
    recipe = json.loads(recipe_path.read_text(encoding="utf-8"))
    assert recipe["visibility"] == "adjudicator_only_regeneration_recipe_not_member_visible"
    assert recipe["member_view_sha256"] == entry["member_view_sha256"]
