# FSP-PUM-ENV-IDENTIFIABILITY-PROBE-001A

STATUS: AUTHORIZED-FOR-IMPLEMENTATION (operator authorization given 2026-07-01, in-session, incl. Revision R1). Design freeze still required before any run: operator/Codex records canonical shas of this card + FSP-ENV-DESIGN-CONSTRAINTS-001A + frozen_design.json at commit time (3-way identity check: live sha == freeze record == readback). Execution plan: docs/codex/tasks/FSP-PUM-ENV-IDPROBE-001A-EXECUTION-PLAN-001A.md.

## Task id

FSP-PUM-ENV-IDENTIFIABILITY-PROBE-001A

## Problem definition

Before any "persistent user model" candidate exists, certify — candidate-free, CPU-only — whether a sealed synthetic-user environment (PUM-ENV) can have the three properties every downstream FSP route depends on:

1. Headroom: an ideal observer with generator access predicts user reactions to counterfactual actions far better than a hostile fair-baseline battery.
2. Probe-dependence: a preregistered subset of the user latent is identifiable only through active probe actions (action-conditioning gap > 0), and probes carry cost (trust dynamics), so probing is a decision, not a freebie.
3. Non-degeneracy: no saturation, no observation-decodability of the latent, no label leakage — all verified by fail-able self-tests, not asserted.

If no PUM-ENV configuration passes after v1 + 2 bounded redesigns, the user-model route family closes at the environment level. That negative is the cheapest possible falsification point for the whole FSP program.

## Current stage

Environment-validity preflight (candidate-free). Analogous in role and method to TLGP-CAPABILITY-WITNESS-RUNG3-IDENTIFIABILITY-PROBE-001A (banked @7f7de677: probe pattern validated; certified ideal ≈ 0.96 vs fair ≈ 0.20 before GPU spend) and to the LRGG candidate-free preflight lineage (docs/codex/tasks/LRGG-CANDIDATE-FREE-*).

## Layer

Engineering implementation + mechanism-hypothesis preflight. Produces environment-validity evidence only. No learning claims, no user-model claims, no social-cognition claims.

## Prior negative evidence consulted (mandatory citations)

- GATE4-CROSS-FAMILY-SOCIAL-001A invalid_self_report: candidate==label-generating process tautology; same-access faithful baseline parity → this card seals the simulator (hash-pinned module, no candidate-side import path), evaluates behavior prediction (never latent readout as primary), and grants identical observation access + budget to every battery member.
- GG-COBIND-ID-001A non-identifiability + killer catalog K1/K2 (docs: itl-self-boundary-killer-catalog) → K1 answered by camouflage + trained-decoder certification (below); K2 answered by making the interventional channel (probes) costly and by requiring the action-conditioning gap to be measured against a fair passive ideal, not assumed.
- ROUTE-C-PREFLIGHT-001A obs-baseline-underpowered blocker (repaired @278819a) → the obs-decoder here is a trained, capable attacker family with a family_max report, never a strawman.
- Candidate-free Route C separation probe false positive (recall-only metric, missing predict_all) → balanced macro metrics only; predict_all/predict_none in battery; single-sided metrics forbidden.
- ACOLB-001A closure (candidate==discounted batch LS) → discounted-LS/running-average preference regressor is in the battery at probe stage already.
- RESIDUE-001A window dominance → battery includes budget-matched full-history sequence baseline with and without action conditioning.
- Gate1 EXEC-001 graph_cache_collapse + CLAUDE.md preflight rule → graph-cache challengers (successor_map, transition_table, count_table, fsm_planner, episodic_traversal) mandatory, implemented as real fitted tables (rung3 precedent: real successor_map with structural blind backoff, alias_report included).
- TLGP runner_copy_fail (positive control caught pooling confound) → this card's instruments ship with their own positive controls and fail-able self-tests before any verdict is read.
- BASELINE-IMMUNITY-ADMISSION-STANDARD-001A + DISTRIBUTION-HEADROOM-PREFLIGHT-CONTRACT-001A (docs/codex/contracts/) → admission checks (saturation, obs-decodable, degenerate predictors) applied as specified.

## Hypothesis

H1 (env-validity): there exists a PUM-ENV configuration within the frozen design family such that, over 10 env seeds, on N_heldout = 200 heldout users:

- ideal-observer counterfactual-reaction macro-accuracy ≥ 0.80;
- fair-battery family_max macro-accuracy ≤ 0.60;
- headroom mean ≥ 0.15 and bootstrap 95% LCB ≥ 0.10;
- action-conditioning gap: ideal-with-probes − ideal-without-probes ≥ 0.10 on the probe-dependent θ subset;
- no battery member ≥ 0.95 (saturation sentinel);
- trained single-session obs-decoder ≤ 0.60 on θ-dependent predictions, AND ≥ 0.80 on the camouflage-off env ablation (proves the decoder is capable and the camouflage is doing the work — fail-able in both directions).

H0: no configuration in the frozen family satisfies the conjunction → verdict env_family_not_identifiable (a bankable negative).

## Environment design (frozen family; parameters frozen before run)

- User latent θ: preference weights over K=8 topics/action styles (with ≥2 conditional/interaction terms — anti-discounted-LS), sensitivity flags (2), trust dynamics (gain α, decay β), disclosure threshold d. A preregistered subset θ_probe (≥3 dims incl. both sensitivity flags) has zero passive identifiability by construction (they gate responses only to probe-class actions).
- Session state z_t: appraisal-structured (valence, arousal, stress), AR(1), influences response style.
- Renderer: p(response_symbol | θ, z_t, a_t) with per-user style camouflage (random style map decorrelating surface symbols from θ across users). Discrete/symbolic alphabet; no natural-language rendering in this card.
- Actions: task actions, recommend, probe_1..probe_m (probe_i informative about specific θ dims; each probe reduces trust by cost c_i via α/β dynamics; low trust degrades observation informativeness — probing is self-limiting).
- Episodes: N_sessions = 20 per user, T = 15 turns; θ persistent, no drift in this card (drift is a later card).
- Evaluation queries: at preregistered query points, predict the user's response distribution to a counterfactual action set (never seen labels; scored against simulator samples, macro-balanced + Brier/ECE).
- Sealing: simulator in isolated module, sha-pinned in frozen_design.json; θ, z never serialized into trace observations; leakage self-test plants θ into an observation field in a mutated copy and the scanner MUST catch it (fail-able detector requirement).

## Baselines (fair battery — all capable, all fitted on the same trace data, identical access and budget)

1. predict_all / predict_none / majority / global-prior (degenerate admission checks)
2. trained single-session obs-decoder (capable attacker family, family_max reported)
3. budget-matched full-history sequence model WITHOUT action conditioning
4. budget-matched full-history sequence model WITH action conditioning but no cross-session persistence (window model)
5. RAG-k episode retrieval; nearest-neighbor user matching
6. graph-cache family: successor_map, transition_table, count_table, fsm_planner, episodic_traversal (real fitted tables, alias_report each)
7. discounted-LS / running-average preference regressor
8. Oracle bounds: ideal observer (Bayes/enumerative with generator access) with probes; ideal without probes (passive ideal)

## Ablations (environment-controls, not candidate ablations)

- camouflage-off variant: obs-decoder must rise ≥ 0.80 (certifies decoder capability + camouflage causality)
- probe-channel-off variant: action-conditioning gap must collapse to ≈ 0 (certifies the gap is real probe information, not artifact)
- flat-θ variant (no conditional terms): discounted-LS must rise toward ideal (certifies the nonlinearity is what defeats it)
- trust-cost-off variant: probe-spam ideal must dominate (certifies cost structure binds)

Each ablation has a preregistered directional prediction; wrong direction = design bug, run stops with failure_manifest.

## Trace / replay requirement

trace.jsonl per episode: t, session, observation, action, (for ideal/baselines) predicted distribution, actual response, prediction error, trust state, query-point counterfactual predictions. Replay validator must reconstruct all reported metrics from trace alone (tolerance 1e-9 for deterministic components; distributional metrics from recorded samples). No hidden state, no future observations at prediction time (enforced by interface: predictors receive prefix-only views).

## Acceptance gate (preregistered; adjudicator must demonstrate ALL terminal states reachable via self-test before the run is read)

Terminal states:
- env_valid_headroom_certified (H1 conjunction holds)
- env_family_not_identifiable (H0 after this configuration)
- invalid_integrity (any self-test, leakage plant, PC, or replay failure)
- inconclusive_underpowered (LCB straddles threshold; explicit, not massaged)

Positive controls: PC-IDEAL-SANITY (ideal on a trivial no-camouflage micro-config must reach ≥ 0.95 — certifies ideal implementation); PC-LEAK-PLANT (planted leak must be caught); PC-DECODER (camouflage-off decoder rise). Any PC failure → invalid_integrity regardless of other numbers.

## Claim ceiling

Bounded environment-validity evidence only: "PUM-ENV configuration X does / does not exhibit ideal-vs-fair headroom and probe-dependent identifiability under the frozen design." NOT evidence of: user modeling capability, social inference, theory of mind, relationship modeling, learnability by any candidate, or any FSP mechanism. Explicitly cannot support consciousness/subjectivity/emotion/agency/companion claims.

## Stop condition

- Any anti-hardcoding audit hit (hardcoded verdict, threshold moved after seeing results, schema change to hide failure, test-only logic path) → STOP, failure_manifest, no patching.
- H0 at v1 → one bounded redesign card (FSP-PUM-ENV-IDPROBE-001B) allowed; H0 again → one final redesign (001C); H0 a third time → close env family, bank negative as route evidence. No threshold relaxation across redesigns; redesigns may change env structure only, never gates.
- Budget: CPU-only; if ideal-observer computation exceeds tractability (enumeration blowup), STOP and report — do not substitute a learned "ideal" (that would be a candidate smuggled into the oracle slot).

## Rollback plan

All new files under src/fsp_pum_env/, tests/fsp_pum_env/, artifacts/FSP-PUM-ENV-IDPROBE-001A/, this card. Forbidden: any edit to banked artifacts, protected TLGP files (retrieval model / positive control / meta_learners), contracts, CLAUDE.md, thresholds after freeze, any git commit (operator banks; executor stops at verdict). Rollback = delete new directories; repo state untouched.

## Expected artifacts

artifacts/FSP-PUM-ENV-IDPROBE-001A/: result.json (with claim_ceiling field + verdict), trace.jsonl, baseline_comparison.json, ablation_report.json, replay_report.json, adjudicator_selftest.json, leakage_selftest.json, frozen_design.json (+ canonical sha recorded pre-run), failure_manifest.json if anything fails.

## Revision R1 (2026-07-01, pre-freeze; authorized 2026-07-01 together with the card — see STATUS line; stale "DRAFT — NOT AUTHORIZED" wording reconciled at S0 with operator sign-off, see ledger)

This card is now governed by `docs/research/FSP-ENV-DESIGN-CONSTRAINTS-001A.md` as a read-only rule source (binding, not advisory). Modifying that document during implementation of this card is a blocking governance-self-modification failure. Deltas introduced by R1:

1. Gap certificates: the verdict gains a mandatory `gap_certificates` vector {gap1, gap2a, gap2b, gap3} ∈ {certified, absent, one_sided_untested} plus a subtype code per the constitution's terminal vocabulary (§10). The four top-level terminal states of this card remain authoritative; subtypes are refinements, not a second schema.
2. Gap-2b measurement added (ON-POLICY regime): myopic-IG-ideal vs best-fixed-probe-schedule ideal and UCB-scheduler ideal. Sufficient-test only: myopic-IG win certifies gap2b; myopic-IG non-win records `one_sided_untested`, never `absent`.
3. Evaluation regimes declared per gap (constitution §2): Gap-1/Gap-3 in LOG-PARITY (all predictor-class members fitted/scored on the same frozen trajectory sets); Gap-2a/2b in ON-POLICY. Regime mixing = INVALID.
4. Gap-3 oracle-side proxy fixed as truncation-ideal (Bayes posterior on declared budget-truncated history); truncation form goes into frozen_design.json.
5. New environment controls: NULL env (θ independent of obs/probes → no system may show headroom, else FAIL_NULL_FALSE_HEADROOM) and surface-remap check (fresh renderer: old decoders must fail, ideal invariant).
6. Cost model: memory reads/writes and offline compute metered; offline-compute parity per constitution §5 (relevant to downstream N1, recorded here so the env emits the accounting fields from day one).
7. Baseline capability certificates (constitution §7) adopted verbatim; any certificate failure → instrument-invalid subtype, candidate/bank actions void.

## Notes for implementer (Codex)

- Freeze order: card final → frozen_design.json canonical sha computed and recorded → implementation → self-tests → run → verdict. Any deviation is a governance failure, not a judgment call.
- The adjudicator is a separate module from the runner; runner cannot write verdicts.
- Battery members are real fitted objects with their own unit tests; each must be demonstrably able to win on some mutated env (fail-able in the winning direction too).

## Freeze record (S0, 2026-07-02)

Canonical blob shas of the other frozen rule sources, computed host-side at commit time (`git hash-object`, filters applied — identical to the committed blob):

- `docs/research/FSP-ENV-DESIGN-CONSTRAINTS-001A.md` (constitution): `882a68de2973ec1dedb588b85c6ee2703b897a4f`
- `docs/codex/tasks/FSP-PUM-ENV-IDPROBE-001A-EXECUTION-PLAN-001A.md` (execution plan): `c07eec2ac38423bed6788904bc15013e6e755410`
- `artifacts/FSP-PUM-ENV-IDPROBE-001A/frozen_design.json` (frozen design, zero TBD): `32d2cbd538f31694246b2e6bb7fd5377a329478f`

This card's own blob sha and the freeze commit sha are recorded in `artifacts/FSP-PUM-ENV-IDPROBE-001A/freeze_record.json` and in the ledger transition entry (self-reference is resolved there, not here). From the freeze commit onward, this card, the constitution, the execution plan, and frozen_design.json are read-only / supersede-only.
