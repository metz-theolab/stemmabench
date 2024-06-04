from stemmabench.algorithms.stemma_algorithm import StemmaAlgo
from stemmabench.algorithms.manuscript_empty import ManuscriptEmpty
from stemmabench.algorithms.manuscript_base import ManuscriptBase
from stemmabench.algorithms.utils import Utils
from stemmabench.algorithms.stemma import Stemma
import gzip as gz
import numpy as np
from typing import Callable, Dict, Union, Tuple, List


class StemmaRHM(StemmaAlgo):
    # TODO: Correct doc string.
    """Class that constructs a stemma using the RHM algorithm.
    
    ### Attributes:
        - folder_path (str): The path to the folder containing all the texts.
        - manuscripts (dict): The dictionay of all the texts with text labels as keys and texts as values.
        - distance (Callable): The function to be used as a distance metric.
        - _dist_matrix (numpy.ndarray): The distance matrix
    """

    def __init__(self, folder_path: Union[str, None] = None) -> None:
        # TODO: Correct doc string.
        """
        Constructor for the StemmaRHM class.

        ### Args:
            - folder_path (str, Optional): The path to the folder containing all the texts.
        """
        super().__init__(folder_path=folder_path)
        if folder_path:
            self.dist()
        else:
            self._dist_matrix: Union[np.ndarray, None] = None

    @property
    def dist_matrix(self):
        return self._dist_matrix

    def compute(self, 
                folder_path: Union[str, None] = None) -> ManuscriptBase:
        """Builds the stemma tree. If the distance is specified in function call it will surplant the existing distance if it exists.

        ### Args:
            - folder_path (str, Optional): The path to the folder containing the texts. The path specified here will surplant the previous path defined in constructor.
            !!! All .txt files in this folder must be files containing Manuscript texts unless the file name contains the substring "edge" !!!
        
        Returns:
            - ManuscriptBase: The root of the stemma with the rest of its tree as its children.
        """
        super().compute(folder_path)
        self.dist()
        return ManuscriptEmpty(parent= None, recursive=Utils.dict_from_edge(edge_list=self._build_edges()), text_list=list(self.manuscripts.keys()))
    
    def dist(self) -> None:
        """Builds the distance matix based on the RHM compression method.
        
        ### Raises:
            - RuntimeError: If the folder_path attribut is not set.
        """
        if not self.folder_path:
            raise RuntimeError("The folder_path attribut needs to be specified in order to buil distance matrix.")
        self._dist_matrix = np.ndarray((len(self.manuscripts), len(self.manuscripts)))
        # TODO: use map instead
        for key, row in zip(self.manuscripts.keys(), range(len(self.manuscripts))):
            for text, col in zip(self.manuscripts.values(), range(len(self.manuscripts))):
                self._dist_matrix[row][col] = len(gz.compress((self.manuscripts[key] + text).encode())) - len(gz.compress(self.manuscripts[key].encode()))
    
    def _build_edges(self) -> list[list[str]]:
        """Builds an edge list representing all the edges in the stemma using the RHM algorythm.

        ### Returns:
            - list: List of edges of the stemma.
        
        ### Example:
            >>> _build_edges()
            [['1','2'], ['1','3'], ['2','4'], ['2','5'], ['3','6'],['3','7']]
        """
        out = []
        # Initializing variables
        temp_dist_matrix = self._dist_matrix.copy()
        max_val = temp_dist_matrix.max() + 1
        np.fill_diagonal(temp_dist_matrix,max_val)
        labels = list(self.manuscripts.keys()) # Labels for the distance matrix
        aglos = dict(zip(labels, labels))
        idx = len(self.manuscripts)-1
        #print(temp_dist_matrix)
        # While at least one of the keys is the same as it's value
        while idx > 0:#not np.array([isinstance(x, list) for x in aglos.values()]).all():
            # Getting smallest
            coord = np.argwhere(temp_dist_matrix == temp_dist_matrix.min())[0]
            # Sort out distance matrix
            temp_dist_matrix[coord[0], coord[1]] = max_val
            temp_dist_matrix[coord[1], coord[0]] = max_val
            # generate new lab
            new_lab = "N_" + str(idx)
            #print(f"label0: {labels[coord[0]]}, key: {aglos[labels[coord[0]]]} | label1: {labels[coord[1]]}, key: {aglos[labels[coord[1]]]}")
            if aglos[labels[coord[0]]][0] != aglos[labels[coord[1]]][0]:
                idx -= 1
                # Setting the values
                # If both strings
                #print(f"New label: {new_lab}")
                if isinstance(aglos[labels[coord[0]]], str) and isinstance(aglos[labels[coord[1]]], str):
                    #print("Both strings!")
                    aglos[labels[coord[0]]] = [new_lab]
                    aglos[labels[coord[1]]] = [new_lab]
                    out.append([new_lab, labels[coord[0]]])
                    out.append([new_lab, labels[coord[1]]])
                # If 0 is list
                elif isinstance(aglos[labels[coord[0]]], list) and isinstance(aglos[labels[coord[1]]], str):
                    #print("0 is list!")
                    out.append([new_lab, aglos[labels[coord[0]]][0]])
                    out.append([new_lab, labels[coord[1]]])
                    aglos = self._update_dict(aglos, aglos[labels[coord[0]]][0], new_lab)
                    aglos[labels[coord[1]]] = [new_lab]
                    #aglos[labels[coord[0]]][0] = new_lab
                    #aglos[labels[coord[1]]] = aglos[labels[coord[0]]]
                    # If 1 is list
                elif isinstance(aglos[labels[coord[0]]], str) and isinstance(aglos[labels[coord[1]]], list):
                    #print("1 is list!")
                    out.append([new_lab, aglos[labels[coord[1]]][0]])
                    out.append([new_lab, labels[coord[0]]])
                    aglos = self._update_dict(aglos, aglos[labels[coord[1]]][0], new_lab)
                    aglos[labels[coord[0]]] = [new_lab]
                    #aglos[labels[coord[1]]][0] = new_lab
                    #aglos[labels[coord[0]]] = aglos[labels[coord[1]]]
                # If both are lists
                elif isinstance(aglos[labels[coord[0]]], list) and isinstance(aglos[labels[coord[1]]], list):
                    #print("Both lists!")
                    # TODO: Look at puting the in value list check her to see when to append which one.
                    out.append([new_lab, aglos[labels[coord[1]]][0]])
                    out.append([new_lab, aglos[labels[coord[0]]][0]])
                    aglos = self._update_dict(aglos, aglos[labels[coord[0]]][0], new_lab)
                    aglos = self._update_dict(aglos, aglos[labels[coord[1]]][0], new_lab)
                    #aglos[labels[coord[0]]][0] = new_lab
                    #aglos[labels[coord[1]]][0] = new_lab#aglos[labels[coord[0]]]
                    #print(f"Are the same object: {aglos[labels[coord[1]]] == aglos[labels[coord[0]]]}")
                #else:
                #    raise RuntimeError("Should never land her!!!")
                #print(f"Out: {out}")
                #print(aglos)
                #print(f"Coordinates: {coord[0]} , {coord[1]}")
                #print(temp_dist_matrix)
                #print("------------------------------------------------------")
        return out
    
    @staticmethod
    def cost(parent_seg: int, parent_text: int, curent_text: int, seg_mat: np.ndarray, adj_matrix: np.ndarray) -> int:
        """Cost calculated for stemma with adjacency matrix.

        ### Args:
            - parent_seg (int): The index of the parent segment in the seg_mat columns.
            - parent_text (int):The index representing the row of the text in both the seg_mat and the adj_matrix. Index is also column in adj_matrix.
            - curent_text (int): The row reference for the curent node in the adj_matrix.
            - seg_mat (np.ndarray): The matrix of text segments of all texts, with texts a rows and segment number as column. If a row is of length 0 then it is an empty node.
            - adj_matrix (np.ndarray): The adjacency matrix representing the stemma.

        ### Returns:
            - int: The cost of the stemma represented in the adj_matrix.
        """
        def C(parent: str,child: str) -> int:
            return len(gz.compress((parent + child + "\n").encode())) - len(gz.compress(parent.encode()))

        def is_leaf(idx: int) -> bool:
            return adj_matrix[:,idx].sum() == 1

        # If is root
        if adj_matrix[:,curent_text].sum() == 2:
            # Find the children indexes by finding index
            children_idx = np.where(adj_matrix[:,curent_text] == 1)[0] # TODO: Factorise this and the rest
            child0_costs = []
            child1_costs = []

            for j in range(len(seg_mat[curent_text,:])):
                child0_costs.append(StemmaRHM.cost(j, curent_text, children_idx[0], seg_mat, adj_matrix))
                child1_costs.append(StemmaRHM.cost(j, curent_text, children_idx[1], seg_mat, adj_matrix))
            return min(child0_costs) + min(child1_costs) + C(seg_mat[curent_text,j],seg_mat[curent_text,j])

        # If current node is empty
        if len(seg_mat[curent_text,:]) == 0:
            return 0

        # Recursion end
        # TODO: Find out what unknown means (If node is flaged as empty?)
        if is_leaf(curent_text):
            # Match parent segment with current node segment.
            matching_flag = True
            for seg in seg_mat[curent_text,:]:
                if seg == seg_mat[parent_text, parent_seg]:
                    matching_flag = False
            if matching_flag:
                return float("inf")
            return 0

        # Find the children indexes by finding index
        children_idx = np.where(adj_matrix[:,curent_text] == 1)[0]
        # Remove the parent index
        children_idx = children_idx[children_idx != parent_text]

        # Run through all the segments of child and compare to current segment
        child0_costs = []
        child1_costs = []
        # TODO: Deal with differing length texts
        if len(seg_mat[curent_text,:]) > 0:
            for i in range(len(seg_mat[curent_text,:])):
                child0_costs.append(C(seg_mat[parent_text,parent_seg],seg_mat[curent_text,curent_text]) + StemmaRHM.cost(i, curent_text, children_idx[0], seg_mat, adj_matrix))
                child1_costs.append(C(seg_mat[parent_text,parent_seg],seg_mat[curent_text,curent_text]) + StemmaRHM.cost(i, curent_text,children_idx[1], seg_mat, adj_matrix))
        return min(child0_costs) + min(child1_costs)
    


    @staticmethod
    def _update_dict(ref_dict: Dict[str, List[str]], old_value: str, new_value: str) -> Dict[str, List[str]]:
        """Updates all values of the dictionary that are equal to old_value to new_value.
        
        ### Args:
            - ref_dict (dict): The dictionary that will have it's values updated.
            - old_value (str): The old values to be found in the dictionary and replaced with new_value.
            - new_value (str): The new value that will take the place of all the old values.

        ### Returns:
            - dict: The dictionary ref_dict with all old_values replaced with new_values.
        """
        for k in ref_dict:
            if ref_dict[k][0] == old_value:
                ref_dict[k][0] = new_value
        return ref_dict