from __future__ import annotations

import subprocess
from pathlib import Path

from . import core


def _write_json(path: Path, data: object) -> None:
    path.write_text(core.pretty_json(data) + "\n", encoding="utf-8")


def _write_text(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8")


def _git_show_bytes(repo_root: Path, commit: str, relative_path: str) -> bytes:
    result = subprocess.run(
        ["git", "show", f"{commit}:{relative_path}"],
        cwd=repo_root,
        capture_output=True,
        check=True,
    )
    return result.stdout


def _git_path_clean(repo_root: Path, relative_path: str) -> bool:
    result = subprocess.run(
        ["git", "diff", "--quiet", "--", relative_path],
        cwd=repo_root,
        check=False,
    )
    return result.returncode == 0


def _verify_old_artifacts_against_anchor(repo_root: Path) -> dict:
    artifact_hashes: dict[str, dict] = {}
    unchanged = True
    for relative_path in core.OLD_ARTIFACT_PATHS:
        current = _git_show_bytes(repo_root, "HEAD", relative_path)
        anchor = _git_show_bytes(repo_root, core.FREEZE_ANCHOR_COMMIT, relative_path)
        current_sha = core.sha256_bytes(current)
        anchor_sha = core.sha256_bytes(anchor)
        worktree_clean = _git_path_clean(repo_root, relative_path)
        unchanged = unchanged and current_sha == anchor_sha and worktree_clean
        artifact_hashes[relative_path] = {
            "current_sha256": current_sha,
            "anchor_sha256": anchor_sha,
            "matches_anchor": current_sha == anchor_sha,
            "worktree_clean_against_head": worktree_clean,
        }
    return {
        "task_id": core.TASK_ID,
        "freeze_anchor_commit": core.FREEZE_ANCHOR_COMMIT,
        "old_artifacts_unchanged_from_anchor": unchanged,
        "old_001b_artifacts_edited": any(
            not record["matches_anchor"]
            for path, record in artifact_hashes.items()
            if "process_intervention_hard_distribution_001b/" in path
        ),
        "old_rca_artifacts_edited": any(
            not record["matches_anchor"]
            for path, record in artifact_hashes.items()
            if "001b_trace_replay_rca_001a" in path
        ),
        "old_001c_artifacts_edited": any(
            not record["matches_anchor"]
            for path, record in artifact_hashes.items()
            if "process_intervention_hard_distribution_001c_replay_gate_revision" in path
        ),
        "artifact_hashes": artifact_hashes,
    }


def _load_json(repo_root: Path, relative_path: str) -> dict:
    return core.load_json(repo_root / relative_path)


def run_preflight_001d(repo_root: Path | str, output_dir: Path | str) -> dict:
    root = Path(repo_root)
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    # The orchestrator prepares a sanitized object. The Phase A challenger only
    # receives that object through AccessFirewall, not direct artifact paths.
    spec = _load_json(root, "artifacts/process_intervention_hard_distribution_001a/hard_distribution_spec.json")
    phase_a_inputs = core.build_phase_a_inputs(spec)
    prediction_commit, phase_a_log = core.run_phase_a_target_free_challenger(phase_a_inputs)

    prediction_commit_path = out / "prediction_commit.json"
    _write_json(prediction_commit_path, prediction_commit)
    prediction_commit_sha = core.sha256_bytes(prediction_commit_path.read_bytes())
    _write_text(out / "prediction_commit.sha256", prediction_commit_sha + "\n")
    phase_a_log["prediction_commit_hash_frozen_before_reveal"] = True
    phase_a_log["prediction_commit_sha256"] = prediction_commit_sha

    phase_order = [
        "phase_a_prediction_commit_written",
        "phase_a_prediction_commit_hash_frozen",
        "phase_b_reveal_started",
    ]

    reveal_cases = spec["case_families"]
    evaluation = core.evaluate_phase_b(
        prediction_commit,
        reveal_cases,
        before_hash=prediction_commit_sha,
        after_hash=core.sha256_bytes(prediction_commit_path.read_bytes()),
    )
    phase_order.append("phase_b_evaluation_written")
    phase_b_log = {
        "target_reveal_after_hash_freeze": True,
        "revealed_inputs": ["target_trace", "heldout_labels", "frozen_prediction_commit.json"],
        "may_write_phase_a_prediction_commit": False,
        "phase_a_prediction_commit_rewritten": False,
        "prediction_commit_sha256_after_evaluation": evaluation["prediction_commit_sha256_verification"][
            "after_evaluation_sha256"
        ],
    }
    access_log = {
        "task_id": core.TASK_ID,
        "phase_order": phase_order,
        "phase_a": phase_a_log,
        "phase_b": phase_b_log,
        "orchestrator_note": (
            "The orchestrator derived a sanitized Phase A object from the frozen 001A distribution; "
            "the challenger itself read only AccessFirewall allowlist keys."
        ),
    }

    result_001b = _load_json(root, "artifacts/process_intervention_hard_distribution_001b/result.json")
    control_comparison = _load_json(root, "artifacts/process_intervention_hard_distribution_001b/control_comparison.json")
    ablation_001b = _load_json(root, "artifacts/process_intervention_hard_distribution_001b/ablation_report.json")
    rca = _load_json(
        root,
        "artifacts/process_intervention_hard_distribution_001b_trace_replay_rca_001a/replay_control_adjudication.json",
    )
    result_001c = _load_json(
        root,
        "artifacts/process_intervention_hard_distribution_001c_replay_gate_revision/replay_gate_revision_result.json",
    )

    old_artifacts = _verify_old_artifacts_against_anchor(root)
    controls = core.preserved_controls_report(control_comparison)
    ablations = core.ablation_report(ablation_001b)
    baseline = core.baseline_comparison_report(result_001b, rca, result_001c, evaluation)
    replay = core.replay_report(access_log, evaluation)
    result = core.result_payload(
        evaluation=evaluation,
        access_log=access_log,
        old_artifacts=old_artifacts,
        ablations=ablations,
    )

    _write_json(out / "access_log.json", access_log)
    _write_json(out / "evaluation_report.json", evaluation)
    _write_json(out / "preserved_controls.json", controls)
    _write_json(out / "old_artifact_anchor_verification.json", old_artifacts)
    _write_json(out / "baseline_comparison.json", baseline)
    _write_json(out / "ablation_report.json", ablations)
    _write_json(out / "replay_report.json", replay)
    _write_json(out / "result.json", result)
    if result["verdict"] != "process_intervention_hard_distribution_001d_bounded_replay_gate_pass":
        _write_json(
            out / "failure_manifest.json",
            {
                "task_id": core.TASK_ID,
                "verdict": result["verdict"],
                "stop_conditions": result["stop_conditions"],
                "claim_ceiling": core.CLAIM_CEILING,
                "authorization_flags": dict(core.AUTHORIZATION_FLAGS),
            },
        )
    _write_text(out / "claim_ceiling.txt", core.CLAIM_CEILING + "\n")
    return result


def main() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    result = run_preflight_001d(
        repo_root=repo_root,
        output_dir=repo_root
        / "artifacts"
        / "process_intervention_hard_distribution_001d_target_free_generative_replay_challenger",
    )
    print(core.pretty_json(result))
