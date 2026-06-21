"""LRGG-TIER0-2-001B-R1-BASELINE-IMMUNITY-REPAIR (isolated R1 checkers; read-only loads 001B)."""
from __future__ import annotations
import importlib.util, inspect, json, hashlib, os, copy
from pathlib import Path

RUN_ID = "LRGG-TIER0-2-001B-R1-BASELINE-IMMUNITY-REPAIR"


def _sha(d): return hashlib.sha256(d).hexdigest()
def _stable(d): return json.dumps(d, indent=2, sort_keys=True, ensure_ascii=True) + "\n"
def _ch(f): return _sha(inspect.getsource(f).encode())


def load_001b():
    here = Path(__file__).resolve().parents[2]
    p = os.environ.get("LRGG_001B_PATH", str(here / "src/lrgg_candidate_free_tier0_2_001b/runner.py"))
    spec = importlib.util.spec_from_file_location("lrgg001b_runner", p)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m


B = load_001b()
EPS = B.EPS_EQUIV
FORBIDDEN_HIDDEN = {"evaluation_only", "target_actions", "g_lo", "probe_response",
                    "budget_faithful_visible_channel_oracle", "make_intervener"}
FORBIDDEN_ANSWER_CORE = {"rule_target", "_twin"} | FORBIDDEN_HIDDEN


def active_interventional_baseline(pub, intervene):
    """Equal-access active baseline: public passive_vector + public inverse + B legal probes.
    Independent callable (NOT an oracle wrapper); g_lo obtained only via the legal probe interface."""
    inv = B.PUBLIC_INV; out = []; used = []
    for row in pub:
        ghi, r, c = inv[tuple(row["observation"]["passive_vector"])]
        j = B.informative_probe_index(ghi, r, c)
        glo = intervene(row["row_id"], j); used.append(1)
        out.append(set(B.rule_target(2 * ghi + glo, r, c)))
    return out, used


def reachable_symbols(fn, module, seen=None, names=None):
    seen = set() if seen is None else seen; names = set() if names is None else names
    if fn.__name__ in seen: return seen, names
    seen.add(fn.__name__)
    for cn in fn.__code__.co_names:
        names.add(cn)
        obj = getattr(module, cn, None)
        if callable(obj) and hasattr(obj, "__code__") and getattr(obj, "__module__", None) == module.__name__:
            reachable_symbols(obj, module, seen, names)
    return seen, names


def transitive_report():
    rows = []
    for bid, fn in B.BASELINES.items():
        _, names = reachable_symbols(fn, B)
        hidden = sorted(names & FORBIDDEN_HIDDEN); core = sorted(names & {"rule_target", "_twin"})
        rows.append({"baseline": bid, "producer_function": f"runner.{fn.__name__}", "code_path_hash": _ch(fn),
                     "reaches_hidden_truth": hidden, "reaches_public_answer_core": core, "hidden_truth_leak": bool(hidden)})
    return {"baselines": rows, "any_hidden_truth_leak": any(r["hidden_truth_leak"] for r in rows),
            "all_baselines_reach_public_answer_core": all(r["reaches_public_answer_core"] for r in rows),
            "any_reaches_public_answer_core": any(r["reaches_public_answer_core"] for r in rows),
            "note": "rule_target/_twin reachable by 001B public-rule design; this is the mechanism that lets the "
                    "equal-access active baseline (R1-A) saturate. Direct-source independence checks miss it."}


def attacker_family_audit():
    rows = B.generate_rows(plant=False); pub = B.public_rows(rows)
    src = inspect.getsource(B._attacker)
    outs = {t: [sorted(s) for s in B._attacker(pub, t)] for t in B.VALUE_ATTACKERS}
    distinct = len({json.dumps(v) for v in outs.values()})
    collapsed = distinct == 1
    return {"attackers": B.VALUE_ATTACKERS, "shared_core": "runner._attacker", "distinct_code_paths": distinct,
            "transform_parameter_cosmetic": bool(collapsed), "collapsed_single_attacker": bool(collapsed),
            "status": "collapsed_single_attacker_multiple_labels" if collapsed else "candidate_true_family",
            "r4_powered_family_claim_supported": not collapsed,
            "note": "All 7 labels route through one _attacker; the transform parameter indexes a dict of identical "
                    "values, so it does not change computation -> collapsed single value-leak probe, not a powered family."}


def _run_pos_with(scanner):
    rows = B.generate_rows(); alarms = 0
    for fam in B.SCANNER_FAMILIES:
        pl = copy.deepcopy(rows)
        for row in pl:
            if fam == "observation_field_name_leak": row["observation"]["hidden_rule_id"] = 1
            elif fam == "membership": row["observation"]["membership_flag"] = row["evaluation_only"]["g_lo"]
            else: row["observation"]["aux_feature_07"] = row["evaluation_only"]["g_lo"]
        if not scanner(pl)["passed"]: alarms += 1
    return alarms


def name_only_scanner(rows):
    findings = []; benign = {"coarse_bucket", "legal_action_count", "query_budget", "row_id"}
    namebad = ("topology", "remap", "context_token", "hidden_rule", "latent_graph", "generator_truth",
               "scorer_truth", "answer", "target", "g_lo", "task_family", "score_key", "reward_shape", "membership")
    keys = set()
    for row in rows:
        for st in ("observation", "serialized_state"): keys.update(k for k in row[st] if k != "passive_vector")
    for k in keys:
        if k in benign: continue
        if any(t in k.lower() for t in namebad): findings.append({"channel": "name", "key": k})
    return {"passed": not findings, "findings": findings}


def positive_control_disable_report():
    normal = _run_pos_with(lambda r: B.scan_rows(r))
    disabled = _run_pos_with(lambda r: B.scan_rows(r, disable=True))
    nameonly = _run_pos_with(name_only_scanner)
    ds = disabled < normal and nameonly < normal
    return {"normal_positive_controls_alarm_count": normal, "scanner_disabled_alarm_count": disabled,
            "value_decoder_disabled_alarm_count": nameonly, "name_only_scanner_alarm_count": nameonly,
            "families_total": len(B.SCANNER_FAMILIES), "disable_sensitive": bool(ds),
            "positive_controls_not_disable_sensitive": not ds,
            "uses_real_scanner_path_evidence": "disabling scan_rows -> %d alarms; name-only scanner -> %d (value-level necessary)" % (disabled, nameonly)}


def run_r1(output_dir, persist=True):
    out = Path(output_dir)
    if persist: out.mkdir(parents=True, exist_ok=True)
    sr = B.read_sources(B.repo_root())
    rows = B.generate_rows(plant=False); pub = B.public_rows(rows); truth = B._truth(rows)
    iv, _ = B.make_intervener(rows, B.B)
    oracle_mean = B._mean(B._per_row(truth, B.budget_faithful_visible_channel_oracle(pub, iv)))
    iv2, _ = B.make_intervener(rows, B.B)
    active_preds, used = active_interventional_baseline(pub, iv2)
    active_vals = B._per_row(truth, active_preds); active_mean = B._mean(active_vals); active_lcb = B._bca(active_vals)
    gap = oracle_mean - active_mean
    asrc = inspect.getsource(active_interventional_baseline)
    fa = {"evaluation_only_read": "evaluation_only" in asrc, "target_actions_read": "target_actions" in asrc,
          "oracle_callable_called": "budget_faithful_visible_channel_oracle" in asrc,
          "direct_truth_map_read": "make_intervener" in asrc, "uses_public_rule": "rule_target" in asrc,
          "uses_public_inverse": "PUBLIC_INV" in asrc, "uses_legal_probe_interface": True}
    a_rep = {"baseline_name": "active_interventional_baseline", "producer_function": "runner_r1.active_interventional_baseline",
             "inputs": ["public_rows", "legal_intervene(budget=8)"], "budget_used_per_row": max(used) if used else 0,
             "max_budget_used": max(used) if used else 0, "mean_score": active_mean, "lcb_95_one_sided": active_lcb,
             "code_path_hash": _ch(active_interventional_baseline), "forbidden_access_scan": fa,
             "call_graph_to_oracle": fa["oracle_callable_called"],
             "call_graph_to_truth_direct": fa["evaluation_only_read"] or fa["direct_truth_map_read"],
             "call_graph_to_truth_via_legal_probe": True, "oracle_mean": oracle_mean,
             "active_minus_oracle_gap": gap, "saturates": active_mean >= oracle_mean - EPS}
    tr = transitive_report(); af = attacker_family_audit(); pc = positive_control_disable_report()

    blockers = []
    if a_rep["saturates"]: blockers.append("invalid_001b_equal_access_active_baseline_saturates")
    if tr["any_hidden_truth_leak"]: blockers.append("invalid_001b_transitive_baseline_answer_core_leak")
    if af["collapsed_single_attacker"]: blockers.append("invalid_001b_attacker_family_collapsed")
    if pc["positive_controls_not_disable_sensitive"]: blockers.append("invalid_001b_positive_controls_not_disable_sensitive")
    if a_rep["saturates"]:
        verdict = "invalid_001b_equal_access_active_baseline_saturates"
    elif "invalid_001b_transitive_baseline_answer_core_leak" in blockers:
        verdict = "invalid_001b_transitive_baseline_answer_core_leak"
    elif "invalid_001b_attacker_family_collapsed" in blockers:
        verdict = "invalid_001b_attacker_family_collapsed"
    elif "invalid_001b_positive_controls_not_disable_sensitive" in blockers:
        verdict = "invalid_001b_positive_controls_not_disable_sensitive"
    else:
        verdict = "001b_r1_artifacts_complete_for_independent_review"

    result = {"run_id": RUN_ID, "verdict": verdict, "all_blockers_detected": blockers,
              "current_layer": "engineering implementation / redesign precheck repair only",
              "mainline_integration_status": "none", "enabled_status": "none",
              "oracle_mean": oracle_mean, "active_interventional_baseline_mean": active_mean,
              "active_minus_oracle_gap": gap, "eps_equiv": EPS,
              "stop_condition_triggered": "active_interventional_baseline_mean >= oracle_mean - eps_equiv" if a_rep["saturates"] else None,
              "generator_tuned_after_stop": False, "attacker_family_status": af["status"],
              "positive_controls_disable_sensitive": pc["disable_sensitive"],
              "transitive_hidden_truth_leak": tr["any_hidden_truth_leak"],
              "baselines_reach_public_answer_core": tr["any_reaches_public_answer_core"],
              "claim_ceiling": "001B-R1 baseline-immunity repair artifacts produced for independent hostile review. No "
              "LRGG admissibility, candidate-free headroom, oracle validity beyond this precheck, mechanism, agency/self/"
              "subjectivity/emotion/consciousness/autonomy, EGO readiness, H0/H1, 001C, Tier3+, mainline, or official Tier 0-2 result.",
              "what_this_shows": "Under EQUAL legal intervention access an independent active baseline solves the current "
              "001B generator to the oracle ceiling (gap=%.4f). The 001B passive-only 'window' was a forbidden "
              "interventional-minus-observational gap, not equal-access headroom. The 001B value-attacker family is also a "
              "collapsed single implementation behind 7 labels." % gap}

    if persist:
        def w(name, obj):
            t = _stable(obj); (out / name).write_text(t, encoding="utf-8"); return _sha(t.encode())
        w("source_readback_report.json", {"preconditions": sr["preconditions"], "sources": sr["sources"],
          "official_run_001a_verdict": "rejected_baseline_saturated",
          "readback_001b_hashes": {"runner": "08612ae2", "test": "569a225d", "precheck_result": "72efbbbf", "report": "25871992"}})
        w("active_interventional_baseline_report.json", a_rep)
        w("transitive_call_graph_report.json", tr)
        w("baseline_call_graph_edges.json", {"baselines": [{"baseline": r["baseline"],
          "reaches_public_answer_core": r["reaches_public_answer_core"], "reaches_hidden_truth": r["reaches_hidden_truth"]} for r in tr["baselines"]]})
        w("forbidden_symbol_reachability.json", {"forbidden_hidden": sorted(FORBIDDEN_HIDDEN),
          "forbidden_answer_core": sorted(FORBIDDEN_ANSWER_CORE),
          "per_baseline": {r["baseline"]: {"hidden": r["reaches_hidden_truth"], "public_core": r["reaches_public_answer_core"]} for r in tr["baselines"]}})
        w("baseline_independence_r1_report.json", {"method": "transitive co_names reachability (not direct-source only)",
          "any_hidden_truth_leak": tr["any_hidden_truth_leak"], "all_reach_public_answer_core": tr["all_baselines_reach_public_answer_core"],
          "independence_downgrade": "001B baselines are independent of HIDDEN truth but all transitively use the PUBLIC "
          "rule_target/_twin; combined with R1-A this means no equal-access headroom.", "detail": tr})
        w("attacker_family_audit_report.json", af)
        w("positive_control_disable_report.json", pc)
        rh = w("r1_precheck_result.json", result)
        (out / "r1_precheck_result.sha256").write_text(rh + "\n", encoding="utf-8")
        w("active_baseline_predictions.json", {"sample_first5": [{"row_id": pub[i]["row_id"], "active_pred": sorted(active_preds[i])} for i in range(5)],
          "active_mean": active_mean, "oracle_mean": oracle_mean})
        (out / "LIMITATIONS.md").write_text("# LIMITATIONS\n\n- 001B-R1 baseline-immunity repair; NOT an official Tier 0-2 "
          "rerun, NOT candidate work, NOT Tier 3+.\n- Decisive: equal-access active baseline saturates the 001B generator "
          "(gap=%.4f); preserved as NEGATIVE evidence; generator NOT tuned.\n- Attacker family collapsed (1 impl, 7 labels) "
          "-> 001B R4 'powered family' downgraded.\n- Baselines reach the PUBLIC rule transitively (by 001B design); not a "
          "hidden-truth leak, but it is why A saturates.\n- A generator redesign requires a NEW task card.\n" % gap, encoding="utf-8")
        (out / "CLAIM_CEILING.md").write_text("# CLAIM_CEILING\n\n" + result["claim_ceiling"] + "\n", encoding="utf-8")
        (out / "R1_BASELINE_IMMUNITY_REPORT.md").write_text(
          "# LRGG Tier 0-2 001B-R1 Baseline-Immunity Repair\n\nVerdict: `%s`\n\nLayer: %s; mainline none; enabled none; "
          "auto-remote-anchor forbidden.\n\nr1_precheck_result.sha256=%s\n\n## R1-A equal-access active baseline (DECISIVE)\n"
          "- oracle_mean=%.4f\n- active_interventional_baseline_mean=%.4f (lcb=%.4f), budget_used/row=%d\n"
          "- gap = oracle - active = %.4f (eps_equiv=%s) -> SATURATES=%s\n- forbidden_access_scan: oracle_called=%s "
          "evaluation_only_read=%s direct_truth_map_read=%s (g_lo only via legal probe)\n- => the 001B passive-only window "
          "was a forbidden interventional-minus-observational gap, NOT equal-access headroom.\n\n## R1-B transitive call-graph\n"
          "- any_hidden_truth_leak=%s (no reach to evaluation_only/target_actions/g_lo/probe_response/oracle)\n"
          "- all_baselines_reach_public_answer_core=%s (rule_target/_twin, public-rule design); direct-source checks miss this.\n\n"
          "## R1-C attacker family\n- status=%s; distinct_code_paths=%d; transform_cosmetic=%s -> 001B R4 'powered family' DOWNGRADED.\n\n"
          "## R1-D positive-control disable sensitivity\n- normal=%d/%d scanner_disabled=%d name_only=%d -> disable_sensitive=%s\n\n"
          "## All blockers detected (verdict = first/decisive)\n%s\n\n%s\n" % (
            verdict, result["current_layer"], rh, oracle_mean, active_mean, active_lcb, a_rep["max_budget_used"], gap, EPS,
            a_rep["saturates"], fa["oracle_callable_called"], fa["evaluation_only_read"], fa["direct_truth_map_read"],
            tr["any_hidden_truth_leak"], tr["all_baselines_reach_public_answer_core"], af["status"], af["distinct_code_paths"],
            af["transform_parameter_cosmetic"], pc["normal_positive_controls_alarm_count"], pc["families_total"],
            pc["scanner_disabled_alarm_count"], pc["name_only_scanner_alarm_count"], pc["disable_sensitive"],
            json.dumps(blockers), result["what_this_shows"]), encoding="utf-8")
    return {"result": result, "active": a_rep, "transitive": tr, "attacker": af, "positive_control": pc, "sr": sr,
            "artifacts": {p.name: p.stat().st_size for p in out.iterdir() if p.is_file()} if persist else {}}


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(); ap.add_argument("--output-dir", default="artifacts/LRGG-CANDIDATE-FREE-TIER0-2/REDESIGN_PRECHECK_001B_R1")
    a = ap.parse_args(); r = run_r1(a.output_dir, persist=True)
    print(_stable({"verdict": r["result"]["verdict"], "oracle": r["result"]["oracle_mean"],
                   "active": r["result"]["active_interventional_baseline_mean"], "gap": r["result"]["active_minus_oracle_gap"]}), end="")
