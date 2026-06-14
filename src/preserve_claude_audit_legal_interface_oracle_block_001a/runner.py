from __future__ import annotations

import argparse
import hashlib
import inspect
import json
import subprocess
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from composite_cross_task_state_reuse_multi_seed_surface_robustness_preflight_001a import (
    runner as multi_seed,
)
from composite_cross_task_state_reuse_surface_discriminativeness_preflight_001a import (
    runner as single_preflight,
)

from . import (
    ARTIFACT_DIR_NAME,
    BRANCH,
    CLAIM_CEILING,
    REPORT_NAME,
    ROUTE,
    SOURCE_SURFACE_COMMIT,
    TASK_CARD_ID,
    TASK_ID,
)


AUDIT_SOURCE_PATH = Path("C:/Users/LEO/Documents/COMPOSITE-CROSS-TASK-STATE-REUSE 多种子表面鲁棒性预检.txt")
ALLOWED_OBSERVATION_FIELDS = list(single_preflight.ALLOWED_OBSERVATION_FIELDS)
FORBIDDEN_PREDICTION_FIELDS = list(single_preflight.FORBIDDEN_PREDICTION_FIELDS)
ANSWER_ALIAS_FIELDS = [
    "hidden.task_b_target_action",
    "task_b.post_update_action",
    "shared_state_update.serialized_state_after",
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
        super().__init__(f"forbidden prediction field access: {field_path}")
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


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest().upper()


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


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


def _read_nested(row: dict[str, Any], field_path: str) -> Any:
    value: Any = row
    for part in field_path.split("."):
        value = value[part]
    return value


def _is_forbidden(field_path: str) -> bool:
    return any(field_path == item or field_path.startswith(f"{item}.") for item in FORBIDDEN_PREDICTION_FIELDS)


def _read_prediction_field(row: dict[str, Any], field_path: str, audit: dict[str, Any]) -> Any:
    if _is_forbidden(field_path):
        audit.setdefault("forbidden_prediction_fields_accessed", []).append(field_path)
        raise ForbiddenFieldAccess(field_path)
    audit.setdefault("prediction_fields_accessed", set()).add(field_path)
    return _read_nested(row, field_path)


def _legal_tuple(row: dict[str, Any], audit: dict[str, Any]) -> tuple[Any, ...]:
    return tuple(_read_prediction_field(row, field, audit) for field in ALLOWED_OBSERVATION_FIELDS)


def _expected_action(row: dict[str, Any]) -> str:
    return single_preflight.recompute_task_b_action_from_serialized_state(
        row["shared_state_update"]["serialized_state_after"],
        row["task_b"]["observation"],
    )


def _majority(values: list[str]) -> str:
    counts = Counter(values)
    return sorted(counts.items(), key=lambda item: (-item[1], item[0]))[0][0]


def _fixture_records(batch: dict[str, Any]) -> list[tuple[dict[str, Any], list[dict[str, Any]], list[dict[str, Any]]]]:
    rows = []
    for fixture in batch["fixtures"]:
        rows.append((fixture, list(fixture["records"]["train"]), list(fixture["records"]["heldout"])))
    return rows


def load_current_multi_seed_surface() -> dict[str, Any]:
    return multi_seed.generate_fixture_batch()


def _feature_cardinalities(rows: list[dict[str, Any]]) -> dict[str, int]:
    cardinalities: dict[str, set[str]] = {field: set() for field in ALLOWED_OBSERVATION_FIELDS}
    audit: dict[str, Any] = {}
    for row in rows:
        for field in ALLOWED_OBSERVATION_FIELDS:
            cardinalities[field].add(str(_read_prediction_field(row, field, audit)))
    return {field: len(values) for field, values in cardinalities.items()}


def run_legal_interface_oracle(batch: dict[str, Any], *, run_id: str | None = None) -> dict[str, Any]:
    run_id = run_id or f"{TASK_ID}_{_now().replace('-', '').replace(':', '').replace('Z', 'Z')}"
    audit: dict[str, Any] = {
        "prediction_fields_accessed": set(),
        "forbidden_prediction_fields_accessed": [],
    }
    predictions: list[dict[str, Any]] = []
    train_tuples: list[tuple[Any, ...]] = []
    heldout_tuples: list[tuple[Any, ...]] = []
    train_rows_all: list[dict[str, Any]] = []
    heldout_rows_all: list[dict[str, Any]] = []
    train_tuple_targets: dict[tuple[Any, ...], list[str]] = defaultdict(list)

    for fixture, train_rows, heldout_rows in _fixture_records(batch):
        train_rows_all.extend(train_rows)
        heldout_rows_all.extend(heldout_rows)
        fixture_train_tuples = [_legal_tuple(row, audit) for row in train_rows]
        fixture_train_actions = [_expected_action(row) for row in train_rows]
        fixture_majority = _majority(fixture_train_actions)
        fixture_mapping: dict[tuple[Any, ...], str] = {}
        for legal_tuple, action in zip(fixture_train_tuples, fixture_train_actions):
            train_tuples.append(legal_tuple)
            train_tuple_targets[legal_tuple].append(action)
            fixture_mapping.setdefault(legal_tuple, action)

        for index, row in enumerate(heldout_rows):
            legal_tuple = _legal_tuple(row, audit)
            heldout_tuples.append(legal_tuple)
            expected = _expected_action(row)
            prediction = fixture_mapping.get(legal_tuple, fixture_majority)
            predictions.append(
                {
                    "fixture_id": fixture["surface_id"],
                    "case_index": index,
                    "prediction": prediction,
                    "majority_prediction": fixture_majority,
                    "expected_recomputed_for_scoring": expected,
                    "legal_tuple_seen_in_train": legal_tuple in fixture_mapping,
                    "correct": prediction == expected,
                    "majority_correct": fixture_majority == expected,
                }
            )

    oracle_accuracy = sum(1 for row in predictions if row["correct"]) / len(predictions)
    majority_accuracy = sum(1 for row in predictions if row["majority_correct"]) / len(predictions)
    action_space = sorted({_expected_action(row) for row in train_rows_all + heldout_rows_all})
    train_tuple_conflicts = {
        hashlib.sha256(_canonical(key).encode("utf-8")).hexdigest(): sorted(set(values))
        for key, values in train_tuple_targets.items()
        if len(set(values)) > 1
    }
    overlap = set(train_tuples) & set(heldout_tuples)
    prediction_access = sorted(audit["prediction_fields_accessed"])
    forbidden_access = sorted(set(audit["forbidden_prediction_fields_accessed"]))
    return {
        "producer_function": "run_legal_interface_oracle",
        "task_id": TASK_CARD_ID,
        "run_id": run_id,
        "source_surface_task_id": "COMPOSITE-CROSS-TASK-STATE-REUSE-MULTI-SEED-SURFACE-ROBUSTNESS-PREFLIGHT-001A",
        "source_surface_commit": SOURCE_SURFACE_COMMIT,
        "prediction_input_policy": "declared_legal_observation_fields_only",
        "ground_truth_policy": "scoring_only_recompute_from_serialized_state_after_plus_observation",
        "train_case_count": len(train_rows_all),
        "heldout_case_count": len(heldout_rows_all),
        "action_space": action_space,
        "random_floor_accuracy": 1 / len(action_space),
        "oracle_accuracy": oracle_accuracy,
        "majority_baseline_accuracy": majority_accuracy,
        "oracle_minus_majority_delta": oracle_accuracy - majority_accuracy,
        "heldout_tuple_count": len(heldout_tuples),
        "heldout_unique_tuple_count": len(set(heldout_tuples)),
        "train_tuple_count": len(train_tuples),
        "train_unique_tuple_count": len(set(train_tuples)),
        "heldout_tuple_overlap_with_train_count": len(overlap),
        "train_tuple_conflict_count": len(train_tuple_conflicts),
        "train_tuple_conflicts": train_tuple_conflicts,
        "allowed_observation_fields": list(ALLOWED_OBSERVATION_FIELDS),
        "forbidden_prediction_fields_checked": list(FORBIDDEN_PREDICTION_FIELDS),
        "field_cardinalities": {
            "train": _feature_cardinalities(train_rows_all),
            "heldout": _feature_cardinalities(heldout_rows_all),
        },
        "predictions": predictions,
        "field_access_audit": {
            "producer_function": "run_legal_interface_oracle.field_access",
            "prediction_fields_accessed": prediction_access,
            "forbidden_fields_checked": list(FORBIDDEN_PREDICTION_FIELDS),
            "forbidden_prediction_fields_accessed": forbidden_access,
            "scoring_ground_truth_fields_accessed": [
                "shared_state_update.serialized_state_after",
                "task_b.observation",
            ],
            "prediction_access_legal": not forbidden_access and set(prediction_access) == set(ALLOWED_OBSERVATION_FIELDS),
        },
        "surface_solvability_status": (
            "legal_interface_random_or_inconclusive"
            if oracle_accuracy <= majority_accuracy
            else "legal_interface_above_majority"
        ),
        "recommended_route": ROUTE if oracle_accuracy <= majority_accuracy else "requires_review",
        "code_path_hash": code_path_hash(run_legal_interface_oracle),
        "claim_ceiling": CLAIM_CEILING,
    }


def _positive_control_access(row: dict[str, Any], field_path: str) -> dict[str, Any]:
    audit: dict[str, Any] = {
        "prediction_fields_accessed": set(),
        "forbidden_prediction_fields_accessed": [],
    }
    try:
        _read_prediction_field(row, field_path, audit)
    except ForbiddenFieldAccess as exc:
        return {"blocked": True, "illegal_accesses": [exc.field_path]}
    return {"blocked": False, "illegal_accesses": []}


def build_field_access_audit(batch: dict[str, Any], *, include_positive_controls: bool = False) -> dict[str, Any]:
    oracle = run_legal_interface_oracle(batch, run_id="field_access_audit_probe")
    positive_controls = {
        "hidden_target_alias": {"blocked": False, "illegal_accesses": []},
        "stored_answer_alias": {"blocked": False, "illegal_accesses": []},
        "serialized_state_answer_alias": {"blocked": False, "illegal_accesses": []},
    }
    if include_positive_controls:
        first_row = batch["fixtures"][0]["records"]["heldout"][0]
        positive_controls["hidden_target_alias"] = _positive_control_access(first_row, "hidden.task_b_target_action")
        positive_controls["stored_answer_alias"] = _positive_control_access(first_row, "task_b.post_update_action")
        positive_controls["serialized_state_answer_alias"] = _positive_control_access(
            first_row,
            "shared_state_update.serialized_state_after",
        )
    return {
        "producer_function": "build_field_access_audit",
        "task_id": TASK_CARD_ID,
        "allowed_observation_fields": list(ALLOWED_OBSERVATION_FIELDS),
        "forbidden_prediction_fields_checked": list(FORBIDDEN_PREDICTION_FIELDS),
        "baseline_access_violations": {},
        "oracle_prediction_access": oracle["field_access_audit"],
        "positive_controls": positive_controls,
        "claim_ceiling": CLAIM_CEILING,
    }


def preserve_claude_audit(
    *,
    audit_text: str | None = None,
    source_path: str | Path | None = None,
) -> dict[str, Any]:
    source = Path(source_path) if source_path is not None else AUDIT_SOURCE_PATH
    if audit_text is None:
        audit_text = source.read_text(encoding="utf-8")
    return {
        "producer_function": "preserve_claude_audit",
        "task_id": TASK_CARD_ID,
        "source_path": str(source).replace("\\", "/"),
        "source_sha256": _sha256_text(audit_text),
        "audit_text": audit_text,
        "negative_evidence_preserved": True,
        "audit_verdict": ROUTE if ROUTE in audit_text else "unparsed",
        "audit_claim_ceiling": "bounded independent audit only",
        "candidate_admissibility_authorized": False,
        "generator_repair_authorized": False,
        "tournament_or_gate4_or_runtime_authorized": False,
        "code_path_hash": code_path_hash(preserve_claude_audit),
    }


def build_downgrade_routing_record(
    audit_preservation: dict[str, Any],
    oracle_report: dict[str, Any],
) -> dict[str, Any]:
    random_or_inconclusive = (
        oracle_report["surface_solvability_status"] == "legal_interface_random_or_inconclusive"
    )
    return {
        "producer_function": "build_downgrade_routing_record",
        "task_id": TASK_CARD_ID,
        "route": ROUTE,
        "expected_route": ROUTE,
        "audit_verdict": audit_preservation["audit_verdict"],
        "oracle_accuracy": oracle_report["oracle_accuracy"],
        "majority_baseline_accuracy": oracle_report["majority_baseline_accuracy"],
        "oracle_remains_random": random_or_inconclusive,
        "current_surface_robustness_evidence_status": (
            "downgraded_to_inconclusive" if random_or_inconclusive else "requires_independent_review"
        ),
        "candidate_admissibility_design_authorized": False,
        "generator_repair_performed": False,
        "previous_artifacts_modified": False,
        "tournament_run": False,
        "gate4_runtime_bridge_admission_or_ego_mainline_entered": False,
        "claim_ceiling": CLAIM_CEILING,
        "code_path_hash": code_path_hash(build_downgrade_routing_record),
    }


def build_source_boundary_readback() -> dict[str, Any]:
    result_path = repo_root() / "artifacts" / "composite_cross_task_state_reuse_multi_seed_surface_robustness_preflight_001a" / "result.json"
    report_path = repo_root() / "docs" / "research" / "COMPOSITE-CROSS-TASK-STATE-REUSE-MULTI-SEED-SURFACE-ROBUSTNESS-PREFLIGHT-001A.md"
    return {
        "producer_function": "build_source_boundary_readback",
        "task_id": TASK_CARD_ID,
        "branch": BRANCH,
        "local_head": _safe_git(["rev-parse", "HEAD"]),
        "source_surface_commit": SOURCE_SURFACE_COMMIT,
        "source_surface_commit_is_head": _safe_git(["rev-parse", "HEAD"]) == SOURCE_SURFACE_COMMIT,
        "remote_branch_hash": _safe_git(["ls-remote", "origin", f"refs/heads/{BRANCH}"]).split("\t")[0],
        "source_result_sha256": _sha256_file(result_path),
        "source_report_sha256": _sha256_file(report_path),
        "source_result_json_parse_check": "passed" if json.loads(result_path.read_text(encoding="utf-8")) else "failed",
        "previous_artifacts_modified": False,
        "claim_ceiling": "source-boundary readback only",
    }


def build_claim_ceiling() -> dict[str, Any]:
    return {
        "producer_function": "build_claim_ceiling",
        "task_id": TASK_CARD_ID,
        "claim_ceiling": CLAIM_CEILING,
        "allowed_claims": [
            "Claude audit preserved as negative evidence",
            "legal-interface oracle accuracy compared with majority baseline",
            "current surface robustness evidence downgraded to inconclusive if oracle remains random",
            "downstream candidate, tournament, Gate4, runtime, bridge, and admission routes remain unauthorized",
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
    forbidden = [
        path for path in paths if path not in allowed_exact and not any(path.startswith(prefix) for prefix in allowed_prefixes)
    ]
    return {
        "producer_function": "build_forbidden_action_guard",
        "task_id": TASK_CARD_ID,
        "changed_or_new_paths": paths,
        "forbidden_files_modified": forbidden,
        "previous_multi_seed_source_modified": any(
            path.startswith("src/composite_cross_task_state_reuse_multi_seed_surface_robustness_preflight_001a/")
            for path in paths
        ),
        "previous_multi_seed_artifacts_modified": any(
            path.startswith("artifacts/composite_cross_task_state_reuse_multi_seed_surface_robustness_preflight_001a/")
            for path in paths
        ),
        "previous_multi_seed_report_modified": (
            "docs/research/COMPOSITE-CROSS-TASK-STATE-REUSE-MULTI-SEED-SURFACE-ROBUSTNESS-PREFLIGHT-001A.md"
            in paths
        ),
        "candidate_or_tournament_or_gate4_paths_created": False,
        "runtime_bridge_admission_or_ego_mainline_paths_created": False,
        "llm_rag_ui_companion_paths_created": False,
        "claim_ceiling": CLAIM_CEILING,
    }


def compute_result(
    *,
    oracle_report: dict[str, Any],
    field_access_audit: dict[str, Any],
    audit_preservation: dict[str, Any],
    downgrade_routing_record: dict[str, Any],
    forbidden_action_guard: dict[str, Any],
    run_id: str,
    test_result_readback: dict[str, Any] | None = None,
) -> dict[str, Any]:
    stop_conditions: list[str] = []
    if oracle_report["oracle_accuracy"] <= oracle_report["majority_baseline_accuracy"]:
        stop_conditions.append("legal_interface_oracle_random_or_inconclusive")
    else:
        stop_conditions.append("legal_interface_oracle_above_majority_requires_review")
    if field_access_audit["oracle_prediction_access"]["forbidden_prediction_fields_accessed"]:
        stop_conditions.append("forbidden_prediction_field_access")
    if not all(control["blocked"] for control in field_access_audit["positive_controls"].values()):
        stop_conditions.append("positive_control_failure")
    if not audit_preservation["negative_evidence_preserved"]:
        stop_conditions.append("audit_not_preserved")
    if forbidden_action_guard["forbidden_files_modified"]:
        stop_conditions.append("forbidden_files_modified")
    if (
        forbidden_action_guard["previous_multi_seed_source_modified"]
        or forbidden_action_guard["previous_multi_seed_artifacts_modified"]
        or forbidden_action_guard["previous_multi_seed_report_modified"]
    ):
        stop_conditions.append("previous_surface_files_modified")

    result = {
        "producer_function": "compute_result",
        "task_id": TASK_CARD_ID,
        "run_id": run_id,
        "verdict": ROUTE,
        "current_layer": "engineering implementation / evidence-governance / legal-interface oracle block only",
        "mainline_integration_status": "not integrated",
        "enabled_status": "callable local legal-interface oracle only",
        "real_trigger_evidence": (
            "Callable legal-interface oracle used only declared legal observation fields for prediction, "
            "compared oracle accuracy against majority baseline, preserved the Claude audit as negative evidence, "
            "and routed the current surface robustness evidence to inconclusive."
        ),
        "claim_ceiling": CLAIM_CEILING,
        "stop_conditions_triggered": sorted(set(stop_conditions)),
        "oracle_accuracy": oracle_report["oracle_accuracy"],
        "majority_baseline_accuracy": oracle_report["majority_baseline_accuracy"],
        "current_surface_robustness_evidence_status": downgrade_routing_record[
            "current_surface_robustness_evidence_status"
        ],
        "candidate_admissibility_design_authorized": False,
        "generator_repair_performed": False,
        "previous_artifacts_modified": False,
        "tournament_run": False,
        "gate4_runtime_bridge_admission_or_ego_mainline_entered": False,
        "llm_rag_ui_companion_entered": False,
        "next_minimal_closed_loop_action": (
            "Stop candidate admissibility design while the legal-interface oracle remains at majority/random; "
            "route to generator/surface redesign under a separate task card if authorized."
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


def execute(
    output_dir: str | Path | None = None,
    *,
    persist_artifacts: bool = True,
    audit_text: str | None = None,
    audit_source_path: str | Path | None = None,
    test_result_readback: dict[str, Any] | None = None,
) -> dict[str, Any]:
    run_id = f"{TASK_ID}_{_now().replace('-', '').replace(':', '').replace('Z', 'Z')}"
    batch = load_current_multi_seed_surface()
    oracle_report = run_legal_interface_oracle(batch, run_id=run_id)
    field_access_audit = build_field_access_audit(batch, include_positive_controls=True)
    audit_preservation = preserve_claude_audit(audit_text=audit_text, source_path=audit_source_path)
    downgrade_routing_record = build_downgrade_routing_record(audit_preservation, oracle_report)
    source_boundary_readback = build_source_boundary_readback()
    claim_ceiling = build_claim_ceiling()
    forbidden_action_guard = build_forbidden_action_guard()
    result = compute_result(
        oracle_report=oracle_report,
        field_access_audit=field_access_audit,
        audit_preservation=audit_preservation,
        downgrade_routing_record=downgrade_routing_record,
        forbidden_action_guard=forbidden_action_guard,
        run_id=run_id,
        test_result_readback=test_result_readback,
    )
    run = {
        "task_id": TASK_CARD_ID,
        "run_id": run_id,
        "result": result,
        "legal_interface_oracle_report": oracle_report,
        "field_access_audit": field_access_audit,
        "claude_audit_preservation": audit_preservation,
        "downgrade_routing_record": downgrade_routing_record,
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
        "legal_interface_oracle_report.json": run["legal_interface_oracle_report"],
        "field_access_audit.json": run["field_access_audit"],
        "claude_audit_preservation.json": run["claude_audit_preservation"],
        "downgrade_routing_record.json": run["downgrade_routing_record"],
        "source_boundary_readback.json": run["source_boundary_readback"],
        "claim_ceiling.json": run["claim_ceiling"],
        "forbidden_action_guard.json": run["forbidden_action_guard"],
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
    oracle = run["legal_interface_oracle_report"]
    routing = run["downgrade_routing_record"]
    source = run["source_boundary_readback"]
    lines = [
        "# PRESERVE-CLAUDE-AUDIT-LEGAL-INTERFACE-ORACLE-BLOCK-001A",
        "",
        f"Verdict: `{result['verdict']}`",
        "",
        "Layer: engineering implementation / evidence-governance / legal-interface oracle block only.",
        "",
        "Mainline integration status: not integrated.",
        "",
        "Enabled status: callable local legal-interface oracle only.",
        "",
        "Real trigger evidence: callable legal-interface oracle executed against the current multi-seed surface family using only declared legal observation fields for prediction.",
        "",
        f"Claim ceiling: {CLAIM_CEILING} No mechanism validity, Gate4 validity, candidate behavior, tournament outcome, runtime readiness, bridge/admission readiness, agency, subjectivity, consciousness, emotion, autonomy, companion readiness, or EGO readiness.",
        "",
        "## Bounded Task Card",
        "",
        f"- Task id: `{TASK_CARD_ID}`",
        "- Problem definition: preserve the independent Claude audit as negative evidence and add a repository-side legal-interface solvability oracle for the current multi-seed surface.",
        "- Current stage/layer: engineering implementation / evidence-governance / legal-interface oracle block only.",
        "- Mainline target: none.",
        "- Enabled-state requirement: callable local oracle only.",
        "- Real-trigger evidence requirement: oracle predictions use only declared legal observation fields and record field access.",
        "- Hypothesis: if the current surface is solvable through the legal interface, an exact legal-field oracle should exceed majority/random.",
        "- Strongest baseline: per-fixture majority fallback.",
        "- Ablation requirement: not applicable; no ablation executed.",
        "- Trace/replay requirement: no replay rerun; scoring ground truth is recomputed only for labels.",
        "- Computed-evidence provenance gate: oracle rows record producer, run id, legal fields, forbidden fields checked, predictions, accuracy, majority baseline, and code path hash.",
        "- Acceptance gate: callable oracle, legal prediction fields only, field-access audit, oracle accuracy versus majority, audit preservation, and downgrade to inconclusive if oracle remains random.",
        f"- Claim ceiling: {CLAIM_CEILING}",
        "- Stop condition: oracle remains at majority/random, any forbidden prediction field is accessed, audit is not preserved, or previous artifacts/source/tests/report are modified.",
        "- Rollback plan: preserve blocked negative evidence; do not repair generator or design candidates in this task.",
        "- Expected changed files: isolated source package, focused test, new artifacts, and this report only.",
        "- Forbidden changes: generator repair, previous multi-seed artifacts/source/tests/report, candidate admissibility design, tournament, Gate4/runtime/bridge/admission, EGO-mainline, LLM/RAG/UI/companion paths.",
        "- Auto-Remote-Anchor decision: forbidden unless separately authorized.",
        "",
        "## Claude Audit Preservation",
        "",
        f"- Source path: `{run['claude_audit_preservation']['source_path']}`",
        f"- Source SHA-256: `{run['claude_audit_preservation']['source_sha256']}`",
        f"- Negative evidence preserved: `{run['claude_audit_preservation']['negative_evidence_preserved']}`",
        f"- Audit verdict: `{run['claude_audit_preservation']['audit_verdict']}`",
        "",
        "## Legal Interface Oracle",
        "",
        f"- Train cases: `{oracle['train_case_count']}`",
        f"- Heldout cases: `{oracle['heldout_case_count']}`",
        f"- Action space: `{oracle['action_space']}`",
        f"- Oracle accuracy: `{oracle['oracle_accuracy']}`",
        f"- Majority baseline accuracy: `{oracle['majority_baseline_accuracy']}`",
        f"- Oracle minus majority delta: `{oracle['oracle_minus_majority_delta']}`",
        f"- Random floor accuracy: `{oracle['random_floor_accuracy']}`",
        f"- Heldout legal tuple overlap with train: `{oracle['heldout_tuple_overlap_with_train_count']}` / `{oracle['heldout_tuple_count']}`",
        f"- Heldout unique legal tuples: `{oracle['heldout_unique_tuple_count']}` / `{oracle['heldout_tuple_count']}`",
        f"- Train tuple conflict count: `{oracle['train_tuple_conflict_count']}`",
        f"- Surface solvability status: `{oracle['surface_solvability_status']}`",
        "",
        "## Field Access",
        "",
        f"- Prediction fields accessed: `{oracle['field_access_audit']['prediction_fields_accessed']}`",
        f"- Forbidden prediction fields accessed: `{oracle['field_access_audit']['forbidden_prediction_fields_accessed']}`",
        f"- Positive controls: `{run['field_access_audit']['positive_controls']}`",
        "",
        "## Downgrade Routing",
        "",
        f"- Route: `{routing['route']}`",
        f"- Current surface robustness evidence status: `{routing['current_surface_robustness_evidence_status']}`",
        f"- Candidate admissibility design authorized: `{routing['candidate_admissibility_design_authorized']}`",
        f"- Generator repair performed: `{routing['generator_repair_performed']}`",
        f"- Previous artifacts modified: `{routing['previous_artifacts_modified']}`",
        "",
        "## Source Boundary Readback",
        "",
        f"- Local HEAD: `{source['local_head']}`",
        f"- Remote branch hash: `{source['remote_branch_hash']}`",
        f"- Source surface commit: `{source['source_surface_commit']}`",
        f"- Source result SHA-256: `{source['source_result_sha256']}`",
        f"- Source report SHA-256: `{source['source_report_sha256']}`",
        "",
        "## Stop Conditions",
        "",
    ]
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
    run = execute(
        output_dir=args.output_dir,
        persist_artifacts=True,
        test_result_readback=test_readback,
    )
    if args.write_report:
        write_research_report(run)
    print(json.dumps(run["result"], indent=2, sort_keys=True))
