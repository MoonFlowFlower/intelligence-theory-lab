## 9. Minimal Codex implementation card (exactly one, for Design A)

```
TASK CARD
task_id: ACOLB-001A   (action-conditioned online latent-boundary, surface A)
type: bounded mechanism-surface implementation (Phase 0 headroom preflight gates Phase 1)
layer: engineering implementation + mechanism hypothesis
authorization: DRAFT ONLY — not authorized to execute. Requires explicit Codex run instruction.

problem definition:
  Build a minimal executable surface where heldout counterfactual action-outcome
  (viability-boundary) prediction under an OOD/episode-fresh latent requires an
  online action-conditioned prediction-error belief update, and where the strongest
  fair baseline (incl. a convergence-trained amortized sequence model) cannot reach
  the oracle ceiling on the OOD split.

current stage: pre-implementation. No prior ACOLB artifacts exist.

hypothesis:
  candidate (recursive Bayesian/GLM PE-update over latent theta) > strongest fair
  baseline on OOD heldout queries beyond predeclared band; ablations on the update
  path collapse to the no_update floor; behavior replayable from serialized_state.

baseline panel (all callable, same legal channel, same budget B, same scorer):
  parametric_frozen, amortized_seq[STRONGEST], exact_key_memory, partial_key_memory,
  factorized_lookup, count_table, successor_map, transition_table/graph_lookup,
  fsm_planner, episodic_traversal, action_conditioned_nearest_neighbor,
  sequence_imitation, no_update[FLOOR]; oracle[privileged, ceiling-only].

ablations (re-run episodes under real intervention; predeclared directions):
  A1 no_update -> floor; A2 no_action_conditioning -> drop; A3 no_PE_correction -> floor;
  A4 shuffled_labels -> <= floor (else STOP: disguised lookup);
  A5 shuffled_probe_order -> NO drop stationary / drop changepoint;
  A6 frozen_posterior_pre_informative_probes -> drop.

trace/replay requirement:
  trace.jsonl per step: {run_id, episode_id, seed, t, action a_t, predicted y_hat,
    actual y_t, prediction_error e_t, posterior mu_t/Sigma_t, query preds, producer_function}.
  Replay re-EXECUTES the update from serialized_state + legal obs + code_path_hash and
  reproduces (mu,Sigma) + query answers within tolerance (NOT hash compare).
  Counterfactual replay on an ablation's action sequence MUST diverge.

acceptance gate (ALL required; predeclared, no post-hoc tuning):
  Phase 0 headroom_preflight.json.verdict == headroom_present
    (OOD headroom > band AND in-distribution negative control holds); else STOP/close.
  Gate3: OOD (candidate - strongest_fair) > band  AND  in-dist |candidate - amortized_seq| <= band.
  Recovery floor: candidate - no_update >= rho*(oracle - no_update), rho predeclared.
  Gate1: leakage scanner L1-L6 pass with positive controls firing; training-invariance fails
    for candidate (candidate MUST depend on legal probe data).
  >= 5 seeds; report CIs.

computed-evidence requirements (no green self-report):
  every score carries producer_function, inputs, run_id, seed, episode_ids, aggregation,
  code_path_hash; independent callable baselines; ablations rerun under real intervention;
  leakage scanner with positive controls; replay from serialized_state + observation
  recomputation; failure_manifest.json on any failure instead of green.

band: predeclared (e.g. |delta| <= 0.02 as in 001B b3). rho: predeclared (e.g. 0.5).
seeds: predeclared set (>=5).

claim ceiling: see this doc section 8 (future-run ceiling). Bounded local mechanism
  evidence only. No Gate-pass honorific, no subjectivity/agency/EGO claim, no mainline.

stop condition: S1-S4 (this doc section A.12) + headroom saturated_close/parity_broken_close.

rollback: isolated branch; writes only under src/acolb_001a/, tests/acolb_001a/,
  artifacts/acolb_001a/. Any gate fail -> failure_manifest.json, do not anchor, leave
  unmerged. No mainline, no LLM, no global schema migration, no remote anchor.

files allowed:   src/acolb_001a/**, tests/acolb_001a/**, artifacts/acolb_001a/**
files forbidden: everything else (EGO mainline, global config/schema, other surfaces,
  ACP-BV 001B files, governance stacks).
commands expected: python -m acolb_001a.headroom_preflight ; python -m acolb_001a.runner ;
  pytest tests/acolb_001a/ -q
expected artifacts: headroom_preflight.json, result.json, trace.jsonl,
  baseline_comparison.json, ablation_report.json, replay_report.json, leakage_report.json,
  parity_report.json, failure_manifest.json (if any failure), claim_ceiling.txt.
```

---
