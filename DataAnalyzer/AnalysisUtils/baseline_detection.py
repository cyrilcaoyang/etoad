import numpy as np
from scipy import sparse
from scipy.sparse.linalg import spsolve


def als_baseline_detection(
        values: np.ndarray,
        smoothing: float,
        weighting: float,
        iterations=10
) -> np.ndarray:
    """
    Detects the baseline of a given numpy array using the algorithm of asymmetric least squares smoothing.
    (P.H.C. Eilers, Kwantitatieve Methoden 1987, 8, 45-64 // P. H. C Eilers, H. Boelens, 2005).

    Args:
        values: 1D Numpy array of values to determine the baseline in.
        smoothing: Smoothing parameter (the larger, the smoother the baseline)
        weighting: Weights of deviations (between 0 and 0.5, the smaller, the stronger peak suppression)
        iterations: Iterations for the solver (default: 10)

    Returns:
        baseline: Fitted baseline
    """
    length: int = len(values)
    d_matrix = sparse.diags([1, -2, 1], [0, -1, -2], shape=(length, length-2))
    d_matrix = smoothing * d_matrix.dot(d_matrix.transpose())
    w_vector = np.ones(length)
    w_matrix = sparse.spdiags(np.ones(length), 0, length, length)
    baseline: np.ndarray = np.zeros(length)

    for _ in range(iterations):
        w_matrix.setdiag(w_vector)
        z_matrix = w_matrix + d_matrix
        baseline: np.ndarray = spsolve(z_matrix, w_vector * values)
        w_vector = weighting * (values > baseline) + (1 - weighting) * (values < baseline)

    return baseline


def als_baseline_removal(
        values: np.ndarray,
        smoothing: float,
        weighting: float,
        iterations=10
) -> np.ndarray:
    """
    Removes the baseline of a given numpy array using the algorithm of asymmetric least squares smoothing.
    (P.H.C. Eilers, Kwantitatieve Methoden 1987, 8, 45-64 // P. H. C Eilers, H. Boelens, 2005).

    Args:
        values: 1D Numpy array of values to determine the baseline in.
        smoothing: Smoothing parameter (the larger, the smoother the baseline)
        weighting: Weights of deviations (between 0 and 0.5, the smaller, the stronger peak suppression)
        iterations: Iterations for the solver (default: 10)

    Returns:
        values_corrected: Array with removed baseline
    """
    baseline = als_baseline_detection(values, smoothing, weighting, iterations)
    return values - baseline
