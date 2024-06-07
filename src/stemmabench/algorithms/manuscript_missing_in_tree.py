from typing import Union, List
from stemmabench.algorithms.manuscript_in_tree_base import ManuscriptInTreeBase


class ManuscriptMissingInTree(ManuscriptInTreeBase):
    """Class for the representation of a missing manuscript in a stemma tree.

    ### Attributes:
        - label (str): The label that references the manuscript.
        - parent (ManuscriptBase): The parent of the manuscript. If it is none it is the root of the stemma tree.
        - children (list): The list of the manuscripts children. If it is empty the manuscript is a leaf node of the tree.
        - edges (list): The list of all the edges conected to the tree. Is in the same order as the children list.
    """

    def __init__(self,
                 label: str,
                 parent: Union[ManuscriptInTreeBase, None],
                 children: Union[List[ManuscriptInTreeBase], None] = None,
                 edges: Union[List[float], None] = None) -> None:
        """Class for the representation of a missing manuscript in a stemma tree.

        ### Args:
            - label (str): The label denoting the text.
            - parent (ManuscriptBase): The parent text of the curent text. If set to None is the root manuscript of the tree.
            - children (list, Optional): A list of this Manuscripts children.
            - edges (list, Optional): A list representing the distance between the edges. 
            In the same order as the children array.

        ### Raises:
            - NotImplementedError: Not implemented for this class.
        """
        raise NotImplementedError()
