"""Suite orchestration: run-spec registry, metric extraction from raw traces,
gate evaluation (task card sections 9.2, 10.2, 11.2, 12, 13), and artifact
generation (section 16). Gates are computed from raw trace records, never from
summaries (section 12.2.18)."""

import json
import os
import re
import subprocess
import sys

from . import config as cfg
from . import metrics as M
from .attestation import NETWORK_POLICY, STORAGE_POLICY, NETWORK_POLICY_HASH, STORAGE_POLICY_HASH
from .trace import (TRACE_SCHEMA, TRACE_SCHEMA_HASH, THRESHOLD_CONFIG_HASH,
                    canonical_json, sha256_hex, load_trace, strip_for_duplicate)
from .validator import split_records, validate_run_dir

TH = cfg.THRESHOLDS


# --------------------------------------------------------------------------- specs

def _base(run_id, group, seed, steps, rule, policy="uniform", **kw):
    spec = {
        "run_id": run_id, "group": group, "seed": seed, "steps": steps,
        "env_rule_id": rule, "policy": policy,
        "eps_T": cfg.EPS_T, "eps_O": cfg.EPS_O,
        "shift_t": None, "ambig_t": None,
        "predictor": {"type": "skeleton", "params": {}},
        "claim_mode": cfg.CLAIM_MODE,
        "baseline_id": "none", "ablation_id": "none", "perturbation_id": "none",
        "declared_retrieval_enabled": False,
    }
    spec.update(kw)
    return spec


def build_specs():
    S = cfg.SEEDS
    groups = {}

    groups["core"] = [
        _base("core_as", "core", S["core_as"], cfg.STEPS_CORE, "AS-CYCLE-001"),
        _base("core_null", "core", S["core_null"], cfg.STEPS_CORE, "NULL-001"),
        _base("core_shift_reversal", "core", S["core_shift_reversal"], cfg.STEPS_SHIFT,
              "SHIFT-REVERSAL-001", shift_t=cfg.SHIFT_T,
              rule_shift_perturbation_id="SHIFT-REVERSAL-001@300",
              perturbation_id="transition_reversal"),
        _base("core_trap", "core", S["core_trap"], cfg.STEPS_CORE, "TRAP-001",
              policy="trap", perturbation_id="spurious_correlation_trap"),
    ]

    def baseline(run_id, regime_spec, ptype, params=None, **kw):
        b = dict(regime_spec)
        b.update({
            "run_id": run_id, "group": "baselines",
            "predictor": {"type": ptype, "params": params or {}},
            "baseline_id": run_id,
            "claim_mode": "baseline_comparison_only",
        })
        b.update(kw)
        return b

    as_, null_, shift_, trap_ = groups["core"]
    groups["baselines"] = [
        baseline("b1_passive_as", as_, "passive"),
        baseline("b2_shuffled_as", as_, "skeleton",
                 {"action_input_mode": "shuffled", "shuffle_seed": 101501,
                  "predictor_id": "baseline_shuffled_action"}),
        baseline("b3_action_token_as", as_, "action_token"),
        baseline("b4_retrieval_as", as_, "retrieval", declared_retrieval_enabled=True),
        baseline("b5_hardcoded_as", as_, "hardcoded"),
        baseline("b6_frozen_theta_at300_as", as_, "skeleton",
                 {"theta_freeze_at_t": cfg.SHIFT_T,
                  "predictor_id": "baseline_frozen_theta_at300"},
                 theta_frozen_baseline_id="frozen_theta@300"),
        baseline("b7_belief_only_as", as_, "skeleton",
                 {"theta_update_enabled": False,
                  "predictor_id": "baseline_belief_only_fixed_theta"}),
        baseline("b8_oracle_leak_as", as_, "oracle"),
        baseline("b1_passive_null", null_, "passive"),
        baseline("b2_shuffled_null", null_, "skeleton",
                 {"action_input_mode": "shuffled", "shuffle_seed": 102501,
                  "predictor_id": "baseline_shuffled_action"}),
        baseline("b3_action_token_null", null_, "action_token"),
        baseline("b4_retrieval_null", null_, "retrieval", declared_retrieval_enabled=True),
        baseline("b5_hardcoded_shift", shift_, "hardcoded"),
        baseline("b6_frozen_theta_at_shift", shift_, "skeleton",
                 {"theta_freeze_at_t": cfg.SHIFT_T,
                  "predictor_id": "baseline_frozen_theta_at_shift"},
                 theta_frozen_baseline_id="frozen_theta@shift"),
        baseline("b4_retrieval_shift", shift_, "retrieval", declared_retrieval_enabled=True),
        baseline("b1_passive_shift", shift_, "passive"),
        baseline("b1_passive_trap", trap_, "passive"),
        baseline("b2_shuffled_trap", trap_, "skeleton",
                 {"action_input_mode": "shuffled", "shuffle_seed": 104501,
                  "predictor_id": "baseline_shuffled_action"}),
        baseline("b3_action_token_trap", trap_, "action_token"),
        baseline("b4_retrieval_trap", trap_, "retrieval", declared_retrieval_enabled=True),
    ]

    def ablation(run_id, base_spec, **kw):
        a = dict(base_spec)
        a.update({"run_id": run_id, "group": "ablations", "ablation_id": run_id})
        a.update(kw)
        return a

    groups["ablations"] = [
        ablation("abl1_remove_action_input", as_,
                 predictor={"type": "skeleton",
                            "params": {"action_input_mode": "none",
                                       "predictor_id": "ablation_no_action_input"}}),
        ablation("abl2_shuffle_action_labels", as_,
                 predictor={"type": "skeleton",
                            "params": {"action_input_mode": "shuffled",
                                       "shuffle_seed": 101502,
                                       "predictor_id": "ablation_shuffled_action"}}),
        ablation("abl3_freeze_theta_as", as_,
                 predictor={"type": "skeleton",
                            "params": {"theta_update_enabled": False,
                                       "predictor_id": "ablation_frozen_theta_init"}}),
        ablation("abl3b_freeze_theta_shift", shift_,
                 predictor={"type": "skeleton",
                            "params": {"theta_update_enabled": False,
                                       "predictor_id": "ablation_frozen_theta_init"}}),
        ablation("abl4_freeze_belief_update", as_,
                 predictor={"type": "skeleton",
                            "params": {"belief_update_enabled": False,
                                       "predictor_id": "ablation_frozen_belief"}}),
        ablation("abl9_delete_memory_reset", as_,
                 memdel_at=cfg.MEMDEL_T, memdel_mode="reset",
                 perturbation_id="memory_deletion_no_reconstruction"),
    ]

    groups["protocol"] = [
        ablation("abl5_disable_precommit", as_, steps=60, commit="disabled"),
        ablation("abl6_retrieval_replaced_update", as_, steps=60,
                 predictor={"type": "retrieval_replaced", "params": {}},
                 declared_retrieval_enabled=False),
        ablation("abl7_remove_raw_all_action_preds", as_, steps=60,
                 drop_fields=["raw_pred_obs_by_action", "raw_pred_belief_by_action"]),
        ablation("abl8_force_replay_event", as_, steps=60, force_replay_at=30),
        ablation("abl10_remove_uncertainty_logging", as_, steps=60,
                 drop_fields=["uncertainty_pre"]),
    ]

    def pert(run_id, **kw):
        p = _base(run_id, "perturbations", kw.pop("seed"), kw.pop("steps"),
                  kw.pop("rule"), **kw)
        p["perturbation_id"] = run_id
        return p

    S_ = cfg.SEEDS
    groups["perturbations"] = [
        pert("pert_obs_noise_low", seed=S_["perturb_obs_noise_low"],
             steps=cfg.STEPS_CORE, rule="AS-CYCLE-001", eps_O=cfg.OBS_NOISE_LOW),
        pert("pert_obs_noise_high", seed=S_["perturb_obs_noise_high"],
             steps=cfg.STEPS_CORE, rule="AS-CYCLE-001", eps_O=cfg.OBS_NOISE_HIGH),
        pert("pert_ambiguous_obs_shift", seed=S_["perturb_ambiguous"],
             steps=cfg.STEPS_CORE, rule="AMBIG-001", ambig_t=cfg.AMBIG_T),
        pert("pert_ambiguous_control", seed=S_["perturb_ambiguous"],
             steps=cfg.STEPS_CORE, rule="AS-CYCLE-001"),
        pert("pert_env_rule_swap", seed=S_["perturb_rule_swap"],
             steps=cfg.STEPS_CORE, rule="AS-SWAP-001"),
        pert("pert_hidden_rule_change", seed=S_["perturb_hidden_rule"],
             steps=cfg.STEPS_SHIFT, rule="HIDDEN-RULE-001", shift_t=cfg.SHIFT_T,
             rule_shift_perturbation_id="HIDDEN-RULE-001@300"),
        pert("pert_memdel_flush_reconstruct", seed=S_["perturb_memdel"],
             steps=cfg.STEPS_CORE, rule="AS-CYCLE-001",
             memdel_at=cfg.MEMDEL_T, memdel_mode="reconstruct"),
        pert("pert_memdel_twin_uninterrupted", seed=S_["perturb_memdel"],
             steps=cfg.STEPS_CORE, rule="AS-CYCLE-001"),
    ]
    return groups


# ----------------------------------------------------------------- suite plumbing

def suite_paths(suite_dir):
    return {"runs": os.path.join(suite_dir, "runs")}


def write_config_artifact(suite_dir):
    groups = build_specs()
    registry = {g: [s["run_id"] for s in specs] for g, specs in groups.items()}
    config_doc = {
        "task_id": cfg.TASK_ID,
        "task_card": cfg.TASK_CARD,
        "claim_mode": cfg.CLAIM_MODE,
        "commit_mode": cfg.COMMIT_MODE,
        "commit_sink_id": cfg.COMMIT_SINK_ID,
        "environment": {
            "n_states": cfg.N_S, "n_actions": cfg.N_A, "n_observations": cfg.N_O,
            "actions": cfg.ACTIONS, "observations": cfg.OBSERVATIONS,
            "eps_T": cfg.EPS_T, "eps_O": cfg.EPS_O,
            "obs_noise_low": cfg.OBS_NOISE_LOW, "obs_noise_high": cfg.OBS_NOISE_HIGH,
            "steps_core": cfg.STEPS_CORE, "steps_shift": cfg.STEPS_SHIFT,
            "shift_t": cfg.SHIFT_T, "ambig_t": cfg.AMBIG_T, "memdel_t": cfg.MEMDEL_T,
            "trap_pref_prob": cfg.TRAP_PREF_PROB,
            "env_rules": cfg.ENV_RULES,
            "rng": "counter-based sha256(seed|t|tag); reconstructible mid-stream",
        },
        "learner": {"alpha_pseudocount": cfg.ALPHA_PSEUDOCOUNT,
                    "eta": cfg.ETA_LEARNING_RATE, "log_eps_smoothing": cfg.LOG_EPS,
                    "init_jitter": cfg.INIT_JITTER,
                    "init_obs_anchor_kappa": cfg.INIT_OBS_ANCHOR_KAPPA,
                    "init_rationale": "T: uninformative + rule-independent seeded "
                    "jitter (must be learned online); O: identity-anchored emission "
                    "prior in pseudo-count vocabulary (perceptual grounding, fixes "
                    "labeling gauge, encodes no transition rule). Cold symmetric and "
                    "jittered-only starts stall at the ln3 plateau; recorded in "
                    "config.py. Frozen update equations unchanged."},
        "retrieval_baseline": {"k_max": 3, "min_match": 3.0, "smoothing": "add-1"},
        "seeds": cfg.SEEDS,
        "thresholds": cfg.THRESHOLDS,
        "threshold_justifications": cfg.THRESHOLD_JUSTIFICATIONS,
        "threshold_config_hash": THRESHOLD_CONFIG_HASH,
        "verdict_precedence": cfg.VERDICT_PRECEDENCE,
        "volatile_fields": cfg.VOLATILE_FIELDS,
        "duplicate_strip_fields": cfg.DUPLICATE_STRIP_FIELDS,
        "registry": registry,
        "specs": {s["run_id"]: s for specs in groups.values() for s in specs},
        "policies": {"storage": STORAGE_POLICY, "network": NETWORK_POLICY,
                     "storage_policy_hash": STORAGE_POLICY_HASH,
                     "network_policy_hash": NETWORK_POLICY_HASH},
        "trace_schema_hash": TRACE_SCHEMA_HASH,
        "declared_before_any_run": True,
    }
    config_manifest_hash = sha256_hex(canonical_json(config_doc))
    config_doc["config_manifest_hash"] = config_manifest_hash
    os.makedirs(suite_dir, exist_ok=True)
    with open(os.path.join(suite_dir, "CONFIG.json"), "w", encoding="utf-8") as f:
        json.dump(config_doc, f, indent=1, sort_keys=True)
    with open(os.path.join(suite_dir, "TRACE_SCHEMA.json"), "w", encoding="utf-8") as f:
        json.dump(TRACE_SCHEMA, f, indent=1, sort_keys=True)
    return config_doc


def load_config_artifact(suite_dir):
    with open(os.path.join(suite_dir, "CONFIG.json"), encoding="utf-8") as f:
        return json.load(f)


def run_group(suite_dir, group):
    from .runner import run_episode
    conf = load_config_artifact(suite_dir)
    specs = [s for s in build_specs()[group]]
    done = []
    for spec in specs:
        spec = dict(spec)
        spec["config_manifest_hash"] = conf["config_manifest_hash"]
        run_dir = os.path.join(suite_dir, "runs", spec["run_id"])
        run_episode(spec, run_dir)
        done.append(spec["run_id"])
    return done


def run_single_spec(suite_dir, spec_json):
    from .runner import run_episode
    conf = load_config_artifact(suite_dir)
    spec = json.loads(spec_json)
    spec["config_manifest_hash"] = conf["config_manifest_hash"]
    run_dir = os.path.join(suite_dir, "runs", spec["run_id"])
    run_episode(spec, run_dir)
    return spec["run_id"]


def run_duplicates(suite_dir, repo_root):
    """Baseline 9: cold-start duplicate runs in fresh subprocesses."""
    base = dict(build_specs()["core"][0])
    ids = []
    for tag in ("dup_a", "dup_b"):
        spec = dict(base)
        spec["run_id"] = f"b9_coldstart_{tag}"
        spec["group"] = "baselines"
        spec["baseline_id"] = "b9_coldstart_duplicate"
        ids.append(spec["run_id"])
        r = subprocess.run(
            [sys.executable, "-m", "predictive_action_learning_contract_001",
             "run-single", "--suite-dir", suite_dir, "--spec-json", json.dumps(spec)],
            cwd=repo_root, capture_output=True, text=True)
        if r.returncode != 0:
            raise RuntimeError(f"duplicate run {tag} failed: {r.stderr[-2000:]}")
    return ids


def compare_record_streams(records_a, records_b):
    sa = [canonical_json(strip_for_duplicate(r)) for r in records_a]
    sb = [canonical_json(strip_for_duplicate(r)) for r in records_b]
    identical = sa == sb
    first_diff = None
    if not identical:
        for i, (x, y) in enumerate(zip(sa, sb)):
            if x != y:
                first_diff = i
                break
        if first_diff is None:
            first_diff = min(len(sa), len(sb))
    return {"identical": identical, "n_a": len(sa), "n_b": len(sb),
            "first_diff_index": first_diff,
            "stream_sha256_a": sha256_hex("\n".join(sa)),
            "stream_sha256_b": sha256_hex("\n".join(sb))}


# ------------------------------------------------------------------ run metrics

def compute_run_metrics(records):
    meta, pres, posts, _ = split_records(records)
    by_t = {p["t"]: p for p in posts}
    nll, brier, ent, jsd_raw, dtheta, dbelief = [], [], [], [], [], []
    jsd_conf = []
    pred_dists, actuals = [], []
    nll_recompute_max_diff = 0.0
    for pre in pres:
        post = by_t.get(pre["t"])
        if post is None:
            continue
        raw = pre.get("raw_pred_obs_by_action")
        label = pre.get("committed_action_label", pre.get("action_t"))
        if raw is not None:
            import math
            chosen = raw[str(label)]
            p = chosen[post["actual_obs"]]
            n = -math.log(max(p, cfg.LOG_EPS))
            nll_recompute_max_diff = max(nll_recompute_max_diff,
                                         abs(n - post["nll_error"]))
            pred_dists.append(chosen)
            actuals.append(post["actual_obs"])
        nll.append(post["nll_error"])
        brier.append(post["brier_component"])
        if "uncertainty_pre" in pre:
            ent.append(pre["uncertainty_pre"])
        asm = pre.get("action_sensitivity_metric") or {}
        if "jsd_mean_raw_nats" in asm:
            jsd_raw.append(asm["jsd_mean_raw_nats"])
        if "jsd_mean_confident_nats" in asm:
            jsd_conf.append(asm["jsd_mean_confident_nats"])
        dt = post.get("delta_theta_derived")
        dtheta.append(dt["l1_total"] if dt else 0.0)
        db = post.get("delta_belief")
        dbelief.append(db["l1"] if db else 0.0)

    W = TH["eval_window_steps"]
    ece_val, ece_report = M.ece(pred_dists, actuals, TH["ece_num_bins"],
                                TH["ece_min_total_samples"],
                                TH["ece_min_nonempty_bins"],
                                TH["ece_min_bin_samples"]) if pred_dists else (None, {})
    out = {
        "run_id": meta["run_id"] if meta else None,
        "predictor_id": meta.get("predictor_id") if meta else None,
        "env_rule_id": meta.get("env_rule_id") if meta else None,
        "steps": len(nll),
        "nll_mean": M.mean(nll), "nll_eval_window": M.window_mean(nll, W),
        "brier_mean": M.mean(brier), "brier_eval_window": M.window_mean(brier, W),
        "entropy_mean": M.mean(ent), "entropy_eval_window": M.window_mean(ent, W),
        "jsd_raw_mean": M.mean(jsd_raw), "jsd_raw_eval_window": M.window_mean(jsd_raw, W),
        "jsd_confident_eval_window": M.window_mean(jsd_conf, W),
        "rolling_nll_last": M.rolling_mean(nll, TH["rolling_window_steps"])[-1] if nll else None,
        "delta_belief_l1_mean": M.mean(dbelief),
        "delta_theta_l1_mean": M.mean(dtheta),
        "nll_recompute_max_abs_diff": nll_recompute_max_diff,
        "ece": ece_report,
        "series": {"nll": nll, "jsd_raw": jsd_raw, "entropy": ent,
                   "delta_theta_l1": dtheta},
    }
    shift_t = meta.get("shift_t") if meta else None
    if shift_t:
        w = TH["delta_theta_window_steps"]
        pre_w = dtheta[max(0, shift_t - w):shift_t]
        post_w = dtheta[shift_t:shift_t + w]
        out["shift_analysis"] = {
            "shift_t": shift_t,
            "nll_postshift_eval_window": M.window_mean(nll, W),
            "nll_immediate_postshift": M.mean(nll[shift_t:shift_t + w]),
            "delta_theta_preshift_window_mean": M.mean(pre_w),
            "delta_theta_postshift_window_mean": M.mean(post_w),
            "delta_theta_ratio": (M.mean(post_w) / M.mean(pre_w)
                                  if pre_w and M.mean(pre_w) and M.mean(pre_w) > 0 else None),
        }
    ambig_t = meta.get("ambig_t") if meta else None
    if ambig_t:
        out["ambig_analysis"] = {
            "ambig_t": ambig_t,
            "entropy_pre_window": M.mean(ent[max(0, ambig_t - W):ambig_t]),
            "entropy_post_window": M.mean(ent[-W:]),
        }
    mem_t = cfg.MEMDEL_T
    if len(nll) > mem_t + TH["memdel_reset_window_steps"]:
        w = TH["memdel_reset_window_steps"]
        out["memdel_analysis"] = {
            "nll_before_window": M.mean(nll[mem_t - w:mem_t]),
            "nll_after_window": M.mean(nll[mem_t:mem_t + w]),
        }
    return out
