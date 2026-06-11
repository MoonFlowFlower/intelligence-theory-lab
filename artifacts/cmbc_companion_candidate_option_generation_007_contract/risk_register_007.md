# Risk Register 007

## Generator Becomes Selector

Risk: proposal ranking or generator rationale becomes the actual control path.

Mitigation: generator may only emit proposals; selector receives only admitted anonymous payloads after admission.

## Semantic Leak

Risk: natural-language descriptions, semantic labels, RAG text, or renderer text leak into selector-visible payloads.

Mitigation: schemas separate generator-visible text from selector-visible payload.

## Lineage Theater

Risk: options are admitted with shallow lineage that cannot support deletion, replay, or reversal.

Mitigation: every admitted option requires lineage and evidence support references.

## Baseline Weakening

Risk: baselines receive less information than CMBC.

Mitigation: baseline contract requires equivalent allowed inputs.
