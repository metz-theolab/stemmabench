import os
from sys import platform
from typing import Union
from ctypes import CDLL, c_char_p, c_int
from stemmabench.algorithms.stemma_algorithm import StemmaAlgo
from stemmabench.algorithms.manuscript_in_tree_empty import ManuscriptInTreeEmpty
from stemmabench.algorithms.manuscript_in_tree_base import ManuscriptInTreeBase
from stemmabench.algorithms.utils import Utils


class StemmaRHM(StemmaAlgo):
    """Class that constructs a stemma using the RHM algorithm.
    
    ### Attributes:
        - folder_path (str): The path to the folder containing all the texts.
        - manuscripts (dict): The dictionay of all the texts with text labels as keys and texts as values.
        - _nb_opti (int): The number of optimistation cycles to run for each strap.
        - _strap (int): The total number of times the algorithm will be run and the results outputed. 
        Used to evaluate the stochastic nature of the algorithm.
        - _segment_size (int): The number of words per segment.
        - _keep_dot (bool): Indicates if the dot files that the c code outputs should be kept.
        - _dll (ctypes.CDLL): The dll file called by the python code.
    """

    def __init__(self, 
                nb_opti: int,
                strap: int = 1,
                segment_size: int = 1,
                keep_dot: Union[bool, int] = False) -> None:
        """
        Constructor for the StemmaRHM class.

        ### Args:
            - _nb_opti (int): The number of optimistation cycles to run for each strap.
            - _strap (int): The total number of times the algorithm will be run and the results outputed. 
            Used to evaluate the stochastic nature of the algorithm.
            - _segment_size (int): The number of words per segment.
            - _keep_dot (bool, int): Indicates if the dot files that the c code outputs should be kept.
        """
        super().__init__()
        self._nb_opti = nb_opti
        self._strap = strap
        self._segment_size = segment_size
        if keep_dot:
            self._keep_dot = 1
        else:
            self._keep_dot = 0
        if platform == "linux" or platform == "linux2":
            self._dll = CDLL(f"{os.path.realpath(__file__)}/../rhm.o")
        elif platform == "darwin":
            self._dll = CDLL(f"{os.path.realpath(__file__)}/../rhm_mac.o")
        elif platform == "win32":
            self._dll = CDLL(f"{os.path.realpath(__file__)}/../rhm.dll")
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
        if self._keep_dot:
            self._keep_dot = 1
        else:
            self._keep_dot = 0
        self._dll.compute(folder_path.encode("utf-8"), self._segment_size, self._strap, self._nb_opti, 1)
        dot_list = Utils.get_dot_list(folder_path)
        for file in dot_list:
            full_path = f"{folder_path}/{file}.dot"
            edges = Utils.dot_to_edge(full_path)
            Utils.save_edge(edges, full_path.replace(".dot", ".txt"))
            if not self._keep_dot:
                os.remove(full_path)
        return ManuscriptInTreeEmpty(parent= None, recursive=Utils.dict_from_edge(edge_list=edges), text_list=list(self.manuscripts.keys()))