""" file:   __init__.py (pydym tests)
    author: Jess Robertson
            CSIRO Minerals Resources Flagship
    date:   Thursday, 24 June 2014

    description: Imports for test suites
"""

import sys

from test_flow_data import *
from test_gerris import *
from test_utilities import *

__all__ = [k for k in sys.modules[__name__].__dict__.keys()
           if k.startswith('Test')]
