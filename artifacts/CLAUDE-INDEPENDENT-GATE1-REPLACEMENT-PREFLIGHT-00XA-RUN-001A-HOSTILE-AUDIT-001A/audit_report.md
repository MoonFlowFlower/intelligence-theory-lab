# Hostile Audit — GATE1 Replacement Preflight 00XA Run 001A

**Audit ID:** CLAUDE-INDEPENDENT-GATE1-REPLACEMENT-PREFLIGHT-00XA-RUN-001A-HOSTILE-AUDIT-001A
**Date:** 2026-06-17
**Role:** Independent auditor / red-team (Same-Agent Bridge Audit Role 001)
**Audited bundle:** `artifacts/gate1_replacement_preflight_00xa_run_001a/`
**Audited terminal-verdict claim:** `rejected_baseline_saturated`

## Verdict

**`requires_one_bounded_evidence_repair`**

The saturation finding is real, computed, fail-able, in-scope, and byte-reproducible from source. There is exactly **one blocking defect**: a frozen-spec conformance gap in generator provenance that, per the spec's own rule, mandates a `blocked_pending_canonical_readback` terminal verdict for this bundle's actual state — not `rejected_baseline_saturated`. The defect is bounded and repairable; the saturation is expected to survive the repair.

## Why (decision basis)

What is strong (independently verified):

- **Verdict is computed, not literal.** `verdict.derive_final_verdict` is an ordered fail-closed cascade. A fresh clean-room re-run reproduced `verdict_derivation.json` **byte-identical** to the committed artifact, and a fail-ability probe drove the function to **six distinct verdicts including `admissible_for_candidate_card_drafting_only`**. This resolves the literal/hardcoded-verdict (B1) failure family that blocked the earlier Route C harness.
- **Saturation is real and legal.** `exhaustive_legal_query` and the visible-channel oracle both read only `legal_channel_responses` (legal majority vote), never `hidden_target`; both score macro F1 = 1.0 and tie within the 0.03 equivalence band. The generator (`_legal_votes`: 14/16 votes correct) makes the legal channel fully determine the target, while passive features carry only partial signal (0.6). Saturation is a true property of the surface as generated.
- **Metric is the correct balanced one.** macro F1 (β=1.0) with per-class P/R recorded. `predict_all` has recall 1.0 but macro F1 = 0.333 and does **not** win — this is precisely the fix for the prior Route C `predict_all == oracle` recall-only false-positive.
- **Thresholds are frozen, not tuned.** `CEILING_BAND_FLOOR=0.87`, `TARGET_CEILING_MINIMUM=0.90`, `EQUIVALENCE_BAND=0.03`, `PER_CLASS_FLOOR=0.85`, `PARTIAL_INFERABILITY_MARGIN=0.06` all match the frozen spec text.
- **Spec identity confirmed.** Live spec sha256 = `fca7e5eb…c9` (24588 bytes, 0 CRLF) reproduced independently; spec/freeze not mutated; readback runs before scoring.
- **Controls are fail-able.** Leakage positive control: inject → detect, remove → clear, same path. Replay: recompute-from-serialized-state with a working corrupt-state negative control (not hash-only). All clean-room reproduced.
- **Baseline panel complete.** 30 baselines incl. all six mandatory graph-cache challengers, lookup-imitation family, direct optimizers, degenerate predictors, size-only sweep — all callable, invoked, consumed.
- **Scope clean.** All gate1 paths untracked; HEAD unchanged; no commit/push/tag; no candidate/runtime/EGO/LLM contamination from this task.

What blocks the terminal label:

- **Generator provenance gate not honored (B1).** The frozen spec is unconditional (lines 350–352): *"If generator provenance is absent, unverifiable, self-readback-only, or candidate-authored, the future verdict must be `blocked_pending_canonical_readback`."* The State Schema (line 104) requires `generator_source_hash: "sha256-or-blocked"` per record; the Generator Provenance section requires source SHA256, code-path hash, `producer_function`, fair-baseline-access, hidden-target-storage, and a no-candidate-authored-truth assertion. The generated bundle records only `generator_id` + a source-path string. `grep` confirms: `generator_source_hash` is absent from `src`, no run_001a artifact records generator provenance, `spec_loader.py` (the generator) is **not** among the canonical source pins, and `derive_final_verdict` contains **no** generator-provenance gate. Therefore the spec-correct terminal verdict for this bundle's actual provenance state is `blocked_pending_canonical_readback`, and the emitted `rejected_baseline_saturated` skips a spec-mandated gate.

This is blocking for the **terminal label only**: a rejection cannot be inflated into a false admission, so the substance (saturation) stands as preliminary route evidence.

## Blocking issues

1. **B1 — generator-provenance gate not implemented and generator provenance absent.** Spec mandates `blocked_pending_canonical_readback`; harness emits `rejected_baseline_saturated`. (See `audit_result.json` for exact evidence.)

## Non-blocking issues

- Per-class floor (0.85) + `validate_metric_contract` defined but not wired into the admissible branch — immaterial to this rejection; required before any admission.
- `visible_channel_oracle` is the same function as `strongest_known_classical_method` — honest for a rejection (no daylight = saturation), but circular if it ever drives an admission.
- Leakage scanner is token-name-only; value-level leakage is covered separately by the passive-decodability gate.
- Ablation values are presence-consumed (not value-consumed) by the verdict; `no_action`/`no_transition` are predict-none counterfactuals rather than bundle mutations (`no_legal_channel` is a real mutation).
- `validation_report.json` and several boolean flags are self-reported shape (load-bearing ones independently corroborated against code and git).

## Required fix (single bounded repair)

Implement the frozen spec's generator-provenance requirement, no more:

1. Record complete generator provenance (generator source SHA256 + version/code-path hash + `producer_function` + fair-baseline-access + hidden-target-storage + no-candidate-authored-truth assertion).
2. Add `src/gate1_replacement_preflight_00xa/spec_loader.py` to the canonical source-pin readback so the generator is hashed.
3. Wire a generator-provenance gate into `derive_final_verdict`: absent/unverifiable/self-readback-only/candidate-authored generator provenance → `blocked_pending_canonical_readback`.

Constraints: do **not** mutate the frozen surface spec; do **not** change thresholds; do **not** add a candidate. Re-run preflight and re-audit.

## Disposition of the questions asked

- **Negative verdict accepted as route evidence?** The *substance* (00xa surface as generated is fair-baseline-saturated) is accepted as preliminary route evidence. The *terminal label* `rejected_baseline_saturated` is **not** admissible as-is; it becomes valid after the bounded provenance repair.
- **Implementation repair allowed?** Yes — exactly the one bounded repair above.
- **New surface design or close 00XA?** Deferred until after the repair confirms generator provenance and persistent saturation. Then: close the 00xa surface for candidate work; if an admissible Gate1 replacement is still wanted, design a new surface with baseline-resistant headroom (visible-channel oracle ≥ 0.90, oracle − strongest fair > 0.03, passive < 0.87).
- **Remaining blocking issue?** B1 (generator provenance) only.

## Final report fields

- **Verdict:** `requires_one_bounded_evidence_repair`
- **Layer:** engineering implementation / candidate-free preflight (no mechanism/subjectivity claim)
- **Files changed:** none in repo source/tests (audit is read-only); audit deliverables written under this directory only
- **Commands run:** `sha256sum` (spec), `git status/log`, `python -m pytest tests/gate1_replacement_preflight_00xa -q` (22 passed), clean-room `run_preflight` re-execution + byte-diff, `derive_final_verdict` fail-ability probe, `grep` for generator-provenance gate
- **Artifacts generated:** `audit_result.json`, `audit_report.md` (this file)
- **Baseline results:** strongest fair `exhaustive_legal_query` = 1.0; passive family = 0.6; degenerate ≤ 0.5247; all six graph-cache = 1.0 (reproduced)
- **Ablation results:** no_action / no_transition / no_legal_channel = 0.3333; no_observation / no_leakage_control = 1.0 (reproduced)
- **Replay result:** valid; recompute-from-serialized-state; corrupt-state negative control flips (reproduced)
- **Stop conditions triggered (by run):** `fair_baseline_ties_oracle_within_equivalence_band` (valid computation, but superseded by the unimplemented generator-provenance block)
- **Claim ceiling:** candidate-free preflight evidence bundle only; bounded offline saturation evidence for the surface as generated
- **What this does not prove:** Gate1 pass, mechanism/candidate validity, that saturation is intrinsic to the spec's intended surface vs the generator, runtime/EGO readiness, or any subjectivity/agency/emotion claim

## Next minimal closed-loop action

Authorize one bounded harness-repair task card (generator-provenance conformance + gate wiring). Re-run preflight, re-audit. If saturation persists with complete generator provenance, record `rejected_baseline_saturated` as terminal and route to surface closure + new headroom-bearing surface design.

**Push status:** NOT pushed/committed/tagged/anchored. `scripts/push.*` hardcoded-PAT remains a standing BLOCK on any remote action until rotated.
