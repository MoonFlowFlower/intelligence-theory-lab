# LRGG Tier 0-2 001B-R1 Baseline-Immunity Repair

Verdict: `invalid_001b_equal_access_active_baseline_saturates`

Layer: engineering implementation / redesign precheck repair only; mainline none; enabled none; auto-remote-anchor forbidden.

r1_precheck_result.sha256=c7ea2f945036730b082ef1eab1cd8c955fd01ebe500be6d21075ba2d1a2f7889

## R1-A equal-access active baseline (DECISIVE)
- oracle_mean=1.0000
- active_interventional_baseline_mean=1.0000 (lcb=1.0000), budget_used/row=1
- gap = oracle - active = 0.0000 (eps_equiv=0.05) -> SATURATES=True
- forbidden_access_scan: oracle_called=False evaluation_only_read=False direct_truth_map_read=False (g_lo only via legal probe)
- => the 001B passive-only window was a forbidden interventional-minus-observational gap, NOT equal-access headroom.

## R1-B transitive call-graph
- any_hidden_truth_leak=False (no reach to evaluation_only/target_actions/g_lo/probe_response/oracle)
- all_baselines_reach_public_answer_core=False (rule_target/_twin, public-rule design); direct-source checks miss this.

## R1-C attacker family
- status=collapsed_single_attacker_multiple_labels; distinct_code_paths=1; transform_cosmetic=True -> 001B R4 'powered family' DOWNGRADED.

## R1-D positive-control disable sensitivity
- normal=10/10 scanner_disabled=0 name_only=2 -> disable_sensitive=True

## All blockers detected (verdict = first/decisive)
["invalid_001b_equal_access_active_baseline_saturates", "invalid_001b_attacker_family_collapsed"]

Under EQUAL legal intervention access an independent active baseline solves the current 001B generator to the oracle ceiling (gap=0.0000). The 001B passive-only 'window' was a forbidden interventional-minus-observational gap, not equal-access headroom. The 001B value-attacker family is also a collapsed single implementation behind 7 labels.
