""" file:   gerris.py (pydym.io)
    author: Jess Robertson
            CSIRO Minerals Resources Flagship
    date:   Tuesday 24 June 2014

    description: Gerris I/O module for pydym
"""

from __future__ import division
import re
import numpy
import pandas
import itertools
import os
import subprocess

from ..utilities import ProgressBar


def read_output_file(output_file):
    """ Read in an output file output by Gerris
    """
    # Read in header
    regex = re.compile('.*:(.*)')
    with open(output_file, 'r') as fhandle:
        header = [regex.findall(k)[0]
                  for k in fhandle.readline().split()[1:]]

        # Read in the rest of the file using pandas
        data = pandas.read_table(fhandle, sep=' ', names=header)

    return data


def boxes_from_gfsfile(gfsfilename):
    """ Read a GFSFile and return the boxes from it
    """
    # Parse the simulation geometry from the gfsfile
    with open(gfsfilename, 'rb') as gfsfile:
        # Return rows which start with two numbers
        boxes = []
        for line in gfsfile:
            # Check we're describing a box
            if not line.startswith('GfsBox'):
                continue

            # Split line into values and keys, generate a dictionary
            line = line.split()[2:]
            line.reverse()
            boxdata = {}
            while len(line) > 2:
                key, _, value = line.pop(), line.pop(), line.pop()
                if key in set(['x', 'y', 'size']):
                    boxdata[key] = float(value)
            boxes.append((boxdata['x'], boxdata['y'], boxdata['size']))
    return numpy.asarray(boxes)


def make_vertex_list(boxes, template=None):
    """ Make a list of vertices given some template, a list of centers and a
        level for those centers
    """
    # Vertex vector function
    if template is None:
        template = numpy.asarray(list(itertools.product([1, -1], [1, -1])),
                                 dtype=int)
    vertex_vectors = lambda level: template / float(2 ** (level + 1))

    # Generate a unique list of vertices
    vertices = numpy.empty((4 * len(boxes), 3), dtype=float)
    for idx, box in enumerate(boxes):
        vertices[(4 * idx):(4 * idx + 4), :2] = \
            vertex_vectors(level=box[2]) + box[:2]
        vertices[(4 * idx):(4 * idx + 4), 2] = box[2] + 1

    # Get unique vertices by voiding the datatype to get unique to treat each
    # row as an object
    temp = numpy.ascontiguousarray(vertices).view(
        numpy.dtype((numpy.void, vertices.dtype.itemsize * vertices.shape[1])))
    _, idx = numpy.unique(temp, return_index=True)
    vertices = vertices[idx]

    # Make sure vertices are sorted
    vertices.view(
        dtype=[('x', numpy.float), ('y', numpy.float), ('level', numpy.float)]
    ).sort(order=['y', 'x', 'level'], axis=0)
    return vertices


def double_resolution(boxes):
    """ Double the sampling resolution in a grid
    """
    double_template = \
        numpy.asarray(list(itertools.product([0.5, -0.5], [0.5, -0.5])))
    return make_vertex_list(boxes, template=double_template)


def in_box(points, left=0, right=1, top=1, bottom=0):
    """ Return the subset of points in the given rectangle
    """
    return reduce(numpy.logical_and,
                  (points[..., 0] > left, points[..., 0] < right,
                   points[..., 1] < top, points[..., 1] > bottom))


class GerrisReader(object):

    """ Class to read and parse Gerris simulation files
    """

    default_templates = dict(
        gerris='/home/jess/gerris/bin/gerris2D',
        pkg_config='/home/jess/gerris/lib/pkgconfig',
        output_file_template='output_{0}.dat',
        input_file_template='simulation_{0}.gfs'
    )

    def __init__(self, vertex_file, **kwargs):
        self.templates = self.default_templates
        self.templates.update(kwargs)
        self.input_file_regex = re.compile('simulation_([\.0-9]*)\.gfs')

        self.command_template = (
            'export PKG_CONFIG_PATH='
            + self.templates['pkg_config']
            + ':${{PKG_CONFIG_PATH}}; '
            + self.templates['gerris']
            + ' -e "OutputLocation {{ istep = 1 }} '
            + self.templates['output_file_template'] + ' '
            + vertex_file + '" '
            + self.templates['input_file_template'])

    def process_directory(self, directory):
        """ Process the Gerris output files to get values at given points
        """
        # Get list of files to process
        gfsfiles = sorted([f for f in os.listdir(directory)
                           if self.input_file_regex.findall(f)])
        pbar = ProgressBar(len(gfsfiles))

        # Loop through files, stash output filenames
        output_files = []
        for idx, simfile in enumerate(gfsfiles):
            pbar.animate(idx)

            # First we need to determine what everything will be called
            time_str = self.input_file_regex.findall(simfile)[0]
            output_filename = 'output_{0}.dat'.format(time_str)
            output_files.append(output_filename)

            # We need to delete the output file first to stop Gerris just
            # appending the data
            output_file = os.path.join(os.getcwd(), output_filename)
            if os.path.exists(output_file):
                os.remove(output_file)

            # Call Gerris to generate the new data files
            command = self.command_template.format(time_str)
            try:
                subprocess.check_output(command,
                                        shell=True,
                                        stderr=subprocess.STDOUT)
            except subprocess.CalledProcessError, err:
                print err.output
                raise err

        return output_files

    def read_directory(self, directory):
        """ Read the output files in a drectory
        """
        pass
