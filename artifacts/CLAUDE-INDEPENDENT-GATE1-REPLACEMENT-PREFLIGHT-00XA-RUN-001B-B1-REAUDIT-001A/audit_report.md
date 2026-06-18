# B1-Focused Hostile Re-Audit — GATE1-REPLACEMENT-PREFLIGHT-00XA run_001b

**Verdict:** `evidence_bundle_001b_accepted_rejected_baseline_saturated`

**Role:** Same-Agent Bridge Audit Role 001 (independent auditor / red-team).
**Layer:** engineering implementation / candidate-free preflight B1 evidence repair.
**Scope:** B1 repair + minimal no-regression only. R1 / implementation-card / surface-spec governance audits were NOT redone.
**Mainline integration:** none. **Enabled status:** no runtime/mainline path enabled.

## Prior state
- Prior audit verdict: `requires_one_bounded_evidence_repair`.
- Prior blocker: `B1_generator_provenance_gate_not_honored` — run_001a lacked (1) `spec_loader.py` in source pins, (2) a recorded generator source SHA256, (3) a generator-provenance gate in `derive_final_verdict`; the spec mandates `blocked_pending_canonical_readback` when generator provenance is absent/unverifiable, so the terminal `rejected_baseline_saturated` was not spec-correct. The saturation substance itself was accepted as real, computed, fail-able, in-scope, reproducible.

## B1 repair — accepted
All three missing pieces are now present and verified:

1. **`spec_loader.py` pinned.** `readback.REQUIRED_SOURCE_PINS` includes it; `source_readback.json` records it with `sha256 = 7cbe9d36…4f5c`, `byte_count = 8921`, `all_present = true`, `hash_conflicts = []`.
2. **Generator provenance complete.** `generator_provenance.json` carries all required fields (source hash, source path, version/code-path hash, producer function, fair-baseline-access, hidden-target-storage, no-candidate-authored-truth, readback channels, consumed flag) plus `self_readback_only=false`, `candidate_authored_truth=false`, `source_pin_integrity=true`. Built by `spec_loader.build_generator_provenance`, where both `generator_source_hash` and `source_pin_sha256` derive from `file_sha256()` of the same path — equality is structural, not asserted.
3. **Gate implemented, fail-able, ordered.** `verdict.validate_generator_provenance` + the call at `derive_final_verdict` line 251 sit **before** the `rejected_baseline_saturated` rule (line 322).

### Fail-ability (clean-room, 8/8 PASS)
Reimplemented the gate + cascade from file-API source and executed in-sandbox. Every malformed generator-provenance case routed to `blocked_pending_canonical_readback`: missing/None, missing `generator_source_hash`, hash mismatch, `self_readback_only=true`, `candidate_authored_truth=true`, `no_candidate_authored_truth=false`, `source_pin_integrity=false`, dropped `canonical_source_pin_readback` channel.

### Ordering + non-literality
- valid gp + forced degenerate ceiling → `rejected_metric_degenerate` (cascade continues past gate).
- invalid gp + forced degenerate ceiling → `blocked_pending_canonical_readback` (gate wins over both the degenerate rejection and saturation → gate precedes them).
- valid gp + non-saturated inputs → `admissible_for_candidate_card_drafting_only`.
Four distinct terminal verdicts from one function ⇒ no literal/static terminal path. `verdict_derivation.final_verdict == final_verdict.json.final_verdict == rejected_baseline_saturated`.

### Spec alignment (not a governance re-audit)
The frozen spec (hash unchanged `fca7e5eb…c9`) mandates this gate at lines 327–352. Because the spec hash is unchanged, this is **not** governance-self-modification — 001B honors a pre-existing frozen rule that run_001a omitted.

## Recomputed saturation (clean-room, independent)
Generator (seeds 4001–4040, 20/40 positive) + baselines + macro-F1 recomputed in-sandbox, not copied from 001A:
- `exhaustive_legal_query` = **1.0**; visible-channel oracle = **1.0**; all six graph-cache challengers = **1.0**; strongest_fair = **1.0**.
- passive_max = 0.60; max degenerate = 0.5247; size_only = 0.5489 → all below the 0.87 floor, so the cascade legitimately reaches the saturation rule (not an earlier degenerate/passive rejection).
- Oracle/exhaustive use legal-channel votes only (`answer_key_access=false`, `visible_channel_only=true`); `hidden_target` is read only by the diagnostic answer-key oracle (`may_support_admission=false`). Saturation is genuine: 16 legal votes (14 correct / 2 flipped) under fixed budget 16 lets a fair baseline recover the target and tie the oracle. `1.0 ≥ 1.0 − 0.03` → `rejected_baseline_saturated`, derived from the frozen equivalence rule.

## No-regression / scope
- Thresholds unchanged: β=1.0, band 0.03, ceiling 0.90, ceiling-band floor 0.87, per-class floor 0.85, partial-inferability margin 0.06.
- No candidate added; frozen spec unmutated; exhaustive_legal_query and graph-cache challengers not weakened; all six present/invoked/consumed.
- Leakage (clean scan empty + fail-able positive control consumed), replay (valid/consumed), ablation (5 rows invoked+consumed) all present and consumed.
- `validation_report.json`: allowlist exact, gate valid, `commit_push_tag_anchor_attempted=false`.
- Git HEAD `b45598b1` unchanged; 001B entirely untracked; 001A preserved as a separate dir.
- 001A↔001B shared artifacts differ only by `run_id` stamp; the two files without a run_id field are byte-identical → metric logic unchanged.

## Auditor decision fields
- **Blocking issues:** none.
- **Non-blocking issues:** (1) generator hash numeric value not byte-level re-derivable through the truncating FUSE mount (real 8921B vs mount 6583B) — verified by content read + structural equality + runtime-computed-not-literal + byte_count corroboration; standing lineage caveat. (2) 001B drops `surface_spec_readback.json` (replaced by `spec_hash_assertion.json` + generator provenance files); freeze identity still anchored via source pins + prior core audit; out of B1 scope. (3) freeze.json expected hash pinned via source_readback only, not a hardcoded constant. (4) pre-existing dirty tree outside 00xa, not attributable to 001B.
- **Required fixes:** none.
- **Implementation may proceed:** No candidate implementation on this surface. B1 repair accepted; only governance close-out + design-only headroom surface drafting allowed.

## Answers to the posed questions
- **`rejected_baseline_saturated` accepted as terminal route evidence?** Yes — now spec-correct (valid generator provenance → gate passes → saturation rule fires on independently reproduced 1.0/1.0).
- **Close 00XA for candidate work?** Yes — fair candidate-free baselines (incl. all six graph-cache + exhaustive legal query) saturate the surface at 1.0; no candidate mechanism can beat a fair baseline here.
- **Further implementation repair allowed?** No further B1 repair; no candidate implementation on this surface.
- **New headroom surface design warranted?** Yes — design-only: a future surface must set fixed budget < full legal-channel count so exhaustive/graph-cache families cannot reach the oracle, creating genuine fair-vs-oracle headroom. Needs its own preflight + freeze + spec.

## Claim ceiling
Repaired candidate-free Gate1-replacement preflight evidence bundle only — bounded offline **negative** (baseline-saturation) evidence, with a now spec-correct, fail-able, correctly-ordered B1 generator-provenance gate.

## What this does not prove
Gate1 pass; Gate1 replacement validity; any mechanism validity; candidate success/feasibility; Gate4/Gate5 readiness; runtime/mainline/live effect; agency, autonomy, consciousness, emotion, self-awareness; stable user benefit; EGO readiness; correctness of Bio-CMBC/CVPSM/VCCO/CMBC/R-G.

## Remaining unknowns
- The exact byte content / true SHA256 of `spec_loader.py` beyond what the file-API exposes (mount truncation) — corroborated, not byte-recomputed.
- Whether the planned headroom surface can produce non-saturated fair-vs-oracle separation without reintroducing oracle/answer-key leakage (open design question).

## Method / commands
- Source forensics via file-API Read (authoritative); bash used only for clean (untruncated) hashes, parsing, git status, and the in-sandbox clean-room run.
- Clean-room reimplementation of generator + 30 baselines + `validate_generator_provenance` + `derive_final_verdict` executed in `/tmp` to bypass the truncating mount.
- `git status --porcelain`; spec sha256 (`24588B → fca7e5eb…c9`); 001A↔001B shared-artifact hash compare; bundle JSON/JSONL shape + consumption checks.

**Audit artifacts not pushed.** Delivered under `artifacts/CLAUDE-INDEPENDENT-GATE1-REPLACEMENT-PREFLIGHT-00XA-RUN-001B-B1-REAUDIT-001A/`.
