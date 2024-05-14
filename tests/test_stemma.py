"""
Unit tests for the Stemma class.
"""
import unittest
import os
import shutil
from stemmabench.algorithms.stemma import Stemma
from stemmabench.algorithms.manuscript import Manuscript


class TestStemma(unittest.TestCase):
    """Unit tests for the Utils functions.
    """
    def setUp(self) -> None:
        """Setup the unit test.
        """
        self.stemma_empty = Stemma()
        self.stemma_edge = Stemma()
        self.stemma_edge.compute(edge_file="tests/test_data/test_edges_stemma.txt", path_to_folder="tests/test_data")
        self.compare_lookup_keys = {'1': 1,'4': 4,'11': 11,'12': 12,'13': 13,'3': 3,'9': 9,'10': 10,'8': 8,'2': 2,'5': 5,'6': 6,'7': 7}
        self.stemma_dict = {'1': {'4': {'11': {}, '12': {}, '13': {}},
                                  '3': {'9': {}, '10': {}, '8': {}},
                                  '2': {'5': {}, '6': {}, '7': {}}}}
        self.stemma_str = 'Tree({"1":{"4":{"11":{},"12":{},"13":{}},"3":{"9":{},"10":{},"8":{}},"2":{"5":{},"6":{},"7":{}}}})'

    def tearDown(self) -> None:
        """Clean up by deleting the output folder and its contents.
        """
        if os.path.exists("tests/test_data/test_output"):
                shutil.rmtree("tests/test_data/test_output")
    
    # Attribute tests
    def test_Stemma(self):
        """Tests Stemma instanciation."""
        self.assertFalse(self.stemma_empty.fitted)
        self.assertIsNone(self.stemma_empty.root)
        self.assertDictEqual(self.stemma_empty.text_lookup, {})
        self.assertIsNone(self.stemma_empty.path_to_folder)
        self.assertIsNone(self.stemma_empty.edge_file)
        self.assertIsNone(self.stemma_empty.edge_file)
        self.assertIsNone(self.stemma_empty.edge_file)
        self.assertIsNone(self.stemma_empty.generation_info)

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

    def test_compute_from_edge(self):
        """Check to see if the compute method sets Stemma attributes properly."""
        self.assertTrue(self.stemma_edge.fitted)
        self.assertEqual(self.stemma_edge.text_lookup.keys(), self.compare_lookup_keys.keys())
        self.assertEqual(self.stemma_edge.path_to_folder, "tests/test_data")
        temp = Stemma()
        with self.assertRaises(ValueError):
            temp.compute(edge_file="tests/test_data/test_edges_stemma.txt")

        
    def test_dump(self):
        """Tests the dump method. !!! Uses __eq__ method from Manuscript class !!!"""
        out = True
        for key in  self.stemma_edge.text_lookup:
            f = open("tests/test_data/" + key + ".txt", "r")
            text = f.read()
            out = not self.stemma_edge.text_lookup[key].__eq__(Manuscript(label=key, parent=None, children=[], text=text))
            if out:
                break
        self.assertFalse(out)
        temp = Stemma()
        temp.compute(edge_file="tests/test_data/test_edges_stemma.txt", path_to_folder="tests/test_data")
        temp._path_to_folder = None
        with self.assertRaises(ValueError):
            temp.dump()
        self.stemma_edge.dump("tests/test_data/test_output")
        files = os.listdir("tests/test_data/test_output")
        files = [x for x in files if "edges" not in x]
        for name in files:
            text2 = open("tests/test_data/test_output/" + name, "r").read()
            self.assertEqual(self.stemma_edge.text_lookup[name.replace(".txt", "")].text, text2)
        for edge in open("tests/test_data/test_edges_stemma.txt", "r").read().split(sep="\n"):
            self.assertTrue(open("tests/test_data/test_output/edges.txt", "r").read().find(edge) > -1)