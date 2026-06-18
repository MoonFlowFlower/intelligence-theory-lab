from __future__ import annotations


TASK_ID = "GATE-EVIDENCE-PROVENANCE-VERIFIER-HARDENING-001A"

CLAIM_CEILING = "Gate evidence-bundle provenance shape verifier only."

VALID_VERDICT = "provenance_wellformed_only"

VERDICTS = (
    VALID_VERDICT,
    "invalid_literal_or_detached_verdict",
    "invalid_missing_or_uninvoked_baseline",
    "invalid_missing_strongest_baseline",
    "invalid_leakage_positive_control_absent_or_not_consumed",
    "invalid_replay_not_recomputed",
    "invalid_source_pin_self_readback_or_conflict",
    "invalid_control_computed_but_not_consumed",
    "invalid_schema_or_parse_failure",
)

REQUIRED_BUNDLE_FILES = (
    "result.json",
    "baseline_comparison.json",
    "provenance_rows.jsonl",
    "leakage_scan.json",
    "replay_report.json",
    "source_pin_readback_report.json",
)

CHECKS = (
    "schema_parse",
    "verdict_derivation",
    "baseline_invocation",
    "strongest_baseline_coverage",
    "leakage_positive_control",
    "replay_recompute",
    "source_pin_readback",
    "control_consumption",
)

REQUIRED_COMPUTED_GATE_INPUTS = (
    "baseline_invocation",
    "strongest_baseline",
    "leakage_positive_control",
    "replay_recompute",
    "source_pin_readback",
    "control_consumption",
)

BASELINE_PROVENANCE_FIELDS = (
    "producer_function",
    "inputs",
    "run_id",
    "aggregation",
    "code_path_hash",
)

STRONGEST_BASELINE_FIELDS = (
    "candidate_score",
    "strongest_fair_baseline_id",
    "strongest_fair_baseline_score",
    "delta_vs_strongest_fair",
)
