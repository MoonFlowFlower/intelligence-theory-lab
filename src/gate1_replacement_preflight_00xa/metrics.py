from __future__ import annotations


CEILING_BAND_FLOOR = 0.87
TARGET_CEILING_MINIMUM = 0.90
EQUIVALENCE_BAND = 0.03
PER_CLASS_FLOOR = 0.85
PARTIAL_INFERABILITY_MARGIN = 0.06

FORBIDDEN_SINGLE_SIDED_METRICS = {
    "recall_only",
    "precision_only",
    "coverage_only",
    "specificity_only",
    "abstention_only",
    "size_only",
}


def _safe_div(numerator: float, denominator: float) -> float:
    return numerator / denominator if denominator else 0.0


def _class_prf(y_true: list[bool], y_pred: list[bool], label: bool) -> dict:
    tp = sum(1 for truth, pred in zip(y_true, y_pred) if truth == label and pred == label)
    fp = sum(1 for truth, pred in zip(y_true, y_pred) if truth != label and pred == label)
    fn = sum(1 for truth, pred in zip(y_true, y_pred) if truth == label and pred != label)
    precision = _safe_div(tp, tp + fp)
    recall = _safe_div(tp, tp + fn)
    f1 = _safe_div(2 * precision * recall, precision + recall)
    return {"precision": precision, "recall": recall, "f1": f1, "tp": tp, "fp": fp, "fn": fn}


def compute_binary_macro_f1(y_true: list[bool], y_pred: list[bool]) -> dict:
    if len(y_true) != len(y_pred):
        raise ValueError("truth and prediction lengths differ")
    positive = _class_prf(y_true, y_pred, True)
    negative = _class_prf(y_true, y_pred, False)
    false_positive_count = sum(1 for truth, pred in zip(y_true, y_pred) if not truth and pred)
    false_negative_count = sum(1 for truth, pred in zip(y_true, y_pred) if truth and not pred)
    true_positive_count = sum(1 for truth, pred in zip(y_true, y_pred) if truth and pred)
    true_negative_count = sum(1 for truth, pred in zip(y_true, y_pred) if not truth and not pred)
    macro_f1 = (positive["f1"] + negative["f1"]) / 2
    return {
        "metric_id": "macro_f1_beta_1_binary",
        "beta": 1.0,
        "macro_f1": macro_f1,
        "per_class": {"true": positive, "false": negative},
        "confusion_counts": {
            "true_positive": true_positive_count,
            "true_negative": true_negative_count,
            "false_positive": false_positive_count,
            "false_negative": false_negative_count,
        },
        "false_positive_count": false_positive_count,
        "false_negative_count": false_negative_count,
        "balanced_metric": True,
    }


def validate_metric_contract(contract: dict) -> dict:
    errors = []
    primary = contract.get("primary_metric")
    if primary in FORBIDDEN_SINGLE_SIDED_METRICS:
        errors.append("single_sided_metric_forbidden")
    if primary != "macro_f1":
        errors.append("primary_metric_must_be_macro_f1")
    if contract.get("beta") != 1.0:
        errors.append("beta_must_equal_1_0")
    if not contract.get("reports_precision") or not contract.get("reports_recall"):
        errors.append("precision_and_recall_required")
    if contract.get("equivalence_band", EQUIVALENCE_BAND) != EQUIVALENCE_BAND:
        errors.append("equivalence_band_must_equal_0_03")
    return {"valid": not errors, "errors": errors, "consumed_by_final_verdict": True}


def metric_clears_admission_floors(metric: dict) -> bool:
    if metric.get("macro_f1", 0.0) < TARGET_CEILING_MINIMUM:
        return False
    per_class = metric.get("per_class", {})
    return all(
        per_class.get(label, {}).get(component, 0.0) >= PER_CLASS_FLOOR
        for label in ("true", "false")
        for component in ("precision", "recall")
    )
