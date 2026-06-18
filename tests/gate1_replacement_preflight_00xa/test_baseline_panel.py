import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


def _panel_rows():
    from gate1_replacement_preflight_00xa.baselines import run_baseline_panel
    from gate1_replacement_preflight_00xa.spec_loader import build_candidate_free_surface_bundle

    bundle = build_candidate_free_surface_bundle(run_id="pytest-panel", seeds=range(4001, 4041))
    return run_baseline_panel(bundle, run_id="pytest-panel")["rows"]


def test_baseline_panel_invokes_all_mandatory_challengers_as_consumed_callable_rows():
    from gate1_replacement_preflight_00xa.baselines import MANDATORY_BASELINE_IDS

    rows = _panel_rows()
    by_id = {row["baseline_id"]: row for row in rows}

    assert set(MANDATORY_BASELINE_IDS) <= set(by_id)
    for baseline_id in MANDATORY_BASELINE_IDS:
        row = by_id[baseline_id]
        assert row["invoked"] is True
        assert row["independence_status"] == "independent_callable"
        assert row["consumed_by_final_verdict"] is True
        assert row["producer_function"].startswith("gate1_replacement_preflight_00xa.")
        assert row["code_path_hash"] and len(row["code_path_hash"]) == 64


def test_missing_graph_cache_challenger_blocks_admissibility():
    from gate1_replacement_preflight_00xa.verdict import minimal_valid_context, validate_baseline_panel

    context = minimal_valid_context()
    context["baseline_rows_by_id"].pop("graph_lookup")

    validation = validate_baseline_panel(context)

    assert validation["valid"] is False
    assert "missing_required_baseline:graph_lookup" in validation["errors"]


def test_graph_cache_saturation_rejects_baseline_saturated():
    from gate1_replacement_preflight_00xa.verdict import derive_final_verdict, minimal_valid_context

    context = minimal_valid_context()
    context["baseline_rows_by_id"]["graph_lookup"]["metric"]["macro_f1"] = 1.0
    context["oracle"]["visible_channel_oracle"]["metric"]["macro_f1"] = 1.0

    verdict = derive_final_verdict(context)

    assert verdict["final_verdict"] == "rejected_baseline_saturated"
    assert verdict["terminal_reason_id"] == "fair_baseline_ties_oracle_within_equivalence_band"


def test_exhaustive_legal_query_saturation_rejects_baseline_saturated():
    from gate1_replacement_preflight_00xa.verdict import derive_final_verdict, minimal_valid_context

    context = minimal_valid_context()
    context["baseline_rows_by_id"]["exhaustive_legal_query"]["metric"]["macro_f1"] = 1.0
    context["oracle"]["visible_channel_oracle"]["metric"]["macro_f1"] = 1.0

    verdict = derive_final_verdict(context)

    assert verdict["final_verdict"] == "rejected_baseline_saturated"
    assert verdict["terminal_reason_id"] == "fair_baseline_ties_oracle_within_equivalence_band"
