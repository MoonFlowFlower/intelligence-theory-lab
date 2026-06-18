import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


def test_macro_f1_uses_both_classes_and_blocks_predict_all_shortcut():
    from gate1_replacement_preflight_00xa.metrics import compute_binary_macro_f1

    y_true = [True, True, False, False]
    y_pred = [True, True, True, True]

    metric = compute_binary_macro_f1(y_true, y_pred)

    assert metric["macro_f1"] < 0.87
    assert metric["per_class"]["false"]["recall"] == 0.0
    assert metric["false_positive_count"] == 2
    assert metric["false_negative_count"] == 0


def test_single_sided_metric_cannot_support_admission():
    from gate1_replacement_preflight_00xa.metrics import validate_metric_contract

    result = validate_metric_contract(
        {
            "primary_metric": "recall_only",
            "reports_precision": False,
            "reports_recall": True,
            "beta": None,
        }
    )

    assert result["valid"] is False
    assert "single_sided_metric_forbidden" in result["errors"]


def test_predict_all_at_ceiling_forces_metric_degenerate_rejection():
    from gate1_replacement_preflight_00xa.verdict import derive_final_verdict, minimal_valid_context

    context = minimal_valid_context()
    context["baseline_rows_by_id"]["predict_all"]["metric"]["macro_f1"] = 0.91

    verdict = derive_final_verdict(context)

    assert verdict["final_verdict"] == "rejected_metric_degenerate"
    assert verdict["terminal_reason_id"] == "degenerate_predictor_reached_ceiling_band"


def test_size_only_sweep_at_ceiling_forces_metric_degenerate_rejection():
    from gate1_replacement_preflight_00xa.verdict import derive_final_verdict, minimal_valid_context

    context = minimal_valid_context()
    context["baseline_rows_by_id"]["size_only_sweep_0_to_N"]["metric"]["macro_f1"] = 0.88

    verdict = derive_final_verdict(context)

    assert verdict["final_verdict"] == "rejected_metric_degenerate"
    assert verdict["terminal_reason_id"] == "size_only_sweep_reached_ceiling_band"
