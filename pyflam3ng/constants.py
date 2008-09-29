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

#NOTE: This file is meant to be imported like so
# from pyflam3ng.constants import *

flam3_defaults_on = (1)
flam3_defaults_off = (0)
flam3_name_len = 64
flam3_print_edits = (1)
flam3_dont_print_edits = (0)
flam3_variation_random = (-1)
flam3_variation_random_fromspecified = (-2)
flam3_nvariations = 54
flam3_nxforms = 12
flam3_parent_fn_len = 30
flam3_interpolation_linear = 0
flam3_interpolation_smooth = 1
flam3_inttype_linear = 0
flam3_inttype_log = 1
flam3_inttype_compat = 2
flam3_inttype_older = 3
flam3_palette_interpolation_hsv = 0
flam3_palette_interpolation_sweep = 1
flam3_max_action_length = 10000
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


flam3_VAR_LINEAR = 0
flam3_VAR_SINUSOIDAL = 1
flam3_VAR_SPHERICAL = 2
flam3_VAR_SWIRL = 3
flam3_VAR_HORSESHOE = 4
flam3_VAR_POLAR = 5
flam3_VAR_HANDKERCHIEF = 6
flam3_VAR_HEART = 7
flam3_VAR_DISC = 8
flam3_VAR_SPIRAL = 9
flam3_VAR_HYPERBOLIC = 10
flam3_VAR_DIAMOND = 11
flam3_VAR_EX = 12
flam3_VAR_JULIA = 13
flam3_VAR_BENT = 14
flam3_VAR_WAVES = 15
flam3_VAR_FISHEYE = 16
flam3_VAR_POPCORN = 17
flam3_VAR_EXPONENTIAL = 18
flam3_VAR_POWER = 19
flam3_VAR_COSINE = 20
flam3_VAR_RINGS = 21
flam3_VAR_FAN = 22
flam3_VAR_BLOB = 23
flam3_VAR_PDJ = 24
flam3_VAR_FAN2 = 25
flam3_VAR_RINGS2 = 26
flam3_VAR_EYEFISH = 27
flam3_VAR_BUBBLE = 28
flam3_VAR_CYLINDER = 29
flam3_VAR_PERSPECTIVE = 30
flam3_VAR_NOISE = 31
flam3_VAR_JULIAN = 32
flam3_VAR_JULIASCOPE = 33
flam3_VAR_BLUR = 34
flam3_VAR_GAUSSIAN_BLUR = 35
flam3_VAR_RADIAL_BLUR = 36
flam3_VAR_PIE = 37
flam3_VAR_NGON = 38
flam3_VAR_CURL = 39
flam3_VAR_RECTANGLES = 40
flam3_VAR_ARCH = 41
flam3_VAR_TANGENT = 42
flam3_VAR_SQUARE = 43
flam3_VAR_RAYS = 44
flam3_VAR_BLADE = 45
flam3_VAR_SECANT2 = 46
flam3_VAR_TWINTRIAN = 47
flam3_VAR_CROSS = 48
flam3_VAR_DISC2 = 49
flam3_VAR_SUPER_SHAPE = 50
flam3_VAR_FLOWER = 51
flam3_VAR_CONIC = 52
flam3_VAR_PARABOLA = 53


flam3_variations = {
        'linear': flam3_VAR_LINEAR,
        'sinusoidal': flam3_VAR_SINUSOIDAL,
        'spherical': flam3_VAR_SPHERICAL,
        'swirl': flam3_VAR_SWIRL,
        'horseshoe': flam3_VAR_HORSESHOE,
        'polar': flam3_VAR_POLAR,
        'handkerchief': flam3_VAR_HANDKERCHIEF,
        'heart': flam3_VAR_HEART,
        'disc': flam3_VAR_DISC,
        'spiral': flam3_VAR_SPIRAL,
        'hyperbolic': flam3_VAR_HYPERBOLIC,
        'diamond': flam3_VAR_DIAMOND,
        'ex': flam3_VAR_EX,
        'julia': flam3_VAR_JULIA,
        'bent': flam3_VAR_BENT,
        'waves': flam3_VAR_WAVES,
        'fisheye': flam3_VAR_FISHEYE,
        'popcorn': flam3_VAR_POPCORN,
        'exponential': flam3_VAR_EXPONENTIAL,
        'power': flam3_VAR_POWER,
        'cosine': flam3_VAR_COSINE,
        'rings': flam3_VAR_RINGS,
        'fan': flam3_VAR_FAN,
        'blob': flam3_VAR_BLOB,
        'pdj': flam3_VAR_PDJ,
        'fan2': flam3_VAR_FAN2,
        'rings2': flam3_VAR_RINGS2,
        'eyefish': flam3_VAR_EYEFISH,
        'bubble': flam3_VAR_BUBBLE,
        'cylinder': flam3_VAR_CYLINDER,
        'perspective': flam3_VAR_PERSPECTIVE,
        'noise': flam3_VAR_NOISE,
        'julian': flam3_VAR_JULIAN,
        'juliascope': flam3_VAR_JULIASCOPE,
        'blur': flam3_VAR_BLUR,
        'gaussian_blur': flam3_VAR_GAUSSIAN_BLUR,
        'radial_blur': flam3_VAR_RADIAL_BLUR,
        'pie': flam3_VAR_PIE,
        'ngon': flam3_VAR_NGON,
        'curl': flam3_VAR_CURL,
        'rectangles': flam3_VAR_RECTANGLES,
        'arch': flam3_VAR_ARCH,
        'tangent': flam3_VAR_TANGENT,
        'square': flam3_VAR_SQUARE,
        'rays': flam3_VAR_RAYS,
        'blade': flam3_VAR_BLADE,
        'secant2': flam3_VAR_SECANT2,
        'twintrian': flam3_VAR_TWINTRIAN,
        'cross': flam3_VAR_CROSS,
        'disc2': flam3_VAR_DISC2,
        'super_shape': flam3_VAR_SUPER_SHAPE,
        'flower': flam3_VAR_FLOWER,
         'conic': flam3_VAR_CONIC,
         'parabola': flam3_VAR_PARABOLA,
     }


