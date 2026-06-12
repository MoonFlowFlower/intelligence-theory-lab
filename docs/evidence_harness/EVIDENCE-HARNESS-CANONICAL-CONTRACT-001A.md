# EVIDENCE-HARNESS-CANONICAL-CONTRACT-001A

## Mode

Canonical evidence-harness contract drafting only.

This is not a Gate repair, Gate execution, mechanism validation, Gate4 001C
continuation, Gate5, admission, runtime, or bridge task.

## Layer

Engineering implementation layer: governance contract and evidence-admissibility
specification.

This document does not test a mechanism. It defines conditions future
score-bearing mechanism-adjacent tasks must satisfy before their evidence can be
used downstream.

## Starting State Readback

- Required branch: `codex/meta-theory-scaffold`
- Required starting HEAD: `7557beccbe5b89b919c61838b6688765d723fd7f`
- Required anchor tag on HEAD:
  `remote-anchor-cross-gate-triage-schema-gap-amendment-001-7557bec`
- Required start condition: clean worktree before generation

## Input Anchors

| Anchor | Commit | Status Used Here |
| --- | --- | --- |
| Gate4 001B sealed boundary | `90dc4b9082593fabf06197b03eaf66c9c64014a2` | Sealed rejected input; not Gate4 pass evidence |
| Cross-gate score credibility triage | `393ebe5b03a07b2a6b5b91c46479b0cf92cb93c9` | Bounded triage evidence only; Gate validity not claimed |
| Triage schema-gap amendment | `7557beccbe5b89b919c61838b6688765d723fd7f` | Downstream entry remains blocked |

The schema-gap amendment records:

- `safe_to_continue_gate4_001c`: false
- `safe_to_enter_gate5`: false
- `safe_to_enter_admission`: false
- `safe_to_enter_runtime`: false

This contract preserves those blocks. It does not convert an anchor, triage, or
amendment into mechanism evidence.

## Anti-Sycophancy / Invalidity Audit

Strongest baseline explanation: the existing ad hoc evidence style can produce
pass-shaped artifacts by writing scores, verdicts, ablation labels, replay
fields, leakage flags, and test expectations directly into JSON or tests without
forcing the candidate, baselines, ablations, replay, or scanner to run through
independent callable computation paths.

Strongest reason this task may be invalid: a document-only contract can become
another governance artifact that future tasks cite while bypassing actual
enforcement. If future repairs still pass with static scores, dead baselines,
hash-only replay, broad whitelist leakage scans, or tests that assert pass
strings, then this contract did not close the false-pass channel.

Falsifier for the current framing: a future Gate repair or deep audit claims
downstream-admissible evidence while any required producer path, baseline call,
real ablation, replay recomputation, leakage positive control, or failure-path
test is absent, static, or dead code.

Evidence still insufficient: clean JSON parsing, artifact existence, local test
pass, tag presence, commit ancestry, or a natural-language summary are not
enough for downstream evidence strength.

Mechanism vs resemblance: this task tests neither mechanism nor behavioral
resemblance. It only defines an admissibility contract for future evidence.

## Problem Definition

The blocker is not one broken Gate. The blocker is that previous score-bearing
tasks may have allowed false-pass evidence through:

- pass-shaped JSON
- static score fields
- weak or unfair baselines
- non-causal metrics
- replay shortcuts
- weak leakage scans
- tests that assert pass outputs

Future Gate repairs, deep audits, and mechanism-adjacent executable tasks must
therefore satisfy a canonical evidence-harness contract before evidence can be
treated as downstream-admissible.

## Baseline Failure Mode

The baseline is the current ad hoc per-task evidence style observed by
cross-gate triage:

- verdicts stored as literal pass strings
- scores stored as static fields or dictionaries
- baselines declared but not invoked
- baselines given less information than the candidate
- ablations represented by labels or branch sentinels instead of interventions
- replay implemented as stored action, stored verdict, or hash comparison
- leakage scanning implemented as broad whitelist or absence of file checks
- tests asserting artifact existence, parse success, perfect scores, or pass
  verdicts

This contract rejects that baseline as downstream-admissible evidence.

## Claim Ceiling

Allowed claim:

`bounded canonical evidence-harness contract only`

Forbidden upgrades:

- Gate validity
- mechanism validity
- theory validity
- architecture correctness
- Gate4 001C authorization
- Gate5 authorization
- admission authorization
- runtime authorization
- bridge authorization
- EGO-mainline readiness
- consciousness, subjectivity, real autonomy, real emotion, or self-awareness
  evidence

## Contract Sections

### 1. Computed-Evidence Provenance

Every future score, baseline, ablation, replay, leakage scan, and verdict must
record:

- producer function
- source file path
- source code hash
- input artifact paths
- run id
- seed
- context ids
- episode ids
- aggregation rule
- raw outputs
- transformed outputs
- final decision path
- whether at least one relevant failure path was tested

Evidence must be derived from callable computation paths.

Reject:

- literal pass verdicts
- static score dictionaries
- unconditional `verified: true`
- unconditional `real_intervention: true`
- hard-coded degradation
- hard-coded clean reports
- post-hoc JSON summaries without producer path

### 2. Score / Metric Contract

Metrics must distinguish:

- ex-ante prediction
- post-hoc explanation
- observed feedback copying
- candidate action generation
- reference action generation

Raw and transformed scores must both be stored.

Reject metrics where:

- candidate and reference are derived from the same observed feedback path
- a constant predictor can tie the candidate
- feedback-copy baseline can tie the candidate but is not included
- perfect score is structurally guaranteed
- score is clipped, min/max forced, or patched to satisfy threshold

### 3. Baseline Fairness Contract

Every future score-bearing task must include independent callable baselines.

Minimum baseline classes unless explicitly inapplicable:

- constant predictor baseline
- random or null-action baseline
- heuristic baseline
- feedback-copy or observed-response-copy baseline when the candidate sees
  feedback
- blind ex-ante baseline when the candidate is also ex-ante

Baselines must have information parity with the candidate. If parity is
impossible, the asymmetry must be classified as invalid for mechanism evidence.

Reject:

- dead-code baselines
- strawman baselines
- baselines that cannot tie by construction
- baselines with less information than candidate
- baselines declared but not invoked

### 4. Ablation Integrity Contract

Ablations must be real interventions.

Required:

- rerun affected episodes
- record intervention target
- record pre/post state difference
- record raw ablation scores
- record unclipped degradation
- record whether degradation is actually causal

Reject:

- variant-name sentinel branches
- ablation-name special cases
- label-only ablations
- threshold-forced degradation
- clipping non-degradation into degradation
- ablations that only modify report text

### 5. Replay Recomposition Contract

Replay must recompute behavior from:

- serialized state
- observation
- allowed context
- deterministic seed when applicable

Replay is not sufficient if it only:

- reuses stored actions
- reuses stored verdicts
- compares hashes
- validates artifact existence
- checks a final report string

Hash chains may support replay but cannot replace recomputation.

### 6. Leakage Scan Contract

Leakage scanning must cover:

- source
- tests
- docs
- task cards
- artifacts
- `result.json`
- `claim_ceiling.txt`
- downstream decision files

Required:

- denylist of unauthorized claims
- positive-control leakage case
- scan of pass-shaped claims
- scan of readiness claims
- scan of mechanism-validity claims
- scan of agency, selfhood, consciousness, emotion, relationship-learning, and
  stable-benefit claims

Reject:

- broad whitelist hiding unauthorized claims
- restraint-marker-only logic
- `result.json` exclusion
- no positive-control case
- scanner that only checks file existence

### 7. Test Integrity Contract

Tests must verify computation paths, not just output shape.

Required test properties:

- invokes candidate producer
- invokes baseline producer
- invokes ablation path
- invokes replay recomputation
- invokes leakage scanner
- tests at least one failure path
- tests positive controls
- fails if pass strings are hard-coded
- fails if scores are static literals
- fails if ablation degradation is clipped or patched
- fails if baseline is not called

Reject tests that only assert:

- artifact exists
- JSON parses
- verdict equals pass
- score equals `1.0`
- degradation is positive
- required field exists
- claim ceiling exists

### 8. Artifact Mutability Contract

Historical artifacts are immutable.

Future repairs must:

- create new artifact directories
- preserve old verdicts
- classify old evidence as rejected, blocked, or reference if needed
- never rewrite old pass into valid pass
- never silently mutate old artifacts
- record before/after inventory if any old path must be inspected

### 9. Downstream Admissibility Matrix

Admissibility states:

- `admissible_downstream_evidence`
- `admissible_negative_evidence_only`
- `reference_only`
- `blocked_pending_audit`
- `rejected_false_pass_risk`
- `governance_anchor_only`

Downstream rules:

- Gate5 requires upstream Gate0-Gate4 score-bearing evidence to be admissible or
  explicitly quarantined with replacement evidence.
- Admission requires no unresolved critical or high upstream score-bearing
  evidence.
- Runtime and bridge require admission plus a separate runtime safety contract.
- Negative evidence can inform repair order but cannot support mechanism
  validity.
- Anchor verification does not raise evidence strength.

### 10. Existing Risk Migration Policy

Existing risk treatment:

- Gate4 001B remains rejected or critical-risk input only.
- Provisional Gate4 001C remains local reference only, not canonical evidence.
- Critical-risk earlier Gate2, Gate3, and testbed tasks block Gate4
  continuation until repaired or quarantined with replacement evidence under
  this contract.
- Any high or critical future repair must satisfy this canonical contract before
  downstream use.
- If many tasks are high or critical, prefer evidence-harness repair over
  individual pass-seeking patches.

Known Gate4 001B false-pass patterns explicitly rejected here:

- static score or pass fields
- pass-shaped tests
- clean literals in leakage reports
- baseline declarations without callable invocation evidence
- ablation reports without real intervention and rerun evidence
- replay by stored hashes, actions, or verdicts instead of recomputation

## Future Task-Card Requirements

Every future Gate repair, deep audit, or mechanism-adjacent executable task card
must include:

- task id
- problem definition
- current stage
- hypothesis
- baseline
- ablation
- trace/replay recomputation requirement
- acceptance gate
- computed-provenance requirement
- leakage positive-control requirement
- test failure-path requirement
- claim ceiling
- stop condition
- rollback plan
- downstream admissibility target or explicit non-admissibility target

No future task may treat this contract itself as evidence that any Gate is valid.

## Stop Conditions

Stop and report blocked if a future task:

- starts from an unverified or dirty state when a clean start is required
- attempts to repair a Gate without a bounded task card
- modifies old artifacts, tests, or verdicts without explicit errata authority
- uses provisional Gate4 001C as canonical evidence
- claims downstream entry from anchor presence alone
- claims mechanism validity from contract existence, JSON parsing, or artifact
  completeness
- authorizes Gate5, admission, runtime, or bridge while high or critical upstream
  score-bearing evidence remains unresolved

## Acceptance Gate For This Contract

This contract is acceptable only if:

- the required starting HEAD and clean worktree precondition were verified before
  generation
- only new contract docs and new contract artifacts were created or modified
- all required contract sections are present
- all required JSON artifacts parse
- downstream entry remains blocked
- Gate4 001C remains unauthorized
- Gate5, admission, runtime, and bridge remain unauthorized
- the contract explicitly rejects the known Gate4 001B false-pass patterns
- the contract explicitly handles baseline fairness, ablation integrity, replay
  recomputation, leakage positive controls, and test failure paths

## What This Does Not Prove

This document does not prove:

- any Gate is valid
- Gate4 001B can be repaired
- Gate4 001C may continue
- Gate5 may start
- admission, runtime, or bridge is authorized
- any mechanism, theory, or architecture is correct
- any functional-subject, agency, selfhood, consciousness, emotion, or EGO
  readiness claim
