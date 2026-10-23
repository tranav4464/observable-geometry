"""Observable Geometry's numerical tools.

The active Track B API is a nominal forward-signature comparison. The older
conditional linear inverse functions remain available as a historical
prototype and are not the active GBFs diagnostic.
"""

from .core import average_reference, fit_linear_geometry, robust_sensor_scores
from .track_b.distinguishability import compute_distinguishability, summarize

__all__ = [
    "average_reference",
    "compute_distinguishability",
    "fit_linear_geometry",
    "robust_sensor_scores",
    "summarize",
]
