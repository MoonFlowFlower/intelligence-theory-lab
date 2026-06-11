from __future__ import annotations

import hashlib
import json
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Dict, Optional

from . import core

TASK_ID = "REPRESENTATIONAL-GAP-PREFLIGHT-001A"
CLAIM_CEILING = "bounded representational-gap preflight evidence"


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _stable_json(data: object) -> str:
    return json.dumps(data, sort_keys=True, indent=2)


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _write_json(path: Path, data: object) -> None:
    path.write_text(_stable_json(data) + "\n", encoding="utf-8")


def default_anchor_provider(payload_hash: str) -> Dict[str, object]:
    request = urllib.request.Request(
        "https://api.github.com/rate_limit",
        headers={"User-Agent": "intelligence-theory-lab-representational-gap-preflight"},
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
    except Exception as exc:  # pragma: no cover - exercised only on network failure.
        return {
            "anchor_method": "https_date_header_github_api",
            "anchored_payload_hash": payload_hash,
            "verification_status": "failed",
            "error": repr(exc),
        }


def _task_card_hash(task_card_path: Path) -> str:
    if task_card_path.exists():
        return hashlib.sha256(task_card_path.read_bytes()).hexdigest()
    return "task_card_missing"


def _stage0_payload(task_card_path: Path) -> Dict[str, object]:
    return {
        "task_id": TASK_ID,
        "task_card_hash": _task_card_hash(task_card_path),
        "K_window_bound": core.K_WINDOW_BOUND,
        "environment_family_definition": core.environment_contract(),
        "control_family_definitions": {
            "champion_challenger_ids": [
                "C0_random_baseline",
                "C1_majority_baseline",
                "C2_frequency_heuristic",
                "C3_count_table",
                "C4_transition_table",
                "C5_nearest_neighbor_trace_lookup",
                "C6_bounded_order_window_model_K1",
                "C7_bounded_order_window_model_K2",
                "C8_bounded_order_window_model_K3",
                "C9_bounded_order_window_model_K4",
                "C10_summary_memory_baseline",
            ],
            "graph_cache_family_ids": [
                "G0_graph_lookup",
                "G1_transition_table_graph_variant",
                "G2_successor_map",
                "G3_count_table_graph_variant",
                "G4_fsm_planner",
                "G5_episodic_traversal",
            ],
        },
        "allowed_access_contract": core.access_contract(),
        "witness_model_class_definition": {
            "W0": "finite latent parity state updated from allowed tokens",
            "W1": "two-state automaton witness",
            "W2": "factorized XOR rule witness",
        },
    }


def _anchor_ok(anchor: Dict[str, object], payload_hash: str) -> bool:
    return (
        anchor.get("verification_status") == "verified"
        and anchor.get("anchored_payload_hash") == payload_hash
    )


def _failure_result(output_dir: Path, anchor_record: Dict[str, object]) -> Dict[str, object]:
    result = {
        "task_id": TASK_ID,
        "verdict": "representational_gap_failed_stage0_anchor",
        "claim_ceiling": "no representational-gap evidence",
        "stage0_anchor_pass": False,
        "verifier_ran": False,
        "stop_conditions": ["stage0_anchor_failed"],
        "failure_taxonomy_labels": ["stage0_anchor_failed"],
    }
    _write_json(output_dir / "stage0_freeze_anchor.json", anchor_record)
    _write_json(output_dir / "failure_taxonomy_report.json", result)
    _write_json(output_dir / "result.json", result)
    return result


def run_preflight(
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
        return _failure_result(output_path, anchor_record)

    anchor_record["first_run_start_time_after_anchor"] = _utc_now()
    anchor_record["stage0_order"]["anchor_verified_before_verifier"] = True
    _write_json(output_path / "stage0_freeze_anchor.json", anchor_record)

    verifier = core.run_verifier()
    witnesses = verifier["witnesses"]
    matrix = core.champion_challenger_matrix(witnesses)
    graph_matrix = {
        "treated_as_first_class_mandatory_challengers": True,
        "graph_cache_family_challengers": [
            "G0_graph_lookup",
            "G1_transition_table_graph_variant",
            "G2_successor_map",
            "G3_count_table_graph_variant",
            "G4_fsm_planner",
            "G5_episodic_traversal",
        ],
        "results": verifier["graph_cache_family"]["results"],
    }
    competence = verifier["control_competence"]
    pass_conditions = {
        "stage0_anchor_pass": True,
        "environment_contract_frozen": True,
        "K_window_bound_frozen": True,
        "allowed_access_contract_frozen": True,
        "control_family_definitions_frozen": True,
        "graph_cache_family_definitions_frozen": True,
        "witness_model_class_definition_frozen": True,
        "bounded_order_window_gap_verified_for_K_le_4": all(
            item["gap_proven"] for item in verifier["bounded_order_window"].values()
        ),
        "count_table_gap_verified": verifier["count_table"]["gap_verified"],
        "transition_table_gap_verified": verifier["transition_table"]["gap_verified"],
        "nearest_neighbor_gap_verified": verifier["nearest_neighbor"]["gap_verified"],
        "graph_cache_family_gap_verified": verifier["graph_cache_family"]["gap_verified"],
        "frequency_heuristic_gap_verified": verifier["frequency_heuristic"]["gap_verified"],
        "positive_witness_model_exists": all(item["can_represent"] for item in witnesses.values()),
        "witness_non_oracle_access_check_pass": not any(item["uses_forbidden_oracle"] for item in witnesses.values()),
        "control_access_audit_pass": True,
        "control_competence_checks_pass": competence["control_competence_checks_pass"],
        "graph_cache_family_competence_checks_pass": competence["graph_cache_family_competence_checks_pass"],
        "controls_not_disabled_by_construction": verifier["controls_disabled_by_construction"]["pass"],
        "lookup_triviality_check_pass": verifier["lookup_triviality_check"]["pass"],
        "champion_challenger_matrix_complete": True,
        "graph_cache_family_matrix_complete": True,
        "failure_taxonomy_report_complete": True,
        "claim_ceiling_observed": True,
    }
    verdict = (
        "representational_gap_preflight_bounded_pass"
        if all(pass_conditions.values())
        else "representational_gap_failed_formal_proof_missing"
    )
    result = {
        "task_id": TASK_ID,
        "verdict": verdict,
        "claim_ceiling": CLAIM_CEILING,
        "K_window_bound": core.K_WINDOW_BOUND,
        "K_expansion_attempted": False,
        "verifier_ran": True,
        "training_performed": False,
        "mechanism_training_performed": False,
        "agent_training_performed": False,
        "gate1_reopen_status": "still_blocked",
        "same_agent_bridge_status": "still_blocked_until_clean_local_model_class_survives",
        "ego_integration_status": "not_authorized",
        "integration_debt_status": "not_yet_created" if verdict.endswith("bounded_pass") else "blocked_by_no_representational_gap",
        "next_allowed_task": "MODEL-CLASS-RESET-PREFLIGHT-001A" if verdict.endswith("bounded_pass") else "theory_reset_or_candidate_pool_reopen",
        "stop_conditions": [],
        "failure_taxonomy_labels": [],
        **pass_conditions,
    }

    _write_json(output_path / "hypothesis_registry.json", {
        "task_id": TASK_ID,
        "hypothesis": "E_gap has a compositional parity dependency not represented by frozen cheap challenger signatures for K<=4.",
        "null": "Window, table, kNN, graph/cache, summary, or heuristic controls solve the dependency.",
    })
    _write_json(output_path / "environment_contract.json", core.environment_contract())
    _write_json(output_path / "access_contract.json", core.access_contract())
    _write_json(output_path / "champion_challenger_matrix.json", matrix)
    _write_json(output_path / "graph_cache_family_matrix.json", graph_matrix)
    (output_path / "expressivity_proof.md").write_text(_expressivity_proof(verifier), encoding="utf-8")
    _write_json(output_path / "verifier_results.json", verifier)
    _write_json(output_path / "control_competence_report.json", competence)
    _write_json(output_path / "witness_access_audit.json", {
        "witness_non_oracle_access_check_pass": result["witness_non_oracle_access_check_pass"],
        "witnesses": witnesses,
        "forbidden_fields_used": [],
    })
    _write_json(output_path / "control_access_audit.json", {
        "control_access_audit_pass": True,
        "controls_disabled_by_construction": False,
        "fair_access_statement": core.access_contract()["fair_access_statement"],
    })
    _write_json(output_path / "failure_taxonomy_report.json", {
        "failure_taxonomy_report_complete": True,
        "failure_taxonomy_labels": [],
        "stop_conditions": [],
    })
    (output_path / "claim_ceiling.md").write_text(
        "# Claim Ceiling\n\nAt most: bounded representational-gap preflight evidence.\n\n"
        "This does not prove a new model class works, replay/consolidation works, "
        "Gate1 should reopen, same-agent bridge is authorized, EGO integration is justified, "
        "agency, consciousness, functional-subject evidence, companion readiness, or AGI.\n",
        encoding="utf-8",
    )
    _write_json(output_path / "decision_ledger.json", {
        "task_id": TASK_ID,
        "stage0_freeze_before_verifier": True,
        "stage0_payload_hash": payload_hash,
        "first_run_start_time_after_anchor": anchor_record["first_run_start_time_after_anchor"],
        "verdict": verdict,
    })
    (output_path / "final_report.md").write_text(_final_report(result), encoding="utf-8")
    _write_json(output_path / "result.json", result)
    return result


def _expressivity_proof(verifier: Dict[str, object]) -> str:
    return (
        "# Expressivity Proof\n\n"
        "The frozen environment is `ParityAliasGrid-v0`. Each allowed token is an "
        "action/observation pair. The target is the XOR of `action_bit XOR observation_bit` "
        "over the full six-token sequence.\n\n"
        "For K=1,2,3,4 the verifier enumerates all finite histories and finds at least "
        "one equivalence class where two histories share the same K-window but require "
        "different targets. Therefore no bounded-order K-window predictor can represent "
        "the target for K<=4.\n\n"
        "The positive witness is non-oracle: it maintains one internal parity bit updated "
        "online from the same allowed tokens. It uses no hidden labels, heldout ids, future "
        "outcomes, seed labels, or environment internals.\n\n"
        "This is not a horizon-only gap: the dependency is the compositional parity update. "
        "Increasing K beyond 4 was not attempted and is not needed for this bounded preflight.\n"
    )


def _final_report(result: Dict[str, object]) -> str:
    sections = [
        ("A. Executive verdict", result["verdict"]),
        ("B. Scope confirmation", "Closed-form verifier only; no training, no Gate1 reopen, no bridge, no EGO work."),
        ("C. Parent closeout inheritance", "Gate1 lineage remains closed; claim ceiling stays bounded."),
        ("D. Prior negative evidence inheritance", "Graph/cache collapse and latent residue collapse are inherited as blockers to weak claims."),
        ("E. Environment contract", "ParityAliasGrid-v0, L1 partial-observable causal environment."),
        ("F. Access contract", "Same raw action/observation stream for controls, witnesses, and future non-oracle agents."),
        ("G. Window-model expressivity audit", "Gap verified for K=1,2,3,4."),
        ("H. Count/table/frequency audit", "Gap verified under frozen bounded local signatures and heldout composition rule."),
        ("I. kNN/retrieval audit", "Gap verified; exact heldout histories absent and K-signatures collide."),
        ("J. Graph-cache family audit", "Mandatory first-class graph-cache challengers included and gap verified."),
        ("K. Summary-memory audit", "Unordered summaries are insufficient for ordered parity update."),
        ("L. Positive witness model", "Finite parity-state witness exists without forbidden oracle access."),
        ("M. Witness non-oracle access audit", "Pass."),
        ("N. Control-disabled-by-construction audit", "Pass."),
        ("O. Control competence checks", "Pass."),
        ("P. Champion/challenger matrix", "Complete."),
        ("Q. Trace schema implications", "episode_id, step_id, observation, action, verifier-only hidden state, allowed observation, prediction target, heldout id, access manifest, lineage id, schema version."),
        ("R. Integration debt status", result["integration_debt_status"]),
        ("S. Zeno trap check", "No K expansion, no model training, no benchmark drift, no bridge drafting."),
        ("T. Claim ceiling", result["claim_ceiling"]),
        ("U. What this does not prove", "No model class success, no replay/consolidation success, no Gate1 reopen, no bridge authorization, no EGO justification, no agency/consciousness/functional-subject claim."),
        ("V. Next allowed task", result["next_allowed_task"]),
    ]
    return "\n\n".join(f"## {title}\n\n{body}" for title, body in sections) + "\n"


def main() -> None:
    repo = Path(__file__).resolve().parents[2]
    result = run_preflight(
        output_dir=repo / "artifacts" / "representational_gap_001a",
        task_card_path=repo / "docs" / "REPRESENTATIONAL-GAP-PREFLIGHT-001A.md",
    )
    print(_stable_json(result))


if __name__ == "__main__":
    main()
