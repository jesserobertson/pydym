#!/usr/bin/env python
""" file: make_hdf5.py
    author: Jess Robertson

    description: Make HDF5 files for running tests
"""

from pydym.io.gerris import GerrisReader
import shutil

def main():
    reader = GerrisReader('vertices.csv')
    flow_data = reader.process_directory('simulations',
                                         update=True,
                                         clean=False)
    shutil.move('simulations/simulations.hdf5', 'simulations.hdf5')

if __name__ == '__main__':
    main()
