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
    "h1_implementation",
    "k0_reference_implementation",
    "mechanism_validity",
    "remote_anchor",
    "scoring",
    "subjectivity",
    "theory_pressure",
    "ui_llm_deployment",
)
K0_PARENT_LEDGER_PATH = "docs/research/FSP-STAGE-LEDGER.md"
K0_PARENT_LEDGER_ENTRY_PREFIX = (
    "- L-020 | 2026-07-09 | transition_decision (operator accepted; transcribed by Codex) | "
    "K0 dual-track supersession REGISTERED under "
    "`docs/codex/tasks/K0-DUAL-TRACK-SUPERSESSION-001A.md`."
)

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
