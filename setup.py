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

from distutils.core import setup
from distutils.extension import Extension
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

def flam3_compiler_options():
    return pkgconfig('flam3')


def numpy_compiler_options():
    import numpy
    return {'include_dirs': [numpy.get_include()]}


def merge_options(x, y):
    for k, v in y.iteritems():
        if k not in x:
            x[k] = v
        else:
            x[k].extend(v)

    return x


def _Extension(name, sources, options_dict, *additional_options):
    if options_dict is None:
        options_dict = {}

    for x in additional_options:
        options_dict = merge_options(options_dict, x)

    return Extension(name, sources, **options_dict)


setup(
    name = "pyflam3ng",
    ext_modules=[
        _Extension("pyflam3ng.flam3", ["pyflam3ng/flam3.pyx"],
            numpy_compiler_options(),
            flam3_compiler_options()
        ),
        _Extension("pyflam3ng.util", ["pyflam3ng/util.pyx"],
            numpy_compiler_options()
        ),
    ],
    cmdclass = {'build_ext': build_ext}

)

