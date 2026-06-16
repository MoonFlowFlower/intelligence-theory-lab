from .schemas import Episode


LEGAL_KEYS = {
    "episode_id",
    "regime",
    "seed",
    "t",
    "action",
    "outcome",
    "q_id",
    "query_action",
    "query_context",
    "counterfactual_actions",
}

FORBIDDEN_LEGAL_KEYS = {
    "theta",
    "latent",
    "latent_at_t",
    "pe_truth",
    "truth",
    "truth_outcome",
    "truth_producer",
    "dynamics_params",
    "outcome_fn_id",
}


def to_legal_episode(episode: Episode) -> dict:
    return {
        "episode_id": episode.episode_id,
        "regime": episode.regime,
        "seed": episode.seed,
        "probes": [
            {
                "episode_id": episode.episode_id,
                "regime": episode.regime,
                "seed": episode.seed,
                "t": step.t,
                "action": step.action,
                "outcome": step.outcome,
            }
            for step in episode.probes
        ],
        "queries": [
            {
                "episode_id": episode.episode_id,
                "regime": episode.regime,
                "seed": episode.seed,
                "q_id": query.q_id,
                "query_action": query.query_action,
                "query_context": query.query_context,
                "counterfactual_actions": [
                    other.query_action
                    for other in episode.queries
                    if other.query_action != query.query_action
                ],
            }
            for query in episode.queries
        ],
    }
