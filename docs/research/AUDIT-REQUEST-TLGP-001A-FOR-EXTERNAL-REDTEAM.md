# External Red-Team Audit Request — TLGP bank + capability-witness cards (001A)

You are an independent hostile auditor for an offline intelligence-theory lab. Two
DESIGN-ONLY draft task cards are awaiting authorization. **Nothing has been
executed** (no commit, no `git add`, no code run). Review the two cards and decide,
per card, whether implementation may proceed.

This packet is self-contained: the evidence below was verified against the live
repo on 2026-06-29 by the drafting assistant. If you have repo access, re-verify
using the listed commands; if not, treat the evidence table as drafter-readback
(the same skepticism the lab applies to operator readback).

## What to review (attach these two files)
1. `docs/task_cards/TLGP-001B-R2-PROVENANCE-BANK-001A.md`
2. `docs/task_cards/TLGP-CAPABILITY-WITNESS-PREFLIGHT-001A.md`

## Required output (per card)
- **Verdict**: `accept_for_authorization` | `requires_revision` | `reject`.
- **Blocking issues** (must fix before execution).
- **Non-blocking issues**.
- **Required fixes** (concrete).
- **May implementation proceed?** yes/no, and under what condition.

Do NOT turn the audit into stylistic rewriting. Wording is non-blocking unless it
changes claim strength, evidence interpretation, schema/repro, or governance.

## Hard constraints on the auditor
- Do not relax the claim ceiling. The strongest allowable claim for the bank is
  exactly: *"TLGP-001B-R2 official full run produced bounded INVALID due to
  learnability-floor failure under frozen prereg sha 6e61a831…"*. Nothing about
  mechanism, learning, transfer, agency, self, subjectivity, AGI, companion/EGO.
- Do not approve any re-run/retraining, scope expansion, or remote push.
- Treat the TLGP prereg / verdict precedence / capacity grid / trace schema /
  failure taxonomy as READ-ONLY rule sources. If a card changes a rule that judges
  it, that is a blocking governance-self-modification issue.

## Context (minimal)
- Lab = offline bounded mechanism-evidence lab. Cards live in `docs/task_cards/`.
- Route chosen by operator: (1) bank the existing TLGP-001B-R2 negative result
  (provenance-only, no re-run); (2) then a candidate-free preflight on whether a
  capability witness is even attainable (prerequisite for the transfer/H1 question,
  which is the lab's only remaining live mechanism thread).
- TLGP world = mod-5 rule world; each episode has an `adapt` phase then a `query`
  phase, with train-vs-held-out feature-value splits (a within-episode
  transfer/generalization test, structurally similar to WorldTest/AutumnBench
  explore→test). Fair baselines: lookup, count_table, predict_all, majority,
  no_adaptation. Primary metas: in_context GRU + Transformer. Verdict = 7-terminal
  function (`verdict.py`); branch 2 = `not any(rung0_pass)`.

## Verified evidence table (value | re-verify command | confidence)
| # | Claim | Value | Re-verify | Confidence |
|---|---|---|---|---|
| E1 | HEAD / bank commit | `b4ee157a01caef34c598bbeb3ac5ed1bb9b90f24` | `git rev-parse HEAD` | verified |
| E2 | TLGP-R2 source tree tracked? | UNTRACKED (`git ls-files src/tlgp_001b_r2/` = 0; `git show HEAD:…harness.py` = empty-string hash) | `git ls-files src/tlgp_001b_r2/ \| wc -l` | verified |
| E3 | on-disk `harness.py` sha256 | `6b32e47ef8bf9ad91716418ede7611ff011a0bdaa5a1c37ebc1b739c580c576f` | `sha256sum src/tlgp_001b_r2/harness.py` | verified |
| E4 | run-time recorded source hashes | `source_manifest.json:delivered_source_hashes` (9 files; harness = `6b32e47e…`) | read that JSON | verified |
| E5 | B2 self-check is tautological | `official_full.py:584 delivered=source_hashes()`, `:585 executed=source_hashes()` (identical calls) → `delivered_equals_executed` always True | read lines 584-602, 701-702 | verified |
| E6 | pre-run source pin exists? | NO (IMPLEMENTATION_REPORT pins no source SHAs) → B2 not truly closable for this run | `grep -i sha256 …/IMPLEMENTATION_REPORT.md` | verified |
| E7 | `.gitattributes` working-vs-HEAD | differs by exactly one trailing CR on the single LFS-rule line | `git diff -- .gitattributes \| cat -A` | verified |
| E8 | trace storage | committed HEAD blob = Git LFS pointer `oid sha256:f9d5f47854b91cc107230a2335b12c8c43dad6ffc82b34a2dee0da708ab6c0fd`, size `507348934`; `.git/lfs` ≈ 484 MiB present | `git show HEAD:…/official_trace.jsonl`; `du -sh .git/lfs` | verified |
| E9 | git-lfs in drafting sandbox | NOT installed (working tree has expanded content, shows as modified) | `git lfs version` | verified |
| E10 | AGENTS.md drift | shows `M` but `git diff --ignore-all-space` is empty (EOL-only); lines 471/2714 blank both | `git diff --ignore-all-space -- AGENTS.md` | verified |
| E11 | prereg canonical sha (frozen) | `6e61a831c6f287c10c25cccbb09a40671410cd4805214dbd91d62528b2c3d5a7` | `python -m src.tlgp_001b_r2.preregistration` | verified |
| E12 | result verdict + replay | `tlgp001b_r2_invalid_learnability_floor_failed`; `result.json:replay_summary` `replay_exact=true`, `metrics_exact=true`, `recomputed_verdict==result_verdict` | read `OFFICIAL_FULL_RUN/result.json` | verified |
| E13 | rung0 failure mechanism | both primary metas memorize train (~0.97) but collapse to ~0.45–0.55 on held-out queries of the SAME 8 rules, ≪ rung0 bar (≈ ideal−DELTA ≈ 0.9) | audit `…OFFICIAL-FULL-RUN-AUDIT-001/audit_report.md` | drafter-readback of audit |
| E14 | prior audit verdict | `requires_official_bundle_repair_before_accepting_verdict`; science "sound and clean-room reproducible" (830,000 rows, max Δ 3.9e-15); "do not bank yet" | read that audit_report.md | drafter-readback of audit |

## Attack surface — the drafter's own honest weak points (please press hardest here)

**Card 1 (PROVENANCE-BANK):**
- W1 — *B2 cannot be truly closed for this run.* No pre-run delivery pin exists
  (E6); `source_manifest.json` was written during the run by the same process, so
  re-verifying "delivered==executed" only proves current-on-disk == run-time-record
  (self-consistency), not a delivery-time pin. Is banking acceptable with B2 only
  partially closed? Drafter's position: yes, because the verdict is clean-room
  reproducible independent of the gate (E12/E14) and the bank string makes no
  self-check claim — but test this.
- W2 — *Banking mechanics.* Robust path = clean git-lfs clone; the drafting sandbox
  cannot do it (E9). Confirm the LFS object (oid `f9d5f478…`) is actually fetchable
  wherever banking happens, and that the commit keeps the pointer, not a ~507 MB
  inline blob. Accidental large-blob commit is a real failure mode.
- W3 — *Untracked-source provenance gap (E2).* The source was never tracked
  during/after the run; proving on-disk == ran-source leans on the same run-time
  manifest (circular with W1). Harness hash match (E3=E4) is reassuring but not
  independent.
- W4 — *Global-config touch.* The `.gitattributes` CR (E7) is trivial, but it is a
  forbidden global-config file of unknown-provenance drift. Is banking-from-clean-
  clone (which sidesteps it) mandated, or is an in-place revert being smuggled in?
- W5 — *B2 fix = changing the judge.* The card defers the verifier fix to future
  runs and forbids re-judging this run as "self-check passed." Confirm that guard is
  airtight and the fix is not used to launder this run.

**Card 2 (CAPABILITY-WITNESS-PREFLIGHT):**
- W6 — *Bar redefinition.* The card must use the prereg's exact rung0/floor
  semantics, not re-invent "within DELTA of ideal." Check it does not move the
  goalpost (governance self-mod / tuning-to-pass).
- W7 — *Budget sweep as hidden capacity lever.* "Epochs/steps only, capacity frozen"
  — but more training can change effective capacity use. Is a budget→balacc plateau
  a clean "ceiling vs budget" discriminator, or could a sub-bar plateau still be a
  capacity artifact?
- W8 — *Rung cherry-picking = tuning-to-pass.* Searching for "a rung where a fair
  learner interpolates but lookup can't" risks cherry-picking. Is the pre-declared
  rung list + pre-result hash enforceable enough?
- W9 — *Over-reading a positive.* `route_open` establishes rung0 capability only,
  NOT transfer (rung3/H1). Confirm the claim ceiling holds and a positive is not
  narrated as progress toward "transferable continual learning."
- W10 — *The route may be dead on arrival.* The lab's own diagnosis is that
  equal-access hands identifiability to the baseline. If rung0 is itself
  equal-access-saturated, even a "capability witness" could be lookup-equivalent.
  Should Card 2 pre-concede `route_closed` as the likely outcome and justify why it
  is still worth running cheaply?

## Note for the operator
You can run the GPT review in Chinese or English. Attach both card files plus this
packet. If GPT has no repo access, it should mark E1–E14 as "unverified, accepted
as drafter-readback" and audit the cards' internal logic + claim ceiling; if it has
access, it should re-run the commands and confirm/refute each row.
