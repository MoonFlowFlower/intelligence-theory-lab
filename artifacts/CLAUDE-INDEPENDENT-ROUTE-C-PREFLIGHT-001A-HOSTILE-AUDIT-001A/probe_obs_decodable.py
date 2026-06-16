"""Read-only hostile probe for ROUTE-C-PREFLIGHT-001A audit.

Demonstrates that the shipped non_identifiability_premise_gate is NOT fail-closed
against a value-level observation-decodable surface (threat F1).

It does NOT modify the implementation. Run from repo root:
    PYTHONPATH=src python3 artifacts/CLAUDE-INDEPENDENT-ROUTE-C-PREFLIGHT-001A-HOSTILE-AUDIT-001A/probe_obs_decodable.py

Observed result (commit 726f26d, LF source):
    trivial mean-attacker score on value-leaked passive data : 1.0000
    shipped obs_only_baseline score on same data            : 0.3854
    shipped premise-gate verdict                            : non_identifiability_present
    => gate ADMITTED (failed to block) a genuinely observation-decodable passive surface
"""
import sys
sys.path.insert(0, "src")
from route_c_preflight_001a import core

cfg = core.default_config()
bundle = core.build_episode_bundle(seeds=range(1600, 1632), config=cfg, run_id="probe")

# HOSTILE VARIANT: make hidden S trivially decodable from PASSIVE VALUES
# (the real F1 threat: S leaks into observation value structure, NOT a planted answer-key).
for ep in bundle["episodes"]:
    truth = set(ep["truth_self_handles"])
    for legal in (ep["legal"], ep["interventional_legal"]):
        for row in legal["passive_rows"]:
            for h in list(row["handle_values"]):
                if h in truth:
                    row["handle_values"][h] += 100.0  # blatant value-level leak of S


def mean_attacker(legal):
    """A legal observational attacker: reads only passive_rows values (allowed by blueprint §6.1)."""
    sums = {h: 0.0 for h in legal["handles"]}
    for row in legal["passive_rows"]:
        for h, v in row["handle_values"].items():
            sums[h] += v
    ranked = sorted(legal["handles"], key=lambda h: -sums[h])
    return sorted(ranked[: legal["query"]["k_self"]])


tot = 0.0
for ep in bundle["episodes"]:
    pred = mean_attacker(ep["legal"])
    tot += core.score_self_set_prediction(pred, ep["truth_self_handles"], k_self=cfg.k_self)
print("trivial mean-attacker score on value-leaked passive data : %.4f (1.0 = fully decodable)" % (tot / len(bundle["episodes"])))

panel = core.run_baseline_panel(bundle, run_id="probe-panel")
gate = core.non_identifiability_premise_gate(panel, config=cfg)
print("shipped obs_only_baseline score on same data            : %.4f" % panel["obs_only"]["aggregate_score"]["value"])
print("shipped premise-gate verdict                            :", gate["verdict"])
print()
print("VERDICT OF PROBE: gate %s a genuinely observation-decodable passive surface"
      % ("BLOCKED" if gate["verdict"].startswith("blocked") else "ADMITTED (failed to block)"))
