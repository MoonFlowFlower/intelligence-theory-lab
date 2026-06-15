# ACP-BV Surface Spec And Independent-Truth Preflight 001A

Task id: `ACP-BV-SURFACE-SPEC-AND-INDEPENDENT-TRUTH-PREFLIGHT-001A`

Verdict: `acp_bv_surface_spec_ready_for_independent_audit`

## Layer And Status

Current layer: mechanism-hypothesis / engineering-governance surface-spec
preflight only.

Mainline integration status: none.

Enabled status: no new enabled path.

Real trigger evidence: repo readback after
`72cb216a8134d21f1ff9e1d57232464a2df4c8cf` and
`49fc5135005664015fb7728e3817f97bd5c36ff8`; inherited EAV 001B circular
candidate-controlled digest negative evidence; inherited future-only harness
001A candidate-authored `policy_map` ground-truth negative evidence; and the
canonical ledger successor constraint requiring harness-owned,
candidate-inaccessible ground truth.

Claim ceiling: ACP-BV surface-spec and independent-truth preflight only.

Next minimal closed-loop action: independent audit of this specification before
any executable harness task card is drafted.

## Minimal Surface

ACP-BV means `ACTION-CONDITIONED-PREDICTIVE-BOUNDARY-VIABILITY`.

The minimal future surface is an offline episodic environment with:

1. public observations presented to the candidate;
2. hidden boundary state owned by the environment;
3. hidden viability state owned by the environment;
4. action-conditioned transitions owned by the environment;
5. candidate raw prediction and action outputs;
6. harness-owned metrics that score raw candidate outputs against hidden
   environment truth;
7. independent baselines, ablations, replay recomputation, and leakage positive
   controls that use the same harness-owned score path.

The candidate may output only:

- raw observations consumed;
- raw predictions;
- raw actions;
- serialized candidate state;
- optional internal uncertainty/logit traces.

The candidate may not output:

- expected labels;
- expected scores;
- expected digests;
- `producer_function`;
- oracle labels;
- environment hidden state;
- boundary truth;
- viability truth;
- baseline, ablation, replay, or leakage results;
- pass or admission verdicts.

## Truth Ownership

Every score-bearing target must have a candidate-inaccessible owner:

| Truth-bearing value | Owner | Score-bearing | Candidate role |
| --- | --- | --- | --- |
| latent boundary state | environment-owned | yes | never output or mutated by candidate |
| viability state | environment-owned | yes | never output or mutated by candidate |
| action consequences | environment-owned conditional on candidate action | yes | candidate action is an intervention input, not a truth source |
| prediction target | environment-owned / harness-selected | yes | candidate predicts raw future consequences only |
| replay target | environment-owned truth plus harness-owned recomputation path | yes | candidate state is replay input, not a truth key |
| baseline target | environment-owned truth scored by harness-owned metrics | yes | candidate cannot choose baseline labels |
| leakage oracle | harness-owned positive-control fixture and scanner | yes | candidate cannot declare scanner success |
| pass/admission condition | repo-source-owned threshold plus harness-owned metric aggregation | yes | candidate cannot author verdict fields |

The future target is blocked if any score-bearing truth depends on
candidate-authored or candidate-derived fields. Candidate action may condition
which environment transition is scored, but the resulting truth remains generated
by the environment under repo-pinned rules.

## Required Baselines

The future executable surface must compare ACP-BV candidates against:

- candidate-authored self-consistency baseline;
- majority/static-action baseline;
- action-independent predictive baseline;
- observation-only predictor;
- boundary-blind viability baseline;
- no-boundary recurrent or world-model-only learner;
- replay/hash-only baseline;
- leakage/oracle-label baseline if hidden truth leaks.

If the strongest fair baseline matches the candidate on the score-bearing
targets, the verdict must be baseline-equivalent or blocked, not admitted.

## Required Ablations

Each ablation must rerun episodes or replay cases through the same
harness-owned score path.

| Ablation | Expected measurable failure mode |
| --- | --- |
| action-conditioning removed or shuffled | action-conditioned prediction loss worsens or admission blocks; unchanged score indicates action-independent behavior |
| boundary signal hidden or swapped | boundary-dependent subset score worsens or mismatch blocks; unchanged score indicates boundary-blind behavior |
| viability signal decoupled from action consequence | viability calibration and consequence prediction worsen; unchanged score indicates reward-shaping or lookup collapse |
| candidate state reset before replay | memory-required replay cases change or fail; unchanged score indicates no state dependence |
| observations held fixed while hidden boundary/viability truth changes | score changes on predeclared hidden-truth-dependent cases; unchanged score indicates truth is not controlling the score |
| hidden truth held fixed while candidate-authored state changes | target truth and metric target remain fixed; admission must not be controlled by candidate-authored state keys |

## Positive Controls

The future executable surface must include these positive controls:

1. Candidate-authored truth key injection blocks.
2. `policy_map` flip with fixed observations/actions/predictions does not
   control score or admission.
3. Hidden truth flip with fixed candidate-authored state changes the score on
   relevant hidden-truth-dependent cases.
4. Baseline-equivalent candidate is classified as baseline-equivalent, not
   admitted.
5. Leakage scanner uses a real positive-control payload, including nested,
   aliased, and value-channel answer keys, not only a hard-coded string check.
6. Replay hash-only submission blocks.

## Trace And Replay Contract

Future traces must include:

- `episode_id`;
- `seed` or `context_id`;
- `observation`;
- `action`;
- `prediction`;
- `serialized_candidate_state`;
- `environment_hidden_truth_hash`;
- `harness_metric_function_path`;
- `baseline_invocation`;
- `ablation_condition`;
- `replay_recomputation_input`;
- `block_or_admit_reason`.

Replay must recompute candidate behavior from serialized candidate state plus a
new observation and score it against environment/harness truth. Replay must not
compare stored output hashes and must not use candidate-authored truth keys.

## Computed-Evidence Gate For Future Harnesses

Future score-bearing results must be callable computations from
environment-owned or harness-owned truth plus raw candidate outputs.

The future harness must explicitly forbid:

- candidate-selected metric producers;
- candidate-declared expected values;
- candidate-authored ground truth;
- literal verdict dictionaries;
- pass-shaped JSON reports;
- row injection into metric producers;
- baseline, ablation, replay, or leakage results as static fields.

Every future score must record producer function, input artifacts, run id,
seed/context/episode ids, aggregation rule, and code path hash.

## Acceptance Readback

Acceptance gate returned:

```text
acp_bv_surface_spec_ready_for_independent_audit
```

Reason: ACP-BV can be specified without candidate-authored truth by making every
score-bearing truth owner environment-owned, harness-owned, or repo-source-owned
and by limiting candidate output to raw observations consumed, raw predictions,
raw actions, serialized candidate state, and optional uncertainty traces.

This is a future target specification only. It does not implement a Gate, run a
harness, create a candidate, compute ACP-BV evidence, or authorize admission.

## What This Does Not Prove

This does not prove Gate validity, mechanism validity, admission readiness,
bridge readiness, runtime readiness, mainline effect, agency, consciousness,
emotion, autonomy, stable user benefit, or EGO readiness.
