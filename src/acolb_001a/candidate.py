from copy import deepcopy

from .config import ACTION_BASIS, DEFAULT_DECAY, OBS_VAR, PRIOR_VAR
from .linear import dot, mat_vec
from .provenance import code_path_hash


def init_state(decay: float = DEFAULT_DECAY) -> dict:
    return {
        "posterior_mean": [0.0, 0.0],
        "posterior_cov": [[PRIOR_VAR, 0.0], [0.0, PRIOR_VAR]],
        "n_updates": 0,
        "last_pred_error": 0.0,
        "decay": decay,
        "uses_hidden_truth_labels": False,
        "uses_future_observations": False,
        "candidate_authored_truth": False,
        "state_size_class": "O(d^2)",
    }


def _feature(action: str, variant: str) -> tuple[float, float]:
    if variant == "no_action_conditioning":
        return (1.0, 1.0)
    return ACTION_BASIS[action]


def predict_outcome(state: dict, action: str, variant: str = "candidate") -> float:
    return dot(state["posterior_mean"], _feature(action, variant))


def update_state(
    state: dict,
    action: str,
    outcome: float,
    variant: str = "candidate",
    decay: float | None = None,
) -> dict:
    next_state = deepcopy(state)
    if variant == "no_update":
        return next_state
    active_decay = decay if decay is not None else next_state.get("decay", DEFAULT_DECAY)
    x = _feature(action, variant)
    pred = predict_outcome(next_state, action, variant)
    error = 0.0 if variant == "no_PE_correction" else outcome - pred
    p = [[cell / active_decay for cell in row] for row in next_state["posterior_cov"]]
    px = mat_vec(p, x)
    denom = dot(x, px) + OBS_VAR
    gain = [px[0] / denom, px[1] / denom]
    next_state["posterior_mean"] = [
        next_state["posterior_mean"][0] + gain[0] * error,
        next_state["posterior_mean"][1] + gain[1] * error,
    ]
    next_state["posterior_cov"] = [
        [p[0][0] - gain[0] * (x[0] * p[0][0] + x[1] * p[1][0]), p[0][1] - gain[0] * (x[0] * p[0][1] + x[1] * p[1][1])],
        [p[1][0] - gain[1] * (x[0] * p[0][0] + x[1] * p[1][0]), p[1][1] - gain[1] * (x[0] * p[0][1] + x[1] * p[1][1])],
    ]
    next_state["decay"] = active_decay
    next_state["n_updates"] += 1
    next_state["last_pred_error"] = error
    return next_state


def serialize_state(state: dict) -> dict:
    allowed = {
        "posterior_mean",
        "posterior_cov",
        "n_updates",
        "last_pred_error",
        "decay",
        "uses_hidden_truth_labels",
        "uses_future_observations",
        "candidate_authored_truth",
        "state_size_class",
    }
    return {key: deepcopy(value) for key, value in state.items() if key in allowed}


def run_candidate(
    legal_episode: dict,
    variant: str = "candidate",
    freeze_until: int | None = None,
    decay: float = DEFAULT_DECAY,
) -> dict:
    state = init_state(decay=decay)
    initial_state = serialize_state(state)
    trace = []
    for idx, obs in enumerate(legal_episode["probes"]):
        before = serialize_state(state)
        pred = predict_outcome(state, obs["action"], variant)
        if freeze_until is not None and idx < freeze_until:
            after = deepcopy(state)
        else:
            after = update_state(state, obs["action"], obs["outcome"], variant, decay=decay)
        trace.append(
            {
                "episode_id": legal_episode["episode_id"],
                "t": obs["t"],
                "action": obs["action"],
                "belief_before": before["posterior_mean"],
                "predicted_outcome": pred,
                "actual_outcome": obs["outcome"],
                "prediction_error": obs["outcome"] - pred,
                "belief_after": after["posterior_mean"],
                "n_updates": after["n_updates"],
                "code_path_hash": code_path_hash(update_state),
            }
        )
        state = after
    serialized = serialize_state(state)
    predictions = {}
    query_rows = []
    for query in legal_episode["queries"]:
        pred = predict_outcome(serialized, query["query_action"], variant)
        predictions[query["q_id"]] = pred
        query_rows.append(
            {
                "episode_id": legal_episode["episode_id"],
                "q_id": query["q_id"],
                "query_action": query["query_action"],
                "query_context": query["query_context"],
                "predicted_outcome": pred,
                "counterfactual_action_preds": {
                    action: predict_outcome(serialized, action, variant)
                    for action in query["counterfactual_actions"]
                },
                "code_path_hash": code_path_hash(predict_outcome),
            }
        )
    return {
        "producer_function": "run_candidate",
        "variant": variant,
        "decay": decay,
        "initial_state": initial_state,
        "serialized_state": serialized,
        "predictions": predictions,
        "trace": trace,
        "query_trace": query_rows,
        "uses_future_observations": False,
        "code_path_hash": code_path_hash(run_candidate),
    }
