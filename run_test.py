#!/usr/bin/env python
""" file: run_test.py (pydym)
    author: Jess Robertson
            CSIRO Minerals Resources Flagship
    date: January 2015

    description: Run tests
"""

from __future__ import print_function, division

import sys
import unittest
import pydym
import os

from tests.resources.update_resources import main as update_resources

def main():
    """ Run the tests!
    """
    # Print version for logging purposes
    print('pydym version: {0}'.format(pydym.__version__))

    # Update test resources if required
    if not os.path.exists('tests/resources/simulations.hdf5'):
        update_resources()

    # Glom tests together and run them
    suite = unittest.defaultTestLoader.discover('tests')
    result = unittest.TextTestRunner(verbosity=2).run(suite)

    # Check for errors and failures, conda expects script to return 1
    # on failure and 0 otherwise
    nerrors, nfailures = len(result.errors), len(result.failures)
    sys.exit(int(nerrors + nfailures > 0))

if __name__ == '__main__':
    main()
