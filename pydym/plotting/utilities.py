""" file:   utilities.py (pydym.plotting)
    author: Jess Robertson
            CSIRO Minerals Resources Flagship
    date:   Tuesday 24 June 2014

    description: Utility functions for plotting
"""

from __future__ import division

import matplotlib.pyplot as plt
import numpy


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


def spy(array):
    """ Plot the log values of an array

        Parameters
            array - the array to plot

        Returns
            (fig, axes) - Handles to the figure and axes containing the plot
    """
    fig = plt.figure(figsize=(11, 11))
    axes = plt.gca()
    axes.imshow(numpy.log(array), interpolation='none')
    axes.set_axis_off()
    axes.set_aspect('equal')
    return fig, axes
