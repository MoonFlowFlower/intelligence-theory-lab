# _run_src/ — exact executed source for AIDSP-001A-R1

This directory is a **verbatim, bash-readable copy** of the code that produced the
artifacts in `artifacts/AIDSP-001A-R1/`. It exists only as a workaround for a FUSE
read-cache bug in the execution session: files in `src/aidsp_001a_r1/` that were
edited multiple times via the file API were read **truncated/stale** by the
sandbox shell (a known issue in this environment — "trust file-API Read, not bash
reads"). To run reliably, the harness was executed from a sandbox-local assembly
of these files.

- **Canonical deliverable:** `src/aidsp_001a_r1/` (per the task card). Same logic
  and identical frozen constants; the canonical copies carry fuller comments.
- **This copy:** logically identical, terser comments. `code_path_hash` in
  `result.json` is computed over the executed files.

Reproduce:

```
mkdir -p /tmp/run/src && cp -r artifacts/AIDSP-001A-R1/_run_src /tmp/run/src/aidsp_001a_r1
touch /tmp/run/src/__init__.py
PYTHONPATH=/tmp/run python3 -c "from src.aidsp_001a_r1 import harness; harness.main(artifact_dir='/tmp/out')"
```

Other stray files in `artifacts/AIDSP-001A-R1/` (`_canary_fresh.txt`) are debug
residue from diagnosing the FUSE bug; the mount is no-delete so they could not be
removed. They are not evidence.
