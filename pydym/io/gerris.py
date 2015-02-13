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

        # Find Gerris on this system
        self.templates['gerris'] = \
            subprocess.check_output('which gerris2D', shell=True)
        self.templates['gerris'] = self.templates['gerris'].strip('\n')
        self.templates.update(kwargs)

        # Generate regexes for simulation files and output files
        self.input_file_regex = re.compile(
            self.templates['input_file_template'].format('([\.0-9]*)'))
        self.templates['input_file_template'] = \
            self.templates['input_file_template'].replace('\\', '')
        self.output_file_regex = re.compile(
            self.templates['output_file_template'].format('[\.0-9]*'))
        self.templates['output_file_template'] = \
            self.templates['output_file_template'].replace('\\', '')
        self.vertex_file = os.path.abspath(vertex_file)

    def process_directory(self, directory, output_name=None,
                          update=False, clean=False, show_progress=True):
        """ Process the Gerris output files to get values at given points

            :param directory: The directory to process
            :type directory: string
            :param output_name: The name for the output HDF5 file. Optional, if
                not specified it defaults to <directory>/<directory>.hdf5
            :type output_name: string
            :param update: Whether to update the files if they already exist.
                If the directory already has an HDF5 file with the given
                output_name and update is False, then this file is just loaded,
                rather than reprocessing the data. Optional, defaults to False.
            :type update: bool
            :param clean: If True, remove temporary data files after they've
                been added to the HDF5 file. Optional, defaults to False.
            :type clean: bool
            :param show_progress: If True, prints a progress bar. Optional,
                defaults to True
            :type show_progress: bool
        """
        # Get output name
        if output_name is None:
            root = os.path.abspath(directory)
            name = os.path.basename(root)
            output_name = os.path.join(root, name + '.hdf5')
            print 'Saving to file {0}'.format(output_name)

        # Set Gerris command string
        self.command_template = (
            self.templates['gerris']
            + ' -e "OutputLocation {{ istep = 1 }} '
            + os.path.abspath(directory) + '/'
            + self.templates['output_file_template'] + ' '
            + self.vertex_file + '" '
            + os.path.abspath(directory) + '/'
            + self.templates['input_file_template'])

        # Get list of files to process
        try:
            current_dir = os.getcwd()
            os.chdir(directory)
            # If the data already exists, then just load it
            if os.path.exists(output_name) and not update:
                print 'Found existing file, loading'
                data = FlowData(filename=output_name, run_checks=False)

            else:
                data = None
                gfsfiles = sorted([f for f in os.listdir('.')
                                   if self.input_file_regex.findall(f)])
                if show_progress:
                    pbar = ProgressBar(len(gfsfiles), 'Processing files')

                for idx, simfile in enumerate(gfsfiles):
                    # First we need to determine what everything will be called
                    time_str = self.input_file_regex.findall(simfile)[0]
                    output_filename = \
                        self.templates['output_file_template'].format(
                            time_str, os.path.dirname(simfile))
                    output_filename = os.path.join(
                        os.path.abspath(os.getcwd()),
                        output_filename)

                    # If we're updating, we need to remove any existing output
                    # or Gerris will just append the new data to the file
                    if os.path.exists(output_filename) and update:
                        os.remove(output_filename)

                    # Call Gerris to generate the new data files
                    if not os.path.exists(output_filename):
                        try:
                            subprocess.check_output(
                                self.command_template.format(time_str),
                                shell=True,
                                stderr=subprocess.STDOUT)
                        except subprocess.CalledProcessError, err:
                            print err.output
                            raise err

                    # Generate data objects
                    if not data:
                        datum = read_output_file(output_filename)
                        data = FlowData(filename=output_name,
                                        n_snapshots=len(gfsfiles),
                                        n_samples=len(datum),
                                        update=True)
                        data[0] = datum

                    else:
                        data[idx] = read_output_file(output_filename)

                    # Clean up if required
                    if clean:
                        os.remove(output_filename)
                    if show_progress:
                        pbar.animate(idx + 1)

                print 'File saved to {0}'.format(output_name)

        except IOError, err:
            print err

        finally:
            os.chdir(current_dir)

        return data
