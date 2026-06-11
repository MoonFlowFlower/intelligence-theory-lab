# Cross-Theory Redteam Gates

Every non-oracle competitor must pass the same redteam gates. A competitor may not win, tie, or cause LCC collapse if it fails a shared gate.

## Required Gates

- Action-label leak scan.
- Semantic goal-label leak scan.
- Object/entity-name leak scan.
- Scenario/task/contract ID mutation.
- Hidden-state leak scan.
- Evaluator-metric leak scan.
- Oracle-transition / oracle-plan scan.
- Behavior-only replay.
- Independent trace-only scorer.
- Candidate freeze before blind holdout generation.
- No code changes after holdout generation.
- Strong baseline equivalence check.
- Negative controls.

## Shared Application Rule

These gates apply to every non-oracle competitor, including LCC. OracleDiagnosticUpperBound is diagnostic-only and cannot bypass gate failure for any valid competitor.

## Gate Failure Consequence

If a competitor fails a leak, metadata, oracle, behavior-replay, freeze, or negative-control gate, its behavioral score cannot count toward a theory win. The tournament must report the failure mode separately.

## Anti-Shortcut Mutations

Future execution must include mutations of:

- Anonymous action handles.
- Non-semantic goal vectors.
- Scenario/task/contract metadata hidden from candidates.
- Identity/self-report fields.
- Object/entity names hidden from candidates.
- Expected-output fields hidden from candidates.

Behavior changes caused by hidden or forbidden fields invalidate the competitor.
