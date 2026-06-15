# ACP-BV Surface Spec And Independent-Truth Preflight 001A Readback

Verdict: `acp_bv_surface_spec_ready_for_independent_audit`.

Layer: mechanism-hypothesis / engineering-governance surface-spec preflight
only.

Mainline integration status: none.

Enabled status: none.

Real trigger evidence:

- current repo state after `72cb216a8134d21f1ff9e1d57232464a2df4c8cf` and
  `49fc5135005664015fb7728e3817f97bd5c36ff8`;
- EAV 001B candidate-controlled digest negative evidence;
- future-only harness 001A candidate-authored `policy_map` ground-truth
  negative evidence;
- canonical ledger successor constraint requiring harness-owned,
  candidate-inaccessible truth.

Acceptance gate: `A`.

Acceptance label: `acp_bv_surface_spec_ready_for_independent_audit`.

Reason: ACP-BV can be specified without candidate-authored truth if all
score-bearing truth is environment-owned, harness-owned, or repo-source-owned,
and candidate output is limited to raw observations consumed, raw predictions,
raw actions, serialized candidate state, and optional uncertainty traces.

Artifacts generated:

- `result.json`
- `truth_ownership_inventory.json`
- `baseline_matrix.json`
- `ablation_matrix.json`
- `positive_controls.json`
- `trace_replay_schema.json`
- `source_hashes.json`
- `validation.json`
- `claim_ceiling.txt`
- `readback.md`

Baseline results: not run. This task specifies future baselines only.

Ablation results: not run. This task specifies future ablations only.

Replay result: not run. This task specifies future replay recomputation
requirements only.

Stop conditions triggered: none during specification. No harness was
implemented, no candidate was created, no Gate was rerun, and no old Gate bundle
was mutated.

Claim ceiling: ACP-BV surface-spec and independent-truth preflight only.

Next minimal closed-loop action: independent audit of this surface spec. Only
after acceptance should a separate executable-harness task card be drafted.

What this does not prove: Gate validity, mechanism validity, admission
readiness, bridge readiness, runtime readiness, mainline effect, agency,
consciousness, emotion, autonomy, stable user benefit, or EGO readiness.
