""" file:   plot_flow_snapshot.py (pydym.plotting)
    author: Jess Robertson
            CSIRO Minerals Resources Flagship
    date:   Tuesday 24 June 2014

    description: Plotting functions for flow Snapshot
"""

from __future__ import division

import numpy
import matplotlib.pyplot as plt


def plot_snapshot(snapshot, axes=None, decimate_by=10):
    """ Plot a Snapshot instance
    """
    if axes is None:
        axes = plt.gca()
    axes.set_aspect('equal')

    # Plot tracer if we can, otherwise plot abs velocity
    try:
        xgrid, ygrid, tracer = snapshot.interpolate('tracer')
        axes.contour(xgrid, ygrid, tracer, [0.5],
                     colors=['gray'], linewidths=[2], zorder=2, alpha=0.6)
        axes.contourf(xgrid, ygrid, tracer, [-0.1, 0.5, 1.1],
                      colors=['red', 'gold'], extend='both',
                      alpha=0.6, zorder=1)
    except AttributeError:
        _, _, xvel = snapshot.interpolate('velocity', 'x')
        _, _, yvel = snapshot.interpolate('velocity', 'y')
        axes.contourf(xgrid, ygrid, numpy.sqrt(xvel ** 2 + yvel ** 2),
                      cmap='Spectral', alpha=0.7, zorder=1)

    # Plot velocity field
    axes.quiver(snapshot.position[0][::decimate_by], 
                snapshot.position[1][::decimate_by],
                snapshot.velocity[0][::decimate_by],
                snapshot.velocity[1][::decimate_by],
                zorder=3)
    axes.set_axis_off()
    axes.set_xlim(min(xgrid), max(xgrid))
    axes.set_ylim(min(ygrid), max(ygrid))
