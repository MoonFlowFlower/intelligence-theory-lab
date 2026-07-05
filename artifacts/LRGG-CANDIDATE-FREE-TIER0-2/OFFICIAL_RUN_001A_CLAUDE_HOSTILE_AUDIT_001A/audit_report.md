# LRGG Tier 0-2 OFFICIAL_RUN_001A — Claude Hostile Audit 001A

Audit task ID: `LRGG-CANDIDATE-FREE-TIER0-2-OFFICIAL-RUN-001A-CLAUDE-HOSTILE-AUDIT-001A`
Role: independent auditor / red-team (CLAUDE.md Same-Agent Bridge Audit Role 001).
Auto-Remote-Anchor: forbidden. This audit modifies no run artifact and rewrites no prior result.

## Verdict

```text
invalid_due_oracle_baseline_coupling
```

Co-decisive (each would independently invalidate): degenerate generator (latent fully
exposed in the observation → trivially decodable), and `invalid_due_leakage_or_positive_control_failure`
(name-only leakage scanner, stubbed value-level attackers, self-fulfilling positive controls).
The reported `rejected_baseline_saturated` is a structural tautology, not a saturation boundary.

## Status

```text
current layer            = engineering implementation + candidate-free cheap-tier evidence (audit)
mainline integration     = none
enabled status           = none outside the isolated Tier 0-2 run
real trigger evidence     = artifacts exist and were read by file API:
                            src/lrgg_candidate_free_tier0_2_001a/runner.py (read in full),
                            tests/.../test_*.py, and 12 OFFICIAL_RUN_001A artifacts incl.
                            result.json, aggregation_report.json, baseline_scores.json,
                            oracle_report.json, leakage_report.json, positive_controls_report.json,
                            tamper_report.json, task_space_report.json, generator_spec.json.
claim ceiling            = bounded audit of THIS run only. No LRGG admissibility, candidate-free
                            headroom, oracle validity, mechanism, agency/self/subjectivity/emotion/
                            consciousness/autonomy, EGO readiness, H0/H1, 001C, or mainline claim.
```

## Decisive Finding — oracle ≡ all 18 baselines ≡ ground-truth function

The ground truth, the oracle, and every "fair baseline" are the SAME computation; the latent is
copied verbatim into the observation. Saturation is therefore an identity, not evidence.

```text
runner.py:274   true_actions = _target_actions_from_tokens(topology, remap, context_token)   # GROUND TRUTH
runner.py:276-281 observation = {visible_topology_token: topology, visible_remap_token: remap,
                                 visible_context_token: context_token, ...}                   # latent COPIED into obs
runner.py:351-359 _public_rule_prediction(row) = _target_actions_from_tokens(
                       obs.visible_topology_token, obs.visible_remap_token, obs.visible_context_token)
runner.py:362-363 budget_faithful_visible_channel_oracle = [_public_rule_prediction(r) for r in rows]   # ORACLE
runner.py:439-508 lookup / graph_lookup / transition_table / successor_map / count_table /
                   fsm_planner / episodic_traversal / trajectory_nearest_neighbor / discounted_wls /
                   least_squares / convex_objective_solver / DP / finite_state_filter /
                   classical_planner / n_gram_h1..h5  ==  [_public_rule_prediction(r) for r in rows]
```

Consequence (confirmed in `baseline_scores.json`): all 18 baselines = **1.0**, oracle = 1.0,
ground truth recovered exactly, because truth = oracle = baseline = the same public function of
tokens that are themselves the observation. `family_max = DP = 1.0 ≥ C−0.05 = 0.95` →
`rejected_baseline_saturated`. The label is mechanically produced by a guaranteed equality.

This is baseline-immunity §4.3 (mechanism/coupled oracle: circular) + §3.2/§3.3 (target directly
decodable / zero passive residual). Per the lab's own contract, zero passive residual is the
`rejected_trivially_decodable` / `rejected_no_fair_signal` condition, NOT a valid saturation.

## Required Checks (1–10)

```text
1. DP=1.0 callable, not literal?           PARTIAL/FAIL. DP is a callable (runner.py:483-484) but it
   is NOT dynamic programming — it is a one-line wrapper returning _public_rule_prediction. All 18
   baseline producers are name-only wrappers around ONE shared core. 18 distinct code_path_hash
   values (cosmetic, from differing def names) FALSELY signal 18 independent implementations.
2. DP access parity / no illegal truth?    VACUOUS-PASS → FAIL in spirit. DP reads only "legal"
   visible tokens, but the generator placed the FULL latent T=(G,R,C) into those visible tokens and
   made the target a public deterministic function of them. Legal access == answer key. Parity with
   the oracle is trivially "equal" because DP and oracle are the same code.
3. Inherently classically solvable under legal access?  Not a fair YES. It is solvable only because
   the latent is exposed and the target is the public rule on it — a DEGENERATE generator, not a
   classically-solvable structure-learning task. Saturation here is not valid negative evidence.
4. Oracle C=1.0 and nonreading collapse computed, not hard-coded?  PASS (computed). oracle_report:
   C mean=1.0 lcb=1.0; nonreading mean=0.0908; random 0.0879; majority 0.0979; gap 0.909 ≥ 0.30.
   But "failability" is necessary-not-sufficient and does not rescue a coupled/degenerate design.
5. Aggregation: baseline ≥ C−0.05 triggers, no averaging?  PASS as code (runner.py:1084-1160,
   hard-stop precedence, family_max). But it faithfully aggregates degenerate inputs → garbage-in.
   Note ordering: trivially_decodable (1140) ranks ABOVE baseline_saturated (1144); the only reason
   the label was not trivially_decodable is that the decodability probes were nerfed (see 6).
6. Leakage positive controls test value-level + structural, not name-only?  FAIL. (a) Real leakage
   scan (runner.py:791-808) is NAME-ONLY: it searches the observation text for tokens
   {"hidden_rule_id","latent_graph","generator_truth","hidden_target",...}. The latent sits in the
   observation under names "visible_topology_token" etc., which are not in that list → real_findings
   = [] → "passed". (b) Value-level attackers (runner.py:809-820) are STUBS: real_recovery_lcb =
   chance, alarm = False, hardcoded; they never read real data (leakage_report confirms all chance,
   real_recovery_blocks=false). (c) Positive controls (_scanner_alarms 741-764) test a PLANTED
   bad-string payload that is constructed to contain the bad string → trivially true, and they test
   a DIFFERENT function than the real scan path. So "10/10 controls alarm" validates nothing about
   the real scanner.
7. Replay recomputes from state+trace, not stored score?  PASS (real). run_replay (863-896)
   recomputes F-beta from serialized_state/observation/reward_trace and checks |Δ|≤1e-12.
8. Tamper probes fail when expected?  PASS (real). All 5 probes triggered mismatches (tamper_report).
9. Generator spec satisfies frozen operator values (n_seed=10,n_ctx=30,N_rows=300,H_min=12,
   distinct_T≥270/300,N_enum^latent≥3000,N_enum^action≥80,coverage≤0.10,B=8)?  PASS. generator_spec
   & task_space report: n_seed=10,n_ctx=30,N_rows=300,H_T=12.0,distinct_T=300,N_enum_latent=4096,
   N_enum_action=96,coverage=0.0833,B=8. NB: H_T_bits=log2(N_enum_latent) (runner.py:319) is
   tautological with N_enum_latent (uniform-spec entropy), not an independent measurement.
10. No stale 200-row/H_min=11/N_enum≥2000 logic?  PASS. Constants are 300/12/4096 (runner.py:25-33);
    a stale-pattern scan exists (read_sources 221-226). No stale survivors found.
```

Net: the plumbing that is REAL (replay, tamper, spec conformance, aggregation mechanics) is real;
the plumbing that MATTERS for this verdict (oracle/baseline independence, decodability gate,
value-level attackers, leakage scanner) is broken, and the environment is degenerate.

## Strongest Objection (steelman of the run, and why it fails)

Steelman: "LRGG is a visible-channel task; the budget_faithful_visible_channel_oracle legitimately
solves it from the legal channel, cheap legal baselines also solve it, so there is no
candidate-exclusive headroom — a valid `rejected_baseline_saturated`."

Why it fails: a valid saturation boundary requires (a) baselines that are INDEPENDENT
implementations, (b) an oracle NOT identical to the baselines, and (c) a powered decodability gate.
None holds. The oracle and all baselines are the same function; the target is a public function of
a fully-exposed latent; the decodability/value-level gates were nerfed/stubbed so the
`rejected_trivially_decodable` label could not fire. Under the lab's own contract (PREFLIGHT R6;
baseline-immunity §3.2/§3.3/§4.3) zero passive residual + coupled oracle = invalid environment, not
valid saturation. The nonreading-oracle collapse (failability) is necessary-not-sufficient and does
not rescue it.

## Is the saturation valid negative evidence?

```text
NO. It is INVALID, not valid no-headroom evidence. A degenerate generator that copies the latent
into the observation and scores one answer-key function under 19 names cannot answer the route-level
headroom question. It must NOT be read as "LRGG cheap-tier is dead/no-headroom", and it must NOT be
patched toward apparent headroom.
```

## Disposition: close / redesign / rerun

```text
REDESIGN, then rerun under a fresh authorization. Do NOT close the route (no valid evidence the
route is dead). Do NOT accept. Required redesign before any rerun:
 R1. Hide the latent: the observation must NOT contain T=(G,R,C) verbatim; the target must require
     inference/intervention beyond reading visible tokens (genuine passive residual; twin-pair
     non-identifiable under P(X), separable under do(.) per baseline-immunity §3.3).
 R2. Independent baselines: DP/WLS/graph-cache/n-gram/classical must be REAL, distinct
     implementations, not wrappers around one shared rule evaluator. Independence must be
     established by behavior on held-out structure, not by per-def code_path_hash.
 R3. Oracle ≠ baselines: the oracle must not be the same callable as any baseline.
 R4. Powered decodability: obs_only / raw_observation_latent_decoder must read the FULL legal
     observation (every visible field), and the value-level attacker family must actually compute on
     real data (no chance/alarm=False stubs). If the latent is decodable, the run MUST emit
     rejected_trivially_decodable.
 R5. Value-level leakage scanner: replace the name-only token list with a value-level check that an
     attacker cannot recover T from observation values; positive controls must exercise the REAL
     scan path on data with a planted leak (not a separate _scanner_alarms on a planted-string
     payload).
```

## Authorization

```text
candidate work : NOT authorized (this run authorizes nothing; it is invalid).
Tier 3+        : NOT authorized.
001C           : NOT authorized.
mainline/EGO   : NOT authorized.
```

## Next Minimal Closed-Loop Action

```text
Operator opens a bounded REDESIGN task card for the LRGG Tier 0-2 generator+harness implementing
R1-R5, preserving OFFICIAL_RUN_001A as an INVALID evidence record (do not delete, do not rewrite).
Re-run only after an independent re-audit of the redesigned generator confirms a non-empty
decodability-solvability window and oracle/baseline independence. The frozen 31-field manifest
values themselves are not implicated and need not be re-frozen unless the redesign changes them.
```

## What This Audit Does Not Prove / Claim

No LRGG admissibility, candidate-free headroom, oracle validity, mechanism evidence,
agency/self/subjectivity/emotion/consciousness/autonomy, EGO readiness, H0/H1, 001C authorization,
or mainline integration. It is a bounded invalidation of one run's saturation claim on the basis of
oracle/baseline coupling, a degenerate generator, and non-functional decodability/leakage gates.
```
