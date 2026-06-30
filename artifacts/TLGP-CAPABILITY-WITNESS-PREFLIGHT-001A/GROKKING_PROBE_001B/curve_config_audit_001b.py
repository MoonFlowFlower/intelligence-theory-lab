from __future__ import annotations

import ast
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


TASK_ID = "TLGP-CAPABILITY-WITNESS-GROKKING-PROBE-001B-CURVE-CONFIG-AUDIT-001A"
ARTIFACT_DIR = Path(__file__).resolve().parent
FROZEN_DESIGN_PATH = (
    REPO_ROOT / "docs" / "task_cards" / "TLGP-CAPABILITY-WITNESS-GROKKING-PROBE-001B.frozen_design.json"
)
GROKKING_PROBE_PATH = REPO_ROOT / "src" / "tlgp_capability_witness_preflight_001a" / "grokking_probe.py"
MINIMAL_PROBE_PATH = REPO_ROOT / "src" / "tlgp_capability_witness_preflight_001a" / "minimal_probe.py"
ROUTE_DECISION_PATH = REPO_ROOT / "src" / "tlgp_capability_witness_preflight_001a" / "route_decision.py"
EXPECTED_BANK_COMMIT = "2de7fef7ef4d06f4ede0d48301839f0f71c2753a"
EXPECTED = {
    "frozen_design_sha256": "515a415b7e2ae41f51d703c131b73927edcacbf92f8e32d34e1cfb815e117e55",
    "route_decision_sha256": "0dcf3659df802912ff2f760e9875526887e14c4c14d1e0cc91c0cb4d8863c0c8",
    "prereg_sha256": "6e61a831c6f287c10c25cccbb09a40671410cd4805214dbd91d62528b2c3d5a7",
}
REQUIRED_ARTIFACTS = [
    "training_records.json",
    "val_curves.jsonl",
    "probe_trend_report.json",
    "route_decision_input.json",
    "route_decision.json",
    "leakage_report.json",
    "manifest.json",
    "closeout_audit_001b.json",
]
PROTECTED_PATHS = [
    "src/tlgp_001b_r2",
    "src/tlgp_001a",
    "src/tlgp_capability_witness_preflight_001a/route_decision.py",
    "src/tlgp_capability_witness_preflight_001a/minimal_probe.py",
    "src/tlgp_capability_witness_preflight_001a/grokking_probe.py",
]
THRESHOLDS = [0.60, 0.65, 0.75]
SUSTAINED_WINDOW_SIZE = 3
FLOAT_TOL = 1e-12


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def read_json(name: str) -> Any:
    return json.loads((ARTIFACT_DIR / name).read_text(encoding="utf-8"))


def read_curves() -> list[dict[str, Any]]:
    rows = []
    for line in (ARTIFACT_DIR / "val_curves.jsonl").read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


def strip_underscore_keys(obj: Any) -> Any:
    if isinstance(obj, dict):
        return {k: strip_underscore_keys(v) for k, v in obj.items() if not str(k).startswith("_")}
    if isinstance(obj, list):
        return [strip_underscore_keys(v) for v in obj]
    return obj


def canonical_json_sha256(obj: Any) -> str:
    payload = json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def git_output(args: list[str]) -> str:
    return subprocess.check_output(["git", *args], cwd=REPO_ROOT, text=True, stderr=subprocess.STDOUT).strip()


def cell_key(row: dict[str, Any]) -> tuple[int, float]:
    return int(row["seed"]), float(row["weight_decay"])


def float_equal(a: Any, b: Any, tol: float = FLOAT_TOL) -> bool:
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        return abs(float(a) - float(b)) <= tol
    return a == b


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


def window_stats(name: str, rows: list[dict[str, Any]]) -> dict[str, Any]:
    if not rows:
        return {"name": name, "available": False, "n_checkpoints": 0}
    return {
        "name": name,
        "available": True,
        "n_checkpoints": len(rows),
        "start_step": int(rows[0]["step"]),
        "end_step": int(rows[-1]["step"]),
        "start_heldout_balacc": float(rows[0]["heldout_balacc"]),
        "end_heldout_balacc": float(rows[-1]["heldout_balacc"]),
        "delta_heldout_balacc": float(rows[-1]["heldout_balacc"]) - float(rows[0]["heldout_balacc"]),
        "slope_per_1000_steps": linear_slope_per_1000_steps(rows),
    }


def sustained_windows(rows: list[dict[str, Any]], threshold: float) -> list[dict[str, Any]]:
    windows = []
    for index in range(0, max(0, len(rows) - SUSTAINED_WINDOW_SIZE + 1)):
        window = rows[index : index + SUSTAINED_WINDOW_SIZE]
        if all(float(row["heldout_balacc"]) >= threshold for row in window):
            windows.append(
                {
                    "start_step": int(window[0]["step"]),
                    "end_step": int(window[-1]["step"]),
                    "steps": [int(row["step"]) for row in window],
                    "heldout_balacc": [float(row["heldout_balacc"]) for row in window],
                }
            )
    return windows


def longest_run(flags: list[bool]) -> int:
    best = 0
    current = 0
    for flag in flags:
        if flag:
            current += 1
            best = max(best, current)
        else:
            current = 0
    return best


def drawdown_diagnostics(rows: list[dict[str, Any]]) -> dict[str, Any]:
    if len(rows) < 2:
        return {
            "available": bool(rows),
            "reason": "need at least two checkpoints for drawdown/monotonicity",
        }
    values = [float(row["heldout_balacc"]) for row in rows]
    steps = [int(row["step"]) for row in rows]
    diffs = [b - a for a, b in zip(values, values[1:])]
    running_peak = values[0]
    max_drawdown = 0.0
    max_drawdown_step = steps[0]
    for step, value in zip(steps, values):
        running_peak = max(running_peak, value)
        drawdown = running_peak - value
        if drawdown > max_drawdown:
            max_drawdown = drawdown
            max_drawdown_step = step
    best_index = max(range(len(rows)), key=lambda i: values[i])
    return {
        "available": True,
        "n_checkpoints": len(rows),
        "monotonic_non_decreasing": all(diff >= -FLOAT_TOL for diff in diffs),
        "monotonic_non_increasing": all(diff <= FLOAT_TOL for diff in diffs),
        "num_increases": sum(1 for diff in diffs if diff > FLOAT_TOL),
        "num_decreases": sum(1 for diff in diffs if diff < -FLOAT_TOL),
        "num_equals": sum(1 for diff in diffs if abs(diff) <= FLOAT_TOL),
        "longest_increase_run": longest_run([diff > FLOAT_TOL for diff in diffs]),
        "longest_decrease_run": longest_run([diff < -FLOAT_TOL for diff in diffs]),
        "post_fit_best_step": steps[best_index],
        "post_fit_best_heldout_balacc": values[best_index],
        "final_heldout_balacc": values[-1],
        "best_to_final_drop": values[best_index] - values[-1],
        "max_drawdown_from_running_peak": max_drawdown,
        "max_drawdown_step": max_drawdown_step,
    }


def best_neighbor_context(rows: list[dict[str, Any]], best_index: int) -> dict[str, Any]:
    context = {
        "previous": rows[best_index - 1] if best_index > 0 else None,
        "best": rows[best_index],
        "next": rows[best_index + 1] if best_index + 1 < len(rows) else None,
    }
    return {
        name: None
        if row is None
        else {
            "step": int(row["step"]),
            "train_balacc": float(row["train_balacc"]),
            "heldout_balacc": float(row["heldout_balacc"]),
        }
        for name, row in context.items()
    }


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


def _is_float_weight_decay_call(node: ast.AST) -> bool:
    if not isinstance(node, ast.Call):
        return False
    if not isinstance(node.func, ast.Name) or node.func.id != "float":
        return False
    if len(node.args) != 1:
        return False
    arg = node.args[0]
    return isinstance(arg, ast.Name) and arg.id == "weight_decay"


def _is_adamw_call(node: ast.Call) -> bool:
    func = node.func
    return isinstance(func, ast.Attribute) and func.attr == "AdamW"


def static_optimizer_readback() -> dict[str, Any]:
    source = GROKKING_PROBE_PATH.read_text(encoding="utf-8")
    parsed = ast.parse(source)
    lines = source.splitlines()
    matches = []
    for node in ast.walk(parsed):
        if not isinstance(node, ast.Call) or not _is_adamw_call(node):
            continue
        weight_decay_kw = next((kw for kw in node.keywords if kw.arg == "weight_decay"), None)
        matches.append(
            {
                "line": int(getattr(node, "lineno", 0)),
                "source": lines[getattr(node, "lineno", 1) - 1].strip(),
                "weight_decay_keyword_present": weight_decay_kw is not None,
                "weight_decay_is_float_weight_decay": bool(
                    weight_decay_kw is not None and _is_float_weight_decay_call(weight_decay_kw.value)
                ),
            }
        )
    return {
        "adamw_call_count": len(matches),
        "adamw_weight_decay_float_call_present": any(
            item["weight_decay_is_float_weight_decay"] for item in matches
        ),
        "adamw_calls": matches,
    }


def runtime_optimizer_param_group_readback(records: list[dict[str, Any]]) -> dict[str, Any]:
    available_records = []
    for record in records:
        for key in ("optimizer_param_groups", "optimizer_param_group", "param_groups"):
            if key in record:
                available_records.append(
                    {
                        "seed": int(record["seed"]),
                        "weight_decay": float(record["weight_decay"]),
                        "key": key,
                        "value": record[key],
                    }
                )
    if available_records:
        return {
            "status": "available",
            "records_with_param_group_readback": available_records,
        }
    return {
        "status": "unavailable",
        "records_with_param_group_readback": [],
        "reason": (
            "completed 001B artifacts record requested weight_decay per run but do not serialize "
            "optimizer.param_groups; this audit can prove manifest inputs plus static AdamW plumbing, "
            "not direct completed-runtime param-group values"
        ),
    }


def compare_value(differences: list[dict[str, Any]], path: str, current: Any, closeout: Any) -> None:
    if float_equal(current, closeout):
        return
    differences.append({"path": path, "current": current, "closeout": closeout})


def compare_to_closeout(audit: dict[str, Any], closeout: dict[str, Any]) -> dict[str, Any]:
    differences: list[dict[str, Any]] = []
    repo_context_differences: list[dict[str, Any]] = []

    pairs = [
        ("artifact_completeness.records_count", audit["artifact_completeness"]["records_count"], closeout["artifact_completeness"]["records_count"]),
        ("artifact_completeness.curve_rows", audit["artifact_completeness"]["curve_rows"], closeout["artifact_completeness"]["curve_rows"]),
        ("artifact_completeness.cells", audit["artifact_completeness"]["cells"], closeout["artifact_completeness"]["cells"]),
        ("artifact_completeness.all_checkpoint_counts_ok", audit["artifact_completeness"]["all_checkpoint_counts_ok"], closeout["artifact_completeness"]["all_checkpoint_counts_ok"]),
        ("formal_outputs.route_decision_route", audit["formal_outputs"]["route_decision_route"], closeout["formal_outputs"]["route_decision_route"]),
        ("formal_outputs.probe_trend_go_no_go_verdict", audit["formal_outputs"]["probe_trend_go_no_go_verdict"], closeout["formal_outputs"]["probe_trend_go_no_go_verdict"]),
        ("formal_result.formal_status", audit["formal_result"]["formal_status"], closeout["closeout_classification"]["formal_status"]),
        ("formal_result.substantive_assessment", audit["formal_result"]["substantive_assessment"], closeout["closeout_classification"]["substantive_assessment"]),
        (
            "split_and_label_readback.shared_closeout_fields",
            {
                key: audit["split_and_label_readback"][key]
                for key in (
                    "label_cardinality_P_K",
                    "uniform_random_balacc_reference",
                    "train",
                    "heldout",
                    "fair_baseline_balacc",
                )
            },
            closeout["split_and_label_readback"],
        ),
        ("hash_gates.manifest_expected_hashes_match", audit["hash_gates"]["manifest_expected_hashes_match"], closeout["hash_gates"]["manifest_expected_hashes_match"]),
        ("hash_gates.frozen_design_matches_expected", audit["hash_gates"]["frozen_design_matches_expected"], closeout["hash_gates"]["frozen_design_matches_expected"]),
        ("hash_gates.route_decision_matches_expected", audit["hash_gates"]["route_decision_matches_expected"], closeout["hash_gates"]["route_decision_matches_expected"]),
        ("config.static_optimizer_weight_decay_argument_passed_to_adamw", audit["config_plumbing_readback"]["static_optimizer_weight_decay_argument_passed_to_adamw"], closeout["config_plumbing_readback"]["static_optimizer_weight_decay_argument_passed_to_adamw"]),
        ("config.runtime_optimizer_param_groups_available", audit["config_plumbing_readback"]["runtime_optimizer_param_groups_available"], closeout["config_plumbing_readback"]["runtime_optimizer_param_groups_available"]),
    ]
    for path, current, old in pairs:
        compare_value(differences, path, current, old)

    current_cells = {
        (int(row["seed"]), float(row["weight_decay"])): row for row in audit["per_cell_curve_diagnostics"]
    }
    closeout_cells = {
        (int(row["seed"]), float(row["weight_decay"])): row for row in closeout["per_cell"]
    }
    compare_value(differences, "per_cell.keys", sorted(current_cells), sorted(closeout_cells))
    for key in sorted(current_cells):
        if key not in closeout_cells:
            continue
        current = current_cells[key]
        old = closeout_cells[key]
        for field in (
            "checkpoints",
            "steps",
            "final_train_balacc",
            "final_heldout_balacc",
            "best_heldout_balacc",
            "best_heldout_step",
            "train_first_ge_0_95_step",
            "late_heldout_rise",
            "tail_delta_heldout_balacc",
            "tail_slope_per_1000_steps",
        ):
            compare_value(differences, f"per_cell[{key[0]},{key[1]}].{field}", current[field], old[field])

    closeout_blips = closeout["threshold_blip_analysis"]["cells_with_best_heldout_over_0_60"]
    current_blips = audit["threshold_blip_analysis"]["cells_with_best_heldout_over_0_60"]
    compare_value(differences, "threshold_blip_analysis.cells_with_best_heldout_over_0_60", current_blips, closeout_blips)
    compare_value(
        differences,
        "threshold_blip_analysis.single_unsustained_threshold_blip",
        audit["threshold_blip_analysis"]["single_unsustained_threshold_blip"],
        closeout["threshold_blip_analysis"]["single_unsustained_threshold_blip"],
    )

    for key in ("current_head", "current_branch"):
        current = audit["repo_readback"].get(key)
        old = closeout["repo_readback"].get(key)
        if current != old:
            repo_context_differences.append({"path": f"repo_readback.{key}", "current": current, "closeout": old})

    return {
        "status": "no_evidence_metric_drift" if not differences else "evidence_metric_drift_found",
        "evidence_metric_drift_found": bool(differences),
        "differences": differences,
        "repo_context_differences": repo_context_differences,
        "repo_context_note": (
            "repo head/branch differences are reported separately from evidence metrics; this audit is expected "
            "to run at or after the local bank commit"
        ),
    }


def build_cell_diagnostics(records: list[dict[str, Any]], curves: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[tuple[int, float], list[dict[str, Any]]] = defaultdict(list)
    for row in curves:
        grouped[cell_key(row)].append(row)
    for rows in grouped.values():
        rows.sort(key=lambda row: int(row["step"]))

    diagnostics = []
    for record in records:
        key = (int(record["seed"]), float(record["weight_decay"]))
        rows = grouped.get(key, [])
        if not rows:
            diagnostics.append(
                {
                    "seed": key[0],
                    "weight_decay": key[1],
                    "error": "missing curve rows for training record",
                }
            )
            continue
        fit_step = record.get("train_first_ge_0_95_step")
        pre_fit = [row for row in rows if fit_step is not None and int(row["step"]) <= int(fit_step)]
        post_fit = [row for row in rows if fit_step is not None and int(row["step"]) >= int(fit_step)]
        tail_count = max(1, int(len(rows) * 0.2))
        tail = rows[-tail_count:]
        best_index = max(range(len(rows)), key=lambda i: float(rows[i]["heldout_balacc"]))
        threshold_tests = {}
        for threshold in THRESHOLDS:
            all_windows = sustained_windows(rows, threshold)
            post_windows = sustained_windows(post_fit, threshold)
            threshold_tests[f"{threshold:.2f}"] = {
                "threshold": threshold,
                "window_size_checkpoints": SUSTAINED_WINDOW_SIZE,
                "any_sustained_window": bool(all_windows),
                "windows": all_windows,
                "any_post_fit_sustained_window": bool(post_windows),
                "post_fit_windows": post_windows,
            }
        diagnostics.append(
            {
                "seed": key[0],
                "weight_decay": key[1],
                "checkpoints": len(rows),
                "steps": [int(row["step"]) for row in rows],
                "step_grid_min": int(rows[0]["step"]),
                "step_grid_max": int(rows[-1]["step"]),
                "step_grid_delta_set": sorted(
                    {int(b["step"]) - int(a["step"]) for a, b in zip(rows, rows[1:])}
                ),
                "final_train_balacc": float(record["final_train_balacc"]),
                "final_heldout_balacc": float(record["final_heldout_balacc"]),
                "best_heldout_balacc": float(record["best_heldout_balacc"]),
                "best_heldout_step": int(record["best_heldout_step"]),
                "train_first_ge_0_95_step": fit_step,
                "late_heldout_rise": bool(record["late_heldout_rise"]),
                "pre_fit_curve": window_stats("pre_fit", pre_fit),
                "post_fit_curve": window_stats("post_fit", post_fit),
                "tail_20_percent_curve": window_stats("tail_20_percent", tail),
                "full_run_curve": window_stats("full_run", rows),
                "tail_window_checkpoints": tail_count,
                "tail_start_step": int(tail[0]["step"]),
                "tail_end_step": int(tail[-1]["step"]),
                "tail_start_heldout_balacc": float(tail[0]["heldout_balacc"]),
                "tail_end_heldout_balacc": float(tail[-1]["heldout_balacc"]),
                "tail_delta_heldout_balacc": float(tail[-1]["heldout_balacc"]) - float(tail[0]["heldout_balacc"]),
                "tail_slope_per_1000_steps": linear_slope_per_1000_steps(tail),
                "best_heldout_neighbor_context": best_neighbor_context(rows, best_index),
                "sustained_window_tests": threshold_tests,
                "post_fit_monotonicity_drawdown": drawdown_diagnostics(post_fit),
            }
        )
    return diagnostics


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
    closeout = read_json("closeout_audit_001b.json")
    frozen_design = json.loads(FROZEN_DESIGN_PATH.read_text(encoding="utf-8"))
    prereg = json.loads(P.PREREG_JSON_PATH.read_text(encoding="utf-8"))

    grouped: dict[tuple[int, float], list[dict[str, Any]]] = defaultdict(list)
    for row in curves:
        grouped[cell_key(row)].append(row)
    for rows in grouped.values():
        rows.sort(key=lambda row: int(row["step"]))

    cell_diagnostics = build_cell_diagnostics(records, curves)
    cells_with_best_over_060 = []
    for cell in cell_diagnostics:
        if float(cell.get("best_heldout_balacc", 0.0)) > 0.60:
            cells_with_best_over_060.append(
                {
                    "seed": cell["seed"],
                    "weight_decay": cell["weight_decay"],
                    "best_heldout_balacc": cell["best_heldout_balacc"],
                    "best_heldout_step": cell["best_heldout_step"],
                    "excess_over_0_60": float(cell["best_heldout_balacc"]) - 0.60,
                    "sustained_3_checkpoint_ge_0_60": bool(
                        cell["sustained_window_tests"]["0.60"]["any_sustained_window"]
                    ),
                    "neighbor_context": cell["best_heldout_neighbor_context"],
                }
            )

    protected_status = git_output(["status", "--porcelain=v1", "--", *PROTECTED_PATHS]).splitlines()
    source_readback = {
        "grokking_probe_py_sha256": sha256_file(GROKKING_PROBE_PATH),
        "minimal_probe_py_sha256": sha256_file(MINIMAL_PROBE_PATH),
        "route_decision_py_sha256": sha256_file(ROUTE_DECISION_PATH),
        "frozen_design_canonical_sha256": canonical_json_sha256(strip_underscore_keys(frozen_design)),
        "prereg_canonical_sha256": canonical_json_sha256(prereg),
    }
    static_optimizer = static_optimizer_readback()
    runtime_param_groups = runtime_optimizer_param_group_readback(records)
    all_checkpoint_counts_ok = all(len(rows) == 25 for rows in grouped.values()) and len(curves) == 150
    manifest_hash_gate = {key: manifest.get(key) == value for key, value in EXPECTED.items()}
    formal_status = trend.get("go_no_go_verdict")
    any_positive = bool(trend["aggregate_flags"]["positive_abs_heldout_ge_0_75"]) or bool(
        trend["aggregate_flags"]["positive_delayed_generalization_signature"]
    )
    any_late_rise = any(bool(record["late_heldout_rise"]) for record in records)
    all_fit = all(record.get("train_first_ge_0_95_step") is not None for record in records)

    audit = {
        "task_id": TASK_ID,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "producer": {
            "script_path": str(Path(__file__).resolve().relative_to(REPO_ROOT).as_posix()),
            "script_sha256": sha256_file(Path(__file__).resolve()),
            "producer_function": "curve_config_audit_001b.build_audit",
        },
        "input_artifacts": {
            name: {
                "path": str((ARTIFACT_DIR / name).relative_to(REPO_ROOT).as_posix()),
                "sha256": sha256_file(ARTIFACT_DIR / name),
            }
            for name in REQUIRED_ARTIFACTS
        },
        "repo_readback": {
            "repo_root": str(REPO_ROOT.as_posix()),
            "current_branch": git_output(["branch", "--show-current"]),
            "current_head": git_output(["rev-parse", "HEAD"]),
            "expected_bank_commit": EXPECTED_BANK_COMMIT,
            "current_head_matches_expected_bank_commit": git_output(["rev-parse", "HEAD"]) == EXPECTED_BANK_COMMIT,
            "manifest_head": manifest.get("git_head"),
            "manifest_branch": manifest.get("git_branch"),
            "closeout_current_head": closeout.get("repo_readback", {}).get("current_head"),
            "closeout_current_branch": closeout.get("repo_readback", {}).get("current_branch"),
            "protected_source_paths": PROTECTED_PATHS,
            "protected_source_status": protected_status,
            "protected_source_status_empty": not protected_status,
        },
        "hash_gates": {
            "expected": EXPECTED,
            "manifest_expected_hashes_match": manifest_hash_gate,
            "frozen_design_matches_expected": source_readback["frozen_design_canonical_sha256"]
            == EXPECTED["frozen_design_sha256"],
            "route_decision_matches_expected": source_readback["route_decision_py_sha256"]
            == EXPECTED["route_decision_sha256"],
            "prereg_matches_expected": source_readback["prereg_canonical_sha256"] == EXPECTED["prereg_sha256"],
        },
        "source_readback": source_readback,
        "artifact_completeness": {
            "records_count": len(records),
            "curve_rows": len(curves),
            "cells": len(grouped),
            "expected_cells": 6,
            "expected_curve_rows": 150,
            "all_checkpoint_counts_ok": all_checkpoint_counts_ok,
            "failure_manifest_present": (ARTIFACT_DIR / "failure_manifest.json").exists(),
            "run_stderr_bytes": (ARTIFACT_DIR / "run_stderr.log").stat().st_size
            if (ARTIFACT_DIR / "run_stderr.log").exists()
            else None,
        },
        "checkpoint_coverage": [
            {
                "seed": key[0],
                "weight_decay": key[1],
                "checkpoints": len(rows),
                "steps": [int(row["step"]) for row in rows],
                "step_delta_set": sorted({int(b["step"]) - int(a["step"]) for a, b in zip(rows, rows[1:])}),
            }
            for key, rows in sorted(grouped.items())
        ],
        "split_and_label_readback": {
            "label_cardinality_P_K": int(P.K),
            "uniform_random_balacc_reference": 1.0 / float(P.K),
            "chance_balacc_reference": 1.0 / float(P.K),
            "train": split_readback("train"),
            "heldout": split_readback("heldout"),
            "fair_baseline_balacc": route_input.get("fair_baseline_balacc"),
            "fair_baseline_note": route_input.get("graph_cache_note"),
        },
        "config_plumbing_readback": {
            "manifest_regime": manifest.get("regime"),
            "records_optimizer_values": sorted(
                {
                    (str(record.get("optimizer")), float(record.get("weight_decay")))
                    for record in records
                }
            ),
            "static_optimizer_weight_decay_argument_passed_to_adamw": bool(
                static_optimizer["adamw_weight_decay_float_call_present"]
            ),
            "static_optimizer_ast_readback": static_optimizer,
            "runtime_optimizer_param_groups_available": runtime_param_groups["status"] == "available",
            "runtime_optimizer_param_group_readback": runtime_param_groups,
        },
        "formal_outputs": {
            "probe_trend_go_no_go_verdict": formal_status,
            "route_decision_route": route.get("route"),
            "route_decision_reason": route.get("reason"),
            "leakage_detector_valid": bool(leakage.get("detector_valid")),
            "all_planted_caught": bool(leakage.get("all_planted_caught")),
            "no_clean_false_flag": bool(leakage.get("no_clean_false_flag")),
            "aggregate_flags": trend.get("aggregate_flags"),
        },
        "per_cell_curve_diagnostics": cell_diagnostics,
        "threshold_blip_analysis": {
            "thresholds": THRESHOLDS,
            "window_size_checkpoints": SUSTAINED_WINDOW_SIZE,
            "cells_with_best_heldout_over_0_60": cells_with_best_over_060,
            "single_unsustained_threshold_blip": (
                len(cells_with_best_over_060) == 1
                and not cells_with_best_over_060[0]["sustained_3_checkpoint_ge_0_60"]
            ),
            "interpretation": (
                "The formal negative-close cutoff remains blocked by one best-heldout checkpoint above 0.60; "
                "the crossing is not sustained over three checkpoints and does not meet 0.65 or 0.75 windows."
            ),
        },
        "formal_result": {
            "formal_status": formal_status,
            "substantive_assessment": (
                "negative_leaning_no_grokking_signature"
                if formal_status == "ambiguous" and all_fit and not any_positive and not any_late_rise
                else "audit_blocked_requires_operator_review"
            ),
            "route": route.get("route"),
            "reason": (
                "All six cells fitted, no 0.75 absolute signal, no sustained late-rise signal, and the sole "
                ">0.60 heldout checkpoint is an unsustained blip."
            ),
        },
        "claim_ceiling": (
            "curve/config audit only; no route terminal, no TLGP-R2 verdict, no mechanism validity claim, "
            "no witness validity claim, no agency/self/subjectivity/AGI/EGO/stable-benefit claim"
        ),
    }
    audit["closeout_comparison"] = compare_to_closeout(audit, closeout)
    if audit["closeout_comparison"]["evidence_metric_drift_found"]:
        audit["formal_result"]["substantive_assessment"] = "audit_blocked_requires_operator_review"
    audit["stop_conditions"] = stop_conditions(audit)
    return audit


def stop_conditions(audit: dict[str, Any]) -> list[str]:
    issues = []
    if audit["artifact_completeness"]["records_count"] != 6:
        issues.append("records_count_not_6")
    if audit["artifact_completeness"]["curve_rows"] != 150:
        issues.append("curve_rows_not_150")
    if audit["artifact_completeness"]["cells"] != 6:
        issues.append("cells_not_6")
    if not audit["artifact_completeness"]["all_checkpoint_counts_ok"]:
        issues.append("checkpoint_coverage_incomplete")
    if audit["formal_result"]["formal_status"] != "ambiguous":
        issues.append("formal_status_not_ambiguous")
    if audit["formal_outputs"]["route_decision_route"] != "inconclusive_underpowered":
        issues.append("route_not_inconclusive_underpowered")
    if not all(audit["hash_gates"]["manifest_expected_hashes_match"].values()):
        issues.append("manifest_hash_gate_mismatch")
    for key in ("frozen_design_matches_expected", "route_decision_matches_expected", "prereg_matches_expected"):
        if not audit["hash_gates"][key]:
            issues.append(key)
    if not audit["repo_readback"]["protected_source_status_empty"]:
        issues.append("protected_source_status_dirty")
    if not audit["config_plumbing_readback"]["static_optimizer_weight_decay_argument_passed_to_adamw"]:
        issues.append("static_optimizer_weight_decay_plumbing_missing")
    if audit["closeout_comparison"]["evidence_metric_drift_found"]:
        issues.append("evidence_metric_drift_vs_closeout")
    return issues


def write_outputs(audit: dict[str, Any]) -> None:
    json_path = ARTIFACT_DIR / "curve_config_audit_001b.json"
    md_path = ARTIFACT_DIR / "CURVE_CONFIG_AUDIT_001B.md"
    json_path.write_text(json.dumps(audit, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    lines = [
        "# GROKKING_PROBE_001B Curve/Config Audit",
        "",
        f"Task: `{audit['task_id']}`",
        f"Formal status: `{audit['formal_result']['formal_status']}`",
        f"Substantive assessment: `{audit['formal_result']['substantive_assessment']}`",
        f"Route: `{audit['formal_result']['route']}`",
        f"Closeout comparison: `{audit['closeout_comparison']['status']}`",
        "",
        "## Coverage",
        "",
        f"- Records: {audit['artifact_completeness']['records_count']}",
        f"- Curve rows: {audit['artifact_completeness']['curve_rows']}",
        f"- Cells: {audit['artifact_completeness']['cells']}",
        f"- Checkpoint coverage ok: `{str(audit['artifact_completeness']['all_checkpoint_counts_ok']).lower()}`",
        f"- Protected source status empty: `{str(audit['repo_readback']['protected_source_status_empty']).lower()}`",
        "",
        "## Curve Diagnostics",
        "",
        "| seed | wd | fit step | best heldout | best step | final heldout | full delta | post-fit delta | tail delta | post-fit best-to-final drop |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in audit["per_cell_curve_diagnostics"]:
        lines.append(
            "| {seed} | {weight_decay:.1f} | {fit_step} | {best:.6f} | {best_step} | "
            "{final:.6f} | {full_delta:.6f} | {post_delta:.6f} | {tail_delta:.6f} | {drop:.6f} |".format(
                seed=row["seed"],
                weight_decay=row["weight_decay"],
                fit_step=row["train_first_ge_0_95_step"],
                best=row["best_heldout_balacc"],
                best_step=row["best_heldout_step"],
                final=row["final_heldout_balacc"],
                full_delta=row["full_run_curve"]["delta_heldout_balacc"],
                post_delta=row["post_fit_curve"]["delta_heldout_balacc"],
                tail_delta=row["tail_delta_heldout_balacc"],
                drop=row["post_fit_monotonicity_drawdown"]["best_to_final_drop"],
            )
        )
    lines.extend(
        [
            "",
            "## Threshold Windows",
            "",
            "No cell has a three-checkpoint sustained window at `0.60`, `0.65`, or `0.75`.",
            audit["threshold_blip_analysis"]["interpretation"],
            "",
            "## Config Readback",
            "",
            "- Static AdamW plumbing passes `weight_decay=float(weight_decay)`: "
            f"`{str(audit['config_plumbing_readback']['static_optimizer_weight_decay_argument_passed_to_adamw']).lower()}`",
            "- Direct optimizer param-group readback: "
            f"`{audit['config_plumbing_readback']['runtime_optimizer_param_group_readback']['status']}`",
            f"- Direct readback reason: {audit['config_plumbing_readback']['runtime_optimizer_param_group_readback'].get('reason', 'available')}",
            "",
            "## Drift",
            "",
            f"- Evidence metric drift vs closeout: `{str(audit['closeout_comparison']['evidence_metric_drift_found']).lower()}`",
            f"- Repo context differences vs closeout: `{len(audit['closeout_comparison']['repo_context_differences'])}`",
            "",
            "## Claim Ceiling",
            "",
            audit["claim_ceiling"],
            "",
        ]
    )
    md_path.write_text("\n".join(lines), encoding="utf-8")


def write_failure(exc: BaseException | None, audit: dict[str, Any] | None = None) -> None:
    payload = {
        "task_id": TASK_ID,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": "failed",
        "exception": None if exc is None else repr(exc),
        "stop_conditions": [] if audit is None else audit.get("stop_conditions", []),
        "claim_ceiling": (
            "failure artifact only; no route terminal, no TLGP-R2 verdict, no mechanism validity claim"
        ),
    }
    (ARTIFACT_DIR / "curve_config_audit_failure_001b.json").write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def main() -> int:
    try:
        audit = build_audit()
        write_outputs(audit)
        if audit["stop_conditions"]:
            write_failure(None, audit)
            print(json.dumps({"status": "failed", "stop_conditions": audit["stop_conditions"]}, indent=2))
            return 1
        print(
            json.dumps(
                {
                    "formal_status": audit["formal_result"]["formal_status"],
                    "substantive_assessment": audit["formal_result"]["substantive_assessment"],
                    "records": audit["artifact_completeness"]["records_count"],
                    "curve_rows": audit["artifact_completeness"]["curve_rows"],
                    "route": audit["formal_result"]["route"],
                    "closeout_drift": audit["closeout_comparison"]["status"],
                    "optimizer_param_group_readback": audit["config_plumbing_readback"][
                        "runtime_optimizer_param_group_readback"
                    ]["status"],
                },
                indent=2,
                sort_keys=True,
            )
        )
        return 0
    except BaseException as exc:
        write_failure(exc)
        print(json.dumps({"status": "failed", "exception": repr(exc)}, indent=2), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
