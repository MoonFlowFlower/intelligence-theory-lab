from acolb_001a.provenance import build_metric_provenance, validate_metric_provenance


def test_metric_provenance_has_required_callable_fields():
    row = build_metric_provenance(
        metric_id="candidate_ood_score",
        metric_name="candidate ood score",
        producer_function="run_candidate",
        producer_module="acolb_001a.candidate",
        code_path_hash="abc123",
        run_id="run-test",
        seed_ids=[5001],
        episode_ids=["ood-5001-0"],
        input_artifact_paths=["trace.jsonl"],
        output_artifact_path="result.json",
        output_row_ids=["candidate_ood_score"],
        aggregation_rule="mean_score",
        threshold_used=0.05,
        computed_not_literal_evidence="score recomputed from per-query prediction errors",
        failure_path_evidence="prediction perturbation changes score",
    )

    verdict = validate_metric_provenance(row)
    assert verdict["valid"] is True
    assert row["computed_not_literal"] is True
    assert row["failure_path_available"] is True


def test_literal_or_static_score_provenance_is_rejected():
    row = build_metric_provenance(
        metric_id="literal_score",
        metric_name="literal score",
        producer_function="",
        producer_module="",
        code_path_hash="",
        run_id="run-test",
        seed_ids=[],
        episode_ids=[],
        input_artifact_paths=[],
        output_artifact_path="result.json",
        output_row_ids=[],
        aggregation_rule="literal",
        threshold_used=0.0,
    )

    verdict = validate_metric_provenance(row)
    assert verdict["valid"] is False
    assert "missing_or_literal_producer" in verdict["errors"]
    assert row["computed_not_literal"] is False
    assert row["failure_path_available"] is False
