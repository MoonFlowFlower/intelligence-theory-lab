# SESSION HANDOFF 001A — post-AIDSP → grounding-gate decision

Purpose: let a FRESH session continue with clean context. Read the 3 linked files; do NOT
rely on prior-conversation memory. This handoff is outcome-neutral: nothing below assumes
any route will succeed.

## State as of handoff (2026-06-17)

1. **AIDSP-001A-R1 = CLOSED, bounded negative.** Verdict `baseline_equivalence_or_no_separation`,
   independently audited and accepted as REAL.
   - Finding: EFE's epistemic-value (curiosity) term is **redundant** in the toy POMDP; the
     winner was **transition-conditioned model-based pragmatic inference** (no-transition
     ablation drops M1 1.692→1.051; epistemic ablation does NOT, 1.692→1.698). The whole
     curiosity family lost (count-based RL last).
   - Card: `docs/research/ACTIVE-INFERENCE-DRIVE-SEPARATION-PREFLIGHT-001A-R1.md`.
   - Evidence: `artifacts/AIDSP-001A-R1/` (result.json, ablation_report.json,
     baseline_comparison.json, triviality_probe_report.json, positive_control_report.json,
     replay_report.json). Executed code provenance-pinned: `code_path_hash 6b8a6b61`,
     `prereg c594f4ae`.
   - Do NOT run AIDSP-R2 to chase a pass. The negative is banked.

2. **RF1 = DONE.** The earlier provenance split is reconciled: `src/aidsp_001a_r1/` is now
   byte-identical to the executed `_run_src/` (all 11 .py), and the delivered `src/`
   reproduces both `prereg c594f4ae` and `code_path_hash 6b8a6b61`. `src/prereg.py` (was a
   truncated SyntaxError) now parses. `_run_src/` + `NOTE.md` retained as the provenance
   record; `_canary_fresh.txt` is harmless residue (no-delete mount).

3. **PAT blocker = CLOSED.** Old `ghp_` PAT in `scripts/push.{py,sh}` revoked + replaced
   with `CLAUDE_GITHUB_KEY` env reads (hard-fail if unset); both files gitignored+untracked.

## The pending decision

External review (GPT) recommends pivoting to a **Grounded World-Model / Self-State
Intervention Gate**: an *intervenable latent that simultaneously constrains prediction,
report, and action*. This is goal-relevant and NOT hit by the AIDSP negative — **but it is
this lab's ACSB / Route C family**, which has a standing negative lineage.

**Mandatory before drafting any such card:** read
`docs/research/SELF-BOUNDARY-INTERVENABLE-LATENT-NEGATIVE-LINEAGE-AND-KILLER-CATALOG-001A.md`.
The card may be drafted ONLY if it states, point by point, how it beats **K1–K7** — above
all:
- **K1 obs-decodability:** latent non-decodable from current observation, tested by a
  *capable* obs-baseline + a value-level decode positive control that can flip the gate.
- **K2 interventional-baseline saturation:** separation = `candidate − max(fair
  interventional panel incl. predict_all-analog + a fitted estimator)`.
- **report = structured/discrete channel, NO LLM** (else confabulation = the "looks alive"
  failure).
- latent must be **history-integrating + non-enumerable** (else a hardcoded `need` scalar
  passes trivially).
- **minimal custom world, NOT MiniGrid/Crafter** (richness breeds false passes).

If K1 and K2 cannot be answered, the card is not ready — that is the contract-preferred
negative answer, and the route closes here.

## Recommended next action (outcome-neutral)

A **candidate-free preflight design** for the grounding gate: build only the
generator + capable obs-baseline + value-level decode positive control + fair interventional
panel, and check K1/K2 BEFORE any candidate exists. The gate may die at design — that is
acceptable and cheap. Do NOT build a candidate first.

Alternative, fully legitimate: **stop here and bank**. AIDSP produced a clean positive
engineering finding ("goals + world model already produce the exploratory behavior; explicit
curiosity is redundant"), usable for a "feels-alive" product without any subjectivity claim.

## Read-these (single source of truth)

- `docs/research/SELF-BOUNDARY-INTERVENABLE-LATENT-NEGATIVE-LINEAGE-AND-KILLER-CATALOG-001A.md`
- `docs/research/ACTIVE-INFERENCE-DRIVE-SEPARATION-PREFLIGHT-001A-R1.md`
- `docs/research/ACTIVE-INFERENCE-DRIVE-AFFECT-LINEAGE-001A.md` (design-language background)
- Memory: `itl-aidsp-001a-r1-independent-audit`, `itl-aidsp-001a-r1-impl`.

## Claim ceiling (binding)

Bounded offline mechanism evidence only. No agency, feeling, emotion, self, autonomy,
companion-readiness. The strongest any grounding gate could ever claim is "bounded evidence
of a non-obs-decodable, interventionally-valid latent co-binding prediction/report/action
vs a fair panel, in one minimal world." Nothing about subjective experience.
