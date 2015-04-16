""" file:   dynamic_decomposition.py (pydym)
    author: Jess Robertson
            CSIRO Minerals Resources Flagship
    date:   Tuesday 24 June 2014

    description: Dynamic decomposition of a data stream
"""

from __future__ import division, print_function

import numpy
from scipy import linalg
from numpy.linalg import matrix_rank

from .utilities import foldr, herm_transpose

class dynamic_decomposition(object):

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

    def __init__(self, data, burn=None):
        # Sort out inputs
        super(dynamic_decomposition, self).__init__()
        self.data = data
        self.burn = burn or 0

        # Set up initial dynamic mode decomposition
        self.pod_modes = None
        self.eigenvalues, self.eigenvectors = None, None
        self.amplitudes, self.modes = None, None
        self._mode_weight_data = (None, None, None)
        self.decompose()

        # Set up some other stuff used for sparsity
        self.rho = 1              # the augmented Lagrangian parameter used in sparsity solver
        self.max_iter = 10000     # the maximum number of iterations allowed for ADMM
        self.absolute_tol = 1e-6  # } Tolerances for the sparsity solver
        self.relative_tol = 1e-4  # }
        self.n_nonzero, self.pre_polish_norm = None, None
        self.polished_amplitudes, self.residual, self.performance_loss = None, None, None

    def decompose(self):
        """ Decompose the data into a Dynamic Mode Decomposition
        """
        # pylint: disable=C0103, R0914
        # Subdivide the time sequence into the past and current states
        past = self.data.snapshots[:, self.burn:-1]
        current = self.data.snapshots[:, (self.burn + 1):]

        # Calculate SVD 'pod modes' of past data array
        U, sigma, Vstar = linalg.svd(past, full_matrices=False)
        V = herm_transpose(Vstar)
        self.pod_modes = (U, sigma, V)

        ## Calculate approximate dynamic array given current data
        # and calculate eigendecomposition
        Fdmd = foldr(numpy.dot, (herm_transpose(U), current, V, numpy.diag(1 / sigma)))
        rank = matrix_rank(Fdmd)
        self.eigenvalues, self.eigenvectors = linalg.eig(Fdmd)

        # Construct Vandermonde matrix from eigenvalue
        n_snapshots = Vstar.shape[1]
        eigvals_r = self.eigenvalues.reshape(rank, 1)
        vandermonde = numpy.hstack((eigvals_r ** n for n in range(n_snapshots)))

        ## Compute mode weightings
        # Construct matrices
        P = (numpy.dot(herm_transpose(self.eigenvectors), self.eigenvectors)
             * (numpy.dot(vandermonde, herm_transpose(vandermonde)).conj())).real
        tmp = numpy.dot(numpy.diag(sigma), Vstar)
        q = numpy.diag(foldr(numpy.dot,
                             (vandermonde, herm_transpose(tmp), self.eigenvectors)))
        s = numpy.trace(numpy.dot(herm_transpose(tmp), tmp))

        # Stash some intermediate values for later use by the sparsity algorithm
        self._mode_weight_data = (P, q, s)

        # Calculate optimal vector of amplitudes, alpha
        L = linalg.cholesky(P, lower=True)
        self.amplitudes = linalg.solve(herm_transpose(L), linalg.solve(L, q))
        self.modes = (numpy.dot(U, self.eigenvectors) * self.amplitudes).real

    def sparsify(self, gamma=1):
        """ Enforce sparsity in a DMD

            Parameters:
                results - the output from a dynamic_decomposition call
                gamma - the sparsity parameter

            There are also several optional parameters:
                rho - the augmented Lagrangian parameter used to regularize the
                    problem. Optional, defaults to 1.
                max_iter - the maximum number of iterations allowed for ADMM,
                    defaults to 10,000 iterations
                absolute_tol - absolute tolerance
                relative_tol - relative tolerance
        """
        # pylint: disable=C0103, R0914
        # Pull out relevant bits
        P, q, s = self._mode_weight_data
        alpha = self.amplitudes

        # Cholesky factorization of matrix P + (rho/2 * I)
        n_variables = q.shape[0]
        L = linalg.cholesky((P + (self.rho / 2.) * numpy.identity(n_variables)),
                            lower=True)
        Lstar = herm_transpose(L)

        # Initial conditions
        y = numpy.zeros(n_variables)  # Lagrange multiplier
        z = numpy.zeros(n_variables)  # Old copy of x

        # ADMM loop
        for step in range(self.max_iter):
            # Minimize x
            tmp = q + (self.rho / 2.) * (z - y / self.rho)
            x_new = linalg.solve(Lstar, linalg.solve(L, tmp))

            # Minimize z via thresholding
            threshold = (gamma / self.rho) * numpy.ones(n_variables)
            tmp = x_new + y / self.rho
            z_new = ((1 - threshold / abs(tmp)) * tmp) * (abs(tmp) > threshold)

            # Primal and dual residuals
            rprim = linalg.norm(x_new - z_new)
            rdual = self.rho * linalg.norm(z_new - z)

            # Update multiplier
            y = y + self.rho * (x_new - z_new)

            # Check stopping criteria
            epsprim = numpy.sqrt(n_variables) * self.absolute_tol \
                      + self.relative_tol * max([linalg.norm(x) for x in (x_new, z_new)])
            epsdual = numpy.sqrt(n_variables) * self.absolute_tol \
                      + self.relative_tol * linalg.norm(y)
            if (rprim < epsprim) and (rdual < epsdual):
                print((' ** ADMM converged **\n'
                       + ' -- ADMM step {0}\n'.format(step)
                       + '    primal residual: {0} (eps = {1})\n'.format(rprim, epsprim)
                       + '    dual residual:   {0} (eps = {1})\n'.format(rdual, epsdual)))
                break
            else:
                if step % 50 == 0:
                    print((' -- ADMM step {0}\n'.format(step)
                           + '    primal residual: {0} (eps = {1})\n'.format(rprim, epsprim)
                           + '    dual residual:   {0} (eps = {1})\n'.format(rdual, epsdual)))
                z = z_new

        # Record some output data
        results = {
            'amplitudes': z,
            'n_nonzero': numpy.count_nonzero(z),
            'pre_polish_norm': (
                foldr(numpy.dot, (herm_transpose(z), P, z)).real
                - 2 * numpy.dot(herm_transpose(q), z).real + s)
        }

        ## Polish non-zero amplitudes
        # Form Karush-Kuhn-Tucker system
        zero_idx = numpy.argwhere(abs(z) < 1e-10)[:, 0]
        size = len(zero_idx)
        E = numpy.identity(n_variables)[:, zero_idx]
        kkt_system = numpy.bmat([
            [P, E],
            [herm_transpose(E), numpy.zeros((size, size))]
        ])
        rhs = numpy.hstack((q, numpy.zeros((size,))))

        # Solve system for polished amplitudes, alpha
        soln = linalg.solve(kkt_system, rhs)
        alpha = soln[:n_variables]
        alpha[zero_idx] = 0

        # Calculate residual
        residual = foldr(numpy.dot, (herm_transpose(alpha), P, alpha)).real \
                   - 2 * numpy.dot(herm_transpose(q), alpha).real + s

        # Record output data
        results.update({
            'polished_amplitudes': alpha,
            'residual': residual,
            'performance_loss': 100 * numpy.sqrt(abs(residual) / s)
        })
        for result, value in results.items():
            setattr(self, result, value)
