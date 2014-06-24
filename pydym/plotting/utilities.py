""" file:   utilities.py (pydym.plotting)
    author: Jess Robertson
            CSIRO Minerals Resources Flagship
    date:   Tuesday 24 June 2014

    description: Utility functions for plotting
"""

import matplotlib.pyplot as plt


def make_axes_grid(nplots, ncols=3):
    """ Make an axes grid

        :param nplots: The number of plots in the grid
        :type nplots: int
        :param ncols: The number of columns in the grid
        :type ncols: int
    """
    nrows = nplots // ncols
    if ncols * nrows < nplots:
        nrows += 1
    return plt.GridSpec(nrows, ncols)
