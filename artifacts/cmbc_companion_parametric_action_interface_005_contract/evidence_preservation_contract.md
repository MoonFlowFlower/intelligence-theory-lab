# Evidence Preservation Contract

Status: contract-only.

## Preserved Evidence

003 remains bounded small-action-set evidence under the current 7 anonymous action handles. It is not rewritten as parametric evidence.

004-EXECUTE remains preserved negative evidence:

`small_action_set_only`

004-RCA remains preserved diagnosis:

`selector_static_action_handle_bottleneck_confirmed`

## Future Shadow Path

A future shadow adapter may compare N=7 parametric traces against prior 003 traces. That comparison is a compatibility check only.

## Forbidden Rewrites

- Do not rewrite 003 as parametric evidence.
- Do not delete 004 failure artifacts.
- Do not reinterpret `small_action_set_only` as a pass.
- Do not patch selector or thresholds to align old and new traces.
- No selector patch is authorized.
- Do not use old public action names as selector-visible fields.

## Required Reporting

Future shadow implementation must report:

- old trace IDs used for compatibility
- mapping from preserved old anonymous handles to new opaque option IDs
- replay match rate
- distribution delta
- any selected-action mismatch
- whether mismatch is due to adapter, model, trace schema, or selector behavior
