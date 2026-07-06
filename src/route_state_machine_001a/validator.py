from __future__ import annotations

import hashlib
import json
import subprocess
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from . import state_machine


def _posix(path: str | Path) -> str:
    return str(path).replace("\\", "/")


def _relative_posix(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return _posix(path)


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def code_path_hash() -> str:
    digest = hashlib.sha256()
    for path in sorted(
        [Path(__file__), Path(state_machine.__file__)],
        key=lambda item: item.as_posix(),
    ):
        digest.update(path.name.encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def _new_error(code: str, message: str, **context: Any) -> dict[str, Any]:
    payload: dict[str, Any] = {"code": code, "message": message}
    if context:
        payload["context"] = context
    return payload


def _non_empty_string_list(value: Any) -> bool:
    return isinstance(value, list) and any(isinstance(item, str) and item.strip() for item in value)


def _normalized_set(paths: list[str] | tuple[str, ...] | None) -> set[str]:
    return {_posix(path).strip().lstrip("./") for path in (paths or [])}


def _path_is_authorized(path: str, authorized_paths: list[str] | tuple[str, ...] | None) -> bool:
    normalized = _posix(path).strip().lstrip("./")
    for authorized in _normalized_set(authorized_paths):
        if normalized == authorized:
            return True
        if authorized.endswith("/") and normalized.startswith(authorized):
            return True
    return False


def is_roadmap_like_changed_file(path: str) -> bool:
    normalized = _posix(path).lower()
    if not normalized.startswith(("docs/", "src/", "tests/", "artifacts/")):
        return False
    basename = normalized.rsplit("/", 1)[-1]
    searchable = f"{normalized} {basename.replace('_', '-')}"
    return any(marker in searchable for marker in state_machine.ROADMAP_LIKE_MARKERS)


def validate_route_payload(
    *,
    route_id: str,
    state_payload: dict[str, Any] | None,
    closure_payload: dict[str, Any] | None,
    changed_files: list[str] | None = None,
    authorized_paths: list[str] | tuple[str, ...] | None = None,
) -> dict[str, Any]:
    errors: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []

    if not isinstance(state_payload, dict):
        errors.append(_new_error("missing_or_invalid_state_json", "state.json must be a JSON object."))
        state_payload = {}

    current_state = state_payload.get("current_state")
    if current_state not in state_machine.ROUTE_STATES:
        errors.append(
            _new_error(
                "invalid_current_state",
                "Route current_state is not in the frozen enum.",
                current_state=current_state,
                valid_states=list(state_machine.ROUTE_STATES),
            )
        )

    state_route_id = state_payload.get("route_id")
    if state_route_id and state_route_id != route_id:
        warnings.append(
            _new_error(
                "state_route_id_mismatch",
                "state.json route_id differs from directory route_id.",
                state_route_id=state_route_id,
                directory_route_id=route_id,
            )
        )

    if current_state == "CLOSURE_REVIEW_REQUIRED" and closure_payload is None:
        errors.append(
            _new_error(
                "closure_review_required_missing_closure_json",
                "CLOSURE_REVIEW_REQUIRED routes must include closure.json.",
            )
        )

    closure_type = None
    if closure_payload is not None:
        if not isinstance(closure_payload, dict):
            errors.append(_new_error("invalid_closure_json", "closure.json must be a JSON object."))
            closure_payload = {}

        closure_type = closure_payload.get("closure_type")
        if not closure_type:
            errors.append(_new_error("missing_closure_type", "closure.json must include closure_type."))
        elif closure_type not in state_machine.CLOSURE_TYPES:
            errors.append(
                _new_error(
                    "invalid_closure_type",
                    "closure_type is not in the frozen enum.",
                    closure_type=closure_type,
                    valid_closure_types=list(state_machine.CLOSURE_TYPES),
                )
            )

        if not _non_empty_string_list(closure_payload.get("allowed_next_actions")):
            errors.append(
                _new_error(
                    "missing_non_empty_allowed_next_actions",
                    "closure.json must include non-empty allowed_next_actions.",
                )
            )

        if not _non_empty_string_list(closure_payload.get("forbidden_next_actions")):
            errors.append(
                _new_error(
                    "missing_non_empty_forbidden_next_actions",
                    "closure.json must include non-empty forbidden_next_actions.",
                )
            )

        claim_ceiling = closure_payload.get("claim_ceiling")
        if not isinstance(claim_ceiling, dict) or not claim_ceiling.get("max"):
            errors.append(
                _new_error(
                    "missing_claim_ceiling_max",
                    "closure.json must include claim_ceiling.max.",
                )
            )

        evidence_status = closure_payload.get("evidence_status")
        if closure_type == "THEORY_PRESSURE":
            missing = [
                key
                for key in state_machine.REQUIRED_THEORY_PRESSURE_EVIDENCE
                if not isinstance(evidence_status, dict) or evidence_status.get(key) != "present"
            ]
            if missing:
                errors.append(
                    _new_error(
                        "theory_pressure_missing_required_evidence",
                        "THEORY_PRESSURE requires baseline, ablation, replay, and provenance marked present.",
                        missing_or_not_present=missing,
                    )
                )

        if closure_type == "INSTRUMENT_INVALID" and closure_payload.get("theory_pressure_authorized") is True:
            errors.append(
                _new_error(
                    "instrument_invalid_authorizes_theory_pressure",
                    "INSTRUMENT_INVALID closure cannot authorize theory pressure.",
                )
            )

        if closure_type == "ARTIFACT_ONLY" and closure_payload.get("mechanism_evidence_authorized") is True:
            errors.append(
                _new_error(
                    "artifact_only_authorizes_mechanism_evidence",
                    "ARTIFACT_ONLY closure cannot authorize mechanism evidence.",
                )
            )

        allowed_actions = closure_payload.get("allowed_next_actions")
        if closure_type == "IMPLEMENTATION_DEFECT" and isinstance(allowed_actions, list):
            normalized_actions = {str(action).strip() for action in allowed_actions}
            if "start_new_mechanism_route" in normalized_actions:
                errors.append(
                    _new_error(
                        "implementation_defect_allows_new_mechanism_route",
                        "IMPLEMENTATION_DEFECT cannot allow start_new_mechanism_route.",
                    )
                )

    if current_state == "CLOSURE_REVIEW_REQUIRED":
        blocked_changed_files = [
            _posix(path)
            for path in (changed_files or [])
            if is_roadmap_like_changed_file(path) and not _path_is_authorized(path, authorized_paths)
        ]
        if blocked_changed_files:
            errors.append(
                _new_error(
                    "unresolved_closure_with_roadmap_like_changed_file",
                    "Roadmap-like changed files are blocked while CLOSURE_REVIEW_REQUIRED is unresolved.",
                    changed_files=blocked_changed_files,
                )
            )

    return {
        "route_id": route_id,
        "current_state": current_state,
        "closure_type": closure_type,
        "validation_errors": errors,
        "validation_warnings": warnings,
        "verdict": "pass" if not errors else "fail",
    }


def _parse_json_file(path: Path, errors: list[dict[str, Any]]) -> dict[str, Any] | None:
    if not path.exists():
        errors.append(_new_error("missing_state_json", "Route is missing state.json.", path=_posix(path)))
        return None
    try:
        payload = load_json(path)
    except json.JSONDecodeError as exc:
        errors.append(_new_error("invalid_json", "JSON file could not be parsed.", path=_posix(path), error=str(exc)))
        return None
    if not isinstance(payload, dict):
        errors.append(_new_error("json_not_object", "JSON file must contain an object.", path=_posix(path)))
        return None
    return payload


def _route_input_artifacts(routes_dir: Path) -> list[str]:
    if not routes_dir.exists():
        return []
    artifacts: list[str] = []
    for path in sorted(routes_dir.glob("*/*")):
        if path.is_file():
            artifacts.append(path.relative_to(routes_dir).as_posix())
    return artifacts


def validate_routes_tree(
    *,
    routes_dir: Path,
    changed_files: list[str] | None = None,
    authorized_paths: list[str] | tuple[str, ...] | None = None,
) -> dict[str, Any]:
    errors: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []
    route_results: list[dict[str, Any]] = []

    if not routes_dir.exists():
        errors.append(_new_error("missing_routes_dir", "Route artifact directory is missing.", path=_posix(routes_dir)))
        return {
            "producer_function": "validate_routes_tree",
            "route_count": 0,
            "routes": [],
            "input_artifacts": [],
            "changed_files": changed_files or [],
            "validation_errors": errors,
            "validation_warnings": warnings,
            "verdict": "fail",
        }

    route_dirs = sorted([path for path in routes_dir.iterdir() if path.is_dir()], key=lambda path: path.name)
    if not route_dirs:
        errors.append(_new_error("no_routes_found", "Route artifact directory contains no routes."))

    for route_dir in route_dirs:
        route_id = route_dir.name
        local_errors: list[dict[str, Any]] = []
        state_payload = _parse_json_file(route_dir / "state.json", local_errors)
        closure_path = route_dir / "closure.json"
        closure_payload: dict[str, Any] | None = None
        if closure_path.exists():
            try:
                loaded_closure = load_json(closure_path)
            except json.JSONDecodeError as exc:
                local_errors.append(
                    _new_error(
                        "invalid_json",
                        "JSON file could not be parsed.",
                        path=_posix(closure_path),
                        error=str(exc),
                    )
                )
            else:
                if isinstance(loaded_closure, dict):
                    closure_payload = loaded_closure
                else:
                    local_errors.append(
                        _new_error("json_not_object", "JSON file must contain an object.", path=_posix(closure_path))
                    )

        result = validate_route_payload(
            route_id=route_id,
            state_payload=state_payload,
            closure_payload=closure_payload,
            changed_files=changed_files,
            authorized_paths=authorized_paths,
        )
        result["validation_errors"] = local_errors + result["validation_errors"]
        if result["validation_errors"]:
            result["verdict"] = "fail"
        route_results.append(result)

    for result in route_results:
        errors.extend(
            {
                **error,
                "route_id": result["route_id"],
            }
            for error in result["validation_errors"]
        )
        warnings.extend(
            {
                **warning,
                "route_id": result["route_id"],
            }
            for warning in result["validation_warnings"]
        )

    return {
        "producer_function": "validate_routes_tree",
        "route_count": len(route_dirs),
        "routes": route_results,
        "input_artifacts": _route_input_artifacts(routes_dir),
        "changed_files": [_posix(path) for path in (changed_files or [])],
        "validation_errors": errors,
        "validation_warnings": warnings,
        "verdict": "pass" if not errors else "fail",
    }


def git_changed_files(repo_root: Path) -> list[str]:
    try:
        completed = subprocess.run(
            ["git", "status", "--porcelain=v1", "--untracked-files=all"],
            cwd=repo_root,
            check=True,
            capture_output=True,
            text=True,
            timeout=10,
        )
    except (OSError, subprocess.SubprocessError):
        return []

    changed: list[str] = []
    for line in completed.stdout.splitlines():
        if not line:
            continue
        path_text = line[3:]
        if " -> " in path_text:
            path_text = path_text.split(" -> ", 1)[1]
        changed.append(_posix(path_text))
    return changed


def build_validation_report(
    repo_root: str | Path,
    *,
    changed_files: list[str] | None = None,
    authorized_paths: list[str] | tuple[str, ...] | None = None,
) -> dict[str, Any]:
    root = Path(repo_root)
    effective_changed_files = git_changed_files(root) if changed_files is None else changed_files
    effective_authorized_paths = (
        list(state_machine.AUTHORIZED_TASK_PATHS) if authorized_paths is None else list(authorized_paths)
    )
    routes_dir = root / state_machine.TASK_ARTIFACT_DIR / "routes"
    route_tree = validate_routes_tree(
        routes_dir=routes_dir,
        changed_files=effective_changed_files,
        authorized_paths=effective_authorized_paths,
    )
    input_artifacts = [
        f"{state_machine.TASK_ARTIFACT_DIR}/routes/{artifact}"
        for artifact in route_tree["input_artifacts"]
    ]
    schema_dir = root / state_machine.TASK_ARTIFACT_DIR / "schemas"
    for schema in sorted(schema_dir.glob("*.schema.json")) if schema_dir.exists() else []:
        input_artifacts.append(_relative_posix(schema, root))

    return {
        "task_id": state_machine.TASK_ID,
        "producer_function": "build_validation_report",
        "input_artifacts": sorted(input_artifacts),
        "run_id": f"{state_machine.TASK_ID.lower()}-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}-{uuid.uuid4().hex[:8]}",
        "aggregation_rule": "verdict is pass iff validate_routes_tree returns zero validation_errors",
        "code_path_hash": code_path_hash(),
        "validation_errors": route_tree["validation_errors"],
        "validation_warnings": route_tree["validation_warnings"],
        "route_count": route_tree["route_count"],
        "routes": [
            {
                "route_id": result["route_id"],
                "current_state": result["current_state"],
                "closure_type": result["closure_type"],
                "verdict": result["verdict"],
            }
            for result in route_tree["routes"]
        ],
        "changed_files": route_tree["changed_files"],
        "authorized_paths": sorted(effective_authorized_paths),
        "claim_ceiling": "local route-governance validation only; no mechanism, theory, agency, autonomy, subjectivity, consciousness, EGO readiness, companion readiness, or mainline-effect claim",
        "verdict": route_tree["verdict"],
    }


def validation_report_path(repo_root: str | Path) -> Path:
    return Path(repo_root) / state_machine.TASK_ARTIFACT_DIR / "validation_report.json"


def write_validation_report(repo_root: str | Path, report: dict[str, Any]) -> Path:
    path = validation_report_path(repo_root)
    write_json(path, report)
    return path


def build_status(repo_root: str | Path) -> dict[str, Any]:
    report = build_validation_report(repo_root)
    return {
        "task_id": state_machine.TASK_ID,
        "route_count": report["route_count"],
        "verdict": report["verdict"],
        "routes": report["routes"],
        "validation_error_count": len(report["validation_errors"]),
        "validation_warning_count": len(report["validation_warnings"]),
        "claim_ceiling": report["claim_ceiling"],
    }


def build_dashboard(repo_root: str | Path) -> dict[str, Any]:
    report = build_validation_report(repo_root)
    return {
        "task_id": state_machine.TASK_ID,
        "producer_function": "build_dashboard",
        "verdict": report["verdict"],
        "route_count": report["route_count"],
        "routes": report["routes"],
        "validation_error_codes": sorted({error["code"] for error in report["validation_errors"]}),
        "validation_warning_codes": sorted({warning["code"] for warning in report["validation_warnings"]}),
        "transition_command_status": "deferred_in_001a_first_local_version",
        "claim_ceiling": report["claim_ceiling"],
    }
