# Errata: PREDICTIVE-ACTION-LEARNING-CONTRACT-001C

Non-mutating errata and supersession notes only. The frozen files named below
are NOT edited; this file is the canonical correction record. Source:
independent audit (verdict `independent_audit_pass_with_caveats`,
`docs/audits/PREDICTIVE_ACTION_LEARNING_CONTRACT_001C_INDEPENDENT_AUDIT.md`).

## C1 — Derived headers still show frozen 001 local_mock constants

`artifacts/predictive_action_learning_contract_001c/suite_001c_2026-06-10_t1/CONFIG.json`
and `.../commitment_report.json` header fields read
`commit_mode: local_mock`, `commit_sink_id: local_mock_sink_v1`,
`receipt_type: local_mock`, `externally_verifiable: false`. These are the
frozen 001 reporting constants, kept by design. The run-level records in the
same suite (RUN_META in every trace, every receipt, every anchor log, and the
sample receipts inside commitment_report.json itself) show
`rfc3161_anchored` / `chained_log_rfc3161_anchor`. Reading rule: run-level
records and `result_001c.json` / `FINAL_REPORT_001C.md` supersede the derived
headers for the commitment question. This is a conservative under-claim of
external verifiability, not evidence-run local_mock use: the independent
audit verified zero local_mock commits in evidence runs.

## C2 — replay_report `hidden_state_needed` label for abl4 is misleading

`artifacts/predictive_action_learning_contract_001/suite_2026-06-10_r1/replay_report.json`
(and identically in the 001C suite) records
`abl4_freeze_belief_update: passed=false, hidden_state_needed=true`.
The auto-derived label is misleading: the mismatch reflects runner-logging vs
replay-check field semantics under the belief-freeze ablation (the runner
logs the APPLIED belief, `runner.py:251`, which stays frozen; the replay
check compares the COMPUTED posterior, `validator.py:214`). It is not a core
hidden-state dependency: in all non-ablated runs applied == computed and
core-run replay is exact (max_abs_diff 0.0 at 1e-9). abl9's replay failure is
the structurally expected consequence of an un-traced mid-run memory-deletion
intervention. No gate or claim depends on abl4/abl9 replay (E3 gates core
runs only). The frozen reports are left unmodified; this erratum is the
reading rule.

## C3 — Anchor-step "before reveal" phrasing

Statements that anchors at anchor steps prove commitment "before that step's
own outcome reveal" rely on the RFC 3161 token genTime PLUS the sink's
synchronous control flow (the token is obtained inside `commit()` before the
runner reveals the outcome) and internal monotonic ordering. The external
token alone proves only that the committed chain head existed no later than
genTime. Between-anchor steps (99.49% of commits) rest on internal
attestation bounded above by the next anchor's genTime.

## L1 — No pre-001 VCS freeze evidence (not repairable)

All 001 / 001B / 001C code, docs, and artifacts were untracked in git until
the post-audit canonical freeze. "Thresholds/seeds frozen before the original
001 run" therefore cannot be proven from version control and must not be
claimed; it rests on artifact-internal declarations
(`declared_before_any_run`, threshold justification strings) and file mtimes.
The canonical freeze (`docs/PREDICTIVE_ACTION_LEARNING_CONTRACT_001C_CANONICAL_RECORD.md`)
is post-audit only and provides no retroactive freeze evidence.

## Scope

These errata change no verdict, no metric, no gate, and no claim ceiling.
Maximum claim remains: "001C has passed-with-caveats the independent evidence
audit for bounded isolated Gate 0 predictive-action mechanism evidence."
