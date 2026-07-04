# FSP-PUM-ENV-IDPROBE-001A — EXECUTION PLAN 001A (Codex handoff)

- Status: ACTIVE. Card authorized 2026-07-01 (see card header). Codex may pick this up when free (currently on TLGP rung1 scout — do NOT interleave; see §8).
- Governing sources (read-only during execution): `docs/task_cards/FSP-PUM-ENV-IDENTIFIABILITY-PROBE-001A.md` (incl. R1), `docs/research/FSP-ENV-DESIGN-CONSTRAINTS-001A.md`. Modifying either during execution = blocking governance-self-modification failure.
- Roles: Codex = implementer/executor. Claude = independent hostile auditor (does NOT implement; separation is deliberate — the audit only has value if the auditor didn't write the code). Operator = authorization, freeze ceremony, bank ceremony.
- Compute: CPU-only. No GPU dependency, no collision with the rung1 scout hardware.
- One-loop-closure definition (what "闭环" means, binding): verdict + gap_certificates banked with complete artifacts under `artifacts/FSP-PUM-ENV-IDPROBE-001A/`, independent audit delivered, memory/handoff updated, next card selected per `FSP-ROADMAP-CONTINGENCY-001A` §N0. A FAIL or INVALID terminal closes the loop just as well as PASS — the loop validates the operating system, not the hypothesis.

## 0. Stage overview and dependency order

```
S0 freeze ceremony ─▶ S1 sealed simulator ─▶ S2 ideal observers ─▶ S3 fair battery
                                                        │                │
                                                        ▼                ▼
                                          S4 harness + adjudicator (needs S1–S3 interfaces)
                                                        │
                                                        ▼
                                          S5 certification run ─▶ S6 verdict / audit / bank / route
```

Estimated effort: 6–10 bounded Codex sessions total. S3 is the bulk. S2 carries the main technical risk (D1 below). Run compute for S5: hours-scale on CPU if S2 follows D1's vectorization plan.

## S0 — Freeze ceremony (operator + Codex, ~0.5 session)

- T0.1 Commit (scoped `git add` of the named files only — never `git add -A`, per standing git constraints) the card, the constitution, and this plan. Record canonical shas into the card's freeze block. DoD: 3-way identity — live blob sha == sha recorded in card == readback via file API (FUSE display truncation precedent: provenance reads use the file API, not mount `cat`).
- T0.2 Author `frozen_design.json` with zero TBD fields: all env parameters (K=8 topics, ≥2 preregistered interaction pairs, 2 sensitivity flags, trust α/β ranges, disclosure d, z_t AR(1) coefficients), thresholds (.80/.60/headroom mean .15/LCB .10/action-gap .10/saturation .95), N_heldout=200, 10 env seeds, sessions 20×15, MI feature families (single symbols, n-grams to k=3, per-session aggregates) + δ, decoder family spec (≥3 architectures + tuning budget), fixed-probe schedule grid + UCB scheduler spec, Gap-3 truncation form (last-B-tokens; B declared), regimes per gap, RNG event-log scheme, battery membership list (additions later allowed, deletions forbidden). DoD: schema-validated; sha pinned.

## S1 — Sealed simulator (~1–2 sessions)

- T1.1 `src/fsp_pum_env/simulator.py`: θ sampler, z_t AR(1), stochastic renderer with per-user style camouflage, probe semantics (probe-only dims respond ONLY to probe-class actions), trust dynamics (probes cost trust; low trust degrades observation informativeness). Sealed module, no import path from candidate/battery code to internals; hash-pinned.
- T1.2 Unit tests: distributional sanity; trust-dynamics direction; probe-only dims silent under passive play (interface-level test); θ/z never serialized into any observation field (structural test, not grep).
- T1.3 Knob variants as constructor parameters of the SAME generator (no second code paths): NULL (θ decoupled), camouflage_off, probe_channel_off, flat_theta, trust_cost_off, plus should-win variants for graph-cache (low-diversity templates) and RAG (stable-facts). DoD: all variants pass unit tests; leakage self-test scaffold in place (planted-leak mutant caught).

Design Decision D1 (resolve in S1, before S2): θ discretization. Recommendation: each θ dim on a 4-level grid; generator built so dims are conditionally independent given actions EXCEPT the ≥2 preregistered interaction pairs (those get joint grids). Posterior atoms ≈ 4^8 ≈ 65,536 (times small joint factors) — a numpy vector update per turn is trivial; 10 seeds × 200 users × 300 turns ≈ 600k turn-updates ⇒ CPU hours, not days. If D1 proves wrong (atoms explode): card N0.F3 fallbacks apply (factorize further → particle filter WITH convergence certificate on enumerable micro-configs). Forbidden at all levels: learned "ideal".

## S2 — Ideal observers (~1–2 sessions)

- T2.1 Exact Bayes filter over the D1 grid, generator-access, prefix-only interface. Variants (all thin wrappers over one filter core): full-history ideal; truncation-ideal (Gap-3 oracle side); passive ideal (no-probe policy); myopic-IG prober; fixed-schedule probers (grid from frozen_design); UCB scheduler.
- T2.2 PC-IDEAL-SANITY: ≥0.95 on the no-camouflage micro-config. DoD: PC green + tractability confirmed (wall-clock measured and logged); PC failure ⇒ stop, instrument fix, no redesign budget consumed.

## S3 — Fair battery (~2–3 sessions; the bulk)

- T3.1 Degenerates: predict_all / predict_none / majority / global-prior.
- T3.2 Trained obs-decoder family (≥3 architectures, tuned within declared budget, family_max reported).
- T3.3 Sequence models, budget-capped, with and without action-conditioning (LOG-PARITY members).
- T3.4 RAG-k retrieval + nearest-neighbor user matching.
- T3.5 Graph-cache family: successor_map, transition_table, count_table, fsm_planner, episodic_traversal — real fitted tables with alias_report each (rung3 precedent).
- T3.6 Discounted-LS / running-average preference regressor.
- T3.7 Should-win certificate run for EVERY member (constitution §7) + NULL-env control (no system shows headroom). DoD: all certificates green. Any certificate failure = FAIL_BASELINE_UNDERPOWERED-class instrument problem: fix the baseline, do not proceed, do not count anything.

## S4 — Harness + adjudicator (~1–2 sessions)

- T4.1 Trace logger per constitution §9: prediction-before-action enforcement (API-level — the env refuses an action without a committed prediction_json), prefix-only predictor interfaces, RNG event log, per-step S_hash/M_hash, memory/baseline manifests.
- T4.2 Leakage scanner + planted-leak self-test (mutant with θ in an obs field MUST be caught; scanner is thereby fail-able).
- T4.3 Replay validator: clean-room recomputation of every reported metric from trace alone (1e-9 deterministic tolerance; distributional metrics from logged samples).
- T4.4 Adjudicator as a SEPARATE module (runner cannot write verdicts): computes top-level terminal + gap_certificates vector + subtype code; self-test demonstrating ALL terminal states reachable on synthetic fixtures. DoD: adjudicator self-test artifact green before S5 starts.

## S5 — Certification run (CPU hours; one session to babysit)

Order fixed: T5.1 MI structural check (necessary-only) → T5.2 decoder gate + camouflage-off PC + surface-remap check → T5.3 gap measurements (Gap-1, Gap-3 in LOG-PARITY on frozen trajectory sets; Gap-2a, Gap-2b in ON-POLICY; Gap-2b via myopic-IG sufficient test, negative direction recorded as one_sided_untested) → T5.4 env-control ablations with preregistered directions → T5.5 NULL-env full battery. Artifacts per card: result.json (verdict + gap_certificates + claim_ceiling), trace.jsonl, baseline_comparison.json, ablation_report.json, replay_report.json, adjudicator_selftest.json, leakage_selftest.json, frozen_design.json, failure_manifest.json if anything fails. Failures are preserved verbatim, never patched.

## S6 — Verdict, audit, bank, route (~1 session + operator ceremony)

- T6.1 Adjudicator emits verdict; Codex STOPS at verdict (no commit, no interpretation beyond the adjudicator's output).
- T6.2 Independent hostile audit (Claude, fresh session): from-artifacts replay; killer-catalog sweep (K1/K2, tautology, parity, saturation, graph-cache aliasing); fail-able-ness spot checks; verdict = accept / requires-repair / invalid.
- T6.3 Operator bank ceremony: scoped commit of artifacts + shas + memory/handoff note.
- T6.4 Route strictly per `FSP-ROADMAP-CONTINGENCY-001A` §N0: PASS ⇒ authorize drafting of the N1 execution card (drafting is NOT pre-authorized by this plan); FAIL subtype ⇒ Plan B redesign card (001B, structural changes only, gates untouched); INVALID subtype ⇒ instrument fix, redesign budget untouched; INCONCLUSIVE ⇒ powered rerun per preregistered N.

## 7. Standing loop protocol (reusable for every future FSP card — this is the "operating system" the first closure validates)

```
card (bounded, numeric gates) → freeze (shas, zero TBD) → implement with PCs and self-tests
→ run (failures preserved) → adjudicate (separate module, all terminals reachable)
→ independent audit (non-implementer) → bank (operator ceremony) → route (contingency tree)
```

Invariants across all loops: no threshold motion post-freeze; instrument failures void rather than count; every chain ends in a bank; claim ladder is one-directional; auditor ≠ implementer.

## 8. Explicitly out of scope / not authorized by this plan

- N1 / N1.5 / N2 / N3 execution cards (drafting gated on N0 verdict — premature drafting is scope creep and will be treated as such).
- Any candidate mechanism code. Any EGO/AIRI/LLM-integration work. Any edit to banked artifacts or TLGP protected files.
- Interleaving with the TLGP rung1 scout: separate sessions, separate scoped commits, separate shas. A mixed commit contaminates both provenance chains.
- Claim ceiling unchanged: this loop can produce environment-validity evidence only; it cannot produce mechanism, user-model, social-cognition, or subject-adjacent claims — whatever the verdict.
