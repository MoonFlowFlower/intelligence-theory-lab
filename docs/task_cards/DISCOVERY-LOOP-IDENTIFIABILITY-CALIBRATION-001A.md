# Task Card — DISCOVERY-LOOP-IDENTIFIABILITY-CALIBRATION-001A

**Status note:** self-authored AND self-executed by Claude in one session at the operator's
explicit instruction ("按你的想法做元实验,直接测 (a) vs (b)"). Per the lab's Same-Agent Bridge
Audit Role, this calibration's *conclusion* should receive an independent hostile audit before it
is used to reroute lab strategy. The card is frozen (pre-registered) before any result was seen.

## task id
DISCOVERY-LOOP-IDENT-CALIB-001A

## research layer
engineering_implementation + mechanism_hypothesis (tool calibration / diagnostic).
NOT subjectivity, NOT philosophical-consciousness.

## problem definition
The lab's discovery/falsification loop ("define problem → executable search → record each step →
preserve failures → extract low-complexity structure → large-scale verification → formal gate")
has produced a long streak of **baseline-equivalence / collapse** verdicts (graph_cache_collapse,
observation-only equivalence, predict_all=oracle saturation, co-binding non-identifiable, etc.).

Two competing readings of that streak:
- **(a)** the specific candidate mechanisms were simply wrong (the loop is a healthy falsifier);
- **(b)** the targets sit in **observationally non-identifiable** regimes, so the loop *cannot* award
  a latent mechanism a win even when one truly exists — i.e. the negative streak is partly an
  identifiability artifact, and the rational move is to map the negative space rather than hunt
  more candidates.

We cannot read (a) vs (b) off the real targets (we do not know their ground truth). This task runs
the loop in **synthetic worlds whose ground truth we fully control**, to test whether the loop is
calibrated: does it **separate** when a latent mechanism is genuinely identifiable, and **report
equivalence** when the latent structure is redundant? A calibrated loop makes "tool artifact" an
unlikely explanation of the real collapses and licenses a bounded inference toward (b) for the
**observational-collapse family only**.

## current stage
Phase-0 tool calibration (candidate-free). No real candidate mechanism is under test.

## hypothesis
H: The loop, scored only on causal one-step-ahead held-out predictive log-loss, will
(i) **separate** the latent mechanism from the strongest observation-only baseline in a
latent-*necessary* world, and (ii) report **baseline-equivalence** in a latent-*redundant* world,
while passing a guaranteed-separable positive control and a no-structure negative control.

If H holds → the loop is calibrated; lab observational-collapse verdicts are not a tool artifact;
reading (b) is the better-supported explanation for that family (bounded inference).
If positive control fails to separate → loop is underpowered/blind (no inference licensed).
If negative control falsely separates → leakage/overfit in the loop (must fix; no inference).

## system (bounded formal object)
- Observation space O = {0,1}.
- Latent/state space S: 2-state Markov for HMM worlds; for the redundant world S is a deterministic
  function of the last observation (redundant by construction).
- Mechanism-under-test M_T: an EM-fitted discrete-emission HMM (latent-state predictor),
  n_states selected by validation on a held-out slice of TRAIN (MDL: prefer fewer states on ties).
- Update U: Baum-Welch (EM); prediction by causal forward filtering.
- Objective J: minimize held-out one-step predictive log-loss (nats/symbol), scored on positions
  t ≥ max_order for ALL models (identical positions → fair).
- agent/non-agent boundary: the predictor sees ONLY past observations; never world identity, never
  true params, never future observations.

## baseline (strongest simpler alternative)
Observation-only **order-k count table** (Laplace-smoothed), k ∈ {0,1,2,3,4}; the per-seed
"strongest baseline" = the best held-out k. This is the lab's recurring collapse family
(observation-only / count_table / transition_table / successor_map / graph_lookup).
The loop "separates" only if the HMM beats the BEST order-k by the pre-registered band.

## ablation
- positive_control world (guaranteed-separable, stronger long-memory HMM): HMM **must** beat
  baseline → sensitivity check on the loop.
- negative_control world (i.i.d. Bernoulli(0.5), no structure): HMM **must not** beat baseline →
  specificity check (false-separation guard).
- leakage ablation (test-only): give the HMM scorer access to the future observation o_t when
  predicting o_t; this MUST flip the negative/redundant verdict to false-separation, proving the
  harness can detect leakage. The shipped run uses NO leak.

## trace / replay requirement
- trace.csv: one row per (regime, seed) with best_base_order, base_logloss, hmm_n_states,
  hmm_logloss, gap, separates.
- trace.jsonl: per held-out position t: base*_logloss_t and hmm_logloss_t (causal, past-only).
- replay: recompute per-seed gaps from trace.jsonl per-step losses, check they match trace.csv,
  then recompute the verdict from trace alone (no generator, no future info). replay verdict must
  equal the result verdict.

## acceptance gate (PRE-REGISTERED — frozen before run; not tuned after results)
Constants:
- alphabet M = 2; L_train = 3000; L_heldout = 2000; max_order K = 4; orders = {0,1,2,3,4}
- HMM n_states candidates = {2,3}; EM restarts = 3; EM iters = 40; EM tol = 1e-4
- baseline = strongest held-out order k (min over k; pro-baseline / conservative against separation)
- HMM n_states selected by BIC on full-train fits (MDL: penalize params, prefer fewer states;
  TRAIN-likelihood only, no held-out peek)
- seeds = 0..9 (10); consistency_min = 8
- separation band ε = 0.01 nats/symbol (frozen; not tuned after results)
- World params (fixed per world; data varies per seed):
  - latent_necessary: 2-state HMM, p_stay = 0.95, P(o=1|s=1)=0.80, P(o=1|s=0)=0.20
  - latent_redundant: order-1 obs Markov chain, P(1|0)=0.25, P(1|1)=0.75 (latent ≡ last obs)
  - positive_control: 2-state HMM, p_stay = 0.97, P(o=1|s=1)=0.75, P(o=1|s=0)=0.25
  - negative_control: i.i.d. Bernoulli(0.5)

Per-world verdict from gap = base_logloss − hmm_logloss (positive ⇒ HMM better):
- "separates"  if #seeds(gap ≥ ε) ≥ consistency_min
- "equivalent" if #seeds(|gap| < ε) ≥ consistency_min
- else "indeterminate"

META verdict (gates evaluated in order):
1. positive_control not "separates" → `check_underpowered_loop_blind`
2. negative_control "separates"     → `check_invalid_false_separation`
3. latent_necessary "separates" AND latent_redundant "equivalent" →
   `loop_calibrated__separates_identifiable_reports_equivalent_when_redundant`  (PASS)
4. latent_necessary "separates" AND latent_redundant not "equivalent" →
   `loop_separates_but_redundant_not_clean`
5. latent_necessary not "separates" → `loop_misses_identifiable_latent`
6. else → `indeterminate`

## claim ceiling
Bounded calibration of the discovery loop's **observational** identifiability discrimination on
four synthetic, ground-truth-known binary-sequence worlds. A PASS shows the loop separates an
identifiable latent mechanism and reports equivalence for a redundant one, label-blind and
future-blind. It supports — for the **observational-collapse family only** — the reading that the
lab's collapse verdicts are not a tool artifact, making non-identifiability/under-power the
better-supported explanation over "all candidates merely wrong."

This task CANNOT and does NOT prove: consciousness, subjective experience, real emotion, autonomy,
agency, self-awareness, AGI, companion readiness; that any *specific* past lab target was
non-identifiable; non-identifiability under *interventional* data (the K2 family — this run is
observational only); non-identifiability for nonlinear/large-alphabet/long-memory worlds beyond
those tested.

## stop condition
- Stop and report failure if: secret scan non-clean; replay verdict ≠ result verdict; positive
  control fails (blind) or negative control false-separates (leak); any test fails.
- Do NOT change ε, seeds, world params, or consistency_min after seeing results. If the result is
  a "check_*" verdict, that IS the reported outcome.

## rollback plan
All work is isolated and additive: new files only under
`src/discovery_loop_ident_calib_001a/`, `tests/test_discovery_loop_ident_calib_001a.py`,
`docs/task_cards/…001A.md`, `artifacts/DISCOVERY-LOOP-IDENT-CALIB-001A/`.
No existing file is modified; no global config touched; no remote push. Rollback = delete those
new paths. Prior artifacts are untouched.

## anti-hardcoding commitments
No if-else stand-in for a mechanism; verdict computed from held-out losses; world identity/true
params never passed to the predictor; band/seeds frozen here; no test-only logic path in the
shipped scorer (leak flag defaults off and is exercised only by an explicit test); strictly causal
(past-only) prediction; replayable from trace.
