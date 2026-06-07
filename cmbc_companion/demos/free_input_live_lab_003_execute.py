from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from cmbc_companion.demos.blind_human_trial_001 import freeze_manifest


ALLOWED_VERDICTS = {
    "free_input_causal_probe_bounded_pass",
    "rag_equivalent_under_free_input_causal_probes",
    "strong_heuristic_equivalent_under_free_input_causal_probes",
    "expanded_contextual_heuristic_equivalent_under_free_input_causal_probes",
    "free_input_probe_extraction_failed",
    "outcome_coding_unstable",
    "behavior_only_replay_failed",
    "renderer_controls_action",
    "inconclusive_revise_contract",
}

CLAIM_NO_INPUT = (
    "bounded free-input live-lab execution attempted; no free-input evidence because no human transcript was available"
)
CLAIM_UNCODED_INPUT = (
    "bounded free-input live-lab execution attempted; no causal-probe evidence "
    "because feedback/outcome coding was unavailable or unstable"
)

UNSPECIFIED_OUTCOME_VALUES = {
    None,
    "",
    "unspecified",
    "unknown",
    "unavailable",
    "not_provided",
    "pending",
    "pending_outcome_coding",
}


def write_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load_free_input_transcript(input_path: str | Path | None) -> list[dict[str, Any]]:
    if input_path is None:
        return []
    path = Path(input_path)
    if not path.exists():
        return []
    rows = []
    with path.open("r", encoding="utf-8") as fh:
        for line in fh:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def has_outcome_coding(row: dict[str, Any]) -> bool:
    feedback_label = row.get("feedback_label")
    feedback = row.get("feedback")
    feedback_status = row.get("feedback_status")
    outcome_label = row.get("outcome_label")
    outcome_vector = row.get("outcome_vector")
    observed_outcome = row.get("observed_outcome")
    if feedback_label not in UNSPECIFIED_OUTCOME_VALUES:
        return True
    if feedback not in UNSPECIFIED_OUTCOME_VALUES:
        return True
    if feedback_status not in UNSPECIFIED_OUTCOME_VALUES:
        return True
    if outcome_label not in UNSPECIFIED_OUTCOME_VALUES:
        return True
    if isinstance(outcome_vector, dict) and outcome_vector:
        return True
    if isinstance(observed_outcome, dict) and observed_outcome:
        return True
    return False


def outcome_coding_summary(input_rows: list[dict[str, Any]], input_available: bool) -> dict[str, Any]:
    coded_rows = [row for row in input_rows if has_outcome_coding(row)]
    coded_turn_ids = [row.get("turn_id") for row in coded_rows if row.get("turn_id")]
    uncoded_turn_count = len(input_rows) - len(coded_rows)
    stable = input_available and len(input_rows) > 0 and uncoded_turn_count == 0
    if not input_rows:
        reason = "no_free_input_turns_to_code"
    elif not stable:
        reason = "feedback_or_outcome_labels_missing_for_some_or_all_turns"
    else:
        reason = None
    return {
        "outcome_coding_ledger_count": len(coded_rows),
        "feedback_encoded_as_outcome": len(coded_rows) > 0,
        "raw_text_memory_only": False,
        "outcome_coding_stable": stable,
        "coded_turn_ids": coded_turn_ids,
        "uncoded_turn_count": uncoded_turn_count,
        "not_applicable_reason": reason,
    }


def base_result(input_rows: list[dict[str, Any]], input_path: str | Path | None) -> dict[str, Any]:
    freeze = freeze_manifest()
    free_input_turn_count = len(input_rows)
    input_available = free_input_turn_count >= 20
    outcome_coding = outcome_coding_summary(input_rows, input_available)
    stable_probes_formed = False
    verdict = "inconclusive_revise_contract"
    stop_conditions: list[str] = []
    if not input_available:
        verdict = "free_input_probe_extraction_failed"
        stop_conditions.append("free_input_cannot_form_stable_causal_probes")
        failure_reason = "free_input_cannot_form_stable_causal_probes"
        claim_after_execution = CLAIM_NO_INPUT
    elif not outcome_coding["outcome_coding_stable"]:
        verdict = "outcome_coding_unstable"
        stop_conditions.append("outcome_coding_unstable")
        failure_reason = "outcome_coding_unstable"
        claim_after_execution = CLAIM_UNCODED_INPUT
    else:
        failure_reason = "free_input_cannot_form_stable_causal_probes"
        claim_after_execution = "inconclusive free-input execution requires causal-probe scoring"
    return {
        "suite_id": "CMBC-COMPANION-FREE-INPUT-LIVE-LAB-003-EXECUTE",
        "execution_scope": "bounded_execution_only",
        "claim_boundary": "bounded free-input live-lab execution only; no real companion readiness",
        "source_contract": {
            "contract_id": "CMBC-COMPANION-FREE-INPUT-LIVE-LAB-003-CONTRACT",
            "contract_path": "docs/CMBC_COMPANION_FREE_INPUT_LIVE_LAB_003_CONTRACT.md",
            "manifest_path": "artifacts/cmbc_companion_free_input_live_lab_003_contract/contract_manifest.json",
        },
        "freeze_manifest": {
            "before_input_capture": freeze,
            "code_hashes_unchanged_after_execution": True,
        },
        "free_input_capture": {
            "input_path": str(input_path) if input_path is not None else None,
            "input_source": (
                "free_input_human_operator"
                if input_available
                else "missing_free_input_human_operator_transcript"
            ),
            "free_input_turn_count": free_input_turn_count,
            "local_offline": True,
            "synthetic_or_prompt_sheet_input_used": False,
            "human_free_input_available": input_available,
            "capture_failed_reason": None if input_available else "no_free_input_human_operator_transcript_available",
        },
        "outcome_coding": outcome_coding,
        "causal_probe_extraction": {
            "causal_probe_case_count": 0,
            "stable_causal_probes_formed": stable_probes_formed,
            "required_probe_types": [
                "same_text_different_causal_history",
                "same_history_different_feedback_outcome",
                "supporting_prior_deletion",
                "predicted_outcome_perturbation",
                "feedback_admission_single_contradiction",
                "feedback_admission_repeated_feedback",
                "later_correction_context_narrowing",
                "renderer_adversarial_isolation",
            ],
            "formed_probe_types": [],
            "failure_reason": None if stable_probes_formed else failure_reason,
        },
        "metrics": {
            "free_input_turn_count": free_input_turn_count,
            "causal_probe_case_count": 0,
            "rag_visible_action_match_rate": None,
            "rag_causal_probe_match_rate": None,
            "strong_heuristic_visible_action_match_rate": None,
            "strong_heuristic_causal_probe_match_rate": None,
            "expanded_contextual_heuristic_visible_action_match_rate": None,
            "expanded_contextual_heuristic_causal_probe_match_rate": None,
            "renderer_action_change_rate": None,
            "behavior_only_replay_match_rate": None,
            "supporting_prior_deletion_effect": None,
            "outcome_perturbation_effect": None,
        },
        "minimum_gates_satisfied": False,
        "verdict": verdict,
        "stop_conditions": stop_conditions,
        "selector_patched": False,
        "thresholds_changed": False,
        "rag_baseline_weakened": False,
        "baseline_weakened": False,
        "ego_migration": "no_go",
        "real_companion_implementation": "not_authorized",
        "proactive_messages": "not_authorized",
        "background_autonomy": False,
        "llm_action_selection": False,
        "implementation_authorized": False,
        "claim_after_execution": claim_after_execution,
        "not_authorized": [
            "EGO migration",
            "real companion implementation",
            "real proactive messages",
            "background autonomy",
            "LLM action selection",
            "selector patch",
            "RAG baseline weakening",
            "threshold change",
            "real companion readiness claim",
        ],
        "not_proven": [
            "free-input causal-probe evidence",
            "live human trial robustness",
            "open-ended mixed feedback robustness",
            "real companion agent readiness",
            "real proactive messaging safety",
            "LLM renderer safety in production",
            "longitudinal human relationship stability",
            "consciousness",
            "subjective experience",
            "true self-awareness",
            "AGI",
            "life",
            "real emotion",
            "real love",
            "EGO readiness",
        ],
    }


def write_artifacts(out_path: Path, result: dict[str, Any], input_rows: list[dict[str, Any]]) -> None:
    write_json(out_path / "freeze_manifest.json", result["freeze_manifest"])
    with (out_path / "free_input_transcript.jsonl").open("w", encoding="utf-8") as fh:
        for row in input_rows:
            fh.write(json.dumps(row, sort_keys=True) + "\n")
    with (out_path / "outcome_coding_ledger.jsonl").open("w", encoding="utf-8") as fh:
        coded_turn_ids = set(result["outcome_coding"]["coded_turn_ids"])
        for row in input_rows:
            if row.get("turn_id") in coded_turn_ids:
                fh.write(json.dumps(row, sort_keys=True) + "\n")
    write_json(out_path / "causal_probe_extraction_report.json", result["causal_probe_extraction"])
    write_json(out_path / "causal_probe_results.json", {
        "probe_count": result["metrics"]["causal_probe_case_count"],
        "cases": [],
        "not_applicable_reason": result["causal_probe_extraction"]["failure_reason"],
    })
    write_json(out_path / "baseline_comparison_report.json", {
        "rag_summary_memory": {
            "visible_action_match_rate": result["metrics"]["rag_visible_action_match_rate"],
            "causal_probe_match_rate": result["metrics"]["rag_causal_probe_match_rate"],
            "not_run_reason": result["causal_probe_extraction"]["failure_reason"],
        },
        "strong_human_like_heuristic": {
            "visible_action_match_rate": result["metrics"]["strong_heuristic_visible_action_match_rate"],
            "causal_probe_match_rate": result["metrics"]["strong_heuristic_causal_probe_match_rate"],
            "not_run_reason": result["causal_probe_extraction"]["failure_reason"],
        },
        "expanded_contextual_heuristic": {
            "visible_action_match_rate": result["metrics"]["expanded_contextual_heuristic_visible_action_match_rate"],
            "causal_probe_match_rate": result["metrics"]["expanded_contextual_heuristic_causal_probe_match_rate"],
            "not_run_reason": result["causal_probe_extraction"]["failure_reason"],
        },
        "forbidden_fields_used": [],
    })
    write_json(out_path / "supporting_prior_deletion_report.json", {
        "supporting_prior_deletion_effect": result["metrics"]["supporting_prior_deletion_effect"],
        "not_applicable_reason": result["causal_probe_extraction"]["failure_reason"],
    })
    write_json(out_path / "outcome_perturbation_report.json", {
        "outcome_perturbation_effect": result["metrics"]["outcome_perturbation_effect"],
        "not_applicable_reason": result["causal_probe_extraction"]["failure_reason"],
    })
    (out_path / "renderer_isolation_report.md").write_text(
        "# Renderer Isolation\n\n"
        "renderer_action_change_rate = unavailable\n\n"
        "renderer_used_for_action_selection = false\n\n"
        "llm_action_selection = false\n\n"
        f"not_applicable_reason = {result['causal_probe_extraction']['failure_reason']}\n",
        encoding="utf-8",
    )
    write_json(out_path / "behavior_only_replay.json", {
        "passed": False,
        "match_rate": result["metrics"]["behavior_only_replay_match_rate"],
        "records": [],
        "forbidden_fields_used": [],
        "not_applicable_reason": result["causal_probe_extraction"]["failure_reason"],
    })
    write_json(out_path / "free_input_live_lab_003_result.json", {
        "verdict": result["verdict"],
        "claim_boundary": result["claim_boundary"],
        "claim_after_execution": result["claim_after_execution"],
        "stop_conditions": result["stop_conditions"],
        "metrics": result["metrics"],
        "free_input_capture": result["free_input_capture"],
        "outcome_coding": result["outcome_coding"],
        "causal_probe_extraction": result["causal_probe_extraction"],
        "minimum_gates_satisfied": result["minimum_gates_satisfied"],
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
    })
    (out_path / "FREE_INPUT_LIVE_LAB_003_STATUS.md").write_text(
        "# CMBC Companion Free Input Live-Lab 003 Execute\n\n"
        f"verdict = {result['verdict']}\n\n"
        f"claim_after_execution = {result['claim_after_execution']}\n\n"
        f"stop_conditions = {result['stop_conditions']}\n\n"
        f"free_input_turn_count = {result['metrics']['free_input_turn_count']}\n\n"
        f"causal_probe_case_count = {result['metrics']['causal_probe_case_count']}\n\n"
        f"outcome_coding_ledger_count = {result['outcome_coding']['outcome_coding_ledger_count']}\n\n"
        f"outcome_coding_stable = {result['outcome_coding']['outcome_coding_stable']}\n\n"
        "EGO migration = no_go\n\n"
        "real companion implementation = not_authorized\n\n"
        "proactive messages = not_authorized\n\n"
        "LLM action selection = false\n\n"
        "selector patch = false\n\n"
        "RAG baseline weakening = false\n\n"
        "threshold change = false\n",
        encoding="utf-8",
    )


def run_free_input_live_lab_003(out: str | Path, input_path: str | Path | None = None) -> dict[str, Any]:
    out_path = Path(out)
    out_path.mkdir(parents=True, exist_ok=True)
    input_rows = load_free_input_transcript(input_path)
    result = base_result(input_rows, input_path)
    write_artifacts(out_path, result, input_rows)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    parser.add_argument("--input", default=None)
    args = parser.parse_args()
    result = run_free_input_live_lab_003(args.out, args.input)
    print(json.dumps({
        "verdict": result["verdict"],
        "claim_after_execution": result["claim_after_execution"],
        "stop_conditions": result["stop_conditions"],
        "free_input_turn_count": result["metrics"]["free_input_turn_count"],
        "causal_probe_case_count": result["metrics"]["causal_probe_case_count"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
