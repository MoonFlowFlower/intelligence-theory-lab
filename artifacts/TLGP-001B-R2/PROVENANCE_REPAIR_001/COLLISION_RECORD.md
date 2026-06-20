# TLGP-001B-R2 Official Bundle Provenance Repair 001 Collision Record

Task id: `TLGP-001B-R2-OFFICIAL-BUNDLE-PROVENANCE-REPAIR-001`

Current layer: engineering implementation + mechanism-hypothesis preflight provenance repair.

Real objective: repair and document official bundle provenance blockers B1-B3 without rerunning training, changing preregistration, changing the scientific verdict, mutating official traces/results, or advancing to 001C.

## Candidate Approaches

### Candidate 1: Minimal Artifact-Only Repair

- Evidence produced: current on-disk R2 source SHA256 values compared against official executed/pinned source hashes; B1/B3 readbacks; prereg/result/trace readbacks; repair reports under `PROVENANCE_REPAIR_001`.
- Strongest cheap baseline that could match it: a report that only restates official manifest fields without recomputing current hashes.
- Leakage / hard-coding risk: low if every current hash is recomputed from disk and compared fail-closed to the executed manifest.
- Smallest falsifying test: alter one current R2 source hash or compare against a missing file; verifier must report mismatch/blocker.
- Expected failure mode: a current source file differs from the official executed hash, requiring `blocked_source_hash_mismatch_persists`.

### Candidate 2: Patch Future Manifest Logic

- Evidence produced: source code would stop using `source_hashes() == source_hashes()` for future runs.
- Strongest cheap baseline that could match it: green future-oriented tests while current official bundle remains source-hash ambiguous.
- Leakage / hard-coding risk: high for this task because changing `official_full.py` would make current on-disk source diverge from the executed official source.
- Smallest falsifying test: current `official_full.py` hash no longer equals the official executed/pinned hash.
- Expected failure mode: violates provenance-only scope and creates a new B2-style drift for the already executed official result.

### Candidate 3: Rerun Official Full Bundle

- Evidence produced: a new official bundle with internally current source hashes.
- Strongest cheap baseline that could match it: rerun-shaped closure that changes the evidence object instead of repairing provenance for the existing bundle.
- Leakage / hard-coding risk: high; rerun could change timestamps, logs, traces, and scientific artifacts.
- Smallest falsifying test: any new `--full` run output or modified training/result/trace artifact appears.
- Expected failure mode: directly violates the task prohibition on rerunning TLGP-001B-R2 training/full run.

## Selection

Selected approach: Candidate 1, minimal artifact-only repair.

Reason: it directly addresses B1-B3 with recomputed, fail-closed provenance evidence while preserving the official scientific result, preregistration, trace data, and executed source code path.

Claim ceiling: provenance repair only; no Gate, mechanism, learning, agency, subjectivity, consciousness, EGO readiness, runtime readiness, companion readiness, or mainline-effect claim.

Stop condition: any current on-disk R2 source hash differs from its official executed/pinned hash; prereg canonical SHA differs from the frozen expected SHA; `AGENTS.md` cannot be reverted/read back cleanly; or any forbidden drift appears.

Rollback plan: remove only files created under `artifacts/TLGP-001B-R2/PROVENANCE_REPAIR_001/`; no scientific source/result/trace changes are part of the selected approach.
