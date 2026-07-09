"""Isolated corrected-gate runner for UNCERTAINTY-VOI-REQUEST-MECHANISM-003A.

003A intentionally reuses the frozen 002A environment, policies, Model-A regret,
Kalman belief, and exploit-pressure KG implementation.  This module changes only
the frozen 003A seed blocks, preregistration identity, corrected G2/G3
collapse/survival gate evaluation, and 003A artifact schema/readback fields.

It is not an EGO runtime path and it does not expose companion / UI / LLM
integration.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import inspect
import json
import os
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Sequence

import numpy as np

from uncertainty_voi import runner_002 as base


TASK_ID = "UNCERTAINTY-VOI-REQUEST-MECHANISM-003A"
EXPECTED_PREREG_SHA256 = "9964fbce108228cf32cd2df8834ed8b002bb27bc210956c3186c3fd7b96a5b26"
CLAIM_CEILING = (
    "Bounded VOI mechanism-proxy in one toy; not intelligence / adaptation / "
    "world-model / subject; not a claim about the pet. Strongest positive outcome "
    "= a bounded, replayable, attribution-checked VOI-mechanism-proxy that beats "
    "a tuned static rival and a random-active baseline on this hold-and-observe "
    "toy, with advantage collapsing under corrupted feedback and uncertainty "
    "ablation. Calibration is not claimed if the verdict is UNCALIBRATED."
)
VERDICT_SET = {
    "VOI_MECHANISM_PRESENT",
    "VOI_MECHANISM_PRESENT_UNCALIBRATED",
    "SIMPLE_ACTIVE_SUFFICIENT",
    "STATIC_SUFFICIENT",
    "ATTRIBUTION_FAILURE",
    "INSTRUMENT_INVALID",
    "CAPABILITY_ABSENT",
}


RestlessGaussianBanditWorld = base.RestlessGaussianBanditWorld
EpisodeResult = base.EpisodeResult
simulate_policy = base.simulate_policy
choose_mechanism_action = base.choose_mechanism_action
sha256_lf = base.sha256_lf
assert_seed_blocks_disjoint = base.assert_seed_blocks_disjoint


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class FrozenConfig(base.FrozenConfig):
    task_id: str = TASK_ID
    scored_seeds: tuple[int, ...] = field(default_factory=lambda: tuple(range(9401, 9421)))
    transfer_seeds: tuple[int, ...] = field(default_factory=lambda: tuple(range(9421, 9431)))
    tuning_seeds: tuple[int, ...] = field(default_factory=lambda: tuple(range(9301, 9311)))
    probe_seed: int = 9001
    prereg_path: Path = field(
        default_factory=lambda: _repo_root()
        / "artifacts"
        / TASK_ID
        / "preregistration.md"
    )
    artifact_dir: Path = field(default_factory=lambda: _repo_root() / "artifacts" / TASK_ID)


def code_path_hash(func: Any) -> str:
    try:
        source = inspect.getsource(func)
    except (OSError, TypeError):
        source = repr(func)
    return sha256_lf(source)


def source_file_sha256() -> str:
    return sha256_lf(Path(__file__).read_bytes())


def runner_002_source_sha256() -> str:
    return sha256_lf(Path(base.__file__).read_bytes())


def _ci_lower(stats: dict[str, Any]) -> float:
    return float(stats["ci95"][0])


def _ci_upper(stats: dict[str, Any]) -> float:
    return float(stats["ci95"][1])


def control_survives(control_advantage_stats: dict[str, Any]) -> bool:
    """Corrected 003A survival predicate: control remains significantly positive."""

    return _ci_lower(control_advantage_stats) > 0.0


def control_collapse_signature(
    control_advantage_stats: dict[str, Any],
    clean_minus_control_stats: dict[str, Any],
) -> dict[str, Any]:
    """Corrected 003A collapse predicate.

    Collapse accepts parity or negative control advantage, provided the clean
    advantage drops significantly relative to the control.
    """

    upper_le_zero = _ci_upper(control_advantage_stats) <= 0.0
    lower_drop_positive = _ci_lower(clean_minus_control_stats) > 0.0
    survived = control_survives(control_advantage_stats)
    return {
        "control_ci_upper_le_zero": bool(upper_le_zero),
        "clean_minus_control_ci_lower_gt_zero": bool(lower_drop_positive),
        "collapsed": bool(upper_le_zero and lower_drop_positive),
        "survived": bool(survived),
    }


def _normalize_trace_rows(trace_rows: Sequence[dict[str, Any]]) -> list[dict[str, Any]]:
    normalized: list[dict[str, Any]] = []
    for row in trace_rows:
        out = copy.deepcopy(row)
        out["task_id"] = TASK_ID
        normalized.append(out)
    return normalized


def tune_static_threshold(cfg: FrozenConfig | None = None) -> dict[str, Any]:
    cfg = cfg or FrozenConfig()
    out = dict(base.tune_static_threshold(cfg))
    out["producer_function"] = "uncertainty_voi.runner_003.tune_static_threshold"
    out["code_path_hash"] = code_path_hash(tune_static_threshold)
    out["reused_callable"] = "uncertainty_voi.runner_002.tune_static_threshold"
    out["reused_callable_code_path_hash"] = base.code_path_hash(base.tune_static_threshold)
    return out


def _condition_results(
    condition_policy_id: str,
    seeds: Sequence[int],
    cfg: FrozenConfig,
    static_params: dict[str, int],
    *,
    trace_mechanism: bool = False,
) -> dict[str, Any]:
    out = dict(
        base._condition_results(
            condition_policy_id,
            seeds,
            cfg,
            static_params,
            trace_mechanism=trace_mechanism,
        )
    )
    out["trace_rows"] = _normalize_trace_rows(out.get("trace_rows", []))
    out["producer_function"] = "uncertainty_voi.runner_003._condition_results"
    out["reused_callable"] = "uncertainty_voi.runner_002._condition_results"
    return out


def _floor_results(seeds: Sequence[int], cfg: FrozenConfig) -> dict[str, Any]:
    return base._floor_results(seeds, cfg)


def replay_trace(trace_rows: Sequence[dict[str, Any]], cfg: FrozenConfig | None = None) -> dict[str, Any]:
    report = dict(base.replay_trace(trace_rows, cfg or FrozenConfig()))
    report["producer_function"] = "uncertainty_voi.runner_003.replay_trace"
    report["code_path_hash"] = code_path_hash(replay_trace)
    report["reused_callable"] = "uncertainty_voi.runner_002.replay_trace"
    report["reused_callable_code_path_hash"] = base.code_path_hash(base.replay_trace)
    return report


def _tamper_replay_control(trace_rows: Sequence[dict[str, Any]], cfg: FrozenConfig) -> dict[str, Any]:
    if not trace_rows:
        return {"detected": False, "reason": "no_trace_rows"}
    tampered = [copy.deepcopy(row) for row in trace_rows]
    tampered[0]["action"] = {"kind": "noop"} if tampered[0]["action"].get("kind") != "noop" else {"kind": "query", "arm": 0}
    report = replay_trace(tampered, cfg)
    return {
        "detected": not report["bit_exact"],
        "mismatch_sample": report["mismatches"][:3],
    }


def scan_rng_source(source: str) -> dict[str, Any]:
    return base.scan_rng_source(source)


def run_rng_audit() -> dict[str, Any]:
    source = Path(__file__).read_text(encoding="utf-8-sig")
    positive_control = "import numpy as np\nx = np.random.default_rng().normal()\n"
    clean = scan_rng_source(source)
    pc = scan_rng_source(positive_control)
    return {
        "producer_function": "uncertainty_voi.runner_003.run_rng_audit",
        "code_path_hash": code_path_hash(run_rng_audit),
        "scanned_module": "uncertainty_voi.runner_003",
        "clean_scan": clean,
        "positive_control": {
            "source": positive_control,
            "detected": not pc["passed"],
            "violations": pc["violations"],
        },
        "passed": clean["passed"] and (not pc["passed"]),
        "aggregation_rule": "actual 003A source must be clean and synthetic unseeded default_rng positive control must be detected",
    }


def _paired_stats(values: Sequence[float], cfg: FrozenConfig, *, label: str) -> dict[str, Any]:
    return base._paired_stats(values, cfg, label=label)


def _ci_excludes_zero_positive(stats: dict[str, Any]) -> bool:
    return base._ci_excludes_zero_positive(stats)


def _cost_projection(cfg: FrozenConfig, probe_start: float, probe_elapsed: float) -> dict[str, Any]:
    return base._cost_projection(cfg, probe_start, probe_elapsed)


def _drop_trace(payload: dict[str, Any]) -> dict[str, Any]:
    out = dict(payload)
    out.pop("trace_rows", None)
    return out


def _compute_core_payload(cfg: FrozenConfig) -> dict[str, Any]:
    assert_seed_blocks_disjoint(cfg)
    probe_start = time.perf_counter()
    probe_mechanism = simulate_policy("mechanism", cfg.probe_seed, cfg)
    probe_static_params = {"theta": int(cfg.static_theta_grid[0]), "request_period": int(cfg.static_request_period_grid[0])}
    probe_static = simulate_policy("static_threshold", cfg.probe_seed, cfg, static_params=probe_static_params)
    probe_elapsed = time.perf_counter() - probe_start
    projection = _cost_projection(cfg, probe_start, probe_elapsed)
    if not projection["within_budget"]:
        return {
            "task_id": TASK_ID,
            "stopped": True,
            "stop_reason": "CPU_PROJECTION_EXCEEDS_PRESET_BUDGET",
            "probe": {
                "seed": cfg.probe_seed,
                "mechanism_regret": probe_mechanism.regret,
                "static_regret_default": probe_static.regret,
            },
            "cost_projection": projection,
        }

    tuning = tune_static_threshold(cfg)
    static_params = tuning["best_params"]

    clean = _condition_results("mechanism", cfg.scored_seeds, cfg, static_params, trace_mechanism=True)
    wrong = _condition_results("wrong_sign", cfg.scored_seeds, cfg, static_params)
    shuffled = _condition_results("shuffled", cfg.scored_seeds, cfg, static_params)
    uncertainty = _condition_results("uncertainty_ablation", cfg.scored_seeds, cfg, static_params)
    value = _condition_results("value_ablation", cfg.scored_seeds, cfg, static_params)
    transfer = _condition_results("mechanism", cfg.transfer_seeds, cfg, static_params)
    floors = _floor_results(cfg.scored_seeds, cfg)
    rng_audit = run_rng_audit()

    clean_adv = np.asarray(clean["advantages_vs_better_rival"], dtype=float)
    wrong_adv = np.asarray(wrong["advantages_vs_better_rival"], dtype=float)
    shuffled_adv = np.asarray(shuffled["advantages_vs_better_rival"], dtype=float)
    uncertainty_adv = np.asarray(uncertainty["advantages_vs_better_rival"], dtype=float)
    value_adv = np.asarray(value["advantages_vs_better_rival"], dtype=float)

    wrong_collapse = _paired_stats((clean_adv - wrong_adv).tolist(), cfg, label="003A:collapse:wrong")
    shuffled_collapse = _paired_stats((clean_adv - shuffled_adv).tolist(), cfg, label="003A:collapse:shuffled")
    uncertainty_collapse = _paired_stats((clean_adv - uncertainty_adv).tolist(), cfg, label="003A:collapse:uncertainty")
    value_collapse = _paired_stats((clean_adv - value_adv).tolist(), cfg, label="003A:collapse:value")

    wrong_signature = control_collapse_signature(wrong["advantage_better_rival_stats"], wrong_collapse)
    shuffled_signature = control_collapse_signature(shuffled["advantage_better_rival_stats"], shuffled_collapse)
    uncertainty_signature = control_collapse_signature(uncertainty["advantage_better_rival_stats"], uncertainty_collapse)
    value_load_bearing = _ci_lower(value_collapse) > 0.0

    mean_static = float(np.mean(clean["static_regrets"]))
    mean_mech = float(np.mean(clean["mechanism_regrets"]))
    mean_random = float(np.mean(clean["random_active_regrets"]))
    mean_hold = float(floors["hold_only"]["mean_regret"])
    mean_no_update = float(floors["no_update"]["mean_regret"])
    rel_advantage_static = float(clean["advantage_static_stats"]["mean"] / mean_static) if mean_static > 0 else 0.0
    rel_advantage_random = float(clean["advantage_random_active_stats"]["mean"] / mean_random) if mean_random > 0 else 0.0
    calibration = clean["calibration"]

    total_mechanism_actions = max(1, sum(int(v) for v in clean["mechanism_action_counts"].values()))
    exploit_fraction = float(clean["mechanism_action_counts"].get("noop", 0) / total_mechanism_actions)
    zero_delta_controls = {
        "wrong_sign": bool(np.all((clean_adv - wrong_adv) == 0.0)),
        "shuffled": bool(np.all((clean_adv - shuffled_adv) == 0.0)),
        "uncertainty_ablation": bool(np.all((clean_adv - uncertainty_adv) == 0.0)),
        "value_ablation": bool(np.all((clean_adv - value_adv) == 0.0)),
    }
    tripwire_fired = bool((not (0.02 < exploit_fraction < 0.98)) or any(zero_delta_controls.values()))

    gates = {
        "G1a_static_rival": {
            "passed": bool(_ci_excludes_zero_positive(clean["advantage_static_stats"]) and rel_advantage_static >= 0.10),
            "mean_relative_advantage": rel_advantage_static,
            "advantage_stats": clean["advantage_static_stats"],
            "mde_relative_advantage": 0.10,
        },
        "G1b_random_active_rival": {
            "passed": bool(_ci_excludes_zero_positive(clean["advantage_random_active_stats"]) and rel_advantage_random >= 0.10),
            "mean_relative_advantage": rel_advantage_random,
            "advantage_stats": clean["advantage_random_active_stats"],
            "mde_relative_advantage": 0.10,
        },
        "G2_falsifiers": {
            "passed": bool(wrong_signature["collapsed"] and shuffled_signature["collapsed"]),
            "wrong_sign_advantage_stats": wrong["advantage_better_rival_stats"],
            "shuffled_advantage_stats": shuffled["advantage_better_rival_stats"],
            "clean_minus_wrong_sign": wrong_collapse,
            "clean_minus_shuffled": shuffled_collapse,
            "collapse_signature": {
                "wrong_sign": wrong_signature,
                "shuffled": shuffled_signature,
            },
            "survival_signature": {
                "wrong_sign": wrong_signature["survived"],
                "shuffled": shuffled_signature["survived"],
            },
            "corrected_rule": "collapse iff A_C ci95 upper <= 0 and clean_minus_control ci95 lower > 0; survival iff A_C ci95 lower > 0",
        },
        "G3_ablations": {
            "passed": bool(uncertainty_signature["collapsed"] and value_load_bearing),
            "uncertainty_ablation_advantage_stats": uncertainty["advantage_better_rival_stats"],
            "value_ablation_advantage_stats": value["advantage_better_rival_stats"],
            "clean_minus_uncertainty_ablation": uncertainty_collapse,
            "clean_minus_value_ablation": value_collapse,
            "collapse_signature": {
                "uncertainty_ablation": uncertainty_signature,
            },
            "survival_signature": {
                "uncertainty_ablation": uncertainty_signature["survived"],
            },
            "value_load_bearing": bool(value_load_bearing),
            "corrected_rule": "uncertainty_ablation must collapse; value_ablation is load-bearing iff clean_minus_value ci95 lower > 0",
        },
        "G4a_calibration": {
            "passed": bool(calibration["mean_z2"] is not None and 0.7 <= float(calibration["mean_z2"]) <= 1.5),
            "mean_z2": calibration["mean_z2"],
            "coverage90_fraction": calibration["coverage90_fraction"],
            "tolerance": [0.7, 1.5],
        },
        "G4b_transfer": {
            "passed": bool(_ci_excludes_zero_positive(transfer["advantage_better_rival_stats"])),
            "advantage_stats": transfer["advantage_better_rival_stats"],
        },
        "G6_headroom": {
            "passed": bool(
                mean_hold >= 2.0 * mean_mech
                and mean_no_update >= 2.0 * mean_mech
                and mean_hold >= 2.0 * mean_random
            ),
            "floor_ratios": {
                "hold_only_over_mechanism": float(mean_hold / mean_mech) if mean_mech > 0 else None,
                "no_update_over_mechanism": float(mean_no_update / mean_mech) if mean_mech > 0 else None,
                "hold_only_over_random_active": float(mean_hold / mean_random) if mean_random > 0 else None,
            },
            "oracle_regret": 0.0,
        },
        "tripwire": {
            "passed": not tripwire_fired,
            "exploit_noop_fraction": exploit_fraction,
            "required_open_interval": [0.02, 0.98],
            "zero_delta_controls": zero_delta_controls,
        },
    }

    trace_rows = clean["trace_rows"]
    replay = replay_trace(trace_rows, cfg)
    tamper = _tamper_replay_control(trace_rows, cfg)
    trace_size_bytes = sum(len(json.dumps(base._json_ready(row), sort_keys=True, separators=(",", ":"))) + 1 for row in trace_rows)
    gates["G5_replay_rng_trace"] = {
        "passed": bool(replay["bit_exact"] and tamper["detected"] and rng_audit["passed"] and trace_size_bytes <= cfg.trace_size_cap_bytes),
        "replay_bit_exact": replay["bit_exact"],
        "tamper_negative_control_detected": tamper["detected"],
        "rng_audit_passed": rng_audit["passed"],
        "trace_size_bytes": int(trace_size_bytes),
        "trace_size_cap_bytes": int(cfg.trace_size_cap_bytes),
    }

    verdict, subtype, positive_claim = _derive_verdict(gates, mean_mech, mean_hold, mean_no_update)
    return {
        "task_id": TASK_ID,
        "stopped": False,
        "probe": {
            "seed": cfg.probe_seed,
            "mechanism_regret": probe_mechanism.regret,
            "static_regret_default": probe_static.regret,
        },
        "cost_projection": projection,
        "tuning": tuning,
        "clean": _drop_trace(clean),
        "wrong_sign": _drop_trace(wrong),
        "shuffled": _drop_trace(shuffled),
        "uncertainty_ablation": _drop_trace(uncertainty),
        "value_ablation": _drop_trace(value),
        "transfer": _drop_trace(transfer),
        "floors": floors,
        "gates": gates,
        "replay_report": {**replay, "tamper_negative_control": tamper},
        "rng_audit": rng_audit,
        "trace_rows": trace_rows,
        "trace_size_bytes": int(trace_size_bytes),
        "verdict": verdict,
        "verdict_subtype": subtype,
        "positive_claim": bool(positive_claim),
        "exploit_noop_fraction": exploit_fraction,
        "tripwire": gates["tripwire"],
    }


def _derive_verdict(
    gates: dict[str, Any],
    mean_mech: float,
    mean_hold: float,
    mean_no_update: float,
) -> tuple[str, str, bool]:
    g1a = bool(gates["G1a_static_rival"]["passed"])
    g1b = bool(gates["G1b_random_active_rival"]["passed"])
    g2 = bool(gates["G2_falsifiers"]["passed"])
    g3 = bool(gates["G3_ablations"]["passed"])
    g4a = bool(gates["G4a_calibration"]["passed"])
    g4b = bool(gates["G4b_transfer"]["passed"])
    g5 = bool(gates["G5_replay_rng_trace"]["passed"])
    g6 = bool(gates["G6_headroom"]["passed"])
    tripwire = bool(gates["tripwire"]["passed"])
    falsifier_or_uncertainty_survived = bool(
        any(gates["G2_falsifiers"]["survival_signature"].values())
        or gates["G3_ablations"]["survival_signature"]["uncertainty_ablation"]
    )
    if not g5:
        return "INSTRUMENT_INVALID", "G5_REPLAY_RNG_TRACE_FAILED", False
    if not tripwire:
        return "INSTRUMENT_INVALID", "MECHANISM_INERT", False
    if not g6:
        return "INSTRUMENT_INVALID", "G6_HEADROOM_FAILED", False
    if mean_mech >= min(mean_hold, mean_no_update):
        return "CAPABILITY_ABSENT", "MECHANISM_NOT_BETTER_THAN_FLOORS", False
    if g1a and g1b and g2 and g3 and g4a and g4b and g5 and g6 and tripwire:
        return "VOI_MECHANISM_PRESENT", "ALL_GATES_PASS", True
    if g1a and g1b and g2 and g3 and (not g4a) and g4b and g5 and g6 and tripwire:
        return "VOI_MECHANISM_PRESENT_UNCALIBRATED", "G4A_CALIBRATION_FAILED", True
    if not g1b:
        return "SIMPLE_ACTIVE_SUFFICIENT", "G1B_RANDOM_ACTIVE_RIVAL_FAILED", False
    if not g1a:
        return "STATIC_SUFFICIENT", "G1A_STATIC_RIVAL_FAILED", False
    if (g1a and g1b) and falsifier_or_uncertainty_survived:
        return "ATTRIBUTION_FAILURE", "FALSIFIER_OR_UNCERTAINTY_SURVIVED", False
    return "INSTRUMENT_INVALID", "UNCLASSIFIED_GATE_FAILURE", False


def canonical_json_bytes(payload: Any) -> bytes:
    return json.dumps(base._json_ready(payload), sort_keys=True, separators=(",", ":")).encode("utf-8")


def _payload_digest(payload: Any) -> str:
    return hashlib.sha256(canonical_json_bytes(payload)).hexdigest()


def _core_for_digest(core: dict[str, Any]) -> dict[str, Any]:
    return {
        key: value
        for key, value in core.items()
        if key
        not in {
            "trace_rows",
            "replay_report",
            "rng_audit",
            "cost_projection",
        }
    }


def _fresh_process_recompute(cfg: FrozenConfig, expected_digest: str) -> dict[str, Any]:
    if cfg.fresh_process_recompute_count <= 0:
        return {
            "fresh_process_recompute_count": 0,
            "bit_exact": True,
            "digests": [],
            "skipped": True,
        }
    digests: list[str] = []
    outputs: list[dict[str, Any]] = []
    with tempfile.TemporaryDirectory() as tmp:
        for i in range(cfg.fresh_process_recompute_count):
            out = Path(tmp) / f"recompute_{i}.json"
            env = os.environ.copy()
            src_path = str(_repo_root() / "src")
            env["PYTHONPATH"] = src_path + os.pathsep + env.get("PYTHONPATH", "")
            subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "uncertainty_voi.runner_003",
                    "--mode",
                    "recompute",
                    "--json-output",
                    str(out),
                ],
                cwd=_repo_root(),
                env=env,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            payload = json.loads(out.read_text(encoding="utf-8"))
            digests.append(str(payload["core_digest"]))
            outputs.append(payload)
    return {
        "producer_function": "uncertainty_voi.runner_003._fresh_process_recompute",
        "code_path_hash": code_path_hash(_fresh_process_recompute),
        "fresh_process_recompute_count": int(cfg.fresh_process_recompute_count),
        "expected_digest": expected_digest,
        "digests": digests,
        "bit_exact": all(d == expected_digest for d in digests),
        "outputs": outputs,
    }


def _build_metric_record(
    *,
    metric_id: str,
    producer_function: str,
    value: Any,
    input_artifacts: Sequence[str],
    seeds: Sequence[int],
    aggregation_rule: str,
    code_hash: str,
) -> dict[str, Any]:
    return {
        "metric_id": metric_id,
        "producer_function": producer_function,
        "input_artifacts": list(input_artifacts),
        "run_id": TASK_ID,
        "seed_ids": [int(s) for s in seeds],
        "aggregation_rule": aggregation_rule,
        "code_path_hash": code_hash,
        "value": value,
    }


def _metric_records(
    cfg: FrozenConfig,
    core: dict[str, Any],
    replay_report: dict[str, Any],
    config_shas: dict[str, str],
) -> list[dict[str, Any]]:
    return [
        _build_metric_record(
            metric_id="clean_advantage_vs_static_and_random_active",
            producer_function="uncertainty_voi.runner_003._condition_results",
            value={
                "G1a_static": core["clean"]["advantage_static_stats"],
                "G1b_random_active": core["clean"]["advantage_random_active_stats"],
                "better_rival": core["clean"]["advantage_better_rival_stats"],
            },
            input_artifacts=["preregistration.md"],
            seeds=cfg.scored_seeds,
            aggregation_rule="paired bootstrap mean CIs vs static_threshold, random_active, and per-seed better rival",
            code_hash=code_path_hash(_condition_results),
        ),
        _build_metric_record(
            metric_id="static_threshold_tuning",
            producer_function="uncertainty_voi.runner_003.tune_static_threshold",
            value=core["tuning"]["best_params"],
            input_artifacts=["preregistration.md"],
            seeds=cfg.tuning_seeds,
            aggregation_rule=core["tuning"]["aggregation_rule"],
            code_hash=code_path_hash(tune_static_threshold),
        ),
        _build_metric_record(
            metric_id="G2_corrected_falsifier_collapse",
            producer_function="uncertainty_voi.runner_003._derive_verdict",
            value=core["gates"]["G2_falsifiers"],
            input_artifacts=["falsifier_report.json"],
            seeds=cfg.scored_seeds,
            aggregation_rule="collapse iff A_C ci95 upper <= 0 and clean_minus_control ci95 lower > 0; survival iff A_C ci95 lower > 0",
            code_hash=code_path_hash(_derive_verdict),
        ),
        _build_metric_record(
            metric_id="G3_corrected_ablation_collapse",
            producer_function="uncertainty_voi.runner_003._derive_verdict",
            value=core["gates"]["G3_ablations"],
            input_artifacts=["ablation_report.json"],
            seeds=cfg.scored_seeds,
            aggregation_rule="uncertainty ablation must collapse; value ablation must significantly reduce clean advantage",
            code_hash=code_path_hash(_derive_verdict),
        ),
        _build_metric_record(
            metric_id="G4_calibration_transfer",
            producer_function="uncertainty_voi.runner_003._derive_verdict",
            value={"G4a": core["gates"]["G4a_calibration"], "G4b": core["gates"]["G4b_transfer"]},
            input_artifacts=["calibration_transfer_report.json"],
            seeds=tuple(cfg.scored_seeds) + tuple(cfg.transfer_seeds),
            aggregation_rule="offline calibration diagnostic plus transfer paired CI against better rival",
            code_hash=code_path_hash(_derive_verdict),
        ),
        _build_metric_record(
            metric_id="G5_replay_rng_trace",
            producer_function="uncertainty_voi.runner_003.replay_trace",
            value=core["gates"]["G5_replay_rng_trace"],
            input_artifacts=["trace.jsonl", "replay_report.json"],
            seeds=cfg.scored_seeds,
            aggregation_rule="trace replay recomputes action/state and RNG audit positive control fires",
            code_hash=code_path_hash(replay_trace),
        ),
        _build_metric_record(
            metric_id="fresh_process_recompute",
            producer_function="uncertainty_voi.runner_003._fresh_process_recompute",
            value=replay_report.get("fresh_process_recompute", {}),
            input_artifacts=["result.json"],
            seeds=tuple(cfg.scored_seeds) + tuple(cfg.transfer_seeds) + tuple(cfg.tuning_seeds),
            aggregation_rule="two fresh-process core recomputes must match canonical core digest",
            code_hash=code_path_hash(_fresh_process_recompute),
        ),
        _build_metric_record(
            metric_id="config_shas",
            producer_function="uncertainty_voi.runner_003.sha256_lf",
            value=config_shas,
            input_artifacts=["preregistration.md", "runner_003.py", "runner_002.py"],
            seeds=[],
            aggregation_rule="LF-normalized SHA-256 readback",
            code_hash=base.code_path_hash(sha256_lf),
        ),
    ]


def _failure_manifest(core: dict[str, Any], replay_report: dict[str, Any]) -> dict[str, Any]:
    failures: list[dict[str, Any]] = []
    for gate_id, gate in core["gates"].items():
        if not gate.get("passed", False):
            failures.append({"gate": gate_id, "status": "failed", "details": gate})
    if core["verdict"] not in {"VOI_MECHANISM_PRESENT", "VOI_MECHANISM_PRESENT_UNCALIBRATED"}:
        failures.append(
            {
                "verdict": core["verdict"],
                "subtype": core["verdict_subtype"],
                "status": "non_positive_or_invalid_boundary",
            }
        )
    if not replay_report.get("fresh_process_recompute", {}).get("bit_exact", True):
        failures.append({"gate": "fresh_process_recompute", "status": "failed"})
    return {
        "task_id": TASK_ID,
        "producer_function": "uncertainty_voi.runner_003._failure_manifest",
        "code_path_hash": code_path_hash(_failure_manifest),
        "failures": failures,
        "stop_conditions_triggered": failures,
        "claim_ceiling": CLAIM_CEILING,
    }


def _build_artifacts_payload(cfg: FrozenConfig, core: dict[str, Any], replay_report: dict[str, Any]) -> dict[str, Any]:
    prereg_sha = sha256_lf(cfg.prereg_path.read_bytes())
    code_hash = source_file_sha256()
    config_shas = {
        "preregistration_lf_sha256": prereg_sha,
        "runner_003_source_lf_sha256": code_hash,
        "runner_002_source_lf_sha256": runner_002_source_sha256(),
    }
    records = _metric_records(cfg, core, replay_report, config_shas)
    run_id = f"{TASK_ID}:R3:{_payload_digest(_core_for_digest(core))[:12]}"
    result = {
        "task_id": TASK_ID,
        "producer_function": "uncertainty_voi.runner_003.run_gate",
        "code_path_hash": code_path_hash(run_gate),
        "verdict": core["verdict"],
        "verdict_subtype": core["verdict_subtype"],
        "positive_claim": bool(core["positive_claim"]),
        "claim_ceiling": CLAIM_CEILING,
        "config_shas": config_shas,
        "run_id": run_id,
        "seed_blocks": {
            "probe": [cfg.probe_seed],
            "tuning": list(cfg.tuning_seeds),
            "scored": list(cfg.scored_seeds),
            "transfer": list(cfg.transfer_seeds),
        },
        "static_threshold_params": core["tuning"]["best_params"],
        "exploit_noop_fraction": core["exploit_noop_fraction"],
        "gates": core["gates"],
        "advantage_tables": {
            "clean_vs_static": core["clean"]["advantage_static_stats"],
            "clean_vs_random_active": core["clean"]["advantage_random_active_stats"],
            "clean_vs_better_rival": core["clean"]["advantage_better_rival_stats"],
            "wrong_sign_vs_better_rival": core["wrong_sign"]["advantage_better_rival_stats"],
            "shuffled_vs_better_rival": core["shuffled"]["advantage_better_rival_stats"],
            "uncertainty_ablation_vs_better_rival": core["uncertainty_ablation"]["advantage_better_rival_stats"],
            "value_ablation_vs_better_rival": core["value_ablation"]["advantage_better_rival_stats"],
            "transfer_vs_better_rival": core["transfer"]["advantage_better_rival_stats"],
        },
        "collapse_survival": {
            "G2": {
                "collapse_signature": core["gates"]["G2_falsifiers"]["collapse_signature"],
                "survival_signature": core["gates"]["G2_falsifiers"]["survival_signature"],
            },
            "G3": {
                "collapse_signature": core["gates"]["G3_ablations"]["collapse_signature"],
                "survival_signature": core["gates"]["G3_ablations"]["survival_signature"],
                "value_load_bearing": core["gates"]["G3_ablations"]["value_load_bearing"],
            },
        },
        "cost_projection": core["cost_projection"],
    }
    baseline_comparison = {
        "task_id": TASK_ID,
        "producer_function": "uncertainty_voi.runner_003._build_artifacts_payload/baseline_comparison",
        "code_path_hash": code_hash,
        "static_threshold_tuning": core["tuning"],
        "clean_scored": core["clean"],
        "floors": core["floors"],
        "oracle": core["floors"]["oracle"],
        "claim_ceiling": CLAIM_CEILING,
    }
    ablation_report = {
        "task_id": TASK_ID,
        "producer_function": "uncertainty_voi.runner_003._build_artifacts_payload/ablation_report",
        "code_path_hash": code_hash,
        "uncertainty_ablation": core["uncertainty_ablation"],
        "value_ablation": core["value_ablation"],
        "gate": core["gates"]["G3_ablations"],
        "collapse_signature": core["gates"]["G3_ablations"]["collapse_signature"],
        "survival_signature": core["gates"]["G3_ablations"]["survival_signature"],
        "value_load_bearing": core["gates"]["G3_ablations"]["value_load_bearing"],
        "claim_ceiling": CLAIM_CEILING,
    }
    falsifier_report = {
        "task_id": TASK_ID,
        "producer_function": "uncertainty_voi.runner_003._build_artifacts_payload/falsifier_report",
        "code_path_hash": code_hash,
        "wrong_sign": core["wrong_sign"],
        "shuffled": core["shuffled"],
        "gate": core["gates"]["G2_falsifiers"],
        "collapse_signature": core["gates"]["G2_falsifiers"]["collapse_signature"],
        "survival_signature": core["gates"]["G2_falsifiers"]["survival_signature"],
        "claim_ceiling": CLAIM_CEILING,
    }
    calibration_transfer_report = {
        "task_id": TASK_ID,
        "producer_function": "uncertainty_voi.runner_003._build_artifacts_payload/calibration_transfer_report",
        "code_path_hash": code_hash,
        "G4a": core["gates"]["G4a_calibration"],
        "G4b": core["gates"]["G4b_transfer"],
        "transfer": core["transfer"],
        "claim_ceiling": CLAIM_CEILING,
    }
    headroom_report = {
        "task_id": TASK_ID,
        "producer_function": "uncertainty_voi.runner_003._build_artifacts_payload/headroom_report",
        "code_path_hash": code_hash,
        "G6": core["gates"]["G6_headroom"],
        "floors": core["floors"],
        "static_mean_regret": float(np.mean(core["clean"]["static_regrets"])),
        "random_active_mean_regret": float(np.mean(core["clean"]["random_active_regrets"])),
        "mechanism_mean_regret": float(np.mean(core["clean"]["mechanism_regrets"])),
        "oracle_regret": 0.0,
        "claim_ceiling": CLAIM_CEILING,
    }
    tripwire_report = {
        "task_id": TASK_ID,
        "producer_function": "uncertainty_voi.runner_003._build_artifacts_payload/tripwire_report",
        "code_path_hash": code_hash,
        "tripwire": core["tripwire"],
        "mechanism_action_counts": core["clean"]["mechanism_action_counts"],
        "claim_ceiling": CLAIM_CEILING,
    }
    metric_records = {
        "task_id": TASK_ID,
        "producer_function": "uncertainty_voi.runner_003._metric_records",
        "code_path_hash": code_path_hash(_metric_records),
        "records": records,
    }
    failure_manifest = _failure_manifest(core, replay_report)
    return {
        "result.json": result,
        "baseline_comparison.json": baseline_comparison,
        "ablation_report.json": ablation_report,
        "falsifier_report.json": falsifier_report,
        "calibration_transfer_report.json": calibration_transfer_report,
        "headroom_report.json": headroom_report,
        "tripwire_report.json": tripwire_report,
        "replay_report.json": replay_report,
        "metric_records.json": metric_records,
        "failure_manifest.json": failure_manifest,
    }


def _write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(base._json_ready(payload), indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")


def _write_artifacts(output_dir: Path, payloads: dict[str, Any], trace_rows: Sequence[dict[str, Any]]) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    for name, payload in payloads.items():
        if name == "failure_manifest.json" and not payload["failures"]:
            continue
        _write_json(output_dir / name, payload)
    with (output_dir / "trace.jsonl").open("w", encoding="utf-8", newline="\n") as handle:
        for row in trace_rows:
            handle.write(json.dumps(base._json_ready(row), sort_keys=True, separators=(",", ":")) + "\n")
    (output_dir / "claim_ceiling.txt").write_text(CLAIM_CEILING + "\n", encoding="utf-8", newline="\n")


def run_gate(
    *,
    cfg: FrozenConfig | None = None,
    output_dir: Path | None = None,
    write_artifacts: bool = True,
    include_fresh_process: bool = False,
) -> dict[str, Any]:
    cfg = cfg or FrozenConfig()
    prereg_sha = sha256_lf(cfg.prereg_path.read_bytes())
    if prereg_sha != EXPECTED_PREREG_SHA256:
        raise RuntimeError(f"frozen prereg SHA mismatch: {prereg_sha}")
    core = _compute_core_payload(cfg)
    if core.get("stopped"):
        if write_artifacts and output_dir:
            output_dir.mkdir(parents=True, exist_ok=True)
            _write_json(output_dir / "failure_manifest.json", core)
        return core
    core_digest = _payload_digest(_core_for_digest(core))
    replay_report = dict(core["replay_report"])
    if include_fresh_process:
        fresh = _fresh_process_recompute(cfg, core_digest)
        replay_report["fresh_process_recompute"] = fresh
        core["gates"]["G5_replay_rng_trace"]["fresh_process_bit_exact"] = bool(fresh["bit_exact"])
        core["gates"]["G5_replay_rng_trace"]["passed"] = bool(core["gates"]["G5_replay_rng_trace"]["passed"] and fresh["bit_exact"])
        if not fresh["bit_exact"]:
            core["verdict"] = "INSTRUMENT_INVALID"
            core["verdict_subtype"] = "FRESH_PROCESS_RECOMPUTE_FAILED"
            core["positive_claim"] = False
    else:
        replay_report["fresh_process_recompute"] = {
            "fresh_process_recompute_count": 0,
            "bit_exact": True,
            "skipped": True,
        }
    payloads = _build_artifacts_payload(cfg, core, replay_report)
    if write_artifacts:
        _write_artifacts(output_dir or cfg.artifact_dir, payloads, core["trace_rows"])
    return {
        **core,
        "core_digest": core_digest,
        "artifact_payloads": _drop_trace({"payloads": payloads})["payloads"],
        "replay_report": replay_report,
    }


def recompute_core_digest(cfg: FrozenConfig | None = None) -> dict[str, Any]:
    cfg = cfg or FrozenConfig()
    core = _compute_core_payload(cfg)
    if core.get("stopped"):
        digest_payload = core
    else:
        digest_payload = _core_for_digest(core)
    return {
        "task_id": TASK_ID,
        "core_digest": _payload_digest(digest_payload),
        "stopped": bool(core.get("stopped", False)),
        "verdict": core.get("verdict"),
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=["official", "recompute", "rng-audit"], default="official")
    parser.add_argument("--output", type=Path, default=FrozenConfig().artifact_dir)
    parser.add_argument("--json-output", type=Path)
    args = parser.parse_args(argv)
    if args.mode == "rng-audit":
        payload = run_rng_audit()
    elif args.mode == "recompute":
        payload = recompute_core_digest(FrozenConfig())
    else:
        payload = run_gate(cfg=FrozenConfig(), output_dir=args.output, write_artifacts=True, include_fresh_process=True)
        payload = {
            "task_id": TASK_ID,
            "verdict": payload["verdict"],
            "verdict_subtype": payload["verdict_subtype"],
            "positive_claim": payload["positive_claim"],
            "core_digest": payload["core_digest"],
            "trace_size_bytes": payload["trace_size_bytes"],
            "artifact_dir": str(args.output),
        }
    if args.json_output:
        _write_json(args.json_output, payload)
    else:
        print(json.dumps(base._json_ready(payload), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
