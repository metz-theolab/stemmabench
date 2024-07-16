"""
Unit tests for the StemmaNJ class.
"""
import numpy as np
import unittest
from textdistance import levenshtein
from stemmabench.algorithms.stemma_NJ import StemmaNJ


class TestStemmaNJ(unittest.TestCase):
    """Unit tests for the StemmaNJ class.
    """

    def setUp(self) -> None:
        """Setup the unit test.
        """
        self.stemma_folder_path = "tests/test_data/test_stemma"
        self.test_edges_list = [['N_1', 'c'],
                                ['N_1', 'd'],
                                ['N_2', 'a'],
                                ['N_2', 'N_1'],
                                ['N_3', 'b'],
                                ['N_3', 'e'],
                                ['N_2', 'N_3']]
        self.dist_mat_edge_test = np.array([[0, 17, 21, 31, 23],
                                            [17, 0, 30, 34, 21],
                                            [21, 30, 0, 28, 39],
                                            [31, 34, 28, 0, 43],
                                            [23, 21, 39, 43, 0]])
        self.test_distance_matrix = np.array([[0.,  5.,  8.,  8., 15.,  2.,  2.,  3.,  5.,  7.,  5.,  4.,  4.],
                                              [5.,  0.,  4.,  4., 10.,  3.,  3.,
                                                  2.,  0.,  2.,  0.,  2.,  2.],
                                              [8.,  4.,  0.,  0., 14.,  7.,  7.,
                                                  5.,  4.,  2.,  4.,  6.,  6.],
                                              [8.,  4.,  0.,  0., 14.,  7.,  7.,
                                                  5.,  4.,  2.,  4.,  6.,  6.],
                                              [15., 10., 14., 14.,  0., 13., 13.,
                                                  12., 10., 12., 10., 12., 12.],
                                              [2.,  3.,  7.,  7., 13.,  0.,  0.,
                                                  2.,  3.,  5.,  3.,  2.,  2.],
                                              [2.,  3.,  7.,  7., 13.,  0.,  0.,
                                                  2.,  3.,  5.,  3.,  2.,  2.],
                                              [3.,  2.,  5.,  5., 12.,  2.,  2.,
                                                  0.,  2.,  4.,  2.,  3.,  3.],
                                              [5.,  0.,  4.,  4., 10.,  3.,  3.,
                                                  2.,  0.,  2.,  0.,  2.,  2.],
                                              [7.,  2.,  2.,  2., 12.,  5.,  5.,
                                                  4.,  2.,  0.,  2.,  4.,  4.],
                                              [5.,  0.,  4.,  4., 10.,  3.,  3.,
                                                  2.,  0.,  2.,  0.,  2.,  2.],
                                              [4.,  2.,  6.,  6., 12.,  2.,  2.,
                                                  3.,  2.,  4.,  2.,  0.,  0.],
                                              [4.,  2.,  6.,  6., 12.,  2.,  2.,  3.,  2.,  4.,  2.,  0.,  0.]])
        self.edge_dictionary_reference = {'N_1,c': 11.0,
                                          'N_1,d': 17.0,
                                          'N_2,a': 4.75,
                                          'N_2,N_1': 7.25,
                                          'N_3,b': 6.75,
                                          'N_3,e': 14.25,
                                          'N_2,N_3': 4.75}

    @staticmethod
    def distance_test(text1: str, text2: str) -> float:
        """Function used to test distance parameter of the dist method.
        """
        return abs(len(text1) - len(text2))

    def test_distance_check(self):
        """Tests the error raising in the constructor."""
        def testing_function(text1: str, text2: str) -> int:
            """Function used for testing is_similaritys d(x,x) = 0 condition."""
            return len(text1) + len(text2)
        with self.assertRaises(ValueError, msg="Does not raise ValueError when compute is called with an invalid distance function."):
            testing_stemma = StemmaNJ(distance=testing_function)

    def test_getters(self):
        """Testing getters for class properties."""
        self.stemmaNJ = StemmaNJ(distance=levenshtein)
        self.stemmaNJ.compute(folder_path=self.stemma_folder_path)
        self.assertTrue((self.stemmaNJ.dist_matrix.round(7) == self.test_distance_matrix.round(
            7)).all(), msg="The distance matrix is not correct.")
        self.assertEqual(self.stemmaNJ.distance, levenshtein,
                         msg="The returned distance is not correct.")

    def test_build_edges(self):
        """Tests the _build_edges method."""
        temp_stem = StemmaNJ(distance=levenshtein)
        temp_stem._dist_matrix = self.dist_mat_edge_test
        temp_stem._manuscripts = {
            "a": "", "b": "", "c": "", "d": "", "e": "", }
        distance_dict, edge_list = temp_stem._build_edges()
        self.assertDictEqual(distance_dict, self.edge_dictionary_reference,
                             msg="Does not return the correct distance dictionary.")
        self.assertCountEqual(edge_list, self.test_edges_list,
                              msg="Does not return the correct edge list.")

    def test_dist(self):
        """Tests that the dist method build and sets the corredt distance matrix"""
        testing_stemma = StemmaNJ(distance=levenshtein)
        testing_stemma._manuscripts = {
            "m1": "text1", "m2": "text2", "m3": "text3"}
        testing_stemma.dist(distance=levenshtein)
        self.assertTrue((testing_stemma.dist_matrix == [
                        [0., 1., 1.], [1., 0., 1.], [1., 1., 0.]]).all())

    def test_is_similarity(self):
        """Tests the is_similarity method."""
        with self.assertRaises(ValueError, msg="Does not raise an error if distance parameter is not callable."):
            StemmaNJ.is_similarity("test")

        def testing_function(text1: str, text2: str) -> str:
            """Function used for testing is_similaritys return a number condition."""
            return "test"

        with self.assertRaises(ValueError, msg="Does not raise an error if distance parameter does not return a number."):
            StemmaNJ.is_similarity(testing_function)

        def testing_function(text1: str, text2: str) -> int:
            """Function used for testing is_similaritys d(x,x) = 0 condition."""
            return len(text1) + len(text2)

        self.assertFalse(StemmaNJ.is_similarity(
            testing_function), msg="Does not retun false if distance parameter function does not respect d(x,x) = 0.")

        def testing_function(text1: str, text2: str) -> int:
            """Function used for testing is_similaritys d(x,y) = d(y,x) condition."""
            if len(text1) < len(text2):
                shortest = text1
            else:
                shortest = text2
            for i in range(len(shortest)):
                if text1[i] != text2[i]:
                    return ord(text1[i]) - ord(text2[i])
            return 0

        self.assertFalse(StemmaNJ.is_similarity(
            testing_function), msg="Does not retun false if distance parameter function does not respect d(x,y) = d(y,x).")
