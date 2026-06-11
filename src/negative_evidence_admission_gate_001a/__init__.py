"""Admission guard for known negative-evidence citation failures."""

from .core import CLAIM_CEILING, TASK_ID, evaluate_successor_task

__all__ = ["CLAIM_CEILING", "TASK_ID", "evaluate_successor_task"]
