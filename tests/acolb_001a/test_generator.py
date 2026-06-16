import json

from acolb_001a.config import SEED_FAMILIES
from acolb_001a.generator import build_dataset, generate_episode
from acolb_001a.legal_view import FORBIDDEN_LEGAL_KEYS, to_legal_episode


def test_generator_is_deterministic_and_keeps_query_actions_disjoint():
    first = generate_episode("id", SEED_FAMILIES["id_test"][0], 0)
    second = generate_episode("id", SEED_FAMILIES["id_test"][0], 0)

    assert first == second
    assert {step.action for step in first.probes}.isdisjoint(
        {query.query_action for query in first.queries}
    )


def test_legal_episode_excludes_oracle_fields():
    episode = generate_episode("ood", SEED_FAMILIES["ood_test"][0], 0)
    legal = to_legal_episode(episode)
    payload = json.dumps(legal, sort_keys=True)

    for forbidden in FORBIDDEN_LEGAL_KEYS:
        assert forbidden not in payload


def test_seed_families_are_disjoint_and_training_consumes_multiple_contexts():
    families = list(SEED_FAMILIES.values())
    flattened = [seed for family in families for seed in family]

    assert len(flattened) == len(set(flattened))
    assert len(build_dataset("train", SEED_FAMILIES["train"][:2], episodes_per_seed=2)) == 4
