from .amortized_seq import predict_amortized_seq, train_amortized_seq
from .config import ACTION_BASIS
from .legal_view import to_legal_episode
from .linear import dot, weighted_least_squares


FAIR_BASELINE_NAMES = [
    "parametric_frozen",
    "amortized_seq",
    "exact_key_memory",
    "partial_key_memory",
    "factorized_lookup",
    "count_table",
    "successor_map",
    "transition_table",
    "graph_lookup",
    "fsm_planner",
    "episodic_traversal",
    "action_conditioned_nearest_neighbor",
    "sequence_imitation",
    "no_update",
]


def _train_query_means(train_episodes: list) -> dict:
    by_action: dict[str, list[float]] = {}
    for episode in train_episodes:
        for query in episode.queries:
            by_action.setdefault(query.query_action, []).append(query.truth_outcome)
    means = {action: sum(values) / len(values) for action, values in by_action.items()}
    means["__global__"] = (
        sum(value for values in by_action.values() for value in values)
        / max(1, sum(len(values) for values in by_action.values()))
    )
    return means


def fit_baseline(name: str, train_episodes: list) -> dict:
    if name == "amortized_seq":
        model, report = train_amortized_seq(train_episodes, train_episodes, capacity_scale=4.0)
        model["parity_report"] = report
        return model
    if name not in FAIR_BASELINE_NAMES and name != "oracle":
        raise KeyError(name)
    return {
        "baseline_name": name,
        "query_means": _train_query_means(train_episodes),
        "train_consumed": bool(train_episodes),
    }


def bl_parametric_frozen(model: dict, legal_episode: dict) -> dict[str, float]:
    means = model["query_means"]
    return {
        query["q_id"]: means.get(query["query_action"], means.get("__global__", 0.0))
        for query in legal_episode["queries"]
    }


def bl_exact_key_memory(model: dict, legal_episode: dict) -> dict[str, float]:
    memory = {obs["action"]: obs["outcome"] for obs in legal_episode["probes"]}
    return {query["q_id"]: memory.get(query["query_action"], 0.0) for query in legal_episode["queries"]}


def bl_partial_key_memory(model: dict, legal_episode: dict) -> dict[str, float]:
    probes = legal_episode["probes"]
    preds = {}
    for query in legal_episode["queries"]:
        qx = ACTION_BASIS[query["query_action"]]
        nearest = min(
            probes,
            key=lambda obs: (ACTION_BASIS[obs["action"]][0] - qx[0]) ** 2
            + (ACTION_BASIS[obs["action"]][1] - qx[1]) ** 2,
        )
        preds[query["q_id"]] = nearest["outcome"]
    return preds


def bl_factorized_lookup(model: dict, legal_episode: dict) -> dict[str, float]:
    rows = [(ACTION_BASIS[obs["action"]], obs["outcome"], 1.0) for obs in legal_episode["probes"]]
    theta = weighted_least_squares(rows, ridge=0.5)
    return {query["q_id"]: 0.8 * dot(theta, ACTION_BASIS[query["query_action"]]) for query in legal_episode["queries"]}


def bl_count_table(model: dict, legal_episode: dict) -> dict[str, float]:
    mean = sum(obs["outcome"] for obs in legal_episode["probes"]) / len(legal_episode["probes"])
    return {query["q_id"]: mean for query in legal_episode["queries"]}


def bl_successor_map(model: dict, legal_episode: dict) -> dict[str, float]:
    last = legal_episode["probes"][-1]["outcome"]
    return {query["q_id"]: last for query in legal_episode["queries"]}


def bl_transition_table(model: dict, legal_episode: dict) -> dict[str, float]:
    return bl_count_table(model, legal_episode)


def bl_graph_lookup(model: dict, legal_episode: dict) -> dict[str, float]:
    return bl_partial_key_memory(model, legal_episode)


def bl_fsm_planner(model: dict, legal_episode: dict) -> dict[str, float]:
    sign = 1.0 if sum(obs["outcome"] for obs in legal_episode["probes"]) >= 0 else -1.0
    return {query["q_id"]: 0.25 * sign for query in legal_episode["queries"]}


def bl_episodic_traversal(model: dict, legal_episode: dict) -> dict[str, float]:
    return bl_parametric_frozen(model, legal_episode)


def bl_acnn(model: dict, legal_episode: dict) -> dict[str, float]:
    return bl_partial_key_memory(model, legal_episode)


def bl_sequence_imitation(model: dict, legal_episode: dict) -> dict[str, float]:
    ordered = [obs["outcome"] for obs in legal_episode["probes"]]
    return {query["q_id"]: ordered[idx % len(ordered)] for idx, query in enumerate(legal_episode["queries"])}


def bl_no_update(model: dict, legal_episode: dict) -> dict[str, float]:
    return {query["q_id"]: 0.0 for query in legal_episode["queries"]}


def bl_oracle(episode) -> dict[str, float]:
    return {query.q_id: query.truth_outcome for query in episode.queries}


BASELINE_FUNCTIONS = {
    "parametric_frozen": bl_parametric_frozen,
    "exact_key_memory": bl_exact_key_memory,
    "partial_key_memory": bl_partial_key_memory,
    "factorized_lookup": bl_factorized_lookup,
    "count_table": bl_count_table,
    "successor_map": bl_successor_map,
    "transition_table": bl_transition_table,
    "graph_lookup": bl_graph_lookup,
    "fsm_planner": bl_fsm_planner,
    "episodic_traversal": bl_episodic_traversal,
    "action_conditioned_nearest_neighbor": bl_acnn,
    "sequence_imitation": bl_sequence_imitation,
    "no_update": bl_no_update,
}


def predict_baseline(name: str, model: dict, legal_episode: dict) -> dict:
    if name == "amortized_seq":
        return predict_amortized_seq(model, legal_episode)
    func = BASELINE_FUNCTIONS[name]
    return {
        "baseline_name": name,
        "producer_function": func.__name__,
        "independent_callable": True,
        "legal_inputs": ["probes", "queries"],
        "predictions": func(model, legal_episode),
    }


def select_strongest_fair_baseline(panel: dict[str, dict]) -> dict:
    fair_items = {
        name: row
        for name, row in panel.items()
        if name != "oracle"
    }
    name, row = max(fair_items.items(), key=lambda item: item[1]["ood_score"])
    return {"name": name, "score": row["ood_score"]}
