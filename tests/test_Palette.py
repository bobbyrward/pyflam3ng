import unittest
import pyflam3ng
from testing_util import print_test_name

class TestCase(unittest.TestCase):
    @print_test_name
    def testPalettes(self):
        palette = pyflam3ng.Palette()

        for (r, g, b) in palette:
            self.assertEqual((0,0,0), (r, g, b))

        palette[0] = (1, 2, 3)

        self.assertEqual((1, 2, 3), palette[0])

        standard_palette = pyflam3ng.standard_palette()

        palette_xml_element = standard_palette.to_element()
        palette_str = standard_palette.to_string()

        palette_from_element = pyflam3ng.Palette.from_element(palette_xml_element)
        palette_from_string = pyflam3ng.Palette.from_string(palette_str)

        for idx, rgb_triple in enumerate(standard_palette):
            for triple_idx in range(3):
                self.assertAlmostEqual(rgb_triple[triple_idx], palette_from_element[idx][triple_idx])
                self.assertAlmostEqual(rgb_triple[triple_idx], palette_from_string[idx][triple_idx])

