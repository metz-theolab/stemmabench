"""
Unit tests for the ManuscriptEmpty class.
"""
import unittest
from stemmabench.algorithms.manuscript_empty import ManuscriptEmpty
import shutil
import os


class TestManuscriptEmpty(unittest.TestCase):
    """Unit tests for ManuscriptEmpty.
    """
    
    def setUp(self) -> None:
        """Setup the unit test.
        """
        self.dump_folder_path = "tests/test_data/test_output"
        self.test_child1 = ManuscriptEmpty(label="child1", parent=None)
        self.test_child2 = ManuscriptEmpty(label="child2", parent=None)
        self.test_child3 = ManuscriptEmpty(label="child3", parent=None)
        children = [self.test_child1, self.test_child2, self.test_child3]
        self.manuscriptEmpty = ManuscriptEmpty(label="label", children=children, parent=None, edges=[1,2,3])
        self.lookup_dict = {'label': self.manuscriptEmpty, 
                            'child1': self.test_child1, 
                            'child2': self.test_child2, 
                            'child3': self.test_child3}
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
        
    def test_Manuscript(self):
        """Tests ManuscriptBase instanciation."""
        with self.assertRaises(ValueError, msg="Dose not throw error if parent is of wrong type."):
            ManuscriptEmpty(label="label", children=[], parent="test")
        with self.assertRaises(ValueError, msg="Dose not throw error if children not a list."):
            ManuscriptEmpty(label="label", children="test", parent=None)
        with self.assertRaises(RuntimeError, msg="Dose not throw error if children and edges of different length."):
            ManuscriptEmpty(label="label", children=[], parent=None, edges=[1])
        with self.assertRaises(ValueError):
             ManuscriptEmpty()
        with self.assertRaises(ValueError, msg="The __init__ method does not raise a ValueError if recursive is specified and text_list is not."):
             ManuscriptEmpty(parent=None, recursive={"label":{}}, children=[])

    def test_Manuscript_attributes(self):
        """Tests attribute instantiation."""
        self.assertEqual(self.manuscriptEmpty.label, "label", msg= "Error in label instantiation")
        self.assertEqual(self.manuscriptEmpty.children[0], self.test_child1, msg="Wrong first child.")
        self.assertEqual(self.manuscriptEmpty.children[1], self.test_child2, msg="Wrong second child.")
        self.assertEqual(self.manuscriptEmpty.children[2], self.test_child3, msg="Wrong third child.")
        self.assertIsNone(self.manuscriptEmpty.parent, msg="Parent is not set properly.")
        self.assertCountEqual(self.manuscriptEmpty.edges, [1,2,3])

    def test_repr(self):
        """Tests the repr method."""
        self.assertEqual(self.manuscriptEmpty.__repr__(), "label")

    def test_dict(self):
        """Tests the dict method."""
        self.assertDictEqual(self.manuscriptEmpty.dict(), {'label': {'child1': {}, 'child2': {}, 'child3': {}}})
        self.assertDictEqual(self.manuscriptEmpty.dict(include_edges=True), self.edge_dict)
        self.assertDictEqual(self.test_child1.dict(include_edges=True), {'child1': {}})

    def test_build_text_lookup(self):
        """Tests the build_text_lookup method."""
        self.assertDictEqual(self.manuscriptEmpty.build_text_lookup(), self.lookup_dict)
    
    def test_dump(self):
         """Tests the dump method. (The rest of this method is tested in test_stemmas test_dump test.)"""
         self.test_child1.dump(self.dump_folder_path)
         self.assertTrue(os.path.isdir(self.dump_folder_path), msg="The dump method does not create directory if it does not already exist.")

    def test_eq(self):
         """Tests the __eq__ method."""
         self.assertFalse(self.manuscriptEmpty.__eq__(self.test_child1), msg="The __eq__ method dose not identify False equality with an other empty manuscript properly.")
         self.assertFalse(self.manuscriptEmpty.__eq__("not_a_manuscript"), msg="The __eq__ method dose not identify False equality with an other eobject properly.")