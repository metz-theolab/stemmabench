"""
Unit tests for the Utils class.
"""
import unittest
import os
from pathlib import Path
import numpy as np
from stemmabench.algorithms.utils import Utils


class TestUtils(unittest.TestCase):
    """Unit tests for the Utils class.
    """

    def setUp(self):
        """Setup the unit test.
        """
        self.output_folder = "tests/test_data/test_output"
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
        self.test_edge_list_2roots = [['2', '5'], ['3', '6'], ['3', '7'],
                                      ['4', '9'], ['4', '10'], ['5', '11'],
                                      ['5', '12'], ['2', '4'], ['5', '13'],
                                      ['1', '3'], ['6', '14'], ['4', '8'],
                                      ['6', '15'], ['6', '16'], ['1', '2'], ['A', '2']]
        self.test_edge_list2 = [["A", "1"], ["1", "2"], ["1", "3"],
                                ["2", "4"], ["2", "5"], ["3", "6"],
                                ["3", "7"]]
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
        self.test_dict_of_connect = {'A': ['1'],
                                     '1': ['A', '2', '3'],
                                     '2': ['1', '4', '5'],
                                     '3': ['1', '6', '7'],
                                     '4': ['2'],
                                     '5': ['2'],
                                     '6': ['3'],
                                     '7': ['3']}
        self.test_dist_dict = {"A,1": 0.5, "1,2": 0.5, "1,3": 0.5,
                               "2,4": 0.5, "2,5": 0.5, "3,6": 0.5, "3,7": 10.5}
        self.test_dot_to_edge1 = [['N_0', '5'], ['N_0', '10'], ['N_1', 'N_0'], 
                                  ['N_1', '4'], ['N_2', 'N_1'], ['N_2', '11'], 
                                  ['N_3', 'N_2'], ['N_3', '8'], ['N_4', 'N_3'], 
                                  ['N_4', '12'], ['N_5', 'N_4'], ['N_5', '9'], 
                                  ['N_6', 'N_5'], ['N_6', '1'], ['N_7', 'N_6'], 
                                  ['N_7', '3'], ['N_8', 'N_7'], ['N_8', '7'], 
                                  ['N_9', 'N_8'], ['N_9', '6'], ['N_10', 'N_9'], 
                                  ['N_10', '2'], ['N_10', '13']]
        self.test_dot_to_edge2 = [['N_0', '1'], ['N_0', '8'], ['N_1', 'N_0'], 
                                  ['N_1', '2'], ['N_2', 'N_1'], ['N_2', '4'], 
                                  ['N_3', 'N_2'], ['N_3', '7'], ['N_4', 'N_3'], 
                                  ['N_4', '13'], ['N_5', 'N_4'], ['N_5', '10'], 
                                  ['N_6', 'N_5'], ['N_6', '12'], ['N_7', 'N_6'], 
                                  ['N_7', '5'], ['N_8', 'N_7'], ['N_8', '3'], 
                                  ['N_9', 'N_8'], ['N_9', '11'], ['N_10', 'N_9'], 
                                  ['N_10', '9'], ['N_10', '6']]

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
        self.assertEqual(Utils.find_root(self.test_edge_list)[
                         0], "1", msg="Can't find the right root for edge list input.")
        self.assertCountEqual(Utils.find_root(self.test_edge_list_2roots), [
                              "1", "A"], msg="find_root can't find the presence of 2 roots for edge list input.")

    def test_validate_edge(self):
        """Tests the validate_edges method."""
        self.assertFalse(Utils.validate_edge(self.test_children_dict_2roots),
                         msg="validate_edges can't detect if 2 roots are present in an edge file.")

    def test_dict_of_connections(self):
        """Tests the dict_of_connections method."""
        with self.assertRaises(ValueError, msg="Does not raise a ValueError list specified as tree parameter is of shapr (n,a) with a not = 2."):
            Utils.dict_of_connections(
                [["1", "2", "error"], ["1", "3", "error"], ["2", "4", "error"]])
        with self.assertRaises(ValueError, msg="Does not raise a ValueError list specified as tree parameter has to many dimentions."):
            Utils.dict_of_connections(
                [[["1"], ["2"]], [["1"], ["3"]], [["2"], ["4"]]])
        with self.assertRaises(ValueError, msg="Does not raise a ValueError if the parameter passed is not of type list or numpy.ndarray."):
            Utils.dict_of_connections("error")
        self.assertDictEqual(Utils.dict_of_connections(self.test_edge_list2),
                             self.test_dict_of_connect, msg="Does not return the right dict of connections.")
        self.assertDictEqual(Utils.dict_of_connections(np.array(self.test_edge_list2)),
                             self.test_dict_of_connect, msg="Does not return the right dict of connections.")

    def test_find_path(self):
        """Tests the find_path method."""
        self.assertCountEqual(Utils.find_path(self.test_edge_list2, "A", "7"), [
                              'A', '1', '3', '7'], msg="Does not find the right path with edge list input.")
        self.assertCountEqual(Utils.find_path(self.test_edge_list2, "4", "7"), [
                              '4', '2', '1', '3', '7'], msg="Does not find the right path with edge list input.")
        self.assertCountEqual(Utils.find_path(self.test_edge_list2, "B", "7"), [
        ], msg="Does not return empty list if start is not in edge list.")
        self.assertCountEqual(Utils.find_path(self.test_edge_list2, "A", "B"), [
        ], msg="Does not return empty list if target is not in edge list.")
        self.assertCountEqual(Utils.find_path(self.test_edge_list2, "A", "A"), [
                              "A"], msg="Does not return the right path if the start is the same as the target.")
        self.assertCountEqual(Utils.find_path(self.test_dict_of_connect, "A", "7"), [
                              'A', '1', '3', '7'], msg="Does not find the right path with dict of connections input.")
        self.assertCountEqual(Utils.find_path(self.test_dict_of_connect, "B", "7"), [
        ], msg="Does not return empty list if start is not in connection dict.")
        self.assertCountEqual(Utils.find_path(self.test_dict_of_connect, "A", "B"), [
        ], msg="Does not return empty list if target is not in connection dict.")
        self.assertCountEqual(Utils.find_path(self.test_dict_of_connect, "4", "7"), [
                              '4', '2', '1', '3', '7'], msg="Does not find the right path with edge list input.")

    def test_find_path_length(self):
        """Tests the find_path_length method."""
        self.assertEqual(Utils.find_path_length(self.test_edge_list2, "A", "7", self.test_dist_dict),
                         11.5, msg="Does not find the right distance with edge list input.")
        self.assertEqual(Utils.find_path_length(self.test_edge_list2, "4", "7", self.test_dist_dict),
                         12.0, msg="Does not find the right distance with edge list input.")
        self.assertEqual(Utils.find_path_length(self.test_dict_of_connect, "A", "7", self.test_dist_dict),
                         11.5, msg="Does not find the right distance with dict of connections input.")
        self.assertEqual(Utils.find_path_length(self.test_dict_of_connect, "4", "7", self.test_dist_dict),
                         12.0, msg="Does not find the right distance with dict of connections input.")
        self.assertCountEqual(Utils.find_path_length(self.test_edge_list2, "A", "7", self.test_dist_dict, True), (11.5, [
                              'A', '1', '3', '7']), msg="Does not find the right distance with edge list input and get_path = True.")
        self.assertCountEqual(Utils.find_path_length(self.test_edge_list2, "4", "7", self.test_dist_dict, True), (12.0, [
                              '4', '2', '1', '3', '7']), msg="Does not find the right distance with edge list input and get_path = True.")
        self.assertCountEqual(Utils.find_path_length(self.test_dict_of_connect, "A", "7", self.test_dist_dict, True), (11.5, [
                              'A', '1', '3', '7']), msg="Does not find the right distance with dict of connections input and get_path = True.")
        self.assertCountEqual(Utils.find_path_length(self.test_dict_of_connect, "4", "7", self.test_dist_dict, True), (12.0, [
                              '4', '2', '1', '3', '7']), msg="Does not find the right distance with dict of connections input and get_path = True.")

    def test_find_midpoint_root(self):
        """Tests the find_midpoint_root method."""
        self.assertEqual(Utils.find_midpoint_root(self.test_edge_list2),
                         "1", msg="Does not find the right midpoint with no dist_dict.")
        self.assertEqual(Utils.find_midpoint_root(self.test_edge_list2, self.test_dist_dict),
                         "3", msg="Does not find the right midpoint with dist_dict.")
        self.assertEqual(Utils.find_midpoint_root(self.test_edge_list2, {"A,1": 0.5, "1,2": 20.5, "1,3": 0.5, "2,4": 0.5, "2,5": 0.5, "3,6": 0.5, "3,7": 10.5}),
                         "1",
                         msg="Does not find the right midpoint with dist_dict.")

    def test_find_leaf_nodes(self):
        """Tests the find_leaf_nodes method."""
        self.assertCountEqual(Utils.find_leaf_nodes(self.test_edge_list), [
                              '10', '11', '12', '13', '14', '15', '16', '7', '8', '9'], msg="Does not return the right leaf list.")
        self.assertCountEqual(Utils.find_leaf_nodes(self.test_edge_list2), [
                              'A', '4', '5', '6', '7'], msg="Does not return the right leaf list with leaf on the right of edge list.")

    def test_set_new_root(self):
        """Tests the set_new_root method."""
        self.assertCountEqual(Utils.set_new_root(self.test_edge_list2, "3"),
                              [['1', 'A'],
                               ['1', '2'],
                               ['3', '1'],
                               ['2', '4'],
                               ['2', '5'],
                               ['3', '6'],
                               ['3', '7']],
                              msg="Does not return the right edge list.")
        with self.assertRaises(ValueError,  msg="Does no raise a ValueError when the specified new root is not in the tree."):
            Utils.set_new_root(self.test_edge_list, "B")

    def test_get_dot_list(self):
        """Tests the get_dot_list method."""
        self.assertCountEqual(Utils.get_dot_list("tests/test_data/dot_files"), ["rhm-tree_0","rhm-tree_1","rhm-tree_2"], msg="Does not return the right list of dot files.")

    def test_save_edge(self):
        """Tests the save_edge method."""
        os.mkdir(self.output_folder)
        edge_list = [["1", "2"],["1", "3"],["2", "4"],["2", "5"],["3", "6"],["3", "7"]]
        Utils.save_edge(edge_list, f"{self.output_folder}/edges.txt")
        try:
            edges = open(f"{self.output_folder}/edges.txt", "r").read().split("\n")
            for edge_f, edge_l in zip(edges, edge_list):
                self.assertCountEqual([edge_f[1], edge_f[3]], edge_l, msg="One of the edges is no correct.")
        finally:
            os.remove(f"{self.output_folder}/edges.txt")
            os.rmdir(self.output_folder)
    def test_dot_to_edge(self):
        """Tests the dot_to_edge method."""
        self.assertCountEqual(Utils.dot_to_edge("tests/test_data/dot_files/rhm-tree_0.dot"), self.test_dot_to_edge1, msg="Does not convert the dot file correctly.")
        self.assertCountEqual(Utils.dot_to_edge("tests/test_data/dot_files/rhm-tree_1.dot"), self.test_dot_to_edge2, msg="Does not convert the dot file correctly.")