import unittest
import pyflam3ng
from testing_util import print_test_name

class TestCase(unittest.TestCase):
    @print_test_name
    def testImageComments(self):
        i = pyflam3ng.ImageComments()
        self.assertEqual('', i.genome)
        self.assertEqual('', i.badvals)
        self.assertEqual('', i.numiters)
        self.assertEqual('', i.rtime)
        del i

