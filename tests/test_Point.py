import unittest
from testing_util import print_test_name
from pyflam3ng import Point


class TestCase(unittest.TestCase):
    @print_test_name
    def testEquality(self):
        self.assertTrue(Point(1.0, 2.0) == Point(1.0, 2.0))
        self.assertFalse(Point(1.0, 2.1) == Point(1.0, 2.0))
        self.assertFalse(Point(1.1, 2.0) == Point(1.0, 2.0))

    @print_test_name
    def testAddition(self):
        p = Point(10.1, 20.2)

        self.assertEqual(p + Point(1.3, 2.5), Point(11.4, 22.7))
        self.assertEqual(p + Point(7.2, 12.41), Point(17.3, 32.61))

        p += Point(5.41, 8.14)
        self.assertEqual(p, Point(15.51, 28.34))




