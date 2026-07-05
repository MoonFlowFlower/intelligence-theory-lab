# LRGG-CANDIDATE-FREE-TIER0-2-OPERATOR-FREEZE-RESOLUTION-PROPOSAL-001A

Task ID: `LRGG-CANDIDATE-FREE-TIER0-2-OPERATOR-FREEZE-RESOLUTION-PROPOSAL-001A`

Status: operator-facing freeze-resolution proposal only. Not a freeze. Not an implementation.
Not a run. Not a manifest write.

Auto-Remote-Anchor: forbidden.

## Verdict

```text
freeze_resolution_package_proposed_for_operator_review
```

Qualifier (non-blocking to this proposal, blocking to the downstream manifest write):
one of six canonical sources (`LRGG-CANDIDATE-FREE-PREFLIGHT-001A.md`) could not have its
byte-level SHA256 reconciled inside this sandbox because the mount serves a FUSE-truncated
copy. Full content was read via the authoritative file API and is internally consistent, so
content-readback succeeded and the package is proposable; but the recorded SHA `764063…` must
be re-confirmed on a non-truncating filesystem before Codex writes any value into the freeze
manifest. See Source Readback Summary.

## Status Block

Current layer:

```text
engineering-governance / operator freeze-resolution proposal
```

Mainline integration status:

```text
none
```

Enabled status:

```text
none
```

This proposal enables no generator, scorer, oracle, baseline, replay, leakage scanner,
provenance checker, tamper probe, training path, Gate run, commit, push, tag, remote anchor,
or EGO path. It writes no value into the freeze manifest.

Real trigger evidence:

```text
- LRGG-CANDIDATE-FREE-TIER0-2-FREEZE-PROPOSAL-TABLE-001A.md exists and was R-A/R-B repaired.
- One-point confirm verdict on that repair: confirm_accept_repair_closed_for_operator_resolution.
- Freeze manifest LRGG-CANDIDATE-FREE-TIER0-2-FREEZE-MANIFEST-001A.md still has all 31 fields
  = UNFROZEN_OPERATOR_REQUIRED.
- Implementation/run remains blocked.
- No generator/scorer/oracle/baseline/replay/leakage/tamper/artifact/commit/push/tag/remote
  anchor exists or is authorized.
```

Claim ceiling:

```text
This request may only propose an operator freeze-resolution package for the 31 manifest
fields. It does not fill the manifest, implement, run, authorize Tier 0-2 execution,
authorize candidate work, authorize Tier 3+, or authorize 001C. It emits no LRGG
admissibility / headroom / oracle-validity / mechanism / EGO / agency / self / subjectivity /
emotion / consciousness / autonomy claim, and no H0/H1 or TLGP-001B-R2 reinterpretation.
```

## Source Readback Summary

Repo state at this readback:

```text
branch = codex/meta-theory-scaffold
HEAD   = 5c03e0af7ce097d9055de5f1ef17052fe3a576be   (unchanged vs proposal-table readback)
git index = partially corrupted (`error: improper chunk offset(s) 476c and 4c38`); ~2813
            porcelain entries; PREFLIGHT card shows as untracked `??` (never committed blob).
```

Per-source SHA256 (UPPER), current vs proposal-table-recorded:

| Source file | recorded (table) | current (file API basis) | status |
|---|---|---|---|
| `LRGG-CANDIDATE-FREE-PREFLIGHT-001A.md` | `764063…2876E47` | UNRECONCILED (mount truncates) | content read in full via file API; byte-SHA not reproducible in sandbox |
| `LRGG-CANDIDATE-FREE-CHEAP-TIER-EXECUTION-001A.md` | `EF80C6D8…E3DF0` | `EF80C6D8…E3DF0` | verified identical |
| `LRGG-CANDIDATE-FREE-TIER0-2-FREEZE-MANIFEST-001A.md` | `ADB72E04…9ADF5B` | `ADB72E04…9ADF5B` | verified identical |
| `LRGG-CANDIDATE-FREE-TIER0-2-IMPLEMENTATION-RUN-001A.md` | `73464BFE…A4BDD` | `73464BFE…A4BDD` | verified identical |
| `BASELINE-IMMUNITY-ADMISSION-STANDARD-001A.md` | `7BD41A04…E80A03` | `7BD41A04…E80A03` | verified identical |
| `BASELINE-IMMUNITY-ADMISSION-STANDARD-001A.registry.json` | `4A3170DE…E899B43F` | `4A3170DE…E899B43F` | verified identical |

PREFLIGHT discrepancy — fact vs inference:

```text
FACT: file-API Read returns 1241 lines, coherent, ending at "...TLGP-001B-R2 reinterpretation."
FACT: mount (cat/wc/stat/python) returns 32217 bytes / 920 lines, ending mid-word at
      "- task-family ID expo" (≈ file-API line 921).
FACT: mount SHA = 3E6522AB… ; recorded SHA = 764063… ; the two do not match.
FACT: file is git-untracked; `git show HEAD:<path>` is empty; git index is corrupted.
INFERENCE (strong): the mount is serving a truncated copy (FUSE truncation illusion already
      recorded in this lab's lessons). A document ending mid-word inside a bulleted list is
      not a real file ending; the 1241-line file-API version is the real file.
UNKNOWN: whether the full file-API content's byte-SHA equals the recorded 764063…. It cannot
      be recomputed here because the only hashing path (bash) reads through the truncating
      mount. This is a provenance-confirmation gap, not a content-readback failure.
```

Required reconciliation before any manifest write (operator-side, non-truncating filesystem):

```text
On the real filesystem (e.g. Windows), recompute:
  certutil -hashfile docs\codex\tasks\LRGG-CANDIDATE-FREE-PREFLIGHT-001A.md SHA256
and confirm it equals 764063172F264939FCAA5AEDD3C02AC72659A4B9FED281759E6DBE4502876E47.
If it matches: provenance closed, proceed to operator freeze decisions.
If it does not match: PREFLIGHT drifted since the proposal table; re-audit before freezing,
because PREFLIGHT is a rule source for ~half of these fields.
```

Registry parse status: `registry_json_parse = ok` (SHA verified identical to table record).

## How To Read This Proposal (Discipline)

```text
1. A proposal is not a freeze. The operator must explicitly accept each value/rule before
   Codex writes it into the manifest. Until then every field stays UNFROZEN_OPERATOR_REQUIRED.
2. This proposal freezes STRUCTURE (rule form, failure label, coupling, measure definition).
   It does NOT invent numeric bands that have no source basis. Inventing a number with no
   source would itself be the post-hoc-threshold failure family this lab forbids.
3. Therefore many fields read: "rule-form freezable now; numeric band = operator-required."
   That is intentional, not an omission.
4. Nothing here may be tuned after results. Any threshold/metric/split/budget/aggregation
   changed after seeing outputs invalidates the run.
5. Tier 0-2 cheap-tier may emit ONLY: rejected_metric_degenerate, rejected_no_fair_signal,
   rejected_trivially_decodable, rejected_baseline_saturated, INVALID,
   blocked_pending_canonical_readback, blocked_pending_operator_freeze,
   cheap_tier_plumbing_valid_not_saturated__proceed_to_separately_authorized_heavier_tiers.
6. Forbidden everywhere (this proposal and any future Tier 0-2 result): admissible_for_
   candidate_preflight, pass, ready, integrated, live, mechanism-valid, EGO-ready,
   001C-authorized.
```

## Special Section: Measure Definitions (read before the entropy / enumerability fields)

A bare number is invalid for `minimum_task_space_entropy` and `max_enumerability_bound`.
The measured object is defined here first; the numeric bound remains operator-required.

### M1. `minimum_task_space_entropy` — measured random variable

```text
Random variable: T = (G, R) — the latent task configuration the agent must infer per
  episode/context, where G is the hidden rule graph (from the generator's graph space) and R
  is the observation/action remapping (from the generator's remapping space). C (context) may
  be appended if contexts carry independent latent structure: T = (G, R, C).
Distribution: P_gen = the FROZEN generator's declared sampling distribution over T on the
  debug split (specification-derived, not estimated from run outputs).
Measure: H(T) = -Σ_t P_gen(t) log2 P_gen(t), in bits. Also report effective support size
  2^{H(T)} and the realized distinct-T count on the frozen seed×context budget.
Why this is the right space for Tier 0-2 cheap-tier debug: the cheap collapse families that
  the gate must catch (six-member graph_cache, exhaustive_legal_probe, lookup, trajectory
  nearest-neighbor) all saturate exactly when the latent configuration space is small enough
  to be covered/memorized. H(T) is the quantity that governs that coverage; observation-string
  entropy or reward entropy would NOT, because a high-entropy observation stream can still
  carry a tiny enumerable latent.
INVALID / rejected conditions:
  - INVALID if P_gen over T is not declared (entropy of an undefined RV is unmeasurable), or
    if the generator cannot enumerate/sample T to estimate H(T).
  - rejected_baseline_saturated if, despite nominal H(T), the REALIZED distinct-T support on
    the frozen budget is small enough that exhaustive_legal_probe or any graph_cache member
    reaches the oracle band (effective-entropy collapse).
Threshold form (numeric operator-required): freeze H_min (bits) such that the realized
  effective support 2^{H(T)} strictly exceeds the combined coverage capacity of the
  enumerable baselines under the frozen seed×context budget (couples to M2 and to the seed/
  context counts). H_min itself is operator-required; the rule that ties H_min above
  enumerable coverage capacity is freezable now.
```

### M2. `max_enumerability_bound` — measured space

```text
Measured space: N_enum = the count of distinct legal objects a cheap exhaustive baseline can
  traverse to saturate the metric under legal access and the frozen per-decision/per-episode
  budget B. Two co-declared instantiations, both required:
    (a) N_enum^action  = number of distinct legal action/query sequences an
        exhaustive_legal_probe enumerates within budget B per decision;
    (b) N_enum^latent  = number of distinct latent configurations T reachable / coverable
        under the debug budget (ties to M1's realized support).
Why this is the right space for Tier 0-2: §8 "exhaustive legal probe on reduced worlds" and
  the graph_cache_family saturate precisely when N_enum is small enough to be fully covered
  within budget. Bounding N_enum from BELOW (it must be large relative to budget) is what
  prevents enumeration from reaching the oracle band. Measuring some unrelated space (e.g.
  raw state count) would not bound the actual cheap attack.
INVALID / rejected conditions:
  - measure-definition gap (space not declared) blocks with operator-required measure first.
  - if N_enum (either instantiation) is small enough that exhaustive_legal_probe or cheap
    enumeration reaches the oracle band → rejected_baseline_saturated.
Threshold form (numeric operator-required): freeze a minimum N_enum (or equivalently a max
  coverage fraction = budget / N_enum) such that exhaustive enumeration cannot cover the
  space within budget B. The rule is freezable now; the numeric bound and B are
  operator-required and must be frozen before results.
```

## Proposed 31-Field Freeze Package

Each field lists the 11 required attributes. "operator can freeze now" distinguishes the
freezable rule-form from any operator-required numeric. "needs Codex manifest write after
acceptance" is YES for every field (conditional on operator acceptance AND PREFLIGHT
provenance reconciliation); no field is written before that.

### Group A — Oracle & metric core

---

**A1. `tau_oracle`**

1. field_name: `tau_oracle`
2. proposed_frozen_value_or_rule: NO numeric proposed (NO_SAFE_PROPOSAL__OPERATOR_REQUIRED).
   Rule form (freezable): tau_oracle is the near-ceiling solvability floor the
   `budget_faithful_visible_channel_oracle` must clear on the debug split under legal access.
   It is NOT a headroom threshold and must not be compared to any candidate. It must be frozen
   jointly with `oracle_failability_band` (see A2) so that `oracle ≥ tau_oracle` and
   `oracle − nonreading_oracle ≥ oracle_failability_band` are simultaneously satisfiable.
3. type: numeric threshold (operator-required) with a freezable selection rule.
4. rationale: sources require oracle solvability and a frozen tau but supply no number; a
   number chosen here would be post-hoc with no source authority.
5. coupled_fields: `oracle_failability_band`, `random_majority_ceiling` (chance/baseline band),
   `metric_balance_rule` (tau is metric-relative).
6. failure_behavior: `INVALID` if oracle cannot reach tau_oracle on the debug split.
7. risk_if_too_weak: a low tau lets an underpowered/non-reading oracle pass and makes invalid
   plumbing look usable.
8. risk_if_too_strict: a high tau falsely blocks a debug split before plumbing is even tested.
9. why pre-result / non-post-hoc: frozen before any score is produced; selection rule is
   stated independent of outputs and may not be relaxed after seeing the oracle score.
10. operator can freeze now: rule YES; numeric NO — operator must supply tau_oracle (Claude/
    independent design input recommended given no source number).
11. needs Codex manifest write after acceptance: yes.

---

**A2. `oracle_failability_band`**

1. field_name: `oracle_failability_band`
2. proposed_frozen_value_or_rule: Rule form (freezable): require
   `budget_faithful_visible_channel_oracle − nonreading_oracle ≥ band`, where nonreading_oracle
   is the oracle with its latent-estimation path disabled/zeroed/shuffled while legal
   observation/action/intervention access is preserved; the ablated oracle must collapse to the
   chance/baseline band. Numeric `band` operator-required.
3. type: numeric threshold (operator-required) with freezable ablation rule.
4. rationale: makes the oracle fail-able; blocks a non-reading or truth-leaking oracle from
   being accepted (PREFLIGHT R5; EXECUTION §5).
5. coupled_fields: `tau_oracle` (joint feasibility), `random_majority_ceiling` (collapse band),
   `import_path_audit_alarm_rule` (oracle must not read truth).
6. failure_behavior: `INVALID` if the gap is below band or the nonreading ablation fails to
   collapse.
7. risk_if_too_weak: a small band lets a partially-reading oracle pass as legitimate.
8. risk_if_too_strict: an over-large band invalidates a legitimate but noisy oracle ablation.
9. why pre-result / non-post-hoc: ablation contract and band are frozen before the oracle is
   scored; the nonreading run is a real rerun, not a post-hoc edit.
10. operator can freeze now: rule YES; numeric band NO — operator-required.
11. needs Codex manifest write after acceptance: yes.

---

**A3. `random_majority_ceiling`**

1. field_name: `random_majority_ceiling`
2. proposed_frozen_value_or_rule: Rule form (freezable): freeze a pre-output ceiling/no-signal
   band; run random (matched on marginal/size) and majority/mode; if either reaches the band,
   emit `rejected_no_fair_signal`. Numeric band operator-required.
3. type: numeric threshold (operator-required) with freezable block rule (baseline-immunity
   §2.5, §5 trivial predictors).
4. rationale: random/majority near ceiling means the metric carries no fair signal to
   discriminate; canonical "no signal" tell.
5. coupled_fields: `metric_balance_rule` (matched marginal), `trivial_predictor_oracle_band_threshold`,
   `tau_oracle` / `oracle_failability_band` (defines the collapse band reference).
6. failure_behavior: `rejected_no_fair_signal`.
7. risk_if_too_weak: a weak ceiling lets no-signal distributions proceed.
8. risk_if_too_strict: an over-strict ceiling rejects noisy but usable debug signal.
9. why pre-result / non-post-hoc: random/majority are size/marginal-matched by a pre-declared
   rule; band frozen before outputs.
10. operator can freeze now: rule YES; numeric band NO — operator-required.
11. needs Codex manifest write after acceptance: yes.

---

**A4. `trivial_predictor_oracle_band_threshold`**

1. field_name: `trivial_predictor_oracle_band_threshold`
2. proposed_frozen_value_or_rule: Rule form (freezable): if `predict_all`, `predict_none`, or
   any `constant_k_sweep` member (k over [0..|set|] / relevant cardinality) reaches the
   operator-frozen oracle/ceiling band or defeats the declared metric, emit
   `rejected_metric_degenerate`. Numeric band operator-required.
3. type: numeric threshold (operator-required) with freezable degeneracy rule (baseline-immunity
   §2.1–§2.3, §2.6).
4. rationale: protects against recall-only, abstention-only, and fixed-size metric degeneracy
   before any candidate work.
5. coupled_fields: `metric_balance_rule`, `random_majority_ceiling`, `aggregation_method`
   (family decisions), `max_enumerability_bound` (k sweep cardinality).
6. failure_behavior: `rejected_metric_degenerate`.
7. risk_if_too_weak: trivial predictors hide inside the metric.
8. risk_if_too_strict: harmless constant baselines rejected on noise.
9. why pre-result / non-post-hoc: degeneracy controls and k-sweep are declared before outputs;
   produced by callable triviality checks, not a static label.
10. operator can freeze now: rule YES; numeric band NO — operator-required.
11. needs Codex manifest write after acceptance: yes.

---

**A5. `metric_balance_rule`**

1. field_name: `metric_balance_rule`
2. proposed_frozen_value_or_rule: Rule form (freezable): use a balanced or cost-weighted metric
   with `predict_all`, `predict_none`, and `constant_k_sweep` controls visible; no single-sided
   recall-only or precision-only metric. Acceptable forms: predeclared F-beta with stated beta;
   joint precision+recall with trivial-predictor controls; or an operator-frozen cost model.
   The beta / cost weights are operator-required before results.
3. type: measure definition + threshold (form freezable; numeric beta/weights operator-required).
4. rationale: a single-sided or size-monotone metric is saturable by set size, abstention, or
   all-positive prediction (baseline-immunity §2.6, §2.7; PREFLIGHT R1).
5. coupled_fields: `trivial_predictor_oracle_band_threshold`, `random_majority_ceiling`,
   `tau_oracle`, `aggregation_method`.
6. failure_behavior: `rejected_metric_degenerate`.
7. risk_if_too_weak: metric saturated by size/abstention/all-positive prediction.
8. risk_if_too_strict: over-penalizes legitimate oracle behavior and blocks a valid split.
9. why pre-result / non-post-hoc: metric form frozen before outputs and checked against trivial
   predictors; beta/weights cannot be chosen after seeing scores.
10. operator can freeze now: form YES; numeric beta/weights NO — operator-required.
11. needs Codex manifest write after acceptance: yes.

### Group B — Baseline block thresholds (saturation → negative evidence, never tuning)

---

**B1. `obs_only_block_threshold`**

1. field_name: `obs_only_block_threshold`
2. proposed_frozen_value_or_rule: Rule form (freezable): if the observation-only / passive
   visible-channel baseline reaches the operator-frozen block band, emit
   `rejected_trivially_decodable` (if it indicates passive determination of the target) or
   `rejected_no_fair_signal` (if it indicates no separable signal). `memoryless_policy` is
   governed by THIS threshold (current-observation-only / no-history / no-cross-episode-memory
   baseline). Numeric band operator-required.
3. type: numeric threshold (operator-required) with freezable block rule + memoryless mapping
   (baseline-immunity §3.1–§3.2).
4. rationale: prevents visible/passive-channel decodability from being mistaken for headroom.
5. coupled_fields: `raw_observation_latent_decodability_ceiling`, `value_level_attacker_family_max_rule`,
   `observation_field_audit_alarm_rule` (legal-access parity).
6. failure_behavior: `rejected_trivially_decodable` or `rejected_no_fair_signal`.
7. risk_if_too_weak: passive leakage / visible target determination slips through.
8. risk_if_too_strict: rejects a split with residual but noisy passive signal.
9. why pre-result / non-post-hoc: obs-only access defined by a pre-declared legal-access spec;
   band frozen before outputs.
10. operator can freeze now: rule + memoryless mapping YES; numeric band NO — operator-required.
11. needs Codex manifest write after acceptance: yes.

---

**B2. `lookup_graph_cache_block_threshold`**

1. field_name: `lookup_graph_cache_block_threshold`
2. proposed_frozen_value_or_rule: Rule form (freezable): if lookup or any of the six
   graph_cache members (`graph_lookup`, `transition_table`, `successor_map`, `count_table`,
   `fsm_planner`, `episodic_traversal`) reaches the oracle-equivalence band, emit
   `rejected_baseline_saturated`. `trajectory_nearest_neighbor` is governed by THIS threshold
   (episode/trajectory retrieval / nearest-neighbor lookup over legal visible histories).
   Numeric band operator-required.
3. type: numeric threshold (operator-required) with freezable block rule + NN mapping
   (baseline-immunity §5 graph-cache; mandatory six-member family).
4. rationale: canonical cheap-collapse control for representational/environment claims.
5. coupled_fields: `n_gram_block_threshold`, `max_enumerability_bound`, `minimum_task_space_entropy`,
   `latent_graph_exposure_alarm_threshold`.
6. failure_behavior: `rejected_baseline_saturated`.
7. risk_if_too_weak: graph-cache/NN saturation masquerades as headroom.
8. risk_if_too_strict: blocks when graph-cache is close but clearly sub-oracle under noise.
9. why pre-result / non-post-hoc: all six members run with legal-access parity by pre-declared
   spec; band frozen before outputs.
10. operator can freeze now: rule + NN mapping YES; numeric band NO — operator-required.
11. needs Codex manifest write after acceptance: yes.

---

**B3. `direct_objective_optimizer_block_threshold`**

1. field_name: `direct_objective_optimizer_block_threshold`
2. proposed_frozen_value_or_rule: Rule form (freezable): if any direct objective optimizer
   (`discounted_wls`, `least_squares`, `convex_objective_solver`) under legal access reaches the
   oracle-equivalence band, emit `rejected_baseline_saturated`. Numeric band operator-required.
3. type: numeric threshold (operator-required) with freezable block rule (baseline-immunity §5;
   ACOLB-A direct-optimizer equivalence grounding).
4. rationale: controls the false explanation that the surface is solved by direct metric
   optimization rather than a mechanism.
5. coupled_fields: `task_specific_classical_block_threshold`, `metric_balance_rule`, `tau_oracle`.
6. failure_behavior: `rejected_baseline_saturated`.
7. risk_if_too_weak: closed-form objective solving appears mechanism-like.
8. risk_if_too_strict: rejects when optimizers are near but not equivalent.
9. why pre-result / non-post-hoc: optimizers are independent callable implementations at frozen
   strength; band frozen before outputs.
10. operator can freeze now: rule YES; numeric band NO — operator-required.
11. needs Codex manifest write after acceptance: yes.

---

**B4. `task_specific_classical_block_threshold`**

1. field_name: `task_specific_classical_block_threshold`
2. proposed_frozen_value_or_rule: Rule form (freezable): if a hand-coded DP solver,
   finite-state filter, or classical planner under legal access reaches the oracle-equivalence
   band, emit `rejected_baseline_saturated`. The classical baseline must be the strongest known
   legal method for the task type. Numeric band operator-required.
3. type: numeric threshold (operator-required) with freezable block rule (baseline-immunity §5).
4. rationale: blocks task-specific classical solutions from being reinterpreted as mechanism
   evidence.
5. coupled_fields: `direct_objective_optimizer_block_threshold`, `tau_oracle`.
6. failure_behavior: `rejected_baseline_saturated`.
7. risk_if_too_weak: a classical solver saturates the task while the route proceeds.
8. risk_if_too_strict: rejects when classical methods are informative but non-saturating.
9. why pre-result / non-post-hoc: classical baseline strength is fixed by pre-declared spec;
   band frozen before outputs.
10. operator can freeze now: rule YES; numeric band NO — operator-required.
11. needs Codex manifest write after acceptance: yes.

---

**B5. `n_gram_block_threshold`**

1. field_name: `n_gram_block_threshold`
2. proposed_frozen_value_or_rule: Rule form (freezable): if an n-gram / short-history cache
   (with a pre-declared history-length sweep) reaches the operator-frozen block band, emit
   `rejected_baseline_saturated`. Numeric band + sweep range operator-required.
3. type: numeric threshold (operator-required) with freezable block rule (baseline-immunity §5
   lookup imitation).
4. rationale: blocks short-history memorization from being mistaken for structural inference.
5. coupled_fields: `lookup_graph_cache_block_threshold`, `max_enumerability_bound`.
6. failure_behavior: `rejected_baseline_saturated`.
7. risk_if_too_weak: local-history cache saturation passes.
8. risk_if_too_strict: rejects when n-gram is sub-oracle with meaningful residual.
9. why pre-result / non-post-hoc: history-length sweep declared before outputs; band frozen.
10. operator can freeze now: rule YES; numeric band + sweep NO — operator-required.
11. needs Codex manifest write after acceptance: yes.

---

**B6. `raw_observation_latent_decodability_ceiling`**

1. field_name: `raw_observation_latent_decodability_ceiling`
2. proposed_frozen_value_or_rule: Rule form (freezable): if a raw-observation latent decoder OR
   the value-level attacker `family_max` (see G10) reaches the ceiling, emit
   `rejected_trivially_decodable`. Probes must cover value-level AND structural features, not
   names only. Numeric ceiling operator-required.
3. type: numeric threshold (operator-required) with freezable decodability rule (baseline-immunity
   §3.2; PREFLIGHT R6).
4. rationale: the decodability wall — raw observations must not directly reveal the latent target.
5. coupled_fields: `value_level_attacker_family_max_rule` (this ceiling is enforced by family_max),
   `obs_only_block_threshold`, `observation_field_audit_alarm_rule`.
6. failure_behavior: `rejected_trivially_decodable`.
7. risk_if_too_weak: latent leakage becomes apparent headroom.
8. risk_if_too_strict: rejects noisy but non-saturating latent signals.
9. why pre-result / non-post-hoc: decoder/attacker family fixed before outputs; family_max
   prevents post-hoc attacker cherry-picking.
10. operator can freeze now: rule YES; numeric ceiling NO — operator-required.
11. needs Codex manifest write after acceptance: yes.

### Group C — Debug-split design

---

**C1. `cheap_tier_debug_split_seed_count`**

1. field_name: `cheap_tier_debug_split_seed_count`
2. proposed_frozen_value_or_rule: NO numeric proposed (NO_SAFE_PROPOSAL__OPERATOR_REQUIRED).
   Rule form (freezable): the seed count must be (a) large enough that the LCB rule (D2) is
   valid at the frozen confidence level and that leakage/cache attacks have power to fire, and
   (b) small enough to remain cheap-tier debug. It must be co-frozen with the context count and
   with the entropy/enumerability bounds so that seed×context samples do not enumerate the task
   space.
3. type: numeric (split design parameter), operator-required; selection rule freezable.
4. rationale: sources require the count be frozen but provide no defensible number.
5. coupled_fields: `cheap_tier_debug_split_context_count`, `confidence_interval_lower_confidence_bound_rule`,
   `minimum_task_space_entropy`, `max_enumerability_bound`.
6. failure_behavior: `blocked_pending_operator_freeze` while unset.
7. risk_if_too_weak: too few seeds miss leakage, cache saturation, or variance.
8. risk_if_too_strict: too many seeds exceed the intended debug budget (drifts toward a heavier
   unauthorized run).
9. why pre-result / non-post-hoc: count fixed before generation; cannot be adjusted after seeing
   scores.
10. operator can freeze now: rule YES; numeric NO — operator must supply (Claude/independent
    sizing input recommended, tied to the LCB estimator).
11. needs Codex manifest write after acceptance: yes.

---

**C2. `cheap_tier_debug_split_context_count`**

1. field_name: `cheap_tier_debug_split_context_count`
2. proposed_frozen_value_or_rule: NO numeric proposed (NO_SAFE_PROPOSAL__OPERATOR_REQUIRED).
   Rule form (freezable): context count must be large enough that the split is not a memorized /
   enumerable toy (couple to entropy H(T) and graph-family coverage) and small enough to stay
   cheap-tier. Co-frozen with seed count.
3. type: numeric (split design parameter), operator-required; selection rule freezable.
4. rationale: sources require freezing but provide no defensible number.
5. coupled_fields: `cheap_tier_debug_split_seed_count`, `minimum_task_space_entropy`,
   `max_enumerability_bound`, `lookup_graph_cache_block_threshold`.
6. failure_behavior: `blocked_pending_operator_freeze` while unset.
7. risk_if_too_weak: too few contexts make the split enumerable/memorizable.
8. risk_if_too_strict: too many contexts convert cheap-tier debug into an unauthorized heavier run.
9. why pre-result / non-post-hoc: count fixed before generation.
10. operator can freeze now: rule YES; numeric NO — operator-required.
11. needs Codex manifest write after acceptance: yes.

---

**C3. `debug_split_seed_ids_or_generation_rule`**

1. field_name: `debug_split_seed_ids_or_generation_rule`
2. proposed_frozen_value_or_rule: Rule form (freezable): freeze either an explicit seed-ID list
   or a deterministic pre-output generation rule (e.g. a fixed function of a frozen master
   seed). Seed IDs must not encode or correlate with hidden rule, family, score key, or split
   membership, and must not become filename/config leakage.
3. type: deterministic generation rule (freezable now once the operator picks list-vs-rule and
   the master seed).
4. rationale: deterministic preregistration prevents post-output seed cherry-picking (PREFLIGHT
   Tier 0; baseline-immunity §3.5).
5. coupled_fields: `cheap_tier_debug_split_seed_count`, `seed_config_filename_leakage_alarm_threshold`,
   `membership_leakage_alarm_threshold`.
6. failure_behavior: `blocked_pending_operator_freeze` while unset; `rejected_trivially_decodable`
   if IDs are later found to leak labels.
7. risk_if_too_weak: seed cherry-picking or split leakage.
8. risk_if_too_strict: over-rigid rule blocks harmless reproducible generation.
9. why pre-result / non-post-hoc: IDs/rule fixed and reproducible before any score.
10. operator can freeze now: YES (rule form is fully specifiable now; operator confirms list or
    master seed).
11. needs Codex manifest write after acceptance: yes.

---

**C4. `debug_split_context_ids_or_generation_rule`**

1. field_name: `debug_split_context_ids_or_generation_rule`
2. proposed_frozen_value_or_rule: Rule form (freezable): freeze explicit context IDs or a
   deterministic pre-output generation rule; require disjointness from any future train/heldout
   context if such splits are later added; context IDs must not encode hidden rule, family, or
   score key.
3. type: deterministic generation rule (freezable now once list-vs-rule + master seed chosen).
4. rationale: avoids post-hoc context selection and future train/test contamination.
5. coupled_fields: `cheap_tier_debug_split_context_count`, `max_train_test_leakage`,
   `membership_leakage_alarm_threshold`.
6. failure_behavior: `blocked_pending_operator_freeze` while unset; `rejected_trivially_decodable`
   on detected hidden overlap/encoding.
7. risk_if_too_weak: context cherry-picking or hidden overlap.
8. risk_if_too_strict: over-rigid rule blocks valid deterministic contexts.
9. why pre-result / non-post-hoc: IDs/rule fixed before outputs; disjointness asserted, not
   inferred after results.
10. operator can freeze now: YES (rule form specifiable now).
11. needs Codex manifest write after acceptance: yes.

### Group D — Aggregation

---

**D1. `aggregation_method`**

1. field_name: `aggregation_method`
2. proposed_frozen_value_or_rule: Rule form (freezable): callable verdict aggregation over
   recorded evidence rows; hard-stop / block conditions DOMINATE any continuous score (a
   triggered stop cannot be averaged away); family baselines decided by `family_max`; no static
   verdict dictionary; the verdict is emitted only by a callable path recording
   `aggregation_code_path_sha256`.
3. type: aggregation rule (freezable now).
4. rationale: non-post-hoc because the aggregation path must be callable and frozen before
   outputs (PREFLIGHT real-trigger requirement; AGENTS computed-evidence gate).
5. coupled_fields: `confidence_interval_lower_confidence_bound_rule`, every block/alarm threshold
   (precedence), `value_level_attacker_family_max_rule`.
6. failure_behavior: `INVALID` if the aggregator is a static dictionary, averages away a blocker,
   or ignores a saturated family member.
7. risk_if_too_weak: a hard blocker or saturated member is averaged away.
8. risk_if_too_strict: any benign warning is escalated to INVALID.
9. why pre-result / non-post-hoc: blocker precedence and family_max semantics implemented in a
   callable aggregator frozen before outputs.
10. operator can freeze now: YES (rule form specifiable now).
11. needs Codex manifest write after acceptance: yes.

---

**D2. `confidence_interval_lower_confidence_bound_rule`**

1. field_name: `confidence_interval_lower_confidence_bound_rule`
2. proposed_frozen_value_or_rule: Rule form (freezable): use a lower-confidence-bound over
   per-(seed,context) evidence; a positive-looking mean that does not clear its LCB cannot
   proceed. The estimator and the confidence level are operator-required and must be valid for
   the frozen seed×context N.
3. type: aggregation rule (form freezable; estimator + confidence level operator-required).
4. rationale: LCB discipline is source-derived; the numeric confidence level is not specified by
   sources (PREFLIGHT R2 LCB language).
5. coupled_fields: `cheap_tier_debug_split_seed_count`, `cheap_tier_debug_split_context_count`,
   `aggregation_method`.
6. failure_behavior: `INVALID` if the LCB is missing/under-specified or invalid for the sample
   size.
7. risk_if_too_weak: noisy positive-looking scores proceed.
8. risk_if_too_strict: a usable split is falsely blocked by small-sample uncertainty.
9. why pre-result / non-post-hoc: estimator and level frozen before outputs; couples to a
   pre-frozen N.
10. operator can freeze now: form YES; estimator + confidence level NO — operator-required.
11. needs Codex manifest write after acceptance: yes.

### Group E — Task-space (see Measure Definitions M1/M2 above)

---

**E1. `max_train_test_leakage`**

1. field_name: `max_train_test_leakage`
2. proposed_frozen_value_or_rule: Rule form (freezable): zero tolerated KNOWN split-membership /
   structural leakage, plus a membership-attacker positive control that MUST alarm on a planted
   leak. Any real leakage above the zero-known-structural rule blocks; a positive control that
   fails to alarm is INVALID (non-fail-able gate). Scanner sensitivity for value-level channels
   operator-required.
3. type: leakage alarm rule (zero-known-structural form freezable; scanner sensitivity
   operator-required).
4. rationale: leakage is source-blocking and must be pre-output fail-able (baseline-immunity
   §3.4–§3.5).
5. coupled_fields: `membership_leakage_alarm_threshold`, `debug_split_context_ids_or_generation_rule`,
   `seed_config_filename_leakage_alarm_threshold`.
6. failure_behavior: `rejected_trivially_decodable` on real leakage; `INVALID` on failed positive
   control.
7. risk_if_too_weak: train/test or split-membership leakage inflates results.
8. risk_if_too_strict: blocks on benign metadata agents cannot access.
9. why pre-result / non-post-hoc: zero-known-structural rule + positive control declared before
   outputs; channels enumerated in advance.
10. operator can freeze now: zero-known-structural rule YES; value-level scanner sensitivity NO —
    operator-required.
11. needs Codex manifest write after acceptance: yes.

---

**E2. `minimum_task_space_entropy`**  (measured RV defined in M1)

1. field_name: `minimum_task_space_entropy`
2. proposed_frozen_value_or_rule: Measure definition = M1 (entropy H(T) in bits of the latent
   task configuration T=(G,R[,C]) under the frozen generator distribution P_gen). Threshold form
   (freezable): require realized effective support 2^{H(T)} to strictly exceed the enumerable
   baselines' coverage capacity under the frozen seed×context budget. Numeric H_min
   operator-required. A bare number with no defined RV is invalid.
3. type: measure definition + threshold (measure freezable now; numeric H_min operator-required).
4. rationale: too little entropy makes enumeration/lookup/cache saturation likely; entropy is
   only meaningful once the random variable is named (PREFLIGHT stop "task space too small").
5. coupled_fields: `max_enumerability_bound`, `cheap_tier_debug_split_seed_count`,
   `cheap_tier_debug_split_context_count`, `lookup_graph_cache_block_threshold`.
6. failure_behavior: `INVALID` if P_gen(T) is undefined/unmeasurable or H(T) < H_min (precondition
   unmeasurable or task space too small).
7. risk_if_too_weak: enumeration/lookup/cache saturate.
8. risk_if_too_strict: debug oracle/scorer validation fails for capacity reasons.
9. why pre-result / non-post-hoc: H(T) computed from the generator SPECIFICATION before runs, not
   estimated from outputs; H_min frozen before results.
10. operator can freeze now: MEASURE DEFINITION YES; numeric H_min NO — operator-required.
11. needs Codex manifest write after acceptance: yes (write both the measure definition and the
    operator H_min).
    INVALID-condition note: failure maps to `INVALID` (unmeasurable precondition / too small).

---

**E3. `max_enumerability_bound`**  (measured space defined in M2)

1. field_name: `max_enumerability_bound`
2. proposed_frozen_value_or_rule: Measure definition = M2 (N_enum^action and N_enum^latent under
   legal access and frozen budget B). Threshold form (freezable): require N_enum (both
   instantiations) large enough — equivalently coverage fraction = budget/N_enum small enough —
   that exhaustive_legal_probe cannot cover the space within B. Numeric bound + B
   operator-required. A bare number with no defined space is invalid.
3. type: measure definition + threshold (measure freezable now; numeric bound operator-required).
4. rationale: a weak bound lets exhaustive legal probe saturate and erase apparent structure;
   enumerability is only meaningful once the space is named.
5. coupled_fields: `minimum_task_space_entropy`, `lookup_graph_cache_block_threshold`,
   `n_gram_block_threshold`, `cheap_tier_debug_split_context_count`.
6. failure_behavior: `rejected_baseline_saturated` when exhaustive legal probe / cheap enumeration
   saturates; measure-definition gap blocks for operator-required measure first.
7. risk_if_too_weak: exhaustive legal probe saturates and erases headroom.
8. risk_if_too_strict: rejects a small debug split before plumbing is tested.
9. why pre-result / non-post-hoc: N_enum computed from generator/action-space SPECIFICATION and
   frozen budget before runs.
10. operator can freeze now: MEASURE DEFINITION YES; numeric bound + B NO — operator-required.
11. needs Codex manifest write after acceptance: yes.
    Reject-condition note: failure maps to `rejected_baseline_saturated`.

### Group F — Tamper

---

**F1. `tamper_probe_expected_behavior`**

1. field_name: `tamper_probe_expected_behavior`
2. proposed_frozen_value_or_rule: Tamper-expectation table (freezable). For each probe declare the
   expected effect BEFORE results:
   - mutate one action → recomputed score changes OR replay detects mismatch;
   - mutate one source byte → source-hash mismatch (provenance trips);
   - mutate hidden graph / remapping → replay or provenance fails;
   - mutate observation trace → recomputed score changes or replay mismatch;
   - mutate reward trace → recomputed score changes or replay mismatch.
   Score must be recomputed from serialized state + action/observation/reward trace; stored-score-
   only evidence is invalid. If a probe that should change score / trip provenance does not, stop.
3. type: tamper expectation (freezable now).
4. rationale: source-derived; protects against stored-score evidence and provenance bypass
   (EXECUTION §11; IMPLEMENTATION-RUN replay/provenance fields).
5. coupled_fields: `import_path_audit_alarm_rule`, `serialized_state_audit_alarm_rule`,
   `aggregation_method` (replay-recomputed score feeds verdict).
6. failure_behavior: `INVALID` if any probe fails its declared expectation.
7. risk_if_too_weak: tampering leaves official evidence unchanged.
8. risk_if_too_strict: fails when a mutation is semantically neutral by design (declare such
   neutrality in advance).
9. why pre-result / non-post-hoc: each tamper class has a declared expected effect frozen before
   outputs; probes are real reruns, not post-hoc edits.
10. operator can freeze now: YES (expectation table specifiable now; operator confirms any
    by-design neutral mutations).
11. needs Codex manifest write after acceptance: yes.

### Group G — Leakage alarm fields (each: planted leak MUST alarm; failed positive control = INVALID)

Common contract for G1–G10 (frozen for all): (i) a planted positive-control leak MUST trigger
the alarm — a non-firing positive control means the gate is non-fail-able → `INVALID`;
(ii) real exposure above the operator-frozen sensitivity → the field's reject label;
(iii) detectors must be value-level AND structural, not name-only. The numeric sensitivity per
field is operator-required; the alarm rule + positive-control requirement + failure label are
freezable now.

---

**G1. `hidden_rule_id_leak_alarm_threshold`**

1. field_name: `hidden_rule_id_leak_alarm_threshold`
2. proposed_frozen_value_or_rule: planted hidden-rule-ID leak MUST alarm; real hidden-rule-ID
   exposure above the frozen alarm rule → `rejected_trivially_decodable`; detector not name-only.
   Numeric sensitivity operator-required.
3. type: leakage alarm rule.
4. rationale: hidden rule ID is a direct side channel (PREFLIGHT/EXECUTION positive controls).
5. coupled_fields: `latent_graph_exposure_alarm_threshold`, `observation_field_audit_alarm_rule`,
   `import_path_audit_alarm_rule`.
6. failure_behavior: `rejected_trivially_decodable` on real leak; `INVALID` on failed positive
   control.
7. risk_if_too_weak: ID leakage solves the task.
8. risk_if_too_strict: flags benign identifiers not visible to agents.
9. why pre-result / non-post-hoc: positive control + sensitivity frozen before outputs.
10. operator can freeze now: rule YES; numeric sensitivity NO — operator-required.
11. needs Codex manifest write after acceptance: yes.

---

**G2. `latent_graph_exposure_alarm_threshold`**

1. field_name: `latent_graph_exposure_alarm_threshold`
2. proposed_frozen_value_or_rule: planted latent-graph exposure MUST alarm; real exposure above
   the frozen rule → `rejected_trivially_decodable`; detector covers graph hashes/IDs/serialized
   fields, not names only. Numeric sensitivity operator-required.
3. type: leakage alarm rule.
4. rationale: latent graph exposure can collapse the task to direct decoding or graph-cache
   saturation.
5. coupled_fields: `lookup_graph_cache_block_threshold`, `serialized_state_audit_alarm_rule`,
   `hidden_rule_id_leak_alarm_threshold`.
6. failure_behavior: `rejected_trivially_decodable` on real leak; `INVALID` on failed positive
   control.
7. risk_if_too_weak: graph exposure masquerades as inference.
8. risk_if_too_strict: blocks benign structural metadata.
9. why pre-result / non-post-hoc: positive control + sensitivity frozen before outputs.
10. operator can freeze now: rule YES; numeric sensitivity NO — operator-required.
11. needs Codex manifest write after acceptance: yes.

---

**G3. `task_family_id_alarm_threshold`**

1. field_name: `task_family_id_alarm_threshold`
2. proposed_frozen_value_or_rule: planted task-family-ID exposure MUST alarm; real exposure above
   the frozen rule → `rejected_trivially_decodable`. Numeric sensitivity operator-required.
3. type: leakage alarm rule.
4. rationale: task-family IDs can route baselines/agents to a hidden shortcut.
5. coupled_fields: `hidden_rule_id_leak_alarm_threshold`, `score_key_reward_shaping_alarm_threshold`.
6. failure_behavior: `rejected_trivially_decodable` on real leak; `INVALID` on failed positive
   control.
7. risk_if_too_weak: family-conditioned lookup passes.
8. risk_if_too_strict: blocks harmless public task metadata.
9. why pre-result / non-post-hoc: positive control + sensitivity frozen before outputs.
10. operator can freeze now: rule YES; numeric sensitivity NO — operator-required.
11. needs Codex manifest write after acceptance: yes.

---

**G4. `score_key_reward_shaping_alarm_threshold`**

1. field_name: `score_key_reward_shaping_alarm_threshold`
2. proposed_frozen_value_or_rule: planted score-key / reward-shaping artifact MUST alarm; real
   exposure above the frozen rule → `rejected_metric_degenerate` (metric-side, not decodability).
   Numeric sensitivity operator-required.
3. type: leakage alarm rule.
4. rationale: score-key exposure lets a baseline optimize the metric rather than infer structure
   (baseline-immunity §2 metric degeneracy).
5. coupled_fields: `metric_balance_rule`, `trivial_predictor_oracle_band_threshold`.
6. failure_behavior: `rejected_metric_degenerate` on real leak; `INVALID` on failed positive
   control.
7. risk_if_too_weak: reward-shaping / score-key leaks create false positives.
8. risk_if_too_strict: rejects legitimate reward observations.
9. why pre-result / non-post-hoc: positive control + sensitivity frozen before outputs.
10. operator can freeze now: rule YES; numeric sensitivity NO — operator-required.
11. needs Codex manifest write after acceptance: yes.

---

**G5. `membership_leakage_alarm_threshold`**

1. field_name: `membership_leakage_alarm_threshold`
2. proposed_frozen_value_or_rule: planted split-membership leak MUST alarm; real membership
   leakage above the frozen rule → `rejected_trivially_decodable`; membership attacker uses only
   legal visible channels. Numeric sensitivity operator-required.
3. type: leakage alarm rule.
4. rationale: membership leakage contaminates debug/heldout interpretation (baseline-immunity
   §3.4–§3.5).
5. coupled_fields: `max_train_test_leakage`, `debug_split_context_ids_or_generation_rule`.
6. failure_behavior: `rejected_trivially_decodable` on real leak; `INVALID` on failed positive
   control.
7. risk_if_too_weak: split membership explains performance.
8. risk_if_too_strict: flags non-agent-visible bookkeeping.
9. why pre-result / non-post-hoc: positive control + sensitivity frozen before outputs.
10. operator can freeze now: rule YES; numeric sensitivity NO — operator-required.
11. needs Codex manifest write after acceptance: yes.

---

**G6. `seed_config_filename_leakage_alarm_threshold`**

1. field_name: `seed_config_filename_leakage_alarm_threshold`
2. proposed_frozen_value_or_rule: planted seed/config/filename leak MUST alarm; real filename or
   config leakage above the frozen rule → `rejected_trivially_decodable`; scanner covers names,
   values, ordering, AND artifact structure. Numeric sensitivity operator-required.
3. type: leakage alarm rule.
4. rationale: filename/config side channels are known leakage families and must be covered beyond
   value fields (baseline-immunity §3.4).
5. coupled_fields: `debug_split_seed_ids_or_generation_rule`, `membership_leakage_alarm_threshold`.
6. failure_behavior: `rejected_trivially_decodable` on real leak; `INVALID` on failed positive
   control.
7. risk_if_too_weak: path/config names carry hidden labels.
8. risk_if_too_strict: blocks ordinary reproducibility metadata not visible to agents.
9. why pre-result / non-post-hoc: positive control + sensitivity frozen before outputs.
10. operator can freeze now: rule YES; numeric sensitivity NO — operator-required.
11. needs Codex manifest write after acceptance: yes.

---

**G7. `observation_field_audit_alarm_rule`**

1. field_name: `observation_field_audit_alarm_rule`
2. proposed_frozen_value_or_rule: observation fields injected with latent/graph/ID truth MUST
   alarm (value-level AND field-name scans, each with its own positive control); real field-level
   leakage → `rejected_trivially_decodable`.
3. type: leakage alarm rule.
4. rationale: direct guard against hidden labels entering legal observations.
5. coupled_fields: `raw_observation_latent_decodability_ceiling`, `value_level_attacker_family_max_rule`,
   `obs_only_block_threshold`.
6. failure_behavior: `rejected_trivially_decodable` on real leak; `INVALID` on failed positive
   control.
7. risk_if_too_weak: labels hide in observation field names or values.
8. risk_if_too_strict: blocks legal observations required by the task.
9. why pre-result / non-post-hoc: both scans + positive controls frozen before outputs.
10. operator can freeze now: rule YES (both-scans + positive-control requirement); any numeric
    value-level sensitivity NO — operator-required.
11. needs Codex manifest write after acceptance: yes.

---

**G8. `serialized_state_audit_alarm_rule`**

1. field_name: `serialized_state_audit_alarm_rule`
2. proposed_frozen_value_or_rule: serialized state embedding generator truth readable by agents
   MUST alarm; real readable truth → `rejected_trivially_decodable`; replay-required state must be
   separated from agent-readable observations.
3. type: leakage alarm rule.
4. rationale: serialized state is part of replay and must not become a hidden answer channel
   (EXECUTION §11).
5. coupled_fields: `tamper_probe_expected_behavior`, `latent_graph_exposure_alarm_threshold`,
   `import_path_audit_alarm_rule`.
6. failure_behavior: `rejected_trivially_decodable` on real leak; `INVALID` on failed positive
   control.
7. risk_if_too_weak: replay state carries direct truth.
8. risk_if_too_strict: blocks necessary replay-state serialization.
9. why pre-result / non-post-hoc: replay/agent-readable separation + positive control frozen
   before outputs.
10. operator can freeze now: rule YES; any numeric sensitivity NO — operator-required.
11. needs Codex manifest write after acceptance: yes.

---

**G9. `import_path_audit_alarm_rule`**

1. field_name: `import_path_audit_alarm_rule`
2. proposed_frozen_value_or_rule: forbidden imports of hidden latent, hidden graph, remapping,
   generator truth, or scorer truth MUST alarm; a failed alarm is `INVALID`. The allow/deny basis
   must not be hardcoded to known names only (must catch structurally equivalent illegal reads).
3. type: leakage alarm rule (failed-alarm → INVALID).
4. rationale: prevents oracle/generator/scorer/future-candidate from reading truth directly
   (EXECUTION §5 oracle contract; baseline-immunity §3.4).
5. coupled_fields: `oracle_failability_band`, `tamper_probe_expected_behavior`,
   `serialized_state_audit_alarm_rule`.
6. failure_behavior: `INVALID` if illegal truth reads occur or the positive control fails to
   alarm.
7. risk_if_too_weak: illegal truth reads produce apparent solvability.
8. risk_if_too_strict: blocks legitimate source hashing or module imports.
9. why pre-result / non-post-hoc: allow/deny rule + positive control frozen before outputs.
10. operator can freeze now: rule YES (allowlist/denylist policy specifiable now).
11. needs Codex manifest write after acceptance: yes.

---

**G10. `value_level_attacker_family_max_rule`**

1. field_name: `value_level_attacker_family_max_rule`
2. proposed_frozen_value_or_rule: compute `family_max` over {mean, variance, correlation, PCA,
   cross-episode, supervised, membership} attackers, all under legal access; if family_max reaches
   the decodability ceiling → `rejected_trivially_decodable`. The supervised attacker must not
   leak labels. The decision is family_max, never a cherry-picked single attacker. Numeric
   ceiling is the same as B6's `raw_observation_latent_decodability_ceiling`.
3. type: leakage alarm rule + measure (family_max).
4. rationale: family_max prevents selecting a weak value-level attacker after outputs
   (baseline-immunity §3.2; PREFLIGHT positive controls).
5. coupled_fields: `raw_observation_latent_decodability_ceiling` (shared ceiling),
   `obs_only_block_threshold`, `observation_field_audit_alarm_rule`.
6. failure_behavior: `rejected_trivially_decodable` on real decode; `INVALID` on failed planted-
   leak positive control.
7. risk_if_too_weak: one attacker decodes while the report cites a weaker one.
8. risk_if_too_strict: one attacker overfits noise on a tiny debug split (mitigated by LCB / N
   coupling).
9. why pre-result / non-post-hoc: full family + family_max rule frozen before outputs.
10. operator can freeze now: rule YES; shared numeric ceiling NO — operator-required (co-frozen
    with B6).
11. needs Codex manifest write after acceptance: yes.

## Explicit Couplings (required coupling map)

These pairs must be frozen jointly; freezing one without the other is incoherent.

```text
tau_oracle  <->  oracle_failability_band
  Joint feasibility: tau_oracle is the oracle solvability floor; oracle_failability_band is the
  minimum (oracle - nonreading_oracle) gap. Both reference the same ceiling and chance/baseline
  band. They are consistent only if tau_oracle sits far enough above the nonreading collapse
  band that the band gap is achievable; a tau set so low it overlaps the collapse band makes the
  oracle simultaneously "passing tau" and "not failable" — contradiction.

seed/context counts  <->  confidence_interval_lower_confidence_bound_rule
  The LCB estimator's validity and width depend on N = seed_count x context_count. You cannot
  freeze a confidence level without N, and you cannot justify N without an LCB width target.

seed/context counts  <->  minimum_task_space_entropy / max_enumerability_bound
  The (seed,context) samples must not instantiate enough of the latent space to let lookup /
  graph-cache / exhaustive probe saturate. Counts couple to H(T) (M1) and N_enum (M2).

raw_observation_latent_decodability_ceiling  <->  value_level_attacker_family_max_rule
  Same ceiling; family_max over {mean,variance,correlation,PCA,cross-episode,supervised,
  membership} is the operationalization that enforces it.

lookup_graph_cache_block_threshold  <->  trajectory_nearest_neighbor
  trajectory_nearest_neighbor (episode/trajectory retrieval / NN lookup over legal visible
  histories) is governed by lookup_graph_cache_block_threshold; failure = rejected_baseline_
  saturated. If a future impl gives it different access/semantics, a dedicated frozen threshold
  must be added before run.

obs_only_block_threshold  <->  memoryless_policy
  memoryless_policy (current-observation-only / no-history / no-cross-episode-memory) is governed
  by obs_only_block_threshold; failure = rejected_trivially_decodable or rejected_no_fair_signal.
  Same boundary condition: different access/semantics require a dedicated frozen threshold.
```

Required-baseline threshold coverage (inherited, restated): every required cheap-tier baseline
must be governed by a frozen threshold or threshold-family mapping before run. A required
baseline with no predeclared threshold mapping → `blocked_pending_operator_freeze`.

## Baseline-Saturation Discipline

Every threshold above is conservative against the full cheap-collapse battery: random/majority
collapse, trivial-predictor saturation, graph-cache saturation (six members), trajectory
nearest-neighbor retrieval, direct objective optimizer, task-specific classical solver, n-gram /
short-history cache, memoryless / obs-only decodability, raw-observation latent decodability,
exhaustive legal probe saturation, and value-level attacker family_max.

```text
If ANY of these saturates the metric (reaches the oracle-equivalence / ceiling band), the result
is NEGATIVE EVIDENCE and the verdict is the corresponding reject label. It is NEVER a reason to
lower a threshold, weaken a baseline, relabel saturation with softer language, or patch the
metric. Saturation is the expected and acceptable outcome of a cheap, honest environment.
```

## Leakage / Replay / Provenance Freeze Requirements

The freeze package requires (frozen for all leakage/replay/provenance fields):

```text
- a fail-able positive control for EVERY leakage alarm (G1-G10, E1): a planted leak MUST flip
  the alarm to blocked. A positive control that cannot fail (e.g. scans a hardcoded dict and is
  structurally always-true) is forbidden; a non-firing positive control = INVALID.
- real leakage above the frozen rule = the field's reject label (mostly
  rejected_trivially_decodable; score-key = rejected_metric_degenerate; import-path failed alarm
  = INVALID).
- replay recomputes the official score from serialized state + action/observation/reward trace;
  stored-score-only evidence is INVALID.
- tamper probes (F1) with declared expected behavior frozen before results; a probe that should
  change the recomputed score / trip provenance but does not = INVALID.
- name-only scanners are insufficient; value-level AND structural channels must be covered.
```

## Fields Safe For Operator Freeze (rule-form ready now)

Rule form / measure / structure is fully specifiable now; for several, an operator-supplied
numeric band remains required before results (noted per field). Operator may accept the rule
form now:

```text
A2 oracle_failability_band (rule)      A3 random_majority_ceiling (rule)
A4 trivial_predictor_oracle_band (rule)  A5 metric_balance_rule (form)
B1 obs_only_block_threshold (rule+map)   B2 lookup_graph_cache_block_threshold (rule+map)
B3 direct_objective_optimizer (rule)     B4 task_specific_classical (rule)
B5 n_gram_block_threshold (rule)         B6 raw_observation_latent_decodability_ceiling (rule)
C3 debug_split_seed_ids_or_generation_rule (FULL)    C4 debug_split_context_ids_rule (FULL)
D1 aggregation_method (FULL)             D2 LCB rule (form)
E1 max_train_test_leakage (rule)
F1 tamper_probe_expected_behavior (FULL)
G1-G10 leakage alarm rules (rule each)
```

"FULL" = rule form is completely freezable now (operator confirms list-vs-rule / master seed /
by-design-neutral mutations); the rest are rule-now / numeric-band-operator-required.

## Fields Still Requiring Design (no source-derivable numeric)

```text
A1 tau_oracle                          -> numeric, operator-required; recommend independent sizing
C1 cheap_tier_debug_split_seed_count   -> numeric, operator-required; tie to LCB estimator
C2 cheap_tier_debug_split_context_count-> numeric, operator-required; tie to H(T) / coverage
E2 minimum_task_space_entropy          -> MEASURE NOW DEFINED (M1); numeric H_min operator-required
E3 max_enumerability_bound             -> MEASURE NOW DEFINED (M2); numeric bound + B operator-required
```

This proposal advances E2/E3 from "no safe proposal" to "measure defined, numeric pending"; it
does not invent the numerics. A1/C1/C2 remain numeric-operator decisions (with the stated
selection rules) because no accepted source supplies a defensible number.

## Strongest Objection

The strongest objection to this package is that it freezes mostly RULE FORM while leaving the
numeric bands operator-required, so an operator could later choose numbers that are individually
"frozen before results" yet jointly weak enough to admit a saturated environment — i.e. the
package's conservatism lives in the numerics it deliberately does not set. Mitigation: the
coupling map and baseline-saturation discipline constrain the numerics relative to each other
(entropy/enumerability vs budget; tau vs failability band; ceiling vs family_max), and every
saturation maps to a reject label rather than a tuning opportunity. But this package cannot, by
itself, guarantee the operator's eventual numbers are strong — that is precisely why operator
freeze plus a pre-result numeric-consistency check (not a post-result one) is mandatory.

Second objection (provenance): one rule source (PREFLIGHT) is byte-unreconciled in-sandbox. If
PREFLIGHT silently drifted, ~half the field rationales rest on a stale source. Mitigation: the
required non-truncating SHA reconciliation before any manifest write.

## Baseline-Saturation Risk

```text
Risk level: inherent and EXPECTED. The accepted prior environment (BASELINE-FIRST-HARNESS-001A,
cited by PREFLIGHT) already closed as rejected_no_headroom_baseline_saturated with strongest
fair baseline = oracle = 1.0 and six graph-cache members all 1.0. A Tier 0-2 cheap-tier debug
on a similar latent-structure surface may well saturate again. This package treats that as the
likely and acceptable negative outcome; it does NOT pre-commit to headroom and forbids relabeling
saturation. The risk to GUARD against is not saturation itself but tuning thresholds to escape it.
```

## Leakage / Replay / Provenance Risk

```text
Lab history shows recurrent leakage/false-green failures: name-only scanners that miss value-level
leaks (Route C preflight), structurally-always-true positive controls (ONE-GATE-FUTURE-ONLY),
baseline_hint = target+1 (GATE4-REPLACEMENT-001B), candidate-authored ground truth, and stored-
score / self-declared-digest bypasses (EAV). This package mandates fail-able positive controls,
value-level + structural coverage, replay recomputation from trace, and tamper probes with
pre-declared expected behavior. Residual risk: positive controls themselves must be audited as
fail-able when implemented — a freeze of the RULE does not guarantee the future IMPLEMENTATION's
controls actually fail on planted leaks; that is an execution-time audit obligation.
```

## Whether Manifest May Be Filled Now

```text
NO. No value may be written into LRGG-CANDIDATE-FREE-TIER0-2-FREEZE-MANIFEST-001A.md until:
  (1) the operator explicitly accepts each rule/value (this is a proposal, not a freeze); AND
  (2) PREFLIGHT-001A.md SHA256 is reconciled to 764063... on a non-truncating filesystem; AND
  (3) the 5 design-required fields (A1, C1, C2, E2-numeric, E3-numeric) receive operator numerics.
Codex must not infer, optimize, tune, or backfill any value.
```

## Whether Implementation / Run May Be Authorized Now

```text
NO. Implementation/run remains blocked. Even a fully frozen manifest only unblocks a SEPARATELY
authorized Tier 0-2 cheap-tier implementation/run; and a non-blocked Tier 0-2 result can at most
emit cheap_tier_plumbing_valid_not_saturated__proceed_to_separately_authorized_heavier_tiers. It
cannot emit admissible_for_candidate_preflight, cannot prove headroom, and cannot authorize
candidate work, Tier 3+, or 001C.
```

## Next Minimal Closed-Loop Action

```text
1. Operator reconciles PREFLIGHT-001A.md SHA256 on a non-truncating filesystem (certutil/sha256).
   - if mismatch: re-audit PREFLIGHT before any freeze.
2. Operator reviews this proposal; accepts/edits the rule-form fields; supplies numerics for the
   5 design-required fields and all operator-required bands.
3. Only then, a separately authorized Codex manifest-write task transcribes the accepted
   values/rules into the freeze manifest (no inference, no tuning).
4. Manifest with zero UNFROZEN_OPERATOR_REQUIRED fields → separate authorization may then be
   requested for the Tier 0-2 cheap-tier implementation/run.
```

## What This Does Not Prove

This proposal does not prove LRGG admissibility, candidate-free headroom, oracle validity,
baseline failure, replay/provenance validity, leakage scanner validity, mechanism evidence,
agency/self/subjectivity/emotion/consciousness/autonomy evidence, EGO readiness, H0/H1, 001A
downgrade, 001C authorization, or TLGP-001B-R2 reinterpretation. It does not fill the manifest,
authorize implementation/run, authorize candidate work, or upgrade any verdict. It is one
proposal document for operator review.

## Acceptance Readback (scope of this task)

```text
Creates only:
  docs/codex/tasks/LRGG-CANDIDATE-FREE-TIER0-2-OPERATOR-FREEZE-RESOLUTION-PROPOSAL-001A.md
Does NOT modify:
  docs/codex/tasks/LRGG-CANDIDATE-FREE-TIER0-2-FREEZE-MANIFEST-001A.md
  docs/codex/tasks/LRGG-CANDIDATE-FREE-TIER0-2-FREEZE-PROPOSAL-TABLE-001A.md
  docs/codex/tasks/LRGG-CANDIDATE-FREE-TIER0-2-IMPLEMENTATION-RUN-001A.md
  docs/codex/tasks/LRGG-CANDIDATE-FREE-CHEAP-TIER-EXECUTION-001A.md
  docs/codex/tasks/LRGG-CANDIDATE-FREE-PREFLIGHT-001A.md
  docs/codex/contracts/**  src/**  tests/**  artifacts/**  docs/research/**
No implementation, run, generator, scorer, oracle, baseline, replay, leakage test, tamper probe,
artifact generation, commit, push, tag, or remote anchor is authorized by this file.
```
