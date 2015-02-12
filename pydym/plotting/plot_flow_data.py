""" file:   plot_flow_data.py (pydym,plotting)
    author: Jess Robertson
            CSIRO Minerals Resources Flagship
    date:   Tuesday 24 June 2014

    description: Plotting functions for flow data
"""

from __future__ import division
import matplotlib.pyplot as plt
import numpy


def plot_flow_data(datum, axes=None, n_quiver=3, n_contours=20):
    """ Plot the flow field in a FlowDatum instance
    """
    if axes is None:
        plt.figure(figsize=(11, 11))
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

    # Try for pressure field, fall back to
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
