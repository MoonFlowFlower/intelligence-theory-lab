# ROUTE CLOSURE — UNCERTAINTY-VOI-REQUEST-MECHANISM (001A→002A→003A) — intelligence-theory-lab

> Bounded route-closure record. Docs-only. This document does NOT rewrite, delete, reinterpret-as-stronger, or patch any prior artifact; all 001A/002A/003A preregistrations, runners, and gated artifacts remain on disk as frozen evidence. This is a Yellow-tier closure (route closes on a preserved bounded-negative result); it claims no mechanism validity.

## task_id
UNCERTAINTY-VOI-REQUEST-MECHANISM-CLOSURE-001

## Verdict
**CLOSED — BOUNDED_NEGATIVE (terminal verdict: `STATIC_SUFFICIENT`).**
On the frozen hold-and-observe restless-Gaussian-bandit toy, a Kalman-belief + myopic knowledge-gradient (exploit-pressure) mechanism does **not** beat a tuned age-threshold heuristic within the pre-registered 10% MDE on fresh held-out seeds. The route is closed as a bounded negative. This is not evidence that value-of-information is worthless, nor that the mechanism is a trivial baseline; see Claim ceiling.

## Research layer
Layer 3 mechanism-hypothesis test, executed as offline engineering + evidence-hygiene artifacts. Closure is Layer-2 evidence hygiene.

## Problem definition
Test whether one implemented uncertainty/VOI mechanism, in one toy environment, beats BOTH a best-tuned static-threshold rival and a random-active baseline on a VOI-headroom task, with attribution (advantage collapses under corrupted feedback and uncertainty-ablation), calibration, and held-out transfer.

## Lineage and per-stage outcomes (all on branch `codex/meta-theory-scaffold`; artifacts preserved)
- **001A** — prereg LF sha256 `46031e0340f0e3eb3f65f22a1728eb925840dba9c890aa1aece375141b740180` (R1 `b05fbac0`), impl R2 `d46a641`, gated R3 `7be2680`. Verdict **`INSTRUMENT_INVALID`**. Yellow audit (2026-07-09) root cause: two coupled prereg-design defects — (a) the primary metric was **blind on information steps** (`regret_t = max_value + cost`, independent of belief ⇒ every non-exploit policy bit-identical ⇒ falsifier/ablation deltas structurally 0.0), and (b) the frozen KG rule (raw expected-improvement − cost) **never exploited** (0/4000 actions) ⇒ collapsed to the non-learning floor. The banked `G6_HEADROOM_FAILED` subtype misattributed the failure to the environment; the environment was valid. Instrument defect, not an environment or mechanism-absence result.
- **002A** — prereg LF sha256 `bc087cfc13102a57a624b7bb5d8684b50303db7c9be701bdd08d709bffffdf73` (R1' `c8f0d0cd`), impl R2' `8968b2e`, gated R3' `e54e8e2b`. Banked verdict **`ATTRIBUTION_FAILURE`**. **This banked label is a frozen-gate artifact and must NOT be read at face value.** Yellow audit (2026-07-09) found the frozen G2/G3 required the falsified advantage's CI to *include 0* (collapse-to-parity) and therefore mislabeled the stronger collapse-to-**negative** signature as "survival." In fact the data showed the advantage was destroyed / driven strongly negative by every falsifier and the key ablation (wrong_sign A≈−123, shuffled ≈−67, uncertainty_ablation ≈−17, value_ablation ≈0) — a genuine attribution *success* signature. The banked 002A artifacts are preserved unchanged; the corrected 003A gates supersede this attribution reading. (Model A — hold-and-observe — and the exploit-pressure KG introduced here fixed the two 001A defects; validated by a pre-freeze simulation before freezing.)
- **003A** — prereg LF sha256 `9964fbce108228cf32cd2df8834ed8b002bb27bc210956c3186c3fd7b96a5b26` (R1'' `a4d68c8d`), impl R2'' `8d8944ce`, gated R3'' `67edff12`. Verdict **`STATIC_SUFFICIENT`** (subtype `G1A_STATIC_RIVAL_FAILED`, `positive_claim=false`). Corrected G2/G3 to the magnitude-free attribution signature; kept q=0.004 and everything else; re-scored on **fresh** seeds `9401–9420` (transfer `9421–9430`) that did not motivate the correction. **Terminal verdict of the lineage.**

## What the lineage established (bounded)
On the frozen 003A fresh seeds (independently re-checked by Claude Yellow audit, bootstrap CI recomputed):
- The mechanism reliably **beats indiscriminate active gathering** (`random_active`): A ≈ +4.35, 95% CI [2.81, 5.98], ~30% relative (G1b pass).
- The advantage is **attributable**: it collapses (to ≤ parity, i.e. driven strongly negative) under `wrong_sign` and `shuffled` (G2 pass) and under `uncertainty_ablation` (G3 uncertainty-collapse true) — i.e. the mechanism genuinely uses correct feedback, correct arm-attribution, and uncertainty.
- The mechanism does **not beat a tuned age-threshold heuristic** (`static_threshold`): A ≈ +1.02, 95% CI [−2.45, 4.36] (includes 0), relative 9.08% < 10% MDE; the mechanism wins 9 of 20 fresh seeds and loses 11 (≈ coin flip). This is the terminal `STATIC_SUFFICIENT`.
- Secondary shortfalls on fresh seeds: `value_ablation` not load-bearing (clean−value CI includes 0), calibration fails (mean z² ≈ 0.45, over-dispersed), transfer not significant (CI includes 0). Floors dominated (G6 pass), tripwire clean (noop fraction 0.616), replay bit-exact (G5 pass).

## Claim ceiling
Bounded offline evidence, this toy only: a Kalman + myopic-KG VOI mechanism **uses feedback and uncertainty (attributable) and beats random active gathering, but does not outperform a tuned age-threshold heuristic** on this hold-and-observe restless bandit, and its uncertainty estimate is uncalibrated. This proves NEITHER "VOI present as a superior mechanism" NOR "VOI worthless." It proves nothing about intelligence, adaptation, world-modeling, subjectivity, agency, autonomy, emotion, consciousness, EGO/companion readiness, or the pet.

## Standing lessons (durable; recommend absorbing into the reusable standards)
1. **Info-step metric must be belief-load-bearing** (from 001A): in any hold/act task, the per-step regret on a non-terminal/observation step must depend on the agent's belief (e.g. credit the held incumbent); otherwise the metric is blind on those steps and every belief-driven falsifier/ablation reads as a structural zero-delta.
2. **Falsifier/ablation success signature = advantage driven to ≤ parity, including strongly negative** (from 002A): a control that corrupts a load-bearing signal may drive the advantage below zero (actively harmful), which is *stronger* attribution evidence, not "survival." Attribution *failure* is reserved for an advantage that stays significantly positive under the control. (Recommend adding to `MECHANISM-SIGNATURE-VERDICT-STANDARD`.)
3. **Pre-freeze simulation must check the expected sign/magnitude of every control and that the mechanism actually exploits** — not merely that it runs. Two instrument mis-specifications (001A metric, 002A gate) were both caught only by post-hoc audit; the 003A pre-freeze sim + fresh seeds prevented a same-seed false positive.

## Stop condition / reopening
Route stays closed. The ONLY principled reopening is a **new pre-registered hypothesis** with an environment where recency (age) is a poor proxy for uncertainty — e.g. per-arm heterogeneous observation noise, so `age ⊥ uncertainty` — such that a tuned age-threshold cannot capture the VOI value. Any such successor MUST be flagged for anti-pattern risk (do not tune the environment merely to make the mechanism win) and is a NEW route, not a rescue of this one.

## Rollback plan
Docs-only additions; no prior file modified. Rollback = revert the closure commit. No experiment state, runtime, or schema is changed.

## Provenance / evidence contract
All numeric claims above trace to preserved machine-readable artifacts under `artifacts/UNCERTAINTY-VOI-REQUEST-MECHANISM-{001A,002A,003A}/` (result.json, baseline_comparison.json, falsifier_report.json, ablation_report.json, calibration_transfer_report.json, replay_report.json, headroom_report.json, tripwire_report.json, trace.jsonl). Prereg hashes and commit anchors are listed per stage above. Independent Claude Yellow audits: 2026-07-09.
