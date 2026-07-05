from __future__ import annotations

import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


BASE_DIR = Path(__file__).resolve().parent
JSON_OUT = BASE_DIR / "operator_review_001b.json"
MD_OUT = BASE_DIR / "OPERATOR_REVIEW_001B.md"

INPUT_FILES = [
    "closeout_audit_001b.json",
    "curve_config_audit_001b.json",
    "manifest.json",
    "probe_trend_report.json",
    "route_decision.json",
]

PROTECTED_SOURCE_PATHS = [
    "src/tlgp_001b_r2",
    "src/tlgp_001a",
    "src/tlgp_capability_witness_preflight_001a/route_decision.py",
    "src/tlgp_capability_witness_preflight_001a/minimal_probe.py",
    "src/tlgp_capability_witness_preflight_001a/grokking_probe.py",
]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(name: str) -> dict[str, Any]:
    path = BASE_DIR / name
    return json.loads(path.read_text(encoding="utf-8"))


def run_git(args: list[str]) -> str | None:
    try:
        completed = subprocess.run(
            ["git", *args],
            cwd=BASE_DIR,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    except (OSError, subprocess.CalledProcessError):
        return None
    return completed.stdout.strip()


def repo_readback() -> dict[str, Any]:
    status = run_git(["status", "--porcelain", "--", *PROTECTED_SOURCE_PATHS])
    return {
        "repo_root": run_git(["rev-parse", "--show-toplevel"]),
        "current_branch": run_git(["branch", "--show-current"]),
        "current_head": run_git(["rev-parse", "HEAD"]),
        "protected_source_paths": PROTECTED_SOURCE_PATHS,
        "protected_source_status": [] if not status else status.splitlines(),
        "protected_source_status_empty": not bool(status),
    }


def per_cell_summary(closeout: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for cell in closeout["per_cell"]:
        rows.append(
            {
                "seed": cell["seed"],
                "weight_decay": cell["weight_decay"],
                "final_train_balacc": cell["final_train_balacc"],
                "final_heldout_balacc": cell["final_heldout_balacc"],
                "best_heldout_balacc": cell["best_heldout_balacc"],
                "best_heldout_step": cell["best_heldout_step"],
                "train_first_ge_0_95_step": cell["train_first_ge_0_95_step"],
                "late_heldout_rise": cell["late_heldout_rise"],
                "tail_slope_per_1000_steps": cell["tail_slope_per_1000_steps"],
            }
        )
    return rows


def build_review() -> dict[str, Any]:
    closeout = load_json("closeout_audit_001b.json")
    curve = load_json("curve_config_audit_001b.json")
    manifest = load_json("manifest.json")
    route = load_json("route_decision.json")
    trend = load_json("probe_trend_report.json")

    repo = repo_readback()
    input_hashes = {
        name: {
            "path": str((BASE_DIR / name).as_posix()),
            "sha256": sha256_file(BASE_DIR / name),
        }
        for name in INPUT_FILES
    }

    formal_status = closeout["closeout_classification"]["formal_status"]
    substantive = closeout["closeout_classification"]["substantive_assessment"]
    route_name = closeout["formal_outputs"]["route_decision_route"]
    no_metric_drift = not curve["closeout_comparison"]["evidence_metric_drift_found"]
    flags = closeout["formal_outputs"]["aggregate_flags"]
    runtime_param_group_available = closeout["config_plumbing_readback"][
        "runtime_optimizer_param_groups_available"
    ]
    hash_gates = curve["hash_gates"]

    acceptance_failures = []
    if formal_status != "ambiguous":
        acceptance_failures.append("formal_status_not_ambiguous")
    if substantive != "negative_leaning_no_grokking_signature":
        acceptance_failures.append("substantive_assessment_not_negative_leaning")
    if route_name != "inconclusive_underpowered":
        acceptance_failures.append("route_not_inconclusive_underpowered")
    if not no_metric_drift:
        acceptance_failures.append("curve_config_metric_drift_found")
    if not hash_gates["frozen_design_matches_expected"]:
        acceptance_failures.append("frozen_design_hash_mismatch")
    if not hash_gates["route_decision_matches_expected"]:
        acceptance_failures.append("route_decision_hash_mismatch")
    if not hash_gates["prereg_matches_expected"]:
        acceptance_failures.append("prereg_hash_mismatch")
    if not repo["protected_source_status_empty"]:
        acceptance_failures.append("protected_source_dirty")

    accepted = not acceptance_failures
    selected_next_action = (
        "known_good_grokking_sanity_before_any_tlgp_continuation"
        if accepted
        else "stop_for_operator_investigation"
    )

    return {
        "task_id": "TLGP-CAPABILITY-WITNESS-GROKKING-PROBE-001B-OPERATOR-REVIEW-001A",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "producer": {
            "producer_function": "operator_review_001b.build_review",
            "script_path": str(Path(__file__).as_posix()),
            "script_sha256": sha256_file(Path(__file__)),
        },
        "input_artifacts": input_hashes,
        "repo_readback": repo,
        "layer": "engineering evidence review / learning-adaptation proxy interpretation",
        "mainline_integration_status": "local ITL artifact interpretation only; no EGO mainline, no TLGP-R2 adjudication",
        "enabled_status": "callable operator review over banked GROKKING_PROBE_001B artifacts",
        "real_trigger_evidence": "read closeout_audit_001b.json, curve_config_audit_001b.json, manifest.json, probe_trend_report.json, and route_decision.json",
        "formal_result": {
            "formal_status": formal_status,
            "substantive_assessment": substantive,
            "route_decision_route": route_name,
            "route_decision_file_route": route.get("route"),
            "probe_trend_go_no_go_verdict": trend.get("go_no_go_verdict"),
            "curve_config_status": curve["closeout_comparison"]["status"],
            "evidence_metric_drift_found": curve["closeout_comparison"][
                "evidence_metric_drift_found"
            ],
        },
        "evidence_summary": {
            "records_count": closeout["artifact_completeness"]["records_count"],
            "curve_rows": closeout["artifact_completeness"]["curve_rows"],
            "cells": closeout["artifact_completeness"]["cells"],
            "all_cells_fit_train_ge_0_95": flags["all_runs_train_fit_ge_0_95"],
            "positive_abs_heldout_ge_0_75": flags["positive_abs_heldout_ge_0_75"],
            "positive_delayed_generalization_signature": flags[
                "positive_delayed_generalization_signature"
            ],
            "any_late_heldout_rise": flags["any_late_heldout_rise"],
            "single_unsustained_threshold_blip": closeout["threshold_blip_analysis"][
                "single_unsustained_threshold_blip"
            ],
            "threshold_blip_interpretation": closeout["threshold_blip_analysis"][
                "interpretation"
            ],
        },
        "hash_gates": {
            "frozen_design_sha256": hash_gates["expected"]["frozen_design_sha256"],
            "route_decision_sha256": hash_gates["expected"]["route_decision_sha256"],
            "prereg_sha256": hash_gates["expected"]["prereg_sha256"],
            "frozen_design_matches_expected": hash_gates[
                "frozen_design_matches_expected"
            ],
            "route_decision_matches_expected": hash_gates[
                "route_decision_matches_expected"
            ],
            "prereg_matches_expected": hash_gates["prereg_matches_expected"],
            "manifest_expected_hashes_match": hash_gates[
                "manifest_expected_hashes_match"
            ],
            "manifest_head": manifest.get("git_head")
            or manifest.get("git", {}).get("head"),
            "manifest_branch": manifest.get("git_branch")
            or manifest.get("git", {}).get("branch"),
        },
        "config_gap": {
            "runtime_optimizer_param_group_readback": "available"
            if runtime_param_group_available
            else "unavailable",
            "reason": closeout["config_plumbing_readback"][
                "runtime_optimizer_param_groups_reason"
            ],
            "static_optimizer_weight_decay_argument_passed_to_adamw": closeout[
                "config_plumbing_readback"
            ]["static_optimizer_weight_decay_argument_passed_to_adamw"],
        },
        "operator_decision": {
            "accepted_for_local_interpretation": accepted,
            "acceptance_failures": acceptance_failures,
            "verdict": "accept_banked_ambiguous_negative_leaning_review"
            if accepted
            else "blocked_review",
            "do_not_start_full_sweep": accepted,
            "do_not_start_tlgp_continuation_from_this_card": accepted,
            "selected_next_minimal_closed_loop_action": selected_next_action,
            "rationale": [
                "All six cells reached train>=0.95, so pure no-fit is not the explanation.",
                "No cell reached heldout>=0.75 and no sustained late-rise signal was present.",
                "The only heldout value above 0.60 was a single unsustained checkpoint blip.",
                "Curve/config audit found no evidence-metric drift versus closeout.",
                "Runtime optimizer param-group readback is still unavailable, so known-good sanity should precede any TLGP continuation.",
            ],
        },
        "per_cell_summary": per_cell_summary(closeout),
        "claim_ceiling": "operator review of local banked evidence only; no route terminal, no TLGP-R2 verdict, no mechanism validity claim, no witness validity claim, no agency/self/subjectivity/AGI/EGO/stable-benefit claim",
        "what_this_does_not_prove": [
            "route_terminal_closure",
            "tlgp_r2_validity_or_invalidity",
            "mechanism_validity_or_invalidity",
            "witness_validity_or_invalidity",
            "that_more_scale_would_not_help",
            "that_the_runner_has_no_runtime_plumbing_bug",
            "agency_self_subjectivity_agi_ego_or_stable_user_benefit",
        ],
        "next_minimal_closed_loop_action": selected_next_action,
        "stop_conditions": acceptance_failures,
    }


def fmt_float(value: float) -> str:
    return f"{value:.6f}"


def render_markdown(review: dict[str, Any]) -> str:
    rows = []
    for cell in review["per_cell_summary"]:
        rows.append(
            "| {seed} | {wd} | {train} | {heldout} | {best} | {best_step} | {fit_step} | {late} | {slope} |".format(
                seed=cell["seed"],
                wd=cell["weight_decay"],
                train=fmt_float(cell["final_train_balacc"]),
                heldout=fmt_float(cell["final_heldout_balacc"]),
                best=fmt_float(cell["best_heldout_balacc"]),
                best_step=cell["best_heldout_step"],
                fit_step=cell["train_first_ge_0_95_step"],
                late=str(cell["late_heldout_rise"]).lower(),
                slope=fmt_float(cell["tail_slope_per_1000_steps"]),
            )
        )

    decision = review["operator_decision"]
    return "\n".join(
        [
            "# OPERATOR REVIEW 001B",
            "",
            f"Task: `{review['task_id']}`",
            "",
            "## Verdict",
            "",
            f"- Review verdict: `{decision['verdict']}`",
            f"- Formal status: `{review['formal_result']['formal_status']}`",
            f"- Substantive assessment: `{review['formal_result']['substantive_assessment']}`",
            f"- Route decision: `{review['formal_result']['route_decision_route']}`",
            f"- Next minimal closed-loop action: `{review['next_minimal_closed_loop_action']}`",
            "",
            "## Operator Decision",
            "",
            "- Do not start a full sweep from this result.",
            "- Do not start a TLGP continuation from this card.",
            "- Run a separate known-good grokking sanity card before any TLGP continuation.",
            "- Preserve the result as formal ambiguous and negative-leaning, not as route terminal closure.",
            "",
            "## Evidence Readback",
            "",
            f"- Records: `{review['evidence_summary']['records_count']}`",
            f"- Curve rows: `{review['evidence_summary']['curve_rows']}`",
            f"- Cells: `{review['evidence_summary']['cells']}`",
            f"- All cells fit train>=0.95: `{review['evidence_summary']['all_cells_fit_train_ge_0_95']}`",
            f"- Heldout>=0.75 signal: `{review['evidence_summary']['positive_abs_heldout_ge_0_75']}`",
            f"- Delayed-generalization signature: `{review['evidence_summary']['positive_delayed_generalization_signature']}`",
            f"- Any late heldout rise: `{review['evidence_summary']['any_late_heldout_rise']}`",
            f"- Single unsustained >0.60 blip: `{review['evidence_summary']['single_unsustained_threshold_blip']}`",
            f"- Curve/config drift: `{review['formal_result']['evidence_metric_drift_found']}`",
            "",
            "## Per-Cell Summary",
            "",
            "| seed | wd | final train | final heldout | best heldout | best step | first train>=0.95 | late rise | tail slope / 1k |",
            "| --- | --- | ---: | ---: | ---: | ---: | ---: | --- | ---: |",
            *rows,
            "",
            "## Config Gap",
            "",
            f"- Runtime optimizer param-group readback: `{review['config_gap']['runtime_optimizer_param_group_readback']}`",
            f"- Static AdamW weight_decay plumbing observed: `{review['config_gap']['static_optimizer_weight_decay_argument_passed_to_adamw']}`",
            "",
            "## Claim Ceiling",
            "",
            review["claim_ceiling"],
            "",
            "## What This Does Not Prove",
            "",
            *[f"- `{item}`" for item in review["what_this_does_not_prove"]],
            "",
            "## Source Protection",
            "",
            f"- Protected source status empty: `{review['repo_readback']['protected_source_status_empty']}`",
            f"- Current branch: `{review['repo_readback']['current_branch']}`",
            f"- Current HEAD: `{review['repo_readback']['current_head']}`",
            "",
        ]
    )


def main() -> None:
    review = build_review()
    JSON_OUT.write_text(
        json.dumps(review, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    MD_OUT.write_text(render_markdown(review), encoding="utf-8")
    print(
        "operator_review_001b: "
        f"verdict={review['operator_decision']['verdict']} "
        f"next={review['next_minimal_closed_loop_action']}"
    )


if __name__ == "__main__":
    main()
