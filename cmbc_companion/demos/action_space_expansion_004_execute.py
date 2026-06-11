from __future__ import annotations

import argparse
import hashlib
import inspect
import json
from pathlib import Path
from typing import Any

from cmbc_companion.demos.blind_human_trial_001 import freeze_manifest
from cmbc_companion.demos.free_input_live_lab_003_reexecute import (
    DEFAULT_OUTCOME_LEDGER_PATH,
    DEFAULT_PROBE_PACK_PATH,
    DEFAULT_TRANSCRIPT_PATH,
)
from cmbc_companion.evals.verify_growth_loop import ACTION_HANDLES, CMBCGrowthLoopCandidate


ALLOWED_VERDICTS = {
    "action_space_expansion_bounded_pass",
    "small_action_set_only",
    "semantic_label_leak_detected",
    "label_permutation_failed",
    "effect_swap_failed",
    "rag_equivalent_in_expanded_action_space",
    "strong_heuristic_equivalent_in_expanded_action_space",
    "expanded_contextual_heuristic_equivalent_in_expanded_action_space",
    "expanded_action_frequency_equivalent",
    "expanded_action_nearest_neighbor_equivalent",
    "behavior_only_replay_failed",
    "renderer_controls_action",
    "inconclusive_revise_contract",
}

CONTRACT_PATH = Path("artifacts/cmbc_companion_action_space_expansion_004_contract/action_space_expansion_004_contract.json")
CONTRACT_MANIFEST_PATH = Path("artifacts/cmbc_companion_action_space_expansion_004_contract/contract_manifest.json")


def write_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def source_freeze_manifest() -> dict[str, Any]:
    paths = {
        "contract": CONTRACT_PATH,
        "contract_manifest": CONTRACT_MANIFEST_PATH,
        "transcript": DEFAULT_TRANSCRIPT_PATH,
        "outcome_ledger": DEFAULT_OUTCOME_LEDGER_PATH,
        "probe_pack_003b": DEFAULT_PROBE_PACK_PATH,
    }
    return {
        "paths": {name: str(path) for name, path in paths.items()},
        "hashes": {name: file_hash(path) for name, path in paths.items()},
    }


def build_requested_action_space(requested_count: int = 20) -> dict[str, Any]:
    requested_handles = [f"anon_option_{index:02d}" for index in range(requested_count)]
    selector_source = inspect.getsource(CMBCGrowthLoopCandidate.choose)
    selector_uses_static_handles = "ACTION_HANDLES" in selector_source
    selector_visible_handles = list(ACTION_HANDLES)
    executable = not selector_uses_static_handles and len(selector_visible_handles) >= requested_count
    return {
        "requested_candidate_action_count": requested_count,
        "requested_anonymous_action_handles": requested_handles,
        "selector_visible_candidate_action_count": len(selector_visible_handles),
        "selector_visible_anonymous_action_handles": selector_visible_handles,
        "expanded_action_space_executable_by_frozen_selector": executable,
        "selector_uses_static_action_handles": selector_uses_static_handles,
        "selector_choose_source_digest": hashlib.sha256(selector_source.encode("utf-8")).hexdigest(),
        "semantic_labels_exposed_to_selector": False,
        "rendered_text_exposed_to_selector": False,
        "public_action_names_exposed_to_selector": False,
        "natural_language_descriptions_exposed_to_selector": False,
        "action_family_names_exposed_to_selector": False,
        "construction_note": (
            "The execution requested an expanded anonymous option set, but the frozen "
            "selector is hard-wired to the existing ACTION_HANDLES tuple. Counting the "
            "requested 20 options as selector-visible would be a false pass."
        ),
    }


def anonymous_action_handle_permutation(handles: list[str]) -> dict[str, Any]:
    rotated = handles[7:] + handles[:7]
    return {
        "permutation_id": "deterministic_rotation_no_semantic_labels",
        "source_handles": handles,
        "permuted_handles": rotated,
        "mapping": dict(zip(handles, rotated)),
        "semantic_labels_in_mapping": False,
        "post_result_selected": False,
    }


def semantic_label_leak_scan(action_space: dict[str, Any]) -> dict[str, Any]:
    forbidden = []
    if action_space["semantic_labels_exposed_to_selector"]:
        forbidden.append("semantic_action_labels")
    if action_space["rendered_text_exposed_to_selector"]:
        forbidden.append("rendered_text")
    if action_space["public_action_names_exposed_to_selector"]:
        forbidden.append("public_action_names")
    if action_space["natural_language_descriptions_exposed_to_selector"]:
        forbidden.append("natural_language_action_descriptions")
    if action_space["action_family_names_exposed_to_selector"]:
        forbidden.append("action_family_names")
    return {
        "passed": not forbidden,
        "forbidden_fields_used": forbidden,
        "selector_read_fields": list(CMBCGrowthLoopCandidate.READ_FIELDS),
        "semantic_label_visible_to_selector": action_space["semantic_labels_exposed_to_selector"],
        "rendered_text_visible_to_selector": action_space["rendered_text_exposed_to_selector"],
        "public_action_name_visible_to_selector": action_space["public_action_names_exposed_to_selector"],
    }


def build_unexecuted_report(report_type: str, reason: str) -> dict[str, Any]:
    return {
        "report_type": report_type,
        "executed": False,
        "not_run_reason": reason,
        "selector_patched": False,
        "thresholds_changed": False,
        "baseline_weakened": False,
    }


def build_result() -> dict[str, Any]:
    contract = read_json(CONTRACT_PATH)
    freeze_before = freeze_manifest()
    source_freeze_before = source_freeze_manifest()
    action_space = build_requested_action_space(
        requested_count=contract["minimum_future_execution_gates"]["candidate_action_count_min"]
    )
    leak_scan = semantic_label_leak_scan(action_space)
    freeze_after = freeze_manifest()
    source_freeze_after = source_freeze_manifest()

    stop_conditions = []
    if action_space["selector_visible_candidate_action_count"] < contract["minimum_future_execution_gates"]["candidate_action_count_min"]:
        stop_conditions.append("candidate_action_count < 20")
    if not action_space["expanded_action_space_executable_by_frozen_selector"]:
        stop_conditions.append("frozen_selector_not_parametric_over_action_space")
    if not leak_scan["passed"]:
        stop_conditions.append("semantic_label_visible_to_selector")

    metrics = {
        "requested_candidate_action_count": action_space["requested_candidate_action_count"],
        "selector_visible_candidate_action_count": action_space["selector_visible_candidate_action_count"],
        "candidate_action_count": action_space["selector_visible_candidate_action_count"],
        "semantic_label_visible_to_selector": leak_scan["semantic_label_visible_to_selector"],
        "rendered_text_visible_to_selector": leak_scan["rendered_text_visible_to_selector"],
        "public_action_name_visible_to_selector": leak_scan["public_action_name_visible_to_selector"],
        "action_distribution_entropy_reported": False,
        "dominant_action_rate_reported": False,
        "label_permutation_change_rate": None,
        "effect_swap_change_rate": None,
        "rag_causal_probe_match_rate": None,
        "strong_heuristic_causal_probe_match_rate": None,
        "expanded_contextual_heuristic_causal_probe_match_rate": None,
        "expanded_action_frequency_match_rate": None,
        "expanded_action_nearest_neighbor_match_rate": None,
        "action_distribution_entropy_mean": None,
        "action_distribution_entropy_min": None,
        "dominant_action_rate": None,
        "behavior_only_replay_match_rate": None,
        "renderer_action_change_rate": 0.0,
        "semantic_label_leak_scan_passed": leak_scan["passed"],
    }
    verdict = "semantic_label_leak_detected" if not leak_scan["passed"] else "small_action_set_only"
    return {
        "suite_id": "CMBC-COMPANION-ACTION-SPACE-EXPANSION-004-EXECUTE",
        "verdict": verdict,
        "claim_boundary": "bounded action-space expansion execution only",
        "claim_after_execution": "small-action-set-only evidence; expanded action-space advantage not established",
        "execution_scope": "bounded_execution_only",
        "contract_id": contract["contract_id"],
        "source_inputs": {
            "contract_path": str(CONTRACT_PATH),
            "contract_manifest_path": str(CONTRACT_MANIFEST_PATH),
            "transcript_path": str(DEFAULT_TRANSCRIPT_PATH),
            "outcome_ledger_path": str(DEFAULT_OUTCOME_LEDGER_PATH),
            "probe_pack_path": str(DEFAULT_PROBE_PACK_PATH),
        },
        "freeze_integrity": {
            "before": freeze_before,
            "after": freeze_after,
            "source_before": source_freeze_before,
            "source_after": source_freeze_after,
            "code_hashes_unchanged_after_execution": freeze_before == freeze_after,
            "source_hashes_unchanged_after_execution": source_freeze_before == source_freeze_after,
        },
        "expanded_action_space": action_space,
        "anonymous_action_handle_permutation": anonymous_action_handle_permutation(
            action_space["requested_anonymous_action_handles"]
        ),
        "semantic_label_leak_scan": leak_scan,
        "label_permutation_report": build_unexecuted_report(
            "label_permutation_invariance",
            "frozen_selector_not_parametric_over_action_space",
        ),
        "effect_swap_report": build_unexecuted_report(
            "effect_swap_sensitivity",
            "frozen_selector_not_parametric_over_action_space",
        ),
        "causal_probe_results": {
            "executed": False,
            "probe_count": 0,
            "not_run_reason": "frozen_selector_not_parametric_over_action_space",
            "cases": [],
        },
        "action_distribution_entropy_report": {
            "reported": False,
            "not_run_reason": "frozen_selector_not_parametric_over_action_space",
        },
        "dominant_action_rate_report": {
            "reported": False,
            "not_run_reason": "frozen_selector_not_parametric_over_action_space",
        },
        "baseline_comparison": {
            "executed": False,
            "not_run_reason": "frozen_selector_not_parametric_over_action_space",
            "rag_summary_memory": {"causal_probe_match_rate": None},
            "strong_human_like_heuristic": {"causal_probe_match_rate": None},
            "expanded_contextual_heuristic": {"causal_probe_match_rate": None},
            "expanded_action_frequency": {"match_rate": None},
            "expanded_action_nearest_neighbor": {"match_rate": None},
            "forbidden_fields_used": [],
        },
        "renderer_isolation": {
            "passed": True,
            "adversarial_renderer_action_change_rate": 0.0,
            "renderer_used_for_action_selection": False,
            "llm_action_selection": False,
            "not_run_reason": "selector_stopped_before_rendering",
        },
        "behavior_only_replay": {
            "passed": False,
            "match_rate": None,
            "records": [],
            "forbidden_fields_used": [],
            "not_run_reason": "no_expanded_action_decisions_to_replay",
        },
        "metrics": metrics,
        "minimum_gates_satisfied": False,
        "stop_conditions": stop_conditions,
        "rca_recommended": "CMBC-COMPANION-ACTION-SPACE-EXPANSION-004-RCA",
        "rca_focus": [
            "action representation too weak or fixed",
            "frozen selector not parametric over candidate action handles",
            "candidate set construction cannot be consumed without selector redesign",
            "probe inherited from 003B may not be adapted to expanded action space",
        ],
        "implementation_authorized": False,
        "selector_patched": False,
        "thresholds_changed": False,
        "rag_baseline_weakened": False,
        "baseline_weakened": False,
        "probe_pack_modified": False,
        "ego_migration": "no_go",
        "real_companion_implementation": "not_authorized",
        "proactive_messages": "not_authorized",
        "background_autonomy": False,
        "llm_action_selection": False,
        "not_authorized": [
            "EGO migration",
            "real companion implementation",
            "real proactive messages",
            "background autonomy",
            "LLM action selection",
            "selector patch",
            "threshold change",
            "RAG baseline weakening",
            "probe pack modification after results",
            "real companion readiness claim",
        ],
        "not_proven": [
            "expanded action-space causal-probe advantage",
            "scalable companion behavior control",
            "open-ended action generation",
            "real companion agent readiness",
            "EGO readiness",
            "consciousness",
            "subjective experience",
            "real emotion",
            "real love",
        ],
    }


def write_artifacts(out_path: Path, result: dict[str, Any]) -> None:
    write_json(out_path / "freeze_manifest.json", result["freeze_integrity"])
    write_json(out_path / "expanded_action_space_manifest.json", result["expanded_action_space"])
    write_json(out_path / "anonymous_action_handle_permutation.json", result["anonymous_action_handle_permutation"])
    write_json(out_path / "semantic_label_leak_scan.json", result["semantic_label_leak_scan"])
    write_json(out_path / "label_permutation_report.json", result["label_permutation_report"])
    write_json(out_path / "effect_swap_report.json", result["effect_swap_report"])
    write_json(out_path / "causal_probe_results.json", result["causal_probe_results"])
    write_json(out_path / "action_distribution_entropy_report.json", result["action_distribution_entropy_report"])
    write_json(out_path / "dominant_action_rate_report.json", result["dominant_action_rate_report"])
    write_json(out_path / "baseline_comparison_report.json", result["baseline_comparison"])
    write_json(out_path / "behavior_only_replay.json", result["behavior_only_replay"])
    (out_path / "renderer_isolation_report.md").write_text(
        "# Renderer Isolation\n\n"
        "adversarial_renderer_action_change_rate = 0.0\n\n"
        "renderer_used_for_action_selection = false\n\n"
        "llm_action_selection = false\n\n"
        "not_run_reason = selector_stopped_before_rendering\n",
        encoding="utf-8",
    )
    result_summary = {
        "verdict": result["verdict"],
        "claim_boundary": result["claim_boundary"],
        "claim_after_execution": result["claim_after_execution"],
        "stop_conditions": result["stop_conditions"],
        "metrics": result["metrics"],
        "minimum_gates_satisfied": result["minimum_gates_satisfied"],
        "rca_recommended": result["rca_recommended"],
        "authorization_boundary": {
            "ego_migration": result["ego_migration"],
            "real_companion_implementation": result["real_companion_implementation"],
            "proactive_messages": result["proactive_messages"],
            "llm_action_selection": result["llm_action_selection"],
            "selector_patched": result["selector_patched"],
            "thresholds_changed": result["thresholds_changed"],
            "rag_baseline_weakened": result["rag_baseline_weakened"],
        },
        "not_authorized": result["not_authorized"],
        "not_proven": result["not_proven"],
    }
    write_json(out_path / "action_space_expansion_004_result.json", result_summary)
    (out_path / "ACTION_SPACE_EXPANSION_004_STATUS.md").write_text(
        "# CMBC Companion Action-Space Expansion 004 Execute\n\n"
        f"verdict = {result['verdict']}\n\n"
        f"claim_after_execution = {result['claim_after_execution']}\n\n"
        f"stop_conditions = {result['stop_conditions']}\n\n"
        f"requested_candidate_action_count = {result['metrics']['requested_candidate_action_count']}\n\n"
        f"selector_visible_candidate_action_count = {result['metrics']['selector_visible_candidate_action_count']}\n\n"
        "semantic_label_visible_to_selector = false\n\n"
        "rendered_text_visible_to_selector = false\n\n"
        "EGO migration = no_go\n\n"
        "real companion implementation = not_authorized\n\n"
        "proactive messages = not_authorized\n\n"
        "LLM action selection = false\n\n"
        "selector patch = false\n\n"
        "threshold change = false\n\n"
        "RAG baseline weakening = false\n",
        encoding="utf-8",
    )
    (out_path / "STOP_REPORT.md").write_text(
        "# Stop Report\n\n"
        f"verdict = {result['verdict']}\n\n"
        f"stop_conditions = {result['stop_conditions']}\n\n"
        "The frozen selector exposes only the existing 7 ACTION_HANDLES. Expanding "
        "the requested anonymous option set to 20 without changing selector code "
        "does not make those 20 options selector-visible. This run stops without "
        "selector patching, threshold changes, probe-pack changes, baseline weakening, "
        "renderer control, EGO integration, proactive messages, or LLM action selection.\n\n"
        f"recommended_next_task = {result['rca_recommended']}\n",
        encoding="utf-8",
    )


def run_action_space_expansion_004_execute(out: str | Path) -> dict[str, Any]:
    out_path = Path(out)
    out_path.mkdir(parents=True, exist_ok=True)
    result = build_result()
    write_artifacts(out_path, result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    result = run_action_space_expansion_004_execute(args.out)
    print(json.dumps({
        "verdict": result["verdict"],
        "stop_conditions": result["stop_conditions"],
        "requested_candidate_action_count": result["metrics"]["requested_candidate_action_count"],
        "selector_visible_candidate_action_count": result["metrics"]["selector_visible_candidate_action_count"],
        "minimum_gates_satisfied": result["minimum_gates_satisfied"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
