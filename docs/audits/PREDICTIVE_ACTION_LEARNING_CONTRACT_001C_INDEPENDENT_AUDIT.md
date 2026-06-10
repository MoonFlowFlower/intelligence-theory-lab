# Independent Evidence Audit: PREDICTIVE-ACTION-LEARNING-CONTRACT-001C

Task card: `docs/PREDICTIVE-ACTION-LEARNING-CONTRACT-001C-INDEPENDENT-AUDIT.md`
Audit task id: `predictive_action_learning_contract_001c_independent_audit`
Layer: mechanism-evidence audit only. Date: 2026-06-10.
Mode: read-only on all frozen artifacts and runtime code. No mechanism change,
no repair, no threshold/seed/baseline/validator mutation, no new experiment
family, no 001D. Machine-readable audit artifacts:
`artifacts/predictive_action_learning_contract_001c_independent_audit/`.

## 1. Executive verdict

```text
independent_audit_pass_with_caveats
```

The frozen verdict `bounded_contract_pass` (implementation AND evidence) is
confirmed against raw canonical evidence. No downgrade is required. The
caveats are the preserved residual trust assumptions (section 7), one
documented evidence-infrastructure limitation (no version-control freeze
evidence, section 7 item 6), and three non-blocking wording-level corrections
(section 10). No stop condition was triggered.

## 2. One-paragraph bounded conclusion

001C supports exactly this: the frozen finite-state predictive-action learning
contract (3 states, 3 actions, 3 observations, declared seeds and thresholds,
one frozen skeleton instantiation) passed the bounded isolated experiment,
with every PRE_STEP prediction committed into an append-only hash chain whose
heads are covered by 257 externally verifiable RFC 3161 tokens from real TSAs
(re-verified offline in this audit: signatures, messageImprint against
independently recomputed chain heads, nonce binding, genTime monotonicity,
full coverage, no test-CA tokens), with byte-identical masked behavioral
equality to the frozen 001 reference, and with mechanism-distinguishability
from retrieval under the frozen composite evidence rule. It does not support:
predictive-performance superiority over retrieval (raw traces show retrieval
matched action-sensitive NLL within margin and outperformed the learner
post-shift by 0.1119 nats), outcome unpredictability (seeded deterministic
simulation), open-world robustness, generalization beyond the declared
environment family, or any agency / functional-subject / consciousness / EGO
/ companion claim.

## 3. Evidence map

Audit re-verification artifacts live under
`artifacts/predictive_action_learning_contract_001c_independent_audit/`
(abbreviated `AUDIT/` below). Frozen suites:
`artifacts/predictive_action_learning_contract_001c/suite_001c_2026-06-10_t1/`
(`001C/`) and
`artifacts/predictive_action_learning_contract_001/suite_2026-06-10_r1/`
(`001/`).

| Claim | Evidence artifact | Raw evidence path | Validator / check | Residual trust assumption | Status |
|---|---|---|---|---|---|
| Every PRE_STEP committed before reveal (protocol) | per-run commit logs + traces | `001C/runs/*/commits.log.jsonl`, `001C/runs/*/trace.jsonl` (PRE `pre_commit_receipt`, POST `obs_reveal_monotonic_ns`) | `validator.validate_chronology` re-run on all 45 runs; 0 errors (`AUDIT/validator_recheck.json`) | monotonic-ns ordering is process-internal | supported |
| Commitments covered by externally verifiable RFC 3161 anchored chain | anchor token sidecars | `001C/runs/*/anchors.log.jsonl` (DER tokens, base64), `001C/suite_anchors.log.jsonl`, `001C/trust_anchors/` | `verify.verify_run_dir` re-run offline: 257/257 tokens ok, chain heads independently recomputed, 0 coverage gaps, genTime monotonic (`AUDIT/anchor_reverification.json`) | signer cert authenticity via embedded cert + recorded fingerprint, out-of-band confirmation; no chain-to-root validation | supported with caveat |
| Anchors are real-TSA, not test CA | token signer certificates | same as above | `is_test_ca=false` for all; signers freetsa.org x254 + digicert x1 + suite x2 | TEST-CA refusal logic itself audited (verify.py reads CN) | supported |
| No local_mock sink in 001C evidence runs | run metadata + receipts | `001C/runs/*/trace.jsonl` RUN_META `commit_mode`, receipt `receipt_type` | `AUDIT/raw_evidence_inventory.json`: 44 runs `rfc3161_anchored`, 1 `disabled` (abl5, by design); `AUDIT/local_mock_scan.json`: all 13 textual hits are derived-header constants or precedence-rule text, none a run record | none | supported (see correction C1) |
| Action-conditioned belief/model update (mechanism gates E6-E13) | raw step records | `001C/runs/*/trace.jsonl` PRE (`raw_pred_obs_by_action`, `raw_pred_belief_by_action`, `belief_pre`, `theta_*_pre`, `uncertainty_pre`), POST (`actual_obs`, `nll_error`, `belief_post`, `theta_*_post`, `transition_responsibility`) | field completeness verified for all 45 runs minus designed ablation drops (`AUDIT/raw_evidence_inventory.json`); E10 components recomputed from raw with my own code: max diff vs gate-reported = 0.0 (`AUDIT/retrieval_recompute.json`); logged NLL vs raw-recomputed NLL max diff 0.0 | seeded deterministic environment | supported |
| Gates computed from canonical raw records, not derived summaries | gate machinery | `001/result.json` E18 (`nll_recompute_max_abs_diff: 0.0`); gates.py reads traces re-parsed from disk | independent E10/NLL/JSD recomputation in this audit reproduced gate-reported values exactly | none | supported |
| Behavior unchanged vs frozen 001 (only commitment swapped) | masked equality | `001C/runs/*/trace.jsonl` vs `001/runs/*/trace.jsonl` | `compare.compare_suite` re-run: 45/45 byte-identical after masking only volatile/sink-identity/dependent-hash fields; mask list verified to contain no behavioral field (`AUDIT/masked_equality_recheck.json`) | mask correctness (inspected: VOLATILE_FIELDS + sink identity + recomputed hashes only) | supported |
| Core runs fully replayable from trace + frozen equations | replay validation | `001C/runs/core_*/trace.jsonl` | `validator.replay_skeleton_run` re-run: core runs max_abs_diff 0.0 at tolerance 1e-9 (`AUDIT/validator_recheck.json`) | none | supported |
| No replay/retrieval/memory leakage in Gate 0 path | attestation + audit hooks | RUN_META flags + POST `external_memory_access_count`, `retrieval_event_log`, `replay_step_count` | `validate_attestation` re-run: 0 errors in core runs; 0 REPLAY_STEP; negative controls abl6/abl8 correctly caught | audit hooks are in-process instrumentation | supported |
| Thresholds/seeds/env/baselines unchanged in 001C | config snapshots | `001/CONFIG.json` vs `001C/CONFIG.json` | deep-diff: identical (incl. `config_manifest_hash` 33032757...); behavioral byte-equality corroborates | pre-001 freeze not provable from VCS (untracked); artifact-internal declarations only | supported with caveat |
| Mechanism-distinguishability from retrieval (composite rule) | retrieval baseline raw traces | `001C/runs/b4_retrieval_*/trace.jsonl` | independent recompute: `retrieval_jsd_null` 0.0292 > 0.02 collapse threshold (false separation) while mechanism collapses at 0.0023; post-shift NLL mismatch -0.1119 outside ±0.05 | composite rule was pre-declared; distinguishability ≠ superiority | supported |
| Predictive superiority over retrieval | — | same raw traces | retrieval matched AS NLL (gap 0.0042 < 0.05) and outperformed post-shift (-0.1119) | — | correctly NOT claimed; would be contradicted by raw evidence |
| Frozen tests pass | test suite | `tests/test_predictive_action_learning_contract_001*.py` | re-run in this audit: 43 passed (`AUDIT/tests_report.txt`) | — | supported |

## 4. T1 commitment audit

What the RFC 3161 anchored chain proves, verified directly in this audit:

1. Every one of the 41,640 commits across 44 anchored runs enters an
   append-only hash chain; recomputing every chain head from the raw
   `commits.log.jsonl` entries reproduced every stored head (0 mismatches).
2. 255 run-level tokens + 2 suite-level tokens parse as RFC 3161
   TimeStampResp, have `status: granted`, carry a messageImprint equal to the
   independently recomputed chain head at the covered seq, bind the expected
   nonce, verify against the signer certificate embedded in the token
   (RSA/ECDSA over the signed attributes), and have monotonic genTime per run.
   Signers: www.freetsa.org (256), DigiCert (1 fallback). Zero tokens signed
   by the test CA; `anchors_signed_by_test_ca = false` is accurate.
3. Coverage is complete: anchor at seq 0, every 200 commits, and a final
   anchor at close; no commit lies beyond the last covered seq in any run.
   The suite start anchor binds the SHA-256 of `CONFIG.json` (recomputed:
   match) and the suite end anchor binds the digest of all final chain heads
   (recomputed: match), so the config could not have been rewritten after the
   runs without breaking the start anchor.
4. abl5_disable_precommit has no anchors by design and its evidence is
   blocked by the frozen gate logic (negative control behaves as designed).
5. The local-mock fallback path was not used in any evidence run: all 44
   anchored runs record `commit_mode=rfc3161_anchored` and receipts of type
   `chained_log_rfc3161_anchor` (see correction C1 for the derived-header
   inconsistency). The sink raises on TSA failure rather than fabricating
   tokens (code inspected read-only; tamper/chain-gap/coverage-gap/test-CA
   refusal paths covered by the 9 frozen 001C tests, re-run passing).

What the anchored chain does not prove — preserved and quantified:

1. Anchors prove committed PRE_STEP content existed no later than the
   anchor's genTime. They do not prove outcome unpredictability — the
   environment is a seeded deterministic simulation; anyone holding the seed
   can compute outcomes in advance. The anchoring evidences protocol
   ordering, not predictive difficulty.
2. Only 211 of 41,640 commits (0.51%; seq ≡ 0 mod 200) are externally
   anchored at their own step. For these, the anchor token was obtained
   synchronously inside `commit()` before the step's reveal; even here,
   "before the reveal" rests on sink control flow plus internal monotonic
   ordering — the token alone proves "no later than genTime" (correction C3).
3. The remaining 41,429 commits (99.49%) are between anchors: their reveal
   ordering rests on internal attestation (flushed append-only chain,
   per-step `commit_monotonic_ns < obs_reveal_monotonic_ns` validated for
   every step, chain prefix bounded above by the next anchor's genTime).
   A process that controlled its own clock and withheld flushes could in
   principle reorder within a 200-commit window without breaking any anchor;
   the frozen record states this dependence and this audit confirms no claim
   exceeds it.
4. `obs_reveal_ts` between anchors is self-reported wall-clock.
5. Signer authenticity: the verifier checks the token signature against the
   certificate embedded in the token and records its SHA-256 fingerprint
   (`trust_anchors/manifest.json`); it does not validate the certificate
   chain to a public root. Out-of-band fingerprint confirmation remains a
   residual assumption.

## 5. Retrieval caveat

The claim boundary is preserved and is the correct reading of the raw
evidence, which this audit recomputed independently from the raw per-step
records (not from any stored summary; recompute-vs-logged max diff 0.0):

| Metric (eval window, recomputed from raw) | Learner | Retrieval (b4) | Reading |
|---|---|---|---|
| Action-sensitive NLL | 0.8812 | 0.8853 | gap 0.0042 < 0.05 margin: retrieval MATCHES predictive performance |
| Shift-regime post-shift NLL | 0.9362 | 0.8243 | retrieval BETTER by 0.1119 nats |
| Null-control all-action JSD | 0.0023 | 0.0292 | mechanism collapses (≤0.02); retrieval falsely separates (>0.02) |
| Action-sensitive all-action JSD | 0.0738 | 0.1335 | both separate |

Predictive-performance superiority over retrieval is unsupported, and on the
post-shift metric the raw evidence points the other way: retrieval was
predictively stronger. Distinguishability rests entirely on the pre-declared
composite rule — principally retrieval's false action-separation in the
null-control regime where action is causally inert (a mechanism property,
not a performance one) together with the post-shift NLL mismatch. No scanned
document claims superiority; the closeout states the caveat explicitly,
including retrieval's post-shift advantage. Threshold-sensitivity note: the
false-separation component sits at 1.46x the 0.02 collapse threshold; the
composite verdict is robust to that single threshold because the post-shift
NLL mismatch (2.2x the margin) independently breaks equivalence, but the
"false separation" wording should not be quoted without its threshold.

## 6. Claim ceiling audit

Scanned: all six PAL docs (`docs/PREDICTIVE-*`), both frozen suites' READMEs,
FINAL_REPORTs, result/metric/report JSONs, all 001/001C package code and the
three test files — 230 term hits for the forbidden vocabulary
(consciousness, subjective experience, sentience, real emotion, agency,
self-awareness, functional subject, electronic life, AGI, companion/EGO
readiness, predictive superiority / outperforms retrieval, final proof of
Bayesian filtering, transformer/scaling refutation, autonomy).

Overclaiming language found: **none**. All 230 hits sit inside forbidden-claim
enumerations, "does not support / must not be quoted as" disclaimers, stop
condition definitions, or audit/task-card text (`AUDIT/claim_language_scan.json`;
the 168 line-level "un-negated" entries were manually reviewed: each is a list
item under a multi-line negation header). The allowed wording (bounded isolated
Gate 0 mechanism evidence; action-conditioned belief/model update evidence;
mechanism-distinguishability from retrieval under the frozen composite
evidence rule; RFC 3161 anchored-chain pre-outcome commitment under residual
trust assumptions) is used consistently.

## 7. Residual trust assumptions

1. Seeded deterministic simulation; no outcome-unpredictability evidence;
   001D randomness beacon remains out of scope and was not started.
2. Between-anchor reveal ordering (99.49% of commits) is internally attested
   only; externally bounded above by the next anchor's genTime.
3. `obs_reveal_ts` between anchors is self-reported.
4. At-anchor-step pre-reveal ordering relies on sink synchronous control flow
   in addition to the token genTime.
5. TSA signer authenticity: token-embedded certificates + recorded SHA-256
   fingerprints; no chain-to-root validation; out-of-band confirmation
   assumed.
6. No version-control freeze evidence: all 001/001B/001C code, docs, and
   artifacts are untracked in git. "Unchanged between 001 and 001C" is
   supported (identical CONFIG.json incl. `config_manifest_hash`,
   byte-identical masked behavior, suite-start anchor binding CONFIG.json at
   run time). "Frozen before the original 001 run" rests on artifact-internal
   declarations (`declared_before_any_run`, threshold justifications) and
   file mtimes only.
7. Anchor genTime granularity is 1 s; TSA-vs-local clock skew
   uncharacterized.
8. Replay tolerance (1e-9) and all gate thresholds are as pre-declared in the
   frozen CONFIG; threshold-sensitivity of the retrieval false-separation
   component noted in section 5.

## 8. Fake-pass paths (most plausible ways 001C could still mislead)

1. Between-anchor ordering dependence: a hostile process could commit and
   reveal out of order within a 200-commit window without breaking any
   anchor; only the 0.51% at-anchor steps and the per-step monotonic checks
   resist this, and the monotonic clock is process-internal.
2. Deterministic seeded simulation: outcomes are computable in advance by the
   process that holds the seed, so "pre-outcome commitment" demonstrates
   protocol ordering, not forecasting ability. Anchors cannot repair this;
   only an external randomness source (out-of-scope 001D) could.
3. Retrieval near-equivalence / predictive strength: the learner does NOT
   predict better than retrieval (matched AS, worse post-shift by 0.1119
   nats). Any quotation of 001C as predictive-performance evidence would be
   a fake pass; the pass is mechanism-distinguishability only.
4. Derived-summary substitution risk: in-suite derived headers
   (commitment_report.json, CONFIG.json `commit_mode`) contradict run-level
   records (correction C1); a reader trusting headers over raw records would
   mis-describe the commitment sink — here in the conservative direction,
   but the same pattern in the other direction would be an overclaim vector.
   The pass itself was re-derived from raw records in this audit.
5. Threshold sensitivity risk: retrieval false-separation sits at 1.46x the
   collapse threshold; E6 separation (0.0738) at 1.48x `sep_min`; post-shift
   recovery margins are larger but finite. Thresholds were not changed (deep
   identical CONFIG), but no VCS history pins their pre-001 declaration.
6. Baseline framing risk: distinguishability rests on the pre-declared
   composite rule. Under a pure predictive-NLL framing, retrieval would be
   equivalent-or-better; the composite rule's null-control component is what
   separates mechanism from lookup. This is stated, not hidden, but any
   summary that drops the framing would overstate the result.
7. Certificate / fingerprint verification assumptions: verification trusts
   token-embedded certificates; a forged token chain signed by a key whose
   certificate falsely carries a real-TSA CN would pass CN-based test-CA
   refusal. Fingerprints are recorded for out-of-band confirmation but this
   audit did not (and offline cannot) confirm them against TSA-published
   values.
8. Replay-label risk (minor): `hidden_state_needed: true` for abl4 in
   replay_report.json could be misread as a core-mechanism replay defect;
   it is an ablation-only logging asymmetry (correction C2); core-run replay
   is exact.

## 9. Stop conditions triggered

None. Checked against the card's eleven stop conditions: no core change was
needed to complete the audit; no post-hoc threshold/seed modification was
detected (identical CONFIG snapshots; mtime nuance documented in section 7
item 6); raw canonical evidence was available for every major claim; PRE_STEP
commitment coverage verified for all 44 anchored runs; anchor verification
succeeded (257/257); no local_mock path was used in evidence runs; no
REPLAY_STEP in Gate 0 evidence; report language preserves the retrieval
caveat; no major claim rests solely on derived summaries; 001D was not
started; no forbidden-claim language found.

## 10. Required corrections

None blocking. All are wording/report corrections; none may be implemented
without separate authorization; none affect the verdict.

1. **C1 (wording/report correction only).** `001C/commitment_report.json`
   header block and `001C/CONFIG.json` carry frozen 001 constants
   (`commit_mode: local_mock`, `externally_verifiable: false`,
   `receipt_type: local_mock`) contradicted by every run-level record and by
   the sample receipts inside the same commitment_report file
   (`chained_log_rfc3161_anchor` with anchors). FINAL_REPORT_001C flags this
   precedence for result.json but not explicitly for commitment_report.json /
   CONFIG.json. Error direction: conservative (under-claims external
   verifiability). Suggested fix if authorized: extend the FINAL_REPORT_001C
   supersession note to name those files.
2. **C2 (wording/derived-label correction only).** replay_report.json
   `hidden_state_needed: true` for abl4_freeze_belief_update mislabels a
   runner-logging vs replay-check field-semantics asymmetry (runner logs the
   applied belief, `runner.py:251`; replay compares the computed posterior,
   `validator.py:214`) that manifests only under the belief-freeze ablation.
   abl9's replay failure is the structurally expected consequence of an
   un-traced mid-run deletion intervention. Both were transparently recorded
   as failures in the frozen 001 record and reproduce bit-identically in
   001C; no gate or claim depends on them (E3 gates core runs only; core
   replay max diff 0.0).
3. **C3 (wording/precision, optional).** Make explicit that at-anchor-step
   "commitment before that step's own reveal" combines the external genTime
   bound with sink control flow and internal monotonic ordering.

No evidence-record correction, validator correction, or protocol-level
blocker is required. No new bounded task is required to keep the frozen
verdict; the only evidence upgrade that would change the trust profile
(external randomness, between-anchor external ordering) is the explicitly
out-of-scope 001D family.

## 11. Final claim ceiling

```text
001C has passed-with-caveats the independent evidence audit for bounded
isolated Gate 0 predictive-action mechanism evidence.
```

No stronger claim is allowed. This audit does not prove: consciousness,
subjective experience, real emotion, self-awareness, agency,
functional-subject evidence, electronic life, AGI, companion readiness, EGO
mainline readiness, predictive superiority over retrieval, outcome
unpredictability, open-world robustness, generalization beyond the declared
3x3x3 seeded environment family, pre-001 threshold freezing (no VCS
evidence), or correctness of any total theory (Bio-CMBC, CVPSM, VCCO, CMBC,
R/G).

## Appendix: audit execution record

Files changed: none in frozen suites or runtime code (verified by re-running
masked equality and anchor verification AFTER all audit writes; `git status`
shows only the new audit paths as additions). New audit-only files:
`docs/audits/PREDICTIVE_ACTION_LEARNING_CONTRACT_001C_INDEPENDENT_AUDIT.md`
and `artifacts/predictive_action_learning_contract_001c_independent_audit/`
(15 files, listed in result.json).

Commands run: offline anchor re-verification + masked-equality recheck +
45-run validator/replay recheck + independent E10 recomputation
(`audit_scripts/run_audit.py`); forbidden-language scan
(`audit_scripts/scan_claims.py`); frozen test suites
(`python3 -m pytest tests/test_predictive_action_learning_contract_001.py
tests/test_predictive_action_learning_contract_001_baselines.py
tests/test_predictive_action_learning_contract_001c.py -q`, 43 passed);
CONFIG deep-diff; git status; read-only code inspection of sink/verify/
driver/compare/validator/gates/runner/skeleton/commitment/fake_tsa.

Dependencies installed for verification only: asn1crypto, cryptography,
pytest (sandbox-local; no repo change).
