from __future__ import annotations

import copy
import hashlib
import inspect
import json
import subprocess
from collections import Counter
from pathlib import Path
from typing import Any, Callable

from gate4_replacement_discriminative_social_latent_001d import core as source_001d

from . import CLAIM_CEILING, TASK_ID


STARTING_BOUNDARY = "79ff36389650a4a32a81cac88d461caacccb6c17"
REQUIRED_TAG = "remote-anchor-gate4-replacement-001d-negative-audit-preservation-anti-zeno-routing-001a-79ff363"
SOURCE_TASK_ID = "gate4_replacement_discriminative_social_latent_001d"
SOURCE_ARTIFACT_DIR = Path("artifacts") / SOURCE_TASK_ID
ARTIFACT_DIR = Path("artifacts") / TASK_ID

VERDICT_BASELINE_EQUIVALENCE = "baseline_equivalence_preserved_negative_evidence"
VERDICT_NO_EQUIVALENT = "no_equivalent_baseline_found_ready_for_independent_audit"
VERDICT_BLOCKED_INCOMPLETE = "blocked_incomplete_adjudication"
VERDICT_SCOPE_MUTATION = "blocked_scope_mutation"
VERDICT_STATIC_OR_STUBBED = "blocked_static_or_stubbed_baseline"

ACTIONS = source_001d.ACTIONS
CUE_SUPPORT = source_001d.CUE_SUPPORT

REQUIRED_BASELINES = [
    "pair_count_table",
    "full_candidate_visible_bundle_decoder",
    "serialized_state_after_update_decoder",
    "feedback_history_only_strongest_decoder",
    "observation_plus_feedback_strongest_decoder",
    "query_action_plus_feedback_strongest_decoder",
    "legal_history_plus_feedback_strongest_decoder",
    "count_table",
    "graph_lookup",
    "transition_table",
    "successor_map",
    "fsm_planner",
    "episodic_traversal",
]

PROTECTED_BOUNDARY_PATHS = [
    Path("src/gate4_replacement_discriminative_social_latent_001b"),
    Path("tests/test_gate4_replacement_discriminative_social_latent_001b.py"),
    Path("artifacts/gate4_replacement_discriminative_social_latent_001b"),
    Path("artifacts/gate4_replacement_discriminative_social_latent_001b_blocked_routing_001a"),
    Path("src/gate4_replacement_discriminative_social_latent_001c"),
    Path("tests/test_gate4_replacement_discriminative_social_latent_001c.py"),
    Path("artifacts/gate4_replacement_discriminative_social_latent_001c"),
    Path("artifacts/gate4_replacement_discriminative_social_latent_001c_negative_audit_preservation_001a"),
    Path("src/gate4_replacement_discriminative_social_latent_001d"),
    Path("tests/test_gate4_replacement_discriminative_social_latent_001d.py"),
    Path("artifacts/gate4_replacement_discriminative_social_latent_001d"),
    Path("artifacts/gate4_replacement_discriminative_social_latent_001d_negative_audit_preservation_001a"),
    Path("docs/research/CLAUDE-INDEPENDENT-EVIDENCE-AUDIT-GATE4-REPLACEMENT-DISCRIMINATIVE-SOCIAL-LATENT-001D.md"),
    Path("docs/research/GATE4-REPLACEMENT-DISCRIMINATIVE-SOCIAL-LATENT-001D-FEEDBACK-LEAKAGE-REPAIR-TASK-CARD-001A.md"),
]

FORBIDDEN_STATUS_PREFIXES = [
    "src/gate4_replacement_discriminative_social_latent_001b",
    "tests/test_gate4_replacement_discriminative_social_latent_001b.py",
    "artifacts/gate4_replacement_discriminative_social_latent_001b",
    "src/gate4_replacement_discriminative_social_latent_001c",
    "tests/test_gate4_replacement_discriminative_social_latent_001c.py",
    "artifacts/gate4_replacement_discriminative_social_latent_001c",
    "src/gate4_replacement_discriminative_social_latent_001d",
    "tests/test_gate4_replacement_discriminative_social_latent_001d.py",
    "artifacts/gate4_replacement_discriminative_social_latent_001d",
    "src/ego_mainline",
    "src/same_agent_bridge",
    "src/post_bridge",
    "artifacts/ego_mainline",
    "artifacts/same_agent_bridge",
    "docs/research/SAME_AGENT_BRIDGE",
]


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _git(args: list[str], cwd: Path | None = None) -> str:
    completed = subprocess.run(
        ["git", *args],
        cwd=str(cwd or _repo_root()),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )
    return completed.stdout.strip()


def _safe_git(args: list[str], cwd: Path | None = None) -> str:
    try:
        return _git(args, cwd=cwd)
    except (FileNotFoundError, subprocess.CalledProcessError):
        return ""


def _normalize_status_path(path: str) -> str:
    return path.replace("\\", "/")


def _status_path_from_line(line: str) -> str:
    if len(line) >= 3 and line[2] == " ":
        return line[3:]
    return line[2:].lstrip() if len(line) > 2 else line


def _path_status(prefixes: list[str]) -> bool:
    raw = _safe_git(["status", "--porcelain=v1"])
    for line in raw.splitlines():
        path = _normalize_status_path(_status_path_from_line(line))
        if any(path.startswith(prefix) for prefix in prefixes):
            return True
    return False


def _read_json(path: Path) -> Any:
    return json.loads((_repo_root() / path).read_text(encoding="utf-8"))


def load_source_trace_records() -> list[dict[str, Any]]:
    trace_path = _repo_root() / SOURCE_ARTIFACT_DIR / "trace_records.jsonl"
    return [json.loads(line) for line in trace_path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _json_ready(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: _json_ready(child) for key, child in value.items()}
    if isinstance(value, list):
        return [_json_ready(child) for child in value]
    if isinstance(value, tuple):
        return [_json_ready(child) for child in value]
    return value


def _write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(_json_ready(value), indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _target(record: dict[str, Any]) -> str:
    return str(record["scorer_only_target_action"])


def _candidate_prediction(record: dict[str, Any]) -> str:
    return str(record["final_prediction"])


def _candidate_visible(record: dict[str, Any]) -> dict[str, Any]:
    return record.get("candidate_visible", {})


def _signal_tokens(record: dict[str, Any]) -> list[str]:
    visible = _candidate_visible(record)
    tokens = []
    for event in visible.get("feedback_history", []):
        token = str(event.get("token", ""))
        if token in CUE_SUPPORT and CUE_SUPPORT[token]:
            tokens.append(token)
    return tokens


def _unordered_pair_key(record: dict[str, Any]) -> tuple[str, ...]:
    return tuple(sorted(_signal_tokens(record)))


def _majority_action(records: list[dict[str, Any]]) -> str:
    counts = Counter(_target(record) for record in records)
    if not counts:
        return ACTIONS[0]
    return max(ACTIONS, key=lambda action: (counts[action], -ACTIONS.index(action)))


def _score_predictions(records: list[dict[str, Any]], predictions: dict[str, str]) -> float:
    if not records:
        return 0.0
    correct = sum(1 for record in records if predictions.get(record["episode_id"]) == _target(record))
    return correct / len(records)


def _score_predictor(records: list[dict[str, Any]], predictor: Callable[[dict[str, Any]], str]) -> float:
    predictions = {record["episode_id"]: predictor(record) for record in records}
    return _score_predictions(records, predictions)


def _action_from_support_intersection(tokens: list[str]) -> str | None:
    if len(tokens) < 2:
        return None
    supports = [set(CUE_SUPPORT.get(token, [])) for token in tokens if CUE_SUPPORT.get(token)]
    if not supports:
        return None
    intersection = set.intersection(*supports)
    if not intersection:
        return None
    return ACTIONS[min(intersection)]


def _single_token_prediction(tokens: list[str], fallback: str) -> str:
    if not tokens:
        return fallback
    support = CUE_SUPPORT.get(tokens[0], [])
    if not support:
        return fallback
    return ACTIONS[min(support)]


def _train_pair_count_table(records: list[dict[str, Any]]) -> dict[tuple[str, ...], Counter[str]]:
    table: dict[tuple[str, ...], Counter[str]] = {}
    for record in records:
        key = _unordered_pair_key(record)
        if not key:
            continue
        table.setdefault(key, Counter())[_target(record)] += 1
    return table


def _predict_from_pair_table(
    record: dict[str, Any],
    table: dict[tuple[str, ...], Counter[str]],
    fallback: str,
) -> str:
    key = _unordered_pair_key(record)
    if len(key) == 1:
        return _single_token_prediction(list(key), fallback)
    if key in table and table[key]:
        counts = table[key]
        return max(ACTIONS, key=lambda action: (counts[action], -ACTIONS.index(action)))
    intersection = _action_from_support_intersection(list(key))
    return intersection or fallback


def _score_pair_table(records: list[dict[str, Any]], training_records: list[dict[str, Any]] | None = None) -> float:
    training = training_records or records
    fallback = _majority_action(training)
    predictions: dict[str, str] = {}
    for record in records:
        if training_records is None:
            table = _train_pair_count_table([row for row in records if row["episode_id"] != record["episode_id"]])
        else:
            table = _train_pair_count_table(training)
        predictions[record["episode_id"]] = _predict_from_pair_table(record, table, fallback)
    return _score_predictions(records, predictions)


def baseline_pair_count_table(records: list[dict[str, Any]]) -> float:
    return _score_pair_table(records)


def _state_decoder_prediction(record: dict[str, Any], fallback: str) -> str:
    state = _candidate_visible(record).get("serialized_state_after_update")
    if not isinstance(state, dict):
        return fallback
    vector = state.get("latent_basis_scores")
    if not isinstance(vector, list) or not vector:
        return fallback
    values = [float(value) for value in vector]
    best_index = max(range(len(values)), key=lambda idx: (values[idx], -idx))
    if best_index >= len(ACTIONS):
        return fallback
    return ACTIONS[best_index]


def baseline_serialized_state_after_update_decoder(records: list[dict[str, Any]]) -> float:
    fallback = _majority_action(records)
    return _score_predictor(records, lambda record: _state_decoder_prediction(record, fallback))


def baseline_full_candidate_visible_bundle_decoder(records: list[dict[str, Any]]) -> float:
    fallback = _majority_action(records)
    table = _train_pair_count_table(records)

    def predict(record: dict[str, Any]) -> str:
        state_prediction = _state_decoder_prediction(record, fallback)
        if state_prediction != fallback or _candidate_visible(record).get("serialized_state_after_update"):
            return state_prediction
        return _predict_from_pair_table(record, table, fallback)

    return _score_predictor(records, predict)


def baseline_feedback_history_only_strongest_decoder(records: list[dict[str, Any]]) -> float:
    return _score_pair_table(records)


def baseline_observation_plus_feedback_strongest_decoder(records: list[dict[str, Any]]) -> float:
    return _score_pair_table(records)


def baseline_query_action_plus_feedback_strongest_decoder(records: list[dict[str, Any]]) -> float:
    query_visible = [
        record
        for record in records
        if _candidate_visible(record).get("query_action", {}).get("query_budget_spent", 0) > 0
    ]
    if len(query_visible) != len(records):
        return _score_predictor(records, lambda _record: _majority_action(records))
    return _score_pair_table(records)


def baseline_legal_history_plus_feedback_strongest_decoder(records: list[dict[str, Any]]) -> float:
    legal_visible = [record for record in records if _candidate_visible(record).get("legal_history")]
    if len(legal_visible) != len(records):
        return _score_predictor(records, lambda _record: _majority_action(records))
    return _score_pair_table(records)


def baseline_count_table(records: list[dict[str, Any]]) -> float:
    return _score_pair_table(records)


def baseline_graph_lookup(records: list[dict[str, Any]]) -> float:
    fallback = _majority_action(records)
    return _score_predictor(
        records,
        lambda record: _action_from_support_intersection(_signal_tokens(record)) or fallback,
    )


def baseline_transition_table(records: list[dict[str, Any]]) -> float:
    fallback = _majority_action(records)

    def predict(record: dict[str, Any]) -> str:
        vector = [0.0, 0.0, 0.0, 0.0]
        for token in _signal_tokens(record):
            for slot in CUE_SUPPORT.get(token, []):
                vector[slot] += 1.0
        if not any(vector):
            return fallback
        return ACTIONS[max(range(len(vector)), key=lambda idx: (vector[idx], -idx))]

    return _score_predictor(records, predict)


def baseline_successor_map(records: list[dict[str, Any]]) -> float:
    fallback = _majority_action(records)
    successor = {
        tuple(sorted(tokens)): action
        for tokens, action in [
            (("cue_alpha", "cue_beta"), "direct_response"),
            (("cue_gamma", "cue_delta"), "reflective_question"),
            (("cue_alpha", "cue_gamma"), "boundary_option"),
            (("cue_beta", "cue_delta"), "planning_summary"),
        ]
    }
    return _score_predictor(records, lambda record: successor.get(_unordered_pair_key(record), fallback))


def baseline_fsm_planner(records: list[dict[str, Any]]) -> float:
    fallback = _majority_action(records)

    def predict(record: dict[str, Any]) -> str:
        active_slots: set[int] | None = None
        for token in _signal_tokens(record):
            support = set(CUE_SUPPORT.get(token, []))
            active_slots = support if active_slots is None else active_slots & support
        if not active_slots:
            return fallback
        return ACTIONS[min(active_slots)]

    return _score_predictor(records, predict)


def baseline_episodic_traversal(records: list[dict[str, Any]]) -> float:
    fallback = _majority_action(records)
    predictions = {}
    for record in records:
        key = _unordered_pair_key(record)
        exemplars = [row for row in records if row["episode_id"] != record["episode_id"] and _unordered_pair_key(row) == key]
        predictions[record["episode_id"]] = _target(exemplars[0]) if exemplars else fallback
    return _score_predictions(records, predictions)


BASELINE_FUNCTIONS: dict[str, Callable[[list[dict[str, Any]]], float]] = {
    "pair_count_table": baseline_pair_count_table,
    "full_candidate_visible_bundle_decoder": baseline_full_candidate_visible_bundle_decoder,
    "serialized_state_after_update_decoder": baseline_serialized_state_after_update_decoder,
    "feedback_history_only_strongest_decoder": baseline_feedback_history_only_strongest_decoder,
    "observation_plus_feedback_strongest_decoder": baseline_observation_plus_feedback_strongest_decoder,
    "query_action_plus_feedback_strongest_decoder": baseline_query_action_plus_feedback_strongest_decoder,
    "legal_history_plus_feedback_strongest_decoder": baseline_legal_history_plus_feedback_strongest_decoder,
    "count_table": baseline_count_table,
    "graph_lookup": baseline_graph_lookup,
    "transition_table": baseline_transition_table,
    "successor_map": baseline_successor_map,
    "fsm_planner": baseline_fsm_planner,
    "episodic_traversal": baseline_episodic_traversal,
}


def _candidate_score(records: list[dict[str, Any]]) -> float:
    return _score_predictor(records, _candidate_prediction)


def run_baseline_equivalence(records: list[dict[str, Any]], candidate_score: float) -> dict[str, Any]:
    rows = []
    scores = {}
    for baseline_id in REQUIRED_BASELINES:
        producer = BASELINE_FUNCTIONS[baseline_id]
        score = producer(records)
        scores[baseline_id] = score
        rows.append(
            {
                "baseline_id": baseline_id,
                "producer_function": producer.__name__,
                "score": score,
                "callable_invoked": True,
                "static_score_injection": False,
                "ties_candidate": score >= candidate_score,
            }
        )
    strongest = max(rows, key=lambda row: (row["score"], -REQUIRED_BASELINES.index(row["baseline_id"])))
    equivalence = strongest["score"] >= candidate_score
    return {
        "producer_function": "run_baseline_equivalence",
        "candidate_score": candidate_score,
        "invoked_baselines": [row["baseline_id"] for row in rows],
        "scores": scores,
        "rows": rows,
        "strongest_faithful_baseline": {
            "baseline_id": strongest["baseline_id"],
            "producer_function": strongest["producer_function"],
            "score": strongest["score"],
        },
        "baseline_equivalence": equivalence,
        "baseline_tie_is_negative_evidence": equivalence,
        "verdict": VERDICT_BASELINE_EQUIVALENCE if equivalence else VERDICT_NO_EQUIVALENT,
        "invocation_check": verify_required_baseline_invocations({"invoked_baselines": [row["baseline_id"] for row in rows]}),
    }


def verify_required_baseline_invocations(report: dict[str, Any]) -> dict[str, Any]:
    invoked = set(report.get("invoked_baselines", []))
    missing = [baseline_id for baseline_id in REQUIRED_BASELINES if baseline_id not in invoked]
    return {
        "producer_function": "verify_required_baseline_invocations",
        "passed": not missing,
        "missing_baselines": missing,
    }


def build_decoder_probe_report(records: list[dict[str, Any]]) -> dict[str, Any]:
    probes = {
        "feedback_history_only_strongest_decoder": baseline_feedback_history_only_strongest_decoder(records),
        "observation_plus_feedback_strongest_decoder": baseline_observation_plus_feedback_strongest_decoder(records),
        "query_action_plus_feedback_strongest_decoder": baseline_query_action_plus_feedback_strongest_decoder(records),
        "legal_history_plus_feedback_strongest_decoder": baseline_legal_history_plus_feedback_strongest_decoder(records),
        "serialized_state_after_update_decoder": baseline_serialized_state_after_update_decoder(records),
        "full_candidate_visible_bundle_decoder": baseline_full_candidate_visible_bundle_decoder(records),
        "observation_only_control": _score_predictor(records, lambda _record: _majority_action(records)),
    }
    return {
        "producer_function": "build_decoder_probe_report",
        "probes": {
            name: {
                "producer_function": name if name == "observation_only_control" else f"baseline_{name}",
                "score": score,
                "computed_from_callable": True,
            }
            for name, score in probes.items()
        },
        "strongest_decoder": max(probes.items(), key=lambda item: item[1])[0],
    }


def _with_feedback(record: dict[str, Any], feedback_history: list[dict[str, Any]]) -> dict[str, Any]:
    changed = copy.deepcopy(record)
    changed["candidate_visible"]["feedback_history"] = copy.deepcopy(feedback_history)
    return changed


def _transform_records(records: list[dict[str, Any]], intervention: str) -> list[dict[str, Any]]:
    if intervention == "full_two_token_feedback":
        return copy.deepcopy(records)
    if intervention == "single_token_feedback_only":
        transformed = []
        for record in records:
            first_signal = [
                event for event in _candidate_visible(record).get("feedback_history", []) if event.get("token") in CUE_SUPPORT and CUE_SUPPORT[event.get("token")]
            ][:1]
            transformed.append(_with_feedback(record, first_signal))
        return transformed
    if intervention == "shuffled_feedback_pair":
        transformed = []
        for record in records:
            feedback = list(reversed(_candidate_visible(record).get("feedback_history", [])))
            transformed.append(_with_feedback(record, feedback))
        return transformed
    if intervention == "counterfactual_feedback_pair":
        episodes = {episode.episode_id: episode for episode in source_001d.generate_episodes()}
        return [
            _with_feedback(record, episodes[str(record["episode_id"])].counterfactual_feedback_history)
            for record in records
        ]
    if intervention == "serialized_state_field_removal":
        transformed = copy.deepcopy(records)
        for record in transformed:
            record["candidate_visible"].pop("serialized_state_after_update", None)
            record["candidate_visible"].pop("serialized_state_before_update", None)
        return transformed
    if intervention == "feedback_history_removal":
        return [_with_feedback(record, []) for record in records]
    if intervention == "observation_only_control":
        transformed = copy.deepcopy(records)
        for record in transformed:
            visible = record["candidate_visible"]
            visible["feedback_history"] = []
            visible["legal_history"] = []
            visible["query_action"] = {"query_type": "observation_only_control", "query_budget_spent": 0}
            visible.pop("serialized_state_after_update", None)
            visible.pop("serialized_state_before_update", None)
        return transformed
    raise KeyError(intervention)


def build_recoverability_adjudication_report(records: list[dict[str, Any]], candidate_score: float) -> dict[str, Any]:
    interventions = {}
    for intervention in [
        "single_token_feedback_only",
        "full_two_token_feedback",
        "shuffled_feedback_pair",
        "counterfactual_feedback_pair",
        "serialized_state_field_removal",
        "feedback_history_removal",
        "observation_only_control",
    ]:
        transformed = _transform_records(records, intervention)
        interventions[intervention] = {
            "producer_function": "build_recoverability_adjudication_report",
            "pair_count_table_score": _score_pair_table(transformed, training_records=records),
            "serialized_state_after_update_decoder_score": baseline_serialized_state_after_update_decoder(transformed),
            "full_candidate_visible_bundle_decoder_score": baseline_full_candidate_visible_bundle_decoder(transformed),
            "records_recomputed": len(transformed),
        }
    pair_tied = interventions["full_two_token_feedback"]["pair_count_table_score"] >= candidate_score
    return {
        "producer_function": "build_recoverability_adjudication_report",
        "interventions": interventions,
        "candidate_advantage_survives_faithful_baselines": not pair_tied,
        "stop_condition_triggered": "pair_count_table_tied_candidate" if pair_tied else "",
        "classification": VERDICT_BASELINE_EQUIVALENCE if pair_tied else VERDICT_NO_EQUIVALENT,
    }


def build_trace_probe_report(records: list[dict[str, Any]]) -> dict[str, Any]:
    removed_state = _transform_records(records, "serialized_state_field_removal")
    removed_feedback = _transform_records(records, "feedback_history_removal")
    return {
        "producer_function": "build_trace_probe_report",
        "records_checked": len(records),
        "serialized_state_replay_score": baseline_serialized_state_after_update_decoder(records),
        "feedback_pair_replay_score": baseline_pair_count_table(records),
        "recomputed_from_serialized_state": True,
        "recomputed_from_feedback_history": True,
        "corruption_controls": {
            "removed_serialized_state_score": baseline_serialized_state_after_update_decoder(removed_state),
            "removed_feedback_history_score": baseline_pair_count_table(removed_feedback),
        },
    }


def hash_protected_boundaries(root: Path | None = None) -> dict[str, str | None]:
    base = root or _repo_root()
    results: dict[str, str | None] = {}
    for protected_path in PROTECTED_BOUNDARY_PATHS:
        path = base / protected_path
        if not path.exists():
            results[str(protected_path)] = None
            continue
        digest = hashlib.sha256()
        if path.is_file():
            digest.update(path.read_bytes())
        else:
            for file_path in sorted(child for child in path.rglob("*") if child.is_file()):
                digest.update(str(file_path.relative_to(path)).replace("\\", "/").encode("utf-8"))
                digest.update(file_path.read_bytes())
        results[str(protected_path)] = digest.hexdigest()
    return results


def build_non_mutation_guard(before_hashes: dict[str, str | None], after_hashes: dict[str, str | None]) -> dict[str, Any]:
    changed = sorted(path for path in before_hashes if before_hashes[path] != after_hashes.get(path))
    return {
        "producer_function": "build_non_mutation_guard",
        "protected_paths": sorted(before_hashes),
        "changed_protected_paths": changed,
        "old_001b_001c_001d_modified": bool(changed),
        "forbidden_status_modified": _path_status(FORBIDDEN_STATUS_PREFIXES),
        "passed": not changed and not _path_status(FORBIDDEN_STATUS_PREFIXES),
    }


def build_source_pin_readback(run_id: str) -> dict[str, Any]:
    local_head = _safe_git(["rev-parse", "HEAD"])
    local_required_tag = _safe_git(["rev-parse", REQUIRED_TAG])
    remote_required_tag = ""
    remote_branch = ""
    remote_rows = _safe_git(["ls-remote", "origin", f"refs/tags/{REQUIRED_TAG}", "refs/heads/codex/meta-theory-scaffold"])
    for row in remote_rows.splitlines():
        if not row.strip():
            continue
        commit, ref = row.split(maxsplit=1)
        if ref == f"refs/tags/{REQUIRED_TAG}":
            remote_required_tag = commit
        if ref == "refs/heads/codex/meta-theory-scaffold":
            remote_branch = commit
    source_artifacts = {
        "trace_records": str(SOURCE_ARTIFACT_DIR / "trace_records.jsonl"),
        "result": str(SOURCE_ARTIFACT_DIR / "result.json"),
        "candidate_report": str(SOURCE_ARTIFACT_DIR / "candidate_report.json"),
        "baseline_report": str(SOURCE_ARTIFACT_DIR / "baseline_report.json"),
    }
    return {
        "producer_function": "build_source_pin_readback",
        "task_id": TASK_ID,
        "run_id": run_id,
        "starting_boundary": STARTING_BOUNDARY,
        "required_tag": REQUIRED_TAG,
        "local_head": local_head,
        "local_required_tag": local_required_tag,
        "remote_required_tag": remote_required_tag,
        "remote_branch": remote_branch,
        "source_boundary_verified": all(
            value == STARTING_BOUNDARY
            for value in [local_head, local_required_tag, remote_required_tag, remote_branch]
        ),
        "source_artifacts": source_artifacts,
        "source_artifacts_exist": {
            name: (_repo_root() / Path(path)).exists() for name, path in source_artifacts.items()
        },
    }


def _downstream_authorization_flags() -> dict[str, bool]:
    return {
        "gate5_authorized": False,
        "admission_authorized": False,
        "bridge_authorized": False,
        "runtime_authorized": False,
        "ego_mainline_authorized": False,
        "ui_authorized": False,
        "llm_airi_integration_authorized": False,
        "relationship_emotion_user_benefit_authorized": False,
    }


def evaluate_acceptance(run: dict[str, Any]) -> dict[str, Any]:
    reasons = []
    if not run["source_pin_readback"]["source_boundary_verified"]:
        reasons.append("source_boundary_not_verified")
    if not run["non_mutation_guard"]["passed"]:
        reasons.append("non_mutation_guard_failed")
    if not verify_required_baseline_invocations(run["baseline_equivalence_report"])["passed"]:
        reasons.append("missing_baseline_invocation")
    if not verify_provenance(run["provenance_report"])["passed"]:
        reasons.append("provenance_gate_failed")
    if any(run["result"]["downstream_authorization_flags"].values()):
        reasons.append("downstream_authorization_flag_true")
    if run["baseline_equivalence_report"]["baseline_equivalence"]:
        verdict = VERDICT_BASELINE_EQUIVALENCE
    elif reasons:
        verdict = VERDICT_BLOCKED_INCOMPLETE
    else:
        verdict = VERDICT_NO_EQUIVALENT
    if run["non_mutation_guard"]["old_001b_001c_001d_modified"] or run["non_mutation_guard"]["forbidden_status_modified"]:
        verdict = VERDICT_SCOPE_MUTATION
    if not verify_provenance(run["provenance_report"])["passed"]:
        verdict = VERDICT_STATIC_OR_STUBBED
    return {
        "producer_function": "evaluate_acceptance",
        "passed": not reasons,
        "blocking_reasons": sorted(set(reasons)),
        "verdict": verdict,
    }


def build_result(run: dict[str, Any], acceptance: dict[str, Any] | None = None) -> dict[str, Any]:
    flags = _downstream_authorization_flags()
    verdict = acceptance["verdict"] if acceptance else run["baseline_equivalence_report"]["verdict"]
    return {
        "producer_function": "build_result",
        "task_id": TASK_ID,
        "verdict": verdict,
        "candidate_score_readback": run["candidate_score_readback"],
        "pair_count_table_score": run["baseline_equivalence_report"]["scores"]["pair_count_table"],
        "full_bundle_decoder_score": run["baseline_equivalence_report"]["scores"]["full_candidate_visible_bundle_decoder"],
        "serialized_state_decoder_score": run["baseline_equivalence_report"]["scores"]["serialized_state_after_update_decoder"],
        "strongest_faithful_baseline": run["baseline_equivalence_report"]["strongest_faithful_baseline"],
        "baseline_equivalence": run["baseline_equivalence_report"]["baseline_equivalence"],
        "baseline_tie_classification": "negative_evidence" if run["baseline_equivalence_report"]["baseline_equivalence"] else "not_tied",
        "positive_mechanism_evidence_allowed": False,
        "downstream_authorization_flags": flags,
        "downstream_authorization_flags_all_false": not any(flags.values()),
        "safe_to_enter_gate5": False,
        "safe_to_enter_admission": False,
        "safe_to_enter_bridge": False,
        "safe_to_enter_runtime": False,
        "safe_to_enter_ego_mainline": False,
        "claim_ceiling": CLAIM_CEILING,
        "what_this_does_not_prove": [
            "replacement Gate4 validity",
            "Gate5 readiness",
            "admission readiness",
            "bridge readiness",
            "runtime readiness",
            "EGO mainline readiness",
            "social agency",
            "selfhood",
            "consciousness",
            "real emotion",
            "autonomy",
            "relationship learning",
            "user benefit",
        ],
    }


def code_path_hash(func: Callable[..., Any]) -> str:
    return hashlib.sha256(inspect.getsource(func).encode("utf-8")).hexdigest()


def resolve_producer(name: str) -> Callable[..., Any]:
    producers: dict[str, Callable[..., Any]] = {
        "run_baseline_equivalence": run_baseline_equivalence,
        "build_decoder_probe_report": build_decoder_probe_report,
        "build_recoverability_adjudication_report": build_recoverability_adjudication_report,
        "build_trace_probe_report": build_trace_probe_report,
        "build_source_pin_readback": build_source_pin_readback,
        "build_non_mutation_guard": build_non_mutation_guard,
        "build_result": build_result,
        "baseline_pair_count_table": baseline_pair_count_table,
        "baseline_full_candidate_visible_bundle_decoder": baseline_full_candidate_visible_bundle_decoder,
        "baseline_serialized_state_after_update_decoder": baseline_serialized_state_after_update_decoder,
        "baseline_feedback_history_only_strongest_decoder": baseline_feedback_history_only_strongest_decoder,
        "baseline_observation_plus_feedback_strongest_decoder": baseline_observation_plus_feedback_strongest_decoder,
        "baseline_query_action_plus_feedback_strongest_decoder": baseline_query_action_plus_feedback_strongest_decoder,
        "baseline_legal_history_plus_feedback_strongest_decoder": baseline_legal_history_plus_feedback_strongest_decoder,
        "baseline_count_table": baseline_count_table,
        "baseline_graph_lookup": baseline_graph_lookup,
        "baseline_transition_table": baseline_transition_table,
        "baseline_successor_map": baseline_successor_map,
        "baseline_fsm_planner": baseline_fsm_planner,
        "baseline_episodic_traversal": baseline_episodic_traversal,
    }
    return producers[name]


def _record_scope(records: list[dict[str, Any]]) -> dict[str, list[str]]:
    return {
        "seed_ids": sorted({str(record["seed_id"]) for record in records}),
        "context_ids": sorted({str(record["context_id"]) for record in records}),
        "episode_ids": sorted({str(record["episode_id"]) for record in records}),
    }


def _provenance_record(
    result_family: str,
    producer_function: str,
    score: float,
    run_id: str,
    records: list[dict[str, Any]],
    identifier: str,
    artifact_pointer: str,
    input_artifacts: list[str],
) -> dict[str, Any]:
    scope = _record_scope(records)
    return {
        "result_family": result_family,
        "producer_function": producer_function,
        "input_artifacts": input_artifacts,
        "run_id": run_id,
        "seed_ids": scope["seed_ids"],
        "context_ids": scope["context_ids"],
        "episode_ids": scope["episode_ids"],
        "split_name": "all_001d_splits",
        "aggregation_rule": "score computed by callable 001E adjudication path over 001D trace records",
        "computed_score": score,
        "code_path_hash": code_path_hash(resolve_producer(producer_function)),
        "candidate_or_baseline_identifier": identifier,
        "artifact_pointer": artifact_pointer,
        "static_score_injection": False,
    }


def build_provenance_report(run: dict[str, Any], records: list[dict[str, Any]]) -> dict[str, Any]:
    run_id = run["run_id"]
    provenance_records = [
        _provenance_record(
            "baseline_equivalence_report",
            "run_baseline_equivalence",
            run["baseline_equivalence_report"]["strongest_faithful_baseline"]["score"],
            run_id,
            records,
            "strongest_faithful_baseline",
            "baseline_equivalence_report.json",
            [str(SOURCE_ARTIFACT_DIR / "trace_records.jsonl")],
        ),
        _provenance_record(
            "decoder_probe_report",
            "build_decoder_probe_report",
            run["decoder_probe_report"]["probes"][run["decoder_probe_report"]["strongest_decoder"]]["score"],
            run_id,
            records,
            "decoder_probe",
            "decoder_probe_report.json",
            [str(SOURCE_ARTIFACT_DIR / "trace_records.jsonl")],
        ),
        _provenance_record(
            "recoverability_adjudication_report",
            "build_recoverability_adjudication_report",
            run["recoverability_adjudication_report"]["interventions"]["full_two_token_feedback"]["pair_count_table_score"],
            run_id,
            records,
            "pair_count_table_intervention",
            "recoverability_adjudication_report.json",
            [str(SOURCE_ARTIFACT_DIR / "trace_records.jsonl")],
        ),
        _provenance_record(
            "trace_probe_report",
            "build_trace_probe_report",
            run["trace_probe_report"]["serialized_state_replay_score"],
            run_id,
            records,
            "trace_probe",
            "trace_probe_report.json",
            [str(SOURCE_ARTIFACT_DIR / "trace_records.jsonl")],
        ),
        _provenance_record(
            "source_pin_readback",
            "build_source_pin_readback",
            1.0 if run["source_pin_readback"]["source_boundary_verified"] else 0.0,
            run_id,
            records,
            "source_pin",
            "source_pin_readback.json",
            [str(SOURCE_ARTIFACT_DIR / "result.json")],
        ),
        _provenance_record(
            "non_mutation_guard",
            "build_non_mutation_guard",
            1.0 if run["non_mutation_guard"]["passed"] else 0.0,
            run_id,
            records,
            "non_mutation_guard",
            "non_mutation_guard.json",
            [str(SOURCE_ARTIFACT_DIR / "trace_records.jsonl")],
        ),
        _provenance_record(
            "result",
            "build_result",
            1.0 if run["result"]["baseline_equivalence"] else 0.0,
            run_id,
            records,
            "result",
            "result.json",
            ["baseline_equivalence_report.json", "recoverability_adjudication_report.json"],
        ),
    ]
    for row in run["baseline_equivalence_report"]["rows"]:
        provenance_records.append(
            _provenance_record(
                f"baseline:{row['baseline_id']}",
                row["producer_function"],
                row["score"],
                run_id,
                records,
                row["baseline_id"],
                "baseline_equivalence_report.json",
                [str(SOURCE_ARTIFACT_DIR / "trace_records.jsonl")],
            )
        )
    report = {"producer_function": "build_provenance_report", "records": provenance_records}
    report["verification"] = verify_provenance(report)
    return report


def verify_provenance(report: dict[str, Any]) -> dict[str, Any]:
    reasons = []
    required_fields = {
        "producer_function",
        "input_artifacts",
        "run_id",
        "seed_ids",
        "context_ids",
        "episode_ids",
        "split_name",
        "aggregation_rule",
        "computed_score",
        "code_path_hash",
        "candidate_or_baseline_identifier",
        "artifact_pointer",
    }
    for row in report.get("records", []):
        missing = sorted(field for field in required_fields if field not in row)
        for field in missing:
            reasons.append(f"missing_field:{row.get('result_family')}:{field}")
        if row.get("static_score_injection"):
            reasons.append("static_score_injection")
        producer_name = str(row.get("producer_function", ""))
        try:
            producer = resolve_producer(producer_name)
        except KeyError:
            reasons.append(f"unknown_producer:{producer_name}")
            continue
        if row.get("code_path_hash") != code_path_hash(producer):
            reasons.append(f"code_path_hash_mismatch:{producer_name}")
        if not row.get("input_artifacts"):
            reasons.append(f"missing_input_artifacts:{row.get('result_family')}")
    return {
        "producer_function": "verify_provenance",
        "passed": not reasons,
        "blocking_reasons": sorted(set(reasons)),
    }


def _write_artifacts(output_dir: Path, run: dict[str, Any]) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    artifact_map = {
        "result.json": run["result"],
        "source_pin_readback.json": run["source_pin_readback"],
        "baseline_equivalence_report.json": run["baseline_equivalence_report"],
        "recoverability_adjudication_report.json": run["recoverability_adjudication_report"],
        "decoder_probe_report.json": run["decoder_probe_report"],
        "trace_probe_report.json": run["trace_probe_report"],
        "provenance_report.json": run["provenance_report"],
        "non_mutation_guard.json": run["non_mutation_guard"],
    }
    for name, payload in artifact_map.items():
        _write_json(output_dir / name, payload)
    (output_dir / "claim_ceiling.txt").write_text(CLAIM_CEILING + "\n", encoding="utf-8")


def execute_adjudication(output_dir: str | Path | None = ARTIFACT_DIR, persist_artifacts: bool = True) -> dict[str, Any]:
    run_id = f"{TASK_ID}-{STARTING_BOUNDARY[:8]}"
    before_hashes = hash_protected_boundaries(_repo_root())
    records = load_source_trace_records()
    candidate_score = _candidate_score(records)
    source_result = _read_json(SOURCE_ARTIFACT_DIR / "result.json")
    source_candidate_report = _read_json(SOURCE_ARTIFACT_DIR / "candidate_report.json")
    baseline_equivalence_report = run_baseline_equivalence(records, candidate_score)
    decoder_probe_report = build_decoder_probe_report(records)
    recoverability_adjudication_report = build_recoverability_adjudication_report(records, candidate_score)
    trace_probe_report = build_trace_probe_report(records)
    source_pin_readback = build_source_pin_readback(run_id)
    after_hashes = hash_protected_boundaries(_repo_root())
    non_mutation_guard = build_non_mutation_guard(before_hashes, after_hashes)
    run: dict[str, Any] = {
        "run_id": run_id,
        "task_id": TASK_ID,
        "source_task_id": SOURCE_TASK_ID,
        "candidate_score_readback": candidate_score,
        "source_result_verdict": source_result.get("verdict"),
        "source_result_candidate_score": source_result.get("candidate_score"),
        "source_candidate_report_score": source_candidate_report.get("score"),
        "baseline_equivalence_report": baseline_equivalence_report,
        "recoverability_adjudication_report": recoverability_adjudication_report,
        "decoder_probe_report": decoder_probe_report,
        "trace_probe_report": trace_probe_report,
        "source_pin_readback": source_pin_readback,
        "non_mutation_guard": non_mutation_guard,
    }
    run["result"] = build_result(run)
    run["provenance_report"] = build_provenance_report(run, records)
    acceptance = evaluate_acceptance(run)
    run["acceptance_gate"] = acceptance
    run["result"] = build_result(run, acceptance=acceptance)
    run["provenance_report"] = build_provenance_report(run, records)
    if persist_artifacts and output_dir is not None:
        _write_artifacts(Path(output_dir), run)
    return run
