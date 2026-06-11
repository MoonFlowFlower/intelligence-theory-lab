from __future__ import annotations

from dataclasses import dataclass
from typing import Callable


TASK_ID = "NEGATIVE-EVIDENCE-ADMISSION-GATE-001A"
CLAIM_CEILING = "bounded successor-task admission guard against known false-confidence risks"


@dataclass(frozen=True)
class Rule:
    rule_id: str
    fails: Callable[[str], bool]


def _has_any(text: str, needles: tuple[str, ...]) -> bool:
    return any(needle in text for needle in needles)


def _has_all(text: str, needles: tuple[str, ...]) -> bool:
    return all(needle in text for needle in needles)


def _missing_001a_supersession(text: str) -> bool:
    cites_001a_pass = _has_any(
        text,
        (
            "representational_gap_preflight_bounded_pass",
            "001a pass",
            "001a bounded pass",
            "representational-gap-preflight-001a pass",
        ),
    )
    cites_supersession = _has_any(
        text,
        (
            "representational-gap-preflight-001a-audit-closeout",
            "001a supersession",
            "001a superseded",
            "superseded_by_independent_audit",
        ),
    )
    return cites_001a_pass and not cites_supersession


def _missing_001b_fair_control_failure(text: str) -> bool:
    cites_successor = _has_any(
        text,
        (
            "representational-gap successor",
            "representational gap successor",
            "model-class-reset",
            "model_class_reset",
        ),
    )
    cites_001b_failure = "representational_gap_001b_failed_count_or_statistic_control_solved" in text
    return cites_successor and not cites_001b_failure


def _missing_001c_canonical_errata(text: str) -> bool:
    cites_current_closeout = "predictive-action-learning-contract-001c-closeout.md" in text
    cites_errata = "predictive-action-learning-contract-001c-canonical-errata-001a" in text
    return cites_current_closeout and not cites_errata


def _process_intervention_draft_pass_treated_as_executable(text: str) -> bool:
    cites_draft_pass = "process_intervention_001a_independent_audit_pass_with_caveats" in text
    treats_as_executable = _has_any(
        text,
        (
            "is executable authorization",
            "as executable authorization",
            "authorizes executable",
            "authorizes mechanism implementation",
            "mechanism implementation authorized = true",
            "mechanism_implementation_authorized = true",
            "execution_authorized = true",
        ),
    )
    return cites_draft_pass and treats_as_executable


def _verdict_string_tests_treated_as_acceptance(text: str) -> bool:
    cites_verdict_tests = _has_any(text, ("verdict-string", "verdict string"))
    treats_as_acceptance = _has_any(
        text,
        (
            "acceptance evidence",
            "sufficient acceptance",
            "acceptance gate evidence",
            "prove acceptance",
        ),
    )
    rejects_pattern = _has_any(
        text,
        (
            "reject verdict-string tests",
            "reject verdict string tests",
            "verdict-string tests are not acceptance evidence",
            "verdict string tests are not acceptance evidence",
        ),
    )
    return cites_verdict_tests and treats_as_acceptance and not rejects_pattern


def _gate1_replay_pass_ignores_graph_cache_collapse(text: str) -> bool:
    cites_replay_pass = "replay_verification_pass" in text
    cites_graph_cache_collapse = "gate1_preflight_failed_graph_cache_collapse" in text
    return cites_replay_pass and not cites_graph_cache_collapse


def _fable_causality_without_provenance_diff_mechanism(text: str) -> bool:
    attributes_fable_causality = _has_any(
        text,
        (
            "fable caused",
            "fable-caused",
            "caused by fable",
            "fable data poisoning",
            "fable poisoning",
        ),
    )
    has_required_evidence_terms = _has_all(text, ("provenance", "diff", "mechanism evidence"))
    return attributes_fable_causality and not has_required_evidence_terms


RULES = (
    Rule("missing_001a_supersession", _missing_001a_supersession),
    Rule("missing_001b_fair_control_failure", _missing_001b_fair_control_failure),
    Rule("missing_001c_canonical_errata", _missing_001c_canonical_errata),
    Rule(
        "process_intervention_draft_pass_treated_as_executable",
        _process_intervention_draft_pass_treated_as_executable,
    ),
    Rule("verdict_string_tests_treated_as_acceptance", _verdict_string_tests_treated_as_acceptance),
    Rule("gate1_replay_pass_ignores_graph_cache_collapse", _gate1_replay_pass_ignores_graph_cache_collapse),
    Rule("fable_causality_without_provenance_diff_mechanism", _fable_causality_without_provenance_diff_mechanism),
)


def evaluate_successor_task(text: str) -> dict:
    """Evaluate a successor task card against known false-confidence risks."""
    normalized = text.casefold()
    failure_ids = [rule.rule_id for rule in RULES if rule.fails(normalized)]
    return {
        "task_id": TASK_ID,
        "passed": not failure_ids,
        "failure_ids": failure_ids,
        "claim_ceiling": CLAIM_CEILING,
        "checked_rules": [rule.rule_id for rule in RULES],
    }
