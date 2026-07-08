"""CLI for the Phase-A borrow-first environment headroom probe."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from . import TASK_ID
from .adapters import ADAPTERS, build_borrowed_adapter_manifest, record_digest
from .battery import code_path_hash, probe_valid_gate, run_battery, stable_digest
from .contract import CONTROL_EXPECTED_VERDICTS, EQUIVALENCE_BAND, build_prereg_contract

OFFICIAL_ENVS = {"POS_INTERNAL_ESTAR", "NEG_5A846D5_SCOUT"}
CONTROL_ENVS = ("POS_INTERNAL_ESTAR", "NEG_5A846D5_SCOUT")
DEFAULT_ARTIFACT_DIR = Path("artifacts") / TASK_ID
PHASE_BI_STATUS = "PHASE_BI_CONTROLS_ONLY"
PHASE_BIII_STATUS = "PHASE_BIII_BORROWED_ENV_NEGATIVE_BANK"
STEP_B_CLAIM_CEILING = """BORROW-FIRST env-selection STEP-B (B-iii): bounded NEGATIVE. No borrowed symbolic env cleared the
headroom bar under the frozen fair floor. bsuite memory_len/0, memory_size/0, umbrella_length/0 =
SATURATED_BY_LEGAL_OBSERVATION_DECODER (target trivially decodable from the full legal observation
history; interface-level determination under the equal-access full-history O, NOT a universal claim
about bsuite). MiniGrid MemoryS13Random + KeyCorridorS3R1 = DROP_INVALID_TARGET_NOT_O_DETERMINED.
dm_alchemy = DROP_UNAVAILABLE. probe_valid = true (POS E* = HEADROOM, NEG 5a846d5 = SATURATED). The
only HEADROOM is the internal bespoke control E*, a privileged-ceiling gap per R4(a), NOT
mechanism-relevant. Proves env-selection headroom bits + probe-validity only. Does NOT prove
mechanism validity, learning, transfer, survival, agency, autonomy, emotion, self-awareness,
consciousness, or EGO/companion readiness."""

MODE_CONFIGS: tuple[dict[str, Any], ...] = (
    {
        "mode": "normal",
        "include_graph_closure": True,
        "shuffle_targets": False,
    },
    {
        "mode": "drop_graph_closure",
        "include_graph_closure": False,
        "shuffle_targets": False,
    },
    {
        "mode": "shuffle_o_y",
        "include_graph_closure": True,
        "shuffle_targets": True,
    },
)


def _json_dump(data: Any) -> None:
    sys.stdout.write(json.dumps(data, indent=2, sort_keys=True) + "\n")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--mode",
        choices=["contract", "recompute", "score", "bank"],
        default="contract",
    )
    parser.add_argument("--env", default="UNIT_SYNTHETIC")
    parser.add_argument("--seed", type=int, default=20260708)
    parser.add_argument("--drop-graph-closure", action="store_true")
    parser.add_argument("--shuffle-o-y", action="store_true")
    parser.add_argument("--emit-artifacts", action="store_true")
    parser.add_argument("--artifact-dir", default=str(DEFAULT_ARTIFACT_DIR))
    parser.add_argument(
        "--phase-b-authorized",
        action="store_true",
        help="Required for registered controls/candidates; Phase A tests do not use it.",
    )
    return parser


def _write_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.write_text(
        "".join(json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n" for row in rows),
        encoding="utf-8",
    )


def _score_digest(payload: dict[str, Any]) -> str:
    without_digest = dict(payload)
    without_digest.pop("score_digest", None)
    return stable_digest(without_digest)


def _control_hard_gates(
    per_control: dict[str, dict[str, Any]],
    probe_valid: dict[str, Any],
) -> dict[str, Any]:
    failures: list[dict[str, Any]] = []

    pos = per_control["POS_INTERNAL_ESTAR"]
    pos_verdict = pos["normal"]["verdict"]["verdict"]
    pos_floor_degenerate = bool(pos["normal"]["floor_competence"]["floor_degenerate"])
    if pos_verdict != "HEADROOM":
        failures.append(
            {
                "gate": "POS_INTERNAL_ESTAR_VERDICT",
                "expected": "HEADROOM",
                "observed": pos_verdict,
            }
        )
    if pos_floor_degenerate:
        failures.append(
            {
                "gate": "POS_INTERNAL_ESTAR_FLOOR_COMPETENCE",
                "expected": "floor_degenerate == False",
                "observed": pos["normal"]["floor_competence"],
            }
        )

    neg = per_control["NEG_5A846D5_SCOUT"]
    neg_verdict = neg["normal"]["verdict"]["verdict"]
    if neg_verdict != "SATURATED":
        failures.append(
            {
                "gate": "NEG_5A846D5_SCOUT_VERDICT",
                "expected": "SATURATED",
                "observed": neg_verdict,
            }
        )

    if not bool(probe_valid["probe_valid"]):
        failures.append(
            {
                "gate": "PROBE_VALID",
                "expected": True,
                "observed": probe_valid,
            }
        )

    for env_id, control in per_control.items():
        shuffle_report = control["shuffle_o_y"]["shuffle_leakage"]
        if not bool(shuffle_report["shuffle_leakage_ok"]):
            failures.append(
                {
                    "gate": f"{env_id}_SHUFFLE_LEAKAGE",
                    "expected": "shuffle_leakage_ok == True",
                    "observed": shuffle_report,
                }
            )

    return {
        "producer_function": "_control_hard_gates",
        "passed": not failures,
        "failures": failures,
        "policy": "STOP_WRITE_FAILURE_MANIFEST" if failures else "CONTROLS_CALIBRATION_ADMISSIBLE",
    }


def _battery_trace_rows(
    *,
    env_id: str,
    adapter_source: str,
    adapter_status: str,
    input_record_digest: str,
    mode: str,
    battery: dict[str, Any],
    run_id: str,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for baseline_id, raw_score in sorted(battery["scores"].items()):
        rows.append(
            {
                "producer_function": "_battery_trace_rows",
                "task_id": TASK_ID,
                "phase": PHASE_BI_STATUS,
                "run_id": run_id,
                "env_id": env_id,
                "adapter_source": adapter_source,
                "adapter_status": adapter_status,
                "input_record_digest": input_record_digest,
                "mode": mode,
                "baseline_id": baseline_id,
                "raw_score": raw_score,
                "seed": battery["seed"],
                "seed_report": battery["seed_report"],
                "aggregation_rule": "mean set-F1 over eval records",
                "battery_code_path_hash": battery["code_path_hash"],
                "include_graph_closure": battery["include_graph_closure"],
                "shuffle_targets": battery["shuffle_targets"],
            }
        )
    return rows


def score_controls_payload(*, seed: int) -> dict[str, Any]:
    """Run controls-only Phase B-i scoring without writing artifacts."""

    run_id = f"{TASK_ID}/phase_bi_controls/seed-{int(seed)}"
    per_control: dict[str, dict[str, Any]] = {}
    trace_rows: list[dict[str, Any]] = []

    for env_id in CONTROL_ENVS:
        adapter = ADAPTERS[env_id]
        records = adapter.build_records(int(seed))
        input_digest = record_digest(records)
        mode_results: dict[str, Any] = {
            "adapter_source": adapter.source,
            "adapter_status": adapter.status,
            "input_record_digest": input_digest,
        }
        for config in MODE_CONFIGS:
            battery = run_battery(
                records,
                seed=int(seed),
                include_graph_closure=bool(config["include_graph_closure"]),
                shuffle_targets=bool(config["shuffle_targets"]),
            )
            mode_name = str(config["mode"])
            mode_results[mode_name] = battery
            trace_rows.extend(
                _battery_trace_rows(
                    env_id=env_id,
                    adapter_source=adapter.source,
                    adapter_status=adapter.status,
                    input_record_digest=input_digest,
                    mode=mode_name,
                    battery=battery,
                    run_id=run_id,
                )
            )
        per_control[env_id] = mode_results

    control_verdicts = {
        env_id: per_control[env_id]["normal"]["verdict"]["verdict"]
        for env_id in CONTROL_ENVS
    }
    probe_valid = probe_valid_gate(control_verdicts)
    hard_gates = _control_hard_gates(per_control, probe_valid)

    baseline_comparison = {
        "producer_function": "score_controls_payload.baseline_comparison",
        "run_id": run_id,
        "per_control": {
            env_id: {
                "scores": control["normal"]["scores"],
                "verdict": control["normal"]["verdict"],
                "floor_competence": control["normal"]["floor_competence"],
                "prediction_variation": control["normal"]["prediction_variation"],
            }
            for env_id, control in per_control.items()
        },
    }
    ablation_report = {
        "producer_function": "score_controls_payload.ablation_report",
        "run_id": run_id,
        "per_control": {
            env_id: {
                "drop_graph_closure": {
                    "normal_verdict": control["normal"]["verdict"]["verdict"],
                    "drop_graph_closure_verdict": control["drop_graph_closure"]["verdict"]["verdict"],
                    "flipped": (
                        control["normal"]["verdict"]["verdict"]
                        != control["drop_graph_closure"]["verdict"]["verdict"]
                    ),
                    "scores": control["drop_graph_closure"]["scores"],
                    "verdict": control["drop_graph_closure"]["verdict"],
                },
                "shuffle_o_y": {
                    "scores": control["shuffle_o_y"]["scores"],
                    "verdict": control["shuffle_o_y"]["verdict"],
                    "shuffle_leakage": control["shuffle_o_y"]["shuffle_leakage"],
                    "floor_competence": control["shuffle_o_y"]["floor_competence"],
                },
            }
            for env_id, control in per_control.items()
        },
    }

    controls_result = {
        "producer_function": "score_controls_payload.controls_result",
        "task_id": TASK_ID,
        "phase": PHASE_BI_STATUS,
        "run_id": run_id,
        "scope": "registered_controls_only",
        "candidate_envs_scored": [],
        "equivalence_band": EQUIVALENCE_BAND,
        "control_expected_verdicts": dict(CONTROL_EXPECTED_VERDICTS),
        "control_verdicts": control_verdicts,
        "probe_valid": probe_valid,
        "hard_gates": hard_gates,
        "per_control": {
            env_id: {
                "normal_verdict": control["normal"]["verdict"],
                "floor_competence": control["normal"]["floor_competence"],
                "drop_graph_closure_verdict": control["drop_graph_closure"]["verdict"],
                "shuffle_leakage": control["shuffle_o_y"]["shuffle_leakage"],
                "adapter_source": control["adapter_source"],
                "adapter_status": control["adapter_status"],
                "input_record_digest": control["input_record_digest"],
            }
            for env_id, control in per_control.items()
        },
    }

    payload = {
        "producer_function": "score_controls_payload",
        "task_id": TASK_ID,
        "phase": PHASE_BI_STATUS,
        "run_id": run_id,
        "seed": int(seed),
        "control_envs": list(CONTROL_ENVS),
        "candidate_envs_scored": [],
        "controls_result": controls_result,
        "baseline_comparison": baseline_comparison,
        "ablation_report": ablation_report,
        "probe_valid": probe_valid,
        "trace_rows": trace_rows,
        "claim_ceiling": (
            "controls-only probe calibration; no borrowed headroom, no mechanism, "
            "no learning, no mainline effect"
        ),
    }
    payload["score_digest"] = _score_digest(payload)
    return payload


def _borrowed_env_verdict_from_manifest_entry(
    env_id: str,
    entry: dict[str, Any],
) -> str:
    """Derive the B-iii borrowed-env verdict from frozen B-ii-R1 manifest data."""

    if "oracle_from_O_admission" in entry:
        guard = entry["oracle_from_O_admission"]["trivial_floor_guard"]["guard"]
        if guard == "VOID_TRIVIALLY_DECODABLE":
            return "SATURATED_BY_LEGAL_OBSERVATION_DECODER"
        if guard == "DROP_INVALID_ADAPTER":
            return "DROP_INVALID_TARGET_NOT_O_DETERMINED"
        raise ValueError(f"{env_id} has unrecognized trivial floor guard: {guard}")

    action = str(entry.get("action", ""))
    reason = str(entry.get("reason", ""))
    if action == "DROP_INVALID_NOT_SINGLE_OBS_ADAPTABLE_BEFORE_SCORING":
        return "DROP_INVALID_TARGET_NOT_O_DETERMINED"
    if action == "DROP_OPTIONAL_ADAPTER_BEFORE_SCORING" and (
        "unavailable" in reason.lower() or "not feasible" in reason.lower()
    ):
        return "DROP_UNAVAILABLE"
    raise ValueError(f"{env_id} has unrecognized borrowed drop entry: {entry}")


def _borrowed_admission_summary(manifest: dict[str, Any]) -> dict[str, Any]:
    """Summarize borrowed adapter admission determinations without rescoring."""

    summary: dict[str, Any] = {}
    for env_id, row in sorted(manifest["wired_adapters"].items()):
        admission = row["oracle_from_O_admission"]
        verdict = _borrowed_env_verdict_from_manifest_entry(env_id, row)
        summary[env_id] = {
            "producer_function": "_borrowed_admission_summary",
            "source": row["source"],
            "status": row["status"],
            "record_count": row["record_count"],
            "record_digest": row["record_digest"],
            "oracle_from_O": admission["oracle_from_O"],
            "trivial_floor_guard": admission["trivial_floor_guard"],
            "floor_member_status": row["floor_member_status"],
            "verdict": verdict,
            "verdict_derivation": "trivial_floor_guard.guard == VOID_TRIVIALLY_DECODABLE",
            "candidate_scoring_performed": False,
        }
    for env_id, row in sorted(manifest["dropped_adapters"].items()):
        verdict = _borrowed_env_verdict_from_manifest_entry(env_id, row)
        summary[env_id] = {
            "producer_function": "_borrowed_admission_summary",
            "source": "borrowed_adapter_manifest.dropped_adapters",
            "status": "dropped_before_scoring",
            "drop_action": row["action"],
            "drop_reason": row["reason"],
            "verdict": verdict,
            "verdict_derivation": "drop action/reason from B-ii-R1 manifest",
            "candidate_scoring_performed": False,
        }
    return dict(sorted(summary.items()))


def _dependency_pins_for_env(env_id: str, manifest: dict[str, Any]) -> dict[str, Any]:
    pins = manifest["dependency_pins"]
    if env_id.startswith("bsuite:"):
        names = ("bsuite", "dm_env")
    elif env_id.startswith("minigrid:"):
        names = ("minigrid", "gymnasium")
    elif env_id.startswith("dm_alchemy:"):
        names = ("dm_alchemy", "symbolic_alchemy")
    else:
        names = tuple()
    return {name: pins[name] for name in names if name in pins}


def _reuse_matrix(
    *,
    borrowed_summary: dict[str, Any],
    manifest: dict[str, Any],
) -> dict[str, Any]:
    matrix: dict[str, Any] = {}
    for env_id, row in sorted(borrowed_summary.items()):
        reason = row.get("drop_reason")
        if reason is None:
            reason = row["trivial_floor_guard"]["reason"]
        matrix[env_id] = {
            "producer_function": "_reuse_matrix",
            "source": row["source"],
            "pinned_dependencies": _dependency_pins_for_env(env_id, manifest),
            "borrow_granularity": "PRINCIPLE-only",
            "verdict": row["verdict"],
            "drop_or_saturate_reason": reason,
            "provenance_clean_attestation": (
                "aggregation-only from score_controls_payload and "
                "build_borrowed_adapter_manifest; no new decoder, target, floor, "
                "threshold, or verdict rule"
            ),
        }
    return {
        "producer_function": "_reuse_matrix",
        "phase": PHASE_BIII_STATUS,
        "per_borrowed_env": matrix,
    }


def _borrowed_admission_trace_rows(
    *,
    borrowed_summary: dict[str, Any],
    manifest: dict[str, Any],
    seed: int,
    run_id: str,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    adapter_code_hash = code_path_hash()
    for env_id, row in sorted(borrowed_summary.items()):
        oracle = row.get("oracle_from_O", {})
        trace_source = {
            "env_id": env_id,
            "summary": row,
            "dependency_pins": _dependency_pins_for_env(env_id, manifest),
        }
        rows.append(
            {
                "producer_function": "_borrowed_admission_trace_rows",
                "task_id": TASK_ID,
                "phase": PHASE_BIII_STATUS,
                "run_id": run_id,
                "env_id": env_id,
                "adapter_sha256": stable_digest(trace_source),
                "adapter_code_path_hash": adapter_code_hash,
                "decoder_name": oracle.get("decoder", "not_applicable_dropped_before_record_building"),
                "input_boundary": oracle.get(
                    "input_boundary",
                    "not_applicable_dropped_before_record_building",
                ),
                "admission_score": oracle.get("score"),
                "admission_ceiling": oracle.get("ceiling"),
                "verdict": row["verdict"],
                "seed": int(seed),
                "rng_record": {
                    "seed": int(seed),
                    "record_count": row.get("record_count"),
                    "record_digest": row.get("record_digest"),
                    "source_phase": manifest["phase"],
                    "dropped_before_record_building": "oracle_from_O" not in row,
                },
            }
        )
    return rows


def _bank_hard_gates(
    *,
    controls_payload: dict[str, Any],
    per_env_verdicts: dict[str, str],
) -> dict[str, Any]:
    failures: list[dict[str, Any]] = []
    probe_valid = controls_payload["probe_valid"]
    if not bool(probe_valid["probe_valid"]):
        failures.append(
            {
                "gate": "PROBE_VALID",
                "expected": True,
                "observed": probe_valid,
            }
        )

    control_verdicts = controls_payload["controls_result"]["control_verdicts"]
    for env_id, expected in CONTROL_EXPECTED_VERDICTS.items():
        if control_verdicts.get(env_id) != expected:
            failures.append(
                {
                    "gate": f"{env_id}_EXPECTED_VERDICT",
                    "expected": expected,
                    "observed": control_verdicts.get(env_id),
                }
            )

    for env_id, control in controls_payload["ablation_report"]["per_control"].items():
        shuffle = control["shuffle_o_y"]["shuffle_leakage"]
        if not bool(shuffle["shuffle_leakage_ok"]):
            failures.append(
                {
                    "gate": f"{env_id}_SHUFFLE_LEAKAGE",
                    "expected": "shuffle_leakage_ok == True",
                    "observed": shuffle,
                }
            )

    borrowed_headroom = [
        env_id
        for env_id, verdict in sorted(per_env_verdicts.items())
        if env_id not in CONTROL_ENVS and verdict == "HEADROOM"
    ]
    if borrowed_headroom:
        failures.append(
            {
                "gate": "NO_BORROWED_HEADROOM",
                "expected": [],
                "observed": borrowed_headroom,
            }
        )

    non_pos_headroom = [
        env_id
        for env_id, verdict in sorted(per_env_verdicts.items())
        if verdict == "HEADROOM" and env_id != "POS_INTERNAL_ESTAR"
    ]
    if non_pos_headroom:
        failures.append(
            {
                "gate": "ONLY_POS_INTERNAL_ESTAR_READS_HEADROOM",
                "expected": ["POS_INTERNAL_ESTAR"],
                "observed": non_pos_headroom,
            }
        )

    return {
        "producer_function": "_bank_hard_gates",
        "passed": not failures,
        "failures": failures,
        "policy": "BANK_STEP_B_NEGATIVE" if not failures else "STOP_DO_NOT_BANK_PASS",
    }


def bank_step_b_payload(*, seed: int) -> dict[str, Any]:
    """Build the B-iii aggregation-only bounded-negative bank payload."""

    run_id = f"{TASK_ID}/phase_biii_negative_bank/seed-{int(seed)}"
    controls_payload = score_controls_payload(seed=int(seed))
    borrowed_manifest = build_borrowed_adapter_manifest(seed=int(seed))
    borrowed_summary = _borrowed_admission_summary(borrowed_manifest)

    per_env_verdicts = dict(controls_payload["controls_result"]["control_verdicts"])
    per_env_verdicts.update(
        {env_id: row["verdict"] for env_id, row in sorted(borrowed_summary.items())}
    )
    headroom_envs = [
        env_id for env_id, verdict in sorted(per_env_verdicts.items()) if verdict == "HEADROOM"
    ]
    borrowed_headroom_envs = [
        env_id
        for env_id in headroom_envs
        if env_id not in CONTROL_ENVS
    ]
    hard_gates = _bank_hard_gates(
        controls_payload=controls_payload,
        per_env_verdicts=per_env_verdicts,
    )
    overall_verdict = (
        "BOUNDED_NEGATIVE_NO_BORROWED_HEADROOM"
        if hard_gates["passed"]
        else "BLOCKED_DO_NOT_BANK_PASS"
    )
    reuse_matrix = _reuse_matrix(
        borrowed_summary=borrowed_summary,
        manifest=borrowed_manifest,
    )
    borrowed_trace_rows = _borrowed_admission_trace_rows(
        borrowed_summary=borrowed_summary,
        manifest=borrowed_manifest,
        seed=int(seed),
        run_id=run_id,
    )
    baseline_comparison = dict(controls_payload["baseline_comparison"])
    baseline_comparison["producer_function"] = "bank_step_b_payload.baseline_comparison"
    baseline_comparison["phase"] = PHASE_BIII_STATUS
    baseline_comparison["borrowed_admission_summary"] = borrowed_summary

    result = {
        "producer_function": "bank_step_b_payload.result",
        "task_id": TASK_ID,
        "phase": PHASE_BIII_STATUS,
        "run_id": run_id,
        "seed": int(seed),
        "probe_valid": controls_payload["probe_valid"],
        "control_verdicts": controls_payload["controls_result"]["control_verdicts"],
        "per_env_verdicts": dict(sorted(per_env_verdicts.items())),
        "headroom_envs": headroom_envs,
        "borrowed_headroom_envs": borrowed_headroom_envs,
        "overall_verdict": overall_verdict,
        "only_headroom_is_internal_control_estar": headroom_envs == ["POS_INTERNAL_ESTAR"],
        "claim_ceiling": STEP_B_CLAIM_CEILING,
        "candidate_envs_scored": [],
    }
    payload = {
        "producer_function": "bank_step_b_payload",
        "task_id": TASK_ID,
        "phase": PHASE_BIII_STATUS,
        "run_id": run_id,
        "seed": int(seed),
        "candidate_envs_scored": [],
        "probe_valid": controls_payload["probe_valid"],
        "control_verdicts": controls_payload["controls_result"]["control_verdicts"],
        "per_env_verdicts": dict(sorted(per_env_verdicts.items())),
        "headroom_envs": headroom_envs,
        "borrowed_headroom_envs": borrowed_headroom_envs,
        "overall_verdict": overall_verdict,
        "hard_gates": hard_gates,
        "result": result,
        "reuse_matrix": reuse_matrix,
        "baseline_comparison": baseline_comparison,
        "trace_rows": controls_payload["trace_rows"] + borrowed_trace_rows,
        "borrowed_adapter_manifest_digest": stable_digest(borrowed_manifest),
        "controls_score_digest": controls_payload["score_digest"],
        "claim_ceiling": STEP_B_CLAIM_CEILING,
    }
    payload["score_digest"] = _score_digest(payload)
    return payload


def _fresh_process_recomputes(
    *,
    seed: int,
    expected_digest: str,
    mode: str = "score",
) -> dict[str, Any]:
    if mode not in {"score", "bank"}:
        raise ValueError(f"unsupported fresh-process recompute mode: {mode}")
    command = [
        sys.executable,
        "-m",
        "scripts.env_headroom_probe.runner",
        "--mode",
        mode,
        "--phase-b-authorized",
        "--seed",
        str(int(seed)),
    ]
    runs: list[dict[str, Any]] = []
    for index in range(2):
        proc = subprocess.run(
            command,
            text=True,
            capture_output=True,
            encoding="utf-8-sig",
        )
        run: dict[str, Any] = {
            "index": index,
            "returncode": proc.returncode,
            "command": command,
            "stdout_digest": stable_digest({"stdout": proc.stdout}),
            "stderr": proc.stderr,
        }
        try:
            payload = json.loads(proc.stdout)
            run["score_digest"] = payload.get("score_digest")
            run["parsed"] = True
        except json.JSONDecodeError as exc:
            run["parsed"] = False
            run["parse_error"] = str(exc)
        runs.append(run)

    digests = [run.get("score_digest") for run in runs]
    bit_exact = all(
        run.get("parsed") is True
        and run.get("returncode") == 0
        and run.get("score_digest") == expected_digest
        for run in runs
    ) and len(set(digests)) == 1

    return {
        "producer_function": "_fresh_process_recomputes",
        "fresh_process_recompute_count": 2,
        "expected_score_digest": expected_digest,
        "runs": runs,
        "bit_exact": bit_exact,
        "compared_digest_scope": (
            "bank_step_b_payload controls + borrowed determinations excluding replay_report "
            "and filesystem artifact paths"
            if mode == "bank"
            else "score_controls_payload excluding replay_report and filesystem artifact paths"
        ),
    }


def emit_score_artifacts(*, artifact_dir: Path, seed: int) -> dict[str, Any]:
    payload = score_controls_payload(seed=seed)
    replay_report = _fresh_process_recomputes(
        seed=seed,
        expected_digest=payload["score_digest"],
    )
    artifact_dir.mkdir(parents=True, exist_ok=True)

    all_failures = list(payload["controls_result"]["hard_gates"]["failures"])
    if not replay_report["bit_exact"]:
        all_failures.append(
            {
                "gate": "FRESH_PROCESS_RECOMPUTE",
                "expected": "two fresh-process recomputes bit-exact",
                "observed": replay_report,
            }
        )

    failure_manifest = {
        "producer_function": "emit_score_artifacts.failure_manifest",
        "task_id": TASK_ID,
        "phase": PHASE_BI_STATUS,
        "run_id": payload["run_id"],
        "failures": all_failures,
        "policy": "STOP_DO_NOT_PROCEED" if all_failures else "NO_FAILURES",
    }

    controls_result = dict(payload["controls_result"])
    controls_result["score_digest"] = payload["score_digest"]
    controls_result["replay_bit_exact"] = bool(replay_report["bit_exact"])
    controls_result["artifact_files"] = [
        "controls_result.json",
        "trace.jsonl",
        "baseline_comparison.json",
        "ablation_report.json",
        "replay_report.json",
        "probe_valid.json",
        "claim_ceiling.txt",
    ] + (["failure_manifest.json"] if all_failures else [])

    _write_json(artifact_dir / "controls_result.json", controls_result)
    _write_jsonl(artifact_dir / "trace.jsonl", payload["trace_rows"])
    _write_json(artifact_dir / "baseline_comparison.json", payload["baseline_comparison"])
    _write_json(artifact_dir / "ablation_report.json", payload["ablation_report"])
    _write_json(artifact_dir / "replay_report.json", replay_report)
    _write_json(artifact_dir / "probe_valid.json", payload["probe_valid"])
    (artifact_dir / "claim_ceiling.txt").write_text(
        payload["claim_ceiling"] + "\n",
        encoding="utf-8",
    )
    if all_failures:
        _write_json(artifact_dir / "failure_manifest.json", failure_manifest)

    return {
        "producer_function": "emit_score_artifacts",
        "artifact_dir": str(artifact_dir),
        "score_digest": payload["score_digest"],
        "hard_gates_pass": not all_failures,
        "failure_manifest": failure_manifest,
        "replay_report": replay_report,
        "controls_result": controls_result,
    }


def emit_bank_artifacts(*, artifact_dir: Path, seed: int) -> dict[str, Any]:
    payload = bank_step_b_payload(seed=seed)
    replay_report = _fresh_process_recomputes(
        seed=seed,
        expected_digest=payload["score_digest"],
        mode="bank",
    )
    artifact_dir.mkdir(parents=True, exist_ok=True)

    hard_failures = list(payload["hard_gates"]["failures"])
    replay_failure: dict[str, Any] | None = None
    if not replay_report["bit_exact"]:
        replay_failure = {
            "gate": "FULL_BANK_FRESH_PROCESS_RECOMPUTE",
            "expected": "two fresh-process recomputes of controls + borrowed determinations bit-exact",
            "observed": replay_report,
            "bsuite_rng_nondeterminism": True,
        }
        hard_failures.append(replay_failure)

    dropped_records = [
        {
            "adapter_id": env_id,
            "verdict": row["verdict"],
            "action": row.get("drop_action"),
            "reason": row.get("drop_reason"),
        }
        for env_id, row in payload["baseline_comparison"]["borrowed_admission_summary"].items()
        if row["verdict"].startswith("DROP_")
    ]
    failure_manifest = {
        "producer_function": "emit_bank_artifacts.failure_manifest",
        "task_id": TASK_ID,
        "phase": PHASE_BIII_STATUS,
        "run_id": payload["run_id"],
        "borrowed_drop_records": dropped_records,
        "failures": dropped_records + ([replay_failure] if replay_failure is not None else []),
        "hard_failures": hard_failures,
        "policy": "STOP_DO_NOT_BANK_PASS" if hard_failures else "DROPS_RECORDED_NO_BANK_FAILURES",
    }

    artifact_files = sorted(
        [
            "result.json",
            "reuse_matrix.json",
            "baseline_comparison.json",
            "replay_report.json",
            "trace.jsonl",
            "claim_ceiling.txt",
            "failure_manifest.json",
        ]
    )
    result = dict(payload["result"])
    result["score_digest"] = payload["score_digest"]
    result["replay_bit_exact"] = bool(replay_report["bit_exact"])
    result["artifact_files"] = artifact_files
    result["hard_gates"] = payload["hard_gates"]

    _write_json(artifact_dir / "result.json", result)
    _write_json(artifact_dir / "reuse_matrix.json", payload["reuse_matrix"])
    _write_json(artifact_dir / "baseline_comparison.json", payload["baseline_comparison"])
    _write_json(artifact_dir / "replay_report.json", replay_report)
    _write_jsonl(artifact_dir / "trace.jsonl", payload["trace_rows"])
    (artifact_dir / "claim_ceiling.txt").write_text(
        STEP_B_CLAIM_CEILING + "\n",
        encoding="utf-8",
    )
    _write_json(artifact_dir / "failure_manifest.json", failure_manifest)

    return {
        "producer_function": "emit_bank_artifacts",
        "artifact_dir": str(artifact_dir),
        "score_digest": payload["score_digest"],
        "hard_gates_pass": not hard_failures,
        "failure_manifest": failure_manifest,
        "replay_report": replay_report,
        "result": result,
    }


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.mode == "contract":
        _json_dump(build_prereg_contract())
        return 0

    if args.mode == "score":
        if not args.phase_b_authorized:
            raise SystemExit("controls-only scoring requires --phase-b-authorized")
        if args.env != "UNIT_SYNTHETIC":
            raise SystemExit("--mode score is controls-only; do not pass --env")
        if args.drop_graph_closure or args.shuffle_o_y:
            raise SystemExit("--mode score runs all frozen modes internally")
        if args.emit_artifacts:
            emitted = emit_score_artifacts(
                artifact_dir=Path(args.artifact_dir),
                seed=int(args.seed),
            )
            _json_dump(emitted)
            return 0 if emitted["hard_gates_pass"] else 1
        _json_dump(score_controls_payload(seed=int(args.seed)))
        return 0

    if args.mode == "bank":
        if not args.phase_b_authorized:
            raise SystemExit("STEP-B B-iii banking requires --phase-b-authorized")
        if args.env != "UNIT_SYNTHETIC":
            raise SystemExit("--mode bank is aggregation-only; do not pass --env")
        if args.drop_graph_closure or args.shuffle_o_y:
            raise SystemExit("--mode bank derives the frozen control modes internally")
        if args.emit_artifacts:
            emitted = emit_bank_artifacts(
                artifact_dir=Path(args.artifact_dir),
                seed=int(args.seed),
            )
            _json_dump(emitted)
            return 0 if emitted["hard_gates_pass"] else 1
        _json_dump(bank_step_b_payload(seed=int(args.seed)))
        return 0

    if args.env not in ADAPTERS:
        raise SystemExit(f"unknown env adapter: {args.env}")
    if args.env in OFFICIAL_ENVS and not args.phase_b_authorized:
        raise SystemExit(
            f"{args.env} is a registered control; official scoring requires --phase-b-authorized"
        )
    if args.env != "UNIT_SYNTHETIC" and not args.phase_b_authorized:
        raise SystemExit(
            "borrowed candidate/control recompute requires --phase-b-authorized after Claude Red-audit"
        )

    adapter = ADAPTERS[args.env]
    records = adapter.build_records(int(args.seed))
    battery = run_battery(
        records,
        seed=int(args.seed),
        include_graph_closure=not args.drop_graph_closure,
        shuffle_targets=bool(args.shuffle_o_y),
    )
    payload = {
        "producer_function": "runner.main",
        "mode": "recompute",
        "env": args.env,
        "adapter_source": adapter.source,
        "adapter_status": adapter.status,
        "record_digest": record_digest(records),
        "battery": battery,
    }
    payload["fresh_process_digest"] = stable_digest(payload)
    _json_dump(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
