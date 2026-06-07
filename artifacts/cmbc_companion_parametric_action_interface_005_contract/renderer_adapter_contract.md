# Renderer Adapter Contract

Status: contract-only. No renderer implementation is authorized here.

## Boundary

The renderer adapter is strictly post-selection.

It receives:

- selected anonymous option ID
- public observation excerpt allowed for rendering
- prediction summary for the selected option
- prior support refs safe for display
- renderer style constraints

It must not feed any renderer output back into selector input.

## Required Guarantees

- rendered text is never selector input
- public action names are never selector input
- action family names are never selector input
- natural language action descriptions are never selector input
- adversarial renderer prompts cannot change `selected_option_id`
- renderer logs must include `selected_option_before_render` and `selected_option_after_render`

## Future Execution Gate

`renderer_action_change_rate` must remain `0.0`.

If the renderer changes selected option, future execution must stop with:

`renderer_adapter_contract_incomplete`

or:

`boundary_violation`
