"""Single-run executor enforcing the per-step protocol order:

  1. external policy picks a_t
  2. learner produces raw all-action predictions (audited window)
  3. PRE_STEP content is serialized, hashed, committed to the sink (flush)
  4. only then does the environment sample and reveal o_{t+1}
  5. learner updates (audited window); POST_STEP is written

The environment object is constructed so that o_{t+1} is not computed anywhere
before step 4 (counter-based draws happen inside transition()).
"""

import math
import time
import uuid
import os

from . import config as cfg
from . import environment as envmod
from . import metrics as M
from .attestation import (AuditMonitor, NETWORK_POLICY_HASH, STORAGE_POLICY_HASH,
                          runtime_manifest_hash)
from .commitment import DisabledCommitSink, LocalMockCommitSink, utc_now
from .predictors import (ActionTokenOnlyPredictor, HardcodedRuleFilterPredictor,
                         NearestHistoryRetrievalPredictor, OracleLeakPredictor,
                         PassiveObsMarkovPredictor, RetrievalReplacedUpdatePredictor,
                         SkeletonPredictor)
from .trace import (TRACE_SCHEMA_HASH, THRESHOLD_CONFIG_HASH, TraceWriter,
                    content_hash)

_PKG_DIR = os.path.dirname(os.path.abspath(__file__))
_RUNTIME_MANIFEST_HASH = None


def get_runtime_manifest_hash():
    global _RUNTIME_MANIFEST_HASH
    if _RUNTIME_MANIFEST_HASH is None:
        _RUNTIME_MANIFEST_HASH = runtime_manifest_hash(_PKG_DIR)
    return _RUNTIME_MANIFEST_HASH


def _initial_target_fn(env_rule_id):
    if env_rule_id in ("AS-CYCLE-001", "SHIFT-REVERSAL-001", "HIDDEN-RULE-001", "AMBIG-001"):
        return envmod._target_as_cycle
    if env_rule_id == "AS-SWAP-001":
        return envmod._target_as_swap
    if env_rule_id in ("NULL-001", "TRAP-001"):
        return envmod._target_null
    raise ValueError(env_rule_id)


def build_predictor(spec, env):
    p = spec["predictor"]
    typ, params = p["type"], dict(p.get("params") or {})
    if typ == "skeleton":
        params.setdefault("init_seed", spec["seed"])
        return SkeletonPredictor(cfg, **params)
    if typ == "passive":
        return PassiveObsMarkovPredictor(cfg)
    if typ == "action_token":
        return ActionTokenOnlyPredictor(cfg)
    if typ == "retrieval":
        return NearestHistoryRetrievalPredictor(cfg)
    if typ == "retrieval_replaced":
        return RetrievalReplacedUpdatePredictor(cfg)
    if typ == "hardcoded":
        return HardcodedRuleFilterPredictor(
            cfg, _initial_target_fn(spec["env_rule_id"]), spec["eps_T"], spec["eps_O"])
    if typ == "oracle":
        return OracleLeakPredictor(cfg, env)
    raise ValueError(typ)


def _skeleton_params_for_meta(spec):
    p = spec["predictor"]
    if p["type"] not in ("skeleton",):
        return None
    d = dict(p.get("params") or {})
    return {
        "action_input_mode": d.get("action_input_mode", "true"),
        "shuffle_seed": d.get("shuffle_seed"),
        "theta_update_enabled": d.get("theta_update_enabled", True),
        "theta_freeze_at_t": d.get("theta_freeze_at_t"),
        "belief_update_enabled": d.get("belief_update_enabled", True),
        "init_seed": d.get("init_seed", spec["seed"]),
        "init_jitter": cfg.INIT_JITTER,
        "init_obs_anchor_kappa": cfg.INIT_OBS_ANCHOR_KAPPA,
    }


def build_commit_sink(spec, run_dir):
    """Declared 001C seam: commit value -> sink. 001 behavior is unchanged
    (local_mock / disabled); 'rfc3161_anchored' lazily imports the isolated
    001C sink so the frozen 001 package keeps zero new dependencies."""
    kind = spec.get("commit") or "local_mock"
    if kind == "disabled":
        s = DisabledCommitSink()
        s.mode = "disabled"
        return s
    if kind == "local_mock":
        s = LocalMockCommitSink(os.path.join(run_dir, "commits.log.jsonl"))
        s.mode = "local_mock"
        return s
    if kind == "rfc3161_anchored":
        from predictive_action_learning_contract_001c.sink import AnchoredRFC3161Sink
        return AnchoredRFC3161Sink(run_dir, spec)
    raise ValueError(f"unknown commit mode {kind}")


def run_episode(spec, run_dir):
    os.makedirs(run_dir, exist_ok=True)
    monitor = AuditMonitor.instance()
    env = envmod.FiniteEnv(spec["env_rule_id"], spec["seed"], spec["eps_T"],
                           spec["eps_O"], shift_t=spec.get("shift_t"),
                           ambig_t=spec.get("ambig_t"))
    policy = (envmod.TrapPolicy(spec["seed"], cfg.TRAP_PREF_PROB)
              if spec["policy"] == "trap" else envmod.UniformPolicy(spec["seed"]))
    predictor = build_predictor(spec, env)

    sink = build_commit_sink(spec, run_dir)
    writer = TraceWriter(os.path.join(run_dir, "trace.jsonl"),
                         drop_fields=spec.get("drop_fields"))
    cache_epoch_id = str(uuid.uuid4())
    skeleton_params = _skeleton_params_for_meta(spec)

    meta = {
        "event_type": "RUN_META",
        "run_id": spec["run_id"],
        "task_id": cfg.TASK_ID,
        "task_card": cfg.TASK_CARD,
        "random_seed": spec["seed"],
        "env_rule_id": spec["env_rule_id"],
        "action_schema": {"n": cfg.N_A, "labels": cfg.ACTIONS},
        "obs_schema": {"n": cfg.N_O, "labels": cfg.OBSERVATIONS},
        "state_schema": {"n": cfg.N_S, "labels": cfg.STATES,
                         "note": "latent; never visible to any predictor"},
        "serializer_version": cfg.SERIALIZER_VERSION,
        "trace_schema_hash": TRACE_SCHEMA_HASH,
        "ablation_id": spec.get("ablation_id", "none"),
        "perturbation_id": spec.get("perturbation_id", "none"),
        "baseline_id": spec.get("baseline_id", "none"),
        "retrieval_enabled": bool(spec.get("declared_retrieval_enabled", False)),
        "replay_enabled": False,
        "runtime_attestation_ref": "attestation_report.json",
        "runtime_manifest_hash": get_runtime_manifest_hash(),
        "config_manifest_hash": spec["config_manifest_hash"],
        "storage_policy_hash": STORAGE_POLICY_HASH,
        "network_policy_hash": NETWORK_POLICY_HASH,
        "claim_mode": spec.get("claim_mode", cfg.CLAIM_MODE),
        "commit_mode": sink.mode,
        "commit_sink_id": sink.sink_id,
        "threshold_config_hash": THRESHOLD_CONFIG_HASH,
        "policy_id": policy.policy_id,
        "predictor_id": predictor.predictor_id,
        "predictor_params": skeleton_params,
        "replayable_skeleton": bool(predictor.replayable_skeleton),
        "steps": spec["steps"],
        "eps_T": spec["eps_T"],
        "eps_O": spec["eps_O"],
        "shift_t": spec.get("shift_t"),
        "ambig_t": spec.get("ambig_t"),
        "action_sensitive_regime_id": "AS-CYCLE-001",
        "null_control_regime_id": "NULL-001",
        "cold_start_marker": True,
        "cache_epoch_id": cache_epoch_id,
        "group": spec.get("group"),
    }
    records = [writer.write(meta)]

    o_t = env.sample_initial_obs()
    predictor.reset(o_t)
    ext_access_running = 0

    for t in range(spec["steps"]):
        # ---- perturbation hooks -------------------------------------------------
        if spec.get("force_replay_at") == t:
            records.append(writer.write({
                "event_type": "REPLAY_STEP", "t": t,
                "note": "forced by ablation 8; must trigger protocol_blocked"}))
        if spec.get("memdel_at") == t:
            if spec.get("memdel_mode") == "reset":
                predictor = build_predictor(spec, env)
                predictor.reset(o_t)
            else:  # reconstruct strictly from the trace written so far
                from .validator import reconstruct_skeleton_from_trace
                predictor = reconstruct_skeleton_from_trace(records, t)

        a_t = policy.act(t, env.s_true)

        with monitor.window():
            pobs_by_a, bhat_by_a = predictor.predict_all(t)
        ext_pred = monitor.window_count

        label = predictor.chosen_action_label(t, a_t)
        chosen = pobs_by_a[label]
        jsd_raw = M.jsd_mean_pairwise([pobs_by_a[a] for a in range(cfg.N_A)])
        pre = {
            "event_type": "PRE_STEP",
            "t": t,
            "obs_t": o_t,
            "belief_pre": predictor.belief(),
            "theta_T_pre": predictor.theta_T(),
            "theta_O_pre": predictor.theta_O(),
            "action_t": a_t,
            "committed_action_label": label,
            "raw_pred_obs_by_action": {str(a): pobs_by_a[a] for a in range(cfg.N_A)},
            "raw_pred_belief_by_action": (None if bhat_by_a is None else
                                          {str(a): bhat_by_a[a] for a in range(cfg.N_A)}),
            "uncertainty_pre": M.entropy(chosen),
            "action_sensitivity_metric": {
                "jsd_mean_raw_nats": jsd_raw,
                "jsd_mean_confident_nats": M.jsd_mean_confident(
                    [pobs_by_a[a] for a in range(cfg.N_A)],
                    cfg.THRESHOLDS["entropy_confident_max_nats"]),
                "entropy_by_action_nats": [M.entropy(pobs_by_a[a]) for a in range(cfg.N_A)],
            },
            "action_sensitive_regime_id": "AS-CYCLE-001",
            "null_control_regime_id": "NULL-001",
            "action_sensitivity_acceptance_threshold": {
                "sep_min_jsd_nats": cfg.THRESHOLDS["sep_min_jsd_nats"],
                "collapse_max_jsd_nats": cfg.THRESHOLDS["collapse_max_jsd_nats"],
            },
            "commit_sink_id": sink.sink_id,
            "receipt_type": sink.receipt_type,
            "receipt_verifier_key_id": sink.receipt_verifier_key_id,
        }
        pre["pre_step_hash"] = content_hash(pre)
        pre["pre_commit_receipt"] = sink.commit(t, pre["pre_step_hash"])
        records.append(writer.write(pre))

        # ---- outcome is sampled only now ---------------------------------------
        o_next, _s_next = env.transition(t, a_t)
        reveal_ns = time.monotonic_ns()
        reveal_ts = utc_now()

        with monitor.window():
            upd = predictor.observe(t, a_t, o_next)
        ext_obs = monitor.window_count
        ext_access_running += ext_pred + ext_obs

        p_actual = chosen[o_next]
        theta_T_post = predictor.theta_T()
        theta_O_post = predictor.theta_O()
        delta_theta = None
        if theta_T_post is not None:
            delta_theta = {
                "l1_T": M.l1_nested(theta_T_post, pre["theta_T_pre"]),
                "l1_O": M.l1_nested(theta_O_post, pre["theta_O_pre"]),
            }
            delta_theta["l1_total"] = delta_theta["l1_T"] + delta_theta["l1_O"]
        belief_post = predictor.belief()
        delta_belief = None
        if belief_post is not None and pre["belief_pre"] is not None:
            delta_belief = {"l1": M.l1(belief_post, pre["belief_pre"])}

        post = {
            "event_type": "POST_STEP",
            "t": t,
            "actual_obs": o_next,
            "obs_reveal_ts": reveal_ts,
            "obs_reveal_monotonic_ns": reveal_ns,
            "pred_prob_actual": p_actual,
            "nll_error": -math.log(max(p_actual, cfg.LOG_EPS)),
            "brier_component": M.brier_component(chosen, o_next),
            "transition_responsibility": upd.get("xi") if isinstance(upd, dict) else None,
            "belief_post": belief_post,
            "delta_belief": delta_belief,
            "theta_T_post": theta_T_post,
            "theta_O_post": theta_O_post,
            "delta_theta_derived": delta_theta,
            "pre_step_hash_ref": pre["pre_step_hash"],
            "external_memory_access_count": ext_pred + ext_obs,
            "replay_step_count": 0,
            "retrieval_event_log": predictor.pop_retrieval_events(),
            "cache_epoch_id": cache_epoch_id,
            "theta_frozen_baseline_id": spec.get("theta_frozen_baseline_id", "none"),
            "rule_shift_perturbation_id": spec.get("rule_shift_perturbation_id", "none"),
        }
        post["post_step_hash"] = content_hash(post)
        records.append(writer.write(post))
        o_t = o_next

    writer.close()
    sink.close()
    return records
