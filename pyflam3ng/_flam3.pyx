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

cimport _flam3
import xml.etree.cElementTree as etree
import StringIO
import os


cdef int PyString_Check(object op):
    return isinstance(op, str)


cdef void* _malloc(size):
    cdef void *p
    p = flam3_malloc(size)
    return memset(p, 0, size)


# Assumes you created a buffer big enough...
cdef char* _copy_str_to_buffer(char* dest_str, object source_str, int max_len):
    if not PyString_Check(source_str) or source_str is None:
        raise TypeError("Expected a string value received %r" % source_str)

    strncpy(dest_str, source_str, max_len)

    return dest_str


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


cdef int _fix_index(object list_type, int key):
    if key < 0:
        key += len(list_type)

    if key < 0 or key >= len(list_type):
        raise IndexError

    return key



cdef class RenderStats:
    cdef stat_struct *_stats

    def __cinit__(self):
        self._stats = <stat_struct*>_malloc(sizeof(stat_struct))

    def __dealloc__(self):
        flam3_free(self._stats)

    property badvals:
        def __get__(self):
           return self._stats.badvals

    property num_iters:
        def __get__(self):
           return self._stats.num_iters

    property render_seconds:
        def __get__(self):
           return self._stats.render_seconds


cdef class Frame:
    cdef flam3_frame* _frame

    def __cinit__(self, **kwargs):
        self._frame = <flam3_frame*>_malloc(sizeof(flam3_frame));
        flam3_init_frame(self._frame)

        self._frame.pixel_aspect_ratio = kwargs.get('aspect', 1.0)
        self._frame.ngenomes = 0
        self._frame.verbose = kwargs.get('verbose', False) and 1 or 0
        self._frame.bits = kwargs.get('bits', 33)
        self._frame.time = kwargs.get('time', 0)

        #progress = kwargs.get('progress_func', None)
        #if callable(progress):
            #print "progress == OK"
        #else:
            #print "progress != OK"

        #param = kwargs.get('progress_param', None)
        #if param:
            #if not isinstance(param, py_object):
                #self.progress_parameter = py_object(param)
            #else:
                #self.progress_parameter = param


        self._frame.nthreads = kwargs.get('nthreads', 0)

        if not self._frame.nthreads:
            self._frame.nthreads = flam3_count_nthreads()

    def __dealloc__(self):
        flam3_free(self._frame)

    property pixel_aspect_ratio:
        def __get__(self):
            return self._frame.pixel_aspect_ratio


cdef void _initialize_genome_list(list genome_list):
    for idx, genome in enumerate(genome_list):
        if not genome_list[idx].name:
            genome_list[idx].name = '%s-%d' % (genome_list[idx].parent_fname, idx)


cdef class CoefficientsSubHelper:
    cdef flam3_xform* _xform
    cdef int _parent_index

    cdef void set_xform(self, int parent_index, flam3_xform* xform):
        self._xform = xform
        self._parent_index = parent_index

    def __len__(self):
        return 2

    def __getitem__(self, int key):
        return self._xform.c[self._parent_index][_fix_index(self, key)]

    def __setitem__(self, int key, int value):
        self._xform.c[self._parent_index][_fix_index(self, key)] = value


cdef class CoefficientsHelper:
    cdef flam3_xform* _xform

    cdef void set_xform(self, flam3_xform* xform):
        self._xform = xform

    def __len__(self):
        return 3

    def __getitem__(self, int key):
        key = _fix_index(self, key)

        cdef CoefficientsSubHelper sub = CoefficientsSubHelper()

        sub.set_xform(key, self._xform)

        return sub


cdef class XForm:
    cdef flam3_xform* _xform

    def __cinit__(self):
        pass

    cdef void set_xform(self, flam3_xform* xform):
        self._xform = xform


    property c:
        def __get__(self):
            cdef CoefficientsHelper coeffs = CoefficientsHelper()

            coeffs.set_xform(self._xform)

            return coeffs


#   double var[flam3_nvariations];   /* interp coefs between variations */
#   double c[3][2];      /* the coefs to the affine part of the function */
#   double post[3][2];   /* the post transform */
#   double density;      /* probability that this function is chosen. 0 - 1 */
#   double color[2];     /* color coords for this function. 0 - 1 */
#   double symmetry;     /* 1=this is a symmetry xform, 0=not */
#   
#   int padding;/* Set to 1 for padding xforms */
#   double wind[2]; /* winding numbers */


cdef class _XFormProxy:
    cdef flam3_genome* _parent

    def __cinit__(self):
        pass

    cdef void set_genome(self, flam3_genome* parent):
        self._parent = parent

    def __len__(self):
        return self._parent.num_xforms

    def __getitem__(self, int key):
        key = _fix_index(self, key)

        cdef XForm xform

        xform = XForm()
        xform.set_xform(&self._parent.xform[key])

        return xform



cdef class Genome:
    cdef flam3_genome* _genome
    cdef _XFormProxy _xforms

    def __cinit__(self, int num_xforms=0):
        self._genome = <flam3_genome*>_malloc(sizeof(flam3_genome));
        self._xforms = _XFormProxy()
        self._xforms.set_genome(self._genome)

        if num_xforms:
            flam3_add_xforms(self._genome, num_xforms, 0, 0)

    cdef void copy_genome(self, flam3_genome* genome):
        memmove(self._genome, genome, sizeof(flam3_genome))

    def __dealloc(self):
        flam3_free(self._genome)


    def clone(self):
        cdef Genome other = Genome()

        flam3_copy(other._genome, self._genome)

        return other

    def to_string(self):
        cdef char* c_string = flam3_print_to_string(self._genome)
        cdef object py_string = str(c_string)

        flam3_free(c_string)

        return py_string

    def to_file(self, filename, fd=None):
        if fd is not None:
            fd.write(self.to_string())
        else:
            with open(filename, 'wb') as fd:
                fd.write(self.to_string())

    @classmethod
    def from_file(cls, object filename=None, object file_like_object=None, object defaults=True):
        cdef object content = ''

        if file_like_object:
            content = file_like_object.read()
        elif filename:
            fd = open(filename, 'rb')

            try:
                content = fd.read()
            finally:
                fd.close()
        else:
            raise IOError('Unable to open file')

        return cls.from_string(content, os.path.basename(filename), defaults)

    @classmethod
    def from_string(cls, object input_buffer, object filename='<unknown>', object defaults=True):
        cdef int ncps = 0
        cdef char* c_buffer_copy
        cdef flam3_genome* result
        cdef list genome_list = list()
        cdef Genome genome

        if filename is None or not PyString_Check(input_buffer):
            return TypeError('filename  must be an str object')

        ##HACK: so, flam3_parse_xml2 actually free's the buffer passed in...ick
        c_buffer_copy =  _create_str_copy(input_buffer)

        result = flam3_parse_xml2(c_buffer_copy, filename,
                flam3_defaults_on if defaults else flam3_defaults_off, &ncps)

        for 0 <= i < ncps:
            genome = cls()
            genome.copy_genome(&result[i])
            genome_list.append(genome)

        ##NOTE: Don't free the input, flam3 already does this.
        ##NOTE: Still need to free the result though.
        flam3_free(result)

        _initialize_genome_list(genome_list)

        return genome_list


    property xforms:
        def __get__(self):
            return self._xforms

    property size:
        def __get__(self):
            return (self._genome.width, self._genome.height)

        def __set__(self, value):
            self._genome.width, self._genome.height = value

    property rotation_center:
        def __get__(self):
            return (self._genome.rot_center[0], self._genome.rot_center[1])

        def __set__(self, value):
            self._genome.rot_center[0], self._genome.rot_center[1] = value

    property bgcolor:
        def __get__(self):
            return (self._genome.background[0], self._genome.background[1], self._genome.background[2])

        def __set__(self, value):
            self._genome.background[0], self._genome.background[1], self._genome.background[2] = value

    property name:
        def __get__(self):
            return self._genome.flame_name

        def __set__(self, char* value):
            strncpy(self._genome.flame_name, value, flam3_name_len+1)

    property time:
        def __get__(self):
            return self._genome.time

        def __set__(self, double time):
            self._genome.time = time
            
    property interpolation:
        def __get__(self):
            return self._genome.interpolation

        def __set__(self, int value):
            if value != flam3_interpolation_linear and value != flam3_interpolation_smooth:
                raise ValueError('must be one of flam3_interpolation_linear  or flam3_interpolation_smooth')

            self._genome.interpolation = value

    property interpolation_type:
        def __get__(self):
            return self._genome.interpolation_type

        def __set__(self, int value):
            if value not in (flam3_inttype_linear, flam3_inttype_log, flam3_inttype_compat, flam3_inttype_older):
                raise ValueError('must be one of flam3_inttype_linear, flam3_inttype_log, flam3_inttype_compat or flam3_inttype_older')

            self._genome.interpolation_type = value

    property palette_interpolation:
        def __get__(self):
            return self._genome.palette_interpolation

        def __set__(self, int value):
            if value not in ( flam3_palette_interpolation_hsv, flam3_palette_interpolation_sweep ):
                raise ValueError('must be one of flam3_palette_interpolation_hsv, flam3_palette_interpolation_sweep')

            self._genome.palette_interpolation = value 

    property genome_index:
        def __get__(self):
            return self._genome.genome_index

        def __set__(self, int value):
            if value < 0:
                raise ValueError('must be a positive integer')

            self._genome.genome_index = value

    property parent_fname:
        def __get__(self):
            return self._genome.parent_fname

        def __set__(self, char* value):
            strncpy(self.parent_fname, value, flam3_parent_fn_len)

    property symmetry:
        def __get__(self):
            return self._genome.symmetry

        def __set__(self, int value):
            self._genome.symmetry = value

    property brightness:
        def __get__(self):
            return self._genome.brightness

        def __set__(self, double value):
            self._genome.brightness = value

    property contrast:
        def __get__(self):
            return self._genome.contrast

        def __set__(self, double value):
            self._genome.contrast = value

    property gamma:
        def __get__(self):
            return self._genome.gamma

        def __set__(self, double value):
            self._genome.gamma = value

    property oversample:
        def __get__(self):
            return self._genome.spatial_oversample

        def __set__(self, int  value):
            self._genome.spatial_oversample = value

    property rotation:
        def __get__(self):
            return self._genome.rotate

        def __set__(self, double value):
            self._genome.rotate = value

    property vibrancy:
        def __get__(self):
            return self._genome.vibrancy

        def __set__(self, double value):
            self._genome.vibrancy = value

    property hue_rotation:
        def __get__(self):
            return self._genome.hue_rotation

        def __set__(self, double value):
            self._genome.hue_rotation = value

    property zoom:
        def __get__(self):
            return self._genome.zoom

        def __set__(self, double value):
            self._genome.zoom = value

    property pixels_per_unit:
        def __get__(self):
            return self._genome.pixels_per_unit

        def __set__(self, double value):
            self._genome.pixels_per_unit = value

    property spatial_filter_radius:
        def __get__(self):
            return self._genome.spatial_filter_radius

        def __set__(self, double value):
            self._genome.spatial_filter_radius = value

    property spatial_filter_select:
        def __get__(self):
            return self._genome.spatial_filter_select

        def __set__(self, int value):
            self._genome.spatial_filter_select = value

    property sample_density:
        def __get__(self):
            return self._genome.sample_density

        def __set__(self, double value):
            self._genome.sample_density = value

    property nbatches:
        def __get__(self):
            return self._genome.nbatches

        def __set__(self, int value):
            self._genome.nbatches = value

    property ntemporal_samples:
        def __get__(self):
            return self._genome.ntemporal_samples

        def __set__(self, int value):
            self._genome.ntemporal_samples = value

    property estimator:
        def __get__(self):
            return self._genome.estimator

        def __set__(self, double value):
            self._genome.estimator = value

    property estimator_curve:
        def __get__(self):
            return self._genome.estimator_curve

        def __set__(self, double value):
            self._genome.estimator_curve = value

    property estimator_minimum:
        def __get__(self):
            return self._genome.estimator_minimum

        def __set__(self, double value):
            self._genome.estimator_minimum = value

    property gamma_linear_threshold:
        def __get__(self):
            return self._genome.gam_lin_thresh

        def __set__(self, double value):
            self._genome.gam_lin_thresh = value

    property temporal_filter_type:
        def __get__(self):
            return self._genome.temporal_filter_type

        def __set__(self, int value):
            self._genome.temporal_filter_type = value

    property temporal_filter_width:
        def __get__(self):
            return self._genome.temporal_filter_width

        def __set__(self, double value):
            self._genome.temporal_filter_width = value

    property temporal_filter_exp:
        def __get__(self):
            return self._genome.temporal_filter_exp

        def __set__(self, double value):
            self._genome.temporal_filter_exp = value

#        int final_xform_index
#        int final_xform_enable
#        flam3_palette palette
#        char *input_image
#        int  palette_index
#        double center[2]
#        int palette_index0
#        double hue_rotation0
#        int palette_index1
#        double hue_rotation1
#        double palette_blend
#



cdef class Palette:
    cdef flam3_palette _pal
    cdef object _name
    cdef object _title
    cdef object _smooth

    def __init__(self):
        self._name = ''
        self._title = ''
        self._smooth = ''

    property name:
        def __get__(self): return self._name
        def __set__(self, val): self._name = val

    property title:
        def __get__(self): return self._title
        def __set__(self, val): self._title = val

    property smooth:
        def __get__(self): return self._smooth
        def __set__(self, val): self._smooth = val

    def __getitem__(self, key):
        #return self._pal[key]
        pass

    def __len__(self):
        return 256

    def __setitem__(self, key, val):
        #self._pal[key][0] = val[0]
        #self._pal[key][1] = val[1]
        #self._pal[key][2] = val[2]
        pass

    def __iter__(self):
        return _PaletteIterator(self)

    def to_element(self, is_root=True, object parent=None):
        # probably an easier way, but I'm not real
        # familiar with ElementTree and it probably
        # shows
        if is_root:
            root = etree.Element('palette')
        else:
            root = etree.SubElement(parent, 'palette')

        root.set('name', getattr3(self, 'name', ''))
        root.set('title', getattr3(self, 'title', ''))
        root.set('smooth', getattr3(self, 'smooth', ''))

        for idx, (r, g, b) in enumerate(self):
            entry = etree.SubElement(root, 'entry')
            entry.set('index', str(idx))
            entry.set('r', str(r))
            entry.set('g', str(g))
            entry.set('b', str(b))

        return root

    def from_element(object cls, object element):
        palette = cls()
        setattr(palette, 'name', element.get('name', ''))
        setattr(palette, 'title', element.get('title', ''))
        setattr(palette, 'smooth', element.get('smooth', ''))

        for entry in element.findall('entry'):
            palette[int(entry.get('index'))] = (float(entry.get('r')),
                float(entry.get('g')), float(entry.get('b')))

        return palette

    from_element = classmethod(from_element)

    def from_string(cls, input):
        return cls.from_element(etree.fromstring(input))

    from_string = classmethod(from_string)

    def to_string(self):
        root = self.to_element(is_root=True)
        tree = etree.ElementTree(root)
        pseudo_fd = StringIO.StringIO()
        tree.write(pseudo_fd)
        return pseudo_fd.getvalue()


cdef class _PaletteIterator:
    cdef int _index
    cdef Palette _palette

    def __cinit__(self, palette):
        self._index = 0
        self._palette = palette

    def __next__(self):
        if self._index >= 256:
            raise StopIteration()

        x = self._palette.__getitem__(self._index)

        self._index = self._index + 1

        return x


def standard_palette(int index=flam3_palette_random, double hue_rotation=0):
    cdef Palette pal
    
    pal = Palette()
    
    flam3_get_palette(index, pal._pal, hue_rotation)

    return pal

def random_seed(object seed=None):
    flam3_srandom()



