# TLGP-CAPABILITY-WITNESS-GROKKING-PROBE-001B-CURVE-CONFIG-AUDIT-001A

> Status: DRAFT execution card. Authorizes a read-only second-pass curve/config
> audit over the already banked `GROKKING_PROBE_001B` artifacts. This is not a new
> training run, not a continuation, not a known-good sanity task, and not a powered
> sweep.

Task id: TLGP-CAPABILITY-WITNESS-GROKKING-PROBE-001B-CURVE-CONFIG-AUDIT-001A

Problem definition: `GROKKING_PROBE_001B` is now locally banked as formal
`ambiguous` with substantive `negative_leaning_no_grokking_signature`. The remaining
decision uncertainty is not how to label the result, but whether curve shape,
configuration plumbing, split/baseline readbacks, and metric summaries support the
interpretation that the strongest explanation is witness/task-structure mismatch,
with scale second and program/config error not first suspect. A second-pass audit is
needed before deciding whether to move to known-good grokking sanity or a single-cell
continuation.

Current stage/layer: engineering evidence audit / learning-adaptation proxy
interpretation. Local ITL artifact review only.

Mainline target: local artifact interpretation. No EGO mainline integration, no
TLGP-R2 adjudication, no H0/H1 verdict, no route terminal.

Enabled-state requirement: consume the banked local 001B artifacts under
`artifacts/TLGP-CAPABILITY-WITNESS-PREFLIGHT-001A/GROKKING_PROBE_001B/` at or after
local commit `2de7fef7ef4d06f4ede0d48301839f0f71c2753a`.

Real-trigger evidence requirement: independently recompute/read back from:
- `training_records.json`
- `val_curves.jsonl`
- `probe_trend_report.json`
- `route_decision_input.json`
- `route_decision.json`
- `leakage_report.json`
- `manifest.json`
- `closeout_audit_001b.json`
- current `grokking_probe.py`, `route_decision.py`, `minimal_probe.py`, and read-only
  split/world helpers

Hypothesis: the curves/config support the banked interpretation:
formal `ambiguous`, substantive `negative_leaning_no_grokking_signature`; the lone
`0.6011401515` crossing is an unsustained checkpoint blip rather than a positive
or trending grokking morphology; runtime/config uncertainty is limited to missing
direct optimizer param-group serialization in the completed run.

Strongest baseline / false explanation:
- the `0.6011401515` value is not noise but a delayed transition precursor;
- `weight_decay` or optimizer config was not actually applied as intended;
- train/heldout split or label distribution makes heldout artificially unstable;
- balanced-accuracy/chance/baseline framing is misleading;
- route/manifest hashes or artifact banking drifted after the closeout;
- existing closeout audit contains a logic bug or copied artifact self-consistency
  rather than independent recomputation.

Ablation requirement: no new ablation or intervention is authorized. This task may
only compute diagnostics over existing artifacts and static source/config readbacks.

Trace/replay requirement: the audit must recompute all curve-shape diagnostics from
`val_curves.jsonl`, not from `closeout_audit_001b.json` alone. It must compare its
results against the closeout audit and explicitly report drift/no drift.

Computed-evidence provenance gate: create a callable audit producer that records:
- producer script path and SHA256;
- input artifact paths and SHA256;
- current branch/HEAD and the bank commit being audited;
- route/prereg/frozen/probe hashes;
- protected source status for `src/tlgp_001b_r2`, `src/tlgp_001a`,
  `route_decision.py`, `minimal_probe.py`, and `grokking_probe.py`;
- exact per-cell checkpoint coverage and step grid;
- pre-fit, post-fit, tail-20%, and full-run heldout slopes/deltas;
- best-heldout neighbor context and sustained-window tests for thresholds `0.60`,
  `0.65`, and `0.75`;
- post-fit monotonicity / drawdown diagnostics sufficient to distinguish a single
  spike from a stable transition;
- train/heldout split sizes, split hashes, rule distributions, answer distributions,
  and uniform-random/chance reference;
- fair baseline readback from `route_decision_input.json`;
- static optimizer plumbing showing `weight_decay=float(weight_decay)` enters AdamW;
- direct runtime optimizer param-group readback status. For this completed run, if
  param groups were not serialized, record `unavailable` and explain that the audit
  can only prove manifest inputs plus static plumbing, not direct runtime param-group
  values;
- any mismatch with `closeout_audit_001b.json`.

Acceptance gate:
- no source files edited;
- no new training, continuation, known-good sanity run, powered sweep, or GPU rerun;
- all required banked 001B artifacts present;
- `val_curves.jsonl` row count is 150 and covers 6 cells x 25 checkpoints;
- formal status remains `ambiguous`;
- substantive assessment remains either `negative_leaning_no_grokking_signature` or
  a stricter `audit_blocked_requires_operator_review` if an evidence mismatch is
  found;
- no threshold tuning;
- manifest hashes match `515a415b...`, `0dcf3659...`, and `6e61a831...`;
- protected source status is empty for the named source paths;
- if artifact outputs are staged, staged set must be exactly the card outputs and
  must not include `runner.pid` or unrelated workspace files;
- no push, tag, PR, or remote anchor.

Claim ceiling: curve/config audit only. This can reduce uncertainty about program
or configuration explanations for `GROKKING_PROBE_001B`; it cannot prove route
closure, TLGP-R2 validity, transfer/rung3/H1, mechanism validity, witness validity,
agency, self, subjectivity, AGI, EGO readiness, or stable user benefit.

Stop condition: stop and write `curve_config_audit_failure_001b.json` if any required
artifact is missing, any hash gate mismatches, protected source status is dirty,
curve rows are incomplete, a source edit is needed to proceed, a GPU/training action
would be required, or the second-pass audit contradicts the banked closeout in a
way that cannot be explained as a narrower claim ceiling.

Rollback plan: remove only the new curve/config audit card and the new curve/config
audit artifacts. Do not delete or modify banked `GROKKING_PROBE_001B` artifacts.

Expected changed files:
- `docs/task_cards/TLGP-CAPABILITY-WITNESS-GROKKING-PROBE-001B-CURVE-CONFIG-AUDIT-001A.md`
- `artifacts/TLGP-CAPABILITY-WITNESS-PREFLIGHT-001A/GROKKING_PROBE_001B/curve_config_audit_001b.py`
- `artifacts/TLGP-CAPABILITY-WITNESS-PREFLIGHT-001A/GROKKING_PROBE_001B/curve_config_audit_001b.json`
- `artifacts/TLGP-CAPABILITY-WITNESS-PREFLIGHT-001A/GROKKING_PROBE_001B/CURVE_CONFIG_AUDIT_001B.md`
- optional only on failure:
  `artifacts/TLGP-CAPABILITY-WITNESS-PREFLIGHT-001A/GROKKING_PROBE_001B/curve_config_audit_failure_001b.json`

Forbidden changes:
- no edits to `grokking_probe.py`, `minimal_probe.py`, `route_decision.py`,
  `src/tlgp_001b_r2/*`, or `src/tlgp_001a/*`;
- no modification of existing banked 001B artifacts;
- no rerun of `grokking_probe.py --run`;
- no continuation past 50k;
- no known-good grokking sanity task;
- no powered/full sweep;
- no threshold tuning after reading results;
- no `git add -A`;
- no `runner.pid` staging;
- no push, tag, PR, or remote anchor;
- no `AGENTS.md`, `CLAUDE.md`, or global config edits.

Local commit: conditional. If and only if the audit completes cleanly and the user
has authorized local banking, make one local-only scoped commit containing exactly
the card plus the new audit outputs. Otherwise leave outputs uncommitted for
operator review.

Auto-Remote-Anchor: forbidden.

## Collision Record

Approach A - jump directly to known-good grokking sanity: rejected for now. It would
test the runner family, but it would skip the cheaper question of whether the
already banked 001B artifacts contain config/curve evidence that changes the
interpretation.

Approach B - run a best-cell continuation to 100k/150k: rejected for now. The banked
curves do not show late-rise morphology strong enough to justify continuation before
curve/config audit.

Approach C - read-only second-pass curve/config audit: selected. It directly tests
the weakest remaining artifact-level explanations without changing the evidence
surface or spending GPU.

Selected approach: Approach C.
