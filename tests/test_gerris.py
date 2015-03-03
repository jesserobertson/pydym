""" file:   __init__.py (pydym tests)
    author: Jess Robertson
            CSIRO Minerals Resources Flagship
    date:   Thursday, 24 June 2014

    description: Unit tests for reading Gerris simulations
"""

import unittest
import os
import subprocess
import numpy

import pydym

# location of test data files
LOCAL = os.path.abspath(os.path.dirname(__file__))
TEST_DATA_DIR = os.path.join(LOCAL, "resources")
GERRIS_DATA_DIR = os.path.join(TEST_DATA_DIR, "gerris_simulations")

class GerrisTest(unittest.TestCase):

    """ Unit tests for flow data
    """

    def setUp(self):
        self.reader = pydym.io.gerris.GerrisReader(
            vertex_file=os.path.join(TEST_DATA_DIR, 'vertices.csv'))

    def test_reader(self):
        """ Reader should initialize OK
        """
        self.assertEqual(
            self.reader.templates['gerris'],
            subprocess.check_output('which gerris2D', shell=True).strip('\n'))
        self.assertIsNotNone(self.reader.templates)

    def test_process_directory(self):
        """ Processing a directory of Gerris simulations should work
        """
        # Load up expected data
        dfile = os.path.join(TEST_DATA_DIR,
                             '{0}.hdf5'.format(os.path.basename(
                                                GERRIS_DATA_DIR)))
        expected_data = pydym.FlowData(dfile)
        import pdb; pdb.set_trace()

        try:
            datafile = self.reader.process_directory(GERRIS_DATA_DIR,
                                                     update=True)
            with pydym.load(datafile) as data:
                for key in data.keys():
                    self.assertTrue(key in self.expected_data.keys())
                    self.assertIsNotNone(data[key])
            self.assertTrue(os.path.exists(data.filename))
            data.close()

        finally:
            filename = os.path.join(GERRIS_DATA_DIR, GERRIS_DATA_DIR + '.hdf5')
            if os.path.exists(filename):
                os.remove(filename)
            self.assertFalse(os.path.exists(filename))

    def test_make_vertex_file(self):
        """ Test that we can make a vertex file OK
        """
        expected_vertices = numpy.loadtxt(
            os.path.join(TEST_DATA_DIR, 'vertices.csv'),
            delimiter=' ')

        # Make vertices from base file
        gfsfile = os.path.join(GERRIS_DATA_DIR, 'chaos-1.0.64.10.gfs')
        boxes = pydym.io.gerris.boxes_from_gfsfile(gfsfile)
        boxes[..., 2] = 1

        # Increase resolution of boxes
        for _ in range(4):
            boxes = pydym.io.gerris.double_resolution(boxes)

        # Mask out a subset of those boxes
        mask = pydym.io.gerris.in_box(
            boxes, top=0.75, bottom=-0.5, left=-0.6, right=1.6)
        subset = boxes[mask]
        subset[..., 2] = 0  # Store a z value of 0
        self.assertTrue(numpy.allclose(subset, expected_vertices))


if __name__ == '__main__':
    unittest.main()
