import json

from scripts.env_headroom_probe.adapters import (
    BORROWED_ADAPTERS,
    build_borrowed_adapter_manifest,
    record_digest,
)
from scripts.env_headroom_probe.contract import PHASE_B_CANDIDATE_ENVS


BORROWED_REQUIRED = {
    "minigrid:MiniGrid-MemoryS13Random-v0",
    "minigrid:MiniGrid-KeyCorridorS3R1-v0",
    "bsuite:memory_len/0",
    "bsuite:memory_size/0",
    "bsuite:umbrella_length/0",
}


def test_borrowed_adapter_registry_wires_required_envs_but_not_alchemy_drop():
    assert BORROWED_REQUIRED <= set(BORROWED_ADAPTERS)
    assert "dm_alchemy:symbolic_default" not in BORROWED_ADAPTERS
    assert {entry["env_id"] for entry in PHASE_B_CANDIDATE_ENVS} >= (
        BORROWED_REQUIRED | {"dm_alchemy:symbolic_default"}
    )


def test_borrowed_adapters_emit_frozen_interface_with_label_separation_and_floor_contract():
    for env_id in sorted(BORROWED_REQUIRED):
        spec = BORROWED_ADAPTERS[env_id]
        records = spec.build_records(20260708)
        assert records, env_id
        assert {record.split for record in records} == {"train", "eval"}
        assert spec.floor_member_status["frequency_marginal"]["status"] == "N/A"
        assert spec.floor_member_status["graph_closure"]["status"] == "N/A"
        assert spec.floor_member_status["per_user_lookup"]["status"] == "populated"
        assert spec.floor_member_status["count_table"]["status"] == "populated"

        encoded = json.dumps([record.to_json_obj() for record in records], sort_keys=True)
        assert '"y":' in encoded
        for record in records:
            assert record.O["schema_version"] == "env_headroom_probe.observation.v1"
            assert record.y == record.y_star
            assert "y" not in record.O
            assert "y_star" not in record.O
            assert "reward" not in record.O
            assert "hidden_label" not in record.O
            assert "lookup_key" in record.O
            assert "cache_key" in record.O
            assert "frequency_value" not in record.O
            assert "relation_pairs" not in record.O
            assert "asserted_tuple" not in record.O


def test_borrowed_adapters_are_deterministic_without_scoring():
    for env_id, spec in BORROWED_ADAPTERS.items():
        left = record_digest(spec.build_records(20260708))
        right = record_digest(spec.build_records(20260708))
        other = record_digest(spec.build_records(20260709))
        assert left == right
        assert left != other


def test_borrowed_adapter_manifest_records_dependency_pins_and_alchemy_drop():
    manifest = build_borrowed_adapter_manifest(20260708)
    assert manifest["phase"] == "PHASE_BII_BORROWED_ADAPTER_WIRING_ONLY"
    assert manifest["scoring_performed"] is False
    assert manifest["candidate_verdicts_computed"] is False
    assert set(manifest["wired_adapters"]) == BORROWED_REQUIRED
    assert manifest["dropped_adapters"]["dm_alchemy:symbolic_default"]["reason"]
    assert manifest["failure_manifest"]["failures"][0]["adapter_id"] == "dm_alchemy:symbolic_default"
    for name in ("minigrid", "gymnasium", "bsuite"):
        pin = manifest["dependency_pins"][name]
        assert pin["installed"] is True
        assert pin["version"]
        assert pin["origin_sha256"]
