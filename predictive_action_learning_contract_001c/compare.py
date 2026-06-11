"""Masked behavioral-equality comparison against the 001 reference suite
(001C card section 7). Masks ONLY: declared volatile fields, sink-identity
fields that change by definition, and the hash fields recomputed over them.
All behavioral content is compared unmasked."""

import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from predictive_action_learning_contract_001 import config as cfg  # noqa: E402
from predictive_action_learning_contract_001.trace import load_trace, sha256_hex  # noqa: E402

MASK = sorted(set(cfg.VOLATILE_FIELDS) | {
    "commit_mode", "commit_sink_id", "receipt_type", "receipt_verifier_key_id",
    "runtime_manifest_hash", "config_manifest_hash",
    "pre_step_hash", "pre_step_hash_ref", "post_step_hash",
})


def _masked(rec):
    return json.dumps({k: v for k, v in rec.items() if k not in MASK},
                      sort_keys=True, separators=(",", ":"))


def compare_run(new_dir, ref_dir):
    a = [_masked(r) for r in load_trace(os.path.join(new_dir, "trace.jsonl"))]
    b = [_masked(r) for r in load_trace(os.path.join(ref_dir, "trace.jsonl"))]
    identical = a == b
    first = None
    if not identical:
        for i, (x, y) in enumerate(zip(a, b)):
            if x != y:
                first = i
                break
        if first is None:
            first = min(len(a), len(b))
    return {"identical": identical, "n_new": len(a), "n_ref": len(b),
            "first_diff_index": first,
            "masked_stream_sha256_new": sha256_hex("\n".join(a)),
            "masked_stream_sha256_ref": sha256_hex("\n".join(b))}


def compare_suite(new_suite, ref_suite):
    out, all_ok = {}, True
    ref_runs = os.path.join(ref_suite, "runs")
    for run_id in sorted(os.listdir(ref_runs)):
        nd = os.path.join(new_suite, "runs", run_id)
        rd = os.path.join(ref_runs, run_id)
        if not os.path.isdir(rd):
            continue
        if not os.path.isdir(nd):
            out[run_id] = {"identical": False, "error": "missing in new suite"}
            all_ok = False
            continue
        out[run_id] = compare_run(nd, rd)
        all_ok &= out[run_id]["identical"]
    return {"all_identical": all_ok, "mask": MASK, "runs": out}
