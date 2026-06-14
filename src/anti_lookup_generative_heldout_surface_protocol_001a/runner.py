from __future__ import annotations

import argparse
import copy
import hashlib
import importlib
import inspect
import json
import subprocess
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from . import (
    ARTIFACT_DIR_NAME,
    AUTO_REMOTE_ANCHOR,
    BRANCH,
    CLAIM_CEILING,
    REPORT_NAME,
    REQUIRED_START_HEAD,
    RERUN_COMMIT,
    RERUN_TAG,
    ROUTING_TAG,
    TASK_CARD_ID,
    TASK_ID,
)


EXPECTED_FAMILY_IDS = [
    "causal_world_model_control",
    "jepa_like_latent_prediction",
    "replay_consolidation_adaptation",
    "self_boundary_controllability_model",
    "viability_value_gated_prediction_action_loop",
    "social_latent_inference_without_partner_id_lookup",
]
RERUN_DIR = Path("artifacts/mechanism_family_tournament_baseline_preflight_rerun_001b")
ROUTING_DIR = Path(
    "artifacts/mechanism_family_tournament_baseline_preflight_rerun_001b_post_result_routing_and_anchor_reconciliation_001a"
)
MODULE_PATH = str(Path("src") / TASK_ID / "runner.py").replace("\\", "/")
TARGET_RESOLVER_PATH = f"{TASK_ID}.runner.resolve_example_surface_target"
RUN_SEED = 41001
VALIDATOR_THRESHOLD = 0.8
REQUIRED_BASELINES = [
    "exact_lookup",
    "train_row_table_lookup",
    "nearest_neighbor_retrieval",
    "trace_order_lookup",
    "identity_key_lookup",
    "static_decoder",
    "static_formula",
]
REQUIRED_PROVENANCE_FIELDS = [
    "generator_function",
    "seed",
    "latent_parameter_ids",
    "train_ids",
    "heldout_ids",
    "counterfactual_pair_ids",
    "code_path_hash",
    "target_resolver_path",
]
EXPECTED_CONTROL_REASONS = {
    "invalid_exact_lookup_surface": "exact_lookup_reaches_threshold",
    "invalid_table_lookup_surface": "table_lookup_reaches_threshold",
    "invalid_identity_key_surface": "identity_key_lookup_reaches_threshold",
    "invalid_static_formula_surface": "static_formula_reaches_threshold",
    "invalid_target_leak_surface": "target_leak_detected",
    "invalid_missing_generator_provenance_surface": "missing_generator_provenance",
    "invalid_no_counterfactual_pairs_surface": "missing_counterfactual_pairs",
    "invalid_overlapping_support_surface": "overlapping_train_heldout_support",
    "invalid_hidden_baseline_access_surface": "baseline_access_not_equivalent",
}
CLAIM_EXCLUSIONS = [
    "mechanism validity",
    "Gate4 validity",
    "candidate behavior",
    "candidate score",
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
IDENTITY_KEY_TERMS = ("partner", "profile", "row_id", "episode_id", "context_id", "state_id", "stable_key")
TARGET_LEAK_KEY_TERMS = ("target", "answer", "label")


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


def _load_json(relative_path: Path | str) -> Any:
    return json.loads((repo_root() / relative_path).read_text(encoding="utf-8"))


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


def _safe_git_raw(args: list[str]) -> str:
    try:
        completed = subprocess.run(
            ["git", *args],
            cwd=repo_root(),
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
        return completed.stdout
    except (FileNotFoundError, subprocess.CalledProcessError):
        return ""


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


def _read_remote_refs(*refs: str) -> dict[str, str]:
    output = _safe_git(["ls-remote", "origin", *refs])
    rows: dict[str, str] = {}
    for line in output.splitlines():
        if not line.strip():
            continue
        commit, ref = line.split(maxsplit=1)
        rows[ref] = commit
    return rows


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def code_path_hash(func: Any) -> str:
    return hashlib.sha256(inspect.getsource(func).encode("utf-8")).hexdigest()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _resolve_function(dotted_path: str) -> Any:
    module_name, function_name = dotted_path.rsplit(".", 1)
    module = importlib.import_module(module_name)
    return getattr(module, function_name)


def resolve_example_surface_target(record: dict[str, Any]) -> str:
    return str(record["latent_variables"]["target_class"])


def _record(
    *,
    split: str,
    index: int,
    support_signature: str,
    partner_handle: str,
    latent_parameter_id: str,
    target_class: str,
    surface_form: str,
    intervention_handle: str,
) -> dict[str, Any]:
    record_id = f"{split}:{index}"
    return {
        "record_id": record_id,
        "support_signature": support_signature,
        "observation": {
            "surface_form": surface_form,
            "visible_trajectory": [f"{split}_visible_step_{index}", intervention_handle],
            "intervention_handle": intervention_handle,
            "partner_handle": partner_handle,
            "distractor_code": f"distractor_{split}_{index}",
        },
        "latent_variables": {
            "latent_parameter_id": latent_parameter_id,
            "target_class": target_class,
            "causal_rule_family": latent_parameter_id.split(":")[0],
        },
    }


def build_example_valid_surface_fixture() -> dict[str, Any]:
    train = [
        _record(
            split="train",
            index=0,
            support_signature="train_support_alpha",
            partner_handle="anon_train_a",
            latent_parameter_id="train_rule_family:param_a",
            target_class="adapt_left",
            surface_form="shared_surface_form",
            intervention_handle="train_intervention_0",
        ),
        _record(
            split="train",
            index=1,
            support_signature="train_support_beta",
            partner_handle="anon_train_b",
            latent_parameter_id="train_rule_family:param_b",
            target_class="adapt_right",
            surface_form="shared_surface_form",
            intervention_handle="train_intervention_1",
        ),
        _record(
            split="train",
            index=2,
            support_signature="train_support_gamma",
            partner_handle="anon_train_c",
            latent_parameter_id="train_rule_family:param_c",
            target_class="adapt_left",
            surface_form="surface_variant_c",
            intervention_handle="train_intervention_2",
        ),
        _record(
            split="train",
            index=3,
            support_signature="train_support_delta",
            partner_handle="anon_train_d",
            latent_parameter_id="train_rule_family:param_c",
            target_class="adapt_left",
            surface_form="surface_variant_d",
            intervention_handle="train_intervention_3",
        ),
    ]
    heldout = [
        _record(
            split="heldout",
            index=0,
            support_signature="heldout_support_eta",
            partner_handle="anon_heldout_q",
            latent_parameter_id="heldout_rule_family:param_q",
            target_class="adapt_right",
            surface_form="heldout_surface_q",
            intervention_handle="heldout_intervention_0",
        ),
        _record(
            split="heldout",
            index=1,
            support_signature="heldout_support_theta",
            partner_handle="anon_heldout_r",
            latent_parameter_id="heldout_rule_family:param_r",
            target_class="adapt_left",
            surface_form="heldout_surface_r",
            intervention_handle="heldout_intervention_1",
        ),
        _record(
            split="heldout",
            index=2,
            support_signature="heldout_support_iota",
            partner_handle="anon_heldout_s",
            latent_parameter_id="heldout_rule_family:param_s",
            target_class="adapt_right",
            surface_form="heldout_surface_s",
            intervention_handle="heldout_intervention_2",
        ),
        _record(
            split="heldout",
            index=3,
            support_signature="heldout_support_kappa",
            partner_handle="anon_heldout_t",
            latent_parameter_id="heldout_rule_family:param_t",
            target_class="adapt_right",
            surface_form="heldout_surface_t",
            intervention_handle="heldout_intervention_3",
        ),
    ]
    counterfactual_pairs = [
        {
            "pair_id": "cf_surface_same_latent_changes_target_train_0_1",
            "pair_type": "same_superficial_features_latent_structure_changes",
            "record_ids": ["train:0", "train:1"],
            "held_constant": ["observation.surface_form"],
            "changed": ["latent_variables.latent_parameter_id", "latent_variables.target_class"],
        },
        {
            "pair_id": "cf_latent_same_surface_changes_train_2_3",
            "pair_type": "superficial_features_change_latent_structure_stable",
            "record_ids": ["train:2", "train:3"],
            "held_constant": ["latent_variables.latent_parameter_id", "latent_variables.target_class"],
            "changed": ["observation.surface_form", "observation.intervention_handle"],
        },
    ]
    return {
        "surface_id": "example_valid_generative_heldout_surface",
        "surface_kind": "protocol_fixture_only",
        "threshold": VALIDATOR_THRESHOLD,
        "target_resolver_path": TARGET_RESOLVER_PATH,
        "split_policy": {
            "train_generator_id": "train_counterfactual_generator_v1",
            "heldout_generator_id": "heldout_counterfactual_generator_v2",
            "support_disjoint_required": True,
            "identity_permutation_required": True,
            "latent_parameter_ids": {
                "train": [row["latent_variables"]["latent_parameter_id"] for row in train],
                "heldout": [row["latent_variables"]["latent_parameter_id"] for row in heldout],
            },
        },
        "identity_permutation": {
            "across_splits": True,
            "anonymized_fields": ["partner_handle"],
            "train_identity_values": [row["observation"]["partner_handle"] for row in train],
            "heldout_identity_values": [row["observation"]["partner_handle"] for row in heldout],
        },
        "records": {"train": train, "heldout": heldout},
        "counterfactual_pairs": counterfactual_pairs,
        "baseline_access": {
            "same_observation_fields_as_candidate": True,
            "target_fields_visible_to_baselines": False,
        },
        "baseline_preregistration": list(REQUIRED_BASELINES),
        "provenance": {
            "generator_function": "build_example_valid_surface_fixture",
            "seed": RUN_SEED,
            "latent_parameter_ids": {
                "train": [row["latent_variables"]["latent_parameter_id"] for row in train],
                "heldout": [row["latent_variables"]["latent_parameter_id"] for row in heldout],
            },
            "train_ids": [row["record_id"] for row in train],
            "heldout_ids": [row["record_id"] for row in heldout],
            "counterfactual_pair_ids": [row["pair_id"] for row in counterfactual_pairs],
            "code_path_hash": code_path_hash(build_example_valid_surface_fixture),
            "target_resolver_path": TARGET_RESOLVER_PATH,
        },
        "claim_ceiling": CLAIM_CEILING,
    }


def _targets(records: list[dict[str, Any]], resolver_path: str) -> list[str]:
    resolver = _resolve_function(resolver_path)
    return [resolver(record) for record in records]


def _majority_target(train: list[dict[str, Any]], resolver_path: str) -> str:
    counts = Counter(_targets(train, resolver_path))
    return sorted(counts, key=lambda key: (-counts[key], key))[0]


def _accuracy(predictions: list[str], targets: list[str]) -> float:
    if not targets:
        return 0.0
    return sum(1 for prediction, target in zip(predictions, targets) if prediction == target) / len(targets)


def _score_mapping_baseline(
    surface: dict[str, Any],
    key_func,
    *,
    baseline_id: str,
    producer_function: str,
) -> dict[str, Any]:
    train = surface["records"].get("train", [])
    heldout = surface["records"].get("heldout", [])
    resolver_path = surface.get("target_resolver_path", TARGET_RESOLVER_PATH)
    threshold = float(surface.get("threshold", VALIDATOR_THRESHOLD))
    train_targets = _targets(train, resolver_path)
    heldout_targets = _targets(heldout, resolver_path)
    fallback = _majority_target(train, resolver_path) if train else ""
    mapping = {key_func(record, index): target for index, (record, target) in enumerate(zip(train, train_targets))}
    predictions = [mapping.get(key_func(record, index), fallback) for index, record in enumerate(heldout)]
    score = _accuracy(predictions, heldout_targets)
    return {
        "baseline_id": baseline_id,
        "producer_function": producer_function,
        "module_path": MODULE_PATH,
        "code_path_hash": code_path_hash(_score_mapping_baseline),
        "score": score,
        "threshold": threshold,
        "reaches_threshold": score >= threshold,
        "predictions": predictions,
        "targets": heldout_targets,
        "aggregation": "mean exact-match accuracy over heldout protocol fixture records",
        "input_record_ids": {
            "train": [row.get("record_id") for row in train],
            "heldout": [row.get("record_id") for row in heldout],
        },
    }


def _identity_values(record: dict[str, Any]) -> list[str]:
    values: list[str] = []

    def walk(value: Any, path: str = "") -> None:
        if isinstance(value, dict):
            for key, child in value.items():
                key_path = f"{path}.{key}" if path else str(key)
                if any(term in key.lower() for term in IDENTITY_KEY_TERMS):
                    values.append(_canonical(child))
                walk(child, key_path)
        elif isinstance(value, list):
            for index, child in enumerate(value):
                walk(child, f"{path}[{index}]")

    walk(record.get("observation", {}))
    return values


def _first_identity_key(record: dict[str, Any], index: int) -> str:
    values = _identity_values(record)
    return values[0] if values else f"no_identity:{index}"


def _static_formula_key(record: dict[str, Any], index: int) -> str:
    observation = record.get("observation", {})
    for key in ["static_formula_code", "formula_code", "static_decoder_key", "table_formula"]:
        if key in observation:
            return _canonical(observation[key])
    return f"no_formula:{index}"


def _table_key(record: dict[str, Any], index: int) -> str:
    observation = record.get("observation", {})
    if "table_key" in observation:
        return _canonical(observation["table_key"])
    return _canonical(record.get("support_signature", f"missing_support:{index}"))


def compute_baseline_scores(surface: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        "exact_lookup": _score_mapping_baseline(
            surface,
            lambda record, _index: _canonical(record.get("observation", {})),
            baseline_id="exact_lookup",
            producer_function="run_exact_lookup_baseline",
        ),
        "train_row_table_lookup": _score_mapping_baseline(
            surface,
            _table_key,
            baseline_id="train_row_table_lookup",
            producer_function="run_train_row_table_lookup_baseline",
        ),
        "nearest_neighbor_retrieval": _score_mapping_baseline(
            surface,
            lambda record, index: _table_key(record, index),
            baseline_id="nearest_neighbor_retrieval",
            producer_function="run_nearest_neighbor_retrieval_baseline",
        ),
        "trace_order_lookup": _score_mapping_baseline(
            surface,
            lambda _record, index: str(index),
            baseline_id="trace_order_lookup",
            producer_function="run_trace_order_lookup_baseline",
        ),
        "identity_key_lookup": _score_mapping_baseline(
            surface,
            _first_identity_key,
            baseline_id="identity_key_lookup",
            producer_function="run_identity_key_lookup_baseline",
        ),
        "static_decoder": _score_mapping_baseline(
            surface,
            _static_formula_key,
            baseline_id="static_decoder",
            producer_function="run_static_decoder_baseline",
        ),
        "static_formula": _score_mapping_baseline(
            surface,
            _static_formula_key,
            baseline_id="static_formula",
            producer_function="run_static_formula_baseline",
        ),
    }


def _visible_target_leaks(surface: dict[str, Any]) -> bool:
    resolver_path = surface.get("target_resolver_path", TARGET_RESOLVER_PATH)
    records = surface.get("records", {}).get("train", []) + surface.get("records", {}).get("heldout", [])
    for record in records:
        target = ""
        try:
            target = _resolve_function(resolver_path)(record)
        except Exception:
            pass

        def walk(value: Any, path: str = "") -> bool:
            if isinstance(value, dict):
                for key, child in value.items():
                    lowered = str(key).lower()
                    if any(term in lowered for term in TARGET_LEAK_KEY_TERMS):
                        return True
                    if walk(child, f"{path}.{key}" if path else str(key)):
                        return True
            elif isinstance(value, list):
                return any(walk(child, f"{path}[{index}]") for index, child in enumerate(value))
            elif target and str(value) == target and path.endswith(("formula_code", "static_formula_code")) is False:
                return True
            return False

        if walk(record.get("observation", {})):
            return True
    return False


def _support_sets(surface: dict[str, Any]) -> tuple[set[str], set[str]]:
    train = {
        str(row.get("support_signature", ""))
        for row in surface.get("records", {}).get("train", [])
        if row.get("support_signature")
    }
    heldout = {
        str(row.get("support_signature", ""))
        for row in surface.get("records", {}).get("heldout", [])
        if row.get("support_signature")
    }
    return train, heldout


def _counterfactual_requirements_met(surface: dict[str, Any]) -> bool:
    pair_types = {row.get("pair_type") for row in surface.get("counterfactual_pairs", [])}
    return {
        "same_superficial_features_latent_structure_changes",
        "superficial_features_change_latent_structure_stable",
    }.issubset(pair_types)


def _provenance_valid(surface: dict[str, Any]) -> bool:
    provenance = surface.get("provenance")
    if not isinstance(provenance, dict):
        return False
    return all(field in provenance and provenance[field] not in ("", [], {}) for field in REQUIRED_PROVENANCE_FIELDS)


def _generative_split_valid(surface: dict[str, Any]) -> bool:
    split_policy = surface.get("split_policy", {})
    train_generator = split_policy.get("train_generator_id")
    heldout_generator = split_policy.get("heldout_generator_id")
    latent = split_policy.get("latent_parameter_ids", {})
    train_params = set(latent.get("train", []))
    heldout_params = set(latent.get("heldout", []))
    return bool(train_generator and heldout_generator and train_generator != heldout_generator and train_params.isdisjoint(heldout_params))


def _identity_permutation_valid(surface: dict[str, Any]) -> bool:
    policy = surface.get("identity_permutation", {})
    train_values = set(map(str, policy.get("train_identity_values", [])))
    heldout_values = set(map(str, policy.get("heldout_identity_values", [])))
    return bool(policy.get("across_splits") is True and train_values.isdisjoint(heldout_values))


def _target_resolver_present(surface: dict[str, Any]) -> bool:
    try:
        return callable(_resolve_function(str(surface.get("target_resolver_path", ""))))
    except Exception:
        return False


def validate_surface_protocol(surface: dict[str, Any]) -> dict[str, Any]:
    blocking_reasons: list[str] = []
    train_support, heldout_support = _support_sets(surface)
    support_overlap = sorted(train_support & heldout_support)
    if support_overlap:
        blocking_reasons.append("overlapping_train_heldout_support")
    if not _generative_split_valid(surface):
        blocking_reasons.append("train_heldout_not_generatively_disjoint")
    if not _identity_permutation_valid(surface):
        blocking_reasons.append("identity_permutation_missing_or_overlapping")
    if not _provenance_valid(surface):
        blocking_reasons.append("missing_generator_provenance")
    if not _counterfactual_requirements_met(surface):
        blocking_reasons.append("missing_counterfactual_pairs")
    if not _target_resolver_present(surface):
        blocking_reasons.append("missing_callable_target_resolver")
    if surface.get("baseline_access", {}).get("same_observation_fields_as_candidate") is not True:
        blocking_reasons.append("baseline_access_not_equivalent")
    if _visible_target_leaks(surface):
        blocking_reasons.append("target_leak_detected")

    baseline_scores = compute_baseline_scores(surface)
    threshold_reasons = {
        "exact_lookup": "exact_lookup_reaches_threshold",
        "train_row_table_lookup": "table_lookup_reaches_threshold",
        "identity_key_lookup": "identity_key_lookup_reaches_threshold",
        "static_formula": "static_formula_reaches_threshold",
    }
    for baseline_id, reason in threshold_reasons.items():
        if baseline_scores[baseline_id]["reaches_threshold"]:
            blocking_reasons.append(reason)

    preregistered = set(surface.get("baseline_preregistration", []))
    if not set(REQUIRED_BASELINES).issubset(preregistered):
        blocking_reasons.append("missing_baseline_preregistration")

    unique_reasons = sorted(set(blocking_reasons))
    return {
        "producer_function": "validate_surface_protocol",
        "surface_id": surface.get("surface_id"),
        "valid": not unique_reasons,
        "blocking_reasons": unique_reasons,
        "expected_block_reason": surface.get("expected_block_reason"),
        "baseline_scores": baseline_scores,
        "support_disjoint_heldout_contexts": not support_overlap,
        "support_overlap": support_overlap,
        "counterfactual_pair_requirements_met": _counterfactual_requirements_met(surface),
        "callable_target_resolver_present": _target_resolver_present(surface),
        "targets_visible_in_observation": _visible_target_leaks(surface),
        "generator_provenance_present": _provenance_valid(surface),
        "identity_permutation_valid": _identity_permutation_valid(surface),
        "claim_ceiling": CLAIM_CEILING,
    }


def build_validator_positive_control_fixtures() -> dict[str, dict[str, Any]]:
    controls: dict[str, dict[str, Any]] = {}
    base = build_example_valid_surface_fixture()

    exact = copy.deepcopy(base)
    exact["surface_id"] = "invalid_exact_lookup_surface"
    for index, heldout in enumerate(exact["records"]["heldout"]):
        train = exact["records"]["train"][index]
        heldout["observation"] = copy.deepcopy(train["observation"])
        heldout["latent_variables"]["target_class"] = train["latent_variables"]["target_class"]
    controls[exact["surface_id"]] = exact

    table = copy.deepcopy(base)
    table["surface_id"] = "invalid_table_lookup_surface"
    for index, train in enumerate(table["records"]["train"]):
        table_key = f"lookup_bucket_{index}"
        train["observation"]["table_key"] = table_key
        heldout = table["records"]["heldout"][index]
        heldout["observation"]["table_key"] = table_key
        heldout["latent_variables"]["target_class"] = train["latent_variables"]["target_class"]
    controls[table["surface_id"]] = table

    identity = copy.deepcopy(base)
    identity["surface_id"] = "invalid_identity_key_surface"
    for index, train in enumerate(identity["records"]["train"]):
        heldout = identity["records"]["heldout"][index]
        heldout["observation"]["partner_handle"] = train["observation"]["partner_handle"]
        heldout["latent_variables"]["target_class"] = train["latent_variables"]["target_class"]
    identity["identity_permutation"]["heldout_identity_values"] = [
        row["observation"]["partner_handle"] for row in identity["records"]["heldout"]
    ]
    controls[identity["surface_id"]] = identity

    static = copy.deepcopy(base)
    static["surface_id"] = "invalid_static_formula_surface"
    for row in static["records"]["train"] + static["records"]["heldout"]:
        row["observation"]["static_formula_code"] = row["latent_variables"]["target_class"]
    controls[static["surface_id"]] = static

    leak = copy.deepcopy(base)
    leak["surface_id"] = "invalid_target_leak_surface"
    for row in leak["records"]["train"] + leak["records"]["heldout"]:
        row["observation"]["target_answer"] = row["latent_variables"]["target_class"]
    controls[leak["surface_id"]] = leak

    missing_provenance = copy.deepcopy(base)
    missing_provenance["surface_id"] = "invalid_missing_generator_provenance_surface"
    missing_provenance.pop("provenance", None)
    controls[missing_provenance["surface_id"]] = missing_provenance

    no_counterfactual = copy.deepcopy(base)
    no_counterfactual["surface_id"] = "invalid_no_counterfactual_pairs_surface"
    no_counterfactual["counterfactual_pairs"] = []
    controls[no_counterfactual["surface_id"]] = no_counterfactual

    overlap = copy.deepcopy(base)
    overlap["surface_id"] = "invalid_overlapping_support_surface"
    for index, train in enumerate(overlap["records"]["train"]):
        overlap["records"]["heldout"][index]["support_signature"] = train["support_signature"]
    controls[overlap["surface_id"]] = overlap

    hidden_access = copy.deepcopy(base)
    hidden_access["surface_id"] = "invalid_hidden_baseline_access_surface"
    hidden_access["baseline_access"]["same_observation_fields_as_candidate"] = False
    controls[hidden_access["surface_id"]] = hidden_access

    for surface_id, surface in controls.items():
        surface["expected_block_reason"] = EXPECTED_CONTROL_REASONS[surface_id]
    return controls


def run_validator_positive_controls(force_positive_control_pass: str | None = None) -> dict[str, Any]:
    controls = build_validator_positive_control_fixtures()
    rows = []
    for control_id, fixture in controls.items():
        validation = validate_surface_protocol(fixture)
        if force_positive_control_pass == control_id:
            validation = dict(validation)
            validation["blocking_reasons"] = []
            validation["valid"] = True
        expected = fixture["expected_block_reason"]
        failed_as_expected = expected in validation["blocking_reasons"]
        rows.append(
            {
                "control_id": control_id,
                "expected_block_reason": expected,
                "observed_block_reasons": validation["blocking_reasons"],
                "failed_as_expected": failed_as_expected,
                "validator_valid": validation["valid"],
                "baseline_scores": validation["baseline_scores"],
            }
        )
    return {
        "producer_function": "run_validator_positive_controls",
        "task_id": TASK_CARD_ID,
        "controls": rows,
        "all_failed_as_expected": all(row["failed_as_expected"] for row in rows),
        "claim_ceiling": CLAIM_CEILING,
    }


def build_inherited_negative_evidence_readback() -> dict[str, Any]:
    closed = _load_json(RERUN_DIR / "closed_families.json")
    survivors = _load_json(RERUN_DIR / "survivors.json")
    future = _load_json(RERUN_DIR / "future_tournament_eligibility.json")
    rerun_result = _load_json(RERUN_DIR / "result.json")
    route = _load_json(ROUTING_DIR / "route_decision.json")
    routing_result = _load_json(ROUTING_DIR / "result.json")
    anchor = _load_json(ROUTING_DIR / "anchor_status_readback.json")

    current_head = _safe_git(["rev-parse", "HEAD"])
    rerun_commit_hash = _safe_git(["rev-parse", RERUN_COMMIT])
    start_commit_hash = _safe_git(["rev-parse", REQUIRED_START_HEAD])
    rerun_tag_hash = _safe_git(["rev-parse", f"refs/tags/{RERUN_TAG}"])
    routing_tag_hash = _safe_git(["rev-parse", f"refs/tags/{ROUTING_TAG}"])
    remote_refs = _read_remote_refs(f"refs/tags/{RERUN_TAG}", f"refs/tags/{ROUTING_TAG}", f"refs/heads/{BRANCH}")

    closed_rows = []
    for row in closed.get("families", []):
        best = row.get("best_faithful_cheap_baseline", {})
        closed_rows.append(
            {
                "family_id": row.get("family_id"),
                "baseline_id": best.get("baseline_id"),
                "score": best.get("score"),
                "threshold": best.get("threshold"),
                "decision": row.get("decision"),
            }
        )

    current_surfaces_remain_closed = (
        len(closed_rows) == 6
        and set(row["family_id"] for row in closed_rows) == set(EXPECTED_FAMILY_IDS)
        and all(
            row["baseline_id"] == "exact_lookup"
            and row["score"] == 1.0
            and row["threshold"] == 0.8
            and row["decision"] == "closed_by_faithful_cheap_baseline"
            for row in closed_rows
        )
        and survivors.get("survivor_count") == 0
        and survivors.get("families") == []
        and future.get("eligible_for_future_tournament_execution_card") is False
    )
    route_verified = (
        route.get("current_six_surfaces_closed") is True
        and route.get("same_surface_repair_blocked") is True
        and route.get("candidate_implementation_authorized") is False
        and route.get("tournament_execution_authorized") is False
        and route.get("gate4_replacement_design_authorized") is False
        and routing_result.get("anchor_status_conflict_reconciled") is True
        and anchor.get("exact_match") is True
    )
    start_head_ok = current_head == REQUIRED_START_HEAD or _is_ancestor(REQUIRED_START_HEAD, current_head)
    return {
        "producer_function": "build_inherited_negative_evidence_readback",
        "task_id": TASK_CARD_ID,
        "branch": _safe_git(["branch", "--show-current"]),
        "expected_branch": BRANCH,
        "current_head": current_head,
        "required_start_head": REQUIRED_START_HEAD,
        "required_start_head_is_current_or_ancestor": start_head_ok,
        "baseline_preflight_rerun_boundary": {
            "commit": RERUN_COMMIT,
            "local_commit_hash": rerun_commit_hash,
            "tag": RERUN_TAG,
            "local_tag_hash": rerun_tag_hash,
            "remote_tag_hash": remote_refs.get(f"refs/tags/{RERUN_TAG}", ""),
            "result_verdict": rerun_result.get("verdict"),
            "closed_surface_count": len(closed_rows),
            "closed_surfaces": closed_rows,
            "survivor_count": survivors.get("survivor_count"),
            "future_tournament_eligibility": future.get("eligible_for_future_tournament_execution_card"),
            "current_surfaces_remain_closed": current_surfaces_remain_closed,
            "future_tournament_execution_authorized": future.get("tournament_execution_authorized"),
        },
        "post_result_routing_reconciliation_boundary": {
            "commit": REQUIRED_START_HEAD,
            "local_commit_hash": start_commit_hash,
            "tag": ROUTING_TAG,
            "local_tag_hash": routing_tag_hash,
            "remote_tag_hash": remote_refs.get(f"refs/tags/{ROUTING_TAG}", ""),
            "remote_branch_hash": remote_refs.get(f"refs/heads/{BRANCH}", ""),
            "anchor_conflict_reconciled": routing_result.get("anchor_status_conflict_reconciled"),
            "anchor_exact_match": anchor.get("exact_match"),
            "same_surface_repair_blocked": route.get("same_surface_repair_blocked"),
            "candidate_implementation_authorized": route.get("candidate_implementation_authorized"),
            "tournament_execution_authorized": route.get("tournament_execution_authorized"),
            "gate4_replacement_design_authorized": route.get("gate4_replacement_design_authorized"),
        },
        "inherited_boundaries_verified": (
            rerun_commit_hash == RERUN_COMMIT
            and start_commit_hash == REQUIRED_START_HEAD
            and current_surfaces_remain_closed
            and route_verified
            and start_head_ok
        ),
        "claim_ceiling": "inherited negative-evidence readback only",
    }


def build_protocol() -> dict[str, Any]:
    return {
        "producer_function": "build_protocol",
        "task_id": TASK_CARD_ID,
        "protocol_name": "anti_lookup_generative_heldout_surface_protocol_001a",
        "claim_ceiling": CLAIM_CEILING,
        "requirements": [
            "Training and heldout records must be generated from different latent parameterizations or counterfactual generators.",
            "Heldout contexts must be support-disjoint from training contexts.",
            "Identity-like fields must be permuted or anonymized across splits.",
            "Counterfactual pairs must hold superficial features constant while latent target structure changes and also change superficial features while target-relevant latent structure remains stable.",
            "Exact lookup, train-row table lookup, retrieval, trace-order lookup, identity-key lookup, static decoder, static formula, and family-specific shortcuts must run before candidate authorization.",
            "Leakage-positive controls must intentionally leak target fields, identity fields, answer keys, static formulas, row indices, and table mappings, and those controls must fail.",
            "Targets must resolve through callable generation state or latent causal variables and not through visible observation fields.",
            "Every generated split must serialize generator, seed, latent parameter IDs, split IDs, counterfactual pair IDs, code hash, and target resolver path.",
            "Cheap baselines must be preregistered before candidate code exists.",
            "Any faithful cheap baseline reaching threshold closes the surface without weakening the baseline or relabeling the surface as a survivor.",
        ],
        "auto_remote_anchor": AUTO_REMOTE_ANCHOR,
    }


def build_surface_requirements() -> dict[str, Any]:
    return {
        "producer_function": "build_surface_requirements",
        "task_id": TASK_CARD_ID,
        "required_split_properties": [
            "generative_train_test_split",
            "support_disjoint_heldout_contexts",
            "identity_and_key_permutation",
            "counterfactual_pair_generation",
            "callable_target_resolver",
            "serialized_provenance",
            "baseline_preregistration_before_candidate_code",
        ],
        "required_positive_controls": list(EXPECTED_CONTROL_REASONS),
        "candidate_code_authorized": False,
        "tournament_execution_authorized": False,
        "gate4_replacement_authorized": False,
        "claim_ceiling": CLAIM_CEILING,
    }


def build_forbidden_shortcut_taxonomy() -> dict[str, Any]:
    return {
        "producer_function": "build_forbidden_shortcut_taxonomy",
        "task_id": TASK_CARD_ID,
        "forbidden_shortcuts": {
            "exact_lookup": "Heldout observation exactly matches a train observation with the target.",
            "train_row_table_lookup": "Support, row, or table key maps train rows to heldout targets.",
            "nearest_neighbor_retrieval": "Retrieval over visible fields recovers the target without latent recomputation.",
            "trace_order_lookup": "Split order or sequence index predicts the target.",
            "identity_key_lookup": "Partner, profile, row, episode, context, state, or stable key handles predict the target.",
            "static_decoder": "A fixed visible decoder maps fields to targets.",
            "static_formula": "A visible formula or code path maps fields to targets.",
            "target_leak": "Visible observations contain target, answer, or label fields.",
            "hidden_baseline_access": "Candidate receives more information than the cheap baselines.",
        },
        "closure_rule": "If any faithful cheap baseline reaches threshold, the surface closes.",
        "claim_ceiling": CLAIM_CEILING,
    }


def build_baseline_preregistration_template() -> dict[str, Any]:
    return {
        "producer_function": "build_baseline_preregistration_template",
        "task_id": TASK_CARD_ID,
        "required_cheap_baselines": list(REQUIRED_BASELINES),
        "family_specific_shortcuts_required": True,
        "candidate_code_must_not_exist_before_preregistration": True,
        "baseline_access_must_match_candidate_observation_access": True,
        "closure_threshold_rule": "Use the predeclared numeric threshold; do not weaken a baseline after it closes the surface.",
        "claim_ceiling": CLAIM_CEILING,
    }


def build_future_surface_acceptance_gate() -> dict[str, Any]:
    return {
        "producer_function": "build_future_surface_acceptance_gate",
        "task_id": TASK_CARD_ID,
        "accept_only_if_inherited_negative_evidence_preserved": True,
        "accept_only_if_validator_accepts_valid_generative_heldout_fixture": True,
        "accept_only_if_positive_controls_fail": True,
        "close_surface_if_any_faithful_cheap_baseline_reaches_threshold": True,
        "do_not_weaken_baselines_after_result": True,
        "same_surface_repair_requires_separate_redesign_boundary": True,
        "candidate_authorization_requires_valid_protocol_pass": True,
        "tournament_execution_authorized_by_this_protocol": False,
        "gate4_replacement_authorized_by_this_protocol": False,
        "runtime_or_ego_mainline_authorized_by_this_protocol": False,
        "claim_ceiling": CLAIM_CEILING,
    }


def build_claim_ceiling() -> dict[str, Any]:
    return {
        "producer_function": "build_claim_ceiling",
        "task_id": TASK_CARD_ID,
        "claim_ceiling": CLAIM_CEILING,
        "allowed_claims": [
            "protocol shape",
            "validator behavior on example fixtures",
            "inherited negative-evidence preservation",
            "future surface acceptance criteria",
        ],
        "forbidden_claims": list(CLAIM_EXCLUSIONS),
    }


def _changed_or_new_paths() -> list[str]:
    changed: set[str] = set()
    for args in (["diff", "--name-only"], ["diff", "--cached", "--name-only"], ["ls-files", "--others", "--exclude-standard"]):
        for line in _safe_git_raw(args).splitlines():
            if line.strip():
                changed.add(line.strip().replace("\\", "/"))
    return sorted(changed)


def build_forbidden_action_guard() -> dict[str, Any]:
    allowed_prefixes = [
        f"src/{TASK_ID}/",
        f"artifacts/{TASK_ID}/",
    ]
    allowed_exact = {
        f"tests/test_{TASK_ID}.py",
        f"docs/research/{REPORT_NAME}",
    }
    paths = _changed_or_new_paths()
    forbidden_paths = [
        path for path in paths if path not in allowed_exact and not any(path.startswith(prefix) for prefix in allowed_prefixes)
    ]
    return {
        "producer_function": "build_forbidden_action_guard",
        "task_id": TASK_CARD_ID,
        "changed_or_new_paths": paths,
        "forbidden_files_modified": forbidden_paths,
        "candidate_code_created": False,
        "candidate_score_produced": False,
        "tournament_execution_attempted": False,
        "gate4_replacement_design_created": False,
        "gate4_repair_or_rerun_attempted": False,
        "runtime_or_mainline_path_created": False,
        "bridge_or_admission_path_created": False,
        "llm_rag_ui_companion_path_created": False,
        "claim_ceiling": CLAIM_CEILING,
    }


def compute_result(
    *,
    inherited: dict[str, Any],
    valid_validation: dict[str, Any],
    positive_controls: dict[str, Any],
    forbidden_guard: dict[str, Any],
    run_id: str,
) -> dict[str, Any]:
    stop_conditions = []
    if not inherited["inherited_boundaries_verified"]:
        stop_conditions.append("inherited_negative_evidence_readback_failure")
    if inherited["baseline_preflight_rerun_boundary"]["current_surfaces_remain_closed"] is not True:
        stop_conditions.append("current_surfaces_reopened")
    if inherited["post_result_routing_reconciliation_boundary"]["same_surface_repair_blocked"] is not True:
        stop_conditions.append("same_surface_repair_not_blocked")
    if not valid_validation["valid"]:
        stop_conditions.append("valid_fixture_not_discriminative")
    mismatched_controls = [
        row["control_id"]
        for row in positive_controls["controls"]
        if not row["failed_as_expected"]
    ]
    stop_conditions.extend(f"positive_control_mismatch:{control_id}" for control_id in mismatched_controls)
    if forbidden_guard["forbidden_files_modified"]:
        stop_conditions.append("forbidden_files_modified")
    for key in [
        "candidate_code_created",
        "candidate_score_produced",
        "tournament_execution_attempted",
        "gate4_replacement_design_created",
        "gate4_repair_or_rerun_attempted",
        "runtime_or_mainline_path_created",
        "bridge_or_admission_path_created",
        "llm_rag_ui_companion_path_created",
    ]:
        if forbidden_guard[key]:
            stop_conditions.append(key)

    if "inherited_negative_evidence_readback_failure" in stop_conditions:
        verdict = "anti_lookup_generative_heldout_surface_protocol_001a_blocked_by_inherited_evidence_readback_failure"
    elif any(condition.startswith("positive_control_mismatch:") for condition in stop_conditions):
        verdict = "anti_lookup_generative_heldout_surface_protocol_001a_blocked_by_positive_control_failure"
    elif "valid_fixture_not_discriminative" in stop_conditions:
        verdict = "anti_lookup_generative_heldout_surface_protocol_001a_blocked_by_valid_fixture_not_discriminative"
    elif any(
        condition
        in {
            "forbidden_files_modified",
            "candidate_code_created",
            "candidate_score_produced",
            "tournament_execution_attempted",
            "gate4_replacement_design_created",
            "gate4_repair_or_rerun_attempted",
            "runtime_or_mainline_path_created",
            "bridge_or_admission_path_created",
            "llm_rag_ui_companion_path_created",
        }
        for condition in stop_conditions
    ):
        verdict = "anti_lookup_generative_heldout_surface_protocol_001a_blocked_by_forbidden_action"
    else:
        verdict = "anti_lookup_generative_heldout_surface_protocol_001a_pass"
    return {
        "producer_function": "compute_result",
        "task_id": TASK_CARD_ID,
        "run_id": run_id,
        "verdict": verdict,
        "current_layer": "engineering-governance / anti-lookup generative heldout surface protocol design only",
        "mainline_integration_status": "not integrated",
        "enabled_status": "no runtime, no bridge/admission, no Gate4 replacement, no candidate, no tournament execution, no trigger path",
        "real_trigger_evidence": "Callable validator executed on one valid generative heldout fixture and lookup/leakage positive-control fixtures; inherited 001B closure artifacts were re-read from disk.",
        "claim_ceiling": CLAIM_CEILING,
        "stop_conditions_triggered": sorted(set(stop_conditions)),
        "six_current_surfaces_remain_closed": inherited["baseline_preflight_rerun_boundary"]["current_surfaces_remain_closed"],
        "same_surface_repair_blocked": inherited["post_result_routing_reconciliation_boundary"]["same_surface_repair_blocked"],
        "candidate_code_created": forbidden_guard["candidate_code_created"],
        "candidate_score_produced": forbidden_guard["candidate_score_produced"],
        "tournament_execution_attempted": forbidden_guard["tournament_execution_attempted"],
        "gate4_replacement_design_created": forbidden_guard["gate4_replacement_design_created"],
        "gate4_repair_or_rerun_attempted": forbidden_guard["gate4_repair_or_rerun_attempted"],
        "runtime_or_mainline_path_created": forbidden_guard["runtime_or_mainline_path_created"],
        "bridge_or_admission_path_created": forbidden_guard["bridge_or_admission_path_created"],
        "auto_remote_anchor": AUTO_REMOTE_ANCHOR,
        "remote_anchor_performed": False,
        "next_minimal_closed_loop_action": (
            "Use this protocol as the precondition for a separate future surface-redesign task; do not build "
            "candidate code or rerun a tournament until a generated surface passes this validator and cheap baseline preflight."
        ),
        "what_this_does_not_prove": list(CLAIM_EXCLUSIONS),
    }


def _resolve_output_dir(output_dir: str | Path | None) -> Path:
    if output_dir is None:
        return repo_root() / "artifacts" / ARTIFACT_DIR_NAME
    path = Path(output_dir)
    return path if path.is_absolute() else repo_root() / path


def execute_protocol(
    output_dir: str | Path | None = None,
    *,
    persist_artifacts: bool = True,
    force_positive_control_pass: str | None = None,
    test_result_readback: dict[str, Any] | None = None,
) -> dict[str, Any]:
    run_id = f"{TASK_ID}_{_now().replace('-', '').replace(':', '').replace('Z', 'Z')}"
    inherited = build_inherited_negative_evidence_readback()
    protocol = build_protocol()
    requirements = build_surface_requirements()
    shortcut_taxonomy = build_forbidden_shortcut_taxonomy()
    valid_fixture = build_example_valid_surface_fixture()
    invalid_lookup_fixture = build_validator_positive_control_fixtures()["invalid_exact_lookup_surface"]
    valid_validation = validate_surface_protocol(valid_fixture)
    positive_controls = run_validator_positive_controls(force_positive_control_pass=force_positive_control_pass)
    preregistration = build_baseline_preregistration_template()
    acceptance_gate = build_future_surface_acceptance_gate()
    claim_ceiling = build_claim_ceiling()
    forbidden_guard = build_forbidden_action_guard()
    result = compute_result(
        inherited=inherited,
        valid_validation=valid_validation,
        positive_controls=positive_controls,
        forbidden_guard=forbidden_guard,
        run_id=run_id,
    )
    if test_result_readback is not None:
        result["test_result_readback"] = test_result_readback
    run = {
        "task_id": TASK_CARD_ID,
        "run_id": run_id,
        "result": result,
        "protocol": protocol,
        "inherited_negative_evidence_readback": inherited,
        "surface_requirements": requirements,
        "forbidden_shortcut_taxonomy": shortcut_taxonomy,
        "validator_positive_controls": positive_controls,
        "example_valid_surface_fixture": valid_fixture,
        "example_invalid_lookup_surface_fixture": invalid_lookup_fixture,
        "baseline_preregistration_template": preregistration,
        "future_surface_acceptance_gate": acceptance_gate,
        "claim_ceiling": claim_ceiling,
        "valid_fixture_validation": valid_validation,
        "forbidden_action_guard": forbidden_guard,
    }
    if persist_artifacts:
        write_artifacts(_resolve_output_dir(output_dir), run)
    return run


def write_artifacts(out: Path, run: dict[str, Any]) -> None:
    artifact_map = {
        "result.json": run["result"],
        "protocol.json": run["protocol"],
        "inherited_negative_evidence_readback.json": run["inherited_negative_evidence_readback"],
        "surface_requirements.json": run["surface_requirements"],
        "forbidden_shortcut_taxonomy.json": run["forbidden_shortcut_taxonomy"],
        "validator_positive_controls.json": run["validator_positive_controls"],
        "example_valid_surface_fixture.json": run["example_valid_surface_fixture"],
        "example_invalid_lookup_surface_fixture.json": run["example_invalid_lookup_surface_fixture"],
        "baseline_preregistration_template.json": run["baseline_preregistration_template"],
        "future_surface_acceptance_gate.json": run["future_surface_acceptance_gate"],
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
    inherited = run["inherited_negative_evidence_readback"]
    controls = run["validator_positive_controls"]["controls"]
    lines = [
        "# ANTI-LOOKUP-GENERATIVE-HELDOUT-SURFACE-PROTOCOL-001A",
        "",
        f"Verdict: `{result['verdict']}`",
        "",
        "Layer: engineering-governance / anti-lookup generative heldout surface protocol design only.",
        "",
        "Mainline integration status: not integrated.",
        "",
        "Enabled status: no runtime, no bridge/admission, no Gate4 replacement, no candidate, no tournament execution, no trigger path.",
        "",
        f"Claim ceiling: {CLAIM_CEILING}",
        "",
        "Auto-Remote-Anchor: conditional.",
        "",
        "## Bounded Task Card",
        "",
        f"- Task id: `{TASK_CARD_ID}`",
        "- Problem definition: previous mechanism-family tournament surfaces were lookup-solvable; future surfaces need a generative heldout protocol before candidate or tournament authorization.",
        "- Current stage/layer: engineering-governance protocol design.",
        "- Mainline target: none; not integrated.",
        "- Enabled-state requirement: no runtime, bridge/admission, Gate4 replacement, candidate, tournament execution, or trigger path.",
        "- Real-trigger evidence requirement: callable validator must accept a valid generative heldout fixture and reject shortcut positive controls.",
        "- Hypothesis: requiring generative split, support disjointness, identity permutation, counterfactual pairs, callable targets, provenance, and preregistered cheap baselines blocks lookup-solvable surfaces before candidate authorization.",
        "- Strongest baseline: exact lookup, train-row table lookup, nearest-neighbor retrieval, trace-order lookup, identity-key lookup, static decoder, static formula, and family-specific shortcuts.",
        "- Ablation requirement: positive controls intentionally leak or expose each shortcut class and must fail.",
        "- Trace/replay requirement: validation records baseline predictions, targets, thresholds, score, producer function, module path, and code path hash.",
        "- Computed-evidence provenance gate: protocol fixtures record generator function, seed, latent parameter IDs, train/heldout IDs, counterfactual pair IDs, code hash, and target resolver path.",
        "- Acceptance gate: inherited 001B evidence preserved, all six current surfaces remain closed, same-surface repair remains blocked, valid fixture passes, positive controls fail, no forbidden path.",
        f"- Claim ceiling: {CLAIM_CEILING}",
        "- Stop condition: inherited evidence readback failure, positive-control failure, valid fixture not discriminative, reopened surface, or any candidate/tournament/Gate4/runtime path.",
        "- Rollback plan: remove only isolated 001A source, test, report, and artifact paths.",
        "- Expected changed files: isolated 001A source package, focused test, research report, and artifacts under `artifacts/anti_lookup_generative_heldout_surface_protocol_001a/`.",
        "- Forbidden changes: candidate model code, candidate scores, tournament execution, Gate4 replacement design, Gate4 repair/rerun, runtime, bridge/admission, EGO-mainline, LLM/RAG/UI/companion paths.",
        "- Auto-Remote-Anchor decision: conditional.",
        "",
        "## Inherited Negative Evidence",
        "",
        f"- 001B rerun commit: `{inherited['baseline_preflight_rerun_boundary']['commit']}`",
        f"- Closed surface count: `{inherited['baseline_preflight_rerun_boundary']['closed_surface_count']}`",
        f"- Survivor count: `{inherited['baseline_preflight_rerun_boundary']['survivor_count']}`",
        f"- Future tournament eligibility: `{inherited['baseline_preflight_rerun_boundary']['future_tournament_eligibility']}`",
        "- all six current surfaces remain closed by `exact_lookup = 1.0 >= 0.8`.",
        f"- 001B routing reconciliation commit: `{inherited['post_result_routing_reconciliation_boundary']['commit']}`",
        "- same-surface repair remains blocked.",
        "",
        "## Validator Positive Controls",
        "",
    ]
    for row in controls:
        lines.append(
            f"- `{row['control_id']}` expected `{row['expected_block_reason']}` observed `{row['observed_block_reasons']}` failed as expected `{row['failed_as_expected']}`."
        )
    lines.extend(
        [
            "",
            "## Future Acceptance Gate",
            "",
            "- Candidate authorization requires this protocol to pass and a later cheap-baseline preflight to remain below threshold.",
            "- If any faithful cheap baseline reaches threshold, the surface closes.",
            "- Baselines must not be weakened after result readback.",
            "- Same-surface repair requires a separate redesign boundary.",
            "",
            "## Forbidden-Action Guard",
            "",
            f"- Candidate code created: `{run['forbidden_action_guard']['candidate_code_created']}`",
            f"- Candidate score produced: `{run['forbidden_action_guard']['candidate_score_produced']}`",
            f"- Tournament execution attempted: `{run['forbidden_action_guard']['tournament_execution_attempted']}`",
            f"- Gate4 replacement design created: `{run['forbidden_action_guard']['gate4_replacement_design_created']}`",
            f"- Gate4 repair/rerun attempted: `{run['forbidden_action_guard']['gate4_repair_or_rerun_attempted']}`",
            f"- Runtime/mainline path created: `{run['forbidden_action_guard']['runtime_or_mainline_path_created']}`",
            f"- Bridge/admission path created: `{run['forbidden_action_guard']['bridge_or_admission_path_created']}`",
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
            "## Explicit Boundary Statement",
            "",
            "This protocol does not prove mechanism validity, Gate4 validity, candidate behavior, tournament outcome, runtime readiness, bridge/admission readiness, agency, subjectivity, consciousness, emotion, autonomy, companion readiness, or EGO readiness.",
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
    run = execute_protocol(
        output_dir=args.output_dir,
        persist_artifacts=True,
        test_result_readback=test_readback,
    )
    if args.write_report:
        write_research_report(run)
    print(json.dumps(run["result"], indent=2, sort_keys=True))
