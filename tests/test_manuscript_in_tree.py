"""
Unit tests for the ManuscriptInTree class.
"""
import unittest
from stemmabench.algorithms.manuscript_in_tree import ManuscriptInTree
from stemmabench.algorithms.utils import Utils


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

    def test_recursive_init(self):
        """Tests the recursive_init method."""
        test_child1 = ManuscriptInTree(label="child1", parent=None)
        test_child2 = ManuscriptInTree(label="child2", parent=None)
        test_child3 = ManuscriptInTree(label="child3", parent=None)
        children = [test_child1, test_child2, test_child3]
        manuscriptEmpty = ManuscriptInTree(
            label="label", children=children, parent=None, edges=[1, 2, 3])
        function_output = ManuscriptInTree(label="label", parent=None).recursive_init({
            'label': {'child1': {}, 'child2': {}, 'child3': {}}}, Utils.get_text_list("test_data/test_stemma"))
        self.assertTrue(function_output.__eq__(manuscriptEmpty))

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
