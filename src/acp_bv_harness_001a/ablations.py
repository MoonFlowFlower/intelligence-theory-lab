from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from . import environment
from .common import classify_delta, provenance_for, seed_ids, stable_run_command, write_jsonl
from .scoring import score_prediction_rows


def _rerun_with_intervention(bundle: dict[str, Any], intervention: str) -> dict[str, Any]:
    mutated = deepcopy(bundle)
    state = mutated["serialized_state"]
    if intervention == "remove_action_input":
        for output in mutated["candidate_outputs"]:
            output["prediction"] = environment.reference_candidate_predict(
                state,
                next(ep["observation"] for ep in mutated["episodes"] if ep["episode_id"] == output["episode_id"]),
                "repair",
            )
            output["counterfactual_predictions"] = {}
    elif intervention == "shuffle_action_labels":
        replacement = {"probe": "shield", "shield": "repair", "repair": "probe"}
        for output in mutated["candidate_outputs"]:
            episode = next(ep for ep in mutated["episodes"] if ep["episode_id"] == output["episode_id"])
            output["prediction"] = environment.reference_candidate_predict(
                state,
                episode["observation"],
                replacement[output["action"]],
            )
            output["counterfactual_predictions"] = {}
    elif intervention == "replace_boundary_state":
        for episode in mutated["episodes"]:
            episode["observation"]["signal"] = "mid"
        for episode, output in zip(mutated["episodes"], mutated["candidate_outputs"]):
            output["prediction"] = environment.reference_candidate_predict(state, episode["observation"], output["action"])
            output["counterfactual_predictions"] = {}
    elif intervention == "replace_viability_state":
        for episode in mutated["episodes"]:
            episode["observation"]["risk"] = 0
        for episode, output in zip(mutated["episodes"], mutated["candidate_outputs"]):
            output["prediction"] = environment.reference_candidate_predict(state, episode["observation"], output["action"])
            output["counterfactual_predictions"] = {}
    else:
        raise ValueError(f"unknown intervention: {intervention}")
    return mutated


def run_ablation_reruns(
    bundle: dict[str, Any],
    *,
    repo_root: Path,
    output_dir: Path,
    output_artifact_path: Path,
    run_id: str,
    before_metric: float,
) -> dict[str, Any]:
    interventions = [
        "remove_action_input",
        "shuffle_action_labels",
        "replace_boundary_state",
        "replace_viability_state",
    ]
    rows = []
    trace_dir = output_dir / "ablation_traces"
    for intervention in interventions:
        rerun = _rerun_with_intervention(bundle, intervention)
        trace_path = trace_dir / f"{intervention}.jsonl"
        write_jsonl(trace_path, rerun["candidate_outputs"])
        after_metric = score_prediction_rows(
            rerun["episodes"],
            rerun["candidate_outputs"],
            environment.held_out_truth_generator,
        )
        effect_size = round(abs(before_metric - after_metric), 6)
        rows.append(
            {
                "intervention_target": intervention,
                "rerun_command": stable_run_command(
                    "acp_bv_harness_001a.runner",
                    output_dir,
                    f"{run_id}-{intervention}",
                ),
                "run_id": f"{run_id}-{intervention}",
                "regenerated_trace_path": trace_path.relative_to(repo_root).as_posix()
                if trace_path.is_relative_to(repo_root)
                else trace_path.as_posix(),
                "before_metric": before_metric,
                "after_metric": after_metric,
                "effect_size": effect_size,
                "threshold_classification": classify_delta(effect_size),
                "episodes_rerun": True,
                "report_field_editing_used": False,
                "provenance": provenance_for(
                    run_ablation_reruns,
                    repo_root=repo_root,
                    inputs={"intervention": intervention, "bundle_id": bundle["bundle_id"]},
                    run_id=f"{run_id}-{intervention}",
                    seed_context_episode_ids=seed_ids(bundle["episodes"]),
                    aggregation_method="rerun_under_real_intervention_then_rescore",
                    output_artifact_path=output_artifact_path,
                ),
            }
        )
    return {
        "producer_function": "run_ablation_reruns",
        "ablations": rows,
        "all_rerun": all(row["episodes_rerun"] for row in rows),
        "report_field_editing_used": False,
    }
