# LRGG-CANDIDATE-FREE-TIER0-2-FREEZE-MANIFEST-001A

Task ID: `LRGG-CANDIDATE-FREE-TIER0-2-FREEZE-AND-RUN-CARD-001A`

Manifest ID: `LRGG-CANDIDATE-FREE-TIER0-2-FREEZE-MANIFEST-001A`

Status: operator freeze manifest template only.

Auto-Remote-Anchor: forbidden.

## Status Block

Current layer:

```text
engineering-governance / pre-execution freeze manifest
```

Mainline integration status:

```text
none
```

No EGO runtime, mainline, bridge, admission, UI, product behavior, mechanism candidate,
Tier 3, Tier 4-5, remote anchor, or 001C path is integrated or touched by this manifest.

Enabled status:

```text
none
```

This manifest enables no generator, scorer, oracle, baseline, replay, leakage scanner,
provenance checker, tamper probe, training path, Gate run, or EGO path.

Real trigger evidence:

```text
confirm_accept_for_operator_freeze_and_tier0_2_authorization
```

This manifest is downstream of the confirmed execution-card repair that closed the
admission-verdict claim leak:

- `admissible_for_candidate_preflight` is not emittable by Tier 0-2 cheap-tier.
- The only non-blocked cheap-tier label is
  `cheap_tier_plumbing_valid_not_saturated__proceed_to_separately_authorized_heavier_tiers`.
- That label does not prove headroom.
- That label does not authorize candidate-card drafting.
- That label only permits requesting separately authorized heavier tiers.

Claim ceiling:

```text
This manifest can only list the values that must be frozen before any Tier 0-2 cheap-tier
implementation or run. It is not evidence and does not authorize execution.
```

## Source Readback Basis

This manifest was drafted after repo-local content readback from:

- `docs/codex/tasks/LRGG-CANDIDATE-FREE-CHEAP-TIER-EXECUTION-001A.md`
- `docs/codex/tasks/LRGG-CANDIDATE-FREE-PREFLIGHT-001A.md`
- `docs/codex/contracts/BASELINE-IMMUNITY-ADMISSION-STANDARD-001A.md`
- `docs/codex/contracts/BASELINE-IMMUNITY-ADMISSION-STANDARD-001A.registry.json`

Readback status for this drafting task:

```text
required_sources_readable
```

If any future executor cannot read these sources directly through file/API content readback,
the only permitted blocking label is:

```text
blocked_pending_canonical_readback
```

## Freeze Discipline

Codex may not choose, infer, optimize, tune, or backfill any value in this manifest.

Any field still marked:

```text
UNFROZEN_OPERATOR_REQUIRED
```

blocks implementation/run.

Any threshold, split, budget, metric, aggregation rule, or tamper expectation changed after
seeing outputs invalidates the run.

If all values are frozen later by the operator before implementation/run, this manifest
becomes the prereg freeze source for the Tier 0-2 cheap-tier debug preflight.

## Freeze Fields

| Field | Frozen value / rule status |
|---|---|
| `tau_oracle` | `0.90` |
| `random_majority_ceiling` | `no_fair_signal if max(random,majority) ≥ C−0.10` |
| `trivial_predictor_oracle_band_threshold` | `degenerate if predict_all/none/constant_k ≥ C−0.05` |
| `metric_balance_rule` | `F-beta, beta=1.0 + trivial-predictor controls; no single-sided metric` |
| `obs_only_block_threshold` | `block if obs-only/memoryless ≥ C−0.05` |
| `lookup_graph_cache_block_threshold` | `saturated if lookup/6-graph-cache/traj-NN ≥ C−0.05` |
| `direct_objective_optimizer_block_threshold` | `saturated if discounted_wls / least_squares / convex_objective_solver ≥ C−0.05` |
| `task_specific_classical_block_threshold` | `saturated if DP / finite-state filter / classical planner ≥ C−0.05` |
| `n_gram_block_threshold` | `saturated if n-gram history sweep h∈{1,2,3,5} ≥ C−0.05` |
| `raw_observation_latent_decodability_ceiling` | `decodable if raw-observation decoder or value-level family_max ≥ C−0.05` |
| `cheap_tier_debug_split_seed_count` | `10` |
| `cheap_tier_debug_split_context_count` | `30` |
| `debug_split_seed_ids_or_generation_rule` | `seed_i = int(sha256(f"{MASTER}\|seed\|{i}").hexdigest()[:8], 16), i in 0..n_seed-1, MASTER="LRGG-T02-DEBUG-001A"; IDs not exposed to agents and do not encode rule/family/score-key` |
| `debug_split_context_ids_or_generation_rule` | `ctx_j = int(sha256(f"{MASTER}\|ctx\|{j}").hexdigest()[:8], 16), j in 0..n_ctx-1, MASTER="LRGG-T02-DEBUG-001A"; contexts disjoint from any future train/heldout context; IDs not exposed to agents` |
| `aggregation_method` | `callable verdict aggregation over recorded evidence rows; hard-stop/block conditions dominate continuous scores; family baselines decided by family_max; no static verdict dictionary; record aggregation_code_path_sha256` |
| `confidence_interval_lower_confidence_bound_rule` | `95% one-sided lower confidence bound over 300 seed/context rows; Wilson interval for proportion metrics, BCa bootstrap with >=2000 resamples otherwise; positive-looking mean without LCB clearance cannot proceed` |
| `max_train_test_leakage` | `zero tolerated known split-membership / structural leakage; membership-attacker positive control must alarm; failed positive control = INVALID; real known structural leakage blocks` |
| `minimum_task_space_entropy` | `H_min = 12 bits for T=(G,R[,C]) under frozen P_gen; realized distinct-T across 300 rows must be ≥270/300` |
| `max_enumerability_bound` | `coverage_fraction = B / N_enum^action ≤ 0.10 with B=8, therefore N_enum^action ≥80; N_enum^latent ≥3000; exhaustive or cheap enumeration reaching ≥C−0.05 emits rejected_baseline_saturated` |
| `oracle_failability_band` | `0.30, requiring C − nonreading_oracle ≥ 0.30` |
| `tamper_probe_expected_behavior` | `mutate-one-action, mutate-source-byte, mutate-hidden-graph/remapping, mutate-observation-trace, mutate-reward-trace must trigger the declared score/replay/hash mismatch; score recomputed from serialized state + trace; stored-score-only invalid` |
| `hidden_rule_id_leak_alarm_threshold` | `planted hidden-rule-ID leak must alarm; real recovery LCB ≥ chance+0.05 emits rejected_trivially_decodable` |
| `latent_graph_exposure_alarm_threshold` | `planted latent-graph exposure must alarm; real exposure LCB ≥ chance+0.05 emits rejected_trivially_decodable` |
| `task_family_id_alarm_threshold` | `planted task-family-ID exposure must alarm; real exposure LCB ≥ chance+0.05 emits rejected_trivially_decodable` |
| `score_key_reward_shaping_alarm_threshold` | `planted score-key / reward-shaping artifact must alarm; shaping-only baseline ≥ C−0.05 or score-key recovery LCB ≥ chance+0.05 emits rejected_metric_degenerate` |
| `membership_leakage_alarm_threshold` | `planted split-membership leak must alarm; real membership recovery through legal visible channels with LCB ≥ chance+0.05 emits rejected_trivially_decodable` |
| `seed_config_filename_leakage_alarm_threshold` | `planted seed/config/filename leak must alarm; scanner covers names, values, ordering, and artifact structure; real leakage emits rejected_trivially_decodable` |
| `observation_field_audit_alarm_rule` | `observation fields injected with latent/graph/ID truth must alarm; value-level and field-name scans each have positive controls; real field-level leakage emits rejected_trivially_decodable` |
| `serialized_state_audit_alarm_rule` | `serialized replay state must be separated from agent-readable observations; generator truth readable by agents must alarm; real readable truth emits rejected_trivially_decodable` |
| `import_path_audit_alarm_rule` | `forbidden imports of hidden latent / hidden graph / remapping / generator-truth / scorer-truth must alarm; failed alarm = INVALID; structurally-equivalent illegal reads must be caught, not only known names` |
| `value_level_attacker_family_max_rule` | `family_max over {mean, variance, correlation, PCA, cross-episode, supervised, membership}; if family_max ≥ C−0.05, emit rejected_trivially_decodable; decision is family_max, never a selected weak attacker` |

## Implementation Block

Before any implementation/run, the future executor must scan this manifest and stop if any
field remains `UNFROZEN_OPERATOR_REQUIRED`.

Required stop label:

```text
blocked_pending_operator_freeze
```

## What This Does Not Prove

This manifest does not prove LRGG admissibility, candidate-free headroom, oracle validity,
baseline failure, replay/provenance validity, leakage scanner validity, mechanism evidence,
agency/self/subjectivity/emotion/consciousness/autonomy evidence, EGO readiness, H0/H1,
001A downgrade, 001C authorization, or TLGP-001B-R2 reinterpretation.
