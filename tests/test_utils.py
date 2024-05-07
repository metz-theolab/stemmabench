"""
Unit tests for utils.
"""
import unittest
import numpy as np
from utils import dict_from_edge, load_text

class TestUtils(unittest.TestCase):
    """Unit tests for the Utils functions.
    """

    def setUp(self):
        """Setup the unit test.
        """
        self.test_dict = {1: {2: {4: {8: {}, 9: {}, 10: {}}, 
                                  5: {11: {}, 12: {}, 13: {}}},
                              3: {6: {14: {}, 15: {}, 16: {}}, 
                                  7: {}}}}
        self.test_text = "This is a test."
        

    def test_load_test(self):
        """Tests that the function load_test imports texts correctly."""
        self.assertEqual(load_text("test_data/test_text2.txt"), self.test_text)

    def test_dict_from_edge(self):
        """Tests the that edge files are imported properly."""
        self.assertDictEqual(dict_from_edge("test/test_edges.txt"), self.test_dict)