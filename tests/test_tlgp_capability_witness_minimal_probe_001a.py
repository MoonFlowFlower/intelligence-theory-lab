from pathlib import Path

from src.tlgp_capability_witness_preflight_001a import minimal_probe as mp


def _record(seed, epochs, lr, heldout):
    return {
        "seed": seed,
        "max_epochs": epochs,
        "lr": lr,
        "heldout_balacc": heldout,
        "train_balacc": heldout + 0.1,
    }


def test_frozen_plan_hash_strips_underscore_metadata():
    plan_path = Path("docs/task_cards/TLGP-CAPABILITY-WITNESS-PREFLIGHT-001A.preflight_plan.FROZEN.json")
    assert mp.canonical_plan_sha256(plan_path) == mp.EXPECTED_FROZEN_PLAN_SHA256


def test_trend_report_uses_best_lr_per_seed_and_predeclared_positive_gate():
    records = []
    for seed, best_200, best_800 in [
        (20260710, 0.61, 0.76),
        (20260711, 0.62, 0.77),
        (20260712, 0.63, 0.78),
    ]:
        records.extend([
            _record(seed, 200, 0.001, best_200 - 0.02),
            _record(seed, 200, 0.0003, best_200),
            _record(seed, 600, 0.001, 0.70),
            _record(seed, 600, 0.0003, 0.71),
            _record(seed, 800, 0.001, best_800),
            _record(seed, 800, 0.0003, best_800 - 0.01),
        ])

    report = mp.compute_probe_trend_report(records)

    assert report["verdict"] == "trend_positive"
    assert report["heldout_mean_by_budget"]["200"] == 0.62
    assert report["heldout_mean_by_budget"]["800"] == 0.77
    assert report["delta_800_minus_200"] == 0.15


def test_trend_report_preserves_flat_gate_without_calling_it_route_closed():
    records = []
    for seed in [20260710, 20260711, 20260712]:
        records.extend([
            _record(seed, 200, 0.001, 0.62),
            _record(seed, 200, 0.0003, 0.63),
            _record(seed, 600, 0.001, 0.64),
            _record(seed, 600, 0.0003, 0.65),
            _record(seed, 800, 0.001, 0.65),
            _record(seed, 800, 0.0003, 0.66),
        ])

    report = mp.compute_probe_trend_report(records)

    assert report["verdict"] == "trend_flat"
    assert report["route_claim_authorized"] is False


def test_route_input_uses_800_epoch_best_per_seed_and_keeps_probe_underpowered():
    records = [
        _record(20260710, 800, 0.001, 0.70),
        _record(20260710, 800, 0.0003, 0.72),
        _record(20260711, 800, 0.001, 0.71),
        _record(20260711, 800, 0.0003, 0.69),
        _record(20260712, 800, 0.001, 0.73),
        _record(20260712, 800, 0.0003, 0.68),
    ]
    fair = {
        "lookup": 0.31,
        "count_table": 0.32,
        "predict_all": 0.20,
        "majority": 0.20,
        "no_adaptation": 0.20,
    }

    route_input = mp.build_route_decision_input(records, ideal_balacc=1.0, fair_baseline=fair, leakage_clean=True)

    assert route_input["rung"] == "rung0"
    assert route_input["n_seeds"] == 3
    assert route_input["learner_per_seed_balacc"]["in_context_transformer"] == [0.72, 0.71, 0.73]
    assert route_input["fair_baseline_balacc"]["graph_cache"] == 0.32
