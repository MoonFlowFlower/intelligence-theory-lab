from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from src.tlgp_001a.world import Episode, Rule
from src.tlgp_001b_r2 import lower_reference as LR
from src.tlgp_capability_witness_preflight_001a import rung3_graph_cache_baselines as GC
from src.tlgp_capability_witness_preflight_001a import rung3_identifiability_adjudicator as ADJ
from src.tlgp_capability_witness_preflight_001a import rung3_identifiability_probe as PROBE


def _episode_for_cache_probe() -> Episode:
    rule = Rule(w=(1, 0, 0), c=0)
    return Episode(
        episode_id=1,
        rule_id=7,
        rule=rule,
        adapt_x=np.array(
            [
                [0, 0, 0],
                [1, 0, 0],
                [2, 0, 0],
                [2, 1, 0],
            ],
            dtype=int,
        ),
        adapt_a=np.array([0, 0, 0, 1], dtype=int),
        adapt_e=np.array([2, 2, 2, 4], dtype=int),
        query_x=np.array(
            [
                [1, 0, 0],
                [4, 4, 4],
            ],
            dtype=int,
        ),
        query_a=np.array([0, 4], dtype=int),
        query_e=np.array([2, 3], dtype=int),
    )


def test_graph_cache_uses_own_map_and_default_not_lower_reference_alias():
    ep = _episode_for_cache_probe()

    pred = GC.successor_map(ep)
    lookup_pred = LR.lookup(ep)
    count_pred = LR.count_table(ep)

    assert pred.tolist() == [2, 0]
    assert lookup_pred.tolist() == [2, 2]
    assert count_pred.tolist() == [2, 2]
    assert GC.graph_cache_is_alias(ep) is False


def test_adjudicator_self_test_reaches_every_terminal_and_verifies_prereg():
    report = ADJ.self_test()

    assert report["prereg_sha256"] == ADJ.FROZEN_PREREG_SHA256
    assert set(report["reachable_terminals"]) == {
        "route_closed_identifiability_ceiling",
        "rung3_headroom_exists_authorize_powered_learner",
        "route_needs_world_rung_redesign",
        "inconclusive_underpowered",
        "invalid_leakage",
    }


def test_adjudicator_uses_lcb_for_headroom_branch():
    decision = ADJ.compute_route_decision(
        {
            "task_id": "unit",
            "split": "rung3_test",
            "controls_passed": True,
            "leakage_clean": True,
            "ideal_degenerate": False,
            "no_adaptation_matches_ideal": False,
            "per_seed_headroom": [0.2] * 10,
            "fair_saturation_seed_count": 0,
            "predict_all_or_majority_match_ideal": False,
        }
    )

    assert decision["route"] == "rung3_headroom_exists_authorize_powered_learner"
    assert decision["detail"]["lcb_headroom"] > decision["detail"]["DELTA"]


def test_adjudicator_keeps_deliberate_negative_control_degeneracy_inconclusive():
    decision = ADJ.compute_route_decision(
        {
            "task_id": "unit",
            "split": "negative_n_adapt_1",
            "control_role": "negative_no_signal",
            "controls_passed": True,
            "leakage_clean": True,
            "ideal_degenerate": True,
            "no_adaptation_matches_ideal": True,
            "per_seed_headroom": [0.0] * 10,
            "fair_saturation_seed_count": 10,
            "predict_all_or_majority_match_ideal": False,
        }
    )

    assert decision["route"] == "inconclusive_underpowered"


def test_probe_frozen_design_hash_matches_recorded_value():
    frozen = PROBE.verify_frozen_design()

    assert frozen["computed_sha256"] == frozen["recorded_sha256"]
    assert frozen["computed_sha256"] == "c2a32ed8612d53186dff54245d9c8c8a86abcdc2f020e78dcd2f6910c2b0d706"


def test_replay_reconstructs_route_input_from_trace_records(tmp_path: Path):
    trace_path = tmp_path / "trace.jsonl"
    records = [
        {
            "seed": 1,
            "split": "rung3_test",
            "ideal_balacc": 0.9,
            "fair_balacc": {"lookup": 0.2, "graph_cache": 0.3},
            "headroom": 0.6,
        },
        {
            "seed": 2,
            "split": "rung3_test",
            "ideal_balacc": 0.8,
            "fair_balacc": {"lookup": 0.25, "graph_cache": 0.35},
            "headroom": 0.45,
        },
    ]
    trace_path.write_text("\n".join(json.dumps(row, sort_keys=True) for row in records) + "\n", encoding="utf-8")

    replay = PROBE.replay_trace(trace_path, controls_passed=True, leakage_clean=True)

    assert replay["route_decision_input"]["per_seed_headroom"] == [0.6, 0.45]
    assert replay["route_decision_input"]["fair_saturation_seed_count"] == 0
    assert replay["route_decision_input"]["n_seeds"] == 2
