from itl_devbench.eval.candidate_factorial import (
    compute_candidate_factorial_interactions,
    derive_candidate_factorial_verdict,
)


def test_candidate_factorial_interactions_compute_required_marginals():
    scores = {
        "families": [
            {
                "family_id": "family_a",
                "variant_scores": {
                    "011": 4.0,
                    "101": 5.0,
                    "110": 6.0,
                    "111": 9.0,
                },
            },
            {
                "family_id": "family_b",
                "variant_scores": {
                    "011": 1.0,
                    "101": 3.0,
                    "110": 2.0,
                    "111": 3.0,
                },
            },
        ]
    }

    interactions = compute_candidate_factorial_interactions(scores)

    by_family = {row["family_id"]: row for row in interactions["by_family"]}
    assert by_family["family_a"]["pe_marginal_under_memory_planning"] == 5.0
    assert by_family["family_a"]["memory_marginal_under_pe_planning"] == 4.0
    assert by_family["family_a"]["planner_read_marginal_under_pe_memory"] == 3.0
    assert by_family["family_a"]["three_way_closure_gain"] == 3.0
    assert by_family["family_b"]["three_way_closure_gain"] == 0.0
    assert interactions["aggregate"]["three_way_closure_gain_mean"] == 1.5


def test_candidate_factorial_verdict_is_computed_from_reports():
    replay = {"verdict": "replay_succeeded"}
    audit = {"verdict": "audit_succeeded"}
    source = {"candidate_source_unchanged": True, "protected_sources_unchanged": True}
    baseline = {"aggregate": {"baseline_saturated": False}}

    signal = {"aggregate": {"positive_three_way_family_count": 1, "three_way_closure_gain_mean": 0.25}}
    no_signal = {"aggregate": {"positive_three_way_family_count": 0, "three_way_closure_gain_mean": 0.0}}
    noncausal = {"aggregate": {"positive_three_way_family_count": 0, "three_way_closure_gain_mean": -1.0}}

    assert derive_candidate_factorial_verdict(replay, audit, source, baseline, signal) == "candidate_factorial_signal_detected"
    assert derive_candidate_factorial_verdict(replay, audit, source, baseline, no_signal) == "candidate_factorial_no_signal"
    assert derive_candidate_factorial_verdict(replay, audit, source, baseline, noncausal) == "candidate_factorial_ablation_noncausal"
    assert derive_candidate_factorial_verdict(replay, audit, source, {"aggregate": {"baseline_saturated": True}}, signal) == "candidate_factorial_baseline_saturated"
    assert derive_candidate_factorial_verdict({"verdict": "replay_failed_evidence_invalid"}, audit, source, baseline, signal) == "replay_failed_evidence_invalid"
    assert derive_candidate_factorial_verdict(replay, {"verdict": "audit_failed"}, source, baseline, signal) == "audit_failed_evidence_invalid"
    assert derive_candidate_factorial_verdict(replay, audit, {"candidate_source_unchanged": False}, baseline, signal) == "candidate_tuning_violation"
