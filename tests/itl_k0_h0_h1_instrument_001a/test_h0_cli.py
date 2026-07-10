from __future__ import annotations

from argparse import Namespace

import pytest

from itl_k0_h0_h1_instrument_001a.h0_cli import PHASE_D_FILENAMES, build_parser, prebank_run
from itl_k0_h0_h1_instrument_001a.h0_freeze import PHASE_C_PATHS


def test_cli_exposes_freeze_and_single_official_prebank_commands():
    parser = build_parser()
    assert parser.parse_args(["freeze", "--output-dir", "x"]).command == "freeze"
    assert parser.parse_args(["prebank-run", "--freeze-manifest", "f", "--output-dir", "o"]).command == "prebank-run"


def test_phase_path_contract_contains_only_declared_source_test_and_freeze_paths():
    assert len(PHASE_C_PATHS) == 17
    assert len(set(PHASE_C_PATHS)) == len(PHASE_C_PATHS)
    assert all(path.startswith(("src/itl_k0_h0_h1_instrument_001a/", "tests/itl_k0_h0_h1_instrument_001a/", "artifacts/ITL-K0-H0-CODE-FIRST-PREBANK-001A/")) for path in PHASE_C_PATHS)
    assert "failure_manifest.json" in PHASE_D_FILENAMES


def test_official_rerun_is_rejected_before_any_computation(tmp_path):
    output = tmp_path / "out"
    output.mkdir()
    (output / "result.json").write_text("{}", encoding="utf-8")
    with pytest.raises(RuntimeError, match="rerun forbidden"):
        prebank_run(Namespace(root=str(tmp_path), freeze_manifest="missing.json", output_dir=str(output)))
