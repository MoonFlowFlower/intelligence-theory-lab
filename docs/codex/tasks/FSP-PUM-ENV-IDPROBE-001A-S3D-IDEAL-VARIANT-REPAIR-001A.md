# FSP-PUM-ENV-IDPROBE-001A — S3d Ideal Variant Repair 001A

Status: **AUTHORIZED bounded repair.** Isolated to `src/fsp_pum_env/factored_filter.py`
(+ minimal private helpers). Implements the exact ideal for the two cert-cell variants the
S1/S2 filter never supported, so S3d can execute. Does **not** change the frozen spec / ρ
definition / thresholds / 18-member set / cert cells, does **not** change any already-supported
variant's ideal, and does **not** run the battery (that is a separate re-run after this is banked).

## task id
`FSP-PUM-ENV-IDPROBE-001A-S3D-IDEAL-VARIANT-REPAIR-001A`

## problem definition
`FactoredExactFilter._compute_distribution_table` (factored_filter.py ~L280) has a deliberate
`raise ValueError("does not support variant ...")` for `FLAT_THETA` and
`RAG_SHOULD_WIN_STABLE_FACTS`. Spec §3 requires ρ anchored to a per-cell exact ideal for every
cert cell — discounted_LS→`flat_theta`, rag_k5→`rag_should_win_stable_facts`. The battery STOPped
(`STOP_UNEXPECTED_EXCEPTION`, banked separately) because the ideal is missing for those two cells.
Implement the exact ideal for both, mirroring the generator exactly.

## current stage
S1/S2 ideal-observer repair enabling S3d execution (Layer 2). Not a mechanism/subjectivity claim.

## what to implement (mirror the generator, do not invent)
- **FLAT_THETA** (generator: simulator.py FLAT_THETA branch pins `topics=(0,)*8`, `flags=(0,0)`;
  trust dynamics α/β/d unchanged): θ is a known constant, so there is **no θ uncertainty**. The
  ideal = the existing observation tables evaluated at the pinned θ over the existing trust grid.
  Add `_flat_theta_table(action)`; reuse the base table machinery at the fixed θ.
- **RAG_SHOULD_WIN_STABLE_FACTS** (generator: per-user `stable_fact_symbol` drawn once from
  `_rng("stable_fact:{user_id}")`; under `action=="recommend"` obs = `_peaked_distribution(
  stable_fact_symbol, strength=3.2)`; non-recommend actions behave as base, θ NOT pinned): add a
  **per-user categorical posterior over `stable_fact_symbol`** (alphabet_size dims), uniform init,
  updated **only** from recommend observations via the same peaked likelihood; θ posterior updated
  from non-recommend observations exactly as base (the two latents are independent). Recommend
  prediction = posterior-weighted mixture of `_peaked_distribution(candidate, 3.2)` over candidates.
  Add `_stable_facts_table(action)` + the posterior state; replace the two `raise` lines with
  dispatch to the new methods. Leave every other branch byte-identical.

## baseline / regression (BLOCKING)
Re-run the ideal on **every already-supported variant** (base/camouflage_off, constant_none,
constant_saturated, graph_cache low_diversity, NULL_env, probe_channel_off) and assert the result
is **bit-identical** to a pre-repair snapshot. In particular the banked one-eval-user
`camouflage_off` ideal metric MUST equal `0.09948462995337995` exactly, and the banked S2 /
variance-probe ideal values MUST be unchanged. Any drift → STOP (the repair leaked into the base
path). This is the guard that makes touching `factored_filter.py` safe.

## oracle-leakage audit (BLOCKING — stable_facts)
The stable-fact posterior must be inferable from **observations only**. Provide:
1. code/trace evidence the filter never reads `stable_fact_symbol` nor re-derives it from
   `_rng("stable_fact:...")` / any seed / any simulator truth (same oracle-boundary discipline as
   the existing filter_seed / z-marginalization work);
2. a **leakage probe**: two synthetic users with identical recommend-observation prefixes but
   different true `stable_fact_symbol` seeds must yield **identical** filter posteriors and
   predictions. If the filter's prediction depends on the hidden truth beyond what observations
   reveal → oracle leakage → STOP.

## ideal-sanity (BLOCKING)
On `flat_theta` and `stable_facts`: the exact ideal metric MUST be ≥ every battery member's metric
on that cell (an ideal beaten by a member is not ideal → STOP), and the ideal should itself achieve
high metric on the should-win cell. Report ideal-vs-each-member on both cells.

## trace / replay + evidence artifacts (under artifacts/FSP-PUM-ENV-IDPROBE-001A/)
`s3d_ideal_variant_repair_report.json` (per-variant ideal metrics, regression bit-identical table,
oracle-probe result, ideal-sanity table, code_path_hash, single_thread_env), a `trace` of the
ideal on the two new variants, `failure_manifest.json` if any BLOCKING gate fails, `claim_ceiling`.
Deterministic, replayable (independent filter seed, no master-seed/truth peeking).

## acceptance gate
Both variants run (no `raise`); regression bit-identical on ALL pre-existing variants; oracle probe
passes; ideal-sanity passes (ideal ≥ every member on both cells); NO change to frozen
spec / ρ / thresholds / 18-member set / cert cells / any already-supported variant's ideal; banked
STOP / probe / authorize artifacts byte-unchanged.

## claim ceiling
Enables S3d execution only. Produces **no** S3d certificate, NULL-env, environment-validity,
baseline-power, gap, mechanism, learning, agency, or EGO claim. The actual S3d evidence comes from
re-running `FSP-PUM-ENV-IDPROBE-001A-S3D-BATTERY-EXEC-001A` (unchanged, L=30 still signed) after
this repair is audited and banked.

## stop condition
STOP + failure_manifest if: any pre-existing-variant ideal changes (regression); oracle leakage
detected; ideal-sanity fails (a member ≥ ideal); `stable_facts` proves NOT exactly tractable within
bounded effort (report honestly — do NOT ship an approximate predictor labeled "ideal"); or any
frozen threshold/spec change would be required. Preserve every failure artifact; do not patch.

## rollback plan
Additive change to `factored_filter.py` (two table methods + posterior state; two `raise` lines
replaced by dispatch). Revert = restore the two `raise` lines. Isolated file; no other src touched;
no banked artifact modified. Codex runs no git.

## dev rules / forbidden
Modify only `factored_filter.py` (+ private helpers inside it). Do NOT change any already-supported
variant's output, the frozen spec, ρ, thresholds, cert cells, or the 18-member set. Do NOT read the
stable-fact seed/truth. Do NOT approximate the ideal and call it exact. Do NOT create a second logic
path used only by tests. Do NOT run git; emit an operator bank-ops proposal (HEAD-pin + reset +
allowlist + staged-count + zero-deletion + per-file Get-FileHash + scoped `git commit -- paths` +
no push) and STOP for Claude audit.
