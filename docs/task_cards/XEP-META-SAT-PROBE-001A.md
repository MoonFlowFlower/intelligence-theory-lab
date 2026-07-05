# XEP-META-SAT-PROBE-001A — Cross-Episode Meta-Baseline Saturation Probe

Status: **DRAFT — implementation NOT authorized.** Drafting a card requires
stopping before implementation (operating contract). Implementation requires an
explicit operator instruction `implement XEP-META-SAT-PROBE-001A` plus a frozen
prereg sha.

Parent analysis: `docs/research/JOI-LIKE-BOUNDED-MECHANISM-PROXY-ROADMAP-001A.md`
(Part 8). This card is candidate-free and writes only to a new artifacts dir; it
does not modify any frozen TLGP artifact or any governance document.

| Field | Value |
|---|---|
| **task_id** | XEP-META-SAT-PROBE-001A |
| **problem_definition** | The one surviving Layer-2 thread is "cross-episode meta-prior beats a *fair* meta-baseline under held-out shift". TLGP-001A left 0.803 within-episode headroom but had **no cross-episode meta-learner** in its panel — its own caveat #2 names this the most likely collapse point. Before authorizing the expensive TLGP-001B-R2 GPU candidate run, cheaply test whether a **fair amortized/meta baseline** already closes that headroom. GO/NO-GO de-risking probe, not a candidate. |
| **current_stage** | preflight / candidate-free baseline-saturation check |
| **layer** | engineering-implementation + learning-adaptation (Layer 2/4) |
| **mainline_target** | Decide GO/NO-GO on authorizing the cross-episode meta CANDIDATE (TLGP-001B-R2 family) by measuring fair-meta-baseline saturation on a frozen world. |
| **hypothesis (H1)** | A fair amortized/meta baseline (matched data+capacity), trained across episodes, does NOT reach (ideal − DELTA) on held-out regimes/values ⇒ residual headroom survives ⇒ candidate worth authorizing. |
| **null (H0, expected likely)** | Fair meta-baseline reaches ideal within DELTA ⇒ headroom was an artifact of withholding cross-episode training ⇒ route collapses to "amortized supervised learning of a known family" ⇒ CLOSE/downgrade. [INFER: H0 more likely] |
| **invalid enum** | ablation/shuffle fails to collapse, OR replay mismatch, OR leak detected ⇒ INVALID (distinct from H0). |
| **baseline (strongest)** | fair amortized meta-learner {MLP, GRU} trained across episodes; small history-conditioned transformer; exact amortized Bayes over the family; per-episode lookup; majority; ORACLE upper bound. All real `.fit`, numeric features (no one-hot starvation, K4). |
| **ablation** | (a) reset meta-state between episodes ⇒ cross-episode gain must vanish; (b) shuffle-structure ⇒ headroom must collapse to chance (headroom is structural, not oracle-privilege). |
| **trace_replay** | per-episode trace (adaptation obs, prediction, held-out answer, meta-state snapshot, per-baseline score); clean-room replay reconstructs the GO/NO-GO verdict from trace ALONE (no future obs, no renderer/private state); prereg sha frozen before any run; executed==delivered sha readback. |
| **acceptance_gate** | GO iff best fair meta-baseline balacc < (ideal − DELTA) with CI excluding DELTA across ≥5 seeds, **balanced two-sided** metric. NO-GO/CLOSE iff best fair meta-baseline ≥ (ideal − DELTA). DELTA, FLOOR, seed list frozen in prereg BEFORE running. Single-sided/accuracy-only metric forbidden (Gate1-replacement lesson). |
| **claim_ceiling** | bounded preflight evidence about whether residual headroom exists for a fair meta-baseline on the specified world. Proves NOTHING about mechanism validity, learning, self, agency, emotion, or Joi. A GO only licenses "authorize the candidate run". |
| **stop_condition** | STOP at NO-GO (do not patch, do not tune thresholds, do not swap metrics). If run on the enumerable mod-5 world and it saturates (likely), licensed conclusion is ONLY "this enumerable world has no fair-meta headroom" ⇒ escalate to designing a NON-enumerable, history-dependent world (K-catalog) BEFORE any candidate. |
| **rollback_plan** | write ONLY to `artifacts/XEP-META-SAT-PROBE-001A/`; never modify TLGP-001A/B frozen artifacts; no git push (PAT standing blocker); git HEAD unchanged until operator review. |
| **forbidden_changes** | TLGP-001A/B frozen prereg & artifacts; AGENTS.md / CLAUDE.md; global schema; thresholds after results; LLM integration; EGO mainline; any push/tag/anchor. |
| **prior_negatives_cited** | TLGP-001A caveat #2 (no cross-episode meta-learner = likely collapse); TLGP-001B INVALID (positive-control design flaw, prereg `6e61a831`); identifiability-ceiling memo; baseline-immunity admission standard 001A; killer catalog K1/K2/K4. |
| **estimated_cost** | CPU-only, ~2 weeks. wk1: reuse frozen world (read-only) + build fair meta-baseline panel + freeze prereg. wk2: ≥5-seed run + ablation + clean-room replay + computed verdict. Chunk `evaluate()` <45s/bash-call (TLGP FUSE/runtime lesson). No GPU. |

## Pre-flight gate (must pass on paper before any code)
1. Answer **K1** (non-obs-decodability) and **K2** (interventional saturation) in
   writing for the chosen world. Un-answerable ⇒ STOP (contract prefers the
   negative answer).
2. Confirm the world's rule family and whether it is **enumerable**. If enumerable
   (e.g. mod-5, 625 rules), pre-register that a NO-GO is the *expected* outcome and
   that a GO would be a weak claim requiring a non-enumerable redesign before any
   candidate. Do not over-read a GO on a weak world.
3. Cross-check the design against `itl-baseline-immunity-admission-standard-001a`
   (19 failure families). Record which families are in-scope.

## Acceptance signals (what a clean run looks like)
- verdict is **computed**, not asserted; tamper test flips it.
- every baseline shows real fit evidence (capacity, data budget).
- killer ablation collapses the claimed effect.
- clean-room replay reproduces the GO/NO-GO from trace alone.
- no leak flagged by the MI detector (incl. renamed-target probe).

## What this card does NOT prove
mechanism validity · learning · self/agency/emotion · consciousness · Joi
feasibility · correctness of any total theory. Maximum yield = bounded GO/NO-GO
preflight evidence on one specified world, under this prereg.
