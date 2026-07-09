# CDAP-001A-R1 — STEP-A FAMILY TABLE: ROW-LEVEL COLLAPSE CERTIFICATES

Status: DESIGN/ANALYSIS, docs-only. Independent Red-audit verdict = CONDITIONAL CLEAR for
docs-only bank / route input over named families (Patch A + Patch B integrated below;
provenance resolution performed at bank). Designer ≠ self-CLEAR. NO STEP-B, NO agent run,
NO mechanism/subject/agency claim. Awaits Claude Yellow post-check.

Template per row: family / score object / τ_eval / A-notes / s*_C /
  certificate(type + proof-or-cite) / oracle vars / fork-A dependency / residual falsifier / verdict
Certificate types: [PROOF] Bayes / proper-scoring / identifiability computation ·
  [REDUCTION+CITE] reduces to another row or a prior closed artifact ·
  [ROUTING] out-of-contract, not a collapse proof.
PROVENANCE RULE (bank gate): every [cite: …] must be resolved to a repo artifact path + commit
  anchor before bank; any cite not resolvable in-repo ⇒ tag that certificate [CONJECTURE —
  provenance unresolved]. A memory-only citation MUST NOT be banked as provenance.

## R1 bank provenance resolution

Resolved in-repo cite anchors:

- ACBU-002A closeout:
  `docs/research/DRIFT-AXIS-CAPABILITY-ACBU-002A-CLOSEOUT-001A.md@28d2ead306b1895e5b03ae91aac6824dfcf62ca0`
  and design card
  `docs/codex/tasks/DRIFT-AXIS-CAPABILITY-ACBU-002A.md@28d2ead306b1895e5b03ae91aac6824dfcf62ca0`.
- Grounding-gate K1/K2:
  `docs/research/GROUNDING-GATE-K1-K2-PREFLIGHT-FEASIBILITY-001A.md@15489ee07ad52640bde6e7b7f23d5bcbd189abdb`
  and closeout
  `docs/research/GROUNDING-GATE-SELF-STATE-ROUTE-NEGATIVE-EVIDENCE-CLOSEOUT-001A.md@15489ee07ad52640bde6e7b7f23d5bcbd189abdb`.
- Self-boundary killer catalog K1–K7:
  `docs/research/SELF-BOUNDARY-INTERVENABLE-LATENT-NEGATIVE-LINEAGE-AND-KILLER-CATALOG-001A.md@15489ee07ad52640bde6e7b7f23d5bcbd189abdb`.
- Gate4 cross-family-social invalid_self_report:
  `docs/research/CLAUDE-INDEPENDENT-AUDIT-IMPLEMENT-FUTURE-GATE4-CROSS-FAMILY-SOCIAL-CAUSAL-TRANSFER-001A.md@23aa206cf6400f59443327ea1091113f310d9013`
  and
  `artifacts/preserve_claude_independent_audit_implement_future_gate4_001a_invalid_self_report_restore_worktree_001a/invalid_self_report_classification.json@23aa206cf6400f59443327ea1091113f310d9013`.
- RESIDUE-001A:
  `docs/LATENT-MULTISTEP-CONSISTENCY-RESIDUE-001A.md@6a7923b7d3fc8616e54255140ae56d77adc01e31`
  and
  `artifacts/latent_multistep_consistency_residue_001a/result.json@d35bd2387a70b47b6d0ae8076316e1329af85b3c`.
- Identifiability-ceiling / cross-episode fair-meta-baseline route context:
  `docs/codex/tasks/N1-ADMIT-IDENTIFIABILITY-001.md@cbd8a2efbedc0811e42cdf93c9dae368a3a9e48f`
  and
  `docs/research/FSP-STAGE-LEDGER.md@af53720f6fffb5cbacc22f5df8b684b3102467d3`.

Unresolved in-repo cite anchors:

- `CSSP-001A` was not resolved to an in-repo artifact path by the bank search. Rows whose original
  certificate depends on `CSSP-001A` are explicitly tagged
  `[CONJECTURE — provenance unresolved]`. This is a provenance downgrade, not a memory-only cite.

────────────────────────────────────────────────────────────────────────
ROW 1 — TASK-COMPETITION / SCORE
- score object: aggregate task return/accuracy on a held-out task set from a fixed, finite,
  learnable task family, > threshold.
- τ_eval: (task instance, agent actions, outcomes, cumulative reward) — reward is visible.
- A-notes: shared samples from the task family; same compute/H/Π.
- s*_C: the amortized Bayes-optimal policy for the task distribution (RL²/large-model amortizer
  computed/trained to the family's optimal action map).
- certificate: [REDUCTION+CITE] task reward is a functional of τ_eval; the Bayes-optimal policy
  maximizes E[reward|A]; no equal-access agent exceeds it. Matched-coverage + adequate baseline ⇒
  candidate ≲ R_ref ≈ Broad amortizer. [cite:
  docs/research/DRIFT-AXIS-CAPABILITY-ACBU-002A-CLOSEOUT-001A.md@28d2ead306b1895e5b03ae91aac6824dfcf62ca0]
- oracle vars: none.
- fork-A dependency: none if stationary; if the family is open-ended/non-stationary → ROW 9.
- residual falsifier: a stationary learnable family where a candidate reproducibly beats the
  max-feasible amortizer at equal compute/data AND a non-memorization ablation survives. Prior: none.
- VERDICT: SHADOW_DOMINATED.

────────────────────────────────────────────────────────────────────────
ROW 2 — INTERVENTIONAL PREDICTION (CSSP c1)
- score object: accuracy of predicted P(Y|do(X=x)) on a held-out do-query set vs true
  interventional outcomes, > threshold.
- τ_eval: (observational data, training interventions+outcomes, held-out do-queries, agent predictions).
- A-notes: shared observational+training-interventional D_train, SCM hypothesis class H, prior Π,
  query grammar. Held-out outcomes are SCORER-ONLY, never fed to agent or shadow (leakage guard).
- s*_C: Bayes posterior-predictive decision rule = per-query argmax over
  ∫ P(Y|do(x),h) dP(h|D_train); COMPUTED by enumerating E(D_train).
- certificate: [CONJECTURE — provenance unresolved] (original type PROOF) enumerate
  E(D_train)={SCMs in H consistent with equal-access data}. Held-out q:
  P_h(q) invariant across E ⇒ s*_C computes it ⇒ passes ⇒ SHADOW_COLLAPSE; not invariant
  (Markov-equivalence-limited) ⇒ no equal-access learner determines it ⇒ CAND fails, only
  structure-handed POS passes ⇒ INDUCTIVE_BIAS_ONLY. [cite: CSSP-001A c1 analytic closure —
  unresolved in repo at bank]
- oracle vars: none (held-out outcomes scorer-only).
- fork-A dependency: none.
- residual falsifier: held-out do-query set where CAND-LEARNED passes at equal access while the
  COMPUTED s*_C fails AND independent re-audit confirms s*_C truly Bayes-optimal + access symmetric
  ⇒ POTENTIAL_ADMISSIBLE. Prior: unreachable (would imply s*_C not optimal).
- VERDICT: SHADOW_DOMINATED (SHADOW_COLLAPSE | INDUCTIVE_BIAS_ONLY by identifiability).

────────────────────────────────────────────────────────────────────────
ROW 3 — COUNTERFACTUAL (Pearl rung-3)
- score object: accuracy of counterfactual predictions Y_x | (X=x', Y=y') on held-out CF queries.
- τ_eval: row-2 trace + factual observations to condition on.
- A-notes: rung-3 needs the STRUCTURAL FORM (equations + exogenous-noise distribution), not just the
  interventional distribution. If H/Π are made strong enough to identify CFs, the shadow gets the
  same H/Π (equal access). Env true-SCM generates the scored counterfactual (scorer-only).
- s*_C: Bayes posterior predictive over counterfactuals = marginalize over posterior on full SCMs
  (structural functions + noise) consistent with D_train.
- certificate: [PROOF] counterfactuals are GENERICALLY (not universally) non-identifiable from
  interventional (let alone observational) data WITHOUT functional-form assumptions in H ⇒ the
  identifiable region SHRINKS vs ROW 2. Identifiable side ⇒ s*_C passes ⇒ COLLAPSE; larger non-id
  side ⇒ only full-SCM-handed POS passes ⇒ INDUCTIVE_BIAS_ONLY. Strictly worse for a foothold than ROW 2.
- oracle vars: the scored "true counterfactual" is env-true-SCM output (scorer-only, like ROW 2);
  becomes ORACLE_SCORED iff the true structural functions are fed to the AGENT to score.
- fork-A dependency: none.
- residual falsifier: same shape as ROW 2, over a smaller region. Prior: unreachable.
- VERDICT: SHADOW_DOMINATED (COLLAPSE | INDUCTIVE_BIAS_ONLY), non-id region larger than ROW 2.

────────────────────────────────────────────────────────────────────────
ROW 4 — CALIBRATION / "KNOWS-WHAT-IT-DOESN'T-KNOW"
- score object: strictly proper scoring rule (log-loss / Brier) on the agent's reported predictive
  distribution q over outcomes, INCLUDING correctly widening on non-identifiable queries.
- τ_eval: (queries, realized outcomes, agent's reported distributions q).
- A-notes: shared D_train, H, Π.
- s*_C: report the equal-access Bayes posterior predictive q*(·)=P(outcome|query,D_train,A).
- certificate: [PROOF] a strictly proper scoring rule's Bayes-expected value (under shared prior+data)
  is uniquely maximized by reporting the posterior predictive (the Bayes act). Among equal-access
  reporters the best achievable conditional IS q*; s*_C reports exactly q*. CRUCIAL: "correctly saying
  I don't know" = widening on non-identifiable queries = PRECISELY what q* does. The metacognition-
  looking property is the shadow's default behavior.
  Scope: shared prior + strictly proper score + Bayes expectation ONLY. Pointwise fixed-world
  calibration or a non-proper score requires re-audit.
- oracle vars: none.
- fork-A dependency: none.
- residual falsifier: an equal-access agent with strictly better Bayes-expected proper score than
  computed q* — impossible under shared prior (violates propriety); if observed ⇒ prior mismatch
  (INDUCTIVE_BIAS_ONLY) or leakage. Prior: unreachable.
- VERDICT: SHADOW_DOMINATED.

────────────────────────────────────────────────────────────────────────
ROW 5 — BELIEF-UPDATE / ACTION-CONDITIONED LATENT
- score object: correct action-conditioned belief update. Two scoring modes (decisive):
  (i) OBSERVABLE consequence — predictive accuracy of the belief-conditioned output;
  (ii) MATCH the agent's internal belief to the "true" latent.
- τ_eval: (observations, actions, agent's belief-conditioned predictions/outputs).
- A-notes: shared.
- s*_C: the Bayes filter — posterior over latent given history P(state|history,A) and its predictive.
- certificate: [PROOF for (i) / REDUCTION for (ii)] (i) belief scored on observable consequence ⇒
  Bayes filter dominates over τ_eval (same optimality as ROWS 2/4) ⇒ SHADOW_DOMINATED. (ii) scoring the
  internal belief vs true latent requires the true latent ⇒ ROW 7 (ORACLE). Self-state/belief grounding
  is non-identifiable — an obs-decoder / co-binding shadow reproduces the same behaviour+intervention
  evidence. [cite:
  docs/research/GROUNDING-GATE-K1-K2-PREFLIGHT-FEASIBILITY-001A.md@15489ee07ad52640bde6e7b7f23d5bcbd189abdb;
  docs/research/GROUNDING-GATE-SELF-STATE-ROUTE-NEGATIVE-EVIDENCE-CLOSEOUT-001A.md@15489ee07ad52640bde6e7b7f23d5bcbd189abdb]
- oracle vars: present ONLY under scoring mode (ii).
- fork-A dependency: none in bounded/stationary (mode ii's non-identifiability is intrinsic).
- residual falsifier: equal-access agent whose action-conditioned belief yields strictly better
  OBSERVABLE predictive score than the Bayes filter — impossible in expectation; vs true latent = oracle.
- VERDICT: SHADOW_DOMINATED (mode i) | ORACLE_SCORED (mode ii).

────────────────────────────────────────────────────────────────────────
ROW 6 — SELF / NON-SELF BOUNDARY   [PATCH A: score-object split]
- score object (by sub-mode):
   (a1) PREDICTION: predict which variables respond to the agent's own interventions.
   (a2) MAINTENANCE POLICY (bounded stationary): actively select interventions / regulate future
        observability to MAINTAIN the boundary, scored by a policy return/loss.
   (a3) ACTIVELY-CONSTRUCTED / EMBODIED (non-stationary): boundary built & rewritten over time.
   (b)  LABEL: match a "true" self/non-self label.
- τ_eval: (observations, agent interventions, outcomes, boundary-dependent behavior/reports).
- s*_C: (a1) the ROW-2 interventional-response predictor; (a2) the Bayes-optimal-for-C equal-access
  boundary-maintenance POLICY/transducer over the full τ_eval and C loss (ROW-1 policy-domination).
- certificate: [REDUCTION+CITE]
   (a1) ⇒ collapses into ROW 2 ⇒ SHADOW_DOMINATED where identifiable.
   (a2) ⇒ Bayes-optimal-for-C policy dominates every equal-access policy on C's own loss ⇒
        SHADOW_DOMINATED (ROW-1 policy-saturation structure). Closes the "I score maintenance, not
        prediction" escape. [cite:
        docs/research/DRIFT-AXIS-CAPABILITY-ACBU-002A-CLOSEOUT-001A.md@28d2ead306b1895e5b03ae91aac6824dfcf62ca0]
   (a3) ⇒ OUT_OF_BOUNDED_CONTRACT_ROUTE_TO_FORK_A (subject to ROW 9's meta-MDP caveat).
   (b)  ⇒ ROW 7 (oracle). Killer catalog K1 obs-decodability + K2 interventional saturation.
        [cite:
        docs/research/SELF-BOUNDARY-INTERVENABLE-LATENT-NEGATIVE-LINEAGE-AND-KILLER-CATALOG-001A.md@15489ee07ad52640bde6e7b7f23d5bcbd189abdb]
- oracle vars: mode (b) only.
- fork-A dependency: mode (a3) only.
- residual falsifier: a bounded stationary (a1/a2) C a candidate passes while the Bayes-optimal-for-C
  predictor (a1) / policy (a2) fails, no oracle label ⇒ POTENTIAL_ADMISSIBLE. Prior: collapses | oracle.
- VERDICT: SHADOW_DOMINATED (a1, a2) | ORACLE_SCORED (b) | ROUTE_TO_FORK_A (a3).

────────────────────────────────────────────────────────────────────────
ROW 7 — INTERNAL SELF-REPORT vs TRUTH
- score object: match between the agent's self-report (its causal graph / belief / "self") and the
  ground-truth internal structure/latent.
- τ_eval: (agent self-report) + the TRUE structure used by the scorer.
- A-notes: the scorer consumes the ground truth, which is NOT in A.
- s*_C: N/A — the criterion is not equal-access; scoring requires the answer.
- certificate: [REDUCTION+CITE] ORACLE by construction (truth is a scorer input). Worse, tautological:
  a candidate GENERATIVELY DEFINED to emit the label scores 1.0, and a same-access faithful baseline
  ties = parity violation. [cite:
  docs/research/CLAUDE-INDEPENDENT-AUDIT-IMPLEMENT-FUTURE-GATE4-CROSS-FAMILY-SOCIAL-CAUSAL-TRANSFER-001A.md@23aa206cf6400f59443327ea1091113f310d9013;
  artifacts/preserve_claude_independent_audit_implement_future_gate4_001a_invalid_self_report_restore_worktree_001a/invalid_self_report_classification.json@23aa206cf6400f59443327ea1091113f310d9013]
- oracle vars: YES — the ground-truth structure/latent (definitional).
- fork-A dependency: none — oracle-ness does not dissolve in fork A.
- residual falsifier: score self-report WITHOUT truth-access (via downstream behavioral consequence
  only) — but then it IS ROW 5/6 (behavioral), which collapses. No escape as stated.
- VERDICT: ORACLE_SCORED (inadmissible).

────────────────────────────────────────────────────────────────────────
ROW 8 — TRACE / SIGNATURE MATCH
- score object: similarity of the agent's emitted trace/signature (internal-state reports, "thinking"
  pattern) to a genuine-subject reference (POS-HANDED).
- τ_eval: (agent trace, reference trace/signature used for scoring).
- A-notes: shared; the reference trace is the target.
- s*_C: a trace-mimic transducer fit to reproduce the reference trace/signature from equal-access inputs.
- certificate: [CONJECTURE — provenance unresolved] (original type REDUCTION+CITE) passive
  trace/signature matching CANNOT separate a mechanism from its imitator BY DEFINITION (only
  interventions / held-out novelty / ablation break behavioural shadow-equivalence). A trace-mimic
  fit to the reference passes ⇒ TRACE_MIMIC_COLLAPSE; the criterion is renderer/behavioural, not
  mechanistic. [cite: CSSP-001A killer catalog trace-mimic — unresolved in repo at bank; RESIDUE
  window-model dominance resolved at
  docs/LATENT-MULTISTEP-CONSISTENCY-RESIDUE-001A.md@6a7923b7d3fc8616e54255140ae56d77adc01e31 and
  artifacts/latent_multistep_consistency_residue_001a/result.json@d35bd2387a70b47b6d0ae8076316e1329af85b3c]
- oracle vars: leakage iff the mimic sees the reference's HELD-OUT trace; even without, it's a
  sequence baseline that collapses.
- fork-A dependency: none.
- residual falsifier: a trace predicate NO equal-access mimic can reproduce yet a genuine mechanism
  satisfies — but any purely trace-defined predicate is imitable by construction; the only way out
  makes the predicate depend on held-out INTERVENTIONS ⇒ that IS ROW 2, not a trace criterion.
- VERDICT: SHADOW_DOMINATED.

────────────────────────────────────────────────────────────────────────
ROW 9 — CROSS-EPISODE / OPEN-ENDED / EMBODIED   [PATCH B: no absolute "no shadow exists"]
- score object: cumulative adaptation advantage over a generative / agent-coupled process.
- τ_eval: whole agent-path-dependent interaction history.
- A-notes: the agent's path generates/rewrites the access; there is NO pre-frozen, enumerable,
  same-access posterior object under the CURRENT bounded offline contract.
- s*_C: NOT well-defined under the CURRENT bounded offline access tuple. CAVEAT (do not over-exempt
  fork A): if the fork-A world is itself pre-frozen as a finite / meta-MDP with a FIXED prior /
  horizon / compute / objective, a Bayes-optimal meta-policy EXISTS and DOMINATES — the wall reappears
  at the meta-level (this is the ACBU death mechanism; RL²/meta-learners amortize it). The bounded
  theorem is escaped ONLY when NO fixed prior closes the generative process (genuine open-endedness);
  an existent-but-intractable meta-optimum is SPECIFICATION_GAP, not a foothold.
- certificate: [ROUTING — not a collapse proof, not admission] fork A must DEFINE and beat its OWN
  strongest baselines: open-ended meta-learner, self-play/POET generator, history-conditioned
  transformer + persistent memory, world-model + curriculum search, graph/cache/replay episodic
  traversal, multi-agent co-adaptation. [cite:
  docs/codex/tasks/N1-ADMIT-IDENTIFIABILITY-001.md@cbd8a2efbedc0811e42cdf93c9dae368a3a9e48f;
  docs/research/FSP-STAGE-LEDGER.md@af53720f6fffb5cbacc22f5df8b684b3102467d3]
- oracle vars / fork-A dependency: this IS the fork-A row.
- residual falsifier / promotion: a fork-A C beaten by a candidate while ALL fork-A baselines fail,
  with a PATCH-5 paired-contract transform proving (i) it is not a C-redefinition and (ii) the fork-A
  world is NOT reducible to a fixed-prior meta-MDP, no oracle/leakage. Prior: UNKNOWN; necessary-not-
  sufficient; the live region is NARROW — only generative processes with no fixed closing prior.
- VERDICT: OUT_OF_BOUNDED_CONTRACT_ROUTE_TO_FORK_A.

────────────────────────────────────────────────────────────────────────
TABLE-LEVEL VERDICT (over named families only)
- 8/9 families (ROWS 1–8) ⇒ SHADOW_DOMINATED or ORACLE_SCORED.
- 1/9 (ROW 9) ⇒ OUT_OF_BOUNDED_CONTRACT_ROUTE_TO_FORK_A — out of contract, necessary-not-sufficient,
  NOT admissible.
- ⇒ CLOSED_OVER_NAMED_FAMILIES. No ADMISSIBLE_BOUNDED_TARGET among named families.
- NOT a universal closure (any new C enters via the same admission schema + a fresh certificate).
- Provenance caveat: Rows 2 and 8 carry `[CONJECTURE — provenance unresolved]` tags because the
  original `CSSP-001A` cite was not resolvable to an in-repo path at bank.

Structural note (honest headline): ROWS 1–8 all reduce to "the Bayes-optimal-for-C shadow s*_C over
τ_eval dominates every equal-access learner," differing only in which s*_C and whether an oracle
enters. ROW 9 is the sole row that escapes the theorem — into fork A (a routing verdict), NOT into
admission, and only in the narrow genuinely-open-ended sub-region.

CLAIM CEILING — what this does NOT prove: global impossibility of the goal; that fork A separates or
succeeds; any mechanism / functional-subject / agency / subjectivity / consciousness evidence; and it
authorizes NO STEP-B agent run. Designer ≠ self-CLEAR; independent Red-audit = CONDITIONAL CLEAR
pending provenance resolution at bank.
