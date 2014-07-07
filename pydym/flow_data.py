""" file:   flow_data.py (pydym)
    author: Jess Robertson
            CSIRO Minerals Resources Flagship
    date:   Tuesday 24 June 2014

    description: Data structures for velocity fields
"""

from __future__ import division
import numpy
import h5py


class FlowDatum(object):

    """ A class to store velocity data from a flow visualisation
    """

    def __init__(self, xs, ys, us, vs, pressure=None, tracer=None):
        super(FlowDatum, self).__init__()
        self.positions = numpy.vstack([xs, ys]).transpose()
        self._velocities = numpy.asarray(numpy.asarray(us)
                                         + 1j * numpy.asarray(vs))
        self.pressure = pressure
        self.tracer = tracer

        self._length = len(us)

    def __len__(self):
        return self._length

    @property
    def snapshot(self):
        """ Return the stored velocities as a vector of complex numbers
        """
        return self._velocities

    @property
    def velocities(self):
        return numpy.asarray([self._velocities.real, self._velocities.imag])


class FlowData(object):

    """ A class to store velocity data from a collection of flow visualisations
    """

    def __init__(self):
        super(FlowData, self).__init__()
        self._data = []
        self._recalc_snapshots = True
        self._snapshot_array = None

    def __iter__(self):
        return (d for d in self._data)

    def __len__(self):
        return len(self._data)

    def __getitem__(self, idx):
        return self._data[idx]

    def __setitem__(self, idx, value):
        """ Set the value at the given index
        """
        if type(value) is not FlowDatum:
            raise ValueError("Trying to append non-FlowDatum object to "
                             "FlowData collection")
        else:
            self._data[idx] = value
            self._recalc_snapshots = True

    @property
    def snapshots(self):
        """ Returns the snapshot array for the data
        """
        if self._recalc_snapshots:
            numpy.vstack(
                (datum.velocities for datum in self._data)).transpose()
        return self._snapshow_array

    def append(self, *data):
        """ Append the data to the collection
        """
        self._data.extend(data)
        self._recalc_snapshots = True
