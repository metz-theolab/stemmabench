"""
Unit tests for the Stemma class.
"""
import unittest
import numpy as np
from stemma.stemma import Stemma

class TestStemma(unittest.TestCase):
    """Unit tests for the Utils functions.
    """
    def setUp(self) -> None:
        """Setup the unit test.
        """
        self.stemma_empty = Stemma()

        

    def test_stemma_fitted_generation(self):
        """Checks that the fitted value is initialised to false."""
        self.assertFalse(self.stemma_empty.fitted)

    def test_stemma_lookup_generation(self):
        """Checks that the lookup dictionary is initialized to an empy dict."""
        self.assertDictEqual(self.stemma_empty.lookup, {})

    def test_stemma_path_to_folder_generation(self):
        """Checks that the path_to_folder is initialized to None."""
        self.assertIsNone(self.stemma_empty.path_to_folder)

    def test_stemma_edge_file_generation(self):
        """Checks that the edge_file is initialized to None."""
        self.assertIsNone(self.stemma_empty.edge_file)

    def test_stemma_generation_info_generation(self):
        """Checks that the generation_info is initialized to None."""
        self.assertIsNone(self.stemma_empty.generation_info)
        