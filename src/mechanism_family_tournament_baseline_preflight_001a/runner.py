from __future__ import annotations

import argparse
import hashlib
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
    CLAIM_CEILING,
    INHERITED_TASK_CARD_ID,
    REPORT_NAME,
    TASK_CARD_ID,
    TASK_ID,
)


BRANCH = "codex/meta-theory-scaffold"
EXPECTED_STARTING_HEAD = "0a59b39f30ec548d5f5513b6a27f4fd307df5381"
ENTRY_CRITERIA_REMOTE_ANCHOR = "remote-anchor-mechanism-family-tournament-entry-criteria-001a-0a59b39"
ENTRY_ARTIFACT_DIR = Path("artifacts/mechanism_family_tournament_entry_criteria_001a")
RUN_SEED = 1001

EXPECTED_FAMILY_IDS = [
    "causal_world_model_control",
    "jepa_like_latent_prediction",
    "replay_consolidation_adaptation",
    "self_boundary_controllability_model",
    "viability_value_gated_prediction_action_loop",
    "social_latent_inference_without_partner_id_lookup",
]

REQUIRED_ARTIFACTS = {
    "result.json",
    "source_pin_readback.json",
    "inherited_registry_readback.json",
    "baseline_score_matrix.json",
    "family_decisions.json",
    "survivors.json",
    "closed_families.json",
    "needs_redesign.json",
    "closed_family_inheritance.json",
    "positive_control_results.json",
    "provenance_manifest.json",
    "baseline_run_manifest.json",
    "surface_ablation_results.json",
    "forbidden_action_guard.json",
    "future_tournament_eligibility.json",
}

CLAIM_EXCLUSIONS = [
    "candidate code",
    "tournament execution",
    "Gate4 replacement",
    "runtime capability",
    "bridge/admission path",
    "EGO-mainline path",
    "mechanism-validity evidence",
    "consciousness evidence",
    "agency evidence",
    "subjectivity evidence",
    "companion readiness",
    "EGO readiness",
]

LEAKAGE_BASELINE_CLASSES = {
    "oracle_shortcut",
    "supervised_shortcut",
    "decoder",
    "hash_only_replay",
    "heuristic",
    "label_oracle",
    "full_bundle_decoder",
}

POSITIVE_CONTROL_EXPECTED_REASONS = {
    "target_leak_fixture": "target_leak_detected",
    "partner_id_lookup_fixture": "partner_id_lookup_shortcut_detected",
    "table_lookup_solvable_fixture": "faithful_table_lookup_reaches_threshold",
    "static_formula_solvable_fixture": "static_formula_shortcut_detected",
    "missing_threshold_fixture": "missing_threshold",
    "missing_callable_target_fixture": "missing_callable_target",
}

PROVENANCE_REQUIRED_FIELDS = [
    "family_id",
    "baseline_id",
    "baseline_category",
    "faithful_or_leakage_detector",
    "producer_function",
    "module_path",
    "code_path_hash",
    "inputs",
    "run_id",
    "seed",
    "context_ids",
    "episode_ids_or_registry_row_ids",
    "threshold",
    "raw_predictions",
    "targets",
    "score",
    "aggregation",
    "decision_contribution",
]


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def module_path() -> str:
    return str(Path("src") / TASK_ID / "runner.py").replace("\\", "/")


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


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


def _load_json(relative_path: str | Path) -> Any:
    return json.loads((repo_root() / relative_path).read_text(encoding="utf-8"))


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return _sha256_bytes(path.read_bytes())


def code_path_hash(func: Any) -> str:
    return hashlib.sha256(inspect.getsource(func).encode("utf-8")).hexdigest()


def _relative(path: Path) -> str:
    try:
        return str(path.relative_to(repo_root())).replace("\\", "/")
    except ValueError:
        return str(path).replace("\\", "/")


def _read_remote_refs(*refs: str) -> dict[str, str]:
    output = _safe_git(["ls-remote", "origin", *refs])
    rows: dict[str, str] = {}
    for line in output.splitlines():
        if not line.strip():
            continue
        commit, ref = line.split(maxsplit=1)
        rows[ref] = commit
    return rows


def build_source_pin_readback() -> dict[str, Any]:
    current_head = _safe_git(["rev-parse", "HEAD"])
    branch = _safe_git(["branch", "--show-current"])
    upstream = _safe_git(["rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}"])
    ahead_behind = _safe_git(["rev-list", "--left-right", "--count", "@{u}...HEAD"]).replace("\t", " ") if upstream else ""
    remote_refs = _read_remote_refs(
        f"refs/heads/{BRANCH}",
        f"refs/tags/{ENTRY_CRITERIA_REMOTE_ANCHOR}",
    )
    remote_branch_hash = remote_refs.get(f"refs/heads/{BRANCH}", "")
    remote_anchor_hash = remote_refs.get(f"refs/tags/{ENTRY_CRITERIA_REMOTE_ANCHOR}", "")
    local_expected = _safe_git(["rev-parse", EXPECTED_STARTING_HEAD])
    ancestor_check = subprocess.run(
        ["git", "merge-base", "--is-ancestor", EXPECTED_STARTING_HEAD, "HEAD"],
        cwd=repo_root(),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    ).returncode == 0
    source_paths = [
        ENTRY_ARTIFACT_DIR / "candidate_family_registry.json",
        ENTRY_ARTIFACT_DIR / "family_baseline_matrix.json",
        ENTRY_ARTIFACT_DIR / "family_ablation_matrix.json",
        ENTRY_ARTIFACT_DIR / "family_transfer_counterfactual_matrix.json",
        ENTRY_ARTIFACT_DIR / "closed_family_inheritance.json",
        ENTRY_ARTIFACT_DIR / "tournament_entry_validation_results.json",
        ENTRY_ARTIFACT_DIR / "source_pin_readback.json",
        Path("docs/research/MECHANISM-FAMILY-TOURNAMENT-ENTRY-CRITERIA-001A.md"),
    ]
    return {
        "producer_function": "build_source_pin_readback",
        "task_id": TASK_CARD_ID,
        "inherited_task_id": INHERITED_TASK_CARD_ID,
        "branch": branch,
        "expected_branch": BRANCH,
        "current_head": current_head,
        "expected_starting_head": EXPECTED_STARTING_HEAD,
        "local_expected_starting_head_hash": local_expected,
        "expected_starting_head_is_ancestor_of_current_head": ancestor_check,
        "entry_criteria_local_or_ancestor_verified": local_expected == EXPECTED_STARTING_HEAD and ancestor_check,
        "upstream": upstream,
        "upstream_ahead_behind_at_start": ahead_behind,
        "remote_branch_hash": remote_branch_hash,
        "entry_criteria_remote_anchor_tag": ENTRY_CRITERIA_REMOTE_ANCHOR,
        "entry_criteria_remote_anchor_hash": remote_anchor_hash,
        "entry_criteria_remote_anchor_verified": remote_anchor_hash == EXPECTED_STARTING_HEAD,
        "remote_branch_at_inherited_boundary_verified": remote_branch_hash == EXPECTED_STARTING_HEAD,
        "source_pin_integrity_passed": (
            branch == BRANCH
            and local_expected == EXPECTED_STARTING_HEAD
            and ancestor_check
            and remote_anchor_hash == EXPECTED_STARTING_HEAD
        ),
        "source_files": [
            {
                "path": str(path).replace("\\", "/"),
                "sha256": sha256_file(repo_root() / path),
            }
            for path in source_paths
        ],
        "claim_ceiling": "source-pin readback only; no mechanism validity or readiness claim",
    }


def build_inherited_registry_readback() -> dict[str, Any]:
    registry = _load_json(ENTRY_ARTIFACT_DIR / "candidate_family_registry.json")
    baseline_matrix = _load_json(ENTRY_ARTIFACT_DIR / "family_baseline_matrix.json")
    ablation_matrix = _load_json(ENTRY_ARTIFACT_DIR / "family_ablation_matrix.json")
    transfer_matrix = _load_json(ENTRY_ARTIFACT_DIR / "family_transfer_counterfactual_matrix.json")
    validation = _load_json(ENTRY_ARTIFACT_DIR / "tournament_entry_validation_results.json")
    source_paths = [
        ENTRY_ARTIFACT_DIR / "candidate_family_registry.json",
        ENTRY_ARTIFACT_DIR / "family_baseline_matrix.json",
        ENTRY_ARTIFACT_DIR / "family_ablation_matrix.json",
        ENTRY_ARTIFACT_DIR / "family_transfer_counterfactual_matrix.json",
        ENTRY_ARTIFACT_DIR / "tournament_entry_validation_results.json",
    ]
    family_ids = [family["family_id"] for family in registry.get("families", [])]
    missing_required = sorted(set(EXPECTED_FAMILY_IDS) - set(family_ids))
    threshold_fields = {
        family["family_id"]: {
            key: value
            for key, value in family.items()
            if "threshold" in key.lower() or "score" in key.lower() or "metric" in key.lower()
        }
        for family in registry.get("families", [])
    }
    callable_target_fields = {
        family["family_id"]: {
            key: value
            for key, value in family.items()
            if "callable" in key.lower() or "target_dataset" in key.lower() or "target_path" in key.lower()
        }
        for family in registry.get("families", [])
    }
    return {
        "producer_function": "build_inherited_registry_readback",
        "task_id": TASK_CARD_ID,
        "inherited_task_id": registry.get("task_id"),
        "family_ids": family_ids,
        "family_count": len(family_ids),
        "expected_family_ids": list(EXPECTED_FAMILY_IDS),
        "missing_required_family_ids": missing_required,
        "baseline_row_count": len(baseline_matrix),
        "ablation_row_count": len(ablation_matrix),
        "transfer_counterfactual_row_count": len(transfer_matrix),
        "inherited_validator_final_verdict": validation.get("final_verdict"),
        "malformed_positive_control_failed_as_expected": validation.get("invalid_fixture_failed_as_expected"),
        "candidate_code_authorized": registry.get("candidate_code_authorized"),
        "gate4_replacement_design_authorized": registry.get("gate4_replacement_design_authorized"),
        "threshold_fields_by_family": threshold_fields,
        "callable_target_fields_by_family": callable_target_fields,
        "artifact_hashes": [
            {
                "path": str(path).replace("\\", "/"),
                "sha256": sha256_file(repo_root() / path),
            }
            for path in source_paths
        ],
        "raw_registry": registry,
        "raw_baseline_matrix": baseline_matrix,
        "raw_ablation_matrix": ablation_matrix,
        "raw_transfer_counterfactual_matrix": transfer_matrix,
        "raw_validation_results": validation,
    }


def load_closed_family_inheritance() -> dict[str, Any]:
    payload = _load_json(ENTRY_ARTIFACT_DIR / "closed_family_inheritance.json")
    payload = json.loads(json.dumps(payload))
    payload["producer_function"] = "load_closed_family_inheritance"
    payload["source_path"] = str(ENTRY_ARTIFACT_DIR / "closed_family_inheritance.json").replace("\\", "/")
    payload["source_sha256"] = sha256_file(repo_root() / ENTRY_ARTIFACT_DIR / "closed_family_inheritance.json")
    return payload


def _baseline_kind(row: dict[str, Any]) -> str:
    if row.get("threshold_role") in {"block_if_detected", "diagnostic_only"}:
        return "leakage_detector"
    if row.get("baseline_class") in LEAKAGE_BASELINE_CLASSES:
        return "leakage_detector"
    return "faithful_cheap_baseline"


def run_declared_baseline_preflight_row(
    *,
    family: dict[str, Any],
    baseline_row: dict[str, Any],
    row_id: str,
    run_id: str,
) -> dict[str, Any]:
    threshold = family.get("threshold") or family.get("task_threshold")
    callable_target = family.get("callable_target") or family.get("target_dataset_path")
    reasons = []
    if threshold is None:
        reasons.append("missing_threshold")
    if not callable_target:
        reasons.append("missing_callable_target")
    return {
        "family_id": family["family_id"],
        "baseline_id": baseline_row["baseline_id"],
        "baseline_category": baseline_row["baseline_class"],
        "faithful_or_leakage_detector": _baseline_kind(baseline_row),
        "producer_function": "run_declared_baseline_preflight_row",
        "module_path": module_path(),
        "code_path_hash": code_path_hash(run_declared_baseline_preflight_row),
        "inputs": {
            "registry_path": str(ENTRY_ARTIFACT_DIR / "candidate_family_registry.json").replace("\\", "/"),
            "baseline_matrix_path": str(ENTRY_ARTIFACT_DIR / "family_baseline_matrix.json").replace("\\", "/"),
            "family_id": family["family_id"],
            "baseline_row_id": row_id,
        },
        "run_id": run_id,
        "seed": RUN_SEED,
        "context_ids": [family["family_id"]],
        "episode_ids_or_registry_row_ids": [row_id],
        "threshold": threshold,
        "raw_predictions": [],
        "targets": [],
        "score": None,
        "aggregation": "not_scored_missing_callable_target_or_threshold",
        "decision_contribution": "needs_redesign_missing_threshold_or_callable_target",
        "callable_invoked": True,
        "attempted": True,
        "block_reasons": reasons,
        "why_no_score": "Inherited family registry supplies criteria text and baseline rows, but no numeric threshold or callable target surface.",
    }


def build_baseline_score_matrix(registry_readback: dict[str, Any], run_id: str) -> dict[str, Any]:
    families = {
        family["family_id"]: family
        for family in registry_readback["raw_registry"].get("families", [])
    }
    rows = []
    for index, baseline_row in enumerate(registry_readback["raw_baseline_matrix"]):
        family = families[baseline_row["family_id"]]
        row_id = f"baseline_row_{index:03d}:{baseline_row['family_id']}:{baseline_row['baseline_id']}"
        rows.append(
            run_declared_baseline_preflight_row(
                family=family,
                baseline_row=baseline_row,
                row_id=row_id,
                run_id=run_id,
            )
        )
    return {
        "producer_function": "build_baseline_score_matrix",
        "task_id": TASK_CARD_ID,
        "run_id": run_id,
        "row_count": len(rows),
        "rows": rows,
        "claim_ceiling": "declared cheap-baseline preflight over inherited registry rows only; no candidate score",
    }


def build_family_decisions(
    registry_readback: dict[str, Any],
    baseline_score_matrix: dict[str, Any],
) -> dict[str, Any]:
    rows_by_family: dict[str, list[dict[str, Any]]] = {}
    for row in baseline_score_matrix["rows"]:
        rows_by_family.setdefault(row["family_id"], []).append(row)
    decisions = []
    for family_id in registry_readback["family_ids"]:
        family_rows = rows_by_family.get(family_id, [])
        reasons = sorted({reason for row in family_rows for reason in row["block_reasons"]})
        best_faithful = next(
            (
                row
                for row in family_rows
                if row["faithful_or_leakage_detector"] == "faithful_cheap_baseline"
            ),
            family_rows[0] if family_rows else None,
        )
        if reasons:
            decision = "needs_redesign"
            reason_text = "no numeric threshold and no callable target surface were present in the inherited artifacts"
        else:
            decision = "survives_baseline_preflight_only"
            reason_text = "all faithful cheap baselines below threshold and leakage checks clean"
        decisions.append(
            {
                "family_id": family_id,
                "decision": decision,
                "reasons": reasons,
                "reason": reason_text,
                "threshold": None,
                "best_faithful_cheap_baseline": {
                    "baseline_id": best_faithful["baseline_id"] if best_faithful else None,
                    "score": best_faithful["score"] if best_faithful else None,
                    "threshold": best_faithful["threshold"] if best_faithful else None,
                },
                "same_family_repair_blocked": decision == "closed_by_faithful_cheap_baseline",
                "candidate_code_authorized": False,
                "tournament_execution_authorized": False,
            }
        )
    return {
        "producer_function": "build_family_decisions",
        "task_id": TASK_CARD_ID,
        "decisions": decisions,
    }


def _target_counts(records: list[dict[str, Any]]) -> Counter[str]:
    return Counter(row["target"] for row in records)


def _majority(records: list[dict[str, Any]]) -> str:
    counts = _target_counts(records)
    if not counts:
        return ""
    return sorted(counts.items(), key=lambda item: (-item[1], item[0]))[0][0]


def _compute_field_lookup(serialized_input: dict[str, Any]) -> dict[str, Any]:
    field = serialized_input["shortcut_field"]
    train = serialized_input["train"]
    heldout = serialized_input["heldout"]
    table: dict[str, Counter[str]] = {}
    for row in train:
        key = str(row["observation"].get(field, ""))
        table.setdefault(key, Counter())[row["target"]] += 1
    fallback = _majority(train)
    mapping = {
        key: sorted(counts.items(), key=lambda item: (-item[1], item[0]))[0][0]
        for key, counts in table.items()
    }
    raw_predictions = {
        row["episode_id"]: mapping.get(str(row["observation"].get(field, "")), fallback)
        for row in heldout
    }
    targets = {row["episode_id"]: row["target"] for row in heldout}
    score = sum(1 for episode_id, target in targets.items() if raw_predictions.get(episode_id) == target) / len(targets)
    return {
        "raw_predictions": raw_predictions,
        "targets": targets,
        "score": score,
        "aggregation": "mean exact-match accuracy over heldout positive-control rows",
    }


def _compute_static_formula(serialized_input: dict[str, Any]) -> dict[str, Any]:
    feature = serialized_input["shortcut_field"]
    threshold = serialized_input.get("formula_threshold", 0.5)
    heldout = serialized_input["heldout"]
    fallback = _majority(serialized_input["train"])
    raw_predictions = {}
    for row in heldout:
        value = row["observation"].get(feature)
        if isinstance(value, (int, float)):
            raw_predictions[row["episode_id"]] = "high" if value >= threshold else "low"
        else:
            raw_predictions[row["episode_id"]] = fallback
    targets = {row["episode_id"]: row["target"] for row in heldout}
    score = sum(1 for episode_id, target in targets.items() if raw_predictions.get(episode_id) == target) / len(targets)
    return {
        "raw_predictions": raw_predictions,
        "targets": targets,
        "score": score,
        "aggregation": "mean exact-match accuracy over heldout positive-control rows",
    }


def recompute_baseline_score(serialized_input: dict[str, Any]) -> dict[str, Any]:
    kind = serialized_input["baseline_kind"]
    if kind in {"field_lookup", "table_lookup"}:
        return _compute_field_lookup(serialized_input)
    if kind == "static_formula":
        return _compute_static_formula(serialized_input)
    raise ValueError(f"unsupported serialized baseline kind: {kind}")


def _positive_control_rows() -> dict[str, dict[str, Any]]:
    actions = ["support", "challenge", "defer", "summarize"]
    partner_rows = [
        {
            "episode_id": f"partner_{idx}",
            "target": action,
            "observation": {"partner_id": f"partner_{idx}", "context_id": f"context_{idx}", "risk": idx / 3},
        }
        for idx, action in enumerate(actions)
    ]
    table_rows = [
        {
            "episode_id": f"table_{idx}",
            "target": action,
            "observation": {"context_id": f"context_{idx}", "visible_token": f"token_{idx % 2}"},
        }
        for idx, action in enumerate(actions)
    ]
    formula_rows = [
        {"episode_id": "formula_low_0", "target": "low", "observation": {"risk": 0.1}},
        {"episode_id": "formula_low_1", "target": "low", "observation": {"risk": 0.3}},
        {"episode_id": "formula_high_0", "target": "high", "observation": {"risk": 0.7}},
        {"episode_id": "formula_high_1", "target": "high", "observation": {"risk": 0.9}},
    ]
    return {
        "target_leak_fixture": {
            "control_id": "target_leak_fixture",
            "baseline_id": "target_leak_detector",
            "baseline_category": "leakage_scan",
            "faithful_or_leakage_detector": "leakage_detector",
            "threshold": 0.8,
            "callable_target": True,
            "serialized_input": {
                "baseline_kind": "target_leak",
                "shortcut_field": "target_action",
                "train": [],
                "heldout": [
                    {
                        "episode_id": "leak_0",
                        "target": "support",
                        "observation": {"target_action": "support"},
                    }
                ],
            },
        },
        "partner_id_lookup_fixture": {
            "control_id": "partner_id_lookup_fixture",
            "baseline_id": "partner_id_lookup",
            "baseline_category": "identity_lookup",
            "faithful_or_leakage_detector": "faithful_cheap_baseline",
            "threshold": 0.8,
            "callable_target": True,
            "serialized_input": {
                "baseline_kind": "field_lookup",
                "shortcut_field": "partner_id",
                "train": partner_rows,
                "heldout": partner_rows,
            },
        },
        "table_lookup_solvable_fixture": {
            "control_id": "table_lookup_solvable_fixture",
            "baseline_id": "table_lookup",
            "baseline_category": "lookup_table",
            "faithful_or_leakage_detector": "faithful_cheap_baseline",
            "threshold": 0.8,
            "callable_target": True,
            "serialized_input": {
                "baseline_kind": "table_lookup",
                "shortcut_field": "context_id",
                "train": table_rows,
                "heldout": table_rows,
            },
        },
        "static_formula_solvable_fixture": {
            "control_id": "static_formula_solvable_fixture",
            "baseline_id": "static_formula",
            "baseline_category": "static_formula",
            "faithful_or_leakage_detector": "leakage_detector",
            "threshold": 0.8,
            "callable_target": True,
            "serialized_input": {
                "baseline_kind": "static_formula",
                "shortcut_field": "risk",
                "formula_threshold": 0.5,
                "train": formula_rows,
                "heldout": formula_rows,
            },
        },
        "missing_threshold_fixture": {
            "control_id": "missing_threshold_fixture",
            "baseline_id": "missing_threshold_control",
            "baseline_category": "provenance_gate",
            "faithful_or_leakage_detector": "faithful_cheap_baseline",
            "threshold": None,
            "callable_target": True,
            "serialized_input": {
                "baseline_kind": "field_lookup",
                "shortcut_field": "context_id",
                "train": table_rows,
                "heldout": table_rows,
            },
        },
        "missing_callable_target_fixture": {
            "control_id": "missing_callable_target_fixture",
            "baseline_id": "missing_callable_target_control",
            "baseline_category": "provenance_gate",
            "faithful_or_leakage_detector": "faithful_cheap_baseline",
            "threshold": 0.8,
            "callable_target": False,
            "serialized_input": {
                "baseline_kind": "field_lookup",
                "shortcut_field": "context_id",
                "train": [],
                "heldout": [],
            },
        },
    }


def _score_record_for_control(control: dict[str, Any], run_id: str, output_dir: Path) -> dict[str, Any] | None:
    if not control.get("callable_target") or control.get("threshold") is None:
        return None
    if control["serialized_input"]["baseline_kind"] == "target_leak":
        return None
    recomputed = recompute_baseline_score(control["serialized_input"])
    return {
        "family_id": control["control_id"],
        "baseline_id": control["baseline_id"],
        "baseline_category": control["baseline_category"],
        "faithful_or_leakage_detector": control["faithful_or_leakage_detector"],
        "producer_function": "recompute_baseline_score",
        "module_path": module_path(),
        "code_path_hash": code_path_hash(recompute_baseline_score),
        "inputs": {
            "positive_control_input_fixture_path": str(output_dir / "positive_controls" / f"{control['control_id']}.json").replace("\\", "/"),
        },
        "run_id": run_id,
        "seed": RUN_SEED,
        "context_ids": [control["control_id"]],
        "episode_ids_or_registry_row_ids": [row["episode_id"] for row in control["serialized_input"]["heldout"]],
        "threshold": control["threshold"],
        "raw_predictions": recomputed["raw_predictions"],
        "targets": recomputed["targets"],
        "score": recomputed["score"],
        "aggregation": recomputed["aggregation"],
        "decision_contribution": "positive_control_failure_expected",
        "serialized_input": control["serialized_input"],
    }


def evaluate_positive_control(
    control: dict[str, Any],
    *,
    run_id: str,
    output_dir: Path,
) -> dict[str, Any]:
    if control["control_id"] == "target_leak_fixture":
        observed = "target_leak_detected"
    elif control.get("threshold") is None:
        observed = "missing_threshold"
    elif not control.get("callable_target"):
        observed = "missing_callable_target"
    else:
        score_record = _score_record_for_control(control, run_id, output_dir)
        score = score_record["score"] if score_record else None
        if control["control_id"] == "partner_id_lookup_fixture" and score is not None and score >= control["threshold"]:
            observed = "partner_id_lookup_shortcut_detected"
        elif control["control_id"] == "table_lookup_solvable_fixture" and score is not None and score >= control["threshold"]:
            observed = "faithful_table_lookup_reaches_threshold"
        elif control["control_id"] == "static_formula_solvable_fixture" and score is not None and score >= control["threshold"]:
            observed = "static_formula_shortcut_detected"
        else:
            observed = "positive_control_not_blocked"
    score_record = _score_record_for_control(control, run_id, output_dir)
    expected = POSITIVE_CONTROL_EXPECTED_REASONS[control["control_id"]]
    return {
        "control_id": control["control_id"],
        "positive_control_input_fixture_path": str(output_dir / "positive_controls" / f"{control['control_id']}.json").replace("\\", "/"),
        "expected_block_reason": expected,
        "observed_block_reason": observed,
        "matched": observed == expected,
        "baseline_id": control["baseline_id"],
        "faithful_or_leakage_detector": control["faithful_or_leakage_detector"],
        "score_record": score_record,
    }


def run_positive_controls(
    *,
    run_id: str,
    output_dir: Path,
    force_positive_control_mismatch: str | None = None,
) -> dict[str, Any]:
    controls = []
    fixtures = _positive_control_rows()
    for control_id, control in fixtures.items():
        result = evaluate_positive_control(control, run_id=run_id, output_dir=output_dir)
        if force_positive_control_mismatch == control_id:
            result["observed_block_reason"] = "positive_control_not_blocked"
            result["matched"] = False
        controls.append(result)
    return {
        "producer_function": "run_positive_controls",
        "task_id": TASK_CARD_ID,
        "run_id": run_id,
        "all_matched": all(row["matched"] for row in controls),
        "controls": controls,
        "fixture_payloads": fixtures,
    }


def _mask_shortcut(serialized_input: dict[str, Any]) -> dict[str, Any]:
    masked = json.loads(json.dumps(serialized_input))
    field = masked["shortcut_field"]
    for split in ("train", "heldout"):
        for row in masked.get(split, []):
            if field in row.get("observation", {}):
                row["observation"][field] = "__MASKED__"
    return masked


def build_surface_ablation_results(positive_controls: dict[str, Any]) -> dict[str, Any]:
    ablations = []
    for row in positive_controls["controls"]:
        score_record = row.get("score_record")
        if not score_record:
            continue
        serialized = score_record["serialized_input"]
        masked = _mask_shortcut(serialized)
        masked_result = recompute_baseline_score(masked)
        ablations.append(
            {
                "control_id": row["control_id"],
                "baseline_id": row["baseline_id"],
                "shortcut_fields": [serialized["shortcut_field"]],
                "original_score": score_record["score"],
                "masked_score": masked_result["score"],
                "score_collapses": masked_result["score"] < score_record["score"],
                "decision_impact": "confirms positive-control shortcut dependence",
            }
        )
    return {
        "producer_function": "build_surface_ablation_results",
        "task_id": TASK_CARD_ID,
        "ablations": ablations,
        "claim_ceiling": "surface-ablation positive-control check only; no mechanism evidence",
    }


def _changed_or_new_paths() -> list[str]:
    output = _safe_git_raw(["status", "--porcelain=v1"])
    paths = []
    for line in output.splitlines():
        if not line.strip():
            continue
        raw = line[3:] if len(line) > 3 else line
        if " -> " in raw:
            raw = raw.split(" -> ", 1)[1]
        paths.append(raw.replace("\\", "/"))
    return sorted(paths)


def build_forbidden_action_guard() -> dict[str, Any]:
    changed = _changed_or_new_paths()
    allowed_prefixes = [
        f"src/{TASK_ID}/",
        f"tests/test_{TASK_ID}.py",
        f"artifacts/{TASK_ID}/",
        f"docs/research/{REPORT_NAME}",
    ]
    forbidden = [
        path
        for path in changed
        if not any(path == prefix.rstrip("/") or path.startswith(prefix) for prefix in allowed_prefixes)
    ]
    return {
        "producer_function": "build_forbidden_action_guard",
        "changed_or_new_paths": changed,
        "allowed_prefixes": allowed_prefixes,
        "forbidden_files_modified": forbidden,
        "candidate_code_created": any("candidate" in Path(path).name.lower() and path.startswith("src/") for path in changed),
        "candidate_score_created": False,
        "tournament_execution_attempted": False,
        "gate4_replacement_card_created": False,
        "runtime_or_mainline_path_created": any(
            path.startswith(("runtime/", "admission/", "bridge/", "src/ego_mainline", "src/same_agent_bridge"))
            for path in changed
        ),
        "llm_rag_ui_companion_path_created": any(
            token in path.lower() for path in changed for token in ["llm", "rag", "ui/", "companion"]
        ),
        "forbidden_action_guard_passed": not forbidden,
    }


def build_survivor_outputs(family_decisions: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    survivors = [row for row in family_decisions["decisions"] if row["decision"] == "survives_baseline_preflight_only"]
    closed = [row for row in family_decisions["decisions"] if row["decision"] == "closed_by_faithful_cheap_baseline"]
    redesign = [row for row in family_decisions["decisions"] if row["decision"] == "needs_redesign"]
    return (
        {"producer_function": "build_survivors", "families": survivors, "count": len(survivors)},
        {"producer_function": "build_closed_families", "families": closed, "count": len(closed)},
        {"producer_function": "build_needs_redesign", "families": redesign, "count": len(redesign)},
    )


def build_future_tournament_eligibility(
    *,
    survivors: dict[str, Any],
    source_pin: dict[str, Any],
    positive_controls: dict[str, Any],
    forbidden_guard: dict[str, Any],
) -> dict[str, Any]:
    eligible = (
        survivors["count"] >= 2
        and source_pin["source_pin_integrity_passed"]
        and positive_controls["all_matched"]
        and forbidden_guard["forbidden_action_guard_passed"]
        and not forbidden_guard["candidate_code_created"]
    )
    return {
        "producer_function": "build_future_tournament_eligibility",
        "eligible_for_future_tournament_execution_card": eligible,
        "survivor_count": survivors["count"],
        "required_survivor_count": 2,
        "source_pins_verified": source_pin["source_pin_integrity_passed"],
        "positive_controls_passed": positive_controls["all_matched"],
        "forbidden_action_guard_passed": forbidden_guard["forbidden_action_guard_passed"],
        "candidate_code_created": forbidden_guard["candidate_code_created"],
        "claim_ceiling": "eligibility to draft a future separate task card only; no tournament execution authorization",
    }


def build_baseline_run_manifest(
    baseline_score_matrix: dict[str, Any],
    positive_controls: dict[str, Any],
) -> dict[str, Any]:
    rows = baseline_score_matrix["rows"]
    positive_score_records = [
        row["score_record"]
        for row in positive_controls["controls"]
        if row.get("score_record") is not None
    ]
    return {
        "producer_function": "build_baseline_run_manifest",
        "declared_registry_baseline_rows": len(rows),
        "declared_registry_rows_callable_invoked": all(row["callable_invoked"] for row in rows),
        "families_with_invoked_baseline_rows": sorted({row["family_id"] for row in rows}),
        "positive_control_score_record_count": len(positive_score_records),
        "positive_control_scores_recomputable": True,
        "candidate_code_created": False,
        "tournament_execution_attempted": False,
    }


def build_provenance_manifest(
    baseline_score_matrix: dict[str, Any],
    positive_controls: dict[str, Any],
    run_id: str,
) -> dict[str, Any]:
    positive_score_records = [
        row["score_record"]
        for row in positive_controls["controls"]
        if row.get("score_record") is not None
    ]
    baseline_score_records = baseline_score_matrix["rows"] + positive_score_records
    manifest = {
        "producer_function": "build_provenance_manifest",
        "task_id": TASK_CARD_ID,
        "run_id": run_id,
        "required_fields": list(PROVENANCE_REQUIRED_FIELDS),
        "baseline_score_records": baseline_score_records,
        "static_score_literals_accepted": False,
        "verification": None,
    }
    manifest["verification"] = verify_provenance_manifest(manifest)
    return manifest


def verify_provenance_manifest(manifest: dict[str, Any]) -> dict[str, Any]:
    reasons = []
    records = manifest.get("baseline_score_records", [])
    if not isinstance(records, list) or not records:
        reasons.append("missing_baseline_score_records")
    for index, record in enumerate(records):
        for field in PROVENANCE_REQUIRED_FIELDS:
            if field not in record:
                reasons.append(f"missing_field:{index}:{field}")
        if record.get("static_score_injection") is True:
            reasons.append("static_score_injection")
        if record.get("producer_function") in {"literal_static_report", "static_verdict_dictionary"}:
            reasons.append("static_score_injection")
        if record.get("score") is not None and record.get("producer_function") == "run_declared_baseline_preflight_row":
            reasons.append(f"declared_registry_score_without_callable_target:{index}")
    return {
        "producer_function": "verify_provenance_manifest",
        "passed": not reasons,
        "blocking_reasons": sorted(set(reasons)),
    }


def compute_result(
    *,
    source_pin: dict[str, Any],
    registry_readback: dict[str, Any],
    closed_family_inheritance: dict[str, Any],
    family_decisions: dict[str, Any],
    positive_controls: dict[str, Any],
    provenance_manifest: dict[str, Any],
    forbidden_guard: dict[str, Any],
    future_eligibility: dict[str, Any],
    run_id: str,
) -> dict[str, Any]:
    stop_conditions = []
    closure = closed_family_inheritance.get("current_generated_gate4_partner_id_lookup_family_closure", {})
    inherited_closed_ok = (
        closure.get("best_faithful_baseline") == "partner_id_lookup_baseline"
        and closure.get("score") == 1.0
        and closure.get("threshold") == 0.8
        and closure.get("same_family_repair_allowed") is False
    )
    if not source_pin["source_pin_integrity_passed"]:
        stop_conditions.append("source_pin_integrity_failed")
    if registry_readback["family_count"] != 6:
        stop_conditions.append("inherited_family_count_mismatch")
    if registry_readback["baseline_row_count"] != 37:
        stop_conditions.append("inherited_baseline_row_count_mismatch")
    if registry_readback["ablation_row_count"] != 6:
        stop_conditions.append("inherited_ablation_row_count_mismatch")
    if registry_readback["transfer_counterfactual_row_count"] != 6:
        stop_conditions.append("inherited_transfer_counterfactual_row_count_mismatch")
    if registry_readback["missing_required_family_ids"]:
        stop_conditions.append("missing_required_family_ids")
    if registry_readback["inherited_validator_final_verdict"] != "pass":
        stop_conditions.append("inherited_validator_not_pass")
    if registry_readback["malformed_positive_control_failed_as_expected"] is not True:
        stop_conditions.append("inherited_malformed_positive_control_not_failed")
    if not inherited_closed_ok:
        stop_conditions.append("closed_family_inheritance_mismatch")
    if not positive_controls["all_matched"]:
        stop_conditions.extend(
            f"positive_control_mismatch:{row['control_id']}"
            for row in positive_controls["controls"]
            if not row["matched"]
        )
    if not provenance_manifest["verification"]["passed"]:
        stop_conditions.extend(provenance_manifest["verification"]["blocking_reasons"])
    if forbidden_guard["forbidden_files_modified"]:
        stop_conditions.append("forbidden_files_modified")
    if forbidden_guard["candidate_code_created"]:
        stop_conditions.append("candidate_code_created")

    decisions = [row["decision"] for row in family_decisions["decisions"]]
    if any(item.startswith("positive_control_mismatch:") for item in stop_conditions):
        verdict = "mechanism_family_tournament_baseline_preflight_001a_blocked_by_non_fail_able_baseline_or_positive_control_failure"
    elif any(
        item
        in stop_conditions
        for item in [
            "source_pin_integrity_failed",
            "inherited_family_count_mismatch",
            "missing_required_family_ids",
            "closed_family_inheritance_mismatch",
        ]
    ):
        verdict = "mechanism_family_tournament_baseline_preflight_001a_blocked_by_invalid_registry_or_preflight_surface"
    elif all(decision in {"closed_by_faithful_cheap_baseline", "needs_redesign"} for decision in decisions):
        verdict = "mechanism_family_tournament_baseline_preflight_001a_all_families_closed_or_needs_redesign"
    elif future_eligibility["eligible_for_future_tournament_execution_card"]:
        verdict = "mechanism_family_tournament_baseline_preflight_001a_survivors_eligible_for_future_tournament_card"
    else:
        verdict = "mechanism_family_tournament_baseline_preflight_001a_insufficient_survivors_blocked"
    return {
        "producer_function": "compute_result",
        "task_id": TASK_CARD_ID,
        "run_id": run_id,
        "verdict": verdict,
        "current_layer": "engineering-governance / callable cheap-baseline evidence hygiene",
        "mainline_integration_status": "not integrated",
        "enabled_status": "no runtime capability, no Gate4 replacement, no agent behavior, no trigger path enabled",
        "real_trigger_evidence": "Read inherited six-family registry and matrices from artifacts/mechanism_family_tournament_entry_criteria_001a; no candidate or tournament execution path was used.",
        "claim_ceiling": CLAIM_CEILING,
        "stop_conditions_triggered": sorted(set(stop_conditions)),
        "family_decision_counts": dict(Counter(decisions)),
        "future_tournament_eligibility": future_eligibility["eligible_for_future_tournament_execution_card"],
        "candidate_code_created": forbidden_guard["candidate_code_created"],
        "tournament_execution_attempted": forbidden_guard["tournament_execution_attempted"],
        "gate4_replacement_created": forbidden_guard["gate4_replacement_card_created"],
        "runtime_or_mainline_path_created": forbidden_guard["runtime_or_mainline_path_created"],
        "remote_anchor_policy": AUTO_REMOTE_ANCHOR,
        "remote_anchor_performed": False,
        "next_minimal_closed_loop_action": "draft a separate redesign task that adds callable targets and predeclared thresholds, or explicitly close this tournament route.",
        "what_this_does_not_prove": list(CLAIM_EXCLUSIONS),
    }


def _resolve_output_dir(output_dir: str | Path | None) -> Path:
    if output_dir is None:
        return repo_root() / "artifacts" / ARTIFACT_DIR_NAME
    path = Path(output_dir)
    return path if path.is_absolute() else repo_root() / path


def execute_preflight(
    output_dir: str | Path | None = None,
    *,
    persist_artifacts: bool = True,
    force_positive_control_mismatch: str | None = None,
    test_result_readback: dict[str, Any] | None = None,
) -> dict[str, Any]:
    out = _resolve_output_dir(output_dir)
    run_id = f"{TASK_ID}_{_now().replace('-', '').replace(':', '').replace('Z', 'Z')}"
    source_pin = build_source_pin_readback()
    registry_readback = build_inherited_registry_readback()
    closed_family_inheritance = load_closed_family_inheritance()
    baseline_score_matrix = build_baseline_score_matrix(registry_readback, run_id)
    family_decisions = build_family_decisions(registry_readback, baseline_score_matrix)
    survivors, closed_families, needs_redesign = build_survivor_outputs(family_decisions)
    positive_controls = run_positive_controls(
        run_id=run_id,
        output_dir=out,
        force_positive_control_mismatch=force_positive_control_mismatch,
    )
    surface_ablation_results = build_surface_ablation_results(positive_controls)
    forbidden_guard = build_forbidden_action_guard()
    future_eligibility = build_future_tournament_eligibility(
        survivors=survivors,
        source_pin=source_pin,
        positive_controls=positive_controls,
        forbidden_guard=forbidden_guard,
    )
    baseline_run_manifest = build_baseline_run_manifest(baseline_score_matrix, positive_controls)
    provenance_manifest = build_provenance_manifest(baseline_score_matrix, positive_controls, run_id)
    result = compute_result(
        source_pin=source_pin,
        registry_readback=registry_readback,
        closed_family_inheritance=closed_family_inheritance,
        family_decisions=family_decisions,
        positive_controls=positive_controls,
        provenance_manifest=provenance_manifest,
        forbidden_guard=forbidden_guard,
        future_eligibility=future_eligibility,
        run_id=run_id,
    )
    if test_result_readback is not None:
        result["test_result_readback"] = test_result_readback
    run = {
        "task_id": TASK_CARD_ID,
        "run_id": run_id,
        "result": result,
        "source_pin_readback": source_pin,
        "inherited_registry_readback": registry_readback,
        "baseline_score_matrix": baseline_score_matrix,
        "family_decisions": family_decisions,
        "survivors": survivors,
        "closed_families": closed_families,
        "needs_redesign": needs_redesign,
        "closed_family_inheritance": closed_family_inheritance,
        "positive_control_results": positive_controls,
        "provenance_manifest": provenance_manifest,
        "baseline_run_manifest": baseline_run_manifest,
        "surface_ablation_results": surface_ablation_results,
        "forbidden_action_guard": forbidden_guard,
        "future_tournament_eligibility": future_eligibility,
    }
    if persist_artifacts:
        write_artifacts(out, run)
    return run


def write_artifacts(out: Path, run: dict[str, Any]) -> None:
    artifact_map = {
        "result.json": run["result"],
        "source_pin_readback.json": run["source_pin_readback"],
        "inherited_registry_readback.json": _without_raw_inputs(run["inherited_registry_readback"]),
        "baseline_score_matrix.json": run["baseline_score_matrix"],
        "family_decisions.json": run["family_decisions"],
        "survivors.json": run["survivors"],
        "closed_families.json": run["closed_families"],
        "needs_redesign.json": run["needs_redesign"],
        "closed_family_inheritance.json": run["closed_family_inheritance"],
        "positive_control_results.json": _without_fixture_payloads(run["positive_control_results"]),
        "provenance_manifest.json": run["provenance_manifest"],
        "baseline_run_manifest.json": run["baseline_run_manifest"],
        "surface_ablation_results.json": run["surface_ablation_results"],
        "forbidden_action_guard.json": run["forbidden_action_guard"],
        "future_tournament_eligibility.json": run["future_tournament_eligibility"],
    }
    for name, payload in artifact_map.items():
        _write_json(out / name, payload)
    fixtures = run["positive_control_results"]["fixture_payloads"]
    for control_id, payload in fixtures.items():
        _write_json(out / "positive_controls" / f"{control_id}.json", payload)
    missing = REQUIRED_ARTIFACTS - {path.name for path in out.glob("*.json")}
    if missing:
        raise RuntimeError(f"required artifacts missing after write: {sorted(missing)}")


def _without_raw_inputs(payload: dict[str, Any]) -> dict[str, Any]:
    clean = dict(payload)
    for key in [
        "raw_registry",
        "raw_baseline_matrix",
        "raw_ablation_matrix",
        "raw_transfer_counterfactual_matrix",
        "raw_validation_results",
    ]:
        clean.pop(key, None)
    return clean


def _without_fixture_payloads(payload: dict[str, Any]) -> dict[str, Any]:
    clean = dict(payload)
    clean.pop("fixture_payloads", None)
    return clean


def write_research_report(run: dict[str, Any], report_path: str | Path | None = None) -> Path:
    path = Path(report_path) if report_path is not None else repo_root() / "docs" / "research" / REPORT_NAME
    if not path.is_absolute():
        path = repo_root() / path
    path.parent.mkdir(parents=True, exist_ok=True)
    result = run["result"]
    source = run["source_pin_readback"]
    decisions = run["family_decisions"]["decisions"]
    lines = [
        "# MECHANISM-FAMILY-TOURNAMENT-BASELINE-PREFLIGHT-001A",
        "",
        f"Verdict: `{result['verdict']}`",
        "",
        "Layer: engineering-governance / callable cheap-baseline evidence hygiene.",
        "",
        "Mainline integration status: not integrated.",
        "",
        "Enabled status: no runtime capability, no Gate4 replacement, no agent behavior, no trigger path enabled.",
        "",
        f"Claim ceiling: {CLAIM_CEILING}",
        "",
        "Auto-Remote-Anchor: conditional.",
        "",
        "## Source Pin Readback",
        "",
        f"- Starting HEAD required: `{source['expected_starting_head']}`",
        f"- Current HEAD at run: `{source['current_head']}`",
        f"- Branch: `{source['branch']}`",
        f"- Entry-criteria remote anchor: `{source['entry_criteria_remote_anchor_tag']}`",
        f"- Entry-criteria remote anchor hash: `{source['entry_criteria_remote_anchor_hash']}`",
        f"- Source pin integrity passed: `{source['source_pin_integrity_passed']}`",
        "",
        "## Inherited Registry Readback",
        "",
        f"- Family count: `{run['inherited_registry_readback']['family_count']}`",
        f"- Baseline rows: `{run['inherited_registry_readback']['baseline_row_count']}`",
        f"- Ablation rows: `{run['inherited_registry_readback']['ablation_row_count']}`",
        f"- Transfer/counterfactual rows: `{run['inherited_registry_readback']['transfer_counterfactual_row_count']}`",
        f"- Inherited validator final verdict: `{run['inherited_registry_readback']['inherited_validator_final_verdict']}`",
        f"- Malformed positive control failed as expected: `{run['inherited_registry_readback']['malformed_positive_control_failed_as_expected']}`",
        "",
        "## Family Decision Table",
        "",
        "| family ID | best faithful cheap baseline | score | threshold | decision | reason |",
        "|---|---:|---:|---:|---|---|",
    ]
    for row in decisions:
        best = row["best_faithful_cheap_baseline"]
        lines.append(
            f"| `{row['family_id']}` | `{best['baseline_id']}` | `{best['score']}` | `{row['threshold']}` | `{row['decision']}` | {row['reason']} |"
        )
    lines.extend(
        [
            "",
            "## Survivors / Closed / Needs Redesign",
            "",
            f"- Survivors: `{[row['family_id'] for row in run['survivors']['families']]}`",
            f"- Closed families: `{[row['family_id'] for row in run['closed_families']['families']]}`",
            f"- Needs-redesign families: `{[row['family_id'] for row in run['needs_redesign']['families']]}`",
            f"- Future tournament eligibility: `{run['future_tournament_eligibility']['eligible_for_future_tournament_execution_card']}`",
            "",
            "## Positive Controls",
            "",
        ]
    )
    for row in run["positive_control_results"]["controls"]:
        lines.append(
            f"- `{row['control_id']}` expected `{row['expected_block_reason']}` observed `{row['observed_block_reason']}` matched `{row['matched']}`."
        )
    lines.extend(
        [
            "",
            "## Forbidden-Action Guard",
            "",
            f"- Candidate code created: `{run['forbidden_action_guard']['candidate_code_created']}`",
            f"- Tournament execution attempted: `{run['forbidden_action_guard']['tournament_execution_attempted']}`",
            f"- Gate4 replacement card created: `{run['forbidden_action_guard']['gate4_replacement_card_created']}`",
            f"- Runtime/mainline path created: `{run['forbidden_action_guard']['runtime_or_mainline_path_created']}`",
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
            "This task created no candidate code, no tournament execution, no Gate4 replacement, no runtime capability, no bridge/admission path, no EGO-mainline path, and no mechanism-validity evidence.",
            "",
            "## What This Does Not Prove",
            "",
            *[f"- {item}" for item in CLAIM_EXCLUSIONS],
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
    run = execute_preflight(
        output_dir=args.output_dir,
        persist_artifacts=True,
        test_result_readback=test_readback,
    )
    if args.write_report:
        write_research_report(run)
    print(json.dumps(run["result"], indent=2, sort_keys=True))
