""" file:   __init__.py (pydym tests)
    author: Jess Robertson
            CSIRO Minerals Resources Flagship
    date:   Thursday, 24 June 2014

    description: Unit tests for flow data objects
"""

import unittest
import os

from pydym import FlowData


# location of test data files
TEST_DATA_DIR = os.path.join(os.path.dirname(__file__), "resources")


class FlowDataTest(unittest.TestCase):

    """ Unit tests for flow data
    """

    def setUp(self):
        self.test_datafile = os.path.join(TEST_DATA_DIR, 'test_data.hdf5')
        self.data = FlowData(self.test_datafile)

    def test_read_from_hdf5(self):
        """ FlowData should initialize ok from hdf5
        """
        expected_keys = set(('velocity', 'position', 'pressure', 'tracer',
                             'snapshots'))
        for key in self.data.keys():
            self.assertTrue(key in expected_keys)
            self.assertIsNotNone(self.data[key])

    def test_get_snapshots(self):
        """ Snapshot calculations should work with defaults
        """
        default_snapshot = 'velocity'
        self.assertIsNotNone(self.data.snapshots)
        self.assertIsNotNone(self.data['snapshots/' + default_snapshot])

    def test_get_item(self):
        """ Check that we can return simulation stuff
        """
        for idx in xrange(self.data.n_snapshots):
            self.assertIsNotNone(self.data[idx])

    def tearDown(self):
        self.data.close()
