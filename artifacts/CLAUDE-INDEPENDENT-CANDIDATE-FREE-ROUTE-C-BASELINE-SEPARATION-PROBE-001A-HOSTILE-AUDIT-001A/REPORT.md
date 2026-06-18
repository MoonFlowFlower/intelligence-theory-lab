# Hostile Audit — CANDIDATE-FREE-ROUTE-C-BASELINE-SEPARATION-PROBE-001A

**Verdict: `reject_as_false_positive_or_weakened_baseline`**
**Implementation may proceed: NO.** Do not draft a Route C re-promotion preflight on this evidence.

Audited: `src/candidate_free_route_c_baseline_separation_probe_001a/runner.py` +
`artifacts/candidate_free_route_c_baseline_separation_probe_001a/`. Probe-reported HEAD
`b45598b1` (not independently verifiable — `.git/config` FUSE mount corrupt; provenance read via file-API).

---

## Conclusion

The reported separation — oracle recall `1.0` vs strongest fair baseline (`mean`) `0.5833`,
delta `0.4167`, verdict `separation_exists_route_c_may_repromote_one_surface` — is **a false
positive**. It is produced by two compounding design defects, not by any real privilege gap:

1. **Pure-recall metric, no precision penalty, no prediction-size cap on passive baselines.**
   `_score_prediction = |truth ∩ pred| / |truth|`. Predicting *more* items strictly raises recall.
2. **The baseline panel omits the trivial recall-maximizing fair baseline.** A non-privileged
   "predict the entire legal action space" baseline scores recall **1.0 == oracle**.

Under the strongest *admissible* fair baseline, `delta = 0.0` and `separation_exists = False`.

## Computed evidence (independent clean-room reproduction)

I regenerated the toy episodes from the salts/seeds hard-coded in `runner.py` **without importing
the module** (`cleanroom_reproduction.py`, in this folder):

| Producer | recall (mean over 6 eval episodes) | privileged? | in panel? |
|---|---|---|---|
| oracle (reads `hidden_set`) | **1.0000** | yes | — |
| `mean` (probe's reported strongest_fair) | 0.5833 | no | yes |
| **`predict_all` (predict all 12 legal items)** | **1.0000** | **no** | **NO** |
| `threshold_min` (same `mean` family, threshold=min) | **1.0000** | no | NO |

- Faithfulness: my generator reproduces the probe's `mean` per-episode `[0.5,0.25,0.75,0.25,1.0,0.75]`
  and oracle `[1.0]*6` **byte-identically** — so the comparison is valid, and the scores are real
  episode execution (Check 6 passes; this is **not** a fabrication, it is a *weakened-baseline* false positive).
- `corr(visible_score, hidden_membership) = 0.0029 ≈ 0`. The hidden set is ranked by `SOURCE_SALT`
  while visible features come from a *different* `VISIBLE_SALT`; the two hash streams are independent,
  so visible features carry **no signal** about the hidden set.
- Max prediction-set size anywhere in the probe's own `trace.jsonl` = **7** (never the full 12) →
  the recall-maximizing baseline is confirmed absent.

## Why this matters (the decisive logic)

Because features are independent of the hidden set, recall can only be raised by **claiming more
items**, which the metric never penalizes. So:

- The oracle gets 1.0 by *reading the answer* (`set(private_episode["hidden_set"])`).
- A fair `predict_all` gets 1.0 by *claiming everything* — no privilege, fully legal, leakage-clean.
- The probe's own ablation shows that at **full budget, `exhaustive_legal_query` → 1.0** as well.

So the ceiling is reachable **three** ways, two of them by fair access. The claim that "only
privileged access reaches the ceiling" is false. The `0.5833` number is an artifact of
`baseline_mean`'s arbitrary `>= mean` threshold; move the threshold to `min` and the *same* baseline
hits 1.0.

## Critical-check results

| # | Check | Result |
|---|---|---|
| 1 | oracle privilege impossible for fair baselines | pass at field level, **not decision-relevant** (predict-all also hits 1.0) |
| 2 | no non-oracle baseline reads hidden truth | **pass** (baselines get `legal_view` + training-episode membership only) |
| 3 | `exhaustive_legal_query`@budget=2 not misleadingly weakened | **fail at panel level** — strongest admissible fair baseline = `predict_all` (1.0), omitted |
| 4 | baselines competent, not placeholders | **fail** — recall-maximizing fair baseline absent; `mean` threshold caps it artificially |
| 5 | access parity per class | **fail** — passive may emit arbitrary-size sets, active confined to confirmed queries; recall metric rewards size |
| 6 | scores from episode execution, not static | **pass** — reproduced byte-for-byte |
| 7 | all attempted configs preserved | partial — single hardcoded budget=2; only 0/12 extremes in ablation |
| 8 | full-budget saturation control drives verdict & can flip | **fail** — control computed but `select_decision_verdict` ignores it; inert |
| 9 | leakage positive control same path & blocked | pass (caveat: name-substring scanner only) |
| 10 | replay recomputes from serialized state | **pass** |
| 11 | source-pin dual-channel / authoritative | weak pass (both reads hit the same on-disk file) |
| 12 | manifold/circular/spectral baselines required | N/A task; spirit violated → folds into 3-4 |

## Blocking issues

- **B1 — metric:** pure recall, no precision/over-claim penalty, no size cap on passive predictions.
- **B2 — weakened panel:** `predict_all` (fair, non-privileged, recall 1.0) omitted; including it makes
  `decision_gate.separation_exists = False`.
- **B3 — claim-ceiling leakage:** the probe admits in `blocked_or_unknown_items` that it "does not show
  any future candidate can exploit the configuration," yet emits a **re-promotion** verdict and a
  "draft a new Route C surface" next-action. An oracle-reads-the-answer / metric artifact is being
  converted into authorization to re-open a closed negative surface.
- **B4 — inert control:** the saturation control that exposes the budget-artifact nature is not wired
  into the verdict path.

## Non-blocking

leakage scanner is name-only (N1); source-pin reads one file twice (N2); single budget config (N3);
**the pytest suite hard-codes the spurious result** (`assert separation_exists is True`) so green
tests are not evidence here (N4); probe-reported git HEAD unverifiable via corrupt mount (N5).

## Required fixes before any separation/re-promotion claim

1. **F1** — precision-aware metric: exact-set match, F1/Jaccard, or cap `|prediction| ≤ hidden_set_size`
   for *all* families incl. passive and oracle.
2. **F2** — add the omitted fair baselines (`predict_all`, threshold-swept passive, size-normalized
   random-K) and re-measure delta against the true strongest admissible fair baseline.
3. **F3** — make the oracle comparison fair (informed-but-budget-limited oracle), or restate the result
   as "field-level privilege only" with no re-promotion implication.
4. **F4** — feed full-budget / budget-sweep into `select_decision_verdict` so the control can flip the verdict.
5. **F5 (deeper)** — as built, the hidden set is information-theoretically independent of every fair
   channel (independent salts). Even a fixed metric would only show the oracle reading an *unlearnable*
   field. If partial inferability is intended, the generator must couple features to the hidden set;
   only then are spectral/NN/supervised challengers meaningful and only then could mechanism-reachable
   headroom exist. Absent that coupling, there is no basis to re-promote Route C.

## Claim ceiling

Candidate-free route-governance separation audit only. No Route C mechanism validity, no candidate
success, no hidden-self-set inference, no self-boundary evidence, no Gate pass, no mainline/runtime/
live effect, no agency, autonomy, consciousness, emotion, stable user benefit, or EGO readiness.

## What this audit does NOT prove

It does not prove Route C is false, that no separating configuration could exist, or that a
precision-aware redesign would also saturate (likely, given corr≈0, but not formally tested here). It
shows only that **this** probe's separation is a false positive driven by metric design and an
incomplete baseline panel.

*Not pushed, not anchored. `scripts/push.*` carries a hard-coded PAT (prior blocker) — must stay unused until rotated.*
