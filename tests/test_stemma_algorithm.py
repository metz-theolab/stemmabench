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

    def test_stemma_algo(self):
        """Tests __init__ method."""
        testing_stemma_algo = StemmaAlgo()
        self.assertDictEqual(testing_stemma_algo.manuscripts, {},
                             msg="__init__ does not build manuscript dictionary properly.")

    def test_getters(self):
        """Tests the getter methods."""
        testing_stemma_algo = StemmaAlgo()
        self.assertEqual(testing_stemma_algo.manuscripts, {},
                         msg="The manuscripts getter dose not return the right value.")

    def test_build_edges(self):
        """Tests the _build_edges method."""
        testing_stemma_algo = StemmaAlgo()
        with self.assertRaises(NotImplementedError, msg="The empty StemmaAlgo does not raise a NotImplementedError when the _build_edges method is called."):
            testing_stemma_algo._build_edges()

    def test__eq__(self):
        """Tests the __eq__ method."""
        testing_stemma_algo = StemmaAlgo()
        with self.assertRaises(NotImplementedError, msg="The __eq__ method does not raise a NotImplementedError."):
            testing_stemma_algo.__eq__("whatever")

    def test__repr__(self):
        """Tests the __repr__ method."""
        testing_stemma_algo = StemmaAlgo()
        with self.assertRaises(NotImplementedError, msg="The __repr__ method does not raise a NotImplementedError."):
            testing_stemma_algo.__repr__()

    def test_compute(self):
        """Tests the compute method."""
        testing_stemma_algo = StemmaAlgo()
        with self.assertRaises(RuntimeError):
            testing_stemma_algo.compute(folder_path="Not/a/valid/folder/path")
