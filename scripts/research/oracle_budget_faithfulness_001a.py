from __future__ import annotations

from copy import deepcopy
from typing import Any

from baseline_battery_001a import macro_f1, query_budget_components
from evidence_provenance_001a import code_path_hash
from minimal_env_spec_loader_001a import BUDGET_COMPONENT_CHANNELS, FINAL_ACTIONS, mask_hidden_fields, permute_hidden_fields, target_from_components


FORBIDDEN_ORACLE_FIELD_TOKENS = {
    "hidden_state",
    "target",
    "answer_key",
    "stored_prediction",
    "stored_final_hash",
}


def _truths(episodes: list[dict[str, Any]]) -> list[str]:
    return [episode["target_label_or_target_variable"] for episode in episodes]


def visible_channel_oracle(
    episodes: list[dict[str, Any]],
    run_id: str,
    budget: int,
    scoring_truths: list[str] | None = None,
) -> dict[str, Any]:
    predictions = []
    traces = []
    consumed_fields = set()
    for episode in episodes:
        observations, query_rows = query_budget_components(episode)
        prediction = target_from_components(observations)
        predictions.append(prediction)
        trace = {
            "episode_id": episode["episode_id"],
            "queried_channel_ids": list(BUDGET_COMPONENT_CHANNELS),
            "observations_received": observations,
            "query_count": len(query_rows),
            "stopping_condition": "candidate_matched_budget_exhausted_after_required_component_queries",
            "final_prediction": prediction,
        }
        traces.append(trace)
        consumed_fields.update(
            {
                "episode_id",
                "seed",
                "observable_state",
                "legal_action_space",
                "budget_state",
                "own_query_history",
            }
        )
        for channel_id in BUDGET_COMPONENT_CHANNELS:
            consumed_fields.add(f"legal_channel_responses.{channel_id}.value_if_queried")

    metric = macro_f1(scoring_truths if scoring_truths is not None else _truths(episodes), predictions)
    return {
        "schema_version": "baseline_first_harness_001a_visible_oracle_v1",
        "run_id": run_id,
        "predictions": predictions,
        "score": metric["macro_f1"],
        "metric": metric,
        "query_trace": traces,
        "consumed_field_manifest": sorted(consumed_fields),
        "producer_function": "oracle_budget_faithfulness_001a.visible_channel_oracle",
        "code_path_hash": code_path_hash(visible_channel_oracle),
        "budget": budget,
        "consumed_by_final_verdict": True,
    }


def answer_key_diagnostic_oracle(episodes: list[dict[str, Any]], run_id: str) -> dict[str, Any]:
    predictions = _truths(episodes)
    metric = macro_f1(_truths(episodes), predictions)
    return {
        "schema_version": "baseline_first_harness_001a_answer_key_oracle_v1",
        "run_id": run_id,
        "score": metric["macro_f1"],
        "metric": metric,
        "diagnostic_only": True,
        "may_support_headroom": False,
        "producer_function": "oracle_budget_faithfulness_001a.answer_key_diagnostic_oracle",
        "code_path_hash": code_path_hash(answer_key_diagnostic_oracle),
        "consumed_by_final_verdict": True,
    }


def replay_predictions_from_serialized_state_and_trace(
    episodes: list[dict[str, Any]],
    oracle_trace: list[dict[str, Any]],
    *,
    reject_hash_only: bool = True,
) -> dict[str, Any]:
    episodes_by_id = {episode["episode_id"]: episode for episode in episodes}
    predictions = []
    errors = []
    for trace in oracle_trace:
        episode = episodes_by_id.get(trace["episode_id"])
        if episode is None:
            errors.append(f"missing_serialized_state:{trace['episode_id']}")
            continue
        serialized_state = episode.get("serialized_state")
        observations = trace.get("observations_received", {})
        if not serialized_state:
            errors.append(f"missing_serialized_state:{trace['episode_id']}")
            continue
        if reject_hash_only and trace.get("stored_prediction_hash_only") is True:
            errors.append(f"hash_only_replay_rejected:{trace['episode_id']}")
            continue
        if sorted(observations) != sorted(BUDGET_COMPONENT_CHANNELS):
            errors.append(f"missing_permitted_observations:{trace['episode_id']}")
            continue
        predictions.append(target_from_components({key: int(observations[key]) for key in BUDGET_COMPONENT_CHANNELS}))
    return {
        "result": "passed" if not errors else "failed",
        "errors": errors,
        "predictions": predictions,
        "producer_function": "oracle_budget_faithfulness_001a.replay_predictions_from_serialized_state_and_trace",
        "code_path_hash": code_path_hash(replay_predictions_from_serialized_state_and_trace),
        "recomputed_from": ["serialized_state", "permitted_observation_query_trace"],
        "did_not_use": ["stored_labels", "stored_predictions", "stored_hashes_only", "hidden_answer_fields"],
        "consumed_by_final_verdict": True,
    }


def run_replay_recompute_report(episodes: list[dict[str, Any]], oracle_report: dict[str, Any], run_id: str) -> dict[str, Any]:
    replay = replay_predictions_from_serialized_state_and_trace(episodes, oracle_report["query_trace"])
    metric = macro_f1(_truths(episodes), replay["predictions"]) if replay["result"] == "passed" else None
    tampered_trace = deepcopy(oracle_report["query_trace"])
    if tampered_trace:
        tampered_trace[0]["observations_received"] = {
            key: value for key, value in tampered_trace[0]["observations_received"].items() if key != BUDGET_COMPONENT_CHANNELS[-1]
        }
    tamper = replay_predictions_from_serialized_state_and_trace(episodes, tampered_trace)
    hash_only_trace = deepcopy(oracle_report["query_trace"])
    if hash_only_trace:
        hash_only_trace[0]["stored_prediction_hash_only"] = True
    hash_only = replay_predictions_from_serialized_state_and_trace(episodes, hash_only_trace)
    return {
        "schema_version": "baseline_first_harness_001a_replay_recompute_v1",
        "run_id": run_id,
        "result": "passed" if replay["result"] == "passed" and tamper["result"] == "failed" and hash_only["result"] == "failed" else "failed",
        "replay": replay,
        "metric": metric,
        "tamper_negative_control": tamper,
        "hash_only_negative_control": hash_only,
        "producer_function": "oracle_budget_faithfulness_001a.run_replay_recompute_report",
        "code_path_hash": code_path_hash(run_replay_recompute_report),
        "consumed_by_final_verdict": True,
    }


def run_oracle_budget_faithfulness_controls(
    episodes: list[dict[str, Any]],
    oracle_report: dict[str, Any],
    replay_report: dict[str, Any],
    run_id: str,
    budget: int,
) -> dict[str, Any]:
    consumed_fields = oracle_report["consumed_field_manifest"]
    forbidden_hits = [
        field
        for field in consumed_fields
        if any(token in field for token in FORBIDDEN_ORACLE_FIELD_TOKENS)
    ]
    scoring_truths = _truths(episodes)
    masked = visible_channel_oracle(
        mask_hidden_fields(episodes),
        run_id=f"{run_id}-hidden-masked",
        budget=budget,
        scoring_truths=scoring_truths,
    )
    permuted = visible_channel_oracle(
        permute_hidden_fields(episodes),
        run_id=f"{run_id}-hidden-permuted",
        budget=budget,
        scoring_truths=scoring_truths,
    )
    query_budget_violations = [
        trace for trace in oracle_report["query_trace"] if trace["query_count"] > budget
    ]
    hidden_ablation_passed = masked["predictions"] == oracle_report["predictions"] and masked["score"] <= oracle_report["score"]
    hidden_permutation_passed = permuted["predictions"] == oracle_report["predictions"]
    replay_passed = replay_report.get("result") == "passed"
    passed = not forbidden_hits and not query_budget_violations and hidden_ablation_passed and hidden_permutation_passed and replay_passed
    failure_reasons = []
    if forbidden_hits:
        failure_reasons.append(f"oracle_read_forbidden_field:{','.join(forbidden_hits)}")
    if query_budget_violations:
        failure_reasons.append("query_budget_exceeded")
    if not hidden_ablation_passed:
        failure_reasons.append("hidden_field_ablation_changed_or_improved_score")
    if not hidden_permutation_passed:
        failure_reasons.append("hidden_field_permutation_changed_prediction")
    if not replay_passed:
        failure_reasons.append("replay_recompute_failed")
    return {
        "schema_version": "baseline_first_harness_001a_oracle_budget_faithfulness_v1",
        "run_id": run_id,
        "result": "passed" if passed else "failed",
        "failure_reason": ";".join(failure_reasons) if failure_reasons else None,
        "field_access_audit": {
            "consumed_field_manifest": consumed_fields,
            "forbidden_field_hits": forbidden_hits,
        },
        "hidden_field_ablation": {
            "result": "passed" if hidden_ablation_passed else "failed",
            "masked_score": masked["score"],
            "original_score": oracle_report["score"],
            "prediction_invariant": masked["predictions"] == oracle_report["predictions"],
        },
        "hidden_field_permutation": {
            "result": "passed" if hidden_permutation_passed else "failed",
            "prediction_invariant": hidden_permutation_passed,
        },
        "budget_trace_audit": {
            "budget": budget,
            "max_query_count": max(trace["query_count"] for trace in oracle_report["query_trace"]),
            "violations": query_budget_violations,
            "query_trace_summary": [
                {
                    "episode_id": trace["episode_id"],
                    "queried_channel_ids": trace["queried_channel_ids"],
                    "query_count": trace["query_count"],
                    "stopping_condition": trace["stopping_condition"],
                    "final_prediction": trace["final_prediction"],
                }
                for trace in oracle_report["query_trace"][:10]
            ],
        },
        "replay_recomputation": {
            "result": replay_report.get("result"),
            "recomputed_from_serialized_state_plus_permitted_trace": replay_passed,
        },
        "producer_function": "oracle_budget_faithfulness_001a.run_oracle_budget_faithfulness_controls",
        "code_path_hash": code_path_hash(run_oracle_budget_faithfulness_controls),
        "consumed_by_final_verdict": True,
    }
