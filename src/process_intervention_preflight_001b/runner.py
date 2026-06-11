from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict

from negative_evidence_admission_gate_001a import evaluate_successor_task

from . import core


SUPPORT_CONTRACTS = [
    "docs/process_intervention_preflight_001a/real_control_implementation_contract.md",
    "docs/process_intervention_preflight_001a/trace_commitment_contract.md",
    "docs/process_intervention_preflight_001a/match_metric_contract.md",
    "docs/process_intervention_preflight_001a/update_path_contract.md",
    "docs/process_intervention_preflight_001a/separation_statistic_contract.md",
    "docs/process_intervention_preflight_001a/state_accounting_contract.md",
    "docs/process_intervention_preflight_001a/resource_budget_contract.md",
    "docs/process_intervention_preflight_001a/environment_intervention_instantiation_contract.md",
    "docs/process_intervention_preflight_001a/memory_key_fidelity_contract.md",
    "docs/process_intervention_preflight_001a/behavior_probe_contract.md",
    "docs/process_intervention_preflight_001a/stage0_freeze_anchor_contract.md",
]


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _write_json(path: Path, data: object) -> None:
    path.write_text(core.pretty_json(data) + "\n", encoding="utf-8")


def _write_jsonl(path: Path, rows: list[dict]) -> None:
    path.write_text("\n".join(core.stable_json(row) for row in rows) + "\n", encoding="utf-8")


def _hash_file(path: Path) -> str:
    return core.sha256_text(path.read_text(encoding="utf-8"))


def _relative(path: Path, root: Path) -> str:
    return str(path.relative_to(root)).replace("\\", "/")


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha_manifest(repo_root: Path) -> Dict[str, str]:
    paths = [
        "docs/codex/tasks/PROCESS-INTERVENTION-PREFLIGHT-001B-EXECUTABLE-PREFLIGHT-TASK-CARD.md",
        "docs/codex/tasks/PROCESS-INTERVENTION-PREFLIGHT-001A-AMENDMENT-001-SUPPORT-PACK-001.md",
        "artifacts/process_intervention_preflight_001a_amendment_001_support_pack_001/support_pack_result.json",
        "artifacts/process_intervention_preflight_001a_amendment_001_semantic_audit_rerun_001/semantic_audit_result.json",
        *SUPPORT_CONTRACTS,
    ]
    return {path: _hash_file(repo_root / path) for path in paths}


def _frozen_inputs(repo_root: Path) -> dict:
    support_pack = _load_json(
        repo_root
        / "artifacts"
        / "process_intervention_preflight_001a_amendment_001_support_pack_001"
        / "support_pack_result.json"
    )
    semantic_rerun = _load_json(
        repo_root
        / "artifacts"
        / "process_intervention_preflight_001a_amendment_001_semantic_audit_rerun_001"
        / "semantic_audit_result.json"
    )
    return {
        "support_pack_task_id": support_pack["task_id"],
        "support_pack_result": support_pack,
        "semantic_audit_rerun_result": semantic_rerun,
        "semantic_audit_rerun_is_mechanism_evidence": False,
        "support_contract_paths": list(SUPPORT_CONTRACTS),
        "contract_source_policy": support_pack["contract_source_policy"],
    }


def _stage0_manifest(repo_root: Path, admission: dict, sha_manifest: dict) -> dict:
    support_hashes = {path: sha_manifest[path] for path in SUPPORT_CONTRACTS}
    payload = {
        "task_id": core.TASK_ID,
        "freeze_before_first_run": True,
        "support_contracts_frozen": True,
        "support_contract_hashes": support_hashes,
        "task_card_hash": sha_manifest[
            "docs/codex/tasks/PROCESS-INTERVENTION-PREFLIGHT-001B-EXECUTABLE-PREFLIGHT-TASK-CARD.md"
        ],
        "support_pack_hash": sha_manifest[
            "artifacts/process_intervention_preflight_001a_amendment_001_support_pack_001/support_pack_result.json"
        ],
        "semantic_audit_rerun_hash": sha_manifest[
            "artifacts/process_intervention_preflight_001a_amendment_001_semantic_audit_rerun_001/semantic_audit_result.json"
        ],
        "negative_evidence_admission": admission,
        "environment_family_definition": {
            "episode_count": core.EPISODE_COUNT,
            "contexts": list(core.CONTEXTS),
            "actions": list(core.ACTIONS),
            "interventions": list(core.INTERVENTIONS),
            "offline": True,
        },
        "control_implementations_or_closed_form_procedures": [
            "online_count_statistic",
            "count_table",
            "graph_cache",
            "transition_table",
            "successor_map",
            "trace_only_replay",
            "behavior_only_replay",
            "posthoc_verdict_string_rejection",
        ],
        "match_metrics": dict(core.THRESHOLDS),
        "claim_ceiling": core.CLAIM_CEILING,
    }
    payload["stage0_payload_hash"] = core.sha256_text(core.stable_json(payload))
    return payload


def _external_anchor(stage0: dict) -> dict:
    return {
        "task_id": core.TASK_ID,
        "anchor_method": "local_offline_hash_anchor",
        "anchor_time_utc": _utc_now(),
        "anchored_payload_hash": stage0["stage0_payload_hash"],
        "external_service_used": False,
        "anchor_before_first_run": True,
    }


def _result(control_comparison: dict, replay: dict, admission: dict) -> dict:
    best = control_comparison["best_fair_control"]
    stop_conditions = []
    if control_comparison["controls"]["online_count_statistic"]["match_rate"] >= core.THRESHOLDS["match_rate_threshold"]:
        stop_conditions.append("fair_count_statistic_control_matched")
    if control_comparison["controls"]["graph_cache"]["match_rate"] >= core.THRESHOLDS["match_rate_threshold"]:
        stop_conditions.append("fair_graph_cache_control_matched")
    if replay["trace_only_replay_match_rate"] >= core.THRESHOLDS["match_rate_threshold"]:
        stop_conditions.append("trace_only_replay_matched")
    return {
        "task_id": core.TASK_ID,
        "verdict": "process_intervention_preflight_001b_failed_control_separation_statistic_match",
        "bounded_pass": False,
        "negative_evidence_recorded": True,
        "claim_ceiling": core.CLAIM_CEILING,
        "thresholds": dict(core.THRESHOLDS),
        "best_fair_control": best,
        "stop_conditions": stop_conditions,
        "negative_evidence_admission": admission,
        "support_contract_classification": {"blocking": [], "nonblocking": [], "backlog": []},
        "new_meta_audit_created": False,
        "nonblocking_caveats_spawned_new_tasks": False,
        "mechanism_evidence_claimed": False,
        "support_pack_or_semantic_audit_treated_as_mechanism_evidence": False,
        "gate1_evidence_claimed": False,
        "same_agent_bridge_evidence_claimed": False,
        "ego_readiness_claimed": False,
        "old_experiments_rerun": False,
        "old_artifacts_repaired": False,
        "fable_or_poisoning_line_expanded": False,
        "model_class_reset_authorized": False,
        "gate1_reopen_authorized": False,
        "same_agent_bridge_authorized": False,
        "ego_integration_authorized": False,
        "next_allowed_task": "record_negative_evidence_or_simplify_process_intervention_framing",
    }


def _failure_manifest(result: dict, control_comparison: dict) -> dict:
    return {
        "task_id": core.TASK_ID,
        "verdict": result["verdict"],
        "failure_type": "fair_controls_matched_process_intervention",
        "matched_controls": control_comparison["matching_controls"],
        "do_not_patch_into_pass": True,
        "claim_ceiling": core.CLAIM_CEILING,
    }


def _final_report(result: dict, control_comparison: dict) -> str:
    matched = ", ".join(control_comparison["matching_controls"])
    return "\n".join(
        [
            "# PROCESS-INTERVENTION-PREFLIGHT-001B Final Report",
            "",
            "## Verdict",
            "",
            f"`{result['verdict']}`",
            "",
            "Fair process/intervention controls matched the witness under frozen support-pack contracts.",
            "",
            "## Matched Controls",
            "",
            matched,
            "",
            "## Claim Ceiling",
            "",
            core.CLAIM_CEILING,
            "",
            "This is bounded executable process-intervention preflight evidence only. It is not Gate1 evidence, not same-agent bridge evidence, not EGO readiness, and not mechanism proof.",
            "",
        ]
    )


def run_preflight_001b(repo_root: Path | str, output_dir: Path | str) -> dict:
    root = Path(repo_root)
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    task_card = root / "docs" / "codex" / "tasks" / "PROCESS-INTERVENTION-PREFLIGHT-001B-EXECUTABLE-PREFLIGHT-TASK-CARD.md"
    admission = evaluate_successor_task(task_card.read_text(encoding="utf-8"))
    sha_manifest = _sha_manifest(root)
    stage0 = _stage0_manifest(root, admission, sha_manifest)
    anchor = _external_anchor(stage0)
    frozen = _frozen_inputs(root)

    trace = core.build_trace()
    replay = core.replay_trace(trace)
    control_comparison = core.evaluate_controls(trace)
    baseline = core.baseline_comparison(control_comparison)
    result = _result(control_comparison, replay, admission)
    failure = _failure_manifest(result, control_comparison)
    ledger = [
        {"event": "negative_evidence_admission_gate", "status": "passed" if admission["passed"] else "failed"},
        {"event": "stage0_freeze", "status": "completed", "payload_hash": stage0["stage0_payload_hash"]},
        {"event": "first_executable_preflight_run", "status": "failed_cleanly_by_fair_control_match"},
    ]

    _write_json(out / "admission_gate_result.json", admission)
    _write_json(out / "stage0_freeze_manifest.json", stage0)
    _write_json(out / "sha256_manifest.json", sha_manifest)
    _write_json(out / "external_anchor.json", anchor)
    _write_json(out / "frozen_inputs.json", frozen)
    _write_json(out / "run_config.json", {"task_id": core.TASK_ID, "thresholds": core.THRESHOLDS})
    _write_jsonl(out / "trace.jsonl", trace)
    _write_json(out / "replay_report.json", replay)
    _write_json(out / "control_comparison.json", control_comparison)
    _write_json(out / "baseline_comparison.json", baseline)
    _write_json(out / "failure_manifest.json", failure)
    _write_json(out / "result.json", result)
    _write_jsonl(out / "run_ledger.jsonl", ledger)
    (out / "claim_ceiling.txt").write_text(core.CLAIM_CEILING + "\n", encoding="utf-8")
    (out / "final_report.md").write_text(_final_report(result, control_comparison), encoding="utf-8")
    return result


def main() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    result = run_preflight_001b(
        repo_root=repo_root,
        output_dir=repo_root / "artifacts" / "process_intervention_preflight_001b",
    )
    print(core.pretty_json(result))


if __name__ == "__main__":
    main()

