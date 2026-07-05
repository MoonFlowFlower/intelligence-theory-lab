# LRGG-CANDIDATE-FREE-TIER0-2-FREEZE-PROPOSAL-TABLE-001A

Task ID: `LRGG-CANDIDATE-FREE-TIER0-2-FREEZE-PROPOSAL-TABLE-001A`

Status: operator-facing proposal table only.

Auto-Remote-Anchor: forbidden.

## Status Block

Current layer:

```text
engineering-governance / operator-freeze preparation
```

Mainline integration status:

```text
none
```

Enabled status:

```text
none
```

Real trigger evidence:

```text
LRGG-CANDIDATE-FREE-TIER0-2-FREEZE-MANIFEST-001A.md and
LRGG-CANDIDATE-FREE-TIER0-2-IMPLEMENTATION-RUN-001A.md were drafted; all 31 freeze
fields remain UNFROZEN_OPERATOR_REQUIRED; future implementation/run remains blocked
pending operator freeze.
```

Claim ceiling:

```text
This document may only propose and classify operator-freeze decisions. It does not freeze
values, modify the freeze manifest, authorize implementation/run, authorize candidate work,
or emit any admission, headroom, mechanism, EGO, 001C, agency, self, subjectivity, emotion,
consciousness, or autonomy conclusion.
```

## Source Readback Summary

Repo state at drafting readback:

```text
branch = codex/meta-theory-scaffold
HEAD = 5c03e0af7ce097d9055de5f1ef17052fe3a576be
status = ## codex/meta-theory-scaffold...origin/codex/meta-theory-scaffold [ahead 1]
pre_existing_unrelated_dirty_or_untracked_files = yes
```

Required source files:

| Source file | Exists | SHA256 |
|---|---:|---|
| `docs/codex/tasks/LRGG-CANDIDATE-FREE-PREFLIGHT-001A.md` | yes | `764063172F264939FCAA5AEDD3C02AC72659A4B9FED281759E6DBE4502876E47` |
| `docs/codex/tasks/LRGG-CANDIDATE-FREE-CHEAP-TIER-EXECUTION-001A.md` | yes | `EF80C6D89E5C88BC12992B0E049F3B8864890D015851AACE48924E45354E3DF0` |
| `docs/codex/tasks/LRGG-CANDIDATE-FREE-TIER0-2-FREEZE-MANIFEST-001A.md` | yes | `ADB72E04B2821717B224ADCDFFD3EBDDFDA98970EDE42B4B79A5C4A1C89ADF5B` |
| `docs/codex/tasks/LRGG-CANDIDATE-FREE-TIER0-2-IMPLEMENTATION-RUN-001A.md` | yes | `73464BFE57A3998B1D1DBB886300AB64C9D68A3A6CD4ECDDBE6306E7CADA4BDD` |
| `docs/codex/contracts/BASELINE-IMMUNITY-ADMISSION-STANDARD-001A.md` | yes | `7BD41A049A28ADED4FB2EB23CED5BC8A71F80A5BB7FB5ABD6D32931C37E80A03` |
| `docs/codex/contracts/BASELINE-IMMUNITY-ADMISSION-STANDARD-001A.registry.json` | yes | `4A3170DE614D697A7FFD99D4E524AD7A2A61585F49F3F095F00B1FD6E899B43F` |

Registry parse status:

```text
registry_json_parse = ok
registry_standard_id = BASELINE-IMMUNITY-ADMISSION-STANDARD-001A
```

## Proposal Discipline

Codex does not choose final operator values in this table.

Rows marked:

```text
NO_SAFE_PROPOSAL__OPERATOR_REQUIRED
```

must remain unresolved until the operator supplies a concrete value/rule or requests a
separate design/audit step. Source-derived proposal rules are not final freeze values and
must not be used after results to tune thresholds.

The existing freeze manifest must remain unchanged until the operator explicitly fills it.

## Interpretive Constraints

Tier 0-2 cannot emit `admissible_for_candidate_preflight`.

Tier 0-2 cannot authorize candidate-card drafting, prove LRGG admissibility, prove
candidate-free headroom, prove oracle validity, prove mechanism evidence, authorize EGO
readiness, or authorize 001C.

The cheap-tier proceed label only permits requesting separately authorized heavier tiers:

```text
cheap_tier_plumbing_valid_not_saturated__proceed_to_separately_authorized_heavier_tiers
```

Negative outcomes are valid evidence, not failures to patch.

Allowed future Tier 0-2 terminal labels:

```text
rejected_metric_degenerate
rejected_no_fair_signal
rejected_trivially_decodable
rejected_baseline_saturated
INVALID
blocked_pending_canonical_readback
blocked_pending_operator_freeze
cheap_tier_plumbing_valid_not_saturated__proceed_to_separately_authorized_heavier_tiers
```

Forbidden labels:

```text
admissible_for_candidate_preflight
pass
ready
integrated
live
mechanism-valid
EGO-ready
001C-authorized
```

## Proposal Table

| field_name | current_manifest_value | decision_class | proposed_value_or_rule | source_basis | rationale | risk_if_too_weak | risk_if_too_strict | failure_behavior | operator_freeze_allowed | notes_for_claude_audit |
|---|---|---|---|---|---|---|---|---|---|---|
| `tau_oracle` | `UNFROZEN_OPERATOR_REQUIRED` | `operator_choice_required` | `NO_SAFE_PROPOSAL__OPERATOR_REQUIRED` | `LRGG-CANDIDATE-FREE-PREFLIGHT-001A.md` Required Threshold Placeholders; `LRGG-CANDIDATE-FREE-CHEAP-TIER-EXECUTION-001A.md` Operator Freeze Requirements | Sources require oracle solvability and a frozen tau but provide no numeric tau. A numeric value chosen here would be post-hoc risk without operator authority. | A low tau can let an underpowered oracle pass and make invalid plumbing look usable. | A high tau can falsely block a debug split before testing cheap-tier plumbing. | `INVALID` | `no_requires_claude_audit` | Check whether any accepted source supports a numeric oracle tau or whether a new design note is required. |
| `random_majority_ceiling` | `UNFROZEN_OPERATOR_REQUIRED` | `conservative_block_threshold` | Rule proposal only: freeze a pre-output ceiling band; if random or majority/mode reaches the band, emit `rejected_no_fair_signal`. | Baseline standard section 2.5 random; registry `trivial_predictors`; CHEAP Required Baselines | The rule is source-derived and conservative because random/majority near ceiling means no fair signal. The numeric band still requires operator freeze. | A weak ceiling lets no-signal distributions proceed. | An overly strict ceiling can reject noisy but usable debug signal. | `rejected_no_fair_signal` | `yes_after_operator_review` | Check that random and majority are marginal/size matched and not underpowered. |
| `trivial_predictor_oracle_band_threshold` | `UNFROZEN_OPERATOR_REQUIRED` | `conservative_block_threshold` | Rule proposal only: if `predict_all`, `predict_none`, or `constant_k_sweep` reaches the operator-frozen oracle/ceiling band, emit `rejected_metric_degenerate`. | Baseline standard sections 2.1 to 2.3; registry `trivial_predictors`; CHEAP trivial_predictors | This directly protects against recall-only, abstention-only, and fixed-size metric degeneracy before any candidate work. | A weak band can let trivial predictors hide inside the metric. | An overly strict band can reject harmless constant baselines due to noise. | `rejected_metric_degenerate` | `yes_after_operator_review` | Check the k sweep covers the relevant full output cardinality. |
| `metric_balance_rule` | `UNFROZEN_OPERATOR_REQUIRED` | `source_derived` | Rule proposal only: use a balanced or cost-weighted metric with visible `predict_all`, `predict_none`, and `constant_k_sweep` controls; no single-sided recall-only or precision-only metric. | Baseline standard sections 2.6 and 2.7; PREFLIGHT R1; CHEAP Scorer Contract | This is source-derived and non-post-hoc because the metric form must be frozen before outputs and checked against trivial predictors. | A weak metric can be saturated by set size, abstention, or all-positive prediction. | An overly strict metric can block a debug split by over-penalizing legitimate oracle behavior. | `rejected_metric_degenerate` | `yes_after_operator_review` | Check whether the selected balance rule is compatible with the target output structure. |
| `obs_only_block_threshold` | `UNFROZEN_OPERATOR_REQUIRED` | `conservative_block_threshold` | Rule proposal only: if observation-only or passive visible-channel attackers reach the operator-frozen block band, emit `rejected_trivially_decodable` or no-fair-signal classification as applicable. | Baseline standard sections 3.1 and 3.2; CHEAP Required Baselines; PREFLIGHT R6 | This prevents visible/passive-channel decodability from being mistaken for mechanism headroom. | A weak threshold lets passive leakage or visible target determination slip through. | An overly strict threshold can reject a debug split with residual but noisy passive signal. | `rejected_trivially_decodable` | `yes_after_operator_review` | Check whether obs-only features have exactly the legal access intended for fair baselines. |
| `lookup_graph_cache_block_threshold` | `UNFROZEN_OPERATOR_REQUIRED` | `conservative_block_threshold` | Rule proposal only: if lookup or any six-member graph-cache family member reaches oracle-equivalence band, emit `rejected_baseline_saturated`. | Baseline standard section 5 graph-cache challengers; registry `graph_cache_challengers`; CHEAP graph_cache_family | This is the canonical cheap-collapse control for representational or environment claims. | A weak threshold lets lookup or graph-cache saturation masquerade as headroom. | An overly strict threshold can block if graph-cache is close but clearly below oracle under uncertainty. | `rejected_baseline_saturated` | `yes_after_operator_review` | Check all six members run with legal access parity and no hidden shortcut. |
| `direct_objective_optimizer_block_threshold` | `UNFROZEN_OPERATOR_REQUIRED` | `conservative_block_threshold` | Rule proposal only: if any direct objective optimizer under legal access reaches oracle-equivalence band, emit `rejected_baseline_saturated`. | Baseline standard section 5 direct objective optimizer; registry `direct_objective_optimizer`; CHEAP Required Baselines | This controls the false explanation that the surface is solved by direct metric optimization. | A weak threshold can allow closed-form objective solving to appear mechanism-like. | An overly strict threshold can reject a debug split where direct optimizers are only near but not equivalent. | `rejected_baseline_saturated` | `yes_after_operator_review` | Check optimizer implementations are independent and not weaker than the objective permits. |
| `task_specific_classical_block_threshold` | `UNFROZEN_OPERATOR_REQUIRED` | `conservative_block_threshold` | Rule proposal only: if hand-coded DP, finite-state filter, or classical planner under legal access reaches oracle-equivalence band, emit `rejected_baseline_saturated`. | Baseline standard section 5 task-specific classical; registry `task_specific_classical`; CHEAP Required Baselines | This blocks task-specific classical solutions from being reinterpreted as mechanism evidence. | A weak threshold lets a classical solver saturate the task while the route proceeds. | An overly strict threshold can reject a split where classical methods are informative but non-saturating. | `rejected_baseline_saturated` | `yes_after_operator_review` | Check the classical baseline is the strongest known legal method for the task type. |
| `n_gram_block_threshold` | `UNFROZEN_OPERATOR_REQUIRED` | `conservative_block_threshold` | Rule proposal only: if n-gram or short-history cache reaches the operator-frozen block band, emit `rejected_baseline_saturated`. | Baseline standard section 5 lookup imitation; CHEAP Other cheap baselines | This blocks short-history memorization from being mistaken for structural inference. | A weak threshold lets local-history cache saturation pass. | An overly strict threshold can reject a split where n-gram behavior is below oracle with meaningful residual. | `rejected_baseline_saturated` | `yes_after_operator_review` | Check history length sweep is sufficient for the debug distribution. |
| `raw_observation_latent_decodability_ceiling` | `UNFROZEN_OPERATOR_REQUIRED` | `conservative_block_threshold` | Rule proposal only: if raw-observation latent decoder or value-level attacker `family_max` reaches the ceiling, emit `rejected_trivially_decodable`. | Baseline standard section 3.2; registry `passive_baselines`; PREFLIGHT R6; CHEAP Other cheap baselines | This protects the decodability wall: raw observations must not directly reveal the latent target. | A weak ceiling lets latent leakage become apparent headroom. | An overly strict ceiling can reject noisy but non-saturating latent signals. | `rejected_trivially_decodable` | `yes_after_operator_review` | Check decodability probes include value-level and structural features, not names only. |
| `cheap_tier_debug_split_seed_count` | `UNFROZEN_OPERATOR_REQUIRED` | `split_design_parameter` | `NO_SAFE_PROPOSAL__OPERATOR_REQUIRED` | PREFLIGHT Required Threshold Placeholders; CHEAP Operator Freeze Requirements | Sources require seed/context count freeze but provide no defensible numeric debug split size. | Too few seeds can miss leakage, cache saturation, or variance. | Too many seeds can make cheap-tier preflight exceed intended debug budget. | `blocked_pending_operator_freeze` | `no_requires_claude_audit` | Check whether a minimum debug seed count can be justified from prior accepted methodology. |
| `cheap_tier_debug_split_context_count` | `UNFROZEN_OPERATOR_REQUIRED` | `split_design_parameter` | `NO_SAFE_PROPOSAL__OPERATOR_REQUIRED` | PREFLIGHT Required Threshold Placeholders; CHEAP Operator Freeze Requirements | Sources require context count freeze but provide no defensible numeric count. | Too few contexts can turn the split into a memorized or enumerable toy. | Too many contexts can convert cheap-tier debug into an unauthorized heavier run. | `blocked_pending_operator_freeze` | `no_requires_claude_audit` | Check whether context count should be tied to entropy or graph-family coverage. |
| `debug_split_seed_ids_or_generation_rule` | `UNFROZEN_OPERATOR_REQUIRED` | `split_design_parameter` | Rule proposal only: freeze explicit seed IDs or a deterministic pre-output generation rule; keep IDs from becoming filename/config leakage. | PREFLIGHT Tier 0 generator deterministic check; CHEAP Generator Contract; baseline standard section 3.5 | Deterministic preregistration is source-derived and prevents post-output seed selection. | A weak rule allows seed cherry-picking or split leakage. | An overly rigid rule can block harmless reproducible debug generation. | `blocked_pending_operator_freeze` | `yes_after_operator_review` | Check the rule is reproducible and does not leak target family or split membership. |
| `debug_split_context_ids_or_generation_rule` | `UNFROZEN_OPERATOR_REQUIRED` | `split_design_parameter` | Rule proposal only: freeze explicit context IDs or a deterministic pre-output generation rule; require disjointness from any train/heldout context if later added. | PREFLIGHT Tier 0; CHEAP Generator Contract; baseline standard section 3.5 | This avoids post-hoc context selection and future train/test contamination. | A weak rule allows context cherry-picking or hidden overlap. | An overly rigid rule can block valid deterministic contexts. | `blocked_pending_operator_freeze` | `yes_after_operator_review` | Check context IDs cannot encode hidden rule, family, or score key. |
| `aggregation_method` | `UNFROZEN_OPERATOR_REQUIRED` | `aggregation_rule` | Rule proposal only: callable verdict aggregation over recorded evidence rows; hard-stop conditions dominate; family baselines use family max; no static verdict dictionary. | PREFLIGHT Real-Trigger Evidence Requirement; CHEAP Required Evidence Artifacts; AGENTS computed-evidence gate | This is non-post-hoc because the aggregation path must be callable and frozen before outputs. | A weak aggregation can average away a hard blocker or ignore a saturated family member. | An overly strict aggregation can turn any benign warning into INVALID. | `INVALID` | `yes_after_operator_review` | Check blocker precedence and family-max semantics are implemented in the future callable aggregator. |
| `confidence_interval_lower_confidence_bound_rule` | `UNFROZEN_OPERATOR_REQUIRED` | `aggregation_rule` | Rule proposal only: use an operator-frozen lower-confidence-bound rule over seed/context evidence; confidence level and estimator remain operator-required before outputs. | PREFLIGHT Required Threshold Placeholders; CHEAP Operator Freeze Requirements; R2 LCB language | LCB discipline is source-derived, but its numeric confidence level is not specified by accepted sources. | A weak or missing LCB lets noisy positive-looking scores proceed. | An overly strict LCB can falsely block a usable debug split due to small sample uncertainty. | `INVALID` | `yes_after_operator_review` | Check the LCB estimator is valid for the chosen seed/context counts. |
| `max_train_test_leakage` | `UNFROZEN_OPERATOR_REQUIRED` | `leakage_alarm_rule` | Rule proposal only: freeze zero tolerated known split-membership leakage plus a positive-control membership alarm rule; any detected leakage above the rule blocks. | Baseline standard sections 3.4 and 3.5; CHEAP Leakage Positive Controls | Leakage is source-blocking and must be pre-output fail-able. Zero known structural leakage is conservative as a rule, while scanner thresholds still need operator freeze. | A weak rule lets train/test or split-membership leakage inflate results. | An overly strict rule can block on benign metadata that agents cannot access. | `rejected_trivially_decodable` | `yes_after_operator_review` | Check what channels are agent-visible and whether membership attackers have legal access. |
| `minimum_task_space_entropy` | `UNFROZEN_OPERATOR_REQUIRED` | `measure_definition_required` | `NO_SAFE_PROPOSAL__MEASURE_DEFINITION_REQUIRED_BEFORE_OPERATOR_VALUE` | PREFLIGHT Required Threshold Placeholders; CHEAP Generator Contract; PREFLIGHT Stop/Rollback task-space too small | Sources require task-space entropy, but no operator value is measurable until entropy is defined over a named random variable such as hidden graph distribution, remapping distribution, context distribution, joint task-instance distribution, or another explicitly named LRGG task-space variable. A numeric entropy value without a defined measurement space is invalid. | Too little entropy makes enumeration, lookup, or cache saturation likely. | Too much entropy can make debug oracle/scorer validation fail for capacity reasons. | `INVALID` | `no_requires_claude_audit` | Implementation/run remains blocked until both the measure definition and value/rule are frozen before results. Entropy failure maps to `INVALID` because the precondition is unmeasurable or the task space is too small. |
| `max_enumerability_bound` | `UNFROZEN_OPERATOR_REQUIRED` | `measure_definition_required` | `NO_SAFE_PROPOSAL__MEASURE_DEFINITION_REQUIRED_BEFORE_OPERATOR_VALUE` | PREFLIGHT Required Threshold Placeholders; CHEAP Other cheap baselines exhaustive legal probe | Sources require a max enumerability bound, but no operator value is measurable until enumerability is defined over a named space such as legal action space, latent graph count, remapping count, reduced-world count, context count, joint task-instance count, or another explicitly named enumerable LRGG space. A numeric enumerability value without a defined measurement space is invalid. | A weak bound lets exhaustive legal probe saturate and erase headroom. | An overly strict bound can reject a small debug split before cheap-tier plumbing is tested. | `rejected_baseline_saturated` | `no_requires_claude_audit` | Implementation/run remains blocked until both the measure definition and value/rule are frozen before results. Enumerability failure maps to `rejected_baseline_saturated` when exhaustive legal probe or cheap enumeration saturates. |
| `oracle_failability_band` | `UNFROZEN_OPERATOR_REQUIRED` | `conservative_invalid_threshold` | Rule proposal only: require `budget_faithful_visible_channel_oracle - nonreading_oracle` to exceed an operator-frozen band; otherwise INVALID. | PREFLIGHT R2 nonreading_oracle_ablation; CHEAP Oracle Contract | This makes the oracle fail-able and prevents a non-reading path from being accepted. | A weak band lets a non-reading or truth-leaking oracle pass. | An overly strict band can invalidate a legitimate but noisy oracle ablation. | `INVALID` | `yes_after_operator_review` | Check the nonreading ablation preserves legal access while disabling latent estimation. |
| `tamper_probe_expected_behavior` | `UNFROZEN_OPERATOR_REQUIRED` | `tamper_expectation` | Rule proposal only: action, source byte, hidden graph/remapping, observation trace, and reward trace mutations must change recomputed score where expected or trip provenance where expected. | CHEAP Replay/Provenance Schema; IMPLEMENTATION-RUN Required Future Replay/Provenance Fields | This is source-derived and protects against stored-score evidence and provenance bypass. | A weak expectation lets tampering leave official evidence unchanged. | An overly strict expectation can fail when a mutation is semantically neutral by design. | `INVALID` | `yes_after_operator_review` | Check each tamper class has a declared expected effect before outputs. |
| `hidden_rule_id_leak_alarm_threshold` | `UNFROZEN_OPERATOR_REQUIRED` | `leakage_alarm_rule` | Rule proposal only: planted hidden-rule-ID leak must alarm; real hidden-rule-ID exposure above the operator-frozen alarm rule emits `rejected_trivially_decodable`. | PREFLIGHT Required Leakage Positive Controls; CHEAP Leakage Positive Controls | Hidden rule ID is a direct side channel and must be detected through positive controls. | A weak alarm lets ID leakage solve the task. | An overly strict alarm can flag benign identifiers not visible to agents. | `rejected_trivially_decodable` | `yes_after_operator_review` | Check detector is not name-only and has a true positive control. |
| `latent_graph_exposure_alarm_threshold` | `UNFROZEN_OPERATOR_REQUIRED` | `leakage_alarm_rule` | Rule proposal only: planted latent graph exposure must alarm; real exposure above the frozen alarm rule emits `rejected_trivially_decodable`. | PREFLIGHT Required Leakage Positive Controls; CHEAP Leakage Positive Controls | Latent graph exposure can collapse the task to direct decoding or graph-cache saturation. | A weak alarm lets graph exposure masquerade as inference. | An overly strict alarm can block benign structural metadata. | `rejected_trivially_decodable` | `yes_after_operator_review` | Check whether graph hashes, IDs, or serialized fields leak equivalent information. |
| `task_family_id_alarm_threshold` | `UNFROZEN_OPERATOR_REQUIRED` | `leakage_alarm_rule` | Rule proposal only: planted task-family ID exposure must alarm; real exposure above the frozen rule emits `rejected_trivially_decodable`. | PREFLIGHT Required Leakage Positive Controls; CHEAP Leakage Positive Controls | Task-family IDs can route baselines or agents to a hidden shortcut. | A weak alarm lets family-conditioned lookup pass. | An overly strict alarm can block harmless public task metadata. | `rejected_trivially_decodable` | `yes_after_operator_review` | Check whether family IDs correlate with hidden rule, remapping, or score key. |
| `score_key_reward_shaping_alarm_threshold` | `UNFROZEN_OPERATOR_REQUIRED` | `leakage_alarm_rule` | Rule proposal only: planted score-key or reward-shaping artifact must alarm; real exposure above the frozen rule emits `rejected_metric_degenerate`. | PREFLIGHT Required Leakage Positive Controls; CHEAP Leakage Positive Controls; baseline standard section 2 metric degeneracy | Score-key exposure can let a baseline optimize the metric rather than infer structure. | A weak alarm lets reward shaping or score-key leaks create false positives. | An overly strict alarm can reject legitimate reward observations. | `rejected_metric_degenerate` | `yes_after_operator_review` | Check whether reward fields are legal observations or scorer-only truth. |
| `membership_leakage_alarm_threshold` | `UNFROZEN_OPERATOR_REQUIRED` | `leakage_alarm_rule` | Rule proposal only: planted split-membership leak must alarm; real membership leakage above the frozen rule emits `rejected_trivially_decodable`. | PREFLIGHT Required Leakage Positive Controls; baseline standard sections 3.4 and 3.5 | Membership leakage contaminates train/test or debug/heldout interpretation. | A weak alarm lets split membership explain performance. | An overly strict alarm can flag non-agent-visible bookkeeping. | `rejected_trivially_decodable` | `yes_after_operator_review` | Check membership attacker uses only legal visible channels. |
| `seed_config_filename_leakage_alarm_threshold` | `UNFROZEN_OPERATOR_REQUIRED` | `leakage_alarm_rule` | Rule proposal only: planted seed/config/filename leak must alarm; real filename or config leakage above the frozen rule emits `rejected_trivially_decodable`. | PREFLIGHT Required Leakage Positive Controls; baseline standard section 3.4 leakage channels | Filename and config side channels are known leakage families and must be covered beyond value fields. | A weak alarm lets path or config names carry hidden labels. | An overly strict alarm can block ordinary reproducibility metadata not visible to agents. | `rejected_trivially_decodable` | `yes_after_operator_review` | Check scanner covers names, values, ordering, and artifact structure. |
| `observation_field_audit_alarm_rule` | `UNFROZEN_OPERATOR_REQUIRED` | `leakage_alarm_rule` | Rule proposal only: observation fields injected with latent, graph, or ID truth must alarm; real field-level leakage emits `rejected_trivially_decodable`. | PREFLIGHT Required Leakage Positive Controls; CHEAP Leakage Positive Controls | Observation-field audit is the direct guard against hidden labels entering legal observations. | A weak rule lets labels hide in observation field names or values. | An overly strict rule can block legal observations required by the task. | `rejected_trivially_decodable` | `yes_after_operator_review` | Check value-level and field-name scans both have positive controls. |
| `serialized_state_audit_alarm_rule` | `UNFROZEN_OPERATOR_REQUIRED` | `leakage_alarm_rule` | Rule proposal only: serialized state embedding generator truth readable by agents must alarm; real readable truth emits `rejected_trivially_decodable`. | PREFLIGHT Required Leakage Positive Controls; CHEAP Leakage Positive Controls | Serialized state is part of replay, so it must not become a hidden answer channel. | A weak rule lets replay state carry direct truth. | An overly strict rule can block necessary replay state serialization. | `rejected_trivially_decodable` | `yes_after_operator_review` | Check replay-required state is separated from agent-readable observations. |
| `import_path_audit_alarm_rule` | `UNFROZEN_OPERATOR_REQUIRED` | `leakage_alarm_rule` | Rule proposal only: forbidden imports of hidden latent, hidden graph, remapping, generator truth, or scorer truth must alarm; failed alarm is INVALID. | CHEAP Oracle Contract; PREFLIGHT Required Leakage Positive Controls; baseline standard section 3.4 leakage channels | Import-path controls prevent oracle, generator, scorer, or future candidates from reading truth directly. | A weak rule lets illegal truth reads produce apparent solvability. | An overly strict rule can block legitimate source hashing or module imports. | `INVALID` | `yes_after_operator_review` | Check allowlist versus denylist is not hardcoded only to known names. |
| `value_level_attacker_family_max_rule` | `UNFROZEN_OPERATOR_REQUIRED` | `leakage_alarm_rule` | Rule proposal only: compute `family_max` over mean, variance, correlation, PCA, cross-episode, supervised, and membership attackers; if it reaches the decodability ceiling, emit `rejected_trivially_decodable`. | Baseline standard section 3.2; registry `passive_baselines`; PREFLIGHT Required Leakage Positive Controls | Family max is source-derived and prevents selecting a weak value-level attacker after outputs. | A weak rule lets one value-level attacker decode while the report cites a weaker one. | An overly strict rule can block if one attacker overfits noise on a tiny debug split. | `rejected_trivially_decodable` | `yes_after_operator_review` | Check all family members share legal access and the supervised attacker does not leak labels. |

## Required Baseline Threshold Coverage Addendum

Every required future cheap-tier baseline must be governed by a frozen threshold
or threshold-family mapping before implementation/run. No required baseline may
run without a predeclared frozen threshold or threshold-family mapping. If a
future implementation introduces a required baseline not covered by the freeze
manifest or this proposal table, execution must stop with
`blocked_pending_operator_freeze`.

Threshold-family mapping must be frozen before results and cannot be chosen after seeing scores.

Explicit required mappings:

| Required baseline | Frozen-threshold mapping | Failure behavior | Boundary condition |
|---|---|---|---|
| `trajectory_nearest_neighbor` | Governed by `lookup_graph_cache_block_threshold` if implemented as episode/trajectory retrieval or nearest-neighbor lookup over legal visible histories. | `rejected_baseline_saturated` | If future implementation gives it different access or semantics, a dedicated frozen threshold must be added before run. |
| `memoryless_policy` | Governed by `obs_only_block_threshold` if implemented as current-observation-only / no-history / no-cross-episode-memory baseline. | `rejected_trivially_decodable` or `rejected_no_fair_signal`, depending on whether it indicates passive decodability or no fair signal. | If future implementation gives it different access or semantics, a dedicated frozen threshold must be added before run. |

Entropy/enumerability label split:

```text
minimum_task_space_entropy failure = INVALID because the task-space precondition is unmeasurable or too small.
max_enumerability_bound failure = rejected_baseline_saturated when cheap legal enumeration or exhaustive legal probe saturates.
```

## Table Counts

```text
total_freeze_fields = 31
fields_with_safe_proposal_rules = 26
fields_requiring_operator_decision = 31
fields_requiring_claude_audit_before_freeze = 5
unsupported_fields_requiring_no_safe_proposal_or_measure_definition = 5
```

The 5 unsupported fields are:

```text
tau_oracle
cheap_tier_debug_split_seed_count
cheap_tier_debug_split_context_count
minimum_task_space_entropy
max_enumerability_bound
```

## Acceptance Readback

This task creates only:

```text
docs/codex/tasks/LRGG-CANDIDATE-FREE-TIER0-2-FREEZE-PROPOSAL-TABLE-001A.md
```

It does not modify:

```text
docs/codex/tasks/LRGG-CANDIDATE-FREE-TIER0-2-FREEZE-MANIFEST-001A.md
docs/codex/tasks/LRGG-CANDIDATE-FREE-TIER0-2-IMPLEMENTATION-RUN-001A.md
src/**
tests/**
artifacts/**
docs/research/**
docs/codex/contracts/**
```

No implementation, run, generator, scorer, oracle, baseline, replay, leakage test, tamper
probe, artifact generation, commit, push, tag, or remote anchor is authorized by this file.

## Next Minimal Closed-Loop Action

Operator reviews this proposal table, resolves the 5 unsupported fields through a separate
operator/audit/design decision, and then decides whether to fill the freeze manifest. Only a
fully resolved freeze manifest can unblock a separately authorized Tier 0-2 implementation/run.
