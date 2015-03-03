""" file:   plot_modes.py
    author: Jess Robertson
            CSIRO Minerals Resources Flagship
    date:   Friday 11 July 2014

    description: Plotting dynamic mode data
"""

def plot_modes(data, axes=None, n_quiver=3, n_contours=20):
    """ Plot the modes derived from a dynamic decomposition of the flow data.
    """
    xs, ys, interp = datum.interpolator()
    abs_velocity = data.velocity[:, ]

    # Plot the results
    if axes is None:
        plt.figure(figsize=(11, 11))
        axes = plt.gca()
    axes.set_aspect('equal')
    axes.contourf(xs, ys, abs_velocity, n_contours,
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
    axes.set_aspect('equal')
