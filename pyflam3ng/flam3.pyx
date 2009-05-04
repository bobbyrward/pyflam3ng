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


def flam3_from_xml(str xml_source, str filename='', object defaults=True):
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


def flam3_to_xml(GenomeHandle genome):
    cdef char* c_string = flam3_print_to_string(genome._genome)
    cdef str py_string = str(c_string)

    flam3_free(c_string)

    return py_string

