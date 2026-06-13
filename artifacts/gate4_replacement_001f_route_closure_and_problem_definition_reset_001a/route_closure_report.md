# GATE4-REPLACEMENT-001F Route Closure And Problem-Definition Reset

Task ID: GATE4-REPLACEMENT-001F-ROUTE-CLOSURE-AND-PROBLEM-DEFINITION-RESET-001A

Mode: Engineering-governance / route-closure / problem-definition reset only.

This record does not implement a new Gate4 experiment. It preserves 001E as
negative evidence and closes 001D-derived puzzle/bundle repair attempts.

## Conclusion

The 001D-derived Gate4 replacement route is closed.

001E showed that the 001D target is recoverable by faithful non-mechanism
decoders:

- candidate score: `1.0`
- `pair_count_table`: `1.0`
- full-bundle decoder: `1.0`
- serialized-state decoder: `1.0`
- strongest faithful baseline: `pair_count_table`
- baseline equivalence: yes
- stop condition: `pair_count_table_tied_candidate`

The correct route is not to repair 001D in place. The correct route is to reset
the Gate4 problem definition so that future targets cannot be recovered by
faithful pair-count, bundle, state, trace-only lookup, or equivalent
non-mechanism baselines.

## Error In The Old Problem Definition

The old repair direction optimized the wrong question:

```text
Can the 001D candidate be patched until it beats the currently listed baselines?
```

The more important question is:

```text
Does the task require a mechanism that is not recoverable from faithful task,
bundle, state, feedback, or trace encodings by simpler decoders?
```

001E answered the second question negatively for the 001D route. That failure
is informative negative evidence, not a defect to patch around.

## Most Likely Wrong Abstraction

The most likely wrong abstraction was treating a puzzle/bundle harness as a
mechanism-discriminative Gate4 target while target-bearing information remained
recoverable from the candidate-visible or faithfully encoded surfaces.

If a pair-count table or serialized-state decoder can reconstruct the target,
then candidate success is not evidence of social-latent inference. It is
behavioral resemblance under an over-informative encoding.

## Strongest Objection

The strongest objection to this closure is that a future puzzle variant might
still be made less leaky. That is possible, but it does not justify continuing
001D-derived patching. Any future attempt must start from a reset problem
definition and must make non-recoverability by faithful decoders a precondition,
not a post-hoc diagnostic.

## Closed Route

Closed:

- continuing to patch 001D until it passes;
- 001D-derived puzzle/bundle variants that keep equivalent target-bearing
  encodings;
- candidate-specific puzzle construction;
- hiding target-bearing serialized fields from baselines while the candidate
  retains equivalent access;
- weakening query-capable or feedback baselines to recover candidate advantage.

This closure does not rewrite 001D. It preserves 001D as historical bounded
evidence and preserves 001E as the later adjudication that demotes the 001D
route to baseline-equivalent negative evidence.

## Better Mechanism Framing

Future Gate4 replacement work must test whether a candidate mechanism survives
against faithful, fair-access, callable non-mechanism baselines.

Minimum future framing:

- target is not recoverable by pair-count, bundle, serialized-state, trace-only
  lookup, or equivalent decoders;
- candidate and baselines receive fair information access;
- query-capable and feedback baselines match candidate affordances;
- positive-control leakage scanners fail when leakage is injected;
- replay recomputes from serialized state plus observation;
- ablations rerun episodes under real interventions;
- provenance records callable producers, source artifacts, run IDs,
  seed/context/episode IDs, aggregation rules, and code path hashes.

## Decision

Recommended next route:

```text
close_001d_route_and_reset_gate4_problem_definition
```

This is the only recommended route. It allows a future governance task to draft
a new Gate4 design card under the reset constraints. It does not authorize
implementation, experiment execution, Gate5, admission, bridge, runtime, or
EGO-mainline work.

## Minimal Validation Used

Only lightweight source/readback checks were used:

- local HEAD readback;
- remote branch readback;
- remote tag readback;
- 001E result readback;
- 001E baseline-equivalence report readback;
- 001E recoverability adjudication readback;
- 001D result and strongest-baseline readback;
- SHA-256 source pinning for selected source artifacts and docs.

No tests, experiments, datasets, source modules, harnesses, or scoring code were
created or rerun.

## Failure Signals

The closure framing would fail if:

- 001E did not preserve baseline equivalence as negative evidence;
- 001E did not show the candidate tied by faithful non-mechanism baselines;
- the stop condition were not `pair_count_table_tied_candidate`;
- prior 001B/001C/001D/001E artifacts were mutated;
- this task started implementing a new Gate4 experiment.

None of those stop conditions was observed in this governance record.

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

This does not prove that a future Gate4 can pass. It does not prove that any
candidate mechanism is valid. It does not prove subjectivity, agency, autonomy,
emotion, selfhood, consciousness, EGO readiness, or user benefit.
