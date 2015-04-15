""" file:   plot_flow_datum.py (pydym.plotting)
    author: Jess Robertson
            CSIRO Minerals Resources Flagship
    date:   Tuesday 24 June 2014

    description: Plotting functions for flow data
"""

from __future__ import division

import numpy
import matplotlib.pyplot as plt


def plot_flow_datum(data, axes=None, decimate_by=10):
    """ Plot a Datum instance
    """
    xval, yval = data.position[0], data.position[1]

    # xlim = xval.min(), xval.max()
    # ylim = yval.min(), yval.max()
    xs, ys, Ts = data.interpolate('tracer', decimate_by=decimate_by)

    # Plot the results
    if axes is None:
        axes = plt.gca()
    axes.set_aspect('equal')
    try:
        _, _, Ts = data.interpolate('tracer')
        axes.contour(xs, ys, Ts, [0.5],
                     colors=['gray'], linewidths=[2], zorder=2, alpha=0.6)
        axes.contourf(xs, ys, Ts, [-0.1, 0.5, 1.1],
                      colors=['red', 'gold'], extend='both',
                      alpha=0.6, zorder=1)
    except AttributeError:
        _, _, us = data.interpolate('velocity', 'x')
        _, _, vs = data.interpolate('velocity', 'y')
        axes.contourf(xs, ys, numpy.sqrt(us ** 2 + vs ** 2),
                      cmap='Spectral', alpha=0.7, zorder=1)

    axes.quiver(xval[::decimate_by], yval[::decimate_by],
                data.velocity[0][::decimate_by],
                data.velocity[1][::decimate_by],
                zorder=3)
    axes.set_axis_off()
    axes.set_xlim(min(xs), max(xs))
    axes.set_ylim(min(ys), max(ys))
