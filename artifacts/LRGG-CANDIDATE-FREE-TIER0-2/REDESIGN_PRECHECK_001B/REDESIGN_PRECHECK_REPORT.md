# LRGG Tier 0-2 REDESIGN PRECHECK 001B

Verdict: `redesign_precheck_ready_for_independent_reaudit`

Layer: engineering implementation / redesign precheck only; mainline: none; enabled: none; auto-remote-anchor: forbidden.

generator_spec_001b.sha256=401096edaa86428cff19692ba6c2fa94c15b963af73ea33e7519341561d5fe04
precheck_result.sha256=72efbbbf02ee5cd40914b8487043eec267621951d13b4b98018ae48f899ae1b4

## Window
- oracle C=1.0000 (>= 0.9)
- nonreading=0.0846; C-nonreading=0.9154 (>= 0.3)
- random=0.0833 majority=0.0967; C-max=0.9033 (>= 0.1)
- passive raw/value decoder family_max=0.6845 (< C-0.05=0.9500)
- strongest cheap baseline fsm_planner=0.6845
- planted-latent attacker family_max=1.0000

## R1-R5
R1 latent_hidden=True R3 oracle_decoupled=True R2 baselines_independent=True (distinct_pred=10, src_clean=True) R4 attackers_powered=True R5 positive_controls_real=True window_ok=True

## Twin pair
{"g0": 0, "g1": 1, "r": 3, "c": 5, "passive_identical": true, "targets_differ": true, "probe_index": 64, "probe_response_g0": 0, "probe_response_g1": 1}
passive_indistinguishable=True intervention_separable=True

## Leakage(real path)
findings=[]

Does not prove headroom/admissibility/mechanism, nor that an ACTIVE interventional baseline (absent from the required panel) would not solve; only that this harness hides the latent, decouples oracle/baselines, powers attackers/scanners, and shows a non-empty decodability-solvability window.
