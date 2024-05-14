from pathlib import Path
import os
from typing import Union


class ManuscriptBase:
    """Base class for representing manuscripts in a stemma tree.
    """

    def __init__(self,
                 label: str,
                 parent: "ManuscriptBase",
                 children: list["ManuscriptBase"] = [],
                 edges: list[float] = None
                 ) -> None:
        """Base class for representing manuscripts.

        Args:
            label (str, reqired): The label denoting the text.
            parent (text, requiered): The parent text of the curent text. If set to None is the root manuscript of the tree.
            children (list, optional): A list of this Manuscripts children.
            edges (list, Optional): A list representing the distance between the edges. 
            In the same order as the children array.
            recursive (dict, Optional): If different than None will ignore all other parameters except parent
            and will build all the children of the manuscript from the given list.

        Raises:
            TypeError: If no Manuscript label specified.
        """
        if label:
                self._label = label
        #TODO: Check not broken
        if parent == None or isinstance(parent, ManuscriptBase):
                self._parent = parent
        else:
            raise ValueError("Parent must be None or of type ManuscriptBase.")
        if isinstance(children, list):
                self._children = children
        else:
            raise ValueError("The children must be of type list.")
        if edges != None:
                if len(children) != len(edges):
                    raise RuntimeError("The edges array must be of same length as the children array.")
                else:
                    self._edges = edges

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
        """String representation of the Manuscript"""
        return self.label

    def dict(self, include_edges = False) -> dict:
        """ Constructs dictionary representaion of tree from the Manuscript it is called from.

        Args:
            include_edges (bool, optional): Indicates if the tree should contain the edges. Default to false.

        Resturns:
            Dictionary representation of Manuscript and all of its children.
        """
        if include_edges:
            if len(self.children) == 0:
                return self.label
            else:
                return {"label": self.label, 
                        "edges": {edge for edge in self.edges},
                        "children": {child.dict() for child in self.children}}
        else:
            if not self.children or len(self.children) == 0:
                return {self.label: {}}
            else:
                out = {}
                for child in self.children:
                     out.update(child.dict())
                return {self.label: out}

    def dump(self, folder_path: str, edge_path: str = None) -> None:
        """Adds the edge to the edge file present in given folder.
            If the folder does not exist it will be created.
            If the edge file does not existe it will be created.
            Will look through edge file if it exists to check that edge is alredy present in edge file. 
        
        Args:
            folder_path (str, Required): The path the folder where the text file will be writen.
            edge_path (str, Optional): The path to the edge file.
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
            
    def build_lookup(self) -> dict:
        """Used to instantiate the stemmas lookup attribute.

        Returns:
            dict: Dictionary of its self and all its decendents. With its label as key and its self as value.
        """
        out = {self.label: self}
        if self.children:
             for c in self.children:
                  out.update(c.build_lookup())
        return out