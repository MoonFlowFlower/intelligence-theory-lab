from acolb_001a.amortized_seq import train_amortized_seq
from acolb_001a.config import SEED_FAMILIES
from acolb_001a.generator import build_dataset


def test_amortized_seq_records_learning_curve_and_converges():
    train = build_dataset("train", SEED_FAMILIES["train"][:3], episodes_per_seed=2)
    validation = build_dataset("id", SEED_FAMILIES["validation"][:2], episodes_per_seed=2)
    model, report = train_amortized_seq(train, validation, capacity_scale=4.0)

    assert model["model_type"] == "amortized_seq"
    assert report["procedure_kind"] == "weighted_batch_wls_decay_grid_selection"
    assert report["convergence_claim"] == "not_applicable_non_training_grid_selection"
    assert report["selection_complete"] is True
    assert report["capacity_parity"]["parity_ok"] is True
    assert len({row["decay"] for row in report["selection_curve"]}) == len(report["selection_curve"])
    assert len(report["id_score_per_seed"]) >= 3
    assert len(report["ood_score_per_seed"]) >= 3


def test_capacity_parity_failure_is_computed():
    train = build_dataset("train", SEED_FAMILIES["train"][:1], episodes_per_seed=1)
    validation = build_dataset("id", SEED_FAMILIES["validation"][:1], episodes_per_seed=1)
    _, report = train_amortized_seq(train, validation, capacity_scale=0.1)

    assert report["capacity_parity"]["parity_ok"] is False
    assert report["capacity_parity"]["amortized_capacity"] < report["capacity_parity"]["candidate_capacity"]
