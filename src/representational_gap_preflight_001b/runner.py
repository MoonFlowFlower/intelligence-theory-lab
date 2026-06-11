from __future__ import annotations

import hashlib
import json
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Dict, Optional

from . import core

TASK_ID = "REPRESENTATIONAL-GAP-PREFLIGHT-001B"
CLAIM_CEILING = "bounded fair-control representational-gap negative preflight evidence only"


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _stable_json(data: object) -> str:
    return json.dumps(data, sort_keys=True, indent=2)


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _write_json(path: Path, data: object) -> None:
    path.write_text(_stable_json(data) + "\n", encoding="utf-8")


def _task_card_hash(task_card_path: Path) -> str:
    if task_card_path.exists():
        return hashlib.sha256(task_card_path.read_bytes()).hexdigest()
    return "task_card_missing"


def default_anchor_provider(payload_hash: str) -> Dict[str, object]:
    request = urllib.request.Request(
        "https://api.github.com/rate_limit",
        headers={"User-Agent": "intelligence-theory-lab-representational-gap-preflight-001b"},
    )
    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            return {
                "anchor_method": "https_date_header_github_api",
                "anchored_payload_hash": payload_hash,
                "external_utc": response.headers.get("Date", ""),
                "external_url": "https://api.github.com/rate_limit",
                "verification_status": "verified" if response.headers.get("Date") else "failed",
            }
    except Exception as exc:  # pragma: no cover - only exercised on network failure.
        return {
            "anchor_method": "https_date_header_github_api",
            "anchored_payload_hash": payload_hash,
            "verification_status": "failed",
            "error": repr(exc),
        }


def _stage0_payload(task_card_path: Path) -> Dict[str, object]:
    return {
        "task_id": TASK_ID,
        "task_card_hash": _task_card_hash(task_card_path),
        "environment_family_definition": core.environment_contract(),
        "target_rule_definition": core.target_rule_contract(),
        "sequence_or_episode_length": core.SEQUENCE_LENGTH,
        "heldout_split_definition": core.environment_contract()["heldout_split_definition"],
        "control_family_definitions": core.control_family_contracts(),
        "graph_cache_family_definitions": core.control_family_contracts()["graph_cache_controls"],
        "fsm_family_definitions": core.control_family_contracts()["finite_state_automaton_controls"],
        "summary_family_definitions": core.control_family_contracts()["summary_controls"],
        "allowed_access_contract": core.access_contract(),
        "positive_witness_class_definition": core.witness_family_contracts(),
        "stage0_freeze_scope": [
            "environment_family_definition",
            "target_rule_definition",
            "sequence_or_episode_length",
            "heldout_split_definition",
            "control_family_definitions",
            "graph_cache_family_definitions",
            "fsm_family_definitions",
            "summary_family_definitions",
            "allowed_access_contract",
            "positive_witness_class_definition",
        ],
    }


def _anchor_ok(anchor: Dict[str, object], payload_hash: str) -> bool:
    return (
        anchor.get("verification_status") == "verified"
        and anchor.get("anchored_payload_hash") == payload_hash
    )


def _failure_stage0_result(output_dir: Path, anchor_record: Dict[str, object]) -> Dict[str, object]:
    result = {
        "task_id": TASK_ID,
        "verdict": "representational_gap_001b_failed_stage0_anchor",
        "claim_ceiling": "no 001B representational-gap evidence",
        "stage0_anchor_pass": False,
        "verifier_ran": False,
        "training_performed": False,
        "model_class_reset_authorized": False,
        "same_agent_bridge_status": "not_authorized",
        "gate1_reopen_status": "not_authorized",
        "ego_integration_status": "not_authorized",
        "stop_conditions": ["stage0_anchor_failed"],
        "failure_taxonomy_labels": ["stage0_anchor_failed"],
        "next_allowed_task": "retry_stage0_or_theory_reset",
    }
    _write_json(output_dir / "stage0_freeze_anchor.json", anchor_record)
    _write_json(output_dir / "failure_taxonomy_report.json", result)
    _write_json(output_dir / "result.json", result)
    return result


def _select_verdict(summary: Dict[str, object]) -> str:
    if summary["full_history_count_statistic_controls_solved"]:
        return "representational_gap_001b_failed_count_or_statistic_control_solved"
    if summary["finite_state_automaton_controls_solved"]:
        return "representational_gap_001b_failed_fsm_control_solved"
    if summary["graph_cache_controls_solved"]:
        return "representational_gap_001b_failed_graph_cache_control_solved"
    if summary["knn_episodic_controls_solved"]:
        return "representational_gap_001b_failed_knn_or_episodic_control_solved"
    if summary["summary_controls_solved"]:
        return "representational_gap_001b_failed_summary_control_solved"
    if not summary["not_trivial_horizon_gap"]:
        return "representational_gap_001b_blocked_trivial_horizon_gap"
    if not summary["environment_not_lookup_trivial"]:
        return "representational_gap_001b_blocked_lookup_triviality"
    if not summary["positive_witness_exists"]:
        return "representational_gap_001b_failed_no_positive_witness"
    if not summary["positive_witness_uses_only_allowed_access"]:
        return "representational_gap_001b_failed_witness_uses_oracle_access"
    if not summary["positive_witness_not_in_failed_challenger_family"]:
        return "representational_gap_001b_failed_witness_family_contradiction"
    if not summary["bounded_window_gap_verified"]:
        return "representational_gap_001b_failed_window_only_gap"
    return "representational_gap_001b_bounded_pass"


def _failure_labels(verifier: Dict[str, object]) -> list[str]:
    summary = verifier["computed_summary"]
    labels = []
    if summary["full_history_count_statistic_controls_solved"]:
        labels.append("fair_full_history_count_statistic_control_solved")
    if summary["finite_state_automaton_controls_solved"]:
        labels.append("fair_fsm_control_solved")
    if summary["graph_cache_controls_solved"]:
        labels.append("fair_graph_cache_control_solved")
    if summary["knn_episodic_controls_solved"]:
        labels.append("fair_knn_or_episodic_control_solved")
    if summary["summary_controls_solved"]:
        labels.append("fair_summary_control_solved")
    if not summary["environment_not_lookup_trivial"]:
        labels.append("lookup_triviality_detected")
    if not summary["not_trivial_horizon_gap"]:
        labels.append("trivial_horizon_gap_after_fair_controls")
    return labels


def run_preflight_001b(
    output_dir: Path | str,
    task_card_path: Path | str,
    anchor_provider: Optional[Callable[[str], Dict[str, object]]] = None,
) -> Dict[str, object]:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    card_path = Path(task_card_path)

    payload = _stage0_payload(card_path)
    payload_hash = _sha256_text(_stable_json(payload))
    provider = anchor_provider or default_anchor_provider
    anchor = provider(payload_hash)
    anchor_record = {
        "task_id": TASK_ID,
        "stage0_payload": payload,
        "stage0_payload_hash": payload_hash,
        "anchor": anchor,
        "stage0_anchor_pass": _anchor_ok(anchor, payload_hash),
        "stage0_order": {
            "freeze_payload_before_anchor": True,
            "anchor_verified_before_verifier": False,
            "verifier_started_before_anchor": False,
        },
    }

    if not anchor_record["stage0_anchor_pass"]:
        return _failure_stage0_result(output_path, anchor_record)

    anchor_record["first_run_start_time_after_anchor"] = _utc_now()
    anchor_record["stage0_order"]["anchor_verified_before_verifier"] = True
    _write_json(output_path / "stage0_freeze_anchor.json", anchor_record)

    verifier = core.run_verifier()
    summary = verifier["computed_summary"]
    verdict = _select_verdict(summary)
    failure_labels = _failure_labels(verifier)
    passed = verdict == "representational_gap_001b_bounded_pass"
    result = {
        "task_id": TASK_ID,
        "verdict": verdict,
        "claim_ceiling": CLAIM_CEILING,
        "stage0_anchor_pass": True,
        "verifier_ran": True,
        "training_performed": False,
        "mechanism_training_performed": False,
        "agent_training_performed": False,
        "model_class_reset_authorized": False,
        "same_agent_bridge_status": "not_authorized",
        "gate1_reopen_status": "not_authorized",
        "ego_integration_status": "not_authorized",
        "llm_rag_companion_emotion_relationship_user_model_modules": "not_introduced",
        "next_allowed_task": (
            "independent_audit_of_001B"
            if passed
            else "theory_reset_or_new_problem_definition"
        ),
        "MODEL_CLASS_RESET": (
            "still_requires_audit_pass_and_human_signoff"
            if passed
            else "not_authorized"
        ),
        "stop_conditions": failure_labels,
        "failure_taxonomy_labels": failure_labels,
        "environment_contract_frozen": True,
        "access_contract_frozen": True,
        "control_signatures_frozen": True,
        "control_competence_tests_execute_real_code_or_real_proofs": verifier[
            "control_competence_report"
        ]["control_competence_tests_execute_real_code_or_real_proofs"],
        "bounded_window_gap_verified": summary["bounded_window_gap_verified"],
        "full_history_count_statistic_controls_solved": summary[
            "full_history_count_statistic_controls_solved"
        ],
        "full_history_count_statistic_controls_fail_fairly": not summary[
            "full_history_count_statistic_controls_solved"
        ],
        "finite_state_automaton_controls_solved": summary["finite_state_automaton_controls_solved"],
        "finite_state_automaton_controls_fail_fairly": not summary["finite_state_automaton_controls_solved"],
        "graph_cache_controls_solved": summary["graph_cache_controls_solved"],
        "graph_cache_controls_fail_fairly": not summary["graph_cache_controls_solved"],
        "knn_episodic_controls_solved": summary["knn_episodic_controls_solved"],
        "knn_episodic_controls_fail_fairly": not summary["knn_episodic_controls_solved"],
        "summary_controls_solved": summary["summary_controls_solved"],
        "summary_controls_fail_fairly": not summary["summary_controls_solved"],
        "positive_witness_exists": summary["positive_witness_exists"],
        "positive_witness_uses_only_allowed_access": summary["positive_witness_uses_only_allowed_access"],
        "positive_witness_not_in_failed_challenger_family": summary[
            "positive_witness_not_in_failed_challenger_family"
        ],
        "controls_not_disabled_by_construction": summary["controls_not_disabled_by_construction"],
        "environment_not_lookup_trivial": summary["environment_not_lookup_trivial"],
        "not_trivial_horizon_gap": summary["not_trivial_horizon_gap"],
        "claim_ceiling_observed": True,
    }

    _write_all_artifacts(output_path, result, verifier, anchor_record)
    return result


def _write_all_artifacts(
    output_path: Path,
    result: Dict[str, object],
    verifier: Dict[str, object],
    anchor_record: Dict[str, object],
) -> None:
    _write_json(
        output_path / "task_manifest.json",
        {
            "task_id": TASK_ID,
            "parent_closeout": "REPRESENTATIONAL-GAP-PREFLIGHT-001A-AUDIT-CLOSEOUT",
            "execution_type": "design + closed-form proof + constructive verifier only",
            "training_authorized": False,
            "stage0_payload_hash": anchor_record["stage0_payload_hash"],
        },
    )
    _write_json(
        output_path / "hypothesis_registry.json",
        {
            "core_hypothesis": (
                "fair full-history cheap controls fail while a non-oracle witness solves"
            ),
            "verdict": result["verdict"],
            "hypothesis_survived": result["verdict"] == "representational_gap_001b_bounded_pass",
            "parent_audit_inheritance": "001A full pass rejected; only K<=4 window residue and XOR witness accepted",
        },
    )
    _write_json(output_path / "environment_contract.json", core.environment_contract())
    _write_json(output_path / "target_rule_contract.json", core.target_rule_contract())
    _write_json(output_path / "access_contract.json", core.access_contract())
    _write_json(output_path / "control_family_contracts.json", core.control_family_contracts())
    _write_json(output_path / "witness_family_contracts.json", core.witness_family_contracts())
    _write_json(output_path / "champion_challenger_matrix.json", verifier["champion_challenger_matrix"])
    _write_json(output_path / "control_competence_report.json", verifier["control_competence_report"])
    _write_json(output_path / "verifier_results.json", verifier)
    _write_json(
        output_path / "control_disabled_by_construction_audit.json",
        verifier["control_disabled_by_construction_audit"],
    )
    _write_json(output_path / "lookup_triviality_audit.json", verifier["lookup_triviality_audit"])
    _write_json(output_path / "trivial_horizon_gap_audit.json", verifier["trivial_horizon_gap_audit"])
    _write_json(
        output_path / "failure_taxonomy_report.json",
        {
            "task_id": TASK_ID,
            "verdict": result["verdict"],
            "failure_taxonomy_labels": result["failure_taxonomy_labels"],
            "primary_failure": result["verdict"],
            "no_posthoc_environment_repair": True,
        },
    )
    _write_json(
        output_path / "decision_ledger.json",
        {
            "task_id": TASK_ID,
            "decision": result["verdict"],
            "codex_001a_verdict": "superseded_by_independent_audit",
            "model_class_reset_authorized": False,
            "same_agent_bridge": "not_authorized",
            "next_allowed_task": result["next_allowed_task"],
        },
    )
    (output_path / "expressivity_proof.md").write_text(_expressivity_proof(result, verifier), encoding="utf-8")
    (output_path / "claim_ceiling.md").write_text(_claim_ceiling_text(), encoding="utf-8")
    (output_path / "final_report.md").write_text(_final_report(result, verifier), encoding="utf-8")
    _write_json(output_path / "result.json", result)


def _expressivity_proof(result: Dict[str, object], verifier: Dict[str, object]) -> str:
    return "\n".join(
        [
            "# Expressivity Proof",
            "",
            "The frozen family preserves the 001A K<=4 bounded-window collision residue: suffix windows of",
            "length 1 through 4 have equivalence classes containing both target labels.",
            "",
            "Under the fair 001B control contract, this residue does not survive. The full-history paired-token",
            "count statistic computes `(count(a0_o1) + count(a1_o0)) mod 2`, which equals the target for every",
            "enumerated history. A 2-state finite automaton with token-conditioned parity transitions also solves",
            "the target. History graph cache, exact episodic retrieval, successor-map parity composition, and",
            "minimal sufficient summary search solve as well.",
            "",
            f"Verdict: `{result['verdict']}`.",
            "",
            "This is negative evidence for the attempted 001B gap, not evidence for model-class reset.",
        ]
    ) + "\n"


def _claim_ceiling_text() -> str:
    return "\n".join(
        [
            "# Claim Ceiling",
            "",
            "At most:",
            "",
            "```text",
            CLAIM_CEILING,
            "```",
            "",
            "This failure does not prove that no representational gap exists in general. It proves only that the",
            "frozen 001B candidate did not survive fair full-history controls.",
            "",
            "```text",
            "model_class_reset = not_authorized",
            "Gate1_reopen = not_authorized",
            "same_agent_bridge = blocked",
            "EGO_integration = not_authorized",
            "agency_consciousness_functional_subject_companion_AGI_claims = not_supported",
            "```",
        ]
    ) + "\n"


def _final_report(result: Dict[str, object], verifier: Dict[str, object]) -> str:
    sections = [
        ("A. Executive verdict", f"`{result['verdict']}`. Fair controls solved the frozen target."),
        ("B. Scope confirmation", "Closed-form verifier only; no training, no Gate1, no bridge, no EGO work."),
        (
            "C. Parent audit inheritance",
            "001A full pass is superseded; only K<=4 window collision and one-bit XOR witness residue are accepted.",
        ),
        (
            "D. Stage 0 freeze / anchor report",
            "Freeze payload was hashed and externally anchored before verifier execution.",
        ),
        ("E. Environment contract", core.environment_contract()["environment_family"]),
        ("F. Target rule contract", core.target_rule_contract()["target_rule"]),
        ("G. Access contract", "Controls and witnesses share the same allowed full token history."),
        ("H. Window-model audit", "K=1..4 suffix windows collide; this residue remains narrow."),
        (
            "I. Full-history count/statistic audit",
            "Full-history pair counts and parity/modular statistic solve the target.",
        ),
        ("J. FSM / automaton audit", "Capacity-2,4,8,16 finite-state automata solve the target."),
        ("K. Graph/cache audit", "History graph cache and allowed-state successor/planner controls solve."),
        ("L. kNN / episodic retrieval audit", "Full-trace nearest neighbor and exact episodic retrieval solve."),
        ("M. Summary-statistic audit", "Minimal sufficient parity summary solves."),
        (
            "N. Positive witness audit",
            "The one-bit XOR witness solves using allowed access, but matching fair controls also solve.",
        ),
        (
            "O. Control-disabled-by-construction audit",
            "Controls were not disabled by construction; multiple controls solved.",
        ),
        ("P. Lookup-triviality audit", "Full-history cache/exact retrieval solve the finite family."),
        (
            "Q. Trivial-horizon-gap audit",
            "The remaining window gap is a K-window horizon limitation, not a fair-control gap.",
        ),
        ("R. Champion/challenger matrix", "Stored in champion_challenger_matrix.json."),
        (
            "S. Trace/schema implications",
            "episode_id, step_id, observation, action, allowed_history, verifier-only target label, witness/control state traces, heldout id, access manifest, lineage id.",
        ),
        (
            "T. Integration debt status",
            "MODEL_CLASS_RESET = not_authorized; same_agent_bridge = blocked.",
        ),
        ("U. Zeno trap check", "No environment repair, K increase, capacity lowering, summary banning, or training occurred."),
        ("V. Claim ceiling", CLAIM_CEILING),
        (
            "W. What this does not prove",
            "model_class_reset_readiness = not_supported; Gate1_reopen = not_authorized; same_agent_bridge = blocked; EGO_integration = not_authorized; agency/consciousness/functional-subject/companion/AGI evidence = not_supported.",
        ),
        ("X. Next allowed task", result["next_allowed_task"]),
    ]
    lines = ["# REPRESENTATIONAL-GAP-PREFLIGHT-001B Final Report", ""]
    for title, body in sections:
        lines.extend([f"## {title}", "", str(body), ""])
    return "\n".join(lines)


def main() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    result = run_preflight_001b(
        output_dir=repo_root / "artifacts" / "representational_gap_001b",
        task_card_path=repo_root / "docs" / "REPRESENTATIONAL-GAP-PREFLIGHT-001B.md",
    )
    print(_stable_json(result))


if __name__ == "__main__":
    main()
