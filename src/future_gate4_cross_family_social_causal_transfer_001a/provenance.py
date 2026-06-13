from __future__ import annotations

from typing import Any

from . import TASK_ID
from . import core


REQUIRED_SCORE_PROVENANCE_FIELDS = (
    "result_id",
    "score",
    "producer_function",
    "input_artifact_paths",
    "input_artifact_hashes",
    "run_id",
    "seed",
    "context_ids",
    "episode_ids",
    "partner_family_ids",
    "task_schema_ids",
    "train_heldout_split_ids",
    "counterfactual_pair_ids",
    "aggregation_rule",
    "source_file_path",
    "source_file_hash",
    "code_path_hash",
)


def _record(
    *,
    result_id: str,
    score: float,
    producer_function: str,
    episodes: list[dict[str, Any]],
    run_id: str,
    equivalence_rule_hash: str,
) -> dict[str, Any]:
    return {
        "result_id": result_id,
        "score": score,
        "producer_function": producer_function,
        "input_artifact_paths": [
            "artifacts/implement_future_gate4_cross_family_social_causal_transfer_001a/train_heldout_split_manifest.json",
            "artifacts/implement_future_gate4_cross_family_social_causal_transfer_001a/counterfactual_pair_manifest.json",
            "artifacts/implement_future_gate4_cross_family_social_causal_transfer_001a/trace.jsonl",
        ],
        "input_artifact_hashes": {
            "episodes": core.sha256_json(episodes),
            "equivalence_rule": equivalence_rule_hash,
        },
        "run_id": run_id,
        "seed": ",".join(sorted({episode["seed_id"] for episode in episodes})),
        "context_ids": sorted({episode["context_id"] for episode in episodes}),
        "episode_ids": sorted({episode["episode_id"] for episode in episodes}),
        "partner_family_ids": sorted({episode["partner_family_id"] for episode in episodes}),
        "task_schema_ids": sorted({episode["task_schema_id"] for episode in episodes}),
        "train_heldout_split_ids": sorted({episode["train_heldout_split_id"] for episode in episodes}),
        "counterfactual_pair_ids": sorted({episode["counterfactual_pair_id"] for episode in episodes}),
        "aggregation_rule": "mean_accuracy_over_heldout_counterfactual_episode_rows",
        "source_file_path": core.source_file_path(),
        "source_file_hash": core.code_path_hash(),
        "code_path_hash": core.code_path_hash(),
        "equivalence_rule_hash": equivalence_rule_hash,
    }

def build_computed_evidence_provenance(
    *,
    run_id: str,
    episodes: list[dict[str, Any]],
    candidate_summary: dict[str, Any],
    baseline_results: dict[str, Any],
    ablation_log: dict[str, Any],
    leakage_scan: dict[str, Any],
    replay_report: dict[str, Any],
    equivalence_rule_hash: str,
) -> dict[str, Any]:
    records = [
        _record(
            result_id="candidate_score",
            score=candidate_summary["score"],
            producer_function=candidate_summary["producer_function"],
            episodes=episodes,
            run_id=run_id,
            equivalence_rule_hash=equivalence_rule_hash,
        )
    ]
    for baseline_id, summary in sorted(baseline_results.items()):
        records.append(
            _record(
                result_id=f"baseline_score:{baseline_id}",
                score=summary["score"],
                producer_function=summary["producer_function"],
                episodes=episodes,
                run_id=run_id,
                equivalence_rule_hash=equivalence_rule_hash,
            )
        )
    for row in ablation_log["invocations"]:
        records.append(
            _record(
                result_id=f"ablation_score:{row['ablation_id']}",
                score=row["score"],
                producer_function=row["intervention_function"],
                episodes=episodes,
                run_id=run_id,
                equivalence_rule_hash=equivalence_rule_hash,
            )
        )
    records.append(
        _record(
            result_id="leakage_scan_result",
            score=1.0 if leakage_scan["verdict"] == "clean" else 0.0,
            producer_function=leakage_scan["producer_function"],
            episodes=episodes,
            run_id=run_id,
            equivalence_rule_hash=equivalence_rule_hash,
        )
    )
    records.append(
        _record(
            result_id="replay_recomputation_result",
            score=1.0 if replay_report["passed"] else 0.0,
            producer_function=replay_report["producer_function"],
            episodes=episodes,
            run_id=run_id,
            equivalence_rule_hash=equivalence_rule_hash,
        )
    )
    report = {
        "task_id": TASK_ID,
        "producer_function": "future_gate4_cross_family_social_causal_transfer_001a.provenance.build_computed_evidence_provenance",
        "records": records,
        "required_fields": list(REQUIRED_SCORE_PROVENANCE_FIELDS),
    }
    report["verification"] = verify_computed_evidence_provenance(report)
    return report


def verify_computed_evidence_provenance(report: dict[str, Any]) -> dict[str, Any]:
    missing_fields = []
    for record in report.get("records", []):
        for field in REQUIRED_SCORE_PROVENANCE_FIELDS:
            if field not in record or record[field] in (None, "", [], {}):
                missing_fields.append(field)
    static_literal = [
        record.get("result_id")
        for record in report.get("records", [])
        if "literal" in str(record.get("producer_function", "")).lower()
        or "static" in str(record.get("producer_function", "")).lower()
    ]
    return {
        "passed": not missing_fields and not static_literal and bool(report.get("records")),
        "missing_fields": sorted(set(missing_fields)),
        "static_or_literal_records": static_literal,
    }
