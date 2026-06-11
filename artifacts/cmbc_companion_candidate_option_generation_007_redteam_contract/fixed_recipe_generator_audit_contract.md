# Fixed Recipe Generator Audit Contract

Purpose: test whether generated CandidateOptions are a fixed hidden table rather than evidence-conditioned proposals.

Required future checks:

- vary allowed experience histories while keeping metadata stable
- mutate scenario/task/contract metadata and confirm generator behavior does not depend on it
- run at multiple option counts without N-specific branches
- compare option fingerprints across seeds, histories, and deleted evidence
- report `fixed_recipe_detected`

Stop if generated option sets are invariant under meaningful allowed evidence changes, depend on metadata IDs, require fixed `ACTION_HANDLES = 20`, or match a hidden recipe table.

