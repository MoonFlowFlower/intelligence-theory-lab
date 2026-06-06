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

