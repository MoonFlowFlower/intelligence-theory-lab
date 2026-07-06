# ROUTE-STATE-MACHINE-001B Current Frontier Gate

## Scope

This document records the ROUTE-STATE-MACHINE-001B local current-frontier gate.
It does not create a new mechanism roadmap, run a mechanism experiment, run
scoring, or authorize EGO runtime/mainline work.

## Layer

Engineering implementation layer: local route-governance validation and
artifact hygiene only.

## Current frontier registration

Registered current frontier:

```text
N2-SBMC-ENV-REDESIGN-001A
```

The registration is design/pre-registration only.

## Ledger source readback

`docs/research/FSP-STAGE-LEDGER.md` entry `L-014` supports the current-frontier
registration because it records `N2-SBMC-ENV-REDESIGN-001A` as a banked
design/pre-registration card, states the scout it supersedes, strengthens the
graph-cache challenger floor, and explicitly records: candidate-free preflight;
NO code/scoring in this bank.

This supports registering the route as the local current frontier for route
governance. It does not support mechanism validity, theory pressure, scoring, or
experiment execution.

## Gate requirements implemented locally

The validator must fail if:

1. `program_state.json` is missing;
2. `current_frontier_route_id` is missing;
3. the current frontier route directory does not exist;
4. the current frontier route is `TOMBSTONED`;
5. `program_state.allowed_next_actions` is empty;
6. `program_state.forbidden_next_actions` is empty;
7. `program_state.claim_ceiling.max` is missing;
8. a `REGISTERED` current frontier authorizes mechanism validity, theory
   pressure, scoring, or experiment execution;
9. `N2-SBMC-ENV-REDESIGN-001A` lacks source readback citing `L-014` or
   equivalent current ledger evidence.

## Claim ceiling

Local route-governance validation only. No mechanism validity, theory pressure,
scoring, experiment execution, agency, autonomy, subjectivity, consciousness,
EGO readiness, companion readiness, or mainline-effect claim.
