"""Geometry-derived scalp mixing operators for synthetic WBEN challenges.

No EEG measurements are loaded here. A subject-specific MNE forward matrix is
reduced to deterministic geometric cortical parcels; these are simulation
nodes, not atlas labels or biological regions.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class RegionalLeadfield:
    operator: np.ndarray  # average-referenced volts per ampere-metre
    node_positions_m: np.ndarray
    hemisphere: np.ndarray
    parcel_sizes: np.ndarray
    source_to_node: np.ndarray
    reference_operator: np.ndarray


def _kmeans(points: np.ndarray, n_clusters: int, seed: int,
            max_iter: int, tolerance_m: float) -> tuple[np.ndarray, np.ndarray]:
    rng = np.random.default_rng(seed)
    n_points = points.shape[0]
    if n_clusters < 1 or n_clusters > n_points:
        raise ValueError("n_clusters must be between 1 and the number of points")
    centers = np.empty((n_clusters, 3), dtype=np.float64)
    first = int(rng.integers(n_points))
    centers[0] = points[first]
    nearest_sq = np.sum((points - centers[0]) ** 2, axis=1)
    for k in range(1, n_clusters):
        total = float(nearest_sq.sum())
        if total <= 0:
            raise ValueError("source coordinates do not support the requested distinct parcels")
        else:
            pick = int(rng.choice(n_points, p=nearest_sq / total))
            if np.min(np.sum((points - points[pick]) ** 2, axis=1)) <= 0:
                candidates = np.argsort(nearest_sq)[::-1]
                pick = next((int(i) for i in candidates
                             if not np.any(np.all(centers[:k] == points[i], axis=1))), int(candidates[0]))
        centers[k] = points[pick]
        nearest_sq = np.minimum(nearest_sq, np.sum((points - centers[k]) ** 2, axis=1))

    labels = np.zeros(n_points, dtype=np.int32)
    for _ in range(max_iter):
        distances = np.sum((points[:, None, :] - centers[None, :, :]) ** 2, axis=2)
        labels = np.argmin(distances, axis=1)
        nearest = np.min(distances, axis=1)
        updated = centers.copy()
        counts = np.bincount(labels, minlength=n_clusters)
        for k in range(n_clusters):
            members = points[labels == k]
            if len(members):
                updated[k] = members.mean(axis=0)
            else:
                # Re-seed empty clusters at the currently least represented point.
                farthest = int(np.argmax(nearest))
                updated[k] = points[farthest]
                nearest[farthest] = -1.0
        shift = float(np.max(np.linalg.norm(updated - centers, axis=1)))
        centers = updated
        if shift <= tolerance_m:
            break
    distances = np.sum((points[:, None, :] - centers[None, :, :]) ** 2, axis=2)
    labels = np.argmin(distances, axis=1).astype(np.int32)
    counts = np.bincount(labels, minlength=n_clusters)
    if np.any(counts == 0):
        raise RuntimeError("geometric clustering produced an empty parcel")
    centers = np.stack([points[labels == k].mean(axis=0) for k in range(n_clusters)])
    return labels, centers


def geometric_regional_leadfield(
    fixed_leadfield: np.ndarray,
    source_positions_m: np.ndarray,
    hemisphere: np.ndarray,
    *,
    regions_per_hemisphere: tuple[int, int] = (35, 34),
    seed: int = 20261022,
    max_iter: int = 100,
    tolerance_m: float = 1e-7,
    average_reference: bool = True,
) -> RegionalLeadfield:
    """Aggregate a fixed-orientation lead field into geometric cortical nodes.

    Each node's column is the equal-weight average of fixed-normal dipole
    fields in a Euclidean k-means cortical patch. This defines a reproducible
    *simulation basis* only. It is not a named cortical atlas, and its equal
    weights do not model parcel area or within-parcel phase variation.
    """
    lead = np.asarray(fixed_leadfield, dtype=np.float64)
    pos = np.asarray(source_positions_m, dtype=np.float64)
    hemi = np.asarray(hemisphere)
    if lead.ndim != 2 or lead.shape[0] < 2 or pos.shape != (lead.shape[1], 3):
        raise ValueError("leadfield must be sensors x sources and positions sources x 3")
    if hemi.shape != (lead.shape[1],) or set(np.unique(hemi).tolist()) != {0, 1}:
        raise ValueError("hemisphere must contain exactly source-wise labels 0 and 1")
    if not np.all(np.isfinite(lead)) or not np.all(np.isfinite(pos)):
        raise ValueError("leadfield and positions must be finite")
    if (len(regions_per_hemisphere) != 2
            or any(not isinstance(k, int) or k < 1 for k in regions_per_hemisphere)):
        raise ValueError("regions_per_hemisphere must contain two positive integers")
    if not isinstance(max_iter, int) or max_iter < 1:
        raise ValueError("max_iter must be a positive integer")
    if not np.isfinite(tolerance_m) or tolerance_m <= 0:
        raise ValueError("tolerance_m must be positive and finite")

    n_sources = lead.shape[1]
    mapping = np.full(n_sources, -1, dtype=np.int32)
    positions_by_node: list[np.ndarray] = []
    hemis_by_node: list[int] = []
    sizes: list[int] = []
    node_columns: list[np.ndarray] = []
    node_index = 0
    for hemi_label, cluster_count in enumerate(regions_per_hemisphere):
        source_ids = np.flatnonzero(hemi == hemi_label)
        labels, centers = _kmeans(pos[source_ids], cluster_count,
                                  seed + hemi_label, max_iter, tolerance_m)
        for cluster in range(cluster_count):
            local = np.flatnonzero(labels == cluster)
            global_ids = source_ids[local]
            mapping[global_ids] = node_index
            node_columns.append(lead[:, global_ids].mean(axis=1))
            positions_by_node.append(centers[cluster])
            hemis_by_node.append(hemi_label)
            sizes.append(len(global_ids))
            node_index += 1
    if np.any(mapping < 0):
        raise RuntimeError("some source vertices were not assigned to a simulation node")
    operator = np.column_stack(node_columns)
    if average_reference:
        n_sensors = operator.shape[0]
        reference = np.eye(n_sensors) - np.ones((n_sensors, n_sensors)) / n_sensors
        operator = reference @ operator
    else:
        reference = np.eye(operator.shape[0])
    if not np.all(np.isfinite(operator)) or np.any(np.linalg.norm(operator, axis=0) <= 0):
        raise FloatingPointError("aggregated lead field contains an invalid or zero node")
    return RegionalLeadfield(
        operator=operator,
        node_positions_m=np.asarray(positions_by_node),
        hemisphere=np.asarray(hemis_by_node, dtype=np.int8),
        parcel_sizes=np.asarray(sizes, dtype=np.int32),
        source_to_node=mapping,
        reference_operator=reference,
    )
