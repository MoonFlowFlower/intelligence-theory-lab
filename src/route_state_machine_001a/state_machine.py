from __future__ import annotations

TASK_ID = "ROUTE-STATE-MACHINE-001A"
TASK_ARTIFACT_DIR = "artifacts/ROUTE-STATE-MACHINE-001A"
PROGRAM_STATE_FILENAME = "program_state.json"
CURRENT_FRONTIER_ROUTE_ID = "N2-SBMC-ENV-REDESIGN-001A"
K0_PARENT_ROUTE_ID = "K0-DUAL-TRACK-SUPERSESSION-001A"
K0_PARENT_ALLOWED_ACTIONS = (
    "bank_ordered_child_cards",
    "run_route_state_machine_validation",
)
K0_PARENT_REQUIRED_FALSE_AUTHORIZATIONS = (
    "agency",
    "autonomy",
    "consciousness",
    "ego_mainline_runtime",
    "experiment_execution",
    "formal_run",
    "foundation_implementation",
    "freeze",
    "h0_implementation",
    "h1_implementation",
    "k0_reference_implementation",
    "mechanism_validity",
    "remote_anchor",
    "scoring",
    "subjectivity",
    "theory_pressure",
    "ui_llm_deployment",
)
K0_READY_PHASE = "FIRST_PAIR_READY_TO_IMPLEMENT"
K0_READY_ALLOWED_ACTIONS = (
    "implement_EGO-K0-FOUNDATION-001A",
    "bank_ITL-K0-H0-H1-INSTRUMENT-001A_H0",
    "run_route_state_machine_validation",
)
K0_READY_AUTHORIZED_IMPLEMENTATION_TARGETS = (
    "EGO-K0-FOUNDATION-001A",
    "ITL-K0-H0-H1-INSTRUMENT-001A:H0",
)
K0_READY_CHILD_AUTHORIZATIONS = {
    "EGO-K0-FOUNDATION-001A": True,
    "ITL-K0-H0-H1-INSTRUMENT-001A:H0": True,
    "EGO-K0-REFERENCE-KERNEL-001A": False,
    "ITL-K0-H0-H1-INSTRUMENT-001A:H1": False,
    "K0-IMMUTABLE-FREEZE-001A": False,
    "ITL-K0-FORMAL-EVIDENCE-001A": False,
}
K0_READY_REQUIRED_TRUE_AUTHORIZATIONS = (
    "foundation_implementation",
    "h0_implementation",
)
K0_READY_REQUIRED_FALSE_AUTHORIZATIONS = tuple(
    key
    for key in K0_PARENT_REQUIRED_FALSE_AUTHORIZATIONS
    if key not in K0_READY_REQUIRED_TRUE_AUTHORIZATIONS
)
K0_READY_CHILD_CARD_BANKS = {
    "ego_foundation": "13bd9268993f74a41b4cc219855761681ab12b66",
    "ego_reference_kernel": "0f043254710b47700f2088213232aba777bd3f46",
    "itl_instrument_freeze_formal": "56f56a998a0ec6e897f98d9ce51a0d8b06eb0f92",
}
K0_READY_BANKED_CARD_OBJECTS = (
    {
        "task_id": "K0-DUAL-TRACK-SUPERSESSION-001A",
        "repo": "intelligence-theory-lab",
        "commit": "56f56a998a0ec6e897f98d9ce51a0d8b06eb0f92",
        "path": "docs/codex/tasks/K0-DUAL-TRACK-SUPERSESSION-001A.md",
        "blob": "11b0e09025d1064a1eb790f42d79f1db3c690f6d",
    },
    {
        "task_id": "EGO-K0-FOUNDATION-001A",
        "repo": "Ego",
        "commit": "13bd9268993f74a41b4cc219855761681ab12b66",
        "path": "docs/codex/tasks/ego-k0-foundation-001a/STAGE_CARD.md",
        "blob": "f100d78e48b8d9b21327ed86a5fb35305d11d534",
    },
    {
        "task_id": "EGO-K0-REFERENCE-KERNEL-001A",
        "repo": "Ego",
        "commit": "0f043254710b47700f2088213232aba777bd3f46",
        "path": "docs/codex/tasks/ego-k0-reference-kernel-001a/STAGE_CARD.md",
        "blob": "55f7ac62bf8aad61b3140c213812d7fb9a166acb",
    },
    {
        "task_id": "ITL-K0-H0-H1-INSTRUMENT-001A",
        "repo": "intelligence-theory-lab",
        "commit": "56f56a998a0ec6e897f98d9ce51a0d8b06eb0f92",
        "path": "docs/codex/tasks/ITL-K0-H0-H1-INSTRUMENT-001A.md",
        "blob": "a642c5734d57af450104b115181a2f7dc18bb646",
    },
    {
        "task_id": "K0-IMMUTABLE-FREEZE-001A",
        "repo": "intelligence-theory-lab",
        "commit": "56f56a998a0ec6e897f98d9ce51a0d8b06eb0f92",
        "path": "docs/codex/tasks/K0-IMMUTABLE-FREEZE-001A.md",
        "blob": "6f01764c2194061fa60c1b84ef6702c7a533cbea",
    },
    {
        "task_id": "ITL-K0-FORMAL-EVIDENCE-001A",
        "repo": "intelligence-theory-lab",
        "commit": "56f56a998a0ec6e897f98d9ce51a0d8b06eb0f92",
        "path": "docs/codex/tasks/ITL-K0-FORMAL-EVIDENCE-001A.md",
        "blob": "c0ce00ff953b389282ba16435ddc884564e2f27e",
    },
)
K0_PARENT_LEDGER_PATH = "docs/research/FSP-STAGE-LEDGER.md"
K0_PARENT_LEDGER_ENTRY_PREFIX = (
    "- L-020 | 2026-07-09 | transition_decision (operator accepted; transcribed by Codex) | "
    "K0 dual-track supersession REGISTERED under "
    "`docs/codex/tasks/K0-DUAL-TRACK-SUPERSESSION-001A.md`."
)
K0_READY_LEDGER_ENTRY_PREFIX = (
    "- L-021 | 2026-07-09 | transition_decision (operator accepted; transcribed by Codex) | "
    "K0 dual-track moved REGISTERED -> READY_TO_IMPLEMENT for exactly "
    "`EGO-K0-FOUNDATION-001A` and `ITL-K0-H0-H1-INSTRUMENT-001A:H0`."
)
K0_READY_TRANSITION_CARD_PATH = "docs/codex/tasks/K0-DUAL-TRACK-READY-TRANSITION-001A.md"

ROUTE_STATES = (
    "PROPOSED",
    "REGISTERED",
    "READY_TO_IMPLEMENT",
    "IMPLEMENTING",
    "RUN_ATTEMPTED",
    "EVIDENCE_PACKET_READY",
    "CLOSURE_REVIEW_REQUIRED",
    "ADJUDICATED",
    "NEXT_FRONTIER_ASSIGNED",
    "REDESIGN_REQUIRED",
    "RERUN_REQUIRED",
    "OPS_FIX_REQUIRED",
    "TOMBSTONED",
)

CLOSURE_TYPES = (
    "THEORY_PRESSURE",
    "INSTRUMENT_INVALID",
    "BASELINE_EQUIVALENCE",
    "IMPLEMENTATION_DEFECT",
    "OPERATION_ERROR",
    "LEAKAGE_OR_CHEATING",
    "METRIC_DEGENERACY",
    "UNDERPOWERED",
    "GOVERNANCE_STOP",
    "INCONCLUSIVE",
    "SCOPE_MISMATCH",
    "ARTIFACT_ONLY",
)

REQUIRED_THEORY_PRESSURE_EVIDENCE = (
    "baseline",
    "ablation",
    "replay",
    "provenance",
)

CURRENT_FRONTIER_FORBIDDEN_AUTHORIZATIONS = (
    "mechanism_validity",
    "theory_pressure",
    "scoring",
    "experiment_execution",
)

CURRENT_FRONTIER_FORBIDDEN_ACTION_TOKENS = (
    "mechanism_validity",
    "mechanism validity",
    "theory_pressure",
    "theory pressure",
    "score",
    "scoring",
    "experiment",
    "execution",
)

AUTHORIZED_TASK_PATHS = (
    "docs/codex/tasks/ROUTE-STATE-MACHINE-001A.md",
    "docs/codex/tasks/ROUTE-STATE-MACHINE-001B-CURRENT-FRONTIER-GATE.md",
    "docs/codex/tasks/K0-DUAL-TRACK-SUPERSESSION-001A.md",
    "docs/codex/tasks/K0-DUAL-TRACK-READY-TRANSITION-001A.md",
    "docs/research/FSP-STAGE-LEDGER.md",
    "docs/research/ROUTE-STATE-MACHINE-001A.md",
    "docs/research/ROUTE-STATE-MACHINE-001B-CURRENT-FRONTIER-GATE.md",
    "src/route_state_machine_001a/__init__.py",
    "src/route_state_machine_001a/routectl.py",
    "src/route_state_machine_001a/state_machine.py",
    "src/route_state_machine_001a/validator.py",
    "tests/route_state_machine_001a/test_validator.py",
    "artifacts/ROUTE-STATE-MACHINE-001A/program_state.json",
    "artifacts/ROUTE-STATE-MACHINE-001A/schemas/route_state.schema.json",
    "artifacts/ROUTE-STATE-MACHINE-001A/schemas/closure_packet.schema.json",
    "artifacts/ROUTE-STATE-MACHINE-001A/routes/PUM-ENV-v0/state.json",
    "artifacts/ROUTE-STATE-MACHINE-001A/routes/PUM-ENV-v0/closure.json",
    "artifacts/ROUTE-STATE-MACHINE-001A/routes/PUM-ENV-v0/events.jsonl",
    "artifacts/ROUTE-STATE-MACHINE-001A/routes/N2-SBMC-ENV-REDESIGN-001A/state.json",
    "artifacts/ROUTE-STATE-MACHINE-001A/routes/N2-SBMC-ENV-REDESIGN-001A/events.jsonl",
    "artifacts/ROUTE-STATE-MACHINE-001A/routes/K0-DUAL-TRACK-SUPERSESSION-001A/state.json",
    "artifacts/ROUTE-STATE-MACHINE-001A/routes/K0-DUAL-TRACK-SUPERSESSION-001A/events.jsonl",
    "artifacts/ROUTE-STATE-MACHINE-001A/STATUS.md",
    "artifacts/ROUTE-STATE-MACHINE-001A/validation_report.json",
)

ROADMAP_LIKE_MARKERS = (
    "roadmap",
    "new-mechanism",
    "mechanism-route",
    "route-candidate",
    "frontier",
    "admission",
    "bridge",
    "mainline",
    "runtime",
    "ego-readiness",
)

TERMINAL_STATES = (
    "ADJUDICATED",
    "NEXT_FRONTIER_ASSIGNED",
    "REDESIGN_REQUIRED",
    "RERUN_REQUIRED",
    "OPS_FIX_REQUIRED",
    "TOMBSTONED",
)
