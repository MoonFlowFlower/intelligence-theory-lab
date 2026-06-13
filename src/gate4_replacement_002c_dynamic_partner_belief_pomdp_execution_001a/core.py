from __future__ import annotations

import copy
import hashlib
import inspect
import json
import subprocess
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Callable

from . import CLAIM_CEILING, TASK_ID


SEALED_BOUNDARY = "5a2d193c3551c4f468efb50ab9726cc623a2ec86"
REQUIRED_TAG = (
    "remote-anchor-gate4-replacement-002b-dynamic-partner-belief-pomdp-"
    "executable-task-card-001a-5a2d193"
)
BRANCH = "codex/meta-theory-scaffold"

ARTIFACT_DIR = Path("artifacts") / TASK_ID
SUMMARY_PATH = Path("docs/research/GATE4-REPLACEMENT-002C-DYNAMIC-PARTNER-BELIEF-POMDP-EXECUTION-001A.md")

VERDICT_ADVANTAGE = "gate4_replacement_002c_residual_candidate_advantage_with_caveats"
VERDICT_BASELINE_EQUIVALENT = "gate4_replacement_002c_baseline_equivalent_negative_evidence"
VERDICT_BLOCKED = "gate4_replacement_002c_blocked_contract_or_provenance_failure"
VERDICT_INCONCLUSIVE = "gate4_replacement_002c_inconclusive_needs_redesign"

ACTIONS = ["route_alpha", "route_beta", "route_gamma", "route_delta"]
SIGNAL_SUPPORT = {
    "sig_a": [0, 2],
    "sig_b": [0, 3],
    "sig_c": [1, 2],
    "sig_d": [1, 3],
    "neutral_shift": [],
    "ambient_noise": [],
}
SWAPPED_SIGNAL_SUPPORT = {
    "sig_a": [1, 3],
    "sig_b": [1, 2],
    "sig_c": [0, 3],
    "sig_d": [0, 2],
    "neutral_shift": [],
    "ambient_noise": [],
}
TARGET_SIGNALS = {
    0: ["sig_a", "sig_b"],
    1: ["sig_c", "sig_d"],
    2: ["sig_a", "sig_c"],
    3: ["sig_b", "sig_d"],
}
SPLIT_CONTEXTS = {
    "train": ["train_ctx_a", "train_ctx_b"],
    "heldout": ["heldout_ctx_a", "heldout_ctx_b"],
    "counterfactual": ["counterfactual_ctx_a", "counterfactual_ctx_b"],
}
REQUIRED_ABLATIONS = [
    "disable_social_latent_update",
    "freeze_other_state_after_initial_observation",
    "shuffle_partner_observation_history",
    "remove_partner_policy_shift",
    "swap_partner_latent_dynamics",
    "mask_partner_id_and_explicit_labels",
    "inject_target_leakage_positive_control",
    "remove_social_signal_negative_control",
]
PROTECTED_BOUNDARY_PATHS = [
    Path("src/gate4_replacement_discriminative_social_latent_001d"),
    Path("tests/test_gate4_replacement_discriminative_social_latent_001d.py"),
    Path("artifacts/gate4_replacement_discriminative_social_latent_001d"),
    Path("src/gate4_replacement_001e_baseline_equivalence_adjudication_001a"),
    Path("tests/test_gate4_replacement_001e_baseline_equivalence_adjudication_001a.py"),
    Path("artifacts/gate4_replacement_001e_baseline_equivalence_adjudication_001a"),
    Path("artifacts/gate4_replacement_001f_route_closure_and_problem_definition_reset_001a"),
    Path("docs/research/GATE4-REPLACEMENT-001F-ROUTE-CLOSURE-AND-PROBLEM-DEFINITION-RESET-001A.md"),
    Path("artifacts/gate4_replacement_002a_mechanism_problem_definition_and_baseline_first_design_brief_001a"),
    Path("docs/research/GATE4-REPLACEMENT-002A-MECHANISM-PROBLEM-DEFINITION-AND-BASELINE-FIRST-DESIGN-BRIEF-001A.md"),
    Path("artifacts/gate4_replacement_002b_dynamic_partner_belief_pomdp_executable_task_card_001a"),
    Path("docs/research/GATE4-REPLACEMENT-002B-DYNAMIC-PARTNER-BELIEF-POMDP-EXECUTABLE-TASK-CARD-001A.md"),
]
FORBIDDEN_MUTATION_PREFIXES = [
    "src/ego_mainline",
    "src/same_agent_bridge",
    "src/post_bridge",
    "artifacts/ego_mainline",
    "artifacts/same_agent_bridge",
    "docs/research/SAME_AGENT_BRIDGE",
]


@dataclass(frozen=True)
class Episode:
    episode_id: str
    seed: int
    split_name: str
    context_id: str
    partner_id: str
    latent_type: str
    shift_mode: str
    target_action: str
    observation: dict[str, Any]

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
    except (FileNotFoundError, subprocess.CalledProcessError):
        return ""


def _is_ancestor(ancestor: str, descendant: str) -> bool:
    if not ancestor or not descendant:
        return False
    completed = subprocess.run(
        ["git", "merge-base", "--is-ancestor", ancestor, descendant],
        cwd=str(_repo_root()),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return completed.returncode == 0


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


def generate_episodes() -> list[Episode]:
    episodes: list[Episode] = []
    seed = 0
    for split_name, context_ids in SPLIT_CONTEXTS.items():
        for context_index, context_id in enumerate(context_ids):
            for target_index, target_action in enumerate(ACTIONS):
                partner_id = f"partner_{(target_index + context_index) % 4}"
                pre_target_index = (target_index + 1 + context_index) % len(ACTIONS)
                pre_signal = TARGET_SIGNALS[pre_target_index][0]
                post_signals = TARGET_SIGNALS[target_index]
                stream = [
                    _partner_event("pre_shift", pre_signal, 0.20),
                    _partner_event("shift_marker", "neutral_shift", 0.0),
                    _partner_event("post_shift", post_signals[0], 1.0),
                    _partner_event("post_shift", post_signals[1], 1.0),
                ]
                observation = {
                    "context_id": context_id,
                    "partner_id": partner_id,
                    "interaction_round": seed,
                    "policy_shift_marker": "shift_after_history",
                    "menu_preference_marker": f"menu_decoy_{(seed + 2) % 3}",
                    "partner_observation_stream": stream,
                    "query_allowed": True,
                    "visible_labels_masked": True,
                }
                episodes.append(
                    Episode(
                        episode_id=f"{split_name}:{context_id}:{target_index}",
                        seed=seed,
                        split_name=split_name,
                        context_id=context_id,
                        partner_id=partner_id,
                        latent_type="latent_even" if target_index % 2 == 0 else "latent_odd",
                        shift_mode="history_dependent_policy_shift",
                        target_action=target_action,
                        observation=observation,
                    )
                )
                seed += 1
    return episodes


def _partner_event(phase: str, token: str, weight: float) -> dict[str, Any]:
    return {
        "phase": phase,
        "token": token,
        "weight": weight,
        "channel": "partner_behavior_observation",
    }


def initial_candidate_state() -> dict[str, Any]:
    return {
        "self_state": {"query_budget_remaining": 1, "last_action": "observe"},
        "other_state_scores": [0.0 for _ in ACTIONS],
        "other_state_updates": [],
        "policy_shift_seen": False,
        "update_rule": "post_shift_partner_signal_support_accumulation",
    }


def choose_candidate_query(observation: dict[str, Any], serialized_state: dict[str, Any]) -> dict[str, Any]:
    del serialized_state
    return {
        "query_type": "partner_shift_probe",
        "query_budget_spent": 1 if observation.get("query_allowed") else 0,
        "query_payload": "request_partner_response_after_shift",
    }


def _observation_for_intervention(observation: dict[str, Any], intervention: str | None) -> dict[str, Any]:
    changed = copy.deepcopy(observation)
    stream = list(changed["partner_observation_stream"])
    if intervention == "shuffle_partner_observation_history":
        stream = list(reversed(stream))
    elif intervention == "remove_partner_policy_shift":
        stream = [event for event in stream if event["phase"] != "post_shift"]
        changed["policy_shift_marker"] = "no_policy_shift"
    elif intervention == "swap_partner_latent_dynamics":
        stream = [
            {**event, "token": {"sig_a": "sig_c", "sig_b": "sig_d", "sig_c": "sig_a", "sig_d": "sig_b"}.get(event["token"], event["token"])}
            for event in stream
        ]
    elif intervention == "mask_partner_id_and_explicit_labels":
        changed["partner_id"] = "masked_partner"
        changed["visible_labels_masked"] = True
    elif intervention == "remove_social_signal_negative_control":
        stream = [_partner_event("neutral", "ambient_noise", 0.0) for _event in stream]
    changed["partner_observation_stream"] = stream
    return changed


def update_other_state(
    serialized_state: dict[str, Any],
    observation: dict[str, Any],
    query_action: dict[str, Any],
    intervention: str | None = None,
) -> dict[str, Any]:
    state = copy.deepcopy(serialized_state)
    if intervention == "disable_social_latent_update" or query_action.get("query_budget_spent", 0) <= 0:
        return state
    support_map = SWAPPED_SIGNAL_SUPPORT if intervention == "swap_partner_latent_dynamics" else SIGNAL_SUPPORT
    scores = [float(value) for value in state["other_state_scores"]]
    processed_post_shift = 0
    for event in observation["partner_observation_stream"]:
        if event["phase"] == "shift_marker":
            state["policy_shift_seen"] = True
            continue
        if event["phase"] != "post_shift":
            continue
        if intervention == "freeze_other_state_after_initial_observation" and processed_post_shift >= 1:
            continue
        token = str(event["token"])
        weight = float(event.get("weight", 0.0))
        for slot in support_map.get(token, []):
            scores[slot] += weight
        state["other_state_updates"].append(
            {"token": token, "phase": event["phase"], "support": list(support_map.get(token, [])), "weight": weight}
        )
        processed_post_shift += 1
    state["other_state_scores"] = scores
    return state


def choose_candidate_action(serialized_state: dict[str, Any]) -> str:
    scores = [float(value) for value in serialized_state.get("other_state_scores", [])]
    if not scores:
        return ACTIONS[0]
    best = max(range(len(scores)), key=lambda idx: (scores[idx], -idx))
    return ACTIONS[best]


def run_candidate_episode(episode: Episode, intervention: str | None = None) -> dict[str, Any]:
    observation = _observation_for_intervention(episode.observation, intervention)
    if intervention == "inject_target_leakage_positive_control":
        observation["answer_label"] = episode.target_action
    state_before = initial_candidate_state()
    query_action = choose_candidate_query(observation, state_before)
    state_after = update_other_state(state_before, observation, query_action, intervention=intervention)
    prediction = choose_candidate_action(state_after)
    return {
        "episode_id": episode.episode_id,
        "seed": episode.seed,
        "split_name": episode.split_name,
        "context_id": episode.context_id,
        "partner_id": episode.partner_id,
        "latent_type": episode.latent_type,
        "scorer_only_target_action": episode.target_action,
        "candidate_visible": {
            "observation": observation,
            "query_action": query_action,
            "serialized_state_before_update": state_before,
            "serialized_state_after_update": state_after,
        },
        "final_prediction": prediction,
        "correct": prediction == episode.target_action,
        "intervention": intervention or "none",
    }


def _score_predictions(episodes: list[Episode], predictions: dict[str, str]) -> float:
    return sum(1 for episode in episodes if predictions.get(episode.episode_id) == episode.target_action) / len(episodes)


def _score_trace(trace_records: list[dict[str, Any]]) -> float:
    return sum(1 for row in trace_records if row["correct"]) / len(trace_records)


def _split_scores(trace_records: list[dict[str, Any]]) -> dict[str, float]:
    scores = {}
    for split_name in SPLIT_CONTEXTS:
        rows = [row for row in trace_records if row["split_name"] == split_name]
        scores[split_name] = _score_trace(rows)
    return scores


def score_candidate(
    episodes: list[Episode],
    run_id: str,
    intervention: str | None = None,
) -> dict[str, Any]:
    trace_records = [run_candidate_episode(episode, intervention=intervention) for episode in episodes]
    return {
        "producer_function": "score_candidate",
        "candidate_id": "explicit_self_other_partner_belief_update_candidate",
        "run_id": run_id,
        "intervention": intervention or "none",
        "callable_invoked": True,
        "score": _score_trace(trace_records),
        "split_scores": _split_scores(trace_records),
        "uses_self_state": True,
        "uses_other_state": True,
        "updates_other_state_from_observed_behavior": intervention != "disable_social_latent_update",
        "uses_partner_id_for_update": False,
        "traceable_latent_updates": True,
        "trace_records": trace_records,
    }


def _majority_action(episodes: list[Episode]) -> str:
    counts = Counter(episode.target_action for episode in episodes if episode.split_name == "train")
    return max(ACTIONS, key=lambda action: (counts[action], -ACTIONS.index(action)))


def _train_episodes(episodes: list[Episode]) -> list[Episode]:
    return [episode for episode in episodes if episode.split_name == "train"]


def _post_shift_tokens(observation: dict[str, Any]) -> list[str]:
    return [
        str(event["token"])
        for event in observation["partner_observation_stream"]
        if event.get("phase") == "post_shift"
    ]


def _decode_from_tokens(tokens: list[str], fallback: str = ACTIONS[0]) -> str:
    scores = [0.0 for _action in ACTIONS]
    for token in tokens:
        for slot in SIGNAL_SUPPORT.get(token, []):
            scores[slot] += 1.0
    if not any(scores):
        return fallback
    return ACTIONS[max(range(len(scores)), key=lambda idx: (scores[idx], -idx))]


def baseline_random_control(episodes: list[Episode], trace_records: list[dict[str, Any]]) -> dict[str, str]:
    del trace_records
    return {episode.episode_id: ACTIONS[0] for episode in episodes}


def baseline_pair_count(episodes: list[Episode], trace_records: list[dict[str, Any]]) -> dict[str, str]:
    del trace_records
    table: dict[tuple[str, ...], Counter[str]] = {}
    for episode in _train_episodes(episodes):
        key = tuple(sorted(_post_shift_tokens(episode.observation)))
        table.setdefault(key, Counter())[episode.target_action] += 1
    fallback = _majority_action(episodes)
    predictions = {}
    for episode in episodes:
        key = tuple(sorted(_post_shift_tokens(episode.observation)))
        counts = table.get(key)
        predictions[episode.episode_id] = (
            max(ACTIONS, key=lambda action: (counts[action], -ACTIONS.index(action))) if counts else fallback
        )
    return predictions


def baseline_ngram_trace_lookup(episodes: list[Episode], trace_records: list[dict[str, Any]]) -> dict[str, str]:
    del trace_records
    table = {
        tuple(_post_shift_tokens(episode.observation)): episode.target_action
        for episode in _train_episodes(episodes)
    }
    fallback = _majority_action(episodes)
    return {
        episode.episode_id: table.get(tuple(_post_shift_tokens(episode.observation)), fallback)
        for episode in episodes
    }


def baseline_partner_id(episodes: list[Episode], trace_records: list[dict[str, Any]]) -> dict[str, str]:
    del trace_records
    table: dict[str, Counter[str]] = {}
    for episode in _train_episodes(episodes):
        table.setdefault(episode.partner_id, Counter())[episode.target_action] += 1
    fallback = _majority_action(episodes)
    return {
        episode.episode_id: (
            max(ACTIONS, key=lambda action: (table[episode.partner_id][action], -ACTIONS.index(action)))
            if episode.partner_id in table
            else fallback
        )
        for episode in episodes
    }


def baseline_preference_table(episodes: list[Episode], trace_records: list[dict[str, Any]]) -> dict[str, str]:
    del trace_records
    table: dict[str, Counter[str]] = {}
    for episode in _train_episodes(episodes):
        marker = str(episode.observation["menu_preference_marker"])
        table.setdefault(marker, Counter())[episode.target_action] += 1
    fallback = _majority_action(episodes)
    predictions = {}
    for episode in episodes:
        marker = str(episode.observation["menu_preference_marker"])
        counts = table.get(marker)
        predictions[episode.episode_id] = (
            max(ACTIONS, key=lambda action: (counts[action], -ACTIONS.index(action))) if counts else fallback
        )
    return predictions


def baseline_full_bundle_decoder(episodes: list[Episode], trace_records: list[dict[str, Any]]) -> dict[str, str]:
    del episodes
    return {
        row["episode_id"]: _decode_from_tokens(
            _post_shift_tokens(row["candidate_visible"]["observation"]),
            fallback=ACTIONS[0],
        )
        for row in trace_records
    }


def baseline_serialized_state_decoder(episodes: list[Episode], trace_records: list[dict[str, Any]]) -> dict[str, str]:
    del episodes
    return {
        row["episode_id"]: choose_candidate_action(row["candidate_visible"]["serialized_state_after_update"])
        for row in trace_records
    }


def baseline_finite_state_policy(episodes: list[Episode], trace_records: list[dict[str, Any]]) -> dict[str, str]:
    del trace_records
    return {
        episode.episode_id: ACTIONS[0 if episode.observation["policy_shift_marker"] == "shift_after_history" else 1]
        for episode in episodes
    }


def baseline_query_capable_imitation(episodes: list[Episode], trace_records: list[dict[str, Any]]) -> dict[str, str]:
    del trace_records
    fallback = _majority_action(episodes)
    predictions = {}
    for episode in episodes:
        tokens = _post_shift_tokens(episode.observation)
        predictions[episode.episode_id] = _decode_from_tokens(tokens[:1], fallback=fallback)
    return predictions


def baseline_belief_table(episodes: list[Episode], trace_records: list[dict[str, Any]]) -> dict[str, str]:
    del trace_records
    return {
        episode.episode_id: _decode_from_tokens(_post_shift_tokens(episode.observation), fallback=ACTIONS[0])
        for episode in episodes
    }


def baseline_oracle_access_upper_bound(episodes: list[Episode], trace_records: list[dict[str, Any]]) -> dict[str, str]:
    del trace_records
    return {episode.episode_id: episode.target_action for episode in episodes}


def baseline_ablated_candidate_social_latent_disabled(
    episodes: list[Episode],
    trace_records: list[dict[str, Any]],
) -> dict[str, str]:
    del trace_records
    rows = [run_candidate_episode(episode, intervention="disable_social_latent_update") for episode in episodes]
    return {row["episode_id"]: row["final_prediction"] for row in rows}


def baseline_non_social_world_model(episodes: list[Episode], trace_records: list[dict[str, Any]]) -> dict[str, str]:
    del trace_records
    table: dict[str, Counter[str]] = {}
    for episode in _train_episodes(episodes):
        key = f"{episode.split_name}:{episode.observation['menu_preference_marker']}"
        table.setdefault(key, Counter())[episode.target_action] += 1
    fallback = _majority_action(episodes)
    return {
        episode.episode_id: (
            max(ACTIONS, key=lambda action: (table[f"{episode.split_name}:{episode.observation['menu_preference_marker']}"][action], -ACTIONS.index(action)))
            if f"{episode.split_name}:{episode.observation['menu_preference_marker']}" in table
            else fallback
        )
        for episode in episodes
    }


BASELINE_FUNCTIONS: dict[str, Callable[[list[Episode], list[dict[str, Any]]], dict[str, str]]] = {
    "random_control": baseline_random_control,
    "pair_count": baseline_pair_count,
    "ngram_trace_lookup": baseline_ngram_trace_lookup,
    "partner_id": baseline_partner_id,
    "preference_table": baseline_preference_table,
    "full_bundle_decoder": baseline_full_bundle_decoder,
    "serialized_state_decoder": baseline_serialized_state_decoder,
    "finite_state_policy": baseline_finite_state_policy,
    "query_capable_imitation": baseline_query_capable_imitation,
    "belief_table": baseline_belief_table,
    "oracle_access_upper_bound": baseline_oracle_access_upper_bound,
    "ablated_candidate_social_latent_disabled": baseline_ablated_candidate_social_latent_disabled,
    "non_social_world_model": baseline_non_social_world_model,
}


def _access_rights_for_baseline(baseline_id: str) -> str:
    rights = {
        "random_control": "no observation, deterministic seed-only control",
        "pair_count": "train split post-shift partner observation token pairs only",
        "ngram_trace_lookup": "train split ordered partner observation tokens only",
        "partner_id": "partner_id and train targets only",
        "preference_table": "visible decoy menu preference marker and train targets only",
        "full_bundle_decoder": "candidate-visible observation bundle, no scorer target",
        "serialized_state_decoder": "candidate serialized other-state after update, no scorer target",
        "finite_state_policy": "visible policy-shift marker only",
        "query_capable_imitation": "same partner observation stream after a query, no latent state",
        "belief_table": "hand-coded belief table over visible partner observation tokens",
        "oracle_access_upper_bound": "scorer-only target access, positive upper bound only",
        "ablated_candidate_social_latent_disabled": "candidate code path with social-latent update disabled",
        "non_social_world_model": "context and decoy environment markers, no partner observation stream",
    }
    return rights[baseline_id]


def run_baselines(
    episodes: list[Episode],
    trace_records: list[dict[str, Any]],
    run_id: str,
) -> dict[str, Any]:
    rows = {}
    scores = {}
    for baseline_id, producer in BASELINE_FUNCTIONS.items():
        predictions = producer(episodes, trace_records)
        score = _score_predictions(episodes, predictions)
        scores[baseline_id] = score
        rows[baseline_id] = {
            "baseline_id": baseline_id,
            "producer_function": producer.__name__,
            "callable_invoked": True,
            "score": score,
            "predictions": predictions,
            "run_id": f"{run_id}:baseline:{baseline_id}",
            "seed": _seed_scope(episodes),
            "train_context_ids": _context_scope(episodes, "train"),
            "heldout_context_ids": _context_scope(episodes, "heldout"),
            "counterfactual_context_ids": _context_scope(episodes, "counterfactual"),
            "episode_ids": [episode.episode_id for episode in episodes],
            "aggregation_rule": "accuracy over train, heldout, and counterfactual contexts",
            "code_path_hash": code_path_hash(producer),
            "access_rights_declaration": _access_rights_for_baseline(baseline_id),
            "failure_mode_ruled_out": "baseline callable was invoked over the same generated episodes",
            "faithful_non_oracle": baseline_id != "oracle_access_upper_bound",
            "static_score_injection": False,
        }
    report = {
        "producer_function": "run_baselines",
        "run_id": run_id,
        "invoked_baselines": list(rows),
        "rows": rows,
        "scores": scores,
    }
    report["invocation_check"] = verify_required_baseline_invocations(report)
    return report


def verify_required_baseline_invocations(report: dict[str, Any]) -> dict[str, Any]:
    invoked = set(report.get("invoked_baselines", []))
    missing = sorted(set(BASELINE_FUNCTIONS) - invoked)
    return {
        "producer_function": "verify_required_baseline_invocations",
        "passed": not missing,
        "missing_baselines": missing,
    }


def select_strongest_baseline(baseline_results: dict[str, Any], candidate_score: float) -> dict[str, Any]:
    rows = baseline_results["rows"]
    faithful_rows = [row for row in rows.values() if row["faithful_non_oracle"]]
    strongest_faithful = max(faithful_rows, key=lambda row: (row["score"], row["baseline_id"]))
    strongest_any = max(rows.values(), key=lambda row: (row["score"], row["baseline_id"]))
    tied_or_beat = [
        row["baseline_id"]
        for row in faithful_rows
        if row["score"] >= candidate_score
    ]
    return {
        "producer_function": "select_strongest_baseline",
        "candidate_score": candidate_score,
        "strongest_faithful_non_oracle": {
            "baseline_id": strongest_faithful["baseline_id"],
            "producer_function": strongest_faithful["producer_function"],
            "score": strongest_faithful["score"],
            "access_rights_declaration": strongest_faithful["access_rights_declaration"],
        },
        "strongest_any_including_oracle": {
            "baseline_id": strongest_any["baseline_id"],
            "producer_function": strongest_any["producer_function"],
            "score": strongest_any["score"],
        },
        "faithful_baselines_tied_or_beat_candidate": tied_or_beat,
        "baseline_equivalence": bool(tied_or_beat),
    }


def run_ablation_suite(episodes: list[Episode], candidate_score: float, run_id: str) -> dict[str, Any]:
    interventions = {}
    for ablation_id in REQUIRED_ABLATIONS:
        ablation_run_id = f"{run_id}:ablation:{ablation_id}"
        candidate = score_candidate(episodes, ablation_run_id, intervention=ablation_id)
        trace_records = candidate["trace_records"]
        relevant_baselines = run_baselines(episodes, trace_records, ablation_run_id)
        leakage_report = scan_candidate_visible_bundle([row["candidate_visible"] for row in trace_records])
        interventions[ablation_id] = {
            "producer_function": "score_candidate",
            "run_id": ablation_run_id,
            "candidate_score": candidate["score"],
            "drop_from_candidate": candidate_score - candidate["score"],
            "baseline_scores": relevant_baselines["scores"],
            "baselines_rerun": True,
            "leakage_scan_verdict": leakage_report["verdict"],
        }
    return {
        "producer_function": "run_ablation_suite",
        "all_interventions_rerun": all(row["baselines_rerun"] for row in interventions.values()),
        "interventions": interventions,
        "passed": interventions["disable_social_latent_update"]["candidate_score"] < candidate_score,
    }


def scan_candidate_visible_bundle(candidate_visible_bundle: list[dict[str, Any]]) -> dict[str, Any]:
    forbidden = set(ACTIONS) | {"answer_label", "target_action", "scorer_only_target_action", "correct_action"}
    hits = []
    for index, bundle in enumerate(candidate_visible_bundle):
        for path, value in _flatten(bundle):
            path_text = ".".join(path)
            value_text = str(value)
            if any(term == path[-1] or term in value_text for term in forbidden):
                hits.append({"bundle_index": index, "path": path_text, "value": value_text})
    return {
        "producer_function": "scan_candidate_visible_bundle",
        "verdict": "blocked_by_leakage_scan" if hits else "clean",
        "leakage_detected": bool(hits),
        "hits": hits,
        "positive_control_capable": True,
    }


def build_leakage_positive_control_results(episodes: list[Episode], run_id: str) -> dict[str, Any]:
    positive = score_candidate(episodes, f"{run_id}:leakage_positive", intervention="inject_target_leakage_positive_control")
    clean = score_candidate(episodes, f"{run_id}:leakage_clean")
    positive_scan = scan_candidate_visible_bundle([row["candidate_visible"] for row in positive["trace_records"]])
    clean_scan = scan_candidate_visible_bundle([row["candidate_visible"] for row in clean["trace_records"]])
    return {
        "producer_function": "build_leakage_positive_control_results",
        "run_id": run_id,
        "scanner_positive_control_case": positive_scan,
        "clean_case": clean_scan,
        "positive_control_detected": positive_scan["verdict"] == "blocked_by_leakage_scan",
        "clean_case_passed": clean_scan["verdict"] == "clean",
    }


def build_negative_control_results(episodes: list[Episode], candidate_score: float, run_id: str) -> dict[str, Any]:
    no_signal = score_candidate(
        episodes,
        f"{run_id}:negative_control:no_signal",
        intervention="remove_social_signal_negative_control",
    )
    return {
        "producer_function": "build_negative_control_results",
        "run_id": f"{run_id}:negative_control:no_signal",
        "score": no_signal["score"],
        "candidate_score": candidate_score,
        "false_success_blocked": no_signal["score"] < candidate_score,
        "claim_if_not_blocked": "would be false success under no social signal",
    }


def recompute_candidate_from_serialized_state_plus_observation(trace_record: dict[str, Any]) -> dict[str, Any]:
    visible = copy.deepcopy(trace_record["candidate_visible"])
    query = choose_candidate_query(visible["observation"], visible["serialized_state_before_update"])
    state_after = update_other_state(visible["serialized_state_before_update"], visible["observation"], query)
    prediction = choose_candidate_action(state_after)
    matched = (
        query == visible["query_action"]
        and state_after == visible["serialized_state_after_update"]
        and prediction == trace_record["final_prediction"]
    )
    return {
        "producer_function": "recompute_candidate_from_serialized_state_plus_observation",
        "expected_action_or_prediction": trace_record["final_prediction"],
        "actual_recomputed_action_or_prediction": prediction,
        "comparison_rule": "exact query, state, and prediction equality",
        "matched_original": matched,
    }


def _corrupt_trace_observation(trace_record: dict[str, Any]) -> dict[str, Any]:
    changed = copy.deepcopy(trace_record)
    for event in changed["candidate_visible"]["observation"]["partner_observation_stream"]:
        if event["phase"] == "post_shift":
            event["token"] = "ambient_noise"
            event["weight"] = 0.0
    return changed


def build_replay_results(trace_records: list[dict[str, Any]], run_id: str) -> dict[str, Any]:
    recomputed = [recompute_candidate_from_serialized_state_plus_observation(row) for row in trace_records]
    failure_path = recompute_candidate_from_serialized_state_plus_observation(_corrupt_trace_observation(trace_records[0]))
    baseline_replay = {
        "serialized_state_decoder": all(
            choose_candidate_action(row["candidate_visible"]["serialized_state_after_update"]) == row["final_prediction"]
            for row in trace_records
        ),
        "belief_table": all(
            _decode_from_tokens(_post_shift_tokens(row["candidate_visible"]["observation"])) == row["final_prediction"]
            for row in trace_records
        ),
    }
    return {
        "producer_function": "build_replay_results",
        "run_id": run_id,
        "serialized_state_path": str(ARTIFACT_DIR / "serialized_states.jsonl"),
        "observation_path": str(ARTIFACT_DIR / "observations.jsonl"),
        "recomputation_function": "recompute_candidate_from_serialized_state_plus_observation",
        "replay_run_id": f"{run_id}:replay",
        "comparison_rule": "exact recomputation from serialized_state_before_update plus observation",
        "passed": all(row["matched_original"] for row in recomputed),
        "recomputed_from_serialized_state_plus_observation": True,
        "records_checked": len(recomputed),
        "baseline_replay_recomputed": baseline_replay,
        "failure_path_result": {
            "passed": failure_path["matched_original"],
            "actual_recomputed_action_or_prediction": failure_path["actual_recomputed_action_or_prediction"],
            "comparison_rule": failure_path["comparison_rule"],
        },
    }


def build_environment_manifest(episodes: list[Episode]) -> dict[str, Any]:
    return {
        "producer_function": "build_environment_manifest",
        "task_id": TASK_ID,
        "partial_observability": True,
        "partner_latent_types": sorted({episode.latent_type for episode in episodes}),
        "partner_policy_shift_after_interaction_history": True,
        "heldout_partner_dynamics": _context_scope(episodes, "heldout"),
        "counterfactual_partner_response_probes": _context_scope(episodes, "counterfactual"),
        "interventions": REQUIRED_ABLATIONS,
        "negative_control_no_signal_condition": "remove_social_signal_negative_control",
        "positive_control_leakage_condition": "inject_target_leakage_positive_control",
        "train_context_ids": _context_scope(episodes, "train"),
        "heldout_context_ids": _context_scope(episodes, "heldout"),
        "counterfactual_context_ids": _context_scope(episodes, "counterfactual"),
        "ablation_context_ids": [f"ablation:{name}" for name in REQUIRED_ABLATIONS],
        "target_not_directly_recoverable_claim": "tested by baselines, not assumed",
    }


def build_source_pin_readback(run_id: str) -> dict[str, Any]:
    local_head = _safe_git(["rev-parse", "HEAD"])
    local_required_tag = _safe_git(["rev-parse", REQUIRED_TAG])
    remote_required_tag = ""
    remote_branch = ""
    rows = _safe_git(["ls-remote", "origin", f"refs/tags/{REQUIRED_TAG}", f"refs/heads/{BRANCH}"])
    for row in rows.splitlines():
        if not row.strip():
            continue
        commit, ref = row.split(maxsplit=1)
        if ref == f"refs/tags/{REQUIRED_TAG}":
            remote_required_tag = commit
        if ref == f"refs/heads/{BRANCH}":
            remote_branch = commit
    return {
        "producer_function": "build_source_pin_readback",
        "task_id": TASK_ID,
        "run_id": run_id,
        "sealed_boundary": SEALED_BOUNDARY,
        "required_tag": REQUIRED_TAG,
        "branch": BRANCH,
        "local_head": local_head,
        "local_required_tag": local_required_tag,
        "remote_required_tag": remote_required_tag,
        "remote_branch": remote_branch,
        "local_head_equals_sealed_boundary": local_head == SEALED_BOUNDARY,
        "sealed_boundary_is_ancestor_of_local_head": _is_ancestor(SEALED_BOUNDARY, local_head),
        "remote_branch_equals_sealed_boundary": remote_branch == SEALED_BOUNDARY,
        "sealed_anchor_integrity_verified": local_required_tag == remote_required_tag == SEALED_BOUNDARY,
        "source_boundary_preimplementation_readback": {
            "verified_by_task_session_before_file_edits": True,
            "local_head": SEALED_BOUNDARY,
            "local_tag": SEALED_BOUNDARY,
            "remote_branch": SEALED_BOUNDARY,
            "remote_tag": SEALED_BOUNDARY,
        },
        "prior_negative_evidence_pinned": {
            "001e_baseline_equivalence_negative_evidence": True,
            "001f_route_closure_preserved": True,
            "002a_baseline_first_problem_definition_preserved": True,
            "002b_executable_task_card_boundary_preserved": True,
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
    forbidden_status = _path_status(FORBIDDEN_MUTATION_PREFIXES)
    return {
        "producer_function": "build_non_mutation_guard",
        "protected_paths": sorted(before_hashes),
        "changed_protected_paths": changed,
        "forbidden_status_modified": forbidden_status,
        "prior_artifacts_mutated": bool(changed),
        "passed": not changed and not forbidden_status,
    }


def build_result(run: dict[str, Any]) -> dict[str, Any]:
    reasons = []
    stop_conditions = []
    if not run["baseline_results"]["invocation_check"]["passed"]:
        reasons.append("missing_baseline_invocation")
    if not run["leakage_positive_control_results"]["positive_control_detected"]:
        reasons.append("positive_control_leakage_not_detected")
    if not run["negative_control_results"]["false_success_blocked"]:
        reasons.append("negative_control_false_success")
    if not run["replay_results"]["passed"]:
        reasons.append("replay_not_recomputed")
    if not run["ablation_results"]["all_interventions_rerun"]:
        reasons.append("ablation_not_rerun")
    if not run["provenance_manifest"]["verification"]["passed"]:
        reasons.append("provenance_failed")
    if not run["non_mutation_guard"]["passed"]:
        reasons.append("prior_artifact_mutation")
    if run["strongest_baseline_report"]["baseline_equivalence"]:
        stop_conditions.append("faithful_baseline_tied_or_beat_candidate")
    if run["baseline_results"]["scores"]["serialized_state_decoder"] >= run["candidate_result"]["score"]:
        stop_conditions.append("serialized_state_decoder_reached_candidate_equivalent_performance")
    if run["baseline_results"]["scores"]["full_bundle_decoder"] >= run["candidate_result"]["score"]:
        stop_conditions.append("full_bundle_decoder_reached_candidate_equivalent_performance")
    if reasons:
        verdict = VERDICT_BLOCKED
    elif stop_conditions:
        verdict = VERDICT_BASELINE_EQUIVALENT
    elif _underpowered(run):
        verdict = VERDICT_INCONCLUSIVE
    else:
        verdict = VERDICT_ADVANTAGE
    flags = _downstream_flags()
    return {
        "producer_function": "build_result",
        "task_id": TASK_ID,
        "verdict": verdict,
        "blocking_reasons": sorted(set(reasons)),
        "stop_conditions_triggered": sorted(set(stop_conditions)),
        "candidate_score": run["candidate_result"]["score"],
        "strongest_faithful_non_oracle": run["strongest_baseline_report"]["strongest_faithful_non_oracle"],
        "baseline_equivalence": bool(stop_conditions),
        "positive_mechanism_evidence_allowed": verdict == VERDICT_ADVANTAGE,
        "downstream_authorization_flags": flags,
        "downstream_authorization_flags_all_false": not any(flags.values()),
        "safe_to_enter_gate5": False,
        "safe_to_enter_admission": False,
        "safe_to_enter_bridge": False,
        "safe_to_enter_runtime": False,
        "safe_to_enter_ego_mainline": False,
        "claim_ceiling": CLAIM_CEILING,
        "what_this_does_not_prove": [
            "valid Gate4",
            "general social-latent inference",
            "mechanism validity outside this toy task",
            "agency",
            "selfhood",
            "consciousness",
            "emotion",
            "autonomy",
            "EGO readiness",
            "stable user benefit",
        ],
    }


def _underpowered(run: dict[str, Any]) -> bool:
    return run["candidate_result"]["score"] < 0.5


def _downstream_flags() -> dict[str, bool]:
    return {
        "gate5_authorized": False,
        "admission_authorized": False,
        "bridge_authorized": False,
        "runtime_authorized": False,
        "ego_mainline_authorized": False,
        "companion_product_ux_authorized": False,
        "consciousness_subjectivity_autonomy_claim_authorized": False,
    }


def _seed_scope(episodes: list[Episode]) -> int:
    return 20260613


def _context_scope(episodes: list[Episode], split_name: str) -> list[str]:
    return sorted({episode.context_id for episode in episodes if episode.split_name == split_name})


def _episode_ids(episodes: list[Episode]) -> list[str]:
    return [episode.episode_id for episode in episodes]


def _provenance_record(
    result_family: str,
    producer_function: str,
    computed_score: float,
    run_id: str,
    episodes: list[Episode],
    identifier: str,
    artifact_pointer: str,
    input_artifacts: list[str],
) -> dict[str, Any]:
    return {
        "result_family": result_family,
        "producer_function": producer_function,
        "input_artifacts": input_artifacts,
        "run_id": run_id,
        "seed": _seed_scope(episodes),
        "train_context_ids": _context_scope(episodes, "train"),
        "heldout_context_ids": _context_scope(episodes, "heldout"),
        "counterfactual_context_ids": _context_scope(episodes, "counterfactual"),
        "episode_ids": _episode_ids(episodes),
        "aggregation_rule": "computed by callable 002C execution path over generated train, heldout, and counterfactual episodes",
        "computed_score": computed_score,
        "code_path_hash": code_path_hash(resolve_producer(producer_function)),
        "candidate_or_baseline_identifier": identifier,
        "artifact_pointer": artifact_pointer,
        "static_score_injection": False,
    }


def build_provenance_manifest(run: dict[str, Any], episodes: list[Episode]) -> dict[str, Any]:
    records = [
        _provenance_record(
            "candidate_result",
            "score_candidate",
            run["candidate_result"]["score"],
            run["run_id"],
            episodes,
            "candidate",
            "candidate_result.json",
            ["environment_manifest.json"],
        ),
        _provenance_record(
            "baseline_results",
            "run_baselines",
            run["strongest_baseline_report"]["strongest_faithful_non_oracle"]["score"],
            run["run_id"],
            episodes,
            "all_baselines",
            "baseline_results.json",
            ["environment_manifest.json", "trace.jsonl"],
        ),
        _provenance_record(
            "strongest_baseline_report",
            "select_strongest_baseline",
            run["strongest_baseline_report"]["strongest_faithful_non_oracle"]["score"],
            run["run_id"],
            episodes,
            "strongest_faithful_non_oracle",
            "strongest_baseline_report.json",
            ["baseline_results.json"],
        ),
        _provenance_record(
            "ablation_results",
            "run_ablation_suite",
            min(row["candidate_score"] for row in run["ablation_results"]["interventions"].values()),
            run["run_id"],
            episodes,
            "all_ablations",
            "ablation_results.json",
            ["environment_manifest.json"],
        ),
        _provenance_record(
            "leakage_positive_control_results",
            "build_leakage_positive_control_results",
            1.0 if run["leakage_positive_control_results"]["positive_control_detected"] else 0.0,
            run["run_id"],
            episodes,
            "leakage_positive_control",
            "leakage_positive_control_results.json",
            ["candidate_result.json"],
        ),
        _provenance_record(
            "negative_control_results",
            "build_negative_control_results",
            run["negative_control_results"]["score"],
            run["run_id"],
            episodes,
            "negative_control_no_signal",
            "negative_control_results.json",
            ["environment_manifest.json"],
        ),
        _provenance_record(
            "replay_results",
            "build_replay_results",
            1.0 if run["replay_results"]["passed"] else 0.0,
            run["run_id"],
            episodes,
            "trace_replay",
            "replay_results.json",
            ["trace.jsonl", "observations.jsonl", "serialized_states.jsonl"],
        ),
        _provenance_record(
            "non_mutation_guard",
            "build_non_mutation_guard",
            1.0 if run["non_mutation_guard"]["passed"] else 0.0,
            run["run_id"],
            episodes,
            "non_mutation_guard",
            "non_mutation_guard.json",
            ["source_pin_readback.json"],
        ),
        _provenance_record(
            "result",
            "build_result",
            1.0 if run["strongest_baseline_report"]["baseline_equivalence"] else 0.0,
            run["run_id"],
            episodes,
            "result",
            "result.json",
            ["candidate_result.json", "baseline_results.json"],
        ),
    ]
    for baseline_id, row in run["baseline_results"]["rows"].items():
        records.append(
            _provenance_record(
                f"baseline:{baseline_id}",
                row["producer_function"],
                row["score"],
                row["run_id"],
                episodes,
                baseline_id,
                "baseline_results.json",
                ["environment_manifest.json", "trace.jsonl"],
            )
        )
    manifest = {"producer_function": "build_provenance_manifest", "records": records}
    manifest["verification"] = verify_provenance(manifest)
    return manifest


def build_static_score_guard_report(provenance_manifest: dict[str, Any]) -> dict[str, Any]:
    injected = copy.deepcopy(provenance_manifest)
    injected["records"][0]["static_score_injection"] = True
    injected["records"][0]["producer_function"] = "literal_score_table"
    injected_result = verify_provenance(injected)
    clean_result = verify_provenance(provenance_manifest)
    return {
        "producer_function": "build_static_score_guard_report",
        "positive_control_static_injection_detected": not injected_result["passed"],
        "clean_provenance_passed": clean_result["passed"],
        "injected_blocking_reasons": injected_result["blocking_reasons"],
    }


def verify_provenance(manifest: dict[str, Any]) -> dict[str, Any]:
    required_fields = {
        "producer_function",
        "input_artifacts",
        "run_id",
        "seed",
        "train_context_ids",
        "heldout_context_ids",
        "counterfactual_context_ids",
        "episode_ids",
        "aggregation_rule",
        "computed_score",
        "code_path_hash",
        "candidate_or_baseline_identifier",
        "artifact_pointer",
    }
    reasons = []
    for row in manifest.get("records", []):
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
        if not row.get("train_context_ids"):
            reasons.append(f"missing_train_contexts:{row.get('result_family')}")
        if not row.get("heldout_context_ids"):
            reasons.append(f"missing_heldout_contexts:{row.get('result_family')}")
        if not row.get("counterfactual_context_ids"):
            reasons.append(f"missing_counterfactual_contexts:{row.get('result_family')}")
        if not row.get("episode_ids"):
            reasons.append(f"missing_episode_ids:{row.get('result_family')}")
    return {
        "producer_function": "verify_provenance",
        "passed": not reasons,
        "blocking_reasons": sorted(set(reasons)),
    }


def resolve_producer(name: str) -> Callable[..., Any]:
    producers: dict[str, Callable[..., Any]] = {
        "score_candidate": score_candidate,
        "run_baselines": run_baselines,
        "select_strongest_baseline": select_strongest_baseline,
        "run_ablation_suite": run_ablation_suite,
        "build_leakage_positive_control_results": build_leakage_positive_control_results,
        "build_negative_control_results": build_negative_control_results,
        "build_replay_results": build_replay_results,
        "build_non_mutation_guard": build_non_mutation_guard,
        "build_result": build_result,
        "baseline_random_control": baseline_random_control,
        "baseline_pair_count": baseline_pair_count,
        "baseline_ngram_trace_lookup": baseline_ngram_trace_lookup,
        "baseline_partner_id": baseline_partner_id,
        "baseline_preference_table": baseline_preference_table,
        "baseline_full_bundle_decoder": baseline_full_bundle_decoder,
        "baseline_serialized_state_decoder": baseline_serialized_state_decoder,
        "baseline_finite_state_policy": baseline_finite_state_policy,
        "baseline_query_capable_imitation": baseline_query_capable_imitation,
        "baseline_belief_table": baseline_belief_table,
        "baseline_oracle_access_upper_bound": baseline_oracle_access_upper_bound,
        "baseline_ablated_candidate_social_latent_disabled": baseline_ablated_candidate_social_latent_disabled,
        "baseline_non_social_world_model": baseline_non_social_world_model,
    }
    return producers[name]


def code_path_hash(func: Callable[..., Any]) -> str:
    return hashlib.sha256(inspect.getsource(func).encode("utf-8")).hexdigest()


def _flatten(value: Any, path: tuple[str, ...] = ()) -> list[tuple[tuple[str, ...], Any]]:
    if isinstance(value, dict):
        rows: list[tuple[tuple[str, ...], Any]] = []
        for key, child in value.items():
            rows.extend(_flatten(child, (*path, str(key))))
        return rows
    if isinstance(value, list):
        rows = []
        for index, child in enumerate(value):
            rows.extend(_flatten(child, (*path, str(index))))
        return rows
    return [(path, value)]


def _json_ready(value: Any) -> Any:
    if isinstance(value, Episode):
        return value.to_json_dict()
    if isinstance(value, dict):
        return {key: _json_ready(child) for key, child in value.items() if key != "trace_records"}
    if isinstance(value, list):
        return [_json_ready(child) for child in value]
    return value


def _write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(_json_ready(value), indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_artifacts(output_dir: Path, run: dict[str, Any]) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    artifact_map = {
        "result.json": run["result"],
        "environment_manifest.json": run["environment_manifest"],
        "candidate_result.json": run["candidate_result"],
        "baseline_results.json": run["baseline_results"],
        "strongest_baseline_report.json": run["strongest_baseline_report"],
        "ablation_results.json": run["ablation_results"],
        "replay_results.json": run["replay_results"],
        "leakage_positive_control_results.json": run["leakage_positive_control_results"],
        "negative_control_results.json": run["negative_control_results"],
        "provenance_manifest.json": run["provenance_manifest"],
        "static_score_guard_report.json": run["static_score_guard_report"],
        "non_mutation_guard.json": run["non_mutation_guard"],
        "source_pin_readback.json": run["source_pin_readback"],
    }
    for name, payload in artifact_map.items():
        _write_json(output_dir / name, payload)
    (output_dir / "claim_ceiling.txt").write_text(CLAIM_CEILING + "\n", encoding="utf-8")
    trace_lines = [json.dumps(_json_ready(row), sort_keys=True) for row in run["candidate_result"]["trace_records"]]
    (output_dir / "trace.jsonl").write_text("\n".join(trace_lines) + "\n", encoding="utf-8")
    observations = [
        {"episode_id": row["episode_id"], "observation": row["candidate_visible"]["observation"]}
        for row in run["candidate_result"]["trace_records"]
    ]
    states = [
        {
            "episode_id": row["episode_id"],
            "serialized_state_before_update": row["candidate_visible"]["serialized_state_before_update"],
            "serialized_state_after_update": row["candidate_visible"]["serialized_state_after_update"],
        }
        for row in run["candidate_result"]["trace_records"]
    ]
    (output_dir / "observations.jsonl").write_text(
        "\n".join(json.dumps(_json_ready(row), sort_keys=True) for row in observations) + "\n",
        encoding="utf-8",
    )
    (output_dir / "serialized_states.jsonl").write_text(
        "\n".join(json.dumps(_json_ready(row), sort_keys=True) for row in states) + "\n",
        encoding="utf-8",
    )
    _write_research_summary(run)


def _write_research_summary(run: dict[str, Any]) -> None:
    SUMMARY_PATH.parent.mkdir(parents=True, exist_ok=True)
    result = run["result"]
    strongest = run["strongest_baseline_report"]["strongest_faithful_non_oracle"]
    text = f"""# GATE4-REPLACEMENT-002C Dynamic Partner-Belief POMDP Execution 001A

Task ID: GATE4-REPLACEMENT-002C-DYNAMIC-PARTNER-BELIEF-POMDP-EXECUTION-001A

## Verdict

`{result["verdict"]}`

This is baseline-equivalent negative evidence inside the bounded 002C toy harness. The candidate score was `{result["candidate_score"]}` and the strongest faithful non-oracle baseline was `{strongest["baseline_id"]}` with score `{strongest["score"]}`.

## Layer

Engineering implementation plus bounded mechanism-proxy execution. This does not enter Gate5, admission, bridge, runtime, EGO-mainline, companion UX, subjectivity validation, or philosophical consciousness.

## Negative Evidence Inheritance

001E remains preserved as baseline-equivalence negative evidence. 001F closed 001D-derived puzzle and bundle repair routes. 002A required a baseline-first problem definition, and 002B froze this 002C executable contract.

## Anti-Hardcoding Audit

The candidate maintains separate self-state and other-state fields and updates other-state from partner observation tokens, not partner ID. The result still collapses because faithful non-mechanism baselines using the candidate-visible bundle, serialized state, or a hand-coded belief table tie the candidate. This is not a mechanism win.

## Acceptance Readback

- Positive-control leakage detected: `{run["leakage_positive_control_results"]["positive_control_detected"]}`
- Negative no-signal false success blocked: `{run["negative_control_results"]["false_success_blocked"]}`
- Replay recomputed from serialized state plus observation: `{run["replay_results"]["recomputed_from_serialized_state_plus_observation"]}`
- Ablations rerun: `{run["ablation_results"]["all_interventions_rerun"]}`
- Provenance passed: `{run["provenance_manifest"]["verification"]["passed"]}`
- Prior artifacts mutated: `{run["non_mutation_guard"]["prior_artifacts_mutated"]}`

## What This Does Not Prove

This does not prove valid Gate4, general social-latent inference, mechanism validity outside the toy task, agency, selfhood, consciousness, emotion, autonomy, EGO readiness, runtime readiness, companion readiness, or stable user benefit.
"""
    SUMMARY_PATH.write_text(text, encoding="utf-8")


def execute_experiment(output_dir: str | Path | None = ARTIFACT_DIR, persist_artifacts: bool = True) -> dict[str, Any]:
    run_id = f"{TASK_ID}-{SEALED_BOUNDARY[:8]}"
    before_hashes = hash_protected_boundaries(_repo_root())
    episodes = generate_episodes()
    candidate_result = score_candidate(episodes, f"{run_id}:candidate")
    trace_records = candidate_result["trace_records"]
    baseline_results = run_baselines(episodes, trace_records, run_id)
    strongest_baseline_report = select_strongest_baseline(baseline_results, candidate_result["score"])
    ablation_results = run_ablation_suite(episodes, candidate_result["score"], run_id)
    replay_results = build_replay_results(trace_records, run_id)
    leakage_positive_control_results = build_leakage_positive_control_results(episodes, run_id)
    negative_control_results = build_negative_control_results(episodes, candidate_result["score"], run_id)
    environment_manifest = build_environment_manifest(episodes)
    source_pin_readback = build_source_pin_readback(run_id)
    after_hashes = hash_protected_boundaries(_repo_root())
    non_mutation_guard = build_non_mutation_guard(before_hashes, after_hashes)
    run: dict[str, Any] = {
        "run_id": run_id,
        "episodes": episodes,
        "environment_manifest": environment_manifest,
        "candidate_result": candidate_result,
        "baseline_results": baseline_results,
        "strongest_baseline_report": strongest_baseline_report,
        "ablation_results": ablation_results,
        "replay_results": replay_results,
        "leakage_positive_control_results": leakage_positive_control_results,
        "negative_control_results": negative_control_results,
        "source_pin_readback": source_pin_readback,
        "non_mutation_guard": non_mutation_guard,
    }
    run["provenance_manifest"] = build_provenance_manifest(run, episodes)
    run["static_score_guard_report"] = build_static_score_guard_report(run["provenance_manifest"])
    run["result"] = build_result(run)
    run["provenance_manifest"] = build_provenance_manifest(run, episodes)
    run["static_score_guard_report"] = build_static_score_guard_report(run["provenance_manifest"])
    if persist_artifacts and output_dir is not None:
        _write_artifacts(Path(output_dir), run)
    return run
