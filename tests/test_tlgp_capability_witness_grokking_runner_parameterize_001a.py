import hashlib
import inspect
from pathlib import Path

from src.tlgp_capability_witness_preflight_001a import grokking_probe as gp


def test_run_probe_defaults_preserve_001a_driver_contract():
    signature = inspect.signature(gp.run_probe)

    weight_decays = signature.parameters["weight_decays"].default
    out_subdir = signature.parameters["out_subdir"].default
    frozen_design_path = signature.parameters["frozen_design_path"].default

    assert weight_decays is gp.WEIGHT_DECAYS
    assert weight_decays == [0.1, 1.0]
    assert out_subdir == "GROKKING_PROBE_001A"
    assert Path(frozen_design_path).resolve() == gp.FROZEN_DESIGN_PATH.resolve()


def test_relative_frozen_design_path_resolves_under_repo_root():
    resolved = gp.resolve_frozen_design_path(
        "docs/task_cards/TLGP-CAPABILITY-WITNESS-GROKKING-PROBE-001B.frozen_design.json"
    )

    assert resolved == (
        gp.REPO_ROOT
        / "docs"
        / "task_cards"
        / "TLGP-CAPABILITY-WITNESS-GROKKING-PROBE-001B.frozen_design.json"
    ).resolve()


def test_train_one_grokking_run_signature_and_source_remain_unchanged():
    signature = inspect.signature(gp.train_one_grokking_run)
    assert str(signature) == (
        "(*, run_id: 'str', seed: 'int', weight_decay: 'float', train_eps, "
        "heldout_eps, train_t, heldout_t, curve_handle) -> 'dict[str, Any]'"
    )

    source_sha256 = hashlib.sha256(
        inspect.getsource(gp.train_one_grokking_run).encode("utf-8")
    ).hexdigest()
    assert source_sha256 == "dcbb16650eff12f8c2ac53da5b1cb08ee98e20141bbae6cb05df3a5a3d6bd69b"
