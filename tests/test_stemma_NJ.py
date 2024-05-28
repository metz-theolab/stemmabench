"""
Unit tests for the StemmaNJ class.
"""
import unittest
from stemmabench.algorithms.stemma_NJ import StemmaNJ
from stemmabench.algorithms.stemma import Stemma
from textdistance import levenshtein
import numpy as np


class TestStemmaNJ(unittest.TestCase):
    """Unit tests for the stemmaNJ class.
    """
    
    def setUp(self) -> None:
        """Setup the unit test.
        """
        self.stemma_folder_path = "tests/test_data/test_stemma"
        self.stemmaNJ_empty = StemmaNJ()
        self.stemmaNJ = StemmaNJ()
        self.test_stemma = Stemma()
        self.test_stemma.compute(algo=StemmaNJ(),folder_path=self.stemma_folder_path, distance=levenshtein)
        self.stemmaNJ.compute(folder_path=self.stemma_folder_path, distance=levenshtein)
        #self.test_edges_list = [['5_7', '5'],
        #                        ['5_7', '7'],
        #                        ['5_7', '6_11_12_8_9_4_1_2_3_10_13'],
        #                        ['6_11_12_8_9_4_1_2_3_10_13', '6_11_12_8_9_4_1_2_3'],
        #                        ['6_11_12_8_9_4_1_2_3_10_13', '10_13'],
        #                        ['6_11_12_8_9_4_1_2_3', '6_11_12'],
        #                        ['6_11_12_8_9_4_1_2_3', '8_9_4_1_2_3'],
        #                        ['6_11_12', '6'],
        #                        ['6_11_12', '11_12'],
        #                        ['11_12', '11'],
        #                        ['11_12', '12'],
        #                        ['8_9_4_1_2_3', '8_9'],
        #                        ['8_9_4_1_2_3', '4_1_2_3'],
        #                        ['8_9', '8'],
        #                        ['8_9', '9'],
        #                        ['4_1_2_3', '4'],
        #                        ['4_1_2_3', '1_2_3'],
        #                        ['1_2_3', '1'],
        #                        ['1_2_3', '2_3'],
        #                        ['2_3', '2'],
        #                        ['2_3', '3'],
        #                        ['10_13', '10'],
        #                        ['10_13', '13']]
        self.test_edges_list = [['N_1', '11'],
                                ['N_1', '12'],
                                ['N_2', '6'],
                                ['N_2', 'N_1'],
                                ['N_3', '2'],
                                ['N_3', '3'],
                                ['N_4', '1'],
                                ['N_4', 'N_3'],
                                ['N_5', '8'],
                                ['N_5', '9'],
                                ['N_6', '4'],
                                ['N_6', 'N_4'],
                                ['N_7', 'N_5'],
                                ['N_7', 'N_6'],
                                ['N_8', 'N_2'],
                                ['N_8', 'N_7'],
                                ['N_9', '10'],
                                ['N_9', '13'],
                                ['N_10', '5'],
                                ['N_10', '7'],
                                ['N_11', 'N_8'],
                                ['N_11', 'N_9'],
                                ['N_10', 'N_11']]
        self.test_distance_matrix = np.array([[ 0.,  5.,  8.,  8., 15.,  2.,  2.,  3.,  5.,  7.,  5.,  4.,  4.],
                                              [ 5.,  0.,  4.,  4., 10.,  3.,  3.,  2.,  0.,  2.,  0.,  2.,  2.],
                                              [ 8.,  4.,  0.,  0., 14.,  7.,  7.,  5.,  4.,  2.,  4.,  6.,  6.],
                                              [ 8.,  4.,  0.,  0., 14.,  7.,  7.,  5.,  4.,  2.,  4.,  6.,  6.],
                                              [15., 10., 14., 14.,  0., 13., 13., 12., 10., 12., 10., 12., 12.],
                                              [ 2.,  3.,  7.,  7., 13.,  0.,  0.,  2.,  3.,  5.,  3.,  2.,  2.],
                                              [ 2.,  3.,  7.,  7., 13.,  0.,  0.,  2.,  3.,  5.,  3.,  2.,  2.],
                                              [ 3.,  2.,  5.,  5., 12.,  2.,  2.,  0.,  2.,  4.,  2.,  3.,  3.],
                                              [ 5.,  0.,  4.,  4., 10.,  3.,  3.,  2.,  0.,  2.,  0.,  2.,  2.],
                                              [ 7.,  2.,  2.,  2., 12.,  5.,  5.,  4.,  2.,  0.,  2.,  4.,  4.],
                                              [ 5.,  0.,  4.,  4., 10.,  3.,  3.,  2.,  0.,  2.,  0.,  2.,  2.],
                                              [ 4.,  2.,  6.,  6., 12.,  2.,  2.,  3.,  2.,  4.,  2.,  0.,  0.],
                                              [ 4.,  2.,  6.,  6., 12.,  2.,  2.,  3.,  2.,  4.,  2.,  0.,  0.]])
        #self.test_dist_dict = {'11_12,11': 0.0,
        #                       '11_12,12': 0.0,
        #                       '6_11_12,6': 0.09999999999999998,
        #                       '6_11_12,11_12': 1.9,
        #                       '2_3,2': 0.0,
        #                       '2_3,3': 0.0,
        #                       '1_2_3,1': 1.90625,
        #                       '1_2_3,2_3': 0.09375,
        #                       '8_9,8': 0.0,
        #                       '8_9,9': 0.0,
        #                       '4_1_2_3,4': 0.3958333333333333,
        #                       '4_1_2_3,1_2_3': 1.1041666666666667,
        #                       '8_9_4_1_2_3,8_9': 1.0375,
        #                       '8_9_4_1_2_3,4_1_2_3': 0.7124999999999999,
        #                       '6_11_12_8_9_4_1_2_3,6_11_12': 1.90625,
        #                       '6_11_12_8_9_4_1_2_3,8_9_4_1_2_3': 0.90625,
        #                       '10_13,10': 0.0,
        #                       '10_13,13': 10.0,
        #                       '5_7,5': 0.0,
        #                       '5_7,7': 0.0,
        #                       '6_11_12_8_9_4_1_2_3_10_13,6_11_12_8_9_4_1_2_3': 0.09375,
        #                       '6_11_12_8_9_4_1_2_3_10_13,10_13': 0.0,
        #                       '5_7,6_11_12_8_9_4_1_2_3_10_13': 0.0
        self.test_dist_dict = {'N_1,11': 0.0,
                               'N_1,12': 0.0,
                               'N_2,6': 0.1,
                               'N_2,N_1': 1.9,
                               'N_3,2': 0.0,
                               'N_3,3': 0.0,
                               'N_4,1': 1.90625,
                               'N_4,N_3': 0.09375,
                               'N_5,8': 0.0,
                               'N_5,9': 0.0,
                               'N_6,4': 0.3958333,
                               'N_6,N_4': 1.1041667,
                               'N_7,N_5': 1.0375,
                               'N_7,N_6': 0.7125,
                               'N_8,N_2': 1.90625,
                               'N_8,N_7': 0.90625,
                               'N_9,10': 0.0,
                               'N_9,13': 10.0,
                               'N_10,5': 0.0,
                               'N_10,7': 0.0,
                               'N_11,N_8': 0.09375,
                               'N_11,N_9': 0.0,
                               'N_10,N_11': 0.0}

    def test_getters(self):
        """Testing getters for class properties."""
        self.assertTrue((self.stemmaNJ.dist_matrix.round(7) == self.test_distance_matrix.round(7)).all(), msg="The distance matrix is not correct.")
        self.assertEqual(self.stemmaNJ.distance, levenshtein, msg="The returned distance is not correct.")
        self.assertEqual(self.stemmaNJ.folder_path, self.stemma_folder_path, msg="Does not return the right folder path.")
    
    def test_build_edges(self):
        """Tests the _build_edges method."""
        temp = StemmaNJ(folder_path=self.stemma_folder_path, distance=levenshtein)
        distance_dict, edge_list = temp._build_edges()
        self.assertDictEqual(distance_dict, self.test_dist_dict, msg="Does not return the correct distance dictionary.")
        self.assertCountEqual(edge_list, self.test_edges_list, msg="Does not return the correct edge list.")
        temp = StemmaNJ()
        with self.assertRaises(RuntimeError, msg="Does not raise error when _build_edges is called if _dist_matrix has not been initialized."):
            temp._build_edges()

    def test_compute(self):
        """Tests the compute method."""
        with self.assertRaises(RuntimeError, msg="Does not raise RuntimeError when compute is called but distance was not specified in the constructor or in the compute function call."):
            self.stemmaNJ_empty.compute(folder_path=self.stemma_folder_path)
    
    def test_dist(self):
        """Tests the dist method."""
        with self.assertRaises(RuntimeError, msg="Does not raise a RuntimeError when the dist method is called on a StemmaNJ object that does not have it's folder_path set."):
            self.stemmaNJ_empty.dist(levenshtein)