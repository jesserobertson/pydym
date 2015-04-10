""" file:   sparse_decomposition.py (pydym)
    author: Jess Robertson
            CSIRO Minerals Resources Flagship
    date:   Tuesday 24 June 2014

    description: Sparsity-preserving dynamic decomposition of a data stream
"""

from __future__ import division, print_function

from scipy import linalg
from numpy import dot, hstack, vstack, trace, diag, zeros

from .utilities import herm_transpose, foldr

def sparsify_dynamic_decomposition(results, gamma=1,
                                   rho=1, max_iter=10000,
                                   absolute_tol=1e-6,
                                   relative_tol=1e-4):
    """ Enforce sparsity in a DMD

        Parameters:
            results - the output from a dynamic_decomposition call
            gamma - the sparsity parameter

        Optional parameters:
            rho - the augmented Lagrangian parameter used to regularize the
                problem. Optional, defaults to 1.
            max_iter - the maximum number of iterations allowed for ADMM
            absolute_tol - absolute tolerance
            relative_tol - relative tolerance
    """
    # Pull out relevant bits
    U, sigma, V = results['intermediate_values']['svd']
    P, q, s = results['intermediate_values']['weights']
    Y = results['eigenvectors']
    mu = results['eigenvalues']
    alpha = results['amplitudes']

    # Cholesky factorization of matrix P + (rho/2 * I)
    n_variables = q.shape[0]
    L = linalg.cholesky((P + (rho / 2.) * identity(n_variables)),
                        lower=True)
    Lstar = herm_transpose(L)

    # Initial conditions
    y = zeros(n_variables)  # Lagrange multiplier
    z = zeros(n_variables)  # Old copy of x

    # ADMM loop
    for step in xrange(max_iter):
        # Minimize x
        tmp = q + (rho / 2.) * (z - y / rho)
        x_new = linalg.solve(Lstar, linalg.solve(L, tmp))

        # Minimize z via thresholding
        threshold = (gamma / rho) * ones(n_variables)
        tmp = x_new + y / rho
        z_new = ((1 - threshold / abs(tmp)) * tmp) * (abs(tmp) > threshold)

        # Primal and dual residuals
        rprim = linalg.norm(x_new - z_new)
        rdual = rho * linalg.norm(z_new - z)

        # Update multiplier
        y = y + rho * (x_new - z_new)

        # Check stopping criteria
        epsprim = sqrt(n_variables) * absolute_tol \
                  + relative_tol * max(map(linalg.norm, (x_new, z_new)))
        epsdual = sqrt(n_variables) * absolute_tol \
                  + relative_tol * linalg.norm(y)
        if (rprim < epsprim) and (rdual < epsdual):
            print(' ** ADMM converged **')
            print(' -- ADMM step {0}'.format(step))
            print('    primal residual: {0} (eps = {1})'.format(rprim, epsprim))
            print('    dual residual:   {0} (eps = {1})\n'.format(rdual, epsdual))
            break
        else:
            if step % 50 == 0:
                print(' -- ADMM step {0}'.format(step))
                print('    primal residual: {0} (eps = {1})'.format(rprim, epsprim))
                print('    dual residual:   {0} (eps = {1})\n'.format(rdual, epsdual))
            z = z_new

    # Record some output data
    results = {
        'amplitudes': z,
        'n_nonzero': count_nonzero(z),
        'pre_polish_norm': foldr(dot, (herm_transpose(z), P, z)).real
                           - 2 * dot(herm_transpose(q), z).real + s
    }

    # Polish non-zero amplitudes
    zero_idx = argwhere(abs(z) < 1e-10)[:, 0]
    m = len(zero_idx)
    eye = identity(n_variables)
    E = eye[:, zero_idx]

    # Form KKT system, solve and calculate residual
    KKT = bmat([[P, E], [herm_transpose(E), zeros((m, m))]])
    spy(KKT)
    rhs = hstack((q, zeros((m,))))
    soln = linalg.solve(KKT, rhs)
    alpha = soln[:n_variables]
    alpha[zero_idx] = 0
    residual = foldr(dot, (herm_transpose(alpha), P, alpha)).real \
               - 2 * dot(herm_transpose(q), alpha).real + s

    # Recod output data
    results.update({
        'polished_amplitudes': alpha,
        'residual': residual,
        'performance_loss': 100 * sqrt(abs(residual) / s)
    })
    return results
