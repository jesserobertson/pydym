""" file:   dynamic_decomposition.py (pydym)
    author: Jess Robertson
            CSIRO Minerals Resources Flagship
    date:   Tuesday 24 June 2014

    description: Dynamic decomposition of a data stream
"""

from __future__ import division
import numpy
from numpy.linalg import svd

from .utilities import foldr


def herm_transpose(array):
    """ Returns the Hermitian transpose of a complex matrix
    """
    return array.conj().transpose()


def dynamic_decomposition(flow_data, return_svd=False):
    """ Decompose the data in a set of flow measurements into SVD components

        Calculates an approximation S to the dynamic matrix A for a
        given set of velocity vectors.

        Velocity vectors should be given as complex numbers
        (i.e. $U = u + iv$).

        :returns: S, where S is the approximant. If return_svd is
            True, also returns the singular value decomposition
            U, Sigma, V
    """
    # Subdivide the time sequence into the past and current states
    past = flow_data.snapshot_array[:-1]
    current = flow_data.snapshot_array[1:]

    # Calculate SVD of past data array
    U, sigma, Vstar = svd(past, full_matrices=False)

    # Calculate apprioximate dynamic array
    S = foldr(numpy.dot, (herm_transpose(U), current, herm_transpose(Vstar),
                          numpy.diag(1 / sigma)))

    # Send back results
    if return_svd:
        return S, U, sigma, Vstar
    else:
        return S
