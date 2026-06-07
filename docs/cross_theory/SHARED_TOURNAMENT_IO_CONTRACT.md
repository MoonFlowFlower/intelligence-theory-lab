# Shared Tournament I/O Contract

All non-oracle competitors in the cross-theory tournament must use the same public I/O. This prevents a theory from winning because it received better information.

## Allowed Inputs For Non-Oracle Competitors

- Public observations.
- Anonymous action handles.
- Own intervention history.
- Observed outcomes.
- Non-semantic goal vector when applicable.
- Non-semantic constraint vector when applicable.
- Horizon and budget.
- Public uncertainty or confidence outputs only if derived from allowed data.

## Forbidden Inputs For Non-Oracle Competitors

- Semantic action labels.
- Semantic goal labels.
- Object names.
- Entity names.
- Scenario ID.
- Task ID.
- Contract ID.
- Cycle ID.
- Hidden latent state.
- Hidden future state.
- Oracle transition table.
- Oracle causal graph.
- Oracle plan table.
- Evaluator metric values.
- Expected output table.
- Baseline outputs.

## Oracle Exception

`T10_OracleDiagnosticUpperBound` may use hidden/oracle information only as a diagnostic upper bound. It must never be counted as a valid competitor and must never be used to infer LCC collapse or LCC loss.

## Equality Rule

Every non-oracle competitor must receive the same observation/action/history/goal/constraint/horizon/budget information at the same decision point. Any unequal information access invalidates the tournament.

## Provenance Rule

Every competitor decision must produce a public provenance record listing the allowed public fields used. Behavior-only replay must reconstruct decision evidence without hidden metadata, semantic labels, evaluator metrics, expected outputs, or competitor outputs.
