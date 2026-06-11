# GATE1-REPLAY-CONSOLIDATION-EXEC-TASKCARD-001 — Final Bounded Verdict Report

Task card sha256 `5118f2a0edf2ead7917757cb465a41678c10431cb0b1887db70517fbbfde205d` · margin hash `f21b82489d824bdd2473ac9150bc85e7ee0fa444b6e6484621aed177c489b0e8` · Stage 0 anchor `d011e735` (2026-06-11T01:24:48Z) · amendment anchor `d0d0fa75` (2026-06-11T01:44:40Z) · first run 2026-06-11T01:45:17Z.

## A. Executive verdict

```text
package_verdict = gate1_preflight_failed_graph_cache_collapse
candidate_A_verdict = collapsed_or_not_distinguishable_in_this_setting
candidate_B_verdict = collapsed_or_not_distinguishable_in_this_setting (single-control margin failure; see D)
```

Under the frozen conservative zero-advantage rule (strict all-seed all-slice dominance, conjunctive over all mandatory controls), neither candidate passed. All evidence, including failures, is preserved.

## B. Scope confirmation

Executed exactly as frozen: candidates A (primary) and B (secondary); counterfactual action replay absent in every role; both control stacks first-class (8 graph/cache + 10 generic replay + 5 memory-object for A; 5 cache/retrieval + 5 generic for B); margins predeclared and externally anchored before the first run; one human-approved pre-run amendment (ENV-PREREG-AMENDMENT-001, observation-map repair after the lumpability failure F1; margins/seeds/slices/controls/hyperparameters untouched; zero runs existed at amendment time).

## C. Candidate A result — full collapse

Matched (min advantage over 5 seeds ≤ 0) by all 23 controls on at least one required slice. Decisive numbers (min advantage, nats):

```text
vs count_table (Laplace):  A1 -1.281  A2 -1.663  A3 -1.185   (count table dominates everywhere)
vs uniform_replay:         A1 -0.013  A2 -0.211  A3 -0.041   (replay-buffer near-equivalence)
vs equal_compute:          A1 -0.012  A2 -0.399  A3 +0.008   (equal compute explains the effect)
vs online_only:            A1 +0.216  A2 -1.663  A3 +0.086   (transfer adds something, but nothing controls don't match)
```

Bounded interpretation: in this setting, the tightened fast-to-slow transfer event is behaviorally a generic replay-buffer training pass, and a smoothed count-table lookup outperforms the entire slow-model class including on held-out pairs (the compositional model produced worse-than-uniform predictions on unseen (s,a)). Source deletion did not destroy the (small) effect (A3 vs online_only remains positive) — the collapse is baseline equivalence, not source dependence.

## D. Candidate B result — near-pass, single-control order collapse

Distinguishable (min advantage > 0 on every seed and every slice) from 9 of 10 controls, including:

```text
vs all 5 cache/retrieval controls:  ≥ +3.16 nats on every slice (caches useless on fresh sequences)
vs online_only_B:                   ≥ +0.103
vs chunk_replay_ss (single-step):   ≥ +0.0039  (multi-step consistency objective adds uniform value)
vs random_replay_B:                 ≥ +0.0015
vs equal_compute_B:                 ≥ +0.0012
```

Matched by exactly one mandatory control: `shuffled_replay_B` (same multi-step loss, shuffled chunk order; min advantage −0.0003). Chronological chunk order contributes nothing — order ablations agree (shuffle/reverse ≈ −0.0002 to −0.0003, i.e. marginally better). Frozen rule verdict: replay-buffer collapse on the order dimension. Bounded positive residue: the multi-step latent-consistency objective itself (vs single-step, random, equal-compute) survived every comparison; chunk chronology did not.

## E. Graph/cache control results

count_table dominates candidate A globally. Unsmoothed lookups (graph_lookup, episodic traversal, etc.) lose on slices where their zero-probability successors meet the stochastic kernel, demonstrating the controls were exercised at full power, not sandbagged. Competence floor: pure-lookup sanity task exact success = true.

## F. Generic replay control results

uniform/salience/chunk/random/shuffled replay all match candidate A (≈0 differences — structural near-equivalence). For B, only shuffled order matches. Competence floor: replay training NLL 2.481 → 1.278 (nonzero reduction) = true.

## G. Control competence — both checks passed (validity prerequisite satisfied).

## H. Runtime-access attestation

Candidate evaluations ran in isolated subprocesses; argv allowlist = [snapshot.npz, queries.json, out.json]; opened-file inventory + sha256 inside each of the 40 attestation files; forbidden objects loaded = 0, reachable = 0. Mount cannot unlink files, so deletion is enforced as runtime absence by process construction (disclosed in source_deletion_log.json); lineage snapshots persist as required.

## I. Source deletion timing

Evidential arm preregistered and executed: deletion after transfer, before evaluation, slow-only eval. Deletion timestamps per seed in source_deletion_log.json. Effect did not vanish on deletion (no source_dependent_collapse); collapse came from baselines.

## J. Lineage reconstruction

Pass rate 1.0. Candidate A slice-1 NLL recomputed from seed + frozen records matches recorded values (<1e-9); stream hashes match; bit-exact recomputation of candidate A transfer and candidate B replay from frozen snapshots + raw chunks (np.array_equal) — all 5 seeds.

## K. Gate 0 interface audit

Only allowed variables used (raw trace items, actions, observations, belief state, theta, prediction error, pseudo-counts). No reward/value/goal/preference/affect/user-model/semantic-memory variables exist anywhere in the harness. Counterfactual contrast: absent entirely.

## L. Anti-hardcoding audit

17/17 checks pass (anti_hardcoding_audit.json). One violation candidate occurred and is documented: F1 lumpable observation map, caught pre-run by closed-form analysis, preserved in failure_manifest.json, repaired only with explicit human approval and a new external anchor. Ledger contains one append-only correction (a smoke-test entry was recorded before pytest actually executed; invalidated, then re-run honestly).

## M. Margin-freeze and external-time-anchor report

Margins frozen inside the card (zero-advantage, conjunctive); margin hash anchored in commit d011e735, pushed and verified via anonymous ls-remote at 01:24:48Z; amendment re-anchored at d0d0fa75 (01:44:40Z); first run 01:45:17Z. Ordering margin_freeze < amendment_anchor < first_run holds. No margin changed at any point.

## N. Environment preregistration report

ring12_structured_stochastic_v1 + amendment-001 observation map (sha256 51d68344…). Not lookup-trivial (heldout pairs, fresh eval sequences); controls not disabled (count_table in fact dominates candidate A — strong evidence the setting favored controls, not the candidate). Disclosed redundancy: after repair, the B4 mask saturates (1700/1700), so B_slice_4 ≡ B_slice_1 in this environment.

## O. Stop-condition report

Fired (collapse-type, terminating candidate claims, not evidence collection): graph_cache_control_matches…, generic_replay_control_matches…. Not fired: all access/lineage/margin/hardcoding/competence stop conditions.

## P. Claim ceiling statement

Bounded Gate 1 preflight evidence only, in this preregistered setting under the frozen margin policy. A "distinguishable" result means only not_matched_by_listed_controls_under_predeclared_rule_in_this_setting.

## Q. What this does not prove

It does not prove fast-to-slow transfer is useless in general, nor that latent-dynamics replay works; it does not prove replay/consolidation is necessary or unnecessary; it does not prove predictive superiority over retrieval (the opposite direction — count-table dominance — holds only in this tiny tabular setting); it proves nothing about consciousness, subjective experience, emotion, self-awareness, agency, functional subjects, electronic life, AGI, companion readiness, or EGO readiness; it does not validate Bio-CMBC, CVPSM, VCCO, CMBC, or R/G; the control list is not exhaustive; statistical power is limited (5 seeds, one environment family).

## R. Rollback / next-action recommendation

Per the card's rollback rules: candidate A → replay-buffer/graph-cache collapse recorded; candidate B → order-dimension replay-buffer collapse with a surviving multi-step-consistency residue. Recommended next bounded step (requires a NEW task card; not authorized here): a narrower Phase-4-scope hypothesis isolating the multi-step latent-consistency objective (B's surviving residue) against stronger function-approximation baselines and a larger environment where count-table dominance is not structural. Alternatively rollback_to_phase4_scope_edit to drop candidate A's current operationalization.
