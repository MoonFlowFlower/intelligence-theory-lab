import json
from pathlib import Path

from .amortized_seq import predict_amortized_seq, score_episodes_with_decay, train_amortized_seq
from .baselines import FAIR_BASELINE_NAMES, fit_baseline, predict_baseline, select_strongest_fair_baseline
from .candidate import run_candidate
from .config import ARTIFACT_DIR, EQUIV_BAND, OOD_BAND, SEED_FAMILIES
from .generator import build_dataset
from .legal_view import to_legal_episode
from .scoring import aggregate_episode_scores, score_episode_predictions


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, sort_keys=True, indent=2) + "\n", encoding="utf-8")


def _score_candidate(episodes: list, decay: float) -> dict:
    scores = []
    for episode in episodes:
        result = run_candidate(to_legal_episode(episode), decay=decay)
        scores.append(score_episode_predictions(episode, result["predictions"], producer="candidate"))
    return aggregate_episode_scores(scores, "candidate")


def _score_amortized(model: dict, episodes: list) -> dict:
    scores = []
    for episode in episodes:
        result = predict_amortized_seq(model, to_legal_episode(episode))
        scores.append(score_episode_predictions(episode, result["predictions"], producer="amortized_seq"))
    return aggregate_episode_scores(scores, "amortized_seq")


def _score_amortized_by_seed(model: dict, episodes: list) -> dict[int, float]:
    grouped: dict[int, list] = {}
    for episode in episodes:
        grouped.setdefault(episode.seed, []).append(episode)
    return {
        seed: _score_amortized(model, grouped_episodes)["score"]
        for seed, grouped_episodes in grouped.items()
    }


def _score_named_baseline(name: str, model: dict, episodes: list) -> dict:
    scores = []
    for episode in episodes:
        result = predict_baseline(name, model, to_legal_episode(episode))
        scores.append(score_episode_predictions(episode, result["predictions"], producer=name))
    return aggregate_episode_scores(scores, name)


def _score_oracle(episodes: list) -> dict:
    scores = []
    for episode in episodes:
        predictions = {query.q_id: query.truth_outcome for query in episode.queries}
        scores.append(score_episode_predictions(episode, predictions, producer="oracle"))
    return aggregate_episode_scores(scores, "oracle")


def _failure_manifest(verdict: str) -> dict:
    reason = {
        "saturated_close": "blocked_by_saturated_distribution",
        "baseline_equivalent": "blocked_by_baseline_equivalence",
        "parity_broken_close": "blocked_by_underpowered_or_unfair_amortized_baseline",
    }[verdict]
    return {
        "verdict": verdict,
        "stop_conditions": [reason],
        "claim_ceiling": "Phase 0 blocker evidence only; no mechanism claim",
    }


def _select_sensitivity_row(rows: list[dict], rule: str) -> dict:
    if rule == "drift_aware_validation":
        return max(rows, key=lambda row: (row["drift_validation_score"], row["id_validation_score"]))
    if rule == "id_validation_min_loss":
        return min(rows, key=lambda row: (row["id_validation_loss"], -row["drift_validation_score"]))
    raise ValueError(rule)


def _build_fair_baseline_sensitivity(
    *,
    id_test: list,
    ood_test: list,
    train: list,
    validation: list,
    drift_validation: list,
    oracle_score: float,
    selected_decay: float,
) -> dict:
    rows = []
    for curve_row in train_amortized_seq(
        train,
        validation,
        drift_validation_episodes=drift_validation,
        selection_rule="drift_aware_validation",
    )[1]["selection_curve"]:
        decay = curve_row["decay"]
        candidate_id = _score_candidate(id_test, decay)
        candidate_ood = _score_candidate(ood_test, decay)
        amortized_id = score_episodes_with_decay(id_test, decay)
        amortized_ood = score_episodes_with_decay(ood_test, decay)
        margin = candidate_ood["score"] - amortized_ood["score"]
        headroom = oracle_score - amortized_ood["score"]
        rows.append(
            {
                "decay": decay,
                "candidate_id_score": candidate_id["score"],
                "candidate_ood_score": candidate_ood["score"],
                "amortized_id_score": amortized_id["score"],
                "amortized_ood_score": amortized_ood["score"],
                "id_validation_loss": curve_row["id_validation_loss"],
                "id_validation_score": curve_row["id_validation_score"],
                "drift_validation_loss": curve_row["drift_validation_loss"],
                "drift_validation_score": curve_row["drift_validation_score"],
                "legal_for_baseline": curve_row["legal_for_baseline"],
                "selected_for_candidate": decay == selected_decay,
                "selected_for_fair_amortized": decay == selected_decay,
                "margin": margin,
                "headroom": headroom,
                "baseline_equivalent": margin <= OOD_BAND,
                "saturated_close": headroom <= EQUIV_BAND,
            }
        )
    id_selected = _select_sensitivity_row(rows, "id_validation_min_loss")
    drift_selected = _select_sensitivity_row(rows, "drift_aware_validation")
    return {
        "artifact_type": "fair_baseline_sensitivity",
        "aggregation_rule": "mean_episode_score",
        "candidate_decay": selected_decay,
        "fair_amortized_decay": selected_decay,
        "selected_rules": {
            "id_validation_min_loss": {
                "decay": id_selected["decay"],
                "selection_metric": "minimum_id_validation_loss",
            },
            "drift_aware_validation": {
                "decay": drift_selected["decay"],
                "selection_metric": "maximum_drift_validation_score_then_id_score",
            },
        },
        "decay_candidates": rows,
    }


def run_headroom_preflight(output_dir: str | Path = ARTIFACT_DIR, fixture: str = "normal") -> dict:
    output_path = Path(output_dir)
    train = build_dataset("train", SEED_FAMILIES["train"], episodes_per_seed=2)
    validation = build_dataset("id", SEED_FAMILIES["validation"], episodes_per_seed=1)
    drift_validation = build_dataset("ood", SEED_FAMILIES["validation"], episodes_per_seed=1)
    id_test = build_dataset("id", SEED_FAMILIES["id_test"], episodes_per_seed=1)
    ood_test = build_dataset("ood", SEED_FAMILIES["ood_test"], episodes_per_seed=1)

    capacity_scale = 0.1 if fixture == "parity_broken" else 4.0
    amortized_model, parity_report = train_amortized_seq(
        train,
        validation,
        drift_validation_episodes=drift_validation,
        capacity_scale=capacity_scale,
        selection_rule="drift_aware_validation",
    )
    selected_decay = amortized_model["decay"]

    candidate_id = _score_candidate(id_test, selected_decay)
    candidate_ood = _score_candidate(ood_test, selected_decay)
    amortized_id = _score_amortized(amortized_model, id_test)
    amortized_ood = _score_amortized(amortized_model, ood_test)
    id_scores_by_seed = _score_amortized_by_seed(amortized_model, id_test)
    ood_scores_by_seed = _score_amortized_by_seed(amortized_model, ood_test)
    parity_report["id_score"] = amortized_id["score"]
    parity_report["ood_score"] = amortized_ood["score"]
    parity_report["id_score_per_seed"] = list(id_scores_by_seed.values())
    parity_report["ood_score_per_seed"] = list(ood_scores_by_seed.values())
    parity_report["ood_score_max"] = max(ood_scores_by_seed.values())
    parity_report["aggregation_rule"] = "mean_episode_score"

    baseline_panel = {
        "amortized_seq": {
            "id_score": amortized_id["score"],
            "ood_score": amortized_ood["score"],
            "decay": selected_decay,
            "producer_function": "bl_amortized_seq",
        }
    }
    for name in FAIR_BASELINE_NAMES:
        if name == "amortized_seq":
            continue
        model = fit_baseline(name, train)
        ood_score = _score_named_baseline(name, model, ood_test)
        baseline_panel[name] = {
            "ood_score": ood_score["score"],
            "producer_function": f"bl_{name}" if name != "action_conditioned_nearest_neighbor" else "bl_acnn",
        }
    oracle = _score_oracle(ood_test)
    no_update_floor = baseline_panel["no_update"]["ood_score"]

    if fixture == "saturated":
        baseline_panel["parametric_frozen"]["ood_score"] = oracle["score"]

    sensitivity = _build_fair_baseline_sensitivity(
        id_test=id_test,
        ood_test=ood_test,
        train=train,
        validation=validation,
        drift_validation=drift_validation,
        oracle_score=oracle["score"],
        selected_decay=selected_decay,
    )
    selected = select_strongest_fair_baseline(baseline_panel | {"oracle": {"ood_score": oracle["score"]}})
    headroom = oracle["score"] - selected["score"]
    margin = candidate_ood["score"] - selected["score"]
    id_negative_control_pass = abs(candidate_id["score"] - amortized_id["score"]) <= EQUIV_BAND
    parity_ok = parity_report["capacity_parity"]["parity_ok"] and parity_report["selection_complete"]

    if not parity_ok or not id_negative_control_pass:
        verdict = "parity_broken_close"
    elif selected["score"] >= oracle["score"] - EQUIV_BAND or headroom <= EQUIV_BAND:
        verdict = "saturated_close"
    elif margin <= OOD_BAND:
        verdict = "baseline_equivalent"
    else:
        verdict = "headroom_present"

    result = {
        "verdict": verdict,
        "fixture": fixture,
        "candidate_evidence_reached": False,
        "candidate_id_score": candidate_id["score"],
        "candidate_ood_score": candidate_ood["score"],
        "candidate_decay": selected_decay,
        "fair_amortized_decay": selected_decay,
        "amortized_seq_id_score": amortized_id["score"],
        "amortized_seq_ood_score": amortized_ood["score"],
        "strongest_fair_baseline_name": selected["name"],
        "strongest_fair_baseline_score": selected["score"],
        "oracle_ceiling_score": oracle["score"],
        "no_update_floor_score": no_update_floor,
        "headroom": headroom,
        "margin": margin,
        "band": EQUIV_BAND,
        "ood_band": OOD_BAND,
        "aggregation_rule": "mean_episode_score",
        "selected_decay_rule": "drift_aware_validation",
        "id_negative_control_pass": id_negative_control_pass,
        "parity_ok": parity_report["capacity_parity"]["parity_ok"],
        "selection_complete": parity_report["selection_complete"],
        "convergence_claim": parity_report["convergence_claim"],
        "stop_conditions": [] if verdict == "headroom_present" else _failure_manifest(verdict)["stop_conditions"],
        "baseline_panel": baseline_panel,
    }
    _write_json(output_path / "headroom_preflight.json", result)
    _write_json(output_path / "baseline_comparison.json", {"baselines": baseline_panel, "selected": selected})
    _write_json(output_path / "fair_baseline_sensitivity.json", sensitivity)
    _write_json(output_path / "parity_report.json", parity_report)
    if verdict != "headroom_present":
        _write_json(output_path / "failure_manifest.json", _failure_manifest(verdict))
    return result


if __name__ == "__main__":
    print(json.dumps(run_headroom_preflight(), sort_keys=True, indent=2))
