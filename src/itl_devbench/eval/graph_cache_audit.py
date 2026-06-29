from __future__ import annotations

import inspect
import json
from pathlib import Path
from typing import Any, Dict

from itl_devbench.agents.graph_cache import GraphCacheAgent
from itl_devbench.core.hashing import sha256_file, sha256_json
from itl_devbench.core.trace import read_jsonl


def audit_graph_cache_access(trace_path: str | Path) -> Dict[str, Any]:
    trace_path = Path(trace_path)
    events = read_jsonl(trace_path)
    graph_events = [event for event in events if event["agent_id"] == "graph_cache"]
    source = inspect.getsource(GraphCacheAgent)
    predict_source = inspect.getsource(GraphCacheAgent.predict)
    act_source = inspect.getsource(GraphCacheAgent.act)
    reset_source = inspect.getsource(GraphCacheAgent.reset)

    checks = {
        "hidden_state_access": {
            "ok": "debug_hidden_state" not in source and "hidden_state" not in source and "hidden" not in source,
            "detail": "source_scan_for_hidden_state_terms",
        },
        "future_outcome_access": {
            "ok": not any(term in f"{predict_source}\n{act_source}" for term in ["obs_after", "reward", "done", "info", "env_result"]),
            "detail": "predict_act_source_scan_for_future_outcome_terms",
        },
        "cache_reset_scope": {
            "ok": "self.cache = {}" in reset_source,
            "detail": "reset_clears_cache_per_seed_stage_episode",
        },
        "cross_seed_rule_seed_contamination": {
            "ok": _graph_cache_starts_empty_each_episode(graph_events),
            "detail": "first_graph_cache_event_per_episode_has_empty_state",
        },
        "unfair_cache_scope": {
            "ok": "self.cache = {}" in reset_source and "GraphCacheAgent.cache" not in source,
            "detail": "cache_is_instance_local_and_reset_per_episode",
        },
    }
    failed = [name for name, check in checks.items() if not check["ok"]]
    result = {
        "producer_function": "itl_devbench.eval.graph_cache_audit.audit_graph_cache_access",
        "trace_path": trace_path.name,
        "source_path": "src/itl_devbench/agents/graph_cache.py",
        "access_contract": {
            "allowed_inputs": ["current Observation in predict/act", "post-step obs_after/reward/done/info only inside update"],
            "forbidden_inputs": ["debug_hidden_state", "hidden_state", "future env_result before action", "cross-episode cache carryover"],
            "cache_scope": "per_episode",
            "cache_scope_detail": "instance-local cache reset for every seed/stage/family/episode run",
            "cross_split_cache_sharing": "forbidden",
        },
        "checks": checks,
        "failed_checks": failed,
        "verdict": "graph_cache_access_contract_ok" if not failed else "invalid_due_graph_cache_leakage",
    }
    result["audit_hash"] = sha256_json(result)
    result["code_path_hash"] = sha256_file(Path(__file__))
    return result


def write_graph_cache_audit(path: str | Path, audit: Dict[str, Any]) -> None:
    Path(path).write_text(json.dumps(audit, indent=2, sort_keys=True), encoding="utf-8")


def _graph_cache_starts_empty_each_episode(graph_events: list[Dict[str, Any]]) -> bool:
    seen: set[tuple[int, int, int]] = set()
    for event in graph_events:
        key = (int(event["seed"]), int(event["stage"]), int(event["episode"]))
        if key in seen:
            continue
        seen.add(key)
        if event["S_before"].get("memory_size", 0) != 0:
            return False
        if event["S_before"].get("transition_model", {}) not in ({}, None):
            return False
    return bool(graph_events)
