# Negative Evidence Ledger

Negative evidence is the primary scientific asset of this lab.

## Seeded Closed Lineage

The initial ledger imports the VCCO/VCAC/FOPC failure chain:

```text
Full VCCO -> VCAC-Core -> FOPC
```

Key outcomes:

```text
Full VCCO closed.
Plastic selection invalidated as no-op.
Repertoire expansion invalidated as no-op.
Boundary did not enter action distribution.
Action closure did not enter action distribution.
Viability/compression were score-sensitive but action-distribution weak.
future_action_variety_proxy was broad action-causal but reducible to action labels.
Clean-room FOPC contract was not authorized.
```

## Ledger Rules

```text
Failures are append-only.
Failure artifacts must remain linked.
Successor theories must cite relevant failed claims.
Failure cannot be rebranded as partial support unless the unsupported claim is explicitly removed.
```

Structured entries live in `theories/failed_claims.yaml`.


## ONE-GATE-FUTURE-ONLY-NON-CIRCULAR-EVIDENCE-HARNESS-001A (cb95bbd) — downgraded

Anchor: commit `cb95bbdb06c9fadbbbf7765ae61acc46609ed994`,
tag `remote-anchor-one-gate-future-only-non-circular-evidence-harness-001a-cb95bbd`.
Linked artifacts: `artifacts/one_gate_future_only_non_circular_harness_001a/`.
Source of record: independent read-only audit (no harness change, no repair).
Claim ceiling: future-only non-circular evidence-harness preflight only.

Bounded conclusion:

```text
cb95bbd future-only harness removes candidate declaration / producer-selection
control, but fails non-circularity because candidate-authored policy_map controls
ground truth. It must not be used as a Gate evidence contract.
```

Reproduced bypass (same evaluator, no second logic path):

```text
Hold observations and actions fixed, change only candidate serialized_state.policy_map:
  self-endorsing map -> score 1.0 / admitted; flipped map -> blocked.
  The candidate controls the score value and admission through a field that is
  not on the leakage name-list.
Degenerate all-"approach" self-consistent fixture -> candidate score 1.0 and
  majority baseline 1.0 (baseline equivalence), still admitted; run-level
  acceptance gates all pass (baseline non-equivalence is not gated).
Leakage scanner is name-based; policy_map/signal carry the answer key under
  non-listed names (0 hits); its positive control scans a hardcoded dict and is
  structurally always true.
```

What it does establish (bounded, not inflated): name-level blocking of
candidate-declared score/digest/verdict/producer/baseline/ablation/leakage/replay;
harness-owned metric registry (no candidate callable injection); a genuine ablation
rerun; single evaluator path; reproducible artifacts.

Next route (does not repair the harness):

```text
Run a separate independent-ground-truth preflight for the intended Gate target.
If no harness-owned / candidate-inaccessible truth source exists, downgrade this
Gate evidence route instead of repairing the harness again.
```

This is bounded offline audit evidence only. It does not prove or disprove any
Gate, mechanism, autonomy, agency, consciousness, or EGO/runtime readiness.
