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
        self.stemmaDummy_empty = StemmaDummy()
        self.stemmaDummy = StemmaDummy(self.stemma_folder_path, width=5)
        self.stemmaDummy_seed = StemmaDummy(folder_path=self.stemma_folder_path, seed=1)
        self.stemmaDummy.compute()
        self.test_random_levels = [['3'], 
                                   ['4', '7'], 
                                   ['9', '1', '11', '6'], 
                                   ['10', '12', '13', '2', '5', '8']]
        self.test_edges_list = [['3', '4'],['3', '7'],['4', '9'],
                                ['4', '1'],['7', '11'],['7', '6'],
                                ['9', '10'],['9', '12'],['1', '13'],
                                ['1', '2'],['11', '5'],['11', '8']]

    def test_StemmaDummy(self):
        """Tests the __init__ method."""
        with self.assertRaises(ValueError, msg="The __init__ method does not raise a ValueError if the width parameter passed to the method is not an int."):
            StemmaDummy(folder_path=self.stemma_folder_path, width=1.5)
        self.assertEqual(self.stemmaDummy.width, 5, msg="The __init__ method does not set the width attribute properly.")

    def test_getters(self):
        self.assertEqual(self.stemmaDummy.width, 5, msg="The width method does not return the correct width value.")

    def test_build_random_levels(self):
        """Tests the _build_random_levels method."""
        temp = self.stemmaDummy._build_random_levels()
        self.assertTrue(len(temp[0]) == 1 , msg="The _build_random_levels method does not create the root list correctly.")
        self.assertTrue(len(temp[1]) == 5 , msg="The _build_random_levels method does not create the right number of children in the 2nd level.")
        self.assertTrue(len(temp[2]) == 7 , msg="The _build_random_levels method does not create the right number of children in the 2nd level.")

    def test_build_edges(self):
        """Tests the _build_edges method."""
        self.assertCountEqual(self.stemmaDummy_seed._build_edges(levels=self.test_random_levels), self.test_edges_list, msg="The _build_edges method does not return a valid edge list.")

    def test_compute(self):
        """Tests the compute method. (All other functionalities of this method are covered in other unit tests.)"""
        temp = StemmaDummy(folder_path=self.stemma_folder_path)
        temp.compute()
        self.assertEqual(temp.folder_path, self.stemma_folder_path, msg="The compute method does not set the folder path properly from the self._folder_path attribut defined in constructor.")
        temp = StemmaDummy()
        temp.compute(folder_path=self.stemma_folder_path)
        self.assertEqual(temp.folder_path, self.stemma_folder_path, msg="The compute method does not set the folder path properly from the parameter folder_path specified in the compute method.")
        temp = StemmaDummy(folder_path=self.stemma_folder_path)
        temp.compute(width=2)
        self.assertEqual(temp.width, 2, msg="The compute methode does not set the width attribute of the StemmaDummy object.")