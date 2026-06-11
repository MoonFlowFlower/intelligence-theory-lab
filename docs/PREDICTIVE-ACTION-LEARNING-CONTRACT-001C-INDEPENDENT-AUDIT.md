Task ID:
PREDICTIVE-ACTION-LEARNING-CONTRACT-001C-INDEPENDENT-AUDIT

Mode:
Independent evidence audit only.
Do not implement new mechanism.
Do not repair failures.
Do not expand theory.
Do not integrate with EGO mainline.

Project context:
This is part of an EGO / R-G predictive-action kernel research project.

The current frozen artifact is:

PREDICTIVE-ACTION-LEARNING-CONTRACT-001C

Current frozen status:
implementation_verdict = bounded_contract_pass
evidence_verdict = bounded_contract_pass
scope = isolated finite-state predictive-action learning contract
claim_ceiling = bounded isolated mechanism evidence only

001C repaired the earlier 001B T1 failure:
local_mock commitment was replaced by externally verifiable RFC 3161 anchored-chain commitment.

Known frozen 001C facts:
anchor_verification_ok_all_runs = true
anchors_externally_valid = true
anchors_signed_by_test_ca = false
masked_equality_vs_001 = true
errors = []

Important caveats that must not be erased:
1. The environment is seeded deterministic simulation.
2. Anchors prove committed PRE_STEP content existed no later than anchor genTime.
3. Anchors do not prove outcome unpredictability.
4. Anchor steps can prove commitment before that step's own outcome reveal.
5. Between-anchor reveal ordering still depends on internal attestation.
6. obs_reveal_ts between anchors is self-reported.
7. signer authenticity depends on token-embedded certificates and recorded fingerprints plus out-of-band confirmation.
8. 001D randomness beacon is out of scope and must not be started.
9. Retrieval caveat: 001C supports mechanism-distinguishability from retrieval under the frozen composite evidence rule, but does not prove predictive-performance superiority over retrieval.

Layer classification:
This task is at the mechanism-evidence audit layer.
It is not:
- performance optimization
- agent architecture
- EGO mainline integration
- companion behavior
- replay/consolidation
- agency validation
- functional subject validation
- consciousness theory

Problem definition:
Audit whether PREDICTIVE-ACTION-LEARNING-CONTRACT-001C has a clean enough canonical evidence record to remain a frozen Gate 0 bounded pass.

The audit must determine whether the evidence actually supports the stated narrow claim:

"The frozen predictive-action learning contract passed the bounded isolated experiment, including externally verifiable RFC 3161 pre-outcome commitment anchoring, under the stated residual trust assumptions."

The audit must also determine whether any stronger claim is accidentally implied, unsupported, or written into reports.

Hypothesis under audit:
001C provides bounded isolated mechanism evidence for action-conditioned belief/model update, distinguishable from retrieval under the frozen composite evidence rule, with external pre-outcome commitment anchoring.

Null / adversarial hypotheses:
1. The pass depends on post-hoc trace construction.
2. The pass depends on local chronology claims not independently supported.
3. The pass depends on derived summaries instead of raw canonical evidence.
4. The pass depends on threshold tuning or seed selection.
5. The pass is actually retrieval-equivalent and only appears distinct due to weak baseline framing.
6. The pass overstates predictive performance superiority.
7. The RFC 3161 anchored-chain proves less than the closeout claims.
8. The report accidentally upgrades Gate 0 evidence into agency / functional-subject / EGO evidence.

Hard boundaries:
Do not modify:
- skeleton learner
- thresholds
- seeds
- environment rules
- baselines
- ablations
- perturbations
- trace schema
- commitment algorithm
- runner logic
- validator logic
- claim ceiling
- EGO mainline
- LLM / replay / retrieval integration
- companion / emotion / relationship logic

Allowed:
- inspect frozen artifacts
- inspect reports
- inspect raw traces
- inspect validators
- inspect commitment logs
- inspect anchor tokens / verification records
- run existing tests / existing validators if available
- create audit-only report files
- optionally create audit-only scripts under an audit folder, provided they do not modify runtime code, thresholds, artifacts, or existing verdict logic

Not allowed:
- no mechanism repair
- no threshold adjustment
- no new experiment family
- no new baseline added to improve the result
- no new claim
- no 001D randomness beacon
- no Gate 1 / replay / consolidation
- no EGO integration
- no agency / consciousness / functional subject language

Required audit questions:

1. Claim ceiling audit
Check every README, report, closeout, metric summary, and generated artifact.
Confirm no text claims or implies:
- consciousness
- subjective experience
- real emotion
- agency
- self-awareness
- functional subject evidence
- electronic life evidence
- AGI evidence
- companion readiness
- EGO mainline readiness
- predictive superiority over retrieval
- final proof of Bayesian filtering
- proof that Transformer / LLM scaling is wrong

Allowed wording:
- bounded isolated Gate 0 mechanism evidence
- action-conditioned belief/model update evidence
- mechanism-distinguishability from retrieval under frozen composite evidence rule
- RFC 3161 anchored-chain pre-outcome commitment evidence under residual trust assumptions

2. Canonical evidence audit
Verify that the pass is supported by raw canonical records, not only derived summaries.

Canonical raw evidence must include:
- raw PRE_STEP predictions
- raw all-action predictions
- raw actual observations
- raw prediction errors
- raw belief states before and after update
- raw theta_pre / theta_post where theta-learning is claimed
- raw commitment records
- raw anchor records
- raw verification outputs
- raw baseline outputs
- raw ablation / perturbation outputs

Derived summaries such as action_contrast, delta_theta, aggregate scores, plots, or final tables are not sufficient as primary evidence.

3. T1 external commitment audit
Verify the anchored-chain commitment claim.

Check:
- every PRE_STEP prediction is committed before actual_obs reveal according to the protocol
- every committed PRE_STEP is included in an append-only hash chain
- every chain segment is covered by a later RFC 3161 anchor
- anchor verification succeeds for all expected anchors
- anchor genTime is correctly interpreted
- token-embedded certificates and recorded fingerprints are preserved
- anchors_signed_by_test_ca = false is true and documented
- there is no local_mock fallback path silently used in evidence runs
- the closeout does not overclaim what RFC 3161 proves

Important distinction:
Anchors prove committed content existed no later than anchor genTime.
Anchors do not prove outcome unpredictability.
Between-anchor reveal ordering still depends on internal attestation unless independently anchored.

4. Chronology / reveal-ordering audit
Check whether each PRE_STEP → actual_obs reveal ordering is supported.

Classify each support type:
- externally anchored before reveal
- internally attested between anchors
- self-reported timestamp only
- unsupported / missing

The report must clearly state which parts are externally verified and which parts still depend on residual trust.

5. Retrieval caveat audit
Check that retrieval is not misrepresented.

The audit must preserve this claim boundary:

001C may support:
"mechanism-distinguishability from retrieval under the frozen composite evidence rule."

001C may not support:
"the learner predictively outperforms retrieval."

Specifically inspect whether retrieval baseline performance was close or better on any metric, especially post-shift.
If retrieval is close or stronger in predictive metrics, that must be explicitly stated.

6. Baseline / ablation audit
Inspect all existing baselines, ablations, and perturbations from 001 / 001B / 001C.

Check:
- baselines use the same observation/action histories allowed by their definitions
- baselines are not weakened by hidden information restriction mistakes
- action-sensitive regime requires all-action prediction separation
- null-control regime requires all-action prediction collapse
- retrieval false separation in null-control is treated as mechanism evidence, not performance evidence
- frozen-theta baseline is used where theta-learning is claimed
- rule-shift perturbation exists where theta-learning is claimed
- belief-update and theta-update claims are separated

7. Threshold / seed integrity audit
Check:
- thresholds were frozen before 001C
- seeds were frozen before 001C
- 001C did not change thresholds, seeds, environments, or acceptance gates
- masked_equality_vs_001 is meaningful and correctly scoped
- there is no evidence of post-hoc tuning
- any threshold sensitivity limitation is documented

8. Trace / replay audit
Verify:
- retrieval=false in the core protocol where required
- replay=false in the core protocol where required
- no REPLAY_STEP is present in the Gate 0 evidence run
- no memory/replay/consolidation mechanism is used to pass Gate 0
- trace-only memory status is preserved

9. Deterministic simulation caveat audit
Verify the report clearly states:
- the environment is seeded deterministic simulation
- 001C does not prove open-world robustness
- 001C does not prove outcome unpredictability
- 001D randomness beacon remains out of scope
- no claims rely on random environment draws unless supported by evidence

10. Evidence map requirement
Produce an evidence map.

For each major claim, map:

Claim:
Evidence artifact:
Raw evidence path:
Validator or check:
Residual trust assumption:
Status:
Supported / supported with caveat / blocked / failed

Required deliverables:

Create a final audit report, preferably:

docs/audits/PREDICTIVE_ACTION_LEARNING_CONTRACT_001C_INDEPENDENT_AUDIT.md

If the repo has an existing artifact convention, follow it without modifying existing runtime logic.

The report must contain:

1. Executive verdict
Use exactly one:

- independent_audit_pass
- independent_audit_pass_with_caveats
- evidence_blocked_by_missing_canonical_record
- evidence_blocked_by_commitment_uncertainty
- evidence_blocked_by_retrieval_caveat_violation
- evidence_blocked_by_threshold_or_seed_uncertainty
- independent_audit_fail

2. One-paragraph bounded conclusion
State what 001C supports and what it does not support.

3. Evidence map table
Map claims to raw evidence.

4. T1 commitment audit section
Explain exactly what RFC 3161 anchored-chain proves and does not prove.

5. Retrieval caveat section
Explicitly state whether predictive superiority over retrieval is unsupported.

6. Claim ceiling audit section
List any overclaiming language found.
If none, say none found.

7. Residual trust assumptions
List all remaining assumptions.

8. Fake-pass paths
List the most plausible ways 001C could still be misleading.

At minimum include:
- between-anchor ordering dependence
- deterministic seeded simulation
- retrieval near-equivalence or predictive strength
- derived-summary substitution risk
- threshold sensitivity risk
- baseline framing risk
- certificate / fingerprint verification assumptions

9. Stop conditions triggered
List any triggered stop condition.
If none, say none.

10. Required corrections
If issues are found, specify whether they are:
- wording/report correction only
- evidence-record correction
- validator correction
- protocol-level blocker
- requires new bounded task
Do not implement the correction unless separately authorized.

11. Final claim ceiling
Restate the maximum allowed claim after audit.

Acceptance gate:

The audit can return independent_audit_pass only if all are true:

1. Every major claim is supported by raw canonical evidence.
2. PRE_STEP commitments are covered by externally verifiable RFC 3161 anchored-chain records.
3. The report correctly separates external anchoring from internal attestation.
4. Retrieval caveat is preserved.
5. No predictive-superiority-over-retrieval claim is made.
6. No agency / consciousness / functional-subject / EGO-readiness claim is made.
7. No threshold, seed, environment, baseline, or validator mutation is detected.
8. No replay / retrieval / memory leakage is used in the core Gate 0 evidence path.
9. Residual trust assumptions are explicitly documented.
10. Any limitation is represented as a limitation, not hidden inside a pass.

Use independent_audit_pass_with_caveats if the evidence supports the bounded claim but residual trust assumptions remain important.

Use evidence_blocked_* if raw records are missing, ambiguous, or insufficient.

Use independent_audit_fail if the frozen pass is contradicted by raw evidence.

Stop conditions:

Immediately stop and report if any of these occur:

1. Core implementation must be changed to complete the audit.
2. Thresholds or seeds appear to have been modified post-hoc.
3. Raw canonical evidence is unavailable.
4. PRE_STEP commitment coverage cannot be verified.
5. Anchor verification fails.
6. A local_mock commitment path was used in evidence runs.
7. REPLAY_STEP appears in Gate 0 evidence.
8. Retrieval caveat is violated by report language.
9. Derived summaries are the only support for a major claim.
10. The audit requires starting 001D randomness beacon.
11. Any report claims agency, functional subject, consciousness, AGI, or EGO readiness.

Rollback plan:
If the audit fails or is blocked, do not repair.
Freeze the current state and write a blocker report.

The blocker report must say:
- what claim is unsupported
- what raw evidence is missing or contradictory
- whether 001C should be downgraded
- what the minimum next bounded task would be
- what must not be claimed meanwhile

Claim ceiling after this task:
At most:

"001C has passed / passed with caveats / failed independent evidence audit for bounded isolated Gate 0 predictive-action mechanism evidence."

No stronger claim is allowed.

Final instruction:
Do not optimize for making 001C pass.
Optimize for preventing false confidence.