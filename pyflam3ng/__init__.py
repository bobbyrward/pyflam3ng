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
import numpy, random, Image
from func import *
from variations import variation_registry

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
        self._x = x
        self._y = y
        self._len, self._ang = polar(self._x, self._y)

    def __iter__(self):
        yield self._x
        yield self._y

    def __len__(self):
        return 2

    def __repr__(self):
        return '<Point x=%f y=%f>' % (self.x, self.y)

    def _get_x(self):
        if self._x > -1E-06 and self._x < 1E-06: self._x = 0.0
        return self._x

    def _set_x(self, x):
        self._x = x
        self._len, self._ang = polar(self._x, self._y)

    x = property(_get_x, _set_x)

    def _get_y(self):
        if self._y > -1E-06 and self._y < 1E-06: self._y = 0.0
        return self._y

    def _set_y(self, y):
        self._y = y
        self._len, self._ang = polar(self._x, self._y)

    y = property(_get_y, _set_y)

    def _get_rect(self):
        return self._x, self._y

    def _set_rect(self, coord):
        self._x, self._y = coord
        self._len, self._ang = polar(self._x, self._y)

    rect = property(_get_rect, _set_rect)

    def _get_len(self):
        return self._len

    def _set_len(self, len):
        self._len = len
        self._x, self._y = rect(self._len, self._ang)

    len = property(_get_len, _set_len)

    def _get_ang(self):
        return self._ang

    def _set_ang(self, ang):
        self._ang = ang
        self._x, self._y = rect(self._len, self._ang)

    ang = property(_get_ang, _set_ang)

    def _get_polar(self):
        return self._len, self._ang

    def _set_polar(self, coord):
        self._len, self._ang = coord
        self._x, self._y = rect(self._len, self._ang)

    polar = property(_get_polar, _set_polar)


class Variations(object):
    """Wraps the variations in use by an XForm"""

    def __init__(self):
        self._values = {}
        self._variables = {}

    def __getitem__(self, key):
        return self.values[key]

    def __setitem__(self, key, value):
        self.values[key] = value

    def __delitem__(self, key):
        del self.values[key]

    def variation_vars(self, variation_name=None):
        if variation_name in self._variables:
            return self._variables[variation_name]
        else:
            return None

    def set_variable(self, variation_name, variable_name, value):
        if variation_name in self._variables:
            vars = self._variables[variation_name]

            if variable_name in vars:
                vars[variable_name] = value
            else:
                raise KeyError('Unknown variable')
        else:
            raise KeyError('Unknown variation')

    def get_variable(self, variation_name, variable_name, value):
        if variation_name in self._variables:
            vars = self._variables[variation_name]

            if variable_name in vars:
                return vars[variable_name]
            else:
                raise KeyError('Unknown variable')
        else:
            raise KeyError('Unknown variation')

    def set_variation(self, variation_name, value=1.0):
        if variation_name not in variation_registry.keys():
            return KeyError('Unknown variation')
        if variation_name in self._values:
            if value == 0.0:
                self._values.pop(variation_name)
            else:
                self._values[variation_name] = value
        else:
            self._values.setdefault(variation_name, value)
        if variation_registry[variation_name]:
            if value == 0.0:
                self._variables.pop(variation_name)
            else:
                self._variables.setdefault(variation_name,
                        variation_registry[variation_name])

    def _get_values(self):
        return self._values

    values = property(_get_values)

    def _get_variables(self):
        return self._variables

    variables = property(_get_variables)


class Palette(object):
    def __init__(self):
        self.array = numpy.zeros((256,3), numpy.uint8)

    def smooth(self, ntries=50, trysize=10000):
        self.array = util.palette_improve(self.array, ntries, trysize)

    def adjust_hue(self, val):
        for i in xrange(256):
            color = self.array[i]
            color = rgb2hls(color[0], color[1], color[2])
            self.array[i] = hls2rgb(color[0]+val, color[1], color[2])

    def adjust_sat(self, val):
        for i in xrange(256):
            color = self.array[i]
            color = rgb2hls(color[0], color[1], color[2])
            self.array[i] = hls2rgb(color[0], color[1], color[2]+val)

    def adjust_bright(self, val):
        for i in xrange(256):
            color = self.array[i]
            color = rgb2hls(color[0], color[1], color[2])
            self.array[i] = hls2rgb(color[0], color[1]+val, color[2])

    def random(self, h_ranges=[(0,1)], l_ranges=[(0,1)], s_ranges=[(0,1)],
               blocks=(32,64)):

        if type(blocks) == int:
            nblocks = blocks
        elif type(blocks) == tuple and len(blocks) == 2:
            nblocks = random.randint(blocks[0], blocks[1])
        else:
            raise TypeError('blocks must be int or 2-tuple range')

        mbs = 256/nblocks
        mbr = 256%nblocks
        bsv = mbs/2
        bs = []
        for i in xrange(nblocks):
            v = random.randint(-bsv, bsv)
            mbr -= v
            bs.append(mbs+v)
        if mbr > 0:
            r = len(bs)/mbr
            for i in xrange(mbr):
                bs[(i*r)+random.randrange(r)] += 1
        elif mbr < 0:
            r = -len(bs)/mbr
            for i in xrange(-mbr):
                bs[(i*r)+random.randrange(r)] -= 1
        index = 0
        for b in bs:
            h = random.random()
            while not in_ranges(h, h_ranges): h = random.random()
            l = random.random()
            while not in_ranges(l, l_ranges): l = random.random()
            s = random.random()
            while not in_ranges(s, s_ranges): s = random.random()
            for i in xrange(b):
                self.array[index] = hls2rgb(h,l,s)
                index += 1

    def from_file(self, filename):
        img = Image.open(filename)
        bin = map(ord, img.tostring())
        for i in xrange(256):
            x = random.randint(0, img.size[0]-1)
            y = random.randint(0, img.size[1]-1)
            idx = 3*(x + img.size[0]*y)
            self.array[i] = bin[idx:idx+3]
        self.smooth()


class Xform(object):
    def __init__(self, xml_node=None):
        self._weight = 0.0
        self._color = 0.0
        self._symmetry = 0.0
        self._opacity = 1.0
        self.animate = 0.0
        self._x = Point(1.0, 0.0)
        self._y = Point(0.0, 1.0)
        self._o = Point(0.0, 0.0)
        self._px = Point(1.0, 0.0)
        self._py = Point(0.0, 1.0)
        self._po = Point(0.0, 0.0)
        #self.coefs = [(x,y for x,y in [self.x, self.y, self.o])] #?
        #self.post = [(x,y for x,y in [self.px, self.py, self.po])]
        self.vars = Variations()

        if xml_node is not None:
            self._load_xml(xml_node)

    def rotate_x(self, deg):
        self._x.ang += deg

    def rotate_y(self, deg):
        self._y.ang += deg

    def scale_x(self, scale):
        self._x.len *= scale

    def scale_y(self, scale):
        self._y.len *= scale

    def rotate(self, deg):
        self.rotate_x(deg)
        self.rotate_y(deg)

    def pivot(self, deg):
        self._o.ang += deg

    def scale(self, scale):
        self.scale_x(scale)
        self.scale_y(scale)

    #properties
    def _get_weight(self):
        return self._weight

    def _set_weight(self, weight):
        self._weight = clip(weight, mini=0.0)

    weight = property(_get_weight, _set_weight)

    def _get_color(self):
        return self._color

    def _set_color(self, color):
        self._color = clip(color, mini=0.0, maxi=1.0)

    color = property(_get_color, _set_color)

    def _get_symmetry(self):
        return self._symmetry

    def _set_symmetry(self, symmetry):
        self._symmetry = clip(symmetry, mini=-1.0, maxi=1.0)

    symmetry = property(_get_symmetry, _set_symmetry)

    def _get_opacity(self):
        return self._opacity

    def _set_opacity(self, opacity):
        self._opacity = clip(opacity, mini=0.0, maxi=1.0)

    opacity = property(_get_opacity, _set_opacity)

    def _get_x(self):
        return self._x

    def _set_x(self, x):
        if not isinstance(x, Point):
            if len(x) <> 2:
                raise ValueError('Need x,y point for x')
            else:
                self._x = Point(x[0], x[1])
        else:
            self._x = x

    x = property(_get_x, _set_x)

    def _get_y(self):
        return self._y

    def _set_y(self, y):
        if not isinstance(y, Point):
            if len(y) <> 2:
                raise ValueError('Need x,y point for y')
            else:
                self._y = Point(y[0], y[1])
        else:
            self._y = y

    y = property(_get_y, _set_y)

    def _get_o(self):
        return self._o

    def _set_o(self, o):
        if not isinstance(o, Point):
            if len(o) <> 2:
                raise ValueError('Need x,y point for o')
            else:
                self._o = Point(o[0], o[1])
        else:
            self._o = o

    o = property(_get_o, _set_o)

    def _get_px(self):
        return self._px

    def _set_px(self, px):
        if not isinstance(x, Point):
            if len(px) <> 2:
                raise ValueError('Need x,y point for px')
            else:
                self._px = Point(px[0], px[1])
        else:
            self._px = px

    px = property(_get_px, _set_px)

    def _get_py(self):
        return self._py

    def _set_py(self, py):
        if not isinstance(y, Point):
            if len(py) <> 2:
                raise ValueError('Need x,y point for py')
            else:
                self._py = Point(py[0], py[1])
        else:
            self._py = py

    py = property(_get_py, _set_py)

    def _get_po(self):
        return self._po

    def _set_po(self, po):
        if not isinstance(po, Point):
            if len(po) <> 2:
                raise ValueError('Need x,y point for po')
            else:
                self._po = Point(po[0], po[1])
        else:
            self._po = po

    po = property(_get_po, _set_po)

    def _get_coefs(self):
        return [self._x.x, self._x.y, self._y.x, self._y.y, self._o.x, self._o.y]

    def _set_coefs(self, coefs):
        if type(coefs)==list or type(coefs)==tuple:
            if len(coefs)==3 and isinstance(coefs[0],Point):
                self._x = coefs[0]
                self._y = coefs[1]
                self._o = coefs[2]
            elif len(coefs)==6:
                self._x = Point(coefs[0], coefs[1])
                self._y = Point(coefs[2], coefs[3])
                self._o = Point(coefs[4], coefs[5])
            else:
                raise TypeError('need list of 3 Points or 6 vals')

    coefs = property(_get_coefs, _set_coefs)

    def _get_post(self):
        return [self._px.x, self._px.y, self._py.x, self._py.y, self._po.x, self._po.y]

    def _set_post(self, coefs):
        if type(coefs)==list or type(coefs)==tuple:
            if len(coefs)==3 and isinstance(coefs[0],Point):
                self._px = coefs[0]
                self._py = coefs[1]
                self._po = coefs[2]
            elif len(coefs)==6:
                self._px = Point(coefs[0], coefs[1])
                self._py = Point(coefs[2], coefs[3])
                self._po = Point(coefs[4], coefs[5])
            else:
                raise TypeError('need list of 3 Points or 6 vals')

    post = property(_get_post, _set_post)

    def _load_xml(self, xform_node):
        def scalar_attrib(src_name, dest_name=None, coerce_type=float, node=xform_node):
            if src_name in node.attrib:
                setattr(self, dest_name if dest_name else src_name,
                        coerce_type(node.attrib[src_name]))


        def whitespace_array(src_name, coerce_type=float, node=xform_node):
            return map(coerce_type, node.attrib.get(src_name).split(' '))


        scalar_attrib('weight')
        self.color = 0.0
        scalar_attrib('color')
        scalar_attrib('symmetry', 'symmetry')
        scalar_attrib('color_speed', 'symmetry')
        scalar_attrib('animate')

        self.opacity = 1.0
        scalar_attrib('opacity')

        coefs_list = whitespace_array('coefs')
        self._x = Point(coefs_list[0], coefs_list[1])
        self._y = Point(coefs_list[2], coefs_list[3])
        self._o = Point(coefs_list[4], coefs_list[5])

        if 'post' in xform_node.attrib:
            post_list = whitespace_array('post')
            self._px = Point(post_list[0], post_list[1])
            self._py = Point(post_list[2], post_list[3])
            self._po = Point(post_list[4], post_list[5])

        for name, value in xform_node.attrib.iteritems():
            if name in variations.variation_registry:
                self.vars.set_variation(name, float(value))
                continue

            parts = name.split('_')

            if len(parts) == 2 and parts[0] in variations.variation_registry:
                self.vars.set_variable(parts[0], parts[1], value)

            #TODO: chaos


#---end Xform

class Genome(object):
    def __init__(self, flame_node=None, genome_handle=None):
        self.set_defaults()

        if flame_node is not None:
            self._init_from_node(flame_node)
        elif genome_handle is not None:
            self._init_from_handle(genome_handle)

    def set_defaults(self):
        self.time = 0.0

        self.palette = Palette()

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

        self.xforms = []


    def _init_from_node(self, flame_node):
        self.flame_node = flame_node
        self._refresh_handle_from_self()
        self._refresh_self_from_handle()

    def _init_from_handle(self, genome_handle):
        self.genome_handle = genome_handle
        self._refresh_self_from_handle()

    def random(self, variations, symmetry=False, num_xforms=2):
        self.genome_handle.random(variations, symmetry, num_xforms)
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

        self.xforms = []
        for xform_node in self.flame_node.xpath('//xform'):
            self.xforms.append(Xform(xml_node=xform_node))


