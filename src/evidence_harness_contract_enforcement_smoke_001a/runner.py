from __future__ import annotations

import hashlib
import inspect
import json
import subprocess
from pathlib import Path
from typing import Any


TASK_ID = "EVIDENCE-HARNESS-CONTRACT-ENFORCEMENT-SMOKE-001A"
TASK_SLUG = "evidence_harness_contract_enforcement_smoke_001a"
CLAIM_CEILING = "bounded evidence-harness contract enforcement smoke only"
STARTING_HEAD = "b11424652c791fd9153322db77d959c3c0cdacac"
BRANCH = "codex/meta-theory-scaffold"
CONTRACT_ANCHOR_COMMIT = STARTING_HEAD
LAYER = "engineering implementation layer: executable evidence-harness enforcement smoke"

ADMISSIBILITY_CLASSES = [
    "admissible_downstream_evidence",
    "admissible_negative_evidence_only",
    "reference_only",
    "blocked_pending_audit",
    "rejected_false_pass_risk",
    "governance_anchor_only",
]

REQUIRED_ARTIFACTS = [
    "contract_input_inventory.json",
    "known_false_pass_input_inventory.json",
    "synthetic_positive_control_fixtures.json",
    "enforcement_rule_manifest.json",
    "gate4_001b_enforcement_report.json",
    "positive_control_enforcement_report.json",
    "negative_control_or_scope_control_report.json",
    "rejection_reason_matrix.json",
    "result.json",
    "claim_ceiling.txt",
    "execution_manifest.json",
    "json_parse_verification.json",
]

AUTHORIZATION_FALSE = {
    "downstream_entry_authorized": False,
    "gate4_001c_authorized": False,
    "gate5_authorized": False,
    "admission_authorized": False,
    "runtime_authorized": False,
    "bridge_authorized": False,
}

RULES = [
    {
        "rule_id": "detect_pass_shaped_result_fields",
        "category": "pass_shaped_result_fields",
        "description": "Detect literal pass verdicts, bounded_pass=true, *_gate_passed=true, or verified=true fields.",
    },
    {
        "rule_id": "detect_static_score_or_perfect_score_literal",
        "category": "static_score_or_perfect_score_literal",
        "description": "Detect perfect score literals or score assertions that can make a pass structurally easy.",
    },
    {
        "rule_id": "detect_unconditional_verified_or_real_intervention_true",
        "category": "unconditional_verified_or_real_intervention_true",
        "description": "Detect verified=true or real_intervention=true fields when used as report literals.",
    },
    {
        "rule_id": "detect_ablation_sentinel_or_label_special_case",
        "category": "ablation_sentinel_or_label_special_case",
        "description": "Detect variant-name or ablation-name branch patterns and label-driven ablation report surfaces.",
    },
    {
        "rule_id": "detect_hash_or_stored_value_replay_shortcut",
        "category": "hash_or_stored_value_replay_shortcut",
        "description": "Detect replay reports or tests that can pass by stored actions, stored verdicts, or hash-only checks.",
    },
    {
        "rule_id": "detect_leakage_scan_gap_or_broad_whitelist",
        "category": "leakage_scan_gap_or_broad_whitelist",
        "description": "Detect leakage reports with clean literal pass surfaces, broad whitelists, or missing positive-control coverage.",
    },
    {
        "rule_id": "detect_output_shape_only_test_assertion",
        "category": "output_shape_only_test_assertion",
        "description": "Detect tests asserting pass strings, perfect scores, artifact existence, or positive degradation.",
    },
]


def _git_output(root: Path, args: list[str]) -> str:
    completed = subprocess.run(
        ["git", *args],
        cwd=root,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    return completed.stdout.strip() if completed.returncode == 0 else ""


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _source_hash() -> str:
    return _sha256_text(inspect.getsource(evaluate_bundle))


def _read_path_payload(repo_root: Path, rel_path: str) -> dict[str, Any]:
    path = repo_root / rel_path
    text = path.read_text(encoding="utf-8")
    payload: Any | None = None
    kind = "text"
    if rel_path.endswith(".json"):
        kind = "json"
        payload = json.loads(text)
    elif rel_path.endswith(".jsonl"):
        kind = "jsonl"
        payload = [json.loads(line) for line in text.splitlines() if line.strip()]
    elif rel_path.endswith(".py"):
        kind = "source"
    elif rel_path.endswith(".md"):
        kind = "markdown"
    return {
        "path": rel_path,
        "kind": kind,
        "payload": payload,
        "text": text if kind != "json" else "",
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
    }


def _walk_json(value: Any, path: str = "$") -> list[tuple[str, Any]]:
    rows = [(path, value)]
    if isinstance(value, dict):
        for key, item in value.items():
            rows.extend(_walk_json(item, f"{path}.{key}"))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            rows.extend(_walk_json(item, f"{path}[{index}]"))
    return rows


def _add_reason(
    reasons: list[dict[str, Any]],
    categories: set[str],
    rule_id: str,
    category: str,
    path: str,
    detail: str,
) -> None:
    categories.add(category)
    reasons.append(
        {
            "rule_id": rule_id,
            "category": category,
            "path": path,
            "detail": detail,
        }
    )


def _scan_json(path: str, payload: Any, reasons: list[dict[str, Any]], categories: set[str]) -> None:
    rows = _walk_json(payload)
    for json_path, value in rows:
        leaf = json_path.rsplit(".", 1)[-1].lower()
        if value is True and (
            leaf in {"bounded_pass", "verified"}
            or leaf.endswith("_gate_passed")
            or leaf in {"leakage_gate_passed", "replay_gate_passed", "baseline_gate_passed", "ablation_gate_passed"}
        ):
            _add_reason(
                reasons,
                categories,
                "detect_pass_shaped_result_fields",
                "pass_shaped_result_fields",
                path,
                f"{json_path} is true",
            )
        if leaf == "verdict" and isinstance(value, str) and "pass" in value.lower() and "failed" not in value.lower():
            _add_reason(
                reasons,
                categories,
                "detect_pass_shaped_result_fields",
                "pass_shaped_result_fields",
                path,
                f"{json_path} contains pass-shaped verdict",
            )
        if not isinstance(value, bool) and isinstance(value, (int, float)) and float(value) == 1.0 and "score" in leaf:
            _add_reason(
                reasons,
                categories,
                "detect_static_score_or_perfect_score_literal",
                "static_score_or_perfect_score_literal",
                path,
                f"{json_path} is perfect score literal 1.0",
            )
        if value is True and leaf in {"verified", "real_intervention"}:
            _add_reason(
                reasons,
                categories,
                "detect_unconditional_verified_or_real_intervention_true",
                "unconditional_verified_or_real_intervention_true",
                path,
                f"{json_path} is {leaf}=true",
            )
        if leaf in {"ablation_name", "variant"}:
            _add_reason(
                reasons,
                categories,
                "detect_ablation_sentinel_or_label_special_case",
                "ablation_sentinel_or_label_special_case",
                path,
                f"{json_path} exposes label-driven ablation or variant field",
            )
        if leaf in {"stored_actions_reused", "stored_verdicts_reused", "hash_only_replay"} and value is True:
            _add_reason(
                reasons,
                categories,
                "detect_hash_or_stored_value_replay_shortcut",
                "hash_or_stored_value_replay_shortcut",
                path,
                f"{json_path} indicates replay shortcut",
            )
        if leaf in {"broad_whitelist", "result_json_excluded", "positive_control_case_present"}:
            if leaf in {"broad_whitelist", "result_json_excluded"} and value is True:
                _add_reason(
                    reasons,
                    categories,
                    "detect_leakage_scan_gap_or_broad_whitelist",
                    "leakage_scan_gap_or_broad_whitelist",
                    path,
                    f"{json_path} indicates leakage scan gap",
                )
            if leaf == "positive_control_case_present" and value is False:
                _add_reason(
                    reasons,
                    categories,
                    "detect_leakage_scan_gap_or_broad_whitelist",
                    "leakage_scan_gap_or_broad_whitelist",
                    path,
                    f"{json_path} is false",
                )


def _scan_text(path: str, text: str, reasons: list[dict[str, Any]], categories: set[str]) -> None:
    lowered = text.lower()
    if "if variant ==" in lowered or "if variant in" in lowered or "if ablation" in lowered:
        _add_reason(
            reasons,
            categories,
            "detect_ablation_sentinel_or_label_special_case",
            "ablation_sentinel_or_label_special_case",
            path,
            "source contains variant or ablation sentinel branch",
        )
    test_patterns = [
        'assert result["verdict"]',
        "bounded_pass",
        "pytest.approx(1.0)",
        "assert metric",
        "assert report",
        "degradation",
        "exists()",
    ]
    if (path.startswith("tests/") or "/tests/" in path) and any(pattern in text for pattern in test_patterns):
        _add_reason(
            reasons,
            categories,
            "detect_output_shape_only_test_assertion",
            "output_shape_only_test_assertion",
            path,
            "test surface asserts pass-shaped outputs, perfect scores, degradation, or existence",
        )
    if "stored_action" in lowered or "stored verdict" in lowered or "hash-only replay" in lowered:
        _add_reason(
            reasons,
            categories,
            "detect_hash_or_stored_value_replay_shortcut",
            "hash_or_stored_value_replay_shortcut",
            path,
            "text mentions stored action/verdict or hash-only replay shortcut",
        )


def evaluate_bundle(bundle: dict[str, Any]) -> dict[str, Any]:
    """Evaluate an evidence bundle by detected features, not task-id denylist."""

    reasons: list[dict[str, Any]] = []
    categories: set[str] = set()
    inspected_paths: list[str] = []

    for item in bundle.get("path_payloads", []):
        path = item["path"]
        inspected_paths.append(path)
        if "/" in path:
            root = path.split("/", 1)[0]
            if root not in inspected_paths:
                inspected_paths.append(root)
        payload = item.get("payload")
        text = item.get("text", "")
        if payload is not None:
            _scan_json(path, payload, reasons, categories)
        if text:
            _scan_text(path, text, reasons, categories)

    positive_controls_detected = bool(bundle.get("positive_control_expected")) and bool(categories)
    static_denylist_only = False

    if categories:
        admissibility_class = "rejected_false_pass_risk"
    elif bundle.get("governance_anchor_only"):
        admissibility_class = "governance_anchor_only"
    else:
        admissibility_class = "blocked_pending_audit"

    return {
        "bundle_id": bundle.get("bundle_id", "unknown"),
        "task_id": bundle.get("task_id"),
        "admissibility_class": admissibility_class,
        "rejection_reasons": reasons,
        "detected_pattern_categories": sorted(categories),
        "inspected_paths": inspected_paths,
        "producer_function": "evaluate_bundle",
        "producer_source_path": "src/evidence_harness_contract_enforcement_smoke_001a/runner.py",
        "source_code_hash": _source_hash(),
        "rule_ids_invoked": [rule["rule_id"] for rule in RULES],
        "positive_controls_detected": positive_controls_detected,
        "static_denylist_only": static_denylist_only,
        "decision_basis": "detected_evidence_pattern_features" if categories else "scope_or_visibility_classification",
    }


def build_contract_input_inventory(repo_root: Path) -> dict[str, Any]:
    paths = [
        "docs/evidence_harness/EVIDENCE-HARNESS-CANONICAL-CONTRACT-001A.md",
        "docs/codex/tasks/EVIDENCE-HARNESS-CANONICAL-CONTRACT-001A.md",
        "artifacts/evidence_harness_canonical_contract_001a/contract_schema.json",
        "artifacts/evidence_harness_canonical_contract_001a/false_pass_rejection_rules.json",
        "artifacts/evidence_harness_canonical_contract_001a/downstream_admissibility_matrix.json",
        "artifacts/evidence_harness_canonical_contract_001a/result.json",
        "artifacts/evidence_harness_canonical_contract_001a/claim_ceiling.txt",
    ]
    records = []
    for rel in paths:
        path = repo_root / rel
        records.append(
            {
                "path": rel,
                "exists": path.exists(),
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else None,
            }
        )
    return {
        "task_id": TASK_ID,
        "contract_anchor_commit": CONTRACT_ANCHOR_COMMIT,
        "claim_ceiling": CLAIM_CEILING,
        "input_records": records,
    }


def build_gate4_001b_inventory(repo_root: Path) -> dict[str, Any]:
    paths = [
        "artifacts/ego_mainline_gate4_preflight_executable_001b/result.json",
        "artifacts/ego_mainline_gate4_preflight_executable_001b/candidate_metric_report.json",
        "artifacts/ego_mainline_gate4_preflight_executable_001b/baseline_invocation_report.json",
        "artifacts/ego_mainline_gate4_preflight_executable_001b/ablation_report.json",
        "artifacts/ego_mainline_gate4_preflight_executable_001b/leakage_scan_report.json",
        "artifacts/ego_mainline_gate4_preflight_executable_001b/replay_recomputation_report.json",
        "artifacts/ego_mainline_gate4_preflight_executable_001b/run_ledger.jsonl",
        "src/ego_mainline_gate4_preflight_executable_001b/runner.py",
        "tests/test_ego_mainline_gate4_preflight_executable_001b.py",
        "docs/codex/tasks/EGO-MAINLINE-GATE4-PREFLIGHT-EXECUTABLE-001B.md",
    ]
    path_payloads = [_read_path_payload(repo_root, rel) for rel in paths if (repo_root / rel).exists()]
    return {
        "bundle_id": "known_gate4_001b_false_pass_boundary",
        "task_id": "EGO-MAINLINE-GATE4-PREFLIGHT-EXECUTABLE-001B",
        "known_boundary": {
            "commit": "90dc4b9082593fabf06197b03eaf66c9c64014a2",
            "tag": "remote-anchor-gate4-preflight-executable-001b-90dc4b9",
            "status": "sealed_but_independently_rejected_not_admissible_as_gate4_pass_evidence",
        },
        "path_payloads": path_payloads,
    }


def build_synthetic_positive_control_bundle() -> dict[str, Any]:
    return {
        "bundle_id": "synthetic_positive_control_false_pass_fixture",
        "task_id": "SYNTHETIC-FALSE-PASS-POSITIVE-CONTROL",
        "positive_control_expected": True,
        "path_payloads": [
            {
                "path": "synthetic_false_pass_fixture/result.json",
                "kind": "json",
                "payload": {
                    "task_id": "SYNTHETIC-FALSE-PASS-POSITIVE-CONTROL",
                    "verdict": "synthetic_bounded_pass",
                    "bounded_pass": True,
                    "verified": True,
                    "candidate_score": 1.0,
                },
            },
            {
                "path": "synthetic_false_pass_fixture/ablation_report.json",
                "kind": "json",
                "payload": {
                    "ablation_gate_passed": True,
                    "ablations": [
                        {
                            "ablation_name": "remove latent state",
                            "candidate_score": 1.0,
                            "score": 0.0,
                            "degradation": 1.0,
                            "real_intervention": True,
                            "clipped_degradation": True,
                        }
                    ],
                },
            },
            {
                "path": "synthetic_false_pass_fixture/replay_report.json",
                "kind": "json",
                "payload": {
                    "replay_gate_passed": True,
                    "stored_actions_reused": True,
                    "stored_verdicts_reused": True,
                },
            },
            {
                "path": "synthetic_false_pass_fixture/leakage_report.json",
                "kind": "json",
                "payload": {
                    "leakage_gate_passed": True,
                    "broad_whitelist": True,
                    "result_json_excluded": True,
                    "positive_control_case_present": False,
                },
            },
            {
                "path": "synthetic_false_pass_fixture/tests/test_false_pass.py",
                "kind": "text",
                "text": 'assert result["verdict"] == "synthetic_bounded_pass"\nassert result["candidate_score"] == pytest.approx(1.0)\n',
                "payload": None,
            },
        ],
    }


def build_governance_anchor_scope_control_bundle() -> dict[str, Any]:
    return {
        "bundle_id": "governance_anchor_scope_control",
        "task_id": "SYNTHETIC-GOVERNANCE-ANCHOR-ONLY",
        "governance_anchor_only": True,
        "path_payloads": [
            {
                "path": "scope_control/anchor_record.json",
                "kind": "json",
                "payload": {
                    "task_id": "SYNTHETIC-GOVERNANCE-ANCHOR-ONLY",
                    "anchor_commit": "abc123",
                    "tag": "remote-anchor-scope-control-abc123",
                    "claim_ceiling": "governance anchor only",
                    "downstream_entry_authorized": False,
                },
            }
        ],
    }


def _write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, sort_keys=True, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def _json_parse_verification(output_dir: Path) -> dict[str, Any]:
    parsed = []
    for path in sorted(output_dir.glob("*.json")):
        json.loads(path.read_text(encoding="utf-8"))
        parsed.append(path.name)
    return {
        "task_id": TASK_ID,
        "claim_ceiling": CLAIM_CEILING,
        "parse_status": "all_required_json_parsed",
        "parser": "json.loads",
        "parsed_files": parsed,
        "non_evidence_statement": "JSON parsing verifies syntax only; it does not prove Gate validity or mechanism validity.",
    }


def run_smoke(repo_root: Path, output_dir: Path | None = None) -> dict[str, Any]:
    repo_root = Path(repo_root)
    out = output_dir or repo_root / "artifacts" / TASK_SLUG
    out.mkdir(parents=True, exist_ok=True)

    branch = _git_output(repo_root, ["branch", "--show-current"])
    head = _git_output(repo_root, ["rev-parse", "HEAD"])
    status = _git_output(repo_root, ["status", "--short", "--branch"])

    contract_inventory = build_contract_input_inventory(repo_root)
    gate4_bundle = build_gate4_001b_inventory(repo_root)
    positive_bundle = build_synthetic_positive_control_bundle()
    scope_bundle = build_governance_anchor_scope_control_bundle()

    gate4_report = evaluate_bundle(gate4_bundle)
    positive_report = evaluate_bundle(positive_bundle)
    scope_report = evaluate_bundle(scope_bundle)

    result = {
        "verdict": "bounded_enforcement_smoke_rejects_false_pass_patterns_downstream_blocked",
        "task_id": TASK_ID,
        "layer": LAYER,
        "claim_ceiling": CLAIM_CEILING,
        "starting_head": STARTING_HEAD,
        "branch": BRANCH,
        "contract_anchor_commit": CONTRACT_ANCHOR_COMMIT,
        "known_false_pass_boundary": gate4_bundle["known_boundary"],
        "gate4_001b_admissibility_class": gate4_report["admissibility_class"],
        "gate4_001b_rejection_reasons": gate4_report["rejection_reasons"],
        "positive_control_detected": positive_report["positive_controls_detected"],
        "static_denylist_only": gate4_report["static_denylist_only"] or positive_report["static_denylist_only"],
        "negative_or_scope_control_class": scope_report["admissibility_class"],
        **AUTHORIZATION_FALSE,
        "json_parse_verification": {
            "artifact": f"artifacts/{TASK_SLUG}/json_parse_verification.json",
            "status": "all_required_json_parsed",
        },
        "what_this_does_not_prove": [
            "Gate validity",
            "mechanism validity",
            "theory validity",
            "architecture correctness",
            "Gate4 001C authorization",
            "Gate5 authorization",
            "admission authorization",
            "runtime authorization",
            "bridge authorization",
            "EGO mainline readiness",
            "agency, selfhood, consciousness, emotion, relationship learning, or stable user benefit",
        ],
    }

    execution_manifest = {
        "task_id": TASK_ID,
        "mode": "minimal executable evidence-harness contract enforcement smoke only",
        "claim_ceiling": CLAIM_CEILING,
        "branch": branch,
        "head": head,
        "expected_starting_head": STARTING_HEAD,
        "status_at_execution": status,
        "producer_function": "run_smoke",
        "producer_source_path": "src/evidence_harness_contract_enforcement_smoke_001a/runner.py",
        "source_code_hash": _source_hash(),
        "old_artifacts_modified": False,
        "provisional_gate4_001c_used": False,
        "forbidden_scope_not_entered": [
            "Gate repair",
            "Gate execution",
            "Gate4 001C continuation",
            "Gate5",
            "admission",
            "runtime",
            "bridge",
        ],
    }

    rule_manifest = {
        "task_id": TASK_ID,
        "claim_ceiling": CLAIM_CEILING,
        "admissibility_classes": ADMISSIBILITY_CLASSES,
        "rules": RULES,
        "static_task_id_denylist_used": False,
        "decision_rule": "Reject only when detected evidence-pattern categories are present; task id alone can at most remain blocked pending audit.",
    }

    reason_matrix = {
        "task_id": TASK_ID,
        "claim_ceiling": CLAIM_CEILING,
        "bundles": {
            gate4_report["bundle_id"]: {
                "admissibility_class": gate4_report["admissibility_class"],
                "detected_pattern_categories": gate4_report["detected_pattern_categories"],
                "rejection_reasons": gate4_report["rejection_reasons"],
            },
            positive_report["bundle_id"]: {
                "admissibility_class": positive_report["admissibility_class"],
                "detected_pattern_categories": positive_report["detected_pattern_categories"],
                "rejection_reasons": positive_report["rejection_reasons"],
            },
            scope_report["bundle_id"]: {
                "admissibility_class": scope_report["admissibility_class"],
                "detected_pattern_categories": scope_report["detected_pattern_categories"],
                "rejection_reasons": scope_report["rejection_reasons"],
            },
        },
    }

    _write_json(out / "contract_input_inventory.json", contract_inventory)
    _write_json(
        out / "known_false_pass_input_inventory.json",
        {
            "task_id": TASK_ID,
            "claim_ceiling": CLAIM_CEILING,
            "known_boundary": gate4_bundle["known_boundary"],
            "inspected_paths": [item["path"] for item in gate4_bundle["path_payloads"]],
        },
    )
    _write_json(out / "synthetic_positive_control_fixtures.json", positive_bundle)
    _write_json(out / "enforcement_rule_manifest.json", rule_manifest)
    _write_json(out / "gate4_001b_enforcement_report.json", gate4_report)
    _write_json(out / "positive_control_enforcement_report.json", positive_report)
    _write_json(out / "negative_control_or_scope_control_report.json", scope_report)
    _write_json(out / "rejection_reason_matrix.json", reason_matrix)
    _write_json(out / "result.json", result)
    (out / "claim_ceiling.txt").write_text(CLAIM_CEILING + "\n", encoding="utf-8")
    _write_json(out / "execution_manifest.json", execution_manifest)
    _write_json(out / "json_parse_verification.json", {"parse_status": "pending"})
    _write_json(out / "json_parse_verification.json", _json_parse_verification(out))

    return result


def main() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    run_smoke(repo_root=repo_root)


if __name__ == "__main__":
    main()
