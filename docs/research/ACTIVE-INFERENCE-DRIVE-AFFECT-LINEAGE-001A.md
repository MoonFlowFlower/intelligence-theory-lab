# ACTIVE-INFERENCE-DRIVE-AFFECT-LINEAGE-001A

Status: research synthesis (literature lineage). NOT an experiment. NOT a task card.
Authorizes no implementation, no EGO/AIRI contact, no schema change.

Research layer: mechanism-hypothesis vocabulary for the engineering-implementation layer.

Claim ceiling (binding): This note collects a *design language* for two requested
components — (A) self-originated drive / "wanting", (B) composing affect. It does NOT
claim that any system built from it has consciousness, subjective experience, real
emotion, self-awareness, autonomy, or agency. "Drive" and "emotion" below denote
functional state variables, not felt states. Grounding a mechanism in this theory is
NOT evidence the mechanism is non-trivial; every implemented mechanism still faces the
lab's baseline/ablation/replay discipline.

---

## 0. Why this note exists

User goal (verbatim intent, three prior turns): a companion that (1) acts from its own
internal state rather than blind obedience, where the impulse is "wants to" not "must"
(no `random-timer`), and (2) has emotion that *composes and derives* rather than N
hard-coded labels. Prior conclusion: a behavior-tree + fake-latent + random-timer
satisfies the *surface* of this and is baseline-equivalent under audit. The open
question was whether there is a *principled, non-hardcoded, non-random* source for
drive and affect.

There is a mature literature line that supplies exactly that vocabulary: the **free
energy principle (FEP) / active inference**, its **interoceptive** extension for affect,
and the **intrinsic-motivation RL** family that makes it buildable. This note maps that
line to the two components, names the buildable substrate, and — per lab role — names
the failure modes and the baselines each candidate must beat.

**Central framing (do not skip):** FEP/active inference is best treated as a *generator
of candidate mechanisms*, not as a result. The theory is criticized as near-tautological
and possibly unfalsifiable at the global level (see §3). Its value here is that it
produces *specific, simulable* generative models whose behavior is testable. The
elegance of the derivation carries zero evidential weight. Only the baseline-beaten,
replayable behavior does.

---

## 1. Component A — self-originated drive ("wanting", not "must")

### 1.1 The non-hardcoded source of a drive
In active inference, a homeostatic need is encoded as a **prior over interoceptive
states** (the viable range of a physiological variable). Behavior that reduces the
discrepancy between predicted-preferred and actual interoceptive signal is what
"feeling hungry → seek food" *becomes* — not an `if hunger>k` branch, but
prediction-error minimization toward a prior. (Pezzulo/Rigoli/Friston; Parr-Pezzulo-
Friston 2022; Yao/Pezzulo-style interoceptive-control simulations.)

Independently, **homeostatic RL** (Keramati & Gutkin 2014) proves that, when primary
reward is defined as *drive reduction* (reduction of distance between an internal state
and its setpoint), a reward-maximizing agent provably minimizes homeostatic error. This
is the discrete, implementable cousin of the interoceptive-active-inference story and is
a **mandatory baseline** (see §1.4): it gives "hungry→eat" from a setpoint with no
hand-written rule, *without* any active-inference machinery.

### 1.2 "Wants to" not "must" — this is a real, named mechanism
Active inference selects policies by a **softmax over negative expected free energy
(EFE)**. The output is a *distribution over policies that is sampled*, not an argmax.
The temperature (a precision parameter) controls how compulsive vs. exploratory the
choice is. This is a precise formalization of the user's "想做 not 必定做": inclination,
overridable, stochastic-but-coherent. (Friston et al., "Active inference and epistemic
value", 2015.)

NOTE — this alone does not escape baseline: a softmax over a utility table is also
"want not must" and is what The Sims already does. The escape, if any, is in §1.3 + §2.

### 1.3 The source of an unprompted "想法" — epistemic value, not a random timer
EFE decomposes into:
- **pragmatic value** (reach preferred/ homeostatic outcomes) — exploitation;
- **epistemic value** (expected information gain about hidden states) — exploration /
  curiosity.
The epistemic term is an *intrinsic* driver: the agent acts to resolve uncertainty even
with no external reward. This is the principled replacement for `random-timer`: an
unprompted action ("comes to find you") can originate from an information-seeking /
uncertainty-reducing term computed from internal state, **not** from `random()<p`. The
same idea appears in intrinsic-motivation RL: curiosity = prediction error (Pathak ICM
2017), learning-progress (Oudeyer & Kaplan 2007), empowerment (Klyubin 2005; Mohamed &
Rezende 2015).

### 1.4 Buildable substrate (so this is architecture, not "scale will emerge")
- **pymdp** (Heins et al. 2022): Python library for discrete-state (POMDP) active
  inference agents; lets you build an EFE-driven agent without deriving the math. Good
  for a small, fully-instrumented proof-of-mechanism with full trace/replay.
- Intrinsic-motivation RL stack (ICM, learning-progress, empowerment) for the
  continuous / higher-dim case.
- Homeostatic RL for the setpoint baseline.

### 1.5 Failure modes you WILL hit (predeclare these as challengers)
- **Dark-room problem**: a pure surprise-minimizer can prefer a dark, unchanging room
  (perfectly predictable). The epistemic term is the *proposed* fix; critics note the
  fix is somewhat stipulative. → Test that your agent does NOT collapse to the dark room.
- **Noisy-TV / white-noise problem** (Pathak; Schmidhuber): prediction-error curiosity
  is captured by stochastic stimuli (infinite, unlearnable error). → use learning-
  progress or control-relevant (inverse-model) features, and test against a noisy
  distractor.
- **Baseline equivalence (lab-mandatory)**: the active-inference agent must beat, on a
  pre-registered metric, at minimum: behavior-tree / utility-softmax, **homeostatic RL**
  (§1.1), random policy, observation-only lookup, and `predict_all`/oracle degeneracies.
  If its behavior is indistinguishable from homeostatic-RL, the verdict is
  baseline-equivalence — the active-inference framing is then explanatory surplus, not
  evidence.

---

## 2. Component B — composing affect (not N hard-coded labels)

### 2.1 Theory: emotion as interoceptive inference
Seth & Critchley ("Extending predictive processing to the body: emotion as
interoceptive inference", BBS) and Seth's interoceptive-predictive-coding model frame an
emotion as the brain's *inference about the causes of interoceptive signals*. Affect is
then not a discrete label but a point/trajectory in a low-dimensional space — most
commonly **valence × arousal** (Barrett's core affect) — which **composes and shifts**,
matching the user's "情绪会组合衍生" requirement far better than N buttons.

### 2.2 The premise the user asserted is CONTESTED — do not hardcode the answer
The user assumed emotions are "encoded in genes" (sadness/fear/anger as primitives).
Status: **unsettled**.
- **Basic / nativist** (Panksepp): ~7 evolutionarily conserved primary affective
  systems (e.g., FEAR, SEEKING, RAGE…).
- **Constructed** (Barrett, theory of constructed emotion): emotions are constructed
  online from core affect (valence/arousal) + learned concepts; denies dedicated
  essentialist emotion circuits.
- Recent work (van Heijst, Kret & Ploeger 2025) argues the two may explain *different*
  things (emotion vs. feeling) and are partly complementary; evidence for both is still
  limited and causation-focused.
→ **Design consequence:** make "fixed basis vs. learned/constructed affect" an
*experimental variable*, not an architecture assumption. A system that hardcodes a basis
set has imported a contested empirical claim and is also more baseline-attackable.

### 2.3 Buildable substrate
A low-dim continuous affective latent (start: valence/arousal) driven by interoceptive
prediction error, which **modulates** policy precision / priors in Component A (affect
as a controller of the EFE temperature and of which preferences are active). "Specific
emotions" = regions/trajectories in that latent, optionally composed with learned
concept embeddings (the constructed view) — testably vs. a fixed-label baseline.

### 2.4 Claim ceiling for B (hard line)
This yields a *functional* affect variable that composes and causally modulates action.
It does **not** yield felt emotion. Seth's account is explicitly about inference over
bodily states, not a solution to phenomenal experience. Per the lab contract, "real
emotion" is a forbidden claim. The most this can ever support is: "a non-hardcoded,
composing affective state that interventionally modulates behavior" — and only if it
beats a fixed-label baseline under replay.

---

## 3. The hard caveats (lab-auditor section)

1. **Substrate ≠ property.** A neural / active-inference implementation whose *behavior*
   equals a behavior-tree or homeostatic-RL baseline IS that baseline, for evidence
   purposes. "Implemented with active inference" is not a result.
2. **Global FEP is criticized as unfalsifiable / trivial** ("compatible with every state
   of affairs", dark-room/triviality disputes). Treat FEP as a *design language* that
   generates specific generative models; validity lives only in the specific model's
   tested, baseline-beaten behavior.
3. **Claim ceiling unchanged.** Bounded offline mechanism evidence only. No
   consciousness, no real emotion, no self, no autonomy. The felt/phenomenal residue is
   untouched by everything above and is not made testable by it.
4. **"Tie ≠ progress toward subjecthood."** Re-stating the standing result: baseline
   equivalence is a *negative* result for the special-property question, regardless of
   how principled the candidate's pedigree is.

---

## 4. What this unlocks (why doing B first helps engineering)

It replaces "intelligence will emerge from scale/prediction" (an untestable promissory
note) with **named, buildable modules**, each with a **known failure mode** and a
**predeclared baseline it must beat**:

| Want | Mechanism | Substrate | Must beat | Known failure |
|---|---|---|---|---|
| drive, non-hardcoded | interoceptive prior + EFE pragmatic | pymdp / homeostatic-RL | behavior-tree, homeostatic-RL | dark room |
| "wants not must" | softmax over −EFE | pymdp | utility-softmax | (none new) |
| unprompted impulse | epistemic value / curiosity | ICM, learning-progress | random-timer, count-based | noisy-TV |
| composing emotion | affect as interoceptive inference, valence/arousal latent | continuous latent + concept emb. | fixed-label affect | contested basis premise |

Future task cards can therefore predeclare challengers *before* implementation, which is
exactly where past lines failed late (baseline saturation discovered post-hoc).

---

## 5. Suggested next step (NOT authorized here)

A candidate-free preflight on a tiny discrete world (pymdp-scale, fully traced): does an
EFE-driven drive beat **homeostatic-RL + behavior-tree + random** on a pre-registered,
balanced metric, with the dark-room and noisy-TV challengers active? This is the lab's
existing discipline applied to a *principled* candidate. A bounded task card must be
drafted and authorized separately before any code.

This note does not authorize that card; it supplies its vocabulary.

---

## Sources

- Parr, Pezzulo & Friston, *Active Inference: The Free Energy Principle in Mind, Brain, and Behavior* (MIT Press, 2022) — https://mitpress.mit.edu/9780262045353/active-inference/
- Interoceptive control via active inference (homeostatic/allostatic/goal-directed) — https://www.sciencedirect.com/science/article/abs/pii/S0301051122000084
- Keramati & Gutkin, "Homeostatic reinforcement learning…" (eLife 2014) — https://elifesciences.org/articles/04811
- Friston et al., "Active inference and epistemic value" (2015) — https://www.fil.ion.ucl.ac.uk/~karl/Active%20inference%20and%20epistemic%20value.pdf
- Heins et al., "pymdp: A Python library for active inference in discrete state spaces" (2022) — https://arxiv.org/pdf/2201.03904
- Seth & Critchley, "Extending predictive processing to the body: emotion as interoceptive inference" (BBS) — https://www.cambridge.org/core/journals/behavioral-and-brain-sciences/article/abs/extending-predictive-processing-to-the-body-emotion-as-interoceptive-inference/A53E081B5EEBD7CF7658F3D484714AFE
- Seth, "Interoceptive predictive coding / conscious presence" (Frontiers 2011) — https://www.frontiersin.org/journals/psychology/articles/10.3389/fpsyg.2011.00395/full
- "Predictive codes of interoception, emotion, and the self" (PMC) — https://pmc.ncbi.nlm.nih.gov/articles/PMC3940887/
- Theory of constructed emotion (Barrett) — https://en.wikipedia.org/wiki/Theory_of_constructed_emotion ; https://pmc.ncbi.nlm.nih.gov/articles/PMC12164598/
- van Heijst, Kret & Ploeger, "Basic Emotions or Constructed Emotions: …Evolutionary Perspective" (2025) — https://journals.sagepub.com/doi/10.1177/17456916231205186
- Pathak et al., "Curiosity-driven Exploration by Self-supervised Prediction" (ICM, ICML 2017) — https://pathak22.github.io/noreward-rl/resources/icml17.pdf
- Oudeyer, Gottlieb & Lopes, "Intrinsic motivation, curiosity, and learning" — http://www.pyoudeyer.com/oudeyerGottliebLopesPBR16.pdf
- Friston, Thornton & Clark, "Free-energy minimization and the dark-room problem" (Frontiers 2012) — https://www.frontiersin.org/journals/psychology/articles/10.3389/fpsyg.2012.00130/full
