# LRGG-CANDIDATE-FREE-TIER0-2-FREEZE-NUMERIC-RESOLUTION-AND-MANIFEST-WRITE-PREP-001A

Task ID: `LRGG-CANDIDATE-FREE-TIER0-2-FREEZE-NUMERIC-RESOLUTION-AND-MANIFEST-WRITE-PREP-001A`

Status: operator-facing numeric-resolution package + manifest-write task draft. Not a freeze.
Not a manifest write. Not an implementation/run authorization.

Auto-Remote-Anchor: forbidden.

## 0. Verdict & Status / Claim Boundary

Verdict:

```text
freeze_numeric_resolution_package_ready_for_operator_acceptance
```

"Ready for acceptance" means ready for the operator's per-field accept/edit/reject pass. It
does NOT mean the proposed numbers are final, and it does NOT authorize a manifest write.

Current layer: `engineering-governance / operator freeze numeric-resolution`.
Mainline integration status: `none`.
Enabled status: `none`. No generator, scorer, oracle, baseline, replay, leakage, tamper,
artifact, commit, push, tag, remote anchor, Tier 3+, candidate work, 001C, or EGO path exists
or is authorized by this task.

Real trigger evidence:

```text
- FREEZE-PROPOSAL-TABLE-001A exists; R-A/R-B repaired; confirm_accept_repair_closed_for_operator_resolution.
- OPERATOR-FREEZE-RESOLUTION-PROPOSAL-001A exists.
- Operator performed host certutil SHA reconciliation for PREFLIGHT-001A:
    observed host = 764063172f...2876e47  ==  recorded 764063172F...2876E47 (case-insensitive match).
- Freeze manifest still has all 31 fields = UNFROZEN_OPERATOR_REQUIRED.
- Implementation/run remains blocked.
```

Claim ceiling:

```text
This task may only produce (1) a concrete pre-result freeze-value proposal for all 31 fields,
(2) an operator acceptance table, (3) a Codex manifest-write task draft usable only after
explicit operator acceptance. It must not fill the manifest, implement, run, authorize Tier
0-2 execution / candidate work / Tier 3+ / 001C, or emit any LRGG admissibility, headroom,
oracle-validity, mechanism, EGO, agency, self, subjectivity, emotion, consciousness, autonomy,
H0/H1, or TLGP-001B-R2 reinterpretation claim.
```

## 1. Source Readback Summary

```text
canonical_readback = succeeded (file-API / host-authoritative).
PREFLIGHT host SHA reconciliation = CLOSED. Operator host certutil == recorded 764063…
  IN-SANDBOX CAVEAT: the FUSE mount still serves a truncated 920/1241-line PREFLIGHT copy
  (mount SHA 3E6522…). The host certutil value is authoritative and matches; therefore the
  blocker is treated as closed. Any future Codex executor MUST verify PREFLIGHT via the host
  / file API, never via the truncating mount.
source_drift = none. The other five sources are byte-identical to the prior turn:
  CHEAP-TIER-EXECUTION EF80C6D8… ; FREEZE-MANIFEST ADB72E04… ; IMPLEMENTATION-RUN 73464BFE… ;
  BASELINE-IMMUNITY .md 7BD41A04… ; registry 4A3170DE… ; PROPOSAL-TABLE CE14088B….
manifest_state = all 31 freeze fields still UNFROZEN_OPERATOR_REQUIRED (unmodified).
proposal_generation_blocked = no.
```

## 2. Frozen Constant Scheme (pre-result design defaults referenced by the 31 rows)

All scores are on a normalized metric in `[0,1]` (operator freezes the exact metric form, A5).
`C` = the measured `budget_faithful_visible_channel_oracle` ceiling on the debug split (the
oracle's achieved score after it clears `tau_oracle`; expected ≈ 1.0 for a solvable split).
`R` = measured random/chance baseline (marginal/size-matched). These are MEASURED at run time;
the BANDS below are FROZEN now and never tuned to results.

```text
eps_equiv   = 0.05   # oracle-equivalence band. A baseline "reaches the band" iff score >= C - 0.05.
gamma_signal= 0.10   # required oracle-over-chance gap: C - max(random,majority) >= 0.10.
tau_oracle  = 0.90   # oracle solvability floor on the normalized metric.
beta_fail   = 0.30   # oracle failability: C - nonreading_oracle >= 0.30.
n_seed      = 10     # debug-split seed count.
n_ctx       = 20     # debug-split context count.  -> N_rows = n_seed * n_ctx = 200.
LCB         = 95% one-sided lower confidence bound; Wilson for proportion metrics, BCa
                bootstrap (>=2000 resamples) otherwise; computed over the 200 (seed,context) rows.
K_enum      = 10     # enumerability safety margin (effective support must exceed K_enum * N_rows).
H_min       = 11 bits# minimum task-space entropy (2^11 = 2048 >= K_enum * N_rows = 2000).
distinct_T_min = 180 # realized distinct latent configs across the 200 rows (>= 0.9 * N_rows).
coverage_max= 0.10   # exhaustive-probe coverage fraction = B / N_enum^action must be <= 0.10.
B           = 8      # per-episode legal query/do() budget (equal for oracle and fair panel).
                     #   -> N_enum^action >= B / coverage_max = 80 ; N_enum^latent >= 2000.
```

Power note (honest): at `N_rows = 200`, a 95% one-sided Wilson LCB near `p = 0.9` has
half-width ≈ 0.04 < `eps_equiv = 0.05`, so the split can resolve the equivalence band. At the
previously-sketched `N_rows = 100` the half-width (~0.06) would exceed the band — that is why
`n_seed` is raised to 10. This is a pre-result sizing argument, not a result-driven one.

## 3. Part A — 31-Field Concrete Freeze Proposal

Attributes per row: (1) field_name (2) proposed_frozen_value_or_rule (3) units_or_measure_space
(4) source_basis_or_design_basis (5) rationale (6) coupled_fields (7) consistency_constraint
(8) failure_behavior (9) risk_if_too_weak (10) risk_if_too_strict (11) operator_acceptance_status.

### Group A — oracle & metric core

---

**A1. tau_oracle**
1. tau_oracle
2. `0.90` (oracle must score ≥ 0.90 on the debug split).
3. normalized metric score in [0,1].
4. design_basis (near-ceiling solvability floor; no source number).
5. forces the oracle to genuinely solve the debug split before any baseline comparison is meaningful.
6. oracle_failability_band, random_majority_ceiling, metric_balance_rule.
7. must satisfy `tau_oracle − R ≥ gamma_signal` and `tau_oracle` allows `C − nonreading ≥ beta_fail`.
8. `INVALID` if oracle < tau_oracle on the debug split.
9. low tau lets an underpowered/non-reading oracle pass; invalid plumbing looks usable.
10. high tau falsely INVALIDs a legitimate oracle on debug-split noise.
11. `operator_should_edit` (0.90 is a defensible default; tighten to 0.95 if the metric is low-noise).

---

**A2. oracle_failability_band**
1. oracle_failability_band
2. `0.30` — require `C − nonreading_oracle ≥ 0.30`; nonreading_oracle must collapse toward the chance band.
3. absolute gap in normalized score.
4. design_basis grounded in PREFLIGHT R5 / EXECUTION §5 nonreading ablation (rule is source-derived; 0.30 is default).
5. proves the oracle's score comes from latent estimation, not the legal channel alone.
6. tau_oracle, random_majority_ceiling, import_path_audit_alarm_rule.
7. jointly satisfiable with tau: `tau_oracle − beta_fail = 0.60 ≥ R` for typical chance.
8. `INVALID` if gap < 0.30 or nonreading ablation fails to collapse.
9. small band lets a partially-reading oracle pass.
10. large band INVALIDs a legitimate noisy ablation.
11. `operator_may_accept`.

---

**A3. random_majority_ceiling**
1. random_majority_ceiling
2. Rule: `rejected_no_fair_signal` if `max(random, majority) ≥ C − gamma_signal` (i.e. `C − max(random,majority) < 0.10`).
3. normalized score band relative to C.
4. baseline-immunity §2.5 + §5 (rule source-derived; gamma_signal=0.10 default).
5. random/majority near ceiling = no fair signal to discriminate.
6. trivial_predictor_oracle_band_threshold, metric_balance_rule, tau_oracle.
7. random/majority must be marginal/size-matched; uses the same C as all bands.
8. `rejected_no_fair_signal`.
9. weak gap lets no-signal distributions proceed.
10. large gap rejects noisy-but-usable debug signal.
11. `operator_may_accept`.

---

**A4. trivial_predictor_oracle_band_threshold**
1. trivial_predictor_oracle_band_threshold
2. Rule: if `predict_all` / `predict_none` / any `constant_k_sweep` (k over [0..|set|]) reaches `≥ C − eps_equiv`, emit `rejected_metric_degenerate`.
3. normalized score band (eps_equiv).
4. baseline-immunity §2.1–§2.3, §2.6 (rule source-derived; eps_equiv=0.05 default).
5. blocks recall-only / abstention-only / fixed-size metric degeneracy pre-candidate.
6. metric_balance_rule, random_majority_ceiling, max_enumerability_bound (k cardinality), aggregation_method.
7. uses shared eps_equiv = graph-cache band (not weaker than any saturation band).
8. `rejected_metric_degenerate`.
9. weak band lets trivial predictors hide in the metric.
10. strict band rejects harmless constant baselines on noise.
11. `operator_may_accept`.

---

**A5. metric_balance_rule**
1. metric_balance_rule
2. Default: balanced `F-beta with beta = 1.0` (F1) on the debug target, with `predict_all`/`predict_none`/`constant_k_sweep` controls reported alongside; single-sided recall-only or precision-only metrics forbidden. Operator may substitute an explicit cost-weighted metric.
3. metric definition; beta dimensionless.
4. baseline-immunity §2.6–§2.7; PREFLIGHT R1 (form source-derived; beta=1.0 default).
5. a balanced metric cannot be saturated by set size / abstention / all-positive prediction.
6. trivial_predictor_oracle_band_threshold, random_majority_ceiling, tau_oracle, aggregation_method.
7. tau/eps/gamma are all defined on this metric; changing the metric re-scales them (must co-freeze).
8. `rejected_metric_degenerate`.
9. single-sided metric is trivially saturated.
10. over-strict cost model blocks a legitimate oracle.
11. `operator_may_accept` (confirm beta or supply cost model).

### Group B — baseline block thresholds (all use eps_equiv; saturation → negative evidence, never tuning)

---

**B1. obs_only_block_threshold**
1. obs_only_block_threshold
2. Rule: if observation-only / passive baseline `≥ C − eps_equiv`, emit `rejected_trivially_decodable` (passive determination) or `rejected_no_fair_signal` (no separable signal). `memoryless_policy` is governed by this threshold.
3. normalized score band (eps_equiv).
4. baseline-immunity §3.1–§3.2 (rule source-derived; band default).
5. stops visible/passive-channel decodability being read as headroom.
6. raw_observation_latent_decodability_ceiling, value_level_attacker_family_max_rule, observation_field_audit_alarm_rule.
7. obs-only has exactly the legal passive access; band = eps_equiv.
8. `rejected_trivially_decodable` / `rejected_no_fair_signal`.
9. weak band lets passive leakage slip through.
10. strict band rejects residual-but-noisy passive signal.
11. `operator_may_accept`.

---

**B2. lookup_graph_cache_block_threshold**
1. lookup_graph_cache_block_threshold
2. Rule: if lookup or any of the six graph_cache members (`graph_lookup`, `transition_table`, `successor_map`, `count_table`, `fsm_planner`, `episodic_traversal`) `≥ C − eps_equiv`, emit `rejected_baseline_saturated`. `trajectory_nearest_neighbor` is governed by this threshold.
3. normalized score band (eps_equiv).
4. baseline-immunity §5 graph-cache (mandatory six-member); rule source-derived; band default.
5. canonical cheap-collapse control for representational/environment claims.
6. n_gram_block_threshold, max_enumerability_bound, minimum_task_space_entropy, latent_graph_exposure_alarm_threshold.
7. all six members run at legal-access parity; band = eps_equiv = trivial band.
8. `rejected_baseline_saturated`.
9. weak band lets graph-cache/NN saturation masquerade as headroom.
10. strict band blocks a clearly sub-oracle cache under noise.
11. `operator_may_accept`.

---

**B3. direct_objective_optimizer_block_threshold**
1. direct_objective_optimizer_block_threshold
2. Rule: if any of `discounted_wls` / `least_squares` / `convex_objective_solver` under legal access `≥ C − eps_equiv`, emit `rejected_baseline_saturated`.
3. normalized score band (eps_equiv).
4. baseline-immunity §5 direct optimizer (ACOLB-A grounding); band default.
5. blocks "surface solved by direct metric optimization" being read as mechanism.
6. task_specific_classical_block_threshold, metric_balance_rule, tau_oracle.
7. optimizers are independent callable impls at frozen strength; band = eps_equiv.
8. `rejected_baseline_saturated`.
9. weak band lets closed-form solving look mechanism-like.
10. strict band rejects near-but-not-equivalent optimizers.
11. `operator_may_accept`.

---

**B4. task_specific_classical_block_threshold**
1. task_specific_classical_block_threshold
2. Rule: if hand-coded DP / finite-state filter / classical planner under legal access `≥ C − eps_equiv`, emit `rejected_baseline_saturated`. Must be the strongest known legal method for the task type.
3. normalized score band (eps_equiv).
4. baseline-immunity §5 task-specific classical; band default.
5. blocks classical task-specific solutions being reinterpreted as mechanism evidence.
6. direct_objective_optimizer_block_threshold, tau_oracle.
7. classical strength fixed by spec; band = eps_equiv.
8. `rejected_baseline_saturated`.
9. weak band lets a classical solver saturate while the route proceeds.
10. strict band rejects informative-but-non-saturating classical methods.
11. `operator_may_accept`.

---

**B5. n_gram_block_threshold**
1. n_gram_block_threshold
2. Rule: if n-gram / short-history cache (history-length sweep `h ∈ {1,2,3,5}`, frozen) `≥ C − eps_equiv`, emit `rejected_baseline_saturated`.
3. normalized score band (eps_equiv); h in steps.
4. baseline-immunity §5 lookup imitation; band + sweep default.
5. blocks short-history memorization being read as structural inference.
6. lookup_graph_cache_block_threshold, max_enumerability_bound.
7. sweep declared pre-result; band = eps_equiv.
8. `rejected_baseline_saturated`.
9. weak band/short sweep lets local-history cache saturate.
10. strict band rejects sub-oracle n-gram with residual.
11. `operator_may_accept` (confirm history sweep).

---

**B6. raw_observation_latent_decodability_ceiling**
1. raw_observation_latent_decodability_ceiling
2. Rule: if a raw-observation latent decoder OR the value-level `family_max` reaches `≥ C − eps_equiv` (passive recovers the latent as well as the oracle), emit `rejected_trivially_decodable`. Optional tighter operator cap: family_max ≤ chance + eps_equiv.
3. normalized score band (eps_equiv).
4. baseline-immunity §3.2; PREFLIGHT R6 / killer K1; band default.
5. the decodability wall: raw observations must not reveal the latent target.
6. value_level_attacker_family_max_rule (shared ceiling), obs_only_block_threshold, observation_field_audit_alarm_rule.
7. shares its ceiling with G10; decoder/attacker fixed before outputs.
8. `rejected_trivially_decodable`.
9. weak ceiling lets latent leakage become apparent headroom.
10. strict ceiling rejects noisy-but-non-saturating latent signal.
11. `operator_may_accept`.

### Group C — debug-split design

---

**C1. cheap_tier_debug_split_seed_count**
1. cheap_tier_debug_split_seed_count
2. `10`.
3. count (integer).
4. design_basis (no source number).
5. with n_ctx=20 gives N_rows=200, where a 95% Wilson LCB half-width (~0.04) resolves eps_equiv=0.05.
6. cheap_tier_debug_split_context_count, confidence_interval_lower_confidence_bound_rule, minimum_task_space_entropy, max_enumerability_bound.
7. N_rows=200 must satisfy: LCB half-width < eps_equiv AND N_rows ≤ 2^{H_min}/K_enum = 204.8.
8. `blocked_pending_operator_freeze` if unset.
9. too few seeds miss leakage/cache/variance and weaken the LCB.
10. too many seeds drift toward an unauthorized heavier-tier run.
11. `operator_should_edit` (10 is a defensible cheap-tier default; raise for tighter LCB).

---

**C2. cheap_tier_debug_split_context_count**
1. cheap_tier_debug_split_context_count
2. `20`.
3. count (integer).
4. design_basis (no source number).
5. with n_seed=10 gives N_rows=200; large enough to exercise graph-cache coverage, small enough to stay cheap.
6. cheap_tier_debug_split_seed_count, minimum_task_space_entropy, max_enumerability_bound, lookup_graph_cache_block_threshold.
7. N_rows=200 ≤ 2^{H_min}/K_enum and distinct_T realized ≥ 180.
8. `blocked_pending_operator_freeze` if unset.
9. too few contexts make the split a memorizable/enumerable toy.
10. too many contexts exceed cheap-tier budget.
11. `operator_should_edit`.

---

**C3. debug_split_seed_ids_or_generation_rule**
1. debug_split_seed_ids_or_generation_rule
2. Deterministic rule: `seed_i = int(sha256(f"{MASTER}|seed|{i}").hexdigest()[:8], 16)` for `i in 0..n_seed-1`, `MASTER = "LRGG-T02-DEBUG-001A"` (frozen). IDs are not exposed to agents and do not encode rule/family/score-key.
3. deterministic generation rule; MASTER is a frozen string.
4. PREFLIGHT Tier 0 deterministic check; baseline-immunity §3.5 (rule source-derived).
5. deterministic preregistration prevents post-output seed cherry-picking.
6. cheap_tier_debug_split_seed_count, seed_config_filename_leakage_alarm_threshold, membership_leakage_alarm_threshold.
7. reproducible from MASTER; disjoint from any future train/heldout seeds.
8. `blocked_pending_operator_freeze` if unset; `rejected_trivially_decodable` if IDs later leak labels.
9. weak rule allows seed cherry-picking / split leakage.
10. over-rigid rule blocks harmless reproducible generation.
11. `operator_may_accept` (confirm MASTER string).

---

**C4. debug_split_context_ids_or_generation_rule**
1. debug_split_context_ids_or_generation_rule
2. Deterministic rule: `ctx_j = int(sha256(f"{MASTER}|ctx|{j}").hexdigest()[:8], 16)` for `j in 0..n_ctx-1`, same frozen MASTER; require disjointness from any future train/heldout context; IDs not agent-exposed.
3. deterministic generation rule.
4. PREFLIGHT Tier 0; baseline-immunity §3.5 (rule source-derived).
5. avoids post-hoc context selection and future train/test contamination.
6. cheap_tier_debug_split_context_count, max_train_test_leakage, membership_leakage_alarm_threshold.
7. reproducible; disjoint; cannot encode hidden rule/family/score-key.
8. `blocked_pending_operator_freeze` if unset; `rejected_trivially_decodable` on detected overlap/encoding.
9. weak rule allows context cherry-picking / hidden overlap.
10. over-rigid rule blocks valid deterministic contexts.
11. `operator_may_accept` (confirm MASTER string).

### Group D — aggregation

---

**D1. aggregation_method**
1. aggregation_method
2. Rule: callable verdict aggregation over recorded evidence rows; hard-stop/block conditions DOMINATE any continuous score; family baselines decided by `family_max`; no static verdict dictionary; verdict emitted only by a callable path recording `aggregation_code_path_sha256`.
3. aggregation rule (no scalar).
4. PREFLIGHT real-trigger requirement; AGENTS computed-evidence gate (rule source-derived).
5. non-post-hoc because the aggregation path is callable and frozen before outputs; a blocker cannot be averaged away.
6. confidence_interval_lower_confidence_bound_rule, every block/alarm threshold, value_level_attacker_family_max_rule.
7. blocker precedence > any score; family_max semantics enforced.
8. `INVALID` if aggregator is static, averages away a blocker, or ignores a saturated member.
9. weak aggregation hides a blocker/saturated member.
10. strict aggregation escalates benign warnings to INVALID.
11. `operator_may_accept`.

---

**D2. confidence_interval_lower_confidence_bound_rule**
1. confidence_interval_lower_confidence_bound_rule
2. `95%` one-sided lower confidence bound over the 200 (seed,context) rows; Wilson interval for proportion metrics, BCa bootstrap (≥2000 resamples, frozen seed) otherwise. A positive-looking mean that does not clear its LCB cannot proceed.
3. confidence level (%) + estimator.
4. PREFLIGHT R2 LCB language (rule source-derived; 95% + estimator default).
5. controls noisy positive-looking scores at debug-tier sample size.
6. cheap_tier_debug_split_seed_count, cheap_tier_debug_split_context_count, aggregation_method.
7. valid for N_rows=200 (Wilson half-width ~0.04 < eps_equiv 0.05).
8. `INVALID` if LCB missing/under-specified or invalid for the sample size.
9. weak/missing LCB lets noise pass.
10. over-strict LCB blocks a usable split on small-sample uncertainty.
11. `operator_may_accept` (confirm 95% and estimator).

### Group E — task-space (measures M1/M2 from OPERATOR-FREEZE-RESOLUTION-PROPOSAL-001A)

---

**E1. max_train_test_leakage**
1. max_train_test_leakage
2. Rule: zero tolerated KNOWN split-membership / structural leakage; a membership-attacker positive control MUST alarm on a planted leak (failure to alarm = `INVALID`); any real leakage above zero-known-structural blocks. Value-level scanner sensitivity = recovery LCB ≥ chance + eps_equiv.
3. leakage rule; sensitivity = normalized band (eps_equiv).
4. baseline-immunity §3.4–§3.5 (rule source-derived; sensitivity default).
5. leakage is source-blocking and must be pre-output fail-able.
6. membership_leakage_alarm_threshold, debug_split_context_ids_or_generation_rule, seed_config_filename_leakage_alarm_threshold.
7. only one debug split exists at Tier 0-2; "zero known structural" + positive control.
8. `rejected_trivially_decodable` on real leak; `INVALID` on failed positive control.
9. weak rule lets membership leakage inflate results.
10. strict rule blocks benign non-agent-visible metadata.
11. `operator_may_accept`.

---

**E2. minimum_task_space_entropy**  (measure M1: H(T) of T=(G,R[,C]) under frozen P_gen, bits)
1. minimum_task_space_entropy
2. `H_min = 11 bits`, with realized rule: distinct-T across the 200 rows ≥ 180. Computed from the frozen generator SPEC (not run outputs).
3. bits (Shannon entropy of the latent task-config RV); effective support = 2^{H(T)}.
4. design_basis on measure M1; threshold set by `2^{H_min} ≥ K_enum · N_rows = 2000` (2^11=2048).
5. too little entropy makes enumeration/lookup/cache saturation likely; 11 bits keeps effective support ≥ 10× the sample budget.
6. max_enumerability_bound, cheap_tier_debug_split_seed_count, cheap_tier_debug_split_context_count, lookup_graph_cache_block_threshold.
7. `2^{H_min} ≥ K_enum · N_rows` AND distinct_T_min ≤ N_rows.
8. `INVALID` if P_gen(T) undefined/unmeasurable, H(T) < 11 bits, or distinct-T < 180.
9. weak H_min lets enumeration/cache saturate.
10. strict H_min can make debug oracle/scorer validation fail for capacity reasons.
11. `operator_should_edit` (11 bits is coupling-derived; adjust with N_rows / K_enum).

---

**E3. max_enumerability_bound**  (measure M2: N_enum^action, N_enum^latent; coverage = B/N_enum)
1. max_enumerability_bound
2. Rule: `coverage_fraction = B / N_enum^action ≤ 0.10` with `B = 8`; `N_enum^latent ≥ 2000`. Checked against the frozen generator spec at run time.
3. counts (N_enum) + dimensionless coverage fraction; B in legal queries/episode.
4. design_basis on measure M2 (rule source-derived; B/coverage default).
5. exhaustive_legal_probe saturates only if it can cover the space within budget; coverage ≤ 0.10 prevents that.
6. minimum_task_space_entropy, lookup_graph_cache_block_threshold, n_gram_block_threshold, cheap_tier_debug_split_context_count.
7. `N_enum^latent ≥ 2^{H_min}-consistent (≥2000)`; `N_enum^action ≥ B/coverage_max = 80`.
8. `rejected_baseline_saturated` when exhaustive probe / cheap enumeration saturates; measure-undefined → operator-required measure first.
9. weak bound lets exhaustive probe saturate and erase structure.
10. strict bound rejects a small debug split before plumbing is tested.
11. `operator_should_edit` (confirm B=8 and coverage 0.10 against the intended action space).

### Group F — tamper

---

**F1. tamper_probe_expected_behavior**
1. tamper_probe_expected_behavior
2. Frozen expectation table: mutate-one-action → recomputed score changes / replay mismatch; mutate-source-byte → source-hash mismatch; mutate-hidden-graph/remapping → replay or provenance fails; mutate-observation-trace → score change / replay mismatch; mutate-reward-trace → score change / replay mismatch. Score recomputed from serialized state + action/observation/reward trace; stored-score-only = invalid.
3. tamper expectation per probe class.
4. EXECUTION §11; IMPLEMENTATION-RUN replay/provenance (rule source-derived).
5. protects against stored-score evidence and provenance bypass.
6. import_path_audit_alarm_rule, serialized_state_audit_alarm_rule, aggregation_method.
7. each tamper class has a pre-declared expected effect; by-design-neutral mutations declared in advance.
8. `INVALID` if any probe fails its declared expectation.
9. weak expectation lets tampering leave official evidence unchanged.
10. strict expectation fails on a semantically neutral mutation.
11. `operator_may_accept` (confirm any by-design-neutral mutations).

### Group G — leakage alarm fields (each: planted leak MUST alarm; failed positive control = INVALID; value-level + structural, not name-only)

---

**G1. hidden_rule_id_leak_alarm_threshold**
1. hidden_rule_id_leak_alarm_threshold
2. Rule: planted hidden-rule-ID leak MUST alarm; real recovery of the hidden-rule-ID from agent-visible channels with LCB ≥ chance + eps_equiv → `rejected_trivially_decodable`.
3. normalized recovery band (eps_equiv) + binary positive control.
4. PREFLIGHT/EXECUTION leakage positive controls (rule source-derived; sensitivity default).
5. hidden rule ID is a direct side channel.
6. latent_graph_exposure_alarm_threshold, observation_field_audit_alarm_rule, import_path_audit_alarm_rule.
7. detector not name-only; sensitivity = eps_equiv at the 95% LCB.
8. `rejected_trivially_decodable` on real leak; `INVALID` on non-firing positive control.
9. weak sensitivity lets ID leakage solve the task.
10. strict sensitivity flags benign non-agent-visible identifiers.
11. `operator_may_accept`.

---

**G2. latent_graph_exposure_alarm_threshold**
1. latent_graph_exposure_alarm_threshold
2. Rule: planted latent-graph exposure MUST alarm; real exposure (graph hashes/IDs/serialized fields, value-level) with LCB ≥ chance + eps_equiv → `rejected_trivially_decodable`.
3. normalized recovery band (eps_equiv) + binary positive control.
4. leakage positive controls (rule source-derived; sensitivity default).
5. latent-graph exposure collapses the task to direct decoding / graph-cache saturation.
6. lookup_graph_cache_block_threshold, serialized_state_audit_alarm_rule, hidden_rule_id_leak_alarm_threshold.
7. covers hashes/IDs/serialized fields, not names; sensitivity = eps_equiv.
8. `rejected_trivially_decodable` on real leak; `INVALID` on non-firing positive control.
9. weak sensitivity lets graph exposure masquerade as inference.
10. strict sensitivity blocks benign structural metadata.
11. `operator_may_accept`.

---

**G3. task_family_id_alarm_threshold**
1. task_family_id_alarm_threshold
2. Rule: planted task-family-ID exposure MUST alarm; real exposure with LCB ≥ chance + eps_equiv → `rejected_trivially_decodable`.
3. normalized recovery band (eps_equiv) + binary positive control.
4. leakage positive controls (rule source-derived; sensitivity default).
5. task-family IDs can route baselines/agents to a hidden shortcut.
6. hidden_rule_id_leak_alarm_threshold, score_key_reward_shaping_alarm_threshold.
7. detector value-level + structural; sensitivity = eps_equiv.
8. `rejected_trivially_decodable` on real leak; `INVALID` on non-firing positive control.
9. weak sensitivity lets family-conditioned lookup pass.
10. strict sensitivity blocks harmless public task metadata.
11. `operator_may_accept`.

---

**G4. score_key_reward_shaping_alarm_threshold**
1. score_key_reward_shaping_alarm_threshold
2. Rule: planted score-key / reward-shaping artifact MUST alarm; a shaping-only baseline reaching `≥ C − eps_equiv` OR real score-key recovery LCB ≥ chance + eps_equiv → `rejected_metric_degenerate`.
3. normalized band (eps_equiv) + binary positive control.
4. leakage positive controls + baseline-immunity §2 (rule source-derived; sensitivity default).
5. score-key exposure lets a baseline optimize the metric rather than infer structure.
6. metric_balance_rule, trivial_predictor_oracle_band_threshold.
7. reward fields classified as legal-observation vs scorer-only-truth before run; sensitivity = eps_equiv.
8. `rejected_metric_degenerate` on real leak; `INVALID` on non-firing positive control.
9. weak sensitivity lets reward shaping create false positives.
10. strict sensitivity rejects legitimate reward observations.
11. `operator_may_accept`.

---

**G5. membership_leakage_alarm_threshold**
1. membership_leakage_alarm_threshold
2. Rule: planted split-membership leak MUST alarm; real membership recovery (legal visible channels only) LCB ≥ chance + eps_equiv → `rejected_trivially_decodable`.
3. normalized band (eps_equiv) + binary positive control.
4. baseline-immunity §3.4–§3.5 (rule source-derived; sensitivity default).
5. membership leakage contaminates debug/heldout interpretation.
6. max_train_test_leakage, debug_split_context_ids_or_generation_rule.
7. membership attacker uses only legal visible channels; sensitivity = eps_equiv.
8. `rejected_trivially_decodable` on real leak; `INVALID` on non-firing positive control.
9. weak sensitivity lets split membership explain performance.
10. strict sensitivity flags non-agent-visible bookkeeping.
11. `operator_may_accept`.

---

**G6. seed_config_filename_leakage_alarm_threshold**
1. seed_config_filename_leakage_alarm_threshold
2. Rule: planted seed/config/filename leak MUST alarm; real filename/config leakage (names, values, ordering, AND artifact structure) above the rule → `rejected_trivially_decodable`.
3. structural + value recovery (eps_equiv) + binary positive control.
4. baseline-immunity §3.4 (rule source-derived; sensitivity default).
5. filename/config side channels are known leakage families beyond value fields.
6. debug_split_seed_ids_or_generation_rule, membership_leakage_alarm_threshold.
7. scanner covers names/values/ordering/structure; sensitivity = eps_equiv.
8. `rejected_trivially_decodable` on real leak; `INVALID` on non-firing positive control.
9. weak scanner lets path/config names carry hidden labels.
10. strict scanner blocks ordinary non-agent-visible reproducibility metadata.
11. `operator_may_accept`.

---

**G7. observation_field_audit_alarm_rule**
1. observation_field_audit_alarm_rule
2. Rule: observation fields injected with latent/graph/ID truth MUST alarm — value-level AND field-name scans, EACH with its own positive control; real field-level leakage → `rejected_trivially_decodable`.
3. dual-scan alarm rule (value + name) + binary positive controls.
4. leakage positive controls (rule source-derived).
5. direct guard against hidden labels entering legal observations.
6. raw_observation_latent_decodability_ceiling, value_level_attacker_family_max_rule, obs_only_block_threshold.
7. both scans + both positive controls frozen before outputs.
8. `rejected_trivially_decodable` on real leak; `INVALID` on either non-firing positive control.
9. weak rule lets labels hide in field names or values.
10. strict rule blocks legal observations the task requires.
11. `operator_may_accept`.

---

**G8. serialized_state_audit_alarm_rule**
1. serialized_state_audit_alarm_rule
2. Rule: serialized state embedding generator truth readable by agents MUST alarm; real readable truth → `rejected_trivially_decodable`; replay-required state must be separated from agent-readable observations.
3. structural alarm rule + binary positive control.
4. EXECUTION §11 (rule source-derived).
5. serialized state is part of replay and must not become a hidden answer channel.
6. tamper_probe_expected_behavior, latent_graph_exposure_alarm_threshold, import_path_audit_alarm_rule.
7. replay-state vs agent-readable separation declared before outputs.
8. `rejected_trivially_decodable` on real leak; `INVALID` on non-firing positive control.
9. weak rule lets replay state carry direct truth.
10. strict rule blocks necessary replay-state serialization.
11. `operator_may_accept`.

---

**G9. import_path_audit_alarm_rule**
1. import_path_audit_alarm_rule
2. Rule: forbidden imports of hidden latent / hidden graph / remapping / generator-truth / scorer-truth MUST alarm; a failed alarm is `INVALID`. Allow/deny basis must catch structurally-equivalent illegal reads, not known names only.
3. import-path alarm rule (failed-alarm → INVALID).
4. EXECUTION §5 oracle contract; baseline-immunity §3.4 (rule source-derived).
5. prevents oracle/generator/scorer/future-candidate reading truth directly.
6. oracle_failability_band, tamper_probe_expected_behavior, serialized_state_audit_alarm_rule.
7. allow/deny rule + positive control frozen before outputs.
8. `INVALID` on illegal truth reads or non-firing positive control.
9. weak rule lets illegal reads produce apparent solvability.
10. strict rule blocks legitimate source hashing / module imports.
11. `operator_may_accept`.

---

**G10. value_level_attacker_family_max_rule**
1. value_level_attacker_family_max_rule
2. Rule: compute `family_max` over {mean, variance, correlation, PCA, cross-episode, supervised, membership} under legal access; if `family_max ≥ C − eps_equiv` → `rejected_trivially_decodable`. Decision is family_max, never a single attacker. Supervised attacker must not leak labels. Ceiling shared with B6.
3. normalized score band (eps_equiv) over a 7-member family.
4. baseline-immunity §3.2; PREFLIGHT positive controls (rule source-derived).
5. family_max prevents selecting a weak attacker after outputs.
6. raw_observation_latent_decodability_ceiling (shared ceiling), obs_only_block_threshold, observation_field_audit_alarm_rule.
7. all members legal access; family_max; band = eps_equiv.
8. `rejected_trivially_decodable` on real decode; `INVALID` on non-firing planted-leak positive control.
9. weak rule lets one attacker decode while a weaker one is reported.
10. strict rule trips on a single attacker overfitting noise (mitigated by LCB / N=200).
11. `operator_may_accept`.

## 4. Part B — Special Numeric Design for the 5 Previously-Unresolved Fields

### A1. tau_oracle
```text
proposed: tau_oracle = 0.90 on the normalized metric.
not post-hoc: it is a solvability FLOOR the oracle must MEET, fixed before any oracle score
  exists; it is never lowered to admit a weak oracle. It is a property requirement, not a knob
  fit to results.
prevents underpowered-oracle acceptance: combined with beta_fail=0.30 (oracle minus nonreading
  >= 0.30) and the import-path audit, an oracle that merely reads the legal channel (or reads
  truth) cannot both clear 0.90 AND show a 0.30 reading-vs-nonreading gap honestly.
avoids impossible debug split: 0.90 (not 1.0) tolerates debug-split noise; if a genuinely
  solvable split's oracle lands at 0.90-0.95, it still passes.
```

### C1. cheap_tier_debug_split_seed_count
```text
proposed: n_seed = 10  (with n_ctx = 20 -> N_rows = 200).
enough for leakage/cache/variance at debug scale: N_rows=200 gives a 95% one-sided Wilson LCB
  half-width ~0.04 < eps_equiv=0.05, so saturation/leakage at the band is resolvable; 7 value-
  level attackers + 6 graph-cache members + trivial predictors each get 200 paired samples.
not heavier-tier: 200 cheap episodes are sandbox-runnable, no GPU, no training; this is debug
  plumbing, not a Tier 4/5 learner run.
couples to LCB: the LCB estimator's validity (D2) is asserted for N_rows=200; raising n_seed
  tightens the LCB, lowering it invalidates the band resolution.
```

### C2. cheap_tier_debug_split_context_count
```text
proposed: n_ctx = 20.
avoids enumerable toy: with H_min=11 bits the effective latent support 2^{H(T)} >= 2048, and
  the realized-distinct-T rule (>=180 of 200) forbids a split that secretly repeats a few
  configs; 20 contexts x 10 seeds cannot enumerate >=2048 configs.
stays cheap-tier: 200 total episodes.
couples to H(T) / N_enum / graph-cache coverage: K_enum=10 margin requires
  2^{H_min} >= K_enum * N_rows = 2000; graph-cache coverage is bounded because N_enum^latent
  >= 2000 >> 200 observed.
```

### E2. minimum_task_space_entropy
```text
measure: T=(G,R[,C]); H(T) in bits under frozen P_gen (spec-derived); effective support 2^{H(T)}.
proposed: H_min = 11 bits.
realized-distinct-T rule: distinct T across the 200 rows >= 180 (>=0.9 * N_rows).
relation to budget/coverage: 2^{H_min}=2048 >= K_enum * N_rows = 10*200 = 2000, so the sampled
  split occupies <=~10% of the latent support and enumerable baselines cannot cover it.
INVALID condition: P_gen(T) undefined/unmeasurable, OR H(T) < 11 bits, OR realized distinct-T
  < 180  ->  INVALID (precondition unmeasurable or task space too small).
```

### E3. max_enumerability_bound
```text
measured spaces: N_enum^action (legal action/query sequences an exhaustive probe enumerates
  within budget B), N_enum^latent (distinct latent configs coverable under the debug budget);
  coverage_fraction = B / N_enum^action.
proposed: coverage_fraction <= 0.10 ; B = 8 ; N_enum^latent >= 2000 ; hence N_enum^action >= 80.
budget B definition: B = number of legal queries / do()-interventions per episode, EQUAL for the
  oracle and the full fair panel (access parity).
saturation mapping: if exhaustive_legal_probe (or any cheap enumeration) reaches >= C - eps_equiv
  under legal access, verdict = rejected_baseline_saturated (NOT a reason to raise the bound).
couples to H_min and graph-cache/lookup: N_enum^latent >= 2000 is the 2^{H_min} consistency
  partner; if graph-cache/lookup/n-gram saturate they are governed by B2/B5 at the same
  eps_equiv band.
```

## 5. Part C — Numeric Consistency Check

```text
1. tau_oracle (0.90) above collapse band:    PASS — requires C - max(random,majority) >= gamma_signal
   (0.10); with oracle near 0.90+ and chance below, satisfiable; violation -> rejected_no_fair_signal.
2. beta_fail (0.30) jointly with tau (0.90):  PASS — tau - beta_fail = 0.60 must be >= nonreading
   collapse (~chance R); holds for typical R<=0.6; if R>0.6 the env fails failability (correct).
3. N_rows=200 sufficient for LCB yet cheap:   PASS — 95% Wilson half-width ~0.04 < eps_equiv 0.05;
   200 episodes are sandbox/no-GPU cheap.
4. N_rows does NOT enumerate latent space:    PASS — 2^{H_min}=2048 >= K_enum*N_rows=2000; distinct-T
   >=180 enforced.
5. H(T) threshold and N_enum mutually consistent: PASS — N_enum^latent>=2000 <-> 2^{H_min}>=2048.
6. graph-cache/NN/lookup not weaker than trivial-predictor band: PASS — all use the SAME eps_equiv
   (0.05); trajectory-NN under B2, n-gram under B5.
7. obs-only/memoryless/raw-decodability not weaker than leakage alarms: PASS — decodability uses
   eps_equiv band AND leakage alarms require fail-able positive controls (independent gates, both
   must pass); memoryless under B1, raw-decode shares B6/G10 ceiling.
8. family_max prevents cherry-picking weaker attackers: PASS — G10 decides on family_max over the
   7-member family, never a single attacker.
9. hard-stop aggregation prevents averaging away a blocker: PASS — D1 gives block conditions
   precedence over any continuous score.
10. no proposed value routes to admissible_for_candidate_preflight: PASS — Tier 0-2 ceiling
    enforced; best attainable label is the non-admission proceed label.

Classification: consistent_for_operator_review
```

Residual (not a contradiction, disclosed): three quantities are CHECKED at run time against the
frozen generator spec — `C`, `R`, realized `H(T)` / distinct-T, and `N_enum^action`. The BANDS
and RULES are frozen now; the generator spec must be frozen as a run prerequisite (EXECUTION §6),
not as one of these 31 fields. No value here is result-dependent.

## 6. Part D — Operator Acceptance Table

Copy, set each `operator_decision` to ACCEPT / EDIT:<value> / REJECT. Nothing is pre-accepted.

| field_name | proposed_value_or_rule | operator_decision |
|---|---|---|
| tau_oracle | 0.90 | PENDING_OPERATOR_ACCEPT_EDIT_REJECT |
| random_majority_ceiling | no_fair_signal if max(random,majority) ≥ C−0.10 | PENDING_OPERATOR_ACCEPT_EDIT_REJECT |
| trivial_predictor_oracle_band_threshold | degenerate if predict_all/none/constant_k ≥ C−0.05 | PENDING_OPERATOR_ACCEPT_EDIT_REJECT |
| metric_balance_rule | F-beta, beta=1.0 + trivial-predictor controls; no single-sided | PENDING_OPERATOR_ACCEPT_EDIT_REJECT |
| obs_only_block_threshold | block if obs-only/memoryless ≥ C−0.05 | PENDING_OPERATOR_ACCEPT_EDIT_REJECT |
| lookup_graph_cache_block_threshold | saturated if lookup/6-graph-cache/traj-NN ≥ C−0.05 | PENDING_OPERATOR_ACCEPT_EDIT_REJECT |
| direct_objective_optimizer_block_threshold | saturated if wls/ls/convex ≥ C−0.05 | PENDING_OPERATOR_ACCEPT_EDIT_REJECT |
| task_specific_classical_block_threshold | saturated if DP/FSF/planner ≥ C−0.05 | PENDING_OPERATOR_ACCEPT_EDIT_REJECT |
| n_gram_block_threshold | saturated if n-gram(h∈{1,2,3,5}) ≥ C−0.05 | PENDING_OPERATOR_ACCEPT_EDIT_REJECT |
| raw_observation_latent_decodability_ceiling | decodable if decoder/family_max ≥ C−0.05 | PENDING_OPERATOR_ACCEPT_EDIT_REJECT |
| cheap_tier_debug_split_seed_count | 10 | PENDING_OPERATOR_ACCEPT_EDIT_REJECT |
| cheap_tier_debug_split_context_count | 20 | PENDING_OPERATOR_ACCEPT_EDIT_REJECT |
| debug_split_seed_ids_or_generation_rule | sha256(MASTER\|seed\|i)[:8], MASTER="LRGG-T02-DEBUG-001A" | PENDING_OPERATOR_ACCEPT_EDIT_REJECT |
| debug_split_context_ids_or_generation_rule | sha256(MASTER\|ctx\|j)[:8], same MASTER; disjoint | PENDING_OPERATOR_ACCEPT_EDIT_REJECT |
| aggregation_method | callable; hard-stop precedence; family_max; no static dict | PENDING_OPERATOR_ACCEPT_EDIT_REJECT |
| confidence_interval_lower_confidence_bound_rule | 95% one-sided; Wilson / BCa(≥2000) over 200 rows | PENDING_OPERATOR_ACCEPT_EDIT_REJECT |
| max_train_test_leakage | zero known structural; membership positive control must alarm | PENDING_OPERATOR_ACCEPT_EDIT_REJECT |
| minimum_task_space_entropy | H_min=11 bits; distinct-T≥180/200 | PENDING_OPERATOR_ACCEPT_EDIT_REJECT |
| max_enumerability_bound | coverage=B/N_enum^action ≤0.10; B=8; N_enum^latent≥2000 | PENDING_OPERATOR_ACCEPT_EDIT_REJECT |
| oracle_failability_band | 0.30 (C − nonreading_oracle ≥ 0.30) | PENDING_OPERATOR_ACCEPT_EDIT_REJECT |
| tamper_probe_expected_behavior | 5-probe expectation table; recompute from trace | PENDING_OPERATOR_ACCEPT_EDIT_REJECT |
| hidden_rule_id_leak_alarm_threshold | planted must alarm; real recovery LCB ≥ chance+0.05 → decodable | PENDING_OPERATOR_ACCEPT_EDIT_REJECT |
| latent_graph_exposure_alarm_threshold | planted must alarm; real exposure LCB ≥ chance+0.05 → decodable | PENDING_OPERATOR_ACCEPT_EDIT_REJECT |
| task_family_id_alarm_threshold | planted must alarm; real exposure LCB ≥ chance+0.05 → decodable | PENDING_OPERATOR_ACCEPT_EDIT_REJECT |
| score_key_reward_shaping_alarm_threshold | planted must alarm; shaping-only ≥ C−0.05 → metric_degenerate | PENDING_OPERATOR_ACCEPT_EDIT_REJECT |
| membership_leakage_alarm_threshold | planted must alarm; real recovery LCB ≥ chance+0.05 → decodable | PENDING_OPERATOR_ACCEPT_EDIT_REJECT |
| seed_config_filename_leakage_alarm_threshold | planted must alarm; names+values+ordering+structure | PENDING_OPERATOR_ACCEPT_EDIT_REJECT |
| observation_field_audit_alarm_rule | value-scan + name-scan, each with positive control | PENDING_OPERATOR_ACCEPT_EDIT_REJECT |
| serialized_state_audit_alarm_rule | replay-state separated from agent-readable; planted must alarm | PENDING_OPERATOR_ACCEPT_EDIT_REJECT |
| import_path_audit_alarm_rule | forbidden-truth imports must alarm; failed alarm = INVALID | PENDING_OPERATOR_ACCEPT_EDIT_REJECT |
| value_level_attacker_family_max_rule | family_max over 7 attackers ≥ C−0.05 → decodable | PENDING_OPERATOR_ACCEPT_EDIT_REJECT |

## 7. Part E — Codex Manifest-Write Task Draft

The follow-up Codex task is drafted as a SEPARATE, clearly-unauthorized file:

```text
docs/codex/tasks/LRGG-CANDIDATE-FREE-TIER0-2-FREEZE-MANIFEST-WRITE-001A.DRAFT.md
```

It is usable only after the operator returns an explicit accepted 31-field table. See that file
for the full contract. Summary of its hard constraints: Codex may only transcribe operator-
accepted values; must not infer/optimize/tune/normalize/simplify/change; must re-readback canonical
sources (host/file-API, not the truncating mount); must verify the PREFLIGHT host-SHA note; must
replace all 31 UNFROZEN_OPERATOR_REQUIRED entries; must preserve the implementation/run block;
must not implement, run, create artifacts, commit, push, tag, or remote-anchor; must return hashes
and confirm zero unresolved freeze fields. Expected Codex verdict:
`freeze_manifest_filled_from_operator_values_requires_readback_and_separate_run_authorization`.

## 8. Whether Manifest May Be Written Now

```text
NO. This is a proposal. The manifest may be written only after the operator returns an explicit
ACCEPT/EDIT/REJECT decision for all 31 fields, and only by the separately-usable Codex
manifest-write task. Codex may not infer or tune any value.
```

## 9. Whether Implementation / Run May Be Authorized Now

```text
NO. Even a fully written manifest only unblocks a SEPARATELY authorized Tier 0-2 cheap-tier
implementation/run, whose best attainable verdict is
cheap_tier_plumbing_valid_not_saturated__proceed_to_separately_authorized_heavier_tiers. No
admission, headroom, candidate, Tier 3+, or 001C authorization follows from this task.
```

## 10. Strongest Objection

```text
The decisive objection is that this task crosses from "operator-required, no number" (the prior
proposal's stance) to proposing concrete magnitudes (eps_equiv=0.05, gamma_signal=0.10, tau=0.90,
beta_fail=0.30, n=10x20, H_min=11 bits, B=8, coverage 0.10). Each magnitude is a DESIGN choice,
not a source-derived constant; an adversary could argue the package smuggles in a particular gate
strictness under the banner of "pre-result freeze." Three things bound this risk: (i) every number
is justified by pre-result design reasoning (statistical sizing, coupling inequalities, cheap-tier
budget) and NONE by results; (ii) the numbers are mutually consistent (Part C) and the safety-
critical ones are flagged operator_should_edit; (iii) the operator must explicitly accept each,
and no number can be changed after results without invalidating the run. The residual, irreducible
risk is that the operator accepts defaults that are jointly lenient enough to let a borderline
environment pass the cheap tier — which is precisely why even a clean Tier 0-2 result is capped at
the non-admission proceed label and cannot authorize candidate work. Secondary objection: the
in-sandbox mount still truncates PREFLIGHT, so the host-SHA closure relies on the operator's
certutil result; any executor must re-verify via host/file-API.
```

## 11. Next Minimal Closed-Loop Action

```text
1. Operator fills the Part D table (ACCEPT/EDIT/REJECT per field), paying special attention to the
   5 operator_should_edit fields (tau_oracle, seed_count, context_count, H_min, max_enumerability).
2. Operator returns the completed 31-field table.
3. The separately-usable Codex task (Part E draft) transcribes the accepted values into the freeze
   manifest verbatim, re-verifies readback + PREFLIGHT host SHA, and reports hashes + zero
   unresolved fields.
4. With a fully-frozen manifest, a SEPARATE Tier 0-2 cheap-tier run authorization may then be
   requested.
```

## 12. What This Does Not Prove

This task does not prove LRGG admissibility, candidate-free headroom, oracle validity, baseline
failure, replay/provenance validity, leakage scanner validity, mechanism evidence, agency / self /
subjectivity / emotion / consciousness / autonomy evidence, EGO readiness, H0/H1, 001A downgrade,
001C authorization, or TLGP-001B-R2 reinterpretation. It writes no manifest value, authorizes no
implementation/run, and upgrades no verdict.

## 13. Acceptance Readback (scope of this task)

```text
Creates only:
  docs/codex/tasks/LRGG-CANDIDATE-FREE-TIER0-2-FREEZE-NUMERIC-RESOLUTION-AND-MANIFEST-WRITE-PREP-001A.md
  docs/codex/tasks/LRGG-CANDIDATE-FREE-TIER0-2-FREEZE-MANIFEST-WRITE-001A.DRAFT.md  (unauthorized draft)
Does NOT modify the freeze manifest, the prior proposal/table/cards, contracts, src, tests,
artifacts, or research. No implementation, run, commit, push, tag, or remote anchor is authorized.
```
