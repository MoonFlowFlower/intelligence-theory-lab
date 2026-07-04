# FSP-ENV-DESIGN-CONSTRAINTS-001A — Environment Validity Constitution

- Status: AUTHORIZED-BINDING (operator authorized N0 under this document, 2026-07-01, in-session). Canonical sha to be recorded at first commit (freeze ceremony, Stage 0 of the execution plan); from authorization onward the content is binding for N0 implementation and read-only in effect. FROZEN label + sha applied at commit.
- Mutation policy after freeze: supersede-only (001B / 002A with written justification). No in-place relaxation, ever.
- Layer: environment-identifiability governance. Applies to: N0 and all its Plan B/C redesigns, and to any future PUM / SBMC / RIA-extension environment design under the FSP program.
- Does not apply to: mechanism validity verdicts, and it cannot be cited as evidence for any mechanism, consciousness, agency, autonomy, or subjectivity claim.
- Claim ceiling: no mechanism evidence; preregistered design constraints only.
- Binding rule: during any implementation task governed by this document, modifying this document is a blocking governance-self-modification failure (mirror of the R-G bridge rule in CLAUDE.md). Auditors must check the sha, not the prose.
- Provenance: derived from FSP-ROUTE-PROGRAM-001A §"env design" discussion; reconciled with an independent external audit (GPT-5, 2026-07-01, user-supplied) whose accepted patches are integrated below and whose residual imprecisions are corrected in §2 and §10.

## 1. Constitutional statement

A test environment is not a task. It is a separation instrument. Its validity is defined by what it kills and what it spares:

- obs-decoder must die (and must win when camouflage is off);
- graph-cache must die (and must win when structure repeats);
- RAG/lookup must die (and must win when facts are stable and uncontradicted);
- discounted-LS must die where latents are conditional (and must win where they are flat);
- active probing must pay where probe-only information exists (and buy nothing where it does not);
- the ideal observer must survive;
- the NULL environment must show no headroom for anyone.

Difficulty is not value. An environment that is merely hard lowers everyone including the ideal; a valid environment creates gaps.

## 2. Definitions: parity and evaluation regimes

Interface parity, not trajectory parity. All systems (candidate, baselines) get: the same observation channels, the same action set, the same cost model, the same denial of hidden labels. Active systems will produce different trajectories than passive ones; that is permitted and is the point. Differences may come only from how a system selects actions, maintains belief, compresses history, and updates memory — never from permissions.

Dual evaluation regimes (every gap declares which regime it is measured in):

- LOG-PARITY regime: all predictor-class battery members (obs-decoder, LS, graph-cache, window/sequence models) are fitted and scored on the same frozen trajectory set, so they compete purely on conversion of identical data. Gap-1 and Gap-3 are measured here.
- ON-POLICY regime: policy-class systems (ideal-with-probes, ideal-without-probes, fixed-schedule probers, myopic-IG prober, candidate) each run under identical interface and budget and are scored on their own trajectories. Gap-2a and Gap-2b are measured here.

A comparison that silently mixes regimes is invalid.

## 3. The eight design laws (each with its enforcing test)

L-A. Advantage from information economics, never from permissions. Decisive information must be (i) extractable in principle from the public action-observation stream (ideal observer succeeds — no oracle coupling), (ii) not extractable by surface/lookup statistics (battery fails), (iii) extractable under the declared budget by belief maintenance + action selection. Enforced by: the Gap certificates (§4) + interface-parity contract (§5).

L-B. Three-gap-plus certification: no gap, no claim (§4).

L-C. Latents causally deep, not label-deep. Camouflage is the removal of marginal channels, not the addition of noise. Enforced by the latent-depth test hierarchy (§6).

L-D. An environment is a knobbed family, not a point. Every battery member has a should-win variant; the instrument's falsifiability is proven by the knobs (§7).

L-E. Evaluation queries are counterfactual and action-conditioned: predict P(user_response | history, candidate_action) and P(state_transition | history, candidate_action) under proper scoring rules (Brier/NLL, macro-balanced), with delayed noisy feedback. Static QA is insufficient. Reward alone is never a success signal: prediction quality and action quality must be reported separately, and mechanism claims attach to prediction quality first.

L-F. Interference and drift are the oxygen of memory claims. Without contradiction / drift / stale-memory traps, a memory-consolidation claim is not weak — it is structurally untestable (§8).

L-G. Replayability is a construction constraint enforced by interface shape, not discipline (§9).

L-H. Negatives carry power. equivalent ≠ inconclusive_underpowered ≠ invalid_instrument; MDE and power are preregistered (§10).

## 4. Gap-to-claim authorization matrix

| Gap | Definition (regime) | Certifies | Does NOT authorize |
|---|---|---|---|
| Gap-1 | ideal − fair_max (LOG-PARITY) | non-surface, non-lookup identifiability exists | any memory, active-probing, or subject-adjacent claim |
| Gap-2a | ideal-with-probes − ideal-without-probes (ON-POLICY) | action-conditioned information acquisition is necessary | complex epistemic planners (needs 2b) |
| Gap-2b | adaptive-active − best-cheap-active (ON-POLICY) | adaptivity of probing matters beyond fixed schedules/UCB | any specific EFE formulation (that is a candidate question) |
| Gap-3 | unbudgeted conditioner − budget-matched conditioner (LOG-PARITY) | persistence/compression under budget is necessary | any specific replay/consolidation mechanism (needs candidate ablation) |
| Gap-4 (SBMC) | detection with metadata-stripped/forged provenance − metadata-only verifier | semantic consistency checking is necessary beyond provenance engineering | self-boundary or self-state claims (route stays closed) |

Rule: no gap, no corresponding claim — a claim whose gap is uncertified is a structural violation, not a judgment call.

One-sidedness caveats (mandatory in any report using this matrix):
- Gap-2b is certified by a SUFFICIENT test only: myopic-IG-ideal is a lower bound of adaptive probing; if it beats the best fixed schedule, Gap-2b exists. If it does not, Gap-2b is "one-sided-untested", NOT "absent" — multi-step planned probing may still exceed fixed schedules. Full Bayes-adaptive certification is intractable in general and is not required.
- Gap-3's oracle-side proxy is the truncation-ideal (Bayes posterior on the declared budget-truncated history). The optimal-compression ideal is intractable; the truncation form must be declared in the frozen design. Gap-3 statements are therefore relative to the declared truncation family.

N0 verdict schema (anti-fragmentation rule): the task card's four top-level terminals stay authoritative (env_valid_headroom_certified / env_family_not_identifiable / invalid_integrity / inconclusive_underpowered). This constitution ADDS a mandatory `gap_certificates` vector {gap1, gap2a, gap2b, gap3} with values in {certified, absent, one_sided_untested}, plus a subtype code (§10). Combination terminals (e.g. "pass but cheap-active sufficient") are projections of the vector, not new schema.

## 5. Interface-parity and cost-model contract

```yaml
interface_parity_contract:
  observation_channels: same for candidate and all baselines
  action_set: same (policy-class members); predictor-class members are scored in LOG-PARITY regime
  cost_model:
    tokens_per_turn: metered, same cap
    probes: metered via in-env trust cost
    memory_reads: metered
    memory_writes: metered
    offline_compute: metered  # see below
  hidden_labels: unavailable to all non-oracle systems
  oracle_exception: upper bounds and positive controls only; oracle outputs never reachable by candidate or battery
  trajectory_parity: not required
  interface_parity: required
```

Offline-compute parity (binding): consolidation/replay compute is not free "sleep-time" compute. The candidate's offline budget B_off is declared, and every baseline is entitled to an equivalent B_off spent in its own idiom (B_rag may build better indices; B_summary may re-summarize; sequence baselines may re-fit). A Gap-3 or consolidation win purchased by unmatched offline compute is a parity violation, not evidence.

## 6. Latent-depth test hierarchy (order fixed; earlier tests are necessary, later tests are the gate)

1. Marginal-MI structural check (fast, necessary, not sufficient): for each latent dim θ_i and each declared feature family (single symbols, n-grams to order k, per-session aggregates — families preregistered), max I(θ_i; feature) ≤ δ, computed exactly on the symbolic alphabet. This check CANNOT clear an environment (XOR-style joint channels pass it); it can only fail one early.
2. Trained decoder gate (the real gate): a capable attacker family (multiple architectures, tuned, family_max reported) trained to decode θ from single sessions must stay ≤ the preregistered fair ceiling.
3. Camouflage-off positive control: same decoder family on the camouflage-off variant must reach ≥ its should-win threshold (proves the attacker is capable and camouflage is causal — fail-able in both directions).
4. Surface-remap generalization check: same latents, freshly randomized renderer; decoders trained on the old renderer must fail on the new one, while ideal-observer performance is invariant (proves θ lives in causal/action-history structure, not in surface statistics).

## 7. Should-win table (baseline capability certificates)

Every battery member must have a knob setting where it wins; a baseline that never wins anywhere is a straw man and invalidates the instrument, not the candidate.

```yaml
baseline_capability_certificates:
  obs_decoder:        {should_win: camouflage_off,                 required: ">= 0.80"}
  discounted_LS:      {should_win: flat_theta_monotone_prefs,       required: "approaches ideal"}
  passive_tracker:    {should_match_ideal: probe_free_variant}
  frozen_memory:      {should_match: no_drift_variant}
  graph_cache_family: {should_win: low_diversity_repeated_templates}
  rag_lookup:         {should_win: stable_facts_no_contradiction}
  hash_chain:         {should_win: provenance_only_tamper_task}     # SBMC
  oracle:             {should_win: direct_theta_access_PC}
  NULL_env_control:   {requirement: "theta independent of obs/probes => NO system shows headroom"}
failure_rule: any certificate failure => FAIL_BASELINE_UNDERPOWERED or FAIL_NULL_FALSE_HEADROOM (instrument invalid); candidate wins in the same run are void and may not be banked.
```

## 8. Interference taxonomy (required for any memory/consolidation-relevant environment)

```text
retrieval distractor:  embedding-similar but semantically superseded episodes
temporal distractor:   once-true, now-false facts (supersession required)
preference distractor: explicit preference later reversed by implicit evidence
```

Per-class directional requirements (preregistered): RAG degrades; PE-gated update helps; no-replay / frozen-memory fails. An environment with zero engineered interference cannot host a consolidation claim (L-F: untestable, not weaker).

## 9. Replay/trace hard requirements (execution-precondition checklist, not best practice)

```text
prediction-before-action committed to trace (an action without a prior committed prediction_json is a contract violation, not a data point)
prefix-only predictor interfaces (future inaccessible by construction)
all stochasticity through a logged RNG event stream
S_hash / M_hash before and after every step
memory write / revise / quarantine manifest
baseline output manifest (same run, same data)
no latent information in prompts, filenames, cache keys, trace ids, or fixture names
clean-room recomputation of all reported metrics from trace alone
```

## 10. Terminal vocabulary with routing

Top-level categories (authoritative, match the N0 card): PASS = env_valid_headroom_certified; FAIL = env_family_not_identifiable; INVALID = invalid_integrity; INCONCLUSIVE = inconclusive_underpowered.

Mandatory subtype codes:

```text
PASS_IDENTIFIABLE                     -> next: candidate card (N1); claims per gap_certificates only
PASS_PARTIAL (via gap_certificates)   -> e.g. {gap2b: absent|one_sided_untested}: N1 allowed, N1.5 claims capped or deferred
FAIL_SATURATED_BY_FAIR_BASELINE       -> next: structural redesign (Plan B/C); prohibited: any candidate run
FAIL_UNIDENTIFIABLE_EVEN_FOR_ACTIVE_IDEAL -> next: Plan C design-by-proof; else terminal bank
FAIL_ORACLE_INVALID                   -> instrument: fix ideal observer; no redesign budget consumed
FAIL_BASELINE_UNDERPOWERED            -> instrument: fix baseline; candidate/bank actions void
FAIL_LEAKAGE                          -> instrument: fix channel; leakage self-test must re-pass
FAIL_NULL_FALSE_HEADROOM              -> instrument: harness fabricates signal; all axis results void
INCONCLUSIVE_UNDERPOWERED             -> next: powered rerun per preregistered N; prohibited: interpreting direction
```

Each subtype's report must include: downstream route-weight update, allowed next card, prohibited claims. Never merge equivalent with inconclusive_underpowered: "no observed difference" at insufficient power is not equivalence; every equivalence verdict ships its MDE.

## 11. Fatal environment invalidators

Any of the following triggers INVALID (instrument), never candidate failure, and voids all same-run results:

```text
latent enters observation, filename, reward shaping, cache key, or prompt scaffold
static QA substituted for action-conditioned counterfactual prediction
LLM judge as primary metric
single-point environment (no knobs => no should-win controls => unfalsifiable instrument)
any baseline lacking its should-win certificate
difficulty produced mainly by rendering noise (lowers ideal without creating gaps)
threshold changed after seeing results
baseline deleted after failing to lose
candidate given a private tool/channel
future information leakage through trace shape or schema
offline-compute parity violation (§5)
regime mixing (§2)
```

## 12. Redesign invariants and ledger

Across all Plan B/C redesigns, immutable: claim ceiling; primary metric family; battery membership (additions allowed, deletions forbidden); threshold values and directions; max redesign count (2); terminal vocabulary; hidden-label denial; this document (supersede-only).

Mutable (with mandatory redesign-ledger entry: what changed, why, which failure signature triggered it): latent construction; renderer; probe channel and economy; drift/interference schedule; cost-model parameters; task-family composition.

## 13. What this document is not

Not mechanism evidence. Not a benchmark. Not a guarantee that any environment satisfying it will show headroom — it only guarantees that whatever N0 reports (pass or fail) will be interpretable, attributable, replayable, and safe to bank. The strongest claim this document can ever support: "the environment design constraints were preregistered and enforced."
