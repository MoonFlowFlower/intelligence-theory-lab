from scripts.env_headroom_probe.adapters import (
    ProbeRecord,
    decode_oracle_from_O_explicit_field,
    evaluate_oracle_from_O_admission,
)


def _record(idx: int, O: dict, y: tuple[str, ...]) -> ProbeRecord:
    return ProbeRecord(
        record_id=f"r{idx}",
        split="eval",
        group_id="synthetic",
        O={
            "schema_version": "env_headroom_probe.observation.v1",
            **O,
        },
        y=y,
        y_star=y,
    )


def test_random_target_independent_of_O_is_invalid_not_o_determined():
    records = [
        _record(idx, {"legal_observation": idx % 2}, (f"random_bit:{(idx * 7 + 3) % 2}",))
        for idx in range(6)
    ]

    admission = evaluate_oracle_from_O_admission(
        "synthetic:random_target_independent_of_O",
        records,
        decode_oracle_from_O_explicit_field,
    )

    assert admission["oracle_from_O"]["score"] < 1.0
    assert admission["oracle_from_O"]["admission_status"] == "INVALID_TARGET_NOT_O_DETERMINED"
    assert admission["trivial_floor_guard"]["guard"] == "DROP_INVALID_ADAPTER"


def test_trivial_target_index_of_O_triggers_saturated_floor_guard():
    records = [
        _record(
            idx,
            {"oracle_from_O_target": [f"class:{idx % 3}"], "legal_observation": idx % 3},
            (f"class:{idx % 3}",),
        )
        for idx in range(6)
    ]

    admission = evaluate_oracle_from_O_admission(
        "synthetic:trivial_target_index_of_O",
        records,
        decode_oracle_from_O_explicit_field,
    )

    assert admission["oracle_from_O"]["score"] == 1.0
    assert admission["oracle_from_O"]["admission_status"] == "ADMISSIBLE_O_DETERMINED"
    assert admission["trivial_floor_guard"]["guard"] == "VOID_TRIVIALLY_DECODABLE"
    assert admission["trivial_floor_guard"]["future_floor_effect"] == (
        "SATURATED_BY_LEGAL_OBSERVATION_DECODER"
    )
    assert "HEADROOM" not in str(admission)
