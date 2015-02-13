#!/usr/bin/env python
""" file: update_test_data.py
    author: Jess Robertson
            CSIRO Mineral Resources Flagship
    date:   Thursday February 12, 2015

    description: Updates the test HDF5 dataset using the provided gerris output
"""

from pydym.io.gerris import GerrisReader
import os
import shutil

def main():
    data_dir = '.'
    simulation_dir = 'gerris_simulations'
    vertex_file = 'vertices.csv'

    # Process data, copy file to data directory
    reader = GerrisReader(os.path.join(data_dir, vertex_file))
    reader.process_directory(os.path.join(data_dir, simulation_dir),
                             update=True)
    shutil.copyfile(os.path.join(data_dir, simulation_dir,
                                 simulation_dir + '.hdf5'),
                    os.path.join(data_dir,
                                 simulation_dir + '.hdf5'))

if __name__ == '__main__':
    main()
