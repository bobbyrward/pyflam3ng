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
from __future__ import with_statement

import unittest
import pyflam3ng
from pyflam3ng.constants import *
from testing_util import print_test_name
import os

class TestCase(unittest.TestCase):
    @print_test_name
    def testCreation(self):
        genome = pyflam3ng.Genome(4)
        genome = pyflam3ng.Genome()

    @print_test_name
    def testName(self):
        genome = pyflam3ng.Genome()

        self.assertEqual('', genome.name)

        s = 'genome_test_name'
        genome.name = s

        self.assertEqual('genome_test_name', genome.name)

        del s

        self.assertEqual('genome_test_name', genome.name)

        def temp(): genome.name = 0.12345
        self.assertRaises(TypeError, temp)

    @print_test_name
    def testSize(self):
        genome = pyflam3ng.Genome()

        self.assertEqual(2, len(genome.size))
        self.assertEqual((0, 0), genome.size)

        genome.size = (1, 2)
        self.assertEqual((1, 2), genome.size)

    @print_test_name
    def testRotationCenter(self):
        genome = pyflam3ng.Genome()

        self.assertEqual(2, len(genome.rotation_center))
        self.assertEqual((0, 0), genome.rotation_center)

        genome.rotation_center = (1, 2)
        self.assertEqual((1, 2), genome.rotation_center)

    @print_test_name
    def testRotationCenter(self):
        genome = pyflam3ng.Genome()

        self.assertEqual(3, len(genome.bgcolor))
        self.assertEqual((0, 0, 0), genome.bgcolor)

        genome.bgcolor = (1, 2, 3)
        self.assertEqual((1, 2, 3), genome.bgcolor)

    @print_test_name
    def testClone(self):
        genome1 = pyflam3ng.Genome()
        self.assertEqual((0, 0), genome1.size)

        genome1.size = (640, 480)
        self.assertEqual((640, 480), genome1.size)

        genome2 = genome1.clone()
        self.assertEqual((640, 480), genome2.size)

    @print_test_name
    def testToString(self):
        genome = pyflam3ng.Genome()

        genome_str = genome.to_string()

        self.assertTrue(isinstance(genome_str, basestring))
        self.assertTrue(len(genome_str) > 0)

    @print_test_name
    def testToFile(self):
        TEST_FILENAME = 'test.output-to_file.flam3'
        genome = pyflam3ng.Genome(2)
        genome_str = genome.to_string()

        if os.path.exists(TEST_FILENAME):
            os.remove(TEST_FILENAME)

        self.assertFalse(os.path.exists(TEST_FILENAME))

        def temp(): genome.to_file(None)
        self.assertRaises(TypeError, temp)

        genome.to_file(TEST_FILENAME)

        self.assertTrue(os.path.exists(TEST_FILENAME))

        with open(TEST_FILENAME) as fd:
            test_str = fd.read()

        self.assertEqual(genome_str, test_str)

        if os.path.exists(TEST_FILENAME):
            os.remove(TEST_FILENAME)

        self.assertFalse(os.path.exists(TEST_FILENAME))

        with open(TEST_FILENAME, 'w') as fd:
            genome.to_file('', fd=fd)

        self.assertTrue(os.path.exists(TEST_FILENAME))

        with open(TEST_FILENAME) as fd:
            test_str = fd.read()

        self.assertEqual(genome_str, test_str)

        if os.path.exists(TEST_FILENAME):
            os.remove(TEST_FILENAME)

    @print_test_name
    def testTime(self):
        genome = pyflam3ng.Genome(2)

        self.assertAlmostEqual(0, genome.time)

        genome.time = 0.12345

        self.assertAlmostEqual(0.12345, genome.time)

        def temp(): genome.time = 'aaa'
        self.assertRaises(TypeError, temp)

    @print_test_name
    def testInterpolation(self):
        genome = pyflam3ng.Genome(2)

        self.assertEqual(0, genome.interpolation)

        genome.interpolation = flam3_interpolation_linear
        self.assertEqual(flam3_interpolation_linear, genome.interpolation)

        genome.interpolation = flam3_interpolation_smooth
        self.assertEqual(flam3_interpolation_smooth, genome.interpolation)

        def temp(): genome.interpolation = -3
        self.assertRaises(ValueError, temp)


    @print_test_name
    def testInterpolationType(self):
        genome = pyflam3ng.Genome(2)

        self.assertEqual(0, genome.interpolation_type)

        values = [ flam3_inttype_linear
                 , flam3_inttype_log
                 , flam3_inttype_compat
                 , flam3_inttype_older
                 ]

        for interp_value in values:
            genome.interpolation_type = interp_value
            self.assertEqual(interp_value, genome.interpolation_type)


        def temp(): genome.interpolation_type = -6
        self.assertRaises(ValueError, temp)


    @print_test_name
    def testPaletteInterpolation(self):
        genome = pyflam3ng.Genome(2)

        self.assertEqual(0, genome.palette_interpolation)

        values = [ flam3_palette_interpolation_hsv
                 , flam3_palette_interpolation_sweep
                 ]

        for interp_value in values:
            genome.palette_interpolation = interp_value
            self.assertEqual(interp_value, genome.palette_interpolation)


        def temp(): genome.palette_interpolation = -6
        self.assertRaises(ValueError, temp)






