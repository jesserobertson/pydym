""" file:   eigenplots.py (pydym.plotting)
    author: Jess Robertson
            CSIRO Minerals Resources Flagship
    date:   Tuesday 24 June 2014

    description: Plotting functions for flow data
"""

import matplotlib.pyplot as plt
import numpy


def eigenplot(array):
    """ Plot complex eigenvalues from a matrix
    """
    eigenvalues, eigenvectors = numpy.eig(array)
    pass


def logeigenplot(array):
    """ Plot log-transformed eigenvalues from a matrix
    """
    pass
