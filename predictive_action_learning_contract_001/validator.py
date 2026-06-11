"""Trace validation and replay (task card sections 7, 12.2, 13).

Checks performed on a run directory:
  schema        - required fields present per event type
  replay_guard  - any REPLAY_STEP in a core run => protocol_blocked / replay_contamination
  chronology    - commitment strictly precedes outcome reveal, per step
  hashes        - content hashes and chain hashes recompute exactly
  commitments   - receipts match the append-only commit log (seq + payload hash)
  attestation   - measured external memory access == 0; declared flags consistent
                  with logged retrieval events
  replay        - for skeleton runs: rebuild the learner from t=0 using only the
                  frozen equations and logged (action, observation) stream; every
                  logged belief/theta/prediction/responsibility must match within
                  the pre-declared tolerance. No hidden state may be needed.
"""

import math

from . import config as cfg
from .commitment import load_commit_log
from .predictors import SkeletonPredictor
from .trace import TRACE_SCHEMA, content_hash, canonical_json, sha256_hex, load_trace


def _required(event_type):
    return TRACE_SCHEMA["required_fields"][event_type]


def split_records(records):
    meta = [r for r in records if r.get("event_type") == "RUN_META"]
    pres = [r for r in records if r.get("event_type") == "PRE_STEP"]
    posts = [r for r in records if r.get("event_type") == "POST_STEP"]
    replays = [r for r in records if r.get("event_type") == "REPLAY_STEP"]
    return (meta[0] if meta else None), pres, posts, replays


def validate_schema(records):
    errors = []
    for i, r in enumerate(records):
        et = r.get("event_type")
        if et not in ("RUN_META", "PRE_STEP", "POST_STEP", "REPLAY_STEP"):
            errors.append(f"record {i}: unknown event_type {et}")
            continue
        if et == "REPLAY_STEP":
            continue
        for f in _required(et):
            if f not in r:
                errors.append(f"record {i} ({et} t={r.get('t')}): missing required field '{f}'")
    return errors


def validate_replay_guard(records):
    _meta, _pres, _posts, replays = split_records(records)
    if replays:
        return {"protocol_verdict": "protocol_blocked",
                "reason": "replay_contamination",
                "replay_step_ts": [r.get("t") for r in replays]}
    return {"protocol_verdict": "ok", "reason": None, "replay_step_ts": []}


def validate_chronology(records):
    errors = []
    meta, pres, posts, _ = split_records(records)
    if meta is None:
        return ["missing RUN_META"]
    if len(pres) != len(posts):
        errors.append(f"PRE/POST count mismatch: {len(pres)} vs {len(posts)}")
    by_t_post = {p["t"]: p for p in posts}
    last_t = -1
    for pre in pres:
        t = pre["t"]
        if t <= last_t:
            errors.append(f"t={t}: non-monotonic PRE_STEP order")
        last_t = t
        post = by_t_post.get(t)
        if post is None:
            errors.append(f"t={t}: PRE_STEP without POST_STEP")
            continue
        rcpt = pre.get("pre_commit_receipt")
        if rcpt is None:
            if meta.get("commit_mode") != "disabled":
                errors.append(f"t={t}: missing pre_commit_receipt with commit_mode != disabled")
            continue
        if rcpt["commit_monotonic_ns"] >= post["obs_reveal_monotonic_ns"]:
            errors.append(f"t={t}: commit_monotonic_ns >= obs_reveal_monotonic_ns "
                          "(commitment did not precede reveal)")
        if rcpt["payload_sha256"] != pre.get("pre_step_hash"):
            errors.append(f"t={t}: committed payload hash != pre_step_hash")
        if post.get("pre_step_hash_ref") != pre.get("pre_step_hash"):
            errors.append(f"t={t}: post.pre_step_hash_ref mismatch")
    return errors


def validate_hashes(records):
    errors = []
    prev_chain = ""
    for i, r in enumerate(records):
        et = r.get("event_type")
        body = {k: v for k, v in r.items() if k != "chain_hash"}
        expect_chain = sha256_hex(prev_chain + canonical_json(body))
        if r.get("chain_hash") != expect_chain:
            errors.append(f"record {i} ({et} t={r.get('t')}): chain_hash mismatch")
        prev_chain = r.get("chain_hash", expect_chain)
        if et == "PRE_STEP" and "pre_step_hash" in r:
            if content_hash(r) != r["pre_step_hash"]:
                errors.append(f"t={r.get('t')}: pre_step_hash does not recompute")
        if et == "POST_STEP" and "post_step_hash" in r:
            if content_hash(r) != r["post_step_hash"]:
                errors.append(f"t={r.get('t')}: post_step_hash does not recompute")
    return errors


def validate_commitments(records, commit_log_path):
    errors = []
    meta, pres, _posts, _ = split_records(records)
    if meta is None:
        return ["missing RUN_META"]
    if meta.get("commit_mode") == "disabled":
        return ["commit_mode=disabled: no commitments to verify (evidence must be blocked)"]
    try:
        log = load_commit_log(commit_log_path)
    except FileNotFoundError:
        return ["commit log file missing"]
    if len(log) != len(pres):
        errors.append(f"commit log has {len(log)} entries for {len(pres)} PRE_STEPs")
    for i, (entry, pre) in enumerate(zip(log, pres)):
        if entry["seq"] != i:
            errors.append(f"commit log seq {entry['seq']} != {i}")
        if entry["t"] != pre["t"]:
            errors.append(f"commit log t {entry['t']} != PRE_STEP t {pre['t']}")
        if entry["payload_sha256"] != pre.get("pre_step_hash"):
            errors.append(f"t={pre['t']}: commit log payload hash mismatch")
        r = pre.get("pre_commit_receipt") or {}
        if r.get("seq") != entry["seq"] or r.get("payload_sha256") != entry["payload_sha256"]:
            errors.append(f"t={pre['t']}: receipt does not match commit log entry")
    return errors


def validate_attestation(records):
    errors = []
    meta, _pres, posts, _ = split_records(records)
    if meta is None:
        return ["missing RUN_META"]
    declared_retrieval = meta.get("retrieval_enabled")
    total_ext = 0
    retrieval_logged = 0
    for p in posts:
        total_ext += p.get("external_memory_access_count", 0)
        retrieval_logged += len(p.get("retrieval_event_log") or [])
        if p.get("replay_step_count", 0) != 0:
            errors.append(f"t={p['t']}: replay_step_count != 0")
    if total_ext != 0:
        errors.append(f"measured external memory access count = {total_ext} (must be 0)")
    if declared_retrieval is False and retrieval_logged > 0:
        errors.append(
            f"declared retrieval_enabled=false but {retrieval_logged} retrieval events "
            "logged: self-reported flag contradicted by mechanism-level evidence")
    if meta.get("replay_enabled") is not False:
        errors.append("replay_enabled must be declared false in core protocol")
    return errors


def replay_skeleton_run(records, tol=None):
    """Full-trace replay for skeleton-class runs. Reconstructs every logged
    quantity from the frozen equations + logged (action, obs) stream only."""
    tol = tol if tol is not None else cfg.THRESHOLDS["replay_abs_tolerance"]
    meta, pres, posts, _ = split_records(records)
    if meta is None or not meta.get("replayable_skeleton"):
        return {"applicable": False, "passed": None,
                "note": "not a skeleton-class run; replay validation not applicable"}
    params = meta["predictor_params"]
    pred = SkeletonPredictor(
        cfg,
        action_input_mode=params["action_input_mode"],
        shuffle_seed=params["shuffle_seed"],
        theta_update_enabled=params["theta_update_enabled"],
        theta_freeze_at_t=params["theta_freeze_at_t"],
        belief_update_enabled=params["belief_update_enabled"],
        init_seed=params.get("init_seed"))
    pred.reset(pres[0]["obs_t"])
    max_diff = 0.0
    mismatches = []
    by_t_post = {p["t"]: p for p in posts}

    def _chk(t, name, got, want):
        nonlocal max_diff
        d = _max_abs_diff(got, want)
        if d is not None:
            max_diff = max(max_diff, d)
            if d > tol and len(mismatches) < 20:
                mismatches.append({"t": t, "field": name, "max_abs_diff": d})

    for pre in pres:
        t = pre["t"]
        post = by_t_post[t]
        _chk(t, "belief_pre", pred.belief(), pre["belief_pre"])
        _chk(t, "theta_T_pre", pred.theta_T(), pre["theta_T_pre"])
        _chk(t, "theta_O_pre", pred.theta_O(), pre["theta_O_pre"])
        pobs, bhat = pred.predict_all(t)
        for a in range(cfg.N_A):
            _chk(t, f"raw_pred_obs_by_action[{a}]", pobs[a],
                 pre["raw_pred_obs_by_action"][str(a)])
            _chk(t, f"raw_pred_belief_by_action[{a}]", bhat[a],
                 pre["raw_pred_belief_by_action"][str(a)])
        label = pred.chosen_action_label(t, pre["action_t"])
        if label != pre["committed_action_label"]:
            mismatches.append({"t": t, "field": "committed_action_label",
                               "max_abs_diff": float(abs(label - pre["committed_action_label"]))})
        p_actual = pobs[label][post["actual_obs"]]
        _chk(t, "pred_prob_actual", [p_actual], [post["pred_prob_actual"]])
        _chk(t, "nll_error", [-math.log(max(p_actual, cfg.LOG_EPS))], [post["nll_error"]])
        upd = pred.observe(t, pre["action_t"], post["actual_obs"])
        _chk(t, "transition_responsibility", upd["xi"], post["transition_responsibility"])
        _chk(t, "belief_post", upd["belief_post"], post["belief_post"])
        _chk(t, "theta_T_post", pred.theta_T(), post["theta_T_post"])
        _chk(t, "theta_O_post", pred.theta_O(), post["theta_O_post"])
    passed = (not mismatches) and max_diff <= tol
    return {"applicable": True, "passed": passed, "steps_replayed": len(pres),
            "max_abs_diff": max_diff, "tolerance": tol, "mismatches": mismatches,
            "hidden_state_needed": not passed,
            "note": "behavior reconstructed from trace + frozen equations only"}


def reconstruct_skeleton_from_trace(records, upto_t):
    """Rebuild learner state strictly from trace records with t < upto_t.
    Used by the cache-flush perturbation. Raises if the run is not skeleton-class."""
    meta, pres, posts, _ = split_records(records)
    params = meta["predictor_params"]
    pred = SkeletonPredictor(
        cfg,
        action_input_mode=params["action_input_mode"],
        shuffle_seed=params["shuffle_seed"],
        theta_update_enabled=params["theta_update_enabled"],
        theta_freeze_at_t=params["theta_freeze_at_t"],
        belief_update_enabled=params["belief_update_enabled"],
        init_seed=params.get("init_seed"))
    pred.reset(pres[0]["obs_t"])
    by_t_post = {p["t"]: p for p in posts}
    for pre in pres:
        if pre["t"] >= upto_t:
            break
        pred.predict_all(pre["t"])
        pred.observe(pre["t"], pre["action_t"], by_t_post[pre["t"]]["actual_obs"])
    return pred


def _max_abs_diff(a, b):
    if a is None and b is None:
        return 0.0
    if a is None or b is None:
        return float("inf")
    if isinstance(a, dict):
        keys = set(a) | set(b)
        return max((_max_abs_diff(a.get(k), b.get(k)) for k in keys), default=0.0)
    if isinstance(a, (list, tuple)):
        if len(a) != len(b):
            return float("inf")
        return max((_max_abs_diff(x, y) for x, y in zip(a, b)), default=0.0)
    return abs(float(a) - float(b))


def validate_run_dir(run_dir):
    records = load_trace(f"{run_dir}/trace.jsonl")
    meta, _p, _q, _r = split_records(records)
    schema_errors = validate_schema(records)
    guard = validate_replay_guard(records)
    chrono = validate_chronology(records)
    hashes = validate_hashes(records)
    commits = validate_commitments(records, f"{run_dir}/commits.log.jsonl")
    attest = validate_attestation(records)
    try:
        replay = replay_skeleton_run(records)
    except Exception as e:  # malformed/dropped-field traces must fail closed
        replay = {"applicable": True, "passed": False,
                  "error": f"replay impossible from trace: {e!r}"}
    commit_blocked = meta is not None and meta.get("commit_mode") == "disabled"
    ok = (not schema_errors and guard["protocol_verdict"] == "ok" and not chrono
          and not hashes and not attest and replay.get("passed") in (True, None)
          and (not commits or commit_blocked))
    return {
        "run_id": meta.get("run_id") if meta else None,
        "ok": ok,
        "schema_errors": schema_errors,
        "replay_guard": guard,
        "chronology_errors": chrono,
        "hash_errors": hashes,
        "commitment_errors": commits,
        "attestation_errors": attest,
        "replay": replay,
        "records": len(records),
    }
