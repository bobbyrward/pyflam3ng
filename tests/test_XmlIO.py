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


test_flam3 = [
"""
<test>
""",
"""
<flame time="0" palette="15" size="640 480" center="0 0" scale="240" zoom="0" oversample="1" filter="1" quality="10" background="0 0 0" brightness="4" gamma="4" vibrancy="1" hue="0.22851">
   <xform weight="0.25" color="1" spherical="1" coefs="-0.681206 -0.0779465 0.20769 0.755065 -0.0416126 -0.262334"/>
   <xform weight="0.25" color="0.66" spherical="1" coefs="0.953766 0.48396 0.43268 -0.0542476 0.642503 -0.995898"/>
   <xform weight="0.25" color="0.33" spherical="1" coefs="0.840613 -0.816191 0.318971 -0.430402 0.905589 0.909402"/>
   <xform weight="0.25" color="0" spherical="1" coefs="0.960492 -0.466555 0.215383 -0.727377 -0.126074 0.253509"/>
</flame>
""",
"""
<flame time="100" palette="29" size="640 480" center="0 0" scale="240" zoom="0" oversample="1" filter="1" quality="10" background="0 0 0" brightness="4" gamma="4" vibrancy="1" hue="0.147038">
   <xform weight="0.25" color="1" spherical="1" coefs="-0.357523 0.774667 0.397446 0.674359 -0.730708 0.812876"/>
   <xform weight="0.25" color="0.66" spherical="1" coefs="-0.69942 0.141688 -0.743472 0.475451 -0.336206 0.0958816"/>
   <xform weight="0.25" color="0.33" spherical="1" coefs="0.0738451 -0.349212 -0.635205 0.262572 -0.398985 -0.736904"/>
   <xform weight="0.25" color="0" spherical="1" coefs="0.992697 0.433488 -0.427202 -0.339112 -0.507145 0.120765"/>
</flame>
""",
"""
</test>
""",
]

class TestCase(unittest.TestCase):
    @print_test_name
    def testToFromXml(self):
        genomes = pyflam3ng.flam3.from_xml(''.join(test_flam3))
        self.assertEqual(len(genomes), 2)

        xml = pyflam3ng.flam3.to_xml(genomes[0])
        self.assertTrue(xml)

        xml = pyflam3ng.flam3.to_xml(genomes[0])
        self.assertTrue(xml)

    def _check_genome_1(self, test):
        pass

    def _check_genome_2(self, test):
        pass

    @print_test_name
    def testHighlevelIO(self):
        gene1, gene2 = pyflam3ng.load_flame(xml_source=''.join(test_flam3))
        self._check_genome_1(gene1)
        self._check_genome_2(gene2)

        gene1 = pyflam3ng.load_genome(xml_source=test_flam3[1])
        self._check_genome_1(gene1)

        gene2 = pyflam3ng.load_genome(xml_source=test_flam3[2])
        self._check_genome_1(gene2)





