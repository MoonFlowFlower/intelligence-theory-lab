# Task Card: PREDICTIVE-ACTION-LEARNING-CONTRACT-001C-T1-EXTERNAL-COMMIT

Status: DRAFT — NOT AUTHORIZED FOR IMPLEMENTATION.
Authorization required because this card uses an external service (RFC 3161
time-stamping authority), which the lab boundary forbids by default.

Predecessor: PREDICTIVE-ACTION-LEARNING-CONTRACT-001 (artifacts:
`artifacts/predictive_action_learning_contract_001/suite_2026-06-10_r1/`),
closed out by PREDICTIVE-ACTION-LEARNING-CONTRACT-001B with
`implementation_pass_but_evidence_protocol_blocked_by_T1`.

## 1. Problem definition

Replace the local-mock pre-outcome commitment sink with an externally
verifiable RFC 3161 timestamp sink and rerun the frozen 001 suite, unchanged,
to remove protocol blocker `T1_external_commit_missing`.

## 2. Current stage

Protocol repair only (001 rollback class 14.2). Frozen and byte-identical to
001: mathematical skeleton, learner initialization, thresholds, seeds,
environment rules, baselines, ablations, perturbations, trace schema, gate
definitions, verdict precedence.

## 3. Hypothesis

Because commitment receipts are declared volatile fields (excluded from
content hashes and duplicate comparison), rerunning the frozen suite with an
RFC 3161 sink reproduces all 001 behavioral records exactly and all gate
outcomes identically, while producing per-step timestamp tokens that verify
offline against the TSA certificate chain.

## 4. Mechanism (amended before implementation; design rationale recorded)

Commitment mode: 001 section 7.5 mode 2 — transparency-style append-only log
with later inclusion proof — NOT per-step mode-1 tokens. Rationale, recorded
honestly: per-step external tokens would mean ~46,000 requests against public
TSAs (rate-abusive, ~13h wall time) while adding no evidential value beyond
anchored inclusion, given the deterministic-environment concession in section
10. Design:

- Every PRE_STEP is committed, before outcome sampling, into the per-run
  append-only commit log exactly as in 001 (flush-ordered, monotonic ns), with
  an explicit running `commit_chain_hash` (sha256 chaining of log entries).
- RFC 3161 anchors: the current chain head is sent as TimeStampReq
  (messageImprint = chain head) to the TSA at: suite start (CONFIG + runtime
  manifest), each run's RUN_META, every K=200 commits (synchronously, before
  that step's outcome reveal), each run end, suite end. ~320 calls total.
- Tokens (DER) are stored in sidecar files (`anchors.log.jsonl`), never inside
  trace.jsonl, so traces remain byte-comparable to 001.
- Inclusion proof: any committed PRE_STEP is covered by the next anchor; the
  chain recomputation from the commit log to the anchored head is the proof.
- Primary TSA: freetsa.org; fallback: timestamp.digicert.com; TSA per anchor
  recorded.
- Offline verifier (no network): token signature (asn1crypto + cryptography)
  against the signer certificate embedded in the token plus CA material stored
  at run time (fingerprints reported for out-of-band confirmation),
  messageImprint == recomputed chain head, genTime monotonic, full segment
  coverage, every PRE_STEP covered by an anchor.

Provable statement per step: "this PRE_STEP existed no later than the genTime
of its covering anchor, and at anchor steps, before that step's own outcome
reveal." Per-step commit-before-reveal ordering between anchors remains
internally attested (monotonic ns), as in 001.

## 5. Execution constraint (declared honestly)

Claude's execution environment cannot make external HTTP calls (network
policy). Division of labor:

1. Claude implements: RFC 3161 sink, offline verifier, token-tamper tests,
   regression comparator, `run-suite-external` CLI; unit-tested with recorded
   token fixtures.
2. The user executes one documented command locally (network required),
   producing `artifacts/predictive_action_learning_contract_001c/<run_id>/`.
3. Claude validates returned artifacts entirely offline: token verification,
   chronology, stripped-trace equality against 001, full gate re-evaluation.

## 6. Dependencies

`asn1crypto` + `cryptography` (or `rfc3161ng`) for the sink/verifier module
only, isolated in `predictive_action_learning_contract_001c/`. The learner and
all 001 modules remain stdlib-pure and untouched.

## 7. Baseline

The 001 local-mock artifacts are the regression baseline. Gate: every rerun
trace must be byte-identical to its 001 counterpart after masking exactly:
(a) the declared volatile fields, (b) the sink-identity fields that change by
definition (`commit_mode`, `commit_sink_id`, `receipt_type`,
`receipt_verifier_key_id`, `runtime_manifest_hash`, `config_manifest_hash`),
and (c) the hash fields recomputed over them (`pre_step_hash`,
`pre_step_hash_ref`, `post_step_hash`). All behavioral content (beliefs,
theta, predictions, actions, observations, errors, responsibilities) is
compared unmasked; internal hash validity of the new traces is verified
separately by the 001 validator. Any behavioral divergence is a stop condition
(hidden nondeterminism), not a thing to patch.

## 8. Ablations and implementation seam

No new mechanism ablations. Protocol ablations: (a) rerun abl5
(commit disabled) -> evidence blocked; (b) anchor-tamper test: corrupt one
stored token -> offline verifier must reject; (c) wrong-imprint test: token
for a different chain head -> reject; (d) chain-gap test: remove a commit log
entry -> inclusion recomputation must fail.

Declared seam: `predictive_action_learning_contract_001/runner.py` gains a
minimal sink registry (commit value -> sink class, lazy import for the 001C
sink) so the frozen suite can be rerun with the external sink without
duplicating the runner. No other 001 module changes; the 34 frozen tests must
still pass; the masked-equality gate empirically confirms behavioral
invariance. Unit tests use a LOCAL fake TSA (test-generated CA via
`cryptography`, clearly labeled `test_local_ca`); runs anchored by the fake
TSA can never be reported as external evidence (verifier refuses issuer in the
test-CA set).

## 9. Acceptance gates

1. 100% of anchors verify offline (signature, imprint == recomputed chain
   head, monotonic genTime, full coverage of all PRE_STEP commits, real-TSA
   issuer).
2. Masked-trace equality with 001 for all 45 runs (section 7 mask).
3. All 001 implementation and evidence gates re-pass on the new artifacts.
4. Tamper / wrong-imprint / chain-gap / disabled-commit detections all fire.
5. Only then: `evidence_verdict = bounded_contract_pass`.

## 10. Claim ceiling

Maximum claim on success:

> The frozen predictive-action learning contract passed the bounded isolated
> experiment, including externally verifiable RFC 3161 pre-outcome commitment,
> under the stated residual trust assumptions.

Residual trust assumptions (must be stated wherever the claim is made):

- The environment is a seeded deterministic simulation; tokens prove that each
  PRE_STEP existed no later than genTime, i.e. procedure chronology — they do
  NOT prove outcome unpredictability (outcomes are deterministic functions of
  the committed seed).
- `obs_reveal_ts` remains self-reported; only commit times are external.
- Genuine outcome unpredictability would require an external randomness beacon
  driving environment draws. That changes the environment draw mechanism,
  which 001B freezes; it is OUT OF SCOPE here and would need a separate card
  (001D) with its own authorization.

All 001B forbidden claims remain forbidden.

## 11. Stop conditions

1. TSA unreachable or tokens unverifiable -> `protocol_blocked` (never fake or
   backfill tokens).
2. Stripped-trace mismatch vs 001 -> stop, report nondeterminism.
3. Any change to skeleton, thresholds, seeds, env rules, baselines, ablations,
   perturbations, or schema -> stop.
4. genTime ordering violation -> stop.
5. Verification depending on network at validation time -> stop.

## 12. Rollback plan

001C artifacts are isolated under
`artifacts/predictive_action_learning_contract_001c/`; 001 artifacts and the
001B closeout are immutable. Rollback = delete the 001C module and artifacts;
nothing else is touched.
