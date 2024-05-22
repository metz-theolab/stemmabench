from stemmabench.algorithms.stemma_algorithm import StemmaAlgo
from stemmabench.algorithms.manuscript import Manuscript
import numpy as np
from textdistance import levenshtein, jaccard
from typing import Callable, Dict, Union


class StemmaNJ(StemmaAlgo):
    """Class that constructs a stemma using the Neighbor-Joining algorithm.
    
    ### Attributes:
        - palceholder
    """

    #TODO: Remove this.
    TESTING_FOLDER = "../../../tests/test_data"

    def __init__(self,
                 folder_path: Union[str, None] = None,
                 distance: Union[Callable, None] = None) -> None:
        if distance == None:
            raise ValueError("No distance specified.")
        super().__init__(folder_path=folder_path)
        self.dist(distance)
    
    def compute(self, folder_path: Union[str, None] = None) -> Manuscript:
        """Builds the stemma tree.

        ### Args:
            - folder_path (str, Optional): The path to the folder containing the texts. The path specified here will surplant the previous path defined in constructor.
            !!! All .txt files in this folder must be files containing Manuscript texts unless the file name contains the substring "edge" !!!
            - distance (distance, Optional): The distance to be used in the construction of the tree.
        
        Returns:
            - Manuscript: The root of the stemma with the rest of its tree as its children.

        Raises:
            - ValueError: If both the folder_path parameter and the folder_path have not been specified.
        """
        super().compute(folder_path)
        raise NotImplementedError()
        
        return Manuscript(parent= None, recursive=_build_dict())
    
    def _build_dict(self, distance=None) -> Dict[str, dict]:
        """Returns the dictionary representation of the tree based to ba used for instanciation.
        This is where the algorythme is implemented.

        ### Args:
            - distance (?, Optional): The distance metric used for the the contruction of the tree.
        """
        pass

    def dist(self, distance: Callable) -> None:
        """Builds the distance matix based on the provided distance function and sets the attribute _dist_matrix.
        
        ### Args:
            - distance (Callable, Required): A function that takes as parameters 2 strings and that returns the distance between them.
        """
        if not self.folder_path:
            raise RuntimeError("The folder_path attribut needs to be specified in order to buil distance matrix.")
        self._dist_matrix = np.ndarray((len(self.manuscripts), len(self.manuscripts)))
        # TODO: use map instead
        for key, row in zip(self.manuscripts.keys(), range(len(self.manuscripts))):
            print(f"nb manuscript rows: {len(self.manuscripts)}")
            for text, col in zip(self.manuscripts.values(), range(len(self.manuscripts))):
                print(f"nb manuscript rows: {len(self.manuscripts)}")
                self._dist_matrix[row][col] = distance(self.manuscripts[key], text)
        

    # Returns the min value, it's column and it's row
    @staticmethod 
    def _get_min(dist: np.ndarray) -> tuple[float, int, int]:
        """When given a matrix returns a tuple containing the minimum value in the matrix, its column position and its row position in that order.
        
        ### Args:
            - dist (np.ndarray, Required): Distance matrix of the of all elements.

        ### Returns:
            - tuple: (minimum value in matrix, its column coordinate, its row coordinate)
        """
        coord = np.argwhere(dist == dist.min())
        return dist.min(), coord[0][0], coord[0][1]
    
    # The Q distance for the neighbour joining algo
    @staticmethod
    def _Q_dist(dist: np.ndarray, zero_diag: bool = True) -> np.ndarray:
        # TODO: Insert the right terms for the objects in description.
        """Given a distance matrix returns its !!!insert name here!!! matrix.
        
        ### Args:
            - dist (np.ndarray, Required): Distance matrix of the of all elements.
            - zero_diag (bool, Optional): Indicates if the resulting matrix should have it's diagonal values set to 0.

        ### Returns:
            - np.ndarray: Matrix of !!!insert name here!!! distance.
        """
        # Q = (n - 2)D - R_i - R_j
        out = (dist.shape[0] - 2) * dist - dist.sum(axis=0) - dist.sum(axis=1)

        if zero_diag:
            np.fill_diagonal(out,0)

        return out

    @staticmethod
    def _aglo(dist_mat: np.ndarray) -> np.ndarray:
        # TODO: Insert the right terms for the objects in description.
        # TODO: Check if description is realy what this does.
        # TODO: Add dict construction output to function.
        # TODO: What to do when 2 distances are equal.
        """Performs one step in the distance matrix aglomeration process.
        
        ### Args:
            - dist_mat (np.ndarray, Requred): A !!!insert name here!!! distance matrix to be aglomerated by one step.

        ### Returns:
            - np.ndarray: The distance matrix aglomerated by one step.
        """
        
        # Calculate divergence matrix
        Q = StemmaNJ._Q_dist(dist_mat)

        # Find min of divergence matrix
        #temp = StemmaNJ._get_min(Q)
        min = dist_mat.min()
        coord = np.argwhere(dist_mat == min)[0]

        # Removed aglomerated rows and columns
        #out = np.delete(np.delete(dist_mat, obj=temp[1:], axis=0), obj=temp[1:], axis=1)
        out = np.delete(np.delete(dist_mat, obj=coord, axis=0), obj=coord, axis=1)

        # Vector to be appended to side of reduced matrix
        vect = 0.5*(np.delete(Q[coord[1]], coord) + np.delete(Q[coord[0]], coord) - min)

        # Stick new U distance vectors on the right and bottom of the original distance matrix
        out =  np.row_stack((np.column_stack((out, vect)), np.append(vect, 0)))

        # Return tuple with new aglomerated matrix as first element, the row of the aglomerated texts and the column of aglo text.
        return out
    
    
    
    
