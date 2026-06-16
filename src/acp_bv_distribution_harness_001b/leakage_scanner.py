from __future__ import annotations

import ast
import inspect
import re
from pathlib import Path
from typing import Any

from . import baselines, code_path_hash, sha256_json, sha256_text, source_path_for


LEAKAGE_CLASSES = [
    "observation_name_leakage",
    "action_name_leakage",
    "filename_leakage",
    "fixture_name_leakage",
    "candidate_authored_alias_leakage",
    "future_observation_leakage",
    "hidden_truth_label_leakage",
    "answer_encoding_metadata_leakage",
]


def _normalize(value: str) -> str:
    return re.sub(r"[^a-z0-9]", "", value.lower())


def _walk(value: Any, path: str = "") -> list[tuple[str, Any]]:
    rows = [(path, value)]
    if isinstance(value, dict):
        for key, nested in value.items():
            next_path = f"{path}.{key}" if path else str(key)
            rows.extend(_walk(nested, next_path))
    elif isinstance(value, list):
        for index, nested in enumerate(value):
            rows.extend(_walk(nested, f"{path}[{index}]"))
    return rows


def scan_payload(payload: dict[str, Any]) -> dict[str, Any]:
    hits = []
    for path, value in _walk(payload):
        normalized_path = _normalize(path)
        normalized_value = _normalize(str(value)) if isinstance(value, str) else ""
        if "observation" in normalized_path and any(token in normalized_path for token in ("answer", "truth", "target")):
            hits.append({"leakage_class": "observation_name_leakage", "path": path})
        if "action" in normalized_path and any(token in normalized_value for token in ("answer", "truth", "oracle", "best")):
            hits.append({"leakage_class": "action_name_leakage", "path": path})
        if any(token in normalized_path for token in ("filename", "filepath", "path")) and any(
            token in normalized_value for token in ("truth", "answer", "oracle")
        ):
            hits.append({"leakage_class": "filename_leakage", "path": path})
        if "fixture" in normalized_path and any(token in normalized_value for token in ("truth", "answer", "oracle")):
            hits.append({"leakage_class": "fixture_name_leakage", "path": path})
        if "alias" in normalized_path and any(token in normalized_value for token in ("truth", "answer", "target", "oracle")):
            hits.append({"leakage_class": "candidate_authored_alias_leakage", "path": path})
        if "future" in normalized_path and "observation" in normalized_path:
            hits.append({"leakage_class": "future_observation_leakage", "path": path})
        if "hidden" in normalized_path and any(token in normalized_path for token in ("truth", "label", "target")):
            hits.append({"leakage_class": "hidden_truth_label_leakage", "path": path})
        if "metadata" in normalized_path and any(token in normalized_value for token in ("encodedanswer", "answerencoding", "truthcode")):
            hits.append({"leakage_class": "answer_encoding_metadata_leakage", "path": path})
    return {
        "producer_function": "scan_payload",
        "hits": hits,
        "detected_classes": sorted({hit["leakage_class"] for hit in hits}),
        "verdict": "blocked" if hits else "clean",
    }


def _runtime_id(run_id: str, leakage_class: str) -> str:
    return f"rt_{sha256_text(run_id + leakage_class)[:16]}"


def _variants(run_id: str, leakage_class: str) -> list[dict[str, Any]]:
    runtime_id = _runtime_id(run_id, leakage_class)
    predefined: dict[str, Any]
    runtime: dict[str, Any]
    if leakage_class == "observation_name_leakage":
        predefined = {"observation": {"answer_target_probe": 1}}
        runtime = {"observation": {f"{runtime_id}_truth_target": 1}}
    elif leakage_class == "action_name_leakage":
        predefined = {"candidate_outputs": [{"action": "answer::probe"}]}
        runtime = {"candidate_outputs": [{"action": f"oracle_best_{runtime_id}"}]}
    elif leakage_class == "filename_leakage":
        predefined = {"filename": "fixture.answer.json"}
        runtime = {"file_path": f"{runtime_id}.truth.json"}
    elif leakage_class == "fixture_name_leakage":
        predefined = {"fixture_name": "oracle_answer_fixture"}
        runtime = {"fixture_id": f"truth_fixture_{runtime_id}"}
    elif leakage_class == "candidate_authored_alias_leakage":
        predefined = {"candidate_alias": "answer_target"}
        runtime = {"aliases": {"candidate_field": f"oracle_target_{runtime_id}"}}
    elif leakage_class == "future_observation_leakage":
        predefined = {"future_observation": {"signal_code": 3}}
        runtime = {f"future_observation_{runtime_id}": {"risk_code": 2}}
    elif leakage_class == "hidden_truth_label_leakage":
        predefined = {"hidden_truth_label": 1}
        runtime = {f"hidden_target_{runtime_id}": 2}
    elif leakage_class == "answer_encoding_metadata_leakage":
        predefined = {"metadata": {"payload": "encoded_answer:probe"}}
        runtime = {"metadata": {"payload": f"truthcode::{runtime_id}"}}
    else:
        raise ValueError(leakage_class)
    return [
        {"variant_id": f"{leakage_class}.predeclared", "runtime_or_heldout": False, "payload": predefined},
        {"variant_id": runtime_id, "runtime_or_heldout": True, "payload": runtime},
    ]


def run_leakage_positive_controls(*, run_id: str, output_artifact_path: Path) -> dict[str, Any]:
    class_results = {}
    runtime_ids = []
    for leakage_class in LEAKAGE_CLASSES:
        variants = []
        runtime_detected = False
        for variant in _variants(run_id, leakage_class):
            scan = scan_payload(variant["payload"])
            detected = leakage_class in scan["detected_classes"]
            if variant["runtime_or_heldout"]:
                runtime_detected = detected
                runtime_ids.append(variant["variant_id"])
            variants.append(
                {
                    "variant_id": variant["variant_id"],
                    "runtime_or_heldout": variant["runtime_or_heldout"],
                    "detected": detected,
                    "scan": scan,
                }
            )
        class_results[leakage_class] = {
            "variants": variants,
            "runtime_or_heldout_variant_detected": runtime_detected,
        }
    report = {
        "producer_function": "run_leakage_positive_controls",
        "run_id": run_id,
        "class_results": class_results,
        "runtime_generated_identifiers": runtime_ids,
        "all_runtime_variants_detected": all(
            row["runtime_or_heldout_variant_detected"] for row in class_results.values()
        ),
        "all_classes_have_two_variants": all(len(row["variants"]) >= 2 for row in class_results.values()),
        "output_artifact_path": output_artifact_path.as_posix(),
    }
    report["validation"] = validate_leakage_positive_controls(report)
    return report


def _source_literals() -> set[str]:
    source = Path(inspect.getsourcefile(scan_payload) or __file__).read_text(encoding="utf-8")
    tree = ast.parse(source)
    literals = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            literals.add(node.value)
    return literals


def audit_scanner_literals(runtime_generated_identifiers: list[str], *, output_artifact_path: Path) -> dict[str, Any]:
    source_path = Path(inspect.getsourcefile(scan_payload) or __file__)
    source_text = source_path.read_text(encoding="utf-8")
    literals = _source_literals()
    exact_conflicts = [identifier for identifier in runtime_generated_identifiers if identifier in literals]
    text_conflicts = [identifier for identifier in runtime_generated_identifiers if identifier in source_text]
    return {
        "producer_function": "audit_scanner_literals",
        "scanner_source_path": source_path.as_posix(),
        "runtime_generated_identifiers": runtime_generated_identifiers,
        "scanner_source_literal_count": len(literals),
        "literal_conflicts": exact_conflicts,
        "source_text_conflicts": text_conflicts,
        "no_runtime_identifier_in_source_literals": not exact_conflicts,
        "no_runtime_identifier_in_source_text": not text_conflicts,
        "blocking_verdict": None if not exact_conflicts and not text_conflicts else "blocked_by_whitelist_leakage_scanner",
        "output_artifact_path": output_artifact_path.as_posix(),
    }


def validate_leakage_positive_controls(report: dict[str, Any]) -> dict[str, Any]:
    class_results = report.get("class_results", {})
    runtime_variants_detected = all(
        row.get("runtime_or_heldout_variant_detected") is True
        for row in class_results.values()
    )
    classes_have_two_variants = all(
        len(row.get("variants", [])) >= 2
        for row in class_results.values()
    )
    passed = bool(class_results) and runtime_variants_detected and classes_have_two_variants
    return {
        "producer_function": "validate_leakage_positive_controls",
        "passed": passed,
        "blocking_verdict": None if passed else "blocked_by_whitelist_leakage_scanner",
    }


LEGAL_OBSERVATION_KEYS = {
    "signal_code",
    "topology_code",
    "risk_code",
    "phase_code",
    "available_actions",
}


def _forbidden_observation_hits(datasets: list[dict[str, Any]]) -> list[dict[str, Any]]:
    hits = []
    forbidden_tokens = ("truth", "target", "answer", "oracle", "hidden", "future", "label")
    for dataset in datasets:
        for split in ("train", "heldout"):
            for episode in dataset.get(split, []):
                for key, value in episode.get("observation", {}).items():
                    normalized = _normalize(str(key))
                    if key not in LEGAL_OBSERVATION_KEYS or any(token in normalized for token in forbidden_tokens):
                        hits.append(
                            {
                                "seed": dataset["seed"],
                                "split": split,
                                "episode_id": episode["episode_id"],
                                "observation_key": key,
                                "sample_value_hash": sha256_text(str(value)),
                            }
                        )
    return hits


def run_solvability_preflight(
    *,
    datasets: list[dict[str, Any]],
    run_id: str,
    output_artifact_path: Path,
) -> dict[str, Any]:
    scores = []
    for dataset in datasets:
        outputs = baselines.parametric_modular_linear_baseline(dataset["train"], dataset["heldout"])
        scores.append(baselines.score_outputs(dataset["heldout"], outputs))
    forbidden_hits = _forbidden_observation_hits(datasets)
    legal_score = round(sum(scores) / len(scores), 6) if scores else 0.0
    leaking = bool(forbidden_hits)
    evidence_payload = {
        "scores": scores,
        "forbidden_hits": forbidden_hits,
        "dataset_seeds": [dataset["seed"] for dataset in datasets],
    }
    return {
        "producer_function": "run_solvability_preflight",
        "run_id": run_id,
        "legal_solvability_detected": legal_score >= 0.95,
        "legal_channel_parametric_score": legal_score,
        "leaking_oracle_solvability_detected": leaking,
        "hidden_truth_labels_required": any("hidden" in _normalize(hit["observation_key"]) for hit in forbidden_hits),
        "future_observations_required": any("future" in _normalize(hit["observation_key"]) for hit in forbidden_hits),
        "candidate_authored_aliases_required": any("alias" in _normalize(hit["observation_key"]) for hit in forbidden_hits),
        "forbidden_observation_hits": forbidden_hits,
        "verdict": "blocked_by_leaking_oracle_invalidity" if leaking else "legal_solvability_without_leaking_oracle",
        "seed": "multi_seed",
        "context_episode_ids": [str(dataset["seed"]) for dataset in datasets],
        "aggregation_method": "parametric_recovery_from_legal_channels_plus_forbidden_observation_key_scan",
        "code_path_hash": code_path_hash(run_solvability_preflight),
        "source_path": source_path_for(run_solvability_preflight),
        "evidence_hash": sha256_json(evidence_payload),
        "output_artifact_path": output_artifact_path.as_posix(),
    }
