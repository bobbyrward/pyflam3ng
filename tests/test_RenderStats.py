import unittest
import pyflam3ng
from testing_util import print_test_name

class TestCase(unittest.TestCase):
    @print_test_name
    def testRenderStats(self):
        stats = pyflam3ng.RenderStats()
        self.assertEqual(0, stats.badvals)
        self.assertEqual(0, stats.num_iters)
        self.assertEqual(0, stats.render_seconds)
        del stats

