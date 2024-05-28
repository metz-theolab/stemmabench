from pathlib import Path
from typing import Union, Dict
import os

class ManuscriptBase:
    """Base class for representing manuscripts in a stemma tree.

    ### Attributes:
        - label (str): The label that references the manuscript.
        - parent (ManuscriptBase): The parent of the manuscript. If it is none it is the root of the stemma tree.
        - children (list): The list of the manuscripts children. If it is empty the manuscript is a leaf node of the tree.
        - edges (list): The list of all the edges conected to the tree. Is in the same order as the children list.
    """

    def __init__(self,
                 label: str,
                 parent: Union["ManuscriptBase", None],
                 children: list["ManuscriptBase"] = [],
                 edges: Union[list[float], None] = [],
                 #recursive: Union[dict[str,dict], None] = None,
                 #text_list: list[str] = []
                 ) -> None:
        """Base class for representing manuscripts.

        ### Args:
            - label (str): The label denoting the text.
            - parent (text): The parent text of the curent text. If set to None is the root manuscript of the tree.
            - children (list, Optional): A list of this Manuscripts children.
            - edges (list, Optional): A list representing the distance between the edges. In the same order as the children list.
            If different than None will ignore all other parameters except parent
            and will build all the children of the manuscript from the given list.

        ### Raises:
            - ValueError: If label is not a string.
            - ValueError: If parent different than None or not of type ManuscriptBase.
            - ValueError: If children not of type list.
        """
        # Setting label
        if not isinstance(label, str): # and not recursive
            raise ValueError("Parameter label must be a string.")
        self._label: str = label
        self._edges: Union[list[float], None] = edges
        #elif not recursive:
        #    raise RuntimeError("If the parameter recursive is not specified then the label must be specified.")
        # Setting parent
        if not parent or isinstance(parent, ManuscriptBase):
                self._parent: Union[ManuscriptBase, None] = parent
        else:
            raise ValueError("Parent must be None or of type ManuscriptBase.")
        # Seting children
        if isinstance(children, list):
                self._children: list["ManuscriptBase"] = children
        else:
            raise ValueError("The children must be of type list.")
        # Setting edges
        #if edges != None:
                #if len(children) != len(edges):
                #    raise RuntimeError("The edges array must be of same length as the children array.")
        
        # If recursivity is specified. !!!!! Not factored due to ciscular imports !!!!!!
        #if recursive:
        #    self._label: Union[str, None] = list(recursive.keys())[0]
        #    # End recursion if list of keys is empty
        #    if list(recursive[self.label]) == []:
        #        return None
        #    # Else for each key value add a new Manuscript if label exists in text_list else and an empty node.
        #    for lab in recursive[self.label].keys():
        #        if lab in text_list:
        #            self._children.append(Manuscript(parent=self, recursive={lab:recursive[self._label][lab]}, text_list = text_list))
        #        else:
        #            self._children.append(ManuscriptEmpty(parent=self, recursive={lab:recursive[self._label][lab]}, text_list = text_list))

    @property
    def parent(self):
        return self._parent
    
    @property
    def children(self):
        return self._children
    
    @property
    def label(self):
        return self._label
    
    @property
    def edges(self):
        return self._edges
    
    def __repr__(self) -> str:
        """String representation of the Manuscript.
        
        ### Returns:
            - str: String representation of the manuscript.
        """
        return self.label

    def dict(self, include_edges: bool = False) -> Dict[str, dict]:
        """ Constructs dictionary representaion of tree from the Manuscript it is called from.

        ### Args:
            - include_edges (bool, Optional): Indicates if the tree should contain the edges. Default to false.

        ### Resturns:
            - dict: Dictionary representation of Manuscript and all of its children.
        """
        if include_edges:
            if len(self.children) == 0:
                return {self.label: {}}
            else:
                return {"label": self.label, 
                        "edges": {child.label: edge for edge,child in zip(self.edges, self.children)},
                        "children": {child.label: child.dict() for child in self.children}}
        else:
            if not self.children or len(self.children) == 0:
                return {self.label: {}}
            else:
                out = {}
                for child in self.children:
                     out.update(child.dict())
                return {self.label: out}

    def dump(self, folder_path: str, edge_path: Union[str, None] = None) -> None:
        """Adds the edge to the edge file present in given folder.
            If the folder does not exist it will be created.
            If the edge file does not existe it will be created.
            Will look through edge file if it exists to check that edge is alredy present in edge file. 
        
        ### Args:
            - folder_path (str): The path the folder where the text file will be writen.
            - edge_path (str, Optional): The path to the edge file.
        """
        if not os.path.isdir(folder_path):
             Path(folder_path).mkdir(exist_ok=True)
        if not edge_path:
            edge_path = Path(folder_path) / "edges.txt"
        with open(edge_path, "a") as fedge:
            edges = open(edge_path, "r").read()
            for child in self.children:
               edge = "('" + self.label + "','" + child.label + "')\n"
               if edges.find(edge) < 1:
                fedge.write(edge)
        fedge.close()

    def build_text_lookup(self) -> Dict[str, "ManuscriptBase"]:
        """Used to instantiate the stemmas lookup attribute.

        ### Returns:
            dict: Dictionary of its self and all its decendents. With its label as key and its self as value.
        """
        out = {self.label: self}
        if self.children:
             for c in self.children:
                  out.update(c.build_text_lookup())
        return out
    
    def set_edges(self, edge_dict: Dict[str, float]) -> None:
        """Sets the edges of the current manuscript and propagates the edge setting to all its children.
        
        ### Args:
            - edge_dict (dict): The dictionary used to set the edges with the edges as keys and the edge distances as values.
            The format of the keys is: "node_label1,node_label2".
        """
        if self.edges != []:
            self._edges = []
        for child in self.children:
            self._edges.append(edge_dict[self.label + "," + child.label])
            child.set_edges(edge_dict=edge_dict)