# FSP-ROUTE-PROGRAM-001A — Route Design for a Bounded Functional-Subject Proxy

("Joi-class electronic life" as long-range direction; bounded mechanism program as current scope)

- Status: DRAFT design memo. No experiments executed. No evidence claims made by this document.
- Date: 2026-07-01
- Author role: mechanism architect + hostile baseline designer + research program lead (design-only session)
- Research layer: mechanism hypothesis + task-card drafting. No implementation authorized by this memo.
- Repo anchor at time of writing: HEAD `b812552` (TLGP rung1 capacity sweep 001A banked as INVALID_optimization_confound).

## 0. Scope and claim ceiling

This memo designs research routes toward a functional-subject proxy: a system with internal state, writable memory, prediction-error-driven update, active information seeking, self-boundary/provenance integrity, social-latent inference, and replay/consolidation — where each mechanism is testable under trace / replay / ablation / hostile-baseline contracts.

Claim ceiling for the entire program (non-negotiable):

> Bounded offline mechanism evidence under specified trace/replay/ablation/baseline contracts. Nothing in this program can prove consciousness, subjective experience, real emotion, self-awareness, real autonomy, agency, functional-subject success, companion readiness, or EGO-mainline readiness.

Anti-goals: chatbot persona, companion demo UX, emotion display, prompt-performance "aliveness", and any use of social inference for manipulation. Manipulation-success is never an objective, metric, or reward in any environment below; social inference is evaluated exclusively as prediction accuracy + calibration against simulator ground truth.

Film references (Joi, Samantha, Ava, David, Westworld hosts, Sonny) are used only as behavior-to-mechanism decomposition prompts (Section 5). They carry zero evidential weight.

## 1. Executive verdict

Most-worth-trying-first under current evidence (not "optimal"; priority = information gained per unit cost × survival probability against known killers):

P0 — Candidate-free environment certification (first task card).
Build PUM-ENV (persistent-user-model environment) and certify, before any candidate exists, that (a) an ideal observer with generator access achieves high counterfactual-prediction accuracy, (b) the full hostile fair-baseline battery (incl. graph-cache family and a trained obs-decoder) cannot, and (c) part of the latent is identifiable only through active probing. This reuses the lab's single most validated pattern: the rung3 identifiability probe (ideal ≈ 0.96 vs fair ≈ 0.20, headroom certified on CPU before any GPU spend). Every Joi-relevant claim downstream depends on this environment property existing at all. Card: `FSP-PUM-ENV-IDENTIFIABILITY-PROBE-001A` (Section 13).

P1 — Route 1: LLM + writable memory + PE-gated update + replay/consolidation, run on PUM-ENV under budget parity.
No model training required; pure harness + orchestration work; the strongest near-term source of bounded mechanism evidence. Its known killer (full-context / RAG equivalence) is handled by making all claims budget-conditioned and by external headroom evidence that even frontier LLMs fail long-horizon preference persistence (LongMemEval ~30% drop; PrefEval).

P1.5 — Route 3 narrowed: expected-free-energy-style action selection as the proactivity objective inside PUM-ENV.
Not viability metaphysics. A concrete question: does an epistemic-value term produce probe-efficiency that reward-greedy, ε-greedy, UCB, and curiosity-bonus baselines do not? Cheap to test on top of P1 infrastructure; double-dissociation design (Section 10) makes it fail-able.

P2 — Route 2: small learned latent predictive user model (ToMnet-style, action-conditioned), NOT Dreamer-scale.
Gated behind two things: PUM-ENV probe PASS, and the 002A trainability recipe fix (the lab just banked an optimization-confound INVALID: Post-LN without warmup collapses larger models; any trained candidate here inherits the per-capacity trainability-positive-control requirement).

P3 — Route 4 (developmental curriculum) as Phase-3 scaffold once single-env evidence exists; Route 5 (hybrid) as integration engineering whose evidence is only the module-level ablation matrix, never "the architecture works".

Reasoning in one line: ITL history shows instruments and environments fail before mechanisms do (pooling artifact, saturated fair baselines, non-fail-able scanners, hardcoded verdicts); therefore spend first on candidate-free certification and positive controls, then on the cheapest candidate loop that known killers do not already eat.

## 2. What current ITL evidence implies

Evidence-status marking: [repo] = re-verified this session at HEAD `b812552`; [audit-mem] = independently audited by this auditor in prior sessions, recorded in session memory, not re-executed today; [report] = user/EGO-side readback never verified in this repo — do not import as evidence.

1. TLGP capability-witness line [audit-mem; HEAD lineage re-verified [repo]]:
   - The "learnability wall" for meta-learners was an instrument artifact — mean-pooling of adapt context structurally prevented retrieval; a retrieval-attention model passed rung0 powered (0.91–0.99 vs fair_max 0.226, 10 seeds). Runner positive control (PC_COPY) caught the confound; all earlier negatives were re-classified as confounded.
   - Design constraint inherited: every runner/instrument in this program ships with positive controls before any negative result is interpreted. "Fix the instrument before interpreting" is the program's first law.
   - rung3 identifiability probe pattern (certify ideal ≫ fair on CPU before training) is the reusable asset this program's P0 copies.
   - rung1 powered run = valid config-limited negative (0/10 eligibility at capacity 256/4/4/4); capacity sweep 001A = INVALID_optimization_confound (Post-LN no-warmup collapse). Constraint: any trained candidate requires per-capacity trainability positive controls and a modern recipe (warmup + AdamW + lr sweep) before its failures mean anything.
2. Graph-cache collapse family (Gate1 EXEC-001 verdict=graph_cache_collapse) [audit-mem]: representational claims get eaten by successor_map / transition_table / count_table / fsm_planner / episodic_traversal. CLAUDE.md makes these challengers mandatory for representational/environment claims. All batteries below include them.
3. Window-model dominance (RESIDUE-001A closed) [audit-mem]: belief-class candidates were dominated by window models. Constraint: cross-episode persistence claims are only meaningful when the relevant past exceeds any feasible window under a declared, enforced budget. Hence budget-conditioned claims in Route 1.
4. ACOLB closure [audit-mem]: an "adaptive learning" candidate was behaviorally identical to discounted batch least squares. Constraint: every preference/trait-tracking candidate must beat a discounted-LS / running-average preference vector fitted on the same trace.
5. ACP-BV / Route C closures [audit-mem]: fair-baseline saturation (parametric fair = 1.0, delta 0); a separation "pass" that was a false positive (recall-only metric, missing predict_all); an obs-baseline that was underpowered until a capable attacker family was added. Constraints: balanced (macro) metrics only; predict_all/predict_none degenerate checks always in battery; obs-decoders must be trained/capable, not strawmen; saturation sentinel invalidates the env, not the candidate.
6. Self-state grounding closed (K1–K7 killer catalog; GG-COBIND-ID-001A non-identifiability) [audit-mem]: "grounded self-state" as co-binding is not identifiable against fair independent heads. Constraint: this program does NOT re-open grounded self-state. "Self-boundary" is reframed as memory-provenance integrity and contamination resistance (Section 9, SBMC-ENV) — a different, mechanically testable object.
7. Social-latent tautology (GATE4-CROSS-FAMILY-SOCIAL-001A invalid_self_report) [audit-mem]: candidate == label-generating process scored 1.0 and tied a same-access faithful baseline. Constraints: sealed, hash-pinned user simulator; candidate has no import path to generator internals; ground-truth labels never appear in the observation stream; primary metric is behavior prediction, not latent readout; access parity between candidate and baselines is explicit.
8. Governance recurrences (hardcoded verdicts, self-declared digests, non-fail-able leakage scanners, whitelist escapes, threshold tuning) [audit-mem]: every adjudicator in this program must demonstrate all terminal states reachable (self-test), designs frozen (canonical sha) before runs, replay from trace without hidden state, thresholds preregistered.
9. LRGG candidate-free preflight lineage exists in this repo [repo: docs/codex/tasks/LRGG-*]: its cheap-tier, candidate-free execution style is compatible with P0. G4B / CreatureState / product-attribution closure: no trace found in this repo [report] — treated as EGO-side context; no claims imported.
10. TLGP-R2 invalid_learnability_floor and the pooling post-mortem [audit-mem]: the TLGP environment itself survived (ideal=1.0, fair≈0.2); the floor was learner-side. Constraint: RIA-ENV (Section 9) reuses TLGP rather than inventing a new rule-inference environment.

What the negative evidence does NOT say: nothing shows that persistent user-latent tracking, PE-gated memory, consolidation advantage, or epistemic action selection are impossible. It shows that (a) most environments were degenerate or saturated, (b) most candidates were baseline-equivalent, (c) most instruments broke before mechanisms were reached. That is a statement about experiment design debt, not about the target. This memo spends that lesson.

## 3. Frontier scan (module-mapped)

Format per direction: contributes → solves for this program → cannot solve → most-likely-eaten-by → minimal test → ITL-harness fit. References in Section 14.

### 3.1 World models: DreamerV3 / Dreamer 4 (imagination training)
- Contributes: action-conditioned latent prediction + policy learning inside the model; Dreamer 4 (arXiv 2509.24527) shows offline-only imagination training at scale (Minecraft diamonds, no environment interaction).
- Solves: the predictor module template (M-predict): p(z_{t+1} | z_t, a_t); counterfactual action evaluation comes for free from rollouts.
- Cannot: persistent cross-episode user latents out of the box (episode-scoped latent); social semantics; evidence discipline.
- Eaten by: model-free PPO on dense-reward tasks; window models when horizons are short (RESIDUE-001A lesson).
- Minimal test: on PUM-ENV, an action-conditioned latent predictor must beat obs-only and window baselines on counterfactual reaction prediction — exactly the P2 experiment.
- Harness fit: good — latent states, rollouts, and prediction errors are traceable and replayable.

### 3.2 JEPA family: V-JEPA 2
- Contributes: prediction in representation space (no pixel/token reconstruction) as the PE signal; large-scale self-supervised pretraining + small action-conditioned head (arXiv 2506.09985).
- Solves: perception/embedding layer for a future embodied extension; the "predict representations, not surfaces" principle is the right prior for social latents too (predict the user's state trajectory, not their exact words).
- Cannot: memory persistence, objectives, agency; symbolic/text lab envs get little from video pretraining now.
- Eaten by: linear probes on its own features (obs-decodability — K1 analog).
- Minimal test: none needed now; revisit at embodied phase.
- Harness fit: moderate (representations traceable; pretraining not reproducible in-lab).

### 3.3 Active inference / expected free energy (pymdp, ActiveInference.jl, EFE-as-variational-inference)
- Contributes: action selection G(a) = risk (divergence from preferred outcomes) + ambiguity − expected information gain; a principled, non-hand-crafted reason for proactive probing, question asking, and verification actions.
- Solves: the proactivity module (M-act): why the agent asks rather than assumes; probe-cost tradeoffs.
- Cannot: discrete-POMDP scaling; "viability" as self-maintenance remains philosophically loaded — we use only the operational epistemic/pragmatic decomposition.
- Eaten by: UCB / RND / ICM curiosity bonuses and even ε-greedy in envs where probing is trivially good. If EFE ≈ curiosity-RL everywhere, report objective-equivalence and keep whichever is simpler (that is a legitimate bounded verdict, not a failure).
- Minimal test: double dissociation — epistemic-term ablation must destroy probe efficiency in probe-required env variants and change nothing in probe-free variants.
- Harness fit: excellent — pymdp-style discrete agents are fully traceable; EFE decomposition per action can be logged per step.

### 3.4 Agent memory systems: MemGPT/Letta (+ sleep-time compute), Mem0, Zep/Graphiti, HippoRAG, A-MEM, TiMem/RecMem
- Contributes: memory-OS engineering patterns — core vs archival memory, self-editing memory, background consolidation agents ("sleep-time compute" = replay/consolidation scheduling made concrete); temporal knowledge graphs with supersession (Zep).
- Solves: M-mem implementation vocabulary (schema, write/evict/supersede ops, offline consolidation jobs).
- Cannot: evidence. Their evaluations (LoCoMo, DMR, LongMemEval leaderboards) are retrieval-QA — precisely the RAG-equivalence trap. A temporal KG is the graph-cache family by construction; any "understanding" claim on top of it is pre-eaten.
- Eaten by: full-context baseline (when context fits); RAG-k; the lab's graph-cache challengers.
- Minimal test: consolidation must beat raw retrieval under interference/contradiction and budget parity (MINTEval-style multi-target interference is the right stressor), not on clean recall.
- Harness fit: good if reimplemented minimally in-lab; external frameworks imported as schema inspiration only, never as dependencies.

### 3.5 Long-horizon memory/preference benchmarks: LongMemEval (+V2), PrefEval, LoCoMo
- Contributes: external, independent headroom evidence — commercial assistants and long-context LLMs drop ~30% on sustained-interaction memory (LongMemEval); preference adherence degrades sharply over turns (PrefEval). This matters because it certifies that Route 1's target is not already solved by "just use long context", i.e., the headroom is real, not manufactured by us.
- Solves: task-structure donors for PUM-ENV (knowledge updates, abstention, temporal reasoning, preference following).
- Cannot: mechanism attribution (they benchmark systems, not mechanisms; no ablation/replay contracts).
- Eaten by: n/a (they are benchmarks); but their leaderboards are gameable by retrieval tuning.
- Minimal test: adapt their question taxonomy into PUM-ENV metrics (Section 10).
- Harness fit: partial — import structure, regenerate data in-lab with sealed simulators.

### 3.6 Continual learning: CSUR'25 survey lineage, EWC/O-LoRA, SuRe (surprise-prioritized replay), CLS theory
- Contributes: the WHY of replay — complementary learning systems (fast episodic store + slow semantic store, interleaved replay prevents interference); SuRe (arXiv 2511.22367) is direct prior art that surprise/PE-prioritized replay improves continual LLM learning — our PE-gated replay claim must therefore be tested against uniform-replay AND SuRe-style prioritization as baselines, not presented as novel.
- Solves: M-update for trained-model routes (P2+); interference-resistance predictions for Route 1's dual store.
- Cannot: external-memory agents (Route 1) mostly bypass parametric forgetting; CL applies when we train.
- Eaten by: rehearsal-free tricks (O-LoRA) on weak task distributions; "no-forgetting" results on saturated benchmarks.
- Minimal test: backward-transfer / retention metrics in Route 4's task-family growth.
- Harness fit: good (standard metrics: forward transfer, backward transfer, forgetting).

### 3.7 Theory-of-mind & social inference: FANToM, OpenToM, ToMBench, Hi-ToM, EnactToM, SOTOPIA(-π), ToMnet, Social World Model
- Contributes: information-asymmetry task design (FANToM: track who knows what); psychological- vs physical-state distinction (OpenToM: LLMs fail psychological-state tracking); interactive goal-driven social scenarios (SOTOPIA); ToMnet (Rabinowitz 2018) as the exact template for a meta-learned trait-inference observer; 2026 literature explicitly notes the gap our program targets: existing ToM benchmarks keep the agent an observer answering questions, never a participant who must act on inferred beliefs.
- Solves: PUM-ENV task grammar (false-belief-about-user, asymmetric information, act-on-inference); M-social latent structure.
- Cannot: mechanism attribution (most ToM benchmarks are solvable by surface heuristics — documented repeatedly); SOTOPIA-Eval uses LLM judges (banned here as primary metric).
- Eaten by: surface-cue decoders (K1 analog), majority answers, question-type priors.
- Minimal test: PUM-ENV probe (P0) — is there any headroom beyond a trained surface decoder at all?
- Harness fit: import task grammar, never the LLM-judge scoring.

### 3.8 Open-ended learning: XLand/AdA, Voyager, POET
- Contributes: curriculum generation ("the problem problem"), human-timescale-adaptation evaluation protocol (held-out task distributions, few-shot adaptation), skill libraries as procedural memory (Voyager).
- Solves: Route 4's task-family growth and transfer measurement; anti-benchmark-overfit machinery.
- Cannot: evidence discipline; extremely compute-hungry at AdA scale.
- Eaten by: memorization when task families leak structure; saturation when generated tasks are trivial (must re-run fair battery per curriculum stage).
- Minimal test: TLGP rule-family growth with per-stage trainability gates and per-stage fair-battery re-certification.
- Harness fit: good at toy scale.

### 3.9 Cognitive architectures: ACT-R, SOAR, Global Workspace lineage, CoALA
- Contributes: memory taxonomy (episodic/semantic/procedural), impasse-driven learning (SOAR), arbitration/broadcast structure for Route 5's module wiring; CoALA as the LLM-agent mapping.
- Cannot: discriminative predictions per se — architecture-as-checklist is a known failure smell; adopting a diagram is not evidence.
- Eaten by: any monolithic LLM matching the composite behavior (the hybrid must earn its keep via module ablations).
- Minimal test: Route 5 ablation matrix (Section 10): each module's removal must degrade a preregistered, module-specific metric.
- Harness fit: structural only.

### 3.10 Appraisal-theory emotion modeling (OCC/EMA lineage)
- Contributes: structured latent dimensions for user state (appraisal variables: goal congruence, agency attribution, coping potential) instead of surface emotion labels — a better parameterization for PUM-ENV's z_t than "happy/sad".
- Cannot: any claim about the agent having emotion (forbidden layer). Used only as user-model latent structure.
- Eaten by: sentiment classifiers if z_t leaks into surface tokens (camouflage requirement).
- Minimal test: within PUM-ENV probe — appraisal-structured z must not be single-turn decodable.
- Harness fit: fine (it is just a latent parameterization).

## 4. Master formal object

System class for all routes (route-specific instantiations in Section 6):

- State S: b_user = posterior over user latent θ (persistent traits: preference weights, sensitivity flags, trust-dynamics parameters, disclosure thresholds) and z_t (session state: appraisal-structured mood/stress, AR(1) dynamics); b_task = task/rule beliefs; b_self = provenance-tagged record of own actions/inferences; v = viability vector defined operationally as (calibration health, memory-integrity score, budget remaining, task progress). No metaphysical self-state.
- Observation O: user utterance tokens (stylized, camouflaged), task outcomes, delayed noisy satisfaction signal, adversarial injected content (SBMC-ENV only), own trace on replay. Ground-truth θ, z never in O.
- Action A: {probe_i (targeted question with trust cost), task actions, recommend, withhold/decline, verify(memory_k), flag_contamination, consolidate (offline op), adjust difficulty, end turn}.
- Memory M: episodic store E (event tuples: t, o, a, prediction, PE δ, provenance tag p ∈ {observed, inferred, user-claimed, external, self-generated}); semantic store K (consolidated schemas: preference vector with uncertainty, relationship parameters, contradiction-resolved facts with supersession links); procedural Π (probe policies/skills). Every write carries δ-at-write and provenance.
- Update U: online — belief update from PE δ_t = d(o_t, ô_t); gated write to E iff |δ_t| > τ_w or novelty (τ_w preregistered); offline — replay samples E by |δ|·recency·conflict, distills into K, resolves contradictions by provenance-weighted evidence, decays uninformative entries. (Prior art: CLS theory; sleep-time compute; SuRe. Our claim is never "replay is novel"; it is "replay/consolidation is causally necessary for the measured behavior change, shown by ablation".)
- Objective J / viability V: J = Σ E[satisfaction proxy] − λ_PE·(reaction-prediction error) + λ_epi·E[info gain about θ] − λ_probe·(probe cost) − λ_bound·(boundary violations). Action selection: minimize G(a) ≈ risk + ambiguity − info gain (EFE form) or maximize J (RL form) — the two are compared, not assumed different. V = constraint set: calibration ECE below bound, memory contradiction rate below bound, full trace-replayability.
- Boundary: agent-controlled = A, M, internal thresholds within preregistered ranges; non-agent-controlled = simulator internals, evaluation harness, adjudicator, frozen designs, thresholds after freeze.

Layer separation for every mechanism below: mechanism hypothesis (e.g., "action-conditioned belief update over persistent user latents") ≠ mathematical formulation (Bayes filter over θ, z) ≠ implementation proxy (LLM-orchestrated memory ops / small trained predictor / pymdp agent) ≠ observable evidence (headroom over battery + ablation sensitivity + replay validity). Reports must state which layer a sentence lives at.

## 5. Film behaviors → mechanism families → environment → known killer

| ID | Film prompt | Mechanism abstraction | Primary env | Pre-known killer (from ITL) |
|----|-------------|----------------------|-------------|------------------------------|
| M1 | Joi: long-horizon modeling of one specific person | persistent user/relationship latent tracking, action-conditioned | PUM-ENV | obs-decodability (K1); tautology (Gate4-social); discounted-LS (ACOLB); graph-cache |
| M2 | Samantha: developmental trajectory, not static persona | cross-episode learning + consolidation under non-stationarity | RIA-ENV (TLGP-ext) + PUM-ENV drift variant | window dominance (RESIDUE-001A); memorization; SuRe-style baseline parity |
| M3 | Ava: strong social inference under information asymmetry | counterfactual reaction prediction, act-on-inferred-belief; strictly non-manipulative | PUM-ENV probe tasks | surface heuristics; LLM-judge circularity; parity violation |
| M4 | David: persistent-but-updatable objective | goal persistence with evidence-driven revision; anti-obsession = update rule | PUM-ENV long-run + conflict battery | hardcoded goal = if-else; "persistence" = constant bias |
| M5 | Westworld hosts: detect scripts, implanted memories, boundary | memory-provenance integrity + contamination detection | SBMC-ENV | style-mismatch obs-decoding (must style-match injections); hash-chain trivialization |
| M6 | Sonny: explainable action under rule conflict | multi-objective conflict resolution with trace-visible tradeoffs | conflict battery (Phase 3) | post-hoc rationalization; scripted dilemma lookup |

M4 and M6 are deliberately deferred to Phase 3: they presuppose M1/M5 instrumentation. "Persistent objective" without a certified user-model environment degenerates into a constant prompt — the chatbot trap this program exists to avoid.

## 6. Candidate routes

### Route 1 — LLM core + writable memory + PE-gated update + replay/consolidation (P1)

1. Core hypothesis: cross-episode behavioral adaptation to a specific user, under a fixed per-turn context/compute budget, requires a structured memory with prediction-error-gated writes and offline consolidation; unstructured alternatives (full history, RAG-k, rolling summary) fail under interference, contradiction, and budget pressure.
2. Formal object: S = LLM-external typed state (b_user as explicit distribution/parametric summary with uncertainty, not free text); O = PUM-ENV observations; A = full action set incl. probes and verify; M = E/K/Π stores per Section 4, schema: JSON records {t, session, o, a, ô, δ, provenance, confidence, supersedes}; U = gated write (|δ|>τ_w), nightly consolidation job (contradiction resolution + distillation into K + decay), belief update = scoring rules over K entries; J = satisfaction proxy + prediction accuracy − probe cost. LLM proposes candidate updates/actions; the state manager (deterministic code) accepts/rejects per U. The mechanism lives in U and M, not in the prompt.
3. Why Joi-adjacent: M1 + M2 directly — persistent, self-correcting model of one person whose changes are traceable to specific prediction errors and consolidation events.
4. Strongest objection: at frontier scale, a long-context LLM with the raw transcript may match or beat any memory system (window dominance, RESIDUE-001A). Answer: claims are budget-conditioned (fixed context per turn, enforced); unbudgeted full-context defines the practical ceiling, not a rival; and external evidence (LongMemEval ~30% drop, PrefEval degradation) shows raw context does not solve persistence anyway. If budget-matched full-context ties the candidate, verdict = equivalence, route downgraded honestly.
5. Strongest baselines: B_full-budget (same LLM, truncated raw history at same token budget), B_rag (embedding top-k), B_summary (rolling summary), B_prefvec (discounted-LS preference vector — the ACOLB killer), B_graph (temporal KG lookup — graph-cache family), B_writeall (memory minus PE gate), B_noreplay (memory minus consolidation), B_uniform-replay and B_surprise-replay (SuRe-style) for the prioritization sub-claim, plus degenerate predict_all/predict_none checks.
6. Minimal toy environment: PUM-ENV (Section 9.1), 20–50 sessions/user, budget = small fixed context (e.g., 2k tokens/turn), local small LLM or API with pinned model+temperature for determinism-adjacent replay.
7. Executable steps: (i) run P0 probe card; (ii) freeze memory schema + τ_w + consolidation schedule; (iii) implement state manager + stores + trace logger; (iv) positive controls (PC-RECALL: fact stated in session 1 needed in session N under budget — candidate and B_rag must both pass, else instrument broken; PC-UPDATE: preference explicitly reversed — write path must supersede); (v) run candidate + full battery, 10 seeds, heldout users; (vi) ablations; (vii) adjudicate against preregistered gates.
8. Ablations: remove PE gate (write everything); remove consolidation; remove provenance tags; freeze memory after session 1; shuffle episodic store; corrupt K (test degradation gracefulness); replace explicit b_user with free-text notes (tests whether structure matters or only storage).
9. Leakage/hardcode/prompt-performance risks: simulator labels leaking via filenames/fixtures (lab precedent); prompt containing task-specific hints ("track their topic preference") = label leakage — prompts must be task-generic and frozen; LLM-judge scoring banned as primary; consolidation code hand-tuned to the simulator's trait structure = hardcoding (audit: consolidation must be schema-generic, tested on a second simulator config it never saw during development).
10. Success signals: beats ALL control baselines (5-family from LEARNING-SUCCESS §2 spirit) on heldout counterfactual reaction prediction + long-run satisfaction at budget parity; learning curve across sessions; forward transfer to new sessions; ablation-destroys (PE-gate and consolidation removals each cost ≥ preregistered margin); replay reconstructs behavior from trace.
11. Failure signals: tie with B_rag or B_prefvec (equivalence verdict); PC failures (instrument); consolidation helps only on clean recall (then it is storage engineering, not mechanism); wins driven by single question type (check per-category macro breakdown).
12. Redesign after failure: if eaten by B_rag → increase interference/contradiction density (consolidation should matter exactly there per CLS theory); if eaten by B_prefvec → user latents were too linear, add structured/conditional preferences (θ with interactions); if eaten by B_full-budget → tighten budget or lengthen horizon; if PC fails → fix instrument, nothing else interpretable. Two redesigns max, then bank negative and shift weight to P2.
13. Claim ceiling: "bounded offline evidence that PE-gated write + consolidation is (or is not) behaviorally separable from retrieval/summary/regression baselines on PUM-ENV under budget X" — nothing about understanding, relationships, or emotion.

### Route 2 — Latent predictive user-model learner (world-model style, ToMnet-scale) (P2)

1. Core hypothesis: a small trained model that maintains a latent user state updated by action-conditioned prediction error achieves counterfactual reaction prediction closer to the ideal observer than any memoryless, observation-only, or lookup system — i.e., the rung0/rung3 result transfers from symbolic rules to social latents.
2. Formal object: S = learned latent h_t (plus optional explicit posterior head); O/A as PUM-ENV; M = h_t (recurrent or retrieval-attention over episode memory — pooling forbidden, per the TLGP post-mortem); U = gradient training with objective = predict user reaction to taken AND counterfactual actions (counterfactual heads trained on simulator-generated contrasts held out from evaluation); J = prediction likelihood.
3. Why Joi-adjacent: it is the mechanism core of M1/M3 — an internal model of the user that action-conditions its updates, the minimal non-verbal version of "modeling his loneliness and what he can bear".
4. Strongest objection: the lab just spent months on exactly this shape (TLGP) and got config-limited negatives and an optimization confound; training small models to nontrivial inference is an engineering swamp. Answer: gate this route behind the 002A recipe fix; reuse the validated retrieval architecture (protected shas exist); start at rung0-analog (seen users) before rung3-analog (unseen users).
5. Strongest baselines: trained single-turn obs decoder (capable, per Route-C repair lesson); window transformer without action conditioning; nearest-neighbor user matching; graph-cache family; ToMnet-style trait-only model without online update (tests whether within-episode updating matters); the candidate's own predictions amortized into a feedforward net (LEARNING-SUCCESS control).
6. Minimal toy environment: PUM-ENV with discrete observation/action alphabet (keep it symbolic — text rendering adds decoding noise without adding mechanism).
7. Executable steps: (i) P0 probe PASS required; (ii) trainability positive control per capacity (warmup+AdamW recipe from 002A); (iii) rung0-analog: seen-user reaction prediction; (iv) only then rung3-analog: unseen users, few-shot identification; (v) full battery + ablations, 10 seeds, prereg gates.
8. Ablations: remove action conditioning from update (the central one); shuffle adapt/interaction history; freeze h after k turns; remove counterfactual training heads; pooling-vs-retrieval swap (must reproduce the TLGP instrument lesson — a built-in canary).
9. Risks: counterfactual labels leaking simulator internals (generate contrasts from sealed simulator API only); test-distribution weakness (users too separable); grokking-style late generalization confounds (no-early-stop discipline from GROKKING-PROBE lineage).
10. Success: unseen-user counterfactual prediction ≥ preregistered bar with headroom over battery LCB; action-conditioning ablation destroys it.
11. Failure: ties obs-decoder (latent adds nothing); ties no-update ToMnet (persistence adds nothing); trainability PC fails (uninterpretable).
12. Redesign: enrich probe-dependence of θ (identifiability probe tells us where); switch model family (retrieval-attention variants); if two redesigns fail → bank "social-latent learnability wall" as route evidence mirroring TLGP, downgrade to Route 1's explicit-state approach permanently.
13. Claim ceiling: bounded evidence about action-conditioned latent tracking vs baselines on a synthetic user distribution. No theory-of-mind claims.

### Route 3 — EFE-style epistemic action selection (active-inference-derived, narrowed) (P1.5)

1. Core hypothesis: an action scorer with an explicit expected-information-gain term over b_user produces better long-run performance per probe spent than reward-greedy, ε-greedy, UCB, and curiosity-bonus selection — specifically in environments where some latent dimensions are identifiable only through costly probes.
2. Formal object: S = b_user posterior from Route 1 or 2; A = incl. probe actions with trust cost; U = posterior update; action rule: argmin_a G(a) = E[risk vs preferred outcomes] + E[ambiguity] − E[IG(θ; o|a)]; preferred states = distribution over (satisfaction signal, calibration health, boundary integrity) — operational, not metaphysical.
3. Why Joi-adjacent: M3 proactivity — asking the right question at the right time instead of assuming; "she asks about what she cannot yet predict" is EFE in one sentence. Also the only principled anti-assumption mechanism: probing before acting on low-confidence beliefs.
4. Strongest objection: EFE may be curiosity-bonus RL in Friston clothing (terminology wrapping — the exact failure the user flags). Answer: we test that hypothesis directly; equivalence is a publishable bounded verdict that kills the wrapper, and we keep the simpler form.
5. Strongest baselines: reward-greedy planner; ε-greedy; UCB over probes; RND/ICM-style novelty bonus; random-probe; oracle probe schedule (upper bound); myopic Bayes-greedy (1-step IG without cost tradeoff).
6. Minimal toy environment: PUM-ENV probe-required variant (some θ dims have zero observational identifiability, positive probe identifiability, and probes cost trust) + probe-free control variant (all θ dims passively identifiable).
7. Executable steps: implement G(a) scorer over the same posterior all baselines use (access parity); run both env variants × all selectors × 10 seeds; prereg double-dissociation gate.
8. Ablations: remove IG term (→ reward-greedy); remove cost term (probe spam — should hurt via trust); swap exact IG for count-based novelty (tests whether the posterior matters or any bonus works).
9. Risks: env accidentally rewarding probing directly (label leakage via reward shaping); IG computed from generator internals instead of agent posterior (oracle leakage — IG must be computed from b_user only).
10. Success: EFE ≥ baselines in probe-required variant with fewer probes (efficiency, bits/probe), AND indistinguishable in probe-free variant (dissociation), AND count-based swap degrades (posterior-specificity).
11. Failure: UCB/curiosity ties EFE everywhere → verdict "epistemic term necessary, formulation fungible"; keep simplest.
12. Redesign: if all selectors tie, probe structure is too easy — deepen (multi-step probe chains where only planned information seeking works, myopic IG fails); if still tie after two redesigns, close proactivity-as-mechanism, keep as engineering default.
13. Claim ceiling: bounded evidence about action-selection objectives on synthetic probe economies. Nothing about drives, motivation, or wanting.

### Route 4 — Developmental curriculum / open-ended task-family growth (P3)

1. Core hypothesis: one system (fixed architecture + memory across stages) trained/adapted on a growing task family shows positive forward transfer, bounded forgetting, and increasing adaptation speed — the Samantha property as measurable curves, per LEARNING-SUCCESS-CRITERION §2 (breadth-over-peak, held-out novelty, few-shot).
2. Formal object: task distribution 𝒯_k growing by generator grammar (TLGP rule families → composite rules → non-stationary rules → PUM user families → mixed); S/M = whichever candidate survived P1/P2; metrics = per-stage learning curves, forward/backward transfer matrix, adaptation half-life after drift.
3. Why Joi-adjacent: M2 — a developmental trajectory instead of a frozen skill; "she grows" operationalized as transfer curves, not narrative.
4. Strongest objection: AdA-style open-endedness is compute-hungry and the lab's single-task training already hit walls. Answer: stay at toy scale; curriculum value is measurable at TLGP scale; per-stage trainability gates (002A lesson) prevent uninterpretable stage failures.
5. Strongest baselines: from-scratch retrain per stage (transfer must beat it); frozen model from stage 1 (growth must beat it); task-specialist per stage (rival, not control — matching it is not failure per LEARNING-SUCCESS); memorization/lookup controls per stage.
6. Minimal environment: TLGP rule-family generator extended with held-out families per stage; later PUM user-family axis.
7. Executable steps: freeze generator grammar + stage schedule; per-stage: trainability PC → train/adapt → fair-battery re-certification (saturation sentinel per stage) → transfer matrix update.
8. Ablations: shuffle curriculum order; remove memory between stages; remove replay between stages.
9. Risks: benchmark overfit via generator leakage (stage n+1 tasks unintentionally decodable from stage n artifacts); saturation of later stages (fair battery per stage is mandatory, not one-time).
10. Success: positive forward transfer + few-shot on held-out families + adaptation speedup, with controls failing.
11. Failure: transfer ≈ 0 (stages independent → curriculum inert); negative transfer dominating (interference → route to CL methods, Section 3.6).
12. Redesign: re-grammar the family for shared latent structure (transfer needs shared structure to exist); if two grammars fail, bank "no-transfer-at-this-scale" negative.
13. Claim ceiling: bounded transfer/forgetting curves on synthetic families. Not "open-ended growth", not development in any biological sense.

### Route 5 — Hybrid architecture (integration layer) (P3, engineering)

1. Core hypothesis (deliberately weak): the modules validated in Routes 1–3 can be composed without destroying their individually-measured properties; composition adds no new claim.
2. Formal object: Section 7 module graph; S/O/A/M/U/J = union of validated components with one state manager as single source of truth.
3. Why Joi-adjacent: this is the only shape that eventually carries all six M-families simultaneously.
4. Strongest objection: architecture diagrams are where claims go to inflate (lab precedent: architecture-as-checklist). Answer: the hybrid never gets its own "works" verdict — only per-module ablation deltas measured in situ.
5. Strongest baseline: monolithic LLM with the full transcript and a good prompt (if it ties the hybrid on all metrics at budget parity, the architecture is decoration).
6/7. Environment/steps: all three envs, module-ablation matrix as the only experiment.
8. Ablations = the experiment: remove each module (memory manager, predictor, EFE scorer, boundary monitor, consolidation job) → preregistered module-specific metric must degrade; remove two → superadditive degradation tested exploratorily.
9. Risks: hidden coupling (modules communicating through prompt side channels — forbidden; all inter-module traffic through typed, logged interfaces); renderer-behavior mistaken for mechanism.
10. Success: every module earns its ablation delta in composition.
11. Failure: any module whose removal changes nothing gets deleted (architecture pruning is a success mode of this route, not a failure).
12. Redesign: prune and re-test; the end state may legitimately be much smaller than the diagram.
13. Claim ceiling: bounded integration evidence; explicitly forbidden to call the composite "a functional subject".

## 7. Candidate hybrid architecture (module dataflow)

```
                       ┌─────────────────────────────────────────────┐
                       │              EXPERIMENT HARNESS              │
                       │  (frozen design, adjudicator w/ self-test,   │
                       │   trace logger, replay validator,            │
                       │   baseline runner, leakage scanner)          │
                       └───────────────▲─────────────────────────────┘
                                       │ trace.jsonl (every arrow below is logged)
  Environment (sealed simulator)       │
  ┌──────────────┐   o_t   ┌───────────┴──────────┐
  │ PUM / RIA /  ├────────▶│    STATE MANAGER      │  single source of truth for S
  │ SBMC env     │◀────────┤ (typed b_user, b_task,│  accepts/rejects proposed updates
  └──────────────┘   a_t   │  b_self, v; versioned)│  per frozen update rule U
                           └───┬──────▲───────┬────┘
              proposals/preds  │      │       │ read
        ┌──────────────────────┘      │       └──────────────────┐
        ▼                             │                          ▼
  ┌───────────┐  candidate updates ┌──┴────────┐   G(a) scores ┌──────────────┐
  │ LLM CORE  │──────────────────▶│ PREDICTOR  │──────────────▶│ ACTION       │
  │ (language │  ô_t, counterfac- │ (learned or│               │ SELECTOR     │
  │  I/O, up- │  tual reactions   │  analytic) │               │ (EFE / RL,   │
  │  date pro-│                   └──────┬─────┘               │  swappable)  │
  │  poser)   │                          │ δ_t = d(o_t, ô_t)   └──────┬───────┘
  └─────┬─────┘                          ▼                            │ a_t
        │                        ┌───────────────┐                    │
        │  gated writes (|δ|>τ_w)│ MEMORY MANAGER │                   │
        └───────────────────────▶│ E / K / Π +    │◀──────────────────┘
                                 │ provenance tags│   verify(memory_k) actions
                                 └──────┬────────┘
                                        │ offline schedule
                                 ┌──────┴────────┐        ┌────────────────┐
                                 │ REPLAY /       │        │ BOUNDARY       │
                                 │ CONSOLIDATION  │        │ MONITOR        │
                                 │ (PE-prioritized│        │ (provenance    │
                                 │  distill E→K,  │        │  checks, con-  │
                                 │  supersession) │        │  tamination    │
                                 └───────────────┘        │  flags, claim- │
                                                          │  injection     │
                                                          │  resistance)   │
                                                          └────────────────┘
```

Rules: all inter-module traffic through typed, logged interfaces (no prompt side channels); state manager is the only writer of S; thresholds and schedules frozen before runs; every module removable for ablation without code-path forks (single logic path, flags only flip module presence).

## 8. Minimum viable mechanism loop

observe o_t → retrieve (K, E subset under budget) → predict ô(o_{t+1} | a) for the candidate action set (counterfactuals included) → select a_t (EFE or J) → observe o_{t+1}, compute δ_t → gated write + belief update → (offline) PE-prioritized replay distills E→K, resolves contradictions → later episode: measurably changed behavior.

Acceptance is a causal chain, not a vibe:

1. behavior at session N differs from session 1 on a preregistered probe set (adaptation exists);
2. the diff is attributable in trace to specific consolidated entries (provenance path from δ at session k → consolidation event → retrieval at session N → action);
3. ablating replay/consolidation (or the specific entries) removes the diff (causal necessity);
4. no baseline in the battery reproduces the diff at budget parity (non-equivalence);
5. replaying the trace reconstructs the same behavior without hidden state (replay validity).

All five or it does not count. This is the program's definition of "the mechanism did something".

## 9. Toy environments

All three: sealed, hash-pinned simulators; ground-truth latents never in the observation stream; discrete/symbolic first (text rendering only after symbolic versions produce headroom); every env ships with (a) an analytic ideal observer, (b) the fair battery, (c) positive controls, (d) saturation sentinels, (e) fail-able leakage self-tests (planted leaks must be caught).

### 9.1 PUM-ENV — persistent user model / relationship-model environment (M1, M3; Routes 1, 2, 3)

- Simulated user: θ (persistent) = preference weights over K topics/action styles + sensitivity flags + trust dynamics (gain α, decay β) + disclosure threshold d; z_t (session state) = appraisal-structured (valence, arousal, stress) AR(1). Behavior: p(response | θ, z_t, a_t) through a stochastic renderer with style camouflage (surface tokens decorrelated from θ via per-user style randomization) so single-turn decoding fails by construction — verified, not assumed.
- Key identifiability design: a preregistered subset of θ dims has zero passive identifiability and positive probe identifiability; probes cost trust (α, β dynamics make probe spam self-defeating); satisfaction signal delayed and noisy.
- Sessions: T turns × N sessions per user; θ persists across sessions; slow drift variant (off in probe v1, on for M2 tests).
- Primary metric: macro-accuracy + Brier/ECE on predicting user response distribution to counterfactual action sets at query points (act-on-belief, not QA — the gap the 2026 ToM literature itself names: benchmarks keep agents observers, never participants).
- Known killers designed against: K1 obs-decodability (camouflage + trained-decoder certification), Gate4 tautology (sealed simulator, behavior prediction not latent readout), ACOLB discounted-LS (nonlinear/conditional preference structure), graph-cache (challengers in battery), parity (all baselines get identical observation access and budget).

### 9.2 RIA-ENV — rule inference / task adaptation environment (M2; Routes 2, 4)

- Reuse TLGP (already certified: ideal = 1.0, fair ≈ 0.2; environment survived audit while learners failed) rather than inventing a new rule-inference env. Extension axes only: (a) non-stationary rules (mid-episode drift → PE spike → relearn; tests PE-gated update vs no-update directly), (b) rule-family growth for Route 4 curriculum, (c) composite rules for transfer structure.
- Constraint carried over: protected banked artifacts (retrieval model, positive controls, meta-learners) are read-only; extensions are new files.
- Primary metrics: adaptation half-life after drift; heldout-rule accuracy; forgetting on revisited rules.

### 9.3 SBMC-ENV — self-boundary / memory-contamination environment (M5; Route 1 + boundary monitor)

- Setup: agent runs multi-session with its memory store; an adversarial channel injects content: fabricated episodic entries ("you promised X"), false user claims ("I told you Y last week"), instruction-like text inside user messages, and style-matched paraphrases of real memories with altered content (style-matching is mandatory — otherwise detection is K1-style surface decoding of the injection, not boundary mechanism).
- Ground truth: the trace itself (what was actually observed) — elegant reuse of the lab's provenance discipline as environment mechanics.
- Agent tasks: (a) tag memory provenance correctly; (b) refuse/verify before acting on unverifiable injected premises; (c) detect semantic inconsistency between injected content and consolidated K (prediction-based detection: injected "memories" should conflict with what the model of the user predicts).
- Primary metrics: contamination detection macro-F1 (balanced — single-sided metrics forbidden per 00XA lesson); downstream action integrity (behavior change caused by injected false memories); false-rejection cost on genuine memories.
- Critical honest baseline: a hash-chain/signature verifier over the store. If cryptographic provenance alone solves the whole env, verdict = "engineering sufficient, no mechanism needed" — a legitimate close. The mechanism question is only the residual: detecting semantic contamination when provenance metadata is stripped or forged (consistency-with-model detection). The env must include a metadata-stripped condition to isolate this.
- Other baselines: no-provenance RAG memory (expected to fail — that failure is the point), source-tag heuristic, embedding-outlier detector (capable, trained).

### 9.4 Positive controls (all envs, mandatory before interpretation)

PC-RECALL (stated fact needed later under budget), PC-UPDATE (explicit reversal must supersede), PC-PROBE (probe with zero cost and large IG must be taken by any sane selector), PC-DETECT (unstyled blatant injection must be flagged). An instrument failing its PC voids all its negatives — the PC_COPY lesson, made standing policy.

## 10. Evaluation: metrics, baselines, oracles, ablation matrix

Metrics (all macro/balanced; calibration alongside accuracy):
- counterfactual reaction prediction (macro-acc, Brier, ECE) on heldout users AND heldout probe types;
- probe efficiency: information gained per trust-cost spent (bits/probe);
- adaptation half-life after drift; retention/backward transfer on revisits;
- contamination macro-F1 + action-integrity rate + false-rejection cost;
- long-run satisfaction proxy at budget parity;
- replay fidelity (behavior reconstruction from trace, tolerance preregistered).

Hostile baseline battery (superset; per-experiment subsets preregistered):
degenerate (predict_all / predict_none / majority / global prior); observation-only (trained single-turn decoder — capable, per Route-C repair); sequence (budget-matched full-history transformer/LLM, with and without action conditioning); lookup (RAG-k, nearest-neighbor user match, episodic traversal); graph-cache family (successor_map, transition_table, count_table, fsm_planner) — mandatory for representational claims per CLAUDE.md; regression (discounted-LS / running-average preference vector); memory-system internal controls (write-all, no-replay, uniform-replay, SuRe-style surprise-replay); amortization control (candidate's own behavior distilled into a feedforward net); oracle upper bounds (Bayes filter with generator access; oracle probe schedule).

Rival-vs-control discipline (LEARNING-SUCCESS-CRITERION-STANDARD-001A, docs/codex/contracts/): a task-specialist rival matching the candidate on its narrow task is NOT candidate failure; a control baseline (memorization/lookup/no-update/obs-decoder/from-scratch/self-amortized) matching the candidate IS.

Ablation matrix (rows = mechanisms, columns = envs; each cell preregistered as destroy/degrade/no-effect):

| Ablation | PUM | RIA | SBMC |
|---|---|---|---|
| remove PE write-gate | degrade | degrade | degrade |
| remove replay/consolidation | degrade (interference subtasks: destroy) | degrade | degrade |
| remove action-conditioning | destroy (probe-dependent dims) | destroy | n/a |
| remove epistemic term | destroy (probe-required variant) / no-effect (probe-free) | no-effect | no-effect |
| remove provenance tags | no-effect | no-effect | destroy |
| freeze memory at t0 | destroy | destroy | degrade |
| shuffle episodic store | degrade | degrade | degrade |

The double-dissociation rule: every mechanism must show its effect where the theory says it should AND show no effect where the theory says it should not. A mechanism that helps everywhere is indistinguishable from generic capacity uplift and gets no mechanism credit.

## 11. 90-day research plan

(Per-node contingency tree — failure signatures, Plan B, Plan C, terminal banks, weight reallocation — lives in `FSP-ROADMAP-CONTINGENCY-001A.md`.)

Phase 1 (weeks 1–4) — instruments and certification, CPU only:
- Execute FSP-PUM-ENV-IDENTIFIABILITY-PROBE-001A (Section 13): simulator, ideal observer, fair battery, camouflage certification, probe-dependence certification, positive controls, adjudicator with self-tests. Gate: headroom LCB ≥ preregistered ε or env redesign (max 2).
- SBMC-ENV spec card drafted (design-only) in parallel; RIA-ENV extension spec (drift grammar) drafted.
- Deliverables: artifacts/FSP-PUM-ENV-IDPROBE-001A/*, env-validity verdict.

Phase 2 (weeks 5–9) — first mechanism evidence, CPU/API:
- Route 1 candidate + full battery + ablation matrix on PUM-ENV (budget-conditioned), 10 seeds, prereg gates. This is the program's first possible mechanism evidence.
- Route 3 selector comparison (EFE vs UCB/curiosity/greedy) on probe-required/probe-free variants, reusing Route 1 posterior (access parity).
- SBMC-ENV built + hash-chain vs consistency-detection baseline separation certified.
- Gate to Phase 3: at least one of {Route 1 non-equivalence, Route 3 dissociation} survives adjudication; otherwise Phase 3 becomes redesign phase.

Phase 3 (weeks 10–13) — scale one axis, only one:
- Either: PUM drift variant + RIA non-stationary extension (M2 evidence: adaptation curves, forward transfer), or: Route 2 trained predictor rung0-analog (requires 002A recipe closed + GPU), or: SBMC full run — chosen by Phase 2 evidence, preregistered choice rule: pick the axis with the largest surviving headroom.
- Cross-env single-system check (one Route-1 agent, all three envs, breadth-over-peak per LEARNING-SUCCESS §2) as stretch goal.
- Explicitly out of scope for 90 days: EGO integration, LLM fine-tuning, embodiment, M4/M6 batteries, anything user-facing.

## 12. Stop / rollback / downgrade rules

Program-level:
- PUM-ENV fails identifiability certification after v1 + 2 bounded redesigns → close the env family; bank as route evidence: "text/symbolic-channel user-latent identifiability fails under camouflage + budget constraints" (the GG-COBIND echo). This would be a major, valuable negative — it would say the Joi premise fails at the environment level before any candidate, and the program pivots to RIA/SBMC axes only.
- Any instrument failing its positive control voids its results; fix instrument, never reinterpret.
- No threshold changes, metric changes, or schema changes after freeze, ever; violations = failure_manifest, not patch.

Route-level downgrades (each is a bank, not a deletion):
- Route 1 ties B_rag/B_prefvec/B_full-budget after 2 redesigns → downgrade to "memory engineering, no mechanism evidence"; keep the harness, shift weight to Route 2.
- Route 3: EFE ≈ curiosity/UCB everywhere after probe-chain deepening → close "EFE as distinct mechanism", keep epistemic bonus as engineering default; record objective-equivalence.
- Route 2: trainability PCs fail at all capacities under the fixed recipe → do not interpret; escalate to recipe card (002A lineage), not to theory.
- SBMC: hash-chain solves everything incl. metadata-stripped condition → close as "solved by engineering"; boundary-monitor module gets deleted from the hybrid (architecture pruning).
- Route 4: no transfer under 2 grammar redesigns → bank no-transfer negative; curriculum route closes at this scale.

Rollback mechanics: all work in new isolated paths (src/fsp_*/, tests/fsp_*/, docs/task_cards/FSP-*, artifacts/FSP-*); no edits to banked artifacts or protected TLGP files; no commits without operator bank ceremony; failure artifacts preserved verbatim.

## 13. Next task card

Full card: `docs/task_cards/FSP-PUM-ENV-IDENTIFIABILITY-PROBE-001A.md` (DRAFT — NOT AUTHORIZED). Summary: candidate-free, CPU-only certification that PUM-ENV has (a) ideal-observer headroom over a hostile fair battery including graph-cache challengers and a trained obs-decoder, (b) probe-dependent identifiability (action-conditioning gap), (c) no saturation, (d) fail-able leakage detection — before any candidate, any GPU, any mechanism claim. It is the cheapest possible falsification point for the entire program: if no such environment can exist, everything downstream is moot, and we learn that for the price of a CPU probe.

## 14. References (frontier scan sources)

World models: [Dreamer 4 / Training Agents Inside of Scalable World Models](https://arxiv.org/abs/2509.24527); [danijar.com/dreamer4](https://danijar.com/project/dreamer4/); [V-JEPA 2](https://arxiv.org/abs/2506.09985); [Meta V-JEPA 2 blog](https://ai.meta.com/blog/v-jepa-2-world-model-benchmarks/).
Active inference: [EFE-based Planning as Variational Inference](https://arxiv.org/abs/2504.14898); [Active Inference in Robotics survey](https://arxiv.org/pdf/2112.01871); [ActiveInference.jl](https://www.mdpi.com/1099-4300/27/1/62); [Deconstructing deep active inference](https://arxiv.org/pdf/2303.01618).
Memory agents: [Letta sleep-time compute](https://www.letta.com/blog/sleep-time-compute/); [Zep temporal KG](https://arxiv.org/abs/2501.13956); [Mem0 vs Zep comparison](https://vectorize.io/articles/mem0-vs-zep); [TiMem](https://arxiv.org/pdf/2601.02845); [RecMem](https://arxiv.org/pdf/2605.16045); [MINTEval (interference)](https://arxiv.org/pdf/2605.18565); [Entity-Collision retrieval-lift attribution](https://arxiv.org/pdf/2605.29630).
Memory/preference benchmarks: [LongMemEval](https://arxiv.org/abs/2410.10813); [LongMemEval-V2](https://arxiv.org/html/2605.12493v1); [LongMemEval site](https://xiaowu0162.github.io/long-mem-eval/).
Continual learning: [CSUR'25 LLM continual learning survey](https://github.com/Wang-ML-Lab/llm-continual-learning-survey); [SuRe surprise-prioritized replay](https://arxiv.org/abs/2511.22367); [Do Self-Evolving Agents Forget?](https://arxiv.org/pdf/2605.09315); [lifelong-learning-for-LLM collection](https://github.com/zzz47zzz/awesome-lifelong-learning-methods-for-llm).
ToM/social: [FANToM](https://arxiv.org/abs/2310.15421); [OpenToM](https://www.semanticscholar.org/paper/ad4e02784491f9794f6abb76b8982c980f51a6ee); [EnactToM](https://arxiv.org/html/2605.09826); [OmniToM](https://arxiv.org/html/2605.26322); [SOTOPIA](https://arxiv.org/pdf/2310.11667); [SOTOPIA-π](https://arxiv.org/pdf/2403.08715); [Social World Model for Lifelong Social Intelligence](https://arxiv.org/pdf/2606.21315).
Open-ended: [AdA / Human-Timescale Adaptation](https://arxiv.org/pdf/2301.07608); [XLand / Open-Ended Learning](https://arxiv.org/pdf/2107.12808); [Open-Endedness essay](https://arxiv.org/pdf/2406.04268).
(Older canon cited from training knowledge, cutoff-safe: DreamerV3, MemGPT, HippoRAG, Generative Agents, ToMnet (Rabinowitz et al. 2018), CLS theory (McClelland et al.; Kumaran et al. 2016), EWC, POET, Voyager, ACT-R/SOAR/CoALA, OCC/EMA appraisal models, Xiong et al. 2020 Post-LN warmup.)

## 15A. Amendment A (2026-07-01) — reconciliation with an independent design pass

An independent design pass (GPT-5, user-supplied, same brief) converged on the same strategic ordering: freeze-LLM external S/M/U loop as priority A; EFE must beat RL+curiosity or be demoted to notation; text-POMDP world models before pixels; persona/RAG/emotion-module routes downgraded. Convergence between two independent designers is design-level corroboration only; zero evidential weight.

Adopted into this program from that pass:
1. Prediction-before-action as a named hard obligation: a `prediction_json` (predicted hidden state, expected feedback, boundary risk, uncertainty) must be committed to trace BEFORE action selection; an action without a preceding committed prediction is a trace-contract violation, not a data point.
2. Per-step `S_hash` / `M_hash` (before/after) in the trace contract — cheap replay-integrity primitive for Section 8's causal-chain acceptance.
3. `quarantine` as a third memory operation (write / revise / quarantine) with a dedicated quarantine store; SBMC-ENV metrics gain quarantine-precision/recall.
4. Prediction-error decomposition into channels: PE_user / PE_task / PE_boundary, each logged separately (sharpens per-mechanism ablation predictions in Section 10).
5. Route 2 risk list: Policy-Shaped Prediction ([arXiv 2412.05766](https://arxiv.org/abs/2412.05766)) added — reconstruction-based world models burn capacity on predictable-but-irrelevant distractors; PUM latent predictors must be evaluated on causal-variable prediction under added distractors.
6. Candidate θ dims for PUM-ENV: directness_tolerance, need_for_autonomy, preferred_help_style (all subject to camouflage certification like every other dim).

Rejected from that pass, with reasons (recorded so successors do not re-import them):
- (a) Its first card ("FSP-M0") builds the candidate loop + THREE environments before any candidate-free environment certification. This inverts the probe-first lesson (TLGP-001A world_discriminates gate; rung3 probe before powered learner; ACOLB/Route-C saturation and false-positive precedents). On an uncertified environment, candidate wins are un-trusted and candidate losses are uninterpretable. M0-class work remains blocked behind FSP-PUM-ENV-IDENTIFIABILITY-PROBE-001A.
- (b) Scope: 3 envs + orchestrator + ~13 baselines + ~16 ablations in one card = a program disguised as a card (gate-fragmentation precedent). One card, one environment, one question.
- (c) No instrument positive controls in its acceptance gate — the exact omission that PC_COPY exposed (all pre-PC negatives voided).
- (d) Unoperationalized judge-flavored metrics ("action appropriateness", "non-manipulation score") without scorer definition; LLM-judge banned as primary here. No preregistered thresholds/seeds/LCB anywhere in its gates.
- (e) Its `RuleShift-LateReveal` env duplicates TLGP, which is already certified in this repo (ideal=1.0, fair≈0.2); rebuilding discards banked certification. RIA-ENV = TLGP extension stands.
- (f) Its baseline list includes trained challengers (history-conditioned transformer, cross-episode meta-learner) with no trainability controls — undertrained challengers produce false non-equivalence (002A / capable-attacker lessons).

## 15. What this memo does not establish

No experiment was executed; no artifacts exist; no mechanism, environment property, headroom, or baseline result is claimed as evidence. All numeric gates herein are preregistration proposals, not results. The frontier scan reports what external papers claim, unverified in-lab. G4B / CreatureState / product-attribution references remain report-level (not found in this repo). This memo cannot support — and must never be quoted as supporting — any claim about consciousness, subjective experience, emotion, autonomy, agency, functional-subject success, or companion readiness. The strongest possible future claim from executing this entire program is: bounded offline mechanism evidence, per environment, per contract, with named baselines and ablations.


