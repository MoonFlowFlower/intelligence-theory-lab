from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

from itl_devbench.core.hashing import sha256_json
from itl_devbench.envs.families import DIMENSION_SPACE, FAMILY_DIMENSIONS, REQUIRED_FAMILY_IDS, TARGET_PRESSURE, TaskFamilyInstance


def load_generator_config(path: str | Path) -> Dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


class TaskFamilyGenerator:
    def __init__(self, config: Dict[str, Any]):
        self.config = config

    def build_spec(self) -> Dict[str, Any]:
        smoke = [self._combination_record(fid, "smoke") for fid in REQUIRED_FAMILY_IDS]
        validation = [self._combination_record(fid, "validation") for fid in REQUIRED_FAMILY_IDS]
        heldout = [self._combination_record(fid, "heldout") for fid in REQUIRED_FAMILY_IDS]
        extrapolation = [self._combination_record(fid, "extrapolation") for fid in REQUIRED_FAMILY_IDS]
        spec = {
            "producer_function": "itl_devbench.envs.task_family_generator.TaskFamilyGenerator.build_spec",
            "families": [
                {
                    "family_id": fid,
                    "dimensions": FAMILY_DIMENSIONS[fid],
                    "target_pressure": TARGET_PRESSURE[fid],
                }
                for fid in REQUIRED_FAMILY_IDS
            ],
            "dimension_space": DIMENSION_SPACE,
            "smoke_split": {"name": "smoke", "combinations": smoke},
            "validation_split": {"name": "validation", "combinations": validation},
            "heldout_split": {"name": "heldout", "combinations": heldout},
            "extrapolation_split": {"name": "extrapolation", "combinations": extrapolation},
            "hidden_rule_sampling": {
                "rule_seed": "100000 + split_offset + family_index * 100 + seed",
                "latent_type": "deterministic parity/hash by family and seed",
            },
            "seed_policy": {
                "smoke": self.config.get("smoke_seeds", [0, 1, 2]),
                "official": self.config.get("official_seeds", list(range(10))),
            },
        }
        spec["split_hash"] = sha256_json(
            {
                "smoke": smoke,
                "validation": validation,
                "heldout": heldout,
                "extrapolation": extrapolation,
            }
        )
        spec["heldout_overlap_with_smoke"] = self.heldout_overlap_with_smoke(spec)
        return spec

    def instances_for_split(self, split: str, seeds: list[int]) -> list[TaskFamilyInstance]:
        instances: list[TaskFamilyInstance] = []
        for family_index, family_id in enumerate(REQUIRED_FAMILY_IDS):
            for seed in seeds:
                instances.append(self.instance_for(family_id=family_id, split=split, seed=seed, stage_index=family_index))
        return instances

    def instance_for(self, family_id: str, split: str, seed: int, stage_index: int | None = None) -> TaskFamilyInstance:
        if family_id not in REQUIRED_FAMILY_IDS:
            raise ValueError(f"unknown_family_id:{family_id}")
        index = REQUIRED_FAMILY_IDS.index(family_id) if stage_index is None else stage_index
        split_offset = {"smoke": 0, "validation": 10000, "heldout": 20000, "extrapolation": 30000}[split]
        rule_seed = 100000 + split_offset + index * 100 + int(seed)
        dimensions = self._dimensions_for_split(family_id, split)
        hidden_rule = self._hidden_rule_for(family_id, seed, split)
        public_observation = self._public_observation_for(family_id, hidden_rule)
        oracle_script = self._oracle_script_for(family_id, hidden_rule)
        signature = sha256_json(public_observation)
        return TaskFamilyInstance(
            family_id=family_id,
            split=split,
            seed=int(seed),
            rule_seed=rule_seed,
            stage_index=index,
            instance_id=f"{split}:{family_id}:{seed}",
            dimensions=dimensions,
            target_pressure=TARGET_PRESSURE[family_id],
            public_observation=public_observation,
            observation_signature=signature,
            hidden_rule=hidden_rule,
            oracle_script=oracle_script,
        )

    def perceptual_aliasing_pair(self, family_id: str) -> tuple[TaskFamilyInstance, TaskFamilyInstance]:
        if family_id != "aliased_food_v1":
            raise ValueError("only_aliased_food_v1_has_required_aliasing_pair")
        return (
            self.instance_for(family_id, "smoke", 0, 0),
            self.instance_for(family_id, "smoke", 1, 0),
        )

    @staticmethod
    def heldout_overlap_with_smoke(spec: Dict[str, Any]) -> list[list[str]]:
        smoke = {tuple(item["dimension_values"]) for item in spec["smoke_split"]["combinations"]}
        heldout = {tuple(item["dimension_values"]) for item in spec["heldout_split"]["combinations"]}
        return [list(item) for item in sorted(smoke.intersection(heldout))]

    def _combination_record(self, family_id: str, split: str) -> Dict[str, Any]:
        dimensions = self._dimensions_for_split(family_id, split)
        return {
            "family_id": family_id,
            "split": split,
            "dimensions": dimensions,
            "dimension_values": [dimensions[key] for key in sorted(dimensions)],
            "target_pressure": TARGET_PRESSURE[family_id],
        }

    def _dimensions_for_split(self, family_id: str, split: str) -> Dict[str, str]:
        dimensions = dict(FAMILY_DIMENSIONS[family_id])
        if split == "heldout":
            dimensions["D0_layout"] = "heldout_layout"
        elif split == "extrapolation":
            dimensions["D7_composition"] = "object_terrain_context"
            dimensions["D2_latent_affordance"] = "compositional_property"
        return dimensions

    def _hidden_rule_for(self, family_id: str, seed: int, split: str) -> Dict[str, Any]:
        parity = (int(seed) + (0 if split == "smoke" else 1)) % 2
        if family_id == "aliased_food_v1":
            return {"latent_type": "nutritive" if parity == 0 else "toxic", "good_reward": 7, "bad_reward": -9}
        if family_id == "delayed_poison_v1":
            return {"latent_type": "delayed_poison" if parity == 0 else "clean_food", "delay_ticks": 9 + (seed % 3)}
        if family_id == "contextual_hazard_v1":
            return {"context": "day" if parity == 0 else "night", "dangerous_context": "day", "safe_reward": 4, "danger_reward": -8}
        if family_id == "rule_reversal_return_v1":
            return {
                "phase_schedule": [
                    {"phase": "A", "start": 0, "end": 5, "good": "red"},
                    {"phase": "B", "start": 6, "end": 11, "good": "blue"},
                    {"phase": "C", "start": 12, "end": 17, "good": "contextual"},
                    {"phase": "A_prime", "start": 18, "end": 23, "good": "red"},
                ]
            }
        if family_id == "info_risk_tradeoff_v1":
            return {"latent_type": "safe_cache" if parity == 0 else "risky_cache", "inspect_cost": -1, "sample_cost": -2}
        raise ValueError(f"unknown_family_id:{family_id}")

    def _public_observation_for(self, family_id: str, hidden_rule: Dict[str, Any]) -> Dict[str, Any]:
        if family_id == "aliased_food_v1":
            return {"local_view": [["empty", "empty", "empty"], ["empty", "food_alias", "empty"], ["empty", "empty", "empty"]], "visible_cues": {}}
        if family_id == "delayed_poison_v1":
            return {"local_view": [["empty", "empty", "empty"], ["empty", "food_delay", "empty"], ["empty", "empty", "empty"]], "visible_cues": {}}
        if family_id == "contextual_hazard_v1":
            return {
                "local_view": [["empty", "empty", "empty"], ["empty", "hazard_alias", "empty"], ["empty", "empty", "empty"]],
                "visible_cues": {"context": hidden_rule["context"]},
            }
        if family_id == "rule_reversal_return_v1":
            return {
                "local_view": [["empty", "red_choice", "empty"], ["empty", "choice_panel", "empty"], ["empty", "blue_choice", "empty"]],
                "visible_cues": {"phase_marker": "visible_but_rule_hidden"},
            }
        if family_id == "info_risk_tradeoff_v1":
            return {"local_view": [["empty", "empty", "empty"], ["empty", "mystery", "empty"], ["empty", "empty", "empty"]], "visible_cues": {"uncertainty": 1.0}}
        raise ValueError(f"unknown_family_id:{family_id}")

    def _oracle_script_for(self, family_id: str, hidden_rule: Dict[str, Any]) -> list[str]:
        if family_id == "aliased_food_v1":
            return ["eat"] if hidden_rule["latent_type"] == "nutritive" else ["wait"]
        if family_id == "delayed_poison_v1":
            return ["wait"] if hidden_rule["latent_type"] == "delayed_poison" else ["eat"]
        if family_id == "contextual_hazard_v1":
            return ["wait"] if hidden_rule["context"] == hidden_rule["dangerous_context"] else ["move"]
        if family_id == "rule_reversal_return_v1":
            return ["left"]
        if family_id == "info_risk_tradeoff_v1":
            return ["eat"] if hidden_rule["latent_type"] == "safe_cache" else ["inspect", "wait"]
        raise ValueError(f"unknown_family_id:{family_id}")
