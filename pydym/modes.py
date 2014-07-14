""" file: modes.py (pydym)
    author: Jess Robertson
            CSIRO Minerals Resources Flagship
    date:   Monday 14 July 2014

    description: Mode data structures
"""

from .flow_data import FlowData


def get_modes(flow_data):
    """ Get the modes from a given FlowData set.

        :returns: a Modes instance with all the modes initialized.
    """
    xxs = data['position/x'][:, mode_idx]
    yys = data['position/y'][:, mode_idx]
    us = U[0::2, mode_idx]
    vs = U[1::2, mode_idx]


class Modes(object):

    def __init__(flow_data):

    def __getitem__(self, idx):
        return self._modes[idx]
