from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .h0_registry import build_registry
from .h0_validation import (
    build_permutation_catalog,
    build_scenario_catalog,
    canonical_json_bytes,
    enumerate_normative_leaves,
    file_hashes,
    sha256_bytes,
    validate_registry_payload,
)


TASK_ID = "ITL-K0-H0-CODE-FIRST-PREBANK-001A"
TASK_CARD_PIN = {
    "bank_commit": "1fcafdc317fb3aed3b3e1cbf057e1f460e9308bd",
    "card_blob": "523ea303c62b893d62db62fe6febb2ca3f2a5a88",
    "card_path": "docs/codex/tasks/ITL-K0-H0-CODE-FIRST-PREBANK-001A.md",
    "card_sha256": "19aefb27620bbc494d81065b4f44c01660c078409afaf551cb18aa7b01f6ff99",
}

SOURCE_PATHS = [
    "src/itl_k0_h0_h1_instrument_001a/__init__.py",
    "src/itl_k0_h0_h1_instrument_001a/h0_schema.py",
    "src/itl_k0_h0_h1_instrument_001a/h0_registry.py",
    "src/itl_k0_h0_h1_instrument_001a/h0_resolver.py",
    "src/itl_k0_h0_h1_instrument_001a/h0_validation.py",
    "src/itl_k0_h0_h1_instrument_001a/h0_freeze.py",
    "src/itl_k0_h0_h1_instrument_001a/h0_cli.py",
]
TEST_PATHS = [
    "tests/itl_k0_h0_h1_instrument_001a/test_h0_schema.py",
    "tests/itl_k0_h0_h1_instrument_001a/test_h0_registry.py",
    "tests/itl_k0_h0_h1_instrument_001a/test_h0_resolver.py",
    "tests/itl_k0_h0_h1_instrument_001a/test_h0_validation.py",
    "tests/itl_k0_h0_h1_instrument_001a/test_h0_cli.py",
]
FREEZE_PATHS = [
    "artifacts/ITL-K0-H0-CODE-FIRST-PREBANK-001A/freeze_manifest.json",
    "artifacts/ITL-K0-H0-CODE-FIRST-PREBANK-001A/normative_field_manifest.json",
    "artifacts/ITL-K0-H0-CODE-FIRST-PREBANK-001A/transformation_catalog.json",
    "artifacts/ITL-K0-H0-CODE-FIRST-PREBANK-001A/baseline_ablation_contract.json",
    "artifacts/ITL-K0-H0-CODE-FIRST-PREBANK-001A/claim_ceiling.txt",
]
PHASE_C_PATHS = SOURCE_PATHS + TEST_PATHS + FREEZE_PATHS

CLAIM_CEILING = "code-first H0 contract prebank implementation and validation evidence only\n"


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n", encoding="utf-8")


def build_freeze_payloads() -> dict[str, Any]:
    registry = build_registry()
    registry_payload = registry.to_dict()
    registry_validation = validate_registry_payload(registry_payload)
    if not registry_validation["accepted"]:
        raise ValueError(f"canonical registry is invalid: {registry_validation['validation_errors']}")
    normative_fields = enumerate_normative_leaves(registry_payload)
    scenarios = build_scenario_catalog(registry)
    permutations = build_permutation_catalog(registry)
    normative_manifest = {
        "task_id": TASK_ID,
        "producer_function": "enumerate_normative_leaves",
        "registry_sha256": sha256_bytes(canonical_json_bytes(registry_payload)),
        "normative_fields": normative_fields,
        "metadata_exclusions": [
            {"path": "$.metadata", "reason": "finite human-readable annotation namespace excluded from H0 domain semantics"}
        ],
        "mutation_operator_contract": "each normative leaf is replaced with JSON null; the mutation must change canonical input bytes and invoke validate_registry_payload",
    }
    transformation_catalog = {
        "task_id": TASK_ID,
        "producer_function": "build_transformation_and_permutation_catalog",
        "transformations": [
            {"transformation_id": "json_key_order", "semantics": "preserving"},
            {"transformation_id": "set_like_arm_order", "semantics": "preserving"},
            {"transformation_id": "metadata_only_fields", "semantics": "preserving"},
            {"transformation_id": "canonical_equivalent_serialization", "semantics": "preserving"},
        ],
        "scenarios": scenarios,
        "permutations": permutations,
        "permutation_seed": 9173,
        "permutation_rule": "all causal permutations for panels with at most six arms; reversed, rotated, adjacent swap, and four fixed-seed permutations for comparator panels",
    }
    baseline_ablation = {
        "task_id": TASK_ID,
        "producer_function": "build_baseline_ablation_contract",
        "baseline_ids": ["exact_blob_equality", "permissive_schema_parse", "same_resolver_twice", "synthetic_atomic_witness"],
        "ablation_ids": ["order_first_hit", "global_panel_scalar", "ignore_provenance", "synthetic_atomic_witness", "same_resolver_oracle"],
        "acceptance": {
            "candidate_invalid_reject_rate": 1.0,
            "candidate_valid_accept_rate": 1.0,
            "each_ablation_detected": True,
            "no_baseline_matches_candidate": True,
        },
    }
    return {
        "registry": registry_payload,
        "normative_field_manifest": normative_manifest,
        "transformation_catalog": transformation_catalog,
        "baseline_ablation_contract": baseline_ablation,
    }


def generate_freeze_files(repo_root: Path, output_dir: Path) -> dict[str, Any]:
    payloads = build_freeze_payloads()
    output_dir.mkdir(parents=True, exist_ok=True)
    _write_json(output_dir / "normative_field_manifest.json", payloads["normative_field_manifest"])
    _write_json(output_dir / "transformation_catalog.json", payloads["transformation_catalog"])
    _write_json(output_dir / "baseline_ablation_contract.json", payloads["baseline_ablation_contract"])
    (output_dir / "claim_ceiling.txt").write_text(CLAIM_CEILING, encoding="utf-8")
    hashed_paths = SOURCE_PATHS + TEST_PATHS + FREEZE_PATHS[1:]
    hashes = file_hashes(repo_root, hashed_paths)
    manifest = {
        "task_id": TASK_ID,
        "schema_version": "itl.k0.h0.code_first_prebank.freeze.001a.v1",
        "producer_function": "generate_freeze_files",
        "task_card_pin": TASK_CARD_PIN,
        "phase_c_paths": PHASE_C_PATHS,
        "source_paths": SOURCE_PATHS,
        "test_paths": TEST_PATHS,
        "freeze_paths": FREEZE_PATHS,
        "frozen_file_hashes": hashes,
        "registry": payloads["registry"],
        "registry_sha256": sha256_bytes(canonical_json_bytes(payloads["registry"])),
        "normative_field_count": len(payloads["normative_field_manifest"]["normative_fields"]),
        "scenario_count": len(payloads["transformation_catalog"]["scenarios"]),
        "permutation_count": len(payloads["transformation_catalog"]["permutations"]),
        "transformation_ids": [row["transformation_id"] for row in payloads["transformation_catalog"]["transformations"]],
        "baseline_ids": payloads["baseline_ablation_contract"]["baseline_ids"],
        "ablation_ids": payloads["baseline_ablation_contract"]["ablation_ids"],
        "formal_result_present": False,
        "h0_acceptance_present": False,
        "external_write_manifest": [],
        "claim_ceiling": CLAIM_CEILING.strip(),
    }
    manifest["manifest_payload_sha256"] = sha256_bytes(canonical_json_bytes(manifest))
    _write_json(output_dir / "freeze_manifest.json", manifest)
    return manifest


def verify_freeze_files(repo_root: Path, freeze_manifest_path: Path) -> dict[str, Any]:
    manifest = json.loads(freeze_manifest_path.read_text(encoding="utf-8"))
    actual = file_hashes(repo_root, list(manifest["frozen_file_hashes"]))
    errors = [path for path, expected in manifest["frozen_file_hashes"].items() if actual.get(path) != expected]
    registry_validation = validate_registry_payload(manifest["registry"])
    payload_hash_source = dict(manifest)
    recorded_payload_hash = payload_hash_source.pop("manifest_payload_sha256", None)
    payload_hash_valid = recorded_payload_hash == sha256_bytes(canonical_json_bytes(payload_hash_source))
    return {
        "producer_function": "verify_freeze_files",
        "hash_mismatches": errors,
        "manifest_payload_hash_valid": payload_hash_valid,
        "registry_valid": registry_validation["accepted"],
        "passed": not errors and payload_hash_valid and registry_validation["accepted"],
        "manifest": manifest,
    }
