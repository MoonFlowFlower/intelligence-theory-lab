import json
from pathlib import Path

import pytest

from src.fsp_pum_env.s3d_certificates import (
    S3D_CERT_CELLS,
    S3D_CPU_HOUR_LIMIT,
    build_s3d_cert_set_specs,
    load_s3d_selected_recipe_hashes,
    macro_balanced_accuracy,
)


ROOT = Path(__file__).resolve().parents[2]
ARTIFACT_ROOT = ROOT / "artifacts" / "FSP-PUM-ENV-IDPROBE-001A"
FROZEN = ARTIFACT_ROOT / "frozen_design.json"


def _design():
    return json.loads(FROZEN.read_text(encoding="utf-8-sig"))


def test_s3d_cert_set_specs_match_frozen_assignment_table_without_heldout_users():
    specs = build_s3d_cert_set_specs(_design())

    assert S3D_CPU_HOUR_LIMIT == 12.0
    assert [spec.cell_id for spec in specs] == [
        "constant_none",
        "constant_saturated",
        "camouflage_off",
        "low_diversity",
        "stable_facts",
        "flat_theta",
        "NULL_env",
    ]
    assert [spec.master_seed for spec in specs] == [20260711, 20260712, 20260713, 20260714, 20260715, 20260716, 20260717]
    assert all(spec.fit_user_range == (0, 639) for spec in specs)
    assert all(spec.eval_user_range == (640, 799) for spec in specs)
    assert all(spec.trajectory_spec.partitions == {"train": {"start_user_id": 0, "count": 800}} for spec in specs)
    assert all(spec.trajectory_spec.turns_per_user == 300 for spec in specs)
    assert {cell.cell_id for cell in S3D_CERT_CELLS} == {spec.cell_id for spec in specs}


def test_s3d_macro_balanced_accuracy_uses_only_present_classes():
    metric = macro_balanced_accuracy([0, 0, 1, 1, 1], [0, 1, 1, 1, 0], alphabet_size=32)

    assert metric == pytest.approx(((1 / 2) + (2 / 3)) / 2)


def test_s3d_selected_recipe_hashes_match_banked_file_sha256s():
    hashes = load_s3d_selected_recipe_hashes(ARTIFACT_ROOT)

    assert hashes["obs_decoder_logreg_selected_recipe.json"].startswith("c331b27db21a")
    assert hashes["obs_decoder_gbt_selected_recipe.json"].startswith("f2a091c9dc3b")
    assert hashes["obs_decoder_gru_selected_recipe.json"].startswith("8341f5d12218")
    assert hashes["seq_full_history_no_action_conditioning_selected_recipe.json"].startswith("723bf89d13af")
    assert hashes[
        "seq_window_with_action_conditioning_W15_no_cross_session_persistence_selected_recipe.json"
    ].startswith("37ae0e00df2a")


def test_s3d_cert_generation_does_not_read_main_trajectory_recipe_files(monkeypatch):
    from src.fsp_pum_env import s3d_certificates

    original_read_text = Path.read_text

    def guarded_read_text(self, *args, **kwargs):
        normalized = str(self).replace("\\", "/")
        if "/trajectory_sets/set_" in normalized:
            raise AssertionError(f"main trajectory recipe read: {self}")
        return original_read_text(self, *args, **kwargs)

    monkeypatch.setattr(Path, "read_text", guarded_read_text)

    manifest = s3d_certificates.generate_s3d_cert_sets_manifest(
        FROZEN,
        ARTIFACT_ROOT / "_pytest_s3d_manifest.json",
        cells=["constant_none"],
    )

    assert manifest["sets"][0]["cell_id"] == "constant_none"
    assert (ARTIFACT_ROOT / "_pytest_s3d_manifest.json").exists()
    (ARTIFACT_ROOT / "_pytest_s3d_manifest.json").unlink()
