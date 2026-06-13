# CLAUDE-INDEPENDENT-EVIDENCE-AUDIT-GATE4-REPLACEMENT-DISCRIMINATIVE-SOCIAL-LATENT-IMPLEMENTATION-001B

This document preserves an independent read-only Claude audit of sealed commit
`ec11f88cf90f7ff1efe77a91830cd7d42f598dc4`.

The audit verdict is preserved as written:

```text
blocked_split_design_failure
```

This preservation record does not implement a repair, rerun the 001B harness,
modify 001B artifacts, or authorize Gate5, admission, bridge, runtime,
EGO-mainline, agency, selfhood, consciousness, real emotion, relationship
learning, stable autonomy, or user-benefit claims.

---

# Independent Implementation Evidence Audit: Gate4 Replacement Discriminative Social Latent 001B

## Verdict

```
Verdict: blocked_split_design_failure
```

The committed evidence at `ec11f88` is **genuinely computed and reproducible** — it is not
self-reported JSON, static literals, decorative traces, or non-recomputed replay. Those
hypotheses are refuted (see positive findings below). However, the audit is **blocked** on the
"Leakage Surface" arm of Split Design (Area 9): the episode generator encodes the prediction
target into an allowed observation feature (`baseline_hint`) as a deterministic, invertible
cyclic shift. An **unmandated, observation-only, single-feature baseline recovers the target with
score 1.0**, which means the candidate's headline margin (1.0 vs 0.2857) is partially explained by
*observation leakage + mandated-baseline-menu weakness*, not solely by a genuine
observation-vs-action-conditioning gap. This violates the project anti-hardcoding contract
("leaks labels through observations") and makes the *discriminative* social-latent premise not
credibly established by this harness.

Implementation may **not** proceed to admission/bridge/Gate5/EGO on this evidence. A re-audit is
warranted after the Required Repairs.

## Layer

Engineering implementation + mechanism-hypothesis test execution (independent evidence review of a
sealed offline toy harness). No subjectivity / consciousness / agency layer is in scope or claimed.

## Anchor Readback

All anchors match exactly. No anchor mismatch.

| Check | Expected | Observed | Result |
|---|---|---|---|
| HEAD | `ec11f88...8dc4` | `ec11f88cf90f7ff1efe77a91830cd7d42f598dc4` | OK |
| `ec11f88` resolves | itself | identical | OK |
| 001B tag -> commit | `ec11f88` | `...f598dc4` | OK |
| Parent of `ec11f88` | `e70a997...660e9` | `e70a9971f81ce00ee9b5a048abf5f4aae46660e9` | OK |
| Parent tag -> commit | `e70a997` | `...46660e9` | OK |
| Commit author/committer | - | `Zhouyu` / `Zhouyu`, 2026-06-12, "feat: implement Gate4 replacement 001B harness" | OK |
| Object integrity | valid | `commit` + `tree` types valid; commit body reproduces evidence | OK |
| Staged (cached) diff | empty | 0 files | OK |

**Worktree-cleanliness caveat (non-blocking, mount artifact - NOT content divergence):**
`git status` reports 1538 "modified" files. Byte-level diagnosis shows this is a Windows->Linux
FUSE-mount rendering artifact, not divergence from the sealed commit:
- 1530 files differ **only** by CRLF<->LF line endings (HEAD blob = LF, worktree render = CRLF;
  first differing byte is an inserted `\r`).
- 8 files (all in the *parent* `...task_card_001a/` dir + its doc, **none** in 001B paths) are
  **truncated reads** in the mount (working copy cut off mid-line, shorter than the sealed blob).
- The committed git objects at `ec11f88` are complete and well-formed.

Because the worktree is unreliable in this mount, **the entire audit was conducted against the
sealed git objects** (`git archive ec11f88 ...` -> clean extraction), not working-tree files. The
dirty-worktree gate's *intent* (audit the sealed commit, not a modified copy) is satisfied more
strictly this way. Recommend `core.autocrlf=false` + a fresh checkout for the user's local tree.

## Scope / File Boundary

**Clean.** `git diff --name-status e70a997 ec11f88` = 32 files, all `A` (added), strictly within
the three allowed paths:

- `src/gate4_replacement_discriminative_social_latent_001b/` — 13 `.py` files (1600 LOC)
- `tests/test_gate4_replacement_discriminative_social_latent_001b.py` — 1 file (365 LOC)
- `artifacts/gate4_replacement_discriminative_social_latent_001b/` — 19 artifacts (incl. `trace_records.jsonl`)

No change to old Gate4 001C artifacts, mainline runtime, bridge, admission, Gate5, UI, LLM, AIRI,
relationship, emotion, deployment, or external-service paths. Old-001C non-mutation is enforced
and verified (`non_mutation_guard.json`: `old_hashes_before == old_hashes_after`, populated).

## Artifact Readback

All 19 required artifacts present under the task artifact dir. **Reproduction check:** an
independent re-run from the sealed code into a throwaway output dir reproduced **18/19 artifacts
byte-for-byte**. The single difference is `non_mutation_guard.json`, fully explained (it embeds
SHA-256 hashes of the old-001C dirs, which are absent from the isolated extraction; within the
committed artifact, before == after, so non-mutation holds). This is strong determinism evidence
that the committed artifacts were produced by the committed code, not hand-edited.

## Computed Evidence Provenance Audit

**Score-bearing results are genuinely computed (PASS on the core question), but the dedicated
provenance manifest is partly decorative (non-blocking defect).**

Genuine: candidate, baseline, ablation, threshold, margin, replay, split-coverage results are all
produced by callable functions invoked by `runner.execute_bounded_run`; per-row records carry real
producer hashes (`candidate.code_path_hash(run_candidate_on_episode)`,
`baselines._code_path_hash(predict_with_baseline)`). Re-run reproduces every headline number, which
refutes static-literal injection.

Defects in `computed_evidence_provenance.json` / `provenance.py` (non-blocking):
- `code_path_hash = _code_path_hash(_producer_for_family)` hashes the **lookup helper**, identical
  across all 12 families — it does **not** bind each result to its real producer.
- Records carry **no actual scores**; the manifest is descriptive, not score-binding.
- `verify_provenance` only checks field *presence*. Its `static_score_injection` and
  `producer_function in {static_json_literal, handwritten_pass}` guards are **vacuous** — the
  producer never sets those, so they fire only under the test's manual injection, never organically.

Not blocking because the *actual* computation is independently provable (re-run + per-row producer
hashes in `candidate_results.json` / `baseline_results.json`).

## Baseline Independence Audit

**Independence holds by code inspection; the dedicated "independence verifier" is a self-report.**

- All 14 mandated baselines present and invoked per split (`verify_baseline_invocations` is a real
  coverage computation over recorded invocations).
- `predict_with_baseline` is a pure function of observation features / split family and `_stable_index`
  (SHA-based). It **never imports or calls** candidate policy/update/state code, reads no candidate
  traces, shares no hidden state. Confirmed by reading every branch.
- `oracle_label_positive_control` returns the label; `select_strongest_baselines` picks the max
  ordinary baseline by **computed** score; the test asserts `baseline_id == computed_from_scores.baseline_id`.
- Disabling a baseline fails the harness — but via a **categorical override** (`runner` lines
  111-114 hardcode `verdict="blocked_baseline_independence_failure"` when `disabled_baselines` is
  non-empty), not an organic metric collapse. Defensible as a "suite must be complete" guard, but
  it is a guard, not evidence.
- `verify_baseline_independence()` returns hardcoded `passed:True` / `shares_candidate_policy:False`
  for all rows **without inspecting code** (non-blocking; the real independence is true anyway).

No baseline is a wrapper around candidate logic. Independence: **PASS** (with the self-report caveat).

## Metric / Threshold Recompute Audit

**PASS — every headline value recomputed from a fresh run, matching the committed report exactly.**

| Metric | Committed claim | Independent re-run | Match |
|---|---|---|---|
| candidate score | 1.0 | 1.0 | OK |
| strongest ordinary non-oracle baseline | `transition_table` | `transition_table` | OK |
| strongest baseline score | 0.2857142857142857 | 0.2857142857142857 | OK |
| oracle positive-control score | 1.0 | 1.0 | OK |
| aggregate margin | 0.7142857142857143 | 0.7142857142857143 | OK |
| per-split margins | 0.4-0.6 | {0.4, 0.6} across 7 splits | OK |
| repeated-seed | 5/5 | seeds 0-4 margins 0.43-0.71, passing=5 | OK |
| active-query ablation drops | 1.0 | no_active_query / shuffled_feedback / counterfactual_transition = 1.0 | OK |

Threshold logic (`evaluate_thresholds`) is computed, not literal: ties block; aggregate >= 0.15;
each split >= 0.10; repeated-seed (>=5 seeds, >=4 with margin >= 0.15); oracle must beat strongest
ordinary baseline (else `harness_invalid_oracle_positive_control_failure`). Tested for the tie,
oracle-failure, and disabled-baseline failure paths.

## Active-Query Causal Audit

**Mixed: ablation drops are real reruns (causal); the report's structural flags are decorative.**

- `ablations.run_ablation_suite` performs genuine `candidate.rerun_with_intervention(...)` reruns
  through the candidate code for all six interventions; scores and drops are computed; `episode_run_ids`
  differ from the baseline run. Removing the active query (using `initial_state()` at decision time)
  collapses the candidate to its fallback -> score 0 -> drop 1.0. Shuffled / counterfactual feedback ->
  wrong belief -> score 0. These are real, recomputed causal contrasts within the toy.
- **But** `active_query_causal_report` hardcodes `uncertainty_before_query=True`,
  `feedback_dependent_update=True`, `later_action_depends_on_updated_state=True`. Only `drops`/`passed`
  are computed. The causal *evidence* exists (in the reruns); the report's *flags* are self-asserted.

Caveat that limits how much this proves: the drop magnitude is inflated by the same leakage defect
— the candidate's fallback is `baseline_hint`, deliberately set to `target+1` (always wrong), so
"remove the query" collapses to 0 by construction rather than to a fair observation-only optimum.

## Budget Parity Audit

**Counts computed; parity verdict NON-FAIL-ABLE (non-blocking defect, recurring family).**

`compute_budget_parity_report` derives the counts from real run artifacts (episode/context counts,
`memory_write_count` summed from traces, etc.). **However**, every row's `classification` is the
hardcoded literal `"equal"`, regardless of the actual values. Demonstrated:

```
field=oracle_label_access_count -> candidate=0  oracle=35  classification="equal"
verify_budget_parity passed = True   (despite candidate 0 vs oracle 35 on that field)
distinct classifications emitted by producer = ['equal']
```

`verify_budget_parity` can only fail if a row is classified into the blocking set, but the producer
never emits a blocking classification — so in practice the verifier **cannot fail**. The test masks
this by *manually* mutating a row to `"unknown"`. (The oracle's label-access disparity is expected
by design, but it should be *computed and justified*, not blanket-labeled "equal".)

## Leakage Positive-Control Audit

**Scanner is fail-able (PASS on that gate); real-bundle scan is engineered-clean (non-blocking defect).**

- `build_positive_control_report` runs a deliberately contaminated payload through the **same**
  `scan_payload_bundle` / `_detect_in_text` path; it detects all forbidden tokens ->
  `positive_control_detected=True`. The on-disk `scan_bundle` is separately tested with clean vs
  contaminated bundles and marks excluded paths `not_scanned` (not `clean`). The scanner is **not**
  an unconditional clean emitter.
- **But** the *real* bundle is passed through `_leakage_safe_summary` (which string-replaces the
  exact forbidden key tokens `seed_id->seed_ref`, `oracle_latent_label->oracle_ref`, ...) **before**
  scanning. The real-bundle "clean" verdict therefore does not test the un-sanitized evidence, and
  the detector only matches a fixed token list by substring (it would not catch a leaked *value*).
  Recommend scanning the un-sanitized bundle or the persisted on-disk artifacts.

## Replay Re-computation Audit

**Core replay is genuine recomputation (PASS); the corrupted-state control is vacuous (non-blocking defect).**

- `recompute_trace_record` rebuilds `CandidateState`/`Observation`/`Feedback` from the trace and
  re-invokes `candidate.update_from_feedback` + `candidate.choose_final_action`, comparing the
  recomputed action **and** state-after to the stored values (`uses_hash_only_comparison=False` is
  truthful — it really recomputes, for all 35 records).
- `corrupt_feedback` and `corrupt_observation` controls are **real** (they mutate input, recompute,
  and detect the mismatch — confirmed: they return full recomputed fields with `passed=False`).
- `corrupt_state` (lines 19-20) **short-circuits**: `if corrupt_state: return {"passed": False,
  "failure_reason": "corrupted_state_detected"}` — it returns *before* any recomputation. Confirmed
  empirically: the returned dict contains only `{failure_reason, passed}`, with no
  `recomputed_action` / `action_recomputed`. It provides **zero** evidence that state corruption is
  actually caught by recomputation. The test asserts this canned value, giving false confidence.

## Split Design Audit

**BLOCKING — leakage surface.** Coverage itself is fine: all 7 mandatory split families are
generated and used; no unused frozen seed / train / heldout / counterfactual / remapped-ID material
(verified by `compute_split_coverage` and the unused-material failure test). The 35 episodes =
7 splits x 5 frozen seeds.

The blocking defect is in the episode *content* design (`episodes.generate_episode_records`):

```
action_index  = (split_index + seed_index) % 4
target        = ACTIONS[action_index]
baseline_hint = ACTIONS[(action_index + 1) % 4]   # <-- deterministic +1 cyclic shift of target
observation.prompt_features["baseline_hint"] = baseline_hint   # allowed, NOT in FORBIDDEN_DECISION_FIELDS
```

So `target = ACTIONS[(index_of(baseline_hint) - 1) % 4]` — the label is recoverable from a single
observation feature by inverting a fixed offset. **Probe result (35 episodes):**

```
UNMANDATED hint_inverter (observation-only, 1 feature) : score 1.0
best MANDATED ordinary baseline (transition_table)     : score 0.2857
candidate (uses feedback)                              : score 1.0
```

Consequences:
1. The premise that the social latent is **not observation-recoverable** (the reason
   action-conditioned querying should be necessary) is **false** in this harness.
2. The candidate's 1.0-vs-0.2857 margin is partly an artifact of (a) target-in-observation leakage
   and (b) the mandated baseline menu omitting the trivial inverter — both named in the Primary
   Audit Question as pass-invalidating ("baseline weakness", "leakage").
3. This violates the explicit anti-hardcoding rule: *"leaks labels through observations ... stop and
   report the failure."*

This does not falsify the *computation* (everything reproduces); it falsifies the *discriminative
interpretation* of the result.

## Test Quality Audit

**Above the "merely asserts pass JSON" bar, but rubber-stamps several decorative self-reports.**
14/14 tests pass in an isolated copy. Genuine failure-path coverage: forbidden-field rejection,
unused-material -> coverage block, candidate/baseline tie -> negative verdict, oracle failure ->
harness-invalid, disabled baseline -> block, on-disk leakage clean-vs-contaminated, budget
`"unknown"` -> verify fail, provenance injection -> verify fail.

Weaknesses:
- Several asserts target hardcoded booleans (`rerun_performed`, `post_hoc_score_edit`,
  `action_recomputed`, `shares_candidate_policy`) rather than recomputed facts.
- Fail-ability of budget/provenance verifiers is shown only by **manual injection**; no test
  exercises an *organic* failing run (because the producers can't emit one).
- `corrupt_state` test asserts the vacuous short-circuit value.
- `test_materialized_artifacts...` writes to the **real** `ARTIFACT_DIR` (rerunning the suite against
  the repo overwrites committed evidence — the audit avoided this by using an isolated copy).
- No test encodes the observation->target leakage check (an "observation-only must not beat oracle
  gate" guard), which is exactly the missing assertion that would have caught the blocking defect.

## Blockers

1. **`blocked_split_design_failure` (observation->target leakage).** `baseline_hint` deterministically
   encodes the target (`target+1` cyclic shift); an unmandated observation-only baseline scores 1.0;
   the discriminative social-latent premise is not credibly established and the margin is partly
   explained by leakage + baseline weakness. Anti-hardcoding contract violation.

## Required Repairs, If Any

Blocking (must fix before re-audit):
1. Decouple `baseline_hint` (and every observation feature) from `target`. Use a decoy that is **not**
   a deterministic invertible function of the target (e.g., a fixed constant, or a frozen-seed value
   provably independent of the label). Add a harness self-check that **no** observation-only function
   recovers the target above an acceptable bound (i.e., the latent is only feedback-recoverable).
2. Add an observation-decode / "best observation-only predictor" challenger to the baseline suite so
   the harness actively rules out observation-only solutions; require the candidate to win **only**
   through the feedback path on a genuinely non-observable latent.

Strongly recommended (non-blocking, fix in the same pass — they make the gates non-fail-able today):
3. Make `budget_parity` `classification` computed per field (compare candidate/ordinary/oracle;
   mark expected oracle disparities as justified-by-design, flag the rest) so `verify_budget_parity`
   can fail organically.
4. Make `replay.recompute_trace_record(corrupt_state=True)` actually mutate the state payload and
   recompute (parallel to `corrupt_feedback`/`corrupt_observation`).
5. Bind `provenance` `code_path_hash` to each family's real producer; reference the actual computed
   scores; make the static-injection guard non-vacuous.
6. Scan the **un-sanitized** real bundle (or the persisted on-disk artifacts via `scan_bundle`),
   and detect leaked values, not only field-name tokens.
7. Replace decorative booleans (`active_query_causal_report` flags, `verify_baseline_independence`,
   `rerun_performed`/`post_hoc_score_edit`) with computed checks; add a test that asserts an
   **organic** failing run, and a test that an observation-only predictor cannot beat the oracle gate.

## Claim Ceiling

This audit can claim only **independent evidence-review status for the bounded isolated toy harness**.
The strongest defensible statement about `ec11f88` after this audit is:

> The 001B harness is honestly engineered and fully reproducible (computed, not fabricated), with
> independent baselines, a fail-able leakage scanner, and genuine replay/ablation recomputation —
> **but** it does not currently provide credible *discriminative social-latent* evidence, because the
> target leaks into observations and the candidate's margin is partly explained by baseline weakness.

It cannot validate replacement-Gate4 general validity, social-latent mechanism validity outside this
harness, Gate5 / admission / bridge / EGO-mainline readiness, agency, selfhood, consciousness, real
emotion, relationship learning, stable autonomy, or user benefit.

## What This Does Not Prove

- It does not prove the candidate mechanism is invalid — only that *this harness* does not isolate it
  from observation leakage. A repaired harness could still pass or fail.
- It does not prove fabrication or dishonesty; the computation is genuine and reproducible. The block
  is a *design/discriminative-validity* failure, not an integrity failure.
- It does not authorize Gate5, admission, bridge, runtime, or EGO mainline under any reading.
- A future PASS (after repairs) would mean only: "bounded isolated 001B implementation evidence
  appears internally credible under the sealed toy harness after independent audit" — nothing stronger.

---
*Independent read-only audit. No repo files, commits, tags, artifacts, or thresholds were modified.
Audit conducted against sealed git objects at `ec11f88` extracted via `git archive`; re-runs and the
test suite executed only in throwaway temp copies.*

