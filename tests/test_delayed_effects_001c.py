import json

from itl_devbench.eval.replay import replay_manifest
from itl_devbench.eval.run_matrix import run_benchmark
from itl_devbench.envs.task_family_generator import load_generator_config


def test_delayed_poison_trace_links_cause_and_effect_after_seven_ticks(tmp_path):
    config = load_generator_config("configs/itl_devbench_001c.yaml")
    run_dir = run_benchmark(config=config, smoke=True, output_root=tmp_path)
    events = [
        json.loads(line)
        for line in (run_dir / "trace.jsonl").read_text(encoding="utf-8").splitlines()
        if '"family_id":"delayed_poison_v1"' in line
    ]
    delayed_events = [
        event for event in events if event["env_result"]["info"].get("delayed_effect_event_id") is not None
    ]

    assert delayed_events
    event = delayed_events[0]
    info = event["env_result"]["info"]
    assert info["delay_ticks"] >= 7
    assert info["cause_event_id"] < info["delayed_effect_event_id"]
    assert info["source_object_id"]

    replay = replay_manifest(run_dir / "manifest.json")
    assert replay["verdict"] == "replay_succeeded"
