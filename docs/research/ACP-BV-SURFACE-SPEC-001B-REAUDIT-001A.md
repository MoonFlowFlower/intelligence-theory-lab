# ACP-BV Surface Spec 001B Reaudit Preservation 001A

Task id: `ACP-BV-001B-REAUDIT-PRESERVATION-AND-HARNESS-CARD-DRAFT-001A`

Verdict: `acp_bv_harness_card_draft_ready_for_independent_review`

## Layer And Status

Current layer: engineering-governance / ACP-BV reaudit preservation and
harness task-card drafting only.

Mainline integration status: none.

Enabled status: no new enabled path.

Real trigger evidence:

- current branch: `codex/meta-theory-scaffold`;
- current start commit: `d8cf5bbf2fdd9895da03d3d382f6f1e0517f2226`;
- local tag:
  `remote-anchor-acp-bv-surface-spec-001b-independent-audit-revision-001a-d8cf5bb`;
- remote branch and remote tag readback at task start both resolved to
  `d8cf5bbf2fdd9895da03d3d382f6f1e0517f2226`;
- worktree at task start: clean.

Claim ceiling: ACP-BV reaudit preservation and executable harness task-card
drafting only.

Next minimal closed-loop action: independent review of
`docs/codex/tasks/ACP-BV-EXECUTABLE-HARNESS-001A-TASK-CARD.md` before any
harness source, test, candidate, Gate, admission, bridge, runtime, or mainline
work.

## Preserved Independent Reaudit Conclusion

Independent read-only reaudit of anchored ACP-BV surface-spec 001B at
`d8cf5bbf2fdd9895da03d3d382f6f1e0517f2226` returned:

```text
accept_for_harness_card_drafting_with_required_bindings
```

The conclusion is preserved only at the audit/spec layer. It authorizes future
executable harness task-card drafting, not implementation.

Blocking issues at the spec layer: none.

Non-blocking but binding harness-card requirements: B1-B5.

No baseline, ablation, replay, leakage, Gate, admission, or mechanism evidence
was executed by this task.

## Binding Requirements Preserved

B1 - Counterfactual action and difficulty control:

- `harness_selected_counterfactual_action_queries` are mandatory.
- A fixed action set alone is insufficient.
- The future harness must include an independent difficulty source, such as a
  graph-cache/static challenger error profile or repo-source-owned environment
  difficulty metadata.
- The difficulty normalization function must be predeclared.
- Candidate error, candidate logits, candidate confidence, and
  candidate-authored difficulty cannot define difficulty.

B2 - Real control execution, no self-reported booleans:

- The future harness must execute and persist clean, dirty, lookup-table replay,
  counterfactual-action, graph-cache-comparator, and replay-hash-only controls.
- Each control artifact must record command, run_id, seed/context/episode IDs,
  input hashes, output hashes, callable path, code path hash, block reason, and
  clean pass result.
- Self-reported booleans such as `command_readback_passed: true` or
  `acceptance_gates: true` cannot be load-bearing evidence.

B3 - Baseline equivalence band repeated locally:

- The future harness card restates the numeric equivalence rules in its own
  baseline matrix.
- Equivalence band: `< 0.02`.
- Inconclusive band: `[0.02, 0.05)`.
- Minimum mechanism-relevant effect: `>= 0.05`.
- Baseline equivalence must be classified as `baseline_equivalent`, not pass.

B4 - Source-hash provenance:

- The future harness card requires source-hash provenance for scorer,
  environment generator, held-out/counterfactual truth generator, leakage
  scanner, graph-cache challengers, replay recomputation function, and ablation
  runner.
- Each entry must record callable path, source path, code path hash, and whether
  it is repo-source-owned.

B5 - Candidate-inaccessible environment and challenger generators:

- Environment and challenger generator code must be repo-source-owned.
- It must be candidate-inaccessible, outside candidate output/artifact
  directories, not selected by the candidate, and not influenced by
  candidate-authored serialized state, policy_map, labels, logits, confidence,
  score, verdict, or producer_function.

## Prior Negative Evidence Cited

The future harness card inherits these constraints as blockers, not as problems
to smooth over:

- `docs/NEGATIVE_EVIDENCE_LEDGER.md` lines 48-51 records that a future-only
  harness remained non-circularly invalid when candidate-authored `policy_map`
  controlled ground truth.
- `docs/NEGATIVE_EVIDENCE_LEDGER.md` lines 77-79 requires a separate
  independent-ground-truth preflight and route downgrade if no harness-owned /
  candidate-inaccessible truth source exists.
- `artifacts/CLAUDE-INDEPENDENT-GATE0-3-EVIDENCE-PROVENANCE-HOSTILE-AUDIT-001A/audit_result.json`
  records literal baseline/ablation and report-shaped evidence risks for Gate1,
  Gate3, and the integrated testbed.
- `artifacts/preserve_claude_gate0_3_evidence_provenance_hostile_audit_001a_and_freeze_downstream_inheritance_001a/freeze_matrix.json`
  freezes Gate1 graph-cache non-equivalence, Gate3 baseline superiority, and
  integrated shared-state claims unless real callable reruns defeat the
  controls.
- `artifacts/post_freeze_gate0_3_sequential_repair_queue_001a_gate1_failed_graph_cache_reconciliation/baseline_comparison.json`
  preserves graph-cache, transition-table, successor-map, count-table,
  episodic-traversal, and FSM/planner controls as fair controls that matched or
  beat the prior Gate1 candidate.
- `artifacts/gate_target_independent_ground_truth_preflight_001a/result.json`
  records that ACP-BV was previously only a route for future task-card drafting,
  with no executable target or independent truth fields.

## Bounded Audit Before Drafting

Layer: engineering-governance / harness-card drafting only.

Real objective: preserve the independent reaudit conclusion and draft a future
executable harness card that cannot weaken B1-B5 into optional suggestions.

Problem definition would be wrong if this task implemented a harness, created a
candidate, created `src/**` or `tests/**`, mutated Gate artifacts, or claimed
baseline, ablation, replay, leakage, mechanism, admission, bridge, runtime, or
mainline evidence.

Strongest baseline explanation: a graph-cache, lookup-table replay,
action-difficulty chooser, static report function, or candidate-authored truth
channel could mimic ACP-BV surface success without evidence for an
action-conditioned boundary/viability mechanism.

Strongest invalidating reason: if the future card cannot make difficulty,
truth, challenger generation, leakage controls, replay targets, and metric
producers independent of candidate-authored outputs, harness implementation
must block.

Would falsify the current framing: B1-B5 cannot be expressed as hard,
non-circular, reviewable harness requirements without requiring implementation
in this task.

Evidence still insufficient: a prose acceptance statement, pass-shaped JSON,
self-reported command booleans, candidate-declared expected values,
candidate-selected producers, stored replay hashes without recomputation, or
baseline rows injected into metric producers.

Mechanism vs resemblance: this task tests no mechanism. It preserves governance
and drafts a future fail-able harness card.

Risk checks:

- hard-coding: no metric, scorer, environment, challenger, candidate, source, or
  test code is added.
- local optimum: no old Gate artifact is patched into a pass.
- Zeno trap: this task routes only to independent review of the card.
- evidence leakage: B2 and B5 require dirty controls and candidate-inaccessible
  truth/challenger generation.
- weak baseline: B3 requires graph-cache-family equivalence to classify as
  `baseline_equivalent`, not pass.
- schema split / second logic path: the future card requires candidate,
  baselines, ablations, leakage, and replay through one harness-owned metric
  path.
- replay weakness: held-out/unseen replay and lookup-table positive controls are
  mandatory.
- claim inflation: the verdict is harness-card draft readiness only.

Minimal validation: parse new JSON artifacts, inspect changed paths against the
allowlist, scan for forbidden `src/**`, `tests/**`, Gate, bridge, runtime, or
mainline changes, verify B1-B5 and required negative-evidence citations are
present, inspect diff, and commit only if the acceptance gate is reached.

Stop condition: stop if any binding is weakened, any implementation path is
created, any old artifact is mutated, any execution result is claimed, or any
candidate-authored truth becomes independent truth.

Rollback plan: if blocked, preserve a bounded blocker artifact in
`artifacts/acp_bv_001b_reaudit_preservation_and_harness_card_draft_001a/` and
leave source unchanged.

## Acceptance Readback

Acceptance gate returned:

```text
acp_bv_harness_card_draft_ready_for_independent_review
```

Reason: the independent reaudit conclusion is preserved; B1-B5 are incorporated
as hard requirements in the future executable harness task card; no harness,
source, test, candidate, Gate artifact, admission, bridge, runtime, or mainline
implementation was created; and the claim ceiling remains ACP-BV reaudit
preservation plus harness-card drafting only.

## What This Does Not Prove

This does not prove Gate validity, mechanism validity, ACP-BV validity,
admission readiness, bridge readiness, runtime readiness, mainline effect,
agency, consciousness, emotion, autonomy, stable user benefit, or EGO readiness.
