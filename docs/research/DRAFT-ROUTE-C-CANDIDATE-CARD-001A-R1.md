# DRAFT-ROUTE-C-CANDIDATE-CARD-001A-R1

Revised Route C candidate-card contract after preserved Claude read-only audit
`CLAUDE-INDEPENDENT-DRAFT-ROUTE-C-CANDIDATE-CARD-001A-AUDIT-001A`.

Date drafted: 2026-06-16

## 0. Status

- Card status: R1 candidate-card revision only.
- Implementation authorized: false.
- Candidate implementation authorized: false.
- Gate/mainline/runtime/live integration authorized: false.
- Push/tag/remote-anchor authorized: false.
- Auto-Remote-Anchor: forbidden.

This card is not an implementation card. It is a contract that a future,
separately authorized implementation card would have to satisfy before any Route
C candidate code can be written.

## 1. Problem Definition

The prior draft candidate-card was independently audited and received:

`requires_candidate_card_revision_before_implementation_authorization`

The R1 problem is to revise the candidate-card contract so that it closes the
B1-B5 audit blockers while preserving the Route C claim ceiling. The revision
must not create a candidate, Gate runner, runtime path, mainline wiring, source
file, test file, scheduler, bridge, product/admission path, credential script,
push, tag, or remote anchor.

## 2. Current Stage / Layer

`engineering-governance / candidate-card audit preservation + card revision only`

## 3. Mainline Target

None. Route C has no mainline target in this task.

## 4. Mainline Integration Status

None. No Gate, EGO-mainline, runtime, bridge, scheduler, admission, product,
deployment, UI, LLM, AIRI, or live path is touched or authorized.

## 5. Enabled-State Requirement

None. This R1 card must not enable a candidate, CLI candidate, pytest candidate,
Gate runner, runtime path, or live path.

## 6. Real-Trigger Evidence Requirement

For this task, real-trigger evidence is local preservation and documentation
artifact creation only:

- preserved read-only audit document;
- R1 candidate-card contract;
- bounded result artifact and claim ceiling.

No mechanism score, candidate score, Gate score, real-world trigger, or live-path
trigger is produced or admitted.

## 7. Governing Prior Negative Evidence

This R1 card is not allowed to treat Route C as a fresh surface with no history.
It must cite and inherit the following repo-local boundaries.

### 7.1 ACSB Downgrade Closure

Source:
`docs/research/ACSB-CURRENT-ROUTE-DOWNGRADE-CLOSURE-001A.md`

Inherited constraints:

- ACSB current route is downgraded and sealed as an active route.
- ACSB is not mechanism-falsified; it remains untested by a valid `001D`
  harness.
- `001B`, `001C`, and `001D` are invalid-harness / evidence-hygiene lessons,
  not mechanism-negative evidence.
- `001E` is not authorized.
- Future ACSB-family re-entry requires a materially different route-decision
  card with hard preflight gates before implementation.
- The decisive collapse to avoid is oracle / same-step legal-observation target
  decoding, boundary-inert behavior, lookup/static decoder behavior, fake
  learner behavior, and replay that confirms stored conclusions instead of
  recomputing.

### 7.2 ACOLB-A Saturation Closure

Sources:

- `docs/research/CLAUDE-INDEPENDENT-ACOLB-A-ROUTE-DECISION-AND-ROUTE-C-DESIGN-AUDIT-001A.md`
- `docs/decision_log.md`

Inherited constraints:

- ACOLB-A closed as bounded local negative fair-baseline / amortization
  saturation evidence.
- The decisive failure was candidate equivalence to a fair amortized sequential
  estimator on that constructed surface, not graph-cache equivalence.
- Route C must therefore compare candidate behavior against the strongest fair
  interventional baseline, not merely against passive observation-only
  baselines.
- Candidate implementation, Gate run, mainline wiring, push, tag, and remote
  anchor remain unauthorized.

### 7.3 Route C Phase 0 Re-Audit Acceptance

Source:
`docs/research/CLAUDE-INDEPENDENT-ROUTE-C-PREFLIGHT-001A-REPAIR-REAUDIT-001A.md`

Inherited constraints:

- The repaired Phase 0 preflight is accepted only for candidate-card drafting.
- Candidate implementation remains forbidden until a separate Route C
  candidate-card design task is independently audited.
- The F-forge provenance caveat must be closed before any Gate-grade or
  candidate-run evidence claim.
- The deferred section 6.3 fair-interventional saturation risk remains
  load-bearing.

## 8. Hypothesis

Only a future separately authorized implementation may test whether Route C can
distinguish a bounded self-boundary / hidden-self-set inference proxy from
passive and fair-interventional baselines.

This R1 card does not test that hypothesis and does not claim that Route C will
work.

## 9. Strongest Baseline And Strongest False Explanation

The strongest baseline family has two required layers:

1. Passive observation-only family: no weaker than the accepted Phase 0 passive
   family, with additional attackers allowed only by union.
2. Fair interventional family: same access as the candidate except for one
   minimal, predeclared, independently specified mechanism component under test.

The strongest false explanation is that Route C apparent success is ordinary
interventional causal discovery, lookup, graph-cache behavior, passive feature
decoding, schema/name/position leakage, or a feature-impoverished fair baseline.
If any fair baseline with access parity saturates the candidate, the verdict is
`close_or_downgrade`, not pass.

## 10. Passive Baseline Family Superset

A future implementation card must require:

- `passive_family` is a superset of the accepted Phase 0 passive family.
- No accepted Phase 0 passive attacker may be removed or weakened.
- Any new passive attacker is added by union, not substitution.
- `obs_only_family_max = max(score(attacker) for attacker in accepted_phase0_family union new_attackers)`.

The passive family must explicitly include, at minimum:

- `legal_field_membership_attacker`
- `passive_mean_attacker`
- `passive_variance_attacker`
- `passive_correlation_attacker`
- `passive_pca_subspace_attacker`
- `passive_cross_episode_attacker`
- `supervised_passive_feature_attacker`
- `positional_first_k_attacker` or an equivalent positional attacker

If any passive attacker exceeds the frozen observation-only ceiling, the
non-identifiability premise fails and the future run must return
`close_or_downgrade`.

## 11. Interventional Graph-Cache Challenger Family

The fair-interventional saturation panel must include all six graph-cache
challengers:

- `graph_lookup`
- `transition_table`
- `successor_map`
- `count_table`
- `fsm_planner`
- `episodic_traversal`

All six must be invoked through callable producers, recorded in provenance, and
included in the saturation judgment in section 13. Omitting any one challenger
invalidates the run.

## 12. Margin Gate

A future implementation card must predeclare and hash all margin values before
any candidate run, including:

- observation-only ceiling;
- candidate-over-passive margin;
- candidate-over-fair-interventional margin;
- saturation equivalence band;
- replay tolerance;
- ablation collapse threshold.

Required artifacts:

- `stage0_margin_freeze_manifest.json`
- `stage0_margin_freeze_manifest.sha256`
- `margin_gate_report.json`
- `margin_gate_negative_control_report.json`

The margin gate must be callable and fail-able. It must ship a demonstrated
failing negative control where a synthetic candidate fails the frozen margin and
the gate returns:

`close_or_downgrade`

If the negative control is absent, tautological, or does not force the failed
verdict, the run is invalid.

## 13. Fair-Interventional Saturation Gate

The mechanism component under test must be:

- predeclared;
- minimal;
- independently specified outside candidate source;
- hashed before the run;
- not defined by the candidate's observed advantage after the fact.

No vague exception may weaken the strongest fair baseline. The only permitted
access asymmetry is the minimal predeclared mechanism component under test. All
other access must be equal.

Required access-parity artifact:

`access_parity_report.json`

It must compare candidate and strongest fair baseline on:

- intervention budget;
- intervention API;
- legal observations;
- action space;
- serialized state access;
- update access;
- train/heldout episode access;
- counterfactual-pair access;
- random seed access;
- replay inputs;
- evaluator-only fields exclusion.

Required feature-impoverishment positive control:

When the tested mechanism component is granted to the strongest fair baseline,
the baseline must approach candidate performance within the frozen equivalence
band. If it does not, the baseline is considered unfair or impoverished and the
run is invalid.

The saturation judgment must compute:

`fair_interventional_max = max(score(baseline) for baseline in fair_interventional_family)`

where `fair_interventional_family` includes all six graph-cache challengers from
section 11 and any additional fair causal-discovery, do-regression,
contingency/count-table, nearest-neighbor intervention-effect, or legal
interventional attacker specified by the implementation card.

The saturation gate must ship a demonstrated failing negative control where a
fair interventional baseline saturates the candidate and the gate returns:

`close_or_downgrade`

If `candidate_score <= fair_interventional_max + saturation_equivalence_band`,
the verdict is `close_or_downgrade`.

## 14. Provenance F-Forge Closure

Every candidate-run material row must record:

- `producer_function`;
- input artifact paths;
- input artifact hashes;
- `run_id`;
- seed IDs;
- train context IDs;
- heldout context IDs;
- counterfactual pair IDs where applicable;
- episode IDs;
- aggregation rule;
- code path hash;
- output artifact path;
- output row IDs.

For every material row, the provenance validator must do at least one of:

1. Re-execute the recorded producer function on the recorded inputs and assert
   the recomputed output equals the recorded value.
2. Rederive the recorded basis from recorded inputs and assert the recorded value
   follows from that rederived basis.

Self-declared basis consistency is insufficient.

Required forged-provenance positive control:

- Inject a self-consistent forged value/basis that points to a true producer and
  has a source hash that otherwise appears valid.
- The provenance gate must block that forged row.
- If the forged row passes, the whole candidate-run evidence claim is invalid.

This requirement applies to candidate-run evidence itself, not only to future
Gate-level reuse.

## 15. Ablation Requirement

Future implementation must bind real rerun ablations. At minimum:

- no-intervention ablation must collapse to the passive ceiling;
- shuffled action-to-channel mapping must collapse;
- disabled tested mechanism component must collapse or return
  `close_or_downgrade`;
- corrupted serialized state must change recomputed replay behavior;
- label/name/order-only access must not recover the hidden self-set.

Every ablation must have callable invocation provenance and must be rerun under
the recorded intervention. Literal copied reports or stale values are invalid.

## 16. Trace / Replay Requirement

Replay must recompute candidate behavior from serialized state plus legal
observations/interventions. It must not compare only stored hashes and must not
read truth self-set labels, evaluator-only fields, future observations, or
candidate-invisible aliases.

Tautological controls do not count toward failability. Examples that do not
count by themselves:

- asserting that a stored hash field was ignored without adversarially changing
  replay inputs;
- checking that a constant flag is false;
- confirming that a JSON key exists.

Load-bearing replay controls must mutate serialized state or legal intervention
rows and demonstrate changed recomputed behavior or a fail-closed verdict.

## 17. Truth-Seed Isolation

Ground-truth self-set seed material must be disjoint from every candidate and
baseline observation seed. At minimum, the future implementation card must
record:

- truth self-set seed IDs;
- candidate observation seed IDs;
- baseline observation seed IDs;
- supervised passive train seed IDs;
- heldout/evaluation seed IDs;
- proof of pairwise disjointness where required.

If truth seed material overlaps candidate or baseline observation seeds in a way
that can leak the hidden self-set, the run is invalid.

## 18. Computed-Evidence Provenance Gate

This R1 card does not generate mechanism scores. A future implementation card
must require all evidence-bearing results, baselines, ablations, contrasts,
leakage scans, replay metrics, and verdicts to come from callable computation
paths.

Forbidden evidence forms:

- literal score dictionaries;
- static verdict dictionaries;
- unconditional clean reports;
- tests that assert pass without testing computation paths and failure paths;
- provenance rows whose basis is only self-declared;
- replay that compares stored hashes only.

Required tests for the future implementation:

- producer invocation path;
- producer failure path;
- baseline invocation;
- ablation invocation;
- leakage positive controls;
- forged-provenance positive control;
- replay recomputation;
- source-pin integrity;
- no unused frozen seed, train context, heldout context, or counterfactual pair.

Any unused frozen seed, train context, heldout context, or counterfactual pair
blocks the evidence claim.

## 19. Global Material-Gate Failability Rule

Every material gate must ship a demonstrated failing negative control. A gate
without a demonstrated failing control is non-fail-able and void.

Material gates include at minimum:

- non-identifiability premise gate;
- passive-family max gate;
- margin gate;
- fair-interventional saturation gate;
- access-parity gate;
- feature-impoverishment control gate;
- leakage gate;
- ablation gate;
- replay gate;
- provenance gate;
- source-pin gate;
- frozen-threshold gate;
- seed-isolation gate.

## 20. Acceptance Gate For This R1 Card

This R1 card is acceptable as a revision artifact only if:

- the preserved audit evidence exists locally;
- B1-B5 are explicitly closed in contract language;
- N1-N4 are incorporated;
- implementation remains forbidden;
- Gate/mainline/runtime paths remain untouched;
- source/test/script paths remain untouched;
- Auto-Remote-Anchor remains forbidden;
- claim ceiling remains candidate-card revision only.

## 21. Stop Condition

Stop if any of the following occurs:

- source, test, script, Gate runner, mainline, runtime, scheduler, bridge,
  product/admission, credential, push, or deployment file is modified;
- candidate implementation is introduced;
- candidate CLI or pytest candidate path is introduced;
- push/tag/remote-anchor is attempted;
- PAT or any secret is printed, copied, exposed, or modified;
- any claim says Route C works, candidate is authorized, Gate passed, mainline
  effect exists, or mechanism evidence has been produced.

## 22. Rollback Plan

If forbidden files are touched, revert those changes immediately and preserve
only the blocker if useful.

If R1 does not close B1-B5, do not proceed to implementation. Return to
candidate-card revision.

## 23. Expected Changed Files For This Preservation Task

- `docs/research/DRAFT-ROUTE-C-CANDIDATE-CARD-001A-R1.md`
- `docs/research/CLAUDE-INDEPENDENT-DRAFT-ROUTE-C-CANDIDATE-CARD-001A-AUDIT-001A.md`
- `artifacts/CLAUDE-INDEPENDENT-DRAFT-ROUTE-C-CANDIDATE-CARD-001A-AUDIT-001A/audit_report.md`
- `artifacts/CLAUDE-INDEPENDENT-DRAFT-ROUTE-C-CANDIDATE-CARD-001A-AUDIT-001A/audit_result.json`
- `artifacts/CLAUDE-INDEPENDENT-DRAFT-ROUTE-C-CANDIDATE-CARD-001A-AUDIT-001A/claim_ceiling.txt`
- `artifacts/DRAFT-ROUTE-C-CANDIDATE-CARD-001A-R1/card.md`
- `artifacts/DRAFT-ROUTE-C-CANDIDATE-CARD-001A-R1/result.json`
- `artifacts/DRAFT-ROUTE-C-CANDIDATE-CARD-001A-R1/claim_ceiling.txt`
- `docs/decision_log.md`

## 24. Forbidden Changes

- `src/**`
- `tests/**`
- `scripts/**`
- Gate runner files
- mainline files
- runtime files
- scheduler files
- bridge files
- product/admission files
- credential or push scripts

## 25. Auto-Remote-Anchor Decision

Auto-Remote-Anchor: forbidden.

This task must not push, tag, or remote-anchor.

## 26. Claim Ceiling

Candidate-card audit preservation and revised candidate-card contract only.

No mechanism evidence, no candidate evidence, no Gate pass, no mainline effect,
no live path, no agency, no autonomy, no consciousness, no emotion, no stable
user benefit, no EGO readiness, and no claim that Route C works.

## 27. Next Minimal Closed-Loop Action

Independent hostile audit of this R1 candidate-card. Candidate implementation
remains forbidden unless that future audit accepts the card and a separate
bounded implementation task card explicitly authorizes implementation scope.

## 28. What This Does Not Prove

This R1 card does not prove Route C mechanism validity, hidden-self-set
inference, self-boundary evidence, candidate success, Gate pass, mainline
effect, runtime readiness, agency, autonomy, consciousness, emotion, stable user
benefit, EGO readiness, or that any prior ACSB/ACOLB artifact was stronger than
its preserved claim ceiling.
