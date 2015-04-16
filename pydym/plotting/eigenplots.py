""" file:   eigenplots.py (pydym.plotting)
    author: Jess Robertson
            CSIRO Minerals Resources Flagship
    date:   Tuesday 24 June 2014

    description: Plotting functions for flow data
"""

import matplotlib.pyplot as plt
import numpy


def eigenplot(dmd_result, amplitudes=None, cmap=None):
    """ Generate an eigenvalue plot with optional shading

        Parameters:
            eigenvalues - the eigenvalues to plot
            amplitudes - the amplitudes of each eigenvalue. Optional, if None
                then all eigenvalues are plotted in black, if specified then
                the amplitudes are used with the colormap
            cmap - the name of the matplotlib colormap to use

        Returns:
            (fig, axes) - Handles to the matplotlib.pyplot.figure and .axes
                instances containing the plot.
    """
    # Pull out relevant info
    eigvals = dmd_result.eigenvalues
    alpha = dmd_result.amplitudes

    # Set up background colors etc
    angles = numpy.linspace(0, 2 * numpy.pi, 299)
    circle = numpy.sin(angles), numpy.cos(angles)
    if amplitudes:
        cmap = plt.get_cmap(cmap if cmap else 'coolwarm')
        shade_by = numpy.log(numpy.abs(alpha))
        colors = cmap((shade_by - shade_by.min())
                      / (shade_by.max() - shade_by.min()))

    # Generate two plots, one with all values, one zoomed in on 1 + 0j
    fig = plt.figure(figsize=(8, 4))
    for axidx in (1, 2):
        axes = plt.subplot(1, 2, axidx)
        if amplitudes:
            axes.scatter(eigvals.real, eigvals.imag,
                         marker='o', edgecolor=colors, facecolor=colors)
        else:
            axes.scatter(eigvals.real, eigvals.imag,
                         marker='.', edgecolor='black', facecolor='black')
        axes.plot(*circle, color='black', dashes=(5, 3))
        axes.set_aspect('equal')
        axes.set_xlim(-1.01, 1.01)
        axes.set_ylim(-1.01, 1.01)
        axes.set_xlabel(r'Re($\lambda_{i}$)')
        axes.set_ylabel(r'Im($\lambda_{i}$)')

    # Resize second set of axes
    axes.set_aspect(0.1 / 0.4)
    axes.set_xlim(0.8, 1)
    axes.set_ylim(-0.5, 0.5)
    fig.tight_layout()
    return fig, axes
