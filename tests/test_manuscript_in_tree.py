"""
Unit tests for the ManuscriptInTree class.
"""
import unittest
from stemmabench.algorithms.manuscript_in_tree import ManuscriptInTree


class TestManuscriptInTree(unittest.TestCase):
    """Unit tests for ManuscriptInTree.
    """

    def setUp(self) -> None:
        """Setup the unit test.
        """
        self.dump_folder_path = "tests/test_data/test_output"
        self.manuscript1 = ManuscriptInTree(
            label="same label", text="same text", children=[])
        self.manuscript2 = ManuscriptInTree(
            label="same label", text="same text", children=[])
        self.manuscript3 = ManuscriptInTree(
            label="different label", text="same text", children=[])
        self.manuscript4 = ManuscriptInTree(
            label="same label", text="different text", children=[self.manuscript1])

    def test_manuscript(self):
        """Tests Manuscript instanciation."""
        self.assertEqual(self.manuscript1.label, "same label")
        self.assertEqual(self.manuscript1.text, "same text")
        self.assertCountEqual(self.manuscript4.children, [self.manuscript1])
        self.assertIsNone(self.manuscript1.parent)
        with self.assertRaises(ValueError):
            ManuscriptInTree()

    def test_eq(self):
        """Tests the __eq__ method."""
        self.assertFalse(self.manuscript1.__eq__("test"))
        self.assertTrue(self.manuscript1.__eq__(self.manuscript2))
        self.assertFalse(self.manuscript1.__eq__(self.manuscript3))
        self.assertFalse(self.manuscript1.__eq__(self.manuscript4))
