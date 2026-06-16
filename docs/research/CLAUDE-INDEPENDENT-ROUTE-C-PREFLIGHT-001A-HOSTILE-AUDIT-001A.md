# Independent Hostile Audit — ROUTE-C-PREFLIGHT-001A

**Audit task id:** `CLAUDE-INDEPENDENT-ROUTE-C-PREFLIGHT-001A-HOSTILE-AUDIT-001A`
**Audit layer:** engineering-governance / independent hostile audit only
**Date:** 2026-06-16
**Method:** read-only audit over source/tests/artifacts/parent-docs + byte-identical reproduction + one demonstrated counterexample probe. No files in the target implementation were modified, repaired, or re-thresholded.

---

## 1. Verdict

**`blocked_by_observation_baseline_underpowered`** — admission **BLOCKED**. Do **not** draft a Route C candidate card. The repair is bounded and is already specified by the blueprint; candidate implementation is forbidden until re-audit.

## 2. Target commit
`726f26daef9d766abe0592972acf8569041483fa` on `codex/meta-theory-scaffold`, message "Implement Route C candidate-free preflight". HEAD == target (verified).

## 3. Target artifact path
`artifacts/route_c_preflight_001a/result.json` (verdict `preflight_admitted_for_candidate_design`).

## 4. Current layer
Engineering implementation / candidate-free Phase 0 preflight evidence only. Correctly classified.

## 5. Mainline integration status
**none.** The commit touches only `src/route_c_preflight_001a/**`, `tests/route_c_preflight_001a/**`, `artifacts/route_c_preflight_001a/**`, and the two parent docs (21 files, +7666/-0). No Gate/mainline/runtime/bridge/scheduler/admission/product path.

## 6. Enabled status
local CLI / pytest / artifact generation only (verified). `result.json` flags `mechanism_claim_admitted=False`, `candidate_implemented=False`, `gate_mainline_..._touched=False`, `push_tag_remote_anchor_performed=False`.

## 7. Real trigger evidence
- `python -m route_c_preflight_001a ... --run-id route-c-preflight-001a` → prints `preflight_admitted_for_candidate_design`.
- **Re-running from the committed (LF) source reproduced `result.json` byte-identical** except the `artifact_dir` path field → the artifact is genuinely machine-computed, not hand-written/patched.
- `python -m pytest tests/route_c_preflight_001a -q` → **12 passed**.
- `parent_doc_hashes.json` matches sha256 of the committed (LF) blueprint and task card exactly.

## 8. Claim ceiling
Audit output is an independent verdict over Route C Phase 0 candidate-free preflight artifacts only. No mechanism / candidate / Gate / mainline / agency / autonomy / consciousness / emotion / user-benefit claim is admitted.

---

## 9. Source/artifact consistency findings (Check A)
- **PASS (integrity):** `result.json` and `route_c_preflight_result.json` are the same blob and reproduce byte-identically from `runner.run_preflight`. Not fabricated.
- **PASS:** parent-doc hashes match the actual committed docs.
- **Confirmed concern:** the result reports **6** `producer_functions` but only **4** `code_path_hashes` (obs_only / schema_only / name_order / interventional_oracle). `leakage.run_leakage_positive_controls` and `replay.replay_oracle_predictions` appear in the producer list and **feed `_select_verdict`** but carry **no code-path hash** and are **not** in `provenance_rows.jsonl`. → leakage and replay are **side reports outside the callable provenance gate**, exactly as the audit brief suspected.
- **Caveat (non-blocking):** committed artifacts/docs are LF; the Windows working tree is CRLF (13/13 artifacts differ on CR only; 10/10 source+test+doc files are byte-identical). Reproduction/hashing is valid only against committed LF content.

## 10. Provenance findings (Check B)
- `provenance_rows.jsonl` has exactly **4 rows** (the obs/schema/name/oracle aggregate score records). Each carries producer_function, inputs, run_id, seed=`multi_seed`, episode_ids, aggregation, code_path_hash (real `inspect.getsource` hash), threshold_used.
- **Block-relevant:** the leakage `blocking_verdict` and the replay `verdict` are **material to the final verdict** (`_select_verdict`) yet sit **outside** provenance. A material gate result outside callable provenance is precisely what Check B says to block on.
- **Non-fail-able attestations:** `computed_not_literal`, `threshold_frozen_before_run`, `failure_path_available` are **hardcoded `True`** in `provenance.score_record`; `result.thresholds_frozen_before_run` is a hardcoded literal. The validator "checks" fields that can never be False. (Thresholds are, separately, predeclared in blueprint §6.10 and frozen in the committed `Config` — that is the real freezing evidence, not the boolean.)

## 11. Passive non-identifiability findings (Check C) — **DECISIVE**
The premise gate's `non_identifiability_present` verdict does **not** establish that passive observation cannot decode S. It is **asserted by construction, not tested**:
- The generator makes passive `handle_values = W·U + noise`, with `W` drawn from the **same** distribution for `i∈S` and `i∉S`; **S never enters passive P(X)**. So passive data is non-identifiable for S *by design*.
- But the gate would emit the **same** `non_identifiability_present` even if the passive values *did* encode S, because the baseline that feeds it never inspects the values (see §12).

**Demonstrated counterexample (read-only probe, committed code):**

| quantity | value |
|---|---|
| trivial *legal* mean-attacker on passive values (S leaked into values) | **1.0000** |
| shipped `obs_only_baseline` on the **same** data | **0.3854** |
| shipped `non_identifiability_premise_gate` verdict on the **same** data | **`non_identifiability_present`** (ADMITTED) |

A surface where S is trivially decodable from observation values is **admitted**, not blocked. The gate is **not fail-closed** against threat **F1** (same-step observation decoding) that the blueprint built it to defend.

## 12. Baseline adequacy findings (Check D) — **root cause**
The blueprint §6.1 predeclares the obs-only baseline as the *"best passive predictor … **may use any observational structure (covariance, clustering, supervised fit on passive features)**"* and requires non-identifiability *"**tested not assumed**"*.

The shipped `core.obs_only_baseline` does the opposite:
```
predicted = _predict_from_membership_map(legal,"leaked_self_membership_by_handle")   # planted answer-map
         or _predict_from_membership_map(legal,"confounder_self_membership_by_handle") # planted answer-map
         or legal["handles"][:k_self]                                                  # positional first-k guess
```
It **never reads `handle_values`.** No covariance/correlation, channel-variance, PCA/subspace, cross-episode clustering, W-loading, or supervised-fit attacker is present — none of the required family. The canonical `passive_baseline_score = 0.385417` is just "first-3 permuted handles ∩ random self-set" ≈ chance (3/8 = 0.375). This is a **materially weaker implementation than its own predeclared, frozen contract** → underpowered baseline. Acceptance condition **#1 fails**.

## 13. Leakage-control findings (Check E)
- All L1–L8 "fire"; clean scan is clean; `blocking_verdict = None`.
- `gate_verdict` is non-null only for **L1, L5, L7** (the ones that re-run the panel). **L2, L3, L4, L6, L8 → `gate_verdict = null`** — they are **nominal key-name detections** not coupled to any decoder/gate. The detector greps for the exact key/token names the injector plants (`leaked_self_membership_by_handle`, `original_index_by_handle`, `answer_handles`, `action_label_alias`, `responded_channel_flag`/`effect_size_label`, source token `self_set_original`). It is an **injector↔detector string-name pair**, near-tautological.
- The only gate-coupled "observation-decodable" path (L1/L5) fires because the baseline **reads an explicit membership answer-map**, not because it decoded values. So L1 proves "baseline can read an answer key," **not** the F1 claim "a capable observational attacker fails on S-independent values."
- On canonical data the leakage subsystem **cannot block** (all controls fire + clean stays clean ⇒ `blocking_verdict=None` by construction). It is a positive-control demo, not a fail-closed guard. Answers to E's required questions: L2/L3/L4/L6/L8 are null because they are detector-only positive controls never wired to the gate; the gate fails closed **only** for planted explicit answer-maps/aliases (L1/L5/L7), **not** for value-structure or do-policy-confound leakage.

## 14. Interventional oracle findings (Check F) — PASS
`_predict_oracle_for_legal` estimates a per-channel effect `Σ v·post[h] / Σ v²` from **randomized ±1 do-responses** and ranks by `|effect|`. It reads `intervention_log` (target_handle, value, post_handle_values) and `handles`/`k_self` only. It does **not** read `self_set_original`, `truth_self_handles`, effect labels, oracle-only fields, gain, or generator internals. The oracle obtains its `0.989583` by **estimation, not answer access** — acceptable for Phase 0.

## 15. Headroom findings (Check G)
- Arithmetic is consistent: `headroom = 0.989583 − 0.385417 = 0.604166 > headroom_band 0.25` → `interventional_headroom_present`.
- Bands `PREMISE_BAND=0.12`, `HEADROOM_BAND=0.25` are predeclared in blueprint §6.10 and frozen in the committed `Config`; the `gain=0` zero-headroom control **genuinely** flips the gate to `blocked_by_no_interventional_headroom` (tests + `failure_manifest`). So the headroom gate itself is fail-able.
- **But the semantics overstate the advantage:** headroom is measured against a **no-op positional baseline**, not against the strongest passive attacker. "Interventions beat a guess that never looked at the data" is not the intended "interventions add signal a capable passive method cannot." This inherits directly from §12 and is decision-relevant, not cosmetic.

## 16. Replay findings (Check H) & Test adequacy (Check I)
**Replay — mostly PASS:** `_predict_from_rows` recomputes predictions from `serialized_state{handles,k_self}` + intervention rows; it does **not** shortcut via stored `effect_state` and does **not** read answer fields. The `corrupt_intervention_log_changes_behavior` control is **real and fail-able**. **Minor:** the `stored_hash_tamper_accepted` control is **vacuous** — `_predict_from_rows` never reads `prediction_hash`, so it is structurally always `False` and cannot flip.

**Tests — adequate breadth, one critical gap:** 12 tests include genuine fail-able paths (zero-gain → no-headroom block; missing `code_path_hash` → provenance block; corrupt log → replay teeth; no-candidate/forbidden-path). **Gap:** *no test feeds a value-level observation-decodable surface and asserts the gate blocks.* `test_hidden_self_set_injection_blocks_observation_decodable_surface` only plants an explicit membership **answer-map** (the same proxy as L1). There is no statistical-decodability block test, no near-threshold variant, and no source/artifact-mismatch test. This is exactly the hole the §11 probe exploits.

## 17. Candidate-free boundary findings (Check K) — PASS
No `src/route_c_preflight_001a/candidate.py`. No learned self-boundary candidate, no fair interventional candidate comparison (6.3 correctly deferred). No Gate/mainline/runtime/bridge/scheduler/admission/product/live path. No push/tag/remote anchor (audit only). Boundary flags in `result.json` all `none`/`False`.

## 18. Strongest objection (and why it still blocks)
**Objection:** the toy is non-identifiable *by construction* (S absent from passive `P(X)`), so a baseline scoring at chance is the *correct* answer and the admission may be substantively right; demanding a heavy attacker over-engineers a toy preflight.
**Rebuttal:** a premise gate that cannot tell a non-identifiable surface from an observation-decodable one provides **zero empirical support** for the premise — and the §11 probe shows it admits a decodable surface. The blueprint itself forbids this with "tested not assumed" and a capable observational attacker. Substantive correctness of the toy does not rescue a gate that is structurally unable to fail on the threat it targets. The admission is an artifact of an underpowered baseline.

## 19. Decision: **BLOCK** (not accept, not downgrade)
Acceptance requires **all 8** conditions. Condition **#1 fails decisively and is demonstrated**. The most specific allowed verdict is **`blocked_by_observation_baseline_underpowered`**. (Secondary applicable labels: `blocked_by_non_fail_able_controls` for the leakage/provenance attestations, and `generator_constructed_success` for the untested constructed non-identifiability — but #1's demonstrated failure is the cleanest decisive blocker.) This is a real block, not `requires_minor_repair`, because the missing piece is the predeclared capable baseline family plus a value-level fail-able control — substantive, not a threshold tweak.

## 20. Next minimal closed-loop action
Open one bounded **preflight-repair** card (still candidate-free, no Gate/mainline/live claim):
1. Replace `obs_only_baseline` with the predeclared §6.1 observational attacker family (covariance/correlation, channel-variance, PCA/subspace, cross-episode clustering, supervised fit on passive features); report `max` over the family.
2. Add a **value-level** fail-able control `inject_observation_value_decodable_self_set` (S leaks into `handle_values`, not into a key) that must drive `obs_only ≈ 1.0` and force `blocked_by_observation_decodable_self_set`. The existing answer-map L1 is insufficient and must remain *in addition*, not *instead*.
3. Bring `leakage` and `replay` producers **inside** the provenance gate (emit `code_path_hash` + provenance rows for their material verdicts); make the three attestation booleans derived, not literal.
4. Re-run, regenerate artifacts, and re-audit. **Candidate implementation forbidden until re-audit accepts.**

## 21. What this audit does not prove
- Does **not** prove Route C mechanism validity or self-boundary mechanism evidence.
- Does **not** prove the canonical toy is observation-decodable (canonical S is genuinely absent from passive `P(X)`); it proves the **harness cannot detect decodability if present**.
- Does **not** prove candidate success, Gate pass, mainline effect, live path, agency, autonomy, consciousness, emotion, stable user benefit, or EGO readiness.
- Does **not** evaluate the deferred §6.3 fair interventional baseline or the F6 saturation risk (the ACOLB-A killer reborn one layer up).

---
*Preserved as negative evidence. Read-only audit; no implementation file modified, no threshold changed, no candidate created, no push/tag/remote anchor.*
