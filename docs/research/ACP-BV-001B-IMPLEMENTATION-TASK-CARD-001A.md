# ACP-BV 001B Implementation Task Card 001A

Task id: `ACP-BV-001B-IMPLEMENTATION-TASK-CARD-001A`

Card status: future implementation task card only; not execution authorization
for this current task.

## Problem Definition

ACP-BV 001A collapsed as baseline-equivalent because a fair lookup baseline
could tie the candidate. The revised ACP-BV 001B distribution-redesign spec at
`cf757ad30dd151ae77e27102679489df2653ca25` closes the predeclared R1-R5 gaps
at the specification layer, and Claude returned:

```text
accept_for_001b_implementation_task_card_drafting
```

The remaining risk is implementation-card-level: if detectors are not fail-able
and leakage controls are name-whitelist checks, the future implementation could
produce non-discriminative or stub-fed detector success. This card defines the
bounded future implementation task needed for independent hostile audit before
any ACP-BV 001B source or test work.

This current card does not implement ACP-BV 001B.

## Stage / Layer

Current stage/layer for this card: mechanism-hypothesis / engineering-
governance implementation-task-card drafting only.

Future implementation layer if independently accepted: engineering
implementation of an isolated offline evidence harness, with mechanism-
hypothesis testing claim ceiling only.

## Mainline Target

Future implementation mainline target: none. The future implementation must
remain an isolated offline harness and artifact generator.

It must not wire into Gate3, Gate4, admission, bridge, runtime, scheduler,
companion behavior, AIRI, LLM integration, EGO mainline, deployment, or any live
path.

## Enabled Requirement

Future implementation enabled-state requirement: local CLI/test execution only,
explicitly invoked by the future task. No enabled runtime path, no scheduler, no
background process, no bridge, no admission path, and no mainline trigger.

## Real-Trigger Requirement

Future implementation real-trigger evidence must include:

- exact starting commit and tag readback for this task card after independent
  audit;
- callable command used to run the isolated harness;
- run id;
- seed list and per-seed episode IDs;
- input artifact hashes;
- output artifact paths;
- source blob hashes or git-object pins for scorer, generator, candidate,
  baselines, detectors, leakage scanner, replay, runner, and source-boundary
  verifier.

No self-reported booleans, static verdict dictionaries, or hand-written scores
may serve as trigger evidence.

## Hypothesis

An ACP-BV candidate may show mechanism-relevant offline evidence only if it
outperforms the strongest fair lookup/memory/nearest-neighbor/graph-cache family
baseline under true heldout generalization, candidate/truth decoupling,
source-pinned repo-owned truth, fail-able leakage controls, fail-able replay,
and detector-bound collapse rules.

This is a bounded hypothesis. It is not a mechanism-validity claim.

## Strongest Baseline

The strongest baseline explanation is that lookup, factorized memory,
per-component memory, graph-cache replay, query-capable imitation, or
candidate/truth coupling can match ACP-BV behavior without using an
action-conditioned predictive boundary/viability mechanism.

The future baseline matrix must include, at minimum:

- `full_access_lookup_baseline`
- `exact_key_memory_baseline`
- `factorized_lookup_baseline`
- `per_component_lookup_baseline`
- `partial_key_lookup_baseline`
- `topology_only_baseline`
- `risk_only_baseline`
- `signal_action_baseline`
- `action_conditioned_nearest_neighbor_baseline`
- `graph_cache_baseline`
- `transition_table_baseline`
- `successor_map_baseline`
- `count_table_baseline`
- `episodic_traversal_baseline`
- `fsm_planner_baseline`
- `query_capable_imitation_baseline`, if applicable to the generated
  representation
- any baseline that has access to all legal observation fields and can fairly
  exploit memory or lookup structure

The strongest baseline must be selected after execution by deterministic
`argmax(score)` over fair baselines. Tie handling must preserve the most
damaging fair baseline classification rather than selecting a more favorable
narrative baseline.

A candidate cannot be called mechanism-relevant if the strongest fair baseline
ties it under B3 bands.

## Ablation Plan

The future implementation must rerun episodes under real interventions. It must
not use static ablation rows or hand-written deltas.

Required ablations must test whether the claimed effect depends on
mechanism-relevant state/action/boundary variables rather than:

- answer-bearing fields;
- memorized keys;
- exact-key lookup;
- factorized lookup;
- per-component lookup;
- candidate/truth coupling;
- action-as-difficulty selection;
- hidden truth labels;
- future observations;
- source-boundary bypasses.

Each ablation must predeclare metric direction, equivalence threshold, minimum
effect criterion, inconclusive band, block condition, input artifacts, run id,
seed/context/episode IDs, aggregation method, callable path, and code path hash.

## Trace / Replay Plan

The future implementation must persist serialized candidate state,
observations, candidate outputs, selected baseline outputs, detector outputs,
and replay recomputation artifacts sufficient for independent rerun.

Replay must recompute candidate behavior from serialized state plus observation.
Hash-only comparison is insufficient.

Replay must be fail-able. At least one negative control must break replay
consistency and flip the replay verdict. If replay is operational and lacks a
paired fail-ability control, the future verdict must be:

```text
blocked_by_non_fail_able_detector
```

## Computed-Evidence Gate

All scores, deltas, baselines, ablations, leakage scans, novelty measurements,
factorization measurements, replay checks, source-boundary checks, and detector
verdicts must come from callable computation paths.

Each score or detector output must record:

- producer_function;
- callable source path;
- inputs;
- run_id;
- seed;
- context/episode IDs;
- aggregation method;
- code path hash;
- source blob hash or equivalent git-object pin;
- output artifact path.

Baselines must be independent callable implementations.

Ablations must rerun episodes under real interventions.

Leakage scans must include the eight positive-control classes plus renamed or
structural variants.

Replay must recompute candidate behavior from serialized state and observation.

Source-boundary/source-pin checks must carry forward the 001A repaired standard:

- git-object frozen anchor;
- callable source-boundary verification;
- tamper-after-anchor negative control;
- rejection of self-declared `repo_source_owned:true` style fields as proof;
- rejection of unpinned or stale worktree source claims.

## Acceptance Gate

The future implementation must return exactly one of the following verdict
families:

- `acp_bv_001b_mechanism_relevant_effect_candidate`
- `blocked_by_baseline_equivalence`
- `blocked_by_insufficient_heldout_novelty`
- `blocked_by_factorized_lookup_equivalence`
- `blocked_by_candidate_truth_coupling`
- `blocked_by_non_fail_able_detector`
- `blocked_by_non_fail_able_leakage_scanner`
- `blocked_by_whitelist_leakage_scanner`
- `blocked_by_unstable_or_noise_level_effect`
- `blocked_by_solvability_preflight_failure`
- `blocked_by_unsolvable_or_leaky_distribution`
- `inconclusive`
- `close_or_downgrade_current_acp_bv_surface_family`

`acp_bv_001b_mechanism_relevant_effect_candidate` is allowed only if all of the
following are true:

- true heldout generalization is satisfied;
- the novelty floor is met;
- the strongest fair baseline selected by deterministic `argmax(score)` does
  not tie the candidate under B3 bands;
- B3 thresholds are predeclared and not post-hoc tuned;
- candidate and truth generation are decoupled;
- solvability preflight succeeds without leakage;
- no candidate-authored truth is used;
- source-boundary/source-pin checks pass through callable git-object anchored
  verification;
- memory resistance defeats exact-key, factorized, per-component, partial-key,
  topology-only, risk-only, signal-action, and action-conditioned nearest-
  neighbor lookup;
- all operational detectors have paired fail-ability controls;
- the leakage scanner detects structural variants of all eight positive-
  control classes;
- per-seed episode count is adequate for the stated B3 / dispersion / CI
  decision rule;
- replay recomputation and its negative control pass;
- no second logic path bypasses the evidence path.

Any 001B collapse condition is the second collapse for the current ACP-BV
surface family after 001A. A detector-bound collapse must route to:

```text
close_or_downgrade_current_acp_bv_surface_family
```

## Hard Binding 1 - Unified Detector Failability

The future implementation must provide a predeclared paired negative control
for every operational detector:

- novelty-floor detector;
- baseline-tie detector;
- factorized-lookup-equivalence detector;
- multi-seed-stability detector;
- candidate/truth-coupling detector;
- leakage detector;
- source-boundary/source-pin detector;
- replay/recomputation detector, if used.

Each paired control must inject a concrete intervention expected to flip the
corresponding verdict. The future implementation must actually run the control
and record expected-vs-actual flip.

If any operational detector lacks a paired fail-ability control, the future
implementation verdict must be:

```text
blocked_by_non_fail_able_detector
```

## Hard Binding 2 - Leakage Positive Controls Are Not Whitelist Checks

The future implementation must prove the leakage scanner detects the eight
positive-control classes by structural detection, not by fixture name, exact
filename, or hard-coded alias.

The eight leakage positive-control classes are:

- observation-name leakage;
- action-name leakage;
- filename leakage;
- fixture-name leakage;
- candidate-authored alias leakage;
- future-observation leakage;
- hidden-truth-label leakage;
- answer-encoding metadata leakage.

For each class, the future implementation must include at least one renamed or
structurally varied positive-control probe.

If the scanner catches only the original named fixture but misses the renamed or
structural variant, the verdict must be:

```text
blocked_by_whitelist_leakage_scanner
```

## Hard Binding 3 - Per-Seed Episode Floor

The future implementation must set a minimum per-seed episode count or
explicitly justify the chosen floor before candidate evaluation.

The floor must be adequate for the B3 decision rule, dispersion estimate, and
confidence interval or predeclared equivalent. If the episode budget is too
small for the stated decision rule, the result must be downgraded to:

```text
inconclusive
```

or blocked as:

```text
blocked_by_unstable_or_noise_level_effect
```

## Hard Binding 4 - Factorization Family Completeness

The future implementation must predeclare all factorization families used by
the novelty and lookup-equivalence detectors. It must explain why no undeclared
axis creates a lookup-complete channel.

If a post-execution undeclared lookup-complete axis is found, the verdict must
be:

```text
blocked_by_factorized_lookup_equivalence
```

## Revised 001B Spec Constraints To Carry Forward

The future implementation must carry forward:

- true heldout generalization;
- fair full-access lookup from the start;
- strongest-baseline selection after execution using deterministic
  `argmax(score)` with tie handling preserving the most damaging fair baseline;
- B3 bands with no post-hoc threshold tuning;
- candidate/truth decoupling;
- solvability preflight;
- no candidate-authored truth;
- memory resistance beyond exact-key lookup;
- source-boundary/source-pin carryover from 001A;
- Anti-Zeno one-redesign rule: 001A is the first collapse, and any 001B
  collapse is the second collapse requiring closure/downgrade of the current
  ACP-BV surface family.

## Future Changed Files

The future implementation task, if independently authorized, may change only:

- `src/acp_bv_distribution_harness_001b/__init__.py`
- `src/acp_bv_distribution_harness_001b/generator.py`
- `src/acp_bv_distribution_harness_001b/candidate.py`
- `src/acp_bv_distribution_harness_001b/baselines.py`
- `src/acp_bv_distribution_harness_001b/detectors.py`
- `src/acp_bv_distribution_harness_001b/leakage_scanner.py`
- `src/acp_bv_distribution_harness_001b/replay.py`
- `src/acp_bv_distribution_harness_001b/runner.py`
- `src/acp_bv_distribution_harness_001b/source_boundary.py`
- `tests/test_acp_bv_distribution_harness_001b.py`
- `tests/test_acp_bv_detector_failability_001b.py`
- `tests/test_acp_bv_leakage_scanner_001b.py`
- `tests/test_acp_bv_replay_001b.py`
- `tests/test_acp_bv_source_boundary_001b.py`
- `artifacts/acp_bv_distribution_harness_001b_execution_001a/**`

This current drafting task must not create those files.

## Forbidden Files For Future Implementation

The future implementation task must not modify:

- EGO mainline runtime;
- UI or companion behavior;
- relationship learning;
- emotion systems;
- proactive behavior;
- LLM integration;
- AIRI integration;
- deployment;
- API keys or external services;
- global schema migrations;
- old ACP-BV 001A implementation or artifacts except read-only references;
- existing 001B spec files except read-only references, unless a separate
  audit-authorized amendment task permits docs-only repair;
- any Gate, bridge, admission, runtime, scheduler, mainline, or real Gate target
  file not explicitly listed in the future changed-file allowlist.

## Auto-Remote-Anchor Policy For Future Implementation

Auto-Remote-Anchor decision for the future implementation task: conditional.

Remote anchor is allowed only if:

- the future verdict is not blocked or inconclusive, or the future task card
  explicitly designates the result as boundary-worthy negative evidence;
- changed files are limited to the future implementation allowlist;
- no forbidden path changes;
- validation artifacts parse successfully;
- worktree and index are clean after commit;
- local HEAD equals remote branch, local tag, and remote tag after push;
- no independent audit is still pending for the boundary being anchored.

Auto anchor must remain forbidden for this current drafting task unless this
task's own validation and commit gates pass.

## Claim Ceiling

Future implementation maximum claim if all gates pass:

```text
bounded offline ACP-BV 001B mechanism-relevant effect candidate under the stated distribution and controls
```

Current card maximum claim:

```text
ACP-BV 001B implementation-task-card drafting only
```

Neither claim proves ACP-BV validity, mechanism validity, harness validity, Gate
validity, admission readiness, bridge readiness, runtime readiness, mainline
effect, agency, consciousness, emotion, autonomy, stable user benefit, or EGO
readiness.

## Stop Condition

Stop and return a blocked verdict if the future implementation:

- omits Hard Binding 1;
- omits Hard Binding 2;
- omits Hard Binding 3;
- omits Hard Binding 4;
- weakens the revised 001B spec constraints;
- authorizes or touches mainline/runtime/bridge/admission/Gate paths;
- uses candidate-authored truth;
- uses static verdicts or literal scores;
- tunes thresholds after seeing results;
- allows a non-fail-able detector to carry the verdict;
- allows whitelist-only leakage scanning;
- treats 001B collapse as authorization for 001C/001D repair.

## Rollback Plan

If future implementation touches forbidden files, revert them before reporting.

If future implementation code or tests are created outside the allowlist, delete
or revert them and report `blocked_by_scope_creep`.

If required detector fail-ability or leakage non-whitelist bindings cannot be
implemented unambiguously, preserve a blocker artifact rather than a pass-shaped
result.
