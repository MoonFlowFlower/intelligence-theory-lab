# ACP-BV-SURFACE-SPEC-001B-INDEPENDENT-AUDIT-REVISION-001A

## Bounded Task Card

Task id: `ACP-BV-SURFACE-SPEC-001B-INDEPENDENT-AUDIT-REVISION-001A`

Problem definition: Independent audit of anchored ACP-BV surface spec
`8ce1df30da8c146060effd348546c7bad5bdf433` returned
`accept_surface_spec_for_audit_layer;
conditional_pass_with_required_revisions_before_harness_card`. The audit
accepted that the surface spec is non-circular at the surface-spec layer, but
required revisions before any executable harness task card.

Current stage/layer: mechanism-hypothesis / engineering-governance ACP-BV
surface-spec revision only.

Mainline target: none. This task does not wire into Gate3, Gate4, integrated
admission, bridge, runtime, companion, or EGO mainline.

Enabled-state requirement: no new enabled path. Specification and artifact
generation only. No candidate, no harness execution, and no Gate rerun.

Real-trigger evidence requirement: start from repo state at
`8ce1df30da8c146060effd348546c7bad5bdf433` with tag
`remote-anchor-acp-bv-surface-spec-independent-truth-preflight-001a-8ce1df3`
resolving to the same commit. Preserve the independent audit conclusion and
residual risks in repo-visible artifacts.

Hypothesis: ACP-BV can proceed toward an executable harness task card only if
this surface specification closes the residual candidate-control and
weak-baseline channels at the specification layer.

Strongest baseline: graph-cache and lookup-family challengers can memorize or
index observed transitions well enough to match ACP-BV surface behavior without
using a mechanism-critical action-conditioned boundary/viability proxy.

Baseline requirement: the future executable harness card must include the
graph-cache challenger family in addition to the 001A baselines. The audit-
required family is `transition_table`, `successor_map`, `count_table`,
`episodic_traversal`, and `fsm_planner`; this revision also includes
`graph_lookup` because the repo operating contract treats it as part of the
graph-cache collapse family.

Ablation requirement: each mechanism-critical ablation must predeclare metric
direction, minimum effect criterion, equivalence criterion, and block condition.
No threshold tuning after candidate results is allowed.

Trace/replay requirement: replay must use held-out or unseen candidate-
inaccessible targets unavailable at serialized-state time. Serialized candidate
state must not contain direct input-output answer tables for replay targets.
Replay success on seen context may be recorded as a positive-control failure
only; it must not count as ACP-BV evidence.

Computed-evidence provenance gate: this is a specification task and does not
claim actual baseline, ablation, replay, leakage, or ACP-BV results. Future
evidence-bearing requirements must be callable, testable, and fail-able.

Acceptance gate: return exactly one of:

- `acp_bv_surface_spec_001b_ready_for_independent_reaudit`;
- `acp_bv_surface_spec_001b_blocked_by_graph_cache_baseline`;
- `acp_bv_surface_spec_001b_blocked_by_replay_lookup_table`;
- `acp_bv_surface_spec_001b_blocked_by_action_difficulty`;
- `acp_bv_surface_spec_001b_blocked_by_leakage_failability`;
- `acp_bv_surface_spec_001b_blocked_by_threshold_or_trace_control`.

This task returns:

`acp_bv_surface_spec_001b_ready_for_independent_reaudit`

Acceptance rationale: R1-R6 are incorporated at the specification layer; no
score-bearing truth is candidate-authored or candidate-derived; the graph-cache
challenger family is specified; replay requires held-out/unseen candidate-
inaccessible targets; leakage scanner controls require real clean and dirty
payloads; action-as-difficulty is controlled by fixed or harness-selected action
probes; ablation thresholds and equivalence rules are predeclared; uncertainty
and logit traces are restricted to diagnostic raw outputs; no harness is
implemented.

Claim ceiling: ACP-BV surface-spec revision only. No Gate validity, mechanism
validity, admission readiness, bridge readiness, runtime readiness, mainline
effect, agency, consciousness, emotion, autonomy, stable user benefit, or EGO
readiness claim.

Stop condition: stop if this task implements a harness, creates a candidate
model, mutates old Gate bundles, claims baseline/ablation/replay results as
run, treats candidate-authored truth as independent truth, omits graph-cache
challengers, leaves replay without held-out/unseen targets, leaves leakage
controls as hard-coded string checks, ignores action difficulty, leaves
thresholds post-hoc, or lets uncertainty/logit traces become hidden truth keys.

Rollback plan: if blocked, preserve blocker artifact and leave source unchanged.
Do not proceed to harness.

Expected changed files:

- `docs/codex/tasks/ACP-BV-SURFACE-SPEC-001B-INDEPENDENT-AUDIT-REVISION-001A.md`
- `docs/research/ACP-BV-SURFACE-SPEC-001B-INDEPENDENT-AUDIT-REVISION-001A.md`
- `artifacts/acp_bv_surface_spec_001b_independent_audit_revision_001a/**`

Forbidden changes:

- `src/**`
- Gate3/Gate4 source or artifacts except read-only references
- integrated admission / bridge / runtime / mainline files
- unrelated tests
- unrelated artifacts

Auto-Remote-Anchor decision: conditional. Remote-anchor is allowed only if the
acceptance gate is clearly reached, final worktree is clean, changed files are
within allowlist, and local HEAD, remote branch HEAD, local tag, and remote tag
exactly match after publication.

## Bounded Audit Before Revision

Layer: mechanism-hypothesis / engineering-governance surface-spec revision only.

Real objective: revise the ACP-BV specification so the next possible executable
harness card cannot admit graph-cache lookup, seen-context replay, non-fail-able
leakage checks, easy-action selection, post-hoc ablation thresholds, or
uncertainty/logit side channels as ACP-BV evidence.

Problem definition wrong if: this task implements a harness, creates a
candidate, reruns a Gate, edits old evidence bundles, claims executable ACP-BV
evidence, or treats the independent audit's conditional pass as harness-card
authorization.

Strongest baseline explanation: a graph-cache or action-difficulty chooser can
look successful by replaying seen transition structure, selecting predictable
actions, or exploiting answer-like fields while never using an ACP-BV mechanism.

Strongest invalidating reason: if action-conditioned boundary/viability cannot
be separated from graph-cache lookup, replay lookup tables, or action-difficulty
selection, the surface should block rather than proceed to harness.

Would falsify this revision framing: the spec cannot define candidate-
inaccessible held-out replay targets, real leakage clean/dirty controls,
graph-cache equivalence rules, action-difficulty controls, predeclared
ablation thresholds, and uncertainty/logit restrictions without collapsing ACP-
BV into a baseline.

Evidence still insufficient: prose that the candidate is non-circular, static
JSON verdicts, dirty-payload scanner strings without callable scanner path,
seen-context replay success, candidate-authored uncertainty as a truth key, or
post-hoc threshold selection.

Mechanism vs resemblance: this task does not test a mechanism. It revises the
future evidence surface so a later executable task card can be independently
audited for mechanism-relevant failability.

Risk checks:

- hard-coding: no scorer, harness, candidate, or threshold-fitting code is
  added.
- local optimum: do not repair old Gate or 001A artifacts into a pass.
- Zeno trap: either the spec closes R1-R6 or returns a blocker verdict.
- evidence leakage: dirty payload controls include labels, hidden truth,
  expected actions, expected scores, producer functions, pass verdicts, and
  answer-key aliases.
- weak baseline: graph-cache and action-difficulty challengers are mandatory.
- schema split / second logic path: candidate, baselines, ablations, replay, and
  leakage must use one future harness-owned scoring path.
- replay weakness: replay requires held-out/unseen targets unavailable at
  serialized-state time.
- claim inflation: only surface-spec revision readiness for independent reaudit
  is claimed.

Minimal validation: parse all new JSON artifacts, scan changed paths against the
allowlist, scan for forbidden source/test/mainline edits, verify R1-R6 markers,
verify no harness implementation file is created, inspect diff, and commit only
if the acceptance gate is reached.

Acceptance signal: `acp_bv_surface_spec_001b_ready_for_independent_reaudit`
with repo-visible artifacts for baseline, ablation, replay, leakage, truth
ownership, validation, claim ceiling, and readback.
