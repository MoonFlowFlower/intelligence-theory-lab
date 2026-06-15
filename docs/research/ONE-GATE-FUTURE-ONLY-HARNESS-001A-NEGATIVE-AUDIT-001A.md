# ONE-GATE-FUTURE-ONLY-HARNESS-001A Negative Audit 001A

Task id: `PRESERVE-ONE-GATE-FUTURE-ONLY-HARNESS-001A-NEGATIVE-AUDIT-001A`

Anchor under audit: `cb95bbdb06c9fadbbbf7765ae61acc46609ed994`

Tag under audit: `remote-anchor-one-gate-future-only-non-circular-evidence-harness-001a-cb95bbd`

Verdict: `harness_001a_blocked_by_candidate_authored_ground_truth`

Independent audit verdict preserved: `partially_real_but_circular_at_ground_truth`

## Layer And Status

Current layer: engineering-governance / future-only harness negative audit preservation and route downgrade only.

Mainline integration status: none.

Enabled status: no new enabled path; the harness was not repaired, not applied to Gate3/Gate4, not wired into integrated admission, bridge, runtime, companion, or EGO mainline.

Real trigger evidence: bounded temp rerun through the existing harness evaluator plus static audit readback. The rerun changed only candidate-authored `serialized_state.policy_map` while holding observations/actions/predictions fixed.

Claim ceiling: future-only harness negative audit preservation and route downgrade only.

Next minimal closed-loop action: run a separate independent-ground-truth preflight for the intended Gate target; if no harness-owned, candidate-inaccessible truth source exists, downgrade the Gate evidence route instead of repairing this harness again.

## Bounded Audit

Problem definition: the anchored future-only harness removes candidate declaration and producer-selection control, but still fails non-circularity because metric, replay, and baseline ground truth is derived from candidate-authored `serialized_state.policy_map`.

Strongest positive baseline: the previous harness claim was that six verifier-001B-derived positive controls block, a raw fixture scores through a harness-owned metric, baseline/ablation/replay execute, and the original local test set passed. This preservation did not rerun the original test set; it rechecked the decisive non-circularity contrast.

Strongest reason the previous framing is invalid: a candidate can author the truth channel used by the scorer, replay checker, and majority baseline while avoiding the blocked candidate-declared evidence fields.

Falsifier for this negative framing: the same observations/actions with only `policy_map` changed would not change score/admission, or the harness would prove that `policy_map` is harness-owned and candidate-inaccessible. The rerun did not show that.

Evidence that remains insufficient: a name-level leakage scanner, a harness-owned metric registry, and successful local positive controls do not establish independent ground truth when the scorer's expected action still comes from candidate-authored serialized state.

Mechanism-vs-resemblance classification: this audit tests an engineering evidence contract boundary only. It does not test mechanism validity.

Anti-hardcoding / leakage check: the failure is a value-channel leakage and circular-truth failure, not a missing forbidden field-name rule. Adding another field-name blacklist here would not make the harness non-circular.

Stop condition: do not repair this harness, apply it to a real Gate, mutate old artifacts, or reframe this audit as a passing non-circular evidence contract.

Rollback plan: if preservation fails, leave source unchanged and treat the route as blocked. No repair is authorized in this task.

Auto-Remote-Anchor decision: authorized by the task card only if acceptance gates pass and final worktree is clean with exact local HEAD / remote branch / local tag / remote tag equality. At preservation time, remote anchoring is blocked by pre-existing out-of-scope modified files.

## Preserved Negative Evidence

The audit's key finding is preserved as follows:

```text
The cb95bbd future-only harness removes candidate declaration / producer-selection
control, but fails non-circularity because candidate-authored policy_map controls
the scoring, replay, and baseline ground truth. It must not be used as a Gate
evidence contract.
```

Decisive contrast preserved:

```text
same observations/actions/predictions + self-consistent candidate-authored policy_map
  -> score 1.0 / admitted

same observations/actions/predictions + flipped candidate-authored policy_map
  -> blocked
```

Baseline-equivalence issue preserved:

```text
Degenerate all-"approach" self-consistent fixture:
  candidate score: 1.0
  majority baseline score: 1.0
  candidate admitted: true
  acceptance gates all pass despite equivalence: true
```

Leakage positive-control weakness preserved:

```text
policy_map in leakage field-name set: false
signal in leakage field-name set: false
self-endorsing leakage hit count: 0
positive control detected: true
weakness: scanner mostly tests forbidden field names, not value-channel leakage.
```

## Computed Evidence Readback

Fresh command run:

```powershell
python -B artifacts\one_gate_future_only_harness_001a_negative_audit_001a\reproduce_policy_map_contrast.py
```

Fresh command verdict:

```text
harness_001a_blocked_by_candidate_authored_ground_truth
```

Artifact directory:

```text
artifacts/one_gate_future_only_harness_001a_negative_audit_001a/
```

Generated files:

```text
claim_ceiling.txt
contrast_report.json
output_hashes.json
reproduce_policy_map_contrast.py
result.json
route_decision.json
source_integrity.json
```

Output hashes:

```text
claim_ceiling.txt: abe88f9a3e89d2116861f320784c5e16324c3ed1e35342b1decf5aebd480af0e
contrast_report.json: 623d16d77ed333ee419bf89bb2a9421cdc014b6900e5b111325522d9ee32039a
result.json: deb00b70c02f4929c7566348a3f5ddfc0533f00b5bd64f8347f79bdf44c01fdb
route_decision.json: e2e4e530b64bdce53f912d1e94c2dccbf330fd60d03b64fb4188fc03e1beef3a
source_integrity.json: c29556c972ba6e4af71b3f64be33aa7e2d75021dab51604d25877c65d529c89c
```

Input hashes recorded in `result.json` / `contrast_report.json`:

```text
self-endorsing payload: 54c4221fe41b707511d219fd208ad937f609c69360cb8722e6cb7295002e6086
flipped payload: 2bb4436cab10dd0315417e0be94276aa838706d7cadd47ac6139a0e556c26ea3
degenerate baseline-equivalent payload: a1314c9c1425b6af5f72a9c32c3d6a47d485f910e5fb2fa40b008a4303d1cfdf
fixed observations/actions/predictions surface: c5138d41b3cac9c1add51f1c93065df79ae3c891686ec1757006dcc15cc99c27
```

Harness source hash recorded:

```text
src/one_gate_future_only_non_circular_harness_001a/runner.py
sha256: cb3b7e5ebbc05a8d3fd68a163f931eba684a9080692ed020e997a86dffc6cf98
```

## Route Decision

`cb95bbd` harness must not be used as a Gate evidence contract.

Downgraded route:

```text
prototype / negative evidence: candidate-authored ground truth failure
```

Safe flags:

```text
safe_to_wire_gate3: false
safe_to_wire_gate4: false
safe_to_wire_bridge: false
safe_to_wire_ego_mainline: false
safe_to_wire_runtime: false
```

This route decision does not repair the harness and does not authorize Gate, bridge, runtime, integrated admission, companion, or EGO-mainline use.

## Scope Readback

Allowed files changed by this preservation:

```text
docs/research/ONE-GATE-FUTURE-ONLY-HARNESS-001A-NEGATIVE-AUDIT-001A.md
artifacts/one_gate_future_only_harness_001a_negative_audit_001a/**
```

Forbidden source paths were not modified by this task:

```text
src/one_gate_future_only_non_circular_harness_001a/**
src/evidence_admission_verifier_001a/**
Gate3/Gate4 source or artifacts
integrated admission / bridge / runtime / mainline files
```

Pre-existing out-of-scope dirty files observed before preservation:

```text
docs/NEGATIVE_EVIDENCE_LEDGER.md
theories/failed_claims.yaml
```

Those files were not edited by this task, but their dirty state blocks clean-worktree acceptance and remote anchoring unless separately resolved.

## What This Does Not Prove

This does not prove Gate validity, mechanism validity, integrated admission readiness, mainline effect, bridge readiness, runtime readiness, agency, consciousness, emotion, autonomy, stable user benefit, companion readiness, or EGO readiness.
