from acolb_001a.baselines import (
    FAIR_BASELINE_NAMES,
    fit_baseline,
    predict_baseline,
    select_strongest_fair_baseline,
)
from acolb_001a.config import SEED_FAMILIES
from acolb_001a.generator import build_dataset, generate_episode
from acolb_001a.legal_view import to_legal_episode
from acolb_001a.scoring import score_episode_predictions


def test_every_fair_baseline_is_independently_callable():
    train = build_dataset("train", SEED_FAMILIES["train"][:2], episodes_per_seed=2)
    legal = to_legal_episode(generate_episode("id", SEED_FAMILIES["id_test"][0], 0))

    for name in FAIR_BASELINE_NAMES:
        model = fit_baseline(name, train)
        result = predict_baseline(name, model, legal)
        assert result["baseline_name"] == name
        assert result["independent_callable"] is True
        assert result["producer_function"].startswith("bl_")
        assert result["legal_inputs"]


def test_oracle_is_not_in_fair_baseline_argmax_selection():
    selected = select_strongest_fair_baseline(
        {
            "count_table": {"ood_score": 0.41},
            "amortized_seq": {"ood_score": 0.52},
            "oracle": {"ood_score": 1.0},
        }
    )

    assert selected["name"] == "amortized_seq"
    assert selected["score"] == 0.52


def test_exact_key_memory_fails_on_disjoint_query_actions():
    train = build_dataset("train", SEED_FAMILIES["train"][:2], episodes_per_seed=1)
    episode = generate_episode("id", SEED_FAMILIES["id_test"][0], 0)
    legal = to_legal_episode(episode)

    exact = predict_baseline("exact_key_memory", fit_baseline("exact_key_memory", train), legal)
    floor = predict_baseline("no_update", fit_baseline("no_update", train), legal)

    exact_score = score_episode_predictions(episode, exact["predictions"], producer="exact_key_memory")
    floor_score = score_episode_predictions(episode, floor["predictions"], producer="no_update")
    assert exact_score["score"] <= floor_score["score"] + 0.05
