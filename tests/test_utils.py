"""
Unit tests for the Utils class.
"""
import unittest
from pathlib import Path
from stemmabench.algorithms.utils import Utils# import dict_from_edge, load_text, edge_to_list, dict_of_children, validate_edge, find_root


class TestUtils(unittest.TestCase):
    """Unit tests for the Utils class.
    """

    def setUp(self):
        """Setup the unit test.
        """
        self.test_path_edge_file = Path("tests/test_data/test_edge.txt").resolve()
        self.test_path_edge_2roots_file = Path("tests/test_data/test_edge_2roots.txt").resolve()
        self.test_path_text_file = Path("tests/test_data/test_text2.txt").resolve()
        self.test_dict = {"1": {"2": {"4": {"8": {}, "9": {}, "10": {}}, 
                                  "5": {"11": {}, "12": {}, "13": {}}},
                              "3": {"6": {"14": {}, "15": {}, "16": {}}, 
                                  "7": {}}}}
        self.test_text = "This is a text."
        self.test_edge_list = [['2', '5'],['3', '6'],['3', '7'],
                               ['4', '9'],['4', '10'],['5', '11'],
                               ['5', '12'],['2', '4'],['5', '13'],
                               ['1', '3'],['6', '14'],['4', '8'],
                               ['6', '15'],['6', '16'],['1', '2']]
        self.test_children_dict = {'2': {'5': {}, '4': {}},
                                   '3': {'6': {}, '7': {}},
                                   '4': {'9': {}, '10': {}, '8': {}},
                                   '5': {'11': {}, '12': {}, '13': {}},
                                   '1': {'3': {}, '2': {}},
                                   '6': {'14': {}, '15': {}, '16': {}}}
        self.test_children_dict_2roots = {'2': {'5': {}, '4': {}},
                                          '3': {'6': {}, '7': {}},
                                          '4': {'9': {}, '10': {}, '8': {}},
                                          '5': {'11': {}, '12': {}, '13': {}},
                                          '1': {'3': {}, '2': {}},
                                          '6': {'14': {}, '15': {}, '16': {}},
                                          '20': {'24': {}}}
        
    def test_load_text(self):
        """Tests that the function load_text imports texts correctly."""
        self.assertEqual(Utils.load_text(self.test_path_text_file), self.test_text, "Both string are not equal!")

    def test_edge_to_list(self):
        """Tests to see if edge file is converted to list properly."""
        self.assertCountEqual(Utils.edge_to_list(self.test_path_edge_file), self.test_edge_list)

    def test_dict_of_children(self):
        """Tests if """
        self.assertDictEqual(Utils.dict_of_children(self.test_edge_list),self.test_children_dict)

    def test_dict_from_edge(self):
        """Tests that the edge files converted to dictionaries properly."""
        self.assertDictEqual(Utils.dict_from_edge(self.test_path_edge_file), self.test_dict)

    def test_dict_from_edge_validate_file(self):
        """Tests if the dict_from_edge method can Throw an invalid exception if the given edge file is not valid."""
        with self.assertRaises(ValueError):
            Utils.dict_from_edge(self.test_path_edge_2roots_file)
    
    def test_find_root_1root(self):
        """Tests that find_root can find the label of the root in a dictionary of children."""
        self.assertCountEqual(Utils.find_root(self.test_children_dict), ["1"])

    def test_find_root_2roots(self):
        """Tests that find_root can find 2 roots if a children dictionary contains 2 roots."""
        self.assertCountEqual(Utils.find_root(self.test_children_dict_2roots), ["1","20"])

    def test_validate_edge_2roots(self):
        """Tests that validate_edges can detect if 2 roots are present in an edge file."""
        self.assertFalse(Utils.validate_edge(self.test_children_dict_2roots))