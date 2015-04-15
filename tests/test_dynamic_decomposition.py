""" file: test_dynamic_decomposition.py
    author: Jess Robertson
            CSIRO Mineral Resources Flagship
    date:   Thursday February 12, 2015

    description: Test for dynamic decomposition
"""

from __future__ import division, print_function

import unittest
import os
import pydym


class TestDynamicDecomposition(unittest.TestCase):

    """ Tests for dynamic decomposition implementation
    """

    def setUp(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        datafile = os.path.join(current_dir, 'resources', 'simulations.hdf5')
        self.data = pydym.Observations(datafile)

    def test_init(self):
        """ Dynamic decomposition should work without errors
        """
        result = pydym.dynamic_decomposition(self.data, burn=0)
        expected_keys = ('eigenvalues', 'eigenvectors', 'amplitudes',
                         'modes', 'intermediate_values')
        for key in expected_keys:
            self.assertTrue(result[key] is not None)

        # Check we have all the expected output
        n_modes = self.data.n_snapshots - 1  # We always lose one snapshot
        self.assertEqual(len(result['eigenvalues']), n_modes)
        self.assertEqual(len(result['amplitudes']), n_modes)
        self.assertEqual(result['eigenvectors'].shape, (n_modes, n_modes))


if __name__ == '__main__':
    unittest.main()
