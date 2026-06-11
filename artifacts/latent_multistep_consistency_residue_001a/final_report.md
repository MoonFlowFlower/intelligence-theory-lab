# LATENT-MULTISTEP-CONSISTENCY-RESIDUE-001A — Final Report

Card sha256 `661424d9…` · env prereg sha256 `e9ba27c2…` · Stage-0 anchor `6a7923b7` (2026-06-11T02:46:30Z, ls-remote verified) · first run postdates anchor · seeds 29/31/37/41/43.

## A. Executive verdict

```text
verdict = latent_residue_failed_shuffled_same_loss_collapse
candidate_R_pass = false
rollback = close_residue_as_order_or_replay_geometry_artifact
```

The residue did not survive. Beyond the headline verdict (predeclared priority: shuffled same-loss first), the evidence kills the residue on three independent axes — see F.

## B. Scope confirmation

Executed exactly as frozen: candidate R only; counterfactual replay absent; Candidate A not reopened; no Gate1 package claim; no same-agent bridge; no EGO paths touched; margins zero-advantage conjunctive, frozen and externally anchored before the first run; interpretation locks (original_order = candidate's own configuration; retrieval h>1 chaining) frozen pre-anchor.

## C. Parent result inheritance

Parent verdict gate1_preflight_failed_graph_cache_collapse; parent hashes recorded in task_manifest.json (final_report e4e47ae8…, result 5e9a28ec…, baseline c7db255f…). Parent artifacts read-only, unmodified.

## D. Environment preregistration

latent_alias_ring16_pomdp_v1: 16 latent states, 3 actions, 5 observations via fixed irregular labeling (verified non-lumpable for every action; memory required at 48/48 (o,a) cells); slip 0.10; heldout pairs {(0,0),(11,0),(5,1),(10,2)} excluded from training behavior, present in evaluation; 800-step phase-1 stream; 60×50 eval sequences per seed. Not lookup-trivial; controls not disabled (retrieval controls answer everything with predeclared fallbacks; parametric table/window controls fully competent — they in fact win).

## E. Slice redundancy report

Pre-run: R4 (w=3, unseen-window mask) fractions 0.419–0.453, inside validity band [0.05,0.95]; R5 horizon-4 targets diverge from horizon-1 on 100% of checked steps. Post-run recheck: same fractions; R4 ≠ R1 numerically for every system. slice_redundancy_check_pass = true. (The parent task's B4-saturation failure mode did not recur.)

## F. Candidate R result — failed on three independent axes

Min advantage over 5 seeds (nats; negative = control matches/beats R):

```text
axis 1 — order geometry (same multi-step loss):
  vs shuffled_same_loss_replay:   −0.0003…−0.0006 on all 5 slices
  vs reverse_order_same_loss:     −0.0008…−0.0015 on all 5 slices
  → chunk chronology contributes nothing; parent killer replicated in a new environment

axis 2 — the multi-step objective itself did not replicate:
  vs single_step_chunk_replay:    −0.003…−0.019 on all 5 slices (single-step now BEATS multi-step)
  vs equal_compute_extra_training: −0.003…−0.017 on all 5 slices
  → the parent's +0.004 multi-step advantage was environment-specific; here the
    k=4 consistency objective actively hurts relative to the same compute spent single-step

axis 3 — function-approximation collapse of the whole model class:
  vs equal_parameter_budget_model (order-2 window): −0.27 (R1–R3), −0.13 (R4), −0.04 (R5)
  vs stronger_sequence_model (interp order-1/2/3):  −0.21 (R1–R4)
  vs count_table (memoryless (o,a)→o' Laplace):     −0.21 (R1–R3), −0.06 (R4)
  → cheap parametric sequence models dominate the belief-model class in this setting
```

What R still beat (for completeness, not rescue): same_data_online_only (+0.11, R1–R4), larger_capacity learned-obs model (+0.17, R1–R4), and every cache/retrieval control by +2.38…+2.58 on R1–R4. R also edged count_table and the interp model on R5 only (+0.004, +0.002).

## G. Shuffled same-loss control result

Matched R on every seed and every slice (min advantage ≤ 0 everywhere; slightly positive for the control). First-class prior-killer control confirmed.

## H. Order control results

Shuffled, reverse, and fixed-random orders all match R on all 5 slices. Order geometry is irrelevant to this objective in this setting. matched multiset/compute/optimizer/seeds hold by construction.

## I. Generic replay control results

single_step_chunk_replay, generic_chunk_replay, random_replay, uniform_replay, equal_compute_extra_training all match R on all 5 slices. same_data_online_only matched on R5 only; frozen_theta matched on R5 only (the trained rollout is no better than an untrained one at horizon 4 under heldout-transition contamination — recorded honestly).

## J. Cache/retrieval control results

All six lost to R massively on R1–R4 (+2.38…+2.58 nats) and narrowly on R5 (+0.012). Retrieval does not explain R's behavior — but this cannot rescue R given axes 1–3.

## K. Strong function-approximation baseline results

equal_parameter_budget_model (1125-param order-2 window table) matched R on ALL slices and dominated by −0.27 nats on R1–R3 — the single strongest control in the battery. stronger_sequence_model matched on R1–R4. larger_capacity_single_step (belief + learned obs map) matched on R5 only. same_architecture_no_multistep ≡ single_step_chunk_replay (equivalence disclosed) matched everywhere.

## L. Graph/table control results

count_table / transition_table matched R on R1–R4 (memoryless table beats the belief tracker at h=1 in this environment); graph_lookup and compressed_map did not match (floor blowups / compression loss). Environment is not lookup-trivial (retrieval class lost), so table success is parametric-smoothing success, not lookup triviality.

## M. Runtime-access attestation

Candidate evaluated in isolated subprocesses (argv allowlist, opened-file inventory + sha256, forbidden objects loaded = reachable = 0; 5 attestation files). Controls evaluated in-process with their defining stores by design.

## N. Lineage reconstruction

Pass rate 1.0: phase-1 and post-replay candidate snapshots recomputed bit-exactly from seed + frozen records for all 5 seeds (np.array_equal); candidate R_slice_1 NLL reproduced < 1e-9; latent traces recomputable from raw chunks (the raw-chunk path used only in offline verification, never on the evaluation forward path). Ledger complete including the one aborted fa-group run (IndexError at an unused pre-scoring prediction call; fixed, failure preserved in ledger).

## O. Gate 0 interface audit

Only allowed variables (raw trace items, actions, observations, derived belief, theta, prediction error, chronology). No blocked variables exist in the module. Counterfactual action replay absent in every role. Pass.

## P. Anti-hardcoding audit

12/12 checks pass. Seeds rule-based and frozen; chunks/burn-in/depth frozen pre-anchor; margins never touched; no control sandbagging (the controls won — sandbagged controls do not win); environment favored controls if anything; ledger append-only.

## Q. Stop-condition report

Fired: collapse-type only (controls matched candidate). All hard stop conditions false. Evidence collection completed.

## R. Claim ceiling

Bounded local residue evidence only, in this preregistered setting under frozen margins. The result is a bounded NEGATIVE: the multi-step latent-consistency residue, as operationalized here, is closed.

## S. What this does not prove

It does not prove multi-step consistency objectives are useless in general (only that this operationalization, in this environment family, at this scale, loses to order-perturbed/same-loss, single-step, and window-model controls). It does not prove Gate1 passed or failed beyond the parent record; nothing about replay/consolidation necessity, retrieval superiority in general, same-agent continuity, Gate0→Gate1 bridging, EGO/companion readiness, agency, consciousness, functional subjects, or AGI. Statistical power: 5 seeds, one environment family.

## T. Rollback / next-action recommendation

Per the frozen rollback plan: `close_residue_as_order_or_replay_geometry_artifact` — and the evidence further supports closing it as a function-approximation artifact (axis 3) and an environment-specific artifact (axis 2). Recommended ledger entry for the research line: the parent task's surviving residue is now closed; the strongest live fact in this lab is negative and architectural — in both environments tested, cheap parametric predictors (count tables, window models) dominate the candidate belief-model class, and no replay variant produced effects beyond generic training. Any future task card should either (a) change the model class hypothesis itself, or (b) target a setting where structure transfer has a provable representational gap over window models — with the same control battery. This card authorizes neither; both require a new bounded task card and human sign-off.
