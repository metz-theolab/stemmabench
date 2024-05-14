"""
Unit tests for the Stemma class.
"""
import unittest
from stemmabench.algorithms.manuscript import Manuscript


class TestManuscript(unittest.TestCase):
    
    def setup(self) -> None:
        """Setup the unit test.
        """
        self.manuscript_empty = Manuscript()
        pass

    def test_Manuscript(self):
        """Tests Manuscript instanciation."""
