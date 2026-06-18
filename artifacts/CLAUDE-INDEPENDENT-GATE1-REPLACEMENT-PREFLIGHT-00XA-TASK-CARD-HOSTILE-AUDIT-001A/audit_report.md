# CLAUDE-INDEPENDENT-GATE1-REPLACEMENT-PREFLIGHT-00XA-TASK-CARD-HOSTILE-AUDIT-001A

Independent hostile audit of the drafted Gate1 replacement preflight task card.

## 1. Verdict

`requires_one_bounded_task_card_repair`

The draft (`GATE1-REPLACEMENT-PREFLIGHT-00XA`) is directionally correct, authorizes no implementation, and survives the most dangerous reuse traps (closed Gate1 inheritance, graph-cache collapse, verifier-as-admission). One narrow, non-redesign repair is required before it is sent to Codex: the metric-degeneracy guard is left to a blanket reference instead of being operationalized, and the specific control that broke the lab's most recent surface (single-sided / size-exploitable metric) is not explicitly mandated.

`impl_may_proceed_now = false`. Next action: `GATE1-REPLACEMENT-PREFLIGHT-00XA-TASK-CARD-R1` (repair the draft card only).

## 2. Current Layer

Engineering-governance / hostile audit of a Gate1 replacement preflight task card. Pre-candidate. No mechanism, no Gate run.

## 3. Mainline Integration Status

None. The draft targets no EGO mainline, runtime, bridge, admission, Gate4/Gate5, Route C, scheduler, UI, LLM, AIRI, deployment, or companion path, and this audit added none.

## 4. Enabled Status

Audit-only. Readback plus local audit-artifact generation under `artifacts/CLAUDE-INDEPENDENT-GATE1-REPLACEMENT-PREFLIGHT-00XA-TASK-CARD-HOSTILE-AUDIT-001A/`. No source/test/Gate/candidate/runtime path executed. No commit, push, tag, or remote anchor.

## 5. Real-Trigger Evidence

The prior selection task `GATE1-REPLACEMENT-READBACK-OR-PREFLIGHT-SELECTION-001A` returned `selected_verdict = draft_gate1_replacement_preflight_card` with `next_minimal_closed_loop_action = "send draft to Claude or equivalent hostile audit before Codex implementation"`. The draft under audit is the artifact that selection produced. Readback was verified rather than trusted (see §7).

## 6. Inspected Files (read channel: file-API authoritative unless noted)

- `artifacts/gate1_replacement_readback_or_preflight_selection_001a/draft_next_task_card.md` — sha256(mount) `7a1b2c5e…ff46`
- `…/selected_verdict.json` — `7ab962d4…ae1f`
- `…/gate1_failure_readback.json` — `2bb4e1c6…c98b3`
- `…/gate_dependency_readback.json` — `a89ff9be…752c`
- `…/final_report.md` — `ddcb31fd…e17c8`
- `docs/codex/contracts/BASELINE-IMMUNITY-ADMISSION-STANDARD-001A.md` — `25db1848…e76e`
- `docs/codex/contracts/BASELINE-IMMUNITY-ADMISSION-STANDARD-001A.registry.json` — `3ddf8753…af89` (mount `json.load` raised Extra-data @char 23125; file-API readback shows clean close at line 266 → FUSE tail artifact, **not** a real defect; this is the `canonical_readback_failure` family the registry itself documents)
- `artifacts/post_freeze_gate0_3_sequential_repair_queue_001a_gate1_failed_graph_cache_reconciliation/baseline_comparison.json` — `4daa4c71…2175` (parses on mount; corroborates the Gate1 failure readback)

Context corroboration only: `gate_canonical_inventory_and_return_point_readback_001a/`, `gate_evidence_provenance_verifier_hardening_001a/`, `CLAUDE-INDEPENDENT-GATE-EVIDENCE-PROVENANCE-VERIFIER-001A-HOSTILE-AUDIT-001A/`.

## 7. Decisive Checks — Passed / Failed

### Readback / no-block determination (rules out `block_pending_canonical_readback`)

- `selected_verdict.json` (`draft_gate1_replacement_preflight_card`) and its `next_minimal_closed_loop_action` match the draft card's own next-action. **No contradiction.**
- `gate1_failure_readback.json` (`failed_graph_cache_collapse`, positive inheritance closed, 001C literal pass not upgraded) is **confirmed** by the cited reconciliation `baseline_comparison.json`: `candidate_A_graph_cache_collapse_detected=true`, `fair_control_match_blocks_positive_gate1_claim=true`. No conflict with decision log or remote-anchored closure.
- `gate_dependency_readback.json`: Gate1 closed; Gate2/Gate3 cannot bypass; Gate4/Route C closed/blocked/negative; Gate5 no lower-gate-safe basis. Consistent with the canonical inventory.
- No tracked `gate1_replacement` source/test/candidate path exists (git index). Candidate-free.
- Registry is well-formed via authoritative readback; `executor: none`; verdict set, oracle taxonomy (`answer_key_oracle.supports_route_re_promotion=false`), and six-member graph-cache family (`min_members: 6`) all present.

Repo state permits a reliable audit. `block_pending_canonical_readback` does **not** apply.

### Audit questions Q1–Q12

| # | Question | Result | Basis |
|---|---|---|---|
| 1 | Avoids old Gate1 positive inheritance | **PASS** | Target is pre-candidate admissibility; old Gate1 used only as negative grounding; stop condition "no old Gate1 positive inheritance is reused"; forbidden-files lists old Gate1 source/tests/artifacts as read-only inputs only. |
| 2 | Six-member graph-cache family tied to a stop condition | **PASS** | All six (`graph_lookup`, `transition_table`, `successor_map`, `count_table`, `fsm_planner`, `episodic_traversal`) listed; acceptance gate requires all six when representational/environment claims present; stop condition: "any graph-cache challenger is omitted or saturates". |
| 3 | Pre-candidate only | **PASS** | "candidate-free"; Candidate-Forbidden Condition; forbids candidate impl, Gate run, Route C, Gate4/5, runtime/admission/bridge. |
| 4 | Real target + legal observable channel | **PASS (non-blocking note)** | Meta-target (`gate1_replacement_surface_pre_candidate_admissibility`) and verdict set are clear; object-level target/observation/budget are delegated to a "frozen surface specification pack" with required fields, and the card blocks (`blocked_missing_candidate_free_surface_spec`) if absent/mutable. Residual: spec **authorship/immutability authority** is unpinned → see R1.c. |
| 5 | Baseline-immunity operationalized, not cited as magic | **PARTIAL GAP** | Strong: panel members enumerated; "record whether each registry class is applicable, invoked, and consumed by final verdict derivation"; "must not treat the standard or registry as an executor." Gap: the metric-shape clauses (std 2.6/2.7) and the positive-admission clauses (std 3.3/4.2) are left to the blanket "any metric degeneracy trigger … fires" rather than enumerated. |
| 6 | Avoids metric degeneracy; precision/recall or cost-balanced required | **FAIL (narrow, blocking)** | `predict_all/predict_none/constant_k_sweep/random/majority` are listed, but **no explicit requirement** for a balanced or jointly-reported precision+recall (or cost-weighted/F-beta) metric, and **no explicit size-only sweep** control. Q6 explicitly requires precision/recall-or-cost-balanced. This is the decisive gap. |
| 7 | No answer-key oracle as route/Gate1 headroom | **PASS** | Budget rules forbid "hidden answer-key access for fair baselines"; admissibility rests on baselines **not** saturating, not on an oracle's headroom; no answer-key oracle is used. (See R1.b on the missing *positive* budget-faithful oracle basis.) |
| 8 | Requires computed evidence, not reports | **PASS (strong)** | Computed-Evidence Gate: `producer_function`, input artifacts, `run_id`, seed/episode IDs, aggregation rule, `code_path_hash`, `consumed_by_final_verdict`; "Literal verdicts, static score dictionaries, unconsumed controls, and tests that only assert pass are forbidden." |
| 9 | Provenance verifier used as prefilter only | **PASS (strong)** | Explicit: `provenance_wellformed_only` = bundle shape only; forbidden as Gate pass, admission, baseline-immunity, replay/source/strongest-baseline validation, candidate/mechanism validity. |
| 10 | Leakage / replay / source-pin computed and consumed | **PASS (strong)** | Leakage scanner with fail-able positive control on the same admission path (inject leak → flip to blocked; always-pass / hardcoded-fixture invalid); replay recomputes from serialized state + observation (hash-only / stored-output / NL-trace insufficient); source-pin via authoritative file API, SHA256, conflict fail-closed, per-producer code path hashes; "self-readback only is invalid." |
| 11 | Terminal anti-Zeno stop conditions | **PASS (strong)** | Comprehensive terminal list incl. candidate-needed, spec missing/mutable, any metric degeneracy, any fair baseline ties/beats, any graph-cache omitted/saturates, leakage control absent/undetected/unconsumed, hash-only replay, source conflict not fail-closed, verifier-as-admission, standard-as-executor, any Gate/Route C/runtime/EGO touched. No "repair until positive signal" loop invited. |
| 12 | Success authorizes at most candidate-card drafting | **PASS** | Claim ceiling "candidate-free Gate1 replacement preflight only"; admission verdict is `admissible_for_candidate_card_drafting_only`; explicitly no Gate pass, no progression, no anchor. |

Net: 10/12 strong-to-pass; 1 partial gap (Q5) and 1 narrow blocking fail (Q6), which share a single root cause (metric/admission clauses left by-reference) and are fixable in one bounded card edit.

## 8. Strongest Objection (and the rest)

**Strongest:** *The metric may be exploitable by trivial predictors.* The draft's most recent grounding evidence — the candidate-free Route C separation probe — was rejected precisely because a single-sided (recall-only, no precision penalty) metric let `predict_all` reach the oracle ceiling, manufacturing a false positive. The draft lists the degenerate predictors but does not mandate the balanced/jointly-reported precision+recall (or cost-weighted) metric or the size-only sweep that would catch this. A faithful-but-literal Codex could enumerate `predict_all`/`predict_none` as required, score them, and still ship a recall-only metric on which a non-degenerate-looking surface saturates. **This is the required repair (R1.a).**

Other objections, addressed:
1. *Old Gate1 in new packaging* — refuted; target is admissibility, inheritance forbidden and stop-gated, failure used only as negative grounding.
2. *Graph-cache still solves it* — the draft does not claim to defeat the family; it mandates the six members and stops on saturation. Correct posture; if the object-level surface collapses, the preflight emits `rejected_baseline_saturated`.
4. *Panel omits the real strongest fair baseline* — panel is broad (trivial, passive value-decoders, active/query, six graph-cache, lookup-imitation, direct optimizer, amortized-must-actually-fit, task-specific classical). The "task-specific classical" member is unpinned because the surface is not yet frozen — acceptable for a preflight, but tied to R1.c.
5. *Relies on answer-key oracle headroom* — no; hidden answer-key access is forbidden. (The flip side — no *positive* budget-faithful oracle is required either — is R1.b.)
6. *Verifier misused as admission* — refuted; prefilter-only is explicit.
7. *Long repair chain vs fail-fast* — the draft is fail-fast (terminal stops). This audit also avoids a chain by scoping a single bounded repair.
8. *Too vague → Codex invents a pass-shaped impl* — the only genuine vagueness is (a) the by-reference metric clauses (R1.a, blocking) and (b) the unpinned surface-spec authorship (R1.c). Both are narrow.

Anti-hardcoding / governance-self-modification: the draft modifies neither the baseline-immunity standard nor the verifier (read-only), forbids post-hoc threshold/metric tuning, and is fail-closed. No governance-self-modification.

## 9. Required Repair

**R1.a (blocking).** In the metric / acceptance-gate / baseline-panel region only (no Gate1 route redesign): mandate an explicitly balanced or jointly-reported **precision + recall** metric (or a stated cost-weighted / F-beta metric), **and** an explicit **size-only sweep** control (vary prediction-set size with content policy fixed; the score must not climb to the ceiling band on size alone). Forbid any single-sided metric from supporting an `admissible_*` verdict. Enumerate this as a panel/acceptance control, not only as a reference to the standard.

**R1.b (recommended fold-in).** Make the *positive* admission basis explicit: require the standard's §3.3 fail-able partial-inferability demonstration (genuine residual under the passive channel **and** that the proposed mechanism class can in principle reduce it, with a non-reading oracle scoring 0) and the §4.2 budget-faithful visible-channel oracle separation by ≥ band. Admission must not rest on mere absence-of-saturation.

**R1.c (recommended fold-in).** Pin surface-spec provenance: the frozen surface specification pack must be authored/frozen under a separate authority (or pre-existing), must not be authored or mutated by the preflight implementer, and its provenance/SHA must be recorded with fail-closed behavior if it is implementer-authored on the fly (closes the §3.5 generator-coupling residue).

All three are draft-card edits. Do not implement the preflight under R1.

## 10. Claim Ceiling

Independent task-card audit only. This audit does not prove Gate1 pass, Gate1 replacement admissibility, mechanism validity, candidate success, baseline-immunity enforcement, Gate4/Gate5 readiness, mainline/runtime/live effect, agency, autonomy, consciousness, emotion, stable user benefit, or EGO readiness. The strongest thing it establishes is: the drafted preflight card is one bounded metric-degeneracy repair away from being safe to send to Codex as a candidate-free preflight implementation task.

## 11. Next Minimal Closed-Loop Action

Author `GATE1-REPLACEMENT-PREFLIGHT-00XA-TASK-CARD-R1` — repair the draft card only: close R1.a (blocking), fold in R1.b and R1.c. Then a brief re-audit confirming the single edit did not weaken any other clause, after which `CODEX-GATE1-REPLACEMENT-PREFLIGHT-00XA-IMPLEMENTATION-001A` may implement the preflight (not a candidate, not a Gate pass attempt). Commit / push / tag / anchor remain forbidden unless separately authorized.
