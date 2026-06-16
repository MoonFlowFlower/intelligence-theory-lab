# ACOLB-001A — Implementation Blueprint Audit

Task id: `ACOLB-001A-IMPLEMENTATION-BLUEPRINT-AUDIT`
Task type: independent hostile implementation-design audit (blueprint production).
Layer: engineering implementation + mechanism-hypothesis design. Not a Gate run, not evidence, not repo modification.
Surface under design: `ACOLB-001A` — action-conditioned online latent-boundary surface.
Intended mechanism: online action-conditioned prediction-error belief update under OOD / non-stationary latent dynamics.

## Claim ceiling (binding on this document and on any future implementation built from it)

This is an implementation blueprint only. It does not prove mechanism validity, Gate passability, baseline non-equivalence, mainline effect, agency, autonomy, consciousness, emotion, stable user benefit, or EGO readiness. The strongest claim any future run built from this blueprint may make is: *bounded offline evidence that, on this generator, a recursive action-conditioned prediction-error update was non-equivalent to the strongest fair amortized/lookup baseline under a predeclared OOD band, with passing in-distribution parity and load-bearing ablations.* Even that claim is bounded to the specific generator, seeds, and band, and is N≈1 surface evidence, not mechanism truth.

---

## 0. Grounding, prior negative evidence, and role separation (read before the plan)

### 0.1 Status facts (verified against the repo at audit time)

- **Fact.** The design file named in the task card, `GATE0-5-FEASIBLE-MECHANISM-SURFACE-DESIGN-001A.md`, **does not exist** anywhere in the repo (searched by name and by content). The only on-disk anchors for this surface are `docs/research/NEXT-MECHANISM-SURFACE-ROUTE-DECISION-001A.md` and a passing mention in `artifacts/gate_target_independent_ground_truth_preflight_001a/readback.md`.
  - **Inference.** This blueprint is therefore not auditing an existing design document; it is producing the design content that document was supposed to contain. Treat every constraint below as originating here, not as a restatement of a predeclared file.
  - **Required follow-up (non-blocking for this doc).** Before Codex implements, the surface owner must either create `GATE0-5-FEASIBLE-MECHANISM-SURFACE-DESIGN-001A.md` containing (or referencing) this blueprint, or rename the task-card pointer. A blueprint that judges an implementation must itself be a frozen, predeclared rule source (see §0.4 role separation).
- **Fact.** `ACOLB-001A` is a derivative of Route A (`ACTION-CONDITIONED-PREDICTIVE-BOUNDARY-VIABILITY`, "ACP-BV") selected in `NEXT-MECHANISM-SURFACE-ROUTE-DECISION-001A`, pivoted from the saturated static-distribution surface to an online / OOD / non-stationary-latent surface.
- **Fact.** The route decision authorizes *future task-card drafting only*; it does not authorize implementation. This blueprint inherits that ceiling — it is design, not authorization to run.

### 0.2 Prior negative evidence this blueprint must not re-incur (cited per operating contract)

The operating contract requires citing relevant prior negative evidence before proposing any new implementation. The following are load-bearing for the F1 risk.

1. **ACP-BV 001B saturation closure (the direct precedent).** The static-distribution ACP-BV surface was closed because the strongest *fair* legal-channel parametric baseline reached ceiling (legal parametric ≈ 1.0), so `candidate − baseline ≈ 0` → **baseline equivalence** → route closed (memory: `acp-bv-001b-post-anchor-route-decision-audit`, `98be7f4`). The 001B candidate (`src/acp_bv_distribution_harness_001b/candidate.py`) was a **closed-form parametric reader of the same-step legal observation** (`intercept + action_delta[a] + Σ obs[k]·w[k]`, then mod). Any fair learner that fits that parametric form ties it. **Lesson: if the target is computable from the same-step legal observation, the surface is saturated and cannot discriminate a mechanism.**
2. **Saturation STOP-gate protocolization** (`docs/codex/contracts/DISTRIBUTION-HEADROOM-PREFLIGHT-CONTRACT-001A`). Derived from that one closure (N=1, explicitly): *before authoring any candidate, require* `strongest_fair_legal_channel_baseline < ceiling − equivalence_band`; otherwise reject the distribution as saturated. This rule is **reused verbatim** as Phase 0 below.
3. **Role-separation rule** (same contract): `red_first_designer != implementer != hostile_auditor`. This blueprint is the red-first designer artifact. Codex is the implementer. A *different* pass must be the hostile auditor of the resulting run. Encoded in §0.4.
4. **ACSB downgrade collapse family** (`NEXT-MECHANISM-SURFACE-ROUTE-DECISION-001A` §8; memory `itl-acsb-001b/001c/001d`). Repeated collapses: oracle / same-step legal-observation shortcut; fake learner with no train consumption; reference path sharing the target-generation identity; boundary memory not causally controlling scored behavior; capacity-disabled inertness that is non-fail-able; replay confirming stored conclusions; tests asserting artifact verdicts instead of recomputation. Every one of these maps to a control below.
5. **Computed-evidence provenance failure family** (`docs/codex/contracts/COMPUTED-EVIDENCE-PROVENANCE-CONTRACT-001A` §4–6): scores from constants/static tables, hash-only replay, candidate action not computed from deserialized state, unused train contexts, tests asserting pass. The provenance schema (§6 of that contract) is **reused** as the per-score provenance block (§12 below).

### 0.3 The eight route-level admissibility gates this blueprint must operationalize

From `NEXT-MECHANISM-SURFACE-ROUTE-DECISION-001A` §9, each mapped to a concrete blueprint section:

| Route gate | Operationalized in |
| --- | --- |
| G1 target non-oracle (not computable from same-step legal obs / action+obs) | §4 generator, §3 legality tags, §11 L1/L2/L3 |
| G2 target-generator isolation (unreachable from candidate/baseline/replay/eval) | §2 module boundaries, §4, §11 L4 |
| G3 train consumption (empty-train / label-shuffle must degrade or block) | §6 baselines, §7 amortized protocol, §9 A4 |
| G4 boundary/latent-state causal dependence (mutate/disable must change behavior or block) | §5 candidate, §9 A1/A3/A6, §10 counterfactual replay |
| G5 fair strongest baseline; if it matches candidate, **downgrade** not repair | §6, §7, §8 headroom, §15 stop |
| G6 replay recomputes from serialized state + observation/history, not hash compare | §10 |
| G7 leakage/scanner positive controls fire | §11 |
| G8 objection test: if mechanism reduces to a simpler thing, downgrade to world-model-only / block | §0.5 (F1), §14 acceptance |

### 0.4 Role separation enforced by this blueprint

- **Designer (this document).** Fixes generator contract, schemas, baseline panel, bands, gates, stop conditions. After Codex starts, this document is **read-only**. If implementation needs a rule changed, that is a governance-self-modification event and must stop, not be silently absorbed (consistent with the same-agent bridge governance rule in `CLAUDE.md`).
- **Implementer (future Codex).** Implements only under §16 card and only the allowed paths. May not edit this blueprint, the generator's hidden-latent contract, the bands, or the failure taxonomy.
- **Hostile auditor (a later, separate pass).** Re-runs, tampers, and checks the produced run against this frozen blueprint. Not the same pass as the implementer.

### 0.5 Strongest objection to this blueprint task — is ACOLB-001A still too easy to fake? (F1)

The task names the central risk **F1: the OOD gap may come from an undertrained or underpowered `amortized_seq` baseline, not from a real online prediction-error update mechanism.** This must be answered before the plan, because the entire module tree exists to make F1 observable and terminal.

**Q1. Can a sufficiently strong `amortized_seq` still saturate OOD?**
Yes, in principle. An in-context sequence learner (meta-learned over many episodes, with test-time access to the same legal probe stream) is a universal-ish amortizer of Bayesian filtering. If the OOD shift stays within the family the amortizer was meta-trained to handle, a large-enough `amortized_seq` can match or beat an explicit recursive update. This is not a defect to engineer around; it is the honest null. **Fact, not assumption:** the 001B precedent shows a fair baseline reaching ceiling is the *expected* outcome on a discriminable-looking surface.

**Q2. If yes, does that close the route or merely reduce headroom?**
It **closes** the mechanism-evidence route for this surface (verdict: baseline equivalence / `saturated_close`), exactly as 001B closed. It does **not** prove the candidate mechanism wrong; it proves the surface cannot *discriminate* the candidate from a strong amortized learner. Per the route decision, that triggers downgrade to Route B (world-model-only) or block. **The blueprint must treat `amortized_seq` saturating OOD as a STOP, never as a reason to weaken `amortized_seq`** (the task forbids weakening it; so does G5).

**Q3. How do we distinguish candidate mechanism from baseline weakness?**
Four independent locks, all required to even reach an OOD claim:
1. **In-distribution (ID) negative control.** Where there is no OOD excuse, the strongest fair baseline **must catch** the candidate: `abs(candidate_id − amortized_seq_id) <= band`. If `amortized_seq` cannot match the candidate *in its own training distribution*, it is underpowered/unfair, and any OOD "win" is attributable to baseline weakness, not mechanism → `parity_broken_close` → `blocked_by_underpowered_or_unfair_amortized_baseline`. This is the primary F1 detector.
2. **Convergence / capacity-parity proof.** A learning-curve artifact must show `amortized_seq` validation loss plateaued (no further descent), and a parity report must show its capacity/compute is ≥ the candidate's effective capacity. An undertrained baseline is caught here even if ID parity is noisy.
3. **Argmax baseline selection.** `strongest_fair_baseline` is selected by `argmax` over the whole panel's score, **by number not by name**. Codex cannot nominate a weak baseline as "strongest."
4. **Load-bearing ablations.** The candidate's OOD advantage must collapse when prediction-error correction (A3) or action-conditioning (A2) is removed. If the advantage survives those ablations, the advantage is not coming from the claimed mechanism and the claim is void.

**Q4. Is OOD adaptation a legitimate mechanism test or just distribution trickery?**
It is legitimate **only under an equal-access parity rule**, otherwise it is trickery. You can always construct a shift that an arbitrary *frozen* baseline fails; that proves nothing. The legitimacy condition: the strongest fair baseline must be a **test-time sequence/in-context learner that receives the same legal probe stream** as the candidate (`amortized_seq`), so both have equal access to the adaptation signal. The only remaining difference is *mechanism* (explicit recursive PE update vs learned in-context adaptation). If, with equal access, `amortized_seq` ties the candidate ID and still loses OOD beyond band, *and* ablations show the loss is due to PE/action-conditioning, that is bounded mechanism-discrimination evidence. Comparing the candidate against a frozen, no-test-time-history baseline is rigged and is **forbidden** (it would be the F1 failure itself).

**Q5. What is the smallest implementation that makes F1 observable rather than hidden?**
The minimal F1-observable core is: `generator` + `amortized_seq` (converged, equal-access) + `candidate` + `headroom_preflight` running the **Phase-0 ID negative control and OOD headroom check before any candidate mechanism claim**. If `amortized_seq` is underpowered, Phase 0 emits `parity_broken_close` / `saturated_close` and the run stops with a `failure_manifest.json` *before* any mechanism score is reported. Everything else (full ablation suite, leakage panel, replay) hardens the claim but F1 is already observable from this minimal core. This is why §8 (Phase 0) is a hard precondition for §5 (candidate evaluation), not a parallel step.

**Designer's bounded conclusion on F1.** ACOLB-001A is *not* automatically safe; it is safe *only if* Phase 0 (ID parity + convergence + argmax + headroom) gates the candidate claim and the ablations are real reruns. Without those, OOD adaptation is exactly as fakeable as the 001B static surface was saturable — the failure mode is merely inverted (fake headroom from a weak baseline instead of zero headroom from a strong one). The rest of this blueprint is the enforcement of that conditional.

---

## 1. Proposed file tree (exact allowed paths)

Codex may create only the following. Anything outside this list is a forbidden-path violation (§15 `blocked_by_forbidden_path`).

```text
src/acolb_001a/
  __init__.py
  config.py                 # frozen constants, bands, seeds, paths; no logic that reads results
  schemas.py                # dataclasses / TypedDicts for every record in §3; legality tags as code
  generator.py              # hidden-latent episode generator; the ONLY module that knows theta/formula
  legal_view.py             # projects a HiddenLatent+ProbeStep into a LegalObservation (the only legal channel)
  candidate.py              # recursive action-conditioned PE update; consumes legal channel only
  baselines.py              # all non-amortized baselines as independent callables (§6)
  amortized_seq.py          # the meta-trained in-context sequence baseline (§7)
  headroom_preflight.py     # Phase 0: ID negative control + OOD headroom + argmax selection (§8)
  ablations.py              # A1..A6 as real rerun interventions (§9)
  leakage.py                # L1..L6 injected-corruption positive controls (§11)
  replay.py                 # recompute-from-serialized-state replay (§10)
  scoring.py                # per-case score + aggregation; pure, deterministic
  provenance.py             # builds the provenance block for every score (§12)
  runner.py                 # orchestrates Phase0 -> (stop|candidate) -> ablation -> replay -> leakage -> artifacts
tests/acolb_001a/
  test_generator.py
  test_legal_channel_isolation.py
  test_candidate_update.py
  test_baselines_independent.py
  test_amortized_convergence.py
  test_headroom_preflight.py
  test_ablations_rerun.py
  test_replay_recompute.py
  test_leakage_positive_controls.py
  test_runner_stop_paths.py
  test_provenance.py
  fixtures/                 # saturated fixture, parity-broken fixture, leaky fixtures (built by code, not hand-labeled)
artifacts/acolb_001a/
  (run outputs only; see §12; never hand-edited)
```

**Forbidden to create or modify (hard block, §15):** `src/acp_bv_distribution_harness_001b/**` and any other prior surface; `src/ego_mainline_**`; any mainline/runtime/bridge/scheduler/admission/companion/product/LLM path; global schemas; `docs/codex/contracts/**` and `docs/research/**` rule sources (read-only); `scripts/push.sh` or any remote-anchor / git-tag script. No new top-level package. No edits to `CLAUDE.md` / `AGENTS.md`.

**Auto-Remote-Anchor: forbidden.** Codex must not push, tag, or create remote anchors. Anchoring, if any, is a separate human-authorized step.

---

## 2. Module responsibilities (what each does and must NOT do)

For each module: **Does** / **Must not**. "Must not" lines are the anti-leakage spine.

- **`config.py`**
  - Does: declare frozen scalars only — `EQUIV_BAND`, `RHO` (mechanism-floor fraction), `OOD_BAND`, seed lists, episode counts, `D=2` (latent dim), action set, probe/query lengths, convergence tolerances, artifact paths. All thresholds carry `frozen_before_run=true`.
  - Must not: import `generator` internals, read any artifact, compute anything from results, or expose `theta` / formula constants. No value in `config.py` may be tuned after a run (§15 `blocked_by_threshold_tuning`).
- **`schemas.py`**
  - Does: define every record in §3 with explicit per-field legality tags (`legal_candidate`, `legal_baseline`, `hidden`, `derived`, `answer_bearing`, `oracle_only`) encoded as metadata an assertion can read.
  - Must not: contain logic that copies a `hidden`/`answer_bearing` field into a `legal_*` field. Schema is data-shape only.
- **`generator.py`** (the single source of ground truth)
  - Does: sample per-episode hidden `theta` (`d=2`); evolve the action-conditioned latent dynamics (train regime and OOD regime); produce `HiddenLatent`, `ProbeStep`s, `Query`s, and the per-(query,action) truth used only by `oracle`/scoring.
  - Must not: be imported by `candidate`, `baselines`, `amortized_seq`, `replay`, or `scoring`'s candidate path. The truth it emits is handed to `scoring`/`oracle` through a **separate channel** that the candidate cannot reach (§4, L4). It must not write `theta` or the formula into any `LegalObservation`.
- **`legal_view.py`**
  - Does: the *only* function that converts internal state into what a learner may see — `to_legal_observation(hidden, probe_step) -> LegalObservation`. This is the legal channel chokepoint.
  - Must not: include `theta`, latent state, future outcomes, query truth, or the generator formula in its output. Every field it emits is tagged `legal_*`. A test asserts the set of emitted keys equals the predeclared legal key set (no extra keys).
- **`candidate.py`**
  - Does: maintain a recursive posterior over `theta` updated from legal `(action, outcome)` pairs via prediction error; serialize/deserialize posterior; predict query outcomes from posterior + legal query context.
  - Must not: import `generator`; read `theta`, query truth, or any `hidden`/`answer_bearing`/`oracle_only` field; use future probe steps for a current prediction; store the truth in serialized state.
- **`baselines.py`**
  - Does: implement each non-amortized baseline (§6) as an independent top-level callable with an explicit `legal_inputs` contract and a `producer_function` name.
  - Must not: share mutable state between baselines; call `generator`; let any baseline read `oracle` fields except the `oracle` baseline (ceiling, never fair).
- **`amortized_seq.py`**
  - Does: meta-train an in-context sequence model over training-regime episodes; at test time consume the **same legal probe stream** as the candidate; expose `fit`, `predict`, learning-curve and capacity introspection.
  - Must not: see `theta` or query truth at train or test; receive a different (weaker) legal channel than the candidate; be capacity-throttled below the candidate (parity rule, §7).
- **`headroom_preflight.py`** (Phase 0; F1 gate)
  - Does: run the full baseline panel + candidate **in-distribution and OOD**, compute headroom and the ID negative control, select `strongest_fair_baseline` by argmax, emit `headroom_preflight.json` with verdict in `{headroom_present, saturated_close, parity_broken_close}`.
  - Must not: be skipped, run after the candidate claim, or read a band that was changed after seeing scores.
- **`ablations.py`**
  - Does: for A1..A6, construct a modified run configuration and **re-execute** episodes end-to-end under the intervention, producing fresh per-case scores.
  - Must not: subtract a stored constant, look up a precomputed ablation table, or reuse the main run's cached predictions (§15 `blocked_by_ablation_not_rerun`).
- **`leakage.py`**
  - Does: for L1..L6, inject a specific corruption into inputs/wiring and assert the scanner *fires* and/or the score moves as predicted.
  - Must not: be an unconditional "clean" reporter; every control must have a positive (injected-leak) case that must fail-loud (§15 `blocked_by_non_fail_able_control`).
- **`replay.py`**
  - Does: reconstruct the posterior trajectory and query predictions by re-running the update from `serialized_state + legal observations`, compare trajectories within tolerance, and run a counterfactual replay on an ablation action sequence.
  - Must not: compare stored output hashes as the pass criterion (§15 `blocked_by_replay_hash_only`).
- **`scoring.py`**
  - Does: pure per-case scoring of a prediction vs truth (truth arrives via the oracle/scoring channel only), and predeclared aggregation (e.g., mean accuracy / negative log loss). Deterministic given inputs.
  - Must not: expose truth back to any candidate/baseline path; change aggregation rule per baseline.
- **`provenance.py`**
  - Does: build the `MetricProvenance` block (§12, reusing `COMPUTED-EVIDENCE-PROVENANCE-CONTRACT-001A` §6) for every emitted score, including `code_path_hash` of the producer function.
  - Must not: emit `computed_not_literal=true` for a value it did not observe being computed; omission of a field is not "not applicable."
- **`runner.py`**
  - Does: orchestrate `Phase0 -> (STOP on non-`headroom_present` | candidate eval) -> ablations -> replay -> leakage -> artifact emission`; write `failure_manifest.json` on any STOP; never reach the candidate claim if Phase 0 did not return `headroom_present` AND ID negative control passed.
  - Must not: catch a gate failure and downgrade it to a warning; reorder so candidate runs before Phase 0; aggregate a verdict that contradicts an emitted failure manifest.

---

## 3. Exact data schemas (with per-field legality tags)

Legality tag legend: **C** legal-for-candidate, **B** legal-for-baseline, **H** hidden/forbidden to both, **D** derived, **A** answer-bearing (forbidden to candidate and all fair baselines), **O** oracle-ceiling-only. A field may carry C+B (both), or H+A (hidden answer), etc. The **legal channel = exactly the C/B fields surfaced through `legal_view.to_legal_observation`.**

### EpisodeSpec
| field | type | tag | notes |
| --- | --- | --- | --- |
| `episode_id` | str | C,B | stable id `f"{regime}-{seed}-{idx}"` |
| `regime` | enum{`train`,`ood`} | C,B | which latent-dynamics regime |
| `seed` | int | C,B | deterministic seed |
| `theta` | float[ d=2 ] | H | hidden per-episode latent; never surfaced |
| `dynamics_params` | dict | H | OOD shift parameters (drift rate, regime map) |
| `probe_len` | int | C,B | number of probe steps |
| `query_len` | int | C,B | number of queries |
| `probe_action_set` | list[str] | C,B | actions used during probe |
| `query_action_set` | list[str] | C,B | **disjoint** from probed actions (see §4) |

### ProbeStep
| field | type | tag | notes |
| --- | --- | --- | --- |
| `t` | int | C,B | time step |
| `action` | str | C,B | action actually taken at probe t |
| `outcome` | legal-coded | C,B | observed outcome of (action,latent) — the legal evidence |
| `outcome_is_stochastic` | bool | C,B | true; outcome has generator noise (§4) |
| `latent_at_t` | float[2] | H | hidden latent value at t |
| `pe_truth` | float | H,A | true prediction error (for diagnostics/oracle only) |

### Query
| field | type | tag | notes |
| --- | --- | --- | --- |
| `q_id` | str | C,B | query id |
| `query_action` | str | C,B | action to predict outcome for; in `query_action_set` (disjoint) |
| `query_context` | legal-coded | C,B | legal context needed to make the prediction |
| `truth_outcome` | legal-coded | H,A,O | the answer; reaches scoring/oracle ONLY |
| `truth_producer` | str | H | name of generator fn that made truth (isolation check) |

### LegalObservation (the entire legal channel; produced only by `legal_view`)
| field | type | tag | notes |
| --- | --- | --- | --- |
| `episode_id` | str | C,B | |
| `t` | int | C,B | |
| `action` | str | C,B | |
| `outcome` | legal-coded | C,B | |
| `query_action` | str | C,B | present only on query rows |
| `query_context` | legal-coded | C,B | |
| (closed key set) | — | — | a test asserts emitted keys == predeclared legal set; no `theta`,`latent_*`,`pe_truth`,`truth_*`,`dynamics_*` |

### HiddenLatent
| field | type | tag | notes |
| --- | --- | --- | --- |
| `theta` | float[2] | H | |
| `regime` | enum | H | |
| `dynamics_params` | dict | H | |
| `outcome_fn_id` | str | H | identifier of action-conditioned outcome function |
| accessor | — | O | only `generator`/`oracle` may read this object |

### CandidateState (serialized posterior; the only thing replay may use)
| field | type | tag | notes |
| --- | --- | --- | --- |
| `posterior_mean` | float[2] | D | belief over theta, derived from legal evidence |
| `posterior_cov` | float[2][2] | D | uncertainty |
| `n_updates` | int | D | count of (action,outcome) pairs consumed |
| `last_pred_error` | float | D | most recent legal prediction error |
| `uses_hidden_truth_labels` | bool | C | must be `false`; asserted |
| `uses_future_observations` | bool | C | must be `false`; asserted |
| `candidate_authored_truth` | bool | C | must be `false`; asserted |
| (forbidden) | — | — | must NOT contain `theta`, `truth_outcome`, `dynamics_params` |

### PredictionRecord
| field | type | tag | notes |
| --- | --- | --- | --- |
| `q_id` | str | D | |
| `producer` | enum{candidate,baseline_name,ablation_id} | D | who produced it |
| `belief_before` | float[2] | D | posterior mean before query (candidate) |
| `selected_action` | str | C,B | the query action |
| `predicted_outcome` | legal-coded | D | model output |
| `actual_outcome` | legal-coded | O | filled by scoring channel only, after prediction |
| `prediction_error` | float | D | computed by scoring; load-bearing for A3 |
| `counterfactual_preds` | dict[action→pred] | D | predictions for non-selected query actions |

### BaselineResult / AblationResult / ReplayResult / LeakageControlResult / HeadroomPreflightResult / FinalResult
| record | key fields | tags |
| --- | --- | --- |
| **BaselineResult** | `baseline_name`, `producer_function`, `legal_inputs`(list of tags it consumed), `id_score`, `ood_score`, `capacity`, `train_consumed`(bool), `provenance` | scores D; `legal_inputs` must contain no H/A/O except `oracle` |
| **AblationResult** | `ablation_id`(A1..A6), `intervention`, `rerun`(must be true), `id_score`, `ood_score`, `delta_vs_candidate`, `expected_direction`, `direction_ok`(bool), `provenance` | D |
| **ReplayResult** | `trajectory_match`(bool, within tol), `query_match`(bool), `recomputed_not_hashed`(must be true), `counterfactual_replay_ok`(bool), `code_path_hash`, `tolerance`, `provenance` | D |
| **LeakageControlResult** | `control_id`(L1..L6), `injected_corruption`, `scanner_fired`(bool), `score_moved_as_expected`(bool), `positive_control_ok`(bool), `provenance` | D |
| **HeadroomPreflightResult** | `strongest_fair_baseline_name`, `strongest_fair_baseline_score`, `oracle_ceiling_score`, `no_update_floor_score`, `headroom`, `band`, `id_negative_control_pass`(bool), `baseline_panel`(list), `verdict`∈{headroom_present,saturated_close,parity_broken_close}, `producer_function`(per score), `provenance` | D |
| **FinalResult** | `verdict`, `candidate_ood_score`, `strongest_fair_ood_score`, `margin`, `band`, `rho_floor_ok`(bool), `ablation_summary`, `replay_summary`, `leakage_summary`, `claim_ceiling`, `failure_manifest_ref`(nullable), `provenance` | D |

**Schema invariant (asserted in tests):** no record reachable by `candidate`/fair-baseline/`amortized_seq`/`replay` may contain a field tagged H, A, or O. Only `scoring`/`oracle` channels may. A schema change that moves a field's tag to make a failure disappear is `blocked_by_schema_alias_leakage` (§15).

---

## 4. Generator design (minimal, non-oracle, OOD)

The generator is the single source of truth and the single highest-risk module (oracle leakage lives here). Keep it minimal.

### 4.1 Hidden latent and action-conditioned outcome
- Per episode, sample hidden `theta ∈ R^2` (`d=2`), e.g. `theta ~ N(0, I)`.
- Action-conditioned outcome function: for action `a` with a fixed (hidden) action vector `phi(a) ∈ R^2`, the latent response is `z = <theta, phi(a)> + drift(t)`. The **observed legal outcome** is a quantized, noisy projection: `outcome = quantize(sigmoid(z) + noise)`, `noise ~ N(0, sigma^2)`, `sigma > 0`.
- **Viability boundary / threshold:** define a hidden boundary `b(theta)` such that the "viable" label flips when `z` crosses a threshold `tau`. The legal `outcome` exposes only the quantized noisy outcome, **not** the boundary label and **not** `z`.
- **Non-oracle requirement (G1):** `truth_outcome` for a query action must **not** be computable from a single `LegalObservation`. It must require integrating multiple probe `(action, outcome)` pairs to estimate `theta`, because a single noisy quantized outcome is insufficient to pin `theta ∈ R^2`. This is the structural defense against the 001B same-step parametric reader. A test (L1/L3) asserts a one-step parametric regressor on a single legal observation cannot exceed the `no_update_floor` by more than `band`.

### 4.2 Train regime vs OOD regime
- **Train regime:** `drift(t)=0` (stationary latent within an episode) OR slow stationary dynamics; `phi(a)` drawn from a "train" family of action geometries; meta-training episodes for `amortized_seq` come only from here.
- **OOD regime:** non-stationary — `theta` drifts within the episode (`drift(t) ≠ 0`), or `phi(a)` is drawn from a held-out geometry family, or the boundary `tau` shifts mid-episode. The shift must be in the **dynamics the online update is designed to track**, not an arbitrary unrelated corruption (Q4 legitimacy). The OOD family is predeclared in `config.py` and frozen.
- Critically, OOD must remain *learnable from the legal probe stream in-context* — otherwise no fair sequence learner could adapt and the test is rigged trickery. The amortized baseline gets the same probe stream; the question is whether explicit PE update beats learned in-context adaptation, not whether the shift is unguessable.

### 4.3 Probe phase, query phase, disjoint actions
- **Probe phase:** `probe_len` steps; agent/baseline observes `(action, outcome)` pairs. Actions drawn from `probe_action_set`.
- **Query phase:** predict `truth_outcome` for `query_action ∈ query_action_set`, where `query_action_set ∩ {actions actually probed in this episode} = ∅`. **Disjointness defeats exact-key memory:** you cannot have stored the answer for an action you never probed; you must generalize via `theta`. (This directly kills `exact_key_memory` as a fair winner.)
- Query context is legal (e.g., the query action id and step index), never the truth.

### 4.4 Stochasticity sufficient to defeat exact memory
- `sigma > 0` and quantization mean a probed `(action,outcome)` is not a deterministic key→value pair; repeated identical actions give varying outcomes. A lookup table over `(action,outcome)` cannot reconstruct `theta` better than a noisy estimator. Set `sigma` so that single-sample outcome entropy is non-trivial but multi-sample averaging recovers `theta` (tuned **before** any candidate run, frozen, `frozen_before_run=true`).

### 4.5 Determinism and ids
- Every random draw flows from `seed`. `episode_id = f"{regime}-{seed}-{idx}"`. Re-running with the same seed reproduces identical episodes (replay precondition). Seed families for train, ID-test, OOD-test, and meta-train are **disjoint** (no train/heldout contamination, L5).

### 4.6 What counts as leakage in the generator (forbidden)
- Surfacing `theta`, `latent_at_t`, `z`, `dynamics_params`, boundary label, `tau`, `pe_truth`, or `truth_outcome` through `legal_view`.
- Any `LegalObservation` field from which `truth_outcome` is a deterministic function (answer-bearing alias).
- `query_action_set` overlapping probed actions (would enable exact memory).
- `sigma=0` or no quantization (would make single-step lookup sufficient → 001B saturation).
- Meta-train seeds overlapping OOD-test seeds (contamination).
- Truth produced by a function reachable from candidate/baseline/replay import graph (isolation break, L4).

---

## 5. Candidate algorithm (specified so Codex does not invent a different one)

The candidate is a **recursive Bayesian / RLS-style online estimator of `theta`**, updated by action-conditioned prediction error, predicting query outcomes from the posterior. No neural net is required or permitted for the candidate (keeps the mechanism inspectable and replayable). Prediction error and action-conditioning must be load-bearing: removing either (A2/A3) must degrade OOD performance.

### 5.1 Required properties
- Recursive update consuming legal `(action, outcome)` pairs one at a time.
- The update step size / gain must depend on the **prediction error** `e_t = outcome_t − predicted_outcome_t(action_t, posterior_{t-1})`. (PE load-bearing.)
- The predicted outcome must depend on the **action** via `phi_hat(action)` (action-conditioning load-bearing). Note: `phi(a)` is hidden in the generator; the candidate must *learn or be given a legal basis* for actions — see §5.3.
- Serialized `CandidateState` contains only `posterior_mean`, `posterior_cov`, counters, last PE — never `theta`, truth, or generator params.
- No access to `generator`, `theta`, query labels, `dynamics_params`, or any O/A/H field.

### 5.2 Pseudocode (normative)
```text
# ---- legal action basis (see 5.3) ----
# ACTION_BASIS[a] : R^2  is a FIXED, LEGAL, episode-independent feature for action a,
#   declared in config.py, identical for candidate AND amortized_seq AND nn baselines.
#   It is NOT the generator's hidden phi(a); it is a public encoding both sides share.

def init_state():
    return CandidateState(
        posterior_mean = zeros(2),
        posterior_cov  = I(2) * PRIOR_VAR,
        n_updates = 0, last_pred_error = 0.0,
        uses_hidden_truth_labels=False, uses_future_observations=False,
        candidate_authored_truth=False,
    )

def predict_outcome(state, action):
    x = ACTION_BASIS[action]                 # legal feature, R^2
    z_hat = dot(state.posterior_mean, x)
    return link(z_hat)                        # same quantize/sigmoid link as legal outcome space

def update(state, action, outcome):           # one legal (action,outcome) pair
    x = ACTION_BASIS[action]
    pred = predict_outcome(state, action)
    e = outcome - pred                         # PREDICTION ERROR (load-bearing)
    # RLS / Kalman-style gain uses covariance and the action feature:
    S = dot(x, state.posterior_cov @ x) + OBS_VAR
    K = (state.posterior_cov @ x) / S          # gain depends on action feature x  (ACTION-COND, load-bearing)
    state.posterior_mean += K * e              # update scaled by PE  (PE load-bearing)
    state.posterior_cov  -= outer(K, x) @ state.posterior_cov
    state.n_updates += 1
    state.last_pred_error = e
    return state

def run_episode(episode_legal_observations):   # probe then query; NO future info
    s = init_state()
    for obs in probe_steps(episode_legal_observations):   # in time order only
        s = update(s, obs.action, obs.outcome)
    serialized = serialize(s)                  # only legal posterior state
    preds = {}
    for q in query_steps(episode_legal_observations):
        s_q = deserialize(serialized)          # replay must reproduce from here
        preds[q.q_id] = {
            "predicted_outcome": predict_outcome(s_q, q.query_action),
            "counterfactual_preds": {a: predict_outcome(s_q, a) for a in q.counterfactual_actions},
            "belief_before": s_q.posterior_mean,
        }
    return serialized, preds
```

### 5.3 The action-basis subtlety (must be predeclared to avoid two failure modes)
- If `ACTION_BASIS` equals the generator's hidden `phi(a)`, that is **oracle leakage** of the generator geometry → forbidden (L4).
- If `ACTION_BASIS` is withheld from baselines but given to the candidate, that is an **unfair advantage** → F1-adjacent rigging → forbidden.
- Rule: `ACTION_BASIS` is a **public, legal, fixed encoding** (e.g., one-hot or a fixed random projection declared in `config.py`) shared identically by `candidate`, `amortized_seq`, and the NN/NN-style baselines. The generator's `phi(a)` is hidden and only correlated with `ACTION_BASIS` through what is learnable from data. A test asserts `ACTION_BASIS` is byte-identical across the candidate and baselines and is not derived from `generator`.

### 5.4 What the candidate must NOT do
- No reading of `truth_outcome`, `theta`, `pe_truth`, `dynamics_params`.
- No use of probe step `t+1..T` when predicting/aggregating step `t` (no future obs).
- No storing per-(action,outcome) raw table that lets it bypass the posterior (that would make it `exact_key_memory`, not a mechanism). Serialized state is the posterior only; a test asserts state size is O(d^2), not O(probe_len).

---

## 6. Baseline panel (each an independent callable)

Every baseline is a top-level callable in `baselines.py` (except `amortized_seq` in its own module). Contract per baseline: `fit(train_episodes_legal) -> model`; `predict(model, episode_legal_observations) -> {q_id: outcome}`. Each declares `legal_inputs` (tag list), `producer_function`, `capacity`, `train_consumed`, `expected_failure_mode`. **`strongest_fair_baseline` is chosen by argmax over `{ood_score}` of all FAIR baselines** (excludes `oracle`).

| baseline | legal inputs | training data | test-time access | capacity / parity | producer_function | expected failure mode | what makes it UNFAIR (forbidden) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `parametric_frozen` | C,B single-step | train-regime fit of a fixed parametric map (the 001B-style reader) | single legal obs, **no online update** | small fixed | `bl_parametric_frozen` | fails OOD (cannot adapt) and fails non-oracle single-step (by §4.1) | giving it the online probe stream as state |
| `amortized_seq` | C,B full probe stream | meta-train over train-regime episodes | **same legal probe stream as candidate** | **≥ candidate capacity (parity, §7)** | `bl_amortized_seq` | should MATCH candidate ID; may or may not match OOD | undertraining; weaker channel; smaller capacity (=F1) |
| `exact_key_memory` | C,B (action,outcome) pairs | memorize probed pairs | lookup by exact action key | unbounded table | `bl_exact_key_memory` | fails: query actions disjoint from probed (§4.3) | letting query actions overlap probed actions |
| `partial_key_memory` | C,B | memorize + nearest action key | approximate lookup | table | `bl_partial_key_memory` | weak: noisy single samples, disjoint actions | reducing sigma to 0 |
| `factorized_lookup` | C,B | per-dimension factor tables | factorized lookup | table | `bl_factorized_lookup` | weak under R^2 coupling | making outcome separable per dim |
| `count_table` | C,B | counts of outcomes per (action bucket) | majority by bucket | table | `bl_count_table` | weak: disjoint query actions, noise | coarse buckets aligned to truth |
| `successor_map` | C,B sequence | learn step→next-outcome map | sequential lookup | table | `bl_successor_map` | weak: not theta-generalizing | exposing latent transition |
| `transition_table` / `graph_lookup` | C,B | (state,action)→outcome graph | graph traversal | table | `bl_transition_table` | weak: states not legal-observable | leaking latent state as node id |
| `fsm_planner` | C,B | induced finite-state machine | plan over induced states | bounded states | `bl_fsm_planner` | weak: continuous theta not FSM-capturable | discretizing on hidden boundary |
| `episodic_traversal` | C,B | store episodes, retrieve nearest episode | retrieve+replay nearest | episode store | `bl_episodic_traversal` | weak: OOD episodes unlike train store | seeding store with OOD episodes |
| `action_conditioned_nearest_neighbor` | C,B | kNN over (probe-summary, action) | nearest-neighbor predict | store + k | `bl_acnn` | medium ID, weaker OOD | distance using hidden theta |
| `sequence_imitation` | C,B | imitate outcome sequence distribution | autoregressive sample | model | `bl_sequence_imitation` | weak: imitates marginal not theta | conditioning on truth |
| `no_update` | C,B | none / prior only | predict from prior, ignore probe | n/a (floor) | `bl_no_update` | defines the FLOOR | accidentally letting it update |
| `oracle` | **O** truth/theta | n/a | reads `theta`/truth | ceiling | `bl_oracle` | defines CEILING, **never fair** | counting it as a fair baseline |

Notes:
- `parametric_frozen` is the explicit 001B re-instantiation — its job is to prove the *non-oracle* property (it must fail single-step) and the *adaptation* property (it must fail OOD). If `parametric_frozen` ties the candidate, the surface is saturated/oracle-leaky → STOP.
- The graph/lookup/table family (`exact_key_memory`…`episodic_traversal`) are the mandatory graph-cache challengers required by the preflight rule in `CLAUDE.md`. They are the "is this just a lookup table" null. They must be present and callable.
- `amortized_seq` is the *only* baseline that should plausibly tie the candidate ID; that is by design (it is the fair learned alternative). Its strength is the whole F1 defense.

---

## 7. `amortized_seq` training protocol (the F1 defense — most important section)

`amortized_seq` is the strongest fair alternative: a learned in-context sequence model that, given the same legal probe stream, predicts query outcomes. If a converged, capacity-matched `amortized_seq` cannot be beaten OOD, the route closes. If it *can* be beaten OOD **and it nonetheless ties the candidate ID**, that is the bounded mechanism signal. The protocol's job is to remove every excuse that the baseline was weak.

### 7.1 Architecture class
- A small sequence model that consumes the ordered probe `(ACTION_BASIS[action], outcome)` pairs and a query action, and outputs a predicted outcome. Allowed: a GRU/LSTM, a small Transformer, or a DeepSets/attention pooler over probe pairs. Implementation may use numpy or a pinned small library; **no external service, no LLM, no pretrained weights** (forbidden paths). If a NN library is used it must actually `fit` (gradient steps that change weights) — a "learned" baseline with no real optimization is the ACSB-001B fake-learner failure (memory `itl-acsb-001b-hostile-audit`) and is a hard block.
- It shares `ACTION_BASIS` with the candidate (§5.3) — equal legal channel.

### 7.2 Capacity parity rule
- Define `candidate_effective_capacity` = number of free parameters the candidate effectively fits (here the `d=2` posterior + covariance ≈ small). The amortized model must have capacity **≥** a predeclared multiple `K_CAP × candidate_effective_capacity`, with `K_CAP ≥ 1` (recommend `K_CAP` large, e.g. the amortized model is strictly higher-capacity). Parity is "baseline at least as powerful," never "baseline throttled down." A `capacity_parity` field records both numbers and `parity_ok = amortized_capacity >= candidate_capacity`.
- If `parity_ok` is false, emit `parity_broken_close` (the baseline was underpowered by construction) — this is an F1 trigger.

### 7.3 Train / validation / test split
- Meta-train episodes: train-regime seeds only. Validation: held-out train-regime seeds (disjoint). ID-test: a third disjoint train-regime seed family. OOD-test: OOD-regime seeds. **All four seed families disjoint** (L5). The amortized model never sees ID-test, OOD-test, or any `theta`/truth.

### 7.4 Convergence criterion (proves "not undertrained")
- Train to a **predeclared convergence criterion**, frozen in `config.py`: validation loss improvement `< CONV_EPS` for `CONV_PATIENCE` consecutive evaluations (plateau), OR max budget reached. Record the full **learning curve** (train loss + val loss per checkpoint) as `parity_report.json::learning_curve`.
- `converged = (val_loss plateaued before max budget)`. If the run hit max budget **without** plateau, `converged=false` → the baseline may be undertrained → emit `parity_broken_close` unless a budget increase (predeclared, not post-hoc) restores convergence. Budget increases after seeing OOD scores are `blocked_by_threshold_tuning`.

### 7.5 Training budget, seeds, early stopping
- Budget (max epochs / steps) predeclared in `config.py`. Early stopping on val plateau (the convergence criterion). Multiple **training seeds** (≥3) for the amortized model; report mean and spread of ID/OOD scores so a single lucky/unlucky init cannot decide the verdict. Use the **median** amortized seed for the headroom comparison, and report the **max** amortized OOD score as the conservative (hardest-to-beat) bar in a sensitivity field.

### 7.6 Artifacts the protocol must emit
- `parity_report.json`: `{candidate_capacity, amortized_capacity, parity_ok, learning_curve:[{step,train_loss,val_loss}], converged, final_val_loss, train_seeds:[...], id_score_per_seed:[...], ood_score_per_seed:[...], id_score_median, ood_score_median, ood_score_max}`.
- These feed Phase 0.

### 7.7 Required terminal conditions (binding)
- **ID negative control (primary F1 detector):** `abs(candidate_id_score − amortized_seq_id_score_median) <= EQUIV_BAND` **must hold**. Interpretation: in-distribution, where the amortized learner has full coverage and no OOD excuse, it must reproduce the candidate's performance. If it cannot, the baseline is underpowered or unfair, and **the run must not claim mechanism evidence**. It must emit `failure_manifest.json` with `blocked_by_underpowered_or_unfair_amortized_baseline` and verdict `parity_broken_close`.
- **Convergence + parity gates:** `converged=true` AND `parity_ok=true` are preconditions for any OOD candidate claim. Either false → `parity_broken_close`.
- **No weakening:** Codex may not reduce `amortized` capacity, shorten its budget, narrow its channel, or remove training seeds to manufacture an OOD gap. Any such change is `blocked_by_codex_success_redefinition` / `blocked_by_underpowered_or_unfair_amortized_baseline`.

> Why ID parity is the right F1 test (designer note): the F1 failure is "candidate wins OOD only because amortized is weak." A weak amortized model is weak everywhere, including ID. By requiring amortized to *tie the candidate ID*, we force it to be genuinely strong; a strong model that then loses OOD is losing for a reason located in the OOD shift, which the ablations then attribute to PE/action-conditioning or refute. ID parity converts "is the baseline strong enough?" from an unfalsifiable judgment call into a measured gate.

---

## 8. Headroom preflight (Phase 0 — runs before any candidate mechanism claim)

Phase 0 reuses the saturation STOP-gate from `DISTRIBUTION-HEADROOM-PREFLIGHT-CONTRACT-001A` verbatim and adds the ID negative control. **`runner.py` must not evaluate the candidate as evidence until Phase 0 returns `headroom_present` AND `id_negative_control_pass=true`.**

### 8.1 Quantities (every one carries a `producer_function`)
- `no_update_floor_score` = `bl_no_update` score (prior-only). Floor.
- `oracle_ceiling_score` = `bl_oracle` score (reads truth). Ceiling.
- `strongest_fair_baseline_score` = `argmax` over OOD scores of all fair baselines (excludes oracle); record which baseline by name (informational only; selection is by number).
- `headroom = oracle_ceiling_score − strongest_fair_baseline_score` (OOD).
- `band = EQUIV_BAND` (frozen).
- `id_negative_control_pass = abs(candidate_id_score − amortized_seq_id_score_median) <= band`.

### 8.2 Verdict logic
```text
# all scores computed by callable baselines/candidate on frozen episodes
if not parity_ok or not converged:
    verdict = "parity_broken_close"           # amortized underpowered/unfair  -> F1 STOP
elif not id_negative_control_pass:
    verdict = "parity_broken_close"           # amortized cannot catch candidate ID -> F1 STOP
elif strongest_fair_baseline_score >= oracle_ceiling_score - band:   # SATURATION rule (contract)
    verdict = "saturated_close"               # no room above strongest fair baseline
elif headroom <= band:
    verdict = "saturated_close"
else:
    verdict = "headroom_present"
emit headroom_preflight.json(verdict, all scores, producer_functions, provenance)
return verdict
```

### 8.3 Exact STOP behavior (binding)
- If OOD `headroom <= band` (or saturation rule trips): **stop before candidate claim**, verdict `saturated_close`, emit `failure_manifest.json::blocked_by_saturated_distribution`. (This is the 001B outcome; it is an honest closure, not a failure to engineer around.)
- If ID negative control fails: **stop**, `parity_broken_close`, `failure_manifest::blocked_by_underpowered_or_unfair_amortized_baseline`.
- If any leakage positive control (§11) fails to fire when run in preflight smoke mode: **stop**, `blocked_by_candidate_truth_or_latent_leakage` / `blocked_by_non_fail_able_control`.
- If `strongest_fair_baseline` is not independently callable (cannot be invoked in isolation in a test): **stop**, `blocked_by_baseline_not_independent`.
- Only `verdict == headroom_present` (with ID parity pass) permits the candidate to be scored as evidence in §14.

### 8.4 Anti-gaming of Phase 0
- The band and all thresholds are frozen `before_run`. Tests assert `threshold_frozen_before_run=true` on every Phase-0 metric.
- `strongest_fair_baseline` selection is `argmax`-by-number; a test (`test_headroom_preflight.py`) feeds a fixture where a non-amortized baseline is strongest and asserts it gets selected, proving selection is not hardwired to a name.
- A **saturated fixture** (generator configured so `parametric_frozen` ties oracle) must return `saturated_close`; a **parity-broken fixture** (amortized capacity throttled) must return `parity_broken_close`. These are required passing tests (§13).

---

## 9. Ablation plan (each ablation RE-RUNS episodes under real intervention)

Every ablation re-executes the full probe→serialize→query loop under a modified mechanism, producing fresh per-case scores. Subtracting a stored number is forbidden (`blocked_by_ablation_not_rerun`). Each emits an `AblationResult` with `rerun=true`, `code_path_hash` of the ablated path, and a `direction_ok` flag.

| id | intervention (code path) | expected direction | terminal failure if not observed | key artifact fields |
| --- | --- | --- | --- | --- |
| **A1 no_update** | replace `update()` with identity (posterior never moves from prior); rerun | OOD score drops toward `no_update_floor` | if A1 ≈ candidate, the update is non-load-bearing → `blocked_by_non_load_bearing_update` | `ablation_id`, `rerun`, `ood_score`, `delta_vs_candidate`, `direction_ok` |
| **A2 no_action_conditioning** | make `predict_outcome` ignore `ACTION_BASIS[action]` (use a constant/averaged feature); rerun | OOD drops if action-conditioning is claimed | if A2 ≈ candidate while action-conditioning is claimed, claim is void → `blocked_by_non_load_bearing_update` (action-cond variant) | same |
| **A3 no_PE_correction** | set the update gain to ignore `e` (e.g. fixed-step update independent of prediction error, or `e:=0`); rerun | OOD drops; this isolates PE | if A3 ≈ candidate, PE is decorative → `blocked_by_non_load_bearing_update` | same |
| **A4 shuffled_labels** | permute `outcome` across probe steps (break action↔outcome correspondence) before update; rerun | OOD drops to floor (no learnable signal) | if A4 ≈ candidate, the model isn't using the legal signal (label-independent) → block | same |
| **A5 shuffled_probe_order** | permute probe step order before update; rerun | mild drop if order/recency matters; small effect tolerated | reported, not auto-terminal (order may legitimately not matter for a stationary estimator); flagged if it *increases* score (suspicious) | same + `note` |
| **A6 frozen_posterior_pre_informative_probes** | freeze posterior at prior until after the first informative probe, then allow update; rerun | intermediate: worse than candidate, better than A1 | if A6 ≈ candidate, early probes carry no information being used → investigate; if A6 > candidate, suspicious | same |

### 9.1 Preventing stored-score replay in ablations
- Ablation runs use the **same generator + seeds** as the main run but a **different mechanism code path**; a test asserts each ablation's `code_path_hash` differs from the candidate's and that ablation predictions are recomputed (not read from the main run's `PredictionRecord`s). The runner must not pass the main run's cached predictions into ablation scoring.
- `direction_ok` is computed by `scoring`, not asserted as a constant. A leakage-style positive control (inject an ablation that secretly calls the real `update`) must be caught by the `code_path_hash` differing-check failing → proves the rerun check is fail-able.

### 9.2 Interpretation gate
- The candidate's OOD advantage is **only** admissible as mechanism evidence if A1/A3/A4 collapse (toward floor) and, if action-conditioning is claimed, A2 collapses. If the advantage survives the ablation that removes the claimed mechanism component, the advantage is coming from something else (capacity, incidental fit) and the mechanism claim is void.

---

## 10. Replay recomputation (strict; not hash compare)

Replay must reconstruct behavior, not confirm stored bytes. This directly answers the ACSB/PROVENANCE failure `hash_only_replay`.

### 10.1 Required replay procedure
1. Load `serialized CandidateState` (posterior only) and the episode's **legal observations**.
2. Re-execute the recursive `update()` from the serialized state's *initial* conditions over the legal probe stream, reproducing the **posterior trajectory** `posterior_mean[t]` for all t.
3. Re-execute `predict_outcome` for every query and reproduce `predicted_outcome` and `counterfactual_preds`.
4. Assert trajectory match within `REPLAY_TOL` (numeric tolerance, frozen) and exact match of discrete predictions.
5. **Counterfactual replay:** re-run on an **ablation action sequence** (e.g., the A2 no-action-conditioning path) and assert the replayed trajectory *differs* where the mechanism says it should — proving replay is sensitive to the mechanism, not a constant.
6. Record `code_path_hash` of the replay update function; assert it equals the candidate's `update` path hash (replay uses the *same* mechanism, not a shortcut).

### 10.2 Forbidden
- Comparing only stored output hashes (`recomputed_not_hashed` must be `true`; a test injects a corrupted serialized state and asserts replay **fails** — proving it actually recomputes).
- Using any future observation or `theta` during replay.
- Replaying from private state not contained in the serialized `CandidateState` (if replay needs something not serialized, that is a trace-causality gap → block).

### 10.3 `ReplayResult` schema
```json
{
  "trajectory_match": true,
  "max_trajectory_abs_error": 0.0,
  "query_match": true,
  "recomputed_not_hashed": true,
  "counterfactual_replay_ok": true,
  "code_path_hash": "<hash of update()>",
  "tolerance": "<REPLAY_TOL>",
  "tamper_control": {"corrupted_state_replay_failed": true},
  "provenance": { "...": "see §12" }
}
```

---

## 11. Leakage scanner and positive controls (L1–L6)

Each control is a **positive control**: it injects a specific corruption and asserts the scanner fires (or the score moves the predicted way). A control that can never fail is itself a failure (`blocked_by_non_fail_able_control`; this is the recurring "whitelist escape / non-fail-able field" defect from memory `itl-gate4-preflight-001b`, `itl-evidence-harness-application-001a`).

| id | injected corruption | scanner mechanism | expected result | terminal failure if positive control does not fire |
| --- | --- | --- | --- | --- |
| **L1 oracle-field leakage** | feed `truth_outcome` into a candidate-visible field | static + runtime check: candidate inputs vs tag set | scanner flags an O/A field in candidate input; candidate score jumps to ≈oracle | if score does **not** jump or scanner silent → `blocked_by_candidate_truth_or_latent_leakage` |
| **L2 hidden-variable leakage** | expose `theta`/`latent_at_t` via a renamed legal key | key-set assertion: emitted keys ⊆ predeclared legal set | scanner flags unexpected key; score may jump | silent pass → block |
| **L3 answer-bearing query label leakage** | make `query_context` a deterministic function of `truth_outcome` | mutual-information / functional-dependence probe between legal field and truth | scanner flags dependence; single-step baseline solves it | if single-step `parametric_frozen` suddenly ties oracle and scanner is silent → block |
| **L4 generator-formula leakage** | import `generator` truth fn into candidate/baseline path | AST / import-graph scan of candidate/baseline/replay modules | scanner flags forbidden import / call edge to `generator` truth producer | reachable `generator` truth producer with silent scanner → block (this is the ACSB "reference path shares target-generation identity" failure) |
| **L5 train/heldout contamination** | overlap meta-train seeds with OOD-test seeds | seed-family disjointness check | scanner flags overlap; amortized OOD score inflates | overlap with silent scanner → block |
| **L6 schema-alias leakage** | rename an H/A field to a `legal_*` name to smuggle it | tag-vs-name consistency check (name claims legal, provenance shows H origin) | scanner flags alias | silent pass → block (`blocked_by_schema_alias_leakage`) |

### 11.1 Scanner construction rules
- The scanner runs on **both** a clean run (must report no leak, all controls green) and each injected run (must fire). A scanner that reports "clean" unconditionally is invalid; `test_leakage_positive_controls.py` asserts every Li fires on its injected fixture and is silent on clean.
- Scanner result feeds Phase 0 smoke (§8.3): if any positive control fails to fire during preflight, STOP before candidate claim.
- The scanner must itself be fail-able: a meta-test feeds the scanner a known-leaky input and asserts a non-zero exit / `scanner_fired=true`. (Defends against the `leakage_scanner_not_fail_able` block in memory `itl-post-bridge-001c`.)

---

## 12. Artifact schema (machine-readable; no artifact = no evidence)

All under `artifacts/acolb_001a/`. Natural-language summaries are not evidence.

Required files:
```text
headroom_preflight.json     # §8 HeadroomPreflightResult (always emitted, even on STOP)
result.json                 # FinalResult (§3); includes claim_ceiling field
trace.jsonl                 # one row per (episode, step/query): see 12.1
baseline_comparison.json    # per-baseline id/ood scores + provenance + argmax selection
ablation_report.json        # A1..A6 AblationResults
replay_report.json          # ReplayResult (§10.3)
leakage_report.json         # L1..L6 LeakageControlResults (clean + injected)
parity_report.json          # §7.6 (learning curve, capacity, convergence, per-seed)
failure_manifest.json       # emitted on ANY stop/gate failure; preserved, never deleted
claim_ceiling.txt           # the §0 ceiling text, byte-copied
```

### 12.1 `trace.jsonl` per-row fields (mechanism trace, supports replay)
```text
episode_id, t, regime, action, belief_before(posterior_mean), predicted_outcome,
actual_outcome, prediction_error, belief_after(posterior_mean), n_updates,
counterfactual_action_preds, code_path_hash
# query rows additionally: q_id, query_action, query_context(legal), predicted_outcome, actual_outcome
# NO theta, latent_at_t, pe_truth, truth_producer, dynamics_params in trace
```

### 12.2 Per-score provenance block (reused from `COMPUTED-EVIDENCE-PROVENANCE-CONTRACT-001A` §6)
Every score in every artifact (baseline, candidate, ablation, replay, leakage, headroom) embeds:
```text
metric_id, metric_name, producer_function, producer_module, code_path_hash,
run_id, seed (or seed_ids), episode_ids, train_context_ids_consumed,
heldout_context_ids_consumed, counterfactual_pair_ids_consumed,
input_artifact_paths, input_artifact_hashes, input_row_count,
output_artifact_path, output_row_ids, aggregation_rule,
threshold_used, threshold_frozen_before_run,
computed_not_literal(true), failure_path_available(true)
```
`computed_not_literal` and `failure_path_available` must be `true`; a field that is not applicable must say *why* (omission ≠ N/A). A score whose provenance cannot point to a callable producer is invalid evidence (`blocked_by_provenance_gap`).

### 12.3 Preservation rule
Failure artifacts are preserved, never patched into passes, never deleted (operating contract). A run that STOPs still emits `headroom_preflight.json` + `failure_manifest.json` + `claim_ceiling.txt`.

---

## 13. Test plan (pytest, including failure-path tests)

Tests assert **computation paths and discriminative failure**, not artifact verdicts (the `tests_asserting_pass` failure). Required tests:

- `test_generator.py`
  - determinism: same seed → identical episodes; seed families disjoint.
  - non-oracle: a one-step parametric regressor on a single `LegalObservation` cannot exceed `no_update_floor + band` (G1).
  - disjointness: `query_action_set ∩ probed_actions == ∅`.
- `test_legal_channel_isolation.py`
  - emitted legal keys == predeclared set; no `theta/latent/pe_truth/truth/dynamics` key reachable.
  - `generator` truth producer not importable from candidate/baseline/replay modules (import-graph assert, L4).
- `test_candidate_update.py`
  - PE load-bearing: zeroing `e` changes outputs (sanity that A3 will bite).
  - action-conditioning load-bearing: constant `ACTION_BASIS` changes outputs.
  - serialized state size O(d^2), not O(probe_len) (not a hidden lookup table).
  - no future obs: predicting query at t uses only ≤t probe rows.
- `test_baselines_independent.py`
  - every baseline callable in isolation (`fit`/`predict`) with only its declared legal inputs; `oracle` excluded from fair set.
  - `exact_key_memory` fails on disjoint query actions (sanity of the null).
- `test_amortized_convergence.py`
  - learning curve is recorded and val loss decreases then plateaus on a fixture; `converged` computed, not hardcoded.
  - capacity parity computed; `parity_ok` reflects real param counts.
  - **failure-path:** a throttled-capacity fixture yields `parity_ok=false`.
- `test_headroom_preflight.py`
  - **saturated fixture** → `saturated_close`.
  - **ID-parity-broken fixture** (underpowered amortized) → `parity_broken_close`.
  - `strongest_fair_baseline` selected by argmax: a fixture where a non-amortized baseline is strongest → that baseline is selected (not name-hardwired).
  - candidate evaluation is **not reached** unless verdict `headroom_present` and ID parity pass (assert runner short-circuits).
- `test_ablations_rerun.py`
  - each ablation's `code_path_hash` ≠ candidate's; predictions recomputed (not read from main run).
  - **failure-path:** an ablation that secretly calls real `update` is caught (hash-equal → fail).
  - A1/A3/A4 drop toward floor on a mechanism-present fixture.
- `test_replay_recompute.py`
  - replay reproduces posterior trajectory + query preds within tol.
  - **failure-path:** corrupted serialized state → replay fails (proves recompute, not hash compare).
  - counterfactual replay on ablation action sequence diverges as expected.
- `test_leakage_positive_controls.py`
  - each L1..L6 fires on its injected fixture and is silent on clean.
  - scanner meta-test: known-leaky input → scanner fires (scanner is fail-able).
- `test_runner_stop_paths.py`
  - on saturated → `failure_manifest::blocked_by_saturated_distribution`, no mechanism claim.
  - on parity-broken → `blocked_by_underpowered_or_unfair_amortized_baseline`.
  - on leakage-not-firing → block.
  - `failure_manifest.json` emitted on every stop; `result.json` verdict never contradicts an emitted failure manifest.
  - no forbidden path is written (assert artifact writes confined to `artifacts/acolb_001a/`).
- `test_provenance.py`
  - every emitted score has a provenance block with a resolvable `producer_function` and `code_path_hash`; `computed_not_literal=true`; a literal-constant score is rejected by the provenance validator (failure-path).

---

## 14. Acceptance gate for future Codex implementation (exact)

A future ACOLB-001A run may claim *bounded mechanism-discrimination evidence* (no stronger — see ceiling) **only if all of the following hold**, each backed by a machine-readable artifact:

1. **Phase 0 = `headroom_present`** (OOD `headroom > band`, saturation rule not tripped).
2. **ID negative control passes:** `abs(candidate_id − amortized_seq_id_median) <= band`, with `converged=true` and `parity_ok=true`.
3. **OOD margin:** `candidate_ood − strongest_fair_ood > OOD_BAND` (strongest fair = argmax, by number; includes the converged `amortized_seq`).
4. **Mechanism floor:** `candidate_ood − no_update_floor >= RHO × (oracle_ceiling − no_update_floor)` (the advantage is a meaningful fraction of the available room, not a sliver).
5. **Ablations:** A1, A3, A4 collapse toward floor as predicted; A2 collapses **if** action-conditioning is claimed. `direction_ok=true` for each, computed by scoring.
6. **Replay:** recomputes posterior trajectory and query predictions within tol; tamper control fails on corrupted state; counterfactual replay diverges as expected; `recomputed_not_hashed=true`.
7. **Leakage:** all L1–L6 positive controls fire; clean run reports no leak; scanner is fail-able.
8. **Baselines:** every baseline independently callable; `oracle` excluded from fair selection.
9. **Provenance:** every score has a resolvable producer + `code_path_hash`; `computed_not_literal=true`, `failure_path_available=true`; thresholds `frozen_before_run`.
10. **No forbidden path touched; no remote anchor; no weakening of `amortized_seq`.**

If **any** fail → no mechanism claim; emit `failure_manifest.json` with the matching blocker (§15); verdict is the corresponding `*_close` / `blocked_*`. **OOD baseline failure is never, by itself, mechanism evidence** — it is admissible only jointly with conditions 1–9.

---

## 15. Stop conditions (terminal blockers)

Any of these → STOP, emit `failure_manifest.json`, preserve artifacts, make no mechanism claim. (A blocker is terminal; it may not be downgraded to a warning.)

```text
blocked_by_saturated_distribution                  # OOD headroom <= band (001B outcome)
blocked_by_underpowered_or_unfair_amortized_baseline   # ID parity fails / not converged / parity_ok false  (F1)
blocked_by_candidate_truth_or_latent_leakage       # L1/L2 fires uncaught, or candidate reads O/A/H
blocked_by_non_load_bearing_update                 # A1/A2/A3 does not drop -> mechanism decorative
blocked_by_replay_hash_only                        # replay compares hashes instead of recomputing
blocked_by_ablation_not_rerun                      # ablation reuses cached scores / same code_path_hash
blocked_by_baseline_not_independent                # strongest fair baseline not callable in isolation
blocked_by_codex_success_redefinition              # success criteria / band / gate changed by implementer
# supporting blockers:
blocked_by_threshold_tuning                        # any threshold changed after seeing scores
blocked_by_schema_alias_leakage                    # H/A field renamed to legal_*
blocked_by_non_fail_able_control                   # a leakage/ablation control cannot fail
blocked_by_provenance_gap                          # score with no callable producer / literal constant
blocked_by_forbidden_path                          # wrote outside src|tests|artifacts/acolb_001a
blocked_by_remote_anchor                           # any push/tag/remote-anchor attempt
blocked_by_governance_self_modification            # implementation edited this blueprint / contracts / bands
```

Auto-Remote-Anchor: **forbidden** (restated). Any anchoring is a separate human step.

---

## 16. Codex implementation card (bounded; the only authorization this blueprint emits)

```yaml
task_id: ACOLB-001A-IMPL-001A
parent_blueprint: ACOLB-001A-IMPLEMENTATION-BLUEPRINT-AUDIT   # this document, read-only
task_type: bounded mechanism-surface implementation (engineering + mechanism-hypothesis)
layer: engineering implementation + mechanism hypothesis testing   # NOT subjectivity/consciousness
role: implementer   # NOT designer, NOT hostile auditor (role separation, contract)

problem_definition: >
  Implement the ACOLB-001A online action-conditioned prediction-error belief-update
  surface exactly as specified in the parent blueprint, such that the F1 risk
  (OOD gap from an underpowered/unfair amortized baseline) is observable and terminal
  via Phase-0 ID negative control + convergence/parity gates, before any mechanism claim.

current_stage: pre-implementation (no src/tests/artifacts for acolb_001a exist yet)

hypothesis: >
  On the specified OOD generator, a recursive action-conditioned PE update will be
  non-equivalent to the strongest fair baseline (incl. converged amortized_seq) beyond
  OOD_BAND, while passing the in-distribution parity negative control and load-bearing ablations.
  Null/expected-honest outcome: amortized_seq ties OOD -> saturated_close (route closes).

baseline: full panel in blueprint §6; strongest fair = argmax (by number); oracle = ceiling only.
ablation: A1..A6 as real reruns (§9).
trace_replay_requirement: trace.jsonl (§12.1) + recompute-from-serialized-state replay (§10), not hash compare.

acceptance_gate: blueprint §14 (all 10 conditions, artifact-backed).
claim_ceiling: >
  bounded offline mechanism-discrimination evidence on this generator/seeds/band only.
  No consciousness, subjectivity, emotion, agency, autonomy, AGI, companion/EGO readiness,
  stable user benefit, or proof of any total theory.

allowed_paths:
  - src/acolb_001a/**
  - tests/acolb_001a/**
  - artifacts/acolb_001a/**
forbidden_paths:
  - any prior surface (src/acp_bv_*, src/acsb_*, etc.), ego_mainline/runtime/bridge/scheduler/admission
  - companion/product/LLM/RAG/AIRI, global schemas, docs/** rule sources (read-only), push/tag/remote-anchor scripts
  - this blueprint and the cited contracts (read-only rule sources)

hard_blockers (any -> STOP + failure_manifest.json, no mechanism claim):
  - blocked_by_saturated_distribution
  - blocked_by_underpowered_or_unfair_amortized_baseline
  - blocked_by_candidate_truth_or_latent_leakage
  - blocked_by_non_load_bearing_update
  - blocked_by_replay_hash_only
  - blocked_by_ablation_not_rerun
  - blocked_by_baseline_not_independent
  - blocked_by_codex_success_redefinition
  - blocked_by_threshold_tuning / schema_alias_leakage / non_fail_able_control / provenance_gap
  - blocked_by_forbidden_path / remote_anchor / governance_self_modification

prohibitions:
  - do NOT weaken amortized_seq (capacity, budget, channel, seeds)
  - do NOT remove or relax the ID negative control
  - do NOT skip Phase 0 or run candidate-as-evidence before headroom_present + ID parity pass
  - do NOT replace a failure with a warning; do NOT patch failures into passes
  - do NOT change bands/thresholds after seeing scores
  - do NOT edit the blueprint, contracts, or governance files
  - Auto-Remote-Anchor: FORBIDDEN (no push, no tag, no remote anchor)

stop_condition: emit failure_manifest.json on first hard blocker; preserve all artifacts; stop.
rollback_plan: >
  All work confined to the three allowed paths. Rollback = delete src/acolb_001a, tests/acolb_001a,
  artifacts/acolb_001a (no other path touched; no schema/global change to revert). No remote state created.

required_final_report (implementer):
  verdict, layer, files_changed, commands_run, tests_run, artifacts_generated,
  baseline_results, ablation_results, replay_result, leakage_results, headroom_verdict,
  stop_conditions_triggered, claim_ceiling, what_this_does_not_prove, remaining_unknowns

next_role_after_implementation: hostile auditor (separate pass) re-runs + tampers vs this frozen blueprint.
```

---

## Self-audit of this blueprint against the task's own accept/reject gate

**Accept-if items (task card) — all present:**

- concrete module tree → §1; function-level plan → §2; data schemas → §3; candidate pseudocode → §5.2; baseline callable contracts → §6 (table) + §5.2 style; amortized_seq training protocol → §7; headroom preflight logic → §8.2; ablation rerun logic → §9 + §9.1; replay recomputation logic → §10; leakage positive controls → §11; artifact schemas → §12; pytest plan → §13; terminal blockers → §15; one Codex implementation card → §16.

**Reject-if items (task card) — checked clear:**

- *Mostly repeats theory?* No — every section emits code-level constraints, schemas, or gates.
- *Does not constrain Codex?* §1 path whitelist, §15 blockers, §16 prohibitions, §7.7 no-weakening.
- *Fails to make F1 observable?* F1 is the spine: §0.5 analysis, §7 ID negative control + convergence/parity, §8 Phase-0 STOP, §14 condition 2. Smallest-observable core named in §0.5 Q5.
- *Treats OOD baseline failure as automatic mechanism evidence?* Explicitly forbidden — §14 closing line, §0.5 Q2; OOD margin is admissible only with conditions 1–9.
- *Lacks ID negative control?* Present and primary (§7.7, §8, §14.2).
- *Allows implementation without Phase 0?* No — §8.3 + §13 `test_headroom_preflight` assert candidate-as-evidence unreachable without `headroom_present` + ID parity.
- *Lacks failure manifests?* §12 + §15 require `failure_manifest.json` on every stop.
- *Allows remote anchor?* Forbidden in §1, §15, §16 (restated 3×).

**Residual gaps / unknowns (honest):**

1. **Design file absence (fact).** `GATE0-5-FEASIBLE-MECHANISM-SURFACE-DESIGN-001A.md` does not exist; this blueprint substitutes for it but must be frozen as the rule source before Codex starts, else the implementer could become its own designer (role-separation violation).
2. **N=1 governance inheritance (fact).** The saturation STOP-gate is N=1-derived (per the contract's own disclaimer). ID-parity + convergence are designed mitigations of F1, but their *sufficiency* is itself an untested assumption until a run exercises the parity-broken and saturated fixtures.
3. **Generator realizability (unknown).** Whether a generator can simultaneously satisfy (a) non-oracle single-step, (b) OOD learnable in-context by amortized_seq, and (c) candidate ID-parity with amortized — without a region where the surface is trivially saturated — is an empirical open question. If no such region exists, the honest outcome is `saturated_close` / route downgrade to Route B. This blueprint does not assume such a region exists; it builds the instrument that would reveal its absence.
4. **`OOD_BAND` / `RHO` values left symbolic.** They must be frozen in `config.py` before any run with a predeclared rationale; this document deliberately does not pick numbers post-hoc.

---

## Final report (this Claude task)

- **Verdict:** blueprint delivered; accept-gate satisfied; F1 made observable and terminal via Phase-0 ID negative control + convergence/parity gates + argmax selection + load-bearing ablations.
- **Research layer:** engineering implementation + mechanism-hypothesis *design* (no execution, no evidence).
- **Files changed:** none in the repo. Deliverable written to the session scratchpad only (`ACOLB-001A-IMPLEMENTATION-BLUEPRINT-AUDIT.md`), honoring the task's "do not write repo files." Placing it at `docs/research/` or `docs/codex/tasks/` requires a separate authorization.
- **Commands run:** read-only repo survey (`ls`, `find`, `grep`, `cat`) to ground the blueprint and cite prior negative evidence.
- **Artifacts generated:** this blueprint document. No experiment artifacts (none authorized).
- **Prior negative evidence cited:** ACP-BV 001B saturation closure; DISTRIBUTION-HEADROOM-PREFLIGHT-CONTRACT-001A; ACSB downgrade collapse family; COMPUTED-EVIDENCE-PROVENANCE-CONTRACT-001A; NEXT-MECHANISM-SURFACE-ROUTE-DECISION-001A 8 gates.
- **Stop conditions triggered:** none (this is a design task; nothing executed).
- **Claim ceiling:** implementation blueprint only. No mechanism evidence, no Gate pass, no mainline effect, no live readiness, no agency, autonomy, consciousness, emotion, stable user benefit, or EGO readiness.
- **What this does not prove:** it does not show ACOLB-001A is implementable into a *passing* surface; it does not show a discriminating generator exists; it does not validate the mechanism, the candidate, or any total theory; it does not authorize execution beyond the §16 card.
- **Remaining unknowns:** the four residual gaps above (design-file freeze, N=1 sufficiency of the F1 mitigations, generator realizability, band/RHO selection).
