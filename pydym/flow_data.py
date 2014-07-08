""" file:   flow_data.py (pydym)
    author: Jess Robertson
            CSIRO Minerals Resources Flagship
    date:   Tuesday 24 June 2014

    description: Data structures for velocity fields
"""

from __future__ import division
import numpy
import h5py
import os


class FlowDatum(object):

    """ A class to store velocity data from a flow visualisation
    """

    def __init__(self, xs, ys, us, vs, pressure, tracer):
        super(FlowDatum, self).__init__()
        self.position = numpy.vstack([xs, ys]).transpose()
        self.velocity = numpy.vstack([us, vs]).transpose()
        self.pressure = pressure
        self.tracer = tracer

        self._length = len(us)

    def __len__(self):
        return self._length


class FlowData(object):

    """ A class to store velocity data from a collection of flow visualisations
    """

    default_axis_labels = ('x', 'y', 'z')

    def __init__(self, filename,
                 n_snapshots=None, n_samples=None, n_dimensions=2,
                 vector_datasets=('position', 'velocity'),
                 scalar_datasets=('pressure', 'tracer'),
                 update=False):
        super(FlowData, self).__init__()

        # Set own attributes to be stored as file attributes
        self.shape = (n_snapshots, n_samples)
        self.n_dimensions = n_dimensions
        self.axis_labels = \
            [self.default_axis_labels[i] for i in range(self.n_dimensions)]
        self.vectors, self.scalars = vector_datasets, scalar_datasets

        # Initialize file
        self.filename = filename
        if os.path.exists(filename) and not update:
            self._init_from_file()
        else:
            self._init_from_arguments()

        self._recalc_snapshots = True
        self._snapshots = None

    def _init_from_file(self):
        """ Initialize the FlowData object from an HDF5 resource
        """
        self._file = h5py.File(self.filename, 'a')
        self.shape = self['position/x'].shape
        self.n_dimensions = len(self['position'].keys())
        self.axis_labels = self['position'].keys()
        self.vectors = [n for n, v in self._file.items()
                        if type(v) is h5py.Group]
        self.scalars = [n for n, v in self._file.items()
                        if type(v) is h5py.Dataset]

    def _init_from_arguments(self):
        """ Initialize the FlowData object from the arguments given to __init__
        """
        # Check inputs to __init__ are specced
        if any((s is None for s in self.shape)):
            raise ValueError('You must specify a shape for a new FlowData '
                             'object created from scratch')

        # Create file - ensure any existing files are deleted (which may be the
        # case if update=True in __init__)
        if os.path.exists(self.filename):
            os.remove(self.filename)
        self._file = h5py.File(self.filename, 'w')

        # Map out vector datasets
        for dset_name in self.vectors:
            grp = self._file.create_group(dset_name)
            for dim_idx in range(self.n_dimensions):
                grp.require_dataset(name=self.axis_labels[dim_idx],
                                    shape=self.shape,
                                    dtype=float)

        # Map out scalar datasets
        for dset_name in self.scalars:
            self._file.require_dataset(name=dset_name,
                                       shape=self.shape,
                                       dtype=float)

    def __getitem__(self, value_or_key):
        """ Get the data associated with a given index or key

            If value_or_key is an integer index, return the FlowDatum object
            associated with that snapshot. If value_or_key is a string, return
            the h5py.Dataset object for that string.
        """
        if type(value_or_key) is int:
            # We have an index
            idx = value_or_key

            # Reconstruct FlowDatum
            return FlowDatum(
                xs=self['position/x'][idx], ys=self['position/y'][idx],
                us=self['velocity/x'][idx], vs=self['velocity/y'][idx],
                pressure=self['pressure'][idx],
                tracer=self['tracer'][idx])
        else:
            # We have a key
            return self._file[value_or_key]

    def __setitem__(self, idx, flow_datum):
        """ Set the snapshot data at the given index
        """
        if type(flow_datum) is not FlowDatum:
            raise ValueError("Trying to append non-FlowDatum object to "
                             "FlowData collection")

        # Append vector data in the right places
        for dset in self.vectors:
            values = getattr(flow_datum, dset)
            if values is not None:
                for aidx, axis in enumerate(self.axis_labels):
                    self._file[dset + '/' + axis][idx] = values[:, aidx]

        # Update scalar data
        for dset in self.scalars:
            values = getattr(flow_datum, dset)
            if values is not None:
                self._file[dset][idx] = values

        self._recalc_snapshots = True

    def snapshots(self, snapshot_keys):
        """ Returns the snapshot array for the data
        """
        if self._recalc_snapshots:
            numpy.vstack(
                (datum.velocities for datum in self._data)).transpose()
        return self._snapshow_array
