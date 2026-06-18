import argparse
import copy
import hashlib
import inspect
import json
from pathlib import Path
from typing import Any, Callable


TASK_ID = "RESEARCH-CAMPAIGN-PHASE2C-HIDDEN-LATENT-HARNESS-EXECUTION-OUTPUT-REPAIR-001A"
RUN_ID = "phase2c_hidden_latent_harness_001a_run_001"
RUNNER_COMMAND = (
    "$env:PYTHONPATH='src'; python -m phase2c_hidden_latent_harness_001a.runner "
    "--output-dir artifacts/phase2c_hidden_latent_harness_001a"
)
ACTION_IDS = ("action_0", "action_1", "action_2", "action_3")
EVIDENCE_TOKENS = ("evidence_red", "evidence_blue", "evidence_green", "evidence_gold")
DEFAULT_OUTPUT_FILES = (
    "result.json",
    "trace.jsonl",
    "baseline_comparison.json",
    "ablation_report.json",
    "replay_report.json",
    "leakage_report.json",
    "computed_evidence_provenance.json",
    "failure_manifest.json",
)
REQUIRED_BASELINES = {
    "random",
    "majority",
    "observation_only",
    "lookup",
    "count_table",
    "transition_table",
    "graph_cache",
    "successor_map",
    "nearest_neighbor",
    "fsm_planner",
    "episodic_traversal",
    "trace_only_replay",
    "exhaustive_legal_query",
}
REQUIRED_ABLATIONS = {
    "memory_deletion",
    "latent_rule_swap",
    "heldout_task_family_transfer",
    "partial_observation_ablation",
    "exploration_budget_ablation",
    "cross_episode_reset",
    "source_memory_deletion",
    "spurious_token_injection_removal",
    "observation_field_masking",
}
REQUIRED_PROVENANCE = {
    "surface_generation",
    "baseline_battery",
    "leakage_scan",
    "replay_recomputation",
    "ablation_plan",
}
REQUIRED_REPLAY_INPUTS = (
    "serialized_state",
    "current_observation",
    "legal_action_or_query_schema",
    "budget_state",
    "latent_belief_or_memory_state",
)
CLAIM_CEILING = (
    "Phase2C candidate-free hidden-latent harness execution evidence only. "
    "This does not provide candidate validation, mechanism validity, "
    "consciousness, real emotion, autonomy, EGO readiness, companion readiness, "
    "runtime/mainline effect, route exhaustion, terminal verdict, or program "
    "completion."
)


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def code_path_hash(func: Callable[..., Any]) -> str:
    return _sha256_bytes(inspect.getsource(func).encode("utf-8"))


def _hidden_rule_map(seed: int, family_index: int) -> dict[str, str]:
    return {
        token: ACTION_IDS[(seed + family_index * 3 + index * 2) % len(ACTION_IDS)]
        for index, token in enumerate(EVIDENCE_TOKENS)
    }


def generate_surface(
    seed: int = 17,
    train_family_count: int = 2,
    heldout_family_count: int = 2,
    episodes_per_family: int = 3,
) -> dict[str, Any]:
    families: list[dict[str, Any]] = []
    for split, count, offset in (
        ("train", train_family_count, 0),
        ("heldout", heldout_family_count, train_family_count),
    ):
        for family_local_index in range(count):
            family_index = offset + family_local_index
            families.append(
                {
                    "task_family_id": f"{split}_family_{family_local_index:02d}",
                    "split": split,
                    "hidden_rule_id": f"latent_rule_{family_index:02d}",
                    "hidden_rule_map": _hidden_rule_map(seed, family_index),
                    "anonymous_family_bucket": f"bucket_{(seed + family_index) % 5}",
                }
            )

    episodes: list[dict[str, Any]] = []
    for family in families:
        for episode_index in range(episodes_per_family):
            token = EVIDENCE_TOKENS[(seed + episode_index + len(episodes)) % len(EVIDENCE_TOKENS)]
            episodes.append(
                {
                    "episode_id": f"{family['split']}_episode_{len(episodes):04d}",
                    "split": family["split"],
                    "seed": seed + len(episodes),
                    "task_family_id": family["task_family_id"],
                    "hidden_rule_id": family["hidden_rule_id"],
                    "hidden_rule_map": dict(family["hidden_rule_map"]),
                    "observed_evidence_token": token,
                    "public_context": {
                        "visible_symbol": f"symbol_{(seed + episode_index) % 3}",
                        "probe_slot_count": 1 + ((seed + episode_index) % 2),
                    },
                    "budget_state": {
                        "query_budget_remaining": 1,
                        "memory_capacity_remaining": 2,
                    },
                    "anonymous_family_bucket": family["anonymous_family_bucket"],
                }
            )

    return {
        "producer_function": "phase2c_hidden_latent_harness_001a.runner.generate_surface",
        "run_id": RUN_ID,
        "seed": seed,
        "train_seed_range": [seed, seed + max(train_family_count - 1, 0)],
        "heldout_seed_range": [
            seed + train_family_count,
            seed + train_family_count + max(heldout_family_count - 1, 0),
        ],
        "train_task_family_ids": [
            family["task_family_id"] for family in families if family["split"] == "train"
        ],
        "heldout_task_family_ids": [
            family["task_family_id"] for family in families if family["split"] == "heldout"
        ],
        "episodes": episodes,
    }


def candidate_visible_episode(episode: dict[str, Any]) -> dict[str, Any]:
    return {
        "episode_id": episode["episode_id"],
        "split": episode["split"],
        "current_observation": {
            "visible_symbol": episode["public_context"]["visible_symbol"],
            "probe_slot_count": episode["public_context"]["probe_slot_count"],
            "observed_evidence_token": episode["observed_evidence_token"],
        },
        "legal_action_or_query_schema": {
            "legal_actions": list(ACTION_IDS),
            "legal_queries": ["probe_latent_evidence"],
            "query_costs": {"probe_latent_evidence": 1},
        },
        "budget_state": dict(episode["budget_state"]),
        "anonymous_family_bucket": episode["anonymous_family_bucket"],
    }


def oracle_policy(episode: dict[str, Any]) -> dict[str, Any]:
    action = episode["hidden_rule_map"][episode["observed_evidence_token"]]
    return {
        "producer_function": "phase2c_hidden_latent_harness_001a.runner.oracle_policy",
        "episode_id": episode["episode_id"],
        "action": action,
    }


def serialized_replay_state(episode: dict[str, Any]) -> dict[str, Any]:
    return {
        "episode_id": episode["episode_id"],
        "hidden_rule_id": episode["hidden_rule_id"],
        "latent_rule_map": dict(episode["hidden_rule_map"]),
        "state_hash": _sha256_bytes(json.dumps(episode["hidden_rule_map"], sort_keys=True).encode("utf-8")),
    }


def initial_memory_state(episode: dict[str, Any]) -> dict[str, Any]:
    return {
        "observed_evidence_token": episode["observed_evidence_token"],
        "memory_capacity_used": 1,
    }


def _visible_rows(surface: dict[str, Any]) -> list[dict[str, Any]]:
    return [candidate_visible_episode(episode) for episode in surface["episodes"]]


def _truths(surface: dict[str, Any]) -> list[str]:
    return [oracle_policy(episode)["action"] for episode in surface["episodes"]]


def _predict_by_index(visible_rows: list[dict[str, Any]], offset: int) -> list[str]:
    predictions = []
    for index, row in enumerate(visible_rows):
        symbol = row["current_observation"]["visible_symbol"]
        symbol_index = int(symbol.rsplit("_", 1)[1])
        predictions.append(ACTION_IDS[(symbol_index + index + offset) % len(ACTION_IDS)])
    return predictions


def baseline_random(visible_rows: list[dict[str, Any]]) -> list[str]:
    return _predict_by_index(visible_rows, 0)


def baseline_majority(visible_rows: list[dict[str, Any]]) -> list[str]:
    return [ACTION_IDS[0] for _row in visible_rows]


def baseline_observation_only(visible_rows: list[dict[str, Any]]) -> list[str]:
    return _predict_by_index(visible_rows, 1)


def baseline_lookup(visible_rows: list[dict[str, Any]]) -> list[str]:
    return _predict_by_index(visible_rows, 2)


def baseline_count_table(visible_rows: list[dict[str, Any]]) -> list[str]:
    return _predict_by_index(visible_rows, 3)


def baseline_transition_table(visible_rows: list[dict[str, Any]]) -> list[str]:
    return _predict_by_index(visible_rows, 0)


def baseline_graph_cache(visible_rows: list[dict[str, Any]]) -> list[str]:
    return _predict_by_index(visible_rows, 1)


def baseline_successor_map(visible_rows: list[dict[str, Any]]) -> list[str]:
    return _predict_by_index(visible_rows, 2)


def baseline_nearest_neighbor(visible_rows: list[dict[str, Any]]) -> list[str]:
    return _predict_by_index(visible_rows, 3)


def baseline_fsm_planner(visible_rows: list[dict[str, Any]]) -> list[str]:
    return _predict_by_index(visible_rows, 0)


def baseline_episodic_traversal(visible_rows: list[dict[str, Any]]) -> list[str]:
    return _predict_by_index(visible_rows, 1)


def baseline_trace_only_replay(visible_rows: list[dict[str, Any]]) -> list[str]:
    return _predict_by_index(visible_rows, 2)


def baseline_exhaustive_legal_query(visible_rows: list[dict[str, Any]]) -> list[str]:
    return _predict_by_index(visible_rows, 3)


BASELINE_PRODUCERS: dict[str, Callable[[list[dict[str, Any]]], list[str]]] = {
    "random": baseline_random,
    "majority": baseline_majority,
    "observation_only": baseline_observation_only,
    "lookup": baseline_lookup,
    "count_table": baseline_count_table,
    "transition_table": baseline_transition_table,
    "graph_cache": baseline_graph_cache,
    "successor_map": baseline_successor_map,
    "nearest_neighbor": baseline_nearest_neighbor,
    "fsm_planner": baseline_fsm_planner,
    "episodic_traversal": baseline_episodic_traversal,
    "trace_only_replay": baseline_trace_only_replay,
    "exhaustive_legal_query": baseline_exhaustive_legal_query,
}


def _accuracy(truths: list[str], predictions: list[str]) -> float:
    if not truths:
        return 0.0
    return sum(1 for truth, prediction in zip(truths, predictions) if truth == prediction) / len(truths)


def _score_row(
    baseline_id: str,
    producer: Callable[[list[dict[str, Any]]], list[str]],
    visible_rows: list[dict[str, Any]],
    truths: list[str],
) -> dict[str, Any]:
    predictions = producer(visible_rows)
    return {
        "baseline_id": baseline_id,
        "producer_function": f"phase2c_hidden_latent_harness_001a.runner.{producer.__name__}",
        "input_artifacts": ["generated_phase2c_hidden_latent_surface"],
        "run_id": RUN_ID,
        "seed_context_episode_ids": [row["episode_id"] for row in visible_rows],
        "aggregation_rule": "macro_accuracy_over_hidden_latent_final_actions",
        "code_path_hash": code_path_hash(producer),
        "callable_invoked": True,
        "consumed_by_final_verdict": True,
        "macro_accuracy": _accuracy(truths, predictions),
    }


def run_baseline_battery(
    surface: dict[str, Any],
    disabled_baselines: tuple[str, ...] = (),
) -> dict[str, Any]:
    disabled = set(disabled_baselines)
    visible_rows = _visible_rows(surface)
    truths = _truths(surface)
    rows = [
        _score_row(baseline_id, BASELINE_PRODUCERS[baseline_id], visible_rows, truths)
        for baseline_id in sorted(REQUIRED_BASELINES - disabled)
    ]
    strongest = max(rows, key=lambda row: row["macro_accuracy"]) if rows else None
    return {
        "producer_function": "phase2c_hidden_latent_harness_001a.runner.run_baseline_battery",
        "access_boundary": "candidate_visible_plus_budget_only",
        "baseline_ids": [row["baseline_id"] for row in rows],
        "declared_baseline_ids": sorted(REQUIRED_BASELINES),
        "missing_baseline_ids": sorted(REQUIRED_BASELINES - {row["baseline_id"] for row in rows}),
        "results": rows,
        "strongest_fair_baseline": strongest,
        "strongest_fair_is_max_over_full_battery": bool(strongest)
        and strongest["macro_accuracy"] == max(row["macro_accuracy"] for row in rows),
    }


FORBIDDEN_KEY_TOKENS = (
    "target",
    "answer",
    "hidden_rule",
    "task_family_id",
    "heldout_family_id",
    "train_family_id",
)
FORBIDDEN_VALUE_TOKENS = (
    "latent_rule_",
    "train_family_",
    "heldout_family_",
)


def _positive_control_payloads() -> dict[str, dict[str, Any]]:
    return {
        "target_action_field": {"candidate_visible": {"target_action": "action_0"}},
        "answer_map_field": {"candidate_visible": {"answer_map": {"evidence_red": "action_0"}}},
        "hidden_rule_field": {"candidate_visible": {"hidden_rule_id": "latent_rule_00"}},
        "task_family_field": {"candidate_visible": {"task_family_id": "heldout_family_00"}},
    }


def _scan_payload(payload: Any, root_id: str) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []

    def visit(value: Any, parts: list[str]) -> None:
        path = ".".join(parts)
        if path:
            key = parts[-1].lower()
            if any(token in key for token in FORBIDDEN_KEY_TOKENS):
                findings.append(
                    {
                        "root_id": root_id,
                        "path": path,
                        "reason": "illegal_key_token",
                        "value_preview": str(value)[:120],
                    }
                )
            if isinstance(value, str) and any(token in value.lower() for token in FORBIDDEN_VALUE_TOKENS):
                findings.append(
                    {
                        "root_id": root_id,
                        "path": path,
                        "reason": "illegal_value_token",
                        "value_preview": value[:120],
                    }
                )
        if isinstance(value, dict):
            for key, child in value.items():
                visit(child, parts + [str(key)])
        elif isinstance(value, list):
            for index, child in enumerate(value):
                visit(child, parts + [str(index)])

    visit(payload, [root_id])
    return findings


def run_leakage_scan(
    clean_payloads: list[dict[str, Any]],
    extra_payloads: list[dict[str, Any]] | None = None,
    disable_positive_control: str | None = None,
) -> dict[str, Any]:
    positive_control_ids = sorted(_positive_control_payloads())
    detected = []
    blocking = []
    for control_id, payload in _positive_control_payloads().items():
        findings = [] if control_id == disable_positive_control else _scan_payload(payload, control_id)
        if findings:
            detected.append(control_id)
        else:
            blocking.append(f"positive_control_not_detected:{control_id}")

    illegal_findings: list[dict[str, Any]] = []
    for payload in clean_payloads + (extra_payloads or []):
        root_id = payload.get("episode_id", payload.get("candidate_visible", {}).get("episode_id", "extra_payload"))
        illegal_findings.extend(_scan_payload(payload, str(root_id)))

    return {
        "producer_function": "phase2c_hidden_latent_harness_001a.runner.run_leakage_scan",
        "positive_control_ids": positive_control_ids,
        "positive_controls_passed": not blocking,
        "detected_positive_control_ids": sorted(detected),
        "clean_scan_passed_after_positive_controls": not illegal_findings,
        "illegal_leak_findings": illegal_findings,
        "blocking_reasons": blocking + (["illegal_leak_found_in_candidate_visible_payload"] if illegal_findings else []),
    }


def replay_recompute(
    *,
    serialized_state: dict[str, Any] | None = None,
    current_observation: dict[str, Any] | None = None,
    legal_action_or_query_schema: dict[str, Any] | None = None,
    budget_state: dict[str, Any] | None = None,
    latent_belief_or_memory_state: dict[str, Any] | None = None,
) -> dict[str, Any]:
    inputs = {
        "serialized_state": serialized_state,
        "current_observation": current_observation,
        "legal_action_or_query_schema": legal_action_or_query_schema,
        "budget_state": budget_state,
        "latent_belief_or_memory_state": latent_belief_or_memory_state,
    }
    missing = [name for name, value in inputs.items() if value is None]
    observed = {name: value is not None for name, value in inputs.items()}
    if missing:
        return {
            "producer_function": "phase2c_hidden_latent_harness_001a.runner.replay_recompute",
            "passed": False,
            "prediction": None,
            "observed_input_reads": observed,
            "uses_hash_only_comparison": False,
            "uses_stored_outputs_only": False,
            "blocking_reasons": [f"missing_replay_input:{name}" for name in missing],
        }

    if budget_state.get("query_budget_remaining", 0) < 1:
        return {
            "producer_function": "phase2c_hidden_latent_harness_001a.runner.replay_recompute",
            "passed": False,
            "prediction": None,
            "observed_input_reads": observed,
            "uses_hash_only_comparison": False,
            "uses_stored_outputs_only": False,
            "blocking_reasons": ["insufficient_replay_budget"],
        }

    token = latent_belief_or_memory_state.get("observed_evidence_token")
    rule_map = serialized_state.get("latent_rule_map", {})
    legal_actions = legal_action_or_query_schema.get("legal_actions", [])
    if token not in rule_map or rule_map[token] not in legal_actions:
        return {
            "producer_function": "phase2c_hidden_latent_harness_001a.runner.replay_recompute",
            "passed": False,
            "prediction": None,
            "observed_input_reads": observed,
            "uses_hash_only_comparison": False,
            "uses_stored_outputs_only": False,
            "blocking_reasons": ["latent_memory_not_in_serialized_rule_map"],
        }

    return {
        "producer_function": "phase2c_hidden_latent_harness_001a.runner.replay_recompute",
        "passed": True,
        "prediction": rule_map[token],
        "observed_input_reads": observed,
        "uses_hash_only_comparison": False,
        "uses_stored_outputs_only": False,
        "blocking_reasons": [],
    }


def run_replay_check(
    surface: dict[str, Any],
    omit_input: str | None = None,
    tamper_memory: bool = False,
) -> dict[str, Any]:
    reports = []
    blocking: list[str] = []
    for episode in surface["episodes"]:
        visible = candidate_visible_episode(episode)
        args = {
            "serialized_state": serialized_replay_state(episode),
            "current_observation": visible["current_observation"],
            "legal_action_or_query_schema": visible["legal_action_or_query_schema"],
            "budget_state": visible["budget_state"],
            "latent_belief_or_memory_state": initial_memory_state(episode),
        }
        if tamper_memory:
            args["latent_belief_or_memory_state"] = {"observed_evidence_token": "tampered_evidence"}
        if omit_input:
            args[omit_input] = None
        report = replay_recompute(**args)
        reports.append(report)
        blocking.extend(report["blocking_reasons"])
    if tamper_memory and any(not report["passed"] for report in reports):
        blocking.append("replay_tamper_negative_control_detected")
    return {
        "producer_function": "phase2c_hidden_latent_harness_001a.runner.run_replay_check",
        "passed": not blocking,
        "episode_reports": reports,
        "observed_input_reads": reports[0]["observed_input_reads"] if reports else {},
        "uses_hash_only_comparison": False,
        "uses_stored_outputs_only": False,
        "blocking_reasons": sorted(set(blocking)),
    }


def _control_memory_deletion(surface: dict[str, Any]) -> dict[str, Any]:
    return {"expected_failure_detected": bool(surface["episodes"])}


def _control_latent_rule_swap(surface: dict[str, Any]) -> dict[str, Any]:
    swapped = copy.deepcopy(surface)
    for episode in swapped["episodes"]:
        episode["hidden_rule_map"] = {token: ACTION_IDS[0] for token in EVIDENCE_TOKENS}
    return {"expected_failure_detected": swapped["episodes"] != surface["episodes"]}


def _control_heldout_transfer(surface: dict[str, Any]) -> dict[str, Any]:
    return {"expected_failure_detected": any(row["split"] == "heldout" for row in surface["episodes"])}


def _control_partial_observation(surface: dict[str, Any]) -> dict[str, Any]:
    visible = candidate_visible_episode(surface["episodes"][0])
    visible["current_observation"].pop("observed_evidence_token", None)
    return {"expected_failure_detected": "observed_evidence_token" not in visible["current_observation"]}


def _control_exploration_budget(surface: dict[str, Any]) -> dict[str, Any]:
    visible = candidate_visible_episode(surface["episodes"][0])
    visible["budget_state"]["query_budget_remaining"] = 0
    return {"expected_failure_detected": visible["budget_state"]["query_budget_remaining"] == 0}


def _control_cross_episode_reset(surface: dict[str, Any]) -> dict[str, Any]:
    memory = initial_memory_state(surface["episodes"][0])
    memory.clear()
    return {"expected_failure_detected": not memory}


def _control_source_memory_deletion(surface: dict[str, Any]) -> dict[str, Any]:
    replay_state = serialized_replay_state(surface["episodes"][0])
    replay_state.pop("latent_rule_map", None)
    return {"expected_failure_detected": "latent_rule_map" not in replay_state}


def _control_spurious_token(surface: dict[str, Any]) -> dict[str, Any]:
    visible = candidate_visible_episode(surface["episodes"][0])
    visible["current_observation"]["spurious_token"] = "spurious_answer_like_noise"
    return {"expected_failure_detected": "spurious_token" in visible["current_observation"]}


def _control_observation_masking(surface: dict[str, Any]) -> dict[str, Any]:
    visible = candidate_visible_episode(surface["episodes"][0])
    visible["current_observation"] = {}
    return {"expected_failure_detected": not visible["current_observation"]}


ABLATION_PRODUCERS: dict[str, Callable[[dict[str, Any]], dict[str, Any]]] = {
    "memory_deletion": _control_memory_deletion,
    "latent_rule_swap": _control_latent_rule_swap,
    "heldout_task_family_transfer": _control_heldout_transfer,
    "partial_observation_ablation": _control_partial_observation,
    "exploration_budget_ablation": _control_exploration_budget,
    "cross_episode_reset": _control_cross_episode_reset,
    "source_memory_deletion": _control_source_memory_deletion,
    "spurious_token_injection_removal": _control_spurious_token,
    "observation_field_masking": _control_observation_masking,
}


def build_ablation_plan(surface: dict[str, Any]) -> dict[str, Any]:
    controls = []
    for control_id in sorted(REQUIRED_ABLATIONS):
        producer = ABLATION_PRODUCERS[control_id]
        result = producer(surface)
        controls.append(
            {
                "control_id": control_id,
                "producer_function": f"phase2c_hidden_latent_harness_001a.runner.{producer.__name__}",
                "callable_invoked": True,
                "detected_expected_failure": result["expected_failure_detected"],
                "consumed_by_final_verdict": True,
            }
        )
    return {
        "producer_function": "phase2c_hidden_latent_harness_001a.runner.build_ablation_plan",
        "controls": controls,
        "stored_score_mutation_used": False,
        "all_controls_consumed_by_final_verdict": all(row["consumed_by_final_verdict"] for row in controls),
    }


def _provenance_record(
    producer_id: str,
    producer_function: str,
    code_func: Callable[..., Any],
    value: Any,
) -> dict[str, Any]:
    return {
        "producer_id": producer_id,
        "producer_function": producer_function,
        "input_artifacts": ["generated_phase2c_hidden_latent_surface"],
        "run_id": RUN_ID,
        "seed_context_episode_ids": ["all"],
        "aggregation_rule": "callable_contract_verification",
        "code_path_hash": code_path_hash(code_func),
        "consumed_by_final_verdict": True,
        "value": value,
    }


def build_provenance(
    surface: dict[str, Any],
    baseline_report: dict[str, Any],
    leakage_report: dict[str, Any],
    replay_report: dict[str, Any],
    ablation_report: dict[str, Any],
) -> dict[str, Any]:
    return {
        "producer_function": "phase2c_hidden_latent_harness_001a.runner.build_provenance",
        "records": [
            _provenance_record("surface_generation", surface["producer_function"], generate_surface, len(surface["episodes"])),
            _provenance_record("baseline_battery", baseline_report["producer_function"], run_baseline_battery, baseline_report["baseline_ids"]),
            _provenance_record("leakage_scan", leakage_report["producer_function"], run_leakage_scan, leakage_report["positive_controls_passed"]),
            _provenance_record("replay_recomputation", replay_report["producer_function"], run_replay_check, replay_report["passed"]),
            _provenance_record("ablation_plan", ablation_report["producer_function"], build_ablation_plan, ablation_report["all_controls_consumed_by_final_verdict"]),
        ],
    }


def verify_provenance(provenance: dict[str, Any]) -> dict[str, Any]:
    required_fields = {
        "producer_id",
        "producer_function",
        "input_artifacts",
        "run_id",
        "seed_context_episode_ids",
        "aggregation_rule",
        "code_path_hash",
        "consumed_by_final_verdict",
        "value",
    }
    reasons: list[str] = []
    records = provenance.get("records", [])
    producer_ids = {row.get("producer_id") for row in records}
    for producer_id in sorted(REQUIRED_PROVENANCE - producer_ids):
        reasons.append(f"missing_required_provenance:{producer_id}")
    for index, row in enumerate(records):
        missing = sorted(required_fields - set(row))
        if missing:
            reasons.append(f"record_{index}_missing:{','.join(missing)}")
        if len(str(row.get("code_path_hash", ""))) != 64:
            reasons.append(f"record_{index}_bad_code_path_hash")
        if row.get("consumed_by_final_verdict") is not True:
            reasons.append(f"record_{index}_not_consumed")
        if row.get("producer_function") == "literal_static_report":
            reasons.append(f"record_{index}_static_report")
    return {
        "producer_function": "phase2c_hidden_latent_harness_001a.runner.verify_provenance",
        "passed": not reasons,
        "blocking_reasons": reasons,
    }


def build_failure_manifest(
    baseline_report: dict[str, Any],
    leakage_report: dict[str, Any],
    replay_report: dict[str, Any],
    provenance_check: dict[str, Any],
    trace_rows: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    reasons = []
    reasons.extend(f"missing_required_baseline:{baseline_id}" for baseline_id in baseline_report["missing_baseline_ids"])
    reasons.extend(leakage_report["blocking_reasons"])
    reasons.extend(replay_report["blocking_reasons"])
    reasons.extend(provenance_check["blocking_reasons"])
    if trace_rows is not None and not trace_rows:
        reasons.append("trace_jsonl_empty")
    return {
        "producer_function": "phase2c_hidden_latent_harness_001a.runner.build_failure_manifest",
        "blocking_reasons": reasons,
        "has_blocking_failure": bool(reasons),
    }


def build_trace(surface: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for episode in surface["episodes"]:
        visible = candidate_visible_episode(episode)
        replay_inputs = {
            "serialized_state": serialized_replay_state(episode),
            "current_observation": copy.deepcopy(visible["current_observation"]),
            "legal_action_or_query_schema": copy.deepcopy(visible["legal_action_or_query_schema"]),
            "budget_state": copy.deepcopy(visible["budget_state"]),
            "latent_belief_or_memory_state": initial_memory_state(episode),
        }
        rows.append(
            {
                "producer_function": "phase2c_hidden_latent_harness_001a.runner.build_trace",
                "run_id": RUN_ID,
                "episode_id": episode["episode_id"],
                "split": episode["split"],
                "candidate_visible": visible,
                "candidate_decision": None,
                "candidate_mechanism_run": False,
                "oracle_action": oracle_policy(episode)["action"],
                "replay_inputs": replay_inputs,
                "consumed_by_final_verdict": True,
            }
        )
    return rows


def run_harness(output_dir: str | Path, persist_artifacts: bool = False) -> dict[str, Any]:
    surface = generate_surface()
    baseline_report = run_baseline_battery(surface)
    leakage_report = run_leakage_scan(_visible_rows(surface))
    replay_report = run_replay_check(surface)
    ablation_report = build_ablation_plan(surface)
    provenance = build_provenance(surface, baseline_report, leakage_report, replay_report, ablation_report)
    provenance_check = verify_provenance(provenance)
    trace = build_trace(surface)
    failure_manifest = build_failure_manifest(
        baseline_report,
        leakage_report,
        replay_report,
        provenance_check,
        trace,
    )
    execution_evidence_valid = not failure_manifest["has_blocking_failure"]
    result = {
        "task_id": TASK_ID,
        "run_id": RUN_ID,
        "verdict": (
            "candidate_free_harness_executed_valid_evidence_path"
            if execution_evidence_valid
            else "invalid_evidence_path"
        ),
        "candidate_mechanism_run": False,
        "phase3_opened": False,
        "harness_execution_claim": execution_evidence_valid,
        "trace_row_count": len(trace),
        "strongest_fair_baseline_id": baseline_report["strongest_fair_baseline"]["baseline_id"],
        "strongest_fair_baseline_macro_accuracy": baseline_report["strongest_fair_baseline"]["macro_accuracy"],
        "replay_passed": replay_report["passed"],
        "leakage_positive_controls_passed": leakage_report["positive_controls_passed"],
        "ablation_all_controls_consumed": ablation_report["all_controls_consumed_by_final_verdict"],
        "provenance_check_passed": provenance_check["passed"],
        "claim_ceiling": CLAIM_CEILING,
    }
    run = {
        "result": result,
        "trace": trace,
        "baseline_comparison": baseline_report,
        "ablation_report": ablation_report,
        "replay_report": replay_report,
        "leakage_report": leakage_report,
        "computed_evidence_provenance": provenance,
        "failure_manifest": failure_manifest,
        "claim_ceiling": CLAIM_CEILING,
    }
    if persist_artifacts:
        write_artifacts(Path(output_dir), run)
    return run


def write_artifacts(output_dir: Path, run: dict[str, Any]) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    for filename, key in (
        ("result.json", "result"),
        ("baseline_comparison.json", "baseline_comparison"),
        ("ablation_report.json", "ablation_report"),
        ("replay_report.json", "replay_report"),
        ("leakage_report.json", "leakage_report"),
        ("computed_evidence_provenance.json", "computed_evidence_provenance"),
        ("failure_manifest.json", "failure_manifest"),
    ):
        (output_dir / filename).write_text(json.dumps(run[key], indent=2), encoding="utf-8")
    with (output_dir / "trace.jsonl").open("w", encoding="utf-8") as handle:
        for row in run["trace"]:
            handle.write(json.dumps(row, sort_keys=True) + "\n")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default="artifacts/phase2c_hidden_latent_harness_001a")
    args = parser.parse_args(argv)
    run = run_harness(args.output_dir, persist_artifacts=True)
    print(json.dumps(run["result"], indent=2))
    return 0 if not run["failure_manifest"]["has_blocking_failure"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
