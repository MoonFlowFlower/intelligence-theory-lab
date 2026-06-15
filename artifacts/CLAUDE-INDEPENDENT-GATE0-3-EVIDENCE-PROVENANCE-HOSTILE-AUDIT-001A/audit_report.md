# CLAUDE-INDEPENDENT-GATE0-3-EVIDENCE-PROVENANCE-HOSTILE-AUDIT-001A

**Layer:** evidence-governance / cross-gate provenance hostile audit only.
**Mode:** read-only. No gate repaired. No old artifact rewritten. No remote anchor (forbidden by task card). No mechanism-validity claim.
**Core question answered:** for each Gate0–3 evidence claim, did the reported result come from a callable, inspectable, *executed* computation path — or from literals / static reports / unconditional-pass logic?

---

## Global verdict

**`gate0_3_evidence_partially_inadmissible_freeze_downstream_inheritance`** (option 3).

The strongest baseline the task card asked me to defeat — *"a trivial report-shaped function can emit all committed baseline/ablation artifacts without executing the claimed mechanism"* — is **DEFEATED only by Gate0 and by Gate2's baselines**. It **SUCCEEDS** against Gate1, Gate3, the integrated Gate0–Gate3 testbed, and Gate2's ablation. For those, the committed `baseline_comparison.json` / `ablation_report.json` are byte-for-byte equal to the output of **zero-argument constant functions**: they cannot depend on any candidate run, and were proven equal to it in-audit.

This is the same failure mode Gate4 exposed. It is present, pre-existing, in the Gate1–Gate3 + integration "executable preflight" layer.

---

## Method and evidence base

- Static source trace of every score/verdict-bearing function in the four gate modules + integrated testbed.
- Live introspection: argument counts of baseline/ablation producers; byte-equality of committed artifacts vs. function output (`artifacts/.../provenance_probe.json`).
- pytest positive control: gate1+gate2+gate3 preflight tests (26 passed); Gate0 baseline/oracle-leak/ablation tests (3 passed).
- Prior-evidence reconciliation: `docs/GATE1-REPLAY-CONSOLIDATION-LINEAGE-CLOSEOUT-001.md`, `artifacts/GATE0-PREDICTIVE-ACTION-POSTFREEZE-SHORTCUT-AUDIT-001A/`, `docs/NEGATIVE_EVIDENCE_LEDGER.md`.

**Environment caveat (honest limitation):** the audit sandbox has a broken `.git` mount (`git ls-files` → exit 128), so the integrated testbed runner could not be executed end-to-end. This does **not** weaken the integrated-testbed finding: the literal nature of its baseline/ablation is proven by argcount=0 + committed-artifact equality, which need no runner. It only means I could not independently re-emit its git-dependent hermeticity artifacts.

---

## Per-gate findings

### Gate0 — predictive action learning (`predictive_action_learning_contract_001` / `_001c`)
**This is the one genuinely computed gate.** Source lives at repo root (not `src/`). Tests run `run_episode` + `compute_run_metrics` per baseline predictor (passive, action_token, retrieval, hardcoded, oracle, skeleton ablations) and assert **directional separation computed from real runs** (`passive nll > main nll + 0.05`). It has a **real leakage positive control**: `test_oracle_leak_is_flagged_as_impossible_and_main_is_not` — the oracle predictor must fall below the NLL leak floor (detector fires), the legitimate learner must not. Ablations (`action_input_mode=none`, `belief_update_enabled=False`, `theta_update_enabled=False`) are real reruns asserting degradation.

- Producer executed: **yes** · Baseline independent: **yes** · Ablation real: **yes** · Leakage positive control: **yes** · Literal risk: **low**
- **Verdict: admissible** — but only at its **pre-existing narrowed ceiling.** The lab's own `GATE0-PREDICTIVE-ACTION-POSTFREEZE-SHORTCUT-AUDIT-001A` already returned `medium_risk_with_claim_caveats`: the count/statistic/transition/successor/graph_cache/fsm/episodic-traversal fair-control family was **never run**, and nearest-history retrieval matched action-sensitive NLL within the declared margin (and beat the learner post-shift). Gate0 is admissible as *mechanism-distinguishability under one frozen rule*, **not** as superiority over cache/retrieval, and it authorizes nothing downstream.

### Gate1 — replay / consolidation (`gate1_replay_consolidation_001c_executable_preflight`)
`_baseline_report()` (runner L367) and `_ablation_report()` (L404) return **hardcoded literals** with `"executed": True` and `"all_required_ablations_executed": True` — both false claims; nothing is executed. The committed graph-cache control is a literal `match_rate: 0.25, equivalent_to_candidate: False`.

- Producer executed: **partial** (trace real; baseline/ablation **no**) · Baseline independent: **no** · Ablation real: **no** · Leakage positive control: **no** · Literal risk: **confirmed**
- **Aggravating:** `docs/GATE1-REPLAY-CONSOLIDATION-LINEAGE-CLOSEOUT-001.md` records `parent_gate1_package_verdict = failed_graph_cache_collapse` ("window model dominated the entire belief-model class by up to −0.27 nats"). The 001c preflight's literal "graph-cache not equivalent" assertion is exactly the negative evidence the lab already filed — re-stated as a literal pass, with no computation that would overturn it.
- **Verdict: inadmissible.** Trace hash-chain hygiene only.

### Gate2 — controllability / self-boundary (`gate2_controllability_self_boundary_001b`)
**Mixed.** Baselines are **real**: `baseline_predictions()` (core L586) implements 8+ control families (random, frozen, behavior-imitation, retrieval-majority, identity-tag lookup, actor-id table, action-outcome count table, transition/graph-cache), and `evaluate_baselines()` (L635) runs each on heldout and computes match rates. Committed result: candidate 1.0 vs best fair baseline (retrieval) 0.5, gate **fail-able**. Heldout controllability accuracy and later-action accuracy are genuinely computed.
**But** `ablation_report()` (L700) is **literal**: every row hardcodes `"executed": True` and all `*_changed: True`; `ablation_gate_passed` is structurally always True. No ablation is run.

- Producer executed: **partial** · Baseline independent: **yes** · Ablation real: **no** · Leakage positive control: **no** (token scan over real keys, but no injected positive control; heldout/support composition-disjointness not separately bounded) · Literal risk: **medium**
- **Verdict: provisionally admissible pending rerun.** Baseline-non-equivalence + heldout controllability accuracy are admissible now. The **ablation-sensitivity claim is inadmissible** until ablations are run as real interventions. (Candidate 1.0 on a tiny heldout also warrants a support/heldout overlap check before any strength claim.)

### Gate3 — viability / functional affect (`gate3_viability_functional_affect_001b`)
`baseline_comparison()` (core L871) and `ablation_report()` (L925) are **0-argument literal constants**; committed artifacts equal function output; candidate score hardcoded `1.0`. Same pattern as the integrated testbed.

- Producer executed: **partial** (candidate loop real) · Baseline independent: **no** · Ablation real: **no** · Leakage positive control: **no** · Literal risk: **confirmed**
- **Verdict: inadmissible.** Trace hash-chain hygiene only.

### Integrated Gate0–Gate3 testbed (`r_g_gate0_gate1_gate2_gate3_canonical_micro_agent_testbed_001b`)
The candidate loop *does* run a single shared-state agent and emits a genuine hash-chained trace; `replay_integrity_report()` genuinely recomputes that chain (real tamper hygiene). **But the distinguishing evidence is literal.** `baseline_comparison()` (core L590) and `ablation_report()` (L621) take **0 arguments**; committed `baseline_comparison.json` / `ablation_report.json` are byte-equal to their output; candidate integration score is hardcoded `1.0`. The verdict gates that yield `bounded_preflight_pass` (stop_conditions `[]`) are therefore driven by literals: `baseline_gate_passed` and `ablation_gate_passed` are structurally always True. The leakage scanner reads a hand-clean hardcoded `input_names` list — there is no positive-control case a real leak must trip.

- Producer executed: **partial** (loop + replay yes; baseline/ablation **no**) · Baseline independent: **no** · Ablation real: **no** · Leakage positive control: **no** · Literal risk: **confirmed**
- **Verdict: inadmissible** as integration mechanism evidence. The anti-sycophancy narrative ("graph caches … do not show one hash-linked shared state") is asserted against baselines that were never run.

---

## Downstream inheritance (task-card check #12)

`docs/codex/audits/EGO-MAINLINE-READINESS-AUDIT-001A.md` inherits Gate1/Gate2/Gate3 `result.json` **directly** as "bounded … preflight evidence" (lines 35–44, 116–118). Three of those four inherited surfaces are report-shaped.

**Required freeze:** downstream EGO-mainline reasoning must stop inheriting (a) Gate1 evidence, (b) Gate3 evidence, (c) the integrated-testbed integration claim, and (d) Gate2 *ablation-sensitivity*. It may inherit Gate0 and Gate2 baseline/heldout-accuracy **only at their narrowed ceilings**.

---

## Minimal rerun / repair (separate bounded Codex tasks — not done here)

1. **Gate1, Gate3, integrated testbed:** replace literal `baseline_comparison`/`ablation_report` with callable baseline policies and real ablation reruns over the actual loop; recompute candidate scores instead of hardcoding `1.0`; add ≥1 leakage positive-control injection. Gate1 must additionally include the graph-cache/window/count family and reconcile with the `failed_graph_cache_collapse` lineage.
2. **Gate2:** run ablations as real interventions; add leakage positive control + heldout/support composition-disjointness bound.
3. **Provenance contract:** require every `*_gate_passed` field to trace to a function that consumes the candidate run; ban 0-argument score producers; make `"executed": true` a computed (not literal) field.

---

## Stop conditions triggered
- Report-shaped baseline/ablation with no callable producer: Gate1, Gate3, integrated testbed, Gate2-ablation → marked inadmissible (not reconstructed).
- Integrated runner not executable in audit sandbox (broken git mount) → recorded as limitation; finding established without it.

## Claim ceiling
This audit establishes **evidence-admissibility status only.** It does **not** prove any Gate0–3 mechanism works; it does not prove consciousness, subjective experience, real emotion, self-awareness, real autonomy, agency, AGI, EGO/bridge/companion readiness, or stable user benefit. "Admissible" means "traceable to executed computation at a bounded ceiling," nothing more.

## What this does not prove
- Does not prove Gate0 or Gate2 mechanisms are *valid* — only that their (narrow) evidence is computed and fail-able.
- Does not prove Gate1/Gate3/integration mechanisms are *false* — only that their committed evidence is non-computed and cannot currently support any claim.
- Does not prove absence of other leakage/shortcut in Gate0/Gate2 beyond the surfaces inspected.

## Remaining unknowns
- Whether re-run Gate1/Gate3/integration baselines would collapse to graph-cache/count/window controls (Gate1 lineage suggests **yes**).
- Gate2 candidate 1.0 heldout: memorization vs. mechanism (support/heldout composition overlap unbounded in current artifacts).
- Whether any *other* downstream record beyond EGO-MAINLINE-READINESS-AUDIT-001A inherits these verdicts.
