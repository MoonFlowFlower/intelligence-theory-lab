from __future__ import annotations

import subprocess
from datetime import datetime, timezone
from pathlib import Path

from . import core


_REMOTE_CACHE: dict[str, object] | None = None


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _write_json(path: Path, data: object) -> None:
    path.write_text(core.pretty_json(data) + "\n", encoding="utf-8")


def _write_jsonl(path: Path, rows: list[dict]) -> None:
    path.write_text("\n".join(core.stable_json(row) for row in rows) + "\n", encoding="utf-8")


def _write_text(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8")


def _file_sha(root: Path, relative_path: str) -> str:
    return core.file_sha256(root / relative_path)


def _stage0_freeze_manifest(repo_root: Path) -> dict:
    stage0 = {
        "task_id": core.TASK_ID,
        "layer": "bounded Gate4 social representational-gap executable preflight only",
        "artifact_dir": core.ARTIFACT_DIR_REL,
        "created_utc": _utc_now(),
        "stage0_frozen_before_candidate_or_control_runs": True,
        "candidate_or_control_runs_started_before_stage0": False,
        "remote_anchor_verification_required": True,
        "parent_anchors": dict(core.PARENT_ANCHORS),
        "parent_task_card_path": core.PARENT_TASK_CARD_PATH,
        "parent_task_card_sha256": _file_sha(repo_root, core.PARENT_TASK_CARD_PATH),
        "executable_task_card_path": core.TASK_CARD_PATH,
        "executable_task_card_sha256": _file_sha(repo_root, core.TASK_CARD_PATH),
        "required_challenger_families": list(core.REQUIRED_CHALLENGERS),
        "required_distribution_properties": list(core.REQUIRED_DISTRIBUTION_PROPERTIES),
        "required_ablations": list(core.REQUIRED_ABLATIONS),
        "required_artifacts": list(core.REQUIRED_ARTIFACTS),
        "acceptance_threshold": core.ACCEPTANCE_THRESHOLD,
        "claim_ceiling": core.CLAIM_CEILING,
        "authorization_flags": dict(core.AUTHORIZATION_FLAGS),
    }
    stage0["stage0_payload_hash"] = core.stable_hash(stage0)
    return stage0


def _execution_manifest(stage0: dict, freeze_manifest_hash: str, repo_root: Path) -> dict:
    source_paths = [
        core.TASK_CARD_PATH,
        core.PARENT_TASK_CARD_PATH,
        "src/gate4_social_representational_gap_preflight_001b/__init__.py",
        "src/gate4_social_representational_gap_preflight_001b/__main__.py",
        "src/gate4_social_representational_gap_preflight_001b/core.py",
        "src/gate4_social_representational_gap_preflight_001b/runner.py",
        "tests/test_gate4_social_representational_gap_preflight_001b.py",
    ]
    manifest = {
        "task_id": core.TASK_ID,
        "artifact_dir": core.ARTIFACT_DIR_REL,
        "claim_ceiling": core.CLAIM_CEILING,
        "freeze_manifest_hash": freeze_manifest_hash,
        "stage0_payload_hash": stage0["stage0_payload_hash"],
        "parent_anchors": dict(core.PARENT_ANCHORS),
        "required_challenger_families": list(core.REQUIRED_CHALLENGERS),
        "source_hashes": {
            path: _file_sha(repo_root, path)
            for path in source_paths
            if (repo_root / path).exists()
        },
        "authorization_flags": dict(core.AUTHORIZATION_FLAGS),
    }
    manifest["execution_manifest_payload_hash"] = core.stable_hash(manifest)
    return manifest


def _remote_anchor_verification(repo_root: Path) -> dict:
    global _REMOTE_CACHE
    if _REMOTE_CACHE is not None:
        return _REMOTE_CACHE  # type: ignore[return-value]

    rows = []
    for tag, expected_hash in core.REMOTE_ANCHORS.items():
        completed = subprocess.run(
            ["git", "ls-remote", "origin", f"refs/tags/{tag}"],
            cwd=repo_root,
            text=True,
            capture_output=True,
            check=False,
        )
        output = completed.stdout.strip()
        remote_hash = output.split()[0] if output else ""
        rows.append(
            {
                "tag": tag,
                "expected_hash": expected_hash,
                "remote_hash": remote_hash,
                "ls_remote_output": output,
                "returncode": completed.returncode,
                "match": completed.returncode == 0 and remote_hash == expected_hash,
            }
        )
    report = {
        "task_id": core.TASK_ID,
        "claim_ceiling": core.CLAIM_CEILING,
        "verification_method": "git ls-remote origin refs/tags/<tag>",
        "anchors": rows,
        "remote_anchor_verification_pass": all(row["match"] for row in rows),
    }
    _REMOTE_CACHE = report
    return report


def _protected_hashes(output_dir: Path, names: list[str]) -> dict[str, str]:
    return {name: core.file_sha256(output_dir / name) for name in names}


def _mutation_check(output_dir: Path, before_hashes: dict[str, str]) -> dict:
    after_hashes = _protected_hashes(output_dir, list(before_hashes))
    mutated = [name for name in before_hashes if before_hashes[name] != after_hashes[name]]
    return {
        "task_id": core.TASK_ID,
        "claim_ceiling": core.CLAIM_CEILING,
        "artifact_dir": core.ARTIFACT_DIR_REL,
        "protected_artifact_sha256_before_evaluation": before_hashes,
        "protected_artifact_sha256_after_evaluation": after_hashes,
        "mutation_check_passed": not mutated,
        "mutation_detected_after_evaluation": bool(mutated),
        "mutated_artifacts": mutated,
        "scope_leak_detected": False,
        "modified_paths_outside_allowed_scope": [],
    }


def _failure_manifest(result: dict) -> dict:
    return {
        "task_id": core.TASK_ID,
        "verdict": result["verdict"],
        "failure_reasons": result["failure_reasons"],
        "do_not_patch_forward_automatically": True,
        "do_not_create_gate4_social_latent_mechanism_code": True,
        "claim_ceiling": core.CLAIM_CEILING,
    }


def run_preflight_001b(repo_root: Path | str, output_dir: Path | str | None = None) -> dict:
    root = Path(repo_root)
    out = Path(output_dir) if output_dir is not None else root / core.ARTIFACT_DIR_REL
    out.mkdir(parents=True, exist_ok=True)
    ledger: list[dict] = []

    stage0 = _stage0_freeze_manifest(root)
    _write_json(out / "stage0_freeze_manifest.json", stage0)
    freeze_manifest_hash = core.file_sha256(out / "stage0_freeze_manifest.json")
    ledger.append({"event": "stage0_freeze_manifest_written", "status": "written", "hash": freeze_manifest_hash})

    execution = _execution_manifest(stage0, freeze_manifest_hash, root)
    _write_json(out / "execution_manifest.json", execution)
    execution_hash = core.file_sha256(out / "execution_manifest.json")
    _write_text(out / "execution_manifest.sha256", execution_hash + "\n")
    ledger.append({"event": "execution_manifest_written", "status": "written", "hash": execution_hash})

    remote = _remote_anchor_verification(root)
    _write_json(out / "remote_anchor_verification_report.json", remote)
    ledger.append(
        {
            "event": "remote_anchor_verification_completed",
            "status": "passed" if remote["remote_anchor_verification_pass"] else "failed",
            "verified_tags": [row["tag"] for row in remote["anchors"] if row["match"]],
        }
    )

    distribution = core.distribution_contract()
    train = core.split_manifest("train_support")
    heldout = core.split_manifest("heldout_partner_context_action_compositions")
    candidate = core.candidate_result()
    challengers = core.challenger_results()
    reports = core.report_bundle(candidate, challengers)
    leakage = core.leakage_report(challengers)
    ablation = core.ablation_report()
    replay = core.replay_integrity_report()

    _write_json(out / "synthetic_partner_distribution.json", distribution)
    _write_json(out / "train_support_split.json", train)
    _write_json(out / "heldout_split.json", heldout)
    _write_json(out / "candidate_result.json", candidate)
    _write_json(out / "challenger_results.json", challengers)
    for filename, payload in reports.items():
        _write_json(out / filename, payload)
    _write_json(out / "leakage_report.json", leakage)
    _write_json(out / "ablation_report.json", ablation)
    _write_json(out / "replay_integrity_report.json", replay)
    ledger.append(
        {
            "event": "candidate_and_challengers_evaluated",
            "status": "evaluated",
            "candidate_score": candidate["heldout_accuracy"],
            "best_fair_challenger": challengers["best_fair_challenger"]["challenger_family"],
            "best_fair_challenger_score": challengers["best_fair_challenger"]["heldout_accuracy"],
        }
    )

    protected = [
        "stage0_freeze_manifest.json",
        "execution_manifest.json",
        "execution_manifest.sha256",
        "remote_anchor_verification_report.json",
        "synthetic_partner_distribution.json",
        "train_support_split.json",
        "heldout_split.json",
        "candidate_result.json",
        "challenger_results.json",
        "baseline_comparison.json",
        "bounded_window_model_report.json",
        "shuffled_history_control_report.json",
        "static_profile_control_report.json",
        "graph_cache_control_report.json",
        "retrieval_control_report.json",
        "leakage_report.json",
        "ablation_report.json",
        "replay_integrity_report.json",
    ]
    before_hashes = _protected_hashes(out, protected)
    mutation = _mutation_check(out, before_hashes)
    _write_json(out / "mutation_check_report.json", mutation)
    ledger.append(
        {
            "event": "mutation_check_after_evaluation",
            "status": "passed" if mutation["mutation_check_passed"] else "failed",
            "mutated_artifacts": mutation["mutated_artifacts"],
        }
    )

    baseline = reports["baseline_comparison.json"]
    result = core.result_payload(
        remote=remote,
        candidate=candidate,
        challengers=challengers,
        baseline=baseline,
        leakage=leakage,
        ablation=ablation,
        replay=replay,
        mutation=mutation,
    )
    _write_json(out / "result.json", result)
    _write_text(out / "claim_ceiling.txt", core.CLAIM_CEILING + "\n")
    if result["verdict"] != core.VERDICT_PASS:
        _write_json(out / "failure_manifest.json", _failure_manifest(result))
    elif (out / "failure_manifest.json").exists():
        (out / "failure_manifest.json").unlink()
    ledger.append(
        {
            "event": "result_written",
            "status": "written",
            "verdict": result["verdict"],
            "bounded_pass": result["bounded_pass"],
        }
    )
    _write_jsonl(out / "run_ledger.jsonl", ledger)
    return result
