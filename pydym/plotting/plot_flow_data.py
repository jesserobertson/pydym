""" file:   plot_flow_datum.py (pydym.plotting)
    author: Jess Robertson
            CSIRO Minerals Resources Flagship
    date:   Tuesday 24 June 2014

    description: Plotting functions for flow data
"""

from __future__ import division

import numpy
import matplotlib.pyplot as plt
import numpy


def plot_flow_datum(data, axes=None, decimate_by=10):
    """ Plot a FlowDatum instance
    """
    xval, yval = data.position[0], data.position[1]
    xlim = xval.min(), xval.max()
    ylim = yval.min(), yval.max()
    nx, ny = len(xval), len(yval)
    xs, ys = numpy.linspace(*xlim, num=nx), numpy.linspace(*ylim, num=ny)
    xs, ys, Ps = data.interpolate('pressure')
    _, _, Ts = data.interpolate('tracer')

    # Plot the results
    if axes is None:
        axes = plt.gca()
    axes.set_aspect('equal')

    # Try to get tracer field
    try:
        xs, ys, ts = datum.interpolate('tracer')
        axes.contour(xs, ys, ts, [0.5],
                     colors=['black'], linewidths=[2],
                     alpha=0.5)
        axes.contourf(xs, ys, ts, [0.5, 1],
                      colors=['black'], alpha=0.1,
                      zorder=1)
    except AttributeError:
        pass

    # Absolute velocity for colors
    datum['abs_velocity'] = \
      numpy.sqrt(datum.velocity[0] ** 2 + datum.velocity[1] ** 2)
    xs, ys, ps = datum.interpolate('abs_velocity')
    axes.contourf(xs, ys, ps, n_contours,
                  cmap=plt.get_cmap('RdYlBu'),
                  alpha=0.6,
                  zorder=0)
    axes.quiver(datum.position[0, ::n_quiver],
                datum.position[1, ::n_quiver],
                datum.velocity[0, ::n_quiver],
                datum.velocity[1, ::n_quiver])
    axes.add_patch(plt.Rectangle((-1.5, -0.5), 1, 1,
                   edgecolor='none',
                   facecolor='white',
                   zorder=100))
    axes.add_patch(plt.Rectangle((0.5, -0.5), 1, 1,
                   edgecolor='none',
                   facecolor='white',
                   zorder=100))
    axes.set_axis_off()
    axes.set_xlim(min(xs), max(xs))
    axes.set_ylim(min(ys), max(ys))
