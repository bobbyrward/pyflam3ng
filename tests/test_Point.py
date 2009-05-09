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

    @print_test_name
    def testSubtraction(self):
        p = Point(10.1, 20.2)

        self.assertEqual(p - Point(1.3, 2.5), Point(8.8, 17.7))
        self.assertEqual(p - Point(7.2, 12.41), Point(2.9, 7.79))

        p -= Point(5.41, 8.14)
        self.assertEqual(p, Point(4.69, 12.06))

    @print_test_name
    def testMultiplication(self):
        p = Point(10.1, 20.2)

        self.assertEqual(p * Point(1.3, 2.5), Point(13.13, 50.5))
        self.assertEqual(p * Point(7.2, 12.41), Point(72.72, 250.682))

        p *= Point(5.41, 8.14)
        self.assertEqual(p, Point(54.641, 164.428))

    @print_test_name
    def testDivision(self):
        p = Point(10.1, 20.2)

        self.assertEqual(p / Point(1.3, 2.5), Point(7.7692307692307683, 8.0800000000000001))
        self.assertEqual(p / Point(7.2, 12.41), Point(1.4027777777777777, 1.627719580983078))

        p /= Point(5.41, 8.14)
        self.assertEqual(p, Point(1.8669131238447318, 2.4815724815724813))

    @print_test_name
    def testMagnitude(self):
        p = Point(10.1, 20.2)
        self.assertAlmostEqual(p.magnitude(), 22.584286572747875)

    @print_test_name
    def testAngle(self):
        p = Point(10.1, 20.2)
        self.assertAlmostEqual(p.angle(), 63.43494882292201)

    @print_test_name
    def testPolar(self):
        p = Point(10.1, 20.2)
        self.assertEqual(p.polar, (22.584286572747875, 63.43494882292201))

    @print_test_name
    def testInCircle(self):
        p = Point(10.1, 20.2)
        self.assertFalse(p.in_circle(Point(0.0, 0.0), 15.0))
        self.assertTrue(p.in_circle(Point(0.0, 0.0), 22.6))

    @print_test_name
    def testInTriangle(self):
        p = Point(6.0, 6.0)

        self.assertTrue(p.in_triangle(
                Point(5.0, 5.0),
                Point(7.0, 5.0),
                Point(6.0, 7.0)
            ))

        self.assertFalse(p.in_triangle(
                Point(5.0, 5.0),
                Point(6.0, 5.0),
                Point(5.0, 6.0)
            ))

    @print_test_name
    def testInRect(self):
        p = Point(10.1, 20.2)
        self.assertFalse(p.in_rect(11, 21, 15, 22))
        self.assertTrue(p.in_rect(10, 20, 15, 22))

        self.assertFalse(p.in_rect_wh(11, 21, 4, 1))
        self.assertTrue(p.in_rect_wh(10, 20, 4, 1))







