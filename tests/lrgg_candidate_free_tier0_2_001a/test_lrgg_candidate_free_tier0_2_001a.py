import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


REQUIRED_ARTIFACTS = {
    "generator_spec.json",
    "generator_spec.sha256",
    "run_manifest.json",
    "result.json",
    "result.sha256",
    "baseline_scores.json",
    "oracle_report.json",
    "task_space_report.json",
    "leakage_report.json",
    "positive_controls_report.json",
    "replay_report.json",
    "tamper_report.json",
    "provenance_report.json",
    "aggregation_report.json",
    "LIMITATIONS.md",
    "CLAIM_CEILING.md",
    "trace.jsonl",
}


def _runner():
    from lrgg_candidate_free_tier0_2_001a import runner

    return runner


def test_preconditions_generator_task_space_and_source_readback(tmp_path):
    runner = _runner()

    run = runner.run_tier0_2(output_dir=tmp_path / "run", persist_artifacts=False)
    manifest = run["run_manifest"]
    spec = run["generator_spec"]
    task_space = run["task_space_report"]

    assert manifest["preconditions"]["canonical_source_readback_succeeded"] is True
    assert manifest["preconditions"]["preflight_sha256_matches_expected"] is True
    assert manifest["preconditions"]["freeze_manifest_sha256_matches_expected"] is True
    assert manifest["preconditions"]["freeze_field_count"] == 31
    assert manifest["preconditions"]["unresolved_freeze_field_rows"] == 0
    assert manifest["preconditions"]["stale_patterns_absent"] is True
    assert spec["n_seed"] == 10
    assert spec["n_ctx"] == 30
    assert spec["N_rows"] == 300
    assert spec["B"] == 8
    assert spec["N_enum_action"] >= 80
    assert spec["coverage_fraction"] <= 0.10
    assert task_space["H_T_bits"] >= 12.0
    assert task_space["realized_distinct_T"] >= 270
    assert task_space["N_enum_latent"] >= 3000
    assert task_space["coverage_fraction"] <= 0.10


def test_scores_and_baseline_saturation_use_family_max(tmp_path):
    runner = _runner()

    run = runner.run_tier0_2(output_dir=tmp_path / "run", persist_artifacts=False)
    result = run["result"]
    oracle = run["oracle_report"]
    baselines = run["baseline_scores"]

    assert result["verdict"] == "rejected_baseline_saturated"
    assert result["candidate_mechanism_run"] is False
    assert oracle["oracle_score_C"]["mean"] >= 0.90
    assert oracle["oracle_score_C"]["mean"] - max(
        oracle["random_baseline"]["mean"],
        oracle["majority_baseline"]["mean"],
    ) >= 0.10
    assert oracle["oracle_score_C"]["mean"] - oracle["nonreading_oracle"]["mean"] >= 0.30
    assert baselines["trivial_predictors"]["triggered_blocker"] is False
    assert baselines["obs_only_memoryless_raw_decode"]["triggered_blocker"] is False
    assert baselines["family_max"]["score"]["mean"] >= oracle["oracle_score_C"]["mean"] - 0.05
    assert baselines["family_max"]["baseline_id"] in set(baselines["required_baseline_ids"])
    assert "rejected_baseline_saturated" in result["blocker_labels_triggered"]


def test_leakage_replay_tamper_and_provenance_are_fail_able(tmp_path):
    runner = _runner()

    run = runner.run_tier0_2(output_dir=tmp_path / "run", persist_artifacts=False)

    assert run["leakage_report"]["passed"] is True
    assert run["positive_controls_report"]["all_planted_controls_alarm"] is True
    assert set(run["positive_controls_report"]["alarm_families"]) >= {
        "hidden_rule_id",
        "latent_graph_exposure",
        "task_family_id",
        "score_key_reward_shaping",
        "membership_leakage",
        "seed_config_filename_leakage",
        "observation_field_audit",
        "serialized_state_audit",
        "import_path_audit",
        "value_level_attacker_family_max",
    }
    assert run["replay_report"]["passed"] is True
    assert run["replay_report"]["uses_stored_score_only"] is False
    assert all(row["triggered_mismatch"] is True for row in run["tamper_report"]["probes"])
    assert run["tamper_report"]["passed"] is True

    provenance = run["provenance_report"]
    check = runner.verify_provenance(provenance)
    assert check["passed"] is True
    assert provenance["record_count"] >= len(run["baseline_scores"]["required_baseline_ids"]) + 4
    assert all(record["producer_function"] for record in provenance["records"])
    assert all(record["code_path_hash"] for record in provenance["records"])
    assert all(record["run_id"] == run["result"]["run_id"] for record in provenance["records"])

    leaked = runner.run_tier0_2(
        output_dir=tmp_path / "leaked",
        persist_artifacts=False,
        disable_positive_control="hidden_rule_id",
    )
    assert leaked["result"]["verdict"] == "INVALID"
    assert "failed_positive_control:hidden_rule_id" in leaked["result"]["blocker_labels_triggered"]


def test_persisted_official_artifacts_parse_and_hash(tmp_path):
    runner = _runner()
    out = tmp_path / "official"

    run = runner.run_tier0_2(output_dir=out, persist_artifacts=True)

    assert REQUIRED_ARTIFACTS <= {path.name for path in out.iterdir()}
    for name in REQUIRED_ARTIFACTS - {
        "LIMITATIONS.md",
        "CLAIM_CEILING.md",
        "trace.jsonl",
        "generator_spec.sha256",
        "result.sha256",
    }:
        json.loads((out / name).read_text(encoding="utf-8"))

    result_hash = (out / "result.sha256").read_text(encoding="utf-8").strip()
    assert result_hash == runner.sha256_bytes((out / "result.json").read_bytes())
    spec_hash = (out / "generator_spec.sha256").read_text(encoding="utf-8").strip()
    assert spec_hash == runner.sha256_bytes((out / "generator_spec.json").read_bytes())

    trace_lines = (out / "trace.jsonl").read_text(encoding="utf-8").splitlines()
    assert len(trace_lines) == run["generator_spec"]["N_rows"]
    assert all(json.loads(line)["candidate_mechanism_run"] is False for line in trace_lines)

    claim_ceiling = (out / "CLAIM_CEILING.md").read_text(encoding="utf-8")
    assert "Tier 0-2 candidate-free cheap-tier plumbing evidence only" in claim_ceiling
    assert "does not prove LRGG admissibility" in claim_ceiling
    assert "does not authorize 001C" in claim_ceiling
