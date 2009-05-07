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
from func import *

from pyflam3ng import flam3
from pyflam3ng import util

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
        return self._x

    def _set_x(self, x):
        self._x = x
        self._len, self._ang = polar(self._x, self._y)

    x = property(_get_x, _set_x)

    def _get_y(self):
        return self._y

    def _set_y(self, val):
        self._y = val
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
        self.values = defaultdict(lambda: 0.0)
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
            'bent2': {
                'x': 0.0,
                'y': 0.0,
            },
            'bipolar': {
                'shift': 0.0,
            },
            'cell': {
                'size': 1.0,
            },
            'cpow': {
                'r': 1.0,
                'i': 0.0,
                'power': 1.0,
            },
            'curve': {
                'xamp': 1.0,
                'yamp': 1.0,
                'xlength': 1.0,
                'ylength': 1.0,
            },
            'escher': {
                'beta': 0.0,
            },
            'lazysusan': {
                'spin': 0.0,
                'space': 0.0,
                'twist': 0.0,
                'x': 1.0,
                'y': 1.0,
            },
            'modulus': {
                'x': 1.0,
                'y': 1.0,
            },
            'oscope': {
                'separation': 0.0,
                'frequency': 1.0,
                'amplitude': 1.0,
                'damping': 0.0,
            },
            'popcorn2': {
                'x': 0.0,
                'y': 0.0,
                'c': 0.0,
            },
            'separation': {
                'x': 0.0,
                'xinside': 0.0,
                'y': 0.0,
                'yinside': 0.0,
            },
            'split': {
                'xsize': 0.0,
                'ysize': 0.0,
            },
            'splits': {
                'x': 1.0,
                'y': 1.0,
            },
            'stripes': {
                'space': 1.0,
                'warp': 0.0,
            },
            'wedge': {
                'angle': 0.0,
                'hole': 0.0,
                'count': 0.0,
                'swirl': 0.0,
            },
            'wedge_julia': {
                'angle': 0.0,
                'count': 0.0,
                'power': 2.0,
                'dist': 1.0,
            },
            'wedge_sph': {
                'angle': 0.0,
                'count': 0.0,
                'hole': 0.0,
                'swirl': 0.0,
            },
            'whorl': {
                'inside': 1.0,
                'outside': 1.0,
            },
            'waves2': {
                'freqx': 1.0,
                'scalex': 1.0,
                'freqy': 1.0,
                'scaley': 1.0,
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
        if weight < 0.0:
            weight = 0.0
        self._weight = weight

    weight = property(_get_weight, _set_weight)

    def _get_color(self):
        return self._color

    def _set_color(self, color):
        if color < 0.0:   color = 0.0
        elif color > 1.0: color = 1.0
        self._color = color

    color = property(_get_color, _set_color)

    def _get_symmetry(self):
        return self._symmetry

    def _set_symmetry(self, symmetry):
        if symmetry < -1.0:  symmetry = -1.0
        elif symmetry > 1.0: symmetry = 1.0
        self._symmetry = symmetry

    symmetry = property(_get_symmetry, _set_symmetry)

    def _get_opacity(self):
        return self._opacity

    def _set_opacity(self, opacity):
        if opacity < 0.0:   opacity = 0.0
        elif opacity > 1.0: opacity = 1.0
        self._opacity = opacity

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

        scalar_attrib('weight')
        self.color = 0.0
        scalar_attrib('color')
        scalar_attrib('symmetry', 'symmetry')
        scalar_attrib('color_speed', 'symmetry')
        scalar_attrib('animate')

        self.opacity = 1.0
        scalar_attrib('opacity')


        self._x = Point(1.0, 0.0)
        self._y = Point(0.0, 1.0)
        self._o = Point(0.0, 0.0)
        self._px = Point(1.0, 0.0)
        self._py = Point(0.0, 1.0)
        self._po = Point(0.0, 0.0)
        pass
s="""
   for (j = 0; j < lnv; j++) {
      double v = x->var[j];
      if (0.0 != v) {
         fprintf(f, "%s=\"%g\" ", flam3_variation_names[j], v);
         if (j==VAR_BLOB)
            blob_var=1;
         else if (j==VAR_PDJ)
            pdj_var=1;
         else if (j==VAR_FAN2)
            fan2_var=1;
         else if (j==VAR_RINGS2)
            rings2_var=1;
         else if (j==VAR_PERSPECTIVE)
            perspective_var=1;
         else if (j==VAR_JULIAN)
            juliaN_var=1;
         else if (j==VAR_JULIASCOPE)
            juliaScope_var=1;
         else if (j==VAR_RADIAL_BLUR)
            radialBlur_var=1;
         else if (j==VAR_PIE)
            pie_var=1;
         else if (j==VAR_NGON)
            ngon_var=1;
         else if (j==VAR_CURL)
            curl_var=1;
         else if (j==VAR_RECTANGLES)
            rectangles_var=1;
         else if (j==VAR_DISC2)
            disc2_var=1;
         else if (j==VAR_SUPER_SHAPE)
            supershape_var=1;
         else if (j==VAR_FLOWER)
            flower_var=1;
         else if (j==VAR_CONIC)
            conic_var=1;
         else if (j==VAR_PARABOLA)
            parabola_var=1;
         else if (j==VAR_BENT2)
            bent2_var=1;
         else if (j==VAR_BIPOLAR)
            bipolar_var=1;
         else if (j==VAR_CELL)
            cell_var=1;
         else if (j==VAR_CPOW)
            cpow_var=1;
         else if (j==VAR_CURVE)
            curve_var=1;
         else if (j==VAR_ESCHER)
            escher_var=1;
         else if (j==VAR_LAZYSUSAN)
            lazys_var=1;
         else if (j==VAR_MODULUS)
            modulus_var=1;
         else if (j==VAR_OSCILLOSCOPE)
            oscope_var=1;
         else if (j==VAR_POPCORN2)
            popcorn2_var=1;
         else if (j==VAR_SPLIT)
            split_var=1;
         else if (j==VAR_SPLITS)
            splits_var=1;
         else if (j==VAR_STRIPES)
            stripes_var=1;
         else if (j==VAR_WEDGE)
            wedge_var=1;
         else if (j==VAR_WEDGE_JULIA)
            wedgeJ_var=1;
         else if (j==VAR_WEDGE_SPH)
            wedgeS_var=1;
         else if (j==VAR_WHORL)
            whorl_var=1;
         else if (j==VAR_WAVES2)
            waves2_var=1;
      }
   }

   if (!motion_flag) {
      if (blob_var==1) {
         fprintf(f, "blob_low=\"%g\" ", x->blob_low);
         fprintf(f, "blob_high=\"%g\" ", x->blob_high);
         fprintf(f, "blob_waves=\"%g\" ", x->blob_waves);
      }

      if (pdj_var==1) {
         fprintf(f, "pdj_a=\"%g\" ", x->pdj_a);
         fprintf(f, "pdj_b=\"%g\" ", x->pdj_b);
         fprintf(f, "pdj_c=\"%g\" ", x->pdj_c);
         fprintf(f, "pdj_d=\"%g\" ", x->pdj_d);
      }

      if (fan2_var==1) {
         fprintf(f, "fan2_x=\"%g\" ", x->fan2_x);
         fprintf(f, "fan2_y=\"%g\" ", x->fan2_y);
      }

      if (rings2_var==1) {
         fprintf(f, "rings2_val=\"%g\" ", x->rings2_val);
      }

      if (perspective_var==1) {
         fprintf(f, "perspective_angle=\"%g\" ", x->perspective_angle);
         fprintf(f, "perspective_dist=\"%g\" ", x->perspective_dist);
      }

      if (juliaN_var==1) {
         fprintf(f, "julian_power=\"%g\" ", x->julian_power);
         fprintf(f, "julian_dist=\"%g\" ", x->julian_dist);
      }

      if (juliaScope_var==1) {
         fprintf(f, "juliascope_power=\"%g\" ", x->juliascope_power);
         fprintf(f, "juliascope_dist=\"%g\" ", x->juliascope_dist);
      }

      if (radialBlur_var==1) {
         fprintf(f, "radial_blur_angle=\"%g\" ", x->radial_blur_angle);
      }

      if (pie_var==1) {
         fprintf(f, "pie_slices=\"%g\" ", x->pie_slices);
         fprintf(f, "pie_rotation=\"%g\" ", x->pie_rotation);
         fprintf(f, "pie_thickness=\"%g\" ", x->pie_thickness);
      }

      if (ngon_var==1) {
         fprintf(f, "ngon_sides=\"%g\" ", x->ngon_sides);
         fprintf(f, "ngon_power=\"%g\" ", x->ngon_power);
         fprintf(f, "ngon_corners=\"%g\" ", x->ngon_corners);
         fprintf(f, "ngon_circle=\"%g\" ", x->ngon_circle);
      }

      if (curl_var==1) {
         fprintf(f, "curl_c1=\"%g\" ", x->curl_c1);
         fprintf(f, "curl_c2=\"%g\" ", x->curl_c2);
      }

      if (rectangles_var==1) {
         fprintf(f, "rectangles_x=\"%g\" ", x->rectangles_x);
         fprintf(f, "rectangles_y=\"%g\" ", x->rectangles_y);
      }

      if (disc2_var==1) {
         fprintf(f, "disc2_rot=\"%g\" ", x->disc2_rot);
         fprintf(f, "disc2_twist=\"%g\" ", x->disc2_twist);
      }

      if (supershape_var==1) {
         fprintf(f, "super_shape_rnd=\"%g\" ", x->super_shape_rnd);
         fprintf(f, "super_shape_m=\"%g\" ", x->super_shape_m);
         fprintf(f, "super_shape_n1=\"%g\" ", x->super_shape_n1);
         fprintf(f, "super_shape_n2=\"%g\" ", x->super_shape_n2);
         fprintf(f, "super_shape_n3=\"%g\" ", x->super_shape_n3);
         fprintf(f, "super_shape_holes=\"%g\" ", x->super_shape_holes);
      }

      if (flower_var==1) {
         fprintf(f, "flower_petals=\"%g\" ", x->flower_petals);
         fprintf(f, "flower_holes=\"%g\" ", x->flower_holes);
      }

      if (conic_var==1) {
         fprintf(f, "conic_eccentricity=\"%g\" ", x->conic_eccentricity);
         fprintf(f, "conic_holes=\"%g\" ", x->conic_holes);
      }

      if (parabola_var==1) {
         fprintf(f, "parabola_height=\"%g\" ", x->parabola_height);
         fprintf(f, "parabola_width=\"%g\" ", x->parabola_width);
      }

      if (bent2_var==1) {
         fprintf(f, "bent2_x=\"%g\" ", x->bent2_x);
         fprintf(f, "bent2_y=\"%g\" ", x->bent2_y);
      }

      if (bipolar_var==1) {
         fprintf(f, "bipolar_shift=\"%g\" ", x->bipolar_shift);
      }

      if (cell_var==1) {
         fprintf(f, "cell_size=\"%g\" ", x->cell_size);
      }

      if (cpow_var==1) {
         fprintf(f, "cpow_i=\"%g\" ", x->cpow_i);
         fprintf(f, "cpow_r=\"%g\" ", x->cpow_r);
         fprintf(f, "cpow_power=\"%g\" ", x->cpow_power);
      }

      if (curve_var==1) {
         fprintf(f, "curve_xamp=\"%g\" ", x->curve_xamp);
         fprintf(f, "curve_yamp=\"%g\" ", x->curve_yamp);
         fprintf(f, "curve_xlength=\"%g\" ", x->curve_xlength);
         fprintf(f, "curve_ylength=\"%g\" ", x->curve_ylength);
      }

      if (escher_var==1) {
         fprintf(f, "escher_beta=\"%g\" ", x->escher_beta);
      }

      if (lazys_var==1) {
         fprintf(f, "lazysusan_x=\"%g\" ", x->lazysusan_x);
         fprintf(f, "lazysusan_y=\"%g\" ", x->lazysusan_y);
         fprintf(f, "lazysusan_spin=\"%g\" ", x->lazysusan_spin);
         fprintf(f, "lazysusan_space=\"%g\" ", x->lazysusan_space);
         fprintf(f, "lazysusan_twist=\"%g\" ", x->lazysusan_twist);
      }

      if (modulus_var==1) {
         fprintf(f, "modulus_x=\"%g\" ", x->modulus_x);
         fprintf(f, "modulus_y=\"%g\" ", x->modulus_y);
      }

      if (oscope_var==1) {
         fprintf(f, "oscope_separation=\"%g\" ", x->oscope_separation);
         fprintf(f, "oscope_frequency=\"%g\" ", x->oscope_frequency);
         fprintf(f, "oscope_amplitude=\"%g\" ", x->oscope_amplitude);
         fprintf(f, "oscope_damping=\"%g\" ", x->oscope_damping);
      }

      if (popcorn2_var==1) {
         fprintf(f, "popcorn2_x=\"%g\" ", x->popcorn2_x);
         fprintf(f, "popcorn2_y=\"%g\" ", x->popcorn2_y);
         fprintf(f, "popcorn2_c=\"%g\" ", x->popcorn2_c);
      }

      if (separation_var==1) {
         fprintf(f, "separation_x=\"%g\" ", x->separation_x);
         fprintf(f, "separation_y=\"%g\" ", x->separation_y);
         fprintf(f, "separation_xinside=\"%g\" ", x->separation_xinside);
         fprintf(f, "separation_yinside=\"%g\" ", x->separation_yinside);
      }

      if (split_var==1) {
         fprintf(f, "split_xsize=\"%g\" ", x->split_xsize);
         fprintf(f, "split_ysize=\"%g\" ", x->split_ysize);
      }

      if (splits_var==1) {
         fprintf(f, "splits_x=\"%g\" ", x->splits_x);
         fprintf(f, "splits_y=\"%g\" ", x->splits_y);
      }

      if (stripes_var==1) {
         fprintf(f, "stripes_space=\"%g\" ", x->stripes_space);
         fprintf(f, "stripes_warp=\"%g\" ", x->stripes_warp);
      }

      if (wedge_var==1) {
         fprintf(f, "wedge_angle=\"%g\" ", x->wedge_angle);
         fprintf(f, "wedge_hole=\"%g\" ", x->wedge_hole);
         fprintf(f, "wedge_count=\"%g\" ", x->wedge_count);
         fprintf(f, "wedge_swirl=\"%g\" ", x->wedge_swirl);
      }

      if (wedgeJ_var==1) {
         fprintf(f, "wedge_julia_angle=\"%g\" ", x->wedge_julia_angle);
         fprintf(f, "wedge_julia_count=\"%g\" ", x->wedge_julia_count);
         fprintf(f, "wedge_julia_power=\"%g\" ", x->wedge_julia_power);
         fprintf(f, "wedge_julia_dist=\"%g\" ", x->wedge_julia_dist);
      }

      if (wedgeS_var==1) {
         fprintf(f, "wedge_sph_angle=\"%g\" ", x->wedge_sph_angle);
         fprintf(f, "wedge_sph_hole=\"%g\" ", x->wedge_sph_hole);
         fprintf(f, "wedge_sph_count=\"%g\" ", x->wedge_sph_count);
         fprintf(f, "wedge_sph_swirl=\"%g\" ", x->wedge_sph_swirl);
      }

      if (whorl_var==1) {
         fprintf(f, "whorl_inside=\"%g\" ", x->whorl_inside);
         fprintf(f, "whorl_outside=\"%g\" ", x->whorl_outside);
      }

      if (waves2_var==1) {
         fprintf(f, "waves2_scalex=\"%g\" ", x->waves2_scalex);
         fprintf(f, "waves2_scaley=\"%g\" ", x->waves2_scaley);
         fprintf(f, "waves2_freqx=\"%g\" ", x->waves2_freqx);
         fprintf(f, "waves2_freqy=\"%g\" ", x->waves2_freqy);
      }

      fprintf(f, "coefs=\"");
      for (j = 0; j < 3; j++) {
         if (j) fprintf(f, " ");
         fprintf(f, "%g %g", x->c[j][0], x->c[j][1]);
      }
      fprintf(f, "\"");

      if (!id_matrix(x->post)) {
         fprintf(f, " post=\"");
         for (j = 0; j < 3; j++) {
            if (j) fprintf(f, " ");
            fprintf(f, "%g %g", x->post[j][0], x->post[j][1]);
         }
         fprintf(f, "\"");
      }

   }

   if (!final_flag && !motion_flag && !flam27_flag) {

      /* Print out the chaos row for this xform */
      int numcols = numstd;

      while (numcols > 0 && chaos_row[numcols-1]==1.0)
         numcols--;

      if (numcols>0) {
         fprintf(f, " chaos=\"");
         for (j=0;j<numcols;j++)
            fprintf(f, "%g ",chaos_row[j]);
         fprintf(f, "\"");
      }

      if (x->opacity<1.0)
         fprintf(f, " opacity=\"%g\"",x->opacity);
   }
}
"""


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
            self.xforms.append(XForm(xml_node=xform_node))


