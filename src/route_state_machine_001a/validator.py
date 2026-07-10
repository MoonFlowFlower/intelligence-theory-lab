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


def _string_values(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, dict):
        strings: list[str] = []
        for item in value.values():
            strings.extend(_string_values(item))
        return strings
    if isinstance(value, list):
        strings = []
        for item in value:
            strings.extend(_string_values(item))
        return strings
    return []


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


def _claim_ceiling_has_max(payload: Any) -> bool:
    return isinstance(payload, dict) and isinstance(payload.get("max"), str) and bool(payload["max"].strip())


def _source_readback_has_l014_or_equivalent(source_readback: Any) -> bool:
    strings = [item.strip() for item in _string_values(source_readback) if item.strip()]
    joined = "\n".join(strings)
    return "L-014" in joined or "L014" in joined


def _is_authorizing_value(value: Any) -> bool:
    if value is True:
        return True
    if isinstance(value, str):
        return value.strip().lower() in {"true", "yes", "authorized", "allow", "allowed"}
    return False


def _forbidden_current_frontier_authorizations(
    *,
    program_state_payload: dict[str, Any],
    route_state_payload: dict[str, Any],
) -> list[str]:
    found: set[str] = set()

    authorizations = route_state_payload.get("authorizations")
    if isinstance(authorizations, dict):
        for key in state_machine.CURRENT_FRONTIER_FORBIDDEN_AUTHORIZATIONS:
            if _is_authorizing_value(authorizations.get(key)):
                found.add(key)

    route_allowed_actions = route_state_payload.get("allowed_next_actions")
    program_allowed_actions = program_state_payload.get("allowed_next_actions")
    for action in _string_values(route_allowed_actions) + _string_values(program_allowed_actions):
        normalized = action.lower().replace("-", "_")
        for token in state_machine.CURRENT_FRONTIER_FORBIDDEN_ACTION_TOKENS:
            if token in normalized:
                found.add(token)

    return sorted(found)


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

    if route_id == state_machine.K0_PARENT_ROUTE_ID:
        if current_state not in ("REGISTERED", "READY_TO_IMPLEMENT"):
            errors.append(
                _new_error(
                    "k0_parent_state_outside_authorized_contract",
                    "The K0 parent contract permits only REGISTERED or the separately carded READY_TO_IMPLEMENT boundary.",
                    current_state=current_state,
                )
            )
        if closure_payload is not None:
            errors.append(
                _new_error(
                    "k0_parent_has_unexpected_closure",
                    "The K0 parent must not have a closure packet at REGISTERED or READY_TO_IMPLEMENT.",
                )
            )

        authorizations = state_payload.get("authorizations")
        allowed_actions = state_payload.get("allowed_next_actions")
        source_readback = state_payload.get("source_readback")
        ledger_readback = source_readback.get("ledger") if isinstance(source_readback, dict) else None

        if current_state == "REGISTERED":
            if state_payload.get("implementation_authorized") is not False:
                errors.append(
                    _new_error(
                        "k0_registered_parent_implementation_not_explicitly_false",
                        "The registered K0 parent must set implementation_authorized to false.",
                    )
                )
            invalid_authorizations = [
                key
                for key in state_machine.K0_PARENT_REQUIRED_FALSE_AUTHORIZATIONS
                if not isinstance(authorizations, dict) or authorizations.get(key) is not False
            ]
            if invalid_authorizations:
                errors.append(
                    _new_error(
                        "k0_registered_parent_forbidden_authorization",
                        "Every registered K0 parent implementation, runtime, claim, and publication authorization must be explicit false.",
                        invalid_or_missing=invalid_authorizations,
                    )
                )
            if not isinstance(allowed_actions, list) or set(allowed_actions) != set(
                state_machine.K0_PARENT_ALLOWED_ACTIONS
            ):
                errors.append(
                    _new_error(
                        "k0_registered_parent_allowed_actions_mismatch",
                        "The registered K0 parent may only authorize child-card banking and route validation.",
                        expected=list(state_machine.K0_PARENT_ALLOWED_ACTIONS),
                        actual=allowed_actions,
                    )
                )
            expected_ledger_prefix = state_machine.K0_PARENT_LEDGER_ENTRY_PREFIX
        else:
            if state_payload.get("implementation_authorized") is not True:
                errors.append(
                    _new_error(
                        "k0_ready_implementation_authorization_not_explicitly_true",
                        "READY_TO_IMPLEMENT must explicitly authorize only the frozen first-pair targets.",
                    )
                )
            if state_payload.get("phase") != state_machine.K0_READY_PHASE:
                errors.append(
                    _new_error(
                        "k0_ready_phase_mismatch",
                        "The READY_TO_IMPLEMENT boundary must use the frozen first-pair phase.",
                        expected=state_machine.K0_READY_PHASE,
                        actual=state_payload.get("phase"),
                    )
                )
            invalid_true_authorizations = [
                key
                for key in state_machine.K0_READY_REQUIRED_TRUE_AUTHORIZATIONS
                if not isinstance(authorizations, dict) or authorizations.get(key) is not True
            ]
            invalid_false_authorizations = [
                key
                for key in state_machine.K0_READY_REQUIRED_FALSE_AUTHORIZATIONS
                if not isinstance(authorizations, dict) or authorizations.get(key) is not False
            ]
            expected_authorization_keys = set(state_machine.K0_PARENT_REQUIRED_FALSE_AUTHORIZATIONS)
            actual_authorization_keys = set(authorizations) if isinstance(authorizations, dict) else set()
            if (
                invalid_true_authorizations
                or invalid_false_authorizations
                or actual_authorization_keys != expected_authorization_keys
            ):
                errors.append(
                    _new_error(
                        "k0_ready_authorizations_mismatch",
                        "READY_TO_IMPLEMENT may authorize Foundation and H0 only; every other authorization must remain explicit false.",
                        invalid_true=invalid_true_authorizations,
                        invalid_false=invalid_false_authorizations,
                        unexpected_or_missing_keys=sorted(actual_authorization_keys ^ expected_authorization_keys),
                    )
                )
            if allowed_actions != list(state_machine.K0_READY_ALLOWED_ACTIONS):
                errors.append(
                    _new_error(
                        "k0_ready_allowed_actions_mismatch",
                        "The READY_TO_IMPLEMENT boundary must expose only the frozen first-pair actions and validation.",
                        expected=list(state_machine.K0_READY_ALLOWED_ACTIONS),
                        actual=allowed_actions,
                    )
                )
            if state_payload.get("authorized_implementation_targets") != list(
                state_machine.K0_READY_AUTHORIZED_IMPLEMENTATION_TARGETS
            ):
                errors.append(
                    _new_error(
                        "k0_ready_implementation_targets_mismatch",
                        "The READY_TO_IMPLEMENT boundary must name exactly Foundation and H0 in frozen order.",
                        expected=list(state_machine.K0_READY_AUTHORIZED_IMPLEMENTATION_TARGETS),
                        actual=state_payload.get("authorized_implementation_targets"),
                    )
                )
            if state_payload.get("child_authorizations") != state_machine.K0_READY_CHILD_AUTHORIZATIONS:
                errors.append(
                    _new_error(
                        "k0_ready_child_authorizations_mismatch",
                        "The child authorization map must contain exactly two true and four false frozen child entries.",
                        expected=state_machine.K0_READY_CHILD_AUTHORIZATIONS,
                        actual=state_payload.get("child_authorizations"),
                    )
                )
            if not isinstance(source_readback, dict) or source_readback.get(
                "child_card_banks"
            ) != state_machine.K0_READY_CHILD_CARD_BANKS:
                errors.append(
                    _new_error(
                        "k0_ready_child_card_commit_pins_mismatch",
                        "The first-pair transition must pin the three frozen child-bank commits.",
                        expected=state_machine.K0_READY_CHILD_CARD_BANKS,
                        actual=source_readback.get("child_card_banks") if isinstance(source_readback, dict) else None,
                    )
                )
            if not isinstance(source_readback, dict) or source_readback.get("banked_card_objects") != list(
                state_machine.K0_READY_BANKED_CARD_OBJECTS
            ):
                errors.append(
                    _new_error(
                        "k0_ready_banked_card_object_readback_mismatch",
                        "The first-pair transition must carry the exact six-card commit/path/blob readback.",
                        expected=list(state_machine.K0_READY_BANKED_CARD_OBJECTS),
                        actual=source_readback.get("banked_card_objects") if isinstance(source_readback, dict) else None,
                    )
                )
            if not isinstance(source_readback, dict) or source_readback.get(
                "transition_card"
            ) != state_machine.K0_READY_TRANSITION_CARD_PATH:
                errors.append(
                    _new_error(
                        "k0_ready_transition_card_mismatch",
                        "The READY_TO_IMPLEMENT boundary must cite its separate bounded transition card.",
                        expected=state_machine.K0_READY_TRANSITION_CARD_PATH,
                        actual=source_readback.get("transition_card") if isinstance(source_readback, dict) else None,
                    )
                )
            expected_ledger_prefix = state_machine.K0_READY_LEDGER_ENTRY_PREFIX

        if not isinstance(ledger_readback, dict):
            errors.append(
                _new_error(
                    "k0_parent_ledger_declaration_missing",
                    "The K0 parent must declare its exact append-only ledger dependency.",
                )
            )
        else:
            if ledger_readback.get("path") != state_machine.K0_PARENT_LEDGER_PATH:
                errors.append(
                    _new_error(
                        "k0_parent_ledger_path_mismatch",
                        "The K0 parent ledger path must equal the frozen repo-relative path.",
                        expected=state_machine.K0_PARENT_LEDGER_PATH,
                        actual=ledger_readback.get("path"),
                    )
                )
            if ledger_readback.get("required_entry_prefix") != expected_ledger_prefix:
                errors.append(
                    _new_error(
                        "k0_parent_ledger_prefix_mismatch",
                        "The K0 parent ledger prefix must match its current frozen transition text.",
                        expected=expected_ledger_prefix,
                        actual=ledger_readback.get("required_entry_prefix"),
                    )
                )
            if current_state == "READY_TO_IMPLEMENT" and ledger_readback.get(
                "preserved_entry_prefixes"
            ) != [state_machine.K0_PARENT_LEDGER_ENTRY_PREFIX]:
                errors.append(
                    _new_error(
                        "k0_ready_preserved_ledger_prefix_mismatch",
                        "The READY_TO_IMPLEMENT ledger declaration must preserve the parent registration entry.",
                        expected=[state_machine.K0_PARENT_LEDGER_ENTRY_PREFIX],
                        actual=ledger_readback.get("preserved_entry_prefixes"),
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


def _parse_program_state_file(path: Path, errors: list[dict[str, Any]]) -> dict[str, Any] | None:
    if not path.exists():
        errors.append(_new_error("missing_program_state_json", "Program state is missing.", path=_posix(path)))
        return None
    try:
        payload = load_json(path)
    except json.JSONDecodeError as exc:
        errors.append(
            _new_error(
                "invalid_program_state_json",
                "program_state.json could not be parsed.",
                path=_posix(path),
                error=str(exc),
            )
        )
        return None
    if not isinstance(payload, dict):
        errors.append(
            _new_error("program_state_not_object", "program_state.json must contain an object.", path=_posix(path))
        )
        return None
    return payload


def validate_program_state(*, artifact_dir: Path, routes_dir: Path) -> dict[str, Any]:
    errors: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []
    program_state_path = artifact_dir / state_machine.PROGRAM_STATE_FILENAME
    program_state_payload = _parse_program_state_file(program_state_path, errors)
    if program_state_payload is None:
        return {
            "producer_function": "validate_program_state",
            "input_artifacts": [],
            "current_frontier_route_id": None,
            "validation_errors": errors,
            "validation_warnings": warnings,
            "verdict": "fail",
        }

    current_frontier_route_id = program_state_payload.get("current_frontier_route_id")
    if not isinstance(current_frontier_route_id, str) or not current_frontier_route_id.strip():
        errors.append(
            _new_error(
                "missing_current_frontier_route_id",
                "program_state.json must include current_frontier_route_id.",
            )
        )
        current_frontier_route_id = None
    else:
        current_frontier_route_id = current_frontier_route_id.strip()

    if not _non_empty_string_list(program_state_payload.get("allowed_next_actions")):
        errors.append(
            _new_error(
                "program_state_missing_allowed_next_actions",
                "program_state.json must include non-empty allowed_next_actions.",
            )
        )

    if not _non_empty_string_list(program_state_payload.get("forbidden_next_actions")):
        errors.append(
            _new_error(
                "program_state_missing_forbidden_next_actions",
                "program_state.json must include non-empty forbidden_next_actions.",
            )
        )

    if not _claim_ceiling_has_max(program_state_payload.get("claim_ceiling")):
        errors.append(
            _new_error(
                "program_state_missing_claim_ceiling_max",
                "program_state.json must include claim_ceiling.max.",
            )
        )

    input_artifacts = [_relative_posix(program_state_path, artifact_dir.parent.parent)]

    if current_frontier_route_id:
        current_frontier_route_dir = routes_dir / current_frontier_route_id
        if not current_frontier_route_dir.exists():
            errors.append(
                _new_error(
                    "missing_current_frontier_route_directory",
                    "current_frontier_route_id must point to an existing route directory.",
                    current_frontier_route_id=current_frontier_route_id,
                    path=_posix(current_frontier_route_dir),
                )
            )
        else:
            route_state_errors: list[dict[str, Any]] = []
            route_state_payload = _parse_json_file(current_frontier_route_dir / "state.json", route_state_errors)
            errors.extend(route_state_errors)
            if route_state_payload is not None:
                input_artifacts.append(
                    _relative_posix(current_frontier_route_dir / "state.json", artifact_dir.parent.parent)
                )
                route_current_state = route_state_payload.get("current_state")
                source_readback = route_state_payload.get("source_readback")
                ledger_readback = source_readback.get("ledger") if isinstance(source_readback, dict) else None
                if current_frontier_route_id == state_machine.K0_PARENT_ROUTE_ID and not isinstance(
                    ledger_readback, dict
                ):
                    errors.append(
                        _new_error(
                            "current_frontier_ledger_declaration_missing",
                            "The K0 parent current frontier must declare its exact append-only ledger dependency.",
                            current_frontier_route_id=current_frontier_route_id,
                        )
                    )
                if isinstance(ledger_readback, dict):
                    ledger_relative_path = ledger_readback.get("path")
                    required_entry_prefix = ledger_readback.get("required_entry_prefix")
                    expected_k0_ledger_prefix = (
                        state_machine.K0_READY_LEDGER_ENTRY_PREFIX
                        if route_current_state == "READY_TO_IMPLEMENT"
                        else state_machine.K0_PARENT_LEDGER_ENTRY_PREFIX
                    )
                    if not isinstance(ledger_relative_path, str) or not ledger_relative_path.strip():
                        errors.append(
                            _new_error(
                                "current_frontier_ledger_path_missing",
                                "Declared current-frontier ledger readback must include a repo-relative path.",
                                current_frontier_route_id=current_frontier_route_id,
                            )
                        )
                    elif not isinstance(required_entry_prefix, str) or not required_entry_prefix.strip():
                        errors.append(
                            _new_error(
                                "current_frontier_ledger_entry_prefix_missing",
                                "Declared current-frontier ledger readback must include required_entry_prefix.",
                                current_frontier_route_id=current_frontier_route_id,
                            )
                        )
                    elif (
                        current_frontier_route_id == state_machine.K0_PARENT_ROUTE_ID
                        and (
                            ledger_relative_path != state_machine.K0_PARENT_LEDGER_PATH
                            or required_entry_prefix != expected_k0_ledger_prefix
                        )
                    ):
                        errors.append(
                            _new_error(
                                "current_frontier_k0_ledger_contract_mismatch",
                                "The K0 parent ledger declaration must match the frozen path and task-specific prefix.",
                                current_frontier_route_id=current_frontier_route_id,
                                expected_path=state_machine.K0_PARENT_LEDGER_PATH,
                                actual_path=ledger_relative_path,
                                expected_entry_prefix=expected_k0_ledger_prefix,
                                actual_entry_prefix=required_entry_prefix,
                            )
                        )
                    else:
                        repo_root = artifact_dir.parent.parent.resolve()
                        ledger_path = (repo_root / ledger_relative_path).resolve()
                        try:
                            ledger_path.relative_to(repo_root)
                        except ValueError:
                            errors.append(
                                _new_error(
                                    "current_frontier_ledger_path_outside_repo",
                                    "Declared ledger path must stay inside the repository.",
                                    current_frontier_route_id=current_frontier_route_id,
                                    path=_posix(ledger_path),
                                )
                            )
                        else:
                            input_artifacts.append(_relative_posix(ledger_path, repo_root))
                            if not ledger_path.is_file():
                                errors.append(
                                    _new_error(
                                        "current_frontier_ledger_missing",
                                        "Declared current-frontier ledger file is missing.",
                                        current_frontier_route_id=current_frontier_route_id,
                                        path=_posix(ledger_path),
                                    )
                                )
                            else:
                                ledger_lines = ledger_path.read_text(encoding="utf-8").splitlines()
                                matching_lines = [
                                    line for line in ledger_lines if line.startswith(required_entry_prefix)
                                ]
                                if not matching_lines:
                                    errors.append(
                                        _new_error(
                                            "current_frontier_ledger_entry_missing",
                                            "Declared current-frontier ledger entry prefix was not found.",
                                            current_frontier_route_id=current_frontier_route_id,
                                            required_entry_prefix=required_entry_prefix,
                                            path=_posix(ledger_path),
                                        )
                                    )
                                elif (
                                    current_frontier_route_id == state_machine.K0_PARENT_ROUTE_ID
                                    and len(matching_lines) != 1
                                ):
                                    errors.append(
                                        _new_error(
                                            "current_frontier_k0_ledger_entry_not_unique",
                                            "The frozen K0 parent ledger entry must occur exactly once.",
                                            current_frontier_route_id=current_frontier_route_id,
                                            required_entry_prefix=required_entry_prefix,
                                            match_count=len(matching_lines),
                                            path=_posix(ledger_path),
                                        )
                                    )
                                if (
                                    current_frontier_route_id == state_machine.K0_PARENT_ROUTE_ID
                                    and route_current_state == "READY_TO_IMPLEMENT"
                                ):
                                    preserved_prefixes = ledger_readback.get("preserved_entry_prefixes")
                                    expected_preserved_prefixes = [state_machine.K0_PARENT_LEDGER_ENTRY_PREFIX]
                                    if preserved_prefixes != expected_preserved_prefixes:
                                        errors.append(
                                            _new_error(
                                                "current_frontier_k0_preserved_ledger_contract_mismatch",
                                                "The READY_TO_IMPLEMENT frontier must preserve the parent registration ledger prefix.",
                                                expected=expected_preserved_prefixes,
                                                actual=preserved_prefixes,
                                            )
                                        )
                                    else:
                                        for preserved_prefix in preserved_prefixes:
                                            preserved_matches = [
                                                line for line in ledger_lines if line.startswith(preserved_prefix)
                                            ]
                                            if len(preserved_matches) != 1:
                                                errors.append(
                                                    _new_error(
                                                        "current_frontier_k0_preserved_ledger_entry_not_unique",
                                                        "Each preserved K0 ledger prefix must occur exactly once.",
                                                        required_entry_prefix=preserved_prefix,
                                                        match_count=len(preserved_matches),
                                                        path=_posix(ledger_path),
                                                    )
                                                )
                current_state = route_current_state
                if current_state == "TOMBSTONED":
                    errors.append(
                        _new_error(
                            "current_frontier_route_tombstoned",
                            "current_frontier_route_id cannot point to a TOMBSTONED route.",
                            current_frontier_route_id=current_frontier_route_id,
                        )
                    )

                if current_state in ("REGISTERED", "READY_TO_IMPLEMENT"):
                    forbidden_authorizations = _forbidden_current_frontier_authorizations(
                        program_state_payload=program_state_payload,
                        route_state_payload=route_state_payload,
                    )
                    if forbidden_authorizations:
                        errors.append(
                            _new_error(
                                "registered_current_frontier_authorizes_forbidden_capability",
                                "REGISTERED current frontier cannot authorize mechanism validity, theory pressure, scoring, or experiment execution.",
                                current_frontier_route_id=current_frontier_route_id,
                                forbidden_authorizations=forbidden_authorizations,
                            )
                        )

                if (
                    current_frontier_route_id == state_machine.CURRENT_FRONTIER_ROUTE_ID
                    and not _source_readback_has_l014_or_equivalent(route_state_payload.get("source_readback"))
                ):
                    errors.append(
                        _new_error(
                            "n2_frontier_missing_l014_source_readback",
                            "N2-SBMC-ENV-REDESIGN-001A must cite L-014 or equivalent current ledger evidence in source_readback.",
                            current_frontier_route_id=current_frontier_route_id,
                        )
                    )

    return {
        "producer_function": "validate_program_state",
        "input_artifacts": sorted(set(input_artifacts)),
        "current_frontier_route_id": current_frontier_route_id,
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
    artifact_dir = root / state_machine.TASK_ARTIFACT_DIR
    program_state = validate_program_state(artifact_dir=artifact_dir, routes_dir=routes_dir)
    input_artifacts = [
        f"{state_machine.TASK_ARTIFACT_DIR}/routes/{artifact}"
        for artifact in route_tree["input_artifacts"]
    ]
    input_artifacts.extend(program_state["input_artifacts"])
    schema_dir = root / state_machine.TASK_ARTIFACT_DIR / "schemas"
    for schema in sorted(schema_dir.glob("*.schema.json")) if schema_dir.exists() else []:
        input_artifacts.append(_relative_posix(schema, root))

    validation_errors = route_tree["validation_errors"] + program_state["validation_errors"]
    validation_warnings = route_tree["validation_warnings"] + program_state["validation_warnings"]

    return {
        "task_id": state_machine.TASK_ID,
        "producer_function": "build_validation_report",
        "input_artifacts": sorted(set(input_artifacts)),
        "run_id": f"{state_machine.TASK_ID.lower()}-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}-{uuid.uuid4().hex[:8]}",
        "aggregation_rule": "verdict is pass iff validate_routes_tree and validate_program_state return zero validation_errors",
        "code_path_hash": code_path_hash(),
        "validation_errors": validation_errors,
        "validation_warnings": validation_warnings,
        "current_frontier_route_id": program_state["current_frontier_route_id"],
        "program_state_verdict": program_state["verdict"],
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
        "verdict": "pass" if not validation_errors else "fail",
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
        "current_frontier_route_id": report["current_frontier_route_id"],
        "program_state_verdict": report["program_state_verdict"],
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
        "current_frontier_route_id": report["current_frontier_route_id"],
        "program_state_verdict": report["program_state_verdict"],
        "routes": report["routes"],
        "validation_error_codes": sorted({error["code"] for error in report["validation_errors"]}),
        "validation_warning_codes": sorted({warning["code"] for warning in report["validation_warnings"]}),
        "transition_command_status": "deferred_in_001a_first_local_version",
        "claim_ceiling": report["claim_ceiling"],
    }
