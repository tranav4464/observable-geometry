# Mathematical definition

Let \(G=[g_1,\ldots,g_n]\in\mathbb{R}^{m\times n}\) be the leadfield: column \(g_i\) is the sensor pattern predicted by one candidate source. Let \(C\in\mathbb{R}^{m\times m}\) be the noise covariance for the same sensors, ordering and reference.

Because referencing or rejected channels can make \(C\) rank deficient, write its supported eigendecomposition as

\[
C=U\Lambda U^\top,
\]

where \(U\) contains eigenvectors with positive supported eigenvalues and \(\Lambda\) contains those eigenvalues. The noise-whitened signature is

\[
z_i=\Lambda^{-1/2}U^\top g_i.
\]

Whitening expresses a pattern in units of the declared noise covariance. Normalize it to remove its overall amplitude:

\[
u_i=\frac{z_i}{\lVert z_i\rVert_2}.
\]

The reported pair score is the absolute cosine

\[
\rho_{ij}=|u_i^\top u_j|,\qquad 0\leq\rho_{ij}\leq 1.
\]

A score near one means the two modeled patterns point in nearly the same or opposite direction after noise whitening. Absolute value makes polarity a nuisance: reversing every sign does not change the comparison. Normalization also removes gain, so the score does not say that both sources would be equally easy to detect.

The associated best-fit residual after allowing the competing source's amplitude and sign to vary is

\[
r_{ij}=\sqrt{\max(0,1-\rho_{ij}^2)}.
\]

The program excludes pairs closer than the chosen Euclidean distance and ranks the eligible alternatives. The minimum-distance choice is a user setting, not a universal biological boundary.

## Interpretation

These equations compare columns of a declared forward model. They do not analyze an observed EEG event, include distributed-source alternatives unless those are supplied as columns, or provide calibrated uncertainty. Their meaning depends on the candidate source family, reference, covariance and forward model. The normalized cosine is established mathematics; the project's contribution is the inspectable software workflow and its provenance controls, not a new similarity formula.
