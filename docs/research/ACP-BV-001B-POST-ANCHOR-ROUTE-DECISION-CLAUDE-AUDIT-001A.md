# ACP-BV 001B — Post-Anchor Route-Decision Independent Hostile Audit (001A)

Role: independent auditor / red-team (Same-Agent Bridge Audit Role 001, Preflight Audit Rule).
Task type: post-anchor **route decision** (not implementation, not candidate repair).
Audited anchor: `remote-anchor-acp-bv-001b-negative-harness-repair-evidence-001a-98be7f4`
Commit: `98be7f4e647d7d5e897ee32b7905e085b67a43e7`
Excluded prior commit (fake-green, not on publication path): `a90ddde2c0536fb3f933fb6218f66ebc1c3bbd9f`
Date: 2026-06-15.

This document records a route decision. It is a **normative/governance artifact**, not mechanism
evidence. Claude design and Claude reasoning in this file are **not** evidence.

---

## 0. Independent verification performed (not narrative trust)

All cited evidence was re-derived from a clean, isolated `/tmp` checkout at `98be7f4`
(the user working tree was never modified). Recompute, not artifact-trust:

| Claim (as briefed) | Verified | Method |
|---|---|---|
| harness exit code = 1 | **YES** | ran `runner` directly, `$?` = 1 |
| verdict `blocked_by_candidate_truth_coupling` | **YES** | reproduced from source |
| co-trigger `blocked_by_baseline_equivalence` | **YES** | `result.json` co-trigger + closure artifact |
| candidate score = 1.0 | **YES** | reproduced |
| strongest baseline = `parametric_modular_linear_baseline`, score 1.0, delta 0.0 | **YES** | reproduced; `b3_classification = baseline_equivalent` over 5 seeds |
| coupling agreement (overall + extrapolation) = 1.0, max_abs_divergence = 0 | **YES** | reproduced; `n_probes = 1632` |
| training invariance | **YES** | `fit([])==fit(legal)==fit(label_permuted)`, `predictions_invariant_to_training=true` |
| detector failability controls executed = 8 | **YES** | all 8 `discriminates_clean_and_intervened=true`, `actual_flip_matches_predeclared=true` |
| scoped pytest = 16 passed | **YES** | reproduced in clean git worktree (`16 passed`) |
| auto-remote-anchor not performed | **YES** | `validation.json.auto_remote_anchor.decision="forbidden"`, `performed=false` |
| no forbidden-scope path changed | **YES** | change set isolated to `src/acp_bv_distribution_harness_001b/`, `tests/…001b…`, one artifact dir |

Two structural findings the brief did not state but which **dominate** the route decision:

1. **The candidate is a hardcoded oracle, and the "repair" did not touch it.**
   `src/acp_bv_distribution_harness_001b/candidate.py` is **byte-identical** between the rejected
   `a90ddde` and the anchored `98be7f4` (empty diff). It embeds the generator's exact parameters
   (boundary modulus 7, weights {signal 2, topology 3, risk 4, phase 5}; viability modulus 5,
   residues [0,2]) and recomputes the closed form. `fit_candidate` ignores training content.
   The repair changed only **detector/harness** files (`coupling.py`, `detectors.py`, `baselines.py`,
   `leakage_scanner.py`, `runner.py`; +924 insertions). The old harness false-negatived this same
   oracle as `candidate_truth_decoupled` via a trivial "shared-helper-name" check; the new harness
   runs a real behavioral probe grid (408 cells × 4 actions = 1632 probes incl. 48 extrapolation
   cells) plus training-invariance and correctly blocks it.

2. **The distribution is saturated by a *fair* baseline.**
   `solvability_preflight.json`: `legal_channel_parametric_score = 1.0`,
   `leaking_oracle_solvability_detected = false`, `legal_solvability_detected = true`. The strongest
   fair baseline (`parametric_modular_linear`) reaches **1.0 through legal channels with no oracle
   leakage**, while every lookup / memory / NN / graph-cache challenger
   (`count_table`, `successor_map`, `fsm_planner`, `episodic_traversal`, `factorized_lookup`,
   `exact_key_memory`, `action_conditioned_nearest_neighbor`, …) scores ≈ 0.046–0.105. The b3
   equivalence band is |delta| ≤ 0.02.

Finding 2 is decisive (see §7, §9).

---

## 1. Verdict

**Accept the challenged hypothesis, with refinements.**

- **Close** ACP-BV 001B as a *mechanism-evidence* route. **ACCEPT.**
- **Downgrade** it to **bounded negative-harness / fail-able-detector (governance) evidence**. **ACCEPT.**
- **Preserve** the harness apparatus (detectors, fair-baseline panel, coupling probe, failability
  controls, replay, source-boundary) as reusable validated tooling — close ≠ delete.
- **Protocolize** the red-first → narrow-impl → hostile-audit workflow, but **only minimally**:
  a distribution **headroom/saturation STOP-gate** + role separation, labeled normative-not-evidence. **ACCEPT (bounded).**
- **Replacement surface**: **DEFER** behind a precondition (a passing headroom preflight that shows
  the strongest *fair* baseline < ceiling − band on legal channels). **Do not authorize building it now.**

The decisive reason to close is **not** "the candidate was a trivial oracle" (that is fixable);
it is **distribution saturation by a fair baseline**, which makes discriminative
"candidate strictly beats fair baseline" evidence **structurally unreachable on this distribution
regardless of candidate quality**.

No mechanism development is needed now. The decision is enacted by documents.

---

## 2. Current layer

Engineering implementation layer (the harness) carrying a **negative** mechanism-hypothesis result.
The candidate+distribution probe sits at the mechanism-hypothesis layer and returned a collapse
(falsification), not a survival. **No** learning/adaptation, subjectivity-validation, or
philosophical-consciousness content is present or claimed.

## 3. Mainline integration status

**None.** `result.json`: `mainline_integration_status="none"`, `safe_to_wire_mainline=false`,
`real_gate_target_applied=false`. Change set is isolated; no EGO mainline file touched; no schema
migration; `forbidden_scope_violation=false`. No accidental mainline contamination detected.

## 4. Enabled status

**Local CLI / local pytest / local artifact generation only.** Not wired to any runtime, scheduler,
gate, admission path, or live service. `auto_remote_anchor = forbidden`, `performed = false`.

## 5. Real trigger evidence (independently reproduced)

- `runner` real exit code **1**; stdout terminal line `blocked_by_candidate_truth_coupling`.
- Primary verdict `blocked_by_candidate_truth_coupling`; co-trigger `blocked_by_baseline_equivalence`;
  `terminal_collapse=true`.
- Candidate score **1.0**; strongest fair baseline `parametric_modular_linear` **1.0**; delta **0.0**;
  `b3_classification=baseline_equivalent` on all 5 seeds {1009,2027,3037,4049,5051}.
- Coupling: `agreement_rate_overall=1.0`, `agreement_rate_extrapolation=1.0`, `max_abs_divergence=0`,
  `n_probes=1632`; `trigger_A_oracle_match=true`, `trigger_B_training_invariance=true`.
- 8 detector failability controls, each `discriminates_clean_and_intervened=true` and
  `actual_flip_matches_predeclared=true`. Notably control "route candidate and truth through shared
  answer helper" → `blocked_by_candidate_truth_coupling` (the exact `a90ddde` fooling family), and
  "force strongest fair baseline score to equal candidate" → `blocked_by_baseline_equivalence`.
- `candidate.py` byte-identical between `a90ddde` and `98be7f4`; repair confined to detector/harness.
- `solvability_preflight`: legal parametric score 1.0, no oracle-leak solvability; all lookup/graph-cache/NN
  baselines ≈ 0.05–0.10.
- Scoped pytest: **16 passed** (reproduced in clean worktree).

This is **detector / negative-control evidence**. It is not mechanism evidence.

## 6. Claim ceiling

Strongest admissible claim:

> The repaired ACP-BV 001B harness reproducibly produces a terminal collapse
> (candidate–truth coupling co-triggered with fair-baseline equivalence) on a hardcoded-oracle
> candidate over a parametrically-saturated distribution, and its eight **enumerated** detectors are
> demonstrably fail-able. This is bounded local negative-harness / fail-able-detector evidence only.

Explicitly **not** established: ACP-BV validity, mechanism validity, Gate validity, bridge/admission/
runtime/scheduler/live/mainline readiness, agency, autonomy, consciousness, emotion, stable user
benefit, EGO readiness, or fooling-proofness **beyond the 8 enumerated injection families** (the
controls prove fail-ability against those 8 patterns, not against an arbitrary 9th evasion).

## 7. Strongest objection to closing / downgrading ACP-BV (steelman)

"This is the most rigorous negative-control apparatus the lab has built — 8 fail-able detectors, a
broad fair-baseline panel covering every mandated graph-cache challenger, a real behavioral coupling
probe, a reproduced collapse, a clean source boundary. Closing the *surface* discards validated
apparatus and momentum. And the saturation is arguably patchable **inside** the 001B family: redefine
the metric or add partial observability / stochasticity / a held-out structural regime the parametric
baseline cannot legally recover, opening headroom without starting a new surface. On that view, 001B
is one distribution patch away from being discriminative, so closure is premature."

**Response.** Partially correct, and it is *why* replacement (option 3) is deferred rather than
rejected — but it does not keep 001B-as-is open:

- Headroom can only be created by **changing the generative distribution/metric**. Doing that *after
  observing the saturation* is exactly the "tune the distribution/threshold after seeing results"
  move the operating contract forbids. A legitimate headroom distribution must be specified and
  preflighted **as a new surface**, blind to the desire to make the candidate pass.
- The apparatus is **preserved** regardless; "close the mechanism route" ≠ "delete the harness."
- Therefore the objection redirects to **option 3 (deferred behind a headroom preflight)**, not to
  reopening 001B. Closure of the *mechanism route* stands.

## 8. Strongest objection to protocolizing the workflow (steelman)

"Protocolizing on n=1 is premature generalization. One successful repair may have succeeded for
reasons specific to this oracle/saturation case; codifying it as *the* workflow risks ossifying a
process that fails on genuinely hard surfaces. It also risks converting a bounded mechanism lab into
a process-governance project (a 'broad architecture' the contract discourages), and treating a
Claude-authored protocol doc as *progress* is the 'Claude design as evidence' fallacy the operator
explicitly warned against."

**Response.** Valid enough to **bound, not block**:

- Restrict protocolization to a **minimal, testable governance rule**: a *headroom/saturation STOP-gate*
  ("if the strongest fair baseline already saturates the legal-channel ceiling within the equivalence
  band, REJECT the distribution before authoring a candidate") plus **role separation** (red-first
  designer ≠ implementer ≠ auditor). No grand framework, no meta-architecture.
- Label it **normative governance**, never evidence. Its existence proves nothing about any mechanism.
- Record the **n=1 limitation** explicitly (see §14). With these bounds the objection is mitigated.

## 9. Route options — accept / reject / defer

| # | Option | Decision | Rationale |
|---|---|---|---|
| 1 | Close as a mechanism surface | **ACCEPT** | Distribution saturated by a fair baseline (§0.2, §7); no candidate can beat strongest fair baseline on this distribution. Preserve harness as tooling. |
| 2 | Downgrade to negative harness / governance evidence | **ACCEPT** | Reproduced collapse + 8 fail-able detectors are real, but bounded to detector/negative-control validity (§5, §6). |
| 3 | Replace with a new surface after stronger preflight | **DEFER** | Conditional only. Precondition: a headroom preflight demonstrating strongest fair baseline < ceiling − band on legal channels, specified blind to pass-desire. Do **not** authorize building now. |
| 4 | Protocolize red-first → narrow-impl → hostile-audit | **ACCEPT (bounded)** | Only the minimal saturation STOP-gate + role separation; normative-not-evidence; n=1 caveat. |

Options are not mutually exclusive.

## 10. Recommended route

**Now (documents only): 1 + 2 + 4.** Defer 3 behind its precondition.

1. Record this closure + downgrade in `docs/decision_log.md` (one bounded entry; do not rewrite prior
   entries).
2. Add a **distribution headroom / saturation STOP-gate** rule to the preflight contract: any future
   mechanism surface must show, at preflight, that its strongest *fair* legal-channel baseline scores
   **strictly below** ceiling − equivalence_band; otherwise the surface is rejected before any
   candidate is authored.
3. Add the **role-separation** rule (designer ≠ implementer ≠ auditor) to the same governance note.
4. Mark **remote anchor forbidden** for this route unless separately authorized; **Auto-Remote-Anchor
   forbidden**.

## 11. Is development actually needed now?

**No.** The route decision is enacted by governance/decision documents. No mechanism code, no
candidate repair, and no harness change is required or advisable now. Specifically: do **not** repair
the 001B candidate toward pass, and do **not** "patch" the 001B distribution to remove saturation.

An **optional, deferred** governance tool (a reusable saturation-preflight evaluator + a generalized
detector-injection failability harness extracted from 001B) is designed at document level in §12 and
drafted as a Codex card in §13. It is **governance / negative-control evidence only**, **not** a
mechanism route, and must **not** execute without separate explicit authorization.

## 12. Document-level design (OPTIONAL, DEFERRED — governance tool only)

> Build nothing from this section without a separate authorizing instruction. No mechanism claims.

- **Proposed docs**
  - `docs/codex/contracts/DISTRIBUTION-HEADROOM-PREFLIGHT-CONTRACT-001A.md` — defines the saturation
    STOP-gate, fairness of the baseline panel, equivalence band, and reject/accept semantics.
  - `docs/decision_log.md` — append one bounded closure/downgrade entry (no rewrite).
- **Proposed artifact paths**
  - `artifacts/distribution_headroom_preflight_001a/headroom_report.json`
  - `.../baseline_panel_scores.json`
  - `.../failability_controls.json`
  - `.../replay_report.json`
  - `.../result.json`, `.../claim_ceiling.txt`, `.../failure_manifest.json` (if any check fails)
- **Proposed module / function names** (new, isolated; reuse 001B baselines/detectors read-only)
  - `src/distribution_headroom_preflight_001a/__init__.py`
  - `evaluate_headroom(distribution_spec, baseline_panel, *, ceiling, equivalence_band) -> HeadroomReport`
  - `strongest_fair_baseline_score(...)` ; `headroom_margin(...)` ; `verdict_from_margin(...)`
    returning `reject_saturated` | `accept_has_headroom`.
  - `run_failability_controls(detectors) -> ControlReport` (generalized from 001B detector injection).
- **Required checks / tests** (`tests/test_distribution_headroom_preflight_001a.py`)
  - saturated distribution (e.g., 001B's own generator) → `reject_saturated` (negative self-test).
  - synthetic distribution with a known unrecoverable held-out regime → `accept_has_headroom`.
  - margin computation matches a hand-computed fixture.
- **Failability requirements**
  - The gate must be demonstrably fail-able: feeding 001B's saturated distribution **must** produce
    `reject_saturated`; a non-saturated fixture **must** produce `accept_has_headroom`. A gate that
    cannot reject is itself rejected (`blocked_by_non_fail_able_preflight`).
- **Baseline / ablation / leakage / replay requirements**
  - Baseline panel must include the mandated fair families: parametric, lookup, exact-key/partial-key
    memory, factorized lookup, and graph-cache (`count_table`, `successor_map`, `fsm_planner`,
    `episodic_traversal`), plus NN. **Strongest = argmax** (most damaging).
  - Leakage: legal-channel-only; reuse 001B `solvability_preflight` to assert
    `leaking_oracle_solvability_detected=false`.
  - Replay: `headroom_report.json` must be recomputable from recorded inputs without future
    observations or private state.
  - Ablation: removing the saturation check must flip a saturated fixture from reject→accept (proving
    the check is load-bearing).
- **Forbidden files / changes**
  - Do **not** modify `src/acp_bv_distribution_harness_001b/**`, its artifacts, or `candidate.py`.
  - Do **not** modify EGO mainline, schemas, thresholds-after-results, or any path outside the new
    isolated module + its test + its artifact dir + the two docs above.
- **Acceptance gate**
  - New tests green; 001B saturated self-test → `reject_saturated`; non-saturated fixture →
    `accept_has_headroom`; failability + ablation + replay artifacts present; claim ceiling recorded;
    no forbidden path touched; worktree clean.
- **Stop condition**
  - If the gate cannot be made fail-able, or if it would require importing hidden labels / future
    observations, **stop** and emit `failure_manifest.json` instead of weakening the check.
- **Rollback plan**
  - Pure additive isolated module; rollback = delete `src/distribution_headroom_preflight_001a/`, its
    test, its artifact dir, and the new contract doc; revert the single decision_log entry. No shared
    state mutated.

## 13. Draft Codex task card (DO NOT EXECUTE without separate authorization)

```yaml
task_id: DISTRIBUTION-HEADROOM-PREFLIGHT-001A
status: DRAFT — NOT AUTHORIZED FOR EXECUTION (governance tool only; not a mechanism route)
authorization_required: separate explicit operator instruction
problem_definition: >
  ACP-BV 001B collapsed because its distribution is saturated by a fair legal-channel parametric
  baseline (score 1.0), making discriminative candidate>baseline evidence structurally impossible.
  No reusable gate currently rejects a saturated distribution BEFORE a candidate is authored.
current_stage: governance preflight tool (engineering implementation layer)
hypothesis: >
  A distribution can be rejected at preflight when its strongest FAIR legal-channel baseline scores
  >= ceiling - equivalence_band, preventing future saturation traps. (Governance hypothesis, not a
  mechanism hypothesis.)
baseline: >
  Reuse 001B fair-baseline families (parametric, lookup, exact/partial-key memory, factorized lookup,
  count_table, successor_map, fsm_planner, episodic_traversal, NN). Strongest = argmax score.
ablation: remove the saturation check -> a saturated fixture must flip reject->accept (load-bearing proof)
trace_replay_requirement: >
  headroom_report.json recomputable from recorded inputs; no future observations; no private state;
  replay_report.json must reproduce the verdict.
acceptance_gate: >
  pytest green; 001B saturated generator -> reject_saturated; non-saturated fixture -> accept_has_headroom;
  failability + ablation + replay + leakage artifacts present; claim_ceiling.txt written; worktree clean.
claim_ceiling: >
  Bounded governance/negative-control evidence only. Proves nothing about ACP-BV, any mechanism, any
  Gate, mainline, agency, autonomy, consciousness, emotion, user benefit, or EGO readiness.
stop_condition: >
  If the gate cannot be made fail-able, or requires hidden labels / future observations, STOP and emit
  failure_manifest.json; do not weaken the check to pass.
rollback_plan: delete the isolated module + test + artifact dir + new contract doc; revert one decision_log entry
forbidden:
  - modifying src/acp_bv_distribution_harness_001b/** or its artifacts or candidate.py
  - repairing the 001B candidate toward pass
  - patching the 001B distribution to remove saturation
  - EGO mainline / schema / threshold-after-results / any out-of-scope path
  - Auto-Remote-Anchor (forbidden unless separately authorized)
constraints_for_codex:
  - do not redefine success as "green"; a reject verdict on the saturated self-test IS success
  - preserve failure artifacts; do not patch failures into passes
  - report files changed, commands run, tests run, artifacts produced, remaining uncertainty
```

## 14. What this does not prove / remaining unknowns

- Does **not** prove ACP-BV validity, mechanism validity, Gate validity, mainline effect, live/runtime
  readiness, agency, autonomy, consciousness, emotion, stable user benefit, or EGO readiness.
- Detector fail-ability is proven only against the **8 enumerated** injection families, not against an
  arbitrary novel evasion.
- The protocolization rests on **n=1** successful repair; the saturation STOP-gate is a hypothesis
  about future surfaces, not a validated law.
- Whether a **non-saturated** ACP-BV-style distribution with legal headroom even exists is **unknown /
  unavailable** until a headroom preflight is run on a concrete proposed redesign.
- This audit verified `98be7f4` in an isolated `/tmp` checkout; it did not re-fetch or re-verify the
  remote tag bytes on GitHub.

---

**Auto-Remote-Anchor: FORBIDDEN (unless separately authorized).**
This route decision creates a stable downstream-citable boundary (001B closed as a mechanism route;
downgraded to bounded negative-harness/governance evidence). Anchoring it remotely is a separate,
explicitly-authorized action and is not performed here.
