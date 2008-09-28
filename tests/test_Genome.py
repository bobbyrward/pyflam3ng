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

import unittest
import pyflam3ng
from testing_util import print_test_name

class TestCase(unittest.TestCase):
    @print_test_name
    def testGenome(self):
        genome = pyflam3ng.Genome(4)
        genome = pyflam3ng.Genome()

        self.assertEqual(2, len(genome.size))
        self.assertEqual((0, 0), tuple(genome.size))

        genome.size = (1, 2)
        self.assertEqual((1, 2), tuple(genome.size))


        size = genome.size
        del genome

        self.assertEqual((1, 2), tuple(size))
        del size

