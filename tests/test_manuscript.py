"""
Unit tests for the Manuscript class.
"""
import unittest
import shutil
import os
from stemmabench.algorithms.manuscript import Manuscript


class TestManuscript(unittest.TestCase):
    """Unit tests for Manuscript.
    """
    
    def setUp(self) -> None:
        """Setup the unit test.
        """
        self.dump_folder_path = "tests/test_data/test_output"
        self.manuscript1 = Manuscript(label = "same label", text= "same text", children=[])
        self.manuscript2 = Manuscript(label = "same label", text= "same text", children=[])
        self.manuscript3 = Manuscript(label = "different label", text= "same text", children=[])
        self.manuscript4 = Manuscript(label = "same label", text= "different text", children=[self.manuscript1])
        pass

    def tearDown(self) -> None:
        """Clean up by deleting the output folder and its contents.
        """
        if os.path.exists(self.dump_folder_path):
                shutil.rmtree(self.dump_folder_path)

    def test_Manuscript(self):
        """Tests Manuscript instanciation."""
        self.assertEqual(self.manuscript1.label, "same label")
        self.assertEqual(self.manuscript1.text, "same text")
        self.assertCountEqual(self.manuscript4.children, [self.manuscript1])
        self.assertIsNone(self.manuscript1.parent)
        with self.assertRaises(ValueError):
            Manuscript()
        with self.assertRaises(ValueError, msg="The __init__ method does not raise a ValueError if recursive is specified and text_list is not."):
             Manuscript(parent=None, recursive={"label":{}}, children=[])

    def test_eq(self):
        """Tests the __eq__ method."""
        self.assertFalse(self.manuscript1.__eq__("test"))
        self.assertTrue(self.manuscript1.__eq__(self.manuscript2))
        self.assertFalse(self.manuscript1.__eq__(self.manuscript3))
        self.assertFalse(self.manuscript1.__eq__(self.manuscript4))
    
    def test_dump(self):
         """Tests the dump method."""
         self.manuscript1.dump(self.dump_folder_path)
         self.assertTrue(os.path.isdir(self.dump_folder_path), msg="The dump method does not create directory if it does not already exist.")