from stemmabench.algorithms.stemma_algorithm import StemmaAlgo
from stemmabench.algorithms.manuscript_empty import ManuscriptEmpty
from stemmabench.algorithms.manuscript_base import ManuscriptBase
from stemmabench.algorithms.utils import Utils
import numpy as np
from typing import Callable, Dict, Union, Tuple


class StemmaNJ(StemmaAlgo):
    """Class that constructs a stemma using the Neighbor-Joining algorithm.
    
    ### Attributes:
        - folder_path (str): The path to the folder containing all the texts.
        - manuscripts (dict): The dictionay of all the texts with text labels as keys and texts as values.
        - distance (Callable): The function to be used as a distance metric.
        - _dist_matrix (numpy.ndarray): The distance matrix
    """

    def __init__(self,
                 folder_path: Union[str, None] = None,
                 distance: Union[Callable, None] = None) -> None:
        """
        Constructor for the StemmaNJ class.

        ### Args:
            - folder_path (str, Optional): The path to the folder containing all the texts.
            - distance (Callable, Optional): A function that takes 2 strings as parameters and returns a numeric value which is
            the distance between the 2 strings.
        """
        super().__init__(folder_path=folder_path)
        self._distance: Union[Callable, None] = distance
        if distance:
            self.dist(distance)
        else:
            self._dist_matrix: Union[np.ndarray, None] = None

    @property
    def distance(self):
        return self._distance
    
    @property
    def dist_matrix(self):
        return self._dist_matrix

    def compute(self, 
                folder_path: Union[str, None] = None,
                distance: Union[Callable, None] = None) -> ManuscriptBase:
        """Builds the stemma tree. If the distance is specified in function call it will surplant the existing distance if it exists.

        ### Args:
            - folder_path (str, Optional): The path to the folder containing the texts. The path specified here will surplant the previous path defined in constructor.
            !!! All .txt files in this folder must be files containing Manuscript texts unless the file name contains the substring "edge" !!!
            - distance (Callable, Optional): A function that takes 2 strings as parameters and returns a numeric value which is
            the distance between the 2 strings.
        
        Returns:
            - Manuscript: The root of the stemma with the rest of its tree as its children.

        Raises:
            - RuntimeError: If the _distance attribute has not been specified in the constructor and has not been specified in the compute function call.
        """
        super().compute(folder_path)
        if not self.distance and not distance:
            raise RuntimeError("The _distance was not specified in the constructor, therefore the distance parameter must be specified.")
        if distance:
            self.dist(distance=distance)
        edges_dict, edges_list = self._build_edges()
        out = ManuscriptEmpty(parent= None, recursive=Utils.dict_from_edge(edge_list=edges_list), text_list=list(self.manuscripts.keys()))
        out.set_edges(edges_dict)
        return out
    
    def dist(self, distance: Callable) -> None:
        """Builds the distance matix based on the provided distance function and sets the attribute _dist_matrix.
        
        ### Args:
            - distance (Callable, Required): A function that takes as parameters 2 strings and that returns the distance between them.
        
        ### Raises:
            - RuntimeError: If the folder_path attribut is not set.
        """
        self._distance = distance
        if not self.folder_path:
            raise RuntimeError("The folder_path attribut needs to be specified in order to buil distance matrix.")
        self._dist_matrix = np.ndarray((len(self.manuscripts), len(self.manuscripts)))
        # TODO: use map instead
        for key, row in zip(sorted(self.manuscripts.keys()), range(len(self.manuscripts))):
            for text, col in zip([self.manuscripts[k] for k in sorted(self.manuscripts.keys())], range(len(self.manuscripts))):
                self._dist_matrix[row][col] = distance(self.manuscripts[key], text)

    def _build_edges(self) -> Tuple[Dict[str, float], list[list[str]]]:
        """Builds list of edges as well as the associated dictionayr containing the edge distances.
        
        ### Returns:
            - dict: The dictionary with edges as keys and distences as values.
            - list: List of edges.
        """
        if not isinstance(self._dist_matrix, np.ndarray):
            raise RuntimeError("Can not call _build_edges if _dist_matrix has not been initialized.")
        temp_dist_matrix = self._dist_matrix.copy()
        labels = sorted(list(self.manuscripts.keys()))
        edges_labels = []
        edges_distance = []
        while temp_dist_matrix.shape[0] > 2:
            temp_dist_matrix, labels, df, f_lab, dg, g_lab = self._aglo(temp_dist_matrix, labels)
            edges_labels.append([labels[len(labels)-1],f_lab])
            edges_distance.append(df)
            edges_labels.append([labels[len(labels)-1],g_lab])
            edges_distance.append(dg)
        edges_distance.append(temp_dist_matrix[0,1])
        edges_labels.append([labels[0], labels[1]])
        edges_dict_labels = [l[0] + "," + l[1] for l in edges_labels]
        print(edges_labels)
        out = {edges_dict_labels[i]: edges_distance[i] for i in range(len(edges_dict_labels))}
        return out, edges_labels

    def _aglo(self, dist_mat: np.ndarray, labels: list) -> Tuple[np.ndarray, list[str], float, str, float, str]:
        """Performs one step in the distance matrix aglomeration process and returns all information needed for Neighbour Joining.
           Does not work for matrix 2*2. 
        
        ### Args:
            - dist_mat (np.ndarray): A !!!insert name here!!! distance matrix to be aglomerated by one step.
            - labels (list): The list of labels that corespond to the distance matrix labels. Can be found in manuscrips.keys().

        ### Returns:
            - np.ndarray: The distance matrix aglomerated by one step.
            - list: The list of labels for the new aglomerated matrix.
            - folat: Distance between the the aglomerrated manuscript f and the new node u.
            - str: The label of the manuscript f.
            - folat: Distance between the the aglomerrated manuscript g and the new node u.
            - str: The label of the manuscript g.
        """
        # Calculate divergence matrix
        Q = (dist_mat.shape[0] - 2) * dist_mat - (dist_mat.sum(axis=0).reshape((dist_mat.shape[0],1)) + dist_mat.sum(axis=1))
        Q = Q.round(7)
        np.fill_diagonal(Q,0)
        # Find min of divergence matrix
        coord = np.argwhere(Q == Q.min())[0]
        # The distances d(f,u) and d(g,u)
        df = round(0.5*dist_mat[coord[0],coord[1]] + (dist_mat[coord[0],].sum() - dist_mat[coord[1],].sum())/(2*(dist_mat.shape[0] - 2)), 7)
        dg = round(dist_mat[coord[0],coord[1]] - df, 7)
        # Removed aglomerated rows and columns
        out = np.delete(np.delete(dist_mat, obj=coord, axis=0), obj=coord, axis=1).round(7)
        # Vector to be appended to side of reduced matrix
        vect = 0.5*(np.delete(dist_mat[coord[0],], [coord[0],coord[1]]) + np.delete(dist_mat[coord[1],], [coord[0],coord[1]]) - dist_mat[coord[0],coord[1]])
        vect = vect.round(7)
        # Stick new U distance vectors on the right and bottom of the original distance matrix
        out =  np.row_stack((np.column_stack((out, vect)), np.append(vect, 0))).round(7)
        # Extracting labels and creating new node label
        f_label = labels[coord[0]]
        g_label = labels[coord[1]]
        new_label = "N_" + str(self.dist_matrix.shape[0] - len(labels) + 1)
        labels = list(np.delete(labels, coord))
        labels.append(new_label)
        print(labels)
        print(new_label)
        print(f_label)
        print(g_label)
        print(coord)
        print(dist_mat)
        print(Q)
        return out, labels, df, f_label, dg, g_label