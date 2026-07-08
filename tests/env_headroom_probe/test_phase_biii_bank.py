import json

from scripts.env_headroom_probe.runner import (
    PHASE_BIII_STATUS,
    bank_step_b_payload,
    emit_bank_artifacts,
)


CLAIM_CEILING_TEXT = """BORROW-FIRST env-selection STEP-B (B-iii): bounded NEGATIVE. No borrowed symbolic env cleared the
headroom bar under the frozen fair floor. bsuite memory_len/0, memory_size/0, umbrella_length/0 =
SATURATED_BY_LEGAL_OBSERVATION_DECODER (target trivially decodable from the full legal observation
history; interface-level determination under the equal-access full-history O, NOT a universal claim
about bsuite). MiniGrid MemoryS13Random + KeyCorridorS3R1 = DROP_INVALID_TARGET_NOT_O_DETERMINED.
dm_alchemy = DROP_UNAVAILABLE. probe_valid = true (POS E* = HEADROOM, NEG 5a846d5 = SATURATED). The
only HEADROOM is the internal bespoke control E*, a privileged-ceiling gap per R4(a), NOT
mechanism-relevant. Proves env-selection headroom bits + probe-validity only. Does NOT prove
mechanism validity, learning, transfer, survival, agency, autonomy, emotion, self-awareness,
consciousness, or EGO/companion readiness."""


def test_bank_payload_derives_bounded_negative_from_controls_and_borrowed_manifest():
    payload = bank_step_b_payload(seed=20260708)

    assert payload["phase"] == PHASE_BIII_STATUS
    assert payload["probe_valid"]["probe_valid"] is True
    assert payload["control_verdicts"] == {
        "POS_INTERNAL_ESTAR": "HEADROOM",
        "NEG_5A846D5_SCOUT": "SATURATED",
    }
    assert payload["overall_verdict"] == "BOUNDED_NEGATIVE_NO_BORROWED_HEADROOM"
    assert payload["result"]["overall_verdict"] == payload["overall_verdict"]
    assert payload["result"]["claim_ceiling"] == CLAIM_CEILING_TEXT

    assert payload["per_env_verdicts"] == {
        "POS_INTERNAL_ESTAR": "HEADROOM",
        "NEG_5A846D5_SCOUT": "SATURATED",
        "bsuite:memory_len/0": "SATURATED_BY_LEGAL_OBSERVATION_DECODER",
        "bsuite:memory_size/0": "SATURATED_BY_LEGAL_OBSERVATION_DECODER",
        "bsuite:umbrella_length/0": "SATURATED_BY_LEGAL_OBSERVATION_DECODER",
        "minigrid:MiniGrid-MemoryS13Random-v0": "DROP_INVALID_TARGET_NOT_O_DETERMINED",
        "minigrid:MiniGrid-KeyCorridorS3R1-v0": "DROP_INVALID_TARGET_NOT_O_DETERMINED",
        "dm_alchemy:symbolic_default": "DROP_UNAVAILABLE",
    }
    assert payload["headroom_envs"] == ["POS_INTERNAL_ESTAR"]
    assert payload["borrowed_headroom_envs"] == []
    assert payload["hard_gates"]["passed"] is True
    assert payload["candidate_envs_scored"] == []


def test_bank_payload_extends_baseline_and_trace_with_borrowed_admission_rows():
    payload = bank_step_b_payload(seed=20260708)

    assert "per_control" in payload["baseline_comparison"]
    summary = payload["baseline_comparison"]["borrowed_admission_summary"]
    assert set(summary) == {
        "bsuite:memory_len/0",
        "bsuite:memory_size/0",
        "bsuite:umbrella_length/0",
        "minigrid:MiniGrid-MemoryS13Random-v0",
        "minigrid:MiniGrid-KeyCorridorS3R1-v0",
        "dm_alchemy:symbolic_default",
    }
    assert summary["bsuite:memory_len/0"]["verdict"] == "SATURATED_BY_LEGAL_OBSERVATION_DECODER"
    assert summary["bsuite:memory_len/0"]["oracle_from_O"]["score"] == 1.0
    assert summary["dm_alchemy:symbolic_default"]["verdict"] == "DROP_UNAVAILABLE"

    borrowed_rows = [
        row for row in payload["trace_rows"] if row["producer_function"] == "_borrowed_admission_trace_rows"
    ]
    assert len(borrowed_rows) == 6
    for row in borrowed_rows:
        assert row["phase"] == PHASE_BIII_STATUS
        assert row["seed"] == 20260708
        assert row["adapter_sha256"]
        assert row["verdict"] == summary[row["env_id"]]["verdict"]
        assert row["input_boundary"] in {
            "record.O only; no private env state, y, y_star, rewards, filenames, or audit labels",
            "not_applicable_dropped_before_record_building",
        }


def test_emit_bank_artifacts_writes_only_step_b_bank_files(tmp_path):
    emitted = emit_bank_artifacts(artifact_dir=tmp_path, seed=20260708)

    assert emitted["hard_gates_pass"] is True
    assert emitted["replay_report"]["bit_exact"] is True
    expected_files = {
        "result.json",
        "reuse_matrix.json",
        "baseline_comparison.json",
        "replay_report.json",
        "trace.jsonl",
        "claim_ceiling.txt",
        "failure_manifest.json",
    }
    assert {path.name for path in tmp_path.iterdir()} == expected_files
    assert (tmp_path / "claim_ceiling.txt").read_text(encoding="utf-8") == CLAIM_CEILING_TEXT + "\n"
    result = json.loads((tmp_path / "result.json").read_text(encoding="utf-8"))
    failure = json.loads((tmp_path / "failure_manifest.json").read_text(encoding="utf-8"))
    assert result["overall_verdict"] == "BOUNDED_NEGATIVE_NO_BORROWED_HEADROOM"
    assert result["replay_bit_exact"] is True
    assert result["artifact_files"] == sorted(expected_files)
    assert failure["hard_failures"] == []
    assert {row["verdict"] for row in failure["failures"]} == {
        "DROP_INVALID_TARGET_NOT_O_DETERMINED",
        "DROP_UNAVAILABLE",
    }
