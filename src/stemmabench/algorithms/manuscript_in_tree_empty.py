from typing import Union, List, Dict
from stemmabench.algorithms.manuscript_in_tree_base import ManuscriptInTreeBase
import stemmabench.algorithms.manuscript_in_tree as man


class ManuscriptInTreeEmpty(ManuscriptInTreeBase):
    """Class for the representation of an existing manuscript in a stemma tree.

    ### Attributes:
        - label (str): The label that references the manuscript.
        - parent (ManuscriptInTreeBase): The parent of the manuscript. If it is none it is the root of the stemma tree.
        - children (list): The list of the manuscripts children. If it is empty the manuscript is a leaf node of the tree.
        - edges (list): The list of all the edges conected to the tree. Is in the same order as the children list.
    """

    def __init__(self,
                 parent: Union[ManuscriptInTreeBase, None] = None,
                 label: Union[str, None] = None,
                 children: List[ManuscriptInTreeBase] = [],
                 edges: Union[List[float], None] = None,
                 recursive: Union[Dict[str, dict], None] = None,
                 text_list: Union[List[str], None] = None) -> None:
        """A class representing the Manuscripts that make up the nodes of a stemma.

        ### Args:
            - parent (ManuscriptInTreeBase, Optional): The parent Manuscript of the curent Manuscript. If set to None should be the root of the tree.
            - label (str, Optional): The label denoting this node.
            - children (list, Optional): A list of this Manuscripts children.
            - edges (list, Optional): A list representing the distance between the edges. Is in the same order as the list of children. 
            - recursive (dict, Optional): Dictionary representation of the current Manuscript and all its decendents. If different than None will build all the children of the manuscript
            - from the given list. Should only be used when instantiating a stemma from the root.
            - text_list (list, Optional): The list of texts present in the tree. Used with the recursive parameter, if current label
            in recursive is not in text_list will instanciate an empty manuscript. Else will instantiate a manuscript. 

        Raises:
            - ValueError: If both recursive and lable are not specified.
        """
        if recursive:
            if text_list != []:
                raise ValueError(
                    "If parameter recursive is specified, parameter text_list must also be specified.")
            self._parent: Union[ManuscriptInTreeBase, None] = parent
            self._children: List[ManuscriptInTreeBase] = []
            self._label: Union[str, None] = list(recursive.keys())[0]
            self.recursive_init(recursive, text_list)
        elif label:
            super().__init__(label, parent, children, edges)
        else:
            raise ValueError(
                "If recursive is not specified then label must be specified.")

    def recursive_init(self,
                       recursive: Dict[str, dict],
                       text_list: List[str]) -> None:
        """When building tree from a dictionary will add all the children for the current manuscript and propagate
        instantiation to the children.

        ### Args:
            - recursive (dict): Dictionary representation of the current Manuscript and all its decendents. If different than None will build all the children of the manuscript
            - from the given list.
            - text_list (list): The list of texts present in the tree. Used with the recursive parameter, if current label
            in recursive is not in text_list will instanciate an empty manuscript. Else will instantiate a manuscript. 
        """
        if not recursive.get(self.label):
            return None
        for lab in recursive[self.label].keys():
            if lab in text_list:
                self._children.append(man.ManuscriptInTree(parent=self, recursive={
                                      lab: recursive[self._label][lab]}, text_list=text_list))
            else:
                self._children.append(ManuscriptInTreeEmpty(parent=self, recursive={
                                      lab: recursive[self._label][lab]}, text_list=text_list))

    def __eq__(self, value: object) -> bool:
        """Returns True if both texts have the same content and the same label.

        ### Args:
            - value (object): The object to compare to.

        ### Returns:
            - bool: Value indicating if the calling object is equal to the value parameter.
        """
        if isinstance(value, ManuscriptInTreeEmpty):
            return value.label == self.label
        return False

    def __repr__(self) -> str:
        """String representation of the Manuscript.

        ### Returns:
            - str: String representation of the manuscript.
        """
        return self.label
