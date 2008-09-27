##############################################################################
#  The Combustion Flame Engine - pyflam3
#  http://combustion.sourceforge.net
#
#  Copyright (C) 2007 by Bobby R. Ward <bobbyrward@gmail.com>
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
from __future__ import with_statement
import sys
import os
from itertools import *
from pyflam3._flam3 import *
import pyflam3.marshal as marshal
import pyflam3._pyapi
from pyflam3._exceptions import *
import xml.etree.cElementTree as etree
import StringIO

def _fix_index(list_type, key):
    if key < 0:
        key += len(self)

    if key < 0 or key >= len(list_type):
        raise IndexError

    return key



class ImageComments(BaseImageComments):
    @classmethod
    def from_stats(cls, stats, genome):
        comments = cls()
        comments.genome = genome.to_string()
        comments.badvals = str(stats.badvals / float(stats.num_iters))
        comments.numiters = str(float(stats.num_iters))
        comments.rtime = str(stats.render_seconds)
        return comments

class Palette(BasePalette):
    def __getitem__(self, key):
        return self._vals.__getitem__(key)

    def __len__(self):
        return self._vals.__len__()

    def __setitem__(self, key, val):
        return self._vals.__setitem__(key, val)

    def __iter__(self):
        for item in self._vals:
            yield item

    def to_element(self, is_root=True, parent=None):
        # probably an easier way, but I'm not real
        # familiar with ElementTree and it probably
        # shows
        if is_root:
            root = etree.Element('palette')
        else:
            root = etree.SubElement(parent, 'palette')

        root.set('name', getattr(self, 'name', ''))
        root.set('title', getattr(self, 'title', ''))
        root.set('smooth', getattr(self, 'smooth', ''))

        for idx, (r, g, b) in enumerate(self):
            entry = etree.SubElement(root, 'entry')
            entry.set('index', str(idx))
            entry.set('r', str(r))
            entry.set('g', str(g))
            entry.set('b', str(b))

        return root

    def to_string(self):
        root = self.to_element(is_root=True)
        tree = etree.ElementTree(root)
        pseudo_fd = StringIO.StringIO()
        tree.write(pseudo_fd)
        return pseudo_fd.getvalue()

    @classmethod
    def from_element(cls, element):
        palette = cls()
        palette.name = element.get('name', '')
        palette.title = element.get('title', '')
        palette.smooth = element.get('smooth', '')

        for entry in element.findall('entry'):
            palette[int(entry.get('index'))] = (float(entry.get('r')),
                float(entry.get('g')), float(entry.get('b')))

        return palette

    @classmethod
    def from_string(cls, input):
        return cls.from_element(etree.fromstring(input))

    @classmethod
    def get_standard(cls, index=flam3_palette_random, hue_rotation=0):
        pal = Palette()
        flam3_get_palette(index, byref(pal), hue_rotation)
        return pal


class _VariationHelper(object):
    def __init__(self, parent):
        self._parent = parent

    def __len__(self):
        return flam3_nvariations

    def __iter__(self):
        for key in variations:
            yield key, self[key]

    def __setitem__(self, key, value):
        if isinstance(key, str):
            key = variations[key]

        if isinstance(key, int):
            self._parent.var[key] = value
        else:
            raise TypeError('key must be an int or string')

    def __getitem__(self, key):
        if isinstance(key, str):
            key = variations[key]

        if isinstance(key, int):
            return self._parent.var[key]
        else:
            raise TypeError('key must be an int or string')


class XForm(BaseXForm):
    def _get_variations(self):
        if not getattr(self, '_variations', None):
            self._variations = _VariationHelper(self)
        return self._variations

    variations = property(fget=_get_variations)

class _XFormHelper(object):
    def __init__(self, parent):
        self._parent = parent
        self._xforms = cast(parent.xform, POINTER(XForm))

    def __len__(self):
        return self._parent.num_xforms

    def __iter__(self):
        for i in range(0, self._parent.num_xforms):
            yield self._xforms[i]

    def __setitem__(self, key, value):
        if isinstance(key, int):
            self._xforms[_fix_index(self, key)] = value
        elif isinstance(key, slice):
            raise NotImplementedError('sorry, I suck and the usefulness'\
                                      'of slices here is questionable')
        else:
            raise TypeError('invalid key type')

    def __delitem__(self, key):
        if isinstance(key, int):
            self.remove(key)
        elif isinstance(key, slice):
            raise NotImplementedError('sorry, I suck and the usefulness'\
                                      'of slices here is questionable')
        else:
            raise TypeError('invalid key type')

    def __getitem__(self, key):
        if isinstance(key, int):
            return self._xforms[_fix_index(self, key)]
        elif isinstance(key, slice):
            raise NotImplementedError('sorry, I suck and the usefulness'\
                                      'of slices here is questionable')
        else:
            raise TypeError('invalid key type')

    def append(self, value=None):
        flam3_add_xforms(byref(self._parent), 1)
        if value:
            self._xforms[len(self) - 1] = value

    def remove(self, index):
        flam4_delete_xform(byref(self._parent), index)

class _FakedGenomeSize(object):
    def __init__(self, parent):
        self._parent = parent

    def __len__(self):
        return 2

    def __iter__(self):
        yield self._parent.width
        yield self._parent.height

    def __setitem__(self, key, value):
        if isinstance(key, int):
            if key == 0:
                self._parent.width = value
            elif key == 1:
                self._parent.height = value
            else:
                raise IndexError('key must be 0 or 1')
        else:
            raise TypeError('key must be an int')

    def __getitem__(self, key):
        if isinstance(key, int):
            if key == 0:
                return self._parent.width
            elif key == 1:
                return self._parent.height
            else:
                raise IndexError('key must be 0 or 1')
        else:
            raise TypeError('key must be an int')


class Genome(BaseGenome):
    def __init__(self, num_xforms=0):
        """allocate a new genome and add xform(s)"""
        if num_xforms:
            flam3_add_xforms(byref(self), num_xforms)

    def _get_xforms(self):
        if not getattr(self, '_xforms', None):
            self._xforms = _XFormHelper(self)
        return self._xforms
    xforms = property(fget=_get_xforms)

    def _get_size(self):
        if not getattr(self, '_faked_size', None):
            self._faked_size = _FakedGenomeSize(self)
        return self._faked_size

    def _set_size(self, value):
        self.width, self.height = value

    size = property(fget=_get_size, fset=_set_size)

    def _get_rot_center(self):
        return self.rot_center

    def _set_rot_center(self, value):
        self.rot_center[0], self.rot_center[1] = value

    rotation_center = property(fget=_get_rot_center, fset=_set_rot_center)

    def _get_center(self):
        return self._center

    def _set_center(self, value):
        self._center[0], self._center[1] = value

    center = property(fget=_get_center, fset=_set_center)

    def _get_background(self):
        return self.background

    def _set_background(self, value):
        bg = self.background
        bg[0], bg[1], bg[2] = value

    bgcolor = property(fget=_get_background, fset=_set_background)

    def clone(self):
        other = Genome()
        flam3_copy(byref(other), byref(self))
        return other

    def render(self, **kwargs):
        channels = kwargs.get('channels', 3)
        transparent = kwargs.get('transparent', False) and 1 or 0

        frame = Frame(**kwargs)
        frame.genomes = cast(pointer(self), POINTER(BaseGenome))
        frame.ngenomes = 1

        output_buffer = kwargs.get('buffer', None)
        if output_buffer:
            if isinstance(output_buffer, buffer):
                # standard write buffer objects
                # allows rendering directly to wxPython Images
                # through the DataBuffer object
                ptr = c_void_p()
                len = _pyapi.Py_ssize_t()
                _pyapi.PyObject_AsWriteBuffer(output_buffer, byref(ptr), byref(len))
                if len < (self.width * self.height * channels):
                    raise BufferTooSmallError("buffer isn't large enough")
                output_buffer = cast(ptr, POINTER(c_ubyte))

            # otherwise...
            # try and pass it in, ctypes will tell us if it won't work
        else:
            output_buffer = allocate_output_buffer(self.size, channels)

        stats = RenderStats()
        flam3_render(byref(frame), output_buffer, self.width, flam3_field_both, channels, transparent, byref(stats))

        return (output_buffer, stats)

    def to_string(self):
        return flam3_print_to_string(byref(self))

    def to_file(self, filename, fd=None):
        if 'win32' in sys.platform:
            if fd:
                fd.write(self.to_string())
            else:
                with open(filename, 'wb') as fd:
                    fd.write(self.to_string())
        else:
            if fd:
                flam3_print(marshal.file_as_FILE(fd), byref(self), None, flam3_dont_print_edits)
            else:
                with open(filename, 'wb') as fd:
                    flam3_print(marshal.file_as_FILE(fd), byref(self), None, flam3_dont_print_edits)

    @classmethod
    def _initialize_genome_list(cls, genomes):
        for i in range(0, len(genomes)):
            if not genomes[i].name:
                genomes[i].name = '%s-%d' % (genomes[i].parent_fname, i)


    @classmethod
    def from_string(cls, input_buffer, filename='<unknown>', defaults=True):
        ncps = c_int()

        #print 'Buffer = ', input_buffer

        # so, flam3_parse_xml2 actually free's the buffer passed in...
        # this hackery sucks but...meh
        c_buffer = marshal.from_string(input_buffer)

        #print string_at(c_buffer)

        result = flam3_parse_xml2(c_buffer, filename,
                defaults and flam3_defaults_on or flam3_defaults_off, byref(ncps))

        genomes = []
        for i in xrange(0, ncps.value):
            genome = cls()
            memmove(byref(genome), byref(result[i]), sizeof(BaseGenome))
            genomes.append(genome)

        #Don't free the input, flam3 already does this.
        #flam3_free(c_buffer)
        flam3_free(result)

        cls._initialize_genome_list(genomes)

        return genomes


    @classmethod
    def from_file(cls, filename=None, handle=None, defaults=True):
        ncps = c_int()

        def open_file(handle):
            return flam3_parse_from_file(marshal.file_as_FILE(handle),
                    os.path.basename(handle.name),
                    defaults and flam3_defaults_on or flam3_defaults_off,
                    byref(ncps))

        if not handle and filename:
            with open(filename, 'rb') as handle:
                if 'win32' in sys.platform:
                    content = handle.read()
                    return cls.from_string(content,
                            filename=os.path.basename(filename))
                else:
                    result = open_file(handle)
        elif handle:
            if 'win32' in sys.platform:
                content = handle.read()
                genomes = cls.from_string(content)
                return cls.from_string(content,
                        filename=os.path.basename(filename))
            else:
                result = open_file(handle)
        else:
            raise IOError('Unable to open file')

        result = cast(result, POINTER(cls))

        genomes = []
        for i in xrange(0, ncps.value):
            genome = cls()
            memmove(byref(genome), byref(result[i]), sizeof(BaseGenome))
            genomes.append(genome) #result[i])

        flam3_free(result)

        cls._initialize_genome_list(genomes)

        return genomes

    @classmethod
    def random(cls, variations=None, symmetry=0, num_xforms=0):
        if variations:
            var_int_array = (c_int * len(variations))()

            for var_name, dest_idx in izip(variations, count()):
                import pyflam3.variations as _variations
                var_int_array[dest_idx] = _variations[var_name]
        else:
            var_int_array = (c_int * 1)()
            var_int_array[0] = flam3_variation_random

        genome = cls()
        flam3_random(genome, var_int_array, len(var_int_array), symmetry,
                num_xforms)

        from datetime import datetime
        genome.name = 'CFE-Random %s' % \
                datetime.now().strftime('%m-%d-%y %H:%M')

        return genome



class Frame(BaseFrame):
    def __init__(self, **kwargs):
        super(BaseFrame, self).__init__()
        flam3_init_frame(byref(self))

        self.pixel_aspect_ratio = kwargs.get('aspect', 1.0)
        self.temporal_filter_radius = kwargs.get('filter', 0.4)
        self.ngenomes = 0
        self.verbose = kwargs.get('verbose', False) and 1 or 0
        self.bits = kwargs.get('bits', 33)
        self.time = kwargs.get('time', 0)

        progress = kwargs.get('progress_func', None)
        if callable(progress):
            self.progress = ProgressFunction(progress)
        else:
            self.progress = ProgressFunction()

        param = kwargs.get('progress_param', None)
        if param:
            if not isinstance(param, py_object):
                self.progress_parameter = py_object(param)
            else:
                self.progress_parameter = param


        self.nthreads = kwargs.get('nthreads', 0)
        if not self.nthreads:
            self.nthreads = flam3_count_nthreads()



def write_flam3_file(filename, genomes):
    if 'win32' in sys.platform:
        with open(filename, 'wb') as fd:
            for genome in genomes:
                fd.write(genome.to_string())
    else:
        with open(filename, 'wb') as fd:
            for genome in genomes:
                flam3_print(marshal.file_as_FILE(fd), byref(genome), None, flam3_dont_print_edits)




# void write_jpeg(FILE *file, unsigned char *image, int width, int height, flam3_img_comments *fpc);
# void write_png(FILE *file, unsigned char *image, int width, int height, flam3_img_comments *fpc);
def write_image(filename, buffer, size, comments=None):
    if 'win32' in sys.platform:
        raise NotImplementedError('write_image is not supported under windows'\
                ' at this time')

    if not comments:
        comments = ImageComments()
        comments.genome = None
        comments.badvals = None
        comments.numiters = None
        comments.rtime = None

    if filename.endswith('png'):
        write_func = write_png
    elif filename.endswith('jpg') or filename.endswith('jpeg'):
        write_func = write_jpeg
    else:
        assert False

    with open(filename, 'wb') as fd:
        write_func(marshal.file_as_FILE(fd), buffer, size[0], size[1], comments)

def random_seed(seed=None):
    if seed is None:
        import time
        seed = hash(time.time())

    flam3_srandom(seed)


