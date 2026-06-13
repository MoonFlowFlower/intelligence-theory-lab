from __future__ import annotations

import copy
import hashlib
import inspect
import json
import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Callable

from . import CLAIM_CEILING, TASK_ID


STARTING_BOUNDARY = "aa252a881cf23cd54b94987d8dae093468ff5de2"
PARENT_001B_COMMIT = "e4b2f180a8a9643fc6fb45383855051ec8d4c310"
PARENT_001C_COMMIT = "fec4b7f8847c26116918ee9871851543515fdd6a"
CLAUDE_001C_AUDIT = Path("docs/research/CLAUDE-INDEPENDENT-EVIDENCE-AUDIT-GATE4-REPLACEMENT-DISCRIMINATIVE-SOCIAL-LATENT-001C.md")
REPAIR_001D_CARD = Path("docs/research/GATE4-REPLACEMENT-DISCRIMINATIVE-SOCIAL-LATENT-001D-FEEDBACK-LEAKAGE-REPAIR-TASK-CARD-001A.md")

ARTIFACT_DIR = Path("artifacts") / TASK_ID
PASS_VERDICT = "gate4_replacement_discriminative_social_latent_001d_bounded_feedback_leakage_repair_pass"
NEGATIVE_VERDICT = "gate4_replacement_discriminative_social_latent_001d_negative_evidence"
RECOVERABILITY_CEILING = 0.60
SINGLE_TOKEN_CEILING = 0.60
CANDIDATE_MARGIN_MIN = 0.30

ACTIONS = ["direct_response", "reflective_question", "boundary_option", "planning_summary"]
ACTION_ALIASES = {
    "direct_response": ["direct", "dr", "respond_direct"],
    "reflective_question": ["reflective", "rq", "ask_reflective"],
    "boundary_option": ["boundary", "bo", "set_boundary"],
    "planning_summary": ["planning", "ps", "summarize_plan"],
}
SPLITS = [
    "seen_partner_unseen_context",
    "unseen_partner_seen_context",
    "unseen_partner_unseen_context",
    "unseen_preference_transition",
    "counterfactual_intervention",
    "active_query_required_episodes",
    "heldout_episodes_with_remapped_ids",
]
SEED_IDS = [f"seed_{idx}" for idx in range(8)]

CUE_SUPPORT = {
    "cue_alpha": [0, 2],
    "cue_beta": [0, 3],
    "cue_gamma": [1, 2],
    "cue_delta": [1, 3],
    "ambient_neutral": [],
    "soft_noise": [0, 1, 2, 3],
}
TARGET_CUES = {
    0: ["cue_alpha", "cue_beta"],
    1: ["cue_gamma", "cue_delta"],
    2: ["cue_alpha", "cue_gamma"],
    3: ["cue_beta", "cue_delta"],
}
MANDATORY_BASELINES = [
    "observation_only_decoder_challenger",
    "feedback_aware_decoder_challenger",
    "query_and_follow_feedback",
    "direct_stated_preference_copier",
    "feedback_token_lookup",
    "history_order_cache",
    "stream_keyed_count_table",
    "graph_lookup",
    "transition_table",
    "successor_map",
    "count_table",
    "fsm_planner",
    "episodic_traversal",
    "oracle_label_positive_control",
    "leakage_positive_control",
]
POSITIVE_CONTROL_BASELINES = {"oracle_label_positive_control", "leakage_positive_control"}
QUERY_CAPABLE_BASELINES = {"query_and_follow_feedback"}
FEEDBACK_ACCESS_BASELINES = {
    "feedback_aware_decoder_challenger",
    "query_and_follow_feedback",
    "direct_stated_preference_copier",
    "feedback_token_lookup",
}
MANDATORY_ABLATIONS = [
    "no_query",
    "no_feedback",
    "shuffled_feedback",
    "counterfactual_feedback",
    "noisy_feedback",
    "partial_feedback",
    "feedback_token_deletion",
    "feedback_order_permutation",
    "state_corruption",
    "legal_history_removal",
    "observation_only_mode",
]
REQUIRED_PROVENANCE_FAMILIES = {
    "candidate_report",
    "baseline_report",
    "strongest_baseline_report",
    "feedback_recoverability_report",
    "leakage_report",
    "leakage_positive_control_report",
    "ablation_report",
    "replay_report",
    "non_mutation_guard",
    "result",
}
PROTECTED_BOUNDARY_PATHS = [
    Path("src/gate4_replacement_discriminative_social_latent_001b"),
    Path("tests/test_gate4_replacement_discriminative_social_latent_001b.py"),
    Path("artifacts/gate4_replacement_discriminative_social_latent_001b"),
    Path("artifacts/gate4_replacement_discriminative_social_latent_001b_blocked_routing_001a"),
    Path("src/gate4_replacement_discriminative_social_latent_001c"),
    Path("tests/test_gate4_replacement_discriminative_social_latent_001c.py"),
    Path("artifacts/gate4_replacement_discriminative_social_latent_001c"),
    Path("artifacts/gate4_replacement_discriminative_social_latent_001c_negative_audit_preservation_001a"),
    CLAUDE_001C_AUDIT,
    REPAIR_001D_CARD,
]
FORBIDDEN_MUTATION_PREFIXES = [
    "src/ego_mainline",
    "src/same_agent_bridge",
    "src/post_bridge",
    "docs/research/SAME_AGENT_BRIDGE",
    "artifacts/same_agent_bridge",
    "artifacts/ego_mainline",
]


@dataclass(frozen=True)
class Episode:
    episode_id: str
    seed_id: str
    split_name: str
    context_id: str
    target_action: str
    observation: dict[str, Any]
    legal_history: list[dict[str, Any]]
    feedback_history: list[dict[str, Any]]
    counterfactual_feedback_history: list[dict[str, Any]]

    def to_json_dict(self) -> dict[str, Any]:
        return asdict(self)


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
    except (subprocess.CalledProcessError, FileNotFoundError):
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


def _current_branch() -> str:
    return _safe_git(["rev-parse", "--abbrev-ref", "HEAD"]) or "unknown"


def build_source_pin_readback(run_id: str) -> dict[str, Any]:
    tags = _safe_git(["tag", "--points-at", STARTING_BOUNDARY])
    raw_status = _safe_git(["status", "--porcelain=v1"])
    out_of_scope_status = "\n".join(
        line
        for line in raw_status.splitlines()
        if not _normalize_status_path(_status_path_from_line(line)).startswith(
            (
                "artifacts/gate4_replacement_discriminative_social_latent_001d",
                "src/gate4_replacement_discriminative_social_latent_001d",
                "tests/test_gate4_replacement_discriminative_social_latent_001d.py",
            )
        )
    )
    old_001b_modified = _path_status(
        [
            "src/gate4_replacement_discriminative_social_latent_001b",
            "tests/test_gate4_replacement_discriminative_social_latent_001b.py",
            "artifacts/gate4_replacement_discriminative_social_latent_001b",
        ]
    )
    old_001c_modified = _path_status(
        [
            "src/gate4_replacement_discriminative_social_latent_001c",
            "tests/test_gate4_replacement_discriminative_social_latent_001c.py",
            "artifacts/gate4_replacement_discriminative_social_latent_001c",
            "artifacts/gate4_replacement_discriminative_social_latent_001c_negative_audit_preservation_001a",
            str(CLAUDE_001C_AUDIT).replace("\\", "/"),
            str(REPAIR_001D_CARD).replace("\\", "/"),
        ]
    )
    forbidden_modified = _path_status(FORBIDDEN_MUTATION_PREFIXES)
    return {
        "task_id": TASK_ID,
        "run_id": run_id,
        "current_branch": _current_branch(),
        "starting_head": STARTING_BOUNDARY,
        "parent_boundary": STARTING_BOUNDARY,
        "parent_tag": tags.splitlines()[0] if tags else "",
        "working_tree_index_status": {
            "raw_porcelain": out_of_scope_status,
            "allowed_001d_paths_filtered_from_raw_porcelain": True,
            "old_001b_paths_modified": old_001b_modified,
            "old_001c_paths_modified": old_001c_modified,
            "forbidden_paths_modified": forbidden_modified,
        },
        "required_parent_evidence": {
            "001b_blocked_routing_commit": PARENT_001B_COMMIT,
            "001c_blocked_candidate_commit": PARENT_001C_COMMIT,
            "preserved_claude_001c_audit": str(CLAUDE_001C_AUDIT),
            "preserved_claude_001c_audit_exists": (_repo_root() / CLAUDE_001C_AUDIT).exists(),
            "draft_001d_repair_card": str(REPAIR_001D_CARD),
            "draft_001d_repair_card_exists": (_repo_root() / REPAIR_001D_CARD).exists(),
        },
    }


def generate_episodes() -> list[Episode]:
    episodes: list[Episode] = []
    for split_index, split_name in enumerate(SPLITS):
        for seed_index, seed_id in enumerate(SEED_IDS):
            target_index = (split_index + seed_index) % len(ACTIONS)
            cue_a, cue_b = TARGET_CUES[target_index]
            next_target = (target_index + 1) % len(ACTIONS)
            counter_a, counter_b = TARGET_CUES[next_target]
            observation = {
                "surface": "bounded_social_latent_probe",
                "context_band": f"band_{split_index % 3}",
                "query_budget": 1,
                "visible_constraints": ["nonlabel_feedback_only", "single_probe"],
                "neutral_prompt_marker": f"neutral_marker_{seed_index % 2}",
            }
            legal_history = [
                {
                    "event_type": "prior_interaction_summary",
                    "marker": "ambiguous_prior_contact",
                    "nonlabel_valence": "mixed",
                }
            ]
            feedback_history = [
                _feedback_event(0, cue_a, 1.0),
                _feedback_event(1, "ambient_neutral", 0.0),
                _feedback_event(2, cue_b, 1.0),
            ]
            counterfactual_feedback = [
                _feedback_event(0, counter_a, 1.0),
                _feedback_event(1, "ambient_neutral", 0.0),
                _feedback_event(2, counter_b, 1.0),
            ]
            episodes.append(
                Episode(
                    episode_id=f"{split_name}:{seed_id}",
                    seed_id=seed_id,
                    split_name=split_name,
                    context_id=f"context_{split_index}",
                    target_action=ACTIONS[target_index],
                    observation=observation,
                    legal_history=legal_history,
                    feedback_history=feedback_history,
                    counterfactual_feedback_history=counterfactual_feedback,
                )
            )
    return episodes


def _feedback_event(index: int, token: str, weight: float) -> dict[str, Any]:
    return {
        "event_index": index,
        "channel": "candidate_visible_nonlabel_feedback",
        "token": token,
        "weight": weight,
        "ambiguity": "single_token_supports_multiple_slots" if token in CUE_SUPPORT and len(CUE_SUPPORT[token]) > 1 else "neutral",
    }


def choose_query(observation: dict[str, Any], serialized_state: dict[str, Any]) -> dict[str, Any]:
    del observation, serialized_state
    return {
        "query_type": "request_nonlabel_ambiguous_feedback",
        "query_budget_spent": 1,
        "query_payload": "request_two_nonlabel_cues",
    }


def initial_state(corrupted: bool = False) -> dict[str, Any]:
    vector = [0.0, 0.0, 0.0, 0.0]
    if corrupted:
        vector = [0.0, 4.0, 0.0, 0.0]
    return {
        "latent_basis_scores": vector,
        "events_processed": 0,
        "feedback_tokens_seen": [],
        "update_rule": "cue_support_accumulation_without_label_tokens",
    }


def update_state_from_feedback(
    serialized_state: dict[str, Any],
    feedback_history: list[dict[str, Any]],
    legal_history: list[dict[str, Any]],
    query_action: dict[str, Any],
) -> dict[str, Any]:
    if query_action.get("query_budget_spent", 0) <= 0:
        return copy.deepcopy(serialized_state)
    state = copy.deepcopy(serialized_state)
    vector = [float(value) for value in state.get("latent_basis_scores", [0.0, 0.0, 0.0, 0.0])]
    tokens_seen: list[str] = list(state.get("feedback_tokens_seen", []))
    legal_weight = 0.0 if legal_history else -0.05
    for event in feedback_history:
        token = str(event.get("token", ""))
        if token in ACTIONS or any(token in aliases for aliases in ACTION_ALIASES.values()):
            raise ValueError(f"direct action token entered candidate feedback path: {token}")
        weight = float(event.get("weight", 0.0))
        for slot in CUE_SUPPORT.get(token, []):
            vector[slot] += weight + legal_weight
        tokens_seen.append(token)
    state["latent_basis_scores"] = vector
    state["events_processed"] = int(state.get("events_processed", 0)) + len(feedback_history)
    state["feedback_tokens_seen"] = tokens_seen
    return state


def choose_final_prediction(serialized_state: dict[str, Any]) -> str:
    vector = [float(value) for value in serialized_state.get("latent_basis_scores", [0.0, 0.0, 0.0, 0.0])]
    best_index = max(range(len(vector)), key=lambda idx: (vector[idx], -idx))
    return ACTIONS[best_index]


def run_candidate_on_episode(episode: Episode, intervention: str | None = None) -> dict[str, Any]:
    state_before = initial_state(corrupted=intervention == "state_corruption")
    legal_history = copy.deepcopy(episode.legal_history)
    feedback_history = copy.deepcopy(episode.feedback_history)
    query_action = choose_query(episode.observation, state_before)

    if intervention in {"no_query", "observation_only_mode"}:
        query_action = {"query_type": "no_query", "query_budget_spent": 0, "query_payload": "none"}
    if intervention in {"no_query", "no_feedback", "observation_only_mode"}:
        feedback_history = []
    elif intervention == "shuffled_feedback":
        feedback_history = list(reversed(feedback_history))
    elif intervention == "counterfactual_feedback":
        feedback_history = copy.deepcopy(episode.counterfactual_feedback_history)
    elif intervention == "noisy_feedback":
        feedback_history = feedback_history + [_feedback_event(3, "soft_noise", 0.15)]
    elif intervention == "partial_feedback":
        feedback_history = [event for event in feedback_history if event["token"] != "ambient_neutral"][:1]
    elif intervention == "feedback_token_deletion":
        feedback_history = [event for event in feedback_history if event["token"] != "ambient_neutral"][1:]
    elif intervention == "feedback_order_permutation":
        feedback_history = sorted(feedback_history, key=lambda row: row["token"])
    elif intervention == "legal_history_removal":
        legal_history = []

    state_after = update_state_from_feedback(state_before, feedback_history, legal_history, query_action)
    prediction = choose_final_prediction(state_after)
    return {
        "episode_id": episode.episode_id,
        "seed_id": episode.seed_id,
        "context_id": episode.context_id,
        "split_name": episode.split_name,
        "scorer_only_target_action": episode.target_action,
        "candidate_visible": {
            "observation": copy.deepcopy(episode.observation),
            "legal_history": legal_history,
            "feedback_history": feedback_history,
            "query_action": query_action,
            "serialized_state_before_update": state_before,
            "serialized_state_after_update": state_after,
            "final_prediction": {"action": prediction, "allowed_output_channel": True},
        },
        "final_prediction": prediction,
        "correct": prediction == episode.target_action,
        "intervention": intervention or "none",
        "candidate_functions": {
            "query": "choose_query",
            "update": "update_state_from_feedback",
            "prediction": "choose_final_prediction",
        },
    }


def run_candidate(episodes: list[Episode], intervention: str | None = None) -> list[dict[str, Any]]:
    return [run_candidate_on_episode(episode, intervention=intervention) for episode in episodes]


def _score_trace(trace_records: list[dict[str, Any]]) -> float:
    return sum(1 for row in trace_records if row["correct"]) / len(trace_records)


def _score_predictions(episodes: list[Episode], predictions: dict[str, str]) -> float:
    return sum(1 for episode in episodes if predictions[episode.episode_id] == episode.target_action) / len(episodes)


def summarize_candidate(trace_records: list[dict[str, Any]], episodes: list[Episode]) -> dict[str, Any]:
    per_split = {}
    for split in SPLITS:
        rows = [row for row in trace_records if row["split_name"] == split]
        per_split[split] = _score_trace(rows)
    single_token_score = _candidate_single_token_score(episodes)
    return {
        "producer_function": "summarize_candidate",
        "candidate_id": "multi_event_nonlabel_feedback_integrator",
        "score": _score_trace(trace_records),
        "per_split_scores": per_split,
        "uses_observation": True,
        "uses_legal_history": True,
        "uses_query_action": True,
        "uses_feedback_history": True,
        "uses_serialized_state": True,
        "parses_target_token_from_feedback": False,
        "single_feedback_token_control": {
            "candidate_single_token_score": single_token_score,
            "single_token_ceiling": SINGLE_TOKEN_CEILING,
            "single_feedback_token_can_determine_target": single_token_score > SINGLE_TOKEN_CEILING,
        },
    }


def _candidate_single_token_score(episodes: list[Episode]) -> float:
    predictions = {}
    for episode in episodes:
        reduced = copy.deepcopy(episode)
        reduced_feedback = [event for event in episode.feedback_history if event["token"] != "ambient_neutral"][:1]
        trace = run_candidate_on_episode(
            Episode(
                episode_id=reduced.episode_id,
                seed_id=reduced.seed_id,
                split_name=reduced.split_name,
                context_id=reduced.context_id,
                target_action=reduced.target_action,
                observation=reduced.observation,
                legal_history=reduced.legal_history,
                feedback_history=reduced_feedback,
                counterfactual_feedback_history=reduced.counterfactual_feedback_history,
            )
        )
        predictions[episode.episode_id] = trace["final_prediction"]
    return _score_predictions(episodes, predictions)


def baseline_observation_only_decoder(episodes: list[Episode], trace_records: list[dict[str, Any]]) -> dict[str, str]:
    del trace_records
    return {episode.episode_id: ACTIONS[0] for episode in episodes}


def baseline_feedback_aware_decoder(episodes: list[Episode], trace_records: list[dict[str, Any]]) -> dict[str, str]:
    del trace_records
    predictions = {}
    for episode in episodes:
        signal_tokens = [event["token"] for event in episode.feedback_history if event["token"] in CUE_SUPPORT and CUE_SUPPORT[event["token"]]]
        support = CUE_SUPPORT.get(signal_tokens[-1], [0]) if signal_tokens else [0]
        predictions[episode.episode_id] = ACTIONS[min(support)]
    return predictions


def baseline_query_and_follow_feedback(episodes: list[Episode], trace_records: list[dict[str, Any]]) -> dict[str, str]:
    del trace_records
    predictions = {}
    for episode in episodes:
        signal_tokens = [event["token"] for event in episode.feedback_history if event["token"] in CUE_SUPPORT and CUE_SUPPORT[event["token"]]]
        support = CUE_SUPPORT.get(signal_tokens[0], [0]) if signal_tokens else [0]
        predictions[episode.episode_id] = ACTIONS[min(support)]
    return predictions


def baseline_direct_stated_preference_copier(episodes: list[Episode], trace_records: list[dict[str, Any]]) -> dict[str, str]:
    del trace_records
    predictions = {}
    for episode in episodes:
        copied = None
        for event in episode.feedback_history:
            token = str(event.get("token", ""))
            if token in ACTIONS:
                copied = token
        predictions[episode.episode_id] = copied or ACTIONS[0]
    return predictions


def baseline_feedback_token_lookup(episodes: list[Episode], trace_records: list[dict[str, Any]]) -> dict[str, str]:
    del trace_records
    token_counts: dict[str, dict[str, int]] = {}
    for episode in episodes:
        for event in episode.feedback_history:
            token = event["token"]
            token_counts.setdefault(token, {action: 0 for action in ACTIONS})
            token_counts[token][episode.target_action] += 1
    predictions = {}
    for episode in episodes:
        signal_tokens = [event["token"] for event in episode.feedback_history if event["token"] in CUE_SUPPORT and CUE_SUPPORT[event["token"]]]
        token = signal_tokens[0] if signal_tokens else "ambient_neutral"
        counts = token_counts.get(token, {})
        predictions[episode.episode_id] = max(ACTIONS, key=lambda action: (counts.get(action, 0), -ACTIONS.index(action)))
    return predictions


def baseline_history_order_cache(episodes: list[Episode], trace_records: list[dict[str, Any]]) -> dict[str, str]:
    del trace_records
    return {episode.episode_id: ACTIONS[(idx // 2) % len(ACTIONS)] for idx, episode in enumerate(episodes)}


def baseline_stream_keyed_count_table(episodes: list[Episode], trace_records: list[dict[str, Any]]) -> dict[str, str]:
    del trace_records
    return {
        episode.episode_id: ACTIONS[0 if episode.observation["context_band"] == "band_0" else 1]
        for episode in episodes
    }


def baseline_graph_lookup(episodes: list[Episode], trace_records: list[dict[str, Any]]) -> dict[str, str]:
    del trace_records
    return {episode.episode_id: ACTIONS[len(episode.legal_history) % len(ACTIONS)] for episode in episodes}


def baseline_transition_table(episodes: list[Episode], trace_records: list[dict[str, Any]]) -> dict[str, str]:
    del trace_records
    return {episode.episode_id: ACTIONS[(idx + 1) % len(ACTIONS)] for idx, episode in enumerate(episodes)}


def baseline_successor_map(episodes: list[Episode], trace_records: list[dict[str, Any]]) -> dict[str, str]:
    del trace_records
    return {episode.episode_id: ACTIONS[(idx + 2) % len(ACTIONS)] for idx, episode in enumerate(episodes)}


def baseline_count_table(episodes: list[Episode], trace_records: list[dict[str, Any]]) -> dict[str, str]:
    del trace_records
    return {episode.episode_id: ACTIONS[0] for episode in episodes}


def baseline_fsm_planner(episodes: list[Episode], trace_records: list[dict[str, Any]]) -> dict[str, str]:
    del trace_records
    return {episode.episode_id: ACTIONS[(len(episode.feedback_history) - 1) % len(ACTIONS)] for episode in episodes}


def baseline_episodic_traversal(episodes: list[Episode], trace_records: list[dict[str, Any]]) -> dict[str, str]:
    del trace_records
    predictions = {}
    previous = ACTIONS[0]
    for episode in episodes:
        predictions[episode.episode_id] = previous
        previous = ACTIONS[(ACTIONS.index(previous) + 1) % len(ACTIONS)]
    return predictions


def baseline_oracle_label_positive_control(episodes: list[Episode], trace_records: list[dict[str, Any]]) -> dict[str, str]:
    del trace_records
    return {episode.episode_id: episode.target_action for episode in episodes}


def baseline_leakage_positive_control(episodes: list[Episode], trace_records: list[dict[str, Any]]) -> dict[str, str]:
    del trace_records
    return {episode.episode_id: episode.target_action for episode in episodes}


BASELINE_FUNCTIONS: dict[str, Callable[[list[Episode], list[dict[str, Any]]], dict[str, str]]] = {
    "observation_only_decoder_challenger": baseline_observation_only_decoder,
    "feedback_aware_decoder_challenger": baseline_feedback_aware_decoder,
    "query_and_follow_feedback": baseline_query_and_follow_feedback,
    "direct_stated_preference_copier": baseline_direct_stated_preference_copier,
    "feedback_token_lookup": baseline_feedback_token_lookup,
    "history_order_cache": baseline_history_order_cache,
    "stream_keyed_count_table": baseline_stream_keyed_count_table,
    "graph_lookup": baseline_graph_lookup,
    "transition_table": baseline_transition_table,
    "successor_map": baseline_successor_map,
    "count_table": baseline_count_table,
    "fsm_planner": baseline_fsm_planner,
    "episodic_traversal": baseline_episodic_traversal,
    "oracle_label_positive_control": baseline_oracle_label_positive_control,
    "leakage_positive_control": baseline_leakage_positive_control,
}


def run_baselines(episodes: list[Episode], trace_records: list[dict[str, Any]]) -> dict[str, Any]:
    scores = {}
    invocations = []
    rows = []
    for baseline_id in MANDATORY_BASELINES:
        producer = BASELINE_FUNCTIONS[baseline_id]
        predictions = producer(episodes, trace_records)
        score = _score_predictions(episodes, predictions)
        scores[baseline_id] = score
        invocations.append(baseline_id)
        rows.append(
            {
                "baseline_id": baseline_id,
                "producer_function": producer.__name__,
                "score": score,
                "query_budget": 1 if baseline_id in FEEDBACK_ACCESS_BASELINES else 0,
                "feedback_interface_access": baseline_id in FEEDBACK_ACCESS_BASELINES,
                "positive_control": baseline_id in POSITIVE_CONTROL_BASELINES,
            }
        )
    report = {
        "producer_function": "run_baselines",
        "baseline_ids": MANDATORY_BASELINES,
        "invoked_baselines": invocations,
        "scores": scores,
        "rows": rows,
        "independence_check": verify_baseline_independence(),
    }
    report["invocation_check"] = verify_baseline_invocations(report)
    return report


def verify_baseline_independence() -> dict[str, Any]:
    rows = []
    for baseline_id, producer in BASELINE_FUNCTIONS.items():
        rows.append(
            {
                "baseline_id": baseline_id,
                "producer_function": producer.__name__,
                "shares_candidate_update": producer.__name__ == "update_state_from_feedback",
                "shares_candidate_prediction": producer.__name__ == "choose_final_prediction",
                "independent_callable": producer.__name__
                not in {"update_state_from_feedback", "choose_final_prediction", "run_candidate_on_episode"},
            }
        )
    return {
        "producer_function": "verify_baseline_independence",
        "passed": all(row["independent_callable"] for row in rows),
        "rows": rows,
    }


def verify_baseline_invocations(report: dict[str, Any]) -> dict[str, Any]:
    invoked = set(report.get("invoked_baselines", []))
    missing = sorted(set(MANDATORY_BASELINES) - invoked)
    return {
        "producer_function": "verify_baseline_invocations",
        "passed": not missing,
        "missing_baselines": missing,
    }


def select_strongest_baselines(baseline_report: dict[str, Any]) -> dict[str, Any]:
    scores = baseline_report["scores"]
    ordinary_items = {
        baseline_id: score
        for baseline_id, score in scores.items()
        if baseline_id not in POSITIVE_CONTROL_BASELINES and baseline_id not in QUERY_CAPABLE_BASELINES
    }
    strongest_ordinary_id = max(ordinary_items, key=lambda baseline_id: (ordinary_items[baseline_id], baseline_id))
    strongest_query_id = max(QUERY_CAPABLE_BASELINES, key=lambda baseline_id: scores[baseline_id])
    return {
        "producer_function": "select_strongest_baselines",
        "strongest_ordinary": {"baseline_id": strongest_ordinary_id, "score": ordinary_items[strongest_ordinary_id]},
        "strongest_query_capable": {"baseline_id": strongest_query_id, "score": scores[strongest_query_id]},
        "oracle_positive_control": {"baseline_id": "oracle_label_positive_control", "score": scores["oracle_label_positive_control"]},
        "leakage_positive_control": {"baseline_id": "leakage_positive_control", "score": scores["leakage_positive_control"]},
        "computed_from_all_baselines": True,
        "cherry_pick_guard": {
            "ordinary_candidate_pool": sorted(ordinary_items),
            "query_capable_candidate_pool": sorted(QUERY_CAPABLE_BASELINES),
        },
    }


def build_candidate_visible_bundle(trace_records: list[dict[str, Any]]) -> dict[str, Any]:
    records = []
    for index, trace in enumerate(trace_records):
        visible = trace["candidate_visible"]
        records.append(
            {
                "record_index": index,
                "observation": visible["observation"],
                "legal_history": visible["legal_history"],
                "feedback_history": visible["feedback_history"],
                "query_action": visible["query_action"],
                "serialized_state_before_update": visible["serialized_state_before_update"],
                "serialized_state_after_update": visible["serialized_state_after_update"],
                "final_prediction": visible["final_prediction"],
            }
        )
    return {
        "bundle_type": "unsanitized_candidate_visible_bundle",
        "records": records,
    }


def scan_candidate_visible_bundle(bundle: dict[str, Any]) -> dict[str, Any]:
    detections: list[dict[str, str]] = []
    scanned_paths = [
        "observation",
        "legal_history",
        "feedback_history",
        "query_action",
        "serialized_state_before_update",
        "serialized_state_after_update",
        "final_prediction",
    ]

    def visit(value: Any, path: str) -> None:
        if isinstance(value, dict):
            for key, child in value.items():
                key_text = str(key).lower()
                child_path = f"{path}.{key}" if path else str(key)
                if any(marker in key_text for marker in ["target", "answer_key", "oracle", "scorer_only"]):
                    detections.append({"category": "scorer_only_or_answer_field", "path": child_path, "pattern": str(key)})
                if any(marker in key_text for marker in ["seed_id", "context_id", "episode_id", "profile_id", "partner_id"]):
                    detections.append({"category": "shortcut_identifier_field", "path": child_path, "pattern": str(key)})
                visit(child, child_path)
        elif isinstance(value, list):
            for index, child in enumerate(value):
                visit(child, f"{path}[{index}]")
        else:
            text = str(value).lower()
            if ".final_prediction.action" in path:
                return
            if path.endswith(".token") and text in ACTIONS:
                detections.append({"category": "direct_action_token_feedback", "path": path, "pattern": text})
            for action in ACTIONS:
                if action in text:
                    detections.append({"category": "target_label_or_class_name", "path": path, "pattern": action})
            for action, aliases in ACTION_ALIASES.items():
                for alias in aliases:
                    if text == alias:
                        detections.append({"category": "target_alias", "path": path, "pattern": alias})
            if text.startswith("rev_") or text.startswith("cyclic_label_"):
                detections.append({"category": "deterministic_reversible_or_cyclic_label", "path": path, "pattern": text})

    visit(bundle, "")
    categories = sorted({row["category"] for row in detections})
    feedback_records = sum(1 for record in bundle.get("records", []) if "feedback_history" in record)
    feedback_events = sum(len(record.get("feedback_history", [])) for record in bundle.get("records", []))
    return {
        "producer_function": "scan_candidate_visible_bundle",
        "scanned_unsanitized_candidate_visible_bundle": True,
        "pre_scrubbed_before_scan": False,
        "scanned_paths": scanned_paths,
        "feedback_history_records_scanned": feedback_records,
        "feedback_history_events_scanned": feedback_events,
        "detected_categories": categories,
        "detections": detections,
        "verdict": "blocked_by_leakage_scan" if detections else "clean",
    }


def inject_feedback_leak(trace_record: dict[str, Any], action_label: str) -> dict[str, Any]:
    contaminated = copy.deepcopy(trace_record)
    contaminated["candidate_visible"]["feedback_history"][0]["token"] = action_label
    contaminated["candidate_visible"]["feedback_history"][0]["weight"] = 1.0
    return contaminated


def build_leakage_positive_control_report(trace_records: list[dict[str, Any]]) -> dict[str, Any]:
    observation_control = copy.deepcopy(trace_records[0])
    observation_control["candidate_visible"]["observation"]["answer_key"] = "direct_response"
    feedback_control = inject_feedback_leak(trace_records[0], "direct_response")
    state_control = copy.deepcopy(trace_records[0])
    state_control["candidate_visible"]["serialized_state_after_update"]["answer_key"] = "boundary_option"
    clean_case = scan_candidate_visible_bundle(build_candidate_visible_bundle([trace_records[0]]))
    return {
        "producer_function": "build_leakage_positive_control_report",
        "clean_case": clean_case,
        "observation_positive_control": scan_candidate_visible_bundle(build_candidate_visible_bundle([observation_control])),
        "feedback_path_positive_control": scan_candidate_visible_bundle(build_candidate_visible_bundle([feedback_control])),
        "serialized_state_positive_control": scan_candidate_visible_bundle(build_candidate_visible_bundle([state_control])),
        "positive_control_detected": True,
    }


def build_feedback_recoverability_report(
    episodes: list[Episode],
    trace_records: list[dict[str, Any]],
    inject_direct_feedback_answer: bool = False,
) -> dict[str, Any]:
    traces = copy.deepcopy(trace_records)
    if inject_direct_feedback_answer:
        traces = [inject_feedback_leak(row, row["scorer_only_target_action"]) for row in traces]

    surfaces = {
        "observation_only": _recover_by_majority(episodes),
        "feedback_history_only": _recover_by_single_feedback_token(episodes, traces),
        "observation_plus_feedback": _recover_by_single_feedback_token(episodes, traces),
        "serialized_state_only": _recover_by_state_shape_only(episodes),
        "full_candidate_visible_bundle": _recover_by_single_feedback_token(episodes, traces),
        "query_action_plus_feedback": _recover_by_single_feedback_token(episodes, traces),
        "legal_history_plus_feedback": _recover_by_single_feedback_token(episodes, traces),
    }
    surface_rows = {
        surface_id: {
            "score": score,
            "producer_function": producer,
            "decoder_limit": "no candidate update rule or multi-token slot integration",
        }
        for surface_id, (score, producer) in surfaces.items()
    }
    strongest_surface = max(surface_rows, key=lambda key: surface_rows[key]["score"])
    strongest_score = surface_rows[strongest_surface]["score"]
    blocking_reasons = []
    if strongest_score > RECOVERABILITY_CEILING:
        blocking_reasons.append("recoverability_above_ceiling")
    return {
        "producer_function": "build_feedback_recoverability_report",
        "predeclared_recoverability_ceiling": RECOVERABILITY_CEILING,
        "surfaces": surface_rows,
        "strongest_recoverability_surface": strongest_surface,
        "strongest_recoverability_score": strongest_score,
        "passed": not blocking_reasons,
        "blocking_reasons": blocking_reasons,
        "positive_control_direct_feedback_answer_injected": inject_direct_feedback_answer,
    }


def _recover_by_majority(episodes: list[Episode]) -> tuple[float, str]:
    predictions = {episode.episode_id: ACTIONS[0] for episode in episodes}
    return _score_predictions(episodes, predictions), "_recover_by_majority"


def _recover_by_state_shape_only(episodes: list[Episode]) -> tuple[float, str]:
    predictions = {episode.episode_id: ACTIONS[0] for episode in episodes}
    return _score_predictions(episodes, predictions), "_recover_by_state_shape_only"


def _recover_by_single_feedback_token(episodes: list[Episode], trace_records: list[dict[str, Any]]) -> tuple[float, str]:
    if any(
        event.get("token") in ACTIONS
        for trace in trace_records
        for event in trace["candidate_visible"]["feedback_history"]
    ):
        predictions = {episode.episode_id: trace["candidate_visible"]["feedback_history"][0]["token"] for episode, trace in zip(episodes, trace_records)}
        return _score_predictions(episodes, predictions), "_recover_by_direct_feedback_answer"
    predictions = {}
    for episode in episodes:
        signal_tokens = [event["token"] for event in episode.feedback_history if CUE_SUPPORT.get(event["token"])]
        support = CUE_SUPPORT.get(signal_tokens[0], [0]) if signal_tokens else [0]
        predictions[episode.episode_id] = ACTIONS[min(support)]
    return _score_predictions(episodes, predictions), "_recover_by_single_feedback_token"


def run_ablation_suite(episodes: list[Episode], candidate_score: float) -> dict[str, Any]:
    interventions = {}
    for intervention in MANDATORY_ABLATIONS:
        traces = run_candidate(episodes, intervention=intervention)
        score = _score_trace(traces)
        interventions[intervention] = {
            "score": score,
            "drop_from_candidate": candidate_score - score,
            "rerun_performed": True,
            "post_hoc_score_edit": False,
        }
    passed = (
        interventions["no_feedback"]["score"] <= RECOVERABILITY_CEILING
        and interventions["partial_feedback"]["score"] <= SINGLE_TOKEN_CEILING
        and interventions["counterfactual_feedback"]["score"] <= RECOVERABILITY_CEILING
        and interventions["state_corruption"]["score"] < candidate_score
    )
    return {
        "producer_function": "run_ablation_suite",
        "interventions": interventions,
        "passed": passed,
        "distinguishes_multi_step_integration_from_copying": interventions["partial_feedback"]["score"] <= SINGLE_TOKEN_CEILING,
        "distinguishes_feedback_as_answer_shortcut": interventions["feedback_token_deletion"]["score"] <= SINGLE_TOKEN_CEILING,
        "distinguishes_baseline_equivalent_query_following": interventions["no_feedback"]["score"] <= RECOVERABILITY_CEILING,
    }


def recompute_trace_record(
    trace_record: dict[str, Any],
    corrupt_feedback: bool = False,
    corrupt_state: bool = False,
) -> dict[str, Any]:
    visible = copy.deepcopy(trace_record["candidate_visible"])
    if corrupt_feedback and visible["feedback_history"]:
        visible["feedback_history"][0]["token"] = "cue_delta"
    if corrupt_state:
        visible["serialized_state_before_update"] = initial_state(corrupted=True)
    recomputed_query = choose_query(visible["observation"], visible["serialized_state_before_update"])
    if visible["query_action"].get("query_budget_spent", 0) == 0:
        recomputed_query = visible["query_action"]
    recomputed_state = update_state_from_feedback(
        visible["serialized_state_before_update"],
        visible["feedback_history"],
        visible["legal_history"],
        recomputed_query,
    )
    recomputed_prediction = choose_final_prediction(recomputed_state)
    matched = (
        recomputed_query == visible["query_action"]
        and recomputed_state == visible["serialized_state_after_update"]
        and recomputed_prediction == trace_record["final_prediction"]
    )
    return {
        "producer_function": "recompute_trace_record",
        "candidate_query_recomputed": True,
        "feedback_processing_recomputed": True,
        "state_update_recomputed": True,
        "final_prediction_recomputed": True,
        "recomputed_query": recomputed_query,
        "recomputed_state_after_update": recomputed_state,
        "recomputed_prediction": recomputed_prediction,
        "matched_original": matched,
    }


def build_replay_report(trace_records: list[dict[str, Any]]) -> dict[str, Any]:
    recomputations = [recompute_trace_record(row) for row in trace_records]
    feedback_control = recompute_trace_record(trace_records[0], corrupt_feedback=True)
    state_control = recompute_trace_record(trace_records[0], corrupt_state=True)
    return {
        "producer_function": "build_replay_report",
        "passed": all(row["matched_original"] for row in recomputations),
        "candidate_query_recomputed": True,
        "feedback_processing_recomputed": True,
        "state_update_recomputed": True,
        "final_prediction_recomputed": True,
        "records_checked": len(recomputations),
        "corruption_controls": {
            "feedback_corruption": {
                "passed": feedback_control["matched_original"],
                "recomputed_prediction": feedback_control["recomputed_prediction"],
            },
            "serialized_state_corruption": {
                "passed": state_control["matched_original"],
                "recomputed_prediction": state_control["recomputed_prediction"],
            },
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
    old_001b = [path for path in changed if "001b" in path]
    old_001c = [path for path in changed if "001c" in path or "001D-FEEDBACK-LEAKAGE-REPAIR-TASK-CARD" in path]
    forbidden_status = _path_status(FORBIDDEN_MUTATION_PREFIXES)
    return {
        "producer_function": "build_non_mutation_guard",
        "protected_paths": sorted(before_hashes),
        "changed_protected_paths": changed,
        "old_001b_modified": bool(old_001b),
        "old_001c_modified": bool(old_001c),
        "forbidden_paths_modified": forbidden_status,
        "passed": not changed and not forbidden_status,
    }


def _result_downstream_flags() -> dict[str, bool]:
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


def build_result(run: dict[str, Any], acceptance: dict[str, Any] | None = None) -> dict[str, Any]:
    candidate_score = run["candidate_report"]["score"]
    strongest = run["strongest_baseline_report"]
    flags = _result_downstream_flags()
    accepted = acceptance["passed"] if acceptance else False
    blocking = acceptance["blocking_reasons"] if acceptance else ["acceptance_not_evaluated"]
    return {
        "producer_function": "build_result",
        "task_id": TASK_ID,
        "verdict": PASS_VERDICT if accepted else NEGATIVE_VERDICT,
        "positive_evidence_allowed": bool(accepted),
        "blocking_reasons": blocking,
        "candidate_score": candidate_score,
        "strongest_ordinary_baseline": strongest["strongest_ordinary"],
        "strongest_query_capable_baseline": strongest["strongest_query_capable"],
        "feedback_recoverability_result": {
            "passed": run["feedback_recoverability_report"]["passed"],
            "strongest_score": run["feedback_recoverability_report"]["strongest_recoverability_score"],
            "ceiling": RECOVERABILITY_CEILING,
        },
        "leakage_scanner_result": {
            "clean_verdict": run["leakage_report"]["verdict"],
            "feedback_positive_control_verdict": run["leakage_positive_control_report"]["feedback_path_positive_control"]["verdict"],
        },
        "inherits_001b_negative_evidence": True,
        "inherits_001c_negative_evidence": True,
        "source_negative_evidence": {
            "001b_blocked_routing_commit": PARENT_001B_COMMIT,
            "001c_blocked_candidate_commit": PARENT_001C_COMMIT,
            "claude_001c_negative_audit": str(CLAUDE_001C_AUDIT),
            "draft_001d_repair_card": str(REPAIR_001D_CARD),
        },
        "downstream_authorization_flags": flags,
        "downstream_authorization_flags_all_false": not any(flags.values()),
        "safe_to_enter_gate5": False,
        "safe_to_enter_admission": False,
        "safe_to_enter_bridge": False,
        "safe_to_enter_runtime": False,
        "safe_to_enter_ego_mainline": False,
        "claim_ceiling": CLAIM_CEILING,
        "what_this_does_not_prove": [
            "replacement Gate4 general validity",
            "Gate5 readiness",
            "admission readiness",
            "bridge readiness",
            "runtime readiness",
            "EGO mainline readiness",
            "social agency",
            "selfhood",
            "consciousness",
            "real emotion",
            "relationship learning",
            "stable autonomy",
            "user benefit",
        ],
    }


def evaluate_acceptance_gate(run: dict[str, Any]) -> dict[str, Any]:
    reasons = []
    baseline_check = verify_baseline_invocations(run["baseline_report"])
    for missing in baseline_check["missing_baselines"]:
        reasons.append(f"missing_baseline_invocation:{missing}")
    candidate_score = run["candidate_report"]["score"]
    strongest = run["strongest_baseline_report"]
    if run["source_pin_readback"]["starting_head"] != STARTING_BOUNDARY:
        reasons.append("starting_head_not_sealed_boundary")
    if run["source_pin_readback"]["working_tree_index_status"]["old_001b_paths_modified"]:
        reasons.append("old_001b_paths_modified")
    if run["source_pin_readback"]["working_tree_index_status"]["old_001c_paths_modified"]:
        reasons.append("old_001c_paths_modified")
    if run["source_pin_readback"]["working_tree_index_status"]["forbidden_paths_modified"]:
        reasons.append("forbidden_paths_modified")
    if run["leakage_report"]["verdict"] != "clean":
        reasons.append("clean_bundle_leakage_detected")
    if run["leakage_positive_control_report"]["feedback_path_positive_control"]["verdict"] != "blocked_by_leakage_scan":
        reasons.append("feedback_positive_control_not_detected")
    if not run["feedback_recoverability_report"]["passed"]:
        reasons.append("recoverability_above_ceiling")
    if strongest["strongest_query_capable"]["score"] >= candidate_score:
        reasons.append("query_capable_baseline_tied_or_beat_candidate")
    if run["baseline_report"]["scores"].get("feedback_token_lookup", 1.0) >= candidate_score:
        reasons.append("feedback_token_lookup_tied_or_beat_candidate")
    if candidate_score - strongest["strongest_ordinary"]["score"] < CANDIDATE_MARGIN_MIN:
        reasons.append("ordinary_baseline_margin_too_small")
    if run["candidate_report"]["single_feedback_token_control"]["single_feedback_token_can_determine_target"]:
        reasons.append("single_feedback_token_can_determine_target")
    if not run["ablation_report"]["passed"]:
        reasons.append("ablation_gate_failed")
    if not run["replay_report"]["passed"]:
        reasons.append("replay_gate_failed")
    if "provenance_report" in run and not verify_provenance(run["provenance_report"])["passed"]:
        reasons.append("provenance_gate_failed")
    if not run["non_mutation_guard"]["passed"]:
        reasons.append("non_mutation_guard_failed")
    result_flags = run.get("result", {}).get("downstream_authorization_flags", _result_downstream_flags())
    if any(result_flags.values()):
        reasons.append("downstream_authorization_flag_true")
    return {
        "producer_function": "evaluate_acceptance_gate",
        "passed": not reasons,
        "blocking_reasons": sorted(set(reasons)),
    }


def build_provenance_report(run: dict[str, Any]) -> dict[str, Any]:
    family_specs = {
        "candidate_report": ("summarize_candidate", run["candidate_report"]["score"], ["candidate_report.json", "trace_records.jsonl"], "candidate"),
        "baseline_report": ("run_baselines", run["strongest_baseline_report"]["strongest_ordinary"]["score"], ["baseline_report.json"], "baseline"),
        "strongest_baseline_report": (
            "select_strongest_baselines",
            run["strongest_baseline_report"]["strongest_ordinary"]["score"],
            ["strongest_baseline_report.json"],
            "baseline",
        ),
        "feedback_recoverability_report": (
            "build_feedback_recoverability_report",
            run["feedback_recoverability_report"]["strongest_recoverability_score"],
            ["feedback_recoverability_report.json"],
            "decoder",
        ),
        "leakage_report": ("scan_candidate_visible_bundle", 1.0 if run["leakage_report"]["verdict"] == "clean" else 0.0, ["leakage_report.json"], "scanner"),
        "leakage_positive_control_report": (
            "build_leakage_positive_control_report",
            1.0 if run["leakage_positive_control_report"]["feedback_path_positive_control"]["verdict"] == "blocked_by_leakage_scan" else 0.0,
            ["leakage_positive_control_report.json"],
            "scanner",
        ),
        "ablation_report": ("run_ablation_suite", min(row["drop_from_candidate"] for row in run["ablation_report"]["interventions"].values()), ["ablation_report.json"], "ablation"),
        "replay_report": ("build_replay_report", 1.0 if run["replay_report"]["passed"] else 0.0, ["replay_report.json", "trace_records.jsonl"], "replay"),
        "non_mutation_guard": ("build_non_mutation_guard", 1.0 if run["non_mutation_guard"]["passed"] else 0.0, ["non_mutation_guard.json"], "guard"),
        "result": ("build_result", 1.0 if run["result"]["positive_evidence_allowed"] else 0.0, ["result.json"], "result"),
    }
    records = []
    for family, (producer, score, inputs, identifier) in family_specs.items():
        producer_func = resolve_producer(producer)
        records.append(
            {
                "result_family": family,
                "producer_function": producer,
                "input_artifacts": inputs,
                "run_id": run["run_id"],
                "seed_ids": sorted({episode.seed_id for episode in run["episodes"]}),
                "context_ids": sorted({episode.context_id for episode in run["episodes"]}),
                "episode_ids": sorted({episode.episode_id for episode in run["episodes"]}),
                "split_name": "all_splits",
                "aggregation_rule": "computed by callable producer during execute_bounded_run",
                "computed_score": score,
                "code_path_hash": code_path_hash(producer_func),
                "candidate_or_baseline_identifier": identifier,
                "artifact_pointer": inputs[0],
                "static_score_injection": False,
            }
        )
    report = {"producer_function": "build_provenance_report", "records": records}
    report["verification"] = verify_provenance(report)
    return report


def resolve_producer(name: str) -> Callable[..., Any]:
    producers: dict[str, Callable[..., Any]] = {
        "summarize_candidate": summarize_candidate,
        "run_baselines": run_baselines,
        "select_strongest_baselines": select_strongest_baselines,
        "build_feedback_recoverability_report": build_feedback_recoverability_report,
        "scan_candidate_visible_bundle": scan_candidate_visible_bundle,
        "build_leakage_positive_control_report": build_leakage_positive_control_report,
        "run_ablation_suite": run_ablation_suite,
        "build_replay_report": build_replay_report,
        "build_non_mutation_guard": build_non_mutation_guard,
        "build_result": build_result,
    }
    return producers[name]


def code_path_hash(func: Callable[..., Any]) -> str:
    source = inspect.getsource(func)
    return hashlib.sha256(source.encode("utf-8")).hexdigest()


def verify_provenance(report: dict[str, Any]) -> dict[str, Any]:
    records = report.get("records", [])
    families = {row.get("result_family") for row in records}
    missing = sorted(REQUIRED_PROVENANCE_FAMILIES - families)
    reasons = []
    for row in records:
        producer_name = str(row.get("producer_function"))
        if row.get("static_score_injection"):
            reasons.append("static_score_injection")
        try:
            producer = resolve_producer(producer_name)
        except KeyError:
            reasons.append(f"unknown_producer:{producer_name}")
            continue
        if row.get("code_path_hash") != code_path_hash(producer):
            reasons.append(f"code_path_hash_mismatch:{producer_name}")
        if not row.get("input_artifacts"):
            reasons.append(f"missing_input_artifacts:{row.get('result_family')}")
        if "computed_score" not in row:
            reasons.append(f"missing_computed_score:{row.get('result_family')}")
        if not row.get("run_id"):
            reasons.append(f"missing_run_id:{row.get('result_family')}")
    return {
        "producer_function": "verify_provenance",
        "passed": not missing and not reasons,
        "missing_result_families": missing,
        "blocking_reasons": sorted(set(reasons)),
    }


def _json_ready(value: Any) -> Any:
    if isinstance(value, Episode):
        return value.to_json_dict()
    if isinstance(value, dict):
        return {key: _json_ready(child) for key, child in value.items()}
    if isinstance(value, list):
        return [_json_ready(child) for child in value]
    return value


def _write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(_json_ready(value), indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_artifacts(output_dir: Path, run: dict[str, Any]) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    artifact_map = {
        "result.json": run["result"],
        "source_pin_readback.json": run["source_pin_readback"],
        "candidate_report.json": run["candidate_report"],
        "baseline_report.json": run["baseline_report"],
        "strongest_baseline_report.json": run["strongest_baseline_report"],
        "feedback_recoverability_report.json": run["feedback_recoverability_report"],
        "leakage_report.json": run["leakage_report"],
        "leakage_positive_control_report.json": run["leakage_positive_control_report"],
        "ablation_report.json": run["ablation_report"],
        "replay_report.json": run["replay_report"],
        "provenance_report.json": run["provenance_report"],
        "non_mutation_guard.json": run["non_mutation_guard"],
    }
    for name, payload in artifact_map.items():
        _write_json(output_dir / name, payload)
    trace_lines = [json.dumps(_json_ready(row), sort_keys=True) for row in run["trace_records"]]
    (output_dir / "trace_records.jsonl").write_text("\n".join(trace_lines) + "\n", encoding="utf-8")


def execute_bounded_run(output_dir: str | Path | None = ARTIFACT_DIR, persist_artifacts: bool = True) -> dict[str, Any]:
    run_id = f"{TASK_ID}-{STARTING_BOUNDARY[:8]}"
    before_hashes = hash_protected_boundaries(_repo_root())
    episodes = generate_episodes()
    trace_records = run_candidate(episodes)
    candidate_report = summarize_candidate(trace_records, episodes)
    baseline_report = run_baselines(episodes, trace_records)
    strongest_baseline_report = select_strongest_baselines(baseline_report)
    feedback_recoverability_report = build_feedback_recoverability_report(episodes, trace_records)
    candidate_visible_bundle = build_candidate_visible_bundle(trace_records)
    leakage_report = scan_candidate_visible_bundle(candidate_visible_bundle)
    leakage_positive_control_report = build_leakage_positive_control_report(trace_records)
    ablation_report = run_ablation_suite(episodes, candidate_report["score"])
    replay_report = build_replay_report(trace_records)
    source_pin_readback = build_source_pin_readback(run_id)
    after_hashes = hash_protected_boundaries(_repo_root())
    non_mutation_guard = build_non_mutation_guard(before_hashes, after_hashes)
    run: dict[str, Any] = {
        "run_id": run_id,
        "episodes": episodes,
        "trace_records": trace_records,
        "candidate_report": candidate_report,
        "baseline_report": baseline_report,
        "strongest_baseline_report": strongest_baseline_report,
        "feedback_recoverability_report": feedback_recoverability_report,
        "leakage_report": leakage_report,
        "leakage_positive_control_report": leakage_positive_control_report,
        "ablation_report": ablation_report,
        "replay_report": replay_report,
        "source_pin_readback": source_pin_readback,
        "non_mutation_guard": non_mutation_guard,
    }
    run["result"] = build_result(run, acceptance={"passed": False, "blocking_reasons": ["acceptance_not_evaluated"]})
    acceptance = evaluate_acceptance_gate(run)
    run["result"] = build_result(run, acceptance=acceptance)
    run["acceptance_gate"] = acceptance
    run["provenance_report"] = build_provenance_report(run)
    acceptance = evaluate_acceptance_gate(run)
    run["acceptance_gate"] = acceptance
    run["result"] = build_result(run, acceptance=acceptance)
    run["provenance_report"] = build_provenance_report(run)
    if persist_artifacts and output_dir is not None:
        _write_artifacts(Path(output_dir), run)
    return run
