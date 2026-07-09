# FACG-TUPLE-001A - Independent Hostile Audit Report

Gate: FORK-A-COLLAPSE-GATE-001A-R3 (FACG); gate_spec + body @ commit 671d552b25c1e9ab85b8a1bffaf91f32c3773af0.
Object under test: tuple_spec.md (Embodied Generated-Access Boundary Maintenance).
Claimant: operator. Auditor: Claude (independent; roles separated). Mode: analysis-only, paper, no run, no callable, no STEP-B, no evidence produced by the gate itself.

## Verdict
CLOSED. Primary = ANALYTIC_CLOSED_BY_CLOSER (paper only). Bank color = Yellow (negative/closure). NOT anchored as a canonical "first gate-fire" boundary unless the operator explicitly elects that (which would be Red).
- Survival path: S-1 NOT_ESTABLISHED; S-2 not invoked.
- Closers fired: K-A5, K-A2, K-A6. Claim cap only: K-A1a.
- K-A1b resource-matched domination: NOT proven (analytic baseline-coverage only).
- Predicted-if-run (not established): FORK_A_SHADOW_DOMINATED / CAPABILITY_NOT_SUBJECT / MECHANISM_FAMILY_REPLICATION.
This is a FAIR kill (grounded in named baselines + a cited reduction + the tuple's own R contract), not a definitional kill.

## 1. Admissibility and the S-1 status (corrected, anti-over-kill)
Six-tuple fully instantiated -> no ADMIN_CLOSED. The survive path requires S-1 (generated-access / no-closing-reference contract).

Correction (tightened, to avoid re-importing the definitional kill that FACG-R3 already removed): it is NOT the case that "R alone refutes S-1." FACG's generated-access fairness protocol REQUIRES M and every baseline to share the same R (environment law, seed distribution, intervention/memory/compute budget, J|V) and requires each B_i to generate its own access path rather than replay M's. Shared R is the fairness precondition, not an automatic failure condition; reading it as auto-fail would make every fair generated-access tuple fail definitionally - exactly the over-kill R1/R3 were hardened against.

Correct finding: the tuple's G+R combination supplies no no-closing-reference structure beyond a fixed shared law / fixed J|V / fixed simulator. The claimant's S-1 hook is "perturbation distribution depends on the agent's generated niche," but future-observation-depends-on-history holds in any MDP with persistent state; if that sufficed, S-1 would be vacuous (the body states "Stationarity is NOT the criterion" and hardens against exactly this). The load-bearing question is whether the LAW/measure generating access is itself agent-generated in a non-amortizable way, or fixed-and-given. Here it is fixed and shared, and every B_i generates its own niche under the same law. The S-1 burden is therefore unmet: S-1 NOT_ESTABLISHED. The tuple falls back to the closers.

## 2. K-A1a - claim cap only (not domination)
The world is reproducible as a simulator -> an ideal Bayes-optimal-for-J reference is definable -> K-A1a fires and CAPS the claim at capability, blocking subject/mechanism overclaim. Per the frozen split, K-A1a does NOT by itself establish a resource-matched shadow (K-A1b). K-A1a is recorded as claim-cap only; it is NOT the closure mechanism.

## 3. K-A2 - amortizability / capability relabel (centerpiece); component decomposition
With S-1 unestablished we are in the fixed-prior embodied meta-MDP regime. M decomposes; each component lies within the span of a fair equal-R baseline:
- U1 (action-conditioned controllability estimate P(var responds | intervention, context)) = the c1 / CDAP Row-2 interventional-prediction functional. SUPPORTING reduction (conjecture grade; CSSP-001A not banked): an equal-access Bayes-optimal-for-c1 shadow dominates the prediction kernel. Closes the PREDICTION component ONLY, not all of C.
- U3 (viability-weighted repair/action selection) with J|V fixed-and-given = optimal control against a fixed objective = exactly what B4 (world-model + planner) and B1 (RL2) optimize under the same law and resources. Control component covered.
- U2/U4 (boundary-state update + cross-episode replay) = representation/reuse covered by B5 (episodic graph-cache) and B3 (history transformer + persistent memory).
- C3 (future-access preservation) = empowerment / option-value objective, expressible by B4/B1/B8 under equal R; if scored against a fixed "reachable-channels" target it re-imposes a fixed reference (K-A3 -> K-A1).
No component carries subject-separating content beyond the fair baseline family.

## 4. Best case is still not a subject foothold (decisive point)
Suppose, counterfactually, B4/B1 fail to match and M empirically wins. Then M is essentially model-based RL with an EXPLICIT boundary/controllability readout, so the "necessity" is that explicit representation = an ARCHITECTURE choice. K-A2 explicitly excludes architecture/efficiency wins from subject separation ("non-transferable mechanism necessity rather than architecture/efficiency"). Any such win routes to MECHANISM_FAMILY_REPLICATION or CAPABILITY_NOT_SUBJECT (-> fork B). Hence the tuple has NO path to a subject foothold even in its best case - matching the gate's honest prior and the K-A2 dichotomy on a concrete construction.

## 5. Remaining closers
- K-A4 (self-play): any population variant falls to B2/B6; no rescue.
- K-A5 (embodiment): embodiment changes the access tuple, not identifiability; fixed-prior embodied MDP has an ideal reference; escape only via S-1 (unestablished).
- K-A6 (cross-episode memory): fixed-prior accumulation is amortized -> B3/B5 coverage.
- K-A3 (measurement): advantage-over-B is legitimate, but any real win here reduces to sample-efficiency -> CAPABILITY_NOT_SUBJECT.

## 6. Fairness self-check (guard against auditor over-kill)
- Baseline family B1-B9 present and instantiated; B7 U-disabled control present; B8/B9 resource-bounded (not ideal Solomonoff / no-regret) -> does not trigger UNDERDEFINED_BASELINE_SET.
- U-boundary pre-registered in mechanistic terms (U1-U4), with U-disabled ablations and pre-declared strong U-non-equivalent baselines (B4 without explicit readout; B3 history-memory) -> satisfies the R3 Patch-D anti-tautology form.
Therefore the tuple is NOT closed by U_BOUNDARY_OVERBROAD or any definitional kill. It is closed substantively by S-1 non-establishment + K-A2 amortizability/relabel + K-A6 coverage. Positive value: the gate fires correctly and fairly on a format-compliant, seriously-constructed tuple and closes it - evidence the gate is non-empty, fireable, and falsifiable.

## 7. What this does NOT claim
- NOT META_AMORTIZED_COLLAPSE as a proven empirical domination: K-A1a ideal-object existence alone does not prove K-A1b resource-matched domination; the closure is analytic coverage + relabel, not a run or a formal domination proof.
- NOT fork-A global impossibility: only this one construction, under its own R, collapses.
- No mechanism evidence, no subject/consciousness/electronic-life evidence, no STEP-B authorization.
- The U1->c1 reduction is conjecture-grade (CSSP-001A not banked) and covers the U1 component only.

## 8. Falsifier (keeps the gate falsifiable)
A tuple that escapes this closure needs a world whose LAW or OBJECTIVE is itself agent-generated in a non-amortizable way (a genuine S-1): J|V or the access law NOT "fixed before results, independent of M's path." That property is exactly excluded by this tuple's R. Per the body, such S-1 worlds have UNKNOWN viability and are necessary-not-sufficient and near-contradictory (the structure must be exploitable-by-M yet not equal-resource-amortizable). Reopening requires a NEW tuple changing G/R accordingly, plus a direct answer to the "exploitable yet non-amortizable" tension.

## 9. Governance / banking
- Bank color: Yellow (negative/closure carrying a result). No threshold, no positive mechanism claim -> not Red. Do NOT anchor as a canonical boundary unless the operator explicitly elects it.
- Token discipline: verdict.json uses ONLY frozen FACG-001A-R3 taxonomy tokens for verdict/closer/survival; descriptive labels are glosses, not new taxonomy (anti schema-fragmentation).
- Frozen sources: docs/codex/tasks/FACG-001A-R3.md and artifacts/FACG-001A/gate_spec.json + artifacts/FACG-001A/claim_ceiling.txt are read-only rule sources; this audit does not modify them.
- Artifact narrowing: paper-only audit; run-based artifacts (trace / baseline_comparison / ablation_report / replay_report) are N/A. verdict.json is the result artifact. Fabricating run artifacts would violate the anti-hardcoding rule; their absence is correct and documented.
