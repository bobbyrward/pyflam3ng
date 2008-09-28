cimport _flam3
import xml.etree.cElementTree as etree
import StringIO

cdef void* _malloc(size):
    cdef void *p
    p = flam3_malloc(size)
    return memset(p, 0, size)


cdef class ImageComments:
    cdef flam3_img_comments *_comments

    def __cinit__(self):
        self._comments = <flam3_img_comments*>_malloc(sizeof(flam3_img_comments))

        self._comments.genome = ''
        self._comments.badvals = ''
        self._comments.numiters = ''
        self._comments.rtime = ''

    def __dealloc__(self):
        flam3_free(self._comments)

    property genome:
        def __get__(self):
            return self._comments.genome

    property badvals:
        def __get__(self):
            return self._comments.badvals

    property numiters:
        def __get__(self):
            return self._comments.numiters

    property rtime:
        def __get__(self):
            return self._comments.rtime


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
        return (self._pal[key][0], self._pal[key][1], self._pal[key][2])

    def __len__(self):
        return 256

    def __setitem__(self, key, val):
        self._pal[key][0] = val[0]
        self._pal[key][1] = val[1]
        self._pal[key][2] = val[2]

    def __iter__(self):
        return _PaletteIterator(self)

    def to_element(self, is_root=True, parent=None):
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

    def from_element(cls, element):
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


def standard_palette(index=flam3_palette_random, hue_rotation=0):
    cdef Palette pal
    
    pal = Palette()
    
    flam3_get_palette(index, <double (*)[3]>&pal._pal, hue_rotation)

    return pal







