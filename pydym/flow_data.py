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
from itertools import product
import matplotlib.mlab as mlab
from collections import OrderedDict

from .dynamic_decomposition import dynamic_decomposition
from .utilities import thinned_length, herm_transpose

AXIS_LABELS = OrderedDict(zip(('x', 'y', 'z'), range(3)))


class FlowDatum(dict):

    """ A class to store velocity data from a flow visualisation
    """

    def __init__(self, xs, ys, us, vs, **kwargs):
        super(FlowDatum, self).__init__()
        self.__dict__ = self
        self.position = numpy.vstack([xs, ys])
        self.velocity = numpy.vstack([us, vs])
        self.length = len(us)
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __len__(self):
        return self.length

    def interpolate(self, attribute, axis=None):
        """ Return the given attribute interpolated over a regular grid
        """
        # Get the values for the given attribute
        values = getattr(self, attribute)
        if axis is not None:
            values = values[AXIS_LABELS[axis]]

        # Generate a position grid
        xval, yval = self.position[0], self.position[1]
        xlim = xval.min(), xval.max()
        ylim = yval.min(), yval.max()
        nx, ny = map(len, (xval, yval))

        # Generate and return interpolation
        xs, ys = numpy.linspace(*xlim, num=nx), numpy.linspace(*ylim, num=ny)
        zs = mlab.griddata(xval, yval, values, xs, ys, interp='linear')
        return xs, ys, zs


class FlowData(object):

    """ A class to store velocity data from a collection of flow visualisations
    """

    def __init__(self, filename, snapshot_keys=('velocity',),
                 n_snapshots=None, n_samples=None, n_dimensions=2,
                 vector_datasets=('velocity',), scalar_datasets=tuple(),
                 update=False, thin_by=None, run_checks=True):
        super(FlowData, self).__init__()
        self.n_samples, self.n_snapshots = n_samples, n_snapshots
        self.n_dimensions = n_dimensions
        self.filename = filename
        self.run_checks = run_checks
        self.vectors, self.scalars = vector_datasets, scalar_datasets

        # Set up snapshot datasets
        self.snapshot_keys = snapshot_keys
        self.thin_by = thin_by
        self.shape = (self.n_samples, self.n_snapshots)
        self.axis_labels = [AXIS_LABELS.keys()[i]
                            for i in range(self.n_dimensions)]
        self._snapshots = None

        # Initialize file
        self._file = None
        if os.path.exists(filename) and not update:
            self._init_from_file()
        else:
            self._init_from_arguments()

    def _init_from_file(self):
        """ Initialize the FlowData object from an HDF5 resource
        """
        self._file = h5py.File(self.filename)
        self.shape = self['position'].attrs['shape']
        self.n_samples, self.n_snapshots = self.shape
        self.n_dimensions = len(self['position'].keys())
        self.axis_labels = self['position'].keys()
        self.vectors = [n for n, v in self._file.items()
                        if type(v) is h5py.Group
                        and n != 'snapshots']
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

        # Generate positions
        grp = self._file.create_group('position')
        grp.attrs['shape'] = self.shape
        for axis_label in self.axis_labels:
            grp.require_dataset(name=axis_label,
                                shape=(self.n_samples,),
                                dtype=float,
                                compression="gzip")
        self._positions_filled = False

        # Map out other vector datasets
        for dset_name in self.vectors:
            grp = self._file.create_group(dset_name)
            for axis_label in self.axis_labels:
                grp.require_dataset(name=axis_label,
                                    shape=self.shape,
                                    dtype=float,
                                    compression="gzip")

        # Map out scalar datasets
        for dset_name in self.scalars:
            self._file.require_dataset(name=dset_name,
                                       shape=self.shape,
                                       dtype=float,
                                       compression="gzip")

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
            datum = FlowDatum(
                xs=self['position/x'], ys=self['position/y'],
                us=self['velocity/x'][:, idx], vs=self['velocity/y'][:, idx])

            # Add other scalar and vector fields
            remaining_vectors = set(self.vectors) \
                - set(('velocity', 'position'))
            for vector in remaining_vectors:
                vec_data = numpy.empty(
                    shape=(self.n_dimensions,
                           self.n_samples,
                           self.n_snapshots))
                for dim_idx in range(self.n_dimensions):
                    key = vector + '/' + self.axis_labels[dim_idx]
                    vec_data[dim_idx] = self[key][:, idx]
                setattr(datum, vector, vec_data)

            for scalar in self.scalars:
                setattr(datum, scalar, numpy.asarray(self[scalar][:, idx]))

            return datum

        else:
            # We have a key
            return self._file[value_or_key]

    def __iter__(self):
        """ Iterate over the data snapshots
        """
        for idx in xrange(self.n_snapshots):
            yield self[idx]

    def __setitem__(self, idx, flow_datum):
        """ Set the snapshot data at the given index
        """
        if type(flow_datum) is not FlowDatum:
            raise ValueError("Trying to append non-FlowDatum object to "
                             "FlowData collection")

        # If we have no positions yet, get them. Otherwise check that the
        # position data matches
        if not self._positions_filled:
            values = flow_datum.position
            for aidx, axis in enumerate(self.axis_labels):
                self._file['position/' + axis][:] = values[aidx]
            self._positions_filled = True
        elif self.run_checks:
            values = flow_datum.position
            for aidx, axis in enumerate(self.axis_labels):
                if not numpy.allclose(self._file['position/' + axis],
                                      values[aidx]):
                    raise ValueError('Flow datum supplied to FlowData '
                                     'does not have the same position data')

        # Append vector data in the right places
        for dset in self.vectors:
            values = getattr(flow_datum, dset)
            if values is not None:
                for aidx, axis in enumerate(self.axis_labels):
                    self._file[dset + '/' + axis][:, idx] = values[aidx]

        # Update scalar data
        for dset in self.scalars:
            values = getattr(flow_datum, dset)
            if values is not None:
                self._file[dset][:, idx] = values

        self._recalc_snapshots = True

    def __enter__(self):
        """ On with block entry, just initialize self
        """
        return self

    def __exit__(self, type, value, traceback):
        """ Clean up HDF5 references on with block exit
        """
        self.close()

    def close(self):
        """ Close the underlying HDF5 file
        """
        try:
            self._file.close()
        except ValueError:
            # Gets raised when file already closed or doesn't exist
            pass

    def __del__(self):
        self.close()

    def keys(self):
        """ Return an iterator over the available keys
        """
        return self._file.keys()

    def items(self):
        """ Return an iterator over the datasets keys and HDF5 datasets
        """
        return self._file.items()

    def values(self):
        """ Return an iterator over the top-level HDF5 datasets and groups
        """
        return self._file.values()

    @property
    def snapshots(self):
        """ Returns the snapshot array for the data
        """
        if not self._snapshots:
            self.generate_snapshots()
        return self._snapshots

    @property
    def modes(self):
        """ Returns the mode array for the data
        """
        if not self._modes:
            self.generate_modes()
        return self._modes

    def get_spatial_mode(self):
        """ Return the dynamic modes from the given snapshots.

            Uses the currently set snapshot_keys by default
        """
        pass

    def generate_modes(self):
        """ Calculate the dynamic modes from the current shapshot
        """
        S, U, sigma, Vstar = dynamic_decomposition(self, return_svd=True)
        V = herm_transpose(Vstar)
        mode_dict = {
            'operator': S,
            'spatial': U,
            'coeffs': sigma,
            'temporal': V
        }
        mode_grp = self._file.require_group('modes')
        for key, values in mode_dict.items():
            dset = mode_grp.require_dataset(
                name=self.snapshot_dataset_key + '_' + key,
                shape=values.shape,
                dtype=values.dtype)
            dset[...] = values

    def set_snapshot_properties(self, snapshot_keys=None, thin_by=None):
        """ Set the properties used to generate snapshots

            :param snapshot_keys: The datasets used to generate the snapshot
                arrays
            :type snapshot_keys: list of strings
            :param thin_by: Take every 'thin_by' snapshots. `thin_by = None`
                removes thinning.
            :type thin_by: int or None
        """
        if snapshot_keys is not None:
            self.snapshot_keys = snapshot_keys
        if thin_by is not None:
            self.thin_by = thin_by
        self._snapshots = None

    @property
    def snapshot_dataset_key(self):
        """ Return the snapshot datset key for the current snapshot dataset
        """
        # Make snapshot dataset
        key = '_'.join(self.snapshot_keys)
        if self.thin_by:
            key += '_thin_by_{0}'.format(self.thin_by)
        return key

    def generate_snapshots(self):
        """ Generate the snapshots
        """
        # Determine number of measurements per sample - need to include fact
        # that vector snapshots have more samples
        vector_components = [key + '/' + ax
                             for ax, key in product(self.axis_labels,
                                                    self.snapshot_keys)
                             if key in self.vectors]
        scalar_components = [key.replace('/', '_')
                             for key in self.snapshot_keys
                             if key not in self.vectors]
        all_components = tuple(vector_components + scalar_components)
        n_components = len(all_components)

        # Determine snapshot size
        if self.thin_by:
            snapshot_size = (n_components * self.n_samples,
                             thinned_length(self.n_snapshots, self.thin_by))
        else:
            snapshot_size = (n_components * self.n_samples, self.n_snapshots)

        # Generate group for snapshots
        snapshot_grp = self._file.require_group('snapshots')
        if self.snapshot_dataset_key in snapshot_grp.keys():
            del snapshot_grp[self.snapshot_dataset_key]
        self._snapshots = snapshot_grp.require_dataset(
            name=self.snapshot_dataset_key, shape=snapshot_size, dtype=float,
            compression="gzip")
        self._snapshots.attrs['keys'] = ','.join(all_components)

        # Copy over dataset data
        for idx, key in enumerate(all_components):
            if self.thin_by:
                self._snapshots[idx::n_components] = \
                    self[key][:, ::self.thin_by]
            else:
                self._snapshots[idx::n_components] = self[key]


def load(datafile):
    """ Load the given filename into a FlowData instance.

        This is essentially a utility wrapper for use with 'with' statements
        so you can do the following:

            with pydym.load('somefile.hdf5') as data:
                # do something with data

        and have pydym clean up the HDF5 references for you nicely.
    """
    return FlowData(datafile)
