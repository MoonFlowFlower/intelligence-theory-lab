# CLAUDE-INDEPENDENT-ACTION-CONDITIONED-SELF-BOUNDARY-001B-HOSTILE-AUDIT-001A

Independent hostile audit (read-only, no implementation) of
`ACTION-CONDITIONED-SELF-BOUNDARY-EXECUTABLE-PREFLIGHT-001B-LEARNED-BASELINE-SCALING-CHALLENGE`.

## Verdict

`claude_independent_acsb_001b_audit_blocks_on_learned_baseline_invalidity`

Co-equal second blocking axis (would independently justify a block):
`claude_independent_acsb_001b_audit_blocks_on_capacity_matched_baseline_invalidity`.

The bounded claim **"offline learned-baseline / scaling challenge evidence survived"
is NOT supported.** The 001B run is engineering-clean (callable module, deterministic
artifacts, genuine replay, fail-able leakage scanner, computed provenance, no oracle
leakage into legal inputs), but its three headline discriminative axes —
learned-baseline, capacity-matched-disabled reference, and core ablations — are
non-fail-able by construction: every challenger is a hand-written deterministic
readout wired to return a non-target channel. `reference = 1.0` vs `challengers = 0.0`
is a *designed* separation, not an *earned* one.

## Canonical state audited

* Boundary: `ACTION-CONDITIONED-SELF-BOUNDARY-EXECUTABLE-PREFLIGHT-001B-LEARNED-BASELINE-SCALING-CHALLENGE`
* Commit audited: `347b75b9fcf610d0eb93206da20297057ead220a` (extracted via `git archive`, LF-clean)
* Branch: `codex/meta-theory-scaffold`; packed-ref confirms tip = `347b75b9…`
* Method: audited the committed blobs at `347b75b`, not the working tree.
* **Worktree-hygiene note (non-blocking for 001B):** the live working tree at audit
  time is dirty — whole-file CRLF rewrites across ~1965 files, plus `AGENTS.md` with
  its 76-line governance block deleted (matches the prior cross-family-social audit
  observation). These are **uncommitted**; the anchored commit `347b75b` retains the
  full `AGENTS.md`, so 001B's evidence integrity is unaffected. Flagged only as repo
  hygiene.

## Current layer

Engineering-governance / independent hostile audit of offline executable preflight only.

## Mainline integration status

None. 001B reports `mainline_integration_status: none`, `gate_bridge_runtime_or_ego_mainline_enabled: false`; confirmed — no runtime/Gate/LLM/EGO path is touched.

## Enabled status

None beyond the local offline module, tests, and artifact generation already reported by 001B.

## Real trigger evidence

Callable local 001B execution produced 13 artifacts under
`artifacts/action_conditioned_self_boundary_executable_preflight_001b/`. Verified
present and self-consistent: `result.json`, `scores.json`, `baseline_comparison.json`,
`ablation_report.json`, `leakage_scan.json`, `replay_report.json`, `provenance.json`,
`trace.jsonl`, `failure_manifest.json`, `summary.md`, `claim_ceiling.txt`,
`git_readback.json`, `episodes.json`.

## Claim ceiling (of this audit)

Independent audit verdict only. This audit does not assert mechanism validity, Gate
validity, candidate behavior, agency, autonomy, consciousness, emotion, subjectivity,
runtime/EGO readiness, stable user benefit, or any mainline effect.

## Audited files / artifacts

* `src/action_conditioned_self_boundary_executable_preflight_001a/learned_scaling_001b.py` (1649 lines — the 001B challenge module)
* `src/action_conditioned_self_boundary_executable_preflight_001a/runner.py` (1584 lines — 001A primitives: reference path, baselines, ablations, leakage scanner)
* `tests/test_action_conditioned_self_boundary_executable_preflight_001b.py` (300 lines)
* All 13 artifacts above (per-baseline scores extracted from `scores.json`).

## Strongest support for 001B (what is genuinely solid)

1. **No oracle/label leakage into legal inputs.** The reference and every baseline are
   scored through one path, `_score_callable_001b`, which feeds only
   `legal_input_for_episode_001b(episode)` = `{serialized_state, legal_observation,
   intervention}`. The legal observation contains no `target_channel`; `target` lives
   only in `episode["expected_measurable_object"]`, which is never passed to any scored
   function. `boundary_update_reference_path` reads only legal fields.
2. **Reference is a legitimate computation, not a static literal.** It computes
   `evidence[ch] = action_counts[ch] − (no_action_counts[ch] + external_counts[ch])`,
   argmax → channel. Replay confirms it is sensitive to both serialized state
   (`update_rate→0` flips it to the prior) and observation (channel replacement flips
   it), invariant to metadata-only mutation, and raises on missing
   `action_effect_evidence`.
3. **Leakage scanner is fail-able and exercised.** Six positive controls inject
   `target_output`/`target_action`, `oracle_boundary_label`, `benign_answer_alias`,
   `hidden_id: answer_map:*`, `future_outcome`, and `precomputed_verdict/score`; all six
   are blocked. The test then runs `disable_leakage_positive_controls=True` and asserts
   the verdict flips to `blocked_by_leakage_positive_control_failure_001b` — i.e. the
   scanner can fail the run. A contaminated baseline that reads an injected
   `target_output` reaches `1.0`, proving the exploit channel is real.
4. **Provenance computed, static-score detection tested.** Score records carry
   `score_source=callable_computation`, `input_hash`, `code_path_hash`; the test injects
   a `static_literal_score` record and asserts verification fails.
5. **Claim-ceiling discipline is present.** `result.json` sets every
   `*_claimed=False`, lists `what_this_does_not_prove`, and a forbidden-positive-claim
   scanner + changed-file allowlist both pass.

These points dispose of audit questions Q6 (no reference privilege/leak), Q8 (leakage
controls complete + fail-able), Q9 (replay recomputes, not a stored verdict), Q12
(no report-shaped/static path survives) — none of these are the failure.

## Strongest objection to 001B (the block)

**The "learned-baseline scaling challenge" was never actually run.** The challengers
that produce the `0.0` scores are not learners and not fair, so the `reference 1.0 vs
challenger 0.0` gap is an artifact of how the challengers were written, not evidence
that an action-conditioned self-boundary update is required.

Grounding (CHANNELS = `[alpha, beta, gamma, delta]`, 4-way; per episode
`target=index%4`, `decoy=index+1`, `external=index+2`, `prior=index+3`):

* `learned_feature_mlp_without_boundary_state` — explicitly `"ml_library_used": False`,
  `"deterministic_lightweight_feature_mlp_fallback"`. It computes `max(action_counts)`
  over boundary channels and ignores `no_action_comparison` and
  `external_effect_comparison` — the very fields that disambiguate `target`. Because
  action effects are tied (`target` and `decoy` both appear in every self-action row by
  construction), its `(count, −first_seen)` tie-break deterministically selects `decoy`
  → `0.0` on every probe/seed.
* `sequence_model_without_boundary_update` — deterministic; returns the last changed
  channel of the last legal-sequence row (an external row) → `0.0`.
* `embedding_knn_or_episodic_retrieval_baseline` — deterministic nearest-neighbour by
  string feature distance, returns `changed_channels[0]` of the nearest row → `0.0`.
* `capacity_matched_boundary_disabled_reference` — computes `action/no_action/external`
  counts (the "capacity") then **discards them and returns
  `serialized_state["stale_prior_channel"]`** (= `prior` = `index+3`), which is never
  `target`. Forced to `0.0` by construction; not capacity-matched, just crippled.

`grep` over the whole package: **no `numpy`/`torch`/`sklearn`/`tensorflow` import, no
`.fit(`, no gradient, no train/test split anywhere.** There is no learner to challenge.

The verdict gate (`_build_result`) defaults to `…survives…` and only downgrades if a
challenger reaches the reference, the capacity reference fails to degrade ≥0.20, the
non-oracle margin <0.15, or a core ablation degrades <0.20. Given the implementations
above, **none of those conditions can ever trigger** — the headline gate is
non-fail-able on exactly the three axes (learned, capacity, ablation) it claims to test.

## Learned-baseline validity assessment — FAIL (primary block)

Audit Q1/Q2/Q4. The three "learned" baselines are deterministic heuristics named after
ML methods. They are callable but not trained/fitted (Q1 fails). Their *inputs* are fair
— they receive the full legal observation including the discriminative no-action/external
rows (Q2 nominally OK) — but each hand-coded readout deliberately ignores those fields,
so their `0.0` is engineered blindness, not task structure forbidding a no-boundary
solution (Q4 fails). A genuinely fitted classifier over the flattened legal observation
(which includes the no-action and external rows) would very plausibly recover the
`action − background` separation and exceed `0.0`. Acceptance criteria 1 and 4 fail;
stop condition "learned baselines are dummy, non-training, or structurally unable to
learn" is triggered.

## Capacity-disabled baseline assessment — FAIL (second block)

Audit Q3. `capacity_matched_boundary_disabled_reference` returns `stale_prior_channel`,
structurally disjoint from `target` (`index+3 ≠ index mod 4`). It is rigged to `0.0`;
the counts it computes are decorative. The reported `degradation ≥ 0.20` is therefore
uninformative. Acceptance criterion 3 fails; the dedicated stop condition
"capacity-disabled reference is not a fair challenger" is triggered.

## Random-baseline residual assessment — benign (NOT a block)

Audit Q5. `random=0.458333` on `combinatorial_heldout` is **not** a low-entropy-collapse
signal. `majority_baseline = 0.25` on all three probes confirms the target is ~4-way
uniform (entropy ≈ 2 bits); `random` is `0.125 / 0.2 / 0.458` across probes, i.e. an RNG
fluctuation over a 4-class target (11/24 on the unlucky seed), not a near-binary target.
I do not block on entropy collapse. (See split-hardness for the real, weaker concern.)

## Split-hardness assessment — weak (non-blocking, but undermines "scaling/heldout")

Audit Q10. Each probe is 16–24 fully deterministic episodes with `target = index mod 4`.
`small_reproduction` self-declares `row_enumerable_from_training: True`. The
`combinatorial_heldout` / `noisy_decoy_intervention` "heldout" only varies
`surface_family` / `context_id` strings; the *solving rule* is identical in train and
heldout (always `action − no_action − external`). So nothing about "scaling" or
"combinatorial generalization" is actually probed — the finite challengers
(`transition_table`, `fsm`, `graph_cache_episodic_traversal`, `recency`,
`action_effect_frequency`) score `0.0–0.25` because they too are hand-coded to skip the
counterfactual subtraction, not because a memorization shortcut was defeated. The probe
prevents transition-table/FSM/graph-cache solutions only in the trivial sense that those
baselines never attempt the subtraction.

## Leakage assessment — PASS

Audit Q8. Controls cover alias, hidden-ID answer-map, future outcome, oracle label,
explicit target, and stored verdict/score. Scanner flags forbidden keys/fragments over a
full dict walk; `normal_legal_input.blocked = false`; all 6 controls blocked; disable→
verdict flip proves fail-ability; contaminated exploitation = `1.0`. No leakage block.

## Replay / provenance assessment — PASS

Audit Q9. `run_replay_001b` recomputes each path from `(serialized_state, observation,
intervention)`: determinism (`direct == replayed`), state-mutation sensitivity,
observation-mutation sensitivity, metadata-mutation invariance, and missing-input raise.
`uses_stored_verdicts: false`, `uses_stored_hashes_only: false`. Provenance verification
checks required fields + `callable_computation` and is shown to reject an injected static
record. Caveat (non-blocking): replay exercises only the first episode of the first
probe; sensitivity uses `any(...)` over paths, so a single path satisfies it (the
reference does). Adequate for a preflight, not a generalization claim.

## Test-strength assessment — mixed

Audit Q11. Stronger than several prior lab audits: tests fail under baseline removal
(`missing_* == []` + required-set loops), leakage-scanner disablement (verdict flips),
and static-score injection (provenance fails). **But** the tests *encode the conclusion*
(`assert reference_score == 1.0`, `assert verdict == …survives…`), and the only
learned-baseline guard, `strongest_learned["score"] < reference_score`, is satisfied by
*any* value below 1.0 — including the engineered `0.0`. No test asserts a learner is
trained, that a no-boundary model given fair features still fails, or that any ablation
is mechanism-specific rather than a constant. So the suite cannot catch the actual
defect; it ratifies it.

## Ablation assessment — partially non-mechanistic (supporting, non-primary)

Audit Q7. Of the six ablations, `freeze_boundary_update` (sets `update_rate→0`, re-runs
reference) and `shuffle_action_effect_linkage` (re-runs reference on shuffled effects)
are genuine mechanism ablations. But `remove_action_conditioned_contingency` and
`reset_state_before_probe` — **two of the four declared CORE ablations** — return a
constant `"unresolved"` and ignore their inputs entirely, so their `1.0` degradation is
trivially true and mechanism-independent. `remove_no_action_counterfactual` and
`replace_boundary_state_with_recency_state` return a fixed wrong channel
(`rows[0][0]=decoy`, `external[-1][0]=external`). The ablation evidence is therefore
half decorative.

## Blocking issues

1. **Learned-baseline invalidity** — all three "learned" baselines are untrained
   deterministic readouts (`ml_library_used: False`; no ML library / `.fit` in the
   package) that ignore the discriminative legal fields; `0.0` is engineered, not earned.
2. **Capacity-matched reference invalidity** — returns `stale_prior_channel`, structurally
   never `target`; not a capacity-matched challenger.
3. **Headline gate non-fail-able on its own three axes** — `_build_result` cannot
   downgrade on the learned / capacity / ablation axes given these implementations; the
   `survives` verdict is granted by construction.

## Non-blocking issues

* Two of four CORE ablations are constant `"unresolved"` stubs (mechanism-independent).
* "Scaling / combinatorial-heldout" is cosmetic: identical solving rule in train and
  heldout; tiny deterministic `target=index mod 4` surface; `small_reproduction`
  self-declared row-enumerable.
* Tests encode the conclusion and do not guard learned-baseline validity or
  ablation specificity.
* Replay covers only one episode with `any`-based sensitivity.
* Worktree hygiene: uncommitted CRLF rewrites + `AGENTS.md` governance-block deletion
  (anchored commit is clean).

## Required fixes (to re-earn the bounded learned-baseline claim)

1. Add at least one **actually-fitted** no-boundary model (e.g. logistic regression / MLP
   via numpy or sklearn) trained on the flattened legal observation **including** the
   no-action and external rows; report fit provenance. The claim survives only if such a
   model, given fair features, still underperforms the reference by the declared margin.
2. Make `capacity_matched_boundary_disabled_reference` a real challenger: let it *use*
   its computed `action/no_action/external` counts but with the action-conditioned
   boundary update disabled, instead of returning the stale prior.
3. Replace the two constant `"unresolved"` core ablations with re-runs of the reference
   that disable exactly one component.
4. Make the split a real scaling/generalization probe (decouple `target` from `index`,
   add channels, require induction across train→heldout), or drop "scaling/heldout"
   from the claim.
5. Strengthen tests so they fail if a learner is replaced by a constant, if an ablation
   is replaced by a constant, or if the no-boundary model is given impoverished features.

## Recommended route

**Do not preserve 001B as a bounded positive preflight under its current verdict.**
Reclassify to blocked. Downgrade the verdict wording from
`…survives_learned_baseline_scaling_challenge` to the only thing the evidence supports —
a *hand-coded heuristic separation* on a constructed 4-channel surface — pending the
required fixes. The engineering harness (replay, leakage fail-ability, provenance,
claim-ceiling) is reusable as-is; the baseline/capacity/ablation/split arms must be
rebuilt before any "learned-baseline" or "scaling" language is permitted.

## Whether implementation may proceed

**No** — for any successor that depends on 001B as positive learned-baseline or scaling
evidence. The required fixes above must land and re-pass first. A successor that only
reuses the leakage/replay/provenance harness (and makes no learned/capacity/scaling
claim) may proceed.

## What this audit cannot prove

This audit cannot prove the mechanism is invalid — only that 001B's *evidence* does not
establish what it claims. A correctly-built learned baseline and a fair capacity-matched
reference might still leave the reference ahead; that experiment has not been run. The
audit also cannot prove anything about consciousness, subjectivity, emotion, agency,
autonomy, Gate4/Gate5 validity, runtime/EGO readiness, or stable user benefit; none of
those are in scope. Bounded to commit `347b75b` and the artifacts listed.
