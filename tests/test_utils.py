"""
Unit tests for the Utils class.
"""
import unittest
from pathlib import Path
from stemmabench.algorithms.utils import Utils


class TestUtils(unittest.TestCase):
    """Unit tests for the Utils class.
    """

    def setUp(self):
        """Setup the unit test.
        """
        self.test_path_edge_file = Path(
            "tests/test_data/test_edge.txt").resolve()
        self.test_path_edge_2roots_file = Path(
            "tests/test_data/test_edge_2roots.txt").resolve()
        self.test_path_text_file = Path(
            "tests/test_data/test_text2.txt").resolve()
        self.test_dict = {"1": {"2": {"4": {"8": {}, "9": {}, "10": {}},
                                      "5": {"11": {}, "12": {}, "13": {}}},
                                "3": {"6": {"14": {}, "15": {}, "16": {}},
                                      "7": {}}}}
        self.test_text = "This is a text."
        self.test_edge_list = [['2', '5'], ['3', '6'], ['3', '7'],
                               ['4', '9'], ['4', '10'], ['5', '11'],
                               ['5', '12'], ['2', '4'], ['5', '13'],
                               ['1', '3'], ['6', '14'], ['4', '8'],
                               ['6', '15'], ['6', '16'], ['1', '2']]
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
        """Tests the load_text method."""
        self.assertEqual(Utils.load_text(self.test_path_text_file),
                         self.test_text, msg="load_text does not load a text properly.")

    def test_edge_to_list(self):
        """Tests edge_to_list method."""
        self.assertCountEqual(Utils.edge_to_list(self.test_path_edge_file), self.test_edge_list,
                              msg="edge_to_list does not convert edge file to edge list properly.")

    def test_dict_of_children(self):
        """Tests _dict_of_children method."""
        self.assertDictEqual(Utils.dict_of_children(self.test_edge_list), self.test_children_dict,
                             msg="Does not convert edge list to dictionary of children properly.")

    def test_dict_from_edge(self):
        """Tests _dict_from_edge method."""
        self.assertDictEqual(Utils.dict_from_edge(edge_path=self.test_path_edge_file),
                             self.test_dict, msg="_dict_from_edge does not convert edge files properly.")
        self.assertDictEqual(Utils.dict_from_edge(edge_list=self.test_edge_list),
                             self.test_dict, msg="_dict_from_edge does not convert edge lists properly.")
        with self.assertRaises(ValueError, msg="_dict_from_edge does not raise ValueError if edge file is not valid."):
            Utils.dict_from_edge(edge_path=self.test_path_edge_2roots_file)
        with self.assertRaises(ValueError, msg="_dict_from_edge does not raise ValueError if both parameters are specified."):
            Utils.dict_from_edge(
                edge_path=self.test_path_edge_2roots_file, edge_list=['1', '2'])
        with self.assertRaises(ValueError, msg="_dict_from_edge does not raise ValueError if no parameters are specified."):
            Utils.dict_from_edge()

    def test_find_root(self):
        """Tests find_root method."""
        self.assertCountEqual(Utils.find_root(self.test_children_dict), [
                              "1"], msg="find_root can't find the root if there is only 1 root.")
        self.assertCountEqual(Utils.find_root(self.test_children_dict_2roots), [
                              "1", "20"], msg="find_root can't find the presence of 2 roots.")

    def test_validate_edge(self):
        """Tests the validate_edges method."""
        self.assertFalse(Utils.validate_edge(self.test_children_dict_2roots),
                         msg="validate_edges can't detect if 2 roots are present in an edge file.")
