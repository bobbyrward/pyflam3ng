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
cimport numpy as np
cimport stdlib

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


cdef int PyString_Check(object op):
    return isinstance(op, str)


cdef void* _malloc(size):
    cdef void *p = flam3_malloc(size)
    return memset(p, 0, size)


#Return value needs to be freed using flam3_free
cdef char* _create_str_copy(object source_str):
    if not PyString_Check(source_str) or source_str is None:
        raise TypeError("Expected a string value received %r" % source_str)

    cdef int string_len = strlen(source_str)

    cdef char* c_string = source_str
    cdef char* c_buffer_copy = <char*>flam3_malloc(string_len + 1)

    if c_buffer_copy == NULL:
        raise MemoryError('Unable to allocate copy of input buffer')

    return strncpy(c_buffer_copy, c_string, string_len + 1)


def random_seed():
    flam3_srandom()


cdef class RenderBuffer:
    cdef unsigned char* _buffer
    cdef int _bytes_per_pixel
    cdef unsigned int _width
    cdef unsigned int _height

    def __cinit__(RenderBuffer self):
        self._buffer = NULL

    cpdef resize(RenderBuffer self, unsigned int width, unsigned int height, int channels):
        if self._width != width and self._height != height and self._bytes_per_pixel != channels:
            self._bytes_per_pixel = channels
            self._width = width
            self._height = height

            self._buffer = <unsigned char*>stdlib.realloc(self._buffer, width * height * self._bytes_per_pixel)

    def write_to_legacy_buffer(RenderBuffer self, object legacy_buffer):
        if self._buffer == NULL:
            raise RuntimeError('Buffer is empty')

        cdef unsigned char* dest_p = NULL
        cdef Py_ssize_t dest_len = 0
        cdef Py_ssize_t total_len = self._width * self._height * self._bytes_per_pixel

        PyObject_AsWriteBuffer(legacy_buffer, <void**>&dest_p, &dest_len)

        if dest_len < total_len:
            raise BufferError("buffer isn't large enough")

        memmove(dest_p, self._buffer, total_len)

    property width:
        def __get__(RenderBuffer self):
            return self._width

    property height:
        def __get__(RenderBuffer self):
            return self._height

    property channels:
        def __get__(RenderBuffer self):
            return self._bytes_per_pixel

    property size_in_bytes:
        def __get__(RenderBuffer self):
            return self._width * self._height * self._bytes_per_pixel

    def __dealloc__(RenderBuffer self):
        if self._buffer != NULL:
            stdlib.free(self._buffer)
            self._buffer = NULL


cdef int __render_callback(void *context, double progress, int stage, double eta) with gil:
    if context != NULL and (<object>context) is not None:
        return <int>(<object>context)(progress, stage, eta)


cdef class GenomeHandle:
    cdef flam3_genome* _genome

    def __cinit__(self):
        self._genome = <flam3_genome*>_malloc(sizeof(flam3_genome));

    def random(GenomeHandle self, list variations, bint symmetry, int num_xforms):
        cdef list variation_list = get_variation_list()
        cdef int num_variations = len(variations)
        cdef int *vars = <int*>stdlib.malloc(sizeof(int) * num_variations)

        for idx, var_name in enumerate(variations):
            try:
                var_idx = variation_list.index(var_name)
            except ValueError:
                raise KeyError('unknown variation: "%s"' % var_name)

            vars[idx] = var_idx

        flam3_random(self._genome, vars, num_variations, symmetry, num_xforms)

        stdlib.free(vars)

    cdef void copy_genome(self, flam3_genome* genome):
        memmove(self._genome, genome, sizeof(flam3_genome))

    def __dealloc(self):
        flam3_free(self._genome)

    def clone(self):
        cdef GenomeHandle other = GenomeHandle()
        flam3_copy(other._genome, self._genome)
        return other

    cdef _render(GenomeHandle self, void *out_buffer, unsigned int channels, int transparent, object progress, 
            double pixel_aspect_ratio, int bits, double time, int nthreads):

        cdef flam3_frame frame
        cdef stat_struct stats
        cdef dict py_stats = dict()
        cdef int c_flam3_field_both = flam3_field_both

        flam3_init_frame(&frame)

        self._genome.ntemporal_samples = 1
        self._genome.nbatches = 1

        frame.genomes = self._genome
        frame.ngenomes = 1
        frame.verbose = 0
        frame.earlyclip = 0
        frame.pixel_aspect_ratio = pixel_aspect_ratio
        frame.bits = bits
        frame.bytes_per_channel = 1
        frame.time = time
        frame.nthreads = nthreads

        if progress is not None:
            frame.progress = __render_callback
            frame.progress_parameter = <void*>progress
        else:
            frame.progress = NULL
            frame.progress_parameter = NULL

        with nogil:
            if frame.nthreads == 0:
                frame.nthreads = flam3_count_nthreads()

            flam3_render(&frame, out_buffer, c_flam3_field_both, channels, transparent, &stats)

        py_stats['badvals'] = stats.badvals
        py_stats['num_iters'] = stats.num_iters
        py_stats['render_seconds'] = stats.render_seconds

        return py_stats

    def render(self, RenderBuffer out_buffer, **kwargs):
        cdef int transparent = <int>kwargs.get('transparent', 0)
        cdef void *data = out_buffer._buffer
        cdef unsigned int channels = out_buffer._bytes_per_pixel
        cdef object progress = kwargs.get('progress', None)
        cdef double pixel_aspect_ratio = <double>kwargs.get('pixel_aspect_ratio', 1.0)
        cdef int bits = <int>kwargs.get('bits', 33)
        cdef double time = <double>kwargs.get('time', 0.0)
        cdef int nthreads = <int>kwargs.get('nthreads', 0)

        self._genome.width = out_buffer.width
        self._genome.height = out_buffer.height

        return self._render(data, channels, transparent, progress, pixel_aspect_ratio, bits, time, nthreads)


def get_variation_list():
    cdef list var_list = list()
    cdef int idx

    for idx in range(flam3_nvariations):
        var_list.append(flam3_variation_names[idx])

    return var_list


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

