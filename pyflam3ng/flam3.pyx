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

cimport flam3

flam3_nvariations = c_flam3_nvariations
flam3_parent_fn_len = c_flam3_parent_fn_len
flam3_name_len = c_flam3_name_len

flam3_palette_random = (-1)
flam3_palette_interpolated = (-2)
flam3_defaults_on = (1)
flam3_defaults_off = (0)
flam3_print_edits = (1)
flam3_dont_print_edits = (0)
flam3_variation_random = (-1)
flam3_variation_random_fromspecified = (-2)
flam3_nxforms = 12
flam3_interpolation_linear = 0
flam3_interpolation_smooth = 1
flam3_inttype_linear = 0
flam3_inttype_log = 1
flam3_inttype_compat = 2
flam3_inttype_older = 3
flam3_palette_interpolation_hsv = 0
flam3_palette_interpolation_sweep = 1
flam3_max_action_length = 10000
flam3_field_both = 0
flam3_field_even = 1
flam3_field_odd = 2
flam3_palette_mode_step   = 0
flam3_palette_mode_linear = 1


VAR_LINEAR = 0
VAR_SINUSOIDAL = 1
VAR_SPHERICAL = 2
VAR_SWIRL = 3
VAR_HORSESHOE = 4
VAR_POLAR = 5
VAR_HANDKERCHIEF = 6
VAR_HEART = 7
VAR_DISC = 8
VAR_SPIRAL = 9
VAR_HYPERBOLIC = 10
VAR_DIAMOND = 11
VAR_EX = 12
VAR_JULIA = 13
VAR_BENT = 14
VAR_WAVES = 15
VAR_FISHEYE = 16
VAR_POPCORN = 17
VAR_EXPONENTIAL = 18
VAR_POWER = 19
VAR_COSINE = 20
VAR_RINGS = 21
VAR_FAN = 22
VAR_BLOB = 23
VAR_PDJ = 24
VAR_FAN2 = 25
VAR_RINGS2 = 26
VAR_EYEFISH = 27
VAR_BUBBLE = 28
VAR_CYLINDER = 29
VAR_PERSPECTIVE = 30
VAR_NOISE = 31
VAR_JULIAN = 32
VAR_JULIASCOPE = 33
VAR_BLUR = 34
VAR_GAUSSIAN_BLUR = 35
VAR_RADIAL_BLUR = 36
VAR_PIE = 37
VAR_NGON = 38
VAR_CURL = 39
VAR_RECTANGLES = 40
VAR_ARCH = 41
VAR_TANGENT = 42
VAR_SQUARE = 43
VAR_RAYS = 44
VAR_BLADE = 45
VAR_SECANT2 = 46
VAR_TWINTRIAN = 47
VAR_CROSS = 48
VAR_DISC2 = 49
VAR_SUPER_SHAPE = 50
VAR_FLOWER = 51
VAR_CONIC = 52
VAR_PARABOLA = 53

flam3_gaussian_kernel = 0
flam3_hermite_kernel = 1
flam3_box_kernel = 2
flam3_triangle_kernel = 3
flam3_bell_kernel = 4
flam3_b_spline_kernel = 5
flam3_lanczos3_kernel = 6
flam3_lanczos2_kernel = 7
flam3_mitchell_kernel = 8
flam3_blackman_kernel = 9
flam3_catrom_kernel = 10
flam3_hamming_kernel = 11
flam3_hanning_kernel = 12
flam3_quadratic_kernel = 13
flam3_temporal_box = 0
flam3_temporal_gaussian = 1
flam3_temporal_exp = 2


def random_seed():
    flam3_srandom()


cdef class GenomeHandle:
    cdef flam3_genome* _genome

    def __cinit__(self):
        self._genome = <flam3_genome*>_malloc(sizeof(flam3_genome));

    cdef void copy_genome(self, flam3_genome* genome):
        memmove(self._genome, genome, sizeof(flam3_genome))

    def __dealloc(self):
        flam3_free(self._genome)

    def clone(self):
        cdef GenomeHandle other = GenomeHandle()
        flam3_copy(other._genome, self._genome)
        return other


def from_xml(str xml_source, str filename='', object defaults=True):
    cdef flam3_genome *result
    cdef int ncps = 0
    cdef char *c_buffer_copy = _create_str_copy(xml_source)
    cdef list result_list = list()
    cdef GenomeHandle handle

    result = flam3_parse_xml2(c_buffer_copy, filename, flam3_defaults_on if defaults else flam3_defaults_off, &ncps)

    for idx in range(ncps):
        handle = GenomeHandle()
        handle.copy_genome(&result[idx])
        result_list.append(handle)

    flam3_free(result)

    return result_list


def to_xml(GenomeHandle genome):
    cdef char* c_string = flam3_print_to_string(genome._genome)
    cdef str py_string = str(c_string)

    flam3_free(c_string)

    return py_string

