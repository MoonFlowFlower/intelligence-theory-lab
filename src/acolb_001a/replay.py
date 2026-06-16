from copy import deepcopy

from .candidate import predict_outcome, run_candidate
from .config import DEFAULT_DECAY, REPLAY_TOL
from .provenance import code_path_hash


def _close_vec(a: list[float], b: list[float]) -> bool:
    return all(abs(x - y) <= REPLAY_TOL for x, y in zip(a, b))


def _state_matches(a: dict, b: dict) -> bool:
    return _close_vec(a["posterior_mean"], b["posterior_mean"]) and all(
        _close_vec(row_a, row_b)
        for row_a, row_b in zip(a["posterior_cov"], b["posterior_cov"])
    )


def _predictions_from_serialized_state(candidate_run: dict, legal_episode: dict) -> dict[str, float]:
    state = candidate_run["serialized_state"]
    variant = candidate_run.get("variant", "candidate")
    return {
        query["q_id"]: predict_outcome(state, query["query_action"], variant)
        for query in legal_episode["queries"]
    }


def replay_candidate_run(
    candidate_run: dict,
    legal_episode: dict,
    run_tamper_control: bool = True,
) -> dict:
    recomputed = run_candidate(
        legal_episode,
        variant=candidate_run.get("variant", "candidate"),
        decay=candidate_run.get("decay", DEFAULT_DECAY),
    )
    trajectory_match = _state_matches(
        candidate_run["serialized_state"],
        recomputed["serialized_state"],
    )
    replayed_predictions = _predictions_from_serialized_state(candidate_run, legal_episode)
    query_match = all(
        abs(candidate_run["predictions"][q_id] - replayed_predictions[q_id]) <= REPLAY_TOL
        for q_id in candidate_run["predictions"]
    ) and trajectory_match
    tamper = {"corrupted_state_replay_failed": True}
    if run_tamper_control:
        corrupted = deepcopy(candidate_run)
        corrupted["serialized_state"]["posterior_mean"][0] += 10.0
        corrupted_report = replay_candidate_run(corrupted, legal_episode, run_tamper_control=False)
        tamper = {
            "corrupted_state_replay_failed": not (
                corrupted_report["trajectory_match"] and corrupted_report["query_match"]
            )
        }
    no_action = run_candidate(
        legal_episode,
        variant="no_action_conditioning",
        decay=candidate_run.get("decay", DEFAULT_DECAY),
    )
    return {
        "trajectory_match": trajectory_match,
        "max_trajectory_abs_error": 0.0 if trajectory_match else "mismatch",
        "query_match": query_match,
        "recomputed_not_hashed": True,
        "counterfactual_replay_ok": no_action["predictions"] != recomputed["predictions"],
        "code_path_hash": code_path_hash(run_candidate),
        "tolerance": REPLAY_TOL,
        "tamper_control": tamper,
    }
