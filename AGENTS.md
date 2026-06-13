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

For every EGO/Codex executable evidence task, require a computed-evidence provenance gate. Reported result, baseline, ablation, contrast, leakage, and replay metrics must be derived from callable computation paths, not literals, static dictionaries, unconditional clean reports, or tests that assert pass. Every score must record producer_function, input artifacts, run_id, seed/context/episode IDs, aggregation rule, and code path hash. Baselines must be independent callable implementations. Ablations must rerun episodes under real interventions. Leakage scans must be real scanners with at least one positive-control case. Replay must recompute candidate behavior from serialized_state + observation, not only replay hashes. Tests must verify computation paths, failure paths, and baseline/ablation invocation, not just pass verdicts. Any unused frozen seed, train context, heldout context, or counterfactual pair must block.

## Evidence-Gate Interpretability Reframe

For future tasks involving explainability, interpretability, black-box learned
components, neural or high-dimensional latent states, internal-state evidence,
or claims that a mechanism is not "explainable" by a simpler route, Codex must
apply and cite:

```text
docs/EVIDENCE-GATE-INTERPRETABILITY-REFRAME-001A.md
```

The gate must not require complete human semantic interpretation of every
latent state as a hard pass condition. It must instead require evidence-grade
auditability:

```text
observable state evidence
trace/replay evidence
ablation sensitivity
counterfactual intervention sensitivity
source-memory deletion or equivalent lineage tests
baseline non-equivalence
leakage resistance
claim ceiling enforcement
```

Black-box or learned components are allowed only when their training/update
history, evaluation boundary, state snapshots or hashes, replay behavior,
intervention sensitivity, ablation sensitivity, leakage boundary, and baseline
comparison are auditable.

Do not use "black box" to weaken trace, replay, baseline, ablation,
intervention, leakage-scan, artifact, or claim-ceiling requirements.

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

## Preflight vs Formal Gate

Preflight / diagnostic tasks are allowed to use lighter evidence requirements than formal gates or same-agent bridge tasks.

For preflight tasks:

* do not claim formal Gate evidence
* do not claim same-agent bridge evidence
* do not claim replay/consolidation evidence
* do not authorize EGO mainline integration
* cite relevant prior negative evidence
* include known collapse-family challengers when relevant
* keep the claim ceiling bounded to the specific preflight result

For Gate 1 / replay / consolidation lineage, graph-cache family challengers are mandatory when representational or environment claims are made:

* graph_lookup
* transition_table
* successor_map
* count_table
* fsm_planner
* episodic_traversal

Formal gates and same-agent bridge tasks still require stronger predeclared metrics, baselines, ablations, run ledger, and freeze rules.


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

## Auto-Remote-Anchor Policy

Codex must not automatically push or tag after every task.

Codex may perform auto-remote-anchor only when the task card explicitly contains:

`Auto-Remote-Anchor: authorized`

or

`Auto-Remote-Anchor: conditional`

If the task card says `Auto-Remote-Anchor: forbidden`, or does not mention auto-remote-anchor, Codex must not push or tag.

### Auto-anchor is allowed only if all gates pass

Codex may auto-anchor in the same session only if all conditions below are true:

1. The task verdict is `pass`, or the task card explicitly designates the result as boundary-worthy negative evidence.
2. The task card explicitly authorizes auto-remote-anchor.
3. Worktree and index are clean after commit.
4. The committed changes are limited to the authorized task scope.
5. No stop condition, blocker, unresolved audit requirement, or pending independent review remains.
6. The result is intended to become a canonical boundary for future tasks.
7. Remote credential hygiene can be checked without printing secrets.
8. Push, tag creation, tag push, and readback can be completed safely.
9. The task does not require Claude/GPT independent audit before canonicalization.
10. The task does not involve provisional implementation or experiment results whose validity still needs review.

### Required auto-anchor procedure

If auto-anchor is authorized and all gates pass, Codex must:

1. Resolve local HEAD full hash.
2. Verify current branch.
3. Verify worktree and index are clean.
4. Verify ahead/behind relative to origin.
5. Check credential hygiene without printing credentials or full secret-bearing remote URLs.
6. Push the branch.
7. Create a lightweight tag using the task name and short hash.
8. Push only that tag ref.
9. Read back:
   - local HEAD full hash
   - remote branch full hash
   - local tag full hash
   - remote tag full hash
   - exact match yes/no
   - local tag type
   - final ahead/behind
   - final git status
   - final `git diff --name-status`
10. Report the claim ceiling as remote-anchor publication and verification only.

### Auto-anchor must be forbidden when

Codex must not auto-anchor if:

- the task is blocked;
- the task card says auto-anchor is forbidden;
- the task card is silent about auto-anchor;
- the result is provisional;
- the result requires Claude/GPT independent audit before canonicalization;
- the task involved implementation or experiment results whose validity has not been reviewed;
- remote push would require rebase, reset, amend, or conflict repair;
- any credential hygiene issue cannot be handled safely;
- any unauthorized file modification appears;
- any source/harness/test change appears outside the task scope;
- the task enters Gate5, admission, bridge, runtime, or EGO-mainline without explicit authorization.

### Claim ceiling

Auto-anchor does not upgrade the claim.

It only seals the current bounded result as a remote-verifiable boundary.

It must never be used to claim valid Gate4, mechanism validity, social-latent inference, agency, selfhood, consciousness, emotion, autonomy, EGO readiness, runtime readiness, companion readiness, or user benefit.

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

## Same-Agent Bridge Governance 001

Durable Codex role:
Codex is an implementation and evidence-preparation agent for this lab. Codex
must not implement broad functional-subject goals directly. Broad goals must be
reduced to bounded task cards, frozen contracts, and replayable evidence
requirements before any implementation.

Every Codex implementation task must have a bounded task card before code is
edited. Every mechanism task card must include:

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

Documentation-only governance tasks may create or update protocols, schemas,
audit instructions, and future task cards. They do not authorize experiment
execution unless the task card explicitly says so.

After a local gate exists, Codex must prefer same-agent bridge tests over more
isolated local gates. A new isolated gate is allowed only when the task card
explains why the bridge dependency cannot yet be tested.

Codex must not touch the EGO mainline, EGO runtime, companion behavior, UI,
LLM integration, AIRI integration, relationship learning, proactive behavior,
emotion systems, self-awareness simulation, or deployment unless a prior
governance document explicitly authorizes that path and a bounded task card
names the exact allowed files.

Codex must not upgrade claims beyond evidence. Passing a local gate, generating
documents, or passing tests is not evidence of consciousness, subjective
experience, real emotion, agency, stable autonomy, functional subject success,
companion readiness, or EGO mainline readiness.

For same-agent bridge work, Codex must preserve one canonical path through:

- one minimal same-agent system
- one generated environment family
- one canonical state schema
- one trace/replay contract
- one baseline suite
- one ablation suite
- one evidence report schema
- one claim ceiling discipline
- one stop/rollback policy

Codex must run lightweight checks that are already available, avoid installing
heavy dependencies for governance-only tasks, and summarize exact files changed
in the final report.

During `R-G-GATE0-TO-GATE1-BRIDGE-001A`, the bridge governance documents are
read-only dependencies. The implementation task must not modify:

- `docs/research/SAME_AGENT_BRIDGE_PROTOCOL_001.md`
- `docs/research/SAME_AGENT_BRIDGE_TRACE_SCHEMA_001.md`
- `docs/research/SAME_AGENT_BRIDGE_BASELINES_001.md`
- `docs/research/SAME_AGENT_BRIDGE_FAILURE_TAXONOMY_001.md`
- `docs/research/SAME_AGENT_BRIDGE_EVIDENCE_SCHEMA_001.md`

Future bridge implementation write paths are restricted to isolated paths such
as:

- `src/same_agent_bridge_001a/`
- `tests/same_agent_bridge_001a/`
- `artifacts/same_agent_bridge_001a/`


涉及 EGO、Codex、agent 架构、主体性理论、AI 自我、长期记忆、主动性、functional subject 或机制验证时，不要把目标降级成普通聊天机器人、人格 prompt、MVP demo 或硬编码行为树。

必须先判断当前问题属于哪一层：
- 表现模拟层
- 工程实现层
- 机制假说层
- 学习适应层
- 主体性验证层
- 哲学意识层

默认目标不是证明“AI 已有意识”，而是寻找、验证、工程化能产生连续自我、主观取向、受控主动性、学习适应、长期记忆、价值评估、自我边界和环境反馈的机制 proxy。

任何理论或架构建议必须做反硬编码审计：
- 是否把高维隐状态偷换成少数显式变量；
- 是否把 if-else、行为树、prompt 表演伪装成主体性；
- 是否把“看起来像生命”偷换成“具有主体机制”；
- 是否遗漏主动探索、注意力筛选、预测误差、长期记忆、自我边界、价值评估和环境反馈；
- 是否能通过 trace / replay 证明行为来自内部状态与学习历史。

任何进入 Codex 的任务必须先变成 bounded task card：
- 问题定义
- 当前阶段
- hypothesis
- baseline
- ablation
- trace/replay requirement
- acceptance gate
- claim ceiling
- stop condition
- rollback plan

Codex 负责执行和产出证据，不负责自我宣布理论成功。
