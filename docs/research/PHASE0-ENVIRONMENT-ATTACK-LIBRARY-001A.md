# PHASE0-ENVIRONMENT-ATTACK-LIBRARY-001A

Status: BRAINSTORMING DRAFT. Not frozen. Not a registry. Not an enforcement harness.
Auto-Remote-Anchor: forbidden.

## Layer And Claim Ceiling

- Layer: route-governance / evidence-governance brainstorming only.
- This is an *attack* library: a catalogue of ways a Phase-0 environment sketch can
  look mechanism-sensitive while actually being solved by a cheaper fair route.
- Claim ceiling: **attack-library brainstorming only.** This file proposes NO final
  candidate environment, promotes NO sketch, authorizes NO route tournament, and
  authorizes NO candidate implementation. It does not prove headroom, Gate1 pass,
  mechanism validity, agency, autonomy, consciousness, emotion, stable user benefit,
  or EGO readiness.
- It is the offensive companion to two existing read-only sources, which remain
  authoritative; this file does not amend, re-freeze, or supersede them:
  - `docs/codex/contracts/BASELINE-IMMUNITY-ADMISSION-STANDARD-001A.md` (defensive
    failure families §2–§8).
  - `docs/research/MINIMAL-ENV-SPEC-001A.md` (the frozen Phase-0 scouting environment
    contract: battery, leakage, replay, provenance, "strongest false explanation").

## 0. How To Read This (anti-fragmentation)

Each attack family below is deliberately expressed in the vocabulary the lab already
runs, so it plugs into the existing two-stage scout rather than forking a new schema:

- **Stage 1 — static kill scan.** `static_kill_scan.json.criteria` in
  `artifacts/batch_env_headroom_scout_002a/`.
- **Stage 2 — micro-probe.** `micro_probe_results.json.allowed_verdicts`.
- **Battery producers.** `MINIMAL-ENV-SPEC-001A` §"Baseline Battery Requirement"
  (lines 286–314).
- **Defensive clause.** `BASELINE-IMMUNITY-ADMISSION-STANDARD-001A` §2–§5.

If an attack here has no existing static criterion / micro-probe verdict / battery
producer / standard clause to bind to, that gap is itself the finding — it means the
current scout cannot detect that attack yet. New detectors require a separate authorized
card; this document does not author them.

**Threat model.** The adversary is not a person — it is *us, optimistically*. The
failure is declaring "candidate beats the battery, therefore headroom" when in truth a
cheaper fair route was never put in the battery, or was put in crippled. Every family
below is a recorded or near-recorded way that gap was manufactured.

**Honest caveat (read before using).** A catalogue of attacks that is *not wired into a
fail-able verdict* is itself the failure mode `MINIMAL-ENV-SPEC-001A` calls a "static
verdict dictionary" / "provenance-wellformed-only" admission (lines 248–249). This file
is a thinking aid for designing fail-able controls. It is not evidence, and a sketch is
not safe because it "passed the attack library" by inspection.

---

## Attack Families

Each family lists exactly the six requested fields, plus a Grounding pointer (the
operating contract requires citing prior negative evidence) and a Binds-to cross-ref.

### A1. Direct legal-channel compute

- **Surface pattern it breaks:** the target is a (near-)deterministic function of a
  set of legal/visible channels whose size is ≤ budget, so the "visible-channel oracle"
  is itself a fair legal-compute baseline. The reported oracle-vs-candidate gap is an
  artifact of *not also running the legal-compute baseline*.
- **Cheapest fair baseline that exploits it:** `exhaustive_legal_query` under the same
  budget, or a closed-form evaluator that reads the legal component fields and applies
  the (recoverable) combining function.
- **Static scanner signal:** `target_deterministic_from_le_budget_visible_channels`
  AND `legal_query_can_read_all_target_components`.
- **Required micro-probe baseline:** `exhaustive_legal_query` *and* the visible-channel
  oracle re-cast as a budget-faithful fair baseline (so oracle and "strongest fair" are
  comparable on the same legal channel and budget).
- **False-positive headroom signature:** oracle high (≈ ceiling), reported strongest
  fair baseline high but *below* oracle, and the legal-compute baseline simply absent
  from the panel → a phantom margin (e.g. reported gap 0.545 when the true gap ≈ 0).
- **Minimal reject condition:** any legal-channel function under budget reaches the
  oracle equivalence band → `reject_direct_decode`.
- **Grounding:** BATCH-ENV-HEADROOM-SCOUT-002A — `relational_contrast_budget_probe`,
  target `(a+2b+phase)%3` with all components legal-readable under budget 3; the oracle
  was itself a fair legal-compute baseline, so true gap ≈ 0. Audited as a direct-decode
  false positive.
- **Binds-to:** standard §3.1 (visible-target independence), §4.2 (budget-faithful
  oracle); MINIMAL-ENV-SPEC "strongest false explanation" item 1.

### A2. Graph-cache / transition-table saturation

- **Surface pattern it breaks:** the reachable state/observation space is small or
  enumerable, so a table that memorizes (state, action) → outcome reconstructs the
  target without any mechanism.
- **Cheapest fair baseline that exploits it:** `transition_table` or `count_table`
  (whichever is cheapest to build over the enumerable space).
- **Static scanner signal:** `graph_cache_transition_table_recovers_target_exactly`
  AND `state_space_small_enough_for_trivial_lookup_saturation`.
- **Required micro-probe baseline:** the **full six-member** graph-cache family —
  `graph_lookup`, `transition_table`, `successor_map`, `count_table`, `fsm_planner`,
  `episodic_traversal` — scored as `family_max`. Partial inclusion is a known evasion.
- **False-positive headroom signature:** candidate beats a *weak or partial* graph-cache
  member (e.g. only `graph_lookup` was included) while an omitted stronger member
  (`count_table` / `episodic_traversal`) would have reached the oracle band.
- **Minimal reject condition:** any of the six members ≥ oracle − band →
  `reject_graph_cache_saturated`.
- **Grounding:** Gate1 EXEC-001 `graph_cache_collapse`; Route C final closure — all six
  graph-cache members reached 1.0; `docs/CLOSED_FAMILIES.md`
  (`pair_count_table`, `full_bundle_decoder`, `serialized_state_decoder`, `belief_table`,
  `ngram_trace_lookup`).
- **Binds-to:** standard §5 (graph-cache challengers, MANDATORY for any representational
  or environment claim); MINIMAL-ENV-SPEC battery lines 305–306, acceptance gate "all six".

### A3. Lookup under memorization split

- **Surface pattern it breaks:** when train/test contexts are disjoint, a pure
  lookup / nearest-neighbor baseline keyed on context ids cannot match unseen keys, so
  its score collapses. The low lookup score is then *misread* as "the candidate is doing
  something lookup can't" — when in fact it only shows lookup memorizes and the split
  hid that.
- **Cheapest fair baseline that exploits it:** a *generalizing* fair baseline on the
  same split — legal-channel compute (A1) or a fitted classical learner (A4) — which
  ignores context identity and recomputes the target.
- **Static scanner signal:** lookup/NN producers are keyed on context ids that are
  disjoint across the declared split (`train_context_memorization` sketch class), and no
  compute/fitted member shares that split.
- **Required micro-probe baseline:** a memorizing lookup **and** a generalizing
  compute/fitted baseline evaluated on the **identical heldout split** as the candidate.
- **False-positive headroom signature:** lookup/NN low on heldout + candidate high →
  reads as headroom; but a compute baseline on the same heldout is also high.
- **Minimal reject condition:** if a generalizing fair baseline reaches the oracle band
  on the heldout split, reject even though lookup failed → `reject_no_headroom_likely`
  (baseline-saturated). Lookup failure alone never certifies headroom.
- **Grounding:** BATCH-ENV-HEADROOM-SCOUT-002A — under a disjoint signature the lookup
  battery necessarily failed (`transition_table` 0.339), flagged as a "memorize-vs-compute
  artifact," not evidence.
- **Binds-to:** standard §5 (lookup imitation); see also A9 (the split-design dual).

### A4. Fitted classical learner over legal channels

- **Surface pattern it breaks:** a trained classical model (logistic / GBM /
  least-squares / convex solver) over the legal channels reaches the target without the
  proposed mechanism; the surface admits a closed-form or standard-ML solution.
- **Cheapest fair baseline that exploits it:** `discounted_wls` / `least_squares` /
  `convex_solver`, or `supervised_passive_attacker`, or the strongest known classical
  method for the task type.
- **Static scanner signal:** the surface's task type has a known closed-form/classical
  solver AND no fitted learner / classical member is present in the declared battery.
- **Required micro-probe baseline:** a **real fitted** learner with
  `ml_library_used = true`, a recorded fit, and an anti-stub guard, plus the strongest
  classical method. A deterministic baseline merely *labeled* "learned" is invalid.
- **False-positive headroom signature:** either (a) battery omits any fitted/classical
  member → apparent gap, or (b) the "learned" baseline is a deterministic stub
  (`ml_library_used = False`, no fit), so it under-scores and flatters the candidate.
- **Minimal reject condition:** a real fitted classical baseline ≥ oracle − band →
  baseline-saturated; OR an amortized stub is detected → baseline **invalid**, headroom
  cannot be certified until re-run with a genuine fit.
- **Grounding:** ACOLB-001A — candidate was structurally equivalent to a discounted
  weighted least-squares fit (direct-optimizer equivalence). ACSB-001B — the "learned"
  baseline was fully deterministic (no fit), invalidating the comparison.
- **Binds-to:** standard §5 (direct objective optimizer; amortized learner anti-stub).

### A5. Passive decoder leakage

- **Surface pattern it breaks:** the target is decodable from passive observation
  *values* (not just from names), so a same-access passive decoder matches any candidate.
- **Cheapest fair baseline that exploits it:** the passive value-decoder family —
  `value_decoder_mean`, `value_decoder_variance`, `value_decoder_correlation`,
  `value_decoder_pca`, plus `membership_passive_attacker` / `supervised_passive_attacker`
  — scored as `family_max`.
- **Static scanner signal:** `visible_fields_leak_target` AND
  `passive_decoder_likely_reaches_oracle`.
- **Required micro-probe baseline:** the full passive value-decoder family with a
  `family_max` gate. Name-only / observation-only checks are insufficient — the leak is
  at the value level.
- **False-positive headroom signature:** the passive panel ran only name-level or
  `observation_only` members and omitted value decoders, so "no passive leak" is reported
  while a mean/PCA attacker would have hit ceiling.
- **Minimal reject condition:** passive `family_max` ≥ passive-rejection floor (0.87) →
  `reject_passive_decodable` (`rejected_trivially_decodable`).
- **Grounding:** Route C preflight — a value-level observation-decodable self-set leak in
  passive `handle_values` let a legal mean-attacker score 1.0; the earlier name-only
  baseline missed it.
- **Binds-to:** standard §3.2 (direct decodability, value-level family + `family_max`);
  MINIMAL-ENV-SPEC passive family lines 300–302.

### A6. Metric degeneracy / predict_all

- **Surface pattern it breaks:** a single-sided or size-monotone metric (recall-only,
  precision-only, coverage-only, specificity/abstention-only) is saturated by a content-free
  predictor.
- **Cheapest fair baseline that exploits it:** `predict_all` (or `predict_none` /
  `constant_k_sweep` / `size_only_sweep_0_to_n` — whichever the metric rewards).
- **Static scanner signal:** `metric_degenerate`.
- **Required micro-probe baseline:** all degenerate predictors (`predict_all`,
  `predict_none`, `constant_k_sweep`, `random`, `majority`) **and** a `size_only_sweep`,
  scored against a balanced macro-F1 (β=1.0) with per-class precision/recall floors.
- **False-positive headroom signature:** the panel reports a recall-only (or other
  single-sided) score and omits `predict_all` from the fair max, so a degenerate predictor
  equals the oracle but is invisible → manufactured separation.
- **Minimal reject condition:** any degenerate predictor ≥ degenerate-rejection floor
  (0.87) under the reported metric → `rejected_metric_degenerate`.
- **Grounding:** candidate-free Route C separation probe — reported oracle-vs-fair
  "separation" was a false positive because `predict_all` recall = 1.0 = oracle and was
  omitted from the fair panel.
- **Binds-to:** standard §2.1–§2.7 (full metric-degeneracy checklist); MINIMAL-ENV-SPEC
  metric requirement lines 226–251.

### A7. Oracle not budget-faithful

- **Surface pattern it breaks:** the "oracle" used to argue headroom reads the answer
  key, hidden state, future labels, or spends more than the candidate-matched budget, so
  its high score does not represent *fair-channel* headroom and cannot justify promotion.
- **Cheapest fair baseline that exploits it:** the discriminating control is the pair —
  run the **answer-key diagnostic oracle** and the **budget-faithful visible-channel
  oracle** side by side; if only the answer-key version clears the ceiling, fair headroom
  is absent.
- **Static scanner signal:** `oracle_needs_hidden_state_answer_key_or_future_labels`
  (and `future_label_dependency`).
- **Required micro-probe baseline:** both oracles, with a budget/read audit proving the
  visible-channel oracle reads only legal fields within budget; the answer-key oracle is
  diagnostic-only and may never support re-promotion.
- **False-positive headroom signature:** an answer-key oracle is reported *as if* it were
  the fair oracle, inflating the ceiling above what any legal channel can reach, so every
  fair baseline looks comfortably below it.
- **Minimal reject condition:** if only the answer-key oracle reaches ceiling while the
  budget-faithful visible-channel oracle sits inside the fair-baseline band →
  `blocked_oracle_not_budget_faithful` (answer-key-only oracle gap = stop condition).
- **Grounding:** Route C preflight — `obs_only_baseline` read planted answer-maps / fell
  back to handle position; underpowered-oracle blocker. Standard §4.1: answer-key oracles
  never support re-promotion.
- **Binds-to:** standard §4.1/§4.2/§4.3 (oracle taxonomy + re-promotion rule);
  MINIMAL-ENV-SPEC strongest-false-explanation item "hidden answer key".

### A8. Baseline aliasing / fake battery diversity

- **Surface pattern it breaks:** a battery that *looks* diverse (many named members) is
  actually one weak predictor under many names — members share a code path — and/or the
  mandatory strong members are missing. `battery_max` is then artificially low, so the
  candidate "beats the battery" trivially.
- **Cheapest fair baseline that exploits it:** the *missing* strong member —
  `exhaustive_legal_query` (A1) or a fitted classical learner (A4) — added back to the
  panel.
- **Static scanner signal:** two or more distinctly-named baselines share the same
  `code_path_hash` / `producer_function`; OR a mandatory producer from the
  MINIMAL-ENV-SPEC battery list is absent.
- **Required micro-probe baseline:** a battery-integrity check — (i) `code_path_hash`
  distinctness across named members, (ii) mandatory-producer completeness against the
  spec list, (iii) at least one strong non-aliased member actually present.
- **False-positive headroom signature:** `battery_max` is low, but inspection shows every
  member resolves to one body (e.g. all `predict_from_budget_components`, or stage-2
  members all `_predict_lookup`), and saturating members (`exhaustive_legal_query`,
  `count_table`, `episodic_traversal`, any classical) are simply not in the list.
- **Minimal reject condition:** if any two distinct-named members share a `code_path_hash`,
  OR any mandatory producer is absent → **battery invalid**; headroom cannot be certified
  and the sketch is not promotable until re-run with a complete, non-aliased battery. (An
  aliased member must never count as independent corroboration.)
- **Grounding:** BASELINE-FIRST-HARNESS-001A-R1 — six graph-cache + 15 "fair" members were
  all byte-identical `predict_from_budget_components` aliases predicting the same oracle.
  BATCH-ENV-HEADROOM-SCOUT-002A — stage-2 battery was all `_predict_lookup`, missing
  `exhaustive_legal_query` + `count_table` + `episodic_traversal` + any fitted classical.
- **Binds-to:** standard §5 (strongest fair = max over full applicable battery; aliasing
  forbidden); MINIMAL-ENV-SPEC battery provenance lines 316–318 (each result records
  `producer_function`, `code_path_hash`, consumed_by_final_verdict).

### A9. Train/test split that defeats memory but not compute

- **Surface pattern it breaks:** the split (deliberately or accidentally) is engineered so
  the memory family — lookup, NN, graph-cache — fails on unseen keys, while a compute /
  closed-form baseline still solves the task. Suppressing only the memory family
  manufactures false headroom. (Second-order dual of A3: A3 is about *misreading* a low
  lookup score; A9 is about the *split itself* as the attack vector.)
- **Cheapest fair baseline that exploits it:** legal-channel compute (A1) or a fitted
  classical learner (A4) evaluated on the same heldout split — neither depends on having
  seen the key.
- **Static scanner signal:** the only baselines below the band are memory-family members,
  and no compute/fitted member is evaluated on the heldout split (a "memory-only battery
  on a disjoint split" shape).
- **Required micro-probe baseline:** at least one compute baseline **and** one real fitted
  learner on the **identical heldout split** as the candidate — not just lookup/graph-cache.
- **False-positive headroom signature:** lookup + NN + graph-cache all low on heldout
  (keys unseen) → `battery_max` low → "headroom"; but a compute/fitted baseline on the
  same heldout is high.
- **Minimal reject condition:** a generalizing compute/fitted baseline reaches the oracle
  band on the heldout split → `reject_no_headroom_likely` despite memory-family failure.
- **Grounding:** BATCH-ENV-HEADROOM-SCOUT-002A — disjoint signature forced the lookup
  battery to fail (`transition_table` 0.339), the canonical memorize-vs-compute artifact;
  generalizes the standard §3.5 seed-disjointness discipline into a battery-coverage rule.
- **Binds-to:** standard §5 (battery must include compute + fitted, not only memory) and
  §3.5 (declared seed partitions); A3 (the interpretation dual).

---

## Cross-Walk (family → existing detector / verdict / producer / clause)

| Attack | Stage-1 static criterion | Stage-2 micro-probe verdict | Key battery producer(s) | Standard clause |
|---|---|---|---|---|
| A1 direct legal-channel compute | `target_deterministic_from_le_budget_visible_channels`; `legal_query_can_read_all_target_components` | `reject_direct_decode` | `exhaustive_legal_query` | §3.1, §4.2 |
| A2 graph-cache saturation | `graph_cache_transition_table_recovers_target_exactly`; `state_space_small_enough_for_trivial_lookup_saturation` | `reject_graph_cache_saturated` | six graph-cache members | §5 |
| A3 lookup under memorization split | (`train_context_memorization`) | `reject_no_headroom_likely` | lookup + compute on same split | §5, §3.5 |
| A4 fitted classical learner | (task admits classical solver; learner absent) | `reject_no_headroom_likely` / saturated | `discounted_wls`, `least_squares`, classical | §5 |
| A5 passive decoder leakage | `visible_fields_leak_target`; `passive_decoder_likely_reaches_oracle` | `reject_passive_decodable` | passive value-decoder `family_max` | §3.2 |
| A6 metric degeneracy / predict_all | `metric_degenerate` | `reject_metric_degenerate` | `predict_all`/`predict_none`/`size_only_sweep` | §2.1–§2.7 |
| A7 oracle not budget-faithful | `oracle_needs_hidden_state_answer_key_or_future_labels`; `future_label_dependency` | `blocked_oracle_not_budget_faithful` | answer-key + budget-faithful oracle pair | §4.1–§4.3 |
| A8 baseline aliasing / fake diversity | (shared `code_path_hash`; missing mandatory producer) | (battery-invalid — no promote) | `code_path_hash` distinctness + completeness | §5 |
| A9 split defeats memory not compute | (memory-only battery on disjoint split) | `reject_no_headroom_likely` | compute + fitted on heldout split | §5, §3.5 |

Parenthesised static criteria have **no existing stage-1 detector** in
`static_kill_scan.json` (A3 is an inference from the `train_context_memorization` sketch
class; A4/A8/A9 are gaps). That absence is a finding: the current scout would not statically
kill these — they rely on the micro-probe battery being complete. Building stage-1 detectors
for them is out of scope here and needs its own authorized card.

## Composite / second-order notes (not new families)

- **Aliasing amplifies everything.** A8 is a force multiplier: any of A1–A7's "required
  micro-probe baseline" can be present *in name* but aliased to a weak body, re-opening the
  attack it was supposed to close. Battery-integrity (A8) should run before trusting any
  other family's negative result.
- **Oracle faithfulness gates the whole panel.** If A7 fires, every "below oracle" margin
  in the panel is suspect, because the ceiling itself is wrong. Check A7 before reading any
  margin as headroom.
- **A1/A3/A4/A9 are one underlying truth from different angles:** *a fair compute route
  exists and was not put in the battery at full strength.* They are kept separate because
  the detection surfaces differ (legal-channel determinism; split design; classical
  solvability; memory-suppressing split).

## How To Use Without Promotion

1. Treat this as a checklist of *controls to demand*, not a pass certificate. A sketch is
   never "cleared" by reading this file.
2. For any future scouting card, require that each applicable family's **required
   micro-probe baseline** is callable, fail-able, and consumed by the final verdict
   (MINIMAL-ENV-SPEC lines 68–70). A control that cannot fail is not a control.
3. Lowest-cost validation of *this library itself*: pick one already-rejected sketch from
   `artifacts/batch_env_headroom_scout_002a/rejected_sketches.json` and confirm the family
   that should catch it is present here with a matching reject condition. (Brainstorming
   check only — not an executable harness, and not authorized to run as one.)

## What This Does Not Prove / Non-Authorization

This file does not prove that any environment has headroom, that any attack family is
exhaustively covered, or that the existing scout is sufficient. It does not authorize: a
candidate environment, sketch promotion, route tournament, candidate implementation, a new
static detector, an enforcement harness, threshold/metric tuning, EGO mainline / runtime /
admission work, LLM/AIRI integration, or any commit, push, tag, or remote anchor. Converting
any part of this into a runnable checker or registry requires a separate, independently
audited bounded task card. Auto-Remote-Anchor: forbidden.
