# TLGP-001B — PREREG FREEZE (prereg-only; no execution)

- artifact: artifacts/TLGP-001B/prereg.json
- canonical_sha256: `c9f4ba279b75cfc1753a6c6586f11708a9d561bbbff82e8db98859165c580d41`
  (canonical = json.dumps(prereg, sort_keys=True, separators=(",",":"), ensure_ascii=True))
- scope executed this session: PREREG FREEZE ONLY. No training, no 001B execution, no 001A
  edits, no git add/commit/push/tag, no remote anchor.

## Frozen fields
DELTA=0.10 · N_SEEDS=10 (+ LCB = mean-2*std/sqrt(N)) · capacity grid (gru/transformer/mlp,
largest=saturation witness) · training budget (5000/1000/200, adam, lr{1e-3,3e-4}, batch256,
max_epochs200, patience20, steps_max200k, identical across conditions) · split construction
(rule 500/125 disjoint + episode disjoint + REAL/CONTROL value regime; test identical across
conditions) · seed list (RULE_SPLIT 20260701 … MODEL_SEEDS 20260710-19) · verdict enum (3
strings + computed precedence) · source allowlist (src/tlgp_001b/** + artifacts/TLGP-001B/**;
read-only import of 4 001A modules) · forbidden files (001A src/artifact, AUDIT-001, push.*,
CLAUDE.md, global config/schema, EGO mainline) · replay/tamper(>=5 axes)/provenance requirements
· Auto-Remote-Anchor policy (local-only, no auto, push.* BLOCKED).

## Claim ceiling
Bounded offline evidence on whether ONE world's within-episode inference headroom survives
cross-episode amortization. Candidate-free; tests NO mechanism. NOT learning-as-mechanism,
agency, self, feeling, subjectivity, intelligence, or EGO-readiness. Negative either direction
bounded to this world + meta-learner family + capacity grid.

## Next step
May request TRAINING AUTHORIZATION: implementation gate = explicit operator "implement
TLGP-001B" + reference to canonical_sha256 above.
