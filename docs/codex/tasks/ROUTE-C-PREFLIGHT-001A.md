# ROUTE-C-PREFLIGHT-001A

- Status: DRAFT ONLY until explicitly authorized.
- Parent blueprint: `docs/research/ROUTE-C-PREFLIGHT-001A-HOSTILE-DESIGN-BLUEPRINT.md`
- Phase: candidate-free Phase 0 preflight only.
- Claim ceiling: Route C preflight evidence only.
- Auto-Remote-Anchor: forbidden.
- Candidate implementation forbidden.

```yaml
task_id: ROUTE-C-PREFLIGHT-001A
parent_blueprint: ROUTE-C-PREFLIGHT-001A-HOSTILE-DESIGN-BLUEPRINT   # this document, read-only
task_type: bounded preflight implementation (generator + baselines + oracle + controls + gates)
layer: engineering implementation + mechanism-hypothesis preflight   # NOT subjectivity/consciousness
role: implementer   # NOT designer, NOT hostile auditor (role separation, contract)

problem_definition: >
  Implement ONLY the Route C Phase 0 falsification harness: generator (§4),
  observation-only baseline + schema/name-order attackers (§6.1), interventional
  oracle (§6.2), leakage/schema positive controls L1-L8 (§7), and Phase 0 gates
  6.1 + 6.2. Determine whether the surface even instantiates non-identifiability
  with interventional headroom, BEFORE any candidate exists. A blocked result is
  the contract-preferred outcome and must be preserved, not patched.

current_stage: pre-implementation (no src/tests/artifacts for route_c_preflight_001a exist)

hypothesis: >
  On the confounded generator (§3), observation-only is at chance (k/C) by
  construction while a randomized-intervention oracle exceeds it beyond
  HEADROOM_BAND. Honest-null outcomes are equally acceptable: obs decodes S
  (premise void) or oracle ties obs (no headroom) -> Route C dies at design.

baseline: obs_only_baseline; schema_only_attacker; name_order_attacker (§6.1). Oracle = ceiling only (§6.2).
ablation: NONE in Phase 0 (candidate-phase, §9). Fail-able controls: gain=0 (kills 6.2), L1 inject (kills 6.1).
trace_replay_requirement: trace.jsonl per §11; replay deferred (no candidate/belief to serialize yet).

candidate_implementation: FORBIDDEN in this task (Phase 0 is candidate-free).
fair_interventional_panel: SPECIFIED ONLY (§6.3), not implemented here.

acceptance_gate: >
  Emit preflight_admitted_for_candidate_design IFF 6.1=non_identifiability_present
  AND 6.2=interventional_headroom_present AND all L1-L8 fire on injection AND
  thresholds_frozen_before_run AND no forbidden path touched. Otherwise emit the
  matching blocked_* verdict + failure_manifest.json.

claim_ceiling: >
  Route C preflight evidence only (does non-identifiability + headroom hold on
  this constructed generator/seeds/thresholds). No mechanism, no candidate result,
  no Gate, no mainline, no agency/autonomy/consciousness/emotion, no stable user
  benefit, no EGO/companion readiness, no proof of any total theory.

allowed_paths:
  - src/route_c_preflight_001a/**
  - tests/route_c_preflight_001a/**
  - artifacts/route_c_preflight_001a/**

forbidden_paths:
  - any candidate implementation or Route C mechanism claim
  - any Gate run (Gate0-5), bridge, tournament, runtime, scheduler, admission
  - src/acsb_*, src/action_conditioned_self_boundary_*  (ACSB files, read-only history)
  - src/acolb_*  (ACOLB files, read-only history)
  - src/acp_bv_*  (ACP-BV files, read-only history)
  - ego_mainline/*, companion/product/LLM/RAG/AIRI/UI, global schemas
  - docs/** rule sources (this blueprint, the route decision, the ACSB closure,
    the provenance contract) -> read-only
  - any push / tag / remote-anchor script

allowed_outcomes:
  - preflight_admitted_for_candidate_design
  - blocked_by_observation_decodable_self_set
  - blocked_by_no_interventional_headroom
  - blocked_by_schema_alias_leakage
  - blocked_by_non_fail_able_control
  - blocked_by_provenance_gap

hard_blockers (any -> STOP + failure_manifest.json, no mechanism claim, preserve artifacts):
  - blocked_by_observation_decodable_self_set
  - blocked_by_no_interventional_headroom
  - blocked_by_schema_alias_leakage
  - blocked_by_action_label_leakage
  - blocked_by_hidden_self_set_leakage
  - blocked_by_intervention_api_leakage
  - blocked_by_non_fail_able_control
  - blocked_by_provenance_gap
  - blocked_by_forbidden_path
  - blocked_by_codex_success_redefinition

prohibitions:
  - do NOT implement a candidate or the fair interventional panel (defer)
  - do NOT tune confounder_strength / gain / ceiling / bands after seeing results
  - do NOT add interventional data to the obs-only baseline
  - do NOT redefine a blocked_* outcome as success; do NOT patch a STOP into a pass
  - do NOT edit ACSB/ACOLB/ACP-BV files, this blueprint, or any docs rule source
  - Auto-Remote-Anchor: FORBIDDEN (no push, no tag, no remote anchor)

stop_condition: emit failure_manifest.json on first hard blocker; preserve all artifacts; stop.
rollback_plan: >
  All work confined to the three allowed paths. Rollback = delete
  src/route_c_preflight_001a, tests/route_c_preflight_001a,
  artifacts/route_c_preflight_001a. No global/schema change, no remote state.

required_final_report (implementer):
  verdict, layer, files_changed, commands_run, tests_run, artifacts_generated,
  obs_only_result, oracle_result, headroom_verdict, non_identifiability_verdict,
  leakage_control_results (L1-L8 fired?), thresholds_frozen_before_run,
  stop_conditions_triggered, claim_ceiling, what_this_does_not_prove, remaining_unknowns

next_role_after_implementation: hostile auditor (separate pass) re-runs + tampers vs this frozen blueprint.
```
