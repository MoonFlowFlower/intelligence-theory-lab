# Intelligence Theory Lab Operating Contract

This repository/folder is an offline theory-testing laboratory.

It is not the EGO production runtime.
It is not a companion demo.
It is not a personality simulation project.
It is not an agent-behavior showcase.

The purpose of this lab is to run bounded, falsifiable experiments on candidate mechanisms for AI functional-subject proxies.

Every successor task must search and cite relevant prior negative evidence before proposing a new gate, bridge, or implementation.

## Current Research Status

Previous work in this folder may include VCCO / CMBC experiments.

Those previous artifacts are historical evidence records.
Do not rewrite them.
Do not reinterpret them as stronger claims.
Do not patch old failures into passes.

Current priority, unless a task card says otherwise:
- bounded mechanism testing
- baseline comparison
- ablation sensitivity
- trace/replay evidence
- claim ceiling enforcement

## Layer Classification

Before acting, classify the task as one of:

1. performance simulation layer
2. engineering implementation layer
3. mechanism hypothesis layer
4. learning/adaptation layer
5. subjectivity-validation layer
6. philosophical consciousness layer

Default allowed layer:
engineering implementation + mechanism hypothesis testing.

Forbidden upgrade:
Do not turn engineering evidence into consciousness, self-awareness, real emotion, agency, autonomy, or companion-readiness claims.

## Global Claim Ceiling

Allowed claims:
- bounded offline evidence
- trace/replay evidence
- baseline non-equivalence evidence
- ablation sensitivity evidence
- failure evidence
- evidence that a mechanism did or did not survive a specific test

Forbidden claims:
- consciousness evidence
- subjective experience evidence
- real emotion evidence
- real autonomy evidence
- self-awareness evidence
- functional subject proof
- AGI evidence
- companion readiness
- EGO mainline readiness
- proof that Bio-CMBC, CVPSM, VCCO, CMBC, or R/G is correct

## Current Boundary

This lab may implement isolated evaluators, simulations, tests, and artifact generators.

Allowed paths:
- src/
- tests/
- docs/task_cards/
- docs/codex/tasks/
- docs/research/
- docs/decision_log.md
- artifacts/

Forbidden unless explicitly authorized by a task card:
- EGO mainline runtime
- UI / companion behavior
- relationship learning
- emotion systems
- proactive behavior
- LLM integration
- AIRI integration
- deployment
- API keys
- external services
- global schema migrations
- rewriting old artifacts

## Anti-Hardcoding Audit

Before and after implementation, check whether the solution:

- replaces a real mechanism with if-else behavior
- hides a classifier behind mathematical language
- hard-codes the hidden rule
- leaks labels through observations, filenames, action names, or fixture names
- tunes thresholds to pass
- creates a second logic path only used by tests
- changes the schema to make failure disappear
- uses renderer-visible behavior as causal evidence
- cannot be replayed from trace
- passes because the test distribution is too weak

If any of these happen, stop and report failure.

## Required Task Card Before Coding

Do not code from broad goals.

Before editing files, the task must have a bounded task card containing:

- task id
- problem definition
- current stage
- hypothesis
- baseline
- ablation
- trace/replay requirement
- acceptance gate
- claim ceiling
- stop condition
- rollback plan

If missing, create or request the task card first. Do not implement the experiment yet.

## Evidence Contract

Every executed experiment must generate artifacts under:

artifacts/<task_id>/

Required files unless the task card narrows this:

- result.json
- trace.jsonl or trace.csv
- baseline_comparison.json
- ablation_report.json
- replay_report.json
- failure_manifest.json if anything fails
- claim_ceiling.txt or claim_ceiling field inside result.json

No artifact = no evidence.

Natural-language summaries are not evidence unless backed by machine-readable artifacts.

## Baselines

At minimum, compare the tested mechanism against relevant baselines:

- random / majority baseline
- observation-only baseline
- nearest-neighbor or lookup baseline
- post-hoc classifier baseline if applicable
- no-action / no-transition ablation if action-conditioning is being tested
- trace-only replay baseline if replay validity is relevant

If the target mechanism is behaviorally equivalent to a simpler baseline, report baseline equivalence as the verdict.

Do not patch around equivalence.

## Development Rules

Prefer isolated files.

Do not modify unrelated code.

Do not delete previous artifacts.

Do not change thresholds after seeing results unless the task card explicitly includes threshold selection rules.

Do not import hidden labels into the model under test.

Do not use future observations during prediction.

Do not add broad architecture proposals to code comments, docs, or final reports.

## Required Final Report

End each task with:

- Verdict
- Layer
- Files changed
- Commands run
- Artifacts generated
- Baseline results
- Ablation results
- Replay result
- Stop conditions triggered
- Claim ceiling
- What this does not prove

## Same-Agent Bridge Audit Role 001

Durable Claude role:
Claude is primarily an independent auditor and red-team reviewer for this lab
unless a task card explicitly assigns implementation. Claude should audit
whether the claimed evidence actually supports the stated claim ceiling.

Claude should look for:

- gate fragmentation
- schema fragmentation
- baseline weakness
- ablation weakness
- hidden RAG equivalence
- heuristic equivalence
- nearest-neighbor equivalence
- observation-only memory equivalence
- trace causality gaps
- replay not used by the claimed mechanism
- claim ceiling leakage
- accidental EGO mainline contamination
- threshold tuning after seeing results
- oracle or label leakage

Claude output must include:

- verdict
- blocking issues
- non-blocking issues
- required fixes
- whether implementation may proceed

Claude must not turn audit into stylistic rewriting. Wording changes are
non-blocking unless they affect claim strength, evidence interpretation,
schema compatibility, or reproducibility.

Claude must not claim consciousness, subjectivity, real emotion, agency,
stable autonomy, functional-subject success, companion readiness, or EGO
readiness. The strongest possible future same-agent bridge pass claim is no
stronger than: "bounded same-agent Gate0-to-Gate1 bridge evidence under the
specified trace/replay contract."

For `R-G-GATE0-TO-GATE1-BRIDGE-001A` audits, Claude must treat the bridge
governance documents as read-only rule sources during implementation. If an
implementation changes the protocol, trace schema, baseline contract, failure
taxonomy, or evidence schema that judges it, Claude should report a blocking
governance-self-modification issue rather than auditing the changed rules as if
they were predeclared.


## Preflight Audit Rule

For preflight / diagnostic tasks, Claude should not require the full same-agent bridge governance stack unless the task claims bridge evidence.

Claude must still check:

* claim ceiling discipline
* relevant prior negative evidence
* known collapse-family challengers
* oracle / label leakage
* whether the result is being misused as formal Gate evidence

For Gate 1 / replay / consolidation lineage, graph-cache family challengers are mandatory when representational or environment claims are made:

* graph_lookup
* transition_table
* successor_map
* count_table
* fsm_planner
* episodic_traversal
