from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict

from itl_devbench.core.hashing import sha256_json
from itl_devbench.core.trace import compute_event_hash, make_env_result, read_jsonl, validate_hash_chain
from itl_devbench.envs.developmental_grid import DevelopmentalGridEnv
from itl_devbench.envs.task_family_generator import TaskFamilyGenerator
from itl_devbench.eval.metrics import compute_metrics_from_trace


def replay_manifest(manifest_path: str | Path) -> Dict[str, Any]:
    manifest_path = Path(manifest_path)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    run_dir = manifest_path.parent
    trace_path = _resolve_path(run_dir, manifest["trace_path"])
    events = read_jsonl(trace_path)
    errors: list[str] = []

    chain_ok, chain_errors = validate_hash_chain(events)
    errors.extend(chain_errors)

    config = manifest["config"]
    generator = TaskFamilyGenerator(config) if manifest.get("task_family_generator_001c_enabled") else None
    env: DevelopmentalGridEnv | None = None
    current_key: tuple[str, str, str, str, int, int, int] | None = None
    current_obs = None
    prev_hash = "0" * 64
    for index, event in enumerate(events):
        key = (
            str(event.get("split", "legacy")),
            str(event.get("family_id", "legacy_stage")),
            str(event["agent_id"]),
            str(event["variant"]),
            int(event["seed"]),
            int(event["stage"]),
            int(event["episode"]),
        )
        if key != current_key:
            env = DevelopmentalGridEnv(config, seed=int(event["seed"]))
            family_instance = None
            if generator is not None and event.get("family_id") not in {None, "legacy_stage"}:
                family_instance = generator.instance_for(
                    family_id=str(event["family_id"]),
                    split=str(event.get("split", "smoke")),
                    seed=int(event["seed"]),
                    stage_index=int(event["stage"]),
                )
            current_obs = env.reset(
                stage=int(event["stage"]),
                rule_seed=int(event["rule_seed"]),
                family_instance=family_instance,
            )
            current_key = key
        assert env is not None
        assert current_obs is not None
        if current_obs.to_dict() != event["O_t"]:
            errors.append(f"observation_mismatch:{index}")
        obs_after, reward, done, info = env.step(event["A_t"])
        expected_env_result = make_env_result(obs_after, reward, done, info)
        if expected_env_result != event["env_result"]:
            errors.append(f"env_result_mismatch:{index}")
        if float(reward) != float(event["reward"]):
            errors.append(f"reward_mismatch:{index}")
        if bool(done) != bool(event["done"]):
            errors.append(f"done_mismatch:{index}")
        if event.get("prev_event_hash") != prev_hash:
            errors.append(f"replay_prev_hash_mismatch:{index}")
        if compute_event_hash(event) != event.get("event_hash"):
            errors.append(f"replay_event_hash_mismatch:{index}")
        prev_hash = str(event.get("event_hash", ""))
        current_obs = obs_after

    metrics = compute_metrics_from_trace(trace_path)
    metrics_hash = metrics["metrics_hash"]
    metrics_match = metrics_hash == manifest.get("metrics_hash")
    if not metrics_match:
        errors.append("metrics_hash_mismatch")

    report = {
        "producer_function": "itl_devbench.eval.replay.replay_manifest",
        "manifest_path": str(manifest_path),
        "trace_path": str(trace_path),
        "replay_ok": not errors and chain_ok,
        "hash_chain_ok": chain_ok,
        "metrics_match": metrics_match,
        "metrics_hash": metrics_hash,
        "manifest_metrics_hash": manifest.get("metrics_hash"),
        "event_count": len(events),
        "errors": errors,
        "verdict": "replay_succeeded" if not errors and chain_ok else "replay_failed_evidence_invalid",
        "report_hash": sha256_json({"errors": errors, "metrics_hash": metrics_hash, "event_count": len(events)}),
    }
    output_path = run_dir / "replay_report.json"
    output_path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    return report


def _resolve_path(run_dir: Path, value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else run_dir / path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True)
    args = parser.parse_args(argv)
    report = replay_manifest(args.manifest)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["verdict"] == "replay_succeeded" else 1


if __name__ == "__main__":
    raise SystemExit(main())
