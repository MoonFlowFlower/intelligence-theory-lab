# ACPC-PREDICTION-CORRECTION-LOOP-ROUTE-DECISION-001A

Route-decision + hostile pre-mortem for the "action-conditioned prediction-correction
loop" as a candidate functional-subject mechanism. **Design only. Not an
implementation authorization. No code, tests, or artifacts are produced by this card.**

```yaml
card_type: route_decision_design_only
implementation_authorized: false
layer: mechanism-hypothesis / route-governance (design)
mainline_integration: none
enabled_status: none
claim_ceiling: route-decision design record only; no computed evidence
role: same-agent auditor / red-team (CLAUDE.md Role 001) — not third-party independent
```

## Verdict (headline)

`route_close_generic_acpc_loop__saturated_by_prior_evidence__only_engineering_layer_endogenous_data_residual_remains`

The **generic** action-conditioned prediction-correction loop (predict next
observation given action → measure error → update belief) is a **closed route**
for *functional-subject mechanism* evidence. It is already proven, in this repo,
to collapse to a fair recursive/batch estimator (ACOLB) and to pass only as an
attestation protocol without predictive superiority (predictive_action_learning
contract). Do **not** spend GPU/implementation on the generic loop.

The only residual with plausible non-saturation is a narrow **endogenous-data /
dual-control** regime, and even there the honest claim ceiling is *engineering-
layer* ("learned adaptive controller vs classical adaptive/dual control"), **not**
subject/agency. Recommendation: do not open it as a subject route; keep focus on
the line that actually shows headroom (TLGP rung3).

## Why this card exists

The user's target is a "prediction-correction model" as a subject component, with
the rung3 transformer viewed as only its learner. This card asks the bounded
question: *is there any version of the action-conditioned prediction-correction
loop that yields mechanism evidence beyond the strongest fair estimator/controller
under budget parity?* Per the lab contract, a successor route must cite prior
negative evidence before proposing a new gate. That prior evidence closes the
generic form.

## Inherited state readback (grounded in artifacts, not self-report)

Read this session from repo:

ACOLB-A (`artifacts/acolb_001a/`, and
`docs/research/CLAUDE-INDEPENDENT-ACOLB-A-ROUTE-DECISION-AND-ROUTE-C-DESIGN-AUDIT-001A.md`):

- verdict `saturated_close`; `mechanism_claim_admitted: false`; stop
  `blocked_by_saturated_distribution`.
- Candidate = online recursive Bayesian/Kalman update with forgetting factor,
  action-conditioned prediction-error correction. Fair baseline = batch weighted
  least-squares with decay weighting over the same probe sequence.
- **Decisive:** on a fixed linear-Gaussian episode these are *algebraically the
  same discounted-least-squares estimator*. Candidate OOD 0.9445 vs fair amortized
  0.9299, margin 0.0147 < band 0.05; equivalence holds across the entire decay
  grid (margin shrinks to 0.0008 at decay 1.0). "The candidate's marginal value
  over precomputation is null."
- The candidate *does* beat the whole graph-cache/lookup/memory family (all ≤
  0.73 vs 0.93) — so it is not a disguised lookup; its *only* equivalent is the
  fair amortized estimator.

predictive_action_learning_contract_001/001c
(`docs/audits/PREDICTIVE_ACTION_LEARNING_CONTRACT_001C_INDEPENDENT_AUDIT.md`):

- Full action-conditioned belief/model update (gates E6-E13): per-step
  `belief_pre` / `raw_pred_obs_by_action` → `actual_obs` / `nll_error` /
  `belief_post`, committed pre-reveal into an append-only hash chain anchored by
  257 real RFC-3161 TSA tokens; core runs replayable at max_abs_diff 0.0.
- Verdict `bounded_contract_pass`; independent audit `pass_with_caveats`.
- **Decisive:** it does **not** support predictive superiority over retrieval —
  raw traces show retrieval matched action-sensitive NLL (gap 0.0042) and
  *outperformed* the learner post-shift by 0.1119 nats. It is distinguishable from
  retrieval only via a pre-declared composite rule, and explicitly supports "no
  agency / functional-subject / consciousness" claim.

Net: the loop has been built to a very high evidentiary standard (commit-before-
reveal, cryptographic timestamping, full replay) and still produced **no
mechanism headroom** over fair estimators/retrieval.

## Bounded formal object (the generic loop under test)

- State `S`: latent parameters θ of an environment transition/observation model
  (possibly non-stationary).
- Observation `O`: `o_t` = possibly-noisy/aliased function of state + last action.
- Action `A`: `a_t` (in the passive-estimation form, actions are a given probe
  sequence; in the active form, agent-chosen).
- Memory/latent `M`: belief `b_t` over θ (mean + covariance, or a learned latent).
- Update `U`: `b_t = f(b_{t-1}, a_{t-1}, o_t, predicted_o)` — prediction-error
  driven belief update.
- Objective `J`: predictive NLL of held-out action-conditioned outcomes (and/or
  control regret).

## K1 / K2 pre-mortem (killer-catalog contract — must answer or STOP)

**K1 (observation-decodability).** *Answerable.* Make θ non-decodable from any
single `o_t` (aliasing: one observation consistent with multiple θ; only the
action-outcome sequence disambiguates). Positive control: an obs-only decoder
must fail ≤ majority+ε. This is achievable and is NOT where the route dies.

**K2 (fair-baseline saturation).** *ALREADY REALIZED — this is the killer.* For a
fixed-structure estimation problem, the online recursive prediction-error update
is the sufficient-statistic-optimal estimator, and a batch/amortized fit with the
same forgetting recovers the same estimate (ACOLB 1.a, proven algebraically and
across the whole decay grid). The "loop" buys nothing a fair recursive filter
(Kalman/RLS/particle) or its batch amortization lacks. Under budget parity the
fair baseline *is* a prediction-correction loop done optimally. **The generic loop
fails K2 at design.** No new experiment is needed to learn this; ACOLB already ran
it.

Contract consequence: *the generic route answers K1 but fails K2 → STOP (close).*

## The one non-saturable residual (and its honest ceiling)

The amortization collapse assumes a **fixed latent estimated from a fixed (or
freely re-runnable) data stream**. It breaks only when the data is **endogenous
and non-amortizable**:

- The agent's actions **change** the environment (control, not passive
  estimation), and/or actions are **irreversible**, so counterfactual data that a
  batch fit would need does not exist; and
- probing and controlling are **coupled** (dual control), whose optimum is
  Bellman-intractable, so classical *certainty-equivalence* control is provably
  suboptimal.

In that regime a learned closed-loop policy might approximate the intractable
dual-control optimum better than the best tractable classical baseline. That is a
**real** gap — but:

- Fair baselines (budget/parity): certainty-equivalence adaptive control, the best
  tractable dual-control approximation, model-predictive control with online
  system-ID, and (Codex parity rule) any baseline that is *also* allowed to act.
- **Claim ceiling of the residual: engineering/ML only** — "a learned adaptive
  controller beats classical adaptive/dual control on an intractable-optimum
  task." This is NOT functional-subject evidence. "Maintain a belief and act on
  it" is the definition of a controller, and controllers are the fair baseline;
  subject-ness is not located in the loop.
- Saturation risk still high (many intractable-control tasks are matched by MPC +
  online SysID in practice).

Go/no-go for the residual: it is worth a *design* probe **only** if the user
explicitly wants engineering-layer control evidence, with the claim ceiling fixed
at "learned vs classical adaptive control." For the lab's stated functional-subject
purpose, its ROI is low.

## Relationship to TLGP rung3 (why rung3 has headroom and the loop does not)

rung3 tests **representation/inference** (infer an *unseen* latent rule from
in-context examples), where `ideal ≫ fair_max` (identifiability headroom is real
and was verified). The loop tests **recursive estimation of a (largely fixed-
structure) latent**, where the fair estimator is optimal and there is no headroom.
Different questions; only the former currently has separation from fair baselines.

## Recommendation

1. **Close the generic action-conditioned prediction-correction loop route** as a
   functional-subject mechanism route. It is saturated by ACOLB and non-superior
   per the predictive_action_learning contract. Do not implement.
2. Do **not** open the endogenous-data/dual-control residual as a *subject* route.
   If ever pursued, it is an engineering-layer probe with a fixed non-subject claim
   ceiling and high saturation risk — low priority.
3. Keep focus on TLGP rung3 (the only line with verified headroom). The honest,
   durable lesson across the loop family: online belief update, as a mechanism,
   collapses to fair recursive/batch estimation — the wall here is K2 (fair-
   baseline saturation), just as the self-boundary family's wall is K1
   (observation-decodability). Both are the identifiability ceiling in different
   dress.

## Stop condition / rollback

- Stop: this is a design record; it authorizes no execution. If any successor
  tries to implement the generic loop, block by citing ACOLB `saturated_close`
  and this route decision.
- Rollback: none needed (no code). If this card is later cited to authorize an
  implementation, that citation is invalid unless a separate task card re-opens the
  route on a *materially different, non-amortizable* surface with a pre-registered
  kill-baseline.

## Non-actions in this card

- Code / tests / artifacts created: false
- Implementation authorized: false
- Mechanism evidence claimed: false
- Old artifacts modified: false
- Git commit/push: false

## What this does not prove

Does not prove ACPC loop validity or invalidity as a general matter, mechanism
validity, agency, autonomy, self, value, consciousness, subjectivity, or EGO
readiness. It is a bounded route-decision that the *generic* loop is closed by
prior in-repo negative evidence and that only an engineering-layer residual
remains.
