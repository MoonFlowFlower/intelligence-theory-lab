# Independent Hostile Re-Audit — Repaired Route C Phase 0 Preflight

**Audit task id:** `CLAUDE-INDEPENDENT-ROUTE-C-PREFLIGHT-001A-REPAIR-REAUDIT-001A`
**Date:** 2026-06-16
**Role:** Same-Agent Bridge Audit Role 001 — independent auditor / red-team (read-only; no repair performed)

---

## 1. Verdict

**`audit_accepts_repaired_phase0_for_candidate_card_drafting`** — ACCEPT.

The prior blocker (`blocked_by_observation_baseline_underpowered`) is genuinely closed. All 12 acceptance conditions are established. Two disclosed non-blocking caveats remain (provenance basis not re-derived from real data; two meta-records validated-by-construction). A **separate** repo-hygiene blocker (hardcoded GitHub PAT in `scripts/push.*`) keeps push/tag/anchor blocked but does not affect the Route C Phase 0 verdict.

## 2. Target commit

`278819ab5b2dccc082bfaa24098c5ddbdbba7749` — "Repair Route C preflight observational baseline".
Parent (preservation): `eadc08f04e9bc465379fd35b3844a823a55062c6`. Original impl: `726f26daef9d766abe0592972acf8569041483fa`. Branch `codex/meta-theory-scaffold`. `origin/codex/meta-theory-scaffold = 8ad1dd84…` ≠ target ⇒ repair chain is local-only (not pushed). No tag on the target.

## 3. Target artifact path

`artifacts/route_c_preflight_001a/` (15 committed files). Source under `src/route_c_preflight_001a/`; tests under `tests/route_c_preflight_001a/`.

## 4. Current layer under audit

Engineering implementation / candidate-free Phase 0 preflight repair evidence only.

## 5. Audit layer

Engineering-governance / independent hostile re-audit only.

## 6. Mainline integration status

None. No Gate / mainline / runtime / bridge / scheduler / admission / product path is touched by the repair (diff = 19 files, all under the three allowed `route_c_preflight_001a` prefixes).

## 7. Enabled status

Local CLI, pytest, and artifact generation only. No enabled or live Route C path.

## 8. Real trigger evidence

- `python3 -m route_c_preflight_001a --output-dir <tmp> --run-id route-c-preflight-001a` → printed `preflight_admitted_for_candidate_design`.
- `pytest tests/route_c_preflight_001a -q` → `22 passed`.
- Callable runner: `route_c_preflight_001a.runner.run_preflight`. All 18 provenance producers resolve to live callables whose source hashes match the recorded `code_path_hash`.

## 9. Claim ceiling

Independent hostile re-audit verdict over the repaired Route C candidate-free Phase 0 preflight only. No mechanism evidence, no candidate evidence, no Gate pass, no mainline/runtime/live effect, no agency/autonomy/consciousness/emotion/stable-user-benefit/EGO-readiness.

## 10. Source / artifact reproduction findings

- CLI re-run from the target commit reproduced the committed `result.json` **byte-for-byte except** `real_trigger_evidence.artifact_dir`, `run_id` (canonical used `route-c-preflight-001a-repair-001a`), and absolute `callable_source_path` (session-mount dependent). These are exactly the permitted path/run-id fields.
- Reproduced scalars: `obs_only_family_max = 0.416667` (winner `supervised_passive_feature_attacker`), `value_level_family_max_on_clean = 0.416667`, `interventional_oracle = 0.989583`, `headroom = 0.572916`, `premise_threshold = 0.495`, `chance = 0.375`, `material_producer_count = 18`, `provenance_row_count = 18`. All match the committed artifact.
- Canonical artifact was produced on session mount `trusting-eloquent-wright`; this re-audit reproduced identical numbers on `elegant-gracious-carson` ⇒ result is generated from source, not manually patched.
- Parent doc hashes in the artifact match live docs: blueprint `a2bb1db2…`, task card `5446b68f…`. The repair did not modify the blueprint or task card it is judged against (no governance self-modification).

## 11. Prior blocker closure findings

Closed. The prior `obs_only_baseline` read only planted answer-maps / a positional first-k fallback. The repair replaces it with an 8-member passive attacker family in which six members read **only** `legal['passive_rows'][*]['handle_values']` through the single entry point `core.passive_value_matrix` (mean, variance, correlation, PCA-subspace, cross-episode, supervised). `obs_only_family_max = max` over the full family; `non_identifiability_premise_gate` consumes `panel["obs_only"]["family_max"]["value"]`. The weak `positional_first_k_attacker` cannot determine the verdict because the gate uses the family max, demonstrated by `test_obs_only_family_max_is_used_by_premise_gate` and by L9 where the value-level mean attacker (1.0) dominates the positional no-op.

## 12. Passive attacker family findings

Family reads passive values (verified by code path and by L9, where the value leak drives `passive_mean_attacker → 1.0` while the positional attacker is unmoved). Family max is used. Generator construction (`_row_values` = `weights·confounder + noise`) excludes S from the passive law; S enters only the interventional regime (`generate_intervention_log` adds `gain·value` to self channels). Empirically, across 8 disjoint CLEAN seed ranges, every value-level attacker hovers near chance (0.375) and the family max stays in 0.379–0.475 — the premise is not a single-seed artifact.

## 13. L9 value-level control findings

`inject_observation_value_decodable_self_set` adds a fixed `+5.0` offset to the passive `handle_values` of the self channels only. Confirmed it introduces **zero** new `legal` keys — no answer-map, truth label, self-set name, alias, schema key, or query field. On L9: premise gate → `blocked_by_observation_decodable_self_set`; family max → 1.0; winning attacker is value-level (`passive_mean_attacker`); the key/name scanner stays `clean`. L9 is a genuine value-level decodable control, not disguised key/name/schema leakage, and is **in addition** to the L1 answer-map control (both present).

## 14. Canonical clean score semantics findings

- S absent from passive P(X) by generator construction (verified in source).
- `premise_band = 0.12` and `headroom_band = 0.25` are **byte-identical across 726f26d → eadc08f → 278819a**; the repair diff touches no Config threshold line. Threshold `0.495` is predeclared, not tuned to the new family max.
- `DEFAULT_SEEDS = range(1600, 1632)` is identical across all three commits — no seed cherry-pick. The repair only added the disjoint `HEADROOM_PROBE_SEEDS` (2M) and `SUPERVISED_TRAIN_SEEDS` (90M).
- Canonical clean `family_max = 0.4167 < 0.495` (margin 0.0783). **Special scrutiny — supervised attacker:** `SUPERVISED_TRAIN_SEEDS = range(90_000_000, 90_000_048)` is disjoint from eval seeds and from the `seed + 10_000_000` learner offset, with an explicit `if seed in eval_seeds: continue` guard; it trains on the trainer's own episodes' truth and never reads eval truth. Empirically it scores 0.34–0.475 across seed ranges (near chance, never near the oracle's 0.99) ⇒ split-safe; it is not decoding S. The canonical 0.4167 is finite-sample max-selection bias, not a leak.
- **Caveat (non-blocking):** worst observed clean draw `family_max = 0.475` (margin 0.020 to threshold). Premise robust (0/8 clean ranges exceed threshold) but finite-sample-thin; error direction is false-BLOCK (conservative), never false-admit.

## 15. Provenance findings

18 material rows, all carrying `code_path_hash`; **all 18 producers resolve to live callables and their live source hashes match the recorded hashes** (no fabricated/renamed/modified producer). Subsystem histogram: premise 10, schema_alias 2, interventional_headroom 2, leakage 1, replay 1, provenance 1, verdict 1. `provenance_validation.json → provenance_valid`. Dropping `code_path_hash` from a real row, or a changed live config-source hash, both force `blocked_by_provenance_gap` (verified). Both actual gates (premise, headroom) are inside the validated set. **Caveat (non-blocking):** the validator certifies 16/18 rows; the two meta-records (`validate_provenance_rows`, `_select_verdict`) are emitted with real source-matching hashes but cannot be re-validated by the same pass without circularity — validated-by-construction.

## 16. Computed-attestation findings

`computed_not_literal`, `threshold_frozen_before_run`, `failure_path_available` are validator-computed, not self-declared. A hardcoded `True` that disagrees with the computed value is rejected; a self-declared attestation must equal the computed one. Verified fail-able paths: missing field → block; value/basis inconsistency → block; wrong source hash → block; config-source changed since snapshot → `threshold_not_frozen` block; failure-control absent for a subsystem → `failure_path_unavailable` block. **Caveat (non-blocking, disclosed):** a fully **self-consistent** forged `(value, recompute_basis)` pair naming a real producer with the correct source hash passes (reproduced) — the basis values are not re-derived from real episode data. Acceptable for candidate-free Phase 0 because the canonical numbers are independently reproduced from source; **required-closure before any Gate-grade claim** (either re-derive the basis from recorded inputs, or re-execute producers under validation).

## 17. Leakage findings

`clean_is_clean = True`, `all_controls_fired = True`, `blocking_verdict = None`. L1/L5/L7/L9 are **gate-coupled** and drive real fail-closed verdicts (L1/L5/L9 → `blocked_by_observation_decodable_self_set`, L7 → `blocked_by_schema_alias_leakage`). L2/L3/L4/L6/L8 are explicitly marked `synthetic_detector_only` with a note that they only prove the key/name scanner fires on a planted token and are not, by themselves, fail-closed safety — resolving the prior non-blocking complaint. The leakage subsystem's own failure path is the L1-no-op probe (`subsystem_blocks = True`), a real block demonstration rather than a name match.

## 18. Replay findings

`replay_oracle_predictions` recomputes from `serialized_state{handles,k_self}` + intervention rows only; the serialized state stores **no** effect map and **no** answer, so replay cannot shortcut. It reads no stored prediction, `prediction_hash`, truth, or oracle-only field. Negative controls #1 corrupt intervention rows, #2 remove rows, #3 corrupt serialized state (via `k_self` decrement) all flip behavior (verified). The replay material record (subsystem `replay`) is in provenance, and `failure_controls["replay"]` requires the three substantive flips. **Caveat (non-blocking):** controls #4 (`recompute_ignores_stored`) and #5 (`stored_hash_tamper_accepted=False`) are tautological/asserted, not dynamically adversarial; the load-bearing fail-ability is #1–#3, and the handle-reversal portion of #3 is inert (the `k_self` decrement is what bites).

## 19. Test adequacy findings

22 tests, `22 passed`, genuinely fail-shaped (not JSON-shape only): value-level control blocks; family max is used and exceeds the weakest attacker; positional cannot pass on a value leak; forged/hardcoded attestation rejected (source-hash mismatch + disagreement); failure-control-absent → provenance block; replay tamper controls flip; serialized-state/intervention-row corruption fails replay; `candidate.py` absent and the source file set is exactly `{__init__, __main__, core, leakage, provenance, replay, runner}`; forbidden-path detector fires on EGO/ACSB/ACOLB paths.

## 20. Candidate-free boundary findings

No `candidate.py`; no learned self-boundary candidate; no fair interventional candidate comparison; no Gate run; no mainline integration; no runtime/bridge/scheduler/admission/product/live path; no push, tag, or remote anchor. `result.json` self-reports `candidate_implemented=false`, `gate_…_touched=false`, `push_tag_remote_anchor_performed=false`, consistent with source inspection.

## 21. Secret / push safety note

`scripts/push.py:31` and `scripts/push.sh:19` each contain one hardcoded GitHub PAT (token redacted — never displayed or quoted in this audit). Both files are **gitignored and untracked** (`.gitignore`: "Push scripts contain token — never commit"), so the token is not in committed/pushed history via these files; it is nonetheless live plaintext on disk. The FUSE-truncated `.git/config` `[credential "https://github…]` section likely holds the same token locally. **Push / tag / remote-anchor must remain BLOCKED until the token is revoked/rotated and removed from the scripts and the local credential store.** This is a repo-hygiene issue separate from the Route C Phase 0 verdict; this audit did not push and did not run the push scripts.

## 22. Strongest objection

The provenance `computed_not_literal` attestation establishes only (a) the row names an importable producer whose live source hashes to the recorded `code_path_hash`, and (b) the recorded value is arithmetically consistent with a self-declared `recompute_basis`. It does **not** re-derive the basis from real episode data, so the attestation layer alone cannot certify that any artifact's numbers are real — only that they are self-consistent and source-bound. An artifact author who knows the schema can mint a passing record. This is the strongest objection to admission. It does not block here because (i) the canonical admission is established by independent byte-level reproduction **from source**, not by the attestation, and (ii) Phase 0 is candidate-free harness validation, not a defense against a malicious artifact author. It must be closed before any Gate-grade reuse of this provenance layer.

## 23. Whether repaired admission is accepted, downgraded, or blocked

**ACCEPTED** for candidate-card drafting, with the recorded non-blocking caveats. Not downgraded, not blocked. The Route C Phase 0 verdict is independent of the separate push/anchor repo-hygiene blocker.

## 24. Next minimal closed-loop action

1. Draft a **separate bounded Route C candidate-card DESIGN task** (§6.3 fair-interventional candidate + ablation + replay). Candidate implementation remains **FORBIDDEN** until that card is independently audited. Carry forward the §6.3 saturation risk (interventional-baseline saturation, the ACOLB-A regeneration hazard) and the obs-decodability hazard as predeclared STOP gates.
2. Open a **separate repo-hygiene task** to rotate/remove the GitHub PAT and scrub it from `scripts/push.*` and the local credential store before any push/tag/anchor.
3. (Pre-Gate, not Phase 0) Close the provenance basis-reproduction caveat: re-derive `recompute_basis` from recorded inputs or re-execute producers under validation.

## 25. What this audit does not prove

Route C mechanism validity; self-boundary mechanism evidence; candidate success; Gate pass; mainline effect; live path; agency; autonomy; consciousness; emotion; stable user benefit; EGO readiness; fair interventional candidate advantage under the deferred §6.3 saturation risk.

---

### Audit method note (environment)

Read-only hostile audit. No source/test/threshold/generator/candidate modification. The repo is on a FUSE "no-delete" mount that renders the whole working tree as `D`/`??` in `git status` (4498 + 17 entries across unrelated historical paths) and truncates `.git/config` at the credential section. To audit the exact commit, this re-audit (a) confirmed all 23 on-disk `route_c` files are hash-identical to the committed blobs of `278819a`, (b) ran git via a temporary read-only gitdir using object alternates, and (c) reproduced the CLI to a temp directory outside the repo, never overwriting canonical artifacts. The untracked diagnostic sentinel `artifacts/route_c_preflight_001a/_bash_write_test.txt` is undeletable via FUSE; it is recorded as a caveat, not read as evidence, and excluded from all comparisons.
