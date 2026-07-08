# DRIFT-AXIS-CAPABILITY-ACBU-002A-STEP-0-PREREG-001A  (FINAL, monolithic)

Status: PREREG (Red). Freezes the unrun STEP-0 kill-test as an ANCESTOR commit of any run
(commit-order = anti-tuning proof). Supersedes ACBU-001A. Awaits INDEPENDENT Red-audit (NOT the
designer) of the banked artifact before Phase-2. Codex sole writer. No scoring in this doc.

## superseded note (keep)
ACBU-001A STEP-0 compared online-ideal − amortized-fixed-ideal. REJECTED: in a POMDP the Bayes-
optimal history-conditioned recurrent meta-policy and the explicit belief-state optimal policy
converge to the SAME optimal object under unbounded data/compute; the gap is 0 by definition
(always SATURATED); a memoryless amortized control is a strawman. Route downgraded to a resource-
bounded structured-vs-amortized OOD sample-efficiency kill-test at DISCLOSED model-form access.

## layer / claim ceiling
learning-adaptation / mechanism-hypothesis benchmark design. At most: disclosed-structure, resource-
bounded, family-bounded OFFLINE evidence for active action-conditioned belief-update sample-
efficiency vs amortized recurrent meta-learning, under the trace/replay contract. NOTHING about
equal-access mechanism, functional subject, agency, autonomy, subjectivity, consciousness, EGO/
companion readiness.

## 1. environment (FROZEN, callable)
K=10 arms, horizon T=200. g_1~Uniform{1..K}. For t≥2: w.p. h, g_t~Uniform({1..K}\{g_{t-1}}); else
g_t=g_{t-1}. Reward Bernoulli: P(r=1|a_t=g_t)=p_high, P(r=1|a_t≠g_t)=p_low. Agent observation=(a_t,r_t).
Reward levels FIXED family-wide: p_high=0.70, p_low=0.30 (gap 0.40) in F_train AND primary OOD.

## 2. family split (FROZEN)
F_train: hazard sampled per episode uniformly from {0.02, 0.05}; gap 0.40.
F_OOD_PARAM_PRIMARY (PRIMARY VERDICT): hazard = 0.10, gap 0.40. (hazard-only OOD; disjoint from train.)
Reported hazard grid (failure geography, same gap 0.40): hazard∈{0.08,0.10,0.12}; verdict on 0.10 ONLY.
F_OOD_SECONDARY (stress, NOT in primary verdict): (a) gap-shift cells gap=0.30 (0.65/0.35);
  (b) semi-Markov dwell (non-geometric). Diagnostic only.

## 3. access rungs (PRE-DECLARE; never let a lower rung pose as higher)
EQUAL_ACCESS (neither told form) / MODEL_FORM_ACCESS (form + reward levels + hazard hyperprior known,
  hazard value & g_t inferred online) / ORACLE_ACCESS (cell params/posterior given; upper bound only).
Candidate-StructuredPrior runs at DISCLOSED MODEL_FORM_ACCESS. claim_access_rung must equal
access_rung_candidate; mismatch → FAIL (see verdict).

## 4. candidate policy (FROZEN, callable) — Candidate-StructuredPrior
Joint belief b_t(g,h), g∈{1..K}, h∈H_grid={0.01,0.02,0.035,0.05,0.08,0.10,0.12,0.15}, prior uniform
over H_grid (spans train AND OOD ⇒ hazard inferred online, NOT misspecified). Reward levels
p_high=0.70,p_low=0.30 disclosed (MODEL_FORM_ACCESS). NEVER given cell hazard/g_t (that is ORACLE).
  L(o|g,i)=p_high if g==i else p_low (o=1); 1−that (o=0)
  M(b,i,o)[g,h] ∝ b[g,h]·L(o|g,i)                                  # measurement, per-h
  T(b)[g',h] = (1−h)·b[·,h]-marginal-at-g' + h·(1−b[g',h])/(K−1)   # transition per-h; h fixed within a component
     precisely: T(b)[g',h] = (1−h)·b[g',h] + h·(Σ_{g≠g'} b[g,h])/(K−1)
  U(b,i,o)=T(M(b,i,o))
  bg_t[g] = Σ_h b_t[g,h]                                           # g-marginal
  imm(b,i)=bg[i]·p_high+(1−bg[i])·p_low
  base    = p_low+(p_high−p_low)·max_j (Σ_h T(b)[j,h])
  future_i= Σ_{o∈{0,1}} P(o|b,i)·[ p_low+(p_high−p_low)·max_j (Σ_h U(b,i,o)[j,h]) ], P(1|b,i)=imm(b,i)
  KG_i=future_i−base ;  q_i=imm(b,i)+KG_i ;  a_t=argmax_i q_i (ties→lowest idx) ;  b_{t+1}=U(b_t,a_t,o_t)
  LOG-ONLY IG_i = H(bg_t) − Σ_o P(o|b,i)·H(g-marginal of M(b,i,o))   # entropy units; NEVER in q_i

## 5. mandatory baseline RL² (FROZEN)
C-MetaRecurrent: GRU hidden 128; input [one-hot last arm(10), last reward(1), norm t(1)]; A2C;
Adam lr 3e-4; entropy coef 0.01; discount 0.99. Compute ladder rungs=[50k,100k,200k] episodes,
max_rung=200k; only episode count varies across rungs. After each rung, eval F_train norm_regret;
use FIRST rung ≤0.15 for ALL F_OOD eval. No rung ≤0.15 → UNDERPOWERED_BASELINE. max_rung>cost cap at
calibration → COMPUTE_INFEASIBLE (no new rungs invented).

## 6. reference ceiling R* + metric (FROZEN, metric-safe)
R* = known-params (true h,gap) receding-horizon planner over b(g); belief-tree depth L; expand both
o∈{0,1}; leaf=greedy imm. L SELECTED AT CALIBRATION: precompute R*_L5,R*_L7 on calibration cells;
use L=7 iff |reward(R*_L7)−reward(R*_L5)|>0.005 on any calibration cell, else L=5; FREEZE L before
primary scoring. If any evaluated policy later exceeds chosen R* by >0.005 → METRIC_INVALID.
Metric: norm_regret(policy)=(reward(R*)−reward(policy))/(reward(R*)−reward(random)); denominator
computed ONCE per cell before candidate-vs-RL².
Weak controls (engineering-sufficient only): memoryless obs→action, random, majority, myopic_greedy,
lookup/NN.

## 7. statistics (FROZEN, callable)
Unit = RL² training seed s∈{1..20}. Each s: RL²_s and candidate evaluated on the SAME 2000 env
episode seeds (candidate deterministic given env seed + frozen priors). d_s=norm_regret(RL²_s)−
norm_regret(cand_probe); total_sep=mean_s d_s. CI = cluster bootstrap over the 20 seeds (10_000
resamples; episode-level resample nested in seed); [L,U]=95% percentile CI; half_width=(U−L)/2.
precision_adequate_X ≡ half_width_X ≤ 0.05  (renamed from "powered"; realized precision, no variance
guess). Computed for X∈{total_sep, probe_increment, and each destroy total_sep_X}.
win(Δ) ≡ lower95_CI(Δ) > 0.05 ;  equivalent(Δ) ≡ 95%CI(Δ) ⊆ [−0.05,+0.05] (TOST via same bootstrap).

## 8. ablations + destroyed() (FROZEN, callable)
Ablation policies: no_info_gain (a=argmax_i imm); random_probe (w.p.0.1 uniform arm else greedy imm);
frozen_belief (b_t≡b_1, U disabled); no_hazard_mix (T uses h=0 ∀ components; cannot re-expand).
For any policy X: total_sep_X = norm_regret(RL²) − norm_regret(X).
probe_increment  = norm_regret(cand at no_info_gain) − norm_regret(cand_probe)
belief_increment = norm_regret(cand at frozen_belief) − norm_regret(cand_probe)
probe_real ≡ win(probe_increment) ; belief_update_real ≡ win(belief_increment)
destroyed ≡ probe_real AND belief_update_real
           AND equivalent(total_sep_no_info_gain) AND equivalent(total_sep_random_probe)
           AND equivalent(total_sep_frozen_belief)
no_hazard_mix: DIAGNOSTIC. If NOT equivalent(total_sep_no_hazard_mix) → HAZARD_MIX_NOT_ISOLATED_FLAG
  and claim drops "exploits drift structure" (keeps "action-conditioned belief update"). Not blocking
  unless the operator upgrades it.

## 9. env admissibility (FROZEN, callable; BLOCKING pre-candidate)
reg_probe = known-params candidate policy; reg_passive = known-params GREEDY filter
  (a=argmax_i bg[i]; updates U; no KG); reward(·) = mean reward.
active_probe_abs = (reward(reg_probe) − reward(reg_passive)) / (reward(R*) − reward(random))
passive_closes  = (reward(reg_passive) − reward(random)) / (reward(reg_probe) − reward(random))
ADMISSIBLE iff active_probe_abs > 0.10 AND passive_closes ≤ 0.90. Else ENV_INADMISSIBLE.
K1 (single-obs): analytic Bayes decoder (a_t,r_t)→g_t over g,a~Uniform, r~frozen env.
  accuracy ≤ 0.35 → pass ; 0.35<acc≤0.50 → ENV_WEAK_K1_FLAG (not auto-pass) ; acc>0.50 → ENV_INADMISSIBLE.

## 10. cost calibration + reduction ladder (FROZEN)
Calibration: 1 training seed end-to-end; measure wall-time; project × full design. ≤3 CPU-hr AND
max_rung feasible → proceed. Else reduce IN ORDER, re-project after each: (1) drop F_OOD_SECONDARY;
(2) drop non-primary grid cells (KEEP primary); (3) drop weak controls except {random,myopic_greedy};
(4) cut eval episodes only while precision_adequate holds on pilot. FORBIDDEN reductions: primary cell,
20 seeds, MDE, band, adequacy 0.15, the four destroy ablations, max_rung. Still >3hr or not precise
after allowed reductions → UNDERPOWERED / COMPUTE_INFEASIBLE.

## 11. verdict callable (FROZEN; computed from committed rows)
cols: compute_infeasible, metric_invalid, env_admissible, access_rung_candidate, claim_access_rung,
  candidate_saw_F_OOD_params, RL2_first_adequate_rung, precision_adequate_total,
  precision_adequate_probe, precision_adequate_destroy, total_sep_CI, probe_increment_CI,
  destroyed, hazard_mix_flag, grid_cells.
def verdict(r):
  if compute_infeasible:                                              return COMPUTE_INFEASIBLE
  if metric_invalid:                                                  return METRIC_INVALID
  if not env_admissible:                                              return ENV_INADMISSIBLE
  if candidate_saw_F_OOD_params or (access_rung_candidate=='MODEL_FORM_ACCESS'
     and claim_access_rung=='EQUAL_ACCESS'):                          return UNDISCLOSED_ORACLE_OR_FORM_ACCESS_FAIL
  if RL2_first_adequate_rung is None:                                 return UNDERPOWERED_BASELINE
  if not precision_adequate_total:                                    return UNDERPOWERED
  if equivalent(total_sep):                                           return SATURATED_BASELINE_EQUIVALENCE
  if win(total_sep) and not (precision_adequate_probe and precision_adequate_destroy):
                                                                      return UNDERPOWERED_ABLATION
  if win(total_sep) and destroyed:                                    return PROCEED_NARROW   # + HAZARD_MIX_NOT_ISOLATED_FLAG if hazard_mix_flag
  if win(total_sep) and equivalent(probe_increment):                 return DISCLOSED_MODEL_FORM_PRIOR_WIN_PROBING_NULL
  if win(total_sep):                                                  return ABLATION_NON_DESTRUCTIVE
  return INCONCLUSIVE
# BUDGET_OR_SHIFT_ARTIFACT_FLAG (reported, never overrides):
#   TRUE iff total_sep point-est >0 in <2 of the 3 reported hazard grid cells {0.08,0.10,0.12}@gap0.40.

## 12. trace / replay (FROZEN)
Per step: t, b_t(g,h) summary, a_t, {q_i}, {KG_i}, {IG_i}(logged), predicted o, actual o_t, pred error,
b_{t+1}, θ_t=(g_t,h) ceiling-only (NOT fed to candidate), per-framework RNG seeding (np/torch/random).
RL² training: seed, data manifest, rung used. Replay reconstructs candidate b-trajectory from
(b_0,{a_t,o_t})+frozen U bit-exact; 2 fresh-process recomputes must match.

## 13. artifacts / stop / rollback / forbidden
Artifacts under artifacts/DRIFT-AXIS-CAPABILITY-ACBU-002A/: result.json (per-cell metrics, increments,
verdict, flags), trace.jsonl, baseline_comparison.json, ablation_report.json, admissibility_report.json,
precision_report.json (all CI half-widths), replay_report.json, claim_ceiling.txt, failure_manifest.json.
Stop on any terminal {COMPUTE_INFEASIBLE, METRIC_INVALID, ENV_INADMISSIBLE, *_FAIL, UNDERPOWERED*,
SATURATED, ABLATION_NON_DESTRUCTIVE}. Preserve failure artifacts; never patch. Isolated
src/drift_capability_acbu/. Forbidden: EGO mainline/LLM/AIRI/UI/emotion/proactive, global schema, any
prior artifact, credentials, pixel/physics env, StructuredInferred at STEP-0, changing any frozen value
after seeing scores, weakening RL²/MDE/band to move a verdict, broadening priors to rescue.
