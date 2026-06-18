import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


def test_unconsumed_baseline_result_blocks_admissibility():
    from gate1_replacement_preflight_00xa.verdict import derive_final_verdict, minimal_valid_context

    context = minimal_valid_context()
    context["baseline_rows_by_id"]["count_table"]["consumed_by_final_verdict"] = False

    verdict = derive_final_verdict(context)

    assert verdict["final_verdict"] == "blocked_pending_canonical_readback"
    assert verdict["terminal_reason_id"] == "baseline_panel_invalid"


def test_trained_learner_without_real_fit_blocks_learning_claims():
    from gate1_replacement_preflight_00xa.verdict import derive_final_verdict, minimal_valid_context

    context = minimal_valid_context()
    context["adaptation_or_learning_claimed"] = True
    context["trained_learner"] = {
        "included": True,
        "ml_library_used": False,
        "real_fit_evidence": False,
        "deterministic_stub": True,
    }

    verdict = derive_final_verdict(context)

    assert verdict["final_verdict"] == "blocked_pending_canonical_readback"
    assert verdict["terminal_reason_id"] == "trained_learner_without_real_fit"


def test_source_pin_hash_mismatch_fails_closed():
    from gate1_replacement_preflight_00xa.verdict import derive_final_verdict, minimal_valid_context

    context = minimal_valid_context()
    context["source_pin_readback"]["all_present"] = True
    context["source_pin_readback"]["hash_conflicts"] = [{"path": "docs/research/gate1_replacement_surface_spec_00xa.md"}]

    verdict = derive_final_verdict(context)

    assert verdict["final_verdict"] == "blocked_pending_canonical_readback"
    assert verdict["terminal_reason_id"] == "source_pin_readback_conflict"


def test_admissible_verdict_requires_all_controls_independent_and_consumed():
    from gate1_replacement_preflight_00xa.verdict import derive_final_verdict, minimal_valid_context

    context = minimal_valid_context(admissible_shape=True)
    assert derive_final_verdict(context)["final_verdict"] == "admissible_for_candidate_card_drafting_only"

    context["baseline_rows_by_id"]["episodic_traversal"]["independence_status"] = "not_independent"
    verdict = derive_final_verdict(context)

    assert verdict["final_verdict"] == "blocked_pending_canonical_readback"
    assert verdict["terminal_reason_id"] == "baseline_panel_invalid"


def test_missing_generator_provenance_blocks_before_saturation():
    from gate1_replacement_preflight_00xa.verdict import derive_final_verdict, minimal_valid_context

    context = minimal_valid_context()
    context.pop("generator_provenance")
    context["baseline_rows_by_id"]["exhaustive_legal_query"]["metric"]["macro_f1"] = 1.0
    context["oracle"]["visible_channel_oracle"]["metric"]["macro_f1"] = 1.0

    verdict = derive_final_verdict(context)

    assert verdict["final_verdict"] == "blocked_pending_canonical_readback"
    assert verdict["terminal_reason_id"] == "generator_provenance_missing_or_invalid"


def test_missing_generator_source_hash_blocks_before_saturation():
    from gate1_replacement_preflight_00xa.verdict import derive_final_verdict, minimal_valid_context

    context = minimal_valid_context()
    context["generator_provenance"].pop("generator_source_hash")

    verdict = derive_final_verdict(context)

    assert verdict["final_verdict"] == "blocked_pending_canonical_readback"
    assert verdict["terminal_reason_id"] == "generator_provenance_missing_or_invalid"


def test_generator_source_hash_mismatch_blocks_before_saturation():
    from gate1_replacement_preflight_00xa.verdict import derive_final_verdict, minimal_valid_context

    context = minimal_valid_context()
    context["generator_provenance"]["generator_source_hash"] = "0" * 64

    verdict = derive_final_verdict(context)

    assert verdict["final_verdict"] == "blocked_pending_canonical_readback"
    assert verdict["terminal_reason_id"] == "generator_provenance_missing_or_invalid"


def test_self_readback_only_generator_provenance_blocks_before_saturation():
    from gate1_replacement_preflight_00xa.verdict import derive_final_verdict, minimal_valid_context

    context = minimal_valid_context()
    context["generator_provenance"]["self_readback_only"] = True
    context["generator_provenance"]["readback_channels"] = ["self_reported_generator_metadata"]

    verdict = derive_final_verdict(context)

    assert verdict["final_verdict"] == "blocked_pending_canonical_readback"
    assert verdict["terminal_reason_id"] == "generator_provenance_missing_or_invalid"


def test_candidate_authored_generator_truth_blocks_before_saturation():
    from gate1_replacement_preflight_00xa.verdict import derive_final_verdict, minimal_valid_context

    context = minimal_valid_context()
    context["generator_provenance"]["no_candidate_authored_truth"] = False

    verdict = derive_final_verdict(context)

    assert verdict["final_verdict"] == "blocked_pending_canonical_readback"
    assert verdict["terminal_reason_id"] == "generator_provenance_missing_or_invalid"


def test_valid_generator_provenance_allows_existing_saturation_cascade():
    from gate1_replacement_preflight_00xa.verdict import derive_final_verdict, minimal_valid_context

    context = minimal_valid_context()
    context["baseline_rows_by_id"]["exhaustive_legal_query"]["metric"]["macro_f1"] = 1.0
    context["oracle"]["visible_channel_oracle"]["metric"]["macro_f1"] = 1.0

    verdict = derive_final_verdict(context)

    assert verdict["final_verdict"] == "rejected_baseline_saturated"
    assert verdict["terminal_reason_id"] == "fair_baseline_ties_oracle_within_equivalence_band"
    assert verdict["generator_provenance_gate"]["valid"] is True


def test_metric_thresholds_remain_frozen():
    from gate1_replacement_preflight_00xa.metrics import (
        CEILING_BAND_FLOOR,
        EQUIVALENCE_BAND,
        PARTIAL_INFERABILITY_MARGIN,
        PER_CLASS_FLOOR,
        TARGET_CEILING_MINIMUM,
    )

    assert CEILING_BAND_FLOOR == 0.87
    assert TARGET_CEILING_MINIMUM == 0.90
    assert EQUIVALENCE_BAND == 0.03
    assert PER_CLASS_FLOOR == 0.85
    assert PARTIAL_INFERABILITY_MARGIN == 0.06


def test_runner_writes_001b_allowed_artifacts_and_rejected_baseline_saturated(tmp_path):
    from gate1_replacement_preflight_00xa.run_preflight import ALLOWED_ARTIFACT_FILENAMES_001B, run_preflight

    output_dir = tmp_path / "run"
    result = run_preflight(repo_root=ROOT, output_dir=output_dir, run_id="gate1_replacement_preflight_00xa_run_001b")

    assert result["final_verdict"] == "rejected_baseline_saturated"
    assert result["claim_ceiling"] == "candidate-free preflight evidence bundle only"
    assert sorted(p.name for p in output_dir.iterdir()) == sorted(ALLOWED_ARTIFACT_FILENAMES_001B)

    final_verdict = json.loads((output_dir / "final_verdict.json").read_text(encoding="utf-8"))
    generator_provenance = json.loads((output_dir / "generator_provenance.json").read_text(encoding="utf-8"))
    generator_gate = json.loads((output_dir / "generator_provenance_gate.json").read_text(encoding="utf-8"))
    baseline_rows = [
        json.loads(line)
        for line in (output_dir / "baseline_results.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    oracle = json.loads((output_dir / "oracle_results.json").read_text(encoding="utf-8"))

    assert final_verdict["final_verdict"] == "rejected_baseline_saturated"
    assert final_verdict["task_repair_verdict"] == "gate1_replacement_preflight_00xa_b1_generator_provenance_repaired"
    assert final_verdict["mainline_integration_status"] == "none"
    assert final_verdict["enabled_status"] == "no runtime/mainline path enabled"
    assert generator_provenance["generator_source_hash"]
    assert generator_provenance["source_pin_sha256"] == generator_provenance["generator_source_hash"]
    assert generator_gate["valid"] is True
    assert next(row for row in baseline_rows if row["baseline_id"] == "exhaustive_legal_query")["metric"]["macro_f1"] == 1.0
    assert oracle["visible_channel_oracle"]["metric"]["macro_f1"] == 1.0
