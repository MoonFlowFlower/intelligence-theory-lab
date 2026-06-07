# Renderer Dependency Audit

{
  "interpretation": "Renderer dependencies would block a user-visible expanded demo, but they are post-selection and did not cause the 004 selector-visible candidate count to remain seven. A future contract needs a renderer adapter that maps selected anonymous options after selection without leaking semantic labels back to the selector.",
  "renderer_does_not_control_action": true,
  "renderer_reads_selected_action": true,
  "renderer_runs_after_selection": true,
  "renderer_static_dependency_blocks_expansion": false,
  "requires_parametric_post_selection_renderer_adapter": true,
  "static_points": [
    "CompanionRenderer.render indexes PUBLIC_ACTION_NAMES[selected_action]",
    "LabOnlyRenderer.templates are keyed by act_0..act_6",
    "LabOnlyRenderer.renderer_input includes public_action_name after selection"
  ]
}
