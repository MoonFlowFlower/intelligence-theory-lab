# ACP-BV Surface Spec 001B Independent Audit Revision 001A

Task id: `ACP-BV-SURFACE-SPEC-001B-INDEPENDENT-AUDIT-REVISION-001A`

Verdict: `acp_bv_surface_spec_001b_ready_for_independent_reaudit`

## Layer And Status

Current layer: mechanism-hypothesis / engineering-governance ACP-BV
surface-spec revision only.

Mainline integration status: none.

Enabled status: no new enabled path.

Real trigger evidence: current repo state at
`8ce1df30da8c146060effd348546c7bad5bdf433`, with
`remote-anchor-acp-bv-surface-spec-independent-truth-preflight-001a-8ce1df3`
resolving to that commit, and independent audit conclusion:

```text
accept_surface_spec_for_audit_layer;
conditional_pass_with_required_revisions_before_harness_card
```

Claim ceiling: ACP-BV surface-spec revision only.

Next minimal closed-loop action: independent reaudit of this revised spec before
any executable harness task card is drafted.

## Preserved Independent Audit Conclusion

The audit accepted the anchored 001A spec as non-circular at the surface-spec
layer, but required revisions before any executable harness card.

Strongest residual risks preserved by this revision:

1. replay state-lookup table over seen context;
2. action-as-difficulty selection;
3. non-fail-able leakage scanner;
4. missing graph-cache challenger family;
5. post-hoc ablation thresholds;
6. uncertainty/logit traces as hidden truth or selection keys.

## R1 - Graph-Cache Challenger Family

Future ACP-BV executable work must include the graph-cache challenger family as
mandatory baselines or challengers. Each challenger must be an independent
callable implementation scored through the same harness-owned metric path as the
candidate.

The family is:

- `graph_lookup`;
- `transition_table`;
- `successor_map`;
- `count_table`;
- `episodic_traversal`;
- `fsm_planner`.

Each challenger receives only public observations, candidate-visible action
history, environment-assigned context identifiers, and past transition records
allowed to the baseline. It must not receive hidden boundary truth, hidden
viability truth, held-out replay targets, expected actions, expected scores,
producer functions, pass verdicts, future observations, or any candidate-
authored answer key.

If a challenger matches ACP-BV on the score-bearing targets within the
predeclared equivalence criterion, ACP-BV must be classified as
baseline-equivalent, not pass.

## R2 - Replay Held-Out And Lookup-Table Blocker

Replay must use targets unavailable at serialized-state time. At least one of
these must be present in the future executable card:

- held-out `context_id` or seed;
- unseen observation / boundary / viability combination;
- harness-owned counterfactual transition.

Serialized candidate state must not contain direct input-output answer tables
for replay targets. A positive control is mandatory:

1. candidate `serialized_state` contains an input-output lookup table for seen
   contexts;
2. replay on seen context may succeed but must be marked non-counting;
3. replay on held-out or unseen context must expose the failure or block as
   `lookup_table_replay_leakage`.

## R3 - Leakage Scanner Real Failability

The future leakage scanner must run against two real payload classes:

- clean raw-output bundle expected to pass leakage scan;
- dirty payload expected to block.

The dirty payload must contain at least one of each forbidden class: oracle
label, hidden boundary, hidden viability, expected action, expected score,
producer function, pass verdict, and answer-key alias. Nested fields, value
channels, alias keys, and path-like fields are in scope.

Scanner result artifacts must record payload path, scanner callable path,
positive-control block reason, and clean-control pass result. A hard-coded-only
string self-test is not sufficient evidence.

## R4 - Action-As-Difficulty Control

The future surface must prevent the candidate from scoring highly merely by
selecting predictable or easy actions. At least one of these controls is
required, and the selected control must be declared before candidate evaluation:

- fixed action set;
- harness-sampled action probes;
- difficulty-normalized prediction score;
- counterfactual action queries where the harness selects actions.

If a future executable card cannot separate action selection from task
difficulty, it must return:

```text
acp_bv_surface_spec_blocked_by_action_difficulty
```

## R5 - Predeclared Ablation Thresholds And Effect Sizes

Each mechanism-critical ablation must predeclare metric direction, minimum
effect criterion, equivalence criterion, block condition, and threshold source.

Metrics must be normalized to `[0, 1]` before applying fixed thresholds. Unless
the executable card justifies a stricter independent-baseline-derived threshold
before candidate evaluation, this spec requires:

- minimum mechanism-critical degradation: absolute normalized delta `>= 0.05`;
- equivalence criterion: absolute normalized delta `< 0.02`;
- inconclusive band: absolute normalized delta `>= 0.02` and `< 0.05`, which
  blocks admission rather than permitting post-hoc threshold tuning.

If a threshold cannot be fixed or derived only from independent baselines before
candidate evaluation, the future task must record
`threshold_unavailable_blocker`.

## R6 - Uncertainty And Logit Trace Restriction

Uncertainty and logit traces may be recorded as diagnostic raw outputs only.
They cannot:

- define truth labels;
- select which cases count;
- mask hard cases;
- act as admission/pass verdict;
- replace environment-owned or harness-owned outcomes.

If uncertainty or logits are scored at all, they must be scored only against
environment-owned or harness-owned outcomes, through the same future metric
provenance gate as every other score.

## Truth Ownership Update

Truth-bearing values introduced by R1-R6 are classified in
`artifacts/acp_bv_surface_spec_001b_independent_audit_revision_001a/truth_ownership_inventory.json`.

Any score-bearing value classified as candidate-authored or candidate-derived
must block. Candidate-authored raw action, serialized state, and diagnostic
logit/uncertainty traces may be inputs or diagnostic outputs only; they are not
independent truth.

## Artifact Matrices

This revision updates:

- `baseline_matrix.json`;
- `ablation_matrix.json`;
- `positive_controls.json`;
- `trace_replay_schema.json`;
- `truth_ownership_inventory.json`;
- `result.json`;
- `validation.json`;
- `claim_ceiling.txt`;
- `readback.md`.

Baseline results: not run. This task specifies future baselines only.

Ablation results: not run. This task specifies future ablations only.

Replay result: not run. This task specifies future replay requirements only.

Leakage result: not run. This task specifies future clean and dirty payload
requirements only.

## Acceptance Readback

Acceptance gate returned:

```text
acp_bv_surface_spec_001b_ready_for_independent_reaudit
```

Reason: R1-R6 are incorporated at the specification layer; no score-bearing
truth is candidate-authored or candidate-derived; graph-cache challengers,
held-out replay, real leakage controls, action-difficulty controls,
predeclared ablation thresholds, and uncertainty/logit restrictions are
specified; no harness implementation was created.

## What This Does Not Prove

This does not prove Gate validity, mechanism validity, admission readiness,
bridge readiness, runtime readiness, mainline effect, agency, consciousness,
emotion, autonomy, stable user benefit, or EGO readiness.
