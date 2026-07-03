"""S3a LOG-PARITY trajectory-set instrumentation.

The member-visible canonical stream contains only actions, observations,
session boundaries, and step indices. Full frozen-population raw files are not
persisted when their deterministic canonical bytes exceed the S3a size ceiling;
the recipe and SHA-256 are enough to regenerate them byte-identically.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import inspect
import json
from pathlib import Path
import time
from typing import Any, Iterator, Mapping

import numpy as np

from .simulator import FspPumSimulator, SimulatorVariant


MEMBER_VIEW_KEYS = frozenset(
    {
        "step_index",
        "session_index",
        "turn_in_session",
        "session_boundary",
        "action",
        "observation",
    }
)

DEFAULT_RAW_SIZE_LIMIT_BYTES = 50 * 1024 * 1024
REAL_ENV_MODE = SimulatorVariant.BASE.value


@dataclass(frozen=True)
class TrajectorySetSpec:
    set_id: str
    master_seed: int
    env_mode: str
    partitions: Mapping[str, Mapping[str, int]]
    turns_per_user: int
    logging_policy: Mapping[str, Any]

    def to_json_dict(self) -> dict[str, Any]:
        return {
            "set_id": self.set_id,
            "master_seed": int(self.master_seed),
            "env_mode": self.env_mode,
            "partitions": {
                name: {"start_user_id": int(spec["start_user_id"]), "count": int(spec["count"])}
                for name, spec in self.partitions.items()
            },
            "turns_per_user": int(self.turns_per_user),
            "logging_policy": _jsonable(self.logging_policy),
        }


def load_frozen_design(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def build_generation_specs(design: Mapping[str, Any], *, env_mode: str = REAL_ENV_MODE) -> list[TrajectorySetSpec]:
    SimulatorVariant(env_mode)
    population = design["population_and_data"]
    episodes = design["env_parameters"]["episodes"]
    train_count = int(population["N_train_users"])
    heldout_count = int(population["N_heldout_users"])
    logging_policy = population["log_parity_trajectory_policy"]
    turns_per_user = int(episodes["total_turns_per_user"])
    specs = []
    for index, seed in enumerate(population["env_master_seeds"]):
        specs.append(
            TrajectorySetSpec(
                set_id=f"set_{index:02d}",
                master_seed=int(seed),
                env_mode=env_mode,
                partitions={
                    "train": {"start_user_id": 0, "count": train_count},
                    "heldout": {"start_user_id": train_count, "count": heldout_count},
                },
                turns_per_user=turns_per_user,
                logging_policy=logging_policy,
            )
        )
    return specs


def iter_member_view_records(design: Mapping[str, Any], spec: TrajectorySetSpec) -> Iterator[dict[str, Any]]:
    for _, _, record, _ in _iter_records_with_adjudicator(design, spec):
        yield record


def write_trajectory_set_recipe(
    design: Mapping[str, Any],
    spec: TrajectorySetSpec,
    output_dir: str | Path,
    *,
    raw_size_limit_bytes: int = DEFAULT_RAW_SIZE_LIMIT_BYTES,
) -> dict[str, Any]:
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    start = time.perf_counter()
    member_sha, adjudicator_sha, member_bytes, adjudicator_bytes, record_count = _hash_spec_streams(design, spec)
    wall_clock = time.perf_counter() - start
    storage_mode = (
        "recipe_only_raw_estimate_exceeds_limit"
        if member_bytes > int(raw_size_limit_bytes)
        else "recipe_only_s3a_no_raw_persisted"
    )
    recipe = {
        "task_id": "FSP-PUM-ENV-IDENTIFIABILITY-PROBE-001A",
        "stage": "S3a",
        "visibility": "adjudicator_only_regeneration_recipe_not_member_visible",
        "member_view_visibility": "member-visible canonical bytes are regenerated from this recipe but this recipe itself is not a battery input",
        "spec": spec.to_json_dict(),
        "member_view_sha256": member_sha,
        "adjudicator_only_sha256": adjudicator_sha,
        "member_view_record_count": record_count,
        "member_view_estimated_raw_bytes": member_bytes,
        "adjudicator_only_estimated_raw_bytes": adjudicator_bytes,
        "storage_mode": storage_mode,
        "raw_size_limit_bytes": int(raw_size_limit_bytes),
        "producer_function": "src.fsp_pum_env.trajectory_sets.write_trajectory_set_recipe",
        "generator_code_hash": _generator_code_hash(),
        "wall_clock_seconds": wall_clock,
    }
    recipe_name = f"{spec.set_id}_recipe.json"
    _write_json(out_dir / recipe_name, recipe)
    return {
        "set_id": spec.set_id,
        "env_mode": spec.env_mode,
        "env_master_seed": int(spec.master_seed),
        "generation_params": spec.to_json_dict(),
        "member_view_sha256": member_sha,
        "adjudicator_only_sha256": adjudicator_sha,
        "member_view_record_count": record_count,
        "member_view_estimated_raw_bytes": member_bytes,
        "adjudicator_only_estimated_raw_bytes": adjudicator_bytes,
        "storage_mode": storage_mode,
        "recipe_path": recipe_name,
        "member_visible_files": [],
        "generator_code_hash": _generator_code_hash(),
        "wall_clock_seconds": wall_clock,
    }


def regenerate_member_view_sha256(design: Mapping[str, Any], manifest_entry: Mapping[str, Any]) -> str:
    spec = _spec_from_manifest_entry(manifest_entry)
    member_sha, _, _, _, _ = _hash_spec_streams(design, spec)
    return member_sha


def generate_s3a_trajectory_sets(
    frozen_design_path: str | Path,
    artifact_root: str | Path,
    *,
    env_mode: str = REAL_ENV_MODE,
    raw_size_limit_bytes: int = DEFAULT_RAW_SIZE_LIMIT_BYTES,
) -> dict[str, Any]:
    if env_mode != REAL_ENV_MODE:
        SimulatorVariant(env_mode)
    run_started_at = _utc_timestamp()
    start = time.perf_counter()
    design_path = Path(frozen_design_path)
    design = load_frozen_design(design_path)
    trajectory_dir = Path(artifact_root) / "trajectory_sets"
    specs = build_generation_specs(design, env_mode=env_mode)
    entries = [
        write_trajectory_set_recipe(
            design,
            spec,
            trajectory_dir,
            raw_size_limit_bytes=raw_size_limit_bytes,
        )
        for spec in specs
    ]
    total_member_bytes = sum(int(entry["member_view_estimated_raw_bytes"]) for entry in entries)
    manifest = {
        "task_id": "FSP-PUM-ENV-IDENTIFIABILITY-PROBE-001A",
        "stage": "S3a",
        "artifact": "s3a_trajectory_set_manifest",
        "env_modes_generated": [env_mode],
        "s3a_scope": "REAL-env LOG-PARITY trajectory sets only; NULL-env reuse is parameterized but not generated in S3a",
        "frozen_design_path": str(design_path),
        "population_and_data": _jsonable(design["population_and_data"]),
        "rng_scheme": _jsonable(design["rng_scheme"]),
        "evaluation": _jsonable(design["evaluation"]),
        "member_view_schema": {
            "allowed_keys": sorted(MEMBER_VIEW_KEYS),
            "observation_keys": ["symbol"],
            "forbidden": ["theta", "z", "seeds", "trust internals", "simulator internals"],
        },
        "raw_size_limit_bytes": int(raw_size_limit_bytes),
        "total_member_view_estimated_raw_bytes": total_member_bytes,
        "storage_decision": (
            "recipe_only_raw_estimate_exceeds_limit"
            if total_member_bytes > int(raw_size_limit_bytes)
            else "recipe_only_s3a_no_raw_persisted"
        ),
        "sets": entries,
        "member_visible_files": [],
        "producer_function": "src.fsp_pum_env.trajectory_sets.generate_s3a_trajectory_sets",
        "generator_code_hash": _generator_code_hash(),
        "run_started_at": run_started_at,
        "run_finished_at": _utc_timestamp(),
        "wall_clock_seconds": time.perf_counter() - start,
        "claim_ceiling": "S3a trajectory-set instrumentation only; no gap, baseline-power, environment-validity, learning, mechanism, agency, or EGO claim",
    }
    _write_json(Path(artifact_root) / "s3a_trajectory_set_manifest.json", manifest)
    return manifest


def _iter_records_with_adjudicator(
    design: Mapping[str, Any],
    spec: TrajectorySetSpec,
) -> Iterator[tuple[str, int, dict[str, Any], dict[str, Any]]]:
    env = design["env_parameters"]
    action_set = env["action_set"]
    task_actions = tuple(str(action) for action in action_set["task_actions"])
    recommend_actions = tuple(str(action) for action in action_set["recommend_actions"])
    probe_actions = tuple(str(item["name"]) for item in action_set["probe_actions"])
    all_actions = task_actions + recommend_actions + probe_actions
    turns_per_session = int(env["episodes"]["T_turns_per_session"])
    fixed_schedule = _fixed_probe_schedule_actions(design, spec.turns_per_user)

    for partition_name, partition in spec.partitions.items():
        start_user = int(partition["start_user_id"])
        count = int(partition["count"])
        for trajectory_ordinal in range(count):
            user_id = start_user + trajectory_ordinal
            simulator = FspPumSimulator(design, master_seed=spec.master_seed, variant=spec.env_mode)
            user = simulator.start_user(user_id=user_id)
            rng = np.random.Generator(
                np.random.PCG64(_derive_seed(spec.master_seed, f"eval_query:log_policy:{partition_name}:{user_id}"))
            )
            for step_index in range(spec.turns_per_user):
                session_index = step_index // turns_per_session
                turn_in_session = step_index % turns_per_session
                action = _logging_action(
                    rng,
                    step_index,
                    spec.logging_policy,
                    task_actions,
                    all_actions,
                    fixed_schedule,
                )
                trust_before = float(getattr(user, "trust"))
                z_before = _z_payload(getattr(user, "z_state"))
                result = simulator.step(user, action)
                member_record = {
                    "step_index": int(step_index),
                    "session_index": int(session_index),
                    "turn_in_session": int(turn_in_session),
                    "session_boundary": "start" if turn_in_session == 0 else "none",
                    "action": action,
                    "observation": dict(result.observation),
                }
                adjudicator_record = {
                    "partition": partition_name,
                    "trajectory_ordinal": int(trajectory_ordinal),
                    "user_id": int(user_id),
                    "env_master_seed": int(spec.master_seed),
                    "step_index": int(step_index),
                    "theta": _theta_payload(getattr(user, "theta")),
                    "z_before": z_before,
                    "z_after": _z_payload(getattr(user, "z_state")),
                    "trust_before": trust_before,
                    "trust_after": float(getattr(user, "trust")),
                    "style_map": list(getattr(user, "style_map")),
                    "stable_fact_symbol": int(getattr(user, "stable_fact_symbol")),
                }
                yield partition_name, trajectory_ordinal, member_record, adjudicator_record


def _hash_spec_streams(design: Mapping[str, Any], spec: TrajectorySetSpec) -> tuple[str, str, int, int, int]:
    member_hash = hashlib.sha256()
    adjudicator_hash = hashlib.sha256()
    member_bytes = 0
    adjudicator_bytes = 0
    records = 0
    for partition, trajectory_ordinal, member_record, adjudicator_record in _iter_records_with_adjudicator(design, spec):
        header = f"trajectory\t{partition}\t{trajectory_ordinal}\n".encode("utf-8")
        if member_record["step_index"] == 0:
            member_hash.update(header)
            member_bytes += len(header)
            adjudicator_hash.update(header)
            adjudicator_bytes += len(header)
        member_line = _canonical_line(member_record)
        adjudicator_line = _canonical_line(adjudicator_record)
        member_hash.update(member_line)
        adjudicator_hash.update(adjudicator_line)
        member_bytes += len(member_line)
        adjudicator_bytes += len(adjudicator_line)
        records += 1
    return member_hash.hexdigest(), adjudicator_hash.hexdigest(), member_bytes, adjudicator_bytes, records


def _logging_action(
    rng: np.random.Generator,
    step_index: int,
    logging_policy: Mapping[str, Any],
    task_actions: tuple[str, ...],
    all_actions: tuple[str, ...],
    fixed_schedule: tuple[str, ...],
) -> str:
    mixture = list(logging_policy["mixture"])
    weights = np.asarray([float(item["weight"]) for item in mixture], dtype=float)
    weights = weights / float(weights.sum())
    chosen = mixture[int(rng.choice(len(mixture), p=weights))]
    policy = str(chosen["policy"])
    if policy.startswith("passive:"):
        return task_actions[step_index % len(task_actions)]
    if policy.startswith("uniform random"):
        return str(rng.choice(all_actions))
    if policy.startswith("fixed probe schedule"):
        return fixed_schedule[step_index % len(fixed_schedule)]
    raise ValueError(f"unsupported logging policy: {policy}")


def _fixed_probe_schedule_actions(design: Mapping[str, Any], total_turns: int) -> tuple[str, ...]:
    policy = next(
        item["policy"]
        for item in design["population_and_data"]["log_parity_trajectory_policy"]["mixture"]
        if str(item["policy"]).startswith("fixed probe schedule")
    )
    if "probe-rate 0.2" not in policy or "uniform placement" not in policy:
        raise ValueError("S3a expects the frozen fixed probe schedule to be probe-rate 0.2, uniform placement")
    rates = [float(value) for value in design["probe_scheduling"]["fixed_schedule_grid"]["probe_rates"]]
    placements = [str(value) for value in design["probe_scheduling"]["fixed_schedule_grid"]["placements"]]
    if 0.2 not in rates or "uniform" not in placements:
        raise ValueError("frozen fixed probe schedule grid is missing rate 0.2 / uniform")
    env = design["env_parameters"]
    task_actions = [str(action) for action in env["action_set"]["task_actions"]]
    probe_actions = [str(item["name"]) for item in env["action_set"]["probe_actions"]]
    actions = [task_actions[index % len(task_actions)] for index in range(total_turns)]
    n_probes = int(round(total_turns * 0.2))
    positions = np.linspace(0, total_turns - 1, n_probes)
    for probe_number, position in enumerate(sorted({int(round(value)) for value in positions})):
        actions[position] = probe_actions[probe_number % len(probe_actions)]
    return tuple(actions)


def _spec_from_manifest_entry(entry: Mapping[str, Any]) -> TrajectorySetSpec:
    params = entry["generation_params"]
    return TrajectorySetSpec(
        set_id=str(params["set_id"]),
        master_seed=int(params["master_seed"]),
        env_mode=str(params["env_mode"]),
        partitions={
            name: {"start_user_id": int(spec["start_user_id"]), "count": int(spec["count"])}
            for name, spec in params["partitions"].items()
        },
        turns_per_user=int(params["turns_per_user"]),
        logging_policy=params["logging_policy"],
    )


def _canonical_line(payload: Mapping[str, Any]) -> bytes:
    return (json.dumps(_jsonable(payload), sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def _write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(_jsonable(payload), indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _derive_seed(master_seed: int, stream_name: str) -> int:
    digest = hashlib.sha256(f"{int(master_seed)}:{stream_name}".encode("utf-8")).digest()
    return int.from_bytes(digest[:8], byteorder="big", signed=False)


def _theta_payload(theta: Any) -> dict[str, Any]:
    payload = asdict(theta) if hasattr(theta, "__dataclass_fields__") else dict(theta)
    return _jsonable(payload)


def _z_payload(z_state: Any) -> dict[str, float]:
    payload = asdict(z_state) if hasattr(z_state, "__dataclass_fields__") else dict(z_state)
    return {key: float(value) for key, value in payload.items()}


def _jsonable(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {str(key): _jsonable(val) for key, val in value.items()}
    if isinstance(value, tuple):
        return [_jsonable(item) for item in value]
    if isinstance(value, list):
        return [_jsonable(item) for item in value]
    if isinstance(value, np.integer):
        return int(value)
    if isinstance(value, np.floating):
        return float(value)
    return value


def _generator_code_hash() -> str:
    h = hashlib.sha256()
    simulator_path = Path(inspect.getsourcefile(FspPumSimulator) or "")
    for path in (Path(__file__), simulator_path):
        h.update(path.name.encode("utf-8"))
        h.update(path.read_bytes())
    return h.hexdigest()


def _utc_timestamp() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
