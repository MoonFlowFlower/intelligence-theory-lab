from __future__ import annotations

TASK_ID = "ROUTE-STATE-MACHINE-001A"
TASK_ARTIFACT_DIR = "artifacts/ROUTE-STATE-MACHINE-001A"

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

AUTHORIZED_TASK_PATHS = (
    "docs/codex/tasks/ROUTE-STATE-MACHINE-001A.md",
    "docs/research/ROUTE-STATE-MACHINE-001A.md",
    "src/route_state_machine_001a/__init__.py",
    "src/route_state_machine_001a/routectl.py",
    "src/route_state_machine_001a/state_machine.py",
    "src/route_state_machine_001a/validator.py",
    "tests/route_state_machine_001a/test_validator.py",
    "artifacts/ROUTE-STATE-MACHINE-001A/schemas/route_state.schema.json",
    "artifacts/ROUTE-STATE-MACHINE-001A/schemas/closure_packet.schema.json",
    "artifacts/ROUTE-STATE-MACHINE-001A/routes/PUM-ENV-v0/state.json",
    "artifacts/ROUTE-STATE-MACHINE-001A/routes/PUM-ENV-v0/closure.json",
    "artifacts/ROUTE-STATE-MACHINE-001A/routes/PUM-ENV-v0/events.jsonl",
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
