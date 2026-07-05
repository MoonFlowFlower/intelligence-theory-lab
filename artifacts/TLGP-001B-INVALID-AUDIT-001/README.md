# TLGP-001B-INVALID-AUDIT-001 — NON-EVIDENTIAL diagnostic

Read-only auditor diagnostic for the TLGP-001B INVALID (capacity-control) audit.
Emits NO H0/H1/INVALID verdict. Modifies NO official TLGP-001B artifact.
No torch, no training, no git. Deterministic from the frozen split code only.

- `diag.py` — regenerates splits from `src/tlgp_001b/splits.py` and checks:
  1. CONTROL test set == REAL test set (episode-for-episode identity).
  2. The ONLY train-side difference is CONTROL adding query values {3,4}; adapt stays {0,1,2}.
  3. test rules ⊂ TEST_RULES and disjoint from train rules (both regimes still require UNSEEN-RULE generalization).
  4. recomputes capacity_control_closed_seeds from official per-seed CONTROL headrooms.
- `capacity_control_design_diagnostic.json` — output.

Finding: the pre-registered CAPACITY_CONTROL relaxes only value-novelty {3,4} in training
queries; the test task (held-out values on 125 unseen rules) is byte-identical to REAL.
"Control closes" therefore requires ~the H1 success condition itself, so the control is not a
valid capability witness. Supports audit bucket B (positive_control_design_flaw_likely).
