"""
Gerenal notes:

A 3d array matrix is calculated for each triplet of segments, with 2 children and 1 parent. It is than 


Initialize the 3D matrix and at each comparison look in matrix to see if number exists. If not calculate it and
place it in the table.
"""

from os import remove
from typing import Callable, Dict, Union, Tuple, List, Set
from ctypes import CDLL, c_char_p, c_int, POINTER, Structure, string_at, c_char
from stemmabench.algorithms.stemma_algorithm import StemmaAlgo
from stemmabench.algorithms.manuscript_in_tree_empty import ManuscriptInTreeEmpty
from stemmabench.algorithms.manuscript_in_tree import ManuscriptInTree
from stemmabench.algorithms.manuscript_in_tree_base import ManuscriptInTreeBase
from stemmabench.algorithms.utils import Utils
from stemmabench.algorithms.stemma import Stemma


class StemmaRHM(StemmaAlgo):
    # TODO: Correct doc string.
    """Class that constructs a stemma using the RHM algorithm.
    
    ### Attributes:
        - folder_path (str): The path to the folder containing all the texts.
        - manuscripts (dict): The dictionay of all the texts with text labels as keys and texts as values.
        - distance (Callable): The function to be used as a distance metric.
        - _dist_matrix (numpy.ndarray): The distance matrix
    """

    def __init__(self, 
                nb_opti: int,
                segment_size: int = 1,
                strap: int = 1,
                print_dot: Union[bool, int] = False) -> None:
        # TODO: Correct doc string.
        """
        Constructor for the StemmaRHM class.

        ### Args:
            - _segment_dict (dict): The dictionary containing the list of segmants for each text
            - _cost_ref_dict (dict): The dictionary containing the costs for all the sements and all the nodes.
            - _segment_nb (int): The number of segments.
        """
        super().__init__()
        self._nb_opti = nb_opti
        self._segment_size = segment_size
        self._strap = strap
        self._print_dot = print_dot
        self._dll = CDLL("./rhm.dll")
        self._dll.compute.argtypes = [c_char_p, c_int, c_int, c_int, c_int]
        self._dll.compute.restype = c_int

    def compute(self, folder_path: Union[str, None] = None
                ) -> ManuscriptInTreeBase:
        """Builds the stemma tree. If the distance is specified in function call it will surplant the existing distance if it exists.

        ### Args:
            - folder_path (str, Optional): The path to the folder containing the texts. The path specified here will surplant the previous path defined in constructor.
            !!! All .txt files in this folder must be files containing Manuscript texts unless the file name contains the substring "edge" !!!
        
        Returns:
            - ManuscriptBase: The root of the stemma with the rest of its tree as its children.
        """
        super().compute(folder_path)
        if self._print_dot:
            self._print_dot = 1
        else:
            self._print_dot = 0
        self._dll.compute(folder_path.encode("utf-8"), self._segment_size, self._strap, self._nb_opti, 1)
        print("!!!!!!!!!!!! Python !!!!!!!!!!!!!!!!!!!!!")
        #edges = Utils.edge_to_list("edges_1.txt")
        #TODO: Deal with the case of multiple dot files
        #TODO: Convert dot files to edge files and place edge files in appropriate output folder
        #TODO: Move or delete the remaning dot files
        dot_list = Utils.get_dot_list(folder_path)
        for file in dot_list:
            edges = Utils.dot_to_edge("rhm-tree_0.dot")
        #print(edges)
        #remove("edges_1.txt")
        #self._dll.free_memory()
        return ManuscriptInTreeEmpty(parent= None, recursive=Utils.dict_from_edge(edge_list=edges), text_list=list(self.manuscripts.keys()))