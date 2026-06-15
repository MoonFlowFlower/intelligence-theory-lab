# ACP-BV Executable Harness 001A Task Card

Task id: `ACP-BV-EXECUTABLE-HARNESS-001A`

Status: draft ready for independent review only. This card must not be executed
until independent review accepts it.

No harness implementation before independent review of the card.

Auto-Remote-Anchor: forbidden.

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

Any changed band values must be justified before candidate evaluation using an
independent baseline-derived rule. Baseline equivalence must be classified as
`baseline_equivalent`, not pass.

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

## B4 - Source-Hash Provenance

The future harness must record source-hash provenance for each code path below.

| Component | Required provenance fields |
| --- | --- |
| scorer | callable path, source path, code path hash, repo-source-owned true/false |
| environment generator | callable path, source path, code path hash, repo-source-owned true/false |
| held-out/counterfactual truth generator | callable path, source path, code path hash, repo-source-owned true/false |
| leakage scanner | callable path, source path, code path hash, repo-source-owned true/false |
| graph-cache challengers | callable path, source path, code path hash, repo-source-owned true/false |
| replay recomputation function | callable path, source path, code path hash, repo-source-owned true/false |
| ablation runner | callable path, source path, code path hash, repo-source-owned true/false |

All reported scores must also record producer_function, input artifacts, run_id,
seed/context/episode IDs, aggregation rule, and code path hash.

Static verdict dictionaries, pass-shaped JSON reports, and report-only rows are
not admissible score producers.

## B5 - Candidate-Inaccessible Environment And Challenger Generators

Environment generator code, challenger generator code, truth generator code, and
metric producer code must be:

- repo-source-owned;
- candidate-inaccessible;
- outside candidate output/artifact directories;
- not selected by the candidate;
- not influenced by candidate-authored serialized state, policy_map, labels,
  logits, confidence, score, verdict, or producer_function.

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
- environment/challenger/truth generators are repo-source-owned and
  candidate-inaccessible;
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
- environment/challenger/truth generators are candidate-accessible or
  candidate-influenced;
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
