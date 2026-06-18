# SESSION HANDOFF 002A — current front + queue (post TLGP-001A)

> Navigation overlay (`REPO-NAVIGATION-ANCHOR-PREP-001A`, 2026-06-18):
> this handoff is preserved as a source/handoff record, not as current
> publication authority. Section 3(a)'s TLGP remote-anchor queue is historical
> session-local guidance and is superseded for current anchor authority by
> `docs/research/REPO-NAVIGATION-ANCHOR-PREP-001A.md`,
> `docs/CURRENT_STATE.md`, and fresh git readback. It does not authorize TLGP
> `src/**`, `tests/**`, artifact staging, push, tag, or any claim upgrade.
> Current remote-anchor scope is docs-only navigation reconciliation if and only
> if the anchor-prep task gates pass.

Supersedes the forward-looking part of `SESSION-HANDOFF-001A` (the grounding-gate decision is
resolved — that route is K1/K2 design-closed; we pivoted to Track 1.1). Read THIS + the linked
files; do NOT rely on prior-conversation memory. Outcome-neutral: nothing here assumes any
route will succeed.

## 0. Claim ceiling (binding for the whole program)
Bounded offline mechanism evidence only. **Capability ≠ mechanism ≠ subjecthood.** No result
here evidences agency, feeling, emotion, self, autonomy, or subjectivity — that frontier has
no known construction route AND no known validation method, and is NOT on the roadmap. Do not
re-attach it to any empirical win. PASSES need MORE scrutiny than negatives (the pull to
over-read peaks on a positive).

## 1. Strategic position (the map)
- **Two tracks.** Track 1.1 = learning/generalization (in THIS lab). Track 2 = companion
  engineering / "feels alive" (in EGO or a SEPARATE repo — companion/LLM/emotion code is
  contract-forbidden in this lab). Build a demo; replace a component only when a challenger
  genuinely BEATS it on a real test, not on vibes.
- **Drive axis (AIDSP-001A-R1): CLOSED, bounded negative.** EFE epistemic/curiosity term is
  redundant; transition-conditioned model-based pragmatic inference won. Independently
  audited. Do not re-test for a pass.
- **Self / grounding / Route-C family: CLOSED at K1/K2 (design-gate).** "Intervenable latent
  binding prediction+report+action" = ACSB/Route-C re-entry; failed gate-to-draft on K2
  (interventional-baseline saturation; co-binding non-identifiable). The K1–K7 killer catalog
  is the mandatory pre-draft checklist for any such gate.
- **Frontier (validated self/feeling): permanently open**, held like Villeneuve/Joi — not a
  milestone, not on the roadmap.

## 2. Current front — TLGP-001A (Track 1.1 learning-gate, candidate-free preflight)
EXECUTED 2026-06-18. Verdict = `world_discriminates_structure_inference` (PASS; computed
boolean conjunction; N=200; frozen prereg sha 3fdad0f3). World `effect=(Σwᵢxᵢ + c·a) mod 5`,
held-out = unseen property VALUES (extrapolation); ideal Bayesian observer = 1.000, max fair
baseline = 0.197 (floor 0.20), **headroom 0.803**; shuffle-structure ablation collapses
headroom (→ comes from structure, not oracle-privilege); K1 single-step decoder at floor
(latent non-decodable); leak positive-controls (incl renamed channel) all caught; replay
exact; 17/17 pytest incl fail-ability probes.

**NOT banked. THREE caveats bound it — do NOT over-read:**
1. **drafter == implementer == same session** → needs INDEPENDENT audit (fresh, outcome-
   neutral) before it counts as banked evidence.
2. **NO cross-episode meta-learner in the panel** — all baselines are per-episode cold-start
   like the observer. A meta-learner trained across episodes could learn the mod-5 family and
   may CLOSE the headroom. The PASS only shows *"within-episode inference (given family
   knowledge) ≠ within-episode lookup."* **This is the most likely collapse point.**
3. Extrapolation-regime only. (Full list: `artifacts/TLGP-001A/LIMITATIONS.txt`.)

What the PASS actually buys: the lab's **test-construction machinery works** — P1 (train/test
gap) + P2 (known-latent + ideal-observer ceiling) + baseline panel + triviality gate + leak
positive-controls + computed fail-able verdict + exact replay can produce a clean
*discriminating* PASS (the gate can say YES, not only NO). A methodology win, pending audit +
panel completion. It buys NOTHING about learning-as-mechanism, and nothing about self/feeling.

## 3. Immediate queue (in order)
**(a) remote-anchor — USER's machine ONLY.** Token = `CLAUDE_GITHUB_KEY` (lives on the user's
OS, NOT in the sandbox; the sandbox cannot push). HAZARD: the working tree shows ~2759
"modified" files that are **pure CRLF line-ending drift** (CLAUDE.md, AGENTS.md, old artifacts
— NOT real changes; diff vanishes under `--ignore-cr-at-eol`), plus a stuck `.git/index.lock`.
Anchor ONLY the new TLGP items via **scoped `git add`** (NOT `git add -A`; NOT `push.py`, which
diffs the whole working tree and would push all 2759 CRLF files → governance + old-artifact
contamination). New items to anchor:
`docs/research/BENCHMARK-METHODOLOGY-APPLICABILITY-001A.md`,
`docs/research/TRACK1-LEARNING-GENERALIZATION-PREFLIGHT-001A.md`,
`docs/research/SESSION-HANDOFF-002A-current-front-and-queue.md` (this file),
`src/tlgp_001a/`, `tests/test_tlgp_001a.py`, `artifacts/TLGP-001A/`.
Clear `.git/index.lock` first; commit with an UNAUDITED/provisional message. (AIDSP work +
earlier docs are already tracked/committed.)

**(b) Independent audit of TLGP-001A** (fresh session, outcome-neutral). Verify from ARTIFACTS,
not prose: verdict computed/fail-able, shuffle ablation real, K1/K3/K4/K6 controls genuine,
replay exact, prereg sha 3fdad0f3 + `code_path_provenance.json` (executed==delivered).
SPECIFICALLY interrogate caveat #2 — confirm the PASS is bounded to within-episode and that a
cross-episode meta-learner is required before any candidate may be admitted.

**(c) Add cross-episode meta-learner to the panel** (panel completion / candidate card).
Make-or-break: if a fair meta-learner (trained across episodes; can learn the rule family)
CLOSES the headroom → the world does not discriminate inference from learned-lookup → bank as
negative. If headroom survives a strong meta-learner → first real bounded learning-axis signal
(still not self/feeling). Keep ALL TLGP-001A gates. Needs explicit authorization to build.

## 4. Hard constraints the new session MUST respect
- Claim ceilings (§0). Capability ≠ mechanism ≠ subjecthood.
- K1–K7 killer catalog: cite + show how you beat each before drafting any new gate (esp. K2
  for any latent/self route).
- Git/sandbox hazards: no-delete mount; **FUSE-lossy bash writes** (for provenance use the
  file-API Read, NOT bash reads; author+run a clean copy in /tmp, `cp` to mount, verify sha256
  executed==delivered); stuck `.git/index.lock`; 2759 CRLF drift (never mass-commit / never
  `git add -A` / never push.py for an anchor); ~45s bash cap (chunk long runs); token only on
  the user's OS; **NO commit/push/tag/anchor without explicit authorization.**
- No LLM integration. Isolated files only. Never touch CLAUDE.md/AGENTS.md or old artifacts.
- Outcome-neutral fresh sessions: keep drafter ≠ implementer ≠ auditor where possible.

## 5. Single source of truth (read these)
- This handoff (002A).
- `docs/research/TRACK1-LEARNING-GENERALIZATION-PREFLIGHT-001A.md` (card) + `artifacts/TLGP-001A/`
  (evidence — start at `result.json`, `claim_ceiling.txt`, `LIMITATIONS.txt`).
- `docs/research/BENCHMARK-METHODOLOGY-APPLICABILITY-001A.md` (P1/P2/P3 method source).
- `docs/research/SELF-BOUNDARY-INTERVENABLE-LATENT-NEGATIVE-LINEAGE-AND-KILLER-CATALOG-001A.md` (K1–K7).
- Memory: `itl-track1-learning-gate-tlgp-001a`, `itl-aidsp-001a-r1-independent-audit`,
  `itl-self-boundary-killer-catalog-001a`, `itl-git-sandbox-constraints`.

## 6. What this session produced (ledger)
- AIDSP-001A-R1 closed-negative + RF1 provenance reconciliation (src == executed, sha verified). [tracked]
- PAT blocker closed: push scripts de-hardcoded to `CLAUDE_GITHUB_KEY` env reads; both gitignored.
- Docs: active-inference lineage, killer-catalog (K1–K7), benchmark-applicability, TLGP card, handoffs.
- TLGP-001A executed: PASS (UNAUDITED / provisional, bounded by 3 caveats).
- This handoff (002A).

## Claim ceiling
Process / handoff record. Authorizes nothing. The next session needs explicit authorization to
run the independent audit or to build the meta-learner panel.
