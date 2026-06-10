"""PREDICTIVE-ACTION-LEARNING-CONTRACT-001C-INDEPENDENT-AUDIT
Audit-only re-verification script. READ-ONLY on all frozen artifacts and
runtime code. Writes outputs ONLY under artifacts/<audit_task_id>/.

Re-runs existing validators (verify.py, compare.py, validator.py) against the
frozen 001C suite in the repo, plus independent recomputation of the retrieval
E10 components directly from raw traces (own code, not repo metrics).
"""

import base64
import hashlib
import json
import math
import os
import sys

REPO = "/sessions/magical-clever-cannon/mnt/intelligence-theory-lab"
sys.path.insert(0, REPO)

S001 = os.path.join(REPO, "artifacts/predictive_action_learning_contract_001/suite_2026-06-10_r1")
S001C = os.path.join(REPO, "artifacts/predictive_action_learning_contract_001c/suite_001c_2026-06-10_t1")
OUT = os.path.join(REPO, "artifacts/predictive_action_learning_contract_001c_independent_audit")
os.makedirs(OUT, exist_ok=True)

from predictive_action_learning_contract_001c.verify import verify_run_dir, verify_token  # noqa: E402
from predictive_action_learning_contract_001c.compare import compare_suite  # noqa: E402
from predictive_action_learning_contract_001c.driver import _final_chain_heads  # noqa: E402
from predictive_action_learning_contract_001 import config as cfg  # noqa: E402
from predictive_action_learning_contract_001.validator import validate_run_dir, split_records  # noqa: E402
from predictive_action_learning_contract_001.trace import load_trace  # noqa: E402

failures = []


def save(name, obj):
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=1, sort_keys=True, default=str)


# ---------------------------------------------------------------- 1. anchors
anchor_out = {"runs": {}, "suite_anchors": [], "all_ok": True, "all_external": True,
              "any_test_ca": False, "n_tokens_verified": 0}
runs_dir = os.path.join(S001C, "runs")
for run_id in sorted(os.listdir(runs_dir)):
    rd = os.path.join(runs_dir, run_id)
    meta = split_records(load_trace(os.path.join(rd, "trace.jsonl")))[0]
    if meta.get("commit_mode") == "disabled":
        anchor_out["runs"][run_id] = {
            "skipped": "commit disabled by ablation 5",
            "anchors_present": os.path.exists(os.path.join(rd, "anchors.log.jsonl"))}
        continue
    rep = verify_run_dir(rd)
    anchor_out["runs"][run_id] = {
        "ok": rep["ok"], "external_valid": rep["external_valid"],
        "n_commits": rep["n_commits"], "n_anchors": len(rep["anchors"]),
        "errors": rep["errors"],
        "signers": sorted({a.get("signer_cn") for a in rep["anchors"]}),
        "fingerprints": sorted({a.get("signer_sha256_fingerprint") for a in rep["anchors"]}),
        "any_test_ca": any(a.get("is_test_ca") for a in rep["anchors"])}
    anchor_out["n_tokens_verified"] += len(rep["anchors"])
    anchor_out["all_ok"] &= rep["ok"]
    anchor_out["all_external"] &= rep["external_valid"]
    anchor_out["any_test_ca"] |= anchor_out["runs"][run_id]["any_test_ca"]
    if not rep["ok"]:
        failures.append(f"anchor verification failed: {run_id}: {rep['errors']}")

# suite anchors (config-at-start, all-chain-heads-at-end)
cfg_digest = hashlib.sha256(open(os.path.join(S001C, "CONFIG.json"), "rb").read()).hexdigest()
heads_digest = hashlib.sha256(json.dumps(
    _final_chain_heads(S001C), sort_keys=True, separators=(",", ":")).encode()).hexdigest()
expected = {"suite_start_config": cfg_digest, "suite_end_all_run_chain_heads": heads_digest}
for line in open(os.path.join(S001C, "suite_anchors.log.jsonl"), encoding="utf-8"):
    a = json.loads(line)
    v = verify_token(base64.b64decode(a["token_b64"]), a["digest"], expected_nonce=a.get("nonce"))
    digest_match = (a["digest"] == expected.get(a["label"]))
    rec = {"label": a["label"], "ok": v["ok"], "digest_matches_recomputed": digest_match,
           "gen_time": v["gen_time"], "signer_cn": v["signer_cn"],
           "is_test_ca": v["is_test_ca"], "errors": v["errors"]}
    anchor_out["suite_anchors"].append(rec)
    anchor_out["n_tokens_verified"] += 1
    if not (v["ok"] and digest_match):
        failures.append(f"suite anchor {a['label']}: ok={v['ok']} digest_match={digest_match}")
    anchor_out["any_test_ca"] |= bool(v["is_test_ca"])
save("anchor_reverification.json", anchor_out)

# ------------------------------------------------------- 2. masked equality
eq = compare_suite(S001C, S001)
save("masked_equality_recheck.json", eq)
if not eq["all_identical"]:
    failures.append("masked equality vs 001 reference failed on recheck")

# --------------------------------------------- 3. validator + replay recheck
# Negative-control ablations are EXPECTED to fail in their designed dimension.
EXPECT = {
    "abl5_disable_precommit": "commitment_errors",
    "abl6_retrieval_replaced_update": "attestation_errors",
    "abl7_remove_raw_all_action_preds": "schema_errors",
    "abl8_force_replay_event": "replay_guard_blocked",
    "abl10_remove_uncertainty_logging": "schema_errors",
}
val_out = {"runs": {}, "consistent_with_001_reference": True}
for run_id in sorted(os.listdir(runs_dir)):
    v_new = validate_run_dir(os.path.join(runs_dir, run_id))
    v_ref = validate_run_dir(os.path.join(S001, "runs", run_id))
    summ = lambda v: {  # noqa: E731
        "ok": v["ok"], "n_schema_errors": len(v["schema_errors"]),
        "replay_guard": v["replay_guard"]["protocol_verdict"],
        "n_chronology_errors": len(v["chronology_errors"]),
        "n_hash_errors": len(v["hash_errors"]),
        "n_commitment_errors": len(v["commitment_errors"]),
        "n_attestation_errors": len(v["attestation_errors"]),
        "replay_applicable": v["replay"].get("applicable"),
        "replay_passed": v["replay"].get("passed"),
        "replay_max_abs_diff": v["replay"].get("max_abs_diff"),
        "records": v["records"]}
    sn, sr = summ(v_new), summ(v_ref)
    designed = EXPECT.get(run_id)
    ok_per_design = sn["ok"] if designed is None else (
        sn["replay_guard"] == "protocol_blocked" if designed == "replay_guard_blocked"
        else sn[f"n_{designed}"] > 0)
    val_out["runs"][run_id] = {"new": sn, "ref_001": sr, "designed_failure": designed,
                               "outcome_matches_design": bool(ok_per_design),
                               "new_equals_ref": sn == sr}
    if sn != sr:
        val_out["consistent_with_001_reference"] = False
        failures.append(f"validator outcome differs from 001 reference: {run_id}")
    if not ok_per_design:
        failures.append(f"validator outcome violates design expectation: {run_id}: {sn}")
save("validator_recheck.json", val_out)

# ------------------------------------- 4. chronology support classification
chron = {"runs": {}, "totals": {"externally_anchored_at_step": 0,
                                "between_anchor_internal_attestation": 0,
                                "uncovered": 0}}
for run_id in sorted(os.listdir(runs_dir)):
    rd = os.path.join(runs_dir, run_id)
    cpath = os.path.join(rd, "commits.log.jsonl")
    apath = os.path.join(rd, "anchors.log.jsonl")
    if not os.path.exists(apath):
        chron["runs"][run_id] = {"skipped": "no anchors (abl5)"}
        continue
    commits = [json.loads(x) for x in open(cpath, encoding="utf-8")]
    anchors = [json.loads(x) for x in open(apath, encoding="utf-8")]
    anchored_seqs = {a["covers_through_seq"] for a in anchors if a["reason"].startswith("interval")}
    max_covered = max(a["covers_through_seq"] for a in anchors)
    at_step = sum(1 for c in commits if c["seq"] in anchored_seqs)
    uncovered = sum(1 for c in commits if c["seq"] > max_covered)
    between = len(commits) - at_step - uncovered
    # consistency: anchor monotonic time precedes the step's own reveal
    posts = {r["t"]: r for r in load_trace(os.path.join(rd, "trace.jsonl"))
             if r.get("event_type") == "POST_STEP"}
    pres = {r["t"]: r for r in load_trace(os.path.join(rd, "trace.jsonl"))
            if r.get("event_type") == "PRE_STEP"}
    anchor_before_own_reveal = []
    by_seq_t = {c["seq"]: c["t"] for c in commits}
    for a in anchors:
        if not a["reason"].startswith("interval"):
            continue
        t = by_seq_t.get(a["covers_through_seq"])
        post = posts.get(t)
        if post is not None:
            anchor_before_own_reveal.append(
                a["anchor_monotonic_ns"] < post["obs_reveal_monotonic_ns"])
    chron["runs"][run_id] = {
        "n_commits": len(commits),
        "externally_anchored_at_step": at_step,
        "between_anchor_internal_attestation": between,
        "uncovered": uncovered,
        "interval_anchor_monotonic_before_own_reveal_all": (
            all(anchor_before_own_reveal) if anchor_before_own_reveal else None),
        "all_reveals_self_reported_wallclock": True}
    for k in ("externally_anchored_at_step", "between_anchor_internal_attestation", "uncovered"):
        chron["totals"][k] += chron["runs"][run_id][k]
    if uncovered:
        failures.append(f"{run_id}: {uncovered} commits not covered by any anchor")
save("chronology_support_map.json", chron)

# ----------------------------------------------- 5. raw evidence inventory
RAW_PRE = ["raw_pred_obs_by_action", "raw_pred_belief_by_action", "belief_pre",
           "theta_T_pre", "theta_O_pre", "uncertainty_pre", "pre_commit_receipt",
           "action_t", "pre_step_hash"]
RAW_POST = ["actual_obs", "nll_error", "brier_component", "belief_post",
            "theta_T_post", "theta_O_post", "transition_responsibility",
            "pred_prob_actual", "obs_reveal_monotonic_ns"]
inv = {"runs": {}}
for run_id in sorted(os.listdir(runs_dir)):
    recs = load_trace(os.path.join(runs_dir, run_id, "trace.jsonl"))
    meta, pres, posts, _ = split_records(recs)
    inv["runs"][run_id] = {
        "n_pre": len(pres), "n_post": len(posts),
        "pre_fields_present": {f: sum(1 for r in pres if f in r) for f in RAW_PRE},
        "post_fields_present": {f: sum(1 for r in posts if f in r) for f in RAW_POST},
        "commit_mode": meta.get("commit_mode"),
        "commit_sink_id": meta.get("commit_sink_id"),
        "retrieval_enabled": meta.get("retrieval_enabled"),
        "replay_enabled": meta.get("replay_enabled")}
save("raw_evidence_inventory.json", inv)

# local_mock scan over the whole 001C suite
lm_hits = []
for root, _dirs, files in os.walk(S001C):
    for fn in files:
        if fn.endswith((".jsonl", ".json", ".md")):
            p = os.path.join(root, fn)
            with open(p, encoding="utf-8", errors="replace") as f:
                for i, line in enumerate(f):
                    if "local_mock" in line:
                        lm_hits.append({"file": os.path.relpath(p, S001C), "line": i + 1,
                                        "snippet": line.strip()[:200]})
save("local_mock_scan.json", {"hits": lm_hits, "n_hits": len(lm_hits)})

# ------------------------------------------ 6. independent E10 recomputation
LOG_EPS = 1e-12
W = 200


def _jsd(p, q):
    def _kl(p, q):
        return sum(x * (math.log(max(x, LOG_EPS)) - math.log(max(q[i], LOG_EPS)))
                   for i, x in enumerate(p) if x > 0.0)
    m = [(a + b) / 2.0 for a, b in zip(p, q)]
    return 0.5 * _kl(p, m) + 0.5 * _kl(q, m)


def recompute(run_dir):
    recs = load_trace(os.path.join(run_dir, "trace.jsonl"))
    _meta, pres, posts, _ = split_records(recs)
    by_t = {p["t"]: p for p in posts}
    nll, jsd_steps, recompute_diff = [], [], 0.0
    for pre in pres:
        post = by_t.get(pre["t"])
        if post is None:
            continue
        raw = pre["raw_pred_obs_by_action"]
        label = pre.get("committed_action_label", pre.get("action_t"))
        p_act = raw[str(label)][post["actual_obs"]]
        n = -math.log(max(p_act, LOG_EPS))
        recompute_diff = max(recompute_diff, abs(n - post["nll_error"]))
        nll.append(n)  # recomputed from raw, NOT the logged nll_error
        dists = [raw[str(a)] for a in range(3)]
        pair = [_jsd(dists[i], dists[j]) for i in range(3) for j in range(i + 1, 3)]
        jsd_steps.append(sum(pair) / len(pair))
    return {"nll_eval_window": sum(nll[-W:]) / len(nll[-W:]),
            "jsd_raw_eval_window": sum(jsd_steps[-W:]) / len(jsd_steps[-W:]),
            "nll_recompute_max_abs_diff_vs_logged": recompute_diff,
            "n_steps": len(nll)}


retr = {"per_run": {}, "components": {}, "gate_reported": None}
for rid in ("core_as", "core_null", "core_shift_reversal",
            "b4_retrieval_as", "b4_retrieval_null", "b4_retrieval_shift"):
    retr["per_run"][rid] = {
        "from_001c_suite": recompute(os.path.join(runs_dir, rid)),
        "from_001_reference": recompute(os.path.join(S001, "runs", rid))}
c = {k: v["from_001c_suite"] for k, v in retr["per_run"].items()}
retr["components"] = {
    "as_nll_gap": c["b4_retrieval_as"]["nll_eval_window"] - c["core_as"]["nll_eval_window"],
    "shift_postshift_nll_gap": (c["b4_retrieval_shift"]["nll_eval_window"]
                                - c["core_shift_reversal"]["nll_eval_window"]),
    "retrieval_jsd_as": c["b4_retrieval_as"]["jsd_raw_eval_window"],
    "retrieval_jsd_null": c["b4_retrieval_null"]["jsd_raw_eval_window"],
    "core_jsd_null": c["core_null"]["jsd_raw_eval_window"],
    "thresholds": {"margin": cfg.THRESHOLDS["baseline_nll_match_margin_nats"],
                   "sep_min": cfg.THRESHOLDS["sep_min_jsd_nats"],
                   "collapse_max": cfg.THRESHOLDS["collapse_max_jsd_nats"]}}
res001 = json.load(open(os.path.join(S001, "result.json")))
for g in res001.get("gates", {}).get("evidence", []):
    if g["gate_id"] == "E10_retrieval_does_not_match":
        retr["gate_reported"] = g["measured"]
comp, rep = retr["components"], retr["gate_reported"]
if rep:
    for k in ("as_nll_gap", "shift_postshift_nll_gap", "retrieval_jsd_as", "retrieval_jsd_null"):
        if abs(comp[k] - rep[k]) > 1e-9:
            failures.append(f"E10 component {k}: independent={comp[k]} vs gate={rep[k]}")
save("retrieval_recompute.json", retr)

# ------------------------------------------------------------ 7. summary
summary = {
    "task_id": "predictive_action_learning_contract_001c_independent_audit",
    "anchors": {"all_ok": anchor_out["all_ok"], "all_external": anchor_out["all_external"],
                "any_test_ca": anchor_out["any_test_ca"],
                "n_tokens_verified": anchor_out["n_tokens_verified"]},
    "masked_equality_all_identical": eq["all_identical"],
    "validator_consistent_with_001": val_out["consistent_with_001_reference"],
    "chronology_totals": chron["totals"],
    "local_mock_hits_in_001c_suite": len(lm_hits),
    "retrieval_components_independent": retr["components"],
    "failures": failures,
}
save("audit_execution_summary.json", summary)
print(json.dumps(summary, indent=1, default=str))
print("\nFAILURES:" if failures else "\nNO FAILURES", *failures, sep="\n")
