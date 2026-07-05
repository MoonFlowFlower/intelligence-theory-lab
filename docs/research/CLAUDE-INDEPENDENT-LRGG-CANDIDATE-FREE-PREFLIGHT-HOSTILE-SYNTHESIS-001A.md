# CLAUDE-INDEPENDENT — LRGG Candidate-Free Preflight Hostile Synthesis 001A

Task ID: `LRGG-CANDIDATE-FREE-PREFLIGHT-HOSTILE-SYNTHESIS-001A`
Role: independent hostile synthesis reviewer (not praise reviewer, mechanism advocate,
implementation assistant, or route-completion assistant).
Status: research synthesis / method-evidence review. NOT a task card. Authorizes no
implementation. Reviewer did not run training, did not modify mechanism code, did not anchor
remotely.
Input under review: uploaded Deep Research benchmark scan
`EGO Benchmark Method Scan for Mechanism-Discriminative Testbed Redesign`.

---

## 1. Executive verdict

**Verdict: `partial_accept_requires_narrow_repair`.**

Short reason: The Deep Research (DR) scan selects the correct route and is usable as
*method evidence*, but it is not yet a contract. Its strongest proposal — the **latent rule
graph gridworld (LRGG)** — converges with the lab's own prior synthesis
(`BENCHMARK-METHODOLOGY-APPLICABILITY-001A`, pattern **P2 = Alchemy known-latent +
ideal-observer bound, named there as "the most valuable for this lab"`). That independent
convergence raises confidence in the *direction*. But the scan (a) does not cite or build on
the lab's existing negative lineage, (b) omits the single baseline most likely to collapse
the route — a capable **fitted cross-episode amortized / ideal-observer-approximating**
learner — which is precisely the standing collapse mode (`K2`), (c) defines "candidate-free
headroom" in a way still contaminated by the underpowered-learner ambiguity that invalidated
TLGP-001B-R2, (d) smuggles a **self/boundary-signal channel** into its ablation matrix, which
is scope creep into the *closed-negative* self-state route, and (e) re-invents stop/accept
thresholds instead of binding to the already-canonical
`BASELINE-IMMUNITY-ADMISSION-STANDARD-001A`.

This is **not** mechanism evidence. It is a benchmark-method scan that can support drafting a
*candidate-free preflight card* once a bounded, enumerable set of repairs (Section 4) is
encoded into that card. The route is correct; the contract is not yet written.

Honest prior to update on (the scan does not): the **immediately preceding** candidate-free
environment-headroom harness, `BASELINE-FIRST-HARNESS-001A-R1`, closed
`rejected_no_headroom_baseline_saturated` — strongest fair baseline = oracle = 1.0, margin
0.0, all six graph-cache challengers = 1.0. The most probable honest outcome of building LRGG
correctly is *another bounded no-headroom negative*. That is the contract-preferred answer,
not a failure to patch around.

---

## 2. Current status report (repeated as required)

- **Current layer:** mechanism-hypothesis / benchmark-method scan hostile synthesis
  (engineering-governance, Phase-0 environment-redesign). No mechanism, candidate, or
  subjectivity layer is entered.
- **Mainline integration status:** none. No EGO runtime, mainline, admission, bridge,
  product behavior, or agent capability is integrated or touched.
- **Enabled status:** none. No runtime/admission/bridge path enabled.
- **Real trigger evidence (independently spot-checked):**
  - TLGP-001B-R2 official full run banked locally as **bounded INVALID**; scientific verdict
    `tlgp001b_r2_invalid_learnability_floor_failed`.
  - B3-only independent re-audit accepted:
    `accept_b3_agents_cleanup__official_bundle_bankable_as_bounded_invalid`.
  - Bank record repo-preserved at commit `5c03e0af7ce097d9055de5f1ef17052fe3a576be`
    — **verified**: local `git log` HEAD is `5c03e0a "docs: preserve TLGP-001B-R2 bounded
    invalid bank record"`. Provenance claim corroborated, not merely asserted.
  - Trace via Git LFS pointer OID `sha256:f9d5f47854b91cc107230a2335b12c8c43dad6ffc82b34a2dee0da708ab6c0fd`
    (pointer cited as-stated; LFS object content not re-fetched in this review — out of scope).
  - Uploaded DR scan proposes a candidate-free latent-structure benchmark direction, top pick
    = latent rule graph gridworld.
- **Claim ceiling (binding):** the strongest possible positive conclusion is only —
  *"The Deep Research benchmark scan is sufficient to support a bounded candidate-free
  preflight card for a latent-structure testbed, pending explicit baseline, leakage, replay,
  provenance, and capability-witness constraints."* This proves nothing about consciousness,
  subjectivity, emotion, self, agency, autonomy, intelligence, EGO/companion/runtime
  readiness, mainline effect, H0, H1, 001A downgrade, 001C authorization, TLGP-001B-R2
  reinterpretation, or mechanism-candidate validity.
- **Next minimal closed-loop action:** see Section 12.10.

### 2.1 R2 interpretation discipline (re-affirmed, not re-litigated)

R2 failed because the chosen primary meta-learners, under frozen prereg/codepath/budget/grid/
seeds, failed the **Rung0 learnability-floor capability witness** before Rung3 could
adjudicate. Correct reading: *the adjudication path was invalidated*. Forbidden readings: H0,
H1, theory failure, 001A downgrade, "headroom survives capable meta-learners",
"learning-as-mechanism", or 001C authorization. This review does not reinterpret R2; it
treats R2 as the reason a **capability witness redesign** (Section 6) is mandatory.

---

## 3. Best proposal selection

The DR scan offers three candidate-free targets. Judged on oracle solvability, cheap-baseline
resistance, structural-heldout quality, implementation cost, replay/provenance simplicity,
leakage-control feasibility, diagnostic clarity, fit to EGO mechanism variables, and risk of
collapsing into a behavior-only benchmark:

| Criterion | (1) Latent rule graph gridworld | (2) Counterfactual memory / latent-context | (3) Causal object-manipulation micro-world |
|---|---|---|---|
| Oracle solvability | High (generator-aware planner) | High (Bayes/DP on reduced cases) | Medium (planner/search; cost grows) |
| Cheap-baseline resistance | High **iff** per-episode resample + non-obs-decodable remap | Medium (short-horizon decode risk) | Medium (appearance-reveals-affordance risk) |
| Structural heldout quality | High (rule/remap/composition families) | Medium (horizon/noise/cue split) | High (causal-factor families) |
| Implementation cost | **Lowest** | Low–Medium | Medium–High |
| Replay/provenance simplicity | High (serialize graph+remap+state+actions) | High | Medium |
| Leakage-control feasibility | High (inject graph/ID as positive control) | High | Medium |
| Diagnostic clarity | **Highest** for the 5 tombstone-failures driving the redesign | Medium (memory-only) | Medium (causal-only, behavior-heavy) |
| Fit to EGO mechanism variables | Strong (online latent inference) | Partial (memory axis) | Partial (causal axis) |
| Behavior-only collapse risk | Low (if metric requires online inference) | Medium | **Higher** (robotics-flavored) |

**Selection: (1) latent rule graph gridworld**, in agreement with the DR scan and with the
lab's existing `BENCHMARK-METHODOLOGY-APPLICABILITY-001A` (steal P1 train/test gap + P2
known-latent/ideal-observer-bound into a *minimal* world with the lab gate bolted on).
Proposal (2) is the right **secondary** memory-axis probe (POPGym P3); proposal (3) is
deferred (engineering cost + the "observation almost reveals affordance" failure is the same
K1 risk with worse instrumentation).

**Critical scope correction to the selection.** LRGG is admissible **only as a
structure-learning / latent-inference (Track 1.1 learning-axis) preflight**, the same axis as
TLGP and `BASELINE-FIRST-HARNESS`. It is **not** the self-state / grounded-latent route. The
DR scan's ablation matrix includes a *"corrupted boundary signal / self-signal"* row; this is
scope creep into the **closed-negative** self-state route
(`SELF-BOUNDARY-INTERVENABLE-LATENT-NEGATIVE-LINEAGE-AND-KILLER-CATALOG-001A`;
`GROUNDING-GATE-...-CLOSEOUT-001A`, co-binding non-identifiable). Per
`BENCHMARK-METHODOLOGY-APPLICABILITY-001A §5`: Alchemy-style worlds satisfy **K1 by
construction** for *structure learning*, but are **not a K2 escape for self**. The
self/boundary channel must be **struck** from the LRGG preflight (Section 4, R3).

---

## 4. Required repairs before Codex (bounded, enumerable)

These are the conditions the preflight card must encode. They are narrow: most are *bindings*
to existing lab contracts, plus one missing baseline, one metric definition, and one
deletion.

- **R1 — Add the missing collapse-mode baseline.** Add a **fitted cross-episode amortized /
  ideal-observer-approximating learner** as a *first-class required fair baseline* (not an
  afterthought). This is the standing collapse mode (`K2`; ACOLB-A `online ≡ amortized
  discounted-LS`; Alchemy §5 "K2 remains"; TLGP memory flag: cross-episode meta-learner =
  "most likely collapse point"). The DR baseline matrix omits it. Also add **trajectory
  nearest-neighbor retrieval** (required by the task; absent from the DR matrix).
- **R2 — Define headroom honestly and make it budget-robust.** "Candidate-free headroom" must
  be `oracle − max(fair-panel including the amortized/meta-learner)`, never
  `oracle − weak-baseline` and never `interventional − observational` (K2). Headroom is only
  admissible if it is **stable under a budget/power requirement** (a pre-registered
  budget-robustness check on the debug split), because the R2-mirror failure
  (`small_data_underestimation_separation`, discovery-loop lineage) makes an apparent gap a
  false positive when the fair learner is under-resourced. A gap that disappears as fair
  budget grows is **not headroom**.
- **R3 — Strike the self/boundary scope creep.** Remove the "corrupted boundary signal /
  self-signal" ablation and any self-state framing. LRGG stays a structure-learning preflight.
  Re-opening the self route requires its own card that answers K1+K2 point-by-point
  (per killer-catalog §4) and is contract-disfavored absent new evidence.
- **R4 — Bind to the canonical admission standard, do not re-invent.** Stop/accept verdicts
  must use the existing registry in
  `docs/codex/contracts/BASELINE-IMMUNITY-ADMISSION-STANDARD-001A(.registry.json)`:
  `{admissible_for_candidate_preflight, rejected_metric_degenerate, rejected_no_fair_signal,
  rejected_trivially_decodable, rejected_baseline_saturated, blocked_pending_canonical_readback}`.
  The value-level attacker family `{mean, variance, correlation, PCA, cross-episode,
  supervised, membership}` gated on `family_max` is mandatory for K1 (Route C preflight
  `726f26d`→repair `278819a`).
- **R5 — Classify and constrain the oracle.** The "generator-aware planner over latent graph"
  must be a **`mechanism_oracle`** that *estimates the non-read latent* such that a
  non-reading oracle scores 0 (fail-able), per the standard's identifiability clause. If the
  oracle simply reads generator truth it is an `answer_key_oracle` and `oracle − fair` is
  meaningless. Demonstrate **genuine residual uncertainty** via a twin-pair construction:
  pairs indistinguishable under passive `P(X)` but separable under `do(·)`.
- **R6 — Operationalize the decodability↔solvability window.** The scan asserts a window
  exists ("retain nontrivial but sub-ceiling performance") but cannot show it is non-empty.
  The card must make this an *outcome to be tested*, with explicit K1 obs-decodability ceiling
  and the R2-style learnability floor as the two walls, and must pre-commit that an empty
  window → `rejected_baseline_saturated` (too decodable) or `INVALID` (unlearnable), not a
  patch.
- **R7 — Define inherited labels.** The DR scan uses tombstone labels A–G without definition.
  The card must define each tombstone → environment property → measurable gate, or drop the
  labels. Inherited undefined literals are a recurring lab anti-pattern.

If R1–R7 are encoded, the scan supports a candidate-free preflight card. None of R1–R7
requires a different route or a re-scan; hence `partial_accept`, not `reject`.

---

## 5. Strongest false explanations (attack surface for the LRGG)

Ranked by how likely each is to manufacture *fake headroom* in this specific environment,
each tagged with the prior anchor showing it has bitten the lab before.

1. **Amortized / ideal-observer saturation (highest risk).** A capable fitted cross-episode
   learner approximates the Bayesian observer and closes `oracle − fair` to within band →
   `rejected_baseline_saturated`. Standing mode: ACOLB-A (`online ≡ discounted-LS`, margin
   0.0147), Alchemy §5 ("K2 remains"). **Controlled only by R1.**
2. **Graph-cache / lookup saturation.** A finite latent-graph cache memorizes transitions and
   saturates if episodes reuse graphs or the heldout is seed-only. Exactly what closed
   `BASELINE-FIRST-HARNESS-001A-R1` (six graph-cache challengers all 1.0). **Controlled by
   per-episode resampling + structural (not seed) heldout + R6.**
3. **Obs-only latent decoding (K1).** Per-episode perceptual remapping that is decodable from
   current obs + short history → obs-only == oracle. ACSB killer (`d5b4b92`,
   `phase XOR action` lived in the observation). **Controlled by R4 value-level attacker
   family + R5 twin-pair + R6 ceiling.**
4. **Metric degeneracy / single-sided (K3).** Recall-only or unbounded prediction-set →
   `predict_all` recall = 1.0 = oracle. Route C separation probe false positive; codified as
   `rejected_metric_degenerate`. **Controlled by R4 balanced metric + triviality probe.**
5. **Structural heldout secretly seed-only.** If test rule-families share generative
   parameters with train, nearest-neighbor retrieval wins. **Controlled by R1 (NN baseline) +
   a family-disjointness criterion in R6.**
6. **Underpowered learner causing false invalidation (R2-mirror) / false separation.**
   Under-budgeted fair learner makes a gap appear (false headroom) or makes the env look
   unlearnable (false INVALID). `small_data_underestimation_separation`. **Controlled by R2
   budget-robustness.**
7. **Finite-state exhaustive probing.** A small/enumerable world is solved by exhaustive legal
   query == oracle. Baseline-immunity `budget_faithful_visible_channel_oracle` saturation.
   **Controlled by minimum task-space entropy requirement (Section 7).**
8. **Short-history / n-gram shortcut.** k-step cache matches the recurrent candidate.
   **Controlled by horizon design + n-gram baseline in panel.**
9. **Candidate/truth coupling & generator-truth leakage.** Generator and scorer share a
   module so the "candidate" imports the answer. **Controlled by Section 8 import-path audit +
   Section 9 separate producer hashes.**
10. **Hidden task-ID / generator-field leakage.** Meta-World-style one-hot task ID in the
    observation short-circuits inference. **Controlled by observation-field audit + positive
    control.**
11. **Reward-shaping exploitation.** Shaping signal optimizable without latent inference.
    **Controlled by shaping-on-legal-progress-only + a shaping-only baseline that must fail.**
12. **Replay not actually recomputing score.** Stored JSON score reused instead of recomputed
    from serialized state + actions. **Controlled by Section 9 replay contract + tamper probe.**
13. **Post-hoc ablation (score edit not rerun) / threshold tuning after results.** K5 /
    baseline-immunity `post-hoc threshold-optimizer`. **Controlled by frozen thresholds
    pre-registration + ablation-as-true-rerun.**

---

## 6. Required baseline family (minimum, before any candidate enters)

For each baseline: false explanation it controls / fair access / forbidden access / result
that blocks the route. This extends the DR matrix with the missing rows (★) and binds to K2.

| Baseline | False explanation controlled | Fair access | Forbidden access | Blocking result |
|---|---|---|---|---|
| Random | Score is shaping noise | Legal obs+actions | latent, keys, task IDs | near-candidate score |
| Majority / mode | class/action imbalance | observation only | history, latent | near-candidate score |
| Obs-only predictor | hidden state not needed | current obs only | history, cache | high heldout score |
| Memoryless policy | dynamics solved reflexively | current obs+reward | sequence history | high heldout score |
| Lookup table | small-state memorization | train trajectories/visited states | generator latent | saturates in-distribution |
| Graph-cache | finite latent-graph memorization | past observed transitions | generator truth graph | saturates seed-only heldout |
| n-gram / short-history cache | short-history shortcut | past k-step obs/actions | unlimited latent | matches recurrent candidate |
| ★ Trajectory nearest-neighbor retrieval | structural heldout is really seed-only | train trajectory corpus | generator latent/graph | high score on "structural" heldout |
| ★ Cross-episode amortized / ideal-observer learner **(K2 core)** | gap is just learnable online inference | same train split+budget, full legal history | generator truth/latent | closes `oracle − fair` to within band |
| Recurrent learner (PPO/A2C) | candidate is generic recurrence | full legal history | generator latent | matches candidate robustly |
| History-conditioned transformer | candidate is long-context pattern-matching | full legal history | generator latent | matches candidate on structural heldout |
| Model-based learner | candidate is learned transition planning | same legal obs/actions | privileged simulator | beats candidate budget-normalized |
| Transition-aware learner | benefit is transition modeling | action-conditioned history | latent oracle | matches candidate |
| Raw-obs latent-decoder probe (K1) | latent decodable from obs values | observation values | history | decodes latent above ceiling |
| Exhaustive legal probe (reduced world) | env enumerable | full legal action set | latent | reaches oracle by enumeration |
| **Mechanism_oracle** upper bound | env not actually solvable | estimates non-read latent | none beyond latent it must estimate | non-reading oracle ≠ 0 (not fail-able) **or** oracle fails floor |

Blocking rule (binding): **if any simpler/fair baseline enters the oracle-equivalence band
under fair access, the route is `rejected_baseline_saturated`.** Do not relabel saturation as
nuance.

---

## 7. Capability-witness redesign (prevents another R2-style invalidation)

Tiered, with explicit invalidation rules. Sandbox-runnable tiers are flagged; training-heavy
tiers require a separately-authorized capable machine + frozen prereg (the R2 lesson: TF
witness ~1035 s/run ≫ 45 s/sandbox-call; full sweep ~28–82 h @ 2 CPU).

- **Tier 0 — generator/scorer/replay smoke** *(sandbox)*. Generator deterministic from seed;
  scorer callable; replay recomputes a trivial case. Fail → `INVALID` (broken harness).
- **Tier 1 — oracle/expert solvability** *(sandbox)*. `mechanism_oracle` near ceiling on debug
  **and** main split; non-reading oracle ≈ 0 (fail-able). Fail → `INVALID` (env not solvable /
  oracle is an answer-key).
- **Tier 2 — cheap-baseline failure** *(sandbox)*. random / majority / obs-only / memoryless /
  lookup / graph-cache / n-gram / NN-retrieval all clearly **below** block threshold on debug,
  ID, **and** structural-heldout splits. Any saturates → `rejected_baseline_saturated` (STOP).
- **Tier 3 — reduced supervised witness** *(sandbox or small GPU)*. Latent-transition or
  action-conditioned next-state prediction learnable above chance on debug. Fail → `INVALID`
  (no learnable signal; do not interpret as no-headroom).
- **Tier 4 — strong fair learner witness** *(capable machine, frozen budget)*. ≥2 families
  (one recurrent + one history-conditioned transformer **+** the K2 amortized/meta-learner)
  clear a pre-declared floor on debug + ID under frozen budget. Fail → `INVALID` (R2 repeat;
  **not** H0/H1). Budget chosen from a frozen pilot sweep on debug, never tuned to pass.
- **Tier 5 — structural-heldout retention** *(capable machine)*. The same strong learners
  retain **nontrivial but sub-ceiling** performance on structural heldout. If they **saturate**
  → `rejected_baseline_saturated` (no candidate-free headroom). If they **collapse to floor**
  → `INVALID` (heldout too hard / underpowered). Only the *middle band* = candidate-free
  headroom worth a future mechanism candidate.

Hard invalidation discipline (binding): **if the capability witness fails at any tier, the
result may invalidate the adjudication path but may NOT support H0/H1/headroom/mechanism
interpretation.** "Apparent headroom" that exists only because all strong baselines sit below
the debug floor is `INVALID`, not headroom.

---

## 8. Threshold / contract freezes required before Codex

Do not invent fake precision. The following must be **chosen and frozen (pre-registered) by
the operator before implementation**; the scan does not fix them and should not.

| Quantity | Proposed form (operator to freeze) |
|---|---|
| Oracle ceiling threshold | `mechanism_oracle ≥ τ_oracle` on debug+main (e.g. ≥0.95); non-reading oracle ≤ chance+band |
| Random/majority ceiling | `≤ chance + band` |
| Obs-only block threshold | `obs_only_family_max < τ_block` AND value-level positive control flips to blocked |
| Lookup / graph-cache block | `< τ_block` on structural heldout (per-episode resample must prevent ≈1.0) |
| Short-history cache block | `n-gram_max < τ_block` |
| Raw-obs latent decodability ceiling | `decoder_acc ≤ τ_decode` (K1 wall) |
| Strong-learner ID floor | `fair_learner ≥ τ_floor` on ID under frozen budget (R2 wall) |
| Structural-heldout retention floor/ceiling | `τ_retain_lo ≤ fair_learner ≤ τ_retain_hi` (the headroom band) |
| Candidate-free headroom definition | `oracle − max(fair panel incl. amortized) ≥ Δ`, budget-robust (R2) |
| Minimum seed/context count | `N_ctx ≥` (TLGP used N=200; pick with LCB/CI) |
| Aggregation method | macro across families + LCB (lower-confidence bound), pre-registered |
| Stability / CI rule | bootstrap CI; gap must hold at LCB, not point estimate |
| Max train/test leakage | semantic MI `< ε·H(label)` (K6; AIDSP used 0.9·H threshold) |
| Min task-space entropy / max enumerability | rule×remap×composition space ≫ training budget; exhaustive-probe must fail |

Threshold-selection rule (binding): thresholds frozen **before** results; no post-hoc tuning
(baseline-immunity `post-hoc threshold-optimizer` → `rejected_metric_degenerate`).

---

## 9. Leakage and positive controls (required)

Each must be a *positive control that can flip the verdict*, not a self-declared boolean
(K5).

- **Direct hidden rule-ID injection** → expect detector alarm + abnormal performance jump;
  if no alarm, scanner underpowered → STOP.
- **Latent graph exposure** (inject graph into observation) → expect obs-only == oracle and
  `rejected_trivially_decodable`.
- **Task-family ID exposure** (Meta-World one-hot analogue) → expect alarm.
- **Score-key / reward-shaping artifact exposure** → expect shaping-only baseline to win →
  alarm.
- **Train/test split membership leakage scan** → membership attacker must not predict split.
- **Seed/config/file-name leakage scan** → name-based AND value-based (K6 semantic MI, not
  substring only).
- **Observation-field audit** → enumerate every field; none may carry latent/graph/ID.
- **Serialized-state audit** → replay state must not embed generator truth read by agents.
- **Candidate import-path audit** → generator and scorer must not be importable by the (future)
  candidate; separate modules + separate source hashes (prevents generator-truth coupling).
- **Value-level attacker family** `{mean, variance, correlation, PCA, cross-episode,
  supervised, membership}` gated on `family_max` (Route C `278819a`).

Blocking result: any positive control that **fails to trigger** its expected alarm ⇒ the
benchmark's leakage gate is non-fail-able ⇒ STOP (this exact failure recurred across
POST-BRIDGE-001C, GATE4-PREFLIGHT-001B; do not repeat).

---

## 10. Replay and provenance contract (minimum schema)

Replay must **recompute** behavior/score from serialized state + action trace. A stored JSON
score is not evidence.

Required fields: `generator_fn_id` + `generator_source_sha256`; `scorer_fn_id` +
`scorer_source_sha256`; `run_id`; `split_id`; `seed_ids` / `context_ids`;
`hidden_rule_graph_id` (+ hash); `remapping_id` (+ hash); `initial_state_serialization`;
`action_trace`; `observation_trace_hash`; `reward_trace_hash`; `replay_recomputed_score`
(must equal recorded score bit-for-bit); `baseline_producer_fn_id` (per baseline);
`aggregation_code_path_sha256`; `code_version` / `commit_hash`; `failure_path_tests`;
`tamper_probe` (mutate one action → score must change; mutate one source byte → hash mismatch
raises).

Operational notes carried from the lineage: mount/FUSE writes can truncate files and stale
`.pyc` can mask source — run from a clean `/tmp` root and sync back with sha-verify
(TLGP-001B lesson); `push.*` scripts have a standing **hard-coded PAT BLOCK** — no remote
anchor in this task.

---

## 11. Stop / rollback conditions (hard, not narrative)

Close or redesign (do **not** patch until pass) if any holds:

- Oracle cannot solve debug or main distribution (or oracle is an `answer_key_oracle`).
- Any cheap baseline saturates the target metric (`rejected_baseline_saturated`).
- Obs-only / value-level attacker decodes latent above the decodability ceiling
  (`rejected_trivially_decodable`).
- Lookup / graph-cache saturates ID or structural heldout.
- Strong fair learners (incl. K2 amortized) **fail** the debug/ID floor → `INVALID` (R2
  repeat, not H0/H1).
- Strong fair learners **saturate** structural heldout → no candidate-free headroom.
- Structural heldout is actually seed-only (NN-retrieval wins).
- Replay cannot recompute the official score.
- Any leakage positive control fails to alarm.
- Any ablation is a post-hoc score edit instead of a true rerun.
- Metric optimizable by trivial probing / reward-shaping artifact (`rejected_metric_degenerate`).
- Task space too small/enumerable (exhaustive probe == oracle).
- Source/provenance cannot be pinned (`blocked_pending_canonical_readback`).
- Apparent headroom vanishes as fair budget grows (R2-mirror false positive).

---

## 12. Final output

1. **Verdict label:** `partial_accept_requires_narrow_repair`.
2. **Short reason:** Correct route (latent-structure / Alchemy-P2), independently convergent
   with the lab's own `BENCHMARK-METHODOLOGY-APPLICABILITY-001A`, and usable as method
   evidence — but not a contract: missing the K2 amortized/meta-learner baseline (the standing
   collapse mode), a budget-contaminated headroom definition, self-state scope creep, and
   re-invented thresholds instead of binding the canonical admission standard. Repairs are
   bounded (R1–R7).
3. **Selected proposal:** latent rule graph gridworld (structure-learning preflight only),
   with self/boundary scope struck; counterfactual-memory suite as secondary; causal
   micro-world deferred.
4. **Required repairs before Codex:** R1 add fitted cross-episode amortized/meta-learner +
   trajectory-NN baselines; R2 budget-robust headroom = `oracle − max(fair incl. amortized)`;
   R3 strike self/boundary channel; R4 bind to `BASELINE-IMMUNITY-ADMISSION-STANDARD-001A`
   verdict registry + value-level attacker family; R5 oracle = `mechanism_oracle` + twin-pair
   residual-uncertainty demo; R6 operationalize decodability↔solvability window with empty-
   window→reject/INVALID precommit; R7 define tombstones A–G or drop them.
5. **Minimum baseline matrix:** Section 6 (18 rows; ★ rows are the additions the scan omitted;
   blocking rule = any fair baseline in oracle-equivalence band → `rejected_baseline_saturated`).
6. **Capability-witness tiers:** Section 7 (Tier 0–5; Tier 0–3 sandbox-runnable; Tier 4–5
   capable-machine + frozen prereg; witness failure may invalidate but never supports
   H0/H1/headroom).
7. **Leakage / replay / provenance:** Sections 9–10 (positive controls must flip the verdict;
   replay must recompute score from serialized state + actions; separate generator/scorer
   source hashes; tamper probe; no remote anchor — `push.*` PAT BLOCK stands).
8. **Stop conditions:** Section 11.
9. **May Codex draft a candidate-free preflight card?** **Yes — drafting only.** Codex may
   author `LRGG-CANDIDATE-FREE-PREFLIGHT-001A` encoding R1–R7, the Section 6 baseline matrix,
   Section 7 witness, Sections 8–11 freezes/controls/stops. **Forbidden:** any mechanism
   candidate; EGO runtime/mainline/bridge/admission integration; LLM/AIRI integration; remote
   anchor; claim of mechanism evidence; 001C authorization; any training-heavy run before
   Tier 0–3 (cheap baselines + leakage + replay) pass; threshold tuning after results;
   self-state framing. The card must be **re-audited** before implementation, and Tier 4–5
   require a *separate* execution authorization + capable machine.
10. **Exact next minimal closed-loop action:** Operator authorizes Codex to **draft only**
    `LRGG-CANDIDATE-FREE-PREFLIGHT-001A` with R1–R7 encoded and all Section-8 thresholds left
    as operator-freeze placeholders. The card's **first executable stage must be the
    candidate-free cheap-tier harness** (generator + `mechanism_oracle` + cheap baselines +
    value-level attacker family + leakage positive controls + replay) on the **debug split
    only**, which is sandbox-runnable and bankable as bounded evidence; the training-heavy
    Tier 4–5 strong-learner witness is deferred to a separately-authorized capable-machine
    run with a frozen prereg. No implementation until the card is re-audited. Most probable
    honest outcome to pre-accept: another bounded `rejected_baseline_saturated` /
    no-headroom negative.

---

## Non-negotiable claim ceiling

This review cannot and does not prove: consciousness, subjectivity, emotion, self, agency
success, autonomy, intelligence, EGO/companion/runtime readiness, mainline effect, H0, H1,
001A downgrade, 001C authorization, TLGP-001B-R2 reinterpretation, or mechanism-candidate
validity. The maximum positive conclusion is exactly:
*"The Deep Research benchmark scan is sufficient to support a bounded candidate-free preflight
card for a latent-structure testbed, pending explicit baseline, leakage, replay, provenance,
and capability-witness constraints."*

## Anchors / sources

- TLGP-001B-R2 bank commit `5c03e0af7ce097d9055de5f1ef17052fe3a576be` (HEAD verified `5c03e0a`);
  LFS trace OID `sha256:f9d5f47854b91cc107230a2335b12c8c43dad6ffc82b34a2dee0da708ab6c0fd`.
- `docs/research/BENCHMARK-METHODOLOGY-APPLICABILITY-001A.md` (P1–P6; P2 = top pick; §5 Alchemy
  K1-by-construction but not a K2 escape).
- `docs/research/SELF-BOUNDARY-INTERVENABLE-LATENT-NEGATIVE-LINEAGE-AND-KILLER-CATALOG-001A.md`
  (K1–K7; ACSB `d5b4b92`; ACSB-001B `347b75b9`; ACOLB-A saturation; Route C preflight `726f26d`;
  AIDSP-001A-R1 code `6b8a6b61` / prereg `c594f4ae`).
- `docs/research/BASELINE-FIRST-HARNESS-001A-R1-ACCEPTED-NO-HEADROOM-CLOSEOUT-001A.md`
  (`rejected_no_headroom_baseline_saturated`; fair = oracle = 1.0; six graph-cache = 1.0).
- `docs/codex/contracts/BASELINE-IMMUNITY-ADMISSION-STANDARD-001A.md` + `.registry.json`
  (verdict registry; metric-degeneracy checklist; value-level attacker family; oracle taxonomy).
- `docs/research/GROUNDING-GATE-...-CLOSEOUT-001A.md` (self-state co-binding non-identifiable;
  route closed).
- Uploaded Deep Research scan (input under review).
