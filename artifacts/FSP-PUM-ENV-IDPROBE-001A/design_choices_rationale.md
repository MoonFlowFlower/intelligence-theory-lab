# frozen_design.json — one-line rationales for choosable parameters (S0, 2026-07-02)

Fixed-by-card values (K=8, thresholds, N_heldout=200, 10 seeds, 20x15 sessions, >=2 interaction pairs, 2 flags, theta_probe >=3 dims incl. both flags, terminal states) are copied verbatim and get no rationale here. Choosable values below were selected at freeze time and are frozen forever; changing any of them post-freeze requires a supersession card.

- Topic grid {-1.5,-0.5,0.5,1.5}: symmetric 4-level per D1; unit-ish spacing keeps interaction terms sign-informative at extremes.
- alpha {0.05,0.1,0.2} / beta {0.9,0.95,0.98} / d {0.3,0.5,0.7}: coarse 3-level grids for nuisance dims keep exact enumeration cheap (factored posterior per D1) while making trust dynamics genuinely user-dependent.
- Interaction pairs (topic_1,topic_2), (topic_5,topic_6), gamma=1.0: two disjoint pairs, multiplicative form — the minimal structure that defeats linear/discounted-LS (anti-ACOLB requirement) without inflating the joint grid.
- theta_probe = {flag_0, flag_1, topic_7}: card minimum (both flags) plus one preference dim so the probe channel carries both categorical and graded information.
- AR(1) rho (0.7/0.5/0.8), sigma 0.3, stationary init: mixed persistence so z matters within session but cannot masquerade as persistent theta; stationary init avoids session-start artifacts.
- Probes m=4, costs {0.08,0.08,0.12,0.15}: per-dim targeted probes plus one weak broad probe; two cost tiers make scheduling a real decision (Gap-2b needs a non-trivial cheap-active frontier).
- Trust update form + low-trust uniform mixing w=(d-trust)/d: simplest monotone self-limiting probe economy satisfying the card's "probing is self-limiting" requirement.
- Alphabet 32, 1 symbol/turn: keeps MI check exact and cheap; n-gram families remain meaningful across consecutive turns (session = 15-symbol string).
- N_train=800 disjoint from 200 heldout: 4:1 gives the decoder family enough data to be a capable attacker (anti-strawman, ROUTE-C lesson) at CPU cost.
- LOG-PARITY logging policy = 50% passive / 25% uniform / 25% fixed-0.2: predictor-class members must see probe outcomes (fairness) while the log stays non-adaptive.
- Query points: sessions {5,10,15,20} x turns {8,15}: early/mid/late coverage tests persistence without drift; 8 queries/user x 9 actions x 200 users = 14400 scored predictions per system.
- Counterfactual action subset (all 4 probes + 4 spread task actions + recommend): covers probe-dependent and passive-dependent responses without evaluating all 13 actions (compute discipline).
- Bootstrap 10k user-level, MDE 0.10 @ power 0.80: user is the exchangeable unit; MDE matches the LCB threshold so "inconclusive" has a preregistered meaning (discovery-loop MDE lesson).
- delta_MI = 0.02 bits: small nonzero floor for finite-sample noise on exact symbolic MI; the check is necessary-only per constitution 6.1.
- Decoder family (logreg / GBT / small GRU), 24 configs each: linear, tree, recurrent capacity spectrum under identical tuning budget; family_max is the reported adversary.
- Fixed-schedule grid 5 rates x 3 placements: dense-enough cheap-active cover so Gap-2b's "best fixed schedule" is a real competitor, not a token.
- UCB1 c=1.0 over probe arms + no-probe arm, reward = one-step IG proxy: the standard no-planning adaptive straw for Gap-2b's sufficient test.
- Gap-3 B=30 turns (2 sessions): 10% of the 300-turn stream — a real budget squeeze; declared unit avoids token-ambiguity.
- RNG: PCG64, 8 named streams, SHA256 seed derivation, per-draw event log: replay re-derives every draw; no stochasticity outside logged streams (constitution section 9).
- Master seeds 20260701..20260710: date-derived literals, no post-hoc seed selection possible.

Drafted by Claude (auditor) at operator request for an operator-executed S0; operator approval is expressed by including this file in the freeze commit. Disclosure: the S6 independent audit will treat frozen_design.json as auditor-co-authored and therefore apply extra scrutiny to whether the S1-S5 implementation silently diverges from it (the audit criterion is the sha-pinned file, not the auditor's memory of intent).
