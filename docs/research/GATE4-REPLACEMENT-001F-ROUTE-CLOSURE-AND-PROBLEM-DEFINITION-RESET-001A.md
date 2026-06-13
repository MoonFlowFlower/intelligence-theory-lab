# GATE4-REPLACEMENT-001F Route Closure And Problem-Definition Reset

Task ID: GATE4-REPLACEMENT-001F-ROUTE-CLOSURE-AND-PROBLEM-DEFINITION-RESET-001A

Mode: Governance-only closure and problem-definition reset.

This document summarizes the closure artifact at:

```text
artifacts/gate4_replacement_001f_route_closure_and_problem_definition_reset_001a/
```

## Decision

001D-derived Gate4 replacement repair attempts are closed.

001E is preserved as negative evidence because faithful non-mechanism decoders
tied the 001D candidate:

- candidate score: `1.0`
- `pair_count_table`: `1.0`
- full-bundle decoder: `1.0`
- serialized-state decoder: `1.0`
- strongest faithful baseline: `pair_count_table`
- stop condition: `pair_count_table_tied_candidate`

This means the 001D route failed structurally. The target was recoverable from
faithful task encodings, so future work must reset the Gate4 problem definition
instead of patching the same harness.

## Closed Route

Closed:

- continuing to patch 001D;
- 001D-derived puzzle/bundle repair attempts;
- puzzle variants that preserve target-bearing encodings under renamed fields;
- hiding target-bearing serialized fields from baselines while the candidate
  keeps equivalent access;
- weakening query-capable or feedback baselines;
- candidate-specific puzzle construction.

001D remains historical bounded evidence. 001E controls future interpretation
as baseline-equivalence negative evidence. Neither artifact is rewritten by this
closure.

## Forbidden Future Fixes

Future Gate4 replacement work must not use:

- encryption;
- obfuscation;
- language/runtime switching;
- field renaming;
- hiding target-bearing serialized fields from baselines;
- weaker query-capable or feedback baselines;
- candidate-specific puzzle construction.

These moves do not create mechanism evidence. They either weaken auditability,
break fair baseline access, or preserve the same recoverable target behind a
different surface.

## Minimum Future Gate4 Requirements

Any future Gate4 replacement must satisfy all of the following before execution:

- target is not recoverable by faithful pair-count, bundle, serialized-state,
  trace-only lookup, or equivalent non-mechanism decoders;
- baselines receive fair information access;
- query-capable and feedback baselines match candidate affordances;
- positive-control leakage scanners fail when leakage is injected;
- replay recomputes from serialized state plus observation;
- ablations rerun episodes under real intervention;
- provenance records callable producers, source artifacts, run IDs,
  seed/context/episode IDs, aggregation rules, and code path hashes;
- 001E is cited as inherited negative evidence;
- claim ceiling blocks Gate5, admission, bridge, runtime, and EGO-mainline
  authorization.

## Recommended Next Route

Exactly one next route is recommended:

```text
close_001d_route_and_reset_gate4_problem_definition
```

The immediate successor, if separately requested, should be a bounded future
Gate4 design card under the reset constraints. It should not implement a new
experiment.

## Claim Ceiling

Allowed claims:

- route closure for 001D-derived Gate4 replacement attempts;
- problem-definition reset constraints for future Gate4;
- bounded governance readiness to draft a future Gate4 design card.

Forbidden claims:

- valid Gate4;
- social-latent inference;
- mechanism validity;
- agency;
- selfhood;
- consciousness;
- emotion;
- autonomy;
- EGO readiness;
- stable user benefit.

## What This Does Not Prove

This does not prove that a future Gate4 can pass, that any social-latent
mechanism is valid, or that any system has agency, selfhood, emotion, autonomy,
consciousness, EGO readiness, or stable user benefit.
