# ROUTE-C-CANDIDATE-IMPLEMENTATION-CARD-001A-R1

Future Route C candidate executable-harness contract, revised after independent
hostile audit of `ROUTE-C-CANDIDATE-IMPLEMENTATION-CARD-001A`.

Date drafted: 2026-06-16

## 0. Status And Authorization Boundary

- Card status: revised future implementation-card draft only.
- Current-task implementation authorized: false.
- Candidate source code authorized by this revision task: false.
- Tests authorized by this revision task: false.
- Gate/mainline/runtime/live integration authorized: false.
- Push/tag/remote-anchor authorized: false.
- Auto-Remote-Anchor: forbidden.

This R1 card defines the contract a future separately authorized implementation
task would have to satisfy. This document does not implement the candidate and
does not by itself authorize implementation.

## 1. Problem Definition

`ROUTE-C-CANDIDATE-IMPLEMENTATION-CARD-001A` received the independent hostile
audit verdict:

`requires_implementation_card_revision_before_candidate_implementation`

The bounded problem is to repair the implementation-card contract so that any
future Route C candidate harness is forced to carry through:

- demonstrated failing negative controls for the candidate-vs-baseline margin
  gate and saturation gate;
- access parity between the candidate and strongest fair interventional
  baseline;
- hardened independent pre-run source-pin provenance;
- a co-forged-anchor positive control;
- explicit truth-seed disjointness.

This R1 card does not test Route C and does not claim the candidate will work.

## 2. Current Stage / Layer

- Current document layer:
  `engineering-governance / implementation-card audit preservation + R1 revision only`.
- Future task layer if separately authorized:
  `engineering implementation / bounded offline mechanism-proxy testing`.

The future task would still have a bounded mechanism-hypothesis claim ceiling,
not a subjectivity, agency, consciousness, runtime, or EGO-readiness claim.

## 3. Lineage Note

Prior `CLAUDE-INDEPENDENT-DRAFT-ROUTE-C-CANDIDATE-CARD-001A-AUDIT-001A` and
`CLAUDE-INDEPENDENT-DRAFT-ROUTE-C-CANDIDATE-CARD-001A-R1-REAUDIT-001A` were
preservation of operator-provided pasted audit text, not Codex independent
re-audit.

The hostile audit preserved as
`CLAUDE-INDEPENDENT-ROUTE-C-CANDIDATE-IMPLEMENTATION-CARD-001A-AUDIT-001A` is
treated as the first independent in-repo audit of
`ROUTE-C-CANDIDATE-IMPLEMENTATION-CARD-001A`.

## 4. Mainline Target

None.

Future implementation, if separately authorized, must remain an isolated offline
harness. It must not target EGO mainline, Gate admission, runtime, bridge,
scheduler, product/admission, UI, deployment, LLM integration, AIRI integration,
or live user-facing behavior.

## 5. Mainline Integration Status

None. No mainline path is integrated, enabled, or authorized by this card.

## 6. Enabled-State Requirement

Current revision task: none.

Future implementation task, if separately authorized, may create only an
explicit local offline harness entrypoint and local tests named in that future
authorization. It must not create an enabled Gate runner, mainline route,
runtime route, scheduler route, product/admission route, deployment path, or
live path.

## 7. Real-Trigger Evidence Requirement

Current revision task: local docs/artifacts only.

Future implementation task, if separately authorized, must produce real-trigger
evidence only from the isolated offline harness entrypoint. Required evidence:

- actual candidate run from the local entrypoint;
- actual passive baseline runs;
- actual fair interventional baseline runs;
- actual graph-cache challenger runs;
- actual margin failing negative control run;
- actual saturation failing negative control run;
- actual access-parity computation;
- actual ablation reruns;
- actual leakage positive controls;
- actual forged-provenance and co-forged-anchor positive controls;
- actual truth-seed disjointness assertion;
- actual replay recomputation;
- actual diff-hygiene readback.

No live user trigger, no EGO runtime trigger, and no Gate/mainline trigger may be
claimed.

## 8. Governing Prior Negative Evidence

Future implementation must read and cite these local sources before code edits:

- `docs/research/ACSB-CURRENT-ROUTE-DOWNGRADE-CLOSURE-001A.md`
- `docs/research/CLAUDE-INDEPENDENT-ACOLB-A-ROUTE-DECISION-AND-ROUTE-C-DESIGN-AUDIT-001A.md`
- `docs/research/CLAUDE-INDEPENDENT-ROUTE-C-PREFLIGHT-001A-HOSTILE-AUDIT-001A.md`
- `docs/research/CLAUDE-INDEPENDENT-ROUTE-C-PREFLIGHT-001A-REPAIR-REAUDIT-001A.md`
- `docs/research/CLAUDE-INDEPENDENT-DRAFT-ROUTE-C-CANDIDATE-CARD-001A-AUDIT-001A.md`
- `docs/research/DRAFT-ROUTE-C-CANDIDATE-CARD-001A-R1.md`
- `docs/research/CLAUDE-INDEPENDENT-DRAFT-ROUTE-C-CANDIDATE-CARD-001A-R1-REAUDIT-001A.md`
- `docs/research/CLAUDE-INDEPENDENT-ROUTE-C-CANDIDATE-IMPLEMENTATION-CARD-001A-AUDIT-001A.md`
- `docs/decision_log.md`

Minimum inherited route consequences:

- ACSB current route downgrade remains a governance/evidence-hygiene boundary,
  not a mechanism pass.
- ACOLB-A remains closed as bounded local negative fair-baseline /
  amortization-saturation evidence.
- Route C Phase 0 hostile audit proved observation-baseline underpowering was a
  real blocker before repair.
- Route C repaired Phase 0 re-audit accepted candidate-card drafting only, with
  F-forge provenance caveat and deferred fair-interventional saturation risk.
- The first candidate-card audit required R1 revision before implementation
  authorization.
- The R1 re-audit authorized implementation-card drafting only.
- The first implementation-card hostile audit required R1 revision before
  candidate implementation.
- Candidate implementation, Gate execution, mainline wiring, push, tag, and
  remote anchor remain forbidden unless a later task explicitly authorizes them.

## 9. Bounded Deep-Audit Card

- Real objective: decide whether a future Route C candidate can show bounded
  offline evidence beyond passive decoding and fair interventional baselines.
- Problem-definition risk: the surface may still be solved by ordinary
  interventional causal discovery, lookup/cache behavior, passive leakage, or a
  fair baseline once access parity is enforced.
- Strongest baseline explanation: a non-candidate baseline with equal access,
  the same legal interventions, and the same predeclared mechanism component can
  match the candidate.
- Strongest invalidating reason: candidate advantage appears only because the
  fair baseline is feature-impoverished, access-impoverished, graph-cache
  challengers are omitted, provenance is self-declared, replay is tautological,
  truth seeds leak, or margins are tuned post hoc.
- Falsifier: strongest fair interventional baseline equals, exceeds, or
  approaches candidate within frozen margin.
- Still-insufficient evidence: both candidate and baseline score high;
  stored-hash replay; clean report without positive controls; literal JSON
  scores; access parity not proven; any unused frozen seed, train context,
  heldout context, or counterfactual pair.
- Mechanism-vs-behavior classification: future task can test only bounded
  mechanism-proxy non-equivalence; it cannot prove subjectivity, agency,
  consciousness, or EGO readiness.
- Minimal validation: a future implementation must run callable producers for
  candidate, baselines, failing negative controls, access parity, ablations,
  provenance controls, leakage controls, truth-seed disjointness, and replay.
- Stop condition: any non-fail-able material gate, access parity failure,
  source-pin weakness, truth-seed overlap, baseline saturation, unauthorized
  path change, secret exposure, or claim inflation stops the task.
- Rollback plan: revert forbidden changes, preserve blocker evidence, and do not
  repair negative results into pass-shaped outputs.
- Acceptance signal: all required gates are callable, fail-able, provenance
  backed, access-parity checked, and negative controls demonstrate closure
  behavior before any bounded candidate evidence is claimed.

## 10. Hypothesis

A future separately authorized Route C candidate may test a bounded
self-boundary / hidden-self-set inference proxy only if it beats both:

1. `obs_only_family_max`, computed over the full passive-family union; and
2. `fair_interventional_family_max`, computed over the strongest fair
   interventional baseline family,

under predeclared hashed margins and while surviving provenance, replay,
leakage, ablation, access-parity, margin, saturation, truth-seed, and
diff-hygiene gates.

This card does not test the hypothesis.

## 11. Strongest Passive Baseline

Future implementation must include the passive family as a superset of accepted
Phase 0. None of these attackers may be removed or weakened:

- `positional_first_k`
- `mean`
- `variance`
- `correlation`
- `pca_subspace`
- `cross_episode`
- `supervised`
- `legal_field_membership`

Additional passive attackers may be added only by union.

Required aggregation:

`obs_only_family_max = max(score(attacker) for attacker in passive_family_union)`

If any passive attacker exceeds the predeclared observation-only premise limit,
the future run must close or downgrade. It must not patch the surface after
seeing the result.

## 12. Strongest Fair Interventional Baseline

Future implementation must include all of the following:

- random legal intervention policy.
- greedy information-gain policy.
- exhaustive legal query policy within same budget.
- Bayesian / likelihood updater if applicable.
- lookup-capable interventional imitation baseline.
- direct-objective optimizer using all legal non-candidate mechanisms.
- `graph_lookup`.
- `transition_table`.
- `successor_map`.
- `count_table`.
- `fsm_planner`.
- `episodic_traversal`.

All must enter the saturation judgment.

Required aggregation:

`fair_interventional_family_max = max(score(baseline) for baseline in fair_interventional_family)`

## 13. Access-Parity Gate

Future implementation must produce the mandatory artifact:

`access_parity_report.json`

It must compare the candidate against the strongest fair interventional baseline
on at least:

- intervention budget;
- API access;
- observation access;
- action space;
- state access;
- update access;
- history access;
- query budget;
- cache/memory access;
- serialized-state access;
- evaluator/oracle exclusion.

Access parity must be computed before candidate advantage is accepted. If access
parity fails, candidate advantage is invalid and the run must return
`close_or_downgrade` or be marked invalid. Feature-impoverishment control does
not replace access parity; it is a separate control.

The saturation judgment and final report must cite
`access_parity_report.json`. A saturation judgment without access parity is
void.

## 14. Global Material-Gate Failability Rule

Every material gate must ship a demonstrated failing negative control.

A gate without demonstrated failability is void and cannot support candidate
evidence.

This rule applies at minimum to:

- candidate-vs-baseline margin decision;
- saturation decision;
- access-parity decision;
- provenance gate;
- leakage gate;
- replay recomputation gate;
- ablation gate;
- truth-seed disjointness gate;
- final verdict selection.

## 15. Candidate-Vs-Baseline Margin Gate

Future candidate must beat both:

- `obs_only_family_max`; and
- `fair_interventional_family_max`,

under predeclared, hashed margin values.

Frozen margin values must be created before any candidate run. Post-hoc
threshold adjustment is forbidden.

Required demonstrated failing negative control:

- create a synthetic candidate that fails the frozen candidate-vs-baseline
  margin;
- run the same callable margin gate on that synthetic candidate;
- the margin gate must return `close_or_downgrade`;
- the control must be a callable demonstrated control, not a label, fixture
  name, static verdict dictionary, or self-report.

If strongest fair interventional baseline equals, exceeds, or approaches
candidate within frozen margin, the verdict is:

`close_or_downgrade`

Both-scored-high is not success.

## 16. Saturation STOP Gate

The future implementation must include a saturation STOP gate:

- if `fair_interventional_family_max >= candidate_score`, close or downgrade;
- if `candidate_score - fair_interventional_family_max <= frozen_saturation_margin`, close or downgrade;
- if all systems score high but the margin is inside the frozen equivalence
  band, close or downgrade;
- if fair baseline saturation is caused by a graph-cache challenger, preserve
  the challenger and close or downgrade.

Required demonstrated failing negative control:

- create a synthetic run where the strongest fair interventional baseline
  saturates candidate performance within the frozen margin;
- include graph-cache challengers in the saturation case;
- run the same callable saturation gate on that synthetic run;
- the saturation gate must return `close_or_downgrade`;
- the control must be a callable demonstrated control, not a label, fixture
  name, static verdict dictionary, or self-report.

The saturation STOP gate must consume `access_parity_report.json`. If access
parity fails or is absent, the saturation judgment cannot support candidate
advantage and the run must return `close_or_downgrade` or invalid.

The STOP result is bounded negative evidence, not a failed implementation to
repair into pass.

## 17. RF-1: Forged-Provenance Option-2 Closure

Definition:

An independent source artifact is a pre-run frozen, source-pinned,
independently hashed artifact created before any candidate or baseline run,
outside candidate source, and referenced by immutable hash in the material row.

Future implementation must require:

- pre-run frozen source pins;
- source artifact hashes fixed before run;
- recorded inputs tied to those pre-run frozen pins;
- rederived-basis path admissible only when recorded inputs are tied to
  independent pre-run frozen pins;
- self-declared input/basis consistency is insufficient.

Required positive control:

- `co_forged_anchor_positive_control.json`

The co-forged-anchor positive control must attempt to forge or alias:

- recorded inputs;
- value;
- basis;
- source artifact reference;
- source artifact hash or alias path.

The provenance gate must fail closed under this co-forged-anchor attack. Weak
forged value/basis controls alone are insufficient.

Every material row must either:

1. re-execute the producer on recorded, source-pinned inputs and compare output
   to recorded value; or
2. rederive basis from source-pinned inputs and prove the source-pinned inputs
   were not co-forged.

Candidate-run material rows are in scope. This cannot be deferred to Gate level.

## 18. RF-2: Pre-Run Mechanism-Component Lock

The mechanism component under test must be specified before any candidate run.

Required lock artifacts:

- `mechanism_component_spec.md`
- `mechanism_component_lock.json`
- `mechanism_component_lock.sha256`

The component must be minimal, independently specified outside candidate source,
and hashed before run. Candidate advantage cannot be used after the fact to
define the mechanism component.

Feature-impoverishment control must use this pre-hashed component. If granting
this component to the fair baseline does not allow it to approach candidate
performance, the baseline is deemed unfair/impoverished and the run is invalid.

Feature-impoverishment control is not a substitute for access parity.

## 19. RF-3: Independent Anchoring Of B1-B5 / N1-N4

Future implementation must independently read back and bind:

- B1 F-forge closure, including co-forged-anchor positive control.
- B2 Phase 0 passive-family superset.
- B3 fair-interventional baseline hardening, including mandatory
  `access_parity_report.json`.
- B4 margin/saturation failability, including demonstrated margin and
  saturation failing negative controls.
- B5 six graph-cache challengers.
- N1 prior negatives.
- N2 frozen margin predeclaration/hash.
- N3 replay tautology exclusion.
- N4 truth-seed isolation, including `truth_seed_disjointness_report.json`.

It must not rely only on preserved audit artifacts or self-reported
`result.json` status.

## 20. RF-4: Future Implementation Diff Hygiene

Future implementation must produce git-verifiable diff evidence.

Required diff artifacts:

- `diff_name_status.txt`
- `diff_stat.txt`
- `forbidden_path_scan.json`
- `changed_file_classification.json`
- `git_status_before.txt`
- `git_status_after.txt`

The future result must prove exactly which files changed and separately prove
whether any of these were touched:

- `src/**`
- `tests/**`
- `scripts/**`
- Gate runner files.
- mainline files.
- runtime files.
- scheduler files.
- bridge files.
- product/admission files.
- credential or push scripts.

Push, tag, and remote anchor remain forbidden while PAT hygiene is unresolved.

## 21. Ablation Plan

Future implementation must run real rerun ablations, not report edits:

- remove mechanism-specific state.
- remove interventional access.
- remove update path.
- remove replay state.
- remove candidate memory/cache.
- remove self-boundary-specific feature.
- shuffle target labels.
- swap twin pairs where passive distribution is held constant.
- remove candidate-only fields.
- replace candidate policy with strongest fair baseline policy.

Every ablation must record callable invocation provenance and must rerun
episodes under real interventions.

## 22. Trace / Replay Plan

Replay must recompute candidate behavior from serialized state plus legal
observation/action history.

Stored-hash comparison alone is insufficient. Tautological replay controls do
not count toward failability.

Required replay artifacts:

- `trace.jsonl`
- `serialized_state_snapshot.json`
- `replay_recompute_report.json`
- `replay_mutation_positive_control.json`

Replay must fail closed if it reads truth labels, evaluator-only fields,
candidate-invisible aliases, future observations, or stored verdict values.

## 23. Truth-Seed Isolation

Future implementation must explicitly prove truth-seed disjointness.

Required artifact:

`truth_seed_disjointness_report.json`

The report must assert and prove that:

- truth/self-set seed is disjoint from all candidate observation seeds;
- truth/self-set seed is disjoint from all baseline observation seeds;
- truth/self-set seed is disjoint from intervention-policy seeds;
- truth/self-set seed is disjoint from replay/counterfactual seeds if those are
  visible to candidate or baseline.

If disjointness cannot be proven, the run is invalid. A truth-seed contamination
positive control is still required; it does not replace disjointness proof.

## 24. Leakage Plan

Future implementation must include fail-able positive controls for:

- value-level passive leakage.
- schema/name/key leakage.
- order leakage.
- action/API leakage.
- serialized-state leakage.
- result-json leakage.
- candidate-only-field leakage.
- train/heldout contamination.
- truth-seed contamination.
- unused frozen seed.

Each leakage positive control must be a callable scanner/probe that demonstrably
detects the injected leak. A clean report without positive controls is invalid.

## 25. Computed-Evidence Provenance Gate

No mechanism score may come from literals, static dictionaries, self-report,
unconditional clean reports, or hand-filled JSON.

Every material score must include:

- `producer_function`
- `source_path`
- `recorded_inputs`
- `source_pinned_input_artifact_hash`
- `run_id`
- `seed`
- `context_id`
- `episode_id`
- `aggregation`
- `code_path_hash`
- `recompute_command`
- `output_artifact`

Material rows include:

- candidate score.
- passive baseline scores.
- `obs_only_family_max`.
- fair interventional baseline scores.
- graph-cache challenger scores.
- `access_parity_report.json`.
- margin decision.
- demonstrated margin failing negative control.
- saturation decision.
- demonstrated saturation failing negative control.
- ablation scores.
- replay recomputation.
- `truth_seed_disjointness_report.json`.
- leakage scan.
- leakage positive controls.
- forged-provenance controls.
- `co_forged_anchor_positive_control.json`.
- final verdict selection.

Every material row must reference the independent pre-run frozen source artifact
hash or must be rejected as unsupported.

## 26. Source Pins And Frozen Inputs

Future implementation must predeclare and hash:

- margin values.
- saturation margin values.
- access-parity rule source.
- access-parity input artifacts.
- mechanism component spec.
- generator source.
- candidate source.
- baseline source.
- graph-cache challenger source.
- ablation source.
- leakage scanner source.
- replay source.
- truth-seed disjointness source.
- train contexts.
- heldout contexts.
- truth/self-set seeds.
- candidate observation seeds.
- baseline observation seeds.
- intervention-policy seeds.
- replay/counterfactual seeds visible to candidate or baseline.
- counterfactual pairs.
- source artifacts used for recorded inputs, value, and basis rows.

Source artifact hashes must be fixed before run. Recorded inputs must be tied to
those pre-run frozen pins. The rederived-basis path is admissible only when
recorded inputs are tied to independent pre-run frozen pins.

`access_parity_report.json`, `truth_seed_disjointness_report.json`,
`co_forged_anchor_positive_control.json`, demonstrated margin failing control,
and demonstrated saturation failing control must all be included in the
artifact-hash/source-pin readback.

Any unused frozen seed, train context, heldout context, or counterfactual pair
blocks the evidence claim.

## 27. Required Future Artifact Set

Unless a later task card narrows this with explicit justification, future
implementation must produce:

- `result.json`
- `trace.jsonl`
- `baseline_comparison.json`
- `access_parity_report.json`
- `ablation_report.json`
- `replay_report.json`
- `replay_recompute_report.json`
- `truth_seed_disjointness_report.json`
- `margin_failing_negative_control.json`
- `saturation_failing_negative_control.json`
- `co_forged_anchor_positive_control.json`
- `leakage_positive_controls.json`
- `source_pin_report.json`
- `material_rows.jsonl`
- `failure_manifest.json` if anything fails
- `claim_ceiling.txt` or a claim-ceiling field inside `result.json`

No artifact = no evidence.

## 28. Acceptance Gate For Future Implementation

A future implementation may be accepted only if all are true:

- prior negative evidence readback is present.
- RF-1 through RF-4 pass.
- B1-B5 and N1-N4 are independently bound in card text and result artifacts.
- `access_parity_report.json` is produced and proves candidate/baseline access
  parity across the required dimensions.
- if access parity fails, candidate advantage is invalid and the run returns
  `close_or_downgrade` or invalid.
- candidate score is computed by callable producer.
- all passive baselines are invoked.
- `obs_only_family_max` is computed over the full union.
- all fair interventional baselines are invoked.
- all six graph-cache challengers enter saturation judgment.
- margins were frozen and hashed before run.
- demonstrated margin failing negative control returns `close_or_downgrade`.
- demonstrated saturation failing negative control returns `close_or_downgrade`
  and includes graph-cache challengers.
- every material gate has demonstrated failability.
- strongest fair interventional baseline does not equal, exceed, or approach
  candidate within frozen margin.
- saturation judgment consumes `access_parity_report.json`.
- all required ablations are real reruns.
- replay recomputes behavior from serialized state plus legal history.
- `truth_seed_disjointness_report.json` proves the required seed disjointness.
- leakage positive controls detect injected leaks.
- independent source artifact is pre-run frozen, source-pinned, independently
  hashed, outside candidate source, and referenced by immutable hash.
- recorded inputs are tied to independent pre-run frozen source pins.
- rederived-basis path is admitted only when recorded inputs are tied to
  independent pre-run frozen source pins.
- co-forged-anchor positive control fails closed against forged or aliased
  recorded inputs, value, basis, source artifact reference, and source artifact
  hash or alias path.
- diff hygiene proves the exact changed-file set.
- no Gate/mainline/runtime/live path is touched.
- no push/tag/remote anchor is attempted.
- no PAT or secret is printed, copied, exposed, or modified.
- final report cites `access_parity_report.json`,
  `truth_seed_disjointness_report.json`, both demonstrated failing controls, and
  the co-forged-anchor positive control.

## 29. Stop Condition

Stop immediately and preserve a blocker if:

- candidate implementation is attempted without a separate explicit operator
  authorization after this card.
- future implementation weakens RF-1 through RF-4.
- future implementation omits any B1-B5 or N1-N4 requirement.
- any material gate lacks a demonstrated failing negative control.
- demonstrated margin failing negative control does not return
  `close_or_downgrade`.
- demonstrated saturation failing negative control does not return
  `close_or_downgrade`.
- `access_parity_report.json` is absent.
- access parity fails or cannot be proven.
- saturation judgment does not consume `access_parity_report.json`.
- independent source artifact is not pre-run frozen, source-pinned,
  independently hashed, outside candidate source, and referenced by immutable
  hash.
- recorded inputs are not tied to independent pre-run frozen source pins.
- co-forged-anchor positive control is absent or does not attack the source
  artifact reference/hash/alias path.
- truth-seed disjointness cannot be proven.
- `truth_seed_disjointness_report.json` is absent.
- any passive Phase 0 attacker is removed or weakened.
- any required fair interventional baseline is omitted.
- any graph-cache challenger is omitted.
- any margin is changed after seeing results.
- a fair interventional baseline saturates the candidate.
- replay is only stored-hash comparison.
- provenance relies on self-declared basis consistency.
- any source/test/runtime/Gate/mainline path outside future authorization is
  touched.
- push/tag/remote anchor is attempted.
- a PAT or secret is printed, copied, exposed, or modified.
- any result claims Route C works, Gate passed, EGO readiness, agency,
  autonomy, consciousness, emotion, or stable user benefit.

## 30. Rollback Plan

If forbidden files are touched, revert those changes immediately and preserve a
violation note if useful.

If fair baseline saturation occurs, do not tune margins or weaken the baseline.
Preserve the result as bounded negative evidence and close or downgrade Route C.

If access parity, provenance, replay, leakage, ablation, truth-seed, source-pin,
or material-gate failability is missing, stop and return a blocker instead of
repairing the result into a pass.

If candidate code appears before explicit authorization, revert it and record a
violation.

## 31. Expected Future Changed Files

These are conditional future implementation paths only. They are not authorized
by the current revision task.

Preferred future isolated paths, if separately authorized:

- `src/route_c_candidate_implementation_001a/**`
- `tests/route_c_candidate_implementation_001a/**`
- `artifacts/ROUTE-C-CANDIDATE-IMPLEMENTATION-001A/**`

Future implementation must not modify docs-only governance sources except for
bounded result/readback docs explicitly named in the future authorization.

## 32. Forbidden Changes

Forbidden unless a later authorization explicitly names the exact files:

- EGO mainline runtime.
- UI / companion behavior.
- relationship learning.
- emotion systems.
- proactive behavior.
- LLM integration.
- AIRI integration.
- deployment.
- API keys.
- external services.
- global schema migrations.
- rewriting old artifacts.
- credential or push scripts.
- push, tag, or remote anchor.

## 33. Auto-Remote-Anchor Decision

Auto-Remote-Anchor: forbidden.

This card must not be used to push, tag, or remote-anchor. A future task must
keep push/tag/remote-anchor forbidden while PAT hygiene remains unresolved.

## 34. Commit Decision

This revision task does not authorize a commit. Local commit is allowed only if
explicitly authorized by the operator after scope/readback checks pass.

Future implementation commit policy must be stated by the future operator task.

## 35. R1 Result.json Correction Requirement

The R1 result artifact may report B3, B4, and RF-3 as bound only because this R1
card text contains:

- `access_parity_report.json` as a required artifact;
- demonstrated margin failing negative control;
- demonstrated saturation failing negative control;
- every-material-gate demonstrated failability rule;
- independent pre-run frozen source-pin definition;
- co-forged-anchor positive control;
- explicit truth-seed disjointness.

If any future result omits the text-backed bindings above, it must not mark B3,
B4, or RF-3 as bound.

## 36. Future Final Report Requirements

A future implementation final report must include:

- `access_parity_report.json` result.
- baseline results.
- ablation results.
- replay result.
- demonstrated margin failing negative control result.
- demonstrated saturation failing negative control result.
- co-forged-anchor positive control result.
- truth-seed disjointness result.
- source-pin/provenance result.
- stop conditions triggered.
- claim ceiling.
- what this does not prove.

## 37. Claim Ceiling

Current claim ceiling:

implementation-card audit preservation and R1 revision only.

Future implementation claim ceiling, if separately authorized and executed:

bounded offline executable-harness evidence only. No mechanism validity claim
unless computed evidence supports the exact bounded claim. No Gate pass. No
mainline effect. No runtime/live effect. No agency, autonomy, consciousness,
emotion, stable user benefit, or EGO readiness.

## 38. Next Minimal Closed-Loop Action

Independent hostile audit of `ROUTE-C-CANDIDATE-IMPLEMENTATION-CARD-001A-R1`
before any Route C candidate implementation. Candidate implementation remains
forbidden until a separate future task explicitly authorizes exact
implementation files and scope.

## 39. What This Does Not Prove

This card does not prove Route C mechanism validity, hidden-self-set inference,
self-boundary evidence, candidate success, Gate pass, mainline effect, runtime
readiness, live path, agency, autonomy, consciousness, emotion, stable user
benefit, EGO readiness, or that any prior ACSB/ACOLB artifact was stronger than
its preserved claim ceiling.
