# DRIFT-AXIS-CAPABILITY-ACBU-002A   (FINAL monolith design card; supersedes 001A design + banked prereg)
Status: DESIGN CARD (Red). Designer self-red-team supersession. Pairs with -STEP-0-PREREG-002A (single
source of all frozen numbers + callables; this card MUST NOT restate them). Awaits INDEPENDENT Red-audit
of the banked pair before Phase-2. Codex sole writer. NO self-CLEAR.

## supersession chain (keep both)
1. 001A STEP-0 ideal-gap REJECTED (definitional): in a POMDP the history-conditioned recurrent
   meta-policy ≡ belief-state optimal policy under unbounded resources; online-ideal − amortized-ideal
   ≡ 0 (always SATURATED); memoryless amortized = strawman.
2. 001A banked prereg (50c6ca82) SUPERSEDED pre-run: HAZARD_COVERAGE_ASYMMETRY — the candidate hazard
   prior support included the primary eval hazard while C-MetaRecurrent trained on a strictly narrower
   hazard set (001A values; corrected matched-coverage config in PREREG §2); a win was unattributable
   among {structured probing | broader coverage | RL² extrapolating unsupported hazard} =
   HIGH_SCORE_NO_ATTRIBUTION.

## layer / claim ceiling
learning-adaptation / mechanism-hypothesis benchmark design. Ceiling: disclosed-structure,
resource-bounded, family-bounded OFFLINE evidence for active action-conditioned belief-update
sample-efficiency vs amortized recurrent meta-learning AT MATCHED hazard coverage, under the
trace/replay contract. Explicitly NOT: equal-access mechanism, OOD/extrapolation generalization,
functional subject, agency, autonomy, subjectivity, consciousness, EGO/companion readiness.

## real objective (REVISED by the coverage fix)
The coverage fix changes the tested quantity: from "explicit structure generalizes to OOD drift" (the
riggable 001A framing) to "at MATCHED hazard coverage and matched finite budget, is explicit online
action-conditioned Bayesian belief-update more sample-efficient than an adequately-trained amortized
recurrent meta-learner, with the advantage isolated by info-gain/belief ablations?"

## reconstructed question (burden of proof)
Not "does it adapt?" but: does Candidate-StructuredPrior beat C-MetaRecurrent-BROAD (train hazard =
candidate prior support) by >MDE on the matched-support in-distribution primary cell, with the
advantage destroyed by info-gain/belief ablation, and NOT reproducible by the coverage confound
(beating only the NARROW baseline)? Beating Narrow-but-not-Broad = the 001A false positive, now caught.

## honest prior = likely SATURATED (state up front)
On a fully-specified finite learnable family, Bayes-optimal is learnable; an adequacy-gated amortized
learner approximates it. At matched coverage both target the same optimum ⇒ expected
SATURATED_BASELINE_EQUIVALENCE. The only escapes are (a) inadequate RL² budget (gated away by the
adequacy requirement) or (b) true extrapolation beyond support — but for a Bayesian, extrapolation
ability = a broad prior = the coverage/inductive-bias advantage itself, which is NOT equal-access
mechanism and would re-import the confound. THEREFORE: do NOT redesign toward "extrapolation" to
manufacture headroom. Run 002A as a cheap decisive kill-test expecting SATURATED; a PROCEED would
require explicit structure to beat a max-feasible-trained amortizer at equal coverage — a high bar.
After the audit-R2 B4 fix (max-feasible baseline rung + adequacy bar = MDE), the bar is near-absolute:
since R_ref = the known-params version of the same candidate policy, candidate ≲ R_ref ≈ a max-feasible
adequate Broad, so sep_broad is structurally pinned within ~MDE. The only PROCEED window is the thin
myopic-exploration edge where candidate > R_ref (flagged by R_REF_EXCEEDED_FLAG). Honest prior is now
near-certain SATURATED_BASELINE_EQUIVALENCE or UNDERPOWERED_BASELINE — weigh this against running.

## mechanism object / controls (design; full callables in PREREG-002A)
S=latent (g_t,h) restless changepoint bandit; O=(a_t,r_t) partial; A=arm choice (exploit/probe);
M=candidate posterior b_t(g,h); U=action-conditioned Bayesian filter+one-step KG (no free β); J=raw reward.
Controls: C-MetaRecurrent-BROAD = PRIMARY comparator (train hazard = candidate prior support, PREREG §2);
C-MetaRecurrent-NARROW = DIAGNOSTIC ONLY (narrower diagnostic hazard set per PREREG §2; measures
coverage_confound; MAY NOT establish PROCEED); R_ref = known-params §4-candidate (one-step KG) LOGGED
reference per PREREG §5 (NOT a metric denominator, NOT a proven ceiling); weak controls
(memoryless/random/majority/myopic/lookup) = engineering-sufficient only. Access = DISCLOSED
MODEL_FORM_ACCESS (hazard prior now coverage-matched to Broad; reward levels disclosed but same-family
in-distribution).

## primary framing (matched-support, NOT OOD)
Primary cell = F_MATCHED_SUPPORT_PRIMARY (primary hazard value ∈ H_grid ∈ Broad training, value in
PREREG §2; in-distribution for BOTH; NOT held-out, NOT hazard-OOD). Reported grid (PREREG §2) likewise
in-support. Any true extrapolation lives only in F_EXTRAPOLATION_SECONDARY (diagnostic; never in the
primary verdict).

## metric (RAW; full callable in PREREG §6)
Primary verdict metric = RAW mean reward/step difference (candidate vs BROAD); no normalization, no
ceiling denominator (audit-R1 fix). R_ref logged for context only. MDE/BAND frozen in PREREG §6.

## frozen signature (summary; callable in prereg)
S1 control separation vs BROAD; S2 tracking curve; S3 (demoted) held-in-support consistency across grid
cells; S4 info-gain/belief ablations destroy the advantage; S5 non-memorization. PROCEED_NARROW needs
S1(vs Broad)+S4 + probe/belief increments real + admissibility + precision.

## verdict terminals (semantics; callable in prereg)
COMPUTE_INFEASIBLE, METRIC_INVALID, ENV_INADMISSIBLE(+ENV_WEAK_K1_FLAG), UNDISCLOSED_ORACLE_OR_FORM_
ACCESS_FAIL, UNDERPOWERED_BASELINE, UNDERPOWERED, UNDERPOWERED_ABLATION,
HAZARD_COVERAGE_CONFOUND_SATURATED_UNDER_MATCHED_COVERAGE (beats Narrow, Broad saturates — the clean
002A result: 001A would false-positive, matched comparator kills it), SATURATED_BASELINE_EQUIVALENCE,
HAZARD_COVERAGE_CONFOUND (beats Narrow, Broad inconclusive), PROCEED_NARROW (beats Broad + destroyed;
from BROAD ONLY, never Narrow), DISCLOSED_MODEL_FORM_PRIOR_WIN_PROBING_NULL, ABLATION_NON_DESTRUCTIVE,
INCONCLUSIVE. no_hazard_mix = diagnostic (HAZARD_MIX_NOT_ISOLATED_FLAG downgrades claim wording).

## stop / rollback / files / forbidden
Stop on any non-PROCEED terminal; preserve failure artifacts; never patch. Rollback = revert run
commit(s); 001A + this pair preserved (no-delete). Files: this card + PREREG-002A (Phase-1 docs-only);
src/drift_capability_acbu/ + artifacts/DRIFT-AXIS-CAPABILITY-ACBU-002A/ (Phase-2). Forbidden:
EGO/LLM/AIRI/UI/emotion/proactive, global schema, any prior artifact, credentials, pixel/physics,
StructuredInferred at STEP-0, using Narrow to establish PROCEED, using a weaker-than-max-feasible baseline
rung, calling the primary cell OOD, changing any frozen value post-score, weakening Broad/MDE/BAND or the
adequacy=MDE bar to move a verdict, chasing extrapolation to manufacture headroom.

## sequencing / role
Phase-1: Codex banks THIS card + PREREG-002A (docs-only, supersede-in-place, no-delete of PREREG-001A).
Independent Red-audit of the banked pair. Phase-2 (run) only after CLEAR. Designer does NOT self-CLEAR.
