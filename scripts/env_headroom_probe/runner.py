"""CLI for the Phase-A borrow-first environment headroom probe."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from . import TASK_ID
from .adapters import ADAPTERS, record_digest
from .battery import probe_valid_gate, run_battery, stable_digest
from .contract import CONTROL_EXPECTED_VERDICTS, EQUIVALENCE_BAND, build_prereg_contract

OFFICIAL_ENVS = {"POS_INTERNAL_ESTAR", "NEG_5A846D5_SCOUT"}
CONTROL_ENVS = ("POS_INTERNAL_ESTAR", "NEG_5A846D5_SCOUT")
DEFAULT_ARTIFACT_DIR = Path("artifacts") / TASK_ID
PHASE_BI_STATUS = "PHASE_BI_CONTROLS_ONLY"

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
    parser.add_argument("--mode", choices=["contract", "recompute", "score"], default="contract")
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


def _fresh_process_recomputes(*, seed: int, expected_digest: str) -> dict[str, Any]:
    command = [
        sys.executable,
        "-m",
        "scripts.env_headroom_probe.runner",
        "--mode",
        "score",
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
        "compared_digest_scope": "score_controls_payload excluding replay_report and filesystem artifact paths",
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
