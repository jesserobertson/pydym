""" file:   __init__.py (pydym tests)
    author: Jess Robertson
            CSIRO Minerals Resources Flagship
    date:   Thursday, 24 June 2014

    description: Unit tests for flow data objects
"""

from __future__ import division, print_function

import unittest
import os
import subprocess
import numpy

from pydym import FlowData


# location of test data files
TEST_DATA_DIR = os.path.join(os.path.dirname(__file__), "resources")


class FlowDataTest(unittest.TestCase):

    """ Unit tests for flow data
    """

    def setUp(self):
        self.test_datafile = os.path.join(TEST_DATA_DIR, 'simulations.hdf5')
        self.data = FlowData(self.test_datafile)

    def test_read_from_hdf5(self):
        """ FlowData should initialize ok from hdf5
        """
        expected_keys = set(('velocity', 'position', 'pressure', 'tracer',
                             'snapshots', 'properties'))
        self.assertIsNone(self.data.thin_by)
        self.assertIsNotNone(self.data.snapshots)
        for key in expected_keys:
            self.assertIsNotNone(self.data[key])

    def test_get_snapshots(self):
        """ Snapshot calculations should work with defaults
        """
        default_snapshot = 'velocity'
        self.assertIsNotNone(self.data.snapshots)
        self.assertIsNotNone(self.data['snapshots/' + default_snapshot])

    def test_change_snapshots(self):
        """ Check that we can change snapshots back and forth
        """
        old_snapshot = self.data.snapshots
        self.data.set_snapshot_properties(
            snapshot_keys=['pressure', 'velocity'])
        self.assertIsNotNone(self.data.snapshots)
        self.assertIsNotNone(self.data['snapshots/pressure_velocity'])
        self.data.set_snapshot_properties(snapshot_keys=['velocity'])
        self.assertIsNotNone(self.data.snapshots)
        self.assertIsNotNone(self.data['snapshots/velocity'])
        self.assertIsNotNone(numpy.allclose(self.data.snapshots, old_snapshot))

    def test_get_item(self):
        """ Check that we can return simulation stuff
        """
        for attr in ('velocity', 'position', 'pressure', 'tracer'):
            self.assertIsNotNone(self.data[attr])

    def tearDown(self):
        # Close references to HDF5 file
        self.data.close()
