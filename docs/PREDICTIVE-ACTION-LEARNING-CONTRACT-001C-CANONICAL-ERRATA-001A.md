# PREDICTIVE-ACTION-LEARNING-CONTRACT-001C-CANONICAL-ERRATA-001A

```text
task_id = PREDICTIVE-ACTION-LEARNING-CONTRACT-001C-CANONICAL-ERRATA-001A
layer = engineering implementation layer / evidence-infrastructure errata
verdict = canonical_errata_recorded
generated_utc = 2026-06-11T10:13:27.0917700Z
```

## Purpose

This errata records one protected-file mismatch found by
`FABLE5-DATA-INTEGRITY-PREFLIGHT-001`.

It does not repair, rewrite, regenerate, normalize, or rerun 001C evidence.
It does not add or remove NUL bytes. It does not modify the canonical freeze
manifest. It does not upgrade the 001C evidence claim.

## Canonical Source Boundary

The canonical 001C source remains the freeze commit/tag plus the SHA-256
manifest:

```text
freeze_commit = 4d07f4ec63096ad20e84010da74ee2690c98062b
annotated_tag_object = 606db57f7096d08a5774853eb877171e0ef9a81c
sha256_manifest = artifacts/predictive_action_learning_contract_001c_canonical_freeze/sha256_manifest.json
```

Current worktree convenience copies must not be cited as byte-identical
canonical evidence unless they match the manifest.

## Recorded Mismatch

The current worktree copy of:

```text
docs/PREDICTIVE-ACTION-LEARNING-CONTRACT-001C-CLOSEOUT.md
```

is not byte-identical to the frozen manifest entry.

```text
frozen_expected_sha256 = ae54f6b06e1411f2da535741b8005d6b1311a7cd357477b4df2ec92d18347f78
current_worktree_sha256 = af35d51b8f0c5b49b029438d1115f6534ef68efc79706c0a492c747256b9fd84
frozen_size_bytes = 7815
current_size_bytes = 6976
common_prefix_bytes = 6976
frozen_extra_suffix_bytes = 839
frozen_extra_suffix_nul_count = 839
current_extra_suffix_bytes = 0
classification = worktree_file_differs_from_frozen_manifest_by_missing_trailing_nul_padding
```

The preflight classified the current evidence state as:

```text
fable5_data_integrity_preflight_protected_hash_mismatch
```

Therefore the current worktree evidence state cannot be classified clean.

## Non-Attribution

This errata does not attribute the mismatch to Fable, Claude, Codex, an
attacker, an editor, the operating system, Git, or any other cause. The
available evidence records a byte mismatch and a trailing-NUL difference only.

The model-provenance summary records `Fable = 0` on machine-evidence paths.
That supports only the absence of a Fable term hit in that scan. It does not
prove Fable involvement or non-involvement.

## Claim Ceiling

Maximum allowed claim:

```text
bounded canonical errata record for one known 001C protected-file worktree-vs-freeze mismatch
```

This does not repair 001C evidence, prove tampering, disprove Fable
involvement, validate Gate 1, authorize bridge work, authorize EGO integration,
or establish any stronger mechanism claim.

## Next Allowed Task

A future task may cite canonical 001C evidence only through the freeze
commit/tag and SHA-256 manifest, or must explicitly cite this errata when using
the current worktree convenience copy of `CLOSEOUT.md`.

Any future repair, cleanup, normalization, or refreeze requires a separate
bounded task card.
