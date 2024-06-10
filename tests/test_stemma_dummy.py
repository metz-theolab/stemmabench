"""
Unit tests for the StemmaDummy class.
"""
import unittest
from stemmabench.algorithms.stemma_dummy import StemmaDummy


class TestStemmaDummy(unittest.TestCase):
    """Unit tests for the stemmaDummy class.
    """

    def setUp(self) -> None:
        """Setup the unit test.
        """
        self.stemma_folder_path = "tests/test_data/test_stemma"
        self.test_random_levels = [['3'],
                                   ['4', '7'],
                                   ['9', '1', '11', '6'],
                                   ['10', '12', '13', '2', '5', '8']]
        self.test_edges_list = [['3', '4'], ['3', '7'], ['4', '9'],
                                ['4', '1'], ['7', '11'], ['7', '6'],
                                ['9', '10'], ['9', '12'], ['1', '13'],
                                ['1', '2'], ['11', '5'], ['11', '8']]

    def test_stemma_dummy(self):
        """Tests the __init__ method."""
        with self.assertRaises(ValueError, msg="The __init__ method does not raise a ValueError if the width parameter passed to the method is not an int."):
            StemmaDummy(width=1.5)
        testing_stemma_dummy = StemmaDummy(width=5)
        self.assertEqual(testing_stemma_dummy._width, 5,
                         msg="The __init__ method does not set the width attribute properly.")

    def test_getters(self):
        testing_stemma_dummy = StemmaDummy(width=5)
        self.assertEqual(testing_stemma_dummy.width, 5,
                         msg="The width method does not return the correct width value.")

    def test_build_random_levels(self):
        """Tests the _build_random_levels method."""
        testing_stemma_dummy = StemmaDummy(width=5)
        testing_stemma_dummy._manuscripts = {'1': 'This is a text.',
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
        levels = testing_stemma_dummy._build_random_levels()
        self.assertTrue(len(
            levels[0]) == 1, msg="The _build_random_levels method does not create the root list correctly.")
        self.assertTrue(len(
            levels[1]) == 5, msg="The _build_random_levels method does not create the right number of children in the 2nd level.")
        self.assertTrue(len(
            levels[2]) == 7, msg="The _build_random_levels method does not create the right number of children in the 2nd level.")

    def test_build_edges(self):
        """Tests the _build_edges method."""
        testing_stemma_dummy = StemmaDummy(width=2)
        self.assertCountEqual(testing_stemma_dummy._build_edges(
            levels=self.test_random_levels), self.test_edges_list, msg="The _build_edges method does not return a valid edge list.")

    def test_compute(self):
        """Tests the compute method. (All other functionalities of this method are covered in other unit tests.)"""
        testing_stemma_dummy = StemmaDummy(width=5)
        testing_stemma_dummy.compute(
            folder_path=self.stemma_folder_path, width=2)
        self.assertEqual(testing_stemma_dummy.width, 2,
                         msg="The compute methode does not set the width attribute of the StemmaDummy object.")
