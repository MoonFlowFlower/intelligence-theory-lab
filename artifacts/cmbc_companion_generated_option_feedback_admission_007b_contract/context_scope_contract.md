# Context Scope Contract

context_scope must be explicit and traceable for every pending or admitted
feedback state.

Required properties:

- scope identifier
- scope kind
- source trace refs
- feedback refs
- option refs
- whether the scope is local, narrowed, session-level, or rejected as too broad

Rules:

- bad_timing and intrusive feedback must be context scoped.
- global feedback application is a stop condition.
- a single local negative feedback item must not globally suppress companion-like options.
- later correction must narrow context rather than globally overwrite the prior.
- option lineage must inherit pending/admitted feedback state for its context.

The selector may see only non-semantic scope handles needed for admission-filtered
effect selection. It must not see semantic labels or natural-language context
descriptions.
