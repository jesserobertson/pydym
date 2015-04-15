#!/usr/bin/env python
""" file: make_hdf5.py
    author: Jess Robertson

    description: Make HDF5 files for running tests
"""

from __future__ import division, print_function

from pydym.io.gerris import GerrisReader
import shutil
import os

# Run parameters for the test data
PARAMETERS = {
    'cavity_aspect':           1,
    'density_ratio':           1,
    'end_time':                300.0,
    'gerris':                  'gerris2D',
    'gfsfile':                 '/media/rayleigh/chaos_runs/chaos.gfs',
    'num_cycles':              30,
    'num_processors':          8,
    'num_split':               2,
    'reynolds_number':         64,
    'run_name':                'chaos-1.0.64.10',
    'simulation_output_times': 0.5,
    'strouhal_number':         0.1,
    'viscosity_ratio':         1
}

# location of test data files
TEST_DATA_DIR = os.path.join(os.path.dirname(__file__))

def main():
    vertex_file = os.path.join(TEST_DATA_DIR, 'vertices.csv')
    reader = GerrisReader(vertex_file)

    flow_data = reader.process_directory(
        os.path.join(TEST_DATA_DIR, 'simulations'),
        update=True,
        clean=True,
        show_progress=True,
        run_parameters=PARAMETERS)
    shutil.move(os.path.join(TEST_DATA_DIR, 'simulations/simulations.hdf5'),
                os.path.join(TEST_DATA_DIR, 'simulations.hdf5'))

if __name__ == '__main__':
    main()
