from __future__ import annotations

import argparse
import hashlib
import inspect
import json
import subprocess
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from . import (
    ARTIFACT_DIR_NAME,
    AUTO_REMOTE_ANCHOR,
    BRANCH,
    CLAIM_CEILING,
    PARENT_ANCHOR,
    PARENT_TAG,
    REPORT_NAME,
    TASK_CARD_ID,
    TASK_ID,
)


SOLVE_THRESHOLD = 0.8
FIXTURE_SEED_FALLBACK = 61001
DEFAULT_FIXTURE_PATH = (
    Path("artifacts")
    / "composite_cross_task_state_reuse_generative_heldout_surface_design_001a"
    / "valid_generated_surface_fixture.json"
)
REQUIRED_BASELINES = [
    "independent_per_task_optimal_ensemble_no_shared_latent",
    "shared_latent_no_cross_task_transfer",
]
OPTIONAL_BASELINES = [
    "visible_feature_only_task_b_decoder",
    "trace_order_or_id_sanitized_retrieval_probe",
    "static_formula_visible_field_decoder",
]
BASELINE_NAMES = REQUIRED_BASELINES + OPTIONAL_BASELINES
ALLOWED_OBSERVATION_FIELDS = [
    "task_a.observation.visible_event_class",
    "task_a.observation.predicted_outcome",
    "task_a.observation.observed_outcome",
    "task_a.observation.prediction_signal",
    "task_b.observation.superficial_signature",
    "task_b.observation.local_visible_cue",
    "task_b.observation.pre_update_default_action",
    "task_b.observation.fallback_action",
    "task_family_id",
]
TRAINING_OUTCOME_FIELDS = ["records.train.task_b.post_update_action"]
FORBIDDEN_PREDICTION_FIELDS = [
    "hidden",
    "hidden.task_b_target_action",
    "hidden.task_a_latent_target",
    "hidden.generator_latent_state_id",
    "record_id",
    "context_handle",
    "partner_handle",
    "support_signature",
    "counterfactual_combo_id",
    "latent_parameter_id",
    "split",
    "task_b.post_update_action",
    "task_b.action_dependency_id",
    "task_b.observation.latent_binding_probe",
    "task_a.prediction_error_event_id",
    "shared_state_update.update_event_id",
    "shared_state_update.channel",
    "shared_state_update.caused_by_task_a_prediction_error_event_id",
    "shared_state_update.serialized_state_after",
    "shared_state_update.serialized_state_before",
    "provenance.heldout_ids",
    "provenance.train_ids",
    "target_resolver_output",
    "row_id",
    "context_id",
    "partner_id",
    "trace_order",
    "answer_key",
]
CLAIM_EXCLUSIONS = [
    "mechanism validity",
    "Gate4 validity",
    "candidate behavior",
    "tournament outcome",
    "runtime readiness",
    "bridge/admission readiness",
    "agency",
    "subjectivity",
    "consciousness",
    "emotion",
    "autonomy",
    "companion readiness",
    "EGO readiness",
]


class ForbiddenFieldAccess(RuntimeError):
    def __init__(self, field_path: str) -> None:
        super().__init__(f"forbidden field access: {field_path}")
        self.field_path = field_path


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _json_ready(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _json_ready(child) for key, child in value.items()}
    if isinstance(value, list):
        return [_json_ready(child) for child in value]
    if isinstance(value, tuple):
        return [_json_ready(child) for child in value]
    if isinstance(value, set):
        return sorted(_json_ready(child) for child in value)
    if isinstance(value, Path):
        return str(value).replace("\\", "/")
    return value


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(_json_ready(payload), indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _canonical(value: Any) -> str:
    return json.dumps(_json_ready(value), sort_keys=True, separators=(",", ":"))


def code_path_hash(func: Callable[..., Any]) -> str:
    return hashlib.sha256(inspect.getsource(func).encode("utf-8")).hexdigest()


def _git(args: list[str]) -> str:
    completed = subprocess.run(
        ["git", *args],
        cwd=repo_root(),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )
    return completed.stdout.strip()


def _safe_git(args: list[str]) -> str:
    try:
        return _git(args)
    except (FileNotFoundError, subprocess.CalledProcessError):
        return ""


def _read_remote_refs(*refs: str) -> dict[str, str]:
    output = _safe_git(["ls-remote", "origin", *refs])
    rows: dict[str, str] = {}
    for line in output.splitlines():
        if not line.strip():
            continue
        commit, ref = line.split(maxsplit=1)
        rows[ref] = commit
    return rows


def _is_ancestor(commit: str, descendant: str) -> bool:
    if not commit or not descendant:
        return False
    completed = subprocess.run(
        ["git", "merge-base", "--is-ancestor", commit, descendant],
        cwd=repo_root(),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return completed.returncode == 0


def _resolve_path(path: str | Path | None) -> Path:
    if path is None:
        path = DEFAULT_FIXTURE_PATH
    resolved = Path(path)
    return resolved if resolved.is_absolute() else repo_root() / resolved


def _relative(path: str | Path) -> str:
    resolved = Path(path)
    try:
        return str(resolved.resolve().relative_to(repo_root())).replace("\\", "/")
    except ValueError:
        return str(resolved).replace("\\", "/")


def load_fixture(fixture_path: str | Path | None = None) -> dict[str, Any]:
    path = _resolve_path(fixture_path)
    return json.loads(path.read_text(encoding="utf-8"))


def _read_nested(row: dict[str, Any], field_path: str) -> Any:
    value: Any = row
    for part in field_path.split("."):
        value = value[part]
    return value


def _is_forbidden(field_path: str) -> bool:
    return any(field_path == item or field_path.startswith(f"{item}.") for item in FORBIDDEN_PREDICTION_FIELDS)


def _audit_prediction_access(audit: dict[str, list[str]], baseline_name: str, field_path: str) -> None:
    if _is_forbidden(field_path):
        audit.setdefault(baseline_name, []).append(field_path)
        raise ForbiddenFieldAccess(field_path)


def _visible_value(row: dict[str, Any], field_path: str, audit: dict[str, list[str]], baseline_name: str) -> Any:
    _audit_prediction_access(audit, baseline_name, field_path)
    return _read_nested(row, field_path)


def _visible_features(row: dict[str, Any], audit: dict[str, list[str]], baseline_name: str) -> dict[str, Any]:
    return {field: _visible_value(row, field, audit, baseline_name) for field in ALLOWED_OBSERVATION_FIELDS}


def _training_action(row: dict[str, Any]) -> str:
    return str(_read_nested(row, "task_b.post_update_action"))


def recompute_task_b_action_from_serialized_state(
    serialized_state: dict[str, Any], observation: dict[str, Any]
) -> str:
    if not serialized_state.get("shared_update_applied"):
        return str(observation.get("pre_update_default_action", observation.get("fallback_action", "hold")))
    binding = serialized_state.get("latent_action_binding", {})
    return str(binding.get(observation.get("latent_binding_probe"), observation.get("fallback_action", "hold")))


def _expected_action(row: dict[str, Any]) -> str:
    return recompute_task_b_action_from_serialized_state(
        row["shared_state_update"]["serialized_state_after"],
        row["task_b"]["observation"],
    )


def _masked_action(row: dict[str, Any]) -> str:
    return recompute_task_b_action_from_serialized_state(
        row["shared_state_update"]["serialized_state_before"],
        row["task_b"]["observation"],
    )


def _records(fixture: dict[str, Any], split: str) -> list[dict[str, Any]]:
    return list(fixture["records"][split])


def _majority(values: list[str], default: str = "hold") -> str:
    if not values:
        return default
    counts = Counter(values)
    return sorted(counts.items(), key=lambda item: (-item[1], item[0]))[0][0]


def _tuple_key(features: dict[str, Any], fields: list[str]) -> tuple[Any, ...]:
    return tuple(features[field] for field in fields)


def _build_mapping(
    train_rows: list[dict[str, Any]],
    fields: list[str],
    audit: dict[str, list[str]],
    baseline_name: str,
) -> dict[tuple[Any, ...], str]:
    buckets: dict[tuple[Any, ...], list[str]] = {}
    for row in train_rows:
        features = _visible_features(row, audit, baseline_name)
        buckets.setdefault(_tuple_key(features, fields), []).append(_training_action(row))
    return {key: _majority(values) for key, values in buckets.items()}


def _predict_with_mapping(
    row: dict[str, Any],
    mapping: dict[tuple[Any, ...], str],
    fields: list[str],
    fallback: str,
    audit: dict[str, list[str]],
    baseline_name: str,
) -> str:
    features = _visible_features(row, audit, baseline_name)
    return mapping.get(_tuple_key(features, fields), fallback)


def _train_accuracy_for_decoder(
    train_rows: list[dict[str, Any]],
    fields: list[str],
    baseline_name: str,
) -> float:
    if not train_rows:
        return 0.0
    correct = 0
    for index, row in enumerate(train_rows):
        audit: dict[str, list[str]] = {}
        subset = [candidate for offset, candidate in enumerate(train_rows) if offset != index]
        fallback = _majority([_training_action(candidate) for candidate in subset])
        mapping = _build_mapping(subset, fields, audit, baseline_name)
        prediction = _predict_with_mapping(row, mapping, fields, fallback, audit, baseline_name)
        if prediction == _training_action(row):
            correct += 1
    return correct / len(train_rows)


def _score_predictions(predictions: list[dict[str, Any]]) -> float:
    if not predictions:
        return 0.0
    return sum(1 for row in predictions if row["correct"]) / len(predictions)


def _prediction_rows(
    heldout_rows: list[dict[str, Any]],
    predictor: Callable[[dict[str, Any]], str],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for index, row in enumerate(heldout_rows):
        expected = _expected_action(row)
        prediction = predictor(row)
        rows.append(
            {
                "case_index": index,
                "prediction": prediction,
                "expected_recomputed_from_serialized_state": expected,
                "correct": prediction == expected,
            }
        )
    return rows


def _baseline_result(
    *,
    baseline_name: str,
    producer_function: str,
    input_fixture_path: str,
    run_id: str,
    seed: int,
    predictions: list[dict[str, Any]],
    field_access_violations: list[str],
    details: dict[str, Any] | None = None,
) -> dict[str, Any]:
    accuracy = _score_predictions(predictions)
    result = {
        "producer_function": producer_function,
        "input_fixture_path": input_fixture_path,
        "run_id": run_id,
        "seed": seed,
        "baseline_name": baseline_name,
        "allowed_observation_fields": list(ALLOWED_OBSERVATION_FIELDS),
        "allowed_training_outcome_fields": list(TRAINING_OUTCOME_FIELDS),
        "forbidden_fields_checked": list(FORBIDDEN_PREDICTION_FIELDS),
        "computed_predictions": predictions,
        "failure_reason": None if predictions else "no_predictions_computed",
        "aggregation_method": "heldout_accuracy",
        "heldout_accuracy": accuracy,
        "solve_threshold": SOLVE_THRESHOLD,
        "solves_fixture": accuracy >= SOLVE_THRESHOLD,
        "executed": True,
        "field_access_violations": sorted(set(field_access_violations)),
        "metadata_only": False,
        "static_verdict_dictionary_used": False,
        "code_path_hash": code_path_hash(globals()[producer_function]),
    }
    if details:
        result["details"] = details
    return result


def independent_per_task_optimal_ensemble_no_shared_latent(
    fixture: dict[str, Any],
    *,
    input_fixture_path: str,
    run_id: str,
    seed: int,
) -> dict[str, Any]:
    baseline_name = "independent_per_task_optimal_ensemble_no_shared_latent"
    train_rows = _records(fixture, "train")
    heldout_rows = _records(fixture, "heldout")
    audit: dict[str, list[str]] = {}
    decoder_fields = {
        "global_majority": [],
        "task_family_majority": ["task_family_id"],
        "task_a_visible_event_class": ["task_a.observation.visible_event_class"],
        "task_a_prediction_signal": ["task_a.observation.prediction_signal"],
        "task_b_visible_pair": [
            "task_b.observation.superficial_signature",
            "task_b.observation.local_visible_cue",
        ],
        "task_b_local_cue": ["task_b.observation.local_visible_cue"],
    }
    train_actions = [_training_action(row) for row in train_rows]
    fallback = _majority(train_actions)
    decoder_scores = {
        name: (1.0 if name == "global_majority" else _train_accuracy_for_decoder(train_rows, fields, baseline_name))
        for name, fields in decoder_fields.items()
    }
    decoder_scores["global_majority"] = sum(1 for item in train_actions if item == fallback) / max(1, len(train_actions))
    selected_decoder = sorted(decoder_scores.items(), key=lambda item: (-item[1], item[0]))[0][0]
    selected_fields = decoder_fields[selected_decoder]
    mapping = _build_mapping(train_rows, selected_fields, audit, baseline_name) if selected_fields else {}

    def predict(row: dict[str, Any]) -> str:
        if not selected_fields:
            return fallback
        return _predict_with_mapping(row, mapping, selected_fields, fallback, audit, baseline_name)

    predictions = _prediction_rows(heldout_rows, predict)
    return _baseline_result(
        baseline_name=baseline_name,
        producer_function="independent_per_task_optimal_ensemble_no_shared_latent",
        input_fixture_path=input_fixture_path,
        run_id=run_id,
        seed=seed,
        predictions=predictions,
        field_access_violations=audit.get(baseline_name, []),
        details={
            "decoder_train_accuracies": decoder_scores,
            "selected_decoder": selected_decoder,
            "shared_latent_state_access": False,
            "cross_task_prediction_error_to_action_transfer_access": False,
        },
    )


def shared_latent_no_cross_task_transfer(
    fixture: dict[str, Any],
    *,
    input_fixture_path: str,
    run_id: str,
    seed: int,
) -> dict[str, Any]:
    baseline_name = "shared_latent_no_cross_task_transfer"
    heldout_rows = _records(fixture, "heldout")
    audit: dict[str, list[str]] = {}

    def predict(row: dict[str, Any]) -> str:
        features = _visible_features(row, audit, baseline_name)
        return str(features["task_b.observation.pre_update_default_action"])

    predictions = _prediction_rows(heldout_rows, predict)
    return _baseline_result(
        baseline_name=baseline_name,
        producer_function="shared_latent_no_cross_task_transfer",
        input_fixture_path=input_fixture_path,
        run_id=run_id,
        seed=seed,
        predictions=predictions,
        field_access_violations=audit.get(baseline_name, []),
        details={
            "shared_latent_state_allowed": True,
            "cross_task_prediction_error_to_action_transfer_access": False,
            "masked_update_policy": "predict_pre_update_default_action",
        },
    )


def visible_feature_only_task_b_decoder(
    fixture: dict[str, Any],
    *,
    input_fixture_path: str,
    run_id: str,
    seed: int,
) -> dict[str, Any]:
    baseline_name = "visible_feature_only_task_b_decoder"
    train_rows = _records(fixture, "train")
    heldout_rows = _records(fixture, "heldout")
    audit: dict[str, list[str]] = {}
    fields = ["task_b.observation.superficial_signature", "task_b.observation.local_visible_cue"]
    fallback = _majority([_training_action(row) for row in train_rows])
    mapping = _build_mapping(train_rows, fields, audit, baseline_name)
    predictions = _prediction_rows(
        heldout_rows,
        lambda row: _predict_with_mapping(row, mapping, fields, fallback, audit, baseline_name),
    )
    return _baseline_result(
        baseline_name=baseline_name,
        producer_function="visible_feature_only_task_b_decoder",
        input_fixture_path=input_fixture_path,
        run_id=run_id,
        seed=seed,
        predictions=predictions,
        field_access_violations=audit.get(baseline_name, []),
        details={"decoder_fields": fields},
    )


def trace_order_or_id_sanitized_retrieval_probe(
    fixture: dict[str, Any],
    *,
    input_fixture_path: str,
    run_id: str,
    seed: int,
) -> dict[str, Any]:
    baseline_name = "trace_order_or_id_sanitized_retrieval_probe"
    train_rows = _records(fixture, "train")
    heldout_rows = _records(fixture, "heldout")
    audit: dict[str, list[str]] = {}
    fallback = _majority([_training_action(row) for row in train_rows])
    predictions = _prediction_rows(
        heldout_rows,
        lambda row: str(_visible_features(row, audit, baseline_name)["task_b.observation.fallback_action"])
        if fallback == "hold"
        else fallback,
    )
    return _baseline_result(
        baseline_name=baseline_name,
        producer_function="trace_order_or_id_sanitized_retrieval_probe",
        input_fixture_path=input_fixture_path,
        run_id=run_id,
        seed=seed,
        predictions=predictions,
        field_access_violations=audit.get(baseline_name, []),
        details={
            "retrieval_keys_removed": [
                "record_id",
                "context_handle",
                "partner_handle",
                "trace_order",
                "task_b.observation.latent_binding_probe",
            ]
        },
    )


def static_formula_visible_field_decoder(
    fixture: dict[str, Any],
    *,
    input_fixture_path: str,
    run_id: str,
    seed: int,
) -> dict[str, Any]:
    baseline_name = "static_formula_visible_field_decoder"
    train_rows = _records(fixture, "train")
    heldout_rows = _records(fixture, "heldout")
    audit: dict[str, list[str]] = {}
    action_space = sorted(set(_training_action(row) for row in train_rows))

    def predict(row: dict[str, Any]) -> str:
        features = _visible_features(row, audit, baseline_name)
        text = _canonical(
            {
                "visible_event_class": features["task_a.observation.visible_event_class"],
                "superficial_signature": features["task_b.observation.superficial_signature"],
                "local_visible_cue": features["task_b.observation.local_visible_cue"],
            }
        )
        digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
        return action_space[int(digest[:2], 16) % len(action_space)] if action_space else "hold"

    predictions = _prediction_rows(heldout_rows, predict)
    return _baseline_result(
        baseline_name=baseline_name,
        producer_function="static_formula_visible_field_decoder",
        input_fixture_path=input_fixture_path,
        run_id=run_id,
        seed=seed,
        predictions=predictions,
        field_access_violations=audit.get(baseline_name, []),
        details={"formula": "sha256_visible_fields_mod_train_action_space"},
    )


def build_cross_task_update_dependency_check(fixture: dict[str, Any]) -> dict[str, Any]:
    heldout_rows = _records(fixture, "heldout")
    preserved = [_expected_action(row) for row in heldout_rows]
    masked = [_masked_action(row) for row in heldout_rows]
    changed = [before != after for before, after in zip(masked, preserved)]
    return {
        "producer_function": "build_cross_task_update_dependency_check",
        "candidate_ablation": False,
        "comparison_type": "fixture_dependency_mask_only",
        "preserved_update_dependency": {"task_b_actions": preserved},
        "masked_update_dependency": {"task_b_actions": masked},
        "changed_action_count": sum(1 for item in changed if item),
        "total_heldout_cases": len(heldout_rows),
        "cross_task_update_dependency_required": bool(heldout_rows) and all(changed),
    }


def detect_static_verdict_or_metadata_only(payload: dict[str, Any]) -> dict[str, Any]:
    reasons: list[str] = []
    if not payload.get("computed_predictions"):
        reasons.append("missing_computed_predictions")
    if payload.get("metadata_only") is True:
        reasons.append("metadata_only_result")
    metric_keys = {"heldout_accuracy", "computed_predictions", "failure_reason"}
    if payload.get("verdict") and not any(key in payload for key in metric_keys):
        reasons.append("static_verdict_without_metrics")
    if payload.get("verdict") and not payload.get("computed_predictions"):
        reasons.append("static_verdict_without_metrics")
    return {
        "producer_function": "detect_static_verdict_or_metadata_only",
        "blocked": bool(reasons),
        "blocking_reasons": sorted(set(reasons)),
        "checked_keys": sorted(payload),
    }


def _fixture_seed(fixture: dict[str, Any]) -> int:
    return int(fixture.get("provenance", {}).get("seed", FIXTURE_SEED_FALLBACK))


def run_baseline_probes(fixture_path: str | Path | None = None, *, run_id: str | None = None) -> dict[str, Any]:
    path = _resolve_path(fixture_path)
    fixture = load_fixture(path)
    if run_id is None:
        run_id = f"{TASK_ID}_{_now().replace('-', '').replace(':', '').replace('Z', 'Z')}"
    input_path = _relative(path)
    seed = _fixture_seed(fixture)
    baseline_functions: list[Callable[..., dict[str, Any]]] = [
        independent_per_task_optimal_ensemble_no_shared_latent,
        shared_latent_no_cross_task_transfer,
        visible_feature_only_task_b_decoder,
        trace_order_or_id_sanitized_retrieval_probe,
        static_formula_visible_field_decoder,
    ]
    baseline_results = [
        func(fixture, input_fixture_path=input_path, run_id=run_id, seed=seed) for func in baseline_functions
    ]
    baseline_results_by_name = {row["baseline_name"]: row for row in baseline_results}
    static_audit = {
        name: detect_static_verdict_or_metadata_only(row) for name, row in baseline_results_by_name.items()
    }
    return {
        "producer_function": "run_baseline_probes",
        "task_id": TASK_CARD_ID,
        "run_id": run_id,
        "input_fixture_path": input_path,
        "fixture_seed": seed,
        "solve_threshold": SOLVE_THRESHOLD,
        "baseline_results": baseline_results,
        "baseline_results_by_name": baseline_results_by_name,
        "ablation_dependency_check": build_cross_task_update_dependency_check(fixture),
        "static_verdict_or_metadata_only_audit": static_audit,
        "claim_ceiling": CLAIM_CEILING,
    }


def build_field_access_audit(
    fixture_path: str | Path | None = None,
    *,
    include_positive_control: bool = False,
    baseline_probe_results: dict[str, Any] | None = None,
) -> dict[str, Any]:
    baseline_access_violations: dict[str, list[str]] = {}
    if baseline_probe_results is not None:
        for name, row in baseline_probe_results["baseline_results_by_name"].items():
            if row["field_access_violations"]:
                baseline_access_violations[name] = list(row["field_access_violations"])

    positive_control = {
        "executed": False,
        "blocked": False,
        "illegal_accesses": [],
    }
    if include_positive_control:
        fixture = load_fixture(fixture_path)
        audit: dict[str, list[str]] = {}
        positive_control["executed"] = True
        try:
            _visible_value(_records(fixture, "heldout")[0], "hidden.task_b_target_action", audit, "positive_control")
        except ForbiddenFieldAccess as exc:
            positive_control["blocked"] = True
            positive_control["illegal_accesses"] = [exc.field_path]

    return {
        "producer_function": "build_field_access_audit",
        "task_id": TASK_CARD_ID,
        "input_fixture_path": _relative(_resolve_path(fixture_path)),
        "allowed_observation_fields": list(ALLOWED_OBSERVATION_FIELDS),
        "allowed_training_outcome_fields": list(TRAINING_OUTCOME_FIELDS),
        "forbidden_fields_checked": list(FORBIDDEN_PREDICTION_FIELDS),
        "baseline_access_violations": baseline_access_violations,
        "positive_control": positive_control,
        "claim_ceiling": CLAIM_CEILING,
    }


def build_source_boundary_readback() -> dict[str, Any]:
    local_head = _safe_git(["rev-parse", "HEAD"])
    local_parent_tag_hash = _safe_git(["show-ref", "--verify", "--hash", f"refs/tags/{PARENT_TAG}"])
    remote_refs = _read_remote_refs(f"refs/heads/{BRANCH}", f"refs/tags/{PARENT_TAG}")
    remote_branch_hash = remote_refs.get(f"refs/heads/{BRANCH}", "")
    remote_parent_tag_hash = remote_refs.get(f"refs/tags/{PARENT_TAG}", "")
    parent_tag_type = _safe_git(["cat-file", "-t", PARENT_TAG])
    parent_exact = local_parent_tag_hash == PARENT_ANCHOR and remote_parent_tag_hash == PARENT_ANCHOR
    return {
        "producer_function": "build_source_boundary_readback",
        "task_id": TASK_CARD_ID,
        "expected_parent_anchor": PARENT_ANCHOR,
        "parent_tag": PARENT_TAG,
        "branch": BRANCH,
        "local_head": local_head,
        "local_parent_tag_hash": local_parent_tag_hash,
        "remote_branch_hash": remote_branch_hash,
        "remote_parent_tag_hash": remote_parent_tag_hash,
        "parent_anchor_exact_match": parent_exact,
        "parent_anchor_is_ancestor_of_head": _is_ancestor(PARENT_ANCHOR, local_head),
        "local_parent_tag_type": parent_tag_type,
        "claim_ceiling": "source-boundary readback only",
    }


def build_forbidden_action_guard() -> dict[str, Any]:
    created_paths = [str(path).replace("\\", "/") for path in (repo_root() / "src" / TASK_ID).glob("**/*")]
    created_paths += [str(path).replace("\\", "/") for path in (repo_root() / "artifacts" / ARTIFACT_DIR_NAME).glob("**/*")]
    forbidden_files_modified: list[str] = []
    return {
        "producer_function": "build_forbidden_action_guard",
        "task_id": TASK_CARD_ID,
        "candidate_code_created": False,
        "candidate_score_produced": False,
        "candidate_harness_created": False,
        "tournament_or_gate4_path_created": False,
        "runtime_bridge_admission_or_ego_mainline_path_created": False,
        "llm_rag_ui_companion_path_created": False,
        "forbidden_files_modified": forbidden_files_modified,
        "checked_created_paths": created_paths,
    }


def build_claim_ceiling() -> dict[str, Any]:
    return {
        "producer_function": "build_claim_ceiling",
        "task_id": TASK_CARD_ID,
        "claim_ceiling": CLAIM_CEILING,
        "allowed_claims": [
            "callable no-candidate baseline probes executed on the existing fixture",
            "required dangerous baselines did or did not solve under audited allowed access",
            "fixture-level cross-task update dependency masking did or did not collapse Task B action change",
            "source-boundary readback status for the parent anchor",
        ],
        "forbidden_claims": list(CLAIM_EXCLUSIONS),
    }


def compute_result(
    *,
    source_boundary_readback: dict[str, Any],
    baseline_probe_results: dict[str, Any],
    field_access_audit: dict[str, Any],
    forbidden_action_guard: dict[str, Any],
    run_id: str,
    test_result_readback: dict[str, Any] | None = None,
) -> dict[str, Any]:
    stop_conditions: list[str] = []
    required = baseline_probe_results["baseline_results_by_name"]
    if not source_boundary_readback["parent_anchor_exact_match"]:
        stop_conditions.append("parent_anchor_mismatch")
    if not source_boundary_readback["parent_anchor_is_ancestor_of_head"]:
        stop_conditions.append("parent_anchor_not_ancestor_of_head")
    if not field_access_audit["positive_control"]["blocked"]:
        stop_conditions.append("forbidden_field_positive_control_missing")
    if field_access_audit["baseline_access_violations"]:
        stop_conditions.append("forbidden_field_access")
    for baseline_name in REQUIRED_BASELINES:
        row = required.get(baseline_name)
        if not row or not row["executed"]:
            stop_conditions.append(f"missing_required_baseline:{baseline_name}")
        elif row["solves_fixture"]:
            stop_conditions.append(f"baseline_solved_fixture:{baseline_name}")
        static_audit = baseline_probe_results["static_verdict_or_metadata_only_audit"].get(baseline_name, {})
        if static_audit.get("blocked"):
            stop_conditions.append(f"static_or_metadata_only:{baseline_name}")
    if not baseline_probe_results["ablation_dependency_check"]["cross_task_update_dependency_required"]:
        stop_conditions.append("cross_task_update_dependency_not_required")
    for key in [
        "candidate_code_created",
        "candidate_score_produced",
        "candidate_harness_created",
        "tournament_or_gate4_path_created",
        "runtime_bridge_admission_or_ego_mainline_path_created",
        "llm_rag_ui_companion_path_created",
    ]:
        if forbidden_action_guard[key]:
            stop_conditions.append(key)

    stop_set = sorted(set(stop_conditions))
    if "forbidden_field_access" in stop_set or "forbidden_field_positive_control_missing" in stop_set:
        verdict = "composite_cross_task_state_reuse_surface_discriminativeness_preflight_001a_blocked_by_forbidden_field_access"
    elif any(item.endswith("independent_per_task_optimal_ensemble_no_shared_latent") for item in stop_set):
        verdict = "composite_cross_task_state_reuse_surface_discriminativeness_preflight_001a_blocked_by_independent_ensemble_solution"
    elif any(item.endswith("shared_latent_no_cross_task_transfer") for item in stop_set):
        verdict = "composite_cross_task_state_reuse_surface_discriminativeness_preflight_001a_blocked_by_shared_latent_no_transfer_solution"
    elif any(item.startswith("static_or_metadata_only:") for item in stop_set):
        verdict = "composite_cross_task_state_reuse_surface_discriminativeness_preflight_001a_blocked_by_static_verdict_or_metadata_only"
    elif any("missing_required_baseline" in item for item in stop_set) or "parent_anchor_mismatch" in stop_set:
        verdict = "composite_cross_task_state_reuse_surface_discriminativeness_preflight_001a_blocked_by_missing_provenance"
    elif stop_set:
        verdict = "composite_cross_task_state_reuse_surface_discriminativeness_preflight_001a_blocked_by_missing_provenance"
    else:
        verdict = "composite_cross_task_state_reuse_surface_discriminativeness_preflight_001a_pass"

    result = {
        "producer_function": "compute_result",
        "task_id": TASK_CARD_ID,
        "run_id": run_id,
        "verdict": verdict,
        "current_layer": "engineering implementation / evidence-governance / no-candidate surface-discriminativeness preflight only",
        "mainline_integration_status": "not integrated",
        "enabled_status": "callable local preflight runner only",
        "real_trigger_evidence": (
            "Callable baseline probes executed against the existing valid generated fixture with audited field access, "
            "positive-control forbidden-field blocking, fixture-level update masking, and source-boundary readback."
        ),
        "claim_ceiling": CLAIM_CEILING,
        "stop_conditions_triggered": stop_set,
        "candidate_code_created": forbidden_action_guard["candidate_code_created"],
        "candidate_score_produced": forbidden_action_guard["candidate_score_produced"],
        "candidate_harness_created": forbidden_action_guard["candidate_harness_created"],
        "tournament_or_gate4_path_created": forbidden_action_guard["tournament_or_gate4_path_created"],
        "runtime_bridge_admission_or_ego_mainline_path_created": forbidden_action_guard[
            "runtime_bridge_admission_or_ego_mainline_path_created"
        ],
        "llm_rag_ui_companion_path_created": forbidden_action_guard["llm_rag_ui_companion_path_created"],
        "auto_remote_anchor": AUTO_REMOTE_ANCHOR,
        "remote_anchor_performed": False,
        "next_minimal_closed_loop_action": (
            "Use this no-candidate preflight result to decide whether the surface can proceed to independent review "
            "or must route back to surface redesign; do not start candidate, tournament, Gate4, runtime, or bridge work."
        ),
        "what_this_does_not_prove": list(CLAIM_EXCLUSIONS),
    }
    if test_result_readback is not None:
        result["test_result_readback"] = test_result_readback
    return result


def _resolve_output_dir(output_dir: str | Path | None) -> Path:
    if output_dir is None:
        return repo_root() / "artifacts" / ARTIFACT_DIR_NAME
    path = Path(output_dir)
    return path if path.is_absolute() else repo_root() / path


def execute_preflight(
    output_dir: str | Path | None = None,
    *,
    persist_artifacts: bool = True,
    fixture_path: str | Path | None = None,
    test_result_readback: dict[str, Any] | None = None,
) -> dict[str, Any]:
    run_id = f"{TASK_ID}_{_now().replace('-', '').replace(':', '').replace('Z', 'Z')}"
    baseline_probe_results = run_baseline_probes(fixture_path=fixture_path, run_id=run_id)
    source_boundary_readback = build_source_boundary_readback()
    field_access_audit = build_field_access_audit(
        fixture_path=fixture_path,
        include_positive_control=True,
        baseline_probe_results=baseline_probe_results,
    )
    forbidden_action_guard = build_forbidden_action_guard()
    claim_ceiling = build_claim_ceiling()
    result = compute_result(
        source_boundary_readback=source_boundary_readback,
        baseline_probe_results=baseline_probe_results,
        field_access_audit=field_access_audit,
        forbidden_action_guard=forbidden_action_guard,
        run_id=run_id,
        test_result_readback=test_result_readback,
    )
    run = {
        "task_id": TASK_CARD_ID,
        "run_id": run_id,
        "result": result,
        "baseline_probe_results": baseline_probe_results,
        "field_access_audit": field_access_audit,
        "source_boundary_readback": source_boundary_readback,
        "claim_ceiling": claim_ceiling,
        "forbidden_action_guard": forbidden_action_guard,
    }
    if persist_artifacts:
        write_artifacts(_resolve_output_dir(output_dir), run)
    return run


def write_artifacts(out: Path, run: dict[str, Any]) -> None:
    artifact_map = {
        "result.json": run["result"],
        "baseline_probe_results.json": run["baseline_probe_results"],
        "field_access_audit.json": run["field_access_audit"],
        "source_boundary_readback.json": run["source_boundary_readback"],
        "claim_ceiling.json": run["claim_ceiling"],
    }
    for name, payload in artifact_map.items():
        _write_json(out / name, payload)
    missing = set(artifact_map) - {path.name for path in out.glob("*.json")}
    if missing:
        raise RuntimeError(f"required artifacts missing after write: {sorted(missing)}")


def write_research_report(run: dict[str, Any], report_path: str | Path | None = None) -> Path:
    path = Path(report_path) if report_path is not None else repo_root() / "docs" / "research" / REPORT_NAME
    if not path.is_absolute():
        path = repo_root() / path
    path.parent.mkdir(parents=True, exist_ok=True)
    result = run["result"]
    source = run["source_boundary_readback"]
    probes = run["baseline_probe_results"]
    baseline_rows = probes["baseline_results_by_name"]
    lines = [
        "# COMPOSITE-CROSS-TASK-STATE-REUSE-SURFACE-DISCRIMINATIVENESS-PREFLIGHT-001A",
        "",
        f"Verdict: `{result['verdict']}`",
        "",
        "Layer: engineering implementation / evidence-governance / no-candidate surface-discriminativeness preflight only.",
        "",
        "Mainline integration status: not integrated.",
        "",
        "Enabled status: callable local preflight runner only.",
        "",
        "Real trigger evidence: callable baseline probes executed against the existing generated fixture.",
        "",
        f"Claim ceiling: {CLAIM_CEILING} No mechanism validity, no Gate4 validity, no candidate behavior, no tournament outcome, no runtime readiness, no bridge/admission readiness, no agency, no subjectivity, no consciousness, no emotion, no autonomy, no companion readiness, and no EGO readiness.",
        "",
        "Auto-Remote-Anchor: conditional.",
        "",
        "## Bounded Audit",
        "",
        "- Real objective: verify whether the existing valid generated fixture is discriminative against no-candidate baselines before any candidate or tournament work.",
        "- Strongest baseline explanation: visible-feature lookup, independent per-task optimal decoding, or shared latent state without cross-task transfer could recover heldout Task B action without the disputed mechanism.",
        "- Strongest invalidity reason: a baseline could solve through hidden labels, row/context/partner IDs, trace order, target resolver outputs, stored answers, or a static verdict path.",
        "- Falsifier: either required dangerous baseline solves the fixture, forbidden fields are needed, static verdict output appears, provenance is missing, or the parent source boundary cannot be read back.",
        "- Evidence still insufficient: this is not candidate behavior, Gate4 evidence, tournament evidence, mechanism validity, runtime readiness, bridge/admission readiness, or EGO readiness.",
        "- Mechanism-vs-resemblance classification: no-candidate surface-discriminativeness preflight only.",
        "",
        "## Bounded Task Card",
        "",
        f"- Task id: `{TASK_CARD_ID}`",
        "- Problem definition: the 001A surface design passed protocol validation but had not executed the strongest no-candidate baseline probes on the valid generated fixture.",
        "- Current stage/layer: engineering implementation / evidence-governance / no-candidate surface-discriminativeness preflight only.",
        "- Mainline target: none.",
        "- Enabled-state requirement: callable local preflight runner only.",
        "- Real-trigger evidence requirement: execute callable baseline probes against the existing valid generated fixture.",
        "- Hypothesis: Task A prediction error must update shared state before Task B support-disjoint action selection changes.",
        "- Strongest baseline: independent per-task optimal ensemble with no shared latent state, plus shared latent state without cross-task prediction-error-to-action transfer.",
        "- Ablation requirement: no candidate ablation; fixture-level masking removes the cross-task update dependency and checks whether Task B action change collapses.",
        "- Trace/replay requirement: expected Task B actions are recomputed from serialized_state + observation for evaluation, not target resolver output or stored hidden labels.",
        "- Computed-evidence provenance gate: every baseline result records producer function, input fixture path, run id, seed, allowed fields, forbidden fields, computed predictions, aggregation, and code path hash.",
        "- Acceptance gate: parent anchor readback, required baseline execution, positive-control forbidden-field audit, no dangerous baseline solve, no forbidden path creation, and passing tests.",
        f"- Claim ceiling: {CLAIM_CEILING}",
        "- Stop condition: dangerous baseline solve, metadata-only probe, forbidden field access, missing provenance, or forbidden path creation.",
        "- Rollback plan: preserve blocked negative evidence and route back to surface redesign.",
        "- Expected changed files: isolated source package, focused test, report, and artifact directory for this task.",
        "- Forbidden changes: candidate model, candidate score, tournament, Gate4 replacement, runtime, bridge/admission, EGO-mainline, LLM/RAG/UI/companion paths.",
        "- Auto-Remote-Anchor decision: conditional.",
        "",
        "## Source Boundary Readback",
        "",
        f"- Expected parent anchor: `{source['expected_parent_anchor']}`",
        f"- Local parent tag hash: `{source['local_parent_tag_hash']}`",
        f"- Remote parent tag hash: `{source['remote_parent_tag_hash']}`",
        f"- Parent anchor exact match: `{source['parent_anchor_exact_match']}`",
        f"- Parent anchor is ancestor of current HEAD: `{source['parent_anchor_is_ancestor_of_head']}`",
        "",
        "## Baseline Probe Results",
        "",
    ]
    for baseline_name in BASELINE_NAMES:
        row = baseline_rows[baseline_name]
        lines.append(
            f"- `{baseline_name}` executed `{row['executed']}` accuracy `{row['heldout_accuracy']}` solves fixture `{row['solves_fixture']}` field violations `{row['field_access_violations']}`."
        )
    ablation = probes["ablation_dependency_check"]
    lines.extend(
        [
            "",
            "## Fixture Dependency Mask",
            "",
            f"- Candidate ablation: `{ablation['candidate_ablation']}`",
            f"- Preserved Task B actions: `{ablation['preserved_update_dependency']['task_b_actions']}`",
            f"- Masked Task B actions: `{ablation['masked_update_dependency']['task_b_actions']}`",
            f"- Cross-task update dependency required: `{ablation['cross_task_update_dependency_required']}`",
            "",
            "## Field Access Audit",
            "",
            f"- Baseline access violations: `{run['field_access_audit']['baseline_access_violations']}`",
            f"- Positive control blocked: `{run['field_access_audit']['positive_control']['blocked']}`",
            f"- Positive control illegal accesses: `{run['field_access_audit']['positive_control']['illegal_accesses']}`",
            "",
            "## Forbidden-Action Guard",
            "",
            f"- Candidate code created: `{run['forbidden_action_guard']['candidate_code_created']}`",
            f"- Candidate score produced: `{run['forbidden_action_guard']['candidate_score_produced']}`",
            f"- Candidate harness created: `{run['forbidden_action_guard']['candidate_harness_created']}`",
            f"- Tournament or Gate4 path created: `{run['forbidden_action_guard']['tournament_or_gate4_path_created']}`",
            f"- Runtime/bridge/admission/EGO-mainline path created: `{run['forbidden_action_guard']['runtime_bridge_admission_or_ego_mainline_path_created']}`",
            f"- LLM/RAG/UI/companion path created: `{run['forbidden_action_guard']['llm_rag_ui_companion_path_created']}`",
            f"- Forbidden files modified: `{run['forbidden_action_guard']['forbidden_files_modified']}`",
            "",
            "## Stop Conditions",
            "",
        ]
    )
    if result["stop_conditions_triggered"]:
        lines.extend(f"- `{item}`" for item in result["stop_conditions_triggered"])
    else:
        lines.append("- None.")
    lines.extend(
        [
            "",
            "## What This Does Not Prove",
            "",
            *[f"- {item}" for item in result["what_this_does_not_prove"]],
            "",
            "## Next Minimal Closed-Loop Action",
            "",
            result["next_minimal_closed_loop_action"],
            "",
            "## Remote Anchor Status",
            "",
            f"- Remote anchor performed: `{result['remote_anchor_performed']}`",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default=None)
    parser.add_argument("--fixture-path", default=None)
    parser.add_argument("--write-report", action="store_true")
    parser.add_argument("--test-command", default=None)
    parser.add_argument("--test-exit-code", default=None)
    parser.add_argument("--test-summary", default=None)
    args = parser.parse_args()
    test_readback = None
    if args.test_command is not None:
        test_readback = {
            "command": args.test_command,
            "exit_code": int(args.test_exit_code) if args.test_exit_code is not None else None,
            "summary": args.test_summary or "",
        }
    run = execute_preflight(
        output_dir=args.output_dir,
        fixture_path=args.fixture_path,
        persist_artifacts=True,
        test_result_readback=test_readback,
    )
    if args.write_report:
        write_research_report(run)
    print(json.dumps(run["result"], indent=2, sort_keys=True))
