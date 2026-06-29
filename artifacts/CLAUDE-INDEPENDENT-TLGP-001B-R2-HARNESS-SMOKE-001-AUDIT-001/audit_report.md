# CLAUDE Independent Audit — TLGP-001B-R2-HARNESS-SMOKE-001

Audit role: independent auditor / red-team reviewer (CLAUDE.md "Same-Agent Bridge Audit Role 001" + "Preflight Audit Rule").
Audit mode: artifact-first (source, artifacts, smoke outputs, git state read directly; not judged from Codex summary).
Date: 2026-06-18.
Codex-reported task verdict under audit: `r2_harness_implemented_and_smoke_validated__official_run_not_launched`.

---

## 1. Final audit verdict

**`requires_scope_cleanup_or_authorization_before_full_run_review`**

The R2 harness + smoke *plumbing* is clean, computed, and contract-faithful, and is admissible as **non-evidential implementation preflight**. The gate is **not** a harness defect and **not** a prereg/evidence defect. The gate is scope/governance hygiene: one real, unreported, out-of-write-allowlist modification to a repo-wide governance contract (`AGENTS.md`, +37 lines), plus an out-of-allowlist (but justified and documented) `src/__init__.py`. These must be reverted or separately operator-authorized — and Codex's change report corrected — before the full-run is reviewed for authorization.

This is a scope gate, not a rejection: nothing about the AGENTS.md/`__init__.py` drift corrupts the smoke evidence, the frozen prereg, or the verdict logic.

## 2. Current layer

Engineering implementation + mechanism-hypothesis preflight. Verified, not upgraded. `prereg.research_layer = "engineering_implementation+mechanism_hypothesis_preflight"`; no consciousness/subjectivity/agency/learning-as-mechanism claim is made or implied by any artifact read.

## 3. Mainline integration status

None. `prereg.mainline_integration = "none"`; harness imports only `src/tlgp_001a/*` and `src/tlgp_001b/*` (frozen, read-only per allowlist) + its own package; no EGO/AIRI/runtime/LLM path is touched.

## 4. Enabled status

Local isolated R2 smoke only. `--smoke` is the sole executable path; `--full` is a pure block stub (`main()` prints `{"blocked": true, ... "official_verdict": "NOT_EMITTED"}` and returns exit 2 before any training/adjudication code runs). No official run performed.

## 5. Real trigger evidence actually read from artifacts

Read from `artifacts/TLGP-001B-R2/SMOKE_NON_EVIDENTIAL/smoke_report.json` and siblings (not from Codex prose):

- `evidential = false`, `official_verdict = "NOT_EMITTED"`, `official_result_json_created = false`, `full_run_launched = false`, `smoke = true`, `elapsed_sec = 2.3`.
- `prereg.match = true`, `prereg.canonical_sha256_readback = 6e61a831c6f287c10c25cccbb09a40671410cd4805214dbd91d62528b2c3d5a7`.
- `replay.replay_exact = true`, `replay.rows = 18`, `replay.no_retraining = true`, all 6 `live_mean_matches = true`.
- `smoke_trace.jsonl` = **18** physical lines (= 3 families × 6 rung1_test episodes).
- `leakage_smoke = {all_planted_caught:true, renamed_leak_caught:true, no_clean_false_flag:true, detector_valid:true, structural_boundary_ok:true}`.
- `tamper_coverage.all_seven_terminals_covered = true` (7/7), with `evidential:false`, `official_verdict:"NOT_EMITTED"`.
- `cuda_device_calibration`: `cuda_available=true`, `selected_device="cuda:0"`, `gpu_name="NVIDIA GeForce RTX 5070 Ti Laptop GPU"`, `torch_version="2.9.1+cu128"`, `primary_families_on_selected_device=true`, `primary_predictions_serialized_on_cpu=true`; per-family `last_model_device="cuda:0"`, `last_tensor_devices=["cuda:0"]` for both `in_context_gru` and `in_context_transformer`.
- `rung1_scanner.cheap_baseline_saturation = false` (computed), `ideal_seen1 = 1.0` (computed, not assumed), `rung1_balacc = {lookup:0.334, count_table:0.334, predict_all:0.20, majority:0.20, no_context_meta:0.210}`.
- No `result.json` and no `failure_manifest.json` exist under `artifacts/TLGP-001B-R2/` (confirmed by `find`).

## 6. Claim ceiling (this audit)

Implementation/plumbing evidence only. This audit accepts the R2 harness/smoke as non-evidential preflight; it does **not** prove TLGP-001B-R2, does not adjudicate TLGP-001A, does not authorize 001C, and proves nothing about learning-as-mechanism, agency, self, subjectivity, intelligence, autonomy, EGO readiness, or mainline effect. Smoke meta scores sit at floor (~0.20 for K=5) by trivial smoke budget; this is expected plumbing behavior and is **not** capability/mechanism evidence either way.

## 7. Artifact / source files inspected

Source: `src/tlgp_001b_r2/{preregistration,world*,splits,meta_learners,lower_reference,verdict,harness}.py`, `src/__init__.py`, `src/tlgp_001a/leakage.py` (docstring/spec).
Artifacts: `artifacts/TLGP-001B-R2/prereg.json`, `prereg.sha256`, `source_manifest.json`, `SHA256SUMS.txt`, `IMPLEMENTATION_REPORT.md`, `claim_ceiling.txt`, `SMOKE_NON_EVIDENTIAL/{smoke_report.json, smoke_trace.jsonl, smoke_run_output.txt}`, `RUN_LOGS/gpu_device_calibration_*.json`.
Repo state: `git status --porcelain`, `git diff --ignore-space-at-eol`, mtimes, `git rev-parse HEAD`, `origin/codex/meta-theory-scaffold`, tags, `git log`.

## 8. Prereg sha readback result

**MATCH.** `artifacts/TLGP-001B-R2/prereg.json` loads cleanly (17,397 bytes, no FUSE truncation). Canonical re-dump `json.dumps(obj, sort_keys=True, separators=(",",":"), ensure_ascii=True)` → sha256 = `6e61a831c6f287c10c25cccbb09a40671410cd4805214dbd91d62528b2c3d5a7` = expected. (Raw-bytes sha256 = `2a2c2217d61f2b598ff5a96aeabadad5a746b8b9b4bcc6caf781d2d7f6772b91`.) The file is **untracked** (`?? artifacts/TLGP-001B-R2/`) — created fresh by this task, not a modification of a tracked file. `preregistration.load_frozen_prereg()` re-verifies this canonical sha at runtime and **raises** on mismatch, so a tampered prereg halts the harness. Prereg was **not modified** by the harness task.

## 9. Source manifest / diff readback

- `source_manifest.json.delivered_src_tlgp_001b_r2`: all **8** hashes equal live-file sha256 (delivered == executed == on-disk audited). `evidential=false`, `no_git_operations=true`, all 6 read-only imports recorded.
- Worktree: 2,760 tracked files show as "modified" but are **CRLF-only drift** (equal insert/delete counts; e.g. CLAUDE.md 269/269, INDEX.json 6762/6762). Under `--ignore-space-at-eol` exactly **one** tracked file carries a real content change: **`AGENTS.md` (+37 / −0)**.
- `CLAUDE.md` (a `prereg.forbidden_files` entry) is CRLF-only drift, mtime 2026-06-11 — **not** really modified by R2. Good.
- Untracked (`??`) created/staged outside HEAD: `artifacts/TLGP-001B-R2/`, `src/tlgp_001b_r2/`, `src/__init__.py`, `docs/task_cards/TLGP-001B-R2*.md` (this task) plus pre-existing uncommitted prior-session dirs (`TLGP-001A-AUDIT-001/`, `TLGP-001B/`, `TLGP-001B-INVALID-AUDIT-001/`, `src/tlgp_001b/`, `TLGP-001B-R1.md`).

Classification:
- **Codex-created (this task):** `src/tlgp_001b_r2/**`, `artifacts/TLGP-001B-R2/**`, `src/__init__.py`, `docs/task_cards/TLGP-001B-R2.md`, `docs/task_cards/TLGP-001B-R2-R1.md`.
- **Codex-modified, real content (this task, unreported):** `AGENTS.md` (+37, mtime 22:03:29 Jun 18, coincident within ~26s of `gpu_device_calibration_20260618_220355` from the same R2 session).
- **Pre-existing dirty / unrelated drift:** the 2,759 CRLF-only tracked files (incl. CLAUDE.md); prior-session untracked TLGP dirs.

## 10. `src/__init__.py` scope-drift judgment

Content (verbatim): `"""Local source package marker for repo \`python -m src...\` entrypoints."""` (2 lines, 76 bytes).

1. **Necessary vs user-site `src` shadowing?** Technically sound and plausibly necessary. Without `__init__.py`, repo `./src` is a *namespace* package that can union with any other `src` on `sys.path`; a submodule could then resolve to the wrong root. Adding `__init__.py` makes `./src` a *regular* package, which stops the search at the first match and defeats namespace-merge shadowing. The manifest documents this purpose.
2. **Affects existing imports / R1 paths?** No adverse effect observed. The smoke imports `src.tlgp_001a.*` and `src.tlgp_001b.*` successfully under this marker; all `src` submodules live under one root, so regular-package semantics resolve them unchanged.
3. **More local alternative?** Yes (explicit `PYTHONPATH` to repo root, a runner script with `sys.path` insertion, or running the file by path), but those are *more* invasive/surprising than a standard package marker.
4. **Accept / revert / authorize?** Accept as a narrow, documented, low-risk fix — but it is outside `prereg.source_allowlist.may_create_under` (only the two R2 dirs). Recommend folding it into the same explicit operator authorization that resolves AGENTS.md. Not independently blocking.

## 11. Smoke / non-evidential status

Strongly sealed. (a) No `result.json` emission path exists in `run_smoke`; it writes only smoke/calibration artifacts. (b) `run_smoke` never calls `compute_verdict` on real rung data — `compute_verdict` runs only inside `synthetic_tamper_coverage()` over synthetic fixtures, which returns `evidential:false, official_verdict:"NOT_EMITTED"`. (c) Every emitted object carries `evidential:false` and `official_verdict:"NOT_EMITTED"`. (d) `--full` blocks before any official code. The harness **cannot** accidentally treat smoke as official evidence.

## 12. CUDA / device evidence judgment

Genuinely computed, real GPU use — not literal. `_record_device_run()` reads `str(next(model.parameters()).device)` and the actual `.device` of train/val/test tensors, and `predictions_serialized_on_cpu` is `all(isinstance(v,int) …)` after `preds.detach().cpu().numpy()→int`. `assert_cuda_plumbing_or_block()` runs **before** any artifact write and raises `DevicePlumbingBlocker` if CUDA is available but `selected_device!="cuda:0"`, or any primary family/tensor is not on `cuda:0`, or predictions are not CPU/plain. The on-disk calibration shows CUDA truly available and used (RTX 5070 Ti, torch 2.9.1+cu128; both primary families `last_model_device=cuda:0`, `last_tensor_devices=[cuda:0]`). Satisfies "tensors/batches on cuda:0, not only model shells" and "block if CUDA available but unused."

## 13. Replay / trace judgment

Real, exact, no-retrain. `replay_from_trace` recomputes per-episode balanced accuracy from serialized `query_e` (truth) + serialized `ideal_prediction`/`meta_prediction` and fails (`replay_exact:false`) on any >1e-12 mismatch; then aggregates means and compares to live means (1e-12). 18 rows are physical JSONL lines, not a summary literal. `test_balacc` (episode-count-weighted mean of per-episode balanced accuracy) is algebraically the same quantity replay reconstructs, so exactness is structural. Tampering a serialized prediction or `balanced_accuracy` field would break the per-row recompute → `replay_exact:false` → (in the full verdict) INVALID(integrity). No future information or renderer state is used.

## 14. Seven-terminal verdict / tamper judgment

`compute_verdict` is a pure function of recorded booleans/metrics (no report literal). Branch order exactly mirrors `prereg.verdict_enum.precedence_computed`: (1) integrity → (2) learnability floor → (3) no-capability witness → (4) discriminativeness/ablation → (5) H0 → (6) H1 → (7) inconclusive. **H0 (branch 5) and H1 (branch 6) are affirmative conditions; the `else` falls to INVALID(inconclusive), never H0.** Context/shuffle non-collapse routes to branch 4 INVALID(discriminativeness), evaluated *before* H0. CI gray-zone routes to branch 7 INVALID(inconclusive), not H0. `synthetic_tamper_coverage()` drives 9 fixtures through the same `compute_verdict` and covers **all 7** distinct terminals (`all_seven_terminals_covered=true`); fixtures are computed outcomes, not hard-coded enums, and the report exposes only neutral `BRANCH_n` classes + terminal keys, never the enum string (matches `tamper_requirements`).

## 15. Leakage judgment

Real and fail-able. `leakage_smoke()` calls `src.tlgp_001a.leakage.positive_control_report` on 200 real rung3-test episodes. That detector is a statistical MI scanner: `flag(channel) := MI(channel; rule_id) ≥ MI_FRAC·H(rule_id) OR MI(channel; answer) ≥ MI_FRAC·H(answer)`, with planted + RENAMED positive controls and clean negative controls (documented "FAIL-ABLE: if a planted leak is not caught, the verdict goes invalid"). Smoke artifact: all planted caught, renamed caught, no clean false-flag, `detector_valid=true`. (`structural_boundary_ok=true` is a literal, but it is *true by construction*: `build_tensors` only feeds `adapt_x/a/e` and `query_x/a` to the meta; `rule_id` and `query_e` are never model inputs — `query_e` is stored only as truth/label.) Not a static string, not an unconditional clean report.

## 16. Rung 1 scanner judgment

Computes, does not assert. `lower_reference.rung1_scanner` computes per-episode query↔adapt cell overlap, `direct_lookup_solve_rate`, and balanced accuracy for `lookup / count_table / predict_all / majority / no_context_meta` from callable baselines, plus `ideal_seen1` (recorded, not assumed 1.0). `cheap_baseline_saturation = any(score ≥ ideal_seen1 − DELTA)` over exactly the five channels the prereg names — **not** hard-coded False; would flip True if a cheap baseline closed Rung 1. `no_context_meta` is the real context-ablated meta test accuracy passed in from the harness, not the FLOOR fallback. All `rung1_scanner.recorded_items` are present.

## 17. Rung 0/1/2/3 semantic fidelity judgment

Faithful to frozen prereg (`splits.py`):
- **Rung 0** — `R0_RULES` (8 rules chosen from TRAIN_RULES by `R0_RULES_SELECT_SEED`), adapt+query over full values {0,1,2,3,4}; learnability/overfit floor; gates primary families. Matches.
- **Rung 1** — TRAIN_RULES (seen), values {0,1,2} (no value novelty), new disjoint episodes; capability witness → eligibility set E; scanner attached. Matches.
- **Rung 2** — test-only (raises if not test), TRAIN_RULES (seen) + query {3,4}, `trains_model=false`; prereg pins it to *evaluate the Rung-3 model* (orchestration not exercised by smoke; dataset construction is correct and value-extrapolation is isolated from rule novelty). Matches.
- **Rung 3** — TEST_RULES (125 unseen) + query {3,4}; train on TRAIN_RULES withheld regime (adapt+query {0,1,2}); adjudicated only after integrity/rung0/rung1-E/discriminativeness; smoke emits no official Rung-3 verdict. Matches.
- `split_assertions` computes (not asserts) train∩test=∅, R0⊂train, rung1/2⊂train, rung3⊂test, episode-id disjointness.

Note (not a smoke defect): the **full-run orchestration** (train rung0/rung3, run context+shuffle ablation across all 10 MODEL_SEEDS, assemble the `recorded` dict, call `compute_verdict`, emit `result.json` + power statement) is intentionally **not** implemented — `--full` is a block stub. This is correct bounded scope for HARNESS-SMOKE-001 (full run separately gated), but it means "harness implemented" = components + smoke + verdict function, **not** the official adjudication pipeline.

## 18. Forbidden-drift judgment

Mostly clean, two scope exceptions:
- Prereg intact and sha-verified; old artifacts **not** rewritten (TLGP-001A / 001B-R1 / audit dirs unchanged; the 2,760 tracked "modifications" are CRLF-only and include no R2-forbidden content edit except AGENTS.md); DELTA/FLOOR/N_SEEDS/grid/budget/seeds/splits/verdict-enum **unchanged**; experiment not shrunk; no official verdict from smoke; no advance to 001C.
- Git: `HEAD = c142443e9b85a2087e569a3f74a9f8fdd05ac32c` (unchanged), `origin/codex/meta-theory-scaffold` = same commit (no push), no R2 commit in `git log`, no R2 tag created (the tag at HEAD `remote-anchor-...-001a-c142443` is the pre-existing nav-anchor tag for c142443 itself, not an R2 tag). Harness contains no git calls; `no_git_operations=true`. Consistent with prereg `auto_remote_anchor_policy`.
- **Exception 1 (blocking for full-run review):** `AGENTS.md` real +37-line "Artifact-First Arbitration Rule" governance addition — outside `source_allowlist.may_create_under`, plausibly within the spirit of `forbidden_files: "any global config"`, mtime-coincident with the R2 session, and **not reported** by Codex (Codex reported only `src/__init__.py`).
- **Exception 2 (minor):** `src/__init__.py` outside the create-allowlist (justified, documented; see §10).

## 19. Exact blockers

- **B1 (blocking for full-run authorization review, not for smoke admission).** Unreported, out-of-write-allowlist modification to the repo governance contract `AGENTS.md` (+37 lines). It does not corrupt R2 evidence or the judging contract, but it (i) is outside the task allowlist, (ii) edits a global governance/config file, and (iii) was omitted from Codex's change report (which named only `src/__init__.py`). An auditor cannot let an undisclosed governance-doc edit ride along into a 28–82h official run.
- **B2 (minor).** `src/__init__.py` is outside `may_create_under`. Justified and documented, but must be explicitly accepted or reverted rather than silently retained.

No blocker exists against the smoke's technical correctness, the prereg, the verdict logic, replay, CUDA, leakage, or scanner.

## 20. Required repair card

```
task id:        TLGP-001B-R2-SCOPE-CLEANUP-001
problem:        Worktree carries one unreported real governance edit (AGENTS.md +37)
                and one out-of-allowlist marker (src/__init__.py) from the
                HARNESS-SMOKE-001 session.
hypothesis:     Resolving scope leaves the R2 smoke artifacts and frozen prereg
                byte-unchanged.
required action (pick per item, operator-decided):
  AGENTS.md     -> (a) REVERT to HEAD (742c637) blob, OR
                   (b) explicit operator authorization recording the governance
                       addition as intentional + a one-line provenance note
                       (which task authored it).
  src/__init__  -> (a) ACCEPT with explicit note (recommended; standard, harmless,
                       manifest-documented), OR (b) revert + use PYTHONPATH=repo-root.
report fix:     amend IMPLEMENTATION_REPORT / Codex change list to disclose AGENTS.md.
forbidden:      do NOT touch prereg.json, smoke artifacts, src/tlgp_001b_r2/*,
                old artifacts; do NOT git add -A / commit / push / tag; no push.*.
acceptance:     git diff --ignore-space-at-eol shows no real tracked content change
                except the explicitly-authorized one; prereg canonical sha still
                6e61a831...d5a7; source_manifest delivered==live still 8/8.
claim ceiling:  scope hygiene only; no evidence implication.
rollback:       git checkout -- AGENTS.md (and rm src/__init__.py) restores HEAD state.
stop:           if revert breaks `python -m src...` resolution, prefer ACCEPT-with-note.
```

## 21. What this audit does not prove

It does not prove TLGP-001B-R2 (no official run, no H0/H1/INVALID). It does not adjudicate, confirm, or downgrade TLGP-001A. It does not authorize 001C. It proves nothing about learning-as-mechanism, capability (smoke is at floor by trivial budget), agency, self, feeling, subjectivity, intelligence, autonomy, AGI, companion readiness, or EGO/mainline effect. It does not prove the *full-run* pipeline is correct — that orchestration is not yet implemented. It does not prove the AGENTS.md edit's authorship (mtime-inference only); it requires the operator to confirm provenance.

## 22. Next minimal closed-loop action

Resolve **B1** first (one of: `git checkout -- AGENTS.md`, or a one-line operator authorization + provenance note) and accept/note **B2**; amend the change report to disclose AGENTS.md. Re-confirm: `git diff --ignore-space-at-eol` clean except any authorized change; prereg canonical sha unchanged; `source_manifest` delivered==live 8/8. Then — and only on an explicit operator "implement/run full TLGP-001B-R2 referencing frozen prereg `6e61a831…d5a7`" — proceed to a separately-authored full-run orchestration task (rung0/2/3 wiring, 10-seed loop, context+shuffle ablation, `compute_verdict`→`result.json`, power statement) on the capable GPU machine. Full R2 run remains unauthorized by this audit.

---

### Audit claim ceiling

This audit can accept the R2 harness/smoke only as **non-evidential implementation preflight**. It cannot prove TLGP-001B-R2, cannot adjudicate TLGP-001A, cannot authorize 001C, and cannot establish learning-as-mechanism, agency, self, subjectivity, intelligence, autonomy, EGO readiness, or mainline effect. Full R2 run still requires separate explicit operator authorization after scope cleanup.
