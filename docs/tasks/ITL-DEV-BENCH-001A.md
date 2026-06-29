# ITL-DEV-BENCH-001A - Developmental MicroWorld Benchmark / Replay Harness

## Task Card

Task id: ITL-DEV-BENCH-001A

Problem definition: Build an isolated, deterministic, Python developmental micro-world benchmark that tests whether a fixed prediction-action-feedback-update loop can be run across progressively changing task-family conditions. The first implementation creates the harness and audit surface only; it does not validate a mechanism.

Current stage / layer: benchmark design, engineering implementation, mechanism-hypothesis test harness, learning-adaptation candidate infrastructure.

Mainline target: isolated `itl_devbench` package, CLI matrix runner, replay checker, audit checker, machine-readable artifacts, and tests. This is not an EGO runtime or product mainline target.

Enabled-state requirement: smoke CLI must run from `python -m itl_devbench.eval.run_matrix --config configs/itl_devbench_001a.yaml --smoke` and generate a timestamped artifact directory plus `latest`.

Real-trigger evidence requirement: the runner must execute all required frozen baselines, all eight minimal-loop variants, stages 0-6, smoke seeds, and produce `trace.jsonl`, `manifest.json`, `metrics.json`, `baseline_scores.json`, `report.md`, `replay_report.json`, and `audit_report.json`.

Hypothesis: A deterministic benchmark scaffold with hidden dynamics, partial observability, delayed effects, rule shifts, frozen baselines, factorial candidate variants, event-hash traces, replay, and forbidden-claim audit can make later developmental-adaptation claims harder to fake.

Strongest baseline / shortcut explanation: graph-cache lookup, generic FSM, and observation-only control may match or beat minimal-loop variants under access parity; oracle provides headroom only and must be labeled separately.

Ablation requirement: run all factorial minimal-loop variants: `000`, `100`, `010`, `001`, `110`, `101`, `011`, `111`.

Trace/replay requirement: every event must record `pre_action_prediction` before `env.step(action)`, action, environment result, update diff, event index, and chained event hash. Replay must rerun the environment with the recorded config/seeds/actions and compare observations, rewards, done flags, info, event hashes, and metrics hash.

Computed-evidence provenance gate: reports derive labels from metrics/replay/audit outputs. Manifest records git commit, git status readback, config hash, source file hashes, seed list, command line, and Python version. Metrics derive from `trace.jsonl`.

Acceptance gate: smoke run completes; trace and manifest are emitted; untampered replay succeeds; tamper test fails; normal audit succeeds; forbidden-claim injection audit fails; pytest passes. Candidate outperformance is not required.

Claim ceiling: before artifacts, benchmark/harness implementation only with evidence unknown. After successful official run, replay, baseline matrix, and audit, at most bounded offline developmental-adaptation / predictive-update evidence under the specified trace/replay contract.

Stop condition: stop as `implementation_blocked_with_reason` if deterministic replay cannot be achieved, candidate requires hidden-state access, pre-action prediction cannot be recorded before environment stepping, baselines cannot run from one CLI, report verdict requires manual typing, or tamper tests cannot detect modification.

Rollback plan: remove only the isolated `docs/tasks/ITL-DEV-BENCH-001A.md`, `configs/itl_devbench_001a.yaml`, `src/itl_devbench/`, `tests/test_*devbench*`/requested devbench tests, and `artifacts/ITL-DEV-BENCH-001A/` paths created by this task. Do not alter existing historical artifacts.

Expected changed files: this task card, config, isolated package under `src/itl_devbench/`, requested tests, and `artifacts/ITL-DEV-BENCH-001A/` smoke outputs.

Forbidden changes: no EGO mainline runtime, UI, companion behavior, relationship learning, emotion systems, proactive behavior, LLM integration, AIRI integration, deployment, external service, global schema migration, old artifact rewrite, persona, chatbot, dialogue renderer, or Joi-like surface.

Auto-Remote-Anchor: forbidden.

## Bounded Audit Before Implementation

Real objective: create a reproducible, baseline-first, anti-self-report developmental benchmark scaffold, not a positive mechanism result.

Problem-definition risk: if the environment is too simple, frozen baselines may saturate it; that is acceptable negative evidence and should not be patched into a candidate win.

Strongest baseline explanation: a symbolic lookup or generic movement heuristic can solve many deterministic grid tasks without any meaningful predictive-update mechanism.

Strongest invalidity reason: if hidden rules leak through observation labels, filenames, action names, trace labels, or candidate access to debug state, the harness would only measure leakage.

Falsifier for current framing: replay mismatch, tamper-insensitive tests, missing baseline matrix, or a candidate implementation that needs hidden state.

Insufficient evidence: smoke completion alone; candidate reward above random alone; report text without machine-readable trace/manifest/replay/audit artifacts.

Mechanism vs resemblance: this task tests harness viability and produces candidate/baseline behavior traces. It does not validate learning, agency, subjectivity, or mechanism truth.

Risk checks:
- Hard-coding: avoid per-stage hand-tuned candidate logic and keep baselines labeled.
- Local optimum: do not optimize minimal-loop policy for a win.
- Zeno trap: do not repair environment thresholds after seeing scores to favor candidate.
- Evidence leakage: block hidden-state fields outside oracle/audit paths.
- Weak baseline: include random, observation-only, generic FSM, graph cache, and oracle.
- Schema split: use one trace schema across all agents.
- Second logic path: replay must recompute from trace/config/actions, not trust report labels.
- Replay weakness: compare observations, rewards, done/info, hashes, and metric hashes.
- Claim inflation: report only benchmark/candidate/baseline/ablation/replay/evidence-unknown wording.

Minimal validation: targeted pytest suite plus smoke run, replay CLI, audit CLI, and final status readback.

Acceptance signal: all acceptance-gate checks complete with generated artifacts under a timestamped run directory and `latest`.

## Collision Record

Candidate approach A - minimal implementation:
- Evidence produced: deterministic stages, basic traces, smoke matrix, replay, audit.
- Strongest cheap baseline that could match it: generic FSM or graph cache may match task behavior.
- Leakage / hard-coding risk: low if hidden state remains outside candidate APIs; medium if observations reveal object effects too directly.
- Smallest falsifying test: tamper a trace reward/action/hash and require replay failure.
- Expected failure mode: environment too easy or policy too weak; accepted as scaffold evidence only.

Candidate approach B - strongest baseline / shortcut-first implementation:
- Evidence produced: baseline-first matrix emphasizing graph-cache and oracle headroom.
- Strongest cheap baseline that could match it: graph cache itself is the central challenger.
- Leakage / hard-coding risk: medium if graph-cache labels are accidentally mixed with candidates.
- Smallest falsifying test: audit fails mislabeled graph-cache/oracle traces and missing minimal-loop variants.
- Expected failure mode: baselines saturate the benchmark; report downgrade or environment redesign, not candidate success.

Candidate approach C - mechanism-faithful implementation:
- Evidence produced: richer candidate update loop and more challenging environment transitions.
- Strongest cheap baseline that could match it: transition table, successor map, exact symbolic lookup.
- Leakage / hard-coding risk: higher in first pass because extra mechanism detail invites post-hoc tuning.
- Smallest falsifying test: planner/no-planner ablations fail to change behavior while claims imply update effects.
- Expected failure mode: overbuilt candidate before the harness is auditable.

Selected approach: A with B embedded as mandatory frozen baselines and audit constraints. Rationale: first-pass goal is a hard-to-fake scaffold; candidate optimization is explicitly out of scope.
