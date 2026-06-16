# ACP-BV Distribution Redesign Spec 001B

Task id: `ACP-BV-DISTRIBUTION-REDESIGN-SPEC-001B`

Spec status: ready for independent hostile spec audit only.

## Layer And Status

Current layer: mechanism-hypothesis / engineering-governance distribution
redesign spec only.

Mainline integration status: none.

Enabled status: none. This specification does not create or modify a Gate,
bridge, runtime, admission path, scheduler, live path, mainline path, or real
Gate target.

Real trigger evidence: ACP-BV 001A closed with
`blocked_by_baseline_equivalence` at
`c105a965de9e05dfdea7bc77b393bd5c85e43754`, with
`full_access_lookup_baseline` tying the candidate at `1.0`, delta `0.0`,
train/heldout overlap `18/18`, and reference candidate classification
`oracle_like_reference_candidate_scaffolding_only`.

Claim ceiling: ACP-BV 001A negative-evidence closure and ACP-BV 001B
distribution redesign spec only.

Next minimal closed-loop action: independent hostile spec audit. Do not
implement ACP-BV 001B until this redesign spec passes independent audit and a
separate bounded implementation task card authorizes exact source, test, and
artifact paths.

## Redesign Objective

ACP-BV 001B must define a distribution where a fair full-access memory or
lookup baseline over train keys is no longer a complete policy, while the task
remains solvable by a candidate that uses the intended
action-conditioned predictive boundary/viability mechanism.

The goal is not cosmetic difficulty. The goal is to make the evidence surface
distinguish:

- train-key memorization;
- visible-key lookup;
- graph-cache replay;
- candidate self-consistency;
- truth leakage;
- oracle-like scaffolding;
- action-conditioned predictive boundary/viability behavior.

## G1 - True Heldout Generalization

Heldout episodes must contain keys, configurations, or latent combinations not
present in training.

The future harness must persist a detector with:

- train key set;
- heldout key set;
- overlap count;
- overlap ratio;
- unseen heldout key count;
- memory-complete-policy verdict.

Required block rule:

```text
if overlap_ratio == 1.0 and full_access_lookup_baseline ties candidate:
    verdict = blocked_by_baseline_equivalence
```

Heldout key construction must be frozen before candidate scoring. The key
schema must be recorded, and changing it after seeing candidate or baseline
scores is forbidden.

## G2 - Candidate Not Equal To Truth Formula

The future reference candidate must not share the same formula or source path
as the truth generator.

If a scaffold candidate is included, it must be labeled:

```text
oracle_like_reference_candidate_scaffolding_only
```

Such a candidate may be used only for wiring checks or negative controls. It
must not be cited as ACP-BV mechanism-relevant evidence.

Required detector:

- candidate function path;
- truth generator function path;
- source hash for each path;
- shared helper dependency analysis;
- formula-equivalence classification;
- block or downgrade reason if formula coupling is detected.

## G3 - Fair Full-Access Baseline Included From The Start

The baseline matrix must include at minimum:

- `full_access_lookup_baseline`;
- nearest-neighbor baseline over full observation/action keys;
- graph-cache transition table baseline;
- graph-cache successor map baseline;
- episodic traversal baseline;
- FSM planner baseline;
- observation-only baseline;
- action-independent baseline;
- static-action baseline;
- replay-hash-only baseline;
- candidate-self-consistency baseline.

The strongest baseline must be selected after execution. A weaker graph-cache
baseline must not be treated as strongest if full-access lookup ties or beats
it.

Every baseline must run through the same harness-owned score path as the
candidate and must record producer function, input artifacts, run id,
seed/context/episode ids, aggregation rule, and code path hash.

## G4 - B3 Bands Preserved

Baseline comparison must preserve these bands:

| Band | Rule | Meaning |
| --- | --- | --- |
| equivalence | `< 0.02` | `baseline_equivalent`, blocker |
| inconclusive | `[0.02, 0.05)` | blocks admission and implementation claims |
| mechanism-relevant effect candidate | `>= 0.05` | still not mechanism proof |

`baseline_equivalent` is a blocker, not pass.

`mechanism_relevant_effect_candidate` is still not ACP-BV mechanism proof,
Gate evidence, admission readiness, bridge readiness, runtime readiness, or
mainline effect.

Post-hoc threshold tuning after seeing candidate, baseline, ablation, leakage,
or replay results is forbidden.

## G5 - Solvability Without Leakage

001B must include an independent solvability preflight before candidate
admission or mechanism claims are possible.

The preflight must execute:

- oracle with allowed observations only;
- fair full-access lookup baseline;
- graph-cache family;
- leakage scanner with at least one positive-control case;
- heldout key overlap detector;
- candidate/truth coupling detector.

Block rules:

- If no allowed-observation oracle can exceed the strongest fair baseline, the
  distribution is not usable.
- If only a leaking oracle can exceed baseline, the distribution is invalid.
- If the leakage scanner lacks a positive-control case, the preflight cannot
  support evidence claims.

The solvability oracle must use only candidate-legal observations and
candidate-legal historical state. It must not read hidden truth, expected
labels, expected scores, verdict fields, file names that encode answers, or
candidate-authored truth aliases.

## G6 - Memory-Resistance Mechanism

001B must include at least one principled memory-resistance mechanism from the
following list or an independently audited equivalent:

- heldout latent recombination;
- compositional generalization over unseen topology/risk/action combinations;
- stochastic but seed-controlled transition dynamics with hidden state not
  directly copyable from train keys;
- counterfactual action queries requiring prediction under unseen action
  consequences;
- distribution shift where superficial key lookup fails but model-based
  state/action prediction can still solve.

The mechanism must target lookup and memorization specifically. Adding random
noise, renaming IDs, increasing fixture count, or changing labels without a
testable generalization structure is not sufficient.

The spec for the chosen mechanism must name:

- train support;
- heldout support;
- latent variables;
- candidate-visible variables;
- hidden variables;
- action-conditioned variables;
- expected failure mode for full-access lookup;
- expected success path for the allowed-observation oracle.

## G7 - No Candidate-Authored Truth

Truth generation, difficulty selection, counterfactual action-query selection,
scoring, thresholding, baseline construction, and verdict classification must
remain repo-owned and candidate-inaccessible.

The following candidate-authored fields must not influence truth, difficulty,
generator selection, thresholding, metric producer selection, baseline
construction, or verdicts:

- `policy_map`;
- labels;
- logits;
- confidence;
- score;
- verdict;
- serialized state;
- producer function;
- baseline result;
- ablation result;
- leakage result;
- replay result.

Candidate action may condition which environment transition is scored. It may
not author the truth used to score that transition.

## G8 - Source Boundary And Source-Pin Carryover

001B must carry over the repaired source-boundary requirements from 001A:

- `verify_callable_source_boundary`;
- git-object frozen source-pin anchor;
- tamper-after-anchor negative control;
- no self-declared ownership;
- no live-regenerated manifest trust.

The future source-boundary verifier must derive repo ownership and
candidate-inaccessibility from resolved source paths, source hashes, source
roots, candidate-writable roots, artifact roots, realpath handling, import
resolution, and candidate configuration influence checks.

It must not accept fields such as:

- `repo_source_owned: true`;
- `candidate_inaccessible: true`;
- `trusted_source: true`;
- `source_owned_by_harness: true`.

## Anti-Zeno Rule

ACP-BV 001B gets one redesign attempt.

If 001B again collapses to fair full-access lookup equivalence,
candidate/truth formula coupling, or a non-discriminative distribution, close
or downgrade the ACP-BV current surface family rather than continuing into
001C/001D repairs.

The allowed route after a second collapse is:

```text
close_or_downgrade_current_acp_bv_surface_family
```

The forbidden route after a second collapse is:

```text
repair_into_pass_shaped_success
```

## Acceptance For Future 001B Design

An executable ACP-BV 001B task card may be drafted only after independent audit
confirms that this spec includes:

- true heldout generalization;
- fair full-access lookup baseline from the start;
- strongest-baseline selection after execution;
- candidate/truth formula-coupling prevention;
- B3 bands;
- independent solvability preflight;
- memory-resistance mechanism targeting lookup;
- no candidate-authored truth;
- source-boundary and git-object source-pin carryover;
- one-redesign Anti-Zeno rule.

This spec does not authorize implementation by itself.

## What This Does Not Prove

This spec does not prove ACP-BV validity, ACP-BV mechanism validity, harness
validity, Gate validity, admission readiness, bridge readiness, runtime
readiness, mainline effect, agency evidence, consciousness, real emotion,
autonomy, stable user benefit, or EGO readiness.
