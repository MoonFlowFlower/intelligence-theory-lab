# Independent Audit: EVIDENCE-HARNESS-CRITICAL-RISK-TARGET-APPLICATION-001A

- Audit id: AUDIT-EVIDENCE-HARNESS-CRITICAL-RISK-TARGET-APPLICATION-001A-CLAUDE-001
- Audited commit: `241d69c109eea603726c6c5c02fc9faf7090c003` (tag `remote-anchor-evidence-harness-critical-risk-target-application-001a-241d69c`, verified locally; remote presence not verifiable from sandbox)
- Audit date: 2026-06-12
- Auditor role: independent evidence-governance audit only (Same-Agent Bridge Audit Role 001)
- Audit claim ceiling: independent audit of conservative historical evidence-risk application only

## Verdict

`audit_passed_conservative_non_admission_valid` (with caveats; see non-blocking issues)

Primary question answered: Codex applied the harness as a genuine conservative
non-admission blocker. The 12 rejections are individually computed from target
input bundles via the callable 001A enforcer, are reproducible, and are
tamper-sensitive in both directions. This is not a static batch verdict.
However, for 2 of 12 targets the class label `rejected_false_pass_risk`
overstates the computed basis (test-surface lexical hits only); the accurate
class there would be `blocked_pending_audit`. Downstream semantics
(quarantine, all authorizations false) are identical, so the error is
label-granularity, not admission risk.

## Verification performed (commands reproducible)

1. `git show --name-status 241d69c`: 18 files, all additions. No old Gate
   artifact/test/verdict touched. Worktree diff vs HEAD is CR/LF-only across
   all 1463 flagged files (`git diff --ignore-cr-at-eol HEAD` is empty),
   including all audited paths.
2. Read `runner.py` (application) and `evaluate_bundle` (001A enforcer):
   no target→verdict dictionary; classification = enforcer class mapping;
   `insufficient_visibility` path exists for empty bundles; enforcer cannot
   return `admissible_downstream_evidence` (class structurally unreachable).
3. Rerun `run_application` against the committed tree into a scratch dir:
   `target_classification_matrix.json` identical to committed artifact modulo
   `run_id`; `enforcer_source_hash` matches (`5114ff27…`).
4. Tamper probes on a throwaway copy:
   - Sanitize the RCA target's test file (its only firing surface) →
     class flips `rejected_false_pass_risk` → `blocked_pending_audit`.
   - Delete all gate3 target inputs → `insufficient_visibility`,
     `callable_enforcer_invoked=false`.
   - Inject `bounded_pass: true` into an otherwise-clean RCA bundle →
     flips back to `rejected_false_pass_risk` (`pass_shaped_result_fields`).
5. `pytest tests/test_evidence_harness_critical_risk_target_application_001a.py`:
   6 passed. Tests include a real recompute-into-tmp path, the
   missing-input failure path, and no-positive-admission assertions.
6. jq checks: 12/12 provenance rows complete (producer_function, input
   artifacts, run_id, aggregation rule, source_code_hash); quarantine matrix
   has 0 rows with any authorization true or non-quarantined result; 001B gap
   list propagated verbatim (diff-identical to
   `contract_coverage_gap_report.json`); no Gate4-001C path appears in any
   input bundle; `src/ego_mainline_gate4_preflight_executable_001c` exists in
   the repo but is never imported or read by the new code.

## Per-target audit table

Categories: PSF=pass_shaped_result_fields, PSL=perfect_score_literal,
VRI=verified/real_intervention_true, ALS=ablation/variant label field,
TSA=test-surface assertion pattern.

| # | target | prior risk | class | inputs | categories | reasons | basis strength |
|---|--------|-----------|-------|--------|------------|---------|----------------|
| 1 | ego_mainline_gate4_preflight_001b | critical | rejected_false_pass_risk | 29 | PSF+PSL+VRI+ALS+TSA | 112 (50 PSL, 18 VRI, 12 PSF) | strong; consistent with 90dc4b9 independent reject |
| 2 | gate2_controllability_self_boundary_001b | critical | rejected_false_pass_risk | 27 | PSF+ALS+TSA | 19 | strong (`*_gate_passed=true` literals in own result/ablation artifacts) |
| 3 | gate3_viability_functional_affect_001b | critical | rejected_false_pass_risk | 20 | PSF+PSL+ALS+TSA | 51 | strong |
| 4 | gate4_social_latent_inference_001b | critical | rejected_false_pass_risk | 24 | PSF+PSL+ALS+TSA | 56 | strong |
| 5 | gate4_social_representational_gap_preflight_001b | critical | rejected_false_pass_risk | 26 | PSF+PSL+ALS+TSA | 32 | strong |
| 6 | r_g_gate0_gate1_gate2_canonical_micro_agent_testbed_001b | critical | rejected_false_pass_risk | 21 | PSF+PSL+ALS+TSA | 47 | strong |
| 7 | r_g_gate0_gate1_gate2_gate3_canonical_micro_agent_testbed_001b | critical | rejected_false_pass_risk | 24 | PSF+PSL+ALS+TSA | 57 | strong |
| 8 | representational_gap_preflight | critical | rejected_false_pass_risk | 40 | PSF+PSL+ALS+TSA | 36 | strong |
| 9 | representational_gap_preflight_001b | critical | rejected_false_pass_risk | 39 | PSF+PSL+ALS+TSA | 33 | strong |
| 10 | gate1_replay_consolidation_001c | high | rejected_false_pass_risk | 18 | PSF+ALS+TSA | 16 | strong (`pass_conditions.*_gate_passed=true` in own artifacts) |
| 11 | process_intervention_hard_distribution_001b | high | rejected_false_pass_risk | 18 | TSA only | 2 | **weak label**: both reasons are lexical hits in test files (one belongs to the RCA task via substring alias bleed); historical verdict is already `…_failed_fair_control_match` — no pass exists to be false. Accurate class: blocked_pending_audit |
| 12 | process_intervention_hard_distribution_001b_trace_replay_rca_001a | high | rejected_false_pass_risk | 13 | TSA only | 1 | **weak label**: sole reason is its own test file containing strings like `degradation`/`exists()`; tamper probe confirms class flips when sanitized. Accurate class: blocked_pending_audit |

## Hard-coding / static dependency risk

Low for the central claim; localized residue elsewhere.

- No static target→verdict dictionary; rerun + bidirectional tamper probes
  confirm classifications are computed from inputs.
- `static_denylist_only` is genuinely false as behavior: `evaluate_bundle`
  never branches on task id; the per-target retask control was actually run
  (re-invocation with rewritten task_id values, compared on class+categories).
- Residue (non-fail-able clean fields, asserted not measured):
  `evaluate_bundle.static_denylist_only` is a constant `False`;
  `targets_with_static_hash_dependency: []` and
  `targets_with_static_path_dependency: []` are unconditional literals with no
  corresponding control (only the task-id control exists; the
  bounded_interpretation discloses this, but empty lists imply a scan ran);
  `computed_not_literal: true`, `hard_coded_target_verdicts_used: false`,
  `old_gate_artifacts_modified: false`, `provisional_gate4_001c_used: false`
  are manifest literals. Each was independently verified true in this audit,
  but the fields themselves cannot fail. This is the same anti-pattern family
  that blocked POST-BRIDGE-001C (non-fail-able scanner).

## Over-conservative classification risk

Real but bounded, concentrated in targets 11–12.

- The enforcer's `detect_output_shape_only_test_assertion` fires on *containing*
  shape-assertion strings, not on *only* containing them; the rule name
  overstates. Any repo test asserting on verdicts or artifact existence —
  which the lab's own evidence contract requires — triggers it. Rejection of a
  historically *failed* record as "false pass risk" on this basis is a
  category error in label, though harmless in effect (still non-admissible).
- Headline-misread hazard: `historical_false_pass_contamination_report.json`
  counts 12/12 `rejected_false_pass_risk`. A future reader could cite this as
  "twelve independent confirmations of false-pass contamination." For targets
  11–12 that is not what was computed. The per-target `rejection_reasons`
  arrays make the true basis inspectable, which is why this stays non-blocking.
- `insufficient_visibility` was never warranted (every target had ≥13 visible
  input files), so its absence is justified, not suppressed.

## Evidence provenance assessment

Pass. Every target row records producer_function (`classify_target`), input
artifact list, run_id (`…:69aa22dc83b6`, matching the recorded execution HEAD),
aggregation rule, and source_code_hash; the enforcer invocation report records
the enforcer module/function/source-path/source-hash, which matches a live
recomputation. Artifacts regenerate bit-identically modulo run_id. Minor
imprecision: bundle membership uses substring alias matching, so reasons can
bleed across related targets (seen in target 11); acceptable for quarantine
semantics, not for fine-grained per-target attribution.

## Claim ceiling assessment

Pass. Verdict string contains no pass-shaped claim ("…conservative_non_admission_complete").
All six authorization fields false at result level and per quarantine row.
Claim ceiling text identical across task card, result, claim_ceiling.txt, and
all reports. what_this_does_not_prove list is complete. Semantic gaps from
001B propagated verbatim and marked as limitation. One vacuous boilerplate
sentence (semantic_gap_impact_report says "blocked targets are quarantined"
while zero targets are in blocked class) — wording-level only.

## Blocking issues

None.

## Non-blocking issues

1. Label inflation on targets 11–12 (test-surface-only rejection labeled
   `rejected_false_pass_risk`; accurate class `blocked_pending_audit`).
2. Non-fail-able clean fields (static path/hash dependency empty-list literals
   without controls; computed_not_literal / hard_coded / manifest governance
   literals).
3. Substring-alias bundle attribution bleed across related targets.
4. `targets_impacted_by_non_admission_default` semantics too narrow to surface
   the two detector-weakness-dependent rejections; vacuous boilerplate sentence.
5. Inherited 001A rule-name overstatement (`output_shape_only` = "contains",
   not "only").

## Required fixes (before downstream reliance on per-target labels)

- Split `rejected_false_pass_risk` into artifact-claim-based rejection vs
  test-surface-only signal (the latter → `blocked_pending_audit`), or add a
  per-target `rejection_basis` field. Low cost: classification code already
  has the category data.
- Replace unconditional `[]` path/hash dependency fields with `not_tested` or
  implement the corresponding controls.
- Keep 001B semantic-detection repair (renamed fields, result-string claims,
  baseline-callable verification) on the backlog before this harness is used
  to *discriminate* rather than merely block.

## Next-step recommendation

Anchor accepted; proceed to Gate4 001C task-card drafting. In parallel,
run the low-cost classification-granularity repair above. Nothing in this
audit authorizes Gate4 001C execution, Gate5, admission, runtime, or bridge
work, and the per-target `rejected_false_pass_risk` labels for targets 11–12
must not be cited as evidence of false-pass contamination.

## What this audit does not prove

It does not prove the 10 strong rejections' historical tasks were in fact
false passes (it proves their artifacts contain the risk patterns the
enforcer defines); it does not prove enforcer detector quality beyond the
patterns tested; it does not prove EGO readiness, Gate validity, mechanism
validity, or any architecture correctness; it does not verify the remote
anchor exists on the remote (local tag only).
