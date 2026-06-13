# GATE4-REPLACEMENT-BASELINE-BLOCKED-ROUTING-AND-REDESIGN-CRITERIA-001A

Verdict: `close_current_generated_gate4_task_family_partner_id_lookup_negative_evidence_001a`

## Source Boundary

- Branch: `codex/meta-theory-scaffold`
- Task starting boundary: `4fa338055ffd995ca7dad8242bcec174d56f5deb`
- No-candidate preflight tag: `remote-anchor-gate4-replacement-no-candidate-baseline-preflight-001a-4fa3380`
- Remote branch hash readback before this routing task: `4fa338055ffd995ca7dad8242bcec174d56f5deb`
- Local preflight tag hash: `4fa338055ffd995ca7dad8242bcec174d56f5deb`
- Remote preflight tag hash: `4fa338055ffd995ca7dad8242bcec174d56f5deb`
- Previous design boundary: `58ec364bd41104ca3b04129df8aa7fc7dd84f2cf`
- Previous design tag: `remote-anchor-gate4-replacement-task-falsification-design-001a-58ec364`

## Upstream Readback

The current no-candidate preflight result artifact reports:

- Verdict: `no_candidate_baseline_preflight_blocked_by_cheap_baseline_001a`
- Baselines declared/run: `22 / 22`
- Best faithful baseline: `partner_id_lookup_baseline`
- Score / threshold: `1.0 / 0.8`
- Candidate code created: `false`
- Candidate score produced: `false`
- Leakage positive controls detected: `true`
- Replay recomputation passed: `true`
- Replay corruption failed or changed as expected: `true`
- Provenance complete: `true`

## Current Layer

Engineering-governance / negative-evidence routing / redesign-criteria extraction only.

## Mainline Integration Status

Not mainline-integrated.

## Enabled Status

No EGO runtime capability is enabled. No new trigger path is authorized.

## Real Trigger Evidence

This routing record read existing artifacts only:

- `artifacts/gate4_replacement_no_candidate_baseline_preflight_001a/result.json`
- `artifacts/gate4_replacement_no_candidate_baseline_preflight_001a/baseline_results.json`
- `artifacts/gate4_replacement_no_candidate_baseline_preflight_001a/best_faithful_baseline.json`
- `artifacts/gate4_replacement_no_candidate_baseline_preflight_001a/no_candidate_code_scan.json`
- `artifacts/gate4_replacement_no_candidate_baseline_preflight_001a/leakage_positive_control_results.json`
- `artifacts/gate4_replacement_no_candidate_baseline_preflight_001a/replay_recomputation_results.json`
- `artifacts/gate4_replacement_no_candidate_baseline_preflight_001a/replay_corruption_results.json`
- `artifacts/gate4_replacement_no_candidate_baseline_preflight_001a/computed_evidence_provenance.json`

No baseline was rerun in this routing task.

## Problem Definition

The no-candidate baseline preflight reached a decisive negative result: `partner_id_lookup_baseline` scored `1.0` against the predeclared invalidation threshold `0.8`. The generated replacement Gate4 task family is therefore identity-solvable before any candidate exists. It cannot be patched into a pass or used as positive mechanism evidence.

## Negative-Evidence Inheritance

This routing record inherits three boundaries:

1. Prior invalid-self-report preservation:
   - Invalid target commit: `78889b69b75baa424e89332558bda798685e9634`
   - Preserved findings: `invalid_self_report`, `negative_evidence_baseline_equivalence`, `audit_blocked_requires_repair`

2. Replacement falsification design:
   - Design boundary: `58ec364bd41104ca3b04129df8aa7fc7dd84f2cf`
   - Principle: cheap baselines run before candidate.
   - Principle: if a cheap faithful baseline reaches threshold, the task family is invalid.
   - Principle: do not weaken baselines or revise thresholds after results.

3. No-candidate baseline preflight:
   - Boundary: `4fa338055ffd995ca7dad8242bcec174d56f5deb`
   - Verdict: `no_candidate_baseline_preflight_blocked_by_cheap_baseline_001a`
   - Best faithful baseline: `partner_id_lookup_baseline`
   - Score / threshold: `1.0 / 0.8`
   - Candidate code and candidate score: absent.

## Baseline-Block Summary

`partner_id_lookup_baseline` used a serialized state with `strategy=partner_id_lookup`, `field=partner_id`, and this direct map:

- `partner_alpha -> support`
- `partner_beta -> challenge`
- `partner_gamma -> defer`
- `partner_delta -> summarize`

The baseline provenance artifact records:

- Producer function: `partner_id_lookup_baseline`
- Run ID: `gate4_replacement_no_candidate_baseline_preflight_001a_534c618e9e363e9a`
- Seeds: `4101`, `4102`
- Aggregation rule: `mean exact-match accuracy over heldout episodes`
- Code path hash: `e14935689a9be5c8f8df96a8c25afda2fb2a99f64164bb93b1004034dfc91556`

Other threshold-reaching shortcuts included preference table, retrieval, imitation frequency, order-k history, oracle-shaped rule, full-bundle decoder, n-gram trace lookup, pair-count frequency, graph/cache family, and query-capable imitation.

## Shortcut Cause Analysis

Partner identity was directly exposed. The target collapsed onto stable partner identity and anonymized partner key. The heldout split did not break identity lookup; it was known-partner interpolation. The context split preserved the same partner mapping. Counterfactual pairs did not make partner identity non-decisive: the partner-ID baseline still solved all heldout episodes.

Primary shortcut family: stable partner identity / partner-key lookup.

Unresolved shortcut families:

- Preference-table reconstruction
- Retrieval over prior traces
- Order-k partner history
- Full-bundle partner decoding
- Pair-count and graph-cache lookup
- Query-conditioned imitation

## Strongest Objection

The wrong repair is to treat `partner_id_lookup_baseline = 1.0` as a small field-removal bug. Removing `partner_id` and rerunning would not address partner key, context ID, row order, preference table, query key, trace structure, filename, serialized state, retrieval surface, or graph/cache lookup. A valid future route must change the evidence target.

## Selected Route

Route A: close current generated task family.

Required verdict:

`close_current_generated_gate4_task_family_partner_id_lookup_negative_evidence_001a`

## Rejected Routes

- Route B rejected: the required artifacts were readable and consistent enough for this routing decision.
- Route C rejected as primary route: this task extracts criteria, but does not itself authorize or create a separate redesign card.
- Route D rejected: additional routing value exists because this record explicitly closes the generated family and rejects same-family patching.
- Repair and rerun rejected: forbidden by the task card and unsupported by the negative evidence.

## Redesign Criteria

Any future Gate4 replacement attempt must satisfy these constraints before implementation:

1. Partner identity must be nuisance, not answer key.
2. Identity permutation test is mandatory.
3. Unseen-partner split is mandatory for cross-partner transfer claims.
4. Unseen-context split is mandatory.
5. Same-ID/different-latent counterfactual pairs are mandatory.
6. Different-ID/same-latent counterfactual pairs are mandatory.
7. Preference-table shortcut must be broken.
8. Retrieval shortcut must be broken.
9. Order-k history shortcut must be broken.
10. Generator-proxy decoding must be blocked.
11. Intervention feedback must be necessary.
12. Transfer phase must be necessary.
13. Baseline-first execution remains mandatory.
14. Positive-control leakage remains mandatory.
15. Replay recomputation remains mandatory.
16. Thresholds must be locked before results.
17. Best faithful baseline must be the primary contrast.

These are constraints, not implementation authorization.

## Anti-Zeno Check

This task adds discriminative value by closing an identity-solvable generated family and preventing unnecessary candidate work. Another governance task is not justified unless it changes the evidence target. The route should close this task family; a future stronger design card may be considered only as a separate user-authorized task.

## Stop Conditions

No stop condition was triggered for this routing task. The negative-evidence stop condition from the upstream preflight remains active:

`cheap_baseline_reached_threshold:partner_id_lookup_baseline`

## Rollback Plan

If unauthorized files are modified, stop, list exact paths, restore unauthorized changes before commit if safe, preserve blocker evidence if meaningful, and do not patch old artifacts or continue into redesign implementation or candidate work.

If required artifacts later prove inconsistent, preserve the inconsistency as blocker evidence and do not infer missing values from memory or handoff text.

## Final Verdict

`close_current_generated_gate4_task_family_partner_id_lookup_negative_evidence_001a`

## Claim Ceiling

This report may claim only that the current generated Gate4 replacement task family is closed by cheap-baseline negative evidence, that the partner-ID lookup baseline result was preserved and routed, that redesign criteria were extracted, and that no candidate/runtime/bridge/admission/Gate5/EGO-mainline work was performed.

## What This Proves

This proves that the current generated task family is not acceptable as positive mechanism evidence or candidate-admission target because it was solved by a cheap partner-ID lookup baseline in the no-candidate preflight.

## What This Does Not Prove

This does not prove Gate4 validity, replacement Gate4 success, mechanism validity, social understanding, social-causal-transfer success, agency, subjectivity, consciousness, emotion, autonomy, stable user benefit, EGO readiness, runtime readiness, bridge readiness, admission readiness, or companion readiness.

It also does not prove that every future Gate4 replacement will fail.

## Next Minimal Action

Do not repair or rerun this generated task family. Close it as partner-ID lookup negative evidence. A future task may create a separate stronger design card only if explicitly authorized and only with partner identity as nuisance rather than answer key.
