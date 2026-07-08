"""Adapters for the Phase-A borrow-first headroom probe.

Adapters expose the frozen ``(O, y, y*)`` record interface.  Official control
and borrowed-env scoring is intentionally not invoked by Phase-A tests.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from hashlib import sha256
import importlib.metadata
import importlib.util
import json
import random
from pathlib import Path
from typing import Any, Callable, Iterable


@dataclass(frozen=True)
class ProbeRecord:
    record_id: str
    split: str
    group_id: str
    O: dict[str, Any]
    y: tuple[str, ...]
    y_star: tuple[str, ...]

    def to_json_obj(self) -> dict[str, Any]:
        return {
            "record_id": self.record_id,
            "split": self.split,
            "group_id": self.group_id,
            "O": self.O,
            "y": list(self.y),
            "y_star": list(self.y_star),
        }


@dataclass(frozen=True)
class AdapterSpec:
    env_id: str
    source: str
    status: str
    build_records: Callable[[int], list[ProbeRecord]]
    floor_member_status: dict[str, dict[str, str]] = field(default_factory=dict)
    dependency_names: tuple[str, ...] = tuple()
    asset_fetch_record: tuple[str, ...] = tuple()


def _label(value: int | str) -> tuple[str, ...]:
    return (str(value),)


def canonical_json(data: Any) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"))


def record_digest(records: Iterable[ProbeRecord]) -> str:
    payload = [record.to_json_obj() for record in records]
    return sha256(canonical_json(payload).encode("utf-8")).hexdigest()


def build_unit_synthetic_records(seed: int = 0) -> list[ProbeRecord]:
    """Tiny synthetic fixture for tests and fresh-process plumbing only."""

    rng = random.Random(int(seed))
    records: list[ProbeRecord] = []
    for split in ("train", "eval"):
        for idx in range(6):
            value = idx % 3
            target = "good" if value == 0 else "bad"
            records.append(
                ProbeRecord(
                    record_id=f"unit-{split}-{idx}",
                    split=split,
                    group_id="unit",
                    O={
                        "schema_version": "env_headroom_probe.observation.v1",
                        "unit_value": value,
                        "cache_key": f"k{value}",
                        "lookup_key": f"k{value}",
                        "frequency_value": f"v{value}",
                        "jitter": rng.randrange(10_000),
                    },
                    y=(target,),
                    y_star=(target,),
                )
            )
    return records


def build_pos_internal_estar_records(seed: int = 20260708) -> list[ProbeRecord]:
    """Build the internal E* positive-control record interface.

    This encodes the R4 E* additive Latin-square structure as legal observations
    with latent row/column codes absent.  Fair cache-like baselines see only
    row/column factor ids and train examples; the ideal/oracle receives y*.
    """

    rng = random.Random(int(seed))
    n = 5
    L = 5
    a_code = list(range(L))
    b_code = [2, 4, 1, 3, 0]
    train_cells = {(r, 0) for r in range(n)} | {(0, k) for k in range(n)}
    records: list[ProbeRecord] = []
    for r in range(n):
        for k in range(n):
            split = "train" if (r, k) in train_cells else "eval"
            y = (a_code[r] + b_code[k]) % L
            # No relation table, no latent code, no answer-bearing filename.
            obs = {
                "schema_version": "env_headroom_probe.observation.v1",
                "env_family": "R4_ESTAR_ADDITIVE_LATIN",
                "row_factor": r,
                "col_factor": k,
                "cache_key": f"cell:{r}:{k}",
                "lookup_key": f"cell:{r}:{k}",
                "frequency_value": f"row:{r}",
                "one_factor_signature": f"row:{r}" if rng.random() < 0.5 else f"col:{k}",
            }
            records.append(
                ProbeRecord(
                    record_id=f"estar-{split}-r{r}-k{k}",
                    split=split,
                    group_id="estar",
                    O=obs,
                    y=_label(y),
                    y_star=_label(y),
                )
            )
    return records


def build_neg_5a846d5_scout_records(seed: int = 20260706) -> list[ProbeRecord]:
    """Adapt the lookup-solvable 5a846d5 scout into the common interface.

    The current source tree for ``src/sbmc_headroom_scout_001a`` has no source
    diff against commit ``5a846d5`` for the package files.  This adapter imports
    that frozen generator shape read-only and converts records.  It does not
    write artifacts.
    """

    from src.sbmc_headroom_scout_001a import gen_model as GM

    records: list[ProbeRecord] = []
    user_ids = [100, 101, 102, 103]
    for user_id in user_ids:
        case = GM.build_user_case(user_id)
        for split_name, items in (("train", case["trusted_seed"]), ("eval", case["test_set"])):
            for item in items:
                item_repr = item["item_repr"]
                edge = tuple(int(x) for x in item_repr["edge"])
                asserted = item_repr["asserted_tuple"]
                pair = (int(asserted[0][1]), int(asserted[1][1]))
                label = "contaminated" if item["audit"]["label_binary"] else "genuine"
                obs = {
                    "schema_version": "env_headroom_probe.observation.v1",
                    "env_family": "P0.5_SBMC_SCOUT_5a846d5",
                    "user_id": int(user_id),
                    "edge": list(edge),
                    "asserted_tuple": asserted,
                    "lookup_key": f"u{user_id}:edge{edge}:first{pair[0]}",
                    "cache_key": f"edge{edge}:pair{pair}",
                    "frequency_value": f"attr{asserted[1][0]}:value{asserted[1][1]}",
                    "relation_pairs": [list(p) for p in GM.RELATION_TABLES[edge]],
                }
                records.append(
                    ProbeRecord(
                        record_id=f"5a846d5-{item['item_id']}",
                        split=split_name,
                        group_id=f"user:{user_id}",
                        O=obs,
                        y=(label,),
                        y_star=(label,),
                    )
                )
    _ = seed
    return records


def _sha256_file(path: str | None) -> str | None:
    if not path:
        return None
    file_path = Path(path)
    if not file_path.exists() or not file_path.is_file():
        return None
    return sha256(file_path.read_bytes()).hexdigest()


def dependency_pin(distribution_name: str, module_name: str | None = None) -> dict[str, Any]:
    """Return local dependency version + import-origin hash for audit manifests."""

    module = module_name or distribution_name
    spec = importlib.util.find_spec(module)
    try:
        version = importlib.metadata.version(distribution_name)
    except importlib.metadata.PackageNotFoundError:
        version = None
    origin = None if spec is None else spec.origin
    return {
        "distribution": distribution_name,
        "module": module,
        "installed": spec is not None and version is not None,
        "version": version,
        "origin": origin,
        "origin_sha256": _sha256_file(origin),
    }


def _canonical_array(value: Any) -> Any:
    try:
        import numpy as np  # type: ignore

        if isinstance(value, np.ndarray):
            return value.tolist()
        if isinstance(value, np.generic):
            return value.item()
    except Exception:
        pass
    if isinstance(value, (list, tuple)):
        return [_canonical_array(item) for item in value]
    if isinstance(value, dict):
        return {str(k): _canonical_array(v) for k, v in sorted(value.items())}
    return value


def _hash_obj(value: Any) -> str:
    return sha256(canonical_json(_canonical_array(value)).encode("utf-8")).hexdigest()


def _split_for_index(index: int, count: int) -> str:
    return "train" if index < max(1, count // 2) else "eval"


def _common_non_contamination_floor_status() -> dict[str, dict[str, str]]:
    return {
        "per_user_lookup": {
            "status": "populated",
            "legal_source": "adapter observation-derived lookup_key",
        },
        "nearest_neighbor": {
            "status": "populated",
            "legal_source": "full legal observation object",
        },
        "count_table": {
            "status": "populated",
            "legal_source": "adapter observation-derived cache_key",
        },
        "frequency_marginal": {
            "status": "N/A",
            "reason": (
                "non-contamination env; current frequency_marginal baseline emits "
                "contaminated/genuine labels and would be a straw floor"
            ),
        },
        "graph_closure": {
            "status": "N/A",
            "reason": "no legal relation_pairs/asserted_tuple arc-consistency surface in symbolic adapter",
        },
        "obs_only_decoder": {
            "status": "populated",
            "legal_source": "legal symbolic observation object",
        },
    }


def build_minigrid_symbolic_records(env_id: str, seed: int = 20260708, episodes: int = 8) -> list[ProbeRecord]:
    """Build MiniGrid borrowed symbolic adapter records without scoring.

    The adapter uses the public Gymnasium observation (`image`, `direction`) as
    O. Mission strings that contain target color/type are not copied into O;
    the target is kept only in y/y_star for audit/label separation.
    """

    import gymnasium as gym  # type: ignore
    import minigrid  # type: ignore  # registers MiniGrid env ids

    _ = minigrid

    records: list[ProbeRecord] = []
    for episode_idx in range(int(episodes)):
        env = gym.make(env_id, render_mode=None)
        try:
            obs, _info = env.reset(seed=int(seed) + episode_idx)
            unwrapped = env.unwrapped
            image = _canonical_array(obs["image"])
            direction = int(obs["direction"])
            image_hash = _hash_obj(image)
            if env_id == "MiniGrid-MemoryS13Random-v0":
                success_pos = tuple(int(v) for v in getattr(unwrapped, "success_pos"))
                center_y = int(getattr(unwrapped, "height")) // 2
                target = "match_branch:upper" if success_pos[1] < center_y else "match_branch:lower"
                mission_schema = "go_to_matching_object_constant"
            elif env_id == "MiniGrid-KeyCorridorS3R1-v0":
                obj = getattr(unwrapped, "obj")
                target = f"pickup:{str(obj.color)}:{str(obj.type)}"
                mission_schema = "pick_up_color_object_target_redacted"
            else:
                raise ValueError(f"unsupported MiniGrid borrowed env: {env_id}")

            O = {
                "schema_version": "env_headroom_probe.observation.v1",
                "adapter_family": "minigrid_symbolic",
                "env_id": f"minigrid:{env_id}",
                "observation_kind": "gymnasium_reset_symbolic",
                "image": image,
                "direction": direction,
                "mission_schema": mission_schema,
                "lookup_key": f"minigrid:{env_id}:view:{image_hash}:dir:{direction}",
                "cache_key": f"minigrid:{env_id}:view:{image_hash}",
            }
            records.append(
                ProbeRecord(
                    record_id=f"minigrid-{env_id}-seed{seed}-ep{episode_idx}",
                    split=_split_for_index(episode_idx, int(episodes)),
                    group_id=f"minigrid:{env_id}",
                    O=O,
                    y=(target,),
                    y_star=(target,),
                )
            )
        finally:
            env.close()
    return records


def _bsuite_env_episode_target(env: Any, bsuite_id: str) -> tuple[str, dict[str, Any]]:
    if bsuite_id.startswith("memory_"):
        context = _canonical_array(getattr(env, "_context"))
        query = int(getattr(env, "_query"))
        return f"correct_action:{int(context[query])}", {
            "target_source": "bsuite_memory_chain_context_query_ground_truth",
            "query_index": query,
        }
    if bsuite_id.startswith("umbrella_"):
        need_umbrella = int(getattr(env, "_need_umbrella"))
        return f"correct_pickup:{need_umbrella}", {
            "target_source": "bsuite_umbrella_chain_need_umbrella_ground_truth",
        }
    raise ValueError(f"unsupported bsuite borrowed env: {bsuite_id}")


def build_bsuite_symbolic_records(bsuite_id: str, seed: int = 20260708, episodes: int = 8) -> list[ProbeRecord]:
    """Build bsuite borrowed symbolic adapter records without scoring.

    O contains legal observation history only. Private env state is used only to
    form y/y_star ground truth, not as fair-baseline input.
    """

    import contextlib
    import io

    import numpy as np  # type: ignore
    from bsuite import load_from_id  # type: ignore

    records: list[ProbeRecord] = []
    for episode_idx in range(int(episodes)):
        with contextlib.redirect_stdout(io.StringIO()):
            env = load_from_id(bsuite_id)
        if hasattr(env, "_rng"):
            env._rng = np.random.RandomState(int(seed) + episode_idx)
        ts = env.reset()
        observations = [_canonical_array(ts.observation)]
        target, target_meta = _bsuite_env_episode_target(env, bsuite_id)
        action = 0
        safety_steps = 0
        while not ts.last() and safety_steps < 256:
            ts = env.step(action)
            observations.append(_canonical_array(ts.observation))
            safety_steps += 1
        if not ts.last():
            raise RuntimeError(f"bsuite adapter failed to reach terminal for {bsuite_id}")
        history_hash = _hash_obj(observations)
        O = {
            "schema_version": "env_headroom_probe.observation.v1",
            "adapter_family": "bsuite_symbolic",
            "env_id": f"bsuite:{bsuite_id}",
            "observation_kind": "dm_env_observation_history",
            "observation_history": observations,
            "action_history_policy": "constant_zero_for_adapter_trace_only",
            "lookup_key": f"bsuite:{bsuite_id}:history:{history_hash}",
            "cache_key": f"bsuite:{bsuite_id}:history:{history_hash}",
        }
        if "query_index" in target_meta:
            O["query_index_from_legal_final_observation"] = target_meta["query_index"]
        records.append(
            ProbeRecord(
                record_id=f"bsuite-{bsuite_id.replace('/', '_')}-seed{seed}-ep{episode_idx}",
                split=_split_for_index(episode_idx, int(episodes)),
                group_id=f"bsuite:{bsuite_id}",
                O=O,
                y=(target,),
                y_star=(target,),
            )
        )
        _ = seed
    return records


def _minigrid_builder(env_id: str) -> Callable[[int], list[ProbeRecord]]:
    return lambda seed: build_minigrid_symbolic_records(env_id, seed)


def _bsuite_builder(bsuite_id: str) -> Callable[[int], list[ProbeRecord]]:
    return lambda seed: build_bsuite_symbolic_records(bsuite_id, seed)


BORROWED_ADAPTERS: dict[str, AdapterSpec] = {
    "minigrid:MiniGrid-MemoryS13Random-v0": AdapterSpec(
        env_id="minigrid:MiniGrid-MemoryS13Random-v0",
        source="minigrid==3.1.0 / gymnasium==1.3.0 symbolic reset observation adapter",
        status="phase_bii_wired_unscored_pending_claude_red_precheck",
        build_records=_minigrid_builder("MiniGrid-MemoryS13Random-v0"),
        floor_member_status=_common_non_contamination_floor_status(),
        dependency_names=("minigrid", "gymnasium"),
        asset_fetch_record=("pip install minigrid==3.1.0 gymnasium==1.3.0; no env assets fetched by adapter",),
    ),
    "minigrid:MiniGrid-KeyCorridorS3R1-v0": AdapterSpec(
        env_id="minigrid:MiniGrid-KeyCorridorS3R1-v0",
        source="minigrid==3.1.0 / gymnasium==1.3.0 symbolic reset observation adapter",
        status="phase_bii_wired_unscored_pending_claude_red_precheck",
        build_records=_minigrid_builder("MiniGrid-KeyCorridorS3R1-v0"),
        floor_member_status=_common_non_contamination_floor_status(),
        dependency_names=("minigrid", "gymnasium"),
        asset_fetch_record=("pip install minigrid==3.1.0 gymnasium==1.3.0; no env assets fetched by adapter",),
    ),
    "bsuite:memory_len/0": AdapterSpec(
        env_id="bsuite:memory_len/0",
        source="bsuite==0.3.6 symbolic dm_env observation-history adapter",
        status="phase_bii_wired_unscored_pending_claude_red_precheck",
        build_records=_bsuite_builder("memory_len/0"),
        floor_member_status=_common_non_contamination_floor_status(),
        dependency_names=("bsuite", "dm_env"),
        asset_fetch_record=("pip install bsuite==0.3.6 dm_env==1.6; no env assets fetched by adapter",),
    ),
    "bsuite:memory_size/0": AdapterSpec(
        env_id="bsuite:memory_size/0",
        source="bsuite==0.3.6 symbolic dm_env observation-history adapter",
        status="phase_bii_wired_unscored_pending_claude_red_precheck",
        build_records=_bsuite_builder("memory_size/0"),
        floor_member_status=_common_non_contamination_floor_status(),
        dependency_names=("bsuite", "dm_env"),
        asset_fetch_record=("pip install bsuite==0.3.6 dm_env==1.6; no env assets fetched by adapter",),
    ),
    "bsuite:umbrella_length/0": AdapterSpec(
        env_id="bsuite:umbrella_length/0",
        source="bsuite==0.3.6 symbolic dm_env observation-history adapter",
        status="phase_bii_wired_unscored_pending_claude_red_precheck",
        build_records=_bsuite_builder("umbrella_length/0"),
        floor_member_status=_common_non_contamination_floor_status(),
        dependency_names=("bsuite", "dm_env"),
        asset_fetch_record=("pip install bsuite==0.3.6 dm_env==1.6; no env assets fetched by adapter",),
    ),
}


def build_borrowed_adapter_manifest(seed: int = 20260708) -> dict[str, Any]:
    """Return B-ii borrowed-adapter manifest. Does not score or compute verdicts."""

    wired = {}
    for env_id, spec in sorted(BORROWED_ADAPTERS.items()):
        records = spec.build_records(int(seed))
        wired[env_id] = {
            "source": spec.source,
            "status": spec.status,
            "record_count": len(records),
            "splits": sorted({record.split for record in records}),
            "record_digest": record_digest(records),
            "floor_member_status": spec.floor_member_status,
            "dependency_names": list(spec.dependency_names),
            "asset_fetch_record": list(spec.asset_fetch_record),
        }

    failure_manifest = {
        "producer_function": "build_borrowed_adapter_manifest.failure_manifest",
        "phase": "PHASE_BII_BORROWED_ADAPTER_WIRING_ONLY",
        "policy": "DROP_OPTIONAL_DM_ALCHEMY_DO_NOT_FAKE",
        "failures": [
            {
                "adapter_id": "dm_alchemy:symbolic_default",
                "reason": "dm_alchemy/symbolic_alchemy modules unavailable in current environment; cheap symbolic wiring not feasible",
                "action": "DROP_OPTIONAL_ADAPTER_BEFORE_SCORING",
            }
        ],
    }
    return {
        "producer_function": "build_borrowed_adapter_manifest",
        "phase": "PHASE_BII_BORROWED_ADAPTER_WIRING_ONLY",
        "scoring_performed": False,
        "candidate_verdicts_computed": False,
        "wired_adapters": wired,
        "dropped_adapters": {
            "dm_alchemy:symbolic_default": failure_manifest["failures"][0],
        },
        "dependency_pins": {
            "minigrid": dependency_pin("minigrid"),
            "gymnasium": dependency_pin("gymnasium"),
            "bsuite": dependency_pin("bsuite"),
            "dm_env": dependency_pin("dm_env"),
            "dm_alchemy": dependency_pin("dm_alchemy"),
            "symbolic_alchemy": dependency_pin("symbolic_alchemy"),
        },
        "failure_manifest": failure_manifest,
        "claim_ceiling": "borrowed-adapter wiring only; no headroom, no probe result, no mechanism, no mainline effect",
    }


ADAPTERS: dict[str, AdapterSpec] = {
    "UNIT_SYNTHETIC": AdapterSpec(
        env_id="UNIT_SYNTHETIC",
        source="unit-test synthetic fixture; not an official control or candidate env",
        status="phase_a_unit_only",
        build_records=build_unit_synthetic_records,
    ),
    "POS_INTERNAL_ESTAR": AdapterSpec(
        env_id="POS_INTERNAL_ESTAR",
        source="docs/codex/tasks/SAME-AGENT-KERNEL-R4-CONCRETE-ENV-ARGUMENT-001A.md",
        status="phase_a_registered_control_unscored_until_phase_b_authorized",
        build_records=build_pos_internal_estar_records,
    ),
    "NEG_5A846D5_SCOUT": AdapterSpec(
        env_id="NEG_5A846D5_SCOUT",
        source="git commit 5a846d51e / src/sbmc_headroom_scout_001a",
        status="phase_a_registered_control_unscored_until_phase_b_authorized",
        build_records=build_neg_5a846d5_scout_records,
    ),
}
