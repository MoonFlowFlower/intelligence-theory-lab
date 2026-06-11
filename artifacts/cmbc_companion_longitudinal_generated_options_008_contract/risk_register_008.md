# Risk Register 008

## Primary Risks

- Generated options remain short-horizon artifacts and do not survive multi-session lifecycle tests.
- Retirement is decorative and retired options still influence selection.
- Near-duplicate options bypass pending/admitted feedback state.
- Feedback inheritance becomes global instead of context-scoped.
- Composition creates untraceable options whose source deletion cannot be audited.
- RAG or recency baseline matches longitudinal behavior because trial cases are too surface-level.
- Replay only reconstructs selected action, not lifecycle and admission state.

## Stop-Loss Rule

If future execution fails, do not patch selector, thresholds, baseline inputs, probe definitions, renderer, or generator to recover a pass. Run RCA on the specific failure family.

## Claim Ceiling

008 contract readiness does not authorize execution. Even a future 008 pass would remain bounded longitudinal generated-options evidence only.
