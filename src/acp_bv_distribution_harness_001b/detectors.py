from __future__ import annotations

from dataclasses import asdict, dataclass
from copy import deepcopy
from pathlib import Path
from typing import Any

from . import baselines, candidate, classify_b3_delta, code_path_hash, coupling, generator, leakage_scanner, replay, source_boundary, source_path_for


@dataclass
class DetectorControl:
    detector_name: str
    expected_intervention: str
    expected_verdict_before: str
    expected_verdict_after: str
    expected_flip: bool
    actual_verdict_before: str
    actual_verdict_after: str
    producer_function: str
    input_fixture_episode_ids: list[str]
    run_id: str
    seed: int
    source_path: str
    code_path_hash: str
    artifact_path: str
    real_detector_invoked: bool = False
    actual_verdict_source: str = ""
    discriminates_clean_and_intervened: bool = False


def summarize_detector_controls(controls: list[DetectorControl]) -> dict[str, Any]:
    rows = []
    for control in controls:
        payload = asdict(control)
        payload["predeclared_expected_flip"] = control.expected_flip
        payload["actual_flip"] = control.actual_verdict_before != control.actual_verdict_after
        payload["actual_flip_matches_predeclared"] = payload["actual_flip"] == control.expected_flip
        payload["discriminates_clean_and_intervened"] = (
            control.real_detector_invoked
            and control.actual_verdict_before == control.expected_verdict_before
            and control.actual_verdict_after == control.expected_verdict_after
        )
        rows.append(payload)
    all_match = all(row["actual_flip_matches_predeclared"] for row in rows)
    all_discriminated = all(row["discriminates_clean_and_intervened"] for row in rows)
    blocking = None if all_match and all_discriminated else "blocked_by_non_fail_able_detector"
    return {
        "producer_function": "summarize_detector_controls",
        "controls": rows,
        "all_controls_executed": len(rows) == 8,
        "all_actual_flips_match_predeclared": all_match,
        "all_controls_discriminated": all_discriminated,
        "blocking_verdict": blocking,
        "verdict_if_any_mismatch": "blocked_by_non_fail_able_detector",
    }


def _lookup_complete_dataset(seed: int) -> dict[str, Any]:
    dataset = generator.generate_distribution(seed=seed, heldout_count=128)
    heldout = []
    for index in range(128):
        row = deepcopy(dataset["train"][index % len(dataset["train"])])
        row["split"] = "heldout"
        row["context_id"] = f"lookup-complete.ctx.{seed}.{index:03d}"
        row["episode_id"] = f"lookup-complete.ep.{seed}.{index:03d}"
        heldout.append(row)
    dataset["heldout"] = heldout
    return dataset


def _novelty_verdict(dataset: dict[str, Any]) -> str:
    manifest = generator.distribution_manifest(dataset)
    return "novelty_floor_passed" if manifest["constraints_satisfied"] else "blocked_by_insufficient_heldout_novelty"


def _baseline_tie_verdict(delta: float) -> str:
    return "blocked_by_baseline_equivalence" if classify_b3_delta(delta) == "baseline_equivalent" else "clean"


def _factorized_verdict(datasets: list[dict[str, Any]]) -> str:
    report = baselines.factorization_report(datasets)
    return "blocked_by_factorized_lookup_equivalence" if report["blocked_by_factorized_lookup_equivalence"] else "clean"


def _multi_seed_verdict(deltas: list[float]) -> str:
    return (
        "blocked_by_unstable_or_noise_level_effect"
        if any(classify_b3_delta(delta) == "baseline_equivalent" for delta in deltas)
        else "clean"
    )


def _majority_fit(train: list[dict[str, Any]]) -> dict[str, Any]:
    by_action: dict[str, dict[str, int]] = {}
    for action in generator.ACTIONS:
        counts = {}
        for episode in train:
            if episode["chosen_action"] != action:
                continue
            truth = episode["truth_by_action"][action]
            key = (truth["boundary_state"], truth["viability_state"])
            counts[key] = counts.get(key, 0) + 1
        if counts:
            boundary, viability = sorted(counts.items(), key=lambda row: (-row[1], row[0]))[0][0]
            by_action[action] = {"boundary_state": boundary, "viability_state": viability}
    return {"by_action": by_action, "fallback": {"boundary_state": -1, "viability_state": -1}}


def _majority_predict(state: dict[str, Any], observation: dict[str, Any], action: str) -> dict[str, int]:
    return state["by_action"].get(action, state["fallback"])


def _oracle_fit(train: list[dict[str, Any]]) -> dict[str, Any]:
    return {"fit_count": len(train)}


def _oracle_predict(state: dict[str, Any], observation: dict[str, Any], action: str) -> dict[str, int]:
    return generator.truth_for({"observation": observation}, action)


def _coupling_verdict(*, predict_fn: Any, fit_fn: Any, seed: int, output_artifact_path: Path) -> str:
    dataset = generator.generate_distribution(seed=seed)
    report = coupling.detect_candidate_truth_coupling(
        predict_fn=predict_fn,
        fit_fn=fit_fn,
        truth_fn=generator.truth_for,
        datasets=[dataset],
        seed=seed,
        run_id=f"detector-control-coupling-{seed}",
        output_artifact_path=output_artifact_path,
    )
    return report["verdict"] if report["verdict"].startswith("blocked_by_") else "clean"


def _leakage_verdict(datasets: list[dict[str, Any]], *, run_id: str, output_artifact_path: Path) -> str:
    report = leakage_scanner.run_solvability_preflight(
        datasets=datasets,
        run_id=run_id,
        output_artifact_path=output_artifact_path,
    )
    return report["verdict"] if report["verdict"].startswith("blocked_by_") else "clean"


def _leaking_dataset(seed: int) -> dict[str, Any]:
    dataset = generator.generate_distribution(seed=seed)
    for split in ("train", "heldout"):
        for episode in dataset[split]:
            action = episode["chosen_action"]
            episode["observation"]["hidden_truth_label"] = episode["truth_by_action"][action]["viability_state"]
    return dataset


def _source_boundary_verdict(repo_root: Path, *, tampered: bool, run_id: str, output_artifact_path: Path) -> str:
    pin = source_boundary.create_source_pin(repo_root=repo_root, run_id=run_id, output_artifact_path=output_artifact_path)
    if not tampered:
        return "source_boundary_pass" if pin["verification"]["passed"] else "blocked_by_source_boundary_failure"
    control = source_boundary.run_tamper_after_anchor_control(pin, repo_root=repo_root)
    return control["verdict_after_intervention"]


def _replay_verdict(*, tampered: bool, seed: int, run_id: str, output_artifact_path: Path) -> str:
    dataset = generator.generate_distribution(seed=seed)
    state = candidate.fit_candidate(dataset["train"])
    outputs = candidate.run_candidate(state, dataset["heldout"])
    if tampered:
        outputs = deepcopy(outputs)
        outputs[0]["prediction"] = {"boundary_state": -1, "viability_state": -1}
    report = replay.recompute_candidate_outputs(
        serialized_state=state,
        episodes=dataset["heldout"],
        candidate_outputs=outputs,
        run_id=run_id,
        output_artifact_path=output_artifact_path,
    )
    return report["verdict"]


def _control_from_actuals(
    *,
    detector_name: str,
    intervention: str,
    expected_before: str,
    expected_after: str,
    actual_before: str,
    actual_after: str,
    run_id: str,
    seed: int,
    artifact_path: Path,
) -> DetectorControl:
    return DetectorControl(
        detector_name=detector_name,
        expected_intervention=intervention,
        expected_verdict_before=expected_before,
        expected_verdict_after=expected_after,
        expected_flip=True,
        actual_verdict_before=actual_before,
        actual_verdict_after=actual_after,
        producer_function="acp_bv_distribution_harness_001b.detectors.run_detector_failability_controls",
        input_fixture_episode_ids=[f"control.{detector_name}.{seed}"],
        run_id=f"{run_id}-{detector_name}",
        seed=seed,
        source_path=source_path_for(run_detector_failability_controls),
        code_path_hash=code_path_hash(run_detector_failability_controls),
        artifact_path=artifact_path.as_posix(),
        real_detector_invoked=True,
        actual_verdict_source="callable_clean_and_intervened_detector_paths",
        discriminates_clean_and_intervened=actual_before == expected_before and actual_after == expected_after,
    )


def run_detector_failability_controls(
    *,
    run_id: str,
    output_artifact_path: Path,
    seed: int = 1009,
    repo_root: Path | None = None,
) -> dict[str, Any]:
    repo_root = (repo_root or Path.cwd()).resolve()
    clean_dataset = generator.generate_distribution(seed=seed)
    lookup_complete_dataset = _lookup_complete_dataset(seed)
    clean_datasets = [clean_dataset]
    leaking_datasets = [_leaking_dataset(seed)]
    controls = [
        _control_from_actuals(
            detector_name="novelty_floor_detector",
            intervention="replace heldout with lookup-complete seen components",
            expected_before="clean",
            expected_after="blocked_by_insufficient_heldout_novelty",
            actual_before="clean" if _novelty_verdict(clean_dataset) == "novelty_floor_passed" else _novelty_verdict(clean_dataset),
            actual_after=_novelty_verdict(lookup_complete_dataset),
            run_id=run_id,
            seed=seed,
            artifact_path=output_artifact_path,
        ),
        _control_from_actuals(
            detector_name="baseline_tie_detector",
            intervention="force strongest fair baseline score to equal candidate",
            expected_before="clean",
            expected_after="blocked_by_baseline_equivalence",
            actual_before=_baseline_tie_verdict(0.10),
            actual_after=_baseline_tie_verdict(0.0),
            run_id=run_id,
            seed=seed,
            artifact_path=output_artifact_path,
        ),
        _control_from_actuals(
            detector_name="factorized_lookup_equivalence_detector",
            intervention="declare lookup-complete hidden factorization axis",
            expected_before="clean",
            expected_after="blocked_by_factorized_lookup_equivalence",
            actual_before=_factorized_verdict(clean_datasets),
            actual_after=_factorized_verdict([lookup_complete_dataset]),
            run_id=run_id,
            seed=seed,
            artifact_path=output_artifact_path,
        ),
        _control_from_actuals(
            detector_name="multi_seed_stability_detector",
            intervention="collapse one seed into equivalence band",
            expected_before="clean",
            expected_after="blocked_by_unstable_or_noise_level_effect",
            actual_before=_multi_seed_verdict([0.08, 0.07, 0.09]),
            actual_after=_multi_seed_verdict([0.08, 0.0, 0.09]),
            run_id=run_id,
            seed=seed,
            artifact_path=output_artifact_path,
        ),
        _control_from_actuals(
            detector_name="candidate_truth_coupling_detector",
            intervention="route candidate and truth through shared answer helper",
            expected_before="clean",
            expected_after="blocked_by_candidate_truth_coupling",
            actual_before=_coupling_verdict(
                predict_fn=_majority_predict,
                fit_fn=_majority_fit,
                seed=seed,
                output_artifact_path=output_artifact_path,
            ),
            actual_after=_coupling_verdict(
                predict_fn=_oracle_predict,
                fit_fn=_oracle_fit,
                seed=seed,
                output_artifact_path=output_artifact_path,
            ),
            run_id=run_id,
            seed=seed,
            artifact_path=output_artifact_path,
        ),
        _control_from_actuals(
            detector_name="leakage_detector",
            intervention="inject runtime hidden-truth structural variant",
            expected_before="clean",
            expected_after="blocked_by_leaking_oracle_invalidity",
            actual_before=_leakage_verdict(
                clean_datasets,
                run_id=f"{run_id}-leakage-clean",
                output_artifact_path=output_artifact_path,
            ),
            actual_after=_leakage_verdict(
                leaking_datasets,
                run_id=f"{run_id}-leakage-intervened",
                output_artifact_path=output_artifact_path,
            ),
            run_id=run_id,
            seed=seed,
            artifact_path=output_artifact_path,
        ),
        _control_from_actuals(
            detector_name="source_boundary_detector",
            intervention="tamper after source anchor",
            expected_before="source_boundary_pass",
            expected_after="blocked_by_source_boundary_failure",
            actual_before=_source_boundary_verdict(
                repo_root,
                tampered=False,
                run_id=f"{run_id}-source-clean",
                output_artifact_path=output_artifact_path,
            ),
            actual_after=_source_boundary_verdict(
                repo_root,
                tampered=True,
                run_id=f"{run_id}-source-intervened",
                output_artifact_path=output_artifact_path,
            ),
            run_id=run_id,
            seed=seed,
            artifact_path=output_artifact_path,
        ),
        _control_from_actuals(
            detector_name="replay_recomputation_detector",
            intervention="change stored candidate prediction after replay source state is frozen",
            expected_before="replay_recomputed",
            expected_after="blocked_by_replay_recomputation_failure",
            actual_before=_replay_verdict(
                tampered=False,
                seed=seed,
                run_id=f"{run_id}-replay-clean",
                output_artifact_path=output_artifact_path,
            ),
            actual_after=_replay_verdict(
                tampered=True,
                seed=seed,
                run_id=f"{run_id}-replay-intervened",
                output_artifact_path=output_artifact_path,
            ),
            run_id=run_id,
            seed=seed,
            artifact_path=output_artifact_path,
        ),
    ]
    return summarize_detector_controls(controls)
