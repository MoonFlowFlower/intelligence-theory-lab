# TLGP-001B-R2 — Preregistration Freeze Report

- Authorized scope: `accept_for_prereg_freeze_only` (card TLGP-001B-R2-R1). Freeze prereg ONLY.
- NOT implemented · NO src/tlgp_001b_r2/ · NO training · NO smoke · NO git · R1/001A/audit artifacts untouched.

## Artifact
- Path: `artifacts/TLGP-001B-R2/prereg.json`
- **canonical_sha256 (authoritative): `6e61a831c6f287c10c25cccbb09a40671410cd4805214dbd91d62528b2c3d5a7`**
- raw_bytes_sha256 (on-disk pretty): `2a2c2217d61f2b598ff5a96aeabadad5a746b8b9b4bcc6caf781d2d7f6772b91`
- Canonical scheme: json.dumps(obj, sort_keys=True, separators=(",",":"), ensure_ascii=True) — identical to R1.
- Readback: reload from mount → recompute canonical sha256 → MUST equal the authoritative constant.

## Frozen fields (committed BEFORE any run)
- Inherited verbatim from R1/001A: DELTA=0.1, FLOOR=0.2, N_SEEDS=10, close>=9/10, LCB=mean-2σ/√N,
  world {K5,D3,M5,ACTION_CARD5,N_ADAPT24,N_QUERY30,values{0,1,2}/{3,4}}, rule mod-5, 625 rules, split 500/125,
  capacity_grid (UNCHANGED), training_budget (Adam, lr{1e-3,3e-4}, batch256, epochs200, patience20, steps200k,
  5000/1000/200), RULE_SPLIT_SEED + MODEL_SEEDS + SHUFFLE/BASELINE_FIT/LEAK seeds.
- NEW (chosen blind to R1 scores): R0_RULES (8 from TRAIN_RULES, full values), RUNG0/1/2/3 + R0_RULES_SELECT seeds.
- family_roles: PRIMARY adjudicators {in_context_gru, in_context_transformer}; DIAGNOSTIC-only amortized_summary_mlp
  (never gates); eligibility E = primary passing rung0 AND rung1.
- rungs: rung0 learnability floor (8 rules, full values, fit+heldout) · rung1 seen-rule capability (TRAIN_RULES,
  seen values, NEW episodes) · rung2 seen-rule {3,4} value-extrapolation (evaluates the rung3 model; diagnostic) ·
  rung3 REAL unseen-rule+unseen-value (=R1 REAL).
- rung1_scanner: query↔adapt overlap, lookup solve rate, count_table/predict_all/majority/no_context_meta vs
  ideal_seen1 (from seen-rule support, NOT assumed 1.0), cheap_baseline_saturation flag + interpretation rule.
- verdict_enum: 7 terminals (H1, H0, invalid_leakage_or_replay, invalid_learnability_floor_failed,
  invalid_no_capability_witness, invalid_discriminativeness_or_ablation, invalid_inconclusive_underpowered).
- precedence: integrity→rung0→rung1→discriminativeness→H0(affirmative)→H1(affirmative)→inconclusive (NO else→H0).
- trace/replay: EVERY rung incl. rung0 + rung1 + diagnostic family predictions recorded; verdict recomputable
  no-retrain (fixes R1's replay gap).
- forbidden_files + claim_ceiling (global + per-INVALID-terminal) frozen.

## Status
Prereg FROZEN. Implementation NOT authorized — requires (2) explicit operator "implement TLGP-001B-R2"
referencing canonical sha `6e61a831c6f287c10c25cccbb09a40671410cd4805214dbd91d62528b2c3d5a7` + (3) this frozen prereg (now exists & verifies).
