# ACP-BV Distribution Redesign Spec 001B

Task id: `ACP-BV-DISTRIBUTION-REDESIGN-SPEC-001B`

Spec status: revised for targeted independent hostile re-audit only.

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

Next minimal closed-loop action: targeted independent hostile re-audit of R1-R5.
Do not
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

## G1 - True Heldout Generalization, Novelty Floor, And Baseline Tie Block

Heldout episodes must contain keys, configurations, or latent combinations not
present in training.

The future harness must persist a novelty and memory-equivalence detector with:

- train key set;
- heldout key set;
- train key count;
- heldout key count;
- exact-key overlap count;
- exact-key overlap ratio;
- unseen heldout count;
- unseen heldout ratio;
- factorized/per-component seen ratio;
- novelty-floor threshold;
- whether novelty floor is met;
- whether any fair memory, lookup, or nearest-neighbor baseline ties the
  candidate under the B3 equivalence band;
- B3 classification.

The default predeclared novelty minimum is:

- `unseen_heldout_ratio >= 0.40`;
- `unseen_heldout_count >= max(8, ceil(0.40 * heldout_key_count))`;
- for every predeclared factorization family, at least `0.25` of score-bearing
  heldout episodes must contain an unseen component or unseen component tuple;
- no more than `0.75` of score-bearing heldout episodes may be complete under
  factorized/per-component train support.

A future implementation task card may only strengthen this novelty floor. It
must not weaken these thresholds after seeing candidate, baseline, ablation,
leakage, or replay results.

The novelty rule must prevent thin-tail distributions where most heldout
episodes remain lookup-complete and only one or two episodes create an apparent
delta.

Required block rules:

```text
if novelty_floor_met is false:
    verdict = blocked_by_insufficient_heldout_novelty

if strongest_fair_memory_lookup_or_nn_baseline ties candidate under B3 equivalence:
    verdict = blocked_by_baseline_equivalence
```

The baseline-equivalence blocker is not conditional on
`exact_key_overlap_ratio == 1.0`. If the strongest fair memory, lookup, or
nearest-neighbor baseline ties the candidate under the B3 equivalence band, the
result is `blocked_by_baseline_equivalence` even when exact train/heldout
overlap is lower than `1.0`.

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
- factorized lookup baseline;
- per-component nearest-neighbor lookup baseline;
- partial-key lookup baseline;
- topology-only lookup baseline;
- risk-only lookup baseline;
- signal-action lookup baseline;
- action-conditioned nearest-neighbor lookup baseline;
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

The strongest-baseline selector must be predeclared as `argmax(score)` over all
executed fair baselines, with deterministic tie handling that preserves the
most damaging fair baseline classification rather than choosing a more
favorable narrative baseline.

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

Any `mechanism_relevant_effect_candidate` classification must be reproduced
across predeclared seeds. A delta of `>= 0.05` on one small episode set is
insufficient.

Minimum multi-seed requirement:

- minimum seed count: `5`;
- default seed list if no stronger task card rule is declared:
  `[1009, 2027, 3037, 4049, 5051]`;
- aggregation method: compute per-seed candidate score, strongest fair baseline
  score, and delta, then report mean delta, median delta, standard deviation,
  and a bootstrap confidence interval or predeclared equivalent dispersion
  estimate;
- minimum stable effect requirement: mean delta `>= 0.05`, median delta
  `>= 0.05`, at least `4/5` seeds have delta `>= 0.05`, no seed is
  `baseline_equivalent`, and the lower dispersion bound remains outside the
  equivalence band;
- episode-budget noise rule: if the observed effect falls inside the
  predeclared sampling-noise estimate, classify as `inconclusive` or stop with
  `blocked_by_unstable_or_noise_level_effect`.

The future harness must persist:

- seed list or seed-generation rule;
- per-seed candidate score;
- per-seed strongest baseline score;
- per-seed delta;
- per-seed B3 classification;
- mean delta;
- dispersion or confidence interval;
- minimum stable effect requirement;
- whether the effect is outside episode-budget sampling noise.

## G5 - Solvability Without Leakage

001B must include an independent solvability preflight before candidate
admission or mechanism claims are possible.

The preflight must execute:

- oracle with allowed observations only;
- fair full-access lookup baseline;
- graph-cache family;
- leakage scanner with the required positive-control panel;
- heldout key overlap detector;
- candidate/truth coupling detector.

Block rules:

- If no allowed-observation oracle can exceed the strongest fair baseline, the
  distribution is not usable.
- If only a leaking oracle can exceed baseline, the distribution is invalid.
- If the leakage scanner lacks the required positive-control panel, the
  preflight cannot support evidence claims.

The solvability oracle must use only candidate-legal observations and
candidate-legal historical state. It must not read hidden truth, expected
labels, expected scores, verdict fields, file names that encode answers, or
candidate-authored truth aliases.

The leakage positive-control panel must include at minimum:

1. observation-name leakage;
2. action-name leakage;
3. filename leakage;
4. fixture-name leakage;
5. candidate-authored alias leakage;
6. future-observation leakage;
7. hidden truth label leakage;
8. answer-encoding metadata leakage.

Each leakage control must persist:

- control name;
- injected leakage path;
- scanner entrypoint;
- expected detection;
- actual detection;
- block reason;
- run id;
- source hash;
- artifact path.

The scanner must be fail-able and must not pass by whitelist-only detection.

Required block rules:

```text
if any_required_leakage_positive_control_is_missed:
    verdict = blocked_by_non_fail_able_leakage_scanner

if scanner_depends_on_fixed_whitelist_names_and_misses_structural_variants:
    verdict = blocked_by_whitelist_leakage_scanner
```

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

The memory-resistance mechanism must defeat not only exact-key lookup, but
also:

- factorized lookup;
- per-component nearest-neighbor lookup;
- partial-key lookup;
- topology-only lookup;
- risk-only lookup;
- signal-action lookup;
- action-conditioned nearest-neighbor lookup.

Low-cardinality factored keys such as `(signal, topology, risk, action)` can be
memorized compositionally even when exact full keys are unseen. Exact-key
novelty alone is therefore insufficient.

The spec for the chosen mechanism must name:

- train support;
- heldout support;
- latent variables;
- candidate-visible variables;
- hidden variables;
- action-conditioned variables;
- expected failure mode for full-access lookup;
- expected failure mode for factorized/per-component lookup;
- expected failure mode for nearest-neighbor lookup;
- expected success path for the allowed-observation oracle.

A valid 001B design must explain:

1. why exact-key lookup fails;
2. why factorized/per-component lookup fails;
3. why nearest-neighbor lookup fails;
4. why the allowed-observation oracle remains solvable without leakage.

If the selected memory-resistance mechanism cannot beat factorized or
per-component lookup, stop with:

```text
blocked_by_factorized_lookup_equivalence
```

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

ACP-BV 001A's baseline-equivalence closure is the first collapse for this
surface family. Any 001B collapse is therefore the second collapse for this
surface family.

Collapse must be bound to operational detector outputs, not narrative judgment.
Collapse is any of:

- `baseline_equivalent`;
- `blocked_by_baseline_equivalence`;
- `blocked_by_factorized_lookup_equivalence`;
- `blocked_by_candidate_truth_coupling`;
- `oracle_like_reference_candidate_scaffolding_only` used as evidence;
- `blocked_by_non_discriminative_distribution`;
- `blocked_by_solvability_preflight_failure`;
- `blocked_by_unsolvable_or_leaky_distribution`.

If 001B triggers any collapse condition, the required output is:

```text
close_or_downgrade_current_acp_bv_surface_family
```

After a second collapse, 001C/001D repair tasks are forbidden. The required
closure artifact is:

```text
artifacts/acp_bv_001b_collapse_closure_*/result.json
```

It must include:

- collapse trigger;
- detector output;
- source artifact path;
- reason for closure/downgrade;
- claim ceiling;
- next route recommendation.

The allowed route after a detector-bound collapse is:

```text
close_or_downgrade_current_acp_bv_surface_family
```

The forbidden route after a second collapse is:

```text
repair_into_pass_shaped_success
```

## R6 - Recommended Defense-In-Depth

The following defenses are recommended but nonblocking for the redesign spec
itself:

1. candidate-vs-truth behavioral equivalence probe on heldout probe cases;
2. predeclared strongest-baseline selector as `argmax(score)` over executed
   fair baselines;
3. namespace clarification distinguishing prior ACP-BV surface-spec 001B from
   distribution-redesign spec 001B.

If any R6 item is deferred in a future implementation task card, the deferral
must be explicit and must not weaken R1-R5.

## Acceptance For Future 001B Design

An executable ACP-BV 001B task card may be drafted only after independent audit
confirms that this spec includes:

- true heldout generalization;
- predeclared novelty floor with persisted heldout novelty evidence;
- baseline-equivalence blocker that applies whenever the strongest fair memory,
  lookup, or nearest-neighbor baseline ties the candidate under the B3
  equivalence band, regardless of exact overlap ratio;
- fair full-access lookup baseline from the start;
- factorized, per-component, partial-key, topology-only, risk-only,
  signal-action, and action-conditioned nearest-neighbor lookup challengers;
- strongest-baseline selection after execution;
- candidate/truth formula-coupling prevention;
- B3 bands;
- multi-seed stability and episode-budget noise handling before any
  `mechanism_relevant_effect_candidate` classification;
- independent solvability preflight;
- leakage positive-control panel with fail-able, non-whitelist-only scanner
  behavior;
- memory-resistance mechanism targeting lookup;
- no candidate-authored truth;
- source-boundary and git-object source-pin carryover;
- detector-bound Anti-Zeno closure rule;
- R6 defense-in-depth either included or explicitly deferred.

This spec does not authorize implementation by itself.

## What This Does Not Prove

This spec does not prove ACP-BV validity, ACP-BV mechanism validity, harness
validity, Gate validity, admission readiness, bridge readiness, runtime
readiness, mainline effect, agency evidence, consciousness, real emotion,
autonomy, stable user benefit, or EGO readiness.
