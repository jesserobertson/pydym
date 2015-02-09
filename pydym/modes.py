""" file: modes.py (pydym)
    author: Jess Robertson
            CSIRO Minerals Resources Flagship
    date:   Monday 14 July 2014

    description: Mode data structures
"""


def get_modes(flow_data, mode_idx):
    """ Get the modes from a given FlowData set.

        :returns: a Modes instance with all the modes initialized.
    """
    xxs = flow_data['position/x'][:, mode_idx]
    yys = flow_data['position/y'][:, mode_idx]
    us = U[0::2, mode_idx]
    vs = U[1::2, mode_idx]
    


class Modes(object):

    def __init__(flow_data):
        pass

    def __getitem__(self, idx):
        return self._modes[idx]
