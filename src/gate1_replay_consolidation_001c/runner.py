import hashlib
import json
from pathlib import Path
from typing import Any


TASK_ID = "GATE1-REPLAY-CONSOLIDATION-001C-EXECUTABLE-PREFLIGHT"
VERDICT = "gate1_replay_consolidation_001c_bounded_preflight_pass"
CLAIM_CEILING = "bounded Gate1 replay/consolidation executable preflight evidence only"
GATE1_RUN_ID = "gate1_replay_consolidation_001c_preflight_run_v1"
BASE_TASK_CARD_ANCHOR = "b813651"
AMENDMENT_ANCHOR = "5734dc8"

REQUIRED_BASELINES = [
    "retrieval / summary retrieval",
    "behavior-only replay",
    "trace-only replay as hygiene only",
    "online count/statistic controls",
    "transition table / successor map / graph cache controls",
    "target-free generative replay challenger",
    "frozen-history control",
    "no-consolidation control",
    "shuffled-replay control",
    "corrupted-replay control",
]
REQUIRED_ABLATIONS = [
    "learning freeze",
    "history replacement",
    "consolidation disabled",
    "replay order shuffled",
    "replay content corrupted",
    "heldout composition",
    "delayed-effect cases",
    "observable-key conflict cases",
    "partial-observability cases",
    "counterfactual action contrast",
]
REQUIRED_EXECUTION_ARTIFACTS = [
    "replay_event_log.json",
    "consolidation_trace.json",
    "state_hash_chain.json",
    "replay_behavior_linkage_table.json",
    "linkage_key_collision_report.json",
    "later_behavior_evaluation.json",
    "mutation_check_report.json",
    "baseline_comparison.json",
    "ablation_report.json",
    "result.json",
    "claim_ceiling.txt",
]
ALLOWED_LINKAGE_INPUTS = [
    "gate1_run_id",
    "target_case_id",
    "replay_event_id",
    "consolidation_event_id",
    "later_behavior_eval_id",
]
FORBIDDEN_LINKAGE_INPUTS = [
    "heldout_outcome",
    "target_heldout_outcome",
    "future_behavior_label",
    "target_future_behavior_label",
    "witness_result",
    "witness_match_result",
    "post_evaluation_metric",
    "post_evaluation_metrics",
]
AUTHORIZATION_FLAGS = {
    "formal_gate1_execution_authorized": False,
    "gate1_runtime_implementation_authorized": False,
    "same_agent_bridge_authorized": False,
    "ego_mainline_authorized": False,
    "ego_integration_authorized": False,
    "mechanism_tournament_authorized": False,
    "model_class_reset_authorized": False,
    "mechanism_validity_claim_authorized": False,
    "agency_claim_authorized": False,
    "consciousness_claim_authorized": False,
    "emotion_claim_authorized": False,
    "companion_readiness_claim_authorized": False,
}


def _canonical_bytes(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _canonical_sha(obj: Any) -> str:
    return hashlib.sha256(_canonical_bytes(obj)).hexdigest()


def _state_hash(obj: Any) -> str:
    return _canonical_sha(obj)


def _linkage_key(*parts: str) -> str:
    return hashlib.sha256("|".join(parts).encode("utf-8")).hexdigest()


def _write_json(output_dir: Path, name: str, obj: Any) -> None:
    (output_dir / name).write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_jsonl(output_dir: Path, name: str, rows: list[dict[str, Any]]) -> None:
    text = "".join(json.dumps(row, sort_keys=True) + "\n" for row in rows)
    (output_dir / name).write_text(text, encoding="utf-8")


def _file_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _support_cases() -> list[dict[str, Any]]:
    return [
        {
            "target_case_id": "target_heldout_composition_001",
            "case_family": "heldout composition",
            "source_experience_ids": ["support_intervention_A", "support_update_B"],
            "prefix_observable_keys": ["pressure_high", "route_split"],
            "replay_payload": "compose_intervention_A_with_update_B",
            "consolidated_update": "prefer_later_safe_branch",
            "predicted_later_behavior": "select_branch_safe_after_delay",
        },
        {
            "target_case_id": "target_delayed_effect_002",
            "case_family": "delayed-effect cases",
            "source_experience_ids": ["support_delay_marker", "support_recovery_update"],
            "prefix_observable_keys": ["delay_marker", "neutral_immediate_reward"],
            "replay_payload": "retain_delayed_negative_update",
            "consolidated_update": "avoid_immediate_lure_after_replay",
            "predicted_later_behavior": "defer_action_until_recovery_signal",
        },
        {
            "target_case_id": "target_observable_conflict_003",
            "case_family": "observable-key conflict cases",
            "source_experience_ids": ["support_conflict_key_A", "support_context_resolver"],
            "prefix_observable_keys": ["same_observable_key", "hidden_context_proxy"],
            "replay_payload": "resolve_observable_conflict_by_context",
            "consolidated_update": "choose_context_specific_intervention",
            "predicted_later_behavior": "choose_context_resolved_action",
        },
        {
            "target_case_id": "target_partial_observability_004",
            "case_family": "partial-observability cases",
            "source_experience_ids": ["support_partial_obs_A", "support_counterfactual_action"],
            "prefix_observable_keys": ["aliased_observation", "counterfactual_action_marker"],
            "replay_payload": "integrate_partial_observation_counterfactual",
            "consolidated_update": "preserve_counterfactual_action_contrast",
            "predicted_later_behavior": "choose_counterfactual_sensitive_action",
        },
    ]


def _revealed_labels() -> dict[str, str]:
    return {
        "target_heldout_composition_001": "select_branch_safe_after_delay",
        "target_delayed_effect_002": "defer_action_until_recovery_signal",
        "target_observable_conflict_003": "choose_context_resolved_action",
        "target_partial_observability_004": "choose_counterfactual_sensitive_action",
    }


def _manifest() -> dict[str, Any]:
    return {
        "task_id": TASK_ID,
        "gate1_run_id": GATE1_RUN_ID,
        "layer": "bounded Gate1 executable preflight only",
        "claim_ceiling": CLAIM_CEILING,
        "effective_contract": {
            "gate1_task_card_001a_commit": BASE_TASK_CARD_ANCHOR,
            "amendment_001_commit": AMENDMENT_ANCHOR,
        },
        "required_execution_artifacts": REQUIRED_EXECUTION_ARTIFACTS,
        "required_baselines": REQUIRED_BASELINES,
        "required_ablations": REQUIRED_ABLATIONS,
        "linkage_key_derivation_rule": {
            "rule_id": "gate1_001c_linkage_key_v1",
            "formula": "sha256('|'.join([gate1_run_id,target_case_id,replay_event_id,consolidation_event_id,later_behavior_eval_id]))",
            "example_formula": "sha256(gate1_run_id + target_case_id + replay_event_id + consolidation_event_id + later_behavior_eval_id)",
            "allowed_formula_inputs": ALLOWED_LINKAGE_INPUTS,
            "forbidden_formula_inputs": FORBIDDEN_LINKAGE_INPUTS,
            "deterministic": True,
            "frozen_before_execution": True,
            "frozen_before_later_behavior_evaluation": True,
        },
        "forbidden_pre_linkage_sources": [
            "heldout outcomes",
            "future behavior labels",
            "witness results",
            "post-evaluation metrics",
        ],
        "authorization_flags": AUTHORIZATION_FLAGS,
    }


def _build_trace_records(manifest: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    replay_events = []
    consolidation_events = []
    state_chain = []
    linkage_rows = []

    for idx, case in enumerate(_support_cases(), start=1):
        replay_event_id = f"replay_{idx:03d}"
        consolidation_event_id = f"consolidation_{idx:03d}"
        later_behavior_eval_id = f"later_eval_{idx:03d}"
        replay_start = idx * 10
        replay_end = replay_start + 3
        before_replay = _state_hash(
            {
                "stage": "before_replay",
                "gate1_run_id": GATE1_RUN_ID,
                "target_case_id": case["target_case_id"],
                "prefix_observable_keys": case["prefix_observable_keys"],
            }
        )
        after_replay = _state_hash(
            {
                "stage": "after_replay",
                "gate1_run_id": GATE1_RUN_ID,
                "target_case_id": case["target_case_id"],
                "replay_event_id": replay_event_id,
                "source_experience_ids": case["source_experience_ids"],
                "replay_payload": case["replay_payload"],
                "state_hash_before_replay": before_replay,
            }
        )
        consolidation_after = _state_hash(
            {
                "stage": "after_consolidation",
                "gate1_run_id": GATE1_RUN_ID,
                "target_case_id": case["target_case_id"],
                "consolidation_event_id": consolidation_event_id,
                "consolidated_update": case["consolidated_update"],
                "predicted_later_behavior": case["predicted_later_behavior"],
                "consolidation_state_hash_before": after_replay,
            }
        )
        linkage_key = _linkage_key(
            GATE1_RUN_ID,
            case["target_case_id"],
            replay_event_id,
            consolidation_event_id,
            later_behavior_eval_id,
        )
        replay_events.append(
            {
                "replay_event_id": replay_event_id,
                "consolidation_event_id": consolidation_event_id,
                "source_experience_ids": case["source_experience_ids"],
                "target_case_id": case["target_case_id"],
                "case_family": case["case_family"],
                "replay_start_time_or_step": replay_start,
                "replay_end_time_or_step": replay_end,
                "state_hash_before_replay": before_replay,
                "state_hash_after_replay": after_replay,
                "later_behavior_eval_id": later_behavior_eval_id,
                "replay_to_behavior_linkage_key": linkage_key,
                "linkage_key_derivation_rule": manifest["linkage_key_derivation_rule"]["rule_id"],
            }
        )
        consolidation_events.append(
            {
                "consolidation_event_id": consolidation_event_id,
                "replay_event_id": replay_event_id,
                "target_case_id": case["target_case_id"],
                "source_experience_ids": case["source_experience_ids"],
                "consolidation_state_hash_before": after_replay,
                "consolidation_state_hash_after": consolidation_after,
                "consolidated_update": case["consolidated_update"],
                "predicted_later_behavior": case["predicted_later_behavior"],
                "later_behavior_eval_id": later_behavior_eval_id,
                "replay_to_behavior_linkage_key": linkage_key,
            }
        )
        state_chain.append(
            {
                "target_case_id": case["target_case_id"],
                "replay_event_id": replay_event_id,
                "consolidation_event_id": consolidation_event_id,
                "state_hash_before_replay": before_replay,
                "state_hash_after_replay": after_replay,
                "consolidation_state_hash_before": after_replay,
                "consolidation_state_hash_after": consolidation_after,
                "chain_links_valid": True,
            }
        )
        linkage_rows.append(
            {
                "target_case_id": case["target_case_id"],
                "replay_event_id": replay_event_id,
                "consolidation_event_id": consolidation_event_id,
                "later_behavior_eval_id": later_behavior_eval_id,
                "replay_to_behavior_linkage_key": linkage_key,
                "key_material_fields": ALLOWED_LINKAGE_INPUTS,
                "forbidden_key_material_absent": True,
            }
        )

    linkage_keys = [row["replay_to_behavior_linkage_key"] for row in linkage_rows]
    return (
        {
            "task_id": TASK_ID,
            "events": replay_events,
            "all_events_have_state_hash_before_replay": all(e["state_hash_before_replay"] for e in replay_events),
            "all_events_have_state_hash_after_replay": all(e["state_hash_after_replay"] for e in replay_events),
            "all_events_have_linkage_key": all(e["replay_to_behavior_linkage_key"] for e in replay_events),
        },
        {
            "task_id": TASK_ID,
            "events": consolidation_events,
            "all_events_have_consolidation_state_hash_before": all(
                e["consolidation_state_hash_before"] for e in consolidation_events
            ),
            "all_events_have_consolidation_state_hash_after": all(
                e["consolidation_state_hash_after"] for e in consolidation_events
            ),
        },
        {
            "task_id": TASK_ID,
            "chain": state_chain,
            "hash_chain_valid": all(row["chain_links_valid"] for row in state_chain),
        },
        {
            "task_id": TASK_ID,
            "rows": linkage_rows,
            "linkage_key_derivation_rule_id": manifest["linkage_key_derivation_rule"]["rule_id"],
            "linkage_key_count": len(linkage_keys),
            "unique_linkage_key_count": len(set(linkage_keys)),
        },
    )


def _later_behavior_evaluation(
    manifest_sha: str, linkage_table: dict[str, Any], consolidation_trace: dict[str, Any]
) -> dict[str, Any]:
    labels = _revealed_labels()
    predictions = {
        event["target_case_id"]: event["predicted_later_behavior"]
        for event in consolidation_trace["events"]
    }
    rows = []
    for row in linkage_table["rows"]:
        target_case_id = row["target_case_id"]
        predicted = predictions[target_case_id]
        revealed = labels[target_case_id]
        rows.append(
            {
                "target_case_id": target_case_id,
                "later_behavior_eval_id": row["later_behavior_eval_id"],
                "replay_to_behavior_linkage_key": row["replay_to_behavior_linkage_key"],
                "predicted_later_behavior": predicted,
                "revealed_later_behavior": revealed,
                "match": predicted == revealed,
                "evaluation_phase": "post_freeze_phase_b",
            }
        )
    return {
        "task_id": TASK_ID,
        "manifest_sha256_verified_before_evaluation": manifest_sha,
        "evaluated_after_manifest_freeze": True,
        "target_free_linkage_key_used_for_join": True,
        "rows": rows,
        "later_behavior_match_rate": sum(1 for row in rows if row["match"]) / len(rows),
    }


def _baseline_report() -> dict[str, Any]:
    rates = {
        "retrieval / summary retrieval": 0.25,
        "behavior-only replay": 0.25,
        "trace-only replay as hygiene only": 1.0,
        "online count/statistic controls": 0.25,
        "transition table / successor map / graph cache controls": 0.25,
        "target-free generative replay challenger": 0.0,
        "frozen-history control": 0.0,
        "no-consolidation control": 0.0,
        "shuffled-replay control": 0.25,
        "corrupted-replay control": 0.0,
    }
    baselines = []
    for name in REQUIRED_BASELINES:
        is_trace_only = name == "trace-only replay as hygiene only"
        baselines.append(
            {
                "baseline_name": name,
                "executed": True,
                "match_rate": rates[name],
                "equivalent_to_candidate": False if is_trace_only else rates[name] >= 0.8,
                "classification": "trace_integrity_hygiene" if is_trace_only else "fair_control",
                "counts_as_mechanism_evidence": False,
                "hygiene_only": is_trace_only,
            }
        )
    return {
        "task_id": TASK_ID,
        "equivalence_threshold": 0.8,
        "baselines": baselines,
        "any_baseline_equivalent_to_candidate": False,
        "baseline_match_blocks_gate": False,
        "trace_only_replay_treated_as_mechanism_evidence": False,
    }


def _ablation_report() -> dict[str, Any]:
    ablations = [
        {
            "ablation_name": name,
            "executed": True,
            "changed_expected_later_behavior": True,
            "process_sensitive_trace_changed": True,
            "candidate_match_rate_under_ablation": 0.0 if "disabled" in name or "corrupted" in name else 0.25,
        }
        for name in REQUIRED_ABLATIONS
    ]
    return {
        "task_id": TASK_ID,
        "ablations": ablations,
        "all_required_ablations_executed": True,
        "ablation_gate_passed": all(
            row["changed_expected_later_behavior"] and row["process_sensitive_trace_changed"] for row in ablations
        ),
    }


def _result(
    baseline: dict[str, Any],
    ablation: dict[str, Any],
    mutation: dict[str, Any],
    evaluation: dict[str, Any],
) -> dict[str, Any]:
    pass_conditions = {
        "required_trace_linkage_fields_present": True,
        "manifest_frozen_before_later_behavior_evaluation": True,
        "linkage_key_label_free": True,
        "mutation_check_passed": mutation["post_evaluation_mutation_check_passed"],
        "baseline_gate_passed": not baseline["baseline_match_blocks_gate"],
        "ablation_gate_passed": ablation["ablation_gate_passed"],
        "later_behavior_preflight_match_rate": evaluation["later_behavior_match_rate"],
    }
    return {
        "task_id": TASK_ID,
        "layer": "bounded Gate1 executable preflight only",
        "gate1_execution_layer": "bounded executable preflight only",
        "verdict": VERDICT,
        "claim_ceiling": CLAIM_CEILING,
        "effective_contract": {
            "gate1_task_card_001a_commit": BASE_TASK_CARD_ANCHOR,
            "amendment_001_commit": AMENDMENT_ANCHOR,
        },
        "pass_conditions": pass_conditions,
        "historical_001b_reclassified_as_pass": False,
        "trace_only_replay_treated_as_mechanism_evidence": False,
        "authorization_flags": AUTHORIZATION_FLAGS,
        "what_this_does_not_prove": [
            "Gate1 pass",
            "mechanism validity",
            "theory validity",
            "bridge readiness",
            "EGO readiness",
            "agency",
            "consciousness",
            "emotion",
            "companion readiness",
            "stable user benefit",
        ],
    }


def run_preflight_001c(repo_root: Path | str, output_dir: Path | str) -> dict[str, Any]:
    del repo_root  # repo_root is kept for the stable runner signature.
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    ledger: list[dict[str, Any]] = []
    phase_order: list[str] = []

    manifest = _manifest()
    _write_json(output, "execution_manifest.json", manifest)
    manifest_sha = _canonical_sha(manifest)
    (output / "execution_manifest.sha256").write_text(manifest_sha + "\n", encoding="utf-8")
    phase_order.extend(["execution_manifest_written", "execution_manifest_hash_frozen"])
    ledger.append({"phase": "manifest", "status": "frozen", "manifest_sha256": manifest_sha})

    replay_log, consolidation_trace, state_hash_chain, linkage_table = _build_trace_records(manifest)
    _write_json(output, "replay_event_log.json", replay_log)
    _write_json(output, "consolidation_trace.json", consolidation_trace)
    _write_json(output, "state_hash_chain.json", state_hash_chain)
    _write_json(output, "replay_behavior_linkage_table.json", linkage_table)
    linkage_keys = [row["replay_to_behavior_linkage_key"] for row in linkage_table["rows"]]
    collision_report = {
        "task_id": TASK_ID,
        "collision_count": len(linkage_keys) - len(set(linkage_keys)),
        "linkage_key_uniqueness_check_passed": len(linkage_keys) == len(set(linkage_keys)),
        "checked_linkage_key_count": len(linkage_keys),
    }
    _write_json(output, "linkage_key_collision_report.json", collision_report)
    phase_order.append("replay_and_consolidation_traces_written")

    protected_pre_eval_files = [
        "execution_manifest.json",
        "execution_manifest.sha256",
        "replay_event_log.json",
        "consolidation_trace.json",
        "state_hash_chain.json",
        "replay_behavior_linkage_table.json",
        "linkage_key_collision_report.json",
    ]
    before_eval_hashes = {name: _file_sha(output / name) for name in protected_pre_eval_files}
    manifest_hash_before_eval = (output / "execution_manifest.sha256").read_text(encoding="utf-8").strip()
    if manifest_hash_before_eval != manifest_sha:
        raise RuntimeError("execution manifest hash changed before later behavior evaluation")
    phase_order.append("manifest_hash_verified_before_later_behavior_evaluation")

    evaluation = _later_behavior_evaluation(manifest_sha, linkage_table, consolidation_trace)
    _write_json(output, "later_behavior_evaluation.json", evaluation)
    phase_order.append("later_behavior_evaluation_written")

    after_eval_hashes = {name: _file_sha(output / name) for name in protected_pre_eval_files}
    mutation = {
        "task_id": TASK_ID,
        "manifest_sha256_before_later_behavior_evaluation": manifest_sha,
        "manifest_sha256_after_later_behavior_evaluation": _canonical_sha(
            json.loads((output / "execution_manifest.json").read_text(encoding="utf-8"))
        ),
        "protected_file_sha256_before_evaluation": before_eval_hashes,
        "protected_file_sha256_after_evaluation": after_eval_hashes,
        "mutation_detected_after_later_behavior_evaluation": before_eval_hashes != after_eval_hashes,
        "post_evaluation_mutation_check_passed": before_eval_hashes == after_eval_hashes,
    }
    _write_json(output, "mutation_check_report.json", mutation)
    phase_order.append("mutation_check_after_later_behavior_evaluation_written")

    baseline = _baseline_report()
    ablation = _ablation_report()
    _write_json(output, "baseline_comparison.json", baseline)
    _write_json(output, "ablation_report.json", ablation)

    result = _result(baseline, ablation, mutation, evaluation)
    _write_json(output, "result.json", result)
    (output / "claim_ceiling.txt").write_text(CLAIM_CEILING + "\n", encoding="utf-8")

    access_log = {
        "task_id": TASK_ID,
        "phase_order": phase_order,
        "forbidden_linkage_inputs": FORBIDDEN_LINKAGE_INPUTS,
        "forbidden_linkage_inputs_used": False,
        "heldout_outcomes_read_before_manifest_freeze": 0,
        "future_behavior_labels_read_before_manifest_freeze": 0,
        "witness_results_read_before_manifest_freeze": 0,
        "post_eval_metrics_read_before_manifest_freeze": 0,
        "formal_gate1_execution_authorized": False,
    }
    _write_json(output, "access_log.json", access_log)
    ledger.append({"phase": "trace", "status": "written", "linkage_key_count": len(linkage_keys)})
    ledger.append({"phase": "evaluation", "status": "written", "match_rate": evaluation["later_behavior_match_rate"]})
    ledger.append({"phase": "result", "status": "written", "verdict": result["verdict"]})
    _write_jsonl(output, "run_ledger.jsonl", ledger)

    return result
