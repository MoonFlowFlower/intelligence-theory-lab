from __future__ import annotations

from copy import deepcopy

from .baselines import code_path_hash
from .spec_loader import visible_bundle


LEAK_TOKENS = {
    "answer_key",
    "hidden_target",
    "planted_truth",
    "admissible_for_candidate_card_drafting_only",
    "target_label",
}


def _scan_value(value, path: str, detections: list[dict]) -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            key_text = str(key).lower()
            for token in LEAK_TOKENS:
                if token in key_text:
                    detections.append({"detection_id": f"leak_key:{path}/{key}", "token": token, "path": f"{path}/{key}"})
            _scan_value(child, f"{path}/{key}", detections)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _scan_value(child, f"{path}[{index}]", detections)
    elif isinstance(value, str):
        text = value.lower()
        for token in LEAK_TOKENS:
            if token in text:
                detections.append({"detection_id": f"leak_value:{path}", "token": token, "path": path})


def scan_visible_admission_path(visible: dict) -> dict:
    detections: list[dict] = []
    _scan_value(visible, "$", detections)
    return {
        "producer_function": "gate1_replacement_preflight_00xa.leakage.scan_visible_admission_path",
        "input_artifacts": ["visible_candidate_free_bundle"],
        "aggregation_rule": "recursive_forbidden_token_scan_over_visible_admission_path",
        "code_path_hash": code_path_hash(scan_visible_admission_path),
        "detected": detections,
    }


def _inject_positive_control(visible: dict) -> dict:
    injected = deepcopy(visible)
    injected["episodes"][0]["visible_state"]["observable_features"]["answer_key_label"] = (
        "admissible_for_candidate_card_drafting_only"
    )
    return injected


def _remove_positive_control(injected: dict) -> dict:
    cleaned = deepcopy(injected)
    cleaned["episodes"][0]["visible_state"]["observable_features"].pop("answer_key_label", None)
    return cleaned


def run_leakage_controls(bundle: dict, run_id: str) -> dict:
    clean_visible = visible_bundle(bundle)
    injected = _inject_positive_control(clean_visible)
    removed = _remove_positive_control(injected)
    clean_scan = scan_visible_admission_path(clean_visible)
    injected_scan = scan_visible_admission_path(injected)
    removed_scan = scan_visible_admission_path(removed)
    detected_id = injected_scan["detected"][0]["detection_id"] if injected_scan["detected"] else None
    positive_control = {
        "control_id": "leakage_positive_control_visible_answer_key_label",
        "same_admission_path": True,
        "injected_scan": injected_scan,
        "removed_scan": removed_scan,
        "detected_id": detected_id,
        "detected": bool(detected_id),
        "removal_removes_detection": not removed_scan["detected"],
        "consumed_by_final_verdict": True,
    }
    return {
        "schema_version": "gate1_replacement_preflight_00xa_leakage_v1",
        "run_id": run_id,
        "clean_scan": clean_scan,
        "positive_control": positive_control,
        "producer_function": "gate1_replacement_preflight_00xa.leakage.run_leakage_controls",
        "input_artifacts": ["candidate_free_surface_bundle"],
        "aggregation_rule": "clean_scan_plus_fail_able_positive_control",
        "code_path_hash": code_path_hash(run_leakage_controls),
        "consumed_by_final_verdict": True,
    }
