import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


def test_live_surface_spec_hash_matches_frozen_value():
    from gate1_replacement_preflight_00xa.readback import (
        EXPECTED_SURFACE_SPEC_SHA256,
        verify_surface_spec_hash,
    )

    result = verify_surface_spec_hash(ROOT)

    assert result["ok"] is True
    assert result["verdict"] == "surface_spec_hash_verified"
    assert result["actual_sha256"] == EXPECTED_SURFACE_SPEC_SHA256
    assert result["expected_sha256"] == EXPECTED_SURFACE_SPEC_SHA256
    assert result["readback_channel"] == "canonical_file_api_read_bytes"


def test_missing_surface_spec_fails_closed(tmp_path):
    from gate1_replacement_preflight_00xa.readback import verify_surface_spec_hash

    result = verify_surface_spec_hash(tmp_path)

    assert result["ok"] is False
    assert result["verdict"] == "blocked_missing_candidate_free_surface_spec"


def test_spec_hash_mismatch_fails_as_candidate_authored_or_mutated(tmp_path):
    from gate1_replacement_preflight_00xa.readback import SURFACE_SPEC_PATH, verify_surface_spec_hash

    path = tmp_path / SURFACE_SPEC_PATH
    path.parent.mkdir(parents=True)
    path.write_text("mutated spec\n", encoding="utf-8")

    result = verify_surface_spec_hash(tmp_path)

    assert result["ok"] is False
    assert result["verdict"] == "blocked_candidate_authored_or_mutated_surface_spec"
    assert result["actual_sha256"] != result["expected_sha256"]


def test_implementer_touching_surface_spec_is_a_stop_condition():
    from gate1_replacement_preflight_00xa.readback import SURFACE_SPEC_PATH, verify_surface_spec_hash

    result = verify_surface_spec_hash(ROOT, implementer_touched_paths=[SURFACE_SPEC_PATH])

    assert result["ok"] is False
    assert result["verdict"] == "blocked_candidate_authored_or_mutated_surface_spec"
    assert result["mutation_detected"] is True


def test_required_source_pins_are_read_and_hashed():
    from gate1_replacement_preflight_00xa.readback import REQUIRED_SOURCE_PINS, read_source_pins

    readback = read_source_pins(ROOT, run_id="pytest-readback")

    assert readback["all_present"] is True
    assert {row["path"] for row in readback["source_pins"]} == set(REQUIRED_SOURCE_PINS)
    assert "src/gate1_replacement_preflight_00xa/spec_loader.py" in REQUIRED_SOURCE_PINS
    assert all(row["sha256"] and len(row["sha256"]) == 64 for row in readback["source_pins"])
    assert all(row["readback_channel"] == "canonical_file_api_read_bytes" for row in readback["source_pins"])
