"""
Unit tests for the Manuscript class.
"""
import unittest
from stemmabench.algorithms.manuscript import Manuscript


class TestManuscript(unittest.TestCase):
    """Unit tests for Manuscript.
    """
    
    def setUp(self) -> None:
        """Setup the unit test.
        """
        self.manuscript1 = Manuscript(label = "same label", text= "same text", children=[])
        self.manuscript2 = Manuscript(label = "same label", text= "same text", children=[])
        self.manuscript3 = Manuscript(label = "different label", text= "same text", children=[])
        self.manuscript4 = Manuscript(label = "same label", text= "different text", children=[self.manuscript1])
        pass

    def test_Manuscript(self):
        """Tests Manuscript instanciation."""
        self.assertEqual(self.manuscript1.label, "same label")
        self.assertEqual(self.manuscript1.text, "same text")
        self.assertCountEqual(self.manuscript4.children, [self.manuscript1])
        self.assertIsNone(self.manuscript1.parent)
        with self.assertRaises(ValueError):
            Manuscript()

    def test_eq(self):
        """Tests the __eq__ method."""
        self.assertFalse(self.manuscript1.__eq__("test"))
        self.assertTrue(self.manuscript1.__eq__(self.manuscript2))
        self.assertFalse(self.manuscript1.__eq__(self.manuscript3))
        self.assertFalse(self.manuscript1.__eq__(self.manuscript4))