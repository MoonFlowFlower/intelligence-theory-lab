from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

from itl_devbench.agents.generic_fsm import GenericFSMAgent
from itl_devbench.agents.graph_cache import GraphCacheAgent
from itl_devbench.agents.minimal_loop import MinimalLoopAgent
from itl_devbench.agents.obs_only_policy import ObsOnlyPolicyAgent
from itl_devbench.agents.oracle import OracleAgent
from itl_devbench.agents.random_policy import RandomPolicyAgent
from itl_devbench.core.hashing import sha256_file, sha256_json
from itl_devbench.core.trace import GENESIS_EVENT_HASH, make_env_result, make_event, write_jsonl
from itl_devbench.envs.developmental_grid import DevelopmentalGridEnv
from itl_devbench.envs.families import TaskFamilyInstance
from itl_devbench.envs.task_family_generator import TaskFamilyGenerator
from itl_devbench.eval.diagnosis import write_oracle_headroom_diagnosis
from itl_devbench.eval.family_metrics import (
    aggregate_scores_by_dimension,
    aggregate_scores_by_family,
    compute_family_metric_summary,
    write_family_json,
)
from itl_devbench.eval.graph_cache_audit import audit_graph_cache_access, write_graph_cache_audit
from itl_devbench.eval.headroom import compute_oracle_headroom_report, write_oracle_headroom_report
from itl_devbench.eval.metrics import (
    METRIC_ORIENTATION,
    aggregate_baseline_scores,
    aggregate_scores_by_stage,
    compute_metrics_from_trace,
    write_metrics,
)
from itl_devbench.eval.replay import replay_manifest
from itl_devbench.eval.report import write_report
from itl_devbench.eval.saturation import compute_graph_cache_saturation_report, write_saturation_report

TASK_ID = "ITL-DEV-BENCH-001A"
REQUIRED_BASELINES = ["random_policy", "obs_only_policy", "generic_fsm", "graph_cache"]
REQUIRED_MINIMAL_LOOP_VARIANTS = ["000", "100", "010", "001", "110", "101", "011", "111"]


def minimal_loop_variants() -> list[tuple[str, MinimalLoopAgent]]:
    variants: list[tuple[str, MinimalLoopAgent]] = []
    for label in REQUIRED_MINIMAL_LOOP_VARIANTS:
        pe_update, memory, planner = (flag == "1" for flag in label)
        variants.append((label, MinimalLoopAgent(pe_update=pe_update, memory=memory, planner_reads_model=planner)))
    return variants


def run_benchmark(
    config: Dict[str, Any] | None = None,
    smoke: bool = False,
    output_root: str | Path = Path("artifacts") / TASK_ID,
    command_line: list[str] | None = None,
) -> Path:
    config = dict(config or load_config(Path("configs") / "itl_devbench_001a.yaml"))
    generator_enabled = bool(config.get("task_family_generator_001c", {}).get("enabled", False))
    seeds = [int(seed) for seed in config.get("smoke_seeds" if smoke else "official_seeds", [0, 1, 2])]
    stages = [int(stage) for stage in config.get("stages", list(range(7)))]
    output_root = Path(output_root)
    output_root.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_dir = output_root / f"RUN_{timestamp}"
    suffix = 0
    while run_dir.exists():
        suffix += 1
        run_dir = output_root / f"RUN_{timestamp}_{suffix:02d}"
    run_dir.mkdir(parents=True)

    run_id = run_dir.name
    trace_path = run_dir / "trace.jsonl"
    metrics_path = run_dir / "metrics.json"
    baseline_scores_path = run_dir / "baseline_scores.json"
    baseline_scores_by_stage_path = run_dir / "baseline_scores_by_stage.json"
    oracle_headroom_report_path = run_dir / "oracle_headroom_report.json"
    graph_cache_audit_path = run_dir / "leakage_audit_graph_cache.json"
    diagnosis_path = run_dir / "diagnosis_oracle_headroom.md"
    manifest_path = run_dir / "manifest.json"
    report_path = run_dir / "report.md"
    generator_spec_path = run_dir / "generator_spec_001c.json"
    baseline_scores_by_family_path = run_dir / "baseline_scores_by_family.json"
    baseline_scores_by_dimension_path = run_dir / "baseline_scores_by_dimension.json"
    graph_cache_saturation_report_path = run_dir / "graph_cache_saturation_report.json"
    family_metric_summary_path = run_dir / "family_metric_summary.json"
    candidate_source_hash_check_path = run_dir / "candidate_source_hash_check.json"
    source_hashes_001b_path = run_dir / "source_hashes_001b.json"

    generator_spec: Dict[str, Any] | None = None
    targets = _episode_targets(config, seeds, stages, generator_enabled)
    if generator_enabled:
        generator_spec = TaskFamilyGenerator(config).build_spec()
        generator_spec_path.write_text(json.dumps(generator_spec, indent=2, sort_keys=True), encoding="utf-8")

    events: list[Dict[str, Any]] = []
    prev_hash = GENESIS_EVENT_HASH
    event_index = 0
    episode = 0
    for agent_factory in _agent_factories():
        for target in targets:
            seed = int(target["seed"])
            stage = int(target["stage"])
            rule_seed = int(target["rule_seed"])
            family_instance = target.get("family_instance")
            agent = agent_factory()
            env = DevelopmentalGridEnv(config, seed=seed)
            obs = env.reset(stage=stage, rule_seed=rule_seed, family_instance=family_instance)
            agent.reset(seed=seed, stage=stage, episode=episode)
            for _ in range(int(config.get("max_ticks", 100))):
                prediction = agent.predict(obs)
                state_before = agent.snapshot()
                if isinstance(agent, OracleAgent):
                    action = agent.act_with_hidden(obs, prediction, env.debug_hidden_state())
                else:
                    action = agent.act(obs, prediction)
                obs_after, reward, done, info = env.step(action)
                update_diff = agent.update(obs, action, prediction, obs_after, reward, done, info)
                prediction_error = update_diff.get("prediction_error", {})
                family_fields = (
                    family_instance.to_event_fields()
                    if isinstance(family_instance, TaskFamilyInstance)
                    else _legacy_family_fields(stage, seed, episode)
                )
                record_values = {
                    "run_id": run_id,
                    "event_index": event_index,
                    **family_fields,
                    "agent_kind": agent.agent_kind,
                    "agent_id": agent.agent_id,
                    "variant": agent.variant,
                    "seed": seed,
                    "rule_seed": rule_seed,
                    "stage": stage,
                    "episode": episode,
                    "tick": obs.tick,
                    "S_before": state_before,
                    "O_t": obs.to_dict(),
                    "pre_action_prediction": prediction.to_dict(),
                    "A_t": action,
                    "env_result": make_env_result(obs_after, reward, done, info),
                    "reward": reward,
                    "done": done,
                    "prediction_error": prediction_error,
                    "U_t": update_diff,
                    "M_diff": {
                        "model_before": update_diff.get("model_before", {}),
                        "model_after": update_diff.get("model_after", {}),
                    },
                    "S_after": agent.snapshot(),
                }
                event = make_event(record_values, prev_hash)
                events.append(event)
                prev_hash = event["event_hash"]
                event_index += 1
                obs = obs_after
                if done:
                    break
            episode += 1

    write_jsonl(trace_path, events)
    metrics = compute_metrics_from_trace(trace_path)
    baseline_scores = aggregate_baseline_scores(metrics)
    baseline_scores_by_stage = aggregate_scores_by_stage(metrics)
    oracle_headroom_report = compute_oracle_headroom_report(
        baseline_scores=baseline_scores,
        baseline_scores_by_stage=baseline_scores_by_stage,
        required_baselines=REQUIRED_BASELINES,
    )
    graph_cache_audit = audit_graph_cache_access(trace_path)
    write_metrics(metrics_path, metrics)
    baseline_scores_path.write_text(json.dumps(baseline_scores, indent=2, sort_keys=True), encoding="utf-8")
    baseline_scores_by_stage_path.write_text(json.dumps(baseline_scores_by_stage, indent=2, sort_keys=True), encoding="utf-8")
    write_oracle_headroom_report(oracle_headroom_report_path, oracle_headroom_report)
    write_graph_cache_audit(graph_cache_audit_path, graph_cache_audit)

    family_outputs: Dict[str, Any] = {}
    if generator_enabled:
        baseline_scores_by_family = aggregate_scores_by_family(metrics)
        baseline_scores_by_dimension = aggregate_scores_by_dimension(metrics)
        family_metric_summary = compute_family_metric_summary(metrics, baseline_scores_by_family, trace_path)
        graph_cache_saturation_report = compute_graph_cache_saturation_report(family_metric_summary, config)
        candidate_source_hash_check = _candidate_source_hash_check(config, source_hashes_001b_path)
        write_family_json(baseline_scores_by_family_path, baseline_scores_by_family)
        write_family_json(baseline_scores_by_dimension_path, baseline_scores_by_dimension)
        write_family_json(family_metric_summary_path, family_metric_summary)
        write_saturation_report(graph_cache_saturation_report_path, graph_cache_saturation_report)
        candidate_source_hash_check_path.write_text(
            json.dumps(candidate_source_hash_check, indent=2, sort_keys=True),
            encoding="utf-8",
        )
        family_outputs = {
            "baseline_scores_by_family": baseline_scores_by_family,
            "baseline_scores_by_dimension": baseline_scores_by_dimension,
            "family_metric_summary": family_metric_summary,
            "graph_cache_saturation_report": graph_cache_saturation_report,
            "candidate_source_hash_check": candidate_source_hash_check,
        }

    manifest = _build_manifest(
        run_id=run_id,
        run_dir=run_dir,
        config=config,
        smoke=smoke,
        seeds=seeds,
        stages=sorted({int(target["stage"]) for target in targets}),
        command_line=command_line or sys.argv,
        metrics_hash=metrics["metrics_hash"],
    )
    manifest.update(
        {
            "trace_path": "trace.jsonl",
            "metrics_path": "metrics.json",
            "baseline_scores_path": "baseline_scores.json",
            "baseline_scores_by_stage_path": "baseline_scores_by_stage.json",
            "oracle_headroom_report_path": "oracle_headroom_report.json",
            "leakage_audit_graph_cache_path": "leakage_audit_graph_cache.json",
            "diagnosis_oracle_headroom_path": "diagnosis_oracle_headroom.md",
            "replay_report_path": "replay_report.json",
            "audit_report_path": "audit_report.json",
            "report_path": "report.md",
            "trace_hash": sha256_file(trace_path),
            "metric_orientation": METRIC_ORIENTATION,
            "task_family_generator_001c_enabled": generator_enabled,
        }
    )
    if generator_enabled:
        manifest.update(
            {
                "generator_spec_001c_path": "generator_spec_001c.json",
                "baseline_scores_by_family_path": "baseline_scores_by_family.json",
                "baseline_scores_by_dimension_path": "baseline_scores_by_dimension.json",
                "graph_cache_saturation_report_path": "graph_cache_saturation_report.json",
                "family_metric_summary_path": "family_metric_summary.json",
                "candidate_source_hash_check_path": "candidate_source_hash_check.json",
                "source_hashes_001b_path": "source_hashes_001b.json",
            }
        )
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    write_oracle_headroom_diagnosis(diagnosis_path, manifest, oracle_headroom_report, graph_cache_audit)

    replay_report = replay_manifest(manifest_path)
    report_verdict = write_report(
        report_path,
        manifest,
        replay_report,
        baseline_scores,
        oracle_headroom_report=oracle_headroom_report,
        graph_cache_audit=graph_cache_audit,
        generator_spec=generator_spec,
        graph_cache_saturation_report=family_outputs.get("graph_cache_saturation_report"),
        candidate_source_hash_check=family_outputs.get("candidate_source_hash_check"),
    )
    manifest["report_verdict"] = report_verdict
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")

    from itl_devbench.eval.audit import audit_manifest

    audit_manifest(manifest_path)
    _refresh_latest(run_dir, output_root / "latest")
    return run_dir


def load_config(config_path: str | Path) -> Dict[str, Any]:
    text = Path(config_path).read_text(encoding="utf-8")
    return json.loads(text)


def _episode_targets(
    config: Dict[str, Any],
    seeds: list[int],
    stages: list[int],
    generator_enabled: bool,
) -> list[Dict[str, Any]]:
    if generator_enabled:
        generator = TaskFamilyGenerator(config)
        split = str(config.get("task_family_generator_001c", {}).get("split", "smoke"))
        return [
            {
                "seed": instance.seed,
                "stage": instance.stage_index,
                "rule_seed": instance.rule_seed,
                "family_instance": instance,
            }
            for instance in generator.instances_for_split(split, seeds)
        ]
    return [
        {
            "seed": seed,
            "stage": stage,
            "rule_seed": _rule_seed_for(config, stage, seed),
            "family_instance": None,
        }
        for seed in seeds
        for stage in stages
    ]


def _agent_factories() -> list[Any]:
    factories: list[Any] = [
        RandomPolicyAgent,
        ObsOnlyPolicyAgent,
        GenericFSMAgent,
        GraphCacheAgent,
        OracleAgent,
    ]
    for label in REQUIRED_MINIMAL_LOOP_VARIANTS:
        pe_update, memory, planner = (flag == "1" for flag in label)
        factories.append(lambda pe=pe_update, mem=memory, plan=planner: MinimalLoopAgent(pe, mem, plan))
    return factories


def _legacy_family_fields(stage: int, seed: int, episode: int) -> Dict[str, Any]:
    return {
        "split": "legacy",
        "family_id": "legacy_stage",
        "family_instance_id": f"legacy:{stage}:{seed}:{episode}",
        "dimension_combo": [],
        "target_pressure": [],
    }


def _candidate_source_hash_check(config: Dict[str, Any], copied_baseline_path: Path) -> Dict[str, Any]:
    baseline_path = _ensure_candidate_hash_baseline(config)
    baseline = json.loads(baseline_path.read_text(encoding="utf-8"))
    source_path = Path(baseline["source_path"])
    after_sha = sha256_file(source_path)
    copied_baseline_path.write_text(json.dumps(baseline, indent=2, sort_keys=True), encoding="utf-8")
    unchanged = after_sha == baseline["sha256"]
    return {
        "producer_function": "itl_devbench.eval.run_matrix._candidate_source_hash_check",
        "baseline_source": str(baseline_path),
        "source_path": baseline["source_path"],
        "before_sha256": baseline["sha256"],
        "after_sha256": after_sha,
        "candidate_source_unchanged": unchanged,
        "verdict": "candidate_source_unchanged" if unchanged else "candidate_tuning_violation",
    }


def _ensure_candidate_hash_baseline(config: Dict[str, Any]) -> Path:
    generator_cfg = config.get("task_family_generator_001c", {})
    baseline_path = Path(
        generator_cfg.get(
            "candidate_source_hash_baseline_path",
            Path("artifacts") / TASK_ID / "latest" / "source_hashes_001b.json",
        )
    )
    if baseline_path.exists():
        return baseline_path
    source_path = Path("src") / "itl_devbench" / "agents" / "minimal_loop.py"
    baseline_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "producer_function": "itl_devbench.eval.run_matrix._ensure_candidate_hash_baseline",
        "task_id": "ITL-DEV-BENCH-001B",
        "source_path": source_path.as_posix(),
        "sha256": sha256_file(source_path),
        "note": "created_from_current_source_before_001c_run_when_001b_hash_file_was_absent",
    }
    baseline_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return baseline_path


def _rule_seed_for(config: Dict[str, Any], stage: int, seed: int) -> int:
    heldout = config.get("heldout_rule_seeds", {})
    stage_values = heldout.get(str(stage), [])
    if stage_values:
        return int(stage_values[seed % len(stage_values)])
    return int(config.get("default_rule_seed_base", 1000)) + stage * 100 + seed


def _build_manifest(
    run_id: str,
    run_dir: Path,
    config: Dict[str, Any],
    smoke: bool,
    seeds: list[int],
    stages: list[int],
    command_line: list[str],
    metrics_hash: str,
) -> Dict[str, Any]:
    repo_root = Path.cwd()
    return {
        "producer_function": "itl_devbench.eval.run_matrix.run_benchmark",
        "task_id": config.get("task_id", TASK_ID),
        "artifact_root_task_id": TASK_ID,
        "run_id": run_id,
        "run_dir": str(run_dir),
        "smoke": smoke,
        "config": config,
        "config_hash": sha256_json(config),
        "seed_list": seeds,
        "stage_list": stages,
        "command_line": command_line,
        "python_version": sys.version,
        "git_commit": _git_read(["rev-parse", "HEAD"]),
        "git_status_readback": _git_read(["status", "--short"]),
        "git_status_branch_readback": _git_read(["status", "--branch", "--short"]),
        "source_file_hashes": _source_hashes(repo_root),
        "metrics_hash": metrics_hash,
        "agent_ids": REQUIRED_BASELINES + ["oracle", "minimal_loop"],
        "minimal_loop_variants": REQUIRED_MINIMAL_LOOP_VARIANTS,
    }


def _source_hashes(repo_root: Path) -> Dict[str, str]:
    source_paths = sorted((repo_root / "src" / "itl_devbench").rglob("*.py"))
    return {path.relative_to(repo_root).as_posix(): sha256_file(path) for path in source_paths}


def _git_read(args: list[str]) -> str:
    try:
        completed = subprocess.run(["git", *args], capture_output=True, text=True, check=False)
    except OSError as exc:
        return f"git_unavailable:{exc}"
    return completed.stdout.strip()


def _refresh_latest(run_dir: Path, latest_dir: Path) -> None:
    if latest_dir.exists():
        shutil.rmtree(latest_dir)
    shutil.copytree(run_dir, latest_dir)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    parser.add_argument("--smoke", action="store_true")
    args = parser.parse_args(argv)
    run_dir = run_benchmark(config=load_config(args.config), smoke=args.smoke, command_line=sys.argv)
    manifest_path = run_dir / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    print(
        json.dumps(
            {
                "run_dir": str(run_dir),
                "manifest_path": str(manifest_path),
                "trace_path": str(run_dir / manifest["trace_path"]),
                "report_path": str(run_dir / manifest["report_path"]),
                "replay_report_path": str(run_dir / manifest["replay_report_path"]),
                "audit_report_path": str(run_dir / manifest["audit_report_path"]),
                "oracle_headroom_report_path": str(run_dir / manifest["oracle_headroom_report_path"]),
                "leakage_audit_graph_cache_path": str(run_dir / manifest["leakage_audit_graph_cache_path"]),
                "diagnosis_oracle_headroom_path": str(run_dir / manifest["diagnosis_oracle_headroom_path"]),
                "generator_spec_001c_path": str(run_dir / manifest.get("generator_spec_001c_path", "")),
                "baseline_scores_by_family_path": str(run_dir / manifest.get("baseline_scores_by_family_path", "")),
                "baseline_scores_by_dimension_path": str(run_dir / manifest.get("baseline_scores_by_dimension_path", "")),
                "graph_cache_saturation_report_path": str(run_dir / manifest.get("graph_cache_saturation_report_path", "")),
                "family_metric_summary_path": str(run_dir / manifest.get("family_metric_summary_path", "")),
                "candidate_source_hash_check_path": str(run_dir / manifest.get("candidate_source_hash_check_path", "")),
                "report_verdict": manifest.get("report_verdict"),
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
