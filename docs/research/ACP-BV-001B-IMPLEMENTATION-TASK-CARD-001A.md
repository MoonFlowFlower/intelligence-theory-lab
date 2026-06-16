# ACP-BV 001B Implementation Task Card 001A

Task id: `ACP-BV-001B-IMPLEMENTATION-TASK-CARD-001A`

Card status: future implementation task card only; not execution authorization
for this current task.

Revision status: revised by
`acp_bv_001b_implementation_task_card_001a_revision_001a` after independent
hostile audit returned:

```text
requires_implementation_card_revision_before_implementation
```

## Problem Definition

ACP-BV 001A collapsed as baseline-equivalent because a fair lookup baseline
could tie the candidate. The revised ACP-BV 001B distribution-redesign spec at
`cf757ad30dd151ae77e27102679489df2653ca25` closes the predeclared R1-R5 gaps
at the specification layer, and Claude returned:

```text
accept_for_001b_implementation_task_card_drafting
```

Claude then independently audited this implementation task card at commit:

```text
7715dfd1322e416dc150fbbd7dde005d669180fb
```

with tag:

```text
remote-anchor-acp-bv-001b-implementation-task-card-001a-7715dfd
```

and returned:

```text
requires_implementation_card_revision_before_implementation
```

The audit did not hard-block the ACP-BV 001B spec and did not reopen the R1-R5
spec revision. The four hard bindings were present, the implementation-card
scope was clean, the baseline matrix was strong, and the computed-evidence and
source-boundary contracts were present. The revision required here closes two
highest-risk historical false-pass modes:

- detector-stub / non-fail-able detector: expected-vs-actual flip recording was
  required, but actual flip divergence did not explicitly block the future
  implementation verdict;
- whitelist leakage scanner: renamed or structural variants were required, but
  one predeclared variant per leakage class could still be defeated by
  whitelisting the original fixture plus that known variant.

This card defines the bounded future implementation task needed for independent
hostile re-audit before any ACP-BV 001B source or test work.

This current card does not implement ACP-BV 001B.

## Stage / Layer

Current stage/layer for this card: mechanism-hypothesis / engineering-
governance implementation-task-card revision only.

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
  re-audit;
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
consistency and flip the replay verdict. If replay/recomputation is operational
and lacks a paired fail-ability control, if the control is not executed, or if
`actual_flip != predeclared_expected_flip`, the future verdict must be:

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

Leakage scans must include the eight positive-control classes plus at least two
structural variants per leakage class. At least one structural variant per class
must be generated at runtime or held out from scanner construction, and its
generated names/identifiers must be disjoint from scanner source string
literals.

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
- `blocked_by_factorized_lookup_equivalence`
- `blocked_by_candidate_truth_coupling`
- `blocked_by_insufficient_heldout_novelty`
- `blocked_by_insufficient_distribution_capacity`
- `blocked_by_lookup_complete_distribution`
- `blocked_by_non_discriminative_distribution`
- `blocked_by_unsolvable_or_leaky_distribution`
- `blocked_by_leaking_oracle_invalidity`
- `blocked_by_non_fail_able_detector`
- `blocked_by_whitelist_leakage_scanner`
- `blocked_by_weak_computed_evidence_gate`
- `blocked_by_missing_callable_provenance`
- `blocked_by_source_boundary_failure`
- `blocked_by_replay_recomputation_failure`
- `blocked_by_static_or_literal_verdict`
- `blocked_by_malformed_artifact`
- `blocked_by_missing_required_artifact`
- `blocked_by_unstable_or_noise_level_effect`
- `blocked_by_solvability_preflight_failure`
- `blocked_by_anti_zeno_gap`
- `blocked_by_scope_creep`
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
- all operational detectors have paired fail-ability controls and every paired
  control satisfies `actual_flip == predeclared_expected_flip`;
- the leakage scanner detects structural runtime/held-out variants of all eight
  positive-control classes after scanner source string-literal disjointness is
  proven;
- per-seed episode count, multi-seed stability, dispersion, and uncertainty
  gates satisfy this card;
- replay recomputation and its negative control pass;
- no second logic path bypasses the evidence path.

Any terminal 001B distribution/surface collapse is the second collapse for the
current ACP-BV surface family after 001A and must route to:

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

For every operational detector, the future implementation must predeclare:

- detector name;
- expected intervention;
- expected verdict before intervention;
- expected verdict after intervention;
- expected flip direction;
- producer_function;
- input fixture/episode IDs;
- run_id;
- seed;
- source path;
- code path hash;
- artifact path.

Each paired control must inject a concrete intervention expected to flip the
corresponding verdict. The future implementation must actually run the control,
record expected-vs-actual flip, assert the expected flip, and block on
divergence.

Mandatory rule:

If `actual_flip != predeclared_expected_flip` for any operational detector, the
future implementation verdict must be:

```text
blocked_by_non_fail_able_detector
```

No warning-only, caveat-only, partial-pass, or "recorded but continue" behavior
is allowed.

If any detector lacks the paired control, or if the control is not executed, the
future implementation verdict must also be:

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

For each class, the future implementation must include at least two structural variants per leakage class.
At least one variant per leakage class must be generated at runtime or held out
from scanner construction.

The runtime/held-out variant must have generated names/identifiers that are
disjoint from scanner source string literals.

The future implementation must include a scanner-literal audit:

- extract scanner source string literals from
  `src/acp_bv_distribution_harness_001b/leakage_scanner.py`;
- record the generated runtime/held-out leakage identifiers;
- prove no generated runtime/held-out identifier appears as a scanner source
  string literal;
- then run the leakage scanner and require structural detection of the
  runtime/held-out variant.

Mandatory rule:

If the scanner detects only the original named fixture or the single
predeclared variant but misses the runtime/held-out structural variant, the
verdict must be:

```text
blocked_by_whitelist_leakage_scanner
```

If the generated runtime/held-out identifier appears in scanner source literals,
the verdict must be:

```text
blocked_by_whitelist_leakage_scanner
```

If the scanner result is justified only by method statements such as
"structural detection was used" without the literal-disjointness audit and
runtime/held-out probe result, the verdict must be:

```text
blocked_by_whitelist_leakage_scanner
```

## Hard Binding 3 - Per-Seed Episode Floor

The future implementation must use at least:

```text
128 heldout evaluation episodes per seed
```

across the five required seeds:

```text
[1009, 2027, 3037, 4049, 5051]
```

If the generator cannot produce at least 128 heldout evaluation episodes per
seed while satisfying the novelty and factorization constraints, the verdict
must be:

```text
blocked_by_insufficient_distribution_capacity
```

If fewer than 128 heldout evaluation episodes per seed are used without a
separately audited card revision, the verdict must be:

```text
inconclusive
```

or:

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

## Hard Binding 5 - Restated Novelty Floor

The future implementation must satisfy and report all novelty-floor values:

- `unseen_heldout_ratio >= 0.40`;
- `unseen_heldout_count >= max(8, ceil(0.40 * heldout_count))`;
- every predeclared factorization family must have at least `0.25` of heldout
  episodes containing unseen components;
- lookup-complete heldout episodes must be `<= 0.75`.

Violation of these values must force:

```text
blocked_by_insufficient_heldout_novelty
```

or, if lookup-complete factorization is discovered:

```text
blocked_by_factorized_lookup_equivalence
```

## Hard Binding 6 - Multi-Seed Stability

The future implementation must run the five required seeds:

```text
[1009, 2027, 3037, 4049, 5051]
```

and must report:

- per-seed candidate score;
- per-seed strongest fair baseline score;
- per-seed delta;
- per-seed B3 classification;
- mean delta;
- median delta;
- standard deviation or equivalent dispersion;
- bootstrap CI or equivalent uncertainty estimate;
- whether at least `4/5` seeds exit baseline-equivalence classification;
- whether any seed is classified as baseline-equivalent;
- whether the dispersion/CI lower bound exits the equivalence band.

Mechanism-relevant effect candidate status requires:

- at least `4/5` seeds outside baseline-equivalence classification;
- no seed classified as baseline-equivalent;
- dispersion/CI lower bound exits the equivalence band.

If this is not satisfied, the verdict must be:

```text
blocked_by_unstable_or_noise_level_effect
```

or:

```text
inconclusive
```

## Hard Binding 7 - Shared Helper Candidate/Truth Decoupling

The future implementation must include candidate/truth decoupling analysis over
shared helpers.

If candidate and truth share answer-bearing helper code, reference tables,
generated labels, hidden keys, or oracle-like scaffolding, the verdict must be:

```text
blocked_by_candidate_truth_coupling
```

## Hard Binding 8 - Solvability Without Leaking Oracle

The future implementation must require the solvability preflight to distinguish
legal solvability from leaking-oracle solvability.

If solvability depends on hidden truth labels, answer-bearing metadata, future
observations, candidate-authored aliases, or other illegal fields, the verdict
must be:

```text
blocked_by_leaking_oracle_invalidity
```

or:

```text
blocked_by_unsolvable_or_leaky_distribution
```

## Anti-Zeno Classification Closure

The future implementation must classify failure verdicts into one of two
families:

### A. Terminal Distribution/Surface Collapse

Terminal distribution/surface collapse must force:

```text
close_or_downgrade_current_acp_bv_surface_family
```

and must forbid 001C/001D repair attempts.

Terminal collapse verdicts include at minimum:

- `blocked_by_baseline_equivalence`;
- `blocked_by_factorized_lookup_equivalence`;
- `blocked_by_candidate_truth_coupling`;
- `blocked_by_insufficient_heldout_novelty`;
- `blocked_by_unsolvable_or_leaky_distribution`;
- `blocked_by_leaking_oracle_invalidity`;
- `blocked_by_non_discriminative_distribution`;
- `blocked_by_lookup_complete_distribution`;
- any strongest fair baseline tying the candidate under B3 bands;
- any renamed/factored/thin-tail recurrence of 001A baseline-equivalence.

For terminal distribution/surface collapse, the future implementation must
write a closure/downgrade artifact under:

```text
artifacts/acp_bv_001b_collapse_closure_001a/result.json
```

or a path matching:

```text
artifacts/acp_bv_001b_collapse_closure_*/result.json
```

The closure artifact must include:

- collapse trigger;
- detector output;
- producer_function;
- source path;
- run_id;
- seed/context/episode IDs;
- strongest baseline;
- candidate score;
- baseline score;
- B3 classification;
- reason;
- claim ceiling;
- next route;
- explicit statement that 001A was the first collapse and 001B is the second
  collapse.

### B. Repairable Harness-Integrity Failure

Repairable harness-integrity failures may be repaired only inside the already
authorized 001B implementation-card scope and may not be cited as mechanism,
harness, Gate, or surface evidence while unresolved.

Repairable harness-integrity verdicts include:

- `blocked_by_non_fail_able_detector`;
- `blocked_by_whitelist_leakage_scanner`;
- `blocked_by_weak_computed_evidence_gate`;
- `blocked_by_missing_callable_provenance`;
- `blocked_by_source_boundary_failure`;
- `blocked_by_replay_recomputation_failure`;
- `blocked_by_static_or_literal_verdict`;
- `blocked_by_malformed_artifact`;
- `blocked_by_missing_required_artifact`.

Mandatory anti-pass-shaped rule:

A repairable harness-integrity failure must not be used to redesign the
distribution into a pass-shaped surface.

A repairable harness-integrity fix must rerun the same predeclared distribution
constraints and detectors after repair.

If, after repairing a harness-integrity issue, a terminal
distribution/surface collapse appears, it still counts as the 001B second
collapse and must force closure/downgrade.

If a repair changes the distribution, baseline matrix, B3 bands, novelty floor,
detector definitions, or candidate/truth boundary in a way that weakens the
revised 001B spec, the result must be:

```text
blocked_by_anti_zeno_gap
```

or:

```text
blocked_by_scope_creep
```

## Revised 001B Spec Constraints To Carry Forward

The future implementation must carry forward:

- true heldout generalization;
- `unseen_heldout_ratio >= 0.40`;
- `unseen_heldout_count >= max(8, ceil(0.40 * heldout_count))`;
- every predeclared factorization family has at least `0.25` of heldout
  episodes containing unseen components;
- lookup-complete heldout episodes are `<= 0.75`;
- fair full-access lookup from the start;
- strongest-baseline selection after execution using deterministic
  `argmax(score)` with tie handling preserving the most damaging fair baseline;
- B3 bands with no post-hoc threshold tuning;
- candidate/truth decoupling, including shared-helper analysis;
- solvability preflight that distinguishes legal solvability from
  leaking-oracle solvability;
- no candidate-authored truth;
- memory resistance beyond exact-key lookup;
- source-boundary/source-pin carryover from 001A;
- five-seed stability over `[1009, 2027, 3037, 4049, 5051]`;
- at least 128 heldout evaluation episodes per seed;
- detector fail-ability with record + assert + block-on-divergence semantics;
- leakage scanner runtime/held-out variant and scanner source string-literal
  disjointness audit;
- Anti-Zeno one-redesign rule: 001A is the first collapse, and any terminal
  001B distribution/surface collapse is the second collapse requiring
  closure/downgrade of the current ACP-BV surface family.

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
- `artifacts/acp_bv_001b_collapse_closure_001a/**` or
  `artifacts/acp_bv_001b_collapse_closure_*/**`, only when terminal
  distribution/surface collapse is triggered.

This current revision task must not create those files.

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

## Current Revision Task Scope

This current revision task may change only:

- `docs/research/ACP-BV-001B-IMPLEMENTATION-TASK-CARD-001A.md`;
- `docs/research/ACP-BV-001B-IMPLEMENTATION-TASK-CARD-001A-CLAUDE-AUDIT-001A.md`;
- `artifacts/acp_bv_001b_implementation_task_card_001a_revision_001a/**`.

This current revision task must not create or modify:

- `src/**`;
- `tests/**`;
- any Gate runner;
- any bridge/admission/runtime/mainline/scheduler/live file;
- any real Gate target artifact;
- ACP-BV 001A repair files;
- ACP-BV 001B implementation files.

## Auto-Remote-Anchor Policy For Current Revision

Auto-Remote-Anchor decision for this current revision task: conditional.

Remote anchor is allowed only if:

- verdict is
  `acp_bv_001b_implementation_task_card_001a_revision_001a_ready_for_independent_reaudit`;
- changed files are limited to the current revision allowlist;
- no `src/**` or `tests/**` changed;
- no Gate/bridge/admission/runtime/mainline/scheduler/live files changed;
- JSON artifacts parse successfully;
- validation confirms Required Revisions #1-#3 and #4 hardening are present;
- local commit hash is recorded;
- worktree and index are clean after commit;
- local HEAD equals remote branch, local tag, and remote tag after push;
- no unresolved stop condition remains.

Suggested tag name:

```text
remote-anchor-acp-bv-001b-implementation-task-card-revision-001a-<shortsha>
```

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

Auto anchor must remain forbidden for the future implementation while the
revised implementation task card is pending independent hostile re-audit.

## Claim Ceiling

Future implementation maximum claim if all gates pass:

```text
bounded offline ACP-BV 001B mechanism-relevant effect candidate under the stated distribution and controls
```

Current card maximum claim:

```text
ACP-BV 001B implementation-task-card revision and hostile-audit preservation only
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
- omits the novelty-floor values in Hard Binding 5;
- omits the multi-seed stability rule in Hard Binding 6;
- omits shared-helper candidate/truth decoupling in Hard Binding 7;
- omits legal-solvability versus leaking-oracle separation in Hard Binding 8;
- weakens the revised 001B spec constraints;
- authorizes or touches mainline/runtime/bridge/admission/Gate paths;
- uses candidate-authored truth;
- uses static verdicts or literal scores;
- tunes thresholds after seeing results;
- allows a non-fail-able detector to carry the verdict;
- records `actual_flip != predeclared_expected_flip` without blocking;
- allows whitelist-only leakage scanning;
- validates leakage scanning using only one predeclared renamed variant per
  leakage class;
- omits runtime/held-out leakage variants;
- omits scanner source string-literal disjointness audit;
- fails to classify terminal collapse versus repairable harness-integrity
  failure;
- allows a repairable harness-integrity failure to become pass-shaped mechanism
  evidence;
- treats 001B collapse as authorization for 001C/001D repair.

Stop and return a blocked verdict if this current revision task:

- cannot verify the start HEAD/tag;
- leaves detector flip divergence as warning-only or record-only;
- leaves leakage scanner validation dependent on one predeclared renamed
  variant per class;
- omits runtime/held-out leakage variants;
- omits scanner source string-literal disjointness audit;
- omits terminal-collapse versus repairable-harness classification;
- authorizes ACP-BV 001B implementation;
- changes `src/**` or `tests/**`;
- changes any Gate/bridge/admission/runtime/mainline/scheduler/live path;
- creates malformed JSON artifacts;
- weakens the revised 001B spec;
- claims ACP-BV, mechanism, harness, Gate, admission, bridge, runtime, mainline,
  agency, consciousness, emotion, autonomy, stable user benefit, or EGO
  readiness.

## Rollback Plan

If future implementation touches forbidden files, revert them before reporting.

If future implementation code or tests are created outside the allowlist, delete
or revert them and report `blocked_by_scope_creep`.

If required detector fail-ability or leakage non-whitelist bindings cannot be
implemented unambiguously, preserve a blocker artifact rather than a pass-shaped
result.

If this current revision task touches forbidden files, revert only the
forbidden files created or modified by this task and return
`blocked_by_forbidden_file_change`.
