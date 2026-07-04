import hashlib
from pathlib import Path

from src.fsp_pum_env.trajectory_sets import (
    TrajectorySetSpec,
    _canonical_line,
    _hash_spec_streams,
    _iter_records_with_adjudicator,
    load_frozen_design,
    regenerate_member_view_sha256,
)


FROZEN = Path(__file__).resolve().parents[2] / "artifacts" / "FSP-PUM-ENV-IDPROBE-001A" / "frozen_design.json"


def _mini_spec(design, partitions):
    return TrajectorySetSpec(
        set_id="partition_order_unit",
        master_seed=20260701,
        env_mode="base",
        partitions=partitions,
        turns_per_user=design["env_parameters"]["episodes"]["total_turns_per_user"],
        logging_policy=design["population_and_data"]["log_parity_trajectory_policy"],
    )


def _manifest_entry_from_spec(spec):
    return {
        "set_id": spec.set_id,
        "generation_params": spec.to_json_dict(),
    }


def _raw_declared_order_member_sha(design, spec):
    member_hash = hashlib.sha256()
    for partition, trajectory_ordinal, member_record, _ in _iter_records_with_adjudicator(
        design,
        spec,
        partition_order="declared",
    ):
        if member_record["step_index"] == 0:
            member_hash.update(f"trajectory\t{partition}\t{trajectory_ordinal}\n".encode("utf-8"))
        member_hash.update(_canonical_line(member_record))
    return member_hash.hexdigest()


def test_regenerate_member_view_sha_is_invariant_to_manifest_partition_key_order():
    design = load_frozen_design(FROZEN)
    canonical_spec = _mini_spec(
        design,
        {
            "train": {"start_user_id": 0, "count": 2},
            "heldout": {"start_user_id": 800, "count": 2},
        },
    )
    stored_order_spec = _mini_spec(
        design,
        {
            "heldout": {"start_user_id": 800, "count": 2},
            "train": {"start_user_id": 0, "count": 2},
        },
    )
    expected, *_ = _hash_spec_streams(design, canonical_spec)

    regenerated = regenerate_member_view_sha256(design, _manifest_entry_from_spec(stored_order_spec))

    assert regenerated == expected


def test_forced_declared_heldout_first_order_remains_fail_able():
    design = load_frozen_design(FROZEN)
    heldout_first = _mini_spec(
        design,
        {
            "heldout": {"start_user_id": 800, "count": 2},
            "train": {"start_user_id": 0, "count": 2},
        },
    )
    canonical, *_ = _hash_spec_streams(design, heldout_first)
    forced_declared = _raw_declared_order_member_sha(design, heldout_first)

    assert forced_declared != canonical


def test_per_user_chunks_are_identical_between_partition_orderings():
    design = load_frozen_design(FROZEN)
    canonical_spec = _mini_spec(
        design,
        {
            "train": {"start_user_id": 0, "count": 2},
            "heldout": {"start_user_id": 800, "count": 2},
        },
    )
    heldout_first = _mini_spec(
        design,
        {
            "heldout": {"start_user_id": 800, "count": 2},
            "train": {"start_user_id": 0, "count": 2},
        },
    )

    assert _per_user_member_hashes(design, canonical_spec) == _per_user_member_hashes(design, heldout_first)


def test_single_partition_specs_are_noop_under_canonical_partition_order():
    design = load_frozen_design(FROZEN)
    single = _mini_spec(design, {"train": {"start_user_id": 0, "count": 3}})

    canonical, *_ = _hash_spec_streams(design, single)
    declared = _raw_declared_order_member_sha(design, single)

    assert canonical == declared


def _per_user_member_hashes(design, spec):
    chunks = {}
    for partition, trajectory_ordinal, member_record, adjudicator_record in _iter_records_with_adjudicator(
        design,
        spec,
        partition_order="declared",
    ):
        key = (partition, int(adjudicator_record["user_id"]))
        hasher = chunks.setdefault(key, hashlib.sha256())
        if member_record["step_index"] == 0:
            hasher.update(f"trajectory\t{partition}\t{trajectory_ordinal}\n".encode("utf-8"))
        hasher.update(_canonical_line(member_record))
    return {key: hasher.hexdigest() for key, hasher in chunks.items()}
