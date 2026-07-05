"""TLGP-001B-INVALID-AUDIT-001 -- NON-EVIDENTIAL read-only diagnostic (no torch, no training)."""
import json, sys
sys.path.insert(0, ".")
import numpy as np
from src.tlgp_001b import splits as S

REAL, CONTROL = S.REAL, S.CONTROL
N = 300

def vals(eps, which):
    s = set()
    for ep in eps:
        s.update(int(v) for v in np.asarray(getattr(ep, which)).ravel())
    return sorted(s)

def rule_ids(eps):
    return sorted({int(ep.rule_id) for ep in eps})

def episodes_identical(a, b):
    if len(a) != len(b):
        return False, "len differs"
    for ea, eb in zip(a, b):
        for f in ("rule_id","adapt_x","adapt_a","adapt_e","query_x","query_a","query_e"):
            if not np.array_equal(np.asarray(getattr(ea,f)), np.asarray(getattr(eb,f))):
                return False, f"field {f} differs at ep {ea.episode_id}"
    return True, "identical"

out = {"NON_EVIDENTIAL": True, "task": "TLGP-001B-INVALID-AUDIT-001", "emits_no_verdict": True}

test_real = S.make_split("test", REAL, N)
test_ctrl = S.make_split("test", CONTROL, N)
ident, why = episodes_identical(test_real, test_ctrl)
out["check1_test_identical_real_vs_control"] = {"identical": ident, "detail": why, "n_episodes": N}

real_tr = S.make_split("train", REAL, N)
ctrl_tr = S.make_split("train", CONTROL, N)
out["check2_value_regimes"] = {
    "REAL_train_adapt_values": vals(real_tr,"adapt_x"),
    "REAL_train_query_values": vals(real_tr,"query_x"),
    "CONTROL_train_adapt_values": vals(ctrl_tr,"adapt_x"),
    "CONTROL_train_query_values": vals(ctrl_tr,"query_x"),
    "test_adapt_values": vals(test_real,"adapt_x"),
    "test_query_values": vals(test_real,"query_x"),
    "control_adds_34_to_train_queries": set([3,4]).issubset(set(vals(ctrl_tr,"query_x"))),
    "real_train_queries_exclude_34": set([3,4]).isdisjoint(set(vals(real_tr,"query_x"))),
    "control_adapt_still_excludes_34": set([3,4]).isdisjoint(set(vals(ctrl_tr,"adapt_x"))),
}

train_idx, test_idx = S.rule_split()
test_rids = set(rule_ids(test_real))
train_rids = set(rule_ids(real_tr)) | set(rule_ids(ctrl_tr))
out["check3_unseen_rule_generalization"] = {
    "test_rules_subset_of_TEST_RULES": test_rids.issubset(set(int(i) for i in test_idx)),
    "test_train_rule_overlap_empty": test_rids.isdisjoint(train_rids),
    "n_train_rules": int(len(train_idx)), "n_test_rules": int(len(test_idx)),
    "n_distinct_test_rules_sampled": len(test_rids),
}

with open("artifacts/TLGP-001B/result.json") as f:
    res = json.load(f)
DELTA = float(res["DELTA"])
recomputed = {}
for fam, rows in res["headroom_vs_meta_per_seed"].items():
    closed = sum(1 for r in rows if float(r["control_headroom_vs_meta"]) <= DELTA)
    recomputed[fam] = {"closed_seeds_recomputed": closed,
                       "official": res["capacity_control_closed_seeds"][fam],
                       "min_control_headroom": round(min(float(r["control_headroom_vs_meta"]) for r in rows),4),
                       "max_control_headroom": round(max(float(r["control_headroom_vs_meta"]) for r in rows),4)}
out["check4_closed_seed_recompute"] = {"DELTA": DELTA, "need_close": 9, "per_family": recomputed,
    "match_official": all(recomputed[f]["closed_seeds_recomputed"]==recomputed[f]["official"] for f in recomputed)}

print(json.dumps(out, indent=2, sort_keys=True))
