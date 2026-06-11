from __future__ import annotations

import argparse
import inspect
import json
from pathlib import Path
from typing import Any

from cmbc_companion.evals.verify_growth_loop import (
    ACTION_HANDLES,
    CMBCGrowthLoopCandidate,
    make_trace,
    replay_decisions,
)


ALLOWED_VERDICTS = {
    "selector_static_action_handle_bottleneck_confirmed",
    "selector_parametric_but_adapter_missing",
    "renderer_static_dependency_blocks_expansion",
    "replay_contract_blocks_expansion",
    "baseline_contract_blocks_expansion",
    "inconclusive_needs_manual_review",
}

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SOURCE_FAILURE_PATH = PROJECT_ROOT / "artifacts/cmbc_companion_action_space_expansion_004_execute/action_space_expansion_004_result.json"

AUDIT_PATHS = [
    PROJECT_ROOT / "cmbc_companion/evals/verify_growth_loop.py",
    PROJECT_ROOT / "cmbc_companion/evals/consolidation_000.py",
    PROJECT_ROOT / "cmbc_companion/evals/feedback_admission_000.py",
    PROJECT_ROOT / "cmbc_companion/demos/lab_console_000.py",
    PROJECT_ROOT / "cmbc_companion/demos/free_input_live_lab_003_reexecute.py",
    PROJECT_ROOT / "cmbc_companion/demos/action_space_expansion_004_execute.py",
]

CLAIM_AFTER_RCA = (
    "CMBC has bounded free-input causal-probe evidence under the current small "
    "7-action anonymous action set. Expanded action-space advantage is not "
    "established because the frozen selector is not parametric over action space."
)


def write_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def relative(path: Path) -> str:
    return str(path.relative_to(PROJECT_ROOT)).replace("/", "\\")


def classify_dependency(path: Path, line: str) -> str:
    text = line.strip()
    rel = relative(path)
    if rel.endswith("verify_growth_loop.py"):
        if "PUBLIC_ACTION_NAMES" in text:
            return "post_selection_renderer_dependency"
        if "ACTION_HANDLES" in text:
            return "primary_selector_bottleneck"
        if "for handle in effect_estimates.items()" in text:
            return "partially_parametric_baseline_only"
    if rel.endswith("consolidation_000.py"):
        return "consolidation_trace_and_prior_static_dependency"
    if rel.endswith("feedback_admission_000.py"):
        return "feedback_admission_import_static_handles"
    if rel.endswith("lab_console_000.py"):
        if "PUBLIC_ACTION_NAMES" in text:
            return "post_selection_renderer_dependency"
        return "demo_trace_static_dependency"
    if rel.endswith("free_input_live_lab_003_reexecute.py"):
        return "free_input_probe_small_action_dependency"
    if rel.endswith("action_space_expansion_004_execute.py"):
        return "diagnostic_execution_detects_static_selector"
    return "static_action_dependency"


def dependency_reason(path: Path, line: str) -> str:
    rel = relative(path)
    text = line.strip()
    if rel.endswith("verify_growth_loop.py") and "def choose" in text:
        return "selector entry point has no candidate-options argument"
    if rel.endswith("verify_growth_loop.py") and "for handle in ACTION_HANDLES" in text:
        return "selector or trace producer enumerates the fixed seven handles"
    if rel.endswith("verify_growth_loop.py") and "ACTION_HANDLES =" in text:
        return "global tuple defines the only selector-visible action handles"
    if "PUBLIC_ACTION_NAMES" in text:
        return "public action names are used after selection for rendering/reporting"
    if rel.endswith("consolidation_000.py"):
        return "consolidated priors and deletion probes are keyed by existing action handles"
    if rel.endswith("lab_console_000.py"):
        return "lab demo rendering and trace output assume existing action handles"
    if rel.endswith("action_space_expansion_004_execute.py"):
        return "004 execution stopped after detecting the frozen static selector"
    return "static action handle reference"


def static_action_handle_dependency_audit() -> dict[str, Any]:
    dependencies: list[dict[str, Any]] = []
    for path in AUDIT_PATHS:
        if not path.exists():
            continue
        for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            if "ACTION_HANDLES" not in line and "PUBLIC_ACTION_NAMES" not in line:
                continue
            symbol = "ACTION_HANDLES" if "ACTION_HANDLES" in line else "PUBLIC_ACTION_NAMES"
            dependencies.append(
                {
                    "path": relative(path),
                    "line": line_no,
                    "symbol": symbol,
                    "source": line.strip(),
                    "classification": classify_dependency(path, line),
                    "reason": dependency_reason(path, line),
                }
            )
    blocking = [
        item
        for item in dependencies
        if item["classification"] == "primary_selector_bottleneck"
    ]
    return {
        "summary": (
            "Static ACTION_HANDLES references are concentrated in the frozen "
            "CMBCGrowthLoopCandidate selector and its trace producer. The 004 "
            "failure is therefore a selector/action-interface bottleneck, not a "
            "semantic-label leak."
        ),
        "dependency_count": len(dependencies),
        "blocking_dependency_count": len(blocking),
        "blocking_dependencies": blocking,
        "dependencies": dependencies,
    }


def selector_parametricity_audit() -> dict[str, Any]:
    choose_signature = inspect.signature(CMBCGrowthLoopCandidate.choose)
    fit_source = inspect.getsource(CMBCGrowthLoopCandidate.fit_effect_model)
    choose_source = inspect.getsource(CMBCGrowthLoopCandidate.choose)
    trace_source = inspect.getsource(make_trace)
    replay_source = inspect.getsource(replay_decisions)
    return {
        "selector_class": "CMBCGrowthLoopCandidate",
        "static_action_handle_count": len(ACTION_HANDLES),
        "static_action_handles": list(ACTION_HANDLES),
        "choose_signature": str(choose_signature),
        "selector_uses_static_action_handles": "ACTION_HANDLES" in choose_source,
        "accepts_candidate_options_parameter": "candidate_options" in str(choose_signature),
        "can_score_arbitrary_options": False,
        "fit_effect_model_static_by_action": "for handle in ACTION_HANDLES" in fit_source,
        "fit_effect_model_extra_history_key_risk": "by_action[item.action_handle]" in fit_source,
        "prediction_before_action_static_handles": "for handle in ACTION_HANDLES" in trace_source,
        "replay_selects_from_distribution_keys": "trace[\"action_distribution\"]" in replay_source,
        "effect_estimates_extra_keys_ignored_by_selector": True,
        "root_cause": (
            "CMBCGrowthLoopCandidate.choose receives effect_estimates but then "
            "builds utilities by iterating ACTION_HANDLES. Extra anonymous "
            "candidate options can exist in the caller, but the frozen selector "
            "will never score them or place them in action_distribution."
        ),
    }


def replay_dependency_audit() -> dict[str, Any]:
    return {
        "replay_contract_blocks_expansion": False,
        "upstream_trace_producer_uses_static_handles": True,
        "behavior_only_replay_can_remain_parametric_if_trace_contains_distribution": True,
        "current_replay_used_fields": [
            "observation",
            "anonymous_candidate_actions",
            "prediction_before_action",
            "action_distribution",
            "selected_action",
            "model_version",
        ],
        "current_static_points": [
            "make_trace writes anonymous_candidate_actions from ACTION_HANDLES",
            "make_trace writes prediction_before_action for ACTION_HANDLES",
            "004 expanded action decisions were not produced, so no expanded replay existed",
        ],
        "interpretation": (
            "Replay itself selects the max action from trace action_distribution keys. "
            "That can work for N options if the trace producer supplies N-option "
            "distributions. The blocking dependency is upstream trace generation."
        ),
    }


def renderer_dependency_audit() -> dict[str, Any]:
    return {
        "renderer_static_dependency_blocks_expansion": False,
        "renderer_runs_after_selection": True,
        "renderer_reads_selected_action": True,
        "renderer_does_not_control_action": True,
        "requires_parametric_post_selection_renderer_adapter": True,
        "static_points": [
            "CompanionRenderer.render indexes PUBLIC_ACTION_NAMES[selected_action]",
            "LabOnlyRenderer.templates are keyed by act_0..act_6",
            "LabOnlyRenderer.renderer_input includes public_action_name after selection",
        ],
        "interpretation": (
            "Renderer dependencies would block a user-visible expanded demo, but "
            "they are post-selection and did not cause the 004 selector-visible "
            "candidate count to remain seven. A future contract needs a renderer "
            "adapter that maps selected anonymous options after selection without "
            "leaking semantic labels back to the selector."
        ),
    }


def baseline_dependency_audit() -> dict[str, Any]:
    return {
        "baseline_contract_blocks_expansion": False,
        "existing_baselines_use_fixed_action_ids": True,
        "expanded_baseline_contract_required_before_execution": True,
        "static_points": [
            "StrongHeuristicBaseline returns act_4/act_6/act_2",
            "RAGMemoryPromptBaseline returns act_4/act_6/act_2/act_0",
            "003 reexecute strong and expanded contextual baselines compare over the small action set",
        ],
        "requirements_for_005_or_later": [
            "baselines must receive the same anonymous CandidateOption list",
            "baselines must not read semantic labels or renderer text",
            "frequency and nearest-neighbor baselines must operate on option features and public outcomes only",
        ],
        "interpretation": (
            "Baseline contracts must be expanded before a valid expanded execution, "
            "but the 004 clean failure happened before baseline scoring. This is not "
            "the primary blocker for the observed small_action_set_only verdict."
        ),
    }


def build_source_failure() -> dict[str, Any]:
    source = read_json(SOURCE_FAILURE_PATH)
    metrics = source["metrics"]
    return {
        "suite_id": "CMBC-COMPANION-ACTION-SPACE-EXPANSION-004-EXECUTE",
        "verdict": source["verdict"],
        "stop_conditions": list(source["stop_conditions"]),
        "requested_candidate_action_count": metrics["requested_candidate_action_count"],
        "selector_visible_candidate_action_count": metrics["selector_visible_candidate_action_count"],
        "semantic_label_leak_scan_passed": metrics["semantic_label_leak_scan_passed"],
        "renderer_action_change_rate": metrics["renderer_action_change_rate"],
        "minimum_gates_satisfied": source["minimum_gates_satisfied"],
    }


def build_result() -> dict[str, Any]:
    static_audit = static_action_handle_dependency_audit()
    selector = selector_parametricity_audit()
    replay = replay_dependency_audit()
    renderer = renderer_dependency_audit()
    baselines = baseline_dependency_audit()
    verdict = "selector_static_action_handle_bottleneck_confirmed"
    return {
        "suite_id": "CMBC-COMPANION-ACTION-SPACE-EXPANSION-004-RCA",
        "task_type": "RCA only / contract-analysis only",
        "verdict": verdict,
        "source_failure": build_source_failure(),
        "claim_after_rca": CLAIM_AFTER_RCA,
        "static_action_handle_dependency_audit": static_audit,
        "selector_parametricity": selector,
        "replay_dependency": replay,
        "renderer_dependency": renderer,
        "baseline_dependency": baselines,
        "can_introduce_parametric_interface_without_invalidating_003_evidence": "contract_only_shadow_adapter_required",
        "next_recommended_task": "CMBC-COMPANION-PARAMETRIC-ACTION-INTERFACE-005-CONTRACT",
        "selector_patched": False,
        "action_handles_added": False,
        "thresholds_changed": False,
        "rag_baseline_weakened": False,
        "baseline_weakened": False,
        "ego_migration": "no_go",
        "real_companion_implementation": "not_authorized",
        "proactive_messages": "not_authorized",
        "llm_action_selection": False,
        "implementation_authorized": False,
        "not_proven": [
            "expanded action-space causal-probe advantage",
            "scalable companion behavior control",
            "open-ended action generation",
            "real companion readiness",
            "EGO readiness",
            "consciousness",
            "subjective experience",
            "real emotion",
            "real love",
        ],
    }


def selector_parametricity_markdown(result: dict[str, Any]) -> str:
    selector = result["selector_parametricity"]
    return (
        "# Selector Parametricity Audit\n\n"
        f"verdict = {result['verdict']}\n\n"
        f"static_action_handle_count = {selector['static_action_handle_count']}\n\n"
        f"choose_signature = `{selector['choose_signature']}`\n\n"
        "Findings:\n\n"
        "- `CMBCGrowthLoopCandidate.choose` has no `candidate_options` parameter.\n"
        "- It constructs utilities by iterating the global `ACTION_HANDLES` tuple.\n"
        "- Extra keys in `effect_estimates` are ignored by selector scoring.\n"
        "- `fit_effect_model` also initializes `by_action` from `ACTION_HANDLES`.\n"
        "- `make_trace` writes predictions and anonymous candidate actions from `ACTION_HANDLES`.\n\n"
        "Conclusion:\n\n"
        "The frozen selector is not parametric over candidate action space. The "
        "004 failure is therefore not evidence against CMBC free-input causal probes; "
        "it is evidence that the current implementation only supports the small "
        "7-action anonymous interface.\n"
    )


def minimal_parametric_interface_proposal() -> str:
    return (
        "# Minimal Parametric Action Interface Proposal\n\n"
        "Status: proposal only. No selector implementation is authorized here.\n\n"
        "A future 005 contract should replace fixed `ACTION_HANDLES` consumption "
        "with an explicit anonymous candidate option interface:\n\n"
        "```text\n"
        "CandidateOption {\n"
        "  option_id: anonymous handle\n"
        "  allowed_observation_features: non-semantic public features\n"
        "  predicted_effect_vector: learned or estimated outcome vector\n"
        "  uncertainty: confidence / evidence quality\n"
        "  prior_support_refs: source prior or episode refs\n"
        "  cost_risk_budget_features: non-semantic control features\n"
        "  forbidden_semantic_fields: semantic labels, rendered text, public names,\n"
        "                             action family names, natural language descriptions\n"
        "}\n"
        "\n"
        "selector_input = observation + list[CandidateOption] + learned causal model state\n"
        "selector_output = prediction_before_action per option + action_distribution over N options\n"
        "N in {7, 20, 50, variable}\n"
        "```\n\n"
        "Compatibility path:\n\n"
        "1. Define the interface contract before implementation.\n"
        "2. Build a 7-action adapter that reproduces 003 evidence in shadow mode.\n"
        "3. Preserve behavior-only replay by recording the full option list and distribution.\n"
        "4. Add expanded baselines that receive the same anonymous option list.\n"
        "5. Keep renderer strictly post-selection.\n\n"
        "Stop conditions:\n\n"
        "- semantic label or renderer text reaches selector\n"
        "- fixed action ids are recreated as `anon_option_00..19` recipes\n"
        "- thresholds are retuned after seeing expanded results\n"
        "- 003 small-action evidence is rewritten instead of preserved as bounded evidence\n"
    )


def risk_register_markdown() -> str:
    return (
        "# Risk Register\n\n"
        "| Risk | Status | Mitigation / stop line |\n"
        "| --- | --- | --- |\n"
        "| 20 fixed handles replace 7 fixed handles | open | 005 must require variable-N CandidateOption input, not a larger tuple. |\n"
        "| Effect representation only works for act ids | open | If confirmed in 005, stop and run ACTION-REPRESENTATION-RCA. |\n"
        "| Renderer leaks public action names | controlled in 004 | Renderer must remain post-selection and adapter-only. |\n"
        "| Replay contract hides fixed ids | partial | Replay can be parametric if traces contain full option distribution. |\n"
        "| Baselines are weaker in expanded space | open | Expanded baselines must consume same anonymous options. |\n"
        "| 003 evidence invalidated by interface rewrite | open | Use shadow adapter and preserve 003 as small-action-set evidence. |\n"
        "| Threshold retune or selector patch to win | forbidden | Any occurrence invalidates the run. |\n"
        "| EGO/product leap from RCA | forbidden | RCA supports only a 005 contract review, not implementation. |\n"
    )


def write_artifacts(out_path: Path, result: dict[str, Any]) -> None:
    write_json(out_path / "static_action_handle_dependency_audit.json", result["static_action_handle_dependency_audit"])
    write_json(out_path / "replay_dependency_audit.json", result["replay_dependency"])
    write_json(out_path / "RCA_RESULT.json", result)
    (out_path / "selector_parametricity_audit.md").write_text(
        selector_parametricity_markdown(result),
        encoding="utf-8",
    )
    (out_path / "renderer_dependency_audit.md").write_text(
        "# Renderer Dependency Audit\n\n"
        + json.dumps(result["renderer_dependency"], indent=2, sort_keys=True)
        + "\n",
        encoding="utf-8",
    )
    (out_path / "baseline_dependency_audit.md").write_text(
        "# Baseline Dependency Audit\n\n"
        + json.dumps(result["baseline_dependency"], indent=2, sort_keys=True)
        + "\n",
        encoding="utf-8",
    )
    (out_path / "minimal_parametric_interface_proposal.md").write_text(
        minimal_parametric_interface_proposal(),
        encoding="utf-8",
    )
    (out_path / "risk_register.md").write_text(risk_register_markdown(), encoding="utf-8")
    (out_path / "ACTION_SPACE_EXPANSION_004_RCA_STATUS.md").write_text(
        "# CMBC Companion Action-Space Expansion 004 RCA\n\n"
        f"verdict = {result['verdict']}\n\n"
        f"source_failure = {result['source_failure']['verdict']}\n\n"
        f"claim_after_rca = {result['claim_after_rca']}\n\n"
        "root_cause = frozen selector iterates static ACTION_HANDLES and ignores arbitrary candidate options\n\n"
        f"next_recommended_task = {result['next_recommended_task']}\n\n"
        "selector_patched = false\n\n"
        "action_handles_added = false\n\n"
        "thresholds_changed = false\n\n"
        "rag_baseline_weakened = false\n\n"
        "EGO migration = no_go\n\n"
        "real companion implementation = not_authorized\n\n"
        "proactive messages = not_authorized\n\n"
        "LLM action selection = false\n",
        encoding="utf-8",
    )


def run_action_space_expansion_004_rca(out: str | Path) -> dict[str, Any]:
    out_path = Path(out)
    out_path.mkdir(parents=True, exist_ok=True)
    result = build_result()
    write_artifacts(out_path, result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    result = run_action_space_expansion_004_rca(args.out)
    print(
        json.dumps(
            {
                "verdict": result["verdict"],
                "source_failure": result["source_failure"]["verdict"],
                "next_recommended_task": result["next_recommended_task"],
                "selector_patched": result["selector_patched"],
                "action_handles_added": result["action_handles_added"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
