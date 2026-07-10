"""Code-first H0 prebank package; no formal H0 execution is authorized here."""

from .h0_registry import build_registry
from .h0_resolver import resolve_comparator_panel, resolve_component_evidence

__all__ = ["build_registry", "resolve_comparator_panel", "resolve_component_evidence"]
