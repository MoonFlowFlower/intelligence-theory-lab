from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

from src.tlgp_001a.leakage import targets
from src.tlgp_001b_r2 import preregistration as P
from src.tlgp_001b_r2 import splits as S

ARTIFACT_DIR = Path(__file__).resolve().parent
FROZEN_DESIGN_PATH = (
    REPO_ROOT / "docs" / "task_cards" / "TLGP-CAPABILITY-WITNESS-GROKKING-PROBE-001B.frozen_design.json"
)
GROKKING_PROBE_PATH = REPO_ROOT / "src" / "tlgp_capability_witness_preflight_001a" / "grokking_probe.py"
ROUTE_DECISION_PATH = REPO_ROOT / "src" / "tlgp_capability_witness_preflight_001a" / "route_decision.py"
REQUIRED_ARTIFACTS = [
    "training_records.json",
    "val_curves.jsonl",
    "probe_trend_report.json",
    "route_decision_input.json",
    "route_decision.json",
    "leakage_report.json",
    "manifest.json",
]
EXPECTED = {
    "frozen_design_sha256": "515a415b7e2ae41f51d703c131b73927edcacbf92f8e32d34e1cfb815e117e55",
    "route_decision_sha256": "0dcf3659df802912ff2f760e9875526887e14c4c14d1e0cc91c0cb4d8863c0c8",
    "prereg_sha256": "6e61a831c6f287c10c25cccbb09a40671410cd4805214dbd91d62528b2c3d5a7",
}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def read_json(name: str) -> Any:
    return json.loads((ARTIFACT_DIR / name).read_text(encoding="utf-8"))


def strip_underscore_keys(obj: Any) -> Any:
    if isinstance(obj, dict):
        return {k: strip_underscore_keys(v) for k, v in obj.items() if not str(k).startswith("_")}
    if isinstance(obj, list):
        return [strip_underscore_keys(v) for v in obj]
    return obj


def canonical_json_sha256(obj: Any) -> str:
    payload = json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def read_curves() -> list[dict[str, Any]]:
    rows = []
    for line in (ARTIFACT_DIR / "val_curves.jsonl").read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


def linear_slope_per_1000_steps(rows: list[dict[str, Any]]) -> float | None:
    if len(rows) < 2:
        return None
    xs = [float(row["step"]) for row in rows]
    ys = [float(row["heldout_balacc"]) for row in rows]
    x_mean = sum(xs) / len(xs)
    y_mean = sum(ys) / len(ys)
    denom = sum((x - x_mean) ** 2 for x in xs)
    if denom == 0:
        return None
    slope_per_step = sum((x - x_mean) * (y - y_mean) for x, y in zip(xs, ys)) / denom
    return slope_per_step * 1000.0


def sustained_windows(rows: list[dict[str, Any]], threshold: float, window_size: int) -> list[dict[str, Any]]:
    windows = []
    for index in range(0, max(0, len(rows) - window_size + 1)):
        window = rows[index : index + window_size]
        if all(float(row["heldout_balacc"]) >= threshold for row in window):
            windows.append(
                {
                    "steps": [int(row["step"]) for row in window],
                    "heldout_balacc": [float(row["heldout_balacc"]) for row in window],
                }
            )
    return windows


def cell_key(row: dict[str, Any]) -> tuple[int, float]:
    return int(row["seed"]), float(row["weight_decay"])


def episode_payload(episode: Any) -> dict[str, Any]:
    return {
        "episode_id": int(episode.episode_id),
        "rule_id": int(episode.rule_id),
        "rule": {"w": list(map(int, episode.rule.w)), "c": int(episode.rule.c)},
        "adapt_x": episode.adapt_x.tolist(),
        "adapt_a": episode.adapt_a.tolist(),
        "adapt_e": episode.adapt_e.tolist(),
        "query_x": episode.query_x.tolist(),
        "query_a": episode.query_a.tolist(),
        "query_e": episode.query_e.tolist(),
        "is_shuffle": bool(episode.is_shuffle),
    }


def split_readback(split: str) -> dict[str, Any]:
    episodes = S.make_episodes("rung0", split)
    target = targets(episodes)
    h = hashlib.sha256()
    for episode in episodes:
        h.update(
            json.dumps(
                episode_payload(episode),
                sort_keys=True,
                separators=(",", ":"),
                ensure_ascii=True,
            ).encode("utf-8")
        )
        h.update(b"\n")
    answer_counts = Counter(map(int, target["answer"].tolist()))
    rule_counts = Counter(map(int, target["rule_id"].tolist()))
    return {
        "split": split,
        "episodes": len(episodes),
        "episode_hash_sha256": h.hexdigest(),
        "answer_distribution": {str(k): int(v) for k, v in sorted(answer_counts.items())},
        "rule_id_distribution": {str(k): int(v) for k, v in sorted(rule_counts.items())},
    }


def git_output(args: list[str]) -> str:
    return subprocess.check_output(["git", *args], cwd=REPO_ROOT, text=True, stderr=subprocess.STDOUT).strip()


def build_audit() -> dict[str, Any]:
    missing = [name for name in REQUIRED_ARTIFACTS if not (ARTIFACT_DIR / name).exists()]
    if missing:
        raise RuntimeError(f"missing required artifacts: {missing}")

    records = read_json("training_records.json")
    curves = read_curves()
    trend = read_json("probe_trend_report.json")
    route = read_json("route_decision.json")
    route_input = read_json("route_decision_input.json")
    leakage = read_json("leakage_report.json")
    manifest = read_json("manifest.json")
    frozen_design = json.loads(FROZEN_DESIGN_PATH.read_text(encoding="utf-8"))

    grouped: dict[tuple[int, float], list[dict[str, Any]]] = defaultdict(list)
    for row in curves:
        grouped[cell_key(row)].append(row)
    for rows in grouped.values():
        rows.sort(key=lambda row: int(row["step"]))

    per_cell = []
    cells_with_best_over_060 = []
    for record in records:
        key = (int(record["seed"]), float(record["weight_decay"]))
        rows = grouped[key]
        tail_count = max(1, int(len(rows) * 0.2))
        tail = rows[-tail_count:]
        best = max(rows, key=lambda row: float(row["heldout_balacc"]))
        best_index = rows.index(best)
        context = {
            "previous": rows[best_index - 1] if best_index > 0 else None,
            "best": best,
            "next": rows[best_index + 1] if best_index + 1 < len(rows) else None,
        }
        windows_ge_060 = sustained_windows(rows, 0.60, 3)
        if float(best["heldout_balacc"]) > 0.60:
            cells_with_best_over_060.append(
                {
                    "seed": key[0],
                    "weight_decay": key[1],
                    "best_heldout_balacc": float(best["heldout_balacc"]),
                    "best_heldout_step": int(best["step"]),
                    "excess_over_0_60": float(best["heldout_balacc"]) - 0.60,
                    "sustained_3_checkpoint_ge_0_60": bool(windows_ge_060),
                    "neighbor_context": {
                        name: None
                        if row is None
                        else {
                            "step": int(row["step"]),
                            "train_balacc": float(row["train_balacc"]),
                            "heldout_balacc": float(row["heldout_balacc"]),
                        }
                        for name, row in context.items()
                    },
                }
            )
        per_cell.append(
            {
                "seed": key[0],
                "weight_decay": key[1],
                "checkpoints": len(rows),
                "steps": [int(row["step"]) for row in rows],
                "final_train_balacc": float(record["final_train_balacc"]),
                "final_heldout_balacc": float(record["final_heldout_balacc"]),
                "best_heldout_balacc": float(record["best_heldout_balacc"]),
                "best_heldout_step": int(record["best_heldout_step"]),
                "train_first_ge_0_95_step": record["train_first_ge_0_95_step"],
                "late_heldout_rise": bool(record["late_heldout_rise"]),
                "tail_window_checkpoints": tail_count,
                "tail_start_step": int(tail[0]["step"]),
                "tail_end_step": int(tail[-1]["step"]),
                "tail_start_heldout_balacc": float(tail[0]["heldout_balacc"]),
                "tail_end_heldout_balacc": float(tail[-1]["heldout_balacc"]),
                "tail_delta_heldout_balacc": float(tail[-1]["heldout_balacc"]) - float(tail[0]["heldout_balacc"]),
                "tail_slope_per_1000_steps": linear_slope_per_1000_steps(tail),
                "sustained_3_checkpoint_ge_0_60_windows": windows_ge_060,
            }
        )

    source_text = GROKKING_PROBE_PATH.read_text(encoding="utf-8")
    static_optimizer_plumbing = (
        "torch.optim.AdamW(model.parameters(), lr=LEARNING_RATE, weight_decay=float(weight_decay))" in source_text
    )
    protected_status = git_output(["status", "--porcelain=v1", "--", "src/tlgp_001b_r2", "src/tlgp_001a"]).splitlines()
    artifact_hashes = {name: sha256_file(ARTIFACT_DIR / name) for name in REQUIRED_ARTIFACTS}
    manifest_hash_gate = {key: manifest.get(key) == value for key, value in EXPECTED.items()}
    frozen_design_sha = canonical_json_sha256(strip_underscore_keys(frozen_design))

    all_fit = all(record["train_first_ge_0_95_step"] is not None for record in records)
    any_positive = bool(trend["aggregate_flags"]["positive_abs_heldout_ge_0_75"]) or bool(
        trend["aggregate_flags"]["positive_delayed_generalization_signature"]
    )
    any_late_rise = any(bool(record["late_heldout_rise"]) for record in records)
    all_checkpoint_counts_ok = all(len(rows) == 25 for rows in grouped.values()) and len(curves) == 150
    single_threshold_blip = (
        len(cells_with_best_over_060) == 1
        and not cells_with_best_over_060[0]["sustained_3_checkpoint_ge_0_60"]
    )

    if trend.get("go_no_go_verdict") == "ambiguous" and all_fit and not any_positive and not any_late_rise:
        substantive_assessment = "negative_leaning_no_grokking_signature"
    else:
        substantive_assessment = "requires_operator_review"

    audit = {
        "task_id": "TLGP-CAPABILITY-WITNESS-GROKKING-PROBE-001B-CLOSEOUT-AUDIT-001A",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "producer": {
            "script_path": str(Path(__file__).resolve().relative_to(REPO_ROOT).as_posix()),
            "script_sha256": sha256_file(Path(__file__).resolve()),
        },
        "input_artifacts": artifact_hashes,
        "repo_readback": {
            "current_head": git_output(["rev-parse", "HEAD"]),
            "current_branch": git_output(["branch", "--show-current"]),
            "manifest_head": manifest.get("git_head"),
            "manifest_branch": manifest.get("git_branch"),
            "protected_source_status": protected_status,
            "protected_source_status_empty": not protected_status,
            "route_decision_py_sha256": sha256_file(ROUTE_DECISION_PATH),
            "grokking_probe_py_sha256": sha256_file(GROKKING_PROBE_PATH),
        },
        "hash_gates": {
            "manifest_expected_hashes_match": manifest_hash_gate,
            "frozen_design_canonical_sha256": frozen_design_sha,
            "frozen_design_matches_expected": frozen_design_sha == EXPECTED["frozen_design_sha256"],
            "route_decision_matches_expected": sha256_file(ROUTE_DECISION_PATH)
            == EXPECTED["route_decision_sha256"],
        },
        "artifact_completeness": {
            "records_count": len(records),
            "curve_rows": len(curves),
            "cells": len(grouped),
            "all_checkpoint_counts_ok": all_checkpoint_counts_ok,
            "failure_manifest_present": (ARTIFACT_DIR / "failure_manifest.json").exists(),
            "run_stderr_bytes": (ARTIFACT_DIR / "run_stderr.log").stat().st_size
            if (ARTIFACT_DIR / "run_stderr.log").exists()
            else None,
        },
        "split_and_label_readback": {
            "label_cardinality_P_K": int(P.K),
            "uniform_random_balacc_reference": 1.0 / float(P.K),
            "train": split_readback("train"),
            "heldout": split_readback("heldout"),
            "fair_baseline_balacc": route_input.get("fair_baseline_balacc"),
        },
        "config_plumbing_readback": {
            "manifest_regime": manifest.get("regime"),
            "static_optimizer_weight_decay_argument_passed_to_adamw": static_optimizer_plumbing,
            "runtime_optimizer_param_groups_available": False,
            "runtime_optimizer_param_groups_reason": (
                "completed 001B artifacts record requested weight_decay per run, but do not serialize "
                "optimizer.param_groups; this audit therefore cannot prove runtime param-group values "
                "beyond the recorded run inputs and static runner plumbing"
            ),
        },
        "formal_outputs": {
            "probe_trend_go_no_go_verdict": trend.get("go_no_go_verdict"),
            "route_decision_route": route.get("route"),
            "route_decision_reason": route.get("reason"),
            "leakage_detector_valid": bool(leakage.get("detector_valid")),
            "all_planted_caught": bool(leakage.get("all_planted_caught")),
            "no_clean_false_flag": bool(leakage.get("no_clean_false_flag")),
            "aggregate_flags": trend.get("aggregate_flags"),
        },
        "per_cell": per_cell,
        "threshold_blip_analysis": {
            "cells_with_best_heldout_over_0_60": cells_with_best_over_060,
            "single_unsustained_threshold_blip": single_threshold_blip,
            "interpretation": (
                "The formal negative-close cutoff is blocked by one best-heldout checkpoint above 0.60; "
                "the crossing is not a 3-checkpoint sustained plateau and is not a positive grokking signal."
            ),
        },
        "closeout_classification": {
            "formal_status": trend.get("go_no_go_verdict"),
            "substantive_assessment": substantive_assessment,
            "reason": (
                "All six cells reached train>=0.95, no cell reached heldout>=0.75, no cell had a sustained "
                "late heldout rise, and the only >0.60 heldout value was an unsustained single checkpoint."
            ),
            "program_bug_priority": "not_first_suspect_but_runtime_optimizer_param_group_readback_missing",
            "primary_suspect": "witness_task_structure_or_grokking_testbed_mismatch",
            "secondary_suspect": "scale_or_duration_insufficient_without_supporting_late_rise_morphology",
        },
        "claim_ceiling": (
            "formal ambiguous; negative-leaning/no grokking signature for this local cheap fit+regularization "
            "probe only. No route terminal, no TLGP-R2 verdict, no mechanism validity claim, no EGO claim."
        ),
        "next_minimal_actions": [
            "operator/auditor review before banking",
            "if banking is authorized, preserve formal ambiguous plus negative-leaning caveat exactly",
            "before any future continuation, add optimizer param-group/runtime config readback to artifacts",
            "run known-good grokking sanity only as a separate task card if operator authorizes",
        ],
    }
    return audit


def write_outputs(audit: dict[str, Any]) -> None:
    json_path = ARTIFACT_DIR / "closeout_audit_001b.json"
    md_path = ARTIFACT_DIR / "CLOSEOUT_AUDIT_001B.md"
    json_path.write_text(json.dumps(audit, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "# GROKKING_PROBE_001B Closeout Audit",
        "",
        f"Task: `{audit['task_id']}`",
        f"Formal status: `{audit['closeout_classification']['formal_status']}`",
        f"Substantive assessment: `{audit['closeout_classification']['substantive_assessment']}`",
        "",
        "## Readback",
        "",
        f"- Records: {audit['artifact_completeness']['records_count']}",
        f"- Curve rows: {audit['artifact_completeness']['curve_rows']}",
        f"- Route decision: `{audit['formal_outputs']['route_decision_route']}`",
        f"- Leakage detector valid: `{audit['formal_outputs']['leakage_detector_valid']}`",
        f"- Failure manifest present: `{audit['artifact_completeness']['failure_manifest_present']}`",
        "",
        "## Per Cell",
        "",
        "| seed | wd | final train | final heldout | best heldout | fit step | tail delta | late rise |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for row in audit["per_cell"]:
        lines.append(
            "| {seed} | {weight_decay:.1f} | {final_train_balacc:.6f} | {final_heldout_balacc:.6f} | "
            "{best_heldout_balacc:.6f} | {fit_step} | {tail_delta_heldout_balacc:.6f} | {late} |".format(
                seed=row["seed"],
                weight_decay=row["weight_decay"],
                final_train_balacc=row["final_train_balacc"],
                final_heldout_balacc=row["final_heldout_balacc"],
                best_heldout_balacc=row["best_heldout_balacc"],
                fit_step=row["train_first_ge_0_95_step"],
                tail_delta_heldout_balacc=row["tail_delta_heldout_balacc"],
                late=str(row["late_heldout_rise"]).lower(),
            )
        )
    lines.extend(
        [
            "",
            "## Threshold Blip",
            "",
            audit["threshold_blip_analysis"]["interpretation"],
            "",
            "## Claim Ceiling",
            "",
            audit["claim_ceiling"],
            "",
        ]
    )
    md_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    audit = build_audit()
    write_outputs(audit)
    print(json.dumps(audit["closeout_classification"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
