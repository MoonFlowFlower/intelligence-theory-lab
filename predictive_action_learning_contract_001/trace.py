"""Trace contract (task card section 7): canonical serialization, deterministic
content hashing, hash chaining, schema declaration, and the append-only writer.
"""

import hashlib
import json

from . import config as cfg


def canonical_json(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), allow_nan=False)


def sha256_hex(s):
    if isinstance(s, str):
        s = s.encode()
    return hashlib.sha256(s).hexdigest()


def content_hash(record):
    """Deterministic hash over the record minus volatile and hash fields."""
    body = {k: v for k, v in record.items() if k not in cfg.VOLATILE_FIELDS}
    return sha256_hex(canonical_json(body))


def strip_for_duplicate(record):
    return {k: v for k, v in record.items() if k not in cfg.DUPLICATE_STRIP_FIELDS}


TRACE_SCHEMA = {
    "schema_id": "palc001-trace-schema-1.0",
    "serializer_version": cfg.SERIALIZER_VERSION,
    "format": "jsonl, one event per line",
    "event_types": ["RUN_META", "PRE_STEP", "POST_STEP", "REPLAY_STEP"],
    "replay_step_rule": "REPLAY_STEP is reserved only; any occurrence in a core run "
                        "=> protocol_verdict=protocol_blocked, reason=replay_contamination",
    "hashing": {
        "content_hash": "sha256 over canonical JSON (sorted keys, compact separators) of the "
                        "record minus volatile_fields; stored as pre_step_hash / post_step_hash",
        "chain_hash": "sha256(prev_chain_hash + canonical(record minus chain_hash)); "
                      "RUN_META starts the chain with prev=''",
        "volatile_fields": cfg.VOLATILE_FIELDS,
        "duplicate_strip_fields": cfg.DUPLICATE_STRIP_FIELDS,
    },
    "chronology_rule": "pre_commit_receipt.commit_monotonic_ns must be < obs_reveal_monotonic_ns "
                       "of the same step; receipts must match commits.log.jsonl by seq and payload hash",
    "required_fields": {
        "RUN_META": [
            "event_type", "run_id", "random_seed", "env_rule_id", "action_schema",
            "obs_schema", "state_schema", "serializer_version", "trace_schema_hash",
            "ablation_id", "perturbation_id", "baseline_id", "retrieval_enabled",
            "replay_enabled", "runtime_attestation_ref", "runtime_manifest_hash",
            "config_manifest_hash", "storage_policy_hash", "network_policy_hash",
            "claim_mode", "commit_mode", "commit_sink_id", "threshold_config_hash",
            "policy_id", "predictor_id", "steps", "eps_T", "eps_O", "shift_t",
            "ambig_t", "cold_start_marker", "cache_epoch_id", "replayable_skeleton",
            "task_id", "task_card", "chain_hash",
        ],
        "PRE_STEP": [
            "event_type", "t", "obs_t", "belief_pre", "theta_T_pre", "theta_O_pre",
            "action_t", "committed_action_label",
            "raw_pred_obs_by_action", "raw_pred_belief_by_action",
            "uncertainty_pre", "action_sensitivity_metric",
            "action_sensitive_regime_id", "null_control_regime_id",
            "action_sensitivity_acceptance_threshold", "pre_step_hash",
            "pre_commit_receipt", "commit_sink_id", "receipt_type",
            "receipt_verifier_key_id", "chain_hash",
        ],
        "POST_STEP": [
            "event_type", "t", "actual_obs", "obs_reveal_ts",
            "obs_reveal_monotonic_ns", "pred_prob_actual", "nll_error",
            "brier_component", "transition_responsibility", "belief_post",
            "delta_belief", "theta_T_post", "theta_O_post", "delta_theta_derived",
            "post_step_hash", "pre_step_hash_ref", "external_memory_access_count",
            "replay_step_count", "retrieval_event_log", "cache_epoch_id",
            "theta_frozen_baseline_id", "rule_shift_perturbation_id", "chain_hash",
        ],
    },
    "nullable_model_fields_note": "Non-skeleton baselines log null for belief/theta/"
                                  "responsibility fields; field presence is still required.",
}

TRACE_SCHEMA_HASH = sha256_hex(canonical_json(TRACE_SCHEMA))
THRESHOLD_CONFIG_HASH = sha256_hex(canonical_json(cfg.THRESHOLDS))


class TraceWriter:
    """Append-only JSONL writer with hash chaining. drop_fields supports
    ablations 7/10 (the validator must then reject the trace)."""

    def __init__(self, path, drop_fields=None):
        self.f = open(path, "w", encoding="utf-8")
        self.prev_chain = ""
        self.drop_fields = set(drop_fields or [])

    def write(self, record):
        rec = {k: v for k, v in record.items() if k not in self.drop_fields}
        chain = sha256_hex(self.prev_chain + canonical_json(rec))
        rec["chain_hash"] = chain
        self.prev_chain = chain
        self.f.write(json.dumps(rec, sort_keys=True, separators=(",", ":")) + "\n")
        self.f.flush()
        return rec

    def close(self):
        self.f.close()


def load_trace(path):
    out = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                out.append(json.loads(line))
    return out
