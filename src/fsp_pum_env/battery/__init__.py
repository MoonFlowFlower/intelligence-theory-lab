"""S3a prefix-only fair-battery members."""

from .base import PrefixEvent, PrefixOnlyPredictor, load_design, validate_prediction
from .degenerates import (
    GlobalPriorPredictor,
    MajorityPredictor,
    PredictAllPredictor,
    PredictNonePredictor,
    degenerate_conventions,
    write_battery_manifest,
)
from .ls_regressors import DiscountedLeastSquaresPredictor, RunningAveragePreferenceRegressor

__all__ = [
    "DiscountedLeastSquaresPredictor",
    "GlobalPriorPredictor",
    "MajorityPredictor",
    "PredictAllPredictor",
    "PredictNonePredictor",
    "PrefixEvent",
    "PrefixOnlyPredictor",
    "RunningAveragePreferenceRegressor",
    "degenerate_conventions",
    "load_design",
    "validate_prediction",
    "write_battery_manifest",
]
