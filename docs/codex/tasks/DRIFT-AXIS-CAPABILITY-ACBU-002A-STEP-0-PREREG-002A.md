# DRIFT-AXIS-CAPABILITY-ACBU-002A-STEP-0-PREREG-002A   (FINAL monolith; 5 final patches applied)
Status/lineage/layer/ceiling: as -002A card. Frozen = ancestor commit of any run. No scoring. NO self-CLEAR.

## supersedes: 001A ideal-gap (definitional) + 001A banked prereg 50c6ca82 (HAZARD_COVERAGE_ASYMMETRY).

## 1. environment (FROZEN)  K=10,T=200; g_1~U{1..K}; t≥2 w.p.h g_t~U({1..K}\{g_{t-1}}) else hold;
reward Bernoulli p_high=0.70/p_low=0.30 (gap0.40) family-wide; observation=(a_t,r_t).

## 2. coverage-matched split (FROZEN)  [PATCH-1: renamed; in-distribution, NOT OOD]
Candidate hazard prior support H_grid={0.01,0.02,0.035,0.05,0.08,0.10,0.12,0.15} uniform.
C-MetaRecurrent-BROAD (PRIMARY) train hazard = Uniform(H_grid).
C-MetaRecurrent-NARROW (DIAGNOSTIC, REQUIRED) train hazard = {0.02,0.05}; may not establish PROCEED.
F_MATCHED_SUPPORT_PRIMARY = hazard 0.10 (∈H_grid ∈Broad training; IN-DISTRIBUTION for both; NOT
held-out, NOT hazard-OOD); primary verdict cell. Reported grid {0.08,0.10,0.12}@gap0.40 (verdict on
0.10). F_EXTRAPOLATION_SECONDARY (diagnostic only, not in verdict): gap-shift 0.30; semi-Markov dwell;
hazards outside H_grid.

## 3. access + disclosure (FROZEN)  Candidate=DISCLOSED MODEL_FORM_ACCESS: hazard prior coverage-matched
to Broad; reward levels 0.70/0.30 = reward-form disclosed, same-family in-distribution (Broad learns
them). claim_access_rung==access_rung_candidate else FAIL. Never cell g_t/exact-hazard (=ORACLE).

## 4. candidate policy (FROZEN, callable)  b_t(g,h),h∈H_grid uniform. M(b,i,o)[g,h]∝b[g,h]L(o|g,i);
T(b)[g',h]=(1−h)b[g',h]+h(Σ_{g≠g'}b[g,h])/(K−1); U=T∘M. bg[g]=Σ_h b[g,h]; imm(b,i)=bg[i]p_high+
(1−bg[i])p_low; base=p_low+(p_high−p_low)max_j Σ_h T(b)[j,h]; future_i=Σ_o P(o|b,i)[p_low+(p_high−p_low)
max_j Σ_h U(b,i,o)[j,h]],P(1|b,i)=imm; KG_i=future_i−base; q_i=imm+KG_i; a_t=argmax_i q_i(ties→low);
b_{t+1}=U(b_t,a_t,o_t). LOG-ONLY IG_i=H(bg)−Σ_o P(o|b,i)H(g-marg M(b,i,o)); never in q.

## 5. baselines + R* (FROZEN)  Broad&Narrow: GRU h128; input[1hot arm(10),reward(1),norm t(1)]; A2C;
Adam3e-4; entropy0.01; γ0.99; ladder[50k,100k,200k]; adequacy own-train norm_regret≤0.15 at first
adequate rung; Broad no-rung → UNDERPOWERED_BASELINE; max_rung>cap → COMPUTE_INFEASIBLE. R*=known-params
receding-horizon planner depth L∈{5,7} (calib-selected, freeze pre-score; policy exceeding R*+0.005 →
METRIC_INVALID). norm_regret=(R*−policy)/(R*−random), denom once/cell. Weak controls as listed.

## 6. statistics (FROZEN, callable)  Unit=training seed s∈{1..20}/baseline; same 2000 env episode seeds
as candidate. total_sep_B=mean_s[norm_regret(B_s)−norm_regret(cand_probe)], B∈{Broad,Narrow}.
probe_increment=norm_regret(cand_no_info_gain)−norm_regret(cand_probe);
belief_increment=norm_regret(cand_frozen_belief)−norm_regret(cand_probe).
coverage_confound=reg_meta_narrow−reg_meta_broad (ALWAYS reported, with CI).
CI=cluster bootstrap over 20 seeds (10k, episode nested); half_width=(U−L)/2.
precision_adequate(Δ)≡half_width(Δ)≤0.05; win(Δ)≡lower95(Δ)>0.05; equivalent(Δ)≡CI(Δ)⊆[−0.05,0.05];
advantage_removed(Δ)≡upper95(Δ)≤0.05.     [PATCH-3 primitive]

## 7. env admissibility (FROZEN, callable; BLOCKING)  reg_probe=known-params candidate;
reg_passive=known-params greedy filter(a=argmax bg,updates U,no KG). active_probe_abs=(reward(reg_probe)
−reward(reg_passive))/(reward(R*)−reward(random)); passive_closes=(reward(reg_passive)−reward(random))/
(reward(reg_probe)−reward(random)). ADMISSIBLE iff active_probe_abs>0.10 AND passive_closes≤0.90.
K1 analytic Bayes decoder (a,r)→g: ≤0.35 pass; 0.35<acc≤0.50 ENV_WEAK_K1_FLAG (not blocking if
admissibility passes; blocks language above ceiling; result carries flag); >0.50 ENV_INADMISSIBLE.

## 8. ablations + destroyed() (FROZEN, callable)  [PATCH-3/4]
Ablations: no_info_gain(argmax imm); random_probe(0.1 uniform else greedy imm); frozen_belief(b≡b_1);
no_hazard_mix(h=0). destroy_set = { probe_increment, belief_increment, total_sep_no_info_gain@Broad,
total_sep_random_probe@Broad, total_sep_frozen_belief@Broad }.
precision_adequate(destroy_set) ≡ ∀Δ∈destroy_set precision_adequate(Δ).
probe_real≡win(probe_increment); belief_update_real≡win(belief_increment).
destroyed ≡ probe_real AND belief_update_real AND advantage_removed(total_sep_no_info_gain@Broad)
  AND advantage_removed(total_sep_random_probe@Broad) AND advantage_removed(total_sep_frozen_belief@Broad).
no_hazard_mix: DIAGNOSTIC — if NOT advantage_removed(total_sep_no_hazard_mix@Broad) →
HAZARD_MIX_NOT_ISOLATED_FLAG, claim drops "exploits drift-rate structure". Not blocking.

## 9. verdict callable (FROZEN)  [PATCH-2 order + terminal]
def verdict(r):
  if compute_infeasible:                                            return COMPUTE_INFEASIBLE
  if metric_invalid:                                                return METRIC_INVALID
  if not env_admissible:                                            return ENV_INADMISSIBLE
  if candidate_saw_F_OOD_params or (access_rung_candidate=='MODEL_FORM_ACCESS'
     and claim_access_rung=='EQUAL_ACCESS'):                        return UNDISCLOSED_ORACLE_OR_FORM_ACCESS_FAIL
  if RL2_broad_first_adequate_rung is None:                         return UNDERPOWERED_BASELINE
  if not precision_adequate(total_sep_broad):                       return UNDERPOWERED
  if win(total_sep_narrow) and equivalent(total_sep_broad):
     if not precision_adequate(total_sep_narrow):                   return UNDERPOWERED
     return HAZARD_COVERAGE_CONFOUND_SATURATED_UNDER_MATCHED_COVERAGE
  if equivalent(total_sep_broad):                                   return SATURATED_BASELINE_EQUIVALENCE
  if win(total_sep_narrow) and not win(total_sep_broad):
     if not precision_adequate(total_sep_narrow):                   return UNDERPOWERED
     return HAZARD_COVERAGE_CONFOUND
  if win(total_sep_broad) and not precision_adequate(destroy_set):  return UNDERPOWERED_ABLATION
  if win(total_sep_broad) and destroyed:                            return PROCEED_NARROW   # +HAZARD_MIX/+WEAK_K1 flags if set
  if win(total_sep_broad) and equivalent(probe_increment):          return DISCLOSED_MODEL_FORM_PRIOR_WIN_PROBING_NULL
  if win(total_sep_broad):                                          return ABLATION_NON_DESTRUCTIVE
  return INCONCLUSIVE
# BUDGET_OR_SHIFT_ARTIFACT_FLAG: total_sep_broad point-est>0 in <2 of 3 grid cells; never overrides.
# PROCEED_NARROW may be established ONLY from total_sep_broad; total_sep_narrow may NEVER establish it.

## 10. cost calibration + reduction ladder (FROZEN)  [PATCH-5: Narrow required]
1 seed end-to-end incl BOTH baselines; project ×20. ≤3 CPU-hr AND max_rung feasible → proceed. Else
reduce IN ORDER, re-project: (1) drop F_EXTRAPOLATION_SECONDARY; (2) drop non-primary grid cells (keep
primary); (3) drop weak controls except {random,myopic_greedy}; (4) cut eval episodes while
precision_adequate holds. FORBIDDEN reductions: primary cell, 20 seeds, MDE, band, adequacy 0.15, the 4
destroy ablations, max_rung, Broad baseline, NARROW baseline, coverage_confound reporting. If Narrow or
Broad cannot run under cap → COMPUTE_INFEASIBLE (bank a superseding reduced prereg that explicitly drops
the confound diagnostic; do NOT silently void coverage_confound).

## 11. trace/replay + artifacts + forbidden (FROZEN)  Per step: t, b_t(g,h) summary, a_t, {q_i,KG_i,
IG_i(log)}, pred o, actual o, error, b_{t+1}, θ_t=(g_t,h) ceiling-only, per-framework RNG seeds; both
baselines' seed/manifest/rung. Replay reconstructs candidate b-traj from (b_0,{a_t,o_t})+frozen U
bit-exact; 2 fresh-process recomputes match. Artifacts under artifacts/DRIFT-AXIS-CAPABILITY-ACBU-002A/:
result.json(per-cell metrics, Broad+Narrow, coverage_confound, increments, verdict, flags), trace.jsonl,
baseline_comparison.json, ablation_report.json, admissibility_report.json, precision_report.json,
replay_report.json, claim_ceiling.txt, failure_manifest.json. Isolated src/drift_capability_acbu/.
Forbidden: EGO/LLM/AIRI/UI/emotion/proactive, global schema, any prior artifact, credentials,
pixel/physics, StructuredInferred at STEP-0, Narrow→PROCEED, calling primary cell OOD, post-score frozen
changes, weakening Broad/MDE/band, chasing extrapolation to rescue.