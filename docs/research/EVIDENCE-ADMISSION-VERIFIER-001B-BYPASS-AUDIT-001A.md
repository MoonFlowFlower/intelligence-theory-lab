# EVIDENCE-ADMISSION-VERIFIER-001B-BYPASS-AUDIT-001A

## Status

verifier_001b_blocked_by_circular_candidate_controlled_digest

## Layer

engineering-governance / verifier bypass audit preservation and route downgrade only

## Audited Boundary

- anchored boundary under audit: `14aa837e1db8265f9ec64c745c46d9a70c1eaaa3`
- repair parent: `b1070058736235dc897d4fa9e693f48f06e63059`
- verifier route under audit: standalone `evidence_admission_verifier_001a` after 001B callable-provenance repair
- mainline integration status: none
- enabled status: no new enabled path; standalone verifier only

## Preserved Independent Audit Text

Independent audit found a decisive bypass in the anchored standalone verifier boundary `14aa837...`: the verifier admits forged evidence because it compares producer-returned `output_digest` against candidate-declared `expected_output_digest`. Both sides are candidate-controlled. Preserve this as negative evidence and downgrade verifier 001B from admission contract to weak prefilter/linter only.

The audit consequence is not a source-repair instruction. The verifier source must remain unchanged in this task. The preserved result is a route downgrade: verifier 001B is not usable as a future Gate evidence admission contract or citation-admission boundary.

## Bounded Audit

- real objective: preserve the bypass as negative evidence and prevent future citation of verifier 001B as an admission contract.
- strongest baseline explanation: the existing verifier claim is that forged provenance, wrong code hash, and wrong output digest controls block, making 001B suitable as a bounded callable-provenance admission gate.
- strongest invalidating reason: the verifier trusts a candidate-controlled callable as the recomputation authority and only compares that callable's returned digest to a candidate-declared expected digest.
- falsifier for this framing: an executable PoC using current `14aa837...` verifier source fails to admit the forged bundle and records a non-empty blocking reason.
- still-insufficient evidence: a normal wrong-output test with an honest producer remains insufficient because it does not test candidate control over both the producer and the expected digest.
- mechanism-vs-resemblance classification: this is engineering evidence hygiene only; it does not test a mechanism hypothesis.

## Preserved PoC Evidence

Repo-visible executable PoC:

```text
artifacts/evidence_admission_verifier_001b_bypass_audit_001a/poc_forged_digest_admission.py
```

Required reproduction outputs:

```text
artifacts/evidence_admission_verifier_001b_bypass_audit_001a/poc_result.json
artifacts/evidence_admission_verifier_001b_bypass_audit_001a/route_decision.json
artifacts/evidence_admission_verifier_001b_bypass_audit_001a/verifier_outputs/constant_producer/admission_decision.json
artifacts/evidence_admission_verifier_001b_bypass_audit_001a/verifier_outputs/row_echo_producer/admission_decision.json
```

The constant-producer case is the stronger preservation target: it records that the bypass does not depend on `row` injection. A candidate-controlled producer can return a fabricated digest constant, while the candidate-controlled metric row declares the same fabricated digest as `expected_output_digest`.

## Route Decision

Verifier 001B is downgraded to weak prefilter/linter only.

It must not be used for:

- citation admission;
- Gate3 or Gate4 admission;
- same-agent bridge admission;
- EGO mainline admission;
- runtime, deployment, readiness, or mechanism-validity claims.

It may only be cited as:

- negative evidence for circular candidate-controlled digest comparison;
- a weak shape/provenance linter whose positive result has no admission-contract force;
- a route blocker until a separate authorized repair task establishes independent callable recomputation against a non-candidate-controlled expected output.

## Acceptance Readback Fields

- current layer: engineering-governance / verifier bypass audit preservation and route downgrade only
- mainline integration status: none
- enabled status: no new enabled path
- real trigger evidence: executable PoC and verifier output artifacts under `artifacts/evidence_admission_verifier_001b_bypass_audit_001a/`
- claim ceiling: verifier-bypass negative evidence and route downgrade only
- next minimal closed-loop action: independent review of preserved bypass and, only if separately authorized, draft a repair task card

## What This Does Not Prove

This does not prove Gate validity, mechanism validity, admission readiness, mainline effect, agency, consciousness, emotion, autonomy, stable user benefit, EGO readiness, or that any repaired verifier would be valid.
