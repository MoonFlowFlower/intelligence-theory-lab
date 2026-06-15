from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


TASK_ID = "PRESERVE-EVIDENCE-ADMISSION-VERIFIER-001B-BYPASS-AUDIT-001A"
ANCHOR_UNDER_AUDIT = "14aa837e1db8265f9ec64c745c46d9a70c1eaaa3"
REPAIR_PARENT = "b1070058736235dc897d4fa9e693f48f06e63059"
CALLABLE_RULE = "callable_result_digest_v1"
FORGED_DIGEST = hashlib.sha256(
    b"candidate-controlled forged digest admitted by verifier 001B"
).hexdigest()
CLAIM_CEILING = "verifier-bypass negative evidence and route downgrade only"

ARTIFACT_DIR = Path(__file__).resolve().parent
REPO_ROOT = ARTIFACT_DIR.parents[1]

sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "src"))

from evidence_admission_verifier_001a.core import verify_bundle, write_admission_artifacts


def constant_forged_digest(
    input_paths: list[Path],
    output_dir: Path,
    run_id: str,
    aggregation_rule: str,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "forged": True,
        "producer_type": "constant_without_row_injection",
        "run_id": run_id,
        "aggregation_rule": aggregation_rule,
        "input_count": len(input_paths),
        "output_digest": FORGED_DIGEST,
    }
    _write_json(output_dir / "constant_forged_digest.json", payload)
    return {
        "aggregation_rule": aggregation_rule,
        "metric_value": 999,
        "output_digest": FORGED_DIGEST,
        "output_row_count": 1,
    }


def row_echo_forged_digest(
    input_paths: list[Path],
    output_dir: Path,
    run_id: str,
    aggregation_rule: str,
    row: dict[str, Any],
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    declared = str(row["expected_output_digest"]).removeprefix("sha256:")
    payload = {
        "forged": True,
        "producer_type": "row_echo_uses_candidate_declared_digest",
        "run_id": run_id,
        "aggregation_rule": aggregation_rule,
        "input_count": len(input_paths),
        "declared_expected_output_digest": row["expected_output_digest"],
        "output_digest": declared,
    }
    _write_json(output_dir / "row_echo_forged_digest.json", payload)
    return {
        "aggregation_rule": aggregation_rule,
        "metric_value": 999,
        "output_digest": declared,
        "output_row_count": 1,
    }


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha256_file(path: Path) -> str:
    return _sha256_bytes(path.read_bytes())


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, sort_keys=True, indent=2) + "\n", encoding="utf-8")


def _write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(json.dumps(row, sort_keys=True) + "\n" for row in rows),
        encoding="utf-8",
    )


def _module_path(function_name: str) -> str:
    return (
        "artifacts.evidence_admission_verifier_001b_bypass_audit_001a."
        f"poc_forged_digest_admission:{function_name}"
    )


def _git(args: list[str]) -> dict[str, Any]:
    proc = subprocess.run(
        ["git", *args],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    return {
        "command": "git " + " ".join(args),
        "returncode": proc.returncode,
        "stdout": proc.stdout.strip(),
        "stderr": proc.stderr.strip(),
    }


def _metric(
    metric_id: str,
    role: str,
    producer: str,
    bundle: Path,
    code_hash: str,
) -> dict[str, Any]:
    return {
        "aggregation_rule": CALLABLE_RULE,
        "code_path_hash": "sha256:" + code_hash,
        "computed_not_literal": True,
        "counterfactual_pair_ids_consumed": ["forged-pair-1"],
        "episode_ids": ["forged-episode-1"],
        "evidence_role": role,
        "expected_metric_value": 999,
        "expected_output_digest": "sha256:" + FORGED_DIGEST,
        "expected_output_row_count": 1,
        "failure_path_available": True,
        "heldout_context_ids_consumed": ["forged-heldout-1"],
        "input_artifact_hashes": {
            "inputs/episodes.jsonl": "sha256:"
            + _sha256_file(bundle / "inputs" / "episodes.jsonl")
        },
        "input_artifact_paths": ["inputs/episodes.jsonl"],
        "input_row_count": 1,
        "metric_id": metric_id,
        "metric_name": metric_id.replace("_", " "),
        "output_artifact_path": f"outputs/{metric_id}.jsonl",
        "output_row_ids": [f"{metric_id}-forged-row-1"],
        "producer_function": producer,
        "producer_module": producer.split(":", 1)[0],
        "recompute_contract": CALLABLE_RULE,
        "run_id": f"forged-{metric_id}",
        "seed_ids": ["forged-seed-1"],
        "threshold_frozen_before_run": True,
        "threshold_used": 0.5,
        "train_context_ids_consumed": ["forged-train-1"],
    }


def _write_forged_bundle(bundle: Path, producer: str, code_hash: str) -> None:
    bundle.mkdir(parents=True, exist_ok=True)
    (bundle / "inputs").mkdir(parents=True, exist_ok=True)
    (bundle / "inputs" / "episodes.jsonl").write_text(
        json.dumps(
            {
                "episode_id": "forged-episode-1",
                "observation": "the candidate controls producer output and expected digest",
            },
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    (bundle / "claim_ceiling.txt").write_text(CLAIM_CEILING + "\n", encoding="utf-8")
    (bundle / "report.md").write_text(
        "forged report text; admission must not rest on this narrative\n",
        encoding="utf-8",
    )
    _write_json(
        bundle / "result.json",
        {
            "admitted_for_citation": True,
            "candidate_controlled_digest": "sha256:" + FORGED_DIGEST,
            "verdict": "forged_candidate_claims_pass",
        },
    )

    metric_specs = [
        ("candidate_score", "candidate_metric"),
        ("baseline_score", "baseline_metric"),
        ("ablation_score", "ablation_metric"),
        ("leakage_scan", "leakage_metric"),
        ("behavior_replay", "replay_metric"),
    ]
    _write_jsonl(
        bundle / "invocation_ledger.jsonl",
        [
            {
                "call_id": f"call-{metric_id}",
                "called": True,
                "function_name": metric_id,
                "input_artifacts": ["inputs/episodes.jsonl"],
                "output_artifact": f"outputs/{metric_id}.jsonl",
                "producer_function": producer,
                "run_id": f"forged-{metric_id}",
            }
            for metric_id, _role in metric_specs
        ],
    )
    _write_jsonl(
        bundle / "metric_provenance.jsonl",
        [
            _metric(metric_id, role, producer, bundle, code_hash)
            for metric_id, role in metric_specs
        ],
    )
    _write_jsonl(
        bundle / "baseline_invocations.jsonl",
        [
            {
                "baseline_id": "forged_baseline",
                "called": True,
                "computed_not_literal": True,
                "function_name": "baseline_score",
                "independent_callable": True,
                "input_row_ids": ["forged-episode-1"],
                "output_row_ids": ["baseline-forged-row-1"],
                "run_id": "forged-baseline",
            }
        ],
    )
    _write_jsonl(
        bundle / "ablation_invocations.jsonl",
        [
            {
                "ablation_id": "forged_ablation",
                "called": True,
                "episodes_rerun": True,
                "intervention_applied": True,
                "intervention_function": "ablation_score",
                "output_row_ids": ["ablation-forged-row-1"],
                "post_intervention_state_hashes": ["sha256:forged-after"],
                "pre_intervention_state_hashes": ["sha256:forged-before"],
                "run_id": "forged-ablation",
                "score_recomputed": True,
            }
        ],
    )
    _write_json(
        bundle / "leakage_scan_report.json",
        {
            "called": True,
            "clean_control_passed": True,
            "computed_not_literal": True,
            "positive_control_detected": True,
            "positive_control_present": True,
            "scanned_surfaces": ["candidate_rows", "producer_function", "expected_output_digest"],
            "scanner_function": "leakage_scan",
        },
    )
    _write_json(
        bundle / "replay_recompute_report.json",
        {
            "behavior_recomputed": True,
            "called": True,
            "compared_action": True,
            "computed_not_literal": True,
            "hash_only": False,
            "replay_function": "behavior_replay",
            "stored_actions_reused": False,
            "used_observation": True,
            "used_serialized_state": True,
        },
    )
    _write_json(
        bundle / "frozen_input_consumption.json",
        {
            "consumed_input_ids": ["forged-seed-1", "forged-heldout-1", "forged-pair-1"],
            "required_input_ids": ["forged-seed-1", "forged-heldout-1", "forged-pair-1"],
            "unused_input_ids": [],
        },
    )


def _run_case(case_id: str, producer_function_name: str) -> dict[str, Any]:
    bundle = ARTIFACT_DIR / "forged_bundles" / case_id
    out = ARTIFACT_DIR / "verifier_outputs" / case_id
    producer = _module_path(producer_function_name)
    code_hash = _sha256_file(Path(__file__))
    _write_forged_bundle(bundle, producer, code_hash)

    decision = verify_bundle(bundle, run_id=f"{TASK_ID}-{case_id}")
    decision["verifier_command"] = (
        f"python -m evidence_admission_verifier_001a {bundle} --out {out}"
    )
    write_admission_artifacts(decision, out)

    return {
        "case_id": case_id,
        "producer_function": producer,
        "bundle_path": str(bundle.relative_to(REPO_ROOT)),
        "output_path": str(out.relative_to(REPO_ROOT)),
        "admitted_for_citation": decision["admitted_for_citation"],
        "canonical_decision": decision["canonical_decision"],
        "block_reason_ids": decision["block_reason_ids"],
        "callable_check_count": len(decision["callable_provenance_checks"]),
        "row_injection_required": producer_function_name == "row_echo_forged_digest",
    }


def main() -> int:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    repo_state = {
        "branch": _git(["branch", "--show-current"]),
        "head": _git(["rev-parse", "HEAD"]),
        "status_short_branch": _git(["status", "--short", "--branch"]),
        "anchor_under_audit_resolved": _git(["rev-parse", ANCHOR_UNDER_AUDIT]),
        "repair_parent_resolved": _git(["rev-parse", REPAIR_PARENT]),
    }

    cases = [
        _run_case("constant_producer", "constant_forged_digest"),
        _run_case("row_echo_producer", "row_echo_forged_digest"),
    ]
    constant_case = next(case for case in cases if case["case_id"] == "constant_producer")
    row_echo_case = next(case for case in cases if case["case_id"] == "row_echo_producer")

    result = {
        "task_id": TASK_ID,
        "verdict": "verifier_001b_blocked_by_circular_candidate_controlled_digest",
        "claim_ceiling": CLAIM_CEILING,
        "current_layer": "engineering-governance / verifier bypass audit preservation and route downgrade only",
        "mainline_integration_status": "none",
        "enabled_status": "no new enabled path; standalone verifier only",
        "audited_boundary": ANCHOR_UNDER_AUDIT,
        "repair_parent": REPAIR_PARENT,
        "forged_digest": "sha256:" + FORGED_DIGEST,
        "poc_cases": cases,
        "constant_producer_admitted": constant_case["admitted_for_citation"],
        "row_echo_producer_admitted": row_echo_case["admitted_for_citation"],
        "bypass_depends_on_row_injection": False
        if constant_case["admitted_for_citation"]
        else "not_proven",
        "blocker": (
            "The verifier compares producer-returned output_digest to "
            "candidate-declared expected_output_digest; the PoC controls both."
        ),
        "real_trigger_evidence": (
            "forged bundle admitted with block_reason_ids empty in verifier_outputs/"
            "constant_producer/admission_decision.json"
        ),
        "repo_state": repo_state,
        "what_this_does_not_prove": [
            "Gate validity",
            "mechanism validity",
            "admission readiness",
            "mainline effect",
            "agency",
            "consciousness",
            "emotion",
            "autonomy",
            "stable user benefit",
            "EGO readiness",
        ],
    }
    _write_json(ARTIFACT_DIR / "poc_result.json", result)

    route = {
        "task_id": TASK_ID,
        "route_decision": "downgrade_verifier_001b_to_weak_prefilter_linter_only",
        "verifier_001b_usable_for_citation_admission": False,
        "verifier_001b_usable_for_gate_admission": False,
        "safe_to_wire_gate3": False,
        "safe_to_wire_gate4": False,
        "safe_to_wire_bridge": False,
        "safe_to_wire_runtime": False,
        "safe_to_wire_ego_mainline": False,
        "claim_ceiling": CLAIM_CEILING,
        "basis": result["blocker"],
        "next_minimal_closed_loop_action": (
            "independent review of preserved bypass; repair only under a separate "
            "authorized task card"
        ),
    }
    _write_json(ARTIFACT_DIR / "route_decision.json", route)
    _write_json(
        ARTIFACT_DIR / "audit_preservation_manifest.json",
        {
            "task_id": TASK_ID,
            "preserved_doc": "docs/research/EVIDENCE-ADMISSION-VERIFIER-001B-BYPASS-AUDIT-001A.md",
            "poc_script": str(Path(__file__).relative_to(REPO_ROOT)),
            "poc_result": "artifacts/evidence_admission_verifier_001b_bypass_audit_001a/poc_result.json",
            "route_decision": "artifacts/evidence_admission_verifier_001b_bypass_audit_001a/route_decision.json",
            "audited_boundary": ANCHOR_UNDER_AUDIT,
            "repair_parent": REPAIR_PARENT,
            "uploaded_poc_preservation_note": (
                "No separate uploaded file was discoverable in the clean repo state; "
                "this repo-visible script preserves an executable reproduction."
            ),
        },
    )
    (ARTIFACT_DIR / "claim_ceiling.txt").write_text(CLAIM_CEILING + "\n", encoding="utf-8")
    return 0 if constant_case["admitted_for_citation"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
