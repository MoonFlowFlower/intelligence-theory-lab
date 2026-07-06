import importlib
import inspect
import json
import sys
import time
import warnings
from pathlib import Path

import numpy as np


PACKAGE = "src.n1_active_admit_001a"
FORBIDDEN_POLICY_PARAMS = {"m", "j", "structure_id", "hidden_structure"}


def test_modules_import_and_package_has_no_torch_dependency():
    imported = {
        name: importlib.import_module(f"{PACKAGE}.{name}")
        for name in [
            "env_causal",
            "env_bandit",
            "policies",
            "harness",
            "preregister",
        ]
    }

    package_root = Path("src/n1_active_admit_001a")
    source_text = "\n".join(path.read_text(encoding="utf-8") for path in package_root.glob("*.py"))
    assert "torch" not in source_text.lower()
    assert "torch" not in sys.modules
    assert all(imported.values())


def test_envs_are_deterministic_and_shape_correct():
    env_causal = importlib.import_module(f"{PACKAGE}.env_causal")
    env_bandit = importlib.import_module(f"{PACKAGE}.env_bandit")

    causal = env_causal.CausalEnv()
    ep_a = causal.sample_episode(structure_index=0, seed_index=7)
    ep_b = causal.sample_episode(structure_index=0, seed_index=7)
    ep_c = causal.sample_episode(structure_index=0, seed_index=8)

    assert ep_a.observation.shape == (64, 4)
    assert np.array_equal(ep_a.observation, ep_b.observation)
    assert not np.array_equal(ep_a.observation, ep_c.observation)
    assert causal.intervene(ep_a, slot=0) == causal.intervene(ep_b, slot=0)

    bandit = env_bandit.BanditEnv()
    b_a = bandit.sample_episode(seed_index=11)
    b_b = bandit.sample_episode(seed_index=11)
    b_c = bandit.sample_episode(seed_index=12)
    assert b_a.arm_probabilities.shape == (10,)
    assert b_a.horizon == 100
    assert b_a.best_arm == b_b.best_arm
    assert np.array_equal(b_a.reward_table, b_b.reward_table)
    assert (b_a.best_arm != b_c.best_arm) or (not np.array_equal(b_a.reward_table, b_c.reward_table))


class GuardedMemory(dict):
    def __getitem__(self, key):
        if key in {"m", "j", "structure_id"}:
            raise AssertionError(f"policy touched forbidden audit key: {key}")
        return super().__getitem__(key)

    def get(self, key, default=None):
        if key in {"m", "j", "structure_id"}:
            raise AssertionError(f"policy touched forbidden audit key: {key}")
        return super().get(key, default)


def test_policies_are_callable_with_legal_signature_only():
    env_causal = importlib.import_module(f"{PACKAGE}.env_causal")
    policies = importlib.import_module(f"{PACKAGE}.policies")

    causal = env_causal.CausalEnv()
    episode = causal.sample_episode(structure_index=0, seed_index=1)
    memory = GuardedMemory(
        {
            "structure_family": env_causal.enumerate_structures(),
            "train_diagnostic_counts": {0: 2, 1: 2, 2: 0, 3: 0},
            "ucb_stats": {0: {"pulls": 2, "reward": 1.0}},
        }
    )

    for name, policy in policies.build_policy_registry().items():
        signature = inspect.signature(policy)
        assert list(signature.parameters) == ["O", "allowed_memory", "observed_outcome_if_any"]
        assert not (set(signature.parameters) & FORBIDDEN_POLICY_PARAMS)
        result_before = policy(episode.observation, memory, None)
        assert isinstance(result_before, dict), name
        result_after = policy(episode.observation, memory, {"slot": 0, "outcome": 1})
        assert isinstance(result_after, dict), name


def test_leakage_scanner_positive_control_fires_on_synthetic_canary():
    harness = importlib.import_module(f"{PACKAGE}.harness")

    report = harness.synthetic_canary_leakage_positive_control(
        n_rows_per_class=50,
        random_state=20260706,
    )

    assert report["positive_control_triggered"] is True
    assert report["decoder_target"] == "j"
    assert report["score"] > report["chance"]


def test_preregistration_json_is_written_and_power_gate_holds():
    preregister = importlib.import_module(f"{PACKAGE}.preregister")

    artifact_path = Path("artifacts/N1-ACTIVE-ADMIT-001/preregistration.json")
    preregistration = preregister.write_preregistration(artifact_path)
    loaded = json.loads(artifact_path.read_text(encoding="utf-8"))

    assert loaded == preregistration
    assert loaded["task_id"] == "N1-ACTIVE-ADMIT-001"
    assert loaded["step"] == "STEP-A"
    assert loaded["scoring_run_executed"] is False
    assert loaded["result_json_written"] is False
    assert loaded["base_seed"] == 20260706
    assert loaded["E_causal"]["train_j"] == [0, 1]
    assert loaded["E_causal"]["heldout_j"] == [2, 3]
    assert loaded["E_bandit"]["K_arms"] == 10
    assert loaded["thresholds"]["delta_causal_margin"] == 0.20
    assert loaded["thresholds"]["candidate_min_heldout_acc"] == 0.85
    assert loaded["thresholds"]["epsilon_bandit_noninferior"] == 0.05
    assert loaded["power"]["delta_margin_power_gate_passed"] is True
    assert loaded["thresholds"]["delta_causal_margin"] >= 1.5 * loaded["power"]["MDE"]
    assert isinstance(loaded["design_sha256"], str)
    assert len(loaded["design_sha256"]) == 64
    assert loaded["claim_ceiling"] == (
        "signature-level admission only; not mechanism / N1 / agency / consciousness"
    )


def test_feasibility_probe_builds_envs_and_runs_five_dummy_random_episodes_under_2s():
    harness = importlib.import_module(f"{PACKAGE}.harness")

    started = time.perf_counter()
    report = harness.run_feasibility_probe(n_dummy_episodes=5)
    elapsed = time.perf_counter() - started
    line = f"FEASIBILITY_PROBE wall_clock_seconds={elapsed:.6f} dummy_episodes={report['dummy_episodes']}"
    print(line)
    warnings.warn(line, stacklevel=1)

    assert report["dummy_episodes"] == 5
    assert report["metric_aggregation_executed"] is False
    assert elapsed < 2.0
