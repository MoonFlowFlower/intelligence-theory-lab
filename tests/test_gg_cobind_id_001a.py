"""Tests for GG-COBIND-ID-001A co-binding identifiability probe.

These check the harness is fail-able and the controls behave: positive control sensitive,
negative control specific, balanced regime ties, replay reproduces the verdict.
"""
import os
import sys
import tempfile
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from gg_cobind_id_001a import probe  # noqa: E402


def _by_regime(regime):
    rows = []
    for seed in probe.PREREG["seeds"]:
        rows.extend(probe.run_regime(regime, seed))
    return rows


def test_positive_control_sensitivity():
    """Planted shared rank-1 + extreme imbalance: shared MUST beat independent on poor channels."""
    rows = _by_regime("positive_control")
    wins, tot = probe._poor_channel_win_seeds(rows, probe.PREREG["DELTA_R2"])
    assert wins >= probe.PREREG["consistency_min"], (wins, tot)


def test_negative_control_specificity():
    """No shared score (disjoint drivers): shared MUST NOT beat independent."""
    rows = _by_regime("negative_control")
    wins, tot = probe._poor_channel_win_seeds(rows, probe.PREREG["DELTA_R2"])
    assert wins < probe.PREREG["consistency_min"], (wins, tot)


def test_balanced_ample_independent_reproduces():
    """On balanced+ample data, independent heads reproduce -> shared has no band advantage."""
    rows = _by_regime("balanced_ample")
    reproduces, tot = probe._balanced_independent_reproduces_seeds(rows, probe.PREREG["DELTA_R2"])
    assert reproduces >= probe.PREREG["consistency_min"], (reproduces, tot)


def test_qualitative_co_change_is_nondiscriminating():
    """Independent model (no shared latent) still moves all 3 channels under intervention."""
    B = probe.make_world(0, shared=True)
    L, y, _ = probe.gen_samples(B, probe.PREREG["n_ample"], 1, probe.PREREG["noise_sd"])
    W = probe.fit_independent([L, L, L], [y[:, 0], y[:, 1], y[:, 2]],
                              probe.PREREG["ridge_lambda_grid"], 0)
    g = np.random.default_rng(7)
    d = probe.PREREG["d_L"]
    delta = (probe.predict_independent(W, g.standard_normal((1, d)))
             - probe.predict_independent(W, g.standard_normal((1, d))))[0]
    assert np.all(np.abs(delta) > 1e-6)


def test_replay_matches_result():
    with tempfile.TemporaryDirectory() as td:
        res = probe.main(td)
        rv, _ = probe.replay_from_trace(os.path.join(td, "trace.csv"))
        assert rv == res["verdict"]


def test_delta_band_is_failable():
    """A near-zero band would make 'independent reproduces' impossible; the fixed band admits ties."""
    assert probe.PREREG["DELTA_R2"] > 0.0
