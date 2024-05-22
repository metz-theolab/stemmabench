from pathlib import Path
from stemmabench.algorithms.manuscript_base import ManuscriptBase
import stemmabench.algorithms.manuscript_empty as empty
from typing import Union


class Manuscript(ManuscriptBase):
    """Class for the representation of an existing manuscript in a stemma tree.

    ### Attributes:
        - label (str): The label that references the manuscript.
        - parent (ManuscriptBase): The parent of the manuscript. If it is none it is the root of the stemma tree.
        - children (list): The list of the manuscripts children. If it is empty the manuscript is a leaf node of the tree.
        - edges (list): The list of all the edges conected to the tree. Is in the same order as the children list.
        - text (str): The text of the manuscript.
    """

    def __init__(self,
                 parent: Union[ManuscriptBase, None] = None,
                 label: Union[str, None] = None,
                 children: list[ManuscriptBase] = [],
                 edges: Union[list[float], None] = None,
                 recursive: Union[dict[str,dict], None] = None,
                 text: Union[str, None] = None,
                 text_list: list[str] = None) -> None:
        """A class representing the Manuscripts that make up the nodes of a stemma.

        ### Args:
            - parent (ManuscriptBase, Optional): The parent Manuscript of the curent Manuscript. If set to None should be the root of the tree.
            - label (str, Optional): The label denoting the text.
            - children (list, Optional): A list of this Manuscripts children.
            - edges (list, Optional): A list representing the distance between the edges. Is in the same order as the list of children. 
            - recursive (dict, Optional): Dictionary representation of the current Manuscript and all its decendents. If different than None will buil all the children of the manuscript
            - from the given list. Should only be used when instantiating a stemma from the root. 
            - text (str, Optional): The contense of the text.
            - text_list (list, Optional): The list of texts present in the tree. Used with the recursive parameter, if current label
            in recursive is not in text_list will instanciate an empty manuscript. Else will instantiate a manuscript. 

        Raises:
            - ValueError: If both recursive and lable are not specified.
        """
        if text:
            self._text: Union[str, None] = text
        if recursive:
            if not text_list:
                raise ValueError("If parameter recursive is specified, parameter text_list must also be specified.")
            self._parent: Union[ManuscriptBase, None] = None
            self._children: list = []
            self._label: Union[str, None] = list(recursive.keys())[0]
            # End recursion if list of keys is empty
            if list(recursive[self.label]) == []:
                return None
            # Else for each key value add a new Manuscript if label exists in text_list else and an empty node.
            for lab in recursive[self.label].keys():
                if lab in text_list:
                    self._children.append(Manuscript(parent=self, recursive={lab:recursive[self._label][lab]}, text_list = text_list))
                else:
                    self._children.append(empty.ManuscriptEmpty(parent=self, recursive={lab:recursive[self._label][lab]}, text_list = text_list))
        elif label:
            super().__init__(label, parent, children, edges)
        else: 
            raise ValueError("If recursive is not specified then lable must be specified.")
        #super().__init__(label=label, parent=parent, children=children, edges=edges, recursive=recursive, text_list=text_list)

    @property
    def text(self):
        return self._text
        
    def __eq__(self, value: object) -> bool:
        """Returns True if both texts have the same content and the same label.

        ### Args:
            - value (object): The object to compare to.

        ### Returns:
            - bool: Value indicating if the calling object is equal to the value parameter.
        """
        if isinstance(value, Manuscript):
            return value.text == self.text and value.label == self.label
        return False

    def dump(self, folder_path: str, edge_path: Union[str, None] = None) -> None:
        """Writes all texts int the stemma to txt files placed in the specified folder.
        If the folder does not exist it will be created. Will also write all edges present in the stemma to 
        the specified edge file. If none is specified a file named edges.txt will be created in the given folder
        and the adges will be writen to that file.
        
        ### Args:
            - folder_path (str): The path the folder where the text file will be writen.
            - edge_path (str, Optional): The path to the edge file.
        """
        if not Path(folder_path).exists():
            Path(folder_path).mkdir(exist_ok=True)
        f = (Path(folder_path) / (self.label + ".txt")).open("w")
        f.write(self.text)
        f.close()
        super().dump(folder_path, edge_path)