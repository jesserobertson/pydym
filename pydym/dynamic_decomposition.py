""" file:   dynamic_decomposition.py (pydym)
    author: Jess Robertson
            CSIRO Minerals Resources Flagship
    date:   Tuesday 24 June 2014

    description: Dynamic decomposition of a data stream
"""

from __future__ import division, print_function

from scipy import linalg
from numpy.linalg import matrix_rank
from numpy import dot, hstack, trace, diag

from .utilities import foldr, herm_transpose

def dynamic_decomposition(data, burn=100):
    r""" Perform a dynamic decomposition on a dataset

        We want to minimize the least-squares deviation between the matrix of
        snapshots `past` and the linear combination of the DMD modes.

        Can be formulated (see Jovanovic et al, 2014; Eqn 4) as:

            minimize || sigma * tr(V) - Y * diag(x) * Z ||_F^2

        where sigma and V are the singular values and right singular vectors of
        $F_{dmd}$, $Y$ is the matrix of eigenvectors of $F_{dmd}$, and $Z$ is
        the Vandermond matrix formed from the eigenvalues of $F_{dmd}$:
        $Z_{ij} = [\mu_j^i]$ To solve we just rewrite as optimization
        problem min J(x) where:

            J(x) = tr(x) . P . x - tr(q) . x - tr(x) . q + s

        (Jovanovic Eqn 6) which has solution x = P^{-1} q.
    """
    # pylint: disable=C0103, R0914
    # Subdivide the time sequence into the past and current states
    past = data.snapshots[:, burn:-1]
    current = data.snapshots[:, (burn + 1):]

    # Calculate SVD of past data array
    U, sigma, Vstar = linalg.svd(past, full_matrices=False)
    V = herm_transpose(Vstar)

    ## Calculate approximate dynamic array given current data
    # and calculate eigendecomposition
    Fdmd = foldr(dot, (herm_transpose(U), current, V, diag(1 / sigma)))
    rank = matrix_rank(Fdmd)
    eigvals, eigvecs = linalg.eig(Fdmd)

    # Construct Vandermonde matrix from eigenvalue
    n_snapshots = Vstar.shape[1]
    eigvals_r = eigvals.reshape(rank, 1)
    vandermonde = hstack((eigvals_r ** n for n in range(n_snapshots)))

    ## Compute mode weightings
    # Construct matrices
    P = (dot(herm_transpose(eigvecs), eigvecs)
         * (dot(vandermonde, herm_transpose(vandermonde)).conj())).real
    tmp = dot(diag(sigma), Vstar)
    q = diag(foldr(dot, (vandermonde, herm_transpose(tmp), eigvecs)))
    s = trace(dot(herm_transpose(tmp), tmp))

    # Calculate optimal vector of amplitudes, x
    L = linalg.cholesky(P, lower=True)
    amplitudes = linalg.solve(herm_transpose(L), linalg.solve(L, q))

    return {
        'eigenvalues': eigvals,
        'eigenvectors': eigvecs,
        'amplitudes': amplitudes,
        'modes': (dot(U, eigvecs) * amplitudes).real,
        'intermediate_values': {
            'svd': (U, sigma, V),
            'weights': (P, q, s)
        }
    }
