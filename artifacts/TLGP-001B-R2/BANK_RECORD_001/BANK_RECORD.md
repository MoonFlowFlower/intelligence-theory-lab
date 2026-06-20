# TLGP-001B-R2 Bank Record 001

Task id: `TLGP-001B-R2-BANK-RECORD-001`

Bank status: `banked_bounded_invalid`

Exact bank label:

`TLGP-001B-R2 official full run produced bounded INVALID due to learnability-floor failure under frozen prereg sha 6e61a831c6f287c10c25cccbb09a40671410cd4805214dbd91d62528b2c3d5a7`

## Scope

Current layer: engineering evidence-governance / provenance banking only.

Mainline integration status: none. No EGO mainline, runtime, admission, bridge, product behavior, or agent capability integration.

Enabled status: no runtime enabling. This record only records an already accepted isolated offline TLGP-001B-R2 official full-run bundle as banked bounded INVALID.

## Trigger Evidence

Independent B3-only short re-audit verdict:

`accept_b3_agents_cleanup__official_bundle_bankable_as_bounded_invalid`

The older full-run audit at `artifacts/CLAUDE-INDEPENDENT-TLGP-001B-R2-OFFICIAL-FULL-RUN-AUDIT-001/` required B1-B3 repair before banking. This is a successor bank record after the accepted B3-only short re-audit.

## Verdict Boundary

Official scientific verdict:

`tlgp001b_r2_invalid_learnability_floor_failed`

Bounded INVALID reason:

Rung0 learnability floor failed before Rung3 could adjudicate H0/H1.

Frozen prereg:

- Path: `artifacts/TLGP-001B-R2/prereg.json`
- Canonical sha256: `6e61a831c6f287c10c25cccbb09a40671410cd4805214dbd91d62528b2c3d5a7`
- Raw bytes sha256: `2a2c2217d61f2b598ff5a96aeabadad5a746b8b9b4bcc6caf781d2d7f6772b91`

Official result:

- Path: `artifacts/TLGP-001B-R2/OFFICIAL_FULL_RUN/result.json`
- SHA256: `3e0a2aaac4c76f6354ff9b4aef5c8c5e24aa0c8b349f11c7677ccc0ba23035ad`

Trace:

- Path: `artifacts/TLGP-001B-R2/OFFICIAL_FULL_RUN/traces/official_trace.jsonl`
- SHA256: `f9d5f47854b91cc107230a2335b12c8c43dad6ffc82b34a2dee0da708ab6c0fd`

## B3 Provenance Note

- Sandbox raw git output superficially showed dirty `AGENTS.md`.
- That was attributed to FUSE null-padding plus CR/autocrlf environment artifacts.
- Decisive proof: stripping only NUL and CR from worktree `AGENTS.md` produced bytes whose `git hash-object` exactly equaled `git rev-parse HEAD:AGENTS.md`.
- `AGENTS.md` content therefore equals the HEAD governance content after removing environment artifacts.
- Prior forbidden governance drift and EOF whitespace blocker are closed.
- Index was empty.
- HEAD was unchanged.
- No add, commit, push, tag, or remote-anchor was performed during B3 cleanup.
- No TLGP-001B-R2 science, prereg, result, trace, replay, leakage, or ablation artifact was modified.

Codex authoritative machine clean readback preserved:

- `git diff --ignore-space-at-eol -- AGENTS.md`: empty
- `git diff -w -- AGENTS.md`: empty
- `git rev-parse HEAD:AGENTS.md`: `742c637e8390afbb5a3af363f0d5e1762bf5724b`
- `git hash-object AGENTS.md`: `742c637e8390afbb5a3af363f0d5e1762bf5724b`
- `git status --short -- AGENTS.md`: empty
- `git diff --cached --name-status`: empty
- `git diff --name-status`: empty
- HEAD: `c142443e9b85a2087e569a3f74a9f8fdd05ac32c`

## Non-Mutation Statement

This bank-record task did not rerun training, reinterpret Rung3 as H1, downgrade 001A, advance to 001C, modify prereg, modify harness source, modify result, modify trace, modify replay/leakage/ablation artifacts, modify the scientific verdict, modify thresholds, budget, grid, or seeds, modify `AGENTS.md`, modify `CLAUDE.md`, or touch mainline/runtime/admission files.

## Claim Ceiling

This bank record proves only that the TLGP-001B-R2 official full run is bankable as bounded offline INVALID due to learnability-floor failure under frozen prereg/codepath/budget/grid/seeds.

It does not prove learning-as-mechanism, agency, self, feeling, subjectivity, intelligence, autonomy, runtime readiness, companion readiness, EGO readiness, mainline effect, theory failure, H0, H1, or 001A downgrade.

Auto-remote-anchor: forbidden. No remote anchor is authorized by this bank-record task.

## Next Minimal Action

Route decision is separate after bank.
