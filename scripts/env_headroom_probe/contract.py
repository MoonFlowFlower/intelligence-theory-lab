"""Frozen Phase-A contract for BORROW-FIRST-ENV-SELECTION-AND-HEADROOM-PROBE-001A."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from . import PHASE_A_STATUS, TASK_ID

EQUIVALENCE_BAND = 0.05

CONTROL_EXPECTED_VERDICTS: dict[str, str] = {
    "POS_INTERNAL_ESTAR": "HEADROOM",
    "NEG_5A846D5_SCOUT": "SATURATED",
}

FAIR_BASELINE_FLOOR: tuple[str, ...] = (
    "predict_all",
    "predict_none",
    "per_user_lookup",
    "nearest_neighbor",
    "count_table",
    "frequency_marginal",
    "graph_closure",
    "obs_only_decoder",
)

STRUCTURAL_FAIR_BASELINES: tuple[str, ...] = (
    "per_user_lookup",
    "nearest_neighbor",
    "count_table",
    "frequency_marginal",
    "graph_closure",
    "obs_only_decoder",
)

FLOOR_KEY_CONTRACT: dict[str, tuple[str, ...]] = {
    "per_user_lookup": ("lookup_key",),
    "count_table": ("cache_key",),
    "graph_closure": ("relation_pairs", "asserted_tuple"),
    "frequency_marginal": ("frequency_value",),
}

PHASE_B_CANDIDATE_ENVS: tuple[dict[str, str], ...] = (
    {
        "env_id": "minigrid:MiniGrid-MemoryS13Random-v0",
        "adapter_status": "phase_b_symbolic_only_unscored_in_phase_a",
    },
    {
        "env_id": "minigrid:MiniGrid-KeyCorridorS3R1-v0",
        "adapter_status": "phase_b_symbolic_only_unscored_in_phase_a",
    },
    {
        "env_id": "bsuite:memory_len/0",
        "adapter_status": "phase_b_symbolic_only_unscored_in_phase_a",
    },
    {
        "env_id": "bsuite:memory_size/0",
        "adapter_status": "phase_b_symbolic_only_unscored_in_phase_a",
    },
    {
        "env_id": "bsuite:umbrella_length/0",
        "adapter_status": "phase_b_symbolic_only_unscored_in_phase_a",
    },
    {
        "env_id": "dm_alchemy:symbolic_default",
        "adapter_status": "phase_b_drop_and_record_failure_manifest_if_not_cheaply_symbolic",
    },
)

CONTROL_ENV_SOURCES: dict[str, dict[str, Any]] = {
    "POS_INTERNAL_ESTAR": {
        "source_docs": [
            "docs/codex/tasks/SAME-AGENT-KERNEL-R4-CONCRETE-ENV-ARGUMENT-001A.md",
            "artifacts/SAME-AGENT-KERNEL-R4-CONCRETE-ENV-ARGUMENT-001A/r4_concrete_env_argument.json",
        ],
        "expected_verdict": "HEADROOM",
    },
    "NEG_5A846D5_SCOUT": {
        "source_commit": "5a846d51e",
        "source_task": "P0.5-SBMC-ENV-HEADROOM-SCOUT-001A",
        "expected_verdict": "SATURATED",
    },
}


def build_prereg_contract(repo_root: Path | None = None) -> dict[str, Any]:
    """Return the frozen Phase-A contract as data.

    This is metadata only.  It does not instantiate adapters, run baselines, or
    write artifacts.
    """

    root = repo_root or Path.cwd()
    return {
        "task_id": TASK_ID,
        "phase": PHASE_A_STATUS,
        "official_scoring_enabled": False,
        "claim_ceiling": (
            "pre-registration and unscored harness only; no probe_valid, no "
            "candidate-env headroom, no mechanism validity, no mainline effect"
        ),
        "repo_root": str(root),
        "adapter_interface": {
            "record_fields": ["record_id", "split", "group_id", "O", "y", "y_star"],
            "O": "legal observation only; no labels, hidden answers, future observations, filenames, or audit fields",
            "y": "evaluation target, forbidden to fair baselines at prediction time",
            "y_star": "ideal/oracle target, reference ceiling only",
        },
        "control_expected_verdicts": dict(CONTROL_EXPECTED_VERDICTS),
        "control_env_sources": CONTROL_ENV_SOURCES,
        "phase_b_candidate_envs": list(PHASE_B_CANDIDATE_ENVS),
        "fair_baseline_floor": list(FAIR_BASELINE_FLOOR),
        "structural_fair_baselines": list(STRUCTURAL_FAIR_BASELINES),
        "floor_key_contract": {
            baseline_id: list(required_fields)
            for baseline_id, required_fields in FLOOR_KEY_CONTRACT.items()
        },
        "ceiling": {
            "reference": "ideal_oracle",
            "rule": "ceiling_score = ideal_oracle_score; HEADROOM iff ceiling - max(fair_floor) > equivalence_band",
        },
        "equivalence_band": {
            "value": EQUIVALENCE_BAND,
            "rationale": (
                "ex-ante non-hairline band for heterogeneous symbolic envs; "
                "larger band makes HEADROOM harder and should not decide the "
                "large-margin controls"
            ),
        },
        "shuffle_leakage_criterion": {
            "callable": "shuffle_leakage_ok",
            "rule": (
                "under shuffle_O_y, every structural fair baseline must score "
                "<= chance + tol; ideal_oracle is privileged and ignored by "
                "this leakage criterion"
            ),
            "structural_baselines": list(STRUCTURAL_FAIR_BASELINES),
            "tol": EQUIVALENCE_BAND,
            "blocking_policy": "VOID candidate verdicts if any structural baseline remains above chance + tol",
        },
        "floor_competence_guard": {
            "callable": "floor_competence_gate",
            "void_verdict": "VOID_FLOOR_DEGENERATE",
            "rule": "if all structural floor members are no-op/constant on an env, that env verdict is VOID",
        },
        "ablations": ["drop_graph_closure", "shuffle_O_y"],
        "fresh_process_recompute": {
            "mode": "python -m scripts.env_headroom_probe.runner --mode recompute",
            "phase_a_default": "contract only; official controls/candidates require explicit Phase-B authorization",
        },
        "forbidden_phase_a_outputs": [
            "artifacts/BORROW-FIRST-ENV-SELECTION-AND-HEADROOM-PROBE-001A/result.json",
            "artifacts/BORROW-FIRST-ENV-SELECTION-AND-HEADROOM-PROBE-001A/baseline_comparison.json",
            "artifacts/BORROW-FIRST-ENV-SELECTION-AND-HEADROOM-PROBE-001A/ablation_report.json",
            "artifacts/BORROW-FIRST-ENV-SELECTION-AND-HEADROOM-PROBE-001A/replay_report.json",
        ],
    }
