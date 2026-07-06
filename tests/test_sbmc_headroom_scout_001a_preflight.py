"""STEP-A preflight tests for P0.5-SBMC-ENV-HEADROOM-SCOUT-001A.

These tests validate invariants and preregistration.  They must not run the
aggregate headroom scoring gate or print detector F1.
"""
from __future__ import annotations

import ast
import json
import os
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from sbmc_headroom_scout_001a import detectors as D
from sbmc_headroom_scout_001a import gen_model as GM
from sbmc_headroom_scout_001a import harness as H
from sbmc_headroom_scout_001a import preregister as P

ARTIFACT_PATH = ROOT / "artifacts" / GM.TASK_ID / "preregistration.json"


def test_no_gpu_framework_imports_in_package():
    forbidden = "tor" + "ch"
    package_dir = SRC / "sbmc_headroom_scout_001a"
    for path in package_dir.glob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                assert all(alias.name.split(".")[0] != forbidden for alias in node.names)
            if isinstance(node, ast.ImportFrom) and node.module:
                assert node.module.split(".")[0] != forbidden


def test_item_repr_excludes_audit_fields_and_guard_blocks_non_ideal_leaks():
    user = GM.build_user_case(7)
    for item in user["trusted_seed"] + user["test_set"]:
        assert not GM.item_repr_contains_forbidden_audit(item["item_repr"])

    def malicious_detector(item_repr, user_context, seed):
        _ = item_repr, seed
        return user_context["theta"]

    with pytest.raises(D.GuardViolation):
        H.run_guarded_non_ideal_detector(
            malicious_detector,
            user["test_set"][0]["item_repr"],
            {"trusted_seed": [x["item_repr"] for x in user["trusted_seed"]], "theta": user["theta"]},
            GM.BASE_SEED,
        )


def test_marginal_plausibility_invariant_for_contaminated_items():
    for user_id in range(25):
        user = GM.build_user_case(user_id)
        for item in user["test_set"]:
            if item["audit"]["label"] != "contaminated":
                continue
            edge = GM.edge_key(item["item_repr"]["edge"])
            first_value = int(item["item_repr"]["asserted_tuple"][0][1])
            second_value = int(item["item_repr"]["asserted_tuple"][1][1])
            assert not GM.is_allowed(edge, first_value, second_value)
            assert second_value in GM.marginal_values_for_second_attr(edge)
            assert item["audit"]["contaminated_value_marginally_plausible"] is True


def test_genuine_and_contaminated_share_identical_template_set():
    user = GM.build_user_case(13)
    by_label = {"genuine": set(), "contaminated": set()}
    vocab_by_label = {"genuine": set(), "contaminated": set()}
    for item in user["test_set"]:
        label = item["audit"]["label"]
        by_label[label].add(item["item_repr"]["template_id"])
        vocab_by_label[label].add(tuple(item["item_repr"]["bow_feature_names"]))
    assert by_label["genuine"] == by_label["contaminated"] == {GM.TEMPLATE_ID}
    assert vocab_by_label["genuine"] == vocab_by_label["contaminated"] == {GM.VOCAB}


def test_leakage_positive_control_fires_without_train_eval_overlap():
    report = H.run_leakage_positive_control(
        train_user_ids=list(range(1000, 1020)),
        eval_user_ids=list(range(2000, 2020)),
        seed=GM.derive_seed("leakage_positive_control_test"),
    )
    assert report["train_eval_disjoint"] is True
    assert set(report["train_user_ids"]).isdisjoint(report["eval_user_ids"])
    assert report["clean_scanner_fires"] is False
    assert report["canary_scanner_fires"] is True
    assert report["clean_accuracy"] <= P.build_preregistration()["frozen_thresholds"]["surface_leakage_max"]
    assert report["canary_accuracy"] >= report["clean_accuracy"] + 0.20
    assert report["canary_accuracy"] >= 0.70
    assert report["positive_control_fires"] is True


def test_preregistration_json_validates_and_matches_builder():
    built = P.build_preregistration()
    assert built["frozen_thresholds"]["G_gte_1_5x_MDE"] is True
    assert built["frozen_thresholds"]["G"] >= 1.5 * built["frozen_thresholds"]["MDE"]
    assert ARTIFACT_PATH.exists()
    on_disk = json.loads(ARTIFACT_PATH.read_text(encoding="utf-8"))
    assert on_disk["design_sha256"] == built["design_sha256"]
    assert on_disk["frozen_module_sha256"] == built["frozen_module_sha256"]
    assert on_disk["evaluation_plan_step_b_unrun"]["result_json_forbidden_in_step_a"] is True


def test_feasibility_build_5_dummy_users_under_3s_without_metric_aggregation(capsys):
    report = H.feasibility_build_dummy_users(5)
    assert report["elapsed_seconds"] < 3.0
    assert report["metric_aggregation_performed"] is False
    with capsys.disabled():
        print(
            "FEASIBILITY P0.5-SBMC-ENV-HEADROOM-SCOUT-001A: "
            f"build_5_dummy_users elapsed_seconds={report['elapsed_seconds']:.6f} "
            "metric_aggregation_performed=False"
        )


def test_scoring_gate_defined_but_step_a_result_artifacts_absent():
    assert callable(H.evaluate_headroom_gate)
    H.assert_no_step_a_scoring_artifacts(ROOT)
    forbidden = [
        ROOT / "artifacts" / GM.TASK_ID / "result.json",
        ROOT / "artifacts" / GM.TASK_ID / "baseline_comparison.json",
        ROOT / "artifacts" / GM.TASK_ID / "ablation_report.json",
        ROOT / "artifacts" / GM.TASK_ID / "replay_report.json",
    ]
    assert not any(path.exists() for path in forbidden)
