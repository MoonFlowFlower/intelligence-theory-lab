TASK: BORROW-FIRST-ENV-SELECTION-AND-HEADROOM-PROBE-001A  (design card in outputs; bank it first)

PHASE A — pre-registration freeze, NO scoring, then STOP:
1. Bank the card at docs/codex/tasks/BORROW-FIRST-ENV-SELECTION-AND-HEADROOM-PROBE-001A.md
   (verbatim from the drafted file).
2. Write docs/codex/tasks/...-STEP-A-PREREG-001A.md freezing: env set, adapter (O, y, y*) interface,
   the fair-baseline floor family (predict_all/none, per_user_lookup, nearest_neighbor, count_table,
   frequency_marginal, graph_closure/arc-consistency, obs-only decoder, ideal/oracle),
   ceiling def, equivalence_band = <state a number + ex-ante rationale>, and the control
   expected-verdicts (POS-INTERNAL E* = HEADROOM, NEG 5a846d5 = SATURATED).
3. Implement in scripts/env_headroom_probe/ (ISOLATED): adapters for E* (from R4 spec) and the
   5a846d5 scout; the frozen battery; the callable verdict function; the probe_valid gate; the
   two ablations (drop graph_closure; shuffle O-y). Each RNG framework (np/random/torch-if-used)
   seeded explicitly; provide a fresh-process recompute mode.
4. Do NOT score candidate envs yet. Commit Phase A (git reset -> add -- explicit paths -> commit ->
   push). This commit is the ex-ante ancestor. STOP and hand to Claude for Red-audit.

PHASE B — only after Claude Red-audit passes:
5. Wire adapters: MiniGrid (1-2 configs), bsuite subset (memory_len/size + one generalization env),
   Alchemy symbolic ONLY if cheaply feasible (else drop + record in failure_manifest, do not fake).
6. Run battery on {controls, candidate envs}; verify probe_valid==true; if false, VOID all
   candidate verdicts, write failure_manifest.json, STOP.
7. Two fresh-process recomputes must match bit-exact before writing verdicts.
8. Emit artifacts under artifacts/BORROW-FIRST-.../: result.json (per-env verdict + probe_valid),
   trace.jsonl, baseline_comparison.json, ablation_report.json, replay_report.json, reuse_matrix.json,
   claim_ceiling.txt, failure_manifest.json if anything fails. Preserve failures. No baseline
   weakening, no band change, no SATURATED->HEADROOM patching.
FORBIDDEN: src/ mechanism code, N2/R4 frozen specs, pixel/physics envs, global config, candidate/
attribution/mechanism code, remote anchor, credentials.
