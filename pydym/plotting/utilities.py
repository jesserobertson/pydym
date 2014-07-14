""" file:   utilities.py (pydym.plotting)
    author: Jess Robertson
            CSIRO Minerals Resources Flagship
    date:   Tuesday 24 June 2014

    description: Utility functions for plotting
"""

from __future__ import division
import numpy
import matplotlib.pyplot as plt
import matplotlib.mlab as mlab


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


def interpolator(data):
    """ Generate an interpolator for the flow data
    """
    xval, yval = data['position/x'], data['position/y']
    xlim = xval.min(), xval.max()
    ylim = yval.min(), yval.max()
    nx, ny = map(len, (xval, yval))
    xs, ys = numpy.linspace(*xlim, num=nx), numpy.linspace(*ylim, num=ny)
    return xs, ys, \
        lambda var: mlab.griddata(xval, yval, xs, ys, interp='linear')
