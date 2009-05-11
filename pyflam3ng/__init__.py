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
import sys
import itertools
import random
import math
from collections import defaultdict

import numpy
import Image
import copy
from lxml import etree
from func import *

from .variations import variation_registry
from . import flam3
from . import util
from . import vector_utils as vu


EPSILON = 0.0000000000001

def float_equality(x, y):
    return abs(x-y) < (x * sys.float_info.epsilon)


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

    def __init__(self, x=0.0, y=0.0, seq=None):
        if seq is not None:
            self.x = seq[0]
            self.y = seq[1]
        else:
            self.x = x
            self.y = y

    def clone(self):
        return Point(self.x, self.y)

    def __iter__(self):
        yield self.x
        yield self.y

    def __getitem__(self, key):
        if key == 0:
            return self.x
        elif key == 1:
            return self.y
        else:
            raise IndexError()

    def __len__(self):
        return 2

    def __repr__(self):
        return '<Point x=%f y=%f>' % (self.x, self.y)

    def magnitude_squared(self):
        return self.x**2 + self.y**2

    def magnitude(self):
        return math.sqrt(self.magnitude_squared())

    def angle_radians(self):
        return math.atan2(self.y, self.x)

    def angle(self):
        return self.angle_radians() * (180.0/math.pi)

    def _get_polar(self):
        return self.magnitude(), self.angle()

    def _set_polar(self, angle, length):
        self.x = math.cos(angle * math.pi / 180.0)
        self.y = math.sin(angle * math.pi / 180.0)

    polar = property(_get_polar, _set_polar)

    def __add__(self, rhs):
        return Point(self.x + rhs[0], self.y + rhs[1])

    def __sub__(self, rhs):
        return Point(self.x - rhs[0], self.y - rhs[1])

    def __mul__(self, rhs):
        return Point(self.x * rhs[0], self.y * rhs[1])

    def __div__(self, rhs):
        return Point(self.x / rhs[0], self.y / rhs[1])

    def __iadd__(self, rhs):
        self.x += rhs[0]
        self.y += rhs[1]
        return self

    def __isub__(self, rhs):
        self.x -= rhs[0]
        self.y -= rhs[1]
        return self

    def __imul__(self, rhs):
        self.x *= rhs[0]
        self.y *= rhs[1]
        return self

    def __idiv__(self, rhs):
        self.x /= rhs[0]
        self.y /= rhs[1]
        return self

    def __eq__(self, rhs):
        if rhs is None:
            return False

        if float_equality(self.x, rhs[0]) and float_equality(self.y, rhs[1]):
            return True

        return False

    def in_circle(self, center, radius):
        # find the difference between the two points
        u = self - center

        # find the magnitude squared of the difference
        mm  = u.magnitude_squared()

        # if the magnitude is less than the radius it is inside the circle
        return (radius*radius - mm) >= 0.0

    def in_triangle(self, v0, v1, v2):
        e0 = self - v0
        e1 = v1 - v0
        e2 = v2 - v0

        if float_equality(e1.x, 0.):
            if float_equality(e2.x, 0.):
                return False

            u = e0.x / e2.x

            if u < 0 or u > 1:
                return False

            if float_equality(e1.y, 0.):
                return False

            v = (e0.y - e2.y * u) / e1.y

            if v < 0:
                return False
        else:
            d = e2.y * e1.x - e2.x * e1.y

            if float_equality(d, 0.):
                return False

            u = (e0.y * e1.x - e0.x * e1.y) / d

            if u < 0 or u > 1:
                return False

            v = (e0.x - e2.x * u) / e1.x

            if v < 0:
                return False

        return u + v <= 1.0

    def in_rect(self, left, top, right, bottom):
        if self.x < left or self.x > right:
            return False

        if self.y < top or self.y > bottom:
            return False

        return True

    def in_rect_wh(self, left, top, width, height):
        return self.in_rect(left, top, left + width, top + height)


class Matrix(object):
    def __init__(self):
        self._matrix = numpy.matrix([[1,0,0],[0,1,0],[0,0,1]])

    def clone(self):
        m = Matrix()
        m._matrix = self._matrix.copy()
        return m

    def transform(self, p):
        return Point(self._matrix[0,0] * p[0] + self._matrix[1,0] * p[1] + self._matrix[2,0],
                     self._matrix[0,1] * p[0] + self._matrix[1,1] * p[1] + self._matrix[2,1])

    def transform_distance(self, p):
        return Point(self._matrix[0,0] * p[0] + self._matrix[1,0] * p[1],
                     self._matrix[0,1] * p[0] + self._matrix[1,1] * p[1])

    def rotate(self, degrees):
        radians = degrees * (180.0/math.pi)
        c = math.cos(radians)
        s = math.sin(radians)

        m = numpy.matrix([[c, -s, 0], [s, c, 0], [0, 0, 1]])
        self._matrix *= m

    def translate(self, pos):
        m = numpy.matrix([[1, 0, 0], [0, 1, 0], [pos[0], pos[1], 1]])
        self._matrix *= m

    def scale(self, point):
        m = numpy.matrix([[point[0], 0, 0], [0, point[1], 0], [0, 0, 1]])
        self._matrix *= m

    def inverse(self):
        m = Matrix()
        m._matrix = numpy.linalg.inv(self._matrix)
        return m

    def __mul__(self, rhs):
        if hasattr(rhs, '_matrix'):
            rhs = rhs._matrix

        return self._matrix * rhs


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

    def __contains__(self, key):
        return key in self._values

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

    def get_variable(self, variation_name, variable_name):
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

    def rotate(self, slots):
        tmp = numpy.zeros((256,3))
        tmp[:slots] = self.array[-slots:]
        tmp[slots:] = self.array[:-slots]
        self.array[:] = tmp[:]

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
            hr = h_ranges[random.randint(0, len(h_ranges)-1)]
            h = random.uniform(hr[0], hr[1])
            lr = l_ranges[random.randint(0, len(l_ranges)-1)]
            l = random.uniform(lr[0], lr[1])
            sr = s_ranges[random.randint(0, len(s_ranges)-1)]
            s = random.uniform(sr[0], sr[1])
            for i in xrange(b):
                self.array[index] = hls2rgb(h,l,s)
                index += 1

    def from_seed(self, seed, c_split=0, split=90, dist=64, space='rgb', curve='hcos'):
        c_split /= 360.0
        split /= 360.0
        if space=='rgb':
            h,l,s = rgb2hls(*seed)
            comp = hls2rgb(h+c_split+0.5,l,s)
            lspl = hls2rgb(h-split,l,s)
            rspl = hls2rgb(h+split,l,s)
        elif space=='hls':
            seed = rgb2hls(*seed)
            comp = [clip(h+c_split+0.5,0,1,True),l,s]
            lspl = [clip(h-split,0,1,True),l,s]
            rspl = [clip(h+split,0,1,True),l,s]
        else:
            raise ValueError('Invalid color space')

        tmp = numpy.zeros((256,3))
        tmp[:dist] = vu.get_spline([vu.CP(comp), vu.CP(lspl)], dist, curve=curve)
        tmp[dist:128] = vu.get_spline([vu.CP(lspl), vu.CP(seed)], 128-dist, curve=curve)
        tmp[128:256-dist] = vu.get_spline([vu.CP(seed), vu.CP(rspl)], 128-dist, curve=curve)
        tmp[256-dist:] = vu.get_spline([vu.CP(rspl), vu.CP(comp)], dist, curve=curve)

        if space=='hls':
            for i in xrange(256):
                tmp[i] = hls2rgb(*tmp[i])

        self.array[:] = tmp[:]

    def from_seeds(self, seeds, space='rgb', curve='hcos'):
        ns = len(seeds)
        d = 256/ns
        r = 256%ns
        ds = []
        for i in xrange(ns):
            if space=='hls':
                seeds[i] = rgb2hls(*seeds[i])
            if i+1<=r: ds.append(d+1)
            else:      ds.append(d)
        tmp = numpy.zeros((256,3))
        for i in xrange(ns):
            v = vu.get_spline([vu.CP(seeds[i-1]), vu.CP(seeds[i])], ds[i], curve=curve)
            tmp[sum(ds[0:i]):sum(ds[0:i+1])] = v
        if space=='hls':
            for i in xrange(256):
                tmp[i] = hls2rgb(*tmp[i])
        self.array[:] = tmp[:]

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
    def __init__(self, xml_node=None, **kwargs):
        self._weight = kwargs.get('weight', 0.0)
        self._color = kwargs.get('color', 0.0)
        self._symmetry = kwargs.get('symmetry', 0.0)
        self._opacity = kwargs.get('opacity', 1.0)
        self.animate = 0.0
        self._x = Point()
        self._y = Point()
        self._o = Point()
        self._px = Point()
        self._py = Point()
        self._po = Point()
        self.coefs = kwargs.get('coefs', [0.0, 1.0, 1.0, 0.0, 0.0, 0.0])
        self.post = kwargs.get('post', [0.0, 1.0, 1.0, 0.0, 0.0, 0.0])
        #self.coefs = [(x,y for x,y in [self.x, self.y, self.o])] #?
        #self.post = [(x,y for x,y in [self.px, self.py, self.po])]
        self.vars = Variations()

        if xml_node is not None:
            self._load_xml(xml_node)

    def copy(self):
        return copy.deepcopy(self)

    def get_pad(self):
        hole_vars = ['spherical', 'ngon', 'julian', 'juliascope', 'polar'
                    ,'wedge_sph', 'wedge_julia']
        pad = self.copy()
        pad.coefs = [0.0, 1.0, 1.0, 0.0, 0.0, 0.0]
        pad.weight = 0.0
        pad.symmetry = 1.0
        
        if len(set(pad.vars.values.keys()).intersection(hole_vars)) > 0:
            pad.coefs = [-1.0, 0.0, 0.0, -1.0, 0.0, 0.0]
            pad.vars.set_variation('linear', -1.0)
        if 'rectangles' in pad.vars.values.keys():
            pad.vars.set_variation('rectangles', 1.0)
            pad.vars.set_variable('rectangles', 'x', 0.0)
            pad.vars.set_variable('rectangles', 'y', 0.0)
        if 'rings2' in pad.vars.values.keys():
            pad.vars.set_variation('rings2', 1.0)
            pad.vars.set_variable('rings2', 'val', 0.0)
        if 'fan2' in pad.vars.values.keys():
            pad.vars.set_variation('fan2', 1.0)
            pad.vars.set_variable('fan2', 'x', 0.0)
            pad.vars.set_variable('fan2', 'y', 0.0)
        if 'blob' in pad.vars.values.keys():
            pad.vars.set_variation('blob', 1.0)
            pad.vars.set_variable('blob', 'low', 1.0)
            pad.vars.set_variable('blob', 'high', 1.0)
            pad.vars.set_variable('blob', 'waves', 1.0)
        if 'perspective' in pad.vars.values.keys():
            pad.vars.set_variation('perspective', 1.0)
            pad.vars.set_variable('perspective', 'angle' , 0.0)
        if 'curl' in pad.vars.values.keys():
            pad.vars.set_variation('curl', 1.0)
            pad.vars.set_variable('curl', 'c1', 0.0)
            pad.vars.set_variable('curl', 'c2', 0.0)
        if 'super_shape' in pad.vars.values.keys():
            pad.vars.set_variation('super_shape', 1.0)
            pad.vars.set_variable('super_shape', 'n1', 2.0)
            pad.vars.set_variable('super_shape', 'n2', 2.0)
            pad.vars.set_variable('super_shape', 'n3', 2.0)
            pad.vars.set_variable('super_shape', 'rnd', 0.0)
            pad.vars.set_variable('super_shape', 'holes', 0.0)
        if 'fan' in pad.vars.values.keys():
            pad.vars.set_variation('fan', 1.0)
        if 'rings' in pad.vars.values.keys():
            pad.vars.set_variation('rings', 1.0)
        #tot = sum(pad.vars.values.values())
        #for v in pad.vars.values: pad.vars.values[v] /= tot
        return 

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

    """This is for interpo for now"""
    def get_attribs(self):
        attribs = {'x': self.x, 'y': self.y, 'o': self.o
                  ,'weight': self.weight, 'color': self.color
                  ,'symmetry': self.symmetry, 'opacity': self.opacity
                  ,'vars': self.vars.values, 'variables': self.vars.variables}
        if self.post <> [0, 1, 1, 0, 0, 0]:
            attribs.setdefault('px', self.px)
            attribs.setdefault('py', self.py)
            attribs.setdefault('po', self.po)
        return attribs

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
    def __init__(self, random=True, flame_node=None, genome_handle=None):
        self.set_defaults()

        if flame_node is not None:
            self._init_from_node(flame_node)
        elif genome_handle is not None:
            self._init_from_handle(genome_handle)
        else:
            self.genome_handle = flam3.GenomeHandle()
            if random: self.random()

    def set_defaults(self):
        self.time = 0.0

        self._finalx = False
        self._final = Xform()
        self._final.vars.set_variation('linear', 1.0)

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

    """This is for interpo for now"""
    def get_attribs(self):
        attribs = {'brightness': self.brightness, 'contrast': self.contrast
                  ,'gamma': self.gamma, 'vibrancy': self.vibrancy
                  ,'rotate': self.rotate, 'scale': self.pixels_per_unit
                  ,'symmetry': self.symmetry, 'center': self.center}
        xattribs = {}
        for i in xrange(len(self.xforms)):
            xattribs.setdefault('xf'+str(i), self.xforms[i].get_attribs())
        attribs.setdefault('xforms', xattribs)
        return attribs

    def has_final(self):
        return self._finalx

    def enable_final(self):
        self._finalx = True

    def disable_final(self):
        self._finalx = False

    def _get_final(self):
        if not self._finalx: return None
        else:                return self._final

    def _set_final(self, xform):
        if not xform:
            self._finalx = False
        else:
            self._final = xform

    final = property(_get_final, _set_final,
             doc='Returns the final xform (None if disabled).')

    def _init_from_node(self, flame_node):
        self.flame_node = flame_node
        self._refresh_handle_from_self()
        self._refresh_self_from_handle()

    def _init_from_handle(self, genome_handle):
        self.genome_handle = genome_handle
        self._refresh_self_from_handle()

    def clone(self):
        return load_genome(xml_source=etree.tostring(self.flame_node))

    def render(self, buffer, **kwargs):
        return self.genome_handle.render(buffer, **kwargs)

    def random(self, variations=None, symmetry=False, num_xforms=2):
        if variations is None:
            variations = flam3.get_variation_list()

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

        self.name = 'unknown'
        scalar_attrib('name', coerce_type=str)
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


