# LRGG-CANDIDATE-FREE-TIER0-2 Collision Record

Task ID: `LRGG-CANDIDATE-FREE-TIER0-2-IMPLEMENTATION-RUN-001A`

Current layer: engineering implementation + candidate-free cheap-tier evidence generation.

Real objective: execute only the isolated Tier 0-2 candidate-free cheap-tier plumbing run, preserving all cheap-baseline, leakage, replay, provenance, and tamper blockers as fail-able outcomes.

Problem definition check: the task is not candidate implementation and not an admissibility/headroom decision. It is a debug split that can only show cheap-tier plumbing did or did not avoid immediate cheap-tier blockers.

Strongest baseline explanation: a legal-access lookup, graph-cache, n-gram, classical planner, direct optimizer, or trajectory-nearest-neighbor baseline may match the visible-channel oracle under the same budget.

Strongest invalidity risk: the environment may leak the latent rule or target through observations, serialized state, filenames, source paths, reward shaping, membership, or task identifiers, making any score a trivial decode rather than fair signal.

Falsification signal for current framing: any cheap baseline reaches `C-0.05`, a trivial predictor reaches `C-0.05`, positive-control leakage fails to alarm, replay cannot recompute from serialized state plus trace, or a tamper probe fails to trigger mismatch.

Insufficient evidence even if non-blocked: a non-blocked Tier 0-2 run is only plumbing evidence for this debug split. It is not LRGG admissibility, not candidate-free headroom, not mechanism evidence, not 001C authorization, and not EGO readiness.

## Candidate Approaches

### 1. Minimal Implementation

- Evidence produced: one callable generator, one oracle, one cheap baseline panel, leakage scan, replay check, tamper checks, and aggregation artifacts.
- Strongest cheap baseline that could match it: lookup or graph-cache can read legal channel structure and match the oracle.
- Leakage or hard-coding risk: high if targets are encoded directly in observations or serialized state without scanner coverage.
- Smallest falsifying test: force graph-cache baseline to oracle score and verify `rejected_baseline_saturated`.
- Expected failure mode: saturated cheap baseline or positive-control leakage miss.

### 2. Strongest Baseline / Shortcut Explanation

- Evidence produced: family-max cheap-baseline saturation analysis with graph-cache, lookup, n-gram, direct optimizer, and classical families.
- Strongest cheap baseline that could match it: any legal-access exhaustive or cache baseline under coverage `B / N_enum^action <= 0.10`.
- Leakage or hard-coding risk: medium if family baselines share oracle internals instead of independent callable producers.
- Smallest falsifying test: disable or corrupt one required family and verify aggregation refuses to proceed.
- Expected failure mode: `rejected_baseline_saturated`.

### 3. Mechanism-Faithful Candidate-Free Plumbing

- Evidence produced: no candidate mechanism; only frozen generator/spec, visible oracle, cheap-tier baselines, positive controls, replay recomputation, tamper mismatch, and provenance rows.
- Strongest cheap baseline that could match it: legal-access planner or trajectory nearest-neighbor if the task is locally enumerable or observation-decodable.
- Leakage or hard-coding risk: low if generator truth is separated from legal observations and positive controls cover values and structure.
- Smallest falsifying test: mutate observation, reward, source byte, hidden graph, or one action and verify declared score/replay/hash mismatch.
- Expected failure mode: invalid task space, no fair signal, baseline saturation, or tamper/replay invalidity.

## Selected Approach

Use approach 3 with explicit family-max baseline rejection from approach 2. The implementation must prefer rejection over positive-looking claims when a cheap legal-access baseline saturates. A non-blocked result may only emit `cheap_tier_plumbing_valid_not_saturated__proceed_to_separately_authorized_heavier_tiers`.

## Bounded Audit

- Tests mechanism or behavioral resemblance: only cheap-tier executable plumbing and baseline/debug discrimination, not mechanism validity.
- Hard-coding check: aggregation and blockers must be callable and based on computed scores, not static verdict dictionaries.
- Local optimum check: no threshold tuning after outputs.
- Zeno trap check: if cheap baselines saturate, stop with rejection rather than repairing toward a proceeding verdict.
- Evidence leakage check: value-level and structural scanners require planted positive controls and real clean-scan outputs.
- Weak baseline check: family-max over all required cheap baseline families is mandatory.
- Schema split check: replay and official scoring must consume the same generated trace/state contract.
- Second logic path check: tests must exercise the same runner functions used by official artifact generation.
- Claim inflation check: final claim ceiling remains Tier 0-2 cheap-tier plumbing only.

Acceptance signal: required artifacts are generated from callable code paths, all positive controls and tamper probes are fail-able, final verdict is within the authorized verdict ceiling, and no forbidden mainline/candidate/remote-anchor action occurs.

Rollback plan: remove only `src/lrgg_candidate_free_tier0_2_001a/`, `tests/lrgg_candidate_free_tier0_2_001a/`, and `artifacts/LRGG-CANDIDATE-FREE-TIER0-2/OFFICIAL_RUN_001A/` if the user requests rollback.
