##############################################################################
#  The Combustion Flame Engine - pyflam3ng
#  http://combustion.sourceforge.net
#  http://github.com/bobbyrward/pyflam3ng/tree/master
#
#  Copyright (C) 2007-2008 by Bobby R. Ward <bobbyrward@gmail.com>
#
#  The Combustion Flame Engine is free software; you can redistribute
#  it and/or modify it under the terms of the GNU General Public
#  License as published by the Free Software Foundation; either
#  version 3 of the License, or (at your option) any later version.
#
#  This library is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#  Library General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this library; see the file COPYING.LIB.  If not, write to
#  the Free Software Foundation, Inc., 59 Temple Place - Suite 330,
#  Boston, MA 02111-1307, USA.
##############################################################################
import itertools
from collections import defaultdict

from lxml import etree
import numpy

from . import flam3
from . import util

def load_flame(xml_source=None, fd=None, filename=None):
    """Load a set of genomes from an xml document

    If filename is specified:
        Loads the genomes from the file

    If fd is specified:
        Loads the genomes from the filelike object

    If xml_source is specified:
        Loads the genomes directly from the string

    Parameters are tested in this order
    """
    if filename is not None:
        fd = open(filename)

    try:
        if fd is not None:
            xml_source = fd.read()
    finally:
        if filename is not None:
            fd.close()

    tree = etree.fromstring(xml_source)
    genome_nodes = tree.xpath('//flame')

    return [load_genome(flame_node=node) for node in genome_nodes]


def load_genome(flame_node=None, xml_source=None, genome_handle=None):
    """Load a genome from a variety of sources

    If xml_source is specified:
        Loads the genome directly from the string

    If flame_node is speficied:
        Loads the genome from the lxml.etree.Element

    If gnome_handle is specified:
        Loads the genomes from the pyflam3ng.flam3.GenomeHandle

    If none are specified, returns None

    Parameters are tested in this order
    """
    if xml_source:
        flame_node = etree.fromstring(xml_source).xpath('//flame')[0]

    if flame_node is not None:
        return Genome(flame_node=flame_node)
    elif genome_handle is not None:
        return Genome(genome_handle=genome_handle)
    else:
        return None


class Point(object):
    """A 2d point in cartesian space"""

    def __init__(self, x=0.0, y=0.0):
        self.x = x
        self.y = y

    def __iter__(self):
        yield self.x
        yield self.y

    def __repr__(self):
        return '<Point x=%f y=%f>' % (self.x, self.y)


class Variations(object):
    """Wraps the variations in use by an XForm"""

    def __init__(self):
        self.values = {}
        self.variables = {
            'blob': {
                'low': 0.0,
                'high': 1.0,
                'waves': 1.0,
            },
            'pdj': {
                'a': 0.0,
                'b': 0.0,
                'c': 0.0,
                'd': 0.0,
            },
            'fan2': {
                'x': 0.0,
                'y': 1.0,
            },
            'rings2': {
                'val': 0.0,
            },
            'perspective': {
                'angle': 0.0,
                'dist': 0.0,
            },
            'julian': {
                'power': 1.0,
                'dist': 1.0,
            },
            'juliascope': {
                'power': 1.0,
                'dist': 1.0,
            },
            'radialblur': {
                'angle': 0.0,
            },
            'pie': {
                'slices': 6.0,
                'rotation': 0.0,
                'thickness': 0.5,
            },
            'ngon': {
                'sides': 5.0,
                'power': 3.0,
                'circle': 1.0,
                'corners': 2.0,
            },
            'curl': {
                'c1': 1.0,
                'c2': 0.0,
            },
            'rectangles': {
                'x': 1.0,
                'y': 1.0,
            },
            'disc2': {
                'rot': 0.0,
                'twist': 0.0,
            },
            'supershape': {
                'rnd': 0.0,
                'm': 0.0,
                'n1': 1.0,
                'n2': 1.0,
                'n3': 1.0,
                'holes': 0.0,
            },
            'flower': {
                'petals': 0.0,
                'holes': 0.0,
            },
            'conic': {
                'eccentricity': 1.0,
                'holes': 0.0,
            },
            'parabola': {
                'height': 0.0,
                'width': 0.0,
            },
        }

    def __getitem__(self, key):
        return self.values[key]

    def __setitem__(self, key, value):
        self.values[key] = value

    def __delitem__(self, key):
        del self.values[key]

    def variation_vars(self, variation_name=None):
        if variation_name in self.variables:
            return self.variables[variation_name]
        else:
            return dict()

    def set_variable(self, variation_name, variable_name, value):
        if variation_name in self.variables:
            vars = self.variables[variation_name]

            if variable_name in vars:
                vars[variable_name] = value
            else:
                raise KeyError('Unknown variable')
        else:
            raise KeyError('Unknown variation')

    def get_variable(self, variation_name, variable_name, value):
        if variation_name in self.variables:
            vars = self.variables[variation_name]

            if variable_name in vars:
                return vars[variable_name]
            else:
                raise KeyError('Unknown variable')
        else:
            raise KeyError('Unknown variation')


class Palette(object):
    def __init__(self):
        self.array = numpy.zeros((256,3), numpy.uint8)

    def smooth(self, ntries=50, trysize=10000):
        self.array = util.palette_improve()


class Genome(object):
    def __init__(self, flame_node=None, genome_handle=None):
        self.set_defaults()

        if flame_node is not None:
            self._init_from_node(flame_node)
        elif genome_handle is not None:
            self._init_from_handle(genome_handle)

    def set_defaults(self):
        self.time = 0.0

        self.palette_index = flam3.flam3_palette_random

        self.center = numpy.zeros(1, [('x', numpy.float32), ('y', numpy.float32)])

        self.gamma = 4.0
        self.vibrancy = 1.0
        self.contrast = 1.0
        self.brightness = 4.0

        self.symmetry = 0

        self.hue_rotation = 0.0
        self.rotate = 0.0

        self.pixels_per_unit = 50
        self.interpolation = flam3.flam3_interpolation_linear
        self.palette_interpolation = flam3.flam3_palette_interpolation_hsv

        self.highlight_power = -1.0

        self.background = numpy.zeros(1, [('r', numpy.uint8), ('g', numpy.uint8), ('b', numpy.uint8)])

        self.width = 100
        self.height = 100

        self.spatial_oversample = 1
        self.spatial_filter_radius = 0.5

        self.zoom = 0.0

        self.sample_density = 1

        self.estimator = 9.0
        self.estimator_minimum = 0.0
        self.estimator_curve = 0.4

        self.gam_lin_thresh = 0.01

        self.nbatches = 1

        self.ntemporal_samples = 1000

        self.spatial_filter_select = flam3.flam3_gaussian_kernel

        self.interpolation_type = flam3.flam3_inttype_log

        self.temporal_filter_type = flam3.flam3_temporal_box
        self.temporal_filter_width = 1.0
        self.temporal_filter_exp = 0.0

        self.palette_mode = flam3.flam3_palette_mode_step


    def _init_from_node(self, flame_node):
        self.flame_node = flame_node
        self._refresh_handle_from_self()
        self._refresh_self_from_handle()

    def _init_from_handle(self, genome_handle):
        self.genome_handle = genome_handle
        self._refresh_self_from_handle()

    def _refresh_handle_from_self(self):
        self.genome_handle = flam3.from_xml(etree.tostring(self.flame_node))[0]

    def _refresh_self_from_handle(self):
        xml_source = flam3.to_xml(self.genome_handle)
        self.flame_node = etree.fromstring(xml_source)
        attrib = self.flame_node.attrib

        def scalar_attrib(src_name, dest_name=None, coerce_type=float, node=self.flame_node):
            if src_name in node.attrib:
                setattr(self, dest_name if dest_name else src_name,
                        coerce_type(node.attrib[src_name]))

        def whitespace_array(src_name, coerce_type=float, node=self.flame_node):
            return map(coerce_type, node.attrib.get(src_name).split(' '))

        def mapped_attrib(src_name, dest_name=None, mapping={}, node=self.flame_node):
            if src_name in node.attrib:
                setattr(self, dest_name if dest_name else src_name,
                        mapping[node.attrib[src_name]])

        self.width, self.height = whitespace_array('size', int)

        self.center.fill(buffer(numpy.array(whitespace_array('center'))))
        self.background.fill(buffer(numpy.array(whitespace_array('background'))))

        scalar_attrib('time')
        scalar_attrib('scale', 'pixels_per_unit')
        scalar_attrib('zoom')
        scalar_attrib('rotate')
        scalar_attrib('filter', 'spatial_filter_radius')
        scalar_attrib('temporal_filter_width')
        scalar_attrib('quality', 'sample_density')
        scalar_attrib('passes', 'nbatches')
        scalar_attrib('temporal_samples', 'ntemporal_samples')
        scalar_attrib('brightness')
        scalar_attrib('gamma')
        scalar_attrib('highlight_power')
        scalar_attrib('vibrancy')
        scalar_attrib('estimator_radius', 'estimator')
        scalar_attrib('estimator_minimum')
        scalar_attrib('estimator_curve')
        scalar_attrib('gamma_threshold', 'gam_lin_thresh')

        scalar_attrib('supersample', 'spatial_oversample', int)

        mapped_attrib('interpolation', mapping={
            'linear': flam3.flam3_interpolation_linear,
            'smooth': flam3.flam3_interpolation_smooth,
        })

        mapped_attrib('palette_interpolation', mapping={
            'hsv': flam3.flam3_palette_interpolation_hsv,
            'sweep': flam3.flam3_palette_interpolation_sweep,
        })

        mapped_attrib('filter_shape', 'spatial_filter_select', mapping={
            'gaussian': flam3.flam3_gaussian_kernel,
            'hermite': flam3.flam3_hermite_kernel,
            'box': flam3.flam3_box_kernel,
            'triangle': flam3.flam3_triangle_kernel,
            'bell': flam3.flam3_bell_kernel,
            'bspline': flam3.flam3_b_spline_kernel,
            'mitchell': flam3.flam3_mitchell_kernel,
            'blackman': flam3.flam3_blackman_kernel,
            'catrom': flam3.flam3_catrom_kernel,
            'hanning': flam3.flam3_hanning_kernel,
            'hamming': flam3.flam3_hamming_kernel,
            'lanczos3': flam3.flam3_lanczos3_kernel,
            'lanczos2': flam3.flam3_lanczos2_kernel,
            'quadratic': flam3.flam3_quadratic_kernel,
        })

        mapped_attrib('temporal_filter_type', mapping={
            'box': flam3.flam3_temporal_box,
            'gaussian': flam3.flam3_temporal_gaussian,
            'exp': flam3.flam3_temporal_exp,
        })


        mapped_attrib('palette_mode', mapping={
            'step': flam3.flam3_palette_mode_step,
            'linear': flam3.flam3_palette_mode_linear,
        })

        mapped_attrib('interpolation', mapping={
            'smooth': flam3.flam3_interpolation_linear,
        })

        mapped_attrib('interpolation_type', mapping={
            'linear': flam3.flam3_inttype_linear,
            'log': flam3.flam3_inttype_log,
            'old': flam3.flam3_inttype_compat,
            'older': flam3.flam3_inttype_older,
        })

        mapped_attrib('palette_interpolation', mapping={
            'sweep': flam3.flam3_palette_interpolation_hsv ,
        })


        sym_node = self.flame_node.xpath('//symmetry')

        if sym_node:
            scalar_attrib('symmetry', coerce_type=int, node=sym_node[0])

        self.palette = Palette()

        for color_node in self.flame_node.xpath('//color'):
            # should this be int(math.floor(float(... ?
            #TODO: This loses all the float palette entries from flam3.  Is this what we want?
            index = int(float(color_node.attrib['index']))
            rgb = map(int, whitespace_array('rgb', node=color_node))

            self.palette.array[index].fill(rgb)

