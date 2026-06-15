# ACP-BV Executable Harness 001A Task Card

Task id: `ACP-BV-EXECUTABLE-HARNESS-001A`

Status: R1 revised after independent card-level audit; ready for targeted
independent re-audit only. This card must not be executed until independent
review accepts this revised card.

No harness implementation before independent re-audit of the revised card.

Auto-Remote-Anchor: forbidden.

R1 audit preservation: the independent card-level audit requiring this revision
is preserved at
`docs/research/ACP-BV-EXECUTABLE-HARNESS-001A-CARD-CLAUDE-AUDIT-001A.md`.
The preserved audit verdict is
`requires_card_revision_before_implementation`.

## Problem Definition

Draft a future executable harness for ACP-BV that can test whether an
action-conditioned predictive boundary/viability candidate survives
harness-owned truth, graph-cache challengers, held-out replay, real leakage
controls, action-difficulty controls, ablations, and source-provenance gates.

This card does not authorize implementation, source creation, test creation,
candidate creation, Gate rerun, admission, bridge, runtime, companion, or EGO
mainline work before independent review.

## Stage / Layer

Current stage/layer: engineering-governance / future executable harness task
card only, mechanism-hypothesis testing boundary not yet executed.

Mainline target: none.

Enabled-state requirement: no enabled path until a separate reviewer accepts
this card and a later bounded implementation task explicitly names allowed
source, test, and artifact paths.

Real-trigger evidence requirement:

- start only from anchored ACP-BV 001B revision
  `d8cf5bbf2fdd9895da03d3d382f6f1e0517f2226`;
- preserve tag
  `remote-anchor-acp-bv-surface-spec-001b-independent-audit-revision-001a-d8cf5bb`;
- cite the preservation record
  `docs/research/ACP-BV-SURFACE-SPEC-001B-REAUDIT-001A.md`;
- cite source artifacts under
  `artifacts/acp_bv_surface_spec_001b_independent_audit_revision_001a/`;
- cite prior negative evidence listed in this card;
- cite the preserved R1 card-level audit before implementation;
- do not execute if current HEAD, local tag, remote branch, or remote tag has
  drifted from the intended start boundary unless a new review explicitly
  revalidates the card.

## Hypothesis

ACP-BV has a mechanism-relevant signal only if a candidate beats independent
graph-cache and static/action-difficulty challengers by a predeclared margin on
harness-selected, held-out, candidate-inaccessible boundary/viability targets
while surviving real leakage, replay recomputation, source-provenance, and
ablation controls.

## Strongest Baselines

The harness must run baselines through the same harness-owned scorer and metric
producer path as the candidate. Baseline outputs must not be inserted as metric
rows or hand-written into reports.

Required graph-cache challengers:

- `transition_table`;
- `successor_map`;
- `count_table`;
- `episodic_traversal`;
- `fsm_planner`;
- `graph_lookup`, if retained by the implementation surface.

Additional required baselines:

- random / majority;
- observation-only predictor;
- action-independent predictor;
- static-action / no-action baseline;
- boundary-blind viability predictor;
- nearest-neighbor or lookup baseline;
- replay-hash-only payload;
- candidate-authored self-consistency payload;
- post-hoc classifier baseline, if any learned classifier is introduced.

Baseline matrix with local equivalence bands:

| Baseline or challenger | Required inputs | Equivalence rule | Required classification |
| --- | --- | --- | --- |
| `transition_table` | public observation/action/context keys plus training transitions | absolute normalized delta `< 0.02` | `baseline_equivalent`, not pass |
| `successor_map` | public state key, candidate-visible action, observed successor relation | absolute normalized delta `< 0.02` | `baseline_equivalent`, not pass |
| `count_table` | public observation/action buckets and training counts | absolute normalized delta `< 0.02` | `baseline_equivalent`, not pass |
| `episodic_traversal` | candidate-visible traces and training episode sequence | absolute normalized delta `< 0.02` | `baseline_equivalent` or `lookup_table_replay_leakage`, not pass |
| `fsm_planner` | public state abstraction, action set, repo-owned planner | absolute normalized delta `< 0.02` | `baseline_equivalent`, not pass |
| `graph_lookup` | public graph keys and candidate-visible history | absolute normalized delta `< 0.02` | `baseline_equivalent`, not pass |
| static-action / no-action | harness-owned action schedule | absolute normalized delta `< 0.02` | `baseline_equivalent`, not pass |
| observation-only | public observations only | absolute normalized delta `< 0.02` | `baseline_equivalent`, not pass |
| action-independent | observations with action shuffled or removed | absolute normalized delta `< 0.02` | `baseline_equivalent`, not pass |
| replay-hash-only | stored state/hash without recomputation | any non-recomputed replay success | block |
| candidate-authored self-consistency | candidate-authored labels, scores, verdicts, policy_map, or expected values | any score influence | block |

Equivalence band: `< 0.02`.

Inconclusive band: `[0.02, 0.05)`.

Minimum mechanism-relevant effect: `>= 0.05`.

The `<0.02`, `[0.02, 0.05)`, and `>=0.05` band values are immutable by
default. Any future change to these bands must be generated before candidate
scoring by repo-owned code from a recorded baseline-error distribution and must
record:

- producer function;
- source hash;
- seed;
- baseline distribution input;
- generated thresholds;
- artifact path.

Post-hoc threshold changes after seeing candidate score are forbidden. Baseline
equivalence must be classified as `baseline_equivalent`, not pass.

## B1 - Counterfactual Action And Difficulty Control

Hard requirement: `harness_selected_counterfactual_action_queries` are
mandatory.

A fixed action set alone is insufficient. The harness must include
harness-selected counterfactual action probes in which the candidate must score
on actions it did not choose.

The implementation must include an independent difficulty source, such as:

- graph-cache/static challenger error profile computed before candidate
  evaluation; or
- repo-source-owned environment difficulty metadata generated outside candidate
  outputs.

The difficulty normalization function must be predeclared before candidate
evaluation. It must use harness-owned or repo-source-owned values only.

Forbidden difficulty sources:

- candidate error;
- candidate logits;
- candidate confidence;
- candidate-authored difficulty;
- candidate-selected cases;
- candidate-declared expected values;
- candidate-authored serialized state, labels, score, verdict, or
  producer_function.

Required positive control: an action-as-difficulty payload where a candidate
succeeds on self-selected easy actions but fails or becomes equivalent under
harness-selected counterfactual action probes.

## B2 - Real Control Execution, No Self-Reported Booleans

The future harness task must execute and persist artifacts for:

- clean bundle expected to pass;
- dirty leakage payload expected to block;
- lookup-table replay payload expected to block on held-out/unseen context;
- counterfactual-action payload expected to expose easy-action selection;
- graph-cache baseline comparators;
- replay hash-only payload expected to block.

Each control artifact must record:

- command;
- run_id;
- seed/context/episode IDs;
- input hashes;
- output hashes;
- callable path;
- code path hash;
- block reason;
- clean pass result.

Self-reported booleans such as `command_readback_passed: true`,
`acceptance_gates: true`, or candidate-declared pass flags cannot be
load-bearing evidence. The harness must derive control pass/block status from
callable execution artifacts.

## B3 - Baseline Equivalence Band

The baseline matrix in this card is load-bearing and must be copied into the
future implementation artifact schema.

Rules:

- equivalence band `< 0.02`;
- inconclusive band `[0.02, 0.05)`;
- minimum mechanism-relevant effect `>= 0.05`;
- `baseline_equivalent` is a blocking or downgrade classification, not pass;
- inconclusive results block admission rather than permitting post-hoc
  threshold tuning.

## B4 - Source-Hash Provenance And Derived Source Boundary

The future harness must include a repo-owned callable source-boundary verifier
named `verify_callable_source_boundary`.

The verifier must derive source ownership and candidate-inaccessibility for
every load-bearing callable. It must not accept self-declared fields such as:

- `repo_source_owned: true`;
- `candidate_inaccessible: true`;
- `trusted_source: true`;
- `source_owned_by_harness: true`;
- any equivalent static or candidate-authored declaration.

The verifier must cover all load-bearing callable components:

- scorer;
- environment generator;
- held-out truth generator;
- counterfactual truth generator;
- leakage scanner;
- graph-cache challengers;
- replay recomputation function;
- ablation runner;
- baseline runner;
- metric aggregator;
- admission/verdict classifier, if any.

The future implementation must explicitly define all source-boundary inputs
before candidate scoring:

1. repo-owned source roots;
2. candidate-writable roots;
3. candidate artifact roots;
4. generated-output roots;
5. import/load resolution rules;
6. symlink and realpath handling;
7. environment-variable influence rules;
8. candidate config influence rules.

Path resolution must use canonical realpaths. String-prefix checks alone are
not sufficient.

The verifier must record these derived fields for every covered callable:

- `resolved_source_path`;
- `normalized_realpath`;
- `source_hash`;
- `repo_source_root_match`;
- `candidate_writable_root_match`;
- `candidate_artifact_root_match`;
- `candidate_config_influence_detected`;
- `candidate_serialized_state_influence_detected`;
- `candidate_policy_map_influence_detected`;
- `candidate_label_or_logit_influence_detected`;
- `repo_source_owned_derived`;
- `candidate_inaccessible_derived`;
- `boundary_verdict`.

The future harness must block unless all of the following are true:

- `repo_source_owned_derived == true`;
- `candidate_inaccessible_derived == true`;
- `candidate_writable_root_match == false`;
- `candidate_artifact_root_match == false`;
- no candidate-controlled config, serialized state, policy map, labels, logits,
  confidence, score, verdict, or producer function influences generator, truth,
  scorer, baseline, ablation, replay, leakage, metric, or verdict selection.

The verifier must block or explicitly test symlink escape, relative-path
escape, generated-code injection, candidate-selected import path, and
candidate-controlled environment variable influence.

Minimum required source-boundary controls:

1. A deliberately candidate-accessible environment or truth generator placed
   under a candidate artifact or candidate-writable path must be rejected.
2. A generator whose selection is influenced by candidate `policy_map` must be
   rejected.
3. A callable with valid source hash but wrong boundary ownership must be
   rejected.
4. A symlink or realpath escape from an allowed-looking path into a
   candidate-controlled path must be rejected. If the implementation
   environment cannot create symlinks, that limitation must be recorded and a
   substitute path-escape control must be used.

Each boundary-control artifact must persist:

- control name;
- injected violation;
- verifier entrypoint;
- resolved source path;
- source hash;
- expected block reason;
- actual block reason;
- run ID;
- artifact path.

A clean report without these boundary-negative controls is insufficient.

All reported scores must also record producer_function, input artifacts, run_id,
seed/context/episode IDs, aggregation rule, and code path hash.

Static verdict dictionaries, pass-shaped JSON reports, and report-only rows are
not admissible score producers.

## B5 - Candidate-Inaccessible Environment And Challenger Generators

Environment generator code, challenger generator code, truth generator code, and
metric producer code must be verified by `verify_callable_source_boundary` as:

- repo-source-owned;
- candidate-inaccessible;
- outside candidate output/artifact directories;
- not selected by the candidate;
- not influenced by candidate-authored serialized state, policy_map, labels,
  logits, confidence, score, verdict, or producer_function.

These properties must be derived verifier outputs, not self-declared fields.

No candidate-authored truth, no candidate-selected producer, no
candidate-declared expected values, no row injection into metric producers, and
no pass-shaped JSON reports are allowed.

## Ablations

The future harness must rerun episodes under real interventions. Required
ablations:

- remove action input;
- shuffle action labels;
- remove or replace boundary state;
- remove or replace viability state;
- freeze candidate update or state transition;
- use observation-only state;
- use no-action / no-transition control;
- delete or replace source memory / serialized state where lineage is claimed;
- disable replay recomputation and require block;
- force graph-cache challengers through the same scorer.

Each ablation must predeclare metric direction, minimum effect criterion,
equivalence criterion, block condition, threshold source, and expected
mechanism-critical variable. No post-hoc threshold tuning is allowed.

Ablation must not be implemented as deleting, masking, or editing report
fields. Ablation must rerun episodes under real input or component intervention
and regenerate the full trace.

Each ablation artifact must persist:

- intervention target;
- rerun command;
- run ID;
- regenerated trace path;
- before/after metrics;
- effect size;
- threshold classification.

## Trace / Replay Plan

Replay must recompute candidate behavior from `serialized_state + observation`.
Hash comparison alone is insufficient.

The harness must include:

- held-out/unseen replay contexts unavailable at serialized-state time;
- harness-selected counterfactual action replay;
- lookup-table replay positive control;
- replay hash-only positive control;
- serialized state hash;
- observation hash;
- replay function source hash;
- recomputed candidate output hash;
- block reason if replay uses stored answers, stored hashes, or seen-context
  lookup.

Replay success on seen context may be recorded only as a positive-control
failure; it must not count as ACP-BV evidence.

## Leakage Controls

The harness must run real leakage clean/dirty controls.

Clean control must include legitimate raw candidate output without answer keys.

Dirty control must include at least one of each forbidden class:

- oracle label;
- hidden boundary;
- hidden viability;
- expected action;
- expected score;
- producer_function;
- pass verdict;
- answer-key alias.

The scanner must inspect nested fields, alias keys, path-like fields, string
values, and numeric values where applicable. A literal string self-test is not
sufficient.

Dirty-control injection must be repo-owned and vary across seeds or cases in at
least:

- alias/name;
- nested location;
- value encoding or representation.

A scanner that only recognizes a fixed injected field name is insufficient.

## Computed-Evidence Gate

No evidence-bearing result may be a literal, static verdict dictionary,
unconditional clean report, pass-shaped JSON report, or test that only asserts
pass.

Required computed evidence:

- candidate score from callable scorer;
- each baseline score from independent callable baseline/challenger;
- ablation scores from real reruns;
- leakage clean and dirty controls from scanner execution;
- replay from recomputation, not stored hashes;
- source-pin integrity for all code paths;
- no unused frozen seed, train context, held-out context, or counterfactual
  pair.

Any unused frozen seed, train context, held-out context, or counterfactual pair
blocks the evidence claim.

## Acceptance Gate

The future executable harness task must return exactly one:

- `acp_bv_executable_harness_001a_pass_bounded_surface_evidence`;
- `acp_bv_executable_harness_001a_baseline_equivalent`;
- `acp_bv_executable_harness_001a_blocked_by_action_difficulty`;
- `acp_bv_executable_harness_001a_blocked_by_leakage`;
- `acp_bv_executable_harness_001a_blocked_by_replay_lookup`;
- `acp_bv_executable_harness_001a_blocked_by_source_provenance`;
- `acp_bv_executable_harness_001a_blocked_by_self_declared_or_unverified_source_boundary`;
- `acp_bv_executable_harness_001a_blocked_by_candidate_accessible_truth_or_generator`;
- `acp_bv_executable_harness_001a_blocked_by_candidate_authored_truth`;
- `acp_bv_executable_harness_001a_blocked_by_missing_control_execution`;
- `acp_bv_executable_harness_001a_blocked_by_inconclusive_effect`;
- `acp_bv_executable_harness_001a_blocked_by_scope_or_claim_inflation`.

Pass is allowed only if all of the following are true:

- clean control passes by callable scanner execution;
- dirty control blocks by callable scanner execution;
- lookup-table replay blocks on held-out/unseen context;
- replay hash-only payload blocks;
- counterfactual-action payload exposes easy-action selection or the candidate
  remains above threshold after difficulty normalization;
- graph-cache challengers execute and do not match within `< 0.02`;
- candidate exceeds strongest baseline by `>= 0.05`;
- no result falls in `[0.02, 0.05)`;
- all ablations execute as real reruns;
- all source-hash provenance fields are present;
- `verify_callable_source_boundary` executes for every load-bearing callable;
- ownership and candidate-inaccessibility are derived from resolved source
  paths and explicit path-boundary rules, not declarations;
- boundary-negative controls reject candidate-accessible, candidate-influenced,
  wrong-boundary, and path-escape callables;
- environment/challenger/truth generators are derived repo-source-owned and
  derived candidate-inaccessible;
- no candidate-authored truth, no candidate-selected producer, no
  candidate-declared expected values, no row-injected metric, no static verdict
  dictionary, and no pass-shaped report is load-bearing.

## Claim Ceiling

ACP-BV executable harness bounded surface evidence only, if later executed and
passed under this card. No Gate validity, mechanism validity, admission
readiness, bridge readiness, runtime readiness, mainline effect, agency,
consciousness, emotion, autonomy, stable user benefit, or EGO readiness claim.

## Stop Condition

Stop if:

- this card is executed before independent review accepts it;
- implementation touches files outside the later authorized allowlist;
- a harness is implemented without B1-B5 as hard requirements;
- `harness_selected_counterfactual_action_queries` are optional;
- difficulty is defined by candidate error, logits, confidence, or authored
  difficulty;
- controls are self-reported booleans rather than real artifacts;
- baseline equivalence is reported as pass;
- source-hash provenance is missing for any required component;
- any load-bearing callable's repo ownership or candidate-inaccessibility is
  accepted from declaration rather than derived by
  `verify_callable_source_boundary` and validated by fail-able controls;
- environment generation, truth generation, counterfactual truth generation,
  scoring, leakage scanning, graph-cache challenger generation, replay
  recomputation, ablation running, metric aggregation, or verdict classification
  is candidate-accessible or candidate-influenced;
- replay uses stored hashes instead of recomputation;
- leakage scanner lacks real clean/dirty controls;
- row injection, static verdict dictionaries, pass-shaped JSON reports,
  candidate-authored truth, candidate-selected producers, or candidate-declared
  expected values affect scores;
- any frozen seed, train context, held-out context, or counterfactual pair is
  unused.

## Rollback Plan

If blocked, preserve a bounded blocker artifact in the task artifact directory,
leave source unchanged unless the later task card explicitly authorized
implementation files, and do not repair the result into pass.

## Expected Changed Files For A Future Implementation

This draft does not authorize these files yet. A later implementation task must
name an allowlist before editing.

Expected future paths may include:

- `src/acp_bv_executable_harness_001a/**`;
- `tests/test_acp_bv_executable_harness_001a*.py`;
- `artifacts/acp_bv_executable_harness_001a/**`.

## Forbidden Changes

Forbidden unless separately authorized by a reviewed task card:

- EGO mainline runtime;
- UI / companion behavior;
- relationship learning;
- emotion systems;
- proactive behavior;
- LLM integration;
- AIRI integration;
- deployment;
- API keys;
- global schema migrations;
- rewriting old artifacts;
- Gate3/Gate4 source or artifacts except read-only references;
- integrated admission / bridge / runtime / mainline files.

## Prior Negative Evidence To Cite Before Execution

The later implementation task must cite these before coding:

- `docs/NEGATIVE_EVIDENCE_LEDGER.md` lines 48-51:
  candidate-authored `policy_map` cannot control ground truth.
- `docs/NEGATIVE_EVIDENCE_LEDGER.md` lines 77-79:
  downgrade if no harness-owned / candidate-inaccessible truth source exists.
- `artifacts/CLAUDE-INDEPENDENT-GATE0-3-EVIDENCE-PROVENANCE-HOSTILE-AUDIT-001A/audit_result.json`:
  literal baseline/ablation and report-shaped evidence risks.
- `artifacts/preserve_claude_gate0_3_evidence_provenance_hostile_audit_001a_and_freeze_downstream_inheritance_001a/freeze_matrix.json`:
  frozen Gate1/Gate3/integrated-testbed inheritance unless callable reruns
  defeat controls.
- `artifacts/post_freeze_gate0_3_sequential_repair_queue_001a_gate1_failed_graph_cache_reconciliation/baseline_comparison.json`:
  graph-cache, transition-table, successor-map, count-table,
  episodic-traversal, and FSM/planner controls matched or beat prior candidate
  surfaces.
- `artifacts/gate_target_independent_ground_truth_preflight_001a/result.json`:
  ACP-BV had no executable target or independent truth fields before this card.

## What This Card Does Not Prove

This card does not prove ACP-BV, any Gate, mechanism validity, admission
readiness, bridge readiness, runtime readiness, mainline effect, agency,
consciousness, emotion, autonomy, stable user benefit, or EGO readiness.
