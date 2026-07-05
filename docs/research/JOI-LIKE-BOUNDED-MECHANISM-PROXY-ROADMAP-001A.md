# JOI-LIKE BOUNDED MECHANISM-PROXY ROADMAP 001A

Status: **DRAFT / analysis-only / implementation NOT authorized.**
Layer: engineering-implementation + mechanism-hypothesis (default allowed).
This document proposes no new gate, bridge, or runtime change. It ranks routes,
formalizes candidate mechanisms, and drafts one bounded task card. Per the
operating contract, drafting a card requires stopping before implementation.

Global claim ceiling (inherited, non-negotiable): nothing in this document, and
nothing any proposed experiment can produce, may be upgraded into evidence of
consciousness, subjective experience, real emotion, self-awareness, autonomy,
agency, AGI, companion-readiness, EGO-mainline-readiness, or the correctness of
any total theory (Bio-CMBC, CVPSM, VCCO, CMBC, R/G). The strongest reachable
claim is: *bounded offline mechanism/learning evidence under a specified
trace/replay contract, relative to a named fair-baseline panel.*

Evidence-status tags used below: **[FACT]** sourced/established, **[INFER]**
defensible inference, **[ASSUM]** assumption, **[UNKNOWN]** not yet decidable.

---

## PART 0 — FRAMING CORRECTION (read before the ranking)

The literal question "the most likely engineering route to a Joi-like
intelligent electronic life" is mis-framed because it fuses three layers your
own negative lineage already separated
(`itl-why-no-qualified-mechanism-testbed-identifiability-ceiling`):

1. **Product Joi** (performance-simulation + engineering): a system that *looks
   alive*, holds memory, takes initiative, models the user. This needs **no
   mechanism gate**. It is buildable today. Your operator already chose this
   target for `joi-demo` (north-star: Bar-1 life-likeness = non-hardcoded +
   extensible + ablation-provable; explicitly NOT Bar-2 special-mechanism, NOT
   Bar-3 subjective proof). [FACT, from `joi-demo-north-star`]
2. **Science** (mechanism / functional-subject proxy): prove the system carries
   a mechanism that beats the strongest fair baseline under equal access. This
   is the lab's job, and your logs show **most routes return bounded-negative**
   because of the identifiability ceiling. [FACT, lineage below]
3. **Philosophy** (consciousness / phenomenal experience): **no accepted test
   exists anywhere.** This is not a missing harness; it is out of scope. [FACT]

**Reconstructed question, split by layer:**
- "Most likely route to a *Joi-like artifact*" → Layer 1. Answer is **engineering
  + performance simulation**, and it proves nothing about subjectivity. (Lives in
  `joi-demo`, not this lab.)
- "Most likely route to *new admissible mechanism evidence*" → Layer 2. Answer
  is the **single surviving thread**: cross-episode meta-learned prior that beats
  a *fair amortized/meta baseline* under held-out non-stationarity. Everything
  that tries to win *within a single episode by identifying a latent* has
  saturated. [INFER, strongly supported]
- "Route to Layer 3" → **none.** Stop asking #2 to deliver #3.

The central recurring fact you must design around:

> **Identifiability is a property of the access regime, not of the candidate.**
> Under an equal-access fair-baseline contract, whatever lets the candidate
> identify a latent also lets the baseline identify it. K1 (obs-decodability)
> and K2 (interventional saturation) squeeze from both sides. The only residual
> axis is *statistical efficiency / amortization across episodes* — and the
> optimal estimator of that is itself a fair baseline. [INFER, from
> `itl-why-no-qualified-mechanism-testbed-identifiability-ceiling`,
> `itl-self-boundary-killer-catalog-001a`; CRL identifiability literature]

This is why the ranking below scores routes by **mechanism-evidence potential
under equal access**, NOT by raw capability or product polish. The routes with
the highest product value (memory chatbots, world-model planners, user-modeling)
have the **highest baseline-saturation risk**, hence the lowest Layer-2 value.

---

## PART 1 — SIX-LAYER CLASSIFICATION (allowed vs forbidden per layer)

| Layer | May claim | May NOT claim | Where it lives |
|---|---|---|---|
| 1. Performance simulation | "looks alive", demo fidelity, latency, UX, replay-faithful rendering | that surface behavior is a mechanism or subjectivity | `joi-demo` (product) |
| 2. Engineering implementation | "it runs / integrates / is reproducible / passes tests" | that integration = mechanism validity | lab `src/`, `tests/` |
| 3. Mechanism hypothesis | "mechanism M produces discriminative predictions vs fair panel P under trace/replay contract C" | that surviving one test = subject / self / emotion | lab gates |
| 4. Learning / adaptation | "measured improvement under specified shift vs fair amortized/meta baseline" | "it learns like a person" / open-ended growth | lab (TLGP lineage) |
| 5. Agency / subject validation | **~nothing reachable today**: honest output is "no admissible positive evidence under equal access" | agency, autonomy, will, self | currently empty |
| 6. Philosophical consciousness | nothing empirical; survey positions only | any empirical claim of phenomenal experience | out of scope |

Default working layers: **2 + 3 (+4 for the live thread).** A result at Layer 2/3
**must not** be re-narrated as Layer 5/6. That re-narration is the single failure
mode your contract exists to prevent.

---

## PART 2 — ROUTE RANKING (A–J)

First, a judgment correction: **A–J are not parallel alternatives.** B (tool-use
substrate), G (attention/salience), J (multi-timescale memory) are *cross-cutting
components*, not mechanism routes — they can be present in any route and prove
nothing on their own. The genuine mechanism-bearing candidates are A, C, D, E, F,
H, I. They are ranked by **Layer-2 mechanism-evidence potential under equal
access**, with raw eng-feasibility shown separately so you can see the divergence.

Scoring: L/M/H. "Baseline-saturation risk" HIGH = a named fair baseline already
closes (or has closed) the gap in your logs or in current public SOTA.

| # | Route | Mech-evidence potential | Eng feasibility | Falsifiability | Baseline-saturation risk | Realistic claim ceiling |
|---|---|---|---|---|---|---|
| 1 | **Cross-episode meta-learning under drift** (learning-adaptation; instantiates on C/D) | **M** (on probation) | M–H | **H** | **H** (public ORBIT/ECET/AMAGO-2 are the fair baseline, and they are getting stronger) | bounded learning-adaptation evidence vs fair meta-baseline |
| 2 | **I. Controlled initiative as control-value** (trigger/veto/cooldown/state-transition) | **M** (NOT yet closed in lab) | H | **H** | M (rate-matched random / scripted FSM) | bounded closed-loop control-value evidence |
| 3 | D. World model + prediction-error + planning | L–M | H | H | **H** (Gate1 `graph_cache_collapse`: transition-table / successor-map / count-table saturate) | bounded |
| 4 | H. Social inference / user-modeling | L | H | H | **H** (GATE4-SOCIAL: candidate == label-generating tautology; equal-access partner-model parity) | bounded |
| 5 | E. Active inference / viability objective | L (as *evidence*) | M | **L–M** (free-energy-min is not falsifiable *as such*) | **H** (ACOLB closed as `discounted-batch-LS` equivalence) | bounded; **do NOT use FE-minimization as evidence** |
| 6 | C. Skill library / curriculum / self-verification | L–M | H | M | H (scripted curriculum; self-verify is an eval harness, not a subject mechanism) | learning-adaptation at best |
| 7 | A. LLM + episodic/semantic memory + reflection/replay | **L** | **H** | M | **VERY H** (obs-only / lookup / graph-cache; reflection has *no standardized eval* — public gap) | performance-simulation |
| — | F. Self-model as bounded latent | **~None under equal access** | M | — | **CLOSED** (co-binding non-identifiable, K2; `GG-COBIND-ID-001A`) | **route CLOSED — do not re-open without a new identifiability construction** |
| — | B / G / J | cross-cutting components, not standalone routes | — | — | — | n/a |

**Headline of the table:** product value and Layer-2 value are *anti-correlated*
here. A/D/H (the most Joi-like, most fundable) carry the **highest** saturation
risk. The only two routes with non-saturated mechanism potential are #1 (live,
on probation) and #2 (genuinely un-tested in your lineage). If the strongest fair
baseline closes either gap, the contract requires **closing/redesigning**, not
patching to pass. Negative evidence is the expected and acceptable product.

### Per-route formal object + the 8 mandatory answers (condensed)

Notation: S=state, O=observation, A=action, M=memory/latent, U=update rule,
J|V=objective/viability, ∂=agent/non-agent boundary.

**Route 1 — Cross-episode meta-prior (live thread).**
S = (current task regime r_t ∈ rule-family R, within-episode history). O =
adaptation observations (no regime label). A = prediction / control action.
M = amortized prior θ over R carried *across* episodes + within-episode posterior.
U = within-episode Bayesian-ish posterior update; *across* episodes, meta-update
of θ. J|V = held-out task return under regimes/values unseen in adaptation.
∂ = agent controls A, M; environment controls regime switches and O-noise.
(1) Explains: faster adaptation on a *new* regime than from-scratch, by reusing
a learned family prior. (2) Cannot explain: any single-episode advantage (none
exists vs fair within-episode baseline — TLGP-001A: max_fair already at floor
*within* episode, headroom only vs cold observers). (3) Simpler mimic: a fair
amortized meta-learner / history-conditioned transformer trained across episodes
(THIS is the killer baseline). (4) Killer ablation: reset M between episodes
(no cross-episode carry) → advantage must vanish. (5) Falsifier: fair meta-
baseline of matched data+capacity reaches candidate performance → close. (6) Toy
env: non-stationary POMDP with a regime that switches across episodes and is not
single-episode-decodable. (7) Trace/replay: per-episode (belief-before, action,
predicted-O, actual-O, prediction-error, updated-belief, cross-episode θ
snapshot), replayable without future info. (8) Ceiling: bounded learning-
adaptation evidence vs fair meta-baseline; NOT "it learns".
Prior negatives: TLGP-001A caveat #2 ("most likely place the route collapses");
TLGP-001B INVALID (positive-control design flaw); identifiability-ceiling memo.

**Route 2 — Controlled initiative as control-value.**
S = environment + user state with time-varying "intervention value". O = partial
obs of that state. A = {act-now, hold} gated by trigger→veto→cooldown. M =
belief about intervention value + cooldown timer. U = belief update + controller
state machine over (trigger, veto, cooldown). J|V = downstream task viability /
return after the initiative decision. ∂ = agent controls the gate and A; env
controls when intervention is actually valuable.
(1) Explains: whether *gated* initiative carries decision-relevant information
that improves downstream viability. (2) Cannot explain: anything about *why* it
acts (no motivation/agency claim). (3) Simpler mimic: rate-matched random
initiative, scripted-FSM initiative, always-on, never-on, post-hoc "good moment"
classifier. (4) Killer ablation: sever trigger→A coupling (fire at same rate but
independent of belief) → viability must drop to rate-matched-random. (5)
Falsifier: rate-matched random matches candidate viability → initiative is
decorative → close. (6) Toy env: episodic task where acting at the right hidden
moment raises return and acting wrongly costs. (7) Trace/replay: (belief, trigger
score, veto, cooldown, action, downstream return), replayable. (8) Ceiling:
bounded closed-loop control-value evidence; NOT autonomy/agency/will.
Why this is worth doing: it is a **control-value** question, not a **latent-
identifiability** question, so it structurally sidesteps the ceiling that closed
F/H/D. It is not in your closed-families list. [INFER]

**Route 3 — World model + prediction-error + planning (D).**
S = env state. O = obs. A = action. M = learned transition/world model. U =
model-based belief update + planning. J|V = planning return / prediction
accuracy. ∂ = agent controls A, M.
(1) Explains: action-conditioned prediction + planning. (2) Cannot explain: any
*representational* advantage when the environment is enumerable. (3) Simpler
mimic: transition-table / successor-map / count-table / FSM-planner / episodic-
traversal (mandatory graph-cache challengers). (4) Killer ablation: no-transition
/ trace-only replay. (5) Falsifier: graph-cache family matches → collapse (this
already happened: Gate1 `graph_cache_collapse`). (6) Toy env: small POMDP with a
non-enumerable, history-dependent latent. (7) Trace/replay: standard action-
conditioned trace. (8) Ceiling: bounded. **Mandatory challengers: graph_lookup,
transition_table, successor_map, count_table, fsm_planner, episodic_traversal.**

**Route 4 — Social inference / user-modeling (H).** Structurally identical to
latent inference. S=partner latent; O=partner behavior; A=response/prediction;
M=partner model; U=partner-posterior update; J|V=interaction return. Simpler
mimic: equal-access partner-model baseline → parity (GATE4-SOCIAL: candidate was
a label-generating tautology, faithful baseline tied at 1.0). Falsifier: parity.
Ceiling: bounded. **High saturation risk; treat as closed-adjacent.**

**Route 5 — Active inference / viability (E).** S=hidden cause; O; A; M=generative
model + preferences; U=variational free-energy / posterior update; J|V=expected
free energy (epistemic+pragmatic). (1) Explains: unified exploration/exploitation
under one objective. (2) Cannot explain: a *falsifiable* advantage — EFE-min is
post-hoc compatible with almost any behavior. (3) Simpler mimic: discounted
control cost / batch least-squares (ACOLB closed exactly here). (4) Ablation:
remove epistemic term → behavior should change measurably or it's decorative. (5)
Falsifier: discounted-control baseline matches. (6) Toy: info-gathering POMDP. (7)
Trace: belief + EFE decomposition per step. (8) Ceiling: bounded. **Contract
note (`joi-demo-north-star`): "free-energy minimization as evidence" is
explicitly excluded as unfalsifiable. Use AIF as an engineering policy, never as
mechanism evidence.**

**Route 6 — Skill library / curriculum / self-verification (C).** S=skill
inventory + task; O; A=compose/learn skill; M=skill library; U=add/verify skill;
J|V=task coverage. Simpler mimic: scripted curriculum + lookup. Self-verification
is an **evaluation harness**, not a subject mechanism — do not let it leak into a
self/agency claim (K7). Ceiling: learning-adaptation at best.

**Route 7 — LLM + memory + reflection/replay (A).** S=conversation/world; O; A=
response; M=episodic+semantic store; U=retrieve/compress/reflect; J|V=task or
preference satisfaction. Simpler mimic: obs-only retrieval / lookup / graph-cache
(your "observation-only memory equivalence"). Reflection currently has **no
standardized benchmark** [FACT, agent-memory survey 2026]. Ceiling: performance-
simulation. **Highest product value, lowest Layer-2 value.**

**Route F (CLOSED) — Self-model as bounded latent.** Co-binding a latent across
predict+report+act is **non-identifiable** for fair independent-heads under equal
access (`GG-COBIND-ID-001A`, K2). Do not draft a new self-boundary gate without a
*new* identifiability construction that answers K1 and K2 on paper first.

---

## PART 3 — RECOMMENDED MINIMAL CLOSED LOOP (formal)

This is the smallest loop that (a) instantiates the one live thread, (b) admits
all mandatory fair baselines, and (c) avoids the closed families. It is a
**candidate-free measurement loop** first; a candidate plugs in only after the
loop's baselines are shown not to saturate.

```
S  (state)        : (regime r_t ∈ R, within-episode latent z_t, env config)
                    R is a NON-enumerable, history-dependent rule family
                    (K-catalog requirement; mod-5 enumerable family is too weak —
                    see Part 5 stop-condition).
O  (observation)  : o_t = obs(S_t) such that z_t is NOT decodable from any single
                    o_t (K1) and NOT recoverable by equal-access single-episode
                    intervention alone (K2). Regime r_t is revealed only through
                    cross-episode regularity.
A  (action)       : a_t ∈ {predict ŷ_t} ∪ {probe actions} ∪ {act-now, hold}
                    (probe + initiative-gate are optional sub-modules per route).
M  (memory/latent): M = (θ : cross-episode amortized prior over R ;
                          b_t : within-episode posterior over (r_t, z_t) ;
                          working buffer ; episodic store ; cooldown timer)
                    Multi-timescale: working ⊂ episodic ⊂ semantic(θ) ⊂ procedural.
U  (update rule)  : within episode: b_{t+1} = f(b_t, a_t, o_{t+1})   (action-cond.)
                    across episodes: θ ← meta_update(θ, episode_trace)
                    initiative: controller(trigger, veto, cooldown) → {act,hold}
J|V (objective)   : J = held-out return on regimes/values UNSEEN in adaptation
                    V = viability: cumulative cost of wrong actions / probe budget
                    (survival-style floor, NOT affect)
∂  (boundary)     : agent CONTROLS A and M (θ, b, buffers, gate).
                    environment CONTROLS regime switches r_t, z_t dynamics, O-noise.
                    Forbidden across ∂: future O during prediction; regime label in
                    O; renderer/private state in replay.
```

The loop is deliberately measurement-first: you run the **fair-baseline panel on
this loop with no candidate** and check whether a fair amortized/meta baseline
already saturates J. Only if it does NOT do you authorize a candidate. This
ordering is the lesson of every prior collapse (build the baseline immunity
before the candidate — `itl-baseline-immunity-admission-standard-001a`).

---

## PART 4 — FIRST THREE MINIMAL TOY EXPERIMENTS

Designed as a portfolio: one **live** thread, one **new** un-closed reframe, one
**definitive closure**. Expected verdicts are stated honestly up front.

- **EXP-1 (live): Cross-episode meta-prior headroom probe.** Does a *fair
  amortized/meta baseline* close the within-episode headroom that TLGP-001A left
  open (0.803)? Candidate-free. CPU-feasible. **Expected verdict [INFER]: likely
  CLOSE** on an enumerable family; the real question is whether headroom survives
  on a non-enumerable family. This is the 2-week card (Part 8).

- **EXP-2 (new): Controlled-initiative control-value.** Does a gated
  trigger/veto/cooldown initiative controller improve downstream viability beyond
  a rate-matched random and a scripted-FSM initiative? **Expected verdict
  [UNKNOWN]: genuinely open** — not in your closed families.

- **EXP-3 (closure): Action-conditioned identifiability with equal-access active
  baseline in panel.** Build a twin-bit non-obs-decodable latent; include an
  equal-access active-interventional baseline. **Expected verdict [INFER]:
  NEGATIVE** (001B-R1 found equal-access active gap = 0.0). Its value is to
  *permanently close* the "single-episode interventional identifiability" route
  with one clean, citable experiment instead of re-litigating it.

---

## PART 5 — PER-EXPERIMENT: BASELINE / ABLATION / GATE / STOP

### EXP-1 — Cross-episode meta-prior headroom probe
- **Strongest fair baseline panel (must all be real `.fit`, matched data+capacity):**
  fair amortized meta-learner (MLP/GRU trained across episodes mapping adaptation
  obs → held-out answer); history-conditioned transformer; in-context learner
  (ORBIT/ECET-style, scaled down); exact amortized Bayes over the family;
  per-episode lookup; majority; oracle upper bound.
- **Ablation:** reset M (θ) between episodes → cross-episode advantage must vanish.
  Shuffle-structure ablation (TLGP-001A style) → headroom must collapse to chance.
- **Acceptance gate (predeclared, balanced metric, two-sided):** "headroom
  survives" iff (best fair meta-baseline balacc) < (ideal − DELTA) AND the gap is
  stable across ≥5 seeds with CI excluding DELTA. Single-sided / accuracy-only
  metrics forbidden (Gate1-replacement lesson).
- **Stop / rollback:** if best fair meta-baseline reaches ideal within DELTA →
  **CLOSE the route**, record baseline-saturation as the verdict, do NOT tune
  thresholds or swap metrics to rescue it. Roll back = leave TLGP-001A/B frozen
  artifacts untouched; the probe writes only to `artifacts/<new-id>/`.
- **Anti-hardcoding:** the meta-baseline is a BASELINE (we *want* it strong); the
  failure mode here is a *weak* baseline faking headroom, so capacity must be
  audited (no one-hot starvation; real fit; K4).

### EXP-2 — Controlled-initiative control-value
- **Strongest fair baseline panel:** rate-matched random initiative; scripted-FSM
  initiative (hand-tuned thresholds); always-on; never-on; post-hoc "good moment"
  classifier (uses full episode → upper bound, must beat candidate or candidate is
  trivial).
- **Ablation:** sever belief→gate coupling (fire at identical rate, independent of
  belief) → viability must fall to rate-matched-random. Remove cooldown → measure
  thrash cost.
- **Acceptance gate:** candidate viability > max(rate-matched-random, scripted-FSM)
  by predeclared margin, ≥5 seeds, CI excluding 0, AND ablation-sensitive (severed
  coupling collapses the gain).
- **Stop / rollback:** rate-matched-random matches → initiative is decorative →
  CLOSE. Post-hoc classifier ties candidate at the same access → no online value →
  downgrade to "offline-only".
- **Anti-hardcoding:** trigger thresholds must be set on a *train* split and frozen
  before test (no threshold tuning after seeing test — explicit contract rule).

### EXP-3 — Action-conditioned identifiability (closure)
- **Strongest fair baseline panel:** obs-only (must fail by construction = positive
  control); **equal-access active-interventional baseline** (the decisive
  challenger — same probe budget as candidate); transition_table; successor_map;
  count_table; fsm_planner; episodic_traversal; oracle.
- **Ablation:** disable probing → candidate must drop to obs-only (proves it uses
  intervention). Disable cross-episode carry → isolates within-episode claim.
- **Acceptance gate:** candidate must beat the **equal-access active baseline**
  (not merely obs-only) by a sample-efficiency margin under a fixed probe-cost
  budget, ≥5 seeds, two-sided.
- **Stop / rollback [expected to trigger]:** equal-access active baseline gap = 0
  → **confirm the ceiling, permanently close single-episode interventional
  identifiability**, file as bounded negative governance evidence.
- **Anti-hardcoding:** latent must be statistically independent of every
  observation/action *name* (K6, MI test not substring); no `predict_all`-as-oracle
  artifact (separation must include precision, not pure recall — Route-C false-
  positive lesson).

---

## PART 6 — WHAT LOCAL ARTIFACTS CONVERT UNKNOWN → FACT

To let me audit a run instead of a narrative, each executed experiment must hand
over machine-readable artifacts under `artifacts/<task_id>/`:

- **`result.json`** with a `claim_ceiling` field and a *computed* (not asserted)
  verdict enum; verdict must be tamper-unique (flipping one input flips the verdict).
- **`trace.jsonl`** per step: `t, belief_before, action, action_conditioned_prior
  /transition, predicted_obs, actual_obs, prediction_error, belief_after`, plus
  for EXP-1 a cross-episode `theta_snapshot`, for EXP-2 `trigger_score, veto,
  cooldown, downstream_return`, for EXP-3 `counterfactual_action_predictions,
  action_contrast_score, probe_cost`.
- **`baseline_comparison.json`** — every panel member's score with fit evidence
  (real `.fit`, capacity, data budget), so a weak/lame challenger (K4) is visible.
- **`ablation_report.json`** — each ablation's effect; the killer ablation must
  destroy the claimed effect or the claim is unsupported.
- **`replay_report.json`** — clean-room replay reconstructs the verdict from
  `trace.jsonl` ALONE, no future obs, no renderer state, no private state.
- **`failure_manifest.json`** if anything fails (preserved, never patched).
- **Provenance:** frozen prereg sha (canonical-json scheme as in TLGP), code sha,
  `executed == delivered` readback. (Note FUSE truncation lesson: author+run in
  `/tmp`, `cp` to mount, verify by sha256 via file API, not bash tail —
  `itl-git-sandbox-constraints`.)
- **Pre-screen:** the experiment's design checked against
  `itl-baseline-immunity-admission-standard-001a` (19 failure families) and the
  K1–K7 killer catalog, with written answers to K1 and K2 (un-answerable ⇒ stop).

Specific handoffs that would most raise the value of my next audit:
1. `src/tlgp_001a/world.py` (frozen) read-only — to reuse the world definition in
   EXP-1 without re-deriving it.
2. `artifacts/TLGP-001B-R2/prereg.json` (sha `6e61a831…`) — to keep EXP-1 disjoint
   from the frozen R2 design and avoid governance self-modification.
3. `joi-demo` 004A property battery — to confirm EXP-2's initiative metric is not a
   re-run of an already-saturated `joi-demo` task.

Until these are in hand, EXP-1/2/3 verdicts remain **[UNKNOWN]** except where the
prior lineage already constrains them (EXP-3 ≈ negative).

---

## PART 7 — WHAT MAY NOT BE CLAIMED (hard list)

No result from any route or experiment here licenses any of:
consciousness · subjective/phenomenal experience · real emotion or feeling ·
self-awareness · real autonomy · agency or will · functional-subject success ·
AGI · companion-readiness · EGO-mainline-readiness · "alive" · stable user benefit ·
correctness of Bio-CMBC / CVPSM / VCCO / CMBC / R/G.

Also forbidden as *evidence*: a green test suite, a passing gate, a demo that
"looks alive", a memory card, a capability score, free-energy minimization, or any
renderer/dialogue-surface behavior. "Buildable" ≠ "passed" ≠ "self/feeling
evidence" (K7). The maximum any single experiment yields is the Part-0 ceiling.

---

## PART 8 — TWO-WEEK BOUNDED TASK CARD (DRAFT — implementation NOT authorized)

```
task_id            : XEP-META-SAT-PROBE-001A
title              : Cross-episode meta-baseline saturation probe (candidate-free)
problem_definition : The one surviving Layer-2 thread is "cross-episode meta-prior
                     beats a fair meta-baseline under held-out shift". TLGP-001A left
                     0.803 headroom but had NO cross-episode meta-learner in its panel
                     (its own caveat #2 names this the most likely collapse point).
                     Before spending the expensive TLGP-001B-R2 GPU candidate run, test
                     CHEAPLY whether a FAIR amortized/meta baseline already closes that
                     headroom. This is a GO/NO-GO de-risking probe, not a candidate.
layer              : engineering-implementation + learning-adaptation (Layer 2/4).
mainline_target    : Decide GO/NO-GO on authorizing the cross-episode meta CANDIDATE
                     (TLGP-001B-R2 family) by measuring fair-meta-baseline saturation.
hypothesis (H1)    : A fair amortized/meta baseline (matched data+capacity), trained
                     ACROSS episodes, does NOT reach (ideal − DELTA) on held-out
                     regimes/values → residual headroom survives → candidate worth
                     authorizing.
null (H0, expected): The fair meta-baseline reaches ideal within DELTA → headroom was
                     an artifact of withholding cross-episode training → the route
                     collapses to "amortized supervised learning of a known family" →
                     CLOSE / downgrade. [INFER: H0 is the more likely outcome.]
invalid enum       : ablation/shuffle fails to collapse, or replay mismatch, or leak
                     detected → INVALID (not H0).
strongest_baseline : fair amortized meta-learner {MLP, GRU} trained across episodes;
                     history-conditioned transformer (small); exact amortized Bayes
                     over the family; per-episode lookup; majority; ORACLE upper bound.
                     All real `.fit`, numeric features (no one-hot starvation, K4).
ablation           : (a) reset meta-state between episodes → cross-episode gain must
                     vanish; (b) shuffle-structure → headroom must collapse to chance
                     (proves headroom is structural, not oracle-privilege).
trace_replay       : per-episode trace (adaptation obs, prediction, held-out answer,
                     meta-state snapshot, per-baseline score); clean-room replay
                     reconstructs the GO/NO-GO verdict from trace alone; prereg sha
                     frozen before any run; executed==delivered sha readback.
acceptance_gate    : GO iff best fair meta-baseline balacc < (ideal − DELTA) with CI
                     excluding DELTA across >=5 seeds, balanced two-sided metric.
                     NO-GO/CLOSE iff best fair meta-baseline >= (ideal − DELTA).
                     DELTA, FLOOR, seed list frozen in prereg BEFORE running.
claim_ceiling      : bounded preflight evidence about whether residual headroom exists
                     for a fair meta-baseline on the specified world. Proves NOTHING
                     about mechanism validity, learning, self, agency, or Joi. A GO only
                     licenses "authorize the candidate run", never "mechanism works".
stop_rollback      : STOP at NO-GO (do not patch). If run on the enumerable mod-5 world
                     and it saturates (likely), the licensed conclusion is ONLY "this
                     enumerable world has no fair-meta headroom" — escalate to designing
                     a NON-enumerable, history-dependent world (K-catalog) before any
                     candidate. Rollback: write ONLY to artifacts/XEP-META-SAT-PROBE-001A/;
                     never modify TLGP-001A/B frozen artifacts; no git push (PAT standing
                     blocker). git HEAD unchanged until operator review.
forbidden_changes  : TLGP-001A/B frozen prereg & artifacts; AGENTS.md/CLAUDE.md;
                     global schema; thresholds after seeing results; LLM integration;
                     EGO mainline; any push.
prior_negatives_cited : TLGP-001A caveat #2; TLGP-001B INVALID (positive-control flaw,
                     prereg 6e61a831); identifiability-ceiling memo; baseline-immunity
                     standard 001A; killer catalog K1/K2/K4.
estimated_cost     : CPU-only, ~2 weeks: wk1 = world reuse + fair meta-baseline panel +
                     prereg freeze; wk2 = >=5-seed run + ablation + clean-room replay +
                     verdict. No GPU. Chunk evaluate() <45s/bash-call (TLGP lesson).
authorization      : DRAFT. Implementation requires explicit operator "implement
                     XEP-META-SAT-PROBE-001A" + a frozen prereg sha. STOP here.
```

**Why this card and not "go build Joi":** it is the lowest-cost falsification of
the single live thread, it is candidate-free (no hardcoding/agency surface), its
most likely outcome is a cheap honest route-closure that saves the expensive GPU
run, and a positive outcome is the *only* thing that would justify re-authorizing
the cross-episode meta candidate. It converts your largest current UNKNOWN ("does
any fair-baseline-immune headroom exist?") into a bounded FACT for one world.

---

## SOURCES (current public anchors, verified 2026-06-29)

- Benchmarking World-Model Learning (AutumnBench / WorldTest), arXiv 2510.19788 — https://arxiv.org/abs/2510.19788
- Scaling In-Context Online Learning via Cross-Episode Meta-RL (ORBIT), arXiv 2602.04089 — https://arxiv.org/abs/2602.04089
- Meta-RL Induces Exploration in Language Agents (LaMer), arXiv 2512.16848 — https://arxiv.org/abs/2512.16848
- AMAGO-2: Breaking the Multi-Task Barrier in Meta-RL with Transformers, arXiv 2411.11188 — https://arxiv.org/pdf/2411.11188
- State of AI Agent Memory 2026 (Mem0 / Zep / LongMemEval) — https://mem0.ai/blog/state-of-ai-agent-memory-2026
- Anatomy of Agentic Memory: Taxonomy and Empirical Analysis, arXiv 2602.19320 — https://arxiv.org/pdf/2602.19320
- Expected Free Energy-based Planning as Variational Inference, arXiv 2504.14898 — https://arxiv.org/abs/2504.14898
- Deep Active Inference with Diffusion Policy + Multiple Timescale World Model, arXiv 2510.23258 — https://arxiv.org/html/2510.23258v1
- CounterScene: Counterfactual Causal Reasoning in Generative World Models, arXiv 2603.21104 — https://arxiv.org/abs/2603.21104
```
