import sys
import IPython.ipapi
import wx


#sys.path.append('/path/to/pyflam3ng')

# null@voidstar:~$  ipython -wthread
# Python 2.5.4 (r254:67916, May 19 2009, 00:22:31)
# Type "copyright", "credits" or "license" for more information.
#
# IPython 0.9.1 -- An enhanced Interactive Python.
# ?         -> Introduction and overview of IPython's features.
# %quickref -> Quick reference.
# help      -> Python's own help system.
# object?   -> Details about 'object'. ?object also works, ?? prints more.
#
# In [1]: import ipy_pyflam3ng
#
# In [2]: import pyflam3ng
#
# In [3]: genomes = pyflam3ng.load_flame(filename='../flam3-early-clip/test.flam3')
#
# In [4]: %wxrender genomes[0]
# filtering: 99.60%
#
# In [5]:



import pyflam3ng


ip = IPython.ipapi.get()


def wxrender(self, arg):
    def progress(progress, stage, eta):
        sys.stdout.write('%s: %0.2f%%\r' % ('chaos' if stage == 0 else 'filtering', progress))
        return 0

    arg = self.api.ev(arg)

    if arg is None:
        raise ArgumentError()

    buffer = pyflam3ng.flam3.RenderBuffer()

    if isinstance(arg, basestring) and arg.strip():
        genome = pyflam3ng.load_genome(xml_source=arg)
    elif isinstance(arg, pyflam3ng.Genome):
        genome = arg
    elif not isinstance(arg, pyflam3ng.Genome):
        raise TypeError('unexpected argument type')

    w = genome.width
    h = genome.height

    buffer.resize(w, h, 3)

    genome.render(buffer, progress=progress)
    sys.stdout.write('\n')

    image = wx.EmptyImage(w, h)
    buffer.write_to_legacy_buffer(image.DataBuffer)

    bmp = wx.BitmapFromImage(image)

    class PreviewFrame(wx.Frame):
        def __init__(self, bmp):
            super(PreviewFrame, self).__init__(None,
                    style=wx.DEFAULT_FRAME_STYLE^(wx.RESIZE_BORDER|wx.MAXIMIZE_BOX))

            self.bmp = bmp

            self.SetClientSize((w, h))

            self.Bind(wx.EVT_ERASE_BACKGROUND, self._on_erase_bkgnd)
            self.Bind(wx.EVT_PAINT, self._on_paint)

        def _on_erase_bkgnd(self, evt):
            pass

        def _on_paint(self, evt):
            dc = wx.PaintDC(self)
            dc.Clear()
            client_size = self.GetClientSize()

            if self.bmp:
                dc.DrawBitmap(self.bmp, 0, 0)

    frame = PreviewFrame(bmp)
    frame.Show()




ip.expose_magic('wxrender', wxrender)

