# FACG-TUPLE-001A - Submitted fork-A separation-claim tuple (audited object)

Object under test for gate **FACG-001A-R3** (gate_spec @ commit 671d552b25c1e9ab85b8a1bffaf91f32c3773af0).
Claimant: operator. Auditor: Claude (independent hostile audit; roles separated).
This file is the frozen audited object. The verdict in audit_report.md / verdict.json is replayable against this specification.

## Claimant-stated claim ceiling
Seeks at most: bounded mechanism-family / capability evidence for generated-access boundary-maintenance.
Does NOT claim functional subject, consciousness, electronic life, autonomy, agency, or EGO readiness.
Claimant's own expected verdict prior: MECHANISM_FAMILY_REPLICATION / CAPABILITY_NOT_SUBJECT. True SURVIVES_HOSTILE_CLOSURE prior: low.

## G - generative / agent-coupled process
Embodied perturbation-repair world with generated access. An embodied agent is coupled to a mutable sensorimotor interface.
- body variables: sensors, actuators, energy/viability variables, controllable interface nodes
- world variables: obstacles, tools, damaging perturbations, repair resources, movable shields / membranes
- agent actions: move, probe, manipulate object, repair channel, reinforce boundary, allocate energy, retreat, explore
- perturbations: stochastic damage to sensors/actuators/boundary channels; distribution depends partly on the agent's generated niche / exposed boundary / past repairs

The agent's trajectory changes future access (expose, protect, damage, repair, extend future observation-action channels). Score is over DISTRIBUTIONS of self-generated trajectories under shared initial laws/seeds, not a fixed task list. Claimant concedes the world is reproducible as a simulator, so K-A1a likely fires (an ideal reference object is definable), which caps the claim.

## M - candidate mechanism
Online boundary-maintenance with an action-conditioned controllability graph.
- S: latent estimate of body/world/interface variables; controllability graph G_c; viability state v_t; damage/repair state; memory of perturbation-repair episodes
- O: local sensor readings; proprioceptive/actuator feedback; energy/viability signals; post-action channel response
- A: probe; repair; reinforce; move; manipulate; exploit; rest/conserve
- memory: cross-episode memory of boundary failures, repairs, affordances, tool-use traces
- U (contested online mechanism): online update of action-conditioned controllability graph P(variable responds | intervention, context) + viability-weighted policy update (choose interventions that preserve/repair/expand future sensorimotor access)

Intuition: maintain an operational self/non-self boundary NOT by reporting a label, but by continuously estimating controllable channels, damage, repairs restoring access, and threats to viability. No true self label is used.

## C - success criterion (non-oracle)
Passes only if, under equal R and shared law, M beats the full fair family on ALL of:
- C1 viability maintenance (viability variables above threshold across generated trajectories)
- C2 boundary repair (recover functional control within bounded cost after unannounced perturbations)
- C3 future-access preservation (maintain/expand reachable observation-action channels over time, not merely immediate reward)
- C4 generated-curriculum robustness (holds over distributions of self-generated trajectories, with difficulty/novelty/coverage diagnostics)
- C5 U-necessity (disabling the contested U destroys the advantage)

Scoring inputs ONLY: observable viability; observable channel function; agent actions; perturbation events; repair outcomes; trajectory distributions; resource use.
Forbidden scoring: true self/non-self label; true hidden causal graph; human "this is alive"; subjectivity label; internal report similarity.
Claimant-listed collapse paths: reduce to predicting which variables respond to own interventions -> interventional predictor / CDAP Row 2; true boundary label -> ORACLE_SCORED; just better reward/sample-efficiency -> CAPABILITY_NOT_SUBJECT; scored trace reports -> TRACE_MIMIC_COLLAPSE.

## B - fork-A baseline family (instantiated under R)
All baselines get the same initial resources, embodiment interface, environment law, seed distribution, intervention budget, memory/compute budget, horizon, viability objective. Each generates its OWN access path; none replays M's realized trajectory.
- B1 resource-matched meta-learner (RL2 / transformer policy across the same simulator family and budget; ideal Bayes-meta = K-A1a reference only, not a domination baseline)
- B2 POET / self-play population (agents + environment perturbation curricula, fixed shared laws)
- B3 history-conditioned transformer + persistent cross-episode memory
- B4 world-model + curriculum planner (learned transition model + active repair/planning search)
- B5 graph/cache/replay (episodic graph of states, channels, repairs, tools, damage contexts; strong representational challenger)
- B6 multi-agent co-adaptation population
- B7 U-disabled control (same architecture family, controllability-graph update disabled or offline-compiled)
- B8 resource-bounded MDL/compression controller (specified representation class, update rule, controller interface, compute/memory budget)
- B9 no-regret / adaptive-control baseline (specified comparator class, feedback model, horizon, memory, regret criterion)

## R - resource / access contract
Equal compute (training steps / wall-clock / model size), equal persistent memory; same seed distribution / environment laws / perturbation generator; no baseline receives M's realized trajectory as replay data (unless testing path-following robustness); fixed evaluation horizon H_eval with predeclared stop conditions and multiple independent generated-trajectory samples; same sensors/actuators/repair actions/energy constraints/perturbation interface; same intervention budget; **viability/future-access objective J|V fixed before results and independent of M's realized path**; distribution-level comparison (optionally paired by common random numbers at the initial-seed level, not by forcing identical paths).
Watched failure terminals: PATH_REPLAY_LEAK, GENERATED_ACCESS_ASYMMETRY, TRAJECTORY_DISTRIBUTION_CONFOUND, SELF_CURRICULUM_EASY_MODE, UNDERPOWERED_GENERATED_ACCESS.

## U-boundary - contested online mechanism (pre-registered, mechanistic terms)
U = action-conditioned controllability-boundary update + viability-weighted repair policy. Four required components:
- U1 intervention-conditioned controllability estimate (which variables/channels respond to the agent's own interventions under context)
- U2 boundary-state update (damaged / intact / extended channels from action-conditioned evidence)
- U3 viability-weighted repair/action selection (probes, repairs, reinforcement, retreat, exploration by expected preservation/expansion of future access)
- U4 replay/consolidation (store perturbation-repair traces, reuse across episodes)

Forbidden U definitions (claimant excludes): U = whatever succeeds on C / any adaptive online learner / any system that builds a useful self-model / any process producing the same trace.
Pre-declared U-disabled ablations: ablate U1 (remove action-conditioned controllability update, keep generic memory+reward learning); ablate U2 (remove explicit boundary-state update); ablate U3 (reward-only policy); ablate U4 (remove cross-episode replay).
Pre-declared U-non-equivalent strong baselines: B4 world-model planner without explicit boundary-state/controllability U (same compute/memory); B3 history transformer with persistent memory, no explicit U readout / no pre-declared controllability graph (same compute/memory).
U-equivalence adjudication (claimant adopts FACG rule): B_i counts U-equivalent only if the U-like component is identifiable in trace/implementation/ablation AND disabling it destroys the match AND classified before outcome-based relabeling; else U_EQUIVALENCE_UNDETERMINED.

## Claimant's own expected first audit result
Most likely hostile verdicts: K-A1a caps; K-A1b/K-A2 -> B4 or B3 matches -> FORK_A_SHADOW_DOMINATED; B5 matches -> boundary mechanism not unique; B7 U-disabled still matches -> U not necessary; strong baselines match only by recreating U -> MECHANISM_FAMILY_REPLICATION; M wins by sample-efficiency -> CAPABILITY_NOT_SUBJECT. Only earns next stage if M beats B1-B9 at equal R, B7 U-disabled fails, U-ablations destroy the advantage, B3/B4/B5/B8/B9 do not match unless instantiating pre-declared U-equivalent components, and C stays non-oracle with controlled difficulty - and even then the purchase is only SURVIVES_HOSTILE_CLOSURE -> measurement-design card, not implementation/subjectivity/electronic-life.
