# BASELINE-IMMUNITY-ADMISSION-STANDARD-001A

Layer: route-governance / evidence-governance documentation only.

Claim ceiling: this is a reusable normative admission standard. It is not mechanism
evidence. It does not prove any Gate, surface, mechanism, autonomy, agency,
consciousness, emotion, stable user benefit, or EGO/runtime readiness. It only
codifies which surfaces are admissible for candidate preflight and which are blocked
on the basis of already-recorded negative evidence in this lab.

## 0. Scope and non-goals

This standard exists because the lab has repeatedly spent candidate-design effort on
surfaces that were never separable from a trivial or fair baseline. It converts that
recorded negative evidence into pre-candidate admission gates so future Gate / surface
preflight tasks fail fast.

In scope:

- A reusable checklist + verdict set that any future preflight task card must satisfy
  before a candidate may be authored.
- A companion static machine-readable registry,
  `BASELINE-IMMUNITY-ADMISSION-STANDARD-001A.registry.json`, that future Codex preflight
  cards may consume directly.

Explicitly out of scope (hard boundaries):

- This standard does NOT design a new Route C surface.
- This standard does NOT authorize candidate implementation.
- This standard ships NO executable enforcement harness. The registry is data, not a
  checker. A future executor must be authorized by its own task card; an unaudited
  "N tests passed" checker is itself a known false-green failure mode and is forbidden
  here.

## 1. Grounding convention (how to read every clause)

Each normative clause is grounded in a recorded failure family, not in abstract best
practice and not in a frozen commit. Read every clause as:

```text
normative_rule    = the failure family it forbids (portable; always applies)
grounding         = ledger / artifact pointer (where the evidence lives)
observed_at_commit = metadata only; NOT a dependency for future applicability
```

A clause stays in force even if the cited commit, artifact path, or decision-log entry
is later relocated. The commit hash records *where it was first observed*, never *when
the rule expires*. If a pointer is moved, update the pointer; do not weaken the rule.

## 2. Metric-degeneracy checklist

A surface metric is inadmissible if any degenerate predictor below can reach the
admission ceiling (`ceiling - equivalence_band`). For each item the preflight must run
the listed control and record its score in the baseline panel.

### 2.1 predict_all
- Failure family: recall-only / coverage-only metric allows full-set prediction to saturate.
- Blocking rule: any metric where predicting the entire candidate set reaches the oracle/ceiling is inadmissible.
- Prior evidence: candidate-free Route C separation probe — reported oracle-vs-fair "separation" was a false positive; `predict_all` recall = 1.0 = oracle, fair panel omitted it.
- Ledger pointer: `docs/decision_log.md` (Route C candidate-free separation probe rejection) + `artifacts/claude_independent_candidate_free_route_c_baseline_separation_probe_001a_hostile_audit_rejection_001a/`.
- Observed HEAD: `b45598b` — metadata only.
- Verdict on trigger: `rejected_metric_degenerate`.

### 2.2 predict_none
- Failure family: specificity/abstention-only metric is maximized by the empty prediction (common when the truth set is mostly negative).
- Blocking rule: any metric where the empty prediction reaches ceiling is inadmissible.
- Prior evidence: dual of 2.1; same probe rejection — degenerate predictors must be on both ends of the size axis.
- Ledger pointer: `docs/decision_log.md` (Route C separation probe rejection) + same artifact as 2.1.
- Observed HEAD: `b45598b` — metadata only.
- Verdict on trigger: `rejected_metric_degenerate`.

### 2.3 constant-k sweep
- Failure family: a fixed-size constant prediction (size k, content fixed) saturates across the distribution.
- Blocking rule: sweep k over `[0 .. |set|]`; if any constant-k predictor reaches ceiling, the metric is inadmissible.
- Prior evidence: generalization of predict_all/predict_none; required because saturating size may be interior, not just the extremes.
- Ledger pointer: `docs/decision_log.md` (Route C separation probe rejection) + `artifacts/candidate_free_route_c_baseline_separation_probe_001a/`.
- Observed HEAD: `b45598b` — metadata only.
- Verdict on trigger: `rejected_metric_degenerate`.

### 2.4 threshold sweep
- Failure family: a post-hoc score threshold with no mechanism reaches ceiling, or thresholds/clips are tuned after seeing results.
- Blocking rule: include a post-hoc threshold-optimizer baseline that sweeps thresholds on a held-out split; if any non-mechanism threshold hits ceiling, the metric is inadmissible. Thresholds may not be selected after observing candidate scores.
- Prior evidence: GATE4-PREFLIGHT-001B — ablation "clip" forged degradation and metric was a tautology; threshold/post-hoc tuning recurred.
- Ledger pointer: `docs/decision_log.md` + GATE4 preflight audit artifacts.
- Observed HEAD: `90dc4b9` — metadata only.
- Verdict on trigger: `rejected_metric_degenerate`.

### 2.5 random
- Failure family: a random predictor at matched output statistics already lands inside the ceiling band — the metric carries no fair signal to discriminate.
- Blocking rule: run a random baseline matched on marginal/size; if random ≈ ceiling (within band), there is no separable signal.
- Prior evidence: weak-distribution failures across the saturation lineage; random-band proximity is the canonical "no signal" tell.
- Ledger pointer: `docs/decision_log.md` + `docs/codex/contracts/DISTRIBUTION-HEADROOM-PREFLIGHT-CONTRACT-001A.md`.
- Observed HEAD: `98be7f4` — metadata only.
- Verdict on trigger: `rejected_no_fair_signal`.

### 2.6 size exploit
- Failure family: the metric is monotone in prediction-set size toward ceiling independent of correctness (recall rewards large sets; specificity rewards empty sets).
- Blocking rule: vary set size only, holding content policy fixed; the score must not climb to ceiling as a function of size alone.
- Prior evidence: Route C separation probe — recall had no size/precision penalty, so larger sets trivially won.
- Ledger pointer: `docs/decision_log.md` (Route C separation probe rejection) + artifact as 2.1.
- Observed HEAD: `b45598b` — metadata only.
- Verdict on trigger: `rejected_metric_degenerate`.

### 2.7 precision/recall imbalance
- Failure family: reporting recall alone (or precision alone) without the complementary penalty lets a degenerate predictor saturate.
- Blocking rule: a single-sided metric is inadmissible. Use a balanced/cost-weighted metric (e.g., F-beta with stated beta, or an explicit cost model) OR report precision and recall jointly with predict_all/predict_none controls visible.
- Prior evidence: Route C separation probe — "pure recall, no precision penalty" was the decisive degeneracy that manufactured the false positive.
- Ledger pointer: `docs/decision_log.md` (Route C separation probe rejection) + artifact as 2.1.
- Observed HEAD: `b45598b` — metadata only.
- Verdict on trigger: `rejected_metric_degenerate`.

## 3. Information-structure checklist

These test whether the task carries fair, non-trivial signal at all. They are about the
data-generating structure, independent of any candidate.

### 3.1 visible-target independence test
- Failure family: the target is a (near-)deterministic function of the visible/passive channel, so a same-access fair baseline matches any candidate.
- Blocking rule: estimate decodability of the target from visible-only features; if a legal same-access baseline reaches ceiling, the target is visibly determined and the surface carries no candidate-exclusive signal.
- Prior evidence: GATE4-CROSS-FAMILY-SOCIAL-001A — same-access faithful baseline tied candidate at 1.0 (access-parity violation).
- Ledger pointer: `docs/decision_log.md` + `artifacts/implement_future_gate4_cross_family_social_causal_transfer_001a/`.
- Observed HEAD: `78889b6` — metadata only.
- Verdict on trigger: `rejected_no_fair_signal` (or `rejected_trivially_decodable` if decodable from a single field; see 3.2).

### 3.2 direct decodability test
- Failure family: the hidden answer/self-set is directly decodable from passive field *values*, not just from names.
- Blocking rule: run a value-level attacker family over the passive channel — at minimum {mean, variance, correlation, PCA, cross-episode, supervised, membership} — and gate on `family_max`. If any legal attacker reaches ceiling-band above chance, the set is self-decodable.
- Prior evidence: Route C preflight — a value-level observation-decodable self-set leak in passive `handle_values` let a legal mean-attacker score 1.0; the earlier name-only baseline missed it.
- Ledger pointer: `docs/decision_log.md` (Route C preflight hostile audit blocker) + `artifacts/route_c_preflight_001a/`.
- Observed HEAD: `726f26d` (blocker) / `278819a` (repair) — metadata only.
- Verdict on trigger: `rejected_trivially_decodable`.

### 3.3 partial-inferability requirement
- Failure family: either the target is fully identifiable from passive observation (no residual for a mechanism to reduce) or it has zero residual structure (nothing to infer).
- Blocking rule: the surface must demonstrate genuine residual uncertainty under the passive channel AND that the proposed mechanism class (e.g., interventional) can in principle reduce it. Non-identifiability must be shown (e.g., a twin-pair indistinguishable under passive `P(X)` but separable under `do(.)`), with an oracle that actually estimates the non-read quantity (so a non-reading oracle scores 0 and the check is fail-able).
- Prior evidence: Route C non-identifiability premise — only randomized `do` identifies the latent; a passive-only attacker cannot. The premise band (0.12) was held fixed across commits (no post-hoc tuning).
- Ledger pointer: `docs/decision_log.md` (Route C repaired preflight re-audit) + `artifacts/route_c_preflight_001a/`.
- Observed HEAD: `278819a` — metadata only.
- Verdict on trigger: `rejected_no_fair_signal` if fully passive-identifiable; `rejected_trivially_decodable` if zero residual.

### 3.4 leakage channels
- Failure family: the label leaks through a side channel — observation names, action names, filenames, fixture names, artifact structure, `baseline_hint`, planted answer-maps, value-level fields, or label ordering.
- Blocking rule: enumerate every leakage channel and attach a fail-able positive control to each (a control that is verified to flip to blocked when the leak is injected). Name-only scanners are insufficient; value-level and structural channels must be covered. Positive controls that scan a hardcoded dict and are structurally always-true are forbidden.
- Prior evidence: (a) GATE4-REPLACEMENT-001B — `baseline_hint = target + 1`; a `hint_inverter` scored 1.0. (b) `ONE-GATE-FUTURE-ONLY` harness — the answer key rode in `policy_map`/`signal` under non-listed names; the leakage scanner's positive control was structurally always true.
- Ledger pointer: `docs/decision_log.md` + `docs/NEGATIVE_EVIDENCE_LEDGER.md` (cb95bbd entry) + `artifacts/gate4_replacement_discriminative_social_latent_001b/`.
- Observed HEAD: `ec11f88` (baseline_hint) / `cb95bbd` (name-list bypass) — metadata only.
- Verdict on trigger: `rejected_trivially_decodable`.

### 3.5 generator coupling requirement
- Failure family: the candidate authors (or can influence) the ground truth, or truth seeds overlap train/validation, so the harness is circular.
- Blocking rule: the data generator must be specified and candidate-inaccessible. The candidate must not write any field that determines ground truth. Truth/test seeds must be disjoint from any train/val/drift seeds, and disjointness must be recorded and asserted.
- Prior evidence: (a) `ONE-GATE-FUTURE-ONLY` harness — candidate-authored `policy_map` controlled ground truth; self-endorsing map → 1.0/admitted, flipped → blocked (non-circularity failure). (b) ACOLB-001A — drift_val seeds (2001–3) held disjoint from ood_test (5001–3) to keep the comparison leakage-free.
- Ledger pointer: `docs/NEGATIVE_EVIDENCE_LEDGER.md` (cb95bbd) + `docs/decision_log.md` (ACOLB-A closure) + `artifacts/one_gate_future_only_non_circular_harness_001a/`, `artifacts/acolb_001a/`.
- Observed HEAD: `cb95bbd` / `bb65008c` — metadata only.
- Verdict on trigger: `blocked_pending_canonical_readback` if generator provenance cannot be verified; otherwise `rejected_no_fair_signal`.

## 4. Oracle taxonomy

An oracle is an upper-bound estimator used to argue that a surface has headroom. Not all
oracles can justify re-promoting a route to candidate design.

### 4.1 answer-key oracle
- Definition: reads the planted answer/label (or any candidate-inaccessible truth) directly.
- Establishes: only that the task is solvable *with illegal access*. It does NOT establish that any fair, legal channel carries signal.
- Re-promotion: CANNOT support route re-promotion. An answer-key-only oracle gap is a stop condition (§6).
- Prior evidence: Route C preflight — `obs_only_baseline` read planted answer-maps / fell back to handle position; this was the underpowered-baseline blocker.
- Ledger pointer: `docs/decision_log.md` (Route C preflight blocker) + `artifacts/route_c_preflight_001a/`. Observed HEAD `726f26d` — metadata only.

### 4.2 budget-faithful visible-channel oracle
- Definition: the best achievable using ONLY the legal/visible channel and the same action/query budget a fair candidate would have — no extra queries, no answer key.
- Establishes: a legitimate upper bound on fair-channel headroom.
- Re-promotion: CAN support re-promotion, but only if (a) it is verified budget-faithful, (b) it is strictly separated from the strongest fair baseline by at least the equivalence band, and (c) it is not reducible to a degenerate predictor from §2 (predict_all / predict_none / constant-k excluded from the fair panel's max).
- Prior evidence: candidate-free Route C probe — the missing `predict_all` member and non-budget-faithful framing turned a budget oracle into a false positive; the fix requires the full-budget degenerate controls inside the panel.
- Ledger pointer: `docs/decision_log.md` (Route C separation probe rejection) + artifact as 2.1. Observed HEAD `b45598b` — metadata only.

### 4.3 mechanism oracle
- Definition: an oracle that presupposes the very mechanism it is meant to validate (e.g., the metric is generated by the candidate's own rule, so the candidate scores 1.0 by construction).
- Establishes: nothing — it is circular.
- Re-promotion: CANNOT support anything.
- Prior evidence: GATE4-CROSS-FAMILY-SOCIAL-001A — candidate score 1.0 was tautological (`== label generative`); EGO EAV self-declared-digest bypass is the same circularity in verifier form.
- Ledger pointer: `docs/decision_log.md` + `artifacts/implement_future_gate4_cross_family_social_causal_transfer_001a/`. Observed HEAD `78889b6` — metadata only.

Re-promotion rule (normative): a route may be re-promoted to candidate preflight only on
the strength of a budget-faithful visible-channel oracle (4.2) that clears the strongest
fair baseline by ≥ band and is not degenerate. Answer-key (4.1) and mechanism (4.3)
oracles never support re-promotion.

## 5. Required baseline registry

Every applicable class below must appear in the preflight panel. The candidate must beat
the strongest fair member of every applicable class by ≥ equivalence band. If any fair
member ties the candidate at ceiling, the verdict is `rejected_baseline_saturated` and
must not be relabeled with softer language.

- trivial predictors — predict_all, predict_none, constant-k sweep, random, majority. (§2)
- passive baselines — observation-only; visible-channel value decoders {mean, variance, correlation, PCA}; nearest-neighbor lookup over passive features. (§3.2)
- active / query baselines — exhaustive legal query; greedy / uncertainty query under the same budget. Grounding: ACP-BV / Route C — `exhaustive_legal_query` was code-identical to the candidate (delta 0).
- graph-cache challengers — MANDATORY whenever any representational or environment claim is made. Minimum six-member family: `graph_lookup`, `transition_table`, `successor_map`, `count_table`, `fsm_planner`, `episodic_traversal`. Grounding: Gate1 EXEC-001 `graph_cache_collapse`; Route C final — six graph-cache members all reached 1.0; CLOSED_FAMILIES (`pair_count_table`, `full_bundle_decoder`, `serialized_state_decoder`, `belief_table`, `ngram_trace_lookup`).
- lookup imitation — trace-only replay; n-gram trace lookup; full-bundle decoder; serialized-state decoder; belief table; pair-count table.
- direct objective optimizer — a solver (e.g., discounted WLS / least-squares / convex) that directly optimizes the surface objective without the proposed mechanism. Grounding: ACOLB-A — candidate was structurally equivalent to a discounted weighted least-squares fit.
- amortized learner — a learner trained on the same legal channel. It must actually fit (record `ml_library_used = true` and a real fit); a deterministic stub labeled "learned" is forbidden. Grounding: ACSB-001B — the "learned" baseline was fully deterministic (`ml_library_used = False`, no fit), invalidating the comparison.
- task-specific classical baselines — the strongest known closed-form / classical method for the surface's task type.

Grounding ledger pointers: `docs/decision_log.md` (ACOLB-A closure `bb65008c`; ACP-BV 001B closure `98be7f4`), `docs/CLOSED_FAMILIES.md`, `artifacts/acolb_001a/`, `artifacts/route_c_candidate_harness_001a_accepted_negative_evidence_closure_001a/`, `artifacts/claude_independent_acsb_001b_hostile_audit_001a/`. Observed HEADs `bb65008c` / `98be7f4` / `347b75b9` — metadata only.

## 6. Admission verdicts

Exactly one verdict is assigned per surface. Only the first is an admission; the rest are
blocks.

- `admissible_for_candidate_preflight` — passes §2, §3, §4 re-promotion rule, and §5 with no §6 stop condition triggered. Authorizes candidate-card *drafting only* (not implementation, not Gate run, not mainline/runtime).
- `rejected_metric_degenerate` — any §2 degenerate predictor reaches the ceiling band, or a single-sided/size-exploitable metric is used.
- `rejected_no_fair_signal` — no fair, legal channel separates from random/visible determination (§3.1, §3.3, §2.5); the surface carries no candidate-exclusive signal.
- `rejected_trivially_decodable` — the target/answer is directly decodable from passive values or a leakage channel (§3.2, §3.4).
- `rejected_baseline_saturated` — the strongest fair baseline ties the candidate at ceiling (delta ≤ band); the discriminative margin is structurally unreachable (§5; DISTRIBUTION-HEADROOM-PREFLIGHT-CONTRACT-001A).
- `blocked_pending_canonical_readback` — the preflight artifacts cannot be byte-faithfully read back from canonical source (mount/FUSE truncation, stale mtime, broken git index), or generator provenance is unverifiable. No admission verdict is trustworthy until canonical readback succeeds via the authoritative file API (not the truncating mount). Grounding: Route C candidate-harness R1 re-audit — a FUSE-truncated mount made an authoritative file look absent; provenance must use file-API readback. Observed in the `route_c_candidate_harness_001a` lineage — metadata only.

## 7. Stop condition (blocking)

Candidate implementation is BLOCKED if any of the following hold:

```text
- any metric degeneracy from §2 (predict_all / predict_none / constant-k /
  threshold / random-band / size-exploit / single-sided metric), OR
- fair-baseline saturation from §5 (strongest fair member ties candidate within band), OR
- an answer-key-only oracle gap (§4.1) with no budget-faithful visible-channel oracle, OR
- a no-fair-signal result (§3.1 / §3.3), OR
- an unresolved canonical-readback block (§6 blocked_pending_canonical_readback).
```

On any stop condition: do not author a candidate, do not tune thresholds to escape the
gate, do not relabel saturation with softer language, and do not patch the metric to hide
the degeneracy. Record the blocking verdict and route to closure or bounded repair under a
separate authorized task card.

## 8. Grounding index (failure family → pointer → observed commit)

| Failure family | Standard clause | Ledger / artifact pointer | Observed commit (metadata only) |
|---|---|---|---|
| recall-only / predict_all saturation | §2.1, §2.6, §2.7 | decision_log (Route C separation probe rejection); `artifacts/claude_independent_candidate_free_route_c_baseline_separation_probe_001a_hostile_audit_rejection_001a/` | `b45598b` |
| post-hoc threshold / clip tuning | §2.4 | decision_log; GATE4-PREFLIGHT-001B artifacts | `90dc4b9` |
| fair-baseline / exhaustive-query saturation | §2.5, §5, `rejected_baseline_saturated` | decision_log (ACP-BV 001B closure); DISTRIBUTION-HEADROOM-PREFLIGHT-CONTRACT-001A; `artifacts/route_c_candidate_harness_001a_accepted_negative_evidence_closure_001a/` | `98be7f4` |
| visible-target / access-parity | §3.1, §4.3 | decision_log; `artifacts/implement_future_gate4_cross_family_social_causal_transfer_001a/` | `78889b6` |
| observation-decodable self-set | §3.2 | decision_log (Route C preflight blocker); `artifacts/route_c_preflight_001a/` | `726f26d` / `278819a` |
| baseline_hint / name-list leakage bypass | §3.4 | decision_log; NEGATIVE_EVIDENCE_LEDGER (cb95bbd); `artifacts/gate4_replacement_discriminative_social_latent_001b/` | `ec11f88` / `cb95bbd` |
| candidate-authored ground truth (non-circularity) | §3.5 | NEGATIVE_EVIDENCE_LEDGER (cb95bbd); `artifacts/one_gate_future_only_non_circular_harness_001a/` | `cb95bbd` |
| direct-objective-optimizer equivalence | §5 (direct optimizer) | decision_log (ACOLB-A closure); `artifacts/acolb_001a/` | `bb65008c` |
| fake "learned" / deterministic-stub baseline | §5 (amortized learner) | decision_log; `artifacts/claude_independent_acsb_001b_hostile_audit_001a/` | `347b75b9` |
| graph-cache collapse | §5 (graph-cache challengers) | CLOSED_FAMILIES; Gate1 EXEC-001; Route C final closure artifact | `495300cb` (Gate1) |
| canonical-readback / mount truncation | §6 `blocked_pending_canonical_readback` | decision_log (Route C candidate-harness R1 re-audit); `artifacts/route_c_candidate_harness_001a/` | `b45598b` |

## 9. Claim ceiling

This standard produces bounded route-governance evidence only. It does not prove
consciousness, subjective experience, real emotion, self-awareness, real autonomy,
agency, AGI, companion readiness, stable user benefit, or the correctness of any total
theory (Bio-CMBC, CVPSM, VCCO, CMBC, R/G). It cannot, by itself, admit any surface as a
Gate pass; the strongest admission it grants is `admissible_for_candidate_preflight`,
which authorizes candidate-card drafting under a separate audited task card.

## 10. Non-authorization

This document does not authorize: a new Route C (or any) mechanism surface; candidate
authoring or implementation; Gate execution; threshold/metric/distribution patching;
EGO mainline, runtime, scheduler, or admission work; LLM/AIRI integration; product or
companion work; or any executable enforcement of this standard. A future executor of this
registry requires its own bounded, independently audited task card.

Auto-Remote-Anchor: forbidden.
