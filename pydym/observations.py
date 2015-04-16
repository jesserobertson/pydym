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
from collections import OrderedDict

from .snapshot import Snapshot
from .dynamic_decomposition import dynamic_decomposition
from .utilities import thinned_length

AXIS_LABELS = OrderedDict(zip(('x', 'y', 'z'), range(3)))


class Observations(object):

    """ A class to store velocity data from a collection of flow visualisations
    """

    def __init__(self, filename, key_on=('velocity',),
                 n_snapshots=None, n_samples=None, n_dimensions=2,
                 vector_datasets=('velocity',), scalar_datasets=tuple(),
                 update=False, thin_by=None, run_checks=True,
                 snapshot_interval=1, properties=None):
        super(Observations, self).__init__()
        self.n_samples, self.n_snapshots = n_samples, n_snapshots
        self.n_dimensions = n_dimensions
        self.snapshot_interval = snapshot_interval
        self.filename = os.path.abspath(filename)
        self.run_checks = run_checks
        self.vectors, self.scalars = vector_datasets, scalar_datasets
        self.properties = properties

        # Set up snapshot datasets
        self.key_on = key_on
        self.thin_by = thin_by
        self.shape = (self.n_samples, self.n_snapshots)
        self.axis_labels = list(AXIS_LABELS.keys())[:self.n_dimensions]
        self._snapshots = None
        self._modes = None
        self._recalc_snapshots, self._positions_filled = None, None

        # Initialize HDF5 backend file
        self._file = None
        if os.path.exists(filename) and not update:
            self._init_from_file()
        elif filename and self.n_samples is None:
            # We obviously wanted a file but it can't be found
            raise IOError("Can't find {0}".format(filename))
        else:
            self._init_from_arguments()

    def _init_from_file(self):
        """ Initialize the FlowData object from an HDF5 resource
        """
        self._file = h5py.File(self.filename, 'a')
        self.properties = self['properties']
        for attr in ('shape', 'n_samples', 'n_snapshots', 'snapshot_interval'):
            setattr(self, attr, self.properties[attr][()])
        self.n_dimensions = len(self['position'])
        self.axis_labels = tuple(self['position'].keys())
        self.vectors = [n for n, v in self._file.items()
                        if isinstance(v, h5py.Group)
                        and n not in ('snapshots', 'properties')]
        self.scalars = [n for n, v in self._file.items()
                        if isinstance(v, h5py.Dataset)]

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

        # Add properties to file
        grp = self._file.create_group('properties')
        attrs_to_add = ('shape', 'n_samples', 'n_snapshots',
                        'n_dimensions', 'snapshot_interval')
        for attr in attrs_to_add:
            grp[attr] = getattr(self, attr)

        # Copy over existing properties, assign properties attrib to group
        if self.properties is not None:
            for key, value in self.properties.items():
                grp[key] = value
        self.properties = grp

    def __getitem__(self, value_or_key):
        """ Get the data associated with a given index or key

            If value_or_key is an integer index, return the Snapshot object
            associated with that snapshot. If value_or_key is a string, return
            the h5py.Dataset object for that string.
        """
        if isinstance(value_or_key, int):
            return self.get_snapshot(value_or_key)
        else:
            try:
                return self._file[value_or_key]
            except KeyError:
                raise KeyError("Can't find item {0}".format(value_or_key))

    def __setitem__(self, index, value):
        """ Set the data associated with an index
        """
        self.set_snapshot(index, value)

    def __iter__(self):
        """ Iterate over the data snapshots
        """
        for idx in range(self.n_snapshots):
            yield self.get_snapshot(idx)

    def __enter__(self):
        """ On with block entry, just initialize self
        """
        return self

    def __exit__(self, *args):
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
        if self._snapshots is None:
            self.generate_snapshots()
        return self._snapshots

    @property
    def modes(self):
        """ Returns the mode array for the data
        """
        if self._modes is None:
            self.generate_modes()
        return self._modes

    def get_snapshot(self, index):
        """ Get the snapshot associated with the given index
        """
        # Reconstruct Snapshot
        snapshot = Snapshot(
            position=numpy.vstack([self['position/x'],
                                   self['position/y']]))

        # Add other scalar and vector fields
        remaining_vectors = [v for v in self.vectors
                             if v != 'position']
        for vector in remaining_vectors:
            vec_data = numpy.empty(
                shape=(self.n_dimensions,
                       self.n_samples,
                       self.n_snapshots))
            for dim_index in range(self.n_dimensions):
                key = vector + '/' + self.axis_labels[dim_index]
                vec_data[dim_index] = self[key][:, index]
            setattr(snapshot, vector, vec_data)

        for scalar in self.scalars:
            setattr(snapshot, scalar, numpy.asarray(self[scalar][:, index]))

        # Add properties
        setattr(snapshot, 'properties', {})
        for key, value in self['properties'].items():
            snapshot.properties[key] = value[()]

        return snapshot

    def set_snapshot(self, idx, snapshot):
        """ Set the snapshot data at the given index
        """
        if not isinstance(snapshot, Snapshot):
            raise ValueError("Trying to append non-Snapshot object to "
                             "Observations collection")

        # If we have no positions yet, get them. Otherwise check that the
        # position data matches
        if not self._positions_filled:
            values = snapshot.position
            for aidx, axis in enumerate(self.axis_labels):
                self._file['position/' + axis][:] = values[aidx]
            self._positions_filled = True
        elif self.run_checks:
            values = snapshot.position
            for aidx, axis in enumerate(self.axis_labels):
                if not numpy.allclose(self._file['position/' + axis],
                                      values[aidx]):
                    raise ValueError('Snapshot supplied to Observations '
                                     'does not have the same position data')

        # Append vector data in the right places
        for dset in self.vectors:
            values = getattr(snapshot, dset)
            if values is not None:
                for aidx, axis in enumerate(self.axis_labels):
                    self._file[dset + '/' + axis][:, idx] = values[aidx]

        # Update scalar data
        for dset in self.scalars:
            values = getattr(snapshot, dset)
            if values is not None:
                self._file[dset][:, idx] = values

        self._recalc_snapshots = True

    def generate_modes(self):
        """ Calculate the dynamic modes from the current shapshot
        """
        # Generate the dynamic decomposition
        results = dynamic_decomposition(self)

        # Add regular dynamic mode info
        self._modes = mode_grp = self._file.require_group('modes')
        items = {
            'eigenvalues': results.eigenvalues,
            'eigenvectors': results.eigenvectors,
            'modes': results.modes,
            'amplitudes': results.amplitudes
        }
        for key, values in items:
            dset = mode_grp.require_dataset(
                name=self.snapshot_dataset_key + '_' + key,
                shape=values.shape,
                dtype=values.dtype)
            dset[...] = values

        # Add POD modes (from SVD) to data
        pod_data = zip(results.pod_modes,
                       ('spatial', 'pod_coeffs', 'temporal'))
        for values, name in pod_data:
            dset = mode_grp.require_dataset(
                name=self.snapshot_dataset_key + '_' + name,
                shape=values.shape,
                dtype=values.dtype)
            dset[...] = values

    def set_snapshot_properties(self, key_on=None, thin_by=None):
        """ Set the properties used to generate snapshots

            :param key_on: The datasets used to generate the snapshot
                arrays
            :type key_on: list of strings
            :param thin_by: Take every 'thin_by' snapshots. `thin_by = None`
                removes thinning.
            :type thin_by: int or None
        """
        if key_on is not None:
            self.key_on = key_on
        if thin_by is not None:
            self.thin_by = thin_by
        self._snapshots = None

    @property
    def snapshot_dataset_key(self):
        """ Return the snapshot datset key for the current snapshot dataset
        """
        # Make snapshot dataset
        key = '_'.join(self.key_on)
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
                                                    self.key_on)
                             if key in self.vectors]
        scalar_components = [key.replace('/', '_')
                             for key in self.key_on
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
        if self.snapshot_dataset_key in set(snapshot_grp.keys()):
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
    return Observations(datafile)
