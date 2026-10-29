"""Experimental tail-closed observable-subspace frontier.

This module is deliberately separate from the sealed Track A calculator.  It
computes a conservative, finite-mesh model certificate from a retained sensor
operator and a sensor-space Gram matrix for the omitted source family.  It does
not use recordings and it does not claim physiological localization.
"""
from __future__ import annotations

from dataclasses import dataclass
import numpy as np


@dataclass(frozen=True)
class TailClosedFrontier:
    """Grid-evaluated lower margins for retained dimensions."""

    normalized_lower_margin: np.ndarray
    selected_multiplier: np.ndarray
    selected_basis_by_rank: tuple[np.ndarray | None, ...]
    scale: float
    gram_error_bound: float
    claim_boundary: str


@dataclass(frozen=True)
class TailClosedRelativeFrontier:
    """Grid-based lower margins normalized by each retained field's gain.

    Unlike :class:`TailClosedFrontier`, this uses the generalized eigenproblem
    relative to ``B.T @ B``. It therefore avoids the additional global
    ``||B||_2**2`` denominator bound. The multiplier search is still finite
    grid search, so these are attainable lower bounds, not continuous-search
    optima or formal interval-arithmetic certificates.
    """

    normalized_lower_margin: np.ndarray
    selected_multiplier_scaled: np.ndarray
    selected_basis_by_rank: tuple[np.ndarray | None, ...]
    effective_rank: int
    operator_scale: float
    multiplier_grid_size: int
    claim_boundary: str


@dataclass(frozen=True)
class FinitePriorEnvelope:
    """One conservative sensor Gram dominating a declared finite prior family."""

    gram: np.ndarray
    anchor_index: int
    isotropic_inflation: float
    minimum_dominance_eigenvalue: tuple[float, ...]
    claim_boundary: str


@dataclass(frozen=True)
class ExactMimicryAudit:
    """Least competing-source cost to reproduce every retained direction."""

    cost_eigenvalues: np.ndarray
    maximum_required_alternative_norm: float
    all_exactly_mimickable: bool
    count_directions_above_budget: int
    gram_condition_number: float
    squared_budget_gap: float
    claim_boundary: str


@dataclass(frozen=True)
class ModelMimicrySubspace:
    """Retained coefficients whose fields all admit exact modeled alternatives."""

    coefficient_basis: np.ndarray
    eligible_cost_eigenvalues: np.ndarray
    dimension: int
    maximum_cost_on_subspace: float | None
    alternative_budget: float
    relative_squared_budget_buffer: float
    claim_boundary: str


@dataclass(frozen=True)
class FinitePriorSensorWitness:
    """A fixed sensor functional separating one source from finite alternatives."""

    projected_retained_amplitude: float
    maximum_competing_amplitude: float
    competing_amplitude_by_prior: tuple[float, ...]
    sensor_norm_separation_lower: float
    normalized_margin_over_retained_gain: float
    strict_exact_mimicry_exclusion: bool
    claim_boundary: str


@dataclass(frozen=True)
class ConstructedPriorWitness:
    """An anchor-ellipsoid projection with a replayable common sensor test."""

    retained_direction: np.ndarray
    sensor_witness: np.ndarray
    anchor_index: int
    normalized_common_margin_lower: float
    normalized_anchor_distance: float
    tight_for_convex_prior_hull: bool
    claim_boundary: str


def _finite_matrix(value: np.ndarray, name: str) -> np.ndarray:
    array = np.asarray(value, dtype=np.float64)
    if array.ndim != 2 or not np.isfinite(array).all():
        raise ValueError(f"{name} must be a finite 2D array")
    return array


def _gram_eigendecomposition(gram: np.ndarray, name: str) -> tuple[np.ndarray, np.ndarray]:
    matrix = _finite_matrix(gram, name)
    if matrix.shape[0] != matrix.shape[1]:
        raise ValueError(f"{name} must be square")
    if not np.allclose(matrix, matrix.T, rtol=1e-10, atol=1e-12):
        raise ValueError(f"{name} must be symmetric")
    values, vectors = np.linalg.eigh((matrix + matrix.T) / 2)
    scale = max(float(np.max(np.abs(values))), np.finfo(float).tiny)
    if float(values.min()) < -1e-10 * scale:
        raise ValueError(f"{name} must be positive semidefinite")
    return np.maximum(values, 0.0), vectors


def finite_prior_gram_envelope(grams: list[np.ndarray] | tuple[np.ndarray, ...]) -> FinitePriorEnvelope:
    """Build a conservative common competitor for a finite family of priors.

    For each candidate Gram C_i, find the smallest isotropic inflation required
    by computed eigenvalues to dominate all C_j. Choose the candidate with the
    smallest trace after inflation. The result is a feasible envelope, not the
    globally least upper bound in Loewner order. A float64 roundoff cushion is
    included; the result is not a formal interval-arithmetic certificate.
    """
    if not isinstance(grams, (list, tuple)) or not grams:
        raise ValueError("grams must be a nonempty list or tuple")
    matrices = []
    size = None
    for index, item in enumerate(grams):
        matrix = _finite_matrix(item, f"grams[{index}]")
        if matrix.shape[0] != matrix.shape[1] or (size is not None and matrix.shape != (size, size)):
            raise ValueError("all prior Grams must have one common square shape")
        _gram_eigendecomposition(matrix, f"grams[{index}]")
        size = matrix.shape[0]
        matrices.append((matrix + matrix.T) / 2)
    assert size is not None
    spectral_scale = max(float(np.linalg.norm(matrix, ord=2)) for matrix in matrices)
    if spectral_scale <= np.finfo(float).tiny:
        raise ValueError("prior Grams must have nonzero scale")
    cushion = 16.0 * size * np.finfo(float).eps * spectral_scale
    options = []
    for index, candidate in enumerate(matrices):
        deficit = max(0.0, *(float(-np.linalg.eigvalsh(candidate-other)[0]) for other in matrices))
        inflation = deficit + cushion
        options.append((float(np.trace(candidate) + size*inflation), index, inflation))
    _, anchor_index, inflation = min(options)
    envelope = matrices[anchor_index] + inflation*np.eye(size)
    gaps = tuple(float(np.linalg.eigvalsh(envelope-other)[0]) for other in matrices)
    if min(gaps) < -cushion:
        raise AssertionError("computed envelope does not dominate all prior Grams")
    return FinitePriorEnvelope(
        gram=envelope,
        anchor_index=anchor_index,
        isotropic_inflation=float(inflation),
        minimum_dominance_eigenvalue=gaps,
        claim_boundary="conditional finite-prior model envelope; not all priors, participant variability, or physiological source identification",
    )


def exact_mimicry_audit(retained_operator: np.ndarray, tail_gram: np.ndarray,
                       *, eta: float = 1.0) -> ExactMimicryAudit:
    """Audit whether a full-row-rank competitor can exactly imitate Bc.

    For C = D D.T > 0, the least squared alternative coefficient cost for
    Bc is c.T B.T C^-1 B c. Its maximum over ||c||=1 is the largest
    eigenvalue of that matrix. This is classical least-norm linear algebra,
    applied here only under the declared source metric and forward model.
    """
    b = _finite_matrix(retained_operator, "retained_operator")
    c = _finite_matrix(tail_gram, "tail_gram")
    if c.shape != (b.shape[0], b.shape[0]):
        raise ValueError("sensor dimensions disagree")
    if not np.isfinite(eta) or eta <= 0:
        raise ValueError("eta must be finite and positive")
    eig, _ = _gram_eigendecomposition(c, "tail_gram")
    if eig[0] <= 0:
        raise ValueError("exact mimicry audit requires a positive-definite tail Gram")
    lower = np.linalg.cholesky((c+c.T)/2)
    whitened = np.linalg.solve(lower, b)
    cost = whitened.T@whitened
    values = np.linalg.eigvalsh((cost+cost.T)/2)
    values = np.maximum(values, 0.0)
    gap = float(eta*eta-values[-1])
    if abs(gap) <= 1e-10*max(eta*eta, float(values[-1])):
        raise ValueError("exact mimicry budget boundary is numerically unresolved")
    return ExactMimicryAudit(
        cost_eigenvalues=values,
        maximum_required_alternative_norm=float(np.sqrt(values[-1])),
        all_exactly_mimickable=bool(values[-1] < eta*eta),
        count_directions_above_budget=int(np.sum(values > eta*eta)),
        gram_condition_number=float(eig[-1]/eig[0]),
        squared_budget_gap=gap,
        claim_boundary="exact mimicry only within the declared finite-mesh source family, coefficient budget, and fixed forward model",
    )


def model_mimicry_subspace(
    retained_operator: np.ndarray,
    tail_gram: np.ndarray,
    *,
    eta: float = 1.0,
    relative_squared_budget_buffer: float = 0.1,
) -> ModelMimicrySubspace:
    """Find a conservative coefficient subspace with exact tail alternatives.

    All unit coefficient combinations in the returned basis have least
    alternative norm squared below ``eta**2*(1-buffer)``. This is a
    finite-model eigenspace diagnostic, not a formal interval certificate or
    evidence that the source patterns occur physiologically.
    """
    b = _finite_matrix(retained_operator, "retained_operator")
    gram = _finite_matrix(tail_gram, "tail_gram")
    if gram.shape != (b.shape[0], b.shape[0]):
        raise ValueError("sensor dimensions disagree")
    if not np.isfinite(eta) or eta <= 0:
        raise ValueError("eta must be finite and positive")
    if (not np.isfinite(relative_squared_budget_buffer)
            or not 0 < relative_squared_budget_buffer < 1):
        raise ValueError("relative_squared_budget_buffer must lie strictly between zero and one")
    values, _ = _gram_eigendecomposition(gram, "tail_gram")
    if values[0] <= 0:
        raise ValueError("model mimicry requires a positive-definite tail Gram")
    lower = np.linalg.cholesky((gram+gram.T)/2)
    z = np.linalg.solve(lower, b)
    cost = z.T @ z
    spectrum, vectors = np.linalg.eigh((cost+cost.T)/2)
    cutoff = eta*eta*(1-relative_squared_budget_buffer)
    tolerance = 1e-10*max(cutoff, float(spectrum[-1]))
    if np.min(abs(spectrum-cutoff)) <= tolerance:
        raise ValueError("mimicry subspace budget boundary is numerically unresolved")
    selected = spectrum < cutoff
    eig = spectrum[selected]
    basis = vectors[:, selected]
    return ModelMimicrySubspace(
        coefficient_basis=basis,
        eligible_cost_eigenvalues=eig,
        dimension=int(basis.shape[1]),
        maximum_cost_on_subspace=float(eig[-1]) if len(eig) else None,
        alternative_budget=float(eta),
        relative_squared_budget_buffer=float(relative_squared_budget_buffer),
        claim_boundary="exact alternatives for every unit coefficient combination only under the fixed forward model, positive-definite competitor Gram and declared source budget",
    )


def finite_prior_sensor_witness(
    retained_operator: np.ndarray,
    prior_grams: list[np.ndarray] | tuple[np.ndarray, ...],
    retained_direction: np.ndarray,
    sensor_witness: np.ndarray,
    *,
    eta: float = 1.0,
) -> FinitePriorSensorWitness:
    """Replay one dual witness against all declared competing-source Grams.

    For each C_j=D_j D_j.T and ||z||<=eta, |u.T D_j z| is no greater than
    eta*sqrt(u.T C_j u). A strict inequality versus |u.T Bc| therefore
    rules out an exact competing field for normalized c in every prior.
    A nonpositive result says only that this particular witness failed.
    """
    b = _finite_matrix(retained_operator, "retained_operator")
    if not isinstance(prior_grams, (list, tuple)) or not prior_grams:
        raise ValueError("prior_grams must be a nonempty list or tuple")
    direction = np.asarray(retained_direction, dtype=np.float64)
    witness = np.asarray(sensor_witness, dtype=np.float64)
    if (direction.shape != (b.shape[1],) or witness.shape != (b.shape[0],)
            or not np.isfinite(direction).all() or not np.isfinite(witness).all()):
        raise ValueError("direction and witness must be finite vectors of matching size")
    direction_norm = float(np.linalg.norm(direction))
    witness_norm = float(np.linalg.norm(witness))
    if direction_norm <= 0 or witness_norm <= 0:
        raise ValueError("direction and witness must be nonzero")
    if not np.isfinite(eta) or eta <= 0:
        raise ValueError("eta must be finite and positive")
    c = direction / direction_norm
    signal = float(abs(witness @ b @ c))
    amplitudes = []
    for index, item in enumerate(prior_grams):
        gram = _finite_matrix(item, f"prior_grams[{index}]")
        if gram.shape != (b.shape[0], b.shape[0]):
            raise ValueError("prior Gram sensor dimensions disagree")
        _gram_eigendecomposition(gram, f"prior_grams[{index}]")
        variance = float(witness @ ((gram + gram.T) / 2) @ witness)
        if variance < 0:
            raise ValueError("negative projected competitor variance")
        amplitudes.append(float(np.sqrt(variance)))
    competitor = float(eta * max(amplitudes))
    if abs(signal - competitor) <= 1e-10 * max(signal, competitor, 1.0):
        raise ValueError("sensor witness separation boundary is numerically unresolved")
    margin = float((signal - competitor) / witness_norm)
    gain = float(np.linalg.norm(b, ord=2))
    if gain <= 0:
        raise ValueError("retained_operator must have nonzero norm")
    return FinitePriorSensorWitness(
        projected_retained_amplitude=signal,
        maximum_competing_amplitude=competitor,
        competing_amplitude_by_prior=tuple(amplitudes),
        sensor_norm_separation_lower=margin,
        normalized_margin_over_retained_gain=float(margin/gain),
        strict_exact_mimicry_exclusion=bool(margin > 0),
        claim_boundary="one retained direction, finite declared priors and coefficient budget; not physiological localization or measured-noise resolvability",
    )


def construct_finite_prior_sensor_witness(
    retained_operator: np.ndarray,
    prior_grams: list[np.ndarray] | tuple[np.ndarray, ...],
    retained_direction: np.ndarray,
    *,
    eta: float = 1.0,
) -> ConstructedPriorWitness | None:
    """Try each prior's nearest-point residual as a common sensor witness.

    This anchor-projection search yields a valid lower separation bound for
    the convex hull of the declared alternative ellipsoids. If its common
    bound equals the anchor's primal distance, that fixed direction's robust
    convex-hull distance is attained. Failure to find a positive witness is
    not proof that none exists.
    """
    b = _finite_matrix(retained_operator, "retained_operator")
    if not isinstance(prior_grams, (list, tuple)) or not prior_grams:
        raise ValueError("prior_grams must be a nonempty list or tuple")
    direction = np.asarray(retained_direction, dtype=np.float64)
    if direction.shape != (b.shape[1],) or not np.isfinite(direction).all():
        raise ValueError("retained_direction must be a finite vector of matching size")
    direction_norm = float(np.linalg.norm(direction))
    if direction_norm <= 0:
        raise ValueError("retained_direction must be nonzero")
    if not np.isfinite(eta) or eta <= 0:
        raise ValueError("eta must be finite and positive")
    c = direction / direction_norm
    y = b @ c
    gain = float(np.linalg.norm(b, ord=2))
    if gain <= 0:
        raise ValueError("retained_operator must have nonzero norm")
    matrices = []
    spectra = []
    for index, item in enumerate(prior_grams):
        gram = _finite_matrix(item, f"prior_grams[{index}]")
        if gram.shape != (b.shape[0], b.shape[0]):
            raise ValueError("prior Gram sensor dimensions disagree")
        values, vectors = _gram_eigendecomposition(gram, f"prior_grams[{index}]")
        if values[0] <= 0:
            raise ValueError("anchor projection requires positive-definite prior Grams")
        matrices.append((gram+gram.T)/2)
        spectra.append((values, vectors))
    best: ConstructedPriorWitness | None = None
    for index, (values, vectors) in enumerate(spectra):
        coordinates = vectors.T @ y
        roots = np.sqrt(values)
        if float(np.linalg.norm(coordinates/roots)) <= eta:
            continue
        def coefficient(multiplier: float) -> np.ndarray:
            return roots*coordinates/(values+multiplier)
        high = float(values[-1])
        while float(np.linalg.norm(coefficient(high))) > eta:
            high *= 2.0
            if not np.isfinite(high):
                raise ValueError("anchor projection multiplier overflow")
        low = 0.0
        for _ in range(120):
            middle = (low+high)/2.0
            if float(np.linalg.norm(coefficient(middle))) > eta:
                low = middle
            else:
                high = middle
        z = coefficient((low+high)/2.0)
        residual = vectors @ (coordinates-roots*z)
        distance = float(np.linalg.norm(residual))
        if distance <= 0:
            continue
        u = residual/distance
        signal = float(abs(u@y))
        supports = [float(np.sqrt(max(u@gram@u, 0.0))) for gram in matrices]
        lower = float((signal-eta*max(supports))/gain)
        if lower <= 1e-10*max(signal/gain, 1.0):
            continue
        anchor_distance = distance/gain
        tight = bool(abs(lower-anchor_distance) <= 1e-7*max(anchor_distance, 1.0))
        candidate = ConstructedPriorWitness(
            retained_direction=c.copy(), sensor_witness=u,
            anchor_index=index,
            normalized_common_margin_lower=lower,
            normalized_anchor_distance=float(anchor_distance),
            tight_for_convex_prior_hull=tight,
            claim_boundary="one fixed retained direction against finite declared prior ellipsoids and their convex covariance mixtures; not measured-noise decoding",
        )
        if (best is None or lower > best.normalized_common_margin_lower + 1e-10
                or (abs(lower-best.normalized_common_margin_lower) <= 1e-10
                    and tight and not best.tight_for_convex_prior_hull)):
            best = candidate
    return best


def tail_closed_margin_frontier(
    retained_operator: np.ndarray,
    tail_gram: np.ndarray,
    *,
    eta: float = 1.0,
    gram_error_bound: float = 0.0,
    grid_size: int = 257,
) -> TailClosedFrontier:
    """Return conservative grid lower bounds for a tail-closed frontier.

    ``retained_operator`` is B and ``tail_gram`` is C=D D.T in a shared,
    reference-consistent sensor space.  ``gram_error_bound`` is a one-sided
    bound epsilon such that the unknown true competitor Gram is no larger than
    C + epsilon I.  The returned values are lower bounds found on a declared
    scalar grid, not global optima or outward-rounded proofs.
    """
    b = _finite_matrix(retained_operator, "retained_operator")
    c = _finite_matrix(tail_gram, "tail_gram")
    if c.shape != (b.shape[0], b.shape[0]):
        raise ValueError("sensor dimensions disagree")
    if not np.isfinite(eta) or eta <= 0:
        raise ValueError("eta must be finite and positive")
    if not np.isfinite(gram_error_bound) or gram_error_bound < 0:
        raise ValueError("gram_error_bound must be finite and nonnegative")
    if not isinstance(grid_size, int) or grid_size < 3:
        raise ValueError("grid_size must be an integer >= 3")

    c = (c + c.T) / 2
    values, vectors = _gram_eigendecomposition(c, "tail_gram")
    scale = float(np.sqrt(values.max()))
    if scale <= np.finfo(float).tiny:
        raise ValueError("tail_gram must have nonzero scale")
    b = b / scale
    c_values = values / (scale * scale)
    e = vectors.T @ b
    gain_squared = float(np.linalg.norm(b, ord=2) ** 2)
    if gain_squared <= np.finfo(float).tiny:
        raise ValueError("retained_operator must have nonzero norm")
    t_max = gain_squared / (eta * eta)
    error = float(gram_error_bound) / (scale * scale)
    # Include zero and logarithmic endpoints. The zero endpoint has H=0.
    multipliers = np.r_[0.0, np.geomspace(t_max * 1e-16, t_max, grid_size)]
    lower = np.zeros(b.shape[1], dtype=np.float64)
    selected = np.zeros_like(lower)
    bases: list[np.ndarray | None] = [None] * b.shape[1]
    eye = np.eye(b.shape[1])
    for t in multipliers:
        if t == 0.0:
            eigenvalues = np.zeros(b.shape[1], dtype=np.float64)
            eigenvectors = eye
        else:
            h = t * (e.T @ ((1.0 / (c_values + t + error))[:, None] * e)) - t * eta * eta * eye
            values, vectors = np.linalg.eigh((h + h.T) / 2)
            eigenvalues = values[::-1]
            eigenvectors = vectors[:, ::-1]
        improved = eigenvalues > lower
        lower[improved] = eigenvalues[improved]
        selected[improved] = t
        for index in np.flatnonzero(improved):
            bases[index] = eigenvectors[:, :index + 1].copy()
    return TailClosedFrontier(
        normalized_lower_margin=np.sqrt(np.maximum(lower, 0.0) / gain_squared),
        selected_multiplier=selected,
        selected_basis_by_rank=tuple(bases),
        scale=scale,
        gram_error_bound=float(gram_error_bound),
        claim_boundary="finite-mesh model observability under the declared operator and prior; not physiological localization",
    )


def tail_closed_relative_margin_frontier(
    retained_operator: np.ndarray,
    tail_gram: np.ndarray,
    *,
    eta: float = 1.0,
    gram_error_bound: float = 0.0,
    grid_size: int = 257,
) -> TailClosedRelativeFrontier:
    """Compute relative-margin lower bounds without a global gain penalty.

    For ``B`` the retained operator, ``C = D D.T`` the competitor Gram, and
    coefficient budget ``||z|| <= eta * ||c||``, the S-lemma matrix at
    multiplier ``t > 0`` is

        H(t) = t B.T (C + t I)^-1 B - t eta**2 I.

    A rank-``k`` coefficient subspace ``V`` has relative separation at least
    ``delta`` when ``V.T @ (H(t) - delta**2 * B.T @ B) @ V`` is positive
    definite. On the row space of ``B``, ``B.T @ B`` is positive definite;
    the maximum feasible ``delta**2`` at fixed ``t`` is therefore the
    ``k``-th largest generalized eigenvalue of ``(H(t), B.T @ B)``. The
    nullspace of ``B`` is excluded because ``H(t)`` is strictly negative
    there for positive ``t``.

    The returned values maximize over a declared logarithmic multiplier grid.
    Every positive result is an attainable finite-model lower bound under the
    supplied one-sided Gram-error bound. This function makes no claim about
    physiological source recovery, calibrated uncertainty, or global
    continuous-multiplier optimality.
    """
    b = _finite_matrix(retained_operator, "retained_operator")
    c = _finite_matrix(tail_gram, "tail_gram")
    if c.shape != (b.shape[0], b.shape[0]):
        raise ValueError("sensor dimensions disagree")
    if not np.isfinite(eta) or eta <= 0:
        raise ValueError("eta must be finite and positive")
    if not np.isfinite(gram_error_bound) or gram_error_bound < 0:
        raise ValueError("gram_error_bound must be finite and nonnegative")
    if not isinstance(grid_size, int) or grid_size < 3:
        raise ValueError("grid_size must be an integer >= 3")

    c = (c + c.T) / 2
    c_values, c_vectors = _gram_eigendecomposition(c, "tail_gram")
    scale = float(np.sqrt(c_values[-1]))
    if scale <= np.finfo(float).tiny:
        raise ValueError("tail_gram must have nonzero scale")
    b = b / scale
    c_values = c_values / (scale * scale)
    error = float(gram_error_bound) / (scale * scale)
    e = c_vectors.T @ b

    _, singular_values, right_vectors_t = np.linalg.svd(b, full_matrices=False)
    if singular_values.size == 0 or singular_values[0] <= np.finfo(float).tiny:
        raise ValueError("retained_operator must have nonzero rank")
    rank_tolerance = np.finfo(float).eps * max(b.shape) * singular_values[0]
    effective_rank = int(np.count_nonzero(singular_values > rank_tolerance))
    singular_values = singular_values[:effective_rank]
    coefficient_vectors = right_vectors_t[:effective_rank].T
    inverse_singular = 1.0 / singular_values
    p = b.shape[1]
    gain_squared = float(singular_values[0] ** 2)
    t_max = gain_squared / (eta * eta)
    if not np.isfinite(t_max) or t_max <= 0:
        raise ValueError("retained_operator scale is numerically unresolved")
    multipliers = np.r_[0.0, np.geomspace(t_max * 1e-16, t_max, grid_size)]

    lower = np.zeros(p, dtype=np.float64)
    selected = np.zeros(p, dtype=np.float64)
    bases: list[np.ndarray | None] = [None] * p
    for t in multipliers[1:]:
        resolvent_b = e / (c_values + t + error)[:, None]
        h = t * (e.T @ resolvent_b) - t * eta * eta * np.eye(p)
        h = (h + h.T) / 2
        h_reduced = coefficient_vectors.T @ h @ coefficient_vectors
        generalized = (inverse_singular[:, None] * h_reduced) * inverse_singular[None, :]
        eigenvalues, eigenvectors = np.linalg.eigh((generalized + generalized.T) / 2)
        order = np.argsort(eigenvalues)[::-1]
        eigenvalues = eigenvalues[order]
        eigenvectors = eigenvectors[:, order]
        improved = eigenvalues > lower[:effective_rank]
        for index in np.flatnonzero(improved):
            lower[index] = float(eigenvalues[index])
            selected[index] = t
            raw_basis = coefficient_vectors @ (inverse_singular[:, None] * eigenvectors[:, :index + 1])
            bases[index] = np.linalg.qr(raw_basis, mode="reduced")[0]

    return TailClosedRelativeFrontier(
        normalized_lower_margin=np.sqrt(np.maximum(lower, 0.0)),
        selected_multiplier_scaled=selected,
        selected_basis_by_rank=tuple(bases),
        effective_rank=effective_rank,
        operator_scale=scale,
        multiplier_grid_size=grid_size,
        claim_boundary=(
            "finite-mesh relative separation under the declared retained operator, "
            "competitor Gram, coefficient budget, and one-sided Gram-error bound; "
            "not physiological localization or calibrated uncertainty"
        ),
    )
