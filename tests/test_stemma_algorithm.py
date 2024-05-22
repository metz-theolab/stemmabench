"""
Unit tests for the StemmaAlgo class.
"""
import unittest
from stemmabench.algorithms.stemma_algorithm import StemmaAlgo


class TestStemmaAlgo(unittest.TestCase):
    """Unit tests for the StemmaAlgo class.
    """
    
    def setUp(self) -> None:
        """Setup the unit test.
        """
        self.stemma_folder_path = "tests/test_data/test_stemma"
        self.stemmaAlgo_empty = StemmaAlgo()
        self.stemmaAlgo_with_path = StemmaAlgo(folder_path=self.stemma_folder_path)
        self.test_manuscript = {'1': 'This is a text.',
                                '10': 'This is is a a text.',
                                '11': 'This this is is a text.',
                                '12': 'This this is is a text.',
                                '13': 'This is is a a textual matter.',
                                '2': 'This is a a text.',
                                '3': 'This is a a text.',
                                '4': 'This is is a text.',
                                '5': 'This is is a a text.',
                                '6': 'This this is a a text.',
                                '7': 'This is is a a text.',
                                '8': 'This is a a a text.',
                                '9': 'This is a a a text.'}
        self.stemmaAlgo_from_compute = StemmaAlgo()
        self.stemmaAlgo_from_compute.compute(folder_path=self.stemma_folder_path)

    def test_set_from_folder_path(self):
        """Tests the _set_from_folder_path method."""
        with self.assertRaises(ValueError, msg="The _set_from_folder_path does not raise a ValueError no parameter is specified."):
            self.stemmaAlgo_empty._set_from_folder_path()
        with self.assertRaises(RuntimeError, msg="The _set_from_folder_path does not raise a RuntimeError if the folder_path parameter is not an existing directory."):
            self.stemmaAlgo_empty._set_from_folder_path(folder_path="tests/test_data/not_an_existing_folder")
        temp = StemmaAlgo()
        temp._set_from_folder_path(folder_path=self.stemma_folder_path)
        self.assertEqual(temp.folder_path, self.stemma_folder_path, msg="The _set_from_folder_path method does not set the folder_path correctly.")
        self.assertEqual(temp.manuscripts, self.test_manuscript, msg="The _set_from_folder_path method does not build the manuscripts dictionary correctly.")

    def test_StemmaAlgo(self):
        """Tests __init__ method."""
        self.assertEqual(self.stemmaAlgo_with_path.folder_path, self.stemma_folder_path, msg="__init__ does not set the folder path properly.")
        self.assertDictEqual(self.stemmaAlgo_with_path.manuscripts, self.test_manuscript, msg="__init__ does not build manuscript dictionary properly.")
    
    def test_getters(self):
        """Tests the getter methods."""
        self.assertEqual(self.stemmaAlgo_with_path.folder_path, self.stemma_folder_path, msg="The folder_path getter dose not return the right value.")
        self.assertEqual(self.stemmaAlgo_with_path.manuscripts, self.test_manuscript, msg="The manuscripts getter dose not return the right value.")

    def test_build_edges(self):
        """Tests the _build_edges method."""
        with self.assertRaises(NotImplementedError, msg="The empty StemmaAlgo does not raise a NotImplementedError when the _build_edges method is called."):
            self.stemmaAlgo_empty._build_edges()
        with self.assertRaises(NotImplementedError, msg="The StemmaAlgo with folder_path attribute does not raise a NotImplementedError when the _build_edges method is called."):
            self.stemmaAlgo_with_path._build_edges()

    def test__eq__(self):
        """Tests the __eq__ method."""
        with self.assertRaises(NotImplementedError, msg="The __eq__ method does not raise a NotImplementedError."):
            self.stemmaAlgo_empty.__eq__("whatever")

    def test__repr__(self):
        """Tests the __repr__ method."""
        with self.assertRaises(NotImplementedError, msg="The __repr__ method does not raise a NotImplementedError."):
            self.stemmaAlgo_empty.__repr__()
    
    def test_compute(self):
        """Tests the compute method."""
        temp = StemmaAlgo()
        with self.assertRaises(ValueError):
            temp.compute()
