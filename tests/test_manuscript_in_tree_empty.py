"""
Unit tests for the ManuscriptEmpty class.
"""
import unittest
import shutil
import os
from stemmabench.algorithms.utils import Utils
from stemmabench.algorithms.manuscript_in_tree_empty import ManuscriptInTreeEmpty


class TestManuscriptEmpty(unittest.TestCase):
    """Unit tests for ManuscriptEmpty.
    """

    def setUp(self) -> None:
        """Setup the unit test.
        """
        self.dump_folder_path = "tests/test_data/test_output"
        self.edge_dict = {'label': 'label',
                          'edges': {'child1': 1, 'child2': 2, 'child3': 3},
                          'children': {'child1': {'child1': {}},
                                       'child2': {'child2': {}},
                                       'child3': {'child3': {}}}}

    def tearDown(self) -> None:
        """Clean up by deleting the output folder and its contents.
        """
        if os.path.exists(self.dump_folder_path):
            shutil.rmtree(self.dump_folder_path)

    def test_manuscript_empty(self):
        """Tests ManuscriptBase instanciation."""
        with self.assertRaises(ValueError, msg="Dose not throw error if parent is of wrong type."):
            ManuscriptInTreeEmpty(label="label", children=[], parent="test")
        with self.assertRaises(ValueError, msg="Dose not throw error if children not a list."):
            ManuscriptInTreeEmpty(label="label", children="test", parent=None)
        with self.assertRaises(RuntimeError, msg="Dose not throw error if children and edges of different length."):
            ManuscriptInTreeEmpty(
                label="label", children=[], parent=None, edges=[1])
        with self.assertRaises(ValueError):
            ManuscriptInTreeEmpty()
        with self.assertRaises(ValueError, msg="The __init__ method does not raise a ValueError if recursive is specified and text_list is not."):
            ManuscriptInTreeEmpty(parent=None, recursive={
                                  "label": {}}, children=[])

    def test_manuscript_attributes(self):
        """Tests attribute instantiation."""
        test_child1 = ManuscriptInTreeEmpty(label="child1", parent=None)
        test_child2 = ManuscriptInTreeEmpty(label="child2", parent=None)
        test_child3 = ManuscriptInTreeEmpty(label="child3", parent=None)
        children = [test_child1, test_child2, test_child3]
        manuscriptEmpty = ManuscriptInTreeEmpty(
            label="label", children=children, parent=None, edges=[1, 2, 3])
        self.assertEqual(manuscriptEmpty.label, "label",
                         msg="Error in label instantiation")
        self.assertEqual(
            manuscriptEmpty.children[0], test_child1, msg="Wrong first child.")
        self.assertEqual(
            manuscriptEmpty.children[1], test_child2, msg="Wrong second child.")
        self.assertEqual(
            manuscriptEmpty.children[2], test_child3, msg="Wrong third child.")
        self.assertIsNone(manuscriptEmpty.parent,
                          msg="Parent is not set properly.")
        self.assertCountEqual(manuscriptEmpty.edges, [1, 2, 3])

    def test_recursive_init(self):
        """Tests the recursive_init method."""
        test_child1 = ManuscriptInTreeEmpty(label="child1", parent=None)
        test_child2 = ManuscriptInTreeEmpty(label="child2", parent=None)
        test_child3 = ManuscriptInTreeEmpty(label="child3", parent=None)
        children = [test_child1, test_child2, test_child3]
        manuscriptEmpty = ManuscriptInTreeEmpty(
            label="label", children=children, parent=None, edges=[1, 2, 3])
        function_output = ManuscriptInTreeEmpty(label="label", parent=None).recursive_init({
            'label': {'child1': {}, 'child2': {}, 'child3': {}}}, Utils.get_text_list("test_data/test_stemma"))
        self.assertTrue(function_output.__eq__(manuscriptEmpty))

    def test_repr(self):
        """Tests the repr method."""
        test_child1 = ManuscriptInTreeEmpty(label="child1", parent=None)
        test_child2 = ManuscriptInTreeEmpty(label="child2", parent=None)
        test_child3 = ManuscriptInTreeEmpty(label="child3", parent=None)
        children = [test_child1, test_child2, test_child3]
        manuscriptEmpty = ManuscriptInTreeEmpty(
            label="label", children=children, parent=None, edges=[1, 2, 3])
        self.assertEqual(manuscriptEmpty.__repr__(), "label")

    def test_dict(self):
        """Tests the dict method."""
        test_child1 = ManuscriptInTreeEmpty(label="child1", parent=None)
        test_child2 = ManuscriptInTreeEmpty(label="child2", parent=None)
        test_child3 = ManuscriptInTreeEmpty(label="child3", parent=None)
        children = [test_child1, test_child2, test_child3]
        manuscriptEmpty = ManuscriptInTreeEmpty(
            label="label", children=children, parent=None, edges=[1, 2, 3])
        self.assertDictEqual(manuscriptEmpty.dict(), {
                             'label': {'child1': {}, 'child2': {}, 'child3': {}}})
        self.assertDictEqual(manuscriptEmpty.dict(
            include_edges=True), self.edge_dict)
        self.assertDictEqual(test_child1.dict(
            include_edges=True), {'child1': {}})

    def test_build_text_lookup(self):
        """Tests the build_text_lookup method."""
        test_child1 = ManuscriptInTreeEmpty(label="child1", parent=None)
        test_child2 = ManuscriptInTreeEmpty(label="child2", parent=None)
        test_child3 = ManuscriptInTreeEmpty(label="child3", parent=None)
        children = [test_child1, test_child2, test_child3]
        manuscriptEmpty = ManuscriptInTreeEmpty(
            label="label", children=children, parent=None, edges=[1, 2, 3])
        test_lookup_dict = {'label': manuscriptEmpty,
                            'child1': test_child1,
                            'child2': test_child2,
                            'child3': test_child3}
        manuscriptEmpty = ManuscriptInTreeEmpty(
            label="label", children=children, parent=None, edges=[1, 2, 3])
        self.assertDictEqual(
            manuscriptEmpty.build_text_lookup(), test_lookup_dict)

    def test_eq(self):
        """Tests the __eq__ method."""
        test_child1 = ManuscriptInTreeEmpty(label="child1", parent=None)
        test_child2 = ManuscriptInTreeEmpty(label="child2", parent=None)
        test_child3 = ManuscriptInTreeEmpty(label="child3", parent=None)
        children = [test_child1, test_child2, test_child3]
        manuscriptEmpty = ManuscriptInTreeEmpty(
            label="label", children=children, parent=None, edges=[1, 2, 3])
        self.assertFalse(manuscriptEmpty.__eq__(
            test_child1), msg="The __eq__ method dose not identify False equality with an other empty manuscript properly.")
        self.assertFalse(manuscriptEmpty.__eq__("not_a_manuscript"),
                         msg="The __eq__ method dose not identify False equality with an other eobject properly.")
