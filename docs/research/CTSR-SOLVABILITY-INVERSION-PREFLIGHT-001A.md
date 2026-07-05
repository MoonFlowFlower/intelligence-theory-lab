# CTSR-SOLVABILITY-INVERSION-PREFLIGHT-001A

Verdict: `refused_surface_preflight`

Layer: engineering implementation / no-candidate surface-admission preflight only.

Mainline integration status: none; offline local preflight only.

Enabled status: callable local preflight runner only; no mechanism path enabled.

Auto-Remote-Anchor: conditional

No mechanism success claim is made.

No candidate mechanism was implemented.

## Bounded Task Card

- Task id: `CTSR-SOLVABILITY-INVERSION-PREFLIGHT-001A`
- Problem definition: perform one no-candidate solvability-inversion preflight after the preserved COMPOSITE-CTSR hostile audit closed the prior pass-chain as mechanism evidence.
- Current stage/layer: engineering implementation / no-candidate surface-admission preflight only.
- Mainline target: none.
- Enabled-state requirement: no new mechanism path, candidate, bridge, Gate5, runtime, tournament, or EGO-mainline behavior.
- Real-trigger evidence requirement: prior negative evidence shows legal oracle = majority = 0.25, leakage-dependent replay, out-of-pool masking fallback, and missed latent_action_binding alias.
- Hypothesis: a clean CTSR legal surface can be admitted if legal oracle solvability, baseline separation, carry ablation collapse, leakage controls, field registry, and forbidden-free replay all pass.
- Strongest baseline: majority, lookup, nearest-neighbor, graph-cache family, and observation-only posthoc classifier.
- Ablation requirement: no-carry and randomized-carry reruns must collapse to majority + eps.
- Trace/replay requirement: replay recomputes from task A raw legal observations, task B legal probes, declared rules, and run metadata only.
- Computed-evidence provenance gate: every score records producer, inputs, run id, seeds/context/episode ids, aggregation, and code path hash.
- Acceptance gate: admitted/refused/invalid-harness only; no threshold tuning after results.
- Claim ceiling: Bounded no-candidate evidence about whether a clean CTSR surface is admissible for future mechanism testing. No mechanism success, Gate4/Gate5 validity, candidate behavior, tournament outcome, bridge/runtime/EGO readiness, agency, autonomy, consciousness, emotion, subjectivity, companion readiness, stable user benefit, or mechanism_score claim is authorized.
- Stop condition: any failed gate, leakage control failure, stored-answer replay, unclassified field channel, baseline threshold closure, or forbidden path touch.
- Rollback plan: additive-only deletion or revert of the isolated task paths.
- Expected changed files: isolated source package, focused test, new artifacts, and this report only.
- Forbidden changes: frozen COMPOSITE source/artifacts, old oracle-block/hostile-audit artifacts, candidate files, Gate4/Gate5/tournament/bridge/runtime/EGO-mainline paths.
- Auto-Remote-Anchor decision: conditional.

## Prior Negative Evidence Cited

- `artifacts/preserve_composite_ctsr_hostile_audit_001a/result.json`: closed prior COMPOSITE-CTSR pass-chain as mechanism evidence and froze it as negative evidence.
- `artifacts/preserve_claude_audit_legal_interface_oracle_block_001a/result.json`: preserved legal-interface oracle block with oracle accuracy = majority = 0.25.

## Admission Gate Readback

- Legal oracle accuracy: `1.0`
- Majority baseline accuracy: `0.25`
- Best graph/cache/lookup/observation baseline: `{'baseline_id': 'transition_table', 'score': 0.25, 'threshold': 0.5}`
- Legal oracle minus best independent baseline: `0.75`
- Invoked baselines: `['majority_baseline', 'exact_legal_tuple_lookup_with_majority_fallback', 'nearest_neighbor_legal_observation', 'graph_lookup', 'transition_table', 'successor_map', 'count_table', 'fsm_planner', 'episodic_traversal', 'observation_only_posthoc_classifier']`
- Missing baselines: `[]`

## Ablation

- No-carry accuracy: `0.25`
- Randomized-carry accuracy: `0.0`
- Masking fallback in action pool: `{'producer_function': 'masking_fallback_in_action_pool', 'passed': True, 'fallback_action': 'inspect_boundary', 'action_pool': ['inspect_boundary', 'consolidate_trace', 'defer_action', 'replan_memory']}`

## Leakage And Replay

- Clean surface scan passed: `True`
- Positive-control unguarded alias accuracy: `1.0`
- Positive-control guard blocked: `True`
- Replay passed: `True`
- Replay forbidden fields: `[]`
- Replay prediction match rate: `1.0`

## Scope Readback

- Branch: `codex/meta-theory-scaffold`
- HEAD: `4afcceec0b5f6f0433ae170a51795d2639cbaeb7`
- Forbidden files modified: `['CLAUDE.md', 'artifacts/FSP-PUM-ENV-IDPROBE-001A/', 'artifacts/FSP-PUM-ENV-IDPROBE-001A/design_choices_rationale.md', 'artifacts/FSP-PUM-ENV-IDPROBE-001A/factored_equivalence_certificate.json', 'artifacts/FSP-PUM-ENV-IDPROBE-001A/factored_equivalence_certificate_s2d_g3.json', 'artifacts/FSP-PUM-ENV-IDPROBE-001A/factored_equivalence_certificate_s2e_g3.json', 'artifacts/FSP-PUM-ENV-IDPROBE-001A/freeze_record.json', 'artifacts/FSP-PUM-ENV-IDPROBE-001A/frozen_design.json', 'artifacts/FSP-PUM-ENV-IDPROBE-001A/pc_ideal_sanity_s2.json', 'artifacts/FSP-PUM-ENV-IDPROBE-001A/pc_z_sensitivity_addendum_s2c.json', 'artifacts/FSP-PUM-ENV-IDPROBE-001A/pc_z_sensitivity_s2b.json', 'artifacts/FSP-PUM-ENV-IDPROBE-001A/s1_implementation_manifest.json', 'artifacts/FSP-PUM-ENV-IDPROBE-001A/s2_collision_record.json', 'artifacts/FSP-PUM-ENV-IDPROBE-001A/s2_tractability_report.json', 'artifacts/FSP-PUM-ENV-IDPROBE-001A/s2_tractability_report_v2.json', 'artifacts/FSP-PUM-ENV-IDPROBE-001A/s2_tractability_report_v3.json', 'artifacts/FSP-PUM-ENV-IDPROBE-001A/s2_tractability_report_v4.json', 'artifacts/FSP-PUM-ENV-IDPROBE-001A/s2d_further_exact_factorization_collision_record.json', 'artifacts/FSP-PUM-ENV-IDPROBE-001A/s2e_log_kernel_collision_record.json', 'artifacts/FSP-PUM-ENV-IDPROBE-001A/s2e_step0_profile_before.json', 'artifacts/FSP-PUM-ENV-IDPROBE-001A/z_marginalization_convergence.json', 'artifacts/FSP-PUM-ENV-IDPROBE-001A/z_marginalization_convergence_s2d_g_selection.json', 'artifacts/ITL-DEV-BENCH-001A/.gitkeep', 'artifacts/ITL-DEV-BENCH-001A/RUN_20260629T150801Z/', 'artifacts/ITL-DEV-BENCH-001A/RUN_20260629T151007Z/', 'artifacts/ITL-DEV-BENCH-001A/RUN_20260629T153122Z/', 'artifacts/LRGG-CANDIDATE-FREE-TIER0-2/OFFICIAL_RUN_001A_CLAUDE_HOSTILE_AUDIT_001A/', 'artifacts/LRGG-CANDIDATE-FREE-TIER0-2/_writetest/', 'artifacts/TLGP-001A-AUDIT-001/', 'artifacts/TLGP-001B-INVALID-AUDIT-001/', 'artifacts/TLGP-001B/', 'artifacts/TLGP-CAPABILITY-WITNESS-PREFLIGHT-001A/GROKKING_PROBE_001B/OPERATOR_REVIEW_001B.md', 'artifacts/TLGP-CAPABILITY-WITNESS-PREFLIGHT-001A/GROKKING_PROBE_001B/operator_review_001b.json', 'artifacts/TLGP-CAPABILITY-WITNESS-PREFLIGHT-001A/GROKKING_PROBE_001B/operator_review_001b.py', 'artifacts/TLGP-CAPABILITY-WITNESS-PREFLIGHT-001A/GROKKING_PROBE_001B/runner.pid', 'artifacts/TLGP-CAPABILITY-WITNESS-PREFLIGHT-001A/RUNG1_CAPACITY_SWEEP_002A/', 'artifacts/action_conditioned_self_boundary_preflight_001a/readback.json', 'artifacts/action_conditioned_self_boundary_preflight_001a/surface_bundle.json', 'artifacts/action_conditioned_self_boundary_preflight_001a/test_results.json', 'docs/codex/contracts/MECHANISM-SIGNATURE-VERDICT-STANDARD-001A.md', 'docs/codex/contracts/MECHANISM-SIGNATURE-VERDICT-STANDARD-001A.md', 'docs/codex/tasks/FSP-PUM-ENV-IDPROBE-001A-EXECUTION-PLAN-001A.md', 'docs/codex/tasks/FSP-PUM-ENV-IDPROBE-001A-EXECUTION-PLAN-001A.md', 'docs/codex/tasks/FSP-PUM-ENV-IDPROBE-001A-S0-FREEZE-OPS-001A.md', 'docs/codex/tasks/FSP-PUM-ENV-IDPROBE-001A-S0-FREEZE-OPS-001A.md', 'docs/codex/tasks/LRGG-CANDIDATE-FREE-CHEAP-TIER-EXECUTION-001A.md', 'docs/codex/tasks/LRGG-CANDIDATE-FREE-PREFLIGHT-001A.md', 'docs/codex/tasks/LRGG-CANDIDATE-FREE-TIER0-2-FREEZE-MANIFEST-001A.md', 'docs/codex/tasks/LRGG-CANDIDATE-FREE-TIER0-2-FREEZE-MANIFEST-WRITE-001A.DRAFT.md', 'docs/codex/tasks/LRGG-CANDIDATE-FREE-TIER0-2-FREEZE-NUMERIC-RESOLUTION-AND-MANIFEST-WRITE-PREP-001A.md', 'docs/codex/tasks/LRGG-CANDIDATE-FREE-TIER0-2-FREEZE-PROPOSAL-TABLE-001A.md', 'docs/codex/tasks/LRGG-CANDIDATE-FREE-TIER0-2-IMPLEMENTATION-RUN-001A.md', 'docs/codex/tasks/LRGG-CANDIDATE-FREE-TIER0-2-OPERATOR-FREEZE-RESOLUTION-PROPOSAL-001A.md', 'docs/codex/tasks/TLGP-001B-R2-PROVENANCE-BANK-001A-CODEX-EXEC.md', 'docs/codex/tasks/TLGP-CAPWITNESS-RETRIEVAL-NEW-SESSION-HANDOFF-20260630.md', 'docs/codex/tasks/TLGP-GROKKING-001B-NEW-SESSION-HANDOFF-20260630.md', 'docs/codex/tasks/TLGP-POWERED-RUNG3-NEW-SESSION-HANDOFF-20260701.md', 'docs/codex/tasks/TLGP-RUNG1-CAPACITY-SWEEP-002A-NEW-SESSION-HANDOFF-20260701.md', 'docs/research/ACPC-PREDICTION-CORRECTION-LOOP-ROUTE-DECISION-001A.md', 'docs/research/ACTION-CONDITIONED-SELF-BOUNDARY-PREFLIGHT-001A.md', 'docs/research/AUDIT-REQUEST-TLGP-001A-FOR-EXTERNAL-REDTEAM.md', 'docs/research/CLAUDE-INDEPENDENT-ACSB-001D-DELTA-REAUDIT-R1-R5-001A.md', 'docs/research/CLAUDE-INDEPENDENT-LRGG-CANDIDATE-FREE-PREFLIGHT-HOSTILE-SYNTHESIS-001A.md', 'docs/research/FSP-ENV-DESIGN-CONSTRAINTS-001A.md', 'docs/research/FSP-ENV-DESIGN-CONSTRAINTS-001A.md', 'docs/research/FSP-LADDER-MEMO-001A.md', 'docs/research/FSP-LADDER-MEMO-001A.md', 'docs/research/FSP-MASTER-PHASE-PLAN-001A.md', 'docs/research/FSP-MASTER-PHASE-PLAN-001A.md', 'docs/research/FSP-ROADMAP-CONTINGENCY-001A.md', 'docs/research/FSP-ROADMAP-CONTINGENCY-001A.md', 'docs/research/FSP-ROUTE-PROGRAM-001A-functional-subject-proxy-route-design.md', 'docs/research/FSP-ROUTE-PROGRAM-001A-functional-subject-proxy-route-design.md', 'docs/research/FSP-STAGE-LEDGER.md', 'docs/research/FSP-STAGE-LEDGER.md', 'docs/research/JOI-LIKE-BOUNDED-MECHANISM-PROXY-ROADMAP-001A.md', 'docs/research/SESSION-HANDOFF-FSP-20260701.md', 'docs/research/SESSION-HANDOFF-FSP-20260701.md', 'docs/research/SESSION-HANDOFF-FSP-20260702.md', 'docs/research/SESSION-HANDOFF-FSP-20260702.md', 'docs/research/TLGP-RUNG1-CAPACITY-SWEEP-002A-QUEUE4-ROUTE-AUDIT-PREREG-001A.md', 'docs/task_cards/FSP-PUM-ENV-IDENTIFIABILITY-PROBE-001A.md', 'docs/task_cards/FSP-PUM-ENV-IDENTIFIABILITY-PROBE-001A.md', 'docs/task_cards/TLGP-001B-R1.md', 'docs/task_cards/TLGP-001B-R2-PROVENANCE-BANK-001A.md', 'docs/task_cards/TLGP-001B-R2-R1.md', 'docs/task_cards/TLGP-001B-R2.md', 'docs/task_cards/TLGP-CAPABILITY-WITNESS-GROKKING-PROBE-001B-OPERATOR-REVIEW-001A.md', 'docs/task_cards/TLGP-CAPABILITY-WITNESS-GROKKING-RUNNER-PARAMETERIZE-001A.md', 'docs/task_cards/TLGP-CAPABILITY-WITNESS-RUNG1-CAPACITY-SWEEP-002A.md', 'docs/task_cards/XEP-META-SAT-PROBE-001A.md', 'docs/tasks/ITL-DEV-BENCH-001E-DIAGNOSIS-ONLY.md', 'scripts/s0_freeze.ps1', 'scripts/s0_ledger_commit.ps1', 'scripts/trackf_checkpoint_commit.ps1', 'src/__init__.py', 'src/fsp_pum_env/', 'src/fsp_pum_env/__init__.py', 'src/fsp_pum_env/factored_filter.py', 'src/fsp_pum_env/ideal_observer.py', 'src/fsp_pum_env/simulator.py', 'src/lrgg_candidate_free_tier0_2_001a/', 'src/tlgp_001b/', 'src/tlgp_capability_witness_preflight_001a/rung1_capacity_sweep_002a.py', 'tests/fsp_pum_env/', 'tests/fsp_pum_env/test_frozen_design.py', 'tests/fsp_pum_env/test_ideal_observer_s2.py', 'tests/fsp_pum_env/test_simulator_s1.py', 'tests/lrgg_candidate_free_tier0_2_001a/', 'tests/test_rung1_capacity_sweep_002a_001a.py']`
- Old frozen artifacts unchanged: `True`
- Old source files unchanged: `True`

## Stop Conditions

- `forbidden_files_modified`

## Claim Ceiling

Bounded no-candidate evidence about whether a clean CTSR surface is admissible for future mechanism testing. No mechanism success, Gate4/Gate5 validity, candidate behavior, tournament outcome, bridge/runtime/EGO readiness, agency, autonomy, consciousness, emotion, subjectivity, companion readiness, stable user benefit, or mechanism_score claim is authorized.

## What This Does Not Prove

- mechanism success
- mechanism validity
- Gate4 validity
- Gate5 validity
- candidate behavior
- tournament outcome
- bridge readiness
- runtime readiness
- EGO readiness
- agency
- autonomy
- consciousness
- emotion
- subjectivity
- companion readiness
- stable user benefit

## Next Minimal Closed-Loop Action

If independent review accepts this no-candidate preflight, draft a separate bounded candidate task card; otherwise preserve refusal/invalid-harness evidence and close or redesign this CTSR route.
