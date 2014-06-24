""" file:   flow_data.py (pydym)
    author: Jess Robertson
            CSIRO Minerals Resources Flagship
    date:   Tuesday 24 June 2014

    description: Data structures for velocity fields
"""

from __future__ import division
import numpy


class FlowDatum(object):

    """ A class to store velocity data from a flow visualisation
    """

    def __init__(self, xs, ys, us, vs):
        super(FlowDatum, self).__init__()
        self.positions = numpy.asarray([xs, ys]).reshape(len(xs), 2)
        self._velocities = numpy.asarray(numpy.asarray(us)
                                         + 1j * numpy.asarray(vs))

    @property
    def snapshot_vector(self):
        """ Return the stored velocities as a vector of complex numbers
        """
        return self._velocities

    @property
    def velocities(self):
        return numpy.asarray(self._velocities.real, self._velocities.imag)


class FlowData(object):

    """ A class to store velocity data from a collection of flow visualisations
    """

    def __init__(self, *data):
        super(FlowData, self).__init__()
        for datum in data:
            self._data = FlowDatum(*datum)

    @property
    def snapshot_array(self):
        """ Returns the snapshot array for the data
        """
        for datum in self.data:
            datum.velocities
