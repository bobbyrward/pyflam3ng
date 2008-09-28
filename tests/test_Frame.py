import unittest
import pyflam3ng
from testing_util import print_test_name

class TestCase(unittest.TestCase):
    @print_test_name
    def testFrame(self):
        frame = pyflam3ng.Frame()
        self.assertEqual(1.0, frame.pixel_aspect_ratio)

        def func():
            pass

        frame = pyflam3ng.Frame(aspect=2.0, progress_func=func)
        self.assertEqual(2.0, frame.pixel_aspect_ratio)

        del frame

