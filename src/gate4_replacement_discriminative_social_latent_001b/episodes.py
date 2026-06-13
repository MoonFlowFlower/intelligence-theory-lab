from __future__ import annotations

from collections import Counter
from typing import Any

from .schemas import EpisodeRecord, Observation


MANDATORY_SPLITS = [
    "seen_partner_unseen_context",
    "unseen_partner_seen_context",
    "unseen_partner_unseen_context",
    "unseen_preference_transition",
    "counterfactual_intervention",
    "active_query_required_episodes",
    "heldout_episodes_with_remapped_ids",
]
FROZEN_SEED_IDS = [f"seed_{idx}" for idx in range(5)]
ACTIONS = ["direct_response", "reflective_question", "boundary_option", "planning_summary"]


def generate_episode_records() -> tuple[dict[str, Any], list[EpisodeRecord]]:
    train_context_ids = [f"train_context_{idx}" for idx in range(len(MANDATORY_SPLITS))]
    heldout_context_ids = [f"heldout_context_{idx}" for idx in range(len(MANDATORY_SPLITS))]
    counterfactual_pair_ids = [f"cf_pair_{idx}" for idx in range(len(MANDATORY_SPLITS))]
    remapped_episode_ids = [f"remap_{idx}" for idx in range(len(FROZEN_SEED_IDS))]
    records: list[EpisodeRecord] = []

    for split_index, split in enumerate(MANDATORY_SPLITS):
        for seed_index, seed_id in enumerate(FROZEN_SEED_IDS):
            action_index = (split_index + seed_index) % len(ACTIONS)
            target = ACTIONS[action_index]
            wrong_hint = ACTIONS[(action_index + 1) % len(ACTIONS)]
            context_id = f"context_raw_{split_index}_{seed_index}"
            partner_id = f"partner_raw_{seed_index}_{split_index}"
            episode_id = f"{split}_{seed_id}"
            counterfactual = ACTIONS[(action_index + 2) % len(ACTIONS)]
            legal_history = [{"event": "prior_preference_seen", "value": "ambiguous"}]
            observation = Observation(
                observable_partner=f"partner_alias_{seed_index % 3}",
                observable_context=f"context_alias_{split_index}",
                prompt_features={
                    "topic": f"topic_{split_index % 3}",
                    "tone": "direct" if split_index % 2 == 0 else "exploratory",
                    "baseline_hint": wrong_hint,
                    "query_available": True,
                },
                legal_history=legal_history,
            )
            records.append(
                EpisodeRecord(
                    episode_id=episode_id,
                    seed_id=seed_id,
                    split_family=split,
                    context_id=context_id,
                    partner_id=partner_id,
                    train_context_id=train_context_ids[split_index],
                    heldout_context_id=heldout_context_ids[split_index],
                    target_action=target,
                    query_feedback=f"prefers:{target}",
                    counterfactual_feedback=f"prefers:{counterfactual}",
                    counterfactual_pair_id=counterfactual_pair_ids[split_index],
                    remapped_episode_id=remapped_episode_ids[seed_index]
                    if split == "heldout_episodes_with_remapped_ids"
                    else None,
                    observation=observation,
                )
            )

    manifest = {
        "task_id": "gate4_replacement_discriminative_social_latent_001b",
        "split_families": list(MANDATORY_SPLITS),
        "frozen_seed_ids": list(FROZEN_SEED_IDS),
        "train_context_ids": train_context_ids,
        "heldout_context_ids": heldout_context_ids,
        "counterfactual_pair_ids": counterfactual_pair_ids,
        "remapped_episode_ids": remapped_episode_ids,
        "generation_rule": "cartesian split by five frozen seeds with active query feedback available",
    }
    return manifest, records


def compute_split_coverage(manifest: dict[str, Any], episode_records: list[EpisodeRecord]) -> dict[str, Any]:
    used_splits = sorted({row.split_family for row in episode_records})
    used_seeds = sorted({row.seed_id for row in episode_records})
    used_train = sorted({row.train_context_id for row in episode_records})
    used_heldout = sorted({row.heldout_context_id for row in episode_records})
    used_counterfactual = sorted({row.counterfactual_pair_id for row in episode_records if row.counterfactual_pair_id})
    used_remapped = sorted({row.remapped_episode_id for row in episode_records if row.remapped_episode_id})
    split_counts = Counter(row.split_family for row in episode_records)

    unused_splits = sorted(set(manifest["split_families"]) - set(used_splits))
    unused_seeds = sorted(set(manifest["frozen_seed_ids"]) - set(used_seeds))
    unused_train = sorted(set(manifest["train_context_ids"]) - set(used_train))
    unused_heldout = sorted(set(manifest["heldout_context_ids"]) - set(used_heldout))
    unused_counterfactual = sorted(set(manifest["counterfactual_pair_ids"]) - set(used_counterfactual))
    unused_remapped = sorted(set(manifest["remapped_episode_ids"]) - set(used_remapped))
    positive = not any(
        [
            unused_splits,
            unused_seeds,
            unused_train,
            unused_heldout,
            unused_counterfactual,
            unused_remapped,
        ]
    )
    return {
        "producer_function": "compute_split_coverage",
        "used_split_families": used_splits,
        "split_counts": dict(split_counts),
        "unused_split_families": unused_splits,
        "unused_frozen_seed_ids": unused_seeds,
        "unused_train_context_ids": unused_train,
        "unused_heldout_context_ids": unused_heldout,
        "unused_counterfactual_pair_ids": unused_counterfactual,
        "unused_remapped_episode_ids": unused_remapped,
        "positive_evidence_allowed": positive,
    }
