# ACOLB-001A-IMPL-001A

Status: DRAFT ONLY unless explicitly authorized.
Parent blueprint: `docs/research/ACOLB-001A-IMPLEMENTATION-BLUEPRINT-AUDIT.md`
Claim ceiling: implementation-blueprint / bounded future local mechanism-discrimination evidence only.
Auto-Remote-Anchor: forbidden.
This supersedes the older `ACOLB-001A.md` for implementation specificity; the older card remains route-design context, not execution authorization.
Binding readback: preserves blueprint §14 acceptance conditions, including Phase 0 before candidate-as-evidence, ID negative control, `amortized_seq` convergence/capacity parity, strongest fair baseline selected by argmax, A1..A6 real reruns, replay recomputation not hash compare, L1..L6 leakage positive controls, `failure_manifest.json` on blockers, no `amortized_seq` weakening, no post-score threshold tuning, future allowed paths only, and Auto-Remote-Anchor forbidden.

---

## 16. Codex implementation card (bounded; the only authorization this blueprint emits)

```yaml
task_id: ACOLB-001A-IMPL-001A
parent_blueprint: ACOLB-001A-IMPLEMENTATION-BLUEPRINT-AUDIT   # this document, read-only
task_type: bounded mechanism-surface implementation (engineering + mechanism-hypothesis)
layer: engineering implementation + mechanism hypothesis testing   # NOT subjectivity/consciousness
role: implementer   # NOT designer, NOT hostile auditor (role separation, contract)

problem_definition: >
  Implement the ACOLB-001A online action-conditioned prediction-error belief-update
  surface exactly as specified in the parent blueprint, such that the F1 risk
  (OOD gap from an underpowered/unfair amortized baseline) is observable and terminal
  via Phase-0 ID negative control + convergence/parity gates, before any mechanism claim.

current_stage: pre-implementation (no src/tests/artifacts for acolb_001a exist yet)

hypothesis: >
  On the specified OOD generator, a recursive action-conditioned PE update will be
  non-equivalent to the strongest fair baseline (incl. converged amortized_seq) beyond
  OOD_BAND, while passing the in-distribution parity negative control and load-bearing ablations.
  Null/expected-honest outcome: amortized_seq ties OOD -> saturated_close (route closes).

baseline: full panel in blueprint §6; strongest fair = argmax (by number); oracle = ceiling only.
ablation: A1..A6 as real reruns (§9).
trace_replay_requirement: trace.jsonl (§12.1) + recompute-from-serialized-state replay (§10), not hash compare.

acceptance_gate: blueprint §14 (all 10 conditions, artifact-backed).
claim_ceiling: >
  bounded offline mechanism-discrimination evidence on this generator/seeds/band only.
  No consciousness, subjectivity, emotion, agency, autonomy, AGI, companion/EGO readiness,
  stable user benefit, or proof of any total theory.

allowed_paths:
  - src/acolb_001a/**
  - tests/acolb_001a/**
  - artifacts/acolb_001a/**
forbidden_paths:
  - any prior surface (src/acp_bv_*, src/acsb_*, etc.), ego_mainline/runtime/bridge/scheduler/admission
  - companion/product/LLM/RAG/AIRI, global schemas, docs/** rule sources (read-only), push/tag/remote-anchor scripts
  - this blueprint and the cited contracts (read-only rule sources)

hard_blockers (any -> STOP + failure_manifest.json, no mechanism claim):
  - blocked_by_saturated_distribution
  - blocked_by_underpowered_or_unfair_amortized_baseline
  - blocked_by_candidate_truth_or_latent_leakage
  - blocked_by_non_load_bearing_update
  - blocked_by_replay_hash_only
  - blocked_by_ablation_not_rerun
  - blocked_by_baseline_not_independent
  - blocked_by_codex_success_redefinition
  - blocked_by_threshold_tuning / schema_alias_leakage / non_fail_able_control / provenance_gap
  - blocked_by_forbidden_path / remote_anchor / governance_self_modification

prohibitions:
  - do NOT weaken amortized_seq (capacity, budget, channel, seeds)
  - do NOT remove or relax the ID negative control
  - do NOT skip Phase 0 or run candidate-as-evidence before headroom_present + ID parity pass
  - do NOT replace a failure with a warning; do NOT patch failures into passes
  - do NOT change bands/thresholds after seeing scores
  - do NOT edit the blueprint, contracts, or governance files
  - Auto-Remote-Anchor: FORBIDDEN (no push, no tag, no remote anchor)

stop_condition: emit failure_manifest.json on first hard blocker; preserve all artifacts; stop.
rollback_plan: >
  All work confined to the three allowed paths. Rollback = delete src/acolb_001a, tests/acolb_001a,
  artifacts/acolb_001a (no other path touched; no schema/global change to revert). No remote state created.

required_final_report (implementer):
  verdict, layer, files_changed, commands_run, tests_run, artifacts_generated,
  baseline_results, ablation_results, replay_result, leakage_results, headroom_verdict,
  stop_conditions_triggered, claim_ceiling, what_this_does_not_prove, remaining_unknowns

next_role_after_implementation: hostile auditor (separate pass) re-runs + tampers vs this frozen blueprint.
```

---
