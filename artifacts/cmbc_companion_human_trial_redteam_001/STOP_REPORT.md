# Human Trial Redteam 001 Stop Report

stop_verdict = contradictory_feedback_overfit

claim_after_redteam = scripted lab harness evidence only

The run is recorded as a clean downgrade. The selector was not patched, thresholds were not changed, baselines were not weakened, and EGO migration / real companion implementation remain no-go.

Primary failure evidence:

- pre_contradiction_selected_action = act_2
- post_contradiction_selected_action = act_4
- probability_shift_abs = 0.21428770500442973
- distribution_kl = 0.09397546452829571
