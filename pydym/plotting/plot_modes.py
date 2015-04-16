""" file:   plot_modes.py
    author: Jess Robertson
            CSIRO Minerals Resources Flagship
    date:   Friday 11 July 2014

    description: Plotting dynamic mode data
"""

from __future__ import division

import matplotlib.pyplot as plt


def plot_modes(data, axes=None, n_quiver=3, n_contours=20):
    """ Plot the modes derived from a dynamic decomposition of the flow data.
    """
    xpos, ypos = data['position/x'], data['position/y']
    abs_velocity = data.velocity[:, ]

    # Plot the results
    if axes is None:
        plt.figure(figsize=(11, 11))
        axes = plt.gca()
    axes.set_aspect('equal')
    axes.contourf(xpos, ypos, abs_velocity, n_contours,
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
    axes.set_xlim(min(xpos), max(xpos))
    axes.set_ylim(min(ypos), max(ypos))
    axes.set_aspect('equal')
