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
from ..flow_data import FlowDatum, FlowData


def read_output_file(output_file):
    """ Read in an output file output by Gerris
    """
    # Read in header
    regex = re.compile('.*:(.*)')
    with open(output_file, 'r') as fhandle:
        header = [regex.findall(k)[0]
                  for k in fhandle.readline().split()[1:]]

        # Read in the rest of the file using pandas
        datum = pandas.read_table(fhandle, sep=' ', names=header)
        datum = FlowDatum(xs=datum['x'], ys=datum['y'],
                          us=datum['U'], vs=datum['V'],
                          pressure=datum['P'], tracer=datum['T'])

        return datum


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
        output_file_template='output_{0}\.dat',
        input_file_template='simulation_{0}\.gfs'
    )

    def __init__(self, vertex_file, **kwargs):
        self.templates = {}
        self.templates.update(self.default_templates)
        self.templates.update(kwargs)

        self.input_file_regex = re.compile(
            self.templates['input_file_template'].format('([\.0-9]*)'))
        self.output_file_regex = re.compile(
            self.templates['output_file_template'].format('[\.0-9]*'))
        self.vertex_file = os.path.abspath(vertex_file)

        self.command_template = (
            'export PKG_CONFIG_PATH='
            + self.templates['pkg_config']
            + ':${{PKG_CONFIG_PATH}}; '
            + self.templates['gerris']
            + ' -e "OutputLocation {{ istep = 1 }} '
            + self.templates['output_file_template'] + ' '
            + self.vertex_file + '" '
            + self.templates['input_file_template'])

    def process_directory(self, directory, output_name=None, update=False):
        """ Process the Gerris output files to get values at given points
        """
        # Get output name
        if output_name is None:
            output_name = os.path.basename(directory)
        if os.path.exists(output_name) and not update:
            data = FlowData(output_name)
            return data
        data = None

        # Get list of files to process
        try:
            current_dir = os.getcwd()
            os.chdir(directory)
            gfsfiles = sorted([f for f in os.listdir(directory)
                               if self.input_file_regex.findall(f)])

            # Loop through files, stash output filenames
            #
            #   TODO:   Parallelize this
            #
            pbar = ProgressBar(len(gfsfiles), 'Processing files')
            output_files = []
            for idx, simfile in enumerate(gfsfiles):
                # First we need to determine what everything will be called
                time_str = self.input_file_regex.findall(simfile)[0]
                output_filename = \
                    self.templates['output_file_template'].format(time_str)
                output_files.append(output_filename)

                # We need to delete the output file first to stop Gerris just
                # appending the data
                output_file = os.path.join(os.getcwd(), output_filename)
                if os.path.exists(output_file):
                    if update:
                        os.remove(output_file)
                    else:
                        # If we're not updating the result, then just skip it
                        pbar.animate(idx + 1)
                        continue

                # Call Gerris to generate the new data files
                command = self.command_template.format(time_str)
                try:
                    subprocess.check_output(command,
                                            shell=True,
                                            stderr=subprocess.STDOUT)
                    pbar.animate(idx + 1)

                except subprocess.CalledProcessError, err:
                    print err.output
                    raise err

            # Generate data objects
            #
            #   TODO:   Parallelize this
            #
            test_datum = read_output_file(output_files[0])
            data = FlowData(filename=output_name,
                            n_snapshots=len(output_files),
                            n_samples=len(test_datum),
                            update=True)
            pbar = ProgressBar(len(gfsfiles), 'Reading files')
            for idx, fname in enumerate(output_files):
                data[idx] = read_output_file(fname)
                pbar.animate(idx + 1)

        except IOError, err:
            print err

        finally:
            os.chdir(current_dir)

        return data
