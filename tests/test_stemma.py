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
        self.stemma = Stemma()

    #def test_stemma_tree(self):
        