# GATE0–5 Feasible Mechanism-Surface Design — 001A

Task: `GATE0-5-FEASIBLE-MECHANISM-SURFACE-DESIGN-001A`
Type: independent hostile mechanism-route **design** audit (not implementation, not governance-tool, not ACP-BV 001B repair, not a Gate run).
Layer: mechanism-hypothesis / route-selection / implementation-design.
Status of this document: **design + reasoning. This file is NOT evidence.** No mechanism is shown to work here; no Gate is claimed passable; nothing is anchored.

> Delivery note: this file is written to the session outputs folder, **not** into the repo, per this card's "Do not modify repo." If you want it under `docs/research/`, place it yourself.

---

## 0. Inherited constraint (independently re-grounded, not narrative trust)

Anchor under which ACP-BV 001B was closed:
`remote-anchor-acp-bv-001b-negative-harness-repair-evidence-001a-98be7f4`, commit `98be7f4e647d7d5e897ee32b7905e085b67a43e7`.
Source: `docs/research/ACP-BV-001B-POST-ANCHOR-ROUTE-DECISION-CLAUDE-AUDIT-001A.md` (§0, §5, §7).

The decisive failure that every design below must defeat is **NOT** "the candidate was a hardcoded oracle." That is real (`candidate.py` byte-identical between rejected `a90ddde` and anchored `98be7f4`, embedding generator constants) but **fixable**. The decisive, **structural** failure is:

> **Distribution saturation by a fair baseline.** On the 001B distribution `parametric_modular_linear` reaches score **1.0 through legal channels with no oracle leakage** (`legal_channel_parametric_score=1.0`, `leaking_oracle_solvability_detected=false`), `delta = 0.0`, b3 equivalence band `|delta| ≤ 0.02`, `baseline_equivalent` on all 5 seeds. Every mandated lookup / graph-cache / NN challenger (`count_table`, `successor_map`, `fsm_planner`, `episodic_traversal`, `factorized_lookup`, `exact_key_memory`, `action_conditioned_nearest_neighbor`) scores ≈ 0.05–0.10.

When the **strongest fair baseline reaches the oracle ceiling**, `candidate > fair_baseline` is **structurally unreachable regardless of candidate quality**. No candidate engineering can recover headroom that the distribution does not contain.

The 001B audit (§1, §7) already enacted the consequence: close 001B as a mechanism route, **DEFER** any replacement surface behind a *precondition* — "a passing headroom preflight that shows the strongest fair baseline `< ceiling − band` on legal channels." **This document is that deferred replacement-surface design, and it embeds that headroom preflight as a hard STOP-gate (§6, §9 Phase 0).**

### 0.1 The deeper root cause the 001B card under-states (load-bearing for this design)

001B framed saturation as "a static parametric closed-form fit the latent." The generalization an auditor must internalize is stronger:

> **Amortization theorem (informal).** For any surface where the correct answer is a fixed, learnable function of the *legal observation history*, a sufficiently trained frozen amortized model (a neural net mapping `legal_history → answer`, trained on the legal distribution, no test-label access) can in principle match *any* online inference procedure — because online inference is itself a fixed computation that can be amortized.

Consequence: **"infer a latent and answer" surfaces are saturable in principle.** A surface that merely requires latent inference does not escape 001B; it reproduces it with a bigger baseline. Genuine, non-rigged headroom requires **breaking an amortization precondition**. There are exactly two principled ways to do so, and every design below must carry **at least one**, *measured by preflight before any candidate is authored*:

- **(NS-1) Test-time distribution shift / non-stationarity.** The test regime (latent prior, or within-episode dynamics) lies **outside** the legal training distribution. A frozen amortized baseline baked in the train prior and is miscalibrated; a test-time **online prediction-error update** seeded with a weak prior adapts from legal observations regardless of regime. The asymmetry "test-time PE update from legal observations" vs "frozen amortization" **is exactly the mechanism under test** (see §2.A.5).
- **(NS-2) Interventional identifiability.** Under confounding, the answer is **non-identifiable from observational data by a causal-identifiability theorem**, so any observation-only baseline (however trained) sits at chance; only the agent's **own interventions** break the confound. This is theorem-backed non-saturation against the observation-only baseline even in-distribution.

Both are predeclared, falsifiable, and measurable. A surface lacking both is rejected at preflight.

---

## 1. The non-saturation gate (applies to all candidate surfaces)

Before authoring any candidate, the surface must pass a **headroom preflight** producing `headroom_preflight.json` with, on the **OOD/test split** and on legal channels only:

```
strongest_fair_baseline_score   (max over the full panel incl. amortized_seq trained to convergence at matched capacity)
oracle_ceiling_score            (privileged, knows latent; upper bound only)
no_update_floor_score           (frozen prior)
headroom = oracle_ceiling - strongest_fair_baseline
in_distribution_negative_control: strongest_fair_baseline ≈ oracle within band   (MUST hold)
band                            (predeclared, e.g. |delta| ≤ 0.02 as in 001B b3)
verdict ∈ {headroom_present, saturated_close, parity_broken_close}
```

Gate logic (predeclared, not tuned post hoc):

- `saturated_close` if `headroom ≤ band` on the OOD split → **the 001B signature → close the surface, do not author a candidate.**
- `parity_broken_close` if in-distribution the strongest fair baseline does **not** reach the candidate-reachable ceiling (i.e., the baseline is under-powered or leakage exists) → panel invalid → close/repair panel first.
- `headroom_present` only if OOD headroom `> band` **and** the in-distribution negative control holds. Only then may a candidate be authored.

This single gate is what 001B lacked at authoring time and what turns "candidate engineering" from theater into a test.

---

## 2. Design A — Online action-conditioned prediction-error adaptation under OOD / non-stationary latent dynamics (**PREFERRED**)

### A.1 Mechanism hypothesis
**Action-conditioned online belief update driven by prediction error** (recursive Bayesian / Kalman-style system identification). Claim under test: on a constructed surface, maintaining and updating a latent belief from action-conditioned prediction errors produces better heldout **counterfactual action-outcome** prediction than the strongest fair baseline that lacks test-time update — *and the advantage is load-bearing on the update path*, shown by ablation collapse and replay recomputation. Carries **NS-1** (OOD) as primary and a weak form of **NS-2** (active probing) as secondary.

### A.2 Surface distribution
- Hidden per-episode latent `θ ∈ R^d`, small `d` (target `d=2`). `θ` defines a smooth action→outcome response, e.g. `g_θ(a) = σ(θ·φ(a))` with `φ` a fixed low-order feature map of action `a ∈ A` (1–2 D continuous or a small grid). A hidden **viability threshold** `τ` turns the regression into a boundary label `viable(a) = [g_θ(a) ≥ τ]` so the surface reads as an action-conditioned **latent-boundary / viability** surface (the card's preferred direction).
- Outcome `y_t = g_θ(a_t) + ε_t`, `ε_t ~ N(0, s²)` (stochasticity defeats exact memory).
- **Regimes:** `R_train` = narrow prior over `θ`; `R_OOD` = shifted/widened prior at test. **Gate5 extension only:** `θ` switches at an unsignaled changepoint `t_c` (non-stationary).
- **Episode:** sample `θ` (and `τ`); **probe phase** of budget `B` closed-loop actions `a_1..a_B`; **query phase** of `K` heldout query actions `a*_1..a*_K` drawn from action regions **not directly probed**, so answering requires *extrapolating θ*, not recalling a probed point.
- Train/heldout split is over **episodes** (fresh `θ` each), and over **action regions within an episode** (query actions disjoint from probe actions).

### A.3 Legal observation channel
- **Candidate sees:** the actions *it chose* `a_t`, their scalar outcomes `y_t`, the query actions `a*_k`, episode id, seed-derived rng *handle* (not the latent), step index. Action budget `B`.
- **Forbidden (answer-bearing leakage if present):** `θ`, `τ`, the noise realizations `ε_t`, the closed form `g_θ`, the query labels/outcomes, any field deterministically encoding the above, and any cross-episode `θ` table.
- Baselines see the **same** legal channel under the **same** budget `B`.

### A.4 Candidate update rule (what is learned / serialized / changes)
Recursive Bayesian linear/GLM update over `θ` (closed-form, tiny, **no LLM, no gradient training at author time**):
1. Predict `ŷ_t = E[g_θ(a_t) | posterior_{t-1}]` from current posterior mean `μ_{t-1}`.
2. Prediction error `e_t = y_t − ŷ_t`.
3. **Action-conditioned** update: posterior `(μ_t, Σ_t) = update(μ_{t-1}, Σ_{t-1}, φ(a_t), e_t)` — the error is attributed to the **action that produced it** via `φ(a_t)`.
4. `serialized_state = (μ_t, Σ_t, t)`.
5. Query: answer `viable(a*) = [σ(μ_T·φ(a*)) ≥ τ̂]` (or regression `ŷ* = σ(μ_T·φ(a*))`), using only the updated posterior and legal info.
Behavior that must change after update: with more informative probes the posterior contracts and heldout query accuracy rises toward the oracle; with the prior alone it stays at floor.

### A.5 Why fair baselines should not saturate (per challenger, predeclared expectation — to be **measured**, not asserted)
- **Frozen parametric (`parametric_modular_linear`-class):** a static `legal_summary → answer` map fit on `R_train`, frozen. Under `R_OOD` it extrapolates with the wrong prior → below ceiling. (This is the exact 001B winner; here it is denied a closed form because `θ` is episode-fresh and the test prior is shifted.)
- **Amortized sequence model (`amortized_seq`, the *strongest* fair baseline):** GRU/MLP mapping probe history→answer, trained to convergence on `R_train`, frozen. In-distribution it **must** match the candidate (negative control). OOD it applies the baked-in train prior → degrades. Gap = generalization-to-OOD that test-time update achieves and frozen amortization does not.
- **Exact-key / partial-key memory (`exact_key_memory`):** continuous, stochastic, episode-fresh `θ` → query key never co-occurred with its answer → miss.
- **Factorized lookup (`factorized_lookup`):** no factor of the *query observation* determines the answer without the within-episode probe history → miss.
- **Graph-cache family (`count_table`, `successor_map`, `transition_table`, `graph_lookup`, `fsm_planner`, `episodic_traversal`):** transitions/outcomes are episode-specific and shifted at test; cached train transitions are wrong this episode → miss (these are the lab's mandated graph-cache challengers and scored ≈0.05–0.10 on 001B; they must be re-run here, not assumed).
- **Nearest-neighbor (`action_conditioned_nearest_neighbor`):** nearest train episode by probe-history embedding carries a *different* `θ` under OOD → wrong answer; similarity in observation space does not predict the answer.
- **Sequence imitation:** no fixed probe→answer policy to copy; optimal answer depends on inferred `θ`.
- **No-update (frozen prior):** ignores probes → prior-predictive floor.

The **honest fairness boundary** (predeclared): baselines may train offline on legal in-distribution data but **do not perform test-time belief update from prediction error**. The candidate's `no_update` ablation collapses *onto* this baseline class — proving the boundary is exactly the mechanism axis, not a rig. If a baseline were *allowed* test-time PE adaptation on legal observations (e.g. test-time training), it would *become an instance of the mechanism*, so it does not refute the claim; it instantiates it. The claim is about the **mechanism class** (test-time PE update), not a specific implementation.

### A.6 Strongest fair baseline panel (all callable, same legal channel, same budget, same scorer)
`parametric_frozen`, `amortized_seq` (strongest), `exact_key_memory`, `partial_key_memory`, `factorized_lookup`, `count_table`, `successor_map`, `transition_table`/`graph_lookup`, `fsm_planner`, `episodic_traversal`, `action_conditioned_nearest_neighbor`, `sequence_imitation`, `no_update` (floor). Privileged non-fair reference: `oracle` (knows `θ,τ`) for ceiling only — never a pass.

### A.7 Headroom argument (inequalities only; numbers must be computed, never claimed)
- **In-distribution (negative control):** `candidate ≈ amortized_seq ≈ (oracle − noise) > no_update`. Baseline catches candidate ⇒ panel not rigged. *If candidate > amortized_seq in-distribution beyond band → leakage/parity → STOP.*
- **OOD (the evidence):** `oracle > candidate > amortized_seq ≈ {parametric, lookup, NN, graph-cache} ≳ no_update`, with `candidate − strongest_fair > band`.
- **Recovery floor (anti-"beat-a-broken-baseline"):** require `candidate − no_update ≥ ρ·(oracle − no_update)` for predeclared `ρ` (e.g. ≥0.5) so the candidate demonstrably tracks `θ`, not merely out-scores a degenerate baseline.
- **Active-probing (secondary NS-2):** `candidate ≫ observation_only` when queries require extrapolation reachable only by adaptive probing.

### A.8 Required ablations (each **re-runs episodes under real intervention**, not a stored re-score)
- **A1 no_update** (frozen prior): → `no_update` floor.
- **A2 no_action_conditioning** (update ignores which action produced `y_t`; pools errors): `θ` mis-estimated → drop.
- **A3 no_PE_correction** (observe but never apply gain·error): ≈ frozen prior → drop.
- **A4 shuffled_labels** (break `(a_t, y_t)` correspondence within episode): posterior corrupted → drop to ≤ floor. *If it does **not** drop, the "update" is a disguised lookup → STOP.*
- **A5 shuffled_probe_order**: **negative control** in the stationary variant — iid-noise posterior is order-invariant → should **not** drop; a drop signals an order artifact. In the Gate5 changepoint variant order **should** matter → drop. Direction predeclared per variant.
- **A6 frozen_posterior_before_informative_probes**: → drop (the late probes are load-bearing).

### A.9 Replay / recomputation requirement
- From `serialized_state` init + recorded `(a_t, y_t)` sequence + the candidate **code-path hash**, **re-execute** the update rule and reproduce the `(μ_t, Σ_t)` trajectory and query answers within numerical tolerance. **Not** a stored-output hash comparison.
- **Counterfactual replay:** feed an ablation's recorded action sequence and confirm the posterior **diverges** → proves the trajectory is load-bearing, not a stored constant.
- Replay uses only the legal channel: no `θ`, no future `y`, no renderer state.

### A.10 Leakage controls (positive controls — each must be **detected** and must **change the score** when injected)
- **L1 oracle-field:** inject `θ` into a legal field → scanner flags; control that candidate is *not already* covertly reading it (randomizing the injected field leaves candidate score unchanged).
- **L2 hidden-variable:** inject `τ` / `s²` into observation → flagged.
- **L3 answer-bearing label:** inject query outcome into a probe field → flagged; a candidate *given* access spikes to oracle (proves the spike is detectable).
- **L4 generator-formula:** expose closed-form `g_θ` → flagged.
- **L5 train/heldout contamination:** query action appears in probe set, or a test `θ` appears in train → contamination check fails.
- **L6 schema-alias:** rename a forbidden field to a benign alias → allowlist must be **by semantics, not by name** → flagged. (001B-family whitelist-escape recurrence guard.)

### A.11 Failure modes (strongest ways this fakes success) — with guard
- **F1 amortized baseline under-trained/under-capacity** → fake OOD gap. Guard: in-distribution negative control must null; record training-budget & capacity parity + learning curves in `parity_report.json`.
- **F2 OOD so extreme nothing works** ("beat a broken baseline"). Guard: recovery floor `ρ` vs oracle (A.7).
- **F3 `θ` leakage** → L1–L6.
- **F4 fake update (lookup in disguise)** → A3/A4 must drop + counterfactual replay must diverge.
- **F5 metric favors candidate representation** → identical scorer for all; `producer_function` logged per score; baselines share the decoder.
- **F6 action-conditioning decorative** → A2 must drop; queries require cross-action extrapolation.
- **F7 equivalence band gamed post hoc** → band predeclared in the Codex card; multi-seed CI (≥5 seeds).

### A.12 Stop condition (close the route, do not repair)
- **S1** headroom preflight `saturated_close` (strongest fair baseline ≥ ceiling − band on OOD) → 001B signature → CLOSE.
- **S2** in-distribution `candidate > amortized_seq` beyond band, cause not removable → leakage/parity → CLOSE.
- **S3** A1/A3/A4 do not drop → mechanism not load-bearing (candidate is lookup/parametric) → CLOSE.
- **S4** candidate cannot beat `no_update` on OOD → no mechanism value → CLOSE.

---

## 3. Design B — Replay / consolidation of serialized past episodes (presented, **attacked, not selected**)

- **B.1 Mechanism:** offline **replay/consolidation** of serialized past episodes improves heldout cold-start on later episodes vs online-only.
- **B.2 Distribution:** a stream of episodes sharing a hidden **hyper-prior** `H` over per-episode `θ`; later episodes get a tight probe budget so cold-start dominates.
- **B.3 Legal channel:** per-episode probes/outcomes + a **bounded** serialized cross-episode memory. Forbidden: `H`, other episodes' `θ`, future episodes.
- **B.4 Update rule:** within-episode `θ` posterior (as A) **plus** a consolidation step replaying serialized episode summaries to update the shared prior used as cold-start. `serialized_state` = consolidated hyper-prior.
- **B.5 Non-saturation:** `H` is in no single episode; only cross-episode aggregation recovers it. **NS-1** if later episodes are OOD relative to the consolidated prior.
- **B.6 Panel:** + `pooled_hierarchical_batch_fit` (**the dangerous one**), `online_no_replay`, `replay_random_episodes`, episode-NN, lookup.
- **B.7 Headroom:** `replay > online_no_replay` (cold-start gap) is real — **but** `replay ≈ pooled_hierarchical_batch` because a batch hierarchical fit also recovers `H`. To separate replay you must impose bounded-memory / streaming, which **handicaps the batch baseline** — a **parity violation** the lab forbids.
- **B.8 Ablations:** no_replay, replay_random_episodes, shuffled_episode_order (weak: episodes exchangeable → order shouldn't matter).
- **B.9 Replay:** consolidated prior recomputable from serialized summaries + code path.
- **B.10 Leakage:** `H` leakage, cross-episode `θ` leakage, future-episode contamination.
- **Attack / why not selected:** the *strongest fair baseline* (pooled hierarchical batch fit) **saturates** the consolidation benefit. Separating replay requires a memory constraint that looks like baseline handicapping → reproduces a milder 001B saturation. Higher infrastructure cost, weaker ablations (exchangeability mutes order ablation). **Defer.**

---

## 4. Design C — Self-boundary via interventional credit assignment under confounding (presented, **attacked, not selected first**)

- **C.1 Mechanism:** **self-boundary inference** — infer which observation channels are under the agent's control (self) vs exogenous — via **interventional** credit assignment.
- **C.2 Distribution:** obs vector `x ∈ R^m`; hidden subset `S` of channels responds to the agent's action (self), the rest follow an exogenous AR process; a **confound** makes some exogenous channels correlate with the action in *observational* data. `S` episode-fresh.
- **C.3 Legal channel:** chosen actions + resulting `x`; the agent may **intervene** `do(a)`. Forbidden: `S`, exogenous seed, confound structure.
- **C.4 Update rule:** belief over `S` by interventional contrast (channels that move under `do(a)` vs baseline are self); update from intervention outcomes. `serialized_state` = posterior over `S`.
- **C.5 Non-saturation (its strength):** under confounding, `S` is **non-identifiable from observational data by a causal-identifiability theorem** → any observation-only baseline (however trained) is at chance. This is **NS-2**, theorem-backed, holding **even in-distribution** — strictly stronger than A on that axis. The candidate's own interventions break the confound.
- **C.6 Panel:** `observation_only` (provably ≈ chance), `correlation_classifier_frozen` (confounded → wrong), `interventional_random_policy` (partial), `amortized_interventional` (strong; needs OOD or active-policy advantage to separate), lookup/NN/graph-cache (S episode-fresh → miss).
- **C.7 Headroom:** `candidate ≫ observation_only` by identifiability, robustly; vs `amortized_interventional` needs OOD or an active-intervention-policy advantage.
- **C.8 Ablations:** no_intervention (→ chance), no_credit_update, shuffled action↔channel correspondence, random intervention policy.
- **C.9 Replay:** posterior over `S` recomputable from intervention log + outcomes + code path.
- **C.10 Leakage:** **high schema-alias risk** — `S` can leak through channel **index ordering or names**; plus confound-structure and exogenous-seed leakage.
- **Attack / why not first:** strongest theoretical non-saturation (observation-only at chance by theorem), but **more moving parts** (multi-channel confounded generator) and **higher hardcoding/alias-leakage surface** (`S` leaking via channel identity). Larger Codex footprint → higher rigging risk. **Excellent second route / a strengthening graft onto A, not the smallest first build.**

---

## 5. Selection

**Selected: Design A.** Against the card's 7 selection criteria:

1. **Smallest implementation that still tests a real mechanism:** `d=2` latent, smooth response, recursive least-squares/GLM update — minimal. (B needs streaming infra; C needs a confounded multi-channel generator.)
2. **Strongest chance candidate > fair baseline without leakage:** carries **two** non-saturation guards (NS-1 OOD amortization gap; NS-2-lite active probing) **plus** a built-in in-distribution null control that catches parity violations.
3. **Clearest ablation drop:** A1/A3/A4 collapse to the prior floor — unambiguous, falsifiable.
4. **Replay recomputable:** closed-form recursive update → exact re-execution from `(serialized_state, legal obs, code path)`.
5. **No subjectivity:** pure heldout prediction; no emotion/consciousness content.
6. **No mainline needed:** fully standalone, local CLI + pytest + artifacts.
7. **Lowest Codex-hardcoding risk:** smallest serialized state, latent sealed off-channel, fewest aliasable fields (vs C's channel-identity surface).

Grafts for later, **not** in the first build: take C's interventional-identifiability (make `θ` partly identifiable *only* via active probing so observation-only is provably weak); add A's Gate5 changepoint for non-stationary initiative. **Avoid B** as a first route — it re-enters saturation via the pooled-batch baseline.

---

## 6. Embedded headroom preflight (the STOP-gate, **not** a standalone tool)

Per the card, `DISTRIBUTION-HEADROOM-PREFLIGHT` exists **only** as Phase 0 inside A's implementation, never as a separate next task. It runs **before** any candidate is authored and emits `headroom_preflight.json` (schema in §1). If `verdict ≠ headroom_present`, implementation **stops** and the surface is closed or the panel repaired — exactly the gate ACP-BV 001B lacked at authoring. This is the single most important structural import from the 001B negative evidence.

---

## 7. Gate0–5 mapping (Design A)

- **Gate0 — hygiene:** candidate + baselines callable; `result.json`, `trace.jsonl`, schemas validate; deterministic seeds; no crash; `claim_ceiling` field present.
- **Gate1 — provenance / anti-hardcoding:** code-path hash pinned; `run_id`, seeds, episode IDs in every record; leakage scanner L1–L6 pass with positive controls firing; candidate has no access to `θ/τ/g_θ/answers`; training-invariance probe (candidate must depend on legal probe data, not be constant).
- **Gate2 — ablation + replay:** A1–A6 re-run real episodes with predeclared drop directions; replay reproduces `(μ,Σ)` trajectory; counterfactual replay diverges.
- **Gate3 — baseline discrimination:** full panel computed; **OOD** `candidate − strongest_fair > band` **AND** in-distribution `|candidate − amortized_seq| ≤ band` (negative control). **Both** required to pass.
- **Gate4 — mechanism-surface evidence:** the **joint** pattern (OOD gap + in-distribution null + ablation collapses + observation-only weak + replay reproduces + recovery floor met) implicates the **online action-conditioned PE-update path** as load-bearing — **bounded to this surface only.**
- **Gate5 — controlled initiative / viability (extension, its own card):** changepoint variant where the agent must decide **when to re-probe** under a changing viability constraint (controlled initiative). Higher risk; not in the minimal card.

---

## 8. Claim ceiling, stop condition, rollback

**Claim ceiling of THIS document:** route-design / implementation-design evidence only. It does **not** prove any mechanism works, any Gate is passable, ACP-BV validity, EGO/mainline readiness, agency, autonomy, consciousness, emotion, or stable user benefit. Claude design is not evidence.

**Strongest claim the FUTURE A run could earn (ceiling for the Codex card):**
> "Bounded local evidence that, on this constructed OOD action-conditioned latent-boundary surface, online prediction-error belief update outperforms the strongest fair amortized/lookup/graph-cache baseline on heldout counterfactual queries beyond a predeclared band, with ablations and replay implicating the update path, and an in-distribution negative control confirming the panel is not rigged."
Nothing stronger — not mechanism-in-general, not any honorific Gate pass, not subjectivity.

**Stop conditions:** S1–S4 (§A.12) + headroom preflight `saturated_close`/`parity_broken_close` (§6).

**Rollback:**
- *This Claude task:* design only; rollback = discard this file. No repo write, no anchor, no Codex run performed.
- *Future Codex run:* isolated branch; writes only under `src/<task>/`, `tests/<task>/`, `artifacts/<task_id>/`. Any Gate fail → write `failure_manifest.json`, **do not anchor**, leave branch unmerged. No mainline, no LLM, no global schema, no remote anchor.

---

## 9. Minimal Codex implementation card (exactly one, for Design A)

```
TASK CARD
task_id: ACOLB-001A   (action-conditioned online latent-boundary, surface A)
type: bounded mechanism-surface implementation (Phase 0 headroom preflight gates Phase 1)
layer: engineering implementation + mechanism hypothesis
authorization: DRAFT ONLY — not authorized to execute. Requires explicit Codex run instruction.

problem definition:
  Build a minimal executable surface where heldout counterfactual action-outcome
  (viability-boundary) prediction under an OOD/episode-fresh latent requires an
  online action-conditioned prediction-error belief update, and where the strongest
  fair baseline (incl. a convergence-trained amortized sequence model) cannot reach
  the oracle ceiling on the OOD split.

current stage: pre-implementation. No prior ACOLB artifacts exist.

hypothesis:
  candidate (recursive Bayesian/GLM PE-update over latent theta) > strongest fair
  baseline on OOD heldout queries beyond predeclared band; ablations on the update
  path collapse to the no_update floor; behavior replayable from serialized_state.

baseline panel (all callable, same legal channel, same budget B, same scorer):
  parametric_frozen, amortized_seq[STRONGEST], exact_key_memory, partial_key_memory,
  factorized_lookup, count_table, successor_map, transition_table/graph_lookup,
  fsm_planner, episodic_traversal, action_conditioned_nearest_neighbor,
  sequence_imitation, no_update[FLOOR]; oracle[privileged, ceiling-only].

ablations (re-run episodes under real intervention; predeclared directions):
  A1 no_update -> floor; A2 no_action_conditioning -> drop; A3 no_PE_correction -> floor;
  A4 shuffled_labels -> <= floor (else STOP: disguised lookup);
  A5 shuffled_probe_order -> NO drop stationary / drop changepoint;
  A6 frozen_posterior_pre_informative_probes -> drop.

trace/replay requirement:
  trace.jsonl per step: {run_id, episode_id, seed, t, action a_t, predicted y_hat,
    actual y_t, prediction_error e_t, posterior mu_t/Sigma_t, query preds, producer_function}.
  Replay re-EXECUTES the update from serialized_state + legal obs + code_path_hash and
  reproduces (mu,Sigma) + query answers within tolerance (NOT hash compare).
  Counterfactual replay on an ablation's action sequence MUST diverge.

acceptance gate (ALL required; predeclared, no post-hoc tuning):
  Phase 0 headroom_preflight.json.verdict == headroom_present
    (OOD headroom > band AND in-distribution negative control holds); else STOP/close.
  Gate3: OOD (candidate - strongest_fair) > band  AND  in-dist |candidate - amortized_seq| <= band.
  Recovery floor: candidate - no_update >= rho*(oracle - no_update), rho predeclared.
  Gate1: leakage scanner L1-L6 pass with positive controls firing; training-invariance fails
    for candidate (candidate MUST depend on legal probe data).
  >= 5 seeds; report CIs.

computed-evidence requirements (no green self-report):
  every score carries producer_function, inputs, run_id, seed, episode_ids, aggregation,
  code_path_hash; independent callable baselines; ablations rerun under real intervention;
  leakage scanner with positive controls; replay from serialized_state + observation
  recomputation; failure_manifest.json on any failure instead of green.

band: predeclared (e.g. |delta| <= 0.02 as in 001B b3). rho: predeclared (e.g. 0.5).
seeds: predeclared set (>=5).

claim ceiling: see this doc section 8 (future-run ceiling). Bounded local mechanism
  evidence only. No Gate-pass honorific, no subjectivity/agency/EGO claim, no mainline.

stop condition: S1-S4 (this doc section A.12) + headroom saturated_close/parity_broken_close.

rollback: isolated branch; writes only under src/acolb_001a/, tests/acolb_001a/,
  artifacts/acolb_001a/. Any gate fail -> failure_manifest.json, do not anchor, leave
  unmerged. No mainline, no LLM, no global schema migration, no remote anchor.

files allowed:   src/acolb_001a/**, tests/acolb_001a/**, artifacts/acolb_001a/**
files forbidden: everything else (EGO mainline, global config/schema, other surfaces,
  ACP-BV 001B files, governance stacks).
commands expected: python -m acolb_001a.headroom_preflight ; python -m acolb_001a.runner ;
  pytest tests/acolb_001a/ -q
expected artifacts: headroom_preflight.json, result.json, trace.jsonl,
  baseline_comparison.json, ablation_report.json, replay_report.json, leakage_report.json,
  parity_report.json, failure_manifest.json (if any failure), claim_ceiling.txt.
```

---

## 10. Self-audit against this task's 13-point acceptance gate

1. ≥2 mechanism-surface candidates — **yes** (A, B, C).
2. one selected best candidate — **yes** (A, §5).
3. clear implementation sketch — **yes** (§A.1–A.10, §9).
4. baseline panel — **yes** (§A.6; named graph-cache challengers incl. mandated set).
5. ablation plan — **yes** (§A.8, A1–A6 with predeclared directions).
6. replay recomputation plan — **yes** (§A.9; re-execute not hash-compare; counterfactual divergence).
7. leakage controls — **yes** (§A.10, L1–L6 positive controls incl. schema-alias).
8. headroom / non-saturation argument — **yes** (§0.1 amortization theorem, §1 STOP-gate, §A.5, §A.7).
9. Gate0–5 mapping — **yes** (§7).
10. one bounded Codex implementation card — **yes** (§9, exactly one: `ACOLB-001A`).
11. claim ceiling — **yes** (§8).
12. stop condition — **yes** (§A.12, §6, §8).
13. rollback plan — **yes** (§8, §9).

Reject/revise checks (all must be false): governance-protocol-dominated → **false** (one short STOP-gate, embedded); recommends more docs without a surface → **false**; treats design as evidence → **false** (stated twice); proposes fixing ACP-BV 001B toward pass → **false** (001B is a *constraint*, untouched); lacks non-saturation argument → **false**; lacks ablation/replay → **false**; cannot explain why success needs update/inference/replay/boundary state → **false** (NS-1/NS-2 + ablation collapse argument).

**Auto-Remote-Anchor: forbidden. No repo modified. No code executed. No Gate claimed passed.**
