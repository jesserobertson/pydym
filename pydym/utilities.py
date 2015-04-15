""" file:   utilities.py (pydym)
    author: Jess Robertson
            CSIRO Minerals Resources Flagship
    date:   Tuesday 24 June 2014

    description: Utility functions for pydym
"""

import sys
import numpy
from matplotlib import mlab
from collections import OrderedDict


AXIS_LABELS = OrderedDict(zip(('x', 'y', 'z'), range(3)))


def interpolate(position, values, axis=None, decimate_by=None):
    """ Return the given attribute interpolated over a regular grid
    """
    # Generate a position grid
    xval, yval = position[0], position[1]
    if decimate_by:
        xval, yval = xval[::decimate_by], yval[::decimate_by]
        values = values[::decimate_by]
    xlim = xval.min(), xval.max()
    ylim = yval.min(), yval.max()
    nx, ny = len(xval), len(yval)

    # Generate and return interpolation
    xs, ys = numpy.linspace(*xlim, num=nx), numpy.linspace(*ylim, num=ny)
    zs = mlab.griddata(xval, yval, values, xs, ys, interp='linear')
    return xs, ys, zs


def herm_transpose(array):
    """ Returns the Hermitian transpose of a complex matrix
    """
    return array.conj().transpose()


class ProgressBar:

    """ A progress bar class which will work in Python and IPython

        Stolen from PyMC
    """

    def __init__(self, iterations, label=None):
        self.iterations = iterations
        if label:
            self.label = label + ': '
        else:
            self.label = ''

        self.prog_bar = '[]'
        self.fill_char = '*'
        self.width = 40
        self.__update_amount(0)

    def animate(self, iter):
        print('\r', self, end='')
        sys.stdout.flush()
        self.update_iteration(iter + 1)

    def update_iteration(self, elapsed_iter):
        self.__update_amount((elapsed_iter / float(self.iterations)) * 100.0)
        self.prog_bar += r'  Running'

    def __update_amount(self, new_amount):
        percent_done = int(round((new_amount / 100.0) * 100.0))
        all_full = self.width - 2
        num_hashes = int(round((percent_done / 100.0) * all_full))
        self.prog_bar = (self.label + '[' + self.fill_char * num_hashes + ' '
                         * (all_full - num_hashes) + ']')
        pct_place = ((len(self.prog_bar) // 2) - len(str(percent_done))
                     + len(self.label) // 2)
        pct_string = '%d%%' % percent_done
        self.prog_bar = self.prog_bar[0:pct_place] + \
            (pct_string + self.prog_bar[pct_place + len(pct_string):])

    def __str__(self):
        return str(self.prog_bar)


# Some functional programming bits and bobs
def foldl(func, iterable, accum=None):
    """ A left-fold function, basically identical to reduce

        Left-associative fold, where

            foldl(lambda a, b: a - b, [1, 2, 3, 4])  # returns -8

        is the same as

            (((1 - 2) - 3) - 4)

        :param func: The function to apply to the fold. Should take two
            arguments and return a single object.
        :type func: callable
        :param iterable: The iterable to accumulate over.
        :type iterable: iterable
        :param accum: The initial value for the accumulator. If None, the
            initial value is set to the first object in the sequence.
    """
    if accum is None:
        return foldl(func, iterable[1:], iterable[0])
    elif len(iterable) == 0:
        return accum
    else:
        return foldl(func, iterable[1:],
                     func(accum, iterable[0]))


def foldr(func, iterable, accum=None):
    """ A right-fold function

        Right-associative fold, where

            foldr(lambda a, b: a - b, [1, 2, 3, 4])  # returns -2

        is the same as

            (1 - (2 - (3 - 4)))

        :param func: The function to apply to the fold. Should take two
            arguments and return a single object.
        :type func: callable
        :param iterable: The iterable to accumulate over.
        :type iterable: iterable
        :param accum: The initial value for the accumulator. If None, the
            initial value is set to the last object in the sequence.
    """
    # Reverse the iterable, only needs doing once
    iterable = iterable[::-1]
    if accum is None:
        accum, iterable = iterable[0], iterable[1:]

    # Make a dummy foldr function to apply things in the right order
    def _foldr(func, iterable, accum):
        if len(iterable) == 0:
            return accum
        else:
            return _foldr(func, iterable[1:],
                          func(iterable[0], accum))
    return _foldr(func, iterable, accum)


def thinned_length(length, thin_by):
    """ Returns the length of a sequence thinned by taking every `thin_by`th
        element

        :param length: The original sequence length
        :type length: int
        :param thin_by: The stride length
        :type thin_by: int
    """
    thin_by = abs(thin_by)  # Remove negative stride if necessary
    if not(length % thin_by):
        return length // thin_by
    else:
        return length // thin_by + 1
