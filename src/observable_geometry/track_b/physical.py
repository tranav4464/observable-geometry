"""Simple current-source comparator, not a layered-head forward solution."""
from __future__ import annotations

import numpy as np


def homogeneous_bipolar_signature(sensor_head_m: np.ndarray,
                                  contacts_head_m: np.ndarray,
                                  min_distance_m: float = .002) -> np.ndarray:
    """Return the unscaled potential difference for +I at contact 0, -I at 1.

    The infinite homogeneous conductor solution is proportional to
    ``1/|r-r0| - 1/|r-r1|``. Current and conductivity multiply the entire
    signature and can be fitted separately. Every coordinate is in metres.
    """
    sensors = np.asarray(sensor_head_m, dtype=float)
    contacts = np.asarray(contacts_head_m, dtype=float)
    if (sensors.ndim != 2 or sensors.shape[1] != 3 or contacts.shape != (2, 3)
            or not np.isfinite(sensors).all() or not np.isfinite(contacts).all()
            or not np.isfinite(min_distance_m) or min_distance_m <= 0):
        raise ValueError("Invalid sensor/contact coordinates or distance bound")
    distances = np.linalg.norm(sensors[:, None, :] - contacts[None, :, :], axis=2)
    if np.any(distances < min_distance_m):
        raise ValueError("Sensor too close to injection contact")
    return 1 / distances[:, 0] - 1 / distances[:, 1]


def bipolar_line_quadrature(contacts_m: np.ndarray, nodes: int) -> tuple[np.ndarray, np.ndarray]:
    """Gauss-Legendre points and dipole moments for a source-sink line.

    For a linear conductor, integrating infinitesimal current dipole fields
    along the path between two contacts gives the potential of an ideal
    monopolar current source/sink pair. The returned moments include path
    displacement and quadrature weights; overall current scale is separate.
    """
    contacts = np.asarray(contacts_m, dtype=float)
    if (contacts.shape != (2, 3) or not np.isfinite(contacts).all()
            or np.linalg.norm(contacts[1] - contacts[0]) <= 0
            or not isinstance(nodes, int) or nodes < 1):
        raise ValueError("Invalid contacts or quadrature node count")
    roots, weights = np.polynomial.legendre.leggauss(nodes)
    positions = contacts[0] + ((roots + 1) / 2)[:, None] * (contacts[1] - contacts[0])
    moments = (weights / 2)[:, None] * (contacts[1] - contacts[0])
    return positions, moments
