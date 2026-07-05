# TLGP-001B-R2-PROVENANCE-BANK-001A

> Status: DRAFT, revised **R1** (2026-06-29) after external red-team audit
> (blocking B1–B4 accepted). Requires explicit operator authorization before any
> `git add` / commit. Provenance-only: NO re-run, NO retraining, **NO source byte
> edit**, NO change to any immutable replay-verified artifact.
> Predecessor audit: `artifacts/CLAUDE-INDEPENDENT-TLGP-001B-R2-OFFICIAL-FULL-RUN-AUDIT-001/`.
> Scientific verdict to be banked (computed + clean-room reproduced, 830,000 rows,
> max Δ 3.9e-15): `tlgp001b_r2_invalid_learnability_floor_failed`.

## R1 revision log (post external red-team)
- **B1 (ingress gap)** — added an explicit hash-verified source-ingress step. A
  clean clone has only HEAD, which does NOT contain the untracked source; the 9
  source files must be ingested from the current worktree under a whitelist
  manifest, then verified.
- **B2 (commit-semantics conflict)** — REMOVED the `official_full.py` B2 verifier
  fix from this card. Editing a runtime source file in the bank commit would make
  banked-source ≠ executed-source. This card now edits NO source and banks the
  executed bytes unmodified. The verifier fix is deferred to
  `TLGP-B2-FUTURE-PIN-FIX-001A`.
- **B3 (anchor unification)** — source anchor = `source_manifest.json:delivered_source_hashes`
  EVERYWHERE (incl. the Falsifying-result line). `SHA256SUMS.txt` is artifact-only
  and is removed from every source gate.
- **B4 (machine-readable B2 limitation)** — `bank_source_reverification.json` must
  carry explicit machine-readable fields recording that B2 is not closable for
  this run.

## Key reframe (why banking is sound even though B2 cannot be closed)
The banked NEGATIVE does not depend on trusting source identity. The verdict
`invalid_learnability_floor_failed` was clean-room reproduced from the TRACE +
frozen prereg alone (audit: 830,000 rows, exact replay), independent of the source.
Source banking here is only for rerun-reproducibility/completeness, and carries a
documented limitation. The source is NOT load-bearing for the verdict.

## Why this card exists (verified current state)
A live-repo check on 2026-06-29 (file-API + git, HEAD `b4ee157a`):
- on-disk `src/tlgp_001b_r2/harness.py` sha256 = `6b32e47e…` = the *executed* hash
  the audit pinned (the audit-time on-disk `8bd467d4` is gone).
- NEW-1: the ENTIRE `src/tlgp_001b_r2/` source tree is UNTRACKED (`git ls-files`=0;
  `git show HEAD:…harness.py` = empty-string hash). The source that produced the
  banked result is in no commit.
- NEW-2: the trace is a Git LFS object — committed HEAD blob = LFS pointer
  (oid `f9d5f47854b91cc107230a2335b12c8c43dad6ffc82b34a2dee0da708ab6c0fd`, size
  `507348934`; ~484 MiB object present in `.git/lfs`). git-lfs is NOT installed in
  the drafting sandbox, so the working tree holds expanded content (shows as
  "modified"); `.gitattributes` differs from HEAD by one trailing CR on the LFS
  rule. These are sandbox artifacts, not content drift.
- B2: the in-run self-check is tautological (`official_full.py:584-585`:
  `delivered = source_hashes()` == `executed = source_hashes()`), so
  `delivered_equals_executed` is always True. No pre-run delivery pin exists.
- AGENTS.md: `git diff --ignore-all-space` empty (EOL-only); it is a forbidden file
  and must not be committed by this task.

Task id: TLGP-001B-R2-PROVENANCE-BANK-001A

Problem definition: bank the already-computed, clean-room-reproduced TLGP-001B-R2
negative into a source-hash-honest commit WITHOUT re-running, retraining, or
editing any source byte or immutable artifact. Ingest the untracked source under a
verified whitelist, keep the LFS trace as its pointer, commit a scoped set, and
record the banking statement and the B2 limitation exactly.

Current stage/layer: engineering evidence-governance / local preservation only.
Not mechanism, not learning, not subjectivity.

Mainline target: local commit on the current branch only. No remote.

Hypothesis (provenance, falsifiable): the working-tree divergences are entirely
explained by untracked-source + LFS-pointer/EOL sandbox artifacts; no immutable
evidence byte and no source byte actually changed vs the executed run. Falsified if
the trace content sha256 ≠ the committed LFS pointer oid `f9d5f478…`, or any
ingested source sha ≠ `source_manifest.json:delivered_source_hashes` — then STOP,
do not bank.

Baseline / comparison: the audit's clean-room replay is the authority; this task
adds no new metric and must REPRODUCE (not recompute differently) the recorded
`recomputed_verdict == result_verdict == tlgp001b_r2_invalid_learnability_floor_failed`.

Trace/replay requirement: a from-trace replay (no retraining, no repo-internal
imports for the clean-room check) must still yield `replay_exact: true`,
`metrics_exact: true`, same verdict; the trace bytes used are the committed
LFS-backed content whose sha256 == pointer oid `f9d5f478…`.

Computed-evidence provenance gate: the banked verdict string must equal the
`compute_verdict` output in `OFFICIAL_FULL_RUN/result.json` (`verdict.py`
7-terminal precedence, branch 2 = `not any(rung0)`); no hand-edit.

Bounded repair steps (each reversible; STOP on any mismatch; **this card edits NO
source byte**):
1. Source ingress (B1): from the current worktree, export exactly the 9 expected
   `src/tlgp_001b_r2/*.py` files (the 9 keys of
   `OFFICIAL_FULL_RUN/source_manifest.json:delivered_source_hashes`). Emit
   `source_ingress_manifest.json` {path, size, sha256} per file. Any missing,
   extra, or out-of-tree path → STOP.
2. Clean LFS bank target (NEW-2): on a machine with git-lfs, clone to scratch and
   `git checkout` HEAD (trace materializes from pointer oid `f9d5f478…`). Copy ONLY
   the whitelisted source files into the clone; copy nothing else. The trace MUST
   stay the LFS pointer — never inline its 507 MB content. Use HEAD's
   `.gitattributes` (LF, no CR); do not introduce the sandbox CR. Confirm
   `git check-attr filter -- <trace>` = `lfs`. If the trace can only be committed
   as inlined content → STOP.
3. Identity verify (B3 anchor): in the clone, recompute sha256 of each ingested
   `src/tlgp_001b_r2/*.py` and compare to
   `source_manifest.json:delivered_source_hashes` (harness pinned `6b32e47e`). Emit
   `bank_source_reverification.json` (fields below).
4. Record B2 honestly; do NOT fix it here: note the in-run gate is tautological and
   that no pre-run pin exists, so `delivered==executed` cannot be asserted for this
   run. Do NOT modify `official_full.py` or any source file. The verifier fix is a
   separate task: `TLGP-B2-FUTURE-PIN-FIX-001A`.
5. Scoped commit ONLY (never `git add -A`, never `scripts/push.*`, never
   `AGENTS.md`/`CLAUDE.md`/global config): add only the whitelisted (unmodified)
   `src/tlgp_001b_r2/` files, `artifacts/TLGP-001B-R2/`,
   `artifacts/CLAUDE-INDEPENDENT-TLGP-001B-R2-*`, and the new
   `bank_source_reverification.json` + `source_ingress_manifest.json`. Commit with
   the exact banking message. Local only.

`bank_source_reverification.json` required fields (B4):
```json
{
  "pre_run_delivery_pin_exists": false,
  "b2_original_gate_status": "tautological_not_closable_for_this_run",
  "posthoc_source_reverification_scope": "current_ingested_equals_runtime_recorded_source_only",
  "may_claim_delivered_equals_executed_for_original_run": false,
  "verdict_validity_basis": "trace_plus_frozen_prereg_clean_room_replay_independent_of_source_identity",
  "per_file": [{"path": "...", "size": 0, "sha256": "...", "matches_delivered_source_hashes": true}]
}
```

Acceptance gate:
- ingress set == exactly the 9 `delivered_source_hashes` keys; no missing/extra/out-of-tree;
- every ingested source sha256 == its `source_manifest.json:delivered_source_hashes` entry;
- committed `official_trace.jsonl` is the LFS pointer (oid `f9d5f478…`, size 507348934),
  NOT inlined; LFS object present/fetchable; `.gitattributes` committed as HEAD (no CR);
- NO source byte modified (`official_full.py` et al. banked as executed bytes); the B2 fix is ABSENT from this commit;
- from-trace replay still `replay_exact:true` / verdict unchanged;
- commit scope = only TLGP-R2 source + TLGP-R2 / TLGP-R2-audit artifacts + the two new provenance JSONs;
- no `AGENTS.md`/`CLAUDE.md`/`scripts/push.*`/unrelated path; no re-run/retraining;
- `bank_source_reverification.json` carries the B4 fields above.

Exact banking statement (verbatim, audit-prescribed — do not paraphrase):
"TLGP-001B-R2 official full run produced bounded INVALID due to learnability-floor
failure under frozen prereg sha
6e61a831c6f287c10c25cccbb09a40671410cd4805214dbd91d62528b2c3d5a7."

Claim ceiling: bounded offline preservation of one negative result only. Banks ONLY
that, on this frozen world + primary meta family (in_context_gru,
in_context_transformer) + frozen capacity grid, the learnability floor was not met
(metas memorized train ~0.97 but collapsed to ~0.45–0.55 on held-out queries of the
same 8 rules, ≪ floor). It does NOT prove the families cannot learn with more
data/diversity/training; it is NOT H0/H1; and it says nothing about mechanism,
learning-as-mechanism, transfer headroom, agency, self, subjectivity, AGI,
companion/EGO readiness. B2 remains recorded-OPEN, not closed.

Stop condition: STOP + emit `failure_manifest.json` if — ingress set ≠ the 9
delivered keys; any ingested source sha ≠ delivered hash; LFS object
absent/unfetchable; trace only committable as inlined content; replay no longer
exact; OR any path would require editing a runtime source file to pass a gate. Do
not bank a patched-over pass.

Rollback plan: the clone is scratch and the worktree is not staged until the final
scoped add. If anything fails, discard the clone and do not commit; leave the
current worktree's TLGP-R2 tree untracked exactly as found; the audit dir remains
the authoritative negative record. No immutable artifact and no source byte is
edited at any step.

Expected changed files: new tracked `src/tlgp_001b_r2/` (added, byte-identical to
the ingested/executed source); new `bank_source_reverification.json` +
`source_ingress_manifest.json` under `artifacts/TLGP-001B-R2/`; this card.
NO `official_full.py` edit. `.gitattributes` committed as HEAD.

Forbidden changes: NO re-run/retraining; NO edit to ANY `src/tlgp_001b_r2/*.py`
(bank executed bytes unmodified — B2 fix is OUT OF SCOPE →
`TLGP-B2-FUTURE-PIN-FIX-001A`); NO edit to `result.json`/`trace_manifest.json`/
`official_trace.jsonl`/`verdict.py` precedence/`prereg.json`/any metric; NO
`git add -A`; NO `AGENTS.md`/`CLAUDE.md`/global config; NO `scripts/push.*`; NO
remote anchor.

Auto-Remote-Anchor: forbidden (prereg `auto_remote_anchor_policy`: remote BLOCKED
until `scripts/push.*` hardcoded-PAT is rotated/removed; any remote is
operator-initiated, scoped explicit `git add`, never `push.py`).

## Bounded Audit

Real objective: a clean, honest commit of an existing negative — not to make the
run "pass" anything.

Strongest invalidity risk: (a) inlining the 507 MB trace instead of its LFS pointer;
(b) editing any runtime source file (incl. `official_full.py`) so banked source ≠
executed source; (c) `git add -A` sweeping in `AGENTS.md`/global churn; (d)
ingesting a non-whitelisted/extra file.

Falsifying result: trace content sha256 ≠ committed LFS pointer oid, or any ingested
source sha ≠ `source_manifest.json:delivered_source_hashes`, or replay no longer
exact → not cleanly bankable; preserve as-is.

Governance self-modification check: NONE in this card — it edits no source and
changes no judge. The B2 verifier fix (which WOULD change the judge) is deferred to
`TLGP-B2-FUTURE-PIN-FIX-001A` and must not be bundled here.

What this does not prove: see claim ceiling. Banking ≠ validating the mechanism, the
learner family, or the transfer question; ≠ closing B2.

## Collision Record

Approach A — re-run TLGP-R2 to regenerate a hash-clean bundle: forbidden (no re-run
authorized; ~28–82h GPU; would bank a different run than the audited one).

Approach B — provenance-only bank with hash-verified source ingress and NO source
edit: selected.

Approach C — leave untracked / do not bank: rejected — loses a citable, clean-room
reproduced negative the capability-witness card must cite.

Approach D — bundle the B2 verifier fix into this bank commit: REJECTED per
red-team B2 — it makes banked-source ≠ executed-source. Deferred to
`TLGP-B2-FUTURE-PIN-FIX-001A`.

Selected approach: Approach B.
