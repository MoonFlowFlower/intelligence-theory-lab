import json
from copy import deepcopy
from pathlib import Path

from .candidate import run_candidate
from .config import ARTIFACT_DIR, EQUIV_BAND, SEED_FAMILIES
from .generator import build_dataset
from .legal_view import to_legal_episode
from .provenance import code_path_hash
from .scoring import aggregate_episode_scores, score_episode_predictions


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, sort_keys=True, indent=2) + "\n", encoding="utf-8")


def _score_variant(episodes: list, variant: str, mutate=None, freeze_until: int | None = None) -> dict:
    scores = []
    for episode in episodes:
        legal = to_legal_episode(episode)
        if mutate is not None:
            legal = mutate(legal)
        result = run_candidate(legal, variant=variant, freeze_until=freeze_until)
        scores.append(score_episode_predictions(episode, result["predictions"], producer=variant))
    return aggregate_episode_scores(scores, variant)


def ablation_A1_no_update(legal_episode: dict) -> dict:
    return run_candidate(legal_episode, variant="no_update")


def ablation_A2_no_action_conditioning(legal_episode: dict) -> dict:
    return run_candidate(legal_episode, variant="no_action_conditioning")


def ablation_A3_no_pe_correction(legal_episode: dict) -> dict:
    return run_candidate(legal_episode, variant="no_PE_correction")


def ablation_A4_shuffled_labels(legal_episode: dict) -> dict:
    mutated = deepcopy(legal_episode)
    outcomes = [row["outcome"] for row in mutated["probes"]]
    shifted = list(reversed(outcomes))
    for row, outcome in zip(mutated["probes"], shifted):
        row["outcome"] = outcome
    return run_candidate(mutated)


def ablation_A5_shuffled_probe_order(legal_episode: dict) -> dict:
    mutated = deepcopy(legal_episode)
    mutated["probes"] = list(reversed(mutated["probes"]))
    return run_candidate(mutated)


def ablation_A6_frozen_posterior_pre_informative_probes(legal_episode: dict) -> dict:
    return run_candidate(legal_episode, freeze_until=len(legal_episode["probes"]) // 2)


def _score_ablation(episodes: list, ablation_id: str, function) -> dict:
    scores = []
    for episode in episodes:
        legal = to_legal_episode(episode)
        result = function(legal)
        scores.append(score_episode_predictions(episode, result["predictions"], producer=ablation_id))
    return aggregate_episode_scores(scores, ablation_id)


ABLATION_FUNCTIONS = {
    "A1": ablation_A1_no_update,
    "A2": ablation_A2_no_action_conditioning,
    "A3": ablation_A3_no_pe_correction,
    "A4": ablation_A4_shuffled_labels,
    "A5": ablation_A5_shuffled_probe_order,
    "A6": ablation_A6_frozen_posterior_pre_informative_probes,
}


def run_ablations(output_dir: str | Path = ARTIFACT_DIR) -> dict:
    output_path = Path(output_dir)
    episodes = build_dataset("ood", SEED_FAMILIES["ood_test"], episodes_per_seed=1)
    candidate = _score_variant(episodes, "candidate")
    floor = _score_variant(episodes, "no_update")
    rows = []
    for ablation_id, function in ABLATION_FUNCTIONS.items():
        score = _score_ablation(episodes, ablation_id, function)
        delta = candidate["score"] - score["score"]
        if ablation_id in {"A1", "A3", "A4"}:
            direction_ok = score["score"] <= floor["score"] + 0.05
        elif ablation_id == "A2":
            direction_ok = delta > EQUIV_BAND
        else:
            direction_ok = True
        rows.append(
            {
                "ablation_id": ablation_id,
                "rerun": True,
                "ood_score": score["score"],
                "delta_vs_candidate": delta,
                "expected_direction": "collapse_or_drop" if ablation_id in {"A1", "A2", "A3", "A4"} else "reported",
                "direction_ok": direction_ok,
                "code_path_hash": code_path_hash(function),
            }
        )
    report = {
        "candidate_ood_score": candidate["score"],
        "no_update_floor_score": floor["score"],
        "candidate_code_path_hash": code_path_hash(run_candidate),
        "ablations": rows,
    }
    _write_json(output_path / "ablation_report.json", report)
    return report
