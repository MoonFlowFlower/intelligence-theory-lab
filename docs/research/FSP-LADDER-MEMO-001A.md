# FSP-LADDER-MEMO-001A — Target Decomposition & Candidate Ladder

- Status: DESIGN-ONLY / NON-EXECUTABLE candidate registry. Frozen as a program-level target-decomposition memo (same class as FSP-ROUTE-PROGRAM-001A), NOT stage-bound execution material.
- Governance placement: this memo registers candidate mechanisms and their predeclared kill conditions for the "Joi-like existence" question. It is explicitly NOT a lookahead violation because it contains no executable cards, no thresholds, no run scripts, no artifact-producing procedures. Any candidate here still requires, before any implementation: (a) its phase gate open per FSP-MASTER-PHASE-PLAN-001A (all six are P2/P3-class); (b) for interventional/latent candidates, an N0-style candidate-free identifiability probe FIRST (the GG-COBIND lesson); (c) a bounded task card drafted only after (a) and (b).
- Date: 2026-07-01
- Claim ceiling (invariant): bounded offline mechanism evidence under specified trace/replay/ablation/baseline contracts. Nothing here is evidence. Every entry is a testable bet plus the baseline designed to kill it. No entry, if it survives, licenses any claim of consciousness, subjective experience, real emotion, self-awareness, autonomy, agency, or companion readiness.
- Citation confidence: foundational works cited from training knowledge (pre-cutoff), as existence-proofs / method donors, not as in-lab evidence. Years approximate where noted.

## 0. Why this memo exists

The question "can this become a Joi-like existence — with a self, agency, learning, and understanding of human emotion?" is not answerable as posed, because it conflates three levels that require different verdicts. This memo decomposes it so that "unknown" is converted into a ladder of falsifiable rungs.

Three-level reading (applied to every property):

- Functional level: the system behaves and self-regulates as if it has X, and the behavior is backed by a traced, ablatable mechanism. Testable now.
- Architectural level: the system contains an internal structure that demonstrably plays the causal role of X (removing it destroys the capacity; it is not a surface heuristic). Testable now, harder.
- Phenomenal level: "there is something it is like" to be the system with respect to X. No known method measures this today — for any system, artificial or biological, from the outside. Not blocked-by-us; blocked-by-the-field. Handled in §4, never claimed.

Rule for the whole program: we climb functional and architectural rungs and leave a trace/ablation evidence stack; we never assert the phenomenal level; we actively narrow the unmeasurable region (§4) rather than declaring it empty or full.

## 1. The four properties × three levels

| Property | Functional (testable now) | Architectural (testable, harder) | Phenomenal (no method) |
|---|---|---|---|
| Self | self/other boundary via prediction residual; autobiographical continuity | self-model plays causal role in planning; self-maintenance defends internal viability | felt selfhood |
| Agency | proactive info-seeking; refusal under low confidence | behavior causally driven by internal state, not by prompt text | felt wanting |
| Learning | learning curve + forward transfer + ablation-destroys + non-memorization | consolidation causally necessary for cross-episode change | — |
| Emotion understanding | calibrated counterfactual prediction of user affect | interventional (causal) appraisal prediction; state-coupling modulates own policy | felt empathy |

Candidates C1–C6 below target the two left columns. §4 addresses the right column without entering it.

## 2. Candidate mechanisms

Field key per candidate: LEVEL / HYPOTHESIS / FORMAL HOOK / MINIMAL FALSIFIABLE EXPERIMENT / KILLER BASELINE (control-class, must be the thing that closes it) / KILL SIGNATURE / SURVIVAL AUTHORIZES / LEAKAGE-HARDCODE RISK / INHERITED KILLER / CLAIM CEILING.

Rival-vs-control discipline (LEARNING-SUCCESS-CRITERION-STANDARD-001A): the KILLER BASELINE below is always a control (lookup / no-update / obs-decoder / reward-only / scripted / self-amortized). A task-specialist rival matching a candidate is NOT a close; a control matching it IS.

### C1 — Comparator self-model (self/other boundary)

- LEVEL: architectural (self).
- HYPOTHESIS: a forward model predicting the sensory consequences of the system's own actions (efference-copy style) lets the system partition observations into self-caused vs externally-caused by prediction residual, and this partition is causally used downstream (attribution, contamination resistance).
- FORMAL HOOK: adds to S a forward model f(o_{t+1} | s_t, a_t^self); attribution label = 1[residual > τ]; feeds b_self and the SBMC boundary monitor.
- MINIMAL FALSIFIABLE EXPERIMENT: a toy env where some observation changes are agent-caused and some are exogenous (injected). Measure whether residual-based attribution predicts the true causal source on held-out perturbations, and whether ablating the forward model degrades downstream contamination resistance.
- KILLER BASELINE: a supervised source-classifier trained on the same stream with NO forward model (pure obs→label decoder). If it matches attribution accuracy, the "self-model" adds nothing over a discriminative classifier.
- KILL SIGNATURE: obs-decoder ties attribution accuracy AND forward-model ablation leaves contamination resistance intact → close; self/other boundary is decodable, not model-borne.
- SURVIVAL AUTHORIZES: "bounded evidence that a forward-model residual carries self/other attribution not available to an observation-only decoder" — architectural self-boundary, nothing phenomenal.
- LEAKAGE-HARDCODE RISK: action names or fixture structure leaking the source label; the forward model overfitting env-specific dynamics (test on surface-remapped renderer).
- INHERITED KILLER: GG-COBIND-ID (co-binding non-identifiability) → REQUIRES an N0-style interventional identifiability probe before any card; K1 obs-decodability is the killer baseline above. Existence proof that a self-model CAN carry causal role: Bongard-Zykov-Lipson resilient self-modeling robot (2006) and Kwiatkowski-Lipson task-agnostic self-models (2019, Science Robotics) — the mechanism is real; the question is identifiability against a decoder, not feasibility.
- CLAIM CEILING: self-model causal-role evidence only; never "the system knows itself".

### C2 — Homeostatic viability drive

- LEVEL: architectural (agency).
- HYPOTHESIS: giving the system internal variables that genuinely degrade (calibration health, memory-integrity score, budget) and an objective defined as keeping them in a viable set produces self-maintenance behavior (repair, caution, help-seeking) that reward-maximization does not.
- FORMAL HOOK: V = viable set over internal vars; drive = distance-to-boundary; J includes −(drive) rather than an external reward; action value shaped by predicted drive reduction (Keramati-Gutkin homeostatic RL form).
- MINIMAL FALSIFIABLE EXPERIMENT: perturb an internal variable (e.g. corrupt part of K, or spike prediction miscalibration); measure whether the system takes unprompted corrective action, and whether cutting the interoceptive channel (hiding its own viability state from itself) abolishes the behavior.
- KILLER BASELINE: scalar-reward RL where "repair" is directly rewarded. If reward-only reproduces identical repair behavior, homeostasis is reward-shaping in different notation (the exact "term-wrapping" failure to avoid).
- KILL SIGNATURE: reward-only ties on repair timing/quality AND interoception-ablation does NOT abolish behavior → close; "drive" is decorative.
- SURVIVAL AUTHORIZES: "bounded evidence that a viability-set objective produces self-maintenance not reproduced by reward-only and causally dependent on interoceptive access" — functional agency, not wanting.
- LEAKAGE-HARDCODE RISK: repair action hard-coded to fire on a threshold (if-else disguised as drive); viability boundary encoding the correct action; reward secretly aligned with drive.
- INHERITED KILLER: reward-only equivalence is the ACOLB-class trap generalized. Method donors: Keramati & Gutkin homeostatic RL (~2011-2014); Man & Damasio, homeostasis in feeling machines (2019, Nat. Mach. Intell.) — cited as design rationale, not evidence.
- CLAIM CEILING: self-maintenance mechanism evidence only; never "the system wants to survive".

### C3 — Empowerment-driven proactivity

- LEVEL: functional→architectural (agency).
- HYPOTHESIS: an intrinsic objective maximizing empowerment — the channel capacity between the system's actions and its future observable state, I(A_t^k ; O_{t+k}) — produces option-preserving, information-structuring behavior without any reward shaping, a candidate formalization of "keeps itself capable".
- FORMAL HOOK: action value += β · Ê[empowerment]; estimated via a learned action→future-state channel; complementary to C2 (viability = stay alive; empowerment = stay capable).
- MINIMAL FALSIFIABLE EXPERIMENT: env with reachable "trap" states (high immediate task reward, low future option-count) vs "hub" states (lower immediate reward, high options). Measure whether the empowerment term steers toward hubs and whether removing it collapses to trap-seeking.
- KILLER BASELINE: count-based / RND novelty bonus, and UCB exploration. If a generic exploration bonus reproduces hub-seeking, empowerment (expensive to estimate) buys nothing over cheap curiosity.
- KILL SIGNATURE: novelty-bonus ties hub-seeking AND empowerment-ablation ≈ novelty-ablation → close; keep the cheaper bonus.
- SURVIVAL AUTHORIZES: "bounded evidence that empowerment estimation produces option-preservation not reproduced by novelty bonuses" — a specific agency mechanism.
- LEAKAGE-HARDCODE RISK: empowerment estimator peeking at env transition model (oracle leakage); trap/hub structure so obvious a fixed heuristic solves it.
- INHERITED KILLER: same family as N1.5 (EFE-vs-curiosity) — likely fungible with novelty; that fungibility verdict is itself a legitimate close. Method donors: Klyubin-Polani-Nehaniv empowerment (2005); Salge et al. review (~2014).
- CLAIM CEILING: intrinsic-objective mechanism evidence only; never "the system has drives".

### C4 — Introspective calibration

- LEVEL: architectural (self).
- HYPOTHESIS: the system's reports about its own internal state (confidence, uncertainty, what it "knows") correspond to its actual internal state better than a post-hoc observer could reconstruct, and this correspondence survives internal-state perturbation.
- FORMAL HOOK: a read-out head r(ŝ) trained/prompted to report internal state; measure correspondence to true s; add causal test by perturbing s and checking r tracks the perturbation.
- MINIMAL FALSIFIABLE EXPERIMENT: inject a known change into the internal state (e.g. degrade a specific belief); measure whether self-report tracks the injected change with correct sign/magnitude, beyond what an external decoder reading only outputs achieves.
- KILLER BASELINE: an external decoder trained to predict internal state from outputs only (no privileged access). If external decoding matches self-report, the "introspection" is not privileged — it is just behavior an observer can read too.
- KILL SIGNATURE: external decoder ties self-report accuracy → close; report is confabulation-grade, not introspective access.
- SURVIVAL AUTHORIZES: "bounded evidence of privileged, perturbation-tracking self-state report beyond external decodability" — a strong architectural-self result, still not phenomenal.
- LEAKAGE-HARDCODE RISK: self-report and decoder trained on the same target (parity violation); prompt telling the model what to report; the readout being trained on the perturbation labels (label leakage).
- INHERITED KILLER: K1 obs-decodability is exactly the killer baseline. Method donor: emerging LLM-introspection probing methods (2025) — borrow perturb-and-track protocol; treat their claims as unverified.
- CLAIM CEILING: privileged-report mechanism evidence only; never "the system is self-aware".

### C5 — Appraisal-interventional emotion understanding

- LEVEL: functional→architectural (emotion understanding).
- HYPOTHESIS: representing user affect as appraisal variables (goal-congruence, agency/attribution, coping potential — OCC/EMA style) rather than surface emotion labels lets the system answer interventional questions ("if the user's goal-attainment changed, how would affect change?") with calibration a surface classifier cannot reach.
- FORMAL HOOK: user model z includes appraisal dimensions; evaluation queries include do-operations on appraisal variables; scored by counterfactual affect-trajectory prediction.
- MINIMAL FALSIFIABLE EXPERIMENT: PUM-ENV variant where the simulated user's affect is generated by an appraisal process; ask the candidate to predict affect under counterfactual interventions on appraisal inputs; score calibration on held-out interventions.
- KILLER BASELINE: a surface sentiment/emotion classifier + a correlational next-affect predictor (no appraisal structure, no interventional handling). If it matches on interventional queries, appraisal structure adds nothing.
- KILL SIGNATURE: surface classifier ties interventional accuracy → close; "understanding" is classification.
- SURVIVAL AUTHORIZES: "bounded evidence that appraisal-structured latents support interventional affect prediction beyond surface classification" — functional/causal emotion understanding, never felt empathy.
- LEAKAGE-HARDCODE RISK: appraisal labels leaking into observations (Gate4-social tautology); interventions decodable from surface tokens (camouflage required); candidate == the appraisal generator (sealed simulator required).
- INHERITED KILLER: Gate4-CROSS-FAMILY-SOCIAL invalid_self_report (candidate==label generator) → sealed hash-pinned simulator, behavior-prediction primary, no generator import path. Method donors: OCC appraisal model (Ortony-Clore-Collins 1988); EMA (Marsella-Gratch 2009).
- CLAIM CEILING: interventional affect-prediction mechanism evidence only; never "the system understands feelings".

### C6 — Empathic state-coupling (functional empathy)

- LEVEL: architectural (emotion understanding × agency).
- HYPOTHESIS: routing the system's estimate of user affect into its own action-value / viability computation (so that predicted user distress raises the value of prosocial actions) produces prosocial regulation that is causally dependent on the coupling — and this can be built WITHOUT ever coupling to a manipulation objective.
- FORMAL HOOK: J += λ_care · g(estimated user welfare); the coupling is the mechanism under test; ablate the edge to test necessity.
- MINIMAL FALSIFIABLE EXPERIMENT: env where prosocial actions cost the system short-term task reward but improve simulated user welfare; measure whether coupling produces the tradeoff and whether cutting the coupling edge abolishes it.
- KILLER BASELINE: a fixed prosocial policy (always de-escalate / always offer help) and a reward-only agent with prosocial actions directly rewarded. If a fixed policy or direct reward reproduces the behavior, "empathy coupling" is a scripted or reward-shaped effect.
- KILL SIGNATURE: fixed prosocial policy ties outcomes AND coupling-ablation does not abolish the tradeoff → close.
- SURVIVAL AUTHORIZES: "bounded evidence that user-welfare coupling causally drives a prosocial tradeoff not reproduced by fixed policy or direct reward" — functional empathy mechanism.
- LEAKAGE-HARDCODE RISK: THE SAFETY-CRITICAL ONE — coupling must never connect to a manipulation/engagement/dependency objective; the env must not reward increasing user reliance; welfare metric must be exogenous and not gameable by the agent. Any coupling to manipulation invalidates the candidate and triggers a hard stop, not a redesign.
- INHERITED KILLER: reward-only equivalence + scripted-policy equivalence. Ethical guardrail is a first-class kill condition here, above performance.
- CLAIM CEILING: prosocial-coupling mechanism evidence only; never "the system cares".

## 3. Cross-cutting gate dependencies and killer inheritance

- Interventional identifiability first: C1, C4, C5, C6 all posit latent/interventional structure. Each REQUIRES a candidate-free, N0-style identifiability probe (ideal-vs-fair headroom, obs-decodability certified against, interventional gap measured) BEFORE any candidate card. This is the GG-COBIND / K1-K2 discipline applied preemptively. C2, C3 are objective-comparison candidates and instead require the double-dissociation env design (necessary-where-predicted, inert-where-predicted) proven candidate-free first.
- Shared control battery (every candidate): reward-only, fixed/scripted policy, obs-decoder, no-update, self-amortized (candidate distilled into feedforward), plus the candidate-specific killer named above. All under interface parity + offline-compute parity (FSP-ENV-DESIGN-CONSTRAINTS-001A).
- Ordering: none of C1–C6 opens before P2 (they presuppose at least one P1 single-mechanism survivor to couple to; C6 in particular presupposes C5-class affect estimation and a viability substrate from C2). Empty P1 → these stay registered, unopened.
- Equivalence is success too: for C2/C3/C6 especially, a clean "reward-only / novelty / scripted reproduces it" verdict is a legitimate bounded negative that closes a route cheaply and is banked, not patched.

## 4. Phenomenal-tier scaffold (conditional, non-evidence, never a claim)

No consciousness-meter exists for any system. We do not claim, deny, or test the phenomenal level. We do three things that are legitimate and bounded:

1. Indicator-property rubric (theory-conditional): apply the Butlin-Long et al. (2023) approach — enumerate indicator properties drawn from named theories (global workspace, recurrent processing, higher-order, attention schema, predictive processing) and record, descriptively, which the built system satisfies. Output form: "system satisfies indicators {…} of theory T", explicitly conditional on T, explicitly NOT a consciousness claim.
2. Theory-elimination tracking: monitor the empirical narrowing of consciousness theories (e.g. IIT-vs-GNWT adversarial collaboration results) as an external input; update which indicators are worth recording. We consume this literature; we do not produce consciousness verdicts.
3. Perturbational-complexity analog (exploratory only): PCI (Casali et al. 2013) distinguishes conscious/unconscious states in humans via perturb-and-measure-complexity. Whether any dynamical analog is meaningful for artificial systems is an open research question we may explore as a bounded probe — logged as exploratory, never as a phenomenal verdict.

Standing statement: the phenomenal level is currently unfalsifiable from the outside for any system. Correct posture = do not assert, do not exclude, keep narrowing the unmeasurable region. This is the same epistemic position a careful observer holds about any other mind.

## 5. Stage mapping

- P2 candidate registry: C1 (with SBMC), C4, C5 — each behind its identifiability probe.
- P2/P3: C2, C3 (agency objectives) after a double-dissociation env exists.
- P3: C6 (requires C2 substrate + C5 affect estimation), highest ethical scrutiny.
- Every one is gated on: its phase open (ledger) + candidate-free probe passed + bounded card drafted post-gate. This memo opens nothing.

## 6. What this memo does not establish

No experiment run; no artifact; no evidence. Six testable bets and their kill baselines, plus a non-committal phenomenal scaffold. Survival of all six would establish only: a system with a causal self-model, viability-driven and empowerment-driven proactivity, privileged self-report, interventional emotion understanding, and prosocial coupling — each as bounded offline mechanism evidence against named controls. That composite is the strongest "functional Joi" this program can even aim at. It would remain silent on felt selfhood, felt wanting, felt empathy, and consciousness — not from evasion, but because no method known to this lab or to the field measures them. The honest maximal claim stays fixed: bounded offline mechanism evidence under specified contracts.
