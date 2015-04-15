#!/usr/bin/env python
""" file: make_hdf5.py
    author: Jess Robertson

    description: Make HDF5 files for running tests
"""

from __future__ import division, print_function

from pydym.io.gerris import GerrisReader
import shutil

from run_parameters import PARAMETERS

def main():
    reader = GerrisReader('vertices.csv')
    flow_data = reader.process_directory('simulations',
                                         update=True,
                                         clean=False,
                                         show_progress=True,
                                         run_parameters=PARAMETERS)
    shutil.move('simulations/simulations.hdf5', 'simulations.hdf5')

if __name__ == '__main__':
    main()
