# LCC Evidence Lineage

Status: frozen for Milestone 001 review.

Cycle 000-010 produced a strong bounded evidence chain, but every cycle preserved the same claim ceiling: LCC_v0 survived a contract redteam; LCC theory support, a general LCC agent, autonomous theory search, and EGO migration were not authorized.

## Cycle Summary

| Cycle | Verdict | Main Gate |
| --- | --- | --- |
| 000 | `lcc_contract_pass_bounded` | Label permutation invariant, effect swap sensitive, behavior-only replay. |
| 001 | `lcc_contract_strengthened_bounded` | Larger action/state counts, learned effect model, stronger baselines, heldout latent actuator world. |
| 002 | `lcc_contract_strengthened_experiential_bounded` | Passive observation separated from own intervention, delayed and stochastic effects, state-dependent generalization. |
| 003 | `lcc_contract_strengthened_active_identification_bounded` | Diagnostic intervention under ambiguous hypotheses and transfer after identification. |
| 004 | `lcc_contract_strengthened_sequential_control_bounded` | Multi-step effect composition, replanning, trap avoidance, sequence transfer. |
| 005 | `lcc_contract_strengthened_nonstationary_revision_bounded` | Model invalidation, safe re-identification, context-specific revision, drift/switch, old-context recovery. |
| 006 | `lcc_contract_strengthened_representation_grounded_bounded` | Raw/aliased observations, nuisance invariance, representation perturbation, cross-renderer transfer. |
| 007 | `lcc_contract_strengthened_relational_compositional_bounded` | Entity permutation, role swap, distractors, relation composition, tool-mediated causal chains. |
| 008 | `lcc_contract_strengthened_goal_conditioned_reuse_bounded` | Goal switch, constraint reweighting, novel goal composition, model reuse. |
| 009 | `lcc_contract_strengthened_unified_mechanism_bounded` | Shared interface across prior families and hybrid holdouts, no per-cycle dispatch. |
| 010 | `lcc_contract_strengthened_blind_holdout_bounded` | Candidate freeze, blind holdout, independent trace scoring, generic baselines, replication, negative controls. |

## Strongest Evidence

- The original FOPC failure mode, action-label shortcut, was directly attacked by label/effect separation across multiple cycles.
- Behavior-only replay remained part of the evidence chain, reducing reliance on post-hoc score claims.
- Cycle 009 reduced the risk that previous passes were only separate per-cycle solvers.
- Cycle 010 added freeze-before-holdout, independent trace-only scoring, generic baselines, replication, and negative controls.

## Remaining Ceiling

The lineage still does not establish that LCC is a supported bottom-level theory. The evidence is authored, bounded, toy-contract evidence inside one repository and one evolving implementation line. It is stronger than a single benchmark pass, but not equivalent to independent replication or cross-theory dominance.

## Current Claim

LCC_v0 survived eleven bounded contract redteams, including blind holdout after candidate freeze.

## Not Authorized

- LCC theory support.
- Bottom intelligence principle claim.
- General LCC agent implementation.
- Autonomous theory search.
- EGO migration.
- AGI, consciousness, subjective experience, self-awareness, life, or robust universal support claims.
