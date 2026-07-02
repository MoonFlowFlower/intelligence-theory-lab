"""Schema/content validator for frozen_design.json (S0 gate, FSP-PUM-ENV-IDPROBE-001A).

Stdlib-only. Run:  python tests/fsp_pum_env/test_frozen_design.py
Exit 0 = valid; exit 1 = violations printed. Usable both as a script and under pytest.

Checks: zero TBD/TODO/placeholder/null fields anywhere; threshold literals exactly
match the card's H1 values; required keys present; structural constraints hold.
"""
import json
import sys
from pathlib import Path

FROZEN = Path(__file__).resolve().parents[2] / "artifacts" / "FSP-PUM-ENV-IDPROBE-001A" / "frozen_design.json"

# Card H1 literals — changing these here is a governance violation, not a fix.
CARD_THRESHOLDS = {
    "ideal_observer_macro_accuracy_min": 0.80,
    "fair_battery_family_max_macro_accuracy_max": 0.60,
    "headroom_mean_min": 0.15,
    "headroom_bootstrap_95_LCB_min": 0.10,
    "action_conditioning_gap_min": 0.10,
    "saturation_sentinel_any_battery_member_max": 0.95,
    "obs_decoder_camouflage_on_max": 0.60,
    "obs_decoder_camouflage_off_min": 0.80,
}

REQUIRED_TOP_KEYS = [
    "task_id", "governing_sources", "terminal_vocabulary_ref", "env_parameters",
    "population_and_data", "evaluation", "thresholds", "statistics",
    "mi_structural_check", "obs_decoder_gate", "probe_scheduling",
    "gap3_truncation", "evaluation_regimes_per_gap", "rng_scheme",
    "cost_metering_fields", "battery_membership", "positive_controls",
]

BANNED_SUBSTRINGS = ("TBD", "TODO", "FIXME", "PLACEHOLDER", "<fill", "???")


def walk(node, path="$"):
    if isinstance(node, dict):
        for k, v in node.items():
            yield from walk(v, f"{path}.{k}")
    elif isinstance(node, list):
        for i, v in enumerate(node):
            yield from walk(v, f"{path}[{i}]")
    else:
        yield path, node


def validate(doc):
    errors = []

    for key in REQUIRED_TOP_KEYS:
        if key not in doc:
            errors.append(f"missing required top-level key: {key}")

    for path, leaf in walk(doc):
        if leaf is None:
            errors.append(f"null value at {path}")
        if isinstance(leaf, str):
            up = leaf.upper()
            for banned in BANNED_SUBSTRINGS:
                if banned.upper() in up:
                    errors.append(f"banned placeholder '{banned}' at {path}: {leaf[:60]!r}")

    thr = doc.get("thresholds", {})
    for k, expected in CARD_THRESHOLDS.items():
        got = thr.get(k)
        if got != expected:
            errors.append(f"threshold {k}: expected card literal {expected}, got {got}")

    env = doc.get("env_parameters", {})
    if env.get("K_topics") != 8:
        errors.append("K_topics must be 8 (card)")
    pairs = env.get("preregistered_interaction_pairs", [])
    if len(pairs) < 2:
        errors.append("need >=2 preregistered interaction pairs (card)")
    tp = env.get("theta_probe_subset", {}).get("dims", [])
    if len(tp) < 3 or "sensitivity_flag_0" not in tp or "sensitivity_flag_1" not in tp:
        errors.append("theta_probe must have >=3 dims incl. both sensitivity flags (card)")
    ts = env.get("theta_structure", {})
    if ts.get("sensitivity_flags", {}).get("count") != 2:
        errors.append("sensitivity flag count must be 2 (card)")
    if len(ts.get("topic_preference_dims", {}).get("grid_levels", [])) != 4:
        errors.append("topic dims must be on a 4-level grid (execution plan D1)")
    ep = env.get("episodes", {})
    if ep.get("N_sessions_per_user") != 20 or ep.get("T_turns_per_session") != 15:
        errors.append("sessions must be 20 x 15 (card)")

    pop = doc.get("population_and_data", {})
    if pop.get("N_heldout_users") != 200:
        errors.append("N_heldout_users must be 200 (card)")
    seeds = pop.get("env_master_seeds", [])
    if len(seeds) != 10 or len(set(seeds)) != 10:
        errors.append("need exactly 10 distinct env master seeds (card)")

    regimes = doc.get("evaluation_regimes_per_gap", {})
    if regimes.get("gap1") != "LOG-PARITY" or regimes.get("gap3") != "LOG-PARITY":
        errors.append("gap1/gap3 must be LOG-PARITY (card R1 / constitution section 2)")
    for g in ("gap2a", "gap2b"):
        if not str(regimes.get(g, "")).startswith("ON-POLICY"):
            errors.append(f"{g} must be ON-POLICY (card R1 / constitution section 2)")

    mi = doc.get("mi_structural_check", {})
    if not isinstance(mi.get("delta_bits"), (int, float)):
        errors.append("mi_structural_check.delta_bits must be a declared number")
    if len(mi.get("feature_families", [])) < 3:
        errors.append("MI feature families must include the three declared families (execution plan T0.2)")

    dec = doc.get("obs_decoder_gate", {})
    if len(dec.get("architectures", [])) < 3:
        errors.append("decoder family needs >=3 architectures (card / constitution section 6.2)")

    g3 = doc.get("gap3_truncation", {})
    if not isinstance(g3.get("B"), int) or "unit" not in g3:
        errors.append("gap3 truncation must declare integer B and its unit (constitution section 4)")

    bat = doc.get("battery_membership", {})
    if bat.get("append_only") is not True:
        errors.append("battery_membership.append_only must be true")
    members = bat.get("members", [])
    for required_member in ("predict_all", "predict_none", "successor_map", "transition_table",
                            "count_table", "fsm_planner", "episodic_traversal"):
        if required_member not in members:
            errors.append(f"mandatory battery member missing: {required_member}")

    pcs = doc.get("positive_controls", {})
    for pc in ("PC_IDEAL_SANITY", "PC_LEAK_PLANT", "PC_DECODER", "NULL_env_control"):
        if pc not in pcs:
            errors.append(f"missing positive control: {pc}")

    return errors


def main():
    if not FROZEN.exists():
        print(f"FAIL: {FROZEN} not found")
        return 1
    doc = json.loads(FROZEN.read_text(encoding="utf-8-sig"))
    errors = validate(doc)
    if errors:
        print(f"FAIL: {len(errors)} violation(s):")
        for e in errors:
            print(f"  - {e}")
        return 1
    print("PASS: frozen_design.json schema-valid, zero TBD, thresholds match card literals.")
    return 0


def test_frozen_design_valid():
    doc = json.loads(FROZEN.read_text(encoding="utf-8-sig"))
    assert validate(doc) == []


if __name__ == "__main__":
    sys.exit(main())
