""" file:   plot_flow_data.py (pydym,plotting)
    author: Jess Robertson
            CSIRO Minerals Resources Flagship
    date:   Tuesday 24 June 2014

    description: Plotting functions for flow data
"""

from __future__ import division
import matplotlib.pyplot as plt

from .utilities import interpolator


def plot_flow_data(data, axes=None, n_quiver=3, n_contours=20):
    """ Plot some data output by Gerris
    """
    xs, ys, interp = interpolator(data)
    Ps = interp('pressure')
    Ts = interp('tracer')

    # Plot the results
    if axes is None:
        plt.figure(figsize=(11, 11))
        axes = plt.gca()
    axes.set_aspect('equal')
    axes.contour(xs, ys, Ts, [0.5], colors=['black'], linewidths=[2])
    axes.contourf(xs, ys, Ps, n_contours,
                  cmap=plt.get_cmap('RdYlBu'),
                  alpha=0.6)
    axes.quiver(data.position[::n_quiver, 0],
                data.position[::n_quiver, 1],
                data.velocity[::n_quiver, 0],
                data.velocity[::n_quiver, 1])
    axes.add_patch(plt.Rectangle((-1.5, -0.5), 1, 1,
                   edgecolor='none',
                   facecolor='white'))
    axes.add_patch(plt.Rectangle((0.5, -0.5), 1, 1,
                   edgecolor='none',
                   facecolor='white'))
    axes.set_axis_off()
    axes.set_xlim(min(xs), max(xs))
    axes.set_ylim(min(ys), max(ys))
