from __future__ import annotations

import subprocess
from pathlib import Path

from . import core


def _write_json(path: Path, data: object) -> None:
    path.write_text(core.pretty_json(data) + "\n", encoding="utf-8")


def _write_jsonl(path: Path, rows: list[dict]) -> None:
    path.write_text("\n".join(core.stable_json(row) for row in rows) + "\n", encoding="utf-8")


def _git_head_bytes(repo_root: Path, relative_path: str) -> bytes | None:
    result = subprocess.run(
        ["git", "show", f"HEAD:{relative_path}"],
        cwd=repo_root,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        return None
    return result.stdout


def _verify_hard_inputs(repo_root: Path) -> dict:
    current_hashes: dict[str, str] = {}
    head_hashes: dict[str, str | None] = {}
    verified = True
    for relative_path in core.HARD_INPUT_PATHS:
        current = (repo_root / relative_path).read_bytes()
        current_hash = core.sha256_bytes(current)
        head = _git_head_bytes(repo_root, relative_path)
        head_hash = core.sha256_bytes(head) if head is not None else None
        current_hashes[relative_path] = current_hash
        head_hashes[relative_path] = head_hash
        verified = verified and head_hash == current_hash
    return {
        "hard_distribution_001a_input_sha256": current_hashes,
        "hard_distribution_001a_git_head_sha256": head_hashes,
        "hard_distribution_001a_inputs_verified_against_git_head": verified,
    }


def _verify_predecessor_hashes(repo_root: Path, hard_frozen_inputs: dict) -> bool:
    for relative_path, expected_hash in hard_frozen_inputs["frozen_input_sha256"].items():
        if core.sha256_bytes((repo_root / relative_path).read_bytes()) != expected_hash:
            return False
    return True


def _load_source_inputs(repo_root: Path) -> dict:
    source_root = repo_root / "artifacts" / "process_intervention_hard_distribution_001a"
    return {
        "hard_distribution_spec": core.load_json(source_root / "hard_distribution_spec.json"),
        "hard_distribution_frozen_inputs": core.load_json(source_root / "frozen_inputs.json"),
        "distribution_shortcut_audit": core.load_json(source_root / "distribution_shortcut_audit.json"),
        "fair_control_budget_spec": core.load_json(source_root / "fair_control_budget_spec.json"),
        "heldout_composition_manifest": core.load_json(source_root / "heldout_composition_manifest.json"),
        "ablation_hook_manifest": core.load_json(source_root / "ablation_hook_manifest.json"),
    }


def run_preflight_001b(repo_root: Path | str, output_dir: Path | str) -> dict:
    root = Path(repo_root)
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    source_inputs = _load_source_inputs(root)
    hard_input_verification = _verify_hard_inputs(root)
    predecessor_hashes_verified = _verify_predecessor_hashes(root, source_inputs["hard_distribution_frozen_inputs"])
    frozen_verified = (
        hard_input_verification["hard_distribution_001a_inputs_verified_against_git_head"]
        and predecessor_hashes_verified
    )

    spec = source_inputs["hard_distribution_spec"]
    cases = spec["case_families"]
    trace = core.build_trace(cases)
    replay = core.replay_trace(trace)
    control_comparison = core.evaluate_controls(cases)
    heldout = core.heldout_report(cases, control_comparison)
    ablations = core.ablation_report(spec)
    baseline = core.baseline_comparison(control_comparison)
    result = core.result_payload(
        frozen_verified=frozen_verified,
        control_comparison=control_comparison,
        replay=replay,
        ablations=ablations,
        heldout=heldout,
    )
    frozen_inputs = {
        "task_id": core.TASK_ID,
        "source_task_id": core.SOURCE_TASK_ID,
        "claim_ceiling": core.CLAIM_CEILING,
        "freeze_before_any_execution": True,
        "execution_authorized_by_source_001a": False,
        "old_001b_or_rca_artifacts_edited": False,
        "predecessor_hashes_verified": predecessor_hashes_verified,
        **hard_input_verification,
        "authorization_flags": dict(core.AUTHORIZATION_FLAGS),
    }

    _write_json(out / "frozen_inputs.json", frozen_inputs)
    _write_jsonl(out / "trace.jsonl", trace)
    _write_json(out / "replay_report.json", replay)
    _write_json(out / "control_comparison.json", control_comparison)
    _write_json(out / "baseline_comparison.json", baseline)
    _write_json(out / "ablation_report.json", ablations)
    _write_json(out / "heldout_report.json", heldout)
    _write_json(out / "result.json", result)
    if result["verdict"] != "process_intervention_hard_distribution_001b_bounded_pass":
        _write_json(out / "failure_manifest.json", core.failure_manifest(result))
    (out / "claim_ceiling.txt").write_text(core.CLAIM_CEILING + "\n", encoding="utf-8")
    return result


def main() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    result = run_preflight_001b(
        repo_root=repo_root,
        output_dir=repo_root / "artifacts" / "process_intervention_hard_distribution_001b",
    )
    print(core.pretty_json(result))
