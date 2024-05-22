"""
Unit tests for the Stemma class.
"""
import unittest
import os
import shutil
from stemmabench.algorithms.stemma import Stemma
from stemmabench.algorithms.manuscript import Manuscript
from stemmabench.algorithms.stemma_dummy import StemmaDummy


class TestStemma(unittest.TestCase):
    """Unit tests for the Stemma class.
    """
    
    def setUp(self) -> None:
        """Setup the unit test.
        """
        self.stemma_folder = "tests/test_data/test_stemma"
        self.stemma_edge_file = self.stemma_folder + "/test_edges_stemma.txt"
        self.stemma_edge_file_with_empty = self.stemma_folder + "/test_edges_empty_nodes.txt"
        self.stemma_output_folder = "tests/test_data/test_output"
        self.stemma_empty = Stemma()
        self.stemma_edge = Stemma()
        self.stemma_edge.compute(edge_file= self.stemma_edge_file, folder_path=self.stemma_folder)
        self.compare_lookup_keys = {'1': 1,'4': 4,'11': 11,'12': 12,'13': 13,'3': 3,'9': 9,'10': 10,'8': 8,'2': 2,'5': 5,'6': 6,'7': 7}
        self.stemma_dict = {'1': {'4': {'11': {}, '12': {}, '13': {}},
                                  '3': {'9': {}, '10': {}, '8': {}},
                                  '2': {'5': {}, '6': {}, '7': {}}}}
        self.stemma_dict_with_empty = {'1': {'4': {'11': {}, '12': {}, '13': {}},
                                             'Empty': {'9': {}, 'Empty2': {}, '8': {}},
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
    
    def test_Stemma(self):
        """Tests Stemma instanciation."""
        self.assertFalse(self.stemma_empty.fitted)
        self.assertIsNone(self.stemma_empty.root)
        self.assertDictEqual(self.stemma_empty.text_lookup, {})
        self.assertIsNone(self.stemma_empty.folder_path)
        self.assertIsNone(self.stemma_empty.edge_file)
        self.assertIsNone(self.stemma_empty.edge_file)
        self.assertIsNone(self.stemma_empty.edge_file)
        self.assertDictEqual(self.stemma_empty.generation_info, {})

    def test_eq(self):
        """Test the __eq__ method."""
        pass

    def test_dict(self):
        """Test dict method."""
        with self.assertRaises(RuntimeError):
            self.stemma_empty.dict()
        self.assertDictEqual(self.stemma_edge.dict(), self.stemma_dict)

    def test_repr(self):
        self.assertEqual(self.stemma_edge.__repr__().replace("\n","").replace(" ",""), self.stemma_str)
        self.assertEqual(self.stemma_empty.__repr__(), "Empty")

    def test_compute(self):
        """Tests compute method."""
        # From edge file
        self.assertTrue(self.stemma_edge.fitted)
        self.assertEqual(self.stemma_edge.text_lookup.keys(), self.compare_lookup_keys.keys())
        self.assertEqual(self.stemma_edge.folder_path, self.stemma_folder)
        temp = Stemma()
        temp.compute(folder_path=self.stemma_folder, edge_file=self.stemma_edge_file_with_empty)
        self.assertDictEqual(temp.dict(), self.stemma_dict_with_empty, msg="The compute methode does not build the right dictionary when one of the nodes is an ampty node.")
        # Error tests
        temp = Stemma()
        with self.assertRaises(ValueError):
            temp.compute(edge_file=self.stemma_edge_file)
        temp = Stemma()
        with self.assertRaises(RuntimeError):
            temp.compute()
        temp = Stemma()
        with self.assertRaises(RuntimeError, msg="The compute methode does not raise a RuntimeError if the folder path has not been specified."):
            temp.compute(StemmaDummy(width=2))
        # From algo
        temp.compute(algo=StemmaDummy(folder_path=self.stemma_folder, width=2, seed=1))
        temp = Stemma()
        with self.assertRaises(ValueError, msg="The compute method does not raise a ValueError when the given folder_path is not an existing directory."):
            temp.compute(folder_path="tests/not_folder_path", algo=StemmaDummy(width=2))
       

    def test_dump(self):
        """Tests the dump method. !!! Uses __eq__ method from Manuscript class !!!"""
        out = True
        for key in  self.stemma_edge.text_lookup:
            f = open(self.stemma_folder + "/" + key + ".txt", "r")
            text = f.read()
            out = not self.stemma_edge.text_lookup[key].__eq__(Manuscript(label=key, parent=None, children=[], text=text))
            if out:
                break
        self.assertFalse(out, msg="The dump method does not write the edge file correctly. (Look at Manuscript and ManuscriptBase dump method for errors.)")
        temp = Stemma()
        temp.compute(edge_file=self.stemma_edge_file, folder_path=self.stemma_folder)
        temp._folder_path = None
        with self.assertRaises(ValueError):
            temp.dump()
        self.stemma_edge.dump(self.stemma_output_folder)
        files = os.listdir(self.stemma_output_folder)
        files = [x for x in files if "edges" not in x]
        for name in files:
            text2 = open(self.stemma_output_folder+ "/" + name, "r").read()
            self.assertEqual(self.stemma_edge.text_lookup[name.replace(".txt", "")].text, text2)
        for edge in open(self.stemma_edge_file, "r").read().split(sep="\n"):
            self.assertTrue(open(self.stemma_edge_file, "r").read().find(edge) > -1)

    def test_get_edges(self):
        """Tests the get_edges method."""
        with self.assertRaises(NotImplementedError):
            self.stemma_empty.get_edges()

    def test_set_folder_path(self):
        """Tests the _set_folder_path method."""
        with self.assertRaises(ValueError, msg="The _set_folder_path method does not raise a ValueError when the given folder_path is not an existing directory."):
            Stemma(folder_path="tests/not_folder_path")