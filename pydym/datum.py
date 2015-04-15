""" file:   datum.py
    author: Jess Robertson
            CSIRO Mineral Resources Flagship
    date:   Thursday 30 October 2014

    description: Class to store some spatially-located data
"""

import numpy

from .utilities import interpolate, AXIS_LABELS


class Datum(object):

    """ A class to store spatially located data
    """

    def __init__(self, position, **datasets):
        self.position = position
        self.n_dimensions = len(position[:, 0])
        for key, value in datasets.items():
            setattr(self, key, value)

    def __len__(self):
        return len(self.position[0])

    def __setitem__(self, key, value):
        setattr(self, key, value)

    def interpolate(self, attribute, axis=None, decimate_by=None):
        """ Return the given attribute interpolated over a regular grid
        """
        # Get the values for the given attribute
        values = getattr(self, attribute)
        if axis is not None:
            values = values[AXIS_LABELS[axis]]

        return interpolate(self.position, values, decimate_by=decimate_by)


def make_velocity_datum(xs, ys, us, vs, **kwargs):
    """ Return a Datum with velocity data
    """
    return Datum(position=numpy.vstack([xs, ys]),
                 velocity=numpy.vstack([us, vs]),
                 **kwargs)
