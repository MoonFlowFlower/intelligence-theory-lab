# Independent Evidence-Integrity Hostile Audit — BASELINE-FIRST-HARNESS-001A-R1

Date: 2026-06-17 · Repo HEAD: `b45598b1` · Audited bundle: `artifacts/baseline_first_harness_001a/` (untracked)

Scope (as requested): evidence-integrity only. NOT candidate evidence, NOT a Gate1 pass,
NOT mechanism/candidate/runtime/agency/consciousness/EGO. No route tournament, WM-P/VSB-C/CSL,
or environment-optimization authorization is implied.

## Verdict

**ACCEPTED — candidate-free Phase-0 no-headroom negative environment evidence.**
Blocking issues: **none.** `impl_may_proceed = false`. Route tournament / candidate work: **not authorized.**

The reported verdict `rejected_no_headroom_baseline_saturated` is computed (not literal),
fail-able, byte-identically reproducible, and correct for the frozen environment. Preserve it
and **close MINIMAL-ENV-SPEC-001A for candidate work**.

## What I independently verified

- **Byte-identical reproduction.** Re-ran the harness from the intact mount to `/tmp`;
  `final_verdict.json` and `score_summary.json` are byte-identical to the committed bundle.
  (No FUSE truncation on these files: bash SHA256 of the spec equals the frozen Windows hash.)
- **Verdict is callable, not handwritten.** `run_harness` returns
  `produce_baseline_first_harness_001a_r1_verdict(...)` (line 686) with no post-hoc override; a
  handwritten-vs-callable disagreement gate exists. Seven fail-ability probes confirm the
  verdict branches on its inputs:

  | Probe | Injection | Verdict |
  |---|---|---|
  | PA | all fair baselines → 0.5 | `headroom_confirmed_...` (flips OFF saturation) |
  | PB | degenerate → 0.95 | `rejected_metric_degenerate` |
  | PC | passive → 0.95 | `rejected_passive_trivially_decodable` |
  | PD | oracle-budget → failed | `blocked_oracle_not_budget_faithful` |
  | PE | one graph-cache 1.0, rest 0.5 | `rejected_no_headroom_baseline_saturated` |
  | PF | visible 0.5, answer-key 1.0 | `rejected_no_oracle_headroom` |

  PA is the decisive one: if the baselines did **not** saturate, the harness would report
  headroom. The stop is earned, not wired.
- **Self-check 12/12** reproduced (`self_check_status=passed`).
- **Pre-registration.** `freeze_status=frozen_before_any_baseline_or_oracle_scores`, freeze
  timestamp 11:57 precedes the run (~18:19) by ~6h; spec SHA256 `bf48145b…` matches the run
  command and an independent recompute; freeze SHA256 `dc6d42b2…` matches the loader pin;
  mutation-ban set; push/tag/remote-anchor all false.
- **Controls consumed.** 49 evidence rows, all `consumed_by_final_verdict=true`; the verdict
  blocks if any required row is missing/unconsumed, and PD/PE prove oracle-budget and the
  graph-cache scores actually drive the result.
- **Degeneracy gate fires before saturation** — directly closing the prior Route-C
  `predict_all == oracle` false-positive family.

## Why the saturation is real (Q5)

The frozen environment defines `target = sum(5 budget-component channels) mod 5`, and the
budget (5) exactly covers those 5 channels. So any budget-respecting legal-channel reader
recovers the target exactly → 1.0, which equals the answer-key ceiling (1.0). Meanwhile the
metric genuinely discriminates: degenerate max **0.189**, passive max **0.40**,
size-only **0.40** — all far below the legal-channel readers, and `observation_only`
predictions differ from the oracle. So this is not metric-trivial saturation; it is
"the cheapest legal-channel route already maxes out, leaving no headroom for a candidate."

The spec itself anticipated exactly this outcome (lines 50-69, 113-117, 220-223): budget below
full legal-channel count is *necessary but not sufficient*, and if a fair baseline reaches the
oracle within the band, the harness *must* return no-headroom and stop. It did.

## Non-blocking issues (matter for REUSE, not for this stop)

- **N1 — baseline diversity is cosmetic.** The 15 "fair / graph-cache / lookup" producers are
  aliases of one function `predict_from_budget_components` (verified: identical source bodies,
  identical predictions to the oracle). "Six graph-cache challengers = 1.0" is one computation
  reported six times. Acceptable for a no-headroom STOP (a faithful budget-respecting
  `graph_lookup`/`count_table` over the same 5 channels would yield the same 1.0), but it must
  **not** be cited as independent corroboration and must **not** be reused as-is for any
  positive headroom claim, candidate tournament, or BASELINE-IMMUNITY admission — there it would
  be a blocking under-powered-battery defect.
- **N2 — `strategy_class_alignment` is non-fail-able.** It compares two hardcoded-identical
  literal dicts; it can never return `failed` for real code. Consumed but evidentially empty.
- **N3 — oracle budget-faithfulness sub-controls are near-vacuous.** Hidden-field
  ablation/permutation pass by construction (the oracle never reads hidden fields); the
  forbidden-token scan runs over a self-declared manifest.
- **N4 — leakage control is name-token only**, not value-level (happens not to matter here).
- **N5 — thresholds + generator live in unfrozen `.py`.** Only the spec `.md` SHA is enforced.
  Mitigated: the decisive margin is exactly 0.0 (band-tuning cannot change the verdict) and the
  `.py` values match the `.md`.
- **N6 — per-class 0.85 floors not enforced** in the verdict (moot for no-headroom; relevant
  only on the headroom path).

None of these can manufacture a *false* no-headroom: 1.0 is the true ceiling and a genuine
legal-channel reader reaches it, so no candidate could exceed it. All defects are conservative
or moot for the path taken.

## Closeout (Q6/Q7)

- No blocking integrity defect. **Preserve** as bounded negative environment evidence.
- **Close MINIMAL-ENV-SPEC-001A for candidate work.** It is not a neutral tournament surface;
  it is trivially legal-channel-solvable and therefore unsuitable for candidate discrimination.
- Next action: **stop / preserve.** No route tournament, no candidate implementation, no
  push/tag/remote-anchor (PAT-bearing scripts remain BLOCKED).

## Claim ceiling

Bounded evidence-integrity certification only: the run is reproducible, fail-able,
pre-registered, and its no-headroom verdict is computed and correct for the frozen spec. This
does **not** prove Gate1 pass, mechanism validity, candidate feasibility, runtime effect,
baseline-immunity of any future surface, or agency/autonomy/consciousness/EGO readiness. If
anything, it proves the environment has **no** headroom.

## What this audit does not prove

Candidate feasibility; that the environment is a valid tournament surface (it is closed);
that the graph-cache challengers are independent (aliases); that the alignment/ablation/leakage
controls are strong in absolute terms; any consciousness/subjectivity/emotion/autonomy/agency/
AGI/EGO claim.

---
Delivered to `artifacts/CLAUDE-INDEPENDENT-BASELINE-FIRST-HARNESS-001A-R1-EVIDENCE-INTEGRITY-HOSTILE-AUDIT-001A/`.
Audited bundle and repository unmodified. Not committed, not pushed.
