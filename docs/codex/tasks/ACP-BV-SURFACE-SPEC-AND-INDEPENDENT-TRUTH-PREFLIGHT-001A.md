# ACP-BV-SURFACE-SPEC-AND-INDEPENDENT-TRUTH-PREFLIGHT-001A

## Bounded Task Card

Task id: `ACP-BV-SURFACE-SPEC-AND-INDEPENDENT-TRUTH-PREFLIGHT-001A`

Problem definition: `GATE-TARGET-INDEPENDENT-GROUND-TRUTH-PREFLIGHT-001A`
ended with `target_selection_blocked` because
`ACTION-CONDITIONED-PREDICTIVE-BOUNDARY-VIABILITY` was only a future route
selected for task-card drafting, not a concrete executable Gate target. This
task converts that route idea into a bounded evidence-surface specification or
returns blocked before any harness, Gate rerun, or implementation.

Current stage/layer: mechanism-hypothesis / engineering-governance
surface-spec preflight only.

Mainline target: none. This task does not wire into Gate3, Gate4, integrated
admission, bridge, runtime, companion, or EGO mainline.

Enabled-state requirement: no new enabled path. This task produces
documentation/specification and artifact readback only. No harness execution is
authorized.

Real-trigger evidence requirement: start from current repo state after
`72cb216a8134d21f1ff9e1d57232464a2df4c8cf` and
`49fc5135005664015fb7728e3817f97bd5c36ff8`; cite and inherit:

- EAV 001B circular candidate-controlled digest negative evidence;
- future-only harness 001A candidate-authored `policy_map` ground-truth
  negative evidence;
- canonical ledger successor constraint requiring harness-owned,
  candidate-inaccessible truth.

Hypothesis: ACP-BV is worth implementing only if a minimal surface can be
specified where at least one score-bearing path uses environment-owned or
harness-owned hidden truth that the candidate cannot author, select, mutate, or
infer trivially from leaked fields.

Strongest baseline: candidate-authored self-consistency, where the candidate
supplies behavior plus the answer key, like `policy_map` in the failed
future-only harness, producing perfect apparent score while proving only
consistency with candidate-authored truth.

Additional baselines to specify:

- majority/static-action baseline;
- action-independent predictive baseline;
- observation-only predictor;
- boundary-blind viability baseline;
- replay/hash-only baseline;
- leakage/oracle-label baseline if hidden truth leaks.

Ablation requirement:

1. action-conditioning removed or shuffled;
2. boundary signal hidden or swapped;
3. viability signal decoupled from action consequence;
4. candidate state reset before replay;
5. observations held fixed while hidden boundary/viability truth changes;
6. hidden truth held fixed while candidate-authored state changes.

Each ablation must define a measurable failure mode. If candidate score is
unchanged under all mechanism-critical ablations, the future surface is not
discriminative.

Trace/replay requirement: future traces must include `episode_id`,
`seed/context_id`, `observation`, `action`, `prediction`, serialized candidate
state, environment hidden truth hash, harness-owned metric function path,
baseline invocation, ablation condition, replay recomputation input, and
block/admit reason. Replay must recompute behavior from serialized candidate
state plus new observation against environment/harness truth. Replay must not
compare stored output hashes or use candidate-authored truth keys.

Computed-evidence provenance gate: all future score-bearing results must be
computed from harness-owned/environment-owned truth plus raw candidate outputs.
The future harness must forbid candidate-selected metric producers,
candidate-declared expected values, candidate-authored ground truth, literal
verdict dictionaries, pass-shaped JSON reports, row injection into metric
producers, and baseline/ablation/replay/leakage as static fields.

Acceptance gate for this preflight: exactly one of the task-card outcomes must
be returned. This task returns:

`acp_bv_surface_spec_ready_for_independent_audit`

Rationale: ACP-BV can be specified as a minimal future evidence surface if the
hidden boundary state, viability state, action consequences, prediction target,
baseline targets, replay targets, leakage oracle, and admission condition are
owned by the environment, harness, or repo-pinned metric contract rather than by
the candidate. The result is only a target specification ready for independent
audit. It is not executable evidence.

Claim ceiling: ACP-BV surface-spec and independent-truth preflight only. No Gate
validity, mechanism validity, admission readiness, bridge readiness, runtime
readiness, mainline effect, agency, consciousness, emotion, autonomy, stable
user benefit, or EGO readiness claim.

Stop condition: stop if the task begins implementing a harness, creates a
candidate model, mutates old Gate bundles, treats candidate-authored truth as
independent truth, claims ACP-BV evidence rather than surface-spec readiness, or
uses memory rather than repo readback for canonical state.

Rollback plan: if blocked, preserve a bounded blocker artifact and leave source
unchanged. Do not repair verifier/harness/Gate in this task.

Expected changed files:

- `docs/codex/tasks/ACP-BV-SURFACE-SPEC-AND-INDEPENDENT-TRUTH-PREFLIGHT-001A.md`
- `docs/research/ACP-BV-SURFACE-SPEC-AND-INDEPENDENT-TRUTH-PREFLIGHT-001A.md`
- `artifacts/acp_bv_surface_spec_and_independent_truth_preflight_001a/**`

Forbidden changes:

- `src/one_gate_future_only_non_circular_harness_001a/**`
- `src/evidence_admission_verifier_001a/**`
- Gate3/Gate4 source or artifacts except read-only references
- integrated admission / bridge / runtime / mainline files
- unrelated tests
- unrelated artifacts

Auto-Remote-Anchor decision: conditional. Remote-anchor is allowed only if the
acceptance gate is clearly reached, final worktree is clean, changed files are
within allowlist, and local HEAD, remote branch HEAD, local tag, and remote tag
exactly match after publication.

## Bounded Audit Before Specification

Layer: mechanism-hypothesis / engineering-governance surface-spec preflight.

Real objective: define whether ACP-BV can become a bounded future target whose
score-bearing truth is independent of candidate-authored state, reports,
digests, labels, or verdict fields.

Problem definition wrong if: this task treats a named route as evidence, creates
or runs a harness, introduces a candidate, uses old harness truth as sufficient,
or converts self-consistency into mechanism evidence.

Strongest baseline explanation: candidate-authored self-consistency can produce
perfect apparent score if the candidate provides both behavior and the answer
key.

Strongest invalidating reason: ACP-BV may collapse into ordinary model-based
control, reward shaping, hidden lookup, or leaked oracle labels unless hidden
boundary/viability truth and metric ownership are isolated from candidate
outputs.

Would falsify this surface-spec framing: a future executable card cannot define
any score-bearing target whose truth owner is environment-owned, harness-owned,
or repo-source-owned and candidate-inaccessible.

Evidence still insufficient: route-governance prose, a task name, report
self-consistency, static verdict JSON, candidate-supplied expected labels,
candidate-supplied producer functions, candidate-authored policy maps, or replay
hash equality.

Mechanism vs resemblance: this task does not test a mechanism. It specifies a
future surface that must be able to distinguish action-conditioned predictive
boundary/viability use from simpler baselines and report-shaped success.

Risk checks:

- hard-coding: no mechanism or scorer code is added.
- local optimum: do not repair the failed future-only harness.
- Zeno trap: this is a single surface-spec preflight, not another Gate repair.
- evidence leakage: candidate may not output labels, scores, digests, hidden
  truth, producer functions, or verdicts.
- weak baseline: strongest self-consistency and no-boundary baselines are
  preserved.
- schema split / second logic path: future harness must use one score path for
  candidate, baselines, ablations, replay, and leakage positive controls.
- replay weakness: replay must recompute behavior from serialized candidate
  state plus new observation against environment/harness truth.
- claim inflation: only surface-spec readiness for independent audit is claimed.

Minimal validation: read current git state, read the inherited negative evidence,
write only allowed files, parse produced JSON artifacts, scan changed files for
forbidden readiness claims, verify changed-file allowlist, inspect diff, and
commit/anchor only if the conditional gates pass.

Acceptance signal: `acp_bv_surface_spec_ready_for_independent_audit` with
machine-readable truth ownership, baseline, ablation, positive-control, trace
schema, and validation artifacts.

## Result Summary

Verdict: `acp_bv_surface_spec_ready_for_independent_audit`.

ACP-BV can be specified as a minimal future evidence surface without
candidate-authored truth if the future harness owns the hidden environment
state, target generator, metric functions, baselines, ablations, leakage oracle,
replay recomputation path, and admission rule. Candidate output is limited to raw
observations consumed, raw predictions, raw actions, serialized candidate state,
and optional internal uncertainty/logit traces. Candidate outputs are never
truth-bearing.

This task does not implement the future harness and does not produce ACP-BV
evidence. It only defines a bounded target specification ready for independent
audit.

Next minimal closed-loop action: independent audit of this surface spec. Only if
that audit accepts the truth ownership and discriminative controls should a
separate executable-harness task card be drafted.
