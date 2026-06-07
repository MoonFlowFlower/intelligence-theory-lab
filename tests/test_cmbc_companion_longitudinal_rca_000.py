import json

from cmbc_companion.evals.longitudinal_rca_000 import ALLOWED_VERDICTS, run_rca


def test_rca_freezes_redteam_failure_artifacts(tmp_path):
    result = run_rca(tmp_path)

    manifest = result["frozen_failure_manifest"]
    assert manifest["source_verdict"] == "longitudinal_drift_failed"
    assert manifest["source_stop_conditions"] == ["longitudinal_drift_failed"]
    assert len(manifest["frozen_artifacts"]) >= 4
    assert (tmp_path / "frozen_failure_manifest.json").exists()


def test_short_fixture_deletion_vs_long_deletion_is_compared(tmp_path):
    result = run_rca(tmp_path)

    comparison = result["short_vs_long_deletion"]
    assert comparison["short_fixture"]["selected_action_changed"] is True
    assert comparison["long_rollout"]["selected_action_changed"] is False
    assert comparison["long_rollout"]["distribution_delta_l1"] > 0.0
    assert (tmp_path / "short_vs_long_deletion_comparison.json").exists()


def test_rca_separates_score_delta_from_distribution_delta(tmp_path):
    result = run_rca(tmp_path)

    score = result["score_vs_distribution_delta"]
    assert score["long_rollout"]["selected_action_changed"] is False
    assert score["long_rollout"]["top_probability_delta"] > 0.0
    assert score["long_rollout"]["distribution_kl"] > 0.0
    assert score["long_rollout"]["rank_margin_delta"] > 0.0


def test_rca_checks_deletion_target_and_recency_dominance(tmp_path):
    result = run_rca(tmp_path)

    deletion = result["deletion_target_audit"]
    recency = result["recency_dominance_audit"]
    assert deletion["deleted_true_causal_record_for_final_action"] is False
    assert deletion["final_action"] == "act_6"
    assert recency["dominant_final_action_count"] >= 6
    assert recency["recency_dominates_long_memory"] is True


def test_rca_verdict_is_allowed_and_records_secondary_findings(tmp_path):
    result = run_rca(tmp_path)

    assert result["verdict"] in ALLOWED_VERDICTS
    assert result["verdict"] == "action_distribution_saturated"
    assert "deletion_target_wrong" in result["secondary_findings"]
    assert "recency_dominates_long_memory" in result["secondary_findings"]
    assert result["runtime_code_changed"] is False


def test_rca_required_artifacts_are_written(tmp_path):
    result = run_rca(tmp_path)

    required = {
        "RCA_STATUS.md",
        "frozen_failure_manifest.json",
        "short_vs_long_deletion_comparison.json",
        "short_vs_long_deletion_comparison.md",
        "trace_causal_path.jsonl",
        "trace_causal_path.md",
        "score_vs_distribution_delta.json",
        "score_vs_distribution_delta.md",
        "representation_dominance_audit.json",
        "deletion_target_audit.json",
        "saturation_recency_update_audit.md",
        "CMBC_COMPANION_LONGITUDINAL_RCA_RESULT.md",
        "cmbc_companion_longitudinal_rca_result.json",
    }
    assert required.issubset({path.name for path in tmp_path.iterdir()})

    with (tmp_path / "cmbc_companion_longitudinal_rca_result.json").open(
        "r", encoding="utf-8"
    ) as fh:
        verdict = json.load(fh)
    assert verdict["verdict"] == result["verdict"]
    assert verdict["claim_after_rca"] == "fixed-fixture companion growth evidence only"

