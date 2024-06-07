"""
Unit tests for the Stemma class.
"""
import unittest
import os
import shutil
from stemmabench.algorithms.stemma import Stemma


class TestStemma(unittest.TestCase):
    """Unit tests for the Stemma class.
    """

    def setUp(self) -> None:
        """Setup the unit test.
        """
        self.stemma_folder = "tests/test_data/test_stemma"
        self.stemma_edge_file = self.stemma_folder + "/test_edges_stemma.txt"
        self.stemma_output_folder = "tests/test_data/test_output"
        self.stemma_edge = Stemma(folder_path=self.stemma_folder)
        self.stemma_edge.compute(
            edge_file=self.stemma_edge_file, folder_path=self.stemma_folder)
        self.compare_lookup_keys = {'1': 1, '4': 4, '11': 11, '12': 12, '13': 13,
                                    '3': 3, '9': 9, '10': 10, '8': 8, '2': 2, '5': 5, '6': 6, '7': 7}
        self.stemma_dict = {'1': {'4': {'11': {}, '12': {}, '13': {}},
                                  '3': {'9': {}, '10': {}, '8': {}},
                                  '2': {'5': {}, '6': {}, '7': {}}}}
        self.test_compute_dict = {'3': {'4': {'9': {'10': {}, '12': {}},
                                              '1': {'13': {}, '2': {}}},
                                        '7': {'11': {'5': {}, '8': {}},
                                              '6': {}}}}
        self.stemma_str = 'Tree({"1":{"4":{"11":{},"12":{},"13":{}},"3":{"9":{},"10":{},"8":{}},"2":{"5":{},"6":{},"7":{}}}})'

    def tearDown(self) -> None:
        """Clean up by deleting the output folder and its contents.
        """
        if os.path.exists(self.stemma_output_folder):
            shutil.rmtree(self.stemma_output_folder)

    def test_getters(self):
        """Tests the @property methods."""
        self.assertEqual(self.stemma_edge.edge_file, self.stemma_edge_file)
        self.assertDictEqual(self.stemma_edge.generation_info, {})

    def test_eq(self):
        """Test the __eq__ method."""
        pass

    def test_dict(self):
        """Test dict method."""
        temp = Stemma(folder_path=self.stemma_folder)
        with self.assertRaises(RuntimeError, msg="Does not raise RuntimeError if dict method called on stemma that has not been fited."):
            temp.dict()
        self.assertDictEqual(self.stemma_edge.dict(), self.stemma_dict)

    def test_repr(self):
        "Tests the __repr__ method."
        temp = Stemma(folder_path=self.stemma_folder)
        self.assertEqual(self.stemma_edge.__repr__().replace(
            "\n", "").replace(" ", ""), self.stemma_str)
        self.assertEqual(temp.__repr__(), "Empty")

    def test_compute(self):
        """Tests compute method."""
        # From edge file
        self.assertTrue(self.stemma_edge.fitted,
                        msg="Does not set the fitted attribute to True after calling the compute method.")
        self.assertEqual(self.stemma_edge.text_lookup.keys(),
                         self.compare_lookup_keys.keys())
        self.assertEqual(self.stemma_edge.folder_path, self.stemma_folder)
        # Error tests
        temp = Stemma(folder_path=self.stemma_folder)
        with self.assertRaises(RuntimeError, msg="Does not raise error when both edge_file and algo are not specified."):
            temp.compute()

    def test_dump(self):
        """Tests the dump method. !!! Uses __eq__ method from ManuscriptInTree class !!!"""
        self.stemma_edge.dump(self.stemma_output_folder)
        files = os.listdir(self.stemma_output_folder)
        files = [x for x in files if "edges" not in x]
        for name in files:
            text2 = open(self.stemma_output_folder + "/" + name, "r").read()
            self.assertEqual(
                self.stemma_edge.text_lookup[name.replace(".txt", "")].text, text2)
        for edge in open(self.stemma_edge_file, "r").read().split(sep="\n"):
            self.assertTrue(open(self.stemma_edge_file,
                            "r").read().find(edge) > -1)

    def test_get_edges(self):
        """Tests the get_edges method."""
        with self.assertRaises(NotImplementedError):
            self.stemma_edge.get_edges()

    def test_set_folder_path(self):
        """Tests the _set_folder_path method."""
        with self.assertRaises(ValueError, msg="The _set_folder_path method does not raise a ValueError when the given folder_path is not an existing directory."):
            Stemma(folder_path="tests/not_folder_path")
