import json

from itl_devbench.eval.run_matrix import run_benchmark


def test_trace_event_contains_required_contract_fields_in_pre_step_order(tmp_path):
    run_dir = run_benchmark(
        config={"width": 7, "height": 7, "max_ticks": 12, "smoke_seeds": [0]},
        smoke=True,
        output_root=tmp_path,
    )
    first_event = json.loads((run_dir / "trace.jsonl").read_text(encoding="utf-8").splitlines()[0])

    required = [
        "run_id",
        "event_index",
        "agent_id",
        "variant",
        "seed",
        "stage",
        "episode",
        "tick",
        "S_before",
        "O_t",
        "pre_action_prediction",
        "A_t",
        "env_result",
        "reward",
        "done",
        "prediction_error",
        "U_t",
        "M_diff",
        "S_after",
        "prev_event_hash",
        "event_hash",
    ]
    assert set(required).issubset(first_event)

    ordered_keys = list(first_event)
    assert ordered_keys.index("pre_action_prediction") < ordered_keys.index("env_result")
    assert first_event["pre_action_prediction"] is not None
    assert first_event["event_index"] == 0
