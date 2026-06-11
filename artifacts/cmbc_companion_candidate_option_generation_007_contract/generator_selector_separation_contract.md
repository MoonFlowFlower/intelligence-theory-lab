# Generator Selector Separation Contract

Generator may propose options but cannot select actions.

Selector receives only admitted anonymous CandidateOptions.

natural-language descriptions are forbidden selector-visible fields.

semantic labels are forbidden selector-visible fields.

The generator may create `CandidateOptionProposal` records. It may not rank options for execution, choose the final option, write directly to the action distribution, alter thresholds, or send text to the renderer as an action command.

The selector consumes only `AdmittedCandidateOption.selector_visible_payload` records after admission.
