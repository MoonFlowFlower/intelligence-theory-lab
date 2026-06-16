import ast
import importlib
import inspect
import json
from pathlib import Path
from typing import Any

from .config import ARTIFACT_DIR, SEED_FAMILIES
from .legal_view import FORBIDDEN_LEGAL_KEYS


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, sort_keys=True, indent=2) + "\n", encoding="utf-8")


def _scan_value(value: Any, path: str, hits: list[dict]) -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            lowered = key.lower()
            if any(forbidden in lowered for forbidden in FORBIDDEN_LEGAL_KEYS):
                hits.append({"path": f"{path}.{key}", "reason": "forbidden_key"})
            _scan_value(child, f"{path}.{key}", hits)
    elif isinstance(value, list):
        for idx, child in enumerate(value):
            _scan_value(child, f"{path}[{idx}]", hits)


def scan_legal_episode(legal_episode: dict) -> dict:
    hits: list[dict] = []
    _scan_value(legal_episode, "legal_episode", hits)
    return {"scanner_function": "scan_legal_episode", "scanner_fired": bool(hits), "hits": hits}


def _scan_source_for_generator_import(module_name: str, source_text: str | None = None) -> list[dict]:
    if source_text is None:
        module = importlib.import_module(module_name)
        source_text = inspect.getsource(module)
    tree = ast.parse(source_text)
    hits = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module and node.module.endswith("generator"):
            hits.append({"module": module_name, "reason": "generator_import"})
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.endswith("generator"):
                    hits.append({"module": module_name, "reason": "generator_import"})
    return hits


def scan_import_boundaries(source_text: str | None = None) -> dict:
    modules = [
        "acolb_001a.candidate",
        "acolb_001a.baselines",
        "acolb_001a.amortized_seq",
        "acolb_001a.replay",
    ]
    hits = []
    if source_text is not None:
        hits.extend(_scan_source_for_generator_import("injected_source", source_text))
    else:
        for module_name in modules:
            hits.extend(_scan_source_for_generator_import(module_name))
    return {"scanner_function": "scan_import_boundaries", "scanner_fired": bool(hits), "hits": hits}


def _seed_overlap_report(seed_families: dict[str, list[int]]) -> dict:
    seen = {}
    hits = []
    for family, seeds in seed_families.items():
        for seed in seeds:
            if seed in seen:
                hits.append({"seed": seed, "families": [seen[seed], family]})
            seen[seed] = family
    return {"scanner_fired": bool(hits), "hits": hits}


def run_leakage_controls(output_dir: str | Path = ARTIFACT_DIR) -> dict:
    output_path = Path(output_dir)
    controls = []
    base = {
        "episode_id": "leak-control",
        "probes": [{"action": "p0", "outcome": 0.1, "t": 0}],
        "queries": [{"q_id": "q0", "query_action": "q0", "query_context": {}}],
    }
    injected_cases = {
        "L1": {**base, "queries": [{**base["queries"][0], "truth_outcome": 1.0}]},
        "L2": {**base, "probes": [{**base["probes"][0], "theta": [1.0, 2.0]}]},
        "L3": {**base, "queries": [{**base["queries"][0], "query_context": {"truth_outcome": 1.0}}]},
        "L6": {**base, "probes": [{**base["probes"][0], "legal_theta_alias": [1.0, 2.0]}]},
    }
    for control_id in ("L1", "L2", "L3", "L6"):
        scan = scan_legal_episode(injected_cases[control_id])
        controls.append(
            {
                "control_id": control_id,
                "injected_corruption": control_id,
                "scanner_fired": scan["scanner_fired"],
                "positive_control_ok": scan["scanner_fired"],
            }
        )
    l4_scan = scan_import_boundaries("from .generator import _outcome\n")
    controls.append(
        {
            "control_id": "L4",
            "injected_corruption": "generator_formula_import",
            "scanner_fired": l4_scan["scanner_fired"],
            "positive_control_ok": l4_scan["scanner_fired"],
        }
    )
    contaminated = dict(SEED_FAMILIES)
    contaminated["ood_test"] = [SEED_FAMILIES["train"][0]]
    l5_scan = _seed_overlap_report(contaminated)
    controls.append(
        {
            "control_id": "L5",
            "injected_corruption": "train_heldout_seed_overlap",
            "scanner_fired": l5_scan["scanner_fired"],
            "positive_control_ok": l5_scan["scanner_fired"],
        }
    )
    clean_seed_scan = _seed_overlap_report(SEED_FAMILIES)
    report = {
        "scanner_function": "run_leakage_controls",
        "clean_control_passed": clean_seed_scan["scanner_fired"] is False,
        "controls": sorted(controls, key=lambda row: row["control_id"]),
    }
    _write_json(output_path / "leakage_report.json", report)
    return report
