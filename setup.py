from distutils.core import setup
from distutils.extension import Extension
#from Pyrex.Distutils import build_ext
from Cython.Distutils import build_ext
import commands
import os


# Taken from partiwm(http://partiwm.org/)
def pkgconfig(*packages, **kw):
    flag_map = {'-I': 'include_dirs',
                '-L': 'library_dirs',
                '-l': 'libraries'}
    cmd = "pkg-config --libs --cflags %s" % (" ".join(packages),)
    (status, output) = commands.getstatusoutput(cmd)
    if not (os.WIFEXITED(status) and os.WEXITSTATUS(status) == 0):
        raise Exception, ("call to pkg-config ('%s') failed" % (cmd,))
    for token in output.split():
        if flag_map.has_key(token[:2]):
            kw.setdefault(flag_map.get(token[:2]), []).append(token[2:])
        else: # throw others to extra_link_args
            kw.setdefault('extra_link_args', []).append(token)
        for k, v in kw.iteritems(): # remove duplicates
            kw[k] = list(set(v))
    return kw



setup(
  name = "pyflam3ng",
  ext_modules=[
    Extension("pyflam3ng._flam3", ["pyflam3ng/_flam3.pyx"], **pkgconfig('flam3'))
    ],
  cmdclass = {'build_ext': build_ext}
)

