import json
from pathlib import Path

from .ablations import run_ablations
from .candidate import run_candidate
from .config import ARTIFACT_DIR, CLAIM_CEILING, OOD_BAND, RHO, SEED_FAMILIES
from .generator import build_dataset
from .headroom_preflight import run_headroom_preflight
from .leakage import run_leakage_controls
from .legal_view import to_legal_episode
from .replay import replay_candidate_run


EXPECTED_ARTIFACTS = [
    "headroom_preflight.json",
    "result.json",
    "trace.jsonl",
    "baseline_comparison.json",
    "fair_baseline_sensitivity.json",
    "ablation_report.json",
    "replay_report.json",
    "leakage_report.json",
    "parity_report.json",
    "claim_ceiling.txt",
]


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, sort_keys=True, indent=2) + "\n", encoding="utf-8")


def _write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(row, sort_keys=True) + "\n" for row in rows), encoding="utf-8")


def _write_claim_ceiling(output_path: Path) -> None:
    (output_path / "claim_ceiling.txt").write_text(CLAIM_CEILING + "\n", encoding="utf-8")


def _write_stop_result(output_path: Path, preflight: dict) -> dict:
    result = {
        "verdict": preflight["verdict"],
        "mechanism_claim_admitted": False,
        "failure_manifest_ref": "failure_manifest.json",
        "claim_ceiling": "Phase 0 blocker evidence only; no mechanism claim",
        "headroom_verdict": preflight["verdict"],
    }
    _write_json(output_path / "result.json", result)
    _write_jsonl(output_path / "trace.jsonl", [])
    skip_payload = {
        "skipped": True,
        "reason": preflight["verdict"],
        "stop_conditions": preflight.get("stop_conditions", []),
        "claim_ceiling": "Phase 0 blocker evidence only; no downstream mechanism evidence",
    }
    _write_json(output_path / "ablation_report.json", skip_payload | {"artifact_type": "ablation_report"})
    _write_json(output_path / "replay_report.json", skip_payload | {"artifact_type": "replay_report"})
    _write_json(output_path / "leakage_report.json", skip_payload | {"artifact_type": "leakage_report"})
    _write_claim_ceiling(output_path)
    return result


def run(output_dir: str | Path = ARTIFACT_DIR, fixture: str = "normal") -> dict:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    preflight = run_headroom_preflight(output_path, fixture=fixture)
    if preflight["verdict"] != "headroom_present":
        return _write_stop_result(output_path, preflight)

    episodes = build_dataset("ood", SEED_FAMILIES["ood_test"], episodes_per_seed=1)
    candidate_runs = [run_candidate(to_legal_episode(episode)) for episode in episodes]
    trace_rows = []
    for episode, candidate_run in zip(episodes, candidate_runs):
        truth_by_q = {query.q_id: query.truth_outcome for query in episode.queries}
        trace_rows.extend(candidate_run["trace"])
        for row in candidate_run["query_trace"]:
            enriched = dict(row)
            enriched["actual_outcome"] = truth_by_q[row["q_id"]]
            trace_rows.append(enriched)
    _write_jsonl(output_path / "trace.jsonl", trace_rows)

    ablation_report = run_ablations(output_path)
    replay_report = replay_candidate_run(candidate_runs[0], to_legal_episode(episodes[0]))
    _write_json(output_path / "replay_report.json", replay_report)
    leakage_report = run_leakage_controls(output_path)

    ablation_ok = all(
        row["direction_ok"]
        for row in ablation_report["ablations"]
        if row["ablation_id"] in {"A1", "A2", "A3", "A4"}
    )
    replay_ok = (
        replay_report["trajectory_match"]
        and replay_report["query_match"]
        and replay_report["recomputed_not_hashed"]
        and replay_report["tamper_control"]["corrupted_state_replay_failed"]
    )
    leakage_ok = leakage_report["clean_control_passed"] and all(
        row["positive_control_ok"] for row in leakage_report["controls"]
    )
    margin = preflight["candidate_ood_score"] - preflight["strongest_fair_baseline_score"]
    floor_room = preflight["oracle_ceiling_score"] - preflight["no_update_floor_score"]
    recovery_floor_ok = (
        preflight["candidate_ood_score"] - preflight["no_update_floor_score"]
        >= RHO * floor_room
    )
    all_ok = margin > OOD_BAND and recovery_floor_ok and ablation_ok and replay_ok and leakage_ok
    result = {
        "verdict": "local_mechanism_discrimination_evidence" if all_ok else "blocked_after_headroom",
        "mechanism_claim_admitted": all_ok,
        "headroom_verdict": preflight["verdict"],
        "candidate_ood_score": preflight["candidate_ood_score"],
        "strongest_fair_ood_score": preflight["strongest_fair_baseline_score"],
        "margin": margin,
        "rho_floor_ok": recovery_floor_ok,
        "ablation_summary": {"direction_ok": ablation_ok},
        "replay_summary": replay_report,
        "leakage_summary": {"positive_controls_ok": leakage_ok},
        "failure_manifest_ref": None if all_ok else "failure_manifest.json",
        "claim_ceiling": CLAIM_CEILING,
    }
    if not all_ok:
        _write_json(
            output_path / "failure_manifest.json",
            {
                "verdict": result["verdict"],
                "stop_conditions": ["blocked_by_non_load_bearing_update_or_margin_gap"],
                "claim_ceiling": CLAIM_CEILING,
            },
        )
    _write_json(output_path / "result.json", result)
    _write_claim_ceiling(output_path)
    return result


if __name__ == "__main__":
    print(json.dumps(run(), sort_keys=True, indent=2))
