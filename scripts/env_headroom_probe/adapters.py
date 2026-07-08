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


def _as_label_tuple(value: Any) -> tuple[str, ...] | None:
    if value is None:
        return None
    if isinstance(value, tuple):
        return tuple(str(item) for item in value)
    if isinstance(value, list):
        return tuple(str(item) for item in value)
    return (str(value),)


def decode_oracle_from_O_explicit_field(O: dict[str, Any]) -> tuple[str, ...] | None:
    """Reference decoder for tests: reads only an explicitly legal O field."""

    return _as_label_tuple(O.get("oracle_from_O_target"))


def decode_oracle_from_O_bsuite(O: dict[str, Any]) -> tuple[str, ...] | None:
    """Compute bsuite targets from legal serialized observation history only.

    This function receives only ``O``. It must not inspect private env state,
    rewards, wrappers, filenames, record ids, ``y``, or ``y_star``.
    """

    history = O.get("observation_history")
    env_id = str(O.get("env_id", ""))
    if not isinstance(history, list) or not history:
        return None
    try:
        first_row = history[0][0]
        if env_id.startswith("bsuite:memory_"):
            num_bits = max(0, len(first_row) - 2)
            if num_bits <= 0:
                return None
            query_row = None
            for candidate in reversed(history):
                row = candidate[0]
                if len(row) >= 2 + num_bits and any(float(v) != 0.0 for v in row[2:]):
                    continue
                if len(row) >= 2 and float(row[0]) > 0.0:
                    query_row = row
                    break
            query = 0 if query_row is None else int(float(query_row[1]))
            if query < 0 or query >= num_bits:
                return None
            bit_value = 1 if float(first_row[2 + query]) > 0.0 else 0
            return (f"correct_action:{bit_value}",)
        if env_id.startswith("bsuite:umbrella_"):
            need_umbrella = 1 if float(first_row[0]) > 0.0 else 0
            return (f"correct_pickup:{need_umbrella}",)
    except (IndexError, TypeError, ValueError):
        return None
    return None


def evaluate_oracle_from_O_admission(
    adapter_id: str,
    records: list[ProbeRecord],
    decoder: Callable[[dict[str, Any]], tuple[str, ...] | None],
    *,
    ceiling: float = 1.0,
    tolerance: float = 0.0,
) -> dict[str, Any]:
    """Evaluate whether ``y`` is determined by legal observation ``O``.

    This is an adapter admission check, not candidate scoring. The decoder is
    called with ``record.O`` only; it never receives private env state, rewards,
    ``y``, or ``y_star``.
    """

    eval_rows = [record for record in records if record.split == "eval"]
    if not eval_rows:
        raise ValueError(f"{adapter_id} emitted no eval rows for oracle_from_O admission")
    predictions: list[tuple[str, ...] | None] = [decoder(record.O) for record in eval_rows]
    correct = sum(1 for record, pred in zip(eval_rows, predictions) if pred == record.y)
    score = float(correct / len(eval_rows))
    reaches_ceiling = score >= float(ceiling) - float(tolerance)
    admission_status = (
        "ADMISSIBLE_O_DETERMINED" if reaches_ceiling else "INVALID_TARGET_NOT_O_DETERMINED"
    )
    mismatches = [
        {
            "record_id": record.record_id,
            "expected_y": list(record.y),
            "oracle_from_O_pred": None if pred is None else list(pred),
        }
        for record, pred in zip(eval_rows, predictions)
        if pred != record.y
    ]
    trivial_guard = (
        {
            "producer_function": "trivial_legal_decoder_guard",
            "guard": "VOID_TRIVIALLY_DECODABLE",
            "future_floor_effect": "SATURATED_BY_LEGAL_OBSERVATION_DECODER",
            "reason": (
                "a legal O-only reference decoder reaches the ceiling; future borrowed-env "
                "selection must treat this as floor saturation / void trivial decodability, "
                "not as headroom"
            ),
        }
        if reaches_ceiling
        else {
            "producer_function": "trivial_legal_decoder_guard",
            "guard": "DROP_INVALID_ADAPTER",
            "future_floor_effect": None,
            "reason": "target is not determined by legal O at the declared ceiling",
        }
    )
    return {
        "producer_function": "evaluate_oracle_from_O_admission",
        "adapter_id": adapter_id,
        "oracle_from_O": {
            "decoder": getattr(decoder, "__name__", str(decoder)),
            "input_boundary": "record.O only; no private env state, y, y_star, rewards, filenames, or audit labels",
            "score": score,
            "ceiling": float(ceiling),
            "tolerance": float(tolerance),
            "eval_record_count": len(eval_rows),
            "correct_eval_count": correct,
            "admission_status": admission_status,
            "mismatch_count": len(mismatches),
            "mismatches_preview": mismatches[:5],
        },
        "trivial_floor_guard": trivial_guard,
        "scoring_performed": False,
        "candidate_verdict_computed": False,
    }


def evaluate_borrowed_adapter_admission(
    env_id: str,
    records: list[ProbeRecord],
) -> dict[str, Any]:
    """Run the R1 legal-O admission check for an active borrowed adapter."""

    if env_id.startswith("bsuite:"):
        decoder = decode_oracle_from_O_bsuite
    else:
        raise ValueError(f"no oracle_from_O decoder registered for borrowed adapter {env_id}")
    return evaluate_oracle_from_O_admission(env_id, records, decoder)


def build_minigrid_symbolic_records(env_id: str, seed: int = 20260708, episodes: int = 8) -> list[ProbeRecord]:
    """MiniGrid reset-only adapter is intentionally blocked after R1.

    Claude's fairness finding is accepted here: the prior reset-only O did not
    determine the Memory branch or KeyCorridor object identity, and the target
    would have required private ``unwrapped`` state absent from O.  A future
    card may redesign this as full legal episode-history O, but this callable
    must not emit private-state targets.
    """

    _ = seed, episodes
    raise RuntimeError(
        f"{env_id} MiniGrid reset-only adapter dropped by Phase B-ii-R1: target is not O-determined"
    )


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
        _ = target_meta
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
    "bsuite:memory_len/0": AdapterSpec(
        env_id="bsuite:memory_len/0",
        source="bsuite==0.3.6 symbolic dm_env observation-history adapter",
        status="phase_bii_r1_admissible_o_determined_trivial_decoder_guarded_unscored",
        build_records=_bsuite_builder("memory_len/0"),
        floor_member_status=_common_non_contamination_floor_status(),
        dependency_names=("bsuite", "dm_env"),
        asset_fetch_record=("pip install bsuite==0.3.6 dm_env==1.6; no env assets fetched by adapter",),
    ),
    "bsuite:memory_size/0": AdapterSpec(
        env_id="bsuite:memory_size/0",
        source="bsuite==0.3.6 symbolic dm_env observation-history adapter",
        status="phase_bii_r1_admissible_o_determined_trivial_decoder_guarded_unscored",
        build_records=_bsuite_builder("memory_size/0"),
        floor_member_status=_common_non_contamination_floor_status(),
        dependency_names=("bsuite", "dm_env"),
        asset_fetch_record=("pip install bsuite==0.3.6 dm_env==1.6; no env assets fetched by adapter",),
    ),
    "bsuite:umbrella_length/0": AdapterSpec(
        env_id="bsuite:umbrella_length/0",
        source="bsuite==0.3.6 symbolic dm_env observation-history adapter",
        status="phase_bii_r1_admissible_o_determined_trivial_decoder_guarded_unscored",
        build_records=_bsuite_builder("umbrella_length/0"),
        floor_member_status=_common_non_contamination_floor_status(),
        dependency_names=("bsuite", "dm_env"),
        asset_fetch_record=("pip install bsuite==0.3.6 dm_env==1.6; no env assets fetched by adapter",),
    ),
}


def build_borrowed_adapter_manifest(seed: int = 20260708) -> dict[str, Any]:
    """Return B-ii-R1 borrowed-adapter manifest. Does not score or compute verdicts."""

    wired = {}
    for env_id, spec in sorted(BORROWED_ADAPTERS.items()):
        records = spec.build_records(int(seed))
        admission = evaluate_borrowed_adapter_admission(env_id, records)
        wired[env_id] = {
            "source": spec.source,
            "status": spec.status,
            "record_count": len(records),
            "splits": sorted({record.split for record in records}),
            "record_digest": record_digest(records),
            "oracle_from_O_admission": admission,
            "floor_member_status": spec.floor_member_status,
            "dependency_names": list(spec.dependency_names),
            "asset_fetch_record": list(spec.asset_fetch_record),
        }

    failures = [
        {
            "adapter_id": "minigrid:MiniGrid-MemoryS13Random-v0",
            "reason": (
                "Phase B-ii-R1 fairness repair: single reset observation O does not determine "
                "the target branch; prior target used private unwrapped.success_pos absent from O"
            ),
            "action": "DROP_INVALID_NOT_SINGLE_OBS_ADAPTABLE_BEFORE_SCORING",
        },
        {
            "adapter_id": "minigrid:MiniGrid-KeyCorridorS3R1-v0",
            "reason": (
                "Phase B-ii-R1 fairness repair: single reset observation O does not determine "
                "the target object identity; prior target used private unwrapped.obj absent from O"
            ),
            "action": "DROP_INVALID_NOT_SINGLE_OBS_ADAPTABLE_BEFORE_SCORING",
        },
        {
            "adapter_id": "dm_alchemy:symbolic_default",
            "reason": "dm_alchemy/symbolic_alchemy modules unavailable in current environment; cheap symbolic wiring not feasible",
            "action": "DROP_OPTIONAL_ADAPTER_BEFORE_SCORING",
        },
    ]
    failure_manifest = {
        "producer_function": "build_borrowed_adapter_manifest.failure_manifest",
        "phase": "PHASE_BII_R1_ADAPTER_FAIRNESS_REPAIR_ONLY",
        "policy": "DROP_INVALID_OR_NONCHEAP_ADAPTERS_DO_NOT_FAKE_DO_NOT_SCORE",
        "failures": failures,
    }
    return {
        "producer_function": "build_borrowed_adapter_manifest",
        "phase": "PHASE_BII_R1_ADAPTER_FAIRNESS_REPAIR_ONLY",
        "scoring_performed": False,
        "probe_valid_computed": False,
        "candidate_verdicts_computed": False,
        "wired_adapters": wired,
        "dropped_adapters": {entry["adapter_id"]: entry for entry in failures},
        "dependency_pins": {
            "minigrid": dependency_pin("minigrid"),
            "gymnasium": dependency_pin("gymnasium"),
            "bsuite": dependency_pin("bsuite"),
            "dm_env": dependency_pin("dm_env"),
            "dm_alchemy": dependency_pin("dm_alchemy"),
            "symbolic_alchemy": dependency_pin("symbolic_alchemy"),
        },
        "failure_manifest": failure_manifest,
        "claim_ceiling": (
            "borrowed-adapter fairness hygiene only; no scoring, no headroom, "
            "no probe result, no candidate verdict, no mechanism, no mainline effect"
        ),
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
