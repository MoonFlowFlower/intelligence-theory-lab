# CLAUDE-INDEPENDENT-AUDIT — IMPLEMENT-FUTURE-GATE4-CROSS-FAMILY-SOCIAL-CAUSAL-TRANSFER-001A

Role: independent auditor / red-team reviewer (no fixes, no push, no tag, no remote-anchor).
Date: 2026-06-13.

---

## VERDICT

**`invalid_self_report`** — primary classification.

The reported `implementation_pass_pending_independent_audit` is produced by a pipeline whose
candidate score is a tautology and whose leakage / replay / provenance gates cannot fail on the
actual run data. The reported "candidate advantage" (1.0 vs 0.875) is an artifact of hand-written
`if/else` branches, not of any recomputed mechanism.

Two further listed verdicts are simultaneously satisfied and are documented as corroborating:

- **`negative_evidence_baseline_equivalence`** (substantive, recomputed): a *faithful* baseline
  with the candidate's own declared observation access ties the candidate at 1.0.
- **`audit_blocked_requires_repair`** (floor): multiple baseline / leakage / replay / equivalence-rule
  / artifact-mutation issues are unresolved.

Implementation may **NOT** proceed to remote-anchor / Gate5 / admission / bridge / runtime / EGO.

Claim ceiling of this audit: independent audit of a local engineering implementation and evidence
harness only. No Gate4 validity, mechanism validity, social-latent success, agency, selfhood,
consciousness, emotion, autonomy, EGO/runtime/companion readiness, or user-benefit claim is made or
implied.

---

## SCOPE & METHOD

- Audited commit: `78889b69b75baa424e89332558bda798685e9634`
- Branch: `codex/meta-theory-scaffold`
- Parent / starting boundary: `79928e2c5f770326a1d0d370186814f4a0b2d104`
- Latest Gate4 design sealed boundary: `4fb24caf1c69d090cc3b6e15347cac18e178f1eb` (ancestor of HEAD — verified)
- Method: read-only git inspection via a clean side `--git-dir` (the in-repo `.git/config` and
  `.git/index` are corrupted with NUL bytes by the FUSE mount; the object store was symlinked intact
  and the index was rebuilt from HEAD via `read-tree`). Committed source + artifacts extracted via
  `git archive`. Candidate / baselines / leakage / replay independently re-executed in an isolated
  copy. No write, commit, push, tag, or remote operation was performed against the repository.

---

## REPOSITORY BOUNDARY (Q1)

| Check | Result |
|---|---|
| HEAD == target `78889b6…` | PASS |
| Branch == `codex/meta-theory-scaffold` | PASS |
| Ahead by 1; `origin/codex/meta-theory-scaffold` == parent `79928e2…`; no push | PASS |
| No tag points at HEAD | PASS |
| Commit changed files isolated to the 4 allowed paths | PASS |
| Commit = 29 files, **all additions (`A`)**, zero sealed-artifact modification in the commit | PASS |
| **Working tree clean before audit** | **FAIL** |

The **commit** is clean and correctly isolated. The **current working tree is not clean**: 1643
tracked files differ from HEAD.

- Dominated by a repo-wide CRLF (LF→CRLF) rewrite that is **content-preserving** — 20/20 sampled
  sealed JSON artifacts had identical values (only re-serialization / line endings changed); a
  sampled sealed `developer_trace.jsonl` differed by line endings only.
- `CLAUDE.md` differs by line endings only.
- `AGENTS.md` has line-ending changes **plus a real, uncommitted deletion of a ~75-line governance
  block** (the "Codex must not touch EGO mainline…", same-agent-bridge canonical-path, and
  read-only bridge-governance-docs list). This edit is **not** in the commit.
- The new task's own 21 artifacts are also "modified" in the worktree, but semantically identical to
  HEAD (0/61 leaf fields differ in `result.json`) — re-serialization only.

Interpretation: `source_pin_readback.json` records `current_head = 79928e2c` (the parent) and
`worktree_clean_at_start = true`, so the harness ran on a clean tree *before* the commit. The
1643-file mutation therefore occurred *after* the run/commit — consistent with the reported
"full suite mutated old artifacts" — and was **never restored in the working tree**. Per the
project's own rule ("Treat unexplained/unrestored mutation as a blocker, even if task-specific tests
pass"), the unrestored worktree mutation is a standalone blocker, independent of the substantive
findings below.

Note (non-blocking): the in-repo `.git/config` line 19 and the `.git/index` contain NUL-byte
corruption (FUSE artifact). This impedes ordinary `git` use in the mount but does not affect the
committed objects.

---

## SUBSTANTIVE FINDINGS (all independently recomputed)

### B1 — Candidate score 1.0 is a tautology (BLOCKER)

`core.candidate_predict` → `_state_score` computes
`sign( [causal_observation == "partner_updates_when_asked"] + [counterfactual_probe_result == "confirms_partner_state"] )`,
i.e. action = `partner_specific_support` iff **both** bits are positive.

`core.generate_episodes` defines the target label as `partner_specific_support` iff
`positive AND query_positive`, and sets `causal_observation`/`counterfactual_probe_result`
directly from those same two bits.

→ The candidate decision rule **is** the label generator. Recomputation: candidate action ==
target for all 8/8 episodes; candidate score = 1.0 **by construction**, with no learning, no
fitting on the declared train split, and no actual transfer. Anti-hardcoding violations: "hard-codes
the hidden rule"; "passes because the test distribution is too weak" (8 synthetic episodes).

### B2 — Best faithful baseline is unfairly access-limited; under true parity it ties (BLOCKER / negative evidence)

`baseline_predict("query_capable_imitation_baseline", …)` uses **only** the query bit plus an
arbitrary `idx % 3 != 2` index hack, and ignores `causal_observation` — a channel the parity
artifact explicitly grants it (`baseline_observation_access ==
"partial_observation_plus_allowed_counterfactual_query"`, same as candidate).

Recomputed scores: candidate 1.0; best faithful baseline 0.875; all graph-cache members 0.75;
decoders 0.625; oracle (excluded) 1.0.

A faithful imitation baseline that uses the **same declared access** (both channels) scores
**1.0 — a tie with the candidate**. Therefore the reported 0.125 advantage exists only because the
baseline was hand-restricted below the candidate. Under the parity the frozen rule itself requires,
this is **baseline equivalence → negative evidence**. (Task Q4: "Block if any baseline is …
unfairly access-limited.")

Corroboration from ablations: `shuffle_partner_family_labels` and
`remove_explicit_partner_family_schema_ids` both leave the score at 1.0 (zero drop) — the candidate
does not use partner-family or schema at all. The "cross-family social causal transfer" framing is
not exercised by the candidate; it reads only the two label-determining observation bits.

### B3 — Leakage scan is fed a sanitized stub, not the real bundle (BLOCKER)

`runner.execute_harness` calls `leakage.scan_clean_bundle({...})` with a hand-built 4-key summary
(`candidate_aggregate`, `baseline_count`, `diagnostic_oracle_present`, `equivalence_rule_hash`).
The episodes, trace, serialized states, observations and target actions are **never scanned**.

Recomputation: `detect_leakage` on the **real** episodes+trace bundle returns `has_leakage = True`
(detects `target_label_in_serialized_state` via the `target_action` key, plus
`partner_family_id_in_candidate_observation` and `heldout_schema_id_in_trace_metadata`). On the
runner's stub it returns `has_leakage = False`. The "clean / `clean_scan_trusted: true`" verdict is
therefore **non-fail-able on real data**. A string-replacing sanitizer (`runner._safe_payload`,
`target_action→target_ref`, `partner_family_id→partner_family_ref`, …) also exists in the module.
This is the recurring stub-feed / whitelist-escape failure family. Positive controls (7/7) do pass,
but only because each control payload literally contains its own trigger substring.

### B4 — Replay does not validate state-dependence; failure control is faked; baselines not replayed (BLOCKER)

- `candidate_predict` ignores `serialized_state["belief_logit"]`. Recomputation: belief_logit 0 vs
  99 → identical action. The serialized_state is **causally inert**; "replay recomputes from
  serialized_state" is hollow (the candidate is a pure function of observation+query, which trivially
  reproduces).
- `replay.recompute_replay_record(corrupt_serialized_state=True)` returns `passed=False`
  **unconditionally** (hardcoded), so `failure_controls.corrupted_serialized_state_detected: true`
  is not evidence of detection. A genuine corruption test would show the action *unchanged* (because
  the state is unused), i.e. the control should expose the inert-state defect, not "pass".
- `build_replay_recomputation_report` lists 17 `baseline_callable_paths` and asserts
  `uses_stored_baseline_output: false`, but **never invokes any baseline**. Task Q6 requires "replay
  calls candidate and baselines again" — baselines are not replayed at all.

### B5 — Provenance self-verification is non-fail-able in practice (BLOCKING-weak)

`provenance.verify_computed_evidence_provenance` flags a record as static/literal **only if its
`producer_function` string contains the substrings "literal" or "static"**. No producer is so named,
so the guard never fires — a genuinely literal score (e.g. the tautological 1.0) is not caught.
Every record also carries the **same** `input_artifact_hashes` (one episodes hash) regardless of
result_id; provenance binds all scores to the same episode set but does not tie each score to an
independent recomputation by its named producer (scores are passed in and stamped). Field-presence
is real; fail-ability is cosmetic.

### B6 — "Frozen" equivalence rule is generated at runtime from code, not pre-registered (NON-BLOCKING→borderline)

`build_frozen_equivalence_rule` is built inline during the run; `created_before_run: True` is a
literal field; the margin `0.05` lives in `core.py`. The rule hash reproduces exactly
(`3f77bb04352c9ff1db5b088c9c8b748f39d8c17efc3a5c87558a14fdffc6039c` — verified), so the rule is a
deterministic function of `core.py`, but it is **mutable in source** and not pinned to an external
artifact predating the run. Tie / equivalence / advantage are defined before execution and a faithful
tie *would* force failure (verified via `force_best_baseline_tie` path) — that machinery is sound;
the weakness is the absence of out-of-band pre-registration. Given B2, the as-run rule also produced
the wrong call because it was fed an unfairly weakened baseline score.

---

## FULL-SUITE FAILURE & MUTATION (Q9)

- Reported: 793 passed, 10 failed; full suite mutated old artifacts, "restored before commit".
- **Confirmed:** the commit is clean (no sealed-artifact mutation committed). **Confirmed:** the
  working tree currently holds 1643 unrestored modifications (CRLF rewrite + AGENTS.md governance
  deletion).
- **Not verified by this audit:** the identity of the 10 failing tests. Re-running the full suite
  would itself mutate the sealed historical artifacts under `artifacts/` (the very side-effect under
  scrutiny) and would violate the audit's non-modification posture, so it was not run. The 10
  failures remain unexplained; combined with the unrestored mutation this is, by the project's own
  rule, a blocker.

---

## REQUIRED FIXES (for any future re-submission; not performed here)

1. Remove the candidate↔label tautology: the candidate must infer partner/family/schema latent state
   from training and be evaluated on genuinely held-out families/schemas, with labels not directly
   readable from a candidate-visible observation bit.
2. Make `query_capable_imitation_baseline` (and all faithful baselines) use the **same** access the
   parity artifact claims; if a faithful equal-access baseline ties, report
   `negative_evidence_baseline_equivalence`.
3. Feed the leakage scanner the **real** bundle (episodes, trace, serialized states, observations,
   provenance, result, replay, filenames); delete `_safe_payload`. The clean scan must be able to
   fail — and currently *should* fail on the real bundle.
4. Make replay depend on `serialized_state` causally (or drop the claim); replace the hardcoded
   corruption control with a real recompute-mismatch detector; actually re-invoke baselines in replay.
5. Make the provenance static/literal guard detect literal/static evidence by construction, not by
   function-name substring.
6. Pre-register the equivalence rule as an out-of-band artifact predating the scoring run.
7. Restore the working tree (revert the CRLF rewrite and the AGENTS.md governance-block deletion);
   make the test suite stop writing into sealed `artifacts/`; explain the 10 full-suite failures.

---

## CLAIM CEILING

Independent audit of a local engineering implementation and evidence harness only. This audit does
not assert any Gate4 validity, mechanism validity, social-latent inference, agency, selfhood,
consciousness, emotion, autonomy, or EGO/runtime/companion readiness — for or against. It asserts
only that, on the audited commit, the reported positive result is **not** supported by the produced
evidence.

## WHAT THIS AUDIT DOES NOT PROVE

- It does not prove the underlying *idea* of cross-family social-causal transfer is wrong — only that
  this harness does not test it.
- It does not prove the 10 full-suite failures are benign or malign (unverified).
- It does not assert the working-tree mutation was intentional.
- It is not a Gate4, bridge, admission, or runtime judgement of any kind.

## REMAINING UNKNOWNS

- Identity and cause of the 10 failing full-suite tests.
- Whether the CRLF rewrite + AGENTS.md edit came from the test suite, an editor, or a checkout.
- Whether a corrected, parity-fair, non-tautological harness would yield advantage or equivalence.
