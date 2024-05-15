"""
Unit tests for the ManuscriptBase class.
"""
import unittest
from stemmabench.algorithms.manuscript_base import ManuscriptBase


class TestManuscriptBase(unittest.TestCase):
    """Unit tests for ManuscriptBase.
    """
    
    def setUp(self) -> None:
        """Setup the unit test.
        """
        self.test_child1 = ManuscriptBase(label="child1", parent=None)
        self.test_child2 = ManuscriptBase(label="child2", parent=None)
        self.test_child3 = ManuscriptBase(label="child3", parent=None)
        children = [self.test_child1, self.test_child2, self.test_child3]
        self.manuscriptBase = ManuscriptBase(label="label", children=children, parent=None, edges=[1,2,3])
        self.lookup_dict = {'label': self.manuscriptBase, 
                            'child1': self.test_child1, 
                            'child2': self.test_child2, 
                            'child3': self.test_child3}
        self.edge_dict = {'label': 'label',
                          'edges': {'child1': 1, 'child2': 2, 'child3': 3},
                          'children': {'child1': {'child1': {}},
                                       'child2': {'child2': {}},
                                       'child3': {'child3': {}}}}
        
    def test_Manuscript(self):
        """Tests ManuscriptBase instanciation."""
        with self.assertRaises(ValueError, msg="Dose not throw error if parent is of wrong type."):
            ManuscriptBase(label="label", children=[], parent="test")
        with self.assertRaises(ValueError, msg="Dose not throw error if children not a list."):
            ManuscriptBase(label="label", children="test", parent=None)
        with self.assertRaises(RuntimeError, msg="Dose not throw error if children and edges of different length."):
            ManuscriptBase(label="label", children=[], parent=None, edges=[1])

    def test_Manuscript_attributes(self):
        """Tests attribute instantiation."""
        self.assertEqual(self.manuscriptBase.label, "label", msg= "Error in label instantiation")
        self.assertEqual(self.manuscriptBase.children[0], self.test_child1, msg="Wrong first child.")
        self.assertEqual(self.manuscriptBase.children[1], self.test_child2, msg="Wrong second child.")
        self.assertEqual(self.manuscriptBase.children[2], self.test_child3, msg="Wrong third child.")
        self.assertIsNone(self.manuscriptBase.parent, msg="Parent is not set properly.")
        self.assertCountEqual(self.manuscriptBase.edges, [1,2,3])

    def test_repr(self):
        """Tests the repr method."""
        self.assertEqual(self.manuscriptBase.__repr__(), "label")

    def test_dict(self):
        """Tests the dict method."""
        self.assertDictEqual(self.manuscriptBase.dict(), {'label': {'child1': {}, 'child2': {}, 'child3': {}}})
        self.assertDictEqual(self.manuscriptBase.dict(include_edges=True), self.edge_dict)
        self.assertDictEqual(self.test_child1.dict(include_edges=True), {'child1': {}})

    def test_build_text_lookup(self):
        """Tests the build_text_lookup method."""
        self.assertDictEqual(self.manuscriptBase.build_text_lookup(), self.lookup_dict)