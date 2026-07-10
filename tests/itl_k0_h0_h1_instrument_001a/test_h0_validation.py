from __future__ import annotations

from itl_k0_h0_h1_instrument_001a.h0_freeze import build_freeze_payloads
from itl_k0_h0_h1_instrument_001a.h0_registry import build_registry
from itl_k0_h0_h1_instrument_001a.h0_validation import (
    run_ablation_catalog, run_baseline_comparison, run_metamorphic_validation,
    run_mutation_validation, run_permutation_validation, run_semantic_validation,
)


def _payloads():
    return build_registry(), build_freeze_payloads()


def test_independent_oracle_agrees_on_positive_and_every_negating_scenario():
    registry, payloads = _payloads()
    report = run_semantic_validation(registry, payloads["transformation_catalog"]["scenarios"])
    assert report["all_candidate_oracle_agree"] is True
    assert report["all_expected_match"] is True
    assert report["atomic_specs_complete"] is True


def test_every_normative_leaf_mutation_is_real_and_killed():
    registry, payloads = _payloads()
    report = run_mutation_validation(registry.to_dict(), payloads["normative_field_manifest"])
    assert report["normative_mutation_kill_rate"] == 1.0
    assert report["all_manifest_ids_consumed"] is True
    assert all(row["input_changed"] and row["real_validator_called"] == "validate_registry_payload" for row in report["results"])


def test_valid_transformations_permutations_baselines_and_ablations_are_computed():
    registry, payloads = _payloads()
    transformations = payloads["transformation_catalog"]
    baseline_contract = payloads["baseline_ablation_contract"]
    metamorphic = run_metamorphic_validation(registry.to_dict(), transformations)
    permutation = run_permutation_validation(transformations["permutations"])
    baseline = run_baseline_comparison(registry.to_dict(), payloads["normative_field_manifest"], {"transformations": transformations["transformations"], "baseline_ids": baseline_contract["baseline_ids"]}, transformations["scenarios"])
    ablation = run_ablation_catalog(registry.to_dict(), registry, baseline_contract)
    assert metamorphic["valid_transformation_accept_rate"] == 1.0
    assert permutation["all_invariant"] and permutation["all_frozen_ids_consumed"]
    assert baseline["all_baselines_invoked"] and baseline["no_baseline_matches_candidate"]
    assert ablation["all_frozen_ablations_consumed"] and ablation["all_ablations_detected"]
