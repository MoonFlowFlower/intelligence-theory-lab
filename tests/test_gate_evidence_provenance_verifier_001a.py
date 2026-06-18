import copy
import json
import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


VALID_VERDICT = "provenance_wellformed_only"
HASH_A = "a" * 64
HASH_B = "b" * 64
HASH_C = "c" * 64
HASH_D = "d" * 64
HASH_E = "e" * 64

FORBIDDEN_CLAIM_TERMS = [
    "gate pass",
    "mechanism validity",
    "baseline-immunity",
    "candidate success",
    "route c viability",
    "mainline effect",
    "runtime effect",
    "live effect",
    "agency",
    "autonomy",
    "consciousness",
    "emotion",
    "stable user benefit",
    "ego readiness",
]


def _valid_bundle() -> dict:
    return {
        "result.json": {
            "schema_version": "gate_evidence_provenance_verifier_001a_fixture_v1",
            "final_verdict": "bundle_provenance_inputs_wellformed",
            "expected_verdict": "invalid_literal_or_detached_verdict",
            "computed_gate_inputs": {
                "baseline_invocation": True,
                "strongest_baseline": True,
                "leakage_positive_control": True,
                "replay_recompute": True,
                "source_pin_readback": True,
                "control_consumption": True,
            },
            "verdict_derivation": {
                "producer_function": "synthetic_verdicts.select_decision_verdict",
                "input_artifacts": [
                    "baseline_comparison.json",
                    "provenance_rows.jsonl",
                    "leakage_scan.json",
                    "replay_report.json",
                    "source_pin_readback_report.json",
                ],
                "aggregation": "all_required_gates_true_fail_closed",
                "terminal_reason_source": "computed_gate_inputs",
                "terminal_reason_id": "all_required_gates_true",
                "consumed_baseline_ids": ["graph_cache_collapse"],
                "consumed_control_ids": [
                    "full_budget_saturation",
                    "baseline_saturation",
                ],
                "consumed_leakage_positive_control_ids": ["leakage-pc-label"],
                "consumed_source_pin_control_ids": ["source-truncation-pc"],
            },
        },
        "baseline_comparison.json": {
            "candidate_score": 0.72,
            "listed_baseline_ids": ["graph_cache_collapse"],
            "required_baseline_ids": ["graph_cache_collapse"],
            "strongest_fair_baseline_id": "graph_cache_collapse",
            "strongest_fair_baseline_score": 0.71,
            "delta_vs_strongest_fair": 0.01,
            "equivalence_band": 0.02,
            "strongest_fair_consumed_by_final_verdict": True,
        },
        "provenance_rows.jsonl": [
            {
                "row_id": "prov-baseline-graph-cache",
                "kind": "baseline_invocation",
                "baseline_id": "graph_cache_collapse",
                "invoked": True,
                "producer_function": "synthetic_baselines.graph_cache_collapse",
                "inputs": ["candidate_trace.jsonl"],
                "run_id": "run-baseline-001",
                "aggregation": "mean(score)",
                "code_path_hash": HASH_A,
            },
            {
                "row_id": "control-full-budget",
                "kind": "control",
                "control_id": "full_budget_saturation",
                "computed": True,
                "producer_function": "synthetic_controls.full_budget_saturation",
                "inputs": ["result.json"],
                "run_id": "run-control-001",
                "aggregation": "fail_closed_if_saturated",
                "code_path_hash": HASH_B,
            },
            {
                "row_id": "control-baseline-saturation",
                "kind": "control",
                "control_id": "baseline_saturation",
                "computed": True,
                "producer_function": "synthetic_controls.baseline_saturation",
                "inputs": ["baseline_comparison.json"],
                "run_id": "run-control-002",
                "aggregation": "fail_closed_if_saturated",
                "code_path_hash": HASH_C,
            },
        ],
        "leakage_scan.json": {
            "scanner": {
                "producer_function": "synthetic_leakage.scan",
                "inputs": ["candidate_trace.jsonl"],
                "run_id": "run-leakage-001",
                "aggregation": "any_detected",
                "code_path_hash": HASH_D,
            },
            "positive_controls": [
                {
                    "case_id": "leakage-pc-label",
                    "same_admission_path": True,
                    "detected": True,
                    "failure_recorded": False,
                    "consumed_by_final_verdict": True,
                }
            ],
        },
        "replay_report.json": {
            "mode": "recompute_from_serialized_state_and_observation",
            "recomputed_from_serialized_state": True,
            "recomputed_from_observation": True,
            "candidate_behavior_recomputed": True,
            "baseline_behavior_recomputed": True,
            "score_recomputed": True,
            "hash_only": False,
            "stored_hashes_only": False,
            "stored_actions_only": False,
            "stored_verdicts_only": False,
            "stored_scores_only": False,
        },
        "source_pin_readback_report.json": {
            "self_comparison_only": False,
            "readback_channels": [
                {
                    "channel": "git_blob",
                    "authoritative": True,
                    "source_path": "src/synthetic.py",
                    "sha256": HASH_E,
                },
                {
                    "channel": "filesystem_readback",
                    "authoritative": True,
                    "source_path": "src/synthetic.py",
                    "sha256": HASH_E,
                },
            ],
            "conflicts": [],
            "fail_closed_on_conflict": True,
            "truncation_positive_control": {
                "case_id": "source-truncation-pc",
                "detected": True,
                "consumed_by_final_verdict": True,
            },
        },
    }


def _write_bundle(bundle_dir: Path, bundle: dict) -> None:
    bundle_dir.mkdir(parents=True, exist_ok=True)
    for name, payload in bundle.items():
        path = bundle_dir / name
        if name.endswith(".jsonl"):
            path.write_text(
                "".join(json.dumps(row, sort_keys=True) + "\n" for row in payload),
                encoding="utf-8",
            )
        else:
            path.write_text(
                json.dumps(payload, sort_keys=True, indent=2) + "\n",
                encoding="utf-8",
            )


def _verify(bundle_dir: Path) -> dict:
    from gate_evidence_provenance_verifier_001a.verifier import verify_bundle

    return verify_bundle(bundle_dir)


def _with_mutation(mutator):
    bundle = copy.deepcopy(_valid_bundle())
    mutator(bundle)
    return bundle


def _literal_verdict(bundle: dict) -> None:
    bundle["result.json"].pop("computed_gate_inputs")
    bundle["result.json"]["verdict_derivation"] = {
        "terminal_reason_source": "literal",
        "terminal_reason_id": "looks_green",
    }


def _missing_baseline_invocation(bundle: dict) -> None:
    bundle["provenance_rows.jsonl"] = [
        row
        for row in bundle["provenance_rows.jsonl"]
        if row.get("kind") != "baseline_invocation"
    ]


def _missing_strongest_baseline(bundle: dict) -> None:
    bundle["baseline_comparison.json"].pop("strongest_fair_baseline_id")
    bundle["baseline_comparison.json"].pop("strongest_fair_baseline_score")
    bundle["baseline_comparison.json"].pop("delta_vs_strongest_fair")


def _leakage_positive_control_absent(bundle: dict) -> None:
    bundle["leakage_scan.json"]["positive_controls"] = []


def _hash_only_replay(bundle: dict) -> None:
    bundle["replay_report.json"].update(
        {
            "mode": "stored_hash_compare",
            "recomputed_from_serialized_state": False,
            "recomputed_from_observation": False,
            "candidate_behavior_recomputed": False,
            "baseline_behavior_recomputed": False,
            "score_recomputed": False,
            "hash_only": True,
            "stored_hashes_only": True,
        }
    )


def _source_pin_self_readback(bundle: dict) -> None:
    bundle["source_pin_readback_report.json"]["self_comparison_only"] = True
    bundle["source_pin_readback_report.json"]["readback_channels"] = [
        bundle["source_pin_readback_report.json"]["readback_channels"][0]
    ]


def _control_not_consumed(bundle: dict) -> None:
    bundle["provenance_rows.jsonl"].append(
        {
            "row_id": "control-orphan-full-budget",
            "kind": "control",
            "control_id": "orphan_full_budget_saturation",
            "computed": True,
            "producer_function": "synthetic_controls.orphan_full_budget",
            "inputs": ["result.json"],
            "run_id": "run-control-orphan",
            "aggregation": "fail_closed_if_saturated",
            "code_path_hash": HASH_A,
        }
    )


INVALID_CASES = {
    "literal_verdict_bundle": (
        _literal_verdict,
        "invalid_literal_or_detached_verdict",
    ),
    "missing_baseline_invocation_bundle": (
        _missing_baseline_invocation,
        "invalid_missing_or_uninvoked_baseline",
    ),
    "missing_strongest_baseline_bundle": (
        _missing_strongest_baseline,
        "invalid_missing_strongest_baseline",
    ),
    "leakage_positive_control_absent_bundle": (
        _leakage_positive_control_absent,
        "invalid_leakage_positive_control_absent_or_not_consumed",
    ),
    "hash_only_replay_bundle": (
        _hash_only_replay,
        "invalid_replay_not_recomputed",
    ),
    "source_pin_self_readback_bundle": (
        _source_pin_self_readback,
        "invalid_source_pin_self_readback_or_conflict",
    ),
    "control_not_consumed_bundle": (
        _control_not_consumed,
        "invalid_control_computed_but_not_consumed",
    ),
}


def test_valid_minimal_fixture_returns_wellformed_only(tmp_path):
    bundle_dir = tmp_path / "valid_minimal_bundle"
    _write_bundle(bundle_dir, _valid_bundle())

    output = _verify(bundle_dir)

    assert output["verdict"] == VALID_VERDICT
    assert output["no_gate_pass_claim"] is True
    assert output["bundle_dir"] == str(bundle_dir)


def test_every_invalid_fixture_returns_intended_invalid_verdict(tmp_path):
    for fixture_name, (mutator, expected) in INVALID_CASES.items():
        bundle_dir = tmp_path / fixture_name
        _write_bundle(bundle_dir, _with_mutation(mutator))

        output = _verify(bundle_dir)

        assert output["verdict"] == expected
        assert output["failed_checks"]


def test_mutating_valid_bundle_into_each_invalid_pattern_flips_verdict(tmp_path):
    for index, (mutator, expected) in enumerate(INVALID_CASES.values()):
        bundle_dir = tmp_path / f"renamed_fixture_{index}"
        _write_bundle(bundle_dir, _with_mutation(mutator))

        output = _verify(bundle_dir)

        assert output["verdict"] == expected
        assert output["verdict"] != VALID_VERDICT


def test_verifier_ignores_literal_expected_verdict_fields(tmp_path):
    valid_dir = tmp_path / "valid_with_bogus_expected"
    valid_bundle = _valid_bundle()
    valid_bundle["result.json"]["expected_verdict"] = "invalid_schema_or_parse_failure"
    _write_bundle(valid_dir, valid_bundle)

    invalid_dir = tmp_path / "invalid_with_bogus_expected"
    invalid_bundle = _with_mutation(_hash_only_replay)
    invalid_bundle["result.json"]["expected_verdict"] = VALID_VERDICT
    _write_bundle(invalid_dir, invalid_bundle)

    assert _verify(valid_dir)["verdict"] == VALID_VERDICT
    assert _verify(invalid_dir)["verdict"] == "invalid_replay_not_recomputed"


def test_schema_or_parse_failure_is_fail_closed(tmp_path):
    bundle_dir = tmp_path / "schema_failure"
    bundle = _valid_bundle()
    del bundle["result.json"]
    _write_bundle(bundle_dir, bundle)

    output = _verify(bundle_dir)

    assert output["verdict"] == "invalid_schema_or_parse_failure"


def test_cli_output_shape_and_forbidden_claim_scan(tmp_path):
    bundle_dir = tmp_path / "valid_minimal_bundle"
    _write_bundle(bundle_dir, _valid_bundle())
    env = {**os.environ, "PYTHONPATH": str(SRC)}

    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "gate_evidence_provenance_verifier_001a",
            str(bundle_dir),
        ],
        cwd=ROOT,
        env=env,
        check=True,
        text=True,
        capture_output=True,
    )
    output = json.loads(completed.stdout)
    serialized = json.dumps(output, sort_keys=True).lower()

    assert output["verdict"] == VALID_VERDICT
    assert output["checks_run"]
    assert output["failed_checks"] == []
    assert output["claim_ceiling"]
    assert output["no_gate_pass_claim"] is True
    for term in FORBIDDEN_CLAIM_TERMS:
        assert term not in serialized
