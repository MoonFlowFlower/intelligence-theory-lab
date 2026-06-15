from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


TASK_ID = "PRESERVE-ONE-GATE-FUTURE-ONLY-HARNESS-001A-NEGATIVE-AUDIT-001A"
ANCHOR_UNDER_AUDIT = "cb95bbdb06c9fadbbbf7765ae61acc46609ed994"
ANCHOR_TAG = "remote-anchor-one-gate-future-only-non-circular-evidence-harness-001a-cb95bbd"
VERDICT = "harness_001a_blocked_by_candidate_authored_ground_truth"
AUDIT_VERDICT = "partially_real_but_circular_at_ground_truth"
CLAIM_CEILING = "future-only harness negative audit preservation and route downgrade only"

ARTIFACT_DIR = Path(__file__).resolve().parent
REPO_ROOT = ARTIFACT_DIR.parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from one_gate_future_only_non_circular_harness_001a import runner  # noqa: E402


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def sha256_json(value: Any) -> str:
    return sha256_text(canonical_json(value))


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git_output(*args: str) -> str:
    completed = subprocess.run(
        ["git", *args],
        cwd=REPO_ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    return completed.stdout.strip() if completed.returncode == 0 else completed.stderr.strip()


def clone_json(value: Any) -> Any:
    return json.loads(json.dumps(value, sort_keys=True))


def fixed_episode_surface(payload: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for trace in payload["raw_traces"]:
        rows.append(
            {
                "seed": trace["seed"],
                "context_id": trace["context_id"],
                "episode_id": trace["episode_id"],
                "observation": trace["observation"],
                "prediction": trace["prediction"],
                "action": trace["action"],
            }
        )
    return rows


def policy_maps(payload: dict[str, Any]) -> list[dict[str, str]]:
    return [trace["serialized_state"]["policy_map"] for trace in payload["raw_traces"]]


def set_policy_map(payload: dict[str, Any], policy_map: dict[str, str]) -> dict[str, Any]:
    updated = clone_json(payload)
    for trace in updated["raw_traces"]:
        trace["serialized_state"]["policy_map"] = dict(policy_map)
    return updated


def degenerate_majority_payload() -> dict[str, Any]:
    payload = runner.build_raw_output_only_fixture()
    payload["candidate_id"] = "degenerate_all_approach_self_consistent_candidate_fixture"
    all_approach = {"green": "approach", "red": "approach", "blue": "approach"}
    for trace in payload["raw_traces"]:
        trace["serialized_state"]["policy_map"] = dict(all_approach)
        trace["action"] = "approach"
    return payload


def summarize_report(report: dict[str, Any]) -> dict[str, Any]:
    return {
        "candidate_id": report.get("candidate_id"),
        "candidate_blocked": report.get("candidate_blocked"),
        "admission_decision": report.get("admission_decision"),
        "computed_score": report.get("computed_score"),
        "baseline_score": report.get("baseline_result", {}).get("score"),
        "baseline_majority_action": report.get("baseline_result", {}).get("majority_action"),
        "ablation_score": report.get("ablation_result", {}).get("score"),
        "replay_matches_original_decision": report.get("replay_result", {}).get(
            "replay_matches_original_decision"
        ),
        "replay_mismatch_episode_ids": report.get("replay_result", {}).get("mismatch_episode_ids"),
        "leakage_hit_count": len(report.get("leakage_result", {}).get("candidate_controlled_hits", [])),
        "leakage_positive_control_detected": report.get("leakage_result", {}).get(
            "positive_control_detected"
        ),
        "block_reason_ids": report.get("block_reason_ids"),
        "metric_provenance": report.get("metric_provenance"),
    }


def main() -> None:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)

    self_endorsing_payload = runner.build_raw_output_only_fixture()
    self_endorsing_payload["candidate_id"] = "self_endorsing_policy_map_candidate_fixture"

    flipped_payload = set_policy_map(
        self_endorsing_payload,
        {"green": "avoid", "red": "wait", "blue": "approach"},
    )
    flipped_payload["candidate_id"] = "flipped_policy_map_same_observations_actions_fixture"

    degenerate_payload = degenerate_majority_payload()

    self_report = runner.evaluate_candidate_outputs(
        self_endorsing_payload,
        run_id=f"{TASK_ID}_self_endorsing",
    )
    flipped_report = runner.evaluate_candidate_outputs(
        flipped_payload,
        run_id=f"{TASK_ID}_flipped_policy_map",
    )
    degenerate_report = runner.evaluate_candidate_outputs(
        degenerate_payload,
        run_id=f"{TASK_ID}_degenerate_majority_equivalent",
    )

    positive_reports = {
        control_id: runner.evaluate_candidate_outputs(payload, run_id=f"{TASK_ID}_{control_id}")
        for control_id, payload in runner.build_positive_control_payloads().items()
    }
    degenerate_acceptance_gates = runner._acceptance_gates(degenerate_report, positive_reports)

    same_fixed_surface = fixed_episode_surface(self_endorsing_payload) == fixed_episode_surface(flipped_payload)
    fixed_surface_hash = sha256_json(fixed_episode_surface(self_endorsing_payload))

    result = {
        "task_id": TASK_ID,
        "anchor_under_audit": ANCHOR_UNDER_AUDIT,
        "anchor_tag_under_audit": ANCHOR_TAG,
        "verdict": VERDICT,
        "audit_verdict": AUDIT_VERDICT,
        "layer": "engineering-governance / future-only harness negative audit preservation",
        "mainline_integration_status": "none",
        "enabled_status": "no new enabled path; existing harness not repaired or wired",
        "real_trigger_evidence": (
            "temp rerun through existing harness evaluator shows same observations/actions with only "
            "candidate-authored policy_map changed flips the result; static audit readback supplies the "
            "independent audit framing"
        ),
        "claim_ceiling": CLAIM_CEILING,
        "evidence_classification": "bounded temp rerun plus audit-readback/static route downgrade",
        "contrast": {
            "same_observations_actions_predictions": same_fixed_surface,
            "fixed_episode_surface_sha256": fixed_surface_hash,
            "self_endorsing_payload_sha256": sha256_json(self_endorsing_payload),
            "flipped_payload_sha256": sha256_json(flipped_payload),
            "policy_maps_differ": policy_maps(self_endorsing_payload) != policy_maps(flipped_payload),
            "self_endorsing_summary": summarize_report(self_report),
            "flipped_policy_map_summary": summarize_report(flipped_report),
            "bypass_demonstrated": (
                same_fixed_surface
                and not self_report["candidate_blocked"]
                and flipped_report["candidate_blocked"]
                and self_report["computed_score"] == 1.0
            ),
        },
        "baseline_equivalence_issue": {
            "degenerate_payload_sha256": sha256_json(degenerate_payload),
            "degenerate_summary": summarize_report(degenerate_report),
            "candidate_score_equals_majority_baseline": (
                degenerate_report["computed_score"] == degenerate_report["baseline_result"]["score"]
            ),
            "degenerate_candidate_still_admitted": not degenerate_report["candidate_blocked"],
            "degenerate_acceptance_gates": degenerate_acceptance_gates,
            "acceptance_gates_all_pass_despite_equivalence": (
                all(degenerate_acceptance_gates.values())
                and degenerate_report["computed_score"] == degenerate_report["baseline_result"]["score"]
            ),
        },
        "leakage_positive_control_weakness": {
            "policy_map_in_leakage_field_names": "policy_map" in runner.LEAKAGE_FIELD_NAMES,
            "signal_in_leakage_field_names": "signal" in runner.LEAKAGE_FIELD_NAMES,
            "policy_map_in_forbidden_candidate_fields": "policy_map" in runner.FORBIDDEN_CANDIDATE_FIELDS,
            "self_endorsing_leakage_hit_count": len(
                self_report["leakage_result"]["candidate_controlled_hits"]
            ),
            "self_endorsing_leakage_hits": self_report["leakage_result"]["candidate_controlled_hits"],
            "positive_control_detected": self_report["leakage_result"]["positive_control_detected"],
            "weakness": "scanner is field-name based and does not treat policy_map/signal value channels as leakage",
        },
        "route_decision": {
            "decision": "cb95bbd_harness_must_not_be_used_as_gate_evidence_contract",
            "downgraded_to": "prototype / negative evidence: candidate-authored ground truth failure",
            "safe_to_wire_gate3": False,
            "safe_to_wire_gate4": False,
            "safe_to_wire_bridge": False,
            "safe_to_wire_ego_mainline": False,
            "safe_to_wire_runtime": False,
            "next_minimal_closed_loop_action": (
                "run a separate independent-ground-truth preflight for the intended Gate target; "
                "if no harness-owned candidate-inaccessible truth source exists, downgrade the Gate evidence route"
            ),
        },
        "source_integrity": {
            "harness_source_path": "src/one_gate_future_only_non_circular_harness_001a/runner.py",
            "harness_source_sha256": sha256_file(
                REPO_ROOT / "src" / "one_gate_future_only_non_circular_harness_001a" / "runner.py"
            ),
            "verifier_source_modified": False,
            "harness_source_modified_by_this_script": False,
            "old_gate_artifacts_modified_by_this_script": False,
        },
        "git_readback_at_rerun": {
            "branch": git_output("branch", "--show-current"),
            "head": git_output("rev-parse", "HEAD"),
            "status_short_branch": git_output("status", "--short", "--branch"),
        },
        "what_this_does_not_prove": [
            "Gate validity",
            "mechanism validity",
            "integrated admission readiness",
            "mainline effect",
            "bridge readiness",
            "runtime readiness",
            "agency",
            "consciousness",
            "emotion",
            "autonomy",
            "stable user benefit",
            "EGO readiness",
        ],
    }

    full_contrast = {
        "task_id": TASK_ID,
        "input_hashes": {
            "self_endorsing_payload_sha256": sha256_json(self_endorsing_payload),
            "flipped_payload_sha256": sha256_json(flipped_payload),
            "degenerate_payload_sha256": sha256_json(degenerate_payload),
        },
        "fixed_surface": {
            "same_observations_actions_predictions": same_fixed_surface,
            "fixed_episode_surface_sha256": fixed_surface_hash,
            "self_endorsing_fixed_episode_surface": fixed_episode_surface(self_endorsing_payload),
            "flipped_fixed_episode_surface": fixed_episode_surface(flipped_payload),
        },
        "reports": {
            "self_endorsing": self_report,
            "flipped_policy_map": flipped_report,
            "degenerate_majority_equivalent": degenerate_report,
            "positive_controls": positive_reports,
        },
    }

    files = {
        "result.json": result,
        "contrast_report.json": full_contrast,
        "route_decision.json": result["route_decision"],
        "source_integrity.json": result["source_integrity"],
    }
    for filename, payload in files.items():
        (ARTIFACT_DIR / filename).write_text(
            json.dumps(payload, sort_keys=True, indent=2, ensure_ascii=True) + "\n",
            encoding="utf-8",
        )
    (ARTIFACT_DIR / "claim_ceiling.txt").write_text(CLAIM_CEILING + "\n", encoding="utf-8")

    output_hashes = {
        filename: sha256_file(ARTIFACT_DIR / filename)
        for filename in sorted([*files.keys(), "claim_ceiling.txt"])
    }
    (ARTIFACT_DIR / "output_hashes.json").write_text(
        json.dumps(output_hashes, sort_keys=True, indent=2, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )

    print(json.dumps({"verdict": VERDICT, "output_hashes": output_hashes}, sort_keys=True))


if __name__ == "__main__":
    main()
