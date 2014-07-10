""" file:   __init__.py (pydym tests)
    author: Jess Robertson
            CSIRO Minerals Resources Flagship
    date:   Thursday, 24 June 2014

    description: Imports for test suites
"""

from test_flow_data import *
from test_gerris import *
from test_utilities import *

print [k for k in sys.modules[__name__].__dict__.keys()
       if k.startswith('Test')]
