# LRGG-CANDIDATE-FREE-TIER0-2-FREEZE-MANIFEST-WRITE-001A (DRAFT — UNAUTHORIZED)

Task ID: `LRGG-CANDIDATE-FREE-TIER0-2-FREEZE-MANIFEST-WRITE-001A`

```text
STATUS: DRAFT. NOT AUTHORIZED. DO NOT EXECUTE.
This task becomes usable ONLY after the operator returns an explicit accepted 31-field table
(ACCEPT / EDIT:<value> / REJECT for every field) from
docs/codex/tasks/LRGG-CANDIDATE-FREE-TIER0-2-FREEZE-NUMERIC-RESOLUTION-AND-MANIFEST-WRITE-PREP-001A.md
(Part D). Until that table exists, the only permitted action is to stop with
blocked_pending_operator_freeze.
```

Auto-Remote-Anchor: forbidden.

## Status Block

```text
current layer            = engineering-governance / freeze manifest write (transcription only)
mainline integration     = none
enabled status           = none
real trigger evidence    = (required before execution) an explicit operator-accepted 31-field table
claim ceiling            = may only transcribe operator-accepted values/rules into the freeze
                           manifest; proves nothing about LRGG admissibility/headroom/oracle/
                           mechanism/EGO/agency/self/subjectivity/emotion/consciousness/autonomy,
                           H0/H1, or TLGP-001B-R2.
```

## Preconditions (hard gate — stop if any fails)

```text
P1. An explicit operator-accepted 31-field table exists (every field ACCEPT or EDIT:<value>;
    any REJECT or PENDING field -> stop blocked_pending_operator_freeze).
P2. Canonical source readback succeeds via host / file API (NOT the truncating FUSE mount):
    LRGG-CANDIDATE-FREE-PREFLIGHT-001A.md, CHEAP-TIER-EXECUTION-001A.md, FREEZE-MANIFEST-001A.md,
    IMPLEMENTATION-RUN-001A.md, BASELINE-IMMUNITY-ADMISSION-STANDARD-001A.md + .registry.json,
    FREEZE-NUMERIC-RESOLUTION-AND-MANIFEST-WRITE-PREP-001A.md. If readback fails -> stop
    blocked_pending_canonical_readback.
P3. PREFLIGHT host-SHA note verified: host certutil SHA256 of PREFLIGHT-001A.md ==
    764063172F264939FCAA5AEDD3C02AC72659A4B9FED281759E6DBE4502876E47 (case-insensitive). The
    in-sandbox mount is known to truncate PREFLIGHT; the host/file-API value is authoritative.
    If it does not match -> stop blocked_pending_canonical_readback.
P4. The freeze manifest currently has exactly 31 UNFROZEN_OPERATOR_REQUIRED field rows.
```

## Allowed Actions (transcription only)

```text
A1. Replace each of the 31 `UNFROZEN_OPERATOR_REQUIRED` entries in
    docs/codex/tasks/LRGG-CANDIDATE-FREE-TIER0-2-FREEZE-MANIFEST-001A.md with the EXACT
    operator-accepted value/rule (verbatim string from the accepted table).
A2. Leave the manifest's status blocks, claim ceiling, implementation block, and
    "What This Does Not Prove" intact.
A3. Emit a short write report: per-field before/after, manifest SHA256 before/after, and a
    confirmation that zero UNFROZEN_OPERATOR_REQUIRED field rows remain.
```

## Forbidden Actions

```text
- Do NOT infer, optimize, tune, normalize, round, simplify, reorder, or otherwise change any
  operator value. Transcribe verbatim.
- Do NOT add, remove, or rename fields.
- Do NOT weaken or remove the implementation/run block; it must remain.
- Do NOT implement, run, generate, score, build baselines, replay, scan leakage, or tamper-probe.
- Do NOT create artifacts under artifacts/**.
- Do NOT commit, push, tag, or remote-anchor.
- Do NOT emit admissible_for_candidate_preflight, pass, ready, integrated, live, mechanism-valid,
  EGO-ready, or 001C-authorized.
- Do NOT claim LRGG admissibility, headroom, oracle validity, baseline failure, replay/provenance
  validity, leakage-scanner validity, mechanism/agency/self/subjectivity/emotion/consciousness/
  autonomy evidence, EGO readiness, H0/H1, or TLGP-001B-R2 reinterpretation.
```

## Required Return

```text
- per-field transcription diff (before=UNFROZEN_OPERATOR_REQUIRED, after=<operator value>)
- manifest SHA256 before and after the write
- confirmation: unresolved_freeze_fields = 0
- confirmation: implementation/run block preserved
- readback + PREFLIGHT host-SHA verification result
verdict (expected):
  freeze_manifest_filled_from_operator_values_requires_readback_and_separate_run_authorization
allowed alternates:
  blocked_pending_operator_freeze | blocked_pending_canonical_readback |
  refused_due_scope_violation_prevented
```

## Rollback

```text
Single-file revert of LRGG-CANDIDATE-FREE-TIER0-2-FREEZE-MANIFEST-001A.md to its all-UNFROZEN
state. No src/tests/artifacts/contracts/research changes are part of this task or its rollback.
```

## What This Does Not Prove

Filling the manifest proves only that operator-accepted values were transcribed. It does not
prove any LRGG admissibility, headroom, oracle/mechanism/replay/leakage validity, or any
EGO/agency/self/subjectivity/emotion/consciousness/autonomy claim, and it does not authorize
implementation or run. A separate Tier 0-2 run authorization is required after the manifest is
written and read back.
