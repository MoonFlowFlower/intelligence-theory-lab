# CLAUDE Independent Hostile Audit — PHASE0-ENVIRONMENT-DESIGN-CONSTRAINTS-002C

Status: independent design-constraint audit (read-only). Not an enforcement harness.
Auto-Remote-Anchor: forbidden.

## Verdict

`accept_design_constraint_record_with_required_revisions_before_003a_authorization`

- Admissible as a recorded negative-lineage design-constraint synthesis: **yes**.
- Authorizes `BATCH-ENV-HEADROOM-SCOUT-003A`: **no**.
- Implementation may proceed: **no** — out of audit scope, and three required fixes (RF-1/2/3) should be closed before 002C is used as the 003A authorization basis.

## Research Layer

engineering-governance / Phase-0 environment design-constraint synthesis (audited read-only).

## Audit Scope And Claim Ceiling

Design-constraint audit only. This audit does not propose environment sketches, authorize 003A, authorize a route tournament, authorize candidate implementation, or wire any runtime/mainline/admission/bridge path. It cannot prove headroom, Gate1 pass, mechanism validity, candidate feasibility, agency, autonomy, consciousness, emotion, stable user benefit, or EGO readiness.

## Method / Real Trigger Evidence

- 002C `.md` and all five JSON artifacts (`failure_taxonomy`, `design_constraints`, `forbidden_surface_patterns`, `required_positive_properties`, `next_batch_generation_brief`) read via the authoritative file-API. The bash mount initially returned a stale directory listing that omitted the freshly-written 002C; per the repo's FUSE-truncation lesson, a whole-mount sweep + file-API Read were used as authoritative.
- All ten provenance sources cited by 002C confirmed to exist on disk.
- 002C's preserved F002B sub-scores cross-checked against `artifacts/batch_env_headroom_scout_002b/rejected_sketches.json`: **verbatim match** (graph-cache 1.0/1.0/1.0/1.0; lookup 1.0/1.0/1.0/0.1667; underpowered oracle 0.333, strongest baseline = `budget_limited_belief_state_planner`; passive 0.375 / family_max 1.0).
- 001A and 002A headline verdicts + numbers matched against their closeouts verbatim.

## Answers To The Five Questions

**Q1 — Preserves 001A no-headroom, 002A false-promotion, 002B all-rejected?** Yes. All three are preserved accurately, including verbatim numeric sub-scores verified against source artifacts. Everything is framed as bounded negative environment evidence; 001A is correctly kept as an environment/surface failure, not candidate failure. Nothing is upgraded, reinterpreted as stronger, or patched into a pass. **Pass.**

**Q2 — Forbidden patterns complete enough to block A1-A9?** All nine families are enumerated, mapped by family id, and given `forbidden_if` + `rejection` + required baselines, plus an extra `S1` underpowered-oracle family beyond the attack library. The one substantive completeness gap: there is no first-class forbidden family for **active budget-faithful planner saturation** (`budget_limited_belief_state_planner` / greedy info-gain planner), even though the belief-state planner was the strongest fair baseline that saturated 001A (margin 0.0) and surfaces again as a strongest-cheap-baseline in 002B. It is in `baseline_battery_minimum` but not in the explicit promotion gates, positive properties, or forbidden patterns. **Pass on A1-A9 naming; required fix RF-1.**

**Q3 — Positive properties real constraints or slogans?** Mostly real. P001-P011 each carry a `minimum_pre_run_evidence` field that operationalizes them; `requires_preliminary_gap_min = 0.08` is pinned and band 0.03 inherited; promotion gates name exhaustive_legal_query / fitted_learner / graph_cache_family_max below oracle-minus-band. The single load-bearing slogan is the top-level positive-grammar summary ("oracle earns score through budget-faithful information gathering"), under-specified exactly where it matters (see RF-2). Some floors are deferred to 003A but predeclaration-before-run is required. **Pass with required fix RF-2.**

**Q4 — Weakens baselines or licenses optimize-until-pass?** No. 002C strengthens the battery (adds the active planners and the closed decoders), explicitly forbids manufacturing headroom by weakening/omitting/aliasing/underpowering, forbids reopening or optimizing the closed MINIMAL-ENV-SPEC-001A, requires pre-registration of the strongest false explanation and A1-A9 mapping before any run, and caps batch size. It does not license per-surface optimize-until-pass. Residual (non-blocking): no cross-batch survivorship / multiple-testing control. **Pass with non-blocking finding NB-2.**

**Q5 — Is `blocked_no_valid_environment_design_grammar` needed if no credible positive grammar exists?** Yes — needed and correctly fail-closed (two triggers, wired across four artifacts). The stronger point: because the proposed positive grammar is not yet separated from the belief-state planner that already saturated 001A, this stop verdict is plausibly the **expected** outcome, not a formality. Weakness: it is the only verdict in 002C with no mechanical trigger — it relies on an agent self-reporting that no non-cheating surface exists, and can be deferred indefinitely by running another batch. **Needed; required fix RF-3.**

## Blocking Issues

- Against recording 002C as a negative-lineage synthesis: **none**.
- Against using 002C to authorize 003A: **RF-1, RF-2, RF-3** below.

## Required Fixes (before 003A authorization)

- **RF-1 — Gate the active planner family explicitly.** Add a `planner_family_max (belief-state + greedy info-gain) below oracle-minus-band` term to `promotion_rule_for_003a`, plus a matching positive property and forbidden pattern; or state explicitly that `strongest_fair` = max over the full battery (planners included) and that the enumerated gate terms are non-exhaustive. Otherwise a 003A surface can pass every enumerated gate while an active planner still saturates the oracle — reproducing 001A.
- **RF-2 — Separate the oracle from a fair budget-limited planner.** The positive grammar's oracle advantage ("budget-faithful information gathering") is the same capability the strongest fair baseline already has. State the specific structural information asymmetry a fair budget-limited/greedy planner provably cannot capture under the same budget, with a pre-run argument; or lower the grammar's confidence and treat the blocked verdict as expected. This is the lab's recurring "candidate behaviorally equivalent to a fair baseline" collapse (cf. ACOLB == discounted weighted least-squares; Route C == exhaustive_legal_query).
- **RF-3 — Operationalize the stop verdict.** Bind `blocked_no_valid_environment_design_grammar` to a checkable trigger (e.g. batch all-rejects AND every rejection is a saturation/leakage/decode family, not a fixable underpowered/signal issue) and/or declare a cross-batch search budget after which continued sketch generation is itself treated as baseline-saturated search.

## Non-Blocking Issues

- **NB-1** Static-detectability honesty: the attack library marks A3/A4/A8/A9 as having no stage-1 static detector (battery-dependent); 002C should note which families are micro-probe-only rather than implying static-killability. Mitigated by the brief requiring micro-probe.
- **NB-2** Cross-batch survivorship / multiple-testing across 003A/004A/... is ungoverned (program-level p-hacking). Ties to RF-3.
- **NB-3** Oracle floor and passive floor are referenced as "expected below" without pinned numeric values in 002C; 003A must bind them.
- **NB-4** Closed decoders `full_bundle_decoder` and `serialized_state_decoder` are not explicitly in the 003A battery (most others are). Minor.

## Confirmed Strengths

Verbatim, numerically exact preservation of the three predecessor results; complete A1-A9 enumeration with reject conditions plus an extra underpowered family; baselines strengthened not weakened; strong pre-registration and anti-weakening discipline with a pinned 0.08 gap floor; correct repeated claim ceiling; no governance self-modification; all provenance present.

## Anti-Hardcoding Audit

No executable mechanism (design doc). No threshold tuned to pass (nothing to pass yet). No schema change hiding failure (taxonomy preserves verdicts verbatim). One self-report risk: the `blocked_no_valid_environment_design_grammar` trigger (RF-3).

## Stop Conditions Triggered

Audit scope forbids authorizing 003A / tournament / full harness / candidate — none authorized. RF-1/2/3 flagged as prerequisites for any later 003A authorization. No commit/push/tag/anchor; Auto-Remote-Anchor forbidden; `scripts/push.*` hardcoded-PAT standing block remains.

## Files Changed

None. Read-only audit; only the two new artifacts under this audit task were created.

## What This Does Not Prove

Does not prove any environment has headroom, that A1-A9 is exhaustive, that a credible positive grammar exists, that 003A would succeed, or anything about Gate1, mechanism validity, candidate feasibility, agency, autonomy, consciousness, emotion, stable user benefit, or EGO readiness.

## Remaining Unknowns

Whether any surface can make a budget-limited belief-state / greedy planner provably fail while keeping a budget-faithful oracle above floor (RF-2) — unknown until a concrete 003A sketch is designed and micro-probed. Whether 002C's qualitative stop trigger would fire before a false positive is manufactured across batches (RF-3).
