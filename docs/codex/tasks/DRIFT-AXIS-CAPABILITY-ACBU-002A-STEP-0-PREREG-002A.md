# DRIFT-AXIS-CAPABILITY-ACBU-002A-STEP-0-PREREG-002A   (FINAL monolith; 5 patches + audit-R1 fixes)
Status/lineage/layer/ceiling: as -002A card. Frozen = ancestor commit of any run. No scoring. NO self-CLEAR.

## supersedes: 001A ideal-gap (definitional) + 001A banked prereg 50c6ca82 (HAZARD_COVERAGE_ASYMMETRY).

## 1. environment (FROZEN)
K=10, T=200; g_1~U{1..K}; t≥2 w.p. h g_t~U({1..K}\{g_{t-1}}) else hold; reward Bernoulli
p_high=0.70/p_low=0.30 (gap 0.40) family-wide; observation=(a_t,r_t).

## 2. coverage-matched split (FROZEN)  [in-distribution, NOT OOD]
Candidate hazard prior support H_grid={0.01,0.02,0.035,0.05,0.08,0.10,0.12,0.15} uniform.
C-MetaRecurrent-BROAD (PRIMARY) train hazard = Uniform(H_grid).
C-MetaRecurrent-NARROW (DIAGNOSTIC, REQUIRED) train hazard = {0.02,0.05}; may not establish PROCEED.
F_MATCHED_SUPPORT_PRIMARY = hazard 0.10 (∈H_grid ∈Broad training; IN-DISTRIBUTION for both; NOT held-out,
NOT hazard-OOD); primary verdict cell. Reported grid {0.08,0.10,0.12}@gap0.40 (verdict on 0.10).
F_EXTRAPOLATION_SECONDARY (diagnostic only, not in verdict): gap-shift 0.30; semi-Markov dwell; hazards
outside H_grid.

## 3. access + disclosure (FROZEN)
Candidate=DISCLOSED MODEL_FORM_ACCESS: hazard prior coverage-matched to Broad; reward levels 0.70/0.30 =
reward-form disclosed, same-family in-distribution (Broad learns them). claim_access_rung==
access_rung_candidate else FAIL. Never cell g_t/exact-hazard (=ORACLE).
candidate_saw_cell_params ≡ candidate had access to the PRIMARY/EVAL cell's true hazard value or g_t
(= ORACLE violation). The guard MUST trip on exact-hazard leak at the matched-support cell, not only on
OOD cells. (Renamed from candidate_saw_F_OOD_params.)

## 4. candidate policy (FROZEN, callable)
b_t(g,h), h∈H_grid uniform. M(b,i,o)[g,h]∝b[g,h]·L(o|g,i); T(b)[g',h]=(1−h)b[g',h]+h(Σ_{g≠g'}b[g,h])/(K−1);
U=T∘M. bg[g]=Σ_h b[g,h]; imm(b,i)=bg[i]p_high+(1−bg[i])p_low; base=p_low+(p_high−p_low)max_j Σ_h T(b)[j,h];
future_i=Σ_o P(o|b,i)[p_low+(p_high−p_low)max_j Σ_h U(b,i,o)[j,h]], P(1|b,i)=imm; KG_i=future_i−base;
q_i=imm+KG_i; a_t=argmax_i q_i (ties→low); b_{t+1}=U(b_t,a_t,o_t). LOG-ONLY IG_i=H(bg)−Σ_o P(o|b,i)
H(g-marg M(b,i,o)); never in q.

## 5. baselines + reference (FROZEN)  [audit-R1 B4: raw metric; R* → logged R_ref, no ceiling]
Broad & Narrow: GRU hidden 128; input [1hot arm(10), reward(1), norm t(1)]; A2C; Adam 3e-4; entropy 0.01;
γ 0.99; ladder [50k,100k,200k] episodes, max_rung 200k (only episode count varies across rungs).
R_ref = the §4 candidate policy run with the cell's TRUE (p_high,p_low,h) (known-params candidate). It is
a LOGGED reference + adequacy reference ONLY — NOT a metric denominator, NOT a proven optimum. Cheap
(one-step KG). Log R_REF_EXCEEDED_FLAG if any evaluated policy mean-reward > reward(R_ref) (non-blocking).
Broad & Narrow are trained to the MAX FEASIBLE rung (highest ladder rung that fits the cost cap after §10
reductions; ≥50k or COMPUTE_INFEASIBLE) and evaluated AT THAT rung — the STRONGEST feasible baseline, NOT
a first-adequate rung (audit-R2 B4 fix). Adequacy is FAIL-CLOSED ONLY, with the bar equal to MDE (there
is NO separate ε_adeq slack, so a win margin can never fall inside baseline-undertraining slack):
RL2_broad_adequate ≡ reward(R_ref,F_train) − reward(Broad_max,F_train) ≤ MDE. NOT adequate →
UNDERPOWERED_BASELINE (Broad too weak even at max feasible training to be a fair comparator; no positive
verdict). F_train ≡ the training-distribution evaluation suite (hazard ~ Uniform(H_grid), gap 0.40, same
K/T/reward family as §1), scored on the frozen 2000 env episode seeds (§6). reward(R_ref,F_train) and
reward(Broad_max,F_train) are committed as `adequacy_eval` rows in baseline_comparison.json, and
RL2_broad_adequate is computed ONLY from those committed rows (no train-set reuse, no future info).
Weak controls (memoryless/random/majority/myopic/lookup) = engineering-sufficient only, logged.

## 6. statistics (FROZEN, callable)  [audit-R1 B4: RAW mean reward/step; positive = candidate better]
reward(P) = mean reward per step of policy P over the shared 2000 env episode seeds. Unit = training seed
s∈{1..20} per baseline; candidate deterministic given env seeds + frozen priors.
MDE = BAND = 0.01 reward/step (FROZEN; rationale: ≈4% of the ~0.25 reachable-over-random reward spread;
non-hairline; detectable at 20 seeds × 2000 eps; set ex-ante and biased toward SATURATED, not PROCEED).
sep_B = mean_s[ reward(cand_probe) − reward(B_s) ],  B∈{Broad,Narrow}.
probe_increment  = reward(cand_probe) − reward(cand_no_info_gain).
belief_increment = reward(cand_probe) − reward(cand_frozen_belief).
adv_X = reward(cand_X) − reward(Broad)  for X∈{no_info_gain, random_probe, frozen_belief, no_hazard_mix}.
coverage_confound = reward(Broad) − reward(Narrow)  (ALWAYS reported, with CI; +ve ⇒ Narrow handicapped).
CI = cluster bootstrap over the 20 seeds (10k resamples, episode-level nested); half_width=(U−L)/2.
precision_adequate(Δ)≡half_width(Δ)≤MDE; win(Δ)≡lower95(Δ)>MDE; equivalent(Δ)≡CI(Δ)⊆[−BAND,+BAND];
advantage_removed(Δ)≡upper95(Δ)≤MDE.

## 7. env admissibility (FROZEN, callable; BLOCKING)
reg_probe = R_ref (known-params candidate); reg_passive = known-params GREEDY filter (a=argmax bg, updates
U, no KG). active_probe_abs=(reward(reg_probe)−reward(reg_passive))/(reward(reg_probe)−reward(random));
passive_closes=(reward(reg_passive)−reward(random))/(reward(reg_probe)−reward(random)). ADMISSIBLE iff
active_probe_abs>0.10 AND passive_closes≤0.90 else ENV_INADMISSIBLE.
K1 analytic Bayes decoder (a,r)→g: ≤0.35 pass; 0.35<acc≤0.50 ENV_WEAK_K1_FLAG (not blocking if
admissibility passes; blocks language above ceiling; result carries flag); >0.50 ENV_INADMISSIBLE.

## 8. ablations + destroyed() (FROZEN, callable)
Ablations: no_info_gain(argmax imm); random_probe(0.1 uniform else greedy imm); frozen_belief(b≡b_1);
no_hazard_mix(h=0). destroy_set = { probe_increment, belief_increment, adv_no_info_gain,
adv_random_probe, adv_frozen_belief }. precision_adequate(destroy_set) ≡ ∀Δ∈destroy_set precision_adequate(Δ).
probe_real≡win(probe_increment); belief_update_real≡win(belief_increment).
destroyed ≡ probe_real AND belief_update_real AND advantage_removed(adv_no_info_gain)
AND advantage_removed(adv_random_probe) AND advantage_removed(adv_frozen_belief).
no_hazard_mix: DIAGNOSTIC — if NOT advantage_removed(adv_no_hazard_mix) → HAZARD_MIX_NOT_ISOLATED_FLAG,
claim drops "exploits drift-rate structure". Not blocking.

## 9. verdict callable (FROZEN)  [audit-R1: raw sep_*, cell-param guard, METRIC_INVALID repurposed]
def verdict(r):
  if compute_infeasible:                                            return COMPUTE_INFEASIBLE
  if (reward(reg_probe) − reward(random)) < 0.05:                   return METRIC_INVALID   # no achievable headroom
  if not env_admissible:                                            return ENV_INADMISSIBLE
  if candidate_saw_cell_params or (access_rung_candidate=='MODEL_FORM_ACCESS'
     and claim_access_rung=='EQUAL_ACCESS'):                        return UNDISCLOSED_ORACLE_OR_FORM_ACCESS_FAIL
  if not RL2_broad_adequate:                                        return UNDERPOWERED_BASELINE  # Broad_max within MDE of R_ref (§5)
  if not precision_adequate(sep_broad):                             return UNDERPOWERED
  if win(sep_narrow) and equivalent(sep_broad):
     if not precision_adequate(sep_narrow):                         return UNDERPOWERED
     return HAZARD_COVERAGE_CONFOUND_SATURATED_UNDER_MATCHED_COVERAGE
  if equivalent(sep_broad):                                         return SATURATED_BASELINE_EQUIVALENCE
  if win(sep_narrow) and not win(sep_broad):
     if not precision_adequate(sep_narrow):                         return UNDERPOWERED
     return HAZARD_COVERAGE_CONFOUND
  if win(sep_broad) and not precision_adequate(destroy_set):        return UNDERPOWERED_ABLATION
  if win(sep_broad) and destroyed:                                  return PROCEED_NARROW   # +HAZARD_MIX/+WEAK_K1 flags if set
  if win(sep_broad) and equivalent(probe_increment):                return DISCLOSED_MODEL_FORM_PRIOR_WIN_PROBING_NULL
  if win(sep_broad):                                                return ABLATION_NON_DESTRUCTIVE
  return INCONCLUSIVE
# BUDGET_OR_SHIFT_ARTIFACT_FLAG: sep_broad point-est>0 in <2 of 3 grid cells; never overrides.
# PROCEED_NARROW may be established ONLY from sep_broad; sep_narrow may NEVER establish it.
# R_REF_EXCEEDED_FLAG logged; non-blocking.

## 10. cost calibration + reduction ladder (FROZEN)  [Narrow required]
1 seed end-to-end incl BOTH baselines; project ×20. ≤3 CPU-hr AND max_rung feasible → proceed. Else
reduce IN ORDER, re-project: (1) drop F_EXTRAPOLATION_SECONDARY; (2) drop non-primary grid cells (keep
primary); (3) drop weak controls except {random,myopic_greedy}; (4) cut eval episodes while
precision_adequate holds. Reductions must FREE compute so the STRONGEST feasible baseline rung is used;
they may never substitute a weaker rung while a stronger one would fit. FORBIDDEN reductions: primary
cell, 20 seeds, MDE, BAND, the adequacy=MDE bar, the 4 destroy ablations, max_rung ceiling, use of the
max-feasible rung, Broad baseline, NARROW baseline, coverage_confound reporting. If Narrow or Broad
cannot reach ≥50k under cap → COMPUTE_INFEASIBLE (bank a superseding reduced prereg that explicitly drops
the confound diagnostic; do NOT silently void coverage_confound).

## 11. trace/replay + artifacts + forbidden (FROZEN)
Per step: t, b_t(g,h) summary, a_t, {q_i,KG_i,IG_i(log)}, pred o, actual o, error, b_{t+1}, θ_t=(g_t,h)
ceiling-only, per-framework RNG seeds; both baselines' seed/manifest/rung. Replay reconstructs candidate
b-traj from (b_0,{a_t,o_t})+frozen U bit-exact; 2 fresh-process recomputes match. Artifacts under
artifacts/DRIFT-AXIS-CAPABILITY-ACBU-002A/: result.json (per-cell raw rewards, Broad+Narrow,
coverage_confound, sep_*, increments, verdict, flags), reference_values.json (R_ref, random,
R_REF_EXCEEDED_FLAG), trace.jsonl, baseline_comparison.json, ablation_report.json,
admissibility_report.json, precision_report.json, replay_report.json, claim_ceiling.txt,
failure_manifest.json. Isolated src/drift_capability_acbu/. Forbidden: EGO/LLM/AIRI/UI/emotion/proactive,
global schema, any prior artifact, credentials, pixel/physics, StructuredInferred at STEP-0,
Narrow→PROCEED, calling primary cell OOD, post-score frozen changes, weakening Broad/MDE/BAND or using a
weaker-than-max-feasible baseline rung to move a verdict, chasing extrapolation to rescue.
